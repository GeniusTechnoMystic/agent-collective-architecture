"""Tests for messaging module — message signing, verification, and serialization."""

import json
import pytest
from agent_collective.identity import AgentIdentity
from agent_collective.messaging import (
    sign_message,
    verify_message,
    SignedMessage,
    PROTOCOL_VERSION,
    MAX_PAYLOAD_BYTES,
)


@pytest.fixture
def alice():
    return AgentIdentity.create("alice", archetype="Scholar-Philosopher")


@pytest.fixture
def bob():
    return AgentIdentity.create("bob", archetype="Systems-Fixer")


class TestSignAndVerify:
    def test_sign_and_verify_valid_message(self, alice):
        payload = {"action": "propose", "tier": 2, "description": "Add new tool"}
        msg = sign_message(alice, payload)
        assert msg.protocol_version == PROTOCOL_VERSION
        assert msg.sender_id == "alice"
        assert msg.payload == payload
        assert len(msg.signature) == 64
        assert msg.timestamp > 0

    def test_verify_valid_message(self, alice):
        payload = {"action": "vote", "proposal_id": "p-001", "decision": "approve"}
        msg = sign_message(alice, payload)
        result = verify_message(msg, alice.public_key)
        assert result is True

    def test_verify_wrong_identity_rejects(self, alice, bob):
        payload = {"action": "spawn_request", "role": "auditor"}
        msg = sign_message(alice, payload)
        # bob's key should not verify alice's signature
        result = verify_message(msg, bob.public_key)
        assert result is False

    def test_verify_tampered_payload_rejects(self, alice):
        payload = {"action": "vote", "proposal_id": "p-001", "decision": "approve"}
        msg = sign_message(alice, payload)
        # Tamper with payload
        msg.payload["decision"] = "reject"
        # Recalculate hash — but the signature won't match
        result = verify_message(msg, alice.public_key)
        assert result is False

    def test_verify_tampered_signature_rejects(self, alice):
        payload = {"action": "ping"}
        msg = sign_message(alice, payload)
        tampered = bytearray(msg.signature)
        tampered[10] ^= 0xFF
        msg.signature = bytes(tampered)
        result = verify_message(msg, alice.public_key)
        assert result is False


class TestSignedMessageSerialization:
    def test_to_dict_includes_all_fields(self, alice):
        payload = {"action": "test"}
        msg = sign_message(alice, payload)
        d = msg.to_dict()
        assert d["protocol_version"] == PROTOCOL_VERSION
        assert d["sender_id"] == "alice"
        assert d["sender_fingerprint"] == alice.fingerprint
        assert d["payload"] == payload
        assert "signature" in d
        assert "timestamp" in d

    def test_to_json_and_parse(self, alice):
        payload = {"action": "heartbeat", "status": "ok"}
        msg = sign_message(alice, payload)
        json_str = msg.to_json()
        parsed = json.loads(json_str)
        assert parsed["sender_id"] == "alice"
        assert parsed["payload"] == payload

    def test_hash_is_deterministic(self, alice):
        payload = {"action": "vote", "id": "abc"}
        msg1 = sign_message(alice, payload)
        msg2 = sign_message(alice, payload)
        assert msg1.message_hash == msg2.message_hash


class TestPayloadValidation:
    def test_rejects_oversized_payload(self, alice):
        large_payload = {"data": "x" * (MAX_PAYLOAD_BYTES + 1)}
        with pytest.raises(ValueError, match="exceeds maximum payload size"):
            sign_message(alice, large_payload)

    def test_accepts_max_size_payload(self, alice):
        payload = {"data": "x" * (MAX_PAYLOAD_BYTES - 100)}
        msg = sign_message(alice, payload)
        assert msg is not None

    def test_rejects_non_dict_payload(self, alice):
        with pytest.raises(TypeError, match="Payload must be a dictionary"):
            sign_message(alice, "not-a-dict")  # type: ignore
