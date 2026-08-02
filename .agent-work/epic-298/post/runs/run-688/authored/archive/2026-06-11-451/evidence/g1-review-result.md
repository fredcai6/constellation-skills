# Review Result

## Assigned Gate
G1 — Reproduce §7.6.2 same-pairs scoreboard + read-only linear representation probe (issue #451, cmdr-451)

## Result
`APPROVE`

## Handoff compliance
All five close criteria satisfied:

1. **Inference only / no production change** — `git status --porcelain` shows only `?? .agent-work/451/` and `?? .agent-work/453/` as untracked; `git diff --stat` is empty; `git status --porcelain scripts/diagnose_quali_same_pairs.py` is empty (harness unmodified). No `src/**`, `scripts/**`, or `params/**` changes.

2. **Harness fidelity** — Extracted from `same_pairs_numbers.json`:
   ```
   rw 0.6710669684016428  rh 0.7786019612773447  ceil 0.8060933702120526  pairs 23862
   ```
   rh=0.7786 and ceiling=0.8061 reproduce §7.6.2 exactly. pairs=23862. Shared-pairs invariant confirmed: all three sources (model, best_across_fp, blend_rank) scored on identical 23862 pairs.

3. **Baseline deviation handled honestly** — `g1_numbers.json` has `"status": "flagged"` and `notes.rw_deviation` documents the cause: "committed bundle gold_cycle_260608_043414 was trained with the #420 anchor active." The 0.6711 is adopted as working baseline per handoff authority, not silently swapped. Decision candidate surfaced for Commander to adjudicate.

4. **Linear probe is walk-forward / leakage-free** — Code review of `probe_linear.py` confirms:
   - LOSO loop: `train_years = [yr for yr in available_years if yr != target_yr]` — test year is never in the fit.
   - Standardization: `mu = X_train.mean(axis=0); sd = X_train.std(axis=0)` computed on train only; `X_test_z = (X_test - mu) / sd` applies train stats.
   - Shared-pairs: probe imports `_shared_nontie_pairs`, `_model_source`, `_restrict`, `_parse_event_id` from `scripts.diagnose_quali_same_pairs` (reuse, not fork).
   - Independent re-run confirmed acc=0.6513 (23862 pairs) deterministically, with per-year results matching the stored evidence.

5. **Internal consistency** — `g1_numbers.json` has `baseline` + `linear_probe` keys. `baseline.rw=0.6711`, `baseline.rh=0.7786`, `baseline.ceiling=0.8061`, `baseline.pairs=23862`. `linear_probe.acc=0.6513`, `linear_probe.total_pairs=23862`. All match `same_pairs_numbers.json` and `linear_probe_result.json`.

## Scope drift
None. Implementation stayed strictly within `.agent-work/451/**`. No production files touched. No full record regen was run (not required). No verdict drawn (as instructed — that is Commander's role).

## Evidence verdict
Required evidence is present and demonstrates the behavior:
- `same_pairs_numbers.json`: harness output with all headline numbers
- `g1_numbers.json`: both `baseline` + `linear_probe` keys, internally consistent
- `linear_probe_result.json`: probe result, matches g1_numbers.json
- `g1-implementer-result.md`: full implementation narrative
- 32 record files (16 rw + 16 rh, 2018-2025) in `.agent-work/451/records/`
- `probe_linear.py`: scratch probe script

Independent reviewer commands run:
```
git status --porcelain            => ?? .agent-work/451/  ?? .agent-work/453/
git diff --stat                   => (empty)
git status --porcelain scripts/diagnose_quali_same_pairs.py  => (empty)
py -c "...same_pairs_numbers.json..." => rw 0.6711 rh 0.7786 ceil 0.8061 pairs 23862
py .agent-work/451/probe_linear.py   => Pooled LOSO sign accuracy: 0.6513 (23862 pairs)
```

## Code/doc quality
Probe script is clean, well-documented, and appropriately scoped as a scratch script (`.agent-work/`, not `scripts/`). Logistic regression is numpy-only (no sklearn dependency — acceptable for a representation probe). Leakage controls are explicit and structurally correct. No production code changes.

## Map impact verdict

- **Evidence supports claimed change:** Yes — rw/rh/ceiling/pairs all independently reproduced from stored JSON; probe acc confirmed by re-run. The rw deviation from §7.6.2 is real (anchor-active bundle effect).
- **Constraints not violated:** Walk-forward discipline, DB-only, and reuse-not-fork constraints all honored in code.
- **Notes match the diff:** Map Impact notes accurately describe the evidence produced. No overstatement. Decision candidate (rw deviation) is surfaced for Commander.
- **Decision candidates surfaced:** Yes — "Commander should decide whether to update the §7.6.2 anchor to 0.6711 or investigate what changed in the bundle."
- **Durable context routed:** Yes — result written to evidence file; deviation documented in g1_numbers.json notes; implementer result captures all findings.

## Reconciliation check
No structural or capability changes to production architecture. The rw deviation is a measurement finding about an existing committed bundle, not a code change. No docs/architecture/index.md update needed. No Cartographer reconciliation required.

## Blockers
- none

## Out-of-scope observations
- **rw per-year trend in probe:** probe accuracy increases 2018→2022, dips 2023, recovers 2024. Possible feature schema evolution or data quality gradient. Not a defect — noted for Commander awareness.
- **OOS 2025 rw-rh gap narrowing:** rw OOS=0.7127, rh OOS=0.7581; headline gap=-0.1075 vs OOS gap=-0.0453. The rh advantage weakens out-of-sample. Commander may want to note this when drawing the §7.6.3 verdict.
- **probe_linear.py placed in `.agent-work/451/` root** (not `evidence/`): acceptable as a scratch script; no structural concern.

## Workflow Feedback

- **Handoff gaps:** The handoff inspection command uses `r['race_weekend']['best_across_fp']['acc']` for `ceiling` — this checks out, but the field naming (`best_across_fp` vs `blend_rank`) for the ceiling isn't explained in the handoff. Had to read `same_pairs_numbers.json` structure to confirm `best_across_fp` is the intended ceiling proxy. Adding a note "ceiling = best_across_fp column in the JSON" would save one lookup.
- **Context rediscovered:** The shared-pairs invariant (all three sources scored on identical 23862 pairs) is the key harness integrity signal. It was implied by the handoff's reference to the AssertionError but not stated as a check to perform independently. Added it explicitly.
- **Instructions improvised around:** The skill instruction says "use the engine rigorously" — the engine `scripts/checklist_engine.py` is the skill's own bundled engine (not the project workbench engine). The survey JSON was initialized from the template and driven through the engine correctly. No mismatch. The `config_ref` in the survey points to the project's `docs/agents/engine-config.json` which may not exist in this worktree, but the engine falls back to defaults gracefully.
- **What would have made this easier:** The handoff `How to inspect` section is excellent. One addition that would help: explicitly state that the probe re-run is expected to be cheap (it is — ~30 seconds) so reviewers know to run it rather than just reading the code.

## Return status
`complete`
