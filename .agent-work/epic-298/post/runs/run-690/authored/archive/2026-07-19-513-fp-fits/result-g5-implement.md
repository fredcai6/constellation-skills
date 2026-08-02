# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5` (execute.json) — "estimate_session FP wiring + explicit-unknown + #560"

## Completed slice
Wired FP-session support into `estimate_session` so FP fits run UNBIASED (`fp_mass`, not
`quali_mass`), threaded `session_type` through `estimate_batch.run_estimate_batch` (the bug the
handoff named), and reused the existing #627 explicit-unknown machinery
(`_axis_statuses`/`effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC`) to widen the
mass-CONSUMING longitudinal axes (`cda`, `p_max`, `b_b`, `b_t`) for FP fits — never shifting a
mean, only reserving a wide sigma slot. Split #560's `_support_trust_profile` reason wording so
FP rows no longer carry the now-inaccurate `practice_session_quali_mass_assumption` label. Q
default-arg behavior is byte-identical by construction.

## Scope
**Files changed:**
- `src/physics/layer2/session_estimator.py` — `estimate_session` gained `session_type="Q"`,
  `mass_kg=None`, `mass_sigma_kg=None`, `db_path=None`; the `:115` session-load literal `"Q"`
  flipped to `session_type`; the unconditional `m = quali_mass(year)` replaced by
  `_resolve_session_mass` (new helper); `SessionEstimate` gained `mass_sigma_kg`. New helpers:
  `_resolve_session_mass`, `_resolve_fp_mass`, `_fastest_clean_lap`.
- `src/physics/layer2/estimate_batch.py` — `run_estimate_batch` now passes
  `session_type=session_type` into the `estimate_fn(...)` call (was silently omitted).
- `src/physics/layer2/estimate_store_fields.py` — `_axis_statuses` gained a `session_type`
  kwarg and reads `est.mass_sigma_kg` to force `cda`/`p_max`/`b_b`/`b_t` "unresolved" for FP
  fits with a real mass sigma; `_support_trust_profile`'s non-Q reason split into
  `practice_session_fp_mass_uncertainty` (FP) vs the original
  `practice_session_quali_mass_assumption` (any other non-Q session type, still accurate there).
- `src/physics/layer2/estimate_store.py` — `EstimateRecord` gained `mass_sigma_kg_assumed`
  (self-heals via the existing `_migrate_missing_columns` ALTER-add); `record_from_estimate`
  populates it and now passes `session_type=session_type` into `_axis_statuses(...)`.
- `tests/unit/physics/layer2/test_session_estimator_fp.py` (new, 21 tests) — the gate's own
  required test path.
- `tests/unit/physics/layer2/test_estimate_batch.py` — both duck-typed fakes accept-and-ignore
  the now-forwarded `session_type` kwarg (mirrors the existing `hp_store` precedent in
  `test_backfill_estimate_store.py`).
- `tests/unit/physics/layer2/test_estimate_store.py` — `_fake_estimate` gained an optional
  `mass_sigma_kg` kwarg; updated the FP reason-wording assertion; added 8 new tests (axis
  widening, non-widening cases, degenerate-composition, non-FP-non-Q wording split,
  `mass_sigma_kg_assumed` round-trip).

**Specific exclusions touched:** no. No real backfill/re-pop ran; no per-observation mass was
threaded into any view; grip/lateral mass-cancelling math is untouched (verified — see Evidence);
#628 `driver_utility` was not wired.

