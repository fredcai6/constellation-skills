# Crash-resume state note — 567-j

- **step:** execute · gate g3-review (crew dispatched, waiting on REVIEW_RESULT); g1, g2 closed complete; g3-implement closed complete on attempt 2 (attempt 1 correctly stopped at a real scope gap -- 3 more pre-existing tests broke when resolve_model was wired into the shared choke point; Commander ruled to fix all three preserving intent, plus a --reason symmetry fix on the abandon-relaunch path -- both within file ownership, no float needed). REPLAN_INPUT.json written and verified (verify_iterative_role_artifacts.py commander exit 0).
- **slug:** 567-j, branch feat/567-j-launcher-declared-defaults, worktree /home/tommy/projects/constellation-skills/.worktrees/567-j-launcher-declared-defaults
- **next command:** poll `.agent-work/567-j/crew-handoffs/g3-reviewer-result.md` for existence (or `py .../recover_crews.py 567-j`); once present and APPROVE, verify yourself (grep for every `CrewSpec(` site, confirm resume_crew() untouched, re-run `py -m pytest tests/test_crew_launcher.py -q`), close g3-review then g3-integrate (waive c1 again for the same known pre-existing failure) via `checklist_engine.py --file .agent-work/567-j/execute.json` (`--session-id commander-567-j-execute`), then g4-verify (reasoning gate, no crew — dispatch one real no-`--model` crew and read its registry entry's model field; run full suite in a CLEAN DETACHED worktree of this branch, unset SPINE_FILE/SPINE_SESSION/SPINE_PARENT/CREW_SCRATCH_DIR).
- **pid:** see `.agent-work/567-j/crew-runs.json` last entry for g3-review's pid once the dispatch call (background task btckaewsz) lands it
- **expected artifact:** .agent-work/567-j/crew-handoffs/g3-reviewer-result.md

_Updated: 2026-08-18T05:59:32Z_
