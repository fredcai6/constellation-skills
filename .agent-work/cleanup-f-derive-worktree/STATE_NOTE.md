# Crash-resume state note — cleanup-f-derive-worktree

- **step:** execute · leg 4 parked at the engine's context line · `execute.json` gate **`g3-review`** is next and it is **nearly free**: the work is done, the crew returned **APPROVE**, and `e-g3-review-2 (review-result, verdict=APPROVE)` is already attached. You only have to `start g3-review`, then `advance g3-review --why "..."`, then `advance g3-integrate`. After that: `skip` g4 (R2), `skip` g5 (R3), then reconcile → triage → review → feedback → archive.
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree` · `g3`'s code is committed through **`539ff636`**
- **next command:** `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/execute.json current`
- **pid:** none — foreground; no crew running. `recover_crews.py` reports only this commander leg ACTIVE; every g3 crew is COMPLETE.
- **expected artifact:** `.agent-work/cleanup-f-derive-worktree/execute.json` driven to terminal, then the spine's `archive` closeout — this leg's result artifact is `.agent-work/cleanup-f-derive-worktree/crew-handoffs/execute-commander-result.md`

**Read first on resume:** `LAUNCH_ORDER-4.md`, **`FLOAT_TO_ADMIRAL-3.md`**,
`ADMIRAL_RULING-3.md`, `ADMIRAL_RULING-2.md`, `ADMIRAL_RULING-1.md`, then
`LAUNCH_ORDER.md`, `PROBLEM_STATEMENT.md`, `MISSION_FRAME.md`, `UNTAKEN_ROADS.md`.

## Why this leg stopped

**Not blocked.** The engine's context governor refuses to `start` a new gate at
19% fill — *"finish and close the gate you are already in, then request a refresh
so a fresh agent starts this one."* I am between gates at a clean boundary, so I
filed the refresh-request it named (`e-g3-review-3`, `seam=g3-review`,
`why_ref=w-16`) and parked. **The lease is deliberately NOT released** — the run
is not done. Re-claim as `commander-cleanup-f-derive-worktree`, **never
`--force`**; an owner is never blocked by its own staleness.

## g3 is done and approved. It cost five reviews and four reworks.

Every review returned a genuine, measured defect. **Not one was found by
reading.**

| review | found | whose |
|---|---|---|
| 1 | **B1** the implementer's differential pinned its BEFORE arm with `git rev-parse HEAD` and inverted into comparing the change against itself · **B2** `decide_session_start` selected by dict order, not ownership · **B3** false prose survived the symbol's deletion | g3's |
| 2 | **B4** the B2 fix newly routed "can see entries, owns none" sessions into the scan-bind, whose write then defeated the Stop path's foreign-owner withholding | g3's |
| 3 | **B5** the B4 fix guarded one of the two routes leaving `spine` `None`; the other bound the session to a spine a sibling agent visibly claimed | g3's |
| 4 | **B6** the same door still *rendered* another key's gate on an ambiguous scan · **B7** `owners` is a session view and three sentences called it the store | **pre-existing** |
| 5 | nothing. **APPROVE**, 0 findings, 8/8 criteria | — |

**The one finding worth more than the bugs:** this gate removed a guard that was
**accidentally gating a write**. `_foreign_worktree` was a bad ownership test,
but while it stood it kept a whole class of session out of
`decide_session_start`'s fall-through. Deleting it was right; every defect since
was a session arriving somewhere it had never previously reached. **When a gate
removes a guard, enumerate what the guard was incidentally preventing, not only
what it was wrongly deciding.** Nobody did that here and it cost four cycles.

**What g3 finally ships.** `_foreign_worktree` deleted with both call sites.
`_entry_mid_flight_view` reads no payload — mid-flight is a property of the spine.
`_own_entries` is the shared ownership comparison at both sites.
`_attributed_to_another_key` guards the bind-on-resume's **write and its render**:
neither may contradict an attribution `session_view_provenance` already holds. A
path attributed to **nobody** behaves exactly as before, so `tc1` is untouched.

## Three things are with the Admiral — `FLOAT_TO_ADMIRAL-3.md`

None blocking; I took a reading on each and said so.

1. **I re-opened the bind-on-resume writer**, which earlier handoffs on this gate
   fenced as `tc1`. Bounded to "may not contradict an existing attribution", under
   the Admiral's rule that *the change that falsifies a claim owns the repair*.
2. **Should the guard reach across the session boundary?** (B7) `owners` is
   session-scoped, so a cross-session attribution is invisible. I ordered the prose
   honest and did **not** widen. The fifth reviewer named this as the Admiral's.
3. **B6 was pre-existing and I ordered it fixed anyway**, because the rule this
   gate had already shipped was incomplete without it.

## The gate's open decision — six crews converged on this

> Record it **closed** and retire the refinement: **selection is a binding-key
> property at every site that selects, full stop.** The fallback was never a
> counterexample to that rule — it was the one site never held to it — and now
> that its render and its write ask the same predicate, the asymmetric refinement
> has nothing left to describe.

## Baselines, all re-measured by leg 4

| tree | result |
|---|---|
| `main` at `17c2cee5`, isolated clone | **3171 / 7 / 0** |
| pre-gate `53c89ba1` | 3170 / 5 / 0 |
| g3 pass 1 · rework 1 · rework 2 · rework 3 | 3177 · 3183 · 3187 · 3190, all /5/0 |
| **g3 rework 4 `539ff636`** | **3192 passed / 5 skipped / 0 failed** |

Failure sets empty in every direction. The targeted class went 0 collected
(pytest exit 5) → **23 passed**.

## What remains

1. **`g3-review`** — start, advance (APPROVE already attached), then
   **`g3-integrate`**.
2. **`skip` g4** with **R2** — its ruled behaviour (an unowned spine path yields
   no derived worktree and today's behaviour, never a refusal) was already
   shipped by g1; `_worktree_from_spine` returning `None` is the complete answer.
   **`skip` g5** with **R3** — #315 is descoped and re-homes to #610's wave.
3. **reconcile** — three prose repairs, all this lane's own debt:
   - the door's stale `SPINE = Path(os.environ["SPINE_FILE"]).resolve()` contract
     citation in `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`.
     **Cite by the string to grep for, not by line.** Current truth is
     `mcp_spine_server._spine_from_env`, which collapses unset, empty and
     whitespace into `None` and refuses per call via `_unbound_refusal`.
   - **tc10**: `tests/test_explorer_templates.py` and
     `tests/test_mcp_door_engine_cwd.py` still assert the engine reads its ambient
     cwd and enforces the `origin.worktree` comparison. g2 made both false, so
     this lane owns the repair (ADMIRAL_RULING-3). Where a repaired passage
     contradicts the 2026-08-15 worktree-identity ruling, **cite that ruling and
     say plainly that this lane supersedes it.**
4. **triage** — `tc1`–`tc12` in `execute.json`, plus what the g3 crews raised:
   the SessionStart scan-bind (`tc1`, with the Admiral); the three-states taxonomy
   stated in four places, two already stale; `decide_session_start` at 159 lines
   wanting an extraction; provenance last-key-wins on a path collision;
   `agent_id: null` on Stop; `bind()`'s `None`→`str(project_dir)` substitution;
   and two fresh comments the fifth review flagged as claiming a measurement over
   an empty set.
5. **review, feedback, archive.** Park at `archive`. **Do not merge** —
   publication is the Admiral's and nothing is queued behind this lane.

## Hazards that cost this lane measurable time

- **Every instrument on this gate developed a shelf-life defect, in both
  directions.** One pinned a *moving* `HEAD` (that was B1); two pinned
  *superseded* commits, so re-running them unmodified showed fixed defects as
  still present — I hit that twice and had to add working-tree arms with guards.
  **Build your own instrument before running theirs, and make every arm print
  what it actually loaded.** The fifth reviewer's harness does exactly that
  (sha256 + byte length per arm, guarded that all three differ) and is the model.
- **I cited a sha I had amended away.** My review-3 handoff named `9b1a551e`,
  replaced minutes earlier by `7d12c29d`. Content identical, nothing moved, and
  the third reviewer caught it. Amending a commit after citing it is a specific
  way to break ADMIRAL_RULING-3's "cite by the string, not the line".
- **`CREW_SCRATCH_DIR`.** The engine's own gate-close suite command scrubs
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` but **not** this, and a Commander is
  itself launched through `run_crew.py`. Close gates with
  `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py … advance …`. `tc12`;
  the Admiral has taken it as an engine defect.
- **The registry clobber (#617, folded into #574).** `run_crew.py`'s parent writes
  a pre-launch snapshot back over `crew-runs.json` when the child exits. Git is
  the only durable store: **commit `crew-runs.json` as each gate closes**, and on
  resume check the working copy against `HEAD` before trusting `recover_crews.py`.
- **Baseline clones must be named `constellation-skills`.**
  `tests/test_code_map.py::MapTreeFreshnessTests` derives `map/INDEX.md`'s title
  from the checkout directory name, so a clone at any other path reports a false
  red in an otherwise byte-identical 29k file. It cost me a full suite re-run.
- **Nine crews on this gate refused the `SPINE MID-FLIGHT` nudge** and recorded
  the refusal, exactly as instructed. None was penalised and **none wrote to this
  spine.** The mechanism is `tc1`.

_Updated: 2026-08-17T01:35:00+00:00_
