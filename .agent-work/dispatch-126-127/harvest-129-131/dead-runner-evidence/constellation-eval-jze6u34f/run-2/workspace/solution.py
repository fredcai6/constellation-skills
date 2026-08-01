"""
Project Euler Problem #1: Multiples of 3 or 5

Find the sum of all the multiples of 3 or 5 below 1000.
"""


def compute_sum_multiples_3_or_5(limit):
    """
    Compute the sum of all multiples of 3 or 5 below the given limit.

    Args:
        limit: Upper bound (exclusive) for finding multiples

    Returns:
        Sum of all multiples of 3 or 5 below limit
    """
    total = 0
    for n in range(limit):
        if n % 3 == 0 or n % 5 == 0:
            total += n
    return total


if __name__ == "__main__":
    result = compute_sum_multiples_3_or_5(1000)
    print(result)
