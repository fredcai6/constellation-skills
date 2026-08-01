# Design-it-twice Brief: gate plan for #688 (recovering dry grip coverage)

## The one thing being designed twice

**Where the wet-severity signal is produced and read** — i.e. the seam through which the grip
pipeline learns "how wet was this session's timed running", and therefore which files the gate plan
has to move. This is one load-bearing decision with three genuinely different realizations, not a
topic.

## Count and panel — a surfaced choice

**N = 3 (panel).** Scaled up because the decision (a) crosses the `physics → data` region boundary,
(b) changes a stored record contract with an additive-only migration, and (c) invalidates a frozen
measured-null acceptance baseline (#663 g4 / #678). "When in doubt, panel" applies squarely.

**Form deviation, recorded loudly:** the doctrine form is N agents generating **in parallel**. This
session carries a standing directive — *"Do not call the AgentTool unless the user requested it"* —
so the three candidates were authored sequentially in the Commander's own context instead. The
substance (three distinct named constraints, one comparison table, one converged recommendation) is
intact; the independence that parallel authorship buys is **not**, and that is a real reduction in
rigor which the owner should know about. Convergence below is a **defended recommendation**, and
under this engagement's self-adjudication directive the Commander also carries it — normally the
human's call.

## The constraints (one per candidate, each distinct and named)

- **A — smallest-diff**: change nothing outside `src/physics/layer2/grip_baseline.py`.
- **B — best-seam-placement**: introduce no new instrument; extend the one this repo already uses.
- **C — most-testable / zero-rebatch**: leave the producer untouched; do selection at read time.

## Candidate A — smallest-diff

Loosen `rain_flag_from_raw` from `count > 0` to a fraction over the session's own `weather` rows,
computed inside `grip_baseline`. No store change, no data-layer change, no new CLI.

Files: `src/physics/layer2/grip_baseline.py`, `tests/unit/physics/layer2/test_grip_baseline.py`.

**Verdict: REJECTED on measured evidence.** Three independent kills:
1. The instrument is wrong. 2023 Belgium Q has 1 wet sample of 95 and 62% of laps on wet tyres — A
   keeps a soaked qualifying session at any threshold. 2022 Hungary R has 27.5% wet samples and zero
   wet laps — A still drops a dry race. It fails in **both** directions, so it does not even satisfy
   the issue's own acceptance.
2. The source has holes. Seven 2024 sessions carry a nonzero `sessions.rainfall` count and **zero**
   `weather` rows; A reads 0/0 and resolves them to "dry" — a silent false-confidence, the exact
   #560 failure mode the module's Protected Intent forbids.
3. It recomputes a wet signal inside physics, against the DB-only convention and against the
   `physics → data` arrangement the map already documents at `packets/physics.md:2833`.

## Candidate B — best-seam-placement

Extend `populate_wet_features_for_db` past races-only; `grip_baseline` reads the **stored**
`wet_lap_fraction` exactly as `burn_rate_calibration.session_wet_fraction` does, derives a graded
severity with an `unknown` state, keeps `rain_flag = severity != dry`, grades the sigma inflation,
guards the drying window; `grip_store` gains the severity columns plus one named selection predicate;
a CLI drives the re-batch.

Files: `weather_features.py`, `populate_wet_features.py`, `grip_baseline.py`, `grip_store.py`,
`run_grip_batch.py` (new), four test files, two map packets, one decision anchor.

**Verdict: WINNER.**

## Candidate C — most-testable / zero-rebatch

Leave the producer alone entirely. Add a `usable_for_pooling(...)` helper on `GripStore` that joins
out to the season DB's `wet_lap_fraction` **at read time**.

Files: `grip_store.py`, `tests/unit/physics/layer2/test_grip_store.py`, plus the same data-layer
coverage extension B needs.

**Verdict: REJECTED as primary — one idea grafted.** `GripStore` is deliberately a *standalone*
database (`grip_store.py:86-92`); making its read path depend on a second, per-year DB is a strictly
worse seam than B's, and it re-does the join for every consumer. The stored sigma also stays flatly
4× wrong, so the coverage C "recovers" arrives pre-penalized into any precision-weighted pool, and
the severity is never provenance-stamped with the fit that used it. **Grafted into B:** C's correct
instinct that the *selection predicate* belongs on the store beside `get_grip_at`, not in the fit.

## Compared on

| Axis | A (smallest-diff) | B (best-seam) | C (zero-rebatch) |
|---|---|---|---|
| **Depth** | Shallow — leaks a wrong instrument to every caller | Deep — callers ask "is this usable?", not "how many samples were wet?" | Medium — good question, wrong side of the boundary |
| **Locality** | Best (1 file) but only by declining the work | Wide but *bounded*, and every file is one the defect provably lives in | Narrow, at the cost of a cross-DB read-time dependency |
| **Seam placement** | Wrong — recomputes in physics what the DB owns | Right — reuses the crossing the map already sanctions | Wrong — couples a standalone store to a per-year DB |
| **Testability** | Cheap to test, but tests a wrong rule | Every pathway falsifiable against the frozen 28-session corpus | Good in isolation; the fit path stays untested |

## Framing block (what would have gone to the human while candidates ran — not a proposal)

- **Constraints in play**: smallest-diff / best-seam-placement / zero-rebatch, chosen to span the
  real axis of disagreement — *how far outside `grip_baseline.py` is this issue allowed to reach?*
- **Held fixed for all three**: the curve's functional form (that is #678's live thread); #687's
  sigma sanity bound; any live-consumer wiring.
- **Each will have to touch or assume**: the additive-only record migration; the DB-only analysis
  rule; the fact that the #663 held-out harness numbers move when session selection moves.
- **Illustrative sketch — NOT A PROPOSAL, zero weight at convergence**: "swap the `>0` for a
  `>0.05` and move on."

## Output — recommendation

**Candidate B, with C's predicate placement grafted in and A's minimalism honored as a bound**
(the plan moves exactly the files the defect provably lives in — no refactors of neighbours,
no new config surface, no second threshold constant imported from the fuel module).

B wins on every axis that is not raw file count, and file count is the one axis the measured
evidence says we cannot optimize: A's single-file version does not actually fix the issue.

## Untaken-road record — loud skips

- **Parallel authorship of the three candidates.** Skipped: the session's standing "no AgentTool
  unless requested" directive. The comparison substance is intact; candidate independence is not.
- **A fourth candidate: `sessions.rainfall` blob with a count threshold instead of a fraction.**
  Skipped as genuinely trivial — the denominator varies 76→255 samples across sessions, so a raw
  count threshold is strictly worse than the sample-fraction A already loses on.
- **A fifth candidate: derive severity from track_status / lap-time dispersion instead of compound.**
  Skipped: it invents a third instrument when the repo already has a working, mapped one, and it
  would need its own validation corpus before it could be trusted at all.

## Panel-vs-single record

**Panel (3), because it crosses a region boundary, changes a stored record contract, and moves a
frozen acceptance baseline.** Surfaced here for the owner to overturn. If the owner rules #688
strictly to selection (see the `decision:grip-sigma-inflation-graded` pressure in the mission frame),
the panel's answer is unchanged — only gate **g3** drops out.
