# Launch Order: `commander-corpus-id — #153`

Commanders start cold. Everything you need is pasted below.

## Mission
Fix the eval harness's install-path-polluted `corpus_id` so byte-identical corpora hash to the same id regardless of install location. This is HIGH priority: it blocks any N≥8 certification run (rolling certification accumulates "across same-corpus-hash runs", which is invalid until this is fixed). Deliverable: one green, reviewed PR.

**Issue #153 (verbatim):** `rewrite_installed_skill_paths` bakes the absolute install path into every skill file, so byte-identical corpora hash to different `corpus_id`s by install location — verified during #145: the +rail and +rail+hooks corpora differ ONLY in the arm-path substring, yet hash differently. The #136/#138-D6 policy of rolling certification accumulation "across same-corpus-hash runs" is invalid until fixed.

**Fix directions (from the issue):** hash a canonical-path (pre-rewrite) corpus, OR path-normalize before hashing. Pick whichever is cleaner given the actual code; justify the choice in your report.

**Also required (docs graduation, lesson `eval-harness-bundles-engine-from-invoking-checkout`):** document — in the harness docs/README — the load-bearing arm-construction fact that **the bundled engine comes from `REPO_ROOT/scripts/` of the checkout that INVOKES `run_skill_eval.py`, not from `--worktree`.** This is a small doc addition, not code.

## Prior-Wave Verdicts (pasted)
None — wave 1, dispatch B. No upstream dependency.

## Pre-Rulings
Each overridable if evidence contradicts it.
- Prefer path-normalization at hash time over a whole second canonical corpus build, unless the code makes the pre-rewrite hash strictly simpler — justify in the report.
- Add a regression test: two corpora identical except for install path hash to the SAME `corpus_id`.
- Keep the fix inside the eval harness; do not change what `rewrite_installed_skill_paths` does at install time for real installs (only how the corpus is HASHED).

## Honest-Null Clause
A measured negative is a complete deliverable. If the pollution is narrower than described (e.g. already partly normalized), report exactly what you found with evidence.

## Inherited Latitude
You may choose the normalization approach, apply it, add tests, open the PR. FLOAT to the Admiral: any change to install-time path rewriting for real (non-eval) installs; any new issue; anything outside your file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `scripts/run_skill_eval.py` and the eval-harness modules/tests it owns, plus the harness docs/README section on arm construction. Do NOT touch `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, the top-level `README.md`, or `docs/CHECKLIST_SCHEMA.md` (other wave-1 commanders own those). If the arm-construction doc naturally belongs in the top-level README, put it in the harness/eval doc instead and note the pointer — do not edit README.md this wave.

## Workspace
Absolute worktree: `C:/Programs/cs-wt-corpus` — branch `fix/corpus-id-153`, base commit `467a6b0` (current main), provisioned via `git worktree add -b fix/corpus-id-153 C:/Programs/cs-wt-corpus main`.
First step: run `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-corpus` — must exit 0; paste output into your report.
PR integration = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** (1) multiline `gh --body`/PR body → write to a temp file, `gh pr create -F <file>`; heredoc and `@'...'@` here-string both fail PS 5.1 for `--body` (here-string works for `git commit -m` only). (2) Use `py`, not bare `python`. (3) Verify your worktree with the isolation script above.
**Active lesson `test-harness-concurrency-failsafe`:** if any test drives concurrent file I/O, wrap per-iteration work in try/except with a stop-signal in `finally` and mark helper threads `daemon=True` (a writer dying silently hangs pytest). Most corpus-hash tests won't need threads — prefer simple ones.
**Eval-harness fact:** the #145 measurement run found the +rail and +rail+hooks corpora differ ONLY in the arm-path substring yet hashed differently — that IS the bug. Use that as your reproduction anchor.

## Pre-empted Steps
None. Run your full spine.

## Data Locations
Read-only reference (main checkout, do not write): `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/` and any #145 harvest under `.agent-work/dispatch-126-127/harvest-129-131/` if you need the original evidence. The issue text above is self-contained.

## Budget
- **Model tier (required):** opus. Correctness-sensitive hashing/normalization on the certification-blocking path.
- **Compute/time, session-window:** bounded; no nested crews. Checkpoint (commit WIP) and return if you near a session limit.

## Stop Conditions
Stop and return when: the fix would change real-install path rewriting; you find the bug is already fixed (report the null); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Write your result artifact to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-1/W1-B-REPORT.md` BEFORE going idle: verdict, evidence (the regression test name + green output proving two install-paths → one corpus_id, the chosen approach + why), PR URL, map impact, triage candidates, workflow feedback, and your isolation-script output. Open the PR with `gh pr create -F <bodyfile>` targeting main; title `fix(evals): install-path-invariant corpus_id (#153)`. Post the verdict in the report, then go idle.
