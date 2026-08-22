# Handoff — the Interrogator has no door onto its own survey

Written 2026-08-22, out of the #639 work that retired `workbench` and applied the
human ruling on how the engine is reached. **Everything marked "Opinion" is a
recommendation, not a finding.** The findings are cited and reproducible; every
claim below is measured at `ee959de5` (merge of #642, an ancestor of `main`).

## The ruling this inherits

> "the skill should be using the engine, but through the MCP. same deal, but
> different door."
>
> — human, 2026-08-22, closing the gap #639 surfaced

That ruling retired the previous answer. Five places in the corpus described a
plan or survey the process's door was not bound to as *"driven by this skill's
bundled checklist engine, and by nothing else"* — the CLI, named by periphrasis
so no pattern in `tests/test_cli_retirement_guard.py` could see it, and offered
as the sanctioned path rather than as the gap it is.

Four of those five closed cleanly, because a crew that must drive its own plan
can be **dispatched so that it has its own door**: `run_crew.py`'s `cli` backend
spawns it as its own process with its own `SPINE_FILE`/`SPINE_SESSION` and stamps
`door_bound: true` into `crew-runs.json`. Same engine, same refusal and evidence
contract, different door. That is the ruling working exactly as stated.

**The Interrogator is the fifth, and it does not close that way.** This handoff
is that residue.

## What is actually true

**The Interrogator runs inside its host's process, by design.** It is loaded with
the Skill tool at the Commander's `understand` step (`commander-core.md`, step
table: *"understand | this context — load `constellation-interrogator`"*), not
dispatched. It runs there *because* it has to reach the human, and the host's
context is the human-reachable one.

**So it shares the host's door, and that door is bound to the host's spine.**
Two engine properties, both enforced rather than described
(`skills/_shared/checklist-engine.md`, "MCP door"):

- `_identity_violation` refuses any call resolving to a spine other than the
  bound one.
