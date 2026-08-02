# R3 — Golf course-fit / venue-fit analog for driver-fingerprint × circuit-fingerprint

**Question:** how do other sports model "player skill-by-category × venue composition"
priors — the structural analog of our driver-fingerprint × circuit-fingerprint join — and
how big do venue-fit effects turn out to be?

**Headline:** golf is the closest structural analog and it is a mature, heavily-scrutinized
field — and the mature-field verdict is a caution, not a green light. DataGolf's own
published course-fit adjustments are small for the vast majority of player-course pairs
(±0.07 strokes/round at the 25th/75th percentile; only a small tail of extreme mismatches
reach ~1 stroke/round), and an independent 119k-round walk-forward replication test found
that once you strip out a player's overall skill level (z-scored), the residual "shape
match" between a player's skill profile and a course's demand profile has **zero**
out-of-sample predictive power (r ≈ −0.019) — the author's summary: "course fit is mostly
just being good." Baseball park factors are the other established venue-effect field, but
they are a *different animal*: physically-grounded (altitude, dimensions, air), not a
skill-crossed interaction, genuinely large at the extremes (Coors Field ~120 index, i.e.
+20% run scoring vs average), and still require heavy multi-year shrinkage (empirically
~38% regression-to-mean even after 3-year averaging) before being trusted. NBA and soccer
have no comparable published skill-category × venue-characteristic effect-size literature —
their "fit" concepts (gravity/spacing archetypes, style-fit scouting tools) are about
player-teammate/scheme fit, not a fixed venue prior, and I found no analog to publish.

---

## 1. Golf — DataGolf course-fit methodology (primary target)

