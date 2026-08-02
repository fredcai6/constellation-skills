# R4 — Telemetry-derived observables that discriminate between drivers

**Question:** which telemetry-derived observables has driver-identification/fingerprinting
and driving-style-characterization research found actually discriminative between drivers?

**Headline:** the literature splits into three streams of very different maturity. Road-car
**driver fingerprinting** (CAN-bus/OBD-II, 15-72 drivers, ML classifiers) is the largest and
most quantified body — brake-pedal and accelerator-pedal *dynamics* (not raw position) are
repeatedly named the most individually-identifying signals, steering-wheel-only models reach
usable accuracy, and there's a real, well-documented **null**: accuracy collapses as driver
count grows and depends heavily on route/turn (some turns discriminate 2 drivers at >90%,
others near chance) — i.e. a chunk of the reported signal is context, not driver identity.
Racing-specific academic work is thin: one directly-on-point paper exists (Löckel et al.,
professional race drivers, DIMRA algorithm) but it's paywalled and I could not extract its
feature ranking — flagged as a genuine gap, not a null. Sim-racing analytics is the newest
and best-instrumented stream but answers an adjacent question (what separates a **fast** lap
from a **slow** one, clustered by lap time) rather than driver identity directly; its findings
overlap heavily with what motorsport engineers already assert qualitatively (trail-braking
duration, steering-angle variation, oversteer frequency). The one hard sampling-rate ceiling:
fine-grained braking-modulation/wheel-slip work in the literature runs at 500–4000 Hz, well
above our 10–20 Hz — anything that needs per-wheel ABS-cycle detail is out of reach.

---

## 1. Ranked feature inventory (does this observable discriminate drivers, and can we compute it at 10–20 Hz?)

