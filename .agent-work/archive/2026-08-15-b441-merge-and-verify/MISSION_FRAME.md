# Mission Frame

Shrunk per template guidance ("skip or shrink ... for a trivial local/mechanical change where
the map adds nothing"). This repo has no `docs/architecture` packet map (confirmed DEGRADED-UNPARSEABLE
by `map_orient.py orient` at the context step — `map/INDEX.md` is a generated code index with no
citable anchor ids), so there is no map inventory for a `decision:`/`struct:`/`claim:` anchor id to
resolve against. This frame is therefore cited from the DEGRADED substitutes the context step
hash-pinned — `README.md`, `map/INDEX.md`, `scripts/checklist_engine.py` — rather than from
map-anchor ids, and uses plain labels (never the `word:id` anchor syntax) for the same reason.

## Intent
Bring PR #589 (`epic-568/441-binding-store`) current against `origin/main` (which now carries
#587 and #588) and re-verify with a clean-env full suite, so the PR's green is evidence against
the real merge base rather than a superseded one. Resolve the one expected merge conflict
(`map/INDEX.md`) by regeneration, not hand-merge. Distinguish and report which of three named
outcomes applies to the interaction between #588's new `origin_worktree_refusal` guard in
`scripts/checklist_engine.py` and #441's binding-store tests that spawn claim writers out of a
pytest tempdir (nothing breaks / fixture is dishonest and gets `git init`-ed / genuine collision
reported, not resolved).

## Affected Capabilities
- The `epic-568/441-binding-store` transactional binding store (#441), already implemented and
  reviewed — content is frozen (LAUNCH_ORDER Pre-Ruling 3, "content-is-final").
- `scripts/checklist_engine.py`'s `origin_worktree_refusal` fail-closed guard (#588) — merged,
  not owned by this run (LAUNCH_ORDER Pre-Ruling 1, File Ownership).
- `scripts/run_crew.py`'s archive-verdict rescue / `verdict_source` / `door_bound` (#587) — merged,
  not owned by this run.
- `map/INDEX.md` generated code map — owned by this run, by regeneration only.

## Structural Anchors
- `scripts/checklist_engine.py:102` — `origin_worktree_refusal(spine, *, cwd, verb)`, confirmed
  present in `origin/main` at the context step.
- `scripts/checklist_engine.py:3433-3441` — call site resolving `git rev-parse --show-toplevel`
  from cwd before invoking the guard.
- Binding-store test(s) spawning claim writers from a pytest tempdir (site named in LAUNCH_ORDER:
  `test_spawn_binding_transaction*`) — the concrete case this run must classify.

## Governing Constraints / Assumptions
- The guard in `scripts/checklist_engine.py` is untouchable this run: fix a dishonest fixture,
  never the guard (LAUNCH_ORDER Pre-Ruling 1, "guard-is-untouchable").
- `map/INDEX.md` is generated; resolve its merge conflict by regeneration, never hand-merge
  (LAUNCH_ORDER Pre-Ruling 2, "regenerate-dont-handmerge").
- #441's binding-store design (transaction, lock, reap policy, identity rules) is not to be
  revisited (LAUNCH_ORDER Pre-Ruling 3, "content-is-final").
- A genuine guard/binding-store collision is reported, not resolved (LAUNCH_ORDER Pre-Ruling 4,
  "outcome-3-is-a-finding").
- No crew dispatch this run — everything is done directly, in this turn (LAUNCH_ORDER "Do not park").

## Rulings Already In Force (from LAUNCH_ORDER.md, cited by section, not map anchors)
- guard-is-untouchable — `scripts/checklist_engine.py` is merged and not this run's to change.
- regenerate-dont-handmerge — `map/INDEX.md` conflicts are resolved by rebuilding, never editing hunks.
- content-is-final — #441's binding-store implementation, transaction design, lock, reap
  policy, and identity rules are not revisited this run.
- outcome-3-is-a-finding — a genuine guard/binding-store collision is stopped-and-reported, not fixed.

No new decision pressure: the launch order pre-settles every choice this run could force; the
only open question is a fact-finding one (which of the three named outcomes obtains), not a design
choice.

## Verification Targets (what each gate re-confirms)
- merge-clean — `git merge origin/main` conflicts in exactly `map/INDEX.md`; checked by
  `git merge-tree --write-tree --name-only origin/main HEAD` (already reproduced at understand: confirms
  single conflict).
- map-regenerates-green — `tests/test_code_map.py` passes after `python -m scripts.code_map
  build --root .`.
- suite-green — clean-env (`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`), cache-cleaned
  full `pytest -q` run reports `0 failed`.
- pr-mergeable — `gh pr view 589 --json mergeable` no longer reports `CONFLICTING` after push.

## Map Confidence / Staleness / Disputes
No packet map exists for this repo (DEGRADED-UNPARSEABLE, discharged at context with substitutes
`README.md`, `map/INDEX.md`, `scripts/checklist_engine.py`). This does not alter the plan: the
launch order already names the exact files, commands, and stop conditions, so no scout/verification
gate is needed to compensate for the missing packet map.

## Out of Scope
- Any edit to `scripts/checklist_engine.py`, `scripts/run_crew.py`, `tests/test_spine_origin_isolation.py`,
  `tests/test_explorer_templates.py`, `tests/test_mcp_identity.py`, `.mcp.json`, or any `episodes/`
  file not authored in this lane (LAUNCH_ORDER File Ownership).
- Revisiting #441's binding-store design.
- Merging PR #589 — fenced to the Admiral (LAUNCH_ORDER, final line).
- Dispatching a crew.
