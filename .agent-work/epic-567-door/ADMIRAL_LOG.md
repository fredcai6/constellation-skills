# Admiral Log — `epic-567-door`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Contract: `.agent-work/epic-567-door/LATITUDE_CONTRACT.md` · Plan: W1 = A (#559 + bind-own-spine + #613 atomicity, Opus) · B (#432) · C (#442 + #595) · G (#574 + #552), all concurrent · **checkpoint** · W2 (provisional) = D (doctrine sweep + #565 + #561/#596/#526) · E (#541) · F (#535)

The run's audit trail, and the raw material the closeout episodes are written from. Append
entries **as they happen** — an unlogged ruling didn't happen. Own errors in the open: an
ADMIRAL ERROR entry that names the mistake and the fix is a closeout asset, not a liability.

Entry grammar (one line of date + tag, then the substance):

- `RULING` — an adjudication inside delegated latitude: what was decided, under which decision class, and why.
- `WAVE` — a wave launched: commanders, issues, worktrees, key launch-order terms (pre-rulings, fences, budgets).
- `INCIDENT` — a commander/crew death, stall, collision, or environmental kill: what died, autopsy, recovery action.
- `MERGE` — a PR merged: checks gated on exit code, diff verified in-fence, merge style and why.
- `ADMIRAL ERROR` — a mistake you own: what happened, cost, immediate fix, and what an episode would record about it.
- `CHECKPOINT` — a contract checkpoint reached: what was presented, what the human decided.
- `ESCALATION` — a surfaced or out-of-taxonomy decision sent to the human, and the answer.

## Rulings & events

- `2026-08-16` — `ESCALATION`: dispatch named "epic 657", which does not exist (highest issue is #619). Asked the human; confirmed the target is **#567** ("the door is the interface — finish the MCP migration"), matching the 2026-08-16 planning ruling that named #567 as the next epic. Digit transposition.
- `2026-08-16` — `CHECKPOINT`: latitude contract confirmed. Interrogation drove `interrogation.json` (survey, 6 questions, 1 fact + 5 decisions) to `RESOLVED`; `verify_interrogation.py` exit 0; record at `INTERROGATION_RECORD.json`. Two waves, seven lanes. Merge-to-main and fix-now triage delegated; architecture surfaced; **issue filing HELD to closeout** ("we've been ballooning out tracking") — candidates stage under `triage-candidates/` and are dispositioned by pairing onto open issues or recording as episodes. Contract expires at the W1 checkpoint. Nine pre-rulings recorded.
- `2026-08-16` — `RULING` (scope class, delegated by the contract's own confirmation): the epic body frames #559's unreachable-own-spine collision as a *dispatched subagent* defect. Measured otherwise — it hit this Admiral in its own process. Lane A's scope therefore covers the general case (any role reaching its own spine), not just the Task-tool crew case. Basis: `spine_status` REFUSED in this session; `spine_open` mints rather than binds.
- TRANSITION | boundary=w1 | decision=advance | verified
- `2026-08-16` — `RULING` (transition, delegated): boundary `w1` exits **advance**. Three discrepancies dispositioned, none filed: `D-own-spine` (revise_plan — lane A's scope is the general case), `D-token-count` (record_evidence_only — 11 tokens, not 9), `D-tracking-ballast` (amend_forecast_or_parked — filing held to closeout). `verify_iterative_role_artifacts.py admiral-prelaunch` exit 0; `CURRENT_TRUTH.md` and `WAVE_REVIEW.md` rendered under `transitions/w1/`.
- `2026-08-16` — `WAVE`: wave 1 launched, four Commanders, four worktrees, all based on `600de020`.
  - Worktrees provisioned by the Admiral (the Agent-tool `isolation:"worktree"` flag is not trusted): `git worktree add .worktrees/567-a-spine-identity -b feat/567-a-spine-identity main`, and likewise `567-b-external-backend`, `567-c-rail-readability`, `567-g-closeout-lease`. All four succeeded.
  - Wave gate: `verify_worktree_isolation.py` across all four paths → "worktree isolation verified: 4 distinct worktrees", exit 0. Launch permitted.
  - Lane A — #559 + bind-own-spine + #613 atomicity — **Opus** — order `crew-handoffs/LANE_A_LAUNCH_ORDER.md`. Key terms: design-it-twice with human-only convergence; self-hosting proof (`current` on the live spine, `advance` on a copy) before PR; owns `checklist_engine.py` and `mcp_spine_server.py`.
  - Lane B — #432 — **Sonnet** — `LANE_B_LAUNCH_ORDER.md`. Key terms: the check must be able to fail and assert what it enumerated; red-proof against the shipped path, not a fixture; fenced off lane A's two files.
  - Lane C — #442 + #595 — **Sonnet** — `LANE_C_LAUNCH_ORDER.md`. Key terms: measure on real cold agents or float; Stop hook is authoritative (pre-ruled, not to be rediscovered); no third advisory mechanism; edits `scripts/hooks/*` so fresh-process validation is mandatory.
  - Lane G — #574 + #552 — **Sonnet** — `LANE_G_LAUNCH_ORDER.md`. Key terms: the PR-opening question is Tommy's and must be floated, not ruled; never run the verb against a live spine (this Admiral's own lease is one of the 43 counted); fenced off lane A's two files.
  - Carried into all four: no issue filing (candidates stage in each worktree); no doctrine promotion to `docs/agents/*`; every lane ends net-deletion; honest null is a complete deliverable; in-session observation of engine/hook behaviour is not evidence; commanders do not merge.
- `2026-08-16` — `ADMIRAL ERROR`: the epic's own door could not carry this spine. `spine_status` REFUSED — no spine is bound to this door process, and `spine_open` mints a *new* worktree+branch+compiled spine rather than binding an existing Admiral spine file. Drove init on the documented CLI fallback (`checklist_engine.py --file .agent-work/epic-567-door/spine.json`, installed copy per the dogfooding rule). Cost: none beyond this note. This is first-hand evidence for the epic's own subject — the Admiral, the role that owns the run, has no door path to its own spine.

- `2026-08-16` — `INCIDENT` (no loss; recorded as evidence for lane C): the Stop hook refused this Admiral's turn-end at `execute` — *"SPINE MID-FLIGHT: gate execute is still open… do not end your turn to wait."* The Admiral had dispatched wave 1, armed a bounded artifact monitor, and presented the wave to the human, judging that a monitor plus a human checkpoint was a legitimate in-turn wait. The hook disagreed. **This is #595's conflict firing live on the Admiral, while lane C is dispatched to fix it** — and it adds a case neither 2026-08-15 episode covered: the two prior instances were Commanders low on context at a gate boundary, whereas this is an orchestrator at full context whose gate cannot close until four dispatched subagents return. Lane C's resolution must decide what an orchestrator waiting on its own fleet is supposed to do, since `spine_halt block` (the sanctioned mid-run exit) would bubble a blocker to a parent that does not exist. Recovery: stayed in-turn and continued working the gate. No work lost.
- `2026-08-16` — `RULING` (fix-now triage, delegated): the Admiral's bookkeeping for this epic is committed to local `main` as it is produced, so a fresh clone can reconstruct the run. Scope is `.agent-work/epic-567-door/` only — no lane touches that path, so it cannot collide with a wave-1 worktree. Not pushed: the project overlay requires human approval for pushes, and the contract's merge pre-clearance covers PR merges, not direct pushes to `main`.

## Merges

- _none yet_

## Closeout

- _pending_
