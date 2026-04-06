"""Distributed census solver (worker process).

Iterates over the environments in a census directory, atomically claims
unclaimed ones, and runs the solver on each. Multiple instances of this
script can run in parallel against the same census directory -- the
file-based claiming protocol (using OS-level O_CREAT|O_EXCL) prevents
two workers from solving the same environment.

If a worker is interrupted (Ctrl+C), the solver saves a checkpoint and
the worker releases its claim on the current environment so that another
worker (or a restarted instance) can pick it up and resume from the
checkpoint.

If the census directory contains a ``manifest.json`` (copied there by
``construct_census.py``), environments are visited in manifest order so
that earlier patterns are solved first.  Otherwise falls back to
filesystem directory order.

Usage:
    poetry run python src/solve_census.py my_census
"""

import json
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


def release_claim(work_dir: Path):
    """Remove the .claimed marker so another worker can pick up this directory.

    Called when the solver is stopped mid-run (e.g. via Ctrl+C). The
    checkpoint is preserved in the environment directory, so the next
    worker that claims this directory will resume from where it left off.

    Args:
        work_dir: Path to the claimed work directory.
    """
    claim_marker = work_dir / CLAIM_FILE
    claim_marker.unlink(missing_ok=True)


def env_dirs_from_manifest(census_dir: Path, manifest_path: str) -> list[Path]:
    """Return environment directories in manifest order.

    Args:
        census_dir: Path to the census root directory.
        manifest_path: Path to the manifest JSON file.

    Returns:
        List of environment directory paths, in manifest order.
    """
    with open(manifest_path) as f:
        manifest = json.load(f)
    return [census_dir / pattern for pattern in manifest["patterns"]]


def claim_dir(census_dir: Path, ordering: list[Path] | None = None) -> Path | None:
    """Find and claim the next unclaimed environment in the census.

    When *ordering* is provided, directories are visited in that order.
    Otherwise falls back to ``iterdir()`` order.

    Args:
        census_dir: Path to the census root directory.
        ordering: Optional explicit list of directories to try, in order.

    Returns:
        Path to the claimed directory, or None if no work remains.
    """
    candidates = ordering if ordering is not None else census_dir.iterdir()
    for d in candidates:
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

    manifest_path = census_dir / "manifest.json"
    ordering = None
    if manifest_path.exists():
        ordering = env_dirs_from_manifest(census_dir, manifest_path)

    while True:
        work_dir = claim_dir(census_dir, ordering)
        if work_dir is None:
            print(f"[{os.getpid()}] No more work, exiting", flush=True)
            break
        print(f"[{os.getpid()}] Working on {work_dir}", flush=True)
        result = solve(work_dir)
        if result == "completed":
            mark_done(work_dir)
            print(f"[{os.getpid()}] Finished {work_dir}", flush=True)
        elif result == "stopped":
            release_claim(work_dir)
            print(f"[{os.getpid()}] Stopped, exiting", flush=True)
            break
        else:
            # Skipped (already done, error, etc.) — mark done to avoid retrying
            mark_done(work_dir)
            print(f"[{os.getpid()}] Skipped {work_dir}", flush=True)


if __name__ == "__main__":
    main()
