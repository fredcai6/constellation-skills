# Mission Frame

Shrunk per template guidance: this is a small, local, mechanical wording change (rewrite
2-3 fixed strings in one function/dict in one module, plus their pinned test literals) with a
measurement component. The map is DEGRADED-UNPARSEABLE in this worktree (`map/ids.jsonl` empty,
`map/INDEX.md` per-package pages absent on disk — Admiral-owned, not regenerated this wave per
the launch order's map-index-is-admiral-owned ruling) and carries no entry for
`scripts/checklist_engine.py` regardless, so it adds nothing this run could have used. The frame
below is built from the declared DEGRADED substitutes (`docs/agents/ORCHESTRATOR_CONTEXT.md`,
`.agent-work/567-h/LAUNCH_ORDER.md`) plus a direct source read of the target module, per the
context step's discharge receipt (`.agent-work/567-h/map-orientation.json`).

## Intent

Rewrite the RAIL "early" banner and the HARD-refusal remedy text in
`scripts/checklist_engine.py` (issue #442) so a cold agent — no corpus, shown only the rail
line and a HARD refusal — reads them as legitimate workflow-engine output and can state and
perform what they ask, instead of discounting them as a possible prompt injection. Measure with
real fresh agents before and after, per the launch order's Honest-Null Clause.

## Affected Capabilities

- The engine doctrine-rail mechanism (`_rail`/`_rail_position`/`_RAIL_STRINGS`,
  `scripts/checklist_engine.py:443-531`): appends a fixed doctrine string to railed-verb output
  at five decision points. This run touches only the `"early"` entry's text, not the mechanism.
- The HARD-band begin-work refusal (`_trip_hard_gate`, `scripts/checklist_engine.py:2144-2228`)
  and its remedy-command builder (`_refresh_attach_hint`, `scripts/checklist_engine.py:1680-1692`):
  refuses `start`/`reopen` over the hard line with no pending refresh-request, naming the exact
  `attach ... --type refresh-request` command to run instead. This run touches the wrapping
  sentence's wording and/or the remedy template's wording, not the refusal logic or the command's
  functional arguments.

## Structural Anchors

- `scripts/checklist_engine.py:459-475` — `_RAIL_STRINGS` dict, the `"early"` key is #442's
  first target.
- `scripts/checklist_engine.py:1680-1692` — `_refresh_attach_hint`, #442's second target.
- `scripts/checklist_engine.py:2224-2228` — the `_trip_hard_gate` `EngineError` raise text, the
  actual message a cold agent sees when refused; candidate third target if the wrapping sentence
  (not just the embedded command) is where the injection-read lives.
- `tests/test_checklist_engine.py` — pins these strings verbatim in multiple places (lines
  ~1934, ~3872-3877, ~6718-6737 at time of read); every rewrite must update its matching
  assertion in the same gate.
- `docs/CHECKLIST_ENGINE_DESIGN.md:117-136` — the design doc's own description of the rail table
  and the "frozen, verbatim... measurement precondition for #145" comment.

## Governing Constraints / Assumptions

- The file's own comment (`scripts/checklist_engine.py:451-455`) calls the five `_RAIL_STRINGS`
  values "FROZEN and verbatim (measurement precondition for #145)". The launch order's ruling
  (frozen-strings-may-change-but-not-silently) permits rewriting them, conditioned on stating
  exactly what changed and why #145 survives it — settled at `understand` (see the attached
  user-decision evidence: issue #145 is a COMPLETE, revision-pinned historical measurement,
  `.agent-work/archive/2026-07-12-epic-138-workarea/verdicts/commander-145.md`; editing today's
  text does not retroact on what that record measured at its own commit).
- Dogfooding hazard (`docs/agents/ORCHESTRATOR_CONTEXT.md` "Dogfooding" section): hooks execute
  from the MAIN checkout regardless of worktree, so an in-session observation of engine/hook
  behavior after editing `checklist_engine.py` is not evidence. Any validation of the rewritten
  strings' actual runtime output must run in a fresh subprocess against explicit paths (this
  worktree's own copy invoked directly, not through a hook).
- `RAIL_VERBS = {"claim", "current", "start", "advance", "attest", "attach"}` — the rail fires on
  these six verbs only; the cold-agent measurement should present the strings exactly as one of
  these verbs would emit them (with the `RAIL: ` prefix `_rail()` always adds), not paraphrased.

## Decision Anchors & Decision Pressure

- The launch order's frozen-strings-may-change-but-not-silently ruling — strings may be
  rewritten if the change and its survival of the #145 precondition are stated in the return.
  @grade: settled/human · leans g2-implement,g2-review
- The launch order's honest-null-is-complete ruling — a measured negative (current wording
  already reads fine to a cold agent) is a complete deliverable.
  @grade: settled/human · leans g1-measure,g3-measure
- decision pressure: whether the third candidate string (the `_trip_hard_gate` wrapping
  sentence) is in scope, or only the two named in Lane C's prior-wave return — resolved at plan
  time below by treating it as in-scope-if-the-baseline-measurement-implicates-it, since I am
  sole writer of the whole file this wave and #442's stated target ("the RAIL banner and its
  HARD refusal remedy") is the message an agent actually receives, which is the wrapping
  sentence plus the embedded command together.

## Claims / Evidence Surfaces

- Claim: current wording of the RAIL early banner and/or the HARD refusal message causes a cold
  agent to misread it as a possible prompt injection and discount the instruction — checked by
  dispatching genuinely fresh subagents (no shared context, no corpus) with only the exact
  engine-emitted text and observing whether they state the correct ask and perform it.
- Claim: any rewrite preserves the mechanism's function — checked by the pinned unit tests
  (updated to the new literals) plus a fresh-process CLI invocation of the rewritten engine
  copy, plus the full suite green in a clean detached worktree.

## Map Confidence / Staleness / Disputes

- The map is DEGRADED-UNPARSEABLE for this whole worktree (see Intent). No map area is
  "low-confidence" for this specific target — there is no map entry for it at all, positive or
  negative — so nothing here is silently trusted from a stale map; the frame is built from a
  direct source read instead, per the context step's discharge.

## Out of Scope

- The other four `_RAIL_STRINGS` positions (`mid-flight`, `near-terminal`, `terminal`,
  `check-failure`) and the SOFT `_trip_advisory` wording — Lane C's prior-wave return recorded
  these as adjacent-but-unedited; #442 names only the early banner and the HARD refusal remedy.
- Reopening #595's context-trip-vs-Stop-hook precedence — settled by Lane C, forbidden to
  relitigate per the launch order's Inherited Latitude table.
- `map/INDEX.md` regeneration — Admiral-owned this wave.
- Any promotion of an observation into `docs/agents/*` — human's call, forbidden this run.
