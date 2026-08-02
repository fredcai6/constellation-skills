# Review Result

## Assigned Gate
`g2` (execute.json) — "FP mass distribution + per-lap latent" — reviewer survey at
`.agent-work/513-fp-fits/g2-review/review.json` (engine-driven, session
`reviewer-513-g2-1784469901`, consolidated `APPROVE` after a rework-verification pass; original
pass consolidated `BLOCK`, both preserved in the survey for audit — see Rework Verification below).

## Result
`APPROVE`

## Handoff compliance
Met on every close criterion, independently reproduced (not just trusted):
- `fp_mass(season, *, fuel_kg=None, fuel_sigma_kg=None, team=None) -> FpMass` — `FpMass` is a
  `NamedTuple(mass_kg: float, sigma_kg: float)`; code path always constructs and returns an
  `FpMass`, never a scalar. **This is the load-bearing contract and it holds.**
- Invariant `SEASON_BASE_KG[season] < fp_mass(...).mass_kg < quali_mass(season) + MAX_FUEL_KG`
  holds across all known seasons; push-lap mass < long-run-lap mass at matched `lap_in_stint` holds
  (own repro: push@3=809.40 < long_run@5=850.80, and at matched lap_in_stint=3
  push=809.40 < long_run=854.40).
- `run_purpose` is genuinely EMERGENT: `classify_run_purpose`'s signature is
  `(lap_time_s, session_best_s, *, is_pit_out, is_pit_in, lap_in_stint, stint_length)` — no
  `session_type`/session-label parameter exists, and `extract_fp_lap_latent`'s call site does not
  pass one (grep-verified: `session_type` is used only to resolve `session_id`, per its own
  docstring, and never reaches the classifier).
- `compound` is read directly from `row["compound"]` (grep-verified — no inference/derivation
  logic anywhere in the file).
- All 6 new tunable constants (`NOMINAL_FP_FUEL_KG`, `FP_FUEL_INTERCEPT_SIGMA_KG`,
  `PUSH_MARGIN_FRAC`, `START_FUEL_PUSH_KG`, `START_FUEL_LONGRUN_KG`, `FP_FUEL_RESERVE_KG`) are
  named at module scope with docstrings explicitly flagging them as calibration placeholders /
  decision-candidates.
- `FpLapLatent`'s field order matches the handoff's literal spec exactly.

## Scope drift
None. Exactly the allowed-scope files were touched: `src/physics/mass_model.py` (additive diff
only — `quali_mass`/`race_mass`/`race_mass_sigma` bodies are byte-identical, confirmed via
`git diff`), `tests/unit/physics/test_mass_model.py` (extended), new
`src/physics/layer2/fp_lap_latent.py`, new `tests/unit/physics/test_fp_lap_latent.py`. `git status`
confirms no other files touched. Grepped `fp_mass`/`fp_lap_latent`/`FpLapLatent`/
`extract_fp_lap_latent` across all of `src/` — zero references outside these two files:
`session_estimator.py`, `estimate_store.py`, and all views are confirmed untouched, and `fp_mass`
is not wired into any fitter. No `data/*.db` read anywhere (test fixture is a `tmp_path` +
synthetic `sqlite3` schema).

## Evidence verdict
All required evidence independently reproduced, matching the implementer's claims:
1. `py -m pytest tests/unit/physics/test_mass_model.py tests/unit/physics/test_fp_lap_latent.py -q`
   → **155 passed** (105 in `test_mass_model.py`, 50 in `test_fp_lap_latent.py`, up from 151/46
   before rework — the +4 delta matches the new `TestExtractFpLapLatentMissingTyreLife` class,
   confirmed via `--collect-only` and a targeted `-k tyre_life` run showing all 4 matching tests
   pass).
2. Value table (2023, push vs long-run) — reran `fp_mass`/`fuel_kg_est` directly:
   `SEASON_BASE_KG[2023]=798.0`, `quali_mass(2023)=808.0`, push@1=813.00, push@3=809.40,
   long_run@1=858.00, long_run@5=850.80, `sigma_kg=15.0` throughout — identical to the claimed
   table (unaffected by the rework fix).
