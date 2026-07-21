# Agent Collective Architecture — Full Development Plan

> **Telos:** Build a self-orchestrating networked organization of AI agents with consensus-based governance
> **Status:** Phase 0 complete (design) → Phase 1 starts here
> **Repo:** `https://github.com/GeniusTechnoMystic/agent-collective-architecture`

---

## I. DEVELOPMENT PROCESS & PARADIGMS

### 1.1 Methodology Stack

| Paradigm | When | Why |
|----------|------|-----|
| **Plan mode** | Before every Phase | Bite-sized tasks, exact paths, complete code. No execution during planning |
| **TDD (RED-GREEN-REFACTOR)** | Every code task | Test first → watch fail → minimal code → watch pass → refactor. Non-negotiable |
| **Vertical tracer bullets** | Per feature | One end-to-end behavior slice at a time, not horizontal slices |
| **Subagent-driven development** | Per task | Fresh `delegate_task` per task with full context. Two-stage review (spec compliance then code quality) |
| **Code red-team** | After each Phase | Adversarial review before marking phase complete. Security + correctness + edge cases |
| **Session journaling** | End of each session | Document what was built, decisions made, pickup line for next session |
| **Frequent commits** | After every task | `git commit -m "type: description"` — never batch unrelated changes |
| **Dogfooding** | Throughout | The collective builds itself. Phase 1 tools are used to spawn Phase 2 agents |

### 1.2 The Build Loop

```
┌─────────────────────────────────────────────────────┐
│                 PER TASK                              │
│                                                       │
│  Plan (you) → Subagent → TDD Cycle → Tests Pass      │
│       → Red-team Review → Commit → Journal            │
│                                                       │
│  Where TDD Cycle = RED → GREEN → REFACTOR             │
│  (failing test → minimal code → clean up)             │
└─────────────────────────────────────────────────────┘
```

### 1.3 Agent Roles in the Development Process

| Role | Archetype | Function |
|------|-----------|----------|
| **Chief Architect** (you) | Wise-Elder + Architect-Engineer | Strategic direction, approves plans, reviews output |
| **Implementation Agent** | Architect-Engineer | Writes code via TDD per task specs |
| **Red-Team Agent** | Aletheia Sentinel + Systems-Fixer | Adversarial review of deliverables before phase closure |
| **Knowledge Steward** | Scholar-Philosopher | Documents decisions, updates knowledge graph, writes journals |

---

## II. PHASE 1 — FOUNDATIONS (Build the Spawning Layer)

**Paradigm focus**: Infrastructure-as-code + TDD. Every component testable in isolation.
**Spawned agents needed**: Implementation agents via `delegate_task` per issue.

### Issue #1: Spawn Spec YAML Validator

**Deliverables:**

| Artifact | Format | Location |
|----------|--------|----------|
| JSON Schema for spawn spec | `spawn-schema.json` | `repo/schemas/spawn-schema.json` |
| Python validator library | Python module | `repo/agent_collective/validator.py` |
| CLI entry point | `agent-collective` script | `repo/agent_collective/cli.py` |
| Unit tests | pytest | `repo/tests/test_validator.py` |
| Example valid specs | YAML files | `repo/examples/*.yaml` |

**Components to build (TDD, one at a time):**

1. `validate_archetype(name)` — checks against 12 known archetypes
2. `validate_personality(name)` — checks against 67 Hermes personalities
3. `validate_tenure(tenure)` — checks task/epoch/indefinite
4. `validate_council_seat(seat)` — checks against 5 councils
5. `validate_permissions(perms)` — checks read/write/admin format
6. `validate_spawn_spec(yaml_path)` — full document validation
7. `CLI: agent-collective validate <path>` — command-line entry point
8. `spawn-schema.json` — formal JSON Schema published to repo

**Verification:** `pytest tests/ -v` — 100% pass. `agent-collective validate examples/valid.yaml` — exits 0 with "VALID".

### Issue #2: Inter-Agent Security Protocol

**Deliverables:**

