# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g2-review` — Dashboard + 2023-Q run (issue #512, C3 regime-capability vector readiness)

## Survey State Location
`.agent-work/512/g2-review/review.json` (under the issue workbench, never the worktree root).

## What Was Implemented
`scripts/regime_capability_dashboard.py` — loads the five-view estimate store, runs the G1
readiness core (`compute_readiness`) over the 2023-Q pool, renders
`reports/physics/regime_capability_2023Q.md` (per-component×axis summary table: 4 metrics +
flags + frac_team-vs-#492 headline) + diagnostic PNGs (gitignored). Smoke test
`tests/unit/physics/layer2/test_regime_capability_dashboard.py`. Final commit `42441108`
(re-run against the corrected G1 core `0116ec93` where `tau_resid` is leave-one-out; flag
rendering hardened with an explicit flags sub-dict + a negative-control guard test).

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-512
git log --oneline main..HEAD
git diff main...HEAD -- scripts/regime_capability_dashboard.py tests/unit/physics/layer2/test_regime_capability_dashboard.py
sed -n '1,80p' reports/physics/regime_capability_2023Q.md
```

## Task Statement
Build the traceable data→readout dashboard for #512: run the readiness core over 2023-Q and
render the per-component readiness table + plots; the rendered table is the evidence the G3
verdict reads. Measured-not-wired, single canonical path, honest covariance.
Full handoff: `.agent-work/512/crew-handoffs/g2-implementer-handoff.md`.

## Close Criteria (each → a review check)
- Loads with **`status=None`** so error rows count toward coverage (not the default `status="ok"`).
- Runs `compute_readiness` (G1, do not reimplement) and renders the summary table to
  `reports/physics/regime_capability_2023Q.md` with all 4 metrics + flags per axis + the
  frac_team-vs-#492 headline.
- **Flag columns are sourced from the core** `AxisReadiness.flags` / `ComponentReadiness`, NOT
  recomputed in the renderer. Verify the negative-control test (flip core flags → rendered cells
  follow) exists and passes; spot-check 2 axes that rendered flags == core `ax.flags`.
- The refreshed numbers reflect the corrected core: `tau_resid` is non-degenerate (NOT 0.0
  everywhere); `stable` is meaningful (TRUE only where `tau_resid ≤ within_σ`).
- Diagnostic plots written to `reports/physics/regime_capability_*.png` (gitignored).
- Pure assembly function separated from I/O; smoke test data/-independent (synthetic store).
- `py -m pytest tests/unit/physics/layer2/test_regime_capability_dashboard.py -q` green.
- Real run over `physics_estimates_g3wired.db` completes and the .md is committed (not the .png).

## Allowed Scope
`scripts/regime_capability_dashboard.py`, `tests/unit/physics/layer2/test_regime_capability_dashboard.py`, `reports/physics/regime_capability_2023Q.md`. Read-only consumer of G1 `regime_readiness` + `estimate_store`.

## Specific Exclusions (flag if touched)
- No modification to G1 `regime_readiness.py`, `estimate_store.py`, `pooling.py`.
- No GO/CONTEXTUAL/NO-GO verdict (G3). No evo import. No #511/#557 work.

## Constraints the Implementation Must Respect (each → a check)
- `constraint:physics_region_no_evo_import`.
- Single canonical execution path (§4) — no dual formats/fallback branches.
- Smoke test independent of `data/`; real run reads the absolute main-checkout DB only.
- Headless matplotlib (Agg).

## Map Anchors (inbound)
- **Structural:** `scripts/regime_capability_dashboard.py`; consumes `src/physics/layer2/regime_readiness.py` + `estimate_store.EstimateStore`; output `reports/physics/`.
- **Capability:** the traceable data→dashboard evidence surface (§4 done-done).
- **Constraints:** `constraint:physics_region_no_evo_import`; single canonical path.
- **Evidence expectations:** the rendered 2023-Q table is what G3 reads; flags must be core-sourced and self-consistent.

## Evidence Produced
`py -m pytest tests/unit/physics/layer2/test_regime_capability_dashboard.py -q` → 20 passed
(54 with G1 core). Refreshed table + the build_summary_rows-vs-ax.flags MATCH diagnostic in
`.agent-work/512/crew-handoffs/g2-implementer-result.md`. Headline: frac_team ABOVE 3% only on
max_power_w (4.0%)/brake_decel_ms2 (4.4%)/coast_rolling (44.1%); zstd calibrated only max_power_w;
stable TRUE only brake_aero_decel_per_m; ALL PASS = zero axes.

## Suggested Model Tier
`simple bounded` (Sonnet) — verify core-sourced flags + the refreshed run; the dashboard logic is thin.

## Stop Conditions
BLOCK if: flags are recomputed rather than core-sourced, `status=None` not used (coverage fake),
the real run didn't refresh against the corrected core, evo import / data-test dependency present,
or a verdict was smuggled in.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
