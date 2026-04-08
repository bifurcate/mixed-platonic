"""Restrict cusp pattern enumeration using octahedron structural constraints.

This module prunes the space of short-meridian cusp patterns by
exploiting structural constraints from octahedron face-pairing graphs
and admissible face labelings (thesis §5.2).

Terminology and binary string hierarchy
----------------------------------------
The short-meridian cusp cellulation is encoded by three levels of cyclic
binary string, each related by mod-2 discrete differentiation/integration
(see ``binary_loop``):

- **Orientation string** ``s``: each entry is the orientation (0 or 1)
  of the corresponding finger.  Two orientation strings that are
  bitwise complements produce the same cusp cellulation (thesis §5.2,
  complement symmetry).
- **Finger pattern** ``f`` (thesis Definition 5.5): the boundary-type
  string ``f_i = (s_i + s_{i+1}) mod 2``, i.e. ``f = differentiate(s)``.
  Entry 0 = stay (same-orientation neighbours), 1 = switch (opposite).
  Equivalence classes of ``f`` under rotation and reversal are bracelets
  (no complement symmetry needed, since complementing ``s`` leaves ``f``
  unchanged).
- **Boundary derivative** ``r`` (thesis Definition 5.10):
  ``r = differentiate(f)``.  Entry ``r_i = 1`` iff the square tile of
  finger ``i+1`` has type [OTTT] (thesis Proposition 5.11).  The
  Hamming weight ``wt_1(r)`` is the *oct-signature* ``σ(f)`` — the
  total number of [OTTT] square tiles.

The primary entry point is ``generate_short_cusp(n)``, which implements
the enumeration algorithm from the thesis (§5.2):

1. Enumerate all non-isomorphic ``G_OO`` multigraphs (``n_oct`` vertices,
   ``n_oct`` edges; thesis Lemma 5.6 and §5.2.1).
2. For each graph, compute achievable oct-signatures from the degree
   sequence via ``DEGREE_RANK_MAP`` (thesis Table 3, Corollary 5.12).
3. For each oct-signature, construct boundary derivatives ``r`` with
   ``wt_1(r) = σ``, then integrate twice to recover orientation strings.
4. Canonicalize under rotation, reversal, and complement.

Additionally, ``generate_balanced_patterns`` provides a simpler
combinatorial approach using balanced binary tuples reduced to bracelets.

The module also includes multigraph enumeration utilities
(``get_nonisomorphic_multigraphs``, ``get_oct_signature_spectrum``) for
enumerating ``G_OO`` candidates and computing oct-signature spectra.
"""

import itertools
from collections.abc import Iterator
from itertools import permutations

from bracelets import BinarySeq, to_canonical, reduce_to_bracelets
from binary_loop import binary_tuples_of_weight, integrate

# Each octahedron has 6 square cusp cells (thesis Proposition 5.9).
# A type vector ``(a, b, c)`` records how those 6 squares distribute
# across three restricted square tile type categories (thesis
# Proposition 5.5):
#   a = [OTTT]  (one stay + one switch boundary)
#   b = [TTTT]  (both boundaries same type: both stays or both switches)
#   c = [OTOT]  (both boundaries same type, alternating edge types)
# The entries always sum to 6.  The six admissible octahedron face
# labelings A–F (thesis Proposition 5.9) each produce one of these
# distributions.
OctTypeVector = tuple[int, int, int]

OCT_TYPE_VECTORS: list[OctTypeVector] = [
    (3, 3, 0),  # Labeling B (degree 1): [OTTT]=3, [TTTT]=3, [OTOT]=0
    (3, 0, 3),  # Labeling E (degree 3): [OTTT]=3, [TTTT]=0, [OTOT]=3
    (4, 1, 1),  # Labeling C (degree 2): [OTTT]=4, [TTTT]=1, [OTOT]=1
    (0, 6, 0),  # Labeling A (degree 0): [OTTT]=0, [TTTT]=6, [OTOT]=0
    (0, 0, 6),  # Labeling F (degree 4): [OTTT]=0, [TTTT]=0, [OTOT]=6
    (6, 0, 0),  # Labeling D (degree 2): [OTTT]=6, [TTTT]=0, [OTOT]=0
]


