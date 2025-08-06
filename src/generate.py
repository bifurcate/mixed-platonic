import argparse
import logging
import time
from pathlib import Path
import json
import os

from construction import (
  dump_traversal,
  Cusp,
)
from finger_cusp import (
  FingerCuspGenerator,
  FingerPattern,
  MultiFingerCuspGenerator,
)

def parse_finger_pattern_arg(input_fp: str):
  if not all(c in '+-' for c in input_fp):
    raise ValueError("Input finger pattern must consist of '+' and '-' characters")
  
  if len(input_fp) % 6 != 0:
    raise ValueError("Input finger pattern length must be divisible by 6")
  
  finger_pattern = []
  for c in input_fp:
    if c == '+':
      finger_pattern.append(1)
    else:
      finger_pattern.append(-1)
  return finger_pattern

def determine_num_tets_octs(finger_pattern):
  num_octs = len(finger_pattern) // 6
  num_tets = 3 * num_octs
  return num_tets, num_octs

def write_state(env_path: Path, state: str):
  state_data = {'state': state}
  state_json_path = Path(env_path) / 'state.json'
  with open(state_json_path, 'w', encoding='utf-8') as f:
    json.dump(state_data, f)

def read_state(env_path: Path) -> str:
  state_json_path = Path(env_path) / 'state.json'
  with open(state_json_path, 'r') as f:
    state_data = json.load(f)
  return state_data['state']

def generate_config_from_finger_pattern(env_path, finger_pattern):
  cusp = Cusp()
  cusp_generator = FingerCuspGenerator(cusp, finger_pattern)
  cusp = cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  num_tets, num_octs = determine_num_tets_octs(finger_pattern)

  config_data = {
    'name': env_path.name,
    'num_tets': num_tets,
    'num_octs': num_octs,
    'cusp': cusp.dump(),
    'traversal': dump_traversal(traversal)
  }

  config_json_path = Path(env_path) / "config.json"

  with open(config_json_path, 'w', encoding='utf-8') as f:
    json.dump(config_data, f)

def generate(env_path: Path, finger_pattern: FingerPattern, debug=False):
  try:
    Path(env_path).mkdir()
  except FileExistsError:
    logging.error(f"search environment {env_path.name} already exists")
    exit(1)

  logging.info(f"Finger Pattern: {finger_pattern}")
  generate_config_from_finger_pattern(env_path, finger_pattern)
  write_state(env_path, 'init')
  logging.info(f"Generated search environment: {env_path.name}")

def generate_multi(env_path: Path, multi_finger_pattern, debug=False):
  try:
    Path(env_path).mkdir()
  except FileExistsError:
    logging.error(f"search environment {env_path.name} already exists")
    exit(1)

  logging.info(f"Finger Pattern: {multi_finger_pattern}")
  generate_config_from_multi_finger_pattern(env_path, multi_finger_pattern)
  write_state(env_path, 'init')
  logging.info(f"Generated search environment: {env_path.name}")

def generate_config_from_multi_finger_pattern(env_path, multi_finger_pattern):
  cusp = Cusp()
  cusp_generator = MultiFingerCuspGenerator(cusp, multi_finger_pattern)
  cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  num_tets, num_octs = determine_num_tets_octs(cusp_generator.flattened)

  config_data = {
    'name': env_path.name,
    'num_tets': num_tets,
    'num_octs': num_octs,
    'cusp': cusp.dump(),
    'traversal': dump_traversal(traversal)
  }

  config_json_path = Path(env_path) / "config.json"

  with open(config_json_path, 'w', encoding='utf-8') as f:
    json.dump(config_data, f)

def main():
  
  logging.basicConfig(
    level=logging.DEBUG,
    format='MP-GENERATE|%(levelname)s: %(message)s',
  )

  parser = argparse.ArgumentParser(description="CLI frontend for generating Mixed Platonic search environments")

  parser.add_argument(
    '-f', '--finger-pattern',
    type=str,
    help="String of '+' and '-' encoding the finger pattern" 
  )

  parser.add_argument(
    '-d', '--debug-mode',
    action='store_true',
    help="Enable debug mode",
  )

  parser.add_argument(
    'name',
    type=str,
    help="Name of the search environment"
  )

  args = parser.parse_args()
  debug = args.debug_mode
  finger_pattern = parse_finger_pattern_arg(args.finger_pattern)
  name = args.name
  env_path = Path(name)

  generate(env_path, finger_pattern, debug)

  
if __name__ == '__main__':
  main()