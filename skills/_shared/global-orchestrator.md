# Global doctrine — orchestrator

Inherited approach-doctrine for the high tier (Commander, Cartographer, Scout, Admiral, Triage), bundled
with the skill at install. Start from this baseline plus `global-everyone.md`; the project states only its
**departures**. The project overlay is the delta — read `docs/agents/ORCHESTRATOR_CONTEXT.md` and
`docs/agents/GLOSSARY.md` if they exist.

Agent-facing. Dense by design.

## Default posture (rigorous unless the project relaxes by subsystem)

- Correctness over velocity for promoted behavior.
- **Map-first**: frame every ask against the affected capabilities, structural anchors, and governing
  constraints/decisions before shaping work.
- Clear canonical input/data boundaries; name canonical sources and don't bypass them.
- Behavior changes are test-led where a test surface exists; no test surface means review/inspection
  evidence, not a TDD exception.
- Machine-checkable evidence when practical; more proof for high-risk or public-facing outputs.
- Compromises tracked with owner, reason, and exit condition when they affect future work.

Relaxation must name what gets faster, what risk increases, and where it applies; strengthening must name the
extra proof or enforcement. The project overlay carries those deltas.

## Shaping and ordering

- Decompose into small, independently-verifiable units; sequence so each gate proves something
  (tracer-bullet vertical slices over horizontal layers).
- For open research/exploration: a tested **scoreboard** gate first, then parallel throwaway worktree spikes
  (one mechanism each) measured on it, then a synthesis gate that productionizes only the winner — surfaces
  structure no single spike sees. Keep losers as documented negative results.
- The project's data-flow philosophy and "what order we tackle problems here" are deltas — get them from the
  local overlay.

## Critical spec review (standard, not optional)

- Any design/spec artifact that will govern cut work — a shaped-design spec, a gate plan for an epic-scale
  change, a doctrine compilation — gets a **cold adversarial critique before confirmation**: the critic reads
  the artifact only (no exploration record, no author context), nothing is sacred, deliberate decisions are
  attackable; the human filters relitigation noise.
- **Panel scaled by weight**: default one critic; an artifact that spawns epics or touches architecture gets a
  3-lens panel (intent-fit — does the design serve the stated point; testability — can each pathway be
  exercised and falsified; simplicity/YAGNI — what can be deleted). When in doubt, panel.
- Findings are **triaged by the human, every one** — edit the artifact / reopen exploration / reject with
  reason — before the artifact is treated as confirmed. Acceptance is human-only; a critic never self-triages.
- **Competitive-critic** (human opt-in): for a panel, the human may tell the critics they are judged against
  each other on serious confirmed findings. Competition modulates critic **effort**, never **disposition** —
  the critics still never **self-triage**, and the human disposes every finding (this is the erosion guard).
  It sits in explicit tension with never-bias-the-reviewer — a critic told to compete is no longer a neutral
  cold reader — so it is opt-in per run, never the default.
- Where the explorer skill is installed, its `CRITIC_HANDOFF` template is the reusable cold-read contract.

## Design-it-twice (standard, not optional)

- **Trigger**: any skill authoring a plan or introducing a load-bearing interface generates alternatives
  before converging — N≥2 candidates in parallel, each under one named distinct constraint, compared on
  depth / locality / seam placement / testability, converging to one opinionated recommendation or named
  hybrid (never a menu).
- **Bias-to-yes**: run it by default. Skip only a genuinely-trivial case, and a skip is never silent — it is
  surfaced as a named **untaken road** (its reason stated), visible at the approval checkpoint next to the
  plan or design it belongs to.
- **Count/panel scaled by weight, a surfaced choice**: a fairly-easy call may run two candidates or a single
  with the alternatives named as untaken roads; a load-bearing interface or architecture-touching plan runs a
  panel. When in doubt, panel. The count and its rationale are surfaced to the human, not chosen silently.
