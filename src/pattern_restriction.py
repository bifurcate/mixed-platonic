import itertools
from finger_cusp import to_finger_pattern_list, to_finger_pattern_str
from bracelets import is_canonical, to_canonical, reduce_to_bracelets
from binary_loop import integrate, differentiate, get_binary_tuples

oct_type_vecs = [
    (3, 3, 0),
    (3, 0, 3),
    (4, 1, 1),
    (0, 6, 0),
    (0, 0, 6),
    (6, 0, 0),
]


def is_valid_oct_sig(a, b, c):
    if a == 0 or a % 2 != 0 or b != c:
        return False
    # if (a // 2 + b) != (a+b+c)/2:
    #     return False
    return True


def potential_vecs(n):
    combos = itertools.combinations_with_replacement(oct_type_vecs, n)
    filtered = []
    for combo in combos:
        csum = (0, 0, 0)
        for vec in combo:
            csum = (
                csum[0] + vec[0],
                csum[1] + vec[1],
                csum[2] + vec[2],
            )
            # csum[0] += vec[0]
            # csum[1] += vec[1]
            # csum[2] += vec[2]
        if is_valid_oct_sig(csum[0], csum[1], csum[2]):
            filtered.append(csum)

    unique = []
    for x in filtered:
        if x not in unique:
            unique.append(x)
    return unique


def _get_partitions_of_length(n, length):
    """
    Helper function that returns all partitions of n into exactly length parts,
    each as a tuple in non-increasing order.
    """
    if length == 1:
        return [(n,)] if n > 0 else []

    if length > n:
        return []

    partitions = []
    # The first part can range from n - length + 1 down to 1
    for first_part in range(n - length + 1, 0, -1):
        remaining = n - first_part
        remaining_length = length - 1

        # Recursively get partitions of the remainder
        sub_partitions = _get_partitions_of_length(remaining, remaining_length)

        for sub_partition in sub_partitions:
            # Only include if first_part is >= the largest part in sub_partition
            if not sub_partition or first_part >= sub_partition[0]:
                partitions.append((first_part,) + sub_partition)

    return partitions[::-1]  # Reverse to get lexicographic order


def get_partitions(n, length):
    """
    Returns all partitions of n with size <= length.
    Each partition is represented as a tuple padded with leading zeros to length.

    Args:
        n: The natural number to partition
        length: The maximum number of parts (tuples will be padded to this length)

    Returns:
        A list of tuples, each of size length, with leading zeros and the partition
        in non-increasing order on the right
    """
    all_partitions = []

    if n == 0:
        return [
            (0,) * length,
        ]

    for partition_length in range(1, length + 1):
        partitions = _get_partitions_of_length(n, partition_length)

        for partition in partitions:
            # Pad with zeros on the left
            padded = (0,) * (length - partition_length) + partition
            all_partitions.append(padded)

    return all_partitions


def toggle_sign(c):
    if c == "+":
        return "-"
    if c == "-":
        return "+"
    return None


def finger_pattern_from_partitions(num_groups, in_p, out_p):
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


def finger_patterns_from_oct_sig(a, b, c):
    paren_pairs = a // 2

    in_partitions = get_partitions(c, paren_pairs)
    out_partitions = get_partitions(b, paren_pairs)

    total_product = itertools.product(in_partitions, out_partitions)

    finger_patterns = []
    for in_p, out_p in total_product:
        fp = finger_pattern_from_partitions(paren_pairs, in_p, out_p)
        finger_patterns.append(fp)

    return finger_patterns


def derivative_finger_pattern(s):
    r = ""
    for i in range(len(s)):
        if s[i] == s[(i + 1) % len(s)]:
            r += "+"
        else:
            r += "-"
    return r


def generate_finger_patterns(n):
    for vec in potential_vecs(n):
        fps = finger_patterns_from_oct_sig(vec[0], vec[1], vec[2])
        for fp in fps:
            fpl = tuple(to_finger_pattern_list(fp))
            if derivative_finger_pattern(fp).count("+") == 3 * n and is_canonical(fpl):
                # if is_canonical(fpl):
                yield (vec, to_finger_pattern_str(fpl))


def pattern_from_parts(odd_part, even_part):
    odd_perms = list(set(itertools.permutations(odd_part)))
    even_perms = list(set(itertools.permutations(even_part)))

    perm_product = itertools.product(odd_perms, even_perms)

    P = set()
    for odd, even in perm_product:
        A = []
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


def patterns_for_rank(n, r):
    b = (n - r) // 2

    odd_parts = get_partitions(b, r // 2)
    even_parts = get_partitions(b, r // 2)

    total_product = itertools.product(odd_parts, even_parts)
    patterns = set()
    for odd, even in total_product:
        patterns = patterns.union(pattern_from_parts(odd, even))

    return patterns


def generate_patterns(n):
    for vec in potential_vecs(n // 6):
        print(vec)
        patterns = patterns_for_rank(n, vec[0])
        for p in patterns:
            yield tuple(p)


def generate_patterns_2(n):
    X = get_binary_tuples(n, n // 2)
    X = reduce_to_bracelets(X)
    return list(X)


def round_with_tolerance(value, tolerance):
    """
    Rounds a number to the nearest integer if it is within a specific tolerance of that integer.
    For complex numbers, rounds the real and imaginary parts separately.

    Args:
        value: The number to potentially round (int, float, or complex)
        tolerance: The tolerance threshold (how close to an integer it must be)

    Returns:
        The rounded integer/complex if within tolerance, otherwise the original value
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
