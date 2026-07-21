# Agent Collective Architecture — Master Test Plan

> **Test Plan ID:** TP-001
> **Version:** 1.0
> **Author:** QA Engineer (Hermes Agent)
> **Status:** Draft for review
> **Covers:** Phase 1 (Foundations) — Issues #1, #2, #3

---

## 1. Scope

### In Scope

| Phase | Module | Status | Test Plan Section |
|-------|--------|--------|:---:|
| 1A | Spawn spec validator (`validator.py`, `cli.py`, `schemas/spawn-schema.json`) | ✅ Built (32 tests) | §6.1 |
| 1B | Agent identity (`identity.py`) | ✅ Built (13 tests) | §6.2 |
| 1B | Message signing (`messaging.py`) | ✅ Built (11 tests) | §6.3 |
| 1B | Audit trail (`audit.py`) | ✅ Built (14 tests) | §6.4 |
| 1B | Delegate wrapper (`delegate.py`) | ❌ Not built | §6.5 |
| 1B | Boundary enforcer (in `delegate.py`) | ❌ Not built | §6.6 |
| 1B | Integration: full lifecycle | ❌ Not built | §6.7 |
| 1C | Proposal system (`proposal.py`) | ❌ Not built | §6.8 |
| 1C | Consensus lifecycle (`consensus.py`) | ❌ Not built | §6.9 |
| 1C | Council minutes (`minutes.py`) | ❌ Not built | §6.10 |
| 1C | Council spawn specs (5 YAML files) | ❌ Not built | §6.11 |
| 1C | Integration: full proposal lifecycle | ❌ Not built | §6.12 |

### Out of Scope

- Phase 2 (Council Automation — weighted voting, deliberation channels, automated triage)
- Phase 3 (Multi-Agent Orchestration — autonomous spawning, anomaly detection)
- Phase 4 (Recursive Governance — protocol amendments, self-improvement)
- Performance testing (deferred to Phase 2 when multi-agent interactions exist)
- Security penetration testing (covered by `code-red-team` skill, run after Phase 1B implementation)
- Browser/UI testing (no web interface)
- Cross-platform compatibility (Linux-only microVM)

---

## 2. Risk Assessment

|| Risk | Impact (1-5) | Probability (1-5) | Risk Score | Test Priority | Test Coverage |
||------|:---:|:---:|:---:|:---:|:---|
|| Cryptographic key generation produces weak/non-random keys | 5 | 2 | 10 | **Critical** | §7.2 — TC-ID-01, TC-ID-02, TC-ID-03 |
|| Message signature fails to detect tampered payload | 5 | 2 | 10 | **Critical** | §7.3 — TC-MSG-04, TC-MSG-05 |
|| Audit log fails to detect tampered entry | 5 | 2 | 10 | **Critical** | §7.4 — TC-AUD-05, TC-AUD-06 |
|| Validator crashes on malformed input (regression) | 4 | 2 | 8 | **Critical** | §7.1 — TC-VAL-10, TC-VAL-11, TC-VAL-12 |
|| Delegate wrapper fails to sign spawned tasks | 4 | 3 | 12 | **Critical** | §7.5 — TC-DEL-01, TC-DEL-02 |
|| Audit log hash chain broken by file corruption | 4 | 1 | 4 | High | §7.4 — TC-AUD-06, TC-AUD-07 |
|| Boundary enforcer allows unauthorized tool access | 5 | 2 | 10 | **Critical** | §7.6 — TC-BND-01, TC-BND-02, TC-BND-09 |
|| Consensus protocol allows double-voting | 4 | 1 | 4 | High | §7.9 — TC-CNS-03 |
|| Proposal triage misclassifies tier | 3 | 3 | 9 | High | §7.8 — TC-PRP-04 |
|| Council spawn spec fails validation at runtime | 3 | 4 | 12 | **Critical** | §7.11 — TC-CSP-01 |
|| Integration test misses contract mismatch between modules | 3 | 3 | 9 | High | §7.7 — TC-INT-01 through TC-INT-09 |

---

## 3. Test Strategy

### 3.1 Levels

| Level | Allocation | Scope | Runner |
|-------|:---:|-------|--------|
| **Unit** | 70% | Individual functions and classes in isolation. No network, no filesystem (except AuditLog which requires it). | `pytest` (direct function calls) |
| **Integration** | 20% | Module boundaries: identity → messaging, messaging → audit, delegate → identity, validator → JSON Schema. Real dependencies, not mocks. | `pytest` (compose real modules) |
| **System/E2E** | 10% | Full pipeline: spawn spec → validate → agent identity → sign message → verify → audit log → query. | `pytest` (full lifecycle script) |

