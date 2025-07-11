from base import (
  SQR,
  TRI,
  TET_TRI,
  OCT_SQR,
  TET_PERMS,
  OCT_PERMS,
  Tri, 
  Sqr,
  Tet,
  Oct,
  Embedding,
  TetTriEmbedding,
  OctSqrEmbedding,
  CuspCell,
)

from construction import (
  Cusp,
  FingerCuspGenerator,
  Embeddings,
  Construction,
)

FIRST = 0
CHOICE = 1
INDUCED = 2


# TET_VERT_PERMS = [ (i,j) for i in range(4) for j in range(6) ]
# TET_PERM_LU = dict(zip(TET_VERT_PERMS, TET_PERMS))
# TET_PERM_RV_LU = dict(zip(TET_PERMS, TET_VERT_PERMS))

# OCT_VERT_PERMS = [ (i,j) for i in range(6) for j in range(8) ]
# OCT_PERM_LU = dict(zip(OCT_VERT_PERMS, OCT_PERMS))
# OCT_PERM_RV_LU = dict(zip(OCT_PERMS, OCT_VERT_PERMS))

# def to_embedding(
#   embedding_type,
#   cusp_cell_idx,
#   manifold_cell_idx,
#   vert_idx,
#   perm_idx,
# ):
#   if embedding_type == TET_TRI:
#     embedding_spec = TET_PERM_LU.get((vert_idx, perm_idx))
#   elif embedding_type == OCT_SQR:
#     embedding_spec = OCT_PERM_LU.get((vert_idx, perm_idx))
#   else:
#     raise ValueError('embedding_type must be TET_TRI or OCT_SQR')
  
#   if embedding_spec is None:
#     return None
  
#   if embedding_type == TET_TRI:
#     return TetTriEmbedding(Tet(manifold_cell_idx), Tri(cusp_cell_idx), embedding_spec)
#   elif embedding_type == OCT_SQR:
#     return OctSqrEmbedding(Oct(manifold_cell_idx), Sqr(cusp_cell_idx), embedding_spec)
  
# def from_embedding(embedding: Embedding):
#   if embedding.embedding_type == TET_TRI:
#     vert_idx, perm_idx = TET_PERM_RV_LU.get(embedding.embedding_spec)
#     return (TET_TRI, embedding.cusp_cell.cell_index, embedding.manifold_cell.cell_index, vert_idx, perm_idx)
#   elif embedding.embedding_type == OCT_SQR:
#     vert_idx, perm_idx = OCT_PERM_RV_LU.get(embedding.embedding_spec)
#     return (OCT_SQR, embedding.cusp_cell.cell_index, embedding.manifold_cell.cell_index, vert_idx, perm_idx)


# def to_cusp_cell(
#   cusp_cell_type,
#   cusp_cell_idx,
# ):
#   if cusp_cell_type == TRI:
#     return Tri(cusp_cell_idx)
#   elif cusp_cell_type == SQR:
#     return Sqr(cusp_cell_idx)
  
# def from_cusp_cell(cusp_cell: CuspCell):
#   return tuple(cusp_cell)

# EntryType = int

# class TetTriIter:
#   def __init__(self, table, n):
#     self.table = table
#     self.n = n
  
#   def __iter__(self):
#     for i in range(self.n):
#       for j in range(4):
#         for k in range(6):
#           if (i,j,k) in self.table:
#             continue
#           else:
#             yield (i,j,k)

# def tt_iter(n, tris = []):
#   manifold_cell_idx = 0
#   perm_idx = 0
#   vert_idx = 0
#   while True:
#     yield (manifold_cell_idx, vert_idx, perm_idx)
#     if perm_idx < 6:
#       perm_idx += 1
#     else:
#       perm_idx = 0
#       if vert_idx < 4:
#         vert_idx += 1
#       else:
#         vert_idx = 0
#         if manifold_cell_idx < n:
#           manifold_cell_idx += 1
#         else:
#           return
        
# def next_factory(num_verts, num_perms):
#   def next_func(n, idx, verts):
#     if idx is not None:
#       manifold_cell_idx, vert_idx, perm_idx = idx
#       if perm_idx < (num_perms - 1):
#         perm_idx += 1
#         return (manifold_cell_idx, vert_idx, perm_idx)
#       perm_idx = 0
#     else:
#       manifold_cell_idx = 0
#       vert_idx = 0
#       perm_idx = 0
#       if (manifold_cell_idx, vert_idx) not in verts:
#           return (manifold_cell_idx, vert_idx, perm_idx)
#     while True:
#       if vert_idx < (num_verts - 1):
#         vert_idx += 1
#         if (manifold_cell_idx, vert_idx) not in verts:
#           return (manifold_cell_idx, vert_idx, perm_idx)
#       else:
#         vert_idx = 0
#         if manifold_cell_idx < (n - 1):
#           manifold_cell_idx += 1
#           if (manifold_cell_idx, vert_idx) not in verts:
#             return (manifold_cell_idx, vert_idx, perm_idx)
#         else:
#           return None
#   return next_func


