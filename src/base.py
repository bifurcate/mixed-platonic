"""Core data structures for mixed-Platonic cellulations of cusped hyperbolic 3-manifolds.

This module defines the combinatorial vocabulary for decomposing a cusped
hyperbolic 3-manifold into regular ideal polyhedra (tetrahedra and octahedra)
and representing the induced cusp cross-sections (triangles and squares).

The key geometric idea: each ideal vertex of a polyhedron contributes a
polygonal cross-section to the cusp boundary. A tetrahedron has 4 ideal
vertices, each contributing an equilateral triangle. An octahedron has 6
ideal vertices, each contributing a square. The cusp boundary is tiled by
these triangles and squares, and two cusp cells share an edge exactly when
the corresponding polyhedra share a face in the manifold.

The module provides:
    - Cusp cells (Triangle, Square) and manifold cells (Tetrahedron, Octahedron)
    - Half-edge / half-face and pairing structures that encode adjacency
    - Embeddings that record how manifold cell vertices map into cusp cells
    - Permutation lookup tables for enumerating vertex arrangements
    - Serialization helpers (``*_from_tuple``) for persistence
"""
from typing import Optional
from collections.abc import Iterator
from functools import cached_property

### Permutation Tables
#
# Each embedding assigns manifold cell vertices to positions in a cusp cell.
# Position 0 is always the ideal vertex at the cusp. The remaining positions
# are the polygon corners (positions 1-3 for a triangle, 1-4 for a square).
# For the octahedron, position 5 is the vertex antipodal to the cusp vertex.
#
# Permutations are indexed by (vert_idx, perm_idx):
#   - vert_idx: which manifold vertex occupies position 0 (the cusp vertex)
#   - perm_idx: which arrangement of the remaining vertices on the polygon
#
# For tetrahedra: 4 choices of cusp vertex x 3! = 6 corner arrangements = 24
# For octahedra: 6 choices of cusp vertex x 8 square symmetries (D_4) = 48

TET_PERMS = [
    (0, 1, 2, 3),
    (0, 1, 3, 2),
    (0, 2, 1, 3),
    (0, 2, 3, 1),
    (0, 3, 1, 2),
    (0, 3, 2, 1),
    (1, 0, 2, 3),
    (1, 0, 3, 2),
    (1, 2, 0, 3),
    (1, 2, 3, 0),
    (1, 3, 0, 2),
    (1, 3, 2, 0),
    (2, 0, 1, 3),
    (2, 0, 3, 1),
    (2, 1, 0, 3),
    (2, 1, 3, 0),
    (2, 3, 0, 1),
    (2, 3, 1, 0),
    (3, 0, 1, 2),
    (3, 0, 2, 1),
    (3, 1, 0, 2),
    (3, 1, 2, 0),
    (3, 2, 0, 1),
    (3, 2, 1, 0),
]

OCT_PERMS = [
    (0, 1, 2, 3, 4, 5),
    (0, 1, 4, 3, 2, 5),
    (0, 2, 1, 4, 3, 5),
    (0, 2, 3, 4, 1, 5),
    (0, 3, 2, 1, 4, 5),
    (0, 3, 4, 1, 2, 5),
    (0, 4, 1, 2, 3, 5),
    (0, 4, 3, 2, 1, 5),
    (1, 0, 2, 5, 4, 3),
    (1, 0, 4, 5, 2, 3),
    (1, 2, 0, 4, 5, 3),
    (1, 2, 5, 4, 0, 3),
    (1, 4, 0, 2, 5, 3),
    (1, 4, 5, 2, 0, 3),
    (1, 5, 2, 0, 4, 3),
    (1, 5, 4, 0, 2, 3),
    (2, 0, 1, 5, 3, 4),
    (2, 0, 3, 5, 1, 4),
    (2, 1, 0, 3, 5, 4),
    (2, 1, 5, 3, 0, 4),
    (2, 3, 0, 1, 5, 4),
    (2, 3, 5, 1, 0, 4),
    (2, 5, 1, 0, 3, 4),
    (2, 5, 3, 0, 1, 4),
    (3, 0, 2, 5, 4, 1),
    (3, 0, 4, 5, 2, 1),
    (3, 2, 0, 4, 5, 1),
    (3, 2, 5, 4, 0, 1),
    (3, 4, 0, 2, 5, 1),
    (3, 4, 5, 2, 0, 1),
    (3, 5, 2, 0, 4, 1),
    (3, 5, 4, 0, 2, 1),
    (4, 0, 1, 5, 3, 2),
    (4, 0, 3, 5, 1, 2),
    (4, 1, 0, 3, 5, 2),
    (4, 1, 5, 3, 0, 2),
    (4, 3, 0, 1, 5, 2),
    (4, 3, 5, 1, 0, 2),
    (4, 5, 1, 0, 3, 2),
    (4, 5, 3, 0, 1, 2),
    (5, 1, 2, 3, 4, 0),
    (5, 1, 4, 3, 2, 0),
    (5, 2, 1, 4, 3, 0),
    (5, 2, 3, 4, 1, 0),
    (5, 3, 2, 1, 4, 0),
    (5, 3, 4, 1, 2, 0),
    (5, 4, 1, 2, 3, 0),
    (5, 4, 3, 2, 1, 0),
]

