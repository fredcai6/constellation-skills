# Triage Recommendation: `collect_evo_data.py --gp accepts only one value (undocumented in a way that invites a silent-wrong multi-GP call)`

## Classification
`missing doc | tooling`

## Source checklist/artifact
- `.agent-work/cmdr-603/execute.json` tc2 (flagged from g1-collect), issue #603 launch order Pre-Rulings ("use --gp to restrict to one GP")

## Structural anchor
`scripts/collect_evo_data.py` line ~1149 (`parser.add_argument("--gp", type=str, default=None, ...)`)

## Cartographer mismatch class
none

## Problem
`--gp` is declared `type=str` (single value), but a launch order can plausibly be read as supporting `--gp <A> --gp <B>` in one invocation (this run's own cmdr-603 launch order example implied restricting to two GPs via the flag). argparse silently keeps only the last `--gp` value with no error — a Commander who tried that literally would silently under-collect one of the two requested GPs with no warning.

## Current truth
Single-value only; two sequential invocations (one `--gp` each) is the only correct way to restrict to two specific GPs without also sweeping every other calendar event (including not-yet-happened future rounds).

## Desired/future concern
A one-line `--help` clarification ("single GP only; for multiple, run once per GP") would have saved a moment of doubt this run and prevents a future silent under-collection if someone runs the two-value form without checking.

## Evidence
- `scripts/collect_evo_data.py:1149` `type=str, default=None` — no `nargs="+"` or list support.
- `.agent-work/601-fantasy-league/launch-orders/cmdr-603.md` line 15's phrasing is ambiguous enough to invite the wrong call shape.

## Impact
Low-medium: doesn't affect this run (I ran two sequential invocations correctly), but a future run that doesn't catch the single-value nature could silently miss a round with zero error signal — argparse just keeps the last `--gp`.

## Suggested scope
One-line `--help` string change: `"Restrict to a single GP (e.g. Bahrain). For multiple GPs, run the script once per GP."`

## Non-goals
Not a request to add multi-GP support to `--gp` itself (single-GP restriction is arguably a deliberate safety rail against accidentally sweeping the whole calendar).

## Acceptance criteria
- [ ] `--help` text makes the single-value, run-once-per-GP contract explicit.

## Recommended priority
`low`

**Reason:** No incident this run; preventative doc clarification only.

## Related artifacts
- `.agent-work/601-fantasy-league/cmdr-603-report.md` (this run's report, Triage candidates section)

## Disposition
`recommend-and-defer`

**Detail:** Filing authority unclear this run — same reasoning as tc1: cmdr-603's Inherited Latitude does not name issue-filing, so deferred to the Admiral rather than filed.

## Issue creation authority
`ask user`
