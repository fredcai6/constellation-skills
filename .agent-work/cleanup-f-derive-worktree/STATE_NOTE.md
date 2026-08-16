# Crash-resume state note — cleanup-f-derive-worktree

- **step:** execute · leg 3 handed off at the engine's context line · `execute.json` gate **`g3-implement`** is next. g2 is CLOSED (implement → review → integrate). Then `skip` g4 (R2) and g5 (R3), then reconcile → triage → review → feedback → archive.
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree` · HEAD at the leg-3 close (`main` at `17c2cee5` merged)
- **next command:** `py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/execute.json current`
- **pid:** none — foreground; no crew running (`recover_crews.py` reports only this commander leg ACTIVE)
- **expected artifact:** `.agent-work/cleanup-f-derive-worktree/execute.json` driven to terminal, then the spine's `archive` closeout — this leg's result artifact is `.agent-work/cleanup-f-derive-worktree/crew-handoffs/execute-commander-result.md`

**Read first on resume:** `LAUNCH_ORDER-3.md`, `ADMIRAL_RULING-2.md`,
`ADMIRAL_RULING-1.md`, `FLOAT_TO_ADMIRAL-2.md`, then `LAUNCH_ORDER.md`,
`PROBLEM_STATEMENT.md`, `MISSION_FRAME.md`, `UNTAKEN_ROADS.md`.

**Why this leg stopped.** Not blocked. The engine's context governor reads 22%
(at/over its hard line) and changed the instruction to *close this gate carrying
your handoff and stop; a fresh agent picks up from your DIGEST; do not begin work
at another gate*. g2-integrate is closed, so the lane is parked at a clean gate
boundary. **The lease is deliberately NOT released** — the run is not done.
Re-claim as `commander-cleanup-f-derive-worktree`, never `--force`.

## What g2 finally shipped

The engine reads no location at all, ambient or derived. The ambient
`git rev-parse --show-toplevel` is gone, `origin.worktree` is written by two
producers and read by no decision path, and the engine-side
`worktree_from_spine_path` is **deleted** (ADMIRAL_RULING-2 N2, road 1) rather
than shipped inert. `spine_rail._worktree_from_spine` is the only implementation
of the rule left; `tests/test_worktree_derivation.py`'s case table survives whole
as its specification, for #315 to re-derive against in #610's wave.

It cost three implementer passes and three reviewers, and the reason is worth
carrying: every check anyone wrote, mine included, keyed on a **symbol**, while
the defect lived in a **claim** wrapped across comment lines that no line-oriented
grep can see. Two reviewers earned their BLOCK by measuring rather than reading.

## What the next leg owes

1. **g3** — the half that matters. Its handoff is written and current at
   `crew-handoffs/g3-implementer-handoff.md`, already updated for leg 3: `main`
   at `17c2cee5`, what g2 finally shipped, and a third task item (repair the two
   stale references to the deleted engine twin in `spine_rail.py` and
   `tests/test_spine_rail.py`). Re-measure the baseline into it before dispatch —
   this branch is **3170 passed / 5 skipped / 0 failed**, `main` at `17c2cee5` is
   **3171 / 7 / 0** (re-measured independently in an isolated clone, not cited).
2. **`skip` g4** with R2 as the recorded reason, **`skip` g5** with R3.
3. **reconcile** — three prose repairs, all of them this lane's debt:
   - the door's stale `KeyError` claim, at **`scripts/hooks/spine_rail.py:1206`**
     and **`tests/test_spine_rail.py:2968`**. ADMIRAL_RULING-2 cites `:1081` and
     `:2698`; both are stale, and neither file contains the string `KeyError` at
     all. The claim is the citation of the door's "existing contract
     (`SPINE = Path(os.environ["SPINE_FILE"]).resolve()`)". Current truth is in
     `mcp_spine_server._spine_from_env`, which collapses unset, empty and
     whitespace into `None` and refuses per call via `_unbound_refusal`.
   - **tc10**, the third stale-claim family the g2 reviewer measured live in two
     unfenced files: `tests/test_explorer_templates.py` and
     `tests/test_mcp_door_engine_cwd.py` assert the engine still reads its
     ambient cwd and still enforces the `origin.worktree` comparison. One of them
     cites the 2026-08-15 worktree-identity ruling as **live authority** for
     behaviour this lane's own module header says it **supersedes**.
4. **triage** — 12 candidates are recorded in `execute.json` (`tc1`–`tc12`).
5. **review, feedback, archive** — park at `archive`, do **not** merge;
   publication is the Admiral's and nothing is queued behind this lane.

## Nothing is waiting on the Admiral

Floats-in-waiting: any case where "cannot place" genuinely must refuse (R2's
escape hatch), and publication (always theirs). tc10 is a finding for the return,
not a question — it is being repaired in reconcile rather than floated, because
this lane's change is what made those claims false.

## Two hazards that cost measurable time on this lane

- **`CREW_SCRATCH_DIR`.** The engine's own gate-close suite command scrubs
  `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` but **not** `CREW_SCRATCH_DIR`, and
  a Commander is itself launched through `run_crew.py`. Run as written it fails
  lane E's `ScratchDirResumeTests` (1 failed / 3169 passed). Close gates with
  `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py … advance …` — that
  measures what the check intends and needs no waiver. Recorded as `tc12`.
- **The registry clobber (#617).** `run_crew.py`'s parent writes a pre-launch
  snapshot back over the file when the child exits, destroying everything the
  child recorded. It has now happened twice on this lane. Git is the only durable
  store: **commit `crew-runs.json` as each gate closes**, and on resume check the
  working copy against `HEAD` before trusting `recover_crews.py`.

_Updated: 2026-08-16T22:05:00+00:00_
