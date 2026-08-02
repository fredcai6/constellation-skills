# Reviewer Handoff — G3 (hierarchical Student-t shrinkage fit)

## Gate
g3-review (issue #666, epic #659)

## Survey State Location
`.agent-work/666-driver-fingerprint/g3-review/review.json` (NOT the worktree root).

## What Was Implemented
`src/physics/fingerprint/fit.py` — the hierarchical Student-t shrinkage fit (field → driver-overall → class cell
+ class-across-drivers parent, recency-weighted, both channels, strictly-pre) writing exactly-k cells into the G2
store; + `tests/unit/physics/fingerprint/test_fit.py` (14 tests). Implementer reports 14/14 fit, 83/83 package,
1006/1006 fingerprint+layer2 (no regression); commander re-ran 14/14.

## How to Inspect the Diff
UNCOMMITTED working tree of `C:/Programs/f1brainz-wt/epic659-666` (NOT `git diff main...HEAD`). `git status
--porcelain` then `git diff`. Implementer result + assumptions at
`.agent-work/666-driver-fingerprint/crew-handoffs/g3-implement-result.md`. #675 verdict in `notes-666.md`.

## Task Statement
Build the strictly-pre hierarchical shrinkage fit, both channels, applying the #675 class-level shared_floor
(sqrt(var_circuit) per channel) once, with the crown invariants structural. No fit-on-read; no edit of
pooling/student_t.

## Close Criteria (each a review check — REPRODUCE, esp. by sabotage)
- **Cutoff-leakage KEYSTONE (crown):** the strictly-pre cutoff filters the ENTIRE input set to
  `round_idx<=as_of_round` before ANY pooling. REPRODUCE both poison forms: an added TARGET-driver row at
  round>R AND an added NON-TARGET driver row at round>R must BOTH leave the target cell (mean AND sigma)
  byte-identical. The non-target case is the load-bearing one (proves the class-across-drivers parent + field
  mean are also cut) — if the test only poisons the target driver, BLOCK. Confirm #628's 14.6× precedent is cited.
- **σ priced ONCE at a single site (crown):** find the SOLE `pool_random_effects` call site
  (`_price_sigma_with_shared_floor`); confirm it is invoked exactly once per resolved cell (the implementer used a
  spy/call-count — reproduce it) and that shared_floor = `sqrt(fit_two_way(...).var_circuit)` for the channel.
  Confirm idempotence (re-flooring is a no-op). The driver-overall level must NOT be floored.
- **G σ⁺=0 byte-identical POINT (crown):** g_sigma_onesided=0 vs >0 leaves the mean byte-identical (σ differs).
- **sigma_lapsampling present-but-zero:** carried as a present component (NULL→0), not dropped.
- **as_of_round REQUIRED no default:** calling without it is a TypeError.
- **Hierarchy + recency:** field/driver/class/parent via fit_two_way; recency `0.5**(Δround/halflife)`; recent
  outweighs old.
- **Both channels** (time + energy) written; **exactly k cells + unresolved-not-missing**.
- **No fit-on-read; pooling.py/student_t.py UNMODIFIED** (git diff empty for both); no data/.agent-work blob staged.

## Allowed Scope
`src/physics/fingerprint/fit.py` + `test_fit.py`. Read-only consumption of pooling/student_t/G2 modules.

## Specific Exclusions
Do NOT require G4 end-to-end validation. The sigma0 base + recency mechanics choices are implementer-authorized
(check they are principled + documented, not that they match a specific formula).

## Constraints the Implementation Must Respect
- as_of_round required; cutoff over entire input set; σ once at one site; byte-identical point under G σ⁺=0;
  sigma_lapsampling present-but-zero; no forbidden-file edit; no blob.

## Map Anchors (inbound)
- **Decision anchors:** `decision:c1_driver_utilization_design` — strictly_pre load-bearing; 14.6× precedent.
  `@grade: settled/measured · leans g3-implement`
  `decision:pooled_sigma_shared_systematic_floor` — class-axis shared_floor. `@grade: settled/measured`
- **Evidence expectations:** `claim: cutoff-leakage`, `claim: sigma-priced-once`, `claim: G-byte-identical`.

## Evidence Produced
Implementer result (path above) with the keystone/σ-once/G tests + 14/14 test_fit + simplification_limits;
commander re-ran 14/14, confirmed pooling/student_t unmodified + single pool_random_effects site + clean tree.
Verify against `g3-integrate.c1` (test_fit pytest) and `g3-integrate.c2` (APPROVE verdict).

## Suggested Model Tier
Stronger — the invariant-dense heart; the parent-side cutoff + once-priced σ are the load-bearing checks.

## Stop Conditions
BLOCK if: the keystone test omits the non-target-driver poison; the σ floor is applied more than once or to the
driver level; the point is not byte-identical under G σ⁺=0; a forbidden file was edited; evidence unverifiable.

## Return Format
REVIEW_RESULT: verdict APPROVE/BLOCK, per-check findings, blockers, out-of-scope, workflow feedback. Write to
`.agent-work/666-driver-fingerprint/crew-handoffs/g3-review-result.md` AND SendMessage a concise summary to
`cmdr-666` before ending your turn.
