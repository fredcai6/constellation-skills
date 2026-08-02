# De-confound Hardening Findings (deconf2.py)
# Epic #445 — physics state-space, prong #2
# 2026-06-14

Script: `.agent-work/445/envelope/deconf2.py`
Cache: `.agent-work/445/envelope/deconf2_nodes.npz` (61,399 nodes, same as first cut)
Output: `.agent-work/445/envelope/deconf2.out`

---

## 1. SAR-Suzuka Artifact: Status After Hardening

**Result: NOT fixed by Huber IRLS. Requires dropping the key.**

| Fit | Gate | SAR/Suzuka B (1e-3) | G@140 | Status |
|-----|------|----------------------|-------|--------|
| FitA | all race | 1.731 | 4.44g | OUTLIER |
| FitB | clean-air race | 1.665 | 4.40g | OUTLIER |
| FitC | quali only | dropped (0 nodes) | — | OK |

SAR had 829 race nodes at Suzuka, 655 under clean-air gate, 0 quali nodes. Huber IRLS
downweights individual outlier *observations* but cannot fix a key (track,driver) whose
**entire node cloud is biased**. SAR's race laps at Suzuka apparently generate a
systematically inflated grip signal — not random noise from a few bad laps.

**What the Huber did do:** it prevented the outlier key from distorting the shared tyre
terms (A, dCompound, wear). The global A, dMed, dHard are physically stable across fits.
But per-key B is estimated key-by-key in the block regression, so SAR's own column absorbs
its own cloud unimpeded.

**Fix applied in FitC:** the minimum-node gate (MIN_NODES=60) drops SAR/Suzuka from
quali-only fits because SAR had 0 quali nodes there. A hard gate on quali-node count
would be more principled than relying on total node count — needs to be gate on
*quali* nodes, not total. The SAR artifact is race-specific and should be treated as:
either (a) SAR genuinely drove unusually at Suzuka in the race (possible — different
car setup?), or (b) position tracking/timing error in that session. Without a
specific investigation, it is safest to **drop SAR/Suzuka from race fits** by
requiring ≥MIN_QUALI_NODES as a separate gate. Not implemented in this script;
flagged for deconf3.

**Conclusion:** Huber IRLS is not sufficient for key-level outliers. The robust tool
needed here is a **per-key outlier detection** step: compute each key's frontier
residual against the pooled model, flag keys with > 2-sigma B deviation from
track median, drop them. Added to the future-work list.

---

## 2. Mercedes Hungary Flip: Clean-Air Gating Results

**Result: Clean-air gating does NOT reconcile the flip. The contradiction is real.**

Hungary downforce ordering (constructor mean B):

| Fit | Gate | RBR | MERC | FER | WIL | MERC vs RBR |
|-----|------|-----|------|-----|-----|-------------|
| FitA | all race | 0.95 | 1.01 | 0.84 | 0.82 | MERC > RBR (+0.056) |
| FitB | clean-air race | 0.87 | 0.93 | 0.78 | 0.78 | MERC > RBR (+0.064) |
| FitC | quali only | 1.08 | 0.93 | 0.92 | 0.95 | RBR > MERC (-0.152) |

The Merc-HIGH ordering in race (FitA) **persists in clean air** (FitB). Removing
dirty-air laps actually slightly *increases* the Merc-RBR gap (0.056 → 0.064).
The Mercedes clean-air race flip at Hungary is not a dirty-air artifact.

**Why it persists — most likely explanation:**

The clean-air gate was built from lap-time gaps at lap boundaries. This correctly
filters lapping in close traffic, but it misses **genuine clean-air driving style
differences**. When Mercedes is running in free air during the Hungary race, they are
likely:

1. **Pushing harder on medium/hard tyres in fast corners** — race pace management on
   Merc's specific setup involves different corner-attack patterns than quali. In quali
   on soft tyres, Merc's W14 is *known* to be fast-corner weak (hence Merc-LOW in
   quali-only fit). In race trim, drivers may brake later into fast corners to protect
   the rear on mediums, generating a different g_tot signature.

