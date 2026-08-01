# Launch Order: `commander-cg-fastfollows — #189 #190 #191 #192`

Commanders start cold. Everything you need is pasted below; do not assume access to the Admiral's context.

## Mission
Land the four Context Governor v1 fast-follows from epic #178 as ONE bounded change (all four touch `scripts/checklist_engine.py` or the schema doc that describes it, so they share a worktree to avoid self-collision). Deliverable: one green, reviewed PR that fixes the three engine defects and refreshes the schema doc. This closes the last real work blocking epic #178 from being closed.

**The four issues (verbatim):**

**#189 — DIGEST/REFRESH REQUESTED display is gated-only (survey roles blind).** `_why_suffix` in `scripts/checklist_engine.py` returns `""` for any non-`gated` checklist `type`, so a `survey` checklist (driven by the reviewer and interrogator roles) shows neither the `DIGEST:` nor `REFRESH REQUESTED:` line on `current`, even with a `refresh-request` attached (verified: `current` is byte-identical before/after attaching one to a survey). This breaks the Context Governor reach-up cold-start (a fresh agent cold-starts from `current` alone, and the reach-up chain explicitly names the reviewer, a survey role). #183 shipped only a doctrine workaround (reviewer reads the survey JSON directly). **Fix:** extend `_why_suffix` (or the equivalent render path) to surface `DIGEST:`/`REFRESH REQUESTED:` for `survey` checklists too, so cold-start is uniform across gated and survey. Add survey-shaped tests.

**#190 — has_pending_refresh_request is why_ref-blind (HARD-band collision).** `has_pending_refresh_request(cl, gate)` in `scripts/checklist_engine.py` returns true if *any* non-superseded `refresh-request` with `payload.seam == gate` exists, without distinguishing which. If a second distinct trip lands on the same still-open gate before the first clears, the predicate is already true and the second trip is silently waved through (verified: a second refresh-request with a different `why_ref` is absorbed; `current` still shows only the first's `why_ref`). #182's HARD band uses this predicate as its release condition, so a stale/first request can satisfy HARD for a different subsequent trip. **Fix:** make the predicate `why_ref`-aware (identity check) or count-based, so a new trip requires its own fresh refresh-request. Coordinate with #182's HARD-band release check. Add tests.

**#191 — advance --from-child double-attaches child consolidation on refusal (idempotency).** `advance --from-child` calls `attach(cl, iid, "review-result", cons)` to record the child consolidation BEFORE the gate's guard checks (postconditions, and #179's why-capture). `attach` appends unconditionally with no dedup. Because `main()` saves state on a refusal, a refused advance (missing `--why`, unmet postcondition) followed by a re-run double-attaches the child consolidation. Impact is low (evidence is additive; a duplicate `review-result` can't falsely satisfy a postcondition it already satisfied) but #179's new why-refusal makes it more reachable. **Fix:** make `attach` (or the from-child seam) idempotent — dedup a `review-result` identical to one already present for the same gate, OR attach only after the guards pass. Add a regression test: refuse-then-retry on a `--from-child` advance → exactly one consolidation attached.

**#192 — docs: CHECKLIST_SCHEMA.md stale.** `docs/CHECKLIST_SCHEMA.md` does not document the epic-#178 additions merged in #179/#182: top-level append-only `why_trail`; per-task `why_exempt` (opt-out default: not exempt); the `--why`/`--mechanical` advance interface (fail-closed: a non-exempt advance with neither is REFUSED); `DIGEST:` and `REFRESH REQUESTED:` lines on `current`; the `refresh-request` evidence type (pointers-only payload: `seam`, `why_ref`); the `has_pending_refresh_request(cl, gate)` predicate; the Trip two-band gate policy (SOFT advisory / HARD refuse-advance) reading `.agent-work/<work_id>/gauge.json` at gate boundaries. **Fix:** update the doc to match the shipped engine — INCLUDING the #189/#190 behavior changes you just made (so the doc lands consistent with the code in the same PR).

## Prior-Wave Verdicts (pasted)
None — this is wave 1, dispatch A. No upstream dependency.

