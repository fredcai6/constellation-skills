# tests.test_feedback_tooling:CheckSkillFreshnessTests.setUp
method, tests/test_feedback_tooling.py:39, 12 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: load, load_installer
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: CheckSkillFreshnessTests.project x4, CheckSkillFreshnessTests.tmp
reads stdlib: tempfile (module)
writes internal: CheckSkillFreshnessTests.m, CheckSkillFreshnessTests.project, CheckSkillFreshnessTests.skills_root, CheckSkillFreshnessTests.tmp
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
