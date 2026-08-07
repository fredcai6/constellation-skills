# State note — issue-716 (deliberate suspension after `plan`)

- **Step:** `plan` COMPLETE. `execute` is `pending` and was deliberately **not** entered — this was a
  planning-only engagement.
- **Slug:** issue-716 (no '/' in this work_id, deliberately: the run's own subject is slash-unsafe
  work_id handling, and the defects it plans to fix are still live).
- **Next command (for a resuming Commander):**
  `py C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-716/spine.json claim --session-id commander-issue-716 --claimed-by commander --worktree . --force --reason "resuming this run"`
  then `current`, then the `execute` step (ensure context headroom, reload the commander skill, rewrite
  this state note with a live PID before any detached dispatch).
- **PID:** none — no detached process was launched this engagement.
- **Expected artifacts (all present):**
  - `.agent-work/issue-716/spine.json` — init/context/understand/plan complete
  - `.agent-work/issue-716/interrogation.json` + `interrogation-record.json` (rail exit 0)
  - `.agent-work/issue-716/MISSION_FRAME.md`
  - `.agent-work/issue-716/PLAN_ALTERNATIVES.md` (candidates + critic findings F1-F6, binding on gates)
  - `.agent-work/issue-716/execute.json` — the frozen gate plan
  - `.agent-work/issue-716/evidence/` — repro + engine drivers + baseline runners

## What a resuming Commander must know

1. **The change is in another repo.** Every file lands in `C:\Programs\constellation-skills`. f1Brainz
   needs no source change; it only invokes the installed copies. No branch was created here (branch
   creation was refused by the harness in this non-interactive session, and with no commits planned it
   was not needed). The implementation branch belongs in constellation-skills, not in f1Brainz.
2. **Gate order is load-bearing, not stylistic.** G1 helper → G2 distribution → G3 adoption.
   `tests/test_install_constellation.py::test_bundled_scripts_carry_their_sibling_imports` compares
   sibling imports against the bundle, so any order that puts the first `from work_id import` before
   the distribution wiring plans a known-red boundary.
3. **One decision is open on purpose.** `g2-integrate` c3 (companion wiring vs hand-added bundle
   literals, and the guard-test edit it implies) was NOT self-decided — it edits an existing guard.
4. **Baselines, measured 2026-08-01:** constellation-skills full suite `1160 passed, 1 skipped, 45.5s`
   (green). Interpreter: `C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe` — the
   Bash-tool `py` is the codex runtime and has **no pytest**.
