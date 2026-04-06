"""Cusp cellulation constructors for the long-meridian case.

In the long-meridian family, each cusp tiling is described by a cyclic
sequence of strip labels drawn from the alphabet ``{a, b, c, d, e}``.
Each label specifies a vertical strip of cusp cells (triangles and/or
squares) with fixed internal edge pairings.  Consecutive strips are then
connected by additional pairings that depend on the two- or three-letter
subsequence at the junction.

The generation pipeline has three stages:

1. **Enumeration** — ``build_cusp_sequences`` uses the transition graph
   ``SEQ_GEN_GRAPH`` to enumerate all valid cyclic label sequences of a
   given length, filtering by polygon-count divisibility and bracelet
   canonicity.
2. **Strip construction** — ``add_strip`` instantiates the cusp cells for
   one label using ``STRIP_TEMPLATES`` and applies the internal pairings.
3. **Strip connection** — ``connect_strips`` applies the inter-strip
   pairings from ``CONNECT_MR_TEMPLATES`` (mid-right, two-letter context)
   and ``CONNECT_LR_TEMPLATES`` (left-right, three-letter context).

Polygon counts per strip label (triangles, squares)::

    a → 2 tri, 2 sqr    b → 2 tri, 0 sqr    c → 2 tri, 1 sqr
    d → 4 tri, 2 sqr    e → 4 tri, 2 sqr
"""

from collections.abc import Iterator

from base import CuspCell, Sqr, Tri, SQR, TRI

from construction import Cusp

# Strip label type: single-character string from the set {a, b, c, d, e}.
StripLabel = str

# A long-cusp pattern is a cyclic sequence of strip labels, e.g. "abdce".
LongCuspPattern = str

# Transition graph for valid label sequences.  Each label maps to the
# tuple of labels that may follow it in a valid cusp sequence.
SEQ_GEN_GRAPH: dict[StripLabel, tuple[StripLabel, ...]] = {
    "a": ("b",),
    "b": ("a", "d"),
    "c": ("c", "e"),
    "d": ("c", "e"),
    "e": ("b",),
}

# Number of (triangles, squares) contributed by each strip label.
POLY_COUNT: dict[StripLabel, tuple[int, int]] = {
    "a": (2, 2),
    "b": (2, 0),
    "c": (2, 1),
    "d": (4, 2),
    "e": (4, 2),
}

# Internal structure of each strip type.
#
# "polys" lists the cell types (TRI or SQR) in top-to-bottom order within
# the strip.  "pairings" lists the internal edge pairings as 4-tuples:
#   (src_local_idx, src_edge_spec, tgt_local_idx, tgt_edge_spec)
# where local indices refer to positions in the "polys" list.
StripTemplate = dict[str, list]
STRIP_TEMPLATES: dict[StripLabel, StripTemplate] = {
    "a": {
        "polys": [
            SQR,
            TRI,
            TRI,
            SQR,
        ],
        "pairings": [
            (
                0,
                (2, 3),
                1,
                (1, 3),
            ),
            (
                2,
                (2, 3),
                3,
                (1, 4),
            ),
            (
                3,
                (2, 3),
                0,
                (1, 4),
            ),
        ],
    },
    "b": {
        "polys": [
            TRI,
            TRI,
        ],
        "pairings": [
            (
                0,
                (2, 3),
                1,
                (1, 3),
            ),
        ],
    },
    "c": {
        "polys": [
            TRI,
            TRI,
            SQR,
        ],
        "pairings": [
            (
                1,
                (2, 3),
                2,
                (1, 4),
            ),
            (
                2,
                (2, 3),
                0,
                (1, 3),
            ),
        ],
    },
    "d": {
        "polys": [
            TRI,
            SQR,
            TRI,
            SQR,
            TRI,
            TRI,
        ],
        "pairings": [
            (
                0,
                (2, 3),
                1,
                (2, 1),
            ),
            (
                1,
                (3, 4),
                2,
                (2, 1),
            ),
            (
                2,
                (2, 3),
                3,
                (1, 4),
            ),
            (
                3,
                (2, 3),
                4,
                (1, 3),
            ),
            (
                4,
                (2, 3),
                5,
                (2, 1),
            ),
            (
                5,
                (2, 3),
                0,
                (1, 3),
            ),
        ],
    },
    "e": {
        "polys": [
            TRI,
            SQR,
            TRI,
            SQR,
            TRI,
            TRI,
        ],
        "pairings": [
            (
                0,
                (2, 3),
                1,
                (1, 4),
            ),
            (
                1,
                (2, 3),
                2,
                (1, 3),
            ),
            (
                2,
                (2, 3),
                3,
                (2, 1),
            ),
            (
                3,
                (3, 4),
                4,
                (2, 1),
            ),
            (
                4,
                (2, 3),
                5,
                (1, 3),
            ),
            (
                5,
                (2, 3),
                0,
                (2, 1),
            ),
        ],
    },
}

