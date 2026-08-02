# Implementer Handoff — G2 (issue #451, cmdr-451) — DECISIVE feature-ablation retrain

You are a constellation-implementer crew (Sonnet). Invoke constellation-implementer, then execute this gate. Worktree `C:/Programs/f1Brainz-worktrees/cmdr-451`; `py` not `python`; `PYTHONIOENCODING=utf-8` on captured python; absolute paths (cwd resets between calls). Long compute runs FOREGROUND, bounded (each retrain <=10 min — they are fast, seconds-to-minutes at the splits below; poll, do NOT background).

## Gate
g2 — the decisive test of hypothesis (a) representation vs (b/c). Two single-module retrains of `driver_quali_power_from_race_weekend`, scored on the §7.6.2 same-pairs harness, contrasted.

## Background you need (load-bearing)
- The rw head's 23 input features are `qs_*`/`short_run_*` ADJUSTED aggregates (see `src/evo_predictor/quali_power_adapter.py`, `DRIVER_QUALI_POWER_FEATURE_NAMES`, built in `_driver_vector`). G1 showed a walk-forward LINEAR probe of these features scores only 0.6513 — at/below the head, ~15pp below the 0.806 ceiling → the cross-channel min-sector pace ordering is NOT linearly present in this vector.
- `DriverFeatures` (`src/evo_predictor/models/_features.py`) ALREADY carries `qs_best_raw` and `lr_best_raw` — raw best-lap times (lower=faster). `min(qs_best_raw, lr_best_raw)` is EXACTLY the #420 production cross-channel pace anchor (§7.6.4) and the all-FP min-sector "who is generally fast" signal whose ceiling is 0.806. The #420 anchor bolts this onto the head's OUTPUT post-hoc; this gate tests whether the head can LEARN it as an INPUT feature.
- `feature_dim` is derived dynamically from the built batch (`module_training_orchestration.py:223`), so appending one value per driver vector auto-propagates to the net — no config edit needed.
- The train CLI and emit CLI are smoke-verified working and fast.

## Task — run BOTH conditions on the SAME split and harness

### Split (keep retrains bounded — single held-out-year reading, flagged as such)
Use TWO eval years to get a stable read without full 7-fold LOSO:
- Condition split A: `--train-years 2018 2019 2020 2021 2022 2023 --eval-year 2024`
- Condition split B: `--train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025` (OOS)
Run each of the two FEATURE conditions below on BOTH splits. (4 retrains total; all fast.) Report per-split harness numbers; do NOT claim the full LOSO headline number — flag these as single-held-out-year readings. The CONTRAST (control vs +pace) on the same split is the localization signal.

