# x1 — Circuit/corner fingerprinting machinery inventory

**Question:** what corner-classification / regime-fraction / circuit-profile / C3
circuit-conditionality machinery exists today, what shape does it produce, what's the
coverage, and is it consumable for conditioning a per-driver utilization prior on "what
kinds of corners this circuit has"?

**Headline:** there are **three structurally separate lineages**, none joined to each
other or to the live predictor. The one that actually answers "corner-type composition of
circuit X" — `src/physics/layer2/regime_rollup.py` (issue #625, stabilized by #638) — is
**built, tested, merged to `main`, and validated** (its own falsifiable stability gate now
passes 5/5), but has **zero downstream importers anywhere in `src/`** — it is officially
tagged `MEASURED-not-wired` in `docs/architecture/packets/physics.md`. Nothing in
`src/physics/feature_view/` or `src/physics/weekend_state/` (the newest Phase-5/6 work,
commits `2e4fd5ef`/`299313cf`) references it either. It is real, validated raw material,
not yet a consumable feature.

---

## 1. Inventory (three lineages)

### Lineage A — the live regime-demand rollup (#625/#638, THE answer to this question)
| Module | Produces |
|---|---|
| `src/physics/layer2/corner_descriptors.py` (`bin_row_to_descriptor`, `descriptors_from_frame`) | Converts `grip_bin_obs` rows (`mu_lat_p90`, `v_mean`) into physically-interpretable `(radius_m, lateral_g)` per corner-phase sample, via steady-state `R = v²/a_lat`. |
| `src/physics/layer2/property_mixture.py` (`fit_property_mixture`, `posterior_membership`, `MixtureFit`) | BIC-selected, support-floored Gaussian mixture over `(log10(radius_m), lateral_g)` — soft/fractional corner-severity classes (k=4: tight/medium/fast/very-fast), **not** a hard per-corner tag. Pre-registered constants `MIN_COMPONENT_WEIGHT_FRAC=0.05`, `MIN_COMPONENT_SUPPORT_COUNT=150`, `k_range=(2,4)`. |
| `src/physics/layer2/mixture_stability.py` | The mandatory falsifiability gate ("F12"): held-out-circuit stability check (Hungarian-matched component means across independent circuit-name splits). **Real-data verdict: PASS 5/5** (two independent seed batches) after the #638 rework — see §3. |
| `src/physics/layer2/regime_rollup.py` (`circuit_distance_share`, `corner_bin_share`, `load_circuit_frame`) | **The rollup itself**: one circuit's `grip_bin_obs` rows → `{corner_distance_share, straight_distance_share, corner_class_{i}_distance_share for i in range(k), n_laps, n_rows}`. Explicitly a **distance**-share (bin-occupancy over 32 uniform arc-length bins), not a time-share — the module docstring states it as a systematic *lower bound* on true corner time-share (cars are slower in corners, so time-share > distance-share) and a dedicated test AST-greps the source to forbid the literal string `time_share` anywhere in code. |
| `src/physics/layer2/arcs.py` (`identify_straight_arcs`, `StraightArc`) | Generalized `_contiguous_runs` (now takes a `regimes: set[str]` param) groups contiguous non-corner samples into `(length_m, duration_s, top_speed_ms)` — straights as first-class segments. Built, tested, **not wired into the rollup** (rollup uses bin-occupancy, not this grouper — a named, accepted design gap, see MISSION_FRAME "Decision pressure"). |
| `src/physics/layer2/observability_router.py` (`ROUTER_ENTRIES`) | Maps the 4 hard regime tags (`corner`, `straight_throttle`, `straight_brake`, `straight_coast`) to which `layer2/*_view.py` file:line evidences each — a citation index, not a demand profile. |
| `scripts/build_regime_rollup.py` | CLI driver: fits Gate 2's mixture once (pooled across all circuits, shared class vocabulary), calls `circuit_distance_share` per circuit, writes the CSV+meta artifact. |
| `scripts/f12_held_out_stability.py` | CLI driver for the stability gate against the real DB. |

