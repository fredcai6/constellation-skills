# VERDICT — #496/#507 Physics-Aware Filter Rebuild

**Gate:** g4 (assembly + judgment over landed G1–G3 work) ·
**Work id:** 496-physics-aware-estimator · **Branch:** feat/physics-aware-estimator-496 ·
**Date:** 2026-06-24 · **Estimator:** `src/physics/layer2/decoupled_longitudinal.py` (MEASURED-not-wired)

---

## Verdict: **GO** — on the #507 acceptance, for the tested scope

Production-readiness (multi-session/driver, HP calibration, wiring) is explicitly **deferred to #518**.

### One-paragraph justification (grounded in the scoreboard)
The #507 acceptance requires the recovered braking knee to track the raw sensor on BOTH a
hard-braking circuit (Bahrain) AND a short-straight circuit (Monaco), with Monaco non-throttle
ringing brought under the raw ceiling. The decoupled 1D longitudinal estimator
(`[E_total, F_vehicle]` total-energy/force state; M7 raw-onset force anchor + M3 decoupling) clears
**all three acceptance circuits simultaneously**: Bahrain knee `−50.98` vs raw `−52.13` (gap **+1.15**,
down from the baseline gap of +12.7 — the deep ~5 g knee is recovered, not rounded away); Monaco
`ring_ok=True` at roc **−0.09 ≤ 0** (under the raw +5.64 ceiling, vs baselines RINGing at roc
+7.5/+7.7); and Belgium does NOT regress (synthesis `−38.49`, actually **deeper** than the kind3
baseline `−37.41`, gap +0.35 vs +1.43). Every point estimate carries an honest per-sample `sigma_a`
from the same RTS posterior (min ≈ 0.09 real-session), and the single canonical execution path is the
total-energy state with no `[v,a]` shim. The acceptance criterion is met literally and in full on both
required circuit types — that is a GO. It is **GO for the tested scope only** because the run is a
single driver (VER), 3 circuits, 2023 Q, at module-default (not per-session-calibrated) HPs, and the
estimator is MEASURED-not-wired; that scope is the reason production-readiness is deferred to #518, not
claimed here.

---

## 3-circuit acceptance table (re-run this gate, `py scripts/prove_synthesis_496.py`, exit 0)

| Circuit | variant | knee (m/s²) | knee_gap_vs_raw | ringing | roc | ring_ok | raw_knee | acceptance |
|---|---|---|---|---|---|---|---|---|
| Bahrain | gaussian | −39.50 | +12.63 | 0.46 | +3.32 | RING! | −52.13 | — |
| Bahrain | kind3 | −39.42 | +12.71 | 0.41 | +3.28 | RING! | −52.13 | bar to beat |
| **Bahrain** | **synthesis** | **−50.98** | **+1.15** | −2.99 | −0.13 | **OK** | −52.13 | **PASS** (gap ≤ 3.0; deep knee recovered) |
| Monaco | gaussian | −38.07 | −0.56 | 13.14 | +7.50 | RING! | −37.51 | — |
| Monaco | kind3 | −37.60 | −0.09 | 13.38 | +7.73 | RING! | −37.51 | bar to beat |
| **Monaco** | **synthesis** | **−36.88** | **+0.63** | 5.56 | **−0.09** | **OK** | −37.51 | **PASS** (ring_ok; roc ≤ 0; under raw ceiling) |
| Belgium | gaussian | −34.93 | +3.91 | 4.36 | −0.21 | OK | −38.84 | — |
| Belgium | kind3 | −37.41 | +1.43 | 4.44 | −0.13 | OK | −38.84 | control |
| **Belgium** | **synthesis** | **−38.49** | **+0.35** | 4.51 | −0.05 | OK | −38.84 | **PASS** (no regress; deeper than kind3) |

**All three PASS simultaneously.** Acceptance lines emitted by the proof:
- `Bahrain knee_gap=+1.15 (<= 3.0) -> PASS`
- `Monaco ringing_ok=True (roc=-0.09) -> PASS`
- `Belgium knee syn=-38.49 vs kind3=-37.41 (regress=-1.08 <= 0.5) -> PASS`

