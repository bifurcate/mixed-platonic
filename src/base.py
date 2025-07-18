from typing import Optional
from functools import cached_property

### Basic Constants and Data objects

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

TET_VERT_PERMS = [ (i,j) for i in range(4) for j in range(6) ]
TET_PERM_LU = dict(zip(TET_VERT_PERMS, TET_PERMS))
TET_PERM_RV_LU = dict(zip(TET_PERMS, TET_VERT_PERMS))

OCT_VERT_PERMS = [ (i,j) for i in range(6) for j in range(8) ]
OCT_PERM_LU = dict(zip(OCT_VERT_PERMS, OCT_PERMS))
OCT_PERM_RV_LU = dict(zip(OCT_PERMS, OCT_VERT_PERMS))

TET_FACES = [
  (0,1,2),
  (0,1,3),
  (0,2,3),
  (1,2,3),
]

OCT_FACES = [
  (0,1,2),
  (0,1,4),
  (0,2,3),
  (0,3,4),
  (1,2,5),
  (1,4,5),
  (2,3,5),
  (3,4,5),
]

TRI_EDGES = [
  (1,2),
  (2,3),
  (1,2),
]

SQR_EDGES = [
  (1,2),
  (2,3),
  (3,4),
  (1,4),
]

TRI = 0
SQR = 1

CUSP_CELL_TYPE_LABEL = {
  None: 'CuspCell',
  SQR: 'Square',
  TRI: 'Triangle',
}

CuspCellType = Optional[int]
CuspCellIndex = int

class CuspCell:
  cell_type: CuspCellType = None

  def __init__(self, cell_index: CuspCellIndex):
    self.cell_index = cell_index

  def __repr__(self):
    return f"{CUSP_CELL_TYPE_LABEL[self.cell_type]}({self.cell_index})"
  
  def __hash__(self):
    return hash(tuple(self))

  def __eq__(self, other):
    return tuple(self) == tuple(other)

  def __iter__(self):
    yield self.cell_type
    yield self.cell_index

  def is_sqr(self):
    return self.cell_type == SQR
  
  def is_tri(self):
    return self.cell_type == TRI

class Triangle(CuspCell):
  cell_type: CuspCellType = TRI

  def __init__(self, cell_index: CuspCellIndex):
    super().__init__(cell_index)

Tri = Triangle

class Square(CuspCell):
  cell_type: CuspCellType = SQR
  
  def __init__(self, cell_index: CuspCellIndex):
    super().__init__(cell_index)

Sqr = Square

TET = 0
OCT = 1

MANIFOLD_CELL_TYPE_LABEL = {
  None: 'ManifoldCell',
  TET: 'Tetrahedron',
  OCT: 'Octahedron',
}

ManifoldCellType = Optional[int]
ManifoldCellIndex = int

class ManifoldCell:
  cell_type: ManifoldCellType = None

  def __init__(self, cell_index: ManifoldCellIndex):
    self.cell_index = cell_index

  def __repr__(self):
    return f"{MANIFOLD_CELL_TYPE_LABEL[self.cell_type]}({self.cell_index})"
  
  def __hash__(self):
    return hash(tuple(self))

  def __eq__(self, other):
    return tuple(self) == tuple(other)
  
  def __iter__(self):
    yield self.cell_type
    yield self.cell_index

  def is_tet(self):
    return self.cell_type == TET
  
  def is_oct(self):
    return self.cell_type == OCT

class Tetrahedron(ManifoldCell):
  cell_type: ManifoldCellType = TET
  
  def __init__(self, cell_index: ManifoldCellIndex):
    super().__init__(cell_index)

Tet = Tetrahedron

class Octahedron(ManifoldCell):
  cell_type: ManifoldCellType = OCT

  def __init__(self, cell_index: ManifoldCellIndex):
    super().__init__(cell_index)

Oct = Octahedron

EdgeSpec = tuple[int, int]

