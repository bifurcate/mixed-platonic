from base import (
  EmbeddingType,
  Embedding,
  TET_TRI,
  OCT_SQR,
  Tetrahedron,
  Octahedron,
  TetTriEmbedding,
  OctSqrEmbedding,
  embedding_from_tuple,
)

from construction import (
  Embeddings,
  Construction,
)

class EmbeddingIterator:
  embedding_type: EmbeddingType = None
  manifold_cell_class = None
  num_verts = 0
  num_perms = 0

  def __init__(self, embeddings: Embeddings, num_manifold_cells: int):
    self.embeddings = embeddings
    self.num_manifold_cells = num_manifold_cells
    self.done = False
    self.cell_idx = 0
    self.vert_idx = 0
    self.perm_idx = 0

  def set(self, cell_idx, vert_idx, perm_idx):
    self.done = False
    self.cell_idx = cell_idx
    self.vert_idx = vert_idx
    self.perm_idx = perm_idx

    if self.is_current_vert_embedded():
      self.next()

  def reset(self):
    self.set(0, 0, 0)

  def is_current_vert_embedded(self):
    return self.embeddings.is_vert_embedded(
      self.manifold_cell_class(self.cell_idx),
      self.vert_idx,
    )

  def weak_next(self):
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
  
  def next(self):
    while True:
      self.weak_next()
      if not self.is_current_vert_embedded() or self.done:
        return self

class TetTriEmbeddingIterator(EmbeddingIterator):
  embedding_type: EmbeddingType = TET_TRI
  manifold_cell_class = Tetrahedron
  num_verts = 4
  num_perms = 6

  def __init__(self, embeddings: Embeddings, num_manifold_cells: int):
    super().__init__(embeddings, num_manifold_cells)

class OctSqrEmbeddingIterator(EmbeddingIterator):
  embedding_type: EmbeddingType = OCT_SQR
  manifold_cell_class = Octahedron
  num_verts = 6
  num_perms = 8

  def __init__(self, embeddings: Embeddings, num_manifold_cells: int):
    super().__init__(embeddings, num_manifold_cells)


INIT = 0
REGULAR = 1
INDUCED = 2

ENTRY_TYPE_SHORT_LABELS = {
  INIT: 'O',
  REGULAR: 'R',
  INDUCED: 'I',
}

EntryType = int

