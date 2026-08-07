# src.utils.simplification_limits:SimplificationLimitsResult
class, src/utils/simplification_limits.py:48, 11 lines

```python
@dataclass
class SimplificationLimitsResult
```

HOLE: no docstring

```python
passed: bool
violations: List[Violation]
files_checked: int
```

- [to_dict](SimplificationLimitsResult.to_dict.md) method: HOLE: no docstring

reads internal: Violation
reads stdlib: builtins.bool, builtins.dict, builtins.int, typing.List
writes internal: SimplificationLimitsResult.files_checked, SimplificationLimitsResult.passed, SimplificationLimitsResult.violations

referenced by: 3 sites, this module only
