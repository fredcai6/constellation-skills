# Cold plan critic — lens: intent-fit

**Verdict: the design's second non-optional property (judgment carried up) and, on inspection, the
first (a place to hand back to) do not survive contact with the engine as it exists today. Both
failures were found by running code, not by reading the plan.** Two BLOCKING findings below.

## BLOCKING — Property 1's `directives.handback` block has no verb that ever writes to it; it renders
forever empty

**What is wrong.** The plan's Property 1 (CANDIDATE_PLAN.md:99-124) claims the compiler gives every
gate "a place to record beliefs, concerns and open questions" by injecting
`directives.handback.{beliefs,concerns,open_questions}` as empty arrays, plus `how_to_record` naming
"the real engine verbs." I searched the engine, the CLI, and the MCP layer for any verb that appends
to those arrays on the gate a crew is actively working, and there is none.

**The evidence.**

1. Grep across the whole engine and MCP surface for the plan's own vocabulary turns up nothing but the
   plan document itself:
   ```
   grep -rn "handback\|beliefs\|open_questions" scripts/ docs/ skills/
   ```
   returns zero hits in `checklist_engine.py`, `mcp_spine_server.py`, or `docs/CHECKLIST_SCHEMA.md` —
   the words are invented by this plan, not grounded in an existing engine capability.

2. `docs/CHECKLIST_SCHEMA.md:124` documents `directives` itself as "forced primitive specifics handed
   down — a standing contract the gate **must satisfy**" — i.e. top-down (author/compiler → gate), not
   a crew-writable inbox. That is the field's actual, load-bearing meaning in the 970/22-task corpus
   measurement the plan itself cites for why it chose `directives` over `constraints`.

3. The only verb that can touch `directives` post-generation is `amend`'s `rescope` op
   (`scripts/checklist_engine.py:2593` on), and it is explicitly restricted: `"only a pending gate can
   be rescoped (is {status!r})"` (checklist_engine.py, rescope branch). A gate a crew is actively
   working is `in-progress`, not `pending` — so the one verb that can edit `directives` categorically
   cannot touch the active gate's own handback block. It also requires `--authority`/`--reason`
   ("human ratification" per its own docstring) — heavyweight re-planning machinery, not a place to
   jot a concern mid-gate.

4. I ran `render_human` on a synthetic active gate carrying exactly the shape the plan specifies:
   ```python
   directives = {"handback": {"beliefs": [], "concerns": [], "open_questions": [],
                               "how_to_record": "spine_evidence attach / spine_halt block",
                               "hand_back_to": "commander-w3a-465 at gate execute"}}
   ```
   Output (pasted verbatim):
   ```
   directives:
     handback:
       beliefs: 
       concerns: 
       open_questions: 
       how_to_record: spine_evidence attach / spine_halt block
       hand_back_to: commander-w3a-465 at gate execute
   ```
   `beliefs:`, `concerns:`, `open_questions:` render with a trailing space and nothing after the colon
   — on every gate, forever — because nothing in the engine ever appends to them. This is not a
   hypothetical: it is the literal, permanent rendering of the property the plan calls out as its
   first non-optional deliverable.

5. The engine already has a real "hand back to parent" verb — `block`
   (`scripts/checklist_engine.py:2385`), which sets `status = "blocked"` and appends to
   `cl["blockers"]`, bubbling to whoever picks the gate back up, with `authority` and `next_action`
   fields that are actually consumed. It is unrelated to `directives.handback` and the plan never
   names it as the mechanism.

**What it costs.** This is the mission frame's first non-optional property, and the launch order's
explicit rule ("a crew with something to hand back has a gate to hand it back at"). As designed, a
crew that wants to record a belief, a concern or an open question has three real options — `attach`
(writes to `evidence`), `flag-candidate` (writes to the top-level `triage_candidates` list, unscoped
to a gate), or `block` (halts the gate entirely, bubbling to `blockers`) — and **none of them write
into the JSON structure the plan spends a whole property designing and the render specifically
surfaces to the agent.** A reviewer or the next crew reading `current` sees a `handback:` block with
three permanently blank fields next to two that are populated once at generation time. That is
"looks like it works" — the exact failure class the launch order names — one level inside the very
mechanism built to avoid it.

**Smallest fix.** Either (a) drop the invented `beliefs/concerns/open_questions` array shape and have
`how_to_record` name the verbs that actually persist somewhere queryable — `flag-candidate` for an
open question that should route to triage, `block` for a concern that should halt the gate, `attach`
for a belief worth recording as evidence — with the compiler wiring `hand_back_to` into the actual
`--authority`/`--blocker` arguments those verbs take; or (b) if the JSON shape is kept because a future
gate's `claims_rollup`-style reader wants to read it back structurally, add the one missing engine verb
(an `amend`-adjacent op, or a new `note` verb) that appends to `directives.<name>.<field>` on the
*active* gate specifically, and prove in g1 that it round-trips through `render_human` with non-empty
content — not just that the empty scaffold renders.

