from base import (
  Sqr,
  Tri,
)

from construction import (
  Cusp
)

# TODO: be more specific with the type here
FingerPattern = list[int]

def to_finger_pattern_str(finger_pattern: FingerPattern):
  s = ''
  for x in finger_pattern:
    if x == -1:
      s += '-'
    else:
      s += '+'
  return s

class FingerCuspGenerator:
  def __init__(self, cusp: Cusp, finger_pattern: FingerPattern):
    self.cusp = cusp
    self.finger_pattern = finger_pattern
    self.current_idx = 0

  def add_finger(self, idx):
    sqr0 = Sqr(idx)
    tri0 = Tri(2 * idx)
    tri1 = Tri(2 * idx + 1)

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

  # TODO: add multi-cusp component generation

  # def generate_torus_component(self, component_idx):
  #   n = len(component_finger_pattern)
  #   for i in range(n):
  #     self.add_finger(i)
    
  #   for i in range(n-1):
  #     if self.finger_pattern[i] == self.finger_pattern[i+1]:
  #       self.connect_fingers_pos(i, i+1)
  #     else:
  #       self.connect_fingers_neg(i, i+1)
    
  #   if self.finger_pattern[n-1] == self.finger_pattern[0]:
  #     self.connect_fingers_pos(n-1, 0)
  #   else:
  #     self.connect_fingers_neg(n-1, 0)
  
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

class MultiFingerCuspGenerator:
  def __init__(self, cusp, multi_finger_pattern: list[FingerPattern]):
    self.cusp = cusp
    self.multi_finger_pattern = multi_finger_pattern
    self.flattened = [item for fp in multi_finger_pattern for item in fp]

  def add_finger(self, idx):
    sqr0 = Sqr(idx)
    tri0 = Tri(2 * idx)
    tri1 = Tri(2 * idx + 1)

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

  def add_component(self, finger_pattern, offset):
    n = len(finger_pattern)

    for i in range(n):
      self.add_finger(offset + i)
    
    for i in range(n-1):
      if finger_pattern[i] == finger_pattern[i+1]:
        self.connect_fingers_pos(offset + i, offset + i + 1)
      else:
        self.connect_fingers_neg(offset + i, offset + i + 1)
    
    if finger_pattern[n-1] == finger_pattern[0]:
      self.connect_fingers_pos(offset + n-1, offset)
    else:
      self.connect_fingers_neg(offset + n-1, offset)
  
  def generate(self) -> Cusp:
    offset = 0
    for fp in self.multi_finger_pattern:
      self.add_component(fp, offset)
      offset += len(fp)
  
  def traversal(self):
    for i in range(len(self.flattened)):
      yield Sqr(i)
      yield Tri(2*i)
      yield Tri(2*i + 1)