2. **Fuel load effect** — early-race laps on full fuel shift mass, which increases the
   normal load and thus absolute lateral force, but our model measures g = force/mass,
   so fuel should cancel. However, fuel mass changes the weight distribution and may
   alter how much the car *understeers* vs *oversteers* in fast corners, changing the
   actual grip circle usage.

3. **Race-specific strategy** — Mercedes in 2023 Hungary was running a longer first
   stint than optimal (they started on mediums). Their early-race pace is faster
   relative to others because degradation hadn't hit yet. This means their "clean air"
   laps at lap 2-10 are at better tyre condition than competitors who pitted earlier.
   The model partially corrects for tyre age, but if Merc is on lap 3 of a medium
   while RBR is on lap 30 of a hard, the wear correction needs to be near-perfect to
   remove this. It is not (see cross-validation below).

4. **Track evolution** — rubber laid down during race makes the track faster. If Merc
   drives more laps in "cleaner" track conditions, their race-clean-air laps land on a
   higher-grip surface. Not modelled.

**What this means:** "Clean air" is a necessary but not sufficient condition for
de-confounding race data. The fundamental problem is that race context sets a
**different operating point** (tyre age, fuel load, rubber, strategic lap targets)
than quali. The confounds that remain after clean-air gating are structural.

**Node count asymmetry at Hungary:**

| Driver | Race nodes | Clean | Dirty |
|--------|-----------|-------|-------|
| VER (RBR) | 4398 | 4398 | 0 |
| PER (RBR) | 4816 | 2795 | 2021 |
| HAM (MERC) | 4615 | 2713 | 1902 |
| RUS (MERC) | 4683 | 1933 | 2750 |
| LEC (FER) | 4904 | 2056 | 2848 |
| SAI (FER) | 4939 | 3241 | 1698 |
| ALB (WIL) | 5090 | 3783 | 1158 |
| SAR (WIL) | 5258 | 1109 | 4149 |

VER was in clean air for all 4398 race nodes (dominant race win). This does NOT mean
his B is upward-biased — it means his data is unusually clean. But his B (0.88 FitB)
is actually below what quali would suggest for RBR (1.08 FitC). The Merc drivers
RUS and HAM have 1933 and 2713 clean nodes respectively — enough to be credible.

The flip in FitB (MERC still highest) is therefore **not** an artifact of node-count
imbalance or dirty-air leakage. It reflects something real about how Merc's car
operates in race conditions at a high-downforce track.

**Conclusion:** Clean-air gating is a useful filter but does NOT reconcile the
quali-vs-race Merc ordering contradiction. The clean-air Merc race B (0.93) remains
above RBR (0.87), while quali shows the reverse (Merc 0.93, RBR 1.08). The gap has
narrowed from 0.056 → 0.064 vs the quali gap of 0.152, but the sign has not flipped.
The contradiction is genuine: the W14 generates *more* lateral force in race (even
clean-air race) at Hungary than in quali, despite being fast-corner weak in quali.
This is either (a) a car that operates differently under fuel/tyre loads at race pace,
or (b) a residual confound we haven't controlled for. Either way, **race data cannot
be used to rank downforce capability without additional controls we haven't built.**

---

## 3. Per-Compound Wear Results

**Result: Qualitatively physical but quantitatively suspicious — intercept leakage.**

| Fit | dMed | dHard | wear_soft | wear_med | wear_hard |
|-----|------|-------|-----------|----------|-----------|
| FitA (all-race) | -0.339g | -0.271g | -0.0353 g/lap | +0.002 | -0.002 |
| FitB (clean-air) | -0.273g | -0.231g | -0.0304 g/lap | 0.000 | -0.003 |

The compound offsets (dMed, dHard) are larger here than in the first cut (-0.26, -0.24).
That's because the per-compound wear slopes now partially absorb what was previously
a shared wear effect.

