# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4 (execute.json: g4-review)` — Regime distance-share rollup + observability router

## Result
`APPROVE`

## Handoff compliance
All close criteria from `g4-review-handoff.md` and `g4-implement-handoff.md` independently
verified against the actual diff/new files and against fresh, independent re-runs — not the
transcript alone:
- `src/physics/layer2/regime_rollup.py` implements `corner_bin_share` (pure, `set[int]` or
  `int` form, documented), `circuit_distance_share` (per-lap bin-occupancy averaged into
  `corner_distance_share`, `straight_distance_share = 1 - that`, class sub-shares via Gate 1's
  `descriptors_from_frame` + Gate 2's `posterior_membership`, `n_samples`-weighted and
  renormalized over valid rows so `corner_class_i_distance_share` sums exactly to
  `corner_distance_share`, degenerate descriptor rows counted toward bin occupancy but not
  their own class), and `load_circuit_frame` (thin, read-only, computation-free).
- `scripts/build_regime_rollup.py` fits `property_mixture.fit_property_mixture` **once** on
  the pooled full-dataset descriptors (not per-circuit), reads Gate 3's committed
  `f12_holdout_stability.json`, and propagates the FAIL verdict into both the CSV's leading
  `#`-comment lines and a sibling `regime_time_share.meta.json`.
- `src/physics/layer2/observability_router.py`'s `ROUTER_ENTRIES` covers all four regime tags
  (`corner`, `straight_throttle`, `straight_coast`, `straight_brake`) with a `view`/`citation`/
  `note` per entry, every citation independently confirmed against real source (see Evidence
  verdict).

## Scope drift
None. `git status --porcelain` shows exactly Gate 4's 5 new files (`regime_rollup.py`,
`observability_router.py`, `build_regime_rollup.py`, `test_regime_rollup.py`,
`test_observability_router.py`) plus the generated artifacts and `.agent-work/` scratch —
nothing outside allowed scope.

Specific exclusions independently confirmed clean: `git diff` shows `arcs.py` and
`segment_classifier.py` as modified, but that diff content matches exactly what
`g1-review-result.md` (APPROVE — `_contiguous_runs` generalization + `identify_straight_arcs`)
and Gate 2's `soft_class_membership` addition already describe — these are Gate-1/Gate-2 diffs,
not new Gate-4 changes. `property_mixture.py`, `mixture_stability.py`, `corner_descriptors.py`
were read in full and match their prior-gate-approved content exactly (imported, not modified).
No `data/damage_integrals.db` writes (independently re-verified: a `CREATE TABLE` attempt
against the `mode=ro` URI raises `sqlite3.OperationalError`). No `circuits.yaml`/
production-default touched. `grep` for `evo_predictor`/`latent_power`/`compound_prior` across
all 3 new physics-region files: zero matches. `git check-ignore -v` on all 5 new paths: all
exit 1 (not ignored).

## Evidence verdict
Independently reproduced, not trusted from the transcript:
- Confirmed worktree resolution first (`py -c "import src.physics.layer2.regime_rollup as m;
  print(m.__file__)"` → prints the path under `C:\Programs\f1-625`).
- `py -m pytest tests/unit/physics/layer2/test_regime_rollup.py
  tests/unit/physics/layer2/test_observability_router.py -v` → **30/30 passed**, identical
  test IDs/order to the implement-result.md transcript.
- `py scripts/build_regime_rollup.py --db C:/Programs/f1Brainz/data/damage_integrals.db` run
  independently by this review (backgrounded past the 120s foreground limit, polled to
  completion, ~2 min runtime against 612,615 pooled rows / 22 circuits). The freshly produced
  `regime_time_share.csv` is **BYTE-FOR-BYTE IDENTICAL** — every column, every decimal digit,
  all 22 rows, including class-share ordering (the mixture fit is fully deterministic under
  `random_state=0`) — to the already-committed CSV.
- Monza(Italy)=`0.5185879511947128` < Monaco=`0.8313941076003416` confirmed on this
  independent rerun.
- Read-only DB access independently re-verified (write attempts against the `mode=ro` URI
  correctly rejected at the driver level).

**Observation (non-blocking):** the transcript pasted into `g4-implement-result.md` shows
slightly different Italy/Monaco decimal values (e.g. Italy `0.5186469527477312` vs the
now-doubly-confirmed `0.5185879511947128`) with identical `n_laps`/`n_rows`. This is the
implementer's own disclosed **first**, "during development" run differing slightly from their
**second** run (which produced the committed artifact) — my independent **third** run matches
the second/committed run exactly, not the transcript's first run. This does not affect the
current deliverable's correctness (now doubly confirmed stable/reproducible by two fully
independent full reruns), but is worth naming in case it points at `grip_bin_obs` data
churning mid-session from a concurrent process against the shared main-repo DB.

## Code/doc quality
Minimal, maintainable, tested, project-rule compliant. `print()` confined to the CLI script
(CREW_CONTEXT-permitted); zero `print()` in the two library modules. No mutable module-level
state (`N_BINS`, `_LAP_KEY_CANDIDATES`, `ROUTER_ENTRIES` are all immutable literals). Read-only
`sqlite3` URI connections, per-call, no `DatabaseManager` singleton. Units/validity explicit
throughout. `constraint:physics_region_no_evo_import` and `constraint:canonical_data_source`
both independently re-confirmed.

