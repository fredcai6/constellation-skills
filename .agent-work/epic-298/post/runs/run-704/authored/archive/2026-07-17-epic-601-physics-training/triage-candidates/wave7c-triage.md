# Triage candidates — Wave 7C (base topology)

## 1. Shallow-clone "disjoint lineage" illusion (file as issue)
`C:/Programs/f1Brainz/.git` was a **shallow clone** (`git rev-parse --is-shallow-repository` → true), which made `git merge-base main origin/main` return empty and presented `origin/main` as an *unrelated 2-commit lineage* missing the physics stack. It is not — `origin/main` is a strict fast-forward superset of local `main`. The tell: the grafted orphan root (#619 `a10912cc`) had a 4905-file / 10.2M-insertion / 0-deletion diff (whole-repo dump = graft signature). Fix applied: `git fetch --unshallow origin` (additive, no ref/tree touched; now in effect for the shared `.git` and all worktrees).
**Recommendation:** file an issue — "shallow clones produce spurious disjoint-lineage diagnoses"; consider a repo-setup note or a guard in fleet/worktree tooling that checks `is-shallow-repository` before any merge-base-based topology reasoning. This cost a full round of (wrong) Admiral analysis.

## 2. Stale feature branches on origin (branch-hygiene pass, non-blocking)
- `origin/feat/604-race-week-build` (tip `244b05d3`): 1 commit beyond origin/main, title duplicates origin/main's own `919f1347` (#604)(#613) — looks like pre-merge residue, safe to delete after confirming.
- `origin/feat/602-mission-consolidation`: 1 commit beyond merge-base, appears superseded by origin/main's `61f1e475` (#602)(#611).
**Recommendation:** branch-hygiene cleanup pass; verify-then-delete. Not fix-now.

## 3. Two pre-existing benchmark/perf test failures on origin/main
`tests/benchmark/test_physics_performance.py` showed 2 failures (FF) at the top of a full-suite run on the (== origin/main) tree. Not introduced by this epic. **Recommendation:** confirm whether these are environment/timing-sensitive benchmark flakes or real; if flaky, mark/xfail; track separately.
