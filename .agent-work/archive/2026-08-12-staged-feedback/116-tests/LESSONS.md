# Lessons Playbook

<!-- playbook-state: run-tick=1 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=116-tests -->

Open problems carried forward — NOT a log of everything learned. If a lesson is
understood and fixable, apply the fix and record it in AGENT_FEEDBACK; do not
bank it here. A lesson lives here only because it needs to be re-observed to be
understood, so every `add` states a bank-reason (what re-observation will
clarify). Reaching the cap is a failure mode — it means the bank is being used
to accumulate instead of to adjudicate. Read the Active section at the Commander
context step. Never edit by hand or by LLM: apply structured deltas via
apply_lessons_delta.py, which enforces cap, grounding, and counter rules.

Counter semantics split by scope: for most scopes a confirm is trust
(the lesson held again). For a constellation-scoped lesson it is the
opposite — a recurrence of an unfixed shared-machinery defect, so it
accrues recurrences (debt) and flags recurrence-debt. Pay the debt by
exporting to CONSTELLATION_FEEDBACK and fixing upstream. Once the fix
ships, `resolve` the lesson (cite the shipping PR): it goes terminal
(fixed-upstream) — never ripe again, a later confirm is ignored rather
than re-exported, and it ages out of the playbook on its own. Do not keep
confirming a constellation defect into a permanent workaround.

## Active

### lesson:stale-installed-corpus-sibling-import-drift
- scope: constellation
- task-class: dogfood-tooling
- statement: When a Commander invokes an installed skill's bundled script by absolute installed path (per doctrine), a sibling module it imports (e.g. `agent_work_root.durable_root`) resolves from the INSTALLED corpus directory, not the repo being worked on -- so if the user's global install lags behind the repo's own `main` (as happened here: the installed `constellation-commander/scripts/agent_work_root.py` was missing the #118 epic-lease-fencing fix that this repo's `scripts/agent_work_root.py` already has), a repo-aware check like `verify_agent_feedback.py`'s durable-root resolution silently regresses to pre-fix behavior. Confirmed by diffing the installed vs. repo copies of `agent_work_root.py` (12+ lines of missing epic-fencing logic) while `verify_agent_feedback.py` itself was byte-identical between the two. Worked around per-call with an explicit `--root .` (the script's own documented override), not by editing the installed corpus.
- grounding: 116-tests feedback step: verify_agent_feedback.py 116-tests --phase feedback failed citing the MAIN checkout path despite an active admiral-burndown-198 epic lease that should have fenced durable_root() to worktree-local; diff of installed vs repo agent_work_root.py confirmed the installed copy predates PR #118's epic-lease-fencing addition.
- bank-reason: Single instance observed so far, and confounded with this session's specific install being behind main -- a second Commander run in this session (or a future one) hitting the same installed-vs-repo sibling-import drift on a DIFFERENT bundled repo-aware script would confirm this as a structural corpus-freshness risk (bundled scripts assuming their sibling imports match the dogfooded repo's HEAD) rather than a one-off stale local install that a corpus refresh alone resolves.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-19 (116-tests)
- last-confirmed: none
- runs-since-confirmed: 0
