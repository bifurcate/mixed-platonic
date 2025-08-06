from itertools import product

def rotate(seq, i):
  return seq[i:] + seq[:i]

def invert(seq):
  return tuple(-x for x in seq)

def all_rotations(seq):
  return [rotate(seq, i) for i in range(len(seq))]

def all_reflections(seq):
  reflected = seq[::-1]
  return all_rotations(seq) + all_rotations(reflected)

# note this is a bit different from general bracelets in that
# we also have an inversion symmetry
def equivalence_class(seq):
  inverted_seq = invert(seq)
  return set(all_reflections(seq) + all_reflections(inverted_seq))

def is_canonical(seq):
  """Return True if seq is the lexicographically smallest of its bracelet class."""
  candidates = equivalence_class(seq)
  return seq == max(candidates)

def generate_2_bracelets(n: int):
  """Yield all distinct bracelets of length n over k colors."""
  for seq in product([1, -1], repeat=n):
    if is_canonical(seq):
      yield seq


    
