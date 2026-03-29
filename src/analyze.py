import argparse
import logging
from pathlib import Path
import json

from stack import Stack

from construction import (
    load_traversal,
    Cusp,
    Embeddings,
    Construction,
)

from export_regina import to_regina_triangulation


def load_search_config(env_path):
    config_file_path = env_path / "config.json"
    with open(config_file_path, "r") as f:
        search_config = json.load(f)
    return search_config


def completed_stacks(env_path, config):
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

    config = load_search_config(env_path)

    for cons in completed_stacks(env_path, config):
        manifold_cellulation = cons.build_manifold_cellulation()
        regina_triangulation = to_regina_triangulation(
            manifold_cellulation, config["num_tets"], config["num_octs"]
        )
        print(regina_triangulation.isoSig())


if __name__ in "__main__":
    main()
