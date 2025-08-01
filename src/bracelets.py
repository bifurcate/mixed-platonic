from itertools import product
from collections import deque

def rotate(seq, i):
  return seq[i:] + seq[:i]

def invert(seq):
  return tuple(-x for x in seq)

def all_rotations(seq):
  return [rotate(seq, i) for i in range(len(seq))]

def all_reflections(seq):
  reflected = seq[::-1]
  return all_rotations(seq) + all_rotations(reflected)

def equivalence_class(seq):
  inverted_seq = invert(seq)
  return set(all_reflections(seq) + all_reflections(inverted_seq))

def is_canonical(seq):
  """Return True if seq is the lexicographically smallest of its bracelet class."""
  candidates = equivalence_class(seq)
  return seq == min(candidates)

def generate_2_bracelets(n: int):
  """Yield all distinct bracelets of length n over k colors."""
  for seq in product([-1, 1], repeat=n):
    if is_canonical(seq):
      yield seq

def foo(n):
  sequences = list(product([-1,1], repeat=n))
  bracelets = []

  while sequences:
    seq = sequences.pop(0)

    for s in all_rotations(seq):
      if s in sequences:
        sequences.remove(s)

    r_seq = seq[::-1]
    for s in all_rotations(r_seq):
      if s in sequences:
        sequences.remove(s)

    i_seq = invert(seq)
    for s in all_rotations(i_seq):
      if s in sequences:
        sequences.remove(s)
    
    ir_seq = i_seq[::-1]
    for s in all_rotations(ir_seq):
      if s in sequences:
        sequences.remove(s)
    
    bracelets.append(seq)

  return bracelets


    
