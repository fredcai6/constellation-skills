# Triage recommendations — issue #624 Phase 0 probes

All 4 candidates checked against the Fix-Now Eligibility Ladder: none clear it (none are bounded-diff code fixes adjacent to this run's own scope — tc1/tc4 are investigations, tc2/tc3 are future-prerequisite/bug-risk items outside this run's allowed scope). Issue-filing authority is clear (`docs/agents/ORCHESTRATOR_CONTEXT.md` Repo Action Authority: "Create issues, comments, branches, worktrees | Autonomous for non-trivial tasks").

## tc1 — Pearson/Spearman sign mismatch on g1's primary axis
- **Label**: research hardening / unresolved decision.
- **Disposition**: `filed` — **#634** (https://github.com/fredcai6/f1Brainz/issues/634).

## tc2 — team_canonicalization.py year-agnostic misjoin risk
- **Label**: bug (latent, unconfirmed-until-triggered).
- **Disposition**: `filed` — **#635** (https://github.com/fredcai6/f1Brainz/issues/635).

## tc3 — residual-history injection seam dormant in every production manifest
- **Label**: missing capability anchor / dependency cleanup.
- **Disposition**: `filed` — **#636** (https://github.com/fredcai6/f1Brainz/issues/636).

## tc4 — SQ probe's flagged brake_aero_decel_per_m axis
- **What**: g4's SQ coverage probe found 10/11 axes numerically plausible vs same-weekend Q for one test weekend/constructor; the one flag (`brake_aero_decel_per_m`, ratio 2.96x) is likely explained by that axis's known noise-sensitivity (per `x7-basis-map-RESULT.md`: "already the most locally-fit, least density/circuit-sensitive quantity") rather than an SQ-specific defect — but this is a single-weekend, single-constructor read, unconfirmed at scale.
- **Importance**: minor — worth a caveat for whoever eventually builds real SQ support (#513-adjacent FP/SQ mechanics work), not urgent enough to block or gate anything now.
- **Evidence**: `.agent-work/archive/2026-07-18-624-phase0/G4_FINDINGS.md`.
- **Acceptance criteria**: N/A — this is a documented caveat, not a bounded task.
- **Out of scope**: building real SQ support (explicitly Phase 4/#513 scope, not Phase 0).
- **Disposition**: `recommend-and-defer` — NOT filed as a standalone issue. Reason authority is unclear for filing: this is a single-data-point observation with no clear owner or urgency; it naturally belongs folded into whichever future issue does #513's FP/SQ mechanics work (already tracked), rather than spawning a separate low-signal issue that would need re-triaging when that work starts. Recorded here so the caveat isn't lost, deferred to the human/Admiral or to whoever picks up #513 next.
