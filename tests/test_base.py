import pytest

from base import (
    SQR,
    TRI,
    Triangle,
    Square,
    Tri,
    Sqr,
    TET,
    OCT,
    Tetrahedron,
    Tet,
    Octahedron,
    Oct,
    CuspHalfEdge,
    ManifoldHalfFace,
    CuspEdgePairing,
    ManifoldFacePairing,
    TetTriEmbedding,
    OctSqrEmbedding,
    TET_TRI,
    OCT_SQR,
)


def test_triangle():
    t0 = Triangle(0)
    t1 = Triangle(1)

    assert repr(t0) == "Triangle(0)"
    assert str(t0) == "Triangle(0)"
    assert t0 != t1
    assert t0.cell_type == TRI
    assert t0.is_tri() == True
    assert t0.is_sqr() == False
    assert tuple(t0) == (TRI, 0)


def test_square():
    t0 = Square(0)
    t1 = Square(1)

    assert repr(t0) == "Square(0)"
    assert str(t0) == "Square(0)"
    assert t0 != t1
    assert t0.cell_type == SQR
    assert t0.is_tri() == False
    assert t0.is_sqr() == True
    assert tuple(t0) == (SQR, 0)


def test_tetrahedron():
    t0 = Tetrahedron(0)
    t1 = Tetrahedron(1)

    assert repr(t0) == "Tetrahedron(0)"
    assert str(t0) == "Tetrahedron(0)"
    assert t0 != t1
    assert t0.cell_type == TET
    assert t0.is_tet() == True
    assert t0.is_oct() == False
    assert tuple(t0) == (TET, 0)


def test_octahedron():
    t0 = Octahedron(0)
    t1 = Octahedron(1)

    assert repr(t0) == "Octahedron(0)"
    assert str(t0) == "Octahedron(0)"
    assert t0 != t1
    assert t0.cell_type == OCT
    assert t0.is_tet() == False
    assert t0.is_oct() == True
    assert tuple(t0) == (OCT, 0)


def test_cusp_half_edge():
    s0 = Square(0)
    e0 = (1, 2)
    h0 = CuspHalfEdge(s0, e0)

    s1 = Triangle(0)
    e1 = (0, 1)
    h1 = CuspHalfEdge(s1, e1)

    assert repr(h0) == "CuspHalfEdge(Square(0), (1, 2))"
    assert str(h0) == "CuspHalfEdge(Square(0), (1, 2))"
    assert h0 != h1
    assert tuple(h0) == ((SQR, 0), (1, 2))


def test_manifold_half_face():
    s0 = Octahedron(0)
    e0 = (0, 1, 2)
    h0 = ManifoldHalfFace(s0, e0)

    s1 = Tetrahedron(0)
    e1 = (0, 1)
    h1 = ManifoldHalfFace(s0, e0)

    assert repr(h0) == "ManifoldHalfFace(Octahedron(0), (0, 1, 2))"
    assert str(h0) == "ManifoldHalfFace(Octahedron(0), (0, 1, 2))"
    assert s0 != s1
    assert tuple(h0) == ((OCT, 0), (0, 1, 2))


def test_cusp_edge_pairing():
    ep = CuspEdgePairing(
        CuspHalfEdge(Square(0), (2, 3)), CuspHalfEdge(Triangle(0), (1, 3))
    )

    assert (
        repr(ep)
        == "CuspEdgePairing(CuspHalfEdge(Square(0), (2, 3)), CuspHalfEdge(Triangle(0), (1, 3)))"
    )
    assert tuple(ep) == (((1, 0), (2, 3)), ((0, 0), (1, 3)))


def test_cusp_edge_pairing_inv():
    ep = CuspEdgePairing(
        CuspHalfEdge(Square(0), (2, 3)), CuspHalfEdge(Triangle(0), (3, 1))
    )

    inv_ep = ep.inv

    assert inv_ep == CuspEdgePairing(
        CuspHalfEdge(Triangle(0), (1, 3)),
        CuspHalfEdge(Square(0), (3, 2)),
    )


