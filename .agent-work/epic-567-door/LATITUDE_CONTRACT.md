# Latitude Contract: `epic-567-door`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

Dispatch named "epic 657"; no such issue exists. Confirmed with the human as a digit
transposition of **#567**, which the 2026-08-16 planning ruling had already named as the
next epic.

## Epic Intent

One interface for agents: the MCP door. The CLI becomes an operator/debug path only.
The outcome that must not be violated: **this epic reduces complexity by removing a
redundant path.**

**Amended 2026-08-17 by Tommy.** The earlier wording — "every lane ends
net-mechanism-negative, something is deleted" — was never his rule. It came from the
Admiral's memory of the 2026-08-16 planning session and mis-stated his intent, then rode
into all four wave-1 launch orders as a hard pre-ruling. Withdrawn. The goal is reducing
complexity, and a lane whose whole job is removing a redundant path serves that even when
its own line count rises.

## Success Shape

A dispatched crew drives **its own** spine through the door end to end; no agent-facing
file teaches the CLI; a guard refuses reintroduction; ExternalBackend refuses a spineless
"success".

A measured negative is a complete, successful deliverable. If lane A finds that
per-dispatch spine identity cannot be had without adding more mechanism than it removes,
that finding — stated with its evidence — closes the lane successfully and the doctrine
sweep does not proceed on a false premise.

### Measured starting point (`600de02`, 2026-08-16)

| Claim | State |
|---|---|
| CLI-fallback clauses | **15**, across 11 files |
| live `<engine>` tokens | **11**, across 7 files (incl. `scripts/init_work_area.py`) |
| door mention in `specs/*.spine.toml` | **zero**; only `implementer` and `reviewer` specs exist |
| verb gap | **closed** — 11 tools cover every engine verb |
| a role agent reaching its **own** spine through the door | **impossible** |

The last row extends the epic body. #559 frames unreachable-own-spine as a *dispatched
subagent* problem; it is not. It hit **this Admiral in its own process at step one** —
`spine_status` returned `REFUSED: no spine is bound to this door`, because `spine_open`
only *mints* a new worktree+branch+spine and no verb binds the door to an existing spine
file. Init was driven on the CLI fallback and logged as an `ADMIRAL ERROR`. The doctrine
sweep is therefore genuinely blocked behind lane A: you cannot delete a fallback that is
currently the only path.

## Checkpoint Protocol

**Stop-and-present at each wave boundary.** Two checkpoints: post-W1, and closeout
acceptance. What reaches the human: a plain-English summary and the decision asks;
evidence on demand.

## Wave Plan

**Wave 1 — unblock and independents (4 lanes, concurrent).** Boundary: `w1`.

| Lane | Issues | Deliverable (the "ends by deleting" column is withdrawn — see the amendment above) | Tier |
|---|---|---|---|
| A | #559 anchor + the bind-own-spine gap + #613's `save()`-atomicity half | per-dispatch spine identity; the door reaches the caller's own spine | Opus |
| B | #432 | ExternalBackend refuses a spineless "success" — deletes the mtime-only path | Sonnet |
| C | #442 + #595 | rail and HARD-refusal readability; settle which of the two competing advisories wins | Sonnet |
| G | #574 + #552 | one-verb mechanical closeout behind `spine_close`; archiving releases the lease (43 stale leases on disk) | Sonnet |

**CHECKPOINT — contract expires here.**

**Wave 2 — the subtraction wave (3 lanes).** Provisional; re-cut at the boundary from
what W1 actually landed.

| Lane | Issues | Deliverable |
|---|---|---|
| D | doctrine sweep + #565 + #561/#596/#526 | delete 15 clauses and 11 `<engine>` tokens, sunset the workbench teaching half (~282 lines), rehome its templates, **land the regrowth guard** |
| E | #541 | door rejections captured as episode friction |
| F | #535 | reveal the spec through the spine, not the launch order |

