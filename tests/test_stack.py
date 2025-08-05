import pytest

from base import (
  Sqr,
  Tri,
  Oct,
  Tet,
  OctSqrEmbedding,
  TetTriEmbedding,
)

from construction import (
  FingerCuspGenerator,
  Embeddings,
  Construction,
)

from stack import (
  Stack,
  INIT,
  REGULAR,
  INDUCED,
)

from draw import draw_stack


# def test_stack():

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

#   stack.load(input_stack)

#   # breakpoint()

#   while stack.counter <= 70000:

#     # if stack.counter == 811:
#     #   breakpoint()
#     stack.next_()
#     # stack_lens.append((stack.counter, len(stack.stack)))
#     # draw_()
#   breakpoint()