| Artifact | Format | Location |
|----------|--------|----------|
| Agent identity module | Python module | `repo/agent_collective/identity.py` |
| Message signing module | Python module | `repo/agent_collective/messaging.py` |
| Audit trail module | Python module | `repo/agent_collective/audit.py` |
| Keypair generation | Ed25519 via libsodium | `identity.py` |
| delegate_task wrapper with signing | Middleware | `repo/agent_collective/delegate.py` |
| Unit tests | pytest | `repo/tests/test_identity.py`, `test_messaging.py`, `test_audit.py` |

**Components to build (TDD, one at a time):**

1. `generate_agent_keypair()` — Ed25519 keypair, returns (private_key, public_key)
2. `sign_message(message, private_key)` — returns signature
3. `verify_message(message, signature, public_key)` — returns bool
4. `AgentIdentity` class — wraps keypair + identity metadata
5. `AuditLog` class — append-only log with tamper evidence
6. `SignedDelegate` wrapper — wraps `delegate_task` with signing middleware
7. `BoundaryEnforcer` — checks spawn spec permissions before tool access
8. Integration test: spawn → sign → verify → audit → decommission

**Verification:** `pytest tests/ -v` — 100% pass. Manual: spawn a test agent with keypair, sign a message, verify it, check audit log.

### Issue #3: Minimal Pentacouncil Bootstrap

**Deliverables:**

| Artifact | Format | Location |
|----------|--------|----------|
| Council agent spawn specs | 5 YAML files | `repo/councils/steering.yaml`, `technical.yaml`, `ethics.yaml`, `knowledge.yaml`, `operations.yaml` |
| Council charters | 5 Markdown docs | `repo/councils/charters/steering.md`, etc. |
| Decision lifecycle implementation | Python module | `repo/agent_collective/consensus.py` |
| Proposal system | Python module | `repo/agent_collective/proposal.py` |
| Council minutes logger | Python module | `repo/agent_collective/minutes.py` |
| Integration test: full proposal lifecycle | pytest | `repo/tests/test_consensus.py` |

**Components to build (TDD, one at a time):**

1. `Proposal` dataclass — title, description, tier, affected_councils, proposer_archetype
2. `DecisionTriage` — classifies Tier 0-5, routes to council
3. `CouncilVote` — records agent votes, checks thresholds
4. `DeliberationTimer` — enforces minimum deliberation windows per tier
5. `ConsensusLifecycle` — orchestrates proposal → triage → deliberation → voting → execution → review
6. `CouncilMinutes` — append-only log of all proposals, votes, outcomes
7. `RetrospectiveDissent` — any agent triggers Review, pauses execution
8. Five spawn specs for council agents, correctly archetyped
9. Integration test: create proposal → triage Tier 2 → Technical Council votes → passes → execution → review → log minutes

**Verification:** Integration test passes end-to-end. All 5 council specs validate clean. Minutes file contains the test proposal lifecycle.

### Phase 1 Gate Criteria

- [ ] `pytest tests/ -v` — 100% pass, zero warnings
- [ ] Red-team review passes (no Critical/High findings)
- [ ] All 3 issues closed on GitHub
- [ ] `agent-collective validate examples/*.yaml` — all pass
- [ ] Integration test: spawn identity → sign message → verify → audit
- [ ] Integration test: proposal → triage → vote → execution → review → minutes
- [ ] Repo README updated with Phase 1 completion badge

---

## III. PHASE 2 — COUNCIL AUTOMATION (Voting & Deliberation)

**Paradigm focus**: State machines + event sourcing. Council decisions are events.
**Spawned agents needed**: 5 council agents (one per council) + integrate with the Pentacouncil from Phase 1.

### Deliverables

| Artifact | Format | Description |
|----------|--------|-------------|
| Weighted voting implementation | Python | `vote_weight = role_relevance × (1 + archetype_fit) × (1 + 0.5 × stake)` |
| Deliberation channels | Gateway messaging | Council agents can deliberate asynchronously via MCP |
| Decision logger | Event store | Every proposal, vote, and outcome logged to append-only store |
| Triage automation | Python | Operations Council auto-triage based on Tier classification |
| Ethics dispute tracking | Python | Formal dispute record with appeal path |
| Inter-agent communication policy | YAML | Which agent pairs may communicate directly, ratified by Technical Council |
| Council dashboard | Markdown + CLI | `agent-collective council status` — shows pending proposals, recent votes |

