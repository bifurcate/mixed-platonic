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
    done_marker = work_dir / DONE_FILE
    done_marker.touch()


def claim_dir(census_dir) -> Path:
    """Find and claim a directory that is not yet claimed or done"""
    for d in census_dir.iterdir():
        if not d.is_dir():
            continue
        if (d / CLAIM_FILE).exists() or (d / DONE_FILE).exists():
            continue
        if try_claim(d):
            return d
    return None


def process(work_dir: Path):
    print(f"[{os.getpid()}] Working on {work_dir}", flush=True)
    solve(work_dir, debug=False)
    mark_done(work_dir)
    print(f"[{os.getpid()}] Finished {work_dir}", flush=True)


def main():

    parser = argparse.ArgumentParser(
        description="CLI frontend for solving Mixed Platonic censuses"
    )

    parser.add_argument(
        "-d",
        "--debug-mode",
        action="store_true",
        help="Enable debug mode",
    )

    parser.add_argument(
        "census_dir",
        nargs="?",
        default=".",
        type=str,
        help="Name of the census directory",
    )

    args = parser.parse_args()
    debug = args.debug_mode
    census_dir = Path(args.census_dir)

    while True:
        work_dir = claim_dir(census_dir)
        if work_dir is None:
            print(f"[{os.getpid()}] No more work, exiting", flush=True)
            break
        print(f"[{os.getpid()}] Working on {work_dir}", flush=True)
        solve(work_dir, debug=debug)
        mark_done(work_dir)
        print(f"[{os.getpid()}] Finished {work_dir}", flush=True)


if __name__ == "__main__":
    main()
