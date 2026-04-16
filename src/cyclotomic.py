"""Exact arithmetic in the ring of 12th-cyclotomic integers Z[ζ₁₂].

Elements are represented as 4-tuples (a, b, c, d) encoding

    a + b·ζ₁₂ + c·ζ₁₂² + d·ζ₁₂³

where ζ₁₂ = e^{2πi/12} = e^{iπ/6}.

The minimal polynomial is Φ₁₂(x) = x⁴ − x² + 1, giving reduction rules::

    ζ₁₂⁴ = ζ₁₂² − 1,   ζ₁₂⁵ = ζ₁₂³ − ζ₁₂,   ζ₁₂⁶ = −1

All cusp vertex positions in a mixed-Platonic tiling by unit-side regular
triangles and squares lie in this ring.
"""

import math

_SQRT3_2 = math.sqrt(3) / 2


class CyclotomicInt:
    """An element of Z[ζ₁₂], the ring of integers of Q(ζ₁₂).

    Supports exact addition, subtraction, multiplication, negation,
    and scalar multiplication by Python ints.

    Attributes:
        coeffs: The 4-tuple (a, b, c, d) of integer coefficients.
    """

    __slots__ = ("_c",)

    def __init__(self, a: int = 0, b: int = 0, c: int = 0, d: int = 0):
        self._c = (a, b, c, d)

    @property
    def coeffs(self) -> tuple[int, int, int, int]:
        return self._c

    # --- arithmetic ---

    def __add__(self, other):
        if isinstance(other, CyclotomicInt):
            return CyclotomicInt(
                self._c[0] + other._c[0],
                self._c[1] + other._c[1],
                self._c[2] + other._c[2],
                self._c[3] + other._c[3],
            )
        if isinstance(other, int):
            return CyclotomicInt(self._c[0] + other, self._c[1], self._c[2], self._c[3])
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, int):
            return CyclotomicInt(self._c[0] + other, self._c[1], self._c[2], self._c[3])
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, CyclotomicInt):
            return CyclotomicInt(
                self._c[0] - other._c[0],
                self._c[1] - other._c[1],
                self._c[2] - other._c[2],
                self._c[3] - other._c[3],
            )
        if isinstance(other, int):
            return CyclotomicInt(self._c[0] - other, self._c[1], self._c[2], self._c[3])
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, int):
            return CyclotomicInt(
                other - self._c[0], -self._c[1], -self._c[2], -self._c[3]
            )
        return NotImplemented

    def __neg__(self):
        return CyclotomicInt(-self._c[0], -self._c[1], -self._c[2], -self._c[3])

    def __mul__(self, other):
        if isinstance(other, int):
            return CyclotomicInt(
                self._c[0] * other,
                self._c[1] * other,
                self._c[2] * other,
                self._c[3] * other,
            )
        if isinstance(other, CyclotomicInt):
            a1, b1, c1, d1 = self._c
            a2, b2, c2, d2 = other._c
            # Expansion of (a1+b1ζ+c1ζ²+d1ζ³)(a2+b2ζ+c2ζ²+d2ζ³)
            # with reductions ζ⁴=ζ²−1, ζ⁵=ζ³−ζ, ζ⁶=−1.
            return CyclotomicInt(
                a1 * a2 - b1 * d2 - c1 * c2 - d1 * b2 - d1 * d2,
                a1 * b2 + b1 * a2 - c1 * d2 - d1 * c2,
                a1 * c2 + b1 * b2 + c1 * a2 + b1 * d2 + c1 * c2 + d1 * b2,
                a1 * d2 + b1 * c2 + c1 * b2 + d1 * a2 + c1 * d2 + d1 * c2,
            )
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, int):
            return CyclotomicInt(
                self._c[0] * other,
                self._c[1] * other,
                self._c[2] * other,
                self._c[3] * other,
            )
        return NotImplemented

    # --- comparison / hashing ---

    def __eq__(self, other):
        if isinstance(other, CyclotomicInt):
            return self._c == other._c
        if isinstance(other, int):
            return self._c == (other, 0, 0, 0)
        return NotImplemented

    def __hash__(self):
        return hash(self._c)

    def __repr__(self):
        return f"CyclotomicInt{self._c}"

    # --- conversion ---

    def to_complex(self) -> complex:
        """Convert to a floating-point complex number.

        Uses ζ₁₂ = e^{iπ/6}, so:
            real = a + b·√3/2 + c·1/2
            imag = b·1/2 + c·√3/2 + d
        """
        a, b, c, d = self._c
        return complex(a + b * _SQRT3_2 + c * 0.5, b * 0.5 + c * _SQRT3_2 + d)

    def is_zero(self) -> bool:
        return self._c == (0, 0, 0, 0)


# --- 12th roots of unity ---

ZETA: list[CyclotomicInt] = [
    CyclotomicInt(1, 0, 0, 0),  # ζ⁰  = 1
    CyclotomicInt(0, 1, 0, 0),  # ζ¹
    CyclotomicInt(0, 0, 1, 0),  # ζ²
    CyclotomicInt(0, 0, 0, 1),  # ζ³  = i
    CyclotomicInt(-1, 0, 1, 0),  # ζ⁴  = ζ² − 1
    CyclotomicInt(0, -1, 0, 1),  # ζ⁵  = ζ³ − ζ
    CyclotomicInt(-1, 0, 0, 0),  # ζ⁶  = −1
    CyclotomicInt(0, -1, 0, 0),  # ζ⁷  = −ζ
    CyclotomicInt(0, 0, -1, 0),  # ζ⁸  = −ζ²
    CyclotomicInt(0, 0, 0, -1),  # ζ⁹  = −i
    CyclotomicInt(1, 0, -1, 0),  # ζ¹⁰ = 1 − ζ²
    CyclotomicInt(0, 1, 0, -1),  # ζ¹¹ = ζ − ζ³
]
"""``ZETA[k]`` is ζ₁₂^k as a CyclotomicInt, for k = 0, …, 11."""

ZETA_INDEX: dict[tuple[int, int, int, int], int] = {z._c: k for k, z in enumerate(ZETA)}
"""Reverse lookup: coefficient tuple → power k such that the element equals ζ₁₂^k."""
