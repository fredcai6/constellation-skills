# scripts.grade_lint:LintToolingError
class, scripts/grade_lint.py:697, 7 lines

```python
class LintToolingError(Exception)
```

A tooling/usage failure (unreadable file, invalid JSON) -- exit code 2.

Carries the exact operator-facing message so `main()` stays the single place
that writes to stderr and decides the exit code; `lint_one_file` never
prints. Distinct from a Violation, which is a finding ABOUT the plan rather
than a failure to read it.

referenced by: 3 sites, this module only
