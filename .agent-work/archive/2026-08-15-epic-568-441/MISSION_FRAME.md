# Mission Frame — #441 transactional binding store

## Intent

Strengthen the binding registry mechanism described by `README.md`'s
mechanically-enforced-rails doctrine: concurrent hook writers preserve every
valid binding, reject unsafe identities and claim targets consistently, and
remove only entries whose death is positively established.

## Affected capabilities

- Hook binding discovery: claim, release, and SessionStart share one registry.
- Context gauge routing: the same acting-agent identity selects both binding
  and transcript state.
- Turn-end enforcement: retained bindings continue to route Stop decisions to
  the correct readable checklist.

## Examples / events

- Two spawned PostToolUse processes claim different checklists at the same
  instant; the final JSON retains both records.
- A SessionStart bind races a PostToolUse claim or release; the transaction
  serializes their complete read/reap/mutate/replace sequences.
- A punctuation-bearing or 65-character agent id reaches both consumers; both
  reject it without writing.
- A readable active checklist remains bound regardless of age. A released
  checklist is removed; a missing target is removed only after the grace.

## Structural anchors

- Spine rail binding-store helpers and the three production writer call sites.
- Gauge writer identity and binding-key consumption seam.
- Focused rail and gauge tests, including a spawn-safe production-handler race.

## Governing constraints / assumptions

- Hook execution remains fail-open and bounded on lock or filesystem failure.
- Stdlib-only, portable advisory locking with crash release; no stale-lockfile
  lifecycle is introduced.
- The registry replacement is unique-temp and atomic on POSIX and Windows.
- Explicit checklist lease release remains mandatory; discovery cleanup never
  infers engine completion from age.
- Linux is the present proof platform. Windows-compatible structure is
  required, while Windows CI failures may remain recorded under the launch
  order.

## Decision anchors and pressure

- Transaction boundary: lock covers read, safe reap, mutation, and replace for
  every writer.
  @grade: settled/human · leans g1-implement,g1-review,g1-integrate
- Active retention: readable active leases are never reaped by age.
  @grade: settled/human · leans g1-implement,g1-review,g1-integrate
- Identity: one rail-owned 1–64 character allowlist governs both consumers.
  @grade: settled/measured · leans g1-implement,g1-review,g1-integrate
- Claim validation: claims require a contained existing JSON checklist;
  releases retain recorded-target compatibility.
  @grade: settled/human · leans g1-implement,g1-review,g1-integrate
- No engine lifecycle: journaling, child ownership, actor/PID liveness, and
  durable-root behavior remain separate waves.
  @grade: settled/human · leans g1-implement,g1-review,g1-integrate
- Bounded choices within inherited latitude: 24-hour missing-target grace and
  a short nonblocking-retry lock budget, both exposed as constants and directly
  tested.
  @grade: settled/inherited · leans g1-implement,g1-review,g1-integrate

## Claims / evidence surfaces

- A real multiprocessing spawn regression must be red on the reviewed base and
  green after the transaction; final registry JSON parses and contains every
  expected entry.
- Mutation control removes the transactional protection and makes the same race
  test fail.
- Focused tests cover all three writers, identity equivalence, contained claim
  validation, recorded release, and each safe-reap branch.
- The relevant broader non-Windows suite remains green.

## Map confidence / staleness / disputes

- The code map is unparseable and contains no citable binding-store packet.
  The context receipt therefore hash-pins `README.md` as the substitute and
  records the writer/consumer topology as unmapped. The plan includes explicit
  source confirmation and returns the gap to reconcile; it does not treat the
  substitute as a structural inventory.

## Out of scope

Checklist-engine lifecycle or journal changes, historical bulk backfill, child
references, actor identity, durable-root liveness, PID inference, PID-less
worktree cleanup, and changes outside the launch order's file ownership.
