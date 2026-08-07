# tests.test_context_determinism:RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content
method, tests/test_context_determinism.py:528, 95 lines

```python
def test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content(self)
```

Regression, review BLOCKER-1 (#300 g5 rework 1).

Reproduces the reviewer's own construction: two FRESH worktrees at the
SAME commit, nothing overlaid. One stays genuinely clean; the other gets a
one-line edit to `docs/CHECKLIST_SCHEMA.md` -- a file NO declaration
names (the reviewer's own choice of undeclared file). The declaration
below names only `TRACKED` paths, so declared canon is byte-identical on
both sides; the only variable is dirt the declaration never sees.

FAILS before the split fix: `repo_rev` carried `dirty` inside content, so
`content()` differed between the two checkouts even though every declared
byte was identical. PASSES after: `dirty` left content, so identical canon
means identical content regardless of undeclared dirt.

Deliberately does NOT assert where -- or whether -- `dirty` survives in
the manifest, only that `content()` agrees. That is why this exact test
body produces both the red transcript (run against the pre-fix shape) and
the green one without being edited in between, and why it also survived
#327 (#305 g4) removing the field from the manifest entirely: it was never
asserting the field's home, only content's insensitivity to it.

No `unittest.SkipTest` environment guard here (unlike its siblings above
in this file) per this round's explicit "introduce no skipTest"
constraint: if git is somehow absent, `git worktree add` fails loudly
below via the ordinary assertion on its return code instead.

- [project](RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content.project.md) method: HOLE: no docstring

calls internal: RealCheckoutSkew.assertEqual x5, RealCheckoutSkew.assertNotEqual
calls stdlib: subprocess.run x5, builtins.str x2, pathlib.Path x2, builtins.list, builtins.open, shutil.rmtree, tempfile.mkdtemp
reads internal: ROOT x3, cm x3, RealCheckoutSkew.TRACKED
reads stdlib: subprocess (module) x5, shutil (module), tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
