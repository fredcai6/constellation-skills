# Design Spec — Fantasy-League Prediction Push (research program, live 2026)

## Confirmation

- **Status: CONFIRMED**
- Confirmed by: Tommy (owner; fredcai6)
- Date: 2026-07-12
- Critic findings dispositioned: YES — all 28 rows carry a Disposition (triaged by the owner 2026-07-12; 22 EDIT applied in rev 2, 6 REJECT with reasons)
- Assumptions exercised: league scoring arithmetic reproduced against workbooks (winners ~674, "human 2697" = sum of league winners); DB staleness verified (R8/R9 missing, Belgium = R10); 2026 workbook internal round-numbering inconsistency verified by direct read of both sheet sets; production sampler verified to have no retirement mechanism (argsort full field); quali headroom baseline corrected against ceiling doc §7.6.4 (#420 anchor live in gold); #375 closure and reopen trigger verified from the issue record.
- Assumptions accepted untested: that ~7.5 pts/race is findable at all across the channel bets (this is the bet itself, with the pivot condition named in Intent); that FP-session physics fits (#513) will be usable as predict-time features (its own done-bar may return "too noisy"); that a DNF channel carries fantasy-point value (arm (a) exists to test exactly this); that the decomposition study's channel attribution will be sharp enough to steer capacity (it gates items 2–4 regardless of sharpness).

## Intent

F1Brainz's owner (Tommy) plays a ~20-player F1 fantasy league: before each qualifying session, every player submits a predicted top-10 race finishing order, scored by delta-sum (|predicted − actual| per pick, lower better) plus a progressive bingo deduction for exact hits. **The goal of this push is to make the model capable of winning that league, live during the 2026 season.** The bar is quantified from the league's own workbooks: winners average ~674 pts/season (~26–31 pts/race across ~24 rounds); Tommy averages ~766; the current model's leakage-free walk-forward equivalent is ~853. The model must find roughly 7.5 pts/race relative to its current self.

This is **fundamentally a research program, not an ops push** (owner framing, 2026-07-12): exploration is sanctioned at the expense of delayed final implementation, with the goal kept visibly in sight so the program doesn't get lost in the woods. "Done" feels like: (1) a single command per race weekend that emits a ranked top-10 the owner can submit unedited on inattentive weeks; (2) a race-preview explainer he can interrogate on attentive weeks; (3) a goal-tracking overlay showing what the model's scores would have meant in league terms. The next race — Belgium, 2026-07-19, seven days from spec date — receives a real prediction through this loop as its plumbing shakedown (explicitly a shakedown, not a quality verdict; see Testing pathways).

Secondary intent: the physics-derived analysis artifacts (why cars are fast, season trends) become first-class outputs — decision support now, substack material on the 2027 horizon.

## Exploration record (digest)

- **Cycles run:** one compare cycle (goal interrogation + four-explorer repo stocktake + three-option roadmap compare), consolidated; convergence initiated by the human. Cold 3-lens critic panel (intent-fit / testability / simplicity) run 2026-07-12; all 28 findings human-triaged same day.
- **Excursion answers (scoped):**
  - Evo predictor: live system is a 3-stage sampled race-weekend simulator over 12 neural latent-power modules, evaluated honestly on 2025 holdout. Race and race-start stages sit at the persistence ceiling; the headroom is the quali stage. **Corrected baseline (critic IF2):** with the #420 cross-channel pace anchor already live in the promoted gold, the quali head scores ~0.776 (LOSO) / ~0.762 (OOS 2025) against data-only ceilings ~0.806 / ~0.764 — roughly 3pp of measured headroom remains on current inputs, not the 6–9pp this spec originally claimed. Raising the *ceiling itself* requires new information entering the model (the physics bet).
  - The context-conditioned net (#375) — collapsing the 12 modules into one conditioning-aware net — was built and measured June 2026: **honest null on ordering** (calibration-only gains; sign-acc/Spearman CIs include zero), closed with a named reopen trigger: "a new conditioning signal that is demonstrably ordering-shaped." Physics-derived features are exactly that kind of new input. The ceiling doc's still-standing cheaper lever is targeted improvement of the standalone practice-evidence quali head's per-context evidence weighting.
  - Physics stack: measurement machinery complete; C1–C3 characterizations returned CONTEXTUAL verdicts (circuit-conditional, fine-margin, covariance-bearing). C4 (#513, FP-session fits) is unbuilt (issue QUEUED) and is the predict-time gap; zero imports connect physics to the predictor (bridge = #513 → #450, unbuilt).
  - Operational: season DB is two races stale (Austria R8, Great Britain R9 uncollected); ephemeris store predates the σ/PVAT rebuild; #589 gates trust in non-2023 physics estimates.
  - League workbooks (docs/reference_docs, 2022–2026): every player's picks, per-pick deltas, bingo counts, all rounds — same scoring format `src/fantasy_scoring` implements. **Verified hazard (critic TS1):** the 2026 workbook is internally inconsistent — the Standings sheet keeps Bahrain/Saudi as stale placeholder columns (Belgium = "Round 12" there) while per-round sheets are renumbered to match the real calendar (Miami = "Round 4", matching the DB). GP naming also varies vs the DB (Barcelona/Barcelona-Catalunya, Austin/United States, Monza/Italy, San Marino). Any join runs through a normalization + reconciliation layer with tests.
  - **Verified gap (critic TS2):** the production sampler (`covariance_sampling.py`) ranks the full field every draw; there is no retirement mechanism anywhere in the live path (only dead legacy code draws DNFs). Retirement-aware draws are a new mechanism to build, not a configuration choice.
- **Rejected approaches, with reasons:** "Everything by Belgium" as a *requirement* (rejected as the bar; later sanctioned as an acceptable outcome — the two-track shape is a floor, not a ceiling: "I wouldn't be mad if B becomes A"). "Roadmap purist" (#513→#450 only). Hard post-Belgium merge freeze (merge when green). Hard-coding human heuristics (FP3-ordering, named-driver reliability discounts) — these conclusions must emerge from learned channels.
- **Open threads carried:** decomposition channel weights unknown; tournament-variance lineup strategy (variance-aware lane selection for a 20-player single-champion season) — named open thread, deliberately deferred; sprint-weekend evidence shape (6 sprint weekends in 2026); train-on-2026 vs recalibrate-on-2026.

## Chosen design

### D1. Mission consolidation

A consolidated mission statement lands in `AGENTS.md` (mirrored in `CLAUDE.md`): the league, the scoring rule, the pre-quali lock, the decision metric and informational league overlay (D4), the co-pilot loop, and the artifacts-are-first-class secondary goal. `CLAUDE.md`'s stale evo description (dead 24-param scorer) is corrected to the live sampled-runtime + latent-power architecture. (Timing: any day this week; owner-requested, trivial cost.)

### D2. Track 1 — the weekly race loop, shaken down on Belgium (Jul 19)

- **Data catch-up now:** Austria R8 + Great Britain R9 classifications/laps/telemetry into the season DBs and Parquet mirror; Belgium FP sessions as they land Friday.
- **`race-week` command:** one entry point wrapping existing pieces (collect → `sampled-predict` → lineup optimizer → emit). Emits (a) the single ranked top-10 list and (b) the race-preview explainer (predicted order with σ, per-driver evidence-channel attribution, an explicit "model is guessing here" section). **Interface design-it-twice runs FIRST (days 1–2), not at cut time** — the seam must be settled before the Friday data path is wired (critic IF4).
- **Lineup lane named (critic IF3):** the Belgium output uses the beam search's *balanced* lane as a deliberate default (mean-score lane as fallback if balanced misbehaves on live data); this is a placeholder choice pending the tournament-variance open thread, and the emitted report states which lane produced the list.
- **Gates split (critic SY8):** the ranked list before quali lock is the hard gate; the explainer is a soft goal for Belgium (its absence does not fail the shakedown).
- **Gold retrain including 2026 R1–R9 — instrumentation, not a test (critics TS9/SY3):** overnight unattended; a regression yardstick for later merges and the first observation of stack behavior under a regime break. It does not gate Belgium and its interpretation is deferred; the current gold predicts Belgium unless the retrain is strictly better on 2026 walk-forward.

### D3. Track 2 — the point engines (merge whenever green; concurrency sanctioned)

Ordered by information dependency; capacity commits to items 2–4 only after item 1's channel table lands (critic IF5 — "first" now means *gating*, not merely scheduled-first):

1. **League decomposition study:** parse the five workbooks **through a round/GP-name normalization + reconciliation layer with tests** (critic TS1; the layer must reproduce each workbook's own recorded totals per player per season before anything downstream consumes it — and the scoring rule itself is encoded as a documented fixture cross-validated over multiple seasons/players/rounds, the closest available substitute for a machine-readable rules source, residual risk accepted; critic TS5). Compute where the model's walk-forward picks would have placed each season; decompose the winners' ~7.5 pts/race edge into channels (top-5 bingo capture, midfield ordering, DNF avoidance, quali-day information). Output: ranked "channel X is worth ~Y pts/race" table that gates items 2–4's capacity. This study also stands up the league-overlay machinery D4 uses.
2. **DNF/reliability channel — reframed (critics TS2/IF7):** start from the ceiling doc's existing characterization (reliability is near-memoryless: team/season prior with a one-sided tail; `predictive_t` / per-site tail machinery named as the lever). Two honestly-scoped arms: (a) **post-hoc tail adjustment** using existing machinery — cheap, no sampler change; (b) **in-sampler retirement mechanism** — a genuine new build inside the sampled-runtime path (nothing exists there today). Arm (b) proceeds only if (a)'s measured lift and the decomposition's DNF-channel value justify it. Calibration gate gets a numeric threshold and named aggregation granularity at cut time (critic TS8).
3. **Targeted quali-head lever (critic IF1 residue):** improve the standalone practice-evidence quali head's per-context evidence weighting — the ceiling doc's own "cheaper targeted alternative," attacking the measured model-side gap on current inputs. Scoped after decomposition confirms quali-ordering points matter as expected.
4. **#513 FP-session physics fits → #450 Phase-P A/B — expectations re-based (critic IF2):** physics capability measured from FP sessions, fed as covariance-bearing relative features into the quali head. With ~3pp of model-side headroom left on current inputs, the physics bet is properly framed as **raising the data ceiling itself** (new information), not capturing the already-mostly-closed model-side gap — and new ordering-shaped inputs are precisely #375's named reopen trigger, so a physics win may also reopen conditioning. **Null branch named (critic TS7):** #513's own done-bar may conclude FP fits are too noisy to use pre-quali; that verdict is a documented negative that bounds the physics bet, #450's A/B is then vacuously closed, and the predictor continues on existing channels — the push does not stall on it.
5. **Ephemeris regeneration + #589 backfill verification — hygiene, justified on hygiene alone (critic SY6):** the explainer-content benefit is real only after physics features reach the predictor; not claimed for this cycle.
6. **New-regs accommodation:** #483 (RegulationEra) pulled forward; train-on-2026 vs recalibrate-on-2026 decided by A/B inside the gold cycle, not by assumption.

### D4. Metrics — decision metric vs informational overlay (owner clarification 2026-07-12)

- **Decision metric (gates model changes):** the model's own fantasy score — its picks scored against **actual race results** with the league formula (delta-sum + progressive bingo via `ScoringCalculator`), reported as pts/race on the 2025 holdout and 2026-so-far walk-forward. Fully self-contained: requires no league data. Alongside it, Brier remains primary for module-level gold-vs-gold comparisons per existing project doctrine — a deliberate two-metric regime (critic IF6): Brier judges module quality, fantasy pts/race judges push-level value; the tension is acknowledged and the fantasy metric wins push-level arguments.
- **League overlay (informational only, never gates decisions):** where those scores would have placed among the ~20 real players. Operational definition (critic TS4): the model is inserted as a virtual 21st competitor into each season's workbook standings; placement = rank by season-cumulative total under the league formula; ties resolve against the model (worst placement). Computed historically by the decomposition study; updated for 2026 rounds **when the workbook is current** — transcription of rivals' picks is a human, out-of-band process (the owner's own bookkeeping) and is explicitly allowed to lag (critic TS6); a stale overlay delays goal-tracking, never development.

### D5. Housekeeping (non-blocking, cheap, front-loaded deliberately)

Rescue the 17 untracked exploratory scripts (damage-clock campaign logic) to a branch or archive; deliberate keep/exclude decision on the 2GB `f1_data_2023.db` telemetry swell before any commit touches it — acknowledged as pre-existing repo-wide practice debt being settled opportunistically here, not something Belgium created (critic SY11); content-level triage of `feat/compound-damage-unit-screening` (~63 unmerged commits; core re-landed via #583/#584).

### Sequencing (research-program pacing; days are soft)

First: housekeeping + data catch-up + decomposition study + `race-week` seam design-it-twice. Then: retrain overnight (instrumentation); DNF arm (a) and remaining channel work as the decomposition's channel table lands. Friday/Saturday: Belgium prediction produced through the new loop, owner holds the pen. After Belgium: channel priorities re-cut against the decomposition table; #513/#450 and the quali-head lever proceed per that evidence; weekly live races accumulate into the rolling comparison.

- **Per-section approval:** outline approved conversationally by the owner pre-spec; critic-panel triage (all 28 findings) dispositioned by the owner 2026-07-12; this revision awaits the owner's confirm-gate decision.

## Testing pathways

Labeled per critic TS9: **[gate]** = has a falsification condition; **[instrumentation]** = observation only, cannot fail by design.

- **[gate] Weekly loop (Belgium):** hard gate = the command produces a submittable ranked top-10 from Friday FP data before quali lock; explainer is a soft goal. **This is a plumbing shakedown, not a quality test (critic TS3):** one race's fantasy score is noise-dominated (per-race model scores historically range ~35–40); quality verdicts come from the walk-forward decision metric and the accumulating rolling comparison over 2026 races, never from Belgium alone.
- **[gate] Decomposition study:** falsified if the reconciliation layer cannot reproduce each workbook's own recorded per-player totals, or the model's recorded walk-forward totals, before decomposing.
- **[gate] DNF arm (a):** A/B on the decision metric with a numeric calibration threshold (granularity and threshold fixed in the cut issue); falsified if pts/race does not improve or calibration fails. Arm (b) carries its own build-feasibility check before any A/B.
- **[gate] #513→#450:** the existing honest A/B harness; binary done-bar; the "FP fits unusable" branch is a documented negative deliverable.
- **[instrumentation] Retrain-with-2026:** walk-forward observation on 2026 R1–R9 vs current gold; informational either way.
- **Deferred to later drills:** tournament-variance lane selection; sprint-weekend-specific loop behavior beyond what Belgium (a conventional weekend) exercises.

## Out of scope

- Hard-coding any human heuristic (FP3 ordering, named-driver reliability discounts).
- Substack/publishing pipeline itself (2027 horizon); this push only keeps artifacts first-class.
- Live in-race strategy tooling; betting markets; any non-league scoring format.
- Physics work beyond #513/#450/ephemeris-regen (D-series debt #587–#594 continues on its own track, not gating this push).

### Untaken roads (named, per design-it-twice doctrine)

The `race-week` command seam's design-it-twice now runs up front (critic IF4) rather than at cut time. Design-it-twice remains deferred to cut time for two load-bearing interfaces: the DNF integration point into the sampled runtime (shape depends on arm (a)-vs-(b) evidence) and the physics-feature adapter into the quali head (shape depends on #513's coverage verdict). Reason: both interfaces' constraints are unresolved until their gating evidence lands; designing them now would design against guesses.

## Critic findings and dispositions

Full finding text lives in `critic-{intent-fit,testability,simplicity}-findings.md` beside this spec; rows below are condensed faithfully. Author verification notes: TS1 CONFIRMED and refined (workbook internally inconsistent — see digest); IF1 partially stale (#375 was closed as an honest null 2026-06-07, which the critic could not know cold) — its residue (the targeted quali-head lever) is adopted as D3 item 3. All dispositions by the owner, 2026-07-12 ("all of that is generally fine" + the D4 informational-overlay clarification).

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| IF1 | intent-fit | BLOCKING | Track 2 omits the repo's documented highest-leverage quali lever (#375 context-conditioned net / targeted quali-head weighting). | EDIT | #375 itself is an honest null (closed 2026-06-07), but the cheaper targeted quali-head lever is real and adopted as D3 item 3; physics inputs noted as #375's reopen trigger. |
| IF2 | intent-fit | MAJOR | Quali headroom stale: ~0.776 vs ~0.806 post-#420, not 0.74 vs 0.81; physics bet mis-sized. | EDIT | Verified; baseline corrected in digest; #513/#450 reframed as ceiling-raising (D3 item 4). |
| IF3 | intent-fit | MAJOR | Expectation-shaped north star for a variance game; Belgium's beam lane chosen by default. | EDIT | Lane named explicitly (balanced, stated in report); tournament-variance remains a named open thread; metric reframed in D4. |
| IF4 | intent-fit | MAJOR | race-week seam design deferred past its own deadline. | EDIT | Design-it-twice pulled to days 1–2 (D2, Untaken roads). |
| IF5 | intent-fit | MINOR | Capacity commits before decomposition can reprioritize. | EDIT | Decomposition's channel table now gates items 2–4 capacity (D3). |
| IF6 | intent-fit | MINOR | Brier-primary vs fantasy-target tension unflagged. | EDIT | Two-metric regime stated explicitly in D4. |
| IF7 | intent-fit | MINOR | DNF channel re-derives documented reliability characterization. | EDIT | D3 item 2 now starts from the ceiling doc's team/season-prior one-sided tail + predictive_t machinery. |
| IF8 | intent-fit | MINOR | Assumptions fields blank while load-bearing numbers are spec-only. | EDIT | To be filled at confirm with the verified figures (IF2-corrected). |
| TS1 | testability | BLOCKING | Round-numbering misjoin risk between DB and workbook. | EDIT | Confirmed + refined (internal inconsistency); reconciliation layer with reproduce-totals gate added (D3 item 1). |
| TS2 | testability | BLOCKING | Production sampler has no retirement mechanism; hazard-in-draws is unbuilt infrastructure. | EDIT | DNF item reframed into arms (a) post-hoc (existing machinery) and (b) in-sampler build, (b) gated on (a)'s evidence (D3 item 2). |
| TS3 | testability | MAJOR | Belgium gate tests plumbing, not prediction quality. | EDIT | Stated plainly in Testing pathways: plumbing shakedown; quality verdicts from walk-forward + rolling comparison. |
| TS4 | testability | MAJOR | "Simulated league placement" never operationally defined. | EDIT | Defined in D4 (virtual 21st competitor, season-cumulative, ties→worst) — and demoted to informational overlay per owner. |
| TS5 | testability | MINOR | No machine-readable scoring-rule source. | EDIT | Rule encoded as documented fixture cross-validated over seasons/players; residual risk accepted (D3 item 1). |
| TS6 | testability | MAJOR | Gap-to-front depends on unscheduled human workbook transcription. | EDIT | Overlay is informational-only and allowed to lag (owner clarification); development never waits on it (D4). |
| TS7 | testability | MAJOR | No plan for "#513 concludes FP fits unusable." | EDIT | Null branch named: documented negative bounds the bet; #450 vacuously closed; push continues (D3 item 4). |
| TS8 | testability | MINOR | DNF calibration gate lacks threshold/granularity. | EDIT | Numeric threshold + granularity fixed in the cut issue (D3 item 2, Testing pathways). |
| TS9 | testability | MINOR | Instrumentation vs test blurred. | EDIT | Pathways now labeled [gate]/[instrumentation]. |
| SY1 | simplicity | MAJOR | Two-track re-creates rejected "everything by Belgium"; concurrency unargued. | REJECT | Owner sanctioned explicitly: "I wouldn't be mad if B becomes A, just setting the bar low" — the two-track shape is a floor; fleet capacity, research-program framing. |
| SY2 | simplicity | MAJOR | Decomposition study over-billed; candidate for descoping. | REJECT | It also builds the reconciliation layer and league-overlay machinery (needed regardless) and now genuinely gates channel capacity (IF5 edit); cheap via subagents. |
| SY3 | simplicity | MINOR | Informational retrain is decorative this week. | REJECT | Overnight unattended compute; interpretation explicitly deferred; owner values it as a regime-break regression case. |
| SY4 | simplicity | MAJOR | Five metric surfaces in shakedown week. | EDIT | D4 collapsed to one decision metric + one informational overlay; other surfaces layer later. |
| SY5 | simplicity | MINOR | Front-loaded housekeeping is displacement activity. | REJECT | Scripts rescue is ~minutes protecting real assets in a high-churn week; the 2GB call gates data/ commits that happen constantly; research-program pacing removes the deadline squeeze. |
| SY6 | simplicity | MAJOR | Ephemeris regen justified by content nothing consumes yet. | EDIT | Justified on hygiene alone (D3 item 5). |
| SY7 | simplicity | MAJOR | #513/#450 capacity vs DNF priority unargued. | EDIT | Allocation now argued: re-based sizing (IF2), decomposition gates capacity, DNF arm (a) first; both proceed under research-program framing. |
| SY8 | simplicity | MAJOR | List+explainer bundled into one pass/fail gate. | EDIT | Split: list hard, explainer soft (D2). |
| SY9 | simplicity | MINOR | Mission statement competes for day-1 attention. | REJECT | Owner-requested; trivial cost; no deadline pressure under research pacing. |
| SY10 | simplicity | MAJOR | Three A/Bs + study + shakedown = a research programme, not a race-week push. | REJECT | Owner: it IS fundamentally a research program; pacing accepted; A/Bs stagger naturally behind the decomposition gate (IF5 edit). |
| SY11 | simplicity | MINOR | 2GB DB call is ambient repo debt riding along. | EDIT | Acknowledged as such in D5. |
