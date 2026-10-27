# Artifact invocation validation — 2026-10-23 UTC

The bounded Implementer path consumes the existing Markdown handoff by path,
records a snapshot/hash and stable role-prompt version, writes the named result,
and returns a receipt. It owns a narrow delivery gate in the unchanged engine;
it does not advance an external Commander or claim human acceptance.

## Offline checks

42 tests pass with the explicitly configured external source engine and Python
3.12. TypeScript checking and git diff whitespace checks pass. The existing
Commander plan/approve/implement/review/repair/accept path remains covered.

New checks exercise legacy Delivery paths and explicit Result Artifact fields;
missing, stale and mismatched results; partial returns; errors after submission;
input changes; locks; reuse of the same session; explicit interrupted-attempt
recovery; recovery before and after terminal engine advancement without another
model request; stable role prompts; request timing and unknown usage; usage report
reconstruction. The shared Constellation template's four existing evidence-
convention tests also pass. No dependency installation was needed.

## Hosted artifact fixture

Sonnet received only a snapshot location, original input location, content hash,
working directory, gate and result location. The handoff itself specified the
entire assignment and result contract. It created answer.txt containing exactly
42 and a newline, verified its bytes, wrote result.md and called submit_result.
The invocation advanced its delivery gate and released its lease. The CLI receipt
contained no duplicate task narrative.

- Elapsed invocation: 51.941 seconds (runtime 51.847 seconds).
- Model requests: 7; all returned usage. First streamed-content latency was
  28.890 seconds for the first request and roughly 0.95–1.73 seconds thereafter.
- Pi model-catalog estimated usage: $0.04243620. The usage report's per-request
  sum agrees with the invocation total. Subsequent requests reported cache reads.
- Running invoke again returned the existing result with no additional request.
- Fixture run: /tmp/pi-artifact-live-6jdMd5/.constellation-pi/invoke-e84291b60bae76e9

This tiny fixture demonstrates transport, delivery and accounting, not a general
engineering productivity or cache-performance benchmark. No GPU operations ran.

## Independent review

A separate Pi Reviewer inspected actual source, tests and legacy compatibility,
ran the then-current 38-test suite, and independently verified the final telemetry
changes with targeted tests and typechecking. It returned APPROVE. Four additional
coordinator-run regressions brought the final suite to 42 tests without further
production changes beyond those reviewed.

The first review invocation hit its 20-turn budget before submitting a verdict.
It spent several calls printing code commentary instead of exercising behavior.
The same session resumed with an 8-turn ceiling and finished in four requests.
This is still workflow friction, not an unattended-workflow success claim.

Review recorded estimated usage: $0.46512900 initial + $0.09442740 resumed.
Initial review had one interrupted request with unknown usage. Known combined
fixture/review estimate: $0.60199260; this is not a reconciled provider invoice.
Review result/session metadata remains at /tmp/pi-artifact-independent-review.

## Deliberate limits

Input/output shape and freshness checks do not prove the semantic truth of crew
claims. Independent review still matters. Only the entry handoff is snapshotted;
referenced project documents remain live references. Existing Commander prompts
have not been migrated to artifact-based input. Direct Claude/Codex launches can
use the same additive template field; their accounting adapters are future work.
