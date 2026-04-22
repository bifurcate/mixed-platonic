import re

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


# --- pattern_filter tests ---

_N = 12
_all_patterns = generate_long_cusp(_N)


def _reference(regex: str) -> set[str]:
    """Post-filter the unfiltered set — the ground truth for pattern_filter."""
    return {p for p in _all_patterns if re.search(regex, p)}


@pytest.mark.parametrize(
    "regex",
    [
        "d",           # contains at least one d
        "de",          # contains the transition de
        "cc",          # contains two consecutive c's
        r"d.*d",       # contains d at least twice
        r"^[abc]+$",   # only a, b, c characters
        r"^[bde]+$",   # only b, d, e characters
        r"^e",         # starts with e
        r"^d",         # starts with d
    ],
)
def test_filter_matches_reference(regex):
    """pattern_filter must produce exactly the same set as post-filtering."""
    result = set(generate_long_cusp(_N, regex))
    assert result == _reference(regex)


def test_filter_none_matches_all():
    """pattern_filter=None must be identical to no filter."""
    assert set(generate_long_cusp(_N, None)) == set(_all_patterns)


def test_filter_compiled_pattern():
    """Accepts a pre-compiled re.Pattern as well as a string."""
    regex = "de"
    compiled = re.compile(regex)
    assert set(generate_long_cusp(_N, compiled)) == _reference(regex)


def test_filter_result_is_subset():
    """Every filtered result is contained in the unfiltered set."""
    filtered = generate_long_cusp(_N, "d")
    assert set(filtered) <= set(_all_patterns)


def test_filter_all_satisfy_regex():
    """Every returned pattern actually matches the regex."""
    regex = r"d.*d"
    for p in generate_long_cusp(_N, regex):
        assert re.search(regex, p), f"{p!r} returned but does not match {regex!r}"


def test_filter_no_false_positives():
    """No returned pattern violates the regex."""
    regex = r"^[abc]+$"
    for p in generate_long_cusp(_N, regex):
        assert re.search(regex, p), f"{p!r} violates {regex!r}"


def test_filter_impossible_regex_returns_empty():
    """A regex that no pattern can satisfy returns an empty list."""
    # 'f' is not in the alphabet, so no pattern can contain it.
    assert generate_long_cusp(_N, "f") == []


def test_filter_nonempty_for_known_matches():
    """Sanity check that a lax filter actually returns results."""
    # Every pattern contains at least one of {a,b,c,d,e}.
    result = generate_long_cusp(_N, "[abcde]")
    assert len(result) == len(_all_patterns)
