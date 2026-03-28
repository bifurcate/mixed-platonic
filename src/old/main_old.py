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

from itertools import combinations, product


def generate_iterates(num_tets, num_tris, num_octs, num_sqrs):
    tet_tri_iterates = [
        (0,) + x for x in combinations(range(1, num_tris), num_tets - 1)
    ]
    oct_sqr_iterates = [
        (0,) + x for x in combinations(range(1, num_sqrs), num_octs - 1)
    ]
    return product(tet_tri_iterates, oct_sqr_iterates)


def create_input_stack(tet_indices, oct_indices):
    input_stack = []

    for tet_idx, tri_idx in enumerate(tet_indices):
        input_stack.append(
            (TetTriEmbedding(Tet(tet_idx), Tri(tri_idx), (0, 1, 2, 3)), INIT)
        )

    for oct_idx, sqr_idx in enumerate(oct_indices):
        input_stack.append(
            (OctSqrEmbedding(Oct(oct_idx), Sqr(sqr_idx), (0, 1, 2, 3, 4, 5)), INIT)
        )

    return input_stack


def do_iterate(construction, tet_indices, oct_indices):
    input_stack = create_input_stack(tet_indices, oct_indices)
    construction.load_stack(input_stack)
    for i, _ in enumerate(construction):
        pass

    print(f"num iterations: {i}")
    print(f"num completed: {len(construction.completed_stacks)}")
    for c_stack in construction.completed_stacks:
        print(stack_to_str(c_stack))

    return construction.completed_stacks


if __name__ == "__main__":
    finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
    cusp_generator = FingerCuspGenerator(finger_pattern)
    cusp = cusp_generator.generate()
    traversal = list(cusp_generator.traversal())

    iterates = list(generate_iterates(6, 24, 2, 12))
    n = len(iterates)
    completed_stacks = []

    for i, indices_spec in enumerate(iterates):
        tet_tri_indices, oct_sqr_indices = indices_spec
        embeddings = Embeddings()
        construction = Construction(cusp, embeddings, traversal, num_tets=6, num_octs=2)
        print(f"iterate({i}/{n}): {tet_tri_indices}, {oct_sqr_indices}")
        completed_stacks_ = do_iterate(construction, tet_tri_indices, oct_sqr_indices)
        completed_stacks.extend(completed_stacks_)

    print(f"completed_stacks ({len(completed_stacks)})")
    for c_stack in construction.completed_stacks:
        print(stack_to_str(c_stack))


# if __name__ == '__main__':
#   finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
#   cusp_generator = FingerCuspGenerator(finger_pattern)
#   cusp = cusp_generator.generate()
#   traversal = list(cusp_generator.traversal())
#   embeddings = Embeddings()

#   # def tr_gen(num_fingers):
#   #   for i in range(num_fingers):
#   #     yield Sqr(i)
#   #     yield Tri(2*i)
#   #     yield Tri(2*i + 1)

#   # traversal = list(tr_gen(12))

#   construction = Construction(cusp, embeddings, traversal)

#   # input_stack = [
#   #   (OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5)), CHOICE),
#   #   (TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3)),       CHOICE),
#   #   (TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3)),       CHOICE),
#   #   (OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5)), CHOICE),
#   #   # (TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3)),       CHOICE),
#   #   # (TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0)),       CHOICE),
#   #   # (OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4)), CHOICE),
#   #   # (TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3)),       CHOICE),
#   #   # (TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3)),       CHOICE),
#   #   # (OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1)), CHOICE),
#   #   # (TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0)),       CHOICE),
#   # ]

#   input_stack = [
#     (OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5)), INIT),
#     (TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3)),       INIT),
#     (OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5)), INIT),
#     (TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(5), Tri(6), (1, 3, 2, 0)),       INIT),
#   ]


#   construction.load_stack(input_stack)

#   BAIL_OUT = 50000

#   print("# STACK TRACE")
#   print()

#   for i,_ in enumerate(construction):
#     print(construction.stack_to_str())
#     if i > BAIL_OUT:
#       break


#   print()
#   print("# COMPLETED STACKS")
#   print()

#   for c_stack in construction.completed_stacks:
#     print(stack_to_str(c_stack))

#   print()
#   print(f"num iterations: {i}")
#   print(f"num completed: {len(construction.completed_stacks)}")

# if __name__ == '__main__':
#   finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
#   cusp_generator = FingerCuspGenerator(finger_pattern)
#   cusp = cusp_generator.generate()
#   traversal = list(cusp_generator.traversal())
#   embeddings = Embeddings()

#   construction = Construction(cusp, embeddings, traversal, num_tets = 12, num_octs = 4)

#   # input_stack = [
#   #   (OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5)), CHOICE),
#   #   (TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3)),       CHOICE),
#   #   (TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3)),       CHOICE),
#   #   (OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5)), CHOICE),
#   #   # (TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3)),       CHOICE),
#   #   # (TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0)),       CHOICE),
#   #   # (OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4)), CHOICE),
#   #   # (TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3)),       CHOICE),
#   #   # (TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3)),       CHOICE),
#   #   # (OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1)), CHOICE),
#   #   # (TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0)),       CHOICE),
#   # ]

#   input_stack = [
#     (OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5)), INIT),
#     (TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3)),       INIT),
#     (OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5)), INIT),
#     (TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(5), Tri(6), (1, 3, 2, 0)),       INIT),
#     (OctSqrEmbedding(Oct(2), Sqr(4), (0, 1, 2, 3, 4, 5)), INIT),
#     (TetTriEmbedding(Tet(6), Tri(8), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(7), Tri(9), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(8), Tri(10), (0, 1, 2, 3)),       INIT),
#     (OctSqrEmbedding(Oct(3), Sqr(5), (0, 1, 2, 3, 4, 5)), INIT),
#     (TetTriEmbedding(Tet(9), Tri(12), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(10), Tri(13), (0, 1, 2, 3)),       INIT),
#     (TetTriEmbedding(Tet(11), Tri(14), (1, 3, 2, 0)),       INIT),
#   ]


#   construction.load_stack(input_stack)

#   BAIL_OUT = 50000

#   print("# STACK TRACE")
#   print()

#   for i,_ in enumerate(construction):
#     print(construction.stack_to_str())
#     if i > BAIL_OUT:
#       break


#   print()
#   print("# COMPLETED STACKS")
#   print()

#   for c_stack in construction.completed_stacks:
#     print(stack_to_str(c_stack))

#   print()
#   print(f"num iterations: {i}")
#   print(f"num completed: {len(construction.completed_stacks)}")
