# Triage recommendations — issue #662

3 candidates from execute.json triage_candidates. Delegated run: no explicit issue-filing authority in
the launch order → non-fix-now candidates are `recommend-and-defer` (surfaced to the Admiral to file).

## tc1 — ribbon._get_clean_laps pit-filter silently no-ops against DBSession  [bug]
- **What:** `src/physics/ribbon.py::_get_clean_laps` filters pit in/out laps via
  `row.get("PitInTime")` / `row.get("PitOutTime")`. `DBSession`'s `_ShimLaps` wrapper has NO
  PitInTime/PitOutTime columns (unlike a real FastF1 `Laps`), so `.get()` returns None and
  `pd.notna(None)` is False — the pit-lap filter is silently skipped when `build_session_ribbon`/
  `_get_clean_laps` runs against a store-backed DBSession.
- **Importance:** low-medium. #662 did NOT reuse `_get_clean_laps` (wrote its own minimal clean-lap
  filter precisely to sidestep this), so it is a LATENT defect, not a live one — but the next agent
  reusing that helper against DBSession would silently include pit laps.
- **Evidence:** g1-impl-result.md out-of-scope observation; ribbon.py `_get_clean_laps` + telemetry_session.py `_ShimLaps`.
- **Acceptance:** either add PitInTime/PitOutTime columns to `_ShimLaps`, or guard `_get_clean_laps` to
  detect their absence and fail loudly / use an alternative pit filter.
- **Out of scope:** #662 (which does not use the helper).
- **Disposition:** recommend-and-defer (fix-now ineligible: cold-start area in ribbon.py/telemetry_session.py,
  not adjacent to the derivation subpackage this run built; filing authority not granted this run).

## tc2 — data/segment_maps.db not gitignored  [cleanup]  — FIXED-NOW
- **What:** the G5 CLI writes a per-weekend SegmentMap store to `data/segment_maps.db`, which was not
  covered by `.gitignore` (unlike the other derived `data/` stores).
- **Disposition:** FIXED-NOW — commit **ee385edf** adds `/data/segment_maps.db` to `.gitignore` beside
  the other regenerable derived stores. Cleared the fix-now ladder (1-line diff, adjacent to the new CLI,
  verifiable by inspection, no architecture impact).

## tc3 — split-half MAX boundary drift large at p10 braking-onset boundaries  [research hardening]
- **What:** GATING-1 split-half MEDIAN boundary drift is stable (Bahrain 2.18m / Austria 3.48m << 10m),
  but the MAX drift is large (Bahrain 15.7m / Austria 80.7m), concentrated at p10 braking-zone-ONSET
  boundaries — the least-stable boundary type across field subsets (a half-sized subsample makes the p10
  onset quantile noisy).
- **Importance:** low for Build 1 (the map is MEASURED-not-wired; median stability is strong). Becomes
  load-bearing only if a downstream consumer depends on precise braking-zone boundaries.
- **Evidence:** VERDICT.md GATING-1 max-drift row + Austria diagnostic dump; g6-impl-result.md.
- **Acceptance:** tighten the p10 braking-onset estimate (larger effective sample / robuster quantile /
  pooling more laps before the split) so max drift approaches the median; re-run the split-half check.
- **Out of scope:** #662 (reported, not asserted-against, per the median-gate design).
- **Disposition:** recommend-and-defer (research hardening; multi-step; filing authority not granted this run).

## Summary
- fixed-now: tc2 (ee385edf).
- recommend-and-defer (surfaced to Admiral for filing decision): tc1 (bug, latent), tc3 (research hardening).
