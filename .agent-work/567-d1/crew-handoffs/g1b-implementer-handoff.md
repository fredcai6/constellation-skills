# Implementer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g1b-implement` — Widen the guard: placeholder-agnostic command lines, and the tracked template
overlay.

## Context you are joining

Gate `g1` authored `tests/test_cli_retirement_guard.py`, the regrowth guard that closes issue #559
(*"the door is the interface, not a second path"*). The human's ruling it enforces, verbatim:

> **"the agents should not know about the CLI. period."**

The guard is deliberately **RED** right now — it is authored *before* the sweep so its failure is
produced by the real corpus. Gate `g2` does the sweep. **You do not sweep anything.**

The `g1` review APPROVEd it and returned two things the plan did not account for. You close both,
**before** the sweep, so the widened guard is still the specification the sweep is written against.

**Read first:** `tests/test_cli_retirement_guard.py` (the guard, ~320 lines — read all of it,
especially the docstring's list of what it deliberately does *not* enforce) and
`.agent-work/567-d1/crew-handoffs/g1-reviewer-result.md` §"The review's real work".

---

## Half (a) — the pattern rests on one 8-character literal

### The finding, reproduced by the reviewer

A spine-template command line **never contains the literal `checklist_engine.py`** — a placeholder
stands in for it. So `ENGINE_INVOCATION_RE` cannot reach that class at all, and the entire "engine
command line inside a JSON spine template" surface rests on the single token `<engine>`. All three
of these pass the current guard **clean** (verified by the reviewer):

```
Second path: <cli> claim --session-id <commander-session-id> --claimed-by commander.
If the door is down: <engine-cli> advance g1 --why 'gate closed'.
Fallback command line: {{engine}} release --session-id <work-id>.
```

Reworded prose (`Second path:`, `If the door is down:`) also clears `CLI_FALLBACK_RE`, so nothing
else catches them either.

**And the corpus invites the respelling.** `scripts/init_work_area.py:24` documents `<engine>`
beside `<date>`, `<N>` and `<path>` as *generic* prose placeholders the resolver deliberately never
touches. A future author restoring a command line has no reason to reach for that exact token.

**Severity, stated honestly** (the reviewer's own framing, and it is right): the regrowth history is
textual *restoration* of the same text, which the current patterns do catch. This is the route a
**fresh** author would take. It is a widening decision, not a defect in `g1`'s delivery.

### What to do

Generalize the pattern from the **token** to the **shape**. The invariant is *"an engine command
line reaches an agent"*, and the shape of one is: **a stand-in for the engine, immediately followed
by an engine verb** — angle-bracketed (`<cli>`, `<engine-cli>`), brace-templated (`{{engine}}`), or
a shell variable (`$ENGINE`). The engine verbs are already enumerated in the file as `_ENGINE_VERBS`.

Design the exact expression yourself — that is your latitude and the reason this gate has a crew.
Two things it must do:

- **Pin all three verified misses in the assertion path**, in `TestTheInvocationPredicateItself` or
  a sibling class, so a later narrowing cannot quietly reopen the route.
- **Keep the existing `PROSE_ONLY` discriminations passing.** The current line — "tells an agent
  how to run it" vs "names the engine as a component" — was reviewed and found to be drawn in the
  right place. Do not move it.

### Measure the widening's cost, and report it

This is not optional and it is the part that most easily goes wrong. **A pattern widened until it
red-lights honest text gets deleted by the next author who trips it, after which there is no check
at all** — that is precisely why `test_mcp_adoption.py` deleted its own polarity predicates (read
`TestCLIStaysAvailableNotDeprecated`'s docstring, ~line 1268, for the measured argument).

So: run the widened pattern over the whole walk, and report **every** new site it flags that the
old pattern did not. For each, say whether it is a genuine second path or an honest sentence caught
by accident. **A widening that red-lights honest text is a finding to report, not a success to
declare.** If the cost is too high, say so and propose the narrower version — that is a complete,
successful outcome for this gate.

One boundary case the reviewer flagged and left to the Commander, which you should decide and pin
either way: `skills/write-a-skill/SKILL.md:20`, an archetype table cell reading *"a
`templates/*.json` checklist driven through `checklist_engine.py`"*. It is currently left alone, and
it is the one of the six prose mentions that asserts a **drive path**. Add it to `PROSE_ONLY`, or
decide it belongs on the other side — either way, put the string in the test so the boundary is
pinned rather than incidental.

---

## Half (b) — a whole agent-facing surface that no walk reads

`.agent-work/templates/` is a **tracked** overlay of the skills templates, and workbench doctrine
tells an agent to **prefer** it over the bundled `skills/` copy when instantiating. (You can see
that instruction in this run's own engine output: *"from `.agent-work/templates/STATE_NOTE.template.md`,
or the bundled `skills/workbench/templates/STATE_NOTE.template.md` when the project has no
`.agent-work/templates/` overlay"*.)

So after a `skills/`-only sweep, the guard goes green while **the copy an agent in this repo actually
instantiates still hands over the second path.**

**Measured today by the Commander.** The overlay carries **7** `<engine>` occurrences and **2**
`CLI fallback` clauses, and every one of the five files is **byte-identical** to its `skills/`
source right now:

| Overlay file | `skills/` source | Carries |
|---|---|---|
| `.agent-work/templates/COMMANDER_SPINE.template.json` | `skills/commander/templates/COMMANDER_SPINE.template.json` | 3 `<engine>` (lines 10, 49, 123) + clauses |
| `.agent-work/templates/ADMIRAL_SPINE.template.json` | `skills/admiral/templates/ADMIRAL_SPINE.template.json` | 2 `<engine>` (lines 10, 52) + clauses |
| `.agent-work/templates/EXPLORER_SPINE.template.json` | `skills/explorer/templates/EXPLORER_SPINE.template.json` | 2 `<engine>` (lines 12, 78) + clauses |
| `.agent-work/templates/gated-engine-SKILL.template.md` | `skills/write-a-skill/templates/gated-engine-SKILL.template.md` | 1 clause (line 15) |
| `.agent-work/templates/survey-SKILL.template.md` | `skills/write-a-skill/templates/survey-SKILL.template.md` | 1 clause (line 11) |

Each is **mirrored again** under `.agent-work/templates/.baseline/<skill-name>/`, also tracked, also
byte-identical.

**This is inside the mission, not adjacent to it.** The launch order's own acceptance test is:
*"after your change, instantiate a fresh spine from your edited template and read its `init` and
`plan` imperatives. If a `<engine>` token or a CLI-fallback clause still reaches a Commander there,
the sweep is not done, whatever a grep over the templates says."*

### What to do

Extend the walk to the overlay **by a directory/suffix rule, never a file list** — the same way
`SPEC_SUFFIXES` extends it to `specs/**/*.toml`. The exception list must stay at length **zero**.

Then verify three things and report each:

1. **The two pre-ruled survivors are still OUT by the structural rule alone**:
   `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` (a historical plan
   record) and `scripts/init_work_area.py:24` (the comment documenting the never-resolved-placeholder
   convention). Neither may be named anywhere in the guard.
2. **No lane-D2 file enters the walk.** Measured: every file under
   `.agent-work/templates/.baseline/constellation-workbench/` is already clean of both patterns, so
   widening here adds no fenced-file dependency. Confirm that yourself.
3. **The guard's RED now names overlay sites.** That is what proves the walk genuinely reached it.

Mind the **vacuity floors** — `TestTheWalkIsNotVacuous` asserts `≥60` skills files, `≥1` spec file,
`≥600` texts. Add a floor for the new surface too, so a moved or emptied overlay says so instead of
silently covering nothing.

The overlay also contains `.agent-work/567-d1/**` siblings — this run's own artifacts, the launch
order, notes, handoffs, crew results. **Those must not enter the walk**: they quote the clause
constantly and they are records, not instruction. Make sure your rule scopes to
`.agent-work/templates/` specifically, and say how you expressed it.

---

## Close criteria

1. The guard **catches** all three respelled command lines, pinned as assertions.
2. The guard **still leaves** the reviewed `PROSE_ONLY` shapes alone; the archetype-table boundary
   case is decided and pinned either way.
3. The walk reaches `.agent-work/templates/**`, expressed as a rule, and **not** this run's own
   `.agent-work/567-d1/**` artifacts.
4. Exception list length is still **zero**; both pre-ruled survivors are still out structurally.
5. `pytest tests/test_cli_retirement_guard.py -k "not TestNoSecondPathReachesAnAgent"` **passes**
   (predicate + floor tests green).
6. `pytest tests/test_cli_retirement_guard.py -k TestNoSecondPathReachesAnAgent` **fails**, and its
   output **names at least one `.agent-work/templates/` site**.
7. The false-alarm cost of the widening is measured over the whole walk and reported site by site.
8. **Nothing was swept.** `git status --porcelain` shows only `tests/test_cli_retirement_guard.py`.

## Allowed scope

- **Modify**: `tests/test_cli_retirement_guard.py`
- Nothing else. Read anything you like.

## Specific exclusions

Do **not** edit `tests/test_mcp_adoption.py` (gate `g2` inverts it), and do **not** touch any file
under `skills/`, `specs/`, `docs/`, `scripts/`, `episodes/`, `map/`, or `.agent-work/templates/`.
Fenced to other lanes this wave: `skills/workbench/**`, `docs/agents/CREW_CONTEXT.md` (D2);
`scripts/mcp_spine_server.py`, `episodes/**` (E); `scripts/run_crew.py` (F);
`scripts/checklist_engine.py` (H); `map/INDEX.md` (Admiral).

## Constraints

1. **NO exception list.** Exclude by a rule the walk applies, never by naming a file.
2. **Assert against the text's absence**, never against a description of the rule.
3. **A guard that loops must assert what it looped over** — keep the census in every failure message
   and add a floor for the new surface.
4. **Report the widening's cost.** A narrower pattern with a stated residual beats a wide one that
   red-lights honest text.
5. Do not make the guard green. It must remain RED on the corpus.

## Deliverable path check

`git check-ignore tests/test_cli_retirement_guard.py` → exit **1** (not ignored). Verified.
`git check-ignore .agent-work/567-d1/crew-handoffs/g1b-implementer-result.md` → exit **1**. Verified.

## Map anchors (inbound)

No architecture map exists in this repo (`map_orient` → `DEGRADED-UNPARSEABLE`). Entry points:

- `tests/test_cli_retirement_guard.py` — the guard itself; `ENGINE_INVOCATION_RE`, `_ENGINE_VERBS`,
  `SPEC_SUFFIXES`, `_walk_spec_files`, `TestTheWalkIsNotVacuous`, `TestTheInvocationPredicateItself`.
- `.agent-work/567-d1/crew-handoffs/g1-reviewer-result.md` — the attack that produced this gate,
  including the 13 misses it found and which of them fall inside a declared limit.
- `tests/test_mcp_adoption.py:1268` — `TestCLIStaysAvailableNotDeprecated`'s docstring: the repo's
  own measured argument for why an over-eager predicate is worse than a stated residual. **Read it
  before you widen.**
- `tests/test_mcp_adoption.py:838` — `TestTier2SpineAlreadyBoundForDispatchedCrews`, the in-tree
  precedent this guard generalizes.
- `scripts/init_work_area.py:24` — the placeholder convention, and one of the two must-survive sites.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q
python3 -m pytest tests/test_cli_retirement_guard.py -q -k "not TestNoSecondPathReachesAnAgent"   # MUST pass
python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent          # MUST fail
git status --porcelain -- skills specs docs scripts episodes tests map .agent-work/templates
```

The gate's own closing check, which the Commander re-runs independently:

```sh
set -o pipefail
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent' >/dev/null 2>&1 \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent > /tmp/g1b-guard.log 2>&1 \
  && grep -q '.agent-work/templates/' /tmp/g1b-guard.log
```

## Test mode

**Test-first**, in the same form as `g1`: the deliverable *is* a test, and the gate closes on it
being RED on the corpus while its own predicate and floor tests are GREEN.

## Required evidence

- The widened pattern, quoted, with the reasoning for its exact shape.
- The three respelled command lines shown caught, and the pinned assertions that hold them.
- The false-alarm delta over the whole walk: every site the widened pattern flags that the old one
  did not, each classified.
- The guard's RED output naming at least one `.agent-work/templates/` site.
- The rule you used to include `.agent-work/templates/` while excluding `.agent-work/567-d1/**`,
  and the confirmation that both pre-ruled survivors are still out.

## Suggested model tier

**Opus**, elevated reasoning effort. Getting a pattern's width right is the wave's load-bearing
unknown, and both failure directions — too narrow (a live evasion route) and too wide (a check the
next author deletes) — are real and were measured in this repo.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: the widened pattern cannot be made to catch the three misses without
red-lighting honest text (report the measurement and propose the narrower version — that is a
complete outcome); including `.agent-work/templates/` cannot be expressed as a rule without also
pulling in this run's own artifacts; or the work would require editing a file outside Allowed Scope.

## Return format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d1/crew-handoffs/g1b-implementer-result.md` **before ending your turn** — that
write is the delivery. Include a `Return status` field whose value is exactly `complete` (lowercase)
when the close criteria are met. Include a `Workflow Feedback` section: what helped, what got in the
way, and your own mistakes.
