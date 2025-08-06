import argparse
import logging
import time

from base import (
  Sqr,
  Tri,
  Oct,
  Tet,
  Square,
  Triangle,
  Octahedron,
  Tetrahedron,
  OctSqrEmbedding,
  TetTriEmbedding,
)

from construction import (
  FingerCuspGenerator,
  Embeddings,
  Construction,
  Cusp,
)

from stack import (
  Stack,
  INIT,
  REGULAR,
  INDUCED,
)

from export_regina import (
  to_regina_triangulation
)

from draw import draw_stack

DEBUG_REPORT_INTERVAL = 1000

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

def initialize_stack(finger_pattern, num_tets, num_octs):
  cusp_generator = FingerCuspGenerator(finger_pattern)
  cusp = cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  embeddings = Embeddings()
  construction = Construction(cusp, embeddings)
  stack = Stack(traversal, construction, num_tets, num_octs)

  return stack

def dump_completed(id, input_stack, output_dir, finger_pattern, num_tets, num_octs):
  cusp = Cusp()
  cusp_generator = FingerCuspGenerator(cusp, finger_pattern)
  cusp = cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  embeddings = Embeddings()
  construction = Construction(cusp, embeddings)
  stack = Stack(traversal, construction, num_tets, num_octs)
  stack.load(input_stack)
  draw_stack(finger_pattern, construction, f"{output_dir}/{id:06}.png")
  with open(f"{output_dir}/id.txt") as f:
    f.write(stack.save())


def main():
  logging.basicConfig(
    level=logging.DEBUG,
    format='MP-SEARCH|%(levelname)s: %(message)s',
  )

  parser = argparse.ArgumentParser(description="CLI frontend for Mixed Platonic census")

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

  args = parser.parse_args()

  debug_on = args.debug_mode

  finger_pattern = parse_finger_pattern_arg(args.finger_pattern)
  num_tets, num_octs = determine_num_tets_octs(finger_pattern)

  logging.info("Beginning search for complete manifolds")
  logging.info(f"Finger Pattern: {args.finger_pattern}")
  logging.info(f"Number Tetrahedrons: {num_tets}")
  logging.info(f"Number Octahedrons: {num_octs}")

  stack = initialize_stack(finger_pattern, num_tets, num_octs)
  
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

  # if debug_on and args.output_dir:
  #   for i, output_stacks in enumerate(stack.completed):
  #     dump_completed(i, finger_pattern, args.output_dir, finger_pattern, num_tets, num_octs)


if __name__ == '__main__':
  main()

  # def draw_():
  #   draw_stack(finger_pattern, construction, f"test_stack_images/{stack.counter:06}.png")

  # stack.load(input_stack)

  # while stack.done == False:
  #     stack.next_()
  #     if (stack.counter % 1000) == 0:
  #       print((stack.counter, len(stack.completed)))
  #   # stack_lens.append((stack.counter, len(stack.stack)))
  #   # draw_()
  # breakpoint()






   

# if __name__ == '__main__':
#   num_tets = 6
#   num_octs = 2
#   finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
#   cusp_generator = FingerCuspGenerator(finger_pattern)
#   cusp = cusp_generator.generate()
#   traversal = list(cusp_generator.traversal())
#   embeddings = Embeddings()
#   construction = Construction(cusp, embeddings)
#   stack = Stack(traversal, construction, num_tets, num_octs)

#   def draw_():
#     draw_stack(finger_pattern, construction, f"test_stack_images/{stack.counter:06}.png")

#   input_stack = [
#     (INIT, OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))),
#     (INIT, TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))),
#     (INIT, TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))),
#     (INIT, OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))),
#   ]

