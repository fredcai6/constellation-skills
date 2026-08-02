# `a_long` reconciliation fracture — prior-diagnosis note for Phase 3 (#627)

Read-only research note. Written ahead of #627 so the Phase-3 Commander does not
re-walk the #523/#546 dead end. All claims below are cited to file:line or issue.

## 1. The fracture, in one line

Braking capability reads `a_long` from `src/physics/layer2/decoupled_longitudinal.py`'s
1D Kalman-RTS `[E_total, F_vehicle]` filter (via `decoupled_braking_input.py`, WIRED
per `docs/architecture/decisions/decoupled-1d-longitudinal.md:35-41`). Traction,
PowerDrag, and Coast still read `a_long` from the older
`clean_longitudinal_from_raw` (`src/physics/layer2/braking_view.py:85-122`, a
median-filter-based finite-difference of the raw speed sensor). Same physical
quantity, two different numbers, depending on which view asks — confirmed as the
"starkest current basis fracture" in the x7 basis-map audit
(`.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x7-basis-map-RESULT.md:33`).

## 2. Why the decoupled filter failed to generalize to throttle-on/coast (diagnosed root cause)

**Issue #523** (characterization) and its follow-on **#546** (fix-or-hold) measured
the decoupled `a_long` against the incumbent for TractionView, PowerDragView, and
CoastView on 2023-Q RBR at three circuits (Belgium/Monaco/Bahrain), using a
"Config C" parity protocol that pairs the decoupled `a_long` with the incumbent's
raw `v` axis to isolate the `a_long` contribution from a v-source confound. Verdict:
**HONEST-NULL** — all three views HOLD (decision doc lines 102-137, 202-205).

**Throttle/PowerDrag root cause (in physical terms):** the Kalman-RTS filter uses a
LOOSE soft-force coupling (`sig_a_soft_other=30.0`, i.e. the filter defers heavily
to the smooth `[E_total, F_vehicle]` process model rather than the raw force anchor)
outside the braking arc. At throttle-on, this loose coupling lets the energy-channel
integration **diverge from the per-sample finite-difference in a way that depends on
circuit topology**: Belgium (simple, high-speed layout — long straights, few
direction changes) passes Config C parity; Monaco and Bahrain (complex, mixed-speed
profiles — frequent corner/straight transitions) show large, persistent shifts
(TractionView Bahrain: -6.2σ to -9σ across HP sweep; PowerDragView Monaco: -7.4σ to
-13.4σ). `decoupled-1d-longitudinal.md:127-129` states this plainly: "The energy
channel integration diverges from the per-sample FD in ways that are
circuit-topology-dependent... The issue is not tunable without tighter soft-obs for
throttle-on regimes" — and then #546's own HP sweep (below) shows even that isn't
true in a simple sense.

**#546 G1 (throttle HP sweep):** tested a dedicated `sig_a_soft_throttle` HP in
[1.0, 2.0, 3.0, 5.0, 30.0] under Config C parity
(`decoupled-1d-longitudinal.md:139-167`). No value in that range passes the <1σ
acceptance bar on all three circuits simultaneously. Belgium improves monotonically
as the HP tightens (+2.57σ → +0.62σ), but **Bahrain gets WORSE as the HP tightens**
(-9.03σ at HP=1.0 vs -6.19σ at HP=30.0) — the two circuits pull the single scalar HP
in opposite directions. Conclusion recorded verbatim: "The root cause is in the
energy-channel structure (circuit-topology-dependent divergence between Kalman-RTS
and per-sample FD), not in the soft-obs magnitude." This is the key finding for any
future redesign: **it is not an undertuned hyperparameter, it is a structural
mismatch** between how the RTS integrates energy over a mixed-topology arc and what
the raw per-sample sensor reads.

**Coast root cause:** the Kalman-RTS filter produces *positive* `a_long` for
22-28% of coast samples where the raw finite-difference gives negative
(`decoupled-1d-longitudinal.md:129-131`). **#546 G2** tested whether this was a
boundary-initialization lag (`F=0` at segment start) via a post-clamp fix
(`a_long_dec = min(res.a_long, a_long_raw_seg)`). Result: boundary lag accounts for
only 3-11 samples per circuit (0.1-1.0% of the loss); the clamp fix distorts
thousands of interior samples instead, inflating CdA shifts to 2.4-4.5σ
(`decoupled-1d-longitudinal.md:169-196`). The **structural** cause (three
contributing mechanisms, all named in the decision doc):
1. The speed filter (`v > 12 m/s`) already strips most off-mask samples (pit lane,
   slow corners).
2. **Short coast segments (3-15 samples) with LOOSE coupling
   (`sig_a_soft_other=30.0`) cannot converge `F_vehicle` before the RTS smooths it
   out** — only long-segment coast is well-estimated by this filter.
3. The incumbent `prepare_coast_samples` uses full-session-stream smoothing, which
   is stable even for 3-sample blips; the decoupled estimator runs **per-segment**
   (contiguous per-lap arcs, see `decoupled_braking_input.py:117-145`), so it
   structurally cannot match the incumbent's cross-segment stability for short
   events.

## 3. What was tried vs. NOT tried

