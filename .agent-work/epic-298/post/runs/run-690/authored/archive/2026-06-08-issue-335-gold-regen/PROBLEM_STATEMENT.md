# Problem Statement — issue-335-gold-regen

**Goal:** One full gold retrain that consolidates everything pending, plus the related cleanups, with the quali pace anchor activated. Promotion is gated behind an explicit human checkpoint.

## What this one regen settles
1. **v6-schema staleness** — `skill_vs_chance` missing on the promoted bundle (#335 body); regen against merged v6 code produces it.
2. **Quali pace anchor activation (#420)** — flip `quali_pace_anchor_enabled = true` so fusion + calibration train against the anchored pi distribution. Headline accuracy win.
3. **Dropout-seeding re-validation + re-promotion (#362)** — regen produces the seeded realization; reproducible at `max` (threads=1).
4. **Median-relative encoding regen (#368/#369)** — lr=1e-3/epochs=100/patience=15 already on `main`; regen runs under them.
5. **#375 composition — NO-OP** — #375 closed an honest null (no production switch; `sampled_runtime.py` untouched). Nothing to activate.

## Confirmed decisions (interrogation 2026-06-07)
- **Anchor: ON** (`quali_pace_anchor_enabled = true`, alpha 0.5 already set).
- **Quali-pace-gap encoding: A/B both arms, full cycles, anchor ON each; save both.**
  - Arm A = `position_quality` (current default) + anchor — also the default production candidate.
  - Arm B = `quali_pace_gap` + anchor.
  - **Decision metric = fused-output quality (Brier primary at the fusion/system level on backtest), NOT a 12-family per-module sweep** — "whose fusion works out best."
  - Within-tolerance/tie → **prefer `quali_pace_gap`** (user bias). User not in a rush; willing to spend compute for real evidence.
- **Runtime:** `utilization = max` (cores-1 workers, threads_per_worker=1 → fastest AND bit-reproducible). Background; checkpoint user on completion.
- **Promotion:** **talk before promotion no matter what** (hard human checkpoint). User picks the arm to promote after seeing the evidence.

## Cleanup items (all four; "talk through the non-obvious")
- **(a) NLL metric naming — already done on `main` (#384).** Producer emits `corr_sigma_pi_trace_vs_nll`; consumer expects it; `test_consumer_sigma_keys_equal_producer_sigma_keys` pins equality. `_vs_log_loss` survives only in stale pre-v6 reports being replaced. → verify fresh reports only.
- **(b) Quali-pace-gap encoding decision** — settled by the A/B above.
- **(c) `_WEIGHT_TOL` (1e-6) at production scale (#362)** — resolved by running at `max` (threads=1 = the bit-reproducible regime the bounded determinism test proves). Accept the construction argument; **no** strict full-scale 2-run repro check (user: "do the thing that makes compute best").
- **(d) sampled_runtime race_count 23→24 (#330)** — code already fixed; regen picks it up. → verify it lands 24.

## Baseline & success
- **Brier baseline:** currently-promoted `gold_cycle_260603_173742_2018thru2024` (anchor-OFF, pre-#420).
- **Done =** both arms trained + fused; fused-Brier comparison computed; `accept_quali_anchor_420.py` reproduces §7.6.4 numbers on the anchored bundle; `pipeline_validation --profile compact` → gold pass; cleanups (a)/(c)/(d) verified; evidence saved for both arms; promotion decision taken by the user.

## Guardrails
- Generated artifacts are derived — regenerate; don't hand-edit. DB is the only analysis source.
- Push/PR/promote/merge require explicit user approval.
- Report-schema convention stays single (nll), per one-canonical-path doctrine.
