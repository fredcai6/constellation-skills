# Implementer Handoff — G4 Corner descriptors + turn direction + severity membership

## Gate
g4 (issue #662) — the HIGHEST-RISK gate (the #639 a_lateral unit boundary). Pinned interpreter:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Task
Compute the per-corner attributes and severity membership for a derived tiling. New files:
- `src/physics/segment_map/derivation/corner_attributes.py`
- `tests/unit/physics/segment_map/derivation/test_corner_attributes.py`

Provide functions that, given the nested tiling (boundaries_m + seg_type_code from g2/g3) and the G1
`ReferenceLap`, produce:
1. `corner_descriptor` — an `(n_segments, 2)` float64 array `[radius_m, lateral_g]`, finite with
   radius>0 on CORNER rows, and NaN (sentinel) on non-corner rows (matches the runtime's non-corner
   convention — SegmentMap.build validates corner rows all-finite radius>0; non-corner rows are ignored).
2. `turn_direction` — an `(n_segments,)` int8 array from the SIGN of curvature (LEFT/RIGHT/STRAIGHT).
3. `severity_membership` — an `(n_segments, k)` float64 array; corner rows = soft posterior over the
   #638 k=4 vocabulary; NON-corner rows EXACTLY 0.0. Plus the fitted mixture wrapped as a
   `SeverityMixture` (via `MixtureFitAdapter`) and its `VocabularyRef` (via `vocabulary_from_fit`), for
   g5 to persist.

## Protected Intent (the unit trap — read TWICE)
`a_lateral` is in **m/s²** (#639, confirmed). The mixture descriptor space is **g-units** for lateral_g.
The conversion m/s²→g via `GRAVITY_MS2` (`src.physics.constants`) must happen at **exactly ONE**
documented call site — never twice, never zero times, never a wrong constant. A silent mis-type here
poisons every corner. This gate exists to get this right.

## REUSE THE ESTABLISHED CONVENTION (do NOT invent a parallel one)
`src/physics/segment_classifier.py::SegmentClassifier.soft_class_membership` (read it — I quote it below)
already settled this exact mixture-query convention for a cornering sample:
```
radius = 1.0 / sample.curvature
lateral_g = sample.a_lateral / GRAVITY_MS2     # m/s² -> g at THIS one call site
descriptor = np.array([[radius, lateral_g]])
membership = posterior_membership(fit, descriptor)
```
Its docstring already documents the unit boundary ("sample.a_lateral is in m/s², so it DOES need dividing
by GRAVITY_MS2 ... Do not confuse the two call sites" — the other site, `corner_descriptors.
bin_row_to_descriptor`, takes mu_lat_p90 already in g and does NOT re-divide). MIRROR this convention
(factor a shared helper if clean); do not open a divergent one.

## The reference-lap difference (documented, endorsed by the Admiral — state it, don't hide it)
`soft_class_membership` uses a sample's MEASURED `a_lateral`. The `ReferenceLap` has NO measured
a_lateral channel — it is pooled geometry + pooled speed. So compute the model centripetal value:
`a_lateral_ms2 = v_ref**2 * abs(curvature)` at the corner's representative point, then
`lateral_g = a_lateral_ms2 / GRAVITY_MS2`, and `radius_m = 1.0 / abs(curvature)`.
- Radius / log-radius is the DOMINANT k=4 discriminator (#638) and is purely geometric (`1/|kappa|`) —
  identical in kind to the mixture's training axis, independent of push-level.
- The lateral_g axis differs only by the median-achieved (reference lap) vs p90-capability (grip_bin_obs)
  offset — a BOUNDED SECONDARY-axis approximation. DOCUMENT it inline as an accepted, DEFERRED refinement
  (per the launch order's "consume #638 as-is, state the deferral"). Do NOT switch to a p90-capability
  descriptor (Admiral ruling: that would couple the structural map to a capability signal it must not own).
- Representative point per corner: use the corner segment's APEX = the grid point of MAX `abs(curvature)`
  within the segment (tightest point); take `v_ref` and `curvature` there. (Document your choice; apex is
  the physical corner descriptor.) Guard degenerate `abs(curvature) <= 1e-9` (skip / sentinel, per
  soft_class_membership's own guard).

## Severity mixture (re-fit; pooled across the era, NOT per-weekend)
- Re-fit the k=4 mixture from `grip_bin_obs`: `GripBinStore(db_path).load(...)` →
  `src.physics.layer2.corner_descriptors.descriptors_from_frame(df)` →
  `src.physics.layer2.property_mixture.fit_property_mixture(descriptors)` (k_range default (2,4)).
- **Fit on the POOLED grip_bin_obs across the era's circuits (all 2023), NOT the single weekend** — the
  #638 vocabulary is a SHARED taxonomy stable across circuits (that is what its F12 gate validated). The
  same fitted mixture is reused across every weekend so `vocabulary_version` is STABLE (required for
  cross-weekend consistency, g6). State the pool scope you used.
- Wrap: `MixtureFitAdapter(fit, version=vocabulary_id)`; mint the vocabulary via
  `from_mixture.vocabulary_from_fit(mixture, taxonomy_name="severity", rules_era=<era, e.g. "2023">,
  fit_version=1)`. Compute membership via `posterior_membership` over the CORNER descriptors (or via the
  adapter). Rows sum to 1 on corner rows; EXACTLY 0.0 on non-corner rows. SOFT — no hard argmax.
- **Sub-phase marks stay DORMANT** — do NOT populate or build any sub-phase store.

## turn_direction
int8 from the SIGN of the reference-lap curvature at the corner apex (ReferenceLap.curvature is SIGNED —
confirm by reading reference_lap.py / ribbon.build_ribbon). Define a small IntEnum or documented codes
(e.g. LEFT=+1, RIGHT=-1, STRAIGHT=0); non-corner rows = 0 (STRAIGHT). State the sign convention.

## Sector-split corners (from g3): each CORNER row is descriptor'd from its OWN arc window — consistent by
construction (both halves read the same reference-lap geometry). No cross-row reconciliation needed.

## Close Criteria (MUST TEST)
1. **Unit boundary (LOAD-BEARING):** a known `(v_ref, curvature)` → hand-computed
   `a_lateral_ms2 = v_ref**2 * abs(curvature)`; assert `lateral_g == a_lateral_ms2 / GRAVITY_MS2`
   (GRAVITY_MS2 IMPORTED, not a literal 9.81) and `radius_m == 1.0/abs(curvature)`, and that the
   division fires EXACTLY ONCE (e.g. monkeypatch GRAVITY_MS2 and confirm lateral_g scales by exactly
   1/that value — proving no double/zero conversion).
2. **Membership invariants (LOAD-BEARING):** non-corner rows all EXACTLY 0.0; corner rows sum to ~1.0;
   shape (n_segments, k) with k from the fit.
3. **Descriptor validity:** corner rows finite, radius_m > 0.
4. **turn_direction:** signed-curvature synthetic → expected LEFT/RIGHT/STRAIGHT codes; non-corner = 0.
5. Use synthetic grip_bin_obs-shaped frames for the mixture fit in unit tests (deterministic); a real
   pooled-2023 fit gets a smoke test guarded on grip_bin_obs availability (skip cleanly if absent).

## Allowed Scope
`corner_attributes.py`; its test. Read (not edit): `reference_lap.py`, `tiling.py`, `sector_nesting.py`,
`segment_classifier.py` (soft_class_membership), `layer2/corner_descriptors.py`, `layer2/property_mixture.py`,
`layer2/grip_bin_obs.py`, `segment_map/from_mixture.py`, `segment_map/runtime.py`, `physics/constants.py`.

## Specific Exclusions
- Do NOT assemble the SegmentMap or write the store (g5). Do NOT populate sub-phase marks.
- Do NOT edit docs/architecture/*, existing segment_map runtime files, layer2 files, or frozen_constants.py.
- Do NOT join official corner-number markers (cosmetic; skip).

## Constraints
- a_lateral m/s²→g via GRAVITY_MS2 at ONE documented call site (#639). GRAVITY_MS2 imported from
  src.physics.constants (not a literal).
- Soft membership (no hard argmax); consume k=4 as-is; Student-t refit + fresh F12 DEFERRED (state it).
- Runtime invariants: corner_descriptor finite+radius>0 on CORNER rows; severity_membership EXACTLY 0.0
  on non-CORNER rows.

## Map Anchors (inbound)
- **Structural:** corner_attributes.py (NEW); segment_classifier.soft_class_membership (REUSE convention);
  corner_descriptors/property_mixture/grip_bin_obs (layer2); from_mixture (MixtureFitAdapter/vocabulary_from_fit);
  constants.GRAVITY_MS2.
- **Decision anchors:**
  - decision:a-lateral-g-boundary — m/s²→g via GRAVITY_MS2 at ONE documented call site.
    @grade: settled/human (#639) · leans g4
  - decision:severity-refit-consume-k4 — re-fit k=4 from POOLED grip_bin_obs; Student-t + fresh F12 DEFERRED.
    @grade: settled/human (launch order T10) · leans g4
  - decision:dormant-subphase — sub-phase reserved, not populated. @grade: settled/human · leans g4
- **Evidence expectations:** the descriptor is on the mixture's axis (radius=1/κ; lateral_g=a_lat/G);
  median-vs-p90 offset documented; non-corner membership 0.0; corner rows sum to 1.
- **Map confidence flags:** HIGHEST-RISK — the #639 unit boundary.

## Deliverable Path Check
- **Committed:** `corner_attributes.py`, `test_corner_attributes.py` — `git check-ignore` exits 1.

## Required Evidence
- pytest `test_corner_attributes.py` green incl. the two LOAD-BEARING tests (unit boundary + membership
  invariants). `simplification_limits --paths corner_attributes.py` clean.
- grep confirming GRAVITY_MS2 imported, no literal 9.81. In IMPLEMENTER_RESULT: the apex-point choice,
  the mixture pool scope, and the turn-direction sign convention.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_corner_attributes.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/corner_attributes.py
```

## Suggested Model Tier
Stronger — the #639 unit trap is the single most dangerous silent-error site in this issue.

## Authority
The unit boundary, reuse-soft_class_membership convention, pooled-era fit, consume-k4, dormant-subphase,
and NOT-switching-to-p90-capability are all DECIDED (Admiral-ratified). You MAY decide the apex-choice,
result shapes, and turn-direction codes (state them).

## Stop Conditions
Stop and return if: the descriptor can't be put on the mixture's axis without a second conversion; the
mixture won't fit (grip_bin_obs empty for the era) — report the data gap rather than fabricating; a
frozen value looks wrong.

## Return Format
IMPLEMENTER_RESULT to `.agent-work/662-segment-map/g4-impl-result.md`: slice, files, test mode, evidence
(pytest incl. the two load-bearing tests + simplification + the no-9.81 grep), apex choice, mixture pool
scope, turn-direction convention, assumptions, stop conditions, out-of-scope, workflow feedback.
**Deliver a concise summary (verdict + result path + how you proved the unit boundary fires exactly once)
to "cmdr-662" via SendMessage before ending your turn.**
