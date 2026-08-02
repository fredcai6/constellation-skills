# Launch Order: `cmdr-P — #549 pyright baseline ratchet`

Commanders start cold. Paste, don't point. **Run the FULL `constellation-commander` gated spine**
(understand → plan → implement → review → integrate). Multi-step commander (user preference).

## Mission
Ratchet the pyright baseline error set toward zero with **behaviour-preserving, type-only** fixes.
#545 (509-w3) wired a pyright baseline-diff CI gate; ~71 pre-existing errors remain, grouped A–I below.
Fix as many groups as cleanly possible; each fix must be type-only (no behaviour change) with a green
test suite. Partial is fine — the ratchet is incremental; leave/file the genuinely hard ones.

## CRITICAL — #549's body is STALE on one point (verified):
The committed `pyright-baseline.json` was **DROPPED** in #545's final design. The CI gate computes the
baseline from `origin/main` at CI runtime (in-job) and fails only on NEW errors. **There is NO baseline
file to update.** Ignore the #549 body's "update pyright-baseline.json / --update flag" instructions —
just FIX the errors; the runtime gate will register the reduction automatically (it reports "fixed"
errors). Confirm the gate mechanism from `.github/workflows/typecheck.yml` + `scripts/pyright_baseline_diff.py`
(both on your base, origin/main `8a19c5bc`) before relying on it.

## Prior-Wave Verdicts (pasted) — the 71 errors, grouped

- **A (9):** `src/physics/layer2/session_estimator.py` L124–L153 — `reportOptionalMemberAccess`/`reportArgumentType`.
  `braking=traction=power_drag=None` at L110 then accessed in the loop without None guards (`View.fit()`→Optional).
  Fix: explicit None guards after the loop (raise/continue).
- **B (11):** `src/physics/layer2/session_braking.py` L156–L161 — pandas `Series.__getitem__`→`Scalar` not narrowed.
  Fix: explicit float/int casts at extraction, or annotate the local.
- **C (20):** `src/physics/utilization/characterize.py` L316–L342 — `argparse.Namespace` attrs `int|str|None`.
  Fix: type assertions/casts after `parse_args()` or a typed dataclass.
- **D (8):** `src/preprocessing/trajectory/smoother.py` L201–L647 — Optional member access on smoother state.
  Fix: investigate; likely Optional-narrowing guards.
- **E (7):** `src/physics/parameter_estimator.py` L199–L263 — `float|None` in arithmetic/typed calls. None guards.
- **F (2):** `src/preprocessing/trajectory/calibration.py` L791, L945 — `reportReturnType` (tuple shape mismatch:
  `_fit_nonstationary_core` returns `NSStintSmoother | None`). Fix the return annotation.
- **G (4):** `src/physics/ribbon.py` L388–L506 — `object` lacks FastF1 attrs (`car_data`/`laps`). Annotate the
  session param with the FastF1 type or `Any`.
- **H (3):** `src/physics/terrain.py` L383/405/430 — `from scipy.spatial import cKDTree` unknown in stubs. Use
  `KDTree` (modern scipy) or a scoped `# type: ignore`.
- **I (6, misc):** `capability_envelope.py:133`, `control_alignment.py:107`, `scoreboard.py:266`,
  `session_lateral.py:103`, `sim_evaluator.py:243` — **AND** `session_coast.py:107` + `session_traction.py:142`
  which are OUT OF YOUR FENCE (see below) — leave those two to cmdr-T.

## Pre-Rulings (overridable with stated evidence)
- **Type-only, behaviour-preserving.** No runtime/logic change. If a "fix" would alter behaviour (e.g. a None
  guard that changes control flow in a way that matters), prefer a precise type annotation/cast/assert; if a
  genuine logic change is needed, that's a real bug → file it, leave the error in the set, don't force it.
- **Group-by-group; verify after each:** run the suite + `py -m pyright` after each group; confirm the count
  drops and nothing regresses. A green suite is the proof of behaviour-preservation.
- **`# type: ignore` is a last resort** — prefer a real annotation/cast; if used, scope it narrowly with a reason.
- Partial completion is fine — file a follow-on for any group you don't finish.

