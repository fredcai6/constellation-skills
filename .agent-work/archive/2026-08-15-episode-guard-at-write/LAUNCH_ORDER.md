# Launch Order: `episode-guard-at-write` — reject an instruction-shaped episode when it is written

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

## Mission

Three lanes on 2026-08-15 shipped closeout episode records that red the suite, and a **fourth full
dispatch** was spent doing nothing but rewording two of them. The lanes were not careless — they were
structurally unable to catch it.

Full evidence:
`/home/tommy/projects/constellation-skills/.agent-work/triage-candidates/closeout-episodes-are-written-after-the-suite-that-guards-them.md`
(untracked, **primary checkout** — your worktree does not contain it). **Read it in full first.**

## The structural defect

`tests/test_episode_observations.py::RealStoreTests` scans `episodes/` and fails the suite on a statement
that reads as an instruction rather than an observation. The full-suite check is a postcondition of an
**integrate** gate. Episode records are authored at **closeout** — strictly later.

**So a lane's own green can never have covered the episodes it had not yet written.** Both its report and
the Admiral's later re-measurement are honest and accurate; they simply describe different trees. The
failure then surfaces at the worst moment: after the lane archived, released its lease and pushed, when
the only remaining actor is the merging Admiral.

Warning the lane does not fix this — one lane carried an explicit warning and tripped it anyway — because
at the moment it writes the record, its verification step is already behind it.

## The change

**Validate at write time.** `scripts/apply_episode_delta.py` is the store's single write path, and it
already has a pure validation seam — `validate_delta` at `~:910`, with per-op `_validate_create` /
`_validate_amend_assertion` / `_validate_restate_assertion` and a shared
`_validate_assertion_payload`. Its documented contract is **validate-then-apply, all-or-nothing**: any
invalid op rejects the whole delta before anything is written.

Reject an instruction-shaped statement there, using the guard that already exists —
`scripts/verify_episode_observations.py`, which the test loads and whose `triggers_for(kind, statement)`
returns the hits for one statement. **Import the guard; do not reimplement its rules.** Two
implementations of this judgement would drift, and the drift would show up as a record that writes
cleanly and then reds the suite — the exact failure you are removing.

The error must be **actionable**: name the offending word, the kind, and why it tripped, so the author
can recast the sentence without going and reading the guard's source.

## Hazards to check before you build

- **`validate_delta` is documented pure — "no disk I/O, so a structurally-invalid delta is rejected
  before…"**. If `triggers_for` (or the guard's import, or its exception-list lookup) touches the
  filesystem, you cannot simply call it from inside that seam without breaking a stated invariant.
  **Establish this first.** If it does read from disk, say so and propose where the check belongs
  instead — an impure layer just outside `validate_delta` is a legitimate answer. **Do not silently make
  a pure function impure.**
- **The exception list.** The guard tolerates 11 grandfathered records. A write-time check must not
  reject an *amendment* to one of those, or it becomes impossible to edit a grandfathered record at all.
  Work out what the right behavior is and say what you chose.
- **Scope of kinds.** The imperative rule is scoped to `workaround` and `proposed-remedy`; the
  second-person rule is not. Mirror the guard exactly — via the guard — rather than restating the scoping.

## Explicitly OUT of scope

- **Changing the guard's rules or its exception list.** `tests/test_episode_observations.py` and
  `scripts/verify_episode_observations.py`'s rule set are **not yours**. You are moving *when* the
  judgement happens, not *what* it judges.
- **Changing gate order** so closeout precedes the verifying check. Larger blast radius; the triage doc
  lists it and does not recommend it.
- **Retro-fixing existing records.** Every episode currently in `episodes/` passes today. Leave them.

## A known guard subtlety, so it does not surprise you

A verbatim quotation in **single** quotes that itself contains an apostrophe (`you're`) breaks the guard's
quote-pairing lookahead, unpairs the span, and leaks a second-person hit from inside legitimately quoted
machine output. Established by measurement against `triggers_for()` earlier today. Relevant if your tests
quote real output — and relevant to your **own** closeout episodes: use double quotes for quoted machine
output.

## Evidence required

- **RED before, GREEN after**, over behavior: a delta carrying a `workaround` statement that opens a
  clause with a bare verb is **rejected by `apply_episode_delta.py`**, and was accepted before your
  change. Drive the real script — this defect is about the real write path.
- A **control**: a well-formed observation-shaped statement still writes successfully. The check must not
  become a blanket refusal.
- A test that the rejection message names the offending word.
- Whatever you conclude about the purity hazard, demonstrated rather than asserted.
- Full clean-env cache-clean suite: **0 failed.** Baseline `main` at `2c46cab8` is **3031 passed,
  6 skipped, 1136 subtests** from inside a worktree.
- Regenerate the map: `python -m scripts.code_map build --root .`; commit if it moves.

## File Ownership

**Yours:** `scripts/apply_episode_delta.py` and its tests, your work area. Read `verify_episode_observations.py`
freely; **do not modify it.**

**NOT yours:** `tests/test_episode_observations.py`, `scripts/verify_episode_observations.py`,
`scripts/hooks/spine_rail.py` and `.claude/settings.json` (a sibling lane `stop-hook-door-binding` is live
in those), `scripts/checklist_engine.py`, `scripts/run_crew.py`, `.mcp.json`, existing `episodes/` records,
and `.worktrees/stop-hook-door-binding/`.

## Do not park — run this as your first action

Your process exits when your turn ends; nothing wakes it. The suite auto-backgrounds at ~120s, and
`checklist_engine.py advance` re-runs it during postcondition verification, backgrounding the same way.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write
rm -f /tmp/egaw-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/egaw-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/egaw-suite.log; do sleep 15; done
tail -20 /tmp/egaw-suite.log
```

If something backgrounds anyway, poll with `TaskOutput(block=true)` or `tail`. If you are about to write
"I'll resume when…", that sentence ends your run. **Do not dispatch a crew.**

## Your own closeout episodes

You are the lane fixing this, so your own records are the natural first test of it: past tense, describing
this run, not addressing a reader; no clause-opening bare verb in `workaround` / `proposed-remedy`; no
additions to the exception list. **If your own change rejects one of your own episode statements, that is
a success, not a problem** — recast the sentence and say so in your report.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write`, branch
`fix/episode-guard-at-write`, based on `main` at `2c46cab8`. Work area
`.agent-work/episode-guard-at-write/`.

`spine_status` must describe `episode-guard-at-write` — if not, stop and report.

## Stop Conditions

- Calling the guard from `validate_delta` would break its documented purity and no clean alternative
  placement exists.
- The check cannot be added without making amendments to grandfathered records impossible.
- Green would require changing the guard's rules, its exception list, or existing episode records.
- Green would require touching anything in the not-yours list.

## Return Shape

What `spine_status` resolved to, named explicitly; where you put the check and why; the purity finding;
what you chose for grandfathered amendments; RED/GREEN and the control; clean-env suite counts; whether
the map moved; and whether your own episodes tripped your own check.

**You may push and open a PR. You are fenced from merging.** The Admiral merges.
