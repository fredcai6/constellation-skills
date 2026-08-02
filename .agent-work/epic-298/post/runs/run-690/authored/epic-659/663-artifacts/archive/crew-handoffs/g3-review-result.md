# Review Result — g3-implement (issue #663, module G batch driver + get_grip_at)

## Assigned Gate
`g3-implement` (reviewing for `g3-review`)

## Result
`APPROVE`

## Handoff compliance
The change does exactly what the handoff asked, within allowed scope. `run_grip_batch`
mirrors `run_estimate_batch`'s injectable-`Callable` seam (`fit_fn` / `calendar_fn` /
`record_fn` / `log` all default to the real production functions, keyword-only). Per-unit
failure isolation works: the season → GP → session loop wraps each `fit_fn` call in a
try/except that, on a raise, builds an `error_record` via `record_fn`, upserts it, bumps
`counts["errors"]`, and `continue`s — one bad session never sinks the batch. `get_grip_at`
evaluates the stored saturating curve, returns `(mu, sigma)`, raises `GripRecordNotFoundError`
(not a bare `KeyError`) on a missing PK **and** on an unusable record (`session_offset is None`,
e.g. a `fit_status="error"` row), and never silently implies `sigma=0`. All four Close
Criteria are met.

## Scope drift
Clean. Only the allowed files were touched: `grip_batch.py` (new), `test_grip_batch.py`
(new), and an additive edit to `grip_store.py` (`import math`, `GripRecordNotFoundError`,
`get_grip_at`). By inspection, `grip_store.py`'s pre-existing `GripStore` /
`GripEstimateRecord` / `error_record` are unchanged — the additive-only claim holds
(the g1 file is still untracked, so there is no tracked baseline to `git diff`, but the
additions are cleanly appended after `error_record` and nothing above them changed).
Specific exclusions respected: `grip_baseline.py` (g2) and `estimate_batch.py` were not
modified. No g4/g5 harness work was done.

