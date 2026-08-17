# Implementation Result

## Assigned gate
`g1-implement` — Author the regrowth guard against the DIRTY tree (issue #559, epic #567, wave 2, lane D1).

## Completed slice
Created `tests/test_cli_retirement_guard.py`, the guard that makes the third deletion of the
CLI-fallback doctrine stick. It walks the corpus and asserts the **absence** of three things in
agent-facing instruction text: the `<engine>` placeholder token, a `CLI fallback` clause in any
punctuation form, and a command-shaped `checklist_engine.py` invocation. It fails today, on the
real unswept corpus, naming real sites.

Nothing was swept. Nothing was made green.

## Scope
**Files changed:**
- `tests/test_cli_retirement_guard.py` (new, the only file created)

`git status --porcelain` over `skills specs docs scripts episodes tests map` shows exactly one
line: `?? tests/test_cli_retirement_guard.py`.

**Specific exclusions touched:** `no` — `tests/test_mcp_adoption.py` is imported, never modified;
nothing under `skills/`, `specs/`, `docs/`, `scripts/`, `episodes/` or `map/` was touched.

## Behavior changed
`no` — the deliverable is a test. No production or instruction text changed. The observable
change is that the suite now has a corpus-wide red that the sweep must clear.

## Scope expression: imported, not re-derived

The handoff left this to my judgement and asked me to say which and why. **I import the walk**
from `tests/test_mcp_adoption.py` (`INSTRUCTION_FILES`, `_instruction_texts`), using this
directory's existing cross-test-import idiom (`sys.path.insert` + `# noqa: E402`, as
`test_mcp_imperative_equivalence.py` does with `test_mcp_identity`).

Why import rather than re-derive: the handoff's own constraint is that the two "must not be able
to drift silently". A re-derived copy is two definitions of "agent-facing instruction text" that
agree today and diverge the first time either is edited, with nothing to notice. An import makes
the repo hold exactly one such definition; if the adoption suite's walk narrows, this guard's own
vacuity floors go red rather than passing quietly on a smaller corpus.

The extension the handoff asked for — `specs/**/*.toml` — is added locally as a **suffix rule**
(`SPEC_SUFFIXES`), applied by an `rglob`, because the adoption walk does not reach `specs/` at all.

**Exception list length: zero.** No file is named as an exclusion anywhere in the guard.

## Measured specificity of the walk (not asserted as a test — see below)

| path | in the guard's walk? |
|---|---|
| `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md` (pre-ruled survivor) | **False** |
| `scripts/init_work_area.py` (pre-ruled survivor) | **False** |
| `tests/data/store_mentions.approved.txt` | **False** |
| `tests/fixtures/legacy_spine_organic.json` | **False** |
| `tests/test_cli_retirement_guard.py` (the guard itself, which quotes all three patterns) | **False** |

Both pre-ruled survivors are excluded by the structural rule alone, named nowhere. I did **not**
turn this table into a test: CONVERGENCE finding F1 rules that proving a walk over `skills/`
ignores `docs/superpowers/` proves only that an rglob is an rglob. It is reported here as a
measurement, which is what F1 asks for.

Forward-looking probe for g2, same reason: the lane's planned reword for the three door-refused
sites — *"The CLI is the only path for a second checklist, because the door refuses to rebind
while you hold your own lease."* — is **not** flagged by any of the three patterns. Reintroducing
an actual fallback clause at one of those sites is what would make it red. That is F1's
discriminating proof, and it belongs to g2 where the reworded text will exist.

## Map Impact
- **Structural anchors touched:** `tests/test_cli_retirement_guard.py` — new module, module level.
  It takes a **hard inbound dependency** on `tests/test_mcp_adoption.py`'s `INSTRUCTION_FILES` and
  `_instruction_texts` (both private-by-underscore in that module, imported deliberately). Gate g2
  inverts `test_mcp_adoption.py`; if that inversion deletes or renames either symbol, this guard
  fails at import. That is intended — loud, not silent — but g2 must expect it.
- **Capabilities added:** corpus-wide regrowth detection for the #559 doctrine. Previously the
  ruling was pinned for **2 files** (`TestTier2SpineAlreadyBoundForDispatchedCrews`); it is now
  pinned across **103 files / 1007 texts**. This guard is that precedent generalized, not a new
  invention.
