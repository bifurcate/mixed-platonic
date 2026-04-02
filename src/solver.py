"""Backtracking search for valid manifold cellulations.

This module implements the core search algorithm that enumerates all valid
ways to embed manifold cell vertices into cusp cells. The search proceeds
as follows:

1. Pick the first unembedded cusp cell in traversal order.
2. Try each candidate embedding (manifold cell, vertex, permutation).
3. After placing an embedding, propagate constraints: neighboring cusp
   cells may have their embeddings fully determined (induced) by the
   current state. Add all induced embeddings.
4. If no contradiction arose, descend to embed the next cusp cell.
5. On backtrack, remove the placed and induced embeddings and try the
   next candidate.

A symmetry-breaking optimization avoids redundant work: when the
embedding iterator is at ``vert_idx == 0`` for a manifold cell, it means
no prior embedding constrains that cell's vertex placement. Only one
vertex assignment is tried in this case, since the others would produce
equivalent solutions under relabeling.

The solver uses an explicit stack rather than recursion, which enables
checkpointing: the search can be stopped (e.g. via Ctrl+C) and resumed
later from exactly where it left off.
"""

from dataclasses import dataclass, field

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
    embedding_from_tuple,
    cusp_cell_from_tuple,
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


@dataclass
class StackFrame:
    """One level of the backtracking search stack.

    Each frame tracks the embedding candidate currently being tried for
    a single cusp cell, along with any embeddings that were induced by
    constraint propagation after placing it.

    Attributes:
        cusp_cell: The cusp cell being embedded at this search level.
        embedding: The current candidate embedding, or None if no candidate
            has been tried yet at this level.
        induced_embeddings: Embeddings added by constraint propagation after
            placing the candidate.
        init: True when the embedding iterator was at vert_idx==0 for this
            candidate, used for symmetry breaking.
        placed: True when the embedding and its induced embeddings are
            currently in the Embeddings collection. This is runtime state
            only and is not serialized in checkpoints.
    """

    cusp_cell: CuspCell
    embedding: Embedding | None = None
    induced_embeddings: list[Embedding] = field(default_factory=list)
    init: bool = False
    placed: bool = False

    def dump(self) -> dict:
        """Serialize to a JSON-compatible dict for checkpointing."""
        return {
            "cusp_cell": tuple(self.cusp_cell),
            "embedding": tuple(self.embedding) if self.embedding else None,
            "induced_embeddings": [tuple(ie) for ie in self.induced_embeddings],
            "init": self.init,
        }

    @classmethod
    def load(cls, data: dict) -> "StackFrame":
        """Deserialize from a checkpoint dict."""
        cusp_cell = cusp_cell_from_tuple(data["cusp_cell"])
        embedding = (
            embedding_from_tuple(data["embedding"]) if data["embedding"] else None
        )
        induced = [embedding_from_tuple(ie) for ie in data["induced_embeddings"]]
        return cls(
            cusp_cell=cusp_cell,
            embedding=embedding,
            induced_embeddings=induced,
            init=data["init"],
        )


