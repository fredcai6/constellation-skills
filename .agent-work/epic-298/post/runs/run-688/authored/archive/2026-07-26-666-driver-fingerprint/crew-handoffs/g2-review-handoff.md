# Reviewer Handoff — G2 (address space + ClassVocabulary + versioned cell store)

## Gate
g2-review (issue #666, epic #659)

## Survey State Location
`.agent-work/666-driver-fingerprint/g2-review/review.json` (NOT the worktree root).

## What Was Implemented
`src/physics/fingerprint/address.py` (CellAddress + non-NULL cell_key), `vocabulary.py` (ClassVocabulary + F12
verdict + require_fittable + era_key), `store.py` (DriverFingerprintStore, own DB, k-cells/unresolved,
replace-on-rerun, loud refusals, no-fit-on-read), + tests. 65 tests green (implementer + commander re-run).

## How to Inspect the Diff
UNCOMMITTED working tree of `C:/Programs/f1brainz-wt/epic659-666` (NOT `git diff main...HEAD`).
`git status --porcelain` then `git diff`. Implementer result at
`.agent-work/666-driver-fingerprint/crew-handoffs/g2-implement-result.md`.

## Task Statement
Build the structural spine (address/vocabulary/store) with the k-cells, non-NULL-cell_key, loud-refusal,
replace-on-rerun, and NO-fit-on-read invariants STRUCTURAL. No fit logic.

## Close Criteria (each a review check — REPRODUCE, don't trust)
- `cell_key` is provably ALWAYS non-NULL: `CellAddress.__post_init__` raises on any None/empty component AND the
  store's PK column is declared `NOT NULL`. Try to construct a CellAddress with an empty field → must raise.
- `INSERT OR REPLACE` idempotency: writing the same fingerprint twice yields k rows, not 2k (find the test; run it).
- k-cells-always-populated: a fingerprint with a class lacking support returns EXACTLY k cells with an
  `unresolved` status row, NEVER a missing row.
- LOUD refusal (raises, no silent substitution) on era/vocabulary mismatch AND on a non-PASS `f12_verdict`
  vocabulary (unless explicit override). Reproduce both refusals.
- NO fit-on-read: `store.py` imports NOTHING from a fit/pooling/observables module; a read never triggers a
  compute. Verify by inspection (grep imports) — the implementer used an ast scan; confirm it.
- Dormant slots present-but-unused: `channel` supports "utilization"+"energy"; `what_measure` has the 4 reserved
  slots present but the store refuses to populate a reserved slot in Build 1.
- Tests use TEMP DBs only (no real DB touched); no data/.agent-work blob staged; simplification_limits passes.

## Allowed Scope
The 3 `src/physics/fingerprint/*.py` + 3 test files. No existing module edited.

## Specific Exclusions
No fit logic expected (G3). The era_key derivation choice (RegulationEra flag signature) is implementer-authorized.

## Constraints the Implementation Must Respect
- Interpreter PIN + `PYTHONPATH=.`; `from src...` imports. OWN db (#632); temp DBs in tests (#656).
- Non-NULL cell_key STRUCTURAL. Loud refusals. Dormant slots present-unused.

## Map Anchors (inbound)
- **Structural:** NEW `struct:physics.fingerprint`; house pattern from reference_utilization_store/grip_store;
  `RegulationEra.for_season`.
- **Decision anchors:** `decision:fingerprint-era-key` — era from RegulationEra.for_season; k=4 severity.
  `@grade: guess · leans g2-implement`
- **Evidence expectations:** `claim: loud-refusal`, `claim: k-cells-populated`.
- **Map confidence flags:** ClassVocabulary net-new.

## Evidence Produced
Implementer result (path above) with 65/65 pytest + simplification_limits pass; commander re-ran 65/65 green +
confirmed no fit import in store + clean tree. Verify against `g2-integrate.c1` (fingerprint pytest command) and
`g2-integrate.c2` (APPROVE verdict).

## Suggested Model Tier
Stronger — keystone store; the structural-invariant checks are the point.

## Stop Conditions
BLOCK if: any invariant is a convention rather than structural (esp. NULL-able cell_key, missing-row instead of
unresolved, a silent substitution, or a read that fits); evidence unverifiable.

## Return Format
REVIEW_RESULT: verdict APPROVE/BLOCK, per-check findings, blockers, out-of-scope, workflow feedback. Write to
`.agent-work/666-driver-fingerprint/crew-handoffs/g2-review-result.md` AND SendMessage a concise summary to
`cmdr-666` before ending your turn.
