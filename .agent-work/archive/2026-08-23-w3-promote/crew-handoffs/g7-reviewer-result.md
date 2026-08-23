# Review Result

## Assigned Gate
g7-implement (execute.json, work-id w3-promote) — independent review of the SCOUT/CARTOGRAPHER
`check: null` promotion slice

## Result
`APPROVE`

## Handoff compliance
Satisfied. The implementer promoted exactly 1 of 5 candidate `check: null` conditions
(`SCOUT.template.json`'s `report.c1`), shipped it report-only, declined all 4 CARTOGRAPHER
candidates with recorded reasoning, red-proofed the promotion with two new test classes, updated
the `falsifiable-all-null` floor, and kept the full listed suite green. Every Close Criterion in
the handoff was independently re-derived (not trusted from prose) — see per-check findings below.

## Scope drift
None found. `git diff --stat -- skills/cartographer/templates/CARTOGRAPHER.template.json
.agent-work/templates/CARTOGRAPHER.template.json` is empty — genuinely untouched, byte-identical to
HEAD. `SCOUT.template.json`'s diff (main + overlay, byte-identical to each other) touches exactly 2
lines: `report.c1`'s `check` field (`null` -> `command`) and the new `map_check_note` field on the
`report` task. `context.c1`, `audit.p1`, `audit.c1` confirmed unchanged by direct re-dump of the
post-edit file. No excluded file (`COMMANDER_SPINE`, `ADMIRAL_SPINE`, `EXPLORER_SPINE`, `CHARTER`,
`checklist_engine.py`, `docs/CHECK_SCRIPT_CENSUS.md`) was touched (confirmed via `git status
--porcelain` — none of those paths appear as modified in this gate's slice).

## Evidence verdict
Independently reproduced rather than trusted:

- **Report-only shape, executed (not read):** ran the exact promoted shell command (with
  `<repo-root>` substituted) against three scratch directories — missing `SCOUT_REPORT.md`, present
  but empty, and populated. All three exited 0. Missing and empty both printed `report-only: NOT
  gating -- SCOUT_REPORT.md missing or empty`; populated printed `PASS: SCOUT_REPORT.md written`.
  This is genuine `-s` (nonempty) semantics, not `-f` (existence) — the empty-file branch proves the
  boundary is real, and the command always discriminates while never blocking. Matches the claim
  exactly.
- **Zero-live-check-kinds claim, both files:** dumped every condition's `check` field from `git show
  HEAD:skills/scout/templates/SCOUT.template.json` and `git show
  HEAD:skills/cartographer/templates/CARTOGRAPHER.template.json` — all 9 conditions across both
  files (4 in SCOUT, 5 in CARTOGRAPHER) were `check: null` pre-edit. Confirms the load-bearing
  premise for shipping report-only under `decision:blocking-where-adjudicated`.
- **`map_check_note` legitimacy:** `docs/CHECKLIST_SCHEMA.md:196` documents it as `*optional*;
  template-only, read by no code`, explicitly naming the Commander spine's `context`/`plan` steps as
  the precedent. Independently confirmed `COMMANDER_SPINE.template.json` carries `map_check_note` on
  its `context` step (line 22) and elsewhere — the field is real and used exactly this way already,
  not invented for this gate.
- **No `basis` collision:** `grep -n "basis" skills/scout/templates/SCOUT.template.json` returns
  nothing, both before (`git show HEAD:...`) and after the edit — no new occurrences.
- **Overlay sync:** `python3 scripts/check_template_overlay_freshness.py` reports all 56 overlay
  templates clean, including `.agent-work/templates/SCOUT.template.json` matching its skill source
  byte-for-byte. `.agent-work/templates/CARTOGRAPHER.template.json` correctly received no edit (0
  edits to the main file means 0 sync needed, and the diff-stat is empty).
- **CARTOGRAPHER decline, independently re-derived:** `docs/architecture/` contains only
  `generated/map.json`, whose content is `{"findings": [], "nodes": [], "relationships": [],
  "version": 1}` — genuinely empty, matching `MISSION_FRAME.md`'s DEGRADED-UNPARSEABLE claim. Read
  `packets.c1` (`touched packets reflect current code`) and `index-overlays.c1` (`index and overlays
  consistent with packets`) directly: a git-diff-based "something under docs/architecture/ changed"
  proxy would indeed only verify motion, and is locator-ambiguous — it cannot distinguish "the
  touched node's own packet was updated" from "an unrelated packet in the same directory changed in
  the same commit," and with the directory currently empty there is no packet population to locate
  against in the first place. The decline holds up under independent re-derivation, not just
  prose-trust.
- **falsifiable-all-null 14->13 sweep, independently re-run:** `git stash push` on just the two
  touched SCOUT files, ran the corpus sweep directly against `validate_file` — measured 14. Popped
  the stash, re-ran — measured 13. The drop is real and isolated to exactly the file this gate
  touched (nothing else was stashed).
- **Unwired-script census claim:** `check_role_spine_bookends.py` and `check_skill_freshness.py`
  both still listed `unwired` in `docs/CHECK_SCRIPT_CENSUS.md`; grepped both template files for
  either script name — zero occurrences. Neither was wired in this gate; the g8 dependency claim is
  accurate.
- **Full suite:** `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q`
  → `643 passed, 31 skipped, 148 subtests passed`, no failures.

## Code/doc quality
`report.c1`'s promoted shape is minimal, matches spec (`-s` nonempty test, unconditional `exit 0`,
prints the real branch), and the JSON edit is surgical (2 lines changed in a compact-format file,
not reflowed) per `Compact-format JSON hand-edit discipline`. `decision:no-new-check-kinds` honored
(`command` kind only, already engine-native — no new kind invented). The two new test classes
(`ScoutW3PromotePromotions`, `CartographerW3PromoteDeclined`) read the new promotion's shipped shape
directly from disk each run, pin `PINNED_HEAD` and `skipTest` (not fail) on drift, and attack the
promoted check with a genuinely adversarial mutation — an EMPTY file, not merely a missing one,
which specifically stresses the `-s` boundary a lazier `-f`-based attack would miss.
`test_report_c1_never_blocks_advance_healthy_or_defective` proves `advance` succeeds across all
three states (empty/missing/healthy); `test_report_c1_underlying_probe_still_discriminates_via_stdout`
runs the check text through the engine's own `_run_check_command` and asserts the stdout verdict
flips correctly. `CartographerW3PromoteDeclined` is not vacuous — it pins that zero conditions in
the file carry a `check`, catching any future accidental promotion or leftover edit.

### Fowler code-smell pass (r6-fowler)
Record written to `.agent-work/w3-promote/FOWLER_PASS.json`; `verify_fowler_pass.py` exits 0
(`smells=12, flagged=[], overridden=['duplicated-code']`). All 12 baseline smells rendered a
verdict; 11 `absent`, 1 `overridden` with a logged reason. The one real smell: `_skip_if_head_moved`
is duplicated verbatim across all 6 `W3Promote*` test classes in this file, including the 2 new
ones. Overridden because `notes-1.md` (lines ~321-326) documents this as a deliberate, epic-wide
red-proof idiom copied from `w2-basis`'s `CommanderSpineBasisFields` class and already reused
identically by every prior gate's own class (g1/g3/g4/g5) before this one — the duplication buys
per-class independence (separately pinned to different `HEAD`s, separately removable) that a shared
mixin would couple away. No other smell found: the classes are smaller than every sibling class
already in the file, the shell command and check dicts add no unnecessary abstraction, and the long
`map_check_note` documents genuine design rationale rather than papering over a defect in the
command itself (which is independently simple and correct).

## Map impact verdict
- **Evidence supports claimed change:** yes — the `report` step's postcondition is now backed by a
  real, executed, discriminating probe rather than an honest-but-unchecked attest; verified by
  running the command myself, not by reading the implementer's paste.
- **Constraints not violated:** yes — `decision:no-new-check-kinds`, `decision:no-basis-backfill`,
  `decision:blocking-where-adjudicated` all independently re-verified as honored (see Evidence
  verdict above).
- **Notes match the diff:** yes — "no code changed, reuses existing `command` check-kind machinery"
  matches the diff exactly (JSON-only + test-only edit, `checklist_engine.py` untouched).
- **Decision candidates surfaced:** n/a — no new authority was required; the report-only default is
  a direct, cited application of an already-settled decision (`decision:blocking-where-adjudicated`),
  not a fresh judgment call needing escalation.
- **Durable context routed:** yes — the triage candidates (re-assess `packets.c1`/`index-overlays.c1`
  once `docs/architecture/` is restored; revisit `report.c1`'s report-only status per its own named
  trigger) are named in Map Impact and repeated in the implementer result's Triage section, not
  dropped.

## Reconciliation check
No structural baseline concerns. The map is independently confirmed DEGRADED-UNPARSEABLE right now
(`docs/architecture/generated/map.json` has empty `findings`/`nodes`/`relationships`), which is a
pre-existing, repo-wide condition this gate correctly declined to build a check against rather than
one this gate caused or should fix.

## Blockers
- None.

## Out-of-scope observations
- `packets.c1`/`index-overlays.c1` in `CARTOGRAPHER.template.json` remain genuinely re-assessable
  once `docs/architecture/` carries a real, parseable map again — already named as a triage candidate
  by the implementer, not a new finding, but worth Commander confirming it lands in Triage rather
  than being lost at closeout.

## Workflow Feedback
- **Handoff gaps:** none of substance. The Close Criteria were specific enough that every claim
  could be independently re-derived without guessing at the implementer's intent — including the
  "run it yourself in a scratch directory" instruction, which caught real, load-bearing behavior
  (the `-s` vs `-f` boundary) that reading the diff alone would not have surfaced with confidence.
- **Context rediscovered:** none beyond what the handoff already anchored — the `<repo-root>`
  resolver claim (`scripts/init_work_area.py::resolve_spine`, line 148) was independently spot-
  checked since the implementer's own result flagged it as something they had to trace by hand; it
  checked out.
- **Instructions improvised around:** this review ran as an in-harness subagent whose `SPINE_*` env
  points at the dispatching Commander's own bound spine, not a spine of this reviewer's own — per
  this crew's system framing, no `mcp__spine__*` tools were available or attempted. The
  constellation-reviewer skill's engine-drive instructions (claim a lease, drive `current`/`advance`
  through the MCP door) do not apply in this configuration; I built a plain survey record
  (`FOWLER_PASS.json`) and this result file directly instead, per the skill's own fallback for "no
  spine bound... you are driving your own process's spine directly." Worth Commander confirming this
  is the intended dispatch shape for a reviewer crew at this tier, since the skill's primary
  instructions assume an MCP-reachable door.
- **What would have made this easier:** nothing concrete — the handoff was thorough and each Close
  Criterion pointed at a specific, checkable command.

## Return status
`complete`
