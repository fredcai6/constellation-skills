# Notes — issue #436, enumeration falsification (r418-436)

## Isolation proof (first command, before any git operation)

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/r418-436
worktree OK: in C:/Programs/constellation-skills-wt/r418-436
EXIT:0
```

## The gap, restated

`scripts/verify_worktree_precondition_coverage.py`'s `WORKTREE_ENTERING_GATES` has, since
#422/#329 shipped, held exactly ONE entry (`COMMANDER_SPINE.template.json`'s `init` gate). The
existing test (`EnumerationDeliberateBreakage` in `tests/test_worktree_precondition_wiring.py`)
proves the check refuses when THAT one entry is broken — but it never proved the enumeration
LOOP itself discriminates a genuinely NEW second entry it had never enumerated before (off-by-one,
stop-at-first-match, or similar loop defects would all pass that existing test unnoticed).

## Empirical probe (before writing any plan item)

Monkeypatched `WORKTREE_ENTERING_GATES` to two entries — the real, fixed Commander entry plus a
fabricated `skills/scoutbot/templates/SCOUTBOT_SPINE.template.json` / gate `init2` missing the
precondition — and called `verify_coverage()` in-process:

```
REFUSED as expected:
skills/scoutbot/templates/SCOUTBOT_SPINE.template.json: gate 'init2' does not wire an
unmet-by-default command precondition/postcondition whose command contains
'verify_worktree_isolation.py'
```

**Verdict up front: the check already correctly discriminates a genuinely new second entry.**
No production defect found in the loop/discrimination logic itself. Per
decision:a-passing-check-is-the-finding this negative (no defect) is itself reported, not
silently treated as "nothing to do" — see the permanent regression test below, which makes
this durable rather than a one-off probe result.

One real gap found and closed: the FAILURE path never stated the enumerated count (only the
success path did) — pre-ruling decision:count-is-part-of-the-output flagged this as in-scope
and cheap; fixed in `verify_coverage()`.

## m1 — TDD evidence

**RED** (`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_worktree_precondition_wiring.py -v`,
pre-fix):

```
tests\test_worktree_precondition_wiring.py ...F.                         [100%]
FAILED tests/test_worktree_precondition_wiring.py::EnumerationStatesCountOnFailure::test_failure_output_states_enumerated_count
AssertionError: '1 of 1 worktree-entering template' not found in "worktree-precondition coverage FAILED:\nskills/commander/templates/COMMANDER_SPINE.template.json: gate 'init' does not wire an unmet-by-default command precondition/postcondition whose command contains 'verify_worktree_isolation.py'\n"
1 failed, 4 passed in 1.11s
```

4/5 pass immediately — the two new discrimination tests (`EnumerationGeneralizesPastOneEntry`)
pass with NO code change, confirming the probe. 1/5 fails as designed (count-on-failure).

**GREEN** (post-fix, same file): `5 passed in 1.28s`, exit 0.

**Full suite green**: `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` →
`1724 passed, 4 skipped, 643 subtests passed in 648.07s (0:10:48)`, exit 0. (Baseline from
LO-436: `1721 passed, 4 skipped, 643 subtests` at main `ca0e36a` — delta is exactly the 3 new
tests, 0 failures, 0 regressions.)

## m2 — live deliberate-breakage demo (real repo, then reverted)

**The new template introduced**: `skills/scoutbot/templates/SCOUTBOT_SPINE.template.json` —
a throwaway, fixture-only "scoutbot" role, `init` gate, no `preconditions` at all. Never before
listed in `WORKTREE_ENTERING_GATES`. Added as a second tuple entry in the real
`scripts/verify_worktree_precondition_coverage.py`.

**Refusal — actual output, real exit code** (`python scripts/verify_worktree_precondition_coverage.py --root .`):

```
EXIT:1
--- STDERR ---
worktree-precondition coverage FAILED:
1 of 2 worktree-entering template(s) checked failed:
skills/scoutbot/templates/SCOUTBOT_SPINE.template.json: gate 'init' does not wire an unmet-by-default command precondition/postcondition whose command contains 'verify_worktree_isolation.py'
```

The refusal names the exact new template path, the exact gate id, and the exact missing
precondition marker (`verify_worktree_isolation.py`) — not a bare "FAIL", and not triggered by
a malformed fixture (the file parses fine; it is a legitimate template simply missing the wired
check). The known-good Commander entry is not named — precision, not a blanket failure. The
count line (`1 of 2`) is the m1 fix landing in the same run that exercises it.

**Revert**: removed the `scoutbot` tuple entry from `WORKTREE_ENTERING_GATES`, deleted
`skills/scoutbot/` entirely.

```
$ git status --short
 M scripts/verify_worktree_precondition_coverage.py   # only the m1 count-message fix remains
 M tests/test_worktree_precondition_wiring.py          # only the m1 new tests remain
?? .agent-work/epic-418-redux/implementer-436/
?? .agent-work/epic-418-redux/issue-436-enumeration-falsification/
```

`git diff scripts/verify_worktree_precondition_coverage.py` shows only the intentional
count-message change from m1 — the `scoutbot` tuple entry is gone, confirming a clean revert.

**Re-run after revert**:

```
$ python scripts/verify_worktree_precondition_coverage.py --root .
worktree-precondition coverage OK: 1 worktree-entering template(s) checked
EXIT:0
```

## The count

The enumeration script loops over `WORKTREE_ENTERING_GATES` — in the shipped state, **1**
worktree-entering template/gate pair (`COMMANDER_SPINE.template.json` / `init`). During the
live demo it looped over **2**, and the failure output now states both halves
(`1 of 2 ... checked failed`) — closing decision:count-is-part-of-the-output for the failure
path, matching what the success path already did.

## Triage candidates

- The enumeration list (`WORKTREE_ENTERING_GATES`) is still hand-maintained with exactly one
  real entry. If/when a second real worktree-entering role is ever dispatched (not a fixture),
  this is the first natural second entry and should reuse the pattern proven here rather than
  re-deriving it.

## Workflow feedback

- `checklist_engine.py advance` on a gate whose `check:command` postcondition runs the full
  ~11-minute test suite exceeds both the Bash tool's default 2-minute timeout AND its 10-minute
  max — had to background the `advance` invocation itself (`nohup ... &`, poll, then read the
  log) rather than the test command directly. Worth a note in the engine reference: a
  command-check postcondition that legitimately runs long needs the same background/poll
  pattern as any other long command, and `advance` itself is not exempt from that.
