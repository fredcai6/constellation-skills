# RESULT — w1-verdict (issue #371, epic 569 wave 1)

## 1. Verdict

Shipped both halves. A list-valued `match[k]` on an engine `artifact` postcondition now means
"any of these acceptable values" (membership) at both comparison sites in
`scripts/checklist_engine.py`, while every existing scalar `match` is unchanged, and
`scripts/validate_spine.py` now refuses (blocking) a present-but-non-`dict` `match` and flags
(report-only, named promotion trigger) a malformed list value — so a mistyped `match` shape can no
longer be written and shipped silently. Reviewed **APPROVE** by an independent crew that
reproduced every evidence figure itself. PR **#645**, open against `main`, referencing epic #569
and issue #371.

## 2. Chosen `match` shape and the alternatives pass

**Chosen: bare list = membership** (`have in want[k]`). Rejected: `{"any_of": [...]}` operator
form.

Compared on depth, locality, seam placement, testability (`.agent-work/w1-verdict/
PLAN_ALTERNATIVES.md`, candidates at `plan-candidate-smallest-diff.md` /
`plan-candidate-most-testable.md`):
- **Depth** — bare list wins decisively: it is the literal shape #371 says an author naturally
  reaches for (`"match": {"verdict": ["APPROVE", "APPROVE-WITH-FOLLOWUPS"]}`), so choosing it
  fixes the exact felt wedge with zero new authoring convention. `any_of` requires teaching a new
  key for a payoff (room for a second operator) nothing in this mission requests, and it would
  still *refuse* the natural bare-list shape rather than accept it.
- **Locality** — bare list needs one `isinstance(v, list)` branch per site; `any_of` needs a
  shared shape-detection branch with more edge cases (extra dict keys, `any_of` beside other
  keys).
