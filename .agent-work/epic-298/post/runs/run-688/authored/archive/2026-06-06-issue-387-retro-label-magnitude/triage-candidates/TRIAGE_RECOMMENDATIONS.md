# Issue #387 — Triage recommendations (for user approval before filing)

Three out-of-scope follow-ups surfaced during the spread-target build. All are deliberately
NOT in #387's label-only lane. None were blockers. Presented for the user to approve/decline
filing — the Admiral may already track some under the epic #378 fleet.

---

## 1. Consume race/race_start `s_e` + disagreement rate in the σ objective (Thrust B)

**Classification:** feature
**Structural anchor:** `src/latent_power/` (training/losses) + `src/evo_predictor/spread_target.py`
**Problem:** #387 produced the per-event race/race_start `s_e` spread target and the companion
pace-vs-finish `disagreement_rate`, but nothing consumes them yet. The σ head still
"bootstraps event uncertainty from its own residuals" (§1.3) instead of learning against the
event-conditioned target now available.
**Current truth:** `params/spread_target/<year>/<round>/{race,race_start}.json` exists (113
events each, CV 0.31/0.35). The σ training path does not read it.
**Desired/future concern:** a σ head (or σ-floor/tail rule) that consumes `s_e` as the
event spread target and `disagreement_rate` as conversion-noise input.
**Impact:** this is the payoff of #387 for race/race-start uncertainty — the artifact is inert
until a consumer lands.
**Suggested scope:** wire `s_e` (+ disagreement rate) into the σ objective / floor; validate
calibration vs the current bundle (Brier primary).
**Non-goals:** do NOT modify the spread-target derivation or the retro solve.
**Acceptance criteria:**
- [ ] σ path reads `params/spread_target/` race/race_start `s_e`
- [ ] disagreement rate consumed as a separate input, not folded into `s_e`
- [ ] calibration evidence vs stable baseline (Brier)
**Recommended priority:** medium — **Reason:** likely already the #386/#388/#389 done-bar; file
only if not already covered by the epic.
**Issue creation authority:** ask user (probable duplicate of fleet wave).

---

## 2. Consume quali `s_e` as the gap scale in the #391 mean head (Thrust A)

**Classification:** feature
**Structural anchor:** `src/evo_predictor/` (quali mean head, #391's lane)
**Problem:** the quali mean head needs a data-side gap scale (the retro labels can't carry it,
§1.3/§9.2). #387 produced the quali `s_e` (CV 0.80, 114 events) for exactly this, but the mean
head does not consume it yet.
**Current truth:** `params/spread_target/<year>/<round>/quali.json` exists. #391's mean head is
unbuilt / does not read it.
**Desired/future concern:** the quali mean head taking its gap scale from quali `s_e`.
**Impact:** unblocks the quali mean-resolution thrust's magnitude calibration.
**Suggested scope:** consume quali `s_e` in the #391 mean head; validate.
**Non-goals:** do NOT modify the spread-target derivation.
**Acceptance criteria:**
- [ ] #391 mean head reads quali `s_e`
- [ ] magnitude/calibration evidence
**Recommended priority:** medium — **Reason:** this IS #391's stated consumer; file only if #391
does not already capture it.
**Issue creation authority:** ask user (probable duplicate of #391).

---

## 3. 2018 race `s_e` leans on the field-median-spike proxy (data-quality note)

**Classification:** research hardening
**Structural anchor:** `src/evo_predictor/race_pace_gap.py`
**Problem:** 2018 race lap data has ~6% null `track_status` (2021-2025 have zero nulls), so for
the affected 2018 laps the actionable-lap filter falls back to the field-median-spike proxy
rather than exact track status. 2018 race/race_start `s_e` is therefore slightly less precise
than 2021+.
**Current truth:** the proxy is tested and approved (ruling D3.4); extending data collection is
explicitly out of scope (rate-limited collector). 2018 `s_e` records are still produced.
**Desired/future concern:** if 2018 is ever used for training/eval where this matters, either
backfill 2018 `track_status` (when collector budget allows) or exclude 2018 from spread-target
consumption.
**Impact:** low — only 2018, only ~6% of its laps, and the proxy is robust to obvious cautions.
**Suggested scope:** a note / optional 2018 track_status backfill when collector budget allows.
**Non-goals:** no in-scope collection now (rate-limited, out of scope per #387 ruling).
**Acceptance criteria:**
- [ ] decision recorded: backfill 2018 track_status OR exclude 2018 from consumers OR accept proxy
**Recommended priority:** low — **Reason:** marginal precision on one older season; proxy covers it.
**Issue creation authority:** ask user (may not warrant an issue).
