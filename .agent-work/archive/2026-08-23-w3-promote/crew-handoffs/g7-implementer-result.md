# IMPLEMENTER_RESULT

## Gate
g7-implement (execute.json, work-id w3-promote)

## Return status
complete

## Summary
Promoted 1 of the 5 candidate `check: null` conditions named across BOTH files this gate covers
(`skills/cartographer/templates/CARTOGRAPHER.template.json`, `skills/scout/templates/SCOUT.template.json`)
to a real, mechanically-checked condition, using only the engine's existing `command` check kind
(`decision:no-new-check-kinds`). The other 4 were fresh-verified against the real shipped JSON and
left `check: null` per the handoff's own stated fallbacks, with the reasoning below.

**CARTOGRAPHER.template.json — 0 of 4 promoted (unchanged, no edit).**
1. `context.c1` ("context and current map loaded") — pure judgment, no locator. Left `check: null`.
2. `map-compliance.c1` ("map compliant; open structural questions recorded") — pure judgment, no
   locator. Left `check: null`.
3. `packets.c1` ("touched packets reflect current code") and `index-overlays.c1` ("index and
   overlays consistent with packets") — the two WEAK candidates the handoff itself named. A
   git-diff-based "something under `docs/architecture/` changed" proxy verifies motion, not
   correctness: it would falsely pass a genuinely STALE map if something else under that path
   happened to change in the same commit — the exact locator-ambiguity the handoff warned against.
   Independently, and sufficient on its own: this run's own `MISSION_FRAME.md` records the map as
   DEGRADED-UNPARSEABLE repo-wide (`docs/architecture/` is empty, `map/ids.jsonl` empty, no citable
   anchor ids) — confirmed fresh (`ls docs/architecture/` returns only an empty `generated/` dir).
   The handoff's own CRITICAL section bars any promoted check from depending on map state this repo
   cannot currently produce, which forecloses both candidates even setting the ambiguity finding
   aside. Both stay `check: null`, matching notes-1.md's own risk-tier assessment exactly.

**SCOUT.template.json — 1 of 3 promoted (split condition).**
1. `report.c1` ("SCOUT_REPORT written; candidates routed") — SPLIT: the "SCOUT_REPORT.md written"
   half gets a real `command`-kind check against the fixed-path locator `.agent-work/SCOUT_REPORT.md`
   (`SKILL.md`'s own "Own: `.agent-work/SCOUT_REPORT.md` candidates" line, not per-`<work-id>`); the
   "candidates routed" half stays uncovered judgment, same partial-conversion shape as g1's
   `COMMANDER_SPINE` `plan.c2`. `statement` text left byte-identical, no `basis` field added
   (`decision:no-basis-backfill`).
   Ships **REPORT-ONLY**, not blocking: `SCOUT.template.json` measured ZERO live check kinds
   anywhere before this gate (confirmed directly against `git show HEAD:...` — all 4 pre-existing
   conditions are `check: null`), so per `decision:blocking-where-adjudicated`'s own default for a
   first-use-of-any-kind file, blocking would need explicit Commander consultation this handoff does
   not grant. The command always exits 0 while still running the real `-s` (nonempty) test and
   printing which branch fired: `PASS: SCOUT_REPORT.md written` or `report-only: NOT gating --
   SCOUT_REPORT.md missing or empty` — the map_orient.py `--report-only` idiom (gate-vs-report is a
   flag flip, not a rebuild), reproduced by hand since this is a plain shell check, not a Python
   script carrying its own flag. **Named promotion trigger** (recorded in the shipped template's own
   `map_check_note` on the `report` task, per `docs/CHECKLIST_SCHEMA.md`'s documented template-only,
   read-by-no-code field): after N clean report-only runs through this gate with zero
   false-refusals, reviewed at the next Cartographer/Scout-owning wave, flip to blocking by dropping
   the trailing `; exit 0` — a flag-flip, not a rebuild.
2. `context.c1` ("context and current map loaded") — pure judgment, no locator, identical pattern to
   CARTOGRAPHER's own `context.c1`. Left `check: null`.
3. `audit.c1` ("candidates gathered with evidence") — pure judgment, no locator. Left `check: null`.

Promoting `report.c1` (the `report` task's ONLY postcondition) cleared 1 all-null gate per
`scripts/validate_spine.py`'s `falsifiable-all-null` fault (postcondition-only; ignores
preconditions) — measured corpus-wide count dropped from 14 (post-g5) to 13. `CARTOGRAPHER`'s own 4
faults are all unchanged (0 promotions there). `tests/test_validate_spine.py`'s floor was updated in
the same edit (both message text and the numeric threshold), confirmed by re-running the corpus
sweep pre/post-edit.

`docs/CHECK_SCRIPT_CENSUS.md`'s unwired-script list names `check_role_spine_bookends.py` (a
COMMANDER-specific bookend concept) and `check_skill_freshness.py` (skill-doc freshness
reconciliation) as options — neither fits SCOUT's `report.c1` (a plain file-existence probe against
`.agent-work/SCOUT_REPORT.md`) or either declined CARTOGRAPHER candidate. Neither was wired; that
census doc's own live/unwired tallies are therefore untouched by this gate, and g8 needs no flag on
this point.

