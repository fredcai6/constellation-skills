# Staged agent feedback (fenced delegated run — harvest into the shared .agent-work/AGENT_FEEDBACK.md)

## 638-f12-stability-rework (2026-07-18)

**Run shape:** commander (delegated) · 10 spine steps + 6 execute gates closed · Sonnet/general crews (implementer, reviewer) + general subagents (cold critic, cartographer).

**Instruction adherence:** fully followed — drove the whole spine through the engine to a terminal archive; the two `user-decision`-heavy gates and the diagnosis reasoning-gate stayed in commander context; crews via `run_crew.py --backend external`.

**Friction / unclear:**
- Full-covariance GMM fits on ~300k rows are SLOW (~12 min per per-half pre-fit) and, under CPU contention with concurrent sibling ships, my foreground diagnostic runs auto-backgrounded at the 600s tool cap. I worked around it by launching to a file with `&` and polling the output + `kill -0 <pid>`. A reasoning-gate diagnosis genuinely needs these in commander context (not a crew), so the `admiral-owns-long-batch-compute` pattern (Admiral-detached) didn't cleanly apply for ~6–15 min diagnostic runs — but the contention was real.
- The `simplification_limits` invocation form differs from the handoff: I authored `py -m src.utils.simplification_limits <paths>` (positional) but the CLI requires `--paths`. The implementer caught it and used the correct form; I should have cited the `--paths` form (it's in CREW_CONTEXT).

**Crew-reported friction (harvested from gN-integrate Workflow Feedback):**
- g2 implementer: the handoff's verification command #3 (`simplification_limits <paths>` positional) was wrong — needs `--paths`; and flagged `docs/architecture/packets/physics.md:979` stale (`RADIUS_SCALE_M=50`) → became triage tc1 (fixed in reconcile).
- g2 reviewer: to prove the discriminating test can fail it perturbed a source file, then `git checkout -- <file>` to restore — but the change was UNCOMMITTED, so checkout reverted to HEAD and wiped the implementer's work; recovered via `git apply` of a captured diff. Real hazard for perturb-to-test on an uncommitted tree.

**What worked:**
- Diagnose-first (lesson `diagnose-first-decide-fix`) paid off exactly: the launch order's stated "leading hypothesis" was a circuit-conditional/hierarchical redesign, but G1 real-data evidence showed the true root cause was a raw-radius heavy-tailed continuum (fixed by a log-radius fit space) plus a composition-brittle relative support floor — circuit-conditional was never needed. Jumping straight to the assumed redesign would have wasted a crew cycle and a ~6-min real-data run.
- The cold plan critic's 3 BLOCKING findings all proved real and materially strengthened the run: (1) anti-seed-overfit → I pre-froze a second independent seed batch (base 137) and it passed 5/5; (2) `.pth` worktree trap → my import-file assertion caught it live when a diagnostic script under `.agent-work/` resolved `src` to the MAIN repo; (3) model-collapse guard → drove the physical-adequacy check on the k=4 centroids.
- Verify-side-effects: after the reviewer's git-checkout scare I ground-truthed the tree (numstat + fix markers + re-ran 23 tests) before advancing, rather than trusting the "restored" claim.

**Where I improvised / worked around (reported as compliance — misfit reporting is compliance):**
- Early on I swept stray python with `taskkill //IM python.exe` (broad) — which in a multi-ship session could have killed sibling ships' compute. I corrected to surgical `kill <pid>` and started checking `ps -W` timestamps/ownership before any sweep. Flagged as a lesson.
- The engine's execute.json was driven WITHOUT a session lease (no `--session-id`) since only the spine claimed one; mutating verbs worked fine. Matches doctrine (a lease-less checklist takes no session-id).

**Improvement signals:**
- A shared fleet convention for ship-tagged process names (or a `ps`-ownership check helper) would make orphan-sweeping safe under multi-ship contention; broad `taskkill //IM python.exe` is a footgun.
- The constellation reviewer skill's perturb-to-test guidance should say: on an UNCOMMITTED working tree, back up by file-copy and restore by copy — never `git checkout` (it reverts to HEAD and wipes uncommitted peer work). Exported to CONSTELLATION_FEEDBACK.