- A rebind is refused while the door holds an active lease on a different spine
  (`spine_bind` tool description: *"refused while this door still holds an active
  lease on a different spine (release it first)"*).

The Commander holds `spine.json`'s lease across the whole run — it claims at
`init` and releases at `archive`. So during `understand`, the exact window the
Interrogator runs in, the door cannot be moved onto `interrogation.json` and
cannot be pointed at it per-call.

**`from_child` is not a way in.** The engine has a child-checklist concept
(`checklist_engine.py:2730` `advance(..., from_child=...)`, `child_checklist` on a
gate at `:3040`), but it only lets a parent *consume* a child's `consolidation` as
`review-result`. The door says so directly (`mcp_spine_server.py:61`):
*"`spine_advance.from_child` does not redirect the door -- the call still
addresses the bound spine."* It is an ingestion seam, not a driving seam.
Something still has to have driven the child.

**Current state of the doctrine.** `skills/interrogator/SKILL.md` now names this
as a known structural gap and tells the Interrogator to surface it to its host
and stop, rather than route around the door. That is honest, and it is also not a
working instruction: an Interrogator that hits it has nothing to do next.

## This is live breakage, not a theoretical gap

Measured at `ee959de5`, over every `interrogation.json` under `.agent-work/`:

- **20 files. Every one fully driven** — all items recorded, `consolidation`
  present on each.
- **17 carry an engine lease, and every single one is `claimed_by=interrogator`**
  under a session id distinct from its host's: `intr-704`, `interrogator-567-d2`,
  `cmdr-698-interro`, `charter-interrogation-20260728`, and so on.

So the survey is not a wrapper anyone has been ignoring. It is real, exercised,
lease-held work — and it has always been driven **by the CLI**, which is the one
mechanism the ruling retires. Nothing replaces it. The next Interrogator run has
no path at all.

**The useful half of that finding:** the Interrogator already has its own
*session identity* and already claims its own lease on its own file. The identity
model does not need inventing — it is in use, in 17 files on disk. What is
missing is only a **door that will accept that identity against that file**. The
ruling's "different door" is therefore much closer to reality than it looks; the
obstacle is the door's process-level binding, not the engine's ownership model.

## The other thing worth knowing before choosing

**Nothing in the Commander's own gating requires `interrogation.json`.**

- The Commander's `understand` gate has exactly one postcondition:
  `{"kind": "artifact", "evidence_type": "user-decision"}`. It does not mention
  the survey, the record, or the rail.
- The rail that carries the real weight — `scripts/verify_interrogation.py`,
  which refuses a self-answered `decision`, an ungrounded resolved `fact`, and a
  consolidation with no joint-understanding sign-off — runs against
  **`INTERROGATION_RECORD.json`**, a plain record file. It is a command. It does
  not need a checklist to exist.
- The only thing binding the two together is that the rail is invoked *as a
  postcondition inside* `INTERROGATION.template.json:28`.

So the survey checklist is the wrapper, and the record plus its rail is the
cargo. That is the same shape #639 just finished untangling one level up, where
`workbench` was a skill wrapper around a script bundle.

## Candidate directions

Not ranked, not decided. Each names what would have to be true.

**A. Give the Interrogator a door of its own.** Faithful to the ruling as
literally stated, and the measurement above says it is a smaller change than it
first appears: the session identity, the lease, and the ownership semantics
already work and are in use on 17 files. What is missing is a door that will bind
a second spine within one process — today the binding is per-process and per-MCP
server, and a Skill-loaded skill has no process of its own. *Opinion: this is
where I would look first, and I have moved it here from last on the strength of
the identity finding.*

**B. Let one door hold more than one binding.** Directly contradicts
one-spine-per-process, which is load-bearing: it is what stops a subagent from
mutating its dispatcher's spine by accident. *Opinion: do not open this without
a very specific reason; the invariant is worth more than the case.*

**C. Retire the survey; keep the record and the rail.** The Interrogator asks its
questions in the host's context as reasoning, writes `INTERROGATION_RECORD.json`,
and the rail gates it. Nothing needs a door because nothing drives a checklist.
*Opinion: I drafted this as the cheap, probably-correct option before measuring,
on the theory that the survey was a wrapper. The measurement refutes that — 20
driven files, 17 leases — so C now means deleting live, exercised, mechanically
enforced behaviour, and "the rail still covers it" is a claim about the RECORD
that says nothing about the one-question-at-a-time discipline the SURVEY
enforces. Still on the table, but no longer the cheap option, and I no longer
recommend it.*

**D. Dispatch the Interrogator as its own process.** Gets it a real door via the
existing `cli` backend. Breaks the reason it is in-context at all: a headless
process cannot reach the human, and the human exchange is the entire point of the
skill (the rail refuses a consolidation with no sign-off). *Opinion: this is a
non-starter, recorded so nobody re-derives it.*

## Measurement already done, and one still open

The epic behind `HANDOFF-2026-08-21` paid for this rule the expensive way —
*"Measure before designing. Three architecture candidates were built against a
cluster that a single channel experiment then retired."* — so the first question
was answered before this handoff was filed rather than left for you:

1. **Is `interrogation.json` actually driven?** ✅ Answered: yes. 20 files, all
   items recorded, 17 holding an `interrogator`-claimed lease. This retired my
   own draft recommendation (C) rather than yours, which is the point.

Still open, and cheap:

2. **Does anything downstream read the survey rather than the record?** If
   nothing does, the survey's value is entirely in the discipline it enforces
   during the run, not in its output — which sharpens what C would actually
   cost and what A actually has to preserve.

Worth noting for whoever picks this up: the measurement that mattered took one
command and overturned the recommendation written above it. Do that again before
building anything.

## Not in scope

- The other four sites are done. `_shared/checklist-engine.md` and the two
  `write-a-skill` authoring templates now state the dispatch rule, and
  `run_crew.py`'s `door_bound` is the fact they rest on.
- The stale claim that `append` and `skip` have no door tool is already fixed;
  both have had one since #559 (`spine_capture`, `spine_halt`). Do not restore
  it — it was the strongest available argument for the path the ruling retired.
