# Mission Frame — issue #704

Work id: `issue-704` · base `main` @ `3541d292` · **planning-only run**

## Intent

Remove the duplicated two-axis grouping loop inside the PANEL stage's replication instrument
(`src/physics/instrument_panel/replication.py`, under `struct:physics.instrument_panel`) by routing
both consumers through one private helper, while the module's measured outputs stay **bit-identical**.
The frame is deliberately **short** — this is a local, single-file, behavior-preserving change — but
NOT skipped, because the file is the panel's load-bearing instrument and sits under an owner-signed
frozen-constant decision anchor, so the governing anchors do change how the plan must be shaped
(what must be proven, and what may not move).

## Affected Capabilities

- `struct:physics.instrument_panel` — the read-only diagnostic sizing panel (#668, epic #659 stage
  PANEL). This run touches ONE of its three instrument modules, `replication.py`, and only its
  internal grouping mechanics: no public symbol in `__all__` changes name, signature, or return type.
- Panel outputs consumed downstream: the per-class channel verdicts
  (`compare_channels_by_class`) and the sigma-honesty coverage report
  (`out_of_sample_coverage`). Both must be unchanged value-for-value.

## Examples / Events

- `docs/physics/instrument_panel_668_gb2023q_report.md` — the emitted, committed panel report. It is
  the promoted artifact whose numbers must not move. **It cannot be regenerated in this checkout**
  (`data/reference_utilization.db` is absent), so it is a *frozen reference*, not a re-runnable check;
  the plan substitutes a numeric characterization harness for it and says so.
- `tests/unit/physics/instrument_panel/test_panel_corpus.py::test_corpus_panel_reproduces_identically`
  — the synthetic end-to-end reproducibility net that DOES run here, and does exercise the verdict path.

## Structural Anchors

- `struct:physics.instrument_panel` — `src/physics/instrument_panel/`, component. The change lands
  wholly inside `replication.py` (738 lines; limits 999 file / 99 function — comfortable headroom).
- `struct:physics.layer2` — `src/physics/layer2/frozen_constants.py`, component. Read-only here: the
  `REPLICATION_*` set is reached only through `frozen_replication_thresholds()`, which this run does
  not touch.
- `struct:physics.fingerprint` — `src/physics/fingerprint/address.py` supplies
  `FINGERPRINT_CHANNELS`, from which `DRIVER_ALIGNED_CHANNEL` is read. Untouched.
- Non-map script consumers (verified importers): `scripts/instrument_panel_668_report.py`,
  `scripts/run_season_panel_670.py`. Neither imports the private helpers; neither needs an edit.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — the new private helper must introduce no import at all;
  in particular nothing from evo / latent_power / compound_prior. Trivially satisfied and cheap to
  re-verify.
- **F12-independence (module invariant, stated in the module docstring):** the pure core imports no
  frozen `REPLICATION_*` constant directly — every threshold is injected via `ReplicationThresholds`.
  The helper lives below that seam and must not reach for `frozen_constants`.
- **Byte-identical acceptance (issue text), read as bit-identical floats.** The measured hazard:
  CPython ≥3.12 `builtins.sum` is Neumaier-compensated and `numpy.mean` is pairwise, so either one
  substituted for the module's current naive `+=` accumulation changes results on ~52% / ~42% of
  randomized ragged grids (measured, 20 000 trials — see PROBLEM_STATEMENT.md). Float addition is
  not associative: **per-key value order and grid iteration order must be preserved**, and the means
  must stay an explicit sequential loop.
- **No-frame-kill:** an undefined quantity stays `None` (never a fabricated 0.0); every class keeps a
  complete verdict.

## Decision Anchors & Decision Pressure

- `decision:replication-frozen-set-signed` — the `REPLICATION_*` set is owner-signed.
  `@grade: settled/human` · this run may not revise it; it is out of scope by the issue's own text.
- The packet's double-centering anchor (golf-correction = double-centering, `packets/physics.md`,
  graded `settled/measured`) — the correction formula
  `v - driver_mean[d] - class_mean[c] + grand_mean` is fixed. This run changes **how the means are
  grouped**, never **what is subtracted**.
- The packet's split-half unit anchor (cross-circuit 2-vs-2, graded `settled/human`) — untouched; the
  split stays injected.
- `claim:instrument_panel_reads_cells_directly` — unaffected: the change is below the read seam.
- **Decision pressure (new, this run forces it):** *the axis means are computed by naive sequential
  accumulation, deliberately and not for lack of a vectorized option.* Today that is an accident of
  how the code was written; after a dedup it becomes a load-bearing property of a shared helper that
  a future simplify-pass will be tempted to "improve" into `np.mean`. Surfaced as a decision
  candidate to record as a graded bullet in the packet at reconcile (proposed
  `@grade: settled/measured`, settle-by = the pinning regression test this run adds).
- **Decision pressure (deferred):** whether `_class_support`'s per-class rescan should join the same
  helper. Ruled out of scope here (it touches the verdict path) → triage candidate.

## Claims / Evidence Surfaces

- `claim:instrument_panel_reads_cells_directly` — verified by "no `join` symbol imported"; re-confirm
  cheaply by grep after the edit.
- Evidence each gate re-confirms:
  1. `tests/unit/physics/instrument_panel/` full green (26 replication + 5 frozen-constant + 10 corpus
     + 8 report + 11 scorecard + 7 variance tests) — the module's OWN pre-existing guard tests, per
     the repo lesson `consumed-frozen-module-run-guard-tests`.
  2. A before/after **`float.hex()` snapshot** over `_axis_means`, `grand_two_way_center`,
     `per_driver_demean`, `main_effect_margin_uncertainty`, `compare_channels_by_class` and
     `out_of_sample_coverage` on a fixed adversarial grid corpus — exact-bit equality, not `approx`.
  3. `py -m src.utils.simplification_limits` on the touched paths (repo evidence rule).
  4. pyright clean on the touched files (issue acceptance: pyright-0).
- Scoping note (repo lesson `scope-self-authored-regression-to-import-graph`): the real import graph
  of `replication.py` is the two panel scripts plus the instrument_panel test package — the regression
  check is scoped to `tests/unit/physics/` rather than the ~2350-test full suite.

## Map Confidence / Staleness / Disputes

- `struct:physics.instrument_panel` — `confidence: high`, reconciled 2026-07-27 (#671); the packet's
  description matches the source read at `context` (three instruments, injected thresholds, the three
  decision bullets). **No** low-confidence, stale, or disputed area this run depends on → no scout
  gate needed.
- One map gap worth naming, not a blocker: the packet documents the panel's *inputs* but not the
  absence of `data/reference_utilization.db` from a fresh checkout. That is why "regenerate the report
  and diff it" is unavailable as evidence; recorded here so a later run does not plan around a check
  that cannot run.

## Out of Scope

- The signed frozen values (`struct:physics.layer2` `REPLICATION_*`) and the double-centering method.
- `sector_scorecard.py`, `variance_decomposition.py`, the two panel scripts, the emitted report.
- `_class_support` / support-grid rescan dedup (deferred → triage).
- Any behavior change, however small, including "harmless" numeric improvements.
