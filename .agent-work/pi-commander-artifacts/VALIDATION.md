# Commander artifact-flow validation — 2026-10-23 UTC

New `new --input TASK_FILE` runs carry task, plan, role handoffs, results and
receipts through files. Commander, Implementer and Reviewer remain Pi sessions.
System prompts stay role-specific and stable; per-invocation context is a named
artifact. Existing `--task` runs and persisted legacy runs keep their old protocol.
The unchanged external engine owns gates, evidence, overrides and leases.

## Verification

- 53 offline tests pass and TypeScript checking passes. Tests use the actual
  external engine and mocked model sessions; they incur no API cost.
- The migration tests cover full plan/implement/review/accept, missing and wrong
  results, approved-artifact changes, repaired rounds and role-session continuity,
  parent integration recovery without a crew retry, retained BLOCK after provider
  failure, rejected errored APPROVE, explicit crew restart, exact output-contract
  inclusion, updated request limits, Markdown fences and native tool termination
  at the final allowed turn.
- Four existing shared-template evidence-convention tests pass. The additive
  Reviewer Result Artifact field does not change the engine or launcher APIs.
- A separate Pi Reviewer read actual source, ran the final 53-test suite and
  typechecking, and returned APPROVE. It had previously hit its 12-turn limit;
  its same session resumed for a focused final review, completing in 6 requests.
- The existing pi-commander client skill now prefers task-file input and points
  callers to receipts and usage. Its repo copy and installed Codex/Claude copies
  passed skill-creator quick validation.

## Hosted workflow fixture

Disposable target: `/tmp/pi-commander-artifacts-live-XeNk37`.
Run: `.constellation-pi/fixture` under that target.

The task was to produce exactly three bytes, 34 32 0a (`42` and newline), then
independently verify them. No GPU reads, compute, containers, dependency installs,
service changes or operations on running workloads were performed.

The first attempt exposed a real contract gap: the Commander did not spell out
the exact output headings/status enum. Implementer wrote bullet fields with
`success`; validation refused it and the parent stayed at implementation. The
Commander then tried drafting the next role's handoff under its still-current
role tools, exhausting its turn budget. No invalid result advanced the engine.

The fix puts a mechanical Output Contract directly in each generated handoff,
using the same field/status definitions as the validator. Pi's native terminating
tool result now ends artifact invocations after plan submission, dispatch or
result delivery, instead of asking the model for another explanatory turn.

The supervising agent explicitly recorded `restart-crew` authority and reason,
blocked/released the unfinished first crew invocation, and preserved its files.
The same Commander/Implementer sessions continued under the unchanged task and
plan with a fresh handoff/result pair. The answer was already byte-correct from
round 1, so the second round verified it and delivered a valid result. A separate
Reviewer independently reproduced the byte count/hex check and returned APPROVE.

Plan execution and final fixture closeout used explicit supervising-codex
waive/start/advance operations. They were not recorded as human approvals. The
fixture reached terminal engine state with its Commander lease released. The final
Commander message is the dispatch_crew tool result; each crew's final message is
its submit_result tool result. No extra explanatory model response was requested.

## Timing and known estimated cost

The post-restart implementation + review execution took 145.263 seconds. This
excludes the first attempt and the intervening development pause; it is not a
clean before/after latency benchmark. Per-request timings, first response times,
cache reads/writes and outcomes are retained in the events ledgers. Parent elapsed
time includes crew wait and must not be added to crew elapsed time as sequential
work.

| Fixture stage | Known estimated USD |
| --- | ---: |
| Initial plan | 0.03942195 |
| Failed initial implementation/Commander continuation | 0.23750895 |
| Implementation after explicit restart | 0.19040850 |
| Independent fixture review and Commander dispatch | 0.20183205 |
| Fixture total | 0.66917145 |

The fixture used 7 workflow invocations and 50 model requests across the original
attempt and recovery; 2 interrupted requests have unknown usage. The request ledger
subtotal agrees with persisted run usage. Its full report is `validation.json` in
the disposable target.

Independent code review used $0.30506910 initially and $0.31104345 on resume, with
1 interrupted request having unknown usage. Known combined fixture + code review
estimate: $1.28528400. These are Pi model-catalog estimates, not provider invoices;
unknown usage is not treated as free. Review result and session evidence remain
at `/tmp/pi-commander-artifacts-review`.

## Deliberate limits

This remains the narrow four-stage integration, not the full installed Commander
or Implementer skill workflow. Files and referenced evidence carry the assignment;
shape/freshness/hash checks do not prove semantic correctness. Human approvals
remain explicit. Only the entry task/handoff and generated artifacts are bound by
hash; referenced project files remain live working context. Role/state tool changes
can still affect provider caching even though the role prompt is stable.
