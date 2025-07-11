from construction import (
  Construction,
  FingerCuspGenerator,
  Embeddings,
  Sqr,
  Tri,
  Oct,
  Tet,
  CHOICE,
  INDUCED,
  OctSqrEmbedding,
  TetTriEmbedding,
  stack_to_str,
)


if __name__ == '__main__':
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp_generator = FingerCuspGenerator(finger_pattern)
  cusp = cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  embeddings = Embeddings()

  # def tr_gen(num_fingers):
  #   for i in range(num_fingers):
  #     yield Sqr(i)
  #     yield Tri(2*i)
  #     yield Tri(2*i + 1)

  # traversal = list(tr_gen(12))

  construction = Construction(cusp, embeddings, traversal)

  input_stack = [
    (OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5)), CHOICE),
    (TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3)),       CHOICE),
    (TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3)),       CHOICE),
    (OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5)), CHOICE),
    (TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3)),       CHOICE),
    (TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0)),       CHOICE),
    (OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4)), CHOICE),
    (TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3)),       CHOICE),
    (TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3)),       CHOICE),
    (OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1)), CHOICE),
    (TetTriEmbedding(Tet(5), Tri(6), (0, 1, 2, 3)),       CHOICE),
    (TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0)),       CHOICE),
  ]
  # construction.load_stack(input_stack)

  print("# STACK TRACE")
  print()

  for i in range(10000):
    construction.next()
    print(construction.stack_to_str())

  print()
  print("# COMPLETED STACKS")
  print()

  for c_stack in construction.completed_stacks:
    print(stack_to_str(c_stack))

  