# Inter-strip pairings keyed by the two-letter subsequence (mid, right).
# Each entry is a list of 4-tuples:
#   (mid_local_idx, mid_edge_spec, right_local_idx, right_edge_spec)
# referencing cell positions within the respective strips.
ConnectTemplate = list[tuple[int, tuple[int, int], int, tuple[int, int]]]
CONNECT_MR_TEMPLATES: dict[str, ConnectTemplate] = {
    "ab": [
        (
            1,
            (2, 3),
            0,
            (2, 1),
        ),
        (
            2,
            (1, 3),
            1,
            (1, 2),
        ),
    ],
    "ba": [
        (
            0,
            (1, 3),
            1,
            (1, 2),
        ),
        (
            1,
            (2, 3),
            2,
            (2, 1),
        ),
    ],
    "bd": [
        (
            0,
            (1, 3),
            1,
            (2, 3),
        ),
        (
            1,
            (2, 3),
            3,
            (2, 1),
        ),
    ],
    "de": [
        (
            1,
            (1, 4),
            3,
            (2, 3),
        ),
        (
            2,
            (1, 3),
            5,
            (1, 2),
        ),
        (
            3,
            (3, 4),
            1,
            (2, 1),
        ),
        (
            5,
            (1, 3),
            2,
            (1, 2),
        ),
    ],
    "eb": [
        (
            1,
            (3, 4),
            0,
            (2, 1),
        ),
        (
            3,
            (1, 4),
            1,
            (1, 2),
        ),
    ],
    "dc": [
        (
            1,
            (1, 4),
            0,
            (1, 2),
        ),
        (
            3,
            (3, 4),
            1,
            (2, 1),
        ),
        (
            5,
            (3, 1),
            2,
            (2, 1),
        ),
    ],
    "ce": [
        (
            0,
            (2, 3),
            1,
            (2, 1),
        ),
        (
            1,
            (1, 3),
            3,
            (2, 3),
        ),
        (
            2,
            (3, 4),
            5,
            (2, 1),
        ),
    ],
    "cc": [
        (
            0,
            (2, 3),
            1,
            (2, 1),
        ),
        (
            1,
            (1, 3),
            0,
            (1, 2),
        ),
    ],
}

# Inter-strip pairings keyed by the three-letter subsequence (left, mid, right).
# These handle "long-range" pairings that skip over the middle strip, connecting
# cells in the left strip directly to cells in the right strip.
CONNECT_LR_TEMPLATES: dict[str, ConnectTemplate] = {
    "eba": [
        (
            0,
            (1, 3),
            0,
            (1, 2),
        ),
        (
            4,
            (1, 3),
            3,
            (1, 2),
        ),
    ],
    "aba": [
        (
            0,
            (3, 4),
            0,
            (1, 2),
        ),
        (
            3,
            (3, 4),
            3,
            (1, 2),
        ),
    ],
    "abd": [
        (
            0,
            (3, 4),
            0,
            (2, 1),
        ),
        (
            3,
            (3, 4),
            4,
            (2, 1),
        ),
    ],
    "ebd": [
        (
            0,
            (1, 3),
            0,
            (1, 2),
        ),
        (
            4,
            (1, 3),
            4,
            (1, 2),
        ),
    ],
    "cce": [
        (
            2,
            (3, 4),
            2,
            (2, 1),
        ),
    ],
    "dce": [
        (
            2,
            (1, 3),
            2,
            (1, 2),
        ),
    ],
    "ccc": [
        (
            2,
            (3, 4),
            2,
            (1, 2),
        ),
    ],
    "dcc": [
        (
            2,
            (1, 3),
            2,
            (1, 2),
        ),
    ],
}