# Forward lookup: (vert_idx, perm_idx) -> permutation tuple
TET_VERT_PERMS = [(i, j) for i in range(4) for j in range(6)]
TET_PERM_LU = dict(zip(TET_VERT_PERMS, TET_PERMS))
TET_PERM_RV_LU = dict(zip(TET_PERMS, TET_VERT_PERMS))

OCT_VERT_PERMS = [(i, j) for i in range(6) for j in range(8)]
OCT_PERM_LU = dict(zip(OCT_VERT_PERMS, OCT_PERMS))
OCT_PERM_RV_LU = dict(zip(OCT_PERMS, OCT_VERT_PERMS))

### Face and Edge Specifications
#
# Faces of manifold cells and edges of cusp cells, specified by vertex/corner
# indices. Cusp cell corners are numbered starting at 1 (position 0 is
# reserved for the cusp vertex in embeddings).

TET_FACES = [
    (0, 1, 2),
    (0, 1, 3),
    (0, 2, 3),
    (1, 2, 3),
]

OCT_FACES = [
    (0, 1, 2),
    (0, 1, 4),
    (0, 2, 3),
    (0, 3, 4),
    (1, 2, 5),
    (1, 4, 5),
    (2, 3, 5),
    (3, 4, 5),
]

TRI_EDGES = [
    (1, 2),
    (2, 3),
    (1, 3),
]

SQR_EDGES = [
    (1, 2),
    (2, 3),
    (3, 4),
    (1, 4),
]

TRI = 0
SQR = 1

CUSP_CELL_TYPE_LABEL = {
    None: "CuspCell",
    SQR: "Square",
    TRI: "Triangle",
}

CUSP_CELL_TYPE_SHORT_LABEL = {
    TRI: "tri",
    SQR: "sqr",
}

CuspCellType = Optional[int]
CuspCellIndex = int


class CuspCell:
    """A 2-dimensional cell in the cusp boundary tiling.

    Each cusp cell is a polygon (triangle or square) arising as the
    cross-section of an ideal polyhedron at one of its ideal vertices.
    Two cusp cells share an edge when the corresponding polyhedra share
    a triangular face in the manifold.

    Cusp cells are identified by their type (triangle or square) and a
    unique integer index. They are hashable and support equality comparison
    based on (cell_type, cell_index).

    Iterating over a CuspCell yields ``(cell_type, cell_index)``, which
    serves as the serialization format.

    Attributes:
        cell_type: Discriminator for the cell shape (TRI or SQR). Set by
            subclasses; None on the base class.
        cell_index: Unique integer identifying this cell within its type.
    """

    cell_type: CuspCellType = None

    def __init__(self, cell_index: CuspCellIndex):
        self.cell_index = cell_index
        self._hash = hash((self.cell_type, self.cell_index))

    def __repr__(self) -> str:
        return f"{CUSP_CELL_TYPE_LABEL[self.cell_type]}({self.cell_index})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: "CuspCell") -> bool:
        return self.cell_type == other.cell_type and self.cell_index == other.cell_index

    def __iter__(self) -> Iterator[CuspCellType | CuspCellIndex]:
        yield self.cell_type
        yield self.cell_index

    def is_sqr(self) -> bool:
        return self.cell_type == SQR

    def is_tri(self) -> bool:
        return self.cell_type == TRI

    def short_str(self) -> str:
        return f"{CUSP_CELL_TYPE_SHORT_LABEL[self.cell_type]}[{self.cell_index:2}]"


class Triangle(CuspCell):
    """An equilateral triangle cusp cell with unit side length.

    Arises as the cusp cross-section of a regular ideal tetrahedron at
    any of its four ideal vertices. Has 3 corners (positions 1, 2, 3 in
    the embedding coordinate system) and 3 edges.
    """

    cell_type: CuspCellType = TRI

    def __init__(self, cell_index: CuspCellIndex) -> None:
        super().__init__(cell_index)


