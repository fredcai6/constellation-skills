# Launch Order: `cmdr-659-665 — Validate the pooling primitive under driver×class imbalance`

Commanders start cold. Read this whole order, then `gh issue view 665` for the full build spec (confirmed spec §4 statistical-core bullet / review T9). **Small, decisive, gates the fingerprint fit (G/#666) — synthetic only, no real-data pipeline dependency, so it runs immediately in parallel with the rest of Wave 0.**

## Mission
Build issue **#665** (epic #659, Build 1, manifest id `F`): a synthetic-recovery harness that decides whether the existing `fit_two_way` primitive (`src/physics/layer2/pooling.py`) is adequate for the DriverFingerprint hierarchy (field mean → driver-overall → class cell + class-across-drivers parent, axes reinterpreted as **driver×class**) under **realistic driver×class imbalance**, or whether the named fallback (#628-style direct per-(driver,class) `pool_random_effects` with explicit parent shrinkage, as in `src/physics/utilization/driver_utility.py`) must be adopted instead. `fit_two_way`'s own docstring says its method-of-moments variance components are **"exact for a balanced grid, approximate otherwise"** — and driver×class support is decidedly unbalanced. The deliverable is a **measured verdict, either way.**

**Key sourcing note (from the issue):** the imbalance profile comes from data that ALREADY EXISTS — per-driver 2023 lap counts crossed with #625/#638 class tallies — NOT from this epic's pipeline output. That's why this issue has no predecessors. Draw synthetic ground-truth driver effects + class effects into deliberately unbalanced cell counts matched to that real 2023 driver×class support profile; score shrinkage behavior and variance-component recovery.

## Prior-Wave Verdicts (pasted)
None — Wave 0.

## Pre-Rulings
- decision:measured-verdict-is-the-deliverable — PASS (adopt `fit_two_way`) or FAIL (adopt #628-style direct pooling with explicit parent shrinkage) are BOTH complete successful deliverables. The point is that the choice is measured, not assumed. State the imbalance profile you tested against.
  @grade: settled/human · leans acceptance
- decision:student-t-seam-both-branches — thin-support→fat-tail goes through the repo's canonical Student-t seam (`predictive_t`, project-wide ν defaults) in BOTH branches; no invented statistical machinery in Build 1.
  @grade: settled/human
- decision:synthetic-only — this issue touches NO real data and NO pipeline output; the 2023 support profile is drawn from existing lap-count/class tallies only, then synthetic effects are injected. A true hierarchical-t upgrade is out of scope (possible later behind the same interface).
  @grade: settled/human
- decision:no-baked-normality — heavy-tailed forms where feasible (standing principle).
  @grade: settled/human

## Honest-Null Clause
Both PASS and FAIL are wins here by construction — the deliverable IS the measured decision. Report the recovery quality (bias/variance of recovered driver & class effects, shrinkage behavior) with full rigor and stated scope (which imbalance regimes tested, which not).

## Inherited Latitude
Exercise (logged): your own harness/test design, debt-issue proposals, bounded fix-now triage. **Float to Admiral:** scope changes, any boundary decision, or if the synthetic result is genuinely ambiguous (neither clean PASS nor clean FAIL) and you need a ruling on which primitive to recommend. Merge is the Admiral's. Model tier: **Sonnet**.

## File Ownership
Working-notes: `.agent-work/epic-659/notes-665.md` (sole writer; not `findings-*`). Do NOT commit any `.agent-work/` path on the mission branch — return lessons-delta + feedback in closeout.

## Workspace
Worktree: **`C:/Programs/f1brainz-wt/epic659-665`** · branch `epic659/665-pooling-validate` · base `f404d2cb` (current local main, 7 ahead of origin — correct).
Created with: `git worktree add C:/Programs/f1brainz-wt/epic659-665 -b epic659/665-pooling-validate f404d2cb`
**First step:** `py C:/Users/fredc/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:/Programs/f1brainz-wt/epic659-665` → exit 0, paste output. PR = server-side merge (do not local-merge).

## Inherited Context (lessons + invariants — paste, not pointer)
- **Python is `py`**; tests `py -m pytest tests/...`.
- **Editable-install .pth worktree trap (critical for a bespoke harness):** a script run from a worktree imports the MAIN repo `src/`, not the worktree's `src/` — so if you edit `pooling.py` in your worktree and run a bespoke harness script, it may silently exercise MAIN's `pooling.py`. Put the worktree `src/` first on `sys.path`, or drive the harness through pytest (safe). This issue is especially exposed because it's a bespoke validation harness.
- **LOO / out-of-sample discipline:** if any part of your recovery scoring uses a self-weighted predictor, use leave-one-out; a self-inclusive form is blind to the σ-understatement failure. (Here you have synthetic ground truth, so recovery is directly scorable — but if you build any predictive check, keep it out-of-sample.)
- **Crews are Agent-tool subagents** (no `claude --role` binary) — dispatch via Agent tool if you spin any; but this issue is small enough to likely need none.
- **Never idle on one long watcher** — synthetic recovery is fast; keep it in-turn. Deliver artifact + post verdict before idling.
- **`py -m src.utils.simplification_limits`** on touched paths (strict) before done.

## Data Locations (untracked — NOT in your worktree)
- 2023 DB (for the support PROFILE only — lap counts × class tallies, not pipeline output): `C:/Programs/f1Brainz/data/f1_data_2023.db`.
- Seams: `src/physics/layer2/pooling.py` (`fit_two_way`, `pool_random_effects` — read the docstrings), `src/physics/utilization/driver_utility.py` (the #628 direct-pooling fallback precedent), `src/common/student_t.py` (`predictive_t`).

## Budget
- **Model tier: Sonnet.**
- Compute/time: synthetic, fast, in-turn. No detach needed.

## Stop Conditions
Stop and return when: scope exceeded; the result is genuinely ambiguous and needs a ruling; or you need context this order doesn't cover. Return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict: **PASS** (adopt `fit_two_way`) or **FAIL** (adopt #628-style direct pooling with parent shrinkage) — with the 2023 driver×class imbalance profile you tested against, the recovery quality (bias/variance of recovered driver & class effects, shrinkage behavior, variance-component recovery), and which regimes were / were not tested. + `simplification_limits` result + map impact + triage candidates + workflow-feedback + `verify_worktree_isolation.py --here` matched path. Open the PR (`gh pr create -F <tempfile>`, never a heredoc body on Windows), post the verdict; Admiral gates+reviews+merges. Return thin, write fat (`notes-665.md`). This verdict is a hard input to G/#666 (fingerprint fit) — state it unambiguously. Deliver artifact + post verdict before idling.
