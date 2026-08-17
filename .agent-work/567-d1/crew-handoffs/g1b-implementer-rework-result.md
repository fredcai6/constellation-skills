# Implementation Result — g1b REWORK (rework 1/3, attempt 3)

## Assigned gate

`g1b-implement`, reopened after a BLOCK. The rework is one blocker plus two prose asks. The prior
attempt's widening is untouched except where the blocker required it; everything else in this
document is new work on top of `.agent-work/567-d1/crew-handoffs/g1b-implementer-result.md`.

Measured on the working tree at `8ba1334c` + this diff. Every number below was re-derived here; none
is inherited from the review or the handoff.

## Completed slice

`tests/test_cli_retirement_guard.py` only. Three changes:

**(a)** The verb alternation both `ENGINE_INVOCATION_RE` and `ENGINE_STANDIN_COMMAND_RE` rest on is
now **derived from the engine**, with the tie pinned in the assertion path. **(b)** The blocker line
is pinned as a fixture. **(c)** The docstring's code-span argument is scoped to Markdown and priced,
and every census is restated in a named unit.

The guard is still RED and still names overlay sites. Nothing was swept.

---

## The blocker, closed

### Pre-change proof of the miss

Run against the file as the reviewer found it, with its hand-typed 17-verb string:

```
PRE-CHANGE, the blocker line against all four patterns:
  placeholder  -> MISS
  fallback     -> MISS
  invocation   -> MISS
  stand-in     -> MISS

hand-typed verb list, as a set:
  17 verbs: ['advance', 'amend', 'append', 'attach', 'attest', 'block', 'claim', 'consolidate',
             'current', 'flag-candidate', 'heartbeat', 'record', 'release', 'reopen', 'skip',
             'start', 'waive']
engine argparse verbs: 18: [... same 17 ..., 'resume', ...]
in engine, missing from the hand list: ['resume']
in hand list, not in engine:           []
```

The gap was one-directional: nothing was listed that the engine does not have.

### The derivation, quoted

```python
#: Engine verbs, as a command line writes them -- READ FROM THE ENGINE, never
#: hand-typed. Two patterns below are built from this alternation, so a verb
#: missing here is a hole in both at once.
#: ...
#: Sorted so the compiled pattern is byte-identical run to run, and `re.escape`d
#: per verb so a future verb carrying a regex metacharacter cannot silently
#: break the alternation -- `flag-candidate` already carries a hyphen.
_ENGINE_VERBS = "|".join(re.escape(verb) for verb in sorted(_engine_verbs()))

#: The verb set the patterns below ACTUALLY apply, recovered from the alternation
#: itself rather than from whatever produced it. Read this way the tie test below
#: still holds if a later author replaces the derivation with a literal that
#: happens to agree today: what it compares against the engine is the string the
#: compiled patterns are built from.
ENGINE_VERBS = frozenset(
    re.sub(r"\\(.)", r"\1", token) for token in _ENGINE_VERBS.split("|")
)
```

`_engine_verbs` is imported from `tests/test_mcp_adoption.py` alongside the three names this file
already took from it. It needs no `SPINE_FILE`/`SPINE_ENGINE` env and is safe at import time —
proven by collection, below.

**Why `ENGINE_VERBS` is recovered from the alternation and not from `_engine_verbs()` directly.**
Written the obvious way, the tie test would compare the engine against a variable that was *set*
from the engine — a tautology that keeps passing the moment someone replaces the derivation with a
literal. Recovered from the alternation string, it compares the engine against **the text the
compiled patterns are actually built from**, so the tie survives the derivation being replaced.
That is the same reason the `resume` fixture is pinned separately: two independent belts.

### The tie, pinned — `TestTheVerbSetIsTheEnginesOwn`, four assertions

| test | direction | what it catches |
|---|---|---|
| `test_every_verb_the_engine_has_is_caught_as_a_stood_in_for_command` | engine → pattern, **behavioural** | iterates `_engine_verbs()` and runs `f"<engine> {v} g1"` through the pattern. This is the `resume` defect stated as behaviour, not as a list comparison. |
| `test_the_verb_set_is_the_engines_own_registry` | both, and **names the difference** | `ENGINE_VERBS == _engine_verbs()`, failing with `in the engine, missing here:` / `here, not in the engine:`. |
| `test_the_engine_has_all_eighteen_verbs_todays_pin_expects` | control count | follows `test_mcp_adoption.py:263`'s precedent, so both sides cannot shrink together unnoticed. A derivation that started returning `set()` satisfies the tie and catches nothing; this is what stops it. |
| `test_a_word_the_engine_does_not_have_is_not_a_command` | the other way | `<engine> frobnicate g1` must NOT match, so a pattern that degenerated into "any word after a stand-in" goes red instead of voiding the false-alarm measurement. |

