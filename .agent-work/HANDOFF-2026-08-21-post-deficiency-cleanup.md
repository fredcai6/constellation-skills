# Handoff — the three issues left open after `20260820-deficiency-cleanup`

Written 2026-08-21 by the Admiral that ran the epic. **Everything below marked
"Opinion" is a recommendation, not a finding** — the findings are cited
separately and are reproducible. A Commander should feel free to disagree with
the opinions; the epic this came out of was mostly a story of Admiral opinions
being wrong.

## The criterion these inherit

The human ruled it during the epic and it governs all three:

> There are no bad actors. The only adversary is an honest agent about to make a
> mistake. **Ease of use is the success criterion** — if the tools get harder to
> use, the change failed. **Added machinery is a cost** that must be earned back
> in mistakes prevented.

And the follow-on ruling that closed #615, #357, #457 and #638:

> Guard rails first, even ones that are only strings. Hold off on a stronger
> response until agent behaviour shows one is necessary. Reopen if there is
> actually a problem.

## What the epic learned that bears on all three

1. **Measure before designing.** Three architecture candidates were built against
   a cluster that a single channel experiment then retired. Ranked by cost, the
   experiment was worth more than all three designs.
2. **Check the mechanism before writing the claim.** Six Admiral claims in that
   epic were wrong; every one was caught downstream. The cheapest were falsifiable
   in two commands and were not run.
3. **Adding a refusal is expensive under this criterion.** A refusal built on a
   weak signal misfires, and a misfire is worse than the silence it replaced.

---

# #632 — the in-harness binding is not scoped

## What is actually true

The issue's stated mechanism is **wrong for the channel that is still broken.**

- **Subprocess channel (`run_crew --backend cli`): done.** `_crew_door_env`
  *assigns* rather than `setdefault`s the child's `SPINE_FILE`/`SPINE_SESSION`/
  `SPINE_PARENT`, and its own comment says why. A crew dispatched this way during
  the epic was fully railed and nothing was stripped by hand.
- **In-harness channel (Agent tool): open.** Measured: the dispatching Admiral's
  `SPINE_FILE`, `SPINE_SESSION` and `SPINE_PARENT` were **all unset**. There is no
  env inheritance. Subagents resolve the door through
  `.agent-work/.spine-rail-binding.json`, keyed by the harness session id they
  *share* with the parent.

## The crux

You cannot scope the binding per-agent at the door, because **the door cannot
identify the caller.** MCP calls carry no caller discriminator. The `sid#<agent_id>`
per-agent key from #419 works at `decide_stop` because a Stop payload carries
`agent_id`; a SessionStart payload does not, and neither does an MCP tool call.

Do not spend a Commander on making the door identify its caller. That is a
harness capability question, not a repo one.

## Opinion

Re-scope the issue to the in-harness case and do the smallest thing that turns a
prose guard into a declared one — a checked-in agent definition that excludes
`mcp__spine__*` from subagent tool access, plus a lint asserting the dispatch
templates carry the guard. Every handoff in the epic hand-wrote "do NOT call any
`mcp__spine__*` tool"; three times in one day is a mechanism, and a declared
exclusion costs nothing at use time.

**Do not** attempt caller identification, and **do not** add a refusal at the
door — it cannot tell a legitimate call from a mistaken one, so any refusal it
adds is a coin flip.

**Falsifier before building:** confirm that a subagent-scoped tool exclusion is
actually expressible and enforced in this harness. If it is not, the honest
outcome is a documented convention plus the lint, and the issue closes as
"convention, not mechanism."

---

# #369 — the resume side of the recovery drill has no obligations

## What is actually true

Two halves, and they are in very different states.

**Half 1 — the resume-side obligation — is untouched and real.** Every drill in
the corpus is written from the dispatcher's side. A resuming agent handed
`claim --force` has no instruction to check whether anyone else is live. Epic-298
hit this twice; the second time a commander refused a resume order and produced
eleven timestamped commits it had not authored, gate states three ahead of its
own, and a reviewer's file written 38 seconds before it looked.

