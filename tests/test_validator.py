"""Tests for the agent collective spawn spec validator."""
import pytest
import copy
import yaml
import json
from pathlib import Path
from agent_collective.validator import (
    ARCHETYPES,
    COUNCILS,
    TENURE_TYPES,
    PERMISSION_PATTERN,
    validate_archetype,
    validate_tenure_type,
    validate_council,
    validate_permission,
    validate_spawn_spec,
    ValidationResult,
)


class TestValidateArchetype:
    def test_known_archetypes_pass(self):
        for a in ARCHETYPES:
            result = validate_archetype(a)
            assert result.valid, f"{a} should be valid"

    def test_unknown_archetype_fails(self):
        result = validate_archetype("Fake-Archetype")
        assert not result.valid
        assert "Fake-Archetype" in result.errors[0]

    def test_empty_string_fails(self):
        result = validate_archetype("")
        assert not result.valid

    def test_case_sensitive(self):
        result = validate_archetype("scholar-philosopher")
        assert not result.valid  # wrong case


class TestValidateTenureType:
    def test_valid_types_pass(self):
        for t in TENURE_TYPES:
            result = validate_tenure_type(t)
            assert result.valid

    def test_invalid_type_fails(self):
        result = validate_tenure_type("permanent")
        assert not result.valid


class TestValidateCouncil:
    def test_valid_councils_pass(self):
        for c in COUNCILS:
            result = validate_council(c)
            assert result.valid

    def test_invalid_council_fails(self):
        result = validate_council("finance-council")
        assert not result.valid


class TestValidatePermission:
    def test_read_permission(self):
        result = validate_permission("read:knowledge-graph")
        assert result.valid

    def test_write_permission(self):
        result = validate_permission("write:council-minutes")
        assert result.valid

    def test_admin_permission(self):
        result = validate_permission("admin:gateway")
        assert result.valid

    def test_invalid_format_fails(self):
        result = validate_permission("read")
        assert not result.valid

    def test_no_prefix_fails(self):
        result = validate_permission("delete:stuff")
        assert not result.valid


class TestValidateSpawnSpec:
    VALID_SPEC = {
        "agent_spawn": {
            "role": "Ontology Auditor",
            "archetype": {"primary": "Scholar-Philosopher", "secondary": "Systems-Fixer"},
            "personality": "noospheric-scholar",
            "skills": ["knowledge-architect", "codebase-inspection"],
            "tenure": {"type": "epoch", "duration": 14, "renewal": "manual"},
            "accountability": {
                "oversight": "knowledge-council",
                "ethics_path": "ethics-council",
            },
        }
    }

    def test_valid_spec_passes(self):
        result = validate_spawn_spec(self.VALID_SPEC)
        assert result.valid
        assert len(result.errors) == 0

    def test_missing_role_fails(self):
        spec = dict(self.VALID_SPEC)
        del spec["agent_spawn"]["role"]
        result = validate_spawn_spec(spec)
        assert not result.valid

    def test_missing_archetype_fails(self):
        spec = dict(self.VALID_SPEC)
        del spec["agent_spawn"]["archetype"]
        result = validate_spawn_spec(spec)
        assert not result.valid

    def test_bad_archetype_fails(self):
        spec = {
            "agent_spawn": {
                "role": "Test",
                "archetype": {"primary": "Fake-Archetype"},
                "personality": "test",
                "skills": ["x"],
                "tenure": {"type": "epoch"},
                "accountability": {"oversight": "knowledge-council", "ethics_path": "ethics-council"},
            }
        }
        result = validate_spawn_spec(spec)
        assert not result.valid

    def test_bad_tenure_type_fails(self):
        spec = dict(self.VALID_SPEC)
        spec["agent_spawn"]["tenure"]["type"] = "forever"
        result = validate_spawn_spec(spec)
        assert not result.valid

    def test_missing_required_field_errors_are_descriptive(self):
        spec = {
            "agent_spawn": {
                "archetype": {"primary": "Scholar-Philosopher"},
                "skills": ["x"],
                "tenure": {"type": "epoch"},
                "accountability": {"oversight": "knowledge-council", "ethics_path": "ethics-council"},
            }
        }
        result = validate_spawn_spec(spec)
        assert len(result.errors) >= 2
        assert any("role" in e.lower() for e in result.errors)
        assert any("personality" in e.lower() for e in result.errors)
