# Launch Order — Wave 9 · #629 Phase 5: as-of-stamped feature view (the product contract)

**Commander:** delegated (`constellation-commander-delegated`). **Model:** Sonnet (plumbing + contract; the subtlety is as-of/leakage correctness, not heavy math — escalate to me if a modeling call appears).
**Worktree:** `C:/Programs/f1-629` (provisioned) · **Branch:** `feat/629-feature-view` · **Base:** main `72577cef`.
**Epic:** #601 physics-as-feature-engine. **Verdict:** `C:/Programs/f1Brainz/.agent-work/epic-601/wave9-629-verdict.md`.

## Mission
Build the **product contract**: take everything Phases 2–4 built and expose it to evo through ONE clean, leakage-safe read API. This is packaging + contract, NOT new modeling. Spec: `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/DESIGN_SPEC.md`.

## What to build — four record types, one store, one read API
1. **Weekend-state record** (per event,session) — field-car state, evolution curve, environment terms, each with σ.
2. **Car-basis posterior** (per constructor,session) — the unified basis vector with **full covariance** (Phase 3's cross-view terms), session-chained (FP1→…→Q process-noise links + the parc-fermé step — note: the *fitted* parc-fermé distribution is bounded-deferred per #513; carry the framing + reserved slot, don't refit it here).
3. **Lap evidence record** (per driver,lap) — representativeness weight (from #513 `fp_representativeness`), inferred mass/mode posteriors, unit-class residuals.
4. **As-of-stamped feature view** (per event,car) — weekend-relative basis + circuit-conditional composite + σ, as-of stamped. **THE ONLY evo-facing surface.**

MODEL_VERSION keyed, append-only, constructor grain (a NAMED round-1 approximation — per-entry divergence is a banked follow-up, don't solve it). 2026 rows appear only after the Phase-3 aero mini-gate closes (note it; don't gate on it).

## Gate (freeze the tests before wiring)
- **Append-only contract test** — a MODEL_VERSION bump NEVER mutates a prior row (the "contract freeze" property, pulled forward as a test).
- **As-of leakage test** — a feature view queried "as of post-FP1" is PROVABLY unable to see FP2/FP3/Q rows — checked BY CONSTRUCTION, not by filtering after the fact. This is the load-bearing correctness property (it's what keeps the eventual A/B honest).
- **DB-only doctrine** — evo never reaches past the feature view into internals; the read API is the whole surface.
- Honest-null / honest-scoping is first-class: if a record type can't yet be honestly composed, carry it as an explicit reserved slot, don't fake it.

## Dependencies / coordination
- Builds on Phases 2 (#626 weekend state), 3 (#627 reconciled basis + covariance), 4 (#513 FP fits + representativeness) — ALL MERGED to `72577cef`.
- Coordinate with the **Phase-0 tracer's four-record contract** (the tracer round-tripped an unbuilt four-record shape — make this the real thing it round-trips against). Read the #624 tracer output first.
- Store lives in the DB (per DB-only doctrine); reuse the existing `estimate_store` / `session_estimates` patterns where they fit, don't reinvent.

## Explicit-unknown contract (OWNER HARD REQUIREMENT — binds)
Every feature-view axis/term carries a resolved/unresolved status; unmeasurable ones = reserved high-σ slots, nothing dropped. Reuse the Phase-3 machinery (`effective_axis_sigma` / `UNRESOLVED_AXIS_SIGMA_FRAC`).

## Standing directives (all binding)
- **Proactive-cleanup default:** fix small, well-understood triage items in-flight (RED-first + test) rather than parking them — but a cleanup that could touch a frozen surface rides its own commit + review; if a "small" item balloons, float it. Record fixes in the verdict.
- **DB hygiene (#632):** NEVER commit `data/*.db`; `git checkout -- data/` any dirtied; explicit `git add` paths only; check `git status data/` every gate.
- **Reap-trap discipline:** any long compute detached (Start-Process -WindowStyle Hidden), state-note-first, BOUNDED in-turn waiters (never one long reap-prone waiter); liveness = check the working python.exe CHILD PID's CPU, not the launcher stub.
- Editable-install `.pth` trap: bespoke scripts need `PYTHONPATH=C:/Programs/f1-629`; pytest is cwd-safe.
- Tests via the pinned interpreter: `py -m pytest tests/unit/physics/... -q` (or `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest` if `py` misresolves). Report exact counts.

## Process (full commander depth)
understand → plan → **cold plan-critic** (fresh context — especially: is the as-of leakage guarantee BY CONSTRUCTION, not a post-filter that can be bypassed? is the append-only property actually enforced, not just conventional?) → execute (independent implement/review crews per record type + the two gate tests) → reconcile.

## Out of scope
The injection wiring into evo (Phase 6 #630); the NN consumer (round 2). Don't build them.

## Decision routing (delegated; Admiral is your reachable tier — you CANNOT reach the human)
Float a decision you can't settle / any capability-ledger deferral / a context query → SendMessage to "main". Merge to main is MINE — open a PR (base main), hand back. Issue filing/triage = yours (fix-in-flight default).

## Deliverables
1. PR (base main, NOT merged) on `feat/629-feature-view`.
2. Verdict → `wave9-629-verdict.md`: the four record types built + their σ/status handling; the append-only + as-of-leakage gate results (by-construction proof); DB-only surface; explicit-unknown status; constructor-grain approximation named; exact test counts; DB-clean; cartographer map impact.
3. Cartographer reconcile of the net structural change.
