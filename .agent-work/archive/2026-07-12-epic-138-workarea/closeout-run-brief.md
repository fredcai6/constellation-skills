# Lessons-audit run brief — epic-138 (2026-07-12)

## Epic intent
Implement the #138 corpus-compliance counter-doctrine (confirmed spec at `.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`): clamps (#142/PR147), engine rail (#140/PR148), hook suite (#141/PR150), fencing-aware gates closing #134 (#143/PR149), warm register (#144/PR146), three measured arms (#145: corpus-only 2/3, +rail 3/3, +rail+hooks 3/3; human kill-ruling: KEEP, revisit at certification). All merged; main a9bb9b3; 648 tests green.

## Model tiers used
Admiral session: Fable (main loop). Commanders: opus (#140, #141, #143, #145), sonnet (#142, #144-implementer). Reviewers/critics: sonnet, except the three spec critics (pre-cap, inherited Fable — since ruled out: subagents capped at opus or lower, standing).

## Templates
No project TEMPLATES_MANIFEST customizations this run — stock admiral/explorer templates from the installed skills.

## Artifacts to audit
- `.agent-work/epic-138/ADMIRAL_LOG.md` — the full audit trail (waves, rulings, incidents incl. the Stop-hook misattribution → #151, the classifier escalation → human-in-loop remedy, session-limit fencing, harvest records)
- `.agent-work/AGENT_FEEDBACK.md` — 2026-07-12 entries for issue-140..145 (six commander closeouts incl. workflow-feedback sections)
- `.agent-work/epic-138/verdicts/commander-14{0..5}.md` — return reports with Workflow Feedback
- `.agent-work/LESSONS.md` — 8 active lessons (5 added this epic: implementer-skill-engine-ref-path-drift, headless-hook-probe-allowedtools, gate-script-fix-cannot-self-verify, engine-no-unblock-verb-after-resolved-block, auto-mode-classifier-blocks-delegate-eval-arms, eval-harness-bundles-engine-from-invoking-checkout, plus the two issue-142 spec-authoring/amend-gap lessons) — every active lesson must be ENDED by this audit: graduated to a named home + retired, or deleted with reason
- `.agent-work/CONSTELLATION_FEEDBACK.md` — exports incl. issue-143's and issue-145's
- Cross-project sweep (dogfood roots, entries marked collected 2026-07-12): read AGENT_FEEDBACK/CONSTELLATION_FEEDBACK under `C:/Programs/f1Brainz`, `C:/Programs/network_elo`, `C:/Programs/story_time`. Notable: story_time reports lease-staleness at execute→closeout; proposal = engine refreshes last_heartbeat on any successful mutating verb by the lease holder.

## Queued triage candidates (route, do not lose)
- corpus_id install-path pollution (breaks D6 same-corpus-hash certification accumulation — MUST precede any N≥8 run)
- engine unblock/resume verb after a resolved block (issue-145 skip-OBE workaround)
- stage_feedback.py helper to mechanize the staged trio (issue-143)
- rail note in docs/CHECKLIST_ENGINE_DESIGN.md (issue-140 tc1)
- heartbeat-refresh-on-mutating-verb (story_time sweep)
- Stop-hook misattribution already filed as #151 — confirm routed, do not re-file

## Standing constraints on dispositions
- Superpowers is a competitor: no imported doctrine, no citations.
- Consolidation yes, prevention machinery no (standing human stance).
- Apply lesson-inbox deltas ONLY via apply_lessons_delta.py (tick=true); graduations are paired edit+retire; JSON templates edited surgically, re-validated with json.load.
- Playbook deltas you apply directly; template/doctrine graduations beyond one-line insertions and ALL new issues: return as recommend-and-defer for the Admiral to route (you have no filing authority).