## Honest-Null Clause
"Group X can't be fixed type-only without a logic change" (with the evidence + a filed issue) is a complete
outcome for that group. Don't force a behaviour change to silence a type error.

## Inherited Latitude
MAY (delegated): all type-only fixes in your fence, filing follow-ons for hard groups. MUST float: any fix that
needs a runtime/behaviour change (surface it as a bug, don't ship it as a type fix); editing OUTSIDE your fence.

## File Ownership
**Sole writer for the pyright-error files EXCEPT cmdr-T's subtree.** You own: session_estimator.py,
session_braking.py, characterize.py, smoother.py, parameter_estimator.py, calibration.py, ribbon.py,
terrain.py, capability_envelope.py, control_alignment.py, scoreboard.py, session_lateral.py, sim_evaluator.py
(+ new tests if needed). **Do NOT touch** `session_traction.py`, `session_coast.py`, `decoupled_longitudinal.py`,
`decoupled_calibration.py`, `decoupled_braking_input.py`, `traction_view.py`, `power_drag_view.py`, `coast_view.py`
— those are cmdr-T's (#546); their pyright errors (session_traction:142, session_coast:107) are deferred to
cmdr-T. Float if you think you must cross.
Findings file: `C:\Programs\f1Brainz-509w4\.agent-work\509-w4\crew-handoffs\cmdr-P-findings.md` (sole writer).

## Workspace
Worktree provisioned: `C:\Programs\f1Brainz-509w4-pyright` (branch `chore/509w4-pyright-ratchet`, base origin/main `8a19c5bc`).
Created: `git worktree add -b chore/509w4-pyright-ratchet ../f1Brainz-509w4-pyright origin/main`.
First, before any git op: run `git -C "C:\Programs\f1Brainz-509w4-pyright" rev-parse --show-toplevel`
(verify_worktree_isolation.py does NOT exist); must return your worktree path. Paste it in your report.

## Inherited Context
- **py-launcher:** `py` not `python`; tests `py -m pytest`; locally `py -m pyright`.
- **ci-gate-selftest-in-ci-environment (NEW):** pyright error sets differ Windows/py3.14 (local) vs ubuntu/py3.11
  (CI). Your local count may differ from CI's — what matters is that your PR ADDS no new errors and the CI gate
  (runtime base-diff vs origin/main) is GREEN on your PR. Verify green in CI before declaring done.
- **shared-files-not-on-mission-branch:** do NOT COMMIT `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md`/
  `CONSTELLATION_FEEDBACK.md`; writing AGENT_FEEDBACK on disk (uncommitted) for your feedback step is fine; do
  NOT run `apply_lessons_delta.py` — return `lessons-delta.json` in your report.
- **state-note-before-detach; crew-idle-strands-deliverable; run-crew via Agent tool; handoff-cite-exact-seam.**
Invariants: <1000 lines/file; PR body via temp file + `gh pr create -F` (never heredoc).

## Data Locations
None needed (type-only fixes). All `src/` code is in your worktree.

## Budget
**Sonnet**, full commander depth. Bounded; group-by-group.

## Stop Conditions
Stop/return when: a fix needs a behaviour change (float as a bug); a fix needs to cross into cmdr-T's fence;
a decision outside inherited latitude; or missing context.

## Return Shape
Which groups FIXED (per-group error delta) + which LEFT (+ issues filed for hard ones) + final pyright error
count (local) + confirmation the CI baseline-diff gate is GREEN on your PR + suite-green evidence + the
`rev-parse --show-toplevel` isolation output + map impact (expected NONE) + workflow feedback/lesson candidates
(returned, not applied). Open ONE PR (`gh pr create -F <tempfile>`, title referencing #549 + "Refs #545 #509";
do NOT write `Closes #549` unless you fix ALL groups — otherwise reference it and note the remainder), required
checks green, do NOT merge (Admiral merges). Commit trailers: `Co-Authored-By: Claude Opus 4.8
<noreply@anthropic.com>` + `Claude-Session: https://claude.ai/code/session_01Pg84miea8Tmz2egJrGg2S4`;
PR footer `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