Tri = Triangle


class Square(CuspCell):
    """A square cusp cell with unit side length.

    Arises as the cusp cross-section of a regular ideal octahedron at
    any of its six ideal vertices. Has 4 corners (positions 1, 2, 3, 4
    in the embedding coordinate system) and 4 edges.
    """

    cell_type: CuspCellType = SQR

    def __init__(self, cell_index: CuspCellIndex) -> None:
        super().__init__(cell_index)


Sqr = Square

CUSP_CELL_CLASS = {
    None: CuspCell,
    SQR: Square,
    TRI: Triangle,
}


def cusp_cell_from_tuple(cell_tuple: tuple[CuspCellType, CuspCellIndex]) -> CuspCell:
    """Deserializes a cusp cell from its ``(cell_type, cell_index)`` tuple."""
    return CUSP_CELL_CLASS[cell_tuple[0]](cell_tuple[1])


TET = 0
OCT = 1

MANIFOLD_CELL_TYPE_LABEL = {
    None: "ManifoldCell",
    TET: "Tetrahedron",
    OCT: "Octahedron",
}

MANIFOLD_CELL_TYPE_SHORT_LABEL = {
    TET: "tet",
    OCT: "oct",
}

ManifoldCellType = Optional[int]
ManifoldCellIndex = int


class ManifoldCell:
    """A regular ideal 3-cell (polyhedron) in the manifold decomposition.

    Each manifold cell is either a regular ideal tetrahedron (4 vertices,
    4 triangular faces) or a regular ideal octahedron (6 vertices, 8
    triangular faces). All vertices are ideal, meaning they lie on the
    boundary at infinity of hyperbolic 3-space.

    Manifold cells are identified by their type (TET or OCT) and a unique
    integer index. They are hashable and comparable by (cell_type, cell_index).

    Iterating yields ``(cell_type, cell_index)`` for serialization.

    Attributes:
        cell_type: Discriminator for the polyhedron type (TET or OCT). Set
            by subclasses; None on the base class.
        cell_index: Unique integer identifying this cell within its type.
    """

    cell_type: ManifoldCellType = None

    def __init__(self, cell_index: ManifoldCellIndex):
        self.cell_index = cell_index
        self._hash = hash((self.cell_type, self.cell_index))

    def __repr__(self) -> str:
        return f"{MANIFOLD_CELL_TYPE_LABEL[self.cell_type]}({self.cell_index})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: "ManifoldCell") -> bool:
        return self.cell_type == other.cell_type and self.cell_index == other.cell_index

    def __iter__(self) -> Iterator[ManifoldCellType | ManifoldCellIndex]:
        yield self.cell_type
        yield self.cell_index

    def is_tet(self) -> bool:
        return self.cell_type == TET

    def is_oct(self) -> bool:
        return self.cell_type == OCT

    def short_str(self) -> str:
        return f"{MANIFOLD_CELL_TYPE_SHORT_LABEL[self.cell_type]}[{self.cell_index}]"


class Tetrahedron(ManifoldCell):
    """A regular ideal tetrahedron with 4 vertices and 4 triangular faces.

    Each ideal vertex contributes an equilateral triangle to the cusp
    boundary. The 4 faces are listed in ``TET_FACES``.
    """

    cell_type: ManifoldCellType = TET

    def __init__(self, cell_index: ManifoldCellIndex) -> None:
        super().__init__(cell_index)


Tet = Tetrahedron


class Octahedron(ManifoldCell):
    """A regular ideal octahedron with 6 vertices and 8 triangular faces.

    Each ideal vertex contributes a square to the cusp boundary. Opposite
    vertex pairs are (0, 5), (1, 3), and (2, 4) under the standard labeling.
    The 8 faces are listed in ``OCT_FACES``.
    """

    cell_type: ManifoldCellType = OCT

    def __init__(self, cell_index: ManifoldCellIndex) -> None:
        super().__init__(cell_index)


Oct = Octahedron

MANIFOLD_CELL_CLASS = {
    None: ManifoldCell,
    TET: Tetrahedron,
    OCT: Octahedron,
}


def manifold_cell_from_tuple(
    cell_tuple: tuple[ManifoldCellType, ManifoldCellIndex],
) -> ManifoldCell:
    """Deserializes a manifold cell from its ``(cell_type, cell_index)`` tuple."""
    return MANIFOLD_CELL_CLASS[cell_tuple[0]](cell_tuple[1])


