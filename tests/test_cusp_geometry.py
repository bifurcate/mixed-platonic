import pytest

from base import Tri, Sqr
from cyclotomic import CyclotomicInt, ZETA
from cusp_geometry import CuspGeometry


class TestCuspGeometry:
    def test_set_and_get_corner(self):
        g = CuspGeometry()
        g.set_corner(Tri(0), 1, CyclotomicInt(0, 0, 0, 0))
        g.set_corner(Tri(0), 2, CyclotomicInt(1, 0, 0, 0))
        g.set_corner(Tri(0), 3, ZETA[2])

        assert g.get_corner(Tri(0), 1) == CyclotomicInt(0, 0, 0, 0)
        assert g.get_corner(Tri(0), 2) == CyclotomicInt(1, 0, 0, 0)
        assert g.get_corner(Tri(0), 3) == ZETA[2]

    def test_get_corner_missing(self):
        g = CuspGeometry()
        assert g.get_corner(Tri(0), 1) is None
        g.set_corner(Tri(0), 1, ZETA[0])
        assert g.get_corner(Tri(0), 2) is None
        assert g.get_corner(Tri(1), 1) is None

    def test_set_cell(self):
        g = CuspGeometry()
        g.set_cell(
            Sqr(0),
            {1: ZETA[0], 2: ZETA[3], 3: ZETA[0] + ZETA[3], 4: CyclotomicInt()},
        )
        assert g.get_cell(Sqr(0)) == {
            1: ZETA[0],
            2: ZETA[3],
            3: ZETA[0] + ZETA[3],
            4: CyclotomicInt(),
        }

    def test_corner_out_of_range_triangle(self):
        g = CuspGeometry()
        with pytest.raises(ValueError):
            g.set_corner(Tri(0), 0, ZETA[0])
        with pytest.raises(ValueError):
            g.set_corner(Tri(0), 4, ZETA[0])

    def test_corner_out_of_range_square(self):
        g = CuspGeometry()
        with pytest.raises(ValueError):
            g.set_corner(Sqr(0), 0, ZETA[0])
        with pytest.raises(ValueError):
            g.set_corner(Sqr(0), 5, ZETA[0])

    def test_is_cell_complete_triangle(self):
        g = CuspGeometry()
        assert not g.is_cell_complete(Tri(0))
        g.set_corner(Tri(0), 1, ZETA[0])
        g.set_corner(Tri(0), 2, ZETA[1])
        assert not g.is_cell_complete(Tri(0))
        g.set_corner(Tri(0), 3, ZETA[2])
        assert g.is_cell_complete(Tri(0))

    def test_is_cell_complete_square(self):
        g = CuspGeometry()
        for i in range(1, 4):
            g.set_corner(Sqr(0), i, ZETA[i])
        assert not g.is_cell_complete(Sqr(0))
        g.set_corner(Sqr(0), 4, ZETA[0])
        assert g.is_cell_complete(Sqr(0))

    def test_remove_cell(self):
        g = CuspGeometry()
        g.set_corner(Tri(0), 1, ZETA[0])
        g.set_corner(Tri(1), 1, ZETA[0])
        g.remove_cell(Tri(0))
        assert Tri(0) not in g
        assert Tri(1) in g

    def test_contains_and_cells(self):
        g = CuspGeometry()
        g.set_corner(Tri(0), 1, ZETA[0])
        g.set_corner(Sqr(0), 1, ZETA[0])
        assert Tri(0) in g
        assert Sqr(0) in g
        assert Tri(1) not in g
        assert set(g.cells()) == {Tri(0), Sqr(0)}

    def test_iter_yields_triples(self):
        g = CuspGeometry()
        g.set_corner(Tri(0), 1, ZETA[0])
        g.set_corner(Tri(0), 2, ZETA[1])
        triples = sorted(((c.cell_index, k, p) for c, k, p in g), key=lambda t: t[1])
        assert triples == [(0, 1, ZETA[0]), (0, 2, ZETA[1])]

    def test_dump_load_roundtrip(self):
        g = CuspGeometry()
        g.set_corner(Tri(0), 1, ZETA[0])
        g.set_corner(Tri(0), 2, ZETA[4])
        g.set_corner(Sqr(2), 3, CyclotomicInt(1, -2, 3, -4))

        data = g.dump()

        g2 = CuspGeometry()
        g2.load(data)

        assert g2.get_corner(Tri(0), 1) == ZETA[0]
        assert g2.get_corner(Tri(0), 2) == ZETA[4]
        assert g2.get_corner(Sqr(2), 3) == CyclotomicInt(1, -2, 3, -4)

    def test_set_corner_overwrites(self):
        g = CuspGeometry()
        g.set_corner(Tri(0), 1, ZETA[0])
        g.set_corner(Tri(0), 1, ZETA[5])
        assert g.get_corner(Tri(0), 1) == ZETA[5]