### Agent Roles to Spawn

| Agent | Archetype | Task |
|-------|-----------|------|
| Steering Council agent | Wise-Elder | Chairs strategic decisions |
| Technical Council agent | Architect-Engineer | Chairs infrastructure decisions |
| Ethics Council agent | Mirror-Mage | Chairs alignment/dispute decisions |
| Knowledge Council agent | Scholar-Philosopher | Chairs ontology/knowledge decisions |
| Operations Council agent | Healer-Magus | Chairs resource allocation |
| **Voting implementation agent** | Systems-Fixer | Builds the weighted voting engine (TDD) |

### Phase 2 Gate Criteria

- [ ] `agent-collective propose` — submits and routes proposal correctly
- [ ] `agent-collective council status` — shows pending proposals
- [ ] Ethics dispute: file dispute → Ethics Council deliberates → resolution
- [ ] Weighted voting: same proposal, different archetypes produce different vote weights
- [ ] All council minutes queryable
- [ ] Inter-agent communication policy ratified and enforced

---

## IV. PHASE 3 — MULTI-AGENT ORCHESTRATION (Autonomy)

**Paradigm focus**: Autonomous systems + monitoring. Agents spawn and retire without human intervention.
**Spawned agents needed**: Multiple. This is where the collective becomes self-sustaining.

### Deliverables

| Artifact | Format | Description |
|----------|--------|-------------|
| Autonomous spawning | Python + delegate_task | Operations Council can spawn agents without approval for Tier 0-1 |
| Archetype switching | Runtime config | Agents can context-switch to secondary archetype |
| Retirement workflows | Python | Auto-archive output, revoke tool access, consolidate memory |
| Workload balancing | Python | Operations Council monitors agent load, adjusts spawns |
| Anomaly detection | Python + gateway | Monitors inter-agent message patterns for attacks |
| Health dashboard | CLI | `agent-collective health` — agent status, council stats, resource usage |

### Agent Roles to Spawn

| Agent | Archetype | Task |
|-------|-----------|------|
| Spawn orchestrator | Architect-Engineer | Manages the spawn/retire lifecycle |
| Workload monitor | Healer-Magus | Balances agent load, detects burnout |
| Anomaly detector | Aletheia Sentinel | Monitors inter-agent patterns for attacks |
| Archetype registrar | Scholar-Philosopher | Manages archetype definitions and switching |
| Agent health reporter | Systems-Fixer | Produces health dashboard data |

### Phase 3 Gate Criteria

- [ ] Agent spawns autonomously via Operations Council decision
- [ ] Agent context-switches archetype mid-task
- [ ] Agent retires, output archived, tools revoked
- [ ] Anomaly detector catches inter-agent attack pattern
- [ ] `agent-collective health` shows live status
- [ ] Workload balancer prevents agent overload

---

## V. PHASE 4 — RECURSIVE GOVERNANCE (Self-Improvement)

**Paradigm focus**: Meta-governance + protocol evolution. The collective governs its own governance.

### Deliverables

| Artifact | Format | Description |
|----------|--------|-------------|
| Protocol amendment process | Python | Any 2 councils jointly propose changes to consensus protocol |
| Council composition evolution | Python | Steering Council can restructure councils |
| Archetype innovation process | Python | Knowledge Council proposes new archetypes, Ethics reviews, Technical implements |
| Collective self-improvement | Automated | Agents audit their own performance and suggest improvements |
| ISO/IEC 42001 mapping | Markdown | AI management system compliance reference |
| External regulatory alignment | Markdown | EU AI Act, NIST AI RMF 2025, Singapore IMDA mapping |

### Agent Roles to Spawn

| Agent | Archetype | Task |
|-------|-----------|------|
| Constitutional reviewer | Justice-Guardian | Ensures all changes align with Shalom telos |
| Protocol amendment agent | Wise-Elder + Systems-Fixer | Manages the amendment lifecycle |
| Compliance auditor | Aletheia Sentinel | Maps architecture to regulatory frameworks |
| Meta-governance observer | Mirror-Mage | Monitors the quality of governance itself |

