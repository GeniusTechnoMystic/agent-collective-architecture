"""Agent identity module — Ed25519 keypairs and AgentIdentity class.

Uses PyNaCl (libsodium bindings) for Ed25519 signing/verification.
The private key is stored as the 32-byte seed and expanded to the
64-byte secret key only when signing.
"""

import hashlib
from typing import Optional

import nacl.bindings
from nacl import exceptions as nacl_exceptions

# Constants
SEED_BYTES = 32
PUBLIC_KEY_BYTES = 32
SIGNATURE_BYTES = 64


def _expand_secret_key(seed: bytes) -> bytes:
    """Expand a 32-byte seed to a 64-byte Ed25519 secret key."""
    _, secret_key = nacl.bindings.crypto_sign_seed_keypair(seed)
    return secret_key


def generate_agent_keypair(seed: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """Generate an Ed25519 (private_seed, public_key) pair.

    Args:
        seed: Optional 32-byte seed for deterministic key generation.
              If None, a random seed is generated.

    Returns:
        Tuple of (private_seed, public_key) — both 32 bytes.
    """
    if seed is None:
        seed = nacl.bindings.randombytes(SEED_BYTES)
    elif len(seed) != SEED_BYTES:
        raise ValueError(f"Seed must be exactly {SEED_BYTES} bytes, got {len(seed)}")

    public_key = nacl.bindings.crypto_sign_seed_keypair(seed)[0]
    return seed, public_key


class AgentIdentity:
    """Represents an agent's cryptographic identity in the collective.

    Wraps an Ed25519 keypair with agent metadata (agent_id, archetype).
    """

    def __init__(
        self,
        agent_id: str,
        private_key: bytes,
        public_key: bytes,
        archetype: Optional[str] = None,
    ):
        self.agent_id = agent_id
        self.private_key = private_key
        self.public_key = public_key
        self.archetype = archetype

    @classmethod
    def create(
        cls,
        agent_id: str,
        archetype: Optional[str] = None,
        seed: Optional[bytes] = None,
    ) -> "AgentIdentity":
        """Create a new AgentIdentity with a fresh or seeded keypair."""
        private_key, public_key = generate_agent_keypair(seed=seed)
        return cls(
            agent_id=agent_id,
            private_key=private_key,
            public_key=public_key,
            archetype=archetype,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "AgentIdentity":
        """Restore an AgentIdentity from a dict representation.

        Expects keys: agent_id, public_key, private_key (hex strings),
        and optional archetype.
        """
        return cls(
            agent_id=data["agent_id"],
            private_key=bytes.fromhex(data["private_key"]),
            public_key=bytes.fromhex(data["public_key"]),
            archetype=data.get("archetype"),
        )

    @property
    def fingerprint(self) -> str:
        """Short hex fingerprint derived from the public key.

        Uses the first 8 bytes of SHA-256(public_key) as a human-readable
        identifier. Not cryptographically secure for identity — use the
        full public key for actual verification.
        """
        h = hashlib.sha256(self.public_key).digest()
        return h[:8].hex()

    def sign(self, message: bytes) -> bytes:
        """Sign a message with this identity's private key.

        Args:
            message: Arbitrary bytes to sign.

        Returns:
            64-byte Ed25519 signature.
        """
        secret_key = _expand_secret_key(self.private_key)
        return nacl.bindings.crypto_sign(message, secret_key)[:SIGNATURE_BYTES]

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a message's signature against this identity's public key.

        Args:
            message: The original message bytes.
            signature: 64-byte Ed25519 signature to verify.

        Returns:
            True if signature is valid for message and public_key.
        """
        try:
            # crypto_sign_open expects signed_message = signature + message
            signed_message = signature + message
            nacl.bindings.crypto_sign_open(signed_message, self.public_key)
            return True
        except nacl_exceptions.BadSignatureError:
            return False

    def to_dict(self) -> dict:
        """Serialize to dict. Private key is NOT included by default."""
        return {
            "agent_id": self.agent_id,
            "fingerprint": self.fingerprint,
            "public_key": self.public_key.hex(),
            "archetype": self.archetype,
        }

    def __str__(self) -> str:
        return f"AgentIdentity({self.agent_id}:{self.fingerprint})"

    def __repr__(self) -> str:
        return (
            f"AgentIdentity(agent_id={self.agent_id!r}, "
            f"fingerprint={self.fingerprint!r}, "
            f"archetype={self.archetype!r})"
        )
