import pytest
import pprint

from mixed_platonic import (
    TRI,
    SQR,
    TET,
    OCT,
    add_finger,
    embed_octahedron,
    embed_tetrahedron,
    build_fingered_cusp,
    complete_tet_embedding_map,
    complete_oct_embedding_map,
    connect_fingers_pos,
    connect_fingers_neg,
    normalize_identification,
    infer_face_pairing,
    infer_embedding,
    identify,
    CuspPairing,
    Embedding,
    get_face_pairing,
    has_exposed_face_tet,
    has_exposed_face_oct,
)

pp = pprint.PrettyPrinter(indent=4, width=80)


def test_normalize_identification():
    a = normalize_identification((2, 1), (0, 2))
    assert a == ((1, 2), (2, 0))

    b = normalize_identification((1, 2), (0, 2))
    assert b == ((1, 2), (0, 2))


def test_identify_1():
    cusp = {
        (TRI, 0): {
            (1, 2): None,
            (2, 3): None,
            (1, 3): None,
        },
        (SQR, 0): {
            (1, 2): None,
            (2, 3): None,
            (3, 4): None,
            (1, 4): None,
        },
    }

    identify(cusp, (SQR, 0), (2, 3), (TRI, 0), (1, 3))
    assert cusp[(SQR, 0)][(2, 3)] == ((TRI, 0), (1, 3))
    assert cusp[(TRI, 0)][(1, 3)] == ((SQR, 0), (2, 3))


def test_identify_2():
    cusp = {
        (TRI, 0): {
            (1, 2): None,
            (2, 3): None,
            (1, 3): None,
        },
        (SQR, 0): {
            (1, 2): None,
            (2, 3): None,
            (3, 4): None,
            (1, 4): None,
        },
    }

    identify(cusp, (SQR, 0), (2, 3), (TRI, 0), (3, 1))
    assert cusp[(SQR, 0)][(2, 3)] == ((TRI, 0), (3, 1))
    assert cusp[(TRI, 0)][(1, 3)] == ((SQR, 0), (3, 2))


def test_add_finger():
    cusp = {}
    add_finger(cusp, 0)

    expected = {
        (0, 0): {
            (1, 3): ((1, 0), (2, 3)),
            (2, 3): ((0, 1), (2, 1)),
        },
        (0, 1): {
            (1, 2): ((0, 0), (3, 2)),
            (2, 3): ((1, 0), (1, 4)),
        },
        (1, 0): {
            (1, 4): ((0, 1), (2, 3)),
            (2, 3): ((0, 0), (1, 3)),
        },
    }

    assert cusp == expected


def test_connect_fingers_pos():
    cusp = {}
    add_finger(cusp, 0)
    add_finger(cusp, 1)

    connect_fingers_pos(cusp, 0, 1)

    expected = {
        (0, 0): {
            (1, 3): ((1, 0), (2, 3)),
            (2, 3): ((0, 1), (2, 1)),
        },
        (0, 1): {
            (1, 2): ((0, 0), (3, 2)),
            (1, 3): ((0, 2), (1, 2)),
            (2, 3): ((1, 0), (1, 4)),
        },
        (0, 2): {
            (1, 2): ((0, 1), (1, 3)),
            (1, 3): ((1, 1), (2, 3)),
            (2, 3): ((0, 3), (2, 1)),
        },
        (0, 3): {
            (1, 2): ((0, 2), (3, 2)),
            (2, 3): ((1, 1), (1, 4)),
        },
        (1, 0): {
            (1, 4): ((0, 1), (2, 3)),
            (2, 3): ((0, 0), (1, 3)),
            (3, 4): ((1, 1), (2, 1)),
        },
        (1, 1): {
            (1, 2): ((1, 0), (4, 3)),
            (1, 4): ((0, 3), (2, 3)),
            (2, 3): ((0, 2), (1, 3)),
        },
    }

    assert cusp == expected


