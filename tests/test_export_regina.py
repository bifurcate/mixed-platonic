import pytest

from base import (
  Triangle,
  Square,
  Tri,
  Sqr,
  Tet,
  Oct,
  CuspHalfEdge,
  ManifoldHalfFace,
  CuspEdgePairing,
  ManifoldFacePairing,
  TetTriEmbedding,
  OctSqrEmbedding,
)

from construction import (
  INIT,
  CHOICE,
  INDUCED,
  Cusp,
  FingerCuspGenerator,
  Embeddings,
  get_manifold_face_pairing,
  get_embedding_tgt,
  get_manifold_half_face,
  Construction,
)

from export_regina import (
  to_regina_triangulation,
  reorder,
  prepend_missing,
  get_r_face_spec,
  TET_TRIANGULATION_MAP,
  OCT_TRIANGULATION_MAP,
)

def test_reorder():
  assert reorder(('a','b','c','d'), ('a', 'c', 'd', 'b'), ('W','X','Y','Z',)) == ('W', 'Y', 'Z', 'X')
  assert reorder(('a','b','c','d'), ('a', 'b', 'c', 'd'), ('W','X','Y','Z',)) == ('W', 'X', 'Y', 'Z')

def test_prepend_missing():
  assert prepend_missing((1,2,3,4), 5) == (0,1,2,3,4)
  assert prepend_missing((2,3,0), 4) == (1,2,3,0)
  with pytest.raises(ValueError) as exc_info:
    prepend_missing((1,2), 5)

def test_get_r_face_spec():
  assert get_r_face_spec(OCT_TRIANGULATION_MAP, (5, 4, 1)) == (2, 3, 1)
  assert get_r_face_spec(TET_TRIANGULATION_MAP, (3, 1, 2)) == (3, 1, 2)

def test_to_regina_triangulation():
  def create_input_stack(tet_indices, oct_indices):
    input_stack = []

    for tet_idx, tri_idx in enumerate(tet_indices):
      input_stack.append((TetTriEmbedding(Tet(tet_idx), Tri(tri_idx), (0, 1, 2, 3)), INIT))

    for oct_idx, sqr_idx in enumerate(oct_indices):
      input_stack.append((OctSqrEmbedding(Oct(oct_idx), Sqr(sqr_idx), (0, 1, 2, 3, 4, 5)), INIT))

    return input_stack
  
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp_generator = FingerCuspGenerator(finger_pattern)
  cusp = cusp_generator.generate()
  traversal = list(cusp_generator.traversal())
  init_tri_indices = (0,1,2,4,5,6)
  init_oct_indices = (0,1)

  embeddings = Embeddings()
  construction = Construction(cusp, embeddings, traversal, num_tets = 6, num_octs = 2)


  input_stack = create_input_stack(init_tri_indices, init_oct_indices)
  construction.load_stack(input_stack)
  for i,_ in enumerate(construction):
    pass

  completed_stacks = construction.completed_stacks
  mc = construction.mc
  reg_tri = to_regina_triangulation(mc, 6, 2)
  breakpoint()