def rotate(s: str, i: int) -> str:
    """Rotate string *s* left by *i* positions."""
    return s[i:] + s[:i]


def all_rotations(s: str) -> list[str]:
    """Return all cyclic rotations of *s*."""
    return [rotate(s, i) for i in range(len(s))]


def is_canonical(s: str) -> bool:
    """Return True if *s* is the lexicographically largest rotation of itself.

    Used to select a unique representative from the equivalence class of
    cyclic rotations (bracelet class) of a label sequence.
    """
    candidates = all_rotations(s)
    return s == max(candidates)


def get_poly_count(lc_pattern: LongCuspPattern) -> list[int]:
    """Sum the (triangle, square) cell counts over all strip labels in a pattern.

    Args:
        lc_pattern: A long-cusp pattern string, e.g. ``"abdc"``.

    Returns:
        Two-element list ``[num_triangles, num_squares]``.
    """
    count = [0, 0]
    for c in lc_pattern:
        char_count = POLY_COUNT[c]
        count[0] += char_count[0]
        count[1] += char_count[1]

    return count


def next_seq_gen(gen: list[str]) -> list[str]:
    """Extend every sequence in *gen* by one step using ``SEQ_GEN_GRAPH``.

    For each sequence, appends every valid successor of its last character,
    producing all one-step extensions.

    Args:
        gen: Current generation of partial label sequences.

    Returns:
        Next generation of sequences, each one character longer.
    """
    next_gen: list[str] = []

    for s in gen:
        next_chars = SEQ_GEN_GRAPH[s[-1]]
        for c in next_chars:
            next_gen.append(s + c)

    return next_gen


def build_cusp_sequences(n: int) -> list[LongCuspPattern]:
    """Enumerate all valid long-cusp patterns up to length *n*.

    Grows sequences from single-character seeds using the transition graph,
    collecting those that form valid closed loops (first character equals
    last) and satisfy:

    - Triangle count divisible by 4 (each tetrahedron contributes 4 triangles).
    - Square count divisible by 6 (each octahedron contributes 6 squares).
    - The pattern is the canonical (lexicographically largest) rotation of
      its equivalence class, avoiding duplicate patterns.

    Args:
        n: Maximum number of generation steps (sequence length before
            trimming the closing character).

    Returns:
        List of canonical long-cusp pattern strings.
    """
    c_seqs: list[LongCuspPattern] = []
    gen: list[str] = ["a", "b", "c", "d", "e"]

    for _ in range(n):
        gen = next_seq_gen(gen)
        for s in gen:
            # Only keep closed loops (last char can transition back to first)
            if s[0] != s[-1]:
                continue

            loop = s[:-1]
            p_count = get_poly_count(loop)
            if p_count[0] % 4 == 0 and p_count[1] % 6 == 0 and is_canonical(loop):
                c_seqs.append(loop)

    return c_seqs


