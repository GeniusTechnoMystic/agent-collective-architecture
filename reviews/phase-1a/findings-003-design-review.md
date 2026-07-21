# Review R-003: Phase 0 — Architecture Design Review

> **Date:** 2026-07-20
> **Reviewer:** Architect-Engineer
> **Scope:** `ARCHITECTURE.md` §I–§IX (725 lines)
> **Result:** CONDITIONAL → FIXED (commits `2ea14d3` + `f170de5`)
> **Registry:** `reviews/registry.yaml` (findings C-01 through C-03, H-01 through H-10, MS-01 through MS-05)

## Summary

The full ARCHITECTURE.md spec (725 lines, 9 sections) was reviewed for design consistency, completeness, and architectural soundness. The review found **3 critical issues** (dangling reference, ambiguous dispute boundary, naming inconsistency), **11 high issues** (threshold ambiguity, missing protocol details, security gaps), and **5 medium issues** (missing operational sections). All fixed across two commits.

## Critical Fixes (commit `2ea14d3`)

### C-01: Explorer archetype — dangling reference

The Explorer archetype was referenced as a counterbalance for Guardian but never defined in the 12-archetype system. It was a remnant from an earlier draft.

**Fix:** Removed Explorer. Guardian counterbalance now uses Seedbearer (for possibility) + Liberator/Saviour (for growth).

### C-02: Steering vs Ethics dispute boundary

Both Steering and Ethics Councils could claim jurisdiction over disputes. No boundary delineation caused scope ambiguity.

**Fix:** Steering resolves *which* council owns a domain (structural overlap). Ethics resolves *how* a council behaved within its domain (operational disputes). When jurisdiction IS the dispute, Steering resolves scope first, Ethics then adjudicates behavioral concerns.

### C-03: Wise-Elder → Wise-Parent-Elder canonical naming

Archetype defined as 'Wise-Parent-Elder' in the definitions table but referenced as 'Wise-Elder' in 4 other places.

**Fix:** Unified to 'Wise-Parent-Elder' across all occurrences.

## High Fixes (commit `2ea14d3` — 1 item)

### H-02: Epoch undefined

Epoch referenced as the fundamental time unit but never defined.

**Fix:** 30-day default, set by Steering Council, change requires Tier 3, extendable by 7 days.

## High Fixes (commit `f170de5` — 10 items)

### H-01: Strategic pivot threshold
"3/5 councils" → "3 of 4 involved councils (Steering, Ethics, Operations, Technical)"

### H-03: Tier 3 multi-council
"Steering + affected council" → "Steering + all affected councils; if 3+, 2/3 majority"

### H-04: Tier 5 trigger
Added trigger rule: any council declares emergency, Ethics confirms/downgrades within 1h

### H-05: Vote weighting ranges
Defined coefficient domains: role_relevance ∈ {0,0.5,1}, archetype_fit ∈ {0,1}, stake ∈ {0,0.5,1}

### H-06: Abstention formula
General formula: `threshold = ceil(max(1, required_ratio × total_seats − abstentions))`

### H-07: Context-switch protocol
Inlined: 2 shifts/day cap, 4h cooldown, 72h max, 5 trigger conditions

### H-08: Security gaps
Added key rotation, encryption, key recovery, downgrade protection, attestation to §IX

### H-09: Kill switch guardrails
5 guardrails: auto-log, Ethics review, no self-kill, 24h auto-restore, kill-rate tracking

### H-10: Recursive spawning
Clarified: agents may *request* spawns but may not autonomously spawn

## Missing Sections (commit `f170de5` — 5 items)

### MS-01: Failure modes
6 failure modes with detection and recovery (Tier 4 deadlock, split-brain, council capture, quorum failure, protocol drift, key compromise)

### MS-02: Human oversight
5 reserved powers (veto, pardon, dissolve, emergency override, phase gate) with graduated autonomy

### MS-03: Communication protocol
5-layer protocol (signaling, direct messaging, broadcast, proposals, heartbeat) with message format and routing rules

### MS-04: Resource model
5 resource types (compute, tasks, bandwidth, storage, memory) with allocation models and priority tiers

### MS-05: Data governance
6 domains (provenance, retention, access control, anonymization, portability, compliance)

## Files Changed

- `ARCHITECTURE.md` — 725→822 lines, 112 insertions, 15 deletions
- `reviews/architecture-compliance-checklist.md` — updated cross-refs