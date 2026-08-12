# Problem statement — issue #704 (dedup axis-grouping helper in `replication.py`)

Work id: `issue-704` · Commander run · **PLANNING ONLY** (execute is a separate engagement)
Base: `main` @ `3541d292` (detached HEAD; no work branch — branch creation declined by the
permission layer and unnecessary for a planning-only run)

## The ask, restated

`src/physics/instrument_panel/replication.py` groups a `(driver, class) -> value` grid along its
two axes in **two separate places**:

| Site | Lines | What it accumulates | Consumer |
|---|---|---|---|
| `_axis_means` | 111–128 | per-driver running **sum + count**, per-class running **sum + count**, grand total + count | `grand_two_way_center` (the load-bearing double-centering), `per_driver_demean` (negative control) |
| `main_effect_margin_uncertainty` | 425–429 | per-driver **list of values**, per-class **list of values** | `_main_effect_se` (std/√n over each axis) |

Both loops are `for (driver, class_id), value in grid.items(): float(value)` then bucket by
`driver` and by `class_id`. That is the duplication triage tc2 flagged (Fowler duplicated code,
non-blocking g6 finding). A shared one-pass axis-grouping helper removes it.

## Protected intent (must survive unchanged)

1. **The double-centering method itself** — `residual = v - driver_mean - class_mean + grand_mean`,
   `decision:golf-correction-is-double-centering` (`@grade: settled/measured`). Out of scope per the
   issue.
2. **The signed frozen values** — `REPLICATION_*` in `src/physics/layer2/frozen_constants.py`,
   `decision:replication-frozen-set-signed` (`@grade: settled/human`). Untouched: the helper sits
   entirely below the injected-thresholds seam.
3. **F12-independence** — the pure core imports no `REPLICATION_*` constant directly;
   `frozen_replication_thresholds()` stays the single production seam. A new private helper must not
   import `frozen_constants`.
4. **Byte-identical behavior** — the issue's own acceptance word. Read strictly: *bit-identical
   floats*, not "close enough". `replication.py` feeds threshold comparisons (`r >= r_floor(n)`,
   `top_r - second_r >= channel_tie_margin`) whose verdicts are categorical, and the committed
   `docs/physics/instrument_panel_668_gb2023q_report.md` is a canonical promoted artifact.
5. **`per_driver_demean` stays the negative control** — still routed through the same axis means,
   still documented as the WRONG correction.
6. **No-frame-kill** — every class keeps a complete verdict; undefined stays `None`, never a
   fabricated zero.

## The load-bearing finding — naive accumulation is NOT `sum()`

The obvious dedup ("collect per-axis value lists once, take `sum(vals)/len(vals)`") **silently
changes the numbers**. Measured on this machine's `py` (CPython 3.12.13 in the agent shell; the
repo's pinned interpreter is 3.14 — same behavior, the change landed in 3.12):

```
running loop  t=0.0; for v in [1e16, 1.0, -1e16, 1.0]: t += v   ->  1.0
builtin       sum([1e16, 1.0, -1e16, 1.0])                      ->  2.0
```

CPython ≥3.12 gives `builtins.sum` **Neumaier compensated summation** for floats, so it is *more*
accurate than — and therefore not equal to — the naive `+=` accumulation `_axis_means` performs
today. On 20 000 randomized ragged grids, `sum(vals)/len(vals)` disagreed with the current running
accumulation in **10 356 / 20 000 cases (52%)**; `float(np.mean(vals))` disagreed in **8 471**
(numpy uses pairwise summation). Typical relative gap on benign data ~1e-13 — invisible in a
`pytest.approx` test, fatal to "byte-identical", and capable in principle of flipping an
`r >= floor` verdict that sits exactly on the boundary.

So the dedup has exactly one real hazard, and it is not the grouping — it is **which mean
formulation the deduped helper hands back**. The plan is built around pinning that.

Two order-preservation corollaries the helper must also respect:

- **Per-key value order** — each driver row / class column must accumulate in `grid.items()` order,
  since float addition is not associative and `_main_effect_se`'s `np.std(ddof=1)` is order-sensitive.
- **Key insertion order** — the returned `driver_mean` / `class_mean` dicts currently key in
  first-encounter order. No current consumer iterates them (both do keyed lookups), but preserving
  it is free and keeps the change genuinely inert.

## Blast radius (verified, not assumed)

