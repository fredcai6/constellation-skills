Verdict: APPROVE

# REVIEW_RESULT — g2 (issue #525), reviewer attempt-1

## Summary

The g2 diff (`scratch_dir`, `CREW_SCRATCH_DIR` wiring, dispatch-side collision
detection, resume-side get-not-reserve) matches the implementer's handoff and
its own IMPLEMENTER_RESULT claims. I re-derived every claim from the source
rather than trusting the pasted evidence, ran the suite independently
(206 passed), and ran a targeted mutation test that confirms `worktree` is
genuinely load-bearing in the key — stripping it from `scratch_dir`'s hash
computation breaks 4 tests, including the exact regression test named for
this scenario. No blockers found.

## Per-check findings

**1. `scratch_dir` keys on all 5 fields (work_id, gate, role, worktree,
attempt); worktree hashed as a RAW string, never resolved — CONFIRMED.**
Read `scratch_dir` at `scripts/run_crew.py:251-279` directly (not just its
docstring): `wtkey = hashlib.sha256(worktree.encode("utf-8")).hexdigest()[:12]`
operates on the `worktree` parameter exactly as passed in — no
`Path(...).resolve()` or any other normalization touches it anywhere in the
function body. The returned path embeds `gate`, `role`, `attempt`, and
`wtkey` in its stem, and `work_id` via `work_dir()`. All 5 fields are
present and load-bearing.

I traced `next_attempt`'s real source (`scripts/run_crew.py:425-435`) rather
than trusting the docstring's claim: it filters `entries` by
`work_id`/`gate`/`role`/`worktree` equality (all four, `worktree` included)
and returns `max(attempts) + 1` over that filtered set. This confirms the
premise the whole worktree-in-key requirement rests on: attempt numbers are
scoped PER (work_id, gate, role, worktree), so two different worktrees
dispatching the same work_id/gate/role can each independently land on
`attempt=1`. Omitting `worktree` from `scratch_dir`'s key would therefore
let those two collide — exactly the regression the handoff calls out.

I additionally ran my own mutation test: temporarily replaced
`wtkey = hashlib.sha256(worktree.encode("utf-8")).hexdigest()[:12]` with a
hardcoded constant (worktree stripped from the key), cleared `__pycache__`,
and reran the suite. Result: 4 tests failed, including
`ScratchDirPureFunctionTests::test_different_worktree_yields_disjoint_directory_at_the_same_attempt`
and `ScratchDirReservationTests::test_disjoint_reserved_directories_for_same_gate_role_attempt_different_worktree`
— the tests genuinely guard the regression, not just document it. Reverted
the mutation immediately after; the suite is back to 206 passed and
`git diff --stat scripts/run_crew.py` matches the pre-mutation diff exactly.

**2. `CliBackend.dispatch` reserves BEFORE any registry write — CONFIRMED.**
`scripts/run_crew.py:1516-1525`: `scratch.mkdir(parents=True, exist_ok=False)`
runs before `build_entry` (1528), `entries.append` (1537), and
`save_registry` (1538-1539). On `FileExistsError` it raises `CrewLaunchError`
naming the colliding path and the full 5-field tuple
(`work_id=...`, `gate=...`, `role=...`, `worktree=...`, `attempt=...`) and
references issue #525. Traced the actual exception path (not just the pasted
message): the `try/except FileExistsError` wraps only the `mkdir` call, and
the `raise CrewLaunchError(...)` inside the `except` block is the only path
that constructs that message — nothing downstream of it runs (`entries` is
never appended, `save_registry` is never called on the collision branch).
Verified experimentally too: `ScratchDirCollisionTests` forces a real
collision by pre-creating the directory, and asserts (a) the exact message
content, (b) zero calls reached `launch()`, (c) `entries == []` and the
registry file was never created, (d) pre-existing directory contents
untouched. All three tests in that class pass.

