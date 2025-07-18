import regina
from base import (
  Tet,
  Oct,
  ManifoldFacePairing,
  ManifoldHalfFace,
  normalize_face_pair,
)
from construction import (
  ManifoldCellulation,
  ManifoldCell,
)

TET_TRIANGULATION_MAP = {
  (0,1,2): (0, (0,1,2)),
  (0,1,3): (0, (0,1,3)),
  (0,2,3): (0, (0,2,3)),
  (1,2,3): (0, (1,2,3)),
}

OCT_TRIANGULATION_MAP = {
  (0,1,2): (0, (2,1,3)),
  (0,2,3): (1, (2,3,1)),
  (0,3,4): (2, (2,1,3)),
  (0,1,4): (3, (2,1,3)),
  (1,2,5): (4, (1,3,2)),
  (2,3,5): (5, (3,1,2)),
  (3,4,5): (6, (1,3,2)),
  (1,4,5): (7, (1,3,2)),
}

def reorder(A,B,C):
  # give an ordering induced by A -> B, reorder C
  sort_indices = [A.index(i) for i in B]
  reordered_C = [C[i] for i in sort_indices]
  return tuple(reordered_C)

def prepend_missing(X,n):
  # finds missing int in X with respect to range(n)
  missing_set = set(range(n)) - set(X)
  if len(missing_set) != 1:
    raise ValueError('only one missing allowed')

  return tuple(tuple(missing_set) + tuple(X))


def get_r_face_spec(triangulation_map, face_spec):
  sorted_face_spec = tuple(sorted(face_spec))
  _, orig_r_face_spec = triangulation_map[sorted_face_spec]
  ordered_r_face_spec = reorder(sorted_face_spec, face_spec, orig_r_face_spec)
  return ordered_r_face_spec


def get_regina_tet_idx(manifold_half_face: ManifoldHalfFace, num_tets, num_octs):
  manifold_cell = manifold_half_face.manifold_cell
  face_spec = manifold_half_face.face_spec

  if manifold_cell.is_tet():
    return manifold_cell.cell_index
  if manifold_cell.is_oct():
    r_tet_idx, _ = OCT_TRIANGULATION_MAP[tuple(sorted(face_spec))]
    return num_tets + 8 * manifold_cell.cell_index + r_tet_idx

def get_regina_perm_data(manifold_face_pairing: ManifoldFacePairing) -> tuple[int, regina.Perm4]:
  src_manifold_cell = manifold_face_pairing.half_face_src.manifold_cell
  tgt_manifold_cell = manifold_face_pairing.half_face_tgt.manifold_cell
  
  src_face_spec = manifold_face_pairing.half_face_src.face_spec
  tgt_face_spec = manifold_face_pairing.half_face_tgt.face_spec

  if src_manifold_cell.is_tet():
    r_src_face_spec = get_r_face_spec(TET_TRIANGULATION_MAP, src_face_spec)
  elif src_manifold_cell.is_oct():
    r_src_face_spec = get_r_face_spec(OCT_TRIANGULATION_MAP, src_face_spec)

  if tgt_manifold_cell.is_tet():
    r_tgt_face_spec = get_r_face_spec(TET_TRIANGULATION_MAP, tgt_face_spec)
  elif tgt_manifold_cell.is_oct():
    r_tgt_face_spec = get_r_face_spec(OCT_TRIANGULATION_MAP, tgt_face_spec)

  # TODO: prepending the zero here has to do with the particular
  # OCT_TRIANGULATION_MAP that was chosen, in general we want to
  # infer the missing element to generate the perm
  r_src_face_spec = prepend_missing(r_src_face_spec, 4)
  r_tgt_face_spec = prepend_missing(r_tgt_face_spec, 4)

  # interleave to pass into Perm4
  perm_input = tuple(x for pair in zip(r_src_face_spec, r_tgt_face_spec) for x in pair)

  return r_src_face_spec[0], regina.Perm4(*perm_input)

def get_gluing_data(manifold_face_pairing: ManifoldFacePairing, num_tets: int, num_octs: int) -> tuple[int, int, regina.Perm4]:
  src_tet_idx = get_regina_tet_idx(manifold_face_pairing.half_face_src, num_tets, num_octs)
  tgt_tet_idx = get_regina_tet_idx(manifold_face_pairing.half_face_tgt, num_tets, num_octs)
  r_face, perm = get_regina_perm_data(manifold_face_pairing)

  return (src_tet_idx, tgt_tet_idx, r_face, perm)

