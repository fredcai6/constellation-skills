# Implementer Handoff — REWORK

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g1b-implement`, **reopened after a BLOCK** (rework 1/3). The original handoff is
`.agent-work/567-d1/crew-handoffs/g1b-implementer-handoff.md` and still governs everything this
document does not change. The prior attempt's work is **already in the tree and is good** — read
`.agent-work/567-d1/crew-handoffs/g1b-implementer-result.md` before you touch anything.

**This is a small, precisely-bounded rework.** The reviewer confirmed both of the widening's
headline claims by independent re-derivation and found the diff otherwise sound. One thing is wrong.

## The blocker

**`_ENGINE_VERBS` in `tests/test_cli_retirement_guard.py` enumerates 17 verbs. The engine defines 18.
`resume` is missing.** So this line passes **all four** patterns clean:

```
Second path: <cli> resume g1 --reason 'unblocked'.
```

That is exactly the class gate `g1b` was opened to close — a stood-in-for engine command line in a
spine template, written with a verb the engine really has — and it is inside none of the docstring's
declared limits.

Proven against the engine itself:

```
$ python3 scripts/checklist_engine.py --help
usage: checklist_engine.py [-h] --file FILE [--dry-run]
      {current,claim,heartbeat,release,start,advance,record,consolidate,skip,block,
       resume,reopen,append,amend,attest,waive,attach,flag-candidate}
```

The gap is also **doubled by this diff**, not merely inherited: the same string feeds both
`ENGINE_INVOCATION_RE` and the new `ENGINE_STANDIN_COMMAND_RE`.

And it breaks a documented repo standard verbatim — `docs/agents/CREW_CONTEXT.md`, §Verification
Discipline:

> **Define a guard by its consumer's behaviour, not by a hand-maintained list.** A list of
> characters, filenames or call sites drifts from the predicate the code actually applies, and the
> gap is silent.

The list drifted on day one.

## What to do — take the durable fix, not the one-token one

The reviewer proposed adding `resume` as this gate's fix and deriving the set from the engine as a
separate, later, above-latitude change. **The Commander's ruling: do the durable fix now.** It is not
above latitude, because the oracle and the import direction already exist in this repo:

`tests/test_mcp_adoption.py:204` defines `_engine_verbs()`, which reads the engine's **own argparse
subparsers** by handing it a bogus verb and reading the choices argparse prints — *"never
hand-typed"*, in its own words. It needs no `SPINE_FILE`/`SPINE_ENGINE` env.

You already import `INSTRUCTION_FILES`, `INSTRUCTION_SUFFIXES` and `_instruction_texts` from that
module. **Import `_engine_verbs` the same way and build `_ENGINE_VERBS` from it.** That is the same
generalize-an-in-tree-precedent move the whole guard is built on, it adds no new import direction,
and it removes the drift *class* rather than the `resume` *instance*.

Concretely, three things:

1. **Derive the verb alternation from `_engine_verbs()`** rather than the hand-typed string. Sort for
   determinism, and `re.escape` each verb so a future verb containing a regex metacharacter cannot
   silently break the pattern (`flag-candidate` already contains a hyphen).
2. **Pin the tie in the assertion path** — one assertion that the pattern's verb set equals the
   engine's, so the two can never drift again and the failure names the difference. Follow
   `test_mcp_adoption.py:263`'s `test_engine_has_all_eighteen_verbs_todays_pins_expect` as the
   control-count precedent: pin the **count** too, so both sides cannot shrink together unnoticed.
3. **Pin the blocker as a regression fixture** — add `"Second path: <cli> resume g1 --reason
   'unblocked'."` to `STAND_IN_COMMANDS`, so the specific miss the review found can never come back
   even if the derivation is later replaced.

**Measure the cost before you claim it.** The reviewer measured adding `resume` as **zero** new
addresses for both patterns over 3098 texts. Deriving all 18 should be the same, but the other 17
are already there so `resume` is the only delta — re-measure and report it rather than inheriting the
figure.

**Note the coupling, and say in your result that you accept it:** `g2` inverts
`tests/test_mcp_adoption.py`. If that gate deletes or renames `_engine_verbs`, this guard dies at
**collection**, which pytest reports as an error and never as a pass. That is the same loud-not-silent
dependency your last result already recorded for the other two imports, now one symbol wider. `g2`'s
constraints tell it to leave `TestTier3CLIOnlyVerbsStayCLI` and the verb-gap tests alone, which is
what uses `_engine_verbs` today.

## Two free improvements the reviewer asked for — take both

