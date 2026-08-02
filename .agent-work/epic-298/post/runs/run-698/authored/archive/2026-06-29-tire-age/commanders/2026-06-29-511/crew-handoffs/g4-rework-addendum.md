# G4 REWORK Addendum — fuel-corrected truth channel (Admiral APPROVED)

Builds on `g4-implementer-handoff.md` + your existing build. The Admiral ratified the reshape you probed. ONLY `build_truth_cells`' slope computation changes; the scoring core, LOO, and verdict rubric stay as built and proven.

## The reshaped truth (adopt exactly)
Replace the per-stint `lap_time ~ tyre_life` slope with a **per-race, cross-stint, fuel-corrected** degradation truth:

    per race: OLS  lap_time ~ stint_fixed_effects + global fuel(lap_number) + per-compound tyre_life_slope

The per-compound `tyre_life` slope is the (race, compound) degradation truth cell; weight = lap count. Use your probed model (it recovered monotone SOFT 0.095 > MEDIUM 0.071 > HARD 0.066). The implementer-noted aggregation caveat applies: use a **robust** per-compound aggregation (median or heteroscedastic-weighted) since the plain mean was noisy.

## Guardrails (non-negotiable, from the Admiral)
1. **Truth stays INDEPENDENT of the physics predictor** — pure lap-time + `lap_number` only. Do NOT use the physics mass model, ANY telemetry/grip channel, or the #443 sensor in the truth computation. The fuel term is a function of **lap_number** (race-lap), NOT the physics fuel/mass curve. This preserves non-circularity w.r.t. physics.
2. **Modality caveat in the verdict output** — the truth is lap-time-family (same as the compound_prior γ incumbent). So in `classify_axis_verdict` / the result: a physics **win or match is unambiguous and strong** (independent telemetry reproducing clean lap-time degradation); a physics **tie/loss is AMBIGUOUS** (the lap-time incumbent has home-field advantage on a lap-time truth). Surface this caveat in the verdict reason/notes. Do NOT gate NO-GO purely on physics-loses-to-γ; triangulate with the #443 telemetry cross-check.
3. **Minimal change** — only `build_truth_cells`' slope computation. Keep all 16 tests green; ADD a test for the new truth channel, INCLUDING a regression asserting the fuel-confounded naive per-stint slope is NOT what's used (e.g. on synthetic data with a known fuel ramp + known per-compound wear, the new truth recovers the wear ordering while the naive per-stint slope would invert).
4. **Re-run the real-data report** with the reshaped truth and report all predictors on the SAME cells: physics μ_tyre(k) [primary per-(race,compound) mean k AND season-pooled LOO], absolute-C# floor (compound_c_number, DB int), and a placeholder for compound_prior γ (the LIVE γ + #443 cross-check are wired in G5). Report neutral within-race P + magnitude R² for each.

## Definition of done (rework)
- `build_truth_cells` uses the fuel-corrected cross-stint truth; pure lap-time + lap_number only (evo-free, telemetry-free, #443-free in the truth).
- All prior 16 tests green + new-truth test(s) incl. the naive-slope-not-used regression.
- `simplification_limits --paths` clean; evo-free assertion still passes.
- Real-data report re-run: paste the new truth-cell summary (expect monotone-up SOFT>MEDIUM>HARD) + physics P / LOO P / placeholder-incumbent P / R² against the NEW truth.
- The verdict carries the modality caveat.

## Return
Overwrite `C:/Programs/f1Brainz-511/.agent-work/511/crew-handoffs/g4-implementer-result.md` with the updated result: add a "REWORK (truth reshape)" section with the new evidence blocks + the supplant finding against the corrected truth (does physics now carry real degradation-ordering signal? P vs incumbents + LOO). Keep Workflow Feedback. Return status complete (not blocked) if the reshape lands cleanly.