class CuspHalfEdge:
  def __init__(self, cusp_cell: CuspCell, edge_spec: EdgeSpec):
    self.cusp_cell = cusp_cell
    self.edge_spec = edge_spec

  def __iter__(self):
    yield tuple(self.cusp_cell)
    yield tuple(self.edge_spec)

  def __repr__(self):
    return f"CuspHalfEdge({repr(self.cusp_cell)}, {repr(self.edge_spec)})"
  
  def __hash__(self):
    return hash(tuple(self))

  def __eq__(self, other):
    return tuple(self) == tuple(other)
  
FaceSpec = tuple[int, int, int]

class ManifoldHalfFace:
  def __init__(self, manifold_cell: ManifoldCell, face_spec: FaceSpec):
    self.manifold_cell = manifold_cell
    self.face_spec = face_spec

  def __iter__(self):
    yield tuple(self.manifold_cell)
    yield tuple(self.face_spec)

  def __repr__(self):
    return f"ManifoldHalfFace({repr(self.manifold_cell)}, {repr(self.face_spec)})"
  
  def __hash__(self):
    return hash(tuple(self))

  def __eq__(self, other):
    return tuple(self) == tuple(other)
  

def normalize_edge_pair(edge_spec_source: EdgeSpec, edge_spec_target: EdgeSpec):
  if edge_spec_source[1] < edge_spec_source[0]:  
    return ((edge_spec_source[1], edge_spec_source[0]), (edge_spec_target[1], edge_spec_target[0]))
  else:
    return (edge_spec_source, edge_spec_target)


class CuspEdgePairing:
  def __init__(self, half_edge_src: CuspHalfEdge, half_edge_tgt: CuspHalfEdge):
    self.half_edge_src = half_edge_src
    self.half_edge_tgt = half_edge_tgt

  def __iter__(self):
    yield tuple(self.half_edge_src)
    yield tuple(self.half_edge_tgt)

  def __repr__(self):
    return f"CuspEdgePairing({repr(self.half_edge_src)}, {repr(self.half_edge_tgt)})"
  
  def __hash__(self):
    return hash(tuple(self))

  def __eq__(self, other):
    return tuple(self) == tuple(other)
  
  @cached_property
  def map(self):
    return dict(zip((0,) + self.half_edge_src.edge_spec, (0,) + self.half_edge_tgt.edge_spec))
    
  @cached_property
  def inv(self):
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

def normalize_face_pair(face_spec_src: FaceSpec, face_spec_tgt: FaceSpec):
  sort_indices = [i for i, _ in sorted(enumerate(face_spec_src), key=lambda x: x[1])]

  face_spec_src_ordered = tuple(face_spec_src[i] for i in sort_indices)
  face_spec_tgt_ordered = tuple(face_spec_tgt[i] for i in sort_indices)

  return (face_spec_src_ordered, face_spec_tgt_ordered)

class ManifoldFacePairing:
  def __init__(self, half_face_src: ManifoldHalfFace, half_face_tgt: ManifoldHalfFace):
    self.half_face_src = half_face_src
    self.half_face_tgt = half_face_tgt

  def __iter__(self):
    yield tuple(self.half_face_src)
    yield tuple(self.half_face_tgt)

  def __repr__(self):
    return f"ManifoldFacePairing({repr(self.half_face_src)}, {repr(self.half_face_tgt)})"
  
  def __hash__(self):
    return hash(tuple(self))

  def __eq__(self, other):
    return tuple(self) == tuple(other)
  
  @cached_property
  def map(self):
    return dict(zip(self.half_face_src.face_spec, self.half_face_tgt.face_spec))
  
  @cached_property
  def inv(self):
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
  None: 'Embedding',
  TET_TRI: 'TetTriEmbedding',
  OCT_SQR: 'OctSqrEmbedding',
}


EmbeddingType = Optional[int]

# be more specific
EmbeddingSpec = tuple