**The soft wear slope is anomalously large (-0.035 g/lap).** This is almost certainly
**intercept leakage**: quali nodes are tagged SOFT/age=0, and race SOFT nodes appear
only in the first stint (fresh stints starting soft). The model "sees" SOFT tyres
at age=0 (quali) and SOFT at age=5-10 (race early stints) and interprets the gap
as high wear per lap. But that gap is partly:
- The quali frontier being higher than race (this is the race confound we're trying
  to remove — circular)
- Real soft degradation being model-conflated with the quali/race session gap

The medium wear slope (≈0) means the model sees no wear on mediums. This is consistent
with race mediums being run during the "anti-degradation" phase where drivers manage
pace. Hard wear slope (-0.002 g/lap) is more physically reasonable.

**Per-compound wear adds noise** to the tyre model rather than improving it, because
the soft slope is absorbing the session (quali vs race) intercept difference.
The shared-slope first cut (-0.0014 g/lap) was more stable because it didn't have
the free DOF to absorb the session gap.

**Recommendation:** If per-compound wear is desired, quali nodes must be separately
tagged and the session intercept modelled explicitly, not conflated with wear.

---

## 4. Cross-Validation Results

**Result: Tyre terms do NOT generalize out-of-track. Negative variance reduction.**

| Held-out track | Gate | n_train | n_test | Var raw | Var corrected | Reduction |
|---------------|------|---------|--------|---------|---------------|-----------|
| Monza | all race | 54,120 | 7,279 | 0.214 | 0.216 | -0.8% |
| Hungary | all race | 20,899 | 40,500 | 0.259 | 0.260 | -0.4% |
| Suzuka | all race | 47,779 | 13,620 | 0.267 | 0.272 | -1.6% |
| Monza | clean-air | 31,640 | 3,341 | 0.232 | 0.238 | -2.7% |
| Hungary | clean-air | 11,007 | 23,974 | 0.271 | 0.269 | +0.5% |
| Suzuka | clean-air | 27,315 | 7,666 | 0.278 | 0.285 | -2.2% |
| Monza | quali | 2,388 | 460 | 0.254 | 0.254 | 0.0% |
| Hungary | quali | 718 | 1,946 | 0.321 | 0.321 | 0.0% |
| Suzuka | quali | 2,222 | 490 | 0.315 | 0.315 | 0.0% |

The cross-validation measures whether the tyre correction terms (compound offsets and
wear slopes) fitted on two tracks reduce variance on the third (held-out) track. A
positive reduction would mean the tyre terms are capturing a shared physical truth.

**All reductions are near zero or slightly negative.** This means:

1. The tyre correction fitted on tracks A+B does not explain variance at track C.
   The compound/wear model is **track-specific**, not a universal tyre-physics term.

2. Quali-only gate shows ~0.0% (no correction at all) because quali nodes are all
   SOFT/age=0 — the wear and compound terms have nothing to work with.

3. The small negative reductions (adding noise) suggest the transferred terms
   actually *mispredict* the held-out track: e.g., soft wear fitted as -0.035 g/lap
   on Monza+Hungary systematically over-corrects the Suzuka race data.

**What this tells us:** The compound/wear confounds are different per track. Soft
compound in Hungary race sees different thermal behaviour than soft at Suzuka. The
"universal tyre physics" assumption — that dMed and wear_rate are track-independent
— is wrong at the level of precision we need for car ranking.

This is actually the expected result: Pirelli tyre compounds behave differently
on different track surfaces (abrasion, thermal window, rubber grain size). Our
model treats them as one number.

**Cross-validation verdict:** The de-confound model does not generalize out of sample.
It is a within-track-set descriptive fit, not a physics model that transfers.
Per-key B values are therefore best interpreted as "effective downforce + unmeasured
residual confounds" not as true car downforce.

---

## 5. Position on Race-vs-Quali Truth

