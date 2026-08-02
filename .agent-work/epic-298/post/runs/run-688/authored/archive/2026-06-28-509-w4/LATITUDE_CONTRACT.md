# Latitude Contract: `509-w4`

Confirmed by the user 2026-06-27 ("spin up another wave of 546 and 549 if those don't
need guidance ... actually just treat those two as wave 4"). Carry-forward of the 509-w3
contract: **full autonomy, merge delegated, one consolidated report at the end.**

## Epic Intent
Two #509 follow-on issues from 509-w3, run as a parallel wave:
- **#546** — re-evaluate the decoupled estimator on throttle/coast (retune `sig_a_soft_throttle`,
  investigate coast filter lag), re-characterize with Config-C parity, wire-or-hold per the
  issue's acceptance bar.
- **#549** — ratchet the pyright baseline errors toward zero (groups A–I), reducing the live
  error set the #545 runtime baseline-diff gate measures against.

## Success Shape
- **#546:** if Config-C parity shifts <1σ on all three circuits with a new throttle HP (and coast
  sample loss <10%) → wire; else **honest-null** (document, stay braking-only, keep the issue's
  remainder). Honest-null is a complete deliverable.
- **#549:** as many groups fixed as cleanly possible; each fix is behaviour-preserving (type-only)
  with a green suite. Partial is fine — file/leave the hard groups; the ratchet is incremental.

## Checkpoint Protocol
**Cleared to completion** (full autonomy). One consolidated report at the end. Surface mid-run
ONLY for out-of-taxonomy / contract-expiry / a true blocker.

## Decision Classes (same as 509-w3)
| Class | Disposition |
|---|---|
| Architecture / structural | delegated within fences; surface if it reshapes a public seam |
| Scope (trim/defer-with-issue) | delegated; surface a net-new addition |
| Merge to main | delegated (green + reviewed, gated on check exit codes) |
| Issue filing/closing | delegated |
| Model tier | delegated (Sonnet default) |
| Physics modelling that changes a measured number's meaning | delegated if it's the issue's job (#546's retune IS the job); surface if it re-opens a units/convention class |
| **Out-of-taxonomy** | **always escalates**, one line on why |

## Float-Up Routing
Adjudicate delegated classes as logged RULINGs; answer context queries and continue the
commander; escalate surfaced/out-of-taxonomy to the user out-of-band. A peer message is never
user approval.

## Comms
Plain English; one consolidated report at the end.

## Budget / Model
Commanders + crew **Sonnet**, full constellation-commander depth (per the user's standing
commanders-own-multistep preference). Escalate to Opus only if a lane stalls on reasoning.

## Pre-Rulings
- **Disjoint fences by file:** #546 owns the decoupled/throttle/coast subtree
  (`decoupled_longitudinal.py`, `decoupled_calibration.py`, `decoupled_braking_input.py`,
  `session_traction.py`, `session_coast.py`, `traction_view.py`, `power_drag_view.py`,
  `coast_view.py`, `scripts/characterize_decoupled_views.py`). #549 owns the pyright errors in
  ALL OTHER files and must NOT touch #546's subtree (the ~2 errors in session_traction:142 /
  session_coast:107 are deferred to #546's lane). Disjoint → merge order irrelevant.
- **#549 stale-body correction:** the committed `pyright-baseline.json` was DROPPED in #545's
  final design (the gate computes the baseline from origin/main at CI runtime). There is NO
  baseline file to update — just fix the errors; the runtime gate registers the reduction.
- **Honest-null is a win** (esp. #546).
- **Worktree isolation:** `verify_worktree_isolation.py` does NOT exist — use native
  `git rev-parse --show-toplevel`.
- **Data:** telemetry cache + DBs live in the MAIN checkout `C:\Programs\f1Brainz\data` (absolute,
  read-only). The main checkout is on the user's `feat/541-parquet-telemetry-store` branch — do
  NOT touch it; all work in worktrees off origin/main `8a19c5bc`.

## Expiry
After Wave-4 merge + closeout, or on any out-of-taxonomy/blocker escalation.

## Confirmation
2026-06-27 — user ("treat those two as wave 4"); recorded as user-decision on the latitude step.
