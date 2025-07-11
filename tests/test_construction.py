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
  Cusp,
  FingerCuspGenerator,
  Embeddings,
  get_manifold_face_pairing,
  get_embedding_tgt,
  get_manifold_half_face,
  Construction,
)

def test_cusp():
  cusp = Cusp()
  
  cusp.add_cell(Square(0))
  cusp.add_cell(Triangle(0))

  cusp.pair(Square(0), (2, 3), Triangle(0), (1, 3))

  sqr0_pairings = cusp.get_cell_pairings(Square(0))

  assert sqr0_pairings.get((2,3)) == CuspEdgePairing(
    CuspHalfEdge(Square(0), (2, 3)),
    CuspHalfEdge(Triangle(0), (1, 3)),
  )

  assert sqr0_pairings.get((1,3)) == None

  tri0_pairings = cusp.get_cell_pairings(Triangle(0))

  assert tri0_pairings.get((1,3)) == CuspEdgePairing(
    CuspHalfEdge(Triangle(0), (1, 3)),
    CuspHalfEdge(Square(0), (2, 3)),
  )

  assert tri0_pairings.get((2,3)) == None

  assert cusp.get_cell_pairings(Sqr(1)) == None

def test_finger_cusp_generator_add_finger():
  finger_pattern = [1,-1]
  cusp_generator = FingerCuspGenerator(finger_pattern)

  cusp_generator.add_finger(0)

  cusp = cusp_generator.cusp

  pairings = cusp.get_cell_pairings(Sqr(0))

  assert pairings.get((2, 3)) == CuspEdgePairing(
    CuspHalfEdge(Sqr(0), (2, 3)), 
    CuspHalfEdge(Tri(0), (1, 3)),
  )
  assert pairings.get((1, 4)) == CuspEdgePairing(
    CuspHalfEdge(Sqr(0), (1, 4)),
    CuspHalfEdge(Tri(1), (2, 3)),
  )
  assert pairings.get((1, 2)) == None
  assert pairings.get((3, 4)) == None

  pairings = cusp.get_cell_pairings(Tri(0))

  assert pairings.get((1, 3)) == CuspEdgePairing(
    CuspHalfEdge(Tri(0), (1, 3)), 
    CuspHalfEdge(Sqr(0), (2, 3)),
  )
  assert pairings.get((2, 3)) == CuspEdgePairing(
    CuspHalfEdge(Tri(0), (2, 3)),
    CuspHalfEdge(Tri(1), (2, 1)),
  )
  assert pairings.get((1,2)) == None

  pairings = cusp.get_cell_pairings(Tri(1))

  assert pairings.get((1,2)) == CuspEdgePairing(
    CuspHalfEdge(Tri(1), (1, 2)), 
    CuspHalfEdge(Tri(0), (3, 2)),
  )
  assert pairings.get((2,3)) == CuspEdgePairing(
    CuspHalfEdge(Tri(1), (2, 3)), 
    CuspHalfEdge(Sqr(0), (1, 4)),
  )

def test_finger_cusp_generator_generate():
  finger_pattern = [1,-1]
  cusp_generator = FingerCuspGenerator(finger_pattern)

  cusp_generator.generate()

