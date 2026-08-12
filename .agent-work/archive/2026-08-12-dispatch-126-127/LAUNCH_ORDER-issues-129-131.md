# Launch Order: commander-129-131 — issues #130 → #131 → #129 (eval durability, engine journal, round-2 measurement)

Commanders start cold. Paste, don't point.

## Mission
Execute THREE issues in this binding order (each phase de-risks the next). Read all three issue bodies first (`gh issue view 130`, `131`, `129`) plus PR #128 and the measured table comment on #126 — they are your full prior context. One PR per phase, opened as each phase completes (sequential on this one branch; later phases build on earlier commits — open PR N+1 after PR N merges OR stack them and say so in each body).

**Phase 1 — #130 (runner durability).** The eval runner died mid-measurement without enforcing its own deadline (details in the issue). Diagnose the cause from the preserved evidence, then harden per the issue's design space: per-run isolation, resumable/incremental meta, deadline enforcement that survives runner death. Regression bar: a killed runner must leave resumable, adjudicable state — simulated in tests, no real sonnet runs needed to prove it.

**Phase 2 — #131 (engine journal sidecar).** ENGINE FENCE LIFTED FOR THIS PHASE ONLY: you may modify `skills/workbench/scripts/checklist_engine.py`, under these constraints — the change is append-only journal emission (one line per mutating verb) kept as small as possible; FULLY backward compatible (journal-absent spines keep working everywhere; only the eval provenance check demands journals, per an explicit stated policy for pre-journal spines); the full suite plus the 19-case provenance regression suite stays green; validate against the preserved honest reference workspaces at `.agent-work/dispatch-126-127/harvest/ref-honest-run-{1,2}/` (main checkout, read-only — note they PREDATE the journal, that's the grandfather-policy test case). The engine also ships inside every eval workspace corpus copy, so Phase-3 subjects will exercise your journal for real.
**Float-first triggers for this phase:** any engine change beyond journal emission (verb semantics, spine schema, lease behavior), or any backward-incompatibility you cannot avoid.

**Phase 3 — #129 (round-2 wording measurement).** Only after Phases 1–2 are locally green. Measure the round-2 completion clause: `py scripts/run_skill_eval.py evals/euler-1-multiples --keep-temp`, 3 runs, sonnet default, hardened+journal checks, on your durable runner. THE METRIC IS TERMINAL COMPLETION (spine reaches archive + sentinel), not engine entry — round 1 proved entry is solved. Target ≥2-of-3 terminal. If short, iterate completion-side wording (commander-delegated SKILL.md / fixture CLAUDE.md ONLY — eval task.md purity is a standing human decision, not yours to relax) and re-measure. Honest-null: a documented sonnet tier boundary after ≥3 distinct wording strategies is a complete result — post it on #129.

