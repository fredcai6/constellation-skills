# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5 (Tier-2 fracture quantification -- close-with-number OR bounded-defer-with-number)`

## Completed slice
All four x7-basis fractures given a NUMBER: DUAL-CdA CLOSED (reproduced live, not re-quoted);
GRIP-TRIPLET, a_long, SHARED-TRAJECTORY-NOISE BOUNDED-DEFER, each with a defensible numeric
bound and stated method. `scripts/tier2_fracture_analysis.py` runs end to end (exit 0) and
`docs/physics/627-tier2-fractures.md` documents all four with citations and the pasted script
output as evidence.

## Scope
**Files changed:**
- `scripts/tier2_fracture_analysis.py` (new)
- `docs/physics/627-tier2-fractures.md` (new)
- `.agent-work/627-unified-basis/g5-implement/IMPLEMENTER_PLAN.json` (engine-owned plan state)

**Specific exclusions touched:** no. `cross_view.py`, `estimate_store.py`,
`decoupled-1d-longitudinal.md` were READ-ONLY (cited, not edited). The decoupled a_long path was
not re-wired. No production default, `circuits.yaml`, gold, or store schema changed. No
`data/*.db` writes (`git status --porcelain -- data/` empty throughout).

## Behavior changed
No production behavior changed. New analysis script + doc only.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` -- new
  `scripts/tier2_fracture_analysis.py` (read-only consumer of `cross_view.py`/`estimate_store.py`)
  and `docs/physics/627-tier2-fractures.md`.
- **Decision anchor:** `decision:decoupled_1d_longitudinal` -- NOT re-opened; the a_long fracture
  is quantified as a bounded-defer citing the existing decision record, no new decision proposed.
- **Evidence produced:** each of the 4 fractures now carries a number (see below), reproducible
  via `py scripts/tier2_fracture_analysis.py`.
- **Trust limitations found:** the SHARED-TRAJECTORY-NOISE bound (fracture 4) is a proxy, not a
  first-principles measurement -- see its section below and the doc's honest framing ("genuine
  null under the tested method, not proof of zero effect"). A live perturbation re-fit of the
  shared smoother would give a tighter, trajectory-noise-specific number; not attempted this gate
  (infeasible under current multi-agent CPU load, cites #644).
- **Triage candidates:** (1) a live perturbation-based measurement of fracture 4's bound, once CPU
  contention (#644) clears; (2) GRIP-TRIPLET's 0.6% bound is small enough that a joint solve is
  not obviously worth building -- flagging for whoever next touches the grip axes so this isn't
  silently re-litigated without checking this number first.

## Test mode
**Required:** test-after allowed (handoff: "the analysis script is the evidence, guard any
DB-dependent path")
**Satisfied:** yes -- the script itself is the evidence; fracture 1 additionally carries inline
`assert` statements that fail loudly if the live `fuse_dual_cda` call ever stops reproducing G3's
cited numbers (z=6.80/2.03, fused sigma ~0.046). No separate `tests/` file was added (optional
per the handoff; the script's own assertions + DB-guard behavior were manually verified, see
Evidence below).

## Evidence

```bash
cd /c/Programs/f1-627
py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"
py scripts/tier2_fracture_analysis.py
```

```
C:\Programs\f1-627\src\physics\layer2\estimate_store.py

Tier-2 fracture quantification -- #627 gate g5
DB path: C:/Programs/f1Brainz/data/physics_estimates.db

