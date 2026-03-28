import argparse
import json
import time
import logging
from pathlib import Path

from construction import (
    load_traversal,
    Cusp,
    Embeddings,
    Construction,
)

from stack import (
    Stack,
)

DEBUG_REPORT_INTERVAL = 1000


def load_search_config(env_path):
    config_file_path = env_path / "config.json"
    with open(config_file_path, "r") as f:
        search_config = json.load(f)
    return search_config


def log_config(config):
    logging.info(f"name: {config['name']}")
    logging.info(f"num_tets: {config['num_tets']}")
    logging.info(f"num_octs: {config['num_octs']}")
    logging.info(f"cusp: {config['cusp']}")
    logging.info(f"traversal: {config['traversal']}")


def write_completed_to_jsonl(env_path, iteration, completed_stack):
    completed_entry = {"iteration": iteration, "completed_stack": completed_stack}
    completed_file_path = Path(env_path) / "out.jsonl"
    with open(completed_file_path, "a") as f:
        f.write(json.dumps(completed_entry) + "\n")


def write_info_json(env_path: Path, info: dict):
    state_json_path = Path(env_path) / "info.json"
    with open(state_json_path, "w", encoding="utf-8") as f:
        json.dump(info, f)


def write_state(env_path: Path, state: str):
    state_data = {"state": state}
    state_json_path = Path(env_path) / "state.json"
    with open(state_json_path, "w", encoding="utf-8") as f:
        json.dump(state_data, f)


def read_state(env_path: Path) -> str:
    state_json_path = Path(env_path) / "state.json"
    with open(state_json_path, "r") as f:
        state_data = json.load(f)
    return state_data["state"]


def search(env_path, debug=False):
    env_path = Path(env_path)

    search_logger = logging.getLogger("search_logger")
    search_logger.setLevel(logging.DEBUG)
    log_format = "MP-SEARCH|%(levelname)s: %(message)s"

    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.DEBUG)  # or whatever level you want
    # console_formatter = logging.Formatter(log_format)
    # console_handler.setFormatter(console_formatter)

    # search_logger.addHandler(console_handler)

    if not (env_path.exists() and env_path.is_dir()):
        search_logger.error(
            f"search environment '{env_path.name}' does not exist, use generate to create"
        )

    state = read_state(env_path)
    if state != "init":
        search_logger.error(
            f"search environment '{env_path.name}' not in init state, skipping execution"
        )
        return

    write_state(env_path, "exec")

    log_file_path = env_path / "log.txt"

    log_file_handler = logging.FileHandler(log_file_path)
    log_file_handler.setLevel(
        logging.DEBUG
    )  # You can have different levels per handler
    file_formatter = logging.Formatter(log_format)
    log_file_handler.setFormatter(file_formatter)

    search_logger.addHandler(log_file_handler)

    try:
        config = load_search_config(env_path)
    except FileExistsError:
        search_logger.error(f"config file for '{name}' does not exist")

    log_config(config)

    if debug:
        config["debug"] = True
    else:
        config["debug"] = False

    cusp = Cusp()
    cusp.load(config["cusp"])

    traversal = load_traversal(config["traversal"])
    num_tets = config["num_tets"]
    num_octs = config["num_octs"]
    name = config["name"]

    embeddings = Embeddings()
    construction = Construction(cusp, embeddings)
    stack = Stack(traversal, construction, num_tets, num_octs)

    start_time = time.perf_counter()
    num_completed = 0
    stack.run()
    # while stack.done == False:
    #   completed = stack.next_()
    #   if completed:
    #     num_completed += 1
    #     write_completed_to_jsonl(env_path, stack.counter, completed)
    #     search_logger.info(f"Completion found at iteration {stack.counter}")
    #   if debug and stack.counter % DEBUG_REPORT_INTERVAL == 0:
    #     check_in_time = time.perf_counter()
    #     search_logger.debug(f"iteration: {stack.counter}, completions: {num_completed}, runtime: {(check_in_time - start_time):.6f}s")
    end_time = time.perf_counter()

    search_logger.info(
        f"Finish after {stack.counter} iterations in {end_time - start_time:.6f} seconds"
    )
    search_logger.info(f"{stack.completed_count} completions found")

    write_info_json(
        env_path,
        {
            "runtime": end_time - start_time,
            "iterations": stack.counter,
            "num_completed": num_completed,
        },
    )

    write_state(env_path, "done")


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="MP-SEARCH|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="CLI frontend for Mixed Platonic census"
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
    name = args.name
    env_path = Path(name)

    search(env_path, debug)


if __name__ == "__main__":
    main()