Only `.agent-work/templates/SCOUT.template.json` was re-synced (byte-copy of the edited shipped
file, never a `json.load`/`json.dump` round-trip, re-verified with
`scripts/check_template_overlay_freshness.py` — all 56 clean); `CARTOGRAPHER`'s overlay was left
untouched, per the handoff's own "only sync the ones you actually edit" instruction. Two new
red-proof test classes in `tests/test_checklist_engine.py`, adjacent to g1's/g3's/g4's/g5's own
W3Promote classes: `ScoutW3PromotePromotions` (pinned HEAD, `skipTest` on drift, adversary-chosen
mutation — an EMPTY `SCOUT_REPORT.md`, not a missing one, attacking the `-s` nonempty boundary — plus
two dedicated report-only-specific tests: one proving `advance` never blocks under any of 3 fixture
states, one proving the underlying probe's stdout still genuinely discriminates via the engine's own
`_run_check_command` shell runner) and `CartographerW3PromoteDeclined` (pins the zero-promotion
decision against future drift, same discipline every promoting class applies to its own declined
candidates).

## Scope
**Files changed:**
- `skills/scout/templates/SCOUT.template.json`
- `.agent-work/templates/SCOUT.template.json`
- `tests/test_checklist_engine.py`
- `tests/test_validate_spine.py`

**Specific exclusions touched:** no — `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`,
`EXPLORER_SPINE.template.json`, `CHARTER.template.json`, `IMPLEMENTER_PLAN.template.json`, their
overlays, `checklist_engine.py`, and `docs/CHECK_SCRIPT_CENSUS.md` were not touched.
`skills/cartographer/templates/CARTOGRAPHER.template.json` was read and fresh-assessed but not
edited (0 eligible promotions found), so its overlay was correctly left untouched too.

## Behavior changed
Yes — 1 condition in `SCOUT.template.json` gained a real, engine-enforced (but non-blocking)
command check, previously vacuous `check: null`. `advance` on the `report` gate will now genuinely
run the `.agent-work/SCOUT_REPORT.md` existence+nonempty probe and record its exit code/command text
as evidence, but the gate itself can never be refused by it (report-only, always exits 0) — a strict
observability addition, not a new blocking surface. `CARTOGRAPHER.template.json`'s behavior is
unchanged.

## Map Impact
- **Structural anchors touched:** none new — reuses `checklist_engine.py`'s existing `command`
  check-kind machinery, no code changed.
- **Capabilities added/changed/affected:** `SCOUT.template.json`'s `report` step now runs a real,
  non-blocking existence probe against `.agent-work/SCOUT_REPORT.md` instead of trusting an
  honest-but-unchecked attest, with the real verdict visible in the command-check's stdout/exit
  evidence.
- **Constraints/assumptions touched:** `decision:no-new-check-kinds` (honored — only `command` used,
  the engine's existing kind); `decision:no-basis-backfill` (honored — no `basis` field added
  anywhere); `decision:blocking-where-adjudicated` (honored — this IS a first-of-kind `command` use
  in `SCOUT.template.json`, so it ships report-only per that decision's own default rather than
  blocking without consult).