def _get_partitions_of_length(n: int, length: int) -> list[tuple[int, ...]]:
    """Return all partitions of *n* into exactly *length* positive parts.

    Parts are in non-increasing order.

    Args:
        n: The integer to partition.
        length: Exact number of parts.

    Returns:
        List of partition tuples in lexicographic order.
    """
    if length == 1:
        return [(n,)] if n > 0 else []

    if length > n:
        return []

    partitions: list[tuple[int, ...]] = []
    for first_part in range(n - length + 1, 0, -1):
        remaining = n - first_part
        remaining_length = length - 1

        sub_partitions = _get_partitions_of_length(remaining, remaining_length)

        for sub_partition in sub_partitions:
            if not sub_partition or first_part >= sub_partition[0]:
                partitions.append((first_part,) + sub_partition)

    return partitions[::-1]


def get_partitions(n: int, length: int) -> list[tuple[int, ...]]:
    """Return all partitions of *n* with at most *length* parts, zero-padded.

    Each partition is represented as a tuple of exactly *length* integers
    with leading zeros and the non-zero parts in non-increasing order on
    the right.

    Args:
        n: The integer to partition.
        length: Maximum number of parts (and output tuple width).

    Returns:
        List of zero-padded partition tuples.
    """
    all_partitions: list[tuple[int, ...]] = []

    if n == 0:
        return [
            (0,) * length,
        ]

    for partition_length in range(1, length + 1):
        partitions = _get_partitions_of_length(n, partition_length)

        for partition in partitions:
            padded = (0,) * (length - partition_length) + partition
            all_partitions.append(padded)

    return all_partitions


def pattern_from_parts(
    odd_part: tuple[int, ...], even_part: tuple[int, ...]
) -> set[BinarySeq]:
    """Build canonical binary patterns from odd/even run-length specifications.

    For each permutation of the odd and even parts, constructs a binary
    pattern by interleaving runs of 1s and 0s, then canonicalizes via
    ``to_canonical``.

    Args:
        odd_part: Tuple of run lengths for odd-position zero runs.
        even_part: Tuple of run lengths for even-position zero runs.

    Returns:
        Set of canonical binary sequences.
    """
    odd_perms = list(set(itertools.permutations(odd_part)))
    even_perms = list(set(itertools.permutations(even_part)))

    perm_product = itertools.product(odd_perms, even_perms)

    P: set[BinarySeq] = set()
    for odd, even in perm_product:
        A: list[int] = []
        for o, e in zip(odd, even):
            A.extend(
                [
                    1,
                ]
                + [
                    0,
                ]
                * o
                + [
                    1,
                ]
                + [
                    0,
                ]
                * e
            )
        P.add(to_canonical(tuple(A)))

    return P


