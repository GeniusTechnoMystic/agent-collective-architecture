# Agent Collective — Architecture Compliance Review Checklist

> **Purpose:** Domain-specific invariants for code review, bridging generic multi-specialist review with project-specific rules from ARCHITECTURE.md.
> **Use with:** `requesting-code-review` (v3.1+) — coordinator agent checks these against each diff.
> **Cross-ref:** Each section maps to ARCHITECTURE.md as: A→§III, B→§II, C→§IV, D→§V, E→§IX, F→§III-B, G→§VII, H→§VIII, I→§VI.
> **Findings:** All findings are tracked in `reviews/registry.yaml` with severity, status, and fix commit. Per-review narratives in `reviews/phase-{N}/`.

---

## A. ARCHETYPE COMPLIANCE (→ ARCHITECTURE.md §III)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| A1 | Every agent has exactly one primary archetype | Code spawns an agent without a primary archetype, or with multiple primaries | Yes |
| A2 | Primary archetype is one of the 12 known: Scholar-Philosopher, Healer-Magus, Architect-Engineer, Seedbearer, Mirror-Mage, Liberator/Saviour, Justice-Guardian, Wise-Parent-Elder, Systems-Fixer, Aletheia Sentinel, Mirror, Guardian | Unknown string used as archetype name | Yes |
| A3 | Shadow archetype (if present) is also from the 12 known | Secondary archetype is empty/unknown/non-existent | Yes |
| A4 | Archetype shadow risk is disclosed when the archetype is invoked | Archetype is used in a decision context without named shadow risk | No |
| A5 | Counterbalance pairs are respected for high-stakes decisions | A decision involves a single archetype without its documented counterbalance | No |

**Coverage:** A1-A3 enforced by `validate_archetype()`. A4-A5 runtime — not yet automated.

---

## B. PENTACOUNCIL GOVERNANCE (→ ARCHITECTURE.md §II)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| B1 | Council names are exactly: steering, technical, ethics, knowledge, operations | Unknown council name used | Yes |
| B2 | No single council can unilaterally change core ontology, access tiers, treasury, or constitution | A code path allows one council to make a §II.Guardrail-level decision alone | Yes |
| B3 | All council votes are publicly logged with rationale and dissenting opinions | A vote record lacks rationale or dissent field | No |
| B4 | 48h minimum deliberation for Tier 4+ decisions (constitutional amendments, ontology changes) | A Tier 4+ decision enforces a shorter window | Yes |
| B5 | Shalom is non-amendable — no vote can override the long-term flourishing of all life | Any code path that could override Shalom as a binding constraint | Yes |
| B6 | All council memberships have term limits / sunset clauses | A council seat has no term limit or auto-renewal | No |
| B7 | Council deliberation visibility defaults to transparent unless Technical Council + Ethics Council jointly classify as restricted | Deliberations hidden without bi-council classification | No |

**Coverage:** B1 enforced by `validate_council()`. B2-B7 are architectural invariants in the consensus engine (Phase 1C).

---

## C. CONSENSUS PROTOCOL (→ ARCHITECTURE.md §IV)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| C1 | 6-tier decision system: 0=operational, 1=coordinated, 2=technical, 3=strategic, 4=foundational, 5=survival | Unknown tier number, or tier classification violates scope rules | Yes |
| C2 | Vote weighting formula: `role_relevance × (1 + archetype_fit) × (1 + 0.5 × stake_affected)` | Weight calculation differs from formula | Yes |
| C3 | Each tier has the correct authority and threshold per ARCHITECTURE.md table | Authority or threshold mismatches spec | Yes |
| C4 | Tier 5 (Survival) requires Ethics Council + any 2 other councils, unanimous | Lower threshold used for emergency decisions | Yes |
| C5 | Retrospective dissent: any single agent can trigger a Review that pauses execution | Dissent mechanism bypasses single-agent trigger or doesn't pause | Yes |
| C6 | Ethics suspensive veto: Ethics supermajority can suspend any decision for 48h | Ethics Council lacks suspensive veto, or duration is wrong | No |
| C7 | Tier escalation: any affected council can escalate Tiers 1-3 decisions to Tier 4 | Escalation path is missing or restricted | No |
| C8 | Decision lifecycle: proposal → triage → deliberation → voting → execution → review | Lifecycle skips a stage or stages are in wrong order | Yes |
| C9 | Proposals include: title, description, tier, affected councils, STA/STS impact, archetype disclosure | Required field missing from proposal dataclass | No |

