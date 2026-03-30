import argparse
import os
from pathlib import Path

from env import read_state, read_info


def get_completed(census_path) -> dict:

    completed = {}
    run_env_paths = (
        census_path / entry.name for entry in os.scandir(census_path) if entry.is_dir()
    )
    for p in run_env_paths:
        state = read_state(p)
        if state != "done":
            continue
        info = read_info(p)
        num_completed = info["num_completed"]
        if num_completed <= 0:
            continue
        completed[p.name] = num_completed
    return completed


def get_run_stats(census_path) -> dict:

    num_init = 0
    num_exec = 0
    num_done = 0
    num_total = 0

    run_env_paths = (
        census_path / entry.name for entry in os.scandir(census_path) if entry.is_dir()
    )

    for p in run_env_paths:
        state = read_state(p)

        if state == "init":
            num_init += 1
        elif state == "exec":
            num_exec += 1
        elif state == "done":
            num_done += 1

        num_total += 1

    return {
        "init": num_init,
        "exec": num_exec,
        "done": num_done,
        "total": num_total,
    }


def print_run_stats(run_stats):
    print("## RUN_STATS ##")
    print(f"init: {run_stats['init']}")
    print(f"exec: {run_stats['exec']}")
    print(f"done: {run_stats['done']}")
    print(f"total: {run_stats['total']}")
    print(f"percent complete: {(run_stats['done']/run_stats['total'])*100:.2f}%")
    print()


def print_completed(completed):
    print("## FOUND ##")

    if not completed:
        print("None")
        return

    for k, v in completed.items():
        print(f"{k}: {v}")


def main():
    parser = argparse.ArgumentParser(
        description="CLI frontend for Mixed Platonic census analysis"
    )

    parser.add_argument(
        "-d",
        "--debug-mode",
        action="store_true",
        help="Enable debug mode",
    )

    parser.add_argument(
        "-r",
        "--run-stats",
        action="store_true",
        help="Get runtime information",
    )

    parser.add_argument("name", type=str, help="Name of the search environment")

    args = parser.parse_args()
    debug = args.debug_mode
    census_name = args.name
    census_path = Path(census_name)

    run_stats = get_run_stats(census_path)
    print_run_stats(run_stats)
    completed = get_completed(census_path)
    print_completed(completed)


if __name__ == "__main__":
    main()