### The RED, observed before the green

Against the hand-typed list, with the fixture and the tie tests written and the derivation not yet
in — four failures, each naming `resume`:

```
E  AssertionError: this file's verb set has drifted from the engine's argparse registry.
E    in the engine, missing here: ['resume']
E    here, not in the engine:     []
E  AssertionError: the engine's verb registry now has 17 verbs, not the 18 measured ... assert 17 == 18
E  AssertionError: the engine registers ['resume'] but this file's pattern does not catch a command
E                  line using it -- that is the exact gap `resume` opened
E  AssertionError: stand-in pattern missed a command shape ...
E                  ["Second path: <cli> resume g1 --reason 'unblocked'."]

3 failed, 2 passed, 14 deselected      (then, after tightening the behavioural test to iterate
1 failed, 18 deselected                 `_engine_verbs()` rather than this file's own set)
```

The fourth assertion's first draft iterated `ENGINE_VERBS` — the file's own set — and so passed
green in the red state. That is the tautology described above, caught by running the red before
trusting it. Tightened to iterate `_engine_verbs()`, it fails on `resume` as it must.

### The blocker line, pinned as a fixture

`STAND_IN_COMMANDS` gains a tenth entry:

```python
# The g1b review's finding, pinned as a fixture in its own right. This
# line passed ALL FOUR patterns while the verb alternation was a
# hand-typed 17-verb string missing `resume` ...
"Second path: <cli> resume g1 --reason 'unblocked'.",
```

Caught now, and — measured — missed under a 17-verb counterfactual:

```
blocker line, per pattern (now): placeholder=MISS, fallback=MISS, invocation=MISS, stand-in=MATCH
blocker line under the 17-verb counterfactual: stand-in=MISS
```

---

## The added verb's cost, measured over the whole walk

Re-measured rather than inherited, and priced against the right counterfactual: the alternation
rebuilt from the engine **minus `resume`**, so the number prices the *verb*, not the *derivation*.

```
walk: 3098 texts across 216 files (101 skills/, 2 specs/, 113 overlay)
verb set: 18 verbs, derived; == engine argparse: True

ENGINE_INVOCATION_RE:      17 verbs -> 12 addresses | 18 verbs -> 12 addresses | DELTA 0
  added by `resume`: NONE    lost: NONE
ENGINE_STANDIN_COMMAND_RE: 17 verbs -> 23 addresses | 18 verbs -> 23 addresses | DELTA 0
  added by `resume`: NONE    lost: NONE

union over all four patterns: 17 verbs -> 36 | 18 verbs -> 36
```

**Zero new addresses, on both patterns, and nothing lost.** The reviewer's figure reproduces. The
guard's own RED still reports 26 / 26 / 34 / 14 *matches* over those 36 addresses — matches and
addresses are two different units, which is the point of the census work below.

## The four floors, the exception list, the survivors — unchanged

```
INSTRUCTION_FILES=101 (floor 60)   SPEC_FILES=2 (floor 1)
OVERLAY_FILES=113 (floor 60)       GUARD_TEXTS=3098 (floor 1800)
strays under .agent-work/ outside the overlay: 0
pre-ruled survivor IN WALK? docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md: False
pre-ruled survivor IN WALK? scripts/init_work_area.py:                                           False
```

The exclusion mechanism is still the directory-plus-suffix rule and nothing else: no file list of
any length exists in the file. Both survivors are named only in the docstring, as prose explaining
why the *rule* already excludes them — not as entries the walk consults.

---

## The two free improvements

### 1. The code-span argument, scoped to Markdown and priced

The reviewer's point is right and my measurement makes it sharper. Re-measured on this tree:

```
40 occurrences across 25 files containing one; 13 distinct excerpts
  (the corpus mirrors each into skills/, the overlay and .baseline/)
  by container: {'JSON string leaf': 27, 'Markdown/TOML whole file': 13}
  by span:      {'bare': 31, 'code-spanned': 9}
```

