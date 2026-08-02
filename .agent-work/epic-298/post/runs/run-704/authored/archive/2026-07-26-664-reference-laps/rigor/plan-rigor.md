# Plan rigor — #664 (design-it-twice + cold plan critic)

Both mechanisms run as read-only Plan subagents (no Write tool → persisted here by cmdr-664).

## Design-it-twice — class-attribution grain (G1 core)
**Decision: Candidate B, the membership-faithful hybrid.** A single `(n, 2+k)` class-weight
matrix `W = hstack([seg_type one-hot (STRAIGHT, BRAKING_ZONE), severity_membership])`; every
class reduction is `Wᵀ · (segment quantity)`. Hard exactly where the SegmentMap is hard
(seg_type), soft exactly where it is soft (k corner-severity columns).
- Exact-summing is STRUCTURAL: `posterior_membership` rows sum to 1 (protocols.py:44-45) and
  severity_membership is exactly 0.0 on non-corner rows (runtime.py:173-177).
- Extends the already-blessed #625 `regime_rollup` fractional-attribution pattern, moved
  distance→time and extended with deficits.
- **Decisive reason:** the GATING jackknife measures per-class deficit stability under
  boundary jitter. Argmax (Candidate A) flips whole segments between severity classes →
  variance dominated by quantization noise → gate measures the wrong thing. B moves a smooth
  fraction → gate is meaningful. A survives only as a FREE diagnostic argmax-view over W
  (B→A reversible; A→B not). @grade for this decision: settled/measured.
- Guard: assert each W row sums to 1 before reducing (construction invariant).

## Cold plan critic — findings + cmdr-664 triage
- **F1 SERIOUS (jackknife leverage/self-weighting)** → ADOPT (partial). The gate perturbs
  SegmentMap BOUNDARIES (boundary jitter), and the deficit per point is fixed; the jackknife
  tests attribution stability, not ceiling contamination — so F1b (scored driver's laps in the
  FIELD reference pool) is attenuated (the scoring ceiling is the strictly_pre car prior, NOT
  the field reference lap; the field lap only places boundaries). But F1a (leverage) is valid:
  drop-one over a ~200-lap pool barely moves boundaries. FIX in g4: use a DELETE-d / BLOCK
  jackknife (drop a driver or a lap-block) with a stated replicate budget, and state explicitly
  that boundary-jitter is the perturbation and the scoring ceiling excludes the target round.
- **F2 SERIOUS (no positive control)** → ADOPT. g4 must run a POSITIVE CONTROL (inject a
  known misattributed deficit, confirm the robustness statistic flags it) before any null is
  accepted — mirrors mixture_stability's "deliberately built so it CAN fail." A null is
  "complete" only if the positive control fired.
- **F3 SERIOUS (acceptance band is an unfrozen threshold → F12 forces a float, not a literal)**
  → ADOPT via REFRAME. Per the launch order the attribution-robustness check is an INSTRUMENT,
  not a hard gate ("2σ is a reference not a gate," allocation-not-gating). So g4 REPORTS
  stability numbers; any comparison is anchored to EXISTING frozen constants (the boundary-drift
  scale `MAP_STABILITY_DRIFT_M`=10 m governs the jitter magnitude) — NO new literal band. If a
  hard pass/fail band is ever truly needed it is a FLOAT to the Admiral (new named F12 set),
  never an inline literal.
- **F4 MODERATE (O(N) re-derivation cost)** → ADOPT (folds into F1's delete-d budget B≈20-50);
  budget the op-count against the <10 min bound in the handoff.
- **F5 MODERATE (g4-integrate `test -f` + `&&`)** → ADOPT (simplify). Engine command
  postconditions run under a POSIX shell so `&&`/`test` would actually work, but it is cleaner
  to drop it: g4-integrate c1 becomes pytest-only; artifact existence is asserted INSIDE the
  smoke test and re-confirmed by the g4 reviewer from the persisted artifact.
- **F6 MODERATE (energy built before the finding; ungated)** → ADOPT. g3 does the
  single-vs-dual elevation-convention FINDING first; energy is explicitly scoped
  DESCRIPTIVE / instrument-this-run (its §7 comparison is downstream), not gated by the
  jackknife.
- **F7 MODERATE (pre-g4 tests are construction invariants; falsifier self-graded)** → ADOPT.
  g4 REVIEWER independently RECOMPUTES the robustness statistic from the persisted artifact and
  checks the positive control fired — not a code read-through.
- **F8 MINOR (dormant escalation columns vs lowest-dimensionality)** → KEEP with noted
  exception: the launch order explicitly rules "escalation layers dormant in schemas from day
  one," which overrides the YAGNI tension. Documented as a deliberate order-blessed exception.
- **F9 MINOR (g1-review no-normality criterion vacuous)** → ADOPT. Remove no-normality from
  g1-review (g1 chooses no form); keep it in g3-review.
- **F10 MINOR (field-reference fingerprint couples to field composition)** → ADOPT. Persist a
  field-basis descriptor alongside the fingerprint; document it as field-conditioned, not
  pure-circuit.

## Panel-vs-single choice (surfaced)
Ran ONE cold critic (3 lenses folded) + ONE design-it-twice pair, NOT a full 3-agent panel.
Rationale: the launch order is highly prescriptive (store shape pre-frozen, "design-it-twice
skipped (precedented shape)"), so the open surface is narrow (one interface + the validation
methodology). Single-critic proportionate. Store-shape design-it-twice = named UNTAKEN ROAD
(order-frozen). This is the surfaced choice; cited to LAUNCH_ORDER at plan approval.
