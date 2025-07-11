FCE = 0  # First Cell Embedding
CHC = 1  # Choice
IND = 2  # Induced

embedding_type_labels = {
  0: "First",
  1: "Choice",
  2: "Induced",
}

TET = 0
OCT = 1

FingerPattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]

Boyd = [
  [(0,0),  (OCT,0), (0,1,2,3,4,5), 0,  FCE],  # First Cell Embedding
  [(0,1),  (TET,0), (0,1,2,3)    , 1,  FCE],
  [(0,2),  (TET,1), (0,1,2,3)    , 2,  FCE],
  [(1,0),  (OCT,1), (0,1,2,3,4,5), 3,  FCE],
  [(1,1),  (TET,2), (0,1,2,3)    , 4,  FCE],
  [(1,2),  (TET,0), (1,3,2,0)    , 5,  CHC],
  [(2,0),  (OCT,0), (2,0,3,5,1,4), 6,  IND],
  [(11,0), (OCT,1), (4,5,3,0,1,2),  7, IND], 
  [(2,1),  (TET,3), (0,1,2,3),     8,  FCE],
  [(11,1), (TET,3), (2,1,3,0),      9, IND],
  [(2,2),  (TET,4), (0,1,2,3),     10,  FCE],
  [(11,2), (TET,4), (2,0,2,3),     11, IND],
  [(3,0),  (OCT,0), (3,4,5,2,0,1), 13, CHC],
  [(3,1),  (TET,5), (0,1,2,3),     12, FCE],
  [(3,2),  (TET,3), (1,3,2,0),     14, IND],
  [(4,0),  (OCT,0), (3,2,5,4,0,1), 15, IND],
  [(4,1),  (TET,2), (3,1,0,2),     16, IND],
  [(4,2),  (TET,0), (3,2,1,0),     17, IND],
  [(5,0),  (OCT,1), (2,0,1,5,3,4), 18, IND],
  [(5,1),  (TET,1), (1,2,0,3),     19 ,IND],
  [(5,2),  (TET,2), (1,2,0,3),     20, IND],
  [(6,0),  (OCT,0), (5,3,4,1,2,0), 21 ,IND],
  [(6,1),  (TET,5), (3,1,0,2),     22, IND],
  [(6,2),  (TET,3), (3,2,1,0),     23, IND],
  [(7,0),  (OCT,1), (5,3,4,1,2),   24, IND],
  [(7,1),  (TET,4), (1,2,0,3),     25, IND],
  [(7,2),  (TET,5), (1,2,0,3),     26, IND],
  [(8,0),  (OCT,0), (4,5,1,0,3,2), 27, IND],
  [(8,1),  (TET,1), (3,2,1,0),     28, IND],
  [(8,2),  (TET,2), (2,0,1,3),     29, IND],
  [(9,0),  (OCT,1), (1,2,0,4,5,3), 30, IND],
  [(9,1),  (TET,0), (2,1,3,0),     31, IND],
  [(9,2),  (TET,1), (2,0,1,3),     32, IND],
  [(10,0), (OCT,0), (1,4,0,2,5,3), 33, IND],
  [(10,1), (TET,4), (3,2,1,0),     34, IND],
  [(10,2), (TET,5), (2,0,1,3),     35, IND],
]

s = ''
for row in Boyd:
  cusp_index = row[0]
  cell_index = row[1]
  embedding_permutation = row[2]
  ep_formatted = ''
  for i in embedding_permutation:
    ep_formatted += str(i)

  stack_position = row[3]
  embedding_type = row[4]

  et_formatted = embedding_type_labels[embedding_type]
  s += f"{cusp_index} & {stack_position} & {cell_index} & {ep_formatted} & {et_formatted} \\\\\n"



