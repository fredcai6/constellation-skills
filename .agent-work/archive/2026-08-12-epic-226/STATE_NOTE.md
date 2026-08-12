# State Note — epic-226 (crash-resume)

- **step:** execute — **in-progress**. **Wave 0 is DONE AND MERGED** (6 PRs, main at `3283158`, zero PRs open). Wave 1 (F #232) is provisioning/dispatching. Closeout has NOT started.
- **slug:** epic-226-wave-1
- **next command:** from `C:/Programs/constellation-skills` (this repo **VENDORS** the engine — drive `scripts/checklist_engine.py`, NOT the installed global copy):
  1. `py scripts/checklist_engine.py --file .agent-work/epic-226/spine.json current`
  2. If the lease is not yours, re-claim with a NEW session id: `... claim --session-id admiral-epic-226-c --claimed-by admiral --worktree . --force --reason "<why>"`. Prior leases (`admiral-epic-226`, `-b`) are left active by design; `--force` records the takeover.
  3. Poll `.agent-work/epic-226/verdicts/commander-232.md`. Then drive **closeout**.
- **pid:** none detached. Commanders are background Agent-tool subagents of the Admiral session — if it dies they die with it and must be relaunched into their existing worktrees (which keep their commits).
- **expected artifact:** verdict at `.agent-work/epic-226/verdicts/commander-232.md` + one PR for #232.

## What is already done (do NOT redo)
- **Latitude contract CONFIRMED, then RE-ARMED by Fred** at the wave-0/1 checkpoint (*"yup, okay to merge and keep on going"*). All 8 pre-rulings stand. Cleared through wave 1 into closeout; closeout's acceptance step is still the final human gate.
- **Six PRs merged:** #236 (#231), #237 (#229), #240 (#228), #238 (#230), #241 (#227), #245 (#239 item 3). Main `83a31b1 → 3283158`.
- **PR-1 self-hosting probes PASSED** — read-only `current` on the LIVE spine under the new engine exit 0; mutating `advance` on a COPY returned a sane REFUSED, not a crash. Do not redo.
- **Batched re-verification (PR-3) PASSED on merged main:** `1033 passed`, exit 0; skip-guard exit 0; **coverage 93%** against the 90% floor (the flagged risk did not materialize — it went UP).
- **HARVEST ALREADY COLLECTED** → `.agent-work/harvest-226/<issue>/` (17 files from all five wave-0 worktrees). Copied, **not yet applied**. Do not re-harvest wave 0; DO harvest wt-232 and wt-239 before sweeping them.
- **Triage all routed:** #239 (from #230), #242 (from #227), #243 (from #228), #244 (Fred's standing instruction). None left unrouted.
- **Worktree isolation gated** for wt-232 (exit 0).

## What the next Admiral must do
1. Finish wave 1: dispatch/monitor commander-232 (**sonnet**), adjudicate, merge.
2. Then drive **closeout** through the engine — do NOT stop at the last merge:
   - lessons audit via a fresh-context `constellation-lessons-auditor` subagent, with a `collect_feedback.py` sweep (this is a dogfood run against constellation-skills itself — see `docs/DEBT_SWEEP_CADENCE.md`);
   - append the epic retrospective to `.agent-work/AGENT_FEEDBACK.md`; `verify_agent_feedback.py` must pass;
   - architecture reconcile via `constellation-cartographer`;
   - **harvest wt-232/wt-239, THEN** sweep all seven worktrees (`git worktree remove` + `prune`) — only after merge or confirmed-dead;
   - archive ADMIRAL_LOG to `.agent-work/archive/`;
   - present the epic summary for user acceptance.
3. Order the close correctly: satisfy closeout postconditions → final `advance closeout` → **then** `release` the lease as the very last action.

## Binding rulings from the checkpoint
- **Wrapped decision bullets are INVALID**, enforced mechanically (shipped as GL013 in #245).
- **`execute-the-advice-a-test-asserts-on` doctrine promotion APPROVED** by Fred — goes to the lessons auditor as a graduation with human authority, no longer a deferred `needs human`.
- **Commanders should file issues at the main repo**, not bank findings worktree-locally. Standing, third occurrence, filed as **#244**; blocked on them lacking `gh issue create` pre-clearance.

## Harvest instructions (apply at closeout — provenance is fresh NOW)
- **SIBLING FORK, CONFIRMED IN THE DATA:** `checklist-engine-from-child-relative-path-and-gated-vs-survey` (wt-228, `add`, constellation) and `from-child-refusal-undiscoverable-from-error` (wt-231, `add`, project) are **two slugs, one defect**. Land **ONE** lesson under the constellation-scoped id, `amend`ed to carry both halves, with wt-231's raise as a **`confirm`** — never two `add`s.
- **`verify-launch-order-claims-against-code` drew `confirm`s from BOTH wt-227 and wt-230** → four data points, the most-confirmed lesson in the inbox and the clearest graduate-and-retire candidate. Fold in #230's widening: from *"is the mechanism already shipped"* to also *"does the named edit target exist at the named address"*.

## Live hazards
- **A test count from a different environment is NOT a baseline.** The main checkout and a fresh worktree legitimately differ (untracked `DESIGN_SPEC.md`; symlink permissions) — I quoted one as a baseline and was corrected. State the environment with the number.
- **Local git-less proofs are error-prone:** stripping `/mingw64/bin` leaves a second `git` at `/cmd/git`. **Assert `which git` exits non-zero** before trusting a git-less result.
- **PR-2b:** no Commander may trigger, wait on, poll for, or claim a GitHub Actions run. "CI green" without a local transcript is invalid evidence.
- **#233 (G) and #234 (H) are NEVER dispatched** — design threads for a future human-led explorer pass. Dispatching either violates the contract.
- **Use `python`, not `py`** — `py` may resolve to a pytest-less runtime here (#242 item 2).
- **Never end a turn to wait on a Commander.** Headless run; nothing resumes it. Poll in bounded in-turn loops. And **late ≠ dead** — check for a read-only agent's *output*, not its file writes, before stopping it.
