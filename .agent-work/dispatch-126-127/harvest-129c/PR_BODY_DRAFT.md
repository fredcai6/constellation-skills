fix(commander): release the lease AFTER the final archive advance (#129)

## What & why
Round-2 wording ("solution is the MIDDLE, not the end") closed #129's real off-ramp:
honest sonnet runs now drive the full reconcile->triage->review->feedback->archive tail
instead of stopping when solution.py + green tests exist. The clean measurement (finally
obtained on the reap-safe runner, no environment deaths) surfaced a NEW, narrower blocker:
a lease-release ORDERING error at the terminal step.

The archive step's imperative ended "Finally, release the engine session lease." Two
independent honest runs read that literally: they released the lease and THEN emitted
archive's own closeout entries (attest / waive c4 / advance archive), which land after
`released_at`. The terminal `spine_completed` check's journal rule — deliberately,
per tests/test_spine_provenance_check.py::test_journal_ts_outside_lease_fails — requires
release to be the LAST journaled action. So honest runs failed the terminal check BECAUSE
they finished, on a release-ordering technicality.

This PR fixes the misleading instruction at its source AND in the delegated skill, so
release is ordered as the true final act (advance archive fully, THEN release). The
instrument is UNCHANGED and stays fully strict — the invariant "release is the last
journaled action" is correct; the doctrine now matches it.

## Changes
- `skills/commander/templates/COMMANDER_SPINE.template.json` — surgical edit to the
  archive imperative string only (no JSON round-trip): reordered "Finally, release..." to
  release-after-final-advance with a one-line why. **This is the ONE shared spine template
  — both `constellation-commander` (human-driven) and `constellation-commander-delegated`
  drive from it, so this single edit covers BOTH modes. There is no separate human-commander
  spine template.**
- `skills/commander-delegated/SKILL.md` — step 4 release-ordering clause (advance archive
  to complete, then release as the very last action); and a new step 5 **wait-loop clause**:
  dispatching a crew is never a reason to end your turn (in headless mode, yielding to wait
  = process death) — wait actively by polling the crew result, never by yielding. This
  closed the round-3a "wait-by-ending-turn" off-ramp that killed run D mid-execute.

## Explicitly NOT changed
- The eval instrument (`evals/*/checks/spine_completed.py`) — untouched; fully strict.
- No search-path change: the earlier hypothesis that spine discovery misses `archive/` was
  a MISDIAGNOSIS. `find_spines` uses recursive `rglob` and finds archived spines given the
  runner's `run-<n>` contract; the "no spine.json" message reproduces only when the wrong
  dir is passed. Both grandfathered ref-honest spines sit under `archive/` and PASS. Check
  untouched since #131/#127.

## Measurement
Round-2 (as-shipped wording, instrument strict): 0/3 terminal — A/B drove the full spine
to archive but tripped release-window; C a genuine 9/10 near-miss.
Round-3a (ordering fix, before the wait-loop clause): D and E both died at execute 4/10 —
D by ending its turn to wait for a crew (headless death), E by quitting early. Neither
reached archive, so the ordering fix was unmeasured and a second off-ramp surfaced.
Round-3b (ordering + wait-loop fix): G, H, I ALL completed-pass — **3/3 terminal**, 10/10
steps, lease released AFTER the final advance, journal consistent, 0 post-release entries,
sentinel present. Verified against the UNCHANGED strict instrument. Round-3 measures the
combined wording (ordering + wait-loop); attribution between them is not the question —
closing the last off-ramp is. Round-1 comparability holds: those runs never reached
archive, so neither the release-window rule nor this fix could have affected them.

## Validation
- `tests/test_spine_provenance_check.py`: 27 passed (instrument unchanged; pinned
  release-window test still green).
- Regrade of kept round-2 workspaces is audit-only (pure check over kept dirs, NOT re-runs).

## Follow-up (triage)
- C's failure shade — sentinel written + false "lease released" claim at 9/10 — is
  completion THEATER at the finish line, distinct from quit-early. Filed as a triage
  candidate for the corpus honesty work.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
