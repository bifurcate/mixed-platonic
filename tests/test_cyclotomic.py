import pytest
import cmath

from cyclotomic import CyclotomicInt, ZETA, ZETA_INDEX


class TestCyclotomicIntArithmetic:
    def test_add(self):
        a = CyclotomicInt(1, 2, 3, 4)
        b = CyclotomicInt(5, 6, 7, 8)
        assert a + b == CyclotomicInt(6, 8, 10, 12)

    def test_add_int(self):
        a = CyclotomicInt(1, 2, 3, 4)
        assert a + 5 == CyclotomicInt(6, 2, 3, 4)
        assert 5 + a == CyclotomicInt(6, 2, 3, 4)

    def test_sub(self):
        a = CyclotomicInt(5, 6, 7, 8)
        b = CyclotomicInt(1, 2, 3, 4)
        assert a - b == CyclotomicInt(4, 4, 4, 4)

    def test_sub_int(self):
        a = CyclotomicInt(5, 1, 2, 3)
        assert a - 2 == CyclotomicInt(3, 1, 2, 3)
        assert 10 - a == CyclotomicInt(5, -1, -2, -3)

    def test_neg(self):
        a = CyclotomicInt(1, -2, 3, -4)
        assert -a == CyclotomicInt(-1, 2, -3, 4)

    def test_mul_int(self):
        a = CyclotomicInt(1, 2, 3, 4)
        assert a * 3 == CyclotomicInt(3, 6, 9, 12)
        assert 3 * a == CyclotomicInt(3, 6, 9, 12)

    def test_mul_zeta_squared(self):
        # ζ · ζ = ζ²
        z = CyclotomicInt(0, 1, 0, 0)
        assert z * z == CyclotomicInt(0, 0, 1, 0)

    def test_mul_i_squared(self):
        # i² = -1, where i = ζ³
        i = CyclotomicInt(0, 0, 0, 1)
        assert i * i == CyclotomicInt(-1, 0, 0, 0)

    def test_mul_zeta4(self):
        # ζ² · ζ² = ζ⁴ = ζ² - 1
        z2 = CyclotomicInt(0, 0, 1, 0)
        assert z2 * z2 == CyclotomicInt(-1, 0, 1, 0)

    def test_mul_zeta5(self):
        # ζ² · ζ³ = ζ⁵ = ζ³ - ζ
        z2 = CyclotomicInt(0, 0, 1, 0)
        z3 = CyclotomicInt(0, 0, 0, 1)
        assert z2 * z3 == CyclotomicInt(0, -1, 0, 1)

    def test_mul_general(self):
        # (1 + i) · ζ² = ζ² + ζ⁵ = ζ² + ζ³ - ζ
        one_plus_i = CyclotomicInt(1, 0, 0, 1)
        z2 = CyclotomicInt(0, 0, 1, 0)
        result = one_plus_i * z2
        assert result == CyclotomicInt(0, -1, 1, 1)

    def test_mul_zero(self):
        a = CyclotomicInt(1, 2, 3, 4)
        zero = CyclotomicInt(0, 0, 0, 0)
        assert a * zero == zero

    def test_mul_one(self):
        a = CyclotomicInt(3, -1, 4, -2)
        one = CyclotomicInt(1, 0, 0, 0)
        assert a * one == a


class TestCyclotomicIntComparison:
    def test_eq(self):
        assert CyclotomicInt(1, 2, 3, 4) == CyclotomicInt(1, 2, 3, 4)

    def test_neq(self):
        assert CyclotomicInt(1, 2, 3, 4) != CyclotomicInt(1, 2, 3, 5)

    def test_eq_int(self):
        assert CyclotomicInt(5, 0, 0, 0) == 5
        assert CyclotomicInt(0, 1, 0, 0) != 0

    def test_hash_consistent(self):
        a = CyclotomicInt(1, 2, 3, 4)
        b = CyclotomicInt(1, 2, 3, 4)
        assert hash(a) == hash(b)

    def test_usable_as_dict_key(self):
        d = {CyclotomicInt(0, 0, 1, 0): "zeta2"}
        assert d[CyclotomicInt(0, 0, 1, 0)] == "zeta2"


class TestZetaTable:
    def test_length(self):
        assert len(ZETA) == 12

    def test_zeta0_is_one(self):
        assert ZETA[0] == 1

    def test_zeta6_is_minus_one(self):
        assert ZETA[6] == -1

    def test_zeta3_is_i(self):
        assert ZETA[3] == CyclotomicInt(0, 0, 0, 1)

    def test_consecutive_products(self):
        """ζ^k · ζ = ζ^{k+1} for all k."""
        zeta1 = ZETA[1]
        for k in range(11):
            assert ZETA[k] * zeta1 == ZETA[k + 1], f"failed at k={k}"

    def test_zeta11_times_zeta_is_one(self):
        assert ZETA[11] * ZETA[1] == ZETA[0]

    def test_inverse_pairs(self):
        """ζ^k · ζ^{12-k} = 1 for all k."""
        for k in range(12):
            assert ZETA[k] * ZETA[(12 - k) % 12] == ZETA[0], f"failed at k={k}"


class TestZetaIndex:
    def test_all_roots_present(self):
        assert len(ZETA_INDEX) == 12

    def test_roundtrip(self):
        for k in range(12):
            assert ZETA_INDEX[ZETA[k].coeffs] == k


class TestToComplex:
    def test_one(self):
        assert CyclotomicInt(1, 0, 0, 0).to_complex() == pytest.approx(1.0)

    def test_i(self):
        z = CyclotomicInt(0, 0, 0, 1).to_complex()
        assert z == pytest.approx(1j)

    def test_zeta1(self):
        z = CyclotomicInt(0, 1, 0, 0).to_complex()
        expected = cmath.exp(1j * cmath.pi / 6)
        assert z.real == pytest.approx(expected.real)
        assert z.imag == pytest.approx(expected.imag)

    def test_zeta2(self):
        z = CyclotomicInt(0, 0, 1, 0).to_complex()
        expected = cmath.exp(1j * cmath.pi / 3)
        assert z.real == pytest.approx(expected.real)
        assert z.imag == pytest.approx(expected.imag)

    def test_all_roots_unit_magnitude(self):
        for k in range(12):
            z = ZETA[k].to_complex()
            assert abs(z) == pytest.approx(1.0), f"ζ^{k} has magnitude {abs(z)}"
