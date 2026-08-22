# Plan candidate — constraint: most-testable

One gate plan for w1-wiring under the constraint: every gate produces independently-verifiable
evidence, even at the cost of more gates, so no single gate's finding is unfalsifiable.

## Gates

1. **g1 — census (reasoning gate).** Enumerate every check-shaped script; classify live/unwired/dead
   with one evidence row each (the classifying command re-runnable by the reviewer). Commit
   `docs/CHECK_SCRIPT_CENSUS.md`. Verification: `grep -c '^|' docs/CHECK_SCRIPT_CENSUS.md` count
   matches `ls scripts/{verify,check,prove,measure}_*.py | wc -l`.
2. **g2 — generate_spine.py disposition (reasoning gate).** Separate gate so its own evidence
   (which live path drives spines) is independently checkable from the census rows, since it feeds
   wave 2 directly and needs to be citable on its own. Verification: the traced live path re-run
   produces a spine; `grep -rln generate_spine skills/` reproduces the launch order's "no caller"
   finding or overturns it with a cited caller.
3. **g3 — #368/#444 re-measurement (reasoning gate).** Separate gate: re-count both field groups by
   command, state whether one check covers both. Verification: the counting command is pasted and
   re-runnable.
4. **g4 — disposition, deletions OR lint (crew-shaped gate, self-driven given no crew-dispatch
   tool available this run).** Execute the census's verdict: delete dead scripts with an evidence row
   each, or author + wire + prove-can-fail the lint. Verification: `pytest` targeted + full suite;
   for a lint, a reproduced failing negative case pasted in the gate's evidence.
5. **g5 — map impact (reasoning gate).** Decide whether `map/INDEX.md` / `docs/architecture/`
   need reconciling given g1-g4's changes; this is also where "Reconciling at the end" (Cartographer)
   would normally run as a subagent — self-driven here for the same reason as g4.

## Compared on

- **Depth** — each finding gets its own falsifiable gate; higher ceremony, lower risk of an
  unreviewable bundled claim.
- **Locality** — g2/g3 stay separate from g1 so a reviewer can check "does generate_spine have a
  caller" without re-deriving the whole census.
- **Seam placement** — the disposition gate (g4) is isolated from the reasoning gates, so a code
  change is never mixed into a document gate's evidence.
- **Testability** — every gate names its own re-runnable verification command up front, before the
  work happens.

## Risk

More gates costs more ceremony per gate for a run whose central ask ("does this deserve a mechanism")
is fundamentally one measurement; over-splitting risks losing the single-document coherence the
mission's "one row, one evidence string" instruction wants.
