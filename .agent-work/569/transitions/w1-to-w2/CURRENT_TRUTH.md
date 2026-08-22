## Current planning truth — epic 569

**Intent.** Make a green qualitative gate mean something by telling the agent *what would count* at
plan time, rather than telling it at attest time that it got it wrong. The boundary that must not be
crossed: this epic must not add machinery that is itself unwired.

### Wave 1 — complete, merged

- **#345 / #444 / #368** — census of all 26 check-shaped scripts (17 live, 8 unwired, 1 dead),
  registration lint and vocabulary rule shipped blocking with negative self-tests, one dead script
  deleted, a live doc/code drift found and fixed. PR #644 at `4cbd2cc9`.
- **#371** — list-valued `match` means membership at both engine sites, scalar behaviour unchanged;
  a non-dict `match` that previously crashed is now a clean refusal. PR #645 at `04888e4a`.

### Current wave (launching)

**Objective.** Make the declared basis actually reach the executor on the path that runs, give every
override one auditable home, and stop the map index going stale by construction.

- **`w2-basis`** (#556) — `because` in the shipped hand-written templates, **rendered by the engine
  at the active step**, with `attest` requiring a resolvable locator. A basis that is neither
  rendered nor required is decorative and is a failure, not a partial win.
- **`w2-ledger`** (#557) — one engine-written, append-only override ledger that no CLI verb can
  forge, read at closeout. Includes the `waive()` hardcoded `produced_by` and the never-compared
  `override_policy.authority`, deliberately left by `244665ee` for this issue.
- **`w2-reindex`** — a pre-commit hook that regenerates and stages `map/INDEX.md`, wired into
  `install_constellation.py`, with the freshness test left exactly as strong as it is.

### Nonbinding forecast

1. Plan-freeze validation + journal fidelity (#518 #524 #381 #382 #459 #515 #390).
2. Reviewer machinery (#375 #358 #363 #259 #223 #388 #376 #221).

The contract expires at the wave-2 checkpoint, where #558's review-level doctrine is settled with the
human before wave 3 dispatches.

### Parked, with measurements attached

- **The spec-to-template migration stalled at 2 of 19 roles**, and the two specs that exist have
  drifted from their shipped templates. Ruled out of 569 by the human; recorded as
  `episodes/active/569-001.md`.
- **No automated defence against a PR that reds `main`** — measured, not theorised.