def test_embeddings():
  embeddings = Embeddings()
  
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(2), (1, 3, 2, 0))
  )
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(2), Sqr(3), (4, 1, 5, 3, 0, 2))
  )

  assert embeddings.get_embedding_by_cusp_cell(Tri(1)) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(0)) == None 

  tet1_embeddings = embeddings.get_embeddings_by_manifold_cell(Tet(1))

  assert tet1_embeddings.get(Tri(0)) == None
  assert tet1_embeddings.get(Tri(1)) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  assert tet1_embeddings.get(Tri(2)) == TetTriEmbedding(Tet(1), Tri(2), (1, 3, 2, 0))

  tet1_embeddings_by_vert = embeddings.get_embeddings_by_verts(Tet(1))
  assert tet1_embeddings_by_vert.get(0) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  assert tet1_embeddings_by_vert.get(1) == TetTriEmbedding(Tet(1), Tri(2), (1, 3, 2, 0))
  assert tet1_embeddings_by_vert.get(2) == None
  
  embeddings.remove_embedding(TetTriEmbedding(Tet(1), Tri(2), (1, 3, 2, 0)))

  assert embeddings.get_embedding_by_cusp_cell(Tri(2)) == None
  
  tet1_embeddings = embeddings.get_embeddings_by_manifold_cell(Tet(1))
  
  assert tet1_embeddings.get(Tri(1)) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  assert tet1_embeddings.get(Tri(2)) == None

  tet1_embeddings_by_vert = embeddings.get_embeddings_by_verts(Tet(1))
  assert tet1_embeddings_by_vert.get(0) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  assert tet1_embeddings_by_vert.get(1) == None
  assert tet1_embeddings_by_vert.get(2) == None

  embeddings.remove_embedding(TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3)))

  tet1_embeddings_by_vert = embeddings.get_embeddings_by_verts(Tet(1))
  assert tet1_embeddings_by_vert == None




def test_get_manifold_half_face():
  embedding = OctSqrEmbedding(
    Oct(0),
    Sqr(0),
    (1, 5, 2, 0, 4, 3),
  )

  cusp_half_edge = CuspHalfEdge(
    Sqr(0),
    (1, 2),
  )

  manifold_half_face = get_manifold_half_face(embedding, cusp_half_edge)
  
  assert manifold_half_face == ManifoldHalfFace(
    Oct(0),
    (1, 2, 5)
  )

  cusp_half_edge = CuspHalfEdge(
    Sqr(0),
    (2, 3),
  )

  manifold_half_face = get_manifold_half_face(embedding, cusp_half_edge)
  
  assert manifold_half_face == ManifoldHalfFace(
    Oct(0),
    (0, 1, 2)
  )

  cusp_half_edge = CuspHalfEdge(
    Sqr(1),
    (2, 3),
  )

  with pytest.raises(ValueError):
    get_manifold_half_face(embedding, cusp_half_edge)

def test_get_embedding_tgt():

  # example from boyd #16

  manifold_face_pairing = ManifoldFacePairing(
    ManifoldHalfFace(Oct(1), (0, 2, 3)),
    ManifoldHalfFace(Tet(2), (0, 1, 3)),
  )

  cusp_edge_pairing = CuspEdgePairing(
    CuspHalfEdge(Sqr(3), (3, 4)),
    CuspHalfEdge(Tri(8), (1, 2)),
  )

  embedding_src = OctSqrEmbedding(
    Oct(1),
    Sqr(3),
    (3, 4, 5, 2, 0, 1)
  )

  embedding_tgt = get_embedding_tgt(manifold_face_pairing, cusp_edge_pairing, embedding_src)

  assert embedding_tgt == TetTriEmbedding(
    Tet(2),
    Triangle(8),
    (3, 1, 0, 2)
  )

  # example from boyd #18

  manifold_face_pairing = ManifoldFacePairing(
    ManifoldHalfFace(Oct(0), (0, 3, 4)),
    ManifoldHalfFace(Oct(1), (0, 2, 1)),
  )

  cusp_edge_pairing = CuspEdgePairing(
    CuspHalfEdge(Sqr(4), (3, 4)),
    CuspHalfEdge(Sqr(5), (2, 1)),
  )

  embedding_src = OctSqrEmbedding(
    Oct(0),
    Sqr(4),
    (3, 2, 5, 4, 0, 1),
  )

  embedding_tgt = get_embedding_tgt(manifold_face_pairing, cusp_edge_pairing, embedding_src)

  assert embedding_tgt == OctSqrEmbedding(
    Oct(1),
    Sqr(5),
    (2, 0, 1, 5, 3, 4),
  )

  # example from boyd #19

  manifold_face_pairing = ManifoldFacePairing(
    ManifoldHalfFace(Tet(0), (0, 2, 3)),
    ManifoldHalfFace(Tet(1), (0, 2, 1)),
  )

  cusp_edge_pairing = CuspEdgePairing(
    CuspHalfEdge(Tri(9), (1, 3)),
    CuspHalfEdge(Tri(10), (1, 2)),
  )

  embedding_src = TetTriEmbedding(
    Tet(0),
    Tri(9),
    (3, 2, 1, 0),
  )

  embedding_tgt = get_embedding_tgt(manifold_face_pairing, cusp_edge_pairing, embedding_src)

  assert embedding_tgt == TetTriEmbedding(
    Tet(1),
    Tri(10),
    (1, 2, 0, 3),
  )

