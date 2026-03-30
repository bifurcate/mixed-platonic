"""Search environment I/O utilities.

Handles reading and writing state, config, info, and completion data
for search environments on disk.
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
    """Write the environment state (init, exec, done) to state.json."""
    state_json_path = Path(env_path) / "state.json"
    with open(state_json_path, "w", encoding="utf-8") as f:
        json.dump({"state": state}, f)


def read_state(env_path: Path) -> str:
    """Read the environment state from state.json."""
    state_json_path = Path(env_path) / "state.json"
    with open(state_json_path, "r") as f:
        state_data = json.load(f)
    return state_data["state"]


def write_config(env_path: Path, num_tets: int, num_octs: int, cusp: Cusp, traversal):
    """Write the search configuration to config.json."""
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
    """Read the search configuration from config.json."""
    config_file_path = Path(env_path) / "config.json"
    with open(config_file_path, "r") as f:
        return json.load(f)


def write_info(env_path: Path, info: dict):
    """Write search run info (runtime, iterations, etc.) to info.json."""
    info_json_path = Path(env_path) / "info.json"
    with open(info_json_path, "w", encoding="utf-8") as f:
        json.dump(info, f)


def read_info(env_path: Path) -> dict:
    """Read search run info from info.json. Returns empty dict if missing."""
    info_json_path = Path(env_path) / "info.json"
    try:
        with open(info_json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def write_completed_to_jsonl(env_path: Path, completion):
    """Append a completed embedding to out.jsonl."""
    completed_entry = {"embeddings": completion}
    completed_file_path = Path(env_path) / "out.jsonl"
    with open(completed_file_path, "a") as f:
        f.write(json.dumps(completed_entry) + "\n")


def create_env(env_path: Path, num_tets: int, num_octs: int, cusp: Cusp, traversal):
    """Create a new search environment directory with config and init state."""
    create_env_dir(env_path)
    write_config(env_path, num_tets, num_octs, cusp, traversal)
    write_state(env_path, "init")
