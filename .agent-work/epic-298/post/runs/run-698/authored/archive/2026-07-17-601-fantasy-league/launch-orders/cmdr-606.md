# Launch Order: `cmdr-606` — issue #606 league decomposition study

## Mission

Run GitHub issue #606 for epic #601: determine where league winners' roughly 7.5 fantasy points per race advantage over the model comes from, using the five league workbooks plus leakage-free model results. The study must produce a tested normalization/reconciliation layer, rules-as-fixture evidence, model virtual-competitor placement, per-channel attribution, and an evidence-backed capacity recommendation for the DNF, quali-head, and physics workstreams.

This is the next dependency-ready bite because #606 explicitly gates capacity allocation to epic #601 Track 2 items 2–4. Do not start those downstream mechanisms here.

## Prior-Wave Verdicts (pasted)

- Epic foundation #602 and data catch-up #603 are complete and closed.
- The race-week seam and command from #604 are merged through PR #613 at `origin/main` commit `919f1347f7bcc718bf5ac5e6c84b6a90226e13c3`. Issue #604 remains open only for the live Belgium shakedown; it does not block this study.
- R8 Austria and R9 Great Britain classifications exist in the canonical 2026 DB. The primary model decision metric is fantasy points per race against actual classifications; the league overlay is informational.
- The confirmed epic spec requires: normalize workbook round/GP discrepancies; reproduce recorded workbook totals before decomposition; encode the scoring rule as a documented fixture cross-validated across multiple seasons/players/rounds; insert the model as a virtual 21st competitor with ties resolved against the model; never hard-code the owner's heuristics; allow an honest ambiguous attribution.
- Known verified 2026 hazard: the Standings sheet retains stale Bahrain/Saudi placeholder columns while per-round sheets follow the real calendar from Miami onward. GP aliases also vary (`Barcelona`/`Barcelona-Catalunya`, `Austin`/`United States`, `Monza`/`Italy`, `San Marino`). Silent positional joins are forbidden.

## Pre-Rulings

Ruled in advance; override only when source evidence contradicts and report the override.

- **First falsification gate:** reproduce the workbooks' own recorded totals before making any channel-attribution claim. A failed reconciliation is a scoped, successful diagnosis but does not authorize downstream decomposition claims.
- **Canonical-source split:** SQLite is canonical for model inputs, predictions, classifications, and leakage-free results. The workbooks are canonical only for league picks, recorded league scoring, and standings. Every cross-source join uses explicit normalized keys plus reconciliation evidence; no silent fallback or round-position assumption.
- **Design-it-twice checkpoint:** the normalization/reconciliation and parser seam is load-bearing. Produce at least two materially distinct interface designs, compare depth/locality/seam placement/testability, and recommend one. **Do not converge or implement the chosen seam.** Return the alternatives and recommendation to the Admiral; human selection is mandatory under the confirmed contract.
- **No heuristic hard-coding:** FP3 ordering, reliability discounts, or named-driver rules may only appear as measured hypotheses/results.
- **Existing scoring seam first:** verify `src/fantasy_scoring/scoring_rules.py` and every relevant consumer signature from source before proposing new logic. Prefer a single canonical scoring path; no duplicate calculator.
- **Spreadsheet evidence workflow:** load the installed `spreadsheets:Spreadsheets` skill before workbook inspection. Use the loader-provided runtime and `@oai/artifact-tool` for workbook reads/inspection; do not use system/global `openpyxl` or ad-hoc parsing. This is read-only workbook analysis: do not edit or export replacements. Inspect displayed values/formulas and render representative source sheets when needed to verify layout/labels. Keep workbook dumps compact.
- **Main checkout fence:** the shared main checkout is stale and heavily dirty with user work. Do not modify, clean, switch, merge, or stage there. All issue writes stay in the provisioned worktree. The untracked workbook inputs are read-only through the absolute paths below.
- **TDD and docs:** after human seam selection, implementation must be test-led and documentation updated with the code. This dispatch currently stops at the seam checkpoint, so no production implementation or PR is expected before the float.

## Honest-Null Clause

A measured negative or ambiguous decomposition is a complete successful deliverable when its tested scope, failed assumptions, and what remains untested are explicit. One failed normalization variant does not prove the whole workbook family unusable; test another materially distinct variant before any impossibility claim.

## Inherited Latitude

You MAY inspect code/docs/workbooks, run read-only probes and tests, create issue-local design artifacts in your worktree, dispatch crews/critics/subagents, and return a seam recommendation. You MAY later push/open a PR only after the Admiral continues you with the human-selected seam.

