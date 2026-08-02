# Review Result — g4 (issue #664, epic #659) — THE SUBSTANTIVE GATE

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4-review` — season-capable build CLI + BOUNDED validation run + gating delete-d/block jackknife with positive control, reported as an instrument.

## Result
`APPROVE`

## Independently RECOMPUTED numbers (reviewer's own math, not the implementer's stats path)

Ran a reviewer recompute script (`scratchpad/g4_recompute.py`) that loads the SAME bounded slice
(2023 Q round 10, VER→Red Bull Racing), reproduces the delete-d driver-block replicate loop, and
computes per-class stability + boundary drift with the reviewer's OWN numpy (`np.nanmedian` /
`np.percentile` / hand-written symmetric nearest-neighbour), NOT `per_class_stability` /
`boundary_set_drift_m`. Every value matched the persisted artifact:

| quantity | reviewer recompute | artifact | match |
|---|---|---|---|
| n_pool_laps / drivers | 272 / 20 | 272 / 20 | ✓ |
| straight time-median (s) / IQR (s) | 1.247645 / 0.012357 | 1.247645 / 0.012357 | ✓ |
| braking_zone IQR_t / IQR_s | 0.004207 / 0.032464 | same | ✓ |
| severity c0 median_t / IQR_t / IQR_s | 3.490806 / 0.016796 / 0.052820 | same | ✓ |
| severity c1 / c2 / c3 (all fields) | match to 6 dp | — | ✓ |
| **boundary drift mean / max (m)** | **0.736349 / 1.154556** | **0.736349 / 1.154556** | ✓ |
| within_anchor (max ≤ 10 m) | True | True | ✓ |
| positive control injected / baseline spread | 0.15894039735 / 0.0 | same | ✓ |

Regression subset (import-graph-scoped, per handoff): **184 passed in 20.11s**, pinned interpreter.

## Handoff compliance
Satisfied. Season-CAPABLE own-db CLI composing g1/g2/g3 + #662 segment_map derivation (resumable,
idempotent, G soft-degrades); BOUNDED validation slice (1 circuit, foreground, 62.1s ≪ 10-min bound);
gating delete-d driver-block boundary-jitter jackknife (B=30) with a REQUIRED positive control;
reported as an INSTRUMENT (allocation-not-gating), no manufactured pass/fail. All eight Close Criteria
met and independently reproduced.

Load-bearing checks:
1. **BOUNDED run** — GB round 10 only, foreground; my jackknife-only recompute completed in 16.2s
   (session load cached), confirming the run is nowhere near the bound. NOT full-season. ✓
2. **Recompute matches** — exact to 6 dp on every per-class stat + boundary drift (table above). ✓
3. **Leveraged + out-of-sample** — `make_delete_d_blocks` drops whole DRIVER blocks until ≥10% of the
   272-lap pool is removed; observed 27–45 laps dropped per replicate, none keeps the full pool (NOT
   drop-one/zero-leverage). Each replicate re-derives the reference lap + boundaries IN-MEMORY from the
   reduced pool (`_reduced_segment_map`, no session reload) and re-attributes the SAME fixed
   v_ideal/v_real (no ceiling re-sim). NOT self-weighted: the scoring ceiling is
   `build_car_ceiling(strictly_pre=True)` (target round excluded from causal history); the field
   reference lap only PLACES boundaries — the perturbed quantity is decoupled from the score. ✓
4. **Positive control FIRED = True** — injected corner→straight-edge deficit; injected straight-class
   spread 0.15894 strictly exceeds clean-interior baseline 0.0. The instrument detects the
   misattribution it exists to detect. ✓
5. **No new literal band** — anchored to frozen `MAP_STABILITY_DRIFT_M` (=10 m); `within_anchor=True`
   is derived, not minted. The `_BLOCK_FRACTION`/`_win` construction params are documented as
   instrument-design knobs, not acceptance thresholds. ✓
6. deficits-sum-to-lap labelled CONSTRUCTION (not validation); own-db (never f1_data); pinned
   interpreter throughout; G soft-degrade documented AND confirmed (grip_estimates.db absent on disk →
   σ⁺=0, grip_batch NOT run). Measured result reported as an instrument reading. ✓

## Scope drift
In scope: 3 new committable files + `.gitignore` + local-only artifact under `.agent-work/`. All
specific exclusions respected — no full-season run, no grip re-fit, no new literal band, no f1_data
writes, no seeded/supersede path. **Observation (non-blocking):** the `.gitignore` diff adds TWO
additive defensive lines (`/data/reference_utilization.db` AND `.agent-work/**/*.db`), where the
handoff mentioned only the latter — both merely prevent committing regenerable DBs (the CLI's `--db`
default is `data/reference_utilization.db`), fully consistent with own-db intent.

## Evidence verdict
Required evidence present and independently reproduced (not read-through). Test mode is
test-after/inspection (#656): 8 synthetic + temp-db unit tests, no real session load; the real slice is
the one-off `.json`/`.md` artifact. Reviewer verified the artifact against the world by re-deriving it.

## Code/doc quality
Fowler pass over all 12 baseline smells; rail `verify_fowler_pass.py` exits 0. 3 flagged NON-BLOCKING
observations (long-method: `compose_and_persist_weekend` ~145 LOC; duplicated-code: v_ideal
ceiling→sim→interp repeated in compose vs `_run_validation`; long-parameter-list: `load_weekend_inputs`
~11 kwargs). 2 logged overrides (data-clumps → epic store-key identity tuple; primitive-obsession →
src/physics raw-numpy + string-class-id idiom). Pure stats correctly split into
`class_utilization_validation.py`; comments carry domain rationale (anti-circularity, instrument-not-gate),
not deodorant.

## Map impact verdict
- **Evidence supports claimed change:** yes — `claim:attribution-robust` confirmed by reproduced
  jackknife + fired positive control; `claim:deficits-sum-to-lap` is a construction check as labelled.
- **Constraints not violated:** own-db, strictly_pre (no race-outcome leakage), build-capable-run-bounded,
  consume-not-refit for G — all honored.
- **Notes match the diff:** yes — new CLI + new pure module; g1/g2/g3 + derivation consumed read-only,
  no contract changes.
- **Decision candidates surfaced:** anchors exercised, none needed new authority.
- **Durable context routed:** implementer already surfaced the absolute-magnitude-vs-ceiling calibration
  question as a triage candidate (out of g4 scope) — appropriate.

## Reconciliation check
No architecture divergence requiring Commander reconcile. Read-only consumption of the epic's existing
modules; the new pure `class_utilization_validation.py` is a clean sibling.

## Blockers
- None.

## Out-of-scope observations
- Absolute per-lap deficit magnitude (5.6–8.8 s vs the physics ceiling) is large — a reference-lap-grid
  vs #628 ribbon-grid calibration question, not attribution robustness. Already a triage candidate.
- Non-blocking refactors: extract the g3 per-driver row loop; a `_constructor_v_ideal` helper to remove
  the v_ideal duplication; group data-source paths in `load_weekend_inputs`.

## Workflow Feedback
- **Handoff gaps:** the Deliverable-Path note / gitignore expectation described a single `.gitignore`
  line, but the diff carries two additive lines (also `/data/reference_utilization.db`); minor, but the
  handoff's "a .gitignore line" undercounts. The implementer already flagged the related `.agent-work/`
  partial-ignore reality in their result.
- **Context rediscovered:** the artifact JSON persists only the per-class SUMMARY (median/IQR/std), not
  the raw per-replicate deficit vectors, so the handoff's option A ("re-derive from the replicate data it
  carries") is not actually possible from the JSON alone — only option B (re-run the pure math on the
  same inputs) is. I took option B. Worth correcting the handoff wording so a future reviewer doesn't
  hunt for replicate arrays that aren't in the file.
- **Instructions improvised around:** none material — the engine + Fowler rail drove cleanly.
- **What would have made this easier:** persisting the raw replicate deficit matrix (or a seed +
  block-schedule dump) alongside the summary would let a reviewer recompute the stats WITHOUT a ~fresh
  weekend load, making the recompute cheaper and truly artifact-only.

## Return status
`complete`