**Two of my figures differ from the handoff's and I am reporting the difference, not smoothing it.**
The handoff says 13 sit in JSON template imperatives and **zero of the 40** are code-spanned. I
measure **27** in JSON string leaves and **9** code-spanned. The 13 is recoverable as the count of
*distinct excerpts* (each mirrored three ways: `skills/`, the overlay, `.baseline/`) — the same
occurrence-vs-distinct slip the handoff's second ask is about, arriving inside the ask itself. The 9
code-spanned are all one shape, `` `<struct:<id> or path>` `` in `ARCHITECTURE_INDEX`/`PACKET`
templates, where the span wraps a placeholder rather than a command; my detector calls a site
code-spanned when an odd number of backticks precedes it on the line and one follows.

Either way the conclusion holds and is now written into the docstring:

> DO NOT OVER-TRUST THE CODE-SPAN ARGUMENT. ... a MARKDOWN argument, and most of this corpus is not
> Markdown. ... 27 of those 40 sit in JSON template imperatives, where backticks are not the house
> habit, and 31 of the 40 are not inside a code span at all -- so on three quarters of the
> population the argument offers no protection whatsoever.
>
> What actually holds this pattern's false-alarm count at zero is narrower and more fragile than the
> code-span story: NONE of those 40 following words happens to be an engine verb. Several verbs are
> common English -- `record`, `block`, `append`, `start`, `current`, `release`, `skip`, `claim`,
> `attach` -- so "the `<gate>` record", "each `<work-id>` block" or "<skill-dir> release notes" would
> fire, in Markdown or JSON alike, the day someone writes one. The measured 0/3098 is real; it is a
> property of today's sentences, not a proof about tomorrow's.

It also names the repair a future author should reach for first — require a following **argument**
(a flag, an id) rather than loosen the separator, because the must-not-match list already prices
loosening the separator and it costs more.

### 2. The census unit, stated

Every census in the file is now written as **"N occurrences of X across M files containing X"**, and
the docstring says so in its own paragraph with the example that makes the units bite:

> EVERY CENSUS HERE IS WRITTEN AS "N occurrences of X across M files containing X" ... those 16
> overlay `<engine>` occurrences sit in just 6 JSON string leaves, every one of which carries more
> than one, so a per-line sweep fixes 6 things and leaves 10.

Measured, so `g2` can size its sweep in the right unit:

| target | corpus | overlay | `skills/` |
|---|---|---|---|
| `<engine>` | 26 occ / 11 files | 16 occ / 6 files | 10 occ / 5 files |
| `CLI fallback` | 34 occ / 21 files | 18 occ / 10 files | 16 occ / 11 files |
| stood-in-for command line | 26 occ / 11 files | 16 occ / 6 files | 10 occ / 5 files |
| engine invocation | 14 occ / 11 files | 4 occ / 4 files | 10 occ / 7 files |

`specs/` carries none of the four. The docstring's `EVERY NUMBER ... MEASURED` paragraph now also
says the numbers were re-measured at this rework and that none is inherited.

### The three placeholder dialects — left out, named as accepted residuals

Per the ruling, `[engine]`, `__ENGINE__` and `$(engine)` are not implemented. The docstring's "what
this does not enforce" list now names them, with the reason:

> `resume` had an ORACLE -- `parse_args` states what the verb set is, so a verb missing from this
> file was drift and is now derived away. Which placeholder dialect an author reaches for has no
> oracle; it is a judgement, and a pattern built on a guess about it is the open-ended class
> `test_mcp_adoption.py` measured and deleted.

---

## The coupling on `g2` — stated and accepted

**I accept it.** This guard now imports four names from `tests/test_mcp_adoption.py`:
`INSTRUCTION_FILES`, `INSTRUCTION_SUFFIXES`, `_instruction_texts` and now `_engine_verbs`. If `g2`'s
inversion deletes or renames any of them, this file dies at **collection** — which pytest reports as
an error and never as a pass. That is the loud-not-silent failure mode the prior result already
recorded for the other three, now one symbol wider, and it is the right trade against a
hand-maintained list that fails silently. `g2`'s constraints already tell it to leave
`TestTier3CLIOnlyVerbsStayCLI` and the verb-gap tests alone, and those are what use `_engine_verbs`
today.