### 3.2 Techniques

| Technique | Where Applied | Rationale |
|-----------|:---:|-----------|
| Equivalence Partitioning | All modules with input domains | Reduce infinite inputs to finite test classes |
| Boundary Value Analysis | All modules with numeric/ordinal boundaries | Catch off-by-one errors (most common bug class) |
| State Transition | Audit log, message lifecycle, consensus lifecycle | Workflow-heavy modules need state coverage |
| Decision Tables | Validator rules, boundary enforcer logic | Business rules with conditional combinations |
| Error Guessing | All modules | Common failure patterns (empty, null, overflow, special chars) |
| Pairwise Testing | Consensus tier parameters (deferred to Phase 1C) | Multi-parameter decision threshold combinations |

### 3.3 Tools

| Tool | Purpose | Status |
|------|---------|--------|
| `pytest` 9.1+ | Test runner | ✅ Installed |
| `pytest-cov` | Coverage measurement | ⬜ Install: `uv add --dev pytest-cov` |
| `tempfile` | Filesystem isolation for audit log tests | ✅ stdlib |
| `PyNaCl` 1.6.2 | Ed25519 crypto (real implementation, not mocked) | ✅ Installed |
| `allpairspy` | Pairwise test generation | ⬜ Install for Phase 1C |
| `hypothesis` | Property-based testing | ⬜ Optional — install for Phase 1B verification |

### 3.4 Test Data Strategy

| Data Type | Strategy | Example |
|-----------|----------|---------|
| Agent identities | Factory fixture (`make_agent()`) | `make_agent("alice", archetype="Scholar")` |
| Message payloads | Inline dicts | `{"action": "ping"}` |
| Audit log files | Tempfile per test (yield fixture + cleanup) | `tmp_path / "audit.jsonl"` |
| Spawn specs | Static fixture files + inline dicts | `examples/spawn-spec.yaml` |
| Signatures | Real crypto (no mocks) | `identity.sign(message)` |

**Golden rule:** No shared mutable state. Each test gets fresh fixtures. Crypto keys are deterministic (seeded) for reproducibility.

---

## 4. Test Architecture

### 4.1 Directory Structure

```
tests/
├── conftest.py                         # Shared fixtures (alice, bob, temp_log_path, make_agent)
├── test_validator.py                   # Phase 1A — 32 tests (existing)
├── test_identity.py                    # Phase 1B — 13 tests (existing)
├── test_messaging.py                   # Phase 1B — 11 tests (existing)
├── test_audit.py                       # Phase 1B — 14 tests (existing)
├── test_delegate.py                    # Phase 1B — NEW (delegate wrapper + boundary enforcer)
├── integration/
│   ├── conftest.py                     # Integration-specific fixtures
│   ├── test_identity_messaging.py      # Identity → messaging boundary
│   ├── test_messaging_audit.py         # Messaging → audit boundary
│   └── test_full_lifecycle.py          # E2E: spawn → sign → verify → audit
├── fixtures/
│   ├── __init__.py
│   ├── agent_factory.py                # Deterministic agent factory
│   └── sample_payloads.py              # Standard test payloads
├── data/
│   └── sample_spawn_spec.yaml          # Valid spawn spec for validator tests
└── test-plans/
    └── master-test-plan.md             # THIS FILE
```

### 4.2 Fixture Architecture

```python
# tests/conftest.py — shared across all test files
@pytest.fixture
def alice():     -> AgentIdentity("alice", deterministic seed)
@pytest.fixture
def bob():       -> AgentIdentity("bob", deterministic seed)
@pytest.fixture
def temp_path(): -> str (temporary file path, cleaned up after test)

# tests/integration/conftest.py — integration-specific
@pytest.fixture
def audit_log(temp_path): -> AuditLog(temp_path)
@pytest.fixture
def signed_msg(alice):    -> sign_message(alice, {"action": "test"})
```

### 4.3 Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Test file | `test_<module>.py` | `test_delegate.py` |
| Test class | `Test<Feature>` | `TestSignedDelegate` |
| Test method | `test_<behavior>` | `test_signs_task_context_on_spawn` |
| Test case ID | `TC-<MOD>-<NN>` | `TC-DEL-01` |
| Fixture | lowercase descriptive | `def alice()` |
| Integration file | `test_<moduleA>_<moduleB>.py` | `test_identity_messaging.py` |

---

## 6. Entry & Exit Criteria

### 6.1 Entry Criteria (per test phase)

