"""
PQC Mesh Authentication Skill — Post-Quantum Secure Node Identity & Communication
==================================================================================
Wraps compute/crypto/pqc.py into mesh-specific operations:
  1. Node identity (ML-DSA-87 keypair)
  2. Signed pulse broadcast (quantum-resistant)
  3. Encrypted peer-to-peer channels (ML-KEM-1024 + AES-256-GCM)
  4. SHA3-based mesh HMAC
"""

import json, hashlib, hmac, time
from compute.crypto.pqc import (
    ensure_node_keys, sign_json, verify_json,
    encapsulate, decapsulate, encrypt, decrypt, derive_key,
    sha3, sha3_bytes, PQCKeyPair, KEMKeyPair,
)


def mesh_hmac(secret: str, payload: str) -> str:
    """HMAC-SHA3-256 for mesh heartbeat authentication."""
    return hmac.HMAC(secret.encode(), payload.encode(), hashlib.sha3_256).hexdigest()


def sign_pulse(pulse: dict) -> dict:
    """Sign a frequency pulse payload with ML-DSA-87. Returns pulse with signature fields."""
    signing_kp, kem_kp = ensure_node_keys()
    pulse_copy = dict(pulse)
    pulse_copy["pqcSignature"] = sign_json(pulse, signing_kp.secret_key)
    pulse_copy["pqcPubKeyHash"] = sha3(signing_kp.public_key)[:32]
    pulse_copy["kemPubKeyHash"] = sha3(kem_kp.public_key)[:32]
    pulse_copy["timestamp"] = int(time.time() * 1000)
    return pulse_copy


def verify_pulse(pulse: dict, peer_public_key: bytes) -> bool:
    """Verify a received pulse signature."""
    sig = pulse.get("pqcSignature")
    if not sig:
        return False
    # Remove signature fields for verification
    payload = {k: v for k, v in pulse.items()
               if k not in ("pqcSignature", "pqcPubKeyHash", "kemPubKeyHash", "timestamp")}
    return verify_json(payload, sig, peer_public_key)


def establish_session(peer_kem_public_key: bytes) -> tuple[bytes, bytes]:
    """Establish encrypted session with peer via ML-KEM-1024.
    Returns (ciphertext_to_send, shared_key)."""
    ciphertext, shared_secret = encapsulate(peer_kem_public_key)
    session_key = derive_key(shared_secret, context=b"dome-mesh-session-v1")
    return ciphertext, session_key


def accept_session(ciphertext: bytes) -> bytes:
    """Accept session from peer. Returns shared session key."""
    _, kem_kp = ensure_node_keys()
    shared_secret = decapsulate(ciphertext, kem_kp.secret_key)
    return derive_key(shared_secret, context=b"dome-mesh-session-v1")


def encrypt_message(message: dict, session_key: bytes) -> bytes:
    """Encrypt a mesh message with AES-256-GCM using session key."""
    plaintext = json.dumps(message, separators=(",", ":")).encode()
    return encrypt(plaintext, session_key, aad=b"dome-mesh-msg")


def decrypt_message(data: bytes, session_key: bytes) -> dict:
    """Decrypt a mesh message."""
    plaintext = decrypt(data, session_key, aad=b"dome-mesh-msg")
    return json.loads(plaintext)


def node_fingerprint() -> str:
    """Get this node's PQC fingerprint (SHA3 of signing public key)."""
    signing_kp, _ = ensure_node_keys()
    return sha3(signing_kp.public_key)[:64]
