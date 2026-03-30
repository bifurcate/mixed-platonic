"""Recursive backtracking search for valid manifold cellulations.

This module implements the core search algorithm that enumerates all valid
ways to embed manifold cell vertices into cusp cells. The search proceeds
as follows:

1. Pick the first unembedded cusp cell in traversal order.
2. Try each candidate embedding (manifold cell, vertex, permutation).
3. After placing an embedding, propagate constraints: neighboring cusp
   cells may have their embeddings fully determined (induced) by the
   current state. Add all induced embeddings.
4. If no contradiction arose, recurse to embed the next cusp cell.
5. On backtrack, remove the placed and induced embeddings and try the
   next candidate.

A symmetry-breaking optimization avoids redundant work: when the
embedding iterator is at ``vert_idx == 0`` for a manifold cell, it means
no prior embedding constrains that cell's vertex placement. Only one
vertex assignment is tried in this case, since the others would produce
equivalent solutions under relabeling.
"""
from base import (
    EmbeddingType,
    Embedding,
    CuspCell,
    ManifoldCell,
    TET_TRI,
    OCT_SQR,
    Tetrahedron,
    Octahedron,
    TetTriEmbedding,
    OctSqrEmbedding,
)

from construction import (
    Embeddings,
    Construction,
)


class EmbeddingIterator:
    """Enumerates candidate embeddings for a given cusp cell type.

    Iterates through a three-dimensional index space::

        (cell_idx, vert_idx, perm_idx)

    where ``cell_idx`` selects a manifold cell, ``vert_idx`` selects which
    of its ideal vertices sits at the cusp, and ``perm_idx`` selects the
    arrangement of remaining vertices on the polygon corners. The total
    number of candidates is ``num_manifold_cells * num_verts * num_perms``.

    The iterator automatically skips vertices that are already embedded
    elsewhere, since each ideal vertex can only be placed in one cusp cell.

    Attributes:
        embedding_type: The embedding type this iterator produces (TET_TRI or OCT_SQR).
        manifold_cell_class: The manifold cell class (Tetrahedron or Octahedron).
        num_verts: Number of ideal vertices per cell (4 for tet, 6 for oct).
        num_perms: Number of polygon symmetries (6 = 3! for triangle, 8 = |D_4| for square).
        embeddings: Reference to the shared Embeddings collection, used to
            check which vertices are already embedded.
        num_manifold_cells: How many cells of this type exist.
        done: True when all candidates have been exhausted.
        cell_idx: Current manifold cell index.
        vert_idx: Current vertex index (which ideal vertex is at the cusp).
        perm_idx: Current permutation index (polygon corner arrangement).
    """

    embedding_type: EmbeddingType = None
    manifold_cell_class: type[ManifoldCell] | None = None
    num_verts: int = 0
    num_perms: int = 0

    def __init__(self, embeddings: Embeddings, num_manifold_cells: int) -> None:
        self.embeddings = embeddings
        self.num_manifold_cells = num_manifold_cells
        self._cells: list[ManifoldCell] = [
            self.manifold_cell_class(i) for i in range(num_manifold_cells)
        ]
        self.done: bool = False
        self.cell_idx: int = 0
        self.vert_idx: int = 0
        self.perm_idx: int = 0

    def set(self, cell_idx: int, vert_idx: int, perm_idx: int) -> None:
        """Positions the iterator at a specific index and skips if already embedded.

        Args:
            cell_idx: Manifold cell index.
            vert_idx: Vertex index within that cell.
            perm_idx: Permutation index.
        """
        self.done = False
        self.cell_idx = cell_idx
        self.vert_idx = vert_idx
        self.perm_idx = perm_idx

        if self.is_current_vert_embedded():
            self.next()

    def reset(self) -> None:
        """Resets the iterator to the beginning of the index space."""
        self.set(0, 0, 0)

    def is_current_vert_embedded(self) -> bool:
        """Checks if the current (cell, vertex) is already embedded elsewhere."""
        return self.embeddings.is_vert_embedded(
            self._cells[self.cell_idx],
            self.vert_idx,
        )

    def weak_next(self) -> "EmbeddingIterator | None":
        """Advances one step in the index space without skipping embedded vertices.

        Increments ``perm_idx`` first, then ``vert_idx`` on overflow, then
        ``cell_idx`` on overflow. If all indices overflow, sets ``done=True``
        and returns None.

        Returns:
            Self if advanced successfully, or None if exhausted.
        """
        if self.perm_idx < self.num_perms - 1:
            self.perm_idx += 1
            return self

        self.perm_idx = 0
        if self.vert_idx < self.num_verts - 1:
            self.vert_idx += 1
            return self

        self.vert_idx = 0
        if self.cell_idx < self.num_manifold_cells - 1:
            self.cell_idx += 1
            return self

        self.cell_idx = 0
        self.done = True
        return None

    def next(self) -> "EmbeddingIterator":
        """Advances to the next candidate whose vertex is not already embedded.

        Repeatedly calls ``weak_next`` until landing on an unembed vertex
        or exhausting all candidates.

        Returns:
            Self (check ``self.done`` to see if exhausted).
        """
        while True:
            self.weak_next()
            if not self.is_current_vert_embedded() or self.done:
                return self


