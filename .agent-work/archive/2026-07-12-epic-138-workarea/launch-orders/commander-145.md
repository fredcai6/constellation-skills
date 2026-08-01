# Launch Order: `commander-145 — issue #145 (three measurement arms)`

## Mission
Run https://github.com/fredcai6/constellation-skills/issues/145 — three parallel arms on the #129 eval harness measuring the merged #138 counter-doctrine: **corpus-only** / **+rail** / **+rail+hooks**. This is a MEASUREMENT mission: the deliverable is results + failure transcripts + a written kill-condition analysis, NOT a code PR. A branch/PR is needed only if the harness itself requires small fixes to run the arms (fix-now latitude below). The shrink/kill decision itself is the HUMAN's — you present evidence, never conclusions about what to delete.

## Prior-Wave Verdicts (pasted)
All five #138 implementation PRs are MERGED on main @ c9b1cf99 (648 tests passed on the merged tree):
- #148 (rail): `_rail()` in `scripts/checklist_engine.py` — five doctrine strings on claim/current/start/advance/attest/attach + REFUSED. Merged FIRST, so no commit has clamps-without-rail.
- #147 (clamps): four-clause doctrine in 5 high-exposure skills + pointer-with-force in 6; presence test `tests/test_clamp_presence.py`.
- #149 (gates): fencing-aware feedback/archive acceptance (not arm-relevant, but part of the corpus).
- #150 (hooks): `scripts/hooks/spine_rail.py` + `.claude/settings.json` (Stop refusal w/ 3-strike hatch, SessionStart resume/startup re-injection, PostToolUse binding). Live-proven headless with `--allowedTools "Bash"` (bypassPermissions is classifier-refused headless — see lesson `headless-hook-probe-allowedtools` in `.agent-work/LESSONS.md`).
- Compact-trigger is a recorded scoped null — the +hooks arm attributes nothing to compaction re-injection (spec TS6).

From the CONFIRMED spec §D6 (preregistered — do not improvise):
- **N=3 per arm for this diagnosis pass**; failure transcripts are the primary signal. Shrink/removal decisions require certification N≥8 accumulated rolling across same-corpus-hash runs — this run does NOT decide removals; it diagnoses.
- "Adds nothing measurable" = no completion-rate gain AND no shade-shift in failure transcripts, at certification N (not yours to invoke at N=3).
- Arms are NESTED (shipping question, not isolation) — state this limit in your report.
- Arms run IN PARALLEL; target ≤ ~half an hour wall-clock for the runs themselves.
- Eval `task.md` prompts: ZERO changes, zero test-awareness, zero workflow coaching. Inviolable.
- Baseline for comparison: the #129 arc's measured history (~1/3 pre-clamp → 3/3 post-clamp on commander-delegated + euler-1, N=3 per round).

## Arm construction (the one design detail delegated to you — document what you do)
Main now carries clamps+rail+hooks together, so arms are constructed by subtraction:
- **corpus-only**: sandbox corpus from a temp variant with the rail suppressed (e.g. revert the #148 commit in a scratch branch/worktree used only as the install source, or an equivalent surgical disable) — clamps intact, no hooks in the sandbox.
- **+rail**: merged corpus as-is, no hooks in the sandbox.
- **+rail+hooks**: merged corpus + hooked sandbox (the `.claude/settings.json` registrations present in the eval sandbox so hooks fire for the eval agent).
Record the exact construction (commands, corpus hashes) so arms are reproducible. If the harness's sandbox install path makes an arm impossible as specced, report the scoped null for THAT arm and run the others — do not silently redefine an arm.

## Pre-Rulings
- Eval subjects run sonnet-class per the harness defaults; `DEFAULT_MODEL` stays pinned `claude-sonnet-4-5` — do not touch.
- Same eval scenario as the #129 arc (commander-delegated + euler-1 class task) so results are comparable; note any deviation forced by the merged corpus.
- Distribution claims (e.g. "all N failures were shade X") must be derived from commands over the transcripts (grep/uniq -c), never from eyeballing summaries.
- Headless eval invocations: use non-bypass allowlists (`--allowedTools`), never bypassPermissions.
- Fenced run: stage your feedback trio via the NEW staged-feedback convention (`.agent-work/staged-feedback/issue-145/` + FENCE.md citing this order) — the merged #149 verifier accepts it; no waive should be needed.

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win. An arm that fails to run is a scoped null on that arm, not on the measurement.

## Inherited Latitude
You may: fix-now bounded harness defects blocking the arms (logged); choose arm-construction mechanics (documented). You must float: anything touching task.md, any change to what checks verify, any conclusion-shaped removal recommendation (present evidence; the human rules). No merges; if you branched harness fixes, open a PR and leave it.

## File Ownership
Sole writer of: `.agent-work/epic-138/verdicts/commander-145.md` (MAIN checkout), your results directory, and (only if needed) harness-fix commits on branch `issue-145`.

## Workspace
`C:/Programs/constellation-wt-145` — branch `issue-145`, base c9b1cf99 (merged main), created via `git worktree add ../constellation-wt-145 -b issue-145 main`.
First step, before any git operation: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-145` — must exit 0; paste output.

## Inherited Context
- Windows/py launcher conventions; UTF-8 writes; `gh pr create -F <tempfile>` if a PR is needed.
- Superpowers is a competitor — never cite or import its doctrine.
- Harness: `scripts/run_skill_eval.py`; scenarios under `evals/`; corpus install via `scripts/install_constellation.py`/`scripts/curate_corpus.py` (read them; the #129 arc drove them successfully).
- Active lessons (`.agent-work/LESSONS.md`): implementer-skill-engine-ref-path-drift; headless-hook-probe-allowedtools; gate-script-fix-cannot-self-verify (moot for you — the fixed verifier is merged and installed copies refresh from main); doctrine-restoration + amend-gap lessons (context only).
- Install the merged corpus into the sandbox fresh — do not measure stale installed copies.

## Pre-empted Steps
Understand/plan pre-empted: the measurement design is spec-frozen (§D6 pasted above); your plan step is arm-construction mechanics only.

## Data Locations
- Confirmed spec: `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`
- #129 arc methodology + prior results: repo `LAUNCH_ORDER-issue-129-continuation.md`, #136 issue comments, `.agent-work/` archives.

## Budget
- **Model tier (required):** opus (measurement orchestration; human-capped at opus or lower). Eval subjects: harness default (sonnet-class).
- **Compute/time:** arms ≤ ~30 min wall-clock in parallel; total mission ≤ 90 min. Partial results + stop condition over overrun.

## Stop Conditions
Stop and return when: an arm is unconstructible as specced, task.md purity would be violated, budget crossed, or context missing — return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict + evidence to `C:/Programs/constellation-skills/.agent-work/epic-138/verdicts/commander-145.md`: per-arm results table (N=3 each: strict-terminal-completion counts), failure-shade breakdown per arm derived from commands (paste the commands), transcript locations, arm-construction record with corpus hashes, interpretation limits (nested arms; compaction unmeasured), and the evidence the human needs for the kill-condition call — WITHOUT a removal recommendation. Isolation-check output. Deliver artifacts **before** going idle.
