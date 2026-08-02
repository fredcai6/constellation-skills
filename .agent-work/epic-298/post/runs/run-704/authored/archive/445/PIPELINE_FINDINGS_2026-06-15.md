# Physics → idealized-pace pipeline — findings (2026-06-14/15)

Built the whole chain from raw telemetry to an idealized lap and driver
utilization. Methods work; car *ranking* is below the noise floor. NOT ready for
productization. Code: .agent-work/445/envelope/.

## The pipeline (all built, all run)
raw telemetry → trajectory smoother → **grip channel G(v)** → **longitudinal
channel (engine power + drag)** → **track ribbon κ(s)** → **idealized lap**
(quasi-static forward-backward) → **utilization** (actual ÷ ideal).

## What's SOLID (bank)
- **Methods/framework** end-to-end. Each channel independently validated.
- **Grip channel**: G(v)=min(A+B·v², G_sat); mechanical A≈1.8g (= tyre μ·g),
  saturating ~5g (driver/tyre sustained limit, derived not assumed). Compound
  lifts the frontier only ~0.036 g/C (~3%, small). Energy account closes to ~3%.
- **Longitudinal**: joint full-throttle fit → engine ~525 kW wheel (≈ICE+ERS−losses),
  drag CdA≈1.5 m² (Suzuka), DRS cuts drag ~30–37% (two-curve fit). Drag is the
  one channel that ranks cars SENSIBLY.
- **Friction unification**: one G(v) bounds cornering, braking (≈G — truer than the
  4.2Hz braking measurement which under-reads to ~3.5g), and traction. Power-to-
  ground = min(G·g·m·v, P_engine): grip-limited <~100 km/h, engine-limited above.
- **Track ribbon**: pooled mean line over ~100 laps → clean κ(s) (the lap sim needs
  this; single-lap curvature is too noisy).
- **Idealized lap + utilization**: quasi-static, friction-circle-limited exit. VER
  Suzuka ~92–94% utilization (slightly optimistic; top speed runs a touch high).
- **Qualitative car CHARACTER** (directional, multi-test consistent): Williams =
  low-grip / low-drag (low-downforce car); Mercedes = draggy; Red Bull = efficient.

## What's NOT solid (do not claim)
- **Per-car / constructor capability RANKING** and the **car-vs-driver split**.
  Tested from THREE independent angles, all below the noise floor:
  1. mid-corner grip → washed out at the noisy high-speed saturation (v²/R);
  2. rotation transient (yaw-rate cap, ψ̈_max≈4.2 rad/s² from VER) → does NOT bind
     at real capability on the smooth ribbon;
  3. exit/traction-ellipse → grip-limited window too narrow (~first 30 km/h of
     exit), power-dominated above and power is noisy.
- Competitive F1 cars are within ~few % across grip/power/drag; our measurement
  noise (esp. high-speed a_lat) exceeds the car-to-car differences.

