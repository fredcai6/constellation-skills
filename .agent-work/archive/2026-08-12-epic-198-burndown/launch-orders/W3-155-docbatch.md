# Launch Order: `commander-docs — #155`

Commanders start cold. Everything you need is pasted below.

## Mission
A small, bounded doc/doctrine batch graduated from the epic-138 audit. Deliverable: one green, reviewed PR.

**Issue #155 (verbatim checklist):**
- [ ] `skills/_shared/windows.md`: add the headless-probe recipe — `claude -p ... --allowedTools "Bash"` (non-bypass allowlist); `--dangerously-skip-permissions`/bypassPermissions is classifier-refused headless; plain `claude -p` fires SessionStart/Stop but cannot run a tool for PostToolUse. (lesson headless-hook-probe-allowedtools, grounded #141)
- [ ] `skills/implementer/SKILL.md`: fix the engine reference pointer — actual installed path is `skills/workbench/references/checklist-engine.md`, not `references/checklist-engine.md`; audit sibling role skills for the same drift. (lesson implementer-skill-engine-ref-path-drift, grounded #140)
- [ ] `docs/CHECKLIST_ENGINE_DESIGN.md`: document the `_rail()` doctrine-rail surface (decision-point strings, refusal-path trigger, canonicality). (issue-140 tc1)
- [ ] Harvest ergonomics: stamp the epic id in a consistent position on each harvested AGENT_FEEDBACK entry so "all entries for an epic" is a grep, not a scroll (auditor's artifact-gap note).
- [ ] LOW-CONFIDENCE, human review before acting: state-note-precondition framing — **DEFER this one** (needs human review; the Admiral has ruled it out of scope for this autonomous run). Note it as a triage candidate, do NOT edit it.

## Prior-Wave Verdicts (pasted)
Base is current main (see Workspace) — includes all epic-198 merges so far. Note: `skills/workbench/references/checklist-engine.md` is the correct engine-reference path (confirmed this epic).

## Pre-Rulings (overridable with evidence)
- `windows.md`: positive-recipe form (working command first, failure mode second), matching the file's existing style. Edit the SOURCE `skills/_shared/windows.md`, NOT a role's `references/windows.md` install-copy.
- implementer engine-ref: fix the pointer in `skills/implementer/SKILL.md`, then grep all `skills/*/SKILL.md` for the same `references/checklist-engine.md` drift and fix each occurrence (the audit is part of the deliverable). These are role SKILL.md sources (canonical), safe to edit.
- Harvest epic-id stamp: this is a doc/convention note (where the epic id goes in an AGENT_FEEDBACK entry) — if it implies a code change to a harvest/feedback script, that is OUT of scope; keep it a documented convention in the owning doc (e.g. the feedback template or RECURSIVE_IMPROVEMENT_DESIGN.md — but do NOT touch RECURSIVE_IMPROVEMENT_DESIGN.md §5.5, just added by #118; add elsewhere or note as triage if no clean home).
- DEFER the state-note-precondition item (triage note only).

## Honest-Null Clause
A measured negative is a complete deliverable. If any item is already present on current main, report where, with evidence, rather than re-adding.

## Inherited Latitude
Make the doc edits, open the PR. FLOAT: any item that would need a code change beyond docs; the deferred state-note item if you think it shouldn't defer; any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `skills/_shared/windows.md`, `skills/implementer/SKILL.md` and any sibling `skills/*/SKILL.md` with the engine-ref drift, `docs/CHECKLIST_ENGINE_DESIGN.md`. Do NOT touch `scripts/curate_corpus.py` (the other 3C commander owns it), `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (just edited by #118), `docs/CHECKLIST_SCHEMA.md`, or any template.

## Workspace
Worktree `C:/Programs/cs-wt-docs` — branch `docs/doctrine-batch-155`, base `1f3417f` (current main). Provisioned via `git worktree add -b docs/doctrine-batch-155 C:/Programs/cs-wt-docs main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-docs` → exit 0; paste into report.
PR = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** multiline `gh --body` → temp file + `gh pr create -F <file>`; `@'...'@` is PowerShell-only, NOT a Git-Bash commit construct — real heredoc or quoted `-m`. Use `py`. Verify your worktree.
**KNOWN FRICTION (agent_work_root staleness):** the INSTALLED constellation-commander bundle's `agent_work_root.py` is stale vs main (missing #118's epic-lease fix), so your `verify_agent_feedback`/`archive` gates may resolve durable_root to the main checkout instead of worktree-local. Workaround: pass `--root .` to verify_agent_feedback, OR write your trio to the worktree-root `.agent-work/` and if the gate still resists, force-waive with reasoning (independently verified) — this is a known, Admiral-acknowledged environment lag, not your bug. Do NOT edit agent_work_root.py (out of fence).
**Doctrine-source rule:** edit `skills/_shared/*` SOURCES, never role `references/` install-copies.
Run the suite before/after; all pre-existing tests stay green (mostly doc-only, so likely no test delta).

## Budget
- **Model tier (required):** sonnet. Bounded doc edits against established files.
- Checkpoint and return if you near a session limit.

## Stop Conditions
Stop and return when: an item needs a code change beyond docs (float it); an item is already present (report the null); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-3/W3-155-REPORT.md` BEFORE going idle: verdict (per item, incl. the deferred one noted as triage), evidence (the sibling-SKILL audit result — which files had the drift; full suite green), PR URL, map impact, triage candidates, workflow feedback (name trio path), isolation output. Open PR with `gh pr create -F <bodyfile>`; title `docs(doctrine): epic-138 graduations — windows headless-probe, engine-ref path, _rail surface (#155)`. Post verdict, go idle.