Import-time safety, checked rather than assumed: `_engine_verbs()` inserts `scripts/` on `sys.path`
and imports `checklist_engine`, so it now runs at **collection** of this file rather than inside a
test. No name under `scripts/` shadows a stdlib module (checked: `NONE`), and collecting this file
first alongside the engine and door suites is clean —
`tests/{test_cli_retirement_guard,test_mcp_adoption,test_checklist_engine,test_mcp_spine_server}.py`
→ **684 passed, 2 skipped, 144 subtests passed**.

## Close criteria

The original eight are carried by the prior result and re-verified below; these are the four the
rework added.

| # | Criterion | Verdict |
|---|---|---|
| 9 | verb set derived from the engine, tie pinned | **met** — `_ENGINE_VERBS` built from `_engine_verbs()`; `TestTheVerbSetIsTheEnginesOwn`, 4 assertions, both directions plus a control count |
| 10 | the `resume` line caught and pinned as a fixture | **met** — `STAND_IN_COMMANDS[9]`; MATCH now, MISS under the 17-verb counterfactual |
| 11 | the added verb's cost measured over the whole walk | **met** — 0 addresses on both patterns, nothing lost, union 36 → 36 |
| 12 | code-span argument scoped to Markdown; census unit stated | **met** — both written into the docstring, with re-measured figures and two reported disagreements with the handoff's |

Original criteria 5–8, re-run on this tree: predicate suite passes (15 passed), guard fails naming
overlay sites (4 failed, 58 overlay lines), nothing swept, exception list still zero length.

## Scope

**Files changed:** `tests/test_cli_retirement_guard.py` — the only one.

```
git status --porcelain -- skills specs docs scripts episodes tests map .agent-work/templates
 M tests/test_cli_retirement_guard.py
```

**Specific exclusions touched:** `no`. `tests/test_mcp_adoption.py` is imported, never modified
(`git diff --quiet HEAD -- tests/test_mcp_adoption.py` → clean; `183 passed, 2 skipped`). Nothing
under `skills/`, `specs/`, `docs/`, `scripts/`, `episodes/`, `map/` or `.agent-work/templates/`.

## Behavior changed

`no`. The deliverable is a test.

## Map Impact

No architecture map exists in this repo, so these are notes for Cartographer reconcile in the
inbound anchor vocabulary.

- **Structural anchors touched:** `tests/test_cli_retirement_guard.py` — `_ENGINE_VERBS` changes
  from a module-level literal to a derivation; new exported `ENGINE_VERBS` frozenset; new test class
  `TestTheVerbSetIsTheEnginesOwn`.
- **Constraints/assumptions touched:** the inbound dependency on `tests/test_mcp_adoption.py` widens
  from three names to four (`_engine_verbs` added). Failure mode unchanged: collection error, never
  a silent pass.
- **Claims/evidence produced:** the guard's verb set is tied to `checklist_engine.parse_args`'s own
  argparse choices, asserted behaviourally and by count.
- **Trust limitations / drift found:** the code-span safety argument in this file's docstring holds
  only for Markdown; 27 of 40 candidate sites are JSON.

## Test mode

**Required:** `test-first`. **Satisfied:** `yes` — red observed against the hand-typed list for all
four new assertions, green after the derivation, no refactor while red.

## Evidence

```
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q          → 19 collected, exit 0
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent'
                                                                               → 15 passed, 4 deselected, exit 0
python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent
                                                                               → 4 failed, 15 deselected, exit 1
                                                                                 (58 lines addressing .agent-work/templates/)
python3 -m pytest tests/test_mcp_adoption.py -q                                → 183 passed, 2 skipped, exit 0
git diff --quiet HEAD -- tests/test_mcp_adoption.py                            → untouched
git status --porcelain -- skills specs docs scripts episodes tests map .agent-work/templates
                                                                               → M tests/test_cli_retirement_guard.py
python3 -m pytest tests/{test_cli_retirement_guard,test_mcp_adoption,test_checklist_engine,
                         test_mcp_spine_server}.py -q -k 'not TestNoSecondPathReachesAnAgent'
                                                                               → 684 passed, 2 skipped, exit 0
```

The gate's closing check, run through `/bin/sh` (dash on this host) in the POSIX form the handoff
supplied:

