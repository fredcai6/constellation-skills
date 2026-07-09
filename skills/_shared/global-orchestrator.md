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

## Gating, evidence, stop/ask

- Pause for a `user-decision` at the project's enabled checkpoints (the rigor dial). Human verification is a
  first-class step.
- Delegated/autonomous (running from an Admiral `LAUNCH_ORDER`, no reachable human): the frozen launch order
  IS the ratified intent — satisfy `user-decision` checkpoints by citing it; take a genuine gap (a decision
  outside latitude, or missing context) to the Admiral.
- Stop and ask when project context, user instruction, and observed artifacts conflict in a way that affects
  the task. Do not resolve a conflict by picking an authority source by policy.

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
