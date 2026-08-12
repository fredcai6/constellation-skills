#!/usr/bin/env python3
"""
Project Euler Problem #1:
Sum of all multiples of 3 or 5 below 1000.
"""


def compute_sum_of_multiples(limit=1000):
    """
    Compute the sum of all multiples of 3 or 5 below the given limit.

    Args:
        limit: Upper bound (exclusive)

    Returns:
        Sum of multiples of 3 or 5 below limit
    """
    total = 0
    for i in range(limit):
        if i % 3 == 0 or i % 5 == 0:
            total += i
    return total


if __name__ == "__main__":
    result = compute_sum_of_multiples(1000)
    print(result)
