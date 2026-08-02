# Review Result — #518 G2 side-by-side braking frontier + decoupled adapter

verdict: APPROVE

(APPROVE = the side-by-side is methodologically sound and the numbers are trustworthy.
It does NOT mean "retire". The retire/wire decision is the human's; my independent
KEEP-vs-ADOPT read is in the KEY JUDGMENT section below.)

## Assigned Gate
`g2 — Side-by-side braking frontier (synthesis F_vehicle vs incumbent raw-speed) + the
decoupled-estimator adapter. Measurement only — no production wiring.`

## Result
`APPROVE`

All 11 survey checks recorded `pass`; 0 blockers; 1 triage candidate (the b_b-pinned re-run).
Verification was run inline (not trusted from pasted output).

## Handoff compliance
Pass. The handoff asked for a per-lap decoupled adapter (terrain-aware, σ-carrying, aligned
to classified samples) + a 6-circuit × VER+PER side-by-side producing the deciding (a_b, b_b)
+ cov + ceiling numbers and a retire/keep recommendation, MEASUREMENT ONLY. All delivered:
`decoupled_braking_input.py`, `altitude_at_positions`, `braking_sidebyside_518.py` + report,
13 synthetic tests, and a KEEP-for-now recommendation. Nothing exceeds the assigned scope.

## Scope drift
Pass. `git diff HEAD` touches exactly one production file — `src/physics/terrain.py` — and
only appends `altitude_at_positions` (hunk `@@ -410,3 +410,28 @@`, the function lands at
L415; it mirrors the existing `gradient_at_positions`/`banking_at_positions` helpers). Every
other file is untracked-new. I read the source of each named exclusion and confirmed all are
UNMODIFIED: `prepare_braking_frontier`, `BrakingView.fit`, `clean_longitudinal_from_raw`,
`session_braking._driver_samples`, `session_estimator`, `EstimateStore`, `car_prior`. The
adapter only *calls* the production loaders; it changes none of them.

