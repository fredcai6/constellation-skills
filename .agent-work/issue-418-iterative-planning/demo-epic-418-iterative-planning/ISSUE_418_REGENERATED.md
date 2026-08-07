## Intent and why
Constellation agents cannot reliably sense their own context fill — self-report is confabulation — and the host harness only intervenes at ~90% with a lossy emergency auto-compaction. The governor gives the fleet a **proactive, portable way to hand off cleanly at a good work seam** before that point: a long-running agent, told by the engine that it is near-full, judges whether now is a good stopping point (biased toward yes) and hands off up its delegation chain to be re-instantiated fresh — carrying its reasoning, not just its mechanical state.

"Done" feels like: an agent finishing a unit of work is told "you've used most of your context"; unless it is basically finished it hands off at that seam; its invoker (Commander → implementer/reviewer; Admiral → Commander; human at the top) starts a fresh agent from a handoff rich enough for a clean cold start, and the fresh agent resumes **without re-deriving the why**.

The load-bearing reframe: the handoff is a **byproduct of continuous why-logging**, not a special artifact generated under duress. So the same mechanism that enables intentional refresh also makes ordinary crash-recovery cheap — the design pays for itself even where the gauge is crude or a harness can't refresh well.

**Kill condition:** if a clean handoff+refresh loses more effective continuity than auto-compaction preserves — i.e. the cold-start block can never be made good enough and every refresh is a productivity cliff — the governor is pointless.

## Definition of done
- One coherent why-capture, gauge-read, and trip-policy loop is implemented and validated independently.
- Future HITL writer and refresh work remains nonbinding until entry evidence supports launch.

## Good-enough boundary and appetite
- Mandatory quality: Preserve the confirmed governor interfaces, human boundaries, and fail-safe missing-gauge behavior.
- Sufficient evidence: Each current issue has independently observable public-interface acceptance evidence.
- Appetite: Three independently testable AFK issues in one initial execution-and-validation loop.

## Hard constraints and fixed decisions
### Hard constraints
- Historical design and issue-set inputs are read-only and hash-pinned.
- No live tracker, GitHub, subprocess, or network write is permitted in the demonstration.
### Fixed decisions
- One engine-native refresh-request mechanism serves every tier.
- Gauge failures collapse to None and never force a handoff.
- SOFT is advisory; HARD requires a refresh request at gate boundaries only.

## Current wave
Objective: Complete one coherent why-capture, gauge-read, and trip-policy execution-and-validation loop.
### Exit criteria
- Why-capture, gauge-reader, and trip-policy acceptance evidence is independently observable.
- The loop preserves the frozen design's fail-safe and human-authority boundaries.
### Runnable issues
- [ ] **[AFK]** CG-A: Why-capture + refresh primitives: engine schema (checklist_engine.py)
- [ ] **[AFK]** CG-C: Gauge reader: plain read() -> Reading|None + model-keyed thresholds
- [ ] **[AFK]** CG-D: Trip: two-band gate policy (SOFT stop-question + HARD refuse-advance)

## Wave forecast (nonbinding)
- **Gauge writer: Claude Code PostToolUse hook + golden-sample fixture** — Original B remains useful after the AFK loop but needs its stated HITL entry evidence.
- **Refresh: reach-up relaunch flow + job-file principle (skill/doctrine wiring)** — Original E remains useful after the AFK loop but needs its stated HITL entry evidence.

## Active uncertainty register
- **Whether the Claude Code gauge estimate is accurate at trip thresholds** — affects Writer calibration and threshold selection; next probe: Compare a golden transcript estimate with live harness accounting

## Parked possibilities
- Codex/pi gauge writers
- Pre-emptive handoff at named gates
- Self-calibrating thresholds