def test_connect_fingers_neg():
    cusp = {}
    add_finger(cusp, 0)
    add_finger(cusp, 1)

    connect_fingers_neg(cusp, 0, 1)

    expected = {
        (0, 0): {
            (1, 3): ((1, 0), (2, 3)),
            (2, 3): ((0, 1), (2, 1)),
        },
        (0, 1): {
            (1, 2): ((0, 0), (3, 2)),
            (1, 3): ((1, 1), (2, 1)),
            (2, 3): ((1, 0), (1, 4)),
        },
        (0, 2): {
            (1, 2): ((1, 0), (3, 4)),
            (1, 3): ((1, 1), (2, 3)),
            (2, 3): ((0, 3), (2, 1)),
        },
        (0, 3): {
            (1, 2): ((0, 2), (3, 2)),
            (2, 3): ((1, 1), (1, 4)),
        },
        (1, 0): {
            (1, 4): ((0, 1), (2, 3)),
            (2, 3): ((0, 0), (1, 3)),
            (3, 4): ((0, 2), (1, 2)),
        },
        (1, 1): {
            (1, 2): ((0, 1), (3, 1)),
            (1, 4): ((0, 3), (2, 3)),
            (2, 3): ((0, 2), (1, 3)),
        },
    }

    assert cusp == expected


def test_build_fingered_cusp():
    finger_pattern = [1, 1, -1, -1]
    cusp = build_fingered_cusp(finger_pattern)

    expected = {
        (0, 0): {
            (1, 2): ((1, 3), (3, 4)),
            (1, 3): ((1, 0), (2, 3)),
            (2, 3): ((0, 1), (2, 1)),
        },
        (0, 1): {
            (1, 2): ((0, 0), (3, 2)),
            (1, 3): ((0, 2), (1, 2)),
            (2, 3): ((1, 0), (1, 4)),
        },
        (0, 2): {
            (1, 2): ((0, 1), (1, 3)),
            (1, 3): ((1, 1), (2, 3)),
            (2, 3): ((0, 3), (2, 1)),
        },
        (0, 3): {
            (1, 2): ((0, 2), (3, 2)),
            (1, 3): ((1, 2), (2, 1)),
            (2, 3): ((1, 1), (1, 4)),
        },
        (0, 4): {
            (1, 2): ((1, 1), (3, 4)),
            (1, 3): ((1, 2), (2, 3)),
            (2, 3): ((0, 5), (2, 1)),
        },
        (0, 5): {
            (1, 2): ((0, 4), (3, 2)),
            (1, 3): ((0, 6), (1, 2)),
            (2, 3): ((1, 2), (1, 4)),
        },
        (0, 6): {
            (1, 2): ((0, 5), (1, 3)),
            (1, 3): ((1, 3), (2, 3)),
            (2, 3): ((0, 7), (2, 1)),
        },
        (0, 7): {
            (1, 2): ((0, 6), (3, 2)),
            (1, 3): ((1, 0), (2, 1)),
            (2, 3): ((1, 3), (1, 4)),
        },
        (1, 0): {
            (1, 2): ((0, 7), (3, 1)),
            (1, 4): ((0, 1), (2, 3)),
            (2, 3): ((0, 0), (1, 3)),
            (3, 4): ((1, 1), (2, 1)),
        },
        (1, 1): {
            (1, 2): ((1, 0), (4, 3)),
            (1, 4): ((0, 3), (2, 3)),
            (2, 3): ((0, 2), (1, 3)),
            (3, 4): ((0, 4), (1, 2)),
        },
        (1, 2): {
            (1, 2): ((0, 3), (3, 1)),
            (1, 4): ((0, 5), (2, 3)),
            (2, 3): ((0, 4), (1, 3)),
            (3, 4): ((1, 3), (2, 1)),
        },
        (1, 3): {
            (1, 2): ((1, 2), (4, 3)),
            (1, 4): ((0, 7), (2, 3)),
            (2, 3): ((0, 6), (1, 3)),
            (3, 4): ((0, 0), (1, 2)),
        },
    }

    assert cusp == expected

    ## traverse forward along meridian

    current = (SQR, 0)
    current, _ = cusp[current][(2, 3)]
    assert current == (TRI, 0)
    current, _ = cusp[current][(2, 3)]
    assert current == (TRI, 1)
    current, _ = cusp[current][(2, 3)]
    assert current == (SQR, 0)

    ## traverse backwards along meridian

    current = (SQR, 0)
    current, _ = cusp[current][(1, 4)]
    assert current == (TRI, 1)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 0)
    current, _ = cusp[current][(1, 3)]
    assert current == (SQR, 0)

    ## traverse forward along meridian starting with square

    current = (SQR, 0)
    current, _ = cusp[current][(3, 4)]
    assert current == (SQR, 1)
    current, _ = cusp[current][(3, 4)]
    assert current == (TRI, 4)
    current, _ = cusp[current][(2, 3)]
    assert current == (TRI, 5)
    current, _ = cusp[current][(1, 3)]
    assert current == (TRI, 6)
    current, _ = cusp[current][(2, 3)]
    assert current == (TRI, 7)
    current, _ = cusp[current][(1, 3)]
    assert current == (SQR, 0)

    ## traverse backward along meridian starting with square

    current = (SQR, 0)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 7)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 6)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 5)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 4)
    current, _ = cusp[current][(1, 2)]
    assert current == (SQR, 1)
    current, _ = cusp[current][(1, 2)]
    assert current == (SQR, 0)

    ## traverse forward along meridian starting with square

    current = (TRI, 0)
    current, _ = cusp[current][(2, 3)]
    assert current == (TRI, 1)
    current, _ = cusp[current][(1, 3)]
    assert current == (TRI, 2)
    current, _ = cusp[current][(2, 3)]
    assert current == (TRI, 3)
    current, _ = cusp[current][(1, 3)]
    assert current == (SQR, 2)
    current, _ = cusp[current][(3, 4)]
    assert current == (SQR, 3)
    current, _ = cusp[current][(3, 4)]
    assert current == (TRI, 0)

    ## traverse backwards along meridian starting with square

    current = (TRI, 0)
    current, _ = cusp[current][(1, 2)]
    assert current == (SQR, 3)
    current, _ = cusp[current][(1, 2)]
    assert current == (SQR, 2)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 3)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 2)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 1)
    current, _ = cusp[current][(1, 2)]
    assert current == (TRI, 0)


