# Wave 2 launch orders — epic 20260706-dogfood-audit

Dispatched 2026-07-06 after PR #57 merged (main e4c922d). #47 held until #44 merges (engine-writer seat). Common block identical to wave1-common.md with wave-2 issue ids; prior-wave verdict pasted below rides in every order.

## Pasted prior-wave verdict (wave1-42, merged as PR #57)
Task 7 + Task 8 are ON MAIN (e4c922d): `verify_lessons_applied.py` is bundled to admiral+commander with spine postconditions wired (commander `feedback` c2, admiral `closeout` c6); `LESSONS.template.md` now documents apply/export/defer ops, `deferred`/`exported` statuses, `target` field, and apply-threshold state-marker fields; `WORKFLOW_CLOSEOUT.template.md` and `AGENT_FEEDBACK.template.md` no longer reference the retired Template Update Candidates table. Suite 255 passed/1 skipped at merge.

## Per-issue missions (full text lives in the dispatch prompts)
- #43 (opus): add `verify_worktree_isolation.py` to admiral AND commander SKILL_SCRIPT_BUNDLES tuples in install_constellation.py + install test. Owns install_constellation.py + its tests only.
- #45 (sonnet): fix-or-remove dead `compact` spine step (8 recurrences). Context: this harness lacks /compact; skip-with-reason is the sanctioned path per global-everyone.md — if removing, update that doctrine line in the same PR (doctrine follows mechanism). Owns COMMANDER_SPINE.template.json + compact-related lines of commander SKILL.md + that doctrine line.
- #50 (sonnet): idle = check-artifacts doctrine. IMPORTANT: admiral-side doctrine partially EXISTS (admiral SKILL.md "An idle commander... is done, not stalled"; fleet-doctrine adjudication invariants; global-everyone idle-strands-the-gate). Audit first; implement only genuine gaps (commander-side crew-idle handling, LAUNCH_ORDER deliver-before-idle return contract); honest-null the rest per PR-5. Owns idle-related lines only; fence vs #45's compact lines in the same commander SKILL.md.
- #51 (sonnet): fold Match-the-Form-to-the-Failure ladder into apply-op guidance: 1 engine gate/script > 2 required template slot > 3 positive recipe > 4 prohibition+counter, with a one-line "could this be a gate?" test. Targets: lessons-auditor SKILL.md + freshly-landed LESSONS.template.md header (reconcile, don't clobber Task 8 text). Owns those two files.