- [ ] Test plan reviewed and approved by QA Engineer / human
- [ ] Test environment: Python 3.13, pytest 9.1+, `uv sync` successful
- [ ] All dependencies installed (PyNaCl, pyyaml, jsonschema, pytest-cov, hypothesis)
- [ ] Baseline: `pytest tests/ -q` — zero failures before any new code
- [ ] Coverage baseline: `pytest --cov=agent_collective` — recorded before additions

### 6.2 Exit Criteria (per test phase)

- [ ] All Critical/High test cases pass
- [ ] Medium/Low failures documented with rationale in `reviews/registry.yaml`
- [ ] Line coverage ≥ 85% per module (measured by `pytest-cov`)
- [ ] Branch coverage ≥ 80% per module
- [ ] No regressions in existing test suite (all previous tests still pass)
- [ ] All findings logged to `reviews/registry.yaml` with severity, status, and fix commit
- [ ] Test plan updated if implementation revealed new test cases

**Regression escalation**: When a Phase N change causes a Phase N-1 test failure:
1. Determine if the failure is a true regression (old behavior broke) or a legitimate contract change (old behavior was intentionally replaced).
2. If true regression: fix the implementation, not the test.
3. If legitimate contract change: update the affected test, document the rationale in the commit message, and have a second engineer review the change.

### 6.3 Phase 1B Gate Criteria

- [ ] **§7.5** delegate.py: 100% of test cases pass
- [ ] **§7.6** BoundaryEnforcer: 100% of test cases pass
- [ ] **§7.7** Integration: full lifecycle test passes
- [ ] Coverage: `agent_collective/identity.py` ≥ 90%, `messaging.py` ≥ 90%, `audit.py` ≥ 85%, `delegate.py` ≥ 85%
- [ ] Findings logged to `reviews/registry.yaml` with review ID R-004
- [ ] Phase 1B gate approved → proceed to Phase 1C

### 6.4 Phase 1C Gate Criteria

- [ ] **§7.8–§7.12**: 100% of test cases pass
- [ ] Coverage: all new modules ≥ 80%
- [ ] Integration test: full proposal lifecycle passes
- [ ] All 5 council spawn specs validate clean
- [ ] Findings logged to `reviews/registry.yaml` with review ID R-005
- [ ] Phase 1 gate criteria met → proceed to Phase 2

---

## 7. Test Design & Test Cases

### 7.1 Phase 1A — Spawn Spec Validator (Retrospective)

**Module:** `agent_collective/validator.py` (342 lines), `agent_collective/cli.py`, `schemas/spawn-schema.json`
**Existing tests:** 32 (all passing)
**Techniques applied:** Equivalence Partitioning, Boundary Value Analysis, Error Guessing

**Test class map (existing):**

| Test Class | Tests | Covers |
|------------|:---:|--------|
| `TestValidateArchetype` | 4 | Known archetypes pass, unknown fails, empty string fails, case sensitivity |
| `TestValidateTenureType` | 2 | Valid types pass, invalid fails |
| `TestValidateCouncil` | 2 | Valid councils pass, invalid fails |
| `TestValidatePermission` | 5 | Read/write/admin pass, invalid format fails, no prefix fails |
| `TestValidateSpawnSpec` | 19 | Full spec validation, missing fields, bad types, crash-path guards, oversight councils, renewal, ethics_path, skills, resources, retirement |

**Coverage gaps identified:**

| Gap | Risk | Mitigation |
|-----|:---:|------------|
| CLI integration tests (only unit tests exist) | Medium | Add `test_cli.py` with subprocess invocation of `agent-collective validate` |
| No test for `--json` flag output format | Low | Add `test_cli_json_output` in Phase 1B |
| No test for malformed YAML file input | Medium | Add `test_malformed_yaml` in Phase 1B |
| No mutation testing to verify test quality | Low | Defer to Phase 2 |

**New test cases to add (Phase 1B):**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-VAL-33 | CLI validates a valid spec file and exits 0 | Error guessing | CLI entry point not tested |
| TC-VAL-34 | CLI rejects invalid spec file and exits non-zero | Error guessing | CLI error path not tested |
| TC-VAL-35 | `--json` flag produces valid JSON output | Error guessing | Machine-parsable output not tested |
| TC-VAL-36 | Malformed YAML produces friendly error, not crash | Error guessing | Parse error handling not tested |
| TC-VAL-37 | All 12 archetypes accepted by `validate_archetype` | EP | Boundary coverage |
| TC-VAL-38 | All 5 councils accepted by `validate_council` | EP | Boundary coverage |

### 7.2 Phase 1B — Agent Identity (Retrospective)

**Module:** `agent_collective/identity.py` (151 lines)
**Existing tests:** 13 (all passing)
**Techniques applied:** Equivalence Partitioning, Error Guessing, Happy Path

