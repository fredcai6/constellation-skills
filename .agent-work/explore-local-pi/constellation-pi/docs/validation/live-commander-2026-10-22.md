# Hosted Commander validation — 2026-10-22

Outcome: a Haiku Commander planned a bounded JavaScript change, dispatched a separate
Pi Implementer, recovered that same session after its turn limit, dispatched a separate
Pi Reviewer, and reached terminal engine state with the lease released.

## Task and fixed inputs

Implement slugify(string): lowercase; replace runs outside ASCII a–z/0–9 with a
hyphen; strip edge hyphens. Only slugify.mjs could change. Four fixed Node tests covered
punctuation/whitespace, edge separators, empty input, and digits.

Before implementation: four tests failed with `not implemented`. After implementation:
all four passed. The root test driver independently reran the tests and verified these
fixed-input SHA-256 hashes had not changed:

- AGENTS.md: b42d314fa54433769d95dc5d8528a6e17902addeb53a3d9cf9d60df413c8de87
- slugify.test.mjs: ae87aac240cb052a6cd7bfb139f7817a41cd4c114697eea4f273a5ce408c6738

## What the run exercised

- Commander JSONL resumed across four chat invocations.
- Implementer and Reviewer had distinct Pi session files, tools, and engine checklists.
- A plan error was caught before implementation: `.trim()` removes whitespace, not
  hyphens. Commander revised the plan to use a regex after test-driver feedback.
- The first Implementer invocation edited the function but hit its six-turn limit
  before testing/submitting evidence. The implementation gate stayed open.
- The same Implementer session resumed, ran tests, and submitted COMPLETE evidence.
- Reviewer independently read the inputs/implementation, ran tests, and submitted APPROVE.
- Final engine projection had `active: null` and `lease_held: false`.

Plan and acceptance gates used explicit parent-test-driver overrides with authority
and reason recorded. No human approval was fabricated. The ordinary human approval
path remains covered by offline integration tests; this hosted run tested its directed
override alternative. Implementation and review evidence gates were not waived.

## Cost and limits

Model: anthropic/claude-haiku-4-5 for every role. Six turns per invocation, 1024 output
tokens per response, 120-second timer, eight invocations including crews. The run
used all eight invocations. No model calls were made to close the acceptance gate.

| Role | Reported cost (USD) |
|---|---:|
| Commander | 0.04705555 |
| Implementer, including interrupted invocation | 0.04013600 |
| Reviewer | 0.02351325 |
| Total | 0.11070480 |

The earlier authentication-only check cost $0.001387 separately. These are Pi-reported
costs, not a billing reconciliation. GPU inference was unused.

## Changes prompted by the run

The directed override client lacked `start`, so a pending waived gate could not be
started through the same interface. Added start, terminal lease release, and a fresh
post-release state projection. A regression test covers the complete override lifecycle.
Crew prompts now name the repository and exact AGENTS.md path to reduce directory/file
confusion observed in the first Implementer invocation.

Final offline verification: 23 tests pass; TypeScript typecheck passes. The existing
Constellation engine source remains unchanged at revision 3ac7a1ab. The prior independent
review covers the initial version; this small follow-up is validated by its regression
suite and this live run rather than claimed to have that earlier source snapshot review.

## Evidence locations and scope

Run ID: cdd35dc0-8ee6-4549-8e2c-ec0e7ee84cdd. Original fixture:
`/tmp/constellation-pi-live-20261022`. A durable copy of its complete run and JSONL
sessions is stored locally under the project's ignored
`.constellation-pi/validation-20261022/` directory. Original absolute paths remain in
those records as provenance; this terminal fixture is not intended as a portable run.
Credentials were not included in that archive or committed to git.

This validates a narrow Commander path on a small task. It does not establish full
Commander-skill parity, performance on large tasks, or reliability across arbitrary
workloads. The six-turn interruption demonstrates recovery, not a reason to silently
raise the limits or assume the model did nothing before interruption.
