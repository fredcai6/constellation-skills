# Launch Order: Phase-6 Commander — issue #630 (prototype BT injection behind manifest toggle)

Commanders start cold. Everything you need is pasted below — do not assume prior-wave context.

## Mission
Epic #601 · Stage-1 physics-as-feature-engine · **Phase 6 — prototype injection**.

Wire the Phase-5 physics **feature view** into the evo fusion as **one more precision-weighted source, behind a manifest toggle that defaults OFF**. This is the plumbing that Phase 7's A/B will later exercise. **v1 PROTOTYPE ONLY** — direct-field injection to test signal cheaply; the eventual destination (round 2, out of scope) is a neural module consuming physics features. Do not let the prototype harden into the destination.

**The deliverable is a green, reviewed PR** that satisfies the gate below, plus a verdict artifact at `.agent-work/epic-601/wave10-630-verdict.md`.

### The gate (this is the whole success criterion — there is NO value claim here)
1. Injection wiring exists: `read_feature_view` → a `ModuleFieldResult` → joined into fusion behind a `FusionStepConfig`.
2. Unit-tested (the wiring, the toggle on/off behavior, the shape/contract of the produced field).
3. Toggled **OFF by default** everywhere (dataclass defaults AND the gold/walkforward template).
4. **The live gold pipeline runs bit-identical with the physics toggle OFF** — i.e. adding this code path changes nothing when the toggle is off. This is a *regression-safety* proof, NOT a value claim. Prove it (see "How to prove bit-identical" below).

A measured "wiring is inert when off, and here's the toggle-on path ready for Phase 7" is exactly the win. **No predictive/value claim is made or expected in this phase.**

## Prior-Wave Verdicts (pasted)

### Phase 5 (#629) — the feature-view seam you consume (MERGED, main `2e4fd5ef`)
A new subpackage `src/physics/feature_view/` is the physics→evo product boundary. **The SOLE evo-facing surface is `src.physics.feature_view.read.read_feature_view`** — a forward import-boundary guard test (`tests/.../test_evo_import_boundary.py`) enforces that evo code may import *only* that one symbol from the feature_view package. Do not import anything else from `src/physics/**` into evo code.

- `read_feature_view(...)` returns as-of-stamped rows (leakage-free by construction: a WHERE-clause session bound — it can only return rows stamped at or before the requested weekend/session). Rows carry a physics pace/capability axis with a covariance-bearing σ, plus a `transition_axis_status` signal used for reserved transition-σ widening (an axis that is unresolved for the as-of point is returned with a widened, explicitly-high σ — an honest "we don't know", never dropped or fabricated).
- Store is a separate append-only DB `data/feature_view.db` (INSERT-only, contract-frozen). It is an **untracked data input** — see Data Locations; it does NOT exist in your fresh worktree. If it is absent/empty for the weekends you test, that is fine — your unit tests should construct minimal fixtures or synthesize rows; you do NOT need a populated store to prove the wiring + the bit-identical-off gate.
- Read `src/physics/feature_view/read.py` and `records.py` FIRST to learn the exact row shape (fields, σ semantics, `transition_axis_status`). Treat this as the contract; do not reach behind it.

### Seam scout (x2-evo-seam) — the EXACT injection recipe (pasted; this is the map)
The live prediction path is `src/evo_predictor/sampled_runtime.py` (`SampledEvoRuntime.predict_from_features`): a 3-stage sampled simulator over 12 neural latent-power modules combined via Bradley-Terry field solve + precision-weighted fusion. There are **two ways a source joins fusion**:

