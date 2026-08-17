# Crash-resume state note — cleanup-f-derive-worktree

- **step:** **`reconcile`**, and it is nearly free. Leg 5 did reconcile's whole
  substance, committed it at `684502ab`, and attested `c1` with its full evidence.
  The engine then refused to **begin** the gate — `start` is hard-guarded and this
  leg was at 0.155 fill against a 0.15 hard line — so a refresh-request is filed
  (`e-reconcile-1`, `seam=reconcile`, `why_ref=w-5`) and the gate is waiting for a
  fresh agent to `start` and immediately `advance` it. `execute.json` is
  **terminal** and the spine's `execute` step is **complete**.
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` ·
  worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`
  · code committed through **`684502ab`** · `main` at **`17c2cee5`**, re-measured
  by leg 5 and unmoved.
- **next command:** `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/spine.json current`
  then `start reconcile --session-id commander-cleanup-f-derive-worktree`, then
  `advance reconcile --why "..."`.
- **pid:** none — foreground, no crew running and none needed. Leg 5 dispatched no
  implementer or reviewer. `recover_crews.py` reports only this commander leg
  (`attempt-5`) ACTIVE; legs 1–4 show `NEEDS-ABANDON` and are my own parked
  predecessors, **not crews to recover**.
- **expected artifact:** the spine driven through `archive`; this leg's result
  artifact is `.agent-work/cleanup-f-derive-worktree/crew-handoffs/execute-commander-result.md`,
  **written and current** — read it first.

**Read first on resume:** `crew-handoffs/execute-commander-result.md` (leg 5's
return), then `LAUNCH_ORDER-5.md`, then `ADMIRAL_RULING-4.md` (the boundary that
closed `g3`), then `-3.md`, `-2.md`, `-1.md` (R1/R2/R3 and N2).

## Re-claim, never `--force`

Re-claim as `commander-cleanup-f-derive-worktree`. The lease is **deliberately
held** — the run is not done. An owner is never blocked by its own stale
heartbeat.

## What is already done

- **`execute.json` terminal.** `g3` closed on review 5's APPROVE (0 findings, 8/8
  criteria). `g4` skipped as **withdrawn** (R2 — the pre-ruling was itself the
  defect and `_worktree_from_spine` returning `None` is already the whole answer).
  `g5` skipped as **re-homed** (R3 — #315 moves to #610's wave).
- **Every number re-measured by leg 5, not cited:** `main` at `17c2cee5` in a clone
  named `constellation-skills` → **3171 / 7 / 0**; shipped tree → **3192 / 5 / 0**;
  targeted class **23 passed** where the same selector exits 5 on the pre-gate arm.
  Failure sets empty both ways.
- **`reconcile`'s work, committed at `684502ab`.** Four stale-claim sites repaired
  plus a fifth found by grepping the claim family: the door's dead
  `SPINE = Path(os.environ["SPINE_FILE"]).resolve()` citation in
  `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py` (current truth is
  `mcp_spine_server._spine_from_env`); `tc10`'s two files
  (`tests/test_explorer_templates.py`, `tests/test_mcp_door_engine_cwd.py`); and
  `scripts/init_work_area.py`'s `instantiate_spine` docstring. All prose, no
  executable line moved, suite unchanged at 3192/5/0.
- **`REPLAN_INPUT.json` verifies** — `g3` folded in as a completed outcome, open
  set empty, 23 wave-evidence rows, `D0`–`D28`, nothing auto-filed.

## What remains

1. **`reconcile`** — `start`, then `advance`. `c1` is already attested.
2. **`triage`** — `tc1`–`tc12` plus what the `g3` crews raised. Under
   `ADMIRAL_RULING-4`, **`tc1` (the SessionStart scan-bind) and the cross-session
   widening (B7) go to #610's wave as ONE package**, carrying the *question* —
   what the scan-bind is for when nobody has claimed the spine — not just the
   symptom. **Route by content, never by id:** `execute.json`'s `tc1` is the empty
   `map/ids.jsonl`, while the launch order's `tc1` is the scan-bind. Two different
   findings, one name — that is `tc7`'s id collision reaching the closeout.
   Satisfy `c2` in delegated mode with
   `attach triage --type user-decision --field cite='LAUNCH_ORDER:Inherited Latitude'`.
3. **`review`** — satisfy `c1` with
   `attach review --type user-decision --field cite='LAUNCH_ORDER:Return Shape'`.
4. **`feedback`** — episodes via `scripts/apply_episode_delta.py --store-root
   episodes`, proved by `verify_episode_captured.py`. The material is in leg 5's
   result artifact under "Feedback material".
5. **`archive`** — park. **Do not merge.**

## The one thing the next leg must take up, not decide alone

**`archive.c2b` requires an OPEN or MERGED PR and there is none.** This branch has
no upstream configured. Opening a PR is outward publication, which
`LAUNCH_ORDER-5` reserves to the Admiral ("Publication is mine"). Leg 5 did not
push and did not open one. Either the Admiral authorizes the push and PR, or
`c2b` is waived with the fence as the recorded reason. **Do not open a PR on your
own authority to satisfy a postcondition.**

## Hazards that cost this lane measurable time

- **The context governor ends a leg roughly every gate.** Defaults are soft 0.08 /
  hard 0.15, and `start`/`reopen` are hard-guarded. Leg 4 was refused at 0.19, leg
  5 at 0.155. Do the *substance* of the gate you cannot start — `attest` is not
  guarded — so your successor's first three commands close it. That is `D27`.
- **The containment test measures its observer.** `test_containment_repo_agent_work_untouched_by_the_chain`
  snapshots the live `.agent-work/` by size and mtime, and **every tool call fires
  the gauge chain**, which writes `gauge.json` under it. Leg 5 polled its own
  suite run ~15 times and got a false red; the identical command run quiet by the
  engine was green. **Run the suite and stay silent while it runs.** That is
  `tc11`/`D23`.
- **`CREW_SCRATCH_DIR`.** The engine's own gate-close suite command scrubs
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` but **not** this, and a Commander is
  itself launched through `run_crew.py`. Always
  `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py …`. That is `tc12`.
- **The registry clobber (#617, folded into #574).** Git is the only durable store:
  **commit `crew-runs.json` as each gate closes**, and on resume check the working
  copy against `HEAD` before trusting `recover_crews.py`.
- **Baseline clones must be named `constellation-skills`** —
  `MapTreeFreshnessTests` derives `map/INDEX.md`'s title from the checkout
  directory name, so a clone anywhere else reports a false red.
- **`run_crew.py` records a `partial` result as `failed`.** Leg 4 and leg 5 both
  parked correctly at clean boundaries; the registry calls both failures. The
  Admiral has taken that as its own defect (`D22`).
- **Nine crews on this gate refused the `SPINE MID-FLIGHT` nudge** and recorded the
  refusal. None wrote to this spine. The mechanism is the scan-bind `tc1`.

_Updated: 2026-08-17T02:35:00+00:00 (leg 5, parking at the reconcile boundary)_