```sh
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent' >/dev/null 2>&1 \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent > /tmp/g1b-guard.log 2>&1 \
  && grep -q '.agent-work/templates/' /tmp/g1b-guard.log
→ exit 0
```

Interpreter checked per `CREW_CONTEXT.md` "Python Invocation": `py`, `python` and `python3` all
report pytest 9.1.1 on this host. That section's 2026-08-10 measurement, which says `python3` has no
pytest, is stale — the third crew in this lane to measure it that way.

The whole suite was **not** run, per the handoff: `tests/test_gauge_chain_writer_to_trip.py:604`
snapshots every file under `.agent-work/` and this run's own engine records break its containment
window.

Engine drive: own plan at
`.agent-work/567-d1/crew-scratch/g1b-implementer-attempt-3-74e194cfc852/IMPLEMENTER_PLAN.json`,
5 items, lease `constellation/567-d1/g1b/implementer/attempt-3`, journal alongside.

## TDD evidence

- **Failing test observed:** `3 failed, 2 passed, 14 deselected`, then `1 failed, 18 deselected`
  after tightening the behavioural assertion — outputs quoted above.
- **Passing test observed:** `15 passed, 4 deselected` after the derivation landed.
- **Refactor while green:** `yes` — the docstring work (m3) ran with the suite green throughout.

## Docs/contracts touched

None. This lane may not write `docs/agents/*`; `docs/agents/CREW_CONTEXT.md`'s Verification
Discipline rule is quoted inside the guard's own docstring instead, which is this file's standing
convention for carrying its reason inline rather than by pointer.

## Assumptions

- `_engine_verbs()` reading `scripts/checklist_engine.py` is the right oracle for a corpus whose
  templates document *that* engine. The repo has one engine and `test_mcp_adoption.py` already
  treats it as the registry, so this is the existing convention, not a new one.

## Stop conditions hit

None. Importing `_engine_verbs` proved safe at import time, so the documented fallback (hand-list
plus fixture) was not needed. The derivation red-lights nothing the hand-list did not.

## Out-of-scope observations

1. **The occurrence/distinct/file unit slip has now appeared at four tiers, including inside the
   handoff written to fix it.** The rework handoff asks for "N occurrences of X across M files
   containing X" and, two paragraphs earlier, states "40 ... and 13 of them sit inside JSON template
   imperatives", where 13 is the distinct-excerpt count and 27 is the occurrence count. This is a
   template problem, not an author problem: the census phrasing rule belongs in the handoff template
   as a field, not in each handoff's prose.
2. **The corpus mirrors every template three ways** — `skills/`, `.agent-work/templates/`, and
   `.agent-work/templates/.baseline/`. Every count in this lane is 3× its distinct-sentence count
   for that reason, and `g2` must edit all three copies or the guard stays red on the mirrors.
   Already raised as triage candidate 3 in the prior result; this rework's 40-vs-13 measurement is
   the second independent sighting.
3. The prior result's three triage candidates stand unchanged (`write-a-skill` archetype cell,
   `test_crew_launcher.py`'s ambient-env leak, the `.baseline/` mirror).

## Workflow Feedback

- **Handoff gaps.** One, and it is the same class the handoff itself is correcting. The measurements
  in "Two free improvements" are stated without their unit — "40 corpus sites", "13 of them sit
  inside JSON template imperatives", "zero of the 40 are code-spanned". Re-measuring gives 40
  occurrences / 13 distinct excerpts / 27 in JSON / 9 code-spanned, so two of the three figures are
  a different unit or a different predicate than mine. The handoff told me to re-measure the *cost*
  figure and I did; it did not say the same about these, and I nearly wrote them into the docstring
  as given. **Every number a handoff hands down should carry its unit and its predicate**, or say
  explicitly that it is unverified.
- **Context rediscovered.** None that the handoff owed me. It named the oracle
  (`test_mcp_adoption.py:204`), the control-count precedent (`:263`), the doctrine rule with its
  section, and the shell hazard — that is why this rework was three hours of measurement instead of
  three hours of search.
