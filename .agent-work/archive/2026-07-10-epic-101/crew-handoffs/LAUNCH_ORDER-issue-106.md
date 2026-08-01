# Launch Order: commander-106 — issue #106 (Cluster E: autonomous eval harness, Euler-piloted)

Commanders start cold. Paste, don't point.

## Mission
Execute issue #106: the autonomous eval harness — a REPO TOOL, not a skill (a skill wrapper fails the deletion test). From the spec section pasted in the issue body:
1. **Runner-contract design gate (the spec's named deferred decision — run it FIRST as a design-it-twice):** scenario schema, checks as plain scripts vs a DSL (the spec leans plain; a DSL needs justification), temp-install mechanics, headless-agent launch mechanics, and the N-of-M defaults. 3 alternatives compared on depth/locality/seam/testability per the tier standard; record the comparison; pick and proceed (float to Admiral only if the candidates genuinely tie or the winner needs out-of-scope machinery).
2. **Runner** (`scripts/run_skill_eval.py`): installs candidate skills from the worktree to a TEMP target, launches fresh headless agents on a scenario (the repo's `run_crew.py --backend cli` was fixed in PR #95 to match the current claude CLI — reuse its launch mechanics or its lessons), then executes the scenario's checks itself. **Check hierarchy is contractual (T3):** process checks carry the verdict — engine spine JSON completed its steps, expected artifacts present, tests written and green. Answer-correctness is a weak signal, NEVER sufficient (Euler answers are likely memorized by frontier models); a scenario passes only on process checks. **N-of-M (T4):** the runner runs each scenario N times with a pass-rate threshold; single-run verdicts are disallowed by the contract. Set pilot defaults small and justified (e.g. 2-of-3) — usage limits are real (a wave commander died to one this epic).
3. **Pilot scenarios** (`evals/<name>/`): 2–3 Project Euler scenarios at graded difficulty — fixture-repo setup + a task prompt driving a real constellation workflow (commander runs "solve Euler #N with tests" as a bounded issue with implementer/reviewer crew) + mechanical checks. Keep transcripts for diagnosing failures, not judging.
4. **Bar documentation:** the situational bar (new skill or behavior-changing rewrite → ≥1 scenario execution, itself N sub-runs, before install; mechanical edits → existing suite + git review; nothing gates on evals) documented where a maintainer will find it (e.g. evals/README.md).
5. **Acceptance (self-testing by construction):** ONE pilot scenario executed for real through the runner, N-of-M, with the verdict and process-check outputs pasted. Falsification evidence: show the checks bite — a deliberately-broken variant (e.g. point the temp install at a skill with its spine template removed) must fail its process checks. Budget guard: if real headless runs prove infeasible in your session (usage limits, CLI auth), ship the harness + a dry-run mode proof and report the blocked live run as an honest null with exact failure output — the Admiral routes it.
6. The delegated-commander selection scenario (F's first non-Euler pilot) is OUT of your scope — document it as the named next scenario in evals/README.md; do not build it.

## Prior-Wave Verdicts (pasted)
- Waves 1–3 all merged (main=c0aed68, your base): cluster A dedup + content-pin/no-residual regression net (tests/test_install_constellation.py); D hygiene; F commander split (commander is now a 254w human entry + commander-core.md reference + NEW constellation-commander-delegated skill — 15-skill roster) + crew-dispatch reference; B diets (admiral/docent/interrogator/history sweep); C curator (scripts/curate_corpus.py + skills/curator/ + 18 golden tests). Suite at 467 passed / 2 skipped.
- Your eval scenarios exercise the POST-cleanup corpus — a commander-driven scenario now loads the entry + core structure. That's the point: the harness guards exactly this restructured corpus.
- Harness constraint (from commander-104, verified): in-process teammates CANNOT spawn background subagents — crew dispatch is synchronous Agent-tool calls. Your runner's headless launches are OS processes (claude CLI), not Agent-tool calls — different path, but budget accordingly.

## Pre-Rulings
- Repo tool, not a skill: no skills/eval-* dir, no SKILL.md, no bundle-map entries. `evals/` + `scripts/run_skill_eval.py` + tests.
- Nothing gates on evals: the runner is never wired into pytest's default collection in a way that makes CI/suite runs launch agents. Runner-invoked only. (A fast unit-test layer for the runner's own logic — schema parsing, check execution, verdict math on canned fixtures — DOES go in tests/ and must not launch agents.)
- Process checks carry the verdict; answer-correctness weak-never-sufficient; N-of-M contractual. These are dispositioned critic findings (T3/T4) — not re-litigable.
- Transcripts kept for diagnosis, never judged by the runner.
- Superpowers is a competitor: never cite or import its doctrine.
- Source repo is authority; never edit installed copies. Temp-installs go under the system temp dir or a gitignored path, never committed.
- Do not touch other skills' content, `_shared/`, docs/ROADMAP.md.

## Honest-Null Clause
A live pilot run blocked by environment (usage limits, CLI auth, headless flakiness) is a complete deliverable when reported with exact evidence and a dry-run-mode proof of the runner logic. A pilot whose process checks fail on a known-good corpus is a FINDING about check strictness — report, tune once with justification, and if still failing, ship with the honest verdict.

## Inherited Latitude
You decide: runner-contract winner (via design-it-twice), scenario schema, N/M defaults (justified), Euler problem choices, dry-run design. Float to Admiral: any urge to gate something on evals, a skill wrapper, touching install bundles, or a runner contract that needs repo-wide changes.

## File Ownership
Yours: `evals/**` (new), `scripts/run_skill_eval.py` (new), `tests/test_run_skill_eval.py` (new; agent-free unit layer), README under evals/. Fences: everything else. Findings: `.agent-work/issue-106/` INSIDE your worktree; never write main-checkout canonical LESSONS/AGENT_FEEDBACK (known engine gap: verify_agent_feedback/verify_lessons_applied resolve to main via git-common-dir — if their spine checks fail against your worktree staging, run them with `--root <your worktree>` as commander-104 proved works, or force-waive with authority cited, and flag it; do NOT write to main).

## Workspace
Worktree: `C:\Programs\constellation-wt-106` — branch `constellation/issue-106`, base c0aed68, created via `git worktree add ../constellation-wt-106 -b constellation/issue-106`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-106` (forward slashes) — must exit 0; paste output. Server-side merge is the Admiral's; never merge locally.

## Inherited Context
Active lessons binding this mission:
- Drive your engine from THE REPO'S OWN templates/scripts (commander = entry + references/commander-core.md now).
- Plan-scope completeness: one execute gate per deliverable class (design gate, runner, scenarios, unit tests, live acceptance — gate each).
- Baseline reconcile at understand: check what run_crew.py --backend cli already provides before building launch mechanics from scratch.
- New tracked files are untracked until staged — say so in diff evidence.
- Never round-trip shipped JSON templates through json.load/dump; surgical text edits.
- Review artifacts under `.agent-work/issue-106/crew-handoffs/<gate>-review/`.
- Crew spawn prompts must require the crew's final message to be its complete report before idling; crew dispatch is synchronous in this harness.
- Counts/verdicts command-derived with pasted output.
- Engine status vocabulary is a closed set — use `complete`, never hand-set `done` (a crew wedged on this last wave).

## Pre-empted Steps
None — full spine. Issue #106's body is the authoritative spec section; the runner-contract design gate is YOURS to run (pre-authorized above).

## Data Locations
All inputs tracked. Epic work area (read-only): `C:\Programs\constellation-skills\.agent-work\epic-101\`. Claude CLI availability/auth for headless runs: probe early (`claude --version`; a trivial `claude -p "say ok"`) and report — it determines whether the live acceptance is feasible this session.

## Budget
- **Model tier (required):** inherit session model for you; crew one tier down where mechanical. Headless pilot agents: ONE tier down (the harness should prove the workflow works on cheaper models, and it conserves the usage pool). Keep total live headless runs ≤ ~6 agent-sessions this mission (N-of-M on one scenario + one broken-variant falsification); if that budget can't prove acceptance, take the honest-null path.
- Session-window: if the window runs short, ship the runner + unit layer green and return the live run as continuation.

## Stop Conditions
Stop and return when: the runner contract can't be satisfied without repo-wide changes; live runs burn budget without converging; or context gaps. Asking up is always sanctioned.

## Return Shape
Final message = full report: design-gate comparison summary + chosen contract, runner interface, scenario list, unit-test results, live acceptance verdict (N-of-M outputs pasted) or honest-null with evidence, falsification evidence, suite result (command + tail), PR URL, isolation output, map impact, triage candidates, workflow feedback. Deliver BEFORE going idle. PR body via `gh pr create -F <tempfile>`, never --body heredoc.