- **Constraints/assumptions touched:** honors "the corpus is WALKED, never listed" (rule 1 of
  `test_mcp_adoption.py`'s own header) and "any guard that loops must assert what it looped over"
  (`docs/agents/CREW_CONTEXT.md`, Verification Discipline). Newly relied on: `specs/` exists and
  holds `.toml` door doctrine — asserted by a floor rather than assumed.
- **Decision candidates:** the invocation predicate draws a line between *"run this from a shell"*
  and *"this file is the engine"*. That line is mine, measured (10 command forms caught, 6 prose
  mentions left alone), and pinned in the assertion path by
  `TestTheInvocationPredicateItself` so a later edit cannot move it quietly. If the Commander
  wants a stricter line — no mention of `checklist_engine.py` at all under `skills/` — that is a
  one-line change, but it red-lights 6 sites nobody has ruled on, including three in
  `skills/_shared/global-everyone.md`.
- **Claims/evidence produced:** the guard is RED on the unswept tree for the right reason
  (collects cleanly; 3 corpus tests fail; 6 scaffolding/predicate tests pass), and the adoption
  suite stays fully green beside it (`189 passed, 2 skipped`).
- **Triage candidates:** see Out-of-scope observations.

## Test mode
**Required:** `test-first` (the gate's entire deliverable is a test, and it closes on that test
being RED for the right reason).
**Satisfied:** `yes` — the guard exists, collects cleanly, and fails against the real corpus. It
was not made green, and no instruction file was edited to move it.

## Evidence

Run from `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`.

```bash
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q
```
**Result:** `9 tests collected in 0.04s` — collection is clean, so the failure below cannot be an
import error misread as a finding.

```bash
python3 -m pytest tests/test_cli_retirement_guard.py -q
```
**Result:** `fail (exit 1) — 3 failed, 6 passed in 0.05s`. This is the required outcome.

```bash
python3 -m pytest tests/test_mcp_adoption.py tests/test_cli_retirement_guard.py -q
```
**Result:** `3 failed, 189 passed, 2 skipped` — the imported-from suite is untouched and fully
green; only this guard's three corpus assertions are red.

```bash
git status --porcelain -- skills specs docs scripts episodes tests map
```
**Result:** `?? tests/test_cli_retirement_guard.py` — one line, the new file.

```bash
test -f tests/test_cli_retirement_guard.py \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g1-guard.log 2>&1 \
  && grep -qiE 'CLI fallback|<engine>' /tmp/g1-guard.log
```
**Result:** `pass (exit 0)` — the gate's own closing check. Run through the engine as
`m1-guard.c2`, and independently by hand.

### Scan counts the guard states

Every failure message carries the census, so a finding can never be read without the size of the
corpus it came from:

> `scanned 1007 texts across 103 files (101 under skills/, 2 under specs/)`

101 files under `skills/` (`.md`/`.json`) + 2 under `specs/` (`.toml`) = **103 files**;
**1007 texts** (each `.md`/`.toml` is one whole-file text; each `.json` contributes one text per
string leaf, by JSON path). Floors asserted so the walk cannot narrow silently: ≥60 skills files,
≥1 spec file, ≥600 texts.

## TDD evidence, if required

- **Failing test observed:** yes — verbatim below.
- **Passing test observed:** not applicable and deliberately not produced. This gate closes on
  RED; making it green is the sweep, which gates g2–g5 own.
- **Refactor while green:** `no`.

### Verbatim RED output

```
============================= test session starts ==============================
collected 9 items

.....FFF                                                                 [100%]

=================================== FAILURES ===================================
_ TestNoSecondPathReachesAnAgent.test_no_engine_placeholder_token_reaches_an_agent _

E       AssertionError: 10 `<engine>` placeholder tokens -- a stand-in for an engine command line that init_work_area.py deliberately never resolves, so each one reaches an agent unresolved -- survive in agent-facing instruction text (scanned 1007 texts across 103 files (101 under skills/, 2 under specs/)).
E         The ruling, verbatim: "the agents should not know about the CLI. period."
E         Sites:
E             skills/admiral/templates/ADMIRAL_SPINE.template.json.tasks.init.imperative
E                 ...s no session id argument. CLI fallback: <engine> claim --session-id <admiral-session-id>...
E             skills/admiral/templates/ADMIRAL_SPINE.template.json.tasks.closeout.imperative
E                 ...sion id argument needed). CLI fallback: <engine> release --session-id <admiral-session-i...
E             skills/commander/references/commander-core.md:127
E                 ...s no session id argument; CLI fallback `<engine> attach <step> --type user-decision --fi...
E             skills/commander/references/crew-dispatch.md:35
E                 ...P tool with `action=block`, or the CLI `<engine> block`), recording the crew id and what...
E             skills/commander/templates/COMMANDER_SPINE.template.json.tasks.init.imperative
E                 ...from its own environment. CLI fallback: <engine> claim --session-id <commander-session-i...
E             skills/commander/templates/COMMANDER_SPINE.template.json.tasks.plan.imperative
E                 ...take that escape as a RECORDED waiver (<engine> waive plan --cond c6 --authority human...
E             skills/commander/templates/COMMANDER_SPINE.template.json.tasks.archive.imperative
E                 ...are intentional, a human waives c4 via <engine> waive archive --cond c4 --authority hum...
E             skills/commander/templates/COMMANDER_SPINE.template.json.tasks.archive.imperative
E                 ...no session id argument). CLI fallback: <engine> release --session-id <commander-session...
E             skills/explorer/templates/EXPLORER_SPINE.template.json.tasks.init.imperative
E                 ...s no session id argument. CLI fallback: <engine> claim --session-id <work-id> --claimed-...
E             skills/explorer/templates/EXPLORER_SPINE.template.json.tasks.route.imperative
E                 ...sion id argument needed). CLI fallback: <engine> release --session-id <work-id>. Attest...

