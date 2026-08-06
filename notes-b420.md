# Working notes — cmdr-420-engine-channel

Sole writer: this Commander. Not a deliverable; scratch trail for my own run.

## Plan-approval rigor mechanisms (commander-core.md, plan step)

**Plan-alternatives (design-it-twice, plan phase).** Not re-run as a fresh parallel fan-out this run.
`DESIGN_SPEC.md` workstream B already states, and Tommy approved 2026-08-03: "Design-it-twice:
skipped as trivial, with the reason stated. Both changes correct how an existing projection
renders, and neither adds a new interface surface... These changes make the code meet [the existing
`current`-is-complete-channel contract]." Per-section approval: APPROVED — Tommy, 2026-08-03. I am
citing that prior, human-approved skip rather than re-litigating it — the launch order's Pre-empted
Steps section says the latitude contract is confirmed and context is established; re-running
plan-alternatives on a decision the human already closed at the spec level would be exactly the
kind of scope growth the launch order's scope-discipline ruling tells me not to do. Untaken road:
recorded here, surfaced at the plan-approved checkpoint below.

**Cold plan critic.** This IS run this wave (a distinct mechanism from design-it-twice; not
pre-discharged by the spec's skip). Panel-vs-single: single critic, Sonnet tier, because this is a
"fairly-easy call" by weight — one file, no new interface, no architecture touch — not a "when in
doubt, panel" case. Dispatched via Agent tool, `subagent_type: general-purpose`, `model: sonnet`,
given only the mission frame + execute.json + the actual code regions + doctrine tests, no authoring
context.

**Critic verdict (would-not-approve-as-is, 3 blockers) — all addressed in this execute.json before
plan approval:**

1. **BLOCKER, real and correct — plan revised.** My first RAIL-fix sketch ("point at the imperative
   with a short pointer") was verb-blind. `_rail_prefix()`/`_rail()` fire for all 6 `RAIL_VERBS`
   (claim/current/start/advance/attest/attach), and `_rail_position()`'s mid-flight branch derives
   its substitution purely from spine state, not from which verb triggered it. For 5 of those 6
   verbs the RAIL is the ONLY place the next imperative appears (no ACTIVE line exists in their
   output) — a pointer like "the ACTIVE gate above" would be FALSE there. The actual 2x duplication
   (per issue #420 and DESIGN_SPEC.md, both scoped explicitly to "every `current` call") only exists
   on the `current` verb. Fix revised to be verb-aware: dedup only when `point == 'current'`; the
   other 5 verbs keep the full imperative unchanged. Constraints in g1-implement/g1-review rewritten
   to state this explicitly and require a sibling test proving non-current verbs are unaffected.
2. **BLOCKER, correct, expected consequence not an oversight.** `DoctrineRail.test_rail_mid_flight`
   pins the OLD (buggy, duplicating) substitution for `_rail('current', cl)`. That test targets
   exactly the bug being fixed, so it is *supposed* to change as part of this fix — I've made that
   explicit in g1-implement's constraints (update it; add the sibling non-current assertion) so the
   implementer doesn't read "frozen rail strings" doctrine as "don't touch this test."
3. **BLOCKER, verified against the source, real defect (separate from my plan).** My plan had cited
   `tests/test_checklist_engine.py:818` as the byte-exact ACTIVE-line pin, copied from
   `render_human()`'s own docstring at `checklist_engine.py:1591`. Read line 818 directly: it's
   `E.require_session(cl, "start", None, {})` in an unrelated lease test, not a rendering pin. The
   real byte-exact pins are the `GoldenOutputBriefing` class (~line 3738 on, e.g.
   `test_pending_active_task_shows_open_preconditions_and_next_start` ~3746), which call
   `E.current(cl)` directly (the pure function, pre-RAIL) — so they're unaffected by the RAIL fix
   but must be extended, not broken, by the anchors/constraints rendering change. Citation fixed in
   execute.json; the stale docstring citation itself is flagged to the implementer as
   fix-if-convenient-else-triage (cosmetic, not blocking).

Minor findings (imprecise line-number spread for the RAIL region, a slightly ambiguous fence
wording around `_RAIL_STRINGS`) — folded into the tightened anchors/constraints text directly
rather than tracked separately; both were wording precision, not substance.

## Baseline (pre-fix, this worktree, this session)

- `python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q` → 388 passed, 24
  subtests passed, ~15s.
- `python -m pytest tests/ -q` (full suite, run once for a broader-suite green baseline per
  `docs/agents/ORCHESTRATOR_CONTEXT.md`'s "targeted automated verification plus the relevant broader
  suite") → 1621 passed, 2 skipped, 550 subtests passed, ~473s (0:07:52). Not re-run as a gate
  postcondition (too slow for a per-advance command check); re-run once more at review/archive to
  confirm the fix didn't regress anything outside the targeted files.
- Windows note: this worktree's `py` launcher resolves to an interpreter with NO `pytest` installed
  (`No module named pytest`). `python` resolves to one with pytest 9.0.2. Use `python -m pytest`,
  not `py -m pytest`, for every test command in this run — logging as workflow feedback, since the
  launch order's `_COMMON.md` platform invariants say "both `py` and `python` work," which was not
  true for pytest specifically on this worktree.
