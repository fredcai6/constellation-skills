# Crash-resume state note — cleanup-f-derive-worktree

- **step:** execute · **leg 5, the closeout** (`LAUNCH_ORDER-5.md`). All of this
  lane's code is written, reviewed and **approved**; nothing left should change an
  executable line outside the three prose repairs named below. `execute.json` gate
  **`g3-review`** is next and it is bookkeeping: `e-g3-review-2 (review-result,
  verdict=APPROVE, 0 findings)` is already attached, so `start g3-review` →
  `advance g3-review` → `advance g3-integrate`. Then `skip g4` (R2), `skip g5`
  (R3), then reconcile → triage → review → feedback → **archive (park, do not
  merge)**.
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` ·
  worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`
  · `g3`'s code is committed through **`539ff636`** · `main` at **`17c2cee5`**,
  unmoved.
- **next command:** `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/execute.json current`
- **pid:** none — foreground, no crew running and **none planned**. Leg 5 dispatches
  no implementer or reviewer; every g3 crew is COMPLETE and `recover_crews.py`
  reports only this commander leg (`attempt-5`) ACTIVE. Legs 1–4 show
  `NEEDS-ABANDON` — they are my own parked predecessors, not crews to recover.
- **expected artifact:** `.agent-work/cleanup-f-derive-worktree/execute.json` driven
  to terminal, then the spine driven through `archive`; this leg's result artifact
  is `.agent-work/cleanup-f-derive-worktree/crew-handoffs/execute-commander-result.md`.

**Read first on resume:** `LAUNCH_ORDER-5.md`, then `ADMIRAL_RULING-4.md` (the
boundary that closed `g3`), then `ADMIRAL_RULING-3.md`, `-2.md`, `-1.md` (R1/R2/R3
and N2 govern the skips and the reconcile list), then
`crew-handoffs/execute-commander-result.md` (leg 4's return — the source of most of
the `feedback`).

## Leg 4 parked; it did not fail

`run_crew.py` records `attempt-4 -> failed` because the result artifact's status is
`partial`. The status is correct and the launcher's reading of it is wrong — the
Admiral has taken that as its own defect to file. **`g3` review 5 returned APPROVE
with 0 findings** and that evidence is attached as `e-g3-review-2`.

Re-claim the lease as `commander-cleanup-f-derive-worktree`; **never `--force`**.
An owner is never blocked by its own stale heartbeat (cause named in
`ADMIRAL_RULING-3.md`). Leg 5 re-claimed cleanly with `claim --session-id
commander-cleanup-f-derive-worktree --claimed-by commander`.

## What g3 shipped (done, approved, do not reopen)

`_foreign_worktree` deleted with both call sites. `_entry_mid_flight_view` reads no
payload — mid-flight is a property of the spine. `_own_entries` is the shared
ownership comparison at both sites. `_attributed_to_another_key` guards the
bind-on-resume's **write and its render**: neither may contradict an attribution
`session_view_provenance` already holds. A path attributed to **nobody** behaves
exactly as before, so `tc1` is untouched. Five reviews, four reworks, every finding
measured rather than read; review 5 returned APPROVE / 0 findings / 8-of-8 criteria.

**Under `ADMIRAL_RULING-4`, review 5 was the last round on `g3`.** A finding that
measures identical on the pre-gate arm is a triage candidate for #610's wave, not a
reopen.

## What remains, in order

1. **`g3-review`** — start, advance (APPROVE attached), then **`g3-integrate`**.
2. **`skip g4`** with **R2** (an unowned spine path yields no derived worktree and
   today's behaviour, never a refusal — already shipped by g1;
   `_worktree_from_spine` returning `None` is the complete answer). **`skip g5`**
   with **R3** (#315 descoped, re-homes to #610's wave).
3. **`reconcile`** — three prose repairs, all this lane's own debt. **Cite by the
   string to grep for, never by line:**
   - the door's stale `SPINE = Path(os.environ["SPINE_FILE"]).resolve()` contract
     citation in `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`;
     current truth is `mcp_spine_server._spine_from_env`, which collapses unset,
     empty and whitespace into `None` and refuses per call via `_unbound_refusal`.
   - **tc10**: `tests/test_explorer_templates.py` and
     `tests/test_mcp_door_engine_cwd.py` still assert the engine reads its ambient
     cwd and enforces the `origin.worktree` comparison; g2 made both false, so this
     lane owns the repair (ADMIRAL_RULING-3). Where a repaired passage contradicts
     the 2026-08-15 worktree-identity ruling, **cite that ruling and say plainly
     that this lane supersedes it.**
4. **`triage`** — `tc1`–`tc12` plus what the g3 crews raised. Under
   `ADMIRAL_RULING-4`, **`tc1` and the cross-session widening (B7) go to #610's wave
   as one package**, carrying the *question* — what the scan-bind is for when nobody
   has claimed the spine — not just the symptom.
5. **`review`**, **`feedback`**, **`archive`**. Park at `archive`. **Do not merge.**

## Feedback material (the most valuable artifact this lane ships)

- **When a gate removes a guard, enumerate what the guard was incidentally
  preventing, not only what it was wrongly deciding.** Four of five g3 reviews trace
  to nobody doing this.
- **Build your own instrument before you run theirs.** Every instrument on this gate
  developed a shelf-life defect — a differential pinned to a moving `HEAD`, reviewer
  harnesses pinned to superseded commits showing fixed defects as live.
- **Cite content that cannot move under you.** Stale line numbers (the Admiral's,
  five times) and amended shas (leg 4's, once) are the same defect in two forms.
- **Measure the claim family, not the symbol.** g2 cost three implementer passes
  because every check keyed on a symbol while the defect lived in a claim wrapped
  across comment lines.

## Hazards that cost this lane measurable time

- **`CREW_SCRATCH_DIR`.** The engine's gate-close suite command scrubs
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` but **not** this, and a Commander is
  itself launched through `run_crew.py`. Always close gates with
  `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py … advance …`. That is
  `tc12`; the Admiral has taken it as an engine defect.
- **The registry clobber (#617, folded into #574).** `run_crew.py`'s parent writes a
  pre-launch snapshot back over `crew-runs.json` when the child exits. Git is the
  only durable store: **commit `crew-runs.json` as each gate closes**, and on resume
  check the working copy against `HEAD` before trusting `recover_crews.py`.
- **Baseline clones must be named `constellation-skills`.**
  `tests/test_code_map.py::MapTreeFreshnessTests` derives `map/INDEX.md`'s title from
  the checkout directory name, so a clone at any other path reports a false red.
- **Nine crews on this gate refused the `SPINE MID-FLIGHT` nudge** and recorded the
  refusal, exactly as instructed. None was penalised and **none wrote to this
  spine.** The mechanism is `tc1`.

_Updated: 2026-08-17T02:10:00+00:00 (leg 5, opening)_