tests/test_cli_retirement_guard.py:298: AssertionError
__ TestNoSecondPathReachesAnAgent.test_no_cli_fallback_clause_reaches_an_agent __

E       AssertionError: 16 `CLI fallback` clauses -- each one hands an agent a second path to the checklist engine beside the MCP door -- survive in agent-facing instruction text (scanned 1007 texts across 103 files (101 under skills/, 2 under specs/)).
E         The ruling, verbatim: "the agents should not know about the CLI. period."
E         Sites:
E             skills/admiral/templates/ADMIRAL_SPINE.template.json.tasks.init.imperative
E                 ...the door needs no session id argument. CLI fallback: <engine> claim --session-id <admiral-s...
E             skills/admiral/templates/ADMIRAL_SPINE.template.json.tasks.closeout.imperative
E                 ...spine; no session id argument needed). CLI fallback: <engine> release --session-id <admiral...
E             skills/charter/SKILL.md:12
E                 ...he process's bound spine, otherwise the CLI fallback: the absolute path to this installed sk...
E             skills/commander/references/commander-core.md:127
E                 ...spine and needs no session id argument; CLI fallback `<engine> attach <step> --type user-dec...
E             skills/commander/templates/COMMANDER_SPINE.template.json.tasks.init.imperative
E                 ...SPINE_SESSION from its own environment. CLI fallback: <engine> claim --session-id <commander...
E             skills/commander/templates/COMMANDER_SPINE.template.json.tasks.plan.imperative
E                 ...fields={cite: 'LAUNCH_ORDER:Mission'}); CLI fallback: attach plan --type user-decision --fie...
E             skills/commander/templates/COMMANDER_SPINE.template.json.tasks.archive.imperative
E                 ...the door needs no session id argument). CLI fallback: <engine> release --session-id <command...
E             skills/explorer/SKILL.md:31
E                 ...xt that owns the process's bound spine; CLI fallback, always available: the absolute path to...
E             skills/explorer/templates/EXPLORER_SPINE.template.json.tasks.init.imperative
E                 ...the door needs no session id argument. CLI fallback: <engine> claim --session-id <work-id>...
E             skills/explorer/templates/EXPLORER_SPINE.template.json.tasks.route.imperative
E                 ...spine; no session id argument needed). CLI fallback: <engine> release --session-id <work-id...
E             skills/interrogator/SKILL.md:26
E                 ...ences/checklist-engine.md` — MCP door). CLI fallback, always available: the absolute path to...
E             skills/workbench/SKILL.md:37
E                 ...ences/checklist-engine.md` — MCP door); CLI fallback, always available and the only path for...
E             skills/workbench/references/checklist-engine.md:5
E                 ...y_result` tools (see "MCP door" below). CLI fallback, always available, and the only path fo...
E             skills/workbench/references/checklist-engine.md:45
E                 ...via the cli is a defect"). There is no CLI-fallback table below this one — every verb the e...
E             skills/write-a-skill/templates/gated-engine-SKILL.template.md:15
E                 ...d crew member driving its own plan) the CLI fallback: through `scripts/checklist_engine.py`....
E             skills/write-a-skill/templates/survey-SKILL.template.md:11
E                 ...crew member driving its own survey) the CLI fallback: through `scripts/checklist_engine.py`....

