# Implementer Handoff — g3 REWORK (attempt 2)

Issue #467 (epic #418), branch `epic-418/a2-467-trip-semantics`, worktree
`C:/Programs/constellation-skills-wt/epic418-a2-467`. Work only in this worktree, absolute paths.

## Why you are here

Gate `g3` was implemented, then independently reviewed, and the review returned **BLOCK with one
blocking finding**. This is a **narrow rework of that one finding**. Everything else in g3 passed —
eight of nine close criteria, verified by attack rather than by reading. **Do not re-do g3.**

The full review is at
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-reviewer-result.md` (finding **B-1**).

## The finding, and it is confirmed

The g3 mutation log declares mutation **M15 an EQUIVALENT mutant** — that no test can kill it
because the gate being advanced is always the active gate. **That declaration is false.** Its
reasoning enumerates `start` and `advance` but never `block()`, which carries **no status guard**,
and `blocked` is **not** in `TERMINAL` (`checklist_engine.py:63`). So `active_id()` can move
**backwards**, behind a later gate that is already `in-progress`.

**The commander reproduced this independently, with public verbs only, at the CLI.** Fixture: two
gates, `g2` carrying `context_headroom_tokens: 50000`, gauge on `claude-opus-5` (1M window; default
hard 15%, `g2`'s overridden hard 10%).

```
start g1  ->  g1 -> in-progress
advance g1 --why "..."  ->  g1 -> complete
start g2  ->  g2 -> in-progress
# gauge fill_fraction 0.02 -> 0.12 while g2 is under way
block g1 --blocker "upstream authority" --authority human --next "wait"
   ->  g1 -> blocked

statuses: {'g1': 'blocked', 'g2': 'in-progress'}
current -> ACTIVE g1 [blocked]      # active_id is g1; the gate being CLOSED is g2
```

**Shipped engine**, closing `g2` silently:

```
$ python scripts/checklist_engine.py --file m15.json advance g2 --mechanical
REFUSED: g2: context is at/over the hard limit, so this gate cannot be closed silently — a
mechanical or why-less close records no understanding, and the next agent would cold-start from a
digest written before your work. Closing the gate is NOT refused; only the silence is.
Run: advance g2 --why "<understanding>"
```

**M15 mutant** — drop the gate argument at `checklist_engine.py:2857-2858`, i.e.
`require_why=_trip_hard_band_reading(cl, base_dir)` — identical fixture, identical fill:

```
$ python <mutant> --file m15.json advance g2 --mechanical
g2 -> complete
```

**Consequence:** the `getattr(args, "id", None)` argument that g3 itself added at `:2857` has **zero
test coverage**, and removing it **silently disables this issue's own no-silent-close guarantee for
the gate being closed**, in a state the engine sanctions.

**The shipped source code is CORRECT.** It behaves exactly as intended. What is missing is the test.

## Task

Two things. No source change.

1. **Add one test** that reaches the state above **through public verbs** and asserts that closing
   the overridden gate silently is refused while a *later-blocked earlier gate* is `active_id`.
   It must go **RED under the M15 mutation** and **GREEN on the shipped code**. Give it a name that
   says what it guards.
2. **Correct the M15 entry** in `.agent-work/issue-467-trip-semantics/g3-mutation-log.md`: replace
   the `EQUIVALENT` declaration with the kill — the named test, the total failure count, and a
   sentence noting the correction, since `f9925be6`'s commit message also asserts the equivalence
   claim ("1 declared EQUIVALENT rather than faked"). The log is an audit record; the correction
   belongs in it, visibly, rather than the entry being quietly rewritten as if it had always said
   this.

## Test mode

**TDD.** Write the test, run it against the **mutant** first and observe it RED, then against the
shipped code and observe it GREEN. Paste both. A test that has only ever been seen green proves
nothing here — that is the exact failure class this whole gate is about.

## Allowed Scope

- `tests/test_checklist_engine.py` — the new test.
- `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — the M15 entry.
- Your own crew plan under `.agent-work/issue-467-trip-semantics/crew-plans/`.

## Specific Exclusions — read these, the temptation is real

- **Do NOT change `scripts/checklist_engine.py` or `scripts/gauge_reader.py`.** The shipped code is
  correct. This is a missing test, not a bug.
- **Do NOT "fix" `block()`** so it refuses a `complete` gate, and do not add `blocked` to `TERMINAL`.
  That `block()` accepts a complete gate is **pre-existing behaviour, outside this gate's scope**,
  and the reviewer already filed it as an observation. Changing it would also destroy the very state
  your new test needs to reach.
- **Do NOT touch anything else in g3** — the resolver, the clamps, `_PROFILES`, the spine template,
  the other fifteen mutations. They passed review.
- **Do NOT re-run the whole g3 mutation battery.** M15 is the only open one.
- Do not touch `.agent-work/issue-467-trip-semantics/execute.json`, `spine.json`, or
  `STATE_NOTE.md` — the Commander holds their lease.

## Close Criteria

1. The new test exists in `tests/test_checklist_engine.py`, reaches the state through public verbs,
   and asserts the silent close is refused.
2. It is **RED under the M15 mutation** — pasted output, with the failure count.
3. It is **GREEN on the shipped code** — pasted output.
4. The M15 log entry states the kill, names the test, gives the total, and notes the correction
   against the earlier `EQUIVALENT` claim.
5. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py tests/test_init_work_area.py tests/test_install_constellation.py` passes.
6. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'` passes and collects (pytest exits 5 on an empty collection).
7. `git diff --stat` shows **no change under `scripts/`**.

## A practical note on the fixture

The gauge file is read as a **sibling of the checklist file**, and a reading is discarded when it is
**stale (>30 min) or dated in the future**. A hand-written `observed_at` that is even slightly ahead
of the wall clock is silently treated as clock skew and collapses to `None`, which makes the whole
scenario read as "no gauge" and the test vacuously green. The existing
`GateHeadroomOverrideTripTests` already solve this by patching `_read_gauge` — prefer that path over
writing timestamps by hand, and if you do go through the file, generate `observed_at` from the
clock rather than typing it.

## Suggested Model Tier

**Sonnet.** Standing default for implementers on this run. No named Opus reason applies: the target
is demonstrated, the reproduction is handed to you verbatim, and the scope is one test plus one log
entry — mechanical execution against a proven target.

## Deliverable Path Check

Both **Committed**; `git check-ignore` exits 1 for each (`.agent-work/` is tracked in this repo).

- `tests/test_checklist_engine.py` — Committed, existing.
- `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — Committed, existing.

## Stop Conditions

Stop and return without completing if: the shipped code turns out to be genuinely wrong (i.e. you
find a state where the silent close is *not* refused when it should be) — that is a different and
larger finding, and it is mine to route, not yours to fix. Also stop if killing M15 appears to
require a source change; say so rather than making one.

## Return Format

Return an `IMPLEMENTER_RESULT` to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-rework-implementer-result.md`, including: the
new test's name and body, the RED-under-mutation output, the GREEN-on-shipped output, the corrected
M15 log entry, the suite runs, `git diff --stat`, stop conditions hit, out-of-scope observations,
and workflow feedback.

**Deliver it via `SendMessage` to `commander-w4-467-f` before ending your turn.**
