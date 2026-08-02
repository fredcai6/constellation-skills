# Launch Order: `cmdr-476 — re-home orphaned physics-characterization scripts`

Commanders start cold. Paste, don't point. **Load the `constellation-commander` skill and drive its spine end-to-end (understand → plan → execute → cleanup) through the checklist engine.** One bounded issue.

## Mission
GitHub issue **#476** — *Re-home orphaned physics-characterization scripts to the new trajectory API*. Epic #509 Phase-F. From #448 cleanup (TR-1): a few physics-characterization scripts were orphaned by the windowed-estimator removal. Re-home them against the **current `src/preprocessing/trajectory/` loaders + smoother API**, or **retire** them. Serves the epic by removing dead/broken tooling and keeping characterization scripts runnable against the live API.

### What the issue says (pasted in full)
"From #448 cleanup (TR-1). A few physics-characterization scripts were orphaned by the windowed-estimator removal; re-home them against the new `src/preprocessing/trajectory/` loaders + smoother API or retire them. Parent epic #445."

## Prior-Wave Verdicts (pasted)
None — wave 1, independent issue. Context from the closed predecessor #448 (cleanup, item TR-1): the **windowed-estimator was removed**; any script that imported the old windowed-estimator entry points is now broken/orphaned. The replacement API is the `src/preprocessing/trajectory/` package (loaders such as `load_session_offline`, the smoother classes `StintSmoother`/`NSStintSmoother`). Your job is discovery + disposition, not a redesign.

## Pre-Rulings
Each overridable if evidence contradicts it — say so when overriding.
- **Discovery first.** Identify which scripts (likely under `scripts/` and possibly `scripts/physics*`/characterization paths) reference the removed windowed-estimator API or otherwise fail to import against the current trajectory API. Enumerate them with evidence (the failing import / dead reference) before changing anything.
- **Retire-vs-rehome is delegated to you, per script** (log each call): a script with **no current consumer and no characterization value** → **retire it** (delete) with a one-line rationale in the PR. A script that still has value → **re-home** it onto the current loaders/smoother API so it imports and runs (or at least imports cleanly and its entry points resolve).
- **Stay inside `scripts/` (+ any script-local docs/README).** You may *import from* `src/preprocessing/trajectory/` but **do NOT modify** `src/preprocessing/` (cmdr-504 owns `smoother.py`, cmdr-461 owns `loaders.py` this wave) and **do NOT touch `src/physics/*`** (#525 lane). If a re-home seems to need an API change in `src/`, STOP and float — that is a different issue.
- Prefer a **light** verification bar: "imports cleanly + entry points resolve against the current API" is sufficient; do not block on full heavy data runs (telemetry cache is ~36 GB and runs are slow).

## Honest-Null Clause
A measured negative is a complete deliverable. "These N scripts are all genuinely dead → retired, with rationale" is a fully successful outcome — re-homing is not required if retirement is the honest call.

## Inherited Latitude
You MAY: enumerate, re-home, **retire (delete) scripts per the pre-ruling**, commit, open the PR, file follow-up triage. Float to the Admiral: any need to modify `src/` (loaders/smoother/physics), any scope growth, anything out-of-taxonomy. **Do NOT merge** — open the PR review-ready and return.

## File Ownership
Sole writer under `scripts/` this wave. **Fence:** do NOT edit `src/preprocessing/` (cmdr-504/cmdr-461) or `src/physics/` (#525). Workbench under `.agent-work/cmdr-476/`.

## Workspace
Absolute worktree path: **`C:/Programs/f1Brainz-worktrees/509-476`** — branch `cleanup/476-rehome-scripts`, base `main@f40a530f`, created by the Admiral with:
`git worktree add C:/Programs/f1Brainz-worktrees/509-476 -b cleanup/476-rehome-scripts main`
**First step, before any git operation:** run `git rev-parse --show-toplevel` and confirm it resolves to `C:/Programs/f1Brainz-worktrees/509-476` (NOT `C:/Programs/f1Brainz`). Paste that into your return report as isolation evidence. (Repo ships no `verify_worktree_isolation.py`; this is the substitute.) Run all commands from the worktree root.

## Inherited Context (Active lessons + invariants — paste)
- **Python is `py`** (3.14), not `python`. Run scripts as `py scripts/<name>.py` or `py -m ...` from the worktree root.
- To detect orphaned imports: try importing/compiling each candidate (`py -m py_compile scripts/<f>.py`, or attempt the import) and grep for references to the removed windowed-estimator API.
- Project tenets: **one canonical path**, no dead/dual code left behind; deleting genuinely dead tooling is *preferred* over keeping it on life support. Notebooks/scripts are scratch — convert real value into runnable form or retire.
- Evidence: any `src/`-touching path would need `simplification_limits` — but you should not be touching `src/`. For scripts, the bar is "imports/compiles cleanly against the current API."
- **Windows shell hazards:** PR body via `gh pr create -F <file>` (temp file) — never heredoc / `@'...'@ --body`.
- If you dispatch crew subagents, a completed subagent leaks cwd — `cd`/`Set-Location` back to worktree root before any git/gh.

## Data Locations
Heavy runs are out of scope. If you want to smoke-test a re-homed script beyond import, the untracked offline cache + DBs are in the main checkout at `C:/Programs/f1Brainz/outputs/cache` and `C:/Programs/f1Brainz/data/f1_data_*.db` (read-only; do not write there). Prefer import/entry-point resolution over full execution.

## Budget
Model tier: **Sonnet**. Bounded cleanup — no long/detached compute. Crews (if any) on Sonnet.

## Stop Conditions
Stop and return when: a re-home needs an `src/` change; scope would grow; or you need uncovered context. Return-and-query the Admiral — asking up is sanctioned.

## Return Shape
Final report: **verdict** with a **per-script disposition table** (script → re-homed / retired / kept-as-is, + one-line rationale + evidence of the orphaning) + **evidence** (each re-homed script imports/compiles cleanly against the current API) + **PR link** (against `main`, NOT merged) + **map impact** (scripts deleted/moved) + **triage candidates** + **workflow feedback**. Include your `git rev-parse --show-toplevel` isolation confirmation.
