"""DSH asyncio mesh peer — newline-delimited JSON over TCP with zk-STARK auth."""
import asyncio, json, hashlib, os, time, logging, sys
from dataclasses import dataclass, field
from typing import Callable, Optional

from compute.crypto.zk_stark import (
    generate_identity as _stark_gen_id,
    verify_identity as _stark_verify_id,
    generate_mesh_auth_proof as _stark_auth_proof,
    verify_mesh_auth_proof as _stark_verify_auth,
    StarkProof, FRILayer,
)
from compute.crypto.pqc import sha3_bytes

log = logging.getLogger("mesh")


def _serialize_proof(proof: StarkProof) -> dict:
    return {
        "evaluations": proof.evaluations,
        "merkle_root": proof.merkle_root.hex(),
        "fri_layers": [{"root": l.root.hex(), "values": l.values} for l in proof.fri_layers],
        "query_responses": [(idx, val, [p.hex() for p in path])
                           for idx, val, path in proof.query_responses],
    }


def _deserialize_proof(d: dict) -> StarkProof:
    return StarkProof(
        evaluations=d["evaluations"],
        merkle_root=bytes.fromhex(d["merkle_root"]),
        fri_layers=[FRILayer(root=bytes.fromhex(l["root"]), values=l["values"]) for l in d["fri_layers"]],
        query_responses=[(idx, val, [bytes.fromhex(p) for p in path])
                        for idx, val, path in d["query_responses"]],
    )

@dataclass
class PeerConn:
    peer_id: str
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    commitment: int = 0

@dataclass
class MeshNode:
    node_id: str = ""
    _secret: bytes = field(default_factory=lambda: os.urandom(32))
    _commitment: int = 0
    peers: dict = field(default_factory=dict)
    on_message: Optional[Callable] = None
    _server: Optional[asyncio.Server] = None
    _tasks: list = field(default_factory=list)

    def __post_init__(self):
        self._commitment, _ = _stark_gen_id(self._secret)
        self.node_id = hashlib.sha3_256(self._secret).hexdigest()[:16]

    # --- transport helpers ---
    @staticmethod
    async def _send(writer: asyncio.StreamWriter, msg: dict):
        writer.write(json.dumps(msg).encode() + b"\n")
        await writer.drain()

    @staticmethod
    async def _recv(reader: asyncio.StreamReader) -> Optional[dict]:
        line = await reader.readline()
        if not line:
            return None
        return json.loads(line)

    # --- server side ---
    async def listen(self, host: str = "0.0.0.0", port: int = 9000):
        self._server = await asyncio.start_server(self._handle_inbound, host, port)
        log.info(f"[{self.node_id[:8]}] listening on {host}:{port}")

    async def _handle_inbound(self, reader, writer):
        peer_id = ""
        try:
            msg = await self._recv(reader)
            if not msg or msg.get("type") != "handshake":
                writer.close(); return
            peer_id = msg["node_id"]
            peer_commitment = msg["commitment"]
            challenge = os.urandom(32).hex()
            await self._send(writer, {"type": "handshake", "node_id": self.node_id,
                                      "commitment": self._commitment, "challenge": challenge})
            auth = await self._recv(reader)
            if not auth or auth.get("type") != "auth":
                writer.close(); return
            # Verify zk-STARK proof against peer's commitment and our challenge
            proof_data = auth["proof"]
            proof = _deserialize_proof(proof_data)
            if not _stark_verify_auth(peer_commitment, bytes.fromhex(challenge), proof):
                log.warning(f"auth failed for {peer_id[:8]}")
                writer.close(); return
            await self._send(writer, {"type": "auth_ok"})
            self.peers[peer_id] = PeerConn(peer_id, reader, writer, peer_commitment)
            log.info(f"[{self.node_id[:8]}] peer joined: {peer_id[:8]}")
            await self._read_loop(peer_id, reader)
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            self._remove_peer(peer_id)

    # --- client side ---
    async def connect(self, host: str, port: int):
        reader, writer = await asyncio.open_connection(host, port)
        await self._send(writer, {"type": "handshake", "node_id": self.node_id,
                                  "commitment": self._commitment, "challenge": ""})
        resp = await self._recv(reader)
        if not resp or resp.get("type") != "handshake":
            writer.close(); return
        peer_id = resp["node_id"]
        challenge = resp["challenge"]
        # Generate zk-STARK proof for the challenge
        proof = _stark_auth_proof(self._secret, bytes.fromhex(challenge))
        await self._send(writer, {"type": "auth", "proof": _serialize_proof(proof)})
        ack = await self._recv(reader)
        if not ack or ack.get("type") != "auth_ok":
            writer.close(); return
        self.peers[peer_id] = PeerConn(peer_id, reader, writer, resp.get("commitment", 0))
        log.info(f"[{self.node_id[:8]}] connected to {peer_id[:8]}")
        self._tasks.append(asyncio.create_task(self._read_loop(peer_id, reader)))

    # --- message loop ---
    async def _read_loop(self, peer_id: str, reader: asyncio.StreamReader):
        try:
            while True:
                msg = await self._recv(reader)
                if msg is None:
                    break
                if msg.get("type") == "pulse":
                    continue  # heartbeat ack
                if self.on_message:
                    self.on_message(peer_id, msg)
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            self._remove_peer(peer_id)

    # --- broadcast / heartbeat ---
    async def broadcast(self, msg: dict):
        dead = []
        for pid, pc in list(self.peers.items()):
            try:
                await self._send(pc.writer, msg)
            except (ConnectionError, OSError):
                dead.append(pid)
        for pid in dead:
            self._remove_peer(pid)

    async def _heartbeat(self):
        while True:
            await asyncio.sleep(10)
            await self.broadcast({"type": "pulse", "data": {"ts": time.time(), "node": self.node_id}})

    # --- lifecycle ---
    def _remove_peer(self, peer_id: str):
        pc = self.peers.pop(peer_id, None)
        if pc:
            pc.writer.close()
            log.info(f"[{self.node_id[:8]}] peer left: {peer_id[:8]}")

    async def shutdown(self):
        for pid in list(self.peers):
            self._remove_peer(pid)
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def run(self, host: str = "0.0.0.0", port: int = 9000):
        await self.listen(host, port)
        asyncio.create_task(self._heartbeat())
        await self._server.serve_forever()


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    node = MeshNode()
    log.info(f"Starting mesh node {node.node_id[:8]} on port {port}")
    if len(sys.argv) > 2:
        await node.listen("0.0.0.0", port)
        asyncio.create_task(node._heartbeat())
        await asyncio.sleep(1)
        await node.connect("127.0.0.1", int(sys.argv[2]))
        await node._server.serve_forever()
    else:
        await node.run("0.0.0.0", port)

if __name__ == "__main__":
    asyncio.run(main())
