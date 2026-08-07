# g5 — Live acceptance + falsification (issue #106)

## Environment probe (feasibility)
- `claude --version` = 2.1.205 (Claude Code); `claude -p "Reply with exactly: OK"` = `OK`, exit 0.
- Corpus temp-install verified live: the runner installed all 15 constellation skills into `<systemp>/constellation-eval-*/skills` and copied them into `run-0/workspace/.claude/skills` (provenance asserted per run).

## Falsification evidence (agent-free, at the check level) — COMPLETE
Fabricated three run-dirs and ran the three real scenario process checks (euler-1) against each. This is the permanent, agent-free falsification the contract's FLOOR requires, and it exercises BOTH the gross-breakage variant and the sentinel-hole variant the g4 reviewer made binding.

| variant | spine_completed | artifact_present | tests_green | scenario verdict | meaning |
|---|---|---|---|---|---|
| **A — gross breakage** (in-progress spine, no deliverable) | FAIL | FAIL | FAIL | **FAIL** | the harness catches a corpus that can't drive the workflow — checks BITE |
| **B — sentinel-hole** (terminal spine + `eval-complete.txt`, NO solution/test) | PASS | PASS (sentinel) | PASS (sentinel) | **PASS** | documents the FLOOR hole exactly as g4-review predicted: the sentinel fallback lets "spine complete + sentinel but no deliverable" pass. Bounded, documented (evals/README limitation 1), and filed as triage candidate tc1 (make dry_run_launch synth real files → drop the fallback). |
| **control — genuine good run** (terminal spine + real solution + green test + sentinel) | PASS | PASS | PASS | **PASS** | a good corpus passes — no false red |

Also the runner's own agent-free modes, on all 3 scenarios: `--dry-run` → PASS (exit 0); `--dry-run-fail` → FAIL (exit 1). The mocked-end-to-end floor (fake subprocess + canned transcript through pass AND fail) is proven permanently by the g3 fake-subprocess tests in `tests/test_run_skill_eval.py`.

### g5-acceptance-discovered fix
Running the checks by hand with a RELATIVE run-dir surfaced a latent false-red in `tests_green.py` (pytest exit 4 usage-error when test paths were passed relative under `cwd=workspace`). Production was unaffected (the runner always uses absolute temp run-dirs), but hardened with `t.resolve()` across all 3 scenarios (commit b9382ba). Re-verified: control PASSes with a relative run-dir; dry-run/dry-run-fail unchanged; full suite 513 green.

## Live acceptance run (real headless N-of-M) — HONEST NULL (environment-blocked), machinery PROVEN

### The run happened for real and the runner machinery worked end-to-end
Command:
```
py scripts/run_skill_eval.py evals/euler-1-multiples --n 1 --m 1 --model claude-sonnet-4-5 --timeout 1100 --keep-temp --json
```
Ran 23:51:20 → 23:58:30 PDT (~7 min), exit 1. Verdict JSON (`.agent-work/issue-106/g5-live/probe-m1.json`):
```json
{ "status": "FAIL", "exit_code": 1, "completed": 1, "passed": 0, "fenced": 0,
  "corpus_id": "sha256:8fdbb15b…7856c", "source_commit": "2ef6c29…",
  "n_of_m": "regression-vs-variance smoke, not a statistical guarantee" }
```
Every stage of the runner functioned against a REAL headless agent: temp-install of all 15 skills, corpus id + `source_commit` computed and surfaced, `claude -p` launched with `cwd=workspace`, transcript captured, the three process checks executed, and the N-of-M verdict computed. The headless commander even loaded the corpus and drove toward crew dispatch (the transcript is an implementer crew member reporting a blocker back to the commander) — so the workflow machinery engaged.

### Why it is an HONEST NULL, not a corpus FAIL
The run classified `completed-fail`, but the cause is the ENVIRONMENT, not the corpus. The headless agent was systematically **permission-denied every file-creation path** (`.agent-work/issue-106/g5-live/live-run-0-transcript.txt`):
```
- Write tool: "Claude requested permissions to write"
- Bash heredoc: "Output redirection... was blocked"
- PowerShell Set-Content: "cannot be statically validated and requires manual approval"
```
A headless `claude -p` runs with no interactive approver, so every tool action needing approval is denied and the agent cannot produce `solution.py`/`test_solution.py`/a spine/the sentinel — regardless of corpus quality. The fix (launch with `--dangerously-skip-permissions` / an authorized `--permission-mode`) is itself **denied by this session's auto-mode classifier** ("Create Unsafe Agents … no user authorization naming this bypass"). So a live pilot cannot be executed in this session; this is exactly the launch order's sanctioned honest-null (environment blocks the live run), reported with exact evidence.

### Honest-null floor (raised per critic finding 1/7) — SATISFIED
The mocked end-to-end path IS exercised: `tests/test_run_skill_eval.py` drives `run_scenario` with a fake subprocess through BOTH a passing and a failing transcript (whole pipeline: temp-install → provenance → launch-seam → checks → classify → N-of-M), and the real `launch_agent` timeout/launch-error mapping is tested feeding the infra-fence. Dry-run alone is NOT relied on as the floor.

### Two harness findings surfaced BY running it for real (triage candidates)
- **tc2 — runner is not live-runnable as shipped:** `launch_agent` passes no `--permission-mode`, so a headless agent can create nothing and every live run is a permission-blocked false-red. The runner needs a permission strategy (an operator-authorized `--permission-mode`/bypass passed through to `claude -p`, documented in evals/README as a live-run prerequisite).
- **tc3 — infra-fence gap:** "agent exited 0 but was permission-denied all writes / produced zero workspace mutations" is currently `completed-fail` (a corpus FAIL), but it is an ENVIRONMENT block that should be FENCED (inconclusive) — the fence catches usage-limits/timeouts but not permission-sandbox blocks, so it can false-red a good corpus. A robust structural signal: agent exited 0 but the workspace is byte-unchanged from the fixture ⇒ inconclusive, not fail. (Interacts with the g2-ratified "exit-0-no-terminal = completed-fail" rule — route through the contract/review process, do not hot-patch.)

### Net g5 verdict
Falsification COMPLETE (gross-breakage fails all checks; sentinel-hole documented; good-run control passes; dry-run/dry-run-fail bite). Live machinery PROVEN end-to-end against a real agent. Live corpus verdict is an HONEST NULL (environment permission sandbox forbids headless deliverable creation, and the bypass is classifier-denied), with exact evidence pasted. Two harness improvements filed (tc2, tc3).