class LongCuspConstructor:
    """Build a connected cusp tiling from a cyclic long-cusp pattern string.

    The generator processes the pattern in two passes:

    1. **Strip creation** — For each label character in the pattern, instantiate
       the cusp cells specified by ``STRIP_TEMPLATES`` and apply the internal
       edge pairings within the strip.
    2. **Strip connection** — For each position in the cyclic pattern, look up
       the two-letter (mid-right) and three-letter (left-mid-right) context
       windows in ``CONNECT_MR_TEMPLATES`` and ``CONNECT_LR_TEMPLATES`` to
       apply inter-strip edge pairings.

    Triangle and square indices are assigned sequentially across all strips,
    so a pattern like ``"abd"`` with strips containing [Tri, Tri], [Sqr, Tri,
    Tri, Sqr], ... will number cells globally.

    Attributes:
        cusp: The cusp tiling being populated.
        long_cusp_pattern: Cyclic sequence of strip labels, e.g. ``"abdce"``.
        tri_idx: Running counter for the next triangle index (starts at -1,
            incremented before use).
        sqr_idx: Running counter for the next square index.
        strips: List of cell lists, one per strip, in pattern order.  Each
            inner list contains the ``CuspCell`` objects for that strip.
    """

    def __init__(self, cusp: Cusp, long_cusp_pattern: LongCuspPattern) -> None:
        self.cusp = cusp
        self.long_cusp_pattern = long_cusp_pattern
        self.tri_idx: int = -1
        self.sqr_idx: int = -1
        self.strips: list[list[CuspCell]] = []

    def generate(self) -> Cusp:
        """Build the complete cusp tiling: create strips then connect them.

        Returns:
            The populated ``Cusp`` object with all cells and edge pairings.
        """
        n = len(self.long_cusp_pattern)

        for c in self.long_cusp_pattern:
            self.add_strip(c)

        for i in range(n):
            self.connect_strips(i)

        return self.cusp

    def traversal(self) -> Iterator[CuspCell]:
        """Yield all cusp cells in strip order (top to bottom within each strip).

        Yields:
            Each cusp cell, iterating through strips left-to-right and
            within each strip top-to-bottom.
        """
        for strip in self.strips:
            for poly in strip:
                yield poly

    def connect_strips(self, idx: int) -> None:
        """Apply inter-strip edge pairings at position *idx* in the cyclic pattern.

        Reads the three-character context window ``(left, mid, right)`` around
        position *idx* (with cyclic wrap-around), then:

        1. Applies the two-letter ``CONNECT_MR_TEMPLATES[mid+right]`` pairings
           between the mid and right strips.
        2. If a three-letter template ``CONNECT_LR_TEMPLATES[left+mid+right]``
           exists, applies those long-range pairings between the left and
           right strips.

        Args:
            idx: Position in the cyclic pattern identifying the right strip.

        Raises:
            KeyError: If the two-letter subsequence is not in
                ``CONNECT_MR_TEMPLATES``.
        """
        n = len(self.long_cusp_pattern)
        cL = self.long_cusp_pattern[(idx - 2) % n]
        cM = self.long_cusp_pattern[(idx - 1) % n]
        cR = self.long_cusp_pattern[idx % n]
        cMR = cM + cR
        cLMR = cL + cM + cR

        sL = self.strips[(idx - 2) % n]
        sM = self.strips[(idx - 1) % n]
        sR = self.strips[idx % n]

        if cMR not in CONNECT_MR_TEMPLATES:
            raise KeyError(f"'{cMR}' at {idx} is not a valid pattern subsequence")

        # Two-letter (mid-right) pairings
        MR_pairings = CONNECT_MR_TEMPLATES[cMR]
        for pr in MR_pairings:
            self.cusp.pair(
                sM[pr[0]],
                pr[1],
                sR[pr[2]],
                pr[3],
            )

        # Three-letter (left-right) pairings, if any
        if cLMR not in CONNECT_LR_TEMPLATES:
            return

        LR_pairings = CONNECT_LR_TEMPLATES[cLMR]
        for pr in LR_pairings:
            self.cusp.pair(
                sL[pr[0]],
                pr[1],
                sR[pr[2]],
                pr[3],
            )

    def add_strip(self, label: StripLabel) -> None:
        """Instantiate one strip's cusp cells and apply its internal pairings.

        Looks up the strip template for *label*, creates ``Tri`` or ``Sqr``
        cells with globally unique indices, applies the template's internal
        edge pairings, and appends the cell list to ``self.strips``.

        Args:
            label: Single-character strip label from ``{a, b, c, d, e}``.

        Raises:
            KeyError: If *label* is not in ``STRIP_TEMPLATES``.
        """
        if label not in STRIP_TEMPLATES:
            raise KeyError(f"'{label}' not a valid strip label")

        polys_spec = STRIP_TEMPLATES[label]["polys"]
        pairings_spec = STRIP_TEMPLATES[label]["pairings"]

        polys: list[CuspCell] = []
        for tp in polys_spec:
            if tp == TRI:
                self.tri_idx += 1
                polys.append(Tri(self.tri_idx))
            elif tp == SQR:
                self.sqr_idx += 1
                polys.append(Sqr(self.sqr_idx))

        for pr in pairings_spec:
            self.cusp.pair(
                polys[pr[0]],
                pr[1],
                polys[pr[2]],
                pr[3],
            )

        self.strips.append(polys)

    def get_num_polys(self) -> tuple[int, int]:
        """Return the total number of triangles and squares created so far.

        Returns:
            ``(num_triangles, num_squares)`` tuple.
        """
        return (self.tri_idx + 1, self.sqr_idx + 1)
