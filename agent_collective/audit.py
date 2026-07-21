"""Append-only audit trail with tamper evidence.

Each entry is a JSON line (JSONL format) that includes the SHA-256 hash
of the previous entry, forming a hash chain. Any modification to past
entries breaks the chain, which verify_integrity() can detect.
"""

import hashlib
import json
import os
import time
from typing import Any, Optional

from agent_collective.messaging import SignedMessage


class AuditLog:
    """Append-only, tamper-evident audit log backed by a JSONL file.

    The log stores a chain of entries where each entry's ``previous_hash``
    field is the SHA-256 of the preceding entry. A genesis entry is written
    on first open to anchor the chain.
    """

    def __init__(self, path: str):
        self.path = path
        self._file: Optional[io.TextIOWrapper] = None
        self._count: int = 0
        self._last_hash: Optional[str] = None
        self._open()

    def _open(self) -> None:
        """Open or create the log file and initialize the chain."""
        exists = os.path.exists(self.path) and os.path.getsize(self.path) > 0

        self._file = open(self.path, "a+")
        self._file.seek(0)

        if exists:
            # Read last line to restore state
            lines = self._file.readlines()
            self._count = 0
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                self._last_hash = entry.get("entry_hash")
                self._count += 1
        else:
            # Write genesis entry
            genesis = {
                "entry_id": 0,
                "timestamp": time.time(),
                "previous_hash": "0" * 64,
                "entry_hash": None,  # computed below
                "event_type": "genesis",
                "payload": {"event": "audit_log_created"},
            }
            genesis["entry_hash"] = _compute_entry_hash(genesis)
            self._file.write(json.dumps(genesis, sort_keys=True) + "\n")
            self._file.flush()
            self._last_hash = genesis["entry_hash"]
            self._count = 0  # genesis doesn't count as a real entry

    @property
    def count(self) -> int:
        return self._count

    @property
    def last_hash(self) -> Optional[str]:
        return self._last_hash

    def append(self, msg: SignedMessage) -> int:
        """Append a signed message to the audit log.

        Args:
            msg: SignedMessage to record.

        Returns:
            Entry ID of the new entry (1-based, excluding genesis).
        """
        entry_id = self._count + 1
        entry = {
            "entry_id": entry_id,
            "timestamp": time.time(),
            "previous_hash": self._last_hash or "0" * 64,
            "entry_hash": None,  # computed below
            "event_type": "signed_message",
            "protocol_version": msg.protocol_version,
            "sender_id": msg.sender_id,
            "sender_fingerprint": msg.sender_fingerprint,
            "message_hash": msg.message_hash,
            "signature": msg.signature_hex,
            "payload": msg.payload,
        }
        entry["entry_hash"] = _compute_entry_hash(entry)

        self._file.write(json.dumps(entry, sort_keys=True) + "\n")
        self._file.flush()
        self._last_hash = entry["entry_hash"]
        self._count = entry_id
        return entry_id

    def read_all(self) -> list[dict[str, Any]]:
        """Read all logged entries (excluding genesis).

        Returns:
            List of entry dicts in chronological order.
        """
        return self.query()

    def query(
        self,
        sender_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Query the audit log with optional filters.

        Args:
            sender_id: Filter by sender_id.
            action: Filter by payload.action key.
            limit: Max entries to return.

        Returns:
            Filtered list of entry dicts.
        """
        results = []
        raw_lines = self._read_raw_lines()
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("event_type") == "genesis":
                continue

            if sender_id and entry.get("sender_id") != sender_id:
                continue
            if action and entry.get("payload", {}).get("action") != action:
                continue

            results.append(entry)
            if limit and len(results) >= limit:
                break

        return results

    def verify_integrity(self) -> bool:
        """Verify the hash chain is intact and every entry matches its hash.

        Reads all entries sequentially and checks:
        1. Each entry's previous_hash matches the previous entry's entry_hash
        2. Each entry's stored entry_hash matches a recomputation from its fields

        Returns:
            True if the entire chain is valid, False if tampered.
        """
        raw_lines = self._read_raw_lines()
        prev_hash = None

        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)

            # Verify entry's content matches its stored hash
            stored_hash = entry.get("entry_hash")
            computed_hash = _compute_entry_hash(entry)
            if computed_hash != stored_hash:
                return False

            # Verify chain link
            if prev_hash is not None and entry.get("previous_hash") != prev_hash:
                return False

            prev_hash = stored_hash

        return True

    def _read_raw_lines(self) -> list[str]:
        """Read all lines from the file without parsing."""
        self._file.flush()
        with open(self.path) as f:
            return f.readlines()

    def close(self) -> None:
        if self._file and not self._file.closed:
            self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


import io  # noqa: E402 — needed for TextIOWrapper type hint above


def _compute_entry_hash(entry: dict) -> str:
    """Compute the SHA-256 hash of an entry (excluding the entry_hash field)."""
    h = hashlib.sha256()
    for key in sorted(entry.keys()):
        if key == "entry_hash":
            continue
        val = entry[key]
        if isinstance(val, dict):
            val = json.dumps(val, sort_keys=True)
        h.update(f"{key}:{val}|".encode())
    return h.hexdigest()