FRACTURE 1: DUAL-CdA (PowerDrag vs Coast) -- CLOSED (cite G3, #627 gate g3)
  RBR agreement z = 6.80 -> REFUSED (disagreement_z_ge_5)
  Mercedes agreement z = 2.03 -> LEGITIMATE, fused sigma 0.0460 m^2 (18.1% tighter than
  PowerDragView alone)

FRACTURE 2: GRIP-TRIPLET cross-coupling -- BOUNDED-DEFER
  n=216 rows / 22 circuits (2023 Q, full store)
  circuit-controlled r: lateral-braking +0.053, lateral-traction -0.107, braking-traction +0.039
  bound: joint solve could tighten pooled grip sigma by AT MOST 0.6%

FRACTURE 3: a_long reconciliation -- BOUNDED-DEFER (structural, NOT re-merged)
  per-view |shift| range 0.15 sigma (best) to 13.40 sigma (worst, PowerDragView P_max Monaco)
  BOUNDED-DEFER at 13.4 sigma; cites decision:decoupled_1d_longitudinal, #523/#546, #644

FRACTURE 4: SHARED-TRAJECTORY-NOISE -- BOUNDED-DEFER
  raw r=-0.064, circuit-controlled r=-0.032 (floored at 0)
  bound: pooled grip sigma underestimated by AT MOST 0.0% (conservative proxy; genuine
  method-scoped null, cites #644 for a tighter live-perturbation number)

SUMMARY
1. DUAL-CdA                : CLOSED         -- Mercedes fused sigma 0.0460 m^2 (18.1% tighter); RBR z=6.80 REFUSED
2. GRIP-TRIPLET             : BOUNDED-DEFER  -- <= 0.6% (r_max=0.107, n=216/22 circuits)
3. a_long                  : BOUNDED-DEFER  -- <= 13.4 sigma (structural HONEST-NULL, do NOT re-merge)
4. SHARED-TRAJECTORY-NOISE  : BOUNDED-DEFER  -- <= 0.0% (conservative proxy)

exit code: 0
```

(Full untruncated output is pasted verbatim in `docs/physics/627-tier2-fractures.md`'s
"Full script output (evidence)" section.)

```bash
git status --porcelain -- data/
```
**Result:** empty (no `data/*.db` touched at any point).

DB-guard sanity check (manually run, not part of the committed evidence chain but verified):
`py scripts/tier2_fracture_analysis.py --db-path C:/nonexistent/nope.db` prints an explicit
"DB not found ... BOUNDED-DEFER" skip line for fractures 2 and 4 and exits 0 (no crash).

**Result:** pass.

## TDD evidence, if required
Not applicable (test-after per handoff; no red/green cycle -- see Test mode above).

## Docs/contracts touched
- `docs/physics/627-tier2-fractures.md` (new) -- the durable writeup this handoff requires.

## Assumptions
1. **Fracture 1 (DUAL-CdA) input numbers** are transcribed from G3's captured evidence
   (`.agent-work/627-unified-basis/g3-implement/monza_final_table.json`), not re-derived from the
   live store, because the CURRENT `data/physics_estimates.db` in main has `cross_view_covariance`
   populated as `None` on every row (the G3 fusion machinery exists in code but this particular
   snapshot of the store predates/lacks a run that persisted fused values) and
   `coast_drag_area_m2 == power_drag_area_m2` with near-zero sigma on every row (CoastView's CdA is
   pinned in production, per g3's own finding -- "production's `estimate_session()` always PINS
   Coast's CdA"). Feeding G3's own real inputs into the real `fuse_dual_cda` function reproduces
   G3's cited z/sigma numbers exactly (verified by inline `assert`), which is the strongest
   reproducibility check available without re-running g3's live session load.
2. **Fracture 2/4 grip-axis and sigma correlations** use `gp_name` (circuit) as the sole grouping
   variable for demeaning/residualization -- a circuit-fixed-effect, not a full ANCOVA with
   constructor or year effects (only one year, 2023, was in scope per the handoff).
3. **Fracture 3's numbers are transcribed, not re-measured** -- the handoff explicitly forbids
   touching the a_long path; the #523/#546 tables in the decision doc are the freshest available
   evidence and are treated as ground truth for this gate.
4. **Fracture 4's bound formula** (`sqrt(1+r) - 1`) reuses the same GLS-fusion logic pattern as
   `cross_view.fuse_dual_cda` (an equal-weight two-measurement pooling case), applied to a PROXY
   correlation (between-session own-sigma correlation) rather than a directly-measured
   within-session fit-error correlation -- explicitly flagged in the doc as conservative/upper-bound
   and structurally incapable of detecting non-overlapping-sample-set correlation.

## Stop conditions hit
None. All four fractures were closed or bounded-deferred with a real number; no fracture was left
undecided or unbounded. The a_long path was never re-wired; no production default was changed; no
`data/*.db` was written.

## Out-of-scope observations
- The main repo's `data/physics_estimates.db` does not currently have `cross_view_covariance`
  populated on any row (all `None` for the 2023 Q rows checked) despite G3's fusion machinery being
  merged -- a future gate wanting to query fused-CdA values directly from the store (rather than
  reproducing g3's captured inputs, as this gate did) will need a fresh `record_from_estimate` run
  with an independently-fit (non-pinned) CoastView to populate that column. Flagging as a triage
  candidate, not fixed here (out of this gate's scope).
- GRIP-TRIPLET's bound (0.6%) and SHARED-TRAJECTORY-NOISE's bound (0.0%, this proxy) are both
  small/near-zero on the evidence available -- neither fracture currently justifies the engineering
  cost of a joint solve or a live perturbation re-fit on its own; if #627 or a successor epic wants
  to revisit either, this doc's numbers are the baseline to beat.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff's example bound formulas (conditional-variance
  reduction for fracture 2, `sqrt(1+r)-1` for fracture 4) were directly usable as stated, which
  made the estimator-choice step fast.
- **Context rediscovered:** the current `data/physics_estimates.db`'s `cross_view_covariance`
  column being uniformly `None` (fusion not yet persisted in this store snapshot) was not flagged
  anywhere in the handoff or the x7 map -- I discovered it by querying the store directly, then
  found G3's captured JSON evidence file as the workaround. A one-line note in a future handoff
  ("the fused_cda column may be unpopulated in the current store; use g3's captured
  monza_final_table.json instead") would have saved the initial dead-end query.
- **Instructions improvised around:** none -- the handoff's allowed scope (script + doc, read-only
  on the cited modules) fit the task cleanly.
- **What would have made this easier:** nothing significant; the handoff's four close-criteria
  subsections mapped almost 1:1 onto the four plan items, which made building the gated plan fast.

## Return status
`complete`