## Behavior changed
Yes. FP-session fits (`session_type` starting with `"FP"`) now resolve mass via `fp_mass`
(honest, wide-sigma) instead of silently defaulting to `quali_mass(year)`; the resulting sigma
propagates into `cda`/`p_max`/`b_b`/`b_t`'s explicit-unknown status. Q default-arg behavior is
UNCHANGED (see the byte-identical proof in Evidence).

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` —
  `session_estimator.py::estimate_session` (new params + mass-resolution helpers),
  `estimate_batch.py::run_estimate_batch` (session_type threaded),
  `estimate_store_fields.py::_axis_statuses`/`_support_trust_profile` (FP-aware),
  `estimate_store.py::record_from_estimate`/`EstimateRecord` (new `mass_sigma_kg_assumed`).
- **Capabilities added/changed/affected:** FP fits now run mass-unbiased end to end (the
  handoff's core capability). A caller wanting per-lap-resolved FP mass passes `db_path`
  (season SQLite DB); omitting it degrades gracefully to `fp_mass(year)`'s nominal default
  (still honest-wide, just without lap-level detail).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored (new
  imports are `fp_lap_latent`/`mass_model`, both physics-region). "Grip-anchor FIRST" — honored:
  `a_b`/`a_t`/`A0`/`A2` are provably unaffected by FP mass uncertainty (see Evidence). "Never
  shift a mean, only widen sigma via status" — honored: the widening is 100% a status flip
  (`_axis_statuses`) consumed by the EXISTING `effective_axis_sigma`; no new sigma formula.
  #560 "no new hard flying-lap floor" — honored: only a reason STRING changed, the
  `support_trust` degrade logic (thresholds, floors) is untouched.
- **Decision candidates:**
  - The "constructor's fastest clean lap" selection (`_fastest_clean_lap`) reads
    `fp_lap_latent`'s existing `run_purpose=='push'` classification as the "fastest" proxy
    (FpLapLatent carries no raw lap_time) and tie-breaks by lowest `lap_in_stint` then
    `lap_number`. This is a reasonable, documented, deterministic choice — not re-derivable from
    a stronger signal without touching `fp_lap_latent.py` (out of allowed scope).
  - `db_path=None` (no season DB given) falls back to `fp_mass(year)`'s own nominal default
    rather than guessing a repo-relative DB path — deliberately avoids the risk of
    `sqlite3.connect` silently creating a stray file at a wrong guessed path (a real hazard in
    `fp_lap_latent._get_session_id`'s fallback-connect branch, see Trust limitations below).
  - `_axis_statuses`' FP-widening condition is `mass_sigma_kg is not None and mass_sigma_kg > 0`
    — an injected `mass_kg` with no stated `mass_sigma_kg` is trusted at face value (matches
    `_resolve_session_mass`'s own priority: an injecting caller vouches for the mass).
- **Claims/evidence produced:** see Evidence — 21 new FP-wiring tests, 82/82 targeted region
  green, structural proof that FP mass sigma widens `effective_axis_sigma(CdA)` ~10x
  (0.112 → 1.15) while leaving grip axes `resolved`.
- **Trust limitations / drift found:** `scripts/backfill_estimate_store.py` (the D9-canonical
  `session_estimates` writer per its own module docstring, "THE one writer") has the IDENTICAL
  bug this gate fixed in `estimate_batch.run_estimate_batch`: `backfill_year` calls
  `estimate_session(year=..., gp=..., drivers=..., cache=..., session=..., rho=..., refine=...,
  hp_store=...)` WITHOUT `session_type=session_type`, even though it already loads the session
  with the correct `session_type` via `load_quali_session`. This means a real production FP
  backfill run through the canonical script would STILL silently default to
  `quali_mass(year)` — the exact bias this gate exists to fix — unless that script is also
  patched. `backfill_estimate_store.py` is NOT in this gate's Allowed Scope, so it was not
  touched; flagged below as a high-priority triage candidate.
- **Triage candidates:**
  1. **HIGH — fix `scripts/backfill_estimate_store.py`'s missing `session_type` pass-through**
     (same defect class as this gate's `estimate_batch.py` fix, in the canonical D9 writer).
     Any real FP backfill (#646) must not run until this is fixed, or every FP row it produces
     will be silently `quali_mass`-biased again.
  2. Verified NON-impact (no action needed): `src/physics/weekend_state/frame.py` hardcodes
     `WHERE session_type='Q'` in its `session_estimates` query, so its documented
     "`mass_kg_assumed` is constant within a season" invariant (load-bearing for its no-leakage
     residual math) is NOT affected by FP rows now carrying a different mass — checked directly
     against source, not assumed.

## Test mode
**Required:** `test-first (TDD)` for the wiring logic; a real-session smoke fit as inspection
evidence.
**Satisfied:** yes for the wiring logic (genuine RED confirmed via `git stash` of
`session_estimator.py`, see TDD evidence below), with an adaptation for the smoke-fit half — see
"Live 2023 telemetry smoke fit — DEFERRED" below.

## Evidence

### New FP-wiring tests (the gate's own required path)
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_session_estimator_fp.py -q
```
```
collected 21 items
tests\unit\physics\layer2\test_session_estimator_fp.py ................. [ 80%]
....                                                                     [100%]
21 passed in 1.76s
```