**Terrain-aware total-energy path** (PE from the #497 z-map, fastest-lap VER) reproduces:
F_vehicle shift on the brake arc 0.339 / 0.738 / 0.702 m/s² (Bahrain/Monaco/Belgium); `sigma_a` min
≈ 0.092–0.097; `altitude_assumed_flat=False` (real z-map used). The a_long scoreboard is **invariant**
to the PE term by construction (the `+m g z` energy correction and the `−g sinθ` output correction
cancel on the round-trip to `a_long`); the terrain payoff lives in the `F_vehicle` channel that #518
will consume, NOT in the a_long acceptance metric. (Re-derived and confirmed by g3-review.)

---

## Honest scope of the claim
The GO is bounded to exactly what was measured:
- **Single driver:** VER only.
- **3 circuits:** Bahrain (hard-braking), Monaco (short-straight ringing), Belgium (control). 2023 Q.
- **Default HPs:** `tv_lambda=0.10`, `sig_a_soft_brake=0.10`, `sig_a_soft_other=30.0`, `sig_a_brake=35.0`
  — swept on these 3 circuits for VER, set as module defaults; **NOT per-session-calibrated**.
- **MEASURED-not-wired:** the estimator is a per-session MEASUREMENT path. Nothing in `src/` imports it
  (grep confirmed 0 importers); it is NOT wired into `braking_view` / capability ceiling / evo.
- **Mass:** `MASS_KG=808.0` pinned (parameter, overridable).

---

## Done-done bar (#509) — confirmed this gate
1. **Full focused suite green:** `py -m pytest tests/unit/physics tests/unit/preprocessing -q` →
   **627 passed, 6 skipped** in 820.52s (exit 0). The 6 skips are pre-existing conditional skips, not
   failures.
2. **Honest covariance (first-class):** every `a_long` sample carries `sigma_a = √(P_s[1,1])/m` from the
   same smoothed RTS posterior; the result dataclass never exposes `a_long` without `sigma_a`. Verified
   > 0 everywhere (min ≈ 0.09 real-session) by g3-implement L2 + g3-review independent re-derivation.
3. **Single canonical execution path:** one estimator in `[E_total, F_vehicle]` coordinates; **no
   `[v,a]` shim**; the 2D `StintSmoother` (`src/preprocessing/trajectory/smoother.py`) and
   `clean_longitudinal_from_raw` (`src/physics/layer2/braking_view.py`) are **untouched** (git status
   clean — only `.agent-work/` untracked; grep confirms no second longitudinal estimator).
4. **Traceable data→scoreboard:** `py scripts/prove_synthesis_496.py` → **exit 0**, the 3-circuit table
   reproduces identically, and the dashboard `reports/physics/synthesis_proof_2023Q.{json,png}`
   regenerates from the committed code.

---

## What the run did NOT do (and where it is tracked)
| Not done | Tracked at |
|---|---|
| Production wiring (estimator → `braking_view` / capability ceiling / evo) | **#518** (C1 ceiling re-eval / consumer) |
| Multi-session / multi-driver HP re-calibration before wiring | **#518** |
| `clean_longitudinal_from_raw` retire (decision deferred — see below) | **#518** side-by-side BrakingView fit |
| Gravity-corrected `F_vehicle` frontier metric (the PE payoff the a_long metric is blind to) | **#518** (new metric) — triage **tc2** |
| Terrain handle on the `CaseInputs` scoreboard seam (so the scoreboard can grade `F_vehicle`) | **#518** wiring — triage **tc1** |
| Predictive output (per-session measurement only — out of scope per PROBLEM_STATEMENT) | super-epic #509 P-phase |

---

## `clean_longitudinal_from_raw` retire-assessment — **do NOT retire here**
Per the #507 acceptance order ("THEN re-evaluate retiring `clean_longitudinal_from_raw`"), this is the
re-eval, and the conclusion is **do not retire in this gate; carry to #518 as a side-by-side**.

**Deciding numbers / facts (carried from g3-implement):**
- The synthesis is a STRONGER capability input: it recovers the deep knee (Bahrain −50.98 vs the
  −52.13 raw target it would replace, gap +1.15), carries HONEST per-sample `sigma_a` (vs
  `clean_longitudinal_from_raw`'s single scalar `sigma_decel`), and already exposes the gravity-free
  `F_vehicle` channel (making the `g sinθ` de-conflation BrakingView re-does downstream redundant if
  `F_vehicle` were consumed directly). It does NOT ring (roc ≤ 0 on all three).
- BUT retiring is **not free**: the scoreboard's raw reference is itself built from
  `clean_longitudinal_from_raw`, and the synthesis sits ~1.1 m/s² shallower than that raw peak
  (irreducible 1D-filter resistance at the single onset sample). #518 must decide whether to anchor
  BrakingView on `F_vehicle` (skipping the redundant gravity de-conflation) or keep
  `clean_longitudinal_from_raw` for the raw-reference role.
- The real consumer is the **C1 ceiling under-call (#518)**; the retire belongs there, with a
  side-by-side BrakingView frontier fit on synthesis-`a_long` vs `clean_longitudinal_from_raw`-`a_long`
  comparing `(a_b, b_b)` + covariance + utilisation.

**Conclusion:** synthesis is the FAVOURED input; the retire is a **#518 decision** with the deciding
numbers in hand. Not retired this gate.

---

## Durable decision candidates (need Cartographer/user authority to ratify)
1. **Decoupled-1D-longitudinal:** "longitudinal `a_long` comes from a decoupled 1D physics filter fed by
   the raw-onset force anchor, not the 2D position smoother." Consistent with
   `decision:smoother_rounds_braking_knee` (the 2D position-smoothness prior is the wrong tool for the
   longitudinal transient; speed/energy is the only good longitudinal observable). The
   `decision:two_cycle_external_anchor_design` invariant is honored and consciously EXTENDED to the
   1D-filter context (anchor = TV-denoised RAW `a_long`, gravity-corrected via the external #497 z-map,
   never re-read from a smoothed trajectory; placement extended from plateau-only to the full braking
   arc incl. the onset sample — the capability sample).
2. **Total-energy / vehicle-force frame:** "the decoupled longitudinal filter works in TOTAL system
   energy (KE + gravitational PE from the #497 z-map); `d(E_total)/ds = F_vehicle`, the gravity-free
   vehicle force, fed by the gravity-corrected raw-onset force anchor." Physically sounder (force is the
   friction-circle-bounded quantity; the brake-onset knee is a benign slope-change/kink, not a sharp
   `v(t)` second-derivative spike). **Caveat:** the a_long scoreboard cannot reward the PE term
   (invariant by construction); the PE payoff is in `F_vehicle`, which #518 must validate against a
   gravity-corrected braking frontier.

These were surfaced (not self-authorized) by the implementer as mid-build coordinator reframes falling
inside the documented "module internals / composition" authority; g3-review confirmed the handling.

Also governing the rebuild's structure (from PROBLEM_STATEMENT, surface at reconcile):
**"Evolutionary-not-revolutionary"** — extend the existing Matérn + kind=3 + raw-speed machinery;
full process-model replacements (M2/M6) were rejected.

---

## Set-aside remainder (routes to Triage)
Nothing below blocks the GO; all are deferred and tracked.

**#518 (C1 ceiling re-eval / consumer) — the primary follow-on:**
- C1 #510 re-eval (the braking + fast-corner driver-utilization NO-GO that gated on #496 — `U` clips at 2.0).
- Production wiring of the estimator into `braking_view` / capability ceiling / evo.
- `clean_longitudinal_from_raw` retire side-by-side (BrakingView fit on both inputs).
- Multi-session / multi-driver HP calibration before wiring.
- The gravity-corrected `F_vehicle` braking-frontier metric (the PE payoff the a_long metric is blind to)
  — engine triage **tc2** (a_long scoreboard structurally blind to the PE term).
- Terrain handle on the `CaseInputs` scoreboard seam so the scoreboard can grade `F_vehicle`
  — engine triage **tc1** (`variant_synthesis` currently runs FLAT on the scoreboard seam).

**Pre-existing / adjacent (out of this run, list so nothing is silent):**
- `validate_refine_505.py` cleanup (#504 territory — the eval harness the scoreboard descends from).
- **M8 ≥10 Hz revival** — the semi-parametric onset mean function is conceptually sound but
  under-determined on ~3 GPS samples/event at 4 Hz; needs ≥10 Hz car telemetry (a different data path,
  a separate future evolutionary step, NOT this scope).
- Open map flag (note only): trajectory consumption bypasses the artifact boundary (`session_fit.py` is
  a 2nd FastF1 entry point) — flagged in PROBLEM_STATEMENT, untouched here.

(Engine triage candidates tc1–tc2 are the two the g3-review flagged; the g3-implement result also notes
the same two plus the C1/retire seam. Listed here so Triage inherits the full set.)

---

## Stop conditions
None hit. The suite and proof both reproduce green; the evidence supports an honest GO on the #507
acceptance for the tested scope. No scope/authority breach: this gate did NOT modify `src/`, did NOT
wire anything, and did NOT retire `clean_longitudinal_from_raw`.
