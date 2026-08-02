# Implementer Handoff — G1 REWORK (per-round fault isolation)

## Gate
`g1` (rework 1) — season runner per-round fault isolation. The original G1 (budget/refutil plumbing, runner, verify script, tests) is LANDED and correct; this is a BOUNDED addition, not a rebuild.

## Why (discovered at g2-run first launch)
The detached season run died on round 1. Root cause (verified by direct E runs): E builds each driver's car ceiling from strictly-prior sessions (`round_idx < R`). Round 1 (Bahrain) has NO prior sessions → E emits only ERROR rows → the round's `reference_laps` has NO `severity:*` classes → `derive_pilot_vocabulary([])` raises INSIDE `run_circuit` → the exception propagates out of `run_season`'s loop and kills all 22 rounds. Round 2 (Saudi) similarly errors ("load_weekend_inputs: array of sample points is empty"); round 3+ run clean. So early rounds legitimately have no strictly-prior data and MUST park — and one round's failure must never kill the season.

## Task (bounded)
In `scripts/run_season_670.py::run_season`, add PER-ROUND FAULT ISOLATION: wrap each round's `run_circuit_fn(...)` call (and its subsequent `check_round_vocabulary`) in a try/except. On ANY exception from a round, PARK that round — record `status="parked"`, a distinct `reason` that INCLUDES the exception type + message as the diagnosis (e.g. `f"round failed at run_circuit: {type(exc).__name__}: {exc}"`), and the `round_idx` — then CONTINUE to the next round. Keep the existing empty-grid park path (its reason already distinguishes "no driver grid"); this new path is for a round whose stages raised. The season must complete over all working rounds regardless of how many early/thin rounds park. Track parked-failure rounds in the same `parked_rounds` list (or a sibling list) so the results JSON reports every gap.

## Close Criteria
- A round whose `run_circuit_fn` raises is PARKED with a diagnostic reason (exception type+message) and the loop continues; the returned results dict still contains every other round's outcome and a non-crashing top-level summary.
- The empty-driver-grid park path is unchanged and still distinguishable from the new run-failure park.
- `parked_rounds` (and/or a clearly-named failure list) records the failed round(s); `season_results.json` remains well-formed with covered + parked rounds both present.
- New test in `tests/unit/physics/pilot/test_season_runner.py`: a `run_circuit_fn` that RAISES for one round (e.g. round 1) and succeeds for others → that round is parked with the exception message in its reason, the other rounds are covered, and `run_season` does NOT propagate the exception. (Use the existing synthetic-runner test style; do NOT invoke real E.)
- All existing pilot tests still pass; pyright-0 on the touched file.

## Allowed Scope
`scripts/run_season_670.py` (the `run_season` loop only), `tests/unit/physics/pilot/test_season_runner.py` (add the isolation test). Do NOT touch `src/physics/pilot/pipeline.py`, frozen sets, stage/gating logic, the panel, join, or fingerprint fit.

## Specific Exclusions
- Do NOT try to "fix" round 1/2 to produce data (they genuinely lack strictly-prior data — parking is the correct, honest behavior; no-frame-kill).
- Do NOT change run_circuit or E. Do NOT run the real compute. Do NOT touch docs/architecture/*.

## Constraints
- OFFLINE; never write a tracked `data/f1_data_*.db`; frozen consumed not minted; pinned 3.14 interpreter (`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`); worktree-first sys.path guard.

## Map Anchors (inbound)
- **Structural:** `scripts/run_season_670.py::run_season` loop (lines ~191-227 — the `for circuit, round_idx in slate` body).
- **Constraints:** offline-only; a per-round failure PARKS, never crashes the season (robustness for an unattended overnight run).
- **Evidence expectations:** a raising round is parked-with-diagnosis; season completes over working rounds.

## Deliverable Path Check
- **Committed** — `scripts/run_season_670.py`, `tests/unit/physics/pilot/test_season_runner.py` (both tracked; verified check-ignore exit 1 earlier).

## Required Evidence
- LOAD-BEARING: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot/test_season_runner.py -q` passes (paste line); `... -m pytest tests/unit/physics/pilot -q` passes.
- CONFIRMATORY: pyright clean on the touched file.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot/test_season_runner.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot -q
```

## Suggested Model Tier
`simple bounded` — a focused try/except + one test; the design is fully specified above.

## Authority
The park-per-round design is decided (this handoff). You must not: change run_circuit/E, edit a frozen set, or run real compute.

## Stop Conditions
Stop and return if isolating per-round failures requires changing run_circuit or E (it should not — catch at the run_season loop level).

## Return Format
Write IMPLEMENTER_RESULT to `.agent-work/670-season-run/crew-results/g1-implementer-rework-result.md` (slice, files changed, evidence with pasted pass lines, assumptions, workflow feedback). Then SendMessage cmdr-670 a thin pointer before ending your turn.
