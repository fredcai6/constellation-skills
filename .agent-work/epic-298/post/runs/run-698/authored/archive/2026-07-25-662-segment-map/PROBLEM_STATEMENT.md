# Problem statement — #662 per-weekend segment-map derivation (2023-first, quali-side)

**Delegated run.** Reconciled against `LAUNCH_ORDER-662.md` (frozen principal) + issue #662 spec +
the merged substrate (#660 constants, #661 runtime, #625 segmentation, #638/#642 vocabulary).
No reachable human; Admiral = `main`.

## Mission
Build a NEW per-weekend segment-map **derivation** that POPULATES the merged `SegmentMap` runtime
(`src/physics/segment_map/`, #661) using thresholds imported from merged
`src/physics/layer2/frozen_constants.py` (#660). Map keystone of epic #659. Build 1 = 2023, quali-side.

## Reconciliation findings (order's assumed baseline vs actual merged code)
1. **Corner gate is CURVATURE, not lateral-g (`decision:corner-gate-is-curvature`).** Merged #660
   `frozen_constants.py` (owner-ratified 2026-07-25, settled/human) reframes spec §1: the
   corner/straight gate is `curvature > CORNER_CURVATURE_THRESHOLD` (0.005 1/m ⇒ radius ≤ 200 m),
   computed off the FIELD REFERENCE LAP geometry — a_lateral does NOT enter the gate. The docstring
   states this explicitly. This SIDESTEPS the launch order's "a_lateral unit trap" *for the gate*.
   The launch order hedged for exactly this ("honor the v_ref²×curvature formulation using the frozen
   threshold; do not introduce a second literal") — I follow the merged owner ruling. **The a_lateral
   unit (#639: m/s²) still bites the SEVERITY-DESCRIPTOR path** (radius/lateral_g), where #625 already
   converts m/s²→g via `GRAVITY_MS2`. That is the real locus of the unit trap.
2. **No field reference lap exists** — closest is `src/physics/ribbon.py::build_ribbon` (median-pooled
   XY → `{distance_m, curvature, px, py}`, geometry-only). Reuse it for geometry; add pooled speed +
   per-lap brake-onset to get the multi-signal reference lap the braking gate + descriptors need.
3. **No sector-line derivation exists.** `lap_times.sector{1,2,3}_time` (per-year DB
   `data/f1_data_2023.db`) hold durations; `tele_laps` has none; `circuit_info` empty. I derive sector
   LINES per weekend by time→distance interpolation (pooled median, sub-meter) myself.
4. **No persisted #638 mixture** — re-fit k=4 from the `grip_bin_obs` table via
   `descriptors_from_frame` + `fit_property_mixture`, consume as-is; per-era Student-t refit + fresh
   F12 gate DEFERRED to backfill (review T10, stated not skipped).
5. **DB-only constraint (project):** analysis code must not call FastF1. The durable `TelemetryStore`
   (#541) carries per-lap X/Y/Speed/brake via `session_fit.load_quali_session` (store-first,
   cache-fallback) — that is the sanctioned source. `build_session_ribbon` (FastF1-direct) is NOT used
   by the derivation.

## What to build (rulings honored)
- **Field reference lap** (pooled/representative, NOT per-lap): pooled geometry (`build_ribbon`) +
  pooled speed v_ref(s) + pooled brake-onset, on a common progress grid.
- **Canonical gate off the reference lap:** corner = curvature > `CORNER_CURVATURE_THRESHOLD`;
  braking zone = field **envelope** brake-onset at `BRAKING_ONSET_QUANTILE` (p10), running to corner
  entry — NEVER a mean; straight = remainder. Every threshold imported from `frozen_constants.py`.
- **Tiling:** complete contiguous partition of the lap (boundaries 0→lap_length, no gaps/overlaps).
- **Sector nesting:** FIA sector lines are MANDATORY cut points — straddlers SPLIT into same-class
  pieces (never snap); sliver-merge (`MIN_SEGMENT_LENGTH_M`=5.0) EXEMPTS sector cuts; fail CLOSED
  (`SectorLineUnavailableError`).
- **Corner descriptor** [radius_m, lateral_g] per corner (a_lateral m/s²→g via `GRAVITY_MS2` at the
  documented call site — the #639 boundary). **Turn direction** int8 from curvature sign.
- **Severity membership:** SOFT fractional weights over the #638 k=4 vocabulary (re-fit), via
  `MixtureFitAdapter` + `SegmentMap.reclassify_severity`/`posterior_membership`; EXACTLY 0.0 on
  non-corner rows. **Sub-phase marks DORMANT** (reserve signature; no backing store; do not populate).
  Adjacency computed on demand (runtime mod-arithmetic), never persisted.
- **Assemble + persist:** `SegmentMap.build(...)` → `SegmentMapStore.write` (cold/historical path);
  `layout_content_hash` fed GEOMETRY cut points ONLY (strip sector-forced splits, per identity.py).

## Acceptance (honest labels)
- **Construction checks** (catch coverage/arithmetic bugs, NOT mis-typing): tiling completeness;
  sector-nesting exactness. Close criteria of the tiling/nesting gates.
- **GATING check 1 — cross-weekend map stability** (< `MAP_STABILITY_DRIFT_M` = 10 m):
  **SCOPED NULL by construction for 2023** — F1 runs each circuit once per season, so no second
  same-circuit 2023 weekend exists. Report the coverage gap honestly (launch-order pre-authorized);
  provide **split-half within-weekend** boundary-drift as the substantive derivation-stability proxy.
- **GATING check 2 — typing spot-checks** vs P4-RESULT Bahrain (~14 corner arcs/lap; BIC = 15 turns)
  and #625 `regime_rollup` corner tallies. Right count + right locations on a couple of circuits.

## Out of scope
Cross-year corner history; per-corner identity beyond arc-length within a layout version; live
seeding (Build 3 #664); the per-era Student-t refit + fresh F12 gate; sub-phase population.

## Float/query candidates for the Admiral (surfaced, not blocking)
- **A_lateral-vs-curvature gate reframe:** I am following the merged owner ruling
  `decision:corner-gate-is-curvature` (gate = curvature) over the launch order's a_lateral framing.
  Flagging for visibility; not relitigating (settled/inherited in merged #660).
- **Cross-weekend stability = scoped null (2023 single-weekend-per-circuit).** Delivering split-half
  within-weekend as the robustness proxy. Flagging; pre-authorized as a coverage gap.
