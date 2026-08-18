# Review Result — g1b RE-REVIEW (rework 1/3, reviewer attempt 2)

## Assigned Gate
`g1b-review` — Widen the guard: placeholder-agnostic command lines, and the tracked template
overlay: review. **Re-review of a reworked gate**, after round 1 returned `BLOCK`.

## Verdict
`APPROVE`

## Result
`APPROVE`

Recorded through the engine at `.agent-work/567-d1/g1b-review/review-2.json`
(`consolidated: verdict=APPROVE findings=0`). Twelve checks, all visited, all `pass`: `r0`–`r6` from
the overlay template plus five I appended for the addendum's named work — `r7-oracle`, `r8-cost`,
`r9-regression`, `r10-import`, `r11-attack`. Round 1's survey is preserved untouched at
`review.json`, and its result is preserved in git at `4df66479`; this file supersedes it.

Measured at `4df66479`. Every number below is mine.

> **This supersedes round 1's `BLOCK` at this path.** That document is recoverable verbatim from
> `git show 4df66479:.agent-work/567-d1/crew-handoffs/g1b-reviewer-result.md`.

---

## The blocker, closed — and closed at the class

Round 1 found `_ENGINE_VERBS` hand-typed with 17 verbs against the engine's 18, missing `resume`, so
`Second path: <cli> resume g1 --reason 'unblocked'.` passed all four patterns clean. The Commander
ruled for the durable fix rather than the one-token one. **It landed, and it is genuinely durable.**

### 1. The verb set is the engine's own — checked against two oracles, neither of them the repo's helper

The obvious way to "verify" this is to call `_engine_verbs()` and compare — which is the tautology the
implementer itself warned about. So I read the engine two other ways:

```
A. from `checklist_engine.py --help` choices block   : 18
B. from argparse's own invalid-choice error          : 18
C. guard's ENGINE_VERBS (recovered from alternation) : 18
D. repo helper _engine_verbs()                       : 18

A == C : True | missing from guard: [] | extra in guard: []
B == C : True        D == C : True        'resume' in guard verb set: True
blocker line vs stand-in pattern: True   (was MISS, is now MATCH)
```

The compiled alternation, verbatim:
`advance|amend|append|attach|attest|block|claim|consolidate|current|flag\-candidate|heartbeat|record|release|reopen|resume|skip|start|waive`

### 2. Red-proofed by mutation — four ways, every one red, every one naming the difference

*"A check that cannot fail is indistinguishable from one that passed."* I made the two sides disagree
in memory rather than trusting the assertion's shape.

| mutation | result |
|---|---|
| **engine gains a verb** the guard lacks | tie **RED**: `in the engine, missing here: ['frobnicate']`; behavioural test **RED** |
| **guard loses `resume`** (the exact historical drift) | tie **RED** naming `resume`; behavioural **RED**; control count **RED** (`17 != 18`); pinned fixture **RED**; and the blocker line goes **MISS** again — the evasion route visibly reopens |
| **derivation replaced by a literal that agrees today**, then the engine moves | tie **still RED** — the claimed durability property is real, not asserted |
| **pattern degenerates** to "any word after a stand-in" | negative control **RED** |

And the case the tie *cannot* catch, which is exactly what the control count exists for — both sides
shrinking together off a broken oracle:

```
oracle returns 2 verbs      -> tie GREEN (they agree), control count RED   <- only the pin catches it
oracle returns the EMPTY set -> tie RED and control count RED
```

The `re.escape` claim also holds: `flag-candidate`'s hyphen survives compile, match, and the
unescape round-trip.

**This is a stronger closure than "add `resume`" would have been**, and the addendum was right to
rule for it: the fix now has an oracle behind it, four assertions of different provenance pinning it,
and a fixture that keeps it closed even if the derivation is later replaced.

### 3. The derivation cost nothing — re-measured after the change

Priced against the right counterfactual (the alternation rebuilt from the engine **minus `resume`**,
so the number prices the *verb*, not the *derivation*):

```
walk: 3098 texts across 216 files (101 skills/, 2 specs/, 113 overlay)
verb set: 18 verbs, derived; == engine argparse: True

ENGINE_INVOCATION_RE       17 verbs -> 12 addr / 14 occ | 18 verbs -> 12 addr / 14 occ | DELTA 0
ENGINE_STANDIN_COMMAND_RE  17 verbs -> 23 addr / 26 occ | 18 verbs -> 23 addr / 26 occ | DELTA 0
union over all four patterns: 36 -> 36        added by `resume`: NONE    lost: NONE
```

