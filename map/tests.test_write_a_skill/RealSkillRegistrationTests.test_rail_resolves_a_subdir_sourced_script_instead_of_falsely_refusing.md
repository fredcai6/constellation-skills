# tests.test_write_a_skill:RealSkillRegistrationTests.test_rail_resolves_a_subdir_sourced_script_instead_of_falsely_refusing
method, tests/test_write_a_skill.py:141, 31 lines

```python
def test_rail_resolves_a_subdir_sourced_script_instead_of_falsely_refusing(self)
```

Regression (#262): the rail checked bundle members with a hand-rolled

`REPO_ROOT/"scripts"/script`, blind to SCRIPT_SOURCE_SUBDIRS. The moment
the Context Governor hook pair was bundled -- its source lives in
`scripts/hooks/`, not flat in `scripts/` -- the rail emitted a FALSE
refusal for the skill that carries it:

    REFUSED: skill 'workbench' registers script 'gauge_writer_hook.py'
             that does not exist under scripts/

The script was right there. Source resolution has exactly ONE owner,
`install_constellation.script_source_path`, and every consumer must go
through it or they drift apart again.

Driven against a TOY skill so the assertion isolates the resolver: the
live corpus carries unrelated pre-existing curate gating flags (missing
`invoker:` tags on ~12 skills, workbench included) that would mask what
this test is measuring. `subdir_scripts` is derived from the live
SCRIPT_SOURCE_SUBDIRS map, so the NEXT subdirectory-sourced script is
covered automatically.

calls internal: RealSkillRegistrationTests.assertTrue, _write_toy
calls stdlib: builtins.sorted, builtins.tuple, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RealSkillRegistrationTests.installer, RealSkillRegistrationTests.rail
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
