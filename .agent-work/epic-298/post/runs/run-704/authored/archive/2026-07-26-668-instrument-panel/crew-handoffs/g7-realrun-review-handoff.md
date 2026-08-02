# Reviewer Handoff — g7-realrun-review (final instrument gate)

## Gate
g7-realrun-review (#668 instrument panel). Worktree `C:/Programs/f1brainz-wt/epic659-668`,
branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`. NOTE the editable-.pth trap
for the bare report script (it self-fixes sys.path — confirm it does).

## Survey State Location
`.agent-work/668-instrument-panel/g7-realrun-review/review.json`.

## What Was Implemented
The cross-circuit real-data run of all four instruments on `fp_slice_2023Q.db` +
`data/f1_data_2023.db`, emitting `scripts/instrument_panel_668_report.py` →
`docs/physics/instrument_panel_668_gb2023q_report.md` (+ `.json`) + `test_panel_report.py`.
Result: `.agent-work/668-instrument-panel/crew-results/g7-realrun-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree. `git status --porcelain` then `git diff`. **DB-BLOB GUARD: running the
report/tests WAL-touches `data/f1_data_2023.db` — do NOT commit it; confirm `git status --porcelain
data/` is clean at the end (restore with `git checkout -- data/f1_data_2023.db`).**

## Close Criteria (each a check — reproduce)
- **Report reproduces**: re-run `scripts/instrument_panel_668_report.py` on the pinned interpreter;
  the four instruments' numbers match the committed `.md`/`.json` (deterministic).
- **No leakback**: the strictly-pre `as_of_round` is threaded; official sector times enter ONLY as
  the post-hoc comparison target, never into a prediction. (The implementer fixed a real bug here —
  confirm the fix and that `test_panel_report.py`'s no-leakback assertion genuinely catches it.)
- **Honest no-frame-kill sizing**: driver-utilization FLOOR = 0.0 must be a GENUINE method-of-moments
  clip (var_team ≤ 0 → 0), NOT a bug — verify by reading the decomposition on the real values.
  Confirm the small/zero size is stated plainly, not spun.
- **Instrument 2/3**: cross-circuit 2v2 (3 partitions averaged); c0/c3 resolved on utilization, c2
  unresolved (r<floor), c1 unmeasurable (below MIN_SUPPORT_N) — consistent with the frozen thresholds
  (double-centering, frozen `frozen_replication_thresholds()`). σ-honesty out-of-sample; 100%/near-100%
  coverage is the CONSERVATIVE (not over-claiming) direction — confirm it's honestly framed (the report
  flags the min-n_eff inflation caveat).
- **Instrument 4**: position-sum construction identity holds; the per-FIA-sector composition
  limitation (class grain ≠ sector tiling; no mapping on disk) is stated HONESTLY and routed to #670,
  not fabricated. Confirm the gross-miscalib gate consumes the frozen bound.
- **Frozen constants**: the report cites the exact SIGNED values; no inline re-mint.
- **Bounded-scope note** (cross-circuit slice; full breadth → #670) present.
- pyright-0 on the new script; full `tests/unit/physics/instrument_panel/` suite green (57);
  `data/` clean; no FastF1 online call; no `docs/architecture/*` touched.

## Allowed Scope
`scripts/instrument_panel_668_report.py`, `docs/physics/instrument_panel_668_gb2023q_report.md`(+json),
`tests/unit/physics/instrument_panel/test_panel_report.py`.

## Specific Exclusions
No `data/f1_data_*.db` commit; no FastF1 online; no signed-value change; no instrument-logic change
beyond the read-adapter; no leakback; no `docs/architecture/*` edit.

## Constraints the Implementation Must Respect
Strictly-pre / no leakback; Student-t coverage; consume frozen constants; no-frame-kill honest sizing;
DB-only; own-path report artifact (#632).

## Map Anchors (inbound)
- **Structural:** `src/physics/instrument_panel/` (all four); the two DBs; `frozen_constants.py`.
- **Decision anchors:** decision:split-half-unit — CROSS-CIRCUIT 2v2 (owner-ruled).
  `@grade: settled/human · leans g7`
- **Evidence:** report reproduces; no leakback; bounded-scope honest; small size stated plainly.

## Evidence Produced
57/57 tests + pyright-0 + report. Reproduce:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/instrument_panel_668_report.py`
then `... -m pytest tests/unit/physics/instrument_panel/ -q` and `git status --porcelain data/`.
Your APPROVE feeds `g7-realrun-integrate.c1` (test_panel_report.py) + `.c2` (verdict).

## Suggested Model Tier
stronger — the real-data honesty judgments (floor-not-bug, scorecard limitation, σ over-coverage
framing) are what this review must confirm, plus the no-leakback fix.

## Stop Conditions
BLOCK if: numbers don't reproduce; leakback present or the no-leakback test is vacuous; the 0.0 floor
is a bug not a genuine clip; the scorecard limitation is spun as success or fabricated; a frozen value
is re-minted; `data/` is dirty; or a FastF1 online call is made.

## Return Format
Return REVIEW_RESULT (APPROVE/BLOCK + findings + workflow feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g7-realrun-review-result.md` before ending your turn.
