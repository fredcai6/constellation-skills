# Triage Recommendations — #495 fit-robustness run

## OUTCOME (human-approved 2026-06-28)
- **tc1 → FILED as #559** (verified OPEN) — rebuild fit store on post-#548/#495 code.
- **tc2 → FILED as #560** (verified OPEN) — min-flying-laps/sample floor investigation.
- **tc3 → NOT filed** (human declined): unreachable cosmetic naming nit
  (`no_speed_stream` reused for the position-empty defense-in-depth branch). Recorded
  here only; revisit only if the position-empty branch ever becomes reachable.


Three candidates surfaced during the run. Authority (ORCHESTRATOR_CONTEXT): "Create
issues — Autonomous for non-trivial tasks", but per the Commander spine, the human
approves filing first.

---

## Triage Recommendation: Rebuild the per-session fit store on post-#548/#495 code

### Classification
cleanup | tooling (stale generated artifact)

### Source checklist/artifact
g1-integrate triage candidate tc1; g1 review; g3 validation note.

### Structural anchor
`struct:physics` | `data/physics_fits.db` (standalone artifact store) | `scripts/build_physics_fit_store.py`

### Problem
The committed-evidence baseline `data/physics_fits.db` was built 2026-06-23, **before
PR #548 and before #495's `no_speed_stream` fix**. It holds 18 `error` + 1 `no_laps`
rows that are now resolved (438 ok / 1 no_laps / 1 no_speed_stream on current code).

### Current truth
The OLD store is stale (pre-fix). #495's G3 validated the fix on re-fits but did NOT
rebuild/replace the store (deliberately — it's the before baseline; G3 used a
separate path / in-memory re-fits).

### Desired/future concern
Rebuild the 2023-Q (and ideally the broader multi-season) fit store on current code
so downstream cross-session pooling (#492 P2) consumes current fits, not stale ones.

### Evidence
- `reports/physics/495_fit_robustness_validation.md` (old→new counts).
- `data/physics_fits.db` mtime 2026-06-23 / engine_sha 6a051ff (pre-#548).

### Impact
P2 pooling quality depends on the store reflecting current fits. Leaving it stale
risks pooling on superseded params.

### Suggested scope
`py scripts/build_physics_fit_store.py --seasons 2023 --sessions Q --force` (and/or
the multi-season set), verify counts, repoint consumers if needed. Note the store is
untracked/regenerable (not committed).

### Non-goals
No fit-method change; no schema change.

### Acceptance criteria
- [ ] Store rebuilt on current code; status counts match the validation note.
- [ ] No `error` rows from the resolved patterns remain.

### Recommended priority
medium — **Reason:** unblocks/cleans P2 pooling input; cheap; no code.

### Issue creation authority
ask user

---

## Triage Recommendation: Minimum-flying-laps / sample floor for fit acceptance

### Classification
research hardening | feature (fit-quality policy)

### Source checklist/artifact
g1-integrate triage candidate tc2; g1 review (thin fits pass); decide-fix (human
deferred it out of #495 scope).

### Structural anchor
`struct:physics` | `src/physics/session_fit.py` (fit acceptance) | none

### Problem
Post-#548, very sparse fits pass as `ok` (e.g. Azerbaijan GAS: 1 flying lap, 412
samples). The human's "no second-class fits in the pool" intent suggests a possible
quality floor below which a fit should be a typed-skip rather than `ok`.

### Current truth
No minimum-flying-laps/sample floor exists; any successful HP fit returns `ok`
regardless of thinness. #495 deliberately did NOT add a floor (out of scope —
crash→typed-skip only).

### Desired/future concern
Investigate whether a min-lap/sample floor improves pool quality **without** dropping
legitimate sparse-track fits — the P0 evidence (`reports/physics/P0_evidence_findings.md`)
shows flowing tracks legitimately yield few braking events, so a blanket floor risks
discarding real data.

### Evidence
- g1 review: Azerbaijan GAS n_fly=1 returns ok.
- P0 findings: braking identifiability tracks circuit demand (sparse ≠ broken).

### Impact
Affects cross-session pool quality and the "no second-class fits" bar.

### Suggested scope
Measure fit quality vs flying-lap count; decide whether a floor (and what kind —
hard skip vs a confidence/trust flag) is warranted; if yes, implement as a typed
reason or a trust-profile field.

### Non-goals
Not a crash fix (that's #495). Do not add a blanket floor without evidence it doesn't
drop legitimate sparse fits.

### Acceptance criteria
- [ ] Measured relationship between thinness and fit quality.
- [ ] Decision (with evidence) on whether/what floor; implemented or explicitly declined.

### Recommended priority
medium — **Reason:** quality concern the human raised; needs evidence, not a quick fix.

### Issue creation authority
ask user

---

## Triage Recommendation: `no_speed_stream` naming for the position-empty guard branch

### Classification
cleanup

### Source checklist/artifact
g2-integrate triage candidate tc3; g2 review (naming nit).

### Structural anchor
`struct:preprocessing` | `src/preprocessing/trajectory/calibration.py` (`calibrate_session_hp` windows= branch) | none

### Problem
The defense-in-depth guard raises `ValueError("no_speed_stream: empty position
stream …")` for the `len(tp) < 1` (position-empty) case — semantically a
position-empty condition labeled with the speed-named reason.

### Current truth
Low reachability: `fit_driver`'s early guard fires on empty `spd_d["t"]` before
`calibrate_session_hp` is reached, so the position-empty branch is essentially
unreachable via the production path. Routes to the same clean-null handling.

### Desired/future concern
If a position-empty case ever becomes reachable, introduce a distinct
`no_position_stream` reason (or relabel the message) for honest accounting.

### Evidence
- g2 review finding; `calibration.py` windows= branch.

### Impact
Cosmetic/taxonomy honesty only; no current functional impact.

### Suggested scope
Either relabel the position-empty message, or add a `no_position_stream` reason if a
reachable case appears.

### Non-goals
Not worth a code change now (unreachable).

### Acceptance criteria
- [ ] Position-empty case has an honest reason name (or documented as unreachable).

### Recommended priority
low — **Reason:** unreachable in production; cosmetic.

### Issue creation authority
ask user
