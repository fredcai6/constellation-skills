# Mission Frame — issue #690 (per-class G σ⁺ band scale)

Work id: `690-grip-sigma-band-units` · Commander planning engagement (implementation is a later engagement).

## Intent

Make the one-sided grip (G) uncertainty band that wraps each **per-class** transit-time deficit carry a
width **proportional to that class's share of the lap**, instead of every class carrying the **whole-lap**
grip σ. In map terms: stage **E** (`struct:physics.utilization`) currently consumes stage **D**'s
(`struct:physics.layer2`, grip) session-level pace σ at the wrong grain, and hands that mis-grained σ to
stage **G** (`struct:physics.fingerprint`) through the `driver_class_observables` store column.

The frame is **required, not skipped**: this run touches a mapped pipeline seam (D→E→G) with an existing
decision anchor, a persisted store contract, and a live downstream consumer.

## Affected Capabilities

- **`capability: per-class utilization observable`** (`compute_class_utilization_observable`) — today it
  produces per-class ABSOLUTE speed/time deficits plus a one-sided grip band per class. This run changes
  **only the band's width**, never its location.
- **`capability: grip-baseline consumption (stage D → E)`** — G is *consumed, never re-fit*
  (`get_grip_at` → `(mu, sigma)`). This run keeps that posture and changes only how the consumed σ is
  allocated across classes.
- **`capability: driver-fingerprint σ composition (stage G)`** — `fingerprint/fit.py` folds the stored
  `g_sigma_onesided` in quadrature into `sigma_cell`. This run **relies on** it and changes its inputs'
  magnitude, but requires no code change there (its cell grain is already `(driver, class)`).

## Examples / Events

- **Example (the defect, concretely).** A lap with `(2+k)=6` classes and a session grip σ of 0.30 s
  currently emits six bands each of scale 0.30 s — total asserted width 1.80 s against a lap-level grip
  uncertainty of 0.30 s. Under this run, a class holding 12% of lap time gets 0.036 s and the six widths
  sum back to 0.30 s.
- **Example (the live consequence).** A shipped season run recorded `g_sigma_onesided` at slice mean
  ~1.15e9 s against a `time_deficit_s` of 0.1–0.2 s, driving held-out coverage to 1.000 and making the
  fingerprint log-score vacuous (`docs/physics/season_670_report.md:82,99`). #721 removes the ~90 s pace
  level; **#690 removes the remaining per-class over-width.**
- **Event (boundary-crossing).** The `driver_class_observables` row write is the D→E→G contract signal.
  Its `g_sigma_onesided` column changes **meaning** without changing name or type — the vintage hazard.

## Structural Anchors

- `struct:physics.utilization` — `src/physics/utilization/class_utilization_observable.py` (module-leaf;
  the band producer, `onesided_sigma_from_grip` / `compute_class_utilization_observable`).
- `struct:physics.utilization` — `src/physics/utilization/class_ledger.py` (module-leaf; supplies
  `ClassTimeLedger.time_share_by_class`, the scaling weight — **consumed read-only, not modified**).
- `struct:physics.utilization` — `src/physics/utilization/reference_utilization_store.py` (module-leaf;
  owns the `driver_class_observables` schema and its `format_version`).
- `struct:physics.layer2` — `src/physics/layer2/grip_store.py` (`get_grip_at`; **read-only** this run).
- `struct:physics.fingerprint` — `src/physics/fingerprint/fit.py` (the real downstream σ consumer;
  expected **doc-only** touch).
- Non-map node — `scripts/build_class_utilization_observables.py` (the CLI that writes the rows).

## Governing Constraints / Assumptions

- **`constraint: anti-circularity (#628)`** — no division of an observed quantity by a capability
  quantity anywhere in this lineage. The chosen weight (`time_share_by_class`) is derived from map
  geometry and **one** speed profile, so it cannot breach this; a deficit-proportional weight would.
- **`constraint: G is consumed, never re-fit`** (binding pre-ruling in the module docstring) — this run
  must not touch the grip fit, and must not mint a per-class grip decomposition G does not carry.
