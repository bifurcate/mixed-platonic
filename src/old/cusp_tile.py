import regina

SQR = 0
TRI = 1
OCT = 0
TET = 1

tet_positions = [
    [0,1,2,3],
    
    
]

cusp_tiling = {
    (0,0): (0, (0,1,2,3,4,5)),
    (0,1): (0, (0,1,2,3)),
    (0,2): (0, (1,0,2,3)),
}

face_pairing = {
    (OCT, 0): { (0,2,3): (TET, 0, (0,2,3)) },
    (TET, 0): { ()
}

class FacePairing():

class FingeredCuspTiling():
    def __init__(self):
        pass

class CuspSquare():
    def __init__(self):
        self.oct = None
        self.position = None
    def set_oct(self, oct: int):
        self.oct = oct
    def set_position(self, perm: regina.Perm6):
        self.position = perm
    def is_square(self):
        return True
    def is_triangle(self):
        return False
    def is_assigned(self):
        return self.oct != None
    def is_positioned(self):
        return self.position != None

class CuspTriangle():
    def __init__(self):
        pass
    def set_tet(self, tet: int):
        self.tet = tet
    def set_position(self, perm: regina.Perm4):
        self.position = perm
    def is_square(self):
        return False
    def is_triangle(self):
        return True
    def is_assigned(self):
        return self.oct != None
    def is_positioned(self):
        return self.position != None
    
class Octahedron():
    def __init__(self):
        self.data = {}
    def join(self, self_face, other, other_face):
        self.data[self_face] = (other, other_face)
    
class TetTetPair():
    pass
        
class OctOctPair():
    pass

class TetOctPair():
    pass

def foo():
    

class CuspFinger():
    def __init__(self, type: int):
        self.type = type
        self.tiles = [
            CuspSquare(),
            CuspTriangle(),
            CuspTriangle(),
        ]

class FingeredCuspTiling():
    def __init__(self, finger_pattern):
        self.fingers = []
        for i, t in enumerate(finger_pattern):
            self.fingers[i] = CuspFinger(t)
    
    def get_tile(self, idx: tuple[int, int]) -> CuspTriangle | CuspSquare:
        finger_idx = idx[0]
        tile_idx = idx[1]
        finger = self.fingers[finger_idx]
        tile = finger.tiles[tile_idx]
        return tile


class FacePairingTable():
    def __init__(self, num_tets: int, num_octs: int):
        self.num_tets = num_tets
        self.num_octs = num_octs
        self.oct_data = {
            (0, 0, {0,2,3}): (1, 1, 4, [0,1,2])
        }
        self.tet_data = {
            (0, 0, (4,3,2))
        }

        


class FingeredCuspIterator():
    def __init__(self, face_pairing_table, fingered_cusp_tiling):
        self.fingered_cusp_tiling = fingered_cusp_tiling
        self.current = (0,0)
    def foo(self):

        face_pairing_table.next_tet()
        face_pairing_table.position_tet()
        


        self.current = (0,0)
        tile = self.fingered_cusp_tiling.get_tile(self.current)
        if not tile.is_assigned() and not tile.is_positioned():
            tile.oct = 0
            tile.position = regina.Perm6()
        
        self.current = (0,1)
        
        tile = self.fingered_cusp_tiling.get_tile(self.current)
        if not tile.is_assigned() and not tile.is_positioned():
            tile.tet = 0
            tile.position = regina.Perm4()

        

class CuspTiling():
    def __init__(self):
        pass
    def attach(self, idx, position):
        self.data[idx] = position

def foo(num_octs):
    num_tets = 3 * num_octs
    fingered_tiling_length = 6 * num_octs
    
    finger_patterns = [[1,-1,1,-1,1,-1],]
    for fp in finger_patterns:
        fct = FingeredCuspTiling(fp)
        