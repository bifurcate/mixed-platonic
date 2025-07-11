def perm(*X):
  p = {}
  for i, x in enumerate(X):
    p[i] = x
  return p

def comp(q, r):
  p = {}
  I = sorted(r.keys())
  for i in I:
    p[i] = q[r[i]]
  return p

def to_tuple(p):
  X = []
  I = sorted(p.keys())
  for i in I:
    X.append(p[i])
  return tuple(X)

def to_cycle_form(p):
  I = sorted(p.keys())
  cycles = []
  while len(I) > 0:
    i = I.pop(0)
    cycle = [i]
    while True:
      i = p[i]
      if i in cycle:
        break
      cycle.append(i)
      I.remove(i)
    cycles.append(cycle)
  return cycles
    
def cycle_string(cycles):
  s = ''
  for cycle in cycles:
    if len(cycle) <= 1:
      continue
    s += '('
    for i in cycle:
      s += str(i)
    s += ')'
  if s == '':
    s = '()'
  return s

def array_string(p):
  t = to_tuple(p)
  s = '['
  for i in t:
    s+=str(i)
  s += ']'
  return s

OCT_MOVE_TO_NORTH = [
  perm(0,1,2,3,4,5),
  perm(3,0,2,5,4,1),
  perm(4,1,0,3,5,2),
  perm(1,5,2,0,4,3),
  perm(2,1,5,3,0,4),
  perm(5,1,4,3,2,0),
]

OCT_REVERSE_ORIENTATION = [
  perm(0,1,2,3,4,5),
  perm(0,4,3,2,1,5),
]

OCT_BELT_ROTATION = [
  perm(0,1,2,3,4,5),
  perm(0,2,3,4,1,5),
  perm(0,3,4,1,2,5),
  perm(0,4,1,2,3,5),
]

def gen_oct_perms():
  perms = []
  acc = perm(0,1,2,3,4,5)
  for p in OCT_MOVE_TO_NORTH:
    pcc = comp(p, acc)
    for q in OCT_REVERSE_ORIENTATION:
      qcc = comp(q, pcc)
      for r in OCT_BELT_ROTATION:
        rcc = comp(r, qcc)
        perms.append(rcc)
  return perms

TET_MOVE_TO_NORTH = [
  perm(0,1,2,3),
  perm(3,0,2,1),
  perm(1,2,0,3),
  perm(2,1,3,0),
]

TET_REVERSE_ORIENTATION = [
  perm(0,1,2,3),
  perm(0,1,3,2),
]

TET_BELT_ROTATION = [
  perm(0,1,2,3),
  perm(0,2,3,1),
  perm(0,3,1,2),
]

def gen_tet_perms():
  perms = []
  acc = perm(0,1,2,3)
  for p in TET_MOVE_TO_NORTH:
    pcc = comp(p, acc)
    for q in TET_REVERSE_ORIENTATION:
      qcc = comp(q, pcc)
      for r in TET_BELT_ROTATION:
        rcc = comp(r, qcc)
        perms.append(rcc)
  return perms

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

s = ''
for i, t in enumerate(OCT_PERMS):
  p = perm(*t)
  sort_order = i
  array_form = array_string(p)
  cycle_form = cycle_string(to_cycle_form(p))
  s += f"{sort_order} & {array_form} & {cycle_form} \\\\\n"
