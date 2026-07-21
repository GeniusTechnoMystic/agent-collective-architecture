"""CLI entry point for the Agent Collective Architecture tools."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .validator import validate_spawn_spec


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a spawn spec YAML or JSON file."""
    path = Path(args.path)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    content = path.read_text()
    if path.suffix in (".yaml", ".yml"):
        import yaml
        data = yaml.safe_load(content)
    elif path.suffix == ".json":
        data = json.loads(content)
    else:
        print(f"Error: unsupported file extension: {path.suffix}. Use .yaml, .yml, or .json", file=sys.stderr)
        return 1

    result = validate_spawn_spec(data)

    if result.valid:
        print(f"VALID — {path}")
        return 0
    else:
        print(f"INVALID — {path}")
        for err in result.errors:
            print(f"  ✗ {err}")
        return 1


def cmd_list_archetypes(args: argparse.Namespace) -> int:
    """List all known archetypes."""
    from .validator import ARCHETYPES
    print("Known archetypes:")
    for a in sorted(ARCHETYPES):
        print(f"  • {a}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Agent Collective Architecture CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # validate subcommand
    val = sub.add_parser("validate", help="Validate a spawn spec file")
    val.add_argument("path", help="Path to YAML or JSON spawn spec")
    val.set_defaults(func=cmd_validate)

    # list-archetypes subcommand
    la = sub.add_parser("list-archetypes", help="List known archetypes")
    la.set_defaults(func=cmd_list_archetypes)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