def test_cusp_edge_pairing_mapping():
    ep = CuspEdgePairing(
        CuspHalfEdge(Square(0), (2, 3)), CuspHalfEdge(Triangle(0), (3, 1))
    )

    assert ep.map.get(0) == 0
    assert ep.map.get(1) == None
    assert ep.map.get(2) == 3
    assert ep.map.get(3) == 1

    assert ep.inv.map.get(0) == 0
    assert ep.inv.map.get(1) == 3
    assert ep.inv.map.get(2) == None
    assert ep.inv.map.get(3) == 2


def test_manifold_face_pairing():
    fp = ManifoldFacePairing(
        ManifoldHalfFace(Oct(0), (2, 3, 5)), ManifoldHalfFace(Tet(0), (2, 0, 3))
    )

    assert (
        repr(fp)
        == "ManifoldFacePairing(ManifoldHalfFace(Octahedron(0), (2, 3, 5)), ManifoldHalfFace(Tetrahedron(0), (2, 0, 3)))"
    )
    assert tuple(fp) == (((1, 0), (2, 3, 5)), ((0, 0), (2, 0, 3)))


def test_cusp_edge_pairing_inv():
    fp = ManifoldFacePairing(
        ManifoldHalfFace(Oct(0), (2, 3, 5)), ManifoldHalfFace(Tet(0), (2, 0, 3))
    )

    inv_fp = fp.inv

    assert inv_fp == ManifoldFacePairing(
        ManifoldHalfFace(Tet(0), (0, 2, 3)), ManifoldHalfFace(Oct(0), (3, 2, 5))
    )


def test_cusp_edge_pairing_mapping():
    fp = ManifoldFacePairing(
        ManifoldHalfFace(Oct(0), (2, 3, 5)), ManifoldHalfFace(Tet(0), (2, 0, 3))
    )

    assert fp.map.get(0) == None
    assert fp.map.get(1) == None
    assert fp.map.get(2) == 2
    assert fp.map.get(3) == 0
    assert fp.map.get(4) == None
    assert fp.map.get(5) == 3
    assert fp.map.get(6) == None

    assert fp.inv.map.get(0) == 3
    assert fp.inv.map.get(1) == None
    assert fp.inv.map.get(2) == 2
    assert fp.inv.map.get(3) == 5
    assert fp.inv.map.get(4) == None
    assert fp.inv.map.get(5) == None
    assert fp.inv.map.get(6) == None


def test_tet_tri_embedding():
    tte0 = TetTriEmbedding(
        Tet(0),
        Tri(0),
        (3, 2, 1, 0),
    )

    tte1 = TetTriEmbedding(
        Tet(1),
        Tri(3),
        (2, 1, 3, 0),
    )

    assert repr(tte0) == "TetTriEmbedding(Tetrahedron(0), Triangle(0), (3, 2, 1, 0))"
    assert str(tte0) == "TetTriEmbedding(Tetrahedron(0), Triangle(0), (3, 2, 1, 0))"
    assert tte0 != tte1
    assert tte0.embedding_type == TET_TRI
    assert tte0.is_tet_tri() == True
    assert tte0.is_oct_sqr() == False
    assert tuple(tte0) == (TET_TRI, (0, 0), (0, 0), (3, 2, 1, 0))

    assert tte0.map.get(0) == 3
    assert tte0.map.get(1) == 2
    assert tte0.map.get(2) == 1
    assert tte0.map.get(3) == 0
    assert tte0.map.get(4) == None

    assert tte0.inv_map.get(0) == 3
    assert tte0.inv_map.get(1) == 2
    assert tte0.inv_map.get(2) == 1
    assert tte0.inv_map.get(3) == 0
    assert tte0.inv_map.get(4) == None

    assert tte1.exposed((1, 2, 3)) == (1, 2)
    assert tte1.exposed((0, 2, 3)) == (2, 3)
    assert tte1.exposed((0, 1, 2)) == (1, 3)
    assert tte1.exposed((0, 1, 3)) == None


