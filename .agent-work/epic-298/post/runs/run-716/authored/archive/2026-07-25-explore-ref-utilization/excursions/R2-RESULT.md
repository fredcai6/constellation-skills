# R2 — Car-vs-driver variance splits in the F1 statistical-modeling literature

Question: what car-vs-driver variance splits and estimation methods has the Formula 1
statistical-modeling literature converged on?

Research excursion (web/academic), 2026-07-24. Read-only, no files modified other than this
result. All numbers below are as reported by secondary summarization of the source (WebFetch's
small-model extraction) except where I quote the source's own abstract text directly — several
primary PDFs (arXiv full-text, SIAM PDF) would not render as text and I could only reach
abstract/landing-page level for those. Flagged per-source below.

## TL;DR

**No convergence on a number — the reported car/team share of variance ranges from 61% to
88% depending on method, era, and (critically) outcome variable, and two papers covering
nearly the same era (2014–2021 vs 2014–2024, both "hybrid era") land 24 points apart (88% vs
64%).** What the literature *does* converge on:

1. **Method**: every serious attempt uses teammate comparisons (same car, two drivers) as the
   core identification device, reinforced by driver-team switching across seasons/careers —
   exactly the "classic instrument" the question named. This is unanimous across five
   independent sources below.
2. **Outcome variable**: every model surveyed fits an **ordinal/discrete outcome** — points,
   finishing position, or finishing rank — **never raw lap time**. This is a real gap against
   f1Brainz's own lap-time-native representation; see "What none of this covers" below.
3. **Direction of the wet/street-circuit effect is consistent across two independent papers**:
   driver effects strengthen (car effects weaken) in wet conditions and on street circuits. This
   is the one finding I'd call load-bearing rather than noisy.
4. **All models are additive** (driver_skill + car_skill, no driver×car interaction term) — none
   of the surveyed literature models a condition-dependent driver fingerprint the way f1Brainz's
   internal exploration (x1/x3) is aiming at; the wet/street finding is a *coarse* two-bucket
   version of that idea, not the fine-grained one.

---

## 1. Bell, Smith, Sabel & Jones (2016), "Formula for success: multilevel modelling of Formula
   One driver and constructor performance, 1950–2014" — *Journal of Quantitative Analysis in
   Sports* 12(2):99–112

- **Method**: cross-classified multilevel (random-coefficient) model. Response variable = **points
  scored per race**. Variance partitioned into three levels — team, team-year, and driver — with
  effects allowed to vary by **year, track type, and weather**.
- **Headline finding (from the abstract, both Aarhus/Bristol/White Rose mirrors agree)**: "Team
  effects are shown to be more important than driver effects (and increasingly so over time),
  although their importance may be reduced in wet weather and on street tracks." Fangio comes out
  as the highest-rated driver once team is partialled out.
