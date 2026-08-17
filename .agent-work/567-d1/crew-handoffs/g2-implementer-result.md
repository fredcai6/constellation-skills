# Implementation Result

## Assigned gate

`g2-implement` — sweep the corpus **and the tracked overlay**, and invert the mandate
(issue #559, epic #567, wave 2, lane D1).

## Return status

Return status: `complete`

## Completed slice

All three halves, in one gate:

- **(a)** 13 `CLI fallback` clauses and 10 `<engine>` occurrences swept from `skills/`
  (excluding `skills/workbench/`), plus the `write-a-skill/SKILL.md:20` drive-path cell the
  guard deliberately does not flag; then propagated to the tracked `.agent-work/templates/`
  overlay and its `.baseline/` mirrors — 16 `<engine>` and 18 clause occurrences across 10
  files there.
- **(b)** The nine mandating assertions in `tests/test_mcp_adoption.py` inverted or deleted
  (**plus a tenth the handoff's table missed** — see the ledger), and the two stale entries in
  `tests/data/store_mentions.approved.txt` regenerated through the guard's own code path.
- **(c)** The specificity proof, both directions, at a reworded second-checklist site.

The guard was not edited. Its non-workbench site list is empty as a consequence of the sweep.

## Scope

**Files changed (23):**

| Area | Files |
|---|---|
| `skills/` (11) | `admiral/templates/ADMIRAL_SPINE.template.json`, `charter/SKILL.md`, `commander/references/commander-core.md`, `commander/references/crew-dispatch.md`, `commander/templates/COMMANDER_SPINE.template.json`, `explorer/SKILL.md`, `explorer/templates/EXPLORER_SPINE.template.json`, `interrogator/SKILL.md`, `write-a-skill/SKILL.md`, `write-a-skill/templates/gated-engine-SKILL.template.md`, `write-a-skill/templates/survey-SKILL.template.md` |
| `.agent-work/templates/` (10) | the 5 visible doctrine templates + their 5 `.baseline/<skill>/` mirrors |
| `tests/` (2) | `test_mcp_adoption.py`, `data/store_mentions.approved.txt` |

**Fenced paths touched:** `none`. `skills/workbench/**`, `scripts/**`, `docs/**`,
`episodes/**`, `map/INDEX.md` and `tests/test_cli_retirement_guard.py` are all unmodified
(`git status --porcelain` over the repo lists only the 23 files above plus this run's own
artifacts).

**Constraint 1 honored:** every shipped compact-format JSON template was edited as **raw
text** with asserted-unique substring replacements (`assert raw.count(old) == 1` per edit) and
re-validated with `json.load`. No file was round-tripped through `json.dump`.

## Half (a) — the sweep, site by site

### The 10 bound-spine sites — the CLI line deleted, the door named as the path

The removed sentence and the sentence that framed it as a choice both went: leaving *"by
default … otherwise"* behind keeps the two-path idea alive in grammar after the second path is
gone. Where a `<engine>` command was the only instruction for a real action (a waiver), it was
converted to the equivalent door-tool call rather than deleted — no agent or human is left
without a path.

| # | Site | What replaced it |
|---|---|---|
| 1 | `ADMIRAL_SPINE` `.tasks.init.imperative` | clause + the `--session-id`-forever sentence deleted; the door sentence now ends *"…so the door needs no session id argument: it reads the spine it is bound to, and the session it drives that spine under, from its own environment."* |
| 2 | `ADMIRAL_SPINE` `.tasks.closeout.imperative` | clause deleted; *"call the spine_lease MCP tool with action=release (your own spine; no session id argument needed)."* |
| 3 | `charter/SKILL.md:12` | *"Drive `templates/CHARTER.template.json` as a `gated` checklist through the MCP door's `spine_status`/`spine_start`/`spine_advance`/`spine_evidence` tools (…) — Charter is orchestrator-tier and owns the process's bound spine, so the door drives this checklist directly: …"* |
| 4 | `commander-core.md:127` | *"— via the `spine_evidence` MCP tool (`action=attach`, …), since this is the Commander's own bound spine and needs no session id argument — with the Admiral as ratifying authority…"* |
| 5 | `COMMANDER_SPINE` `.tasks.init.imperative` | clause + the `--session-id`-forever sentence deleted; ends at *"…it reads SPINE_SESSION from its own environment."* (the stale-lease escape survives as `force=true`/`reason=` on the door call) |
| 6 | `COMMANDER_SPINE` `.tasks.plan.imperative` | **two edits.** The `<engine> waive plan --cond c6 …` command became *"(the spine_evidence MCP tool with action=waive, task_id=plan, condition_id=c6, which=postconditions, authority=human, reason='…')"*; the `CLI fallback: attach plan --type user-decision …` clause deleted |
| 7 | `COMMANDER_SPINE` `.tasks.archive.imperative` | **two `<engine>` occurrences, both edited.** `<engine> waive archive --cond c4 …` became the `spine_evidence` waive call; `CLI fallback: <engine> release …` deleted |
| 8 | `explorer/SKILL.md:31` | clause and the trailing *"pass `--session-id <work-id>` on every mutating CLI call"* deleted; *"…then `claim` the session lease through the door, which reads its own spine and session from the process environment and takes no session id argument."* |
| 9 | `EXPLORER_SPINE` `.tasks.init.imperative` | clause + `--session-id`-forever sentence deleted |
| 10 | `EXPLORER_SPINE` `.tasks.route.imperative` | clause deleted; *"Attest c1."* retained |
| — | `crew-dispatch.md:35` (`<engine>`, no clause) | *"(the `spine_halt` MCP tool with `action=block`)"* — the `, or the CLI `<engine> block`` alternative deleted |

**The `<engine>` census, by occurrence:** 10 occurrences on 9 lines. `COMMANDER_SPINE`
`.tasks.archive.imperative` carried two on one line and **both** were edited — a per-line sweep
would have left one.

### The handed-over prose target the guard will not flag

`skills/write-a-skill/SKILL.md:20`, the archetype table's Shape cell:

- **before:** `a `templates/*.json` checklist driven through `checklist_engine.py` (`commander`)`
- **after:** `a `templates/*.json` checklist driven gate by gate through the MCP door (`commander`)`

It asserted the drive-path belief #559 removes. The replacement states the drive path that is
now true rather than deleting the cell, so the archetype table still says what a gated-engine
skill *is*.

### The 3 second-checklist sites — reworded, before and after

The wording constraint was respected everywhere: these paragraphs **name** the engine as what
drives a second checklist, and **show no command** — no path, no interpreter, no flag, no
placeholder followed by an engine verb. I did not need to show a command, so no stop condition
fired. The word *"fallback"* is gone from all three, deliberately: *a fallback implies a
working primary, and here there is none.*

**Site 11 — `skills/interrogator/SKILL.md`**

> **before:** Default path, when your survey file *is* the spine this process's MCP door was
> launched for: the door's `spine_status`/`spine_survey_result`/`spine_evidence` tools (see
> workbench `references/checklist-engine.md` — MCP door). CLI fallback, always available: the
> absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`,
> workbench `references/checklist-engine.md`). **Use the CLI whenever the door is bound to
> someone else's spine — which is the usual case here.** Interrogator runs in the invoking
> agent's own human-reachable context, … Check what the door is bound to before you reach for
> it; when in doubt, the CLI is always correct.
>
> Two verbs on this loop have no door tool at all and always take the CLI: `append` follow-ups
> and new branches as answers open them, and `skip` questions an earlier answer settled.

> **after:** When your survey file *is* the spine this process's MCP door was launched for,
> drive it through the door's `spine_status`/`spine_survey_result`/`spine_evidence` tools (see
> workbench `references/checklist-engine.md` — MCP door). **Usually it is not.** Interrogator
> runs in the invoking agent's own human-reachable context, so it shares that agent's process
> and therefore that agent's door binding: a Commander drives `interrogation.json` through this
> skill while its own door stays bound to `spine.json`, and a door call from inside the
> interrogation would operate on the Commander's spine, not on the survey you own. **Check what
> the door is bound to before you reach for it.**
>
> The door cannot be moved onto your survey either: one door drives one spine at a time, and it
> refuses to rebind while its owner still holds that spine's lease — which is exactly the state
> the agent hosting you is in. So a survey the door is not bound to is not a second-best path
> with a working primary behind it; it is driven by this skill's bundled checklist engine, and
> by nothing else. Two of its verbs have no door tool at all, so that is their only path in any
> case: `append` follow-ups and new branches as answers open them, and `skip` questions an
> earlier answer settled.

**Note — an adjacent sentence the handoff did not list.** The second paragraph ("always take
the CLI") is not a guard target and was not one of the 13, but it is the same claim as the
clause above it and would have contradicted the reword. I carried it into the same vocabulary
rather than leaving the paragraph pair inconsistent, and its **fact** (`append` and `skip` have
no door tool) is preserved unchanged. Reported here rather than done silently.

**Site 12 — `skills/write-a-skill/templates/gated-engine-SKILL.template.md:15`**

> **before:** Build a `gated` plan from `templates/<NAME>_PLAN.template.json` and drive it — by
> default via the MCP door's `spine_status`/`spine_start`/`spine_advance`/`spine_evidence` tools
> (…) when this agent owns the process's bound spine, otherwise (and always for an in-session
> dispatched crew member driving its own plan) the CLI fallback: through
> `scripts/checklist_engine.py`. One item per step, …

> **after:** Build a `gated` plan from `templates/<NAME>_PLAN.template.json` and drive it. When
> this plan *is* the spine this process's door is bound to, drive it through the MCP door's
> `spine_status`/`spine_start`/`spine_advance`/`spine_evidence` tools (…). An in-session crew
> member driving its own plan beside the spine it was launched for is not that case: one door
> drives one spine at a time, and it refuses to rebind while its owner still holds that spine's
> lease, so the door cannot reach your plan at all. That is not a second-best path with a
> working primary behind it — such a plan is driven by this skill's bundled checklist engine,
> and by nothing else. One item per step, …

**Site 13 — `skills/write-a-skill/templates/survey-SKILL.template.md:11`**

> **before:** Drive a `survey` checklist — by default via the MCP door's
> `spine_status`/`spine_survey_result`/`spine_evidence` tools (…) when this agent owns the
> process's bound spine, otherwise (and always for an in-session dispatched crew member driving
> its own survey) the CLI fallback: through `scripts/checklist_engine.py`. **Visit every item, …**

> **after:** Drive a `survey` checklist. When this survey *is* the spine this process's door is
> bound to, drive it through the MCP door's `spine_status`/`spine_survey_result`/`spine_evidence`
> tools (…). An in-session crew member driving its own survey beside the spine it was launched
> for is not that case: one door drives one spine at a time, and it refuses to rebind while its
> owner still holds that spine's lease, so the door cannot reach your survey at all. That is not
> a second-best path with a working primary behind it — such a survey is driven by this skill's
> bundled checklist engine, and by nothing else. **Visit every item, …**

### The overlay

Measured before propagation, by occurrence: **16 `<engine>` and 18 clause occurrences across
10 files** (5 visible copies + 5 `.baseline/` mirrors) — not the 7-across-5 a line count
suggests. All ten were **blob-identical to their unswept `skills/` sources at `HEAD`**, verified
with `git hash-object` before touching them, which is what made whole-file propagation correct
rather than a merge.

After propagation, all three copies of each file share one blob OID:

```
file                                   skills/ source                             overlay                                    .baseline/ mirror
ADMIRAL_SPINE.template.json            cc5db8eecb58ef1716541d96ef65c46d7552f9a9 cc5db8eecb58ef1716541d96ef65c46d7552f9a9 cc5db8eecb58ef1716541d96ef65c46d7552f9a9  MATCH
COMMANDER_SPINE.template.json          3ba74fa199cd03c45cb443f7d9476363beb5356c 3ba74fa199cd03c45cb443f7d9476363beb5356c 3ba74fa199cd03c45cb443f7d9476363beb5356c  MATCH
EXPLORER_SPINE.template.json           3a6165ddaf2619a0e40ee4357cd7f52dc0ce8d61 3a6165ddaf2619a0e40ee4357cd7f52dc0ce8d61 3a6165ddaf2619a0e40ee4357cd7f52dc0ce8d61  MATCH
gated-engine-SKILL.template.md         196319da3450a6d61b3748a060dd6d1abd6dea55 196319da3450a6d61b3748a060dd6d1abd6dea55 196319da3450a6d61b3748a060dd6d1abd6dea55  MATCH
survey-SKILL.template.md               4c73056da1ccfff15b87084b6ac8810f6b9081bb 4c73056da1ccfff15b87084b6ac8810f6b9081bb 4c73056da1ccfff15b87084b6ac8810f6b9081bb  MATCH
```

**The launch order's acceptance test, run rather than argued.** A fresh spine instantiated from
the *overlay* COMMANDER template into a scratch root:

```sh
python3 scripts/init_work_area.py accept-567-d1 --root /tmp/g2-accept \
  --spine .agent-work/templates/COMMANDER_SPINE.template.json --skill-dir <commander-skill-dir>
```

```
==================== init ====================
  <engine> occurrences: 0
  clause occurrences  : 0
==================== plan ====================
  <engine> occurrences: 0
  clause occurrences  : 0
```

The `init` imperative a Commander is now handed ends: *"…this is your own spine (the one this
process's door is bound to), so the door needs no session id argument, it reads SPINE_SESSION
from its own environment."* — and stops there.

## Half (b) — the inversion ledger

Every row states what happened and why. **Ten** assertions, not nine: the handoff's table
missed one of the same class.

| # | Assertion | Disposition | Reason |
|---|---|---|---|
| 1 | `TestTier1ImperativeFields::test_field_still_carries_cli_fallback` (7 fields) | **INVERTED** → `test_field_no_longer_carries_a_cli_command_line` | All 7 fields are this lane's and survive. Now asserts the exact removed command line is absent **and** `<engine>` is absent field-wide — the second half catches a *reworded* command that would not match the recorded literal. `TIER1_JSON_FIELDS`' fourth column is kept verbatim as the record of what was swept. |
| 2 | `TestTier1CommanderCoreAttachLine::test_paragraph_still_carries_cli_fallback` | **INVERTED** → `test_paragraph_no_longer_carries_a_cli_command_line` | Asserts the paragraph carries neither `<engine>` nor `checklist_engine.py`. **The locator had to move with it** — see the finding below. |
| 3 | `TestTier2SkillBodyDefaultPath::test_file_still_names_cli_at_all` | **INVERTED** → `test_file_hands_over_no_second_path_anywhere` | Scoped to the clause + placeholder, **not** to `checklist_engine.py` — see the finding below. |
| 4 | `TestTier2SkillBodyDefaultPath::test_default_path_paragraph_is_two_sided` | **INVERTED** → `test_door_path_paragraph_names_the_door_and_not_the_cli` | The door half is unchanged in strength; the CLI half became absence. |
| 5 | `skills/workbench/SKILL.md` entry in `TIER2_SKILL_FILES` | **DELETED** | **Rule 2.** Lane D2's file, still carries the swept text, has not merged. An inverted assertion would go red on a file this lane is fenced from. |
| 6 | `TestTier3ChecklistEngineReference::test_still_names_cli_invocation` | **DELETED** | **Rule 2** — lane D2's file. |
| 7 | `TestTier3ChecklistEngineReference::test_door_section_itself_keeps_the_cli` | **DELETED** | **Rule 2** — lane D2's file; also depended on `CANONICAL_CLI_SENTENCE`, deleted with it. |
| 8 | `TestTier3ChecklistEngineReference::test_states_identity_trade_rule` | **DELETED** | **Not in the handoff's table — the tenth.** It required lane D2's file to carry a sentence routing a dispatched subagent *to the CLI* for its own plan. That claim is false since `run_crew.py --spine` binds a crew's own spine (the same fact `TestTier2SpineAlreadyBoundForDispatchedCrews` already records), and it is a CLI-presence mandate on a fenced file, so it is rule 2's class exactly. |
| 9 | `TestTier4AuthoringTemplate::test_file_still_names_cli_at_all` | **INVERTED** → `test_file_never_names_the_cli_at_all` | Both files are this lane's. Kept **whole-file strict** (unlike Tier2) because an authoring template has no scripts manifest and no reason to name the engine as a component — a mention here propagates into every skill minted from it. |
| 10 | `TestTier4AuthoringTemplate::test_default_path_paragraph_is_two_sided` | **INVERTED** → `test_door_path_paragraph_names_the_door_and_not_the_cli` | As row 4. |
| 11 | `TestCLIStaysAvailableNotDeprecated::test_the_canonical_cli_sentence_is_present_verbatim` | **DELETED** | **Rule 2** — a byte equality on a sentence inside lane D2's file. |
| 12 | `TestCLIStaysAvailableNotDeprecated::test_default_path_paragraph_states_the_cli_is_still_available` | **DELETED** | Its whole premise is gone: it required the word *"fallback"* / *"always available"* in every Tier2 and Tier4 drive-path paragraph — the exact clause the sweep removes. |
| 13 | `TestTier5DoNotTouch::test_still_names_checklist_engine_as_artifact` | **UNCHANGED**, deliberately | It asserts only that two files still **name** `checklist_engine.py` as a component — *"the engine rail string table (`checklist_engine.py`, #140)"*, *"nothing enforces the execution-time half in code — `checklist_engine.py` does not"*. No path, interpreter, flag or verb beside it; the guard's own line (`TestTheInvocationPredicateItself`) sits in exactly the same place. Inverting it would assert something the epic did not decide and go red on two files nothing swept. The reasoning is now written into the class docstring. |
| 14 | `TestTier3CLIOnlyVerbsStayCLI` (1040) and `TestCLIOnlyVerbsAcrossEveryInstructionFile` (1163) | **UNCHANGED** | A different claim (the gap between engine verbs and door tools), `CLI_ONLY_VERBS` is empty, neither broke. |

**Assertions deleted because the target is another lane's file, named explicitly as the handoff
asked:** rows 5, 6, 7, 8, 11. Coverage of their *absence* half is not lost —
`tests/test_cli_retirement_guard.py` walks the whole corpus including `skills/workbench/**`.
**What is genuinely lost is row 5's paragraph-scoped DOOR assertion for
`skills/workbench/SKILL.md`**, which nothing else replaces; the code comment says so and says
re-adding the entry after D2 merges restores it. That is a real, stated reduction, not a wash.

**Door-affirmative halves: none weakened.** `test_field_names_door_tool_as_default`,
`test_paragraph_names_door_tool`, `test_names_door_tools_as_default`,
`test_no_door_tool_name_introduced` and `TestTier2SpineAlreadyBoundForDispatchedCrews`' three
are untouched.

**`TestCLIStaysAvailableNotDeprecated` was kept, not emptied.** Its docstring is the measured
record of the deleted polarity predicates that two other files cite by name — including the
guard, which names this class as the precedent for refusing to build a predicate that reads
English. It now opens by stating that #559 superseded the *corpus* reading of "the CLI door
stays" and narrowed it to its true half, and carries one live assertion,
`test_the_engine_survives_as_a_tool_even_though_no_instruction_names_it`: the engine file still
exists and still registers all 18 verbs, read from its own argparse registry. That is a
narrower claim than what it replaced, and it is the protected intent stated as a check — the
epic removed an agent-facing path, not a tool.

### Two findings that changed how the inversion had to be written

**1. The `commander-core.md` locator was keyed to the text being deleted.** `_attach_paragraph()`
found its paragraph by requiring `'<engine> attach' in para`. After the sweep it could find no
paragraph at all — so **both** assertions in that class, including the door-affirmative one that
is explicitly not mine to weaken, would have died with an unrelated *"has the CLI line moved?"*
message. The locator now keys on the door tool, which is what must be present. A locator keyed
to what must be *absent* cannot survive its own sweep.

**2. Tier2's whole-file absence cannot be `checklist_engine.py not in text`** — the standard
`TestTier2SpineAlreadyBoundForDispatchedCrews` uses for its two files. `skills/explorer/SKILL.md`
carries a scripts manifest: *"Scripts: `checklist_engine.py`, `init_work_area.py`,
`run_crew.py`, …"*. That names the engine as a component and tells nobody to run it — the prose
side of the exact line the epic drew and the guard pins in both directions. Tier2 is therefore
scoped to the `CLI fallback` clause and the `<engine>` placeholder; Tier4 stays whole-file. This
surfaced as a real RED during the work, not as a prediction.

### `tests/data/store_mentions.approved.txt`

**There is no generator.** `scripts/verify_retirement.py` has only a scan CLI; its own comment
("one code path, used by the leg AND by whatever seeds the census") describes a seeding path
nothing in the repo implements. So the handoff's *"do not hand-edit it if a generator exists"*
resolved to: derive the entries **mechanically through that same code path**. I did —
`store_mention_sites()` produced the new normalized lines, `load_approved()` + `_read_lines()`
identified the two stale ones, and the swap refused unless each was a clean 1:1 pairing within
its own file. Two lines changed (the ADMIRAL closeout and COMMANDER archive imperatives); every
reason comment and the census structure are untouched.

```
$ python3 scripts/verify_retirement.py ; echo "exit:$?"
exit:0
```

## Half (c) — the specificity proof, verbatim, both directions

**The scratch edit.** A genuine clause appended to the *reworded* paragraph in
`skills/interrogator/SKILL.md` — the same file, one line below the reword, saying nearly the
same thing:

> `CLI fallback, always available: the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`).`

### Direction 1 — RED, and it names the site

```
$ python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g2-guard-red.log 2>&1; echo "pytest exit: $?"
pytest exit: 1

### site addresses the guard names, non-workbench only:
skills/interrogator/SKILL.md:28

### the interrogator excerpts, verbatim from the failure messages:
E             skills/interrogator/SKILL.md:28
E                 ...checklist engine, and by nothing else. CLI fallback, always available: the absolute path to...
--
E             skills/interrogator/SKILL.md:28
E                 ...this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engin...

### summary line:
=========================== short test summary info ============================
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_cli_fallback_clause_reaches_an_agent
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_engine_invocation_reaches_an_agent
2 failed, 17 passed in 0.09s
```

### Direction 2 — reverted, and GREEN on the reworded text itself

```
$ cp /tmp/g2-interrogator-shipped.md skills/interrogator/SKILL.md
### scratch edit reverted; diff vs shipped-swept content:
(identical)

$ python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g2-guard.log 2>&1; echo "pytest exit: $?"
pytest exit: 1

### site addresses, non-workbench only (must be empty):
### end
=========================== short test summary info ============================
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_cli_fallback_clause_reaches_an_agent
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_engine_invocation_reaches_an_agent
2 failed, 17 passed in 0.09s
```

**Why this is discriminating rather than vacuous:** the reintroduction is flagged at
`skills/interrogator/SKILL.md:28`, one line **below** the reworded text at `:27` that describes
the same mechanism in the same words and is flagged by nothing, in either run. The guard is
separating the two sentences, not the two files. The two remaining failures are lane D2's four
addresses, unchanged across both directions.

### The tree after the revert

```
$ git status --porcelain -- skills tests .agent-work/templates
 M .agent-work/templates/.baseline/constellation-admiral/ADMIRAL_SPINE.template.json
 M .agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json
 M .agent-work/templates/.baseline/constellation-explorer/EXPLORER_SPINE.template.json
 M .agent-work/templates/.baseline/constellation-write-a-skill/gated-engine-SKILL.template.md
 M .agent-work/templates/.baseline/constellation-write-a-skill/survey-SKILL.template.md
 M .agent-work/templates/ADMIRAL_SPINE.template.json
 M .agent-work/templates/COMMANDER_SPINE.template.json
 M .agent-work/templates/EXPLORER_SPINE.template.json
 M .agent-work/templates/gated-engine-SKILL.template.md
 M .agent-work/templates/survey-SKILL.template.md
 M skills/admiral/templates/ADMIRAL_SPINE.template.json
 M skills/charter/SKILL.md
 M skills/commander/references/commander-core.md
 M skills/commander/references/crew-dispatch.md
 M skills/commander/templates/COMMANDER_SPINE.template.json
 M skills/explorer/SKILL.md
 M skills/explorer/templates/EXPLORER_SPINE.template.json
 M skills/interrogator/SKILL.md
 M skills/write-a-skill/SKILL.md
 M skills/write-a-skill/templates/gated-engine-SKILL.template.md
 M skills/write-a-skill/templates/survey-SKILL.template.md
 M tests/data/store_mentions.approved.txt
 M tests/test_mcp_adoption.py
```

No scratch text survives; the mutation file is byte-identical to the shipped swept content.

### The inverted assertions were red-proofed too

*A check that cannot fail is indistinguishable from one that passed* (`CREW_CONTEXT.md`,
Verification Discipline). Reinstating the exact removed command line in `COMMANDER_SPINE`
`.tasks.init.imperative`:

```
FAILED tests/test_mcp_adoption.py::TestTier1ImperativeFields::test_field_no_longer_carries_a_cli_command_line[skills/commander/templates/COMMANDER_SPINE.template.json-keys0-spine_lease-<engine> claim --session-id <commander-session-id>]
1 failed, 171 passed, 2 skipped in 0.13s
```

Reverted: `172 passed, 2 skipped`. The mutation was asserted to have applied
(`assert raw.count(old) == 1`) before the run, so this is not a `sed` that matched nothing.

## Close criteria

| # | Criterion | Result |
|---|---|---|
| 1 | `grep -rn -i 'CLI fallback' skills/ --exclude-dir=workbench` | **nothing** (exit 1) |
| 2 | `grep -rn '<engine>' skills/ --exclude-dir=workbench` | **nothing** (exit 1) |
| 3 | same two greps over `.agent-work/templates/` | **nothing**, mirrors included (exit 1, exit 1) |
| 4 | `python3 -m pytest tests/test_mcp_adoption.py -q` | **`172 passed, 2 skipped`** |
| 5 | guard fails only at `skills/workbench/` sites | **yes** — see below |
| 6 | overlay + mirrors match their `skills/` sources | **MATCH ×5**, table above |
| 7 | half (c) pasted both directions, scratch reverted | **yes**, above |
| 8 | `scripts/init_work_area.py:24` and the superpowers plan untouched | **yes** — `git diff --name-only` over both paths is empty; both still carry their `<engine>` |
| 9 | every edited `.json` parses | **yes**, `skills/**` and `.agent-work/templates/**` |
| — | the gate's own POSIX closing check, run through `/bin/sh` (dash) | **exit 0** |

### Criterion 5, and a defect in its command

The guard's four surviving addresses, all lane D2's:

```
skills/workbench/SKILL.md:37
skills/workbench/references/checklist-engine.md:5
skills/workbench/references/checklist-engine.md:41
skills/workbench/references/checklist-engine.md:45
```

Filtered to non-workbench: **empty**.

**The criterion's literal command cannot print nothing, for a reason that is not about my
work.** Every guard failure message carries the census sentence *"(scanned 3098 texts across
216 files (101 under skills/, 2 under specs/, 113 under .agent-work/templates/))"*, and

```sh
grep -oE '(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g2-guard.log | grep -v '^skills/workbench/' | sort -u
```

matches `.agent-work/templates/` **out of that prose** — it prints exactly that one token and
nothing else. `skills/` and `specs/` escape only by the accident of being followed by a comma.
So as written the criterion is satisfiable only when the guard is entirely green, which is the
state it explicitly says this lane cannot reach. The corrected filter, anchored to whole address
lines (the shape `_sites()` emits), prints nothing:

```sh
sed -E 's/^E? *//' /tmp/g2-guard.log \
  | grep -E '^(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+(:[0-9]+)?$' \
  | grep -v '^skills/workbench/'
```

I amended my own plan's check to the corrected form through the engine's `amend` verb rather
than hand-editing it, with the reason recorded.

## Test mode

**Required:** inversion-first. **Satisfied:** `yes` — the guard was already RED and was treated
as the specification. It was not edited; the corpus and the mandate were changed until its
non-workbench site list emptied. No exception list exists anywhere.

## Full-suite state, honestly

`python3 -m pytest tests/ -q` → **`6 failed, 3355 passed, 5 skipped, 1218 subtests passed`**.
The six, classified against a stashed-change baseline (my changes stashed, same command re-run):

| Failure | Mine? |
|---|---|
| `test_cli_retirement_guard.py` ×2 (`skills/workbench/**`) | **expected**, named cause, lane D2's — clears at `g5-final` on the rebased tree |
| `test_code_map.py::…root_index_matches_a_fresh_build` | **pre-existing** — fails identically with my changes stashed |
| `test_crew_launcher.py::…leaves_scratch_dir_unbound` | **pre-existing and environmental** — it asserts `CREW_SCRATCH_DIR` is absent from a launched env, and `run_crew.py` sets that variable in *this crew's own process*, so it fails for any crew running under `run_crew.py`. Fails identically with my changes stashed. |
| `test_retirement_guard.py` ×2 | **were mine, now fixed** — the stale census; both green after the regeneration above |

## Map Impact

- **Structural anchors touched:** `tests/test_mcp_adoption.py` — `_default_path_paragraph`
  **renamed** to `_door_path_paragraph` with its CLI and "default" requirements dropped;
  `TIER2_SKILL_FILES` shortened by one entry; five test methods renamed, five deleted.
  `tests/test_cli_retirement_guard.py` imports `INSTRUCTION_FILES`, `INSTRUCTION_SUFFIXES`,
  `_engine_verbs` and `_instruction_texts` from this module — **all four still exist and are
  unchanged**, so the g1 result's flagged hard dependency is intact (verified by the guard
  collecting and running).
- **Capabilities changed:** the corpus no longer hands any agent a second path to the engine
  outside `skills/workbench/**`. The adoption suite's Tier1/2/4 CLI half flipped from mandate to
  prohibition, generalizing `TestTier2SpineAlreadyBoundForDispatchedCrews` from 2 files to that
  whole surface.
- **Constraints/assumptions touched:** *"The CLI door stays; F is additive"* is now scoped to
  the **tool**, not the corpus — recorded in `TestCLIStaysAvailableNotDeprecated`'s docstring and
  pinned by its one surviving assertion. The prose-vs-command line (a scripts manifest may name
  the engine; nothing may show a command) is now relied on by `test_mcp_adoption.py` as well as
  by the guard.
- **Decision candidates:** whether `skills/workbench/SKILL.md` returns to `TIER2_SKILL_FILES`
  after lane D2 merges. It is a one-line restoration and the code says so; leaving it out
  permanently silently drops that file's door-affirmative paragraph check.
- **Claims/evidence produced:** the overlay hash-object table; the instantiate-a-fresh-spine
  acceptance run; the two-direction specificity proof; the Tier1 mutation proof.

## Out-of-scope observations (staged, not filed)

Nothing new rose to the level of a triage-candidate file this gate. Two items are recorded here
for the Commander instead, both already visible above:

1. **`tests/test_crew_launcher.py::ScratchDirResumeTests::…leaves_scratch_dir_unbound` fails for
   any crew launched by `run_crew.py`**, because the launcher exports `CREW_SCRATCH_DIR` into the
   crew's own environment and the test asserts its absence from a subprocess env it builds. It is
   green when a human runs the suite and red when a crew does. Not mine, not touched.
2. **`docs/agents/CREW_CONTEXT.md`'s "Python Invocation" measurement is still stale** (it records
   `python3` as lacking pytest; today all three of `py`, `python`, `python3` report pytest 9.1.1).
   The g1 crew reported this too. I re-measured before running anything, per that section's own
   instruction.

## Stop conditions hit

`none`. Specifically: no reworded second-checklist site needed to show a command line; no
assertion required weakening a door-affirmative half to invert; no fenced file was needed; and
the guard fired on no text I believe is legitimate outside `skills/workbench/`.

## Workflow Feedback

**What helped.**
- The handoff's *"count by occurrence, not by line, and not by visible file"* warning, with the
  `COMMANDER_SPINE.archive` two-tokens-on-one-line example named. I would have written a
  one-per-line sweep and left one behind.
- Naming the mechanism of the regrowth (a test mandates the text) at the top rather than as a
  footnote. It made the ordering obvious: the corpus edit and the inversion are one gate.
- The `.baseline/` mirror count. A `git status` after propagation showing 10 modified files
  instead of 5 is the only signal that the mirrors were real, and the handoff predicted it.

**What got in the way.**
- **Close criterion 5's filter command is defective** (documented above): it matches
  `.agent-work/templates/` out of the guard's own census sentence, so it cannot print nothing
  while the guard is red at all — which is the precise state the criterion was written to
  accommodate. I copied it verbatim into my plan and it failed on prose. Anchoring the pattern to
  a whole line fixes it.
- **The nine-assertion table was a nine-of-ten enumeration.** `test_states_identity_trade_rule`
  is the same class (a CLI-presence mandate on lane D2's file) and was not listed. A handoff that
  enumerates by line number invites treating the list as closed; *"these nine, and anything else
  of the same class you find"* would have cost nothing.
- **The handoff assumed a generator for `store_mentions.approved.txt`.** There is none — only a
  comment describing one. *"Regenerate through its own code path, hand-typing nothing"* is the
  instruction that survives contact with the repo.
- The implementer skill still presents a `run_crew.py` dispatch as arriving with a bound spine.
  Mine did not: my environment carried only `SPINE_PARENT`, and `crew-runs.json` registers this
  crew with `"spine": null`. I took the skill's other branch (author my own plan, claim the lease
  first). This is the third consecutive crew on this lane to report the same gap.

**My own mistakes.**
1. **I wrote my own m3 check as a bare name grep over the whole test file**, so it fired on the
   deliberate historical citations the inversion is *supposed* to leave in the docstrings — the
   check could not tell a deleted assertion from a record that it was deleted. Fixed through the
   engine's `amend` verb, rescoped to the `def ` line and widened to all eight retired names.
   The lesson is the file's own rule 2, applied to my plan instead of to the corpus: I asserted
   over text that describes the fact rather than over the fact.
2. **My first Tier2 inversion was `checklist_engine.py not in text`**, copied from the two-file
   precedent without checking whether the precedent's files resembled mine. `skills/explorer/SKILL.md`
   has a scripts manifest; the assertion went red on honest prose the epic deliberately left
   alone. Caught by running the suite, not by reading — I had the guard's docstring open, which
   states that exact distinction, and still generalized past it.

**What would have made this easier.** State the counting unit in every census (the handoff does,
and it was the single most useful thing in it), and pre-run any filter command a criterion hands
down against a *red* log rather than a green one — a filter that only works on an empty input is
not a filter.
