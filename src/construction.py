"""Compound structures for cusp tilings, embedding collections, and manifold cellulations.

This module builds on the primitives in ``base.py`` to manage the full
combinatorial state of a mixed-Platonic decomposition. The central objects
are:

    - ``Cusp``: the 2D tiling of the cusp boundary by triangles and squares,
      stored as cells plus bidirectional edge pairings.
    - ``Embeddings``: a multi-indexed collection of vertex-to-cusp-cell
      assignments, supporting lookup by manifold cell, by cusp cell, and
      by (manifold cell, vertex).
    - ``Construction``: the orchestrator that ties the cusp tiling to the
      embedding state and provides constraint propagation (induced
      embeddings) and the final assembly of a ``ManifoldCellulation``.

The key algorithmic idea: an edge shared by two cusp cells corresponds to
a face shared by two manifold 3-cells. Given an embedding on one side of a
cusp edge, the cusp edge pairing and the manifold face pairing together
determine (induce) the embedding on the other side. The search algorithm
(in ``solver.py``) places embeddings one by one, propagating induced
constraints via the methods here, and backtracks when contradictions arise.
"""

from base import (
    TRI_EDGES,
    SQR_EDGES,
    TET_FACES,
    OCT_FACES,
    Tet,
    Oct,
    CuspCell,
    ManifoldCell,
    EdgeSpec,
    FaceSpec,
    CuspHalfEdge,
    ManifoldHalfFace,
    CuspEdgePairing,
    ManifoldFacePairing,
    TetTriEmbedding,
    OctSqrEmbedding,
    Embedding,
    embedding_from_tuple,
    normalize_edge_pair,
    normalize_face_pair,
    cusp_cell_from_tuple,
    cusp_edge_pairing_from_tuple,
)

# Violation sentinels returned by constraint-propagation functions.
# A non-None violation string indicates that the current partial
# embedding assignment is inconsistent and the search should backtrack.
CUSP_CELL_MISMATCH = "cusp cell mismatch"
INCOMPATIBLE_FACE_PAIRING = "incompatible face pairing"
CUSP_SHAPE_INCOMPATIBLE = "cusp shape incompatible"
MISSING_SOURCE_EMBEDDING = "missing source embedding"
DISTINCT_INDUCED_EMBEDDINGS = "distinct induced embeddings"

## COMPOUND OBJECTS


class Cusp:
    """The 2-dimensional cusp boundary tiling by triangles and squares.

    Stores the cusp cells and their edge pairings, which encode how
    adjacent cells are glued together. Each edge pairing is stored in
    both directions for bidirectional lookup.

    A Cusp may consist of multiple disconnected components (one per
    manifold cusp). Each component should tile a torus.

    Attributes:
        X: Adjacency index mapping each cusp cell to a dict of its edge
            pairings, keyed by ``EdgeSpec``. Contains both the forward
            and inverse direction of every pairing.
        pairs: Ordered list of edge pairings (forward direction only),
            preserving the insertion order from the cusp constructor.
    """

    def __init__(self) -> None:
        self.X: dict[CuspCell, dict[EdgeSpec, CuspEdgePairing]] = {}
        self.pairs: list[CuspEdgePairing] = []

    def add_cell(self, cell: CuspCell) -> None:
        """Registers a cusp cell with an empty adjacency dict."""
        self.X[cell] = {}

    def pair(
        self,
        cusp_cell_src: CuspCell,
        edge_spec_src: EdgeSpec,
        cusp_cell_tgt: CuspCell,
        edge_spec_tgt: EdgeSpec,
    ) -> None:
        """Creates an edge pairing between two cusp cells.

        Normalizes the edge specs (source ascending), builds the
        ``CuspEdgePairing``, appends it to ``pairs``, and inserts both
        the forward and inverse pairings into the adjacency index ``X``.

        Args:
            cusp_cell_src: The source cusp cell.
            edge_spec_src: Edge endpoints in the source cell.
            cusp_cell_tgt: The target cusp cell.
            edge_spec_tgt: Corresponding edge endpoints in the target cell.
        """

        edge_spec_src, edge_spec_tgt = normalize_edge_pair(edge_spec_src, edge_spec_tgt)

        cp = CuspEdgePairing(
            CuspHalfEdge(cusp_cell_src, edge_spec_src),
            CuspHalfEdge(cusp_cell_tgt, edge_spec_tgt),
        )

        self.pairs.append(cp)

        # insert in both directions

        if self.X.get(cp.half_edge_src.cusp_cell) is None:
            self.X[cp.half_edge_src.cusp_cell] = {}
        self.X[cp.half_edge_src.cusp_cell][cp.half_edge_src.edge_spec] = cp

        if self.X.get(cp.inv.half_edge_src.cusp_cell) is None:
            self.X[cp.inv.half_edge_src.cusp_cell] = {}
        self.X[cp.inv.half_edge_src.cusp_cell][cp.inv.half_edge_src.edge_spec] = cp.inv

    def get_cell_pairings(
        self, cusp_cell: CuspCell
    ) -> dict[EdgeSpec, CuspEdgePairing] | None:
        """Returns all edge pairings for a cell, keyed by edge spec, or None."""
        return self.X.get(cusp_cell)

    def dump(self) -> list[tuple]:
        """Serializes all pairings (forward direction) to a list of tuples."""
        return [tuple(cp) for cp in self.pairs]

    def load(self, data: list[tuple]) -> None:
        """Restores pairings from serialized tuple data produced by ``dump``."""
        for pairing in data:
            cp = cusp_edge_pairing_from_tuple(pairing)
            self.pair(
                cp.half_edge_src.cusp_cell,
                tuple(cp.half_edge_src.edge_spec),
                cp.half_edge_tgt.cusp_cell,
                tuple(cp.half_edge_tgt.edge_spec),
            )