class Solver:
    """Backtracking search engine for cusp completion.

    Drives the search for valid embedding assignments over all cusp cells.
    For each unembedded cusp cell (in traversal order), the search tries
    every candidate embedding from the appropriate iterator, propagates
    induced constraints to a fixpoint, and descends. Completed solutions
    (where every cusp cell has an embedding) are serialized and stored in
    ``self.completed``.

    The search uses an explicit stack (``self.stack``) rather than recursive
    calls, enabling checkpoint/resume: the solver can be stopped mid-search
    via ``request_stop()`` and the state saved with ``save_checkpoint()``.
    A subsequent run can restore the state with ``load_checkpoint()`` and
    call ``run()`` to continue from where it left off.

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
        stack: Explicit backtracking stack (list of StackFrame).
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
        self.stack: list[StackFrame] = []
        self._stop_requested: bool = False

    def request_stop(self) -> None:
        """Signal the solver to stop at the next safe point.

        The solver will finish backtracking the current candidate (if any),
        then return "stopped" from ``run()``. The caller can then save a
        checkpoint and resume later.
        """
        self._stop_requested = True

    def save_checkpoint(self) -> dict:
        """Serialize the current search state for later resumption.

        Returns:
            A JSON-serializable dict containing the search stack, iteration
            counter, and any completions found so far.
        """
        return {
            "stack": [frame.dump() for frame in self.stack],
            "counter": self.counter,
            "completed": self.completed,
        }

    def load_checkpoint(self, data: dict) -> None:
        """Restore search state from a previously saved checkpoint.

        Rebuilds the explicit search stack and re-adds all placed embeddings
        to the Embeddings collection. All frames except the topmost have
        their embeddings re-placed, so the search resumes by trying the
        next candidate for the top frame.

        Args:
            data: Checkpoint dict as produced by ``save_checkpoint()``.
        """
        self.counter = data["counter"]
        self.completed = data["completed"]
        self.stack = []
        self._stop_requested = False

        frames = data["stack"]
        for i, frame_data in enumerate(frames):
            frame = StackFrame.load(frame_data)
            # All frames except the last have their embeddings currently placed
            if i < len(frames) - 1:
                frame.placed = True
                self.construction.embeddings.add_embedding(frame.embedding)
                for ie in frame.induced_embeddings:
                    self.construction.embeddings.add_embedding(ie)
            self.stack.append(frame)

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

    def run(self) -> str:
        """Execute the backtracking search.

        Uses an explicit stack instead of recursion. Each stack frame
        represents one level of the search: a cusp cell and the candidate
        embedding currently being tried for it.

        The main loop repeatedly:

        1. **Backtracks** the top frame's embedding if one is currently
           placed (removing induced embeddings first, then the candidate).
           If the symmetry-breaking ``init`` flag was set, the frame is
           popped entirely.

        2. **Checks for stop requests** — if ``request_stop()`` was called
           (e.g. via a signal handler), returns ``"stopped"`` so the caller
           can save a checkpoint.

        3. **Tries the next candidate** embedding for the top frame's cusp
           cell. If all candidates are exhausted, pops the frame.

        4. **Places** the candidate and **propagates** induced embeddings
           to a fixpoint. If a contradiction is found, loops back to
           backtrack and try the next candidate.

        5. If propagation succeeded and all cusp cells are now embedded,
           records the completion. Otherwise, **pushes a new frame** for
           the next unembedded cusp cell and continues.

        Returns:
            ``"completed"`` if the entire search space was explored, or
            ``"stopped"`` if the search was interrupted via ``request_stop()``.
        """
        # Initialize the stack on a fresh start
        if not self.stack:
            tr_idx = self.get_least_available_cusp_cell_idx()
            if tr_idx is None:
                self.process_completed()
                return "completed"
            self.stack.append(StackFrame(cusp_cell=self.traversal[tr_idx]))

        while self.stack:
            frame = self.stack[-1]

            # Step 1: Backtrack if the current candidate is placed
            if frame.placed:
                for ie in frame.induced_embeddings:
                    self.construction.embeddings.remove_embedding(ie)
                self.construction.embeddings.remove_embedding(frame.embedding)
                frame.induced_embeddings = []
                frame.placed = False

                # Symmetry breaking: if init was True for this candidate,
                # all permutations for an unconstrained vertex have been
                # tried. Pop this frame.
                if frame.init:
                    self.stack.pop()
                    continue

            # Step 2: Check for stop request (safe point — nothing from
            # this frame is placed, so the stack is in a clean state for
            # checkpointing)
            if self._stop_requested:
                return "stopped"

            # Step 3: Try the next candidate embedding
            init, next_embedding = self.get_next_embedding(
                frame.cusp_cell, frame.embedding
            )
            if next_embedding is None:
                self.stack.pop()
                continue

            frame.embedding = next_embedding
            frame.init = init

            # Step 4a: Place the candidate
            self.construction.embeddings.add_embedding(frame.embedding)
            frame.placed = True
            self.counter += 1

            # Step 4b: Propagate induced embeddings to fixpoint
            frame.induced_embeddings = []
            ok = True
            while True:
                ok_inner, _, next_induced = self.get_next_induced()
                if not ok_inner:
                    ok = False
                    break
                if next_induced is None:
                    break
                frame.induced_embeddings.append(next_induced)
                self.construction.embeddings.add_embedding(next_induced)

            if not ok:
                continue  # Contradiction — will backtrack on next iteration

            # Step 5: Check if all cusp cells are now embedded
            next_tr_idx = self.get_least_available_cusp_cell_idx()
            if next_tr_idx is None:
                self.process_completed()
                continue  # Will backtrack on next iteration to find more

            # Push a new frame for the next unembedded cusp cell
            self.stack.append(StackFrame(cusp_cell=self.traversal[next_tr_idx]))

        return "completed"