tests/test_cli_retirement_guard.py:307: AssertionError
__ TestNoSecondPathReachesAnAgent.test_no_engine_invocation_reaches_an_agent ___

E       AssertionError: 10 command-shaped `checklist_engine.py` invocations -- the rename-around that survives deleting the phrase, because the runnable command is what the sentence is for -- survive in agent-facing instruction text (scanned 1007 texts across 103 files (101 under skills/, 2 under specs/)).
E         The ruling, verbatim: "the agents should not know about the CLI. period."
E         Sites:
E             skills/charter/SKILL.md:12
E                 ...this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engin...
E             skills/explorer/SKILL.md:31
E                 ...path to this installed skill's bundled `scripts/checklist_engine.py` (workbench `references/checklist-engin...
E             skills/interrogator/SKILL.md:26
E                 ...this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engin...
E             skills/workbench/SKILL.md:37
E                 ...path to this installed skill's bundled `scripts/checklist_engine.py` (canonical JSON state). Do not run `sc...
E             skills/workbench/SKILL.md:37
E                 ...py` (canonical JSON state). Do not run `scripts/checklist_engine.py` relative to the target repo unless tha...
E             skills/workbench/references/checklist-engine.md:5
E                 ...driving its own plan or survey: `python <skill-dir>/scripts/checklist_engine.py --file <checklist.json> <verb>`. Instal...
E             skills/workbench/references/checklist-engine.md:5
E                 ...source repo, the same script lives at `scripts/checklist_engine.py`. Schema: `docs/CHECKLIST_SCHEMA.md`. M...
E             skills/workbench/references/checklist-engine.md:41
E                 ...`REVIEW_SURVEY.json` through the CLI (`scripts/checklist_engine.py`) instead — calling a door tool from in...
E             skills/write-a-skill/templates/gated-engine-SKILL.template.md:15
E                 ...ts own plan) the CLI fallback: through `scripts/checklist_engine.py`. One item per step, each with a real c...
E             skills/write-a-skill/templates/survey-SKILL.template.md:11
E                 ...own survey) the CLI fallback: through `scripts/checklist_engine.py`. **Visit every item, append more from...

tests/test_cli_retirement_guard.py:315: AssertionError
=========================== short test summary info ============================
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_engine_placeholder_token_reaches_an_agent
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_cli_fallback_clause_reaches_an_agent
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_engine_invocation_reaches_an_agent
3 failed, 6 passed in 0.05s
```

Elided from the paste, and only this: pytest's own `self = <...object at 0x...>` header, the
echoed source of each assert statement, and the one-line `assert not [...]` list repr that follows
each message. Nothing inside any failure message was cut; the site lists are complete.

## Two census discrepancies against the handoff baseline — reported, not smoothed

Close criterion 3 asks for a census "consistent with the measured baseline: **15** `CLI fallback`
occurrences across 11 files, and **9** `<engine>` tokens". The guard reports 16 and 10. Both gaps
are real and both are refinements of the baseline, not contradictions of it:

