# Issue #688 — consolidated problem statement

**Work id:** `issue-688` · **Engagement:** planning only (spine runs `init → context → understand → plan`, then stops)
**Governing scope:** the owner's **#724 routing comment on #688** — *W2 chain **STEP 6**, continuous wetness*
**Base to plan against:** **`main` = `3cf79f78`** (this worktree's HEAD `3541d292` is 9 commits behind and does **not** contain the #680 rain fix)

---

## 1. What the issue asked for, and what is actually true

The issue body says: the grip fit uses an *"any wet sample"* **exclusion** (`rain_flag_from_raw`,
`src/physics/layer2/grip_baseline.py`) that **dropped 20 of 36 candidate weekends** in the #678
G-pooling spike, and asks for a **fraction-of-wet-samples threshold** to recover dry coverage.

Three corrections, all source-verified, none of which change the owner's scope — but all of which
change *where the work lands*:

| # | Issue body says | Actually true | Evidence |
|---|---|---|---|
| C1 | rain **excludes / drops** sessions | Nothing is dropped. Rain multiplies `session_offset_sigma` by `RAIN_SIGMA_INFLATION = 4.0`. `fit_grip_baseline_from_laps`'s own docstring: *"never drops a session"*. Wet laps are already absent from the fit input (`_read_clean_session_laps` restricts to `SOFT/MEDIUM/HARD`). | `grip_baseline.py` (main) rain branches at the ok path and the thin path; the clean-lap SQL |
| C2 | the rule is `rain_flag_from_raw` | **LEGACY** as of **#680** (`d4cd4b79`, merged `23c3e1f9`, on `main`, **not** in this checkout). The live path is `rain_read_from_surface_features` → `session_surface_features.session_rain_flag`. | `git merge-base --is-ancestor d4cd4b79 HEAD` ⇒ not an ancestor; main's `grip_baseline.py` `"LEGACY -- see module note above"` |
| C3 | the source swap presumably helped | The **defect survived the swap, it only moved**. `_session_rain_flag` is *still* all-or-nothing: `1` if `sessions.rainfall > 0` **or** the summed weather-sample rainfall `> 0` **or** **any** lap ran on WET/INTERMEDIATE. #680's own docstring hands the loosening to #688 by name. | `src/data/weather_features.py::_session_rain_flag`; `rain_read_from_surface_features` docstring |

So the real defect is **a falsely-wide σ on sessions whose timed running was in fact dry** — not a
dropped session. The `~55%` figure is a **weekend-grain** artefact of the spike's own candidate
selection, and **no committed consumer performs that drop** (`session_rain_flag` has no consumer
outside the data region and `grip_baseline`; grip consumers reach it only through `get_grip_at`,
which never sees `rain_flag`).

## 2. Two measurements that decide the mechanism

Run read-only against `data/f1_data_2022.db` / `data/f1_data_2023.db`
(`.agent-work/issue-688/probe_coverage.py`, `probe_weekend_grain.py`):

**M1 — the continuous signal is missing exactly where it is needed.** `wet_lap_fraction` is
populated for **race sessions only** (#575's populator iterates `session_type='R'`):

| year | FP1 | FP2 | FP3 | Q | S | SQ | R |
|---|---|---|---|---|---|---|---|
| 2022 | 0/22 | 0/19 | 0/19 | **0/22** | 0/3 | 0/3 | 22/22 |
| 2023 | 0/22 | 0/16 | 0/16 | **0/22** | 0/6 | 0/6 | 22/22 |

Quali — the session type #678 named as the coverage crux — has **zero** coverage. A design that
just reads `wet_lap_fraction` into the fit is a **no-op where it matters**. A non-R fallback is
mandatory, not a nicety.

**M2 — granularity is the lever; the threshold is a rounding error.** Session retention over
2022+2023 (220 sessions, 44 weekends):

| rule | sessions retained |
|---|---|
| any-session-wet **weekend** rule (what the spike did) | **59 %** (65/110 per season) |
| per-**session** binary flag | **84 %** (92/110) — **+25 pts** |
| per-session **graded**, `<5 %` wet laps | **85–86 %** — **+1–2 pts** |

And at the session grain the flag is mostly *honest*: of ~35 rain-flagged sessions across the two
seasons, only ~5 have under 20 % wet laps. **The issue's own proposed acceptance (a wet-fraction
threshold) is real but small.** The recoverable coverage is in refusing to let one genuinely-wet
session condemn its four dry siblings — which is exactly what a graded, session-grain signal makes
expressible, and exactly what the owner's *"wire it in place of the current all-or-nothing
exclusion"* authorizes.

## 3. Precedent to reuse, not reinvent

`src/physics/layer2/damage_batch.py::is_wet_race` — **same package** — already reads
`wet_lap_fraction`, thresholds it, and falls back to a **physics-local compound proxy** (this
session's fraction of laps on INTERMEDIATE/WET) *precisely because* "the population script is
R-only, so it is NULL for every S/Q/SQ session today". It even names the case it rescues
(Belgium/Austria S 2023, 403/480 laps on inters). Second precedent for the threshold idiom:
`burn_rate_calibration.WET_EXCLUDE_THRESHOLD = 0.05`, a named constant with written rationale over
the same stored column.

**#688's job is to generalize `is_wet_race` from a bool to a fraction and give it one home**, not to
author a third wetness reader.

## 4. Protected intent (what must not break)

- **P1 — never falsely confident.** `grip_baseline`'s standing rule: a thin or rain session must
  never produce a small-σ estimate. The graded ramp may only narrow σ where the evidence says the
  running was dry.
- **P2 — the FROZEN "rain must widen" requirement** (#663 Mission): rain must have a *real, tested*
  widening effect, never an inert stored flag. Preserved by keeping the existing **×4.0 exactly at
  full wetness**; only the marginal end relaxes.
- **P3 — no session is ever dropped.** Every session still yields a record (`ok` /
  `thin_fallback` / `error`).
- **P4 — no hidden fallback.** A session with neither `wet_lap_fraction` nor laps must be
  *conservatively* treated (full ×4.0 if flagged), never silently graded to dry — the same posture
  `MissingSurfaceFeaturesRow` already takes.
- **P5 — DB-only.** No FastF1/Jolpica; physics must not import evo
  (`constraint:physics_region_no_evo_import`).

## 5. Scope, as the counterpart set it

**In:** wire R2's continuous wetness into the grip fit's own σ treatment; persist the graded value;
produce the W2 band-distribution acceptance artefact with the retained-session fraction beside it;
score **H5** (do condition regressors absorb inter-session offset) via #663's held-out harness.

**Out:** (a) *"threshold loosening beyond what R2's continuous wetness enables"* — an explicit
spec out-of-scope line; (b) **consumer gating** — the σ consumer contract is the stream's terminal
item, **#712**, and is the owner's call on measured evidence; (c) **track-temp / overnight-gap /
circuit-conditional** regressors — those are **#686**, the other half of step 6; (d) the
**surface-features backfill** for 2018–2021 / 2024–2026 — that is **#728**.

## 6. Sequencing

#688 is **step 6 of a seven-step ordered chain** and lands **after** #679 (flying-lap gate),
#678 (sign gate → V1 reparameterization **with the `GripEstimateRecord` re-key** → |D| prior) and
#687 (physical-σ gate). Consequences carried into the plan: the work must be **additive to a
re-keyed record and must not itself re-key**, and its acceptance is a **delta against the step-5
band distribution**, not against today's.

**Latent interaction, pre-declared by the owner:** the R2 → R3 rain-flag × σ-inflation interaction
is *"named and latent until the re-fit. Expect it; it is not a regression."*

## 7. Known limits of this understanding

- All measurement is on **2022/2023 only** — the only seasons with surface-features coverage
  (2018 0/105, 2021 22/110, 2024 24/120). Outside them the live fit *hard-fails*
  (`MissingSurfaceFeaturesRow`), which is #728's problem, not #688's.
- The compound proxy measures *"how much of this session was run on wet tyres"*, which is the right
  question for a contaminated dry-lap sample, but it is **not** a rain-intensity measure and will
  read `0` for a damp-but-slick-shod session.
- Stage D is a recorded **honest measured-NULL** (g4 +155.5 % RMS, g5 31.9 % separability). #688
  improves the *honesty of the band*; it does not, on its own, discharge that null.