**Half 2 — attribution vs continuity — is partly overtaken.** A *stale-lease*
reclaim already writes `previous_session_id` and `takeover_reason` automatically,
without `--force` being used at all. What remains is the deliberate
job-file-not-agent-file guidance: reusing the predecessor's session id keeps
journal continuity and knowingly costs actor attribution.

## Opinion

**Half 1 is the valuable one and it is small.** Every artifact the drill would
check already exists: in-flight `crew-runs.json` entries, the newest filesystem
write under the worktree, recent commits by another author, journal entries
carrying a session id.

Build it as **information, not permission.** When `claim --force` runs, report
what was found — "3 in-flight crew entries, newest write 38s ago, 11 commits by
another author" — and let the agent decide. That serves the criterion: it makes
the mistake visible without adding a refusal that can misfire, and it is the same
shape as the display fix that closed #615.

**Half 2: close it as a documented trade** rather than fixing it. The trade is
deliberate and the epic measured that the automatic path already preserves
attribution. Say so in the issue and stop tracking it.

**Falsifier before building:** check whether any of those four artifact signals is
actually reliable. The epic found `_is_stale` is heartbeat-only at 1800s with no
pid, and pid was unavailable for 55 of 57 stale leases — so at least one obvious
signal is weaker than it looks. Report age and counts, never a verdict.

---

# #634 — a run's plan should be frozen at the bookends and mutable in the middle

## What is actually true

Untouched by the epic — and the epic is **evidence for it**. A nine-lane,
two-round epic ran inside a single `execute` gate, with its real structure living
in `ADMIRAL_LOG.md` and `transitions/`, unguarded by the engine. That is exactly
the complaint.

**But its own proposed remedy is mis-scoped**, and this is the finding worth
rescuing from the epic artifacts. A candidate lane ran an explicit falsification
test — assume #634 lands in full, then re-read the evidence — and found the
observed problems survive untouched. Its reading: #634's evidence is about
**identity**, so "one *actor* per binding" is what it supports, not merging the
second file. Collapsing the pair deletes the two places authority already lives
(`_release_child_plans`, and the `from_child` verdict seam), both of which exist
*because* the pair exists. 81% of plans on disk are second files.

## Opinion

**Do not build this one.** Post the mis-scoping finding to the issue, re-scope its
remainder from "migrate `execute.json` to one spine per agent" to "give the child
plan an identity," and leave it open.

The reason is the epic's own lesson: this is a design question with no measured
defect attached. The last time this repo designed before measuring, a channel
experiment retired most of the work. If a Commander wants to advance #634, the
right first move is an experiment that shows what the missing middle actually
costs — not a design.

---

# Suggested shape for the Commander

Three issues, very different sizes. **Opinion:** treat them as three separate
bounded pieces, not one lane.

| Issue | Shape | Size |
|---|---|---|
| #632 | Re-scope, then declared exclusion + lint | Small |
| #369 | Half 1 as an informational report on force-claim; close half 2 | Small |
| #634 | Comment and re-scope only — no build | Minutes |

Each carries a falsifier above. **Run the falsifier before writing code** — that
is the single thing the epic this came from would tell you, and it earned it
expensively.

## Where the evidence lives

- `.agent-work/20260820-deficiency-cleanup/evidence/CHANNEL-EXPERIMENT.md` — the
  channel measurement, including the M1 finding that corrects #632
- `.agent-work/20260820-deficiency-cleanup/evidence/LIVED-CLUSTER-EVIDENCE.md` —
  read the three Corrections at the end; the body above them contains errors the
  Corrections fix
- `.agent-work/20260820-deficiency-cleanup/architecture/` — five candidates, the
  cold critic comparison, and the C viability report
- `episodes/active/20260820-deficiency-cleanup-*.md` — 13 episodes
- `.agent-work/archive/2026-08-21-20260820-deficiency-cleanup/ADMIRAL_LOG.md`