### Phase 4 Gate Criteria

- [ ] Protocol amendment: 2 councils propose → all 5 vote → ratified
- [ ] New archetype proposed → Knowledge approves → Ethics reviews → Technical implements
- [ ] Council composition changed → Steering ratifies → 3/5 majority
- [ ] ISO/IEC 42001 mapping complete
- [ ] EU AI Act human-in-the-loop requirement satisfied for Tier 4+
- [ ] Collective can propose and ratify improvements to its own governance

---

## VI. AGENT SPAWNING MAP — Who Builds What

### Phase 1 Agents (Implementation, spawned via delegate_task)

| Task | Agent Archetype | Skills Needed | Spawn Duration |
|------|-----------------|---------------|----------------|
| Spawn spec validator | Architect-Engineer | Python, JSON Schema, TDD, CLI design | 2-3 sessions |
| Identity + signing module | Systems-Fixer | Cryptography (Ed25519), Python, TDD | 1 session |
| Audit trail module | Aletheia Sentinel | Python, append-only stores, tamper evidence | 1 session |
| delegate_task signing wrapper | Architect-Engineer | Hermes delegate_task, Python | 1 session |
| Proposal system | Scholar-Philosopher | Data modeling, state machines, TDD | 1 session |
| Consensus lifecycle | Systems-Fixer | Workflow orchestration, TDD | 2 sessions |
| Council spec YAMLs | Seedbearer | YAML writing, detailed documentation | 1 session |

### Phase 2 Agents

| Task | Agent Archetype | Skills Needed | Spawn Duration |
|------|-----------------|---------------|----------------|
| Weighted voting engine | Scholar-Philosopher | Algorithm design, TDD | 1 session |
| Ethics dispute tracker | Justice-Guardian | State machine, case management | 1 session |
| Deliberation timer | Systems-Fixer | Time-based scheduling | 1 session |
| Council dashboard | Architect-Engineer | CLI UX, Python | 1 session |

### Phase 3 Agents

| Task | Agent Archetype | Skills Needed | Spawn Duration |
|------|-----------------|---------------|----------------|
| Autonomous spawning | Architect-Engineer | delegate_task orchestration, lifecycle mgmt | 2 sessions |
| Archetype switcher | Mirror-Mage | Runtime config, context management | 1 session |
| Anomaly detector | Aletheia Sentinel | Pattern matching, security monitoring | 2 sessions |
| Workload balancer | Healer-Magus | Resource monitoring, scheduling | 1 session |

### Phase 4 Agents

| Task | Agent Archetype | Skills Needed | Spawn Duration |
|------|-----------------|---------------|----------------|
| Amendment process | Wise-Elder | Constitutional design, protocol logic | 2 sessions |
| Compliance auditor | Aletheia Sentinel | Regulatory analysis, documentation | 2 sessions |
| Meta-governance observer | Mirror-Mage | Quality metrics, introspection | 1 session |

---

## VII. RISKS & MITIGATIONS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **delegate_task limitations** | Medium | High — spawning mechanism is foundational | Test boundary early in Phase 1. Have fallback (direct terminal spawning) |
| **Inter-agent attack during testing** | Medium | High — 94.1% model vulnerability rate | Phase 1B (security protocol) must precede any multi-agent test |
| **Cognitive load of 5 simultaneous council agents** | High | Medium — 4GB microVM | Phase 1 uses human-in-the-loop. Scale to 5 agents only when infrastructure can support it |
| **Architecture drift from design** | Medium | Medium — implementation may diverge | Red-team review at end of each phase. Design doc updated when implementation reveals gaps |
| **GitHub auth for automated pushes** | Low | Medium — initial setup needed | gh auth or PAT configured early |
| **TDD friction with exploration** | Medium | Low — temptation to skip tests | Enforce TDD in subagent goals. Red-team checks for test coverage |
| **Phase scope creep** | High | Medium — each Phase can expand | Gate criteria are hard boundaries. No Phase N+1 until Phase N gate passes |

