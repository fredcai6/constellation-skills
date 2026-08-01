# Launch Order: `commander-init — #154`

Commanders start cold. Everything you need is pasted below.

## Mission
Two bounded script fixes. Deliverable: one green, reviewed PR. This also RESOLVES the closed duplicate #114 (same init-placeholder defect).

**Issue #154 (verbatim):**
1. **init_work_area placeholder resolution (RECURRENCE — epic-101 and epic-138, high confidence).** `init_work_area.py` leaves `<epic-id>` unresolved inside the admiral spine template's engine check *commands* (epic-138: 9 unresolved placeholders; the p2 verify_state_note check could not run and was hand-patched in place). Fix the resolver to cover check-command strings, and add a post-init assertion that no `<placeholder>` survives anywhere in the materialized spine.
2. **stage_feedback.py helper (issue-143 follow-on).** Mechanize the fenced staged trio: create `.agent-work/staged-feedback/<work-id>/` with AGENT_FEEDBACK.md, lessons-delta.json, CONSTELLATION_FEEDBACK.md, and FENCE.md (launch-order citation) in the shapes `verify_agent_feedback.py` accepts, so fenced commanders don't hand-roll it. Both #140 and #143 hand-rolled staged trios this epic; #145 followed the convention manually.

## Prior-Wave Verdicts (pasted)
Your base `d524b41` (current main) already includes all wave-1 + wave-2A merges. No dependency on them; you're on current main. Live corroboration: this very epic's commanders (corpus-id-153, cg-fastfollows-198, stop-rail-151, 152-engine-verbs) EACH hand-rolled a staged trio under `.agent-work/staged-feedback/<work-id>/` — those are your real-world shape references for the `stage_feedback.py` output (go read one, e.g. `.agent-work/staged-feedback/152-engine-verbs/`, to match the exact file shapes `verify_agent_feedback.py` accepts).

## Pre-Rulings (overridable with evidence)
- Part 1: the resolver must substitute `<epic-id>` (and any sibling placeholders like `<engine>`, `<admiral-session-id>`) inside check-command STRINGS, not just top-level fields — do it as surgical text substitution, never a JSON round-trip (round-tripping reflows the compact template and destroys blame). Re-validate with `json.load` after.
- Part 1: add the post-init assertion (no surviving `<...>` placeholder anywhere in the materialized spine) as a hard check that would have caught epic-138's 9 unresolved placeholders. Model the regression test on the existing #99/#114-class init test.
- Part 2: `stage_feedback.py` writes the four-file trio in the exact shapes `verify_agent_feedback.py --phase feedback` and `--phase archive` accept — verify by running that script against the generated dir (must pass).
- Keep both fixes in one PR; they're the same "init/feedback scripting" cluster.

## Honest-Null Clause
A measured negative is a complete deliverable. If part 1's resolver already covers check-command strings on current main (it was touched by prior fixes), report that with the exact code + a test proving it, rather than re-fixing.

## Inherited Latitude
Implement, test, open the PR. FLOAT: any change to the spine template's schema; any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `scripts/init_work_area.py`, the new `scripts/stage_feedback.py`, and their test files under `tests/`. Do NOT touch `scripts/run_skill_eval.py` (the other batch-2B commander owns it), `scripts/checklist_engine.py`, or `scripts/hooks/spine_rail.py`.

## Workspace
Absolute worktree: `C:/Programs/cs-wt-init` — branch `fix/init-placeholder-154`, base `d524b41` (current main), provisioned via `git worktree add -b fix/init-placeholder-154 C:/Programs/cs-wt-init main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-init` — must exit 0; paste output into your report.
PR integration = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** (1) multiline `gh --body`/PR body → temp file + `gh pr create -F <file>`; heredoc and `@'...'@` both fail PS 5.1 `--body`; and in the **Bash** tool (Git Bash) `@'...'@` is NOT a commit construct — use a real heredoc or quoted `git commit -m`. (2) Use `py`, not bare `python`. (3) Verify your worktree.
**Compact-JSON-template rule:** the admiral spine template is compact-format JSON — edit/resolve its text surgically, never via json.load/json.dump (reflow destroys blame); re-validate with json.load after.
**Active lesson `test-harness-concurrency-failsafe`:** concurrent-file-I/O tests need try/except + stop-signal in `finally` + `daemon=True`. (Unlikely to apply here — prefer simple tests.)
Run the existing suite before and after; all pre-existing tests stay green.

## Budget
- **Model tier (required):** sonnet. Bounded, well-specified script work with a known fix shape (documented recurrence).
- **Compute/time:** bounded; checkpoint and return if you near a session limit or if the work turns out larger/subtler than "bounded script fix" (then float to the Admiral to re-tier).

## Stop Conditions
Stop and return when: the fix needs a spine-template schema change; part 1 is already fixed on current main (report the null); the work exceeds a bounded script fix (float to re-tier); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Write your report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-2/W2-154-REPORT.md` BEFORE going idle: verdict (per part), evidence (regression test names + green output — incl. the no-surviving-placeholder assertion and the verify_agent_feedback pass against stage_feedback.py output; full suite green), PR URL, map impact, triage candidates, workflow feedback (use YOUR OWN new stage_feedback.py to stage the fenced trio if it's ready — dogfood it — else hand-roll and name the path), and your isolation-script output. Open the PR with `gh pr create -F <bodyfile>` targeting main; title `fix(scripts): init_work_area placeholder resolution in check commands + stage_feedback.py helper (#154, closes #114)`. Post the verdict, then go idle.
