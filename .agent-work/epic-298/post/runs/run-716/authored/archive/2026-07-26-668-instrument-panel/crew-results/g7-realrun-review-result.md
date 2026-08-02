# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g7-realrun-review` (#668 instrument panel, epic #659) — **FOCUSED RE-REVIEW after rework1**
(driven via `.agent-work/668-instrument-panel/g7-realrun-review2/review.json`, session
`g7rr2-session`, consolidated APPROVE, all 7 survey items visited).

## Result
`APPROVE`

## Handoff compliance
Attempt-1 confirmed all six substantive real-data judgments correct and BLOCKED solely because
`py -m src.utils.simplification_limits --paths scripts/instrument_panel_668_report.py` FAILED (2
over-complex functions). Rework1's sole task — extract helpers to clear that gate with byte-identical
output — is DONE and independently reproduced:

1. **Simplification-limits gate clears**: `PASS (1 files checked)`, exit 0, independently re-run.
2. **Refactor is a faithful extract-function split**: read the full 923-line script end-to-end.
   `instruments_2_3_replication` (was cyclomatic 26) → 5 helpers (`_channel_halves_for_partition`,
   `_partition_verdict_entry`, `_accumulate_partition_r`, `_sigma_honesty_checks_for_channel`,
   `_combine_class_verdict`), each doc-stamped "extracted from X, no behavior change." `render_markdown`
   (was 125 lines / complexity 20) → 4 section helpers (`_render_header`, `_render_instrument1`,
   `_render_instruments_2_3`, `_render_instrument4`), concatenated by the parent in the same original
   order. Both parent functions now only sequence/concatenate the extracted calls — no branch,
   computation, or ordering changed from what the code review shows.
3. **Report output identity — verified stronger than claimed**: no pre-refactor git baseline exists (the
   entire #668 issue is uncommitted — every touched file is `??`), so a literal diff against a prior
   commit is impossible. Instead: backed up the on-disk committed `.md`/`.json`, ran the script twice
   fresh, and diffed all three pairwise (pre-committed vs regen1, regen1 vs regen2) — **all diffs empty,
   zero output, for both files**. This is stronger than the implementer's own claim (they reported only a
   key-order-stable JSON deep-equality); independently found full byte-identity, meaning `sort_keys=True`
   achieved complete determinism, not just value-equality. `--check-reproduce` independently re-run: PASS.
   Additionally cross-checked specific numeric/text values quoted verbatim in attempt-1's review (which
   read the pre-refactor report) against the current report — `driver_utilization_share=0.0` (both
   channels, floor), all 8 frozen constants (`REPLICATION_MIN_SUPPORT_N=15.0` etc.),
   `composed_n_eff=0.029346968994966607` (LEC/Belgium), `sigma_honesty` `hits=144/n_checks=144
   empirical=1.0 nominal=0.9` — **all match exactly**. No report number, frozen value, or instrument
   logic changed.
4. **"Also fix" items done**: `sort_keys=True` confirmed at both `json.dumps` sites (lines 912, 917);
   the bug-narrative correction is recorded in the implement-result, correctly separating the real fixed
   bug (`instrument4_whole_lap_calibration`'s hardcoded `DRIVERS`/`CIRCUITS` iteration bug) from
   no-leakback (structurally correct from the start, never needed a fix).

Attempt-1's six substantive real-data judgments (report reproduces at the value level, no-leakback
genuine, driver-utilization FLOOR=0.0 a real `var_team=0` clip, Instrument 4 limitation honest + #670
real, σ-honesty conservative, frozen constants exact) were **not re-litigated** per this dispatch's own
instruction — nothing in this rework touches the code paths they covered (no instrument-module or
frozen-value edit; confirmed via unchanged file mtimes, see Scope drift).