| Observable | Evidence it discriminates | Computable at 10–20 Hz speed/throttle/brake/gear? |
|---|---|---|
| **Brake pedal dynamics** (pressure profile shape, not just on/off) | Named most individually-informative signal among CAN channels tested; braking-impulse (pressure integral over a ~1.6 s window) + max-pressure classified 30 drivers' braking style at **88.86%** (HMM) vs 82.83% (SVM) vs 77.27% (NN), at 10 Hz — i.e. matches our rate. [Wang et al., HMM braking-style paper, PMC5570378](https://pmc.ncbi.nlm.nih.gov/articles/PMC5570378/) | **Yes** — the discriminative computation (pressure integral/max over a rolling window) only needed 10 Hz brake-pressure samples |
| **Accelerator pedal dynamics** | Repeatedly named alongside brake pedal as carrying the most "biometric" individual signal in CAN-bus driver-ID surveys; used in combination with steering in HMM models reaching 85% at 20 drivers. [Driver-ID feature survey summary](https://www.researchgate.net/publication/315866948_Driver_Identification_Using_Vehicle_Telematics_Data) | Yes |
| **Steering wheel angle — used alone** | A GRU model using *only* steering-wheel time series (no pedals) lifted driver identification for 15 drivers from <15% (near chance) to >65%; on the full 72-driver naturalistic set it beat random guessing by 25×. Longitudinal (pedal) data was independently flagged as "particularly useful" too — steering alone is sufficient but not the whole story. [Doyle et al., "Driver Identification via the Steering Wheel," arXiv:1909.03953](https://arxiv.org/abs/1909.03953) | Yes, at typical logged steering rates |
| **Trail-braking duration / brake-release shape into the corner** | In sim-racing (Assetto Corsa Competizione, 174 drivers, 1327 laps, Brands Hatch), trail-braking duration was one of the top features separating FAST vs SLOW laps alongside speed, lateral accel, steering angle, oversteer. [AI-enabled prediction of sim racing performance, ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2451958824000472) — corroborated qualitatively as a driver "fingerprint" by motorsport telemetry writing (brake-release slope). [F1 telemetry driver-style pieces, see §3] | Yes, shape-of-trace from throttle/brake at 10–20 Hz is enough for duration/slope; sub-lap-second modulation detail is not (see §4) |
| **Steering-angle variation / smoothness during a corner phase** | FAST laps in the ACC study had markedly *lower* steering-angle variation and smaller average angle under braking (−6.5° vs −29.1° for SLOW); oversteer occurrences were 0.24× as frequent. This is style-correlated-with-pace, not proven driver-identity-orthogonal-to-pace — flagged as a distinct claim from pure fingerprinting. [ScienceDirect, above] | Yes |
| **kNN on a broad CAN-bus feature set (15 features)** | 99.99% accuracy for a **2-driver** classification; same method drops to **76.36%** on the **full 10-driver** dataset. Sharpest documented illustration that "high accuracy" claims in this literature are driver-count-sensitive and shouldn't be read as generalizing to a large field. [Machine Learning Approach for Driver Identification Based on CAN-BUS Sensor Data, arXiv:2207.10807](https://arxiv.org/pdf/2207.10807) | Depends on the 15 features chosen; core ones (speed, accel/brake, steering) are within our rate |
| **Per-turn / per-corner discriminativeness is NOT uniform** | Single-turn driver-ID accuracy ranged 55–93.5% (avg 76.9%) for 2 drivers and 33.2–70% (avg 50.1%) for 5 drivers **depending on which turn** — some corners are far more diagnostic of driver identity than others. Directly analogous to the racing-engineer notion of "driver corners." [Driver Identification Using Automobile Sensor Data from a Single Turn, arXiv:1708.04636](https://arxiv.org/abs/1708.04636) | Yes, this is a finding about *where* to look, not a new channel |
| **51-signal broad CAN/OBD-II sweep (engine load, torque, coolant temp, fuel, transmission, wheel velocity, accelerator) at 1 Hz** | 98.72% accuracy with a 40 s window using depthwise-conv+GRU — but note the winning feature subset (15 of 51) leaned heavily on **powertrain/engine** channels, not driving-dynamics channels, and ran at **1 Hz**, below our rate. [Lightweight Driver Behavior Identification, PMC7570946](https://pmc.ncbi.nlm.nih.gov/articles/PMC7570946/) | Only partially — most of what made this model work (engine/fuel/transmission telemetry) is not in our speed/throttle/brake/gear set, and the rate is coarser than ours |
| **Driving-primitive "shape" of speed/accel traces (not just summary stats)** | 75 clustered driving-pattern primitives from naturalistic car-following data; drivers differ measurably in which primitives they use (KL-divergence between drivers' primitive-usage distributions). Supports treating the *trace shape* (not scalar features) as informative — car-following context, not racing, so an analogy not a direct racing result. [Wang et al., "Driving Style Analysis Using Primitive Driving Patterns," arXiv:1708.08986](https://arxiv.org/pdf/1708.08986) | Yes in principle — shape-based features from 10–20 Hz throttle/brake/speed traces |
| **Race-specific: DIMRA metric-ranking (professional race drivers)** | Only directly-on-point academic paper found. Develops a "Driver Identification and Metric Ranking Algorithm" specifically to rank which telemetry metrics separate professional race drivers' styles, paired with an imitation-learning driver model (ProMoD). **Could not extract the actual ranked metric list** — publisher page 403'd, ResearchGate full text blocked, and the author's TU Darmstadt dissertation PDF downloaded but wouldn't OCR/extract in this session. Flagged as the single most important follow-up if someone has institutional access. [Löckel, Kretschi, van Vliet, Peters, "Identification and modelling of race driving styles," Vehicle System Dynamics 60(8), 2022, DOI:10.1080/00423114.2021.1930070](https://doi.org/10.1080/00423114.2021.1930070) — dissertation: [Löckel, "Machine Learning for Modeling and Analyzing of Race Car Drivers," TU Darmstadt (tuprints)](https://tuprints.ulb.tu-darmstadt.de/server/api/core/bitstreams/34ef8bab-62fa-4b26-9b9d-5426678dcaae/content) | Unknown — this is exactly the gap |

---

## 2. What "discriminative" means across the two different questions being asked

Two genuinely different questions keep getting conflated in this literature, and it matters
for how to read the table above:

- **Driver-identity fingerprinting** (road-car CAN-bus papers, steering-wheel paper,
  single-turn paper): given a labeled trace, which driver produced it? This is the literature
  with real accuracy numbers, and its central caveat is that accuracy is highly sensitive to
  driver-pool size and route/context — see the null in §4.
- **Style-vs-pace clustering** (the sim-racing ACC study, and essentially all the F1/karting
  "driving style" trade writing): given a lap, is it fast or slow, and what style correlates
  with fast? This tells you what *good* drivers do differently from *bad* ones on the same
  car — useful for a driver-quality signal, but it is not the same claim as "driver A is
  reliably distinguishable from driver B independent of pace," and none of the sim-racing
  sources tested identity-recovery directly.

If the goal is a driver-fingerprint feature independent of car/pace, the road-car
fingerprinting literature (§1, top five rows) is the closer analog; if the goal is a
style-quality signal correlated with lap time, the ACC sim-racing study is closer.

## 3. Motorsport-engineering (non-academic) corroboration

Trade/coaching writing on F1 and sim-racing telemetry consistently names the same handful of
observables as "driver fingerprints" without formal discriminability testing: later brake
application point, trail-braking slope/shape into the apex, throttle-reapplication timing and
smoothness out of the corner (feathered vs abrupt), and racing-line/apex choice (early vs late
apex trading entry speed for exit speed). [Podium Prophets, "Reading F1 Telemetry"](https://podiumprophets.com/blog/reading-f1-telemetry-beginners-guide) ·
[Coach Dave Academy, cornering telemetry guide](https://coachdaveacademy.com/tutorials/a-delta-guide-understanding-telemetry-data-in-cornering-types/) ·
[Driver61, racing line](https://driver61.com/uni/racing-line/). These are consistent with,
but not independent confirmation of, the academic findings above — no accuracy numbers, no
held-out validation, treat as directionally corroborating rather than evidentiary.

## 4. Scoped nulls / what this excursion did NOT establish

- **No confirmed racing-specific ranked feature list.** DIMRA (§1, last row) is the one paper
  that asks exactly our question on exactly our kind of data (professional race drivers) and
  I could not read it. This is a gap, not a negative result — worth a second attempt with
  institutional journal access or OCR tooling on the dissertation PDF.
- **Driver-count collapse is real and not fully characterized for our N.** Every accuracy
  number above degrades as driver-pool size grows (99.99%→76.36% going 2→10 drivers in one
  study; <40% accuracy reported for naturalistic studies with 9+ drivers in another). None of
  the papers found tested pools near F1 grid size (20). Do not extrapolate small-pool accuracy
  numbers to a 20-driver field.
- **Route/context confound is real.** Per-turn accuracy in the single-turn study ranged
  33–93.5% depending on which turn — meaning a chunk of "driver identification" signal in
  these studies is really "this corner/route is distinctive," not portable driver identity.
  For a fixed-circuit-per-race setting like ours this is less of a problem than for the
  naturalistic multi-route studies it was measured on, but it means corner-selection (not just
  feature selection) will matter for signal strength.
- **Sub-20 Hz ceiling confirmed for one specific thing:** ABS-cycle / individual-wheel-slip
  braking-modulation research (the fine-grained mechanism behind "how" a driver trail-brakes,
  as opposed to the coarse impulse/duration/slope features that are computable at our rate)
  runs at 500–4000 Hz in the literature — two to three orders of magnitude above our 10–20 Hz
  speed/throttle/brake/gear channels. [ABS wheel-slip test-rig sampling rates, search
  synthesis — no single citable primary source found, treat as directional] Coarse
  brake-pressure-integral/max/duration/slope features remain computable; per-wheel modulation
  detail does not.
- **No sim-racing or karting study found that directly tests driver-identity recovery** (as
  opposed to style-vs-pace clustering) — the closest, best-instrumented modern telemetry
  dataset (ACC/Brands Hatch, 174 drivers) was never run through a classifier asking "whose lap
  is this," only "how fast is this lap and why."
- **Steering-entropy** (Nakayama/Boer method, workload literature) is a well-established
  metric for detecting *changes* in a driver's steering behavior (workload, fatigue) but I
  found no study applying it to *between-driver* discrimination in a racing context —
  flagged as a plausible unexplored feature, not a confirmed one. [Steering entropy revisited,
  ResearchGate](https://www.researchgate.net/publication/228969825_Steering_entropy_revisited)
