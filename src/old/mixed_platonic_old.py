TRI = 0
SQR = 1

TET = 0
OCT = 1

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

def is_oct(cell):
  return cell[0] == OCT

def is_tet(cell):
  return cell[0] == TET

def is_tri(cell):
  return cell[0] == TRI

def is_sqr(cell):
  return cell[0] == SQR

def normalize_identification(edge1, edge2):
  if edge1[1] < edge1[0]:  
    return ((edge1[1], edge1[0]), (edge2[1], edge2[0]))
  else:
    return (edge1, edge2)
  
def identify(cusp, cell1, edge1, cell2, edge2):
  n_edge1, n_edge2 = normalize_identification(edge1, edge2)
  cusp[cell1][n_edge1] = (cell2, n_edge2)
  m_edge2, m_edge1 = normalize_identification(edge2, edge1)
  cusp[cell2][m_edge2] = (cell1, m_edge1)

def add_new_cell(cusp, cell):
  cusp[cell] = {}

def add_finger(cusp, idx):
  a = (SQR, idx)
  b = (TRI, 2 * idx)
  c = (TRI, 2 * idx + 1)

  add_new_cell(cusp,a)
  add_new_cell(cusp,b)
  add_new_cell(cusp,c)

  identify(cusp, a, (2,3), b, (1,3))
  identify(cusp, b, (2,3), c, (2,1))
  identify(cusp, c, (2,3), a, (1,4))

def connect_fingers_pos(cusp, idx_a, idx_b):
  identify(cusp, (SQR, idx_a), (3, 4), (SQR, idx_b), (2,1))
  identify(cusp, (TRI, 2 * idx_a + 1), (1, 3), (TRI, 2 * idx_b), (1, 2))

def connect_fingers_neg(cusp, idx_a, idx_b):
  identify(cusp, (SQR, idx_a), (3, 4), (TRI, 2 * idx_b), (1,2))
  identify(cusp, (TRI, 2 * idx_a + 1), (1, 3), (SQR, idx_b), (2, 1))

def build_fingered_cusp(finger_pattern):
  cusp = {}
  n = len(finger_pattern)
  for i in range(n):
    add_finger(cusp, i)
  
  for i in range(n-1):
    if finger_pattern[i] == finger_pattern[i+1]:
      connect_fingers_pos(cusp, i, i+1)
    else:
      connect_fingers_neg(cusp, i, i+1)
  
  if finger_pattern[n-1] == finger_pattern[0]:
    connect_fingers_pos(cusp, n-1, 0)
  else:
    connect_fingers_neg(cusp, n-1, 0)
  
  return cusp

def embed_octahedron(
  cusp,
  cellulation_embeddings,
  cusp_embeddings,
  octahedron,
  square,
  embedding
):
  vertex_at_infinity = embedding[0]
  cellulation_embeddings[octahedron][vertex_at_infinity] = (square, embedding)
  cusp_embeddings[square] = (octahedron, embedding)

def embed_tetrahedron(
  cusp,
  cellulation_embeddings,
  cusp_embeddings,
  tetrahedron,
  triangle,
  embedding
):
  vertex_at_infinity = embedding[0]
  cellulation_embeddings[tetrahedron][vertex_at_infinity] = (triangle, embedding)
  cusp_embeddings[triangle] = (tetrahedron, embedding)


def infer_face_pairing(
  cusp,
  cusp_embeddings,
  cusp_cell,
  cusp_edge,
):
  other_cusp_cell, other_cusp_edge = cusp[cusp_cell][cusp_edge]

  cusp_embedding = cusp_embeddings[cusp_cell]
  if cusp_embedding is None:
    return None
  manifold_cell, embedding = cusp_embedding

  other_cusp_embedding = cusp_embeddings[other_cusp_cell]
  if other_cusp_embedding is None:
    return None
  other_manifold_cell, other_embedding = other_cusp_embedding

  half_face_self_unordered = (embedding[0], embedding[cusp_edge[0]], embedding[cusp_edge[1]])
  half_face_other_unordered = (other_embedding[0], other_embedding[other_cusp_edge[0]], other_embedding[other_cusp_edge[1]])

  # order the pairing
  # TODO: make a normalize function for this, like in edge case
  sort_indices = [i for i, _ in sorted(enumerate(half_face_self_unordered), key=lambda x: x[1])]

  half_face_self_ordered = tuple(half_face_self_unordered[i] for i in sort_indices)
  half_face_other_ordered = tuple(half_face_other_unordered[i] for i in sort_indices)

  return (manifold_cell, half_face_self_ordered, other_manifold_cell, half_face_other_ordered)


def complete_tet_embedding_map(embedding_map):
  # TODO: handle undefined behaviour
  em = list(embedding_map)
  unknown_idx = -1
  X = [0,1,2,3]
  for i, v in enumerate(em):
    if v == None:
      unknown_idx = i
    else:
      X.remove(v)
  em[unknown_idx] = X[0]
  return tuple(em)

def complete_oct_embedding_map(embedding_map):
  # TODO: do this better
  em = list(embedding_map)

  known_idx = [ i for i,v in enumerate(embedding_map) if v is not None]

  for perm in OCT_PERMS:
    if all( perm[i] == em[i] for i in known_idx):
      return perm
  
  return None
  
