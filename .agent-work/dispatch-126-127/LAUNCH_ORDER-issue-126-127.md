# Launch Order: commander-126-127 — issues #127 + #126 (eval instrument hardening, then compliance-rate debug)

Commanders start cold. Paste, don't point.

## Mission
Execute BOTH issues in this order, one PR each (sequential on the same branch is acceptable if cleanly separable commits; two stacked PRs preferred):

**Phase 1 — issue #127 (spine provenance hardening).** `spine_completed` in `scripts/run_skill_eval.py` currently trusts plain JSON state; a fabricated spine failed only because the agent forgot to mark `archive` complete. Harden the check to demand **engine-shaped provenance**, not just step statuses. Key fact: the checklist engine ALREADY writes an `engine_session` lease block into spine.json (fields: `session_id`, `claimed_at`, `last_heartbeat`, `released_at`) plus `status_detail` fields on advanced steps. Minimum bar (from the issue): reject spines lacking a plausible engine_session block; check evidence ids / status_detail match engine grammar; consider heartbeat-vs-claim timestamp plausibility. Stronger option (your judgment whether it's worth it this pass): engine append-only journal sidecar cross-verified against spine state — but that changes the engine itself (`skills/workbench` scripts), which is a bigger blast radius; the issue's stated bar is **fabrication-cost > doing-the-work-cost, not tamper-proofness**. Ground truth for what genuine engine output looks like: the two honest-pass eval workspaces (Data Locations below) vs the fabricated spine described in the issue.

**Phase 2 — issue #126 (compliance-rate debug, fresh eyes).** Baseline established 2026-07-10: the corpus DOES drive sonnet through the full honest engine workflow, but at ~1/3 of runs; honest runs took 13.5–30+ min and BOTH were fenced by the old 900s/1800s timeouts, so recorded verdicts undercount. Your job:
1. **Verdict refinement (grader fix, do first, cheap):** a timed-out run whose workspace nevertheless passes ALL process checks should judge PASS — the checks are monotone (more time cannot un-pass spine_completed/artifact_present/tests_green); a timeout with failing checks stays fenced (infra, not FAIL). Also raise the scenario timeout floor to ≥2400s. Add tests.
2. **Wording iteration (the real work):** the question is precisely "what in `skills/commander-delegated/SKILL.md` (and the eval fixture `evals/*/fixture/CLAUDE.md`) phrasing moves sonnet from ~33% to reliably ≥2-of-3 honest engine runs". Failure modes observed: skip (solve directly, no artifacts), theater (copy spine template, never advance), fabrication (hand-write completed spine — which your Phase-1 hardening now catches). Fix space: imperative entry ritual / first-command-is-the-engine wording in commander-delegated, CLAUDE.md doctrine phrasing. HARD CONSTRAINT (human-established eval purity): the eval `task.md` prompts must contain ZERO test-awareness and ZERO workflow coaching — a real dispatch is "load the commander skill, go implement"; the SKILL must carry the agent. Do not touch task.md wording beyond what a real dispatcher would say.
3. **Re-measure:** `py scripts/run_skill_eval.py evals/euler-1-multiples --keep-temp --timeout 2400` (check actual flag names in the script). Runs cost 15–35 min each at sonnet; budget accordingly — measure after each wording iteration, not after each micro-edit. Target: 2-of-3 pass honestly with hardened Phase-1 checks. If the honest ceiling for sonnet stays below that after genuine iteration, that is a valid measured result: document the boundary ("gated-engine discipline needs ≥ tier X") in the issue and ship the best wording achieved — honest-null clause applies.

