# Excursion handoff: exc-6-governor-prototype (PROTOTYPE_HANDOFF)

Full brief: `### EXCURSION_BRIEF exc-6-governor-prototype` in `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/IDEAS_BOARD.md` — read it first. Load the **constellation-prototyper** skill and drive its workflow; this file carries the PROTOTYPE_HANDOFF fields.

## Question
Can the context governor track a dispatched subagent's engine work under the subagent's OWN identity — the prototype agent creates its own subagents whose activity is gauged separately (not accumulated onto the parent's binding), with terminal work releasing its binding — or is the fix pernicious as suspected?

Background you must read first (the measured failure this prototypes against):
- Issue #383: subagents share the parent session id; every crew claim adds a binding; terminal spines never release; 30 bindings accumulated; the gauge produced ZERO readings across a multi-day run.
- Issue #271/#287 (adjacent shapes), #284 (cost: four commanders past the HARD band, one at 2.4x).
- Relevant code: `scripts/checklist_engine.py` (`_gauge_path` and lease/session handling), `scripts/hooks/spine_rail.py`, gauge writer hook docs at `docs/GAUGE_WRITER_HOOK.md`.

## Branch
logic

**Why this branch:** pure mechanism behavior — runtime identity and file routing; no UI, no measurement apparatus.

## Host-project conventions
- **Runtime / language:** Python 3.12
- **Task runner:** run tests as `python -m pytest` (NOT `py -m pytest` — the `py` launcher resolves to a pytest-less runtime, issue #313)
- **Routing:** n/a
- **Other conventions:** engine + hooks under `scripts/`; work areas under `.agent-work/<work-id>/`

## Location
worktree

**Driver:** agent-driven → throwaway worktree. Create it yourself (git worktree off main), name it clearly as a prototype, and dispose per prototyper doctrine when done.

## Stop conditions
- "Answered" = a live demonstration in the worktree that a spawned subagent's engine activity lands under its own binding/gauge while the parent's binding stays clean AND a terminal spine releases its binding — or a scoped statement of exactly where separation breaks and why (which is a full answer too: "pernicious, here is the wall").
- The demonstration must include you actually creating subagents (Agent tool, model sonnet or lower) that drive engine calls in the worktree — separate tracking must be shown live, not argued.
- Budget: ~3 mechanism variants, then report back even if inconclusive. Scoped nulls: state what was and was NOT tested.
- Exclusions: do NOT modify `C:/Users/fredc/.claude/settings.json` (the human's file); do NOT wire hooks globally; do NOT land anything on main. Everything stays in the throwaway worktree except the result file.

## Return format
`PROTOTYPE_RESULT` written to `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/evidence/exc-6-governor-prototype-RESULT.md` (this path is in the main checkout, not your worktree): the answer, what was tested and what was NOT tested, what it taught, any surviving module worth keeping, and the disposition of the worktree. Your final return message: one verdict line + the artifact path.
