import pytest

from base import (
    Sqr,
    Tri,
    CuspHalfEdge,
    CuspEdgePairing,
    TRI,
    SQR,
    TRI_EDGES,
    SQR_EDGES,
)

from construction import Cusp

from finger_cusp import (
    FingerCuspConstructor,
    MultiFingerCuspConstructor,
)


def _edges_for_cell(cell):
    """Return the list of edge specs for a cusp cell."""
    if cell.cell_type == TRI:
        return TRI_EDGES
    elif cell.cell_type == SQR:
        return SQR_EDGES


def _all_edges_paired(cusp):
    """Check that every edge of every cell in the cusp has a pairing."""
    for cell, pairings in cusp.X.items():
        for edge in _edges_for_cell(cell):
            if edge not in pairings:
                return False
    return True


def _euler_characteristic(cusp):
    """Compute the Euler characteristic (V - E + F) of the cusp tiling."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for cell in cusp.X:
        if cell.cell_type == TRI:
            for v in (1, 2, 3):
                parent[(cell, v)] = (cell, v)
        elif cell.cell_type == SQR:
            for v in (1, 2, 3, 4):
                parent[(cell, v)] = (cell, v)

    for cp in cusp.pairs:
        src = cp.half_edge_src
        tgt = cp.half_edge_tgt
        union((src.cusp_cell, src.edge_spec[0]), (tgt.cusp_cell, tgt.edge_spec[0]))
        union((src.cusp_cell, src.edge_spec[1]), (tgt.cusp_cell, tgt.edge_spec[1]))

    V = len(set(find(x) for x in parent))
    E = len(cusp.pairs)
    F = len(cusp.X)
    return V - E + F


_finger_patterns = [
    [1, 0],
    [1, 1],
    [0, 0],
    [1, 0, 1],
    [1, 1, 0],
    [1, 0, 1, 0],
    [1, 1, 0, 0],
    [1, 1, 1, 0],
    [1, 0, 1, 0, 1, 0],
    [1, 1, 1, 0, 0, 0],
    [1, 1, 0, 1, 0, 0],
    [1, 1, 0, 0, 1, 0, 0, 0],
]


@pytest.mark.parametrize("pattern", _finger_patterns, ids=[str(p) for p in _finger_patterns])
def test_all_edges_paired(pattern):
    cusp = Cusp()
    FingerCuspConstructor(cusp, pattern).generate()
    assert _all_edges_paired(cusp), f"Pattern {pattern} has unpaired edges"


@pytest.mark.parametrize("pattern", _finger_patterns, ids=[str(p) for p in _finger_patterns])
def test_torus_topology(pattern):
    cusp = Cusp()
    FingerCuspConstructor(cusp, pattern).generate()
    chi = _euler_characteristic(cusp)
    assert chi == 0, f"Pattern {pattern} has Euler characteristic {chi}, expected 0 (torus)"


_multi_finger_patterns = [
    [[1, 0], [1, 0]],
    [[1, 1], [0, 0]],
    [[1, 0, 1], [0, 1, 0]],
    [[1, 0], [1, 0], [1, 0]],
]


@pytest.mark.parametrize(
    "pattern", _multi_finger_patterns, ids=[str(p) for p in _multi_finger_patterns]
)
def test_multi_finger_all_edges_paired(pattern):
    cusp = Cusp()
    MultiFingerCuspConstructor(cusp, pattern).generate()
    assert _all_edges_paired(cusp), f"Pattern {pattern} has unpaired edges"


@pytest.mark.parametrize(
    "pattern", _multi_finger_patterns, ids=[str(p) for p in _multi_finger_patterns]
)
def test_multi_finger_torus_topology(pattern):
    cusp = Cusp()
    MultiFingerCuspConstructor(cusp, pattern).generate()
    chi = _euler_characteristic(cusp)
    assert chi == 0, f"Pattern {pattern} has Euler characteristic {chi}, expected 0 (torus)"


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
