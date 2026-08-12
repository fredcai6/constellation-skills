# Launch Order: `commander-grad — 3 HIGH doctrine graduations (Fred-approved)`

Commanders start cold. Everything you need is pasted/pointed below.

## Mission
Apply the THREE HIGH-confidence doctrine graduations from the epic-198-burndown lessons audit, which the human (Fred) explicitly approved for application ("accept and push the high ones"). Deliverable: one green, reviewed PR. Each is a `.md`/`.template.*` doctrine edit; the human has authorized applying them (authority=human satisfied).

**Read the exact spec + grounding for each in these MAIN-CHECKOUT read-only artifacts (see Data Locations):**
- `.agent-work/CONSTELLATION_FEEDBACK.md` entries 1 (drill-scenario-decontamination) and 3 (command-postcondition-cannot-attest).
- `.agent-work/epic-198-burndown/LESSONS_AUDIT.md` "Needs-human doctrine graduations" items 2, 4, 5 (config-ref is item 5 there).

**The three graduations:**

1. **`config-ref-absent-skill-source`** (strongest corroboration — all 4 CG crews rediscovered it). The commander plan/survey templates carry `config_ref: docs/agents/engine-config.json`, which is ABSENT in skill-source repos (like this one), so crews rediscover the inline-config convention. FIX: conditionalize / annotate the `config_ref` in the commander plan + survey templates so a skill-source worktree (no `docs/agents/engine-config.json`) is guided to inline config, AND/OR add a note to CREW_CONTEXT for skill-source worktrees. Locate the templates (`skills/commander/templates/*.json` — the plan and survey templates) and the CREW_CONTEXT home.

2. **`command-postcondition-cannot-attest`** (reproduced 3× in one run). A `command`-kind postcondition is REFUSED by `attest` (the engine runs the check during `advance`); only null/artifact conditions are attestable ahead of `advance`. FIX: reword `skills/commander/templates/EXECUTE_PLAN.template.json` gN-integrate imperative AND `skills/workbench/references/checklist-engine.md` to state that command-kind gates are satisfied by `advance` (run the check, then `advance --why`), not `attest`.

3. **`drill-scenario-decontamination`** (two fresh auditors independently hit it). A reproduction-drill scenario that pre-itemizes the divergent clauses or names the harness/fixtures makes the WEAK-doctrine (before) arm pass too, collapsing the variable under test. FIX: graduate an anti-contamination rule into the repro-drill doctrine — home is `docs/superpowers/specs/2026-07-07-lesson-repro-drills-design.md` AND/OR `skills/lessons-auditor/SKILL.md` (Reproduction drills section): "State the drill scenario positively / by-outcome; never pre-itemize or alarm-flag the failure trigger — a scenario that names what the doctrine is supposed to make the author notice passes both arms and proves nothing."

## Prior-Wave Verdicts (pasted)
Base is current main @ 8ba1293 (all epic-198 merges in). These graduations were surfaced needs-human by lessons-auditor-198 and approved by Fred at closeout acceptance.

## Pre-Rulings (overridable with evidence)
- Use the EXACT proposal text/intent from the audit artifacts — do not re-invent the doctrine; you are transcribing an approved graduation, faithfully, into the named homes.
- **Reproduction drills:** per the drill-required doctrine (itself graduated in #157), author a fail-pre/pass-post reproduction drill (fresh-context auditor, distinct from you) for a graduation WHERE a drill meaningfully proves the fix. Use judgment: graduations 1 and 2 are behavior-adjacent (a crew/agent led to the wrong action by the old text) and are drillable; graduation 3 is a meta-rule about drills. Author drills where they prove something; for any you judge pure-ceremony, say so explicitly in your report with the reason (do NOT fabricate a passing drill). Drills live under `docs/superpowers/drills/`.
- Edit `skills/_shared/*` SOURCES if any global doctrine is touched, never role `references/` install-copies. Edit shipped compact-JSON templates (EXECUTE_PLAN, plan/survey) SURGICALLY as raw text (no json.load/dump round-trip — it reflows and destroys blame); re-validate with json.load after.
- After applying each graduation, note it so the Admiral can retire the paired needs-human lesson state.

## Honest-Null Clause
If any graduation is already present in current doctrine, report where with evidence rather than duplicating it.

## Inherited Latitude
Apply the 3 edits, author drills where meaningful, open the PR. FLOAT: any edit that would touch a file's meaning beyond the approved graduation; any new issue; anything ambiguous about the intended home. Merge is the Admiral's call.

## File Ownership
Sole writer of: the commander plan/survey templates + CREW_CONTEXT (graduation 1); `skills/commander/templates/EXECUTE_PLAN.template.json` + `skills/workbench/references/checklist-engine.md` (graduation 2); `docs/superpowers/specs/2026-07-07-lesson-repro-drills-design.md` and/or `skills/lessons-auditor/SKILL.md` (graduation 3); new drill files under `docs/superpowers/drills/`. No other agent is running — the whole tree is yours, but touch ONLY the files these 3 graduations require.

## Workspace
Worktree `C:/Programs/cs-wt-grad` — branch `docs/high-graduations-198`, base `8ba1293` (current main). Provisioned via `git worktree add -b docs/high-graduations-198 C:/Programs/cs-wt-grad main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-grad` → exit 0; paste into report.
PR = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** multiline `gh --body` → temp file + `gh pr create -F <file>`; `@'...'@` is PowerShell-only, NOT a Git-Bash commit construct — real heredoc or quoted `-m`. Use `py`. Verify your worktree.
**KNOWN FRICTION (agent_work_root install-staleness):** your feedback/archive gates may resolve durable_root to the main checkout; pass `--root .` to verify_agent_feedback, or write your trio to the worktree-root `.agent-work/` and force-waive with independently-verified reasoning if it resists — Admiral-acknowledged lag, not your bug.
**Meta note:** graduation 2 (`command-postcondition-cannot-attest`) is the exact gotcha you'll hit driving your own spine — command-kind gates advance, they don't attest. You're documenting the thing you're living.
Run the suite before/after; all pre-existing tests stay green (JSON-template edits must keep `json.load` valid — a template test may cover this).

## Data Locations (main-checkout read-only inputs — your worktree lacks .agent-work/)
- `C:/Programs/constellation-skills/.agent-work/CONSTELLATION_FEEDBACK.md` (entries 1, 3 — exact proposal text + grounding).
- `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/LESSONS_AUDIT.md` (needs-human items 2, 4, 5).

## Budget
- **Model tier (required):** opus. Doctrine edits other agents obey + drill authoring.
- Checkpoint and return if you near a session limit.

## Stop Conditions
Stop and return when: a graduation's intended home is genuinely ambiguous (float); a graduation is already present (honest null); a drill can't be made fail-pre/pass-post honestly (report it, don't fabricate); or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-3/W-HIGH-graduations-REPORT.md` BEFORE going idle: per-graduation verdict (applied + where; drill result or reasoned no-drill), evidence (each edit faithful to the approved text; full suite green; templates still json.load-valid), PR URL, independent-reviewer verdict, workflow feedback (name trio path), isolation output. Open PR with `gh pr create -F <bodyfile>`; title `docs(doctrine): apply 3 HIGH graduations — config-ref, command-postcondition, drill-decontamination (epic-198)`. Post verdict, go idle.
