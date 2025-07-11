from base import (
  TRI_EDGES,
  SQR_EDGES,
  TET_PERMS,
  OCT_PERMS,
  Tet,
  Oct,
  Tri,
  Sqr,
  CuspCell,
  ManifoldCell,
  EdgeSpec,
  CuspHalfEdge,
  ManifoldHalfFace,
  CuspEdgePairing,
  ManifoldFacePairing,
  TetTriEmbedding,
  OctSqrEmbedding,
  Embedding,
  normalize_edge_pair,
  normalize_face_pair,
)

## COMPOUND OBJECTS

class Cusp:
  def __init__(self):
    self.X = {}

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
    
    # insert in both directions
    self.X[cp.half_edge_src.cusp_cell][cp.half_edge_src.edge_spec] = cp
    self.X[cp.inv.half_edge_src.cusp_cell][cp.inv.half_edge_src.edge_spec] = cp.inv

  def get_cell_pairings(self, cusp_cell: CuspCell) -> dict[EdgeSpec, CuspEdgePairing]:
    return self.X.get(cusp_cell)
  
# TODO: be more specific with the type here
FingerPattern = list[int]

class FingerCuspGenerator:
  def __init__(self, finger_pattern: FingerPattern):
    self.cusp = Cusp()
    self.finger_pattern = finger_pattern
    self.current_idx = 0

  def add_finger(self, idx):
    sqr0 = Sqr(idx)
    tri0 = Tri(2 * idx)
    tri1 = Tri(2 * idx + 1)

    self.cusp.add_cell(sqr0)
    self.cusp.add_cell(tri0)
    self.cusp.add_cell(tri1)

    self.cusp.pair(
      sqr0, (2, 3),
      tri0, (1, 3),
    )

    self.cusp.pair(
      tri0, (2, 3),
      tri1, (2, 1),
    )

    self.cusp.pair(
      tri1, (2, 3),
      sqr0, (1, 4),
    )

  def connect_fingers_pos(self, idx_src, idx_tgt):
    self.cusp.pair(
      Sqr(idx_src), (3, 4), 
      Sqr(idx_tgt), (2, 1),
    )

    self.cusp.pair(
      Tri(2 * idx_src + 1), (1, 3),
      Tri(2 * idx_tgt),     (1, 2)
    )
  
  def connect_fingers_neg(self, idx_src, idx_tgt):
    self.cusp.pair(
      Sqr(idx_src),     (3, 4),
      Tri(2 * idx_tgt), (1, 2),
    )

    self.cusp.pair(
      Tri(2 * idx_src + 1), (1, 3),
      Sqr(idx_tgt),         (2, 1),
    )
  
  def generate(self) -> Cusp:
    n = len(self.finger_pattern)
    for i in range(n):
      self.add_finger(i)
    
    for i in range(n-1):
      if self.finger_pattern[i] == self.finger_pattern[i+1]:
        self.connect_fingers_pos(i, i+1)
      else:
        self.connect_fingers_neg(i, i+1)
    
    if self.finger_pattern[n-1] == self.finger_pattern[0]:
      self.connect_fingers_pos(n-1, 0)
    else:
      self.connect_fingers_neg(n-1, 0)
      
    return self.cusp
  
  def traversal(self):
    for i in range(len(self.finger_pattern)):
      yield Sqr(i)
      yield Tri(2*i)
      yield Tri(2*i + 1)

class Embeddings:
  def __init__(self):
    self.X = {}
    self.Y = {}
    self.verts = {}

  def add_embedding(self, embedding: Embedding):
    if self.X.get(embedding.manifold_cell) == None:
      self.X[embedding.manifold_cell] = {}

    self.X[embedding.manifold_cell][embedding.cusp_cell] = embedding
    self.Y[embedding.cusp_cell] = embedding

    if self.verts.get(embedding.manifold_cell) == None:
      self.verts[embedding.manifold_cell] = {}
    
    # TODO: make vert a method on embedding
    vert = embedding.embedding_spec[0]
    self.verts[embedding.manifold_cell][vert] = embedding

  def remove_embedding(self, embedding: Embedding):
    d = self.X.get(embedding.manifold_cell)
    if d != None:
      d.pop(embedding.cusp_cell, None)
      if not d:
        self.X.pop(embedding.manifold_cell)
    
    self.Y.pop(embedding.cusp_cell, None)

    vert = embedding.embedding_spec[0]
    d = self.verts.get(embedding.manifold_cell)
    if d != None:
      d.pop(vert, None)
      if not d:
        self.verts.pop(embedding.manifold_cell)

  def is_vert_embedded(self, manifold_cell, vert):
    d = self.verts.get(manifold_cell, None)
    if d is None:
      return False
    
    return vert in d.keys()
  
  def get_embeddings_by_manifold_cell(self, manifold_cell) -> dict[CuspCell, Embedding]:
    return self.X.get(manifold_cell)

  def get_embedding_by_cusp_cell(self, cusp_cell) -> Embedding:
    return self.Y.get(cusp_cell)
  
  def get_embeddings_by_verts(self, manifold_cell) -> dict[int, Embedding]:
    return self.verts.get(manifold_cell)
  