def test_embed_octahedron():
    finger_pattern = [1, 1]
    cusp = build_fingered_cusp(finger_pattern)

    cellulation_embeddings = {
        (OCT, 0): {
            0: None,
            1: None,
            2: None,
            3: None,
            4: None,
            5: None,
        }
    }

    cusp_embeddings = {(SQR, 0): None}

    octahedron = (OCT, 0)
    square = (SQR, 0)
    embedding = (0, 1, 2, 3, 4, 5)

    embed_octahedron(
        cusp, cellulation_embeddings, cusp_embeddings, octahedron, square, embedding
    )

    assert cellulation_embeddings[(OCT, 0)][0] == ((SQR, 0), (0, 1, 2, 3, 4, 5))
    assert cusp_embeddings[(SQR, 0)] == ((OCT, 0), (0, 1, 2, 3, 4, 5))


def test_embed_tetrahedron():
    finger_pattern = [1, 1]
    cusp = build_fingered_cusp(finger_pattern)

    cellulation_embeddings = {
        (TET, 0): {
            0: None,
            1: None,
            2: None,
            3: None,
            4: None,
            5: None,
        }
    }

    cusp_embeddings = {(TRI, 0): None}

    tetrahedron = (TET, 0)
    triangle = (TRI, 0)
    embedding = (0, 1, 2, 3)

    embed_tetrahedron(
        cusp, cellulation_embeddings, cusp_embeddings, tetrahedron, triangle, embedding
    )

    assert cellulation_embeddings[(TET, 0)][0] == ((TRI, 0), (0, 1, 2, 3))
    assert cusp_embeddings[(TRI, 0)] == ((TET, 0), (0, 1, 2, 3))


def test_infer_face_pairing_1():
    finger_pattern = [1, 1]
    cusp = build_fingered_cusp(finger_pattern)

    cusp_embeddings = {
        (SQR, 0): ((OCT, 0), (0, 1, 2, 3, 4, 5)),
        (TRI, 0): ((TET, 0), (0, 1, 2, 3)),
    }

    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 0), (2, 3))

    assert pairing == ((OCT, 0), (0, 2, 3), (TRI, 0), (0, 1, 3))


