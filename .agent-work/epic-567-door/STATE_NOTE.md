# Crash-resume state note — epic-567-door

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** closeout · **in-progress.** Admiral spine `.agent-work/epic-567-door/spine.json`, **lease active** through the door. Only **c5 — human acceptance** is unmet; c1–c4 are satisfied and re-measured this pass.
- **slug:** epic-567-door · main checkout `/home/tommy/projects/constellation-skills` · `origin/main` @ **`519226cc`** · last gated tree **`c30ef5ae`**, GREEN 3431 passed / 0 failed. All 12 lanes merged; lane M closed unsent; every 567 branch merged (`git branch --no-merged main` empty for all of them); only `main` in `git worktree list`.
- **next command:** present `EPIC_SUMMARY.md` and get the human's acceptance, then `spine_evidence(action="attach", task_id="closeout", evidence_type="acceptance", ...)` for c5, close **#567**, `spine_advance("closeout", why=...)`, and **`spine_lease(action="release")` as the very last action**. Release-is-last: the lease must cover every journaled action.
- **pid:** none. No crew live. Nothing detached.
- **expected artifact:** the human's acceptance, then a terminal spine and a released lease.

_Updated: 2026-08-18 — closeout, third pass. Episodes: **34** for this run (`epic-567-door-001`…`-034`), capture gate exit 0; the 9 newest cover the cleanup wave. Reconcile: evidenced honest null, unchanged (no packet map, 0 of 167,950 statements anchored). Feedback sweep run over the three dogfood roots — on this host they are under `/home/tommy/projects/`, not the Windows paths in `docs/DEBT_SWEEP_CADENCE.md`; 5 candidates marked at `.agent-work/debt-sweeps/2026-08-18.md`, none filed. ADMIRAL_LOG archived to `.agent-work/archive/2026-08-18-epic-567-door/`. Standing hazards: unset `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`/`CREW_SCRATCH_DIR` before any suite run; the installer rewrites tracked `.mcp.json` on a self-install — revert it._
