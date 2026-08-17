# Triage candidate: a dispatched crew's own environment reds a test it never touched

**Status:** not filed. Held to closeout per the epic's standing ruling.

**Found by:** lane F (`cmdr-567-f`), self-reported in its return §6. **Reproduced independently by
the Admiral** before being recorded, because a lane's account of why a test failed is exactly the
kind of claim that should not be taken on trust.

**Proposed disposition:** **episode.** No open issue covers it, and the standing ruling mints
none.

## Reproduction

Same commit, same clean detached worktree, one variable different:

```
$ python3 -m pytest tests/test_crew_launcher.py::ScratchDirResumeTests::\
test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound -q
1 passed

$ env CREW_SCRATCH_DIR=/tmp/x/scratch python3 -m pytest <same node id> -q
1 failed
E   AssertionError: 'CREW_SCRATCH_DIR' unexpectedly found in {...}
```

`tests/test_crew_launcher.py:4061` asserts the key is **absent** from the env a resume
constructs. `fake_launch` builds that env on top of `os.environ`, so an ambient
`CREW_SCRATCH_DIR` is already present before the code under test does anything.

## Why it matters more than an ordinary flaky test

`scripts/run_crew.py`'s CLI backend **sets `CREW_SCRATCH_DIR` in every crew's environment**. So:

- Every crew that runs the full suite from inside its own dispatch sees this test fail.
- The failure has nothing to do with the crew's change.
- The dangerous outcome is not the red. It is a crew "fixing" `run_crew.py` to satisfy a test
  that was never measuring its change — a real regression introduced to silence a false one.

All five lanes of epic #567 wave 2 ran their merge gate this way. Lane F recognised it,
diagnosed it precisely (reproducing with only three of the four variables unset, then clearing
it with the fourth), worked around it by stripping the variables, and reported it. It did not
edit the test, correctly: `tests/` is shared and its launch order named only `scripts/run_crew.py`.

## The general shape

A test that asserts about a constructed environment, while building that environment from the
ambient one, cannot distinguish "the code under test added this" from "the world already had
it." It passes for every developer and fails only for the one population that matters here —
processes launched by the very launcher it tests.

## Recommended remedy

The assertion should be made against an env built from a controlled base, or the test should
clear the keys it asserts about before constructing. Either converts a false red for dispatched
crews into a real check for everyone.

**Not fixed here:** `tests/test_crew_launcher.py` is shared across lanes this wave, and no lane
owns it.
