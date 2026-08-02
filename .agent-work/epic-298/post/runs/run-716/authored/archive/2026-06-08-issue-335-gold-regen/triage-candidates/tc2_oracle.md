## What
The `oracle_all_states` sampled-backtest mode raises `ValueError('sampled positions must be a strict permutation of positions 1..20')` on at least one 2025 race (job/race index 20), **non-fatally** — the gold cycle logs a warning and continues, leaving that race unscored in the oracle mode. The `sampled_state` (production) mode scores all 24 races cleanly.

Surfaced during the #335 gold regen on **both** arms (`position_quality` and `quali_pace_gap`), so it is encoding-independent and **pre-existing**.

## Why it matters
`oracle_all_states` is an oracle upper-bound diagnostic; production scoring (`sampled_state`) is unaffected. But the oracle aggregate is computed over 23/24 races instead of 24, and the error is the same DNS / non-contiguous-grid family that #330 fixed for `sampled_state` — the oracle scoring path appears not to have received the equivalent entrant-restriction / permutation-gap handling.

## Evidence
- #335 regen cycle logs (both arms): `Sampled-runtime backtest mode 'oracle_all_states' failed (non-fatal): job at index 20 ... failed: ValueError('sampled positions must be a strict permutation of positions 1..20')`.
- `sampled_state` for the same run: 24 scored, 0 skipped.
- Branch `constellation/issue-335-gold-regen`; promotion commit `2327803`.

## Acceptance
- `oracle_all_states` scores all 24 races for 2025 (and historical years) without the permutation `ValueError`, applying the #330-style entrant-restriction / permutation-gap handling to the oracle scoring path.

## Out of scope
`sampled_state` (already correct), the quali pace anchor, the form encoding.
