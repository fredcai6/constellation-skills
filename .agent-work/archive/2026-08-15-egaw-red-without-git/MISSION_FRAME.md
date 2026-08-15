# Mission Frame

Shrunk per the template's own escape: trivial, local, mechanical, single-file test change. The repo map
is DEGRADED-UNPARSEABLE (`map/ids.jsonl` empty; `map/INDEX.md` an unfilled template — recorded at the
context gate, receipt `.agent-work/egaw-red-without-git/map-orientation.json`). The context gate's
declared substitute for this degraded reading is `README.md` (see that receipt's `substitutes` list),
cited below so this frame is checked against that same committed declaration rather than a same-breath
claim. No map anchor ids are cited — none resolve in a degraded reading, and asserting one anyway would
be worse than omitting it.

## Intent
Per LAUNCH_ORDER.md and the project doctrine `README.md` sets out for this corpus (test-led change,
machine-checkable evidence, small bounded gates): remove the one remaining git dependency from
`tests/test_episode_observation_guard_at_write.py`'s RED test, while preserving the property it proves —
that the write-time guard added by PR #592 is what causes the rejection, not merely present. Approach (a)
from the launch order: monkeypatch the guard seam to a no-op on the current writer, assert the delta
writes cleanly; restore it, assert the identical delta is rejected. Same code path, same process, no git,
no hardcoded commit SHA.

## Affected Capabilities
The RED/GREEN pair inside one test class. Nothing else in the suite changes.

## Governing Constraints / Assumptions
LAUNCH_ORDER.md: do not delete the RED; do not `pytest.skip` it (the repo's skip-guard fails the build on
any undocumented skip); only the one test file and this work area are mine to touch; do not touch
`.github/workflows/ci.yml`, `scripts/apply_episode_delta.py`, `scripts/verify_episode_observations.py`,
`scripts/install_constellation.py`, or the grandfathered-exception decision.

## Decision Anchors & Decision Pressure
The choice of approach (a) over (b) is ratified in LAUNCH_ORDER.md itself ("(a) is the closer match to a
true RED/GREEN pair and I lean toward it") — settled by the Admiral who issued this order, not a
decision this run makes freely. No further decision pressure: the scope is one test method plus its
now-dead git-only helpers.

## Claims / Evidence Surfaces
Attribution: the rejection the GREEN test observes is caused by this change's guard call, not merely
present — verified by neutralizing the guard call and observing the write succeed, then restoring it and
observing the identical delta fail. No-git: after the change, nothing in the test file imports
`subprocess`, calls `git`, or names the commit SHA `2c46cab8` — verified by grep.

## Map Confidence / Staleness / Disputes
Repo-wide, `map/ids.jsonl` is empty and `map/INDEX.md` has no citable anchor id — pre-existing, unrelated
to this fix. Flagged as a triage candidate at the triage gate; not blocking this bounded change.

## Out of Scope
`.github/workflows/ci.yml` fetch-depth (explicitly forbidden by LAUNCH_ORDER.md); any change to the
production guard or its call sites; the grandfathered-record exception list.
