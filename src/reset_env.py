"""Reset a search environment (or every environment in a census) to init.

For each target environment directory, removes all files except
``config.json`` and rewrites ``state.json`` with ``{"state": "init"}``.
This discards solver output, logs, checkpoints, and claim markers so the
environment is ready to be solved again from scratch.

When the target directory is not itself an environment (no config.json),
it is treated as a census root: every immediate subdirectory that
contains a config.json is reset.

Usage:
    poetry run python src/reset_env.py data/long-cusp/bababa
    poetry run python src/reset_env.py data/long-cusp
"""

import argparse
import logging
import shutil
from pathlib import Path

from env import write_state


def is_env_dir(path: Path) -> bool:
    return (path / "config.json").is_file()


def reset_env(env_path: Path) -> None:
    """Delete every file in env_path except config.json, then write init state."""
    for entry in env_path.iterdir():
        if entry.is_file() and entry.name != "config.json":
            entry.unlink()
        elif entry.is_dir() and entry.name == "debug":
            shutil.rmtree(entry)
        elif entry.is_dir():
            logging.warning(
                f"{env_path.name}: unexpected subdirectory {entry.name}, skipping"
            )
    write_state(env_path, "init")


def reset_census(census_path: Path) -> int:
    """Reset every environment subdirectory under census_path.

    Returns the number of environments reset.
    """
    count = 0
    for entry in sorted(census_path.iterdir()):
        if entry.is_dir() and is_env_dir(entry):
            reset_env(entry)
            count += 1
    return count


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        type=Path,
        help="Environment directory, or census root containing env subdirs.",
    )
    args = parser.parse_args()

    if not args.path.is_dir():
        logging.error(f"{args.path} is not a directory")
        raise SystemExit(1)

    if is_env_dir(args.path):
        reset_env(args.path)
        logging.info(f"reset environment {args.path}")
    else:
        n = reset_census(args.path)
        logging.info(f"reset {n} environment(s) under {args.path}")


if __name__ == "__main__":
    main()
