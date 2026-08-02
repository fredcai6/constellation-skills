# Wave 2 verdict — issue #625 (Stage-1 Phase 1 segmentation substrate)

**FINAL.**

Commander: ShipC-625 (delegated, `constellation-commander-delegated`). Worktree:
`C:/Programs/f1-625`, branch `feat/625-segmentation-substrate`, base `main` `8a23b42c`. Spine
driven to terminal `archive` through the checklist engine (`checklist_engine.py`); journal at
`.agent-work/625-segmentation-substrate/spine.json` and `execute.json` (archived after this
verdict finalizes). **PR #640**: https://github.com/fredcai6/f1Brainz/pull/640 (base `main`,
commit `bbc5a006`, 23 files changed). Not merged — Admiral's call.

**Admiral disposition (2026-07-18, logged in team messaging):** the F12 FAIL is accepted as an
honest, provisional Phase-1 deliverable, not a defect. Owner has chosen to REWORK Phase 1
(circuit-conditional mixtures / regularized-narrower-k) as a **follow-on wave**, tracked as
**issue #638**. This wave's job was to finalize and ship the honest current state — done below.

## 1. VERDICT

**FALSIFIED.** The substrate and rollup were both built to spec (all 4 gates
implemented + independently reviewed APPROVE), but the **mandatory F12 falsifiable gate
(Gate 3) FAILED on real data** — the held-out-circuit class-membership stability check found
the property-class mixture's class count (`k`) is unstable across circuit-composition splits.
Per the launch order's Honest-Null Clause, this is a complete, valuable, reportable finding,
not a blocker to shipping the built artifacts — but it means the substrate should be treated
as **provisional, not validated**, before Phase 2/4 load-bear on it.

## 2. The substrate

Soft/fractional corner property-class membership: `src/physics/layer2/property_mixture.py`
(`fit_property_mixture`, `posterior_membership`, `MixtureFit`) — a BIC-selected
`sklearn.mixture.GaussianMixture` over STANDARDIZED `(radius, lateral_g)` descriptors, with a
pre-registered support floor (`MIN_COMPONENT_WEIGHT_FRAC = 0.05`, no component may hold less
than 5% of pooled weight) chosen before any real-data fit — support-driven class count per
pre-ruling #1. Rejected candidate `k`s fall back to `k=1` (never a raise, never a silently
accepted below-floor split). An additive `SegmentClassifier.soft_class_membership` method
(new, `_classify_regime`/`_VALID_REGIMES` byte-identical) lets a live per-session classifier
attach corner membership vectors post-hoc without changing the existing hard-tag pipeline.

Corners-as-mixtures is represented literally as a posterior probability vector over `k`
fitted Gaussian components in standardized descriptor space — never a single hard label.

Straights are first-class segments via a generalized `arcs.py`: `_contiguous_runs` now takes
a `regimes: set[str]` parameter (was hardcoded to the brake regime); `identify_braking_arcs`
keeps its exact public signature (verified byte-identical); new `StraightArc`/
`identify_straight_arcs` groups contiguous non-corner runs into `(length_m, duration_s,
top_speed_ms)` records, the reusable pattern Phase 2/4 or a future live-session run can call.

Lateral-g/radius axis: `src/physics/layer2/corner_descriptors.py` derives
`radius_m = v_mean**2 / (mu_lat_p90 * GRAVITY_MS2)` and `lateral_g = mu_lat_p90` from
`grip_bin_obs` rows (already g-units per that table's own docstring — verified from source,
not assumed) — per pre-ruling #2, built from `grip_bin_obs`, not the excluded corner-fingerprint
CSVs.

## 3. The rollup

`.agent-work/625-segmentation-substrate/artifacts/regime_time_share.csv` (+ sibling
`.meta.json`), built by `scripts/build_regime_rollup.py` against the real
`data/damage_integrals.db` (`grip_bin_obs`, 612,615 rows, 22 circuits, 2019-2026). One mixture
fit (`k=3`) pooled across the full dataset defines the shared class vocabulary every circuit's
sub-shares are expressed in. Fields are named `corner_distance_share`/
`straight_distance_share`/`corner_class_N_distance_share` — **deliberately not `time_share`**
anywhere in code or output (only the deliverable's filename carries that word, per the
mission's own naming) — because `grip_bin_obs` is corner-gated-only (no straight-line rows
exist in the source table by construction), so bin-occupancy-fraction is an honest **arc-length
distance proxy**, not literal lap time; it systematically UNDERSTATES true time-share for
corners (cars are slower there, so more real time is spent per unit distance than distance-share
implies). This caveat is stated in the module docstring and is independently AST-verified
(a dedicated test greps the module source for the literal string `time_share`).

