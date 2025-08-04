import argparse
import logging
import time
from pathlib import Path
import json
import os

from stack import (
  Stack
)

from construction import (
  load_traversal,
  Cusp,
  Embeddings,
  Construction,
)

from export_regina import (
  to_regina_triangulation
)

def load_search_config(env_path):
  config_file_path = env_path / 'config.json'
  with open(config_file_path, 'r') as f:
    search_config = json.load(f)
  return search_config

def completed_stacks(env_path, config):
  completed_file_path = Path(env_path) / 'out.jsonl'
  if not completed_file_path.exists():
    logging.error(f"no completed output exists")
  
  with open(completed_file_path, 'r') as f:
    for line in f:
      cusp = Cusp()
      cusp.load(config['cusp'])
      traversal = load_traversal(config['traversal'])
      num_tets = config['num_tets']
      num_octs = config['num_octs']
      embeddings = Embeddings()
      construction = Construction(cusp, embeddings)
      completed_entry = json.loads(line)
      input_stack = completed_entry['completed_stack']
      stack = Stack(traversal, construction, num_tets, num_octs)
      stack.load(input_stack)
      yield stack

def main():

  parser = argparse.ArgumentParser(description="CLI frontend for analyzing Mixed Platonic censuses")

  parser.add_argument(
    'name',
    type=str,
    help="Name of the search environment",
  )

  parser.add_argument(
    '-i', '--get-iso-sigs',
    action='store_true',
    help="Load into regina triangulation and return isomorphism signatures",
  )

  args = parser.parse_args()
  name = args.name

  env_path = Path(name)

  if not (env_path.exists() and env_path.is_dir()):
    logging.error(f"search environment '{name}' does not exist, use generate to create")
  

  config = load_search_config(env_path)

  for st in completed_stacks(env_path, config):
    manifold_cellulation = st.construction.build_manifold_cellulation()
    regina_triangulation = to_regina_triangulation(manifold_cellulation, config['num_tets'], config['num_octs'])
    print(regina_triangulation.isoSig())

if __name__ in '__main__':
  main()

