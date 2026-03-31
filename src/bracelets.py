from itertools import (
    product,
    combinations,
    combinations_with_replacement,
)


def flatten_1(nested_tuple):
    return tuple(item for sub in nested_tuple for item in sub)


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


def balanced_strings(n):
    if n % 2 != 0:
        return []

    k = n // 2
    result = []

    for plus_positions in combinations(range(n), k):
        s = [-1] * n
        for i in plus_positions:
            s[i] = 1
        result.append(tuple(s))

    return result


def integrate_string(seq, c):
    int_seq = [1]
    n = len(seq)
    for i in range(len(seq)):
        if seq[i] == seq[(i + 1) % n]:
            int_seq.append(c)


def generate_balanced_bracelets(n: int):
    """Yield all distinct bracelets of length n over 2 colors."""
    for seq in balanced_strings(n):
        if is_canonical(seq):
            yield tuple(int(x) for x in seq)


def reduce_to_bracelets(X):
    for x in X:
        if is_canonical(x):
            yield x


def is_canonical(seq):
    """Return True if seq is the lexicographically smallest of its bracelet class."""
    candidates = equivalence_class(seq)
    return seq == max(candidates)


def to_canonical(seq):
    """Return True if seq is the lexicographically smallest of its bracelet class."""
    candidates = equivalence_class(seq)
    return max(candidates)


def generate_2_bracelets(n: int):
    """Yield all distinct bracelets of length n over k colors."""
    for seq in product([1, -1], repeat=n):
        if is_canonical(seq):
            yield seq


def partitions_no_ones(n, max_val=None):
    if max_val is None:
        max_val = n
    if n == 0:
        yield []
    else:
        for i in range(min(max_val, n), 1, -1):
            for p in partitions_no_ones(n - i, i):
                yield [i] + p


def generate_multi_2_bracelets_from_partition(partition):
    uniq_elements = sorted(list(set(partition)))
    factors = []
    for x in uniq_elements:
        count = partition.count(x)
        factors.append(combinations_with_replacement(generate_2_bracelets(x), count))

    return (flatten_1(T) for T in product(*factors))


def generate_multi_2_bracelets(n: int):
    for p in partitions_no_ones(n):
        for mb in generate_multi_2_bracelets_from_partition(p):
            yield mb
