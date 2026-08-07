# G1 Implementer Rework 1

Reviewer verdict: BLOCK only on stale evidence identity. All behavioral, scope, quality, migration, receipt, rename, and exclusion checks passed.

Required rework:

1. Read `.agent-work/issue-418-iterative-planning/g1-review/REVIEW_RESULT.md`.
2. Recompute the exact sorted 20-path current-byte digest using the documented algorithm after every final test/edit. Persist the path inventory and reproducible command/helper with the result so the next reviewer does not reconstruct it.
3. Re-run the identical focused GREEN command. Do not change production behavior unless reproducing the digest uncovers a real defect.
4. Update `.agent-work/issue-418-iterative-planning/g1-implement/IMPLEMENTER_RESULT.md` with `gate_id: g1`, `red_exit: 1`, `green_exit: 0`, the current reproducible digest, exact inventory/algorithm, and current green output. Preserve the historical causal RED explanation; note the final-test overlay reproduces 29 expected missing-behavior failures because two tests were added while green.
5. Drive `constellation-implementer` rework checklist to terminal state and send the refreshed result to `/root`.

No scope expansion. Do not touch archives, external state, G2/G3, or add an alias.