class ManifoldCellulation:
    """The 3-dimensional manifold decomposition into tetrahedra and octahedra.

    Stores manifold 3-cells and their face pairings, which encode how
    adjacent polyhedra are glued along triangular faces. Like ``Cusp``,
    each face pairing is stored in both directions.

    Typically constructed as output by ``Construction.build_manifold_cellulation``
    once all embeddings have been placed.

    Attributes:
        X: Adjacency index mapping each manifold cell to a dict of its face
            pairings, keyed by ``FaceSpec``.
        pairs: Ordered list of face pairings (forward direction only).
    """

    def __init__(self) -> None:
        self.X: dict[ManifoldCell, dict[FaceSpec, ManifoldFacePairing]] = {}
        self.pairs: list[ManifoldFacePairing] = []

    def add_cell(self, cell: ManifoldCell) -> None:
        """Registers a manifold cell with an empty adjacency dict."""
        self.X[cell] = {}

    def pair(
        self,
        manifold_cell_src: ManifoldCell,
        face_spec_src: FaceSpec,
        manifold_cell_tgt: ManifoldCell,
        face_spec_tgt: FaceSpec,
    ) -> None:
        """Creates a face pairing between two manifold cells.

        Normalizes the face specs (source ascending), builds the
        ``ManifoldFacePairing``, and inserts both forward and inverse
        pairings into the adjacency index ``X``.

        Args:
            manifold_cell_src: The source manifold 3-cell.
            face_spec_src: Triangle vertex indices on the source side.
            manifold_cell_tgt: The target manifold 3-cell.
            face_spec_tgt: Corresponding vertex indices on the target side.
        """

        face_spec_src, face_spec_tgt = normalize_face_pair(face_spec_src, face_spec_tgt)

        cp = ManifoldFacePairing(
            ManifoldHalfFace(manifold_cell_src, face_spec_src),
            ManifoldHalfFace(manifold_cell_tgt, face_spec_tgt),
        )

        # insert in both directions
        self.X[cp.half_face_src.manifold_cell][cp.half_face_src.face_spec] = cp
        self.X[cp.inv.half_face_src.manifold_cell][
            cp.inv.half_face_src.face_spec
        ] = cp.inv

    def get_cell_pairings(
        self, manifold_cell: ManifoldCell
    ) -> dict[FaceSpec, ManifoldFacePairing] | None:
        """Returns all face pairings for a cell, keyed by face spec, or None."""
        return self.X.get(manifold_cell)


# TODO: make traversal a class
def dump_traversal(traversal: list[CuspCell]) -> list[tuple]:
    """Serializes a traversal order to a list of ``(cell_type, cell_index)`` tuples."""
    return [tuple(cell) for cell in traversal]


def load_traversal(data: list[tuple]) -> list[CuspCell]:
    """Deserializes a traversal order from tuple data produced by ``dump_traversal``."""
    return [cusp_cell_from_tuple(tuple(cell_tuple)) for cell_tuple in data]