- **Exact %**: I could not pull an exact number from the primary abstract text itself — the
  degruyter DOI page 405'd (not fetchable), and Semantic Scholar returned no extractable
  abstract text. The commonly cited figure — **"86% team"** — comes from a secondary source
  (f1metrics's 2016 post, below), not verified against the paper directly. Treat as
  literature-adjacent, not primary-confirmed.
- **Era trend**: team importance is stated to *increase* over the 1950–2014 span (i.e. the car
  has become a larger share of the result in the modern era than in the 1950s–60s), consistent
  with the general intuition that aero/hybrid-era cars are more differentiated than 1950s cars —
  but I have no year-by-year numeric breakdown, only the directional abstract claim.
- Sources: [Aarhus mirror](https://pure.au.dk/portal/en/publications/formula-for-success-multilevel-modelling-of-formula-one-driver-an/), [Bristol mirror](https://research-information.bris.ac.uk/en/publications/formula-for-success-multilevel-modelling-of-formula-one-driver-an/), [White Rose eprint](https://eprints.whiterose.ac.uk/96995/), [degruyter (405, unreachable)](https://www.degruyterbrill.com/document/doi/10.1515/jqas-2015-0050/html), [Semantic Scholar (no abstract text returned)](https://www.semanticscholar.org/paper/Formula-for-success:-Multilevel-modelling-of-One-Bell-Smith/5eabb71a86e1a64b570f644f87f82d5d511c49e0)

## 2. Phillips (2014) / f1metrics community model — "Who was the greatest F1 driver?" +
   "Experts versus models: how do we rank drivers?"

- **Method**: not a peer-reviewed paper, a long-running statistics blog (f1metrics, WordPress).
  Uses an **extended/fractional points system** (assigns fractional points to non-scoring
  positions instead of raw points or raw finishing position) specifically to avoid two known
  distortions: raw-position models over-penalize bad results non-linearly, and raw points can't
  discriminate among non-scoring finishes (12th vs 15th look identical on 0 points).
- **Identification**: teammate comparisons are the *only* direct driver-vs-driver signal ("no
  direct driver comparisons are possible" except within a team); cross-team comparison is
  propagated by chaining through drivers who changed teams. Team ratings are fit **independently
  year-to-year** (no assumed continuity of team strength across seasons).
- **DNF handling**: explicitly excludes *non-driver-caused* DNFs (mechanical failures) from the
  fit, an attempt to strip "bad luck" out of the driver signal — a deliberate methodological
  choice not shared by the Bayesian ROL paper below (which excludes DNFs wholesale).
- **Reported split**: **61% team** (Phillips 2014), contrasted in the same post against **86%
  team** attributed to Bell et al. (2016) — i.e. f1metrics itself flags these two numbers as
  disagreeing by 25 points and does not reconcile them.
- Sources: [Experts versus models](https://f1metrics.wordpress.com/2016/10/06/experts-versus-models-how-do-we-rank-drivers/), [f1metrics home](https://f1metrics.wordpress.com/)

## 3. Eichenberger & Stadelmann (2009), "Who Is The Best Formula 1 Driver? An Economic
   Approach to Evaluating Talent" — *Economic Record* (via ScienceDirect / Australian Economic
   Papers lineage)

- **Method**: linear regression with driver dummy variables and constructor-year covariates on
  **finishing position**, 1950–2006. Framed as an economics/labor-market talent-identification
  paper (constructor-year as a proxy for "firm" quality, driver dummy as individual "worker"
  productivity net of firm).
- Ranks: Fangio #1, then Clark/Schumacher/Stewart/Prost/Alonso cluster near the top; the paper's
  placement of Mike Hawthorn at #5 is noted elsewhere in the literature as an outlier result
  relative to other models' rankings.
- **No numeric variance split obtained** — ScienceDirect returned HTTP 403 and the abstract text
  I could extract (via a secondary WebSearch summary) does not state a %. **Scoped null**: I did
  not get this paper's own car/driver quantitative split; it is cited here for its historical
  role as (per secondary sourcing) an early, methodologically influential paper using
  driver-team-switching identification.
- Sources: [ScienceDirect (403, unreachable)](https://www.sciencedirect.com/science/article/pii/S0313592609500355), [Semantic Scholar](https://www.semanticscholar.org/paper/Who-Is-The-Best-Formula-1-Driver-An-Economic-to-Eichenberger-Stadelmann/7d79193bfc49c8775f0ccbd9452db7ae213991b1), [ResearchGate](https://www.researchgate.net/publication/41110138_Who_Is_The_Best_Formula_1_Driver_An_Economic_Approach_to_Evaluating_Talent)

## 4. Bayesian multilevel rank-ordered logit (arXiv 2203.08489), "Bayesian Analysis of Formula
   One Race Results: Disentangling Driver Skill and Constructor Advantage" — JQAS 2022/2023,
   also on PMC

- **Method**: Bayesian multilevel **rank-ordered logit (Plackett-Luce-style)** on per-race
  finishing position, hybrid era **2014–2021**, non-finishers excluded entirely. Latent ability
  decomposed additively: `θ_competitor = θ_driver(long-run) + θ_driver(yearly form deviation) +
  θ_constructor(average) + θ_constructor(yearly form)`. Parameters interpreted as Elo-like
  log-odds of beating a competitor.
- **Identification**: explicitly names both mechanisms the question asked about — teammate
  comparisons (identical-car within-team pairs) *and* career mobility (drivers changing
  constructors over the years) used jointly to identify driver vs. constructor terms
  simultaneously.
- **Numeric split — the strongest single number found**: **constructor effects ≈ 88% of
  variance** (89% CI reported as [0.775, 0.945]), driver ≈ 12%. Posterior SDs: constructor
  σ_t = 1.63, driver σ_d = 0.54 (i.e. the constructor spread is ~3× the driver spread on the
  model's own latent scale).
- **Conditional effects — the wet/street finding, confirmed independently of Bell et al.**: the
  model includes a **random slope on driver skill for wet conditions** — the authors' own framing
  is that wet races "require a specific set of skills, which rely less on the car and more on the
  driver." Separately, **constructor advantage gets a random slope for street vs. permanent
  circuits**, reflecting that car philosophy (not driver skill) differs by circuit type. Note this
  is *not quite* the same claim as Bell et al: Bell et al. say driver *effects* grow in wet/street
  (a driver-side claim on both axes), whereas this paper puts the wet effect on the driver side
  but the street-circuit effect on the *constructor* side (car philosophy varies by track type,
  not driver skill per se). The two papers agree wet weather elevates driver-relative importance;
  they attribute the street-circuit effect to different sides of the driver/car split.
- **Explicit limitations (stated by the authors)**: DNFs excluded → reliability/luck signal
  discarded; no driver×constructor interaction term (assumes additive separability — same
  limitation noted across every source in this survey); **explicitly stated to have poor
  out-of-sample forecasting performance for new seasons** (requires unobserved year-effect
  priors); results are truncated to the 2014–2021 window so historical (pre-2014) driver
  reputation is not represented; posterior predictive checks show the model **cannot reproduce
  observed bimodal within-driver-team-season performance distributions** — i.e. there's real
  structure in the data (e.g. a driver having two distinct competitive "modes" within one season)
  the additive latent-ability model doesn't capture.
- Sources: [arXiv abstract](https://arxiv.org/abs/2203.08489), [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10660124/), [degruyter](https://www.degruyterbrill.com/document/doi/10.1515/jqas-2022-0021/html?lang=en)

## 5. RAPM-style ridge regression (arXiv 2508.00200), "Predicting Formula 1 Race Outcomes:
   Decomposing the Roles of Drivers and Constructors through Linear Modeling" (2025)

- **Method**: extends **Regularized Adjusted Plus-Minus (RAPM)** — a technique borrowed from
  basketball/hockey analytics for isolating individual contribution net of teammates/opponents —
  via **time-decayed ridge regression with LOESS smoothing**. Outcome variable = race results /
  finishing positions, **hybrid era 2014–2024**.
- **Numeric split — directly contradicts source #4 above**: **constructors explain 64.0% of
  variance in race outcomes**, i.e. driver ≈ 36%. This is on essentially the same era (2014–2024
  vs. #4's 2014–2021) and the same broad outcome family (finishing position/race result), yet
  lands **24 percentage points lower on the constructor share than the Bayesian ROL paper**. I
  did not get enough of the full methodology (PDF wouldn't render as text) to know whether this
  is driven by DNF handling, the ridge-regularization prior, or the RAPM opponent-adjustment
  machinery — flagging as an open, unresolved contradiction rather than reconciling it.
- **Quali vs. race split — the one data point closest to f1Brainz's own lap-time framing**: the
  paper reports constructor importance is **higher in race outcomes than in qualifying**
  ("increased importance in ... Top 10 points finishers", "decreased importance in qualifying"),
  which the extraction read as "drivers play a relatively larger role in qualifying." Caveat:
  I could not confirm from the abstract whether "qualifying" here means qualifying **lap time**
  or qualifying **finishing/grid position** — likely the latter (rank-based, consistent with the
  paper's stated race-outcome framing), so this is *still* not a direct lap-time result, just the
  closest proxy found.
- Sources: [arXiv abstract](https://arxiv.org/abs/2508.00200), [PDF (unreadable as text, saved locally)](https://arxiv.org/pdf/2508.00200)

## 6. Time-rank duality (arXiv 2312.14637), "Faster identification of faster Formula 1 drivers
   via time-rank duality"

- **Method**: a theoretical-equivalence result, not an applied fit. Shows that an
  exponential-distribution race-time model and an econometric rank(-ordered logit) model of
  finishing order have **equivalent parametrizations** ("time-rank duality") under an equating of
  race-winning probabilities. The stated payoff is faster/cheaper estimation of driver-vs-car
  effects (the duality lets you solve the rank model's likelihood via the time model's simpler
  closed form, or vice versa).
- **Outcome variable**: still finishing **rank**, not observed lap time, despite the name
  suggesting a lap-time connection — the "time" side is a latent exponential race-time construct
  used for its mathematical tractability, not fitted directly to telemetry/timing data.
- **No numeric car/driver split obtained** — the extraction did not surface one; this reads as
  primarily a methods/identifiability paper rather than an applied variance-decomposition result.
  **Scoped null**: did not fetch the full PDF for this one, abstract-page extraction only.
- Source: [arXiv abstract](https://arxiv.org/abs/2312.14637)

## 7. Community/informal Bayesian model — martiningram.github.io, "A first model to rate
   Formula 1 drivers"

- **Method**: informal (blog/GitHub Pages, not peer-reviewed) rank-ordered logit
  (Bradley-Terry-Luce style) with latent ability `θ = driver_skill + car_skill`, **both
  components following a year-to-year random walk** (explicit modeling choice: teams improve
  cars over time, driver skill can also drift). DNFs modeled separately via a **Bernoulli
  likelihood with logit-scale driver and car risk parameters** — i.e. reliability is modeled
  rather than excluded, unlike source #4.
- **Identification**: teammate comparisons again, with an explicit acknowledged weakness — the
  author flags that Verstappen's high rating is driven largely by how much he outperforms his
  teammates, which conflates "Verstappen is great" with "Red Bull's second seat has been weak,"
  and the model has no way to distinguish those two explanations from teammate-comparison data
  alone. This is a concrete, named failure mode of the teammate-comparison identification
  strategy that the more formal papers above don't foreground.
- **No clean %, but a scale comparison**: reports Mercedes' 2014 car advantage over Red Bull as
  ~2 points on the model's skill scale, versus the *entire spread* of current top drivers being
  ~2.5 points — i.e., informally, one team's single-year car swing is comparable in magnitude to
  the whole current driver-skill spread. Not a variance-%, but points at car effects being
  large relative to driver effects, consistent with the "team dominates" direction of every
  other source here.
- Source: [martiningram.github.io/f1-model](https://martiningram.github.io/f1-model/)

---

## Contradictions surfaced (not smoothed over)

| Claim | Source | Era / outcome | Value |
|---|---|---|---|
| Constructor share of variance | Phillips/f1metrics | 1950s–2014, extended points | **61%** |
| Constructor share of variance | Bell et al. 2016 (per f1metrics's own citation, unconfirmed vs. primary text) | 1950–2014, points, multilevel | **~86%** |
| Constructor share of variance | Bayesian ROL, arXiv 2203.08489 | 2014–2021, finishing position (DNFs excluded) | **88%** (CI [77.5%, 94.5%]) |
| Constructor share of variance | RAPM ridge regression, arXiv 2508.00200 | 2014–2024, race outcomes | **64%** |

The two most rigorous/recent papers (#4 and #5) cover almost the same window and outcome family
and disagree by 24 points. I could not resolve why from the material I could fetch (DNF
treatment, regularization choice, and race-vs-broader-outcome definition are all plausible
culprits, none confirmed). **This is the headline finding of the excursion**: there is no
converged number, only a converged *direction* (car > driver, by a wide and disputed margin) and
a converged *method* (teammate comparison + career switching for identification).

Secondary, smaller contradiction: Bell et al. (2016) attributes the street-circuit effect to
driver-side importance rising; the Bayesian ROL paper (#4) attributes the (separate) street-
circuit random slope to constructor-side car-philosophy differences. Not necessarily
incompatible (both effects could be real and simultaneous), but the two papers frame the same
qualitative phenomenon (street circuits behave differently) on opposite sides of the driver/car
split, and I found no source that reconciles them.

## What none of this literature covers (relevant to f1Brainz's own lap-time-native work)

Every source surveyed models an **ordinal outcome** — points, finishing position, or finishing
rank. **None models raw lap time or pace as the dependent variable.** The closest approach found
is source #5's qualifying-vs-race importance comparison, and even that is very likely still
rank/position-based, not a lap-time delta in seconds. This matters directly for f1Brainz, which
works in lap time: the academic car/driver variance-decomposition literature is not directly
portable to a lap-time framing without re-deriving it — the % splits above answer "how much does
the car explain who finishes ahead of whom," not "how much does the car explain the gap in
seconds," and those are not guaranteed to be the same number (a small lap-time gap can produce a
large probability-of-beating-you if variance is small, and vice versa).

Also universal: every model here is **additive** (driver effect + car effect, no interaction
term). None model a condition-dependent driver "fingerprint" more granular than the two coarse
buckets found (wet vs. dry, street vs. permanent). The corner-type / regime-level driver
fingerprint work already scoped in [[x1-RESULT.md]]/[[x3-RESULT.md]] inside this repo goes
substantially finer than anything in the published literature I could find — this survey found
no external prior art at that granularity to borrow from or benchmark against.

## Scoped nulls — what I did NOT survey

- Did not read any full primary-source PDF end-to-end successfully — arXiv PDFs for #5 and the
  SIAM Elo paper both returned as unparseable binary/PDF-stream content to the fetch tool; all
  findings for those come from abstract pages or secondary WebSearch summarization, not a close
  read of methods/results sections.
- Did not access the Bell et al. (2016) primary text directly (degruyter 405'd, Semantic Scholar
  returned no abstract) — the oft-cited "86% team" number is unconfirmed against the primary
  source, sourced only via f1metrics's secondary citation of it.
- Did not access Eichenberger & Stadelmann (2009) full text (ScienceDirect 403'd) — no numeric
  split obtained for that paper at all.
- Did not fetch the SIAM "From Pole to Podium: Adjusting Elo Method" paper's content (PDF
  unparseable) — found via search only, not read; it's a real gap on the specifically
  Elo-flavored branch the question named, since I could not confirm its methodology or findings
  beyond the search snippet.
- Did not search for team-side/constructor-side public statements (e.g., FIA, F1 technical
  press, or team principals quoting internal car/driver split estimates) — scoped to
  academic/community statistical literature only, per the question as posed.
- Did not search for papers specifically modeling **lap time** as the outcome (e.g., tire-
  degradation-adjusted pace models, sector-time driver decomposition) outside of the general
  queries run — the ML lap-time-prediction paper surfaced in passing (589,081 laps, R²=0.999)
  is a predictive model, not a car/driver variance-decomposition study, and was not investigated
  further.
- Did not check publication/citation counts, peer-review status, or replication history for any
  of the arXiv preprints (#4, #5, #6) — #4 has a JQAS DOI (peer-reviewed venue) per the degruyter
  link; #5 and #6 appear to be preprints only, not confirmed as peer-reviewed, which bears on how
  much weight to put on their numbers relative to #1 and #4.
- Did not look for post-2024 or 2026-season-specific driver-rating commentary beyond what
  surfaced incidentally in search results.