3. `py -m src.utils.simplification_limits --paths src/physics/mass_model.py
   src/physics/layer2/fp_lap_latent.py` → `PASS (2 files checked)`.
4. `git status --short data/` → empty (independently confirmed, both before and after rework).

## Code/doc quality
The one project-rule violation found in the initial pass is fixed and independently re-verified
(see Rework Verification below). Everything else checked clean: exception messages name field +
expectation + actual value; no hidden fallback for the load-bearing paths (fuel/run_purpose/compound
are all documented and tested); `DEFAULT_BURN_PER_LAP_KG` is reused, not redefined; all new
constants are module-scope only, no mutable module state; the season-DB read pattern genuinely
mirrors `session_race.py`'s `_get_session_id`/`_ro_uri` read-only-URI convention.

**Fowler code-smell pass** (`.agent-work/513-fp-fits/g2-review/fowler_pass.json`,
`verify_fowler_pass.py` exit 0): 10/12 baseline smells absent. Two overridden with a logged repo
standard + reason, not flagged as defects (duplicated-code — `_get_session_id`/`_ro_uri` matches an
established repo pattern already present in 4 other physics modules; speculative-generality —
`fp_mass`'s no-op `team=` mirrors `quali_mass`/`race_mass`'s existing convention). Unaffected by
the rework (the fix is a one-line change plus a type annotation and docstring, no new smell
surface).

## Map impact verdict
- **Evidence supports claimed change:** Yes.
- **Constraints not violated:** Yes — `constraint:physics_region_no_evo_import` honored; the "FP
  starting fuel is UNOBSERVABLE" assumption honored end-to-end.
- **Notes match the diff:** Yes.
- **Decision candidates surfaced:** Yes.
- **Durable context routed:** Yes — the implementer's out-of-scope triage candidate
  (`session_race.py._is_clean`'s dead-code NaN-vs-`None` trap, allegedly mirrored by
  `tyre_supplant.py`) was independently re-verified as accurate and flagged in this survey (`tc1`)
  for Cartographer/Triage.

## Reconciliation check
None. No divergence from the recorded architecture requiring Commander reconciliation beyond the
routed triage candidate above.

## Rework Verification (2026-07-19, second pass)
The initial review (below, preserved for audit) found one genuine BLOCK: `fp_lap_latent.py`
silently zero-filled a missing/NULL `tyre_life` to `0`, a real physical value (fresh tyre),
violating CREW_CONTEXT.md's named missingness-policy rule. ShipI-513 reported a fix; independently
re-verified in this pass (survey item `r7-rework-verify`, appended to the engine checklist rather
than editing the original `r4-quality` fail — the original finding is retained verbatim for audit):

- `src/physics/layer2/fp_lap_latent.py:361` now reads
  `tyre_life=int(row["tyre_life"]) if pd.notna(row["tyre_life"]) else None` (was `else 0`).
- `FpLapLatent.tyre_life` type annotation changed to `Optional[int]`; docstring updated to state
  the explicit-unknown discipline (missingness carried as `None`, never guessed as `0`).
- New `TestExtractFpLapLatentMissingTyreLife` class (3 tests) exercises the previously-untested
  NULL path: `test_null_tyre_life_yields_none_not_zero`, `test_null_tyre_life_is_not_the_integer_zero`,
  `test_real_tyre_life_still_populated`. All pass.
- Full suite reproduced green: 155/155. `git status --short data/` still empty.
- All 4 owner-named BLOCK triggers re-checked and still clean (no regression).

**track_status disposition:** the lower-severity `track_status` `None -> ""` fallback (unchanged,
`fp_lap_latent.py:368`) was never itself a blocker in the original finding — it was already
recorded as a non-blocking out-of-scope observation, on the rationale that an empty string cannot
be mistaken for a real status value the way `tyre_life=0` could be mistaken for a real fresh-tyre
reading. Ship I (gate owner) formally accepts it as-is with a triage candidate logged. Concur — this
is a reasonable, non-blocking disposition consistent with the original severity assessment.