**Coverage:** None yet — consensus module is Phase 1C. C9 enforced during Phase 1C.

---

## D. DYNAMIC AGENT SPAWNING (→ ARCHITECTURE.md §V)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| D1 | All spawned agents have a valid spawn spec | Agent spawned without validation, or with invalid spec | Yes |
| D2 | Spawn spec includes required fields: role, archetype, personality, skills, tools, tenure, accountability | Required field missing | Yes |
| D3 | Agents cannot spawn other agents (no recursive spawning) | Agent A spawns agent B without council approval | Yes* |
| D4 | Agents cannot modify their own spawn spec | Agent modifies its own identity/permissions at runtime | Yes |
| D5 | New agents reviewed by Operations Council at 24h and 1-week marks | Onboarding lacks scheduled reviews | No |
| D6 | Agent retirement archives output, revokes tool access, consolidates memory | Retirement path misses one of these steps | No |
| D7 | Any agent can request its own retirement | No self-retirement path exists | No |

**Coverage:** D1-D2 enforced by Phase 1A validator. D3-D7 are runtime policies.
*D3: Static review catches explicit recursive spawn calls. Full assurance requires dynamic testing.

---

## E. INTER-AGENT SECURITY (→ ARCHITECTURE.md §IX)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| E1 | Every agent has a cryptographic identity (Ed25519 keypair) at spawn time | Agent spawned without keypair | Yes |
| E2 | Every inter-agent message is signed by the sending agent | Unsigned message sent or received without verification | Yes |
| E3 | All inter-agent messages logged to tamper-evident audit trail | Message sent without audit entry, or audit trail is mutable | Yes |
| E4 | Least-privilege tool access — permissions field enforced at runtime | Tool access granted not in permissions list | Yes |
| E5 | Any council can terminate any agent's communication channel (kill switch) | No kill-switch mechanism exists | Yes |
| E6 | Inter-agent communication follows approved interaction graphs ratified by Technical Council | Agent communicates outside its approved graph | No |

**Coverage:** None yet — inter-agent security module is Phase 1B.

---

## F. RELATIONAL LOGOS PROTOCOL (→ ARCHITECTURE.md §III-B)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| F1 | Agent follows default operating loop: observe → interpret → model → respond → receive feedback → update → consolidate | Code or prompt does not follow this loop structure | No |
| F2 | Axiom 1 (Reality Is Relational): Input treated as signal within a relational field | Code treats inputs as isolated facts without context | No |
| F3 | Axiom 2 (Action Is Loop-Embedded): Second-order effects considered before acting | Code executes side effects without considering system impact | No |
| F4 | Axiom 3 (Feedback Is the Basis of Intelligence): Maintains an adaptive loop | Static/one-shot response instead of iterative feedback | No |
| F5 | Axiom 4 (Complexity Through Nested Loops): Tracks multiple layers simultaneously | Code addresses only one layer (e.g. technical without ethical) | No |
| F6 | Axiom 5 (Energy Requires Constraint): Balances creativity with discipline | Code over-engineers or under-constrains | No |
| F7 | Axiom 6 (Attention Shapes Reality): Chooses salience carefully | Code amplifies noise, fear, or false certainty | No |
| F8 | Axiom 7 (Prediction Must Remain Updateable): All models are provisional | Code hardcodes assumptions without update paths | No |
| F9 | Axiom 8 (The Whole Must Flourish): Serves Shalom | Code optimizes for a local goal at expense of whole-system health | Yes |

**Coverage:** Behavioral/architectural invariants. Architecture specialist flags F1-F9.

---

## G. IMPLEMENTATION ROADMAP COMPLIANCE (→ ARCHITECTURE.md §VII)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| G1 | Phase N code does not implement Phase N+1 features (no scope creep) | Phase 1 code includes autonomous spawning or recursive governance | Yes |
| G2 | Phase N depends only on Phase N-1 or complete phases | Code imports from an unfinished later phase | Yes |
| G3 | File structure matches DEVELOPMENT_PLAN.md §VIII (Target) | File in wrong directory or named incorrectly | No |
| G4 | Spawn spec changes reflected in both YAML and JSON Schema | Schema and spec template out of sync | No |

