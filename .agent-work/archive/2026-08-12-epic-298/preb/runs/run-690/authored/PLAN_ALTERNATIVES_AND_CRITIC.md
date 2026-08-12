# Plan-alternatives + cold critic — #690

Both rigor mechanisms are **bias-to-yes** and were run. Each carries a named untaken road for the part
that could not be run as doctrine prefers.

## Untaken road (mechanism level) — parallel/cold subagent dispatch

**Not taken:** dispatching the plan-alternative authors and the cold plan critic as independent
subagents with no authoring context. **Reason:** the engagement's standing instruction for this session
forbids launching agents unless the user asked for it, and the user did not. **Consequence, stated
plainly:** the critic below is *not cold* — it was written by the same context that authored the plan,
so it is weaker than a fresh-context adversarial read on exactly the axis that matters (blind spots the
author shares). **Recommended remedy at the implementation engagement:** run one cold critic over
`MISSION_FRAME.md` + `execute.json` alone before g2 opens. Panel-vs-single: **single** is right here —
this is one function's scaling law in one module, not an epic-spawning or architecture-touching artifact.

---

## Plan-alternatives (design-it-twice)

### Candidate A — constraint: *minimum blast radius*

Do the whole change inside `compute_class_utilization_observable`: call `class_time_ledger(...)` on the
real lap, multiply the session σ by the share vector inline, store both grains on the dataclass. No new
public name.

- **Depth:** modest — the law is an inline expression.
- **Locality:** excellent — one module.
- **Seam placement:** none new; the law is reachable only through the full observable.
- **Testability:** *weak on the axis the issue names.* Every width-shape assertion (partition identity,
  monotonicity, degenerate limits) has to be driven through a constructed `SegmentMap` plus two speed
  profiles. The proof of a three-line invariant becomes a fixture exercise.

### Candidate B — constraint: *seam placement first — the law must be provable on its own*

Add one public pure function to the same module, beside the existing `onesided_sigma_from_grip`:

```
allocate_sigma_to_classes(sigma_session: float, time_share_by_class: np.ndarray) -> np.ndarray
```

with the invariants stated on its interface (weights must be finite, non-negative, sum to 1 within
tolerance; output is non-negative and sums to `sigma_session`). `compute_class_utilization_observable`
becomes its single production caller. The width-shape test targets the function directly with plain
arrays; a thinner integration test confirms the observable wires it.

- **Depth:** real — an interface (inputs, invariants, error modes) with the law behind it.
- **Locality:** identical to A — same file, no new module.
- **Seam placement:** *matches the module's existing shape.* This module already exports exactly this
  kind of pure numeric helper (`onesided_sigma_from_grip`, `grip_band`, `grip_scale_from_store`), so the
  seam is not invented — it is the one already there.
- **Testability:** strong. Fixture-free, and every degenerate case is one line.
- **Cost:** one additional public name in `__all__`.

### Convergence → **Candidate B**, with A's restraint grafted in

The deciding axis is the issue's own acceptance criterion: *"per-class G σ⁺ scaling with documented
rationale **+ a width-shape unit test**."* B makes that test a direct assertion on the law; A makes it a
map-fixture integration test that proves the same thing more slowly and less legibly. Deletion test on
B's new name: delete `allocate_sigma_to_classes` and the invariant proof scatters back into
fixture-heavy tests — it earns its keep.

**Grafted from A:** do **not** extend `class_ledger.py`. Shares come from calling the existing public
`class_time_ledger`, leaving the anti-circular g1 core untouched.

### Untaken road (candidate level) — Candidate C: extend `ClassDeficits`

Add real-lap `time_share_by_class` to `ClassDeficits` so the observable gets shares and deficits from one
call, avoiding a second transit-time integral. **Not taken:** it modifies the frozen, safety-critical
anti-circular core for a micro-optimisation, widening the review surface on the most sensitive file in
the lineage. **Settle:** if the builder's per-driver cost ever becomes material, profile the duplicated
`ds/v` integral and revisit then.

---

## Cold plan critic (self-run — see the mechanism-level untaken road)

Findings, each with the disposition taken. All six were folded into the plan **before** it froze.

**C1 — "Σ_c σ⁺_c = σ_session is asserted, not derived."**
Under perfect correlation it is the *signed* perturbations that add. σ⁺ is the scale of a **half/truncated**
Student-t, so summing folded quantities is not obviously the same statement.
→ **Accepted, and it sharpened the plan.** The identity holds on the **scale parameter of the underlying
(un-folded) t**, which is precisely what `OneSidedGripBand.sigma_plus` is — the folding happens later, in
`upper_bound()`. Disposition: g2's close criteria now require the rationale to say this explicitly, and
require the width-shape test to assert on `sigma_plus`, **not** on differences of `upper_bound()`.

**C2 — "Why does a zero-time-share class get zero width?"**
→ **Accepted as under-specified.** A class with no lap time also has a structurally zero time deficit, so
a zero band on a zero point is coherent — but that must be *pinned*, not incidental. Disposition: an
explicit degenerate case in the width-shape test.

**C3 — "Does this actually fix the 1e9 σ that made the diagnostic vacuous?"**
→ **Accepted, and it is the most important correction.** No. #690 divides the width by roughly the class
count; **#721** is what removes the ~90 s pace level and the 1e9 magnitude. Disposition: g1's re-scope
note and the decision anchor must both state that #690 alone does not make the #712/#670 diagnostic
informative. No gate may claim otherwise.

**C4 — "You change a persisted column's meaning but never rebuild the store."**
→ **Accepted; deliberate but implicit.** Regenerating is a season-scale batch run — out of scope here and
Admiral-owned per `lesson:admiral-owns-long-batch-compute`. Disposition: g3 must state in the open that
existing rows are a **stale vintage**, name the vintage marker, and name who rebuilds — rather than
leaving a silently-mixed store.

**C5 — "Calling `class_time_ledger` duplicates a transit integral `class_deficits` already did."**
→ **Accepted as a real cost, consciously paid.** Disposition: the tradeoff and Candidate C are recorded
in the gate so a reviewer meets the reasoning instead of rediscovering the duplication.

**C6 — "Is g1 a genuine evidence gate, or ceremony?"**
→ **Accepted as a live risk.** An evidence-only gate that cannot change the outcome is theatre.
Disposition: g1 carries an explicit **falsification exit** — a named condition under which it blocks the
run rather than proceeding.
