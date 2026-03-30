import argparse
import logging
import time
from pathlib import Path

from construction import (
    load_traversal,
    Cusp,
    Embeddings,
    Construction,
)
from solver import Solver
from env import (
    read_config,
    read_state,
    write_state,
    write_info,
    write_completed_to_jsonl,
)

def log_config(config):
    logging.info(f"name: {config['name']}")
    logging.info(f"num_tets: {config['num_tets']}")
    logging.info(f"num_octs: {config['num_octs']}")
    logging.info(f"cusp: {config['cusp']}")
    logging.info(f"traversal: {config['traversal']}")


def solve(env_path):
    env_path = Path(env_path)

    solve_logger = logging.getLogger("solve_logger")
    solve_logger.setLevel(logging.DEBUG)
    log_format = "MP-SOLVE|%(levelname)s: %(message)s"

    if not (env_path.exists() and env_path.is_dir()):
        solve_logger.error(
            f"search environment '{env_path.name}' does not exist, use generate to create"
        )

    state = read_state(env_path)
    if state != "init":
        solve_logger.error(
            f"search environment '{env_path.name}' not in init state, skipping execution"
        )
        return

    write_state(env_path, "exec")

    log_file_path = env_path / "log.txt"

    log_file_handler = logging.FileHandler(log_file_path)
    log_file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format)
    log_file_handler.setFormatter(file_formatter)

    solve_logger.addHandler(log_file_handler)

    try:
        config = read_config(env_path)
    except FileExistsError:
        solve_logger.error(f"config file for '{env_path.name}' does not exist")

    log_config(config)

    cusp = Cusp()
    cusp.load(config["cusp"])

    traversal = load_traversal(config["traversal"])
    num_tets = config["num_tets"]
    num_octs = config["num_octs"]

    embeddings = Embeddings()
    construction = Construction(cusp, embeddings)
    solver = Solver(traversal, construction, num_tets, num_octs)

    start_time = time.perf_counter()
    num_completed = 0
    solver.run()
    end_time = time.perf_counter()

    solve_logger.info(
        f"Finish after {solver.counter} iterations in {end_time - start_time:.6f} seconds"
    )
    solve_logger.info(f"{len(solver.completed)} completions found")

    for completion in solver.completed:
        write_completed_to_jsonl(env_path, completion)

    write_info(
        env_path,
        {
            "runtime": end_time - start_time,
            "iterations": solver.counter,
            "num_completed": num_completed,
        },
    )

    write_state(env_path, "done")


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format="MP-SOLVE|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="CLI frontend for running the Mixed Platonic solver"
    )

    parser.add_argument("name", type=str, help="Name of the search environment")

    args = parser.parse_args()
    name = args.name
    env_path = Path(name)

    solve(env_path)


if __name__ == "__main__":
    main()
