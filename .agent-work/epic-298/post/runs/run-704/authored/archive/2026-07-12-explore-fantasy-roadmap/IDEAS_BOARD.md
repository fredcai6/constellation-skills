# Ideas Board — `explore-fantasy-roadmap`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history.

## The point

Tommy (the human) plays in a ~20-player F1 fantasy league (delta-sum + progressive bingo scoring on predicted race top-10, picks submitted pre-quali). **The goal is to WIN the league** — not beat his own picks. He is historically mid-pack (~766 pts/season; winners ~674; model-equivalent ~853). The model must find ~7.5 pts/race over the current stack, live during 2026, reliable ASAP. Next race: Belgium, R10, 2026-07-19 (7 days out). "Done" feels like: a single emitted ranked top-10 he can submit unedited on inattentive weeks, an explainer he can interrogate on attentive weeks, and a weekly league-placement scoreboard showing the gap to the front closing. Kill condition: if physics + DNF + decomposition channels demonstrably cannot close the gap to winners (honest negative results across the channel bets), the push pivots rather than polishes.

Secondary goals: analysis artifacts explaining WHY cars will perform (season trends, substack-grade explainers, 2027 horizon). Derived physics information should be surfaced, not hidden.

## Current candidates

**Two-track push (user-modified Option B) — the live candidate:**
- **Track 1 (race week, Belgium as shakedown):** DB catch-up (Austria R8 + Silverstone R9 missing; collected only through Barcelona R7) → one `race-week` command: collect FPs → sampled-predict → lineup optimizer → emit (a) single ranked top-10 + (b) race-preview explainer (order, σ, per-driver "why", "model is guessing here" section). Gold retrain incl. 2026 R1-R9 as **informational regression case only** — NOT a trusted output; current gold predicts Belgium unless retrain strictly better on 2026 walk-forward.
- **Track 2 (point engines, merge whenever green — NO artificial post-Belgium freeze; user expects mergeable Thu/Fri; race weekend is not sacred):** (1) league decomposition study from docs/reference_docs workbooks (2022-2026, all players' picks) → simulated league placement per season + winners' edge decomposed into channels (top-5 bingo capture, midfield ordering, DNF avoidance, quali-day info); (2) DNF/reliability hazard channel learned from data, integrated into sampled runtime draws (Stroll-discount as emergent property, NOT hard-coded); (3) #513 FP-session physics fits → #450 A/B into quali head vs 0.80 ceiling with honest binary done-bar; (4) ephemeris regen + #589 backfill verify; (5) new-regs accommodation (#483 RegulationEra pulled forward; train-on-2026 vs recalibrate decided by A/B, not assumption).
- **Mission statement** consolidated into AGENTS.md (+ CLAUDE.md fix: stale 24-param scorer description; live system is sampled runtime + 12 latent-power modules).
- **Metrics:** north star = simulated league placement (leakage-free walk-forward vs real league picks); every model change reports league placement + fantasy pts/race (2025 holdout + 2026 so-far) + existing Brier/sign-acc. Weekly live scorecard vs actual league from the 2026 workbook.
- **Housekeeping:** rescue 17 untracked exploratory scripts (damage-clock campaign logic); deliberate call on 2GB f1_data_2023.db telemetry swell; content-triage feat/compound-damage-unit-screening (~63 unmerged commits, core re-landed via #583/#584).

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Success bar = win the league (~20 humans), not beat Tommy | User decision 2026-07-12 | cycle-1 |
| Live + competitive in 2026; Belgium (R10, Jul 19) gets a real confident prediction | User decision | cycle-1 |
| Weekly loop = co-pilot long-term: single emitted ranked list for inattentive weeks, explainer + human pen otherwise | User decision | cycle-1 |
| Two-track shape accepted; NO prescribed merge freeze — merge when green, expect Thu/Fri | User decision (modified my proposed freeze away) | cycle-1 |
| Gold retrain w/ 2026 = informational/regression case only, not trusted; useful later as regression when better data merges | User decision | cycle-1 |
| Learned conclusions over hard-coded strategies (FP3-ordering, Stroll-discount must EMERGE from channels) | User decision / design principle | cycle-1 |
| Model race/race_start stages sit at persistence ceiling; ~all headroom in quali stage (0.74 vs ~0.81 sign-acc ceiling) | Tested on 2025 holdout, gold_cycle_260612. NOT tested: post-physics-features ceiling | explore-evo report |
| "Human 2697" benchmark in multiseason_fantasy.md = sum of LEAGUE WINNERS' totals (739+632+615+711), not Tommy | Verified arithmetic vs workbooks | cycle-1 |
| DB is 2 races stale (R8 Austria, R9 GB missing); next race Belgium R10 Jul 19 | Verified against f1_data_2026.db sessions table | cycle-1 |
| Physics↔evo stacks share zero imports; bridge = #513 (FP fits, unbuilt) → #450 (Phase P A/B) | Verified by import scan (explore-evo) | cycle-1 |
| C1-C3 capability verdicts CONTEXTUAL: circuit-conditional fine-margin covariance-bearing signals, not clean car axes | Per #509 refresh + memory | explore-issues |
| League data available: all players' picks/deltas/bingos 2022-2026, format matches src/fantasy_scoring exactly | Workbooks parsed (openpyxl), structure verified | cycle-1 |
| f1_data_2023.db swelled 16MB→2GB (telemetry ingest into season DB) — needs deliberate keep/exclude call | Observed git status + sizes; NOT yet decided | explore-wip |

## Open threads

- **Where exactly do winners' ~7.5 pts/race come from?** (decomposition study answers; steers channel priority)
- Where would the model have PLACED in the league each season? (per-season walk-forward totals vs standings)
- Train-on-2026 vs recalibrate-on-2026 for the regime break (A/B in gold cycle)
- #589: did the 2019-2026 physics_estimates.db backfill complete? (gates non-2023 ephemeris trust)
- Ephemeris RUN 3 predates σ/PVAT rebuild — regen needed before explainer-grade physics content
- DNF hazard: model shape undecided (per-driver? per-car? per-circuit interaction? hazard into sampled draws vs post-hoc discount)
- `race-week` command seam: wraps existing CLI pieces vs new orchestrator module — undesigned
- Explainer content/format undesigned (what "per-driver why" means concretely given 12-module fusion + physics channels)
- Tournament dynamics: MILP maximizes expected score; winning a league may favor variance-aware lineup lanes (beam search risk lanes exist, unused strategically)
- 2026 sprint weekends (China, Miami, Canada, GB, Netherlands, Singapore) change the FP-evidence shape pre-quali — SQ/sprint handling in weekly loop
- League workbooks: emoji sheet names/cp1252 traps; parser needs care (PYTHONIOENCODING=utf-8 works)
- Whether "17 untracked scripts" carry durable conclusions worth distilling (damage-clock campaign) or just archive

## Rejected ideas (with reasons)

- **Option A "everything by Belgium"** — four workstreams converging on an untested weekly loop in 7 days; the thing trusted Sunday shouldn't be rebuilt Friday. Would revive if: loop proves stable early in week. (Partially revived by user removing the merge freeze — difference from live candidate is now only sequencing discipline, not content.)
- **Option C "roadmap purist" (#513→#450 only, Belgium as mere ops shakedown)** — under-serves "real confident prediction next Sunday"; bets everything on one channel before decomposition evidence. Would revive if: decomposition shows quali accuracy dominates all other channels.
- **Hard post-Belgium merge freeze** — user rejected: historically pushes take days, nothing is sacred about race weekend.
- **Hard-coding human heuristics (FP3 ordering, Stroll discount)** — user principle: model should reach these conclusions from data channels, not encode them.

## Review-round verdicts (2026-07-12, post-panel)

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| #375 context-conditioned net = HONEST NULL on ordering (calibration-only gains), closed 2026-06-07; reopen trigger = new ordering-shaped inputs (physics features qualify) | Fusion-layer conditioning for race/race_start on cached 2018-2025 inputs; NOT tested: conditioning with physics-derived inputs | gh #375 close-out, PR #428 |
| Quali baseline corrected: ~0.776 LOSO / ~0.762 OOS vs ceilings ~0.806 / ~0.764 (#420 anchor live in gold) — ~3pp model-side headroom, not 6-9pp | Current input recipe; NOT tested: raised ceiling from new inputs | critic IF2 + ceiling doc §7.6.4 |
| 2026 workbook internally inconsistent: Standings columns keep Bahrain/Saudi placeholders (Belgium="Round 12") while round sheets renumbered (Miami="Round 4"); GP-name variants vs DB | Verified by direct read of both sheet sets | critic TS1 + author verification |
| Production sampler has no retirement mechanism (argsort full field every draw); DNF-in-draws = new build | covariance_sampling.py live path; legacy race_simulator.py dead | critic TS2 |
| Metric regime: decision metric = self-contained fantasy pts/race vs actual results; league placement = informational overlay, never gates development, allowed to lag | User decision 2026-07-12 | triage session |
| All 28 panel findings dispositioned: 22 EDIT (applied to spec rev 2), 6 REJECT (SY1/SY2/SY3/SY5/SY9/SY10, reasons in spec table) | Human triage, wholesale acceptance of recommendations + metric clarification | triage session |

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | compare (run pre-engine under superpowers:brainstorming; recorded here retroactively at engine adoption) | 4-explorer repo stocktake (evo/physics/issues/WIP); fantasy goal interrogation; league workbooks discovered + parsed; 3 roadmap options compared | Two-track push selected + user-modified (no freeze, retrain informational); board seeded; user directed convergence to spec + cold 3-lens critic panel |

## Routing outcome (2026-07-12)

Spec CONFIRMED by the owner (Confirmation block filled; verifier passes both phases). Routed as a shaped-design epic **#601** holding the full spec body, plus child issues #602-#610 cut same day. Owner-directed backlog sweep executed alongside routing: 10 issues closed with citations (#255 #204 #205 #208 #210 #325 #265 #392 #445-as-delivered #132), 11 issues absorbed/updated into the push (#513 #450 #482 #389 #483 #589 #577 #434 #423 #529 #390), physics debt pile consolidated into burn-down tracker #609 (owner: "make sure our plan includes closing the physics debt"), #435 kept per owner. Work area archived; lease released.