def patterns_for_oct_sig(n: int, sigma: int) -> set[BinarySeq]:
    """Enumerate all canonical boundary derivatives of length *n* with oct-signature *sigma*.

    The boundary derivative ``r`` (thesis Definition 5.10) has
    ``wt_1(r) = sigma``, where ``sigma`` is the oct-signature — the
    total number of [OTTT] square tiles.  This function constructs all
    canonical binary sequences of length *n* with exactly *sigma* ones
    by distributing ``(n - sigma) / 2`` zeros across ``sigma / 2`` odd
    and even slots via integer partitions.

    Args:
        n: Total pattern length (number of fingers).
        sigma: Oct-signature — Hamming weight of the boundary derivative.
            Must have the same parity as *n*; ``sigma / 2`` must be
            integral.

    Returns:
        Set of canonical binary sequences.
    """
    b = (n - sigma) // 2

    odd_parts = get_partitions(b, sigma // 2)
    even_parts = get_partitions(b, sigma // 2)

    total_product = itertools.product(odd_parts, even_parts)
    patterns: set[BinarySeq] = set()
    for odd, even in total_product:
        patterns = patterns.union(pattern_from_parts(odd, even))

    return patterns


def generate_short_cusp(n: int) -> Iterator[tuple[int, ...]]:
    """Yield all canonical orientation strings of length *n* for short-meridian cusps.

    Implements the enumeration algorithm from the thesis (§5.2):

    1. **G_OO enumeration.**  The oct-oct face-pairing subgraph ``G_OO``
       has ``v = e = n_oct`` (thesis Lemma 5.6).  Enumerate all
       non-isomorphic loopless multigraphs with these parameters.
    2. **Oct-signature spectrum.**  For each graph, compute achievable
       oct-signatures from the degree sequence via ``DEGREE_RANK_MAP``
       (thesis Table 3, Corollary 5.12).
    3. **Boundary derivatives → finger patterns → orientation strings.**
       For each oct-signature ``σ``, construct all boundary derivatives
       ``r`` with ``wt_1(r) = σ`` via ``patterns_for_oct_sig``.
       Integrate ``r`` with both initial values (``c=0`` and ``c=1``)
       to recover finger patterns ``f`` (two solutions per ``r`` since
       integration is ambiguous up to an additive constant).  Integrate
       ``f`` once more (``c=0`` only) to get orientation strings ``s``.
       Only one initial value is needed here: complementing ``s``
       (swapping 0 ↔ 1) leaves ``f`` unchanged, so ``s`` and ``s̄``
       encode the same cusp cellulation.
    4. **Canonicalization.**  Each orientation string is reduced to its
       canonical bracelet representative under rotation, reversal, and
       complement (via ``to_canonical`` with ``with_complement=True``).

    Args:
        n: Number of fingers (must be divisible by 6).

    Yields:
        Canonical orientation strings as tuples of 0/1 values.
    """
    nv_oct = n // 6
    for sigma in get_oct_signature_spectrum(get_nonisomorphic_multigraphs(nv_oct, nv_oct)):
        boundary_derivatives = patterns_for_oct_sig(n, sigma)
        # Integrate boundary derivatives → finger patterns.  Both initial
        # values are needed (integration ambiguous up to a constant).
        finger_patterns = set(
            [integrate(r, 0) for r in boundary_derivatives]
            + [integrate(r, 1) for r in boundary_derivatives]
        )
        # Integrate finger patterns → orientation strings.  Only c=0 is
        # needed: complementing s leaves f unchanged (complement symmetry).
        # Canonicalize under rotation, reversal, and complement.
        orientation_strings = set(
            to_canonical(integrate(f, 0), with_complement=True)
            for f in finger_patterns
        )
        for s in orientation_strings:
            yield tuple(s)


def generate_balanced_patterns(n: int) -> list[BinarySeq]:
    """Generate all canonical balanced binary patterns of length *n*.

    A balanced pattern has exactly ``n / 2`` ones and ``n / 2`` zeros.
    Patterns are reduced to bracelet representatives (up to rotation,
    reflection, and sign inversion).

    Args:
        n: Pattern length (should be even).

    Returns:
        List of canonical balanced binary tuples.
    """
    X = binary_tuples_of_weight(n, n // 2)
    X = reduce_to_bracelets(X)
    return list(X)


def round_with_tolerance(
    value: int | float | complex, tolerance: float
) -> int | float | complex:
    """Round a number to the nearest integer if within *tolerance*.

    For complex numbers, rounds the real and imaginary parts independently.

    Args:
        value: The number to potentially round.
        tolerance: Maximum distance from an integer to trigger rounding.

    Returns:
        The rounded value if within tolerance, otherwise *value* unchanged.
    """
    if isinstance(value, complex):
        real_rounded = round(value.real)
        imag_rounded = round(value.imag)
        real_rounded_final = (
            real_rounded if abs(value.real - real_rounded) <= tolerance else value.real
        )
        imag_rounded_final = (
            imag_rounded if abs(value.imag - imag_rounded) <= tolerance else value.imag
        )
        return complex(real_rounded_final, imag_rounded_final)
    else:
        rounded = round(value)
        if abs(value - rounded) <= tolerance:
            return rounded
        return value


### Multigraph enumeration
#
# Brute-force enumeration of small loopless multigraphs and rank-spectrum
# computation from vertex degrees.

# Adjacency matrix: list of rows, each a list of edge multiplicities.
AdjMatrix = list[list[int]]


def get_vertex_degrees(adj_matrix: AdjMatrix) -> list[int]:
    """Compute the degree of each vertex in a multigraph.

    Args:
        adj_matrix: Symmetric adjacency matrix where entry ``[i][j]`` is the
            edge multiplicity between vertices *i* and *j*.

    Returns:
        A list of vertex degrees (sum of incident edge multiplicities).
    """
    degrees: list[int] = []
    for row in adj_matrix:
        degrees.append(sum(row))
    return degrees


def get_nonisomorphic_multigraphs(v: int, e: int) -> list[AdjMatrix]:
    """Generate all non-isomorphic loopless multigraphs on *v* vertices with *e* edges.

    In the short-meridian enumeration, this produces candidate ``G_OO``
    subgraphs of the face-pairing graph (thesis Definition 5.8, §5.2.1).
    Each vertex represents an octahedron and each edge an oct-oct face
    pairing; ``v = e = n_oct`` by thesis Lemma 5.6.

    Uses brute-force distribution of edge multiplicities across vertex pairs,
    with degree-sequence pruning and exhaustive permutation checking for
    isomorphism (practical for v <= 7).

    Args:
        v: Number of vertices (octahedra).
        e: Total number of edges (oct-oct face pairings).

    Returns:
        A list of adjacency matrices, one per isomorphism class.
    """
    pairs = [(i, j) for i in range(v) for j in range(i + 1, v)]
    num_pairs = len(pairs)

    if e < 0:
        return []

    def distribute_edges(num_edges: int, num_pairs_left: int) -> Iterator[list[int]]:
        """Generate all ways to distribute num_edges among num_pairs_left pairs."""
        if num_pairs_left == 1:
            yield [num_edges]
        else:
            for i in range(num_edges + 1):
                for rest in distribute_edges(num_edges - i, num_pairs_left - 1):
                    yield [i] + rest

    def multigraph_to_adj_matrix(
        edge_multiplicities: list[int],
        num_vertices: int,
        pairs_list: list[tuple[int, int]],
    ) -> AdjMatrix:
        """Convert edge multiplicities to adjacency matrix."""
        adj: AdjMatrix = [[0] * num_vertices for _ in range(num_vertices)]
        for (u, w), mult in zip(pairs_list, edge_multiplicities):
            adj[u][w] = mult
            adj[w][u] = mult
        return adj

    def get_degree_sequence(adj: AdjMatrix) -> tuple[int, ...]:
        """Get sorted degree sequence (sum of edge multiplicities)."""
        return tuple(sorted([sum(row) for row in adj]))

    def are_isomorphic(adj1: AdjMatrix, adj2: AdjMatrix) -> bool:
        """Check if two multigraphs are isomorphic by exhaustive permutation."""
        n = len(adj1)

        if get_degree_sequence(adj1) != get_degree_sequence(adj2):
            return False

        if n <= 7:
            for perm in permutations(range(n)):
                match = True
                for i in range(n):
                    for j in range(n):
                        if adj1[i][j] != adj2[perm[i]][perm[j]]:
                            match = False
                            break
                    if not match:
                        break
                if match:
                    return True
            return False
        else:
            return False

    unique_graphs: list[AdjMatrix] = []

    for edge_multiplicities in distribute_edges(e, num_pairs):
        adj = multigraph_to_adj_matrix(edge_multiplicities, v, pairs)

        is_new = True
        for existing_adj in unique_graphs:
            if are_isomorphic(adj, existing_adj):
                is_new = False
                break

        if is_new:
            unique_graphs.append(adj)

    return unique_graphs


# Maps vertex degree in G_OO to the tuple of achievable oct-signature
# contributions (= [OTTT] tile counts) for that octahedron.  Derived from
# thesis Table 3 (tab:degree-oct-sig): each degree determines which
# admissible face labelings are possible, and the [OTTT] count of each
# labeling gives the contribution.  Degree 2 has two labelings (C and D)
# with different contributions (4 and 6).
#
# See thesis Corollary 5.12 for how these per-vertex contributions combine
# to give the set of achievable total oct-signatures.
DEGREE_RANK_MAP: dict[int, tuple[int, ...]] = {
    0: (0,),   # Labeling A only
    1: (3,),   # Labeling B only
    2: (4, 6), # Labeling C (4) or D (6)
    3: (3,),   # Labeling E only
    4: (0,),   # Labeling F only
}


def get_oct_signature_spectrum(graphs: list[AdjMatrix]) -> list[int]:
    """Compute all achievable oct-signatures across a collection of G_OO multigraphs.

    The oct-signature ``σ(f)`` is the total number of [OTTT] square tiles
    (thesis Definition 5.10).  Each octahedron contributes an [OTTT] count
    determined by its degree in ``G_OO`` (thesis Table 3).  The total
    oct-signature is the sum over all octahedra (thesis Corollary 5.12).

    For each graph, maps every vertex degree through ``DEGREE_RANK_MAP``,
    takes the Cartesian product over vertices, and sums each combination.
    Returns the union of all such sums across all graphs.

    Args:
        graphs: A list of adjacency matrices (one per isomorphism class
            of ``G_OO``).

    Returns:
        List of all distinct achievable oct-signatures.
    """
    all_sums: set[int] = set()
    for graph in graphs:
        degs = get_vertex_degrees(graph)
        rank_options = [DEGREE_RANK_MAP[d] for d in degs]
        combos = itertools.product(*rank_options)
        all_sums = all_sums.union([sum(x) for x in combos])
    return list(all_sums)
