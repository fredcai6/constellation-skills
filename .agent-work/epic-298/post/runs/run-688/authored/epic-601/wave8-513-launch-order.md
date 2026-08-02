# Launch Order — Wave 8 · #513 Phase 4: FP-session fits (mass / representativeness / parc-fermé)

**Commander:** Ship I (delegated, `constellation-commander-delegated`). **Model:** Opus (deepest/most-complex phase).
**Worktree:** `C:/Programs/f1-513` (provisioned) · **Branch:** `feat/513-fp-fits` · **Base:** main `27b6eac9`.
**Epic:** #601 physics-as-feature-engine. **Verdict artifact:** `C:/Programs/f1Brainz/.agent-work/epic-601/wave8-513-verdict.md`.

## Mission — the deliberately load-bearing "deepest piece"
Extend the physics estimator to fit **FP (free-practice) sessions**, solving the "estimator fixed at quali because mass is hard" problem the whole architecture exists for. FP is a WEAK car-performance demonstrator but a STRONG driver-utility demonstrator; its **main product feeds Phase 3b (#628, merged)**; car-capability is a heavily-downweighted byproduct that only NUDGES the season-pooled estimate. Round-1 deliverable; honest-null at the gate is complete and reportable.

## What to build
1. **`fp_mass()` + per-lap latent state.** Today `session_estimator.py:125` applies `quali_mass(year)` UNCONDITIONALLY (also in session_braking/coast/traction/race) → running FP today produces silently **fuel-biased** numbers. Build `fp_mass()` + per-lap latent (fuel mass, engine mode, run purpose). **Compound is directly observed in lap data — use it**, don't infer it.
2. **Grip-class apex speeds as the mass-robust anchor** (lateral capability largely mass-CANCELS) — anchor grip FIRST; **power-to-weight extracted from the confounded straight/traction classes SECOND** (straight-line residual decomposed after grip is pinned). **Sandbagging / detuned engines → WIDER σ, NEVER bias** (the honest-unknown discipline).
3. **Weekend car-state chain FP1→FP2→FP3→[parc-fermé]→Q with PROCESS NOISE** (teams tweak/learn between sessions). The **parc-fermé reaction step is a LEARNABLE per-team distribution** (how well a team converts Friday info into Saturday pace).
4. **Continuous representativeness weights — nothing binary-dropped.** Every FP lap earns a weight from its OBSERVATION properties.

## Gate (pinned — freeze BEFORE seeing numbers)
- **FP × regime coverage map with quantified σ vs the Q baseline.**
- **Representativeness is a property of the OBSERVATION (compound, fuel, run-purpose), NOT the session.** "FP3 usually matters most" must be **EMERGENT** (FP3 happens to hold the most quali-representative laps), never a hardcoded session weight. If a team quali-sims in FP2, THAT lap earns the weight.
- **The learned weighting MUST BEAT a "weight purely by clock-distance-to-Q" baseline on HELD-OUT weekends** (critic F10) — otherwise it merely rediscovered the calendar. A known **sandbagging weekend must visibly discount**. This is the load-bearing falsifiable gate.
- Freeze the split + rubric before any held-out number (wave-4/5/7 methodology-freeze precedent).

## Dependencies / coordination
- **Builds on #627 (Phase 3, merged)** — FP fits need the trustworthy reconciled Q basis to project against. Frames its output for #628 (Phase 3b, merged).
- **Phase-2 evolution latent must stand FIRST** — a green-track FP1 lap looks slow for TRACK reasons, not car reasons (#626's within-session evolution). Use it; do not re-confound track-state with car-pace.
- **Coordinate with #560 (thin-fit acceptance floor)** — FP sessions are FULL of thin runs; #560's min-flying-laps/sample floor is directly relevant. COORDINATE, do not duplicate. Read #560 first.
- **Carries the Phase-2 Layer-2 UNLOCK (from #626 deferral):** record **per-car representative-lap `cumulative_track_laps` into `session_estimates`** (it exists in damage_store/race_stint_store as the W3 axis but NOT in session_estimates). This makes per-car within-session grip evolution possible — an explicit Phase-4 deliverable annotated on #513. Do it if in-scope-and-tractable; if it balloons, float a bounded-defer with a quantified reason (capability-ledger decision → surface).
- **#646 (store re-pop) is now UNBLOCKED** (#644 merged). Phase 4 FP fits write to the store; coordinate the re-batch (populate the #627 cross-view-covariance/σ-honesty columns) — either fold it in or hand it back as a clean follow-on. Surface if it forces a scope decision.

## Explicit-unknown contract (OWNER HARD REQUIREMENT — still binds)
Every FP-derived axis/observation carries an explicit resolved/unresolved status; unmeasurable ones = reserved high-σ slots, nothing dropped. Reuse the Phase-3 machinery (`estimate_store` status field + `UNRESOLVED_AXIS_SIGMA_FRAC` + `effective_axis_sigma`). Sandbagging/detuned = wider σ, never bias, is a direct instance of this.

## Compute (HEAVIEST phase — read carefully)
- **Headless launch:** `Start-Process -WindowStyle Hidden` or resolved `sys.executable` — NEVER bare `py`+`subprocess.DETACHED_PROCESS` (the launcher stub hangs at 0% CPU pre-Python, #648).
- **Thread recovery (owner-approved plan):** the #644 single-thread cap in base ~2x's fit time. Recover speed by setting explicit `OPENBLAS_NUM_THREADS`/`OMP_NUM_THREADS`=N (e.g. 4) in the detached launch ENV — the guard's `setdefault` RESPECTS the override (torch stays 1, but FP fits are scipy/numpy-BLAS, not torch). **LIVENESS-CHECK FIRST** (confirm the detached proc accumulates real CPU in the first ~1-2 min, not 0%), single-thread FALLBACK if a headless hang appears. Follow-on #650 tracks reconsidering the cap globally — do NOT change the guard here.
- **Reap-trap discipline (LEARNED from Ship H's whole run):** long single background waiters get HARNESS-REAPED, killing your wake mechanism. Poll IN-TURN with **BOUNDED CHAINED waiters** (short windows, re-armed), never one long waiter. State-note-BEFORE-detach. Report proof-of-life at the frozen-gate boundary and again when the batch completes.

## Process (full commander depth)
understand → plan → **cold plan-critic** (fresh context — especially test that representativeness genuinely beats clock-distance-to-Q and isn't the calendar in disguise; and that grip-anchor-then-power-residual isn't circular) → execute (independent implement/review crews per gate) → reconcile. Honest-null is first-class.

## Isolation / harness / DB
- Work ONLY in `C:/Programs/f1-513`. Verify `git worktree list` before writing. Confirm base carries deps (grep `quali_mass`, `session_estimator`, the #627 σ-honesty status fields, #628 `driver_utility`) — editable-install `.pth` trap: bespoke scripts silently import MAIN `src/`; pytest cwd-safe, bespoke scripts need `PYTHONPATH=C:/Programs/f1-513`.
- **DB hygiene (#632):** NEVER commit `data/*.db`; `git checkout -- data/` any dirtied; `git add` explicit paths only; check `git status data/` every gate. New scratch/banked DBs → gitignore glob.
- Tests: `py -m pytest tests/unit/physics/... -q`, report exact counts.

## Decision routing (you are delegated; the Admiral is your reachable tier — you CANNOT reach the human)
- Float a DECISION you can't settle, any capability-ledger DEFERRAL (surface, don't silently drop), or a CONTEXT QUERY → SendMessage to "main". I adjudicate or escalate.
- Merge to main is MINE — do NOT merge; open a PR (base main) and hand back. Issue filing/triage = yours.

## Deliverables (hand back — front-load the critical trio if the reap trap threatens)
1. PR (base main, NOT merged) on `feat/513-fp-fits`.
2. Verdict → `.agent-work/epic-601/wave8-513-verdict.md`: PASS/honest-null; the fp_mass + latent-state construction; grip-anchor→power-residual proof (non-circular); the FP×regime coverage+σ map; the held-out weighting-beats-clock-distance result (+ sandbagging-discount demonstration); explicit-unknown status; per-car `cumulative_track_laps` unlock status; #646 re-pop disposition; named limits; exact test counts; DB-clean confirmation; cartographer map impact; #560 coordination note; the #644-cap compute-tax note.
3. Cartographer reconcile of the net structural change.
