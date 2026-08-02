# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement` (epic #601 wave-7 issue #628 Phase 3b, delegated)

## Completed slice
Built the per-driver, per-axis ABSOLUTE-deficit observable and its resumable batch CLI:

1. `src/physics/utilization/driver_utility_observable.py` — pure function `compute_regime_deficits(distance,
   curvature, v_real, v_ideal, ...)` returning per-regime `RegimeDeficits` (`g_*`, `n_points_*`,
   `sigma_lapsampling_*`, `mask_*`) for axes `braking, slow_corner, fast_corner, straight`. Reuses
   `regime_utilization._build_regime_masks` unchanged; the per-regime metric is the ABSOLUTE deficit
   `g = mean(v_ideal - v_real)` — never a ratio.
2. `scripts/build_driver_utility_observables.py` — resumable batch CLI (`--year --session-type --rounds
   --drivers --db`). Per (constructor, round) builds ONE `build_car_ceiling(strictly_pre=True)` + ONE
   `simulate_lap`, shared across that constructor's requested drivers; per driver calls
   `fit_best_lap_trace` for v_real, `resample_by_progress` onto the ribbon grid, then
   `compute_regime_deficits`. Persists rows to a scratch SQLite DB, idempotent per-axis
   (skip-if-present; a driver/round with an error row or all 4 axis rows present is skipped entirely
   without re-doing heavy compute).
3. `tests/unit/physics/test_driver_utility_observable.py` — TDD unit tests (8 tests, synthetic arrays only).

## Scope
**Files changed:**
- `src/physics/utilization/driver_utility_observable.py` (new)
- `scripts/build_driver_utility_observables.py` (new)
- `tests/unit/physics/test_driver_utility_observable.py` (new)

**Specific exclusions touched:** no — did not build the latent estimator (G2), the gate harness (G3), or run
any real batch beyond the 2-case smoke; did not modify `regime_utilization.py`, `car_prior.py`, or
`session_fit.py` (read-only reuse/import only); did not compute or store any ratio.

## Behavior changed
Yes — two new modules add a new observable and a new CLI entry point. No existing module's behavior changed
(`regime_utilization.py`, `car_prior.py`, `session_fit.py`, `characterize.py` untouched; `_lookup_constructor`
and `_make_track_df` imported read-only from `characterize.py`).

## Map Impact
- **Structural anchors touched:** `struct:physics.utilization` — added `driver_utility_observable.py` (pure
  deficit function) and `scripts/build_driver_utility_observables.py` (resumable batch CLI). Reused
  `regime_utilization._build_regime_masks`, `car_prior.build_car_ceiling`, `session_fit.fit_best_lap_trace`,
  `session_fit.load_quali_session`, `sim_evaluator.resample_by_progress`, `physics_simulator.PhysicsSimulator`,
  and `characterize._lookup_constructor` / `characterize._make_track_df` (read-only imports, not modified).
- **Capabilities added/changed/affected:** new capability — per-driver, per-axis absolute speed-access deficit
  against a `strictly_pre=True` causal car ceiling, persisted as tidy rows
  `(year, session_type, gp_name, round_idx, constructor, driver, axis, g_deficit, n_points,
  sigma_lapsampling, n_sessions_causal, error)`.
- **Constraints/assumptions touched:** `constraint:no-ratio-observable` (F4) — honored, grep-verified;
  `constraint:db-only` — honored (no FastF1 direct calls; `EstimateStore` + `load_quali_session`'s
  telemetry-store seam only); untracked-scratch-DB constraint — honored, never staged.
- **Decision anchors:** `decision:c1_driver_utilization_design` — implemented per the Commander's
  cold-critic-ratified construction (absolute deficit vs strictly_pre causal ceiling); not re-opened.
- **Claims/evidence produced:** at-ceiling → g≈0 (all axes, `TestAtCeiling`); corner-only 5% deficit →
  g>0 on braking/slow_corner/fast_corner, g≈0 on straight (`TestCornerOnlyDeficit`); SEM closed-form match
  on the deficit, not a ratio (`TestLapSamplingSigma`); grep proves no ratio in either new source file; a
  real 2023 Miami (round 5) VER/PER CLI run produced 8 rows and a re-run added 0 new rows (idempotent).
- **Trust limitations / drift found:** none found — all cited seam signatures (`build_car_ceiling`,
  `_build_regime_masks`, `simulate_lap`, `resample_by_progress`, `fit_best_lap_trace`, `load_quali_session`,
  `EstimateStore.load`) matched the handoff's "Exact seam signatures" section exactly on inspection.
- **Triage candidates:** `data/driver_utility_observables.db` is untracked but not literally covered by any
  `.gitignore` pattern (checked: no `/data/*.db` glob exists, only individually-named DB files are ignored) —
  a future crew should add an explicit `.gitignore` entry so an accidental `git add -A` cannot stage it. This
  was left out of scope here since `.gitignore` was not in the Allowed Scope's file list.

