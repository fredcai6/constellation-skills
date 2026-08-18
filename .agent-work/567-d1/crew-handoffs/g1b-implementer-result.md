# Implementation Result

## Assigned gate
`g1b-implement` — Widen the guard: placeholder-agnostic command lines, and the tracked template
overlay (issue #559, epic #567, wave 2, lane D1).

Measured at `8ba1334c`. Every number below is pinned to that revision.

## Completed slice

`tests/test_cli_retirement_guard.py` only. Two changes:

**(a)** A fourth pattern, `ENGINE_STANDIN_COMMAND_RE`, generalizing the `<engine>` token to the
shape it is one spelling of. **(b)** The walk extended to `.agent-work/templates/**` by a
directory-plus-suffix rule, with its own vacuity floor and a rule-scope assertion.

Nothing was swept. The guard is still RED, and it is redder — 18 addresses before, **36** after.

---

## Half (a) — the widened pattern

### The pattern, quoted

```python
_ENGINE_STANDIN = (
    r"(?:<[A-Za-z0-9_.-]+>"             # <engine>, <cli>, <engine-cli>, <script>
    r"|\{\{[^{}\n]+\}\}"                # {{engine}}
    r"|\{[A-Za-z0-9_.-]+\}"             # {engine}
    r"|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?"  # $ENGINE, ${ENGINE}
    r"|%[A-Za-z_][A-Za-z0-9_]*%)"       # %ENGINE%
)

ENGINE_STANDIN_COMMAND_RE = re.compile(
    _ENGINE_STANDIN + r"[ \t]+(?:" + _ENGINE_VERBS + r")\b"
)
```

`_ENGINE_VERBS` is the file's existing enumeration, reused not restated.

### Why exactly this shape

Two width decisions. Both were settled by running candidates over the whole walk, not by argument.

**1. The stand-in is NOT required to spell `engine` or `cli`.**

The obvious narrow version — require the placeholder token to contain `engine` or `cli` — catches
all three verified misses and also costs zero on this tree. I measured it and rejected it anyway:
it rebuilds the exact defect this gate exists to remove, one level up. The class would then rest on
two substrings instead of one token, and `restore the second path with <script> claim --session-id
<id>` walks straight through. The reviewer's own framing is that this is the route a **fresh**
author takes; a fresh author has no more reason to type `cli` than to type `<engine>`.

Measured cost of taking the wider form instead: **zero**. Over 3098 texts it reports 26 matches at
23 addresses, and every one of those addresses is already reported by `<engine>`.

**2. The separator is horizontal whitespace, and nothing may sit between.**

This is the arm that pays for the width, and both halves of it are load-bearing:

| loosening | what it costs, measured |
|---|---|
| `[ \t]` → `\s` | 1 false alarm: `skills/workbench/references/checklist-engine.md:92`, where `heartbeat --session-id <id>` ends one line of a usage block and `release --session-id <id>` opens the next. `<id>` is a session id, not a program. |
| allow a trailing `` [`'"]* `` | 3 honest prose shapes fire: "the `` `<work-id>` `` record", "each `` `<gate>` `` block", "the `` `<path>` `` append". None exists in the corpus today; any is writable tomorrow. |

Markdown is why the tight form works without losing anything: a code span wraps the **whole**
command (`` `<engine> attach <step> --type user-decision` ``), so a stand-in carrying its own
closing backtick is a noun, not a program name. Both rejected loosenings are pinned as
must-not-match in `NOT_A_STAND_IN_COMMAND`, so a later author reaching for the obvious `\s` goes
red immediately — the same trick `g1` used to freeze the em-dash false alarm.

This is the direct answer to the bar the handoff set: `TestCLIStaysAvailableNotDeprecated`'s
argument is that a check punishing honest authors gets deleted. This pattern's measured
false-alarm rate on honest text is 0/3098.

### The three respellings, shown caught

`TestTheStandInCommandPredicateItself::test_the_three_verified_misses_are_the_ones_pinned` asserts
**both** halves of the review's finding, so the finding cannot silently stop being true:

```python
g1_patterns = (ENGINE_PLACEHOLDER_RE, CLI_FALLBACK_RE, ENGINE_INVOCATION_RE)
for respelling in self.STAND_IN_COMMANDS[:3]:
    assert not any(p.search(respelling) for p in g1_patterns)   # still a real miss for g1
    assert ENGINE_STANDIN_COMMAND_RE.search(respelling)         # and now caught
```

Reproduced before the widening landed, with the pre-change patterns:

```
MISSED  {'placeholder': False, 'fallback': False, 'invocation': False} | Second path: <cli> claim --session-id <commander-session-id> --claimed-by commander.
MISSED  {'placeholder': False, 'fallback': False, 'invocation': False} | If the door is down: <engine-cli> advance g1 --why 'gate closed'.
MISSED  {'placeholder': False, 'fallback': False, 'invocation': False} | Fallback command line: {{engine}} release --session-id <work-id>.
```

`STAND_IN_COMMANDS` holds 9 entries and `test_catches_every_stand_in_command_shape` pins all of
them: the three above, the review's `$ENGINE` alias-use miss (miss #4 from its table of 12, now
closed as a bonus), the `<script>` / `{engine}` / `%ENGINE%` residuals a narrower version leaves
open, and the corpus's two live backticked shapes (`` `<engine> block` ``, `` `<engine> attach` ``)
so the tightening cannot narrow into blindness.

### The archetype-table boundary — decided, pinned

**Decision: it stays on the prose side.** `skills/write-a-skill/SKILL.md:20` — *"a
`templates/*.json` checklist driven through `checklist_engine.py`"* — is now the fifth entry in
`PROSE_ONLY`, so `test_leaves_a_bare_component_mention_alone` pins it and a future widening that
starts flagging archetype tables goes red.

The reasoning, also written into the docstring's "what this does not enforce" list: the cell does
assert the drive-path belief #559 removes, and it **is** a real target for the g2 sweep. But it
hands an agent no runnable command, and no predicate separates *"driven through X"* from *"Scripts:
X"* without reading English. That predicate is precisely the class `test_mcp_adoption.py` built,
measured at two bars, and deleted. Deciding that cell is a one-line human judgement; encoding it is
a check the next author deletes.

**This is a hand-off to g2, not a dismissal:** the sweep should reword that cell, and the guard
will not tell it to. Flagged for the Commander below.

---

## Half (b) — the overlay walk

### The rule

```python
OVERLAY_DIR = ".agent-work/templates"

def _walk_dir(rel_dir: str, suffixes: tuple[str, ...]) -> list[str]:
    base = ROOT / rel_dir
    if not base.is_dir():
        return []
    return sorted(p.relative_to(ROOT).as_posix()
                  for p in base.rglob("*")
                  if p.is_file() and p.suffix in suffixes)

SPEC_FILES   = _walk_dir("specs", SPEC_SUFFIXES)
OVERLAY_FILES = _walk_dir(OVERLAY_DIR, INSTRUCTION_SUFFIXES)
```

`_walk_spec_files` was generalized into `_walk_dir` rather than copied — one directory-plus-suffix
walker serving both extensions.

**How `.agent-work/567-d1/**` is excluded: by where the rglob is rooted.** The walk starts *at* the
overlay directory, so a run's own artifacts are not reached and then filtered — they are never
reachable. There is no sibling to name, which is why the exception list is still length **zero**.
Rooting at `.agent-work/` and filtering back out would have been the same defect this file exists
to avoid.

`INSTRUCTION_SUFFIXES` is **imported** from the adoption suite, not restated, for the same
anti-drift reason `INSTRUCTION_FILES` is: the repo keeps one machine-readable definition of "a file
carrying instruction text", and both walks use it. Measured: all 113 overlay files are `.md`/`.json`,
so the imported suffix rule covers the surface completely today.

### The three verifications

**1. Both pre-ruled survivors are still OUT, structurally, named nowhere.**

```
survivor IN WALK? docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md: False
survivor IN WALK? scripts/init_work_area.py:                                           False
```

Neither is under `skills/`, a `specs/*.toml`, or under `.agent-work/templates/` — because of what
they are. `grep` for either path in the guard returns nothing.

**2. No lane-D2 file enters the walk.** Every text under
`.agent-work/templates/.baseline/constellation-workbench/` run against all four patterns:

```
D2 baseline overlay dirty sites: NONE (clean)
```

Confirmed independently with `grep -rInE '<engine>|CLI[ -]+fallback|checklist_engine\.py'` over that
directory: no matches. The widening adds **no fenced-file dependency**. (The 11 `skills/workbench/**`
files already in the walk are the known, expected coverage from `g1` constraint 4, unchanged here.)

**3. The RED names overlay sites.** 58 lines of the failure output address
`.agent-work/templates/`. Verbatim head of the new assertion's failure:

```
E  AssertionError: 26 stood-in-for engine command lines -- a placeholder standing where the program
E  name goes, followed on the same line by an engine verb, which is what a command line in a spine
E  template looks like when the script's own name is never written -- survive in agent-facing
E  instruction text (scanned 3098 texts across 216 files (101 under skills/, 2 under specs/,
E  113 under .agent-work/templates/)).
E    The ruling, verbatim: "the agents should not know about the CLI. period."
E    Sites:
E        .agent-work/templates/.baseline/constellation-admiral/ADMIRAL_SPINE.template.json.tasks.init.imperative
E        .agent-work/templates/.baseline/constellation-commander/COMMANDER_SPINE.template.json.tasks.archive.imperative
E        .agent-work/templates/ADMIRAL_SPINE.template.json.tasks.init.imperative
E        ...
```

### Floors for the new surface

- `test_the_walk_reaches_the_project_template_overlay` — `len(OVERLAY_FILES) >= 60` (113 measured).
- `test_the_walk_yields_texts_not_just_paths` — raised `600 → 1800` (3098 measured), with the
  message now carrying both the 1007 pre-overlay figure and the 3098 post-overlay one.
- `test_the_overlay_rule_does_not_reach_a_live_runs_own_artifacts` — a **new** floor in the other
  direction, asserting no walked file is under `.agent-work/` but outside the overlay. That is the
  scope rule itself, in the assertion path, so widening it to `.agent-work/` goes red rather than
  quietly dragging every crew handoff in.

---

## The false-alarm cost, priced site by site

Both deltas separated, as asked. "Address" = the file:line or JSON path the guard would print.

| surface | g1 patterns report | widened stand-in pattern reports | **addresses the widening ADDS** |
|---|---|---|---|
| `skills/` + `specs/` (g1's own surface) | 18 | 9 | **0** |
| `.agent-work/templates/` (new surface) | 18 | 14 | **0** |
| whole walk | 36 | 23 | **0** |

**The widening's false-alarm cost is zero. There is no site to classify, because there is no new
site.** Every address the stand-in pattern reports is already reported by `<engine>`; it changes
nothing about *today's* corpus and everything about what a *fresh* author can get past it. No
narrower version needs proposing.

The gate's other delta is the new surface, and it is not a false-alarm delta — but it is 18 new
addresses, so each is classified:

| # | address (18 total) | verdict |
|---|---|---|
| 1–7 | `.agent-work/templates/{ADMIRAL,COMMANDER,EXPLORER}_SPINE.template.json` — 7 imperatives (`init`, `plan`, `archive`, `closeout`, `route`) | **genuine second path.** Each carries `CLI fallback: <engine> <verb> …`. |
| 8–9 | `.agent-work/templates/{gated-engine,survey}-SKILL.template.md:15`, `:11` | **genuine second path.** A `CLI fallback` clause plus a command-shaped `checklist_engine.py` invocation. |
| 10–18 | the same nine, mirrored under `.agent-work/templates/.baseline/<skill>/` | **genuine second path.** |

Not asserted on the strength of the handoff's claim — verified with `git hash-object`:

```
ADMIRAL_SPINE.template.json:     overlay-vs-skills=IDENTICAL  overlay-vs-baseline=IDENTICAL
COMMANDER_SPINE.template.json:   overlay-vs-skills=IDENTICAL  overlay-vs-baseline=IDENTICAL
EXPLORER_SPINE.template.json:    overlay-vs-skills=IDENTICAL  overlay-vs-baseline=IDENTICAL
gated-engine-SKILL.template.md:  overlay-vs-skills=IDENTICAL  overlay-vs-baseline=IDENTICAL
survey-SKILL.template.md:        overlay-vs-skills=IDENTICAL  overlay-vs-baseline=IDENTICAL
```

**Zero honest sentences are red-lighted by anything this gate added.**

### Two census discrepancies against the handoff, reported not smoothed

1. **The overlay carries 16 `<engine>` occurrences, not 7.** The handoff's table counts the five
   non-`.baseline` files by **line** (2 + 3 + 2 = 7). By **occurrence** those five hold 8 —
   `COMMANDER_SPINE.template.json` line 123 carries two tokens, which is the same
   one-edit-per-line trap the `g1` reviewer already flagged for `skills/`. With the `.baseline/`
   mirrors, which the table names but does not count, the overlay total is **16**. Clause matches:
   **18**, not 2.
2. **`g2` must therefore edit 16 overlay tokens across 10 files**, not 7 across 5. A sweep that
   fixes the five visible copies and not their `.baseline/` mirrors leaves this guard red.

---

## Close criteria

| # | Criterion | Verdict |
|---|---|---|
| 1 | Catches all three respelled command lines, pinned as assertions | **met** — `TestTheStandInCommandPredicateItself`, two tests, both directions asserted |
| 2 | Still leaves reviewed `PROSE_ONLY` alone; archetype boundary decided and pinned | **met** — 5/5 `PROSE_ONLY` pass; archetype cell decided prose-side and added to the list |
| 3 | Walk reaches `.agent-work/templates/**` as a rule, not this run's artifacts | **met** — `_walk_dir` rooted at the overlay; strays assertion is green |
| 4 | Exception list still zero; both survivors out structurally | **met** — no file named as an exclusion anywhere; both survivors `False` |
| 5 | `-k "not TestNoSecondPathReachesAnAgent"` passes | **met** — `11 passed, 4 deselected`, exit 0 |
| 6 | `-k TestNoSecondPathReachesAnAgent` fails, naming an overlay site | **met** — exit 1, `4 failed`, 58 overlay site lines |
| 7 | False-alarm cost measured over the whole walk and reported site by site | **met** — zero new addresses; the 18 surface additions classified individually |
| 8 | Nothing swept | **met** — `git status --porcelain` over `skills specs docs scripts episodes tests map .agent-work/templates` is one line: `M tests/test_cli_retirement_guard.py` |

The gate's own closing check, run in POSIX form (see Workflow Feedback on the `set -o pipefail`
defect in the handoff's version):

```sh
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent' >/dev/null 2>&1 \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent > /tmp/g1b-guard.log 2>&1 \
  && grep -q '.agent-work/templates/' /tmp/g1b-guard.log
→ exit 0
```

## Scope

**Files changed:** `tests/test_cli_retirement_guard.py` — the only one.

**Specific exclusions touched:** `no`. `tests/test_mcp_adoption.py` is imported, never modified
(`git diff --quiet HEAD -- tests/test_mcp_adoption.py` → clean, `183 passed, 2 skipped`). Nothing
under `skills/`, `specs/`, `docs/`, `scripts/`, `episodes/`, `map/` or `.agent-work/templates/`.
No lane-D2, lane-E, lane-F, lane-H or Admiral fenced file written.

**Behavior changed:** `no`. The deliverable is a test.

## Evidence

Interpreter checked first per `CREW_CONTEXT.md` "Python Invocation" — `py`, `python` **and**
`python3` all report pytest 9.1.1 on this host. (That section's 2026-08-10 measurement, which says
`python3` has no pytest, is stale; the `g1` reviewer found the same.)

```
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q     → 15 tests collected, exit 0
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent'
                                                                          → 11 passed, 4 deselected, exit 0
python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent
                                                                          → 4 failed, 11 deselected, exit 1
python3 -m pytest tests/test_mcp_adoption.py -q                           → 183 passed, 2 skipped, exit 0
python3 -m pytest tests/ -q                                               → 6 failed, 3362 passed, 5 skipped,
                                                                            1219 subtests passed in 140.88s
```

**The 6 whole-suite failures, accounted for.** Four are this guard, RED by design. The other two are
**pre-existing and not mine** — proved by stashing my change and re-running them, where both still
fail:

- `test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  — map freshness; no architecture map exists in this repo and `map/INDEX.md` is Admiral-fenced.
- `test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
  — asserts `CREW_SCRATCH_DIR` is absent from a child env, but builds that env from the **ambient**
  one. `run_crew.py` sets `CREW_SCRATCH_DIR` in every crew process, so this test fails whenever it
  is run from inside a dispatched crew and passes when a human runs it. Triage candidate below.

Engine drive: own plan at
`.agent-work/567-d1/crew-scratch/g1b-implementer-attempt-1-74e194cfc852/IMPLEMENTER_PLAN.json`,
5 items, lease `constellation/567-d1/g1b/implementer/attempt-1`, journal alongside.

## Map impact

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`), so these are notes for
Cartographer reconcile, in the inbound anchor vocabulary.

- **`tests/test_cli_retirement_guard.py`** gains one exported pattern (`ENGINE_STANDIN_COMMAND_RE`,
  built on private `_ENGINE_STANDIN`), one walk symbol pair (`OVERLAY_DIR`, `OVERLAY_FILES`), and
  one generalized helper (`_walk_dir`, replacing `_walk_spec_files`). `SPEC_SUFFIXES` survives
  unchanged as `_walk_dir`'s argument.
- **Inbound dependency widened.** The guard now imports three names from `tests/test_mcp_adoption.py`
  (`INSTRUCTION_FILES`, `INSTRUCTION_SUFFIXES`, `_instruction_texts`) where `g1` imported two. Same
  failure mode as `g1` recorded, one symbol wider: if `g2`'s inversion deletes or renames any of
  them the guard dies at **collection**, which pytest reports as an error, never as a pass.
- **New surface under guard.** `.agent-work/templates/**` is now agent-facing instruction text with
  a machine check on it. It was previously read by no walk in the repo. This is the structural
  answer to the `g1` review's triage candidate 1.
- **Unchanged:** the `TestTier2SpineAlreadyBoundForDispatchedCrews` precedent this file generalizes;
  the `specs/**/*.toml` extension; the zero-length exception list.

## Triage candidates

1. **`skills/write-a-skill/SKILL.md:20` is a sweep target the guard deliberately will not catch.**
   The archetype table cell asserting a drive path *"driven through `checklist_engine.py`"* is
   decided prose-side here for good reasons, but #559's ruling still argues it should be reworded.
   It needs a human or `g2`'s judgement, not a pattern. Routed to the Commander rather than settled
   by this crew.
2. **`tests/test_crew_launcher.py:4061` fails whenever the suite is run from inside a dispatched
   crew.** `ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
   asserts `CREW_SCRATCH_DIR` is absent from the child env while inheriting the ambient env, and
   `run_crew.py` sets that variable in every crew process. Any crew that runs the whole suite as
   evidence sees a red that a human never sees. Environment-leak in the test, not in the launcher.
3. **The `.agent-work/templates/.baseline/` mirror doubles every sweep target.** Nine of the
   eighteen overlay addresses are `.baseline/` copies. Whatever mechanism reconciles the overlay
   from `skills/` has to re-run after `g2`, or the guard stays red on the mirrors alone.

## Workflow Feedback

- **What helped most.** The handoff did the thing that makes a widening gate tractable: it stated
  the invariant ("a stand-in for the engine, immediately followed by an engine verb") and then
  explicitly left the expression to me, while naming the exact bar to judge width against
  (`TestCLIStaysAvailableNotDeprecated`, with a line number). That turned "how wide?" from a matter
  of taste into a measurement I could run four candidates through. Handing me the three verified
  misses as literal strings meant the RED half of test-first cost one command instead of an
  afternoon.

- **Handoff gaps, three, all small.**
  1. **The gate's own closing check does not run under the shell the engine uses.** It opens with
     `set -o pipefail`; the engine runs `command` postconditions under `/bin/sh`, which on this host
     is dash, and dash rejects that option with exit 2. I copied it verbatim into my plan and the
     engine refused my `advance` on a shell dialect error, not on the guard. The check has no
     pipeline, so the option was inert — I corrected it through the engine's `amend --op
     retext-check` (authority `implementer`, reason recorded) rather than hand-editing, and it
     passes. `global-everyone.md` already says command checks must be authored in POSIX form; the
     handoff's own check is the counter-example.
  2. **The overlay census is stated in lines and read as occurrences.** "7 `<engine>` occurrences"
     is 7 *lines* and 8 *occurrences* in the five visible files, and 16 once the `.baseline/`
     mirrors the same table mentions are counted. This is the *identical* unit slip the `g1`
     implementer reported about its own handoff's "15 `CLI fallback` occurrences / 9 `<engine>`
     tokens" — twice in two gates, so it is a template problem, not an author problem. Naming the
     unit, or phrasing every census as a floor, would end it.
  3. **No **Deliverable Path Check** for my own plan file.** The handoff verifies the result path is
     not git-ignored but says nothing about where a `spine: null` crew should put its plan. I used
     `$CREW_SCRATCH_DIR`, which `run_crew.py` sets and which the `g1` implementer also used — a
     convention discovered from a sibling's result artifact, not from any document.

- **The dispatch-shape misfit, now seen four times in this lane.** The implementer skill opens with
  "a dispatched crew's spine is bound for you before you start (`SPINE_FILE`/`SPINE_SESSION` in your
  environment); `spine_status` is your first call, not plan-building." Mine is not bound: my
  environment carries only `SPINE_PARENT`, and `crew-runs.json` registers this crew with
  `"spine": null`. I took the skill's other branch — authored `IMPLEMENTER_PLAN.json` in my scratch
  dir, claimed the lease as my first command, drove it through the engine. The `g1` implementer and
  the `g1` reviewer each reported this independently; with mine that is three crews in two gates,
  plus the reviewer's report of the same misfit from its own side. **For this dispatch shape the
  skill's stated norm is the exception, and the skill says the opposite.** The deeper of the two
  fixes already proposed — have `run_crew.py` bind the crew's own plan into `SPINE_FILE` — would
  make the opening sentence true instead of needing a caveat.

- **My own mistakes, two.**
  1. **I did half (b)'s edits before advancing half (a)'s gate.** My plan cuts the two halves as
     separate items with separate checks, and I then wrote both into the file in one editing pass
     before running either check. Both gates' postconditions are honestly satisfied — `m1`'s check
     is the predicate suite, which was green on the widened pattern alone — but the slices stopped
     being independently verifiable at the moment I merged the edits, and if half (b) had broken a
     floor I would have had no clean way to tell which half did it. The engine recorded the order I
     *claimed*, not the order I *worked*. Cutting vertical slices is worth nothing if I then batch
     them.
  2. **My first widened pattern tolerated a closing backtick after the stand-in**
     (`` [`'"]* ``, copied from the shape of `g1`'s invocation pattern without re-deriving whether
     it belonged). It cost nothing on the corpus — zero new addresses — so the measurement I had
     set up would have passed it, and I nearly shipped it. What caught it was writing the
     must-not-match list *before* trusting the number: "the `` `<work-id>` `` record" fired
     immediately. The corpus test could not have found this, because the sentence that trips it has
     not been written yet. Same lesson the `g1` implementer recorded about its em-dash, arriving by
     a different road: the predicate's own test finds what the corpus cannot.

- **What would have made this easier.** Author the gate's closing check in POSIX form in the
  handoff, and add a **Plan File Location** field to the implementer handoff template for the
  `spine: null` dispatch shape.

## Stop-hook refusal — the third crew in this lane to hit it, and the second gate

After my plan reached `DONE` and I released my lease, the Stop hook fired **twice** with
`SPINE MID-FLIGHT: gate execute is still open` and handed me the **Commander's** next imperative:
reload `constellation-commander`, rewrite `STATE_NOTE.md`, drive `execute.json` gate by gate,
dispatch crews through `run_crew.py`, run `recover_crews.py`, write `REPLAN_INPUT.json`.

**I did not comply.** Verified at the source before refusing, not inferred:

| fact | measured |
|---|---|
| my environment | `SPINE_PARENT` only — **no `SPINE_FILE`, no `SPINE_SESSION`** |
| my registration in `crew-runs.json` | `"spine": null`, `parent: constellation/567-d1/lane-d1/commander-delegated` |
| owner of the spine the hook quotes | `constellation/567-d1/lane-d1/commander-delegated`, **status `active`**, claimed 17:20:59, heartbeat 17:59:18 — before this run started |
| my own plan | `LEASE released`, `DONE: no open items` |

The hook resolves the project spine from `CLAUDE_PROJECT_DIR`, so for a `spine: null` crew it reads
the **parent's** file and cannot tell that the reader is not its owner. Complying would mean
passing the Commander's session id on mutating verbs against a spine whose owner is, at that
moment, blocked waiting for this foreground process to exit — impersonation, not delegation. This
is `CREW_CONTEXT.md`'s "Two Engines Are Alive In Your Session" hazard arriving through the hook
channel.

**Its named escape hatches do not fit either.** The hook offers `spine_halt block` or a
human-authority `waive`. Both **write to the parent's spine**, so the sanctioned "honest stop" is
itself the destructive act. `block` is the exit for a gate of *mine*, and I have none open.

**This is now reproducible across roles and gates**: the `g1` implementer, the `g1` reviewer, and
this crew each hit it independently, each refused, each recorded it. Three crews, two gates, two
roles. The two candidate fixes already proposed still look right, and the second is the real one:

1. Skip the hook when `SPINE_FILE` is unset and `SPINE_PARENT` is set — the exact signature of a
   `spine: null` crew.
2. Have `run_crew.py` bind the crew's own plan/survey into `SPINE_FILE`. This is the deeper fix and
   it also makes both crew skills' "your spine is already bound before you start" opening **true**
   for this dispatch shape, instead of a sentence every dispatched crew has to work around.

The lease-ownership check belongs in the hook, not in more prose telling crews to be careful.

## Return status
Return status: `complete`
