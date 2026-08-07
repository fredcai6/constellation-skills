Closes #34. Closes #36.

## The finding

Two related gaps from the 2026-06-24 dogfooding harvest, both tracing to skill/template text that assumes a **reachable human** or a **crew per gate**:

- **#34 — no sanctioned autonomous Commander.** `constellation-commander` is written as the human's rigor scaffold ("surface decisions to the human"), but under an Admiral it is routinely driven autonomously on a harness where a dispatched subagent **cannot reach the human**. The `understand` step's Interrogator "must reach the human," four `user-decision` checkpoints pause for a human, and gates launch nested crews — none fits. Admirals worked around it by abandoning the Commander skill and re-deriving a bespoke implementer every run. Separately, an idle Agent-tool commander sometimes returns only an `idle_notification` and **never emits its verdict text** (hit 2 of 4 commanders), so an Admiral could hang waiting for a message that never comes.
- **#36 — three commander-spine papercuts.** The `compact` step runs `/compact` (a user-level CLI the agent can't invoke) → a dead skip every run; the execute gate mandates implementer/reviewer crew dispatch for **every** gate, even pure design-note gates where a crew is *shallower*; and a crew reviewer's survey JSON landed at the worktree root, leaving orphan untracked scratch.

## The strategy — documented reading, zero engine code

Every fix is a **documented reading / convention** of the existing spine — **no new engine fields, gate markers, or spine variants, and nothing under `scripts/` changes.** This is mechanically sufficient: the engine already accepts a `user-decision` artifact regardless of who authored it, already accepts attested (`check: null`) postconditions, and already lets the Commander author the gate shapes it needs. Consistent with the fold-back arc's no-new-machinery posture (#32/#33/#35).

## The change

- **Delegated/autonomous mode** (`commander/SKILL.md`, `COMMANDER_SPINE`, `interrogator/SKILL.md`). Running from an Admiral `LAUNCH_ORDER` is the delegated signal: the `understand` step reconciles against the frozen launch order instead of interrogating a human; the four `user-decision` checkpoints are satisfied by **attaching a `user-decision` evidence item citing the launch order**; the Interrogator carries a delegated-context clause.
- **The chain terminates at the human.** Autonomous mode is *not* a licence to guess. Beyond the launch order the Commander has two recourses up the same channel — **float an out-of-latitude decision**, or **query the Admiral for missing context**. A delegate is not a replacement: when the Admiral's own knowledge and latitude run out, **"I need to talk to my human" is a first-class move**, reaching the human out-of-band. Honest about the mechanism: this is a *float-and-continue round-trip* (the Commander returns with context intact and is continued), **not** a host-process resume — distinct from the dead-Commander recovery drill. The Admiral side (`admiral/SKILL.md`, `LATITUDE_CONTRACT`, `LAUNCH_ORDER`) is the receiver: it fields context queries and the float-up routing + Stop Conditions are broadened to carry them.
- **Verify-from-artifacts on idle** (`fleet-doctrine.md` Adjudication invariants + `admiral/SKILL.md`). An idle commander with complete artifacts is *done*: verify from the artifact set + a clean-room reviewer, never block on a dropped verdict. This judges the **verdict, not liveness** — it does **not** weaken "confirm dead before you reuse/sweep the worktree" (idle ≠ dead).
- **Compact reframed conditional** (`COMMANDER_SPINE` + the matching `fleet-doctrine` quirk bullet). Run a compaction command if the harness exposes one, else rely on auto-compaction; **always reload the skill** (the load-bearing half). No more permanent skip-ceremony.
- **Reasoning gate** (`commander/SKILL.md` "Executing a gate"). A gate whose deliverable is a document/diagnosis may be authored crew-less, with the waiver reason stated — reconciling the "every gate has three tasks" / "Never hand-launch a crew" absolutes in place (a *crew gate* has three tasks and dispatches via `run_crew.py`; a *reasoning gate* dispatches none).
- **Crew survey-state convention** (`REVIEWER_HANDOFF` + `reviewer/SKILL.md`). The Commander dictates the path `.agent-work/<work-id>/<gate>-review/review.json` — under the issue workbench, never the worktree root.

## Testing

All documentation/template text — no engine code, so the gate is **review against the spec** plus a JSON-parse check on `COMMANDER_SPINE.template.json`. Full suite stays green: **222 passed / 1 skipped** (unchanged — the template-loading tests are the regression guard that the spine JSON still parses). A whole-`skills/`-tree grep confirms **no stale absolute** ("must reach the human" / "run /compact") remains unqualified anywhere.

Built subagent-driven (per-task TDD-style + spec/quality review + opus whole-branch review). The whole-branch review earned its keep: it caught stale absolutes in a **second** `commander/SKILL.md` location (the step table) that the per-task reviews structurally couldn't see — each per-task reviewer only sees its own diff, and the consistency grep had only swept `skills/commander/templates`. Fixed in the final wave (commit `db88b4f`), re-verified across the whole tree. The spec review also caught two scope gaps before the plan (the Interrogator skill needed the delegated clause; the reasoning-gate edit had to *reconcile* the absolutes, not just sit beside them).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