#   input_stack = [(0, OctSqrEmbedding(Octahedron(0), Square(0), (0, 1, 2, 3, 4, 5))), (0, TetTriEmbedding(Tetrahedron(0), Triangle(0), (0, 1, 2, 3))), (0, TetTriEmbedding(Tetrahedron(1), Triangle(1), (0, 1, 2, 3))), (0, OctSqrEmbedding(Octahedron(1), Square(1), (0, 1, 2, 3, 4, 5))), (0, TetTriEmbedding(Tetrahedron(2), Triangle(2), (0, 1, 2, 3))), (1, TetTriEmbedding(Tetrahedron(0), Triangle(3), (1, 3, 2, 0))), (2, OctSqrEmbedding(Octahedron(0), Square(2), (2, 0, 3, 5, 1, 4))), (2, OctSqrEmbedding(Octahedron(1), Square(11), (4, 5, 3, 0, 1, 2))), (0, TetTriEmbedding(Tetrahedron(3), Triangle(4), (0, 1, 2, 3))), (0, TetTriEmbedding(Tetrahedron(4), Triangle(5), (0, 1, 2, 3))), (1, OctSqrEmbedding(Octahedron(1), Square(3), (3, 4, 5, 2, 0, 1))), (2, TetTriEmbedding(Tetrahedron(3), Triangle(7), (1, 3, 2, 0))), (2, OctSqrEmbedding(Octahedron(0), Square(4), (3, 2, 5, 4, 0, 1))), (2, TetTriEmbedding(Tetrahedron(2), Triangle(8), (3, 1, 0, 2))), (2, TetTriEmbedding(Tetrahedron(0), Triangle(9), (3, 2, 1, 0))), (2, OctSqrEmbedding(Octahedron(1), Square(5), (2, 0, 1, 5, 3, 4))), (2, TetTriEmbedding(Tetrahedron(1), Triangle(10), (1, 2, 0, 3))), (2, TetTriEmbedding(Tetrahedron(2), Triangle(11), (1, 2, 0, 3))), (2, OctSqrEmbedding(Octahedron(0), Square(6), (5, 3, 4, 1, 2, 0))), (2, TetTriEmbedding(Tetrahedron(3), Triangle(13), (3, 2, 1, 0))), (2, OctSqrEmbedding(Octahedron(1), Square(7), (5, 3, 4, 1, 2, 0))), (2, TetTriEmbedding(Tetrahedron(4), Triangle(14), (1, 2, 0, 3))), (2, TetTriEmbedding(Tetrahedron(1), Triangle(16), (3, 2, 1, 0))), (2, OctSqrEmbedding(Octahedron(0), Square(8), (4, 5, 1, 0, 3, 2))), (2, TetTriEmbedding(Tetrahedron(2), Triangle(17), (2, 0, 1, 3))), (2, OctSqrEmbedding(Octahedron(1), Square(9), (1, 2, 0, 4, 5, 3))), (2, TetTriEmbedding(Tetrahedron(0), Triangle(18), (2, 1, 3, 0))), (2, TetTriEmbedding(Tetrahedron(1), Triangle(19), (2, 0, 1, 3))), (2, OctSqrEmbedding(Octahedron(0), Square(10), (1, 4, 0, 2, 5, 3))), (2, TetTriEmbedding(Tetrahedron(4), Triangle(20), (3, 2, 1, 0))), (2, TetTriEmbedding(Tetrahedron(4), Triangle(23), (2, 0, 1, 3))), (2, TetTriEmbedding(Tetrahedron(3), Triangle(22), (2, 1, 3, 0))), (0, TetTriEmbedding(Tetrahedron(5), Triangle(6), (0, 1, 2, 3)))]

#   stack.load(input_stack)

#   while stack.counter <= 100000:
    
#     stack.next_()
    
#     # stack_lens.append((stack.counter, len(stack.stack)))
#     # draw_()
#   breakpoint()

# if __name__ == '__main__':
#   num_tets = 12
#   num_octs = 4
#   finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
#   cusp_generator = FingerCuspGenerator(finger_pattern)
#   cusp = cusp_generator.generate()
#   traversal = list(cusp_generator.traversal())
#   embeddings = Embeddings()
#   construction = Construction(cusp, embeddings)
#   stack = Stack(traversal, construction, num_tets, num_octs)

#   def draw_():
#     draw_stack(finger_pattern, construction, f"test_stack_images/{stack.counter:06}.png")

#   # stack.load(input_stack)

#   while stack.done == False:
#       stack.next_()
#       if (stack.counter % 1000) == 0:
#         print((stack.counter, len(stack.completed)))
#     # stack_lens.append((stack.counter, len(stack.stack)))
#     # draw_()
#   breakpoint()