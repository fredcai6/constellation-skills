# Plan alternatives — issue #704 (design-it-twice)

Contract: `references/design-it-twice-brief.md`. Three gate-plan candidates, each under one named
distinct constraint, compared on depth / locality / seam placement / testability, converging to one
recommendation (not a menu).

**Panel-vs-single, and how these were generated — surfaced, not silent.** The doctrine default is
parallel candidate authors (subagents) plus a *cold* critic with no authoring context. This session
carries a standing instruction not to dispatch subagents unless the user asks. So all three
candidates and the critic pass below were authored **in this context, by the same agent**. That is a
real weakening — a self-critic shares the author's blind spots — and it is recorded here as a
**named untaken road** rather than skipped silently:

> **Untaken road 1 — parallel candidate authors.** Not dispatched (session policy: no subagents
> unless requested). Mitigation: each candidate was written to its constraint first and judged
> against fixed axes afterwards.
> **Untaken road 2 — cold plan critic.** Not dispatched (same reason). Mitigation: the critic pass
> in `PLAN_CRITIC.md` was run adversarially against the frozen candidate, and its findings are
> triaged in writing. It is **not** a cold read and must not be reported as one.

Weight check: this is a single-file, private-helper, behavior-preserving change. Under the
scaled-by-weight rule a single candidate with named untaken roads would have been defensible; three
were run anyway because the byte-identical acceptance makes the *ordering* of the proof, not the code
shape, the actual design question.

---

## Candidate A — "smallest possible diff" (constraint: minimize the footprint on a load-bearing module)

One gate. Introduce `_axis_value_lists(grid)` (one pass, returns per-driver value lists, per-class
value lists, running total, count); rewrite `_axis_means` and `main_effect_margin_uncertainty` to
consume it; add the pinning test in the same gate. Capture the `float.hex()` snapshot before and
after within that gate.

- **Depth:** shallowest. One diff, one review.
- **Locality:** perfect — nothing outside `replication.py` + its test module.
- **Seam:** the helper sits below the injected-thresholds seam; no public surface moves.
- **Testability:** the weak point. The snapshot harness is authored in the same gate as the change,
  so a harness bug that happens to be insensitive to the very difference it exists to catch would
  pass both runs. Self-consistent ≠ pinned.

## Candidate B — "characterize first" (constraint: test-led; the proof instrument must be validated against the pre-change code)

Two gates.

- **G1 — characterization + pinning, no source change.** Add to
  `tests/unit/physics/instrument_panel/test_replication_channel.py`: (a) an axis-grouping contract
  test (ragged / empty / single-cell / duplicate-driver grids, key insertion order, per-key value
  order); (b) a **naive-accumulation pinning test** built on a grid where compensated and naive
  summation provably differ (a driver row containing `1e16, 1.0, -1e16, 1.0` — naive → 1.0,
  `sum()` → 2.0), asserting the module's mean matches the naive value exactly. Emit the
  `float.hex()` snapshot to `.agent-work/issue-704/evidence/axis_snapshot_before.json`. Gate closes
  only if the new tests pass **against unmodified `replication.py`** — that is what proves the
  instrument measures today's behavior rather than tomorrow's.
- **G2 — the dedup.** Introduce the helper; rewrite both consumers; re-emit the snapshot and require
  an exact-bit diff of zero. G1's tests must pass **unmodified** (any edit to them in G2 is a
  BLOCK-worthy tell).

- **Depth:** one extra gate boundary on a cosmetic change. Real cost, one review round.
- **Locality:** same two files as A.
- **Seam:** same as A.
- **Testability:** strongest. The pinning test is validated against the pre-change code, the
  before-snapshot is provably taken from unmodified source, and the durable guard survives the run —
  which is what stops the next simplify-pass from replacing the loop with `np.mean`.

## Candidate C — "extract for reuse" (constraint: maximize reuse across the panel)

Move the axis-grouping into a new shared module (e.g. `src/physics/instrument_panel/_grids.py`) so
the other instruments could adopt it.

- **Depth:** deepest — a new module surface.
- **Locality:** worst; adds a file the architecture map must account for.
- **Seam:** wrong seam. `sector_scorecard.py` and `variance_decomposition.py` do not group on the
  `(driver, class)` axes; there is **no second consumer today**. A shared module for one caller is
  speculative generality (YAGNI) and buys a Cartographer reconcile edit for six lines of arithmetic.
- **Testability:** neutral, but it widens the reviewed surface on a change whose entire acceptance is
  "nothing changed".
- **Verdict: rejected.** Recorded so the option is visibly closed, not overlooked.

---

## Comparison

| Axis | A | B | C |
|---|---|---|---|
| Depth (cost) | ✅ lowest | ⚠️ +1 gate | ❌ new module |
| Locality | ✅ | ✅ | ❌ |
| Seam placement | ✅ below the injected seam | ✅ below the injected seam | ❌ premature shared surface |
| Testability of the *stated acceptance* | ❌ harness unvalidated | ✅ harness validated pre-change | ⚠️ unchanged from A |
| Leaves a durable guard against re-breaking | ⚠️ yes, but unproven | ✅ proven | ⚠️ |

## Recommendation — **B**, with A's discipline on diff size

Take Candidate B. The one thing this issue actually risks is a silent numeric change, and B is the
only ordering in which the instrument that would detect it is itself proven to work **before** the
code moves. The extra gate is one review round on a ~40-line test addition — cheap against the
alternative, which is a green suite that proves nothing because both sides of the comparison were
authored together.

Adopt from A: keep the G2 diff minimal — one new private helper, two rewritten function bodies, one
comment explaining the naive-accumulation constraint. No opportunistic tidying of neighbouring code
in the same gate.

Reject C outright; if a second consumer for axis grouping ever appears, promoting the private helper
is a two-line move at that time.
