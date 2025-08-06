import argparse
import logging
from pathlib import Path

from generate import generate
from bracelets import generate_2_bracelets
from finger_cusp import to_finger_pattern_str

def main():

  logging.basicConfig(
    level=logging.DEBUG,
    format='MP-GENERATE-CENSUS|%(levelname)s: %(message)s',
  )

  parser = argparse.ArgumentParser(description="CLI frontend for generating Mixed Platonic censuses")

  parser.add_argument(
    '-n', '--num-fingers',
    type=int,
    help="Length of finger patterns to enumerate"
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
  census_name = args.name
  census_root = Path(census_name)
  num_fingers = args.num_fingers
  
  
  try:
    Path(census_root).mkdir()
  except FileExistsError:
    logging.error(f"census {census_name} already exists")

  logging.info("Generating census '{census_name}'")

  for fp in generate_2_bracelets(num_fingers):
    fp_str = to_finger_pattern_str(fp)
    env_path = census_root / fp_str
    generate(env_path, fp)

  logging.info("Completed census generation")

if __name__ == '__main__':
  main()