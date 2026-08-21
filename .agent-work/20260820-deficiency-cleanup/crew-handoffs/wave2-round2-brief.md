# Round 2 shared brief — design against measured ground

Round 1 produced three authority designs. An experiment then retired most of
what they were designing for. Read that history before you design anything; you
are not starting where round 1 started.

## What the experiment settled

One reviewer crew was dispatched through `run_crew --backend cli` — the shipped,
blessed dispatch path — and completed a seven-gate plan.

**E1, E2, E3 and E5b all failed to reproduce.** The authority half of this
cluster is substantially an artifact of the Admiral dispatching through the
in-harness Agent-tool channel instead. Grants, capability splits, supervise
surfaces and permission edges are answers to a question the main path does not
ask.

**The single most important measurement.** That crew drove all seven gates to
consolidation without ever claiming a lease:

```
journal verb census, whole run:  7 record  1 attest  1 consolidate
                                 0 claim   0 release
```

`require_session` permits it explicitly: `if not lease: return  # no lease
claimed: legacy behavior, no session needed`. **On the main path the lease never
fires.** The 58 stranded `active` leases in this checkout come from actors that
do claim — Admirals and in-harness roles — never from dispatched crews.

**What survived the experiment.** Exactly one structural thing: the lineage edge
is empty on *both* channels. The `run_crew` registry recorded `parent: null` at
completion and the child's `origin` carried no `parent` key — a real parent,
dispatching through the channel built for it.

## The success criterion — unchanged and binding

> There are no bad actors. The only adversary is an honest agent about to make a
> mistake. **Ease of use for agents is the success criterion.** Added machinery
> is a cost that must be earned back in mistakes prevented.

Round 1 failed against this criterion. All three lanes built forgery-resistant
identity when the problem needed *legible* identity. Do not repeat that.

**You may not add a subsystem.** No new module, no new permission concept, no
new store. If you believe one is unavoidable, you must first show why the
existing carriers cannot serve: the session string already encodes
work-id/gate/role/attempt, and `crew-runs.json` already records role, parent,
worktree and pid.

## The three questions

1. **What should a plan display to a reader who does not own it?** Round 1 and
   the critic all designed the *write* surface. Nobody designed the read
   surface, which is where honest mistakes are made. Today a 22-day-dead plan
   renders `LEASE active` plus `RAIL: ... you are 7 steps from done. Next: the
   ACTIVE line above. Run it.` The system instructs an agent into the mistake.
2. **Should the lease be demoted to a presence marker?** It never fires on the
   main path. Nobody has been able to name one mistake its refusal prevented.
   If it is not a guard, what is it, and what should it cost?
3. **Is the lineage edge worth writing at all?** It is the one survivor — but
   `crew-runs.json` already records parent, role, worktree and pid. Say whether
   writing `origin.parent` earns its keep, or whether the existing carrier plus
   a better display is the whole answer.

## Constraints on the liveness signal

Any display change rests on a liveness signal, and the current one is weak.
`_is_stale` is heartbeat-only, 1800s, no pid. `run_crew.entry_liveness` answers
the same question three-state and pid-corroborated at 28800s — **16x apart, and
the engine holds the blind one.** The cold critic's warning stands: today's lie
is biased toward inaction; a naive fix biases toward *seizure*, and a Commander
thinking hard for 31 minutes would render STALE. Render age, not a verdict.

## Required reading

- `evidence/CHANNEL-EXPERIMENT.md` — the experiment, in full.
- `evidence/LIVED-CLUSTER-EVIDENCE.md` — **including all three Corrections and
  the threat-model section.** The Admiral wrote three errors into that dossier
  (E1 overstated, E3 false, E2's mechanism wrong). The corrections are
  load-bearing.
- `architecture/CRITIC_COMPARISON.md` — especially Entry 5 (minimal
  intervention), which won round 1, and the critic's self-critique of it.
- The three round-1 candidates, for what not to redo.
- `scripts/checklist_engine.py` rendering paths, `require_session`, `_is_stale`.

## Deliver

Boundaries, what changes, what it costs in machinery and learning burden, what
it leaves open, migration, per-issue dispositions for #634/#638/#632/#357/#369/
#615, risks, and how someone would know it worked. Answer all three questions
explicitly, even where your lane's bias makes one uncomfortable.

State plainly what you would ship **first**, and what you would drop if you
could only ship one thing.

## Hard constraints

Artifact only — no source, test, `map/`, or GitHub change; no commit; no push.
`gh issue view` reads are fine. Do not call any `mcp__spine__*` tool. Do not read
the other round-2 lane's file.