1. **`<engine>`: 10 occurrences on 9 lines, in 5 files.** The baseline counted *lines* (its table
   has 9 rows under `skills/`). `COMMANDER_SPINE.template.json` `tasks.archive.imperative` carries
   **two** tokens on its one line — `<engine> waive archive --cond c4 ...` and
   `CLI fallback: <engine> release ...`. The guard counts occurrences, so it reports that line
   twice. Same sites, finer unit. **The sweep must edit both tokens on that line, not one.**
2. **`CLI fallback`: 16, because there is a fourth surface form.** The baseline measured three
   (`:` ×10, `,` ×4, ` ` ×1 = 15). My separator is loosened to `CLI[\s-]+fallback`, which also
   catches **`CLI-fallback`** at `skills/workbench/references/checklist-engine.md:45` — *"There is
   no CLI-fallback table below this one"*. That site is **lane D2's** file, and the sentence is
   prose asserting the absence of such a table rather than handing an agent a path. It is the
   accepted false-alarm class the guard documents in its own docstring ("prose that FORBIDS the
   violation while quoting it"). I did not narrow the pattern to duck it: a space-only separator
   is exactly the spelling-sensitivity constraint 4 forbids, and a hyphenated respelling is the
   cheapest way to defeat a space-only pattern.

Neither discrepancy changes any site the launch order assigned to this lane: **13 clause sites and
9 clause-bearing lines under lane D1's files, unchanged.**

## Docs/contracts touched
- `none` — the lane may not write `docs/agents/*`, so the ruling is carried inline in the guard's
  failure messages instead (`HUMAN_RULING`), per the handoff's constraint 5 and CONVERGENCE F10.
  Deleting the guard now deletes the reason with it, which is the property a dangling pointer
  loses.

## Assumptions
- `specs/**/*.toml` is a stable home for door doctrine. Asserted, not assumed: the guard has a
  `≥1` floor on that walk, so if `specs/` empties or moves, the guard says so instead of silently
  covering nothing.
- The guard's own file is out of scope by the walk rule (it is neither under `skills/` nor a
  `specs/*.toml`), which is why it may quote all three patterns without flagging itself. Verified.

## Stop conditions hit
- `none`. The scope expression covered every target and caught no pre-ruled survivor. No exception
  list was needed or added, and nothing outside Allowed Scope was edited.

## Out-of-scope observations
1. **Triage candidate — `docs/agents/CREW_CONTEXT.md` "Python Invocation" is stale.** It records
   (measured 2026-08-10) that `python3` has no pytest on this host. Measured today: `py`, `python`
   and `python3` all report pytest 9.1.1. I checked before running, per that section's own
   instruction, so nothing was harmed — but a crew that trusts the recorded measurement instead of
   re-running it will reach the wrong conclusion about which interpreter to use.
2. **For g2's attention — the guard's invocation pattern leaves 6 prose mentions of
   `checklist_engine.py` alone**: `skills/_shared/global-everyone.md:70,178,254`,
   `skills/admiral/references/fleet-doctrine.md:234`, `skills/explorer/SKILL.md:115` (a scripts
   manifest), `skills/write-a-skill/SKILL.md:20` (an archetype table cell). None is a command.
   Whether #559's *"the agents should not know about the CLI. period."* reaches a sentence that
   merely names the engine as a component is a doctrine call above my authority; I drew the line
   at "tells an agent how to run it" and pinned that line in a test. Three of those six are in
   `skills/_shared/`, which is regenerated into per-role copies by
   `scripts/install_constellation.py`.
3. **For g2's attention — `TestTheInvocationPredicateItself` will constrain the sweep's prose.**
   A swept file may still say `checklist_engine.py`, but may not put a path, an interpreter or a
   flag next to it. If the sweep's replacement wording needs to show a command (e.g. for the three
   door-refused second-checklist sites), the guard goes red on it, and that is a decision to make
   deliberately rather than by patching the pattern.