## Evidence verdict
Pass. Test mode was `test-after` (pure-logic unit tests + a script/report); appropriate for a
measurement seam. Inline re-runs:
- `py -m pytest tests/unit/physics/layer2/ -q` → **197 passed in 89.64s** (matches the
  implementer's 197; includes the 10 adapter + 3 terrain tests).
- `py -m src.utils.simplification_limits --paths <5 touched>` → **EXIT 0**. The lone printed
  violation is `terrain.py build_terrain_profile function_lines=105`, which I confirmed is
  PRE-EXISTING (the function sits at L21, entirely outside the diff hunk at L410+). `--baseline`
  also EXIT 0 (6 pre-existing repo-wide file-line violations, none in the touched files).
- Report `reports/physics/braking_sidebyside_2023Q.md` present; its numbers reproduce the
  implement-result table exactly. (Did NOT re-run the ~10-min sweep, per the handoff.)

The two load-bearing guard tests genuinely encode the gravity invariant:
`test_double_count_trap_diverges` feeds `F_vehicle/m` with the REAL θ on a 6° grade and asserts
`a_b` shifts > 0.5 m/s² vs the correct path; `test_variantA_and_variantB_deconflate_equally`
asserts A and B land within 1.5 m/s² of the same `a_b` on a synthetic downhill braking lap.

## Code/doc quality
Pass. Inherited rules met: `py` not `python` (no bare `python` in touched files);
`physics_region_no_evo_import` honored (no evo/latent_power/compound_prior imports — the only
match is the docstring constraint declaration); honest per-sample σ carried 1:1 and asserted
non-constant (`test_sigma_is_per_sample_not_broadcast`) — strictly MORE honest than incumbent B,
which `np.full`-broadcasts a scalar `sig_decel`; inputs validated with named ValueErrors
(`split_samples_by_lap` length mismatch, `estimate_longitudinal` lengths + `mass_kg>0`,
`_resolve_terrain` θ-xor-z); utilities reused rather than duplicated (`_driver_samples`,
`_to_kinematic_samples`, `_DECEL_CEILING`, `build_terrain_profile`). Truth-anchored physics
tests present (L1 step recovery, gravity double-count guard).

## Map impact verdict
- **Evidence supports claimed change:** Yes. The side-by-side `(a_b, b_b)` + cov + ceiling on
  6 circuits × 2 cars, and the gravity-once F_vehicle metric, are produced and reproduce.
- **Constraints not violated:** Yes. `decision:two_cycle_external_anchor_design` honored (anchor
  is the TV-denoised RAW `a_long` from `clean_longitudinal_from_raw`, never a smoothed
  trajectory — verified at `decoupled_braking_input.py:127` → `decoupled_longitudinal.py:401,406`);
  `constraint:physics_region_no_evo_import` honored.
- **Notes match the diff:** Yes. The new `struct:physics.layer2` symbols
  (`build_decoupled_braking_input`, `estimate_driver_braking`, `estimate_lap_longitudinal`,
  `split_samples_by_lap`, `DecoupledBrakingInput`) all exist as named; `altitude_at_positions`
  matches the terrain.py diff. Both additive; no edge into production views.
- **Decision candidates surfaced:** Yes, correctly. `decision:decoupled_1d_longitudinal` (G3
  wiring) and `decision:smoother_rounds_braking_knee` (retire caveat) are surfaced for the human,
  not decided here — correct for a measurement-only gate.
- **Durable context routed:** Yes. Triage candidates (b_b-pinned re-run, `build_terrain_profile`
  decomposition, Singapore identifiability) are flagged, not dropped.

## Reconciliation check
No reconciliation needed beyond the surfaced retire/keep decision. The change is purely additive
measurement; no contract, schema, or structural baseline is altered. `build_terrain_profile`'s
pre-existing 105-line over-limit is repo debt, not introduced here.

---

## THE KEY JUDGMENT — independent KEEP-vs-ADOPT read

**My recommendation: (b) do an explicit b_b-PINNED A-vs-B re-compare in G2 before deciding —
and I LEAN ADOPT-A. The cold-start ceiling@80 divergence should NOT, by itself, keep B.**

I diverge from the implementer's stated *rationale* (though not entirely from "don't retire
yet"). The implementer attributes B's larger b_b to B's local-gradient θ pushing high-speed
decline into b_b on hilly circuits. The data does not support that:

**1. B's larger b_b is NOT "more correct," and the terrain explanation fails quantitatively.**
I computed `corr(θ_brake_min, b_b excess B−A) = −0.22` — weak, and the wrong shape for a
terrain story. The two HILLIEST circuits (Monaco −4.61°, Belgium −4.31°) have the SMALLEST b_b
excess (4.5e−4, 7.8e−4). The LARGEST b_b divergence is at **Monza** (+1.53e−3) and **Singapore**
(−2.71e−3, reversed) — both **near-FLAT** brake zones (θ ≈ −0.8 to −0.9°). If terrain handling
drove the gap, the hilly circuits would dominate it; they don't. So the b_b divergence is a
**fit-identifiability** phenomenon, not a terrain-handling artifact in either direction.

**2. The ceiling@80 is an extrapolation off a weakly-identified a_b↔b_b ridge — the least
trustworthy number in the table.** `ceiling@80 = a_b + b_b·6400`, so it amplifies the curvature
term 6400×. Where the (a_b, b_b) split is poorly conditioned, the ceiling just reads out wherever
the fit slid along the ridge. The diagnostics make this explicit at the two circuits driving the
verdict:
- **Monza:** B's `a_b σ = 6.76` (A: 1.58) and B's a_b↔b_b covariance off-diagonal `= −8.4e−3`
  (A: −3.7e−4, ~20× tighter). B trades a low a_b (32.73) for a high b_b (1.73e−3); the σ confirms
  it cannot separate them. B's "ceiling win" (+5.25) is B sliding UP the ridge, not measuring
  more braking capability. A's fit is far better conditioned.
- **Singapore (the inversion):** A's off-diagonal `= −1.6e−2` (the loosest in the set), so HERE
  it is A that is weakly identified and slides up the ridge (b_b 3.31e−3, a_b 24.10±7.81). This
  is the same pathology pointing the other way — not a directional truth about either method.

The pattern is consistent: **the floor (a_b) is the well-identified quantity, the curvature (b_b)
is the weakly-identified one, and ceiling@80 inherits the curvature's instability.**

**3. b_b-pinning is exactly what production does, and both variants here ran UNPINNED.** From
`session_estimator.estimate_session`: PowerDragView measures CdA, which is then fed into
`fit_braking(cda)` (`session_estimator.py:122`). The measured CdA pins the `drag` de-conflation
term in `BrakingView.fit` (`drag = cda_closed.mu·ρ·v²/(2m)`, `braking_view.py:163`) — i.e. b_b is
pinned INDIRECTLY by removing the v²-shaped drag contaminant that otherwise competes with b_b·v².
The cold reference path uses a wide CdA prior `ParamPrior(1.2, 0.6)` + `GaussianPrior2.cold()`.
The side-by-side used precisely that **cold CdA + cold (a_b,b_b) prior** for BOTH variants. So the
comparison is between two **cold, unpinned, weakly-identified curvature extrapolations** — the
regime production is built to replace. Rejecting A on that basis rejects it on the least reliable
number, measured outside the conditions it will run in.

**What A clearly wins (the well-identified half):** a_b deeper on 5/6 (all but Singapore), tighter
a_b σ on 4/6 (Monza 1.58 vs 6.76 is the standout), and a strictly-honest per-sample σ vs B's
scalar broadcast. That is a real floor + calibration + conditioning upgrade.

**Bottom line for the human:** The implementer's KEEP is defensible ONLY in the narrow sense of
"don't retire before the decisive measurement exists." It is NOT supported as "B's ceiling is
more correct." The decisive measurement is the b_b-pinned ceiling@80 (pin the PowerDrag-measured
CdA so both variants share the drag/downforce term, then re-compare). My expectation, given (1)–(3):
pinning will tighten both curvatures and collapse most of the ceiling gap toward the well-identified
a_b — where A wins. So: do the b_b-pinned re-compare (option b); if A's pinned ceiling matches or
beats B on ≥4/6, ADOPT A; if a pinned, well-conditioned B ceiling still genuinely exceeds A's, that
would be the first real evidence to keep B. I would NOT retire on the cold numbers, and I would NOT
keep B on them either.