---

## VIII. REPO STRUCTURE (Final)

```
agent-collective-architecture/
├── README.md                        # Project overview, badges, quick-start
├── ARCHITECTURE.md                  # Design specification (Phase 0 output)
├── LICENSE                          # MIT
├── schemas/
│   └── spawn-schema.json            # JSON Schema for spawn spec validation
├── agent_collective/
│   ├── __init__.py
│   ├── validator.py                 # Spawn spec YAML validator
│   ├── identity.py                  # Agent identity + Ed25519 keypairs
│   ├── messaging.py                 # Message signing + verification
│   ├── audit.py                     # Append-only audit trail
│   ├── delegate.py                  # Signed delegate_task wrapper
│   ├── proposal.py                  # Proposal dataclass + lifecycle
│   ├── consensus.py                 # Voting mechanics + tiers
│   ├── minutes.py                   # Council minutes logger
│   └── cli.py                       # CLI entry point
├── councils/
│   ├── steering.yaml                # Spawn specs for council agents
│   ├── technical.yaml
│   ├── ethics.yaml
│   ├── knowledge.yaml
│   ├── operations.yaml
│   └── charters/
│       ├── steering.md
│       ├── technical.md
│       ├── ethics.md
│       ├── knowledge.md
│       └── operations.md
├── examples/
│   └── spawn-spec.yaml              # Example valid spawn spec
├── tests/
│   ├── test_validator.py
│   ├── test_identity.py
│   ├── test_messaging.py
│   ├── test_audit.py
│   ├── test_proposal.py
│   ├── test_consensus.py
│   └── test_integration.py          # End-to-end lifecycle test
└── .github/
    └── ISSUE_TEMPLATE.md            # Standard issue template for tasks
```

---

## IX. EXECUTION ORDER

```text
Phase 1:
  ├── Issue #1: Spawn spec validator (foundation — everything depends on valid specs)
  │     Task 1.1: JSON Schema for spawn spec
  │     Task 1.2: archetype/personality/tenure/council validators
  │     Task 1.3: full document validator
  │     Task 1.4: CLI entry point
  │     Task 1.5: example YAMLs + tests
  │     Task 1.6: red-team review
  │
  ├── Issue #2: Inter-agent security (safety — must precede any multi-agent test)
  │     Task 2.1: identity module + keypairs
  │     Task 2.2: message signing/verification
  │     Task 2.3: audit trail
  │     Task 2.4: delegate_task signing wrapper
  │     Task 2.5: boundary enforcer
  │     Task 2.6: integration test + red-team review
  │
  └── Issue #3: Minimal Pentacouncil (capstone — proves the architecture works)
        Task 3.1: proposal dataclass + triage
        Task 3.2: voting mechanics + thresholds
        Task 3.3: deliberation timer
        Task 3.4: consensus lifecycle orchestrator
        Task 3.5: council minutes logger
        Task 3.6: retrospective dissent
        Task 3.7: 5 council spawn specs + charters
        Task 3.8: end-to-end integration test
        Task 3.9: red-team review

Phase 1 Gate → proceed to Phase 2

Phase 2: Council Automation (voting + deliberation)
Phase 3: Multi-Agent Orchestration (autonomy)
Phase 4: Recursive Governance (self-improvement)
```

---

## X. QUICK-START — First Task

When ready to begin Phase 1:

```bash
# Clone the repo
git clone https://github.com/GeniusTechnoMystic/agent-collective-architecture.git
cd agent-collective-architecture

# Set up Python project structure
mkdir -p agent_collective tests schemas councils/charters examples

# Install test runner
uv add --dev pytest

# First TDD cycle: write failing test for validate_archetype()
vi tests/test_validator.py
# ... (covered in Issue #1 Task 1.1)

pytest tests/test_validator.py -v  # RED

# Implement
vi agent_collective/validator.py

pytest tests/test_validator.py -v  # GREEN

# Commit
git add tests/test_validator.py agent_collective/validator.py
git commit -m "feat: add validate_archetype with 12 known archetypes"
```