- **`constraint: μ stays at zero`** (#678 is out of scope) — the band's centre remains the unshifted
  point deficit. `point_deficit` must stay **byte-identical** with and without G.
- **`constraint: one canonical path`** (project tenet) — no compatibility shim, no dual field meaning.
- **`constraint: physics changes need L1–L4 truth evidence`** — the width-shape test is L2
  (invariant/known-answer: the coherence identity) plus L3 (limit/degenerate: σ=0, empty class,
  single-class lap).
- **`constraint: producer + committed consumers + schema doc move together`** — the store column's
  changed meaning obliges the producer, the vintage marker, and the docs in the same run.
- **`assumption: grip perturbs a lap uniformly per unit time`** — the substantive modelling assumption
  behind time-share weighting, stated explicitly because it is *not* measured (see decision pressure).

## Decision Anchors & Decision Pressure

- `decision:c1_driver_utilization_design` — the governing anchor for this layer; already carries a #628
  Phase-3b Extension section, so it is the natural home for this run's documented rationale.
  `@grade: settled/human · leans g3`
- `decision:class-attribution-membership-faithful` — every class reduction is `Wᵀ·quantity`, never an
  argmax collapse. The weight vector must come through the same `W`, not a hand-rolled class map.
  `@grade: settled/human · leans g2`
- `decision:grip_estimate_record_session_level_pk` — G's PK is the session, which is *why* its σ is a
  session-level common-mode quantity and *why* linear (not quadrature) allocation is the coherent law.
  `@grade: settled/measured · leans g2`
- `decision:690-per-class-sigma-allocation-law` (**new, this run**) — σ⁺_c = s_c · σ_session with
  s_c = `time_share_by_class`, under the coherence identity Σ_c σ⁺_c = σ_session.
  `@grade: guess · leans g2,g3 · settle: recompute the #670 held-out coverage/log-score under linear vs sqrt-share weighting`
- `decision:690-shares-from-real-lap` (**new, this run**) — weights come from the driver's real lap.
  `@grade: guess · leans g2 · settle: compare per-class shares from v_real vs v_ideal on one weekend; immaterial if max |Δs_c| < 0.01`
- `decision:690-observable-carries-both-grains` (**new, this run**) — the observable exposes both
  `g_sigma_onesided_by_class` and `g_sigma_session_s`; the old scalar field name is retired, not re-pointed.
  `@grade: settled/measured · leans g2,g3`
- `decision:690-base-on-721-branch` (**new, this run**) — build on `fix/721-grip-band-units`, not main.
  `@grade: settled/measured · leans g1,g2`
- **Decision pressure (surfaced, not decided):** a *grip-sensitivity* weighting (corners weighted above
  straights, since a straight is power-limited and barely grip-limited) is physically better than a flat
  time share, but it mints a per-class physical weighting G does not carry — i.e. re-fitting G, explicitly
  out of #690's scope. Routed to triage as a follow-on, not taken here.
- **Decision pressure (surfaced, not decided):** whether `format_version` on `driver_class_observables`
  is bumped depends on a fact this run has not yet checked (who reads it) — the plan verifies before
  choosing, and states the fallback.

## Claims / Evidence Surfaces

- **`claim: point deficit is unchanged by G`** — verified by the pre-existing
  `test_point_deficit_byte_identical_with_and_without_grip`. **Must still pass**; this run widens nothing
  about the location.
- **`claim: the band is one-sided toward larger deficit`** — `test_grip_band_is_one_sided_toward_larger_deficit`.
  **Must still pass**; scaling the width never flips the direction.
- **`claim: the band is heavy-tailed (Student-t), not Gaussian`** — `test_grip_band_is_heavy_tailed_not_gaussian`.
  **Must still pass**; the law changes the scale, not the distribution family.
- **`claim: the module does not re-fit G`** — `test_module_does_not_refit_grip`. **Must still pass.**
- **`claim (new): per-class widths partition the session σ`** — the width-shape test the issue's
  acceptance names: Σ_c σ⁺_c == σ_session, monotone in share, σ⁺_c ≤ σ_session with equality only for a
  degenerate single-class lap, σ_session=0 ⇒ all widths 0, zero-share class ⇒ zero width.
- **`claim (new): the fix strictly narrows`** — every per-class width is ≤ the width it replaces, on the
  same inputs.

## Map Confidence / Staleness / Disputes

- **`struct:physics.layer2` grip node — recorded HONEST MEASURED-NULL.** The packet states the grip node
  was built and gated but g4 held-out reconciliation regressed +155.5% RMS and g5 separability was 31.9%
  (FAIL). **Effect on the plan:** this run must not present a narrower band as *improved grip skill* — it
  is a units/grain correction to a signal whose own separability has not cleared its bar. The gate's
  evidence language is constrained accordingly.
- **Issue text is stale (verified, not assumed).** #690's premise (`hypot(mu,sigma)`) and its priority
  framing ("low while the grip store is empty") are both out of date. **Effect on the plan:** gate g1 is
  evidence-only, per the project's diagnose-before-fixing planning invariant, and re-states scope before
  any code is written.
- **Unmerged sibling branch is a live dispute surface.** `fix/721-grip-band-units` (issue #721, OPEN)
  rewrites the same function and is not merged; its worktree is **locked**, i.e. possibly active.
  **Effect on the plan:** g1 re-verifies the branch state at execution time rather than trusting this
  frame's snapshot, and the plan names the rebase-onto-main path if #721 lands first.
- **Naming collision (map-recorded).** #663 files call grip "module **G**", but in the pipeline chain
  grip is stage **D** and letter **G** is the driver *fingerprint*. **Effect on the plan:** every gate and
  handoff says "grip (stage D)" or "fingerprint (stage G)" — never bare "G".

## Out of Scope

- Moving μ off zero / sharpening the band's centre (**#678**).
- Re-fitting, re-pooling, or re-parameterising the grip curve itself (**#663**, and the c2x2
  "band keyed to evolution magnitude" replacement contract, explicitly unsettled by #721).
- The `hypot(mu,sigma)` → `abs(sigma)` correction and the `x=0` evaluation-point move (**#721**) — this
  run *depends on* them, it does not redo them.
- Any change to `class_ledger.py`'s deficit computation, the `W` attribution matrix, the energy channel,
  or `class_utilization_validation.py`.
- Any change to `fingerprint/fit.py`'s σ composition *arithmetic* (doc-only touch permitted).
- Re-running the season / regenerating the #670 report.
