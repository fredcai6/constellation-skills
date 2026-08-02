# Review Result — G3 separation (f_tyre vs g_track), issue #511 W3

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3` — issue #511 W3 tyre-age capstone: the subtle separation (per-compound tyre decay
`f_tyre(compound, age)` vs within-weekend track evolution `g_track`).

## Result
`APPROVE`

Survey driven through the engine (`.agent-work/511/g3-review/review.json`): all 13 checks
recorded pass; consolidated verdict=APPROVE. Every load-bearing claim was verified
independently (re-run / code-path read / AST scan / independent probe), not trusted from the
implementer paste.

## Handoff compliance
PASS. Implements exactly the crossed log-grip separation the handoff specified:
`grip_axis = car_envelope(driver→constructor, gp)[quali, relative] + f_tyre(base + decay k)
+ g_track(gp, cumulative_track_laps) + noise`. Season-pooled per-compound `k` via
`pooling.pool_random_effects` with a structural-only monotone prior; per-circuit `g_track`
slope partial-pooled; identifiability + leave-one-circuit-out LOO reported. Per-axis vector
delivered: lateral_mech (primary), lateral_aero (honest-null), traction (speculative). Stop
conditions (evo import / baked #443 magnitudes / race-refit car / self-inclusive LOO /
trivial planted test / W2-pooling-store mutation / committed .db) — none hit.

## Scope drift
PASS. `git status`: only the two allowed new files (`src/physics/layer2/tyre_separation.py`,
`tests/unit/physics/layer2/test_tyre_separation.py`) plus the `.agent-work/511/` work area are
untracked. No tracked-file modifications. HEAD is the unrelated G1 commit (`race_stint_batch`),
untouched. `pooling.py`, the stores, the W2 modules, and the quali path are all unmodified
(read-only consumption only). No `.db` written or committed.

## Evidence verdict
PASS. Re-ran independently in the worktree:
- `py -m pytest tests/unit/physics/layer2/test_tyre_separation.py -q` → **9 passed in 0.26s**.
- `py -m src.utils.simplification_limits --paths …` → **PASS (2 files checked)** (<1000 lines,
  functions <100, CC <20).
- Independent AST import scan → imports are
  `__future__, dataclasses, json, numpy, pandas, sqlite3, src.physics.layer2.pooling, typing` —
  no evo region.
Test mode `test-after` is appropriate: the load-bearing test is the planted-recovery synthetic,
which is behavior-focused (recovers known truth) rather than asserting implementation detail.

## Code/doc quality
PASS. Minimal, composable, well-documented. Canonical DBs opened strictly read-only
(`file:…?mode=ro`); `RaceStintStore` (write-mode `__init__`) is never instantiated. Honest-null
returned visibly (coverage below `MIN_STINTS`, `lateral_aero`, traction level) rather than
faked. Structural-only prior (precision-weighted PAVA isotonic + non-negativity). Units
explicit (per-100-track-laps scaling; log vs linear space declared per axis). Tunables are
named module constants, not inline magic numbers. No module-level mutable state; no DB query
caching.

## Map impact verdict
- **Evidence supports claimed change:** Yes. The 9 passing tests + real-data smoke + my
  independent probes back the "lateral decay axis separates cleanly, fresh-grip base does not"
  finding. The expected honest finding (compound signal lives in decay `k`, not the age-0 base)
  is corroborated by the anti-circular probe.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored (AST-verified);
  `lesson:loo-residual-diagnostic-over-self-weighted-predictor` honored (LOO is genuinely
  leave-one-circuit-out); structural-only / anti-circular line held.
- **Notes match the diff:** Yes. New leaf `struct:physics.layer2/tyre_separation.py` consuming
  the `pooling.py` seam read-only; `purpose:physics_utilization` measured-not-wired Phase-C
  output. No overstated or missing structural/capability impact.
- **Decision candidates surfaced:** Yes. The net-new within-weekend `g_track` pooling structure
  (per-circuit slope on `cumulative_track_laps`, partial-pooled) is surfaced as a decision
  candidate routed to `decision:regime_readiness_rubric` (#512) / Cartographer — not silently
  adopted.
- **Durable context routed:** Yes. Triage candidates (fresh-grip base non-separation;
  traction-level honest-null → #557 territory) are routed, not dropped.

## Reconciliation check
No silent architecture divergence. The new `g_track` term is a genuine new pooling structure
and is correctly flagged as a decision candidate for Cartographer reconcile rather than treated
as settled architecture. No committed schema/contract changed (result dataclasses are the
module's own internal API surface).

## Load-bearing check findings (independently verified)
1. **ANTI-CIRCULAR (the critical check) — HOLDS.** Default `prior=None`: `_blend_prior` returns
   pooled values unchanged; `_apply_structural` applies ONLY the monotone PAVA ladder +
   non-negativity (both structural). `StructuralPrior` defaults are empty dicts → zero baked
   magnitude. No `#443`/SOFT/MED/HARD `k` constants in source (grep clean; the only `#443`
   mention is the docstring stating none are used). **Independent probe:** planting two
   different k-ladders (A 0.001/0.0025/0.004; B 0.003/0.006/0.009) produced two different
   default outputs that TRACK the data (A→0.00104/0.00242/0.00408; B→0.00304/0.00592/0.00908),
   proving the default bakes no fixed magnitude; an injected tight prior moved HARD
   0.00104→0.01584. The injectable hook is live but fires only when explicitly injected.