class Stack:
  def __init__(self, traversal, construction: Construction, num_tets, num_octs):
    self.stack = []
    self.construction = construction
    self.traversal = traversal
    self.tr_idx = None
    self.cusp_cell = None
    self.embedding = None
    self.entry_type = None
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
    self.done = False
    self.counter = 0
    # self.completed = []
    # self.iso_sigs = []

  def get_next_embedding(self):
    if self.cusp_cell.is_tri():
      embedding_class = TetTriEmbedding
      embedding_iterator = self.tet_tri_embedding_iterator
    else:
      embedding_class = OctSqrEmbedding
      embedding_iterator = self.oct_sqr_embedding_iterator

    if self.embedding is None:
      embedding_iterator.reset()
    else:
      cell_idx, vert_idx, perm_idx = self.embedding.get_iterator_indices()
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
        self.cusp_cell.cell_index,
        embedding_iterator.vert_idx,
        embedding_iterator.perm_idx,
      )
      return (init, next_embedding)

  def get_next_induced(self) -> tuple[bool, int, Embedding]:
    # TODO: make this more efficient, right now we check everything!
    for i, c in enumerate(self.traversal):
      existing_embedding = self.construction.embeddings.get_embedding_by_cusp_cell(c)

      try:
        # TODO: capture more info on violation type
        proposed_embedding = self.construction.get_induced_embedding_for_cell(c)
      except:
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
  def get_least_available_cusp_cell_idx(self):
    for idx, cusp_cell in enumerate(self.traversal):
      em = self.construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
      if em is None:
        return idx
    return None
  
  def load(self, input_stack: list[tuple[int, Embedding]]):
    for tp, em_tuple in input_stack:
      em = embedding_from_tuple(em_tuple)
      self.cusp_cell = em.cusp_cell
      self.embedding = em
      self.tr_idx = self.traversal.index(em.cusp_cell)
      self.entry_type = tp
      self.push_state()

  def dump(self):
    output_stack = []
    for tr_idx, tp in self.stack:
      cusp_cell = self.traversal[tr_idx]
      em = self.construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
      output_stack.append((tp, tuple(em)))
    return output_stack

  def pop_state(self):
    self.tr_idx, self.entry_type = self.stack.pop()
    self.cusp_cell = self.traversal[self.tr_idx]
    self.embedding = self.construction.embeddings.get_embedding_by_cusp_cell(self.cusp_cell)
    self.construction.embeddings.remove_embedding(self.embedding)

  def push_state(self):
    self.construction.embeddings.add_embedding(self.embedding)
    self.stack.append((self.tr_idx, self.entry_type))

  def rewind(self):
    while True:
      self.pop_state()
      if self.entry_type == REGULAR:
        break

  # def next_open_cell(self):
  #   self.tr_idx = self.get_least_available_cusp_cell_idx()
  #   self.cusp_cell = self.traversal[self.tr_idx]
  #   self.embedding = None
  #   self.entry_type = REGULAR

  # def next_embedding(self):
  #   embedding = self.get_next_embedding()

  #   if embedding is None:
  #     self.rewind()
  #     return
    
  #   self.embedding = embedding
  #   self.entry_type = REGULAR
  #   self.push_state()

  # def induce(self):
  #   while True:
  #     ok, tr_idx, next_embedding = self.get_next_induced()
  #     if not ok:
  #       self.rewind()
  #       break

  #     if next_embedding is not None:
  #       self.tr_idx = tr_idx
  #       self.embedding = next_embedding
  #       self.entry_type = INDUCED
  #       self.push_state()
  #     else:
  #       self.next_open_cell()

  # def next(self):
  #   while True:
  #     ok = self.next_embedding()
  #     if ok:
  #       self.induce()

  def pp_stack(self):
    s = ''
    for stack_entry in reversed(self.stack):
      tr_idx, tp = stack_entry
      cusp_cell = self.traversal[tr_idx]
      em = self.construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
      s += f"{tr_idx:3}, {ENTRY_TYPE_SHORT_LABELS[tp]}, {em.short_str()}\n"
    return s
  
  def pp_state(self):
    return f"{self.tr_idx: 3},  {ENTRY_TYPE_SHORT_LABELS[self.entry_type]}, {self.embedding.short_str()}\n"
  
  # def process_completed(self):
    # self.completed.append(self.dump())
    # manifold_cellulation = self.construction.build_manifold_cellulation()
    # regina_triangulation = to_regina_triangulation(manifold_cellulation, self.num_tets,self.num_octs)
    # self.iso_sigs.append(regina_triangulation.isoSig())
    # draw_stack([1, -1, 1, -1, 1, -1], self.construction, f"test_boyd_images/{self.counter:08}.png")

  def next_(self):

    ## TODO END and COMPLETE conditions
    # breakpoint()
    # induce
    while True:
      completed = None

      ok, tr_idx, next_embedding = self.get_next_induced()

      if not ok:
        self.rewind()
        break
 
      if next_embedding is None:
        # next_open_cell
        tr_idx = self.get_least_available_cusp_cell_idx()
        if tr_idx is None:
          # complete
          completed = self.dump()
          self.rewind()
          break
        else:
          self.tr_idx = tr_idx
          self.cusp_cell = self.traversal[tr_idx]
          self.embedding = None
          self.entry_type = REGULAR
          break
      else:
        self.tr_idx = tr_idx ## <--
        self.embedding = next_embedding
        self.entry_type = INDUCED
        self.push_state()

    # next_embedding
    while True:
      init, next_embedding = self.get_next_embedding()
      if next_embedding is None:
        # rewind
        while True:
          if len(self.stack) == 0:
            # done
            self.done = True
            break

          self.pop_state()
          if self.entry_type == REGULAR:
            break
      else:
        if init:
          self.entry_type = INIT
        else:
          self.entry_type = REGULAR
        self.embedding = next_embedding
        self.push_state()
        break
    
    self.counter += 1
    return completed