**Test class map (existing):**

| Test Class | Tests | Covers |
|------------|:---:|--------|
| `TestGenerateKeypair` | 3 | Returns correct types, different calls = different keys, deterministic from seed |
| `TestAgentIdentity` | 10 | Create, archetype, deterministic seed, string repr, fingerprint, to_dict, from_dict, sign/verify, wrong-msg reject, tampered-sig reject |

**Coverage analysis:**
- `identity.py` has 151 lines with 13 tests. Estimated coverage: ~90%+ (all public functions tested)
- **Untested:** `_expand_secret_key()` internal function (tested indirectly via `sign()`)
- **Untested:** `generate_agent_keypair()` invalid seed length error path
- **Untested:** `AgentIdentity.__init__()` with edge case parameters

**New test cases to add:**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-ID-14 | Invalid seed length raises ValueError | BVA | Error path: 0-byte seed, 33-byte seed |
| TC-ID-15 | Fingerprint is deterministic for same public key | EP | Multiple calls to same identity produce same fingerprint |
| TC-ID-16 | Two different identities produce different fingerprints | EP | Collision resistance (informational) |
| TC-ID-17 | `to_dict()` excludes private_key | Error guessing | Security: private key must not leak to serialization |
| TC-ID-18 | `from_dict()` with missing required key raises KeyError | Error guessing | Deserialization of malformed data |

**Property-Based Invariants (hypothesis required):**

In addition to the example-based tests above, the following invariants should be verified using property-based testing with `hypothesis`. These catch edge cases that example-based tests cannot cover systematically.

```python
from hypothesis import given, strategies as st

# Invariant 1: sign+verify roundtrip succeeds for ALL valid payloads
@given(st.dictionaries(st.text(min_size=1), st.integers(), min_size=1))
def test_sign_verify_roundtrip_property(payload):
    identity = AgentIdentity.create("prop-test")
    msg = sign_message(identity, payload)
    assert verify_message(msg, identity.public_key) is True

# Invariant 2: wrong key NEVER verifies a message from another identity
@given(st.binary(min_size=1, max_size=256))
def test_wrong_key_never_verifies(message):
    alice = AgentIdentity.create("alice")
    bob = AgentIdentity.create("bob")
    # can only sign valid payloads, not raw bytes — adapt as needed
    pass  # Concrete implementation depends on sign_message interface
```

Install: `uv add --dev hypothesis`

### 7.3 Phase 1B — Message Signing (Retrospective)

**Module:** `agent_collective/messaging.py` (139 lines)
**Existing tests:** 11 (all passing)
**Techniques applied:** Equivalence Partitioning, Boundary Value Analysis, Error Guessing, Happy Path

**Test class map (existing):**

| Test Class | Tests | Covers |
|------------|:---:|--------|
| `TestSignAndVerify` | 5 | Sign+verify roundtrip, verify with correct key, wrong key rejects, tampered payload rejects, tampered signature rejects |
| `TestSignedMessageSerialization` | 3 | to_dict, to_json, deterministic hash |
| `TestPayloadValidation` | 3 | Oversized payload rejected, max-size accepted, non-dict rejected |

**Coverage analysis:**
- `messaging.py` has 139 lines with 11 tests. Estimated coverage: ~85%
- **Untested:** `_canonical_json()` edge cases (nested dicts, special characters in keys)
- **Untested:** `verify_message()` with wrong protocol_version (not yet in data model)
- **Untested:** `SignedMessage` constructor with minimal parameters

**New test cases to add:**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-MSG-12 | Canonical JSON is deterministic for same payload with different key order | EP | `sort_keys=True` must produce identical bytes |
| TC-MSG-13 | Empty dict payload is accepted | BVA | Boundary: minimal valid payload |
| TC-MSG-14 | Nested dict payload is correctly serialized and verified | EP | Complex payload structure |
| TC-MSG-15 | Message with special characters in keys is handled | Error guessing | Unicode, null bytes in dict keys |
| TC-MSG-16 | to_json() output is parseable and roundtrips | Error guessing | JSON serialization integrity |

### 7.4 Phase 1B — Audit Trail (Retrospective)

**Module:** `agent_collective/audit.py` (213 lines)
**Existing tests:** 14 (all passing)
**Techniques applied:** State Transition, Equivalence Partitioning, Error Guessing, Tamper Evidence

**Test class map (existing):**

| Test Class | Tests | Covers |
|------------|:---:|--------|
| `TestAuditLogCreation` | 3 | Zero entries, genesis hash, persists to disk |
| `TestAppend` | 3 | Increases count, multiple entries, returns entry ID |
| `TestTamperEvidence` | 3 | Chain intact, tampered entry detected, deleted entry detected |
| `TestQuery` | 5 | Read all, query by sender, query by action, query with limit, empty results |

