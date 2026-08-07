# Run retrospective — commander issue-102 (staged worktree-local for Admiral harvest)

Under epic #101. Per launch order File Ownership + Inherited Context, the durable AGENT_FEEDBACK entry
and lessons-delta are staged HERE (worktree-local), NOT written through to the main checkout's canonical
`.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` mid-epic. Admiral harvests at closeout. The spine feedback
postconditions (c1 verify_agent_feedback, c2 verify_lessons_applied) resolve to the shared/main-checkout
root via git-common-dir — writing there is exactly what the launch order forbids — so they are WAIVED
with that citation, and this file + lessons-delta.json are the durable record.

## How closely the run followed the skills/handoffs/engine
Closely. Full spine driven through the repo's own engine (`scripts/checklist_engine.py`) and the repo's
own commander templates (dogfooding per launch order). Every gate dispatched implementer+reviewer crew
via `run_crew.py --dispatch external` + synchronous Agent-tool subagent + `--verify-result`. All 7 gates
closed with integrated, independently-reproduced evidence; per-move before/after grep; suite green at
every boundary (442 → 444). 7 commits, one per gate.

## Where I improvised / worked around
- **Crew dispatch backend:** no headless `claude` CLI in this harness, and in the teammate context the
  Agent tool refused background dispatch — so crews ran as SYNCHRONOUS Agent-tool subagents via
  `--dispatch external`. This SUPERSEDES the "prefer background subagent dispatches" memory for this run
  (the harness forced synchronous). Worked cleanly.
- **Parent spine lease went stale** while I drove the child `execute.json` through the engine: the
  child's mutations heartbeat the CHILD lease, not the parent spine lease, so after the long execute
  phase the parent spine lease was stale and refused `advance`. A same-id `--force` re-claim fixed it
  (idempotent, free — as the doctrine says). Surfacing as a lesson candidate.
- **Moves 2 and 10 proved subsumed** (honest partials): move 2's generic engine-invocation clause rode
  into global-everyone WITH move 1's compliance boilerplate (same sentence); move 10's design-it-twice
  restatements were already reduced to pointers by prior #99. The honest-null clause was essential — both
  are complete deliverables reported with grep proof, not failures. Baseline reconcile predicted move 10;
  move 2 only became clear after move 1 landed.
- **Waived feedback c1/c2** as above (launch-order override of a shared-root write).

## What was ambiguous / missing / contradictory
- The git-common-dir "shared durable root" design (durable trio → one shared root) is in direct tension
  with the launch order's "stage worktree-local, don't write the main checkout mid-epic." I resolved it
  in favor of the binding launch order (waive + worktree-local stage). This tension should be settled at
  the epic/doctrine level — it will recur for every under-epic Commander.
- Pointer-path convention (cite installed `references/global-*.md`, never source `skills/_shared/…`) and
  "cite by slug not section-title when the moved phrase equals the heading" were rediscovered by crews;
  worth codifying in the "move doctrine into a bucket" handoff pattern.

## Harvested crew workflow feedback (per gN-integrate)
- Handoffs consistently rated precise/complete; the drift-robust FIRST-STEP grep + explicit carrier list
  (g1) and the per-bucket destination + SKILL.md-only residual scoping (g7) were called out as exactly
  what avoided false-pass/false-fail traps.
- Asks: state the case-INSENSITIVE grep (commander's boilerplate was "This is mandatory…", capital T, so
  exact-case caught 9/10); prefix installer/source paths with `scripts/`; a per-move handoff/survey
  template with per-move check slots (reviewers split `r4-quality` into per-move checks by hand).
- Engine ergonomics (cosmetic): `current` rejects `--session-id` while mutating verbs require it;
  reviewer `consolidate` takes `--verdict/--summary` and must run before `release`; `config_ref`
  `docs/agents/engine-config.json` is absent in this skill-source repo (tolerated, benign).
- g7 implementer: the full gated-engine flow is disproportionate for a 2-test mechanical addition —
  front-loaded source-grep verification of the real risk surface instead (reported as misfit, compliant).

## What went well
- The cold plan critic (bias-to-yes even on a "mechanical" cluster) returned 3 HIGH findings that
  materially hardened the plan BEFORE execution: word-count evidence was missing from execute.json; the
  residual test scope would have false-failed on retained role references; the integrate command only
  ran one test file, not the 444-test suite. High ROI.
- g7 reviewer EXECUTED both falsifications (content-pin reds on a dropped bucket line; residual reds on a
  reinserted banner) rather than reasoning — the T5 detector/fix-same-author guard actually exercised.