EdgeSpec = tuple[int, int]


class CuspHalfEdge:
    """One side of a shared edge between two cusp cells.

    In the cusp tiling, an edge is shared by exactly two cusp cells. A
    CuspHalfEdge represents that edge from the perspective of one cell,
    pairing the cell with the specific edge (given by the corner positions
    at its endpoints).

    A full edge pairing (``CuspEdgePairing``) consists of two half-edges,
    one from each adjacent cell.

    Attributes:
        cusp_cell: The cusp cell this half-edge belongs to.
        edge_spec: A pair of corner positions identifying the edge within
            the cell. For triangles these are drawn from {1, 2, 3}; for
            squares from {1, 2, 3, 4}.
    """

    def __init__(self, cusp_cell: CuspCell, edge_spec: EdgeSpec) -> None:
        self.cusp_cell = cusp_cell
        self.edge_spec = edge_spec
        self._hash = hash((self.cusp_cell._hash, self.edge_spec))

    def __iter__(self) -> Iterator[tuple[int, ...]]:
        yield tuple(self.cusp_cell)
        yield tuple(self.edge_spec)

    def __repr__(self) -> str:
        return f"CuspHalfEdge({repr(self.cusp_cell)}, {repr(self.edge_spec)})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: "CuspHalfEdge") -> bool:
        return self.cusp_cell == other.cusp_cell and self.edge_spec == other.edge_spec


def cusp_half_edge_from_tuple(half_edge_tuple: tuple) -> CuspHalfEdge:
    """Deserializes a CuspHalfEdge from its nested tuple form."""
    return CuspHalfEdge(
        cusp_cell_from_tuple(half_edge_tuple[0]),
        tuple(half_edge_tuple[1]),
    )


FaceSpec = tuple[int, int, int]


class ManifoldHalfFace:
    """One side of a shared triangular face between two manifold 3-cells.

    Each triangular face of a polyhedron is shared with exactly one
    neighboring polyhedron. A ManifoldHalfFace represents the face from
    the perspective of one cell.

    A full face pairing (``ManifoldFacePairing``) consists of two
    half-faces, one from each adjacent cell.

    Attributes:
        manifold_cell: The manifold 3-cell this half-face belongs to.
        face_spec: A triple of vertex indices identifying the triangular
            face within the cell.
    """

    def __init__(self, manifold_cell: ManifoldCell, face_spec: FaceSpec) -> None:
        self.manifold_cell = manifold_cell
        self.face_spec = face_spec
        self._hash = hash((self.manifold_cell._hash, self.face_spec))

    def __iter__(self) -> Iterator[tuple[int, ...]]:
        yield tuple(self.manifold_cell)
        yield tuple(self.face_spec)

    def __repr__(self) -> str:
        return f"ManifoldHalfFace({repr(self.manifold_cell)}, {repr(self.face_spec)})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: "ManifoldHalfFace") -> bool:
        return (
            self.manifold_cell == other.manifold_cell
            and self.face_spec == other.face_spec
        )


def normalize_edge_pair(
    edge_spec_source: EdgeSpec, edge_spec_target: EdgeSpec
) -> tuple[EdgeSpec, EdgeSpec]:
    """Puts an edge pairing into canonical form by sorting the source ascending.

    The source edge_spec is rewritten so that its first element is the
    smaller index. The same swap (if any) is applied to the target to
    preserve the vertex correspondence.

    Args:
        edge_spec_source: Edge endpoints in the source cusp cell.
        edge_spec_target: Corresponding edge endpoints in the target cell.

    Returns:
        A ``(source, target)`` pair with the source in ascending order.
    """
    if edge_spec_source[1] < edge_spec_source[0]:
        return (
            (edge_spec_source[1], edge_spec_source[0]),
            (edge_spec_target[1], edge_spec_target[0]),
        )
    else:
        return (edge_spec_source, edge_spec_target)


