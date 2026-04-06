"""Bracelet and necklace enumeration for binary (0/1) cyclic sequences.

A *necklace* is an equivalence class of sequences under cyclic rotation.
A *bracelet* is an equivalence class under both rotation and reflection.
Optionally, sequences can additionally identify under complement (0 ↔ 1),
so the full equivalence class includes all rotations and reflections of
both the sequence and its bitwise complement.

The ``with_complement`` flag on ``is_canonical``, ``to_canonical``,
``reduce_to_bracelets``, and ``generate_2_bracelets`` controls whether
complement symmetry is included (default: False).

The primary use case is enumerating distinct finger patterns for cusp
cellulations: each finger pattern is a cyclic 0/1 sequence, and two
patterns are equivalent if one can be obtained from the other by rotation
and reflection (and optionally global complement).

Public API:
    - ``generate_2_bracelets(n)`` — all bracelets of length *n* over {0, 1}
    - ``generate_multi_2_bracelets(n)`` — multi-component bracelets that
      partition *n* into components of size ≥ 2
    - ``is_canonical(seq)`` / ``to_canonical(seq)`` — canonical representative
      selection within bracelet equivalence classes
    - ``reduce_to_bracelets(X)`` — filter an iterable to canonical representatives
"""

from collections.abc import Iterator
from itertools import (
    product,
    combinations_with_replacement,
)

# A binary sequence is a tuple of 0/1 values representing a cyclic pattern.
BinarySeq = tuple[int, ...]


def flatten_once(nested_tuple: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    """Flatten one level of nesting, concatenating inner tuples.

    Args:
        nested_tuple: A tuple of tuples.

    Returns:
        A single tuple with all inner elements concatenated in order.
    """
    return tuple(item for sub in nested_tuple for item in sub)


def rotate(seq: BinarySeq, i: int) -> BinarySeq:
    """Rotate *seq* left by *i* positions."""
    return seq[i:] + seq[:i]


def complement(seq: BinarySeq) -> BinarySeq:
    """Return the bitwise complement of *seq* (0 ↔ 1)."""
    return tuple(1 - x for x in seq)


def all_rotations(seq: BinarySeq) -> list[BinarySeq]:
    """Return all cyclic rotations of *seq*."""
    return [rotate(seq, i) for i in range(len(seq))]


def all_reflections(seq: BinarySeq) -> list[BinarySeq]:
    """Return all rotations of *seq* and of its reversal (2n total)."""
    reflected = seq[::-1]
    return all_rotations(seq) + all_rotations(reflected)


def _candidates(seq: BinarySeq, with_complement: bool) -> list[BinarySeq]:
    """Return all equivalent forms of *seq* under the chosen symmetry group.

    Args:
        seq: A 0/1 binary sequence.
        with_complement: If True, include complement variants.

    Returns:
        List of equivalent sequences.
    """
    candidates = all_reflections(seq)
    if with_complement:
        candidates += all_reflections(complement(seq))
    return candidates


def is_canonical(seq: BinarySeq, with_complement: bool = False) -> bool:
    """Return True if *seq* is the canonical (lexicographically largest) representative.

    Args:
        seq: A 0/1 binary sequence.
        with_complement: If True, the equivalence class includes complement.
    """
    return seq == max(_candidates(seq, with_complement))


def to_canonical(seq: BinarySeq, with_complement: bool = False) -> BinarySeq:
    """Return the canonical (lexicographically largest) representative of *seq*'s bracelet class.

    Args:
        seq: Any 0/1 binary sequence.
        with_complement: If True, the equivalence class includes complement.

    Returns:
        The lexicographically largest sequence in the equivalence class.
    """
    return max(_candidates(seq, with_complement))


def reduce_to_bracelets(
    X: Iterator[BinarySeq], with_complement: bool = False
) -> Iterator[BinarySeq]:
    """Filter an iterable of sequences, yielding only canonical representatives.

    Args:
        X: Iterable of 0/1 binary sequences.
        with_complement: If True, the equivalence class includes complement.

    Yields:
        Those elements of *X* that are canonical in their bracelet class.
    """
    for x in X:
        if is_canonical(x, with_complement):
            yield x


def generate_2_bracelets(
    n: int, with_complement: bool = False
) -> Iterator[BinarySeq]:
    """Yield all distinct bracelets of length *n* over {0, 1}.

    Enumerates all 2^n binary sequences and yields only the canonical
    representative from each equivalence class.

    Args:
        n: Sequence length.
        with_complement: If True, the equivalence class includes complement.

    Yields:
        Canonical 0/1 tuples, one per distinct bracelet.
    """
    for seq in product([1, 0], repeat=n):
        if is_canonical(seq, with_complement):
            yield seq


def partitions_min_two(n: int, max_val: int | None = None) -> Iterator[list[int]]:
    """Yield all integer partitions of *n* with every part ≥ 2.

    Parts are yielded in non-increasing order.  Used to enumerate the ways
    to split *n* fingers across multiple cusp components (each component
    must have at least 2 fingers).

    Args:
        n: The integer to partition.
        max_val: Largest part allowed (defaults to *n*; used internally
            for recursion).

    Yields:
        Partitions as lists of ints in non-increasing order.
    """
    if max_val is None:
        max_val = n
    if n == 0:
        yield []
    else:
        for i in range(min(max_val, n), 1, -1):
            for p in partitions_min_two(n - i, i):
                yield [i] + p


def generate_multi_2_bracelets_from_partition(
    partition: list[int],
) -> Iterator[tuple[BinarySeq, ...]]:
    """Yield all distinct multi-component bracelets for a given size partition.

    For each distinct part size in the partition, generates all
    combinations-with-replacement of bracelets of that size (respecting
    multiplicity), then takes the Cartesian product across part sizes.

    Args:
        partition: A list of component sizes (each ≥ 2), e.g. ``[4, 2, 2]``.

    Yields:
        Tuples of bracelets, one per component, flattened into a single tuple.
    """
    uniq_elements = sorted(list(set(partition)))
    factors = []
    for x in uniq_elements:
        count = partition.count(x)
        factors.append(
            combinations_with_replacement(
                generate_2_bracelets(x, with_complement=True), count
            )
        )

    return (flatten_once(T) for T in product(*factors))


def generate_multi_2_bracelets(n: int) -> Iterator[tuple[BinarySeq, ...]]:
    """Yield all distinct multi-component bracelets that partition *n*.

    Iterates over all integer partitions of *n* (parts ≥ 2), and for each
    partition yields all distinct assignments of bracelets to components.

    Args:
        n: Total number of fingers to distribute across components.

    Yields:
        Flattened tuples of component bracelets.
    """
    for p in partitions_min_two(n):
        for mb in generate_multi_2_bracelets_from_partition(p):
            yield mb
