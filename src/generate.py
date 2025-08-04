import argparse
import logging
import time
from pathlib import Path
import json
import os


from construction import (
  FingerCuspGenerator,
  dump_traversal,
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

def generate_config_from_finger_pattern(name, finger_pattern):
  cusp_generator = FingerCuspGenerator(finger_pattern)
  cusp = cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  num_tets, num_octs = determine_num_tets_octs(finger_pattern)

  config_data = {
    'name': name,
    'num_tets': num_tets,
    'num_octs': num_octs,
    'cusp': cusp.dump(),
    'traversal': dump_traversal(traversal)
  }

  config_json_path = Path(name) / "config.json"

  with open(config_json_path, 'w', encoding='utf-8') as f:
    json.dump(config_data, f)

def main():
  
  logging.basicConfig(
    level=logging.DEBUG,
    format='MP-GENERATE|%(levelname)s: %(message)s',
  )

  parser = argparse.ArgumentParser(description="CLI frontend for generating Mixed Platonic censuses")

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
    '-o', '--output-dir',
    type=str,
    help="Directory to store info on completions" 
  )

  parser.add_argument(
    'name',
    type=str,
    help="Name of the search environment"
  )

  args = parser.parse_args()
  debug_on = args.debug_mode
  finger_pattern = parse_finger_pattern_arg(args.finger_pattern)
  name = args.name

  try:
    Path(name).mkdir()
  except FileExistsError:
    logging.error(f"search environment {name} already exists")
    exit(1)


  logging.info(f"Finger Pattern: {args.finger_pattern}")

  generate_config_from_finger_pattern(name, finger_pattern)

  logging.info(f"Generated search environment: {name}")
  
  
if __name__ == '__main__':
  main()