## Workflow Feedback
- **Handoff gaps:** two, both in Close Criteria 3. It states the baseline in a **unit it does not
  name** — "15 `CLI fallback` occurrences" is occurrences, "9 `<engine>` tokens" is lines — and I
  could only tell by re-measuring both ways. It also states the three measured surface forms as a
  closed set, in a criterion that grades the census; a pattern built to be punctuation-agnostic
  (which Constraint 4 demands) will necessarily find *more* than a three-form census predicts, so
  as written the criterion mildly penalizes doing the thing the constraint asks for. Naming the
  unit, and phrasing criterion 3 as a floor ("at least the 15 known sites, and say what else you
  find"), would remove both.
- **Context rediscovered:** none of substance. The Map Anchors were unusually good — `notes-1.md`
  and `CONVERGENCE.md` carried the measured census, the three surface forms, the two pre-ruled
  survivors and the F1/F10 rulings, so I spent my reading budget on the two precedent tests rather
  than on re-deriving the baseline. The one thing I had to dig for was the cross-test-import idiom
  (`sys.path.insert` + `# noqa: E402`); the Scope expression section says "import it or re-derive
  it" without noting the repo already has a house pattern for the import, at
  `test_mcp_imperative_equivalence.py:72`.
- **Instructions improvised around:** the implementer skill says a dispatched crew's spine is bound
  before it starts and `spine_status` is the first call. Mine is not: `run_crew.py` registered this
  run with `"spine": null` and my environment carries only `SPINE_PARENT`, no `SPINE_FILE`. I
  followed the skill's other branch — authored my own `IMPLEMENTER_PLAN.json` under my scratch dir
  and drove it, claiming the lease as my first command. Worth noting because the skill presents
  the bound case as the norm for a `run_crew.py` dispatch, and this dispatch was not it.
- **My own mistakes:** one, caught before it shipped. My first invocation pattern accepted a bare
  `--` as "an argument follows", so it red-lighted `rewrites \`checklist_engine.py\` -- the very
  engine driving it`, where the dashes are an ASCII em-dash in prose about *editing* the file.
  `TestTheInvocationPredicateItself` failed on exactly that string in the first run; I tightened
  the arm to require a long flag (`--[A-Za-z]`) and kept the string as a permanent regression pin.
  Writing the predicate's own test before trusting the predicate is what caught it — had I only
  looked at the corpus result, the pattern would have looked perfect, because that particular
  sentence uses a real em-dash and never fired.
- **What would have made this easier:** state the counting unit in Close Criteria 3, and point at
  `test_mcp_imperative_equivalence.py:72` as the sanctioned cross-test-import idiom.
- **A hook misfire worth an episode — the Stop hook told this crew to drive its PARENT's spine.**
  After my plan reached `DONE` and I released my lease, the Stop hook fired twice with
  `SPINE MID-FLIGHT: gate execute is still open`, and the next imperative it handed me was the
  Commander's: reload `constellation-commander`, rewrite `STATE_NOTE.md`, drive `execute.json`
  gate by gate, dispatch crews via `run_crew.py`. That is `.agent-work/567-d1/spine.json`, leased
  by `constellation/567-d1/lane-d1/commander-delegated` (heartbeat 17:59, before this run started
  at 18:03) — not mine. My environment has **no `SPINE_FILE`**, only `SPINE_PARENT`, and
  `crew-runs.json` registers this crew with `"spine": null`.

  I did not comply, and the refusal is the point: the hook resolves the project spine from
  `CLAUDE_PROJECT_DIR`, so for a crew process it reads the parent's file and cannot tell that the
  reader is not its owner. This is `docs/agents/CREW_CONTEXT.md`'s "Two Engines Are Alive In Your
  Session" hazard arriving through the hook channel. Complying would have meant passing the
  Commander's session id on mutating verbs — impersonation, not delegation — against a spine whose
  owner is at that moment **blocked waiting for this process to exit**, since `run_crew.py`
  dispatches foreground. The hook also names `spine_halt block` as the sanctioned exit; that is
  the exit for a gate of *mine*, and I have none open.

  Two candidate fixes, both above my authority to make: have the Stop hook skip when `SPINE_FILE`
  is unset but `SPINE_PARENT` is set (the exact signature of a `spine: null` crew), or have
  `run_crew.py` bind the crew's own plan into `SPINE_FILE` so the hook reads the right spine. The
  second is the deeper fix and matches what the implementer skill already assumes a `run_crew.py`
  dispatch looks like — see "Instructions improvised around" above, which is the same gap seen
  from the other end.

## Return status
Return status: `complete`