- **Trust limitations / drift found:** this run's own map is DEGRADED-UNPARSEABLE
  (`docs/architecture/` empty) — recorded here so a future Cartographer reconcile does not assume
  `packets.c1`/`index-overlays.c1` were skipped for lack of effort; they were skipped because the
  map state this repo can currently produce cannot support a genuinely discriminating locator, per
  this gate's own CRITICAL constraint.
- **Triage candidates:** `packets.c1`/`index-overlays.c1` become re-assessable once
  `docs/architecture/` carries a real, non-empty, parseable map again — worth a future issue tied to
  whatever restores the map, not invented here. `report.c1`'s report-only status is itself the named
  promotion trigger: re-visit at the next Cartographer/Scout-owning wave after N clean runs.

## Test mode
**Required:** test-after
**Satisfied:** yes — `ScoutW3PromotePromotions` (6 tests) and `CartographerW3PromoteDeclined`
(1 test) added after the JSON edit, red-proofed with an adversary-chosen mutation (empty file, not
missing), then the full listed suite run green.

## Evidence

```bash
$ git diff -- skills/scout/templates/SCOUT.template.json
```
```diff
--- a/skills/scout/templates/SCOUT.template.json
+++ b/skills/scout/templates/SCOUT.template.json
@@ -26,8 +26,9 @@
       "id": "report",
       "title": "Write SCOUT_REPORT",
       "imperative": "Write SCOUT_REPORT with ranked candidates and evidence. Record each finding's disposition: current-truth fix -> Cartographer, or future work -> Triage. Route future-work candidates to triage; Scout reports candidates only and never edits the map.",
+      "map_check_note": "epic-569/w3-promote g7: c1's check covers only the SCOUT_REPORT.md-written half of the statement ... [full text in the shipped file]",
       "preconditions": [],
-      "postconditions": [{"id": "c1", "statement": "SCOUT_REPORT written; candidates routed", "check": null, "satisfied": false}],
+      "postconditions": [{"id": "c1", "statement": "SCOUT_REPORT written; candidates routed", "check": {"kind": "command", "command": "if [ -s \"<repo-root>/.agent-work/SCOUT_REPORT.md\" ]; then echo \"PASS: SCOUT_REPORT.md written\"; else echo \"report-only: NOT gating -- SCOUT_REPORT.md missing or empty\"; fi; exit 0"}, "satisfied": false}],
       "constraints": [], "directives": null, "child_checklist": null,
       "status": "pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], "rework_count": 0
     }
```

```bash
$ git diff --stat skills/cartographer/templates/CARTOGRAPHER.template.json
```
**Result:** empty (no output) — confirms zero edits to this file.

```bash
$ python3 -c "import json; json.load(open('skills/cartographer/templates/CARTOGRAPHER.template.json',encoding='utf-8')); print('OK')"
OK
$ python3 -c "import json; json.load(open('skills/scout/templates/SCOUT.template.json',encoding='utf-8')); print('OK')"
OK
```
**Result:** pass

```bash
$ python3 scripts/check_template_overlay_freshness.py
...
  ok                 .agent-work/templates/SCOUT.template.json -- matches skills/scout/templates/SCOUT.template.json
  ok                 .agent-work/templates/CARTOGRAPHER.template.json -- matches skills/cartographer/templates/CARTOGRAPHER.template.json
...
all 56 overlay template(s) checked -- none stale
```
**Result:** pass

```bash
$ grep -n '"check"' skills/cartographer/templates/CARTOGRAPHER.template.json   # before == after, all null, unchanged
$ grep -n '"check"' skills/scout/templates/SCOUT.template.json                  # report.c1 now carries a real check; context.c1/audit.c1 unchanged
```
**Result:** pass — CARTOGRAPHER identical before/after; SCOUT shows exactly the one new check.

```bash
$ python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
643 passed, 31 skipped, 148 subtests passed in 5.80s
```
**Result:** pass

```bash
$ git check-ignore skills/scout/templates/SCOUT.template.json .agent-work/templates/SCOUT.template.json tests/test_checklist_engine.py tests/test_validate_spine.py
```
**Result:** exit 1 for each (not ignored, all trackable/committable).

