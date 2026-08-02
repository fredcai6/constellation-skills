# Triage Recommendation: `Operator's personal Claude Code MEMORY.md carries the actual stale evo_predictor description`

## Classification
`ungrounded claim/decision` (a persisted claim about the codebase that is no longer true; not a repo doc)

## Source checklist/artifact
- execute.json triage_candidates tc2 (flagged during cmdr-602 g2-claude source verification, 2026-07-12)

## Structural anchor
`none` — the file in question is not part of this git repository. Path (outside repo):
`C:\Users\fredc\.claude\projects\C--Programs-f1Brainz\memory\MEMORY.md`, sections "## evo_predictor Architecture"
and "## Key Files (evo_predictor)".

## Cartographer mismatch class
`none` (out of Cartographer's scope — not a repo artifact)

## Problem
Issue #602's premise ("CLAUDE.md still describes the retired 24-parameter vector / scorer.py / ranker.py path")
is factually false for `CLAUDE.md` itself — see the sibling `fixed-now`-adjacent work this run already did
(added a source-verified architecture pointer to `CLAUDE.md`, PR #611). But the underlying concern that motivated
the issue is real: the operator's own Claude Code session memory file DOES still carry the stale 24-param
architecture description, and that file is auto-loaded into every session's context for this project — meaning
every future agent session (including this one) still gets fed the stale claim as background context, regardless
of what `CLAUDE.md` now says.

## Current truth
`MEMORY.md`'s "## evo_predictor Architecture" section (as loaded into this very session's system prompt)
states: 24-parameter vector (indices, sw_* weights etc.), `models.py`, `scorer.py` as `score_drivers(features,
params, form_drop_worst=2)`, `ranker.py` as `rank_cutoff at params[15]`. All of this describes the retired
pre-#602-era path. The live architecture (verified 2026-07-12, see PROBLEM_STATEMENT.md) is the 3-stage
`sampled_runtime.py` simulator over 12 latent-power modules with Bradley-Terry field solve + precision-weighted
fusion; `ranker.py` does not exist; `scorer.py`'s current content is unrelated helpers.

## Desired/future concern
The operator's MEMORY.md "evo_predictor Architecture" and "Key Files (evo_predictor)" sections should be updated
or retired to reflect the live architecture, so future sessions aren't fed the stale claim as background context.
This is genuinely outside any Commander's git-repo file-ownership fence — it is a personal Claude Code memory
file, not a repo artifact, and no launch order this epic has issued scopes a Commander to edit it.

## Evidence
- The MEMORY.md content quoted verbatim in this session's own system-reminder context block (2026-07-12).
- `.agent-work/cmdr-602/PROBLEM_STATEMENT.md` — full live-architecture verification trail.

## Impact
Every future Claude Code session on this repo (not just Commander runs) will keep receiving the stale
evo_predictor description as auto-loaded context until the memory file itself is corrected — this is the actual
vector that motivated issue #602, and #602 as scoped (repo files only) cannot close it.

## Suggested scope
The operator (fredcai6), the next time they are directly at the keyboard, updates or retires the stale sections
of their MEMORY.md — likely a small one-file edit mirroring the CLAUDE.md pointer added in PR #611. Alternatively,
the Admiral could ask a future run explicitly scoped (with an updated launch order naming the memory file as
in-fence) to do it.

## Non-goals
No Commander or crew should silently edit the operator's personal memory file outside an explicit launch-order
grant to do so — it is user-personal state, not repo state, and out of every current fence.

## Acceptance criteria
- [ ] MEMORY.md's "## evo_predictor Architecture" / "## Key Files (evo_predictor)" sections no longer describe
      the retired 24-param/scorer.py/ranker.py path as current
- [ ] Sections reflect (or point to CLAUDE.md, which now reflects) the live sampled_runtime.py architecture

## Recommended priority
`medium`

**Reason:** Not urgent (no production/prediction impact), but it is the actual root cause of the misleading-agent
risk issue #602 was trying to close, and will keep recurring every session until fixed.

## Related artifacts
- `CLAUDE.md` (PR #611 — the repo-side fix already landed)
- `.agent-work/cmdr-602/PROBLEM_STATEMENT.md`

## Disposition
`recommend-and-defer`

**Detail:** Filing authority is unclear for a non-repo target (a GitHub issue against this repo cannot bind a
change to a file outside the repo), and no launch order has scoped any Commander to touch the operator's personal
memory store. Recorded here for the Admiral to relay directly to the human (fredcai6) rather than filed as a
GitHub issue.

## Issue creation authority
`ask user` (relay directly, not a GitHub issue — target is outside the repo)