class CuspEdgePairing:
    """An adjacency between two cusp cells along a shared edge.

    Records a source and target half-edge that together describe how two
    cusp cells are glued along an edge in the cusp tiling. The source
    edge_spec is kept in canonical (ascending) order.

    The pairing carries a vertex map that extends the edge correspondence
    to include the cusp vertex (position 0 maps to 0), enabling the
    translation of embeddings across the shared edge.

    Attributes:
        half_edge_src: The half-edge on the source side.
        half_edge_tgt: The half-edge on the target side.
        map: Dict mapping source positions to target positions, including
            the cusp vertex ``0 -> 0`` and the two edge endpoints.
        inv: The inverse pairing (source and target swapped, re-normalized).
    """

    def __init__(
        self, half_edge_src: CuspHalfEdge, half_edge_tgt: CuspHalfEdge
    ) -> None:
        self.half_edge_src = half_edge_src
        self.half_edge_tgt = half_edge_tgt
        self._hash = hash((self.half_edge_src._hash, self.half_edge_tgt._hash))

    def __iter__(self) -> Iterator[tuple]:
        yield tuple(self.half_edge_src)
        yield tuple(self.half_edge_tgt)

    def __repr__(self) -> str:
        return (
            f"CuspEdgePairing({repr(self.half_edge_src)}, {repr(self.half_edge_tgt)})"
        )

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: "CuspEdgePairing") -> bool:
        return (
            self.half_edge_src == other.half_edge_src
            and self.half_edge_tgt == other.half_edge_tgt
        )

    @cached_property
    def map(self) -> dict[int, int]:
        """Vertex correspondence from source to target, including cusp vertex 0."""
        return dict(
            zip(
                (0,) + self.half_edge_src.edge_spec, (0,) + self.half_edge_tgt.edge_spec
            )
        )

    @cached_property
    def inv(self) -> "CuspEdgePairing":
        """The inverse pairing with source and target swapped."""
        inv_cusp_cell_src = self.half_edge_tgt.cusp_cell
        inv_cusp_cell_tgt = self.half_edge_src.cusp_cell

        inv_edge_spec_src, inv_edge_spec_tgt = normalize_edge_pair(
            self.half_edge_tgt.edge_spec,
            self.half_edge_src.edge_spec,
        )

        inv_half_edge_src = CuspHalfEdge(
            inv_cusp_cell_src,
            inv_edge_spec_src,
        )

        inv_half_edge_tgt = CuspHalfEdge(
            inv_cusp_cell_tgt,
            inv_edge_spec_tgt,
        )

        return CuspEdgePairing(inv_half_edge_src, inv_half_edge_tgt)


def cusp_edge_pairing_from_tuple(cusp_edge_pairing_tuple: tuple) -> CuspEdgePairing:
    """Deserializes a CuspEdgePairing from its nested tuple form."""
    return CuspEdgePairing(
        cusp_half_edge_from_tuple(cusp_edge_pairing_tuple[0]),
        cusp_half_edge_from_tuple(cusp_edge_pairing_tuple[1]),
    )


def normalize_face_pair(
    face_spec_src: FaceSpec, face_spec_tgt: FaceSpec
) -> tuple[FaceSpec, FaceSpec]:
    """Puts a face pairing into canonical form by sorting the source ascending.

    Computes the index permutation that sorts the source face_spec into
    ascending vertex order, then applies the same permutation to the target
    so that the vertex-to-vertex correspondence is preserved.

    Args:
        face_spec_src: Triangle vertex indices on the source side.
        face_spec_tgt: Corresponding vertex indices on the target side.

    Returns:
        A ``(source, target)`` pair with the source in ascending order.
    """
    sort_indices = [i for i, _ in sorted(enumerate(face_spec_src), key=lambda x: x[1])]

    face_spec_src_ordered = tuple(face_spec_src[i] for i in sort_indices)
    face_spec_tgt_ordered = tuple(face_spec_tgt[i] for i in sort_indices)

    return (face_spec_src_ordered, face_spec_tgt_ordered)


