# tests.test_run_skill_eval:test_corpus_id_install_path_invariant
function, tests/test_run_skill_eval.py:601, 32 lines

```python
def test_corpus_id_install_path_invariant(tmp_path)
```

#153: two byte-identical corpora installed at DIFFERENT absolute temp roots must

hash to the SAME corpus_id. Driven through the REAL copy path — `run_scenario` ->
`_run_once` copies the installed tree into `workspace/.claude/skills` and asserts it
against the recorded id — so a naive "strip the dir I am hashing" fix (which no-ops
on the copy) would false-fence and be caught here, not pass. The RAW `compute_corpus_id`
of the two installed trees DIFFERS (the installer baked the absolute install path in);
that canary proves the equality below is the fix normalizing real pollution out, not
two trivially-identical trees.

calls internal: _tokened_worktree, make_scenario
calls stdlib: builtins.all x2, builtins.str x2
reads internal: rse x5, fake_pass_launch x2, PASS_CHECK
unresolved: 6 calls (dispatch-unknown-base), 9 reads (dispatch-unknown-base)

referenced by: none found
