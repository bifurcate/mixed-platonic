"""Distributed census solver (worker process).

Iterates over the environments in a census directory, atomically claims
unclaimed ones, and runs the solver on each. Multiple instances of this
script can run in parallel against the same census directory -- the
file-based claiming protocol (using OS-level O_CREAT|O_EXCL) prevents
two workers from solving the same environment.

Usage:
    poetry run python src/solve_census.py my_census

Run multiple workers in parallel (e.g. in separate terminals or via a
job scheduler) pointing at the same census directory.
"""

import os
import argparse
from pathlib import Path

from solve import solve

CLAIM_FILE = ".claimed"
DONE_FILE = ".done"


def try_claim(work_dir: Path) -> bool:
    """Try to atomically claim a directory by creating .claimed"""
    marker = work_dir / CLAIM_FILE
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False


def mark_done(work_dir: Path):
    """Create a .done marker file in a work directory."""
    done_marker = work_dir / DONE_FILE
    done_marker.touch()


def claim_dir(census_dir) -> Path:
    """Find and claim the next unclaimed environment in the census.

    Iterates subdirectories and returns the first one that has neither
    a .claimed nor a .done marker. Returns None if all are claimed or done.

    Args:
        census_dir: Path to the census root directory.

    Returns:
        Path to the claimed directory, or None if no work remains.
    """
    for d in census_dir.iterdir():
        if not d.is_dir():
            continue
        if (d / CLAIM_FILE).exists() or (d / DONE_FILE).exists():
            continue
        if try_claim(d):
            return d
    return None


def process(work_dir: Path):
    """Solve a single environment and mark it done.

    Args:
        work_dir: Path to a claimed search environment directory.
    """
    print(f"[{os.getpid()}] Working on {work_dir}", flush=True)
    solve(work_dir)
    mark_done(work_dir)
    print(f"[{os.getpid()}] Finished {work_dir}", flush=True)


def main():

    parser = argparse.ArgumentParser(
        description="CLI frontend for solving Mixed Platonic censuses"
    )

    parser.add_argument(
        "census_dir",
        nargs="?",
        default=".",
        type=str,
        help="Name of the census directory",
    )

    args = parser.parse_args()
    census_dir = Path(args.census_dir)

    while True:
        work_dir = claim_dir(census_dir)
        if work_dir is None:
            print(f"[{os.getpid()}] No more work, exiting", flush=True)
            break
        print(f"[{os.getpid()}] Working on {work_dir}", flush=True)
        solve(work_dir)
        mark_done(work_dir)
        print(f"[{os.getpid()}] Finished {work_dir}", flush=True)


if __name__ == "__main__":
    main()
