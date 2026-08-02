# Implementer Handoff — G6 Acceptance: GATING checks + verdict

## Gate
g6 (issue #662) — the substantive falsification + verdict. Pinned interpreter:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Task
Produce the two GATING checks with REAL NUMBERS and a verdict. New files:
- `tests/unit/physics/segment_map/derivation/test_segment_map_gating.py`
- `scripts/validate_segment_map_662.py` (the validation harness that computes the numbers)
- `.agent-work/662-segment-map/VERDICT.md` (the run verdict with real numbers — this is a work-area doc,
  NOT committed)

Keep the two GATING checks as **two separately-named tests** so a failure distinguishes
`claim:map-stable` from `claim:typing-correct`.

## Environment / data
Real 2023 data IS present in this environment: telemetry store at
`C:/Programs/f1Brainz/data/telemetry_store.db`; grip_bin_obs in the MAIN-checkout
`damage_integrals.db` (G4's `fit_era_severity_mixture` locates it — reuse G4/G5 functions, do not
re-derive paths). The full pipeline is `derive.derive_segment_map(year, gp_name, "Q")`.

## GATING-1 — cross-weekend map stability (SCOPED NULL for 2023) + split-half proxy
- **State the scoped null honestly:** F1 runs each circuit ONCE per season, so there is NO second
  same-circuit 2023 weekend — the cross-weekend stability gate is a coverage NULL by construction, not an
  oversight. Assert/verify this from the 2023 calendar (`src.utils.constants get_calendar(2023)` — confirm
  no circuit repeats) and record it as a TYPED coverage-gap result, DISTINCT from "gate passed" (never
  silently green — constraint:no-frame-kill).
- **Substantive proxy (split-half within-weekend):** derive the tiling from two DISJOINT halves of the
  field's clean flying laps (e.g. even-indexed vs odd-indexed drivers) on **≥2 circuits**, and compare
  corresponding segment-boundary distances. Assert the boundary drift (median, and report max) is
  < `MAP_STABILITY_DRIFT_M` (IMPORT from `src.physics.layer2.frozen_constants`; = 10.0 m). Report the
  drift in metres per circuit. This tests derivation stability directly.
  - To derive from a driver subset, either add a MINIMAL backward-compatible `drivers: list[str] | None
    = None` filter to `reference_lap_from_store` (allowed — see Allowed Scope; the default path must be
    byte-unchanged), or build the two reference laps via the public `build_reference_lap` agnostic core
    on subset laps loaded the same way. Cite which you did.
  - Comparing boundaries across two tilings with possibly-different segment counts: match by nearest
    boundary / by ordered corner apexes — document the matching. If counts differ materially, report it
    (that itself is instability evidence).

## GATING-2 — typing spot-checks (real ground truth)
- **Bahrain 2023 Q (primary):** derive it; count **PHYSICAL corners** = collapse contiguous CORNER
  segments AND merge CORNER rows separated ONLY by a sector cut (a sector-split corner is multiple rows
  but ONE physical corner — do NOT double-count). Compare to P4-RESULT
  (`.agent-work/archive/2026-07-25-explore-ref-utilization/excursions/P4-RESULT.md`: ~14 corner arcs/lap,
  range 11–17, BIC = 15 official turns). Report the count AND the physical-corner apex locations
  (distances) so "right locations" is checkable. Assert the count is in the P4 plausible range [11, 17].
- **regime_rollup distance-share cross-check:** compute the map's corner distance FRACTION
  (sum of CORNER segment lengths / lap_length) for Bahrain and compare to `regime_rollup`'s corner
  distance-share for the same circuit (regime_rollup emits continuous distance-SHARE fractions, NOT a
  discrete count — use it as a share cross-check, cite the source). Report both fractions; they should be
  comparable (state a reasonable tolerance).
- **2nd circuit (official turn count):** derive a second 2023 circuit; count physical corners; compare to
  its KNOWN official turn count (external F1 fact — cite it, e.g. a circuit whose turn count you state).
  Report count vs official.

## Honest labels (review T3)
Label tiling-completeness + sector-nesting-exactness (already tested in g2/g3) as CONSTRUCTION checks
(they catch coverage/arithmetic bugs, NOT mis-typing). GATING-1 and GATING-2 are the substantive checks
(falsified by unstable or physically-wrong maps). Say this in VERDICT.md.

## No-frame-kill
A clean scoped null on any check (the cross-weekend null; or a circuit whose data is absent) is a
COMPLETE deliverable — report it with what was and was NOT tested; do NOT fabricate a second weekend or a
number. Tests skip cleanly (green) when data is absent; the numbers live in VERDICT.md.

## Allowed Scope
`test_segment_map_gating.py`, `scripts/validate_segment_map_662.py`, `.agent-work/.../VERDICT.md`. A
MINIMAL backward-compatible `drivers=` filter on `src/physics/segment_map/derivation/reference_lap.py`
IS pre-authorized IF needed for split-half (default behavior byte-unchanged; add/adjust its test).
Read (not edit) the rest of the derivation modules, `regime_rollup.py`, P4-RESULT.md, `constants.py`.

## Specific Exclusions
- Do NOT edit docs/architecture/* or any existing segment_map runtime/store/identity file or
  frozen_constants.py. Do NOT retune CORNER_CURVATURE_THRESHOLD even if a spot-check is off — if the
  typing looks wrong, REPORT it (route to structural work / float), never silently retune (frozen-constants).

## Constraints
- MAP_STABILITY_DRIFT_M imported (no literal 10.0). Count PHYSICAL corners (merge sector-split rows) for
  the P4/official comparisons. DB-only.

## Map Anchors (inbound)
- **Structural:** test_segment_map_gating.py, validate_segment_map_662.py (NEW); P4-RESULT.md (reference);
  regime_rollup.py (distance-share); frozen_constants.MAP_STABILITY_DRIFT_M.
- **Decision anchors:**
  - decision:stability-scoped-null-split-half — cross-weekend stability is a scoped null for 2023;
    split-half within-weekend is the substantive proxy + report the gap.
    @grade: guess · leans g6 · settle: enumerate 2023 calendar (no circuit repeats)
- **Evidence expectations:** claim:map-stable (split-half drift < MAP_STABILITY_DRIFT_M);
  claim:typing-correct (physical corner count + locations match P4 + official turn counts).
- **Map confidence flags:** integration checks over G1–G5 — a failure may localize to an earlier gate.

## Deliverable Path Check
- **Committed:** `test_segment_map_gating.py`, `scripts/validate_segment_map_662.py` — `git check-ignore`
  exits 1. **Local-only:** `.agent-work/662-segment-map/VERDICT.md` (gitignored work area — not in diff).

## Required Evidence
- pytest `test_segment_map_gating.py` green (skips-when-data-absent are green) on the pinned interpreter.
- `simplification_limits --paths scripts/validate_segment_map_662.py` clean.
- `VERDICT.md` with REAL numbers: split-half drift (m) per circuit, physical corner count + apex
  locations for Bahrain vs P4, corner distance-share vs regime_rollup, 2nd-circuit count vs official
  turn count, and the honest scoped-null statement for cross-weekend stability. The numbers must
  reproduce when `validate_segment_map_662.py` is re-run.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_segment_map_gating.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths scripts/validate_segment_map_662.py
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/validate_segment_map_662.py   # prints the numbers
```

## Suggested Model Tier
Stronger — the physical-corner collapse + honest scoped-null + real-data interpretation are judgment-heavy.

## Authority
Scoped-null + split-half proxy + physical-corner-merge + P4/official references are DECIDED
(Admiral-ratified). You MAY decide the split (even/odd drivers etc.), the 2nd circuit, matching method,
and tolerances (state them).

## Stop Conditions
Stop and return if: a real-data check needs editing a reviewed module beyond the pre-authorized `drivers=`
filter; the split-half can't be run; a frozen threshold looks wrong; the typing is materially off (report
it, do not retune).

## Return Format
IMPLEMENTER_RESULT to `.agent-work/662-segment-map/g6-impl-result.md`: slice, files, test mode, evidence
(pytest + simplification + the validate script output), the split-half drift numbers, physical corner
count + locations vs P4, distance-share vs regime_rollup, 2nd-circuit count vs official, the scoped-null
statement, assumptions, stop conditions, out-of-scope, workflow feedback. **Deliver a concise summary
(verdict + result path + the real gating numbers) to "cmdr-662" via SendMessage before ending your turn.**
