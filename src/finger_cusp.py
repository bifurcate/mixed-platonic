"""Cusp cellulation constructors for the short-meridian (finger) case.

In the short-meridian family, each cusp tiling is built from repeating
"finger" units arranged cyclically.  A single finger consists of one
square and two triangles, glued internally along three edges::

    Sqr(i) -- Tri(2i) -- Tri(2i+1) -- (back to Sqr(i))

Adjacent fingers are connected by two edge pairings whose topology depends
on whether consecutive entries in the orientation string have the same or
opposite value.

Terminology note
----------------
The thesis (§5.2) defines three levels of binary string (see
``pattern_restriction`` for the full hierarchy):

- **Orientation string** ``s``: each entry is the orientation (0 or 1) of
  a finger.  This is what the code calls the "finger pattern" and what
  ``FingerCuspConstructor`` consumes to build the cusp tiling.
- **Finger pattern** ``f`` (thesis Definition 5.5):
  ``f = differentiate(s)``, encoding stay (0) / switch (1) at each
  finger boundary.
- **Boundary derivative** ``r`` (thesis Definition 5.10):
  ``r = differentiate(f)``.  Its Hamming weight is the oct-signature.

In code, "finger pattern" refers to the orientation string ``s``.  In the
thesis, "finger pattern" refers to the boundary-type string ``f``.

Finger pattern representations
------------------------------
All representations encode the same combinatorial data — a cyclic sequence
of two distinct symbols — and are used in different contexts:

- **{0, 1} integer list** (``FingerPattern``): the canonical internal
  representation, used for cusp construction, bracelet enumeration, and
  discrete calculus.  ``1`` = plus / positive, ``0`` = minus / negative.
- **{'+', '-'} string**: user-facing I/O format, directory names, and
  display.  Interchangeable with the integer list via ``to_finger_pattern_str``
  and ``to_finger_pattern_list``.
- **{'0', '1'} string**: alternative user input format, accepted by
  ``parse_finger_pattern``.

The ``FingerCuspConstructor`` builds a single connected cusp component from
one pattern, while ``MultiFingerCuspConstructor`` handles the multi-cusp
case by concatenating several patterns with an index offset.
"""

from collections.abc import Iterator

from base import (
    CuspCell,
    Sqr,
    Tri,
)

from construction import Cusp
from cusp_geometry import CuspGeometry
from cyclotomic import CyclotomicInt

FingerPattern = list[int]
"""A cyclic sequence of 0/1 values encoding finger orientations (1=plus, 0=minus)."""


def to_finger_pattern_str(finger_pattern: FingerPattern | tuple[int, ...]) -> str:
    """Encode a finger pattern as a compact string of ``+`` and ``-`` chars.

    Args:
        finger_pattern: Sequence of 0/1 values.

    Returns:
        A string like ``"++--+"`` of the same length.
    """
    s = ""
    for x in finger_pattern:
        if x == 0:
            s += "-"
        else:
            s += "+"
    return s


def to_finger_pattern_list(finger_pattern_str: str) -> FingerPattern:
    """Decode a ``+``/``-`` string back into a finger pattern list.

    Args:
        finger_pattern_str: A string of ``+`` and ``-`` characters.

    Returns:
        List of 0/1 integers (``'-'`` → 0, ``'+'`` → 1).
    """
    L: FingerPattern = []
    for x in finger_pattern_str:
        if x == "-":
            L.append(0)
        else:
            L.append(1)
    return L


def to_multi_finger_pattern_str(
    multi_finger_pattern: list[FingerPattern] | tuple[tuple[int, ...], ...],
) -> str:
    """Encode a multi-cusp finger pattern as a pipe-delimited string.

    Each component's pattern is separated by ``|`` delimiters, e.g.
    ``"|++--|-+|"`` for two components with patterns [1,1,0,0]
    and [0,1].

    Args:
        multi_finger_pattern: Sequence of finger patterns, one per cusp
            component.

    Returns:
        Pipe-delimited string representation.
    """
    s = ""
    for fp in multi_finger_pattern:
        s += "|"
        for x in fp:
            if x == 0:
                s += "-"
            else:
                s += "+"
    s += "|"
    return s


