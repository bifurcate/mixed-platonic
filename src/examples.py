from base import (
  Oct,
  Sqr,
  Tet,
  Tri,
  OctSqrEmbedding,
  TetTriEmbedding,
)

from construction import (
  Embeddings,
  Cusp,
  FingerCuspGenerator,
  Construction,
)

finger_pattern = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
cusp = FingerCuspGenerator(finger_pattern).generate()

embeddings = Embeddings()

# finger 0 embeddings
embeddings.add_embedding(
  OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(1), Tri(1), (0, 1, 2, 3))
)

# finger 1 embeddings
embeddings.add_embedding(
  OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(2), Tri(2), (0, 1, 2, 3))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(0), Tri(3), (1, 3, 2, 0))
)

# finger 2 embeddings

embeddings.add_embedding(
  OctSqrEmbedding(Oct(0), Sqr(2), (2, 0, 3, 5, 1, 4))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(3), Tri(4), (0, 1, 2, 3))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(4), Tri(5), (0, 1, 2, 3))
)

# finger 3 embeddings

embeddings.add_embedding(
  OctSqrEmbedding(Oct(1), Sqr(3), (3, 4, 5, 2, 0, 1))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(5), Tri(6), (0, 1, 2, 3))
)
embeddings.add_embedding(
  TetTriEmbedding(Tet(3), Tri(7), (1, 3, 2, 0))
)

boyd_to_f3 = Construction(cusp, embeddings)