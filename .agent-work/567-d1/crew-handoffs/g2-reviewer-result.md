# Review Result

Reviewer session: `constellation/567-d1/g2/reviewer/attempt-1` · Parent: `constellation/567-d1/lane-d1/commander-delegated`
Survey: `.agent-work/567-d1/g2-review/review.json` (7 template items + 3 appended, all visited, consolidated)
Fowler record: `.agent-work/567-d1/g2-review/FOWLER_PASS.json` (rail exit 0)
Diff reviewed: commit `aeba10ae`, 23 files over `skills/`, `.agent-work/templates/`, `tests/`.

## Assigned Gate
`g2-review` — Sweep the corpus and the tracked overlay, and invert the mandate.

## Result
`APPROVE`

One check is recorded `fail` (`r4a-wording`) and the consolidation carries an explicit
`--override-reason`. The finding is real and is not softened below; it does not bar this change,
and it is also filed as a triage candidate. Nothing was downgraded to get APPROVE through.

## Handoff compliance

All eight close criteria re-run by me, exit codes read, none accepted from the report.

| # | Criterion | My result |
|---|---|---|
| 1 | `grep -rn -i 'CLI fallback' skills/ --exclude-dir=workbench` | exit 1, no output |
| 2 | `grep -rn '<engine>' skills/ --exclude-dir=workbench` | exit 1, no output |
| 3 | Same two greps over `.agent-work/templates/` | both exit 1, no output |
| 4 | `pytest tests/test_mcp_adoption.py -q` | **172 passed, 2 skipped**, exit 0 |
| 5 | Guard reports no violation outside `skills/workbench/` | exit 1; site list outside workbench **empty** |
| 6 | Overlay + `.baseline/` mirrors match `skills/` sources | all 5 templates byte-identical, three copies |
| 7 | `scripts/init_work_area.py`, `docs/superpowers/…` untouched | untouched vs `HEAD` **and** vs `aeba10ae^` |
| 8 | Every edited `.json` parses | 41 files parse |

Two of these needed a non-vacuity check before they meant anything, because an absence grep over a
narrowed walk reads exactly like a passing guard:

