# D9 competing-pathway sweep — spur verdicts

Task 16 closeout. D9 (ratified, progress.md line 47): "single canonical pathway; no
surviving spurs — retire/wire/document verdict per spur at T16." This file records
that verdict per known spur, plus two more found during a fresh sweep. Verdicts are
recommendations for follow-on issues, not code changes (Task 16 scope is docs-only).

| # | Spur | Verdict | Follow-on |
|---|---|---|---|
| 1 | Old `ParameterEstimator` → `fit_store` engine | **DOCUMENT** (mixed role, not a spur) | `.superpowers/sdd/followon-issues/01-fit-store-retirement.md` |
| 2 | `sim_evaluator.py` unconditional re-fit | **DOCUMENT + WIRE FOLLOW-ON** | `.superpowers/sdd/followon-issues/02-sim-evaluator-wiring.md` |
| 3 | `preprocessing/trajectory/grading.py` trust profile | **WIRE** (recommend) | `.superpowers/sdd/followon-issues/03-trust-profile-wiring.md` |
| 4 | `data/physics_estimates_g3wired.db` | **RETIRE** (already done; one script still references it) | `.superpowers/sdd/followon-issues/04-g3wired-cleanup.md` |
| 5 | Ephemeris fit_store-fallback flip | **DOCUMENT** (post-backfill decision, deferred) | `.superpowers/sdd/followon-issues/05-estimate-store-backfill.md` |
| 6 | Wear spine A (`wear/`) vs spine B (`layer2/tyre_separation.py`) role split | **DOCUMENT** (by-design split, not a spur) | none — captured in packets |
| 7 | `push_signal.py` producer never wired to a script | **WIRE** (recommend, minor) | No dedicated issue draft — recorded as a `packets/physics.md` Known Limits entry (low effort; see rationale below) |

---

## 1. Old `ParameterEstimator` → `fit_store` engine

**Current truth:** `FitStore`/`FitRecord` (`src/physics/fit_store.py`) has a real, mixed
role — it is NOT a dead spur and NOT purely a fallback. Every `ideal_lap()` call
(`src/physics/ideal_lap/generator.py`) uses `FitStore` **unconditionally** to identify
the (year, gp, driver) row and recover the power curve (`_load_fit_row`,
`_power_curve_from_row`) — that part is primary, not fallback, regardless of
`ceiling_source`. Only the **ceiling itself** is fallback-scoped as of this epic's
Task 1: `ceiling_source="estimate_store"` (default) routes through
`utilization.car_prior.build_car_ceiling`; `"fit_store"` (`_ceiling_from_row`) is kept
as an explicit-request path AND the automatic fallback when the estimate store is
unavailable.

**Full consumer enumeration** (grep `from src.physics.fit_store` / `fit_store\.`
across `src/`, `scripts/`, `tests/`, excluding `__pycache__`):

- **Producers:** `src/physics/session_fit.py` (`fit_driver`/`record_from_params`
  build `FitRecord` rows), `src/physics/fit_batch.py` (`run_batch` upserts),
  `scripts/build_physics_fit_store.py` (batch-build CLI).