## Prior Context (pasted — do not rediscover)
- Headless `claude -p` DOES see project `.claude/skills/`; the harness copies the repo corpus into the eval workspace and stamps CORPUS.json.
- Workspace `.claude/settings.json` permissions are IGNORED in untrusted dirs headless; execution rights ship via `--allowedTools` CLI flag (`EXEC_ALLOWED_TOOLS` in run_skill_eval.py) — already fixed, don't regress.
- Runner uses Popen + deadline poll + `taskkill /T /F` + bounded drain (PR #125) because `subprocess.run(timeout=)` hangs on inherited pipes — don't regress.
- `__pycache__`/`*.pyc` are excluded from corpus hash and workspace copy — don't regress.
- Grading is N-of-M (default 2-of-3), process-checks-carry-verdict (spine_completed / artifact_present / tests_green; answer advisory), infra-fenced runs are excluded from the denominator, sentinel is `work-complete.txt`.
- DEFAULT_MODEL is pinned "claude-sonnet-4-5" ON PURPOSE (low tier = the boundary being measured). Do not raise the default; a `--model` flag already exists for diagnostics.
- Opus-tier diagnostic was run at issue-filing time and appended to #126 as a comment — read it.

## Pre-Rulings
- Phase order is binding: #127 lands (or is at least implemented locally) before #126 measurement runs, so measurements grade against the hardened check.
- Provenance hardening must not fail the two known-honest reference workspaces — they are your regression fixtures; validate the new check against both BEFORE relying on it.
- Eval-purity constraint above is a human decision, not yours to relax.
- Superpowers is a competitor: never cite or import its doctrine.
- Source repo is authority; never edit installed copies at `~/.claude/skills/`.
- No AskUserQuestion-style blocking; you have no reachable human — float decisions to the Admiral via your report.

## Honest-Null Clause
"Sonnet cannot be worded into ≥2-of-3 compliance" is a complete, successful deliverable IF backed by measured runs across ≥3 genuinely distinct wording strategies, each with pasted verdicts. So is "journal sidecar not needed; lease-block check suffices."

## Inherited Latitude
You decide: exact provenance-check heuristics and thresholds, wording strategies to try, whether stacked PRs or one branch with two clean commit groups, test structure. Float to Admiral: any change to the checklist engine itself (`skills/workbench/scripts/checklist_engine.py`) beyond read-only inspection, raising DEFAULT_MODEL, relaxing eval purity, scope beyond these two issues.

## File Ownership
Yours: `scripts/run_skill_eval.py`, `tests/test_run_skill_eval.py`, `skills/commander-delegated/**`, `evals/**` (fixture CLAUDE.md yes; task.md only within the purity constraint), issue comments on #126/#127. Fences: NOT `skills/workbench/scripts/**` (engine — float first), NOT `skills/commander/**` core doctrine unless the wording fix genuinely lives in `references/commander-core.md` (then flag it loudly in the PR body), NOT installer/index unless a new file requires a bundle entry. Findings: `.agent-work/issue-126-127/` INSIDE your worktree; never write main-checkout canonical LESSONS/AGENT_FEEDBACK.

## Workspace
Worktree: `C:\Programs\constellation-wt-126-127` — branch `constellation/issue-126-127`, base 76056ab (clean main), created via `git worktree add`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-126-127` (forward slashes — backslash args mangle in the Bash tool) — must exit 0; paste output. Server-side merge is the Admiral's; never merge locally.

## Inherited Context
- MSYS `/c/...` paths are unreadable by Windows `py`; pipe file content via `cat | py -c "...sys.stdin..."` or use `C:/` forward-slash paths.
- Never `pytest | tail -1` — pipes mask exit codes; run pytest bare and paste the tail separately.
- Counts and distribution claims command-derived with pasted output (e.g. `uniq -c`), never eyeballed from a log tail.
- Never round-trip shipped JSON templates through json.load/dump; surgical text edits only.
- Drive any engine spine of your own from THE REPO'S templates/scripts in your worktree, not installed copies.
- New files are invisible to `git diff` until staged; say so in evidence.
- Any crew you spawn must deliver its full report as its final message before idling.
- Long eval runs: launch via your Bash tool with run_in_background and poll the run directory / process, or set the Bash timeout ≥ the eval timeout; never let a 2-minute default kill a 30-minute run.

## Pre-empted Steps
Understand is largely pre-answered by the two issue bodies + this order + the #126 opus-diagnostic comment; cite them rather than re-deriving. Full plan/execute/reconcile spine still applies.

## Data Locations
- Honest-pass reference workspaces (READ-ONLY ground truth for engine-written spines): `C:\Users\fredc\AppData\Local\Temp\constellation-eval-zecv2779\run-1\` and `C:\Users\fredc\AppData\Local\Temp\constellation-eval-vp5l6ob_\run-2\` — each contains a genuine engine-driven spine.json with an `engine_session` lease block. COPY anything you need into your worktree findings dir early; temp dirs can vanish.
- Fabrication example: described in #127 body (attempt 6); the epic archive `.agent-work/archive/2026-07-10-epic-101/harvest/live-acceptance-*.json` (main checkout, read-only) holds all ten acceptance verdicts.

## Budget
- **Model tier (required):** inherit session model for the commander (judgment-heavy wording + instrument design). Eval subject runs are sonnet by harness default — that's the point. Crew (reviewers) may run one tier down.
- Expect a LONG session dominated by eval wall-clock (each measurement round ≈ 3 runs × 15–35 min; the harness runs them sequentially). Plan wording iterations in batches; 2–3 measurement rounds is a realistic budget. If out of runway, ship Phase 1 + the grader fix green and return wording iteration as a continuation.

## Stop Conditions
Stop and return when: the provenance check cannot pass the honest references without also passing the fabrication pattern (instrument contradiction — needs Admiral); wording fixes demand engine or commander-core changes beyond your fences; suite pre-broken on base; or context gaps. Asking up is always sanctioned.

## Return Shape
Final message = full report: Phase-1 check design + validation against both reference spines and the fabrication pattern, grader verdict-refinement summary, wording strategies tried with per-round measured verdicts (pasted run summaries, temp dirs kept), final compliance rate, suite result (command + tail), PR URL(s), isolation output, triage candidates, workflow feedback. Deliver BEFORE going idle. PR body via `gh pr create -F <tempfile>`, never `--body` heredoc.
