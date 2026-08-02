# Implementer Handoff

## Gate
`g1` — season runner + E-budget/refutil plumbing (epic #659 Wave 6, #670 season-scale run, Build-1 culmination)

## Task
Build the OFFLINE season runner that runs the landed #669 pilot machine over the full 2023 season (22 rounds × per-round 20-driver grid), as a PURE CONSUMER of the landed stages. Two parts:
(a) **Plumbing** in `src/physics/pilot/pipeline.py`: thread two run-parameters through `run_circuit` → `run_stage_e` — `budget_s` (raise the E per-circuit timeout) and a `refutil_db` override (so every round can write ONE shared observables slice). Defaults MUST be unchanged (budget stays 180s default; refutil defaults to the current per-circuit scratch path). This is pure plumbing, NOT a frozen-constant edit.
(b) **New scripts** `scripts/run_season_670.py` + `scripts/verify_season_artifacts_670.py` + tests.

This is the runner; the LONG detached run itself is a later gate (G2). G1 must PROVE the runner works via unit tests only — do NOT run the real E subprocess in this gate.

## Protected Intent
The season run must be OFFLINE, killable, and never dirty a tracked `data/f1_data_*.db`. A wrong runner that leaks online or corrupts the tracked DB defeats the reversibility contract the owner (AFK overnight) is relying on.

## Test Mode
`test-after allowed` — but tests are load-bearing here (they are the ONLY proof this gate ships, since the real E run is deferred to G2). Use a synthetic/monkeypatched `run_circuit` in unit tests; never spawn real E.

## Close Criteria
- `run_circuit(...)` and `run_stage_e(...)` in `src/physics/pilot/pipeline.py` accept `budget_s` and `refutil_db` (or an equivalently-named refutil override) and forward them correctly; run_circuit forwards `budget_s` to run_stage_e (it currently does NOT). All existing defaults unchanged; all existing pilot tests still pass.
- `scripts/run_season_670.py`: enumerates the 22 2023-Q rounds; reads each round's ACTUAL driver grid from `f1_data_2023.db` `session_classifications` (year=2023, session_type='Q'); copies the tracked `f1_data_2023.db` to a scratch path ONCE (never dirties the tracked DB — reuse the pilot's `run_pilot` scratch-copy pattern); calls `run_circuit` per round with that round's drivers + a raised budget (default ~480s) + a SHARED `refutil_db` path so E's `INSERT OR REPLACE` accumulates ALL rounds' `driver_class_observables` + `reference_laps` into ONE consolidated slice DB (NO hand-rolled merge); collects per-round `CircuitResult` → writes `season_results.json`; a missing round/driver PARKS (recorded, NO FastF1 pull).
- **VOCABULARY GUARD**: the season pooled fingerprint fit (`run_stage_g`, called inside `run_circuit`, uses `map_version=None` and the fit filters only `class LIKE 'severity:%'`) can silently blend incompatible taxonomies if circuits derive different severity vocabularies. Add a guard that, across the covered rounds, asserts a shared severity `vocabulary_id` and `k`; a divergent round is PARKED/FLAGGED (recorded in the results), never silently pooled. (Implement the guard where it is cheapest and correct — e.g. read each round's `reference_laps` `class_ids_json`/`vocabulary_id` from the consolidated slice and compare before the join/fit stage, or flag per-round at collection time.)
- `scripts/verify_season_artifacts_670.py`: exits 0 iff `season_results.json` exists AND the consolidated slice DB has ≥1 covered round with `provenance == "fresh"` AND both are non-empty; exits non-zero otherwise. Defaults its paths to the season runner's out-dir (`.agent-work/670-season-run/artifacts/`). This is G2's acceptance check.
- `tests/unit/physics/pilot/test_season_runner.py` covers: per-round grid-read from a synthetic DB; park-on-missing-round/driver; shared-refutil-DB accumulation (rows from ≥2 rounds coexist, no drop/dup); budget_s + refutil_db threaded through run_circuit→run_stage_e (assert the forwarded kwargs, e.g. via a monkeypatched run_stage_e/runner capturing the call); vocabulary-guard flags a divergent taxonomy; the tracked DB is never written (assert only the scratch copy is opened for write). Tests must be REAL (assert observable behavior), not vacuous, and must NOT invoke real E.

## Allowed Scope
- `src/physics/pilot/pipeline.py` (plumbing only: add the two forwarded kwargs; do not change stage logic or any gating decider).
- NEW: `scripts/run_season_670.py`, `scripts/verify_season_artifacts_670.py`, `tests/unit/physics/pilot/test_season_runner.py`.
- Read-only reference: `scripts/run_pilot_669.py`, `scripts/build_class_utilization_observables.py`, `src/data/database.py` (DatabaseManager / session_classifications getters).

## Specific Exclusions
- Do NOT edit any frozen constant set (`src/physics/layer2/frozen_constants.py`) — #659 F12 rule.
- Do NOT modify the stage functions' logic, the gating deciders, the panel, the join, or the fingerprint fit.
- Do NOT run the real season compute (that's G2). Do NOT touch `docs/architecture/*` (map fence, #671).
- Do NOT build the panel-over-corpus or the diagnostic (G3/G4).

## Constraints
- OFFLINE only — no FastF1 online calls; the pilot proved all stages run offline. A missing round/driver PARKS (no pull).
- NEVER write a tracked `data/f1_data_*.db` — copy to a scratch path once (the pilot's `run_pilot` does exactly this: `shutil.copy(src_db, per_year_db)` under the out-dir scratch).
- Frozen constants CONSUMED not minted; `budget_s`/`refutil_db` are run-params (invocation), not frozen edits.
- Student-t σ preserved end-to-end (you touch no σ code; just don't break it).
- Use the PINNED interpreter for any script you run: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py` (on this box `py`=3.12, which lacks the project deps). Worktree-first sys.path guard on bare scripts (see run_pilot_669.py lines 21-24: `sys.path.insert(0, repo_root)`) to avoid the global editable `.pth` importing the MAIN checkout's src.
- pyright-0 on new code.

## Map Anchors (inbound)
- **Structural:** `src/physics/pilot/pipeline.py::run_circuit` (thread budget_s+refutil_db; it currently does NOT forward budget_s to run_stage_e — line ~892 calls run_stage_e without budget_s); `run_stage_e` (has `budget_s` kwarg default 180s at line ~587, `refutil_db` param); `run_pilot` (scratch-copy pattern, lines ~963-971); `build_class_utilization_observables.py` (E CLI, `--db` INSERT OR REPLACE accumulates — module docstring line ~38).
- **Capability:** season-scale-run — run the landed pipeline over 22 rounds × per-round grid, offline.
- **Constraints/assumptions:** offline-only; no-tracked-db-write; frozen-consumed-not-minted; budget-is-run-param.
- **Decision anchors:** decision:consolidated-slice — one shared slice via INSERT-OR-REPLACE accumulation (NO hand-rolled merge).
  `@grade: settled/measured · leans g1-implement,g3-implement,g4-implement`
- **Evidence expectations:** full per-round 2023-Q coverage is VERIFIED (all 22 rounds present in physics_estimates.db + telemetry_store.db + f1_data_2023 20-driver grid); provenance=fresh expected where stores cover the round.
- **Map confidence flags:** epic-659 docs/architecture map deferred to #671 → framed vs SOURCE (pipeline.py), not a packet. Verify against source, do not trust a stale packet.

## Deliverable Path Check
- **Committed** — `scripts/run_season_670.py`, `scripts/verify_season_artifacts_670.py`, `tests/unit/physics/pilot/test_season_runner.py`, `src/physics/pilot/pipeline.py`: all verified `git check-ignore` exit 1 (NOT ignored) on 2026-07-27. The three new files appear in `git status` (untracked) until staged; the pipeline.py edit appears in `git diff`.
- **Local-only** — none (season run artifacts under `.agent-work/670-season-run/artifacts/` are produced in G2, not this gate).

## Required Evidence
- LOAD-BEARING (prove rigorously): the new unit tests pass; run: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot/test_season_runner.py -q` — paste the pass line. The EXISTING pilot tests still pass: `... -m pytest tests/unit/physics/pilot -q`.
- LOAD-BEARING: show (test or short inspection) that run_circuit forwards budget_s to run_stage_e and refutil_db is honored.
- CONFIRMATORY (spot-check): pyright clean on the new files; a one-line note that no `data/f1_data_*.db` write path exists outside the scratch copy.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot/test_season_runner.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot -q
```

## Suggested Model Tier
`stronger` — reason: touches a load-bearing offline/reversibility contract at season scale, and the plumbing must forward correctly through a subprocess boundary.

## Authority
The plan is frozen by LAUNCH_ORDER-670 and ratified by the Admiral. Decisions already made: shared-DB accumulation (no merge); budget/refutil are run-params; 22-round 2023-Q slate with per-round DB-read grid; vocabulary guard required. You must NOT: mint a constant, edit a frozen set, change stage/gating logic, run the real compute, or decide the diagnostic/panel design (later gates). If you hit a genuine gap, STOP and return it — do not guess.

## Stop Conditions
Stop and return if: allowed scope must be exceeded; a frozen set must be edited; the shared-DB accumulation cannot work without changing stage logic; required evidence cannot be produced; a decision outside this authority is needed.

## Return Format
Write IMPLEMENTER_RESULT to `.agent-work/670-season-run/crew-results/g1-implementer-result.md` (completed slice, files changed, test mode satisfied, evidence produced with the pasted pass lines, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback). ALSO SendMessage cmdr-670 a thin pointer to that result file before ending your turn.
