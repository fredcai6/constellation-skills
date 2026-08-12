# Design-it-twice Brief: where the lifecycle seam goes

## The one thing being designed twice

**Where the open/close lifecycle operation lives, and what the door tool is a client of.**

Not "how do we archive a work area" and not "what gates do we need" — one load-bearing decision:
**is the lifecycle a set of functions the door happens to call, or a module with its own interface that
the door is one adapter over?** Every other choice in this run (the gate cut, the test surface, where a
rollback lives, whether a CLI ships beside the door) falls out of that answer, which is why it is the
thing being designed twice rather than the gate list.

## Count and panel — a surfaced choice

**N = 2**, not 3, and the reason is a constraint rather than a judgment that this is easy — it is not
easy, and by the "when in doubt, panel" rule it would normally get three.

The frozen launch order forbids two crews in one worktree. That makes each candidate **serial**
wall-clock, not parallel, so the panel's cost is additive rather than concurrent. Measured while
deciding this: the corpus's own mechanical guard (`active_duplicate`, `scripts/run_crew.py:253`) is keyed
on work-id/gate/**role**/worktree, so it would have *permitted* two differently-roled crews here — the
prose rule is stricter than the machinery that is supposed to carry it. I follow the launch order, which
is my principal, and record the prose-versus-mechanism gap as a finding.

The third candidate I would have run is named as an untaken road below, with the reason it is refuted
before it is written rather than "we ran out of budget".

**The Admiral may overturn this scaling call.** It is surfaced here for exactly that.

## The constraints (one per agent, each distinct and named)

- **Candidate A — `smallest-diff`.** The least new structure that satisfies every required property.
  No new module unless a property cannot otherwise be met. Reuse `init_work_area.py` and
  `generate_spine.py` as libraries; new code is glue. Prove the properties, add nothing else.
- **Candidate B — `best-seam-placement`.** One deep lifecycle module owns open and close as its
  interface; the MCP door and a shell CLI are two adapters over the same seam. Draw the boundary where
  the caller and the tests actually want it, and pay whatever new structure that costs.

Both candidates hold the same things fixed: the engine's on-disk format, the close ordering, no PR and
no worktree removal, stage-by-name, `.mcp.json` / `settings.json` / `docs/agents/*` / `skills/**`
untouched, and the four properties open must have (refuse-rather-than-half-succeed with rollback,
record where it opened, never reuse an occupied worktree, reachable through the door).

## Compared on

- **Depth** — how much behaviour sits behind how much interface the caller must learn.
- **Locality** — does a change to the close ordering touch one place or several.
- **Seam placement** — is the boundary where the tests want it, given that the door cannot be driven
  in-process without a bound spine and the pass-through pin.
- **Testability** — can rollback, occupied-worktree refusal, and the close ordering each be exercised
  and *falsified* on their own, with a violating fixture rather than only a happy path.

## Framing block — the parallel-reasoning prime

**Constraints in play.** `smallest-diff` and `best-seam-placement`, chosen because the honest tension in
this run is between "the corpus already has `init_work_area.py`, `generate_spine.py` and
`verify_worktree_isolation.py`, so open is glue" and "open has four properties none of those files owns,
and glue with four properties is a module wearing a disguise."

**Dependencies, held fixed for both.** The choke-point pin
(`tests/test_mcp_identity.py::IdentityBindingPinTests::test_call_tool_can_only_produce_content_two_ways`)
restricts every `return` in `call_tool` to `as_result(run_engine(...))` or `_tool_error(...)`;
`_identity_violation` refuses any argv resolving `--file` off the bound spine; the engine round-trips
unknown top-level spine keys (measured); the crew registry records `parent` and `model` (measured).

**Illustrative sketch — NOT a proposal, carries zero weight at convergence.** One plausible shape: a
`scripts/spine_lifecycle.py` with `open_work(...)` and `close_work(...)`, a `spine_open`/`spine_close`
pair dispatched from a sibling of `call_tool`, and a top-level `origin` block in the emitted spine. It
is written down only so the reader reasons in parallel; a candidate that argues against it is doing its
job.

## Output — a recommendation, never a menu

Each candidate returns a full gate plan (gate list, close criteria, required evidence, violating
fixtures) under its constraint, plus its own honest read of where its constraint hurts. The Commander
converges to one opinionated pick or a named hybrid, scored axis by axis. A menu handed back is a failed
run.

## Untaken-road record — loud skips

- **Candidate C — `close-is-a-generated-gate-not-a-tool`.** Skipped, and refuted rather than deferred: a
  gate postcondition runs *during* `advance`, and the launch order fixes the ordering as advance →
  release → move. A postcondition that archives would move the work area **before** the release, which
  is the exact failure the fixed ordering exists to prevent. Writing a candidate whose defining
  constraint contradicts a no-go would produce a candidate that cannot win.
- **A third `most-testable` candidate.** Skipped: testability is already a scoring axis on both
  candidates, so a third agent would re-run a comparison rather than surface a new structure.

## Panel-vs-single record

**Two, not three or one.** Not one, because this is an architecture-touching interface decision and the
bias is to panel. Not three, because the one-crew-per-worktree constraint makes candidates serial, and
the third constraint worth naming is refuted a priori (above). Surfaced to the Admiral at plan approval,
and overturnable there.