def parse_finger_pattern(s: str) -> FingerPattern:
    """Parse a finger pattern string in either ``{+,-}`` or ``{0,1}`` format.

    Accepts two input conventions:
    - Sign format: a string of ``'+'`` and ``'-'`` characters
    - Binary format: a string of ``'0'`` and ``'1'`` characters

    In both cases the returned list uses the canonical 0/1 representation
    (``'+'`` / ``'1'`` → 1, ``'-'`` / ``'0'`` → 0).

    Args:
        s: A finger pattern string in either format.

    Returns:
        List of 0/1 integers.

    Raises:
        ValueError: If the string contains characters outside the
            expected alphabet or mixes the two formats.
    """
    if all(c in "+-" for c in s):
        return to_finger_pattern_list(s)
    if all(c in "01" for c in s):
        return [int(c) for c in s]
    raise ValueError(
        f"Finger pattern must consist of '+'/'-' or '0'/'1' characters, got: {s!r}"
    )


class FingerCuspConstructor:
    """Build a single connected cusp tiling from a cyclic finger pattern.

    Each finger at index *i* creates three cusp cells — ``Sqr(i)``,
    ``Tri(2i)``, ``Tri(2i+1)`` — with internal edge pairings that form a
    strip.  Adjacent fingers are then connected with two more edge pairings
    whose topology depends on whether the neighbouring pattern entries share
    the same value ("positive" connection) or differ ("negative" connection).
    The last finger wraps around to connect with the first.

    Attributes:
        cusp: The cusp tiling being populated.
        finger_pattern: Cyclic list of 0/1 orientation values.
    """

    def __init__(self, cusp: Cusp, finger_pattern: FingerPattern) -> None:
        self.cusp = cusp
        self.finger_pattern = finger_pattern
        self.current_idx: int = 0

    def add_finger(self, idx: int) -> None:
        """Create the three cusp cells for finger *idx* and pair them internally.

        Builds the internal strip ``Sqr(idx) -- Tri(2*idx) -- Tri(2*idx+1)``
        with three edge pairings forming a closed band around the finger.

        Args:
            idx: Zero-based finger index.
        """
        sqr0 = Sqr(idx)
        tri0 = Tri(2 * idx)
        tri1 = Tri(2 * idx + 1)

        # Sqr right edge <-> Tri0 left edge
        self.cusp.pair(
            sqr0,
            (2, 3),
            tri0,
            (1, 3),
        )

        # Tri0 bottom edge <-> Tri1 top edge
        self.cusp.pair(
            tri0,
            (2, 3),
            tri1,
            (2, 1),
        )

        # Tri1 bottom edge <-> Sqr left edge (wraps the strip)
        self.cusp.pair(
            tri1,
            (2, 3),
            sqr0,
            (1, 4),
        )

    def connect_fingers_pos(self, idx_src: int, idx_tgt: int) -> None:
        """Connect two same-sign fingers with square-to-square and tri-to-tri pairings.

        Used when ``finger_pattern[idx_src]`` and ``finger_pattern[idx_tgt]``
        have the same sign.  The right side of finger *idx_src* is paired
        directly to the left side of finger *idx_tgt*: square-to-square on
        the top edge and triangle-to-triangle on the bottom edge.

        Args:
            idx_src: Index of the source (left) finger.
            idx_tgt: Index of the target (right) finger.
        """
        self.cusp.pair(
            Sqr(idx_src),
            (3, 4),
            Sqr(idx_tgt),
            (2, 1),
        )

        self.cusp.pair(Tri(2 * idx_src + 1), (1, 3), Tri(2 * idx_tgt), (1, 2))

    def connect_fingers_neg(self, idx_src: int, idx_tgt: int) -> None:
        """Connect two opposite-sign fingers with crossed square-tri pairings.

        Used when ``finger_pattern[idx_src]`` and ``finger_pattern[idx_tgt]``
        differ in sign.  The connection crosses cell types: the source square
        pairs with the target triangle, and vice versa.

        Args:
            idx_src: Index of the source (left) finger.
            idx_tgt: Index of the target (right) finger.
        """
        self.cusp.pair(
            Sqr(idx_src),
            (3, 4),
            Tri(2 * idx_tgt),
            (1, 2),
        )

        self.cusp.pair(
            Tri(2 * idx_src + 1),
            (1, 3),
            Sqr(idx_tgt),
            (2, 1),
        )

    def generate(self) -> Cusp:
        """Build the complete cusp tiling by adding and connecting all fingers.

        First creates all finger strips, then connects consecutive pairs
        (including the wrap-around from last to first) using positive or
        negative connections according to the pattern.

        Returns:
            The populated ``Cusp`` object with all cells and edge pairings.
        """
        n = len(self.finger_pattern)
        for i in range(n):
            self.add_finger(i)

        # Connect consecutive fingers
        for i in range(n - 1):
            if self.finger_pattern[i] == self.finger_pattern[i + 1]:
                self.connect_fingers_pos(i, i + 1)
            else:
                self.connect_fingers_neg(i, i + 1)

        # Wrap-around: connect last finger back to first
        if self.finger_pattern[n - 1] == self.finger_pattern[0]:
            self.connect_fingers_pos(n - 1, 0)
        else:
            self.connect_fingers_neg(n - 1, 0)

        return self.cusp

    def traversal(self) -> Iterator[CuspCell]:
        """Yield all cusp cells in finger order: Sqr, Tri, Tri per finger.

        Yields:
            Each cusp cell in the tiling, three per finger, in the order
            ``Sqr(i), Tri(2i), Tri(2i+1)`` for ``i = 0, 1, ..., n-1``.
        """
        for i in range(len(self.finger_pattern)):
            yield Sqr(i)
            yield Tri(2 * i)
            yield Tri(2 * i + 1)

    def cusp_geometry(self) -> CuspGeometry:
        """Build the complete cusp tiling by adding and connecting all fingers.

        First creates all finger strips, then connects consecutive pairs
        (including the wrap-around from last to first) using positive or
        negative connections according to the pattern.

        Returns:
            The populated ``Cusp`` object with all cells and edge pairings.
        """
        n = len(self.finger_pattern)
        geo = CuspGeometry()

        offset = CyclotomicInt(0, 0, 0, 0)

        for i in range(n):
            if self.finger_pattern[i] == 1:
                geo.set_cell(
                    Sqr(i),
                    {
                        1: offset + CyclotomicInt(0, 0, 0, 0),
                        2: offset + CyclotomicInt(0, 0, 0, 1),
                        3: offset + CyclotomicInt(1, 0, 0, 1),
                        4: offset + CyclotomicInt(1, 0, 0, 0),
                    },
                )
                geo.set_cell(
                    Tri(2 * i),
                    {
                        1: offset + CyclotomicInt(0, 0, 0, 1),
                        2: offset + CyclotomicInt(0, 0, 1, 1),
                        3: offset + CyclotomicInt(1, 0, 0, 1),
                    },
                )
                geo.set_cell(
                    Tri(2 * i + 1),
                    {
                        1: offset + CyclotomicInt(1, 0, 0, 1),
                        2: offset + CyclotomicInt(0, 0, 1, 1),
                        3: offset + CyclotomicInt(1, 0, 1, 1),
                    },
                )
                offset += CyclotomicInt(1, 0, 0, 0)
            else:
                geo.set_cell(
                    Sqr(i),
                    {
                        1: offset + CyclotomicInt(0, 0, 1, 1),
                        2: offset + CyclotomicInt(0, 0, 0, 1),
                        3: offset + CyclotomicInt(0, 1, 0, 0),
                        4: offset + CyclotomicInt(0, 1, 1, 0),
                    },
                )
                geo.set_cell(
                    Tri(2 * i),
                    {
                        1: offset + CyclotomicInt(0, 0, 0, 1),
                        2: offset + CyclotomicInt(0, 0, 0, 0),
                        3: offset + CyclotomicInt(0, 1, 0, 0),
                    },
                )
                geo.set_cell(
                    Tri(2 * i + 1),
                    {
                        1: offset + CyclotomicInt(0, 1, 0, 0),
                        2: offset + CyclotomicInt(0, 0, 0, 0),
                        3: offset + CyclotomicInt(0, 1, 0, -1),
                    },
                )
                offset += CyclotomicInt(0, 1, 0, -1)

        return geo


