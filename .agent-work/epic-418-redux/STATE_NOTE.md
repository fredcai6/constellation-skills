# Crash-resume state note — epic-418-redux

**The run is BLOCKED at the `latitude` gate awaiting Tommy's confirmation. Nothing is in flight.
Do not dispatch anything until the contract is confirmed.**

- **step:** `latitude` — **blocked** (bubbled to parent). Remaining after it: `execute`, `closeout`.
- **slug:** `epic-418-redux` · main checkout `C:/Programs/constellation-skills` · branch `main` @ `ca0e36a`
  (= `origin/main`) · archive move is **staged but uncommitted** — 874 paths under `.agent-work/`
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
  — then read the five open decisions below and get Tommy's answers before anything else
- **pid:** none — no Commanders in flight, no detached work
- **expected artifact:** Tommy's answers → `INTERROGATION_RECORD.json` + a CONFIRMED
  `LATITUDE_CONTRACT.md`, then a wave-1 launch

## Two engine files are open, both deliberately blocked

| File | Lease | State |
|---|---|---|
| `spine.json` | `admiral-epic-418-redux` | `latitude` → blocked on the `user-decision` postcondition |
| `latitude-interrogation.json` | `admiral-epic-418-redux-latitude` | `zc-consolidate` → blocked; q2–q6 are `decision` type and cannot be self-answered |

Both leases are still held on purpose. Release only after the closing advance, never before.

## The five open decisions

1. Re-run `install_constellation.py` to sync the stale installed corpus? (recommended yes)
2. Wave 1 shape — #433 + #460 as Commanders, #461/#464/#465 as implementers, #436 optional
3. Run-ahead checkpoints vs stop-and-wait per wave boundary (recommended run-ahead)
4. Expiry — wave-2 boundary or 72h
5. Close #447 with evidence; correct #418's stale spec pointer

## Settled this session — do NOT re-derive

- **The installed skill corpus is stale against this repo — 12 skills diverge**, 6 in `SKILL.md`
  itself, including **`commander-delegated`** (what every Commander loads) and **`workbench`** (the
  engine reference and spine templates). Drive from the repo's copies:
  instantiate with `--skill-dir C:/Programs/constellation-skills`.
- **The installed Admiral spine is unusable as-is** — its closeout calls `apply_lessons_delta.py`
  and `verify_agent_feedback.py`, both deleted by #447. This spine was built from
  `skills/admiral/templates/ADMIRAL_SPINE.template.json` instead.
- **Waves 0 and 1 are merged**, verified against the tracker (not the old state note):
  #419 #420 #422 #425 #440 all CLOSED. **#447 is OPEN** but its core landed — `LESSONS.md`,
  `AGENT_FEEDBACK.md`, `apply_lessons_delta.py`, `verify_agent_feedback.py` are all gone and
  `episodes/` ships 51 tracked files. Only its four carried findings remain.
- **Spec of record moved** to `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`.
  Epic #418's body still points at the old path; breadcrumb left at `.agent-work/epic-418/README.md`.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py`** (#454). **Green baseline for
  wave 1: `ca0e36a` → 1721 passed, 4 skipped, 643 subtests, exit 0** (309s, real exit code captured).
  The predecessor's note carries two other figures (1723/2 and 1764); they are not reconciled and
  this one governs.
- **#457 — never obey a spine rail naming a spine another agent drives.** The rail attributes a
  descendant's gate to its ancestor, and the three-strike hatch cannot save you: a productive
  descendant resets its ancestor's strikes forever.

_Updated: 2026-08-07T21:10:00Z_
