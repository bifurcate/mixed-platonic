"""Construct a census of search environments from a manifest.

Reads a census manifest JSON file (produced by ``generate_census.py``)
and creates a search environment for each pattern under a shared census
directory.

Usage:
    poetry run python src/construct_census.py my_manifest.json my_census
"""

import argparse
import json
import logging
import shutil
from pathlib import Path

from construct import (
    generate,
    generate_multi,
    generate_config_from_long_cusp_pattern,
)
from finger_cusp import (
    parse_finger_pattern,
    to_finger_pattern_list,
)


def parse_multi_finger_pattern_str(s: str) -> list[list[int]]:
    """Decode a pipe-delimited multi-finger pattern string.

    Args:
        s: A string like ``"|++--|-+|"``.

    Returns:
        List of finger patterns (each a list of 0/1 integers).
    """
    parts = s.strip("|").split("|")
    return [to_finger_pattern_list(p) for p in parts]


def construct_from_manifest(census_root: Path, manifest: dict) -> None:
    """Build solver environments for every pattern in a manifest.

    Args:
        census_root: Path to the census directory (will be created).
        manifest: Dict with ``type`` and ``patterns`` keys.
    """
    pattern_type = manifest["type"]
    patterns = manifest["patterns"]

    try:
        census_root.mkdir()
    except FileExistsError:
        logging.error(f"Census directory '{census_root}' already exists")
        return

    logging.info(
        f"Constructing census '{census_root.name}': "
        f"{len(patterns)} {pattern_type} patterns"
    )

    for pattern_str in patterns:
        if pattern_type == "finger":
            fp = parse_finger_pattern(pattern_str)
            env_path = census_root / pattern_str
            generate(env_path, fp)

        elif pattern_type == "multi_finger":
            mfp = parse_multi_finger_pattern_str(pattern_str)
            env_path = census_root / pattern_str
            generate_multi(env_path, mfp)

        elif pattern_type == "long_cusp":
            env_path = census_root / pattern_str
            generate_config_from_long_cusp_pattern(env_path, pattern_str)

        else:
            logging.error(f"Unknown pattern type: {pattern_type}")
            return

    logging.info("Completed census construction")


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="MP-CONSTRUCT-CENSUS|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Construct search environments from a census manifest"
    )

    parser.add_argument("manifest", type=str, help="Path to the census manifest JSON")
    parser.add_argument("name", type=str, help="Name of the census directory to create")

    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = json.load(f)

    census_root = Path(args.name)
    construct_from_manifest(census_root, manifest)

    # Copy the manifest into the census directory so solve_census can use it.
    shutil.copy2(args.manifest, census_root / "manifest.json")


if __name__ == "__main__":
    main()
