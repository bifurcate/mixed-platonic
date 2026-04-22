"""Backfill pattern and pattern_type fields in an existing data.json.

For each environment entry whose pattern/pattern_type are missing, sets
pattern from the environment name (key) and pattern_type from the CLI argument.

Usage:
    poetry run python src/backfill_census.py data/short_cusp_12/data.json finger
"""

import argparse
import json
from pathlib import Path


def backfill(data: dict, pattern_type: str) -> int:
    """Add missing pattern and pattern_type fields to each environment entry.

    Args:
        data: Combined census data mapping env names to env data dicts.
        pattern_type: Value to write into each entry's ``pattern_type`` field.

    Returns:
        Number of entries that were updated.
    """
    updated = 0
    for env_name, env_data in data.items():
        config = env_data.setdefault("config", {})
        changed = False
        if "pattern" not in config:
            config["pattern"] = env_name
            changed = True
        if "pattern_type" not in config:
            config["pattern_type"] = pattern_type
            changed = True
        if changed:
            updated += 1
    return updated


def main():
    parser = argparse.ArgumentParser(
        description="Backfill pattern and pattern_type fields in a census data.json"
    )
    parser.add_argument("data_json", type=str, help="Path to the data.json file")
    parser.add_argument("pattern_type", type=str, help="Pattern type to set (e.g. finger, long_cusp)")
    args = parser.parse_args()

    path = Path(args.data_json)
    with open(path, "r") as f:
        data = json.load(f)

    updated = backfill(data, args.pattern_type)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Updated {updated}/{len(data)} entries in {path}")


if __name__ == "__main__":
    main()
