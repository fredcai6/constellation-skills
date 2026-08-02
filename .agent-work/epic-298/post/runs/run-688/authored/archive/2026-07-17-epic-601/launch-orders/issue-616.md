# Launch Order: cmdr-616 — sampled-runtime reproducibility

## Mission

Run GitHub issue #616 end to end on branch `codex/616-sampled-runtime-determinism`. Diagnose and repair the sampled prediction/backtest seed contract so identical inputs plus seed produce stable canonical position-distribution facts and identical ranked output in both same-process and fresh-process runs. Preserve sampling semantics and model tuning. Add test-led evidence, update the strict interface documentation, commit, push, and open a ready PR that references #616 and epic #601. Do not merge or close the issue.

This is the first dependency-ready bite after #606: trustworthy fantasy-channel A/B work is blocked until stochastic drift is controlled.

## Prior-Wave Verdicts (pasted)

The merged #606 decomposition study established this controlling verdict:

> Across the four complete seasons, the sampled model's mean deficit to the season winner was approximately 7.76 fantasy points/race. FIELD_ORDERING accounted for approximately 5.21 points/race and TOP5 approximately 2.54 points/race. DNF is unidentifiable with current stored classification facts; zero bookkeeping contribution is not evidence of zero opportunity. FIELD_ORDERING is the primary measured opportunity and TOP5 is secondary, but neither clears capacity until a bounded intervention improves the decision metric. Future experiments must report total fantasy points/race plus banded TOP5 and FIELD_ORDERING effects. Do not treat generic rank/sign/correlation improvement as sufficient. Sequencing consequence: resolve sampled-runtime reproducibility (#616) before trusting A/B deltas.

Issue #616's concrete failure evidence is also controlling: a 2022 round-one pilot and full reconstruction used the same current code, assembled manifest, `n_samples=1000`, and `seed=0`, but produced different distribution hashes (`995415…` vs `12c22a…`), different top tens, and fantasy scores 57 vs 55. Fresh full-season totals 832/841/811 diverged from the hash-frozen historical 873/850/859 while race-classification row hashes were unchanged.

Acceptance shape:

- Two same-process and two fresh-process executions with identical inputs and seed produce byte-stable canonical position-distribution facts and identical ranked outputs.
- Changing the seed changes at least one sampled fact in a controlled test.
- The seed is threaded through every RNG source with no implicit global-state fallback.
- `race-week`, `sampled-predict`, and `sampled-backtest` expose and record the same seed contract.
- A regression fixture covers the #606 repeated-round failure shape.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- Diagnose before fixing. Inventory Python, NumPy, PyTorch/model-framework, distribution, and worker/process RNG sources along the full consumer topology.
- Use test-driven development: first reproduce at the smallest runtime seam that still exercises the drift, then add fresh-process coverage.
- Preserve statistical/sampling semantics, model parameters, and canonical historical outputs. Do not bless a new score as canonical.
- Prefer a single explicit seed-derivation interface with strict inputs and no global-state fallback. Backward compatibility is not a goal if it would preserve ambiguous execution paths.
- Run design-it-twice for any load-bearing seed interface. You may converge autonomously only if both alternatives fit the existing architecture and the choice is non-architectural; otherwise return the comparison to the Admiral.
- A measured negative is complete only when it names every RNG source inspected, exact conditions tested, and the remaining nondeterministic surface.
- The dirty primary checkout and all pre-existing untracked data/scripts are owner state. Do not modify, move, delete, or stage them.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win, including what was tested and what was not.

## Inherited Latitude

You may decide diagnosis tactics, test shape, issue-scoped implementation/refactors, non-architectural RNG threading, documentation, commits, push, and PR creation. Float any load-bearing seam or architecture-boundary change, sampling-semantic/model-tuning change, canonical-result change, file deletion, issue scope expansion, merge, or issue close/reopen. A decision fitting no class always floats to the Admiral.

## File Ownership

You are the sole writer in `C:/Programs/f1Brainz/.claude/worktrees/616-sampled-runtime-determinism`. Own all issue-scoped code/tests/docs and `.agent-work/cmdr-616/COMMANDER_RESULT.md`. Do not write the primary checkout. For feedback/archive, stage the complete fenced trio plus `FENCE.md` under worktree-local `.agent-work/staged-feedback/cmdr-616/`; the Admiral will harvest it later.

## Workspace

Absolute worktree: `C:/Programs/f1Brainz/.claude/worktrees/616-sampled-runtime-determinism`

Branch: `codex/616-sampled-runtime-determinism`

Base: `16bece5353b1ed06612bfcbc9816baba5190a508` (`origin/main`, PR #618 merged)

Created with:

`git worktree add -b codex/616-sampled-runtime-determinism .claude/worktrees/616-sampled-runtime-determinism origin/main`

First step before any git operation:

`py C:/Users/fredc/.codex/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:/Programs/f1Brainz/.claude/worktrees/616-sampled-runtime-determinism`

Paste its output into the return report. PR integration is server-side and is not authorized in this bite.

## Inherited Context

- Read `docs/AGENT_GUIDE.md`, `README.md`, `TESTING.md`, `docs/architecture/index.md`, `docs/DOCUMENTATION.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/CREW_CONTEXT.md`, and relevant evo/runtime docs before changes.
- Database records are the sole authoritative analysis source; no direct FastF1/Jolpica calls from analysis/runtime code.
- Prediction output is high-stakes: fail visibly, avoid hidden fallback, and require calibrated machine-checkable evidence.
- Test-led logic changes; run focused evo tests first and the broader evo/strategy or compact pipeline validation when shared runtime interfaces change.
- Run strict simplification limits on touched Python paths.
- Python is invoked as `py`, never `python`.
- Artifact postconditions use engine `attach`, not manual JSON edits or null attestations.
- Keep the worktree fence. Worktrees do not inherit the primary checkout's untracked databases or artifacts.

## Pre-empted Steps

Epic context, #606 sequencing verdict, issue selection, base freshness, worktree provisioning, and publication latitude are ratified by this launch order. Cite it at delegated `user-decision` gates; do not ask the human.

## Data Locations

Tracked gold/runtime inputs exist in the worktree. If a test genuinely requires untracked inputs, read only from `C:/Programs/f1Brainz/data/` or `C:/Programs/f1Brainz/outputs/` and record exact paths and hashes. Do not mutate them. Prefer synthetic fixtures for deterministic regression coverage.

## Budget

- **Model tier (required):** high-reasoning/default Codex tier, justified by cross-process stochastic state and shared runtime-interface risk.
- **Compute/time, session-window:** one bounded Commander run. Prefer focused synthetic tests; no model retraining or multi-season backtest. A focused test may run minutes, but stop before any unbounded or overnight compute.

## Stop Conditions

Stop and return when scope exceeds #616; a load-bearing architecture decision or sampling-semantic change is required; canonical results would change by design; required evidence needs model retraining or long multi-season compute; `origin/main` changes in a relevant conflicting way; owner state would need mutation; or the acceptance surface is impossible with current inputs. Query the Admiral for missing context rather than guessing.

## Return Shape

Drive the delegated Commander spine through terminal archive and release. Before going idle, write `.agent-work/cmdr-616/COMMANDER_RESULT.md` containing: verdict; root cause; alternatives compared and chosen seam; files/commits/PR; exact test commands and outputs; same-process/fresh-process evidence; changed-seed evidence; isolation-check output; architecture/map impact; triage candidates; staged feedback location; and workflow feedback. Send the same concise verdict to the Admiral. Do not merge the PR or close #616.