**3. `CliBackend.resume` does NOT re-reserve — CONFIRMED.** Read
`scripts/run_crew.py:1564-1637` end to end: the resume path computes
`scratch` via a plain call to `scratch_dir(...)` (line 1609) with no `.mkdir`
call anywhere in the function — grepped the function body for `mkdir` and
found none. The legacy-entry case (`entry.get("worktree")` is `None`) is
handled explicitly: `entry_worktree = entry.get("worktree")`, then
`scratch = scratch_dir(...) if entry_worktree is not None else None`, and
downstream `scratch_dir=(str(scratch) if scratch is not None else None)`
passed into `_crew_door_env` → `crew_env`, which only sets
`CREW_SCRATCH_DIR` when its `scratch_dir` param `is not None`. No crash path;
`ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
constructs exactly this entry (no `"worktree"` key at all) and asserts
`CREW_SCRATCH_DIR` is absent from the resumed child's env. Passes.

**4. `CREW_SCRATCH_DIR` only in the CLI-backend child's env — CONFIRMED.**
`ExternalBackend.dispatch` (`scripts/run_crew.py:1654-1700`) never calls
`crew_env`/`_crew_door_env` at all — it builds no environment whatsoever
(matches its own docstring: "spawns nothing... builds no environment"), and
its `build_entry(...)` call passes no `scratch=` kwarg, so the registry entry
also gets no `scratch_dir` key. This is a structural guarantee, not
incidental: there is no code path in `ExternalBackend` that could touch
`CREW_SCRATCH_DIR`. (Minor evidence gap, not a blocker: there is no test
asserting this negative directly for the external backend, mirroring the
pre-existing lack of such a test for `SPINE_FILE`'s absence there — noted
under workflow feedback below, not a BLOCK-worthy gap since the code
structurally cannot do otherwise.)

**5. `run_log_paths` untouched — CONFIRMED.** `git diff scripts/run_crew.py`
shows `run_log_paths` (`:244-248`) appears only as unchanged context in the
hunk header immediately preceding the new `scratch_dir` function — no `+`/`-`
lines touch its body. Confirmed by direct read of the current file: the
function is byte-for-byte the one-liner tuple-return it always was, keyed on
4 fields (no `worktree`), its own pre-existing, deliberately out-of-scope
asymmetry left exactly as found. Nobody "fixed" it as a drive-by.

**6. `git diff --stat` scope — CONFIRMED.** Only `scripts/run_crew.py` and
`tests/test_crew_launcher.py` changed (`git status --porcelain` shows no
other tracked-file modifications; the only untracked path is this run's own
`.agent-work/cleanup-e-crew-tooling/` work area, not part of the diff).

**7. Mechanical suite reproduces green — CONFIRMED, independently, in my own
hands.**
```
$ find . -name __pycache__ -exec rm -rf {} +
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q tests/test_crew_launcher.py
........................................................................ [ 34%]
........................................................................ [ 69%]
..............................................................           [100%]
206 passed in 0.80s
```
Matches the claimed 206 (188 g1 + 18 new). I also independently verified the
18-new-tests count by collecting only: `pytest --collect-only -q -k
ScratchDir` → exactly 18 items across `ScratchDirPureFunctionTests` (7),
`ScratchDirReservationTests` (5), `ScratchDirCollisionTests` (3),
`ScratchDirResumeTests` (3).

**8. Wiring grep — CONFIRMED (trivial count discrepancy, not a correctness
issue).** My own run of the handoff's exact grep command:
```
grep -rn "scratch_dir\|CREW_SCRATCH_DIR" --include=*.py . | grep -v "def scratch_dir" | grep -v "^\./tests/"
```
returned 18 lines (the IMPLEMENTER_RESULT claims 17) — all in
`scripts/run_crew.py`, none elsewhere. The count difference is off-by-one
and immaterial; the substantive claim ("zero references outside
`scripts/run_crew.py` and the test file") holds and I confirmed it with a
second, stricter grep excluding both `tests/` and `scripts/run_crew.py`
itself, which returned nothing.

## Blockers

None.

## Out-of-scope observations (not blockers)

- `run_log_paths`'s own worktree-omission asymmetry remains — confirmed
  correctly left alone per the handoff's explicit exclusion, not this
  gate's job.
- Making a dispatched crew's own skill actually WRITE into
  `CREW_SCRATCH_DIR` remains unimplemented, as explicitly excluded — this
  gate closes only the collision-avoidance half (reserve + expose + raise).
- g1's `_parent_lease_heartbeat` code (issue #607) sits unmodified in the
  same two files, exactly as instructed — not reviewed here.

## Workflow feedback

- The IMPLEMENTER_RESULT's wiring-grep count (17) was off by one against my
  own rerun of the identical command (18) — harmless here since the
  substantive "zero references outside scope" claim held either way, but a
  future implementer should paste the actual `grep` output rather than a
  hand-typed count, since a pasted count can silently drift from the command
  it claims to summarize.
- Consider adding one explicit test asserting `ExternalBackend.dispatch`
  never sets `CREW_SCRATCH_DIR` (symmetric to how `SPINE_FILE`'s absence
  there is currently unasserted too) — purely a coverage nicety, not a
  blocker, since the code is structurally incapable of doing otherwise
  (no environment is built on that path at all).
- The mutation-test technique (temporarily strip the `worktree` term from
  `scratch_dir`'s hash input, confirm named regression tests fail, revert)
  was a fast, high-confidence way to verify the single most load-bearing
  claim in this gate beyond just reading code; worth keeping as a standard
  reviewer move for "field X must stay in key Y" claims generally.
