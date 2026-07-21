"""Message signing and verification for inter-agent communication.

Provides SignedMessage dataclass with Ed25519 signatures, serialization,
and payload validation.
"""

import hashlib
import json
import time
from typing import Any

from agent_collective.identity import AgentIdentity

PROTOCOL_VERSION = 1
MAX_PAYLOAD_BYTES = 16 * 1024  # 16KB max payload


class SignedMessage:
    """A signed message from one agent to another (or broadcast).

    Fields are always populated after construction via sign_message().
    """

    def __init__(
        self,
        protocol_version: int,
        sender_id: str,
        sender_fingerprint: str,
        timestamp: float,
        payload: dict[str, Any],
        signature: bytes,
        signature_hex: str,
        message_hash: str,
    ):
        self.protocol_version = protocol_version
        self.sender_id = sender_id
        self.sender_fingerprint = sender_fingerprint
        self.timestamp = timestamp
        self.payload = payload
        self.signature = signature
        self.signature_hex = signature_hex
        self.message_hash = message_hash

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict (safe for JSON/logging — signature as hex)."""
        return {
            "protocol_version": self.protocol_version,
            "sender_id": self.sender_id,
            "sender_fingerprint": self.sender_fingerprint,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "signature": self.signature_hex,
            "message_hash": self.message_hash,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _canonical_json(payload: dict) -> bytes:
    """Deterministic JSON serialization for signing.

    Sorts keys so the same payload always produces the same bytes.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_message(identity: AgentIdentity, payload: dict) -> SignedMessage:
    """Sign a payload with the given identity.

    Args:
        identity: The AgentIdentity to sign with.
        payload: Dictionary payload to sign (must be JSON-serializable).

    Returns:
        SignedMessage containing the payload, signature, and metadata.

    Raises:
        TypeError: If payload is not a dict.
        ValueError: If payload exceeds MAX_PAYLOAD_BYTES when serialized.
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary")

    payload_bytes = _canonical_json(payload)
    if len(payload_bytes) > MAX_PAYLOAD_BYTES:
        raise ValueError(
            f"Payload size ({len(payload_bytes)} bytes) exceeds maximum "
            f"payload size ({MAX_PAYLOAD_BYTES} bytes)"
        )

    message_hash = hashlib.sha256(payload_bytes).hexdigest()
    to_sign = message_hash.encode("utf-8")
    signature = identity.sign(to_sign)
    timestamp = time.time()

    return SignedMessage(
        protocol_version=PROTOCOL_VERSION,
        sender_id=identity.agent_id,
        sender_fingerprint=identity.fingerprint,
        timestamp=timestamp,
        payload=payload,
        signature=signature,
        signature_hex=signature.hex(),
        message_hash=message_hash,
    )


def verify_message(msg: SignedMessage, public_key: bytes) -> bool:
    """Verify a signed message against a public key.

    Args:
        msg: The SignedMessage to verify.
        public_key: 32-byte Ed25519 public key of the claimed sender.

    Returns:
        True if the signature is valid for the payload and public_key.
    """
    # Recompute the message hash from the payload
    payload_bytes = _canonical_json(msg.payload)
    expected_hash = hashlib.sha256(payload_bytes).hexdigest()

    # Verify the hash matches
    if expected_hash != msg.message_hash:
        return False

    # Verify the signature on the hash
    to_verify = expected_hash.encode("utf-8")

    # Create a temporary identity for verification
    from agent_collective.identity import AgentIdentity

    temp = AgentIdentity(
        agent_id="__verifier__",
        private_key=b"\x00" * 32,  # dummy — won't be used
        public_key=public_key,
    )
    return temp.verify(to_verify, msg.signature)
