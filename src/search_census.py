import argparse
import logging
import multiprocessing
import os
from pathlib import Path

from search import search

def search_args(census_path, debug):
  return ((census_path / entry.name, debug) for entry in os.scandir(census_path) if entry.is_dir())

def main():
  logging.basicConfig(
    level=logging.DEBUG,
    format='MP-SEARCH-CENSUS|%(levelname)s: %(message)s',
  )

  parser = argparse.ArgumentParser(description="CLI frontend for executing Mixed Platonic censuses")

  parser.add_argument(
    '-w', '--workers',
    type=int,
    default=os.cpu_count(),
    help="Number of worker processes (default: use os.cpu_count)",
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
  num_processes = args.workers
  census_name = args.name
  census_root = Path(census_name)

  logging.info(f"Starting multi-process census")
  logging.info(f"Census: {census_name}")
  logging.info(f"Num worker processes: {num_processes}")

  with multiprocessing.Pool(num_processes) as pool:
    results = pool.starmap(search, search_args(census_root, debug))

if __name__ == '__main__':
  main()