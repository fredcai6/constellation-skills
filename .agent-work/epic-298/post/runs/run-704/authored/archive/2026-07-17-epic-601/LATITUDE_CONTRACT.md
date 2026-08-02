# Latitude Contract - epic 601, bite 3

Confirmed from the owner's 2026-07-14 continuation instruction: "keep going" after PR #619/#616 was presented at the prior bite checkpoint.

## Intent and success shape

Merge the validated #616 reproducibility prerequisite, then take the next dependency-ready bite: #617, which persists verbatim classification status so DNF opportunity becomes identifiable before #389. Success is a bounded, independently reviewed #617 branch with schema/collector/read-path coverage, a measured 2022-2026 status-vocabulary and coverage audit, and a ready PR, or an honestly scoped null/blocker that names what was and was not measured.

## Checkpoint protocol

Cleared through merge and verified closure of #616, then local investigation, design alternatives, implementation, tests, data backfill/audit evidence, commit, push, and PR creation for #617. Stop and present before merging #617, closing #617, starting #389, destructive cleanup, or committing generated database artifacts unless separately authorized.

## Delegated decision classes

- Diagnosis, test shape, migration approach, collector/upsert/read API details within #617 acceptance criteria.
- Selection among non-architectural status-persistence approaches after design-it-twice comparison.
- Test commands, documentation/map updates, and issue-scoped refactors needed for strict fail-fast inputs and lossless status preservation.
- Read-only or disposable backfill/audit runs over 2022-2026 data; generated database changes remain evidence, not commit payload, unless explicitly approved.
- Commit, push, and opening/updating a PR for the #617 branch.

## Surfaced decision classes

- Any load-bearing seam or architecture-boundary change after alternatives are compared.
- Any lossy normalization or reliability/DNF taxonomy that collapses unknown source statuses.
- Scope expansion into #389 modeling, tuning, or sampler changes.
- Committing large/generated database artifacts, merge, issue close/reopen, file deletion, or destructive worktree/branch cleanup.
- Any decision not fitting a delegated class.

## Float-up routing

The delegated Commander returns genuine gaps to the Admiral. The Admiral adjudicates inside the delegated classes and surfaces all other decisions to the owner.

## Communications and budget

Concise milestone updates. One high-reasoning Commander owns #617 and may dispatch implementation/review crews under its spine. Prefer schema/API unit tests first, then collector integration and a bounded real-data audit. No explicit monetary or token budget was set.

## Pre-rulings

- #617 is truth enablement for #389, not the DNF model itself.
- Preserve FastF1 classification status verbatim; interpretation belongs at an explicit consumer boundary and unknown statuses remain visible.
- Preserve existing ordinal position semantics and existing database-as-canonical-source policy.
- Backfill evidence must report season/round coverage, nulls, vocabulary, duplicates, and provenance; it must not infer DNF capacity from lap-completion proxies.
- The dirty main checkout and owner artifacts are out of scope. Issue work stays in an explicit worktree based on current `origin/main`.
- An honest null is acceptable if upstream status is unavailable for a scoped subset; report exact missingness rather than inventing a fallback.

## Expiry

Expires when the #617 PR is presented at the next checkpoint, when a surfaced decision is reached, when `origin/main` changes underneath active work in a relevant way, or at the end of this Admiral bite - whichever comes first.