class ManifoldFacePairing:
    """An adjacency between two manifold 3-cells along a shared triangular face.

    Records a source and target half-face that together describe how two
    polyhedra are glued along a face. The source face_spec is kept in
    canonical (ascending vertex) order.

    Attributes:
        half_face_src: The half-face on the source side.
        half_face_tgt: The half-face on the target side.
        map: Dict mapping each source face vertex to the corresponding
            target face vertex.
        inv: The inverse pairing (source and target swapped, re-normalized).
    """

    def __init__(
        self, half_face_src: ManifoldHalfFace, half_face_tgt: ManifoldHalfFace
    ) -> None:
        self.half_face_src = half_face_src
        self.half_face_tgt = half_face_tgt
        self._hash = hash((self.half_face_src._hash, self.half_face_tgt._hash))

    def __iter__(self) -> Iterator[tuple]:
        yield tuple(self.half_face_src)
        yield tuple(self.half_face_tgt)

    def __repr__(self) -> str:
        return f"ManifoldFacePairing({repr(self.half_face_src)}, {repr(self.half_face_tgt)})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: "ManifoldFacePairing") -> bool:
        return (
            self.half_face_src == other.half_face_src
            and self.half_face_tgt == other.half_face_tgt
        )

    @cached_property
    def map(self) -> dict[int, int]:
        """Vertex correspondence from source face to target face."""
        return dict(zip(self.half_face_src.face_spec, self.half_face_tgt.face_spec))

    @cached_property
    def inv(self) -> "ManifoldFacePairing":
        """The inverse pairing with source and target swapped."""
        inv_manifold_cell_src = self.half_face_tgt.manifold_cell
        inv_manifold_cell_tgt = self.half_face_src.manifold_cell

        inv_face_spec_src, inv_face_spec_tgt = normalize_face_pair(
            self.half_face_tgt.face_spec,
            self.half_face_src.face_spec,
        )

        inv_half_face_src = ManifoldHalfFace(
            inv_manifold_cell_src,
            inv_face_spec_src,
        )

        inv_half_face_tgt = ManifoldHalfFace(
            inv_manifold_cell_tgt,
            inv_face_spec_tgt,
        )

        return ManifoldFacePairing(inv_half_face_src, inv_half_face_tgt)


TET_TRI = 0
OCT_SQR = 1

EMBEDDING_TYPE_LABEL = {
    None: "Embedding",
    TET_TRI: "TetTriEmbedding",
    OCT_SQR: "OctSqrEmbedding",
}


EmbeddingType = Optional[int]

# be more specific
EmbeddingSpec = tuple


class Embedding:
    """Maps the vertices of a manifold cell into the coordinate system of a cusp cell.

    An embedding records how a single ideal vertex of a manifold cell
    (tetrahedron or octahedron) projects into a particular cusp cell
    (triangle or square). The ``embedding_spec`` is a permutation that
    assigns each position index to a manifold cell vertex:

        ``embedding_spec[position] = manifold_vertex``

    Position 0 is the ideal vertex sitting at the cusp. The remaining
    positions correspond to the polygon corners of the cusp cell. For
    octahedra, position 5 is the vertex antipodal to the cusp vertex.

    If the embedding_spec contains None values (partially known), the
    ``complete()`` method on the appropriate subclass is called during
    ``__init__`` to deduce the full permutation.

    Attributes:
        embedding_type: Discriminator (TET_TRI or OCT_SQR).
        manifold_cell: The 3-cell being embedded.
        cusp_cell: The 2-cell receiving the embedding.
        embedding_spec: Permutation tuple mapping positions to manifold vertices.
        map: Forward dict ``{position: manifold_vertex}``.
        inv_map: Reverse dict ``{manifold_vertex: position}``.
    """

    embedding_type: EmbeddingType = None

    def __init__(
        self,
        manifold_cell: ManifoldCell,
        cusp_cell: CuspCell,
        embedding_spec: EmbeddingSpec,
    ) -> None:
        self.manifold_cell = manifold_cell
        self.cusp_cell = cusp_cell
        self.embedding_spec = embedding_spec

        if None in embedding_spec:
            self.complete()

        self._hash = hash(
            (
                self.embedding_type,
                self.manifold_cell._hash,
                self.cusp_cell._hash,
                self.embedding_spec,
            )
        )

    def __iter__(self) -> Iterator:
        yield self.embedding_type
        yield tuple(self.manifold_cell)
        yield tuple(self.cusp_cell)
        yield self.embedding_spec

    def __repr__(self) -> str:
        return f"{EMBEDDING_TYPE_LABEL[self.embedding_type]}({repr(self.manifold_cell)}, {repr(self.cusp_cell)}, {repr(self.embedding_spec)})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: "Embedding") -> bool:
        return (
            self.embedding_type == other.embedding_type
            and self.embedding_spec == other.embedding_spec
            and self.manifold_cell == other.manifold_cell
            and self.cusp_cell == other.cusp_cell
        )

    def is_tet_tri(self) -> bool:
        return self.embedding_type == TET_TRI

    def is_oct_sqr(self) -> bool:
        return self.embedding_type == OCT_SQR

    def get_iterator_indices(self) -> tuple[int, int, int]:
        """Returns ``(cell_index, vert_idx, perm_idx)`` for search iterator state."""
        vert_idx, perm_idx = self.get_indices()
        return self.manifold_cell.cell_index, vert_idx, perm_idx

    def short_str(self) -> str:
        em_spec_str = "".join(str(i) for i in self.embedding_spec)
        return f"{self.manifold_cell.short_str()}, {self.cusp_cell.short_str()}, {em_spec_str}"

    @cached_property
    def map(self) -> dict[int, int]:
        """Forward map from position index to manifold cell vertex."""
        return dict(
            zip(
                range(len(self.embedding_spec)),
                self.embedding_spec,
            )
        )

    @cached_property
    def inv_map(self) -> dict[int, int]:
        """Reverse map from manifold cell vertex to position index."""
        return dict(
            zip(
                self.embedding_spec,
                range(len(self.embedding_spec)),
            )
        )