class Embeddings:
    """Multi-indexed collection of manifold-to-cusp vertex embeddings.

    Maintains three parallel indices over the same set of embeddings,
    supporting efficient lookup patterns needed by the search algorithm:

    Attributes:
        X: Indexed by ``(manifold_cell, cusp_cell) -> Embedding``.
            Answers: "for a given manifold cell, which cusp cells has it
            been embedded into, and how?"
        Y: Indexed by ``cusp_cell -> Embedding``.
            Answers: "which manifold cell (if any) is embedded in this
            cusp cell?" Each cusp cell hosts at most one embedding.
        verts: Indexed by ``(manifold_cell, vert_idx) -> Embedding``,
            where ``vert_idx`` is ``embedding_spec[0]`` (the manifold
            vertex at the cusp). Answers: "has this particular ideal
            vertex of this manifold cell been embedded somewhere already?"
    """

    def __init__(self) -> None:
        self.X: dict[ManifoldCell, dict[CuspCell, Embedding]] = {}
        self.Y: dict[CuspCell, Embedding] = {}
        self.verts: dict[ManifoldCell, dict[int, Embedding]] = {}

    def add_embedding(self, embedding: Embedding) -> None:
        """Inserts an embedding into all three indices.

        Args:
            embedding: The embedding to add. Its ``embedding_spec[0]``
                determines the vertex index used in the ``verts`` index.
        """
        m_cell = embedding.manifold_cell
        self.X.setdefault(m_cell, {})[embedding.cusp_cell] = embedding
        self.Y[embedding.cusp_cell] = embedding
        vert = embedding.embedding_spec[0]
        self.verts.setdefault(m_cell, {})[vert] = embedding

    def remove_embedding(self, embedding: Embedding) -> None:
        """Removes an embedding from all three indices.

        Cleans up empty nested dicts so that manifold cells with no
        remaining embeddings are fully removed from ``X`` and ``verts``.

        Args:
            embedding: The embedding to remove.
        """
        d = self.X.get(embedding.manifold_cell)
        if d != None:
            d.pop(embedding.cusp_cell, None)
            if not d:
                self.X.pop(embedding.manifold_cell)

        self.Y.pop(embedding.cusp_cell, None)

        vert = embedding.embedding_spec[0]
        d = self.verts.get(embedding.manifold_cell)
        if d is not None:
            d.pop(vert, None)
            if not d:
                self.verts.pop(embedding.manifold_cell)

    def remove_embedding_by_cusp_cell(self, cusp_cell: CuspCell) -> None:
        """Convenience method to remove the embedding occupying a cusp cell."""
        em = self.get_embedding_by_cusp_cell(cusp_cell)
        self.remove_embedding(em)

    def is_vert_embedded(self, manifold_cell: ManifoldCell, vert: int) -> bool:
        """Checks whether a specific ideal vertex of a manifold cell has been embedded."""
        d = self.verts.get(manifold_cell)
        return d is not None and vert in d

    def get_embeddings_by_manifold_cell(
        self, manifold_cell: ManifoldCell
    ) -> dict[CuspCell, Embedding] | None:
        """Returns all embeddings for a manifold cell, keyed by cusp cell."""
        return self.X.get(manifold_cell)

    def dump_embeddings_by_manifold_cell(self) -> str:
        """Returns a human-readable string of all embeddings grouped by manifold cell."""
        s = ""
        for m_cell, d in self.X.items():
            s += f"{m_cell.short_str()}\n"
            for c_cell, em in d.items():
                s += f"  {c_cell.short_str()}: {em.short_str()}\n"
        return s

    def get_embedding_by_cusp_cell(self, cusp_cell: CuspCell) -> Embedding | None:
        """Returns the embedding occupying a cusp cell, or None if unoccupied."""
        return self.Y.get(cusp_cell)

    def dump_embeddings_by_cusp_cell(self) -> str:
        """Returns a human-readable string of all embeddings grouped by cusp cell."""
        s = ""
        for c_cell, em in self.Y.items():
            s += f"  {c_cell.short_str()}: {em.short_str()}\n"
        return s

    def get_embeddings_by_verts(
        self, manifold_cell: ManifoldCell
    ) -> dict[int, Embedding] | None:
        """Returns all embeddings for a manifold cell, keyed by cusp vertex index."""
        return self.verts.get(manifold_cell)

    def dump_embeddings_by_verts(self) -> str:
        """Returns a human-readable string of all embeddings grouped by vertex."""
        s = ""
        for m_cell, d in self.verts.items():
            s += f"{m_cell.short_str()}\n"
            for vert_idx, em in d.items():
                s += f"  {vert_idx}: {em.short_str()}\n"
        return s

    def dump(self) -> list[tuple]:
        """Serializes all embeddings to a list of tuples (via the Y index)."""
        return [tuple(em) for em in self.Y.values()]

    def load(self, data: list[tuple]) -> None:
        """Restores embeddings from serialized tuple data produced by ``dump``."""
        for embedding_tuple in data:
            self.add_embedding(embedding_from_tuple(embedding_tuple))


