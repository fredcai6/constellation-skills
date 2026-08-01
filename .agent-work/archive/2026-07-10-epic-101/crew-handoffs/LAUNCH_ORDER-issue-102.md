# Launch Order: commander-102 — issue #102 (Cluster A: single-sourcing dedup + content-pin regression net)

Commanders start cold. Paste, don't point.

## Mission
Execute issue #102 end to end: the 10 single-sourcing dedup moves from epic #101's cluster A, plus the mechanical regression net (per-doctrine content-pin tests + no-residual-duplicate test). The issue body on GitHub (#102) contains the full authoritative spec section — read it first; it is self-contained (moves table, constraints, cross-cutting conventions, testing pathways). Deliverable: a green, reviewed PR against main implementing all safe moves, with per-move grep evidence (before/after carrier counts) pasted into the gate evidence, and before/after per-skill word counts in the PR body.

## Prior-Wave Verdicts (pasted)
None — this is wave 1. Relevant verified facts from the epic's exploration (c2-x2 excursion, already confirmed against code, do not re-verify from scratch):
- `install_constellation.py` `SKILL_REFERENCE_BUNDLES` (lines ~98–113) bundles `skills/_shared/` files per tier (EVERYONE/ORCHESTRATOR/CREW/ALL_TIERS).
- Tests pin bundle sets via a `global-*.md` filename glob (tests/test_install_constellation.py:196–208): **never create a new `global-*.md` filename** — append into existing bucket files only.
- Exactly one content-pin test exists today (deep-module vocabulary, test_install_constellation.py:679–690) — model your new per-doctrine content-pin tests on it.
- The inline doctrine copies HAVE drifted between carriers. Every move is reconcile-then-cut: reconcile the wording first, confirm the carrier list by grep against the final wording, then cut.

## Pre-Rulings
Ruled in advance, each overridable if evidence contradicts it — say so when overriding.
- Destination buckets are fixed by the spec's moves table (pasted in issue #102). Cross-tier doctrines go to `_shared/global-everyone.md`; orchestrator-only to `_shared/global-orchestrator.md`; "FOLLOW THIS SKILL STRICTLY" banners are deleted outright, not relocated.
- A move that proves unsafe on reconcile (wording differences turn out semantic, not drift) is skipped with the inline copy kept and the finding logged — an honest null on that move, not a cluster blocker. Do not force-merge semantically different rules.
- After each move, the carrier keeps a one-line pointer naming the shared file the rule moved to.
- Dedup-sibling-ids doctrine: single home is lessons-auditor (the executing role); admiral keeps a pointer.
- Design-it-twice restatements in commander + explorer: cut to one pointer line each (canonical text already lives in `_shared/global-orchestrator.md` + `design-it-twice-brief.md`).
- The source repo (`skills/`) is authority; do not edit installed copies under `~/.claude/skills/`.
- Superpowers is a competitor: never cite or import its doctrine in anything you write.
- Edit `SKILL.md` prose carefully — these files are the product. Match existing register; the spec's register rule is rule-plus-why, emphasis only at mechanism-backed gates.

## Honest-Null Clause
A measured negative on any single move (unsafe to consolidate, carrier list unconfirmable) is a complete, successful deliverable for that move. Report it with the same rigor as a completed move.

## Inherited Latitude
You may decide: wording reconciliation per move, test naming/placement, pointer phrasing, commit structure. You must float to the Admiral: any new file whose name could collide with the bundle glob, any move whose destination seems wrong against the code you see, any scope beyond the 10 listed moves + regression net, anything touching skills outside the moves' carrier lists.

