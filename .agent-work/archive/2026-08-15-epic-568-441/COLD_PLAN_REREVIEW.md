# Cold Plan Rereview — epic-568-441

Verdict: **BLOCK** (`CP-03`, `CP-05` remain)

Scope: rereviewed only revised `execute.json`, unchanged `MISSION_FRAME.md`,
`COLD_PLAN_CRITIQUE.md`, and `PLAN_CRITIC_TRIAGE.md`. No source, launch order,
history, tests, or engine state was inspected.

## Finding disposition

| Finding | Disposition | Executable or matched gate |
|---|---|---|
| CP-01 | Repaired | The implementer contract explicitly requires a deterministic spawned SessionStart-versus-claim test; implementer and verification artifacts match `mixed_writer`, and the focused pytest command executes the scoped test files. |
| CP-02 | Repaired | The stable, non-replaced sibling lock identity and full transaction lifetime are explicit constraints; independent review must verify them and is gated by matched `verdict=APPROVE`, with focused tests as a command gate. |
| CP-03 | **Not repaired** | The platform mechanism is substantially specified, but neither a command-selected test nor a matched artifact field requires the triaged contention, timeout, lock-failure, and replacement-failure cases. |
| CP-04 | Repaired | The retained-active production Stop path and foreign-identity discriminator are explicit evidence requirements; integration matches `stop_retention=verified`, and focused pytest is a command gate. |
| CP-05 | **Not repaired** | Artifact matching was improved, but the categorical fields do not prove run freshness or the actual red/green and mutation observations requested by the finding. |

## Remaining blockers

### CP-03 — Failure-path coverage can still disappear while every gate passes

`PLAN_CRITIC_TRIAGE.md` accepts deterministic tests for contention, timeout,
lock failure, and replacement failure. Revised `execute.json` mentions
“injected POSIX/Windows adapter failure contracts” only as an evidence anchor,
and the integration imperative mentions adapter-failure evidence, but:

- it never explicitly requires deterministic contention, timeout, lock-API
  failure, and replacement-failure test cases;
- the focused pytest command does not select or name such tests; and
- `verification-result` has no `adapter_failure` (or equivalent) matched field,
  despite the imperative saying that evidence must be verified.

Add the four explicit failure cases to the test contract and add a matched
verification field such as `lock_failure_contract=verified` covering all four,
or provide a dedicated command gate selecting those tests.

### CP-05 — Fresh, discriminating proof is still reduced to unchecked labels

The revised artifacts match categorical values such as
`red_green=production-spawn`, `mutation_control=discriminating`, and later
`...=verified`. They do not carry or match a test identifier, reviewed base
revision, mutation identity, expected base/mutant failure, post-change result,
or run identifier/timestamp. Consequently an old or conclusory artifact can
satisfy `g1-integrate.c4`; the word “fresh” in its statement is not enforced by
the match. The missing adapter-failure match also leaves a named integration
proof outside the gate.

Add matched provenance/observation fields for at least test id, base revision,
mutation used, expected failing observation, post-change passing observation,
and run identity or timestamp, plus the adapter-failure verification field.
The exact four-file blast-radius match and reviewer `APPROVE` match are repaired.