**Tried (both HONEST-NULL):**
- Config B (confounded v-source) and Config C (parity v-source) characterization
  across 3 circuits × 3 views (#523).
- A dedicated `sig_a_soft_throttle` HP swept over 5 values, Config C parity (#546 G1)
  — installed as a first-class kwarg (`decoupled_longitudinal.py:366`,
  `decoupled_braking_input.py:118,140,144`) but never wired to a passing value.
- A coast boundary-lag post-clamp fix (#546 G2) — rejected, distorts interior
  samples worse than it fixes.

**NOT tried (explicitly named as required-before-re-evaluation in #546's own
acceptance criteria, never executed since #546 closed HONEST-NULL rather than
reopening):**
- A **per-segment-class** (rather than single-scalar) throttle coupling — #546 only
  swept one throttle-wide HP value at a time; it never conditioned the coupling on
  finer regime structure (e.g., corner-radius, curvature, or a continuous
  topology descriptor) that could let Belgium and Bahrain use *different* effective
  couplings within the same "throttle-on" tag.
- Any change to the **process-model structure itself** (the `[E_total, F_vehicle]`
  state and its `Phi`/`Q` in `decoupled_longitudinal.py:241-242`) — only the
  observation-noise HPs were tuned; the constant-force-between-samples process
  assumption that underlies the RTS integration was never revisited for
  complex-topology segments.
- A minimum-segment-length filter for coast (option (b) named in
  `decoupled-1d-longitudinal.md:196` but not executed) or accepting a tighter
  `sig_a_soft_coast` HP (option (a), also named but not executed — #546 G1 swept
  "throttle" HP, not a distinct "coast" HP).

## 4. Would Phase 1's segmentation substrate plausibly unblock this?

**#627's scope item 3** names this fracture and instructs: "read the #523/#546
decoupled-1D failure diagnosis before redesigning." The epic's Phase 1 (from the
confirmed spec,
`.agent-work/archive/2026-07-17-explore-physics-evo-hookup/DESIGN_SPEC.md:57-59`)
upgrades `segment_classifier` from **hard per-sample regime tags** (the current
`straight_brake` / `straight_throttle` / `corner` strings consumed at
`decoupled_longitudinal.py:404-405`) to **soft/fractional property-class
membership over a continuous descriptor substrate**, adds straights as first-class
segments, and adds a lateral-g/radius axis — explicitly framed to serve "the
observability router" (line 60).

**Plausibility assessment:** genuinely plausible but unproven, and #546's own
finding is a real caution against it working trivially. The diagnosed root cause is
that ONE scalar throttle-coupling HP cannot serve both Belgium (simple topology,
wants tight coupling) and Bahrain (complex topology, wants loose coupling) at once
— that is precisely a "one blunt regime tag hides real topology variation" failure
mode, which a continuous segment-class substrate is designed to fix in principle:
it could let the RTS's soft-force coupling (or even the process noise `Q`) vary
*per segment class* rather than per one binary throttle/other split, giving Belgium
and Bahrain effectively different couplings without a global retune. That is a
structurally different lever than anything #546 tested (#546 only varied the
scalar magnitude of a single throttle-wide HP, never conditioned it on topology).

However, `decoupled-1d-longitudinal.md:127-129` frames the divergence as being in
"the energy channel integration" itself — i.e., potentially a mismatch between the
RTS's constant-force-over-arc-length assumption and what happens physically at
corner/straight transitions, not merely "the wrong regime bucket got the wrong HP."
If that framing is right, finer segmentation would let you assign a *better* HP per
class but might not close the gap **within** a class that still spans a
transition-heavy stretch (e.g., Monaco's short straights are mostly transition
zones) — the fix might need the process-model change that was never tried (see
§3), not just better routing of an unchanged filter. So: Phase 1 segmentation is a
plausible enabling substrate for a *smarter* retune attempt, not a guaranteed fix,
and it was never tested against this specific failure.

## 5. Honest fallback

The two-estimator split is a **documented, standing decision**, not an oversight:
`decoupled-1d-longitudinal.md:68-70` states braking uses the decoupled filter while
"throttle and coast regimes remain on `clean_longitudinal_from_raw` (#523
honest-NULL, #546)," and the module docstring (`decoupled_longitudinal.py:68-70`)
carries the same statement in code. The x7 audit
(`x7-basis-map-RESULT.md:33`) is the current honest accounting of the resulting
gap: two different noise models for the same physical quantity, "no attempt to
reconcile/correlate them." Per #627's own gate language, if Phase 3 cannot close
this fracture outright, the acceptable exit is **not** silence but a **quantified
downstream-impact bound** — e.g., persist the measured Config-C σ-shifts
(TractionView/PowerDragView/CoastView shift magnitudes already measured in #523/#546,
reproduced in §2 above) as an explicit reconciliation-error term wherever Traction/
PowerDrag/Coast parameters are consumed downstream, rather than presenting them as
directly comparable to Braking's `a_long`-derived parameters. Cross-view covariance
persistence (fracture 5) is the one fracture #627 marks **non-deferrable**; this
`a_long` fracture (fracture 3) may legitimately defer with that quantified bound.

## Files/issues referenced

- `docs/architecture/decisions/decoupled-1d-longitudinal.md` (decision record, full read)
- `gh issue view 523`, `gh issue view 546` (closed, HONEST-NULL both)
- `src/physics/layer2/decoupled_longitudinal.py` (the filter, `estimate_longitudinal`/`rts_smooth_energy_force`)
- `src/physics/layer2/decoupled_braking_input.py` (the braking-only adapter/wiring)
- `src/physics/layer2/braking_view.py:85-122` (`clean_longitudinal_from_raw`, the incumbent still used by Traction/PowerDrag/Coast)
- `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x7-basis-map-RESULT.md` (row 5 of table (b): the fracture stated as basis-map fact)
- `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/DESIGN_SPEC.md:57-59` (Phase 1 segmentation substrate definition)
- `gh issue view 627` (Phase 3 scope item 3, cites #523/#546 as required reading)