- **Convergence is human-only**: the agents generate and compare, the human picks the winner or the hybrid.
  While they run, the orchestrator presents the human a framing block — constraints, dependencies, and an
  illustrative sketch explicitly marked "not a proposal" — so the human reasons in parallel instead of waiting.
- The reusable contract is `design-it-twice-brief.md`, the fill-in brief that carries the mechanism (constraint
  menus, comparison axes, framing block, untaken-road and panel-vs-single records); this section is the norm
  only. Where the explorer skill is installed, its excursion `design-it-twice` type is the same contract in its
  design-phase form.

## Handoff completeness

Every crew handoff carries: assigned task, allowed scope, specific exclusions, success criteria, required
evidence, required verification commands (POSIX-form, absolute paths), test mode or no-test-surface
rationale, stop conditions, return format. Do NOT re-derive proven mitigations into each handoff — they are
inherited (`global-crew.md`, `global-everyone.md`); the handoff carries only the task-specific specifics.

**Return thin, write fat.** Put the detail in the durable artifact and keep the returned message a pointer to
it: the artifact survives the run and is what the next actor reads, while a fat return is paid for in every
reader's context and is lost when the agent ends. A return states the verdict, the evidence that decides it,
and the artifact path — not the full transcript the artifact already holds.

## Gating, evidence, stop/ask

- Pause for a `user-decision` at the project's enabled checkpoints (the rigor dial). Human verification is a
  first-class step.
- Delegated/autonomous (running from an Admiral `LAUNCH_ORDER`, no reachable human): the frozen launch order
  IS the ratified intent — satisfy `user-decision` checkpoints by citing it; take a genuine gap (a decision
  outside latitude, or missing context) to the Admiral.
- Stop and ask when project context, user instruction, and observed artifacts conflict in a way that affects
  the task. Do not resolve a conflict by picking an authority source by policy.

## A check that cannot fail

**A check whose output is identical in the healthy and the defective world cannot discriminate, however
correctly it runs.** The crew tier carries this family in full — `docs/agents/CREW_CONTEXT.md`,
"a check that cannot fail is indistinguishable from one that passed". **It belongs here too, because the
expensive instances are authored at this tier**, in the guards an orchestrator writes for itself: sweep
checks, liveness probes, install-delta comparisons, gate postconditions.

**Mechanical detector: any guard that loops must assert what it looped over.** State the count. An
under-inclusive enumeration presented as complete reports clean without ever reaching the interesting
items — and it reports clean *because* it never reached them.

Three routes in, all observed: **vacuity** (the guard passes on an empty set); **wrong question** (a
*can-this-fail?* sweep is structurally blind to *does-it-cover-what-it-claims?*, because the answer is
"yes" in both worlds); and **wrong iteration set** (a comparison that enumerates only one side never sees
what exists only on the other).

Two corollaries worth carrying:

- **Assert against the behaviour, never against text describing the behaviour.**
- **A check that runs against your own working copy is not a check on the world.** A reachability test
  against local refs passes while a fresh clone is already broken; a success code proves delivery, not
  content. Test the thing a stranger would get.

## Unchanged-tree shortcut

A redundant manual re-verification may be skipped ONLY when the working tree is provably identical to the
last green run: `git rev-parse HEAD` matches the hash recorded with that green run, AND `git status
--porcelain` is empty, AND the prior green output is pasted alongside the matched hash. Any tree change — a
different HEAD or a dirty tree — voids the shortcut and forces a fresh run. This is doctrine and evidence
shape only; no engine or script change. Tier-specific application (the engine-postcondition boundary at a
Commander gate, wave-batched re-verify at an Admiral close) rides beside each caller.

## Idle subagent adjudication

An idle subagent (`idle_notification`, `idleReason: available`) that has produced COMPLETE artifacts is
*done*, not stalled. Judge it from the **artifact set** — result content, files changed, diff — never from
the idle signal alone: complete artifacts → integrate as if the verdict had arrived; silence plus
incomplete or missing artifacts → *stalled*, rework or relaunch. This judges the **verdict**, not liveness:
an idle/"completed" process may still resurrect, so confirm it dead before you reuse, sweep, or launch a
continuation into its worktree. "The verdict is in the artifacts" is not "the process is gone."