def test_tet_tri_embedding_complete():
    tte = TetTriEmbedding(
        Tet(1),
        Tri(3),
        (2, 1, None, 0),
    )
    assert tte == TetTriEmbedding(Tet(1), Tri(3), (2, 1, 3, 0))


def test_oct_sqr_embedding():
    ose0 = OctSqrEmbedding(
        Oct(0),
        Sqr(0),
        (5, 4, 3, 2, 1, 0),
    )

    ose1 = OctSqrEmbedding(
        Oct(1),
        Sqr(3),
        (4, 1, 5, 3, 0, 2),
    )

    assert repr(ose0) == "OctSqrEmbedding(Octahedron(0), Square(0), (5, 4, 3, 2, 1, 0))"
    assert str(ose0) == "OctSqrEmbedding(Octahedron(0), Square(0), (5, 4, 3, 2, 1, 0))"
    assert ose0 != ose1
    assert ose0.embedding_type == OCT_SQR
    assert ose0.is_tet_tri() == False
    assert ose0.is_oct_sqr() == True
    assert tuple(ose0) == (OCT_SQR, (1, 0), (1, 0), (5, 4, 3, 2, 1, 0))

    assert ose0.map.get(0) == 5
    assert ose0.map.get(1) == 4
    assert ose0.map.get(2) == 3
    assert ose0.map.get(3) == 2
    assert ose0.map.get(4) == 1
    assert ose0.map.get(5) == 0
    assert ose0.map.get(6) == None

    assert ose0.inv_map.get(0) == 5
    assert ose0.inv_map.get(1) == 4
    assert ose0.inv_map.get(2) == 3
    assert ose0.inv_map.get(3) == 2
    assert ose0.inv_map.get(4) == 1
    assert ose0.inv_map.get(5) == 0
    assert ose0.inv_map.get(6) == None

    assert ose1.exposed((1, 4, 5)) == (1, 2)
    assert ose1.exposed((3, 4, 5)) == (2, 3)
    assert ose1.exposed((0, 3, 4)) == (3, 4)
    assert ose1.exposed((0, 1, 4)) == (1, 4)
    assert ose1.exposed((1, 2, 5)) == None
    assert ose1.exposed((2, 3, 5)) == None
    assert ose1.exposed((0, 2, 3)) == None
    assert ose1.exposed((0, 1, 2)) == None


def test_tet_tri_embedding_indices():
    tte0 = TetTriEmbedding.from_indices(2, 1, 3, 1)

    assert tte0 == TetTriEmbedding(Tet(2), Tri(1), (3, 0, 2, 1))

    assert tte0.get_indices() == (3, 1)


def test_oct_sqr_embedding_indices():
    ose0 = OctSqrEmbedding.from_indices(2, 1, 3, 1)

    assert ose0 == OctSqrEmbedding(Oct(2), Sqr(1), (3, 0, 4, 5, 2, 1))

    assert ose0.get_indices() == (3, 1)


def test_tet_tri_embedding_get_indices():
    ose0 = TetTriEmbedding.from_indices(2, 1, 3, 1)

    assert ose0 == TetTriEmbedding(Tet(2), Tri(1), (3, 0, 2, 1))


def test_oct_sqr_embedding_complete():
    ose = OctSqrEmbedding(
        Oct(0),
        Sqr(0),
        (5, 4, 3, None, None, None),
    )

    assert ose == OctSqrEmbedding(
        Oct(0),
        Sqr(0),
        (5, 4, 3, None, None, None),
    )

    ose = OctSqrEmbedding(
        Oct(0),
        Sqr(0),
        (2, 0, None, None, 1, None),
    )

    assert ose == OctSqrEmbedding(
        Oct(0),
        Sqr(0),
        (2, 0, 3, 5, 1, 4),
    )
