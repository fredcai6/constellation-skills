# Launch Order: cmdr-602 — #602 mission consolidation

## Mission
Issue #602 (epic #601, design D1). Two edits: (1) consolidate the project mission statement into `AGENTS.md`; (2) fix `CLAUDE.md`'s stale `evo_predictor` description (it still documents the retired 24-parameter vector / `scorer.py` / `ranker.py` path). Deliverable = both files updated, reviewed, PR opened. This serves the epic by making "win the fantasy league live in 2026" the stated north star every future agent reads first, and by stopping agents from being misled by a dead-architecture description.

## Prior-Wave Verdicts (pasted)
None — this is Wave 1 of the chunk.

## Pre-Rulings
Each overridable if evidence contradicts — say so when overriding.
- **Verify the live architecture from source before writing it.** Do NOT copy the issue's prose blindly — confirm `src/evo_predictor/sampled_runtime.py` exists and that the "3-stage sampled race-weekend simulator over 12 neural latent-power modules, Bradley-Terry field solve + precision-weighted fusion" description matches the actual code. Replacing a stale description with a newly-inaccurate one is a failure. Cite the real module/function names you verified.
- **Mission statement content** (AGENTS.md): the project produces a race-performance prediction capable of **winning the owner's ~20-player F1 fantasy league, live during 2026**. Scoring = per-player pre-qualifying predicted top-10, scored by delta-sum (|predicted−actual| per pick, lower better) + a progressive bingo deduction for exact hits. Bar: league winners average ~674 pts/season (~26–31 pts/race over ~24 rounds); the current model's leakage-free walk-forward equivalent is ~853 → the model must find ~7.5 pts/race vs its current self. **Metric regime:** decision metric = model's own fantasy pts/race scored against ACTUAL race results (self-contained, no league data needed); league placement = an INFORMATIONAL overlay only, never gates development. Co-pilot loop: one `race-week` command emits a submittable ranked top-10 + an interrogable race-preview explainer. Secondary goal: physics-derived explainers (why cars are fast, season trends) are first-class outputs (substack horizon 2027).
- **No other doc should claim a different mission** — if you find one, note it in your report (do not edit files outside your fence to fix it; float it).
- Keep AGENTS.md tight; it is a bootstrap file, not an essay.

## Honest-Null Clause
N/A for a docs task, but: if the live-architecture verification reveals the issue's description is itself wrong in some respect, report that finding rather than encoding a guess.

## Inherited Latitude
You MAY: edit within your fence, self-review, open a PR (push+PR pre-cleared this wave). You must FLOAT to the Admiral: any need to touch a file outside your fence, any scope change, closing the issue (Admiral surfaces close to the human), merging (human decision). Report `user-decision`-class questions up — you cannot reach the human directly.

## File Ownership
**Sole writer this wave of: `AGENTS.md` and `CLAUDE.md` only.** No other files. Your findings/report file: `.agent-work/601-fantasy-league/cmdr-602-report.md` (write it in the MAIN checkout path via absolute path, OR return it inline — it is NOT committed on your branch; see shared-files rule below).

## Workspace
Worktree: `C:/Programs/f1Brainz/.claude/worktrees/602-mission` — branch `feat/602-mission-consolidation`, base `5e8e92d7` (current origin/main). Created via `git worktree add .claude/worktrees/602-mission -b feat/602-mission-consolidation 5e8e92d7`.
First step, before any git op: run `py scripts/verify_worktree_isolation.py --here C:/Programs/f1Brainz/.claude/worktrees/602-mission` — must exit 0; paste its output into your report.
PR integration defaults to server-side merge (do not local-merge).

## Inherited Context
- **Python is `py`, never `python`** (Python Launcher; Python 3.14).
- **Never commit `.agent-work/LESSONS.md`, `AGENT_FEEDBACK.md`, `CONSTELLATION_FEEDBACK.md`, or your own `.agent-work/<id>/` work area on the mission branch** (`lesson:shared-files-not-on-mission-branch`). Return your lessons-delta/feedback in the closeout report; the Admiral applies them centrally. Your PR must contain ONLY `AGENTS.md` + `CLAUDE.md`.
- **Windows PR bodies:** write the body to a temp file and `gh pr create -F <file>` — never a heredoc or PowerShell here-string `--body`.
- Docs-change evidence bar (ORCHESTRATOR_CONTEXT): reviewer checks correct repo/domain, valid commands, existing references, current workflow; add `Last verified` if `docs/DOCUMENTATION.md` requires it for the section you touch.
- Live architecture facts to verify: `src/evo_predictor/sampled_runtime.py` (3-stage sampled runtime), 12 neural latent-power modules under `src/latent_power/`, Bradley-Terry field solve + precision-weighted fusion. The retired path being replaced: 24-param vector, `src/evo_predictor/scorer.py`, `ranker.py`.

## Pre-empted Steps
Context is established by this launch order (epic intent, the two edits, the verified-architecture requirement). Run your full commander spine (understand → plan → execute → cleanup) but you may cite this order rather than re-interrogating intent.

## Data Locations
None needed (docs only). Untracked inputs live in the main checkout at `C:/Programs/f1Brainz/`; your worktree lacks them.

## Budget
- **Model tier:** Sonnet.
- Compute/time: small; single-session.

## Stop Conditions
Stop and return when: the two files are edited + reviewed + PR open; OR you need to touch a file outside your fence; OR you find a genuine architecture ambiguity you cannot resolve from source. Asking up is always sanctioned.

## Return Shape
Final report (write `.agent-work/601-fantasy-league/cmdr-602-report.md` in the main checkout via absolute path, AND post verdict before going idle): verdict (DONE/BLOCKED), the PR URL, the exact live-architecture module/function names you verified, `verify_worktree_isolation.py --here` output, any triage candidates, workflow feedback (friction/what-worked), and your proposed lessons-delta entries (do NOT apply them). Deliver the artifact before going idle — an idle notification with no artifact reads as stalled.
