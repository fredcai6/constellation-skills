def compute_sum():
    """
    Compute the sum of all multiples of 3 or 5 below 1000.

    Returns:
        int: The sum of all multiples of 3 or 5 below 1000
    """
    total = 0
    for i in range(1, 1000):
        if i % 3 == 0 or i % 5 == 0:
            total += i
    return total


if __name__ == "__main__":
    result = compute_sum()
    print(result)