**Coverage analysis:**
- `audit.py` has 213 lines with 14 tests. Estimated coverage: ~80%
- **Untested:** `AuditLog` re-opening an existing log file restores state correctly
- **Untested:** Race condition on concurrent writes (not applicable — single-threaded)
- **Untested:** `query()` with combined filters (sender_id + action)
- **Untested:** Very large audit log performance (deferred to Phase 2)

**New test cases to add:**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-AUD-15 | Re-opening existing log restores count and last_hash | State transition | Persistence across sessions |
| TC-AUD-16 | Re-opening log and appending links to existing chain | State transition | Chain continuity across sessions |
| TC-AUD-17 | Query with sender_id + action combined filters | EP | Filter combination |
| TC-AUD-18 | Empty log file (genesis only) reports 0 entries | BVA | Boundary: minimal state |
| TC-AUD-19 | 100 consecutive entries maintain chain integrity | Error guessing | Long chain stress test |
| TC-AUD-20 | AuditLog with directory path raises clear error | path="/tmp" | OSError with message containing "is a directory" | Error guessing | File path edge case |
| TC-AUD-21 | AuditLog with path in non-existent directory raises clear error | path="/nonexistent/audit.jsonl" | FileNotFoundError with actionable message | Error guessing | File path edge case |

### 7.5 Phase 1B — Delegate Wrapper (NEW)

**Module:** `agent_collective/delegate.py` (to be built)
**Requirement:** `SignedDelegate` class wrapping `delegate_task` with signing middleware. Each spawned task is signed by the spawning agent's identity.

**Test class:** `TestSignedDelegate`

**Techniques:** Equivalence Partitioning, State Transition, Error Guessing, Decision Tables

**Test design:**

**Equivalence Partitioning:**
| Partition | Valid/Invalid | Values |
|-----------|:---:|--------|
| goal string (1-5000 chars) | Valid | "Implement X", detailed multi-line goal |
| goal string (0 chars) | Invalid | "" |
| identity (valid AgentIdentity) | Valid | alice, bob |
| identity (None) | Invalid | None |
| context (0-10000 chars) | Valid | "", detailed context |
| toolsets (known set) | Valid | ["terminal", "file"] |
| toolsets (empty) | Valid | [] |
| toolsets (unknown tool) | Invalid | ["nonexistent-tool"] |

**Boundary Value Analysis:**
| Boundary | Values |
|----------|--------|
| goal length | 0, 1, 5000, 5001 |
| context length | 0, 1, 10000, 10001 |
| Number of toolsets | 0, 1, 5, 6 |

**Test cases:**

| ID | Description | Preconditions | Input | Expected Output | Technique | Rationale |
|:---|:---|:---|:---|:---|:---:|:---|
| TC-DEL-01 | delegate spawns task with signed goal | Valid identity | goal="test", context={} | Returns task_id, goal is signed | Happy path | Core requirement |
| TC-DEL-02 | Spawned task's context includes signature | Valid identity | goal="test" | context has `_signed_by` dict with: agent_id, fingerprint, signature (hex), message_hash, protocol_version, timestamp | EP | Signing proof |
| TC-DEL-03 | Delegate with None identity raises TypeError | None | goal="test" | TypeError | EP | Invalid input |
| TC-DEL-04 | Delegate with empty goal raises ValueError | Valid identity | goal="" | ValueError | BVA | Boundary at 0 |
| TC-DEL-05 | Delegate with very long goal accepted | Valid identity | goal="x" × 5000 | Returns task_id | BVA | Boundary at max |
| TC-DEL-06 | Delegate with unknown toolset raises ValueError | Valid identity | goal="test", toolsets=["bad-tool"] | ValueError | EP | Invalid toolset |
| TC-DEL-07 | Delegate with empty toolsets list accepted | Valid identity | goal="test", toolsets=[] | Returns task_id | BVA | Empty list boundary |
| TC-DEL-08 | Delegate with all known toolsets accepted | Valid identity | goal="test", toolsets=["terminal","file","web"] | Returns task_id | EP | All valid |


### 7.6 Phase 1B — Boundary Enforcer (NEW)

**Module:** `agent_collective/delegate.py` (to be built — `BoundaryEnforcer` class)
**Requirement:** Checks that an agent's spawn spec permissions are respected before tool access. Agents cannot spawn other agents or modify their own spawn spec.

**Test class:** `TestBoundaryEnforcer`