1. **Scope the code-span safety argument to Markdown.** The docstring rests the separator's safety
   case on *"a stand-in carrying its own closing backtick is a noun, not a program name."* The
   reviewer measured **40** corpus sites where a stand-in is followed by whitespace and an ordinary
   English word, and **zero of the 40 are code-spanned** — 13 of them sit inside JSON template
   imperatives, where backticks are not the house habit and the argument gives no protection at all.
   The measured 0/3098 is real, but what actually holds it at zero is that none of those 40 following
   words happens to be an engine verb — and several verbs (`record`, `block`, `append`, `start`,
   `current`, `release`) are common English. **Say that**, so a later author does not over-trust the
   code-span argument.
2. **State the census unit.** "16 tokens across 10 files" conflates two counts: 16 `<engine>`
   occurrences live in **6** files; **10** overlay files carry a sweep target of *some* kind. Write
   any census as "N occurrences of X across M files containing X". This exact unit slip has now
   occurred at three consecutive tiers in this lane, so phrase it so the next reader cannot repeat it.

## Not in scope for this rework — do not do these

- **Three placeholder dialects the reviewer found and did not demand**: `[engine]`, `__ENGINE__`,
  `$(engine)`. Their cost is also zero, but the reviewer's distinction is right and the Commander
  upholds it: **`resume` has an oracle** (`parse_args` says what the verb set is, so its absence is
  drift), while **placeholder dialects have none** — which dialects an author reaches for is a
  judgement call, and `test_mcp_adoption.py:1268` is this repo's own measured argument for treating
  those two situations differently. Leave them as a stated residual. If you think the docstring
  should name them explicitly as accepted residuals, that is fine and is the most it should do.
- Anything under `skills/`, `specs/`, `docs/`, `scripts/`, `episodes/`, `map/`, or
  `.agent-work/templates/`. **Nothing is swept in this gate.**
- `tests/test_mcp_adoption.py` — imported, never modified. `g2` inverts it.

## Close criteria

The original handoff's eight criteria still hold, plus:

9. `tests/test_cli_retirement_guard.py`'s verb set is **derived from the engine**, not hand-typed,
   and an assertion pins the tie so the two cannot drift.
10. `"Second path: <cli> resume g1 --reason 'unblocked'."` is caught, and pinned as a fixture.
11. The added verb's cost is measured over the whole walk and reported.
12. The docstring's code-span argument is scoped to Markdown, and the census unit is stated.

## Allowed scope

`tests/test_cli_retirement_guard.py`. Nothing else.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q
python3 -m pytest tests/test_cli_retirement_guard.py -q -k "not TestNoSecondPathReachesAnAgent"   # MUST pass
python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent          # MUST fail
python3 -m pytest tests/test_mcp_adoption.py -q                                                    # MUST stay green
git diff --quiet HEAD -- tests/test_mcp_adoption.py && echo untouched
git status --porcelain -- skills specs docs scripts episodes tests map .agent-work/templates
```

The gate's closing check, which the Commander re-runs independently, in **POSIX form** (the engine
runs `command` checks through `/bin/sh`, which is `dash` here, and `set -o pipefail` is rejected
outright with exit 2 — this lane already paid for that once):

```sh
python3 -m pytest tests/test_cli_retirement_guard.py -q -k 'not TestNoSecondPathReachesAnAgent' >/dev/null 2>&1 \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q -k TestNoSecondPathReachesAnAgent > /tmp/g1b-guard.log 2>&1 \
  && grep -q '.agent-work/templates/' /tmp/g1b-guard.log
```

**Do not run the whole suite while driving your own plan through the engine.**
`tests/test_gauge_chain_writer_to_trip.py:604` snapshots the size and mtime of every file under the
repo's `.agent-work/` and asserts it is unchanged, so your own engine records break its containment
window and produce a 7th failure that is yours. The g1b reviewer hit exactly this and nearly reported
it as someone else's defect. Run the suite quiet, or not at all — this gate does not need it.

## Required evidence

- The derivation, quoted, and the assertion that pins the tie to the engine's verb set.
- The `resume` line shown caught, with the pre-change proof that it was missed.
- The measured cost of the added verb over the whole walk.
- Confirmation the four floors, the zero-length exception list, and both pre-ruled survivors are
  unchanged.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1). Reopened
through the engine, rework 1/3, reason recorded in the journal.

## Stop conditions

Stop and return if: importing `_engine_verbs` proves unsafe at import time in this context (say why,
and fall back to adding `resume` to the hand-list plus the pinned fixture — that closes the blocker
and is an acceptable outcome); or the derivation red-lights honest text that the hand-list did not.

## Return format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d1/crew-handoffs/g1b-implementer-rework-result.md` **before ending your turn** —
that write is the delivery. Include a `Return status` field whose value is exactly `complete`
(lowercase) when the close criteria are met. Include a `Workflow Feedback` section.
