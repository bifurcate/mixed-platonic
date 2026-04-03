"""Restrict cusp pattern enumeration using octahedron signature constraints.

This module provides tools to prune the space of finger patterns by
exploiting structural constraints from octahedron decompositions.  The
key idea: each octahedron contributes a characteristic "type vector"
``(a, b, c)`` counting how its six square cusp cells distribute across
three edge-pairing categories.  Summing these vectors over all octahedra
yields an *octahedron signature* for the cusp, which constrains which
finger patterns are geometrically realizable.

The pipeline has three stages:

1. **Signature enumeration** — ``valid_oct_signatures`` computes all
   achievable octahedron signatures for *n* octahedra by summing
   combinations of ``OCT_TYPE_VECTORS`` and filtering by validity.
2. **Pattern construction** — ``finger_patterns_from_oct_signature``
   builds candidate finger pattern strings from integer partitions that
   distribute the signature components across groups.
3. **Canonicalization and filtering** — ``generate_finger_patterns``
   applies a derivative test and bracelet canonicality to yield only
   distinct, valid patterns.

Additionally, ``generate_balanced_patterns`` provides a simpler
combinatorial approach using balanced binary tuples reduced to bracelets.

The module also includes multigraph enumeration utilities
(``get_nonisomorphic_multigraphs``, ``get_rank_spectrum``) used to
compute achievable rank spectra from vertex-degree constraints.
"""

import itertools
from collections.abc import Iterator
from itertools import permutations

from finger_cusp import to_finger_pattern_list, to_finger_pattern_str
from bracelets import BinarySeq, is_canonical, to_canonical, reduce_to_bracelets
from binary_loop import binary_tuples_of_weight

# Each octahedron has 6 square cusp cells.  A type vector ``(a, b, c)``
# records how those 6 squares distribute across three edge-pairing
# categories.  The entries always sum to 6.
OctTypeVector = tuple[int, int, int]

OCT_TYPE_VECTORS: list[OctTypeVector] = [
    (3, 3, 0),
    (3, 0, 3),
    (4, 1, 1),
    (0, 6, 0),
    (0, 0, 6),
    (6, 0, 0),
]

# An octahedron signature ``(a, b, c)`` is the sum of type vectors over
# all octahedra in the decomposition.  Valid signatures satisfy:
# a > 0, a even, and b == c.
OctSignature = tuple[int, int, int]


def is_valid_oct_signature(a: int, b: int, c: int) -> bool:
    """Check whether ``(a, b, c)`` is a valid octahedron signature.

    A signature is valid when *a* is positive and even, and *b* equals *c*.

    Args:
        a: Count of squares in the first edge-pairing category.
        b: Count in the second category.
        c: Count in the third category.

    Returns:
        True if the signature is valid.
    """
    if a == 0 or a % 2 != 0 or b != c:
        return False
    return True


def valid_oct_signatures(n: int) -> list[OctSignature]:
    """Enumerate all distinct valid octahedron signatures for *n* octahedra.

    Forms all combinations-with-replacement of *n* type vectors from
    ``OCT_TYPE_VECTORS``, sums each combination component-wise, and
    keeps only those sums that pass ``is_valid_oct_signature``.

    Args:
        n: Number of octahedra.

    Returns:
        De-duplicated list of valid ``(a, b, c)`` signature tuples.
    """
    combos = itertools.combinations_with_replacement(OCT_TYPE_VECTORS, n)
    filtered: list[OctSignature] = []
    for combo in combos:
        csum: OctSignature = (0, 0, 0)
        for vec in combo:
            csum = (
                csum[0] + vec[0],
                csum[1] + vec[1],
                csum[2] + vec[2],
            )
        if is_valid_oct_signature(csum[0], csum[1], csum[2]):
            filtered.append(csum)

    unique: list[OctSignature] = []
    for x in filtered:
        if x not in unique:
            unique.append(x)
    return unique


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


def toggle_sign(c: str) -> str | None:
    """Flip a sign character: ``"+"`` ↔ ``"-"``.

    Args:
        c: A single-character sign string.

    Returns:
        The opposite sign, or None if *c* is neither ``"+"`` nor ``"-"``.
    """
    if c == "+":
        return "-"
    if c == "-":
        return "+"
    return None


def finger_pattern_from_partitions(
    num_groups: int, in_p: tuple[int, ...], out_p: tuple[int, ...]
) -> str:
    """Build a finger pattern string from in/out partition specifications.

    Constructs a cyclic ``+``/``-`` string by iterating over *num_groups*
    groups.  Within each group, the current sign is repeated according to
    the in-partition, then the sign alternates according to the
    out-partition.

    Args:
        num_groups: Number of groups (equal to ``a // 2`` from the signature).
        in_p: In-partition tuple (one entry per group).
        out_p: Out-partition tuple (one entry per group).

    Returns:
        A finger pattern string of ``+`` and ``-`` characters.
    """
    s = ""
    c = "+"
    for i in range(num_groups):
        s += c
        for j in range(in_p[i]):
            s += c
        s += c

        for j in range(out_p[i]):
            c = toggle_sign(c)
            s += c

        c = toggle_sign(c)
    return s