- `_axis_means`, `_main_effect_se`, `_class_support` are **module-private with zero external
  references** — `grep -rn` across the repo returns nothing outside `replication.py`. The helper's
  shape is unconstrained by any other file.
- Real importers of `replication.py`: `scripts/instrument_panel_668_report.py`,
  `scripts/run_season_panel_670.py`, and the four `tests/unit/physics/instrument_panel/` test
  modules. `src/physics/layer2/frozen_constants.py` references it in prose only.
- Nothing in `src/evo_predictor/`, `src/latent_power/`, or `src/compound_prior/` imports it —
  `constraint:physics_region_no_evo_import` is unaffected in both directions.
- `data/reference_utilization.db` is **absent from this checkout**, so the end-to-end panel report
  (`docs/physics/instrument_panel_668_gb2023q_report.md`) **cannot be regenerated locally**. The
  byte-identical proof therefore has to come from a numeric characterization harness plus the
  existing suite — planned as such, not hand-waved. (`tests/.../test_panel_corpus.py` does run the
  season panel end to end on a *synthetic* corpus, including
  `test_corpus_panel_reproduces_identically` — that is the closest available integration net and it
  does exercise `compare_channels_by_class`.)

## Decisions a human would have been asked (no human reachable — decided here)

| # | Question | Decision taken | Why |
|---|---|---|---|
| D1 | Is a cosmetic dedup worth re-triggering full review on the panel's load-bearing module at all? | **Do it, but recommend shipping it batched into the next planned touch of `replication.py` rather than as a standalone PR.** | The issue's own out-of-scope note says exactly this. The dedup is ~6 lines of grouping and is close to net-neutral on line count; its real value is drift-proofing (one site gaining a filter or a conversion the other lacks). That value is real but small, and the review cost is fixed. Recorded as a triage/decision candidate, not silently resolved. |
| D2 | Does "byte-identical" mean bit-identical floats or behaviorally equivalent? | **Bit-identical.** | Downstream verdicts are categorical and the emitted report is a promoted artifact; the weaker reading would let the compensated-`sum()` trap through. |
| D3 | Should the helper return value **lists** (so `_main_effect_se` can consume them) or sums+counts (so `_axis_means` stays a division)? | **Lists, plus the grand total/count accumulated in the same pass.** | Lists are the common denominator — the SE genuinely needs the values, and a sums+counts helper would dedup nothing at the second site. The grand total/count rides along so the grand mean stays the *literal* expression it is today. |
| D4 | Do the means get computed with `sum()`, `np.mean`, `statistics.fmean`, or an explicit loop? | **Explicit sequential loop, in a named private helper, with a comment stating why.** | The measurement above. This is the whole risk of the issue. |
| D5 | Is the naive-accumulation constraint durable enough to record in the map? | **Yes — a `@grade: settled/measured` decision bullet in the `instrument_panel` section of `docs/architecture/packets/physics.md`.** | It is precisely a fact a future simplify-pass would rediscover the hard way ("why isn't this `np.mean`?"). Recording it is what stops the next agent from undoing this one. Cartographer owns the edit at reconcile. |
| D6 | Should `_class_support`'s O(classes × cells) rescan be folded into the same helper? | **No — out of scope; file as a triage candidate.** | The issue names the `_axis_means` / `main_effect_margin_uncertainty` pair. Widening to support-grouping touches `_replicate_channel`, the actual verdict path. Deliberately deferred, not missed. |
| D7 | Should the run add a committed golden-values fixture? | **No.** The hex snapshot lives in `.agent-work/issue-704/` as run evidence; the durable guard is a regression **test** that fails if a compensated/vectorized mean ever returns. | A committed fixture would add a maintenance surface for a change whose whole point is that nothing changed. |

## Out of scope

- Any change to the signed frozen values or to the double-centering method (issue text).
- `_class_support` / support-grid rescan dedup (D6 → triage).
- `sector_scorecard.py`, `variance_decomposition.py`, the panel scripts, the emitted report.
- Regenerating `docs/physics/instrument_panel_668_gb2023q_report.md` (store absent; behavior
  unchanged so the artifact stands).

## Map confidence

`struct:physics.instrument_panel` is `confidence: high`, reconciled 2026-07-27 under #671, and its
packet section matches the source I read (three instrument modules, injected thresholds, the three
decision anchors). No stale/disputed area this ask depends on. No scout step needed.
