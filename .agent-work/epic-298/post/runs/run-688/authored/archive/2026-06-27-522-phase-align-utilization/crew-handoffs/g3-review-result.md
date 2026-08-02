# Review Result — G3 Re-run + Verdict (#522)

## Assigned Gate
`g3-review` — verify the C1 re-run + verdict are honestly grounded; verify doc edits match the result.

## Result
`APPROVE`

## Handoff compliance
All five close-criteria deliverables satisfied. (1) VERDICT.md exists with before/after table, per-regime verdicts, and root-cause statement. (2) Dashboard re-run completed (4/4 OK, 264.3 s as reported by implementer; independently re-run at 267.6 s with identical numbers). (3) Both doc files updated: `docs/architecture/packets/physics.md` and `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md`. (4) Tests 35/35 green with no new test expectations. (5) g3 added no src/ changes — the lateral fix is entirely the G2 commit.

## Scope drift
No drift. `git diff HEAD -- src/` returns empty. The working tree contains only uncommitted changes to the two docs/ files and the untracked `.agent-work/522-phase-align-utilization/` directory. The HEAD commit (33c56214 = G2) touched only `src/physics/utilization/car_prior.py` and `tests/unit/physics/test_car_prior.py`. `car_prior.py` and all consumer code are unchanged by g3.

## Evidence verdict
Evidence is present and demonstrates the claimed behavior.

- **VERDICT.md** — before/after table (16 rows), per-regime verdicts with full reasoning, root-cause statement, triage finding for straight under-call.
- **`reports/physics/driver_util_subset_2023.csv`** — 4 rows with full numeric precision for all U + sigma components, produced by the implementer's run.
- **Fresh independent re-run** — `py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"` completed 4/4 OK, 267.6 s. Numbers reproduced to 3 significant figures across all cases and regimes (see Code/doc quality for table).
- **g3-implement-result.md** — complete, lists all files changed, test results (35/35), and assumptions.

## Code/doc quality

**Numbers reproduced (fresh independent run vs VERDICT.md claims):**

| Case | regime | VERDICT claim | Fresh run | Match |
|------|--------|---------------|-----------|-------|
| Monaco/VER | u_braking | 1.018 ± 0.038 | 1.018 ± 0.032 | yes |
| Monaco/VER | u_slow_corner | 0.889 ± 0.028 | 0.889 | yes |
| Monaco/VER | u_fast_corner | 0.953 ± 0.024 | 0.953 | yes |
| Monaco/VER | u_straight | 0.898 ± 0.032 | 0.898 ± 0.032 | yes |
| Italy/VER | u_braking | 0.994 ± 0.014 | 0.994 | yes |
| Italy/VER | u_slow_corner | 0.930 ± 0.007 | 0.930 | yes |
| Italy/VER | u_fast_corner | 0.917 ± 0.008 | 0.917 | yes |
| Italy/VER | u_straight | 0.987 ± 0.007 | 0.987 ± 0.007 | yes |
| Great Britain/VER | u_braking | 1.015 ± 0.012 | 1.015 | yes |
| Great Britain/VER | u_straight | 1.012 ± 0.008 | 1.012 ± 0.008 | yes |
| Singapore/VER | u_braking | 0.891 ± 0.014 | 0.891 | yes |
| Singapore/VER | u_straight | 0.958 ± 0.007 | 0.958 ± 0.007 | yes |

Un-pinning claimed ranges confirmed real: braking 0.891–1.018 (handoff: 0.89–1.02), fast_corner 0.917–0.972 (handoff: 0.92–0.97), slow_corner 0.889–0.955 (handoff: 0.89–0.96), straight 0.898–1.012 (handoff: 0.90–1.01). No 2.0 clip present.

**Verdict grounding:** All per-regime CONTEXTUAL calls are supported by the numbers + sigma. No regime over-claimed as GO. Braking: Monaco/Italy/GB at ceiling (~1.0), Singapore genuinely below (0.891; explained as potential under-extraction or apex-alignment confound). Slow_corner and fast_corner: all below ceiling, plausible ranges. Straight: GB at ceiling (1.012); Italy/Singapore slight under-calls (0.987, 0.958) explicitly recorded as a persisting finding from #518 G6 and routed to triage — not papered over. The car/driver impurity caveat (split_is_impure=True) is present and owned by covariance throughout.

