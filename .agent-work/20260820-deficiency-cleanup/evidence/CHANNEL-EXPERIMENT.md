# Channel experiment — `run_crew --backend cli` vs in-harness Agent tool

**Question (Lane C §9.5, endorsed by the cold critic as the thing to do before
designing anything):** run one wave entirely through `run_crew --backend cli`.
If E1/E2 stop recurring and E3/E5b persist, the authority work is earned. If
E3 and E5b also stop, this cluster was a dispatch convention, not an
architecture defect.

**Design.** The experiment is real epic work, not a toy: commit `efe92791`
(the Cartographer's map regeneration) had not been independently reviewed, and
that is reviewer-shaped work fitting the shipped `specs/reviewer.spine.toml`.
One reviewer crew, dispatched through `run_crew --backend cli` into its own
provisioned worktree.

- Lane worktree: `/tmp/constellation-20260821-mapreview` (detached at `efe92791`)
- Crew id: `constellation/20260821-mapreview/map-review/reviewer/attempt-1`
- Registry: `door_bound: true`, real pid, own worktree, `backend: cli`

---

## Pre-dispatch measurements

### M1 — the dispatcher's `SPINE_*` env is UNSET (corrects E2's stated mechanism)

```
SPINE_FILE=<unset>   SPINE_SESSION=<unset>   SPINE_PARENT=<unset>
```

The Admiral dispatched three Agent-tool subagents earlier in this epic and
hand-wrote a "do not call `mcp__spine__*`" clause into every handoff, attributing
the hazard to env inheritance per #632. **That attribution was wrong for this
channel.** No `SPINE_*` variable was ever set in the dispatching shell.

The in-harness door resolves its binding from a **session-keyed file**,
`.agent-work/.spine-rail-binding.json`, whose top-level keys are harness session
ids. Agent-tool subagents share the parent's harness session id, so they resolve
to the parent's bound spine through the file — not through the environment.

**Consequence for design.** #632 describes env-var inheritance, which is the
`run_crew` subprocess mechanism. The in-harness channel has a *different
mechanism with the same symptom*. A design that fixes env stripping fixes one of
the two. Neither candidate distinguishes them, because the dossier told all
three lanes it was env inheritance. That error is the Admiral's.

### M2 — the lineage edge is empty on BOTH channels

The registry entry for this `run_crew` dispatch records `"parent": null`, and
the child spine's `origin` block carries the three-key `init_work_area` shape:

```json
{"work_id": "20260821-mapreview", "worktree": "/tmp/...", "opened_by": "init_work_area"}
```

No `parent` key. This is a parent that genuinely exists, dispatching through the
channel designed for it, and the edge is still not written. It corroborates Lane
B's finding (`origin.parent` carried by zero of 40 plans) on the one path where
it had the best chance of being populated.

**This weakens the "channel convention" hypothesis for the identity half.** The
missing lineage edge is not an artifact of the Admiral using the Agent tool.

### M3 — an ease-of-use defect found while setting the experiment up

`init_work_area.py --spine` takes a path. Handed `specs/reviewer.spine.toml` —
the spec file that ships in this repository, sitting in the obvious place, whose
name contains the word `spine` — it fails with a raw traceback:

```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

It wants the *compiled* JSON from `generate_spine.py`, not the TOML spec. The
correct sequence is two commands and nothing says so. Under the human's
criterion this is exactly the target class: an honest agent, doing the obvious
thing, gets a stack trace instead of "that is the spec; compile it first with
`generate_spine.py`, then pass the result."

---

## Post-dispatch measurements — the crew completed, exit 0, verdict APPROVE

The reviewer drove all seven reviewer gates (`r0-context` … `r6-fowler`) to
`complete`, wrote its durable result, and returned APPROVE on `efe92791`. The
launcher reported `crew ... -> completed`, registry `status: completed`,
`abandoned: false`.

### E1 — rail loss: **DOES NOT REPRODUCE.** The crew was fully railed.

Seven gates driven on its own spine through its own door in its own process.
This settles Correction 1 empirically: rail loss belongs to the in-harness
Agent-tool channel, not to the system. The Admiral's original E1 was wrong.

### E2 — hand env-stripping: **DOES NOT REPRODUCE** on this channel.

`_crew_door_env` assigned the child's binding; the dispatcher stripped nothing
and wrote no prose guard. The in-harness mechanism (session-keyed binding file,
M1) is a *separate* defect that this channel does not exercise.

### E3 — stranded `active` lease: **DOES NOT REPRODUCE — and the reason inverts the finding.**

`engine_session` is `null` after completion. It is null because the crew
**never claimed a lease at all**. Journal verb census across the whole run:

```
7 record   1 attest   1 consolidate
0 claim    0 release
```

A complete seven-gate plan was driven to consolidation **unleased, start to
finish**, on the shipped, blessed dispatch path. `require_session` permits this
explicitly: `if not lease: return  # no lease claimed: legacy behavior, no
session needed`.

**This is #615 demonstrated as the normal case, not the edge case.** The lease
is not a guard that is too weak. On this path it is a guard that is not in the
road at all. It also explains the 58 stranded leases: they come from actors
that *do* claim — Admirals and in-harness roles — not from dispatched crews.

### E5b — the five-step handshake: **did not arise.** No waive was needed.

### M2 (restated) — the lineage edge stayed empty.

`parent: null` in the registry at completion; no `parent` key in the child's
`origin`. The one measurement that persisted across both channels.

---

## Verdict against the critic's decision rule

The rule was: *if E1/E2 stop and E3/E5b persist, the authority work is earned;
if E3 and E5b also stop, this cluster was a dispatch convention.*

**E1, E2, E3 and E5b all stopped.** By the stated rule, the authority half of
this cluster is substantially a dispatch convention rather than an architecture
defect — the Admiral's channel choice manufactured most of it.

Two honest qualifications, and they matter:

1. **E3 stopped for the wrong reason.** Not a clean release — no claim ever
   happened. The defect did not disappear; it inverted, from "dead lease looks
   alive" to "no lease exists to look at." A design that adds parent authority
   over leases is now designing for a mechanism the main path does not use.
2. **The identity half survived the experiment.** M2 persisted on both channels.
   The missing lineage edge is not an artifact of tooling choice, and it is the
   one thing all three lanes independently diagnosed correctly.

## What this retires and what it leaves

**Retires:** most of the authority ballot. Grants, capability splits, supervise
surfaces and permission edges are answers to a question the shipped path does
not ask, because it never takes a lease.

**Leaves standing:**
- The display lie (58 stranded leases, `RAIL: ... Run it.` on a 22-day-dead
  plan) — untouched by this experiment, and still the strongest finding.
- The empty lineage edge — persists on both channels.
- Two mechanisms behind one issue number (#632: env on one channel, session-keyed
  binding file on the other).
- `require_session` recommending two filed defects.
- `init_work_area --spine` traceback (M3).

Every one of those is a legibility or message defect. None needs a subsystem.
