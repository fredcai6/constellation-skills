# Launch Order: `commander-rail — #151`

Commanders start cold. Everything you need is pasted below.

## Mission
Fix the Stop-rail hook so it stops misattributing a subagent-claimed spine to the parent session. Deliverable: one green, reviewed PR. This is a correctness bug in the fleet-run safety rail — it false-positives on every background-wave dispatch under a hooked project dir.

**Issue #151 (verbatim):**
Field-caught minutes after #150 merged, during the epic-138 wave-2 dispatch. **What happened:** an Agent-tool subagent shares its parent session_id (x2-research fact from the #138 design pass). When the subagent ran the engine's `claim`, the PostToolUse hook wrote `binding[shared_session_id] -> subagent's spine`. The parent (Admiral) session's next turn-end was then Stop-blocked as "abandoning" a spine a different, live agent was actively driving. The sanctioned background-wave pattern (dispatch commanders, end turn, adjudicate on notification) is exactly this shape, so the false positive hits every fleet run under a hooked project dir. **What worked:** everything else — refusal wording, reconstructed `current` context, nudge accounting all behaved as designed. The defect is attribution, not mechanism.
**Design directions to evaluate (pick one, justify):**
- Make Stop compare the stopping context against the lease/binding's recorded `worktree` (already stored) — a turn-end whose project dir differs from the binding's worktree is not that spine's driver.
- Or record which transcript/agent performed the `claim` (PostToolUse payload may distinguish subagent tool calls), and only block matching stoppers.
- Or register SubagentStop for subagent turn-ends and make the plain Stop handler ignore bindings claimed under a different worktree.
- Consider whether `decide_session_start`'s `_scan_active_spine` fallback has the same misattribution shape for resume re-injection.
**Constraint (spec §D3):** the hook judges engine-journal facts only, never agent prose; the 3-strike escape hatch must survive any fix. Note the escape hatch does NOT save the parent here (the subagent makes journal progress between parent turn-ends, resetting the no-progress counter).

## Prior-Wave Verdicts (pasted)
Wave 1 merged cleanly (engine + eval fixes) into main @ 7be19cf, which is your base — no dependency on it, but you are on current main.

## Pre-Rulings (overridable with evidence)
- Pick ONE design direction and justify why over the others in your report; the worktree-comparison approach is the Admiral's weak preference (the binding already stores `worktree`) but not binding — if SubagentStop is cleaner, take it.
- The fix MUST preserve the 3-strike escape hatch and the journal-facts-only constraint (§D3). Do not make the hook read agent prose.
- Add a regression test reproducing the shared-session_id parent/subagent misattribution and proving the parent is no longer Stop-blocked while the subagent drives.

## Honest-Null Clause
A measured negative is a complete deliverable. If the misattribution is narrower or already partly mitigated, report exactly what you found with evidence.

## Inherited Latitude
Choose the design, implement, test, open the PR. FLOAT to the Admiral: any change to the §D3 journal-facts-only constraint or the escape-hatch semantics; any new issue; anything outside your file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: the Stop-rail hook source (`scripts/spine_rail.py` and/or the hook module — locate it; #150/#141 shipped the `spine_rail.py` suite) and its test file under `tests/`. Do NOT touch `scripts/checklist_engine.py`, `scripts/init_work_area.py`, `scripts/run_skill_eval.py` (other commanders own those).

## Workspace
Absolute worktree: `C:/Programs/cs-wt-rail` — branch `fix/stop-rail-attribution-151`, base `7be19cf` (current main), provisioned via `git worktree add -b fix/stop-rail-attribution-151 C:/Programs/cs-wt-rail main`.
First step: run `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-rail` — must exit 0; paste output into your report.
PR integration = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** (1) multiline `gh --body`/PR body → temp file + `gh pr create -F <file>` (heredoc and PowerShell `@'...'@` here-string both fail PS 5.1 `--body`; here-string works only for `git commit -m`). NOTE: you are in the **Bash** tool (Git Bash), where `@'...'@` is NOT a commit construct either — use a real heredoc or quoted `-m`. (2) Use `py`, not bare `python`. (3) Verify your worktree with the isolation script above.
**Active lesson `test-harness-concurrency-failsafe`:** if a test drives concurrent file I/O, wrap per-iteration work in try/except with a stop-signal in `finally` and mark helper threads `daemon=True` (a silently-dying writer hangs pytest).
**Hook architecture:** the spine_rail hooks are PostToolUse (writes binding on `claim`), Stop (blocks abandonment), SessionStart (`decide_session_start` re-injection). The binding files are `.agent-work/.spine-rail-binding.json` and `.spine-rail-nudges.json`. Read the existing `tests/` for these hooks to learn the harness before changing behavior; all pre-existing tests must stay green.

## Budget
- **Model tier (required):** opus. Subtle attribution logic in a safety rail with correctness stakes.
- **Compute/time:** bounded; checkpoint (commit WIP) and return if you near a session limit.

## Stop Conditions
Stop and return when: the fix needs a §D3 or escape-hatch change; the bug is already fixed (report the null); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Write your report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-2/W2-151-REPORT.md` BEFORE going idle: verdict, chosen design + why, evidence (regression test name + green output proving parent no longer blocked while subagent drives; full suite green), PR URL, map impact, triage candidates, workflow feedback (stage the fenced trio per doctrine and name its path — the durable root is the read-only main checkout), and your isolation-script output. Open the PR with `gh pr create -F <bodyfile>` targeting main; title `fix(hooks): Stop-rail no longer misattributes subagent spine to parent (#151)`. Post the verdict in the report, then go idle.
