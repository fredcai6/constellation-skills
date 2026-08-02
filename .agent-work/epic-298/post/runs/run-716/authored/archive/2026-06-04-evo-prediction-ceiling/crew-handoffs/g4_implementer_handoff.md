# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g4` — update the findings doc to current truth.

## Task
Edit `docs/evo/prediction_ceiling_and_priorities.md` so it reflects what this run
actually established and did. The doc currently OVERSTATES the race-start σ problem
(§1.3 claims "the σ level is too high / too flat" and §3/§4 call "Fix the race-start
σ mis-level (negative sigma_corr)" the "concrete, bounded first win"). That framing
is not supported by a significance test. Correct it.

## Corrected facts to encode (these are verified — G1 harness + independent review)
1. **Decomposition.** The pooled race-start `sigma_corr ≈ −0.065` is not uniform: it
   splits into the two *recent_history* modules
   (`driver_race_start_power_from_recent_history` r=−0.119,
   `constructor_race_start_power_from_recent_history` r=−0.092) plus the two
   *race_weekend* modules which are positive/fine (driver +0.108, constructor +0.206).
2. **It is noise.** Computed over n=24 eval-year-2025 events. The n-aware critical
   value is `r_crit(n=24, α=0.05) ≈ 0.40`; all four |r| ≤ 0.206, every 95% CI spans 0,
   every p > 0.33 → all four are **statistically indistinguishable from zero**. The
   negative sign is sampling noise, not a real anti-signal. (race-start is the most
   deterministic phase: driver rank_mae ~1.2–1.7 vs quali ~3.5–5, so σ barely varies
   and the correlation is noise-dominated.)
3. **The level is fine.** Race-start calibrated-σ level is coverage-aligned, NOT "too
   high / too flat": its calibrated-σ/realized-error ratio is ~+19% vs the quali/race
   reference (under a 25% materiality bar) and its σ flatness matches the reference.
   The earlier "too high / too flat / leaving predictability on the table" claim was
   not supported once significance is accounted for.
4. **The lever can't do what the old framing implied.** The existing post-hoc σ
   calibration (`α·trace + β·dof`, fit vs `rank_mae²`) is **monotone in the trace, so
   it cannot change a correlation's sign** — it is a level/scale lever only. Keep it
   distinct from the *training-time* σ-production lever (`lambda_sigma_nll`, #142),
   which is the only thing that could alter the correlation and is out of scope here.
5. **What this run actually did.** The "concrete, bounded first win" turned out to be
   making the **diagnostic statistically honest**, not re-leveling σ — because there
   was no mis-level. Concretely: the `sigma_error_correlation_wrong_sign` flag is now
   **n-aware** (fires only on a *significantly* negative correlation at the module's
   event count); statistically-insignificant correlations get an advisory
   `insignificant` flag and are no longer reported as defects. The re-level was
   evaluated against held-out evidence and correctly **declined** (no change).
6. **Deferred.** A full fused-Brier confirmation at the next scheduled gold cycle is
   the remaining, tracked step (the offline-only done-bar for this run).

## Protected Intent
The doc must describe CURRENT truth honestly. Do not over-correct into the opposite
overclaim: we did NOT prove race-start σ is perfectly calibrated in an absolute Brier
sense (that is the deferred check) — we established there is no statistically
significant mis-level or wrong-sign signal at n=24, and that the prior claim was
unsupported.

## Test Mode
inspection-only (doc). Reviewer verifies accuracy + valid references.

## Close Criteria
- §1.3: the race-start σ bullet is corrected to the decomposition + insignificance +
  "level is coverage-aligned" framing; the "too high / too flat" / "leaving
  predictability on the table" claim is removed or explicitly retracted. The doc cites
  the `−0.119` figure (and the others) and `r_crit(n=24)≈0.40`.
- §3 Thrust B and §4: the "race-start σ mis-level (negative sigma_corr)" bounded-first-
  win is reframed as the honest-diagnostic fix (n-aware significance gate), noting the
  re-level was declined as unsupported and distinguishing the post-hoc level lever from
  the training-time production lever.
- §5 durable-vs-model-bound table: the "race-start `sigma_corr` sign/level" row is
  updated to reflect "insignificant at n=24" rather than a defect.
- The deferred fused-Brier confirmation is noted.
- Durable facts (persistence baselines, 6.5% ceiling, CV≈0 label collapse, near-
  memoryless reliability) are UNCHANGED — only the race-start σ framing changes.

## Allowed Scope
- `docs/evo/prediction_ceiling_and_priorities.md` ONLY.

## Specific Exclusions
- No code, no other docs, no artifacts.
- Do NOT reference the ephemeral `.agent-work/...` harness path (it is archived, not
  committed) — cite the findings/method, and the existing re-check scripts
  (`scripts/diagnose_prediction_ceiling.py`) where relevant.

## Constraints
- Docs describe current truth, not archaeology.
- Valid commands + existing references only (issue refs #325/#142/#314/#316 if used
  must be real — they are).
- Keep the durable/model-bound split intact.

## Required Evidence
Paste into IMPLEMENTER_RESULT: the git diff of the edited sections, and confirmation
the durable sections are untouched.

## Verification Commands
```bash
py -c "import pathlib,sys; t=pathlib.Path('docs/evo/prediction_ceiling_and_priorities.md').read_text(encoding='utf-8'); sys.exit(0 if '0.119' in t else 1)"
```

## Suggested Model Tier
stronger — reason: a canonical findings doc; the corrected statistical framing must be
exactly right (getting it subtly wrong re-introduces the defect we removed).

## Authority
Decided (human + verified evidence): there is no race-start σ mis-level; G3 re-level
was declined; the win is the honest diagnostic. You must NOT reverse that conclusion or
add new claims beyond the verified facts above.

## Stop Conditions
Stop and return if: encoding the corrected facts requires touching code/other docs, or
a durable fact would have to change (it should not).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, evidence (diff of edited
sections + durable-sections-untouched confirmation), assumptions, stop conditions hit,
out-of-scope observations.
