# Launch Order: implementer-105 — issue #105 (Cluster D: hygiene quick fixes)

Right-sized dispatch: implementer-with-plan, not a full Commander (small, bounded, mechanical).

## Mission
Execute issue #105: (1) delete root `manifest.json` (verified dead — nothing reads it; confirm with a repo-wide grep for "manifest.json" and paste the output before deleting); (2) delete the stray junk file at repo root named `C:Programsconstellation-skills.superpowerssdd` (a literal filename — it exists, `ls` confirms); (3) typo sweep — fix `managemetn` in the workbench skill and any other typos a targeted spell-pass over `skills/**/*.md` and `docs/*.md` finds (fix only unambiguous misspellings; never reword prose); (4) `docs/ROADMAP.md` edits: rename/reframe the "superpowers execution-discipline imports" section as constellation-native items with the deletion test, dropping the imports framing entirely; then add three new entries: (a) permanent base rigor rules + simplified charter setup — the author is the real user, rigor is worth the cost, fewer knobs; (b) canonize the issues/specs ↔ architecture interplay — deliberately deferred, the human has strong feelings; (c) interrogator finish-gate — explicit human sign-off that questioning is complete, folded into a Pocock 1.1-release evaluation. Match the ROADMAP's existing entry format and register.
Deliverable: one green PR against main.

## Pre-Rulings
- Superpowers is a competitor: the reframed ROADMAP section must not cite superpowers as authority; describing what we independently want is fine, "import from superpowers" framing is not.
- `docs/superpowers/` directory: LEAVE IT ALONE — out of scope (its removal is a separate human chore).
- If any grep shows something actually reads `manifest.json`, do NOT delete it; report the finding instead (honest null on that item).

## Honest-Null Clause
A measured negative on any item (e.g. manifest.json turns out live) is a complete deliverable for that item; report with evidence and skip the deletion.

## File Ownership
You own: `manifest.json` (deletion), the stray root file (deletion), `docs/ROADMAP.md`, typo-level edits across `skills/**/*.md` and `docs/*.md`. Fence: do NOT touch `skills/_shared/global-*.md` content, any doctrine wording, or `tests/` — a sibling (issue #102) owns those this wave. A typo fix inside a file #102 owns is allowed only if it is a pure spelling fix on a line #102's dedup moves don't touch; when in doubt, list it in your report instead of fixing.

## Workspace
Worktree: `C:\Programs\constellation-wt-105` — branch `constellation/issue-105`, base commit 2696769, created via `git worktree add ../constellation-wt-105 -b constellation/issue-105`.
First step: run `py scripts/verify_worktree_isolation.py --here C:\Programs\constellation-wt-105` from inside the worktree; must exit 0; paste output in your report. Work ONLY in this worktree. Server-side merge (the Admiral merges the PR); do not merge locally.

## Budget
- **Model tier (required):** one tier below session default is fine (mechanical work).

## Stop Conditions
Stop and return when: an item's scope exceeds this order (e.g. ROADMAP restructure beyond the named section), the test suite fails on your changes, or you need context this order doesn't cover.

## Return Shape
Final message = full report: per-item disposition (done/null + evidence: the manifest grep output, deleted file paths, typo list with file:line, ROADMAP diff summary), test-suite result if any tests reference deleted files (run `py -m pytest tests/ -x -q` and paste tail), PR URL, worktree-isolation verification output. Deliver the report as your final message BEFORE going idle.
On Windows: write the PR body to a temp file and use `gh pr create -F <file>` — never heredoc/here-string `--body`.
