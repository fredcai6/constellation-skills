# Launch Order: `commander-runner — #130`

Commanders start cold. Everything you need is pasted below.

## Mission
Harden the eval runner so a runner-process death mid-measurement leaves resumable, adjudicable state instead of a silent hang. Deliverable: one green, reviewed PR.

**Issue #130 (verbatim):**
From the 2026-07-10 round-1 measurement (#126 / PR #128 report): the eval runner **died ~12 minutes into run-2** — the only run whose subject spawned BOTH implementer and reviewer crews — before its own 2400s deadline fired. meta.json stuck at "launched", transcript/stderr 0 bytes, no finalization, and the watching session idled 4.5h on an EXITCODE line that never appeared. PR #125 fixed the direct-child pipe hang; this is the **runner-process-death** case it does not cover.
**Hardening directions (design space, not prescription):**
- **Per-run isolation:** each subject run launched/finalized by a unit that survives sibling failures, so one dead run can't take the whole measurement down.
- **Resumable meta:** meta.json written incrementally (launched → heartbeats → finalized) so a dead runner leaves an adjudicable record and a re-invocation can resume the remaining runs instead of restarting.
- **Independent wall-clock watchdog:** deadline enforcement must not live only inside the process being watched. A watchdog (separate process or the re-invoked runner on resume) reaps runs whose deadline passed and finalizes their meta as infra-fenced.
- Diagnose WHY the runner died on the both-crews run (0-byte transcript suggests the streaming path when the subject's own subprocess tree deepens) — the fix should address the cause, not just the blast radius.
**Regression bar:** a `kill -9` of the runner mid-measurement must leave state a re-run can resume and adjudicate; tests should simulate this WITHOUT a real 30-min sonnet run.

## Prior-Wave Verdicts (pasted)
Your base `d524b41` (current main) already includes wave-1 PR #197, which changed `scripts/run_skill_eval.py`: added `stable_corpus_id()` (install-path-invariant hashing; 3 id sites rewired) and an arm-construction note in the module docstring. Your durability work is in the runner-lifecycle/meta/watchdog paths — do NOT alter #197's corpus_id hashing; build alongside it and keep its test `test_corpus_id_install_path_invariant` green.

## Pre-Rulings (overridable with evidence)
- Prioritize **resumable meta + independent watchdog** (the two that make a dead runner adjudicable) over a full per-run-process re-architecture — pick the smallest design that meets the regression bar; if you judge per-run isolation is required to meet it, do it and justify.
- The regression test MUST simulate runner death without a real model run (e.g. a fake/stub subject that the test can `kill -9`, or an injected death point) — a 30-min sonnet run in the suite is unacceptable.
- Diagnose the root cause of the original 0-byte-transcript death and address it, not just the blast radius — state your root-cause finding in the report even if the fix is blast-radius containment.

## Honest-Null Clause
A measured negative is a complete deliverable. If PR #125's fix already covers more of the process-death case than #130 assumes, report exactly what's covered vs. still-exposed with evidence.

## Inherited Latitude
Choose the durability design, implement, test, open the PR. FLOAT: a re-architecture that changes the eval harness's public contract or the arm-construction seam; any change to #197's corpus_id behavior; any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `scripts/run_skill_eval.py` and its runner-support modules, plus `tests/test_run_skill_eval.py` (and any new runner test file). Do NOT touch `scripts/init_work_area.py`, `scripts/stage_feedback.py`, `scripts/checklist_engine.py`, or `scripts/hooks/spine_rail.py` (other commanders own those).

## Workspace
Absolute worktree: `C:/Programs/cs-wt-runner` — branch `fix/runner-durability-130`, base `d524b41` (current main), provisioned via `git worktree add -b fix/runner-durability-130 C:/Programs/cs-wt-runner main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-runner` — must exit 0; paste output into your report.
PR integration = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** (1) multiline `gh --body`/PR body → temp file + `gh pr create -F <file>`; heredoc and `@'...'@` both fail PS 5.1 `--body`; in the **Bash** tool (Git Bash) `@'...'@` is NOT a commit construct — use a real heredoc or quoted `-m`. (2) Use `py`, not bare `python`. (3) `kill -9` / process-tree semantics differ on Windows — your test's death simulation must work on this Windows box (use Python's process APIs, e.g. `Popen.kill()` / `psutil`, not a POSIX-only `kill -9` shell call). (4) Verify your worktree.
**Active lesson `test-harness-concurrency-failsafe` (DIRECTLY relevant — you are testing runner/process lifecycle):** test harnesses that drive real concurrent file I/O or helper threads need try/except with a guaranteed stop-signal in `finally` and `daemon=True` helper threads — a writer thread dying on a transient OS error without signaling stop leaves a non-daemon reader spinning forever and hangs pytest. This bit the epic-178 TF9 test on a Windows `os.replace` sharing violation. Apply it rigorously to any watchdog/heartbeat test you write.
**Reference:** the original incident report is in the #126/PR #128 material; the #145 measurement harvest under `.agent-work/dispatch-126-127/harvest-129-131/dead-runner-evidence/` (read-only, main checkout) has the actual dead-runner meta.json/transcript artifacts if you want the real failure shape.
Run the existing suite before and after; all pre-existing tests stay green.

## Budget
- **Model tier (required):** opus. Process-lifecycle/watchdog/resumability with concurrency and Windows-process subtlety; correctness stakes on the measurement infra.
- **Compute/time:** bounded (no real model runs); checkpoint and return if you near a session limit.

## Stop Conditions
Stop and return when: meeting the regression bar requires a public-contract re-architecture (float first); the process-death case is already covered (report the null); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Write your report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-2/W2-130-REPORT.md` BEFORE going idle: verdict, root-cause finding for the original death, the durability design + why, evidence (the runner-death simulation test name + green output proving resumable/adjudicable state after a kill; full suite green), PR URL, map impact, triage candidates, workflow feedback (stage the fenced trio, name its path), and your isolation-script output. Open the PR with `gh pr create -F <bodyfile>` targeting main; title `fix(evals): runner durability — resumable meta + independent watchdog (#130)`. Post the verdict, then go idle.