## Test mode
**Required:** `test-first (TDD) for the pure function; test-after for the CLI`
**Satisfied:** yes — `compute_regime_deficits` was TDD'd (test file written first, observed failing on
`ModuleNotFoundError`, then implemented to green); the CLI was built then verified with a 2-case smoke
(fresh run + resumable re-run) per the handoff's allowed test mode.

## Evidence

### 1. pytest — full pass
```
$ py -m pytest tests/unit/physics/test_driver_utility_observable.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-628
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 8 items

tests\unit\physics\test_driver_utility_observable.py ........            [100%]

============================== 8 passed in 1.03s ==============================
```

### 2. grep — no-ratio proof (handoff's literal verification command)
```
$ grep -nE "v_real ?/ ?v_ideal|/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py || echo "NO-RATIO-OK"
NO-RATIO-OK
```
(Strict gate form used to drive the plan — `! grep -nE ... && for f in ...; do git check-ignore "$f" && exit 1; done; true` — also passed; see engine journal `.agent-work/628-driver-utility/g1-implement-plan.json` item `m3-noratio-verify`.)

### 3. CLI 2-case smoke — 2023 Miami (round 5), VER/PER, real data
```
$ rm -f data/driver_utility_observables.db
$ PYTHONPATH=C:/Programs/f1-628 py scripts/build_driver_utility_observables.py --year 2023 --session-type Q --rounds 5 --drivers VER,PER --db data/driver_utility_observables.db
Loaded 216 ok-status estimate rows for 2023 Q from C:/Programs/f1Brainz/data/physics_estimates.db
  -> VER (Red Bull Racing) round 5 (Miami): inserted 4 axis rows (g_braking=2.0950380234750794, g_straight=0.5637725917501667)
  -> PER (Red Bull Racing) round 5 (Miami): inserted 4 axis rows (g_braking=5.3763711413312, g_straight=0.07118595042446055)
Done. Rows persisted to data/driver_utility_observables.db

$ PYTHONPATH=C:/Programs/f1-628 py scripts/build_driver_utility_observables.py --year 2023 --session-type Q --rounds 5 --drivers VER,PER --db data/driver_utility_observables.db
Loaded 216 ok-status estimate rows for 2023 Q from C:/Programs/f1Brainz/data/physics_estimates.db
round 5 (Miami): all requested drivers already present -- skipping
Done. Rows persisted to data/driver_utility_observables.db
```
Row contents after the first run (8 rows, all `error IS NULL`):
```
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'VER', 'braking',     2.0950380234750794, 294, 0.3127460688992049,  4, None)
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'VER', 'slow_corner', 2.728497995188024,  800, 0.1616307430114681,  4, None)
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'VER', 'fast_corner', 3.7831756370201424, 156, 0.2840884452593251,  4, None)
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'VER', 'straight',    0.5637725917501667, 250, 0.17880689841704778, 4, None)
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'PER', 'braking',     5.3763711413312,    294, 0.29317458570346233, 4, None)
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'PER', 'slow_corner', 2.0592820448779254, 756, 0.13440059575272142, 4, None)
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'PER', 'fast_corner', 2.1714648039850646, 200, 0.25052695538391334, 4, None)
(2023, 'Q', 'Miami', 5, 'Red Bull Racing', 'PER', 'straight',    0.07118595042446055,250, 0.16177500681060425, 4, None)
```
Additionally spot-checked round 1 (2023, VER) separately to confirm the no-causal-history path never
crashes the batch — it writes ONE error row instead:
```
-> ERROR VER (Red Bull Racing) round 1: build_car_ceiling(strictly_pre=True): round: no ok-status sessions
   with round_idx < 1; available: [1, 2, ..., 22]
```
(This round-1 probe row was written to a throwaway state and the DB was reset with `rm -f` before the
official 2-case smoke above, so the final `data/driver_utility_observables.db` on disk contains only the
round-5 rows shown.)

### 4. git status data/ — only the untracked scratch DB
```
$ git status --short data/
?? data/driver_utility_observables.db
```
Never staged; `data/driver_utility_observables.db` is not covered by an explicit `.gitignore` glob (see
Triage candidates above) but was at no point `git add`-ed.

### 5. Deliverable path check (not gitignored)
```
$ git check-ignore src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py tests/unit/physics/test_driver_utility_observable.py; echo "exit: $?"
exit: 1
```
Exit 1 = none of the three paths are ignored (correct — these are the committed deliverables).

### 6. Simplification limits (project engine-config rule, run proactively)
```
$ py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py tests/unit/physics/test_driver_utility_observable.py
PASS (3 files checked)
```
(First pass FAILED — `_process_round` in the CLI was 142 lines / cyclomatic complexity 28, over the
<100/<20 limits. Refactored into `_resolve_pending_drivers`, `_load_round_track`, `_process_constructor`,
`_process_driver` + a slim `_process_round` orchestrator; re-ran the full evidence set after the refactor —
all green, behavior unchanged.)