def get_manifold_face_pairing(
  embedding_src: Embedding,
  embedding_tgt: Embedding,
  cusp_pairing: CuspEdgePairing,
):
  cusp_half_edge_src = cusp_pairing.half_edge_src
  cusp_cell_src = cusp_half_edge_src.cusp_cell
  edge_spec_src = cusp_half_edge_src.edge_spec

  cusp_half_edge_tgt = cusp_pairing.half_edge_tgt
  cusp_cell_tgt = cusp_half_edge_tgt.cusp_cell

  domain = (0,) + edge_spec_src
  face_spec_src = tuple(embedding_src.map.get(i) for i in domain)
  face_spec_tgt = tuple(embedding_tgt.map.get(cusp_pairing.map.get(i)) for i in domain)
  
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
    raise ValueError('embedding cusp cell must match cusp half edge cell')
  
  domain = (0,) + cusp_half_edge.edge_spec
  face_spec = tuple(sorted(embedding.map.get(i) for i in domain))
  
  return ManifoldHalfFace(
    embedding.manifold_cell,
    face_spec,
  )

def get_embedding_tgt(
    manifold_face_pairing: ManifoldFacePairing,
    cusp_edge_pairing: CuspEdgePairing,
    embedding_src: Embedding,
):
  
  if manifold_face_pairing.half_face_src != get_manifold_half_face(embedding_src, cusp_edge_pairing.half_edge_src):
    raise ValueError('incompatible')
  
  if cusp_edge_pairing.half_edge_tgt.cusp_cell.is_sqr() and manifold_face_pairing.half_face_tgt.manifold_cell.is_tet():
    raise ValueError('cusp shape incompatible')
  
  if cusp_edge_pairing.half_edge_tgt.cusp_cell.is_tri() and manifold_face_pairing.half_face_tgt.manifold_cell.is_oct():
    raise ValueError('cusp shape incompatible')

  half_edge_tgt = cusp_edge_pairing.half_edge_tgt

  domain = []
  if cusp_edge_pairing.half_edge_tgt.cusp_cell.is_tri():
    n = 4
  else:
    n = 6

  for i in range(n):
    if i in (0,) + half_edge_tgt.edge_spec:
      domain.append(i)
    else:
      domain.append(None)

      
  embedding_spec_tgt = []
  for i in domain:
    embedding_spec_tgt.append(manifold_face_pairing.map.get(
      embedding_src.map.get(
        cusp_edge_pairing.inv.map.get(i)
      )
    ))

  if cusp_edge_pairing.half_edge_tgt.cusp_cell.is_tri():
    return TetTriEmbedding(
      manifold_face_pairing.half_face_tgt.manifold_cell,
      cusp_edge_pairing.half_edge_tgt.cusp_cell,
      tuple(embedding_spec_tgt)
    )
  else:
    return OctSqrEmbedding(
      manifold_face_pairing.half_face_tgt.manifold_cell,
      cusp_edge_pairing.half_edge_tgt.cusp_cell,
      tuple(embedding_spec_tgt)
    )
  
CHOICE = 0
INDUCED = 1

def stack_to_str(stack):
  s = ''
  for em, tp in stack:
    s += '['
    if tp == CHOICE:
      s += 'C'
    elif tp == INDUCED:
      s += 'I'
    if em.is_tet_tri():
      s += f", Tri({em.cusp_cell.cell_index}), Tet({em.manifold_cell.cell_index}), {em.embedding_spec}], "
    elif em.is_oct_sqr():
      s += f", Sqr({em.cusp_cell.cell_index}), Oct({em.manifold_cell.cell_index}), {em.embedding_spec}], "
  s = s[:-2]
  return s