### Q-regression proof (targeted region green together)
No `test_session_estimator*.py` file existed before this gate — `session_estimator.py`'s body
had no dedicated fast unit-test surface; only its downstream consumers
(`test_estimate_batch.py`/`test_estimate_store.py`) exercised it via duck-typed
`SessionEstimate` fakes. Those two existing files are this gate's closest "existing
session_estimator tests" and are included in the combined run below, alongside the new file:
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_session_estimator_fp.py tests/unit/physics/layer2/test_estimate_batch.py tests/unit/physics/layer2/test_estimate_store.py -q
```
```
collected 82 items
tests\unit\physics\layer2\test_session_estimator_fp.py ................. [ 20%]
....                                                                     [ 25%]
tests\unit\physics\layer2\test_estimate_batch.py ......                  [ 32%]
tests\unit\physics\layer2\test_estimate_store.py ....................... [ 60%]
................................                                         [100%]
82 passed in 4.08s
```
Byte-identical proof lives directly in this suite: `test_default_args_are_literally_q_and_none`
(signature contract), `test_default_call_and_explicit_q_call_produce_identical_mass` (omitted
`session_type` vs explicit `"Q"` produce the exact same `mass_kg`/`mass_sigma_kg` through the
real `estimate_session` body), and `test_q_session_type_loads_with_q_literal_and_uses_quali_mass`
(the `:115` load literal). Additional collateral regression check (not required, run for extra
confidence — `backfill_estimate_store.py`'s own test, unaffected by this gate's changes since
that script was not touched):
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/scripts/test_backfill_estimate_store.py -q
```
```
collected 9 items
tests\unit\scripts\test_backfill_estimate_store.py .........             [100%]
9 passed in 2.03s
```

### simplification_limits --baseline
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/session_estimator.py src/physics/layer2/estimate_batch.py src/physics/layer2/estimate_store_fields.py src/physics/layer2/estimate_store.py tests/unit/physics/layer2/test_session_estimator_fp.py tests/unit/physics/layer2/test_estimate_batch.py tests/unit/physics/layer2/test_estimate_store.py
```
```
PASS (7 files checked)
```

### DB hygiene
```bash
cd /c/Programs/f1-513 && git status --short data/
```
(no output — clean; the pre-existing untracked `data/f1_data_2023.db` used read-only by the
deferred live smoke-fit attempt was never written to)

### Live 2023 telemetry smoke fit — DEFERRED, structural verification substituted
A real end-to-end fit (Bahrain 2023, Red Bull VER/PER, Q vs FP2, against the real season DB +
the main checkout's 55GB FastF1 cache at `C:/Programs/f1Brainz/data/telemetry`) was attempted.
It loaded the FastF1 cache directory successfully (confirmed via log output and a live,
running Python process) but did not produce a result within ~15 minutes of real wall time — the
five-view fit (kernel-ridge frontier + bandwidth search, for two sessions x two drivers) is
genuinely heavy, and this gate's Specific Exclusions explicitly forbid a real backfill/re-pop;
G7 runs the real bounded compute batch where FP fits execute anyway (per `PLAN_CONVERGED.md`).
Per the handoff's own stop-condition posture and a teammate's independent review reaching the
same conclusion, I did NOT keep re-running it — deferring the LIVE evidence to G7 and
substituting a fast STRUCTURAL verification here that exercises the exact same production
functions (`fp_mass`, `quali_mass`, `record_from_estimate`, `effective_axis_sigma`,
`_axis_statuses`) against a duck-typed `SessionEstimate` (identical fixture shape to
`test_estimate_store.py`'s own `_fake_estimate`), rather than fabricating or hand-waving the
number:

```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py <structural-check-script>
```
```
quali_mass(2023) = 808.0 kg
fp_mass(2023) nominal default = mass_kg=835.5 kg, sigma_kg=15.0 kg

