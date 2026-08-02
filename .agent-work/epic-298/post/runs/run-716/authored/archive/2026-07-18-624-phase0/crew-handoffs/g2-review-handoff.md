# Reviewer Handoff

## Gate
`g2` (wide-sigma A/B checkpoint)

## What was implemented
`C:/Programs/f1-624/scripts/g2_wide_sigma_ab.py` (new, committed-eligible) — a standalone driver script that injects 2025 Japan `session_estimates` physics (pre-registered primary axis `lateral_total_grip_g`, constructor-broadcast) into `RuntimeModuleContext.driver_residual_states['quali']` via the existing `driver_residual_history_adapter` seam, with a widened sigma (16x variance / 4x SD inflation), and runs the headless `sampled-predict` runtime once baseline (injection off) and once injected. Full IMPLEMENTER_RESULT at `.agent-work/624-phase0/crew-handoffs/g2-implement-result.md` — read it first. Findings at `.agent-work/624-phase0/G2_FINDINGS.md`.

**Headline claim**: no STOP condition hit; the seam IS cleanly externally injectable via `SampledEvoRuntime.predict_from_features(runtime_context=...)` with zero `src/` modification. But the A/B is a bit-identical structural null (Brier baseline=injected=0.13028701052631578, G1 delta=0.0) — root cause claimed: `driver_quali_power_from_residual_history` is registered in `module_adapters/_registry.py` but present in ZERO `params/gold/*.json` manifests' stage `steps`/`fusion_order`, so the injected data is structurally never read regardless of what's populated in it.

## How to inspect the diff
`cd C:/Programs/f1-624 && git status --short` (expect `scripts/g2_wide_sigma_ab.py` new, plus g1's pre-existing `scripts/g1_correlation_screen.py`; `.agent-work/624-phase0/` is the local work area). Read the full script and `G2_FINDINGS.md`.

## Task Statement
Independently verify: (a) the "bit-identical null" claim is real and not a bug in the driver script that silently fails to inject anything; (b) the root-cause explanation (module absent from every manifest) is actually correct and not a red herring; (c) the seam-injectability claim (`predict_from_features(runtime_context=...)`) is real, not a misread; (d) the #623 CPU>0 claim; (e) sigma-widening is honestly justified, not copy-pasted; (f) no `src/` file was modified and no `data/*.db` was left dirty.

## Close Criteria — verify each explicitly
1. **Root-cause claim** — independently run `grep -l residual_history params/gold/*.json` (or equivalent) from `C:/Programs/f1Brainz` yourself; confirm zero matches. Then read `params/gold/sampled_runtime_manifest.json`'s quali-stage `steps`/`fusion_order` list yourself and confirm `driver_quali_power_from_residual_history` (or its registry name) is genuinely absent — this is the load-bearing claim behind "the null is structural, not a script bug."
2. **The null is not a script bug** — read `scripts/g2_wide_sigma_ab.py`'s injection code path yourself. Confirm the script actually constructs a NON-EMPTY `DriverResidualState` (with real, non-zero `residual_mean` values derived from `lateral_total_grip_g`) and actually threads it into the `RuntimeModuleContext` passed to `predict_from_features`. If the injected dict/dataclass field name is wrong, or the injection point isn't actually reached, that would ALSO produce a bit-identical result but for the wrong (buggy) reason — rule this out explicitly, e.g. by adding a temporary print/assert or by tracing the exact keyword the runtime reads (`context.driver_residual_states.get(adapter.task)` per the original anchors) against what the script sets.
3. **Seam-injectability claim** — read `src/evo_predictor/sampled_runtime.py`'s `SampledEvoRuntime.predict_from_features` signature yourself; confirm it genuinely accepts an externally-supplied `runtime_context` (or equivalent) without needing any `src/` edit. Confirm the claim "zero `src/` modification" against `git status`/`git diff --stat` — no tracked `src/` file should appear changed.
4. **CPU>0 / #623 regression check** — the implementer's evidence is a process-CPU-time polling snapshot (six samples, ~1.03 CPU-s per 0.5s wall-clock) plus a 208.9s total wall-clock matching "~3-4 min per race." Sanity-check this is a plausible CPU-bound signature (steady ~1x core utilization, not 0%) — you do not need to re-run the full ~3.5min sampler yourself unless you doubt the evidence; if you do doubt it, re-run one stage and watch CPU yourself.
5. **Sigma-widening formula** — read the exact formula in `G2_FINDINGS.md` / the script docstring; confirm it is NOT simply copy-pasted from a single view's own stored diagonal (it should show independence-floor + explicit inflation-factor reasoning, per the handoff).
6. **No `src/` modification, no dirty `data/`** — `cd C:/Programs/f1-624 && git status --short` (only `scripts/g2_wide_sigma_ab.py` new, nothing under `src/` modified) AND `cd C:/Programs/f1Brainz && git status --short data/` (expect empty — confirms the claimed cleanup).
7. **G0/G1 read discipline** — confirm from the logs/JSON that G0 and G1 were each computed exactly once per stage (no iteration/tuning loop visible in the script).

## Allowed Scope
Read-only review of `scripts/g2_wide_sigma_ab.py`, `.agent-work/624-phase0/G2_FINDINGS.md`, `.agent-work/624-phase0/crew-handoffs/g2-implement-result.md`, `.agent-work/624-phase0/g2_*_run.log`, `.agent-work/624-phase0/g2_*.json`, and the cited `src/evo_predictor/` files (read-only). Do not modify the implementer's script. If you find a real bug (e.g. the null is actually a script bug, not the claimed manifest-absence), BLOCK with a precise description.

## Constraints
`py` not `python`. If you re-run anything, expect ~3-4 min per sampler stage; budget accordingly, and re-run only if you have genuine doubt about a specific claim (the grep/manifest-read checks are fast and should be your primary verification tool).

## Map Anchors (inbound)
Same as g2-implement's anchors (see `execute.json` g2-implement.anchors), plus the implementer's own additionally-traced anchors: `src/evo_predictor/sampled_runtime.py:200-217`, `src/evo_predictor/data_adapter/_helpers.py:197-282`, `src/evo_predictor/module_adapters/_registry.py:237-264`.

## Return Format
Return REVIEW_RESULT with an explicit **verdict: APPROVE** or **verdict: BLOCK**, one line per close-criterion item above (pass/fail + evidence), and any out-of-scope observations as triage candidates. Send it to me (ShipB-624) via SendMessage AND write it to `C:/Programs/f1-624/.agent-work/624-phase0/crew-handoffs/g2-review-result.md` before ending your turn.
