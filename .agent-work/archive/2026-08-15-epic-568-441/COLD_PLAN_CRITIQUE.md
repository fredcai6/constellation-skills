# Cold Plan Critique — epic-568-441

Verdict: **BLOCK**

Scope of review: only `MISSION_FRAME.md` and `execute.json` were read. No source,
tests, launch-order material, engine state, or history was inspected.

## Blocking findings

### CP-01 — The cross-writer race promised by the mission has no discriminating gate

The mission explicitly names a SessionStart bind racing a PostToolUse claim or
release. The execution plan requires one real spawned race through
`handle_post_tool_use`, while “all three transactional writers” is only a broad
matrix requirement. A two-claim PostToolUse race can prove one entry point was
made transactional while SessionStart or release still performs a split
read/reap/mutate/replace sequence.

Add an executable concurrency test covering at least one mixed-entry-point race
(SessionStart versus claim, and preferably SessionStart versus release), with a
barrier that forces the vulnerable overlap and assertions for the precise
serial outcomes. Require its red/green and mutation-control evidence in the
integration postconditions.

### CP-02 — Stable lock identity is not specified, leaving a replace/lock split-brain

The plan requires advisory locking plus atomic registry replacement, but never
states that the lock is taken on a stable sibling lock object that is not itself
replaced. Locking the registry file and then replacing it permits one process to
hold the old inode/file object while another locks the new one, defeating the
transaction on POSIX and creating sharing/replacement hazards on Windows.

Make the stable lock target and lifetime an explicit decision anchor: every
writer locks the same non-replaced sibling lock file before loading and keeps it
through cleanup, mutation, close/flush, and `replace`. Add a structural test or
review gate that rejects locking the replace target itself.

### CP-03 — “Portable” and “bounded fail-open” lock behavior is asserted but not tested

No executable gate injects lock contention, acquisition timeout, lock API
failure, or replacement failure. There is also no Windows-semantic test or
specified Windows contract. This matters because POSIX and Windows advisory
locking differ in byte-range behavior, file-handle/share semantics, and
replacement constraints. Allowing Windows failures to be merely recorded
cannot prove the mission’s required “Windows-compatible structure.”

Specify the platform contracts (including lock byte/range, file initialization,
seek position, handle closure before replacement, and error classes that fail
open), then gate deterministic contention/timeout and filesystem-failure tests.
At minimum, add a platform-independent fake/backend contract suite runnable on
Linux; record-only Windows CI may supplement, not replace, that proof.

### CP-04 — Retained-binding Stop routing is a named capability without an executable gate

The mission promises that a readable active binding survives age and continues
to route Stop decisions to the correct checklist. The plan asks for safe-reap
and identity matrices but not an end-to-end assertion that an old readable
binding is retained *and consumed by Stop routing* for the same acting identity.
A store-only retention test can pass while the gauge/Stop seam is broken.

Add a focused executable test that seeds an older-than-grace readable checklist,
runs the relevant discovery/cleanup writer, then invokes the production gauge or
Stop consumer and proves it selects that checklist. Include a second identity to
discriminate wrong-key or transcript-identity routing.

### CP-05 — Critical evidence is attestation-only, so the gate can pass without the proof

`g1-implement.c1` checks only for a complete result, `g1-review.c1` checks only
that a review artifact exists, and `g1-integrate.c4` has `check: null`. Thus the
named requirements for production spawn red/green, deterministic mutation
control, mixed writer coverage, freshness, and exact blast radius are not
machine-checkable. The two pytest commands prove only the final green state;
they do not prove base-red, mutation discrimination, or evidence freshness.

Give each critical evidence surface its own matched artifact fields (test id,
base revision, mutation used, expected failure, post-change pass, timestamp or
run identity, and four-file list), and make integration checks match those
fields. Also require the review artifact verdict to be `APPROVE` at the review
task itself rather than allowing any review result to satisfy that task.

## Non-blocking plan pressure

- Keep the implementation to one transaction helper plus thin writer calls;
  avoid a generalized storage/locking framework. The frozen exclusions already
  support this YAGNI boundary.
- “Contained existing JSON checklist” should be sharpened into executable cases
  for absolute paths, traversal, symlink escape, non-file targets, malformed
  JSON, and validation/open races; otherwise implementations can disagree while
  nominally satisfying the phrase.
- The mission says the degraded architecture-map gap is returned to reconcile,
  but `execute.json` has no reconciliation/consolidation item. Either add a
  bounded artifact gate for that handoff or remove the unexecutable promise.
