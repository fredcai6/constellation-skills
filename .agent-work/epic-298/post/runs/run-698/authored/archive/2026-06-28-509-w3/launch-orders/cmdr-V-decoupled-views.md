# Launch Order: `cmdr-V — #523 productize decoupled longitudinal estimator into Traction/PowerDrag/Coast`

Commanders start cold. Paste, don't point. **Run the FULL `constellation-commander` gated
spine** (understand → plan → implement → review → integrate). Multi-step commander, not a
one-shot implementer (explicit user preference). This issue's own bar is **characterize FIRST,
then wire-or-hold** — do not blind-cut.

## Mission
Make the decoupled longitudinal estimator the **single canonical longitudinal source**
across the throttle/coast capability views. #518 wired it into the braking frontier only;
the **Traction / PowerDrag / Coast** views still read the legacy `clean_longitudinal_from_raw`.
The decoupled estimator is a strictly better longitudinal measurement (deeper knee, honest
per-sample σ, terrain-aware). This completes the single-canonical-longitudinal-path
architecture — the runway for **C3 #512** (the regime vector = these throttle/coast views).

Two phases, in order:
1. **Characterize** (evidence-only, no wiring): re-fit Traction / PowerDrag / Coast on the
   decoupled `a_long` vs the incumbent `clean_longitudinal_from_raw`. Report how
   `(CdA, P_max [max_power_w], a_t/b_t [brake/traction decel], θ_R [spec drag])` shift, WITH
   covariance. Flag any view that regresses (worse de-conflation / wrong-sign / inflated cov).
2. **Productize**: wire the views that don't regress. Any regressing view is surfaced as a
   **fix-or-hold** decision (file an issue + track the compromise) — NOT blindly cut over.
   End state: single canonical longitudinal path; update `decision:decoupled_1d_longitudinal`
   to fully-wired.

## Prior-Wave Verdicts (pasted)

