# Design-it-twice Brief: gate-plan shape for the #458 readiness check

## The one thing being designed twice

How to decompose "add a readiness check to `install_constellation.py`" into Commander gates.

## Count and panel — a surfaced choice

**N=2, self-authored single pass (not parallel-dispatched), named as an untaken road below.**
Rationale: the higher-order architectural choice this comparison would otherwise contest —
mode-of-installer vs. standalone script — is already substantially pre-decided by the launch
order's Pre-Ruling 4 ("prefer a mode of `install_constellation.py`... unless you can argue the
separation is worth a second entry point"; no such argument surfaced during `understand`). What
remains is a genuinely "fairly-easy call" per `global-orchestrator.md` §Design-it-twice, which
explicitly permits "a single with the alternatives named as untaken roads" at this weight.

## The constraints (one per candidate, each distinct and named)

- **smallest-diff** — one gate, one implement/review/integrate cycle, all four checks and their
  CLI wiring in the same pass.
- **best-seam-placement** — two gates: g1 extracts the four readiness checks as independently
  callable/testable pure functions; g2 wires them into the CLI mode and its report/exit-code
  formatting, reviewed separately.

## Compared on

- **Depth** — smallest-diff leaks report-formatting concerns into the same pass as detection
  logic; best-seam-placement hides CLI concerns behind a smaller, pure check-computation seam.
- **Locality** — smallest-diff stays inside one commit boundary; best-seam-placement spreads one
  ~150-line, single-file feature across two gates and two review round-trips.
- **Seam placement** — best-seam-placement's seam (pure check functions vs. CLI wiring) is real
  and independently testable, but for a feature this size the implementer would naturally write
  both together regardless, and the reviewer inspects both in one diff either way.
- **Testability** — both allow full unit testing of each of the four checks in isolation; the
  second gate does not meaningfully add coverage a single gate's tests can't already assert.

## Output — a recommendation, never a menu

**Named hybrid: smallest-diff's ONE gate, carrying best-seam-placement's seam discipline as an
implementation instruction inside that gate's handoff** — each of the four readiness checks
written as a separately-callable, separately-testable function, with one thin CLI/report layer
on top, but reviewed as a single diff in a single gate. This captures the seam's testability
benefit without paying for a second gate's review round-trip on a Sonnet-tier, one-issue budget.

## Untaken-road record — loud skips

- **Parallel agent dispatch for this comparison** — skipped; ran as a single self-authored pass
  instead, per the Count-and-panel rationale above (Pre-Ruling 4 already narrowed the load-bearing
  half of the decision; what remained was fairly-easy-call-weight).
- **A three-way split (checks / CLI wiring / fresh-clone test harness as separate gates)** —
  skipped; the fresh-clone observation (Pre-Ruling 3) is evidence gathered during g1's own
  integrate step (run the built check against a real fresh clone), not a separate deliverable
  gate, since nothing is shipped by that step alone.

## Panel-vs-single record

Single (self-authored), because fairly-easy-call weight — restated for the plan-approval
checkpoint (satisfied here via the launch order's frozen intent in delegated mode, no reachable
human) so the scaling call is visible and overturnable.
