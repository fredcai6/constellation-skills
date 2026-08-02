# Mission Frame — issue #688 (grip-fit rain treatment → graded wetness)

Work id `issue-688` · base to plan against **`main` = `3cf79f78`** (this checkout's HEAD `3541d292` is
9 commits behind and lacks #680) · governing scope: the owner's **#724 routing comment on #688**,
*W2 chain **STEP 6** (continuous wetness)*.

## Intent

Replace the grip-baseline fit's **binary** wetness treatment with a **graded** one, so a session's
grip-offset σ reflects *how much of that session's running was actually wet* rather than *whether
any wet sample exists*. The frame is required here (not a trivial change): the work lands inside
`struct:physics.layer2`'s grip-G leaf, which the map records as a **disclosed measured-NULL** under
a `settled/inherited` store-schema decision, and it touches a record other components consume.

**Note the frame corrects the issue's own framing** (see `PROBLEM_STATEMENT.md` §1): there is **no
exclusion** in the producer — rain multiplies `session_offset_sigma` by `4.0`, and
`fit_grip_baseline_from_laps` "never drops a session". The `~55 %` weekend loss is a **weekend-grain
artefact of the #678 spike's own candidate selection**; no committed consumer performs it.

## Affected Capabilities

- **Grip-baseline session uncertainty** (pipeline **stage D**) — today: fit a field-pooled saturating
  curve per session and attach a Student-t σ, then multiply `session_offset_sigma` by a fixed `4.0`
  on any rain flag. After: the same fit, with the multiplier a **monotone function of measured
  wetness severity**, and the severity + its provenance persisted on the record.
- **`purpose:physics_estimation`** — this run serves it by making one estimate's uncertainty honest
  in both directions; it adds no new estimand.
- **NOT touched:** the curve form, the offset, the thin-session fallback, `get_grip_at`'s
  propagation algebra, and every downstream consumer's gating.

## Examples / Events

- **The case the change exists for** — 2023 Q at a circuit with a wet FP1 and a dry qualifying hour:
  flagged today (any wet sample), σ ×4.0, band effectively vacuous. Measured: **~5 of ~35**
  rain-flagged sessions across 2022+2023 have under 20 % wet laps. Small at the session grain — and
  that is the honest finding, not a disappointment.
- **The case the change must NOT break** — Belgium/Austria **S** 2023, 403/480 laps on
  intermediates (named in `damage_batch.is_wet_race`'s own docstring). Genuinely wet; must still
  receive the full ×4.0.
- **The case that makes a naive design a no-op** — any **Q** session, 2022 or 2023: measured
  **0/22** `wet_lap_fraction` coverage in both seasons (the column is populated R-only). Reading
  only `wet_lap_fraction` recovers nothing on the crux session type.
- **The case that must fail loudly** — a session with no `session_surface_features` row at all
  (2018–2021 / 2024–2026, `MissingSurfaceFeaturesRow`). Out of scope here; **#728**.
- No new architecturally-meaningful event is emitted or consumed: no boundary-crossing signal
  changes shape. The record gains fields; that is a store-contract change, handled below.

## Structural Anchors

- `struct:physics.layer2` — component, `src/physics/layer2/`. **Primary landing zone.** The grip-G
  module leaf (`grip_baseline.py` 705 lines at main / 999 limit, `grip_store.py`, `grip_batch.py`)
  and the reuse target `damage_batch.py::is_wet_race`.
- `struct:data` — container, `src/data/`. **Read-only dependency.** Owns
  `session_surface_features` (`session_rain_flag`, `wet_lap_fraction`) and its populators
  (`weather_features.py`). Physics reads; physics must not write or recompute here.
- `struct:sqlite_db` — the canonical `data/f1_data_<year>.db` artefact the whole read is mediated by.
- `struct:physics.utilization` — component, `src/physics/utilization/`. **Downstream, untouched.**
  `class_utilization_observable.py` is the real stage-D consumer via `get_grip_at`; it never sees
  `rain_flag`, so nothing here changes its behaviour beyond the σ it already consumes.
- `struct:physics.pilot` — component, `src/physics/pilot/`. Pure read-only consumer of the grip
  slot; a regression surface, not a change surface.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — nothing added here may import evo / latent_power /
  compound_prior. Every touched file already honours it; the new module must too.
- **Canonical-data constraint** (`ORCHESTRATOR_CONTEXT`, "Canonical Data Constraint") — SQLite is the
  only authoritative source. No FastF1/Jolpica; the wetness signal is *read* from the DB, never
  re-derived from a live source.
- **Missingness is explicit** (`ORCHESTRATOR_CONTEXT`, Planning Invariants) — an unknown wetness is
  `None`, never `0.0`. `0.0` means "measured dry"; `None` means "not populated". #680 already
  established this exact discipline for `wet_lap_fraction` and it must not be softened.
- **FROZEN (#663 Mission):** rain must have *a real, tested widening effect, never an inert stored
  flag*. Preserved by pinning the ramp to **exactly `RAIN_SIGMA_INFLATION = 4.0` at full wetness**;
  only the marginal end relaxes.
- **Protected intent (`grip_baseline` module docstring):** "a thin or rain session must NEVER
  silently produce a falsely-confident (small-sigma) estimate". This is the one-way ratchet on every
  constant chosen in this run.
- **No session is ever dropped** — every session still yields an `ok` / `thin_fallback` / `error`
  record.
- **Assumption carried, stated:** wet-tyre lap fraction is a usable stand-in for how contaminated a
  session's dry-lap sample is. It is *not* a rain-intensity measure and reads `0` for a
  damp-but-slick-shod session. Recorded as a known limit, not silently assumed away.
- **Simplification limits** — `py -m src.utils.simplification_limits` (999-line cap) on every touched
  path; `grip_baseline.py` is already at 705, which is itself an argument for a separate module.

## Decision Anchors & Decision Pressure

- `decision:grip_estimate_record_session_level_pk` — the grip record is keyed per `(year, gp_name,
  session_type)`, deliberately diverging from `EstimateStore`'s per-constructor key, because grip is
  a track/session-level quantity.
  `@grade: settled/inherited · leans g3-implement · a downstream consumer meeting a per-constructor
  expectation floats to the epic tier, never re-keys` — **this run adds fields to that record and
  must not touch its key.** (#678 step 3 re-keys the *coordinates*; #688 must be additive to
  whatever that lands.)

New decisions this run forces (surfaced as **candidates**, carrying working grades):

- **decision pressure — where the graded wetness read lives.** One home
  (`src/physics/layer2/session_wetness.py`) with two adapters (grip + `is_wet_race`), versus a
  second private copy inside `grip_baseline`. Recommended: one home — `is_wet_race` is already an
  implementation of exactly this read, so the seam has two implementers and is real, not
  hypothetical. `@grade: guess · leans g2-implement · settle: the deletion test — if `is_wet_race`
  cannot delegate without changing its bool semantics, the seam is wrong`
- **decision pressure — the ramp's shape and its two constants** (`WETNESS_DRY_FLOOR`,
  `WETNESS_WET_CEILING`). Recommended: linear between them, `1.0` below the floor, exactly `4.0` at
  and above the ceiling. `@grade: guess · leans g3-implement · settle: g1's measured
  wetness histogram + g4's band-distribution delta — the floor must not admit a session the
  compound proxy says ran materially wet`
- **decision pressure — what a graded record must say about its own provenance.** Recommended: a
  `wetness_source` discriminator (`surface_features` / `compound_proxy` / `unknown`) beside the
  severity, so #712's consumer can tell a *measured* dry from a *proxied* dry.
  `@grade: guess · leans g3-implement · settle: whether g4's report can partition the band
  distribution by source without it — if not, it is load-bearing`
- **decision pressure — the unknown-wetness policy.** Recommended: fail conservative — a flagged
  session with no severity keeps the full ×4.0. `@grade: settled/inherited · leans g2-implement,
  g3-implement · this is the module's Protected Intent, not a free choice`

## Claims / Evidence Surfaces

- **Producer honesty** — `tests/unit/physics/layer2/test_grip_baseline.py` already pins
  `rain.session_offset_sigma == dry.session_offset_sigma * RAIN_SIGMA_INFLATION` and rain×thin
  composition. Every gate re-runs it; the pinned equality must survive **at full wetness** and be
  deliberately, visibly re-expressed at the marginal end.
- **Store round-trip** — `tests/unit/physics/layer2/test_grip_store.py`; `GripStore` migration is
  additive-only and driven off the dataclass fields (`_migrate_missing_columns`), so new fields cost
  no migration code but *do* need a round-trip assertion.
- **Reuse guard** — `tests/unit/physics/layer2/test_damage_batch.py` already covers the S/Q NULL
  fallback case explicitly ("The population script is R-only: wet_lap_fraction is NULL for S/Q/SQ").
  Per lesson `consumed-frozen-module-run-guard-tests`, this pre-existing file is a *required*
  re-run, not an optional one, the moment `is_wet_race` is touched.
- **W2 stream acceptance (binding, T7/IF15/T19/T20)** — the **band-distribution report** (median,
  p90, vacuous count, plausible-|D| count) recomputed on the stamped substrate, the **retained-session
  fraction reported beside it**, and the **per-step delta** recorded. The harnesses must
  **hard-fail, not `pytest.skip`,** when the store is absent — `test_grip_heldout.py:432` currently
  does `pytest.skip("main-checkout DB absent")`, so this amendment is unmet on the base.
- **H5 (scoreable)** — condition regressors absorb a measurable share of inter-session offset;
  confirm/deny by **held-out log-score with and without**, per #663's harnesses.
- **Sizing evidence produced during this planning run** (read-only, reproducible):
  `.agent-work/issue-688/probe_coverage.py`, `.agent-work/issue-688/probe_weekend_grain.py`.

## Map Confidence / Staleness / Disputes

- **This worktree is stale — the single biggest planning hazard.** HEAD `3541d292` predates #680,
  #684, #721, #723. The issue names a symbol (`rain_flag_from_raw`) that is **legacy on main**.
  *Plan alteration:* every gate states `main` as its base and the plan's first act is a rebase
  check; no gate may be authored against symbols read in this checkout without a `git show main:`
  confirmation. Already applied throughout this frame.
- **`struct:physics.layer2` grip-G leaf is a recorded honest measured-NULL** (g4 +155.5 % RMS, g5
  31.9 % separability). The packet says revisiting the fit is future work. *Plan alteration:* #688
  improves the **honesty of the band** and must not be written or reported as discharging that null
  — g4's acceptance is a *delta*, and a null-that-stays-null is a pass here.
- **The map does not yet know about #679/#678/#687.** W2 steps 1–5 land ahead of this issue and
  #678 step 3 **re-keys `GripEstimateRecord` to in-data coordinates**. The map's grip section
  describes the pre-chain shape. *Plan alteration:* gates are authored **additive to** the re-keyed
  record, never as a re-key, and the plan carries an explicit rebase-and-reconcile gate condition
  rather than assuming today's field set.
- **The W2 band-distribution reporter is not in committed code** (grep: no
  band-distribution/vacuous-count artefact under `src/` or `scripts/`). It is a stream artefact step 1
  would introduce. *Plan alteration:* g4's imperative is conditional — reuse #679's reporter if it
  landed, otherwise ship the minimal version, and say which happened.
- **Surface-features coverage is 2022/2023 only** (2018 0/105, 2021 22/110, 2024 24/120; the live
  fit hard-fails outside). *Plan alteration:* every measurement in this run states its frame as
  2022–2023 and no claim generalizes past it; the backfill is **#728**, not this run.

## Out of Scope

- **Threshold loosening beyond what R2's continuous wetness enables** — explicit spec out-of-scope
  line; a modelling decision, not part of the chain.
- **Consumer gating / the σ consumer contract** — the stream's terminal item, **#712**, owner's call
  on measured evidence. No committed consumer gates on rain today, so there is nothing to edit.
- **Track-temp regressor, overnight-gap term, circuit-conditional evolution scale** — **#686**, the
  other half of step 6.
- **Surface-features backfill 2018–2021 / 2024–2026** — **#728**.
- **The curve form, the sign gate, the V1 reparameterization and the record re-key** — **#678**
  (steps 2/3/5); the flying-lap gate — **#679**; the physical-σ acceptance gate — **#687**.
- **Re-fitting or re-deriving the wetness signal in the physics region** — `src/data/` owns the
  column; physics reads it. The compound proxy is a *fallback for an unpopulated read*, precedented
  by `is_wet_race`, not a competing derivation.
- **`rain_count_from_raw` / `rain_flag_from_raw` removal** — legacy but still a correct blob decoder
  retained deliberately by #680 for audits. Deleting it is not this run's business.