The forecast is provisional. At the W1 boundary the replan pass runs
(`REPLAN_INPUT`/`REPLAN_RESULT` under `transitions/w1/`, `NEXT_WAVE.json`, one
`TRANSITION` audit line, then `verify_iterative_role_artifacts.py admiral-prelaunch`).

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | **surfaced** |
| Scope change (issue added/dropped/re-scoped) | **surfaced** |
| Merge to main | **delegated** — pre-approved for this epic specifically |
| Issue filing | **HELD — see below** |
| Issue closing (this epic's own member issues) | **delegated**, on verified-merged only |
| Fix-now triage (bounded fix applied immediately, not filed) | **delegated** |
| Spend / budget / model tier | **delegated** within the wave plan above |
| Production defaults / user-visible behavior | **surfaced** |
| Self-hosting hazard (lane A edits the engine driving this spine) | **delegated**, under the pre-ruling below |
| **Out-of-taxonomy** | **always escalates**, with one line on why it fit no class |

**Issue filing is held, not delegated and not surfaced.** The human's ruling:

> keep track of the issues, but we've been ballooning out tracking. let's hold on to them
> until the end then see if we can pair them with open issues, anything else we can file
> under episodes.

Operationally, and carried into **every** launch order: **no lane files any issue during
the run.** Triage candidates accumulate under
`.agent-work/epic-567-door/triage-candidates/`. At closeout each is paired against an
**open** issue as a comment where one fits; whatever does not pair is recorded as an
**episode** rather than minted as a new issue.

- **Apply a lesson / fold doctrine** — **surfaced.** A lane may not promote an observation
  into `docs/agents/*` on its own; that is a human's call per the project overlay. Lanes
  record observations and say so.

## Permission prerequisites

A `delegated` disposition settles who decides, not what the harness permission classifier
will let through — it can veto the concrete action at runtime regardless (#145, and #408
where this recurred at the Admiral's own merge step).

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr create`, `gh pr merge`, `git push` | No settings allowlist entry granted. **Fallback (#408's recorded shape):** on a veto, take one human approval in the moment, then **batch the remaining equivalent merges to the next checkpoint** rather than re-litigating each one. Log the veto as an `INCIDENT`. |
| Issue closing (member issues) | `gh issue close`, `gh issue comment` | Same fallback: one approval in the moment, batch the rest. |
| Fix-now triage | file edits inside the lane's own worktree | No external action; no clearance needed. |
| Self-hosting engine edit | running the edited engine against a **copy** of the live spine | No external action; the copy is the safety. |
| Worktree provisioning | `git worktree add`/`remove`, `git branch` | Routine local git; no clearance needed. Logged in `ADMIRAL_LOG`. |

## Float-Up Routing

When a Commander floats — a `user-decision` **or a context query**: for a decision,
adjudicate inside delegated classes and log a `RULING`; escalate surfaced classes and
out-of-taxonomy to the human. For a **context query**, answer from epic knowledge and
continue the Commander; reach the human out-of-band when the answer is beyond Admiral
knowledge or latitude.

Per-class nuance: a lane that wants to **file an issue** is not floating a decision — the
answer is already ruled. Point it at `triage-candidates/` and continue it without
escalating.

## Comms

Plain English by default; technical depth and evidence on demand.

## Budget / Model Parameters

All four W1 lanes run concurrently. **Opus** Commander on lane A (design-heavy,
load-bearing interface). **Sonnet** Commanders on B, C and G (bounded, well-specified).
Least-powerful-model-that-works, escalating only where complexity or risk demands it.

**Usage-limit budget.** The account session pool is a **wave-sizing input**, not merely a
per-issue budget. Four concurrent Commanders plus their crews draw on one pool. When a
limit reset is near, **defer the next wave's dispatch past the reset rather than launching
into it** — a wave that trips the limit mid-flight strands its Commanders worse than one
that waited.

## Pre-Rulings

Each is overridable by the human at any checkpoint.

- `decision:no-issue-filing-mid-run` — no lane files an issue; triage candidates go to
  `.agent-work/epic-567-door/triage-candidates/` and are dispositioned at closeout.
  `@grade: settled/human · leans all lanes`
- `decision:self-hosting-engine-edit` — lane A rewrites `checklist_engine.py` and
  `mcp_spine_server.py`, the very engine driving this Admiral's spine. Implement and review
  in the isolated worktree. **Before merging**: a read-only `current` on the live spine
  must exit 0, and a mutating verb (`advance`) must run against a **copy** of the spine —
  never the live file — to confirm it refuses or succeeds sanely rather than crashing.
  Only then merge, sync the checkout, and drive remaining advances on the new engine.
  `@grade: settled/doctrine · leans A · fleet-doctrine.md §engine-platform-quirks`
- `decision:in-session-hook-observation-is-not-evidence` — hooks execute from the main
  checkout regardless of worktree (`CLAUDE_PROJECT_DIR` resolves once at session launch,
  #269). Any lane validating engine or hook behavior does so in a **fresh process** with
  explicit paths. An in-session observation after an edit is struck from any gate that
  would accept it. `@grade: settled/project · leans A, G · ORCHESTRATOR_CONTEXT.md`
- `decision:sequence-hook-touching-lanes` — concurrent lanes editing hook code can break
  every live session. If two W1 lanes both touch `scripts/hooks/*`, they merge sequentially
  behind a fresh-process suite, never on their own liveness.
  `@grade: settled/project · leans A, G`
- `decision:design-it-twice-on-A` — #559 introduces a load-bearing interface, so lane A
  generates N≥2 candidates under distinct named constraints before converging.
  **Convergence is human-only**: lane A returns a comparison and a recommendation; the
  Admiral surfaces it at the W1 checkpoint. `@grade: settled/doctrine · leans A`
- ~~`decision:every-lane-deletes`~~ — **WITHDRAWN 2026-08-17 by Tommy**, who never set it:
  *"I never said that every lane needs to end with something deleted, or at least never
  intended that."* It was the Admiral's mis-recording of the 2026-08-16 session. Replaced by:
- `decision:reduce-complexity` — judge a change by whether it reduces complexity, and in
  particular by Tommy's test for trades of this kind: **does this choice reduce work on
  agents by moving it into mechanisms?** Removing a redundant path counts even when the
  removing lane's own line count rises. Do not over-engineer; note simplification
  opportunities rather than building for them.
  `@grade: settled/human · leans all lanes`
- `decision:honest-null-is-complete` — a measured negative is a successful deliverable,
  stated with its evidence. `@grade: settled/human · leans all lanes`
- `decision:worktrees-provisioned-by-admiral` — the Agent-tool `isolation:"worktree"` flag
  is not trusted. The Admiral runs `git worktree add` per lane, logs it, and gates the wave
  on `verify_worktree_isolation.py` exiting 0 before any dispatch.
  `@grade: settled/doctrine · leans all lanes · fleet-doctrine.md`
- `decision:no-turn-ending-waits` — the Admiral polls dispatched Commanders inside its turn
  and never ends a turn waiting on a wave. `@grade: settled/doctrine · leans admiral`

## Expiry

**Event: the W1 checkpoint.** The contract covers wave 1 and its adjudication. Crossing
into wave 2 forces a contract-refresh decision before further dispatch. It also expires
early on any material exception that invalidates the wave plan.

## Confirmation

2026-08-16 — confirmed by Tommy across two interrogation rounds (scope and slurps; then
checkpoints, decision classes, budget, expiry). Recorded as `user-decision` evidence on
the latitude step. Full record: `.agent-work/epic-567-door/INTERROGATION_RECORD.json`.
