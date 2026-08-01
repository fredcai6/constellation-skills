"""
Tests for Project Euler Problem #1 solution.
"""
import pytest
from solution import compute_sum_multiples_3_or_5


def test_sum_multiples_below_10():
    """Test with example: multiples of 3 or 5 below 10 are 3,5,6,9 -> sum=23"""
    assert compute_sum_multiples_3_or_5(10) == 23


def test_sum_multiples_below_1000():
    """Test the actual problem: sum of multiples of 3 or 5 below 1000"""
    assert compute_sum_multiples_3_or_5(1000) == 233168


def test_sum_multiples_below_1():
    """Test edge case: no multiples below 1"""
    assert compute_sum_multiples_3_or_5(1) == 0


def test_sum_multiples_below_3():
    """Test edge case: no multiples below 3"""
    assert compute_sum_multiples_3_or_5(3) == 0
