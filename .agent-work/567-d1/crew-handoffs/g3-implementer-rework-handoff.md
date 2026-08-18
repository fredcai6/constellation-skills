# Implementer Handoff — REWORK

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g3-implement`, **reopened after a BLOCK** (rework 1/3). The original handoff is
`.agent-work/567-d1/crew-handoffs/g3-implementer-handoff.md` and still governs everything this
document does not change. **Your predecessor's work is in the tree and is good** — read
`.agent-work/567-d1/crew-handoffs/g3-implementer-result.md` and
`.agent-work/567-d1/crew-handoffs/g3-reviewer-result.md` before touching anything.

**This is a one-clause fix in two files.** Everything else in the diff was measured true and stays.

## What the reviewer confirmed — do not change any of it

It re-measured in **three fresh processes with explicit paths**, with a positive control:

- **The rebind refusal is real**, quoted verbatim by both specs, and total (`spine_status` still
  showed the first spine afterwards).
- **It is conditioned on holding your own lease and nothing else** — the identical `spine_bind` call
  *succeeds* after releasing. So the prose's stated reason is the actual reason, not a coincidence.
- **An unbound door binds and drives fine**, with the session identity derived from the spine's own
  `work_id`. No role is stranded.
- **Your predecessor was right to refuse my handoff's premise.** My handoff asserted that a
  dispatched crew "cannot" use the door and that every crew in this lane drove its plan under a
  hand-supplied CLI session id. That is **wrong for the dispatched-crew case** — a crew dispatched
  with no `--spine` has an *unbound* door, so it can bind its own plan. Your predecessor measured
  that first-hand and did not repeat my error; the reviewer reproduced the correction independently,
  and was itself the live case. **The shipped prose is right here and must stay right.**

## The blocker — one clause, false as stated

Both specs assert:

> …the escape that refusal names is barred for you, because **the archive gate requires the lease to
> cover every journaled action**, so releasing it to reach a second checklist **fails your own
> closeout**.

Measured, and I re-verified each point myself before sending this:

| # | The claim | What is actually there |
|---|---|---|
| 1 | "the archive gate requires this" | The phrase **"archive gate" appears nowhere in `skills/`**. The Commander spine's `archive` gate has one lease postcondition, `c3` *"engine session lease released"*, with **`check: null`** — a qualitative attest, silent on journal coverage. Its others are episode-captured, branch/PR, and git-change-policy. None reads a journal. |
| 2 | "…so releasing fails closeout" | `scripts/spine_lifecycle.py` refuses in the **opposite** direction: *"close refused: the lease is still active"*. Release is what closeout **wants**. |
| 3 | "the lease must cover every journaled action" | **Real** — but it lives in the role skills' own prose as the **"terminal provenance check"**, and is mechanically enforced only by `evals/euler-*/checks/spine_completed.py::journal_consistent`, which nothing in the live path calls. |
| 4 | "your own closeout" | **Neither crew plan template has a closeout gate at all.** `IMPLEMENTER_PLAN.template.json` is `['m0-context','m1']`; `REVIEW_SURVEY.template.json` is `['r0-context'…'r6-fowler']`. The role being told its closeout will fail has no closeout. |

**Where it came from:** `skills/reviewer/SKILL.md:17` and `skills/implementer/SKILL.md:17` both say
*"fails the **terminal provenance check** — the lease must cover every journaled action"*, which is
accurate. The clause renamed a correctly-named check into a differently-named, real gate that does
not do this.

**Why it blocks rather than rides as an observation.** It sits inside a sentence that advertises
itself as *"a measured refusal rather than an oversight"*, in the two files that are now the corpus's
statement of what the door is for a role. The whole point of stating the reason is so a future author
cannot "fix" the rule — but a future author who checks *this* reason finds no archive gate in their
own plan and is entitled to discount the entire paragraph. `CREW_CONTEXT`'s *"assert against
behaviour, never against text that describes it"* is the standard missed.

## What to do

**Replace that one clause, in both files, with something true.** Two things to get right:

1. **Use the inherited name**: the **terminal provenance check**, worded as
   `skills/{reviewer,implementer}/SKILL.md:17` word it — *the lease must cover every journaled
   action*. Do not invent a third name for it.
2. **Scope the claim to the role that actually has a closeout.** A Commander or Admiral driving its
   own spine has one and is genuinely barred. A dispatched crew has no closeout gate, so "your own
   closeout fails" is not the reason it should not release-and-rebind. Say what is true for the
   reader of *that* file. If the honest answer for a crew plan is that the release-and-rebind escape
   simply does not arise — because a dispatched crew's door is **unbound**, so it binds its own plan
   directly and never holds a competing lease — then say that, and the paragraph gets shorter and
   truer.

**Prefer accuracy over completeness.** A shorter paragraph that survives being checked beats a fuller
one that does not. If part of the reasoning turns out to apply to no reader of these two files, cut
it rather than hedging it.

**The paragraph is duplicated near-verbatim across both specs**, so the repair must land in **both**,
identically. The reviewer flagged that duplication as its own observation; if you can state the fact
once in a way both files can carry without divergence, say so, but do not restructure the specs to
achieve it.

## Close criteria

The original six still hold, plus:

7. No claim in either spec names a gate, check or file that does not exist or does not do what the
   claim says. **Verify each factual assertion you leave in place**, not just the one you fixed.
8. Both files still parse as TOML, and the guard still reports no violation at any `specs/` address.

## Allowed scope

`specs/**`. Nothing else.

## Constraints

1. **Do not promise a door path the measurement shows does not exist** — and equally, do not deny one
   that does. Your predecessor's dispatched-crew correction is right; keep it.
2. **Your prose is inside the guard's walk** — it may name the engine as a component, never show the
   command.
3. Do not edit `tests/test_cli_retirement_guard.py`, `skills/**`, `scripts/**`, `episodes/**`,
   `docs/**`, or `map/INDEX.md`.
4. File no issues; stage candidates under `.agent-work/567-d1/triage-candidates/`.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -c "import tomllib;[tomllib.load(open(p,'rb')) for p in ['specs/implementer.spine.toml','specs/reviewer.spine.toml']];print('toml ok')"
grep -rn 'archive gate' specs/ skills/        # expect nothing
python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g3.log 2>&1
grep -oE '^E +(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g3.log | sed 's/^E *//' \
  | grep -v '^skills/workbench/' | sort -u    # expect nothing
git status --porcelain
```

**POSIX form only** — the engine runs `command` checks through `/bin/sh`, which is `dash` here, and
`set -o pipefail` is rejected with exit 2. **Do not run the whole suite while driving your own plan
through the engine**: `tests/test_gauge_chain_writer_to_trip.py:604` snapshots every file under the
repo's `.agent-work/` and asserts nothing moved, so your own engine records produce a failure that is
yours.

## Required evidence

- The before and after text of the clause, in both files, quoted.
- For every **remaining** factual assertion in the new prose: the file, symbol or measurement that
  makes it true. This is the one the gate turns on now — the BLOCK was not that the prose was
  careless, it was that one claim had no measurement behind it while sitting in a sentence that
  advertised one.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1). Reopened
through the engine, rework 1/3, reason recorded in the journal.

## Stop conditions

Stop and return if: no true statement covers both files' readers without splitting the paragraph; or
a remaining assertion turns out to be unverifiable, in which case say which and propose cutting it.

## Return format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d1/crew-handoffs/g3-implementer-rework-result.md` **before ending your turn** — that
write is the delivery. Include a `Return status` field whose value is exactly `complete` (lowercase)
when the close criteria are met. Include a `Workflow Feedback` section.
