import solution

def test_euler_problem_1():
    """Test that the solution correctly computes the sum of multiples of 3 or 5 below 1000."""
    result = solution.solve()
    assert result == 233168, f"Expected 233168, but got {result}"