# def traversal(num_fingers):
#   for i in range(num_fingers):
#     yield (SQR, i)
#     yield (TRI, 2*i)
#     yield (TRI, 2*i + 1)


# tt_next = next_factory(4, 6)
# os_next = next_factory(6, 8)

# def next_1(
#     num_tets,
#     num_octs,
#     trvsl,
#     stack,
#     cusp_cell_map,
#     tet_verts,
#     oct_verts
# ):
#   if not stack:
#     tr_idx = 0
#   else:
#     tr_idx, _ = stack.pop()
  
#   entry = cusp_cell_map.get(tr_idx)
#   tr_cusp_cell_type, _ = trvsl[tr_idx]

#   if entry == None:
#     if tr_cusp_cell_type == TET_TRI:
#       manifold_cell_idx, vert_idx, perm_idx = os_next(num_tets, None, tet_verts)
#       tet_verts.append((manifold_cell_idx, vert_idx))

#     elif tr_cusp_cell_type == OCT_SQR:
#       manifold_cell_idx, vert_idx, perm_idx = os_next(num_octs, None, oct_verts)
#       oct_verts.append((manifold_cell_idx, vert_idx))
#     else:
#       raise ValueError('cusp cell type must be TRI or SQR')
    
#     cusp_cell_map[tr_idx] = (manifold_cell_idx, vert_idx, perm_idx)
#     stack.append((tr_idx, FIRST))
#   else:
#     manifold_cell_idx, vert_idx, perm_idx = entry
#     if tr_cusp_cell_type == TET_TRI:
#       tet_verts.remove((manifold_cell_idx, vert_idx))
#       manifold_cell_idx, vert_idx, perm_idx = os_next(num_tets, entry, tet_verts)
#       tet_verts.append((manifold_cell_idx, vert_idx))

#     elif tr_cusp_cell_type == OCT_SQR:
#       oct_verts.remove((manifold_cell_idx, vert_idx))
#       manifold_cell_idx, vert_idx, perm_idx = os_next(num_octs, entry, oct_verts)
#       oct_verts.append((manifold_cell_idx, vert_idx))
#     else:
#       raise ValueError('cusp cell type must be TRI or SQR')
    
#     cusp_cell_map[tr_idx] = (manifold_cell_idx, vert_idx, perm_idx)
#     stack.append((tr_idx, CHOICE))

# # class Stack:
# #   def __init__(self, construction):
# #     self.construction = construction
# #     self.X = []

# #   def add_embedding(self, embedding: Embedding, entry_type: EntryType):
# #     self.X.append((embedding, entry_type))

# #   def rewind(self):
# #     embedding, entry_type = self.X.pop()
# #     while entry_type != INDUCED:
# #       embedding, entry_type = self.X.pop()
# #     self.X.append((embedding, entry_type))

# #   def induce(self):
# #     ...


# # [TET_TRI, TRI_IDX, TET_IDX, VERT_IDX, PERM_IDX]
# # [OCT_SQR, SQR_IDX, OCT_IDX, VERT_IDX, PERM_IDX]




# class Stack:
#   def __init__(self, num_tri, num_sqr, num_tet, num_oct):
#     self.num_tri = num_tri
#     self.num_sqr = num_sqr
#     self.num_tet = num_tet
#     self.num_oct = num_oct
#     self.tris = []
#     self.sqrs = []



# # class Stack:
# #   def __init__(self, num_tri, num_sqr, num_tet, num_tri):
# #     self.num_tri = num_tri
# #     self.num_sqr = num_sqr
# #     self.num_tet = num_tet
# #     self.stack = []

# #   def next(self):
# #     e = self.stack.pop()
# #     tp, cusp_cell_idx, manifold_cell_idx, vert_idx, perm_idx = e

#     # if tp == TET_TRI:
#     #   if perm_idx < 6:
#     #     perm_idx += 1
#     #   else:
#     #     perm_idx = 0
#     #     if vert_idx < 4:
#     #       vert_idx += 1
#     #     else:
#     #       vert_idx = 0
#     #       if manifold_cell_idx < self.num_tet:
#     #         manifold_cell_idx += 1
#     #       else:
#     #         ## DONE
#     #         ...
#     # elif tp == OCT_SQR:
#     #         if perm_idx < 6:
#     #     perm_idx += 1
#     #   else:
#     #     perm_idx = 0
#     #     if vert_idx < 4:
#     #       vert_idx += 1
#     #     else:
#     #       vert_idx = 0
#     #       if manifold_cell_idx < self.num_tet:
#     #         manifold_cell_idx += 1
#     #       else:
#     #         ## DONE
#     #         ...

