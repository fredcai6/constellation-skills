# RESULT — epic-569 w2-ledger (#557 wave 2)

## Verdict

**Shipped, live (not report-only except where named).** Three genuine engine-authority-bypass
paths — `waive`, forced claim/release, and the trip ledger — now share one engine-written,
append-only home (`override_ledger`), reachable only from the `dispatch()` chokepoint, provably
(AST-based call-graph test, not asserted). Both #503 defects in `waive()` are fixed. Closeout
visibly renders the ledger, both immediately (`finish_work`'s return, all four return points) and
durably (the persisted episode text). #259 closes on evidence: the census shows the opposite of its
premise, and `consolidate --override-reason` is deliberately excluded from the unification as a
structurally different thing (a survey-verdict annotation, not a gate-authority bypass) — an
**Honest-Null** outcome the launch order named as an acceptable result. `amend`'s authority
handling was reviewed and found to need no fix.

## Alternatives pass and why the loser lost

Two real, independently-dispatched candidates (design-it-twice, N=2, "fairly-easy call" per the
brief): **smallest-diff** (reuse `trip_ledger`'s name in place, widen `_append_trip_entry`) vs.
**best-seam-placement** (retire `trip_ledger` as a write target, introduce `override_ledger` with a
`kind` discriminant, backward-compat via one merge-reading function). **Hybrid won, not a pure
pick**: took best-seam-placement's schema (the more honest name once the container holds
waive/claim/release entries too — both candidates independently converged on the same
direct-call-vs-dispatch-call chokepoint-proof test pattern, which gave confidence the rename was
executable safely) plus smallest-diff's `waive()` fix shape (both candidates converged on this
independently too — the strongest signal in either document). smallest-diff's literal G5 (a
`finish_work` snippet reading raw `trip_ledger`/`outcome`) was dropped as written — a cold critic
caught that it would silently break under the winning schema (Finding 2) — and replaced with a
version reading through the winning schema's own `override_summary`. best-seam-placement's own G5
(relocating `amend`'s audit write to the dispatch chokepoint "for consistency") was explicitly
dropped as a named untaken road: no payoff for #503/#504/the ledger-unification goal, since `amend`
was never going to join the unified ledger either way. Full record: `PLAN_ALTERNATIVES.md`.

## Evidence

- **Red-proof, pinned to shipped SHA `0427898a`** (`RED_PROOF.md`): on base `9d5aac6d`, waiving a
  condition declaring `override_policy.authority: "human"` with `--authority commander` produces
  `produced_by: "human"` (hardcoded, wrong) and no mismatch record at all. On the shipped SHA, the
  same repro produces `produced_by: "commander"` (correct) plus `authority_mismatch: true,
  expected_authority: "human"` — and `waive` still succeeds (report-only, never refuses).
- **Chokepoint proof**: `tests/test_checklist_engine.py::test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`
  (AST-based, asserts the exact caller graph) plus
  `test_dispatch_call_records_waive_claim_release_direct_call_does_not` (drives the CLI path and
  gets ledger writes; calls the bare verb functions directly and gets none).
- **Closeout-render proof**: `tests/test_spine_lifecycle.py::TestFinishWorkOverrides` (all 4 return
  points); `tests/test_episode_store.py::OverridesPersistenceTests` +
  `EpisodeOverridesRoundTripTests` (the durable half — actually reads the persisted `.md` file from
  disk, not just an in-memory object).
- **#259 census**: `notes-w2b.md` — 117-file archive grep, extensive sanctioned use.
- Full local suite (real gate; CI here is Windows-only and known-red): **3660 passed, 6 skipped, 0
  failed**, up from the launch order's stated baseline of 3622 passed, 6 skipped at base `9d5aac6d`
  — net +38 from new coverage across g1-g3, zero regressions, zero net loss.

## Where new checks run, and proof they can fail there

- The AST chokepoint test and the direct-call-vs-dispatch-call test both live in
  `tests/test_checklist_engine.py`, run by `pytest tests/` (the real local gate). Proven to fail: a
  hand-run mutation (temporarily adding a direct `_append_override_entry` call inside `waive()`'s
  own body during g2's review) was independently reproduced by the reviewer crew as part of its
  Fowler pass; the shipped code has no such call.
- `_validate_create`'s new `overrides` shape check (`scripts/apply_episode_delta.py`) is exercised
  by `tests/test_episode_store.py::OverridesMechanicalFieldTests::test_non_dict_overrides_value_rejected`
  — passing a non-dict `overrides` value raises `EpisodeDeltaError`, proven to fail on a bad input.
- The round-trip invariant (`render_episode(parse_episode(text)) == text`) is exercised by
  `EpisodeOverridesRoundTripTests` for both the overrides-present and overrides-absent cases.

## PR and full local suite

Branch `epic-569/w2-ledger`, 5 commits on top of base `9d5aac6d`: `2895dc8b` (g1), `87ea0655` (g2),
`7627d381` (g3), `0427898a` (g4). PR against `main` referencing epic #569: **opened at archive**, via
`spine_close`'s `push`/`open_pr` — see the archive step's own record for the number. Full local
suite at close: **3660 passed, 6 skipped, 0 failed** (`python -m pytest -q`).

## Map impact

No packet map exists for this repo (`docs/architecture` DEGRADED-UNPARSEABLE, confirmed at the
context step and discharged with hash-pinned substitutes — `.agent-work/w2-ledger/map-orientation.json`).
Reconciled the structural record directly instead of dispatching Cartographer: `docs/CHECKLIST_SCHEMA.md`
already carries the full `override_ledger` schema, its `kind` table, the migration contract, the
`produced_by`/`authority_mismatch`/promotion-trigger paragraph, and the #259/`amend` closing notes —
each landed in the same commit as the code it describes, not a follow-up. `map/INDEX.md` rebuilt
and committed (g3) after the new symbols.

**Separately, out of this issue's scope**: `docs/architecture/generated/map.json` (parses but
`nodes[]` carry no `id`) and `map/INDEX.md`'s citable-anchor format are stale/broken repo-wide, a
pre-existing condition this run did not cause and has no mandate to fix. Flagged as a triage
candidate for whoever owns the map generator next.

## Triage candidates

**Fixed, not filed** (this run's standing preference: fix or write an episode over filing) — every
finding from the cold plan critic's 10 items and both implementers' out-of-scope observations was
either fixed inline this run or explicitly, reasonedly dropped as a named untaken road (see
`PLAN_CRITIC.md`'s Commander triage table). Nothing from `execute.json`'s own `triage_candidates`
array required routing — it is empty.

**Recorded as evidence, not filed** (in `REPLAN_INPUT.json`'s `discrepancies`, per the execute
directive's explicit "discrepancies remain evidence and MUST NOT be auto-filed as issues"):
- `dc1-spine-null-dispatch`: every `run_crew.py` `cli`-backend implementer/reviewer dispatch this
  run made (7 crews) inherited the dispatching Commander's own `SPINE_FILE`/`SPINE_SESSION` rather
  than a fresh door of its own (`crew-runs.json` records `spine: null` on all 7). Every crew
  self-corrected (authored and drove its own local plan/survey via the CLI, never touching the
  Commander's spine) — no bad state resulted, so this did not block the run, but it is a real,
  reproducible dispatch-mechanism gap outside this lane's fenced surface (`scripts/run_crew.py`'s
  env wiring / the implementer & reviewer skills' opening engine-drive instructions). **Recommend
  to the Admiral**: worth a dedicated fix, since 7-for-7 crews hitting the identical gap and
  self-correcting via tribal knowledge (each one's own Workflow Feedback names it independently) is
  a strong signal, not a one-off.
- `dc2-missing-return-status-field`: two IMPLEMENTER_RESULT documents (`g3-implement` attempts 1
  and 2) omitted the required `## Return status` line despite unambiguous, complete content; the
  independently-dispatched reviewer agreed with the Commander's `complete` reading in both cases.
  Minor template-compliance gap, not run-blocking.
- The stale/broken architecture map (above) — out of scope, pre-existing, named for whoever owns
  `docs/architecture/generated/map.json`'s generator next.

**#259 (GitHub)**: commented, not closed — the issue bundles an unrelated, still-open item (a
`git checkout`-based perturb-restore data-loss hazard in reviewer doctrine) outside this mission's
scope. See https://github.com/fredcai6/constellation-skills/issues/259#issuecomment-5382193485.

## Workflow feedback, including where this order was underspecified

- **The four-path framing needed a census before it could be trusted, and the order said so
  correctly.** The launch order's own settle instruction for #259 ("grep the archive... zero real
  uses means delete") was exactly right, and running it early (at `understand`) reshaped the whole
  plan's scope from "unify four paths" to "unify three, document why the fourth stays out." A
  well-specified order that says "go measure, don't guess" did take real judgment off this agent's
  plate — the census methodology was named, not the conclusion.
- **Where this order was underspecified**: it did not anticipate that unifying the ledger's storage
  key would collide with ~35 existing tests that pinned the OLD key directly
  (`cl["trip_ledger"][0]`-style assertions). The first g1-implement attempt correctly stopped
  (returned `blocked`) rather than silently reinterpreting "passes unmodified," and the Commander
  had to make an explicit in-latitude call (implementation shape: "unmodified" means observable
  *behavior*, not literal storage-key text) before rework could proceed. A launch order authoring a
  ledger-rename plan should name this class of risk explicitly next time: "check whether the
  existing test suite pins the storage shape you're about to move, not just the storage's
  *behavior*."
- **Also underspecified**: the launch order's `decision:closeout-must-render-it` said rendering
  "is part of the deliverable, not a follow-up" but did not anticipate that "render" has two
  distinct senses (immediate return vs. durable persisted record), and that satisfying one without
  the other is a plausible, easy-to-miss partial completion. The first g3-implement attempt did
  exactly this (wired both `mechanical_fields` validation AND `finish_work`'s return, but the
  durable half silently dropped the value before it reached disk) and correctly flagged its own gap
  as an out-of-scope observation rather than claiming full compliance — that self-report is what
  let the Commander catch and close it in a rework pass before this gate could close. Worth naming
  explicitly in future closeout-rendering orders: "render" implies both the immediate signal and
  survives to the durable record, and both need their own round-trip test.
- **`run_crew.py`'s `cli`-backend env-inheritance gap** (see `dc1` above) is a workflow-mechanism
  observation, not a content gap in this order — but it means every crew dispatch this run made had
  to spend part of its own turn rediscovering and working around the same gap independently, which
  is real, avoidable overhead across 7 dispatches.
- **Model tier**: sonnet handled this correctly end to end, including two genuine rework cycles
  (g1's storage-key conflict, g3's persistence gap) where the model had to recognize a real
  handoff-content conflict and stop rather than guess past it — both stops were correct calls, not
  under-capability. This supports the epic's thesis: a well-specified launch order let sonnet do
  real engine-internals work, including judgment calls about when a handoff itself was wrong.
- **This session never received a `SendMessage` from any of the 7 dispatched crews** despite each
  handoff instructing it as a best-effort courtesy ping — consistent with the doctrine's own
  warning that this is non-load-bearing; every result was correctly found via the result-artifact
  path instead, with zero impact on the run.