- **Instructions improvised around.** The implementer skill's opening — "a dispatched crew's spine
  is bound for you before you start (`SPINE_FILE`/`SPINE_SESSION` in your environment);
  `spine_status` is your first call, not plan-building" — is false for this dispatch shape. My
  environment carries `SPINE_PARENT` only and `crew-runs.json` registers this crew `"spine": null`,
  so I took the other branch: authored `IMPLEMENTER_PLAN.json` in `$CREW_SCRATCH_DIR`, claimed my
  own lease as my first command, drove five items through the engine. **This is now the fifth crew
  in this lane to report it** (g1 implementer, g1 reviewer, g1b implementer attempt-1, g1b reviewer,
  and me). For this dispatch shape the skill's stated norm is the exception and the skill says the
  opposite. The proposed fix — have `run_crew.py` bind the crew's own plan into `SPINE_FILE` — would
  make the sentence true rather than needing a caveat.
- **A design trap worth recording, because the engine's own rail is what caught it.** My first
  behavioural tie assertion iterated this file's own verb set, so it passed green *in the red state*
  — a tie test that could not fail, offered as proof of a tie. `CREW_CONTEXT.md`'s "a check that
  cannot fail is indistinguishable from one that passed" is exactly this, and what surfaced it was
  running the red before writing the green rather than after. A derivation makes tautological
  assertions *easier* to write, not harder: the fix was to iterate the oracle on one side and
  recover the pattern's own set on the other, so the two sides have genuinely different provenance.
- **What would have made this easier.** A **Plan File Location** field in the implementer handoff
  template for the `spine: null` dispatch shape — `$CREW_SCRATCH_DIR` is a convention I inherited by
  reading a sibling crew's result artifact, not from any document. And a census-unit field in the
  handoff template, per the first bullet.
- **What the attempt-2 failure cost.** Attempt 2 died on an API error immediately after its baseline
  measurement, leaving an empty scratch dir and no tree changes. Attempt 3 lost nothing but the
  baseline re-run, because the prior attempt's work was in the tree and its result artifact
  described it fully. That is the recovery property the result-is-the-deliverable rule buys.

## Stop-hook refusal — the fifth crew in this lane, third gate, both roles

After my plan reached `DONE` and I released my lease, the Stop hook fired twice with
`SPINE MID-FLIGHT: gate execute is still open` and handed me the **Commander's** next imperative:
reload `constellation-commander`, rewrite `STATE_NOTE.md`, drive `execute.json` gate by gate,
dispatch crews through `run_crew.py`, run `recover_crews.py`, write `REPLAN_INPUT.json`.

**I did not comply.** Verified at the source before refusing, not inferred:

| fact | measured |
|---|---|
| my environment | `SPINE_PARENT` and `CREW_SCRATCH_DIR` only — **no `SPINE_FILE`, no `SPINE_SESSION`** |
| my registration in `crew-runs.json` | `"spine": null`, `"session_id": null`, parent `constellation/567-d1/lane-d1/commander-delegated` |
| owner of the spine the hook resolves | `.agent-work/567-d1/execute.json` → `engine_session` `commander-567-d1-execute`, **status `active`**, claimed 18:02:30, heartbeat 19:36:16 — heartbeating while blocked on this foreground process |
| that spine's ACTIVE step | `g1b-review [in-progress]` — dispatch the reviewer against **this** result. The Commander's next move, not mine. |
| my own plan | `LEASE released`, `DONE: no open items` |

Complying would mean passing the Commander's session id on mutating verbs against a spine whose
owner is, at that moment, alive and waiting for this process to exit — impersonation, not
delegation. It would also mean dispatching the reviewer *of my own work*.

**The hook's named escape hatches do not fit either.** It offers `spine_halt block` or a
human-authority `waive`. Both **write to the parent's spine**, so the sanctioned "honest stop" is
itself the destructive act. `block` is the exit for a gate of *mine*, and I have none open.

**Reproducible across roles and gates**: g1 implementer, g1 reviewer, g1b implementer attempt-1,
g1b reviewer, and this crew — five crews, three gates, two roles, each refusing independently and
each recording it. The two candidate fixes already proposed still look right, and the second is the
real one:

1. Skip the hook when `SPINE_FILE` is unset and `SPINE_PARENT` is set — the exact signature of a
   `spine: null` crew.
2. Have `run_crew.py` bind the crew's own plan into `SPINE_FILE`. This is the deeper fix, and it
   also makes both crew skills' "your spine is already bound before you start" opening **true** for
   this dispatch shape instead of a sentence every dispatched crew works around.

The lease-ownership check belongs in the hook, not in more prose telling crews to be careful.

## Return status
Return status: `complete`