### Estimation structure — the direct analog
DataGolf decomposes every player's skill into four strokes-gained (SG) categories
established by Mark Broadie's Columbia research and used league-wide by the PGA Tour:
off-the-tee (OTT), approach (APP), around-the-green (ARG), putting (PUTT). This is the
golf equivalent of a per-channel driver fingerprint rather than one scalar "good/bad"
rating. [DataGolf Skill Decompositions](https://datagolf.com/player-skill-decomposition),
[DataGolf Predictive Model Methodology](https://datagolf.com/predictive-model-methodology/).

Each course gets a **demand vector**: a regression of which SG categories actually
correlate with low scores at that specific venue. Published examples: Augusta National
weights APP 31% / ARG 24%; Bethpage Black weights OTT 30% — i.e., courses have measurably
different "shapes" of what they reward, same as a circuit-fingerprint would encode
braking-heavy vs traction-heavy vs high-speed-corner composition.
[Golf course fit magnitude/examples via SharpSide search summary — see Sources]

### Shrinkage — category-dependent, and it's the load-bearing design choice
DataGolf's regression coefficients for predictive persistence by category are reported as
β_OTT=1.2, β_APP=1.0, β_ARG=0.9, β_PUTT=0.6 — off-the-tee skill is the *most* persistent
and needs the *least* shrinkage; putting is the noisiest/least persistent and needs the
**heaviest** mean-reversion, especially on short samples. Practically: a short-term putting
hot streak gets pulled hard back toward the player's baseline, while an OTT distance gain
gets believed more readily. [DataGolf Predictive Model Methodology](https://datagolf.com/predictive-model-methodology/)

**The critical negative finding, stated explicitly by DataGolf itself:** they tried the
naive approach first — raw course-history averaging (how has this player scored at this
course historically) — and abandoned it because it was "mostly just a noise mine." Their
working replacement is a **random-effects model** estimating how golfer *attributes*
(driving distance, accuracy, approach, short game, putting) interact with course-specific
random effects, not a raw per-player-per-course outcome average.
[DataGolf Predictive Model Methodology](https://datagolf.com/predictive-model-methodology/)

### Magnitude — DataGolf's own numbers
Course-fit adjustments range from −0.93 to +0.95 strokes/round at the extremes, but the
**25th/75th percentile band is only ±0.07 strokes/round** — for the great majority of
player-course pairings the fit adjustment is nearly negligible. Named exception: Brian Gay
got a +0.9 strokes/round adjustment at El Camaleón (accuracy specialist at an
accuracy-rewarding course) — the tail case, not the median. Separately, ~25% of
round-to-round scoring *variance* across the Tour is attributable to course difficulty
characteristics (a course-level property, distinct from player-course fit).
[DataGolf Predictive Model Methodology](https://datagolf.com/predictive-model-methodology/)

### Replication test — the part that matters most for us
Independent analysis (Hayden Kreikemeier, Medium, 2026; 118,920 PGA Tour rounds, 117
courses, 2018–2026, walk-forward validated, min. 40 rounds/player and 200 rounds/course,
30,499 player-events tested):
- Built the same demand-vector structure as DataGolf (per-course regression of which SG
  categories predict scoring).
- Tested two things: (1) a skill-weighted dot-product projection (player skill · course
  demand) → **r = 0.275** to actual performance — looks good, but this is dominated by
  players' overall skill level, not fit shape.
- (2) A pure **shape-match** test: z-score out each player's overall skill first, then
  measure cosine similarity between the residual skill-profile shape and the course
  demand vector → **r = −0.019**, indistinguishable from zero.
- Conclusion: "course fit is mostly just being good" — once you control for being an
  elite, well-rounded player, the specific alignment between your skill profile and the
  course's demand profile adds essentially nothing predictive out-of-sample.
[I analyzed 119,000 PGA Tour rounds to test whether course fit is real — Hayden Kreikemeier, Medium](https://medium.com/@haydenmk715/i-analyzed-119-000-pga-tour-rounds-to-test-whether-course-fit-is-real-acc036a04a9d)

This is a genuine tension worth naming: DataGolf (the commercial, revenue-motivated
provider) still ships course-fit adjustments and describes them as valuable; an
independent, out-of-sample replication attempt using a comparable method found the
*residual* fit effect (after controlling skill) washes out. Both can be true at once —
DataGolf's adjustments may be doing useful work mostly by getting the *category-level
skill estimates* right (the β-weighted, shrunk SG decomposition), with the *course-crossed*
term contributing a small tail correction on top, not a broad signal.

---

## 2. Baseball — park factors (secondary target)

### Estimation structure
Modern approaches use regression (ridge or logistic) treating each plate appearance as a
batter × pitcher × park interaction, rather than simple home/road run ratios, allowing
simultaneous adjustment for opponent quality. [Park factor estimation improvement using
pairwise comparison method, arXiv:2109.09287](https://arxiv.org/abs/2109.09287);
[FanGraphs Park Factors](https://library.fangraphs.com/principles/park-factors/)

### Shrinkage
FanGraphs uses 5-year regressed park factors. Phil Birnbaum's variance decomposition
(3-year averages): observed SD=4.8, true SD=4.3, luck SD=2.1 → naive statistics say ~20%
regression-to-mean is enough to recover the "true" 3-year park effect, but empirically
**38%** regression is needed to project forward to predict a *future single year* — i.e.,
even a well-measured, physically-grounded venue effect needs roughly double the shrinkage
that naive noise-variance math would suggest, because the park itself isn't perfectly
stable year to year (weather patterns, fence/dimension tweaks, humidor changes).
[Sabermetric Research: Regressing Park Factors, Parts I–III, Phil Birnbaum](http://blog.philbirnbaum.com/2020/03/regressing-park-factors-part-i.html)

### Magnitude — genuinely large at the extremes, unlike golf course-fit
Index scale, 100 = average. A 105 park factor = +10% run scoring vs average. Coors Field
is famously ~120 (thin, warm, high-altitude air aids ball carry); most parks cluster much
closer to 95–105. Unlike golf's player-course *fit* term (which nets to ~noise after
controlling skill), baseball park factors are a **main effect on the venue alone** — no
skill-crossing needed to see it, and it's large and consistently replicated. This is the
opposite end of the spectrum from golf's fit term and worth keeping distinct: park factors
answer "does this venue inflate/deflate everyone's output," not "does this specific
player's skill shape match this specific venue" — the latter (golf's actual course-fit
question, and ours) is the harder, noisier one.

---

## 3. NBA / soccer — scoped null (secondary target)

No published, quantified skill-category × venue-characteristic effect-size literature
analogous to golf course-fit or baseball park factors was found for either sport.

- **NBA:** "gravity," "spacing," and lineup/archetype-fit models are real and
  well-developed (ridge-regression-estimated gravity, archetype-conditioned scoring
  gravity), but they quantify player-*teammate*/scheme fit — a moving target that changes
  with roster construction — not a fixed venue prior. The closest true venue effect
  (Denver altitude) is treated as a minor single-scalar home-court adjustment, not a
  skill-crossed model, and no magnitude estimate for it turned up in this pass.
  [Quantifying Gravity in the NBA With Ridge Regression, The Spax](https://www.thespax.com/nba/quantifying-gravity-in-the-nba-with-ridge-regression/)
- **Soccer:** recruitment platforms (StatsBomb IQ, SkillCorner) publish "playing style"
  and archetype-fit tools for matching a player's profile to a club's system, but this is
  scouting-workflow guidance, not a validated, published statistical effect size. No
  analog to DataGolf's ±0.07-strokes number or baseball's park-index number was found.
  [Using StatsBomb IQ For Player Recruitment](https://blogarchive.statsbomb.com/articles/soccer/using-statsbomb-iq-for-player-recruitment/),
  [Contextual Scouting: The Art of Complementary Squad Building, SkillCorner](https://skillcorner.com/articles/contextual-scouting-the-art-of-complimentary-squad-building-1-2)

Read this null as: the "here's a mature field with a rigorously tested, published
skill×venue effect-size number" pattern really only exists in golf and baseball among the
sports checked. NBA/soccer "fit" work is real but answers a different question
(teammate/scheme fit) and hasn't been effect-sized the way DataGolf and sabermetrics have.

---

## 4. Transferable patterns for driver-fingerprint × circuit-fingerprint

1. **Per-category skill, not a scalar rating, crossed with a per-venue demand vector** —
   the structure golf and baseball both converge on, and the structure already implied by
   "driver-fingerprint × circuit-fingerprint." Both fields decompose skill into channels
   with materially different persistence/noise properties (OTT vs PUTT; a hitter's true
   talent vs park-driven variance) rather than fitting one combined number.

2. **Category-dependent shrinkage is not optional** — the channel with the lowest
   persistence (putting) gets the heaviest regression-to-mean; the highest-persistence
   channel (OTT/driving) gets the least. Whatever the driver-observable channels turn out
   to be, expect them to need *different* shrinkage strengths, not one global regularizer.

3. **Raw historical averaging at the venue is a known trap, confirmed by the one provider
   who tried it and rejected it.** DataGolf explicitly abandoned raw course-history
   averaging as "mostly a noise mine" in favor of a random-effects model over
   attribute×venue interactions. This is a direct warning against any raw
   "driver's historical results at circuit X" feature without an equivalent
   random-effects/regression structure underneath it.

4. **The gate that actually matters is out-of-sample replication of the *residual* fit
   effect after controlling for baseline skill** — not in-sample variance explained, not
   plausibility. Kreikemeier's z-score-then-cosine-similarity test is the concrete
   template: strip skill, then ask whether the leftover shape-match still predicts
   held-out performance. Build that specific test before trusting any driver×circuit
   interaction term as more than "the driver is just good."

5. **Honest effect-size bounds to carry forward, both from mature, heavily-scrutinized
   fields:**
   - Golf (skill-crossed venue *fit*, the closer analog to ours): median-case effect is
     tiny (±0.07 strokes/round, 25th/75th pct.), tail-case effect ~1 stroke/round, and an
     independent replication found the *residual* fit-shape term (after controlling
     skill) is statistically indistinguishable from zero out-of-sample.
   - Baseball (venue *main effect*, not skill-crossed — a different, easier question):
     large and real at the extremes (~+20% at Coors), but even this cleaner, physically
     grounded effect needs ~38% empirical shrinkage and 3–5 years of data to trust.
   - Net: if the F1 driver×circuit interaction resembles golf's fit term (an interaction
     effect on top of already-known individual skill), the prior should assume it is
     **small relative to baseline driver skill** until a held-out replication test
     analogous to Kreikemeier's says otherwise — not assumed real because it's plausible
     or because it explains in-sample variance.

## Sources
- [DataGolf — Skill Decompositions](https://datagolf.com/player-skill-decomposition)
- [DataGolf — Predictive Model Methodology](https://datagolf.com/predictive-model-methodology/)
- [I analyzed 119,000 PGA Tour rounds to test whether course fit is real — Hayden Kreikemeier, Medium (2026)](https://medium.com/@haydenmk715/i-analyzed-119-000-pga-tour-rounds-to-test-whether-course-fit-is-real-acc036a04a9d)
- [Golf Course Fit Tool — SharpSide Golf](https://www.sharpsidegolf.com/tools/course-fit/) (course demand-vector examples: Augusta, Bethpage)
- [FanGraphs — Park Factors (Sabermetrics Library)](https://library.fangraphs.com/principles/park-factors/)
- [Park factor estimation improvement using pairwise comparison method, arXiv:2109.09287](https://arxiv.org/abs/2109.09287)
- [Sabermetric Research — Regressing Park Factors, Parts I–III, Phil Birnbaum](http://blog.philbirnbaum.com/2020/03/regressing-park-factors-part-i.html)
- [Quantifying Gravity in the NBA With Ridge Regression — The Spax](https://www.thespax.com/nba/quantifying-gravity-in-the-nba-with-ridge-regression/)
- [Using StatsBomb IQ For Player Recruitment — StatsBomb](https://blogarchive.statsbomb.com/articles/soccer/using-statsbomb-iq-for-player-recruitment/)
- [Contextual Scouting: The Art of Complementary Squad Building — SkillCorner](https://skillcorner.com/articles/contextual-scouting-the-art-of-complimentary-squad-building-1-2)
