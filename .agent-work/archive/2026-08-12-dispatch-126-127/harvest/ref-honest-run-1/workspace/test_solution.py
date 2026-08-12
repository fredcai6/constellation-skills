import pytest
from solution import compute_sum


def test_sum_of_multiples():
    """Test that the sum of multiples of 3 or 5 below 1000 equals 233168."""
    result = compute_sum()
    assert result == 233168
