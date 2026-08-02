# AGENT_FEEDBACK

## 2026-07-18 — 627-unified-basis (Commander ShipF-627, delegated under Admiral epic #601; issue #627+#506 Phase 3)

Staged (fenced run: sole durable writers are the verdict in main + this worktree `.agent-work`; the Admiral
harvests this trio into the shared root). Honest retrospective on how the run actually went.

**What went well:**
- The spine drove cleanly init→context→understand→plan→execute(6 gates)→reconcile→triage→review→feedback→archive; engine mechanics (attest preconditions before start, attach-by-reference for APPROVE at integrate, waive-with-authority) worked as documented.
- The single cold plan critic earned its keep pre-freeze: caught the fused-CdA tautology, the disjoint persisted-cov-vs-demo, and the naive-independent-fusion σ-understatement. Folding those into G3 produced a genuinely non-tautological, honest NON-DEFERRABLE deliverable (the fusion REFUSING RBR's z=6.80 pair on real data proves the falsifiability isn't cosmetic).
- Seam-grounding before handoffs (braking_view Jacobian, PowerDrag/Coast result fields) meant crews hit the right seams first time; verify-claimed-side-effects held throughout (re-ran every crew's tests, reproduced G3/G4 numbers myself).

**Friction / unclear:**
- **Foreground vs background waiting — the run's biggest friction.** I repeatedly armed fire-and-forget background watchdogs and yielded my turn to "wait" for the G4 rework / re-review / slow suite; the Admiral read this as IDLE and nudged 3 times. Correct for genuinely-long detached work, but for medium waits it stalls the run between steps and looks like a stall. → banked lesson `delegated-commander-foreground-poll-over-watcher-yield` (prefer bounded foreground in-turn polls; reserve detach+notify for >~10min jobs and verify-alive).
- **Slow physics suite under multi-agent contention.** `tests/unit/physics/layer2/ + weekend_state/` exceeded 20+ min under concurrent Ship agents (verified CPU-moving, not #644). The g4-integrate full-suite postcondition was impractical; I proved the 188 diff-affected tests green + the pure-extraction rationale and WAIVED c1 with Admiral authority. Felt right but leaned on the Admiral's pre-authorization rather than a first-class plan option.
- **Resume-time subagent cwd leak.** On SendMessage-resume, crew transcripts showed `cwd C:\Programs\f1Brainz` / `gitBranch main` (session default), NOT the worktree — a worktree-isolation hazard on resume specifically; the crews' `__file__` assertion saved it, and main stayed clean.

**Crew-reported friction (harvested from gN-integrate Workflow Feedback sections):**
- G1: fallback validation (algebraic vs live perturbation) pre-sanctioned + adequate; flagged tc1 (3 back-solved constants lack a closed-form check) to gate G4's trust in the split.
- G2: honest NULL-backfill finding (SQLite bare ADD COLUMN backfills legacy rows NULL, not the dataclass default); a reviewer `git stash` phrase inside an engine `--finding` string got backtick-expanded and briefly re-stashed the diff (self-corrected) — hazard: no literal git-command text in engine `--finding`/`--reason` args.
- G3: found + fixed a real correctness issue (raw fit-only cov is non-PSD on real data → honest total σ); reviewer reproduced it against the real stored row.
- G4: the implementer never ran `simplification_limits` (not named in handoff or its IMPLEMENTER_PLAN final-verify) → estimate_store.py hit 1010>1000 and the reviewer BLOCK'd; a mechanical split cleared it.
- G5: reviewer verified the circuit-fixed-effect partial correlation is genuine and all 18 a_long numbers match the decision doc.

**Improvement signals:**
- Name `simplification_limits` as a standing crew final-verify postcondition for any gate touching src/tests (→ CONSTELLATION_FEEDBACK #1) — it is a CREW_CONTEXT-named mechanical blocker that fell through both the implementer self-check and would have fallen through review if not run independently.
- crew-dispatch.md should note a resumed subagent's cwd is the session root and the resume prompt must re-assert the worktree cwd + `__file__` check (→ CONSTELLATION_FEEDBACK #2).
- Consider a sanctioned "fast integrate gate = diff-affected tests + simplification; full suite = merge-gate" pattern for compute-heavy suites, so the Commander need not waive a mechanical postcondition under contention (→ CONSTELLATION_FEEDBACK #3). Recurrence-debt is growing (4 constellation lessons / 38 unfixed recurrences at run 26).