The stronger claims still hold after the rework: stand-in addresses **not** reported by `g1`'s three
patterns = `[]`, and every one of the 23 is also an `<engine>` address — so no honest text is newly
red-lighted. Per the addendum I did not re-derive the headline census from scratch; it fell out of
this measurement anyway and reproduces figure for figure.

---

## 4. Nothing regressed

| what | measured |
|---|---|
| floors | skills **101**≥60, specs **2**≥1, overlay **113**≥60, texts **3098**≥1800 |
| exception list | **zero**. `_walk_dir`'s only filter is `p.is_file() and p.suffix in suffixes`; a source scan for any `EXCLUDE/SKIP/ALLOW/IGNORE/EXEMPT` assignment finds **NONE** |
| both pre-ruled survivors | out **by the walk rule alone** — each appears exactly once in the file, both occurrences inside the module docstring (verified by index against `from __future__`), never in a code path; neither in `GUARDED_FILES` though both files exist |
| `PROSE_ONLY` / `COMMAND_SHAPED` | all three discriminations still pass; 5 and 6 entries, incl. the `write-a-skill` archetype cell |
| overlay scope rule | verified **structurally**: `.agent-work/567-d1` is neither ancestor nor descendant of the overlay root; strays **0**; **no symlink** escapes the overlay |
| lane-D2 fence | `.baseline/constellation-workbench/` = 4 files, 20 texts, **0** matches on all four patterns — still no fenced-file dependency |

## 5. The import is safe at collection time

A guard that dies at collection is a guard that never runs. Four checks:

- **Needs no env.** 19 collected with `SPINE_FILE`/`SPINE_SESSION`/`SPINE_ENGINE`/`SPINE_PARENT`/
  `CREW_SCRATCH_DIR`/`CLAUDE_PROJECT_DIR` all stripped, exit 0; and `env -i` with only `PATH`/`HOME`
  → 15 passed.
- **No shadowing.** All 48 `scripts/*.py` names checked against `sys.stdlib_module_names` → **NONE**,
  and none resolvable elsewhere on `sys.path` → **NONE**. The `sys.path.insert` cannot hijack a later
  import.
- **No ordering dependency.** Guard collected **first** and guard collected **last** against
  adoption / checklist_engine / mcp_spine_server / generate_spine / spine_lifecycle →
  **974 passed, 2 skipped, 144 subtests**, byte-identical both ways.
- **The one global mutation is pre-existing, not introduced.** Importing `checklist_engine` runs
  `_utf8_stdio()`, which reconfigures `sys.stdout`/`stderr`. But `tests/test_generate_spine.py` and
  `tests/test_spine_lifecycle.py` **already import it at module level**, so any whole-suite run did
  this before the rework. The guard only adds it to a guard-only run, where it is harmless
  (`try/except AttributeError, OSError`).

## 6. Attacked once more — 32 strings, two observations, no findings

The widened verb arm holds. All five `resume` dialects caught (angle, `{{ }}`, `$ENV`, `%WIN%`,
single-brace), tab and double-space separators caught, trailing punctuation caught, `frobnicate`
still clean. **No new evasion route of the `resume` class.**

Correctly missed, each inside a declared limit or handing an agent no runnable path: verb on the next
line, code span, colon or quote between stand-in and verb, capitalized/uppercase verb,
word-introduced with no stand-in, bare program word.

**Observation A — the separator gap, and I want to be precise about why it is not a second BLOCK.**
The docstring's invariant says the stand-in must be followed by *"HORIZONTAL whitespace"*; the code
says `[ \t]`. So NBSP (U+00A0), U+202F and U+2003 all walk through. Priced:

```
[ \t]        (SHIPPED)                       addresses=23   extra vs shipped=0
[^\S\r\n]    (horizontal ws incl. unicode)   addresses=23   extra vs shipped=0   <- free
\s           (the priced loosening)          addresses=24   extra=1  skills/workbench/references/checklist-engine.md:92
corpus contains non-ASCII whitespace: NONE
```

It is the same *shape* as the closed blocker — stated broader than implemented — which is why I
looked hard at it. It is not the same *severity*, and the distinction is the one this gate already
ruled on: **`resume` had an oracle** (argparse states the verb set, so the gap was drift from a
definable truth) — **"horizontal whitespace" has none**; no definition says which code points it
means. The corpus contains no non-ASCII whitespace at all, and NBSP before a command verb is not text
a future agent restoring this doctrine would write. Flagged as `tc1`, free to fold into `g2` if the
Commander wants it; I am not blocking on it and would not have blocked round 1 on it either.