def test_infer_face_pairing_2():
    finger_pattern = [1, -1]
    cusp = build_fingered_cusp(finger_pattern)

    cusp_embeddings = {
        (TRI, 1): ((TET, 0), (1, 3, 2, 0)),
        (SQR, 1): ((OCT, 0), (2, 0, 3, 5, 1, 4)),
    }

    pairing = infer_face_pairing(cusp, cusp_embeddings, (TRI, 1), (1, 3))

    assert pairing == ((TET, 0), (0, 1, 3), (OCT, 0), (0, 2, 3))


def test_infer_face_pairing_2():
    finger_pattern = [1, 1]
    cusp = build_fingered_cusp(finger_pattern)

    cusp_embeddings = {
        (SQR, 0): ((OCT, 0), (3, 2, 5, 4, 0, 1)),
        (SQR, 1): ((OCT, 1), (2, 0, 1, 5, 3, 4)),
    }

    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 0), (3, 4))
    assert pairing == ((OCT, 0), (0, 3, 4), (OCT, 1), (0, 2, 1))
    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 1), (1, 2))
    assert pairing == ((OCT, 1), (0, 1, 2), (OCT, 0), (0, 4, 3))
    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 1), (3, 4))
    assert pairing == ((OCT, 1), (2, 3, 5), (OCT, 0), (3, 2, 5))
    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 0), (1, 2))
    assert pairing == ((OCT, 0), (2, 3, 5), (OCT, 1), (3, 2, 5))


def test_infer_face_pairing_3():
    finger_pattern = [1, 1]
    cusp = build_fingered_cusp(finger_pattern)

    cusp_embeddings = {
        (SQR, 0): None,
        (SQR, 1): ((OCT, 1), (2, 0, 1, 5, 3, 4)),
    }

    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 0), (3, 4))
    assert pairing == None
    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 1), (1, 2))
    assert pairing == None
    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 1), (3, 4))
    assert pairing == None
    pairing = infer_face_pairing(cusp, cusp_embeddings, (SQR, 0), (1, 2))
    assert pairing == None


# def test_infer_embedding():
#   face_pairing = ((OCT,0),(0,2,3),(TET,0),(0,1,3))
#   edge_pairing = ((SQR,0),(2,3),(TRI,0),(1,3))
#   source_embedding = ((SQR,0),(OCT,0),(0,1,2,3,4,5))

#   target_embedding = infer_embedding(face_pairing, edge_pairing, source_embedding)

#   assert target_embedding == ((TET,0), (TRI,0), (0,1,2,3))


def test_complete_tet_embedding_map():
    embedding_map = complete_tet_embedding_map((1, 2, None, 3))
    assert embedding_map == (1, 2, 0, 3)
    embedding_map = complete_tet_embedding_map((None, 2, 1, 3))
    assert embedding_map == (0, 2, 1, 3)


def test_complete_oct_embedding_map():
    embedding_map = complete_oct_embedding_map((0, None, None, 3, 4, None))
    assert embedding_map == (0, 1, 2, 3, 4, 5)

    embedding_map = complete_oct_embedding_map((3, 2, 0, None, None, None))
    assert embedding_map == (3, 2, 0, 4, 5, 1)

    embedding_map = complete_oct_embedding_map((4, 0, None, None, 1, None))
    assert embedding_map == (4, 0, 3, 5, 1, 2)


def test_infer_embedding_1():
    cusp_edge_pairing = (((SQR, 0), (2, 3)), ((TRI, 0), (1, 3)))
    manifold_face_pairing = (((OCT, 0), (0, 1, 4)), ((TET, 0), (1, 2, 3)))
    embedding = ((OCT, 0), (SQR, 0), (1, 2, 0, 4, 5, 3))

    inferred_embedding = infer_embedding(
        cusp_edge_pairing, manifold_face_pairing, embedding
    )

    assert inferred_embedding == ((TET, 0), (TRI, 0), (2, 1, 0, 3))


