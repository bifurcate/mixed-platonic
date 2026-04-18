"""Construct search environments from cusp patterns.

Creates a search environment directory for a single cusp tiling. The cusp
pattern can be specified as a finger pattern (string of '+' and '-') or a
long cusp pattern string. The environment is written to disk and left in
the "init" state, ready for the solver.

Usage:
    poetry run python src/construct.py -f '++--++--++--' my_env
    poetry run python src/construct.py -l 'ebdcebdccc' my_env
"""

import argparse
import logging
from pathlib import Path

from construction import Cusp
from finger_cusp import (
    FingerCuspConstructor,
    FingerPattern,
    MultiFingerCuspConstructor,
    parse_finger_pattern,
    to_finger_pattern_str,
    to_multi_finger_pattern_str,
)
from long_cusp import LongCuspConstructor
from env import (
    create_env_dir,
    write_config,
    write_state,
)


def parse_finger_pattern_arg(input_fp: str) -> FingerPattern:
    """Parse a CLI finger pattern string into a list of 0/1 values.

    Accepts either ``{+,-}`` or ``{0,1}`` format strings.

    Args:
        input_fp: String of ``'+'``/``'-'`` or ``'0'``/``'1'`` characters.
            Length must be divisible by 6 (each group of 6 encodes one
            octahedron).

    Returns:
        List of 0/1 integers.

    Raises:
        ValueError: If the string contains invalid characters or has
            a length not divisible by 6.
    """
    finger_pattern = parse_finger_pattern(input_fp)

    if len(finger_pattern) % 6 != 0:
        raise ValueError("Input finger pattern length must be divisible by 6")

    return finger_pattern


def determine_num_tets_octs(finger_pattern):
    """Compute the number of tetrahedra and octahedra from a finger pattern.

    Each group of 6 entries in the pattern corresponds to one octahedron
    and three tetrahedra.

    Args:
        finger_pattern: List of 0/1 values.

    Returns:
        Tuple of (num_tets, num_octs).
    """
    num_octs = len(finger_pattern) // 6
    num_tets = 3 * num_octs
    return num_tets, num_octs


def generate_config_from_finger_pattern(env_path, finger_pattern):
    """Build cusp tiling from a finger pattern and write config.json.

    The environment directory must already exist. This writes only the
    config; the caller is responsible for setting the state.

    Args:
        env_path: Path to the environment directory.
        finger_pattern: List of 0/1 values encoding the finger pattern.
    """
    cusp = Cusp()
    cusp_constructor = FingerCuspConstructor(cusp, finger_pattern)
    cusp = cusp_constructor.generate()
    traversal = list(cusp_constructor.traversal())
    num_tets, num_octs = determine_num_tets_octs(finger_pattern)

    write_config(
        env_path,
        num_tets,
        num_octs,
        cusp,
        traversal,
        pattern=to_finger_pattern_str(finger_pattern),
        pattern_type="finger",
    )


def generate_config_from_long_cusp_pattern(env_path, long_cusp_pattern):
    """Create a search environment from a long cusp pattern string.

    Creates the environment directory, builds the cusp tiling, validates
    that the polygon counts are compatible with whole cell counts, and
    writes config and state.

    Args:
        env_path: Path to the environment directory to create.
        long_cusp_pattern: Long cusp pattern string (e.g. "a", "ab").
    """
    create_env_dir(env_path)

    cusp = Cusp()
    cusp_constructor = LongCuspConstructor(cusp, long_cusp_pattern)
    cusp = cusp_constructor.generate()
    traversal = list(cusp_constructor.traversal())
    num_tris, num_sqrs = cusp_constructor.get_num_polys()
    if num_tris % 4 != 0:
        logging.error("num tris must be a multiple of 4")
        exit(1)

    if num_sqrs % 6 != 0:
        logging.error("num sqrs must be a multiple of 6")
        exit(1)

    num_tets = num_tris // 4
    num_octs = num_sqrs // 6

    write_config(
        env_path,
        num_tets,
        num_octs,
        cusp,
        traversal,
        pattern=long_cusp_pattern,
        pattern_type="long_cusp",
    )
    write_state(env_path, "init")
    logging.info(f"Generated search environment: {env_path.name}")


def generate(env_path: Path, finger_pattern: FingerPattern):
    """Create a search environment from a single finger pattern.

    Args:
        env_path: Path to the environment directory to create.
        finger_pattern: List of 0/1 values encoding the finger pattern.
    """
    create_env_dir(env_path)

    logging.info(f"Finger Pattern: {finger_pattern}")
    generate_config_from_finger_pattern(env_path, finger_pattern)
    write_state(env_path, "init")
    logging.info(f"Generated search environment: {env_path.name}")


def generate_multi(env_path: Path, multi_finger_pattern):
    """Create a search environment from a multi-component finger pattern.

    Args:
        env_path: Path to the environment directory to create.
        multi_finger_pattern: List of finger patterns, one per cusp
            component.
    """
    create_env_dir(env_path)

    logging.info(f"Finger Pattern: {multi_finger_pattern}")
    generate_config_from_multi_finger_pattern(env_path, multi_finger_pattern)
    write_state(env_path, "init")
    logging.info(f"Generated search environment: {env_path.name}")


def generate_config_from_multi_finger_pattern(env_path, multi_finger_pattern):
    """Build cusp tiling from a multi-component finger pattern and write config.

    The environment directory must already exist. This writes only the
    config; the caller is responsible for setting the state.

    Args:
        env_path: Path to the environment directory.
        multi_finger_pattern: List of finger patterns, one per component.
    """
    cusp = Cusp()
    cusp_constructor = MultiFingerCuspConstructor(cusp, multi_finger_pattern)
    cusp_constructor.generate()
    traversal = list(cusp_constructor.traversal())
    num_tets, num_octs = determine_num_tets_octs(cusp_constructor.flattened)
    write_config(
        env_path,
        num_tets,
        num_octs,
        cusp,
        traversal,
        pattern=to_multi_finger_pattern_str(multi_finger_pattern),
        pattern_type="multi_finger",
    )


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="MP-GENERATE|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="CLI frontend for generating Mixed Platonic search environments"
    )

    parser.add_argument(
        "-f",
        "--finger-pattern",
        type=str,
        help="Finger pattern string ('+'/'-' or '0'/'1' characters)",
    )

    parser.add_argument(
        "-l",
        "--long-cusp-pattern",
        type=str,
        help="long cusp pattern string",
    )

    parser.add_argument("name", type=str, help="Name of the search environment")

    args = parser.parse_args()
    name = args.name
    env_path = Path(name)

    if args.finger_pattern:
        finger_pattern = parse_finger_pattern_arg(args.finger_pattern)
        generate(env_path, finger_pattern)
    elif args.long_cusp_pattern:
        generate_config_from_long_cusp_pattern(env_path, args.long_cusp_pattern)


if __name__ == "__main__":
    main()
