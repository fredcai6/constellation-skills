# Launch Order: commander-107 — issue #107 (Cluster F: commander entry-split) + cluster B's commander diet

Commanders start cold. Paste, don't point.

## Mission
Execute issue #107 (commander entry-split) PLUS the commander-diet move re-scoped from issue #103 (both restructure `skills/commander/`; you are its sole writer this wave). From the spec sections (issues #107 and #103 bodies):
1. **Entry-split (F):** `constellation-commander` becomes two entry-only skills over a joint core reference:
   - `skills/commander/SKILL.md` (human entry): thin — precise third-person description (with exclusion clause "not for delegated/launch-order dispatch"), the human-principal binding (live human: ask and wait), pointer into the core.
   - New delegated entry skill (e.g. `skills/commander-delegated/SKILL.md`): thin — description carries "do NOT use when a human is driving" + the admiral-confusable exclusion ("runs ONE issue under a frozen LAUNCH_ORDER; for running an EPIC as the human's delegate use constellation-admiral"), the frozen-principal binding (cite the launch order and proceed; genuine gaps go up), pointer into the same core.
   - Core: `skills/commander/references/commander-core.md` — the full role doctrine written mode-neutral against "your principal". Single source; the two entries carry NO competing doctrine.
   - Update `skills/commander/SKILL.md` description AND the admiral's description if needed so the confusable-pair exclusion clauses exist BOTH ways (commander-delegated ↔ admiral).
