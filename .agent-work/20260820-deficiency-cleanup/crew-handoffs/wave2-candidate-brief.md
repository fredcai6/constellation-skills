# Shared brief — architecture candidate lanes

You are one of **three independent candidate authors**. Each of you starts from a
different root-cause hypothesis. You will not see the others' work, and you must
not go looking for it. Divergence is the point: if all three lanes converge by
accident the exercise has told the human nothing.

## What you are producing

**An artifact, not a change.** You do not choose an architecture, you do not
implement one, and you do not touch source, tests, or GitHub. A human chooses
later, from your candidate and two others, with a cold critic's comparison in
hand. Write for that reader.

## The knot

Six open issues, one cluster:

- **#634** — a run's plan should be frozen at the bookends and mutable in the middle, in one spine per agent
- **#638** — the door's fixed path, identity and spine are set at process start, so a run cannot act on itself or move its own work area
- **#632** — a helper agent inherits its launcher's spine and Stop hook, so every dispatcher must strip four variables by hand
- **#357** — the lease does not protect the gates: child gate plans carry `engine_session: null`, so a force-claim buys no exclusivity
- **#369** — the resume side of the recovery drill has no obligations: confirm-alone is one-sided, and `claim --force` erases actor attribution
- **#615** — a spine with no active lease has no ownership guard at all, never-claimed or released

Read all six with `gh issue view <n>` before you design anything. Read them in
full, including comments.

## Required reading, in order

1. `.agent-work/20260820-deficiency-cleanup/evidence/LIVED-CLUSTER-EVIDENCE.md`
   — five reproductions this epic hit on current code, each with the hand
   workaround actually used. This is your sharpest input.
2. `.agent-work/20260820-deficiency-cleanup/crew-handoffs/wave2-cartographer-result.md`
   — the orientation section names the modules and seams the cluster lives in,
   with entity counts, documented holes, and dependency direction.
3. `map/INDEX.md` at the integration base, and the source it points at:
   `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
   `scripts/spine_lifecycle.py`, `scripts/run_crew.py`.
4. The six issues.

There is no curated packet map under `docs/architecture/` and you must not
author one — the human ruled against it. Ground on root `map/` and source.

## Your candidate must contain

- **Boundaries** — what components exist, and what each one owns.
- **Ownership and authority** — who may act on a spine, a gate, a child plan;
  what a parent may do to a child and what it may not.
- **Failure semantics** — what happens on crash, on takeover, on a dead session
  holding a lease, on a stranded child plan.
- **Migration** — how the repository gets from current state to yours, in
  stages that each leave the system working. Name what breaks.
- **Issue dispositions** — for each of the six: does your design close it,
  partly close it, leave it open, or reveal it as mis-scoped? An honest "this
  issue is already mostly fixed" or "this issue dissolves under my design" is a
  valuable finding, not a dodge.
- **Risks** — where your design is most likely to be wrong, and what evidence
  would falsify it.
- **Tests** — what would have to pass for someone to believe the design landed.

## The acceptance tests you cannot skip

For **each** of E1–E5 in the lived-evidence dossier, state plainly whether your
design **removes** the workaround, **keeps** it, or **replaces** it with a
different one. "Keeps it, and here is why that is acceptable" is legitimate.
Silence is not.

The sharpest of these is E5's five-step handshake — release → parent claims →
parent waives → parent releases → child reclaims. If you claim to fix parent
capability, say what that sequence becomes under your design.

## Honesty obligations

- If your assigned hypothesis turns out to be **wrong** — if the evidence does
  not support it as the dominant root — say so directly and design the best
  thing the evidence does support. Do not defend your seed. A lane that reports
  "my hypothesis is not the root, here is what is" is a success, not a failure.
- The four reproductions in the dossier are **not a ranking**. They are what one
  Admiral-driven run happened to trip over, and an Admiral is the most
  privileged actor in the system. Do not infer importance from frequency.
- Where you are guessing, mark it as a guess.

## Hard constraints

- Do not choose or implement an architecture. Artifact only.
- Do not change source, tests, or `map/`. Do not commit anything.
- No push, no PR, no GitHub mutation. `gh issue view` reads are fine; nothing
  that writes.
- Do not author `docs/architecture` packets or overlays.
- Do not call any `mcp__spine__*` tool. The door in your session is bound to the
  Admiral's epic spine and driving it would corrupt the run. This lane is
  unrailed by ruling.
- Do not read the other candidate lanes' results.

## Workspace

Read from the integration worktree `/tmp/constellation-20260820-integration`
(branch `afk/20260820-deficiency-integration`, base `efe92791`, ordinary suite
green at 3447 passed / 6 skipped / 1222 subtests). Treat it as read-only.

Write your result to the main checkout at
`/home/tommy/projects/constellation-skills/.agent-work/20260820-deficiency-cleanup/architecture/<your-lane>.md`.
Do not commit it.