def test_infer_embedding_2():
    cusp_edge_pairing = (((SQR, 0), (2, 3)), ((TRI, 0), (1, 3)))
    manifold_face_pairing = (((OCT, 0), (0, 1, 4)), ((TET, 0), (1, 2, 3)))
    embedding = ((OCT, 0), (SQR, 0), (1, 2, 0, 4, 5, 3))

    inferred_embedding = infer_embedding(
        cusp_edge_pairing, manifold_face_pairing, embedding
    )

    assert inferred_embedding == ((TET, 0), (TRI, 0), (2, 1, 0, 3))


def test_infer_embedding_3():
    cusp_edge_pairing = (((SQR, 0), (3, 4)), ((SQR, 1), (2, 1)))
    manifold_face_pairing = (((OCT, 0), (1, 2, 5)), ((OCT, 1), (4, 3, 5)))
    embedding = ((OCT, 0), (SQR, 0), (1, 4, 0, 2, 5, 3))

    inferred_embedding = infer_embedding(
        cusp_edge_pairing, manifold_face_pairing, embedding
    )

    assert inferred_embedding == ((OCT, 1), (SQR, 1), (4, 5, 3, 0, 1, 2))


def test_infer_embedding_3():
    cusp_edge_pairing = (((TRI, 0), (1, 3)), ((TRI, 1), (1, 2)))
    manifold_face_pairing = (((TET, 0), (0, 2, 3)), ((TET, 1), (0, 2, 1)))
    embedding = ((TET, 0), (TRI, 0), (3, 2, 1, 0))

    inferred_embedding = infer_embedding(
        cusp_edge_pairing, manifold_face_pairing, embedding
    )

    assert inferred_embedding == ((TET, 1), (TRI, 1), (1, 2, 0, 3))


# @pytest.fixture
# def triangulation():
#     return regina.Triangulation3()

# def test_platonic_octahedron(triangulation):
#     o = PlatonicOctahedron(triangulation)
#     tri = o.triangulation

#     assert tri.countVertices() == 7
#     assert tri.countEdges() == 18
#     assert tri.countTriangles() == 20
#     assert tri.countTetrahedra() == 8

#     vertex_degrees = [ v.degree() for v in tri.vertices() ]

#     assert vertex_degrees.count(8) == 1
#     assert vertex_degrees.count(4) == 6

#     assert tri.countBoundaryFaces(0) == 6
#     assert tri.countBoundaryFaces(1) == 12
#     assert tri.countBoundaryFaces(2) == 8

#     assert tri.isValid()
#     assert tri.isBall()

# def test_get_face_pairing():

#   embeddings = {
#     (SQR, 0): Embedding(
#       (OCT, 0),
#       (SQR, 0),
#       (4, 0, 1, 5, 3, 2),
#     ),
#     (TRI, 0): Embedding(
#       (TET, 0),
#       (TRI, 0),
#       (2, 1, 3, 0),
#     )
#   }

#   cusp_pairing = CuspPairing(
#     ((SQR, 0), (2,3)),
#     ((TRI, 0), (1,3)),
#   )


#   face_pairing = get_face_pairing(embeddings, cusp_pairing)

#   assert face_pairing.half_face_a == ((OCT,0), (4, 1, 5))
#   assert face_pairing.half_face_b == ((TET,0), (2, 1, 0))


def test_has_exposed_face_tet():

    assert has_exposed_face_tet((1, 3, 2, 0), (0, 2, 3)) == False
    assert has_exposed_face_tet((1, 3, 2, 0), (0, 1, 2)) == True
    assert has_exposed_face_tet((1, 3, 2, 0), (1, 2, 3)) == True


def test_has_exposed_face_oct():
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (0, 1, 2)) == True
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (1, 2, 5)) == True
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (2, 3, 5)) == True
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (0, 2, 3)) == True
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (3, 4, 5)) == False
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (1, 4, 5)) == False
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (0, 1, 4)) == False
    assert has_exposed_face_oct((2, 0, 1, 5, 3, 4), (0, 1, 3)) == False