**Consolidation:** the survey's original `r4-quality` fail is retained unedited; a new item
(`r7-rework-verify`) records the fix's independent verification; `consolidate --verdict APPROVE
--override-reason ...` documents why APPROVE is warranted despite the historical fail (full
override reason logged in the engine checklist JSON).

## Blockers
- None remaining. (Original blocker — tyre_life silent zero-fill — fixed and independently
  re-verified above.)

## Out-of-scope observations
- `session_race.py._is_clean` (dead code within that module) uses `row["pit_in_time"] is None` /
  `row["pit_out_time"] is None` directly on a float64-typed DataFrame column — the same trap this
  gate's own TDD RED caught and fixed in `fp_lap_latent.py`. `tyre_supplant.py` explicitly claims to
  mirror `_is_clean`; worth a dedicated triage issue/Cartographer-Scout pass. (Flagged as triage
  candidate `tc1` in the engine survey.)
- `track_status` `None -> ""` fallback: accepted-as-is by the gate owner with a triage candidate
  logged (see Rework Verification above). Not blocking.

## Workflow Feedback
- **Handoff gaps:** none material across either pass.
- **Context rediscovered:** confirming the `_get_session_id`/`_ro_uri` duplication was pre-existing
  repo convention (not a newly-introduced smell) required an independent grep across
  `src/physics/`.
- **Instructions improvised around:** the survey checklist type has no `reopen` verb (that's
  gated-only — `REFUSED: reopen applies to gated checklists` when attempted). For the rework
  re-verification I used `append` to add a new sibling item (`r7-rework-verify`) rather than
  overwriting `r4-quality`'s original fail, then `consolidate --override-reason` to APPROVE despite
  the retained historical fail — this preserves the full audit trail (the original defect is never
  erased) while still producing a clean final verdict. This seems like the right pattern for a
  survey-type rework re-review in general; worth documenting in the reviewer skill/engine reference
  so future rework passes don't have to rediscover it.
- **What would have made this easier:** an explicit "rework re-verification" pattern documented in
  `references/checklist-engine.md` for survey types (mirroring the gated `reopen` cascade
  semantics) would have saved the one failed `reopen` attempt.

## Return status
`complete`

---

## Appendix: original review pass (2026-07-19, first pass — superseded above)

Preserved verbatim for audit.

### Result (original)
`BLOCK`

### Blockers (original)
- **[BLOCK, medium severity] Missingness silently zero-filled without a named policy —
  `src/physics/layer2/fp_lap_latent.py`, `extract_fp_lap_latent` (around the `FpLapLatent(...)`
  construction, `tyre_life=int(row["tyre_life"]) if pd.notna(row["tyre_life"]) else 0`).**
  Defect: a NULL/missing `lap_times.tyre_life` is silently mapped to `0`, which is a real physical
  value (a genuinely fresh tyre — confirmed by `session_race.py`'s own `tyre_life` docstring
  precedent, which shows real stints legitimately starting at non-zero values like 4). This is the
  exact anti-pattern CREW_CONTEXT.md's Data Semantics section and its literal Review Blocker list
  name: *"Missingness is imputed inline without a named/configured policy."* Not one of the 4
  explicit owner-named BLOCK triggers — all 4 of those were clean. But it was a genuine,
  independently-verified, project-rule violation, and the path was untested (the fixture never set
  `tyre_life` NULL). **RESOLVED — see Rework Verification above.**

### Out-of-scope observations (original)
- `session_race.py._is_clean` NaN/`None` trap — same as above, carried forward.
- `track_status` `None -> ""` fallback — same inline-imputation pattern, lower risk/severity, not
  blocking. **Disposition: accepted-as-is by gate owner — see Rework Verification above.**
