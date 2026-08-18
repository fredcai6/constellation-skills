# Reviewer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g1b-review` — Widen the guard: placeholder-agnostic command lines, and the tracked template
overlay: review.

## Task statement

`tests/test_cli_retirement_guard.py` is the regrowth guard that closes issue #559 (*"the door is
the interface, not a second path"*). The human's ruling it enforces, verbatim:

> **"the agents should not know about the CLI. period."**

Gate `g1` authored it and its review APPROVEd it. **This gate exists because that review found a
real hole and measured a whole surface no walk read.** The implementer just closed both. You are
reviewing that widening — and this gate exists at all because the last reviewer attacked the
pattern successfully, so **do the same thing again**.

The guard is deliberately **RED** and must stay red. `g2` does the sweep. Do not ask for green.

**Read first:** the diff (`git diff HEAD -- tests/test_cli_retirement_guard.py`), then
`.agent-work/567-d1/crew-handoffs/g1b-implementer-result.md`, then
`.agent-work/567-d1/crew-handoffs/g1-reviewer-result.md` §"The review's real work" (the attack that
produced this gate).

## How to inspect the diff

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
git status --porcelain -- skills specs docs scripts episodes tests map .agent-work/templates
git diff HEAD -- tests/test_cli_retirement_guard.py
```

Expect exactly one modified file. Everything else is untouched, including
`tests/test_mcp_adoption.py`, which is imported and must be byte-identical to `HEAD`.

## What changed

**(a) A fourth pattern, `ENGINE_STANDIN_COMMAND_RE`** — a placeholder-shaped stand-in (angle,
brace, `$VAR`, `%VAR%`) followed on the same line, separated by horizontal whitespace only, by an
engine verb from the file's existing `_ENGINE_VERBS`. This closes the route the `g1` review found:
a spine-template command line never contains the literal `checklist_engine.py`, so the whole class
rested on the single token `<engine>`, and `<cli> claim …`, `<engine-cli> advance …` and
`{{engine}} release …` all walked through clean.

**(b) The walk extended to `.agent-work/templates/**`** — the tracked overlay an agent in this repo
actually instantiates, previously read by no walk. Rooted *at* the overlay directory so this run's
own `.agent-work/567-d1/**` artifacts are never reachable rather than reached-and-filtered.

## Close criteria

1. Only `tests/test_cli_retirement_guard.py` is modified; `tests/test_mcp_adoption.py` is
   byte-identical to `HEAD`.
2. `pytest tests/test_cli_retirement_guard.py -q -k "not TestNoSecondPathReachesAnAgent"` **passes**.
3. `pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent` **fails**, and
   its output names at least one `.agent-work/templates/` site.
4. Exception list length is still **zero**; both pre-ruled survivors
   (`docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59`,
   `scripts/init_work_area.py:24`) are still out **by the walk rule alone**, named nowhere.
5. The vacuity floors cover the new surface and the raised text count.

## The review's real work

Close criteria 1–5 are cheap. Three things are not.

### 1. Attack the widened pattern — again

The last review's attack is why this gate exists. Repeat it against the new pattern. Write
plausible regrowth — the text a future agent restoring this doctrine would actually write — and
report every miss with the exact string.

Directions worth trying, not a closed list: a stand-in with the verb on the **next** line; a
stand-in separated by something other than a space; a verb not in `_ENGINE_VERBS`; a command
introduced by a word rather than a placeholder; a clause split across a JSON string boundary; a
stand-in shape none of the five alternatives covers.

As before, a miss is **not** automatically a BLOCK. The docstring declares what the guard
deliberately does not enforce. Judge whether a miss falls inside a declared limit (report it as an
observation) or defeats the guard's stated purpose (that is a finding).

### 2. Judge the width — in BOTH directions, and this is the load-bearing one

The implementer made two width decisions and claims both were settled by measurement, not argument.
**Re-measure both yourself.**

- **The stand-in is not required to spell `engine` or `cli`.** The narrow version catches all three
  verified misses and costs zero on this tree; it was rejected because it rebuilds the same defect
  one level up (`<script> claim --session-id <id>` would walk through). Is that reasoning right, and
  is the wider form's measured cost really zero?
- **The separator is horizontal whitespace with nothing between.** The claim is that loosening
  `[ \t]` to `\s` costs one false alarm at `skills/workbench/references/checklist-engine.md:92`
  (a usage block where `<id>` ends one line and an engine verb opens the next), and that allowing a
  trailing backtick fires on three honest prose shapes. Both loosenings are pinned as must-not-match.
  Verify the `\s` false alarm exists where claimed.

**The bar to judge against is in this repo, measured.** Read
`tests/test_mcp_adoption.py:1268`, `TestCLIStaysAvailableNotDeprecated`'s docstring. It records why
that suite **deleted** its own polarity predicates: their errors were not symmetric across authors,
5 of 6 planted honest affirmatives fired them, *"a check that punishes the people doing the right
thing is deleted by the next person who trips it — after which there is no check at all."* A guard
widened past that line is worse than no widening.

The implementer's headline claim is **"false-alarm rate on honest text: 0/3098"** and
**"the widening adds zero new addresses."** Re-derive both. If the number is right, say so; if it is
wrong, that is the finding of this gate.

### 3. Verify the overlay walk's scope rule

- Confirm `.agent-work/567-d1/**` — this run's own launch order, notes, handoffs and crew results,
  which quote the clause constantly — is genuinely **not** in the walk, and confirm *why*: the rglob
  is rooted at the overlay, so there is no sibling to exclude and the exception list stays at zero.
- Confirm no lane-D2 file enters the walk through the overlay. The implementer measured every file
  under `.agent-work/templates/.baseline/constellation-workbench/` as clean of all four patterns.
  Re-run that yourself: if it is wrong, this widening created a fenced-file dependency.
- The implementer reports a census discrepancy against its own handoff: the overlay holds **16**
  `<engine>` occurrences across **10** files once the `.baseline/` mirrors are counted, not the 7
  across 5 the handoff stated. **Verify this**, because `g2` depends on it — a sweep of the five
  visible copies that misses the mirrors leaves this guard red.

## Constraints on you

1. **Re-run every verification command yourself and read the exit code.** A pasted summary is a
   pointer to evidence, never the evidence.
2. **Do not edit anything.** Report findings.
3. Do **not** ask for the guard to be made green, and do **not** propose an exception list.
4. The guard walking `skills/workbench/**` is **known and expected** — lane D2 owns and deletes
   those files, this lane merges last, and `g5-final` re-runs the guard on the rebased tree. Not a
   defect.
5. **Author any shell you hand back in POSIX form.** The engine runs `command` checks through
   `/bin/sh`, which is `dash` on this host, and `set -o pipefail` is rejected outright with exit 2 —
   this gate's own handoff shipped that bug and the implementer had to correct it through the
   engine. Do not reproduce it.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q                              # expect 15
python3 -m pytest tests/test_cli_retirement_guard.py -q -k "not TestNoSecondPathReachesAnAgent"     # MUST pass (11)
python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent           # MUST fail (4)
python3 -m pytest tests/test_mcp_adoption.py -q                                                     # expect 183 passed, 2 skipped
git diff --quiet HEAD -- tests/test_mcp_adoption.py && echo untouched
```

The gate's own closing check, which the Commander has already re-run independently under `dash`
(exit 0):

```sh
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent' >/dev/null 2>&1 \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent > /tmp/g1b-guard.log 2>&1 \
  && grep -q '.agent-work/templates/' /tmp/g1b-guard.log
```

## Map anchors (inbound)

No architecture map exists in this repo (`map_orient` → `DEGRADED-UNPARSEABLE`). Entry points:

- `tests/test_cli_retirement_guard.py` — the guard; `_ENGINE_STANDIN`, `ENGINE_STANDIN_COMMAND_RE`,
  `_walk_dir`, `OVERLAY_FILES`, `TestTheWalkIsNotVacuous`, `TestTheInvocationPredicateItself`,
  `TestTheStandInCommandPredicateItself`.
- **`tests/test_mcp_adoption.py:1268`** — `TestCLIStaysAvailableNotDeprecated`. The repo's own
  measured argument for why an over-eager predicate is worse than a stated residual. **This is the
  bar for §2 and you should read it before judging the width.**
- `tests/test_mcp_adoption.py:838` — `TestTier2SpineAlreadyBoundForDispatchedCrews`, the two-file
  in-tree precedent this guard generalizes.
- `.agent-work/567-d1/crew-handoffs/g1-reviewer-result.md` — the attack that produced this gate.
- `.agent-work/567-d1/notes-1.md` — the measured baseline and the second-checklist probe.

## Evidence produced by the implementer

Each figure below is the implementer's; **re-derive rather than accept**. Where a number is quoted
here, the command that produced it is named, so a mismatch is traceable.

- `pytest tests/test_cli_retirement_guard.py --collect-only -q` → 15 collected.
- `pytest … -k 'not TestNoSecondPathReachesAnAgent'` → 11 passed, 4 deselected, exit 0.
- `pytest … -k TestNoSecondPathReachesAnAgent` → 4 failed, 11 deselected, exit 1; 58 output lines
  address `.agent-work/templates/`.
- `pytest tests/test_mcp_adoption.py -q` → 183 passed, 2 skipped, exit 0.
- Census in every failure message: `scanned 3098 texts across 216 files (101 under skills/, 2 under
  specs/, 113 under .agent-work/templates/)`.
- Floors: ≥60 skills files, ≥1 spec file, ≥60 overlay files, ≥1800 texts, plus a new
  no-strays-under-`.agent-work/` assertion.
- Whole suite: `6 failed, 3362 passed, 5 skipped, 1219 subtests passed`. Four failures are this
  guard by design; the implementer claims the other two are pre-existing and proved it by stashing.
  **Re-prove that yourself** — one of them
  (`test_crew_launcher.py::ScratchDirResumeTests::…scratch_dir_unbound`) is claimed to fail only
  when the suite runs *inside a dispatched crew*, which is what you are.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: the guard does not collect; it fails for a reason other than the corpus; the
widened pattern red-lights honest text and the implementer's zero-cost claim does not hold; or
reviewing it would require editing a file another lane owns.

## Return format

Write the full `REVIEW_RESULT` to
`.agent-work/567-d1/crew-handoffs/g1b-reviewer-result.md` **before ending your turn** — that write
is the delivery. Include a `Verdict` field whose value is exactly `APPROVE` or `BLOCK` (uppercase).
Include a `Workflow Feedback` section: what helped, what got in the way, and your own mistakes.

Survey state location: `.agent-work/567-d1/g1b-review/review.json`.

---

# REWORK ADDENDUM — read this first, then the document above

Your predecessor reviewed this gate and returned **BLOCK**, correctly. Its result is at
`.agent-work/567-d1/crew-handoffs/g1b-reviewer-result.md` — **read it before anything else**, and do
not re-derive what it already established. Everything above still governs except where this
addendum overrides it.

## What it found, and what changed

**The blocker.** `_ENGINE_VERBS` enumerated 17 verbs where `checklist_engine.py`'s argparse defines
18 — `resume` was missing — so `Second path: <cli> resume g1 --reason 'unblocked'.` passed all four
patterns clean. It proved the verb set against the engine's own `--help`, not against a document, and
it named the standard that was broken: `CREW_CONTEXT.md` §Verification Discipline, *"define a guard
by its consumer's behaviour, not by a hand-maintained list … the gap is silent."*

**The Commander ruled for the durable fix, not the one-token one.** Your predecessor proposed adding
`resume` now and deriving from the engine later, as an above-latitude change. That reading was wrong
in one respect and the ruling says so: `tests/test_mcp_adoption.py:204` already defines
`_engine_verbs()`, which reads the engine's argparse, and this guard already imports three names from
that module — so there is no new import direction and no new machinery.

**What the reworked diff does:**

1. `_ENGINE_VERBS` is built from `_engine_verbs()`, sorted, with each verb `re.escape`d.
2. `TestTheVerbSetIsTheEnginesOwn` pins the tie in the assertion path, and — going past what was
   asked — recovers the verb set from the **compiled alternation** rather than from whatever produced
   it, so the tie still holds if a later author swaps the derivation for a literal that agrees today.
3. `"Second path: <cli> resume g1 --reason 'unblocked'."` is pinned as a regression fixture.
4. The docstring's code-span safety argument is scoped to Markdown, and the census unit is stated.

**Deliberately not done, and this is a ruling you should test rather than re-litigate:** the three
placeholder dialects your predecessor found free (`[engine]`, `__ENGINE__`, `$(engine)`) are left as
a stated residual. Its own distinction is the reason and the Commander upheld it — **`resume` has an
oracle** (`parse_args` says what the verb set is, so its absence is drift), **placeholder dialects
have none**. If you think that line is drawn wrong, say so as a finding with the argument; do not
simply restate the misses.

## What this review is for

**It is a re-review of a reworked gate, not a fresh one.** Your predecessor already re-derived the
census independently and confirmed both headline claims (zero new addresses; 0/3098 false alarms on
honest text). **Do not spend your budget re-deriving those.** Spend it on:

1. **Does the rework actually close the blocker at the class?** Confirm the verb set is the engine's
   own — check it against `scripts/checklist_engine.py --help` yourself — and that the tie assertion
   would genuinely fail on a drift. Red-proof it: make the two disagree in memory and confirm the test
   goes red and names the difference.
2. **Did the derivation cost anything?** Measure the delta from adding `resume` over the whole walk.
   Your predecessor measured it as zero before the change; confirm it after.
3. **Did the rework break anything the previous review passed?** The four floors, the zero-length
   exception list, both pre-ruled survivors out structurally, the `PROSE_ONLY` discriminations, the
   overlay scope rule.
4. **Is the import safe at collection time?** `_engine_verbs()` now runs at module import. Confirm it
   needs no `SPINE_FILE`/`SPINE_ENGINE`, does not mutate global state that a later test depends on,
   and that the guard still collects cleanly — a guard that dies at collection is a guard that never
   runs.
5. **Attack it once more**, briefly. The verb arm is now wider by one; anything new get through?

## Two things your predecessor learned the hard way — do not re-pay them

1. **Do not run the whole suite while driving your own survey through the engine.**
   `tests/test_gauge_chain_writer_to_trip.py:604` snapshots size and mtime of every file under the
   repo's `.agent-work/` and asserts nothing moved. Your predecessor measured 7 failures with
   concurrent records and 6 when quiet, and the 7th was its own write. **This gate does not need a
   whole-suite run at all** — `g5-final` owns that, in a clean detached worktree.
2. **Write your Fowler record to `.agent-work/567-d1/g1b-review/FOWLER_PASS.json`**, not the
   template's work-id-root default. That default path already holds the `g1` review's record, and
   writing there destroys another gate's audit evidence.

## Verdict expectations

`APPROVE` if the blocker is genuinely closed and nothing regressed. `BLOCK` again if it is not —
this gate has already shown that a second look is worth its cost, and a rework that half-closes a
finding is worse than one that fails loudly. Rework budget is 1 of 3 used.

Survey state location: `.agent-work/567-d1/g1b-review/review-2.json` — a **new** file, so the
previous round's consolidated survey is preserved as the audit record of the BLOCK.