TetTriEmbeddingSpec = tuple[int, int, int, int]


class TetTriEmbedding(Embedding):
    """Embedding of a tetrahedron vertex into a triangle cusp cell.

    The embedding_spec is a permutation of (0, 1, 2, 3) drawn from
    ``TET_PERMS``. Position 0 is the cusp vertex; positions 1, 2, 3 are
    the three corners of the triangle.

    Example:
        ``TetTriEmbedding(Tet(0), Tri(0), (3, 2, 1, 0))`` means
        tet vertex 3 sits at the cusp, and tet vertices 2, 1, 0 map
        to triangle corners 1, 2, 3 respectively.
    """

    embedding_type: EmbeddingType = TET_TRI

    def __init__(
        self,
        manifold_cell: Tetrahedron,
        cusp_cell: Triangle,
        embedding_spec: TetTriEmbeddingSpec,
    ) -> None:
        super().__init__(manifold_cell, cusp_cell, embedding_spec)

    def exposed(self, face_spec: FaceSpec) -> Optional[EdgeSpec]:
        """Returns the cusp cell edge exposed by a face, or None.

        A triangular face of the tetrahedron is "exposed" to this cusp
        cell if one of its three vertices is the cusp vertex (position 0).
        The other two vertices then project to two corners of the triangle,
        defining an edge of the cusp cell.

        Args:
            face_spec: A triple of manifold vertex indices forming a face
                of the tetrahedron (from ``TET_FACES``).

        Returns:
            The ``EdgeSpec`` (pair of corner positions) of the exposed
            triangle edge, or None if the face does not include the cusp
            vertex.
        """
        inv = self.inv_map
        indices = sorted((inv[i] for i in face_spec))

        if indices[0] == 0:
            return (indices[1], indices[2])
        else:
            return None

    def complete(self) -> None:
        """Fills in a single unknown position in the embedding_spec.

        When three of the four vertex assignments are known, the remaining
        one is uniquely determined. Called automatically during ``__init__``
        when the spec contains a None.
        """
        em = list(self.embedding_spec)
        unknown_idx = -1
        X = [0, 1, 2, 3]
        for i, v in enumerate(em):
            if v == None:
                unknown_idx = i
            else:
                X.remove(v)
        em[unknown_idx] = X[0]
        self.embedding_spec = tuple(em)

    def get_indices(self) -> Optional[tuple[int, int]]:
        """Returns the ``(vert_idx, perm_idx)`` pair for this permutation.

        Performs a reverse lookup in ``TET_PERM_RV_LU``. Returns None if
        the embedding_spec is not a valid tetrahedron permutation.
        """
        return TET_PERM_RV_LU.get(self.embedding_spec)

    @classmethod
    def from_indices(
        cls, manifold_cell_idx: int, cusp_cell_idx: int, vert_idx: int, perm_idx: int
    ) -> "TetTriEmbedding":
        """Constructs an embedding from iterator index coordinates.

        Args:
            manifold_cell_idx: Index of the tetrahedron.
            cusp_cell_idx: Index of the triangle cusp cell.
            vert_idx: Which tet vertex occupies position 0 (the cusp vertex).
            perm_idx: Which of the 6 arrangements of remaining vertices.

        Returns:
            The corresponding TetTriEmbedding.

        Raises:
            ValueError: If ``(vert_idx, perm_idx)`` is not a valid index pair.
        """
        embedding_spec = TET_PERM_LU.get((vert_idx, perm_idx))
        if embedding_spec is None:
            raise ValueError("invalid indices")
        return cls(Tet(manifold_cell_idx), Tri(cusp_cell_idx), embedding_spec)


OctSqrEmbeddingSpec = tuple[int, int, int, int, int, int]