class Embedding:
  embedding_type: EmbeddingType = None

  def __init__(self,
    manifold_cell: ManifoldCell,
    cusp_cell: CuspCell,
    embedding_spec: EmbeddingSpec,
  ):
    self.manifold_cell = manifold_cell
    self.cusp_cell = cusp_cell
    self.embedding_spec = embedding_spec

    if None in embedding_spec:
      self.complete()

  def __iter__(self):
    yield self.embedding_type
    yield tuple(self.manifold_cell)
    yield tuple(self.cusp_cell)
    yield self.embedding_spec

  def __repr__(self):
    return f"{EMBEDDING_TYPE_LABEL[self.embedding_type]}({repr(self.manifold_cell)}, {repr(self.cusp_cell)}, {repr(self.embedding_spec)})"
  
  def __hash__(self):
    return hash(tuple(self))

  def __eq__(self, other):
    return tuple(self) == tuple(other)
  
  def is_tet_tri(self):
    return self.embedding_type == TET_TRI
  
  def is_oct_sqr(self):
    return self.embedding_type == OCT_SQR
  
  @cached_property
  def map(self):
    return dict(zip(
      range(len(self.embedding_spec)),
      self.embedding_spec,
    ))
  
  @cached_property
  def inv_map(self):
    return dict(zip(
      self.embedding_spec,
      range(len(self.embedding_spec)),
    ))

TetTriEmbeddingSpec = tuple[int, int, int, int]

class TetTriEmbedding(Embedding):
  embedding_type: EmbeddingType = TET_TRI

  def __init__(self,
    manifold_cell: Tetrahedron,
    cusp_cell: Triangle,
    embedding_spec: TetTriEmbeddingSpec,
  ):
    super().__init__(manifold_cell, cusp_cell, embedding_spec)
    
  def exposed(self, face_spec: FaceSpec) -> Optional[EdgeSpec]:
    indices = sorted((self.embedding_spec.index(i) for i in face_spec))

    if indices[0] == 0:
      return (indices[1], indices[2])
    else:
      return None
    
  def complete(self):
    em = list(self.embedding_spec)
    unknown_idx = -1
    X = [0,1,2,3]
    for i, v in enumerate(em):
      if v == None:
        unknown_idx = i
      else:
        X.remove(v)
    em[unknown_idx] = X[0]
    self.embedding_spec = tuple(em)

  def get_indices(self):
    return TET_PERM_RV_LU.get(self.embedding_spec)
  
  @classmethod
  def from_indices(cls, manifold_cell_idx, cusp_cell_idx, vert_idx, perm_idx):
    embedding_spec = TET_PERM_LU.get((vert_idx, perm_idx))
    if embedding_spec is None:
      raise ValueError('invalid indices')
    return cls(Tet(manifold_cell_idx), Tri(cusp_cell_idx), embedding_spec)

OctSqrEmbeddingSpec = tuple[int, int, int, int, int, int]

class OctSqrEmbedding(Embedding):
  embedding_type: EmbeddingType = OCT_SQR

  def __init__(self,
    manifold_cell: Octahedron,
    cusp_cell: Square,
    embedding_spec: OctSqrEmbeddingSpec,
  ):
    super().__init__(manifold_cell, cusp_cell, embedding_spec)
  
  def exposed(self, face_spec: FaceSpec) -> Optional[EdgeSpec]:
    indices = sorted((self.embedding_spec.index(i) for i in face_spec))

    if indices[0] == 0 and indices[2] != 5:
      diff = indices[2] - indices[1]
      if diff == 1 or diff == 3:
        return (indices[1], indices[2])
    else:
      return None
    
  def complete(self):

    # TODO: eliminate underfined behaviour
    em = list(self.embedding_spec)

    known_idx = [ i for i,v in enumerate(self.embedding_spec) if v is not None]

    for perm in OCT_PERMS:
      if all( perm[i] == em[i] for i in known_idx):
        self.embedding_spec = perm
        return
      
  def get_indices(self):
    return OCT_PERM_RV_LU.get(self.embedding_spec)
  
  @classmethod
  def from_indices(cls, manifold_cell_idx, cusp_cell_idx, vert_idx, perm_idx):
    embedding_spec = OCT_PERM_LU.get((vert_idx, perm_idx))
    if embedding_spec is None:
      raise ValueError('invalid indices')
    return cls(Oct(manifold_cell_idx), Sqr(cusp_cell_idx), embedding_spec)
  
# CHOICE = 0
# INDUCED = 1

# EntryType = int

# class StackEntry:
#   def __init__(self, embedding: Embedding, entry_type: EntryType):
#     self.embedding = embedding
#     self.entry_type = entry_type

# class Stack