# Mission frame — issues #130 → #131 → #129

**Intent.** Three sequenced issues, each de-risking the next: (1) make the eval
runner survive its own process death; (2) add an append-only engine journal that
raises spine-fabrication cost; (3) measure whether round-2 completion wording drives
sonnet to terminal spine completion on a now-durable runner.

Map note: skill-source repo, no `docs/agents/` overlay. The frozen Admiral launch
order + the three issue bodies + PR #128 + the #126 measured comments ARE the map;
substitution recorded at the context gate.

## Phase 1 — #130 runner durability

Diagnosis (from preserved `constellation-eval-jze6u34f`): run-0/run-1 finalized
`completed-fail` (exit 0) — runner alive through both. run-2 stuck `"launched"`,
0-byte transcript. The runner PROCESS itself stopped before its own 2400s deadline
could fire (never wrote final meta, never reaped). Root cause: deadline enforcement
lives ONLY inside the runner process (`launch_agent`'s poll loop), so runner death =
deadline never fires = orphaned `launched` meta + a watcher hung forever on an
EXITCODE sentinel. The both-crews run (subject + implementer + reviewer = 3
concurrent `claude` trees) is peak resource pressure, the most likely moment for the
runner or a sibling to be OS-killed / lose its background-shell parent. The 0-byte
transcript is NOT a streaming bug: `claude -p` emits its result to stdout only at the
END, so a mid-run subject legitimately has an empty transcript — corroboration that
run-2 was still in flight when the runner died, not the cause.

Design (within the issue's stated space):
1. **Resumable meta + loop.** `run_scenario` becomes idempotent over an existing
   `temp_root`: `--resume <dir>` re-adopts finalized run-N metas (kept, counted,
   not re-launched), adjudicates orphans, then launches only the remaining runs.
2. **Independent wall-clock watchdog.** An orphan (`launched` meta) is adjudicated
   OUTSIDE the dead process: re-score its workspace — all process checks green =>
   `completed-pass` (monotone carve-out, same as `timeout-checks-green`); else
   FENCED (`inconclusive`, never fails the corpus). Adjudicable + resumable.
3. **Heartbeats in meta.** `launch_agent` stamps `heartbeat_at`/`elapsed_seconds`
   into the launch meta on a schedule, so a watcher (my Phase-3 poller or a
   re-invocation) distinguishes "runner alive, subject working" from "runner dead"
   without waiting the full 2400s.
4. **Per-run isolation in-process.** `_run_once` wrapped so one run's unexpected
   exception fences THAT run (errored) and the loop continues.

Regression bar: a kill-9 of the runner mid-measurement leaves resumable, adjudicable
state — simulated in tests, no real sonnet run.

## Phase 2 — #131 engine journal sidecar (ENGINE FENCE LIFTED, journal emission only)

Design: `checklist_engine.main()` appends one line to `<spine>.journal` per
SUCCESSFUL mutating verb — `{ts, session_id, verb, task, evidence_id, seq,
prev_hash, hash}` (monotonic seq + hash-chain). Append-only; never read by the engine
itself (fully backward compatible — journal-absent spines keep working everywhere).
The eval `spine_completed` check cross-verifies journal-vs-spine when a journal is
present; **grandfather policy**: a journal-ABSENT but lease-valid spine still passes
(the two ref-honest workspaces predate the journal). Bar: fabrication-cost >
work-cost, not tamper-proofness.

Float-first triggers honored: any engine change beyond journal emission → float.

## Phase 3 — #129 round-2 wording measurement

Metric = TERMINAL completion (archive + `work-complete.txt`), not engine entry.
Measure round-2 clause on the durable+journal runner, sonnet, 3 runs. Target ≥2/3.
Iterate completion-side wording (commander-delegated SKILL.md / fixture CLAUDE.md
only; task.md purity is a standing human decision) if short. Honest-null after ≥3
strategies is a complete result.

## Untaken roads (design-it-twice / bias-to-yes, surfaced not hidden)

- **Separate supervisor process** for Phase 1 instead of resumable re-invocation:
  rejected — heavier, and the launch order explicitly names "the re-invoked runner
  on resume" as the watchdog vehicle; resume keeps the runner a single testable unit.
- **Journal as the sole provenance source** (drop the lease/grammar checks):
  rejected — breaks the grandfather case and exceeds the "small, append-only" bar.
- **Per-run subprocess isolation** (each run a fresh `python run_skill_eval` child):
  deferred — resumability already delivers cross-death isolation; in-process
  try/except covers sibling-exception isolation at a fraction of the complexity.

## Out of scope

Engine semantics beyond journal emission; DEFAULT_MODEL; task.md purity; anything
beyond these three issues. All → float to Admiral.