**Sanity read:** Monza (`gp_name="Italy"`) `corner_distance_share = 0.5186` **<** Monaco
`corner_distance_share = 0.8314` — the expected low-downforce-vs-street-circuit ordering holds
on the real store. Independently reproduced twice by two different agents (commander +
reviewer), byte-identical on the current committed code.

**The rollup's own output visibly carries the F12 FAIL verdict** — the CSV's leading `#`
comment lines state the verdict, `n_pass`, and a plain-English caveat directly, so a reader
opening only the CSV (not the separate `.meta.json` or `f12_holdout_stability.json`) still
sees it (critic finding #6, independently verified by the Gate 4 reviewer).

## 4. The falsifiable gate (F12) — the load-bearing result of this wave

**Check used:** held-out-circuit class-membership stability (not the independent-proxy
alternative — `circuits.yaml`'s `downforce` field is explicitly low-trust/provisional per
owner note, ruled out as begging the question). 5 independent seeded (base seed 42, +0..+4)
50/50 splits of the 22 circuit NAMES (not rows) into two non-overlapping halves; `fit_property_
mixture` run independently on each half's pooled descriptors; component means Hungarian-matched
(`scipy.optimize.linear_sum_assignment`) after inverse-transforming back to raw physical units
(radius meters, lateral-g); statistic = mean matched-component distance in a combined
normalized space (`RADIUS_SCALE_M=50.0` m, `LATERAL_G_SCALE=0.5` g,
`F12_AGREEMENT_THRESHOLD=1.0`, all three pre-registered before the real-data run — confirmed
by file-mtime ordering at review, `mixture_stability.py` last written strictly before either
real-data run). A `k`-mismatch between a split's two halves is a pre-declared automatic FAIL
for that split (`float("inf")`), not an error — itself instability evidence.

**Discriminating test (mandatory, per pre-ruling #4):** two synthetic scenarios independently
verified genuine by two reviewers — same-generator circuits assert PASS, deliberately-shifted-
generator circuits assert FAIL — proving the check can actually distinguish stable from
unstable, not merely execute.

**Real-data result: FAIL. `n_pass = 0/5`.** Every one of the 5 seeded splits produced a
DIFFERENT `k` between its two halves (4v6, 6v2, 4v6, 5v3, 3v4) — the mixture never even agreed
on the NUMBER of property classes across circuit-composition splits, let alone their
locations; every split hit the automatic k-mismatch FAIL before the distance-threshold
comparison was ever reached. Independently reproduced by the commander (once, 5m49s) and the
Gate 3 reviewer (once more), byte-identical verdict, per-split `k_a`/`k_b`, and circuit
membership both times — confirms determinism, rules out a flaky/non-reproducible bug.

**Reading:** this is a clean, unambiguous instability finding, not a borderline
near-threshold result. The mixture's class-count selection (BIC over `k_range=(2,6)` with the
5% support floor) is sensitive to which ~11 circuits are in the ~300k-row fit pool — plausibly
because different circuit mixes carry genuinely different corner-radius/lateral-g
distributions (street circuits vs. high-speed circuits), or because BIC selection itself is
under-regularized at this scale, or because a single global mixture is the wrong model
(circuit-conditional classes might be needed instead of one shared vocabulary). This wave's
scope was to build and honestly run the check, not diagnose or fix the instability — routed to
triage/Admiral below.

## 5. Observability-router output (round-1 load-bearing consumer)

`src/physics/layer2/observability_router.py`: `ROUTER_ENTRIES` maps the four regime tags to
the `layer2/*_view.py` view(s) each evidences, EVERY entry grounded in a real, independently
verified `file:line` citation (not just a resolvable symbol name):
- `"corner"` → `lateral_view.LateralView` (`session_lateral.py:61`) and
  `traction_view.TractionView`/`power_drag_view.PowerDragView` (`session_traction.py:24`,
  `_TRACTION_REGIMES = ("straight_throttle", "corner")`).
- `"straight_throttle"` → `traction_view.TractionView`/`power_drag_view.PowerDragView` (same
  citation).
- `"straight_brake"` → `braking_view.BrakingView` (`arcs.py`'s `_BRAKE_REGIME` →
  `decoupled_braking_input.py:183`, `brake = regime == _BRAKE_REGIME`).
- `"straight_coast"` → `coast_view.CoastView` — cited HONESTLY as an INDIRECT linkage:
  `session_coast.py`'s `prepare_coast_samples` does not filter on `SegmentClassifier`'s
  `regime` field at all, it derives its own coast mask from raw throttle/brake/speed
  thresholds — the router entry states this explicitly rather than fabricating a
  `regime == "straight_coast"` filter that does not exist. A dedicated test confirms the
  entry does not claim a direct filter it doesn't have.

Every citation independently re-verified by both the commander and two reviewers by reading
the exact cited line.

## 6. Isolation evidence

```
$ git worktree list
C:/Programs/f1Brainz 8a23b42c [main]
C:/Programs/f1-625   8a23b42c [feat/625-segmentation-substrate]

$ py -c "import src.physics.segment_classifier as s; print(s.__file__)"
C:\Programs\f1-625\src\physics\segment_classifier.py
```
Re-confirmed via `.pth` file-path checks before every gate's test run, by the commander and
every implementer/reviewer independently.

## 7. Tests run + result

- Gate 1: `tests/unit/physics/layer2/test_arcs.py` + `test_corner_descriptors.py` — 16/16 pass.
- Gate 2: `tests/unit/physics/layer2/test_property_mixture.py` + `tests/unit/physics/test_segment_classifier.py` — 15/15 pass.
- Gate 3: `tests/unit/physics/layer2/test_mixture_stability.py` — 8/8 pass (including the mandatory discriminating test); real-data script run — FAIL (see §4).
- Gate 4: `tests/unit/physics/layer2/test_regime_rollup.py` + `test_observability_router.py` — 30/30 pass; real-store rollup run — Monza < Monaco holds.
- **Full-suite regression (`py -m pytest tests/unit/physics -q`)** — did NOT complete: reaped
  by the harness TWICE at ~90 min runtime (once as a manual background copy, once as the
  engine's own authoritative `advance g4-integrate` invocation), both times with **zero
  failures observed** up to the point of being killed (one run reached ~90% complete, clean).
  Floated to the reachable Admiral (team-lead), who explicitly authorized a fallback:
  substituted a **targeted regression subset** — grep of the real import graph of the two
  changed EXISTING files (`arcs.py`, `segment_classifier.py`) found exactly 7 test files
  actually importing them (`test_apex_extract.py`, `test_drag_source_throttle.py`,
  `test_numerical_stability.py`, `test_regulation_era.py`, `tests/property/
  test_physics_properties.py`, `tests/integration/test_preprocessor_physics_interface.py`,
  `tests/unit/preprocessing/trajectory/test_physics_adapter.py`) — **170/170 pass** (21 min).
  Combined with the reaped partial run's clean 90% coverage (which includes
  `test_segment_classifier.py` itself, unmodified-regime-tag tests included), this is
  overwhelming convergent evidence of no regression. The original `g4-integrate.c3`
  postcondition was **waived through the engine** with the Admiral's authority explicitly
  cited (`waive g4-integrate --cond c3 --authority "Admiral (team-lead, this session,
  2026-07-18)"`, full reasoning in the waiver's recorded evidence) — not silently skipped.
- `constraint:physics_region_no_evo_import` grep across all 5 new physics.layer2 files — zero matches, clean.

Every gate independently reproduced by the commander (not just trusted from crew transcripts)
per the global "verify claimed side-effects against the world" doctrine.

## 8. Triage candidates filed / deferred

- **tc1**: g1-implement handoff mis-cited `session_braking.py` as `identify_braking_arcs`'s
  caller; real caller is `braking_report.py::plot_arcs` — map anchor correction, low priority.
- **tc2**: minor 3-line duplicated-code (Fowler) in `fit_property_mixture`'s k=1 fallback path.
- **tc3**: `KinematicSample.a_lateral`'s m/s² unit not documented inline on the dataclass
  field — a reviewer had to cross-reference other consumers to confirm it.
- **tc4/tc6 (same finding, filed at both g3 and g4)**: **the headline finding** — F12 FAILED
  on real data. **Filed as issue #638** (title: "Phase 1 (#625) F12 stability rework:
  circuit-conditional or regularized property-class mixture") — full diagnosis/candidate
  root causes and acceptance criteria in the issue body. Admiral confirmed this is a follow-on
  wave, not this wave's job.
- **tc8** (new, surfaced by Cartographer reconcile): `scikit-learn` was a new runtime
  dependency (used by `property_mixture.py`/`mixture_stability.py`) undeclared in
  `requirements.txt` — a fresh clone/CI environment would fail to import this wave's own
  modules. **Fixed-now**: added `scikit-learn>=1.3.0` to `requirements.txt` (commit `bbc5a006`).
- **tc2/tc3**: minor Fowler duplicated-code nit + an undocumented unit on
  `KinematicSample.a_lateral` — **filed as issue #639** (combined, low priority; deliberately
  not fixed-now to avoid reopening already-reviewed/approved gate files at finalization time).
- **tc1, tc5/tc7**: ephemeral wave-scoped artifacts (a transient handoff-file mis-citation; the
  `CONVERGED_PLAN.md` planning doc's terser phrasing vs. the binding handoffs) —
  `recommend-and-defer`, not GitHub-issue-worthy (no downstream consumer once this wave
  archives); captured instead as workflow feedback (staged
  `.agent-work/staged-feedback/625-segmentation-substrate/AGENT_FEEDBACK.md`, for the Admiral
  to harvest into the shared durable log).

Full triage record: `.agent-work/625-segmentation-substrate/TRIAGE_RECOMMENDATIONS.md` (in the
worktree, archived with this wave's work area).

## 9. Map impact

Cartographer reconciled `docs/architecture/packets/physics.md` (new "Segmentation substrate
(#625, Phase 1...)" subsection under `struct:physics.layer2` documenting all 5 new modules —
all marked **MEASURED-not-wired**, no `src/` importer outside their own tests yet, consistent
with this being Phase-1 substrate for Phase 2/4 to consume later; the `arcs.py` and
`segment_classifier.py` entries extended in place; a "Characterization finding (#625)" callout
stating the F12 FAIL plainly, matching the file's existing callout style) and
`docs/architecture/index.md` (a 2026-07-18 reconciliation-log entry, following the #624
precedent). `check_arch_map.py` green, unchanged node/packet/overlay counts (42/20/12) — this
wave is module-leaf additions under an existing component, no new container/edge/overlay
warranted (verified: no new evo-region import, so no overlay-constraint edge change either).

## 10. Anything floated to the Admiral — DISPOSITIONED

**The F12 FAIL verdict** was floated as a capability-ledger/scope decision (does Phase 2/4
proceed treating the substrate as provisional, or does Phase 1 need a rework cycle first).
**Admiral ruling (2026-07-18, team messaging):** accepted as an honest, provisional Phase-1
deliverable — the FAIL is a data/model property, not a defect; the built artifacts are
reusable and stand. Owner chose to REWORK Phase 1 as a **follow-on wave** (tracked as issue
#638), not this wave's job. This wave's job was to finalize and ship the honest current
state — done.

**A second, smaller item was floated mid-flight and also dispositioned by the Admiral**: the
self-authored full-suite regression check proved impractically slow (see §7); the Admiral
explicitly authorized the targeted-subset fallback, which was then executed and the original
postcondition waived through the engine with that authority cited.

No other genuine gaps were hit this wave — every other decision point (cross-fit
standardization resolution, exact threshold value, class-share renormalization convention,
CSV metadata format, the `requirements.txt` fix-now) was within inherited
implementer/commander latitude and is documented in each gate's
IMPLEMENTER_RESULT/REVIEW_RESULT or in `TRIAGE_RECOMMENDATIONS.md`.
