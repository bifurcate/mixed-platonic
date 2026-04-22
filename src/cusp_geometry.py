"""Exact 12-cyclotomic geometry for cusp tilings.

Associates a ``CyclotomicInt`` position to each corner of each cusp cell.
Corner positions are taken in the universal cover of the cusp torus; since
the tiling consists of unit-side regular triangles and squares, every
corner position lies in the ring Z[ζ₁₂] (see ``cyclotomic.py``).

Corners are indexed by the same conventions as ``base.py``:

    - Triangles: corners 1, 2, 3 (matching ``TRI_EDGES``)
    - Squares:   corners 1, 2, 3, 4 (matching ``SQR_EDGES``)

Position 0 (the cusp vertex used by embeddings) is *not* a corner of the
cusp cell and has no geometry stored here.
"""

from collections.abc import Iterator

from base import CuspCell, TRI, SQR, cusp_cell_from_tuple
from cyclotomic import CyclotomicInt


# Number of polygon corners by cusp cell type.
NUM_CORNERS: dict[int, int] = {
    TRI: 3,
    SQR: 4,
}


class CuspGeometry:
    """A geometric assignment of 12-cyclotomic positions to cusp cell corners.

    Stores a ``CyclotomicInt`` for each ``(cusp_cell, corner_index)`` pair.
    The indexing mirrors the multi-indexed dict pattern used by ``Cusp``
    and ``Embeddings``.

    Attributes:
        X: Nested dict ``cusp_cell -> {corner_index: CyclotomicInt}``.
            The outer dict is keyed by ``CuspCell``; the inner dict maps
            corner indices (1-based) to their cyclotomic positions.
    """

    def __init__(self) -> None:
        self.X: dict[CuspCell, dict[int, CyclotomicInt]] = {}

    def set_corner(
        self, cusp_cell: CuspCell, corner: int, position: CyclotomicInt
    ) -> None:
        """Assigns the position of one corner of a cusp cell.

        Args:
            cusp_cell: The cusp cell whose corner is being set.
            corner: 1-based corner index (1-3 for triangles, 1-4 for squares).
            position: The cyclotomic integer position.

        Raises:
            ValueError: If ``corner`` is out of range for ``cusp_cell``.
        """
        n = NUM_CORNERS[cusp_cell.cell_type]
        if not 1 <= corner <= n:
            raise ValueError(f"corner {corner} out of range 1..{n} for {cusp_cell!r}")
        self.X.setdefault(cusp_cell, {})[corner] = position

    def set_cell(
        self,
        cusp_cell: CuspCell,
        corners: dict[int, CyclotomicInt],
        offset: CyclotomicInt = CyclotomicInt(0, 0, 0, 0),
    ) -> None:
        """Assigns multiple corner positions of a single cusp cell.

        Args:
            cusp_cell: The cusp cell to populate.
            corners: Map ``corner_index -> position`` for one or more corners.
        """
        for corner, position in corners.items():
            self.set_corner(cusp_cell, corner, offset + position)

    def get_corner(self, cusp_cell: CuspCell, corner: int) -> CyclotomicInt | None:
        """Returns the position of one corner, or None if unassigned."""
        d = self.X.get(cusp_cell)
        if d is None:
            return None
        return d.get(corner)

    def get_cell(self, cusp_cell: CuspCell) -> dict[int, CyclotomicInt] | None:
        """Returns the corner-to-position dict for a cell, or None if absent."""
        return self.X.get(cusp_cell)

    def is_cell_complete(self, cusp_cell: CuspCell) -> bool:
        """Returns True iff every corner of ``cusp_cell`` has a position."""
        d = self.X.get(cusp_cell)
        if d is None:
            return False
        return len(d) == NUM_CORNERS[cusp_cell.cell_type]

    def remove_cell(self, cusp_cell: CuspCell) -> None:
        """Drops all stored corner positions for a cusp cell."""
        self.X.pop(cusp_cell, None)

    def cells(self) -> Iterator[CuspCell]:
        """Iterates over cusp cells with at least one assigned corner."""
        return iter(self.X.keys())

    def __iter__(self) -> Iterator[tuple[CuspCell, int, CyclotomicInt]]:
        """Yields ``(cusp_cell, corner_index, position)`` triples."""
        for cell, d in self.X.items():
            for corner, position in d.items():
                yield cell, corner, position

    def __contains__(self, cusp_cell: CuspCell) -> bool:
        return cusp_cell in self.X

    def dump(self) -> list[tuple]:
        """Serializes the geometry as a list of nested tuples.

        Each entry is ``((cell_type, cell_index), corner, (a, b, c, d))``.
        """
        return [
            (tuple(cell), corner, position.coeffs)
            for cell, d in self.X.items()
            for corner, position in d.items()
        ]

    def load(self, data: list[tuple]) -> None:
        """Restores corner positions from data produced by ``dump``."""
        for cell_tuple, corner, coeffs in data:
            cell = cusp_cell_from_tuple(tuple(cell_tuple))
            self.set_corner(cell, corner, CyclotomicInt(*coeffs))
