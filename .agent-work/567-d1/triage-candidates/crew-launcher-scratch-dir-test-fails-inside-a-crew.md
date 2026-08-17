# Triage candidate — a test that fails only when the suite is run from inside a dispatched crew

**Found at:** `g1b`, lane D1, epic #567 wave 2. Reported by the g1b implementer; independently
predicted by the Admiral, whose addendum warned this lane it would bite the suite run.

**What was found.**
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts `CREW_SCRATCH_DIR` is **absent** from a child environment, but builds that environment from
the **ambient** one. `run_crew.py` sets `CREW_SCRATCH_DIR` in every crew process it launches, so the
test fails whenever the suite is run from inside a dispatched crew and passes whenever a human runs
it.

**Why it matters more than a flake.** Any crew asked to run the whole suite as evidence sees a red
that its dispatcher never sees, and the natural repair — "fix `run_crew.py` so the variable is not
set" — would be a real regression introduced to silence a false one. The Admiral's addendum says
exactly that, and this lane's crews were told not to. The leak is in the test's environment
construction, not in the launcher.

**Why it is a candidate and not a fix.** `scripts/run_crew.py` is **lane F's** file this wave. The
test itself is in no lane's sole-writer list, and changing it is a judgement about how the crew
launcher's tests should isolate their environment — a decision for whoever owns that suite, not a
drive-by from the lane that happened to trip it.

**Mitigation used this run:** every crew dispatch and every suite run is launched with
`env -u SPINE_FILE -u SPINE_SESSION -u CREW_SCRATCH_DIR`, which also stops a no-`--spine` crew
inheriting this lane's own spine.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.
