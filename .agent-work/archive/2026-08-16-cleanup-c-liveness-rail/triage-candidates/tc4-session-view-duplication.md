# Triage Recommendation: minor duplicated fetch-and-validate shape between `session_view` and `session_view_provenance`

## Classification
cleanup

## Source checklist/artifact
- execute.json triage_candidates tc4 (flagged from g2-review's Fowler code-smell pass)
- `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g2-review-result.md`

## Structural anchor
`scripts/hooks/spine_rail.py` — `session_view()` (`:515`-ish after this lane's change), `session_view_provenance()` (new, adjacent)

## Cartographer mismatch class
none

## Desired behavior
- **Desired:** `session_view` and `session_view_provenance` share the entry-fetch-and-type-check step (`entries = binding.get(key); if not isinstance(entries, dict): continue`), not just the key-list (`_session_keys`), so a future change to that validation cannot land in one function and not the other.
- **Today instead:** both functions independently call `_session_keys(binding, sid)` (the shared seam this lane added, preventing the two from disagreeing about WHICH paths are visible) but each re-implements its own `entries = binding.get(key)` / `isinstance` guard before doing its own thing with `entries` (`session_view` merges the dict; `session_view_provenance` records the key per path). A small, low-risk duplication, not a correctness gap — flagged by the reviewer's Fowler pass as non-blocking.
- **Type:** `measured` — read both function bodies in `scripts/hooks/spine_rail.py` after commit `915daefa`.
- **Rev:** this lane's head, `915daefa` (and unaffected by the later map-only commit `590bf44d`).

## Possible fix
Extract a small internal generator, e.g. `_session_entries(binding, sid) -> Iterator[tuple[str, dict]]` yielding `(key, entries)` pairs already fetched and type-checked, and have both `session_view` and `session_view_provenance` iterate it. Low risk since both callers' current behavior is already pinned by tests (`session_view`'s return shape, `session_view_provenance`'s owner-mapping).

## Recommended priority
low

**Reason:** purely a duplication/locality nit inside a change that already passed independent review with two adversarial mutation tests; no observed or suspected defect.

## Related artifacts
- `scripts/hooks/spine_rail.py` (commit `915daefa`)
- `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g2-review-result.md`

## Disposition
`recommend-and-defer`

**Detail:** filing authority is unclear this run — not named in Inherited Latitude, and this is sub-issue-scale cleanup inside an already-shipped fix, better suited to a future simplify pass than a standalone issue.

## Issue creation authority
`issue-ready only`
