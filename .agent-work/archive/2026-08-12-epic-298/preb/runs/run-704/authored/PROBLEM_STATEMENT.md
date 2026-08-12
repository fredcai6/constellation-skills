# Problem statement — issue #704

**Work id:** `issue-704-dedup-axis-grouping`
**Engagement:** PLANNING ONLY. Implementation is a separate, later engagement. No source, test, or
doc file in this repo is modified by this run; artefacts under `.agent-work/` are the sole exception.

## The ask

`src/physics/instrument_panel/replication.py` computes the same thing twice. `_axis_means()`
(`:103-128`) and `main_effect_margin_uncertainty()` (`:408-446`) each make one pass over the
`(driver, class) -> value` grid, accumulating a **per-driver-row** aggregate and a
**per-class-column** aggregate of `float(value)`. `_axis_means` accumulates sums and counts and
divides; `main_effect_margin_uncertainty` accumulates the value lists themselves and takes a
standard error. #704 asks for a small shared helper to remove the duplication, with all
`instrument_panel` tests green, pyright-0, and **byte-identical behavior**.

## Protected intent — what must NOT change

The module is the load-bearing instrument of the #668 panel and carries an explicit Protected
Intent in its own docstring:

- **The golf-correction is double-centering.** `residual[d,c] = v[d,c] - driver_mean[d] -
  class_mean[c] + grand_mean`. The formula is untouchable; so is `per_driver_demean` as the
  deliberately-wrong negative control.
- **F12-independence.** The pure core imports no frozen `REPLICATION_*` constants; every threshold
  is injected via `ReplicationThresholds`, and `frozen_replication_thresholds()` is the single
  production seam. The dedup adds no import and no constant.
- **No-frame-kill.** Every class gets a complete verdict; `None` means honestly-undefined, never a
  fabricated number. Unchanged.
- **The owner-signed `REPLICATION_*` frozen set** (`decision:replication-frozen-set-signed`,
  `@grade: settled/human`) is out of scope, as #704 states.

## Capability (unchanged)

The system measures whether a driver's characteristic pattern *across* severity classes replicates
across an independent split of the data, after removing both main effects. #704 changes **no**
capability, event, or constraint — it is a structural change behind a private seam.

## What the interrogation settled

Full record: `.agent-work/issue-704-dedup-axis-grouping/INTERROGATION_RECORD.json`
(`verify_interrogation.py` exit 0, mode=delegated, 7 questions).

**Facts (resolved from code):**

1. **The duplication is real and the seam is private.** Nothing outside `replication.py` references
   `_axis_means` (grep: 3 hits, all in-file). `per_driver_demean` is a third consumer that already
   calls `_axis_means` and discards two thirds of its result.
2. **The blast radius is closed and small.** Importers: `scripts/instrument_panel_668_report.py:71-75`,
   `scripts/run_season_panel_670.py`, `src/physics/pilot/pipeline.py` (lazy `run_panel`). The one
   source-text guard test (`tests/unit/physics/instrument_panel/test_panel_corpus.py:243-267`) greps
   `scripts/run_season_panel_670.py`, **not** `replication.py` — a new private helper cannot trip it,
   provided it is not named one of the eight forbidden public names.
3. **Byte-identity is a real constraint, not a slogan.** Float accumulation is order-sensitive, so
   the implementation must (a) keep per-axis accumulation in grid-iteration order, (b) keep the
   grand mean as its own single left-to-right pass — never re-derived from concatenated driver rows,
   never `math.fsum` — and (c) preserve per-axis list order, because `_main_effect_se` feeds it to
   `np.std(ddof=1)`.
4. **Evidence path.** `simplification_limits` (strict) + focused region suite + pyright-no-new-errors.
   Measured this session: the agent-shell `py` is the codex runtime with neither `pytest` nor
   `radon`; `--file-lines-only` passes, the strict check does not run there. **Every test-run attempt
   this session was blocked by harness permission**, so the green baseline is *not* an inherited fact
   — capturing it is gate-0 work.

**Decisions (recorded as asked, then self-decided under the engagement's standing no-human
instruction — a cited frozen-order sign-off, not a live human confirmation):**

- **Helper shape:** grouped value lists, `_axis_groups(grid) -> (driver_rows, class_cols)`. Lists are
  the superset both callers can be served from; sums+counts would fail the margin caller, which needs
  the values themselves for a std.
- **Proceed vs. defer:** proceed, with a deliberately surgical diff (one private helper, two call
  sites, zero public surface change) so the review cost #704 warns about is answered by evidence
  rather than by re-derivation.
- **Regression scope:** all six `tests/unit/physics/instrument_panel/` files + `tests/unit/physics/pilot/`
  + a before/after exact-equality identity harness. Not the full physics suite.

## Out of scope

- Any change to the signed frozen values, `ReplicationThresholds`, or the double-centering method.
- Any change to the public API of `replication.py` (`__all__` is frozen as-is).
- Regenerating `docs/physics/instrument_panel_668_gb2023q_report.md` or any panel report — behavior
  is byte-identical, so no artifact changes.
- Deduplicating anything else in the module (`_class_support`, `_pearson_r`, `_resolved_grid`).
- The optional micro-win of letting `per_driver_demean` skip the grand/class computation it discards:
  **explicitly declined** — it widens the diff on a Protected-Intent module for no measurable gain.

## Named residual risk

A reviewer must still re-read a Protected-Intent module for a cosmetic gain. That is the cost #704
itself flags, and this plan does not pretend it away — it minimises it (surgical diff) and pays it
down with machine-checkable identity evidence.
