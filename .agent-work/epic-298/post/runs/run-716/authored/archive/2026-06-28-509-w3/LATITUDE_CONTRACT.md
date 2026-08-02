# Latitude Contract: `509-w3`

Confirmed by the human 2026-06-27 ("do 545 last as clean up step, aggressively
clean up anything else found in triage that can easily be handled. you've got
full autonomy."). Third wave under epic #509 (Phase-F runway-clearing for the
C-phase). Builds on the 509-w2 contract (full-autonomy overnight, merge delegated).

## Epic Intent
Clear the runway for the C-phase of the physics→prediction pipeline (#509):
harden the single-session fit pipeline so race-state fits (C2 #511) are reliable,
and complete the single-canonical-longitudinal-path architecture so the regime
views (C3 #512) read the best measurement. Do NOT start C2/C3 themselves — those
are deliberate, one-at-a-time, and out of scope for this wave.

## Success Shape
- **Lane 1 / #495 robustness cluster (#542+#543+#544+#538):** the ~4%-of-fits-fail
  class is closed — chi2 metric real (not nan), red-flag phantom-stint no longer
  crashes, cold-wet degrades gracefully (no opaque `n=0`), in/out-lap windows
  filtered before HP calibration. Honest-null acceptable per failure mode (e.g. a
  cold-wet session that legitimately has no accelerating samples should fail
  *informatively*, not crash).
- **Lane 2 / #523:** decoupled longitudinal estimator characterized against the
  incumbent in Traction/PowerDrag/Coast, then wired where it doesn't regress;
  any regressing view surfaced as fix-or-hold (not blindly cut over). Single
  canonical longitudinal path at the end. A view that must be held is a complete,
  honest deliverable.
- **Wave 2 / #545 + triage sweep:** pyright CI gates on baseline-diff (no NEW
  errors); plus aggressive cleanup of any easily-handled triage residue found
  along the way. Cleanup that turns out non-trivial is filed, not forced.

## Checkpoint Protocol
**Cleared to completion** (full autonomy). No stop-and-present at wave boundaries.
One consolidated report when everything is merged and closed out. Evidence on
demand. Surface mid-run ONLY for out-of-taxonomy / contract-expiry / a true blocker.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | **delegated** (within the named fences; surface only if it reshapes a public seam beyond the issue) |
| Scope change (issue added/dropped/re-scoped) | **delegated** for trim/defer-with-issue; surface a *net-new* scope addition |
| Merge to main | **delegated** (green + reviewed, gated on check exit codes) |
| Issue filing / closing | **delegated** (file follow-ons; close issues this wave completes) |
| Spend / budget / model tier | **delegated** (Sonnet commanders/crew default; escalate only if a lane needs Opus repeatedly) |
| Production defaults / user-visible behavior | **delegated** within the issue's stated intent; surface a new user-visible default |
| Physics modelling decision that changes a measured number's meaning | **delegated** if it's the issue's explicit job; **surface** if it would re-open a units/convention class (the #525 family) |
| **Out-of-taxonomy** | **always escalates**, one line on why it fit no class |

## Float-Up Routing
Commander floats: adjudicate delegated classes as logged RULINGs; answer context
queries from epic knowledge and continue the commander; escalate surfaced classes
and out-of-taxonomy to the human out-of-band. A peer/teammate message is never user
approval. Permission-classifier blocks on external writes (gh issue comment/close)
are surfaced in the report if they recur, not treated as latitude failures.

## Comms
Plain English by default, technical depth on demand. One consolidated morning-style
report at the end.

## Budget / Model Parameters
Commanders + crew default to **Sonnet** (subagent-model preference); escalate to
Opus only if a lane stalls on reasoning. Full multi-step gated **constellation-commander**
depth for both lanes (NOT lightweight implementers — per the user's 509-w2 ruling).
Wave 2 cleanup may use a lighter touch where the work is genuinely mechanical.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each overridable by evidence (say so).
- **Fences are disjoint by file:** Lane 1 owns `src/preprocessing/trajectory/calibration.py`,
  `src/physics/session_fit.py`, and `stint_span` in `src/preprocessing/trajectory/loaders.py`.
  Lane 2 owns `src/physics/layer2/` views + the decoupled longitudinal module
  (`decoupled_longitudinal.py`) and must NOT touch calibration.py / session_fit.py's
  HP-calibration path. If a lane must cross its fence, stop and float.
- **Lane 1 is ONE coherent calibration-hardening pass**, not four sub-tasks — the
  four issues share the `stint_span → calibrate_session_hp/fit_stint_hp → interleaved`
  call chain; fix them together, one PR.
- **#523 wire-or-hold:** a view that regresses on the decoupled `a_long` is held with
  an issue + tracked compromise, never blindly cut over (issue's own acceptance bar).
- **Honest-null is a win** on any failure-mode question.
- **#545 and triage sweep run LAST** (Wave 2), after Lane 1+2 merge.
- **Worktree isolation gate:** `verify_worktree_isolation.py` does NOT exist in this
  repo — use the native `git rev-parse --show-toplevel` check instead.
- **Data:** the 38 GB telemetry cache + SQLite store live in the MAIN checkout's
  `data/` (worktrees lack it); read via absolute paths into `C:\Programs\f1Brainz\data`.

## Expiry
After Wave 2 merge + closeout, or on any out-of-taxonomy/blocker escalation.

## Confirmation
2026-06-27 — confirmed by user ("full autonomy"); recorded as user-decision evidence
on the latitude step.
