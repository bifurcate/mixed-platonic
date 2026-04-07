"""Run the solver on a single search environment.

Loads a previously generated search environment from disk, runs the
backtracking solver to find all valid manifold cellulations, and writes
completions and run metadata back to the environment directory.

Supports stop/resume: pressing Ctrl+C during a run saves a checkpoint
to the environment directory. Running the solver again on the same
environment will detect the checkpoint and resume from where it left off.

State transitions:
    "init"  -> solver starts -> "exec"
    "exec"  -> Ctrl+C        -> checkpoint saved, state stays "exec"
    "exec"  -> solver resumes from checkpoint
    "exec"  -> solver finishes -> "done"

Usage:
    poetry run python src/solve.py my_env
"""

import json
import logging
import signal
import time
from pathlib import Path
import argparse

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
    write_checkpoint,
    read_checkpoint,
    remove_checkpoint,
)


def log_config(config):
    """Log the search configuration at INFO level.

    Args:
        config: Config dict as returned by ``read_config``.
    """
    logging.info(f"name: {config['name']}")
    logging.info(f"num_tets: {config['num_tets']}")
    logging.info(f"num_octs: {config['num_octs']}")
    logging.info(f"cusp: {config['cusp']}")
    logging.info(f"traversal: {config['traversal']}")


def solve(env_path):
    """Run the solver on a single search environment.

    Loads the config, builds the cusp tiling and construction, runs the
    solver, and writes all completions and run metadata to disk. Logs
    are written both to the console and to ``log.txt`` in the environment
    directory.

    If the environment is in "exec" state with a checkpoint, resumes
    from the checkpoint. Installs a SIGINT handler so that Ctrl+C
    saves a checkpoint instead of terminating immediately.

    Args:
        env_path: Path to a search environment directory.

    Returns:
        ``"completed"`` if the solver finished the search, ``"stopped"``
        if interrupted by Ctrl+C (checkpoint saved), or ``None`` if the
        environment was skipped (already done, missing, or in error).
    """
    env_path = Path(env_path)

    solve_logger = logging.getLogger("solve_logger")
    solve_logger.setLevel(logging.DEBUG)
    log_format = "MP-SOLVE|%(levelname)s: %(message)s"

    if not (env_path.exists() and env_path.is_dir()):
        solve_logger.error(
            f"search environment '{env_path.name}' does not exist, use generate to create"
        )
        return None

    state = read_state(env_path)
    resuming = False
    checkpoint = None

    if state == "done":
        solve_logger.info(
            f"search environment '{env_path.name}' already done, skipping"
        )
        return None
    elif state == "exec":
        checkpoint = read_checkpoint(env_path)
        if checkpoint is None:
            solve_logger.error(
                f"search environment '{env_path.name}' in exec state but no checkpoint found"
            )
            return None
        resuming = True
    elif state == "init":
        write_state(env_path, "exec")
    else:
        solve_logger.error(
            f"search environment '{env_path.name}' in unknown state '{state}'"
        )
        return None

    log_file_path = env_path / "log.txt"

    log_file_handler = logging.FileHandler(log_file_path)
    log_file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format)
    log_file_handler.setFormatter(file_formatter)

    solve_logger.addHandler(log_file_handler)

    try:
        config = read_config(env_path)
    except FileNotFoundError:
        solve_logger.error(f"config file for '{env_path.name}' does not exist")
        return None

    log_config(config)

    cusp = Cusp()
    cusp.load(config["cusp"])

    traversal = load_traversal(config["traversal"])
    num_tets = config["num_tets"]
    num_octs = config["num_octs"]

    embeddings = Embeddings()
    construction = Construction(cusp, embeddings)
    solver = Solver(traversal, construction, num_tets, num_octs)

    if resuming:
        solver.load_checkpoint(checkpoint)
        solve_logger.info(
            f"Resumed from checkpoint (counter={solver.counter}, "
            f"{len(solver.completed)} completions so far)"
        )

    # Install signal handlers for graceful stop (SIGINT for Ctrl+C,
    # SIGTERM for kill/SLURM job cancellation)
    def handle_stop(signum, frame):
        sig_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        solve_logger.info(f"Stop requested ({sig_name}), will save checkpoint...")
        solver.request_stop()

    original_sigint = signal.getsignal(signal.SIGINT)
    original_sigterm = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    start_time = time.perf_counter()
    result = solver.run()
    end_time = time.perf_counter()

    # Restore original signal handlers
    signal.signal(signal.SIGINT, original_sigint)
    signal.signal(signal.SIGTERM, original_sigterm)

    if result == "stopped":
        solve_logger.info(
            f"Stopped after {solver.counter} iterations "
            f"({len(solver.completed)} completions so far)"
        )
        checkpoint_data = solver.save_checkpoint()
        write_checkpoint(env_path, checkpoint_data)
        solve_logger.info("Checkpoint saved, run again to resume")
        return "stopped"

    else:
        solve_logger.info(
            f"Finished after {solver.counter} iterations "
            f"in {end_time - start_time:.6f} seconds"
        )
        solve_logger.info(f"{len(solver.completed)} completions found")

        # Write all completions (overwrite any partial output)
        out_path = env_path / "out.jsonl"
        out_path.unlink(missing_ok=True)
        for completion in solver.completed:
            write_completed_to_jsonl(env_path, completion)

        write_info(
            env_path,
            {
                "runtime": end_time - start_time,
                "iterations": solver.counter,
                "num_completed": len(solver.completed),
                "violation_counts": solver.violation_counts,
                "max_embeddings": solver.max_embeddings,
            },
        )

        if solver.max_embeddings_state is not None:
            max_emb_path = env_path / "max_embeddings_state.json"
            with open(max_emb_path, "w", encoding="utf-8") as f:
                json.dump(solver.max_embeddings_state, f)

        write_state(env_path, "done")
        remove_checkpoint(env_path)
        return "completed"


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
