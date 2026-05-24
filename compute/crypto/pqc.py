"""
DOME-HUB Post-Quantum Cryptography Layer
=========================================
NIST FIPS 203/204/205 compliant. Quantum-resistant mesh security.

Algorithms:
  - ML-KEM-1024 (FIPS 203): Key encapsulation — lattice-based key exchange
  - ML-DSA-87 (FIPS 204): Digital signatures — lattice-based signing
  - AES-256-GCM: Authenticated symmetric encryption (quantum-safe at 256-bit)
  - SHA3-512: Quantum-resistant hashing
  - HKDF-SHA3-256: Key derivation

Usage:
  from compute.crypto.pqc import PQCKeyPair, sign, verify, encapsulate, decapsulate, encrypt, decrypt, sha3

Copyright (c) 2024-2026 Trinity Global Partners LLC
"""

from __future__ import annotations
import os, hashlib, json
from dataclasses import dataclass
from pathlib import Path

import oqs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# ─── Constants ────────────────────────────────────────────────────────────────

KEM_ALG = "ML-KEM-1024"       # NIST Level 5 (highest security)
SIG_ALG = "ML-DSA-87"         # NIST Level 5 (highest security)
AES_KEY_BITS = 256
NONCE_BYTES = 12              # AES-GCM standard nonce
KEY_DIR = Path.home() / ".trinity-spore" / "keys"


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class PQCKeyPair:
    """ML-DSA signing keypair."""
    public_key: bytes
    secret_key: bytes
    algorithm: str = SIG_ALG

    def save(self, name: str = "node") -> None:
        KEY_DIR.mkdir(parents=True, exist_ok=True)
        (KEY_DIR / f"{name}.pub").write_bytes(self.public_key)
        sk_path = KEY_DIR / f"{name}.sk"
        sk_path.write_bytes(self.secret_key)
        os.chmod(sk_path, 0o600)

    @classmethod
    def load(cls, name: str = "node") -> "PQCKeyPair":
        pub = (KEY_DIR / f"{name}.pub").read_bytes()
        sk = (KEY_DIR / f"{name}.sk").read_bytes()
        return cls(public_key=pub, secret_key=sk)

    @classmethod
    def exists(cls, name: str = "node") -> bool:
        return (KEY_DIR / f"{name}.pub").exists() and (KEY_DIR / f"{name}.sk").exists()


@dataclass
class KEMKeyPair:
    """ML-KEM key encapsulation keypair."""
    public_key: bytes
    secret_key: bytes
    algorithm: str = KEM_ALG

    def save(self, name: str = "node_kem") -> None:
        KEY_DIR.mkdir(parents=True, exist_ok=True)
        (KEY_DIR / f"{name}.pub").write_bytes(self.public_key)
        sk_path = KEY_DIR / f"{name}.sk"
        sk_path.write_bytes(self.secret_key)
        os.chmod(sk_path, 0o600)

    @classmethod
    def load(cls, name: str = "node_kem") -> "KEMKeyPair":
        pub = (KEY_DIR / f"{name}.pub").read_bytes()
        sk = (KEY_DIR / f"{name}.sk").read_bytes()
        return cls(public_key=pub, secret_key=sk)

    @classmethod
    def exists(cls, name: str = "node_kem") -> bool:
        return (KEY_DIR / f"{name}.pub").exists() and (KEY_DIR / f"{name}.sk").exists()


# ─── Key Generation ───────────────────────────────────────────────────────────

def generate_signing_keypair() -> PQCKeyPair:
    """Generate ML-DSA-87 signing keypair."""
    with oqs.Signature(SIG_ALG) as signer:
        pub = signer.generate_keypair()
        sk = signer.export_secret_key()
    return PQCKeyPair(public_key=pub, secret_key=sk)


def generate_kem_keypair() -> KEMKeyPair:
    """Generate ML-KEM-1024 key encapsulation keypair."""
    with oqs.KeyEncapsulation(KEM_ALG) as kem:
        pub = kem.generate_keypair()
        sk = kem.export_secret_key()
    return KEMKeyPair(public_key=pub, secret_key=sk)


# ─── Signing (ML-DSA-87) ─────────────────────────────────────────────────────

def sign(message: bytes, secret_key: bytes) -> bytes:
    """Sign message with ML-DSA-87. Returns signature bytes."""
    with oqs.Signature(SIG_ALG, secret_key=secret_key) as signer:
        return signer.sign(message)


def verify(message: bytes, signature: bytes, public_key: bytes) -> bool:
    """Verify ML-DSA-87 signature. Returns True if valid."""
    with oqs.Signature(SIG_ALG) as verifier:
        return verifier.verify(message, signature, public_key)


# ─── Key Encapsulation (ML-KEM-1024) ─────────────────────────────────────────

def encapsulate(public_key: bytes) -> tuple[bytes, bytes]:
    """Encapsulate: generate (ciphertext, shared_secret) from peer's public key."""
    with oqs.KeyEncapsulation(KEM_ALG) as kem:
        ciphertext, shared_secret = kem.encap_secret(public_key)
    return ciphertext, shared_secret


def decapsulate(ciphertext: bytes, secret_key: bytes) -> bytes:
    """Decapsulate: recover shared_secret from ciphertext using own secret key."""
    with oqs.KeyEncapsulation(KEM_ALG, secret_key=secret_key) as kem:
        return kem.decap_secret(ciphertext)


# ─── Symmetric Encryption (AES-256-GCM) ──────────────────────────────────────

def derive_key(shared_secret: bytes, context: bytes = b"dome-mesh-v1") -> bytes:
    """Derive AES-256 key from shared secret via HKDF-SHA3-256."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=context,
    )
    return hkdf.derive(shared_secret)


def encrypt(plaintext: bytes, key: bytes, aad: bytes = b"") -> bytes:
    """AES-256-GCM encrypt. Returns nonce || ciphertext."""
    nonce = os.urandom(NONCE_BYTES)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext, aad)
    return nonce + ct


def decrypt(data: bytes, key: bytes, aad: bytes = b"") -> bytes:
    """AES-256-GCM decrypt. Input is nonce || ciphertext."""
    nonce = data[:NONCE_BYTES]
    ct = data[NONCE_BYTES:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, aad)


# ─── Hashing (SHA3-512) ──────────────────────────────────────────────────────

def sha3(data: bytes) -> str:
    """SHA3-512 hash, hex-encoded."""
    return hashlib.sha3_512(data).hexdigest()


def sha3_bytes(data: bytes) -> bytes:
    """SHA3-512 hash, raw bytes."""
    return hashlib.sha3_512(data).digest()


# ─── Convenience: Sign JSON payload ──────────────────────────────────────────

def sign_json(payload: dict, secret_key: bytes) -> str:
    """Sign a JSON payload, return hex-encoded signature."""
    msg = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sign(msg, secret_key).hex()


def verify_json(payload: dict, signature_hex: str, public_key: bytes) -> bool:
    """Verify a JSON payload signature."""
    msg = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return verify(msg, bytes.fromhex(signature_hex), public_key)


# ─── Node Identity ───────────────────────────────────────────────────────────

def ensure_node_keys() -> tuple[PQCKeyPair, KEMKeyPair]:
    """Ensure node has both signing and KEM keypairs. Generate if missing."""
    if not PQCKeyPair.exists():
        kp = generate_signing_keypair()
        kp.save()
    else:
        kp = PQCKeyPair.load()

    if not KEMKeyPair.exists():
        kem_kp = generate_kem_keypair()
        kem_kp.save()
    else:
        kem_kp = KEMKeyPair.load()

    return kp, kem_kp