## BLOCKING — the `magnitude = "large"` escalation postcondition is closable by the same session that
made the claim, with the engine enforcing no provenance at all

**What is wrong.** The plan's Property 2 (CANDIDATE_PLAN.md:126-149) claims auto-injecting an
`artifact`/`user-decision` postcondition "mechanically changes what the gate requires to close" so
"the gate cannot close on the crew's own say-so." The launch order's lens question is exact: *"does
the auto-injected escalation postcondition actually cause greater review, or does it only cause one
more artifact to be attached by the same agent that made the claim?"* I ran it. It is the latter.

**The evidence.** A minimal checklist with one `in-progress` gate carrying a postcondition shaped
exactly as the plan describes (`check.kind == "artifact"`, `evidence_type == "user-decision"`,
`match == {}`), closed in two calls with no session, authority, or identity distinction whatsoever:

```python
>>> ce.attach(cl, 'g1', 'user-decision', {'decision': 'looks fine to me'})
'attached e-g1-1 (user-decision) to g1'
>>> ce.attest(cl, 'g1', 'c1', 'postconditions', 'self-attested', evidence_id='e-g1-1')
'attested g1.c1 via e-g1-1'
>>> cl['tasks']['g1']['postconditions'][0]['satisfied']
True
>>> cl['tasks']['g1']['evidence'][0]['produced_by']
'engine'
```

Three separate gaps compound here:

1. `attach()` (`scripts/checklist_engine.py:2933`) takes no `authority` or session argument at all —
   contrast `waive()`, three functions below it, which *requires* `--authority` and refuses an empty
   one. Nothing distinguishes "the crew attached this" from "a human attached this." The
   `produced_by` field is hardcoded to the literal string `"engine"` regardless of caller
   (`attach`'s body: `"produced_by": "engine"`), so the record doesn't even retroactively show who
   really did it.
2. `evidence_type: "user-decision"` is in `ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH`
   (`scripts/validate_spine.py:453`), meaning the escalation postcondition the plan auto-injects can
   validly ship with `match: {}` — so there are no payload fields constraining *what* the self-attached
   decision says either. The check accepts any one-line string from the same agent.
3. `docs/CHECKLIST_SCHEMA.md:166` states only a **convention**: "A human checkpoint is
   `artifact`/`user-decision`." Convention is not mechanism. Nothing in `attest`/`attach`/`dispatch`
   enforces it — I closed the checkpoint programmatically above with zero human or higher-tier
   involvement, in-process, no CLI trickery needed.

**What it costs.** This is the human's verbatim rule the launch order quotes: *"greater claim requires
greater review."* The design's own text (CANDIDATE_PLAN.md:138) says the mechanism's whole point is
"the gate cannot close on the crew's own say-so" — but mechanically, it can, in the same two calls a
crew already makes for any other artifact-typed postcondition, and the engine cannot tell the
difference between the two cases from the record it keeps. This is also a direct answer to a separate
lens question — "is anything a check that cannot fail" — yes: as auto-injected, the escalation
postcondition cannot fail against the very agent it exists to check, because nothing gates who may
attach the artifact that satisfies it.

**Smallest fix.** Bind the escalation artifact's provenance the same way `waive` already binds
authority: either (a) require `attach --type user-decision` to carry a `--session-id` that the engine
checks is *not* the session holding the gate's claim/lease (the lease machinery already exists —
`_active_lease`, `require_session`, `checklist_engine.py:906` on — so this is wiring an existing
capability, not new machinery), or (b) route `magnitude = "large"` through `block`
(`checklist_engine.py:2385`) instead of a same-session `attach`+`attest` pair: `block` already forces a
status change and a `blockers` bubble that requires a *different* verb (`resume`, itself requiring
`--reason`) to clear, which is closer to "a tier above must act" than an artifact the same session can
manufacture unwitnessed.

## Smaller note (not separately ranked)

CANDIDATE_PLAN.md:117-121 justifies making `how_to_record` non-empty by citing
`checklist_engine.py:2189` rendering "a directives block only when it is non-empty." Checked against
the code at that line (`_render_directive_lines`) plus `render_human`'s
`if active.get("directives"):` gate: what must be non-empty is the *whole `directives` dict* (i.e. the
`handback` key existing at all), not `how_to_record` specifically — a `handback` block with an empty
`how_to_record` string would still render. This doesn't change any behavior on its own, but it's a
sign the plan's stated reasoning about the renderer was not checked against the renderer, in the same
document that goes on to build an unwritable-field design (finding 1 above) on adjacent reasoning.

## Scope discipline

I did not read `crew-handoffs/plan-alt-*-result.md` or the launch order. Everything above is from
`CANDIDATE_PLAN.md`, `MISSION_FRAME.md`, and running `scripts/checklist_engine.py`,
`scripts/validate_spine.py`, `scripts/mcp_spine_server.py`, and `docs/CHECKLIST_SCHEMA.md` as shipped
at the base commit. No file was written except this one; no code, template, or spine was changed; no
`git` write operation was run.