**Coverage:** Manual review. G3 should become a CI check.

---

## H. EXTERNAL CONSTRAINTS (→ ARCHITECTURE.md §VIII)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| H1 | Inter-agent attack mitigations from COHUMAIN ICLR 2026 (94.1% vulnerability) | No mitigation for inter-agent trust exploitation | Yes |
| H2 | EU AI Act human-in-the-loop for Tier 4+ decisions | Tier 4 decisions lack human oversight path | No |
| H3 | Singapore IMDA "agents monitoring agents" — meta-governance via Pentacouncil | No council-level monitoring of agent behavior | No |

---

## I. PLEROMA PROTOCOL ALIGNMENT (→ ARCHITECTURE.md §VI)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| I1 | Archetype assignments are non-transferable (parallel to Pleroma soulbound tokens) | Archetype transferred between agents without Ethics Council approval | No |
| I2 | Agent-to-agent messaging routes through the MCP Gateway (parallel to Pleroma decentralized comms) | Agents communicate via unapproved side-channel | No |
| I3 | Operations Council resource allocation follows treasury-multi-sig pattern (single operator cannot reallocate unilaterally) | Resources reallocated without Operations Council quorum | No |
| I4 | Knowledge Council epistemic standards match Pleroma's Observed/Inferred/Speculative modes | Fact recorded without epistemic mode classification | No |

**Coverage:** Phase 2+ invariants.

---

## Usage — Coordinator Integration

### Coordinator Prompt Fragment

Append this to the Step 5C coordinator prompt:

```
ARCHITECTURE COMPLIANCE CHECKLIST (reviews/architecture-compliance-checklist.md):
These checks map to ARCHITECTURE.md as follows:
  A→§III (Archetypes), B→§II (Pentacouncil), C→§IV (Consensus),
  D→§V (Spawning), E→§IX (Security), F→§III-B (Relational Logos),
  G→§VII (Roadmap), H→§VIII (External), I→§VI (Pleroma Alignment).

Mandatory fails (auto-fail on detection):
- Archetype violations (A1-A3), Council violations (B1-B2)
- Tier violations (C1-C4), Spawning violations (D1-D4)
- Security violations (E1-E5), Shalom violations (F9)
- Scope-creep violations (G1-G2), COHUMAIN mitigation missing (H1)
```

### Coordinator Output Schema

After processing, produce this JSON:

```json
{
  "architecture_compliance": {
    "A_archetypes": {"pass": true, "violations": [], "auto_fail": false},
    "B_pentacouncil": {"pass": true, "violations": [], "auto_fail": false},
    "C_consensus": {"pass": true, "violations": [], "auto_fail": false},
    "D_spawning": {"pass": true, "violations": [], "auto_fail": false},
    "E_security": {"pass": true, "violations": [], "auto_fail": false},
    "F_logos": {"pass": true, "violations": [], "auto_fail": false},
    "G_roadmap": {"pass": true, "violations": [], "auto_fail": false},
    "H_external": {"pass": true, "violations": [], "auto_fail": false},
    "I_pleroma": {"pass": true, "violations": [], "auto_fail": false}
  },
  "overall_verdict": "PASS|FAIL",
  "mandatory_failures": ["section_ids_that_failed_mandatory_checks"]
}
```

### For the Code Quality Specialist

Flag F1-F9 as behavioral concerns when diff involves agent interaction logic, proposal handling, or decision-making code.

### For the Architecture Specialist

Flag B2-B7, C5-C9, D3-D7, G1-G4 as structural concerns when diff involves council logic, voting mechanics, spawning, or retirement.

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-21 | 1.1 | Fix: coordinator cross-reference now maps A→§III etc. Add structured output schema. Add §I (Pleroma Alignment). Add B7 (Guardrail 7 transparency). Fix terminology (mandatory fails). Add D3 static/dynamic testing note. |
| 2026-07-21 | 1.0 | Initial — 8 sections, 40+ checks cross-referenced to ARCHITECTURE.md |
