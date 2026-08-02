# Launch Order: `cmdr-7c-reconcile` — reconcile physics ↔ fantasy lineages into a unified main

You are a delegated Commander under Admiral `epic-601-physics-training`. Run the full Commander spine. No reachable human — float to the Admiral. This is delicate git-history work: **investigate before you merge, surface genuine judgment calls, and do NOT push.**

## Mission
Local `main` and `origin/main` have **forked into two disjoint lineages**, each missing what the other has. Produce and **fully verify** a single unified-main candidate (on a dedicated branch) that contains BOTH halves, resolve conflicts with documented judgment, and hand back a proven recipe. **Do NOT push to `origin/main`** — the Admiral performs the final push at wave close after the other Wave-7 work integrates (bases must stay stable meanwhile).

## The topology (pasted — verify it yourself first)
- **local `main` = 5e8e92d7 (#600), UNPUSHED** — carries the physics foundation: #585 ideal-lap/ephemeris, #586 wear v2, #595 pipeline-tightening (honest σ/covariance, D9 pathway), **#596 the 2026 `SEASON_BASE_KG` entry in `src/physics/mass_model.py`**, #597/#598 wear coast, #599/#600 docs+archive. These 8 commits are on NO remote branch's `main`.
- **`origin/main` = 9f014121 (#621)** — carries the fantasy closeout: **#619 (a10912cc) determinism fix** ("Make sampled runtime execution deterministic" — the Wave-8 A/B depends on this) + **#621 (9f014121) classification-status-for-DNF**. It is MISSING all of #585–#600.
- `git merge-base main origin/main` returned **empty** — the lineages may share only a very old ancestor or unrelated roots. Investigate (`git merge-base`, `git log --oneline --graph`, check `git rev-list --count`), and determine whether a normal 3-way merge applies or `--allow-unrelated-histories` is needed.
- The physics stack ALSO exists on `origin/feat/604-race-week-build` (tip 244b05d3) and `origin/feat/602-mission-consolidation` — those are physics-lineage feature branches. `#619`/`#621` exist only on `origin/main` and `origin/codex/617-classification-status`.

## Deliverable
A dedicated branch (e.g. `reconcile-physics-fantasy`) off local `main` (5e8e92d7) into which `origin/main`'s unique commits (#619 determinism + #621 classification) are merged, conflicts resolved, such that the result has: the full physics foundation (verify `src/physics/mass_model.py` `SEASON_BASE_KG[2026]` present; #595 pipeline-tightening intact) AND the determinism fix's behavior (verify sampled runtime is reproducible/deterministic per #619) AND #621's classification-status. Full test suite green on the unified tree. A written recipe (exact commands + conflict resolutions + rationale) so the Admiral can re-apply the same reconcile onto local `main`+#560+7A+7B at wave close.

## Pre-Rulings (overridable with evidence — SURFACE if a conflict is a genuine judgment call)
- **Do NOT push `origin/main` or force-push anything.** Local branch + report only.
- **Do NOT delete/rewrite the user's local `main`** or their dirty working tree. Work entirely in your worktree on a new branch.
- Prefer a MERGE that preserves both histories over a rebase that rewrites them (auditability; the user wants to "merge up").
- Conflict-resolution intent: **keep the physics foundation whole AND keep the determinism fix's behavior.** Where a file was touched by both lineages (most likely `src/evo_predictor/sampled_runtime.py` and any shared config), resolve to satisfy BOTH properties; if that's impossible or ambiguous, STOP and surface the specific conflict to the Admiral with both sides quoted — do not guess on a load-bearing file.
- Verification is part of the deliverable: full `py -m pytest` suite must pass on the unified tree; call out any pre-existing failures that also fail on plain local `main` (not yours to fix).

## Honest-Null / Escalation Clause
If the reconcile cannot be done cleanly without a judgment call that belongs to the human (e.g. two incompatible versions of a core file, or the histories are genuinely unrelated in a way that needs a human decision on canonical lineage), that is a valid outcome: STOP, document precisely what conflicts and why, and surface it. A precise blocker beats a guessed merge.

## Inherited Latitude
Delegated: subagent dispatch (Sonnet), local git operations on YOUR worktree/branch, conflict resolution within the stated intent, running the suite. Surface/float: pushing anything, any operation on the shared local `main` or the user's working tree, any conflict resolution that is a genuine human judgment call, force-pushes.

## File Ownership
Your reconcile branch + `.agent-work/cmdr-7c-reconcile/RESULT.md` (the recipe). You do not author feature code. No contention with 7A/7B (different worktrees/branches).

## Workspace
Worktree: `C:/tmp/f1brainz-601-7c-reconcile`, branch `wave7c-reconcile`, base `5e8e92d7` (local main). Created via `git worktree add -b wave7c-reconcile C:/tmp/f1brainz-601-7c-reconcile 5e8e92d7`. Do your reconcile on this branch (or a child of it).
FIRST STEP: `py scripts/verify_worktree_isolation.py --here C:/tmp/f1brainz-601-7c-reconcile` — must exit 0; paste output. `git fetch origin` first so `origin/main` is current in your worktree.

## Inherited Context (invariants)
- Python `py` (3.14); full suite `py -m pytest tests/...` (integration tests can take 10–15 min — NN training; budget for it). Some tests need the main-checkout DBs (see Data Locations).
- Windows/PowerShell primary; a Bash tool exists. Line-ending (CRLF/LF) diffs are common and are NOT real conflicts — normalize/ignore whitespace-only diffs.
- The editable `.pth` may point at the MAIN checkout; when running the suite to verify YOUR tree, ensure you're testing the worktree (pin `PYTHONPATH`/sys.path or run pytest from the worktree root, which resolves local `src/`).
- Determinism check (#619): verify the sampled runtime reproduces identical output across two runs with the same seed — that's the property the merge must preserve.

## Data Locations (main checkout — worktrees lack large/untracked DBs)
- `C:/Programs/f1Brainz/data/f1_data_<year>.db`, `C:/Programs/f1Brainz/data/physics_estimates.db` — read-only for any test that needs them.

## Budget
- **Model tier (required):** Sonnet. Escalate to a higher tier only if conflict resolution on a core file proves genuinely ambiguous (prefer surfacing to the Admiral over guessing).
- Compute: the full suite once on the final unified tree (batched), not per-attempt. Integration tests are slow — run them once at the end.

## Stop Conditions
Stop/return when: the unified branch is built and the full suite is green with both properties verified; OR a conflict needs human/Admiral judgment; OR you'd need to push/touch shared main to proceed. Ask up freely.

## Return Shape
Write `.agent-work/cmdr-7c-reconcile/RESULT.md` before idle. Include: the verified topology (merge-base finding, commit counts each side); the exact reconcile recipe (commands, in order); every conflict + how you resolved it + why; proof both properties hold (2026 mass present; determinism reproduced) + full-suite result (pass count / any pre-existing failures); the unified branch name + tip commit; explicit confirmation you did NOT push; the `verify_worktree_isolation.py --here` output; triage candidates (e.g. "origin/main was physics-incomplete — track as its own issue?"). Do not open a PR to `origin/main` (Admiral owns the push).
