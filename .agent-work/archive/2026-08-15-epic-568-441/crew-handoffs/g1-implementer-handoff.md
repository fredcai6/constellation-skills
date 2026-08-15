# Implementer Handoff — #441 transactional binding store

## Gate

`g1`

## Task

Implement one rail-owned portable transaction for every binding-registry
writer, unify acting-agent identity validation, validate contained checklist
claims, and reap only positively dead entries.

## Protected Intent

Concurrent PostToolUse claim/release and SessionStart writers preserve all
serially valid updates. Readable active leases survive regardless of age.
Explicit engine release, journaling, child semantics, actor/PID liveness, and
durable-root behavior remain unchanged.

## Test Mode

TDD required. First prove reviewed base `065445de` loses an update under the
production spawn topology or the exact `disable-binding-transaction` mutation.
If that topology cannot discriminate, return an honest scoped null and stop.

## Close Criteria

- One stable sibling lock file, never the replaced registry, is held from
  before load through safe reap, mutation, unique-temp close/flush, replace,
  cleanup, and unlock.
- POSIX uses nonblocking `flock`; Windows initializes one byte, seeks to zero,
  locks/unlocks the same byte with `msvcrt`, and closes temp handles before
  replacement. Acquisition is bounded and all lock/filesystem failures fail
  open without raising or mutating the registry.
- Claim, release, and SessionStart all mutate through the transaction seam.
- `spine_rail.is_usable_agent_id` is the sole 1–64 ASCII alnum/`_`/`-`
  predicate; gauge delegates to it.
- Claims require a resolved contained `.agent-work/<work-id>/<name>.json`
  readable JSON checklist, including absolute paths; traversal, symlink escape,
  non-file, malformed JSON, missing target, and validation/open races bind
  nothing. Release resolves its recorded target from the locked snapshot first
  and still removes moved/deleted entries.
- Transaction-internal reap removes malformed/empty records, readable released
  targets, and missing targets only after a parseable aware timestamp reaches
  24 hours. Missing targets with untrustworthy age and all readable active
  targets remain.
- A retained older-than-grace active binding still drives production Stop for
  its identity while a foreign second identity does not.
- Real spawned claim writers and a spawned SessionStart-versus-claim race
  produce valid final JSON retaining every expected serial update.

## Allowed Scope

- `scripts/hooks/spine_rail.py`
- `scripts/hooks/gauge_writer_hook.py`
- `tests/test_spine_rail.py`
- `tests/test_gauge_writer.py`

Existing tests in both test files may be reseeded or rewritten where their old
scenario relies on absolute claims bypassing validation or divergent identity
predicates.

## Specific Exclusions

- #441 does not change checklist-engine leases or journals.
- #441 does not change child ownership, actor identity, PID liveness,
  durable-root discovery, PID-less worktree cleanup, or historical registries.
- Do not edit any file outside the four paths above. Workflow artifacts and the
  required result are local-only delivery state, not part of the code blast
  radius.

## Constraints

- Stdlib only; hook path stays fail-open and bounded.
- Lock retry budget and 24-hour grace are named constants and directly tested.
- Stable lock target is a sibling such as `.spine-rail-binding.json.lock`, not
  the registry inode replaced by `os.replace`.
- Readers retain current absent/corrupt/ambiguous/inaccessible fail-open
  behavior.
- Linux tests must pass. Keep spawn workers module-level/picklable and Windows
  compatible; record Windows-specific uncertainty but do not mask Linux red.
- Use your normal file-edit tool for edits; never shell/Python rewrites of
  source files.
- Drive the Implementer workflow through the checklist-engine CLI against
  `.agent-work/epic-568-441/g1-implementer-plan.json` (`--file <path> <verb>`);
  never hand-edit that engine JSON. `m0-context` is already complete;
  `m1-transaction` is `in-progress` with `p1`/`c1` already attested (RED
  observed against reviewed base `065445de`, evidence recorded) — resume from
  there, obtain GREEN on `c2`, then continue `m2-validation-reap`,
  `m3-writers-routing`, `m4-verify-report` in order. The lease is currently
  held by `constellation/epic-568-441/g1/implementer/attempt-2` (claimed_by
  `implementer`) — you are running as that identity; do not re-claim.

## Map Anchors (inbound)

- **Map entry point:** degraded; start from the hash-pinned `README.md`
  mechanism doctrine and this handoff. Do not invent map ids.
- **Structural:** rail store and its claim/release/SessionStart writers; gauge
  identity consumer; focused rail/gauge tests.
