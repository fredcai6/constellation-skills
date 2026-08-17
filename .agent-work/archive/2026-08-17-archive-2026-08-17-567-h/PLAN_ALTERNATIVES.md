# Plan alternatives (design-it-twice, scaled down)

Scale: two candidates authored directly by the Commander, not a parallel subagent panel —
this is a well-scoped, 2-3 string rewrite in one file with a bounded test surface, which the
"count/panel scaled by weight" rule sanctions as a fairly-easy call. Untaken road: a full
parallel-subagent plan-alternatives panel, skipped as disproportionate to the change size and
the Sonnet-tier budget note ("the hard part is measurement discipline, not reasoning depth").

## Candidate A — reasoning-only, no crew for the rewrite itself
The Commander edits `scripts/checklist_engine.py` and its pinned tests directly in this
context (already holds full context of the target strings from the `understand` source read);
cold-agent measurement subjects are still fresh Agent-tool dispatches, but the code edit itself
has no independent implementer/reviewer.
- Depth/locality: fast, single actor, no handoff overhead.
- Testability: still falsifiable via the pinned tests + fresh-process checks.
- Simplicity: fewer gates, less ceremony for a small change (decision:reduce-complexity leans
  this way on pure LOC).
- Risk: `_RAIL_STRINGS`/`_refresh_attach_hint` are the file's own-declared "single canonical
  enforcement source", consumed at every railed verb (claim/current/start/advance/attest/attach)
  and cited by `_shared/global-everyone.md`. A self-reviewed edit to a shared table with this
  blast radius has no independent check that the edit didn't leak into an untouched entry
  (e.g. a stray token substitution corrupting `mid-flight` while editing `early`).

## Candidate B — crew-gated implement+review for the rewrite, reasoning gates around it
Cold-agent measurement (before and after) stays reasoning-gate, driven directly — it produces a
diagnosis, not code. The actual string rewrite + test-literal updates go through an
implementer/reviewer crew per commander-core's crew-gate default for any code-producing gate.
- Depth/locality: crew boundary adds one round-trip, but keeps the edit and its review
  independently falsifiable exactly where commander-core's "crew gate vs reasoning gate" rule
  says a crew belongs — "a gate whose deliverable is a document or diagnosis... may instead be
  a reasoning gate"; a source-code edit is the opposite case.
- Testability: reviewer independently re-derives the "did every pinned literal move together"
  check (grep for the old text repo-wide) rather than trusting the same actor who wrote the
  edit to also confirm it's complete.
- Simplicity: one extra gate boundary (g2-implement/g2-review/g2-integrate vs. one reasoning
  gate), justified by the shared table's blast radius, not by the string count.

## Convergence: B
The blast radius argument decides it: this is a canonical, five-consumer table the file's own
header calls out as the enforcement source, so the marginal cost of an independent review
(one crew round-trip) is small next to the cost of a silent cross-entry corruption slipping
through self-review on the exact mechanism #442 is about making legible. Measurement gates
(g1, g3) stay reasoning-gate — their deliverable is a diagnosis, and dispatching fresh
Agent-tool subjects as the measurement instrument is not the same thing as a crew "implementing"
a solution.

Recorded as execute.json's authored shape: g1-measure-baseline (reasoning) -> g2-implement /
g2-review / g2-integrate (crew) -> g3-measure-post (reasoning) -> g4-validate (reasoning:
fresh-process + full suite).