### Condition CONTROL (as-is, current 23 features)
Retrain rw as-is, emit records for the eval year from the freshly trained bundle, score the §7.6.2 harness on that year. Expected near the G1 working baseline for that year (rw 2024 ~ headline-ish; the harness reports per-regime — for a single eval year you will score that year's events only).

### Condition +PACE (add one input feature = the min-sector pace anchor)
Make a SCRATCH, BRANCH-LOCAL, REVERSIBLE edit to `src/evo_predictor/quali_power_adapter.py` that appends ONE extra feature to each driver's vector in `_driver_vector`: the cross-channel min best-lap = NaN/None-safe `min(qs_best_raw, lr_best_raw)` from the `DriverFeatures` (mirror the #420 idiom). Append it as the final value AND add its name (e.g. `cross_channel_min_pace`) to `DRIVER_QUALI_POWER_FEATURE_NAMES` so dims stay consistent. Keep the edit minimal and clearly marked `# PROBE g2 #451 — revert`. Bump the feature_schema_version string suffix locally if the bundle write requires it. Then retrain + emit + harness on the SAME splits.
- NOTE on scale: the raw best-lap is in seconds; the head ingests antisymmetric pairwise DIFFERENCES, so the feature enters as a pace-gap-in-seconds difference. That is acceptable for this probe (LayerNorm in the net handles scale). If you want a cleaner read, ALSO try a within-event-standardised variant of the same min-pace (z-score per event) as a second +pace sub-run and report both — but the raw-min variant is the required minimum.

### Harness scoring
For each retrained bundle, emit `rw_{evalyear}.record.json` into a CONDITION-SPECIFIC records dir (e.g. `.agent-work/451/records_g2_control/`, `.agent-work/451/records_g2_pace/`) using the SAME `backtest-latent-power-module --emit-module-record` recipe as G1 (bundle = the freshly trained module dir). Also emit the `rh_{evalyear}` record (unchanged rh bundle from the committed gold is fine, OR reuse G1's rh records) so the harness's shared-pairs set is identical across conditions. Run `scripts/diagnose_quali_same_pairs.py` UNMODIFIED with `QUALI_SAME_PAIRS_RECORDS_DIR` pointed at each condition dir. Record rw acc, ceiling, pairs per condition per split.

CRITICAL for apples-to-apples: the shared-pairs population depends on rh and the ceiling, which are identical across conditions, so control vs +pace differ ONLY in the rw head — the contrast is clean.

## Verdict logic to REPORT (Commander decides, you report the numbers + which way they point)
- If +PACE closes the bulk of the control→ceiling gap (rw rises materially toward ~0.74-0.80) while CONTROL reproduces the deficit → hypothesis (a) representation CONFIRMED: the info was absent from the feature vector and is learnable once supplied as an input.
- If +PACE does NOT lift rw materially → representation is NOT the lever (points to training-signal/capacity); G3 then matters.

## Write evidence
`.agent-work/451/evidence/g2_numbers.json` with top-level keys `as_is_control` (dict: per-split rw/ceiling/pairs) and `pace_feature` (dict: per-split rw/ceiling/pairs, plus the within-event-z variant if run), plus a `splits` note and a `points_to` string ('a' | 'not_a' | 'ambiguous').

## Allowed scope
`.agent-work/451/**` (records, scratch runs, evidence); a SCRATCH reversible edit to `src/evo_predictor/quali_power_adapter.py` (and `src/evo_predictor/models/_features.py` ONLY if a field is genuinely missing — it is not, qs_best_raw/lr_best_raw exist). Do NOT commit these src edits to a promoted path; they are probe-local and MUST be reverted before the gate's git is clean (the Commander will confirm the working tree is clean of src/ changes at integrate — leave the edit in place for the reviewer to inspect, then revert when told, OR keep it on a clearly-marked scratch stash and report the diff).

## Specific exclusions
NO gold cycle. NO fusion retrain. NO Piece-2. NO change to promoted defaults that persists (the adapter edit is a probe; it must be reverted/stashed, not landed). NO modification of `diagnose_quali_same_pairs.py`.

## Constraints
- Single-module ablation retrains ONLY. Walk-forward as-of: the pace feature is FP-derived (pre-Q), so it respects the cutoff; the eval year is held out (or OOS) — no scored pair leaks into training.
- DB-only; `py`; utf-8 child env. Foreground bounded retrains; if any single retrain exceeds ~30 min repeatedly, STOP and report.
- Determinism: pass a fixed `--seed` (e.g. 0) to all retrains so control and +pace differ only by the feature.

## Map anchors (inbound)
Structural: quali_power_adapter `_driver_vector`; DriverFeatures qs_best_raw/lr_best_raw; run.py train-latent-power-module + backtest emit; InnerNetwork (feature_dim auto). Decision: §7.6.3 C3 (only a new ordering signal moves sign-accuracy); decision pressure — a small representation fix touches a promoted default → Commander floats to Admiral, does not self-merge. Evidence: #414/#420 anchor recovered ~70% post-hoc; G1 linear probe 0.6513.

## Required evidence
`g2_numbers.json`; the harness stdout per condition (saved); the adapter diff (`git diff src/evo_predictor/quali_power_adapter.py`) quoted in your result; per-split rw control vs +pace numbers quoted in IMPLEMENTER_RESULT.

## Verification commands
```bash
git diff --stat src/                                  # shows the probe edit (to be reverted/stashed)
PYTHONIOENCODING=utf-8 py -c "import json; d=json.load(open('.agent-work/451/evidence/g2_numbers.json')); print('as_is_control' in d, 'pace_feature' in d, d.get('points_to'))"
```

## Suggested model tier
stronger — involves a careful src edit + multiple retrains + harness wiring; reason: moderate ambiguity and care needed to keep the contrast clean and reversible.

## Authority
Probe design fixed here. You do NOT decide the verdict or land any src change. If the adapter edit cascades into errors you cannot resolve in ~2 attempts (e.g. schema-version assertions, feature_dim mismatch on emit), STOP and report exactly where it broke — do NOT hack around contracts.

## Stop conditions
Stop and return if: a retrain errors irrecoverably; the feature injection cannot be made without touching a frozen contract beyond a reversible local edit; the harness can't score a condition; or you'd need to exceed the single-module fence.

## Return format
Return IMPLEMENTER_RESULT: per-split CONTROL vs +PACE rw numbers (and z-variant if run), ceiling, pairs; which way it points ('a'/'not_a'/'ambiguous') and why; the adapter diff; files changed; whether the src edit is reverted or stashed (report the diff either way); assumptions; stop conditions hit; out-of-scope observations; workflow feedback. Write it to `C:/Programs/f1Brainz-worktrees/cmdr-451/.agent-work/451/evidence/g2-implementer-result.md`.
