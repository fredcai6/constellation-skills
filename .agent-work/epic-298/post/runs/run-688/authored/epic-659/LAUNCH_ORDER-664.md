# LAUNCH ORDER — #664 (manifest E), epic #659 Wave 2

**Commander:** `constellation-commander-delegated` (full commander depth — understand/plan/execute/reconcile).
**Model tier:** OPUS (anti-circularity discipline + GATING attribution-robustness + season-capable build + prereq navigation).
**Worktree:** `C:/Programs/f1brainz-wt/epic659-664` · branch `epic659/664-reference-laps-utilization` · base main `0deea80f` (carries #660 frozen constants, #661 SegmentMap runtime, #662 per-weekend segment-map derivation, #663 grip G, #665 pooling).
**Interpreter PIN (CRITICAL):** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` (Python 3.14.3 / fastf1 3.8.1). NEVER bare `py` (that resolves to a different 3.12 with no fastf1). Verify `import fastf1` before any real run.

## Issue intent
#664 (manifest E): **Reference laps as a first-class product + class-grain utilization observables store (time and energy channels).** Reference laps via the #628 Path B production path (`build_car_ceiling` strictly-pre, anti-circular → `simulate_lap`); the scalar ideal lap time becomes a **first-class stored product** (currently computed and discarded). Circuit fingerprint = **per-class TIME-shares** from the FIELD-REFERENCE car's simulated lap (retires the #625 distance-share caveat). Build the class-grain **utilization observables store** (per-driver, per-segment-class), persisted with `map_version`, time-ledger native (transit-time deficits), energy tracked in both channels for §7's pre-registered comparison.

## THE FIVE EPIC OWNER RULINGS (binding on every child)
1. **No frame-kill.** Weak signal → structural work / honest-null, never abandonment. Sizing steers by allocation, not gating.
2. **Frozen constants (F12).** Every threshold pre-registered before the first real-data run (#660 `frozen_constants.py` is merged — consume it; do NOT mint new literals). Post-hoc changes need a new named constant set + re-run.
3. **Pre-quali constraint.** Build 1 is quali-side. Predictions are made BEFORE quali; the quali anchor is post-facto calibration only. NO race-outcome leakage into any observable.
4. **Lowest dimensionality that solves the problem.** Escalation layers dormant in schemas from day one.
5. **No baked-in normality.** Student-t / heavy-tailed wherever a distributional form is chosen.

## ⚠️ CRITICAL PRE-RULING — how #664 consumes Grip G (overrides the spec's "G-subtracted" wording)
The spec says "G-subtracted." **Read that as G-DIRECTED-UNCERTAINTY, NOT literal point subtraction.** Owner ruling (Fred, 2026-07-25), and now DATA-VINDICATED by a read-only pooling spike:
- G is consumed as a **directed uncertainty**: **μ=0, one-sided σ⁺, truncated/half Student-t on the "grip only improves" side**, evolution shape = **linear ramp to a plateau**, **circuit-agnostic, no environmental terms**.
- **Do NOT subtract a point G.** The spike measured that subtracting a point/pooled G *worsens* cross-session reconciliation (+56% pooled, +155% within-weekend #663) — the correction is directionally real but too small vs the ±20–60 s truth-side scatter to help. Subtracting it reproduces that damage.
- So #664 carries G as a **one-sided uncertainty band on the utilization observable**, not a shift of the point value. If the utilization observable's point value is unchanged by G and only its σ gains a one-sided component, that is CORRECT and expected. "G barely moves utilization" is the honest first-pass outcome, not a failure.
- Sharpening G (moving μ off zero via cross-weekend pooling + sigma-gated subtraction) is **#678, OUT OF SCOPE here.** Do not attempt it.
- If the current merged #663 G module exposes only a point estimate, wrap it to the (μ=0, σ⁺) contract at the consumer boundary; do not re-fit G.

## PREREQUISITE — TRACED CLEAR (do not re-litigate)
Admiral ran a read-only trace (2026-07-26): the reference-lap path (`car_prior.build_car_ceiling` → `physics_simulator.simulate_lap`) reads only **point-estimate capability values + per-scalar `_sigma` + per-VIEW covariance blobs** (`braking/traction/lateral_covariance`). It reads **ZERO** of `cross_view_covariance` / `{axis}_status` / `{axis}_shared_sigma` / `systematic_budget`. `simulate_lap` reads nothing from `physics_estimates.db`. The utilization estimator (`driver_utility.py`) computes `status` LOCALLY from a scratch observables DB, not the store's honesty columns. **Therefore #646 (physics_estimates.db re-batch) → #644 (headless deadlock) is NOT a hard prerequisite for #664.** The one nuance: on legacy pre-#627 rows the `_sigma` columns lack the folded systematic budget → a SOFT DEGRADE (narrower uncertainty widths), never NULL/crash, immaterial to the point-estimate lap. Document it as honest scope; do not block on it. Load-bearing cites: `src/physics/utilization/car_prior.py:363-419,531-533,603`; `physics_simulator.py:50`; `estimate_store.py:455`; `driver_utility.py:169,182`; `scripts/build_driver_utility_observables.py:278,283`.

## ⚠️ SCOPE BOUNDARY — build season-CAPABLE, run BOUNDED (overridable only if the spec truly demands otherwise, which it does not)
The spec's "the season-scale utilization run" describes the pipeline's TARGET, not #664's execution scope. The epic reserves the **full season-scale 2023 run for Wave 6 #670 (HITL, explicit go/no-go)**, gated behind the **Wave 5 #669 3-circuit pilot (tracer bullet)**. So #664 delivers: (1) the reference-lap first-class product, (2) the utilization store schema + the runnable, season-capable pipeline, (3) a **validation run on a bounded, representative slice** (enough to pass the GATING attribution-robustness check and to seed downstream #666) — **NOT** the full expensive season-scale run. Do not launch a full-season run: it belongs to #670, is rate-limit/thread-cap/launcher-hang exposed (#650/#648), and needs the Wave-6 human go/no-go. If a season-scale run feels necessary to pass GATING, STOP and float — it isn't (jackknife over derivation laps on the bounded slice is the gate).

## Scope specifics (from the confirmed spec §3)
- **Reference laps:** scalar ideal lap time promoted to a first-class stored product. Frontier discipline confirmed 4/5 views; coast feeds no utilization axis.
- **Circuit fingerprint = per-class TIME-shares** from the FIELD-REFERENCE car's simulated lap (retires #625 distance-share caveat). Each car's own reference still baselines its own utilization. Consume the **merged #662 per-weekend SegmentMap + `map_version`** and the #625/#638 **k=4** class vocabulary AS-IS (this epic is the consumer #642 waits on; do NOT re-open k).
- **Utilization observables:** per-driver, per-segment-class, **G-directed-uncertainty** (per the critical pre-ruling), persisted with `map_version`. Time-ledger native (transit-time deficits). Speed profiles kept diagnostic.
- **Units:** absolute deficit (m/s), NEVER a ratio (#628 anti-circularity-hardened convention).
- **Asymmetric channel treatment (ruled):** straights are car-rich / driver-thin (slipstream confound — the existing negative-control finding); braking zones are driver-rich. Reflect this in how much weight/interpretation each channel carries.
- **Energy channel:** tracked in BOTH channels for §7's pre-registered comparison, honest scope: **relative deployment vs the car's own rolling baseline + phase structure + derate flags — NEVER absolute SOC or kW** (2026 rampdown regulation → deployment signatures are curved ramps, not cliffs). If any MECHANICAL-energy quantity involving speed change enters on ELEVATION circuits, use **TOTAL mechanical energy (½v²+g·h), not KE-only** (owner ruling; altitude in the store as `pos_data` Z / `z_dm` decimetres) — but confirm whether #664's deployment-focused energy channel even needs this; state your finding. Do not import the #682 energy-vocabulary work (separate epic).
- **Store:** mirror the existing `driver_utility_observables` schema + class and `map_version` columns. Design-it-twice skipped (precedented shape).

## GATING acceptance (the substantive falsification)
- **deficits-sum-to-lap is a CONSTRUCTION check** (review T5) — it cannot catch misattribution between classes; label it as construction, not validation.
- **The substantive GATING check is ATTRIBUTION ROBUSTNESS:** per-class deficits stay stable under boundary jitter within the frozen quantile's uncertainty — **jackknife over derivation laps** on the bounded validation slice. Report the real stability numbers. A measured-null/weak-attribution result is a COMPLETE deliverable (no-frame-kill) — say so honestly.

## Out of scope
Race-side observables (Build 2); absolute ERS/SOC inference; ANY fingerprint fitting (that is #666, Wave 3); moving G's μ off zero (#678); the full season-scale run (#670).

## Debt to heed (context, not blockers unless you hit them)
#632 (DB bloat via `processed_telemetry` — write the utilization store to its OWN db, keep it off the f1_data DBs); #560 (thin-fit acceptance floor); #656 (tests must not dirty real DBs); #650/#648 (thread-cap + launcher-hang taxes on any long run — detach + state-note-first if a run is long); #646 soft-degrade (above). Newly filed grip-fit data-quality: #687 (fit-quality `ok`-gate hole), #688 (over-aggressive rain filter) — relevant only if you touch grip fits directly (you consume G, you don't re-fit it).

## Constraints & hygiene
- **Map fence:** do NOT touch `docs/architecture/*`. Record map impact as prose in your return + stage `notes-664.md` and `664-cartography/` for the epic's single CLOSEOUT cartographer reconcile.
- **Cartographer-wrong-checkout carry-forward:** IF you dispatch a cartographer subagent, run an independent `git status` in BOTH the worktree AND the main checkout afterward, and verify its edits landed AND are COMMITTED on the branch (a prior run's cartographer wrote to the wrong checkout, git-invisible).
- Do NOT commit any `.agent-work/` path on the mission branch. Stage the feedback trio (AGENT_FEEDBACK + lessons-delta.json + CONSTELLATION_FEEDBACK) under `.agent-work/staged-feedback/664-reference-laps/` with a `FENCE.md` citing this launch order; satisfy your feedback/archive gate against that staging dir.
- One writer per shared document per wave; working-notes file = `notes-664.md` (never `findings-*.md` — the Write tool refuses that basename).
- Isolation gate already passed (worktree provisioned off `0deea80f`, first-action echo confirmed by Admiral). Do NOT re-provision; do NOT run in any other worktree.

## Reporting
Report at PR + closeout with: the reference-lap product + the utilization store + the GATING attribution-robustness numbers (jackknife stability) on the bounded slice, and an honest statement of signal size (this is an instrument, not a gate — allocation-not-gating). NO merge without the Admiral (independent world-verify + gating re-run on the pinned 3.14 interpreter precede any squash). Float any `user-decision` up to the Admiral; do not reach for the human directly (owner is AFK).

## Pre-rulings recap (overridable ones marked)
- G = directed-uncertainty μ=0 σ⁺ half-t, linear-ramp-plateau, circuit-agnostic (NOT point-subtraction) — **binding**.
- #646/#644 not a prereq (traced clear); legacy `_sigma` soft-degrade documented — **binding**.
- Build season-capable, run bounded slice; full season run is #670 — **overridable only via float if the spec provably demands the full run (it does not)**.
- Consume #662 map + #638 k=4 vocabulary as-is; do not re-open k (#642 is downstream) — **binding**.
- Energy channel = relative deployment, never absolute SOC/kW; total-energy convention if mechanical energy enters on elevation circuits — **binding**.

**Expiry:** this order expires at #664 merge or on a Wave-2 contract-refresh from the Admiral.
