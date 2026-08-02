# Ideas Board — `explore-driver-observable`

Living record + source of truth for the exploration of **how we measure the driver-utilization observable** (issue #717). Informal mode (no gated engine spine claimed yet) — promote to the full explorer spine if/when we drive to a confirmed spec. Every consolidation updates this file.

> **STATUS 2026-08-01 — cycle 4 GRADUATED; this thread is parked behind it.**
> The cycle-4 root cause (lateral-cap curvature-basis mismatch) is a physics-fit defect
> in its own right and is now filed as **#719**, with #684 (ribbon pit-filter no-op) as a
> cheap prerequisite. The wider pre-Build-2 round it belongs to is gathered on the holding
> board **#720** (physics measurement-fidelity), where this exploration is cluster C and
> the grip/σ work is cluster B (#712 + #687 + #678 read as one problem).
> **Ordering: #719 first.** Resuming the observable work against a mis-calibrated ideal
> would just re-measure the bias. Nothing below is retracted — it is waiting on a
> de-biased reference.

## The point

Epic #659 built the plumbing (telemetry → per-corner-class utilization → driver fingerprint → held-out prediction) and got an honest near-null: on 2023 the driver-utilization term lands on top of a no-driver baseline (between-driver σ≈0.36s vs within-driver weekend-to-weekend σ≈0.96s → **2.7:1 noise:signal**). The plumbing is fine; the question is whether **the object we chose to transmit is the right one**. This exploration is about the **unit, reference, sampling, corner-grouping, and how grip uncertainty enters** — *around* the ideal ceiling, not instead of it.

Owner framing (refined in-session):
- Improve **how we measure**, not (mostly) **what the model is**. Prefer measurement/estimator changes over model changes — though owner has explicitly relaxed this to reconsider the *physical quantity transmitted* (time → energy).
- **No leakage**: we must not need to *see quali to predict quali*. The predictor is the same physical corner seen earlier (FP3 → quali) or prior weekends; classes/families are the **transfer layer** for cold-start, not the measurement layer.
- The trait is **not a scalar — it's a distribution.** Peak is a quantile of it, not a different thing. Stop collapsing to the max/mean; look at the distribution.
- Lead with **plots**, not tables.

Kill condition (ONLY against the proper methodology — NOT prototype spikes): the direction dies only if driver deficit vs a **condition-adapted ideal** (below) shows no stable, separable per-driver signal across seasons. Prototype spikes that use a rejected reference (teammate-centering) or a static, non-condition-adapted ideal do **NOT** trigger this — we are in prototype mode and those tests are insufficient to judge the final model. **No null is recorded from them.**

## Current candidates

- **C1 — Condition-adapted ideal reference (THE direction, owner-steered).** Compare driver to the IDEAL *under the session's actual conditions* — an ideal lap that ADAPTS to track state (rubbering-in / grip evolution through quali), not the static pre-session car ceiling. Driver observable = apex/energy deficit vs this condition-adapted ideal. **No teammate subtraction.** This is "the next iteration of the ideal lap." STANDING: the real methodology; unbuilt. Buildable on existing grip machinery (GripStore/get_grip_at, track_grip_mult, sim).
- **C2 — Energy/apex unit, boundary-free.** apex-speed/energy is the cleaner, canonical, boundary-free unit for the deficit above. STANDING: confirmed as the unit; it carries C1's reference.
- **C3 — Consistency / predictability as a SECOND driver product.** dispersion may be a separable driver property (hinted by two spikes: within-noise large; sign-stability heterogeneous VER/ALO vs HAM/NOR). STANDING: candidate, unbuilt. Speculative until conditions are properly removed (some "dispersion" is just track-evolution).
- **C4 — Distribution substrate: all flying laps + FP3.** needed for BOTH condition estimation (C1) and dispersion (C3). STANDING: plumbing, not yet run.
- **REJECTED as methodology — teammate-centering.** Removes car+track but INJECTS the teammate's own habits/variability as the reference → measures driver-vs-driver, not driver-vs-ideal. Fine for a quick prototyping spike (fast car removal), NOT the final methodology. Every "kill test" number below inherits this confound.
- **Corner FAMILIES** — real + transferable + richer than severity (confirmed); retained as a grouping. The family-pooling spike used the rejected teammate reference + a static ideal, so it does NOT verdict the family idea.

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Max IS a metronome where the unit is clean (many corners σ<20ms, <1% of transit); the pipeline CAN see driver consistency | VER only, Monaco/Japan/Belgium 2023 Q, single best-lap-free extraction; NOT other drivers, NOT predictive | in-session probe (VER per-corner) |
| Consistency is a per-CORNER property, NOT per-CLASS — same severity class varies 10–70× in σ; the class reduction destroys the signal | VER, 3 circuits; NOT generalized across drivers/seasons | in-session probe |
| Absolute-second σ mostly tracks segment LENGTH (corr 0.74 VER / 0.33 field) — "seconds aren't a common currency" at corner grain | VER Monaco (0.74) + 10-driver Monaco/Japan (0.33); NOT weekend-to-weekend | in-session + excursion energy-vs-time |
| Energy/apex is a CLEANER unit: length-contamination vanishes (corr 0.33→−0.12 apex-v / 0.09 energy). Boundary-free (finding #4 fixed) | 10 drivers (5 pairs), Monaco+Suzuka 2023 Q, lap-to-lap; NOT weekend-to-weekend, NOT 20-driver (my run overwrote the field CSV) | excursion energy-vs-time |
| Switching UNIT does NOT rescue signal: within:between ≈ 2.3 in ALL bases (time 2.31 / apex-v 2.24 / energy 2.43), teammate-centered. The wall is basis-invariant → the fix is aggregation, not unit engineering | lap-to-lap within one session, 2 circuits, 10 drivers, 2–10 laps/driver; NOT weekend-to-weekend, NOT pooled-over-family | excursion energy-vs-time |
| Corners form cross-circuit-transferable FAMILIES on physics/energy features; every family spans ≥10/14 circuits even at k=6 | 209 corners, 14 circuits, 2023 Q, field-median reference; NOT multi-season, NOT wet/street-stratified | excursion corner-clustering |
| New families are richer than k=4 severity (ARI 0.47) on a real BRAKING/ENERGY axis; inside one severity class, braking-energy p10→p90 spans 0→6155 (invisible to radius/lat_g) | same as above; families are SOFT (silhouette ≤0.33 — a continuum, not islands) | excursion corner-clustering |
| Apex/energy is the CANONICAL cornering-skill observable; time-deficit is the less-standard choice. "Energy retained" self-ratio is our novel coinage (interpretability, not a new metric) | practitioner-heavy sources (MoTeC/vendors/coaching) + 2 academic anchors; full SAE texts not pulled | excursion skill-lit-research |
| The real design decision is the REFERENCE, not the unit: never compare raw apex speed across corners — reference vs modeled car-capability apex or grip-utilization (car+geometry-normalized). Teammate is the gold-standard car removal | literature consensus; corroborated empirically (2.3 wall persists even teammate-centered) | skill-lit-research + energy-vs-time |
| PROTOTYPE SPIKE (NOT a verdict) — family-pooling of a **teammate-centered** apex residual did not break the noise wall (w:b 2.04→~1.4). **Doubly confounded**: the rejected teammate reference (injects teammate habits) AND a static, non-condition-adapted ideal (leaves track-rubbering in the residual). Insufficient to conclude anything about the model — no null recorded | teammate-centered, static ideal, 2023 Q, thin laps | residual-stability (prototype) |
| Track rubbering-in (grip evolution through a quali session) is a KNOWN dominant variance source — a static ideal does not adapt to it, so any deficit-to-ideal is contaminated by "how rubbered was the track when this lap was set." OUT OF SCOPE (separate problem, owner) | owner domain knowledge | in-session |
| **BASELINE (vs the model's own ideal, no teammate) — the dominant term is per-corner IDEAL MISCALIBRATION, not driver skill.** Whole field shares ±15–20 m/s per-corner offsets (Italy c9 +20; Japan c13/19/36, Monaco c30 field BEATS ideal by ~18). This swamps driver spread and is why #659 read noisy-near-null (summing deficits sums the bias). Teammate-centering CANCELS it (why spikes missed it). **Underneath: driver IS moderately separable at a fixed corner — per-corner ICC(driver) median 0.49** — but corner-specific, NOT family-general (family-pooled ICC 0.05–0.12). Small persistent family signature (weekend ICC 0.36 fams1-2: STR high, VER/NOR/PIA low). Ideal is a ceiling ~76%; under-calls fast corners (class-2 40% neg). Length-contamination low (0.11) | 2023 Q, 10 circuits, 10 drivers, static ideal (track-evo left in), per-constructor ceilings all built; NOT a verdict — a baseline | excursion ideal-baseline |

## Open threads

- **TOP LEVER — ATTRIBUTED (excursion ideal-error-attribution).** The per-corner ideal-apex error is ENTIRELY in the **LATERAL corner-speed cap** (analytic cap vs sim apex corr 0.927; braking/traction/power/coast ruled out). Root cause = **curvature-basis mismatch**: lateral grip A0(mech)/A2(aero) FIT on sharp per-lap Matérn κ (`layer2/lateral_view.py:31`), then SIMULATED on the field ribbon κ that `build_ribbon` box-smooths ~2× flatter (`physics_simulator._compute_speed_caps`). Grip-on-sharp-κ applied to flat-κ → v_ideal inflated, per-corner (85% idiosyncratic, tracks grip demand corr −0.80; aero-v² tilt minor R²=0.15). **Fix = fit & simulate on the SAME κ basis — NOT de-smoothing** (raw κ over-corrects: class-2 → −25 m/s, see attribF_h1_counterfactual). Secondary: fast-corner under-calls (Japan/Monaco sweepers, field beats ideal) 41% hit the **`gsat` ceiling = an UNMEASURED fallback** (`build_car_ceiling` always passes `ceiling=None`). Also apex-station misregistration at worst fast corners (impossible 7.4–7.8g ribbon κ). De-biasing exposes the ICC-0.49 driver signal.
- Utilization skill is CORNER-SPECIFIC (per-corner ICC 0.49) not family-general (0.05–0.12) → prediction likely needs the SAME physical corner seen earlier (FP3→quali), not family generalization. (No-leakage path anyway.)
- C3 consistency-as-product — revisit after the per-corner bias is removed (else "dispersion" is partly miscalibration + track-evo).
- Grip uncertainty as identifiability/shrinkage weight, NOT additive predictive σ (issue thread 6; re-scopes #712).
- FP3 → quali (causal direction); pull FP3 to fatten distributions.
- Track-evolution / condition-adapted ideal — SEPARATE problem, parked (owner).

## Rejected ideas (with reasons)

- **Unit engineering as the fix for the null** — CULLED. The 2.3:1 wall is basis-invariant (time/apex/energy all ~2.3), so no choice of unit rescues per-corner separability. Revive only if a reference change (vs modeled ideal-apex) rather than a unit change moves it.
- **Energy-retained self-ratio (v_apex²/v_entry²) as the geometry-stripping move** — DOWNGRADED. It's a novel monotone re-expression of a speed ratio and is fairly length-clean empirically (0.09), but it does NOT strip corner geometry the way hoped; the literature's geometry fix is a matched car-capability reference, not a self-ratio.
- **k=4 severity {radius, lat_g} as the corner-grouping for skill** — CULLED as the *measurement* grouping (destroys per-corner signal; misses the braking/energy axis; only 3/4 classes populated). Retained as a possible coarse *transfer* prior.

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 0 (informal) | discuss + probe | Reframed #717: estimand = distribution not scalar; unit problem (corr 0.74 length); per-corner not per-class; FP3→quali no-leakage | Led to 3 excursions |
| 1 (informal) | 3 excursions | energy-vs-time (unit), corner-clustering (families), skill-lit (prior art) | Energy = cleaner unit but null on separability; families real+transferable+richer; reference (not unit) is the decision. Next: residual-stability test (boundary-free) |
| 2 (informal) | prototype spike | residual-stability: does family-pooling break the noise wall? | Inconclusive — pooling dents (2.04→~1.4) but the spike is doubly confounded (teammate reference + static ideal). **No null recorded** (owner: prototype mode). Owner correction → reference = ideal (not teammate); track-evo is a separate problem |
| 3 (informal) | baseline | ideal-baseline: rebuild relationships vs the model's OWN ideal (no teammate) | REFRAME — dominant term is per-corner IDEAL MISCALIBRATION (±15–20 m/s, whole-field), not driver. Underneath, driver moderately separable at a fixed corner (ICC 0.49) but corner-specific not family. TOP LEVER = fix per-corner ideal calibration. Baseline, not verdict |
| 4 (informal) | attribution | ideal-error-attribution: which corners / pattern / which view? | PINNED — error is entirely the LATERAL cap; root cause = fit/sim curvature-basis mismatch (Matérn κ fit → 2×-flatter ribbon κ simulated) + unmeasured gsat fast-corner ceiling (ceiling=None). Fix = same-κ-basis (NOT de-smooth). Closes #717 loop: near-null is a fixable lateral-view bug, not absent driver signal |