**Result:** pass

## TDD evidence
- Failing test observed: `ModuleNotFoundError: No module named 'src.physics.utilization.driver_utility_observable'`
  when running the test file against the not-yet-written module (manual attest, engine gate `m1-pure-fn.c1`).
- Passing test observed: see pytest output above (8/8 passed).
- Refactor while green: yes — the CLI's `_process_round` was decomposed into four helper functions after the
  simplification-limits check failed; the full evidence set (pytest, grep, CLI 2-run smoke, path checks) was
  re-run after the refactor and stayed green throughout.

## Docs/contracts touched
- none — no committed docs or contracts reference these two new modules yet; this result's Map Impact
  section carries the anchors forward for Cartographer reconcile.

## Assumptions
- `--rounds` and `--drivers` are comma-separated lists (the handoff's example used a single round/two
  drivers; the CLI generalizes to `3,4,5` / `VER,PER,HAM` etc. since "a `(year, session_type, rounds,
  drivers)` slice" implies plural).
- The scratch DB schema has no UNIQUE constraint; idempotency is enforced entirely by the Python
  existence-check-before-insert logic (per axis, and per error row) rather than a DB-level constraint —
  simpler to reason about and matches the "skip-if-present" wording without needing upsert semantics.
- `load_quali_session`'s default `store=None` already resolves to the absolute main-checkout path
  (`C:/Programs/f1Brainz/data/telemetry_store.db`, verified in `src/data/telemetry_store.py`), so the CLI
  does not need to pass an explicit `--store` override; only `--estimate-store` is exposed (default
  `C:/Programs/f1Brainz/data/physics_estimates.db`) since `EstimateStore` has no such built-in default.
- An error row uses `axis IS NULL` as its distinguishing marker (one row per failed driver/round, not four
  empty per-axis rows) — chosen because the row schema is fixed as given and NULL-axis is the natural
  "this driver/round never got past X" sentinel; `_error_row_exists`/`_axis_row_exists` both account for it.

## Stop conditions hit
- none — no seam signature mismatched the handoff's "Exact seam signatures" section; scope was not exceeded;
  the F4 no-ratio requirement was met (after one docstring wording fix — see Workflow Feedback); the scratch
  DB was written without needing to stage any tracked data file.

## Out-of-scope observations
- `data/driver_utility_observables.db` is not covered by any `.gitignore` glob today (confirmed: only
  individually-named `.db` files are ignored, no `data/*.db` pattern exists). Recommend a follow-up to add
  an explicit ignore entry so a future `git add -A` cannot accidentally stage it. Filed as a triage candidate
  above rather than actioned, since `.gitignore` was outside this gate's Allowed Scope file list.
- G2 (the latent estimator consuming these rows) and G3 (the gate harness) are the natural next gates; this
  gate's output schema (`g_deficit`, `n_points`, `sigma_lapsampling` per axis) is the contract they should
  build against.

## Workflow Feedback
- **Handoff gaps:** none material — the "Exact seam signatures" section was accurate for every seam used
  (`build_car_ceiling`, `_build_regime_masks`, `simulate_lap`, `resample_by_progress`, `fit_best_lap_trace`,
  `load_quali_session`, `EstimateStore.load`), which saved real rediscovery time.
- **Context rediscovered:** the handoff's suggested no-ratio grep verification command
  (`grep ... || echo "NO-RATIO-OK"`) is non-blocking as written — if a match IS found, `grep` exits 0 (found)
  and the `||` branch never runs, so the command still exits 0. I had to design a strict gate form
  (`! grep ... && ...`) for the engine's actual postcondition, and kept the handoff's literal form only as
  human-readable evidence output. Future handoffs authoring a "prove absence via grep" verification command
  should give the inverted (`!`) form directly so it's usable as a real gate, not just a print statement.
- **Instructions improvised around:** the module docstring initially spelled out the literal string
  "v_real / v_ideal" in prose to explain what the observable must NOT compute — that literal string itself
  tripped the F4 grep gate (a legitimate reading of "no `v_real / v_ideal`...anywhere in this module", not a
  gate bug). Reworded the docstring to describe the forbidden ratio without embedding the banned substring.
- **What would have made this easier:** the CLI's natural single-function orchestration (`_process_round`)
  blew the project's simplification-limits (cyclomatic complexity / function-length) on the first pass even
  though the handoff's Allowed Scope didn't call out that check — CREW_CONTEXT.md's "Simplification limits"
  rule is project-wide and applies regardless. Worth a one-line pointer in G1-style handoffs whose CLI has
  several sequential try/except stages ("expect to decompose the per-unit-of-work function into helpers to
  stay under the complexity/line limits") so it's budgeted for up front rather than discovered at the end.

## Return status
`complete`
