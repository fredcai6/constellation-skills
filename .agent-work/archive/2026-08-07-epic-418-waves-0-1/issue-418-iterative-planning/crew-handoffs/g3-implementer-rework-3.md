# G3 Implementer Rework 3

Use `constellation-implementer` for the final Gate 3 launch-authorization edge in `.agent-work/issue-418-iterative-planning/g3-review-3/REVIEW_RESULT.md`.

TDD first in the real installed runtime: add a case proving an otherwise valid, applicable `decision:"repair"` record is valid/renderable through generic G2 but returns nonzero from `admiral-prelaunch` for `NEXT_WAVE`. Preserve successful authorization for applicable `advance` and `replan`; preserve refusal for `applicable:false` and `stop`.

Make the smallest prelaunch-only correction: authorize next launch iff `applicable is true` and `decision` is `advance` or `replan`. Do not alter generic G2 validation/rendering, engine, schemas, authority, tracker/network, history, or unrelated files.

Run the exact focused suite, all reviewer installed probes, installer suite, G1/G2/init suite, JSON/diff/no-network/path audits. Refresh the nine-path ordinal digest and implementer result with causal RED/GREEN. Complete/release the checklist and report to `/root`.
