# Launch Order: commander-103 — issue #103 (Cluster B: per-skill diets, MINUS commander)

Commanders start cold. Paste, don't point.

## Mission
Execute issue #103 (cluster B per-skill diets) **excluding the commander move** — the commander diet is re-scoped to the sibling running issue #107 (commander entry-split), because both restructure `skills/commander/` and one writer owns a file per wave. Your scope, from the spec section in issue #103:
1. **Admiral diet:** the 12-bullet "learned from field fleets" list in `skills/admiral/SKILL.md` folds into `skills/admiral/references/fleet-doctrine.md`; inline keeps only bullets that are genuine deltas not already there. Reconcile-then-cut (wordings may have drifted; post-#108 some bullets already moved to `_shared/global-orchestrator.md` — check current state first).
2. **Docent:** extract the self-contained-HTML constraint block from `skills/docent/SKILL.md` to a docent reference; body keeps the method.
3. **History-to-current-truth sweep** over all `skills/**/*.md` EXCEPT `skills/commander/**` (sibling owns it): rewrite "is now engine-enforced", "learned from field fleets", PR-number asides, and similar historical framing as timeless current truth. Meaning-preserving; the rule stays, its origin story goes (origin stories that carry operative content move to a reference or the lessons file, not deleted silently — list them in your report).
4. **Interrogator register rewrite:** `skills/interrogator/SKILL.md` stays ONE skill (~490 words, do not split, do not bloat): rewrite in place so agent-loaded prose leads and the human-direct case is a brief mode note. Preserve all doctrine.
Deliverable: green, reviewed PR with before/after word counts per touched skill (command-derived).

## Prior-Wave Verdicts (pasted)
Wave 1 (PR #108, merged, main=c25c4a6): cluster A single-sourcing landed. Boilerplate/engine-string/banners/scoped-nulls/world-verification/delegate-not-replacement now live in `_shared/global-everyone.md`; unchanged-tree + crew-idle in `_shared/global-orchestrator.md`; sibling-ids single-homed in lessons-auditor; carriers hold one-line pointers. Regression net: content-pin tests + no-residual-duplicate test now in tests/test_install_constellation.py — your edits MUST NOT reintroduce retired inline doctrine signatures (the residual test will fail) and must not remove the pointer lines' shared-file names.
PR #109 (issue #105 hygiene, merged or merging imminently): deletes root manifest.json, reframes docs/ROADMAP.md, fixes workbench "managemetn" typo. Do not touch docs/ROADMAP.md; rebase onto latest origin/main before opening your PR.

## Pre-Rulings
- One writer per file: you own `skills/admiral/`, `skills/docent/`, `skills/interrogator/`, and the history sweep everywhere EXCEPT `skills/commander/**` (sibling #107) — hard fence.
- Rebase onto latest origin/main immediately before opening the PR; if #109 landed, its workbench/ROADMAP changes are upstream — never revert them.
- Register rule (binding): rule-plus-why, one clause of reason; emphatic register only at rationalization-prone gates with a mechanical check behind them.
- No new `global-*.md` filenames (test glob pins bundle composition). New role references (docent) live under that skill's `references/` and must not match `global-*.md`.
- If a "learned from field fleets" bullet duplicates what #108 already moved to `_shared/global-orchestrator.md`, the inline bullet is CUT (pointer already exists) — do not fold it into fleet-doctrine.md too.
- Superpowers is a competitor: never cite or import its doctrine.
- Source repo (`skills/`) is authority; never edit installed copies.

## Honest-Null Clause
A sweep item or fold that proves semantically load-bearing where it is (cutting would lose operative content) is skipped-and-reported per item — a complete deliverable.

## Inherited Latitude
You decide: wording, reference file naming/placement within a skill, commit structure. Float to Admiral: any doctrine whose home seems wrong, scope beyond the four items, anything touching `skills/commander/**` or `_shared/` content beyond pointer lines.

## File Ownership
Yours: `skills/admiral/**`, `skills/docent/**`, `skills/interrogator/**`, history-sweep line edits across `skills/**/*.md` except commander. Fences: NOT `skills/commander/**`, NOT `docs/ROADMAP.md`, NOT `tests/` (unless a content-pin test's source line legitimately moves — then update surgically and say so), NOT `_shared/` beyond what a fold explicitly requires (float first). Findings: `.agent-work/issue-103/` INSIDE your worktree (worktree-local; Admiral harvests — never write main-checkout canonical LESSONS.md/AGENT_FEEDBACK.md).

## Workspace
Worktree: `C:\Programs\constellation-wt-103` — branch `constellation/issue-103`, base c25c4a6, created via `git worktree add ../constellation-wt-103 -b constellation/issue-103`.
First step: `py scripts/verify_worktree_isolation.py --here C:\Programs\constellation-wt-103` (forward slashes if backslashes mangle) — must exit 0; paste output in report. Server-side merge is the Admiral's; never merge locally.

## Inherited Context
Active lessons binding this mission:
- Dogfooding divergence: drive your engine from THE REPO'S OWN commander templates/scripts, not the installed copies.
- Plan-scope completeness: execute.json needs one gate per file/decision-class in scope.
- Doc-only gates: use inspection-attestation evidence (quoted before/after + grep output), not test-shaped proxies.
- Under-epic durable writes: stage feedback/lessons worktree-local for harvest.
- Baseline reconcile at understand: post-#108 state may already cover parts of your items (esp. admiral bullets) — re-scope against actual code, and a narrower genuine gap is the real mission.
- If your rewrite invalidates an existing test scenario, name it explicitly in the handoff.
- Never round-trip shipped JSON templates through json.load/dump; surgical text edits only.
- Review artifacts all under `.agent-work/issue-103/crew-handoffs/<gate>-review/`.
- Any crew you spawn must be told to deliver its full report as its final message before idling.
- Counts (words, carriers) are command-derived with pasted output, never impressions.

## Pre-empted Steps
None — full spine. The issue body pre-answers most understand questions; cite it.

## Data Locations
All inputs tracked. Epic work area (read-only): `C:\Programs\constellation-skills\.agent-work\epic-101\`.

## Budget
- **Model tier (required):** inherit session model (register-sensitive prose across many files). Crew may run one tier down.
- Single session target; ship completed items + explicit continuation note if the window runs short.

## Stop Conditions
Stop and return when: an item requires touching commander or _shared beyond pointers; suite has pre-existing failures on your base; or you need context this order doesn't cover. Asking up is always sanctioned.

## Return Shape
Final message = full report: per-item disposition (+ evidence: quoted before/after snippets, word counts, sweep list with file:line), suite result (command + tail), PR URL, isolation output, map impact, triage candidates, workflow feedback. Deliver BEFORE going idle. PR body via `gh pr create -F <tempfile>`, never --body heredoc.
