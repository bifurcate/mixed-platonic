import regina
import itertools

IDENTITY_PERM = regina.Perm4()


class MixedPlatonic3:
    def __init__(self, num_octs: int):
        self.num_octs = num_octs
        self.num_tets = 3 * num_octs
        self.initialize_triangulation()

    def initialize_triangulation(self):
        self.octs = []
        self.tets = []
        self.triangulation = regina.Triangulation3()


class PlatonicTetrahedron:
    def __init__(self, triangulation: regina.Triangulation3):
        self.triangulation = triangulation
        self.tet = self.triangulation.newTetrahedron()

    def join_tet(self, self_face_num, other_tet, perm):
        self.tet.join(self_face_num, other_tet.tet, perm)

    def join_oct(self, self_face_num, other_oct, other_face_num, perm):
        other_oct.join_tet(other_face_num, self, self_face_num, perm)


class PlatonicOctahedron:
    def __init__(self, triangulation: regina.Triangulation3):
        self.triangulation = triangulation
        self.tets = []
        self.create_tets()
        self.glue_tets()

    def create_tets(self):
        for i in range(8):
            self.tets.append(self.triangulation.newTetrahedron())

    def glue_tets(self):

        # glue up the top hemisphere
        self.tets[0].join(1, self.tets[1], IDENTITY_PERM)
        self.tets[1].join(3, self.tets[2], IDENTITY_PERM)
        self.tets[2].join(1, self.tets[3], IDENTITY_PERM)
        self.tets[3].join(3, self.tets[0], IDENTITY_PERM)

        # glue up the bottom hemisphere

        self.tets[4].join(1, self.tets[5], IDENTITY_PERM)
        self.tets[5].join(3, self.tets[6], IDENTITY_PERM)
        self.tets[6].join(1, self.tets[7], IDENTITY_PERM)
        self.tets[7].join(3, self.tets[4], IDENTITY_PERM)

        # glue the hemipheres together

        self.tets[0].join(2, self.tets[4], IDENTITY_PERM)
        self.tets[1].join(2, self.tets[5], IDENTITY_PERM)
        self.tets[2].join(2, self.tets[6], IDENTITY_PERM)
        self.tets[3].join(2, self.tets[7], IDENTITY_PERM)

    def join_tet(self, self_face_num, other_tet, perm):
        self_tet = self.tets[self_face_num]
        self_tet.join(0, other_tet.tet, perm)

    def join_oct(self, self_face_num, other_oct, other_face_num, perm):
        self_tet = self.tets[self_face_num]
        other_tet = other_oct.tets[other_face_num]
        self_tet.join(0, other_tet, perm)


def next_balls_tet(isosig):
    next_sigs = set()
    triangulation = regina.Triangulation3(isosig)
    assert triangulation.countBoundaryComponents() == 1
    boundary = triangulation.boundaryComponents()[0]
    for face in boundary.facets():
        faceEmbedding = face.front()
        boundaryTetIdx = faceEmbedding.simplex().index()
        boundaryFace = faceEmbedding.face()
        newTriangulation = regina.Triangulation3(triangulation)
        boundaryTet = newTriangulation.tetrahedron(boundaryTetIdx)
        newTet = newTriangulation.newTetrahedron()

        boundaryTet.join(boundaryFace, newTet, IDENTITY_PERM)
        newSig = newTriangulation.isoSig()
        next_sigs.add(newSig)
    return next_sigs


def next_balls(isosig, cell_type):

    triangulation = regina.Triangulation3(isosig)

    n_boundary_components = triangulation.countBoundaryComponents()

    if n_boundary_components == 0:
        if cell_type == "O":
            PlatonicOctahedron(triangulation)
        else:
            PlatonicTetrahedron(triangulation)

        return {triangulation.isoSig()}

    next_sigs = set()

    assert triangulation.countBoundaryComponents() == 1
    boundary = triangulation.boundaryComponents()[0]

    for face in boundary.facets():
        faceEmbedding = face.front()
        boundaryTetIdx = faceEmbedding.simplex().index()
        boundaryFace = faceEmbedding.face()
        newTriangulation = regina.Triangulation3(triangulation)
        boundaryTet = newTriangulation.tetrahedron(boundaryTetIdx)

        if cell_type == "O":
            newOct = PlatonicOctahedron(newTriangulation)
            newOct.tets[0].join(0, boundaryTet, regina.Perm4(0, boundaryFace))
        else:
            newTet = PlatonicTetrahedron(newTriangulation)
            boundaryTet.join(boundaryFace, newTet.tet, IDENTITY_PERM)

        newSig = newTriangulation.isoSig()
        next_sigs.add(newSig)
    return next_sigs


def gen_balls_from_type_ordering(cell_types):
    print("processing: " + str(cell_types))
    current_sig_set = {"a"}  # initial with empty triangulation
    for cell_type in cell_types:
        last_sig_set = current_sig_set.copy()
        current_sig_set = set()
        for sig in last_sig_set:
            current_sig_set.update(next_balls(sig, cell_type))
    return current_sig_set


def gen_mixed_platonic_balls(num_tets, num_octs):

    type_string = ""
    for i in range(num_tets):
        type_string += "T"
    for i in range(num_octs):
        type_string += "O"

    sig_set = set()
    type_orderings = set(itertools.permutations(type_string))
    for to in type_orderings:
        new_sigs = gen_balls_from_type_ordering(to)
        sig_set.update(new_sigs)
    return sig_set
