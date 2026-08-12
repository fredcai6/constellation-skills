# Launch Order: `commander-curate — #117 (MECHANICAL TOOL FIXES ONLY)`

Commanders start cold. Everything you need is pasted below.

## Mission
The **curate_corpus.py v2 tool refinements** portion of #117 ONLY. Deliverable: one green, reviewed PR.

**SCOPE RULING (Admiral, per latitude):** #117 has two halves. The **consolidation-run half** (the actual measure→mend of the listed targets: the engine-invocation rule restated in 5 skills, the implementer/reviewer Workflow-Feedback hoist, the commander/commander-delegated overlap) is DEFERRED — it requires a human-invoked `constellation-curator` run per that skill's cadence-is-a-habit design, and Fred will drive it. Your mission is ONLY the mechanical tool fixes below. Do NOT perform consolidation edits on any skill SKILL.md.

**Tool fixes (#117 v2, verbatim):**
- Shared status/check-vocabulary contract fragment read by BOTH `curate_corpus.py` and its golden tests (#104 lesson `curate-contract-shared-vocabulary`) — single-source the status/check vocabulary so the tool and its golden tests can't drift apart.
- Matcher refinements: the exclusion-clause matcher hits `'not '` anywhere (over-broad); the person-shortlist matcher false-positives on `'us'` (tc6). Tighten both.
- Drift-vs-baseline diff block: only if THIS need is proven — spec ruling S7 stands (do NOT add speculative diff machinery; skip unless the tool clearly demands it now).

## Prior-Wave Verdicts (pasted)
Base is current main (see Workspace). Note: `skills/curator/SKILL.md` was just edited by #118 (two-sided-acceptance guard + dedup-move sequencing) — it is OUT of your fence; do not touch it.

## Pre-Rulings (overridable with evidence)
- Single-source the status/check vocabulary as a shared fragment (module constant or data file) imported by both `curate_corpus.py` and its golden tests — the point is they can't drift.
- Matcher fixes: make the exclusion matcher match `'not '` only as a genuine exclusion clause (word-boundary / clause-position aware, not substring-anywhere); make the person shortlist not fire on the token `'us'`. Add a test for each fixed false-positive.
- Do NOT run consolidation / edit skill SKILL.md content (that's the deferred human-curator half).

## Honest-Null Clause
A measured negative is a complete deliverable. If a matcher issue is already fixed on current main, report where, with evidence.

## Inherited Latitude
Implement the tool fixes + tests, open the PR. FLOAT: anything that would require running consolidation or editing skill content (that's deferred — surface it, don't do it); any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `scripts/curate_corpus.py`, its shared-vocabulary fragment (new module/data file if you add one), and its golden/test files under `tests/`. Do NOT touch any `skills/*/SKILL.md` (consolidation is deferred; curator SKILL is #118's), `skills/_shared/windows.md` or `skills/implementer/SKILL.md` (the other 3C commander owns those), or any doc.

## Workspace
Worktree `C:/Programs/cs-wt-curate` — branch `fix/curate-corpus-117`, base `1f3417f` (current main). Provisioned via `git worktree add -b fix/curate-corpus-117 C:/Programs/cs-wt-curate main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-curate` → exit 0; paste into report.
PR = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** multiline `gh --body` → temp file + `gh pr create -F <file>`; `@'...'@` is PowerShell-only, NOT a Git-Bash commit construct — real heredoc or quoted `-m`. Use `py`. Verify your worktree.
**KNOWN FRICTION (agent_work_root staleness):** the installed bundle's `agent_work_root.py` is stale vs main (missing #118's fix), so your feedback/archive gates may resolve durable_root to the main checkout. Workaround: pass `--root .`, or write the trio to the worktree-root `.agent-work/` and force-waive with independently-verified reasoning if the gate resists — a known Admiral-acknowledged lag, not your bug. Do NOT edit agent_work_root.py.
**Active lesson `test-harness-concurrency-failsafe`:** concurrent-file-I/O tests need try/except + stop-signal in `finally` + `daemon=True` (unlikely here).
Read `scripts/curate_corpus.py` + its tests first. Run the suite before/after; all pre-existing tests stay green.

## Budget
- **Model tier (required):** sonnet. Bounded tool/matcher fixes against an established script + golden tests.
- Checkpoint and return if you near a session limit.

## Stop Conditions
Stop and return when: a fix would require consolidation or skill-content edits (surface it — that's the deferred half); a matcher issue is already fixed (report the null); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-3/W3-117-REPORT.md` BEFORE going idle: verdict (per tool fix), evidence (shared-vocabulary single-source proof; a test for each fixed matcher false-positive + green output; full suite green), PR URL, map impact, triage candidates (incl. an explicit note that the consolidation-run half remains for Fred's human-invoked curator run), workflow feedback (name trio path), isolation output. Open PR with `gh pr create -F <bodyfile>`; title `fix(curator): shared status vocabulary + matcher false-positive fixes (#117 tooling)`. Post verdict, go idle.
