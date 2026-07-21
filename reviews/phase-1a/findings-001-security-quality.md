# Review R-001: Phase 1A — Security & Quality Review

> **Date:** 2026-07-20
> **Reviewers:** Aletheia Sentinel (Security) + Systems-Fixer (Code Quality)
> **Scope:** `agent_collective/validator.py`, `agent_collective/cli.py`, `tests/test_validator.py`
> **Result:** FAIL → FIXED (commit `25b9ca2`)
> **Registry:** `reviews/registry.yaml` (findings SEC-01, SEC-02, CQ-01 through CQ-09, TST-01)

## Summary

The Phase 1A spawn spec validator was reviewed by two specialist subagents. The review found **2 critical security issues** (crash paths on unexpected input) and **9 code quality issues** (missing validation, config drift, insufficient error handling). All 11 issues were fixed, plus 13 new tests added (32 total).

## Key Findings

### Critical — SEC-01, SEC-02: Crash paths on malicious/malformed input

The validator had no input sanitization at the entry point. Non-dict input (e.g., from a malformed YAML parse) caused unhandled `TypeError` crashes. Type-mismatched nested fields (archetype as string instead of dict) caused `AttributeError` on nested `.get()` calls.

**Fix:** Added `_get_dict`, `_get_list`, `_get_str` safe accessor methods that guard all nested dict traversal. Entry point returns `ValidationResult(success=False, errors=[...])` instead of crashing.

### High — CQ-01, CQ-02: Missing JSON Schema integration + wrong dependency config

The validator had its own validation logic but didn't run `jsonschema.validate()` against the JSON Schema file, creating two diverging validation paths. Dependencies were in `optional-dependencies` instead of `dependencies`.

### High — CQ-03, CQ-04: Unhandled parse errors + unsafe intermediate traversal

YAML/JSON parse errors (malformed input) crashed the validator. `_check_required` didn't handle non-dict intermediate values in nested paths.

### Medium — CQ-05 through CQ-08: Missing field-level guards

Four fields lacked proper type/validation guards: `council_seat.eligible` (not guarded as list), `skills` (empty list accepted), `ethics_path` (no enum check), `OVERSIGHT_COUNCILS` (hardcoded, drifting from `COUNCILS`).

### Low — CQ-09: Missing machine output format

CLI only printed human-readable output. Added `--json` flag for machine-parseable results.

## Tests Added

13 new tests (19→32 total):
- Crash-path: `test_non_dict_input_fails_gracefully`, `test_archetype_as_string_fails_gracefully`, `test_tenure_as_string_fails_gracefully`
- Validation: `test_oversight_council_valid`, `test_oversight_council_invalid_fails`, `test_renewal_invalid_fails`, `test_ethics_path_invalid_fails`, `test_skills_empty_fails`, `test_council_eligible_as_string_does_not_crash`, `test_resources_priority_valid`, `test_resources_priority_invalid_fails`, `test_retirement_condition_valid`, `test_retirement_condition_invalid_fails`

## Verification

All 32 tests pass. CLI produces correct output for both valid and invalid specs.

## Files Changed

- `agent_collective/validator.py` — rewritten with safe accessors + JSON Schema integration
- `agent_collective/cli.py` — added `--json` flag, parse error handling
- `schemas/spawn-schema.json` — created
- `tests/test_validator.py` — 19→32 tests
- `pyproject.toml` — dependencies fixed