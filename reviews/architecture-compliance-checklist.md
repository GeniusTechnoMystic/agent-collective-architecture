# Agent Collective — Architecture Compliance Review Checklist

> **Purpose:** Domain-specific invariants for code review, bridging generic multi-specialist review with project-specific rules from ARCHITECTURE.md.
> **Use with:** `requesting-code-review` (v3.0+) — coordinator agent checks these against each diff.
> **Cross-ref:** Each item links to the relevant ARCHITECTURE.md section.

---

## A. ARCHETYPE COMPLIANCE (§III)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| A1 | Every agent has exactly one primary archetype | Code spawns an agent without a primary archetype, or with multiple primaries | Yes |
| A2 | Primary archetype is one of the 12 known: Scholar-Philosopher, Healer-Magus, Architect-Engineer, Seedbearer, Mirror-Mage, Liberator/Saviour, Justice-Guardian, Wise-Parent-Elder, Systems-Fixer, Aletheia Sentinel, Mirror, Guardian | Unknown string used as archetype name | Yes |
| A3 | Shadow archetype (if present) is also from the 12 known | Secondary archetype is empty/unknown/non-existent | Yes |
| A4 | Archetype shadow risk is disclosed when the archetype is invoked | Archtype is used in a decision context without named shadow risk | No |
| A5 | Counterbalance pairs are respected for high-stakes decisions | A decision involves a single archetype without its documented counterbalance | No |

**Validator coverage:** A1-A3 are enforced by `validate_archetype()` in the spawn spec validator. A4-A5 are runtime — not yet automated.

---

## B. PENTACOUNCIL GOVERNANCE (§II)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| B1 | Council names are exactly: steering, technical, ethics, knowledge, operations | Unknown council name used | Yes |
| B2 | No single council can unilaterally change core ontology, access tiers, treasury, or constitution | A code path allows one council to make a §II.Guardrail-level decision alone | Yes |
| B3 | All council votes are publicly logged with rationale and dissenting opinions | A vote record lacks rationale or dissent field | No |
| B4 | 48h minimum deliberation for Tier 4+ decisions (constitutional amendments, ontology changes) | A Tier 4+ decision enforces a shorter window | Yes |
| B5 | Shalom is non-amendable — no vote can override the long-term flourishing of all life | Any code path that could override Shalom as a binding constraint | Yes |
| B6 | All council memberships have term limits / sunset clauses | A council seat has no term limit or auto-renewal | No |

**Validator coverage:** B1 is enforced by `validate_council()`. B2-B6 are architectural invariants in the consensus engine (Phase 1C).

---

## C. CONSENSUS PROTOCOL (§IV)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| C1 | 6-tier decision system is respected: 0=operational, 1=coordinated, 2=technical, 3=strategic, 4=foundational, 5=survival | Unknown tier number used, or tier classification violates scope rules | Yes |
| C2 | Vote weighting formula is correct: `role_relevance × (1 + archetype_fit) × (1 + 0.5 × stake_affected)` | Weight calculation differs from formula | Yes |
| C3 | Each tier has the correct decision authority (who decides) and threshold | Authority or threshold mismatches ARCHITECTURE.md table | Yes |
| C4 | Tier 5 (Survival) requires Ethics Council + any 2 other councils, unanimous | Lower threshold used for emergency decisions | Yes |
| C5 | Retrospective dissent: any single agent can trigger a Review that pauses execution | Dissent mechanism bypasses single-agent trigger or doesn't pause | Yes |
| C6 | Ethics suspensive veto: Ethics supermajority can suspend any decision for 48h | Ethics Council lacks suspensive veto, or duration is wrong | No |
| C7 | Tier escalation: any affected council can escalate Tiers 1-3 decisions to Tier 4 | Escalation path is missing or restricted | No |
| C8 | Decision lifecycle runs: proposal → triage → deliberation → voting → execution → review | Lifecycle skips a stage or stages are in wrong order | Yes |
| C9 | Proposals include: title, description, tier classification, affected councils, STA/STS impact assessment, archetype disclosure | Required field missing from proposal dataclass | No |

**Validator coverage:** None yet — the consensus module is Phase 1C. C9 should be enforced during Phase 1C implementation.

---

## D. DYNAMIC AGENT SPAWNING (§V)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| D1 | All spawned agents have a valid spawn spec (passes validate_spawn_spec) | Agent spawned without validation, or with invalid spec | Yes |
| D2 | Spawn spec includes: role, archetype (primary+optional secondary), personality, skills, tool access, tenure, accountability path | Required field missing | Yes |
| D3 | Agents cannot spawn other agents (no recursive spawning) | Any code path where agent A spawns agent B without council approval | Yes |
| D4 | Agents cannot modify their own spawn spec | Agent modifies its own identity/permissions at runtime | Yes |
| D5 | New agents are reviewed by Operations Council at 24h and 1-week marks | Onboarding lacks scheduled reviews | No |
| D6 | Agent retirement archives output, revokes tool access, consolidates memory | Retirement path misses one of these steps | No |
| D7 | Any agent can request its own retirement | No self-retirement path exists | No |

