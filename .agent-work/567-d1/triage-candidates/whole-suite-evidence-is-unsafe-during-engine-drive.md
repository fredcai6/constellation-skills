# Triage candidate — the standard whole-suite evidence command is unsafe to run while driving the engine

**Found at:** `g1b-review`, lane D1, epic #567 wave 2. Reported by the g1b reviewer, which
reproduced it in both directions on itself.

**What was found.** `tests/test_gauge_chain_writer_to_trip.py:604` ends with
`assert _snapshot_repo_agent_work() == before` — a helper that snapshots the **size and mtime of
every file under the repo's `.agent-work/`** and asserts nothing moved during the test.

Every crew is told to run `pytest tests/ -q` as evidence, and every crew drives its own plan or
survey through the engine, which writes under `.agent-work/`. So a crew that records a check while
the suite is running sees a failure it did not cause, in a file it never touched.

**Measured, both ways, by the reviewer:**

| condition | result |
|---|---|
| whole suite run while recording survey checks | **7 failed**, 3361 passed |
| whole suite run quiet | **6 failed**, 3362 passed |

The 7th failure was the reviewer's own side effect. It caught this only by going to the failing
assertion instead of to the implementer's claim — and it says plainly that had it reported "7, not
6" as a finding, it would have blocked a gate on its own write.

**Why it matters beyond one crew.** This is not a flake; it is deterministic and it fires on
precisely the recipe the role skills prescribe. It will bite every future crew that runs the
standard evidence command, and the natural misreading — "the implementer's tally was wrong" — points
the investigation at innocent work.

**Candidate fixes:**
1. Fence the snapshot to the fixture's own subtree rather than the whole repo `.agent-work/`.
2. Failing that, state the quiescence requirement wherever crews are told to run the suite, so the
   requirement is visible before the failure rather than after it.

**Why it is a candidate and not a fix.** The test is in no lane's sole-writer list this wave, and
narrowing a containment assertion is a judgement about what that test is *for* — it may be
deliberately repo-wide. Not a drive-by from the lane that tripped it.

**Mitigation used this run:** every crew handoff after this discovery tells the crew not to run the
whole suite while driving its own plan, and this lane's own merge-gate suite run at `g5-final` is
executed in a **clean detached worktree** with no engine activity, which is the launch order's
requirement anyway.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.
