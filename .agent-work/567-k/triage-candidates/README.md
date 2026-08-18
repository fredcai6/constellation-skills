# Triage — lane K, issue #634

**Nothing was filed.** `decision:no-issue-filing-mid-run` is `settled/human`, with the human's
reason recorded in the launch order: *"we've been ballooning out tracking."* Every candidate below
is therefore `recommend-and-defer` — the recorded form of "ask", not an improvised filing
decision. Issue-creation authority sits with the human, and `docs/agents/ORCHESTRATOR_CONTEXT.md`
independently requires explicit human approval for anything beyond a local commit.

I checked each candidate against the fix-now ladder honestly. **None clears all four rungs**, and
each fails on a *different* rung, which is why none was quietly pulled into scope.

| # | Candidate | Classification | Fails the ladder on | Priority |
|---|---|---|---|---|
| 1 | [`current` does not render the bookend freeze](current-does-not-render-the-bookend-freeze.md) | missing capability anchor; ungrounded claim | **verifiable now** — the property test that should cover it is structurally blind to the field, so "it works" cannot be shown in this context | high |
| 2 | [human confirmation sits in the mutable middle](human-confirmation-sits-in-the-mutable-middle.md) | structure/constraint mismatch | **no architecture/production-default impact** — it changes what a run must prove before it may close | high |
| 3 | [the gauge writer overwrote its parent's reading](gauge-writer-overwrites-parent-reading.md) | bug | **adjacent to current scope** — gauge/hook code, a cold-start area this run never opened | medium |
| 4 | [the crew registry loses concurrent dispatches](crew-registry-loses-concurrent-dispatches.md) | bug | **adjacent to current scope** — `scripts/run_crew.py` is fenced to lane J this wave | high |

## Why each is deferred rather than fixed, in one line

1. Rendering the flag would bake in a declaration name the human has **not yet chosen** — the
   design comparison is returned deliberately unconverged. Doing it now risks doing it twice.
2. Baking a human-acceptance postcondition onto a frozen closing bookend changes the rigor dial.
   That is the human's, and it is wider than #634 asked for.
3. Observed with a diff, not diagnosed. I did not read the gauge writer's source, so I have an
   effect and no cause — filing a fix from that would be guessing.
4. `scripts/run_crew.py` is **lane J's file** this wave. Route it to lane J's owner rather than to
   a backlog — that lane already has the file open. Measured, not inferred: three crews ran and
   wrote results and stdout, and only one registry entry survived.

## Also carried, and NOT a triage candidate

The two genuine **scope floats** are in the return, not here, because they need an Admiral ruling
on ownership rather than a future issue:

- **The crew half of `decision:every-planning-role`**, blocked on `scripts/generate_spine.py`
  (unowned by either lane) whose gate compiler emits a fixed field list.
- **The `execute.json` → spine migration**, which reaches `run_crew.py` and `recover_crews.py`
  (lane J's) and role prose in neither lane's grant.

## Not claimed

These are the candidates I noticed. I did not run a sweep for others, and two of the three came
from crews and critics rather than from me — the reviewer found #2, and #1 surfaced only because
reconcile made me read the schema doc's own account of its blind spot.
