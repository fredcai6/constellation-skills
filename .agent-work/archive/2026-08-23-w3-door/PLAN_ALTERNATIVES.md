# Design-it-twice Brief: how to express "clear the spine pair" in `_crew_door_env`

## The one thing being designed twice

The single load-bearing decision: where does the "actively clear SPINE_FILE/SPINE_SESSION
when `spine is None`" logic live — inside `_crew_door_env` only, or pushed down into
`crew_env` as a first-class primitive capability. `decision:clear-both-or-neither`
(clear both together, never one) is already settled/admiral and not re-litigated here.

## Count and panel — a surfaced choice

N=2, single self-authored pass per candidate (not two independently-dispatched agents) —
surfaced as an untaken road below. Fairly-easy call: the design space is genuinely narrow
(the mission names the exact function to edit, and the pre-ruling already settled the
"both together" shape), so a 2-candidate comparison rather than a 3+ panel.

## The constraints (one per candidate, each distinct and named)

- **minimal-diff** — touch only `_crew_door_env`; `crew_env`'s signature/contract is
  untouched.
- **primitive-clear** — push "clear" into `crew_env` itself as a first-class kwarg, so any
  future direct caller of `crew_env` inherits the same safety.

## Compared on

- **Depth** — minimal-diff hides the clear-on-no-spine behind the one seam that actually
  needs it; primitive-clear exposes a new capability on `crew_env` for a caller that does
  not exist.
- **Locality** — minimal-diff changes stays inside `_crew_door_env`, matching the mission's
  own naming of that function; primitive-clear touches `crew_env`'s signature plus its
  docstring plus new unit tests at that layer too.
- **Seam placement** — `_crew_door_env` is documented as "the env every dispatched/resumed
  crew gets... built in one place so `dispatch` and `resume` cannot drift apart" — it is
  already the seam. `crew_env` is a lower-level generic env-builder with exactly one
  caller (`_crew_door_env`, grepped repo-wide, confirmed at `understand`).
- **Testability** — both are equally testable; primitive-clear adds a second set of tests
  at the `crew_env` layer for a capability nothing yet independently exercises.

## Framing block

- **Constraints in play** — minimal-diff (smallest surface) vs. primitive-clear
  (generalize the safety one layer down).
- **Dependencies** — both hold `decision:clear-both-or-neither` fixed, both must flip the
  same test (`test_dispatch_without_spine_leaves_ambient_pair_untouched`), both must edit
  both docstrings the mission calls out.
- **Illustrative sketch — NOT a proposal**: `env.pop("SPINE_FILE", None)` /
  `env.pop("SPINE_SESSION", None)` after the existing `crew_env(...)` call is the shape
  either candidate ends up emitting at the bottom; the question is only which function
  owns that logic.

## Output — recommendation

**Minimal-diff wins.** `crew_env` has exactly one caller in the entire repo
(`_crew_door_env`, confirmed by grep at `understand`) — adding a `clear_spine` kwarg to
`crew_env` is speculative generality for a caller that does not exist (YAGNI), and the
mission itself names `_crew_door_env` as the function to change, not `crew_env`. The
minimal-diff candidate's one named weakness (a future direct `crew_env` caller could
reintroduce the leak) is real but not present-tense: there is no such caller today, and
`_crew_door_env`'s updated docstring will say plainly that the crew-dispatch door
actively clears rather than inherits, which is the load-bearing fact for the next reader.

## Untaken-road record

- Independently-dispatched parallel agents for each candidate: skipped. The design space
  is narrow (single function, pre-ruled shape, mission-named target), so a self-authored
  2-candidate comparison in this context was judged sufficient rather than spending a
  subagent dispatch on a decision with one clearly dominant answer once the caller-count
  fact (grepped) is in hand.
- A 3rd candidate (e.g. a decorator/context-manager abstraction over "doors that clear vs.
  bind") was not authored: it would introduce an abstraction for a single call site,
  directly contradicting the no-speculative-abstraction default posture.

## Panel-vs-single record

Single self-authored comparison, not a panel — fairly-easy call, narrow pre-ruled design
space, mission names the exact function. Cold critic (below) still runs independently to
catch anything the single author missed.
