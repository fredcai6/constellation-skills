# Launch Order: `cmdr-T — #546 decoupled estimator throttle/coast re-evaluation`

Commanders start cold. Paste, don't point. **Run the FULL `constellation-commander` gated spine**
(understand → plan → implement → review → integrate). Multi-step commander (user preference).
This is investigation-first, wire-or-hold: characterize BEFORE any production wiring.

## Mission
#523 (509-w3) found the decoupled longitudinal estimator HOLDs on throttle/coast (honest-null) —
root-caused to LOOSE Kalman-RTS coupling (`sig_a_soft_other=30.0`) not preserving throttle-on
frontier structure on complex topology. #546 is the re-evaluation: **retune the throttle-on soft-obs
HP and the coast path, re-characterize with Config-C parity, then wire-or-hold per the acceptance bar.**

Two sub-investigations:
1. **Throttle (Traction/PowerDrag):** introduce/tune a `sig_a_soft_throttle` (try the 1.0–5.0 range —
   tighter than braking-deference 30.0, looser than braking's 0.10) and re-run the Config-C parity
   characterization. Acceptance: parity shifts **<1σ on all three circuits** (Belgium/Monaco/Bahrain).
2. **Coast:** investigate the filter-lag mechanism (Kalman-RTS produces positive `a_long` at coast
   segment boundaries → 22–28% systematic sample loss). May require clamping the coast output to the
   raw `f_vehicle` signal instead of `a_long`. Acceptance: **sample loss <10%, no directional shift >1.5σ.**

If acceptance is met → wire that view onto the decoupled path (in-fence). If not → **honest-null**:
document the result, keep the view on the incumbent, update the decision anchor + #546. Honest-null
is a complete, successful deliverable.

## Prior-Wave Verdicts (pasted)

**#546 full text:**
> #523 measured the decoupled estimator vs incumbent `clean_longitudinal_from_raw` for Traction/
> PowerDrag/Coast → HONEST-NULL, all HOLD. A Config-C parity round (decoupled `a_long` + incumbent raw
> `v_at` from `spd_d["V"]`) isolated the `a_long` contribution.
> **Config-C parity results:** TractionView — Belgium +0.37σ/+0.15σ (passes), Monaco +4.0σ/-2.7σ (HOLD),
> Bahrain -6.2σ/+9.4σ (HOLD). PowerDragView — Belgium -0.98σ/+1.62σ (notable), Monaco -13.4σ/-8.4σ (HOLD),
> Bahrain -11.3σ/-5.3σ (HOLD). The v-source confound explained Belgium-Traction + the Monaco-PowerDrag
> degenerate flag (now degenerate=False, CdA=0.928 under C); Bahrain is virtually unchanged (7.1σ→6.2σ,
> almost all from `a_long`); Monaco PowerDrag stays 8–13σ.
> **Root cause:** LOOSE coupling (`sig_a_soft_other=30.0`) at throttle-on doesn't preserve frontier accel
> structure on complex topologies (Belgium simple → passes; Monaco/Bahrain complex → fail).
> **Coast:** already parity by construction (both use raw `car["Speed"]/3.6`); shifts + 22–28% sample loss
> are from `a_long` alone → investigate filter lag; may need to clamp to raw `f_vehicle`.
> **Acceptance:** (1) throttle Config-C shifts <1σ on all three circuits with a new `sig_a_soft_throttle`;
> (2) coast sample loss <10%, no directional shift >1.5σ.
> **Methodology:** re-use the Config-C parity script `scripts/characterize_decoupled_views.py`.

**Seam facts (verified — on origin/main `8a19c5bc`, your base):**
- `scripts/characterize_decoupled_views.py` IS present in your worktree (landed via #547). Re-use/extend it
  for the Config-C re-characterization — verify its current interface from source before relying on it.
- The soft-obs coupling HP (`sig_a_soft_other`) lives in the decoupled estimator
  (`src/physics/layer2/decoupled_calibration.py` / `decoupled_longitudinal.py`) — confirm the exact symbol
  + call site from source. The throttle/coast views read it via `session_traction.py` / `session_coast.py`.
- `clean_longitudinal_from_raw` (incumbent anchor) is defined in `layer2/braking_view.py:84`; keep it defined.
- decision anchor: `docs/architecture/decisions/decoupled-1d-longitudinal.md` (update if you change wiring/status).

## Pre-Rulings (overridable with stated evidence)
- **Characterize before wiring (diagnose-first).** Re-run Config-C parity with the new HP BEFORE any
  production cutover; decide wire-or-hold per view from that evidence.
- **Wire-or-hold, never blind-cut.** A view that still regresses stays on the incumbent; document + keep
  the #546 remainder. Honest-null (tuning doesn't reach <1σ) is a valid complete verdict.
- The `sig_a_soft_throttle` retune IS this issue's job — changing this measured-number behaviour is
  delegated (NOT a surfaced units/convention class). If you find it re-opens a units/convention question,
  float.

## Honest-Null Clause
A measured negative ("no throttle HP in 1–5 reaches <1σ on all three circuits" / "coast needs more than a
clamp") is a complete deliverable. Report with full rigor (the Config-C table per HP tried).

## Inherited Latitude
MAY (delegated): in-fence HP retune + wiring + the characterization script, filing follow-ons, updating the
decision anchor. MUST float: editing OUTSIDE the fence (esp. cmdr-P's pyright lane) BEFORE doing so; any
change re-opening a units/convention class; scope beyond #546.

## File Ownership
**Sole writer this wave for the decoupled/throttle/coast subtree:** `src/physics/layer2/decoupled_longitudinal.py`,
`decoupled_calibration.py`, `decoupled_braking_input.py`, `session_traction.py`, `session_coast.py`,
`traction_view.py`, `power_drag_view.py`, `coast_view.py`, and `scripts/characterize_decoupled_views.py`,
plus new tests under `tests/unit/physics/layer2/`. If you fix any pyright errors in session_traction.py
(L142) / session_coast.py (L107) as a side effect, that's yours (cmdr-P is fenced out of these files).
**Do NOT touch** anything outside this subtree — cmdr-P (#549 pyright ratchet) owns the rest. Float if you must.
Findings file: `<admiral-worktree>/.agent-work/509-w4/crew-handoffs/cmdr-T-findings.md` — i.e. absolute
`C:\Programs\f1Brainz-509w4\.agent-work\509-w4\crew-handoffs\cmdr-T-findings.md` (sole writer).

## Workspace
Worktree provisioned: `C:\Programs\f1Brainz-509w4-coast` (branch `feat/509w4-throttle-coast`, base origin/main `8a19c5bc`).
Created: `git worktree add -b feat/509w4-throttle-coast ../f1Brainz-509w4-coast origin/main`.
First, before any git op: `verify_worktree_isolation.py` does NOT exist — run
`git -C "C:\Programs\f1Brainz-509w4-coast" rev-parse --show-toplevel`; it must return your worktree path
(NOT `C:\Programs\f1Brainz`, which is on the user's unrelated feat/541 branch). Paste it in your report.

## Inherited Context
- **py-launcher:** `py` not `python`; tests `py -m pytest`.
- **worktree-untracked-data:** DBs/cache absent from your worktree — absolute paths (Data Locations).
- **shared-files-not-on-mission-branch:** do NOT COMMIT `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md`/
  `CONSTELLATION_FEEDBACK.md` on your branch. Writing AGENT_FEEDBACK.md on disk (uncommitted) for your
  spine `feedback` step is fine/required; do NOT run `apply_lessons_delta.py` — return `lessons-delta.json`
  in your closeout report (the Admiral applies centrally).
- **frontier-characterize-v-source (NEW):** when characterizing frontier-fitting views, hold v-source parity
  (the #523 confound) — Config-C already does this; preserve it.
- **diagnose-first-decide-fix; handoff-cite-exact-seam-signature; state-note-before-detach; crew-idle-strands-deliverable; run-crew via Agent tool.**
Invariants: <1000 lines/file (`py -m src.utils.simplification_limits`); pyright non-required + now gated on a
baseline-diff (your PR must not ADD pyright errors); PR body via temp file + `gh pr create -F` (never heredoc).

## Data Locations
Telemetry cache + DBs in the MAIN checkout `C:\Programs\f1Brainz\data` (absent from your worktree; read-only,
do NOT write there). Characterize on Belgium/Monaco/Bahrain 2023-Q (the #523/#546 circuits) at minimum.

## Budget
**Sonnet**, full commander depth. Multi-hour; keep the state note current + crews polled.

## Stop Conditions
Stop/return when: a change needs editing outside your fence (float first); the retune can't reach acceptance
(return the honest-null + evidence); a decision outside inherited latitude; or missing context.

## Return Shape
Per-view Config-C table for each `sig_a_soft_throttle` value tried + the wire-or-hold verdict per view + what
(if anything) you wired + coast result + decision-anchor status update + the `rev-parse --show-toplevel`
isolation output + map impact + triage candidates + workflow feedback/lesson candidates (returned, not applied).
Open ONE PR (`gh pr create -F <tempfile>`, title referencing #546 + "Refs #523 #509"), required checks green,
verdict in the PR body, do NOT merge (Admiral merges). Commit trailers: `Co-Authored-By: Claude Opus 4.8
<noreply@anthropic.com>` + `Claude-Session: https://claude.ai/code/session_01Pg84miea8Tmz2egJrGg2S4`;
PR footer `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
