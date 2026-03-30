import argparse
import logging
from pathlib import Path

from construction import Cusp
from finger_cusp import (
    FingerCuspGenerator,
    FingerPattern,
    MultiFingerCuspGenerator,
)
from long_cusp import LongCuspGenerator
from env import (
    create_env_dir,
    write_config,
    write_state,
)


def parse_finger_pattern_arg(input_fp: str):
    if not all(c in "+-" for c in input_fp):
        raise ValueError("Input finger pattern must consist of '+' and '-' characters")

    if len(input_fp) % 6 != 0:
        raise ValueError("Input finger pattern length must be divisible by 6")

    finger_pattern = []
    for c in input_fp:
        if c == "+":
            finger_pattern.append(1)
        else:
            finger_pattern.append(-1)
    return finger_pattern


def determine_num_tets_octs(finger_pattern):
    num_octs = len(finger_pattern) // 6
    num_tets = 3 * num_octs
    return num_tets, num_octs


def generate_config_from_finger_pattern(env_path, finger_pattern):
    cusp = Cusp()
    cusp_generator = FingerCuspGenerator(cusp, finger_pattern)
    cusp = cusp_generator.generate()
    traversal = list(cusp_generator.traversal())
    num_tets, num_octs = determine_num_tets_octs(finger_pattern)

    write_config(env_path, num_tets, num_octs, cusp, traversal)


def generate_config_from_long_cusp_pattern(env_path, long_cusp_pattern):
    create_env_dir(env_path)

    cusp = Cusp()
    cusp_generator = LongCuspGenerator(cusp, long_cusp_pattern)
    cusp = cusp_generator.generate()
    traversal = list(cusp_generator.traversal())
    num_tris, num_sqrs = cusp_generator.get_num_polys()
    if num_tris % 4 != 0:
        logging.error("num tris must be a multiple of 4")
        exit(1)

    if num_sqrs % 6 != 0:
        logging.error("num sqrs must be a multiple of 6")
        exit(1)

    num_tets = num_tris // 4
    num_octs = num_sqrs // 6

    write_config(env_path, num_tets, num_octs, cusp, traversal)
    write_state(env_path, "init")
    logging.info(f"Generated search environment: {env_path.name}")


def generate(env_path: Path, finger_pattern: FingerPattern):
    create_env_dir(env_path)

    logging.info(f"Finger Pattern: {finger_pattern}")
    generate_config_from_finger_pattern(env_path, finger_pattern)
    write_state(env_path, "init")
    logging.info(f"Generated search environment: {env_path.name}")


def generate_multi(env_path: Path, multi_finger_pattern):
    create_env_dir(env_path)

    logging.info(f"Finger Pattern: {multi_finger_pattern}")
    generate_config_from_multi_finger_pattern(env_path, multi_finger_pattern)
    write_state(env_path, "init")
    logging.info(f"Generated search environment: {env_path.name}")


def generate_config_from_multi_finger_pattern(env_path, multi_finger_pattern):
    cusp = Cusp()
    cusp_generator = MultiFingerCuspGenerator(cusp, multi_finger_pattern)
    cusp_generator.generate()
    traversal = list(cusp_generator.traversal())
    num_tets, num_octs = determine_num_tets_octs(cusp_generator.flattened)
    write_config(env_path, num_tets, num_octs, cusp, traversal)


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
        help="String of '+' and '-' encoding the finger pattern",
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