**Techniques:** Decision Tables, Equivalence Partitioning, Error Guessing, State Transition

**Decision table — spawn permission rules:**

| C1: Agent has spawn ability? | C2: Agent is spawning self? | C3: Target is council agent? | Action |
|:---:|:---:|:---:|:---|
| No | — | — | Deny |
| Yes | Yes | — | Deny (no self-spawn) |
| Yes | No | Yes | Require Tier 3 approval |
| Yes | No | No | Allow |

**Test cases:**

| ID | Description | Preconditions | Input | Expected Output | Technique | Rationale |
|:---|:---|:---|:---|:---|:---:|:---|
| TC-BND-01 | Agent without spawn permission cannot spawn | Agent with perms=[] | spawn_request() | PermissionError | Decision table | C1=No → Deny |
| TC-BND-02 | Agent cannot spawn itself | Any agent | spawn_request(agent_id=self) | PermissionError | Error guessing | Self-spawn prohibited |
| TC-BND-03 | Agent with spawn permission can spawn standard agent | Agent with perms=["spawn"] | spawn_request(new_agent) | Accepted | Happy path | Standard case |
| TC-BND-04 | Agent cannot modify own spawn spec | Any agent | modify_spec(self) | PermissionError | Error guessing | Self-modification prohibited |
| TC-BND-05 | BoundaryEnforcer checks permission before tool access | Agent with perms=["read:knowledge"] | access tool="write:knowledge" | PermissionError | EP | Permission mismatch |
| TC-BND-06 | Agent with matching permission can access tool | Agent with perms=["read:knowledge"] | access tool="read:knowledge" | Accepted | EP | Permission match |
| TC-BND-07 | Empty permissions list blocks all tool access | Agent with perms=[] | access any tool | PermissionError | BVA | Minimal permissions |
| TC-BND-08 | Unknown permission format raises ValueError | Any agent | perms=["invalid_format"] | ValueError | EP | Malformed permission |
| TC-BND-09 | Agent with spawn permission spawning a council agent requires Tier 3 approval | Agent with perms=["spawn"], target is council role | spawn_request(council_agent) | AuthorizationError requiring Tier 3 approval | Decision table | Row 3: council agent spawn bypasses oversight |

### 7.7 Phase 1B — Integration: Full Lifecycle (NEW)

**Test class:** `TestFullLifecycle`

**Techniques:** State Transition, Happy Path, End-to-End

**State transition — full lifecycle:**

```
Start → Create AgentIdentity → Sign Message → Verify Message → Append to Audit Log → Query Audit Log → Verify Integrity
```

**Test cases:**

| ID | Description | Steps | Expected Output | Rationale |
|:---|:---|:---|:---|:---|
| TC-INT-01 | Full lifecycle: spawn → sign → verify → audit | 1. Create identity<br>2. Sign a message<br>3. Verify with correct key<br>4. Append to audit log<br>5. Query log | All steps succeed. Log contains 1 entry. | Core invariant |
| TC-INT-02 | Sign → wrong-key verify → audit (rejected) | 1. Create identity A<br>2. Sign message<br>3. Verify with identity B's key<br>4. Log the rejection | Verify returns False. Log records the rejection. | Wrong-key scenario |
| TC-INT-03 | Sign → tamper payload → verify → audit | 1. Sign message<br>2. Modify payload after signing<br>3. Verify → must fail<br>4. Log tamper detection | Verify returns False. Log records the tamper attempt. | Tamper detection |
| TC-INT-04 | Delegate wrapper → signed spawn → audit | 1. Create identity<br>2. Delegate with signed context<br>3. Verify signature in spawned context<br>4. Log the delegation | Delegate returns task_id. Context has valid signature. | Delegate integration |
| TC-INT-05 | Delegate → boundary enforcement → audit | 1. Create identity without spawn permission<br>2. Attempt to delegate<br>3. BoundaryEnforcer rejects<br>4. Log the rejection | PermissionError raised. Log records the blocked attempt. | Security enforcement |

**Boundary-specific integration tests:**

| ID | Description | Boundary | Steps | Expected Output |
|:---|:---|:---|:---|:---|
| TC-INT-06 | Identity → messaging: sign with valid identity produces valid SignedMessage | identity→messaging | 1. Create identity<br>2. sign_message(identity, payload)<br>3. Verify SignedMessage fields | All SignedMessage fields populated correctly |
| TC-INT-07 | Identity → messaging: sign with identity A, verify with identity B's key fails | identity→messaging | 1. Create identity A<br>2. Sign message<br>3. Verify with identity B's public key | verify_message() returns False |
| TC-INT-08 | Messaging → audit: append signed message and verify log entry | messaging→audit | 1. Sign a message<br>2. Append to AuditLog<br>3. Read back from log | Log entry matches signed message fields |
| TC-INT-09 | Messaging → audit: tamper log entry after append is detected | messaging→audit | 1. Append signed message<br>2. Modify log file directly<br>3. Run verify_integrity() | verify_integrity() returns False |

