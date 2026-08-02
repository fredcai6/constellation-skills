# Excursion Brief: `x6-circuit-demand-join-readiness`

## The one named question

Are the existing corner-fingerprint artifacts (data/corner_fingerprints_*.csv, data/corner_matches.csv, coast_frac_*, driver_corner_reliability_*) sufficient today to build a per-circuit corner-demand profile that a regime-capability vector can be crossed with — and what exactly is missing if not?

## Type

research

**Why this type:** artifact-readiness audit; nothing to build.

## What "answered" looks like

(a) What each artifact actually contains (columns, grain, season coverage, producing script); (b) a concrete sketch of the demand-profile join — for circuit X, the share of lap-time sensitivity attributable to each regime (power/aero/traction/braking) — and whether current artifacts support it; (c) a named gap list (e.g. "no per-corner time-weight", "2021 fingerprints missing") with sizes. Also note where the artifacts' producing code lives and whether it's promoted or scratch (.agent-work/601-cartographer, epic-601 dirs are the likely provenance).

## Budget / stop conditions

- Read-only. ~30–45 min.
- Do not regenerate artifacts.
- **Scoped nulls:** verdict on THESE artifacts; a gap is a to-build item, never "affinity impossible."

## Research excursion

- **Sources:** the CSVs themselves (data/corner_fingerprints_*.csv, data/corner_matches.csv, data/coast_frac_*.csv, data/driver_corner_reliability_2023.csv, data/entry_panel_estimates_*), their producing scripts (search scripts/, .agent-work/575-cartographer/, .agent-work/601-fantasy-league/, .agent-work/cmdr-601-active-aero-zones/, .agent-work/epic-601*), corner_fingerprints*.png for intent.
- **Findings format:** per-artifact table + join sketch + gap list, cited.

## Return

Full findings → `.agent-work/explore-physics-evo-hookup/excursions/x6-circuit-demand-RESULT.md`. Final message = short summary.
