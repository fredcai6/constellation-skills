# Triage Recommendation: `collect_evo_data.py --dry-run requires --worklist (undocumented breaking change)`

## Classification
`missing doc | tooling`

## Source checklist/artifact
- `.agent-work/cmdr-603/execute.json` tc1 (flagged from g2-verify-report), issue #603 launch order Pre-Rulings ("a dry run: `py scripts/collect_evo_data.py --seasons 2026 --dry-run` shows the worklist")

## Structural anchor
`scripts/collect_evo_data.py` (function `collect_evo_data`, ~line 716-718)

## Cartographer mismatch class
none

## Problem
`--dry-run` used to (per prior commander-facing launch-order language) print a worklist standalone. It now raises `ValueError: --dry-run requires --worklist` unless a pre-built worklist JSON is supplied. Any Commander/Admiral following the still-circulating "run --dry-run alone to preview" instruction hits an immediate crash instead of a preview.

## Current truth
`collect_evo_data(dry_run=True, worklist_path=None)` raises at line ~718. The only way to preview a plan now is to already have a worklist file (produced how? not documented in `--help`), or — the workaround this run used — call the pure `src.utils.constants.get_weekend_sessions(season, gp)` directly, which is a strictly equivalent (and stronger, since it's the exact function the live path consults) substitute for classification-only previews.

## Desired/future concern
Either (a) restore a standalone `--dry-run` (no `--worklist` needed) that builds the plan the same way the live path does, or (b) update `--help` / any commander-facing docs to state the `--worklist` requirement and point at `get_weekend_sessions` as the offline-preview substitute.

## Evidence
- `py scripts/collect_evo_data.py --seasons 2026 --dry-run` → `ValueError: --dry-run requires --worklist` (this run, 2026-07-12).
- `.agent-work/601-fantasy-league/launch-orders/cmdr-603.md` line 15 assumes bare `--dry-run` works.

## Impact
Low severity (a working substitute exists and was used), but it's a repeat-cost paper cut: every future launch order that says "dry-run to preview" will hit the same crash until either the code or the doc catches up.

## Suggested scope
Small: either restore no-worklist dry-run behavior, or add a `--help` line + one doc mention of the `--worklist` requirement and the `get_weekend_sessions` fallback.

## Non-goals
Not a request to redesign the worklist format or the collector's planning architecture.

## Acceptance criteria
- [ ] `py scripts/collect_evo_data.py --seasons 2026 --dry-run` either works standalone again, or fails with a `--help`-documented, non-surprising message.
- [ ] Launch-order-adjacent doc/template no longer implies bare `--dry-run` works if the requirement stays.

## Recommended priority
`low`

**Reason:** Papercut with a known working substitute; not blocking any current work.

## Related artifacts
- `.agent-work/601-fantasy-league/cmdr-603-report.md` (this run's report, "Note on the launch order's dry-run step")

## Disposition
`recommend-and-defer`

**Detail:** Filing authority unclear this run — the cmdr-603 launch order's Inherited Latitude grants "run collection, read/verify the DB, write your report" only; issue creation is not named, and any code change explicitly floats to the Admiral. Deferred rather than filed.

## Issue creation authority
`ask user`
