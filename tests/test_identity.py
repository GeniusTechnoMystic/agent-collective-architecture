"""Tests for identity module — Ed25519 keypairs and AgentIdentity class."""

import pytest
from agent_collective.identity import (
    generate_agent_keypair,
    AgentIdentity,
    SEED_BYTES,
    PUBLIC_KEY_BYTES,
    SIGNATURE_BYTES,
)


class TestGenerateKeypair:
    def test_returns_private_and_public_key(self):
        private, public = generate_agent_keypair()
        assert isinstance(private, bytes)
        assert isinstance(public, bytes)
        assert len(private) == SEED_BYTES
        assert len(public) == PUBLIC_KEY_BYTES

    def test_different_calls_produce_different_keys(self):
        priv1, pub1 = generate_agent_keypair()
        priv2, pub2 = generate_agent_keypair()
        assert priv1 != priv2
        assert pub1 != pub2

    def test_public_key_derives_from_private(self):
        priv, pub = generate_agent_keypair()
        _, pub2 = generate_agent_keypair(seed=priv)
        assert pub == pub2


class TestAgentIdentity:
    def test_create_from_new_keypair(self):
        identity = AgentIdentity.create("test-agent")
        assert identity.agent_id == "test-agent"
        assert len(identity.private_key) == SEED_BYTES
        assert len(identity.public_key) == PUBLIC_KEY_BYTES
        assert identity.archetype is None

    def test_create_with_archetype(self):
        identity = AgentIdentity.create("scholar-1", archetype="Scholar-Philosopher")
        assert identity.archetype == "Scholar-Philosopher"

    def test_create_from_seed_is_deterministic(self):
        seed = bytes([i for i in range(32)])
        id1 = AgentIdentity.create("det-1", seed=seed)
        id2 = AgentIdentity.create("det-2", seed=seed)
        assert id1.public_key == id2.public_key
        # private keys must also match when same seed
        assert id1.private_key == id2.private_key

    def test_identity_string_representation(self):
        identity = AgentIdentity.create("test-agent")
        s = str(identity)
        assert "test-agent" in s
        assert identity.fingerprint in s

    def test_fingerprint_is_hex_of_public_key_hash(self):
        identity = AgentIdentity.create("fp-test")
        assert len(identity.fingerprint) == 16  # 8 bytes hex
        assert all(c in "0123456789abcdef" for c in identity.fingerprint)

    def test_to_dict_contains_all_fields(self):
        identity = AgentIdentity.create("dict-test", archetype="Systems-Fixer")
        d = identity.to_dict()
        assert d["agent_id"] == "dict-test"
        assert d["archetype"] == "Systems-Fixer"
        assert d["fingerprint"] == identity.fingerprint
        assert "public_key" in d
        assert "private_key" not in d  # never expose private key

    def test_from_dict_restores_identity(self):
        original = AgentIdentity.create("roundtrip", archetype="Mirror-Mage")
        d = original.to_dict()
        # Need private key for full restoration — add it separately
        d["private_key"] = original.private_key.hex()
        restored = AgentIdentity.from_dict(d)
        assert restored.agent_id == original.agent_id
        assert restored.archetype == original.archetype
        assert restored.public_key == original.public_key
        assert restored.private_key == original.private_key

    def test_sign_and_verify_message(self):
        identity = AgentIdentity.create("sign-test")
        message = b"Test message for signing"
        signature = identity.sign(message)
        assert len(signature) == SIGNATURE_BYTES
        assert identity.verify(message, signature) is True

    def test_verify_rejects_wrong_message(self):
        identity = AgentIdentity.create("verify-test")
        message = b"Original message"
        signature = identity.sign(message)
        assert identity.verify(b"Wrong message", signature) is False

    def test_verify_rejects_tampered_signature(self):
        identity = AgentIdentity.create("tamper-test")
        message = b"Don't tamper with me"
        signature = identity.sign(message)
        tampered = bytearray(signature)
        tampered[0] ^= 0xFF
        assert identity.verify(message, bytes(tampered)) is False
