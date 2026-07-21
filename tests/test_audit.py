"""Tests for audit trail module — append-only, tamper-evident log."""

import json
import os
import tempfile

import pytest
from agent_collective.identity import AgentIdentity
from agent_collective.messaging import sign_message
from agent_collective.audit import AuditLog


@pytest.fixture
def audit_log():
    """Create a temporary audit log for testing."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    log = AuditLog(path)
    yield log
    log.close()
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def agent():
    return AgentIdentity.create("test-agent", archetype="Systems-Fixer")


class TestAuditLogCreation:
    def test_new_log_has_zero_entries(self, audit_log):
        assert audit_log.count == 0

    def test_new_log_has_genesis_hash(self, audit_log):
        assert audit_log.last_hash is not None
        assert len(audit_log.last_hash) == 64  # SHA-256 hex

    def test_persists_to_disk(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = f.name
        log = AuditLog(path)
        log.close()
        assert os.path.exists(path)
        with open(path) as f:
            content = f.read()
        assert len(content) > 0  # genesis entry
        os.unlink(path)


class TestAppend:
    def test_append_increases_count(self, audit_log, agent):
        msg = sign_message(agent, {"action": "test"})
        entry_id = audit_log.append(msg)
        assert audit_log.count == 1
        assert entry_id == 1  # first entry after genesis

    def test_append_multiple_entries(self, audit_log, agent):
        for i in range(5):
            msg = sign_message(agent, {"action": f"test-{i}"})
            audit_log.append(msg)
        assert audit_log.count == 5

    def test_returns_entry_id(self, audit_log, agent):
        msg = sign_message(agent, {"action": "first"})
        id1 = audit_log.append(msg)
        msg2 = sign_message(agent, {"action": "second"})
        id2 = audit_log.append(msg2)
        assert id1 == 1
        assert id2 == 2


class TestTamperEvidence:
    def test_chain_of_hashes_intact(self, audit_log, agent):
        """Each entry stores the hash of the previous entry."""
        entries = []
        for i in range(3):
            msg = sign_message(agent, {"action": f"op-{i}"})
            eid = audit_log.append(msg)
            entries.append(eid)

        # Read raw file and verify chain
        log_data = audit_log.read_all()
        prev_hash = None
        for entry in log_data:
            if prev_hash is None:
                # First real entry links to genesis
                prev_hash = entry["previous_hash"]
            else:
                assert entry["previous_hash"] == prev_hash
            prev_hash = entry["entry_hash"]

    def test_detect_tampered_entry(self, audit_log, agent):
        """Modifying a past entry breaks the hash chain."""
        msg = sign_message(agent, {"action": "original"})
        audit_log.append(msg)
        msg2 = sign_message(agent, {"action": "second"})
        audit_log.append(msg2)

        # Read the raw file and tamper with it
        raw = audit_log._read_raw_lines()
        modified_line = json.loads(raw[1])  # first real entry (index 1)
        modified_line["payload"]["action"] = "tampered"
        raw[1] = json.dumps(modified_line, sort_keys=True)

        # Write tampered data back
        with open(audit_log.path, "w") as f:
            for line in raw:
                f.write(line + "\n")

        # Verify detection
        assert audit_log.verify_integrity() is False

    def test_detect_deleted_entry(self, audit_log, agent):
        """Deleting an entry breaks the hash chain."""
        msg = sign_message(agent, {"action": "first"})
        audit_log.append(msg)
        msg2 = sign_message(agent, {"action": "second"})
        audit_log.append(msg2)
        msg3 = sign_message(agent, {"action": "third"})
        audit_log.append(msg3)

        # Delete middle entry by rewriting without it
        raw = audit_log._read_raw_lines()
        del raw[2]  # remove second real entry (index 2 in 0-based)

        with open(audit_log.path, "w") as f:
            for line in raw:
                f.write(line + "\n")

        assert audit_log.verify_integrity() is False


class TestQuery:
    def test_read_all_returns_all_entries(self, audit_log, agent):
        entries = []
        for i in range(3):
            msg = sign_message(agent, {"action": f"op-{i}"})
            eid = audit_log.append(msg)
            entries.append(eid)

        all_entries = audit_log.read_all()
        assert len(all_entries) == 3
        for i, entry in enumerate(all_entries):
            assert entry["payload"]["action"] == f"op-{i}"

    def test_query_by_sender(self, audit_log):
        """Filter entries by sender_id."""
        agent1 = AgentIdentity.create("agent-1")
        agent2 = AgentIdentity.create("agent-2")

        msg1 = sign_message(agent1, {"action": "from-1"})
        audit_log.append(msg1)
        msg2 = sign_message(agent2, {"action": "from-2"})
        audit_log.append(msg2)
        msg3 = sign_message(agent1, {"action": "from-1-again"})
        audit_log.append(msg3)

        results = audit_log.query(sender_id="agent-1")
        assert len(results) == 2
        for r in results:
            assert r["sender_id"] == "agent-1"

    def test_query_by_action(self, audit_log, agent):
        """Filter entries by payload action."""
        for action in ["propose", "vote", "propose", "execute"]:
            msg = sign_message(agent, {"action": action})
            audit_log.append(msg)

        results = audit_log.query(action="propose")
        assert len(results) == 2

    def test_query_with_limit(self, audit_log, agent):
        for i in range(10):
            msg = sign_message(agent, {"action": f"op-{i}"})
            audit_log.append(msg)

        results = audit_log.query(limit=3)
        assert len(results) == 3

    def test_search_returns_empty_for_no_match(self, audit_log, agent):
        msg = sign_message(agent, {"action": "unique"})
        audit_log.append(msg)
        assert audit_log.query(action="nonexistent") == []