**For car downforce ranking, quali is more trustworthy. Here is why.**

### Arguments for quali as ground truth:

1. **Same compound, same condition.** All quali drivers run on SOFT/fresh tyres.
   The tyre confound is zero — no compound split, no wear gradient, no strategy
   differences. Shared-A holds because everyone runs the same tyre.

2. **Maximum effort.** Quali is the closest approximation of "maximum performance"
   that we can observe. Race laps have pace management, fuel, traffic, and tyre care
   that all push laps away from the performance frontier.

3. **The Merc signal is clear and internally consistent.** Quali-only FitC shows
   Merc-LOW at all three tracks (Monza: 0.56, Hungary: 0.93, Suzuka: 0.78 vs
   RBR 1.23, 1.08, 0.93). This ordering is supported by the known 2023 W14 weakness
   in high-speed corners. The race signal contradicts this at Hungary.

4. **Teammate decomposition is best in quali.** FitC achieves between/within ratio
   of 2.88 — the highest of all three fits. This means the teammate noise collapses
   most in quali, and the between-team signal stands clearest.

5. **No cross-contamination with session intercept.** The soft wear slope anomaly
   (section 3) shows that mixing quali and race creates an artificial soft-wear DOF
   that absorbs the session gap. Quali-only avoids this entirely.

### Arguments for race as complementary data:

1. **Volume.** Quali gives ~2,900 nodes; race gives ~58,500. High-speed corners that
   are nearly always fast (Suzuka S1) give only a handful of quali nodes per driver.
   Race data is the only path to sufficient high-speed coverage per driver.

2. **The variance reduction on teammate decomposition from the first cut is real.**
   Even the impure race de-confound lifted the between/within ratio from 0.61 to 1.85
   (FitA: 1.91). Race data *does* carry car signal — the confound is mixed in, not
   dominant.

3. **Car character can persist.** RBR high-downforce survives consistently in every
   fit (FitA, FitB, FitC, and prior iterations). It's the most robust single fact.

### Verdict:

**Quali is truth for downforce ranking. Race is truth for nothing specific yet.**

Quali provides a clean, condition-controlled measurement of the downforce frontier.
Race provides volume but introduces at least four layers of confound (tyre compound,
tyre wear, fuel load, track rubber) that interact in track-specific ways. Our
cross-validation shows these confounds are NOT universally removable by a shared
tyre-physics model.