**Doc quality:** Minimal, factual edits. Stale claims fully removed:
- Decision-anchor: "KNOWN METHOD FLAW", "NOT trustworthy", "phase misalignment binding constraint", "clipped at 2.0" gone as current-truth claims. Phase-alignment trigger demoted from "primary unblock" to secondary concern (accurate post-fix). `~~lateral units fix~~` FIRED bullet added.
- physics.md packet: "NO-GO (braking/fast-corner); CONTEXTUAL-trending-NO-GO" paragraph gone; replaced with accurate CONTEXTUAL finding. Known Limits "known method flaw...pin at 2.0" gone; replaced with honest secondary-concern framing.
- Both docs cite commit 33c56214 and reference VERDICT.md and the CSV.

Minor cosmetic: the decision-anchor file has a BOM character (`﻿`) prepended — likely an editor artifact. Does not affect content or rendering; not a blocker.

**Test quality:** 35/35 pass, 0.56 s. No old clipped-value (2.0) assertions found in either test file. g3 added no src/ code, so no new test expectations were introduced.

## Map impact verdict

- **Evidence supports claimed change:** Yes. Fresh run reproduces the CONTEXTUAL verdict. The capability:driver_utilization status change from NO-GO to CONTEXTUAL is backed by the fresh numbers, not asserted.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored (no src/ changes in g3). Car_prior consumer unchanged. Store read-only.
- **Notes match the diff:** Yes. struct:physics.utilization characterization-finding paragraph replaced; capability:driver_utilization upgraded; decision:ideal_lap_sim_two_sided_evaluator review-trigger fired. Map impact notes in g3-implement-result accurately describe what the diff contains.
- **Decision candidates surfaced:** Straight under-call routed to triage as #525-adjacent rather than forced as a fix here. Appropriate — the lateral fix does not touch the power-drag path.
- **Durable context routed:** VERDICT.md is the durable characterization artifact; referenced from both doc files. Triage candidate for straight under-call explicitly stated. Phase-alignment confound preserved as secondary known concern.

## Reconciliation check
No structural divergence from the recorded map. This gate is evidence+doc only. The physics packet and decision-anchor are updated accurately and consistently. No new structural nodes, no new import edges, no new constraints. No Cartographer reconciliation required beyond what the doc edits already supply.

## Blockers
None.

## Out-of-scope observations
- **Straight under-call persists (Italy 0.987, Singapore 0.958):** Confirmed real, confirmed not caused by the lateral fix (power-drag path untouched). Triage candidate to #525-adjacent power-drag calibration. Root cause candidates: DRS mask under-counting DRS-open segments at these circuits; P_max/CdA conservative in the store; straight-classification boundary bleeding into low-radius approach zones.
- **Singapore u_braking = 0.891 (8σ below ceiling):** Most divergent braking value. Plausible (tight stop-go street circuit with conservative corner entries) or could reflect residual apex-vs-approach point-alignment confound at Singapore's geometry. Not a defect at this gate; the phase-alignment confound is an acknowledged secondary concern.
- **BOM character prepended to ideal-lap-sim-two-sided-evaluator.md:** Cosmetic editor artifact introduced by g3. No content impact. Noting for Commander — trivial cleanup if desired at commit time.

## Workflow Feedback

- **Handoff gaps:** The handoff said "adjust GP names to the store if needed" — which was a helpful hedge, but the implementer already confirmed all four GP names resolved. A note that the store uses "Great Britain" (not "British Grand Prix") would have saved a lookup. Minor.
- **Context rediscovered:** The docs/ changes are uncommitted (working tree only, not in any commit after 33c56214). The handoff says "G2 committed 33c56214" and lists g3 artifacts as doc edits — it does not explicitly say whether g3 committed those doc edits or left them as working tree changes. I had to check `git status` to establish that the docs/agent-work changes are uncommitted. The handoff should clarify commit status of g3 deliverables explicitly.
- **Instructions improvised around:** The skill instruction says to use `scripts/checklist_engine.py` from the skill bundle. The skill's engine is at `C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py`, not in the repo root. I used the absolute skill path directly — this worked but the implementer had the same friction (noted in their workflow feedback). The skill instruction should cite the absolute path or note that the engine is in the skill bundle, not the repo.
- **What would have made this easier:** Handoff should state "g3 doc and agent-work artifacts are left uncommitted (working-tree-only)" vs "g3 committed X, Y, Z" so the reviewer can skip the `git status` disambiguation step.

## Return status
`complete`
