# Design note — capturing a door refusal into episodes/ (#541)

Single-author two-candidate comparison (not a panel): this is a fairly-easy call confined to
one already-owned file, not an architecture-touching plan, so per
`references/global-orchestrator.md` "Design-it-twice", a panel is not run here. **Untaken
road, named rather than silent:** a 2-3 agent parallel-dispatch panel authoring independent
candidates was not run; skipped because the design space is small (one seam, one write path,
one constraint to satisfy) and the cost of three independent agents re-deriving the same
`docs/EPISODE_STORE.md` §10 constraint did not look likely to surface a materially different
option than the two below.

## Candidate A — synchronous in-process capture at the refusal site

`_tool_error(..., tool=..., rejection_class=...)` (the same choke-point that already calls
`_log_rejection`) additionally, when a spine is bound, shells out to
`apply_episode_delta.py --store-root episodes` with a `create` delta whose five agent-supplied
fields are literal derivations from the refusal's own data (verbatim message as
`observed-behavior`; tool+args as `task-intent`; "the call did not proceed" as `impact-cost`;
the refusal's own named escape hatch, already present in every refusal string in this module,
as `workaround`; `expected-behavior` states what the call was trying to do, derived from the
tool name and its declared purpose — the one field with no literal source, addressed by
keeping it a fixed, mechanical sentence template per tool family rather than free narrative).

- **Depth**: high — callers (every refusal site) do nothing differently; the capture is a
  property of `_tool_error` itself.
- **Locality**: high — one seam (`_tool_error`), same file already owned this wave, same
  choke-point already proven to catch every door-own rejection (the `IdentityBindingPinTests`
  pin cited in that function's own docstring).
- **Testability**: high — trigger a real refusal in a fresh process, read `episodes/` back.
  Negative control is deleting/reverting the new call and showing the same refusal leaves no
  trace (exactly what the launch order's acceptance evidence demands).
- **Cost**: a subprocess spawn (`apply_episode_delta.py`) on every captured refusal. Bounded
  by the filter (see below) — not every refusal is captured.
- **Engine-native refusals** (through `run_engine`, e.g. a postcondition failing) are NOT
  covered by this seam — `_tool_error` is never called on that path (`as_result` handles it
  directly). Out of scope for this candidate; noted as a real limit, not hidden.

## Candidate B — deferred, batch capture at Commander closeout

Leave the door alone. At each Commander's `feedback` step (already the place episodes get
written, per `commander-core.md`), read `mcp_rejections.jsonl` (the existing sidecar) and fold
any refusals it holds into that run's own retrospective episode as additional agent-supplied
detail or extra assertions.

- **Depth**: low — every future Commander template needs the same read-and-fold instruction;
  the behavior is a property of *every caller remembering*, not of the door.
- **Locality**: low — spreads the capture logic across role doctrine (commander-core.md) and
  N future run retrospectives, rather than living once at the seam that already sees every
  refusal.
- **Testability**: fails the launch order's own acceptance shape directly — "a real refusal,
  triggered through the door in a fresh process, read back out of the episode store
  afterward" cannot be demonstrated from a *single* fresh-process door call, because nothing
  writes to `episodes/` until a much later, separate closeout step run by a different role.
- **The exact failure this mission exists to end**: a refusal that happens in a run with no
  Commander closeout ever reached — the Admiral's own two hits, cited as evidence in the
  launch order, happened *during dispatch*, outside any Commander's `feedback` step. Candidate
  B would still lose those.

## Recommendation

**Candidate A**, with the engine-native-refusal gap named as an explicit filter boundary
(§ below), not silently absorbed into "captures everything." B is kept in this note because
it names why the seam has to be at the door and not at a later retrospective — the mission's
own evidence (the Admiral's dispatch-time refusals) directly falsifies B's premise that a
later closeout will always run.

## Filter (settling `decision:capture-filter-is-yours`)

Counted by re-reading the refusal inventory at context/understand: this module has on the
order of a dozen distinct `_tool_error(..., tool=, rejection_class=)` call sites (unbound,
missing-arg, bad-argument-type, path-escape, cross-checkout, lease-held, etc.), each already
routed through the one choke-point. Capturing **every** one that reaches `_tool_error` with
both `tool` and `rejection_class` set (i.e., every one already opted into `_log_rejection`)
is not a flood: it is the same population already written once per call to the JSONL sidecar,
which has run all wave without incident. The filter is therefore: **capture exactly the
population `_log_rejection` already captures, no more** — this makes the change additive to
an existing, already-scoped mechanism rather than a new, wider one. Engine-native refusals
(through `run_engine`) are explicitly NOT captured by this change; naming that limit is the
honest-null half of this design, not a gap to silently paper over.

**Unbound-door refusal — no work-id.** Skip episode capture when `SPINE` is `None` (no bound
spine, hence no run id `apply_episode_delta.py --store-root episodes` could attribute the
episode to) and say so plainly rather than inventing a sentinel id. The JSONL sidecar still
catches it when `SPINE_REJECTION_LOG` is set; when neither is available (truly unbound, no
override) `_rejectionlog()` already returns `None` and the call is a no-op today, unchanged.
