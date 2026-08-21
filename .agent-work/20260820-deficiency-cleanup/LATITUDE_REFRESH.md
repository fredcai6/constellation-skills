# Latitude refresh — 2026-08-21

The Wave 2 contract expired at the architecture checkpoint. This replaces it.

## Granted by Tommy, 2026-08-21

- Implement **A** (display and message fixes) and **B** (two narrow behavior fixes).
- Cleanup, commit, push, and lease extension are cleared.
- "In a good spot, let's keep working."

## What that authorizes

| Class | Authority |
|---|---|
| Implement A and B on a feature branch | Delegated |
| Tests, evidence, independent review | Delegated |
| Commit locally; merge to the epic integration branch | Delegated |
| Push branches | Delegated (newly granted) |
| Worktree and branch cleanup after merge | Delegated (newly granted) |
| Lease extension / heartbeat | Delegated (newly granted) |
| Merge to `main` | **Surfaced** — not granted here |
| Opening PRs, closing/re-scoping issues, filing new issues | **Surfaced** — not granted here |
| Option C, or any architecture beyond A and B | **Surfaced** — C is retired as dominated |
| The R9/R10 defect | **Surfaced** — write-up complete, filing needs authorization |

## Standing criterion, unchanged

No bad actors. The only adversary is an honest agent about to make a mistake.
Ease of use is the success criterion. Added machinery is a cost.

## Scope fence for this batch

**A** — remove `"current"` from `RAIL_VERBS`; archive banner and rail suppression;
`HELD` rather than `active`; `next (for the holder):`; staleness in
`_scan_active_spine`; rewrite `require_session`'s refusal text.

**B** — exempt `waive` from the session gate **without** touching `MUTATING_VERBS`;
make `--parent` required.

Anything beyond those eight items is out of scope and floats up.