class TetTriEmbeddingIterator(EmbeddingIterator):
    """Iterator for tetrahedron-into-triangle embeddings.

    Produces 4 vertices x 6 permutations = 24 candidates per tetrahedron.
    """

    embedding_type: EmbeddingType = TET_TRI
    manifold_cell_class: type[Tetrahedron] = Tetrahedron
    num_verts: int = 4
    num_perms: int = 6

    def __init__(self, embeddings: Embeddings, num_manifold_cells: int) -> None:
        super().__init__(embeddings, num_manifold_cells)


class OctSqrEmbeddingIterator(EmbeddingIterator):
    """Iterator for octahedron-into-square embeddings.

    Produces 6 vertices x 8 permutations = 48 candidates per octahedron.
    """

    embedding_type: EmbeddingType = OCT_SQR
    manifold_cell_class: type[Octahedron] = Octahedron
    num_verts: int = 6
    num_perms: int = 8

    def __init__(self, embeddings: Embeddings, num_manifold_cells: int) -> None:
        super().__init__(embeddings, num_manifold_cells)


INIT = 0
REGULAR = 1
INDUCED = 2

ENTRY_TYPE_SHORT_LABELS = {
    INIT: "O",
    REGULAR: "R",
    INDUCED: "I",
}

EntryType = int