def get_manifold_face_pairing(
    embedding_src: Embedding,
    embedding_tgt: Embedding,
    cusp_pairing: CuspEdgePairing,
) -> ManifoldFacePairing:
    """Translates a cusp edge pairing into a manifold face pairing.

    Given two embeddings on either side of a shared cusp edge, computes
    the corresponding manifold face pairing. The shared edge in the cusp
    (plus the cusp vertex at position 0) maps through each embedding to
    give three manifold vertices on each side, defining the shared
    triangular face.

    The translation works by composing maps::

        cusp positions --embedding_src.map--> source face vertices
        cusp positions --cusp_pairing.map--> target cusp positions
                       --embedding_tgt.map--> target face vertices

    Args:
        embedding_src: The embedding on the source side of the cusp edge.
        embedding_tgt: The embedding on the target side of the cusp edge.
        cusp_pairing: The cusp edge pairing connecting the two cells.

    Returns:
        The manifold face pairing with normalized (ascending) source face.
    """
    cusp_half_edge_src = cusp_pairing.half_edge_src
    edge_spec_src = cusp_half_edge_src.edge_spec

    domain = (0,) + edge_spec_src
    face_spec_src = tuple(embedding_src.map.get(i) for i in domain)
    face_spec_tgt = tuple(
        embedding_tgt.map.get(cusp_pairing.map.get(i)) for i in domain
    )

    face_spec_src, face_spec_tgt = normalize_face_pair(face_spec_src, face_spec_tgt)

    return ManifoldFacePairing(
        ManifoldHalfFace(embedding_src.manifold_cell, face_spec_src),
        ManifoldHalfFace(embedding_tgt.manifold_cell, face_spec_tgt),
    )


def get_manifold_half_face(
    embedding: Embedding,
    cusp_half_edge: CuspHalfEdge,
) -> tuple[str | None, ManifoldHalfFace | None]:
    """Computes the manifold half-face corresponding to a cusp half-edge.

    Maps the cusp vertex (position 0) and the two edge endpoints through
    the embedding to obtain three manifold vertex indices, which form
    a triangular face of the manifold cell.

    Args:
        embedding: The embedding in the cusp cell that owns the half-edge.
        cusp_half_edge: The cusp half-edge to translate.

    Returns:
        A ``(violation, half_face)`` pair. If the embedding's cusp cell
        does not match the half-edge's cusp cell, returns
        ``(CUSP_CELL_MISMATCH, None)``. Otherwise returns
        ``(None, ManifoldHalfFace)``.
    """
    if embedding.cusp_cell != cusp_half_edge.cusp_cell:
        return (CUSP_CELL_MISMATCH, None)

    domain = (0,) + cusp_half_edge.edge_spec
    face_spec = tuple(sorted(embedding.map.get(i) for i in domain))

    return (
        None,
        ManifoldHalfFace(
            embedding.manifold_cell,
            face_spec,
        ),
    )


