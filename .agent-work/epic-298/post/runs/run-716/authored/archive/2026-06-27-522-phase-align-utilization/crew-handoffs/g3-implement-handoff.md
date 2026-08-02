# Implementer Handoff — G3 Re-run + Verdict (#522)

## Gate
g3-implement (the payoff: does the lateral units fix un-pin the corner regimes?)

## Task
Re-run the C1 driver-utilization dashboard on the RBR 2023-Q subset with the lateral-units-corrected ceiling (the G2 `car_prior` conversion is live on this branch), compare per-regime U + honest σ against the #518 clipped baseline, and author a per-regime GO/CONTEXTUAL/NO-GO **VERDICT.md**. Update the architecture packet + decision-anchor text to reflect the units fix (Cartographer confirms at reconcile).

## Context — what changed and what to expect
G2 fixed a lateral units bug at the `car_prior` boundary (g-unit store A0/A2 → m/s²; Monaco tunnel cap 17→63 m/s). Before G2, `u_braking` and `u_fast_corner` clipped at `U_CLIP_MAX=2.0` (the #518 G6 NO-GO) because the ideal-lap corner caps were ~10× too low, making `v_real/v_ideal` blow up. With physical caps, the ratio should fall toward ≤~1 for a lap at/under capability. **This run measures whether that actually happens.** The G1 diagnosis already overturned the #518 "phase misalignment" story (true-distance registration changes U <1%); state that explicitly in the verdict.

## Close Criteria
- The dashboard runs on the RBR 2023-Q subset (Monaco / Italy / Great Britain / Singapore, VER) with the corrected ceiling; per-regime U + σ captured.
- A before/after table: #518 baseline (braking & fast_corner pinned at 2.000; straight Italy 1.07 / GB 1.23; slow_corner ~1.56–1.89) vs the corrected run.
- `.agent-work/522-phase-align-utilization/VERDICT.md` with a per-regime GO / CONTEXTUAL / NO-GO assessment **grounded in the actual new numbers** (not narrative), honest covariance considered, and an explicit statement that #518's "phase misalignment binding constraint" was superseded by the lateral units bug (this run's root cause).
- The secondary straight under-call re-checked: the lateral fix does NOT touch straight (power-drag), so straight likely persists — record it as a finding (route to triage / note for #525-adjacent work) rather than forcing it.
- Packet + decision-anchor text updated (see Required Evidence).

## How to run (verified seams)
- Dashboard: `py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"` from repo root. Use the OLD `data/physics_estimates.db` (the #510 / #518-G6 baseline store) for apples-to-apples — the lateral fix lives in `car_prior` and applies regardless of store. First confirm the GP names exist in the store: `EstimateStore("data/physics_estimates.db").load(year=2023)["gp_name"].unique()` (adjust spelling, e.g. "Great Britain" vs "British Grand Prix", to whatever the store uses).
- The dashboard writes its output (HTML/console table) keyed by the db stem; capture the per-regime U + σ for each case.
- Cache: `data/telemetry` (default). Store/cache read-only via the main checkout.

## Allowed Scope
- NEW: `.agent-work/522-phase-align-utilization/VERDICT.md` + any captured dashboard output.
- EDIT (docs only): `docs/architecture/packets/physics.md` (the utilization characterization-finding paragraph) and `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md` (the characterization-finding + review-trigger text) — update to reflect the units fix + the new verdict. Keep edits factual and minimal; Cartographer reconciles.
- If a `test_driver_utilization_dashboard.py` / `test_regime_utilization.py` assertion encodes the old clipped expectation and is now wrong, update it to the corrected truth (note which + why).

## Specific Exclusions
- No change to `src/physics/utilization/car_prior.py` or the consumer (G2 is done + committed). No store writes. No wiring of other constructors. No evo files.

## Constraints
- `py` launcher; physics rigor (units explicit). Verdict grounded in actual dashboard numbers.
- RBR subset only.

## Map Anchors (inbound)
- **Structural:** `scripts/driver_utilization_dashboard.py`, `struct:physics.utilization`.
- **Capability:** per-regime driver utilization — re-assessed verdict.
- **Decision:** `decision:ideal_lap_sim_two_sided_evaluator` (its characterization-finding + review-trigger get the units-fix update); `decision:c1_driver_utilization_design`.
- **Evidence:** braking/fast-corner un-pin from 2.0; straight stays as-is (lateral fix doesn't touch it); honest covariance preserved.

## Required Evidence
- The dashboard command + its per-regime U/σ output for the 4 cases.
- VERDICT.md with the before/after table and per-regime verdict.
- The packet + decision-anchor doc edits (diff).
- Test result for the g3 verification command.

## Verification Commands
```bash
py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"
py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py -q
```

## Suggested Model Tier
Sonnet — a bounded run + grounded verdict + minimal doc edits; the verdict is judgment but anchored in concrete numbers.

## Authority
You report the verdict the numbers support — GO / CONTEXTUAL / NO-GO per regime, honestly. The final acceptance is the human's at the spine review step. Do not soften or inflate; if braking/fast-corner still don't reach U≈1, say so and diagnose why (within reason).

## Stop Conditions
Stop and return if: the dashboard cannot load the store/cache; the GP names can't be resolved; or the corrected numbers contradict the G2 truth anchor (would mean the fix didn't propagate to the dashboard path — surface it).

## Return Format
IMPLEMENTER_RESULT to exactly `.agent-work/522-phase-align-utilization/crew-handoffs/g3-implement-result.md`: the per-regime before/after numbers, the verdict, files created/edited, evidence/commands, assumptions, stop conditions, out-of-scope observations, workflow feedback.
