import regina


def fingered_cellulation():
    cusp = regina.Triangulation2()

    r_perm = regina.Perm3(1, 0, 2)
    ident_perm = regina.Perm3()

    tris = []

    for i in range(6):
        tris.append(cusp.newTriangle())

    tris[0].join(1, tris[1], ident_perm)
    tris[1].join(2, tris[2], ident_perm)
    tris[2].join(1, tris[3], ident_perm)
    tris[3].join(2, tris[0], ident_perm)

    tris[1].join(0, tris[4], ident_perm)
    tris[4].join(2, tris[5], ident_perm)

    ## make torus

    tris[1].join(2, tris[3], r_perm)
    tris[0].join(2, tris[2], r_perm)

    return cusp


class Finger:
    def __init__(self, cusp):
        self.cusp = cusp
        self.gen_tris()

    def gen_tris(self):
        ident_perm = regina.Perm3()

        self.sqr_face_0 = self.cusp.newTriangle()
        self.sqr_face_1 = self.cusp.newTriangle()
        self.sqr_face_2 = self.cusp.newTriangle()
        self.sqr_face_3 = self.cusp.newTriangle()

        self.sqr_face_0.join(0, self.sqr_face_1, ident_perm)
        self.sqr_face_1.join(1, self.sqr_face_2, ident_perm)
        self.sqr_face_2.join(0, self.sqr_face_3, ident_perm)
        self.sqr_face_3.join(1, self.sqr_face_0, ident_perm)

        ## create triangle A

        self.tri_face_A = self.cusp.newTriangle()

        self.sqr_face_1.join(2, self.tri_face_A, ident_perm)

        ## create triangle B

        self.tri_face_B = self.cusp.newTriangle()

        self.tri_face_A.join(1, self.tri_face_B, ident_perm)

        ## connect the short meridian

        self.tri_face_B.join(0, self.sqr_face_3, regina.Perm3(2, 1, 0))

    def connect(self, finger):
        self.sqr_face_0.join(2, finger.sqr_face_2, regina.Perm3(1, 0, 2))
        self.tri_face_A.join(0, finger.tri_face_B, regina.Perm3(2, 0, 1))


class FingeredCellulation:
    def __init__(self, finger_sequence):
        self.finger_sequence = finger_sequence
        self.cusp = regina.Triangulation2()

    def gen_triangulation(self):

        initial_finger = Finger(self.cusp)

        prev_finger = initial_finger

        for i in self.finger_sequence:
            current_finger = Finger(self.cusp)
            current_finger.connect(prev_finger)
            prev_finger = current_finger

        initial_finger.connect(prev_finger)