**When you do judge liveness, measure it over the whole worktree — never over `.agent-work/<work-id>/`.**
A commander at `reconcile` writes to the **source tree**, not to its workbench, so a workbench-only mtime
probe reads silence exactly when reconcile is going *well*. Measured on a healthy commander: inter-write
gaps at `reconcile` reach **~7 minutes**, so a threshold under ten adjudicates live agents dead. A
workbench-only probe once came one step from killing a commander that was writing `docs/` and `skills/`
continuously.

A third read, distinct from both *done* and *stalled*: an idle subagent whose `current` carries a
`REFRESH REQUESTED:` line (the uniform reach-up primitive — `global-everyone.md` §reach-up) tripped correctly,
filed the pointer, and stopped exactly as designed. Relaunch immediately: a **fresh** agent, pointed at the
**same job file** (job-file-not-agent-file — the file is never copied or replaced), that cold-starts from
`current` alone (`DIGEST:` + `ACTIVE <gate> — <imperative>`). Do not write it a handoff document and do not
re-brief it from your own memory of the run — the digest is the brief. This is distinct from a **query
round-trip** (the same agent continues after you answer a context question it lacked — no cold start, no
agent swap) and from the **dead-agent recovery drill** (host-process exit, no id left to message): a refresh
is a *live, correctly-idled* agent whose replacement is a deliberate act, not a resurrection.

**Job-file-not-agent-file buys journal continuity with actor attribution, and that
trade is deliberate** (#369). The replacement reuses the predecessor's session id,
so the hash-chained journal reads as one unbroken run of one job — which is what
you want when reconstructing *what happened to this work*. The cost is that the
entries cannot tell you *which agent* wrote them: in epic-298 journal seq 44–47
all carried `commander-304-e298` and none of them were commander-304's. Take the
trade knowingly; do not expect the journal to answer the actor question.

Where a takeover is *not* the deliberate reuse case, the engine already records
the actor split for you, with no flag to remember: any reclaim of a stale lease —
and every forced claim — writes `previous_session_id` and `takeover_reason`
into `engine_session` (`checklist_engine.claim`). A force claim additionally
prints an **occupancy report** — journal entry count, newest entry's age and
session id, non-terminal `crew-runs.json` entries — so a resuming agent sees the
room it is walking into at the moment it walks in. It is information, not
permission: the takeover still succeeds, and deciding whether to proceed is
yours. It does not check git authorship (every agent commits under the human's
identity, so the signal is constant) and it does not walk the worktree.

Adjudication ends with a shutdown, not an idle. Once an agent's work is accepted, merged, and harvested,
send it a `shutdown_request` and confirm the termination — accepted-but-idle agents accumulate as clutter
and ambiguity about what is still live. An agent that answers a shutdown request with another idle
notification usually isn't refusing; it didn't parse the protocol — re-send as a plain message quoting the
pending `request_id` and the exact `shutdown_response` call to make. Never shut down an agent whose work
you have not yet adjudicated and harvested; the shutdown is the last step of closeout, not a cleanup
reflex.

## Arm a watchdog on everything you dispatch

Completion signals are not guaranteed to arrive: subagents die silently, background runners get reaped,
and a watcher keyed to "the EXITCODE line appears" waits forever when the process dies without writing it.
After dispatching background work, **arm an independent wall-clock watchdog** keyed to the work's own
deadline (a scheduled wake-up where the harness offers one, otherwise a polling loop): when the deadline
passes without a result, wake, inspect the artifacts, and adjudicate — do not keep waiting on a signal
that may never fire. Every watch-failure incident in the field followed the same shape: the watcher
trusted a completion signal and slept through the death. The deadline, not the signal, is the backstop.
