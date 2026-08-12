# Prepared fixes (drafts — not yet applied)

## New evidence: the release-window rule is DELIBERATE, not an oversight
`tests/test_spine_provenance_check.py::test_journal_ts_outside_lease_fails` pins it:
it pushes the terminal task's advance to t0+30min (release is t0+13m3s) and asserts
FAIL with "release" in the reason. In that fixture the terminal task is `execute`.
So "no journal entry after release" is an intended contract (release must be the LAST
journaled action). => "the check is buggy" is too strong; it's a tension between the
archive imperative ("Finally, release the lease") and the check's release-last contract.

## Fix A (WORDING — my ownership, respects the invariant) — RECOMMENDED
File: skills/commander-delegated/SKILL.md, step 4 (append a release-ordering clause).
Draft clause:
> "At the archive step the lease release is your FINAL engine action: satisfy/waive the
>  archive postconditions, run the engine's final `advance` on archive so the spine
>  reports done, and ONLY THEN `release` the lease. Releasing before that final advance
>  leaves archive's own closeout entries (attest/waive/advance) after the lease release
>  and fails the terminal provenance check."
- Pros: within my ownership; respects the deliberate invariant; on-mission (wording).
- Cons: needs a round-3 re-measurement (cannot regrade existing A/B — their journals
  already encode release-before-final-advance). Robustness = whether sonnet threads it.
- Note: the ordering error originates in the FENCED spine-template archive imperative
  ("Finally, release..."). If round-3 shows SKILL.md wording is insufficient because the
  template imperative dominates at the archive step, that is evidence the fix belongs in
  the fenced template -> float. Clean experimental logic.

## Fix B (INSTRUMENT — fenced; overrides the pinned invariant) — alternative
File: evals/*/checks/spine_completed.py (x3 identical copies) journal_consistent().
Change: permit post-release journal entries only for the TERMINAL task's closeout.
Blocker: the pinned test's terminal task is `execute`, so "terminal task" scoping would
make that test's post-release execute-advance PASS => breaks/rewrites the pinned test.
Any non-test-breaking scoping needs a magic time-window and is hacky. Enables the
regrade-without-re-runs path, but is a deliberate-invariant change = human/Admiral call.

## Regrade math (unchanged): relax release-window => A PASS, B PASS, C FAIL = 2/3 terminal.

## Validation harness (ready): run chosen check against A/B/C + refs; run pytest
tests/test_spine_provenance_check.py; for Fix A, launch round-3 (3 runs) with the wording.
