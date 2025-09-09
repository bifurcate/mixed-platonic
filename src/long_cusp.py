from base import (
  Sqr,
  Tri,
  SQR,
  TRI
)

from construction import (
  Cusp
)

SEQ_GEN_GRAPH = {
  'a': ('b',),
  'b': ('a', 'd'),
  'c': ('c', 'e'),
  'd': ('c', 'e'),
  'e': ('b',)
}

POLY_COUNT = {
  'a': (2,2),
  'b': (2,0),
  'c': (2,1),
  'd': (4,2),
  'e': (4,2),
}

STRIP_TEMPLATES = {
  'a': {
    'polys': [
      SQR,
      TRI,
      TRI,
      SQR,
    ],
    'pairings': [
      (
        0, (2, 3),
        1, (1, 3),
      ),
      (
        2, (2, 3),
        3, (1, 4),
      ),
      (
        3, (2, 3),
        0, (1, 4),
      )
    ],
  },

  'b': {
    'polys': [
      TRI,
      TRI,
    ],
    'pairings': [
      (
        0, (2, 3),
        1, (1, 3),
      ),
    ],
  },

  'c': {
    'polys': [
      TRI,
      TRI,
      SQR,
    ],
    'pairings': [
      (
        1, (2, 3),
        2, (1, 4),
      ),
      (
        2, (2, 3),
        0, (1, 3),
      ),
    ]
  },

  'd': {
    'polys': [
      TRI,
      SQR,
      TRI,
      SQR,
      TRI,
      TRI,
    ],
    'pairings': [
      (
        0, (2, 3),
        1, (2, 1),
      ),
      (
        1, (3, 4),
        2, (2, 1),
      ),
      (
        2, (2, 3),
        3, (1, 4),
      ),
      (
        3, (2, 3),
        4, (1, 3),
      ),
      (
        4, (2, 3),
        5, (2, 1),
      ),
      (
        5, (2, 3),
        0, (1, 3),
      ),
    ]
  },
  
  'e': {
    'polys': [
      TRI,
      SQR,
      TRI,
      SQR,
      TRI,
      TRI,
    ],
    'pairings': [
      (
        0, (2, 3),
        1, (1, 4),
      ),
      (
        1, (2, 3),
        2, (1, 3),
      ),
      (
        2, (2, 3),
        3, (2, 1),
      ),
      (
        3, (3, 4),
        4, (2, 1),
      ),
      (
        4, (2, 3),
        5, (1, 3),
      ),
      (
        5, (2, 3),
        0, (2, 1),
      ),
    ],
  },
}

CONNECT_MR_TEMPLATES = {
  'ab': [
    (
      1, (2, 3),
      0, (2, 1),
    ),
    (
      2, (1, 3),
      1, (1, 2),
    ),
  ],
  'ba': [
    (
      0, (1, 3),
      1, (1, 2),
    ),
    (
      1, (2, 3),
      2, (2, 1),
    ),
  ],
  'bd': [
    (
      0, (1, 3),
      1, (2, 3),
    ),
    (
      1, (2, 3),
      3, (2, 1),
    )
  ],
  'de': [
    (
      1, (1, 4),
      3, (2, 3),
    ),
    (
      2, (1, 3),
      5, (1, 2),
    ),
    (
      3, (3, 4),
      1, (2, 1),
    ),
    (
      5, (1, 3),
      2, (1, 2),
    ),
  ],
  'eb': [
    (
      1, (3, 4),
      0, (2, 1),
    ),
    (
      3, (1, 4),
      1, (1, 2),
    )
  ],
  'dc': [
    (
      1, (1, 4),
      0, (1, 2),
    ),
    (
      3, (3, 4),
      1, (2, 1),
    ),
    (
      5, (3, 1),
      2, (2, 1),
    ),
  ],
  'ce': [
    (
      0, (2, 3),
      1, (2, 1),
    ),
    (
      1, (1, 3),
      3, (2, 3),
    ),
    (
      2, (3, 4),
      5, (2, 1),
    ),
  ],
  'cc': [
    (
      0, (2, 3),
      1, (2, 1),
    ),
    (
      1, (1, 3),
      0, (1, 2),
    ),
  ],
}