def test_get_manifold_face_pairing():

  # example from boyd 6-8

  embedding_src = OctSqrEmbedding(
    Oct(0),
    Sqr(3),
    (2, 0, 3, 5, 1, 4),
  )
  embedding_tgt = TetTriEmbedding(
    Tet(3),
    Tri(4),
    (0, 1, 2, 3)
  )

  cusp_pairing = CuspEdgePairing(
    CuspHalfEdge(Sqr(3), (2, 3)),
    CuspHalfEdge(Tri(4), (1, 3)),
  )

  mfp = get_manifold_face_pairing(embedding_src, embedding_tgt, cusp_pairing)

  assert mfp == ManifoldFacePairing(
    ManifoldHalfFace(Oct(0), (2, 3, 5)),
    ManifoldHalfFace(Tet(3), (0, 1, 3)),
  )

def test_construction_find_face_pairing():

  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()
  embeddings = Embeddings()

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
  )

  construction = Construction(cusp, embeddings)

  fp = construction.find_face_pairing(
    ManifoldHalfFace(Oct(0), (0, 2, 3))
  )

  assert fp == ManifoldFacePairing(
    ManifoldHalfFace(Oct(0), (0, 2, 3)),
    ManifoldHalfFace(Tet(0), (0, 1, 3)),
  )

  fp = construction.find_face_pairing(
    ManifoldHalfFace(Tet(2), (0, 1, 3))
  )

  assert fp == ManifoldFacePairing(
    ManifoldHalfFace(Tet(2), (0, 1, 3)),
    ManifoldHalfFace(Oct(1), (0, 2, 3)),
  )

  fp = construction.find_face_pairing(
    ManifoldHalfFace(Tet(1), (0, 2, 3))
  )

  assert fp == ManifoldFacePairing(
    ManifoldHalfFace(Tet(1), (0, 2, 3)),
    ManifoldHalfFace(Oct(0), (0, 1, 4)),
  )

def test_construction_get_induced_embedding_1():

  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()

  embeddings = Embeddings()

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
  )

  construction = Construction(cusp, embeddings)

  et = construction.get_induced_embedding_from_src(CuspHalfEdge(Tri(3), (1,3)))
  
  assert et == OctSqrEmbedding(
    Oct(0),
    Sqr(2),
    (2, 0, 3, 5, 1, 4),
  )

  et = construction.get_induced_embedding_from_tgt(CuspHalfEdge(Sqr(2), (1,2)))
  
  assert et == OctSqrEmbedding(
    Oct(0),
    Sqr(2),
    (2, 0, 3, 5, 1, 4),
  )

  pe = construction.get_induced_embeddings_for_cell(Sqr(2))

  assert pe[(1,2)] == OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4))


def test_get_induced_embedding_2():

  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()

  embeddings = Embeddings()

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
  )
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3))
  )

  construction = Construction(cusp, embeddings)

  et = construction.get_induced_embedding_from_src(CuspHalfEdge(Sqr(0), (1,2)))
  assert et == TetTriEmbedding(
    Tet(4),
    Tri(23),
    (2, 0, 1, 3),
  )

  et = construction.get_induced_embedding_from_tgt(CuspHalfEdge(Tri(23), (1,3)))
  assert et == TetTriEmbedding(
    Tet(4),
    Tri(23),
    (2, 0, 1, 3),
  )


def test_get_induced_embedding_2():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()

  embeddings = Embeddings()

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(2), (1, 2, 0, 3))
  )

  construction = Construction(cusp, embeddings)

  with pytest.raises(ValueError):
    et = construction.get_induced_embedding_from_tgt(CuspHalfEdge(Tri(3), (1,2)))

