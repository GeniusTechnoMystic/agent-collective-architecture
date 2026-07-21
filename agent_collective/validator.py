"""Spawn spec validator for the Agent Collective Architecture.

Validates agent spawn specifications against the 12 known archetypes,
5 councils, tenure types, permission format, and canonical JSON Schema
defined in ARCHITECTURE.md and schemas/spawn-schema.json.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# --- Constants from ARCHITECTURE.md ---

ARCHETYPES = frozenset({
    "Scholar-Philosopher", "Healer-Magus", "Architect-Engineer",
    "Seedbearer", "Mirror-Mage", "Liberator/Saviour",
    "Justice-Guardian", "Wise-Parent-Elder", "Systems-Fixer",
    "Aletheia Sentinel", "Mirror", "Guardian",
})

COUNCILS = frozenset({
    "steering", "technical", "ethics", "knowledge", "operations",
})

TENURE_TYPES = frozenset({"task", "epoch", "indefinite"})
RENEWAL_TYPES = frozenset({"automatic", "manual", "none"})
PRIORITY_TYPES = frozenset({"low", "medium", "high", "critical"})
RETIREMENT_CONDITIONS = frozenset({"epoch-expiry", "task-complete", "manual", "indefinite"})
REVIEW_TYPES = frozenset({"check-in", "performance", "security-audit"})

PERMISSION_PATTERN = re.compile(r"^(read|write|admin):[a-z][a-z0-9_-]*$")

# Derived from COUNCILS to avoid maintenance drift (CQ-08 fix)
OVERSIGHT_COUNCILS = frozenset(f"{c}-council" for c in COUNCILS)

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "spawn-schema.json"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool = True
    errors: list[str] = field(default_factory=list)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Combine two validation results."""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
        )


def _get_dict(data: Any, key: str) -> dict | None:
    """Safely get a nested dict, returning None if not a dict."""
    if isinstance(data, dict) and key in data:
        val = data[key]
        return val if isinstance(val, dict) else None
    return None


def _get_list(data: Any, key: str) -> list | None:
    """Safely get a nested list, returning None if not a list."""
    if isinstance(data, dict) and key in data:
        val = data[key]
        return val if isinstance(val, list) else None
    return None


def _get_str(data: Any, key: str) -> str | None:
    """Safely get a nested string, returning None if not a string."""
    if isinstance(data, dict) and key in data:
        val = data[key]
        return val if isinstance(val, str) else None
    return None


# ---------------------------------------------------------------------------
# Individual validators
# ---------------------------------------------------------------------------

def validate_archetype(name: str) -> ValidationResult:
    """Check that the archetype name is one of the 12 known archetypes."""
    if not name:
        return ValidationResult(valid=False, errors=["Archetype name cannot be empty"])
    if name not in ARCHETYPES:
        valid_list = ", ".join(sorted(ARCHETYPES))
        return ValidationResult(
            valid=False,
            errors=[f"Unknown archetype '{name}'. Valid: {valid_list}"],
        )
    return ValidationResult()


def validate_tenure_type(t: str) -> ValidationResult:
    """Check that the tenure type is valid."""
    if t not in TENURE_TYPES:
        valid = ", ".join(sorted(TENURE_TYPES))
        return ValidationResult(
            valid=False,
            errors=[f"Invalid tenure type '{t}'. Valid: {valid}"],
        )
    return ValidationResult()


def validate_council(name: str) -> ValidationResult:
    """Check that the council name is one of the 5 councils."""
    if name not in COUNCILS:
        valid = ", ".join(sorted(COUNCILS))
        return ValidationResult(
            valid=False,
            errors=[f"Invalid council '{name}'. Valid: {valid}"],
        )
    return ValidationResult()


def validate_permission(perm: str) -> ValidationResult:
    """Check that the permission string matches read/write/admin:scope format."""
    if not PERMISSION_PATTERN.match(perm):
        return ValidationResult(
            valid=False,
            errors=[f"Invalid permission '{perm}'. Must match read|write|admin:<scope>"],
        )
    return ValidationResult()