def finger_patterns_from_oct_signature(a: int, b: int, c: int) -> list[str]:
    """Generate all finger pattern strings compatible with an octahedron signature.

    Distributes the *b* and *c* counts across ``a // 2`` groups via integer
    partitions, then builds a finger pattern for each (in, out) partition pair.

    Args:
        a: First signature component (must be positive and even).
        b: Second signature component.
        c: Third signature component (must equal *b*).

    Returns:
        List of finger pattern strings.
    """
    paren_pairs = a // 2

    in_partitions = get_partitions(c, paren_pairs)
    out_partitions = get_partitions(b, paren_pairs)

    total_product = itertools.product(in_partitions, out_partitions)

    finger_patterns: list[str] = []
    for in_p, out_p in total_product:
        fp = finger_pattern_from_partitions(paren_pairs, in_p, out_p)
        finger_patterns.append(fp)

    return finger_patterns


def derivative_finger_pattern(s: str) -> str:
    """Compute the discrete derivative of a finger pattern string.

    At each position, outputs ``"+"`` if the character and its cyclic
    successor are the same sign, or ``"-"`` if they differ.

    Args:
        s: A finger pattern string of ``+``/``-`` characters.

    Returns:
        The derivative string of the same length.
    """
    r = ""
    for i in range(len(s)):
        if s[i] == s[(i + 1) % len(s)]:
            r += "+"
        else:
            r += "-"
    return r


def generate_finger_patterns(n: int) -> Iterator[tuple[OctSignature, str]]:
    """Yield all valid canonical finger patterns for *n* octahedra.

    For each valid octahedron signature, constructs candidate finger patterns
    and filters them by two criteria:

    1. The derivative must have exactly ``3n`` ``"+"`` characters (ensuring
       the correct number of same-sign adjacent pairs).
    2. The pattern must be the canonical representative of its bracelet class.

    Args:
        n: Number of octahedra.

    Yields:
        ``(signature, pattern_string)`` pairs.
    """
    for vec in valid_oct_signatures(n):
        fps = finger_patterns_from_oct_signature(vec[0], vec[1], vec[2])
        for fp in fps:
            fpl = tuple(to_finger_pattern_list(fp))
            if derivative_finger_pattern(fp).count("+") == 3 * n and is_canonical(fpl):
                yield (vec, to_finger_pattern_str(fpl))


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


def patterns_for_rank(n: int, r: int) -> set[BinarySeq]:
    """Enumerate all canonical binary patterns of length *n* with rank *r*.

    Distributes ``(n - r) / 2`` zeros across ``r / 2`` odd and even slots
    via integer partitions, then builds and canonicalizes all resulting
    patterns.

    Args:
        n: Total pattern length.
        r: Rank (must have same parity as *n*; ``r / 2`` must be integral).

    Returns:
        Set of canonical binary sequences.
    """
    b = (n - r) // 2

    odd_parts = get_partitions(b, r // 2)
    even_parts = get_partitions(b, r // 2)

    total_product = itertools.product(odd_parts, even_parts)
    patterns: set[BinarySeq] = set()
    for odd, even in total_product:
        patterns = patterns.union(pattern_from_parts(odd, even))

    return patterns


def generate_patterns(n: int) -> Iterator[tuple[int, ...]]:
    """Yield all binary patterns of length *n* consistent with octahedron signatures.

    For each valid signature of ``n // 6`` octahedra, generates patterns
    matching the signature's rank.

    Args:
        n: Total pattern length (must be divisible by 6).

    Yields:
        Binary pattern tuples.
    """
    for vec in valid_oct_signatures(n // 6):
        patterns = patterns_for_rank(n, vec[0])
        for p in patterns:
            yield tuple(p)


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

    Uses brute-force distribution of edge multiplicities across vertex pairs,
    with degree-sequence pruning and exhaustive permutation checking for
    isomorphism (practical for v <= 7).

    Args:
        v: Number of vertices.
        e: Total number of edges (counting multiplicity).

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


# Maps vertex degree to the tuple of possible rank contributions for that
# degree.  Used by ``get_rank_spectrum`` to enumerate all feasible rank
# sums over a multigraph's vertices.
DEGREE_RANK_MAP: dict[int, tuple[int, ...]] = {
    0: (0,),
    1: (3,),
    2: (4, 6),
    3: (3,),
    4: (0,),
}


def get_rank_spectrum(graphs: list[AdjMatrix]) -> list[int]:
    """Compute all achievable rank sums across a collection of multigraphs.

    For each graph, maps every vertex degree through ``DEGREE_RANK_MAP`` to
    get the set of possible rank contributions, then takes the Cartesian
    product over vertices and sums each combination.  Returns the union of
    all such sums across all graphs.

    Args:
        graphs: A list of adjacency matrices.

    Returns:
        List of all distinct achievable rank sums.
    """
    all_sums: set[int] = set()
    for graph in graphs:
        degs = get_vertex_degrees(graph)
        rank_options = [DEGREE_RANK_MAP[d] for d in degs]
        combos = itertools.product(*rank_options)
        all_sums = all_sums.union([sum(x) for x in combos])
    return list(all_sums)
