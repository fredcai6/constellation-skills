# Triage Recommendation: `checklist_engine.save()` is a non-atomic write, now with a new concurrent writer

## Classification
`performance/resource`

## Source checklist/artifact
- `execute.json` `triage_candidates[3]` (`tc4`, flagged via `flag-candidate --from g1-review`); g1's `IMPLEMENTER_RESULT` and `REVIEW_RESULT`.

## Structural anchor
`scripts/checklist_engine.py` (`save()`, referenced but not modified by this run)

## Cartographer mismatch class
none

## Observations

### Observation 1
- **What's wrong:** `checklist_engine.save()` performs a plain read-modify-write with no observed file locking or atomic-rename semantics. This run's #607 fix (`_parent_lease_heartbeat` in `scripts/run_crew.py`) introduces a new concurrent writer onto a spine JSON file: in the common "shared-spine" dispatch case (no explicit `--spine` given), the parent's background heartbeat thread and the dispatched child crew process now both call `checklist_engine.save()` against the *same* file — the parent every `PARENT_HEARTBEAT_INTERVAL_SECONDS` (300s in production), the child via its own engine verbs during its work.
- **Expected:** either a documented argument that concurrent single-field (`last_heartbeat`) writes are safe under `save()`'s actual write mechanism (e.g. it already writes atomically via a temp-file rename, making last-write-wins safe for this field), or a hardening of `save()` to make concurrent writers genuinely safe.
- **Conditions:** the shared-spine dispatch case specifically (most implementer/reviewer dispatches, since they typically carry no explicit `--spine`) — not the common isolated-worktree case where a child gets its own distinct spine file.
- **Type:** `inferred` — g1's implementer independently surfaced a related symptom while hardening test polling ("a transient same-file read/write race between the test's own poll and the heartbeat thread's non-atomic `checklist_engine.save`", per `g1-implementer-result.md`), and g1's reviewer confirmed by reading `checklist_engine.py`'s `save()` source that it shows no lock/atomic-rename pattern — neither observed an actual data-loss incident from this pattern; the risk is read off the code, not reproduced as a corruption.
- **Rev:** `cleanup/e-crew-tooling` at the commit this run integrated (g1-integrate), base `e36e630b`. `scripts/checklist_engine.py` itself is unmodified by this run.

## Possible fix
Have `checklist_engine.save()` write to a temp file in the same directory and `os.replace()` it into place (a standard atomic-rename pattern), which would make even fully-concurrent writers safe for the whole-file replace, though a genuine field-level race (two writers computing different in-memory deltas from the same read) would still silently drop one writer's change — for `last_heartbeat` specifically that is low-consequence (self-heals on the next tick), but the general pattern deserves an explicit decision either way.

## Open questions
- Does `checklist_engine.save()` already write atomically (temp file + rename) and the "non-atomic" read was itself mistaken? This run's reviewer read the source directly and reported no such pattern, but re-confirming against the actual current `checklist_engine.py` before scoping a fix is worth doing, since the file is fenced and this run did not modify or deeply audit it beyond the specific functions it called.

## Recommended priority
`low`

**Reason:** No observed corruption; the window is narrow at the 300s production interval; the specific field at risk (`last_heartbeat`) self-heals on the very next tick even in the worst case. Worth a deliberate look, not an urgent one.

## Related artifacts
- `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-implementer-result.md`
- `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-reviewer-result.md`

## Disposition
`recommend-and-defer`

**Detail:** `scripts/checklist_engine.py` is explicitly fenced from this run ("do not touch") per `LAUNCH_ORDER.md`'s File Ownership section — any fix belongs to a different lane/run with authority over that file, and filing a new GitHub issue is outside this delegated run's clear authority.

## Issue creation authority
`ask user`