- **Capability:** serializable discovery, consistent identity, safe cleanup,
  retained Stop routing.
- **Constraints/assumptions:** fail-open bounded hooks; explicit engine lease
  lifecycle unchanged; Linux green required.
- **Decision anchors:** full read-reap-mutate-replace transaction.
  @grade: settled/human · leans g1
- **Decision anchors:** stable non-replaced sibling lock.
  @grade: settled/measured · leans g1
- **Decision anchors:** readable active never age-reaped.
  @grade: settled/human · leans g1
- **Decision anchors:** rail-owned identity allowlist.
  @grade: settled/measured · leans g1
- **Decision anchors:** contained checklist claim, recorded-first release.
  @grade: settled/human · leans g1
- **Decision anchors:** 24-hour missing grace and short lock budget.
  @grade: settled/inherited · leans g1
- **Evidence expectations:** fixed run `epic-568-441-g1-attempt-1`; test id
  `test_spawn_binding_transaction_red_green`; base `065445de`; mutation
  `disable-binding-transaction`; expected red `lost-update`; green
  `all-entries-retained`; five named adapter/failure tests.
- **Map confidence flags:** binding topology is unmapped; return this gap, do
  not widen scope.

## Deliverable Path Check

- **Committed** — `scripts/hooks/spine_rail.py`; `git check-ignore` exit 1.
- **Committed** — `scripts/hooks/gauge_writer_hook.py`; exit 1.
- **Committed** — `tests/test_spine_rail.py`; exit 1.
- **Committed** — `tests/test_gauge_writer.py`; exit 1.
- **Local-only** — `.agent-work/epic-568-441/crew-handoffs/g1-implementer-result.md`;
  intentionally under workflow state and not counted in the four-file diff.

Exact command run before dispatch:
`git check-ignore scripts/hooks/spine_rail.py scripts/hooks/gauge_writer_hook.py tests/test_spine_rail.py tests/test_gauge_writer.py`; exit 1.

## Required Evidence

Load-bearing:

- Exact base-red/mutant-red and green commands/output for run
  `epic-568-441-g1-attempt-1`.
- Production spawned final-JSON/all-entries proof and mixed-writer serial
  outcome.
- Named tests:
  `test_binding_lock_contention_fails_open`,
  `test_binding_lock_timeout_fails_open`,
  `test_binding_lock_api_failure_fails_open`,
  `test_binding_replace_failure_fails_open`, and
  `test_windows_lock_adapter_contract`.
- Exact four production/test paths from `git diff --name-only`; count 4.

Confirmatory: identity/path/reaper matrices, wiring grep, and full focused output.

The result must contain these exact machine-copyable fields:

- `Return status: complete`
- `run_id: epic-568-441-g1-attempt-1`
- `test_id: test_spawn_binding_transaction_red_green`
- `base_revision: 065445de`
- `mutation: disable-binding-transaction`
- `expected_failure: lost-update`
- `post_change: all-entries-retained`
- `adapter_failure: four-cases-covered`
- `mixed_writer: sessionstart-claim`
- `blast_radius: 4-files`

## Wiring Grep

Run one command covering every new production symbol, exclude definitions and
tests, and state the external call-site count. Zero is a stop condition.

## Verification Commands

```bash
pytest -q tests/test_spine_rail.py::test_binding_lock_contention_fails_open tests/test_spine_rail.py::test_binding_lock_timeout_fails_open tests/test_spine_rail.py::test_binding_lock_api_failure_fails_open tests/test_spine_rail.py::test_binding_replace_failure_fails_open tests/test_spine_rail.py::test_windows_lock_adapter_contract
pytest -q tests/test_spine_rail.py tests/test_gauge_writer.py
```

## Suggested Model Tier

Stronger — cross-platform multiprocess serialization and a lifecycle-adjacent
retention boundary require high reasoning.

## Authority

The Admiral launch order and approved Commander plan settle every policy above.
Implementation choices inside the private transaction helper are delegated.

## Stop Conditions

Stop and return for any need to reap readable active leases, change engine
lifecycle/journal/child/PID behavior, exceed the four files, use a stale
lockfile protocol, or claim concurrency proof from a topology that stays green
when the transaction is disabled.

## Return Format

Write the complete `IMPLEMENTER_RESULT` to
`.agent-work/epic-568-441/crew-handoffs/g1-implementer-result.md` before ending.
Include files changed, TDD proof, exact outputs/exit codes, assumptions, stop
conditions, out-of-scope observations, and workflow feedback. The artifact is
the delivery; any message is courtesy only.