def glue_oct_internal(triangulation: regina.Triangulation3, base_idx: int):
  identity_perm = regina.Perm4()

  # TODO: make this more elegant, and concise
  # glue up the top hemisphere
  triangulation.tetrahedron(base_idx + 0).join(1, triangulation.tetrahedron(base_idx + 1), identity_perm)
  triangulation.tetrahedron(base_idx + 1).join(3, triangulation.tetrahedron(base_idx + 2), identity_perm)
  triangulation.tetrahedron(base_idx + 2).join(1, triangulation.tetrahedron(base_idx + 3), identity_perm)
  triangulation.tetrahedron(base_idx + 3).join(3, triangulation.tetrahedron(base_idx + 0), identity_perm)

  # glue up the bottom hemisphere
  triangulation.tetrahedron(base_idx + 4).join(1, triangulation.tetrahedron(base_idx + 5), identity_perm)
  triangulation.tetrahedron(base_idx + 5).join(3, triangulation.tetrahedron(base_idx + 6), identity_perm)
  triangulation.tetrahedron(base_idx + 6).join(1, triangulation.tetrahedron(base_idx + 7), identity_perm)
  triangulation.tetrahedron(base_idx + 7).join(3, triangulation.tetrahedron(base_idx + 4), identity_perm)

  # glue the hemipheres together
  triangulation.tetrahedron(base_idx + 0).join(2, triangulation.tetrahedron(base_idx + 4), identity_perm)
  triangulation.tetrahedron(base_idx + 1).join(2, triangulation.tetrahedron(base_idx + 5), identity_perm)
  triangulation.tetrahedron(base_idx + 2).join(2, triangulation.tetrahedron(base_idx + 6), identity_perm)
  triangulation.tetrahedron(base_idx + 3).join(2, triangulation.tetrahedron(base_idx + 7), identity_perm)

def to_regina_triangulation(manifold_celluation: ManifoldCellulation, num_tets: int, num_octs: int) -> regina.Triangulation3():
  triangulation = regina.Triangulation3()
  for _ in range(num_tets + 8 * num_octs):
    triangulation.newTetrahedron()

  for i in range(num_octs):
    glue_oct_internal(triangulation, num_tets + 8*i)
  
  for i in range(num_tets):
    pairings = manifold_celluation.get_cell_pairings(Tet(i))
    for p in pairings.values():
      src_tet_idx, tgt_tet_idx, r_face, perm = get_gluing_data(p, num_tets, num_octs)
      # we need to do this because each gluing is attempted twice, this will be fixed when
      # ManifoldFacePairing is refactored
      try:
        triangulation.tetrahedron(src_tet_idx).join(r_face, triangulation.tetrahedron(tgt_tet_idx), perm)
      except regina.engine.InvalidArgument:
        continue

  for i in range(num_octs):
    pairings = manifold_celluation.get_cell_pairings(Oct(i))
    for p in pairings.values():
      src_tet_idx, tgt_tet_idx, r_face, perm = get_gluing_data(p, num_tets, num_octs)
      # we need to do this because each gluing is attempted twice, this will be fixed when
      # ManifoldFacePairing is refactored
      try:
        triangulation.tetrahedron(src_tet_idx).join(r_face, triangulation.tetrahedron(tgt_tet_idx), perm)
      except regina.engine.InvalidArgument:
        continue

  return triangulation
  
    

# class MixedPlatonic3:
#     def __init__(self, num_octs: int):    
#         self.num_octs = num_octs
#         self.num_tets = 3 * num_octs
#         self.initialize_triangulation()

#     def initialize_triangulation(self):
#         self.octs = [];
#         self.tets = [];
#         self.triangulation = regina.Triangulation3()

#     def build_oct

# class PlatonicTetrahedron:
#     def __init__(self, triangulation: regina.Triangulation3):
#         self.triangulation = triangulation
#         self.tet = self.triangulation.newTetrahedron()

# class PlatonicOctahedron:
#     def __init__(self, triangulation: regina.Triangulation3):
#         self.triangulation = triangulation
#         self.tets = []
#         self.create_tets()

#     def create_tets(self):
#         for i in range(8):
#             self.tets.append(self.triangulation.newTetrahedron())

#     def glue_tets(self):

#         identity_perm = regina.Perm4()

#         # glue up the top hemisphere
#         self.tets[0].join(1, self.tets[1], identity_perm)
#         self.tets[1].join(3, self.tets[2], identity_perm)
#         self.tets[2].join(1, self.tets[3], identity_perm)
#         self.tets[3].join(3, self.tets[0], identity_perm)

#         # glue up the bottom hemisphere

#         self.tets[4].join(1, self.tets[5], identity_perm)
#         self.tets[5].join(3, self.tets[6], identity_perm)
#         self.tets[6].join(1, self.tets[7], identity_perm)
#         self.tets[7].join(3, self.tets[4], identity_perm)

#         # glue the hemipheres together

#         self.tets[0].join(2, self.tets[4], identity_perm)
#         self.tets[1].join(2, self.tets[5], identity_perm)
#         self.tets[2].join(2, self.tets[6], identity_perm)
#         self.tets[3].join(2, self.tets[7], identity_perm)
    
  

# regina.Triangulation3();

# oct = Triangulation3()

# for i in range(4):
#     oct.newTetrahedron()

# for i, tet in enumerate(oct.tetrahedra()):
#     T[i].join(1,T[i + 1 % 4],Perm4([0,2,1,3]))


# sqrt(3)/2 + 1/2 i

# 1 5 7 11