### 7.8 Phase 1C — Proposal System (Forward)

**Module:** `agent_collective/proposal.py` (to be built)
**Test class:** `TestProposal`

**Techniques:** Equivalence Partitioning, State Transition, Boundary Value Analysis

**Test cases (design level — implement when module is built):**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-PRP-01 | Create valid proposal with all required fields | EP | Happy path |
| TC-PRP-02 | Missing required field raises validation error | EP | Missing title, description, tier, affected_councils |
| TC-PRP-03 | Invalid tier number (0-5 only) rejected | BVA | 0, 5 are valid; -1, 6 are invalid |
| TC-PRP-04 | Triage correctly classifies Tier 0-5 | EP | Each tier maps to correct councils |
| TC-PRP-05 | Invalid council name rejected | EP | Only 5 known councils |
| TC-PRP-06 | Proposal with no affected councils rejected | BVA | Empty list boundary |
| TC-PRP-07 | Archetype disclosure of proposer validated | EP | Must be one of 12 known archetypes |

### 7.9 Phase 1C — Consensus Lifecycle (Forward)

**Module:** `agent_collective/consensus.py` (to be built)
**Test class:** `TestConsensusLifecycle`

**Techniques:** State Transition, Decision Tables, Boundary Value Analysis

**State transition — proposal lifecycle:**

```
Draft → Triage → Deliberation → Voting → Execution → Review
  ↑         ↑           ↑             ↑          ↑
  └─Reject──┴──Reject───┴────Reject───┴──────────┘
```

**Test cases (design level):**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-CNS-01 | Full lifecycle: draft → approved → executed | State transition | Happy path |
| TC-CNS-02 | Proposal rejected at any stage enters terminal state | State transition | Each rejection path |
| TC-CNS-03 | Double-voting prevented | Error guessing | Same agent votes twice |
| TC-CNS-04 | Voting threshold calculation correct for simple majority | Decision table | 3/5 = pass, 2/5 = fail |
| TC-CNS-05 | Voting threshold calculation correct for supermajority | Decision table | 4/5 = pass, 3/5 = fail |
| TC-CNS-06 | Deliberation timer enforces minimum window | BVA | Tier 0=0h, Tier 2=24h, Tier 4=48h |
| TC-CNS-07 | Retrospective dissent pauses execution | State transition | Any agent triggers → paused |
| TC-CNS-08 | Tier escalation (1→4) routes to all councils | State transition | Scaled authority |

### 7.10 Phase 1C — Council Minutes (Forward)

**Module:** `agent_collective/minutes.py` (to be built)
**Test class:** `TestCouncilMinutes`

**Techniques:** Equivalence Partitioning, Error Guessing

**Test cases (design level):**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-MIN-01 | Append minutes entry with all required fields | EP | Happy path |
| TC-MIN-02 | Minutes are append-only (cannot modify past entry) | Error guessing | Immutability |
| TC-MIN-03 | Query minutes by council name | EP | Filter by council |
| TC-MIN-04 | Query minutes by date range | EP | Temporal filter |
| TC-MIN-05 | Minutes with dissenting opinions include dissent field | EP | Guardrail B3 compliance |

### 7.11 Phase 1C — Council Spawn Specs (Forward)

**Files:** `councils/{steering,technical,ethics,knowledge,operations}.yaml`
**Test class:** `TestCouncilSpawnSpecs`

**Test cases (design level):**

| ID | Description | Technique | Rationale |
|:---|:---|:---:|:---|
| TC-CSP-01 | All 5 council spawn specs validate against schema | EP | `agent-collective validate` on each |
| TC-CSP-02 | Each spec has correct archetype for its council | EP | Steering→Wise-Parent-Elder, Technical→Architect-Engineer, etc. |
| TC-CSP-03 | Each spec has correct council_seat.eligible | EP | Only own council |
| TC-CSP-04 | Each spec has non-empty skills list | EP | All agents need at least one skill |
| TC-CSP-05 | Charter document exists for each council | Error guessing | File existence check |

### 7.12 Phase 1C — Integration: Full Proposal Lifecycle (Forward)

**Test class:** `TestFullProposalLifecycle`

**Test cases (design level):**

