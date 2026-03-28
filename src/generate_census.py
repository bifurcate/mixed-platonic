import argparse
import logging
from pathlib import Path

from generate import (
    generate,
    generate_multi,
    generate_config_from_long_cusp_pattern,
)
from bracelets import (
    generate_2_bracelets,
    generate_multi_2_bracelets,
)

from finger_cusp import (
    to_finger_pattern_str,
    to_multi_finger_pattern_str,
)

from long_cusp import build_cusp_sequences


def generate_multi_census(census_root, n):

    try:
        Path(census_root).mkdir()
    except FileExistsError:
        logging.error(f"census {census_root.name} already exists")

    logging.info("Generating census '{census_root.name}'")

    for mfp in generate_multi_2_bracelets(n):
        mfp_str = to_multi_finger_pattern_str(mfp)
        env_path = census_root / mfp_str
        generate_multi(env_path, mfp)


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="MP-GENERATE-CENSUS|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="CLI frontend for generating Mixed Platonic censuses"
    )

    parser.add_argument(
        "-n", "--num-fingers", type=int, help="Length of finger patterns to enumerate"
    )

    parser.add_argument(
        "-l", "--long-cusp", type=int, help="Maximum length of long cusp pattern"
    )

    parser.add_argument(
        "-d",
        "--debug-mode",
        action="store_true",
        help="Enable debug mode",
    )

    parser.add_argument("name", type=str, help="Name of the search environment")

    args = parser.parse_args()
    debug = args.debug_mode
    census_name = args.name
    census_root = Path(census_name)
    num_fingers = args.num_fingers

    try:
        Path(census_root).mkdir()
    except FileExistsError:
        logging.error(f"census {census_name} already exists")

    logging.info("Generating census '{census_name}'")

    if num_fingers:
        for fp in generate_2_bracelets(num_fingers):
            fp_str = to_finger_pattern_str(fp)
            env_path = census_root / fp_str
            generate(env_path, fp)

    elif args.long_cusp:
        for cs in build_cusp_sequences(args.long_cusp):
            env_path = census_root / cs
            generate_config_from_long_cusp_pattern(env_path, cs)

    logging.info("Completed census generation")


if __name__ == "__main__":
    main()