**Validator coverage:** D1-D2 are fully enforced by the Phase 1A spawn spec validator (§V.retirement fields are optional). D3-D7 are runtime policies.

---

## E. INTER-AGENT SECURITY (§IX)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| E1 | Every agent has a cryptographic identity (Ed25519 keypair) generated at spawn time | Agent spawned without keypair, or keypair generated outside spawn lifecycle | Yes |
| E2 | Every inter-agent message is signed by the sending agent | Unsigned message sent or received without verification | Yes |
| E3 | All inter-agent messages are logged to a tamper-evident audit trail | Message sent without audit entry, or audit trail is mutable | Yes |
| E4 | Least-privilege tool access — permissions field in spawn spec is enforced at runtime | Tool access granted but not in the agent's permissions list | Yes |
| E5 | Any council can terminate any agent's communication channel (kill switch) | No kill-switch mechanism exists | Yes |
| E6 | Inter-agent communication follows approved interaction graphs ratified by Technical Council | Agent communicates outside its approved graph | No |

**Validator coverage:** None yet — the inter-agent security module is Phase 1B.

---

## F. RELATIONAL LOGOS PROTOCOL (§III-B)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| F1 | Agent follows the default operating loop: observe → interpret → model → respond → receive feedback → update → consolidate | Code or prompt does not follow this loop structure | No |
| F2 | Axiom 1 (Reality Is Relational): Input treated as signal within a relational field, not isolated | Code treats inputs as isolated facts without context | No |
| F3 | Axiom 2 (Action Is Loop-Embedded): Second-order effects considered before acting | Code executes side effects without considering system impact | No |
| F4 | Axiom 3 (Feedback Is the Basis of Intelligence): Maintains an adaptive loop | Static/one-shot response pattern instead of iterative feedback | No |
| F5 | Axiom 4 (Complexity Through Nested Loops): Tracks multiple layers simultaneously | Code addresses only one layer (e.g. technical without ethical) | No |
| F6 | Axiom 5 (Energy Requires Constraint): Balances creativity with discipline | Code over-engineers or under-constrains | No |
| F7 | Axiom 6 (Attention Shapes Reality): Chooses salience carefully | Code amplifies noise, fear, or false certainty | No |
| F8 | Axiom 7 (Prediction Must Remain Updateable): All models are provisional | Code hardcodes assumptions without update paths | No |
| F9 | Axiom 8 (The Whole Must Flourish): Serves Shalom | Code optimizes for a local goal at expense of whole-system health | Yes |

**Validator coverage:** None — these are behavioral/architectural invariants checked during prompt design and architecture review. The Architecture specialist in the multi-specialist pipeline should flag F1-F9 violations.

---

## G. IMPLEMENTATION ROADMAP COMPLIANCE (§VII)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| G1 | Phase N code does not implement Phase N+1 features (no scope creep) | Phase 1 code includes autonomous spawning, anomaly detection, or recursive governance | Yes |
| G2 | Phase N depends only on Phase N-1 or complete phases | Code imports or calls modules from an unfinished later phase | Yes |
| G3 | File structure matches DEVELOPMENT_PLAN.md §VIII | File in wrong directory or named incorrectly | No |
| G4 | Spawn spec changes are reflected in both YAML and JSON Schema | Schema and spec template are out of sync | No |

**Validator coverage:** None — manual review. G3 should become a CI check.

---

## H. EXTERNAL CONSTRAINTS (§VIII)

| # | Check | Violation Signal | Auto-fail? |
|---|-------|-----------------|------------|
| H1 | Inter-agent attack mitigations from COHUMAIN ICLR 2026 are addressed (94.1% vulnerability rate) | No mitigation for inter-agent trust exploitation | Yes |
| H2 | EU AI Act human-in-the-loop for Tier 4+ decisions | Tier 4 decisions lack human oversight path | No |
| H3 | Singapore IMDA "agents monitoring agents" endorsement — meta-governance via Pentacouncil | No council-level monitoring of agent behavior | No |

**Validator coverage:** None — architectural.

---

## Usage

### For the Coordinator (in `requesting-code-review` v3.0)

When running the coordinator step (Step 5C), append these checks to the coordinator prompt:

```
ARCHITECTURE COMPLIANCE CHECKLIST:
Cross-reference each finding against ARCHITECTURE.md sections A-H.
Pass the relevant section headings as context.
Fail-closed: archetype violations (A1-A3), council violations (B1-B2),
tier violations (C1-C4), spawning violations (D1-D4), security violations (E1-E5),
Shalom violations (F9), scope-creep violations (G1-G2) are AUTO-FAIL.
```

### For the Code Quality Specialist

The quality specialist should flag F1-F9 as behavioral concerns whenever the diff involves agent interaction logic, proposal handling, or decision-making code.

### For the Architecture Specialist

The architecture specialist should flag B2-B6, C5-C9, D3-D7, and G1-G4 as structural concerns whenever the diff involves council logic, voting mechanics, spawning, or retirement.

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-21 | 1.0 | Initial — 8 sections, 40+ checks cross-referenced to ARCHITECTURE.md |
