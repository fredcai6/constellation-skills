# Launch Order: `cmdr-461 — trajectory-grading hygiene`

Commanders start cold. Paste, don't point. **Load the `constellation-commander` skill and drive its spine end-to-end (understand → plan → execute → cleanup) through the checklist engine.** One bounded issue.

## Mission
GitHub issue **#461** — *Hygiene: trajectory-grading follow-ups from Phase 0a (#446)*. Epic #509 Phase-F. Four small, independent hygiene items consolidated from the grading-harness run. Serves the epic by hardening the offline trajectory loaders the physics-fit base reads through.

### The four items (pasted in full)
1. **Document the FastF1 `pos_data` decimetre convention** where loaders consume it (verified against Spa: 6941.6 m arc length vs official 6949.5 m).
2. **GP-name normalization:** DB uses "Belgium", FastF1 event name is "Belgian Grand Prix" — a shared normalization helper would remove per-caller mapping.
3. **FastF1 version-guard hardening** in the offline loaders.
4. **Confirm/pin the scipy dependency** introduced by the grading primitives.

None block anything. Filed under delegated issue-filing latitude in the epic-445 run.

## Prior-Wave Verdicts (pasted)
None — wave 1, independent issue. Context from the closed predecessor #446/#458 (Phase 0a grading harness): these items were the deferred low-priority residue; the decimetre convention and the Spa arc-length discrepancy (6941.6 measured vs 6949.5 official) were *already verified* there — item 1 is to **document** that fact at the seam, not re-derive it.

## Pre-Rulings
Each overridable if evidence contradicts it — say so when overriding.
- **Honest-null per item.** If any of the four is already done, OBE, or net-negative to implement, **document why and skip it** — do not invent scope to "complete" all four. A skip with a one-line rationale is a valid outcome for that item.
- **The GP-name normalizer lands in ONE shared util** (e.g. under `src/utils/` or wherever existing name mapping lives — find the current callers first), not duplicated per caller. Refuse a second copy.
- **Stay inside the loaders/util/packaging territory.** Expected files: `src/preprocessing/trajectory/loaders.py`, a shared normalization util + its callers, `pyproject.toml` (scipy pin), and any doc/docstring at the seam. **Do NOT touch `src/physics/*`** (separate parallel #525 lane) and **do NOT touch `src/preprocessing/trajectory/smoother.py`** (owned by a sibling commander this wave). If a fix needs either, STOP and float.
- Item 4: "confirm/pin scipy" means pin to the **already-installed** working version (find it via `py -m pip show scipy`), not upgrade-and-hope.

## Honest-Null Clause
A measured negative is a complete deliverable. "Item N is already handled / not worth doing because X" reported with evidence is success for that item.

## Inherited Latitude
You MAY: implement the items, commit, open the PR, file follow-up triage, and **decide per-item skip-vs-do** within the honest-null clause (log each call). Float to the Admiral: any need to touch `src/physics` or `smoother.py`, any scope growth beyond the four items, anything out-of-taxonomy. **Do NOT merge** — open the PR review-ready and return.

## File Ownership
Sole writer of `src/preprocessing/trajectory/loaders.py`, the GP-name normalization util + its callers, `pyproject.toml`, and related docs/docstrings. **Fence:** do NOT edit `smoother.py` (cmdr-504) or anything in `scripts/` (cmdr-476) or `src/physics/` (#525). Workbench under `.agent-work/cmdr-461/`.

## Workspace
Absolute worktree path: **`C:/Programs/f1Brainz-worktrees/509-461`** — branch `chore/461-trajectory-hygiene`, base `main@f40a530f`, created by the Admiral with:
`git worktree add C:/Programs/f1Brainz-worktrees/509-461 -b chore/461-trajectory-hygiene main`
**First step, before any git operation:** run `git rev-parse --show-toplevel` and confirm it resolves to `C:/Programs/f1Brainz-worktrees/509-461` (NOT `C:/Programs/f1Brainz`). Paste that into your return report as isolation evidence. (Repo ships no `verify_worktree_isolation.py`; this is the substitute.) Run all commands from the worktree root.

## Inherited Context (Active lessons + invariants — paste)
- **Python is `py`** (3.14), not `python`. Tests: `py -m pytest tests/...`. `py -m pip show scipy` to read the installed version. Run from worktree root.
- Project tenets: **one canonical path** (no dual mapping helpers), tunables/pins in config not inline, docs describe current truth at the seam (the unit convention lives where the loader consumes it, not a faraway doc).
- Evidence: `py -m src.utils.simplification_limits` on any touched `src/` path; region tests green for touched areas (`py -m pytest tests/unit/preprocessing/ -q` and any util-test path you touch).
- **Windows shell hazards:** PR body via `gh pr create -F <file>` (temp file) — never heredoc / `@'...'@ --body`. (`@'...'@` works for `git commit -m` only.)
- If you dispatch crew subagents, a completed subagent leaks cwd — `cd`/`Set-Location` back to worktree root before any git/gh.
- **Canonical-data constraint:** no live FastF1/Jolpica calls from analysis code; the version-guard (item 3) hardens the *offline* loader path, which is allowed.

## Data Locations
Mostly source/docs/packaging — minimal untracked data needed. If verifying the Spa arc-length claim, the offline cache + DBs live in the main checkout at `C:/Programs/f1Brainz/outputs/cache` and `C:/Programs/f1Brainz/data/f1_data_*.db` (read-only; do not write there). Prefer documenting the already-verified number over re-running heavy loads.

## Budget
Model tier: **Sonnet**. Bounded hygiene — no long/detached compute. Crews (if any) on Sonnet.

## Stop Conditions
Stop and return when: a fix needs `src/physics` or `smoother.py`; scope would grow beyond the four items; or you need uncovered context. Return-and-query the Admiral — asking up is sanctioned.

## Return Shape
Final report: **per-item verdict** (done / skipped-honest-null with reason) + **evidence** (touched-path `simplification_limits` PASS, relevant region tests GREEN, the pinned scipy version, where the shared normalizer landed + its callers) + **PR link** (against `main`, NOT merged) + **map impact** (new shared util? loaders doc seam?) + **triage candidates** + **workflow feedback**. Include your `git rev-parse --show-toplevel` isolation confirmation.
