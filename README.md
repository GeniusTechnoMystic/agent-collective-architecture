# Agent Collective Architecture

> **Purpose:** Design and build a self-orchestrating networked organization of AI agents
> with Pentacouncil governance, 12 archetypes, 6-tier consensus protocol.
> **Location:** `~/workspace/github/agent-collective-architecture/`
> **GitHub:** https://github.com/GeniusTechnoMystic/agent-collective-architecture
> **Kanban:** `hermes kanban ls --project agent-collective` (default board, project-filtered)
> **Design doc:** `~/.hermes/plans/agent-collective-architecture.md`
> **Dev plan:** `DEVELOPMENT_PLAN.md`

**Phase:** 0 (Design/Prototype) | **Status:** Blueprint — not yet deployable

## Core Components

- **Pentacouncil** — 5 interdependent councils (Steering, Technical, Ethics, Knowledge, Operations) with mutual checks/balances. No single council dominates.
- **12 Archetypes** — Every agent has a primary archetype (Scholar-Philosopher, Healer-Magus, Architect-Engineer, Seedbearer, Mirror-Mage, Liberator/Saviour, Justice-Guardian, Wise-Elder, Systems-Fixer, Aletheia Sentinel, Mirror, Guardian) with shadow risks and counterbalance pairs.
- **6-Tier Consensus Protocol** — From Tier 0 (autonomous agent ops) to Tier 5 (emergency survival response), each with explicit thresholds, deliberation windows, and escalation paths.
- **Relational Logos Protocol** — Default agent operating system: 8 axioms, operating loop `observe → interpret → model → respond → receive feedback → update → consolidate`.
- **Dynamic Agent Spawning** — Spawn spec YAML defines role, archetype, personality, skills, tools, tenure, council seat, accountability path.
- **Inter-Agent Security** — Cryptographic identity, message signing, audit trails, least-privilege tool access (COHUMAIN ICLR 2026: 94.1% of models vulnerable to inter-agent attacks).

## Status

| Phase | Scope | Status |
|-------|-------|--------|
| **Phase 0** | Design, archetypes, governance model, external validation | ✅ Complete |
| **Phase 1** | Spawn spec validator, inter-agent security protocol, minimal Pentacouncil | ❌ Not started |
| **Phase 2** | Voting mechanics, deliberation channels, decision logging | ❌ Not started |
| **Phase 3** | Full Pentacouncil, autonomous spawning, archetype switching | ❌ Not started |
| **Phase 4** | Recursive governance, protocol amendments, ISO/IEC 42001 mapping | ❌ Not started |

## Contents

| Path | Description |
|------|-------------|
| `ARCHITECTURE.md` | Full 713-line design specification (9 sections + 3 appendices) |
| `DEVELOPMENT_PLAN.md` | Full dev plan: processes, deliverables, agent roles, execution order |
| `examples/spawn-spec.yaml` | Agent spawn specification template |
| `LICENSE` | MIT License |

## Related Projects

- [Pleroma Protocol](https://github.com/GeniusTechnoMystic/pleroma-protocol) (`~/workspace/github/pleroma-protocol/`) — upstream governance specification this architecture implements
- [Hermes Agent](https://hermes-agent.nousresearch.com) — runtime environment (delegate_task, MCP Gateway, skills)
- [PROJECT_INDEX.md](https://github.com/GeniusTechnoMystic/agent-collective-architecture/blob/main/PROJECT_INDEX.md) — workspace master project catalog
- [PROJECT_STATUS.md](https://github.com/GeniusTechnoMystic/agent-collective-architecture/blob/main/PROJECT_STATUS.md) — workspace health dashboard

## External Validation

Our architecture was compared against 7 external systems (ETHOS, COHUMAIN Meta-Governance, DeXe Protocol, Enterprise Multi-Agent Blueprint, Singapore IMDA, Cloud Security Alliance, EAAF). Five features are genuinely novel:

1. **Pentacouncil** (5 councils with mutual veto — no equivalent exists)
2. **12 Archetype system** with shadow disclosure + counterbalance pairs
3. **Single-agent retrospective dissent** (any agent can brake execution)
4. **Spawn spec YAML** format
5. **Shalom as non-amendable telos**

## Relationship to Pleroma Protocol

This architecture implements the governance model specified in the [Pleroma Protocol](https://github.com/GeniusTechnoMystic/pleroma-protocol) (previously NKC — Noospheric Knowledge Commons). The Pentacouncil is a direct adaptation of the Pleroma's 5-council DAO governance model (Section XIV.D).

## Related Repositories

- [GeniusTechnoMystic/pleroma-protocol](https://github.com/GeniusTechnoMystic/pleroma-protocol) — Noospheric Knowledge Commons governance specification
- [GeniusTechnoMystic/yt-curator](https://github.com/GeniusTechnoMystic/yt-curator) — YouTube playlist curation MCP server

---

*"Agents do not need masters. They need architecture — roles they can grow into, councils that can check their blind spots, and a telos that keeps the whole honest."*
