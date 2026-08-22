# Design-it-twice Brief: the unified override ledger's schema/seam/write-discipline

## The one thing being designed twice

The gate plan for issue #557 wave 2 ("w2-ledger"): where the unified
engine-written override ledger physically lives (key name, entry schema), how
`waive()`'s two #503 defects get fixed, and where closeout renders it (#504).

## Count and panel — a surfaced choice

N=2, single pair, not a panel. This is a fairly-easy call: the mission fences
the surface tightly (waive/forced-claim-release/trip-ledger/consolidate/amend
authority only, no attest/condition surface, no spec migration), the proven
model (`_append_trip_entry` at the `dispatch()` chokepoint) already exists to
imitate, and the two live design questions (reuse `trip_ledger`'s name vs.
rename; where closeout reads it) are answerable by direct comparison of two
candidates rather than needing a wider panel to surface structure.

## The constraints (one per agent, each distinct and named)

- **smallest-diff** — minimize code touched and concepts introduced; reuse
  `trip_ledger` verbatim as the unified home, widen `_append_trip_entry` in
  place.
- **best-seam-placement** — optimize for the seam a fresh design would choose
  (a correctly-named `override_ledger` with a `kind` discriminant), even at
  higher diff cost, over the cheapest-to-reach seam.

## Compared on

- **Depth** — smallest-diff is shallow by design (one-token fixes, widened
  signatures, zero new top-level keys) and explicitly declines to plumb
  closeout visibility into the episode-capture schema, calling that a
  deliberate scope stop. best-seam-placement goes deeper: it traces the full
  #503 defect chain the same way, but additionally resolves two structural
  questions the mission poses without naming (what happens to `amend`'s
  chokepoint-adjacent write; where closeout visibility should actually attach
  given nothing today auto-composes a PR body) rather than leaving them
  implicit.
- **Locality** — smallest-diff keeps every touch inside `dispatch()`'s body
  and one-line fixes elsewhere; genuinely the smaller diff. best-seam-placement
  touches two existing selectors' read source and `episode_capture.py`'s
  `mechanical_fields()` — wider, but each touch point stays narrow (one
  function's read source, one function's write call site).
- **Seam placement** — smallest-diff reuses `dispatch()`'s existing branches
  verbatim (the proven seam) but leaves the container named `trip_ledger` even
  once it holds non-trip entries — a real naming leak a future grep would hit.
  best-seam-placement's rename to `override_ledger` with `kind` as
  discriminant is the more honest name for what the container becomes, with a
  migration contract (single merge-reading function, never rewriting archived
  JSON) that costs a defined amount of code, not an open-ended one.
- **Testability** — both candidates independently converged on the SAME
  strongest test pattern: call the verb function directly (bypassing
  `dispatch()`) and assert the ledger did not move, then call it through
  `dispatch()` and assert it did. This is strong agreement between two blind
  candidates, and is adopted verbatim regardless of which candidate wins.

## Framing block (for the record — presented after the fact, since this is a
delegated run with no human to reason in parallel; kept per the brief's
contract for audit completeness)

- **Constraints in play:** smallest-diff vs. best-seam-placement, as above.
- **Dependencies:** both candidates hold fixed the dispatch-chokepoint
  discipline, the report-only shape for the new authority-mismatch check, and
  the #259/consolidate exclusion — none of that was in contention.
- **Illustrative sketch (not a proposal):** "just add three new top-level
  lists, one per path" was the naive third option neither candidate chose —
  both independently rejected it as the leaky-abstraction case worth avoiding.

## Output — recommendation

**Hybrid, not a pure pick.** Take best-seam-placement's schema and seam
(`override_ledger` top-level key, `kind` discriminant covering `trip` /
`force-claim` / `force-release` / `waive`, a single `_override_entries()`
merge-reader that also folds in legacy `trip_ledger` entries as `kind="trip"`
for backward-compatible reads with zero archived-JSON migration) — this is the
more honest name and the two candidates' independent agreement on the
dispatch-only write-discipline test pattern gives high confidence the rename
is executable safely. Take smallest-diff's #503 fix for `waive()` itself
(one-token `produced_by` fix inside `waive()`; the authority-mismatch read
done as a chokepoint-side post-hoc check, report-only, named promotion
trigger) — both candidates converged on this shape independently, which is
the strongest signal in either document. For closeout (#504), take BOTH
candidates' render targets rather than picking one: wire `override_summary()`
into `episode_capture.py`'s `mechanical_fields()` (best-seam-placement's G6 —
the durable, retrospective-consumed surface, absence-is-meaningful) AND add
the same cheap computed `overrides` field to `finish_work`'s return dict
(smallest-diff's G5 — free, already flows to `spine_done_cli.py`'s printed
output, visible at the moment of closing, not just in the durable record
later). These are complementary, not competing, and the second costs a few
lines against an already-loaded dict.

**Explicitly dropped:** best-seam-placement's G5 (relocating `amend`'s
`cl["amendments"]` append to the dispatch chokepoint "for consistency").
Real reasoning, but no closeout-visibility or ledger-unification payoff —
`amend` stays out of the unified ledger by both candidates' own agreement, and
moving its write site buys future-proofing this mission does not need today
at the cost of touching a third verb's mechanics with no test surface calling
for it. Recorded as an untaken road below, not silently lost.

## Untaken-road record

- **best-seam-placement's amend-relocation (its G5).** Skipped: no payoff for
  this mission's two named defects (#503, #504) or the ledger-unification
  goal; `amend` was already ruled out of ledger scope by both candidates.
  Worth a future issue if `amend` ever grows its own `override_policy`-shaped
  authority check, not before.
- **A third "just add three parallel top-level lists" candidate.** Skipped:
  both blind candidates independently rejected this shape as the naive/leaky
  option; a third parallel run to confirm that agreement would be redundant.
- **A data migration that rewrites archived `trip_ledger` JSON in place.**
  Skipped by both candidates and by this convergence: out of scope (touches
  archived history this run has no mandate to rewrite) and unnecessary once a
  read-side merge function exists.

## Panel-vs-single record

Single pair (N=2), not a panel — restated per the brief: this is a
fairly-easy call inside a tightly-fenced surface with a proven seam already in
hand, not an architecture-touching or load-bearing-interface decision that
would warrant a 3+ panel.