2. **Commander diet (B's commander move):** while building the core, the ~250-word crew-backend paragraph and kin move to a commander reference (or `_shared/windows.md` where platform-generic); the entry SKILL.md files stay trigger + spine map + pointers. Apply the history-to-current-truth sweep to all commander text you rewrite (timeless present, no PR-number asides).
3. **Install mechanics:** wire the new skill into `install_constellation.py` (bundle map entry for the delegated entry; core reference must ship to BOTH entries — per-skill bundle map entry or cross-skill absolute-path pointer, precedent: every role points at workbench's checklist-engine.md). The core reference must NOT match `global-*.md` (test glob pins bundle composition). Update SKILL_INDEX.md. Add install tests for the new skill modeled on existing per-skill tests.
4. **Manual fresh-context selection check (F's acceptance, binding):** after the split, run a cold-agent check — spawn a fresh subagent given ONLY the skill descriptions (all constellation skills' frontmatter descriptions) and three invocation contexts (a human driving an issue; a LAUNCH_ORDER delegated dispatch; an epic to run) — it must name commander / commander-delegated / admiral respectively. Paste the transcript excerpt as gate evidence. If selection fails, iterate the descriptions and re-run.
Deliverable: green, reviewed PR; before/after word counts for commander surface (command-derived).

## Prior-Wave Verdicts (pasted)
Wave 1 (PR #108, merged, main=c25c4a6): cluster A landed. Commander SKILL.md already shrank 2580→2452 words: compliance boilerplate, engine-string detail, banners, world-verification, unchanged-tree, crew-idle, delegate-not-replacement, design-it-twice restatements are GONE — now in `_shared/global-everyone.md` / `_shared/global-orchestrator.md` with one-line pointers. Build the core from the POST-#108 commander text. The regression net (content-pin + no-residual tests in tests/test_install_constellation.py) must stay green: do not reintroduce retired inline doctrine signatures; keep pointer lines naming the shared files.
PR #109 (issue #105, merged or merging imminently): manifest.json deleted, ROADMAP reframed, workbench typo. Rebase onto latest origin/main before opening your PR; never revert its changes.

## Pre-Rulings
- Interrogator is NOT split (it gets a register rewrite under #103 — sibling owns `skills/interrogator/`). The split pattern is documented once as a convention; commander is its only instance today — do not build generalized apparatus beyond commander's own split.
- Templates remain the shared interface, unchanged (`skills/commander/templates/` stays where it is; both entries reference it).
- Existing installed-skill name `constellation-commander` keeps the HUMAN entry (least surprise for the human who types it). The delegated entry is the new name.
- Descriptions: third-person, what + when-to-use, never procedure; exclusion clauses ONLY for the confusable pairs named in the spec.
- No new `global-*.md` filenames. Bundle-glob tests must stay green.
- The Admiral's own SKILL.md is sibling #103's file this wave EXCEPT its frontmatter description line: if the admiral-side exclusion clause requires editing `skills/admiral/SKILL.md`'s description, make that ONE surgical frontmatter-line edit, flag it loudly in your PR body and report (fence exception, granted here), and touch nothing else in that file.
- Superpowers is a competitor: never cite or import its doctrine.
- Source repo is authority; never edit installed copies (the manual selection check uses descriptions read from YOUR WORKTREE's files, not installed skills).

## Honest-Null Clause
If the selection check keeps failing after honest description iteration, ship the split with the failure documented and the best descriptions achieved — a measured negative on selection is a reportable deliverable; the Admiral routes it.

## Inherited Latitude
You decide: the delegated entry's exact name (recommend `constellation-commander-delegated`), core reference structure/TOC, which commander paragraphs are platform-generic vs role-specific, test naming. Float to Admiral: any change to admiral doctrine beyond the one description line, any bundle-map change affecting OTHER skills' bundles, scope beyond commander split + diet.

## File Ownership
Yours: `skills/commander/**`, new `skills/commander-delegated/**` (or chosen name), `install_constellation.py` (scripts/ path — locate it), `SKILL_INDEX.md`, `tests/test_install_constellation.py` (additions + surgical updates), plus the single admiral description line (flagged exception). Fences: NOT `skills/admiral/**` otherwise, NOT `skills/interrogator/**`, `skills/docent/**`, NOT `docs/ROADMAP.md`, NOT `_shared/` content beyond what the diet move explicitly requires for `windows.md` (float first if unsure). Findings: `.agent-work/issue-107/` INSIDE your worktree; never write main-checkout canonical LESSONS/AGENT_FEEDBACK.

## Workspace
Worktree: `C:\Programs\constellation-wt-107` — branch `constellation/issue-107`, base c25c4a6, created via `git worktree add ../constellation-wt-107 -b constellation/issue-107`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-107` (forward slashes — backslash args mangle in the Bash tool) — must exit 0; paste output. Server-side merge is the Admiral's; never merge locally.

## Inherited Context
Active lessons binding this mission:
- Dogfooding divergence: drive your engine from THE REPO'S OWN commander templates/scripts, not installed copies.
- Plan-scope completeness: one execute.json gate per file/decision-class in scope (this mission has many: split, diet, installer, index, tests, selection check — gate each).
- Doc-only gates: inspection-attestation evidence (quoted before/after + grep), not test proxies.
- Under-epic durable writes: stage feedback/lessons worktree-local for harvest.
- Baseline reconcile at understand: post-#108 commander is thinner than the spec's 2,580-word snapshot; re-scope the diet against actual text.
- New tracked files are untracked until staged: "git diff shows N-1 files; new files appear in git status" — say so in evidence.
- If your restructure invalidates an existing test scenario (e.g. a test reading commander SKILL.md content), name it explicitly.
- Never round-trip shipped JSON templates through json.load/dump; surgical text edits only.
- Review artifacts under `.agent-work/issue-107/crew-handoffs/<gate>-review/`.
- Any crew you spawn must deliver its full report as its final message before idling.
- Counts command-derived with pasted output.

## Pre-empted Steps
None — full spine. Issue bodies (#107 + #103's commander paragraph) pre-answer most understand questions; cite them.

## Data Locations
All inputs tracked. Epic work area (read-only): `C:\Programs\constellation-skills\.agent-work\epic-101\`.

## Budget
- **Model tier (required):** inherit session model (highest-judgment cluster: descriptions steer live skill selection). Crew may run one tier down; the selection-check cold agent SHOULD run one tier down (selection must work for cheaper models too).
- Single session target; if short, ship the split green and return the selection-check as continuation.

## Stop Conditions
Stop and return when: the bundle-glob constraint cannot be satisfied for the core reference; the split forces changes in sibling-owned files beyond the granted description line; suite pre-broken on base; or context gaps. Asking up is always sanctioned.

## Return Shape
Final message = full report: split summary (files created/changed, word counts before/after), installer/index/test changes, selection-check transcript excerpt + verdict, suite result (command + tail), PR URL, isolation output, map impact, triage candidates, workflow feedback. Deliver BEFORE going idle. PR body via `gh pr create -F <tempfile>`, never --body heredoc.
