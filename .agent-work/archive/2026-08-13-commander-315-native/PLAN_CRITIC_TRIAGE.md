# Cold plan critic — triage of every finding

Critic report: `.agent-work/commander-315-native/PLAN_CRITIC.md` (17 CONFIRMED, 3 PLAUSIBLE).
Triaged by the Commander in delegated mode; the Admiral is the ratifying authority and the
human ratifies at the epic return boundary. No finding was left undisposed.

Dispositions: **PLAN** (changed the frozen plan), **FILE** (triage candidate, not this run),
**NOTE** (accepted and recorded, no action), **REJECT** (with reason).

| # | Finding | Disposition |
|---|---|---|
| 1 | The guard's subject is the same ambient cwd; `cd` disarms it in one token; the delivered property is coverage + unbypassability, not non-forwardability | **PLAN** — intent rewritten to claim only what is delivered, and to state the limit explicitly |
| 2 | `heartbeat`/`release` write; the exemption carries a write | **PLAN** — `heartbeat` moved into the guarded set; `release` stays exempt as the named recovery hatch, with the hole stated |
| 3 | The guard's own refusal writes into the protected tree and can clobber a concurrent writer | **PLAN** — the guard refuses in `main()` before `dispatch()` and without persisting |
| 4 | Inert on child checklists (`review.json`, `IMPLEMENTER_PLAN.json`) — where crew subagents work | **NOTE + FILE** — stated as a scoped limit; extending the stamp to the other instantiation paths is a separate issue |
| 5 | `tests/test_explorer_templates.py` breaks by construction; the integrate gate runs 6 files | **PLAN** — integrate now runs the full suite; the test reconciliation is pre-authorized in the handoff |
| 6 | The two producers emit incompatible `origin.worktree` formats (`str(Path(...))` unresolved vs `as_posix()` resolved) | **PLAN** — normalization specified explicitly as a constraint |
| 7 | `== Path.cwd()` in the frozen plan is a regression against containment | **PLAN** — plan says containment; the repro gains a subdirectory case |
| 8 | The repro's discriminator is a prose substring match — the named corollary defect, in a postcondition | **PLAN** — repro rewritten to assert the state fact (no lease taken), not the sentence |
| 9 | `c1` runs a test file the implementer authors, with nothing arming its failing side | **PLAN** — the Commander arms it by mutation at integrate: revert each half, show the new tests go red |
| 10 | The fallback shape is not exhaustive; `validate_spine` guards `origin` not at all | **PLAN** — the exhaustive shape walk is a constraint and a required test |
| 11 | A stamped spine becomes unclaimable once its worktree is removed at closeout | **NOTE + FILE** — the `release` exemption keeps lease-clearing working; the `claim --force` half is a real gap, filed |
| 12 | The merged tripwire is green by construction and blind to the new path; its own docstring invites teaching it the new contract | **PLAN** — new deliberate-breakage coverage for the origin path is required, authored in the NEW test file so the merged guard is neither weakened nor rewritten |
| 13 | `init.c0` vacuity confirmed; the cost of shipping it knowingly is understated | **NOTE + FILE** — floated to the Admiral, filed as a triage candidate, and stated loudly in the return and PR body |
| 14 | `origin` is undocumented as a top-level key in `docs/CHECKLIST_SCHEMA.md` | **PLAN** — a docs deliverable added to the gate |
| 15 | The frozen plan lost the converged design and does not cite `PLAN_ALTERNATIVES.md` | **PLAN** — `execute.json` rewritten to carry the design and cite it |
| 16-17, plausibles | (see report) | **NOTE** — recorded; none changed the plan |

## Count correction

The critic counts **2** live origin-less spines; this run counted 3. Both are right and the
difference is this run itself: `.agent-work/commander-315/spine.json` and
`examples/mcp-interactive-demo/spine.json` pre-existed, and
`.agent-work/commander-315-native/spine.json` was created by this Commander at its `init`
step, after the launch order's measurement. The launch order's "2" is correct as of
`9bb8c1b6`. Stated as **2 pre-existing + 1 created by this run**.

## Finding 1 is the one that matters most

It is the only finding that changes what this run may honestly claim. The launch order says
"the engine asking itself where it stands cannot be lied to by a child process's cwd." That
is true and narrow: no child process can lie to the engine. It does not follow that the
*agent* cannot choose where the engine stands. Since `_run_check_command` passes no `cwd=`,
the existing `--here` check and the new native comparison read the same ambient value.

The change is still strictly stronger than what it replaces, for the three reasons now
stated in the frame's Intent. But "non-forwardable" is not among them, and this run does not
certify it. This is reported to the Admiral as a correction to the order's framing, not as a
reason to stop: the ruled direction remains right, its benefit is just narrower than the
order states.
