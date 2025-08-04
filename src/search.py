import argparse
import json
import sys
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
  config_file_path = env_path / 'config.json'
  with open(config_file_path, 'r') as f:
    search_config = json.load(f)
  return search_config

def log_config(config):
  logging.info(f"name: {config['name']}")
  logging.info(f"num_tets: {config['num_tets']}")
  logging.info(f"num_octs: {config['num_octs']}")
  logging.info(f"cusp: {config['cusp']}")
  logging.info(f"traversal: {config['traversal']}")

def write_completed_to_jsonl(env_path, iteration, completed_stack):
  completed_entry = {'iteration': iteration, 'completed_stack': completed_stack}
  completed_file_path = Path(env_path) / 'out.jsonl'
  with open(completed_file_path, "a") as f:
      f.write(json.dumps(completed_entry) + "\n")

def run(config):
  cusp = Cusp()
  cusp.load(config['cusp'])
  traversal = load_traversal(config['traversal'])
  num_tets = config['num_tets']
  num_octs = config['num_octs']
  name = config['name']
  debug_on = config['debug']
  
  embeddings = Embeddings()
  construction = Construction(cusp, embeddings)
  stack = Stack(traversal, construction, num_tets, num_octs)

  start_time = time.perf_counter()
  while stack.done == False:
    stack.next_()
    if debug_on and stack.counter % DEBUG_REPORT_INTERVAL == 0:
      check_in_time = time.perf_counter()
      logging.debug(f"iteration: {stack.counter}, completions: {len(stack.completed)}, runtime: {(check_in_time - start_time):.6f}s")
  end_time = time.perf_counter()

  logging.info(f"Finish after {stack.counter} iterations in {end_time - start_time:.6f} seconds")
  logging.info(f"{len(stack.completed)} completions found")
  if len(stack.iso_sigs) > 0:
    logging.info("isomorphism signatures:")
    for sig in stack.iso_sigs:
      logging.info(sig)

def main():

  logging.basicConfig(
    level=logging.DEBUG,
    format='MP-SEARCH|%(levelname)s: %(message)s',
  )

  parser = argparse.ArgumentParser(description="CLI frontend for Mixed Platonic census")

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
  debug_on = args.debug_mode
  name = args.name

  p = Path(name)

  if not (p.exists() and p.is_dir()):
    logging.error(f"search environment '{name}' does not exist, use generate to create")
  
  log_file_path = p / 'log.txt'

  log_file_handler = logging.FileHandler(log_file_path)
  log_file_handler.setFormatter(logging.Formatter('MP-SEARCH|%(levelname)s: %(message)s'))
  log_file_handler.setLevel(logging.DEBUG)

  # Add to root logger
  logging.getLogger().addHandler(log_file_handler)  

  try:
    config = load_search_config(p)
  except FileExistsError:
    logging.error(f"config file for '{name}' does not exist")
      
  log_config(config)

  if debug_on:
    config['debug'] = True
  else:
    config['debug'] = False

  cusp = Cusp()
  cusp.load(config['cusp'])

  traversal = load_traversal(config['traversal'])
  num_tets = config['num_tets']
  num_octs = config['num_octs']
  name = config['name']
  
  embeddings = Embeddings()
  construction = Construction(cusp, embeddings)
  stack = Stack(traversal, construction, num_tets, num_octs)

  start_time = time.perf_counter()
  num_completed = 0
  while stack.done == False:
    completed = stack.next_()
    if completed:
      num_completed += 1
      write_completed_to_jsonl(p, stack.counter, completed)
      logging.info(f"Completion found at iteration {stack.counter}")
    if debug_on and stack.counter % DEBUG_REPORT_INTERVAL == 0:
      check_in_time = time.perf_counter()
      logging.debug(f"iteration: {stack.counter}, completions: {num_completed}, runtime: {(check_in_time - start_time):.6f}s")
  end_time = time.perf_counter()

  logging.info(f"Finish after {stack.counter} iterations in {end_time - start_time:.6f} seconds")
  logging.info(f"{len(stack.completed)} completions found")

if __name__ == '__main__':
  main()