## Pre-Rulings
Each overridable if evidence contradicts it — say so when overriding.
- Bundle all four into ONE PR/branch — they are co-located and interdependent; a split would collide on `scripts/checklist_engine.py`.
- Fix #189 and #190 first (they change engine behavior), then write #192's doc to match the *post-fix* behavior — don't document the old behavior.
- Prefer the smallest change that makes the render path uniform (#189) and the predicate identity-aware (#190); do not refactor the engine's evidence model wholesale.
- If #190's identity-aware predicate needs a matching change in #182's HARD-band release check, make it — that is in-scope, not a new issue.

## Honest-Null Clause
A measured negative on any sub-fix is a complete, successful deliverable. If any one of the four turns out to be already-fixed or a non-problem on inspection, report that with evidence (the exact code path + a test proving current behavior) rather than inventing a change.

## Inherited Latitude
You may: choose the implementation shape, apply the fix, write tests, open the PR. You must FLOAT to the Admiral (return-and-query): any change to the engine's public evidence/gate model beyond these four fixes, any new issue you'd file, anything touching a file outside your ownership below. Merge is the Admiral's call — open the PR, don't merge.

## File Ownership
Sole writer this wave of: `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, and any new/edited tests under `tests/` for the engine. No other wave-1 commander touches these. Do NOT edit `scripts/gauge_reader.py`, `scripts/run_skill_eval.py`, `README.md`, or docs outside CHECKLIST_SCHEMA.md.

## Workspace
Absolute worktree: `C:/Programs/cs-wt-cg` — branch `fix/cg-fastfollows-198`, base commit `467a6b0` (current main), provisioned via `git worktree add -b fix/cg-fastfollows-198 C:/Programs/cs-wt-cg main`.
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-cg` — it must exit 0. Paste its output into your return report.
PR integration = server-side merge (the Admiral merges the GitHub PR).

## Inherited Context
**Active lesson `test-harness-concurrency-failsafe` (directly relevant — you are adding engine tests):** Test harnesses that drive real concurrent file I/O need the same fail-safe discipline as the production code under test: wrap per-iteration work in try/except with a guaranteed stop-signal in `finally`, and mark helper threads `daemon=True`. A writer thread that dies on a transient OS error without signaling stop leaves a non-daemon reader spinning forever and hangs pytest. (Grounded: epic-178 TF9 hung pytest on a transient Windows `os.replace` sharing violation.) If your engine tests spawn threads, apply this; most of these tests won't need threads, so prefer simple single-process tests.
**Windows hazards:** (1) `gh ... --body`/PR body with multiline content: write the body to a temp file and use `gh pr create -F <file>` — a bash heredoc or PowerShell `@'...'@` here-string passed to `--body` fails the PS 5.1 parse. (`@'...'@` DOES work for `git commit -m`, not for `gh --body`.) (2) Use the `py` launcher (`py scripts/...`), not bare `python`. (3) You are already in your own worktree — verify with the isolation script above.
**Engine invariants:** never hand-edit spine JSON; the engine owns it. Run the existing engine test suite (`tests/`) before and after so you have a clean baseline; all pre-existing tests must stay green.

## Pre-empted Steps
None. Run your full understand→plan→execute→reconcile spine.

## Data Locations
All inputs are tracked in the worktree. Reference material (read-only, in the main checkout, do not write): `C:/Programs/constellation-skills/.agent-work/archive/2026-07-18-explore-context-governor/` and epic-178 crew-handoffs if you need design context, but the four issue texts above are self-contained.

## Budget
- **Model tier (required):** opus. Engine-behavior changes with correctness stakes and new tests.
- **Compute/time, session-window:** bounded change; no nested crews needed. If you approach a session/usage limit, checkpoint your branch (commit WIP) and return so the Admiral can relaunch a continuation into this same worktree.

## Stop Conditions
Stop and return when: a fix requires changing the engine's public model beyond these four; a test reveals one of the four is already-fixed (report the null); you need context this order doesn't cover; or you hit a budget/session limit. Asking up is always sanctioned — return-and-query, the Admiral answers and continues you.

## Return Shape
Write your result artifact to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-1/W1-A-REPORT.md` BEFORE going idle, containing: verdict (per-issue: fixed / honest-null-already-fixed), evidence (test names + green run output, the exact functions changed), the PR URL, map impact (does this change the architecture map?), any triage candidates, workflow feedback, and your `verify_worktree_isolation.py --here C:/Programs/cs-wt-cg` output. Open the PR with `gh pr create -F <bodyfile>` targeting main; title `fix(engine): Context Governor v1 fast-follows (#189 #190 #191 #192)`. Post the verdict in the report, then go idle.
