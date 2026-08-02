# Implementer Handoff — g6-finalize-implement

## Gate
g6-finalize-implement (#668 instrument panel). Worktree `C:/Programs/f1brainz-wt/epic659-668`,
branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Task
The F12 set is OWNER-SIGNED. Three cohesive pieces:
1. **Append the signed `REPLICATION_*` frozen set** to `src/physics/layer2/frozen_constants.py`
   (replace the existing DEFERRED note at ~lines 35-43).
2. **Wire the replication module to CONSUME the frozen set** (a factory that builds the injected
   thresholds from the frozen constants — the module keeps taking injected params, but gains a
   frozen-backed constructor).
3. **Refinement 2 (owner/Admiral-endorsed)**: carry the double-centering **main-effect
   estimation uncertainty** into the σ-honesty check, and **surface any class too thin to center
   reliably**.

## Signed values (freeze EXACTLY these — an owner signature; do NOT alter)
Append to `src/physics/layer2/frozen_constants.py`, mirroring the existing `SECTOR_CALIB_*`
block's in-place-documented style, with a freeze-date/author note ("2026-07-26, Fred — owner
signature; #668 panel F12 pre-registration, see F12_PREREGISTRATION.md"):
- `REPLICATION_MIN_SUPPORT_N: float = 15.0` — per-observation `n_points` floor; an observation
  below it is excluded before splitting. Grounded in the 4-circuit support gap (c1 ~0-5 excluded;
  c3 ~25 / c0,c2 >=112 kept).
- `REPLICATION_THRESHOLD: float = 0.5` — base split-half agreement floor on the double-centered
  interaction residual. UNIFORM across BOTH channels (not axis-differentiated — equal footing for
  a fair time-vs-energy comparison; owner-accepted).
- `REPLICATION_R_FLOOR_CAP: float = 0.7` and `REPLICATION_R_FLOOR_SUPPORT_REF: float = 100.0` —
  the support-scaling `r_floor(n) = REPLICATION_THRESHOLD + (CAP − THRESHOLD) *
  clip((SUPPORT_REF − n)/SUPPORT_REF, 0, 1)` (thin classes need a higher bar, capped at 0.7).
- `REPLICATION_CHANNEL_TIE_MARGIN: float = 0.1` — a channel wins a class iff its r ≥ r_floor(n)
  AND it beats the other channel by this Δr; else unresolved; a tie defaults to `utilization`.
- Document (in the block's docstring, as method registration — these two are METHOD choices,
  not tunable scalars): golf-correction = DOUBLE-CENTERING (both margins, interaction residual);
  split-half unit = CROSS-CIRCUIT 2-vs-2 over the available circuits.
Discipline note (repeat the module's existing F12 discipline): changing ANY value requires a NEW
named set + a full re-run; never a silent edit.

## Wire the replication module to consume the frozen set
In `src/physics/instrument_panel/replication.py`, add a factory (e.g.
`frozen_replication_thresholds() -> ReplicationThresholds`) that builds the injected
`ReplicationThresholds` dataclass from the frozen constants above (import them from
`src/physics/layer2/frozen_constants.py` — do NOT re-mint literals). The pure core keeps taking
injected params (tests still inject synthetic values); this factory is the production wiring.

## Refinement 2 — main-effect uncertainty in σ-honesty + thin-class surfacing
Double-centering removes estimated driver and class MAIN EFFECTS; those estimates are themselves
noisy (especially on a thin/unbalanced grid — GB's c1 is near-empty). Two additions:
- **Widen the σ-honesty margin by the margin-removal (main-effect estimation) uncertainty.** In
  the σ-honesty check (does the held-out half fall within the other half's predictive-t
  interval), the interval's scale must ALSO carry the standard error of the removed driver+class
  means (add in quadrature to the cell's stated σ before building `predictive_t`). A cell must
  replicate within its stated σ *including* the margin-removal noise. Keep it Student-t / OOS.
- **Surface thin classes.** A class whose main-effect estimate rests on too few points to center
  reliably (below `REPLICATION_MIN_SUPPORT_N` per half, i.e. c1) is flagged in the result as
  `thin_class` / `center_unreliable` — a documented limitation, not a silent drop (no-frame-kill).
Add unit tests: (a) the widened margin behaves correctly (a cell with a thin main-effect estimate
gets a wider interval → higher coverage, not spuriously "over-claiming"); (b) a thin class is
surfaced/flagged, not silently dropped.

## Allowed Scope
- EDIT `src/physics/layer2/frozen_constants.py` (append the signed set; replace the DEFERRED note).
- EDIT `src/physics/instrument_panel/replication.py` (add the factory + refinement 2).
- CREATE `tests/unit/physics/instrument_panel/test_replication_frozen_constants.py`.
- EDIT `tests/unit/physics/instrument_panel/test_replication_channel.py` (add refinement-2 tests).

## Specific Exclusions
- Do NOT change any SIGNED value (it's an owner signature). Do NOT re-mint the SECTOR_CALIB_* or
  FINGERPRINT_* constants. Do NOT touch #660/#664/#666/#667 producers beyond the frozen_constants
  append. Do NOT read a real DB in these unit tests. Do NOT add a fitted interaction term (double-
  centering stays a data transform). Do NOT touch `data/f1_data_*.db`.

## Constraints
- Values EXACTLY as signed. No inline literals in the consumer (import from frozen_constants).
- σ-honesty stays OUT-OF-SAMPLE + Student-t. pyright-0. Existing 18 replication tests + 7 variance
  + 11 scorecard tests must stay green.

## Map Anchors (inbound)
- **Structural:** `src/physics/layer2/frozen_constants.py` (append); `src/physics/instrument_panel/replication.py` (factory + refinement 2).
- **Constraints:** constraint:no-inline-literals; constraint:no-baked-normality; constraint:no-frame-kill.
- **Decision anchors:** decision:replication-deferred — finalized with owner-signed values.
  `@grade: settled/human · leans g6`

## Deliverable Path Check
- **Committed** — `src/physics/layer2/frozen_constants.py` (edit),
  `src/physics/instrument_panel/replication.py` (edit),
  `tests/unit/physics/instrument_panel/test_replication_frozen_constants.py` (new),
  `test_replication_channel.py` (edit). All committed; `git check-ignore` exits 1.

## Required Evidence
- LOAD-BEARING: `test_replication_frozen_constants.py` passes (named set present with EXACT
  signed values; the replication module consumes them via the factory).
- LOAD-BEARING: refinement-2 tests pass (widened σ-honesty margin; thin-class surfaced).
- LOAD-BEARING: pyright-0 on both edited modules; the full instrument_panel test suite green.
- Confirmatory: `git diff src/physics/layer2/frozen_constants.py` shows only the append + the
  DEFERRED-note replacement.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_replication_frozen_constants.py tests/unit/physics/instrument_panel/test_replication_channel.py -q
```

## Suggested Model Tier
stronger — touches the frozen-constant discipline (owner signature) + the load-bearing σ-honesty
path; exactness and no-inline-literal discipline matter.

## Authority
The signed values are DECIDED by the owner — freeze exactly, never alter. Refinement 2's method
(quadrature-add of main-effect SE to the σ-honesty scale; thin-class surfacing) is DECIDED
(Admiral-endorsed). STOP and return if a signed value seems miscalibrated (do NOT change it — the
commander re-floats) or a real DB read seems required.

## Stop Conditions
Stop and return if: a signed value must change, scope must be exceeded, a real DB read is needed,
or the refinement-2 margin cannot be added without a fitted interaction term.

## Return Format
Return IMPLEMENTER_RESULT (slice, files, evidence, assumptions, stops, out-of-scope, workflow
feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g6-finalize-implement-result.md` before ending
your turn — that file IS the deliverable.