Fowler code-smell pass (`r6-fowler`, recorded to `.agent-work/625-segmentation-substrate/
g4-review/g4-fowler-pass.json`, `scripts/verify_fowler_pass.py` exit 0): 12/12 baseline smells
rendered. 1 **flagged**, non-blocking: `duplicated-code` — `load_circuit_frame` and
`build_regime_rollup.py`'s `_connect_read_only` both hand-roll the identical
read-only-URI-connection recipe (resolve → exists-check → `FileNotFoundError` → `as_uri()` +
`?mode=ro` → `sqlite3.connect(uri, uri=True)`), differing only in error text; a shared helper
would remove the duplication. Small, correct, independently tested — non-blocking, worth a
follow-up. 1 **overridden**: `primitive-obsession` (`corner_bin_share`'s `set[int] | int`
union parameter) — subordinate to the handoff's own literal specified signature and the
already-accepted `layer2/` small-primitive convention (`g1-review-result.md`'s Fowler pass
already overrode the same smell for `bin_row_to_descriptor`'s bare tuple return).

## Map impact verdict
- **Evidence supports claimed change:** yes — the real-store run and citation-grounding tests
  independently reproduce exactly what `g4-implement-result.md`'s Map Impact section claims.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` (grep-clean)
  and `constraint:canonical_data_source` (read-only, absolute-path DB access, no FastF1 call)
  both independently confirmed.
- **Notes match the diff:** yes — structural (`struct:physics.layer2`) and capability
  (per-circuit rollup, observability router) anchors match exactly what changed; no overstated
  or missing impact.
- **Decision candidates surfaced:** yes — the class-share renormalization convention
  (degenerate rows' bin-mass proportionally absorbed into valid rows' classes) was a genuine
  interpretive choice, correctly documented as the literal reading of the handoff's "sum to
  `corner_distance_share`" requirement; no undisclosed decision beyond delegated latitude.
- **Durable context routed:** one triage candidate flagged this review (not dropped, see
  below).

## Reconciliation check
No divergence from `CONVERGED_PLAN.md` Gate 4 requiring BLOCK. Built and run exactly per plan:
pooled-once mixture fit, per-circuit rollup, F12 FAIL honestly propagated (Honest-Null
Clause), observability router with citation-grounded (not merely symbol-resolvable) entries
per cold-critic finding #5's disposition. One pre-existing, non-blocking wording gap (same
pattern already accepted in `g1-review-result.md`/`g3-review-result.md`): `CONVERGED_PLAN.md`
line 90 names the function `circuit_time_share` and `ROUTER_ENTRIES: dict[str, list[str]]`,
while the binding `g4-implement-handoff.md` (citing cold-critic dispositions #1/#5) correctly
overrides these to `circuit_distance_share` and `dict[str, list[dict]]` with citation-grounded
entries — the implementation correctly followed the handoff, not the terser/stale plan prose.

## Blockers
- none

## Out-of-scope observations
- (`tc1`, triage candidate flagged in the survey engine) `CONVERGED_PLAN.md`'s Gate-4 prose
  (`circuit_time_share`, `ROUTER_ENTRIES: dict[str, list[str]]`) is stale against the binding
  handoff's correctly-overridden signature (`circuit_distance_share`,
  `dict[str, list[dict]]` with citation-grounded entries) — a one-line `CONVERGED_PLAN.md`
  reconciliation edit would prevent a future reader from assuming the terser plan-prose
  signature is authoritative. Same pattern as Gate 3's `tc1`.
- The `duplicated-code` Fowler finding above (read-only-URI-connection boilerplate repeated
  between `load_circuit_frame` and `build_regime_rollup.py`) is a cheap, low-priority
  follow-up candidate — not filed as a blocking triage item since it is purely cosmetic and
  both copies are independently correct and tested.
- Per the handoff's own note, `py -m pytest tests/unit/physics -q` (full-suite regression) and
  the 5-file no-evo-import grep are explicitly `g4-integrate`'s responsibility, not this
  review's — not run here, consistent with the handoff's scoping.

## Workflow Feedback
- **Handoff gaps:** none material. The g4-review-handoff.md's Close Criteria list was unusually
  precise and directly checkable against source (naming discipline, F12 readability, sanity
  ordering, router citation honesty, class-sum invariant, reuse discipline, read-only access) —
  each point named exactly what evidence would settle it.
- **Context rediscovered:** the transcript-vs-committed-CSV decimal mismatch (see Evidence
  verdict observation) was not flagged anywhere in the handoff or implement-result.md's own
  text as something to check — I found it by comparing my own independent full-precision CSV
  read against the pasted transcript's full-precision values, not just the 4-decimal stdout
  print. Worth naming as a technique for a future gate's close criteria: "diff the pasted
  transcript's full-precision values against the currently-committed artifact's full-precision
  values, not just the print()'d 4-decimal summary" — it caught a real (if ultimately
  non-blocking) data-stability question the 4-decimal prints alone would have hidden.
- **Instructions improvised around:** none. The reviewer skill's engine-drive workflow and the
  Fowler-pass rail both applied cleanly; the appended `r7-close-criteria` item was a natural
  fit for the handoff's own numbered Close Criteria list, mirroring the pattern
  `g3-review-result.md` used for its `r7-genuineness` item.
- **What would have made this easier:** none — the handoff, `g4-implement-handoff.md`, and
  `g4-implement-result.md` together gave a complete, self-consistent evidence trail. The one
  genuinely useful thing to carry forward: when a handoff's Required Evidence asks for a
  "real-store run transcript," future implementers/reviewers should paste (or independently
  reproduce) FULL-PRECISION values, not just the 4-decimal `print()` summary, since that is
  what actually lets a reviewer catch subtle run-to-run drift like the one noted above.

## Return status
`complete`