def get_embedding_tgt(
    manifold_face_pairing: ManifoldFacePairing,
    cusp_edge_pairing: CuspEdgePairing,
    embedding_src: Embedding,
) -> tuple[str | None, Embedding | None]:
    """Induces a target embedding from a source embedding across a shared face.

    This is the core constraint propagation step. Given a known embedding
    on one side of a cusp edge, the cusp edge pairing tells us which
    target cusp cell to embed into, and the manifold face pairing tells
    us how the shared face vertices correspond. Together they determine
    the target embedding for the positions that touch the shared edge
    (cusp vertex + two edge endpoints). The remaining positions are
    filled in by ``Embedding.complete()``.

    The computation chains three maps for each known position::

        target cusp position --inv(cusp_pairing)--> source cusp position
                             --embedding_src.map--> source manifold vertex
                             --face_pairing.map---> target manifold vertex

    Positions not on the shared edge produce None values that
    ``complete()`` resolves.

    Args:
        manifold_face_pairing: The face pairing between the two manifold cells.
        cusp_edge_pairing: The edge pairing between the two cusp cells.
        embedding_src: The known embedding on the source side.

    Returns:
        A ``(violation, embedding)`` pair. Possible violations:

        - ``CUSP_CELL_MISMATCH``: source embedding's cusp cell doesn't
          match the cusp edge pairing's source cell.
        - ``INCOMPATIBLE_FACE_PAIRING``: the manifold face implied by
          the source embedding doesn't match the given face pairing.
        - ``CUSP_SHAPE_INCOMPATIBLE``: the target cusp cell type
          (tri/sqr) doesn't match the target manifold cell type (tet/oct).
    """

    violation, half_face_src = get_manifold_half_face(
        embedding_src, cusp_edge_pairing.half_edge_src
    )
    if violation:
        return (violation, None)

    if manifold_face_pairing.half_face_src != half_face_src:
        return (INCOMPATIBLE_FACE_PAIRING, None)

    half_edge_tgt = cusp_edge_pairing.half_edge_tgt
    is_tri = half_edge_tgt.cusp_cell.is_tri()
    is_tet = manifold_face_pairing.half_face_tgt.manifold_cell.is_tet()

    if is_tri != is_tet:
        return (CUSP_SHAPE_INCOMPATIBLE, None)

    n = 4 if is_tri else 6
    known = frozenset((0,) + half_edge_tgt.edge_spec)
    inv_map = cusp_edge_pairing.inv.map
    src_map = embedding_src.map
    fp_map = manifold_face_pairing.map

    embedding_spec_tgt = tuple(
        fp_map.get(src_map.get(inv_map.get(i if i in known else None)))
        for i in range(n)
    )

    manifold_cell_tgt = manifold_face_pairing.half_face_tgt.manifold_cell
    cusp_cell_tgt = half_edge_tgt.cusp_cell

    if is_tri:
        return (
            None,
            TetTriEmbedding(manifold_cell_tgt, cusp_cell_tgt, embedding_spec_tgt),
        )
    else:
        return (
            None,
            OctSqrEmbedding(manifold_cell_tgt, cusp_cell_tgt, embedding_spec_tgt),
        )


