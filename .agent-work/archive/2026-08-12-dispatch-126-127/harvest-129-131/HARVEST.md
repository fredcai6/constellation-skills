# Harvest — issues #130 / #131 / #129 (commander-129-131)

Worktree-local durable evidence for Admiral harvest. Branch state: `constellation/issue-130`
(PR #132, #130 amended) and `constellation/issue-131` (PR #133, #131, stacked on #130).

## Deliverables
- **#130 runner durability** — `scripts/run_skill_eval.py` + `tests/test_run_skill_eval.py`.
  Resumable meta, orphan watchdog, heartbeats, per-run isolation, `--max-new-runs` reap-safe
  drive, subject-PID recording, preserved liveness in final meta.
- **#131 engine journal sidecar** — `scripts/checklist_engine.py` (append-only journal per
  mutating verb) + `evals/*/checks/spine_completed.py` (cross-verification, grandfather policy)
  + tests. Merging #131 requires a local skills reinstall (installed engine copies go stale).
- **#129 measurement** — round-1 adjudicated on the issue (0/3 terminal, confounded by the
  runner reap; run-2 = fenced environment death; round-2 wording unmeasured). Clean
  re-measurement returned as a continuation on the reap-safe runner.

## Root cause (command-verified, `constellation-eval-phase3-r1`)
Background runner reaped at **59.6 min total lifetime** (run-0 10min + run-1 20min + run-2
29.5min), **10.5 min before** run-2's own 2400s deadline. Heartbeats DID engage (run-2 meta
`heartbeat_at` + `elapsed_seconds=1771.5`); the "no heartbeat" report was a `heartbeat_at`
vs `last_heartbeat` field-name mismatch + a final-meta overwrite, both fixed. See
`harvest/phase3-r1-metas/`.

## Live proofs (real subprocesses, no claude)
- `harvest/live_kill_test.py` — driver spawning a real sleeper subject through the genuine
  launch_agent/resume machinery.
- Proof A: a 5s deadline tree-killed a live subject; meta finalized `timeout`; pid confirmed dead.
- Proof B (`harvest/proof_b.sh`, output `harvest/proof_b_output.txt`): killed the runner
  mid-flight → meta stuck `launched` → `--resume` adjudicated the orphan to
  `inconclusive/orphaned-runner-died`; recorded pid tree-killed the orphaned subject.

## Suite
`py -m pytest tests/ -q` → 600 passed, 2 skipped, 152 subtests.

## Triage candidates (routed at the triage gate)
1. Clean #129 re-measurement — continuation dispatch on the reap-safe runner (Admiral-accepted).
2. The feedback/archive engine gates require main-canonical `AGENT_FEEDBACK.md`/`LESSONS.md`
   writes, conflicting with the delegated worktree fence — durable reconciliation needed.
3. (Optional hardening) a detached external-watchdog process for deadline enforcement,
   deferred in favor of the simpler reap-safe one-run-per-invocation drive.
