Surfaced by #495 (physics fit robustness). The per-session fit store
`data/physics_fits.db` is the **pre-fix baseline**: built 2026-06-23 (engine_sha
`6a051ff`), before PR #548 and before #495's `no_speed_stream` fix. It still holds
the 18 `error` + 1 `no_laps` rows that are now resolved.

**Current truth (validated in #495):** re-fitting 2023-Q on current code gives
**438 ok / 1 no_laps / 1 no_speed_stream** (the lone remaining typed-skip is Saudi
Arabia DEV, empty session-wide speed stream). The store on disk does not reflect
this — #495's G3 validation deliberately did not overwrite the baseline.

**Task:** rebuild the fit store on current code so downstream cross-session pooling
(#492 P2) consumes current fits, not stale ones.

- `py scripts/build_physics_fit_store.py --seasons 2023 --sessions Q --force`
  (and/or the broader multi-season set the pool needs).
- Verify status counts match the #495 validation note
  (`reports/physics/495_fit_robustness_validation.md`).
- The store is untracked/regenerable (not committed); repoint consumers only if a
  path changes.

**Non-goals:** no fit-method change; no schema change.

**Acceptance criteria:**
- [ ] Store rebuilt on current code; status counts match the #495 validation note.
- [ ] No `error` rows from the resolved interleaved-n=0 / NoneType / empty-speed
      patterns remain.

Refs: #495, #492, `reports/physics/495_fit_robustness_validation.md`,
`scripts/build_physics_fit_store.py`.