## Scope drift
None. `git status --porcelain`: only `scripts/instrument_panel_668_report.py` (refactor),
`docs/physics/instrument_panel_668_gb2023q_report.{md,json}` (regenerated), and
`.agent-work/668-instrument-panel/` (workflow artifacts) as new/untracked, plus the pre-existing
`M src/physics/layer2/frozen_constants.py` that traces to the already-APPROVED g3-replication gate
(unchanged since attempt-1's own check). `tests/unit/physics/instrument_panel/test_panel_report.py` was
NOT touched, matching the implement-result's claim. Re-verified via mtime that all four
`src/physics/instrument_panel/*.py` instrument modules are dated 18:44–20:16 PDT 2026-07-26, identical
to attempt-1's check, predating both the original g7 session and this rework session. No FastF1 import.
No `docs/architecture/*` touched.

## Evidence verdict
All 3 LOAD-BEARING evidence items independently reproduced, pinned interpreter, in-context:
`simplification_limits` PASS; report byte-identical (zero diff, stronger than required); pytest
`tests/unit/physics/instrument_panel/ -q` → 57 passed; pyright → 0 errors/0 warnings/0 informations;
`git status --porcelain data/` → found `data/f1_data_2023.db` WAL-touched by my own verification runs,
restored via `git checkout --`, confirmed clean after. No claim rested on an unreproduced assertion.

## Code/doc quality
Confirmed against the handoff's own Constraints block (all pass, see Evidence verdict) and
CREW_CONTEXT.md project rules: absolute path convention retained for the untracked slice DB; no
module-level mutable state or DB singleton introduced by the new helpers (all pure functions on explicit
args); extracted-helper naming/doc convention matches the surrounding file. Fowler refactoring pass run
(`r6-fowler`, recorded to `.agent-work/668-instrument-panel/g7-realrun-review2/fowler_pass.json`,
`verify_fowler_pass.py` exits 0, 12 smells assessed): `long-method` now **absent** (resolved — the
rework's whole point); **flagged** = `duplicated-code` (carried over unchanged from attempt-1, out of
this rework's scope — `build_half_cells`/`half_cell_sem` share a filter-and-group block),
`data-clumps` (newly visible post-extraction: `(rows, half/circuits_subset, channel)` recurs across
4 helpers), `long-parameter-list` (`_sigma_honesty_checks_for_channel`, 7 params); **overridden** =
`primitive-obsession` (same logged reason as attempt-1: must interoperate with `replication.py`'s own
`Cell`/string-`class_id` convention). Remaining 8 smells absent. None of the flagged smells are
blocking — all minor, none touch correctness, and the two new ones (`data-clumps`,
`long-parameter-list`) are a natural side-effect of doing exactly what the handoff asked (splitting one
large function into explicit-signature helpers).

## Map impact verdict
- **Evidence supports claimed change:** yes — the implement-result's Map Impact section (internal-only
  restructuring, public surface unchanged) matches the diff, verified by reading the full script:
  `run_panel`/`render_markdown`/`instruments_2_3_replication`/`instrument4_whole_lap_calibration`/
  `enumerate_2v2_partitions`/`instrument4_construction_check` are unchanged in name and signature.
- **Constraints not violated:** yes — no instrument-logic, frozen-value, capability, or constraint
  surface changed; attempt-1's already-confirmed constraint checks (`no-frame-kill`, `strictly-pre`,
  `db-only`/`own-db`, `decision:split-half-unit`) are unaffected since this rework touches none of the
  code paths they cover.
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** none newly needed.
- **Durable context routed:** yes — unchanged from attempt-1 (`#670` real and open, already verified).

## Reconciliation check
No structural baseline concern. Purely internal restructuring of one already-scoped script; nothing to
reconcile against the architecture map beyond what attempt-1 already cleared.

## Blockers
None.

## Out-of-scope observations
- `duplicated-code` (Fowler pass, carried over from attempt-1, unchanged): `build_half_cells` and
  `half_cell_sem` share an identical filter-rows-by-`circuits_subset`-and-group-by-`(driver, class_id)`
  block. Minor, not correctness-affecting.
- `data-clumps` (Fowler pass, newly visible post-extraction): the `(rows, half/circuits_subset,
  channel)` triple recurs across `build_half_cells`, `half_cell_sem`, `_channel_halves_for_partition`,
  and `_sigma_honesty_checks_for_channel`. A small context dataclass could resolve this and the
  duplicated-code observation above in one move, if this file grows further. Not urgent.
- `long-parameter-list` (Fowler pass, newly visible post-extraction): `_sigma_honesty_checks_for_channel`
  takes 7 params. Single call site, each param independently needed; a parameter object would be
  premature abstraction today.

## Fowler pass (r6-fowler)
Recorded to `.agent-work/668-instrument-panel/g7-realrun-review2/fowler_pass.json`;
`verify_fowler_pass.py` exits 0. 12 smells assessed: `absent` = long-method (resolved by this rework),
large-class, feature-envy, shotgun-surgery, divergent-change, message-chains, speculative-generality,
comments-as-deodorant (8); `flagged` = duplicated-code, data-clumps, long-parameter-list (3, all
non-blocking, see Out-of-scope observations); `overridden` = primitive-obsession (1, logged reason: must
interoperate with `replication.py`'s own `Cell`/string-`class_id` convention, unaffected by this rework).

## Workflow Feedback
- **Handoff gaps:** none of substance. The dispatch's instruction to "rely on attempt-1's confirmation
  of the six substantive judgments" was clear and followed; no re-litigation was needed since the
  rework's diff provably does not touch any of the code paths those judgments covered (confirmed via
  unchanged instrument-module mtimes).
- **Context rediscovered:** none — the prior review result, implement result, and rework handoff were
  all present and consistent in `.agent-work/668-instrument-panel/`; no independent digging needed
  beyond reading them.
- **Instructions improvised around:** the dispatch asked to verify "the .md is unchanged" against a
  baseline that does not exist in git (entire #668 issue uncommitted). Improvised a two-part
  verification instead: (a) self-consistency across independent fresh regenerations (proves
  determinism/no-drift from what's currently committed), and (b) cross-checking specific values quoted
  verbatim in attempt-1's prose review (proves content parity with the pre-refactor report attempt-1
  actually read). Both together are at least as strong as a literal git diff would have been, but a
  future rework-verification handoff on an uncommitted branch should name this explicitly rather than
  assume a git baseline exists.
- **What would have made this easier:** nothing further needed — the implement-result's own Evidence
  section (byte-diff proof, deep-equal walk) plus attempt-1's quoted values gave enough independently
  reproducible anchors to close this without ambiguity.

## Return status
`complete`
