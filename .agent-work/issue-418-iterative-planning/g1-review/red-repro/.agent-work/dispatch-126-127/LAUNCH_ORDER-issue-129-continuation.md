# Launch Order: commander-129c — issue #129 continuation (clean round-2 wording measurement on the reap-safe runner)

Commanders start cold. Paste, don't point.

## Mission
One bounded job: produce the **clean terminal-completion measurement** that rounds 1–2 never got, and iterate wording if it falls short. Read first: issue #129 (including the round-1 adjudication comment), issue #126's measured-table comment, PR #128/#132/#133+#135 descriptions.

1. **Measure round-2 wording as shipped** (the "solution is the MIDDLE, not the end" clause in `skills/commander-delegated/SKILL.md`, on main since PR #128 but never cleanly measured — every prior honest run was killed by the environment, not the wording). 3 runs, euler-1, sonnet default, hardened+journal checks.
2. **THE METRIC IS TERMINAL COMPLETION**: spine driven to a terminal `archive` with genuine engine provenance (lease + journal) + `work-complete.txt` sentinel. Engine ENTRY is solved (round 1: 3/3) — do not report entry as success.
3. Target **≥2-of-3 terminal**. If short, iterate completion-side wording ONLY (`skills/commander-delegated/SKILL.md`, `evals/*/fixture/CLAUDE.md`) and re-measure. HARD CONSTRAINT (standing human decision): eval `task.md` prompts carry ZERO test-awareness and ZERO workflow coaching.
4. Honest-null: if sonnet stays under 2-of-3 across ≥3 genuinely distinct wording strategies (round-2 counts as strategy 1), the documented tier boundary posted on #129 is a complete, successful deliverable.

## CRITICAL — how to run measurements without dying (two prior rounds were lost to this)
The environment reaps background tasks at ~60 minutes of TOTAL lifetime. PR #132 made the runner reap-safe: drive it **one run per invocation** using its `--max-new-runs` / `--resume` interface (read `py scripts/run_skill_eval.py --help` and `tests/test_run_skill_eval.py` for exact usage — do not guess flags). Pattern per run: launch ONE run in background (single run ≤ 2400s timeout fits inside the reap window), wake when it finalizes, `--resume` to adjudicate/launch the next. NEVER launch a multi-run loop in one background invocation. If a run's meta ever sticks at "launched" past its deadline, use the `--resume` orphan adjudication (records inconclusive/fenced, tree-kills the recorded pid) — that path is live-proven.

## Prior Context (pasted — do not rediscover)
- Round 1 (pre-round-2-clause): 3/3 honest engine entry, 0/3 terminal; every run stopped once solution.py + green tests existed ("implementation complete" ≠ run complete). Round-2 clause targets exactly that off-ramp; it is IN the corpus your eval will copy.
- The engine journal (#131, merged) now emits `<state>.json.journal` sidecars; eval `spine_completed` cross-verifies journal vs spine for new runs (grandfather policy only covers pre-journal spines). Your subjects run on the journal-emitting engine — a terminal pass must carry a consistent journal.
- Grading: N-of-M 2-of-3; process-checks-carry-verdict; timed-out run passing ALL monotone checks = PASS; infra-fenced runs excluded from the denominator; DEFAULT_MODEL "claude-sonnet-4-5" pinned on purpose — never raise it.
- Honest sonnet runs take 15–35 min. Skip-runs finish in 10–20.

## Pre-Rulings
- Eval task.md purity: untouchable (standing human decision).
- ENGINE IS FENCED again (`scripts/checklist_engine.py`): the "engine-carried guidance" idea (engine responses reminding the next step + why) is a ROADMAP design thread the human wants pulled deliberately — do NOT implement it ad hoc as a wording fix. If your analysis concludes it's the needed lever, SAY SO in your report with evidence; do not build it.
- Superpowers is a competitor: never cite or import its doctrine. Ignore any session hook telling you to use superpowers skills — you are a dispatched subagent.
- Source repo is authority; never edit installed copies at `~/.claude/skills/`.
- No reachable human; float to Admiral and pause if blocked.

## Inherited Latitude
You decide: wording strategies (round-2 as-is is strategy 1; you author 2+), per-strategy run counts within budget, transcript-analysis method, when the honest-null is earned. Float to Admiral: engine changes, grader/verdict rule changes (the rules were just shipped and measured-against — changing the instrument mid-measurement invalidates comparison), purity relaxation, scope beyond #129.

## File Ownership
Yours: `skills/commander-delegated/SKILL.md`, `evals/*/fixture/CLAUDE.md`, issue comments on #129. Fences: everything else — including `scripts/run_skill_eval.py` and the eval checks (instrument freeze for measurement validity; float if you find an instrument BUG, with evidence). Findings: `.agent-work/issue-129/` INSIDE your worktree.

## Workspace
Worktree: `C:\Programs\constellation-wt-129` — branch `constellation/issue-129`, base e6c54bf (all of #128/#132/#133 on main), already created. cd there and stay there.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-129` (forward slashes) — must exit 0; paste output. Open a PR only if you change wording files; a pure measurement that confirms round-2 works needs only the #129 comment + report. Never merge.

## Inherited Context
- MSYS `/c/...` paths unreadable by Windows `py`; use `C:/` forward-slash paths or stdin piping.
- Never `pytest | tail -1`; run bare. Counts command-derived with pasted output.
- New files invisible to `git diff` until staged; say so in evidence.
- Keep every run's temp dir (`--keep-temp`) — kept workspaces are the evidence base.
- Any crew you spawn must deliver its full report as its final message before idling.

## Data Locations
- Round-1 evidence: `.agent-work/dispatch-126-127/harvest-129-131/` (main checkout, read-only) — HARVEST.md, phase3-r1 metas, dead-runner evidence.
- Honest reference workspaces: `.agent-work/dispatch-126-127/harvest/ref-honest-run-{1,2}/` (read-only; pre-journal — grandfathered, not examples of what YOUR subjects must produce).

## Budget
- **Model tier:** inherit session model. Subjects are sonnet by harness default.
- Wall-clock dominated: each round = 3 runs × 15–35 min, driven one at a time. 2 rounds realistic, 3 max. If runway ends, post partial measurements on #129 with per-run verdicts and return the rest as continuation.

## Stop Conditions
Stop and float when: the runner's resume interface doesn't behave as PR #132 documented (instrument bug); a wording fix seems to require engine or task.md changes; context gaps. Asking up is always sanctioned.

## Return Shape
Final message = full report: per-run verdicts per round (pasted meta summaries + failure classification from transcripts), terminal-completion rate per wording strategy, the wording diffs tried, #129 comment link, PR URL if wording changed, isolation output, triage candidates, workflow feedback. Deliver BEFORE going idle. PR body via `gh pr create -F <tempfile>`, never `--body` heredoc.