2. **evo-free — PASS.** AST scan clean (above).
3. **car_envelope from QUALI — PASS.** Reads `physics_estimates.db` `session_estimates`
   (`session_type='Q'`), maps driver→constructor via the decoded `drivers` JSON list, centres
   per-constructor `lateral_mech_grip_g` per GP (relative), and **subtracts** it from race grip
   (`y = base − car_rel`) — never re-fit from race; absolute quali-vs-race level is absorbed by
   the per-circuit intercept.
4. **LOO discipline — PASS.** `tr = frame[gp != g]` excludes the held-out circuit; base/k/track
   are re-pooled on training folds only; k-stability std is across folds; OOS residuals predict
   the held-out circuit with out-of-fold base+slope, fitting only the unknowable per-circuit
   intercept in-fold (legitimate — it cannot be borrowed). Genuinely out-of-sample.
5. **planted-recovery — PASS.** Non-trivial planted base/k/track with car deliberately
   confounded into compound and pit-stagger overlap; tolerances are load-bearing (k abs 0.0008
   ≈ half the ladder spacing). `test_car_removal_beats_naive` proves the car anchor is not
   decorative.
6. **g_track genuine — PASS.** Real per-circuit slope on centred `cumulative_track_laps`
   (distinct design column), partial-pooled; thin circuits (Mexico, n<10) flagged and shrunk to
   the pooled mean. Not a constant, not a relabeled tyre term.
7. **Re-run / simplification / clean git — PASS** (see Evidence verdict).

## Blockers
- none

## Out-of-scope observations
- **Fresh-grip base does not separate by compound** — expected, honest, anti-circular result
  (compound signal lives in decay `k`, not the age-0 level); explicitly NOT a blocker per the
  handoff. Phase-P should carry the per-compound `k` vector, not a fresh-grip base.
- **Traction level is honest-null** (~66% residual variance); decay ladder holds but the level
  does not → `traction_a0` fit quality is #557 territory. Triage candidate.
- The net-new `g_track` within-weekend pooling structure is a decision candidate for
  Cartographer / `decision:regime_readiness_rubric` (#512).

## Workflow Feedback
- **Handoff gaps:** The handoff said the G3 files are "untracked — read directly" and gave
  `git diff -- <file>` as an inspection step; for an untracked file that diff is empty, so the
  instruction is mildly self-contradictory. Minor — the handoff also said to read the file
  directly, which is what works.
- **Context rediscovered:** The store-read nuance (`RaceStintStore.__init__` runs
  `CREATE TABLE IF NOT EXISTS`, i.e. opens write-mode, so the implementer used a `mode=ro`
  SELECT helper) was pre-blessed in the handoff reviewer notes — that note saved a verification
  pass and was accurate. No rediscovery cost beyond confirming the store is never instantiated.
- **Instructions improvised around:** none — the survey template plus the handoff's explicit
  load-bearing-check list mapped cleanly onto appended engine checks (a1–a7).
- **What would have made this easier:** none — confirmed after review: the handoff's
  load-bearing-check enumeration, the pre-blessed `mode=ro` note, and the "base-non-separation
  is expected" steer were exactly the three things that would otherwise have cost time, and all
  three were already present.

## Return status
`complete`
