# Reviewer Handoff

## Gate
g4-implement (reviewing for g4-review) — GATING acceptance gate, issue #663

## What Was Implemented
`tests/unit/physics/layer2/test_grip_heldout.py`: a real-data held-out reconciliation harness across 4 contrasting 2023 circuits (Monaco, Spain, Netherlands, Saudi Arabia; FP-vs-FP session pairs). Result: **MEASURED NEGATIVE / honest-null** — subtracting G's fitted curve+offset WORSENS held-out cross-session reconciliation RMS by +155.5% (before 3.02s -> after 7.72s aggregate, 0/4 circuits improved). Diagnosed to structurally unidentified per-session saturating-curve fits on practice data (offset<->asymptote correlation near ±1 in several sessions, implausible offset/asymptote magnitudes).

## How to Inspect the Diff
```bash
cd /c/Programs/f1brainz-wt/epic659-663
git status --porcelain
```
New file, untracked. Read `tests/unit/physics/layer2/test_grip_heldout.py` directly in full.

## Task Statement
Build the held-out reconciliation GATING harness per the frozen decision (driver-split, fit-set-only fit, held-out scoring, leakage discipline, honest-null operationalization). This is NOT a rubber-stamp review — this is the FIRST of two GATING acceptance criteria for the whole issue, and the reported result is a significant negative finding about G's current viability. Your job is to determine whether this negative is REAL (a genuine, correctly-measured property of G's current fit) or an ARTIFACT of a flawed harness (in which case it should BLOCK, not because the result is unwelcome, but because an unverified harness cannot be trusted either way).

## Close Criteria — scrutinize each carefully, do not just re-run and accept
1. **Split integrity:** re-verify the driver split is genuinely disjoint (read the assertion, re-run and confirm the printed sets don't overlap for at least 2 circuits by hand).
2. **Fit-set-only fit:** confirm G is ACTUALLY fit using only fit-set drivers' laps (not the full field) — read the exact call into `fit_grip_baseline_from_laps` and confirm the `laps` argument is filtered to fit-set drivers before the call, not after.
3. **Held-out-only scoring:** confirm the reconciliation metric is computed ONLY on held-out drivers' laps — read the scoring loop.
4. **Leakage-avoidance-by-design claim:** the implementer claims the truth side uses raw fastest-3-laps median (no regression), hence "structurally not collinear" with G's own tyre_life/fuel terms, hence no rank-check needed. VERIFY this claim by reading the actual pace-extraction code — confirm there really is no `np.linalg.lstsq`/OLS/regression call anywhere on the truth-side comparison path. If there IS one you missed, the LEAKAGE DISCIPLINE constraint was violated and this is a BLOCK.
5. **Negative-control (swap test) logic:** confirm the "swap" comparison (using the WRONG session's G on a held-out driver) is actually wired to use a different session's G than the "after" comparison uses — re-read the code, don't trust the printed table alone. If swap and after are accidentally computing the same thing, the "directional/real, not machinery" argument collapses.
6. **The diagnosis (why the negative):** independently sanity-check ONE of the cited degenerate fits yourself — e.g. re-run `fit_grip_baseline_from_laps` on Monaco FP2 (or another named session) directly, and confirm the printed offset/asymptote/correlation numbers reproduce. If they don't reproduce, something is wrong with either the harness or its diagnostic printout.
7. **Honest-null operationalization:** read every `assert` in the test file (already greppable) and confirm NONE of them asserts `after_rms < before_rms` or any equivalent "G must improve" condition — only harness-validity assertions (split disjoint, all fields finite, cell counts >0, etc). This is the most important structural property of this gate.
8. **Scope honesty:** confirm the harness genuinely ran 4 real circuits against `C:/Programs/f1Brainz/data/f1_data_2023.db` (not a synthetic fixture) and the printed scope matches what's claimed in the result.

## Allowed Scope
New file only: `tests/unit/physics/layer2/test_grip_heldout.py`.

## Specific Exclusions
Do not modify `grip_baseline.py`, `grip_store.py`, or `grip_batch.py` — even if you suspect the ill-conditioned curve fit is a bug in g2, that is NOT this gate's job to fix (if you believe it needs fixing, say so as a blocking or triage finding, and the commander will decide whether to reopen g2 or accept the null as the deliverable per the Honest-Null Clause).

## Constraints the Implementation Must Respect
Held-out-not-in-sample, leakage discipline, honest-null operationalization (see Close Criteria above — these ARE the constraints for this gate).

## Map Anchors (inbound)
- **Decision anchors:** `decision:held-out-not-in-sample` @grade: settled/human; `decision:heldout-split-axis` @grade: guess.
- **Constraints/assumptions:** `constraint:db-only-analysis`.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/663-grip-g/crew-handoffs/g4-implement-result.md`, results artifact at `.agent-work/663-grip-g/g4-heldout-results.json`. Use `"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe"` for every command; run with `-q -s` so diagnostic output isn't swallowed.

## Suggested Model Tier
Stronger — reason: this is a GATING gate with a significant negative finding; getting this wrong (accepting a broken harness's false negative, OR rejecting a valid honest-null out of discomfort with the result) has real consequences for the issue's verdict.

## Stop Conditions
Stop and return BLOCK if: the split isn't genuinely disjoint, fit-set laps leak into the fit, held-out laps leak into training, a hidden regression violates the leakage discipline, the swap/negative-control isn't actually wired correctly, a diagnosed degenerate fit doesn't reproduce, or any assertion secretly encodes "G must improve."

## Return Format
Return REVIEW_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g4-review-result.md`, and return as final message text): verdict (APPROVE or BLOCK), per-check findings for EACH of the 8 close criteria above, your independent determination of whether the negative result is real or an artifact, blockers, out-of-scope observations, workflow feedback.
