# Agent Collective — Review & QA Tracking

> **Purpose:** Persistent, auditable record of all reviews, findings, fixes, and verification results across the project lifecycle.
> **Convention:** Every review produces a findings file + updates the registry. No finding is closed without a fix commit + verification.
> **Schema:** `registry.yaml` is the canonical index. Per-review findings files contain the full narrative.

## Structure

```
reviews/
├── README.md                         # This file — conventions and index
├── registry.yaml                     # Structured finding registry (all findings, statuses, cross-refs)
├── architecture-compliance-checklist.md  # Static checklist for reviewers (v1.1)
└── phase-1a/                         # Phase 1A review artifacts
    ├── findings-001-security-quality.md   # Review 1: Security/Quality (13 issues)
    ├── findings-002-meta-review.md        # Review 2: Dev plan meta-review (13 issues)
    └── findings-003-design-review.md      # Review 3: Architecture design review (19 issues)
└── phase-1b/                         # Phase 1B review artifacts (TBD)
```

## Finding Lifecycle

```
OPEN → IN_FIX → FIXED(commit) → VERIFIED(date) → CLOSED
                                                    ↓
                                              REOPENED(regression)
```

| Status | Meaning |
|--------|---------|
| `open` | Identified, not yet assigned or fixed |
| `in_fix` | Fix in progress (fix_commit may be partial) |
| `fixed` | Fix committed. Waiting verification. |
| `verified` | Fix confirmed by re-review or test pass |
| `closed` | Finding retired (no longer applicable, superseded) |
| `reopened` | Previously fixed finding regressed |

## Severity Levels

| Severity | Meaning | Response |
|----------|---------|----------|
| `critical` | Crash, data loss, security bypass, Shalom violation | Blocking — must fix before next commit |
| `high` | Functional defect, design gap, missing test coverage | Must fix before phase gate |
| `medium` | Code quality, documentation gap, minor design ambiguity | Should fix before next phase |
| `low` | Style, naming, suggestion, nice-to-have | May defer |

## Review Results

| Result | Meaning |
|--------|---------|
| `PASS` | All checks pass. No findings. |
| `PASS_WITH_NOTES` | All checks pass. Non-blocking findings (medium/low) recorded. |
| `CONDITIONAL` | Critical/high findings exist but can be fixed post-merge with a plan. |
| `FAIL` | Critical/high findings block the commit. Must fix before merge. |
| `FAIL → FIXED` | Failed review, fixes applied and verified. |

## Registry Format

The `registry.yaml` file is the canonical source of truth. All tooling reads from it. Per-review findings files are the narrative companion for human review.

## Integration with requesting-code-review

The skill (v3.1+) appends findings to `registry.yaml` after each review cycle. See `~/.hermes/skills/software-development/requesting-code-review/SKILL.md` for the pipeline.