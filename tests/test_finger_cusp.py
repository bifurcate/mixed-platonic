import pytest

from base import (
    Sqr,
    Tri,
    CuspHalfEdge,
    CuspEdgePairing,
)

from construction import Cusp

from finger_cusp import (
    FingerCuspConstructor,
    MultiFingerCuspConstructor,
)


def test_finger_cusp_constructor_add_finger():
    cusp = Cusp()
    finger_pattern = [1, 0]
    cusp_constructor = FingerCuspConstructor(cusp, finger_pattern)

    cusp_constructor.add_finger(0)

    cusp = cusp_constructor.cusp

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
    assert pairings.get((1, 2)) == None

    pairings = cusp.get_cell_pairings(Tri(1))

    assert pairings.get((1, 2)) == CuspEdgePairing(
        CuspHalfEdge(Tri(1), (1, 2)),
        CuspHalfEdge(Tri(0), (3, 2)),
    )
    assert pairings.get((2, 3)) == CuspEdgePairing(
        CuspHalfEdge(Tri(1), (2, 3)),
        CuspHalfEdge(Sqr(0), (1, 4)),
    )


def test_finger_cusp_constructor_generate():
    cusp = Cusp()
    finger_pattern = [1, 0]
    cusp_constructor = FingerCuspConstructor(cusp, finger_pattern)
    cusp_constructor.generate()


def test_multi_finger_cusp_constructor_generate():
    cusp = Cusp()
    multi_finger_pattern = [[1, 0], [1, 0]]
    cusp_constructor = MultiFingerCuspConstructor(cusp, multi_finger_pattern)
    cusp_constructor.generate()
