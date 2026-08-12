# Tiny pytest-collectable fixture for tests/test_validate_spine.py's fault-2
# (zero-collect selector) cases. Named `fixture_tests.py`, not `test_*.py` /
# `*_test.py`, so pytest's default discovery never picks this up on its own --
# it is only ever collected when a test in test_validate_spine.py points
# `--collect-only` at it explicitly.


def test_alpha():
    assert True


def test_beta():
    assert True