- Criterion 3's grep **does** reach `.baseline/`: a control word matches 13 of the 56 baseline files.
- Criterion 5's guard walk is intact: `scanned 3098 texts across 216 files (101 under skills/, 2 under
  specs/, 113 under .agent-work/templates/)` — the same census the guard was authored against, with its
  `>=60` / `>=1800` floors passing.

The guard's two remaining failures name only `skills/workbench/SKILL.md` and
`skills/workbench/references/checklist-engine.md` — lane D2's files, known and expected.

Interpreter note: the handoff's `python3 -m pytest` works on this host despite `CREW_CONTEXT.md`'s
2026-08-10 measurement saying `python3` has no pytest. I ran criterion 4 under **both** `py` and
`python3` and got 172/2/exit 0 from each.

## Scope drift

None. 23 files: 11 under `skills/`, 10 under `.agent-work/templates/`, 2 under `tests/` — matching the
claim exactly. `tests/test_cli_retirement_guard.py` is not in the diff. No file under
`skills/workbench/` was touched, so lane D2's fence held. The only edits outside the corpus and the
overlay are the two test files the implementer floated an ownership gap on, and the sweep is
impossible without both.

## Evidence verdict

Every claimed side-effect was reproduced against the world, not read off the report.

**The 183 → 172 count reconciles exactly.** I built a detached worktree at `aeba10ae^`, confirmed
183 passed / 2 skipped there, and diffed collected node ids: **185 before, 174 after — 30 removed,
19 added, net −11.**

| Group | before → after | net |
|---|---|---|
| Tier1 field assertion (7 params) | inverted 7 → 7 | 0 |
| `commander-core` attach paragraph | inverted 1 → 1 | 0 |
| Tier2 `two_sided` / `file_still_names_cli` | 4 → 3 and 4 → 3 (workbench off the list) | −2 |
| Tier3 three deletions | 3 → 0 | −3 |
| Tier4 both assertions (2 params each) | inverted 2 → 2, 2 → 2 | 0 |
| `TestCLIStaysAvailableNotDeprecated` | 7 → 1 | −6 |

−2 −3 −6 = **−11**. Nothing silently lost.

**No door-affirmative half was weakened**, and I proved it structurally rather than by reading:
of the **75 functions present in both revisions, exactly one body differs** — `_attach_paragraph`,
whose locator had to move off the deleted text or both assertions in its class, including the
door-affirmative one, would have died with an unrelated "has the CLI line moved?" message.
`test_field_names_door_tool_as_default`, `test_paragraph_names_door_tool`,
`test_names_door_tools_as_default` and `test_no_door_tool_name_introduced` are byte-identical.

**The suite's two rules about itself hold.** `INSTRUCTION_FILES` and `INSTRUCTION_SUFFIXES` are
untouched, so the walk did not become a list; the only constant changes are `TIER1_JSON_FIELDS`
comments (its data is identical under `literal_eval`) and one entry off `TIER2_SKILL_FILES`. Every new
assertion is an absence or an existence fact, so none can be satisfied by the negation of what it
pins — the failure message a re-introduction produces quotes the ruling rather than describing it.

**The specificity proof reproduces in my hands.** I re-inserted the clause into
`skills/interrogator/SKILL.md` line 28 (asserting the anchor matched exactly once before editing);
the guard went to exit 1 naming `skills/interrogator/SKILL.md:28` under **both** the clause pattern
and the invocation pattern. `git checkout` restored blob `dc78419a` byte-identical, the guard
returned to workbench-only sites, and `git status --porcelain` shows no source change.

One correction to how that proof is described, not to whether it works: `:27` is a **blank line**.
The reworded prose is at `:26` and inside `:28` itself, and it contains neither trigger token
(`CLI fallback`, `checklist_engine.py`) — so "the same mechanism in the same words" overstates it.
What the run actually shows is the discrimination that matters: the guard separates a sentence that
hands over a runnable second path from a sentence that names the same mechanism in English, **inside
the same line of the same file**.

**`store_mentions.approved.txt` is a real regeneration, not a hand-edit dressed as one.** I
re-derived the census through `verify_retirement.store_mention_sites` over `git ls-files` +
`is_shipped`: **64 generated, 64 approved, zero difference in either direction**, and both swept
spine imperatives match through `normalize()` byte-for-byte. The file's remaining content is true of
the tree.

**The F-1 measured truth, re-measured by me.** Fresh process, git-backed scratch checkout, two spines
under its own `.agent-work/`: `spine_bind` to a second checklist **while holding your own lease** is
REFUSED — *"one door drives one spine at a time. Rebinding this door now would leave that lease held
by nobody."* After `spine_lease release`, it succeeds. That is exactly what the three reworded
second-checklist sites assert, so they state the measurement rather than avoiding the banned phrase.

## Code/doc quality

**The mandate inversion is right, and it is the part that mattered.** The old
`test_field_still_carries_cli_fallback` failed with *"the CLI door must stay, never be removed or
discouraged"* — that message is the regrowth mechanism, and it is gone, replaced by an absence
assertion whose failure text quotes the human ruling. The Tier1 inversion is also stronger than a
straight flip: it asserts both the exact removed command line **and** `<engine>` field-wide, so a
*reworded* command that no longer matches the recorded literal is still caught.

**Deletions.** Five are covered by the stated lane-D2 rule — the `skills/workbench/SKILL.md` entry off
`TIER2_SKILL_FILES`, `test_still_names_cli_invocation`, `test_door_section_itself_keeps_the_cli`,
`test_the_canonical_cli_sentence_is_present_verbatim`, and `test_states_identity_trade_rule`, the
tenth the handoff's table missed. I confirmed each targets `skills/workbench/**` (`TIER3_PATH` is
that file, and the byte-equality reads its `## MCP door` section), and that the guard genuinely
re-covers their absence half over the whole corpus.

**One deletion is not covered by that rule, and I flag it as asked:**
`test_default_path_paragraph_states_the_cli_is_still_available` — 5 of its 6 parameters target *this*
lane's files. Its stated reason is different and sound: it required the literal words "fallback" /
"still available" in every drive-path paragraph, which is the mandate #559 removes, so it cannot be
inverted into anything the new absence assertions do not already say. The implementer stated that
reason plainly in ledger row 12 rather than filing it under the D2 rule. Not a defect.

**The stated loss is real and is written where it will be read**: `skills/workbench/SKILL.md` loses
its paragraph-scoped *door* assertion until lane D2 merges, and that is a code comment in
`TIER2_SKILL_FILES`, not only a line in a report.

**One finding on the replacement wording** — the biggest question the handoff asked, and the answer is
mixed. The two-path grammar is genuinely gone: every "by default … otherwise the CLI fallback"
framing is now a single-path sentence, and the only surviving "fallback" words under `skills/`
(excluding workbench) are unrelated ones. But the ten bound-spine replacements assert that the door
*"reads its own spine and session from the process environment"* **at `init`** — and at Explorer,
Charter and Admiral `init` the spine does not exist until `init_work_area.py` runs inside that same
imperative, so `SPINE_FILE` cannot have named it at server start and the door is provably unbound at
the moment the sentence is read.

Measured, fresh process with no `SPINE_FILE`: `spine_lease claim` returns
*"REFUSED: no spine is bound to this door … Call `spine_bind` with the path to a spine that already
exists, or `spine_open` to mint a spine and bind this process to it."*

So **nobody is stranded** — the failure is visible and carries its own remedy, which is
`global-everyone.md`'s "fail visibly … no hidden fallback" working exactly as intended. What is lost
is that the corpus no longer carries the first move. `grep spine_open\|spine_bind` over `skills/`
excluding workbench returns **zero hits**; the single corpus mention is
`skills/workbench/references/checklist-engine.md:34` — lane D2's file — and it documents only
`spine_open` (mint), never `spine_bind` (adopt an existing spine), which is the case these three
sites are actually in. The deleted CLI clause is what used to carry that moment.

This does not meet the handoff's stop condition ("a replacement leaves an agent with no path"), it
breaks no close criterion, and the fix spans a fenced lane-D2 file — so it is a triage candidate, not
a block.

**Fowler pass** (12 smells, rail exit 0): two flagged, two overridden with the standard that wins.
Flagged — the adoption suite re-implements the guard's `CLI_FALLBACK_RE` inline, two definitions of
one predicate (the import direction forbids the obvious fix, since the guard imports *from* the
adoption suite); and prose grew +278/−198 while the test count fell 11, with `_door_path_paragraph`'s
docstring asserting a property nothing mechanically holds — the locator now selects a paragraph *by*
the door-tool property the test then asserts, so a file with two door paragraphs would have the clean
one selected and the corpus-wide catch would land in the guard instead. Overridden — `large-class` on
`TestCLIStaysAvailableNotDeprecated` (its docstring is the measured record two other files cite by
name) and `shotgun-surgery` on the 15 triplicated template edits (that triplication is the
install/customize/reconcile contract, not an accident).

**One typo in shipped doctrine.** `skills/admiral/templates/ADMIRAL_SPINE.template.json` `init`
imperative, and its overlay and `.baseline/` mirrors, now read *"the door needs no session id
argument**.:** it reads the spine it is bound to"* — a stray period before the colon. Cosmetic, but it
ships to every Admiral.

## Map impact verdict

- **Evidence supports claimed change:** yes — every figure in the implementer result re-derived
  independently and matched (23 files, 172/2, the census, the ledger, the regeneration).
- **Constraints not violated:** yes — survivors untouched, lane D2 fence held, the guard not edited.
- **Notes match the diff:** yes, with the two wording corrections recorded above (the `:27` line
  reference, and "the same words").
- **Decision candidates surfaced:** yes — the implementer floated the second-checklist finding rather
  than deciding it, and the Admiral's F-1 ruling governs the three sites.
- **Durable context routed:** two triage candidates raised on this survey (`tc1`, `tc2`).

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`), so there is no recorded structure
to diverge from. The change introduces no module, seam or dependency.

## Reconciliation check

One consequence Commander should carry forward rather than discover at `g5-final`: the sweep edited
the `.baseline/` mirrors, so `check_skill_freshness.py --project . --skills-root ~/.claude/skills` now
exits 1 with *"5 template(s) need reconciliation"* where it exited 0 before — I confirmed the
pre-change baselines matched the installed upstream exactly for all five. No test consumes it (every
freshness test builds its own tmp fixture), so no suite goes red; it clears on the next install or
`--update-baseline`.

## Blockers
- none

## Out-of-scope observations

1. **`TEMPLATES_MANIFEST.json` is a fourth copy of template truth, and it is now stale.**
   `.agent-work/templates/TEMPLATES_MANIFEST.json` records a `sha256` per template; the five edited
   ones no longer match it. Inert today — `check_skill_freshness.py` recomputes hashes from the files
   and never reads that field, and no test reads it either — but the guard's own docstring says *"a
   sweep must edit all three copies"* and there are four. Raised as `tc2`.
2. **The corpus never names the door's binding call.** Detail above; raised as `tc1`. The natural
   home for half of it is lane D2's `checklist-engine.md`, which documents `spine_open` but not
   `spine_bind`.
3. **After lane D2 merges, no file in the corpus will tell an in-session crew member how to invoke
   the engine for its own plan or survey** — and the door provably cannot reach it. That is the
   epic-level consequence of the F-1 measurement, already floated by the implementer and ruled on;
   worth confirming deliberately at `g5-final` rather than meeting it as a surprise. I am that agent
   in this run: I drove this survey through the engine using knowledge from the not-yet-swept
   workbench reference.
4. **The typo** in the Admiral spine `init` imperative (above) — a one-character fix across three
   copies, and the same edit must go through all three or criterion 6 breaks.

## Workflow Feedback

- **Handoff gaps:** the nine old line numbers were accurate and saved real time, and naming the tenth
  as findable rather than naming it was the right call — it made the ledger audit a check instead of a
  transcription. Two small frictions: the verification block says `python3 -m pytest`, while
  `docs/agents/CREW_CONTEXT.md` says `python3` has no pytest on this host (it does now — I ran both,
  which is what the CREW_CONTEXT rule asks for, but the two documents disagree and one of them is
  wrong). And the close-criteria table gave no non-vacuity check for the absence greps; I added the
  `.baseline/`-reachability and guard-census checks myself, and without them criteria 3 and 5 are
  indistinguishable from a narrowed walk — which is the exact failure this whole epic is about.
- **Context rediscovered:** whether an unbound door strands an agent. The handoff's question 1 asks
  "does it leave anyone stranded?" but neither the handoff nor `notes-1.md` §M1 covers the *cold-start
  orchestrator* case — M1's probe sets `SPINE_FILE` up front, so it measures the second-checklist
  case only. I had to read `mcp_spine_server.py` and run my own unbound probe to answer it. If the
  Commander had carried M1's scope boundary ("this measures a bound door rebinding, not an unbound
  one starting"), the answer would have been one grep away.
- **Instructions improvised around:** the reviewer skill says a `run_crew.py`-dispatched crew drives
  its own spine through the MCP door, but my `SPINE_FILE` was empty, so the door would have failed
  closed. I authored my own survey and drove it through the engine directly, which is the documented
  path for exactly that case — recording it because the skill's two branches read as either/or and my
  situation was a third. Separately, the `r6-fowler` postcondition path had to move to the gate-scoped
  location the handoff named; I took the template's own documented repair path (`amend`/`retext-check`,
  authority = the dispatching Commander) rather than hand-editing, and it worked first try. That
  repair path being written into the item's own imperative is the single most useful thing in this
  template.
- **What would have made this easier:** one line in the handoff pinning **which python** to use, and
  a note that `.agent-work/567-d1/567-d1/mechanical/` already exists — my first engine `record` wrote
  into that nested path, which looked for a moment like I had corrupted the work area.

## Return status
`complete`