**#523 full text:**
> Parent #509. Deferred from #518 (user re-plan 2026-06-25): #518's remaining gates were
> redirected to the ideal-lap simulator fix, so the wider-views work was not done.
> **What:** Characterize, then productize, the decoupled longitudinal estimator into the
> throttle/coast capability views — Traction, PowerDrag, Coast — making the decoupled `a_long`
> the single canonical longitudinal source across all views and retiring
> `clean_longitudinal_from_raw` from `session_traction` / `session_coast`.
> **Importance MEDIUM:** quality + architecture cleanliness, **not** on the C1 critical path
> (the C1 blocker was the comparison method, #522).
> **Evidence:** `clean_longitudinal_from_raw` still imported by `session_traction.py` (~79/109)
> and `session_coast.py` (~49/75). Where the decoupled estimator has no tight anchor
> (throttle/coast), its `a_long` should track the raw read closely → blast radius expected
> small — but **characterize before wiring**.
> **Acceptance:** characterize (CdA, P_max, a_t, b_t, θ_R shifts + cov; flag regressions) →
> productize non-regressing views; regressing view = fix-or-hold (issue + tracked compromise),
> not blindly cut; single canonical path; `decision:decoupled_1d_longitudinal` → fully-wired.
> **Out of scope:** the C1 comparison-method rework (#522); braking wiring (done #518);
> repopulating the cross-session estimate store beyond what characterization needs.

**#518 context (the braking wiring this extends):** the decoupled 1-D longitudinal estimator
(`src/physics/layer2/decoupled_longitudinal.py` / `decoupled_braking_input.py`) works in TOTAL
system energy / vehicle-force coordinates (`dE_total/ds = F_vehicle`, gravity-free), recovers
the real braking knee without 2-D ringing, honest σ. It was wired as the canonical braking
input in #518; the throttle/coast views were left on the legacy path.

**#525 vocabulary (LANDED, PR #534):** the physics param names were renamed `<what>_<unit>`
(`p_max → max_power_w`, `theta_D → spec_drag_m2_kg`, `A0 → lateral_mech_grip_{g,ms2}`, etc.).
Use the CURRENT names — verify from source, don't assume pre-#525 names.

## Verified Seams (cite exact — confirmed from source at dispatch)
- `clean_longitudinal_from_raw` is DEFINED at `src/physics/layer2/braking_view.py:84` —
  signature returns `(v_at, a_long_raw, sig)`. **Do not remove the function** (the decoupled
  estimator and scoreboard still use it as the un-biased raw anchor) — retire only the
  throttle/coast *direct reads* of it.
- Incumbent throttle/coast reads to migrate:
  - `src/physics/layer2/session_traction.py:80` (import) + `:110` `v_at, al_at, sig = clean_longitudinal_from_raw(spd_d["t"], spd_d["V"], t_s)`
  - `src/physics/layer2/session_coast.py:49` (import) + `:75` `v_at, al_at, _ = clean_longitudinal_from_raw(t, v, t)`
- View modules: `traction_view.py`, `power_drag_view.py`, `coast_view.py` (+ their `session_*`
  and `*_report` siblings). **PowerDrag** is the throttle-on descent that deconfounds drag —
  include it in the characterization (it shares the longitudinal source).
- The decoupled estimator entry points live in `decoupled_braking_input.py` /
  `decoupled_calibration.py` / `decoupled_longitudinal.py` — verify the exact function +
  return type from source before calling (the #518 braking path in `session_braking.py:191`
  shows the wired usage pattern).

## Pre-Rulings
Ruled in advance, each overridable if evidence contradicts it — say so when overriding.
- **Characterize before wiring (diagnose-first).** Gate-1 is evidence-only: the per-view
  shift table + covariance, no production wiring. Decide wire-or-hold per view FROM that
  evidence at a checkpoint, then implement.
- **Wire-or-hold, never blind-cut.** A view whose fit regresses on the decoupled `a_long`
  (worse de-conflation, wrong-sign coefficient, inflated covariance) is HELD — file an issue,
  track the compromise, leave it on the incumbent path — do not cut it over.
- **Honest-null is a win.** "Decoupled does not improve view X / regresses view X" with the
  evidence is a complete deliverable. If ALL three regress, that is a valid honest-null verdict
  (the estimator stays braking-only) — report it, don't force the wiring.
- **Keep `clean_longitudinal_from_raw` defined** (braking/scoreboard depend on it); retire only
  the throttle/coast direct reads of it that you replace.

## Honest-Null Clause
A measured negative on "does the decoupled source improve/hold each throttle-coast view" is a
complete, successful deliverable. Report regressions with the same rigor as wins.

## Inherited Latitude
You MAY (delegated): in-fence wiring + refactors within `layer2/`, filing the fix-or-hold
follow-on issue(s), updating `decision:decoupled_1d_longitudinal`. You MUST float: any need to
edit OUTSIDE your fence BEFORE editing (esp. `calibration.py` / `session_fit.py` — that is
cmdr-R's Lane 1); any change to a measured number's *meaning* beyond the issue's intent
(units/convention — #525 family); any scope addition beyond #523. Asking up is sanctioned.

## File Ownership
**Sole writer this wave for:** `src/physics/layer2/**` (the throttle/coast view + session +
report modules and the decoupled-estimator modules) and any NEW test files under
`tests/unit/physics/layer2/`.
**Do NOT touch** `src/preprocessing/trajectory/calibration.py`, `src/physics/session_fit.py`,
or `stint_span` in `src/preprocessing/trajectory/loaders.py` — those are cmdr-R's Lane 1. If
your work needs them, STOP and float.
Findings file: `.agent-work/509-w3/crew-handoffs/cmdr-V-findings.md` (sole writer).

## Workspace
Worktree **already provisioned for you**: `C:\Programs\f1Brainz-509w3-views`
- Branch: `feat/509w3-decoupled-views`  ·  Base commit: `accf07a2` (fresh main, verified)
- Created with: `git worktree add -b feat/509w3-decoupled-views ../f1Brainz-509w3-views accf07a2`

First step, before any git operation: `verify_worktree_isolation.py` does **NOT exist** —
use the native gate: run `git -C "C:\Programs\f1Brainz-509w3-views" rev-parse --show-toplevel`
and confirm it returns your worktree path (NOT `C:\Programs\f1Brainz`). Paste that into your
report as isolation evidence. Worktrees lack untracked inputs — see Data Locations.

## Inherited Context
Active playbook lessons:
- **py-launcher:** `py`, never `python`; tests `py -m pytest tests/...`.
- **worktree-untracked-data:** DBs / FastF1 cache / generated records are absent from your
  worktree — use absolute main-checkout paths (Data Locations).
- **shared-files-not-on-mission-branch:** never commit `.agent-work/LESSONS.md`,
  `AGENT_FEEDBACK.md`, `CONSTELLATION_FEEDBACK.md` on your branch — return them in closeout.
- **state-note-before-detach:** rewrite the state note before any detached/multi-hour run.
- **crew-idle-strands-deliverable:** poll your own backgrounded sweeps to completion; the
  result file is the deliverable.
- **run-crew-cli-launcher-misfit:** dispatch crews via the Agent tool; record via run_crew.py
  pure functions; recover_crews before each dispatch.
- **handoff-cite-exact-seam-signature:** cite exact signatures/return types from source.
- **diagnose-first-decide-fix:** gate-1 = characterization evidence; wire-or-hold decided at
  the checkpoint from that evidence, not assumed.

Technical invariants: strict <1000 lines/file (`py -m src.utils.simplification_limits`);
pyright baseline red + non-required (gate on no NEW per-file errors); PR body via temp file +
`gh pr create -F <file>` (never heredoc / here-string for PR bodies).

## Data Locations
FastF1 telemetry cache + per-year SQLite DBs + physics store live in the MAIN checkout
(absent from your worktree):
- FastF1 cache: `C:\Programs\f1Brainz\data\telemetry` (loaders default to this absolute path).
- DBs + physics estimate store (`session_estimates` table): under `C:\Programs\f1Brainz\data\`.
Read-only from the shared path; do NOT write the main checkout's data dir. Characterize on a
representative spread (e.g. RBR 2023-Q Spa + Monaco — the views were confirmed there in #496 —
plus one high-speed + one street circuit for breadth).

## Budget
Model: **Sonnet** (commander + crews). Escalate only if a step stalls on reasoning.
Multi-hour; keep the state note current and crews polled.

## Stop Conditions
Stop and return when: a change requires editing outside your fence (float first); ALL three
views regress (return the honest-null verdict); a decision outside inherited latitude is
needed; or you need context this order doesn't cover. Return-and-query the Admiral.

## Return Shape
Final report: the **per-view characterization table** (CdA / max_power_w / traction & brake
decel / spec_drag shifts + covariance, per view, decoupled vs incumbent), the **wire-or-hold
verdict per view** (with evidence), what was wired, any fix-or-hold issue filed, the
`decision:decoupled_1d_longitudinal` status update, map impact, triage candidates, workflow
feedback, and your `git rev-parse --show-toplevel` isolation output. Open ONE PR
(`gh pr create -F <tempfile>`, title referencing #523 and "Refs #509"), checks green, verdict
in the PR body. Do NOT merge — the Admiral merges. Commit trailers required:
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` and
`Claude-Session: https://claude.ai/code/session_01Pg84miea8Tmz2egJrGg2S4`; PR body footer
`🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