CONNECT_LR_TEMPLATES = {
  'eba': [
    (
      0, (1, 3),
      0, (1, 2),
    ),
    (
      4, (1, 3),
      3, (1, 2),
    ),
  ],
  'aba': [
    (
      0, (3, 4),
      0, (1, 2),
    ),
    (
      3, (3, 4),
      3, (1, 2),
    )
  ],
  'abd': [
    (
      0, (3, 4),
      0, (2, 1),
    ),
    (
      3, (3, 4),
      4, (2, 1),
    )
  ],
  'ebd': [
    (
      0, (1, 3),
      0, (1, 2),
    ),
    (
      4, (1, 3),
      4, (1, 2),
    )
  ],
  'cce': [
    (
      2, (3, 4),
      2, (2, 1),
    ),
  ],
  'dce': [
    (
      2, (1, 3),
      2, (1, 2),
    ),
  ],
  'ccc': [
    (
      2, (3, 4),
      2, (1, 2),
    ),
  ],
  'dcc': [
    (
      2, (1, 3),
      2, (1, 2),
    ),
  ],
}

def rotate(s, i):
  return s[i:] + s[:i]

def all_rotations(s):
  return [rotate(s, i) for i in range(len(s))]

def is_canonical(s):
  """Return True if seq is the lexicographically smallest of its bracelet class."""
  candidates = all_rotations(s)
  return s == max(candidates)

def get_poly_count(lc_pattern):
  s = lc_pattern
  count = [0, 0]
  for c in s:
    char_count = POLY_COUNT[c]
    count[0] += char_count[0]
    count[1] += char_count[1]

  return count

def next_seq_gen(gen):
  next_gen = []

  for s in gen:
    next_chars = SEQ_GEN_GRAPH[s[-1]]
    for c in next_chars:
      next_gen.append(s + c)

  return next_gen

def build_cusp_sequences(n: int):
  c_seqs = []
  gen = ['a', 'b', 'c', 'd', 'e']

  for _ in range(n):
    gen = next_seq_gen(gen)
    for s in gen:
      if s[0] != s[-1]:
        continue

      loop = s[:-1]
      p_count = get_poly_count(loop)
      if p_count[0] % 4 == 0 and p_count[1] % 6 == 0 and is_canonical(loop):
        c_seqs.append(loop)

  return c_seqs



  

    

class LongCuspGenerator:
  def __init__(self, cusp: Cusp, long_cusp_pattern):
    self.cusp = cusp
    self.long_cusp_pattern = long_cusp_pattern
    self.tri_idx = -1
    self.sqr_idx = -1
    self.strips = []

  def generate(self) -> Cusp:
    n = len(self.long_cusp_pattern)

    for c in self.long_cusp_pattern:
      self.add_strip(c)
    
    for i in range(n):
      self.connect_strips(i)

    return self.cusp

  def traversal(self):
    for strip in self.strips:
      for poly in strip:
        yield poly

  def connect_strips(self, idx):
      n = len(self.long_cusp_pattern)
      cL = self.long_cusp_pattern[(idx-2) % n]
      cM = self.long_cusp_pattern[(idx-1) % n]
      cR = self.long_cusp_pattern[idx % n]
      cMR = cM + cR
      cLMR = cL + cM + cR

      sL = self.strips[(idx-2) % n]
      sM = self.strips[(idx-1) % n]
      sR = self.strips[idx % n]

      if cMR not in CONNECT_MR_TEMPLATES:
        raise KeyError(f"'{cMR}' at {idx} is not a valid pattern subsequence")
      

      MR_pairings = CONNECT_MR_TEMPLATES[cMR]
      for pr in MR_pairings:
        self.cusp.pair(
          sM[pr[0]], pr[1],
          sR[pr[2]], pr[3],
        )

      if cLMR not in CONNECT_LR_TEMPLATES:
        return
      
      LR_pairings = CONNECT_LR_TEMPLATES[cLMR]
      for pr in LR_pairings:
        self.cusp.pair(
          sL[pr[0]], pr[1],
          sR[pr[2]], pr[3],
        )

  def add_strip(self, label):
    if label not in STRIP_TEMPLATES:
      raise KeyError(f"'{label}' not a valid strip label")
    
    polys_spec = STRIP_TEMPLATES[label]['polys']
    pairings_spec = STRIP_TEMPLATES[label]['pairings']
    
    polys = []
    for tp in polys_spec:
      if tp == TRI:
        self.tri_idx += 1
        polys.append(Tri(self.tri_idx))
      elif tp == SQR:
        self.sqr_idx += 1
        polys.append(Sqr(self.sqr_idx))

    for pr in pairings_spec:
      self.cusp.pair(
        polys[pr[0]], pr[1],
        polys[pr[2]], pr[3],
      )

    self.strips.append(polys)

  def get_num_polys(self):
    return (self.tri_idx + 1, self.sqr_idx + 1)

