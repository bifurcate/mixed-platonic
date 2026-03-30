"""Analyze completed solver results for a single search environment.

Loads completions from out.jsonl, reconstructs the manifold cellulation
for each, and exports Regina isomorphism signatures. These signatures
are canonical identifiers that can be used to look up manifolds in
existing censuses or compare results across runs.

Usage:
    poetry run python src/analyze.py -i my_env
"""

import argparse
import json
import logging
from pathlib import Path

from construction import (
    load_traversal,
    Cusp,
    Embeddings,
    Construction,
)
from export_regina import to_regina_triangulation
from env import read_config


def completed_stacks(env_path, config):
    """Yield reconstructed Construction objects from completed solver output.

    Reads each line of out.jsonl, deserializes the embedding data, and
    rebuilds the full Construction (cusp + embeddings + traversal) so
    that the caller can build manifold cellulations from it.

    Args:
        env_path: Path to the search environment directory.
        config: Config dict as returned by ``read_config``.

    Yields:
        Construction objects, one per completed embedding.
    """
    completed_file_path = Path(env_path) / "out.jsonl"
    if not completed_file_path.exists():
        logging.error(f"no completed output exists")

    with open(completed_file_path, "r") as f:
        for line in f:
            cusp = Cusp()
            embeddings = Embeddings()
            cusp.load(config["cusp"])
            traversal = load_traversal(config["traversal"])
            num_tets = config["num_tets"]
            num_octs = config["num_octs"]
            completed_entry = json.loads(line)
            embeddings.load(completed_entry["embeddings"])
            construction = Construction(cusp, embeddings, traversal, num_tets, num_octs)
            yield construction


def main():

    parser = argparse.ArgumentParser(
        description="CLI frontend for analyzing Mixed Platonic censuses"
    )

    parser.add_argument(
        "name",
        type=str,
        help="Name of the search environment",
    )

    parser.add_argument(
        "-i",
        "--get-iso-sigs",
        action="store_true",
        help="Load into regina triangulation and return isomorphism signatures",
    )

    args = parser.parse_args()
    name = args.name

    env_path = Path(name)

    if not (env_path.exists() and env_path.is_dir()):
        logging.error(
            f"search environment '{name}' does not exist, use generate to create"
        )

    config = read_config(env_path)

    for cons in completed_stacks(env_path, config):
        manifold_cellulation = cons.build_manifold_cellulation()
        regina_triangulation = to_regina_triangulation(
            manifold_cellulation, config["num_tets"], config["num_octs"]
        )
        print(regina_triangulation.isoSig())


if __name__ in "__main__":
    main()
