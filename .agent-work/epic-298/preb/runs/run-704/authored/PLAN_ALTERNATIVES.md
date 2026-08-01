# Design-it-twice Brief: gate plan for #704 axis-grouping dedup

## The one thing being designed twice

**The seam:** what shape the shared helper takes inside `src/physics/instrument_panel/replication.py`,
and how the gate plan around it proves byte-identical behavior on a Protected-Intent module.

## Count and panel — a surfaced choice

**N = 3, authored serially in this context** (not by 3 parallel agents — see untaken roads).
Rationale: the *change* is trivially small, which argues for N=2; but the *module* is the panel's
load-bearing instrument with two `settled/human` decision anchors, and #704's own text warns the
edit re-triggers full review. "When in doubt, panel" resolves that tension toward 3. A human may
overturn the count.

## The constraints (one per candidate, each distinct and named)

- **A — smallest-diff:** minimise lines changed in `replication.py`; touch nothing else.
- **B — most-testable:** maximise machine-checkable proof that behavior is byte-identical, accepting
  a wider diff (new test file) to get it.
- **C — best-seam-placement:** put the boundary where the module's own concepts want it, even if that
  means a slightly larger refactor of the private helpers.

## Framing block — constraints, dependencies, illustrative sketch

**Constraints in play:** the three above. **Held fixed for all candidates:** the public `__all__`
surface; the double-centering formula; `ReplicationThresholds` / `REPLICATION_*`; F12-independence
(no new import into the pure core); bit-exact float ordering.

**Dependencies every candidate must assume:** `_axis_means` has no external caller; the
`test_panel_corpus.py` source-text guard targets `scripts/run_season_panel_670.py`, not this module;
`_main_effect_se` consumes a list under `np.std(ddof=1)`, so list order is load-bearing.

**Illustrative sketch — NOT A PROPOSAL, zero weight at convergence:** `def _axis_groups(grid) ->
tuple[dict, dict]` accumulating `driver_rows` / `class_cols` by `setdefault`, with both existing
functions rewritten to call it. Offered only to prime parallel reasoning.

---

## Candidate A — smallest-diff

Add `_axis_groups(grid)` returning `(driver_rows, class_cols)`. Rewrite `_axis_means` to call it and
compute means by `sum(vals)/len(vals)`, keeping its own `grand` pass. Delete the two accumulation
loops from `main_effect_margin_uncertainty`. **No test file added**; rely on the existing six
instrument_panel test files to catch regressions. Diff ≈ +14 / −16 lines, one file.

- *Depth:* good — one private name hides the whole grouping pass.
- *Locality:* excellent — one file, two call sites.
- *Seam placement:* good — the seam is exactly the duplicated pass.
- *Testability:* **weak.** Existing tests use `pytest.approx` and synthetic balanced-ish grids; they
  would not catch a last-ulp shift from a reordered summation, which is precisely the failure mode
  this refactor risks. "Byte-identical" would be asserted, not proven.

## Candidate B — most-testable

Candidate A's production change, **plus** a purpose-built identity test in the module's existing test
file: golden values captured from the pre-change implementation and asserted with `==` (not
`approx`) on ragged, unbalanced, and singleton-row grids, covering all three public entry points
that route through the helper. Diff ≈ +14 / −16 in `replication.py`, +45 in the test file.

- *Depth / Locality / Seam placement:* identical to A (same production change).
- *Testability:* **strong** — turns "byte-identical" from a claim into a check the reviewer can
  re-run, and leaves a permanent guard against a future well-meaning `fsum`/`np.mean` "cleanup" that
  would silently shift the instrument's output.
- Cost: one more file in the diff, and the golden values must be captured *before* the edit.

## Candidate C — best-seam-placement

Go further: introduce a small internal `_AxisGrouping` dataclass (rows, cols, grand, counts) and
route `_axis_means`, `per_driver_demean`, and `main_effect_margin_uncertainty` through it, with
`per_driver_demean` no longer computing the class means it discards.

- *Depth:* highest — one object carries the whole two-way decomposition.
- *Locality:* still one file, but **three** call sites and a new type.
- *Seam placement:* arguably the "right" boundary in the abstract…
- *Testability:* same as B if B's test comes along.
- **Why it loses:** it is a *deeper* edit to a Protected-Intent module for zero behavioral gain, and
  it changes `per_driver_demean` — the module's deliberately-wrong **negative control**, whose whole
  value is that it is obviously, readably the weaker correction. Adding indirection there raises
  review cost on exactly the function the docstring asks readers to scrutinise. It also risks the
  bit-exactness constraint by tempting a shared `grand` derivation across callers.

---

## Output — the recommendation

**Candidate B**, unmodified. It is Candidate A's production diff (which every candidate agrees on)
plus the one thing A lacks: proof. The decisive axis is **testability against this specific failure
mode** — a float-reordering regression is invisible to `approx`-based tests and would corrupt a
signed instrument's output silently, which is the top entry in this project's own
"failure modes to prevent" list (`docs/agents/ORCHESTRATOR_CONTEXT.md`: *silent wrong prediction*).
C is rejected for spending Protected-Intent review budget on abstraction the module did not ask for.

Sequencing consequence: the golden values must be captured **before** the production edit, so the
plan opens with a baseline gate rather than starting at the refactor.

## Untaken-road record — loud skips

- **Parallel independent authorship of the three candidates.** Not taken: this session's operating
  instruction forbids dispatching subagents. The three candidates were authored serially in one
  context, so they share an author's blind spots — the contrast between them is real, but their
  *independence* is weaker than the contract intends. Named loudly rather than glossed.
- **A "leave it alone / close won't-do" candidate.** Not generated as a design candidate because the
  proceed-vs-defer fork was already settled at `understand` (q5). It remains the honest fallback if a
  reviewer judges the review cost too high.
- **A candidate that de-duplicates across modules** (e.g. hoisting axis-grouping into a shared
  physics utility for `variance_decomposition.py` to reuse). Not generated: no second consumer exists
  today — one adapter is a hypothetical seam, and #704 scopes the fix in-module.

## Panel-vs-single record

**Panel (N=3), because the target module is load-bearing and carries `settled/human` anchors** — not
because the change is large. The scaling call is surfaced here for the approver to overturn; the
serial-authorship caveat above is part of what they are overturning or accepting.
