# G3 Evidence Repair After Rework Cap

Use `constellation-implementer` for the sole test-evidence defect in `.agent-work/issue-418-iterative-planning/g3-review-4/REVIEW_RESULT.md`. Product runtime is approved by that review; do not change production behavior.

In `tests/test_iterative_planning_doctrine.py`, make zero- and multiple-transition-audit cases use otherwise launch-authorized applicable `advance` or `replan` packets with matching audit lines. Prove the tests are causal: temporarily/otherwise demonstrate removing or bypassing audit enforcement makes them fail, then restore enforcement. Preserve the accumulated launch table (`advance`/`replan` authorize; `repair`/`stop`/non-applicable refuse).

Run the exact focused suite, installer suite, G1/G2/init suite, reviewer installed matrix, JSON/diff/no-network/path audits. Refresh the nine-path ordinal digest and implementer result with tests-only causal evidence. No production/schema/engine/tracker/network/history/unrelated changes. Complete/release the checklist and report to `/root`.
