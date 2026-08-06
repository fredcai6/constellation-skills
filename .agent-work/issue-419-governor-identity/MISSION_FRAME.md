# Mission Frame — issue #419, governor per-agent identity

Cut from the **declared reading**, not from a map. This run oriented `DEGRADED-NO-MAP`: the repo has
no `docs/architecture/` at all, so there is no anchor inventory to cite. The two documents the
orientation receipt hash-pinned as substitutes are the structural record this frame is built from:

- `docs/GAUGE_WRITER_HOOK.md` — the governor write side's own design record: the wiring, the exact
  transcript fields the parser depends on, the enumerated skip-on-uncertainty causes, and the
  session-to-spine binding coupling. This is the closest thing the repo has to a structural packet
  for the area this run changes, and it is **wrong in a load-bearing place today** (see below).
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — the project's rigor deltas. It classes workflow mechanisms
  and verifiers as a *strengthened durable system* requiring targeted automated verification plus the
  relevant broader suite, and it reserves pushes/PRs/merges to explicit human pre-approval (which the
  launch order supplies for this run).

No anchor ids appear anywhere in this frame, deliberately: in a degraded run there is no map for an
anchor to be a member of, so citing one would be a claim with nothing behind it.

## Intent

Make the context governor attribute a reading to the **agent that produced it**, so that the engine's
live trip mechanic acts on a subagent's own context fill instead of going silent. Bounded outcome:
a real trip fires from a per-agent reading on a live run.

## Affected behaviour (named in the declared reading, not by anchor id)

- **Session-to-spine binding.** `docs/GAUGE_WRITER_HOOK.md` documents it as a nested multi-entry map
  keyed by `session_id`, maintained by `scripts/hooks/spine_rail.py` on engine `claim`/`release`.
  This run changes the **outer key** to per-agent identity. That is the load-bearing interface shape
  of this whole run.
- **Gauge write.** The writer resolves a gauge path from that binding and, per the same document,
  writes for a session bound to *exactly one* spine — zero or 2+ both skip. Per-agent keying is what
  makes "exactly one" true again for a dispatched agent.
- **Fill sensing.** The document's field table requires `isSidechain` to be **falsy**. Every line in a
  subagent's own transcript is `isSidechain: true`, so that filter must invert for a subagent, and the
  table gains the payload's `agent_id`. The doc fix belongs to this run, not to a follow-up.
- **Trip.** Engine-side and unchanged by this run: it reads `gauge.json` beside the spine and applies
  model-keyed bands. It is deliberately identity-blind — which is why fixing the *writer* is sufficient
  to make it fire.

## Governing constraints and assumptions

- **Skip-on-uncertainty, never fabricate** — the writer's founding rule in the declared reading. This
  run must not weaken it; per-agent identity narrows uncertainty rather than tolerating more of it.
- **Fail-closed on identity** — an unresolved identity binds nothing and writes nothing. Explicitly:
  never fall back to the parent's transcript, which is the misattribution the fan-out reversal already
  ruled against.
- **The gauge record's four required fields** are shared with the read side. Adding an optional
  diagnostic field is tolerated by the reader (it checks presence of the required four, not absence of
  extras); removing or renaming one is not on the table.
- **`CLAUDE_PROJECT_DIR` is fixed at session launch** (the declared reading says so in its own words,
  as the reason it refuses to emit the variable form). Consequence for this run: the change **cannot**
  be validated from inside the worktree that contains it.
- **Rigor delta from `docs/agents/ORCHESTRATOR_CONTEXT.md`:** targeted automated tests *plus* the
  relevant broader suite; a no-test-surface claim needs a stated rationale.
- **A check that cannot fail is worse than no check** — inherited. Applied here: any test that
  hand-injects the `agent_id` it is trying to prove the harness delivers is forbidden.

## Decision pressure this run forces

These are choices, not settled anchors — they are surfaced as candidates, and the ones that resolve
into recorded decisions are graded in `execute.json`, where the grade lint can see them.

- Whether the branch point's outcome — the payload carries the parent's transcript path **and** a
  per-agent `agent_id` — is inside the frozen taxonomy or an escalation. Resolved at `understand` as
  in-taxonomy with an unanticipated fact; floated to the Admiral, not absorbed.
- Whether identity resolution's measured duration rides on the gauge record or a sidecar.
- How large a real context fill the acceptance run must reach for the trip to fire, and whether a soft
  trip discharges the done-condition or only a hard one does.

## Evidence surfaces

- Live headless `claude -p` with settings wiring **this worktree's** hook by absolute path — the only
  vehicle that can see the real change. Already proven to work end to end at `understand`.
- The captured real payloads at `.agent-work/issue-419-governor-identity/evidence/probe-payloads.jsonl`.
- The repo's own test suite for the two hooks, plus the broader suite per the project rigor delta.
- The live binding store's recorded before-state, which the sweep must produce before it mutates.

## Map confidence

There is no map, and that is a recorded, escalated fact rather than a silent one. The declared reading
is a **design document, not a generated map**, so it can be stale relative to code — and this run has
already found one place where it *is* wrong (the sidechain filter). Every structural claim above was
re-confirmed by reading the code it describes; nothing here rests on the document alone. The plan
therefore treats correcting that document as in-scope work, not as reconcile-time bookkeeping.

## Out of scope

Metrics methodology. Any consumer of the reading beyond the live trip mechanic. The residual case
where a genuine orchestrator holds several spines at once and stays ambiguous — that is the known
cost recorded in the declared reading, and this run does not close it.
