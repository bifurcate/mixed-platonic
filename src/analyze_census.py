"""Analyze the status and results of a census run.

Reports aggregate statistics across all environments in a census
directory: how many are in each lifecycle state (init, exec, done)
and which completed environments produced valid cellulations.

Reads from the combined ``data.json`` produced by ``gather_census.py``.

Usage:
    poetry run python src/analyze_census.py my_census
"""

import argparse
import json
from pathlib import Path


def load_census_data(census_path: Path) -> dict:
    """Load the combined data.json from a census directory.

    Args:
        census_path: Path to the census root directory.

    Returns:
        Dict mapping environment names to their gathered data.
    """
    data_path = census_path / "data.json"
    with open(data_path, "r") as f:
        return json.load(f)


def get_completed(census_data: dict) -> dict:
    """Find environments that finished with at least one completion.

    Args:
        census_data: Combined census data from data.json.

    Returns:
        Dict mapping environment name to number of completions.
    """
    completed = {}
    for env_name, env_data in census_data.items():
        state = env_data.get("state", {}).get("state")
        if state != "done":
            continue
        info = env_data.get("info", {})
        num_completed = info.get("num_completed", 0)
        if num_completed <= 0:
            continue
        completed[env_name] = num_completed
    return completed


def get_run_stats(census_data: dict) -> dict:
    """Count environments in each lifecycle state.

    Args:
        census_data: Combined census data from data.json.

    Returns:
        Dict with keys: init, exec, done, total.
    """
    num_init = 0
    num_exec = 0
    num_done = 0
    num_total = 0

    for env_data in census_data.values():
        state = env_data.get("state", {}).get("state")

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
    """Print a summary of environment lifecycle states to stdout."""
    print("## RUN_STATS ##")
    print(f"init: {run_stats['init']}")
    print(f"exec: {run_stats['exec']}")
    print(f"done: {run_stats['done']}")
    print(f"total: {run_stats['total']}")
    print(f"percent complete: {(run_stats['done']/run_stats['total'])*100:.2f}%")
    print()


def print_completed(completed):
    """Print environments that had completions to stdout."""
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
        "-r",
        "--run-stats",
        action="store_true",
        help="Get runtime information",
    )

    parser.add_argument("name", type=str, help="Name of the search environment")

    args = parser.parse_args()
    census_name = args.name
    census_path = Path(census_name)

    census_data = load_census_data(census_path)

    run_stats = get_run_stats(census_data)
    print_run_stats(run_stats)
    completed = get_completed(census_data)
    print_completed(completed)


if __name__ == "__main__":
    main()
