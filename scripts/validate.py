#!/usr/bin/env python3
"""Validate every company file in data/companies/ against data/schema.json.

Usage: python scripts/validate.py
Exits non-zero if any file fails validation. Skips _template.json.
"""
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator as SchemaValidator
except ImportError:
    try:
        from jsonschema import Draft7Validator as SchemaValidator  # older jsonschema fallback
    except ImportError:
        sys.exit("jsonschema not installed. Run: pip install jsonschema")

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "data" / "schema.json").read_text())
COMPANIES = ROOT / "data" / "companies"


def main() -> int:
    validator = SchemaValidator(SCHEMA)
    files = sorted(p for p in COMPANIES.glob("*.json") if not p.name.startswith("_"))
    if not files:
        print("No company files found.")
        return 1

    failures = 0
    slugs = {}
    for path in files:
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"FAIL {path.name}: invalid JSON — {e}")
            failures += 1
            continue

        errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        if errors:
            failures += 1
            print(f"FAIL {path.name}:")
            for err in errors:
                loc = "/".join(str(p) for p in err.path) or "(root)"
                print(f"  - {loc}: {err.message}")
        else:
            # extra checks beyond schema
            slug = record.get("slug", "")
            if slug != path.stem:
                failures += 1
                print(f"FAIL {path.name}: slug '{slug}' != filename '{path.stem}'")
                continue
            if slug in slugs:
                failures += 1
                print(f"FAIL {path.name}: duplicate slug with {slugs[slug]}")
                continue
            slugs[slug] = path.name
            snaps = record["snapshots"]
            dates = [s["as_of"] for s in snaps]
            if dates != sorted(dates):
                failures += 1
                print(f"FAIL {path.name}: snapshots not in chronological order")
                continue
            print(f"ok   {path.name} ({len(snaps)} snapshot{'s' if len(snaps) != 1 else ''})")

    print(f"\n{len(files) - failures}/{len(files)} files valid.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
