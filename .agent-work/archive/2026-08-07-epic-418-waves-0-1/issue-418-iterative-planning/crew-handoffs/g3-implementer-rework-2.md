# G3 Implementer Rework 2

Use `constellation-implementer` for the two remaining launch-authorization defects in `.agent-work/issue-418-iterative-planning/g3-review-2/REVIEW_RESULT.md`.

TDD first in the real installed-runtime surface: add cases proving `admiral-prelaunch` refuses (nonzero) a valid G2 result with `applicable:false` and refuses `decision:"stop"` with `current_wave:null`. These are valid transition records but cannot authorize `NEXT_WAVE`. Prove causal red before production edits.

Then make the smallest correction in `verify_iterative_role_artifacts.py`: after generic G2 verification and before launch authorization/render success, require `applicable is true` and a non-terminal decision. Preserve the separate ability of G2 to validate/render proposals and stop records outside next-launch authorization. Update Admiral doctrine only if needed to state this distinction.

Run the exact frozen suite, reviewer installed probe, installer suite, G1/G2/init suite, JSON/diff/no-network checks. Recompute the exact final ordinal inventory/digest and refresh `IMPLEMENTER_RESULT.md` with rework RED/GREEN. No engine/schema/tracker/network/history/unrelated edits. Complete/release the checklist and report to `/root`.
