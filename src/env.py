"""Search environment I/O utilities.

A search environment is a directory on disk that holds all the data for a
single solver run. This module provides functions to create, read, and write
the files that make up an environment:

    env_dir/
        config.json      — cusp tiling, traversal order, and cell counts
        state.json       — lifecycle state: "init" | "exec" | "done"
        info.json        — post-run metadata (runtime, iterations, completions)
        out.jsonl        — completed embeddings, one JSON object per line
        log.txt          — solver log output (created by solve.py)
        checkpoint.json  — solver checkpoint for stop/resume (created on stop)

All other modules that need to interact with environment data on disk import
from here rather than duplicating I/O logic.
"""

import json
import logging
from pathlib import Path

from construction import Cusp, dump_traversal


def create_env_dir(env_path: Path):
    """Create the directory for a search environment.

    Args:
        env_path: Path to the environment directory.

    Raises:
        SystemExit: If the directory already exists.
    """
    try:
        env_path.mkdir()
    except FileExistsError:
        logging.error(f"search environment {env_path.name} already exists")
        exit(1)


def write_state(env_path: Path, state: str):
    """Write the environment lifecycle state to state.json.

    Args:
        env_path: Path to the environment directory.
        state: One of "init" (generated, ready to solve), "exec" (solver
            running), or "done" (solver finished).
    """
    state_json_path = Path(env_path) / "state.json"
    with open(state_json_path, "w", encoding="utf-8") as f:
        json.dump({"state": state}, f)


def read_state(env_path: Path) -> str:
    """Read the environment lifecycle state from state.json.

    Args:
        env_path: Path to the environment directory.

    Returns:
        The state string ("init", "exec", or "done").
    """
    state_json_path = Path(env_path) / "state.json"
    with open(state_json_path, "r") as f:
        state_data = json.load(f)
    return state_data["state"]


def write_config(env_path: Path, num_tets: int, num_octs: int, cusp: Cusp, traversal):
    """Write the search configuration to config.json.

    The config captures everything the solver needs to reconstruct the cusp
    tiling and run the search: cell counts, serialized cusp pairings, and
    the traversal order for embedding cells.

    Args:
        env_path: Path to the environment directory.
        num_tets: Number of tetrahedra in the decomposition.
        num_octs: Number of octahedra in the decomposition.
        cusp: The cusp tiling with all edge pairings defined.
        traversal: Ordered list of cusp cells to embed during search.
    """
    config_data = {
        "name": env_path.name,
        "num_tets": num_tets,
        "num_octs": num_octs,
        "cusp": cusp.dump(),
        "traversal": dump_traversal(traversal),
    }
    config_json_path = Path(env_path) / "config.json"
    with open(config_json_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f)


def read_config(env_path: Path) -> dict:
    """Read the search configuration from config.json.

    Args:
        env_path: Path to the environment directory.

    Returns:
        Dict with keys: name, num_tets, num_octs, cusp, traversal.
    """
    config_file_path = Path(env_path) / "config.json"
    with open(config_file_path, "r") as f:
        return json.load(f)


def write_info(env_path: Path, info: dict):
    """Write post-run metadata to info.json.

    Args:
        env_path: Path to the environment directory.
        info: Dict with keys like "runtime", "iterations", "num_completed".
    """
    info_json_path = Path(env_path) / "info.json"
    with open(info_json_path, "w", encoding="utf-8") as f:
        json.dump(info, f)


def read_info(env_path: Path) -> dict:
    """Read post-run metadata from info.json.

    Args:
        env_path: Path to the environment directory.

    Returns:
        Dict of run metadata, or empty dict if info.json does not exist.
    """
    info_json_path = Path(env_path) / "info.json"
    try:
        with open(info_json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def write_completed_to_jsonl(env_path: Path, completion):
    """Append a completed embedding to out.jsonl.

    Each line in out.jsonl is a JSON object with an "embeddings" key
    containing the serialized embedding data for one valid completion.

    Args:
        env_path: Path to the environment directory.
        completion: Serializable embedding data from the solver.
    """
    completed_entry = {"embeddings": completion}
    completed_file_path = Path(env_path) / "out.jsonl"
    with open(completed_file_path, "a") as f:
        f.write(json.dumps(completed_entry) + "\n")


def write_checkpoint(env_path: Path, checkpoint: dict):
    """Write solver checkpoint to checkpoint.json.

    The checkpoint captures the solver's explicit search stack, iteration
    counter, and any completions found so far, allowing the search to be
    resumed later from exactly where it left off.

    Args:
        env_path: Path to the environment directory.
        checkpoint: Serialized solver state from ``Solver.save_checkpoint()``.
    """
    checkpoint_path = Path(env_path) / "checkpoint.json"
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f)


def read_checkpoint(env_path: Path) -> dict | None:
    """Read solver checkpoint from checkpoint.json.

    Args:
        env_path: Path to the environment directory.

    Returns:
        Checkpoint dict, or None if no checkpoint exists.
    """
    checkpoint_path = Path(env_path) / "checkpoint.json"
    try:
        with open(checkpoint_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def remove_checkpoint(env_path: Path):
    """Remove checkpoint.json if it exists.

    Called after the solver completes normally to clean up the checkpoint
    file, since it is no longer needed.

    Args:
        env_path: Path to the environment directory.
    """
    checkpoint_path = Path(env_path) / "checkpoint.json"
    checkpoint_path.unlink(missing_ok=True)


def create_env(env_path: Path, num_tets: int, num_octs: int, cusp: Cusp, traversal):
    """Create a new search environment directory with config and init state.

    Convenience function that combines create_env_dir, write_config, and
    write_state into a single call. Used by examples.py and other code that
    builds cusp tilings programmatically.

    Args:
        env_path: Path to the environment directory to create.
        num_tets: Number of tetrahedra in the decomposition.
        num_octs: Number of octahedra in the decomposition.
        cusp: The cusp tiling with all edge pairings defined.
        traversal: Ordered list of cusp cells to embed during search.
    """
    create_env_dir(env_path)
    write_config(env_path, num_tets, num_octs, cusp, traversal)
    write_state(env_path, "init")
