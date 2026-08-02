# G3 — Integration tracer findings

## What ran

Exact verified headless invocation from the launch order (Prior-Wave Verdict block), run from `C:/Programs/f1-624`:

```
PYTHONIOENCODING=utf-8 py -m src.evo_predictor.run sampled-predict \
  --sampled-runtime-manifest C:/Programs/f1Brainz/params/gold/sampled_runtime_manifest.json \
  --year 2025 --race Japan --seed 42 \
  --compound-prior-root C:/Programs/f1Brainz/params/gold/compound_prior \
  --db-path C:/Programs/f1Brainz/data/f1_data_2025.db \
  --output .agent-work/624-phase0/g3-tracer/2025_japan_tracer.json
```

Ran headless, completed (~4 min, `.pth` confirmed resolving to this worktree before the run), produced a 514 KB output JSON. `git checkout -- data/` run in the main checkout afterward per known issue #632 (running against `--db-path` rewrites/bloats `f1_data_2025.db` via `processed_telemetry`) — confirmed clean (`git status --short data/` empty) after cleanup.

## "Round-trips" — operationally defined and verified

- No error, exit 0.
- `scripts/g3_schema_assert.py --check` (committed, `git check-ignore` confirms exit 1 / not ignored) asserts the produced output's schema and spot-checks it against DB ground truth. All checks PASS (full output above/in the script's own run log).
- Spot-checked 3 driver rows (`VER`, `NOR`, `PIA` — the DB's actual top-3 Q classification for 2025 round 3) against the prediction: all three exist in the output's `driver_ids`/`position_distribution`, each with non-trivial predicted-position probability mass (0.099 / 0.313 / 0.224 peak). This is a roster/sanity spot-check (does the real driver appear, with a sane non-degenerate distribution), not an accuracy check — a probabilistic prediction cannot be "checked" against ground truth in the pass/fail sense the launch order's other probes use.

## The four-record contract — NOT what currently exists (a finding, not a failure)

DESIGN_SPEC.md's Phase 5 names a **four-record contract** as the eventual evo-facing product surface: weekend-state / car-basis posterior (full covariance, session-chained) / lap evidence / as-of-stamped feature view. That contract is explicitly **Phase 5, UNBUILT** — Phase 0 runs entirely before it exists.

What the LIVE `sampled-predict` path actually produces today (verified from this run's real output) is a single JSON with:
- `manifest_path`, `effective_seed` (run provenance)
- `prediction`: `schema_version=2`, `year`/`round_num`/`gp_name`, `sample_count=1000`, `driver_ids` (20 for this weekend), `final_order_samples`, `position_distribution` (per-driver position-probability dict, verified sums to 1.0), `pairwise_finish_probability_matrix`, **`stage_snapshots`: {quali, race_start, race}** (the 3-stage sampled sim's per-stage snapshots — this is the closest current analogue to "four records," but organized by SIMULATION STAGE, not by the Phase-5 taxonomy of weekend-state/car-basis-posterior/lap-evidence/feature-view), `stage_diagnostics`
- `breakdown`: `stage_diagnostics`

**This is the honest mismatch to record**: today's artifact is a single monolithic prediction-output JSON keyed by simulation stage (quali/race_start/race), not four separately-typed, append-only, as-of-stamped records. Phases 1-5 have not run, so this is expected, not a defect. It is exactly the kind of "unbuilt contract" gap the launch order anticipated by scoping this tracer's purpose as "decoupling seam/wiring risk from architecture risk" — the WIRING (CLI runs headless, produces a well-formed, DB-roster-consistent JSON) is confirmed sound; the Phase-5 CONTRACT SHAPE is simply not built yet, which is Phase 5's job, not Phase 0's.

## Verdict

**Round-trips: YES** (operationally: no error, schema-asserted, spot-check passes). **Four-record contract: NOT YET BUILT** (current shape is a single monolithic 3-stage-keyed prediction JSON — informational finding for Phase 5 planning, not a Phase-0 blocker).
