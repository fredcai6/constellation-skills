# Mission Frame

No `docs/architecture` packet map exists in this repo (`map/ids.jsonl` builds to 0 ids; `map/INDEX.md`
is an unfilled landing-zone stub). Context oriented DEGRADED-UNPARSEABLE and discharged with substitutes:
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, `docs/CHECKLIST_SCHEMA.md`,
`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `tests/test_spine_origin_isolation.py`.
This frame is cut from those substitutes plus the authoritative ruling doc named by the launch order,
never from a map that does not exist.

## Intent

Reconcile three doctrine surfaces against what the engine actually does at `main` `0646d61b`, per launch
order `admiral-post-568`. Docs-only: no behavior change, no code edit. Fix `docs/CHECKLIST_SCHEMA.md`'s
stale worktree-isolation passage (superseded by PR #588); make a defended judgment call on whether
`skills/admiral/templates/LAUNCH_ORDER.template.md`'s mandated `verify_worktree_isolation.py --here`
check is redundant now or still earns its place; measure whether `skills/workbench/references/checklist-engine.md`
carries the isolation claim the launch order's third-surface premise assumes, and sweep `docs/` and
`skills/` for any other surface asserting containment / `Path.cwd()` / `verify_worktree_isolation.py`
as current engine behavior.

## Affected Capabilities

- Worktree-origin isolation doctrine as documented for humans/agents in `docs/CHECKLIST_SCHEMA.md`
  (the `origin` block section) — currently describes containment + `Path.cwd()`, which PR #588 replaced
  with git-toplevel resolution + equality.
- The Commander launch-order template's first-step isolation instruction in
  `skills/admiral/templates/LAUNCH_ORDER.template.md` (line ~43, evidence requirement line ~76) —
  mandates a per-template `command` check the schema doc says the engine now supersedes.
- The workbench engine reference `skills/workbench/references/checklist-engine.md`, named by the launch
  order as a possible (unconfirmed) third disagreeing surface.

## Structural Anchors (source, confirming — not building — the frame; no map to cite instead)

- `scripts/checklist_engine.py` — `origin_worktree_refusal` (~line 102-179): the pure predicate, now
  equality (`os.path.normcase` + `==`), not containment (`is_relative_to`).
- `scripts/checklist_engine.py` — `main()` call site (~line 3411-3444): the one impure half; resolves
  `engine_cwd` via `git rev-parse --show-toplevel` before handing it to the predicate; fails closed
  (`engine_cwd is None`) for an origin-carrying spine.
- `tests/test_spine_origin_isolation.py::test_it_is_pure` — the shipped purity invariant the predicate
  must uphold.
- `docs/CHECKLIST_SCHEMA.md` lines ~120-126 — the stale passage Task 1 corrects.
- `skills/admiral/templates/LAUNCH_ORDER.template.md` lines ~43, ~46-54, ~76 — Task 2's target and the
  still-accurate "isolation is git-only" / `CLAUDE_PROJECT_DIR` passages that must survive untouched.
- `skills/workbench/references/checklist-engine.md` — Task 3's target, premise to be re-measured.

## Governing Constraints / Assumptions

- Docs follow the engine, never the reverse (launch order Pre-Ruling 1, `engine-is-truth`) — this lane
  has no authority to change behavior in `scripts/checklist_engine.py`, `scripts/verify_worktree_isolation.py`,
  `scripts/hooks/spine_rail.py`, `scripts/mcp_spine_server.py`, or any test file, or in
  `scripts/run_crew.py` / `skills/commander/references/crew-dispatch.md` (owned by the concurrent
  `launcher-hygiene` lane).
- The unforgeability withdrawal ("does NOT make the comparison unforgeable... a check authored as
  `cd <origin.worktree> && ...` still satisfies it") stays exactly as strong as written — never upgraded
  (Pre-Ruling 2, `forgery-stays-named`).
- Task 2 is a defended judgment call, not a mechanical edit — pick (a) redundant-so-drop/demote or
  (b) distinct-so-explain-the-difference (Pre-Ruling 3, `judgment-on-task-2`).
- Task 3's premise may be wrong; report an honest null rather than manufacture an edit (Pre-Ruling 4,
  `honest-null`).
- Caches cleared before measuring; the full suite runs cache-clean, clean-env, non-backgrounded
  (Pre-Ruling 5, `clear-caches-before-measuring`, and the launch order's "Do not park" section).

## Decision Anchors & Decision Pressure

No new load-bearing decision is minted by this run — the launch order's five Pre-Rulings above are
already settled by the Admiral and are cited, not re-litigated. Decision pressure carried into Task 2:
whether the template's first-step check is redundant now the engine refuses every guarded verb natively,
or remains a distinct, valuable early human-readable signal — resolved within this run's latitude per
Pre-Ruling 3, and reported (not floated) since the launch order already grants the Commander authority
to make and defend that call.

## Claims / Evidence Surfaces

- The ruling doc `/home/tommy/projects/constellation-skills/.agent-work/rulings/2026-08-15-worktree-identity.md`
  (untracked, primary checkout) is the authority for current engine behavior; every rewritten passage
  must be checked against it and against the live code, not merely against the launch order's paraphrase.
- `docs/CHECKLIST_SCHEMA.md`, `scripts/checklist_engine.py`, `tests/test_spine_origin_isolation.py` are
  declared substitutes from the degraded context read; already read in full during `understand`.

## Map Confidence / Staleness / Disputes

No packet map exists for this repo; this is a structural absence, not a stale or low-confidence map area
to route around — hence the DEGRADED discharge above rather than a scout/verify gate. `map/ids.jsonl`
building to 0 ids is itself worth a Task-3-style honest note if it recurs, but is out of scope for this
docs-only lane.

## Out of Scope

- Any edit to `scripts/checklist_engine.py`, `scripts/verify_worktree_isolation.py`,
  `scripts/hooks/spine_rail.py`, `scripts/mcp_spine_server.py`, or test files.
- `scripts/run_crew.py`, `skills/commander/references/crew-dispatch.md`, `.worktrees/launcher-hygiene/`
  (owned by the concurrent `launcher-hygiene` lane).
- Building or repairing a `docs/architecture` packet map for this repo (a Task-3-adjacent finding, not
  this run's job).
- Any behavior change to worktree-identity comparison; this ruling is already shipped at `0646d61b`.
