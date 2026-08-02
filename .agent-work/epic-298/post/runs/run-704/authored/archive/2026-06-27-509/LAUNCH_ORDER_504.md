# Launch Order: `cmdr-504 — split smoother.py`

Commanders start cold. Paste, don't point. **Load the `constellation-commander` skill and drive its spine end-to-end (understand → plan → execute → cleanup) through the checklist engine.** This is one bounded issue.

## Mission
GitHub issue **#504** — *cleanup: split `src/preprocessing/trajectory/smoother.py` (exceeds verify_simplification_limits)*. Part of epic #509 Phase-F (foundation hardening). Deliverable: `smoother.py` split into cohesive modules so the file and its `fit`/`__init__` methods pass `verify_simplification_limits`, with **zero behavior change**. Serves the epic by removing review-risk/maintenance-erosion debt on the trajectory filter that the whole physics-fit base depends on.

### What the issue says (pasted in full)
- **Problem:** `smoother.py` exceeds the project `verify_simplification_limits` ceiling. This is the **exit condition for a tracked compromise** accepted during #498 (commander Option B): violations were NOT refactored in-gate to protect the byte-identical guarantee on the most sensitive methods (`fit`/`__init__`).
- **Current truth:** PRE-EXISTING (HEAD before #498): `file_lines` 1043 > 1000. After #498 (Student-t jerk prior + kind=3 channel): `file_lines` 1140; `__init__` cyclomatic 21 (limit <20); `fit` cyclomatic 26 (<20) + function_lines 118 (<100).
- **Suggested scope:** split into cohesive modules — e.g. SDE/state-layout, the forward/backward Kalman-RTS core, the IRLS reweighting (for both `nu` observations and `nu_proc` jerk process), the query accessors — so the file and `fit`/`__init__` pass.
- **Non-goals:** No behavior change. No public API change. The byte-identical Gaussian path AND the #498 `nu_proc`/`kind=3` semantics must be preserved exactly.
- **Acceptance criteria:**
  - [ ] `py -m src.utils.simplification_limits` PASSES on `src/preprocessing/trajectory/smoother.py`.
  - [ ] `py -m pytest tests/unit/preprocessing/trajectory/ -q` GREEN (E4 nesting / byte-identical preserved).
  - [ ] No public API change (`StintSmoother`/`NSStintSmoother` signatures + behavior unchanged).

## Prior-Wave Verdicts (pasted)
None — wave 1, independent issue. Context you need from the closed predecessor #498: the byte-identical guarantee on `fit`/`__init__` was the *reason* the split was deferred; honor it. The Gaussian path must produce identical bytes; the `nu`/`nu_proc`/`kind=3` (Student-t observation + jerk-process) machinery must be semantically unchanged.

## Pre-Rulings
Each overridable if evidence contradicts it — say so when overriding.
- **Public API is frozen.** `StintSmoother` and `NSStintSmoother` class names, constructor signatures, public method signatures, and behavior must be unchanged. If a clean split is impossible without an API change, **STOP and float to the Admiral** — do not change the API on your own authority.
- **Stay inside `src/preprocessing/trajectory/`** (+ its tests). **Do NOT touch `src/physics/*`** — that is the lane of a separate parallel effort (#525 units audit); touching it causes a collision. If a fix seems to need a `src/physics` change, STOP and float.
- This is a **mechanical refactor**, not a logic change: the simplification-limits ceiling is met by *moving cohesive units into new modules*, not by rewriting algorithms. Prefer extracting: SDE/state-layout, Kalman-RTS forward/backward core, IRLS reweighting, query accessors.
- Verify byte-identity empirically if a test exists for it; if none does, that is itself worth noting (and the region suite is your guard).

## Honest-Null Clause
A measured negative is a complete deliverable. If the split cannot meet the limits without an API or behavior change, that finding — with evidence — is a valid return; float it rather than forcing a bad change.

## Inherited Latitude
You MAY: plan and execute the refactor, create the branch's commits, open the PR, file follow-up triage. You must **float to the Admiral** (do not decide yourself): any public-API change, any need to touch `src/physics`, any scope change, or anything out-of-taxonomy. **Do NOT merge** your PR — open it review-ready and return; the Admiral merges at the wave checkpoint.

## File Ownership
Sole writer of everything under `src/preprocessing/trajectory/` and `tests/unit/preprocessing/trajectory/` this wave. Your local findings/workbench files live under `.agent-work/cmdr-504/` in your worktree. No shared-file fences with the other two commanders (they own `loaders.py`/util/`pyproject` and `scripts/` respectively — disjoint).

## Workspace
Absolute worktree path: **`C:/Programs/f1Brainz-worktrees/509-504`** — branch `cleanup/504-split-smoother`, base `main@f40a530f`, created by the Admiral with:
`git worktree add C:/Programs/f1Brainz-worktrees/509-504 -b cleanup/504-split-smoother main`
**First step, before any git operation:** run `git rev-parse --show-toplevel` and confirm it resolves to `C:/Programs/f1Brainz-worktrees/509-504` (NOT `C:/Programs/f1Brainz`). Paste that output into your return report as your isolation evidence. (The repo does not ship `verify_worktree_isolation.py`; this native check is its substitute.) Run all commands from the worktree root.

## Inherited Context (Active lessons + invariants — paste)
- **Python is `py`** (Python Launcher, 3.14), not `python`. Tests: `py -m pytest tests/...`. Run from repo (worktree) root.
- Evidence requirement (project doctrine): `py -m src.utils.simplification_limits` on touched paths is **strict**; "plan file splits when approaching limits" is exactly this issue.
- **Windows shell hazards:** when you open the PR, write the body to a temp file and use `gh pr create -F <file>` — NOT a bash heredoc and NOT a PowerShell `@'...'@` here-string `--body` (both fail for PR bodies; here-strings work for `git commit -m` only).
- If you dispatch crew subagents, a completed subagent leaks its cwd into the shell — `Set-Location` (or `cd`) back to the worktree root before any git/gh call.
- Refuse compatibility shims/dual paths (project tenet) — a split must leave **one** canonical implementation, not a shim + original.

## Data Locations
This refactor needs no untracked data — tests + simplification_limits are source-only. If a test fixture is missing in the worktree, the main checkout is at `C:/Programs/f1Brainz` (do not write there).

## Budget
Model tier: **Sonnet**. This is a bounded mechanical refactor — no long/detached compute. Keep crews (if any) on Sonnet.

## Stop Conditions
Stop and return when: the public API would have to change; a fix would require touching `src/physics`; scope exceeds "split for limits + zero behavior change"; or you need context this order doesn't cover. Return-and-query the Admiral — asking up is always sanctioned.

## Return Shape
Final report: **verdict** (done / blocked / honest-null) + **evidence** (the two acceptance commands' output: `simplification_limits` PASS on the file, `pytest tests/unit/preprocessing/trajectory/ -q` GREEN; confirmation the public API is unchanged) + **PR link** (opened against `main`, NOT merged) + **map impact** (new module files added under the trajectory package) + **triage candidates** + **workflow feedback**. Include your `git rev-parse --show-toplevel` isolation confirmation as evidence.