1. **Trained-NN path** (the 12 production modules): adapter builds a `PairBatch` → NN forward → `field_solve.solve()` → `FieldSolution` → wrapped `ModuleFieldResult`. **You are NOT doing this** (no network, no training — that's round 2).
2. **Direct-field path** (what you ARE doing): construct a `ModuleFieldResult` **directly**, skipping PairBatch/NN/field_solve entirely. **The existing template for this is `src/evo_predictor/driver_residual_history_adapter.py::build_neutral_driver_residual_history_field`** (`_registry.py:247-264` registers the 3 `*_FROM_RESIDUAL_HISTORY` modules; `_runtime_builders.py:536 _make_runtime_driver_residual_history` calls it). It builds a `ModuleFieldResult` directly with `pi` (N,) and `sigma_pi` (N,N) — currently neutral/no-op. **Copy this shape.** Your physics field replaces the neutral `pi`/`sigma_pi` with values/covariance read from `read_feature_view`.

> ⚠️ **Issue-title trap:** #630's title says "wire into `field_solve.py`". The scout confirms the *direct* path **does not touch field_solve** — field_solve is the NN-path aggregator. Wiring physics into field_solve would be the wrong seam. Inject at **fusion** via a `ModuleFieldResult` + `FusionStepConfig`, mirroring the residual-history modules. (If your understand-phase finds a concrete reason the field_solve seam is actually required, that's a design divergence — FLOAT it to the Admiral before building, don't silently pick.)

**Contract to satisfy** to join fusion (all three):
- (i) a `ModuleFieldResult` satisfying `src/evo_predictor/runtime_contracts.py:89-133` validation — fields: `module_name`, `task ∈ {quali, race_start, race}`, `entity_scope ∈ {driver, constructor}`, `evidence_source ∈ {recent_history, race_weekend}`, `event_id`, `entity_ids`, `pi` (N,), `sigma_pi` (N,N) symmetric.
- (ii) a call site that produces it (a registry entry `ModuleAdapter` in `_registry.py`, OR a bespoke direct call site mirroring the residual-history runtime builder — pick whichever is the smaller, more toggle-able change; record which and why).
- (iii) a `FusionStepConfig` (`covariance_scale`, `mean_scale`, `covariance_tension_inflation`, `enabled`) added to the task's `FusionLayerConfig.fusion_order`/`steps` (`src/evo_predictor/fusion.py:23-78`). `fuse_module_fields_ordered` (`fusion.py:256-316`) does sequential Gaussian precision-weighted assimilation — smaller `sigma_pi` = more trusted = pulls the posterior harder. Constructor-scope results project to drivers via `constructor_projection.py`.

### The toggle pattern to mirror — `quali_pace_anchor_enabled` (pasted)
The production quali-pace anchor (#420) is the established "extra source behind a manifest toggle" precedent:
- Gated by a manifest flag `quali_pace_anchor_enabled`, consumed at `src/evo_predictor/sampled_runtime.py` (~line 486-495).
- **Dataclass defaults are `False`** at `src/evo_predictor/gold_cycle/config.py:76` and `src/evo_predictor/sampled_runtime_manifest_assembly.py:36`.
- The walk-forward/gold template **overrides to True** at `src/evo_predictor/walkforward/pipeline.py:186-187`.
- **YOUR physics toggle (name it something like `physics_feature_injection_enabled`) stays OFF in ALL of these — including the walkforward template.** The default-ON override that #420 has is exactly what you must NOT replicate. Off means off, everywhere, this phase.

## Pre-Rulings
Ruled in advance, each overridable if evidence contradicts it — say so when overriding.
- **Injection seam = fusion via direct `ModuleFieldResult`, mirroring `driver_residual_history_adapter.py`.** NOT field_solve. (Override → FLOAT, do not silently choose the field_solve seam.)
- **Toggle OFF everywhere, including the walkforward/gold template.** No default-ON anywhere.
- **Task scope for v1: start with `quali` only** if a single task keeps the change smaller and the gate cleaner. Physics pace maps most cleanly to the quali axis, and the scout shows quali is where the measured headroom is. Wiring all three tasks is acceptable if it's naturally uniform, but do not expand scope for its own sake. (Overridable — record your choice + why.)
- **`read_feature_view` is the ONLY symbol you may import from `src/physics/**`.** Enforced by `test_evo_import_boundary.py`. If you need something else, that's a Phase-5-seam gap → FLOAT it, don't reach behind the boundary.
- **Proactive cleanup is authorized** for small triage you touch (dead imports, a stale comment, an obvious typo in a line you're editing) — but frozen-seam or gold-template cleanups ride their own commit and get called out in your verdict. If a cleanup balloons past trivial, FLOAT it instead of absorbing it.
- **Empty/absent `feature_view.db` is fine.** Prove the wiring + bit-identical-off with fixtures/synthetic rows; a populated store is not required this phase.

## Honest-Null Clause
This phase's "result" is regression-safety, not signal. If you find the injection is inert-when-off and the toggle-on path is correctly shaped and ready for Phase 7 — that IS the complete, successful deliverable. Report it plainly. Equally, if you discover the seam **cannot** be made bit-identical-off without a design change (e.g. the fusion order mutates even when a step is disabled), that is a real finding — STOP and float it, do not paper over it.

## Inherited Latitude
- **You MAY adjudicate** (log as RULING in your verdict): implementation shape within the pre-rulings; test design; which call-site pattern (registry vs bespoke) is smaller/cleaner; naming; trivial proactive cleanup; whether to scope v1 to quali-only vs all-three tasks.
- **You MUST float to the Admiral** (return-and-query — I answer and continue you): any need to touch the field_solve seam instead of fusion; any change to the Phase-5 feature_view package or its import boundary; any inability to achieve bit-identical-off without altering existing behavior; any manifest/config schema change that affects the live gold default; scope creep beyond "wire + toggle + test + prove-inert-off".
- Decisions fitting no class above are out-of-taxonomy → float with one line on why.

## File Ownership
- Sole writer this wave of: your verdict `.agent-work/epic-601/wave10-630-verdict.md`, and all new/edited source under `src/evo_predictor/**` + new tests. No other Commander is active in evo this wave.
- Do NOT edit `src/physics/feature_view/**` (frozen Phase-5 seam — float if you think you need to).

## Workspace
Absolute worktree path: **`C:/Programs/f1-phase6`**, branch **`feat/phase6-bt-injection`**, base commit **`2e4fd5ef`** (main HEAD, Phase 5 merged).
Created via: `git worktree add -b feat/phase6-bt-injection C:/Programs/f1-phase6 2e4fd5ef`.

**First step, before any git operation:** run `py scripts/verify_worktree_isolation.py --here C:/Programs/f1-phase6` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.

NOTE: PR integration defaults to **server-side merge** (the Admiral merges the PR on GitHub). Do not local-merge to main.

## Inherited Context (platform/technical invariants — READ, these have burned prior waves)
- **Python interpreter:** the `py` launcher on this machine can shadow-resolve to a pytest-less codex runtime. For running the **test suite / any bespoke script**, use the pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest ...`. `py` is fine for the repo's own `scripts/verify_*.py` helpers.
- **Editable-install `.pth` trap:** ad-hoc scripts run from a worktree can silently import the MAIN repo's `src/` via a global editable `.pth`. pytest is safe; bespoke scripts must put the worktree first on `sys.path`. Verify any repro script actually imports YOUR worktree's code.
- **Windows shell hazards:** write PR bodies to a temp file and use `gh pr create -F <file>` — never a heredoc or PowerShell here-string for `--body` (here-strings work for `git commit -m` only). UTF-16/BOM: write files as UTF-8.
- **Reap-trap:** the harness reaps long single background waiters. This wave shouldn't need detached compute (wiring + unit tests + one gold check). If a bit-identical gold check runs long, poll it IN-TURN with BOUNDED chained waiters, or launch truly OS-detached via `Start-Process -WindowStyle Hidden` + a sentinel file — never `nohup ... &` inside a Bash tool call (harness-tracked → reaped).
- **DB hygiene:** NEVER `git add data/*.db` (or `.db-shm`/`.db-wal`). Explicit `git add <path>` only; no `git add -A`/`git add .`.
- **`quali_pace_anchor_enabled` precedent** is your best in-repo worked example of "extra source behind a manifest toggle" — read `quali_pace_anchor.py` + its call site + its config plumbing end to end before writing yours.

**Charter-lite:** this project has a `docs/agents/` overlay; read `.agent-work/LESSONS.md` Active section if present. Standing doctrine: honest-null is a complete deliverable; commanders run the full understand→plan→execute→reconcile spine (not lightweight one-shot).

### How to prove bit-identical-off (the gate's hard part)
The claim is: "with the physics toggle OFF, the gold pipeline produces byte-identical output to pre-change main." Options, cheapest first — pick and justify:
1. **Unit-level determinism proof:** a test that runs the fusion for a fixed synthetic input with the physics step present-but-disabled, and asserts the resulting `FieldSolution`/fused `pi`,`sigma_pi` are bit-identical (exact tensor equality) to the same fusion without the physics step in the order at all. This is the tightest and cheapest proof that a disabled step is truly inert.
2. **Pipeline-level:** run a short deterministic slice of the gold/walkforward pipeline (fixed seed, small fixture) on pre-change base and on your branch with toggle OFF; diff the emitted bundle/report artifacts for exact equality. Heavier — only if (1) doesn't fully cover the code path you added.
Prefer (1) as the primary gate proof; add (2) only if your change touches pipeline assembly in a way (1) can't reach. **Whichever you use, the bit-identical assertion must be EXACT (not "close"), because the claim is regression-safety.**
Beware silent non-determinism: if the disabled path still *constructs* the physics field (reads the store, allocates) even when not fusing it, that's wasted work but still must not perturb output — assert it doesn't. Ideally the toggle short-circuits before any physics work when off.

## Pre-empted Steps
- **Context/seam already mapped** — the x2 seam scout (pasted above) is the authoritative injection map; you need not re-derive the fusion/field-solve/toggle topology from scratch. Verify the specific line numbers against current `2e4fd5ef` (they were captured pre-merge and may have drifted a few lines) but trust the topology.
- **Base freshness verified** by the Admiral: `2e4fd5ef` is current main HEAD.

## Data Locations (untracked inputs — NOT in your worktree)
- Feature-view store: `C:/Programs/f1Brainz/data/feature_view.db` (Phase-5 append-only store; may be sparse/empty — you do NOT need it populated, see pre-rulings). If you want to read real rows, point at this absolute path in the MAIN checkout; do not copy DBs into the worktree, do not commit them.
- Per-year evo DBs: `C:/Programs/f1Brainz/data/f1_data_<year>.db` (only if a pipeline-level bit-identical check needs real classifications; prefer fixtures).
- Gold bundles / manifests live under the main checkout's configured gold dir — only relevant if you attempt the pipeline-level (option 2) proof.

## Budget
- **Model tier (required): Sonnet.** This is careful integration + regression-proof, not modeling. Escalate to the Admiral (float) if you hit genuine modeling ambiguity (e.g. how to map the physics σ into `sigma_pi` covariance is under-determined by the seam) rather than self-escalating the model.
- **Compute/time:** session-window. No large training. At most one short deterministic pipeline slice if you need option-2. Keep it bounded and in-turn.

## Stop Conditions
Stop and return (float to Admiral) when: the field_solve seam appears actually required; bit-identical-off is unachievable without changing existing behavior; you need a Phase-5 seam change; scope would exceed wire+toggle+test+prove-inert; or you need context this order doesn't cover and can't safely proceed. Asking up is always sanctioned — I answer and continue you with context intact.

## Return Shape
Write `.agent-work/epic-601/wave10-630-verdict.md` and post your verdict there **before** going idle. It must contain:
1. **Verdict:** gate PASS/FAIL — wiring exists ✓/✗, unit-tested ✓/✗, toggle OFF by default everywhere ✓/✗, bit-identical-off PROVEN ✓/✗ (with the exact-equality evidence).
2. **What you built:** the call-site pattern chosen (registry vs bespoke) + why; the toggle name + every location its default is set; the task scope (quali-only vs all-three) + why; how physics σ maps into `sigma_pi`.
3. **Evidence:** test names + `pytest` output (pinned interpreter); the bit-identical proof output; `py scripts/verify_worktree_isolation.py --here C:/Programs/f1-phase6` output (proof you worked in isolation); the PR URL.
4. **RULINGs** you made under inherited latitude; **floats** you're returning for my decision.
5. **Map impact** (does `docs/architecture` need a note? — likely a small evo-fusion edge) + **triage candidates** + **workflow feedback**.
6. The **green, reviewed PR** — open it (`gh pr create -F <bodyfile>`), get a clean-room reviewer subagent to review it, and report the review verdict. I merge server-side.

Deliver the artifact + verdict BEFORE going idle — an idle notification with no artifact reads as stalled, not done.
