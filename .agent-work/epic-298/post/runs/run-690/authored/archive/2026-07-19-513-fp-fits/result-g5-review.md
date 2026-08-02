# Review Result

## Assigned Gate
`g5` (execute.json) — "estimate_session FP wiring + explicit-unknown + #560"

## Result
`APPROVE`

## Handoff compliance
All close criteria reproduced independently (not just re-read from the report):

1. `estimate_session` gained `session_type: str = "Q"`, `mass_kg: Optional[float] = None`,
   `mass_sigma_kg: Optional[float] = None`, `db_path: str | None = None`; the `:115` load literal
   flipped from the hardcoded `"Q"` to `session_type` — confirmed by direct diff read.
2. **Q BYTE-IDENTICAL (hard check 1):** `_resolve_session_mass`'s Q branch is
   `return quali_mass(year), None` — the exact old unconditional `m = quali_mass(year)` line,
   relocated verbatim. Proven by `test_default_call_and_explicit_q_call_produce_identical_mass`
   (omitted `session_type` vs explicit `"Q"` produce identical mass/sigma through the real
   function body) and by the Q/store regression suite (66/66 green, reproduced live).
3. `estimate_batch.run_estimate_batch` now passes `session_type=session_type` into the
   `estimate_fn(...)` call — this was the literal bug named in the handoff (the session loaded
   with the right type, but `estimate_session` never told). Confirmed in the diff; the fake
   estimators in `test_estimate_batch.py` were updated to accept-and-ignore the newly-forwarded
   kwarg, and the batch suite still passes (66/66).
4. **σ WIDENS, NEVER SHIFTS (hard check 2):** `_axis_statuses` gained a `session_type` kwarg and
   reads `est.mass_sigma_kg`; when `session_type.startswith("FP")` and a real (`> 0`) mass sigma
   is present, `cda`/`p_max`/`b_b`/`b_t` are forced `"unresolved"`. This status feeds the
   **pre-existing, unmodified** `effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC` machinery
   (verified: neither function appears in the diff at all) — no parallel σ path was invented, and
   no mean is ever touched (`drag_area_closed_m2` etc. are only nulled on genuine PowerDrag
   degeneracy, an unrelated pre-existing branch). Grip/lateral (mass-cancelling) axes
   `a_b`/`a_t`/`A0`/`A2` are independently confirmed untouched by the widening logic (read the
   source: only `cda_ok`/`b_b_ok`/`b_t_ok` gain the `fp_mass_unresolved` term).
