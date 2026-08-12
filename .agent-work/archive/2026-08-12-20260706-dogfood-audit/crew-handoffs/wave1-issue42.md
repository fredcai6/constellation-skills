# Launch Order: wave1-42 — Land lessons-apply-or-defer (#42)

## Mission
Finish and prepare the in-flight `constellation/lessons-apply-or-defer` branch for merge. Task 7 (bundle verifier + spine postconditions + latitude decision class + install test) is COMPLETE but UNCOMMITTED in the working tree — exactly these five modified files: `scripts/install_constellation.py`, `skills/admiral/templates/ADMIRAL_SPINE.template.json`, `skills/admiral/templates/LATITUDE_CONTRACT.template.md`, `skills/commander/templates/COMMANDER_SPINE.template.json`, `tests/test_install_constellation.py`. Task 8 (template/doc reconcile) is UNSTARTED. Spec: `docs/superpowers/specs/2026-06-27-lessons-apply-or-defer-design.md` — read it first; it is the authority for Task 8.

Task 8 scope (from the audit, confirmed against the spec):
- `skills/workbench/templates/LESSONS.template.md` — document the apply/export/defer ops, `deferred`/`exported` statuses, `target` field, and apply-threshold state-marker fields (`apply-recurrences`, `apply-confirmed`); currently the template describes the OLD mechanism and contradicts the gate that will block a fresh install's `feedback` step.
- `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` — retire the Template Update Candidates table per the spec.
- `skills/workbench/templates/AGENT_FEEDBACK.template.md` — stop routing fixes "through the closeout Template Update Candidates table"; route per the new COMMANDER_SPINE feedback imperative.
- Any spec-mandated doc updates the diff reveals as missing (check the spec's task list for Task 8's exact contents).

## Prior-Wave Verdicts
None — wave 1.

## Pre-Rulings
- Commit Task 7 first as its own commit (message: `feat(lessons): bundle verify_lessons_applied and wire apply-or-defer gates` or per repo convention from `git log`), THEN do Task 8 as separate commit(s).
- Commit ONLY the five Task-7 files in the first commit; only Task-8 files after. Nothing under `.agent-work/`.
- Do NOT merge the branch or the PR — the #42 merge is a surfaced decision the human takes at the wave checkpoint. Open/refresh the PR and stop.

## Workspace — SPECIAL (PR-1)
You work in the MAIN checkout `C:/Programs/constellation-skills` on the EXISTING branch `constellation/lessons-apply-or-defer` — the uncommitted Task 7 work lives only there. Because you are deliberately in the shared checkout, SKIP the `verify_worktree_isolation.py --here` step and state why in your verdict. The Admiral also operates in this checkout but writes only under `.agent-work/` (gitignored). No other commander touches this checkout in wave 1. Do not switch branches. Use `.agent-work/issue-42/` for your spine/work area. NEVER touch `.agent-work/20260706-dogfood-audit/` (the Admiral's area).

## File Ownership
The five Task-7 files + the three Task-8 workbench templates + spec-mandated doc files. Fence: do not edit `scripts/checklist_engine.py` (#44 owns it this wave), `scripts/run_crew.py` (#46), charter/platform references (#49).

## Budget
Model tier: opus-class. One implementer pass + one fresh-context reviewer subagent before the PR.

## Stop Conditions
Stop and query the Admiral (SendMessage to "main") if: the spec's Task 8 definition materially exceeds the three templates above; tests fail for reasons unrelated to the branch; you'd need to modify fenced files.