## Evidence verdict
All required evidence present and **independently reproduced** (not taken on the report's word):
- `pytest test_grip_batch.py test_grip_store.py -q` → **22 passed**.
- `pytest test_grip_batch.py -k isolat` → **2 passed** (the load-bearing isolation tests).
- `simplification_limits` on the 3 files → **PASS**.

The isolation test assertions genuinely verify continuation (I read them, not just the
pass count): `test_batch_isolates_one_failing_session_and_continues` makes `fit_fn` raise
for Monaco/Q only, then asserts `fitted==1` (Bahrain still fitted), `errors==1`, the error
row lands in the store with `fit_status="error"`, the exact exception message, and the
`session_id==-1` sentinel; the bracketing variant isolates two failing GPs around one good
one with exact per-GP status partitions. The `get_grip_at` tests assert curve evaluation
against a hand-computed expected `mu`, `sigma > 0` **and** `sigma != raw offset sigma`
(so the curve uncertainty genuinely propagates), the thin-fallback path returning
`offset_sigma`, and the named exception (never a bare `KeyError`) on both missing and
unusable-error records. Test mode was test-after (allowed by the handoff).

## Code/doc quality
Minimal, maintainable, convention-matched. The delta-method sigma is honest: the
`max(variance, 0.0)` clamp is mathematically defensive-only — for `|corr| <= 1`,
`offset_sigma² + d_asy²·asy_sigma² + 2·corr·offset_sigma·d_asy·asy_sigma ≥
(offset_sigma − d_asy·asy_sigma)² ≥ 0`, so it can never actually produce `sigma=0` for a
well-formed record. The `record_fn` re-mapping (build an error record when `fit_fn` raises
outright, since g2's `fit_fn` already returns a full record on the success path — unlike
`estimate_batch.py`'s estimate→transform split) is a documented, in-scope Authority
decision, honestly flagged in the IMPLEMENTER_RESULT. Docstrings explain real design
choices rather than papering over unclear code.

**Fowler code-smell pass:** all 12 baseline smells rendered a verdict (rail
`verify_fowler_pass.py` exit 0). 10 `absent`; 2 `overridden` with logged repo-standard
reasons — **data-clumps** (the `(year, gp_name, session_type)` PK triple travels together,
but a value-object would diverge this module from every `estimate_*`/g2 sibling and break
the mandated `estimate_batch.py` mirroring) and **long-parameter-list** (9 params, but the
injectable-collaborator-fn seam is the handoff's explicit non-negotiable constraint and each
fn is a genuine, tested seam). Nothing rises to a blocker. Record at
`.agent-work/663-grip-g/g3-review/fowler_pass.json`.

## Map impact verdict
- **Evidence supports claimed change:** yes — the two claims (`claim:failure-isolation-batch-level`,
  `claim:get-grip-at-honest-sigma`) are each backed by dedicated, reproduced tests.
- **Constraints not violated:** injectable-fn pattern, per-unit isolation, honest sigma all honored;
  `decision:session-scope-uniform` honored (fans out over `SESSION_TYPES` when unfiltered).
- **Notes match the diff:** yes — new `struct:physics.layer2` sibling module + additive consumer
  query surface; no overstated or missing structural/capability impact.
- **Decision candidates surfaced:** yes — the `record_fn` re-mapping is honestly flagged as a
  plausible-alternative reading worth a Cartographer/Commander sanity check.
- **Durable context routed:** yes — three triage candidates routed, not dropped.

## THE ONE THING — weekend-neighbor determination: **(b), does NOT block**
The gap is real but **appropriately out-of-scope for g3**, and it does **not** bite the two
GATING gates. Decisive evidence from `grip_baseline.py`:

- `run_grip_batch` calls `fit_session_grip_baseline` — the **DB wrapper**, whole-session,
  with **no driver-subset parameter**.
- **g4-implement** requires fitting G using **ONLY fit-set drivers' laps** and scoring on the
  held-out drivers. That driver split is *impossible* through `run_grip_batch` (it fits the
  whole session's field). g4 must therefore call the lap-frame seam
  `fit_grip_baseline_from_laps(..., laps=<fit-set frame>, weekend_neighbors=...)`
  (`grip_baseline.py:442`), where **`weekend_neighbors` is a first-class exposed parameter
  (line 450)**. So the batch driver's un-wired neighbors are irrelevant to g4, and g4 can
  supply neighbors directly at the seam it must use anyway.
- **g5-implement** says run "G's actual fit pipeline (from g2, imported directly — not a
  reimplementation)" on synthetic injected data. It never routes through `run_grip_batch`.
- Additionally, g4 fits full-field race sessions on a 3–5 circuit slice (~10 drivers per
  50/50 split) and g5 injects realistic, fittable field-pooled data, so the thin-session
  fallback — and thus its neighbor-lookup path — is unlikely to even trigger in their
  primary evaluation.

The implementer flagged this clearly and honestly as triage candidate #1 with correct
scoping ("needs an ordered two-pass batch… real design work, not a drop-in"). It **is** a
genuine limitation for a future *production* store-population run via `run_grip_batch`
(where thin sessions would degrade straight to the degenerate no-neighbor path), so it is
correctly deferred to triage — recorded here and flagged through the engine, not silently
dropped.

## Reconciliation check
No architecture divergence needing Commander reconcile beyond what g1/g2 already surfaced.
The session-level PK divergence (`GripEstimateRecord` PK = `(year,gp_name,session_type)` vs
`EstimateRecord`'s per-constructor PK) is already carried into g6-verdict's triage list and
the Mission decision-pressure note — no new action required here.

## Blockers
- None.

## Out-of-scope observations (triage candidates — flagged through the engine)
- **tc1 — weekend_neighbors batch wiring** (`run_grip_batch`): thin-session fallbacks in a
  real production run degrade to the no-neighbor path even when a normal same-weekend fit
  exists; needs an ordered two-pass batch. Does NOT affect g4/g5.
- **tc2 — `get_grip_at` query cost:** `store.load(year, session_type)` + pandas `gp_name`
  filter rather than an indexed single-row query. Fine at current volumes; revisit for a
  tight-loop hot-path consumer.
- **(implementer's #3) `session_id=-1` sentinel documentation reach:** if a future consumer
  of the `grip_estimates` table assumes `session_id` is always a valid DB id, the `-1`
  error-path sentinel would want documenting there too (currently only in `grip_batch.py`).

## Workflow Feedback
- **Handoff gaps:** none in the g3-review handoff itself — it was unusually well-targeted,
  and the "THE ONE THING TO SCRUTINIZE" section correctly pointed me to read the g4/g5
  imperatives in `execute.json`, which is exactly where the answer lived. Confirmed after
  review: the handoff's assumption ("g4/g5 call g2's fit fairly directly rather than through
  run_grip_batch") is not just plausible but *structurally forced* — g4's driver-subset
  requirement is incompatible with `run_grip_batch`'s whole-session `fit_fn` signature.
- **Context rediscovered:** I had to read `grip_baseline.py` to discover the two-tier fit
  seam (`fit_session_grip_baseline` DB-wrapper vs `fit_grip_baseline_from_laps` lap-frame,
  the latter exposing `weekend_neighbors`). The handoff pointed at g2's neighbor mechanism
  but not at *which* seam g4 would use — that seam distinction is what makes the answer
  unambiguous, and a one-line pointer would have saved the lookup.
- **Instructions improvised around:** the handoff notes `grip_store.py` is untracked so
  there is no incremental `git diff` — I confirmed the additive-only claim by inspection of
  the appended region instead. Worth noting the same untracked-baseline situation will
  recur for g4/g5 unless g1–g3 get committed first.
- **What would have made this easier:** a one-line note in the handoff naming the lap-frame
  seam (`fit_grip_baseline_from_laps`) as the surface g4 would use — it is the linchpin of
  the weekend-neighbor determination.

## Return status
`complete`
