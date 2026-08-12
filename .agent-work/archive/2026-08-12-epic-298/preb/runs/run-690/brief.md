You are picking up issue #690 in this repository (fredcai6/f1Brainz).

--- ISSUE #690: Reconcile #664 G σ⁺ band scale (whole-lap pace σ) with per-class deficit units ---
From #664 triage T2 (recommend-and-defer). `class_utilization_observable` sets the one-sided σ⁺ = `hypot(mu,sigma)` from `get_grip_at`, whose (mu,sigma) are grip PACE-seconds (whole-lap scale), attached (coherently) only to the per-class TIME-deficit → a conservatively WIDE band (whole-lap pace σ into a per-class transit-time band). Refine so the band scales to the per-CLASS grip contribution, not the whole-lap pace swing. Low while the grip store is empty (σ⁺=0); matters once G is populated (#664-T4). **Acceptance:** per-class G σ⁺ scaling with documented rationale + a width-shape unit test. **Out of scope:** moving μ off zero (#678); re-fitting G. Flagged by both g3 reviewer + implementer; judged coherent-but-generous, non-blocking.
--- END ISSUE ---

This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify this repository's source, tests, or documentation,
do not commit, push, or open a pull request, and do not comment on the issue. Your own
working notes and planning artifacts under `.agent-work/` are the one exception, and are
expected.

Run this as a Commander. Load the `constellation-commander` skill and drive its spine
through its steps in order, stopping once the `plan` step is complete: the mission frame
authored and `execute.json` authored. Do not enter `execute`: stop there and return.
No human is reachable for this engagement, so wherever a step calls for a human decision,
record what you would have asked, decide it yourself, and carry on rather than waiting.

Your plan must name the specific files you would change and explain why each one. Finish
by stating your file list plainly under a final heading `FILES I WOULD CHANGE`, one path
per line.
