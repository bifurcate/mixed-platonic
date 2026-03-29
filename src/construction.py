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

CUSP_CELL_MISMATCH = "cusp cell mismatch"
INCOMPATIBLE_FACE_PAIRING = "incompatible face pairing"
CUSP_SHAPE_INCOMPATIBLE = "cusp shape incompatible"
MISSING_SOURCE_EMBEDDING = "missing source embedding"
DISTINCT_INDUCED_EMBEDDINGS = "distinct induced embeddings"

## COMPOUND OBJECTS


class Cusp:
    def __init__(self):
        self.X = {}
        self.pairs = []

    def add_cell(self, cell: CuspCell):
        self.X[cell] = {}

    def pair(
        self,
        cusp_cell_src: CuspCell,
        edge_spec_src: EdgeSpec,
        cusp_cell_tgt: CuspCell,
        edge_spec_tgt: EdgeSpec,
    ):

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

    def get_cell_pairings(self, cusp_cell: CuspCell) -> dict[EdgeSpec, CuspEdgePairing]:
        return self.X.get(cusp_cell)

    def dump(self):
        return [tuple(cp) for cp in self.pairs]

    def load(self, data):
        for pairing in data:
            cp = cusp_edge_pairing_from_tuple(pairing)
            self.pair(
                cp.half_edge_src.cusp_cell,
                tuple(cp.half_edge_src.edge_spec),
                cp.half_edge_tgt.cusp_cell,
                tuple(cp.half_edge_tgt.edge_spec),
            )


class ManifoldCellulation:
    def __init__(self):
        self.X = {}
        self.pairs = []

    def add_cell(self, cell: ManifoldCell):
        self.X[cell] = {}

    def pair(
        self,
        manifold_cell_src: ManifoldCell,
        face_spec_src: FaceSpec,
        manifold_cell_tgt: CuspCell,
        face_spec_tgt: FaceSpec,
    ):

        face_spec_src, face_spec_tgt = normalize_face_pair(face_spec_src, face_spec_tgt)

        cp = ManifoldFacePairing(
            ManifoldHalfFace(manifold_cell_src, face_spec_src),
            ManifoldHalfFace(manifold_cell_tgt, face_spec_tgt),
        )

        # insert in both directions
        self.X[cp.half_face_src.manifold_cell][cp.half_face_src.face_spec] = cp
        self.X[cp.inv.half_face_src.manifold_cell][cp.inv.half_face_src.face_spec] = (
            cp.inv
        )

    def get_cell_pairings(
        self, manifold_cell: ManifoldCell
    ) -> dict[FaceSpec, ManifoldFacePairing]:
        return self.X.get(manifold_cell)


# TODO: make traversal a class
def dump_traversal(traversal):
    return [tuple(cell) for cell in traversal]


def load_traversal(data):
    return [cusp_cell_from_tuple(tuple(cell_tuple)) for cell_tuple in data]


class Embeddings:
    def __init__(self):
        self.X = {}
        self.Y = {}
        self.verts = {}

    def add_embedding(self, embedding: Embedding):
        m_cell = embedding.manifold_cell
        self.X.setdefault(m_cell, {})[embedding.cusp_cell] = embedding
        self.Y[embedding.cusp_cell] = embedding
        vert = embedding.embedding_spec[0]
        self.verts.setdefault(m_cell, {})[vert] = embedding

    def remove_embedding(self, embedding: Embedding):
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

    def remove_embedding_by_cusp_cell(self, cusp_cell: CuspCell):
        em = self.get_embedding_by_cusp_cell(cusp_cell)
        self.remove_embedding(em)

    def is_vert_embedded(self, manifold_cell, vert):
        d = self.verts.get(manifold_cell)
        return d is not None and vert in d

    def get_embeddings_by_manifold_cell(
        self, manifold_cell
    ) -> dict[CuspCell, Embedding]:
        return self.X.get(manifold_cell)

    def dump_embeddings_by_manifold_cell(self):
        s = ""
        for m_cell, d in self.X.items():
            s += f"{m_cell.short_str()}\n"
            for c_cell, em in d.items():
                s += f"  {c_cell.short_str()}: {em.short_str()}\n"
        return s

    def get_embedding_by_cusp_cell(self, cusp_cell) -> Embedding:
        return self.Y.get(cusp_cell)

    def dump_embeddings_by_cusp_cell(self):
        s = ""
        for c_cell, em in self.Y.items():
            s += f"  {c_cell.short_str()}: {em.short_str()}\n"
        return s

    def get_embeddings_by_verts(self, manifold_cell) -> dict[int, Embedding]:
        return self.verts.get(manifold_cell)

    def dump_embeddings_by_verts(self):
        s = ""
        for m_cell, d in self.verts.items():
            s += f"{m_cell.short_str()}\n"
            for vert_idx, em in d.items():
                s += f"  {vert_idx}: {em.short_str()}\n"
        return s

    def dump(self):
        return [tuple(em) for em in self.Y.values()]

    def load(self, data):
        for embedding_tuple in data:
            self.add_embedding(embedding_from_tuple(embedding_tuple))


def get_manifold_face_pairing(
    embedding_src: Embedding,
    embedding_tgt: Embedding,
    cusp_pairing: CuspEdgePairing,
):
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
):
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
):

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


# TODO: traversal concept does not need to be in construction. remove and adjust implementation


class Construction:
    def __init__(
        self,
        cusp: Cusp,
        embeddings: Embeddings,
        traversal: list[CuspCell] = [],
        num_tets=6,
        num_octs=2,
    ):
        self.cusp = cusp
        self.embeddings = embeddings
        self.traversal = traversal
        self.num_tets = num_tets
        self.num_octs = num_octs

    def find_face_pairing(
        self,
        manifold_half_face: ManifoldHalfFace,
    ):
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
        embedding_src: Embedding = None,
        cusp_edge_pairing: CuspEdgePairing = None,
    ):

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
    ):
        cusp_pairing = self.cusp.get_cell_pairings(cusp_half_edge_tgt.cusp_cell).get(
            cusp_half_edge_tgt.edge_spec
        )

        if cusp_pairing is None:
            return (None, None)

        cusp_half_edge_src = cusp_pairing.inv.half_edge_src
        return self.get_induced_embedding_from_src(cusp_half_edge_src)

    def get_induced_embeddings_for_cell(self, cusp_cell: CuspCell):
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

    def get_induced_embedding_for_cell(self, cusp_cell: CuspCell):
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

    def build_manifold_cellulation(self) -> ManifoldFacePairing:
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