class Solver:
    """Recursive backtracking search engine for cusp completion.

    Drives the search for valid embedding assignments over all cusp cells.
    For each unembedded cusp cell (in traversal order), the search tries
    every candidate embedding from the appropriate iterator, propagates
    induced constraints to a fixpoint, and recurses. Completed solutions
    (where every cusp cell has an embedding) are serialized and stored in
    ``self.completed``.

    Attributes:
        construction: The Construction holding cusp, embeddings, and
            constraint propagation logic.
        traversal: The order in which cusp cells are visited.
        num_tets: Number of tetrahedra in the decomposition.
        num_octs: Number of octahedra in the decomposition.
        tet_tri_embedding_iterator: Shared iterator state for tet-tri candidates.
        oct_sqr_embedding_iterator: Shared iterator state for oct-sqr candidates.
        counter: Total number of embedding placements attempted (for diagnostics).
        completed: List of serialized embedding states, one per valid solution.
    """

    def __init__(
        self,
        traversal: list[CuspCell],
        construction: Construction,
        num_tets: int,
        num_octs: int,
    ) -> None:
        self.construction = construction
        self.traversal = traversal
        self.num_tets = num_tets
        self.num_octs = num_octs
        self.tet_tri_embedding_iterator = TetTriEmbeddingIterator(
            self.construction.embeddings,
            self.num_tets,
        )
        self.oct_sqr_embedding_iterator = OctSqrEmbeddingIterator(
            self.construction.embeddings,
            self.num_octs,
        )
        self.counter: int = 0
        self.completed: list[list[tuple]] = []

    def get_next_embedding(
        self, cusp_cell: CuspCell, embedding: Embedding | None
    ) -> tuple[bool, Embedding | None]:
        """Advances the iterator to the next candidate embedding for a cusp cell.

        If ``embedding`` is None, resets the appropriate iterator to the
        beginning. Otherwise, positions the iterator at the given embedding's
        indices and advances to the next candidate.

        Args:
            cusp_cell: The cusp cell being embedded (determines which iterator
                to use: tet-tri for triangles, oct-sqr for squares).
            embedding: The most recently tried embedding, or None to start
                from the beginning.

        Returns:
            A ``(init, embedding)`` pair. ``init`` is True when the iterator
            is at ``vert_idx == 0``, indicating the start of an unconstrained
            manifold cell (used for symmetry breaking). ``embedding`` is the
            next candidate, or None if the iterator is exhausted.
        """
        if cusp_cell.is_tri():
            embedding_class = TetTriEmbedding
            embedding_iterator = self.tet_tri_embedding_iterator
        else:
            embedding_class = OctSqrEmbedding
            embedding_iterator = self.oct_sqr_embedding_iterator

        if embedding is None:
            embedding_iterator.reset()
        else:
            cell_idx, vert_idx, perm_idx = embedding.get_iterator_indices()
            embedding_iterator.set(cell_idx, vert_idx, perm_idx)
            embedding_iterator.next()

        if embedding_iterator.vert_idx == 0:
            init = True
        else:
            init = False

        if embedding_iterator.done:
            return (init, None)
        else:
            next_embedding = embedding_class.from_indices(
                embedding_iterator.cell_idx,
                cusp_cell.cell_index,
                embedding_iterator.vert_idx,
                embedding_iterator.perm_idx,
            )
            return (init, next_embedding)

    def get_next_induced(self) -> tuple[bool, int, Embedding | None]:
        """Scans all cusp cells for the next inducible or conflicting embedding.

        Iterates through the entire traversal looking for a cusp cell where
        neighbor constraints determine (or conflict with) an embedding.

        Returns:
            A ``(ok, index, embedding)`` triple:

            - ``(True, i, embedding)``: cell at index ``i`` has a valid
              induced embedding that should be added.
            - ``(True, i, None)``: all cells are consistent and no further
              inductions are possible (fixpoint reached).
            - ``(False, i, _)``: a contradiction was found at index ``i``.
              Either a constraint violation, a vertex double-embedding
              conflict, or an inconsistency with an existing embedding.
              The search should backtrack.
        """
        for i, c in enumerate(self.traversal):
            existing_embedding = (
                self.construction.embeddings.get_embedding_by_cusp_cell(c)
            )

            violation, proposed_embedding = (
                self.construction.get_induced_embedding_for_cell(c)
            )
            if violation:
                return (False, i, None)

            if proposed_embedding is None:
                continue

            if existing_embedding is None:
                m_cell = proposed_embedding.manifold_cell
                vert_idx = proposed_embedding.embedding_spec[0]
                if self.construction.embeddings.is_vert_embedded(m_cell, vert_idx):
                    # Vert already embedded!
                    return (False, i, proposed_embedding)
                else:
                    return (True, i, proposed_embedding)

            else:
                if existing_embedding != proposed_embedding:
                    # Embedding inconsistency!
                    return (False, i, proposed_embedding)
        return (True, i, None)

    def get_least_available_cusp_cell_idx(self) -> int | None:
        """Returns the traversal index of the first unembedded cusp cell, or None."""
        for idx, cusp_cell in enumerate(self.traversal):
            em = self.construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
            if em is None:
                return idx
        return None

    def process_completed(self) -> None:
        """Serializes the current embedding state and appends it to ``completed``."""
        self.completed.append(self.construction.embeddings.dump())

    def run(self) -> None:
        """Executes the recursive backtracking search from the current state.

        This is the main entry point for the search. Each call to ``run``
        handles one level of the recursion: it picks the first unembedded
        cusp cell and systematically tries candidate embeddings for it.

        **Base case**: If every cusp cell already has an embedding, the
        current state is a complete valid solution. It is serialized and
        appended to ``self.completed``, and the method returns so the
        caller can continue searching for additional solutions.

        **Recursive case**: For the first unembedded cusp cell, the method
        enters a while loop that iterates over candidate embeddings from
        ``get_next_embedding``. Each iteration performs:

        1. **Place**: Add the candidate embedding to the shared Embeddings
           collection.

        2. **Propagate (fixpoint loop)**: Repeatedly call ``get_next_induced``
           to find cusp cells whose embeddings are now fully determined by
           their already-embedded neighbors. Each induced embedding is added
           immediately, which may in turn induce further embeddings. The
           loop continues until either:

           - A contradiction is detected (``ok=False``): two neighbors
             induce conflicting embeddings, or an induced embedding would
             double-assign a manifold vertex. This means the current
             candidate is invalid.
           - No more inductions are possible (``ok=True, embedding=None``):
             the constraint propagation has reached a fixpoint and the
             partial assignment is consistent so far.

        3. **Recurse**: If propagation succeeded (``ok=True``), recursively
           call ``run()`` to embed the next unembedded cusp cell. This may
           find solutions (appended to ``completed``) or exhaust its
           options and return.

        4. **Backtrack**: Regardless of whether propagation or recursion
           succeeded, undo all changes: remove every induced embedding
           (in the order they were added), then remove the candidate
           embedding itself. This restores the Embeddings collection to
           the exact state it was in before step 1, so the next candidate
           starts from a clean slate.

        5. **Symmetry-breaking check**: If ``init`` is True, stop the
           loop and return. The ``init`` flag (from ``get_next_embedding``)
           is True when the embedding iterator is at ``vert_idx == 0`` for
           the current manifold cell. This arises in two situations:

           - **First candidate** (``embedding`` was None, iterator was
             reset): ``vert_idx == 0`` means no prior embedding constrains
             this manifold cell, so the vertex choice is arbitrary up to
             the cell's symmetry group. Only one vertex assignment (and
             all its permutations) needs to be tried; the others would
             yield equivalent solutions. After trying all permutations
             for this one vertex, the method returns.

           - **Manifold cell boundary**: The iterator exhausted all
             ``(vert, perm)`` pairs for one manifold cell and wrapped to
             ``vert_idx == 0`` of the next cell. Since each manifold cell's
             vertices are interchangeable when no prior constraints exist,
             trying additional cells would be redundant.

           When ``init`` is False, the iterator is partway through a
           manifold cell's vertex/permutation space (because prior
           embeddings already constrained some of its vertices, causing
           the iterator to skip to a non-zero vert_idx). In this case
           the full remaining space must be searched, so the loop continues.
        """
        # --- Base case: all cusp cells embedded ---
        tr_idx = (
            self.get_least_available_cusp_cell_idx()
        )  # maybe make this return embedding
        if tr_idx is None:
            self.process_completed()
            return

        cusp_cell = self.traversal[tr_idx]
        embedding = self.construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
        assert embedding is None

        # --- Recursive case: try each candidate for this cusp cell ---
        while True:
            # Advance the iterator to the next candidate. On the first
            # iteration embedding is None, so the iterator resets to the
            # beginning of its index space. On subsequent iterations it
            # resumes from the last tried position.
            init, next_embedding = self.get_next_embedding(cusp_cell, embedding)
            if next_embedding is None:
                return  # All candidates exhausted for this cusp cell.

            embedding = next_embedding

            # Step 1: Place the candidate embedding.
            self.construction.embeddings.add_embedding(embedding)

            self.counter += 1

            # Step 2: Propagate induced embeddings to a fixpoint.
            # Each newly induced embedding may enable further inductions,
            # so we loop until stable or until a contradiction is found.
            induced_embeddings = []
            while True:
                ok, _, next_induced_embedding = self.get_next_induced()
                if not ok or next_induced_embedding is None:
                    break
                induced_embeddings.append(next_induced_embedding)
                self.construction.embeddings.add_embedding(next_induced_embedding)

            # Step 3: If consistent, recurse to embed the next cusp cell.
            if ok:
                self.run()

            # Step 4: Backtrack — undo all embeddings from this iteration
            # (induced first, then the candidate itself) to restore the
            # state for the next candidate.
            for ie in induced_embeddings:
                self.construction.embeddings.remove_embedding(ie)

            self.construction.embeddings.remove_embedding(embedding)

            # Step 5: Symmetry-breaking — if init is True, we have tried
            # all permutations for an unconstrained manifold cell vertex.
            # Further candidates would be equivalent under symmetry.
            if init:
                return
