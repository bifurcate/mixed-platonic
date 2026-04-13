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

from long_cusp import (
    LongCuspConstructor,
    generate_long_cusp,
    get_poly_count,
    next_seq_gen,
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
    """Compute the Euler characteristic (V - E + F) of the cusp tiling.

    Uses union-find on cell corner positions to compute the number of
    distinct vertices. The vertex correspondence across shared edges is
    read from each CuspEdgePairing's map: src edge_spec[i] corresponds to
    tgt edge_spec[i] (validated against finger cusp geometric coordinates).
    """
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


# Generate patterns once for parametrization
_long_cusp_patterns = generate_long_cusp(12)


@pytest.mark.parametrize("pattern", _long_cusp_patterns)
def test_all_edges_paired(pattern):
    cusp = Cusp()
    constructor = LongCuspConstructor(cusp, pattern)
    constructor.generate()
    assert _all_edges_paired(cusp), f"Pattern {pattern!r} has unpaired edges"


@pytest.mark.parametrize("pattern", _long_cusp_patterns)
def test_torus_topology(pattern):
    cusp = Cusp()
    constructor = LongCuspConstructor(cusp, pattern)
    constructor.generate()
    chi = _euler_characteristic(cusp)
    assert chi == 0, f"Pattern {pattern!r} has Euler characteristic {chi}, expected 0 (torus)"


def test_long_cusp_constructor_generate():
    cusp = Cusp()
    pattern = "ebdcc" * 2
    cusp_constructor = LongCuspConstructor(cusp, pattern)

    cusp_constructor.generate()


def test_get_poly_count():
    pattern = "abdceb"
    count = get_poly_count(pattern)
    assert count[0] == 16
    assert count[1] == 7


@pytest.mark.parametrize("pattern", _long_cusp_patterns)
def test_divisibility(pattern):
    """Constructed cusp cell counts satisfy 4|n_tri and 6|n_sqr."""
    cusp = Cusp()
    constructor = LongCuspConstructor(cusp, pattern)
    constructor.generate()
    n_tri, n_sqr = constructor.get_num_polys()
    assert n_tri % 4 == 0, f"Pattern {pattern!r}: n_tri={n_tri} not divisible by 4"
    assert n_sqr % 6 == 0, f"Pattern {pattern!r}: n_sqr={n_sqr} not divisible by 6"


def test_next_seq_gen():

    gen = ["a", "b", "c", "d", "e"]
    next_gen = next_seq_gen(gen)
