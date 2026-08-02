# Review Result — g3-replication-review (LOAD-BEARING)

## Assigned Gate
`g3-replication-review` (#668 instrument panel, epic #659) — Instruments 2+3,
`src/physics/instrument_panel/replication.py` + `tests/unit/physics/instrument_panel/test_replication_channel.py`.

## Result
`APPROVE`

All 12 survey checks recorded pass; consolidated verdict APPROVE, 0 findings. Every reported number
reproduced on the pinned interpreter, and the load-bearing cross-class resolution was independently
verified by a standalone derivation + script that does not reuse the module's own centering code.

## THE ONE THING — independent verification of the cross-class resolution (CONFIRMED SOUND)
I re-derived the resolution from scratch and confirmed it numerically with a standalone script that
reimplements double-centering and per-driver-demean in pure numpy (no repo import for the derivation),
then cross-checks the module.

- **(a) Within a single class, across drivers, double-centering ≡ per-driver-demean.** For a fixed
  class `c`, the two residuals differ by `(grand − class_mean[c])`, a **constant across drivers**.
  Pearson r is invariant to an additive constant, so the two corrections give an identical within-class
  correlation. Measured: `max |r_double − r_demean|` over the 8 within-class correlations = **1.11e-16**
  (identical to floating point). CONFIRMED.
- **(b) The module's primary `interaction_replication_r` SPANS CLASSES.** It flattens the residual over
  the shared `(driver, class)` cells (`shared = set(resid_a) & set(resid_b)`, then correlates) — i.e.
  the whole driver×class matrix, not one class. On identical pure-shared-class halves my independent
  cross-class correlation gave `r_double = −0.0851`, `r_demean = 0.7922`; the module returned
  **exactly** the same values (`__file__` asserted to be the worktree copy, not the main-repo editable
  install). Only across classes does the shared class main effect (left in by demean) inflate a
  vacuous replication that double-centering removes.
- **Conclusion:** because the primary r spans classes, the negative control is **genuine, not vacuous**.
  Were the primary r within-class-only, demean and double-centering would be numerically identical and
  the negative control could not discriminate — exactly the failure mode the handoff warned to BLOCK on.
  That failure mode is **absent**.

## Handoff compliance
Did exactly what the handoff asked, within allowed scope. Instruments 2+3 delivered: golf-corrected
split-half replication (double-centering), out-of-sample σ-honesty (Student-t), per-class channel
comparison with injected thresholds. Every close criterion met and reproduced.

## Scope drift
Clean. `git status --porcelain` shows only the two new untracked trees (`src/physics/instrument_panel/`,
`tests/unit/physics/instrument_panel/`) plus `.agent-work/`. No `data/` change, no modified tracked
files → `pooling.py`, `student_t.py` unmodified. Grep confirms **no** `REPLICATION_*` frozen import
(only docstring mentions), **no** `join` usage, **no** `f1_data`/DB read, **no** `frozen_constants`
import, no fitted interaction term. Imports limited to `src.common.student_t` and
`src.physics.fingerprint.address` (read-only).

## Evidence verdict — every number reproduced (pinned interpreter)
- **Tests:** `pytest test_replication_channel.py -q` → **18 passed in 4.29s**.
- **pyright:** `pyright src/physics/instrument_panel/replication.py` → **0 errors, 0 warnings, 0 informations**.
- **3-arm falsifier:** arm(a) overall-skill = **0.0114**, arm(b) shared-class = **−0.0306** (both < 0.2
  null band), arm(c) injected-interaction sweep = **0.063 → 0.738 → 0.917 → 0.978** (monotone, clears
  0.5). Generator carries a **TRUE** driver×class interaction term (`_draw_true_effects` draws an
  `interaction[(d,c)] ~ N(0, INTER_SIGMA)` added as `inter_strength·interaction`), so arm(c)'s monotone
  recovery is real, not an additive-only artifact.
- **Negative control (seed 404, same data both corrections):** `r_double = 0.0006`, `r_demean = 0.6854`,
  gap = **0.6848 (> 0.4)** — matches the implementer's 0.0006 / 0.685 exactly.
- **σ-honesty out-of-sample:** correct-σ empirical coverage = **0.9063 ≈ nominal 0.90**; understated
  (0.35×) = **0.5040** (materially below). The estimate (`mu/sigma/n_eff` from the training half) never
  sees `held_out_value` → genuinely out-of-sample, not self-referential.
- **Student-t heavy-tail (not Gaussian):** at `n_eff=1`, `nu = 3.5 < DEFAULT_NU_LOSS 4`; interval
  half-width **4.16 > Gaussian 1.96·scale = 2.77** (ratio 2.94). Heavy-tail path exercised.
- **r_floor formula:** `r_floor(0)=0.70`, `r_floor(25)=0.65`, `r_floor(100)=0.50`, `r_floor(280)=0.50`
  — matches `threshold + (cap−threshold)·clip((ref−n)/ref,0,1)` exactly.
- **Channel comparison:** winner-by-margin, tie-default→utilization (`DRIVER_ALIGNED_CHANNEL =
  FINGERPRINT_CHANNELS[0]`), unresolved (neither clears floor), unmeasurable (support<15 and <2
  resolved drivers) — all decision paths green, no-frame-kill enumerates every raw class.

## Code/doc quality
Minimal, cohesive, well-documented. Functions are short and single-purpose; structured values are
objectified into frozen dataclasses (`CellValue`, `ReplicationThresholds`, `CoverageCheck`,
`ClassChannelVerdict`). Docstrings carry the load-bearing intent (double-centering rationale,
negative-control warning, out-of-sample requirement). `_pearson_r` returns an honest `None` for
<2 points or constant vectors rather than fabricating a number.

### Fowler refactoring pass
Driven over all 12 baseline smells; `verify_fowler_pass.py` exits 0. 10 absent, 2 **overridden**
(logged): **primitive-obsession** — `Cell = tuple[object, object]` is the registered "any hashable
label" requirement, not lazy primitives (structured values are already objectified); **speculative-
generality** — the injection seams (`center` fn, `ReplicationThresholds`, pre-split halves) are stated
F12-independence / negative-control requirements, i.e. load-bearing extension points, not speculation.
No smell flagged.

## Map impact verdict
- **Evidence supports claimed change:** yes — reproduced tests + pyright + the arm/negative-control/σ numbers.
- **Constraints not violated:** yes — `lowest-dimensionality` (pure data transform, no new model param),
  `no-baked-normality` (Student-t), `no-frame-kill` (unmeasurable/unresolved are COMPLETE verdicts).
- **Notes match the diff:** yes — new sibling module to `variance_decomposition.py`, read-only reuse of
  `student_t.predictive_t` + `fingerprint.address.FINGERPRINT_CHANNELS`; no overstated impact.
- **Decision candidates surfaced:** the implementer correctly surfaced (and resolved in favor of the
  negative-control requirement) the cross-class-vs-within-class subtlety and flagged it as an assumption.
  I independently confirmed the resolution is the correct one.
- **Durable context routed:** G6 wiring of the frozen `REPLICATION_*` values is left as a noted follow-on;
  no dropped context.

## Reconciliation check
No architecture divergence requiring Commander reconcile. `decision:golf-correction-is-DOUBLE-CENTERING`
(interaction r spans classes) is realized exactly as recorded. The module is F12-independent (frozen
constants not minted; G6 wires later) — an intended, documented deferral, not drift.

## Blockers
- none

## Out-of-scope observations
- none requiring triage. (G6 will wire the frozen `REPLICATION_*` set into `ReplicationThresholds`;
  caller-side averaging over the 3 distinct 2v2 partitions is left to the caller per the handoff — the
  core correctly takes two pre-split halves.)

## Workflow Feedback
- **Handoff gaps:** none in the review handoff itself — it was precise and correctly elevated the
  cross-class-vs-within-class resolution as THE load-bearing thing to verify. Worth noting the
  *implementer's* handoff was ambiguous on this exact point (it read as within-class), which the
  implementer flagged; the review handoff already absorbed that lesson and named the correct resolution.
- **Context rediscovered:** the editable-install `.pth` trap (ad-hoc worktree scripts silently import the
  MAIN repo `src/`) — I defended against it by prepending the worktree to `sys.path[0]` and asserting the
  loaded module's `__file__`. A one-line note in the handoff pinning "assert worktree `__file__` when
  importing the new module standalone" would have saved the rediscovery, but pytest itself resolved
  correctly.
- **Instructions improvised around:** none material — the engine survey template, the Fowler rail, and the
  reproduce-every-number close criteria fit the task cleanly.
- **What would have made this easier:** nothing beyond the `.pth` note above. The handoff's explicit
  "verify (a) and (b) yourself with a scratch derivation" framing was exactly right and made the
  load-bearing check unambiguous.

## Return status
`complete`