| ID | Description | Steps | Rationale |
|:---|:---|:---|:---|
| TC-PLC-01 | Create proposal → triage Tier 2 → Technical Council votes → passes → execution → review → log minutes | 7-step lifecycle | Core invariant |
| TC-PLC-02 | Proposal rejected at triage | Proposal with invalid tier | Rejection path |
| TC-PLC-03 | Proposal with retrospective dissent | Lifecycle interrupted by dissent | Safety mechanism |
| TC-PLC-04 | Ethics suspensive veto on Tier 3 decision | Ethics supermajority suspends | Guardrail |
| TC-PLC-05 | Council minutes contain full lifecycle record | All steps logged | Audit trail |

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

- All tests run in isolated temp directories (no shared state between tests)
- Network is not available during tests (no external dependencies)
- Agent identities are created fresh per test (no key reuse)
- Deterministic seeds are used for reproducibility (keypairs are predictable in tests)
- PyNaCl 1.6.2 API is stable (uses `crypto_sign` + `crypto_sign_open` — no `verify_detached`)
- The 4GB microVM has sufficient resources for the test suite (< 60s total runtime)
- No concurrent test execution (single-threaded pytest)

### 8.2 Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| 4GB microVM | No parallel test execution, no large mutation testing | Keep suite under 60s, mutation testing as nightly only |
| PyNaCl 1.6.2 specific API | `crypto_sign_verify_detached` not available | Use `crypto_sign_open` pattern (already implemented) |
| No CI pipeline | Tests run locally only | Document pre-commit gate in §5.1 |
| No pytest-cov installed | Cannot measure coverage | Install: `uv add --dev pytest-cov` |
| No hypothesis installed | No property-based testing | Install for Phase 1B verification pass |

### 8.3 Accepted Risks

| Risk | Rationale | Review Date |
|------|-----------|:---:|
| No mutation testing in Phase 1B | Expensive for 4GB microVM. Defer to Phase 2 gate. | Phase 2 gate |
| No performance/load testing | No multi-agent deployment yet. Meaningless without concurrent agents. | Phase 3 |
| No cross-platform testing | Linux-only microVM. No Windows/Mac target. | Project lifetime |
| CLI integration tests are low priority | Validator is stable (32 tests). CLI is thin wrapper. | Phase 1B |

---

## 9. Test Execution Order

```
Phase 1B Implementation Order (TDD):
  0. Install deps: uv add --dev pytest-cov; uv add --dev hypothesis
  1. TC-DEL-01 → TC-DEL-08    (delegate.py — SignedDelegate)
  2. TC-BND-01 → TC-BND-08    (delegate.py — BoundaryEnforcer)
  3. TC-INT-01 → TC-INT-05    (integration/test_full_lifecycle.py)
  4. TC-VAL-33 → TC-VAL-38    (backfill validator test gaps)
  5. TC-ID-14 → TC-ID-18      (backfill identity test gaps)
  6. TC-MSG-12 → TC-MSG-16    (backfill messaging test gaps)
  7. TC-AUD-15 → TC-AUD-19    (backfill audit test gaps)
  8. Coverage measurement + gap analysis
  9. Findings to reviews/registry.yaml
  10. Phase 1B gate review

Phase 1C Implementation Order (TDD):
  1. TC-PRP-01 → TC-PRP-07    (proposal.py)
  2. TC-CNS-01 → TC-CNS-08    (consensus.py)
  3. TC-MIN-01 → TC-MIN-05    (minutes.py)
  4. TC-CSP-01 → TC-CSP-05    (council YAML files)
  5. TC-PLC-01 → TC-PLC-05    (integration/test_proposal_lifecycle.py)
  6. Phase 1 gate review
```

---

## 10. Review Sign-off

### 10.1 Review Checklist

Before signing off, the reviewer must verify:

- [ ] All risks in §2 have corresponding test coverage in §7
- [ ] Test design techniques in §3.2 are appropriate for each module
- [ ] Test cases are concrete enough for another engineer to execute from the plan alone
- [ ] Entry/Exit criteria in §6 are measurable and complete
- [ ] Assumptions and constraints in §8 are documented and reasonable
- [ ] Test cases are traceable to requirements (ARCHITECTURE.md sections)
- [ ] Directory structure in §4.1 is complete and navigable

### 10.2 Sign-off Table

| Role | Name | Date | Decision |
|------|------|:---:|:---|
| Test Plan Author | QA Engineer (Hermes Agent) | 2026-07-21 | Draft |
| Reviewer | *[human]* | | |
| Approver | *[human]* | | |

*Test plan is approved when all sections are reviewed and the Approver signs off. No implementation begins until approval.*

---

*"Test planning is a design activity, not a verification chore." — QA Engineer skill*