## File Ownership
You own this wave: `skills/_shared/global-everyone.md`, `skills/_shared/global-orchestrator.md`, all carrier SKILL.md files named in the moves table, `tests/test_install_constellation.py` (additions), and any new test file you add under `tests/`. Fence: do NOT touch `manifest.json`, the repo-root stray file, `docs/ROADMAP.md`, or fix typos outside your carriers — a sibling crew (issue #105) owns hygiene this wave. Findings file: `.agent-work/issue-102/` inside YOUR worktree (worktree-local; the Admiral harvests at closeout — do not write to the main checkout's canonical `.agent-work/LESSONS.md` or `AGENT_FEEDBACK.md`).

## Workspace
Worktree: `C:\Programs\constellation-wt-102` — branch `constellation/issue-102`, base commit 2696769 (current main), created via `git worktree add ../constellation-wt-102 -b constellation/issue-102`.
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:\Programs\constellation-wt-102` (from inside the worktree) — it must exit 0. Paste its output into your return report.
PR integration is server-side merge on the PR (the Admiral merges); do not merge locally.

## Inherited Context
Active lessons that bind this mission (paste-quality, from `.agent-work/LESSONS.md`):
- Dogfooding divergence: the globally-installed commander skill copy and this repo's `skills/commander/templates/` can diverge. Drive your engine from THE REPO'S OWN templates and scripts (`skills/commander/`, `skills/workbench/scripts/checklist_engine.py` or the repo's canonical engine path), not the installed copy.
- Plan-scope completeness: before advancing past plan/execute, confirm execute.json contains one gate for every file/decision-class in the stated file-ownership scope — a gate "handled directly by the Commander" that isn't in execute.json doesn't exist.
- Doc-only gates: prose/doctrine gates lack a runtime evidence contract; use inspection-attestation style evidence (quoted before/after text + grep output), don't invent test-shaped proxies.
- Under-epic durable writes: stage your AGENT_FEEDBACK entry and lessons-delta WORKTREE-LOCAL (e.g. `.agent-work/issue-102/` in your worktree) for Admiral harvest; do not write through to the main checkout's canonical files mid-epic.
- Baseline reconcile: at understand, reconcile this order's assumed baseline against actual code before planning; a mechanism assumed missing may already exist — the genuine gap may be narrower.
- Test invalidation: if a doctrine relocation invalidates an existing test's scenario, say so explicitly in the handoff ("expect to rewrite test X"), so "suite green" doesn't read as don't-touch-existing-tests.
- New-file diffs: a gate creating a NEW tracked file must state it's untracked until staged ("git diff shows N-1 files; the new file appears in git status").
- JSON templates: never round-trip shipped JSON templates through json.load/json.dump; edit raw text surgically, validate after.
- Reviewer artifact paths: park ALL of a gate's review artifacts under `.agent-work/issue-102/crew-handoffs/<gate>-review/` (one subtree per gate).
- Any background crew you spawn must be told, in its spawn prompt, to deliver its result in its final message before going idle.
- Word counts and carrier counts are command-derived (`wc -w`, `grep -c` with pasted output), never impressions.

## Pre-empted Steps
None — run your full spine (understand → plan → execute → reconcile). The issue body pre-answers most understand-phase questions; cite it rather than re-deriving.

## Data Locations
All inputs are tracked in the repo. Epic work area (Admiral-owned, read-only to you): `C:\Programs\constellation-skills\.agent-work\epic-101\`.

## Budget
- **Model tier (required):** inherit session model (this is the corpus's highest-risk cluster: many files, drift reconciliation, register-sensitive prose). Crew (implementer/reviewer) may run one tier down at your discretion.
- **Compute/time, session-window:** single session target; if the 10 moves + tests exceed your window, ship the completed moves as the PR and return the remainder as an explicit continuation note.

## Stop Conditions
Stop and return when: a move requires restructuring beyond the listed carriers; the bundle-glob constraint cannot be satisfied; test suite has pre-existing failures on base commit 2696769 (report, don't fix unrelated breakage); or you need context this order doesn't cover. Asking up is always sanctioned.

## Return Shape
Final message = full report: per-move disposition table (done/skipped-null + one-line reason + before/after carrier-count grep output), test additions summary, suite result (command + exit code), PR URL, before/after per-skill word counts, worktree-isolation verification output, map impact, triage candidates, workflow feedback. Deliver this report as your final message BEFORE going idle — an idle notification with no report reads as stalled.
On Windows: write the PR body to a temp file and use `gh pr create -F <file>` — never heredoc/here-string `--body`.