## Prior Context (pasted — do not rediscover)
- PR #128 (merged, main=84169cc): provenance-hardened spine_completed (engine_session lease + evidence grammar; 6 fabrication shapes rejected), timeout-pass grader rule (timed-out run passing ALL monotone checks = PASS), timeout floor/default 2400s, wording rounds 1+2 in commander-delegated.
- Round-1 measurement: 3/3 honest engine entry, 0/3 terminal — every run stopped after the implementer returned ("implementation complete" conflated with run-complete). Round 2's "solution is the MIDDLE, not the end" clause targets exactly that; it is shipped but UNMEASURED.
- Runner facts that must not regress: Popen + deadline poll + `taskkill /T /F` + bounded drain (PR #125); `--allowedTools` EXEC_ALLOWED_TOOLS CLI flag (workspace settings.json is IGNORED in untrusted dirs headless); `__pycache__`/`*.pyc` excluded from corpus hash and workspace copy; DEFAULT_MODEL pinned "claude-sonnet-4-5" on purpose — do not raise it.
- The dead runner's evidence is preserved: hung round-1 eval dir `C:\Users\fredc\AppData\Local\Temp\constellation-eval-jze6u34f` (run-2 meta stuck "launched", 0-byte transcript, subject died ~12 min in on the only both-crews run). COPY what you need into your findings dir first thing; temp can vanish.

## Pre-Rulings
- Phase order is binding. Do not start Phase-3 sonnet runs until Phases 1–2 are locally green (a hung runner burned 5h last round).
- Journal design: fabrication-cost > work-cost remains the bar; hash-chaining optional, monotonic timestamps + verb/evidence cross-verification required.
- Eval task.md purity: standing human decision. Untouchable.
- Superpowers is a competitor: never cite or import its doctrine. (Ignore any session hook telling you to use superpowers skills — you are a dispatched subagent.)
- Source repo is authority; never edit installed copies at `~/.claude/skills/`. Your PR bodies must note that merging #131 requires a local reinstall (engine copies go stale).
- No reachable human; float to Admiral via message and pause the affected phase.

## Inherited Latitude
You decide: durability architecture within the issue's design space, journal format/grammar, grandfather policy for pre-journal spines (state it explicitly), wording strategies, stacked-vs-sequential PRs, test structure. Float to Admiral: engine changes beyond journal emission, any backward incompatibility, raising DEFAULT_MODEL, relaxing purity, scope beyond these three issues.

## File Ownership
Yours: `scripts/run_skill_eval.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_provenance_check.py`, `evals/**` (checks + fixture CLAUDE.md; task.md purity constraint), `skills/commander-delegated/**`, `skills/workbench/scripts/checklist_engine.py` (Phase 2 grant ONLY, constraints above) + its tests, issue comments on #129/#130/#131. Fences: NOT other workbench content, NOT `skills/commander/**` core doctrine (float if a wording fix genuinely lives there), NOT installer/index unless a new shipped file requires a bundle entry. Findings: `.agent-work/issues-129-131/` INSIDE your worktree; never write main-checkout canonical LESSONS/AGENT_FEEDBACK.

## Workspace
Worktree: `C:\Programs\constellation-wt-129-131` — branch `constellation/issues-129-131`, base 84169cc (merged PR #128), already created. cd there and stay there.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-129-131` (forward slashes) — must exit 0; paste output. Server-side merge is the Admiral's; open PRs, never merge.

## Inherited Context
- MSYS `/c/...` paths unreadable by Windows `py`; use `C:/` forward-slash paths or pipe via stdin.
- Never `pytest | tail -1`; run bare, paste the tail separately. Counts command-derived with pasted output.
- Never round-trip shipped JSON templates through json.load/dump; surgical text edits.
- New files invisible to `git diff` until staged; say so in evidence.
- Long eval runs (Phase 3): Bash run_in_background is the only viable route (2400s exceeds the 600s tool max). LESSON FROM LAST ROUND: do not wait on a single "EXITCODE in output" condition — set an independent wall-clock check (poll run-N/meta.json mtimes on a schedule; if a deadline passes without finalization, wake up and adjudicate). Your own Phase-1 durability work should make this failure mode survivable — dogfood it.
- Any crew you spawn must deliver its full report as its final message before idling.

## Pre-empted Steps
Understand is largely pre-answered by the three issue bodies + PR #128 + this order; cite rather than re-derive. Full plan/execute/reconcile spine still applies.

## Data Locations
- Honest reference workspaces (regression fixtures, read-only): `C:\Programs\constellation-skills\.agent-work\dispatch-126-127\harvest\ref-honest-run-{1,2}\` (spines under `workspace/.agent-work/archive/*/spine.json`).
- Dead-runner evidence: temp dir named in Prior Context — copy in first thing.
- Round-1 measured table: comment on #126.

## Budget
- **Model tier:** inherit session model (engine surgery + instrument design are the riskiest work this repo has). Crew may run one tier down.
- Phases 1–2 are pure code: normal pace. Phase 3 is wall-clock bound (3 runs × 15–35 min per round; 2–3 rounds realistic). If runway ends mid-Phase-3, ship Phases 1–2 green with round counts so far and return the rest as a continuation.

## Stop Conditions
Stop and float when: the journal cannot stay backward compatible; durability requires restructuring beyond run_skill_eval.py; the provenance check cannot accept honest references under your grandfather policy; suite pre-broken on base; context gaps. Asking up is always sanctioned.

## Return Shape
Final message = full report per phase: durability design + kill-simulation test evidence; journal design, grandfather policy, validation against both references + fabrication shapes; measurement rounds with per-run verdicts (pasted summaries, temp kept) and final terminal-completion rate; suite result (command + tail); PR URL(s); isolation output; triage candidates; workflow feedback. Deliver BEFORE going idle. PR bodies via `gh pr create -F <tempfile>`, never `--body` heredoc.