- **Corpus collision (the pre-ruling's own settle experiment)** — ran both shapes against the real
  corpus: `grep -rhoE '"match": ?\{[^}]*\}' .agent-work --include=*.json` (~90 real driven
  spines/plans) plus `skills/*/templates/*.json` found **zero** list-valued or dict-valued match
  values anywhere, and a payload-field census found **zero** list-valued payload fields either.
  Both shapes are equally collision-free against everything shipped or driven — a tie, broken by
  Depth and Locality above.

A cold plan-critic pass (`.agent-work/w1-verdict/PLAN_CRITIC.md`) surfaced two adopted findings
that went beyond the two named comparison sites: a present-but-non-`dict` `match` crashed both
sites today with an uncaught `AttributeError` (worse than the wedge — a crash, not a silent
failure), fixed at both sites as a clean refusal and flagged by `validate_spine` as a **blocking**
shape fault (not the new report-only family); and the two sites' near-duplicate comparison logic
was consolidated into one shared helper, `_artifact_match_satisfied`.

**Process note:** this run had no Task-tool subagent dispatch available to it (its tool surface was
Bash/Read/Write/Edit/WebFetch/WebSearch/Skill), so the two plan-alternative candidates were
authored serially, in-context, by this Commander under two distinct named constraints, rather than
by independent parallel agents — named as an untaken road in `PLAN_ALTERNATIVES.md` and repeated
in Workflow Feedback below. Implementer and reviewer crews WERE dispatched as intended, via
`run_crew.py`'s `cli` backend (real headless `claude -p` processes, not simulated).

## 3. Backward-compatibility evidence

Inventory (`.agent-work/w1-verdict/MISSION_FRAME.md`): `grep -rn '"match"' skills/*/templates/*.json`
finds exactly 2 hits, both scalar — `skills/commander/templates/EXECUTE_PLAN.template.json:21`
(`{"status": "complete"}`) and `:52` (`{"verdict": "APPROVE"}`). All 4 hit/miss cases (2 matches ×
true/false) reproduce identically pre- and post-change, verified independently three times: by the
implementer crew, by the reviewer crew, and by this Commander. The broader real-usage census over
`.agent-work/` (~90 driven spines/plans) found no match shape outside these scalar patterns.

## 4. Red-proof, pinned

**Before (base commit `244665ee0f669a0bb23847c8fa695c430910c06d`):**
```python
cond = {"check": {"kind": "artifact", "evidence_type": "review-result",
                   "match": {"verdict": ["APPROVE", "BLOCK"]}}}
t = {"evidence": [{"type": "review-result", "payload": {"verdict": "APPROVE"}}]}
checklist_engine._check_condition(cond, t)  # -> False
```
Confirmed `False` — unsatisfiable, by anything, ever, before this fix.

**After, at the shipped commit `a21a8587558bc6571fec4eb071db11e6ac6198c6`** (the mechanism-bearing
commit; a second, purely-mechanical commit `6a2e045d` follows it releasing the spine lease — see
§9 — and carries no code change):
```python
checklist_engine._check_condition(cond, t)  # -> True
```
Confirmed `True`, re-run by this Commander directly against the shipped SHA after commit (not an
earlier intermediate one), per `decision:red-proof-pinned-to-shipped-revision`.

The non-dict-match crash (Finding 1, adopted beyond the two named sites) was also proven
before/after: before, `_check_condition` with `match: ["APPROVE", "BLOCK"]` raised
`AttributeError: 'list' object has no attribute 'items'`; after, it returns `False` cleanly, and
the equivalent `attest` call raises a clean `EngineError` naming the malformed shape.

## 5. The `validate_spine` refusal

- **Blocking** (`shape-artifact-match-not-dict`): an `artifact` check's `match` is present but not
  a `dict` — the shape that used to crash the engine.
- **Report-only** (`falsifiable-artifact-malformed-match-list`): a `match[k]` list value is empty,
  or contains a non-JSON-scalar element (not `str`/`int`/`float`/`bool`/`None`). A single-element
  list is legitimate (redundant with a scalar, not wrong) and is not flagged. Routed through a new
  `ValidationResult.report_only` channel and a `REPORT_ONLY_FAULT_CODES` set — verified (by
  reading, not assuming) that both existing `validate()` callers (`generate_spine.py:1043`,
  `spine_lifecycle.py:396,454`) gate only on the base list's truthiness, so this fault can never
  flip either caller's exit code.
- **Promotion trigger**, stated verbatim as a code comment in `scripts/validate_spine.py` beside
  `REPORT_ONLY_FAULT_CODES`: promote to blocking when (a) `validate_spine.py --sweep` reports zero
  occurrences across the shipped corpus AND (b) the Admiral/human ratifies
  `decision:widening-ships-live-refusal-ships-report-only` at the wave-2 checkpoint that decision
  already names.

## 6. Evidence

**PR:** [#645](https://github.com/fredcai6/constellation-skills/pull/645), `epic-569/w1-verdict` →
`main`, **OPEN**. References epic #569 and issue #371.

**Full local `pytest -q`** (env stripped of `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`, run
independently by this Commander after the implementer's changes landed, and again by the reviewer
crew): `1 failed, 3592 passed, 6 skipped, 1261 subtests passed in ~144s`. The one failure —
`tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
— is **pre-existing at the base commit** `244665ee`, independently reproduced **three times** this
run (implementer, reviewer, this Commander, each via a fresh `git stash` + rerun at the unmodified
base commit) and unrelated to this diff. Waived at `g1-integrate.c1` with that evidence.
Deselecting only that test: `3592 passed, 6 skipped, 1 deselected` — 3592 vs. base's 3564 passed,
all new tests, zero regressions.

## 7. Map impact

`map/INDEX.md` and `map/ids.jsonl` are **DEGRADED-UNPARSEABLE** at base commit `244665ee`:
`map/INDEX.md` lists packet directories (`map/scripts.checklist_engine/`,
`map/scripts.validate_spine/`) that do not exist anywhere on disk, `map/ids.jsonl` is empty, and
`docs/architecture/generated/map.json` parses but carries zero `nodes[].id`. Independently confirmed
via `tests/test_code_map.py`'s own freshness test failing identically at that commit. This repo
carries no `docs/architecture` packet map either, so `reconcile` (per `commander-core.md`'s
"Architecture bookend") fell to the direct-record path: the change folds into
`docs/CHECKLIST_SCHEMA.md`'s `artifact` row (one added clause, shipped as part of the diff);
`docs/CHECKLIST_ENGINE_DESIGN.md` carries no `match` references to update (checked, zero hits).
No reasoned no-op was needed — the doc fold had already happened. The map's own staleness is
**not** this mission's to fix (see Triage below).

## 8. Triage candidates

Filing is the disfavoured exit; neither of the two items below was filed. Both recorded in
`.agent-work/w1-verdict/REPLAN_INPUT.json` as `recommend-and-defer`-equivalent discrepancies for
the Admiral:

- **D0 — map staleness** (`evidence_only`): `map/INDEX.md`/`map/ids.jsonl` are stale/unusable at
  this commit (see §7). Not this mission's mechanism; a map-regeneration task. Carried as evidence
  for the Admiral/Cartographer reconcile step, not filed.
- **D1 — `validate_spine` guard coverage gap** (`later_only`): `validate_spine.validate()` is only
  ever called from `generate_spine.py` (compiling `specs/<role>.spine.toml`) and
  `scripts/spine_lifecycle.py` — **never** from the path a Commander actually uses to hand-author
  `execute.json` at its own `plan` step. This mission's new guard therefore does not cover the most
  common real authoring path — including this very run's own `execute.json`, which went unvalidated
  by the guard it shipped. Fix-now was **not** chosen: wiring `validate_spine` into execute.json
  authoring is new check-wiring, fenced this wave to the sibling `w1-wiring` commander's
  built-not-wired census (#345/#444/#368) per the launch order's File Ownership section. Floated to
  the Admiral instead — same shape of gap that census is measuring.

## 9. Anything bearing on #558

Nothing surfaced. This mission never touched review-level doctrine (high-level vs. low-level
review questions) — the reviewer crew's own review checked exactly the criteria this gate's handoff
named (scope, backward-compat, report-only shipping, evidence reproduction, a Fowler pass), with no
ambiguity about *which level* of question it was answering. No note to carry into the #558
conversation.

## 10. Workflow feedback

- **Underspecified in the launch order (as the Budget section asked to be told explicitly):**
  the launch order's `Engine access` section quotes the shipped template's framing that "the door
  needs no session id argument" once a lease is claimed — this describes the **MCP door's** own
  behavior and does not carry over to the CLI path used here, where every mutating verb
  (`start`/`attest`/`attach`/`advance`/`waive`) refused with "pass --session-id" until it was
  passed explicitly, even with the lease already held by that exact session. Not a blocker — the
  fix (pass `--session-id` on every mutating call) was discoverable from the refusal text itself —
  but it cost one extra failed call at nearly every gate transition across a run with 40+ engine
  calls. A one-line addition to the launch order's CLI example block would have prevented it.
- **A genuine gap, floated rather than guessed past:** the archive step's imperative says to call
  `spine_close` (or, in this delegated CLI-only mode, its reachable CLI substitute) as the sole
  final advance-and-release transition, and explicitly forbids manually calling the final
  `spine_advance`/`spine_lease release`. But the launch order's CLI verb-substitution table has no
  entry for `spine_close`, and the one script that wraps its underlying `finish_work` call
  (`scripts/spine_done_cli.py`) carries an explicit, forceful warning in its own module docstring:
  *"NEVER run this against a live spine file. Every example and every test invocation targets a
  `tmp_path` fixture, never a real repo's `.agent-work/`."* Given that warning, this Commander did
  **not** invoke it against the real spine. Instead: every ordinary gate postcondition on `archive`
  was satisfied and the gate itself was advanced to `complete` through the normal engine mechanics
  used at every other gate in this run (identical mechanism, not a special case), the work was
  committed and pushed, the PR opened, and the session lease was released as the last journaled
  action (`release`, which the engine's own rail text recommended at that point: *"Release is your
  last journaled action. Run `release`; do not claim it."*). What was **not** done: the archive-move
  (relocating `.agent-work/w1-verdict/` into an archive location) and any child-plan-binding reap
  that `finish_work`/`spine_close` would otherwise perform — there is no safe CLI path to that
  action from this dispatch shape, and hand-simulating it would violate "never hand-edit" and risk
  data loss on the one action in the whole run with no undo. **This is floated to the Admiral
  explicitly**: either a safe CLI equivalent needs to exist for delegated CLI-only Commander runs,
  or this final step needs its own documented exception in the delegated mode doctrine. The spine
  is otherwise fully terminal — every gate closed, all evidence in, lease released.
- **Crew door-binding gap** (also captured as episode `w1-verdict-001`): both the implementer and
  reviewer crews, dispatched via `run_crew.py --backend cli`, found their environment carried only
  `SPINE_PARENT` — no `SPINE_FILE`/`SPINE_SESSION` — despite `crew-runs.json` recording
  `door_bound: true` for both. Each crew worked around it by authoring its own local plan/survey
  JSON and driving it through the CLI directly (matching a pattern the reviewer noted was already
  observed in a prior epic, 567-d1 g4). No work was lost, but the registry's claim and the actual
  environment disagreed twice in one run.
- **None beyond the above** — confirmed after re-reading the launch order in full a second time at
  archive: the mission-scope pre-rulings (vocabulary out of scope, live/report-only split, fix-now
  triage, filing disfavoured) all had clear, actionable text and needed no interpretation beyond
  what's captured in §2's process note and the two items above.

## Episodes captured
`episodes/active/w1-verdict-001.md` (crew door-binding gap), `w1-verdict-002.md` (CLI session-id
friction), `w1-verdict-003.md` (map staleness, reproduced 3×) — applied via
`scripts/apply_episode_delta.py`, verified via `scripts/verify_episode_captured.py` at both the
`feedback` and `archive` phases.

## Addendum — branch repair (post-acceptance, at the Admiral's instruction)

The Admiral found the launch order's "base is green, 3564 passed" claim was itself wrong —
`map/INDEX.md` shipped stale at base commit `244665ee` (measured, not assumed: a fresh
`code_map` build at that commit disagreed with the committed index), which is *why* the
`test_map_tree_freshness_...` failure this run waived as "pre-existing, unrelated" existed at
all. The human's own fix landed on `main` at `3c0ae817`; merging this branch as-is would have
re-introduced staleness (this branch's new entities — `_artifact_match_satisfied`,
`_fault_artifact_malformed_match_list`, and their tests — were never indexed).

Repair, branch-only, spine untouched (already terminal, lease released, per the Admiral's
explicit instruction not to reopen or re-drive it):
1. `git fetch origin && git merge origin/main` — clean, no conflicts (merge commit `09350ac3`;
   touched only Admiral epic-569 bookkeeping files, the `spine_rail` hook fix, and
   `map/INDEX.md`, none overlapping this mission's own changed files).
2. `python -m scripts.code_map build --root .` — regenerated `map/INDEX.md` (not hand-edited);
   diff confirms it now reflects this branch's new entities (`scripts.checklist_engine` 115→116,
   `scripts.validate_spine` 23→24, plus the corresponding test-file entity growth) on top of the
   human's fix.
3. `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
   now passes on its own (no waiver needed).
4. Full suite, no allowance: **3598 passed, 6 skipped** (up from 3592/3564 — all new tests, zero
   regressions, zero waived failures).
5. Committed (`a9924053`) and pushed. PR #645: `mergeable: MERGEABLE`.

Nothing about the mechanism itself (the two comparator sites, the `validate_spine` guard) changed
in this repair — verified: `git diff a21a8587 a9924053 -- scripts/checklist_engine.py
scripts/validate_spine.py docs/CHECKLIST_SCHEMA.md tests/test_checklist_engine.py
tests/test_validate_spine.py` is empty.
