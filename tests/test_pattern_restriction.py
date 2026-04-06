from binary_loop import differentiate
from pattern_restriction import generate_short_cusp


def test_generate_short_cusp_balanced_derivative():
    """Every n=12 pattern must have a balanced derivative (equal 0 and 1 counts)."""
    for fp in generate_short_cusp(12):
        deriv = differentiate(fp)
        assert deriv.count(0) == deriv.count(1), (
            f"Unbalanced derivative for {fp}: {deriv}"
        )
