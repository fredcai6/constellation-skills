# Launch Order — Wave 7 · #628 Phase 3b: Driver utility on the same basis (produced, not consumed)

**Commander:** Ship H (delegated, `constellation-commander-delegated`). **Model:** Opus (modeling/stats-heavy phase).
**Worktree:** `C:/Programs/f1-628` (provisioned) · **Branch:** `feat/628-driver-utility` · **Base:** main `61b1c76e`.
**Epic:** #601 physics-as-feature-engine. **Verdict artifact:** `C:/Programs/f1Brainz/.agent-work/epic-601/wave7-628-verdict.md`.

## Mission
Build **driver utility on the same physics basis** as a round-1 artifact that is **produced, not consumed** (round-2 consumption is out of scope). Driver utility = **per-unit-class access of the car capability envelope**: a race-history prior with a weekend update, expressed per axis (corners dominate; ≈zero utility on power-to-weight; style dimensions like throttle-application timing are possible). Banked for round-2 driver-affinity consumption.

## THE load-bearing discipline — anti-circularity (critic F4). Read twice.
The gate is circular and worthless UNLESS you build it this way:
- **Car capability is a POOLED latent** — season-pooled per-constructor envelope, estimated from many observations, fit **independently of any single driver-weekend**. `src/physics/utilization/car_prior.py` is the pooled car latent and has **NO driver dimension by design**. Do not add one.
- **Driver utility is how well the driver ACCESSES that separately-estimated latent** — NOT a per-lap `observed ÷ capability` division. If you ever compute `observed/capability`, the recomposition check becomes true-by-algebra and tests nothing. That is the failure mode; avoid it structurally.
- Because capability comes from the pool and utility is measured against it, the recomposition check is genuinely falsifiable.
- `src/physics/layer2/pool_driver.py` already exists (driver pooling) — use it as the starting point / prior art; don't reinvent.

## Gate (F4 — held-out, un-gameable)
Validate on a **HELD-OUT slice**: fit utility on a subset of a driver's laps/sessions, then check on the held-out remainder that **BOTH**:
1. the **recomposition** (capability-latent ⊗ driver-utility → predicted lap/axis behavior) replicates out-of-sample, AND
2. the **per-axis structure replicates** — corners dominate, power-to-weight ≈ 0 — out-of-sample, not just on the fit laps.
Freeze the split + rubric BEFORE seeing held-out numbers (wave-4/5 methodology-freeze precedent). Directional sanity vs driver reputations (e.g. does a known qualifying specialist score high) is a **smell test only, never pass/fail**. Named limit: no external driver-utility ground truth exists — held-out replication is the substitute. State that limit plainly in the verdict.

## Explicit-unknown contract (OWNER HARD REQUIREMENT — still binds, carried from Phase 2/3)
Every axis/dimension carries an explicit resolved/unresolved status. Any axis where driver utility is unmeasurable or unidentified is recorded as a **reserved high-uncertainty slot** future effort can fill — NOT dropped. Turn implicit wide-σ into an explicit, testable "we don't know." Follow the Phase-3 pattern (`estimate_store` status field + `UNRESOLVED_AXIS_SIGMA_FRAC` sentinel) — reuse that machinery, don't invent a parallel one.

## Honest-null is a complete deliverable
A measured negative (utility doesn't replicate held-out on some/all axes) is a **complete, successful, reportable result** — report it, don't paper over it. This phase has no automated kill switch. If the held-out replication fails broadly, that is a legitimate PASS-with-honest-null verdict, recorded with the reserved-slot contract.

## Scope guardrails
- **OUT of scope:** driver-affinity *consumption*, any evo-feature consumption, delta-basis evolution (utility as its own basis — banked/open). Do not build round-2.
- Depends on the Phase-3 reconciled car-capability basis (merged, `61b1c76e`) — build on it, don't re-fit it.
- Per-axis: corners dominate; power-to-weight ≈0 (this is a *prediction* the gate tests, not an input you hardcode).

## Process (full commander depth — understand → plan → cold-critic → execute → reconcile)
- Run a **cold plan-critic** (fresh context, no authoring bias) before freezing the gate — especially to confirm you did not smuggle in `observed÷capability`. Fold dispositions.
- Build + review through independent crews; each review re-runs the load-bearing numbers on the live store.
- **Model tier:** Opus for the modeling/gate work.

## Data / stores
- SQLite is the source (no direct FastF1). Pooled car latent: `src/physics/utilization/car_prior.py`. Session estimates: `data/physics_estimates.db:session_estimates`. Telemetry: `data/telemetry_store.db`. Per-year `data/f1_data_<year>.db`.
- **DB hygiene (#632):** running samplers/fits dirties `data/*.db`. NEVER commit `data/*.db` — `git checkout -- data/` any dirtied DBs, `git add` explicit paths only. Check `git status data/` at every gate.
- **Headless compute launch rule (post-#644/#648):** any detached/headless fit MUST launch via `Start-Process -WindowStyle Hidden` or a resolved `sys.executable` path — **NOT bare `py` + subprocess.DETACHED_PROCESS** (the `py` launcher stub hangs at 0% CPU before Python starts — see #648). The #644 thread-cap guard (now in `src/physics/__init__.py`) is inherited automatically on any `src.physics` import.

## Isolation / harness (platform doctrine — follow exactly)
- You are in `C:/Programs/f1-628` ONLY. Verify with `git worktree list` before writing. Confirm the base actually carries Phase-3 deps (grep e.g. `car_prior`, `pool_driver`, the Phase-3 σ-honesty status fields) before building — the editable-install `.pth` trap means bespoke scripts can silently import MAIN `src/`; pytest is cwd-safe, bespoke scripts need `PYTHONPATH=C:/Programs/f1-628`.
- State-note-before-detach; OS-detached long compute (no per-line watchers); poll result artifacts, don't idle on a watcher (three prior ships hit the watcher-sleep stall — poll in-turn).
- Tests: `py -m pytest tests/unit/physics/... -q`. Report exact pass/fail counts.

## Decision routing (you are delegated; I am your reachable tier)
- Float a **decision** you can't settle → I adjudicate (delegated classes) or escalate (surfaced). Float a **context query** → I answer from epic knowledge and continue you.
- Deferral of any piece is a **capability-ledger decision → surface it to me** (do not silently drop). This phase is itself the epic's "top deferral candidate" — but its defer-trigger (weak Phase-0 reads / tight schedule) does NOT hold (Phases 0-3 all passed), so the directive is BUILD it. If you hit a sub-piece you believe should defer, float it with a quantified reason.
- Merge to main is MINE (do not merge; open a PR base main, I merge at the boundary). Issue filing/triage = delegated to you (file follow-ons freely).

## Deliverables (hand back)
1. PR (base main, NOT merged) on `feat/628-driver-utility`.
2. Verdict → `.agent-work/epic-601/wave7-628-verdict.md`: PASS/honest-null, the anti-circularity construction proof, the held-out gate result (recomposition + per-axis structure replication), the explicit-unknown status per axis, the reputational smell-test read (labeled non-gating), named limits, tests, DB-clean confirmation, cartographer map impact, triage/floats.
3. Cartographer reconcile of the net structural change.