The specific reconciliation of the Merc Hungary flip: the W14's fast-corner *deficit*
in quali was real (Merc-LOW is structurally correct given the W14's philosophy).
What the race data shows — that Merc generates high effective lateral g in race at
Hungary — is also real, but it reflects something other than pure downforce:
likely a race-specific tyre loading behaviour or strategy that our model cannot
cleanly separate from wing capability.

**Implication for the pipeline:** Use quali-only for downforce B estimation.
The conditions-matrix de-confound with race data requires additional controls
(explicit session intercept, fuel proxy, per-track compound model) before it
can be trusted. The first cut's Merc-flip contradiction was a correct warning sign.

---

## 6. What Is Trustworthy Now

### Trustworthy:

- **Tyre-terms are physically directional.** MEDIUM < SOFT, HARD < SOFT in grip
  (both cuts). The sign is right. The magnitude is track-dependent (cannot transfer).

- **Between/within ratio improvement.** FitA: 1.91, FitB: 1.40, FitC: 2.88 vs
  iter3 quali-only 0.61. The de-confound architecture (shared tyre terms + per-key B)
  genuinely reduces teammate noise relative to car signal. This is the method's
  core validity.

- **RBR high-downforce.** Survives in FitC (best fit): Monza 1.23 (rank 1/4),
  Hungary 1.08 (rank 1/4), Suzuka 0.93 (rank 1/4). The only constructor to rank 1
  in downforce at all three tracks under the cleanest gate.

- **Merc fast-corner deficit in quali.** FitC: Monza 0.56 (rank 3/4 among those
  present), Hungary 0.93 (rank 3/4), Suzuka 0.78 (rank 2/4). Directionally consistent
  with known 2023 W14 character.

- **Huber IRLS is a useful addition.** It stabilises the global terms (A, dMed, dHard)
  against isolated lap anomalies, even if it cannot fix a systematically biased key.

### NOT trustworthy:

- **SAR/Suzuka B under any race gate.** 1.66-1.73 (unphysical). The artifact is
  not random noise — it's a systematic race confound specific to SAR's Suzuka race.
  Root cause unknown. Do not use. Requires explicit key-level outlier detection.

- **Per-compound wear slopes.** Soft wear (-0.035 g/lap) is absorbing the
  quali/race session gap, not pure tyre degradation. The per-compound extension
  added noise (cross-validation worsened slightly relative to shared-slope model).
  Revert to shared wear slope and add explicit session-type intercept for deconf3.

- **Race car ordering (including with clean-air gate).** Merc Hungary flip persists
  in clean air. Cross-validation shows tyre terms don't transfer across tracks.
  Race B values are "effective downforce + residual confounds" not pure car downforce.

- **Monza ordering under any gate.** Monza is low-aero — all teams run similar B
  values (0.55-0.65 in FitA). Discrimination at a power-sensitive track requires
  the *longitudinal* channel (drag/power), not the lateral channel.

---

## 7. What's Still Not Resolved / Future Work

1. **Per-key outlier detection.** Compute each (track,driver) B vs track median;
   flag keys > 2σ; drop before final fit. Would cleanly kill SAR/Suzuka without
   needing a quali-only filter.

2. **Explicit session-type intercept.** Add a `is_race` binary covariate to absorb
   the average quali/race grip gap. This breaks the conflation of soft-wear-slope
   with session type, fixing the per-compound wear estimation.

3. **Fuel proxy.** Lap number in race correlates with fuel burn-off (~1 kg/lap,
   ~0.1% mass reduction). Adding `race_lap / total_laps` as a covariate might
   capture the fuel-induced grip change (lower mass → lower absolute grip but not
   in g units — cancels out). However, balance-of-car changes with fuel may
   matter. To investigate.

4. **Track-specific compound model.** The cross-validation failure shows tyre terms
   don't transfer. Fitting per-track compound offsets (instead of global dMed, dHard)
   would fit better within-sample but eliminate the "shared physics" claim.
   The correct intermediate: per-compound tire *identity* (compound spec changes
   across rounds) — if Monza uses C4/C5/C6 and Suzuka uses C1/C2/C3, they should
   not share tyre offsets.

5. **More tracks / season.** Three tracks (Monza, Hungary, Suzuka) are too few to
   test consistency of ordering. Extending to 6-8 tracks across the season would
   allow a track-pair comparison of B ordering stability.

6. **4th independent confirmation of Merc-LOW.** The quali-only signal at 3 tracks
   is suggestive. A 4th track (e.g. Spain, Canada) where Merc's fast-corner weakness
   was noted in 2023 would strengthen the finding.

---

## 8. Immediate Action for the Pipeline

If forced to produce a car downforce ranking TODAY with available data:

- Use **FitC (quali-only)** B values with Huber IRLS.
- Drop Monza (low-aero, no discrimination in lateral channel).
- Report: **RBR > MERC ≈ FER > WIL** at Hungary, **RBR > WIL > MERC > FER** at
  Suzuka — but note the Suzuka WIL result is suspect (SAR no quali data, single-driver
  basis from ALB only after SAR is dropped).
- Confidence: directional only, not quantitative. The between/within ratio (2.88)
  is better than chance but not definitive.
- Do NOT use race data for car ranking until deconf3 adds session intercept +
  per-key outlier detection.

---

*Generated by: deconf2.py, 2026-06-14*
*Nodes: 61,399 (same collection as grip_deconf.py first cut)*
*Cache: .agent-work/445/envelope/deconf2_nodes.npz*
