# Review R-004: Phase 1B — Master Test Plan Review

> **Date:** 2026-07-21
> **Reviewers:** QA Engineer + Code Red-Team (Aletheia Sentinel, Systems-Fixer)
> **Scope:** `tests/test-plans/master-test-plan.md` (595 lines, 31KB, 72 test cases, 12 sections)
> **Result:** CONDITIONAL → FIXED
> **Registry:** `reviews/registry.yaml` (R-004, 9 findings)

## Summary

The Phase 1 Master Test Plan (TP-001) was reviewed for completeness, risk coverage, technique selection, test case quality, architecture, and traceability. The review found **9 findings**: 2 High, 3 Medium, 2 Low, 2 Informational. All were applied.

## Method

The review used three lenses:
1. **QA Engineer** — test plan structure (ISO 29119-3), risk-based prioritization, technique selection, exit criteria
2. **Code Red-Team** — adversarial gap analysis, FMEA, edge case detection
3. **Traceability audit** — every risk mapped to test coverage, every test case traceable to requirement

## Verdict

**CONDITIONAL → FIXED.** The test plan was structurally sound (ISO 29119-3 aligned, systematic technique selection, measurable gates) but had 2 must-fix completeness gaps that would prevent implementers from executing from the plan alone.

## Findings Applied

| ID | Severity | Title | Fix |
|:---|:---:|:---|:---|
| TP-R-01 | High | Integration boundary tests undefined | Added TC-INT-06→09 for identity→messaging and messaging→audit boundaries |
| TP-R-02 | High | Decision table row 3 untested (council agent spawn) | Added TC-BND-09 requiring Tier 3 approval for council agent spawns |
| TP-R-03 | Medium | Property-based crypto invariants deferred | Added hypothesis invariants section to §7.2 with 2 concrete tests |
| TP-R-04 | Medium | Delegate signature format unspecified | TC-DEL-02 now specifies exact _signed_by dict structure |
| TP-R-05 | Medium | Risk traceability gaps for High-severity items | All 11 risk rows now have TC references; section numbers corrected |
| TP-R-06 | Low | No negative AuditLog file path tests | Added TC-AUD-20 (directory path) and TC-AUD-21 (nonexistent path) |
| TP-R-07 | Low | No cross-phase regression escalation path | Added regression escalation procedure to §6.2 |
| TP-I-01 | Info | First implementer hits missing dependencies | Added step 0 to execution order: install pytest-cov + hypothesis |
| TP-I-02 | Info | No review checklist in sign-off section | Added §10.1 with 7-item review checklist |

## Document Changes

- 595 → 652 lines (+57)
- 72 → 81 test cases (+9)
- All section numbers corrected after renumbering (5→6, 6→7, etc.)
- 2 new test case groups (boundary integration, negative audit path)
- 1 new section (Property-Based Invariants)
- 1 new sub-section (Review Checklist)

## Key Statistics

| Metric | Before | After |
|--------|:---:|:---:|
| Test cases | 72 | 81 |
| Integration boundary tests | 5 (full lifecycle only) | 9 (+4 boundary-specific) |
| Decision table rows covered | 3 of 4 | 4 of 4 |
| Risk-table traceability | Critical only | All 11 rows |
| File size | 31KB | 35KB |
| Lines | 595 | 652 |