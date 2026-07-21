"""Spawn spec validator for the Agent Collective Architecture.

Validates agent spawn specifications against the 12 known archetypes,
5 councils, tenure types, and permission format defined in ARCHITECTURE.md.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# --- Constants from ARCHITECTURE.md ---

ARCHETYPES = frozenset({
    "Scholar-Philosopher",
    "Healer-Magus",
    "Architect-Engineer",
    "Seedbearer",
    "Mirror-Mage",
    "Liberator/Saviour",
    "Justice-Guardian",
    "Wise-Parent-Elder",
    "Systems-Fixer",
    "Aletheia Sentinel",
    "Mirror",
    "Guardian",
})

COUNCILS = frozenset({
    "steering",
    "technical",
    "ethics",
    "knowledge",
    "operations",
})

TENURE_TYPES = frozenset({"task", "epoch", "indefinite"})

PERMISSION_PATTERN = re.compile(r"^(read|write|admin):[a-z][a-z0-9_-]*$")

OVERSIGHT_COUNCILS = frozenset({
    "steering-council",
    "technical-council",
    "ethics-council",
    "knowledge-council",
    "operations-council",
})


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
    errors = []
    for field_name in fields:
        keys = field_name.split(".")
        obj = data
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                errors.append(f"Missing required field: {path}.{field_name}")
                break
    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_spawn_spec(spec: dict[str, Any]) -> ValidationResult:
    """Validate a complete agent spawn specification.

    Checks:
    - Required top-level fields exist
    - Archetype is one of the 12 known
    - Tenure type is valid
    - Council names are valid
    - Permission format is correct
    """
    result = ValidationResult()

    # Check top-level structure
    if "agent_spawn" not in spec:
        return ValidationResult(valid=False, errors=["Missing top-level 'agent_spawn' key"])

    spawn = spec["agent_spawn"]

    # Check required fields
    required = ["role", "archetype", "personality", "skills", "tenure", "accountability"]
    result = result.merge(_check_required(spawn, "agent_spawn", required))

    if not result.valid:
        return result

    # Validate archetype
    if "primary" in spawn.get("archetype", {}):
        result = result.merge(validate_archetype(spawn["archetype"]["primary"]))
    if "secondary" in spawn.get("archetype", {}) and spawn["archetype"]["secondary"]:
        result = result.merge(validate_archetype(spawn["archetype"]["secondary"]))

    # Validate tenure type
    if "type" in spawn.get("tenure", {}):
        result = result.merge(validate_tenure_type(spawn["tenure"]["type"]))

    # Validate council seat
    if "council_seat" in spawn:
        seat = spawn["council_seat"]
        if "eligible" in seat:
            for c in seat["eligible"]:
                result = result.merge(validate_council(c))
        if "assigned" in seat and seat["assigned"]:
            result = result.merge(validate_council(seat["assigned"]))

    # Validate permissions
    if "tools" in spawn and "permissions" in spawn["tools"]:
        for p in spawn["tools"]["permissions"]:
            result = result.merge(validate_permission(p))

    # Validate accountability
    if "accountability" in spawn:
        acc = spawn["accountability"]
        if "oversight" in acc and acc["oversight"] not in OVERSIGHT_COUNCILS:
            result = result.merge(ValidationResult(
                valid=False,
                errors=[f"Invalid oversight '{acc['oversight']}'. Must be one of: {', '.join(sorted(OVERSIGHT_COUNCILS))}"],
            ))

    # Validate renewal
    if "tenure" in spawn and "renewal" in spawn["tenure"]:
        renewal = spawn["tenure"]["renewal"]
        if renewal not in ("automatic", "manual", "none"):
            result = result.merge(ValidationResult(
                valid=False,
                errors=[f"Invalid renewal '{renewal}'. Must be automatic, manual, or none"],
            ))

    return result