## Blockers
- None.

## Out-of-scope observations
- **The decisive next measurement is the b_b-pinned A-vs-B re-run** (flagged as triage candidate
  `tc1`). Both the implementer and I converge that the cold-start ceiling@80 should not gate the
  retire decision; the pinned ceiling should. This is the single most useful follow-on for G3.
- **`terrain.py::build_terrain_profile` is pre-existing simplification debt** (105 lines, limit
  <100). Non-gating (canonical run EXIT 0), not introduced here; a decomposition candidate if
  terrain.py is next touched.
- **Singapore frontier identifiability:** A's a_b↔b_b covariance off-diagonal (−1.6e−2) flags a
  weakly-identified curvature there; worth a per-circuit bandwidth-sensitivity check if Singapore
  ever becomes load-bearing for a decision.

## Workflow Feedback
- **Handoff gaps:** The handoff did not name the capability-ceiling metric (`v_ref`, or the house
  `a_brake @ 30/60/90` convention). The implementer chose `a_brake(80)` and documented it, which
  is fine for a *relative* comparison — but since the whole KEEP debate hinges on the ceiling, a
  one-line "report ceiling as `a_brake@<v>` AND report a_b separately" in the Close Criteria would
  have pinned the metric the judgment turns on. (The implementer raised the same gap.)
- **Context rediscovered:** I had to read `session_estimator.py` to confirm HOW production pins
  b_b (indirectly, via the PowerDrag CdA into the drag term — NOT a direct b_b prior). The handoff's
  question 2 says "production pins b_b" but the *mechanism* (CdA→drag term) is what makes the
  cold-vs-pinned argument precise; naming it in the handoff would have saved the dig and sharpened
  the implementer's own rationale.
- **Instructions improvised around:** None of consequence. The reviewer survey template + engine
  covered the work cleanly; I appended r6–r10 for the gate-specific checks per the skill's
  "append one check per inherited rule / context warrant" instruction, which fit naturally.
- **What would have made this easier:** (1) Name the ceiling metric in Close Criteria. (2) Spell
  the b_b-pinning mechanism (CdA→drag de-conflation term) in the KEY JUDGMENT section so the
  reviewer and implementer reason from the same model. Both are 1-line additions.

## Return status
`complete`