## TDD evidence, if required
N/A (test-after per handoff's Test Mode).

## Docs/contracts touched
None — `docs/CHECKLIST_SCHEMA.md` (the `command` check kind and `map_check_note` field) and
`docs/CHECK_SCRIPT_CENSUS.md` describe existing mechanisms this work only reuses; no new mechanism
was introduced, and `docs/CHECK_SCRIPT_CENSUS.md` itself was deliberately left unedited per the
handoff's own Specific Exclusions (g8's job).

## Assumptions
- `<repo-root>` resolves for `SCOUT.template.json` the same generic way it does for every other
  role's own top-level spine (`COMMANDER_SPINE`/`ADMIRAL_SPINE`/`EXPLORER_SPINE`), via
  `init_work_area.resolve_spine`'s blind text substitution when Scout's own checklist is
  instantiated — confirmed against that function's docstring and its existing, already-shipped uses
  of the same token in `EXPLORER_SPINE.template.json`'s command checks; no `<work-id>` token was
  needed since `.agent-work/SCOUT_REPORT.md` is explicitly NOT per-work-id-scoped (`SKILL.md`'s own
  "Own: `.agent-work/SCOUT_REPORT.md`" line).
- The `falsifiable-all-null` fault's postcondition-only scope (same discipline g1/g3/g4/g5 used)
  means `report` clearing is judged solely on its single postcondition; it has no preconditions at
  all, so this is unambiguous.
- `map_check_note` (task-level, sibling of `imperative`) was the right home for the report-only
  promotion trigger rather than a new field on the condition itself: it is documented in
  `docs/CHECKLIST_SCHEMA.md` as template-only/read-by-no-code, already used this exact way by
  `COMMANDER_SPINE`'s own `context`/`plan` steps, and does not collide with `decision:no-basis-backfill`
  (which is specifically about the `basis` field, not this one).

## Stop conditions hit
None triggering a blocked return. The Stop Conditions section named three scenarios; none of them
actually fired:
- CARTOGRAPHER's `packets.c1`/`index-overlays.c1` locator question was resolved cleanly in the
  DECLINE direction by the CRITICAL section's own map-state constraint (this run's map IS
  DEGRADED-UNPARSEABLE, confirmed directly), not left ambiguous — no genuinely unambiguous locator
  was found, so there was nothing to be unsure about shipping report-only vs. blocking.
- No edit required touching `checklist_engine.py`.
- `check_role_spine_bookends.py`/`check_skill_freshness.py` wiring was assessed and declined on
  fit grounds (neither script's subject matter matches either file's remaining candidates), not left
  unsure — flagged plainly above per the handoff's own instruction, no Commander round-trip needed.

## Out-of-scope observations
None beyond the triage candidates already named in Map Impact above (re-assess
`packets.c1`/`index-overlays.c1` once the map is restored; revisit `report.c1`'s report-only status
per its own named trigger).

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff's own CRITICAL section pre-answered the hardest
  judgment call here (report-only-by-default for a first-use file) precisely enough that no
  round-trip was needed even though this gate's default REVERSES every prior gate's own default —
  worth naming as a genuinely well-designed handoff, not friction.
- **Context rediscovered:** had to trace `scripts/init_work_area.py::resolve_spine`/`instantiate_spine`
  by hand to confirm `<repo-root>` really does resolve generically for a non-COMMANDER role spine
  like Scout's own `SCOUT.template.json`, since that file (like CARTOGRAPHER's) carried ZERO
  placeholder tokens anywhere before this gate — nothing in the handoff or its Map Anchors named
  this resolver path directly. A future handoff introducing the FIRST placeholder token into a
  previously-token-free template could usefully cite `scripts/init_work_area.py::resolve_spine`
  directly, the way this one cited `map_orient.py`'s `--report-only` flag for the report-only shape.
- **Instructions improvised around:** the handoff named `map_check_note` nowhere explicitly as the
  place to record a report-only promotion trigger; `docs/CHECKLIST_SCHEMA.md`'s own schema table and
  `COMMANDER_SPINE.template.json`'s two existing uses were traced independently to confirm it was a
  legal, non-`basis`, template-only field before using it this way.
- **What would have made this easier:** none — this gate's CRITICAL section was unusually thorough
  and the map_orient.py citation made the report-only shell-wrapper shape immediately concrete to
  copy.