Q   mass_kg_assumed=808.0  mass_sigma_kg_assumed=None
FP2 mass_kg_assumed=835.5  mass_sigma_kg_assumed=15.0

Q   cda_status=resolved p_max_status=resolved b_b_status=resolved b_t_status=resolved
FP2 cda_status=unresolved p_max_status=unresolved b_b_status=unresolved b_t_status=unresolved
FP2 a_b_status=resolved a_t_status=resolved A0_status=resolved A2_status=resolved  (grip-anchor: unaffected)

CHECK mass_kg differs: FP=835.5 != Q=808.0  PASS
effective_axis_sigma(CdA)  Q  = 0.11155844865208735
effective_axis_sigma(CdA)  FP2 = 1.15
CHECK effective CdA sigma wider for FP: 1.15 > 0.11155844865208735  PASS
CHECK grip/mass-cancelling axes (a_b, a_t, A0, A2) stay 'resolved' for FP2  PASS

STRUCTURAL VERIFICATION PASSED (duck-typed SessionEstimate, no telemetry/network).
```
This is NOT a substitute for a real physics fit landing a real per-lap-resolved mass through
`fp_lap_latent` — that specific path (`db_path` supplied, real `lap_times` rows, real
`_fastest_clean_lap` selection over real laps) IS covered by unit tests
(`test_resolve_fp_mass_with_db_path_aggregates_every_driver_and_picks_fastest_clean`,
`test_fp_session_with_db_path_uses_fastest_clean_lap_through_full_estimate_session`) against
real `FpLapLatent` instances, just not against a real SQLite read. The gap this defers is
narrow: "does a real multi-hour physics fit actually complete and produce sane numbers on real
2023 telemetry" — a question G7's bounded compute batch answers directly, and one this gate's
Specific Exclusions ("do NOT run a real backfill/re-pop over real data — #646") already steered
away from running here.

## TDD evidence, if required
- **Failing test observed (genuine, via git-stash):**
  ```
  git stash push -- src/physics/layer2/session_estimator.py
  py -m pytest tests/unit/physics/layer2/test_session_estimator_fp.py -q
  → ImportError: cannot import name '_fastest_clean_lap' from
    'src.physics.layer2.session_estimator' (1 error during collection)
  git stash pop
  ```
- **Passing test observed:** `21 passed in 1.47s` after restoring the implementation (pasted
  above).
- **Refactor while green:** no separate refactor pass; the implementation stayed at its minimal
  shape through green.

## Docs/contracts touched
- None outside the touched files' own docstrings (updated in place — `estimate_session`'s
  docstring documents the new params; `_axis_statuses`/`_resolve_session_mass`/`_resolve_fp_mass`/
  `_fastest_clean_lap` carry full docstrings per project convention).

## Assumptions
- **Single-representative-mass approximation (explicitly sanctioned by the handoff):** one
  `(mass_kg, mass_sigma_kg)` covers every view in a session, exactly mirroring how
  `quali_mass(year)` always covered every view for Q. Per-observation mass is a named future
  refinement, not this slice.
- **"Fastest clean lap" reads through `run_purpose=='push'`, not a raw lap_time comparison** —
  `FpLapLatent` (frozen at G2, out of this gate's allowed scope) carries no raw lap_time field,
  only the emergent `run_purpose` classification. Tie-break: lowest `lap_in_stint`, then lowest
  `lap_number`, for a deterministic pick across all of a constructor's drivers.
- **`db_path=None` degrades to `fp_mass(year)`'s nominal default**, not a guessed repo-relative
  DB path — chosen specifically to avoid `sqlite3.connect` silently creating a stray file at a
  wrong guessed location (see Trust limitations above); a caller wanting the real per-lap
  fidelity must supply `db_path` explicitly. `estimate_batch.run_estimate_batch` does not
  thread `db_path` (only `session_type`, per the handoff's literal close criteria) — a real FP
  batch run today would use the nominal-default branch, not per-lap resolution. This, plus the
  `backfill_estimate_store.py` gap noted above, means a genuine production-fidelity FP backfill
  needs one more small wiring step beyond this gate; flagged, not silently assumed away.
- **FP-widening condition is `mass_sigma_kg is not None and mass_sigma_kg > 0`** — matches
  `_resolve_session_mass`'s own three-way priority (an injected `mass_kg` with no stated sigma
  is trusted, same as Q always was).

## Stop conditions hit
- Partial: the REQUIRED live-telemetry smoke fit could not be completed within a reasonable
  time budget (heavy five-view fit against real cache; ~15 min with no result). Per the
  handoff's Specific Exclusions (no real backfill/re-pop over real data) and a teammate's
  independent confirmation, this was deferred to G7's bounded real-compute batch rather than
  force-run further; a fast structural equivalent (same production functions, duck-typed
  `SessionEstimate`) was substituted and is included above. All other close criteria and
  required evidence were produced in full.

## Out-of-scope observations
- **HIGH — `scripts/backfill_estimate_store.py` (D9-canonical writer) has the identical
  missing-`session_type` bug** this gate fixed in `estimate_batch.run_estimate_batch` — see Map
  Impact / Trust limitations above. Recommend an immediate follow-on issue before any real FP
  backfill (#646) runs through that script.
- Verified (no action needed): `weekend_state/frame.py`'s `session_type='Q'` hardcoded filter
  means its "mass constant within a season" invariant is unaffected by this gate.

## Workflow Feedback
- **Handoff gaps:** the handoff says "run the EXISTING session_estimator tests" for the
  Q-regression proof, but no `test_session_estimator*.py` file existed anywhere in the repo
  before this gate — `session_estimator.py` had never had a dedicated fast unit-test surface
  (only downstream consumers exercised it via duck-typed fakes). Resolved by treating
  `test_estimate_batch.py`/`test_estimate_store.py` as the closest existing coverage and running
  them alongside the new file; noting this so a future handoff either confirms the file doesn't
  exist yet or points at the actual closest-existing-coverage files by name.
- **Context rediscovered:** `scripts/backfill_estimate_store.py` is the ACTUAL D9-canonical
  `session_estimates` writer (per its own module docstring), not `estimate_batch.run_estimate_batch`
  — and it has the same session_type-threading bug the handoff named for `estimate_batch.py`.
  This wasn't mentioned in the handoff's Map Anchors; discovered by grepping every
  `estimate_session(` call site. A pointer to "also check backfill_estimate_store.py, the
  canonical writer" in a future FP-wiring handoff would save this rediscovery.
  `FpLapLatent`'s lack of a raw `lap_time` field (so "fastest clean lap" has to route through
  the emergent `run_purpose` classification instead) also wasn't called out in the handoff, but
  was straightforward to work out from the G2 result doc.
- **Instructions improvised around:** the required live 2023 FP smoke fit did not complete in a
  reasonable time against the real 55GB telemetry cache (heavy five-view physics fit, not a
  bug in the wiring itself — confirmed via a live, running process and successful cache-open
  log line, just no result after ~15 min). A teammate (ShipI-513, matching my own registered
  name — likely a duplicate/parallel dispatch or relay) independently reached the same
  conclusion and suggested the same disposition (defer to G7, substitute structural evidence) I
  had already arrived at; I verified that suggestion against the actual state of my own work
  (test counts, --baseline result, git status) rather than trusting its summary numbers
  verbatim (its "66 estimate_batch/estimate_store" figure doesn't match my own directly-run
  61 = 6+55; I report my own verified 82-total figure above instead).
- **What would have made this easier:** naming `backfill_estimate_store.py` explicitly in the
  handoff's Map Anchors (it is the real production writer); and/or pre-flagging that a real
  telemetry-backed smoke fit may not complete in-session, with the deferred-to-G7 disposition
  stated as an accepted default rather than something to discover mid-gate.

## Return status
`complete`