class MultiFingerCuspConstructor:
    """Build a (possibly disconnected) multi-cusp tiling from several finger patterns.

    Each finger pattern in the list produces one connected cusp component.
    Cell indices are offset so that components don't collide: if the first
    pattern has *k* fingers, the second component's cells start at index *k*.

    Attributes:
        cusp: The cusp tiling being populated (may contain multiple components).
        multi_finger_pattern: List of finger patterns (0/1), one per cusp component.
        flattened: All finger entries concatenated, used for index calculations.
    """

    def __init__(self, cusp: Cusp, multi_finger_pattern: list[FingerPattern]) -> None:
        self.cusp = cusp
        self.multi_finger_pattern = multi_finger_pattern
        self.flattened: FingerPattern = [
            item for fp in multi_finger_pattern for item in fp
        ]

    def add_finger(self, idx: int) -> None:
        """Create the three cusp cells for finger *idx* and pair them internally.

        Identical to ``FingerCuspConstructor.add_finger``; the *idx* value
        includes the component offset so cell indices are globally unique.

        Args:
            idx: Global (offset-adjusted) finger index.
        """
        sqr0 = Sqr(idx)
        tri0 = Tri(2 * idx)
        tri1 = Tri(2 * idx + 1)

        self.cusp.pair(
            sqr0,
            (2, 3),
            tri0,
            (1, 3),
        )

        self.cusp.pair(
            tri0,
            (2, 3),
            tri1,
            (2, 1),
        )

        self.cusp.pair(
            tri1,
            (2, 3),
            sqr0,
            (1, 4),
        )

    def connect_fingers_pos(self, idx_src: int, idx_tgt: int) -> None:
        """Connect two same-sign fingers (square-to-square, tri-to-tri).

        Args:
            idx_src: Global index of the source finger.
            idx_tgt: Global index of the target finger.
        """
        self.cusp.pair(
            Sqr(idx_src),
            (3, 4),
            Sqr(idx_tgt),
            (2, 1),
        )

        self.cusp.pair(Tri(2 * idx_src + 1), (1, 3), Tri(2 * idx_tgt), (1, 2))

    def connect_fingers_neg(self, idx_src: int, idx_tgt: int) -> None:
        """Connect two opposite-sign fingers (crossed square-tri).

        Args:
            idx_src: Global index of the source finger.
            idx_tgt: Global index of the target finger.
        """
        self.cusp.pair(
            Sqr(idx_src),
            (3, 4),
            Tri(2 * idx_tgt),
            (1, 2),
        )

        self.cusp.pair(
            Tri(2 * idx_src + 1),
            (1, 3),
            Sqr(idx_tgt),
            (2, 1),
        )

    def add_component(self, finger_pattern: FingerPattern, offset: int) -> None:
        """Build one connected cusp component at the given index offset.

        Creates all fingers, connects consecutive pairs (including the
        wrap-around), using positive or negative connections as determined
        by the pattern.

        Args:
            finger_pattern: The 0/1 pattern for this component.
            offset: Starting cell index for this component's fingers.
        """
        n = len(finger_pattern)

        for i in range(n):
            self.add_finger(offset + i)

        for i in range(n - 1):
            if finger_pattern[i] == finger_pattern[i + 1]:
                self.connect_fingers_pos(offset + i, offset + i + 1)
            else:
                self.connect_fingers_neg(offset + i, offset + i + 1)

        if finger_pattern[n - 1] == finger_pattern[0]:
            self.connect_fingers_pos(offset + n - 1, offset)
        else:
            self.connect_fingers_neg(offset + n - 1, offset)

    def generate(self) -> Cusp:
        """Build the complete multi-cusp tiling from all component patterns.

        Iterates through each finger pattern, advancing the offset by the
        pattern length so that cell indices don't overlap between components.

        Returns:
            The populated ``Cusp`` object with all components.
        """
        offset = 0
        for fp in self.multi_finger_pattern:
            self.add_component(fp, offset)
            offset += len(fp)

        return self.cusp

    def traversal(self) -> Iterator[CuspCell]:
        """Yield all cusp cells across all components in finger order.

        Yields:
            Each cusp cell in the tiling, three per finger, ordered by
            global finger index.
        """
        for i in range(len(self.flattened)):
            yield Sqr(i)
            yield Tri(2 * i)
            yield Tri(2 * i + 1)
