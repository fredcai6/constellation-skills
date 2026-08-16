# Triage Recommendation: `main`'s own `map/INDEX.md` is stale at current tip

## Classification
stale generated map

## Source checklist/artifact
- execute.json triage_candidates tc3 (flagged from g3-verify)
- `/tmp/g3-main-suite.log` (ephemeral; signature quoted below)

## Structural anchor
`map/INDEX.md` (repo root)

## Cartographer mismatch class
none

## Observations

### Observation 1
- **What's wrong:** `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build` fails on `main`'s own current tip with the signature "map/INDEX.md is stale: rerun `python -m scripts.code_map build --root .` and commit the result" — a fresh build reports 82 modules / 4678 entities against the committed 81 modules / 4665 entities.
- **Expected:** `main`'s committed `map/INDEX.md` matches a fresh build of `main`'s own tip (the whole point of the freshness test).
- **Conditions:** ran on a disposable `git worktree` checked out at `main`'s tip `43c577d4` (the commit this lane's branch would actually merge against), full clean-env suite. This lane's dispatch-time baseline (`a69bbac4`) is NOT affected — the staleness was introduced by commits that landed on `main` between dispatch and this lane's gate-time re-measurement (lane D's #602/#597/#598, per the epic's shared state note).
- **Type:** `measured` — ran `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q` in a disposable worktree at `main`@`43c577d4`; 1 failed, 3068 passed, 7 skipped. Pasted the full failure traceback into this lane's `g3-verify` gate evidence.
- **Rev:** `main`@`43c577d4`, as re-measured 2026-08-16 at this lane's `g3-verify` gate.

## Recommended priority
medium

**Reason:** this is the exact check every lane's own merge gate depends on (`map/INDEX.md is generated and freshness-tested`); if `main` itself carries a stale map, the NEXT lane to re-measure its own baseline against `main` will see this same pre-existing failure and may misattribute it to its own change unless it independently confirms (as this lane did) that the failure predates its branch.

## Related artifacts
- `.agent-work/epic-568-cleanup/STATE_NOTE.md` (the shared epic coordination note; lane D's #602/#597/#598 are the likely source)
- this lane's own analogous fix: commit `590bf44d`, `python -m scripts.code_map build --root .`

## Disposition
`recommend-and-defer`

**Detail:** this is on `main`, entirely outside this lane's file ownership (`scripts/run_crew.py`, `scripts/hooks/spine_rail.py` only) and outside its worktree; the fix is a one-line `python -m scripts.code_map build --root . && git add map/INDEX.md && git commit`, but it is not this lane's to run against `main` directly. Recommending the Admiral either run it or route it to whichever lane (D, or a merge-time step) is closest to `main`.

## Issue creation authority
`ask user`
