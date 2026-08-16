# Untaken roads — lane F plan step

Both plan-step rigor mechanisms are bias-to-yes. One was run, one was skipped;
the skip is named here rather than left silent.

## Taken: cold plan critic — **single, not a panel**

Run as one cold critic reading `MISSION_FRAME.md` and `execute.json` only, on
the three standard lenses (intent-fit, testability, simplicity/YAGNI).

**Panel-vs-single, surfaced:** single. A panel is the default when an artifact
spawns epics or touches architecture. This plan does neither — it decomposes one
bounded, already-designed issue into four gates, and its architecture-shaping
choices were made one tier up and arrive as frozen pre-rulings. What the critic
is actually being asked to judge is gate decomposition and falsifiability, which
one competent cold reader covers. Competitive-critic was not used (opt-in only,
and it needs a human to dispose of findings).

## Skipped: plan-alternatives (design-it-twice)

**Not run.** Reason, stated so the approver sees it:

The launch order's *Pre-empted Steps* freeze the design — "Triage and design are
done. #609 carries the rule, the retirement list, the two known limits and the
migration question. Implement; do not re-derive the design." Every load-bearing
interface choice arrives pre-ruled: the derivation rule (nearest ancestor, fail
closed), where normalization happens (once, at the boundary, reusing an existing
definition), what the stamp becomes (provenance, read by nothing), and that the
worktree is location and never identity. Generating parallel gate-plan candidates
under distinct constraints would be generating alternatives to a design that is
not this run's to choose.

The one genuinely open interface question the order left open — **where the
derivation function lives** — the order itself scoped as a settle-experiment
with a named first choice ("try the single-definition placement first and report
what it would require"). That experiment was run at `understand`, not deferred:
`scripts/hooks/spine_rail.py` has zero cross-module imports and no
`SCRIPT_RUNTIME_COMPANIONS` entry, so any placement outside it requires editing
lane A's installer. The answer is measured, not chosen, so there is nothing for
competing candidates to compete over.

**What is lost by skipping.** A genuinely different *decomposition* — for
instance, landing #315 first and derivation second, or collapsing all four gates
into one — was never generated in parallel and compared on depth, locality, seam
placement and testability. The ordering used instead follows the launch order's
own sequencing instruction ("Derivation and `origin_worktree_refusal` first;
#315's `cwd=` thread is small once they land"), with one deliberate departure:
#315 was moved to **last**, behind the hook-ownership gate, because it is the
gate expected to surface a floated conflict and everything else should land
before it blocks. That departure is the only decomposition choice this run made
alone, and the cold critic was pointed at it explicitly.