class OctSqrEmbedding(Embedding):
    """Embedding of an octahedron vertex into a square cusp cell.

    The embedding_spec is a permutation of (0, 1, 2, 3, 4, 5) drawn from
    ``OCT_PERMS`` (the 48-element symmetry group of the octahedron).
    Position 0 is the cusp vertex, positions 1-4 are the four corners
    of the square, and position 5 is the vertex antipodal to the cusp vertex.

    Example:
        ``OctSqrEmbedding(Oct(0), Sqr(0), (2, 0, 3, 5, 1, 4))`` means
        oct vertex 2 sits at the cusp, vertices 0, 3, 5, 1 map to square
        corners 1-4, and vertex 4 is the antipodal vertex.
    """

    embedding_type: EmbeddingType = OCT_SQR

    def __init__(
        self,
        manifold_cell: Octahedron,
        cusp_cell: Square,
        embedding_spec: OctSqrEmbeddingSpec,
    ) -> None:
        super().__init__(manifold_cell, cusp_cell, embedding_spec)

    def exposed(self, face_spec: FaceSpec) -> Optional[EdgeSpec]:
        """Returns the cusp cell edge exposed by a face, or None.

        A triangular face of the octahedron is "exposed" to this cusp cell
        if all of the following hold:

        1. One vertex of the face is the cusp vertex (position 0).
        2. Neither of the other two vertices is the antipodal vertex
           (position 5).
        3. The two non-cusp vertices are adjacent corners on the square
           (their position indices differ by 1, or wrap around as 1 and 4).

        Four of the eight octahedral faces satisfy these conditions,
        corresponding to the four edges of the square.

        Args:
            face_spec: A triple of manifold vertex indices forming a face
                of the octahedron (from ``OCT_FACES``).

        Returns:
            The ``EdgeSpec`` of the exposed square edge, or None.
        """
        inv = self.inv_map
        indices = sorted((inv[i] for i in face_spec))

        if indices[0] == 0 and indices[2] != 5:
            diff = indices[2] - indices[1]
            if diff == 1 or diff == 3:
                return (indices[1], indices[2])
        else:
            return None

    def complete(self) -> None:
        """Fills in unknown positions by matching against valid octahedral permutations.

        Unlike the tetrahedron case where a single unknown is trivially
        deduced, the octahedron's symmetry constraints mean that multiple
        unknowns must be resolved simultaneously. This method searches
        ``OCT_PERMS`` for the unique permutation consistent with all known
        positions. Called automatically during ``__init__`` when the spec
        contains None values.
        """
        em = list(self.embedding_spec)

        known_idx = [i for i, v in enumerate(self.embedding_spec) if v is not None]

        for perm in OCT_PERMS:
            if all(perm[i] == em[i] for i in known_idx):
                self.embedding_spec = perm
                return

    def get_indices(self) -> Optional[tuple[int, int]]:
        """Returns the ``(vert_idx, perm_idx)`` pair for this permutation.

        Performs a reverse lookup in ``OCT_PERM_RV_LU``. Returns None if
        the embedding_spec is not a valid octahedron permutation.
        """
        return OCT_PERM_RV_LU.get(self.embedding_spec)

    @classmethod
    def from_indices(
        cls, manifold_cell_idx: int, cusp_cell_idx: int, vert_idx: int, perm_idx: int
    ) -> "OctSqrEmbedding":
        """Constructs an embedding from iterator index coordinates.

        Args:
            manifold_cell_idx: Index of the octahedron.
            cusp_cell_idx: Index of the square cusp cell.
            vert_idx: Which oct vertex occupies position 0 (the cusp vertex).
            perm_idx: Which of the 8 square symmetries (D_4) for the
                remaining vertex arrangement.

        Returns:
            The corresponding OctSqrEmbedding.

        Raises:
            ValueError: If ``(vert_idx, perm_idx)`` is not a valid index pair.
        """
        embedding_spec = OCT_PERM_LU.get((vert_idx, perm_idx))
        if embedding_spec is None:
            raise ValueError("invalid indices")
        return cls(Oct(manifold_cell_idx), Sqr(cusp_cell_idx), embedding_spec)


EMBEDDING_CLASS = {
    None: Embedding,
    TET_TRI: TetTriEmbedding,
    OCT_SQR: OctSqrEmbedding,
}


def embedding_from_tuple(embedding_tuple: tuple) -> Embedding:
    """Deserializes an Embedding from its ``(type, manifold, cusp, spec)`` tuple."""
    return EMBEDDING_CLASS[embedding_tuple[0]](
        manifold_cell_from_tuple(embedding_tuple[1]),
        cusp_cell_from_tuple(embedding_tuple[2]),
        tuple(embedding_tuple[3]),
    )