class Construction():
  def __init__(self, cusp: Cusp, embeddings: Embeddings, traversal: list[CuspCell] = [], num_tets = 6, num_octs = 2):
    self.cusp = cusp
    self.embeddings = embeddings
    self.traversal = traversal
    self.num_tets = num_tets
    self.num_octs = num_octs
    self.stack = []
    self.exc_state = 'init'
    self.completed_stacks = []

  def find_face_pairing(
    self,
    manifold_half_face: ManifoldHalfFace,
  ):
    manifold_cell = manifold_half_face.manifold_cell
    face_spec = manifold_half_face.face_spec
    
    ems = self.embeddings.get_embeddings_by_manifold_cell(manifold_cell)

    for cusp_cell, embedding_src in ems.items():
      edge_spec = embedding_src.exposed(face_spec)
      if edge_spec is None:
        continue

      pairings = self.cusp.get_cell_pairings(cusp_cell)
      cusp_pairing = pairings[edge_spec]
      if cusp_pairing is None:
        continue
      
      embedding_tgt = self.embeddings.get_embedding_by_cusp_cell(cusp_pairing.half_edge_tgt.cusp_cell)
      if embedding_tgt is None:
        continue
      
      return get_manifold_face_pairing(embedding_src, embedding_tgt, cusp_pairing)

  def get_induced_embedding_from_src(
      self,
      cusp_half_edge_src: CuspHalfEdge,
  ):
    
    embedding_src = self.embeddings.get_embedding_by_cusp_cell(
      cusp_half_edge_src.cusp_cell
    )

    if embedding_src is None:
      raise ValueError('source cusp cell must have embedding')
    
    cusp_edge_pairing = (
      self.cusp
      .get_cell_pairings(cusp_half_edge_src.cusp_cell)
      .get(cusp_half_edge_src.edge_spec)
    )

    if cusp_edge_pairing is None:
      return None
    
    manifold_half_face_src = get_manifold_half_face(
      embedding_src,
      cusp_half_edge_src,
    )

    if manifold_half_face_src is None:
      return None

    manifold_face_pairing = self.find_face_pairing(
      manifold_half_face_src,
    )

    if manifold_face_pairing is None:
      return None

    embedding_tgt = get_embedding_tgt(
      manifold_face_pairing,
      cusp_edge_pairing,
      embedding_src
    )

    if embedding_tgt is None:
      return None

    return embedding_tgt

  def get_induced_embedding_from_tgt(
    self,
    cusp_half_edge_tgt: CuspHalfEdge,
  ):
    cusp_pairing = (
      self.cusp
      .get_cell_pairings(cusp_half_edge_tgt.cusp_cell)
      .get(cusp_half_edge_tgt.edge_spec)
    )

    if cusp_pairing is None:
      return None

    cusp_half_edge_src = cusp_pairing.inv.half_edge_src
    return self.get_induced_embedding_from_src(cusp_half_edge_src)

  def get_induced_embeddings_for_cell(self, cusp_cell: CuspCell):
    if cusp_cell.is_tri():
      edges = TRI_EDGES
    elif cusp_cell.is_sqr():
      edges = SQR_EDGES
      
    possible_embeddings: dict[EdgeSpec, Embedding] = {}
    pairings = self.cusp.get_cell_pairings(cusp_cell)
    for e in edges:
      pairing = pairings.get(e)
      if pairing is None:
        continue
      
      neighbor_embedding = self.embeddings.get_embedding_by_cusp_cell(pairing.half_edge_tgt.cusp_cell)
      if neighbor_embedding is None:
        continue

      induced_embedding = self.get_induced_embedding_from_tgt(pairing.half_edge_src)
      possible_embeddings[e] = induced_embedding
    return possible_embeddings
  
  def get_induced_embedding_for_cell(self, cusp_cell: CuspCell):
    possible_embeddings = self.get_induced_embeddings_for_cell(cusp_cell)
    if not possible_embeddings:
      return None
    
    embedding_values = list(possible_embeddings.values())

    if len(set(embedding_values)) != 1:
      raise ValueError('distinct induced embeddings')
    
    return embedding_values[0]
  
  
  def is_complete(self):
    return (self.get_least_available_cusp_cell_idx() is None)
  
  def get_least_available_cusp_cell_idx(self):
    for idx, cusp_cell in enumerate(self.traversal):
      em = self.embeddings.get_embedding_by_cusp_cell(cusp_cell)
      if em is None:
        return idx
    return None

  def induce_one(self):
    # TODO: make this more efficient, right now we check everything!
    for cusp_cell in self.traversal:
      existing_embedding = self.embeddings.get_embedding_by_cusp_cell(cusp_cell)

      proposed_embedding = self.get_induced_embedding_for_cell(cusp_cell)

      if proposed_embedding is None:
        continue

      if existing_embedding is None:
          self.push_embedding(proposed_embedding, INDUCED)
          return proposed_embedding
      else:
        if existing_embedding != proposed_embedding:
          raise ValueError('embedding inconsistency')
        
  def induce(self):
    while True:
      induced_embedding = self.induce_one()
      if induced_embedding is None:
        break

  def get_next_embedding(self, cusp_cell: CuspCell):
    cusp_cell_idx = cusp_cell.cell_index
    if cusp_cell.is_tri():
      MCell = Tet
      Emb = TetTriEmbedding
      num_manifold_cells = self.num_tets
      num_verts = 4
      num_perms = 6

    elif cusp_cell.is_sqr():
      MCell = Oct
      Emb = OctSqrEmbedding
      num_manifold_cells = self.num_octs
      num_verts = 6
      num_perms = 8

    em = self.embeddings.get_embedding_by_cusp_cell(cusp_cell)

    if em is None:
      manifold_cell_idx = 0
      vert_idx = 0
      perm_idx = 0
      if not self.embeddings.is_vert_embedded(MCell(manifold_cell_idx), vert_idx):
          return Emb.from_indices(manifold_cell_idx, cusp_cell_idx, vert_idx, perm_idx)
    else:
      vert_idx, perm_idx = em.get_indices()
      manifold_cell_idx = em.manifold_cell.cell_index
      if perm_idx < (num_perms - 1):
        perm_idx += 1
        return Emb.from_indices(manifold_cell_idx, cusp_cell_idx, vert_idx, perm_idx)
      perm_idx = 0
      
    while True:
      if vert_idx < (num_verts - 1):
        vert_idx += 1
        if not self.embeddings.is_vert_embedded(MCell(manifold_cell_idx), vert_idx):
          return Emb.from_indices(manifold_cell_idx, cusp_cell_idx, vert_idx, perm_idx)
      else:
        vert_idx = 0
        if manifold_cell_idx < (num_manifold_cells - 1):
          manifold_cell_idx += 1
          if not self.embeddings.is_vert_embedded(MCell(manifold_cell_idx), vert_idx):
            return Emb.from_indices(manifold_cell_idx, cusp_cell_idx, vert_idx, perm_idx)
        else:
          return None
        
  def choose(self, cusp_cell: CuspCell):
    em = self.get_next_embedding(cusp_cell)
    if self.embeddings.get_embedding_by_cusp_cell(cusp_cell) is not None:
      self.pop_embedding()
    if em is None:
      return None
    self.push_embedding(em, CHOICE)
    return em
  
  def push_embedding(self, embedding: Embedding, stack_type: int):
    self.stack.append((embedding, stack_type))
    self.embeddings.add_embedding(embedding)
  
  def pop_embedding(self):
    if not self.stack:
      return None
    em, tp = self.stack.pop()
    self.embeddings.remove_embedding(em)
    return (em, tp)
  
  def peek_embedding(self):
    return (self.stack[-1] if self.stack else None)
  
  def init_stack(self):
    cusp_cell = self.traversal[0]
    self.choose(cusp_cell)

  def rewind(self):
    while True:
      em, tp = self.peek_embedding()
      if tp == INDUCED:
        self.pop_embedding()
      else:
        break
  
  def load_stack(self, input_stack):
    # this assumes the construction has just been initialized
    for em, tp in input_stack:
      self.push_embedding(em, tp)
  
  def stack_to_str(self):
    s = stack_to_str(self.stack)
    s += f" ! {self.exc_state}"
    return s

  def next(self):
    if not self.stack:
      self.init_stack()
      return
    
    try:
      self.induce()
      tr_idx = self.get_least_available_cusp_cell_idx()
      if tr_idx is None:
        self.completed_stacks.append(self.stack[:])
        raise ValueError('complete')
      cusp_cell = self.traversal[tr_idx]
    except ValueError as e:
      self.exc_state = str(e)
      self.rewind()
      em, tp = self.peek_embedding()
      cusp_cell = em.cusp_cell

    while True:
      chosen_embedding = self.choose(cusp_cell)
      if chosen_embedding is None:
        self.rewind()
        em, tp = self.peek_embedding()
        cusp_cell = em.cusp_cell
      else:
        break
    