**Output artifact (promoted, current):** `docs/physics/625-regime-time-share.csv` +
`docs/physics/625-regime-time-share.meta.json` — header states
`F12 HELD-OUT-CIRCUIT STABILITY VERDICT: PASS (n_pass=5/5)`, k=4, generated
2026-07-18T12:28:34Z. Columns: `gp_name, corner_distance_share, straight_distance_share,
corner_class_0..3_distance_share, n_laps, n_rows`. (An earlier FAIL-verdict copy also sits
in `.agent-work/archive/2026-06-28.../` and `2026-07-18-625-.../artifacts/` — those are
history, superseded by the #638 rework; don't read the archived one as current.)

**Sanity check that passed:** Monza (`gp_name="Italy"`) `corner_distance_share=0.5186` <
Monaco `0.8314` — correct low-downforce-vs-street-circuit ordering, independently
reproduced twice.

Source docs: `docs/physics/625-phase1-segmentation-substrate.md`,
`docs/physics/638-f12-stability-rework.md`, `docs/architecture/packets/physics.md` lines
~1310–1472 (the authoritative current-state section, reconciled after #638),
`.agent-work/epic-601/wave2-625-verdict.md`, `.agent-work/epic-601/wave3-638-verdict.md`.

### Lineage B — the C3 regime-capability vector (#512, power/braking/traction/aero *capability*, not demand)
| Module | Produces |
|---|---|
| `src/physics/layer2/regime_readiness.py` (`compute_readiness`, `ReadinessThresholds`) | Per-(car, circuit, session) readiness metrics for the 5-view estimate store (Braking/Lateral/Traction/PowerDrag/Coast): `frac_team` (car-vs-car separability) vs `frac_circuit` (circuit-dominance), static-latent `separation_ratio` (car-spread / own σ), LOO covariance-honesty z-scores. Pure-over-DataFrame, no I/O. |
| `scripts/regime_capability_dashboard.py` | Renders coverage / `frac_team` / `frac_circuit` tables — **not** a demand cross with circuit geometry. |
| `docs/architecture/decisions/regime-readiness-rubric.md` | The rubric doc: 2σ is a reference line, not a pass/fail gate. |

**C3 finding (2023-Q pool, 216/220 sessions, 10 constructors × 22 rounds):** capability is
**circuit-conditional, not a clean car axis** — `frac_team` 0–4% vs `frac_circuit`
0.44–0.65. Best clean axis is `straight_line/max_power_w` at only ~1.16σ separation; most
other axes are aero/setup-conflated (0.5–0.9σ). Verdict: **CONTEXTUAL**, carried forward as
a covariance-bearing relative vector, not a hard gate. Full detail:
`.agent-work/archive/2026-06-28-512/VERDICT.md`.

This is the "regime-capability" side the brief asked about — it answers "how separable is
a car's capability by regime," **conditioned on** circuit but with **no explicit per-corner
demand vector inside it**. It has never been joined to Lineage A.

### Lineage C — hand-tagged circuit ratings (subjective, pre-existing, low-trust)
`src/evo_predictor/circuits.yaml` (2076 lines, ~96 circuit-year blocks) — Pirelli
TrackCharacteristics infographic ratings, 8 traits per circuit-year on a 1–5 scale:
`traction, braking, lateral, tyre_stress, track_evolution, asphalt_grip, asphalt_abrasion,
downforce`, plus `altitude_m`. **Exact-year match required** (no silent fallback; missing
year → neutral 3.0 profile + warning). This is the live predictor's *only* current
circuit-character signal and it is explicitly flagged low-trust: 2025/2026 rows carry
inline "carried from 2025" comments (e.g. lines 349/442/540), and the #625 Mission Frame
explicitly ruled it out as a validation proxy for the same reason ("would validate the
substrate against a hand-tag the mission itself frames as low-trust").

### Adjacent / superseded, for completeness
- `src/physics/wear/fingerprint.py` (`fingerprint_year`, `corner_fingerprint`, `label`) →
  `data/corner_fingerprints_{2019..2026}.csv` — per-corner **tyre-wear-sensor** diagnostics
  (`shed_pct`/`gain_pct`/`headroom_pct`, a rule-based `label` like `traction`/`entry`/
  `flat-out`). Looks like a regime tag, **is not one** — it's "where does the tyre-refund
  jump statistically show up," built for a different pipeline
  (`src/physics/wear/`) than the layer2 regime work. Coverage: 2019 (21 gps) through 2026
  (6 gps, season in progress). Prior excursion `x6-circuit-demand-RESULT.md` (below)
  concluded these CSVs are the wrong foundation for demand-profiling; the #625 work took
  that finding and built on `grip_bin_obs` instead, as Pre-ruling #2 explicitly records.
- `src/physics/layer2/grip_bin_obs.py` (`lap_bin_observations`, `N_BINS=32`,
  `CORNER_GATE_MS2=3.0`) — the **shared data source** for both `corner_fingerprints` (no —
  actually fingerprint.py reads `entry_sweep_*` CSVs, a different upstream) and Lineage A.
  Position-binned (32 bins/lap, per-lap-normalized — bin index is **not** a stable
  cross-session corner identity), combined-slip `mu_comb`/`mu_lat` p90 per (lap, bin).
  Backing table: `data/damage_integrals.db::grip_bin_obs`, 612,615 rows.
- `src/physics/utilization/regime_utilization.py` (`regime_utilization`,
  `estimate_driver_utilization`) — **this is very close to what the brief's "downstream
  consumer" wants**, but it is a **per-driver-lap** utilization measure (4 hard tiling
  regimes: braking/slow_corner/fast_corner/straight, via curvature+`a_lat` thresholds on
  ONE realized lap vs a physics-simulated ideal-lap ceiling), computed live per lap, **not**
  a stored per-circuit demand profile. It already has the exact regime taxonomy
  (`FAST_CORNER_ALAT_THRESHOLD=25.0 m/s²`, `CURVATURE_THRESHOLD=1e-4`) a demand-prior
  consumer would want to cross against Lineage A's corner-severity classes, but nothing
  connects them today.
- `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x6-circuit-demand-RESULT.md`
  — the **direct predecessor** to this question, dated one day before #625 was built. Its
  verdict was "not sufficient today" with 8 named, sized gaps (G1–G8). **#625/#638 close
  G1 (time-weighting, partially — as distance-share, not literal time), G3 (lateral-g/radius
  axis, via `grip_bin_obs`), and G8 (the actual per-circuit rollup)** — those three gaps are
  no longer open. G2 (straight length/duration/top-speed as first-class demand rows — `arcs.py`
  has the grouper but it's not wired into the rollup), G4 (cross-year corner-identity mapping
  — `corner_matches.csv`, still only 9/~24 gps × 3 years), G5 (the wear-fingerprint `label`
  reuse trap), G6 (exclude `coast_frac`), G7 (2026 partial coverage) remain as stated.

## 2. Coverage

| Artifact | Circuits | Seasons |
|---|---|---|
| Lineage A rollup (`625-regime-time-share.csv`) | **22** (source table's full circuit set) | Pooled across `grip_bin_obs`'s full range, **2019–2026** (612,615 rows total; 22 distinct `gp_name` values: Abu Dhabi, Australia, Austria, Azerbaijan, Bahrain, Brazil, China, Emilia Romagna, Great Britain, Hungary, Italy, Japan, Las Vegas, Mexico, Miami, Monaco, Netherlands, Qatar, Saudi Arabia, Singapore, Spain, United States). Notably **absent**: Canada, Belgium, Madrid — not in `grip_bin_obs` as of this run. One shared mixture fit pooled across all years/circuits (not per-year). |
| Lineage B (C3 readiness) | 22 rounds (2023 season) | **2023-Q only** — a single-season pilot pool, not multi-year. |
| Lineage C (`circuits.yaml`) | ~24 circuits × up to 9 years each (2018–2026) | Widest nominal coverage but **quality degrades toward present**: 2025/2026 rows are largely carried-forward, not freshly verified. |
| Wear fingerprints (`corner_fingerprints_*.csv`) | 17–24 gps/year | 2019–2026 (2026 partial, 6 gps) |

## 3. Consumability verdict: **PARTIALLY**

**Can a downstream consumer ask "give me the corner-type composition of circuit X" today?**
Yes, mechanically — `docs/physics/625-regime-time-share.csv` has exactly that row per
circuit, validated, in a stable location. But three caveats sit between that CSV and a
usable per-driver utilization prior:

1. **Not wired anywhere.** Confirmed by grep: no file under `src/` imports
   `regime_rollup`, `circuit_distance_share`, `property_mixture`, or `MixtureFit` outside
   the module's own tests and itself. This includes the newest Phase-5/6 feature-view work
   (`src/physics/feature_view/build_feature_view.py`, `src/physics/weekend_state/*.py`,
   commits `2e4fd5ef` #629 and `299313cf` #630) — neither references it. The architecture
   packet (`docs/architecture/packets/physics.md`) explicitly tags the whole #625 subsection
   **MEASURED-not-wired**, "no `src/` importer outside their own tests yet, consistent with
   this being Phase-1 substrate for Phase 2/4 to consume later." Phase 2 (four-layer
   weekend-state model) and Phase 4 (FP extension) were the *named intended consumers* in the
   Mission Frame — neither has happened yet as of this excursion.
2. **Distance-share, not time-share, by explicit design.** The rollup's own docstring is
   emphatic that this is a **lower bound** on true corner time-share (corners cost more real
   time per unit distance than straights, since `dt = ds/v` and cars are slower there). If a
   utilization prior needs "what fraction of a LAP's time is spent in each corner-severity
   class," this artifact systematically understates the corner-heavy end — usable as an
   ordinal/relative signal, not a calibrated time-weight, without further work (x6's G1 was
   only partially closed).
3. **`k=4` classes are corner-severity buckets (radius/lateral-g), not aero-vs-mechanical
   axes directly.** The classes recovered (tight/medium/fast/very-fast, roughly 50m/2.7g →
   500m/1.2g) are a genuine physically-meaningful ladder and passed a real stability gate —
   good raw material — but crossing them against Lineage B's capability vector
   (power/braking/traction/aero) to build a driver-utilization-style prior is an unbuilt
   join, same as x6 flagged for the join in general. No code anywhere computes "expected
   utilization drag from this circuit's class-0-vs-class-3 mix."

What's missing for full consumability: (a) a consumer in `feature_view`/`weekend_state` or
`evo_predictor` that actually reads the CSV/rebuilds the rollup live and joins it per-race;
(b) a documented mapping from the k=4 severity classes to the capability-vector axes
(braking/slow-corner-grip/fast-corner-grip/straight-line-power) that `regime_utilization.py`
already uses — the class *semantics* (radius+lateral-g) and the utilization taxonomy
(curvature+a_lat thresholds) are close cousins but were built independently and never
cross-validated against each other; (c) the time-share correction if literal time-weighting
matters more than an ordinal distance proxy for the prior's purpose.

## 4. Scoped nulls — explicitly NOT searched/inspected

- Did not read `src/physics/feature_view/build_car_basis.py`, `build_lap_evidence.py`,
  `build_weekend_state.py`, `read.py`, `records.py`, `store.py` line-by-line (only grepped
  the whole `feature_view/` and `weekend_state/` directories for the four regime-rollup
  symbol names — confirmed zero hits, but did not otherwise audit those files' actual
  content/logic).
- Did not read `.agent-work/archive/2026-07-18-638-f12-stability-rework/` gate-by-gate
  handoffs (implementer/reviewer JSON, DIAGNOSIS.md) beyond the summarizing verdict in
  `wave3-638-verdict.md` — the root-cause narrative there is second-hand from that verdict,
  not independently re-derived from the raw diagnosis artifacts.
- Did not open `data/damage_integrals.db::damage_lap_integrals` (the sibling table found
  alongside `grip_bin_obs`) — only queried `grip_bin_obs`'s row/circuit counts.
- Did not run any of the scripts (`build_regime_rollup.py`, `f12_held_out_stability.py`,
  `regime_capability_dashboard.py`) — all findings on data shape/coverage/verdicts are from
  reading source, docs, and pre-existing output artifacts, not fresh execution.
- Did not inspect `scripts/corner_match.py`, `scripts/corner_severity_gradient.py`,
  `scripts/driver_corner_reliability.py`, or `data/corner_matches.csv`/
  `data/driver_corner_reliability_2023.csv` directly — coverage numbers for those (9/~24
  gps, 2023-only) are carried forward from the prior x6 excursion's audit, not re-verified
  by this run.
- Did not check `data/entry_panel_estimates_*` (the tyre-decay panel fits) beyond what x6
  already establishes — confirmed orthogonal to demand-profiling, not re-audited.
- Did not search `.agent-work/archive/` beyond the specific hits surfaced by grepping
  `corner|regime|fingerprint|circuit_profile|curvature|C3|#512|#625|#638` — there may be
  other historical excursions/spikes not indexed by those exact terms.
- Did not check whether `src/evo_predictor/` (live prediction path) reads `circuits.yaml`'s
  `downforce`/trait fields anywhere downstream of loading (confirmed the file exists and its
  shape/provenance, not its consumers).
- Did not verify current `check_arch_map.py` / node-count freshness beyond what the #638
  verdict already states (42/20/12, unchanged) — treated as accurate from the verdict doc,
  not independently re-run.
