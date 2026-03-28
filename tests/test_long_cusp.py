import pytest

from base import (
    Sqr,
    Tri,
    CuspHalfEdge,
    CuspEdgePairing,
)

from construction import Cusp

from long_cusp import (
    LongCuspGenerator,
    get_poly_count,
    next_seq_gen,
)


def test_long_cusp_generator_generate():
    cusp = Cusp()
    pattern = "ebdcc" * 2
    cusp_generator = LongCuspGenerator(cusp, pattern)

    cusp_generator.generate()


def test_get_poly_count():
    pattern = "abdceb"
    count = get_poly_count(pattern)
    assert count[0] == 16
    assert count[1] == 7


def test_next_seq_gen():

    gen = ["a", "b", "c", "d", "e"]
    next_gen = next_seq_gen(gen)
