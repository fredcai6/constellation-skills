# Excursion Brief: `x3-physics-open-debt-ledger`

## The one named question

What physics/preprocessing debt is actually still open, and for each item what would "settled" mean — build it, or formally close it with a decision record?

## Type

research

**Why this type:** ledger compilation from issues + code; nothing to build.

## What "answered" looks like

A ledger of every open physics-side item with: issue number, one-line what-it-is, current state (open/contextual/stale), whether it blocks *feature extraction for evo* (the low bar) or only *best-possible physics* (the later tiers), and a settle-or-close recommendation with rough size (S/M/L). Known candidates to verify and expand: #496 outer loop (kind=3 Matérn feedback, the one remaining piece of the physics-aware estimator), #506 σ over-claim, #557 traction follow-on, #546, #549, #499 aero base-vs-setup, #502 coast/PU diagnostic, C2 #511 race-state, C4 #513 FP-fits, the physics-blind-smoother interim workaround (raw-speed braking not productionized), #450 Phase-P compose. Do not trust this list — verify each against GitHub and sweep for others (label/title search on physics).

## Budget / stop conditions

- Read-only; `gh issue list/view` allowed.
- ~30–45 min; UNKNOWN state is acceptable per item, silence is not.
- **Scoped nulls:** state what was and was NOT swept.

## Research excursion

- **Sources:** GitHub issues via `gh` (search: physics, preprocessing, estimator, smoother, sigma, traction), `docs/architecture/decisions/`, `src/physics/` + `src/preprocessing/` TODO/FIXME markers, `.agent-work/archive/` physics epics.
- **Findings format:** cited per-item (issue URL or file:line).

## Return

Write the full findings to `.agent-work/explore-physics-evo-hookup/excursions/x3-debt-ledger-RESULT.md`. Final message = 10-line summary.
