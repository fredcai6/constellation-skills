# Cartographer Result — #495 fit-robustness reconcile

Date: 2026-06-28
Branch: fix/495-fit-robustness
Cartographer run: post-implementation map reconcile

---

## Map Impact: NONE

No packet, overlay, index, or decision anchor edits required.

### Rationale (Inclusion Rule applied per change)

**`no_speed_stream` typed-skip sentinel** (fit_store.py comment + session_fit.py
exception mapping):
The `FitRecord.fit_status` field is a string with an enumerated set of sentinel
values. The map does not document `FitRecord` fields, parameter lists, or
fit-status sentinel strings — established as below the packet-description boundary
in the 2026-06-28 509-w3 reconcile (#495-cluster / PR #548). The new
`no_speed_stream` value does not cross the Inclusion Rule:
- **Planning**: no commander needs to know this sentinel exists to scope or
  sequence future work.
- **Boundary correctness**: entirely internal to `src/physics/`; no cross-region
  contract is introduced.
- **Rule preservation**: no constraint governs sentinel values.
- **Trust**: covered by unit tests (`test_calibration_robustness.py` A5 class,
  `test_475_validation_breadth.py` sentinel-set update) without map documentation.

**`calibrate_session_hp` empty-stream guard** (preprocessing/trajectory/calibration.py):
A defensive `ValueError("no_speed_stream: ...")` raise added before `tc.min()` on
an empty array. Local crash-prevention guard inside the preprocessing container.
No new cross-region import; no new public symbol. Below packet-description
boundary — the `calibrate_session_hp` function is already documented in
`packets/preprocessing.md` at the function-description level; this guard changes
only its failure mode on degenerate input, which is below the Inclusion Rule
threshold.

**`fit_session_full` early return** (session_fit.py):
Returns `None` when speed stream is empty. Same reasoning: internal guard, no
structural change.

---

## Decision-Pressure Adjudication

### Candidate 1: Enumerated typed-skip reason set as FitRecord store contract

**Verdict: REJECT (below boundary; consistent with #548 precedent)**

The typed-skip reason set (`no_laps`, `no_accel_samples`, `no_speed_stream`) is
a `FitRecord.fit_status` field-value contract. The #548 precedent established that
fit-status sentinel strings are below the packet-description boundary. That
precedent applies here: the full set is now documented in the `fit_store.py` line
34 comment and in the test sentinel sets; it does not need a map anchor because:
- it serves no future planning value (the set is extensible by code inspection),
- it does not define a cross-module boundary (consumers of `FitRecord` already
  read `fit_status` as a string; no routing logic depends on the exact set being
  map-documented),
- it has no authority/consequence/review-trigger structure that a decision anchor
  requires.
Short rationale: captured as code comment + test documentation; not a durable
map anchor.

### Candidate 2: Recover-vs-skip boundary (recoverable iff flying-lap windows; skip iff empty session-wide)

**Verdict: REJECT (purely local crash-prevention policy; not a structural design choice)**

The policy — skip a driver when the session-wide speed stream is empty, recover
(normal calibration path) when streams overlap in flying-lap windows — is a
defensive guard pattern, not an architectural decision that materially governs
current structure. It does not:
- constrain future planning (a future recovery path would read the code, not the
  map),
- cross a module boundary or ownership seam,
- introduce a rule that could be silently violated.
The rationale is obvious from the guard code itself. A decision anchor requires
authority, consequence, and a review trigger; this candidate supplies none of
those. **Reject**: stays as local code/test documentation.

---

## Constraints Re-Verified

### `constraint:physics_region_no_evo_import`

**HOLDS — re-verified on this branch.**

Checked all three modified files:
- `src/physics/session_fit.py`: no import of `evo_predictor`, `latent_power`, or
  `compound_prior`.
- `src/physics/fit_store.py`: comment-only change; no import change.
- `src/preprocessing/trajectory/calibration.py`: no import of `evo_predictor`,
  `latent_power`, or `compound_prior`.

Select-String on all three returned empty (no matches). Constraint holds.

### No new module / edge / overlay

**Confirmed.**

- No new `src/` file created.
- No new import edges introduced (the only modified `import` path is the existing
  `calibration` module; `session_fit` already imports it).
- No new overlay node or edge.
- No new decision anchor file.

### `check_arch_map.py` green

Run: `py scripts/check_arch_map.py`
Result: `Parsed 39 catalog nodes, 18 packets, 12 overlay nodes. OK: architecture
map is consistent.`

Map counts unchanged from last reconcile (2026-06-28 #546/#549 close): 39/18/12.

---

## Triage Candidates

None. This change is fully below the map boundary; no future structural work is
implied by the robustness fix itself.

---

## Summary

The #495 fit-robustness change is a clean local fix: one new typed-skip sentinel
(`no_speed_stream`), two early-exit guards (session_fit.fit_driver and
fit_session_full), one typed-ValueError raise (calibration.py windows branch),
test coverage, and a comment update. All changes are below the packet-description
boundary established by the #548 precedent. Both decision candidates (typed-skip
reason set, recover-vs-skip boundary) are rejected as durable anchors — they stay
as code/test documentation. The `constraint:physics_region_no_evo_import` is
re-verified clean. The map requires no edits.
