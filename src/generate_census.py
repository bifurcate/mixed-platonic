"""Generate a census manifest of cusp patterns.

Enumerates all distinct cusp patterns of a given size (using bracelet
enumeration to avoid duplicates under rotation and reflection) and writes
a JSON manifest listing the pattern type and all patterns.  The manifest
is consumed by ``construct_census.py`` to build solver environments.

Supports three pattern types:
    - Finger patterns: ``-n <num_fingers>`` enumerates 2-bracelets of
      the given length.
    - Multi-component finger patterns: ``-m <num_fingers>`` enumerates
      multi-component 2-bracelets with the given number of fingers per
      component.
    - Long cusp patterns: ``-l <max_length>`` enumerates long cusp
      sequences up to the given length.

Usage:
    poetry run python src/generate_census.py -n 12 my_manifest.json
    poetry run python src/generate_census.py -m 6 my_manifest.json
    poetry run python src/generate_census.py -l 16 my_manifest.json
"""

import argparse
import json
import logging

from bracelets import (
    generate_2_bracelets,
    generate_multi_2_bracelets,
)
from finger_cusp import (
    to_finger_pattern_str,
    to_multi_finger_pattern_str,
)
from long_cusp import build_cusp_sequences


def generate_finger_manifest(num_fingers: int) -> dict:
    """Enumerate finger patterns and build a manifest dict.

    Args:
        num_fingers: Length of finger patterns to enumerate.

    Returns:
        Manifest dict with ``type`` and ``patterns`` keys.
    """
    patterns = [to_finger_pattern_str(fp) for fp in generate_2_bracelets(num_fingers)]
    return {"type": "finger", "patterns": patterns}


def generate_multi_finger_manifest(num_fingers: int) -> dict:
    """Enumerate multi-component finger patterns and build a manifest dict.

    Args:
        num_fingers: Number of fingers per component to enumerate.

    Returns:
        Manifest dict with ``type`` and ``patterns`` keys.
    """
    patterns = [
        to_multi_finger_pattern_str(mfp)
        for mfp in generate_multi_2_bracelets(num_fingers)
    ]
    return {"type": "multi_finger", "patterns": patterns}


def generate_long_cusp_manifest(max_length: int) -> dict:
    """Enumerate long cusp sequences and build a manifest dict.

    Args:
        max_length: Maximum sequence length to enumerate.

    Returns:
        Manifest dict with ``type`` and ``patterns`` keys.
    """
    patterns = list(build_cusp_sequences(max_length))
    return {"type": "long_cusp", "patterns": patterns}


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="MP-GENERATE-CENSUS|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Enumerate cusp patterns and write a census manifest"
    )

    parser.add_argument(
        "-n", "--num-fingers", type=int, help="Length of finger patterns to enumerate"
    )

    parser.add_argument(
        "-m",
        "--multi-fingers",
        type=int,
        help="Number of fingers per component for multi-component patterns",
    )

    parser.add_argument(
        "-l", "--long-cusp", type=int, help="Maximum length of long cusp pattern"
    )

    parser.add_argument("output", type=str, help="Path to write the manifest JSON file")

    args = parser.parse_args()

    if args.num_fingers:
        manifest = generate_finger_manifest(args.num_fingers)
    elif args.multi_fingers:
        manifest = generate_multi_finger_manifest(args.multi_fingers)
    elif args.long_cusp:
        manifest = generate_long_cusp_manifest(args.long_cusp)
    else:
        parser.error("One of -n, -m, or -l is required")

    with open(args.output, "w") as f:
        json.dump(manifest, f, indent=2)

    logging.info(
        f"Wrote manifest: {len(manifest['patterns'])} {manifest['type']} patterns -> {args.output}"
    )


if __name__ == "__main__":
    main()
