from construction import (
  Construction,
  FingerCuspGenerator,
  Embeddings,
  Sqr,
  Tri,
  Oct,
  Tet,
  INIT,
  CHOICE,
  INDUCED,
  OctSqrEmbedding,
  TetTriEmbedding,
  stack_to_str,
)

from draw import draw_stack

from itertools import combinations, product

def generate_iterates(num_tets, num_tris, num_octs, num_sqrs):
  tet_tri_iterates = [ (0,) + x for x in combinations(range(1, num_tris), num_tets - 1) ]
  oct_sqr_iterates = [ (0,) + x for x in combinations(range(1, num_sqrs), num_octs - 1) ]
  return product(tet_tri_iterates, oct_sqr_iterates)

def create_input_stack(tet_indices, oct_indices):
  input_stack = []

  for tet_idx, tri_idx in enumerate(tet_indices):
    input_stack.append((TetTriEmbedding(Tet(tet_idx), Tri(tri_idx), (0, 1, 2, 3)), INIT))

  for oct_idx, sqr_idx in enumerate(oct_indices):
    input_stack.append((OctSqrEmbedding(Oct(oct_idx), Sqr(sqr_idx), (0, 1, 2, 3, 4, 5)), INIT))

  return input_stack

# def do_iterate(construction, tet_indices, oct_indices):
#   input_stack = create_input_stack(tet_indices, oct_indices)
#   construction.load_stack(input_stack)
#   draw_stack
#   for i,_ in enumerate(construction):
#     pass

#   print(f"num iterations: {i}")
#   print(f"num completed: {len(construction.completed_stacks)}")
#   for c_stack in construction.completed_stacks:
#     print(stack_to_str(c_stack))

#   return construction.completed_stacks


if __name__ == '__main__':
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp_generator = FingerCuspGenerator(finger_pattern)
  cusp = cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  init_tet_indices = (
    0,1,2,4,5,6
  )
  init_oct_indices = (0,1)

  embeddings = Embeddings()
  construction = Construction(cusp, embeddings, traversal, num_tets = 6, num_octs = 2)


  input_stack = create_input_stack(init_tet_indices, init_oct_indices)
  construction.load_stack(input_stack)
  # draw_stack(finger_pattern, construction, "test.svg")


  for i,_ in enumerate(construction):
    # draw_stack(finger_pattern, construction, f"draw_test/{i}.svg")
    breakpoint()

    pass

  # print(f"num iterations: {i}")
  # print(f"num completed: {len(construction.completed_stacks)}")
  # for c_stack in construction.completed_stacks:
  #   print(stack_to_str(c_stack))

  # return construction.completed_stacks

