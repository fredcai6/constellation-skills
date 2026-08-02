# x6 — Circuit-demand join readiness (corner-fingerprint artifact audit)

**Question:** Are the existing corner-fingerprint artifacts sufficient today to build a
per-circuit corner-demand profile that a regime-capability vector (power/aero/traction/
braking) can be crossed with — and what exactly is missing if not?

**Verdict up front:** No — not because the numbers are wrong, but because every named
artifact was built for a **different question** (tyre-wear panel diagnostics), by a
**different pipeline** (`src/physics/wear/`), than the one the regime-capability vector
lives in (`src/physics/layer2/`, issue #512/#496). The geometry columns inside them
(`shed_pct`, `gain_pct`, `headroom_pct`) are real per-corner braking/traction/flat-out
proxies and are a legitimate *starting material*, but turning them into a time-weighted,
regime-crossable demand profile is unbuilt work, not a blocked question. Sizes below.

---

## 1. Per-artifact audit

| Artifact | Grain | Columns (relevant) | Season coverage | Producing code | Status |
|---|---|---|---|---|---|
| `data/corner_fingerprints_{2019..2026}.csv` | one row per (gp, corner), per year | `v_apex, v_in, v_out, shed_pct (braking demand), gain_pct (traction demand), headroom_pct (flat-out-ness), n_laps`, tyre-refund jump/slope/se per phase (in/apex/out), noise/traffic sensitivity, `label` (rule-based) | 2019: 21 gps, 2020: 17, 2021: 20, 2022: 21, 2023: 22, 2024: 24, 2025: 24, 2026: 6 (season in progress; matches the known Bahrain/Saudi-dropped-2026 calendar) | `src/physics/wear/fingerprint.py::fingerprint_year` (promoted from `scripts/corner_fingerprint.py` per `docs/superpowers/specs/2026-07-04-wear-model-productization-design.md`) | **Promoted src/**, actively used by the wear pipeline |
| `data/corner_matches.csv` | one row per (gp, corner_ref, year) matched pair | `gp, corner_ref, year, corner_other, jaccard` (cross-year corner-index reconciliation via track-progress window overlap) | Only 9 gps × years {2022, 2024, 2025} vs `--ref 2023` (190 rows total) — a spot-check run, not a full cross-year table | `scripts/corner_match.py` (reads `src/physics/wear/fingerprint.py` output + `entry_sweep_*_windows.csv`) | **Scratch script**, not promoted, partial run only |
| `data/coast_frac_{2019..2026}.csv` | one row per (gp, driver, lap), ~18k–27k rows/year | `gp, driver, lap, coast_frac, n_samples` — fraction of the lap spent throttle-and-brake-off | Same year range as fingerprints | `src/physics/wear/push_signal.py::coast_fraction`/`write_coast_table` | **Promoted src/**. **Not a circuit-geometry artifact** — it's a per-driver-per-lap racecraft signal (pushing vs. track-position-managing a gap), used only as a wear-panel lap-gating covariate. Same circuit gives wildly different values by driver/race situation; not usable as a fixed per-circuit demand feature. |
| `data/driver_corner_reliability_2023.csv` | one row per (year, gp, corner, driver) | `noise_pct, n_eff` — measurement-noise decomposition for weighting the wear panel | **2023 only**, single year | `scripts/driver_corner_reliability.py` (reads `entry_sweep_2023_*_laps.csv`) | **Scratch script**, single-year, purpose-built for panel precision-weighting, not demand |
| `data/entry_panel_estimates_{year}_v_apex/v_out.csv` (+ 2023's bare/`_fp2` variants) | one row per (gp, corner, label, level) | per-compound decay (`d_HARD`, `kappa_HARD`, …), fresh-offset `u`, mass-beta covariate — a **tyre-decay panel fit**, not a demand measure | 2019–2026, matches fingerprint years; 2023 has 3 file variants (base, `_v_apex`, `_v_apex_fp2`) — historical/exploratory branching, not a clean series | `src/physics/wear/panel.py::panel_year` (promoted; `scripts/entry_panel_estimator.py` is the CLI) | **Promoted src/**, but the *output* is decay-rate estimates, orthogonal to demand |
| `corner_fingerprints*.png` (root) | plots: refund composition (entry vs exit refund, sized by noise) + sensor quality (headroom vs apex-drift slope) | — | matches whichever year the script was last run with | `scripts/corner_fingerprint.py::main` plotting block | Confirms intent: these are **wear-sensor-quality diagnostics**, not lap-time/regime-demand visualizations |

**Key semantic trap:** the fingerprint `label` column (`traction`, `entry`, `mixed-tyre`,
`flat-out`, `quiet`, `noisy` — see `src/physics/wear/fingerprint.py:104-118`) looks like a
regime tag but isn't one. It's a rule on **where the tyre-refund jump statistically shows
up** (does pit-fresh rubber pay off more on the way in or the way out of the corner), for
picking wear-sensor corners. A corner labeled `"traction"` here means "this corner's tyre
decay is best measured on exit speed" — it says nothing about how much of the circuit's
lap-time sensitivity to a car's traction *capability* runs through that corner. Don't
reuse this label as a capability-regime tag without relabeling.

## 2. Where the actual regime-capability vector lives (for contrast)

The brief's "regime-capability vector (power/aero/traction/braking)" is not hypothetical —
it already exists, built by a **separate** pipeline than any artifact above:
`src/physics/layer2/` (issue #512/#496, the five-view estimate store: Braking, Lateral,
Traction, PowerDrag, Coast), with readiness gating in `src/physics/layer2/regime_readiness.py`
(`docs/architecture/decisions/regime-readiness-rubric.md`) and a dashboard in
`scripts/regime_capability_dashboard.py`. That vector is **per (car, circuit, session)** —
already circuit-conditional (`frac_circuit` 0.44–0.65 dominates `frac_team` per the C3
finding in memory `physics-predictive-pipeline-509`). It has no circuit-demand join today;
`regime_capability_dashboard.py` renders coverage/frac_team/frac_circuit tables, not a
per-circuit demand cross.

Also adjacent, and closer in spirit to a demand profile than anything in the brief's list:
`data/damage_integrals.db` table `grip_bin_obs` (used by `scripts/corner_severity_gradient.py`)
stores **track-position-binned** `mu_lat_p90` (measured lateral g) and `v_mean` per bin —
a physics-native severity measure with an actual grip axis, unlike the wear-fingerprint
CSVs which only carry speeds (no radius/lateral-g, so "aero-limited high-speed corner" vs
"mechanical-grip-limited slow corner" are not distinguishable from `corner_fingerprints`
alone). It isn't circuit-demand-profiled either (no per-circuit time-share rollup exists),
but if a demand profile gets built, this store is arguably a better foundation for the
*aero/lateral* axis than the fingerprint CSVs are.

Separately, `src/evo_predictor/circuits.yaml` already carries a **hand-tagged**
`downforce: 1-5` categorical per circuit (subjective, not measured) — the live prediction
path's current (crude) stand-in for exactly this kind of demand signal.

## 3. Join sketch: circuit X, share of lap-time sensitivity per regime

What you'd want, per circuit X:

```
demand_share(X, regime) = Σ_corner∈X  time_weight(corner) × regime_purity(corner, regime)
                         + straight_time_weight(X) × 1[regime == power/drag]
```

Walking that through with what's on disk today:

1. **Enumerate corners for X, one year.** `corner_fingerprints_{year}.csv` filtered to
   `gp == X` gives this — but only for **one year's corner numbering**. Corner indices
   are auto-detected per (year, gp) sweep and are **not stable across years**
   (`corner_match.py` docstring, line 4-6) — a circuit with a layout tweak (e.g. Austin,
   COTA chicane changes; Qatar in and out of the calendar) silently renumbers.
2. **Assign each corner a demand vector.** `shed_pct` → braking-demand proxy, `gain_pct` →
   traction-demand proxy, `headroom_pct` → inverse power/aero-demand proxy (low headroom =
   near-vmax = power-limited straight-like corner; high headroom = grip-limited). This is
   usable as a **relative, unitless ordinal** signal per corner today. It is NOT a lateral-g
   or radius measure, so a genuine aero/downforce axis (vs mechanical grip) can't be split
   out of `corner_fingerprints` alone — see the `grip_bin_obs` note above.
3. **Weight by how much of the LAP the corner costs.** This is the load-bearing missing
   piece. `entry_sweep_{year}_{gp}_windows.csv` gives each corner's window as a
   **track-distance fraction** (`start`, `end` in cumulative-planar-distance/lap-length,
   e.g. `0.7637–0.8867`), not a time fraction, and only 3 speed samples exist per corner
   (`v_in`, `v_apex`, `v_out`) — not a full speed trace across the window. Converting
   distance-fraction to time-fraction (which is what "share of lap-time sensitivity"
   actually means) requires integrating 1/v across the corner, which these 3 points can
   only crudely approximate (trapezoidal on 3 samples).
4. **Straights are not first-class rows anywhere.** The complement of the corner windows
   (implicitly, whatever isn't inside a `[start, end]` window) is the straight-line/power
   regime, but no artifact tabulates straight length, straight duration, or top speed
   reached per straight. `headroom_pct` is a per-corner proxy for "how flat-out is this
   corner," but it can't stand in for "how much of the lap and how many seconds are spent
   on the straight before/after it."
5. **Cross-year/season pooling.** To build one demand profile per circuit (not per
   circuit-year), you'd pool fingerprints across years — but corner numbering instability
   (point 1) means you need `corner_matches.csv` for every (gp, year-pair), and that file
   only covers 9 of ~24 gps and 3 comparison years against a single 2023 reference.
6. **Cross with the regime-capability vector.** Once (2)-(4) give a per-circuit,
   per-regime time-share vector, crossing it with the layer2 five-view estimate store is a
   join on `(gp, year)` — mechanically straightforward once the demand side exists, no
   blocker there. The capability side is already circuit-conditional so the cross would
   need to be careful not to double-count circuit effects already baked into
   `frac_circuit`.

## 4. Named gaps, sized

| # | Gap | Size | Why |
|---|---|---|---|
| G1 | No time-weighting per corner (only distance-fraction windows + 3-point speed samples, not a time-share) | **M** | Needs integrating a fuller speed trace (or at minimum a numerically-justified in/apex/out interpolation) over the `entry_sweep_*_windows.csv` distance windows; the raw telemetry to do this right likely already exists in the trajectory/telemetry store, just not summarized this way |
| G2 | No straight/power-share rows — straights are implicit gaps between corner windows, never tabulated (length, duration, top speed) | **M** | New extraction pass over the same `entry_sweep_*` windows (complement set) plus a max-speed reach-check per straight |
| G3 | No lateral-g / radius axis in `corner_fingerprints` — can't separate aero-limited high-speed corners from mechanical-grip-limited slow corners from speeds alone | **M** | `grip_bin_obs` in `damage_integrals.db` already has measured `mu_lat_p90`; needs a join/rollup to corner grain, or building the aero axis from that store instead of `corner_fingerprints` |
| G4 | Cross-year corner-identity mapping (`corner_matches.csv`) covers 9/~24 gps, 3/8 years — most circuits have no stable cross-year corner index | **L** | Needs a full `corner_match.py` run matrix (all gps × all year-pairs vs a reference), plus a policy for circuits with real layout changes (can't just Jaccard-match those) |
| G5 | `label` column is a wear-sensor-suitability tag, not a capability-regime tag — reusing it directly would silently mislabel corners | **S** | Needs a dedicated regime classifier over the geometry columns (`shed_pct`/`gain_pct`/`headroom_pct`[/lateral-g from G3]), separate from `fingerprint.py::label` |
| G6 | `coast_frac_*` is a per-driver-per-lap racecraft signal, not a circuit property — not usable as demand-side input at all, despite being in the brief's artifact list | **S** (exclude, not build) | Scope correction: drop from the demand-join input set; it belongs to the wear panel, not here |
| G7 | 2026 season coverage is partial (6/~24 gps; season in progress as of 2026-07-17) and will only fill in as races run | **S** | Not fixable now — time-gated, will resolve itself; don't block on it, just don't compute a "full 2026" profile yet |
| G8 | No existing rollup anywhere (fingerprint pipeline or layer2) that outputs "per circuit, % of lap-time-sensitivity by regime" — confirmed absent by grepping `src/physics/` for `time_share`/`regime_fraction`/duration-weighted regime aggregates | **L** | This is the actual deliverable; everything above is raw material for it. `src/physics/segment_classifier.py` already classifies telemetry samples into `straight_brake/straight_throttle/straight_coast/corner` per lap for Layer-1 fitting — that per-sample classification is the closest existing building block to a genuine time-weighted regime share, but nothing aggregates it into a per-circuit summary today |

**Scoped null, explicitly:** none of this says circuit-demand-crossing is impossible or
that the physics doesn't support it — the underlying telemetry (full speed traces,
per-sample regime classification) that would answer G1/G2 already flows through
`src/physics/segment_classifier.py` and the trajectory store for other purposes. The gap is
that nobody has aggregated it into a per-circuit, time-weighted demand rollup yet. That's a
scoped build (roughly G1+G2+G8 as one extraction pass, G3 as a second pass reusing
`grip_bin_obs`, G4 as a wide corner_match run, G5 as a small relabel), not a research dead
end.

## 5. Bottom line

**Not sufficient today**, for one clean reason: the corner-fingerprint family was built
and promoted (`src/physics/wear/`) to serve tyre-decay panel fitting, and its geometry
columns are a *byproduct* useful for demand-profiling, not the designed output. The
regime-capability vector lives in a structurally separate part of the codebase
(`src/physics/layer2/`) that has never been joined to it. Building the join is real but
bounded work — no single gap above is a research question; all are named, sized
extraction/aggregation tasks (2×M scaffolding + 1×M cross-store join + 1×L wide match run
+ 1×L the actual rollup + small relabel/scope fixes), with the raw telemetry substrate for
the hardest piece (time-weighting) already present elsewhere in the physics pipeline.
