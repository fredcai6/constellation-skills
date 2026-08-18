# Full suite — lane K

**Commit sha:** `eb94b1509997fa441641110e51d633c2b7542ec3`
**Where:** a **clean detached worktree** of that commit, created with
`git worktree add --detach`, **not** the working copy. *A check that runs against your own working
copy is not a check on the world.*
**Env:** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`, per the launch
order's Inherited Context (a dispatched crew's `CREW_SCRATCH_DIR` otherwise leaks into an
`os.environ`-based assertion and reds a `test_crew_launcher.py` test this change never touches).
**Platform:** Linux. Windows CI is not the yardstick (#575 deferred, ~122-failure path-casing
baseline).

This was not run by hand and reported — it is the `g3-proof.c2` **engine postcondition**, so the
gate could not close unless the command exited 0. The engine ran it.

## Tally

```
3383 passed, 6 skipped, 2 deselected, 1222 subtests passed in 134.70s (0:02:14)
```

## The `^FAILED` grep

```
$ grep -c '^FAILED' /tmp/567k-suite.log
0
```

The root `conftest.py` restates each failed subtest as a line beginning `FAILED`, so this grep
covers subtest failures too, not just top-level ones.

## The 2 deselected, and why that is honest

`--deselect tests/test_code_map.py::MapTreeFreshnessTests`, permitted by
`decision:map-index-is-admiral-owned` (#544): "Your branch is accepted green **except**
`tests/test_code_map.py::MapTreeFreshnessTests`."

I checked that the deselection was actually necessary rather than assuming it, by running that
class alone at the same sha in a fresh detached worktree:

```
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 1 passed in 5.02s
```

So: **one** of the two genuinely fails, and it is precisely the Admiral-owned `map/INDEX.md`
freshness assertion. The deselection took the whole class, which also removed one test that
would have passed — stated here rather than glossed. It fails because `map/INDEX.md` is stale
against a fresh build and is fenced to the Admiral, so this lane does not regenerate it.

**Nothing else fails.**
