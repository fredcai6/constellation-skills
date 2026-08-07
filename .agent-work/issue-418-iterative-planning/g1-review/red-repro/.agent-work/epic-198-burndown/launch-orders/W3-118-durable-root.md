# Launch Order: `commander-durable — #118 (+ stage_feedback doc)`

Commanders start cold. Everything you need is pasted below.

## Mission
Land the epic-101 template/doctrine deltas AND the epic's most-recurred mechanism gap (durable-root resolution). Deliverable: one green, reviewed PR.

**Issue #118 (verbatim):**
1. `IMPLEMENTER_HANDOFF.template.md`: (a) name the self-check-budget vs content-coverage tension; (b) authoring rule: dry-run any verbatim SKILL.md prose against the residual-guard signature list before dispatch.
2. `LATITUDE_CONTRACT.template.md` (Budget section): usage-limit budget line — treat the account session pool as a wave-sizing input; defer next-wave dispatch past a limit reset rather than launching into it.
3. `skills/curator/SKILL.md`: fold the two-sided-acceptance pattern (detector-self-confirmation guard: own run + independent fresh-context sweep) and the broad-first dedup-move sequencing note into curator doctrine.
4. **Durable-trio under-epic gap (the epic's most-recurred mechanism gap):** `verify_agent_feedback`/`verify_lessons_applied`/`agent_work_root` resolve to the MAIN checkout that under-epic launch orders fence; all four worktree commanders force-waived c1s. Fix direction: spine postconditions pass `--root .` (or `agent_work_root` honors the worktree under an active epic lease).

**Live corroboration:** in THIS epic (epic-198-burndown), every commander (corpus-id-153, cg-fastfollows-198, stop-rail-151, 152-engine-verbs, 154-init-placeholder, runner-durability-130) hit item 4 — each STAGED its feedback trio worktree-locally because the durable root pointed at the read-only main checkout. That staging is now mechanized by `scripts/stage_feedback.py` (shipped in #154, PR #203). Item 4 is the complementary fix: make the durable-root resolution itself worktree-aware under an active epic lease, so the trio can be verified/written without the fence dance.

**Also (Admiral-assigned doc debt):** `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (~L443, the staging section) should now NAME `scripts/stage_feedback.py` as the tool that produces the fenced staged trio (it existed only as hand-rolled convention before #154).

## Prior-Wave Verdicts (pasted)
Base `0f354ed` (current main) includes #154/PR #203 which shipped `scripts/stage_feedback.py` (the trio-staging tool) and the init_work_area resolver generalization. Read `scripts/stage_feedback.py` and `.agent-work/staged-feedback/152-engine-verbs/` to understand the trio shape before touching item 4.

## Pre-Rulings (overridable with evidence)
- Item 4 is the priority — it's a real mechanism fix with heavy recurrence. Prefer `agent_work_root` honoring the worktree under an active epic lease (so the fix is transparent to every caller) over threading `--root .` through every spine postcondition, unless the lease-detection is too fragile — justify your choice. Add a test: under a simulated worktree + active epic lease, agent_work_root/verify_agent_feedback resolve to the worktree, not the main checkout.
- Items 1–3 are bounded doctrine edits — make them faithfully; do NOT paraphrase-drift the existing doctrine voice.
- Edit shipped compact-JSON templates (if any) surgically (no json.load/dump round-trip); re-validate after. The .template.md files are markdown, edit normally.

## Honest-Null Clause
A measured negative is a complete deliverable. If item 4 was already partly fixed on current main (agent_work_root was touched recently), report exactly what resolves where, with evidence, and fix only the residual.

## Inherited Latitude
Implement, test, open the PR. FLOAT: any change to the lease model or the fence contract beyond root-resolution; any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `scripts/agent_work_root.py`, `scripts/verify_agent_feedback.py`, `scripts/verify_lessons_applied.py` (item 4 + their tests); `IMPLEMENTER_HANDOFF.template.md`, `LATITUDE_CONTRACT.template.md`, `skills/curator/SKILL.md` (items 1–3); `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (doc debt). Do NOT touch `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/stage_feedback.py` (read-only), `skills/implementer/SKILL.md` or `skills/admiral/SKILL.md` (other wave-3 commanders own those).

## Workspace
Worktree `C:/Programs/cs-wt-durable` — branch `fix/durable-root-118`, base `0f354ed`. Provisioned via `git worktree add -b fix/durable-root-118 C:/Programs/cs-wt-durable main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-durable` → exit 0; paste into report.
PR = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** multiline `gh --body` → temp file + `gh pr create -F <file>`; `@'...'@` is PowerShell-only and NOT a Git-Bash commit construct — use a real heredoc or quoted `-m`. Use `py`. Verify your worktree.
**Git-common-dir note (relevant to item 4):** worktrees share a git common dir; agent_work_root's current resolution is what points the durable root at the main checkout. The intended behavior under an active epic lease is worktree-local.
**Active lesson `test-harness-concurrency-failsafe`:** concurrent-file-I/O tests need try/except + stop-signal in `finally` + `daemon=True`.
Run the suite before/after; all pre-existing tests stay green.

## Budget
- **Model tier (required):** opus. Item 4 is a load-bearing mechanism fix across the feedback/verify path with recurrence history.
- Checkpoint and return if you near a session limit.

## Stop Conditions
Stop and return when: item 4 needs a lease/fence-contract change beyond root resolution (float first); a piece is already fixed (report the null); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-3/W3-118-REPORT.md` BEFORE going idle: verdict (per item), evidence (item-4 worktree-resolution test + green output; full suite green; the doctrine edits faithful to voice), PR URL, map impact, triage candidates, workflow feedback (stage fenced trio — dogfood stage_feedback.py; name path), isolation output. Open PR with `gh pr create -F <bodyfile>`; title `fix(scripts+doctrine): worktree-aware durable-root + epic-101 template deltas (#118)`. Post verdict, go idle.
