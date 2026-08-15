# Plan convergence — #441

## Panel choice

Two parallel candidates were used because the human-set launch order already
settled the transaction boundary, active-retention policy, identity owner,
claim contract, exclusions, and four-file ownership. The remaining planning
choice was bounded seam shape, not open architecture. A three-lens panel would
have repeated settled constraints rather than expose another viable boundary.

Constraints compared:

- smallest-diff
- best-seam-placement / most-testable

## Recommendation

Use the best-seam candidate's single private transaction callback, combined
with the smallest-diff candidate's strict four-file scope and exact production
writer routing. The transaction owns lock acquisition, locked reload, safe
reap, one mutation callback, unique-temp replace, and release. Claim, release,
and SessionStart remain thin callers. Gauge delegates identity validation to
the rail and never becomes a store owner.

## Comparison

- Depth: both hide the complete serialization invariant behind one call. The
  hybrid explicitly keeps release resolution inside the locked snapshot.
- Locality: both touch two production modules and their two focused suites.
- Seam placement: the shared rail store seam wins over per-writer locking,
  because a future writer has one canonical transaction path.
- Testability: use spawned production handlers, deterministic unlocked
  post-load synchronization, valid-final-JSON and all-entries assertions,
  distinct-temp and contention controls, plus policy matrices.

## Untaken roads

- Per-writer locks: rejected because they duplicate the transaction invariant
  and make SessionStart drift likely.
- Lock only around replacement: rejected because it cannot prevent stale
  snapshots from losing updates.
- Stale lockfile / PID ownership: excluded by the crash-released advisory-lock
  ruling and the actor/PID stop condition.
- Global or historical sweep: excluded by the no-backfill ruling; safe reap
  happens only inside a new writer transaction.
- More than one execute gate: rejected because production changes overlap the
  same store seam and splitting them would create a knowingly inconsistent
  intermediate boundary.

## Frozen gate shape

One crew gate: implement the complete transaction/identity/validation/reaper
contract with test-led red/green and mutation control; obtain a fresh
independent review; integrate only after focused and full non-Windows tests.