def infer_embedding(cusp_edge_pairing, manifold_face_pairing, embedding):
  source_half_edge, target_half_edge = cusp_edge_pairing
  source_half_face, target_half_face = manifold_face_pairing

  if source_half_edge[0] != embedding[1]:
    raise Exception("Source cusp cell does not match embedding cusp cell")

  if source_half_face[0] != embedding[0]:
    raise Exception("Source manifold cell does not match embedding manifold cell")

  embedding_permutation = embedding[2]

  A = dict(zip((0,) + target_half_edge[1], (0,) + source_half_edge[1]))
  B = dict(zip(list(range(len(embedding_permutation))), embedding_permutation))
  C = dict(zip((0,) + source_half_face[1], (0,) + target_half_face[1]))

  if target_half_face[0][0] == TET:

    partial_embedding_map = (
      C.get(B.get(A.get(0))),
      C.get(B.get(A.get(1))),
      C.get(B.get(A.get(2))),
      C.get(B.get(A.get(3))),
    )

    complete_embedding_map = complete_tet_embedding_map(partial_embedding_map)
  
  else:

    partial_embedding_map = (
      C.get(B.get(A.get(0))),
      C.get(B.get(A.get(1))),
      C.get(B.get(A.get(2))),
      C.get(B.get(A.get(3))),
      C.get(B.get(A.get(4))),
      C.get(B.get(A.get(5))),
    )

    complete_embedding_map = complete_oct_embedding_map(partial_embedding_map)

  return (target_half_edge[0], target_half_face[0], complete_embedding_map)


class CuspPairing:
  def __init__(self, half_edge_a, half_edge_b):
    self.half_edge_a = half_edge_a
    self.half_edge_b = half_edge_b

    self.map = dict(
      zip(
        (0,) + self.half_edge_a[1],
        (0,) + self.half_edge_b[1],
      )
    )

    self.inv_map = dict(
      zip(
        (0,) + self.half_edge_b[1],
        (0,) + self.half_edge_a[1],
      )
    )

class ManifoldPairing:
  def __init__(self, half_face_a, half_face_b):
    self.half_face_a = half_face_a
    self.half_face_b = half_face_b
  
class Embedding:
  def __init__(self, manifold_cell, cusp_cell, embedding_map):
    self.manifold_cell = manifold_cell
    self.cusp_cell = cusp_cell
    self.embedding_map = embedding_map
    self.map = dict(
      zip(
        list(range(len(embedding_map))),
        embedding_map,
      )
    )

    self.inv_map = dict(
      zip(
        embedding_map,
        list(range(len(embedding_map))),
      )
    )

def get_face_pairing(embeddings, cusp_pairing):
  source_cusp_cell, source_edge_spec = cusp_pairing.half_edge_a
  target_cusp_cell, target_edge_spec = cusp_pairing.half_edge_b

  source_embedding = embeddings.get(source_cusp_cell)
  target_embedding = embeddings.get(target_cusp_cell)

  if source_embedding == None:
    return None
  
  source_domain = (0,) + source_edge_spec
  target_domain = (0,) + target_edge_spec

  half_face_a = []
  half_face_b = []

  for i in (0,1,2):
    half_face_a.append(
      source_embedding.map.get(
        source_domain[i]
      )
    )
    half_face_b.append(
      target_embedding.map.get(
        target_domain[i]
      )
    )
  
  return ManifoldPairing(
    (
      source_embedding.manifold_cell,
      tuple(half_face_a),
    ),
    (
      target_embedding.manifold_cell,
      tuple(half_face_b),
    ),
  )

def has_exposed_face_tet(embedding_perm, face_spec):
  indices = sorted((embedding_perm.index(i) for i in face_spec))

  if indices[0] == 0:
    return True
  else:
    return False
  
def has_exposed_face_oct(embedding_perm, face_spec):
  indices = sorted((embedding_perm.index(i) for i in face_spec))

  if indices[0] == 0 and indices[2] != 5:
    diff = indices[2] - indices[1]
    if diff == 1 or diff == 3:
      return True
  else:
    return False
  
def exposed_face_tet(embedding_perm, face_spec):
  indices = sorted((embedding_perm.index(i) for i in face_spec))

  if indices[0] == 0:
    return (indices[1], indices[2])
  else:
    return None
  
def exposed_face_oct(embedding_perm, face_spec):
  indices = sorted((embedding_perm.index(i) for i in face_spec))

  if indices[0] == 0 and indices[2] != 5:
    diff = indices[2] - indices[1]
    if diff == 1 or diff == 3:
      return (indices[1], indices[2])
  else:
    return None
  

def get_face_pairing(embedding, cusp, source_half_face):
  ...
  # source_manifold_cell, source_face_spec = source_half_face
  # source_cusp_cell = embedding.cusp_cell
  # source_embedding_map = embedding.embedding_map
  # if is_oct(source_cusp_cell):
  #   source_edge_spec = exposed_face_oct(source_embedding_map, source_face_spec)
  # else:
  #   source_edge_spec = exposed_face_tet(source_embedding_map, source_face_spec)

  # cusp_pairing = cusp[source_cusp_cell][source_edge_spec]

  # embeddings_by_cusp_cell(cusp_pairing.half_edge_b)
  