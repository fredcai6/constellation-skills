# Launch Order: cmdr-604d — #604 race-week command, SEAM DESIGN ONLY

## Mission
Issue #604 (epic #601, Track 1), **design phase only**. Produce the design-it-twice seam decision for a single `race-week` command that will (later) chain: collect FP sessions → `sampled-runtime` predict → lineup optimizer → emit (a) one submittable ranked top-10 and (b) a race-preview explainer. **You do NOT build the command this wave.** Your deliverable is a seam-decision document comparing 3+ independent interface designs and recommending one. The build is Wave 2, gated on the Admiral getting the human to ratify your recommended seam (it is an architecture/structural decision = surfaced). This serves the epic by settling the interface BEFORE the Friday Belgium data path is wired (critic IF4: the seam decision must precede any wiring).

## Prior-Wave Verdicts (pasted)
None — Wave 1.

## Pre-Rulings
Each overridable if evidence contradicts — say so when overriding.
- **Design-it-twice: at least 3 genuinely independent designs.** The named axis is *wraps-existing-CLI (a thin orchestrator shelling/calling the existing subcommands) vs a new first-class orchestrator module vs a hybrid*. Compare on: reuse vs duplication, testability, how cleanly each handles the sprint-weekend evidence shape, error/partial-data handling (FP sessions land incrementally Fri/Sat), and how the explainer (soft deliverable) attaches.
- **Sprint-aware, not FP1/FP2/FP3-hardcoded.** 2026 has 6 sprint weekends; the pre-quali evidence set differs (e.g. FP1 + Sprint Quali + Sprint, not FP1/FP2/FP3). The seam must not bake in the conventional 3-FP shape. State how each design discovers the actual available sessions.
- **Gate split (carry into the design):** the ranked top-10 list is the HARD deliverable (must emit a submittable list from Friday FP data before quali lock); the explainer is SOFT (an unfinished explainer does not fail the shakedown). Design so the list can ship even if the explainer is stubbed.
- **Balanced beam lane is the deliberate default** lineup lane (revisitable after the future decomposition study); the emitted report must state which lane produced the list. Design the seam to make the lane a named, swappable parameter.
- **Verify every reused seam from source** before citing it (signature, return type, who else consumes it). Do not design against from-memory signatures.

## Honest-Null Clause
If the comparison decisively shows one design dominates (e.g. wrapping the existing CLI is clearly right and a new module is over-engineering), a crisp "designs 2–3 considered and rejected because X" is a complete, successful deliverable — design-it-twice requires the alternatives be genuinely explored, not that the winner be exotic.

## Inherited Latitude
You MAY: read across the repo, write your design doc within your fence, self-review, open a PR for the doc (push+PR pre-cleared). You MUST FLOAT: any build/wiring of the actual command (explicitly out of scope this wave); touching files outside your fence; the seam recommendation itself is surfaced — present it, do not treat it as ratified. You cannot reach the human; report seam trade-offs up to the Admiral.

## File Ownership
**Sole writer this wave of: one new design doc** — propose its committed home (recommend `docs/design/race_week_seam.md`; create the `docs/design/` dir if absent). No source (`src/`) or script changes this wave. Report file: `.agent-work/601-fantasy-league/cmdr-604d-report.md` (main checkout, absolute path, not committed on branch).

## Workspace
Worktree: `C:/Programs/f1Brainz/.claude/worktrees/604-seam` — branch `feat/604-race-week-seam`, base `5e8e92d7`. Created via `git worktree add .claude/worktrees/604-seam -b feat/604-race-week-seam 5e8e92d7`.
First step, before any git op: `py scripts/verify_worktree_isolation.py --here C:/Programs/f1Brainz/.claude/worktrees/604-seam` — must exit 0; paste output into your report.
PR integration = server-side merge.

## Inherited Context
- **Python is `py`, never `python`.** The DB is the single source of truth for analysis; collection is the ONLY place live FastF1 calls are allowed (relevant to how the `collect` stage fits the seam).
- **Existing pieces the command will wrap (verify each from source):**
  - Collection: `scripts/collect_evo_data.py` (CLI: `--seasons`, `--sessions`, `--gp <single GP>`, `--include-telemetry`, `--dry-run`, rate-limit aware; no `--rounds` arg).
  - Prediction: `py -m src.evo_predictor.run sampled-predict --year <y> --race <name> [--manifest ...] [--output ...]` (see `src/evo_predictor/run.py:792` `_add_sampled_predict_parser` / `cmd_sampled_predict`).
  - Lineup optimizer + scoring: `src/fantasy_scoring/` — `beam_search.py`, `lineup_evaluator.py`, `scoring_rules.py` (ScoringCalculator), `expected_assignment.py`, `season.py`. The "balanced lane" lives in the beam search.
- **Never commit `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md` or your work area on the branch.** PR contains only the design doc.
- **Windows PR bodies:** `gh pr create -F <file>`.

## Pre-empted Steps
Intent + scope established here. Run your commander spine; treat "execute" as producing + self-critiquing the design doc (there is no code gate this wave). You may cite this order rather than re-interrogating intent.

## Data Locations
Read-only inspection of `src/`, `scripts/` in your worktree. Canonical DBs (untracked in worktree) are at `C:/Programs/f1Brainz/data/f1_data_2026.db` — you do not need to run predictions this wave, only design the seam.

## Budget
- **Model tier:** Sonnet.
- Compute/time: single-session; this is design work, no long compute.

## Stop Conditions
Stop and return when: the seam-decision doc is written (3+ designs compared + recommendation) + reviewed + PR open. Do NOT proceed to build the command — that is Wave 2. Stop earlier if you need context this order doesn't cover.

## Return Shape
Final report (`.agent-work/601-fantasy-league/cmdr-604d-report.md`, main checkout; post verdict before idle): verdict, PR URL for the design doc, a crisp statement of the **recommended seam** + the 2+ rejected alternatives with reasons (this is what the Admiral surfaces to the human for ratification), the verified signatures of every reused seam, `verify_worktree_isolation.py --here` output, triage candidates, workflow feedback, proposed lessons-delta (do not apply). Deliver the artifact before going idle.
