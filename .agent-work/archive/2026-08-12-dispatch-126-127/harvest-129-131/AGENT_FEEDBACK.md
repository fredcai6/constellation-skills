# Agent feedback — issues-129-131-cmd (worktree-local; NOT main-canonical per launch-order fence)

## issues-129-131-cmd

### What worked
- **Dogfooding the engine surfaced the real bug.** Driving my own commander spine through
  the journal-emitting engine (Phase 2) meant the Phase-3 subject exercised the journal for
  real — run-2 produced genuine `spine.json.journal` + `execute.json.journal` + g1/g2 crew
  journals. The feature was validated in the wild, not just in tests.
- **Live-kill proof over unit-sim.** The Admiral asked for a live proof, not only unit
  simulation. Two real-subprocess proofs (deadline tree-kills a live sleeper; runner-death +
  `--resume` adjudicates the orphan) were decisive and caught what unit sims assumed away.
- **Command-derived diagnosis beat the reported symptom.** The escalation said "heartbeats
  never engaged"; command-verifying the actual metas showed heartbeats DID engage and the
  real cause was a ~60-min background-task lifetime reap. Deriving the distribution from the
  evidence (per [[derive-distribution-claims-from-command]]) corrected a wrong root cause.

### What to improve
- **Field-name collision cost a misdiagnosis.** I named the runner heartbeat `heartbeat_at`
  while the engine lease uses `last_heartbeat`; an inspector looking for `last_heartbeat`
  saw "no heartbeat." Reusing the established field name (or namespacing clearly) would have
  avoided the confusion.
- **Final-meta overwrite destroyed liveness history.** Writing a fresh dict at finalization
  dropped `heartbeat_at`/`elapsed`, so finalized runs looked like the path never fired.
  Merge-onto-launch-record is the right default for any two-phase status file.
- **A long-lived background runner is the wrong shape for this environment.** The 3-run loop
  in one background task straddled the ~60-min reap. One short-lived run per invocation,
  driven by the commander, is reap-safe — but I only learned the reap window empirically,
  after burning a measurement round on it.

### Workflow signal
- The feedback/archive engine gates hard-require writing the MAIN-CHECKOUT canonical
  `AGENT_FEEDBACK.md`/`LESSONS.md` (durable_root resolves to the main checkout from a linked
  worktree), which directly conflicts with the delegated launch-order fence "never write
  main-checkout canonical LESSONS/AGENT_FEEDBACK." A delegated commander in a worktree cannot
  satisfy those gates without violating its fence. Resolved this run by waiving the gates with
  Admiral authority; a durable fix (e.g. the gate honoring a worktree-local feedback log, or
  the launch order granting a scoped write) is a triage candidate.