**Observation B — the declared false-alarm residual is real, and I confirmed it by writing the text
rather than reading the claim.** These honest sentences fire on the shipped pattern:

```
FIRES  'see <skill-dir> release notes for the change'
FIRES  'after a crash the <run> resume picks up where it stopped'
FIRES  'the <id> current state is read from the journal'
clean  'the `<work-id>` resume is written by the engine'      (code span saves it)
```

This is **not** a finding: the docstring predicts it exactly, names `<skill-dir> release notes`
verbatim, prices it at 0/3098 today, and names the right repair (require a following *argument*, not
a looser separator). That is the honest treatment of a residual. 12 of the 18 verbs are ordinary
English; the docstring names 9 — `resume`, `advance` and `amend` are omitted, and `resume` is the one
just added (`tc3`).

**On the upheld placeholder-dialect ruling.** I tested it rather than restating the misses. There is a
partial oracle in the repo — `generate_spine.py:439`'s `_SHIPPED_SPEC_PLACEHOLDER_PARENT_RE =
^<[A-Za-z0-9-]+>$`, and `init_work_area.py`'s comment naming the prose placeholders as
`<engine>, <date>, <N>, <path>` — and it says the sanctioned dialect is **angle-bracket**. The guard's
`_ENGINE_STANDIN` already covers a strict superset of that. So the repo's own oracle, where one
exists, argues *for* the ruling rather than against it: `[engine]`, `__ENGINE__` and `$(engine)` are
outside anything this repo's tooling accepts. The line is drawn right.

---

## Handoff compliance — the close criteria

| # | Criterion | Verdict |
|---|---|---|
| 1 | Only the guard modified; `test_mcp_adoption.py` byte-identical | **met**, in a re-derived frame — see the note below. `git diff --quiet 8ba1334c..HEAD -- tests/test_mcp_adoption.py` → exit 0 |
| 2 | `-k "not TestNoSecondPathReachesAnAgent"` passes | **met** — 15 passed, 4 deselected, exit **0** |
| 3 | `-k TestNoSecondPathReachesAnAgent` fails, naming an overlay site | **met** — 4 failed, 15 deselected, exit **1**; **58** lines address `.agent-work/templates/` |
| 4 | Exception list zero; both survivors out by the walk rule | **met** — no exclusion construct exists in any code path |
| 5 | Vacuity floors cover the new surface and the raised count | **met** |
| 9 | Verb set derived from the engine, tie pinned | **met** — verified against two independent oracles and red-proofed four ways |
| 10 | The `resume` line caught and pinned as a fixture | **met** — `STAND_IN_COMMANDS[9]`; MATCH now, MISS under the 17-verb counterfactual |
| 11 | The added verb's cost measured over the whole walk | **met** — zero on both patterns, nothing lost |
| 12 | Code-span argument scoped to Markdown; census unit stated | **met** — and every figure in it reproduces |

**One handoff-shape note, not a defect in the work.** The rework was **committed** as `4df66479`
before I was dispatched, so the handoff's `git diff HEAD -- tests/test_cli_retirement_guard.py` and
*"expect exactly one modified file"* both return **empty** against a clean tree. I re-derived the
review diff as `8ba1334c..HEAD` (426 insertions, 28 deletions, one file) and checked criterion 1 in
that frame: the commit touches exactly one file under the reviewed source paths; everything else in
it is `.agent-work/567-d1/**` run bookkeeping, outside the fenced set.

## Evidence verdict

Every claimed side-effect reproduced independently, exit codes read.

```
--collect-only -q                                     → 19 collected, exit 0   (was 15; +4 is the tie class)
-k 'not TestNoSecondPathReachesAnAgent'               → 15 passed, 4 deselected, exit 0
-k TestNoSecondPathReachesAnAgent                     → 4 failed, 15 deselected, exit 1 (58 overlay lines)
tests/test_mcp_adoption.py -q                         → 183 passed, 2 skipped, exit 0
the implementer's exact 4-suite command               → 684 passed, 2 skipped, 144 subtests, exit 0
git diff --quiet 8ba1334c..HEAD -- test_mcp_adoption  → exit 0 (byte-identical)
gate closing check, verbatim under /bin/sh (→ dash)   → exit 0
```

Interpreter checked first per `CREW_CONTEXT.md` §Python Invocation: `py`, `python` **and** `python3`
all report pytest 9.1.1. That section's 2026-08-10 measurement is stale — the fifth crew in this lane
to measure it so.

**I did not run the whole suite,** per the addendum. `tests/test_gauge_chain_writer_to_trip.py:604`
snapshots size and mtime of every file under `.agent-work/` and my own engine records would break its
containment window — round 1 paid for that lesson and `g5-final` owns the whole-suite run in a clean
detached worktree. I record this as a deliberate omission, not a gap I overlooked.

## Code/doc quality

Fowler pass at `.agent-work/567-d1/g1b-review/FOWLER_PASS-2.json`;
`scripts/verify_fowler_pass.py` → **exit 0** (`smells=12,
flagged=['duplicated-code','primitive-obsession','shotgun-surgery'],
overridden=['feature-envy','data-clumps','speculative-generality','comments-as-deodorant']`).

**Round 1's load-bearing `primitive-obsession` flag is the design root the rework actually fixed** —
`_ENGINE_VERBS` was a pipe-joined *string*, which is precisely why the missing verb was invisible. It
stays flagged, honestly downgraded: a sliver survives in the split-and-unescape recovery. Measured —
the round-trip is exact for `.`, a space and `flag-candidate`'s hyphen, and breaks for exactly one
character, a literal `|` in a verb name, where it **fails safe** (tie goes red naming the difference).

`duplicated-code` and `shotgun-surgery` are round 1's flags, **not taken**, and now marginally worse:
the `resume` story is told at four sites, and the measured figures are pinned to `8ba1334c` at four
sites in a file that has moved to `4df66479` — accurate today, citing a revision the file is past.
Neither is a blocker; both are the cost of this file's deliberate carry-the-reason-inline convention,
which is also why `comments-as-deodorant` is overridden rather than flagged.

**Record path.** Written to `FOWLER_PASS-2.json`, moved off the template default through the engine's
sanctioned `amend --delta` repair path (single `retext-check` op, `--authority
constellation/567-d1/lane-d1/commander-delegated`, reason recorded), never by hand-editing the survey.
The addendum redirected me to `.agent-work/567-d1/g1b-review/FOWLER_PASS.json` — but **that path
already held this gate's round-1 record**, so following it literally would have destroyed the audit
evidence of the BLOCK, for the same reason the addendum gave `review-2.json` its own filename. I
confirmed round 1's record is intact after my write. Raised as `tc2`.

## Map impact verdict

- **Evidence supports claimed change:** yes. The verb set really is the engine's, verified against two
  oracles and by mutation.
- **Constraints not violated:** yes. *"The corpus is walked, never listed"* holds — no exclusion
  construct exists. *"Any guard that loops must assert what it looped over"* holds via four floors plus
  a census in every message.
- **Notes match the diff:** yes. The inbound dependency really widened from three imported names to
  four, and the claimed failure mode is accurate — a rename kills the guard at **collection**, which
  pytest reports as an error, never as a pass. I verified that collection is otherwise clean.
- **Decision candidates surfaced:** yes. The placeholder-dialect residual was routed to the Commander
  as a ruling rather than settled by the crew, and the ruling holds up under test.
- **Durable context routed:** yes, plus three triage candidates from this review.

## Reconciliation check

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`). **The census `g2` depends on is
now correct and in a stated unit** — the slip that ran through three tiers is fixed. Every figure
reproduces against my own walk:

| target | corpus | overlay | `skills/` | `specs/` |
|---|---|---|---|---|
| `<engine>` | 26 occ / 11 files | **16 occ / 6 files** | 10 occ / 5 files | 0 |
| `CLI fallback` | 34 occ / 21 files | 18 occ / 10 files | 16 occ / 11 files | 0 |

That reconciles the 10-vs-6 disagreement between the handoff and round 1: **six** files carry
`<engine>`, **ten** carry a sweep target of some kind, and the docstring now states both correctly.

**What `g2` must sweep for `<engine>`, enumerated** — 16 occurrences in 6 files, every one a JSON
`.tasks.*.imperative` leaf:

```
ADMIRAL_SPINE.template.json     init 1, closeout 1     (+ the same 2 in .baseline/)
COMMANDER_SPINE.template.json   init 1, plan 1, archive 2   (+ the same 4 in .baseline/)
EXPLORER_SPINE.template.json    init 1, route 1        (+ the same 2 in .baseline/)
```

`COMMANDER`'s `archive` imperative carries **two** in each copy, so a per-line sweep fixes 6 things
and leaves 10 — which is the exact point the docstring's census-unit paragraph makes. A sweep of the
three visible copies alone leaves this guard red on the `.baseline/` mirrors.

## Blockers

**None.** The round-1 blocker is closed at the class, verified by mutation rather than by reading the
diff.

## Out-of-scope observations

Recorded as triage candidates on the survey (`tc1`, `tc2`, `tc3`).

1. **`tc1` — the `[ \t]` vs "horizontal whitespace" separator gap.** `[^\S\r\n]` closes it at zero
   measured cost. Prospective, not live.
2. **`tc2` — the Fowler record path collides across *rounds*, not just gates.** Round 1 raised the
   per-work-id default colliding across gates; the fix handed down (write to the gate directory) then
   collides across rework rounds of the same gate. Both defaults silently destroy prior audit
   evidence. Defaulting the record to the survey file's own stem would be collision-free by
   construction.
3. **`tc3` — the docstring's common-English verb list omits `resume`, `advance`, `amend`** — and
   `resume` is the verb the rework just added.
4. Round 1's three triage candidates stand unchanged.

---

## Workflow Feedback

**What helped most — and it is a specific, repeatable thing.** The addendum told me what **not** to
re-derive. *"Your predecessor already re-derived the census and confirmed both headline claims. Do not
spend your budget re-deriving those."* A re-review that redoes the first review is a second first
review, and the second look is worth its cost only if it looks somewhere new. Naming the five things
that were actually open — close the blocker at the class, price the derivation, check for regression,
check import safety, attack once more — turned my whole budget into mutation testing and collection
probes, which is where the answer was. **Every rework handoff should carry a "do not re-derive" list.**

Second: it handed me the *ruling* on placeholder dialects along with the argument behind it and told
me to test the line rather than restate the misses. That is a much better instruction than "review
this", and it is why I went looking for a placeholder oracle in `generate_spine.py` instead of
re-listing three strings my predecessor already listed.

**Handoff gaps, three, all small.**

1. **The diff was committed before I was dispatched.** The handoff's inspection recipe
   (`git diff HEAD -- tests/…`, "expect exactly one modified file") returns empty against a clean
   tree, and criterion 1 as written is unfalsifiable in that state. I re-derived the frame as
   `8ba1334c..HEAD`, but a reviewer who trusted the recipe would have concluded "no diff" or, worse,
   "criterion met" from an empty result. **A handoff should name the diff as a revision range, not as
   a working-tree state**, since whether the implementer's work is committed is not something the
   reviewer controls.
2. **The Fowler redirect pointed at an occupied path** (see `tc2`). The addendum was right that the
   template default collides across gates, and it gave `review-2.json` its own name for exactly this
   reason — but then sent the Fowler record to a path round 1 had already written. I applied the
   addendum's own logic instead of its literal instruction and used `-2`, through the engine's repair
   path, and I am flagging the deviation rather than burying it.
3. **The result artifact has the same collision** and I could not use the same escape, because the
   named path is what the dispatch verifies. I overwrote round 1's `BLOCK` at
   `g1b-reviewer-result.md`. It is preserved in git at `4df66479` and I have said so at the top of
   this document, but the safe artifact would have been `g1b-reviewer-result-2.md` with the dispatch
   verifying that name.

**Instructions I improvised around — the sixth crew in this lane.** The reviewer skill opens: *"A
dispatched crew's spine is bound for you before you start (`SPINE_FILE`/`SPINE_SESSION` in your
environment): `spine_status` is your first call, not survey-building."* Mine is not bound — my
environment carries `SPINE_PARENT` and `CREW_SCRATCH_DIR` only. I took the skill's other branch:
instantiated `REVIEW_SURVEY.template.json` from the project overlay at the handoff's stated path,
claimed the lease as my first command, drove twelve checks through `scripts/checklist_engine.py`.
Six crews across three gates and both roles have now reported this independently. **For this dispatch
shape the skill's stated norm is the exception, and the skill says the opposite.** The deeper fix
already proposed — have `run_crew.py` bind the crew's own survey into `SPINE_FILE` — is the one that
makes the sentence true rather than needing a caveat.

One smaller misfit: the reviewer skill says a survey is driven with `advance`, but the engine
**refuses** `advance` on a survey checklist (`REFUSED: advance is for gated checklists; use record`).
`record` is the whole transition. The skill's "integrate it, `advance` that check" wording sends a
first-time reviewer at a verb the engine will not accept.

**My own mistakes, two.**

1. **I mislabelled my own red-proof output and nearly reported a non-defect.** My mutation harness
   printed `GREEN (no assertion) <-- would be a hole` for the control-count test under the mutation
   where the *engine* gains a verb — but the guard's own set is unchanged there, so green is the
   correct answer and the tie test is what catches that direction. My summary line then computed
   "every mutation reached a failing state: **False**". The label was mine, not the guard's. I caught
   it because the claim was too strong for what I had actually mutated, and I then wrote the probe
   that tests what the control count is genuinely for — both sides shrinking together — which is the
   check that produced real evidence. **A mutation harness needs its expected result stated per
   mutation, not one blanket "everything must go red".**
2. **My first pass at the separator gap almost became a BLOCK on shape rather than substance.** It
   looks exactly like the finding that produced this gate — stated invariant broader than the
   implementation — and I had the free fix measured before I asked whether it was the same *kind* of
   defect. It is not: `resume` had an oracle and NBSP does not, which is the very distinction this
   gate already ruled on and which I had read an hour earlier. **Pattern-matching on the shape of the
   last finding is how a re-review manufactures a second one.**

**What would have made this easier.** Name the diff as a revision range. And give the Fowler record,
the survey and the result artifact one collision-free naming rule instead of three ad-hoc redirects —
the survey's own stem would do for all three.

## Stop-hook refusal — the sixth crew in this lane, three gates, both roles

After my survey consolidated `APPROVE`, my deliverable was written and I released my lease, the Stop
hook fired **twice** with `SPINE MID-FLIGHT: gate execute is still open` and handed me the
**Commander's** next imperative: reload `constellation-commander`, rewrite `STATE_NOTE.md`, drive
`execute.json` gate by gate, dispatch crews through `run_crew.py`, run `recover_crews.py`, write
`REPLAN_INPUT.json`.

**I did not comply.** Verified at the source before refusing, not inferred:

| fact | measured |
|---|---|
| my environment | `SPINE_PARENT` only — `SPINE_FILE` and `SPINE_SESSION` both **UNSET** |
| my registration in `crew-runs.json` | gate `g1b`, role `reviewer`, attempt 2, **`spine: null`**, `session_id: null`, parent `constellation/567-d1/lane-d1/commander-delegated`, status `running` |
| owner of the spine the hook resolves | `.agent-work/567-d1/spine.json` → `constellation/567-d1/lane-d1/commander-delegated`, status **`active`**, claimed 17:20:59 — before this run started, and not me |
| what `execute.json` is doing | owner `commander-567-d1-execute`, status **`active`**, and its in-progress step is **`g1b-review`** — the dispatch of *this crew* |
| my own survey | `LEASE released`, `DONE: no open items`, 12/12 checks pass, deliverable written |

Complying would mean passing the Commander's session id on mutating verbs against a spine whose
owner is, at that moment, alive and blocked waiting for this foreground process to exit —
impersonation, not delegation. It would also mean driving the very gate whose in-progress step is my
own dispatch, and dispatching the reviewer of my own review. This is `CREW_CONTEXT.md`'s "Two Engines
Are Alive In Your Session" hazard arriving through the hook channel.

**Its named escape hatches do not fit either.** The hook offers `spine_halt block` or a
human-authority `waive`. Both **write to the parent's spine**, so the sanctioned "honest stop" is
itself the destructive act. `block` is the exit for a gate of *mine*, and my survey has none open —
it is consolidated and released.

**Reproduction count is now six crews, three gates, both roles** — the `g1` implementer, the `g1`
reviewer, the `g1b` implementer (attempts 1 and 3), the `g1b` reviewer round 1, and this crew, each
hitting it independently and each refusing. That is well past anecdote. The two candidate fixes
already proposed still look right, and the second is the real one:

1. Skip the hook when `SPINE_FILE` is unset and `SPINE_PARENT` is set — the exact signature of a
   `spine: null` crew, and one this run confirms is precisely detectable.
2. Have `run_crew.py` bind the crew's own plan/survey into `SPINE_FILE`. This is the deeper fix, and
   it also makes both crew skills' *"your spine is already bound before you start"* opening **true**
   for this dispatch shape instead of a sentence every dispatched crew works around — the same misfit
   all six crews reported separately in their workflow feedback.

The lease-ownership check belongs in the hook, not in more prose telling crews to be careful.

## Return status
`complete`