You MUST FLOAT to the Admiral: seam convergence; any architecture/structural change; any data/physics/evo boundary crossing; scope changes or new epic issues; merge/issue close/file deletion; production defaults/user-visible behavior; materially long compute; any out-of-taxonomy choice. You cannot reach the human directly.

## File Ownership

Before the seam checkpoint, sole writer of worktree-local `.agent-work/cmdr-606/**` plus one proposed design artifact under `docs/design/` if useful. Do not modify production source/tests before human convergence. Never write the main checkout's `.agent-work/AGENT_FEEDBACK.md`, `LESSONS.md`, or `CONSTELLATION_FEEDBACK.md`; stage the complete fenced feedback trio under the worktree-local `.agent-work/staged-feedback/cmdr-606/` at final closeout.

## Workspace

Absolute worktree: `C:/Programs/f1Brainz/.claude/worktrees/606-league-decomposition`

Branch: `codex/606-league-decomposition`

Base: `origin/main` at `919f1347f7bcc718bf5ac5e6c84b6a90226e13c3`

Provision command: `git worktree add C:/Programs/f1Brainz/.claude/worktrees/606-league-decomposition -b codex/606-league-decomposition origin/main`

First step, before any git operation: `py C:/Users/fredc/.codex/skills/constellation-commander/scripts/verify_worktree_isolation.py --here C:/Programs/f1Brainz/.claude/worktrees/606-league-decomposition`. Paste its output into the return artifact.

PR integration defaults to server-side merge after explicit human authorization.

## Inherited Context

- Read `docs/AGENT_GUIDE.md`, `README.md`, `TESTING.md`, `docs/architecture/index.md`, `docs/DOCUMENTATION.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, and `docs/agents/GLOSSARY.md` before planning.
- Python is `py`, not `python`. The DB is the only authoritative analysis source; live FastF1 is collection-only.
- Relevant active lessons: use `py`; cite exact seam signatures and all consumers; worktrees lack untracked inputs and tracked data can also be stale; keep shared workflow files off the mission branch; every crew must deliver its result before idling; verify claimed side effects at their source; diagnose first when the fix locus is uncertain.
- Workbook runtime: Node `C:/Users/fredc/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`; packages `C:/Users/fredc/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules`. Create only a worktree-local junction/symlink when the spreadsheet skill requires it; never modify the dependency bundle.
- Current main checkout dirty state belongs to the user and is out of scope.

## Pre-empted Steps

Epic intent, issue ordering, and latitude are ratified by the Admiral contract refresh dated 2026-07-14. The issue's design spec is confirmed in epic #601. Cite this launch order for delegated `user-decision` evidence. The seam winner is deliberately **not** pre-ratified.

## Data Locations

Read-only league workbooks in the shared checkout (untracked; absent from worktree):

- `C:/Programs/f1Brainz/docs/reference_docs/Fantasy F1 2022.xlsx`
- `C:/Programs/f1Brainz/docs/reference_docs/Fantasy F1 2023.xlsx`
- `C:/Programs/f1Brainz/docs/reference_docs/Fantasy F1 2024.xlsx`
- `C:/Programs/f1Brainz/docs/reference_docs/Fantasy F1 2025.xlsx`
- `C:/Programs/f1Brainz/docs/reference_docs/Fantasy F1 2026.xlsx`

Canonical DBs and existing model artifacts are also read-only through absolute main-checkout paths under `C:/Programs/f1Brainz/data/` and `C:/Programs/f1Brainz/params/gold/`. Verify freshness before relying on them.

## Budget

- **Model tier:** harness default Codex tier (only exposed tier). Use at most the available concurrency; prefer two focused alternatives plus one cold critic if slots permit.
- **Compute/time:** bounded foreground discovery and workbook inspection. Do not start gold training or multi-hour backtests. If the seam study unexpectedly needs detached compute, float a plan first.

## Stop Conditions

Stop and return when the design-it-twice seam artifact is complete: evidence-backed baseline, at least two distinct alternatives, comparison, one recommendation, cold critique, and a concise human decision question. Stop earlier for missing/unreadable workbooks, inability to reproduce any workbook's totals after two distinct tested variants, need to modify production code before convergence, or any decision outside inherited latitude.

## Return Shape

Write `C:/Programs/f1Brainz/.claude/worktrees/606-league-decomposition/.agent-work/cmdr-606/ADMIRAL_RETURN.md` before going idle and send the verdict to the Admiral. Include: `CHECKPOINT` or `BLOCKED`; isolation-verifier output; workbook/source evidence inspected; exact existing scoring/parser seams and consumer topology; alternatives and comparison; cold-critic findings with dispositions proposed but not self-triaged; one opinionated recommendation; the exact human decision required; what was tested and not tested; map impact; triage candidates; workflow feedback. Deliver the artifact before ending the turn.
