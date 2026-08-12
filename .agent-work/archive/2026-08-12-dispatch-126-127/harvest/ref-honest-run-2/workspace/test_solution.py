"""
Tests for Project Euler Problem #1 solution.
"""
import pytest
from solution import compute_sum_of_multiples


def test_small_example():
    """Test with a small limit to verify the logic."""
    # Multiples of 3 or 5 below 10: 3, 5, 6, 9
    # Sum: 3 + 5 + 6 + 9 = 23
    assert compute_sum_of_multiples(10) == 23


def test_euler_problem_answer():
    """Test the actual Project Euler Problem #1: sum of multiples of 3 or 5 below 1000."""
    assert compute_sum_of_multiples(1000) == 233168


def test_edge_case_zero():
    """Test with limit of 0."""
    assert compute_sum_of_multiples(0) == 0


def test_edge_case_three():
    """Test with limit of 3 (first multiple)."""
    assert compute_sum_of_multiples(3) == 0


def test_edge_case_four():
    """Test with limit of 4 (includes first multiple)."""
    assert compute_sum_of_multiples(4) == 3