- **Primary consumers (not fallback):**
  - `src/physics/ideal_lap/generator.py` — row/power-curve identification,
    unconditional (see above).
  - `src/physics/ideal_lap/residuals.py` — bulk-loads `FitStore` rows up front,
    feeds each into `generator.ideal_lap(fit_row=...)`.
  - `scripts/physics_fit_evidence.py` — `FitStore(db).load_fits(status=None)` is its
    only data source; writes `reports/physics/fit_store_evidence.md`.
  - `scripts/compare_capability_stores.py` — treats `FitStore` and `EstimateStore` as
    two coequal channels being cross-checked (#575 Task 2's divergence finding: median
    ~3σ across 75% of 2023-Q sessions, likely the old engine's `b_t` identifiability
    failure — supports the D1 ceiling switch).
  - `src/physics/sim_evaluator.py` (`evaluate_store`) — loads `FitStore` rows
    unconditionally as its row source (see spur #2).
- **Fallback-only consumer:** `generator._resolve_ceiling`'s `"fit_store"`/
  `"fit_store_fallback"` branch.
- **Tests:** `test_fit_store.py`, `test_fit_batch.py`, `test_session_fit.py`,
  `test_sim_evaluator.py`, `test_generator.py`, `test_residuals_sigma.py`,
  `test_compare_capability_stores.py`.

**Verdict:** DOCUMENT, not retire. `FitStore` is a real, still-used per-driver
power-curve store with four live production/diagnostic consumers plus the ceiling
fallback. Full retirement would require migrating `fit_evidence.py`,
`compare_capability_stores.py`, `sim_evaluator.py`, and `generator.py`'s row/power-curve
lookup onto some other row source (`EstimateStore` doesn't carry a power curve or a
per-driver — vs per-constructor — grain today) — that is real design work, scoped as
a dedicated follow-on issue, not a byproduct of this epic's ceiling-source switch.

## 2. `sim_evaluator.py` unconditional re-fit

**Current truth:** `evaluate_session` (`sim_evaluator.py`) calls
`fit_session_full(session, driver, ...)` fresh every time rather than reading a
cached `FitStore`/`EstimateStore` row — the module docstring documents this as
intentional ("this re-fit redundancy is a known concern — do not optimise it now").
Its only import outside its own file is `layer2/regime_utilization.py` pulling two
pure helpers/constants (not the evaluator entry points); its only CALLER is
`scripts/run_sim_evaluator.py`, a standalone CLI writing
`reports/physics/sim_evaluator_2023Q.csv`. No production/pipeline module invokes it.
`decision:ideal_lap_sim_two_sided_evaluator` explicitly scopes it as a
measurement/evaluation surface, not a wired prediction feature — its standalone
status is a ratified decision, not an oversight, and this epic did not touch its
behavior.

**Verdict:** DOCUMENT (already accurately documented in `packets/physics.md`'s Known
Limits — see this task's new entry) + file a WIRE follow-on for the re-fit
redundancy itself, since a cached-row read would be a straightforward efficiency win
whenever the evaluator is run over a large batch.

## 3. `preprocessing/trajectory/grading.py` trust profile

**Current truth:** `compute_trust_profile` has exactly one caller in the entire
repo — `tests/unit/preprocessing/trajectory/test_trust_profile.py`. It is exported
from `trajectory/__init__.py` and documented in
`docs/report_schemas/trajectory_trust_profile.md`, but no production module calls
it. Its original design intent (#448) was to replace ad hoc pass/fail gates with a
structured, per-observation-class quality readout — a real, tested capability that
happens to have no current caller because the artifact-boundary consumer
(`artifact.py`'s downstream Phase-2 reader) that would have called it was never
built, and is now formally deleted (Task 10).

**Recommendation: WIRE, not retire.** Task 10 just built a real persistence path
(`processed_telemetry` via `pvat_writer.py`) with **no quality gate at all** — every
fitted lap is persisted regardless of fit quality. `compute_trust_profile`'s
per-class held-out chi², NIS summary, and sector-crossing residuals are exactly the
signal that path is missing. Rationale for WIRE over RETIRE: the function is
tested, well-specified, and directly answers a gap the epic itself just created;
deleting tested/working code to declutter a "zero consumers" statistic is lower
value than closing the gap it was built for. Filed as a follow-on
(`03-trust-profile-wiring.md`) rather than done in this epic (would be a `src/`
change, out of Task 16's docs-only scope).

## 4. `data/physics_estimates_g3wired.db`

**Current truth:** Already retired as intended. `scripts/repopulate_g3wired_store.py`
no longer exists (deleted this epic, replaced by `scripts/backfill_estimate_store.py`
— see that script's docstring for the three defects the replacement fixes: stale
post-#525 field names causing every `[ok]` log line to silently overwrite a good row
with an error record; a same-day-only resume check; undersized constructor/round
defaults). `data/physics_estimates_g3wired.db` does not exist on disk in this
worktree (neither does `data/physics_estimates.db` — both are gitignored data files,
out of scope for this doc-only reconciliation). **One straggler remains:**
`scripts/compare_g3wired_braking.py:31,43` still hardcodes
`NEW_DB = ".../data/physics_estimates_g3wired.db"` and would fail today (file
absent); it has no test coverage and is referenced only from its own file plus
archived `.agent-work/518` handoffs.

**Verdict:** RETIRE (already substantially done). Follow-on: delete or repoint
`scripts/compare_g3wired_braking.py` (trivial cleanup, filed as a minor item in
`04-g3wired-cleanup.md` rather than done here since it's a `scripts/` edit).

## 5. Ephemeris fit_store-fallback flip

**Current truth:** `generator.ideal_lap`/`ideal_lap_sigma_grid` both default
`ceiling_source="estimate_store"`; `ideal_lap/residuals.py`'s `build_ephemeris`
family inherits this default rather than overriding it (no literal
`ceiling_source=` override anywhere in `residuals.py`). Practical consequence per
the epic ledger (progress.md D8 note): the estimate store's real-world coverage is
currently thin (backfill for the full 2019-2026 range was launched detached mid-epic
but this worktree has no visibility into its completion — `data/` is gitignored).
Until the backfill is verified complete and the estimate store's coverage matches
`FitStore`'s, most `ideal_lap`/ephemeris calls outside the backfilled years will
silently take the `"fit_store_fallback"` path (logged, `ceiling_source_used` records
it, never a crash).

**Verdict:** DOCUMENT as a deferred, data-dependent decision — not a code spur.
Nothing to retire or wire in `src/`; the "flip" already happened at the code level
(default is estimate_store), what's pending is the data-side backfill completion and
a verification pass. Follow-on issue tracks completion + verification
(`05-estimate-store-backfill.md`).

## 6. Wear spine A vs B role split

**Current truth:** Two independent, non-competing grip-decay measurement pathways
exist and do NOT cross-import:

- **Spine A** (`src/physics/wear/`): CSV entry sweeps → per-corner panel
  (apex-speed observable; realized + capability kappa; CR1 clustered covariance) →
  S×R ALS factorization + gauge-fixed factor covariance → `data/wear_model.db` /
  `params/wear/wear_run_<id>.json`. Feeds `ideal_lap/wear_derate.py`'s per-corner
  census transfer.
- **Spine B** (`src/physics/layer2/tyre_separation.py` + `tyre_supplant.py`):
  `race_stint_estimates` → crossed log-grip model (car envelope + `f_tyre` +
  `g_track`, PAVA monotone compound ladder, random-effects season pooling) →
  cross-modal falsification against fuel-corrected lap-time truth (#511 W3 verdict:
  CONTEXTUAL — clean separable decay axis, but does NOT cross-modally track
  race-window pace-degradation).

Different observable (grip envelope vs apex pace), different units, never
cross-validated against each other in production. This is a documented,
intentional split (packets/physics.md already frames W3 as measuring a
"structurally different axis" from spine A's per-corner kappa), not an
accidental duplicate pathway.

**Verdict:** DOCUMENT (already adequately captured across `packets/physics.md`'s wear
and race-stint-path sections — no further packet change needed this task). The one
open item is the not-yet-done cross-validation diagnostic between spine A's
per-corner `kappa` and spine B's per-stint `k` (already tracked as a Triage item in
the epic ledger) — carried forward as a follow-on
(`10-kappa-panel-vs-k-stint-diagnostic.md`).

## 7. Additional finding: `push_signal.py` producer never wired

**Current truth (found during the general dead/dormant sweep, not on the original
spur list):** `wear/batch.py`'s CLI auto-loads on-disk `coast_frac_{year}.csv`
tables (`_load_coast_tables`) that `push_signal.write_coast_table` is documented to
produce — but no script in `scripts/` calls `write_coast_table` anywhere. The
capability-kappa path (`--no-capability` to disable) is reachable only via a manual
Python invocation of `push_signal.write_coast_table`, not any committed CLI entry
point. `push_signal.py` itself has exactly one importer in the whole repo — its own
unit test (`tests/unit/physics/wear/test_push_signal.py`) — and is NOT re-exported
from `wear/__init__.py`'s `__all__` (unlike `windows`/`sweep`/`fingerprint`/`panel`/
`season_model`/`store`/`batch`, all of which are).

**Verdict:** WIRE (recommend) — write the missing driver script (a thin CLI wrapping
`write_coast_table`, mirroring `entry_speed_sweep.py`'s existing pattern) so the
capability-kappa path in `wear/batch.py` is reachable without manual invocation.
Low effort, not filed as its own numbered issue draft (see the Known Limits entry
added to `packets/physics.md` instead) — the maintainers should decide whether this
warrants a dedicated ticket or a same-day fix when someone next touches `wear/`.

## General dead/dormant sweep (beyond the named spurs)

Checked `grep -rln "def explore_\|def characterize_" src/physics/ src/preprocessing/`:
one hit, `src/physics/utilization/characterize.py` (`characterize_case`/
`characterize_cases`) — called by `scripts/driver_utilization_dashboard.py` (a real
production dashboard script) + its own test. Not dormant.

Checked importer counts for five "diag/characterize-shaped" candidates:
`wear/push_signal.py` (1 importer — its own test only, see #7 above),
`layer2/estimator_report.py` (1 importer — `scripts/plot_session_estimate.py`, a
plotting script; no test file, but a real single consumer, not zero), `layer2/
damage_scoring.py` (has a real `src/`-internal consumer, `damage_candidates.py`, not
dormant), `wear/sweep.py` and `wear/windows.py` (both wired internally into the
wear batch pipeline via `wear/__init__.py`/`batch.py`, not dormant). Of these,
`push_signal.py` is the one genuine zero-production-importer leftover — already
covered above.
