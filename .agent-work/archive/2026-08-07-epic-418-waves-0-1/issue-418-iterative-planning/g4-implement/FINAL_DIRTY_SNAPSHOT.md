# Gate 4 Final Dirty Snapshot

The inherited tracked and untracked paths listed in `INITIAL_DIRTY_SNAPSHOT.md` remain present with their original modified/deleted/untracked classifications. Gate 4 added only its two verifier scripts, two focused test modules, demo/run evidence, and the bounded removability-ledger home rename required by the full-suite coverage rail.

## Gate 4 product additions

- `scripts/verify_epic_418_demo.py`
- `scripts/verify_iterative_planning_acceptance.py`
- `tests/test_epic_418_demo.py`
- `tests/test_iterative_planning_acceptance.py`
- `docs/removability_ledger.json` and `docs/REMOVABILITY_LEDGER.md` updated so external `to-issues` maps to canonical home `to-initial-issues`

## Local evidence additions

- `.agent-work/issue-418-iterative-planning/demo-epic-418-iterative-planning/**`
- `.agent-work/issue-418-iterative-planning/g4-implement/**`
- `.agent-work/issue-418-g4-implement/**`

## Preservation result

- Frozen archive: 28/28 path+SHA entries identical before/after.
- Unrelated dirty work: preserved; no reset, checkout, overwrite, commit, push, PR, tracker write, or network write occurred.
- `git diff --check`: exit 0 (line-ending notices only).
