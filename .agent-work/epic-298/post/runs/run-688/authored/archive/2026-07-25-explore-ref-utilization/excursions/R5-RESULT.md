# R5 — Track Evolution: Prior Art Across Tyre Literature, Team Practice, and F1 Analytics

Question: how do engineering literature and analytics practice model track grip evolution (a) WITHIN a session, (b) BETWEEN sessions of a weekend, and (c) for FP-to-qualifying pace correction?

Method: web search + fetch across three lanes — tyre/pavement literature, motorsport-engineering trade commentary, and F1 analytics/betting practice. No academic paper was found that directly models F1 track evolution with a fitted functional form and published coefficients; the strongest quantitative source is a hobbyist data-science writeup (Renville) and a race-sim developer's devlog (The Undercut), both triangulated against qualitative team/press commentary. Treat magnitudes as approximate, not calibrated truth.

---

## 1. Mechanism (why grip changes at all)

Track evolution has two physically distinct contributors that the general-audience sources conflate but that matter for modeling:

1. **Rubber deposition ("rubbering-in").** Tyres shed rubber under load (braking, traction, high lateral-g cornering); viscoelastic rubber-on-rubber contact has higher friction than rubber-on-bare-asphalt. Deposition is concentrated in braking zones and apex/corner-exit zones, much less in acceleration zones and straights — i.e., evolution is *spatially non-uniform by construction*, not just in effect. [Friction One](https://frictionone.us/rubbering-in-the-essentials-of-motorsport-friction/), [F1 Chronicle](https://f1chronicle.com/how-is-racetrack-grip-maintained/)
2. **Surface cleaning / debris removal.** Independent of rubber, repeated passes clear dust, marbles, and loose aggregate, especially early in a weekend on a track that's been idle (or used by road traffic, as on street circuits). This is why the *very first* laps of a weekend show large gains that are not pure rubber-laydown. [Catapult](https://www.catapult.com/blog/race-strategy-f1-track-surface), [Motorsportscalendar glossary](https://motorsportscalendar.com/glossary/track-evolution)

Pavement-engineering literature on tyre-polishing (not F1-specific, but the underlying surface-tribology process) shows the friction-vs-wear-cycles curve is **non-monotonic at long horizons**: dynamic friction coefficient rises with initial polishing (macrotexture voids filling — same mechanism as rubber deposition), peaks, then *declines and stabilizes* as the aggregate itself polishes smooth over many more cycles than a single race weekend would ever apply. [ScienceDirect: asphalt polishing/friction study](https://www.sciencedirect.com/science/article/abs/pii/S0950061822009461) This is a caution against extrapolating an F1 weekend's monotonic-rise regime indefinitely — it's the front slice of a curve that eventually turns over, just not within 3 days of on-track running.

---

## 2. Within-session functional form

**Best quantitative source found:** Colin Renville's 2021-season FastF1-based analysis fit lap time via a GAM with *session progress* (running total of laps completed by the whole field, i.e., cumulative car-laps, not wall-clock time or own-driver lap count) as the primary predictor, holding tyre compound and team fixed, restricted to Q3 drivers to control for car-performance variance. [colinrenville.com](https://www.colinrenville.com/posts/exploref1/)

- Result: **non-linear** improvement curves; magnitude ≈ **0.75–1.0s (≈1.2%) average improvement from session start to end at Abu Dhabi** (a "typical" low-street-cleaning permanent circuit).
- Circuit-to-circuit variance is large: Mexico City showed the steepest early decrease and biggest percent change; Portugal (Portimão) showed the least. Explanation offered was surface characteristics / off-weekend track usage frequency, not track type per se.
- Key methodological point for de-trending: **cumulative car-laps**, not elapsed minutes, is the chosen evolution axis — consistent with the physical mechanism being rubber-deposition-per-pass, not time-per-se (temperature is a separate, session-time-correlated confound layered on top).

**A second, independent functional form** comes from a hobbyist race-sim's rubber-accumulation model (The Undercut devlog), which is engineering-practice-adjacent but not a published F1 team method — flag it as illustrative, not authoritative:

```
rubber_fraction = 1 − (1 − initial) · e^(−rate · cumulative_car_laps)
```
with rate ≈ 0.003/car-lap and initial ≈ 10–30% at a fresh session start. This is a **saturating exponential in cumulative laps**, matching Renville's qualitative "front-loaded gains, plateauing" shape and matching the pavement-polishing literature's early-cycle rise phase. [The Undercut devlog-003](https://www.the-undercut.com/blog/devlog-003/)

That source also assigns **zone-differentiated intensity** to the deposition (braking 85%, cornering 55%, acceleration 25% of max effect) and a **lateral falloff off the racing line** (`e^(−distance²·4)`) — i.e., its internal model treats evolution as a 2D field over the track surface, not a scalar. This directly corroborates the qualitative per-corner evidence in §5 below, and would only cite as "one practitioner's inductive model," not a validated F1 dataset fit.

**No source gave a session-time (minutes-elapsed) functional form as primary** — every quantitative or semi-quantitative source keyed off cumulative laps run, consistent with the physical mechanism.

---

## 3. Between-session (inter-session) offset problem

This is the weakest-evidenced part of the survey — no source directly modeled "how rubbered does session N start relative to where session N−1 ended."

What is established qualitatively:
- **No reset between adjacent dry sessions.** Rubber/cleaning gains carry forward: FP1 → FP2 → FP3 → Q → Race is treated by every source as monotonically increasing grip absent a reset event, i.e., the state variable (cumulative laps) keeps accumulating across session boundaries rather than restarting at zero each session. The Undercut's devlog is explicit about this for its own model ("qualifying starts with 10–30% rubber," "race starts where qualifying left off" — no reset), and is consistent with press-level commentary that Saturday quali is run on a Friday-evolved track and the race inherits Saturday's state. [The Undercut](https://www.the-undercut.com/blog/devlog-003/)
- **Rain is a hard reset**, not a gradual decay: water washes deposited rubber off, returning the track close to "green," including erasing support-race contributions. If a wet session intervenes between the last dry session and the one you're correcting to, the cumulative-laps state variable should be treated as reset (or heavily decayed) rather than carried forward. Multiple sources converge on this qualitatively but none quantify the residual grip fraction after a rain event. [F1technical forum](https://www.f1technical.net/forum/viewtopic.php?t=6937), [FlowRacers](https://flowracers.com/blog/green-track-f1/)
- **Support-race contribution is additive to the same cumulative-lap ledger.** F2/F3/Porsche Supercup laps on the same circuit before FP1 or between F1 sessions are described as materially advancing evolution — meaning an FP1 grip *level* is not comparable across venues/weekends purely from F1's own lap count; the support-race calendar for that circuit needs to enter the cumulative-laps state too. No source gives a per-support-car-lap weight relative to an F1 car-lap (plausible confound: lighter/slower cars may deposit less rubber per lap than F1 cars, but this wasn't found addressed anywhere). [Formula1.com support-race scheduling](https://www.formula1.com/en/latest/article/f1-to-be-supported-by-f2-and-f3-at-all-8-opening-races.31icxDcxgfbTROwpxRJBVp)
- **Sprint weekends compress the ledger.** Only one practice session (FP1) precedes Sprint Qualifying, so the cumulative-car-laps count entering SQ is structurally much lower than a conventional weekend's Q — sources treat this as a genuine grip/setup deficit going into SQ, not merely a compressed schedule. This is a clean, low-ambiguity signal for any model that keys evolution off cumulative laps: sprint-format weekends need a distinct, lower lap-count prior at the SQ/Q boundary. [Sky Sports 2026 sprint format](https://www.skysports.com/f1/news/12040/13518235/f1-sprint-schedule-points-results-format-explained-qualifying-race-and-venues-for-2026-season)

No source proposed or validated a decay/half-life for grip *between* sessions absent rain (e.g., does an 18-hour overnight gap between FP2 and FP3 cost any grip from oxidation, oil residue, cleaning-crew activity, or wind?). This is a genuine gap, not a suppressed finding — flagged as Null 1 below.

---

## 4. FP-to-qualifying pace correction in analytics/betting practice

Practitioner consensus (not a single rigorous published method, but converging trade practice):

- **FP2 long-run (high-fuel, race-sim) pace is treated as the highest-value input**, precisely because it's least contaminated by the specific evolution-state-at-that-moment problem that plagues single-lap comparisons — teams' race-sim laps are compared to each other *within* the same tight window of the session, so the evolution confound is roughly constant across the field at that moment, though not corrected for outright. FP1 is treated as unreliable (exploratory programs, low sample), FP3 as a secondary confirmation limited by short duration and quali-prep contamination. [TrackSims](https://www.tracksims.com/unauthorized)
- **Raw practice classification is explicitly distrusted as a ranking** because of unequal fuel loads, tyre ages, and run priorities across drivers — the correction practitioners describe is *program-normalization* (fuel-corrected pace, "Q-sim vs race-sim" run classification) more than an explicit additive track-evolution term. TrackSims' marketed methodology (fuel-corrected pace + Q-sim/race-sim separation across 24 circuits) is the most concrete named commercial approach found, though its internal formula is not public. [TrackSims](https://www.tracksims.com/unauthorized)
- **No source described an explicit additive/multiplicative track-evolution correction term being applied to reconcile an FP1 lap against a Q lap** (e.g., "+0.8s expected FP1→Q gap, subtract before comparing pace"). The Renville GAM is the closest thing to that correction being formalized, but it was built as retrospective analysis, not as a live betting/prediction correction pipeline. This is the second explicit gap — flagged as Null 2 below.
- Teams themselves are described (at a qualitative, press-commentary level) as timing their final Q attempts to land in the last minutes of the session specifically because they expect the track to still be evolving at that point — i.e., team practice treats "grip at lap X of Q" as a live, non-stationary target they're chasing, reinforcing that the cumulative-laps-within-session model (§2) is the operative mental model on pit walls too, not a fixed FP-to-Q offset. [SportsRush](https://thesportsrush.com/f1-news-what-is-track-evolution-in-f1-and-how-does-it-happen/), [FlowRacers green track](https://flowracers.com/blog/green-track-f1/)

---

## 5. Per-corner / per-sector evidence

Evidence is directional, not quantified:
- Rubber deposition is heaviest in **braking zones and corner apexes**, lightest on **straights/acceleration zones** — this is stated as mechanism (§1) and echoed in sector-analysis commentary: sectors with more on-line corner content evolve more than straight-dominated sectors. [ScuderiaFans sector analysis](https://scuderiafans.com/f1-technical-analysis-aerodynamic-load-and-track-types-here-are-all-the-secrets/)
- The Undercut's practitioner model operationalizes this as a **zone-weighted intensity** (braking 85% > cornering 55% > acceleration 25% of the deposition effect) plus a **lateral-distance falloff off the racing line**, i.e., its internal representation is literally a 2D heat-field over the track, informed by corner/braking-zone geometry, not a scalar-per-lap number. [The Undercut](https://www.the-undercut.com/blog/devlog-003/)
- No source gave a controlled comparison isolating whether *high-load* (high lateral-g) corners specifically evolve faster/more than low-load corners as a distinct claim from "corners vs straights" — the braking-zone claim is about longitudinal load (braking), and the apex claim is stated but not decomposed by corner speed/load class anywhere found. This is Null 3.

---

## 6. Magnitudes summary table (approximate, mixed rigor)

| Claim | Magnitude | Source rigor |
|---|---|---|
| Full-weekend (Friday AM → Saturday Q) improvement, general dry permanent circuit | ~2s cited illustratively (1:32 → 1:30) | Qualitative press framing, not a fitted study |
| Abu Dhabi 2021, session-start→end (Q only) | 0.75–1.0s (~1.2%) | GAM fit, single hobbyist analysis, one season |
| Cross-circuit spread of that same metric | Mexico City steepest, Portimão flattest | Same source, descriptive only |
| Street circuit FP1→Q evolution | "Several seconds," qualitatively larger than permanent circuits | Multiple qualitative sources agree directionally; no paired numeric comparison found |
| Rain reset | Track returns to near-"green" state | Universal qualitative agreement; no residual-grip fraction quantified |
| Sprint-weekend SQ grip deficit vs standard-weekend Q | Directionally present (fewer laps banked) | Qualitative only |

---

## Scoped nulls

1. **No inter-session decay/carryover model found.** Nothing quantifies how much (if any) grip is lost or retained across a dry overnight gap between sessions, or gives a residual-grip fraction after a rain reset. If f1Brainz needs this, it would have to be estimated from the DB's own session_classifications / lap data rather than borrowed from literature.
2. **No explicit FP→Q additive/multiplicative correction formula found in analytics or betting practice.** The trade converges on *program-normalization* (fuel/tyre-age/run-type correction) rather than a stated track-evolution offset term. Renville's GAM is retrospective research, not a documented live-correction pipeline anyone publishes.
3. **No load-class-specific (high-g vs low-g corner) evolution comparison found**, only the broader braking-zone/apex vs straight distinction. Claims about "high-load corners evolve more" would need to be derived from f1Brainz's own telemetry, not cited to this survey.
4. **No peer-reviewed/academic paper modeling F1 track evolution directly was located** (the arXiv qualifying-predictive-power paper found does not touch track evolution at all despite matching the search terms). The strongest quantitative source (Renville) is a personal data-science blog post, one season, one method (GAM on FastF1 data) — not independently replicated. The pavement-tribology literature is real peer-reviewed material but is about generic asphalt wear over far longer horizons (thousands of polishing cycles) than a race weekend, so its long-run friction *decline* phase is informative as a boundary condition, not directly transferable magnitude-wise.
5. **No per-support-series lap-weighting found** (F2/F3/Porsche laps vs F1 laps contributing unequally to the shared rubber ledger) — flagged in §3, unresolved.

## Sources
- [Renville — Analyzing Track Evolution during the 2021 F1 Season](https://www.colinrenville.com/posts/exploref1/)
- [The Undercut — devlog-003, Track Evolution & the Rubber Line System](https://www.the-undercut.com/blog/devlog-003/)
- [Friction One — Rubbering In: The Essentials of Motorsport Friction](https://frictionone.us/rubbering-in-the-essentials-of-motorsport-friction/)
- [F1 Chronicle — How Is Racetrack Grip Maintained?](https://f1chronicle.com/how-is-racetrack-grip-maintained/)
- [Catapult — How Track Surface & Temperature Impact F1 Race Strategy](https://www.catapult.com/blog/race-strategy-f1-track-surface)
- [Motorsportscalendar — Track Evolution glossary](https://motorsportscalendar.com/glossary/track-evolution)
- [ScienceDirect — Evolution characteristics of surface texture of wearing course, accelerated pavement polishing](https://www.sciencedirect.com/science/article/abs/pii/S0950061822009461)
- [ScuderiaFans — F1 technical analysis: aerodynamic load and track types](https://scuderiafans.com/f1-technical-analysis-aerodynamic-load-and-track-types-here-are-all-the-secrets/)
- [F1technical.net forum — What is the "rubbering in" of a track?](https://www.f1technical.net/forum/viewtopic.php?t=6937)
- [FlowRacers — What Is A Green Track In F1?](https://flowracers.com/blog/green-track-f1/)
- [TheSportsRush — What Is Track Evolution in F1 and How Does It Happen?](https://thesportsrush.com/f1-news-what-is-track-evolution-in-f1-and-how-does-it-happen/)
- [TrackSims — F1 Practice Pace Analytics for Betting & DFS](https://www.tracksims.com/unauthorized)
- [Sky Sports — F1 Sprint 2026 format explainer](https://www.skysports.com/f1/news/12040/13518235/f1-sprint-schedule-points-results-format-explained-qualifying-race-and-venues-for-2026-season)
- [Formula1.com — F2/F3 support race scheduling](https://www.formula1.com/en/latest/article/f1-to-be-supported-by-f2-and-f3-at-all-8-opening-races.31icxDcxgfbTROwpxRJBVp)
- [arXiv 2507.10966 — Evaluating the Predictive Power of Qualifying Performance in F1](https://arxiv.org/abs/2507.10966) (checked directly — does not cover track evolution despite matching search terms; cited to document the null)
- [Glama — pitstop MCP get_track_evolution tool](https://glama.ai/mcp/servers/@praneethravuri/pitstop/tools/get_track_evolution) (documents intent to expose lap-by-lap evolution deltas from FastF1 data; no formula disclosed)
