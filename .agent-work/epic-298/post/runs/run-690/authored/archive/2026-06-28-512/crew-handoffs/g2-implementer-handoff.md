# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g2-implement` — Dashboard + 2023-Q run (issue #512, C3 regime-capability vector readiness)

## Task
Build `scripts/regime_capability_dashboard.py`: load the five-view estimate store, run the G1
readiness core over the 2023-Q pool, and render the **traceable data→readout** surface — a
per-component summary table (`reports/physics/regime_capability_2023Q.md`) + diagnostic plots
(`reports/physics/regime_capability_*.png`). Plus a data/-independent smoke test. Then actually
run it over the real store and capture the rendered table into the result.

## Protected Intent
This dashboard IS the characterization evidence the G3 verdict reads. It must be faithful and
reproducible (single canonical path). Measured-not-wired: no evo plumbing, no verdict assignment
beyond surfacing the G1 per-axis flags.

## Test Mode
test-after allowed — the script is mostly I/O/rendering; the testable logic is a pure
table-assembly function (smoke-tested on a synthetic store).

## Close Criteria
- `scripts/regime_capability_dashboard.py` with a CLI: `--db` (default the absolute main-checkout
  path below), `--out-dir` (default `reports/physics`), `--year 2023`.
- **Loads with `status=None`** so error rows are included → coverage is real, not trivially 1.0:
  `EstimateStore(db).load(year=2023, session_type="Q", status=None)`. (Default `status="ok"`
  would hide the denominator — do NOT use it.)
- Runs `compute_readiness(df)` (G1) and renders `reports/physics/regime_capability_2023Q.md`:
  one section/row per component×axis with coverage, frac_team (+frac_circuit/frac_resid), tau,
  tau_resid, within_sigma, zstd, z_frac_within_1, param_pair_corr, and the G1 boolean flags
  (separable/covered/stable/calibrated). Include a headline line per component restating frac_team
  against the #492-era "constructors not separable, frac_team ≤ 3%" claim.
- Diagnostic plots to `reports/physics/regime_capability_*.png` (headless `matplotlib.use("Agg")`):
  at least (a) frac_team per component bar, (b) zstd calibration per component (vs the 1.0 line),
  (c) coverage heatmap constructor×round. PNGs are **gitignored** — regenerable evidence, fine.
- A **pure** assembly function (e.g. `build_summary_rows(readiness: dict) -> list[dict]` or
  `render_markdown_table(readiness) -> str`) separated from I/O so it's unit-testable without a DB.
- Smoke test `tests/unit/physics/layer2/test_regime_capability_dashboard.py` over a tiny synthetic
  in-memory store (NO `data/` read) asserting the assembly yields one row per component with all 4
  metrics present and finite-or-None.
- **Actually run** the dashboard over the real store (the absolute main-checkout DB) and paste the
  rendered `regime_capability_2023Q.md` table + the produced plot paths into IMPLEMENTER_RESULT.

## Allowed Scope
`scripts/regime_capability_dashboard.py` (new), `tests/unit/physics/layer2/test_regime_capability_dashboard.py` (new), output under `reports/physics/`. Read-only import of `src/physics/layer2/regime_readiness.py` (G1) + `estimate_store.EstimateStore`.

## Specific Exclusions
- Do NOT modify `regime_readiness.py` (G1, locked), `estimate_store.py`, `pooling.py`.
- No GO/CONTEXTUAL/NO-GO verdict (G3). No evo wiring. No #511/#557 work.
- Do not commit `.png` (gitignored); DO commit the `.md` + script + test.

## Constraints
- `constraint:physics_region_no_evo_import`.
- Single canonical execution path (§4) — no dual formats / fallback branches.
- Smoke test independent of `data/`; the real run reads the absolute main-checkout DB only.
- Headless matplotlib (Agg) — no display.

## Map Anchors (inbound)
- **Structural:** new `scripts/regime_capability_dashboard.py`; consumes `src/physics/layer2/regime_readiness.py` (G1) + `estimate_store.EstimateStore`; output `reports/physics/`.
- **Capability:** the traceable data→dashboard evidence surface (§4 done-done).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; single canonical path.
- **Decision anchors:** decision pressure — the rubric thresholds surface in the table (from G1 `DEFAULT_THRESHOLDS`); do not hardcode new ones.
- **Evidence expectations:** the rendered 2023-Q summary table is what G3 reads to assign verdicts; frac_team per component must re-measure the #492-era claim.

## Data
Real store (real run only): `C:/Programs/f1Brainz/data/physics_estimates_g3wired.db` (absolute,
main checkout — the worktree has no `data/`). 10 constructors × 22 rounds, session_type='Q',
216 ok / 4 error.

## Required Evidence
`py -m pytest tests/unit/physics/layer2/test_regime_capability_dashboard.py -q` green; the rendered
`reports/physics/regime_capability_2023Q.md` content + plot file list, pasted into the result.

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_regime_capability_dashboard.py -q
py scripts/regime_capability_dashboard.py --db C:/Programs/f1Brainz/data/physics_estimates_g3wired.db
```

## Suggested Model Tier
`simple bounded` (Sonnet) — well-specified; care needed on `status=None` and the pure/IO split.

## Authority
The `status=None` load, the output paths, the component/axis table shape, and "no new verdict"
are DECIDED (commander). Plot styling and the exact pure-function signature are the implementer's call.

## Stop Conditions
Stop and return if: the real DB can't be read, `compute_readiness` errors on the real store
(report the traceback — that's a finding), allowed scope must be exceeded, or a verdict decision is forced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (pytest
output + the rendered 2023-Q table + plot paths), assumptions, stop conditions hit, out-of-scope
observations, workflow feedback.
