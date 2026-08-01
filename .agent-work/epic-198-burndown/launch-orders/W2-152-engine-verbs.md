# Launch Order: `commander-verbs — #152`

Commanders start cold. Everything you need is pasted below.

## Mission
Add the sanctioned repair/ergonomics verbs the delegated tier needs for long runs. Deliverable: one green, reviewed PR. Three related engine-verb ergonomics, bundled (all `checklist_engine.py`).

**Issue #152 (verbatim):**
Two engine gaps, same shape — no sanctioned repair path for an in-progress/blocked gate:
1. **No unblock/resume after a resolved `block`.** A commander blocked plan/execute on a classifier veto; when the human resolved it out-of-band, the only path forward was skip-with-reason (OBE) — a `resume`/`unblock` verb would fit the delegate float-then-resume pattern the tier is built on.
2. **`amend` only touches PENDING gates**, so an in-progress gate whose own postcondition check *command text* is discovered wrong mid-flight (e.g. a path made stale by a legitimate relocation) has no lighter repair than `waive` — which is framed as accepting residual risk, not correcting an authoring mistake. Add a narrow "correct the check, not the condition" path.
Related (cross-project, story_time sweep, grounded): **refresh `last_heartbeat` on any successful mutating verb by the lease-holding session** so an actively-working session never goes stale; reserve explicit `heartbeat` for genuinely idle waits. Bundle here — all three are engine-verb ergonomics for long delegated runs.

## Prior-Wave Verdicts (pasted)
Your base `7be19cf` (current main) already includes wave-1 PR #199, which changed `checklist_engine.py`: `has_pending_refresh_request` gained an optional `why_ref` param; `_why_suffix` renders for surveys; the `advance --from-child` seam is dedup-idempotent; HARD callers key on the current-digest why-record. Your work (new verbs + amend fix + heartbeat-on-mutate) is in different code paths — do NOT alter those #199 behaviors; build alongside them and keep their tests green.

## Pre-Rulings (overridable with evidence)
- Name the unblock verb `resume` (fits the tier's float-then-resume language) unless an existing verb name collides — say so if you deviate.
- The amend "correct the check text" path must be narrow: it edits a postcondition's `check.command`/`check` text on an in-progress gate WITHOUT marking the condition satisfied (that stays `waive`'s job). Frame it as correcting an authoring mistake, distinct from accepting risk.
- Heartbeat-on-mutate: every successful mutating verb by the lease-holder refreshes `last_heartbeat`; explicit `heartbeat` stays for idle waits. Do not change the staleness threshold, only when it's refreshed.
- Add tests for all three: resume-after-resolved-block advances; amend-check-text on in-progress gate leaves the condition unsatisfied but fixes the command; a mutating verb refreshes the heartbeat.

## Honest-Null Clause
A measured negative is a complete deliverable. If any of the three is already covered by an existing verb, report that with the code path rather than adding a redundant one.

## Inherited Latitude
Choose verb shapes/names, implement, test, open the PR. FLOAT: any change to the lease/staleness model beyond heartbeat-refresh timing; any change to #199's behaviors; any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `scripts/checklist_engine.py` and `tests/test_checklist_engine.py`. Do NOT touch `scripts/spine_rail.py`, `scripts/init_work_area.py`, `scripts/run_skill_eval.py`, or `docs/CHECKLIST_SCHEMA.md` (if your new verbs need schema-doc updates, note it as a triage candidate for the Admiral — CHECKLIST_SCHEMA.md was just refreshed in #199 and is out of your fence this wave).

## Workspace
Absolute worktree: `C:/Programs/cs-wt-verbs` — branch `feat/engine-resume-verbs-152`, base `7be19cf` (current main), provisioned via `git worktree add -b feat/engine-resume-verbs-152 C:/Programs/cs-wt-verbs main`.
First step: run `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-verbs` — must exit 0; paste output into your report.
PR integration = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** (1) multiline `gh --body`/PR body → temp file + `gh pr create -F <file>`; heredoc and `@'...'@` both fail PS 5.1 `--body`. You are in the **Bash** tool (Git Bash) where `@'...'@` is NOT a commit construct — use a real heredoc or quoted `-m`. (2) Use `py`, not bare `python`. (3) Verify your worktree.
**Active lesson `test-harness-concurrency-failsafe`:** concurrent-file-I/O tests need try/except + stop-signal in `finally` + `daemon=True` threads.
**Engine invariants:** never hand-edit spine JSON; the engine owns it. The engine schema is documented in `docs/CHECKLIST_SCHEMA.md` (read it to learn the current verb set and state shape — but do not edit it). Run the existing engine suite before and after; all pre-existing tests stay green.

## Budget
- **Model tier (required):** opus. New engine verbs with state-transition correctness stakes.
- **Compute/time:** bounded; checkpoint and return if you near a session limit.

## Stop Conditions
Stop and return when: a verb needs a lease/staleness-model change beyond heartbeat timing; a gap is already covered; you'd have to touch #199's behaviors or CHECKLIST_SCHEMA.md; you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Write your report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-2/W2-152-REPORT.md` BEFORE going idle: verdict (per sub-fix), evidence (test names + green output, full suite green), PR URL, map impact, triage candidates (incl. the CHECKLIST_SCHEMA.md doc-update note for the new verbs), workflow feedback (stage the fenced trio, name its path), and your isolation-script output. Open the PR with `gh pr create -F <bodyfile>` targeting main; title `feat(engine): resume verb + amend check-text repair + heartbeat-on-mutate (#152)`. Post the verdict, then go idle.
