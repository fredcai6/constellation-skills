# Triage candidate: test_crew_launcher.py scratch-dir test leaks CREW_SCRATCH_DIR from caller env

**Found during:** 567-d2 g3-suite-green, full-suite verification.

**What:** `tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts `CREW_SCRATCH_DIR` is absent from a launched subprocess's env, but its
`fake_launch` capture does not scrub the CALLING process's own environment first.
Any process that is itself a dispatched crew (and therefore already has
`CREW_SCRATCH_DIR` set, as every crew under `run_crew.py`'s scratch-dir mechanism
does) fails this specific test, even against a fully green tree.

**Evidence:** Failed inside this session (a dispatched Commander crew, `CREW_SCRATCH_DIR`
set in its own env). Passed in the same clean detached worktree at the same commit
with `env -u CREW_SCRATCH_DIR py -m pytest tests/test_crew_launcher.py::...`.

**Why this lane didn't fix it:** `tests/test_crew_launcher.py` is not under
`skills/workbench/**` or `docs/agents/CREW_CONTEXT.md` (this lane's file
ownership this wave). The fix likely belongs beside `run_crew.py`'s own test
suite, e.g. scrubbing `CREW_SCRATCH_DIR` (and probably `SPINE_FILE`/`SPINE_SESSION`/
`SPINE_PARENT`, which the crew-dispatch doctrine already tells callers to unset)
from `fake_launch`'s captured/asserted environment, or from `os.environ` at test
setup.

**Suggested disposition:** recommend-and-defer — a small, well-scoped test-isolation
fix, owner TBD (whichever lane/issue owns `scripts/run_crew.py` and its tests).