def test_get_induced_embedding_3():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()

  embeddings = Embeddings()

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(2), (1, 2, 0, 3))
  )

def test_complete_boyd():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()

  embeddings = Embeddings()

  # finger 0 embeddings
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )

  # finger 1 embeddings
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
  )

  # finger 2 embeddings

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3))
  )

  # finger 3 embeddings

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(5), Tri(6), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0))
  )

  boyd_to_f3 = Construction(cusp, embeddings)

  def cell_iterator(m, n):
    for finger_idx in range(m, n): 
      yield(Sqr(finger_idx))
      yield(Tri(2 * finger_idx))
      yield(Tri(2 * finger_idx + 1))

  for c in cell_iterator(4, 12):
    induced_embeddings = boyd_to_f3.get_induced_embeddings_for_cell(c)
    first_embedding = next(iter(induced_embeddings.values()))
    embeddings.add_embedding(first_embedding)

  

  assert embeddings.get_embedding_by_cusp_cell(Sqr(0)) == OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  assert boyd_to_f3.get_induced_embedding_for_cell(Sqr(0)) == OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  assert embeddings.get_embedding_by_cusp_cell(Tri(0)) == TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(1)) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(1)) == OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
  assert embeddings.get_embedding_by_cusp_cell(Tri(2)) == TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(3)) == TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(2)) == OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4))
  assert embeddings.get_embedding_by_cusp_cell(Tri(4)) == TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(5)) == TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(3)) == OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1))
  assert embeddings.get_embedding_by_cusp_cell(Tri(6)) == TetTriEmbedding(Tet(5), Tri(6), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(7)) == TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(4)) == OctSqrEmbedding(Oct(0), Sqr(4), (3, 2, 5, 4, 0, 1))
  assert embeddings.get_embedding_by_cusp_cell(Tri(8)) == TetTriEmbedding(Tet(2), Tri(8), (3, 1, 0, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(9)) == TetTriEmbedding(Tet(0), Tri(9), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(5)) == OctSqrEmbedding(Oct(1), Sqr(5), (2, 0, 1, 5, 3, 4))
  assert embeddings.get_embedding_by_cusp_cell(Tri(10)) == TetTriEmbedding(Tet(1), Tri(10), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(11)) == TetTriEmbedding(Tet(2), Tri(11), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(6)) == OctSqrEmbedding(Oct(0), Sqr(6), (5, 3, 4, 1, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(12)) == TetTriEmbedding(Tet(5), Tri(12), (3, 1, 0, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(13)) == TetTriEmbedding(Tet(3), Tri(13), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(7)) == OctSqrEmbedding(Oct(1), Sqr(7), (5, 3, 4, 1, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(14)) == TetTriEmbedding(Tet(4), Tri(14), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(15)) == TetTriEmbedding(Tet(5), Tri(15), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(8)) == OctSqrEmbedding(Oct(0), Sqr(8), (4, 5, 1, 0, 3, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(16)) == TetTriEmbedding(Tet(1), Tri(16), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(17)) == TetTriEmbedding(Tet(2), Tri(17), (2, 0, 1, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(9)) == OctSqrEmbedding(Oct(1), Sqr(9), (1, 2, 0, 4, 5, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(18)) == TetTriEmbedding(Tet(0), Tri(18), (2, 1, 3, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(19)) == TetTriEmbedding(Tet(1), Tri(19), (2, 0, 1, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(10)) == OctSqrEmbedding(Oct(0), Sqr(10), (1, 4, 0, 2, 5, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(20)) == TetTriEmbedding(Tet(4), Tri(20), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(21)) == TetTriEmbedding(Tet(5), Tri(21), (2, 0, 1, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(11)) == OctSqrEmbedding(Oct(1), Sqr(11), (4, 5, 3, 0, 1, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(22)) == TetTriEmbedding(Tet(3), Tri(22), (2, 1, 3, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(23)) == TetTriEmbedding(Tet(4), Tri(23), (2, 0, 1, 3))
  assert boyd_to_f3.get_induced_embedding_for_cell(Tri(23)) == TetTriEmbedding(Tet(4), Tri(23), (2, 0, 1, 3))


def test_empty_boyd():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()

  def tr_gen(num_fingers):
    for i in range(num_fingers):
      yield Sqr(i)
      yield Tri(2*i)
      yield Tri(2*i + 1)

  traversal = list(tr_gen(12))
  
  embeddings = Embeddings()
  
  boyd_empty = Construction(cusp, embeddings, traversal)

  assert embeddings.get_embedding_by_cusp_cell(Sqr(0)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(0)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(1)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(1)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(2)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(3)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(2)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(4)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(5)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(3)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(6)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(7)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(4)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(8)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(9)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(5)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(10)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(11)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(6 )) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(12)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(13)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(7 )) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(14)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(15)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(8 )) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(16)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(17)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(9 )) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(18)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(19)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(10)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(20)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(21)) == None
  assert embeddings.get_embedding_by_cusp_cell(Sqr(11)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(22)) == None
  assert embeddings.get_embedding_by_cusp_cell(Tri(23)) == None

  assert boyd_empty.get_least_available_cusp_cell_idx() == 0
  assert embeddings.is_vert_embedded(Oct(1), 1) == False

def test_construction_get_embedding_by_cusp_cell_1():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()

  embeddings = Embeddings()

    # finger 0 embeddings
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )

  # finger 1 embeddings
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(2), (1, 2, 0, 3))
  )

  construction = Construction(cusp, embeddings)

  with pytest.raises(ValueError) as exc_info:
    construction.get_induced_embedding_for_cell(Tri(3))

  assert str(exc_info.value) == 'cusp shape incompatibility'

  with pytest.raises(ValueError) as exc_info:
    construction.get_induced_embedding_for_cell(Sqr(11))

  assert str(exc_info.value) == 'cusp shape incompatibility'

def test_construction_induce_1():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()
  
  def tr_gen(num_fingers):
    for i in range(num_fingers):
      yield Sqr(i)
      yield Tri(2*i)
      yield Tri(2*i + 1)

  traversal = list(tr_gen(12))
  
  embeddings = Embeddings()
  
  boyd_to_f3 = Construction(cusp, embeddings, traversal)



  # finger 0 embeddings
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )

  # finger 1 embeddings
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
  )

  # finger 2 embeddings

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3))
  )

  # finger 3 embeddings

  embeddings.add_embedding(
    OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(5), Tri(6), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0))
  )

  induced_embedding = boyd_to_f3.induce_one()
  while induced_embedding is not None:
    induced_embedding = boyd_to_f3.induce_one()
  
  assert boyd_to_f3.is_complete()

  assert embeddings.get_embedding_by_cusp_cell(Tri(0)) == TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(1)) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(1)) == OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
  assert embeddings.get_embedding_by_cusp_cell(Tri(2)) == TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(3)) == TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(2)) == OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4))
  assert embeddings.get_embedding_by_cusp_cell(Tri(4)) == TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(5)) == TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(3)) == OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1))
  assert embeddings.get_embedding_by_cusp_cell(Tri(6)) == TetTriEmbedding(Tet(5), Tri(6), (0, 1, 2, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(7)) == TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(4)) == OctSqrEmbedding(Oct(0), Sqr(4), (3, 2, 5, 4, 0, 1))
  assert embeddings.get_embedding_by_cusp_cell(Tri(8)) == TetTriEmbedding(Tet(2), Tri(8), (3, 1, 0, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(9)) == TetTriEmbedding(Tet(0), Tri(9), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(5)) == OctSqrEmbedding(Oct(1), Sqr(5), (2, 0, 1, 5, 3, 4))
  assert embeddings.get_embedding_by_cusp_cell(Tri(10)) == TetTriEmbedding(Tet(1), Tri(10), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(11)) == TetTriEmbedding(Tet(2), Tri(11), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(6)) == OctSqrEmbedding(Oct(0), Sqr(6), (5, 3, 4, 1, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(12)) == TetTriEmbedding(Tet(5), Tri(12), (3, 1, 0, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(13)) == TetTriEmbedding(Tet(3), Tri(13), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(7)) == OctSqrEmbedding(Oct(1), Sqr(7), (5, 3, 4, 1, 2, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(14)) == TetTriEmbedding(Tet(4), Tri(14), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(15)) == TetTriEmbedding(Tet(5), Tri(15), (1, 2, 0, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(8)) == OctSqrEmbedding(Oct(0), Sqr(8), (4, 5, 1, 0, 3, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(16)) == TetTriEmbedding(Tet(1), Tri(16), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(17)) == TetTriEmbedding(Tet(2), Tri(17), (2, 0, 1, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(9)) == OctSqrEmbedding(Oct(1), Sqr(9), (1, 2, 0, 4, 5, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(18)) == TetTriEmbedding(Tet(0), Tri(18), (2, 1, 3, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(19)) == TetTriEmbedding(Tet(1), Tri(19), (2, 0, 1, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(10)) == OctSqrEmbedding(Oct(0), Sqr(10), (1, 4, 0, 2, 5, 3))
  assert embeddings.get_embedding_by_cusp_cell(Tri(20)) == TetTriEmbedding(Tet(4), Tri(20), (3, 2, 1, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(21)) == TetTriEmbedding(Tet(5), Tri(21), (2, 0, 1, 3))
  assert embeddings.get_embedding_by_cusp_cell(Sqr(11)) == OctSqrEmbedding(Oct(1), Sqr(11), (4, 5, 3, 0, 1, 2))
  assert embeddings.get_embedding_by_cusp_cell(Tri(22)) == TetTriEmbedding(Tet(3), Tri(22), (2, 1, 3, 0))
  assert embeddings.get_embedding_by_cusp_cell(Tri(23)) == TetTriEmbedding(Tet(4), Tri(23), (2, 0, 1, 3))

  assert embeddings.is_vert_embedded(Oct(1), 1) == True

def test_construction_get_next_embedding_1():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()
  
  def tr_gen(num_fingers):
    for i in range(num_fingers):
      yield Sqr(i)
      yield Tri(2*i)
      yield Tri(2*i + 1)

  traversal = list(tr_gen(12))
  
  embeddings = Embeddings()
  
  boyd = Construction(cusp, embeddings, traversal)

    # finger 0 embeddings
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )

  assert boyd.get_next_embedding(Sqr(0)) == OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 4, 3, 2, 5))
  assert boyd.get_next_embedding(Tri(0)) == TetTriEmbedding(Tet(0), Tri(0), (0, 1, 3, 2))

def test_construction_get_next_embedding_2():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()
  
  def tr_gen(num_fingers):
    for i in range(num_fingers):
      yield Sqr(i)
      yield Tri(2*i)
      yield Tri(2*i + 1)

  traversal = list(tr_gen(12))
  
  embeddings = Embeddings()
  
  boyd = Construction(cusp, embeddings, traversal)

  # finger 0 embeddings
  embeddings.add_embedding(
    OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
  )
  embeddings.add_embedding(
    TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
  )

  assert boyd.get_next_embedding(Sqr(1)) == OctSqrEmbedding(Oct(0), Sqr(1), (1, 0, 2, 5, 4, 3))
  assert boyd.get_next_embedding(Tri(1)) == TetTriEmbedding(Tet(1), Tri(1), (0, 1, 3, 2))

def test_construction_next():
  finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  cusp = FingerCuspGenerator(finger_pattern).generate()
  embeddings = Embeddings()

  def tr_gen(num_fingers):
    for i in range(num_fingers):
      yield Sqr(i)
      yield Tri(2*i)
      yield Tri(2*i + 1)

  traversal = list(tr_gen(12))

  construction = Construction(cusp, embeddings, traversal)

  breakpoint()
  construction.next()
  construction.next()
  construction.next()
  construction.next()
  construction.next()
  construction.next()
  construction.next()
  construction.next()
  construction.next()
  construction.next()