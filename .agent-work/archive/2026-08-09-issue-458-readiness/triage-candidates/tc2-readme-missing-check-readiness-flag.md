# Triage Recommendation: README.md doesn't document `--check-readiness`

## Classification
missing doc

## Source checklist/artifact
- spine.json triage_candidates[tc2], raised at `reconcile`; originally noted by g1's independent
  reviewer as a non-blocking observation during REVIEW_RESULT

## Structural anchor
README.md (## Install section) | none — no map exists in this repo

## Cartographer mismatch class
none

## Problem
`scripts/install_constellation.py` gained a new `--check-readiness` flag this run (issue #458),
documented in its own `--help` text but not in README.md's `## Install` section, where every other
installer flag/workflow is documented (`--dry-run`, `--wire-hooks`, `--force`, etc.).

## Current truth
README.md's Install section walks through install invocations and flag behavior in prose; the new
flag is absent from it. The flag's own `--help` text is complete and accurate.

## Desired/future concern
A short paragraph or bullet in README.md's Install section describing `--check-readiness`: what it
answers, that it is report-only (never repairs, never writes settings.json), and its exit-code
convention — mirroring the existing paragraph for the hook-wiring report behavior.

## Evidence
- `scripts/install_constellation.py --help` shows `--check-readiness` with a complete description.
- README.md's Install section (as of this run) has no mention of it.
- g1's reviewer flagged this exact gap as non-blocking during REVIEW_RESULT.

## Impact
Low — the flag is self-documenting via `--help`, and README.md already documents the closely
related `--wire-hooks`/hook-wiring-report behavior it complements, so a reader scanning README for
"how do I check if I'm set up" would not find this new flag without already knowing to look.

## Suggested scope
One short section/paragraph addition to README.md's Install section. Bounded, single file.

## Non-goals
Does not change `install_constellation.py` itself or add new functionality.

## Acceptance criteria
- [ ] README.md's Install section names `--check-readiness`, what it answers, and its report-only
      guarantee (never writes settings.json).

## Recommended priority
low

**Reason:** Cosmetic/discoverability gap, not a correctness issue; the flag works and is tested
regardless of whether README mentions it.

## Related artifacts
- `scripts/install_constellation.py` (`--check-readiness`, this run's issue #458)
- README.md `## Install`

## Disposition
recommend-and-defer

**Detail:** This run's launch order's file ownership is `scripts/install_constellation.py` and its
tests only; README.md is outside that scope, and Inherited Latitude does not name issue-filing
authority. Bounded enough to be a fix-now candidate on the ladder (small diff, adjacent to current
scope, trivially verifiable by reading) except for the file-ownership boundary itself, which this
run does not have latitude to cross without asking. Deferred to the Admiral.

## Issue creation authority
ask user