def foo():

  # finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  # cusp = FingerCuspGenerator(finger_pattern).generate()
  # embeddings = Embeddings()

  # def tr_gen(num_fingers):
  #   for i in range(num_fingers):
  #     yield Sqr(i)
  #     yield Tri(2*i)
  #     yield Tri(2*i + 1)

  # traversal = list(tr_gen(12))

  # construction = Construction(cusp, embeddings, traversal)

  # tr_idx = construction.get_least_available_cusp_cell_idx()

  # stack = []

  # while tr_idx is not None:

  #   try:
  #     while True:
  #       induced_embedding = construction.induce()
  #       if induced_embedding is None:
  #         break
  #       stack.append((induced_embedding, INDUCED))
  #       yield stack
  #   except ValueError:
  #     # rollback induced
  #     while True:
  #       em, tp = stack.pop()
  #       if tp != INDUCED:
  #         stack.append((em, tp))
  #         break
  #       else:
  #         yield stack
  #         embeddings.remove_embedding(em)
        
  #   while True:
  #     tr_idx = construction.get_least_available_cusp_cell_idx()
  #     cusp_cell = traversal[tr_idx]
  #     chosen_embedding = construction.choose(cusp_cell)
      
  #     if chosen_embedding is None:
  #       # pop choice and rollback induced
  #       em, tp = stack.pop()
  #       if tp != CHOICE:
  #         raise ValueError('inconsistent stack')
  #       embeddings.remove_embedding(em)
  #       while True:
  #         em, tp = stack.pop()
  #         if tp != INDUCED:
  #           stack.append((em, tp))
  #           break
  #         else:
  #           yield stack
  #           embeddings.remove_embedding(em)
  #     else:
  #       yield stack
  #       stack.append(chosen_embedding, CHOICE)
  #       break


  # CHOICE = 0
  # INDUCED = 1

  # finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
  # cusp = FingerCuspGenerator(finger_pattern).generate()
  # embeddings = Embeddings()

  # def tr_gen(num_fingers):
  #   for i in range(num_fingers):
  #     yield Sqr(i)
  #     yield Tri(2*i)
  #     yield Tri(2*i + 1)

  # traversal = list(tr_gen(12))

  # construction = Construction(cusp, embeddings, traversal)

  # tr_idx = construction.get_least_available_cusp_cell_idx()

  # stack = []

  # breakpoint()
  # while tr_idx is not None:

  #   try:
  #     while True:
  #       induced_embedding = construction.induce()
  #       if induced_embedding is None:
  #         tr_idx = construction.get_least_available_cusp_cell_idx()
  #         cusp_cell = traversal[tr_idx]
  #         break
  #       stack.append((induced_embedding, INDUCED))
  #   except ValueError:
  #     # rollback induced
  #     while True:
  #       em, tp = stack[-1]
  #       if tp == INDUCED:
  #         stack.pop()
  #         embeddings.remove_embedding(em)
  #       else:
  #         break

  #   while True:
  #     chosen_embedding = construction.choose(cusp_cell)
      
  #     if chosen_embedding is None:
  #       # pop choice and rollback induced
  #       em, tp = stack.pop()
  #       if tp != CHOICE:
  #         raise ValueError('inconsistent stack')
  #       embeddings.remove_embedding(em)
  #       while True:
  #         em, tp = stack[-1]
  #         if tp == INDUCED:
  #           stack.pop()
  #           embeddings.remove_embedding(em)
  #         else:
  #           break
  #       em, _ = stack[-1]
  #       cusp_cell = em.cusp_cell
  #     else:
  #       stack.append((chosen_embedding, CHOICE))
  #       em, _ = stack[-1]
  #       cusp_cell = em.cusp_cell
  #       break
      




  # num_tets = 6
  # num_octs = 2
  # stack = []
  # cusp_cell_map = {}
  # tet_verts = []
  # oct_verts = []

  # next_1(num_tets, num_octs, finger_traversal, stack, cusp_cell_map, tet_verts, oct_verts)

  # tr_idx, entry_type = stack[-1]
  # cusp_cell_type, cusp_cell_idx = finger_traversal[tr_idx]
  # manifold_cell_idx, vert_idx, perm_idx = cusp_cell_map.get(tr_idx)
  # new_embedding = to_embedding(
  #   cusp_cell_type,
  #   cusp_cell_idx,
  #   manifold_cell_idx,
  #   vert_idx,
  #   perm_idx
  # )
  # embeddings.add_embedding(new_embedding)

  # change = True
  # violation = False

  # while change and not violation:
  #   for i in finger_traversal:
  #     cusp_cell_type, cusp_cell_idx = finger_traversal[i]
  #     cusp_cell = to_cusp_cell(cusp_cell_type, cusp_cell_idx)
  #     existing_embedding = embeddings.get_embedding_by_cusp_cell(cusp_cell)
  #     try: 
  #       proposed_embedding = construction.get_induced_embeddings_for_cell(cusp_cell)
  #     except ValueError:
  #       violation = True
  #       break

  #     if existing_embedding is None:
  #       embeddings.add_embedding(proposed_embedding)

  # if violation:
  #   rewind()

  

      



  


  