## PARTIAL REVEAL: shared-grip frontier (2026-06-14, grip_iter.py)
Attacked grip noise with a hierarchical frontier fit: G(v)=min(A+Bv²,Gsat) on the
FULL cornering-node cloud (g_tot=√(a_lat²+a_long²), friction-circle magnitude),
quali only, iterative quantile-IRLS + EM membership peel, and — the key move —
mechanical grip A SHARED across cars (it's tyre×surface, not wing). Code:
grip_iter.py; raw grip_iter.out; grip_iter.png.
- Independent per-car A spread 0.5–0.9 g = impossible as real mechanical grip →
  per-car A was pure noise-absorption; sharing it is structurally correct.
- ONE car axis SURVIVES: per-car downforce B (on a global A=1.46 g baseline) puts
  **Mercedes lowest cornering-downforce at all 3 tracks (rank 4,4,3), Red Bull
  top-2 throughout** — under BOTH per-track-shared-A and global-A fits. First
  car-capability difference to hold anywhere; physically right (W14 fast-corner-
  weak, RB19 downforce benchmark). Suggestive, not proven.
- Still NOT resolved: the top order (RBR vs FER) and the middle (FER/WIL) shuffle
  when the A baseline moves. The reveal came mostly from the POOLING (dropping the
  per-car A DOF), not the peel — which is under-tuned: G@120≈2.75 g vs apex
  ~3.8 g, because the high-speed downforce regime is still data-starved (few fast-
  corner nodes at the limit → B weakly pinned). Williams quali too thin (Suzuka 63
  nodes, skipped). NEXT: feed the high-speed end — admit RACE nodes via the EM peel
  (keeps at-limit nodes, drops tyre-management laps); per-driver (not constructor)
  to test B is a car property; more weekends per wing-config.

### Iteration 2 (2026-06-14, grip_iter2.py): race nodes — confound dominated
Admitted FRESH-tyre race nodes (TyreLife<=6), down-weighted, EM-peeled, to feed
the high-speed downforce end. Outcome: the μ-loss won (user pre-warned).
- Race FED the high-speed end ~10x (Suzuka ≥120km/h nodes 40-73 → 487-776). Data
  starvation solved.
- But shared-A μ-common breaks under race: admitted nodes are mostly MEDIUM/HARD
  (quali is SOFT) → lower μ, and per-car compound splits differ → compound-μ leaks
  into per-car B. Fresh gate controlled WEAR (median life 5), not COMPOUND.
- Loss made visible: freeing A FLIPS Monza ranks (WIL #4↔#1, MERC #2↔#4 on G@140);
  freed-A spread 0.43-0.64g; Suzuka grows a Williams artifact (G@140≈4.0g vs ~2.6g,
  unphysical, thin quali 63 + race overshoots slope). Quali-only Merc-low DEGRADED
  (4,4,3 → 4,2,4; Hungary flipped Merc to #2).
- SURVIVES everything (quali/race, shared/freed A, all tracks): RBR high downforce,
  top-2 in 5/6 views — firmest single fact. Merc-low is a QUALI signal race muddies
  (W14 fast-corner deficit shows on equal soft/fresh tyres; race tyre behavior
  contaminates). VERDICT: quali-only is the cleaner grip basis; using race for grip
  needs per-car compound×wear μ modeled out (the conditions-matrix de-confound,
  bigger build), not node pooling.

### Iteration 3 (2026-06-14, grip_iter3.py): per-driver gate — data-volume-limited
Fit B per DRIVER (quali, global A=1.63g), decompose WITHIN-team (teammate gap) vs
BETWEEN-team (car gap) to test if B is a CAR property. Blunt average: within 0.36
> between 0.22 (ratio 0.61) → reads "driver/line". BUT that average is dominated
by Monza (few corners → per-driver B is noise: teammate gaps 0.58-0.75 and the
SLOWER teammate "wins" — VER 0.57<PER 1.26, ALB<SAR — signature of noise). By
track: Monza within>>between (junk); Hungary (data-richest) teammates AGREE
(0.04-0.23) AND RBR>MERC holds for BOTH pairs (VER 3.37 & PER 3.28 > HAM 2.95 &
RUS 3.24); Suzuka between>within (0.36>0.26). Drop thin Monza → ratio ~1.4 (leans
CAR). VERDICT: inconclusive, ENTIRELY data-volume-limited — where data is abundant
(Hungary) teammates converge + car signal appears; where thin (Monza) it's noise.
This is the case FOR #2 (conditions-matrix de-confound): the binding constraint is
measurements-per-car, and race conditions are the only path to enough volume.

### #2 FIRST CUT (2026-06-14, grip_deconf.py): variance↓ real, signal validity NOT
Covariate frontier: g = A + dCompound(soft/med/hard) + wear·age + B(car,track)·v²,
shared tyre terms pinned by pooled data (61,399 nodes), per-(track,driver) B, keyed
by driver to re-run the teammate decomposition. Quali=SOFT/age0, race=all valid
laps (full age range).
- METHOD WORKS (variance): tyre terms physical (compound MEDIUM −0.26g / HARD
  −0.24g; wear −0.0014 g/lap). Per-driver noise COLLAPSED: teammate gap 0.36→0.13,
  ratio 0.61→1.85. Monza teammate chaos (iter3 gaps 0.6-0.75) gone (now ~0.02-0.08).
  Volume + de-confound stabilizes the per-unit estimate → validates #2 DIRECTION.
- SIGNAL NOT VALID YET: car ordering inconsistent across tracks AND contradicts
  quali. Constructor mean B — Monza: all ~0.55-0.60 (no separation, low-aero ✓);
  Hungary: MERC 0.99 HIGHEST (contradicts quali Merc-LOW!), RBR 0.94, FER/WIL 0.81-
  0.83; Suzuka: RBR 0.75 top, but WIL 1.17 = SAR artifact (B=1.70, unphysical).
  Merc flipping to highest-downforce at Hungary ⇒ race-context confounds BEYOND
  compound/wear remain (dirty air, traffic lines, race situation); crude linear
  model misses them; SAR-Suzuka raw artifact persists. So variance↓ (win) but the
  estimate may be race-context not car capability. NEXT for #2: robustify (kill
  outliers / robust loss), add race-context controls (clean-air-lap gate, gap-to-
  car-ahead), per-compound wear, cross-validate, and reconcile race-vs-quali truth.

## Key gotchas (so we don't relitigate)
- **High-speed lateral grip = v²/R is irreducibly noisy** at 4.2 Hz; the saturation
  is the noise-dominated regime. Trust slow/medium corners only.
- **Apex grip ≠ braking ≠ traction** but ~round friction circle held well enough.
- **Forward-backward IS the global optimization** (brake-to-apex + curvature-limited
  exit). It's correct for a point-mass quasi-static car.
- **Rotation doesn't bind** → the 6% utilization gap is genuine utilization
  (perfect line + grip-every-corner + driver imperfection), not a missing constraint.

## RESOLVED: cross-circuit test (2026-06-14) — model can't discriminate ordering
Ran the constructor-ideal pipeline at Monza (low-DF), Hungary (high-DF), Suzuka
(balanced), re-fitting grip + power/drag PER TRACK (wings reconfigured) and
rebuilding the ribbon per track. Code: envelope/cross_circuit.py; raw:
envelope/cross_circuit.out; per-track ribbons ribbon_{monza,hungary}.npz.

Two clean negatives + one positive:
1. **Spread is track-INVARIANT.** Constructor spread = Monza 749 ms, Hungary
   715 ms, Suzuka 749 ms — ~1% of lap at ALL THREE. A constant *relative* spread
   is the signature of fixed fractional fit uncertainty, NOT track-character
   divergence. Suzuka's "near-equal ideals" were never special (the packed look
   came from the earlier per-car-Gsat run; common-Gsat spreads it the same ~1%).
   So the "balanced-track cancellation" reading is WRONG — it's the same noise
   everywhere.
2. **Ordering SCRAMBLES, not physically.** Delta-from-mean (ms): FER -189/-298/
   +215; MERC +430/-255/+339; RBR +77/+416/-145; WIL -319/+137/-409 (Monza/
   Hungary/Suzuka). RBR slowest ideal at Hungary, Williams fastest at Suzuka —
   both nonsensical. No constructor holds a consistent relative position. The
   low-drag-wins-at-Monza / grip-swing-at-Hungary prediction does NOT appear.
   This is the 4th independent confirmation that per-car capability RANKING is
   below the noise floor.
3. **Drag channel (CdA) DOES re-fit correctly per track** — CdA_closed ~1.1-1.2
   Monza, ~1.5 Suzuka, ~1.7-1.9 Hungary (teams add wing Monza→Suzuka→Hungary).
   Merc-draggy character partially survives at drag-sensitive Monza (Merc slowest
   +430). Drag is the lone channel that responds to config + weakly preserves
   character. The grip term A is the culprit elsewhere: swings unphysically across
   tracks (FER 1.23 Monza → 1.97 Suzuka; mechanical μ shouldn't move with wing),
   noise-dominated where slow-corner apex data is thin (Monza's few corners).

Also: utilization is NOT track-invariant (Monza ~88%, Hungary ~90%, Suzuka ~93%),
so "utilization" isn't yet a clean track-independent driver metric — the ideal is
relatively more generous on long straights (quasi-static top-speed section).

NET: pipeline captures track CONFIGURATION (CdA per track) and car CHARACTER
(drag), not capability RANKING. Confirms prior finding; not productization-ready.
