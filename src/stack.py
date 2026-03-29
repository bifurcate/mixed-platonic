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
    embedding_type: EmbeddingType = None
    manifold_cell_class: type[ManifoldCell] | None = None
    num_verts: int = 0
    num_perms: int = 0

    def __init__(self, embeddings: Embeddings, num_manifold_cells: int) -> None:
        self.embeddings = embeddings
        self.num_manifold_cells = num_manifold_cells
        self._cells: list[ManifoldCell] = [self.manifold_cell_class(i) for i in range(num_manifold_cells)]
        self.done: bool = False
        self.cell_idx: int = 0
        self.vert_idx: int = 0
        self.perm_idx: int = 0

    def set(self, cell_idx: int, vert_idx: int, perm_idx: int) -> None:
        self.done = False
        self.cell_idx = cell_idx
        self.vert_idx = vert_idx
        self.perm_idx = perm_idx

        if self.is_current_vert_embedded():
            self.next()

    def reset(self) -> None:
        self.set(0, 0, 0)

    def is_current_vert_embedded(self) -> bool:
        return self.embeddings.is_vert_embedded(
            self._cells[self.cell_idx],
            self.vert_idx,
        )

    def weak_next(self) -> "EmbeddingIterator | None":
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
        while True:
            self.weak_next()
            if not self.is_current_vert_embedded() or self.done:
                return self


class TetTriEmbeddingIterator(EmbeddingIterator):
    embedding_type: EmbeddingType = TET_TRI
    manifold_cell_class: type[Tetrahedron] = Tetrahedron
    num_verts: int = 4
    num_perms: int = 6

    def __init__(self, embeddings: Embeddings, num_manifold_cells: int) -> None:
        super().__init__(embeddings, num_manifold_cells)


class OctSqrEmbeddingIterator(EmbeddingIterator):
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


class Stack:
    def __init__(self, traversal: list[CuspCell], construction: Construction, num_tets: int, num_octs: int) -> None:
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

    def get_next_embedding(self, cusp_cell: CuspCell, embedding: Embedding | None) -> tuple[bool, Embedding | None]:
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
        for idx, cusp_cell in enumerate(self.traversal):
            em = self.construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
            if em is None:
                return idx
        return None

    def process_completed(self) -> None:
        self.completed.append(self.construction.embeddings.dump())

    def run(self) -> None:
        tr_idx = (
            self.get_least_available_cusp_cell_idx()
        )  # maybe make this return embedding
        if tr_idx is None:
            self.process_completed()
            return

        cusp_cell = self.traversal[tr_idx]
        embedding = self.construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
        assert embedding is None

        while True:
            init, next_embedding = self.get_next_embedding(cusp_cell, embedding)
            if next_embedding is None:
                return

            embedding = next_embedding

            self.construction.embeddings.add_embedding(embedding)

            self.counter += 1

            induced_embeddings = []
            while True:
                ok, _, next_induced_embedding = self.get_next_induced()
                if not ok or next_induced_embedding is None:
                    break
                induced_embeddings.append(next_induced_embedding)
                self.construction.embeddings.add_embedding(next_induced_embedding)

            if ok:
                self.run()

            for ie in induced_embeddings:
                self.construction.embeddings.remove_embedding(ie)

            self.construction.embeddings.remove_embedding(embedding)

            if init:
                return
