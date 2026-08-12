# Implementation Result

## Assigned gate
`g4a-implement` (#542 criterion 1, adoption)

## Completed slice
Made role spine instructions name the MCP door's tools as the default path, with the CLI documented as the remaining fallback, across the full pre-authored Tier 1-5 invariant chain from the handoff. Pinned both halves with `tests/test_mcp_adoption.py`, proved the pin two-sided by deliberate deletion (twice — the first attempt exposed a weak generic pin, which I tightened before re-proving), and fixed a real regression the edits caused in `tests/test_retirement_guard.py`'s store-mention census.

## Scope

**Files changed:**

Tier 1 (7 imperative fields by JSON field path, plus 1 markdown command line):
- `skills/commander/templates/COMMANDER_SPINE.template.json` — `.tasks.init.imperative`, `.tasks.plan.imperative`, `.tasks.archive.imperative`
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` — `.tasks.init.imperative`, `.tasks.closeout.imperative`
- `skills/explorer/templates/EXPLORER_SPINE.template.json` — `.tasks.init.imperative`, `.tasks.route.imperative`
- `skills/commander/references/commander-core.md` (line ~127, the delegated-mode `attach` command line)

Tier 2 (default-path prose, 6 SKILL bodies):
- `skills/workbench/SKILL.md`, `skills/charter/SKILL.md`, `skills/reviewer/SKILL.md`, `skills/interrogator/SKILL.md`, `skills/implementer/SKILL.md`, `skills/explorer/SKILL.md`

Tier 3 (the engine CLI reference):
- `skills/workbench/references/checklist-engine.md`

Tier 4 (authoring templates):
- `skills/write-a-skill/templates/gated-engine-SKILL.template.md`, `skills/write-a-skill/templates/survey-SKILL.template.md`

New test:
- `tests/test_mcp_adoption.py`

Incidental fix, caused by the Tier1 edits (not in the original allowed scope, but leaving it broken would leave the suite red — see Stop conditions hit):
- `tests/data/store_mentions.approved.txt` — 2 stale verbatim-line approvals updated to the new exact text of the ADMIRAL_SPINE closeout and COMMANDER_SPINE archive imperatives.

Code map:
- `map/INDEX.md` and related map artifacts rebuilt via `python -m scripts.code_map build --root .`.

Tier 5 (`skills/_shared/global-everyone.md`, `skills/admiral/references/fleet-doctrine.md`): **untouched**, as instructed. `TestTier5DoNotTouch` in the new test file confirms both files still name `checklist_engine.py` and contain no door-tool name.

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/install_constellation.py`, `scripts/hooks/spine_rail.py` were never edited (confirmed no diff against them).

## Behavior changed
No runtime behavior changed — this is a doc-only gate. Every literal engine command line that used to say only `<engine> claim/release/attach ...` now says the same CLI line PLUS a preceding door-tool default; nothing was deleted, deprecated, or discouraged.

## Map Impact

- **Structural anchors touched:** the 7 imperative fields in the 3 spine templates (Tier1); `skills/workbench/references/checklist-engine.md`'s canonical invocation line and Session lease verb table; the 6 SKILL.md drive-mechanism paragraphs; the 2 write-a-skill authoring templates. No new files, symbols, or scripts were introduced — only prose/JSON-string edits to existing anchors.
- **Capabilities added/changed/affected:** none new. The MCP door (`scripts/mcp_spine_server.py`) itself is unchanged; only the instructions that reach for it were added.
- **Constraints/assumptions touched:** `the-cli-door-stays` — honored throughout; every edited field/paragraph keeps its pre-existing CLI text verbatim alongside the new door-default text. The g1 identity-trade rule (in-session dispatched crew member cannot drive its own plan through the door) is now carried in `skills/implementer/SKILL.md`, `skills/reviewer/SKILL.md`, and `skills/workbench/references/checklist-engine.md`'s new "MCP door" section, not merely cited.
- **Decision candidates / resolved decisions:** none raised. This gate executes a decision (`the-cli-door-stays`) already settled by the human, per the handoff.
- **Claims/evidence produced:** `tests/test_mcp_adoption.py` (55 assertions across 8 test classes) is the durable evidence that the invariant chain holds; the deliberate-deletion proof below is the evidence the pin is genuinely two-sided.
- **Trust limitations / drift found:** the store-mention census in `tests/data/store_mentions.approved.txt` pins exact verbatim lines of spine-template imperatives. Any FUTURE edit to those same lines (in `ADMIRAL_SPINE.template.json`'s closeout imperative or `COMMANDER_SPINE.template.json`'s archive imperative) will again go stale and needs the same census update — flagging this as a durable coupling Cartographer/Charter may want to record, since it is not obvious from the spine templates themselves that a second file must move in lockstep.
- **Triage candidates:** none raised as new issues; see Out-of-scope observations below.

## Test mode
**Required:** test-first (TDD red -> green), per the handoff's "pin both halves with a test."
**Satisfied:** yes. `tests/test_mcp_adoption.py` was written and run RED against the unedited corpus (21 failed / 34 passed) before any Tier1-4 file was touched, then driven GREEN tier by tier.

## Evidence

```bash
python -m pytest -q tests/test_mcp_adoption.py
```
**Result:** pass — 55 passed.

```bash
python -c "import json;[json.load(open(p)) for p in ['skills/commander/templates/COMMANDER_SPINE.template.json','skills/admiral/templates/ADMIRAL_SPINE.template.json','skills/explorer/templates/EXPLORER_SPINE.template.json']]"
```
**Result:** pass — no exception, all 3 templates parse.

```bash
python -m pytest -q
```
**Result:** pass — 2339 passed, 1 skipped, 1078 subtests passed (101s). (The 1 skip is pre-existing and unrelated — not introduced by this change.)

```bash
python -m scripts.code_map build --root .
```
**Result:** pass — rebuilt before the final full-suite run, per the constraint.

```bash
git check-ignore <path>   # for every committed deliverable
```
**Result:** exit 1 for all 17 paths (13 edited Tier1-4 files, `tests/test_mcp_adoption.py`, `tests/data/store_mentions.approved.txt`, `map/INDEX.md`, my own `IMPLEMENTER_PLAN.json`) — none is git-ignored.

```bash
grep -rlE 'mcp__spine__|spine_status|spine_lease|spine_start|spine_advance|spine_evidence|spine_halt|spine_survey_result' skills/
```
**Result:** **13** files (was **0** at the wave boundary):
```
skills/admiral/templates/ADMIRAL_SPINE.template.json
skills/charter/SKILL.md
skills/commander/references/commander-core.md
skills/commander/templates/COMMANDER_SPINE.template.json
skills/explorer/SKILL.md
skills/explorer/templates/EXPLORER_SPINE.template.json
skills/implementer/SKILL.md
skills/interrogator/SKILL.md
skills/reviewer/SKILL.md
skills/workbench/references/checklist-engine.md
skills/workbench/SKILL.md
skills/write-a-skill/templates/gated-engine-SKILL.template.md
skills/write-a-skill/templates/survey-SKILL.template.md
```
This is exactly the 13 files edited (Tier1 x4 including commander-core.md, Tier2 x6, Tier3 x1, Tier4 x2). Report as a number, per the handoff — this is NOT the gate's evidence; the two-sided test below is.

## TDD evidence, if required

- **Failing test observed** (m1-red, against the unedited corpus): `python -m pytest -q tests/test_mcp_adoption.py` -> **21 failed, 34 passed**. All 21 failures were door-tool-not-named assertions across Tier1 (7 fields), the commander-core.md attach line, Tier2 (6 files), Tier3 (3 assertions), Tier4 (2 files) — exactly the corpus this gate edits. The 34 passes were the CLI-still-present half (already true) plus JSON validity and Tier5 do-not-touch (both halves already true, since nothing had been touched).
- **Passing test observed** (after all Tier1-4 edits): `python -m pytest -q tests/test_mcp_adoption.py` -> **55 passed**.
- **Refactor while green:** yes, but not routine refactor — a genuine strengthening. See the two-sided proof below: the first version of the test used a generic `<engine>` substring check per field, which the deliberate-deletion drill exposed as vacuously passable (a different, unrelated CLI verb mention in the same field kept the assertion green after the targeted line was deleted). I tightened `TIER1_JSON_FIELDS` to carry the exact per-action CLI command line instead of a bare placeholder, re-confirmed GREEN against the then-current corpus, then repeated the deletion against the tightened test.

### The two-sided proof (required by the handoff)

**Attempt 1 — the weak pin, caught by its own drill:**
1. Deleted `CLI fallback: <engine> release --session-id <commander-session-id>` from `COMMANDER_SPINE.template.json`'s `.tasks.archive.imperative`, leaving the `spine_lease` door mention intact.
2. `python -m pytest -q tests/test_mcp_adoption.py -k Tier1` -> **19 passed** (unexpected GREEN). Root cause: the test's `test_field_still_carries_cli_fallback` checked only the generic `CLI_PLACEHOLDER = "<engine>"` string anywhere in the field. The SAME field's `archive` imperative also contains an unrelated `waive` CLI line (`a human waives c4 via <engine> waive archive --cond c4 ...`), which alone satisfied the generic check. This is exactly the "enumeration is not a property" / weak-pin failure class the handoff named — an under-specified assertion that would also pass a partial CLI deletion.
3. Restored the line, then **rewrote** `TIER1_JSON_FIELDS` to carry the exact per-action CLI command line for each of the 7 fields (e.g. `"<engine> release --session-id <commander-session-id>"`, not just `"<engine>"`), and reran to confirm the tightened pin was still GREEN against the (unchanged since m2) corpus: `python -m pytest -q tests/test_mcp_adoption.py -k Tier1` -> **19 passed**.

**Attempt 2 — the same deletion, against the tightened pin:**
1. Deleted the same `CLI fallback: <engine> release --session-id <commander-session-id>` text again, leaving the door mention intact.
2. `python -m pytest -q tests/test_mcp_adoption.py -k Tier1` -> **1 failed, 18 passed** — genuine RED:
   ```
   FAILED tests/test_mcp_adoption.py::TestTier1ImperativeFields::test_field_still_carries_cli_fallback[
     skills/commander/templates/COMMANDER_SPINE.template.json-keys2-spine_lease-<engine> release --session-id <commander-session-id>]
   AssertionError: ... lost its exact CLI command line '<engine> release --session-id <commander-session-id>' ...
   ```
   Crucially, `test_field_names_door_tool_as_default` for the SAME field stayed green throughout — proving the two assertions are independent, not coupled, and that the failure is specific to the CLI half.
3. Restored the exact original text from a pre-deletion backup; `diff` against the backup after restore was **empty** (byte-identical).
4. `python -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json'))"` -> no exception.
5. `python -m pytest -q tests/test_mcp_adoption.py -k Tier1` -> **19 passed** (GREEN again). Full file: `python -m pytest -q tests/test_mcp_adoption.py` -> **55 passed**.

## Docs/contracts touched
- `skills/workbench/references/checklist-engine.md` — new "MCP door" section, Contents TOC entry, augmented canonical invocation and Session lease table.
- `tests/data/store_mentions.approved.txt` — 2 census entries updated to new exact line text (see Scope).

## Assumptions
- The door tool name convention an agent actually invokes is `mcp__spine__<tool_name>` (Claude Code's `mcp__<server>__<tool>` pattern, server name `spine` per `.mcp.json`); I named the bare tool names (`spine_lease`, etc., matching `mcp_spine_server.py`'s own `TOOLS` list) in most prose since that is what the tool schemas and error messages use, and is unambiguous once the door section explains the prefix. The test's `DOOR_TOOL_RE` accepts both forms.
- For fields where a single JSON string contains more than one engine-verb mention (e.g. `archive` also has a `waive` line I did not touch), I only added a door-default sentence for the specific action targeted by that field path's Tier1 requirement (`claim`/`release`/`attach`), not for every verb mentioned in prose — the untouched `waive` mention stays CLI-only in text, though `waive` itself does have a door tool (`spine_evidence`) not covered by this gate's Tier1 list.

## Stop conditions hit
- None. No decision this handoff did not settle was encountered; the store-mention census fix was mechanical (updating a stale line to match a field I was authorized to edit), not a scope or authority question.

## Out-of-scope observations
- The store-mention census coupling noted under Map Impact / Trust limitations: any future edit to the 2 pinned spine-template lines needs a matching `tests/data/store_mentions.approved.txt` update, and nothing about the census format signals this dependency from the spine template side. Not filed as a triage candidate since it is a general property of the census mechanism (already true before this gate), not something this gate introduced.
- Reproduced the same doubled-path defect the prior `g2-implement` run flagged (its tc1 triage candidate): my own nested work-id (`epic-418-followon/commander-f2/g4a-implement`, one segment deeper than the 2-segment convention `tests/test_work_id_nesting.py` covers) caused a mechanical-snapshot write to land at the doubled `.agent-work/epic-418-followon/epic-418-followon/commander-f2/g4a-implement/...` instead of the correct path. Untracked, harmless, deleted as cleanup. Not re-filed as a new triage candidate since it is the same already-known defect, outside this run's file ownership (`episode_capture.py`/`context_manifest.py`).

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review. The handoff's pre-authored invariant chain (file + JSON field path for every Tier1 entry) was precise enough that I never had to invent a proxy; the one place I had to make a judgment call (which door tool to use for the `commander-core.md` attach line, and the exact door-tool-to-CLI-verb mapping for `waive`/`attach`/`claim`/`release`) was fully resolvable from `mcp_spine_server.py`'s own tool schemas, which the handoff correctly pointed me toward via the fallback-table citation.
- **Context rediscovered:** the `tests/data/store_mentions.approved.txt` verbatim-line census mechanism was not mentioned anywhere in the handoff, and its existence is not discoverable from the Tier1-4 file list alone — I only found it because the full-suite run in m7-verify went red on `tests/test_retirement_guard.py` after my Tier1 edits changed exact line text that a completely separate test file had pinned. A handoff for any future gate that edits `COMMANDER_SPINE.template.json`'s archive imperative or `ADMIRAL_SPINE.template.json`'s closeout imperative verbatim should flag this coupling in advance.
- **Instructions improvised around:** none. The skill's TDD-red guidance ("encode the RED step as a check:null postcondition... NOT a command check") applied cleanly to `m1-red`, and the vertical-slice-per-tier plan shape mapped directly onto the handoff's own Tier1-4 structure.
- **What would have made this easier:** a one-line pointer in the handoff (or in `checklist-engine.md` itself, prospectively) noting that editing a spine template's exact imperative text may require a matching update to `tests/data/store_mentions.approved.txt` if that line is store-mention-census-approved — would have saved the one detour of tracing the retirement-guard failure back to its cause.

## Return status
`complete`
