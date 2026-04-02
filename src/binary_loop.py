"""Discrete calculus on cyclic binary (mod 2) sequences.

This module provides operations on binary loops — cyclic sequences of 0s
and 1s with mod-2 arithmetic:

    - ``integrate`` / ``differentiate``: discrete antiderivative and derivative.
    - ``binary_tuples_of_weight``: enumerate all binary tuples with a given
      Hamming weight.
    - ``hamming_weight``: count the number of 1s in a binary sequence.
    - ``has_rotational_symmetry``: test whether a binary sequence is invariant
      under a given cyclic shift.
"""

from itertools import combinations

# Type alias for a binary (0/1) sequence.
BinaryLoop = tuple[int, ...]


def integrate(loop: list[int], c: int) -> list[int]:
    """Compute a discrete antiderivative of a cyclic binary loop (mod 2).

    Starting from initial value *c*, accumulates ``(loop[i] + running) % 2``
    at each step.  The loop must be *orientable*: the accumulated value after
    a full pass must equal *c* again.

    Args:
        loop: A cyclic binary sequence (list of 0s and 1s).
        c: Initial value (0 or 1).

    Returns:
        The antiderivative as a list of 0/1 values of the same length.

    Raises:
        ValueError: If the loop is not orientable (the running value after
            a full cycle does not return to *c*).
    """
    result: list[int] = []
    n = len(loop)
    val = c
    for i in range(n):
        result.append(val)
        val = (loop[i] + val) % 2

    if val != c:
        raise ValueError("Unorientable String")

    return result


def differentiate(loop: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    """Compute the discrete derivative of a cyclic binary loop (mod 2).

    The derivative at position *i* is ``(loop[i] + loop[(i+1) % n]) % 2``,
    which is 0 when neighbours agree and 1 when they differ.

    Args:
        loop: A cyclic binary sequence.

    Returns:
        The derivative as a tuple of 0/1 values of the same length.
    """
    result: list[int] = []
    n = len(loop)
    for i in range(n):
        val = (loop[i] + loop[(i + 1) % n]) % 2
        result.append(val)
    return tuple(result)


def binary_tuples_of_weight(n: int, k: int) -> list[BinaryLoop]:
    """Generate all binary tuples of length *n* with exactly *k* ones.

    Args:
        n: The length of each tuple.
        k: The Hamming weight (number of 1s).

    Returns:
        A list of binary tuples, each with exactly *k* ones and *n − k* zeros.
        Empty list if *k* < 0 or *k* > *n*.
    """
    if k > n or k < 0:
        return []

    tuples: list[BinaryLoop] = []
    for positions in combinations(range(n), k):
        binary_tuple = [0] * n
        for pos in positions:
            binary_tuple[pos] = 1
        tuples.append(tuple(binary_tuple))

    return tuples


def hamming_weight(binary_seq: list[int] | tuple[int, ...]) -> int:
    """Return the Hamming weight (number of 1s) of a binary sequence.

    Args:
        binary_seq: A binary sequence (list or tuple of 0s and 1s).

    Returns:
        The count of 1s.
    """
    return sum(binary_seq)


def has_rotational_symmetry(binary_seq: list[int] | tuple[int, ...], n: int) -> bool:
    """Check if a binary sequence is invariant under a right-shift of *n* positions.

    Args:
        binary_seq: A binary sequence (list or tuple).
        n: Number of positions to right-shift.

    Returns:
        True if shifting *binary_seq* right by *n* yields the same sequence.
    """
    length = len(binary_seq)
    if length == 0:
        return True

    n = n % length

    if n == 0:
        return True

    rotated = binary_seq[-n:] + binary_seq[:-n]

    return rotated == binary_seq