class Construction:
    """Orchestrator tying cusp tiling, embeddings, and manifold cellulation together.

    Holds the cusp boundary tiling, the current set of vertex embeddings,
    the traversal order for the search, and the expected cell counts. Provides
    methods for:

    - Finding manifold face pairings implied by current embeddings.
    - Propagating constraints (induced embeddings) across cusp edges.
    - Building the complete ``ManifoldCellulation`` from a finished
      embedding assignment.

    Attributes:
        cusp: The cusp boundary tiling.
        embeddings: The current (possibly partial) set of embeddings.
        traversal: The order in which cusp cells are visited during search.
        num_tets: Expected number of tetrahedra in the decomposition.
        num_octs: Expected number of octahedra in the decomposition.
    """

    def __init__(
        self,
        cusp: Cusp,
        embeddings: Embeddings,
        traversal: list[CuspCell] = [],
        num_tets: int = 6,
        num_octs: int = 2,
    ) -> None:
        self.cusp = cusp
        self.embeddings = embeddings
        self.traversal = traversal
        self.num_tets = num_tets
        self.num_octs = num_octs

    def find_face_pairing(
        self,
        manifold_half_face: ManifoldHalfFace,
    ) -> ManifoldFacePairing | None:
        """Finds the manifold face pairing for a given half-face, if determinable.

        Searches all embeddings of the half-face's manifold cell to find
        one whose cusp cell has an exposed edge corresponding to this face.
        Then follows the cusp edge pairing to the neighboring cusp cell,
        and if that neighbor also has an embedding, computes the full
        manifold face pairing.

        Returns None if the manifold cell has no embeddings, or if the
        required neighbor embedding hasn't been placed yet.

        Args:
            manifold_half_face: The half-face to find a partner for.

        Returns:
            The complete ``ManifoldFacePairing``, or None if it cannot
            be determined from the current embedding state.
        """
        manifold_cell = manifold_half_face.manifold_cell
        face_spec = manifold_half_face.face_spec

        ems = self.embeddings.get_embeddings_by_manifold_cell(manifold_cell)

        if not ems:
            return None

        for cusp_cell, embedding_src in ems.items():
            edge_spec = embedding_src.exposed(face_spec)
            if edge_spec is None:
                continue

            pairings = self.cusp.get_cell_pairings(cusp_cell)
            cusp_pairing = pairings[edge_spec]
            if cusp_pairing is None:
                continue

            embedding_tgt = self.embeddings.get_embedding_by_cusp_cell(
                cusp_pairing.half_edge_tgt.cusp_cell
            )
            if embedding_tgt is None:
                continue

            return get_manifold_face_pairing(embedding_src, embedding_tgt, cusp_pairing)

    def get_induced_embedding_from_src(
        self,
        cusp_half_edge_src: CuspHalfEdge,
        embedding_src: Embedding | None = None,
        cusp_edge_pairing: CuspEdgePairing | None = None,
    ) -> tuple[str | None, Embedding | None]:
        """Propagates an embedding across a cusp edge from the source side.

        Starting from a source cusp half-edge, determines what embedding
        the target cusp cell must have, given the current state. The
        process is:

        1. Look up the source embedding (or use the one provided).
        2. Compute the manifold half-face exposed by this cusp edge.
        3. Find the manifold face pairing for that half-face.
        4. Induce the target embedding via ``get_embedding_tgt``.

        Args:
            cusp_half_edge_src: The half-edge on the source side.
            embedding_src: Optional pre-fetched source embedding. If None,
                looked up from ``self.embeddings``.
            cusp_edge_pairing: Optional pre-fetched cusp edge pairing. If
                None, looked up from ``self.cusp``.

        Returns:
            A ``(violation, embedding)`` pair. Returns ``(None, None)``
            (no violation, no result) when the face pairing or cusp
            pairing cannot be determined yet. A non-None violation string
            signals an inconsistency.
        """

        if embedding_src is None:
            embedding_src = self.embeddings.get_embedding_by_cusp_cell(
                cusp_half_edge_src.cusp_cell
            )
        if embedding_src is None:
            return (MISSING_SOURCE_EMBEDDING, None)

        if cusp_edge_pairing is None:
            cusp_edge_pairing = self.cusp.get_cell_pairings(
                cusp_half_edge_src.cusp_cell
            ).get(cusp_half_edge_src.edge_spec)
        if cusp_edge_pairing is None:
            return (None, None)

        violation, manifold_half_face_src = get_manifold_half_face(
            embedding_src,
            cusp_half_edge_src,
        )
        if violation:
            return (violation, None)

        manifold_face_pairing = self.find_face_pairing(
            manifold_half_face_src,
        )

        if manifold_face_pairing is None:
            return (None, None)

        violation, embedding_tgt = get_embedding_tgt(
            manifold_face_pairing, cusp_edge_pairing, embedding_src
        )
        if violation:
            return (violation, None)

        return (None, embedding_tgt)

    def get_induced_embedding_from_tgt(
        self,
        cusp_half_edge_tgt: CuspHalfEdge,
    ) -> tuple[str | None, Embedding | None]:
        """Propagates an embedding across a cusp edge from the target side.

        Inverts the cusp edge pairing and delegates to
        ``get_induced_embedding_from_src``.

        Args:
            cusp_half_edge_tgt: The half-edge on the target side.

        Returns:
            A ``(violation, embedding)`` pair, same semantics as
            ``get_induced_embedding_from_src``.
        """
        cusp_pairing = self.cusp.get_cell_pairings(cusp_half_edge_tgt.cusp_cell).get(
            cusp_half_edge_tgt.edge_spec
        )

        if cusp_pairing is None:
            return (None, None)

        cusp_half_edge_src = cusp_pairing.inv.half_edge_src
        return self.get_induced_embedding_from_src(cusp_half_edge_src)

    def get_induced_embeddings_for_cell(
        self, cusp_cell: CuspCell
    ) -> tuple[str | None, dict[EdgeSpec, Embedding] | None]:
        """Collects all embeddings inducible for a cusp cell from its neighbors.

        For each edge of the cusp cell, checks whether the neighbor across
        that edge has an embedding. If so, propagates it back through the
        inverse pairing to determine what embedding this cell should have.

        Args:
            cusp_cell: The cusp cell to compute induced embeddings for.

        Returns:
            A ``(violation, embeddings_dict)`` pair. The dict maps each
            edge that yielded an induced embedding to that embedding.
            A non-None violation signals an inconsistency from one of
            the edges.
        """
        edges = TRI_EDGES if cusp_cell.is_tri() else SQR_EDGES

        possible_embeddings: dict[EdgeSpec, Embedding] = {}
        pairings = self.cusp.get_cell_pairings(cusp_cell)
        for e in edges:
            pairing = pairings.get(e)
            if pairing is None:
                continue

            neighbor_cell = pairing.half_edge_tgt.cusp_cell
            neighbor_embedding = self.embeddings.get_embedding_by_cusp_cell(
                neighbor_cell
            )
            if neighbor_embedding is None:
                continue

            inv_pairing = pairing.inv
            violation, induced_embedding = self.get_induced_embedding_from_src(
                inv_pairing.half_edge_src,
                embedding_src=neighbor_embedding,
                cusp_edge_pairing=inv_pairing,
            )
            if violation:
                return (violation, None)
            possible_embeddings[e] = induced_embedding
        return (None, possible_embeddings)

    def get_induced_embedding_for_cell(
        self, cusp_cell: CuspCell
    ) -> tuple[str | None, Embedding | None]:
        """Computes the unique induced embedding for a cusp cell, with consistency check.

        Like ``get_induced_embeddings_for_cell``, but requires that all
        edges inducing an embedding agree on the same result. If two edges
        produce different embeddings, this is a ``DISTINCT_INDUCED_EMBEDDINGS``
        violation, meaning the current partial assignment is inconsistent.

        Args:
            cusp_cell: The cusp cell to compute the induced embedding for.

        Returns:
            A ``(violation, embedding)`` pair. Returns ``(None, None)``
            if no neighbor has an embedding yet. Returns the single
            consistent embedding if one or more neighbors agree. Returns
            a violation if neighbors disagree.
        """
        edges = TRI_EDGES if cusp_cell.is_tri() else SQR_EDGES
        pairings = self.cusp.get_cell_pairings(cusp_cell)

        result = None
        for e in edges:
            pairing = pairings.get(e)
            if pairing is None:
                continue

            neighbor_cell = pairing.half_edge_tgt.cusp_cell
            neighbor_embedding = self.embeddings.get_embedding_by_cusp_cell(
                neighbor_cell
            )
            if neighbor_embedding is None:
                continue

            inv_pairing = pairing.inv
            violation, induced = self.get_induced_embedding_from_src(
                inv_pairing.half_edge_src,
                embedding_src=neighbor_embedding,
                cusp_edge_pairing=inv_pairing,
            )
            if violation:
                return (violation, None)
            if induced is None:
                continue

            if result is None:
                result = induced
            elif result != induced:
                return (DISTINCT_INDUCED_EMBEDDINGS, None)

        return (None, result)

    def build_manifold_cellulation(self) -> ManifoldCellulation:
        """Assembles the complete manifold cellulation from current embeddings.

        Iterates over every face of every manifold cell (tetrahedra and
        octahedra), finds its face pairing via the cusp structure and
        current embeddings, and registers it in a new ``ManifoldCellulation``.

        Should only be called once all embeddings have been placed (i.e.,
        when the search has found a complete solution).

        Returns:
            A fully populated ``ManifoldCellulation`` with all face pairings.
        """
        # right now this is redundant and adds cell twice for each pair
        # however it builds the correct object
        mc = ManifoldCellulation()
        for i in range(self.num_tets):
            mc.add_cell(Tet(i))

        for i in range(self.num_octs):
            mc.add_cell(Oct(i))

        for i in range(self.num_tets):
            for face_spec in TET_FACES:
                fp = self.find_face_pairing(ManifoldHalfFace(Tet(i), face_spec))
                if fp is not None:
                    mc.pair(
                        fp.half_face_src.manifold_cell,
                        fp.half_face_src.face_spec,
                        fp.half_face_tgt.manifold_cell,
                        fp.half_face_tgt.face_spec,
                    )
        for i in range(self.num_octs):
            for face_spec in OCT_FACES:
                fp = self.find_face_pairing(ManifoldHalfFace(Oct(i), face_spec))
                if fp is not None:
                    mc.pair(
                        fp.half_face_src.manifold_cell,
                        fp.half_face_src.face_spec,
                        fp.half_face_tgt.manifold_cell,
                        fp.half_face_tgt.face_spec,
                    )
        return mc