def _check_required(data: dict, path: str, fields: list[str]) -> ValidationResult:
    """Check that required fields exist in a nested dict."""
    errors: list[str] = []
    for field_name in fields:
        keys = field_name.split(".")
        obj: Any = data
        found = True
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                errors.append(f"Missing required field: {path}.{field_name}")
                found = False
                break
        # If the final value is None (JSON null), also flag it
        if found and obj is None:
            errors.append(f"Missing required field: {path}.{field_name} (null)")
    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_spawn_spec(spec: Any) -> ValidationResult:
    """Validate a complete agent spawn specification.

    First validates against the canonical JSON Schema (if jsonschema is
    available), then runs Python-level checks for invariants the schema
    cannot express (archetype validity, council name cross-references).

    Parameters
    ----------
    spec: Parsed YAML/JSON data (expected to be a dict with an
        ``agent_spawn`` key).

    Returns
    -------
    ValidationResult with valid=True/False and descriptive errors.
    """
    # --- Guard: reject non-dict input (SEC-01 fix) ---
    if not isinstance(spec, dict):
        return ValidationResult(
            valid=False,
            errors=[f"Input must be a JSON/YAML object (dict), got {type(spec).__name__}"],
        )

    result = ValidationResult()

    # --- JSON Schema validation (CQ-01 fix) ---
    schema_errors = _validate_against_schema(spec)
    if schema_errors is not None:
        # jsonschema is available — merge errors
        for err in schema_errors:
            result = result.merge(ValidationResult(valid=False, errors=[err]))
    # If jsonschema is not installed, we fall through to Python-level checks

    # Check top-level structure
    if "agent_spawn" not in spec:
        return result.merge(
            ValidationResult(valid=False, errors=["Missing top-level 'agent_spawn' key"])
        )

    spawn = spec["agent_spawn"]

    # Check required fields
    required = ["role", "archetype", "personality", "skills", "tenure", "accountability"]
    result = result.merge(_check_required(spawn, "agent_spawn", required))

    if not result.valid:
        return result

    # --- Validate archetype (SEC-02 fix: guard with isinstance) ---
    archetype = _get_dict(spawn, "archetype")
    if archetype is not None:
        primary = _get_str(archetype, "primary")
        if primary is not None:
            result = result.merge(validate_archetype(primary))
        secondary = _get_str(archetype, "secondary")
        if secondary:
            result = result.merge(validate_archetype(secondary))
    else:
        # archetype key exists but isn't a dict
        result = result.merge(ValidationResult(
            valid=False,
            errors=["'archetype' must be a dict with 'primary' key"],
        ))

    # --- Validate skills is a non-empty list (CQ-06 fix) ---
    skills = _get_list(spawn, "skills")
    if skills is not None and len(skills) == 0:
        result = result.merge(ValidationResult(
            valid=False,
            errors=["'skills' must be a non-empty array"],
        ))

    # --- Validate tenure (SEC-02 fix: guard with isinstance) ---
    tenure = _get_dict(spawn, "tenure")
    if tenure is not None:
        ttype = _get_str(tenure, "type")
        if ttype is not None:
            result = result.merge(validate_tenure_type(ttype))
        renewal = _get_str(tenure, "renewal")
        if renewal is not None and renewal not in RENEWAL_TYPES:
            result = result.merge(ValidationResult(
                valid=False,
                errors=[f"Invalid renewal '{renewal}'. Must be automatic, manual, or none"],
            ))

    # --- Validate council seat (CQ-05 fix: guard with isinstance before iterating) ---
    council_seat = _get_dict(spawn, "council_seat")
    if council_seat is not None:
        eligible = _get_list(council_seat, "eligible")
        if eligible is not None:
            for c in eligible:
                if isinstance(c, str):
                    result = result.merge(validate_council(c))
        assigned = _get_str(council_seat, "assigned")
        if assigned:
            result = result.merge(validate_council(assigned))

    # --- Validate permissions ---
    tools = _get_dict(spawn, "tools")
    if tools is not None:
        permissions = _get_list(tools, "permissions")
        if permissions is not None:
            for p in permissions:
                if isinstance(p, str):
                    result = result.merge(validate_permission(p))

    # --- Validate accountability (CQ-07 fix: add ethics_path check) ---
    accountability = _get_dict(spawn, "accountability")
    if accountability is not None:
        oversight = _get_str(accountability, "oversight")
        if oversight is not None and oversight not in OVERSIGHT_COUNCILS:
            result = result.merge(ValidationResult(
                valid=False,
                errors=[
                    f"Invalid oversight '{oversight}'. "
                    f"Must be one of: {', '.join(sorted(OVERSIGHT_COUNCILS))}"
                ],
            ))
        ethics_path = _get_str(accountability, "ethics_path")
        if ethics_path is not None and ethics_path != "ethics-council":
            result = result.merge(ValidationResult(
                valid=False,
                errors=[f"ethics_path must be 'ethics-council', got '{ethics_path}'"],
            ))
        review_schedule = _get_list(accountability, "review_schedule")
        if review_schedule is not None:
            for i, item in enumerate(review_schedule):
                if isinstance(item, dict):
                    rt = _get_str(item, "type")
                    if rt is not None and rt not in REVIEW_TYPES:
                        result = result.merge(ValidationResult(
                            valid=False,
                            errors=[
                                f"review_schedule[{i}].type '{rt}' invalid. "
                                f"Must be one of: {', '.join(sorted(REVIEW_TYPES))}"
                            ],
                        ))

    # --- Validate resources ---
    resources = _get_dict(spawn, "resources")
    if resources is not None:
        priority = _get_str(resources, "priority")
        if priority is not None and priority not in PRIORITY_TYPES:
            result = result.merge(ValidationResult(
                valid=False,
                errors=[
                    f"Invalid priority '{priority}'. "
                    f"Must be one of: {', '.join(sorted(PRIORITY_TYPES))}"
                ],
            ))

    # --- Validate retirement ---
    retirement = _get_dict(spawn, "retirement")
    if retirement is not None:
        condition = _get_str(retirement, "condition")
        if condition is not None and condition not in RETIREMENT_CONDITIONS:
            result = result.merge(ValidationResult(
                valid=False,
                errors=[
                    f"Invalid retirement condition '{condition}'. "
                    f"Must be one of: {', '.join(sorted(RETIREMENT_CONDITIONS))}"
                ],
            ))

    return result


def _validate_against_schema(spec: dict) -> list[str] | None:
    """Validate spec against the canonical JSON Schema.

    Returns a list of error messages, or None if jsonschema is not installed
    (graceful degradation — Python-level checks still run).
    """
    try:
        import json

        import jsonschema
    except ImportError:
        return None  # jsonschema not installed — fall through gracefully

    if not _SCHEMA_PATH.exists():
        return ["spawn-schema.json not found — skipping schema validation"]

    try:
        schema = json.loads(_SCHEMA_PATH.read_text())
        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(spec))
        if not errors:
            return []
        return [f"Schema violation: {e.message}" for e in errors]
    except json.JSONDecodeError as e:
        return [f"Invalid spawn-schema.json: {e}"]
    except jsonschema.SchemaError as e:
        return [f"spawn-schema.json is not valid Draft7: {e}"]