5. **FP PATH REACHABLE:** confirmed structurally end-to-end — `run_estimate_batch` →
   `estimate_session(session_type=...)` → `_resolve_session_mass` → `mass_sigma_kg` on
   `SessionEstimate` → `record_from_estimate(session_type=...)` → `_axis_statuses(...,
   session_type=session_type)`. Not dead code: exercised by 21 new unit tests, and
   `record_from_estimate`'s only call site (`estimate_store.py:327`) already passed
   `session_type` prior to this gate (only `_axis_statuses`' own signature needed to accept it).
6. #560 `_support_trust_profile`: FP rows now get reason `practice_session_fp_mass_uncertainty`
   (any other non-Q/non-FP type keeps the original `practice_session_quali_mass_assumption`);
   trust degrade stays at `"medium"` in both cases — a wording fix, not a new floor. Confirmed via
   diff + reproduced tests.
7. Injected `mass_kg` without a stated σ passes through unchanged and does **not** trigger
   widening — confirmed by `test_axis_status_fp_without_mass_sigma_not_widened` and
   `test_injected_mass_kg_bypasses_quali_and_fp_paths`.
8. The required live 2023 FP smoke fit is **DEFERRED to G7** per the review handoff's own accepted
   disposition — not blocked on, per explicit instruction.

## Scope drift
None. `git status --short` shows only the 4 Allowed-Scope src files
(`session_estimator.py`, `estimate_batch.py`, `estimate_store_fields.py`, `estimate_store.py`)
plus the 3 test files (2 modified, 1 new at the exact required path
`tests/unit/physics/layer2/test_session_estimator_fp.py`). `scripts/backfill_estimate_store.py`
(flagged in Trust limitations, see below) is genuinely untouched.

Specific Exclusions honored:
- `git status --short data/` clean — no backfill/re-pop, no `data/*.db` write.
- Mass is resolved **once** per session and passed identically into every braking/traction/
  power_drag fit call across all `n_rounds` — no per-observation threading.
- `braking_view.py`/`traction_view.py`/`lateral_view.py` are entirely absent from the diff — grip/
  lateral mass-cancelling math is untouched; only the `_axis_statuses` status routing changed.
- No `driver_utility`/#628 references anywhere in the diff.

## Evidence verdict
Every required evidence item independently reproduced, live, in this review session:

- `tests/unit/physics/layer2/test_session_estimator_fp.py -q` → **21 passed**.
- Combined `test_session_estimator_fp.py` + `test_estimate_batch.py` + `test_estimate_store.py`
  → **82 passed** (exact match to the implementer's claimed evidence).
- `test_estimate_batch.py` + `test_estimate_store.py` + `test_estimate_store_cumulative.py` →
  **66 passed**.
- `py -m src.utils.simplification_limits --baseline --paths <4 touched src files>` → **PASS (4
  files checked)**.
- `git status --short data/` → clean.
- **Genuine TDD RED reproduced live**: `git stash push -- src/physics/layer2/session_estimator.py`
  → `py -m pytest tests/unit/physics/layer2/test_session_estimator_fp.py -q` →
  `ImportError: cannot import name '_fastest_clean_lap'` (exact match to the claimed evidence) →
  `git stash pop` cleanly restored the working tree (`git status` identical before/after; 21/21
  green again afterward).

The deferred live-2023-telemetry smoke fit was not required per the review handoff; its
structural-verification substitute in `result-g5-implement.md` is consistent with the
independently-reproduced axis-status test behavior, so it reads as genuine, not fabricated.

## Code/doc quality
Minimal, well-scoped change. Every handoff constraint checked individually:
- Physics-region import discipline: `grep` for `evo|latent_power|compound_prior|fastf1` across
  all 4 touched files + `fp_lap_latent.py` — zero hits.
- `#627` machinery reused verbatim (no new sigma formula anywhere in the diff).
- `fp_mass`/`fp_lap_latent` correctly imported and reused from G2.
- No `print()`/logging added; no new module-level mutable state.
- `getattr(est, "mass_sigma_kg", None)` matches the file's pre-existing
  `getattr(est, "braking"/"traction"/"lateral", None)` duck-typing convention — not new
  caller-probing.
- Docstrings are thorough, cross-referenced, and match surrounding convention; degradation/
  uncertainty-inflation behavior is visible in both code comments and tests.

## Map impact verdict
- **Evidence supports claimed change:** yes — every Map Impact claim independently reproduced (see
  Handoff compliance above).
- **Constraints not violated:** yes — physics-region, grip-anchor-first, sigma-widens-never-shifts,
  and #560-no-new-hard-floor all independently confirmed.
- **Notes match the diff:** yes — structural anchors listed match the touched functions exactly.
- **Decision candidates surfaced:** yes — the `_fastest_clean_lap` selection heuristic and the
  `db_path=None` fallback choice are both documented as deliberate, bounded decisions, not silently
  assumed.
- **Durable context routed:** yes, and independently re-verified at source (not just trusted):
  - `weekend_state/frame.py`'s "hardcoded `session_type='Q'`, unaffected by FP mass" claim —
    confirmed directly, line 74 literally reads
    `"FROM session_estimates WHERE session_type='Q' AND fit_status='ok'"`.
  - `scripts/backfill_estimate_store.py` "D9-canonical writer has the identical missing-
    `session_type` bug" claim — **confirmed directly** at lines 140-143: `estimate_session(year=...,
    gp=..., drivers=..., cache=..., session=..., rho=..., refine=..., hp_store=...)` genuinely
    omits `session_type=session_type`, despite the module's own docstring claiming "THE one
    writer." A real FP backfill run through this canonical script today would still silently
    default to `quali_mass`. Correctly flagged HIGH-priority triage by the implementer and
    re-flagged by this review (`flag-candidate tc1` on the survey).

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation beyond the
already-surfaced triage candidate above.

## Refactoring pass (Fowler)
Recorded to `.agent-work/513-fp-fits/g5-review/fowler-pass.json`; cleared
`scripts/verify_fowler_pass.py` (`smells=12, flagged=[feature-envy, data-clumps,
long-parameter-list], overridden=[primitive-obsession, speculative-generality]`).

- **flagged** (minor, non-blocking): `_fastest_clean_lap`'s feature-envy toward `FpLapLatent`
  (documented trade-off — `fp_lap_latent.py` is frozen/out of this gate's scope); a data-clump in
  the `(year, gp, drivers, session_type, mass_kg, mass_sigma_kg, db_path)` parameter set; and
  `estimate_session`'s growing parameter list (12→16, all keyword/defaulted).
- **overridden**, both with a logged standard + reason: primitive-obsession against the module's
  own established raw-float/raw-str field convention; speculative-generality against
  `GATE_PROTOCOL.md`'s frozen F2/F10 mass-σ-propagation requirement + the handoff's own Authority
  section explicitly mandating the `db_path`/`mass_kg`/`mass_sigma_kg` hooks for G7's
  already-scheduled consumption (also exercised directly by 3 of the 21 new unit tests, not dead
  code).

## Blockers
- none

## Out-of-scope observations
- **HIGH — `scripts/backfill_estimate_store.py` (D9-canonical `session_estimates` writer) is
  missing `session_type=session_type` in its `estimate_session(...)` call (lines 140-143)** —
  independently re-confirmed by this review at source. Same defect class as the bug this gate
  fixed in `estimate_batch.py`. Must be fixed before any real FP backfill (#646) or every FP row
  produced through that script will still be silently `quali_mass`-biased. Flagged to the survey
  as a triage candidate (`tc1`).

## Workflow Feedback
- **Handoff gaps:** none material. The g5-review handoff was precise and its two named hard
  checks mapped directly onto the actual diff — no rediscovery needed on the wiring itself.
- **Context rediscovered:** the `backfill_estimate_store.py` gap was already flagged by the
  implementer's own result doc, so this review's independent re-confirmation (reading the actual
  source lines) was fast, not a rediscovery from scratch.
- **Instructions improvised around:** none. The engine-drive/Fowler-pass/reach-up mechanics all
  worked as documented for this survey.
- **What would have made this easier:** none — this handoff was well-scoped and its evidence
  claims were all faithfully reproducible; nothing to improve here.

## Return status
`complete`
