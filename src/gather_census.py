"""Gather census data into a combined data.json.

Walks every environment directory in a census root, collects all JSON
and JSONL data files (skipping .txt files), and writes a single
``data.json`` at the census root.  The output is a dict keyed by
environment name, where each value holds the parsed contents of that
environment's JSON files (with JSONL files converted to arrays).

Missing or malformed files are skipped with a warning so that partial
census runs can still be gathered.

Usage:
    poetry run python src/gather_census.py data/short_cusp_12
"""

import argparse
import json
import logging
import os
from pathlib import Path


def gather_env(env_path: Path) -> dict:
    """Collect all JSON/JSONL data from a single environment directory.

    Args:
        env_path: Path to the environment directory.

    Returns:
        Dict mapping filename stems to parsed data.  JSON files map to
        their parsed object; JSONL files map to a list of parsed lines.
    """
    data = {}
    for entry in sorted(os.scandir(env_path), key=lambda e: e.name):
        if not entry.is_file():
            continue
        name = entry.name
        path = Path(entry.path)

        if name.endswith(".json"):
            try:
                with open(path, "r") as f:
                    data[path.stem] = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logging.warning(f"Skipping {path}: {e}")

        elif name.endswith(".jsonl"):
            lines = []
            try:
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            lines.append(json.loads(line))
            except (json.JSONDecodeError, OSError) as e:
                logging.warning(f"Skipping {path}: {e}")
            if lines:
                data[path.stem] = lines

    return data


def gather_census(census_path: Path) -> dict:
    """Gather data from all environments in a census directory.

    Args:
        census_path: Path to the census root directory.

    Returns:
        Dict mapping environment names to their gathered data dicts.
    """
    result = {}
    env_dirs = sorted(
        (census_path / entry.name for entry in os.scandir(census_path) if entry.is_dir()),
        key=lambda p: p.name,
    )
    for env_path in env_dirs:
        env_data = gather_env(env_path)
        if env_data:
            result[env_path.name] = env_data
    return result


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="MP-GATHER|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Gather census environment data into a combined data.json"
    )
    parser.add_argument(
        "census_dir",
        type=str,
        help="Path to the census root directory",
    )

    args = parser.parse_args()
    census_path = Path(args.census_dir)

    if not census_path.is_dir():
        logging.error(f"Census directory not found: {census_path}")
        exit(1)

    data = gather_census(census_path)
    output_path = census_path / "data.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    logging.info(f"Gathered {len(data)} environments -> {output_path}")


if __name__ == "__main__":
    main()
