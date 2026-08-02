# notes-308 — issue #308, first collated consolidation AND retire the playbook

Sole writer: commander-308. Worktree `C:/Programs/constellation-skills-wt/e298-308`, branch
`epic-298/308`, cut from `4cec87a`. Engine lease `commander-308-e298`.

Every number below is pinned to the revision it was measured at. Base revision for all
measurements in this file unless stated otherwise: **`4cec87a`**.

## Worktree isolation (launch order item 10)

```
$ py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/e298-308"
worktree OK: in C:/Programs/constellation-skills-wt/e298-308
EXIT=0
```

## Launch-order claims reconciled against the tree

The order instructs verification of its own claims (three of this Admiral's orders carried
wrong claims this epic). Result: **the order is materially accurate.** Two deltas, both
minor, neither changing scope.

| Order's claim | Verdict | Evidence |
|---|---|---|
| f1Brainz `docs/agents/` has 3 files, all in its `README.md` index | **HOLDS, with a delta** | README.md:205-207 lists exactly `ORCHESTRATOR_CONTEXT.md`, `CREW_CONTEXT.md`, `engine-config.json`. But a **4th file exists on disk and is NOT indexed**: `GLOSSARY.md` (41 lines). So "all three listed" is true; "docs/agents/ contains three things" is not. |
| This repo has one file there (`ORCHESTRATOR_CONTEXT.md`) | **HOLDS** | `test -f` over all four candidate names: only `ORCHESTRATOR_CONTEXT.md` present. `GLOSSARY.md`, `engine-config.json`, `CREW_CONTEXT.md`, `README.md` all ABSENT. |
| #342: `LIFECYCLE_STANDINGS` has no `confirmed` | **HOLDS** | `scripts/apply_episode_delta.py:149` — `LIFECYCLE_STANDINGS = ("active", "disputed", "superseded", "rejected")` |
| The 20-entry hard cap | **HOLDS, and is binding NOW** | `scripts/apply_lessons_delta.py:37` `DEFAULT_CAP = 20`; :435 `if len(book.active) >= book.cap: raise`. See the reproduced refusal below. |
| #322: truth-layer taxonomy omits the episode store | **HOLDS** | `docs/CONSTELLATION_OVERVIEW.md:63-77` — four layers (dense / compressed durable / workflow-local / issues). Neither `episodes/` nor `LESSONS.md` appears anywhere in the block. |
| #348: `EPISODE_STORE.md` §1 stale gitignore claim | **HOLDS** | `git check-ignore .agent-work/` exits **1** (NOT ignored); `git ls-files .agent-work/` returns **1958** tracked files. `docs/EPISODE_STORE.md:27-29` still shows a transcript asserting exit 0 / zero files. |

## Half 2's reason, in checkable form

The Admiral's standing instruction: state the deletion's reason with the command and the
counts, not in a form that merely sounds settled. #327 shipped a justification measured
false by the gate that executed it.

**Tommy's stated rationale:** *"The hard cap was intended to not let things hang out, but it
just leads to forgetting when it's not cleaned up."*

**Measured at `4cec87a`. The rationale HOLDS, and it is UNDERSTATED.**

### (a) The bank is at cap, derived from a command

```
$ python -c "<split .agent-work/LESSONS.md on '## Active', regex '^### lesson:' per block>"
active entries: 20
status tally: Counter({'active': 17, 'exported': 3})
```

Header state line: `run-tick=40 cap=20`. So **20/20**.

### (b) The cap does not merely warn — the writer HARD REFUSES

Reproduced against a **copy** in the scratchpad, never the live file:

```
$ python scripts/apply_lessons_delta.py --file <copy>/LESSONS.md <copy>/delta.json
error: add cap-proof-probe: active cap 20 reached — retire before adding
EXIT=1
```

Live file verified byte-identical before and after by sha256 (both
`34774cba14fc64ed66e040750c0a7ed33dca47dff7895b1f7c5e580ebefd2f95`).

**Guard against a false proof.** The first two probe attempts also exited non-zero, but for
the WRONG reason — `delta requires a non-empty string work_id`, then `task_class is
required` (the op schema uses `task_class`/`bank_reason`, not the hyphenated forms the
Markdown record displays). A refusal for a schema reason would have "proved" the cap
without ever reaching the cap check. Only the third attempt, with a schema-valid op,
reached `active cap 20 reached`. Recording this because it is the exact failure class the
epic keeps finding: **a check that cannot fail is indistinguishable from one that passed**,
and its mirror — a refusal attributed to the wrong cause.

### (c) The "forgetting" half, measured per-lesson

Predicate note: fields are bound per-lesson by splitting on `^### lesson:` FIRST and
regexing within each block, not by regexing the whole section (which would let one lesson's
`- confirmed:` line bind to another's id). Block count asserted == 20.

- **10 of 20** carry `last-confirmed: none` — never once reconfirmed since being banked.
- **12 of 20** have `runs-since-confirmed >= 4`.
- Two have sat **9 runs**: `test-harness-concurrency-failsafe`,
  `observe-midprocess-state-not-via-end-output`.

### The correction Tommy's wording does not cover

His reason is about **forgetting**. Measured, there is a second and currently more acute
effect he did not name: at 20/20 the cap is **actively blocking capture**. The next real
finding any run produces cannot be banked at all — the writer refuses it. The cap's
present-day effect is not an untidy bank; it is a **closed intake**.

So the deletion stands on a stronger reason than the one that authorised it. This is the
#327 shape repeating with the opposite sign: there, the stated reason was measured false and
the action was still right; here, the stated reason is measured TRUE and incomplete.

## The store, and what it can be trusted to contain

`#305` (merged `4cec87a`, PR #389) wired mechanical capture from engine state, with
`tests/test_episode_negative_control.py` proving the mechanical field group lands correctly
**without agent diligence** (`test_control_records_nothing_agent_authored`,
`test_the_seam_emits_the_same_group_unasked`, plus four red-proofs). So `## Mechanical` is
trustworthy without diligence; `## Agent-supplied` is still irreducibly agent-authored
(`_validate_create` requires all five kinds non-empty), so nothing auto-creates an episode.

**Store contents at `4cec87a`: 7 active episodes, 0 retired, across 2 runs.**

```
episodes/active/: issue-304-g3-001 .. -005 (run issue-304-g3, role implementer)
                  issue-309-001, issue-309-002 (run issue-309, role commander)
episodes/retired/: empty
```

## #342 — the store cannot express "consolidated", and my workaround

`LIFECYCLE_STANDINGS = ("active","disputed","superseded","rejected")` — no `confirmed`, and
no per-episode "consolidated" standing distinct from retirement. Changing the store is
#301's territory.

**Workaround, named rather than silent:** I do NOT invent a standing. Retirement already
carries the two fields that express consolidation exactly — `retired-reason` and
`consolidated-into` — and per `decision:retirement-moves-the-file` the retire MOVES the file
into `episodes/retired/`. So "marked consolidated" is represented as:

- the file's **location** (`episodes/retired/<id>.md`) — a filesystem fact, not a parsed field;
- `consolidated-into: <cluster-id>` naming the destination;
- `retired-reason:` naming this issue and the consolidation.

What this does NOT give, stated plainly: there is no way to distinguish "retired because
consolidated" from "retired for any other reason" **except by reading `retired-reason`
prose**. That is a real residual limitation of the store as shipped, and it is #301's to
close, not mine.

---

# Run log — gates g1, g2 (complete), and what g4 needs

Pinned to `c2d7414` on `epic-298/308`.

## Cold plan critic: 2 BLOCKING, both mine, both real

The launch order made the critic mandatory ("has caught a blocking defect in every plan
this epic"). It held again.

**BLOCKING 1 — g4's postcondition was unreachable before g6.** g4 demanded zero active
lessons and ran four items before g6. But `lesson:verify-launch-order-claims-against-code`
*states cluster A's own pattern*, so disposing it IS the routing decision: graduating it to
`docs/agents/` is bin 2. Three bad options and no fourth — self-rule, destroy the bank's
most-confirmed entry, or leave g4 unreachable. Fixed by carving that one lesson out **by
id** (`checks/dispositions_done.py`), with g6 disposing it as part of the consolidation.
I did not see this. The plan would have deadlocked at g4.

**BLOCKING 2 — my intake guard matched 2 of 6 real sites.**
`! grep -rn 'Active section of .agent-work/LESSONS.md' skills/` matches only the two spine
JSONs. The other four phrase it differently. Editing the two would have turned the guard
green while the Admiral doctrine, the launch-order inherited-context block and the Charter
agent guide all still fed lessons to live agents.

### The recurrence I committed while planning its own consolidation

**This is the sharpest finding of the run and it is against me.**

Cluster A is *an under-inclusive or stale secondhand claim taken as premise*. While planning
its consolidation I committed it **twice**:

1. My g5 imperative enumerated **5** intake sites as though complete. A command over the
   corpus finds **6 across 5 files** — I missed the one in `ADMIRAL_SPINE.template.json`,
   and it sits in the `latitude` task, not `context`, so a reader checking `context` would
   also have missed it. This is `issue-304-g3-001` exactly: *enumerating suites, not
   assertions*.
2. Then, **one revision later, in the very guard written to fix it**, I used
   `[^.\n]{0,40}` — a character class that excludes the dot, so it could never match any
   phrase containing `.agent-work/`. It went green against three live intake sites. That is
   `lesson:guard-must-be-defined-by-the-consumer-not-a-character-list`, committed inside the
   file whose own docstring cites that lesson.

Recorded rather than quietly fixed, because it is evidence, not embarrassment: **prose did
not stop an agent that had just read the cluster, was actively consolidating it, and had the
remedy in front of it.** That is a real argument for **bin 1** and against my own stated
lean in `ROUTING_QUESTION.md`. It should be weighed in Tommy's ruling.

## Gates closed

| gate | what landed | evidence |
|---|---|---|
| `g1-build-destination` | `docs/agents/CREW_CONTEXT.md` (f1Brainz's structure, not invented); both files indexed from README under "This repo's own agent context"; tier stated in the file header | c1-c3 green, full suite green |
| `g2-doc-coherence` | **#348**: section 1's transcript re-measured at `4cec87a`, cause named (`b69e6c8` / #326), ruling preserved. **#322**: taxonomy gains `episodes/` plus the cutover and why LESSONS.md's absence is the ruling | c1-c3 green, full suite green |

**g2 c1 was mutation-verified**, not merely observed green: green, then append the false
line, then **red**, then restore, then green. The check demonstrably fires.

Two shell traps hit, both named in the launch order and both real:

- **Backticks inside a double-quoted string are executed.** My first g2 c1 command died with
  `.gitignore\: Not a directory` — a refusal for entirely the wrong reason, which would have
  read as a failing gate. Single-quoted now.
- **`git checkout <file>` to undo a test mutation reverted the real edit too.** Snapshot to a
  scratch copy instead. Cost one redo of the whole section-1 edit.

## PROPOSED dispositions for g4 — analysis only, NOT executed

g4 has not run. This is left so a successor does not re-derive 20 judgments from scratch.
**Every graduation names its tier** (`tier-must-be-justified`). Writes go through
`apply_lessons_delta.py`; a graduation is a paired edit-plus-retire whose retire reason names
the destination.

| # | lesson | proposed disposition | tier justification |
|---|---|---|---|
| 1 | test-harness-concurrency-failsafe | GRADUATE to `CREW_CONTEXT.md` | test-authoring discipline; its own bank-reason says it lacked a home — that home now exists |
| 2 | verify-launch-order-claims-against-code | **CARVED OUT to g6** | disposing it IS the routing decision |
| 3 | observe-midprocess-state-not-via-end-output | GRADUATE to `CREW_CONTEXT.md` | test-authoring; crew writes the tests |
| 4 | verify-harness-field-and-drive-real-writer | GRADUATE to `CREW_CONTEXT.md` | confirmed 5x; crew-tier testing rule |
| 5 | round-trip-tests-prove-artifacts-not-parsers | RETIRE — **already graduated at g1** | already in CREW_CONTEXT.md's verification section |
| 6 | checklist-engine-from-child-relative-path-and-gated-vs-survey | DELETE | constellation-scoped, already `exported`; debt is paid upstream, not by banking |
| 7 | harvest-before-sweep-enforcement-gap | DELETE | same — already `exported` |
| 8 | cold-critic-mandatory-for-measurement-dependent-plans | GRADUATE to `ORCHESTRATOR_CONTEXT.md` | planning/gate authority is orchestrator-tier. **This run is a 6th confirmation** |
| 9 | windows-subprocess-env-does-not-shadow-path-resolution | GRADUATE to `CREW_CONTEXT.md` | Windows section; crew writes the subprocess probes |
| 10 | prove-command-fails-postcondition | GRADUATE to `ORCHESTRATOR_CONTEXT.md` | postcondition authoring is gate authority |
| 11 | canonical-routing-can-dissolve-a-file-fence | GRADUATE to `ORCHESTRATOR_CONTEXT.md` | launch-order / fence authoring is orchestrator-tier |
| 12 | crew-plan-file-shares-parent-gauge-directory | GRADUATE to `ORCHESTRATOR_CONTEXT.md` | crew-dispatch mechanics; the dispatcher is the orchestrator |
| 13 | reviewer-old-vs-new-repro-without-mutating-file-under-review | GRADUATE to `CREW_CONTEXT.md` | a reviewer technique; reviewer is crew |
| 14 | drill-scope-should-name-every-sibling-template | GRADUATE to `docs/superpowers/drills/` | the doc that owns drills owns this; NOT docs/agents — wrong audience |
| 15 | lightweight-critic-catches-real-findings-on-bounded-issues | DELETE | subsumed by #8; keeping both graduates one rule twice |
| 16 | reviewer-fowler-template-path-wording-ambiguous | FILE AN ISSUE, then DELETE | a fixable wording defect in `skills/reviewer/`, which **this repo owns** — a lesson is the wrong container for a fix |
| 17 | guard-must-be-defined-by-the-consumer-not-a-character-list | RETIRE — **already graduated at g1** | already in CREW_CONTEXT.md |
| 18 | a-panel-inherits-what-it-was-not-told-to-vary | GRADUATE to `ORCHESTRATOR_CONTEXT.md` | design-it-twice is an orchestrator activity |
| 19 | a-check-that-cannot-fail-is-indistinguishable-from-one-that-passed | RETIRE — **already graduated at g1**; cluster B filed as **#392** | already in CREW_CONTEXT.md |
| 20 | stale-description-has-two-shapes-and-only-one-yields-to-verification | **FLAGGED — do not dispose without checking it against the ruling** | its shape 1 overlaps cluster A; shape 2 (agent-to-agent drift) does not. A successor must confirm graduating it is not a second consolidation in disguise |

**Row 20 is a genuine open question, not a recommendation.** Its own bank-reason warns
against graduating one half and declaring the class closed — precisely the risk if cluster
A's consolidation lands separately.

Count check: 20 rows = 1 carved out + 3 already-graduated + 4 deletes + 11 graduations + 1
flagged. `checks/dispositions_done.py` requires exactly the carve-out to survive.

## Honest status of the two halves

- **Half 1** — rhyme-search done and NOT a null; cluster selected; routing question posed
  with both bins argued. The consolidation itself (g6) and the source-episode retirement
  (g7) are **not landed**; they await Tommy's ruling.
- **Half 2** — the destination is built (g1) and the two coherence defects are closed (g2).
  The cap removal (g3), the dispositions (g4) and the intake cut (g5) are **planned and
  gated but not executed**.

---

# CORRECTION — #308 WAS RE-SCOPED. THE TABLE ABOVE IS OBSOLETE.

**Everything above this line was written under the OLD scope. Read `STATE_NOTE.md` first.**

Tommy re-scoped the issue mid-run. What changed, and what it invalidates in this file:

## The "PROPOSED dispositions for g4" table is DEAD — do not execute it

Its 20 rows route lessons to **GRADUATE** (11), **DELETE** (4), **RETIRE as already
graduated** (3), plus one carve-out and one flagged row. **Graduation and deletion are both
withdrawn.** The correct disposition for every one of the 20 is now the same:

> **Migrate it into an episode. Record what is known; mark what is not as unknown.**

The table's only surviving value is as a **per-lesson summary of what each lesson contains**,
useful when composing the episodes. **Its disposition column is wrong on every row.**

## The carve-out rule is dead, and the check that enforces it is now inverted

The table's row 2 holds `verify-launch-order-claims-against-code` back for `g6` because
"disposing it IS the routing decision." That was correct under the old scope. **There is no
`g6` now** — the consolidation is withdrawn, not blocked.

**`checks/dispositions_done.py` requires exactly ONE surviving active lesson and FAILS on
zero.** Under the new scope **zero is correct.** That script asserts the opposite of the
requirement and is still wired as `g4-disposition-lessons` c1 in the frozen `execute.json`.
It must be rewritten or replaced. **A successor who trusts it will be blocked by a check
defending a withdrawn rule.**

## What else in this file is now historical rather than operative

- **The two-bin routing question** (`ROUTING_QUESTION.md`, and this file's discussion of
  bins, coverage and my lean): **historical.** No bin will be chosen.
- **My argument that the self-recurrence "is a real argument for bin 1 and against my own
  stated lean":** that conclusion is exactly the kind of importance judgement Tommy has now
  ruled a local agent must not make. **The observation survives; the conclusion is demoted
  to `other-notes`, attributed, deciding nothing.**
- **The two coverage numbers (mechanism 1/3, prose 3/3):** they **stay**, as observed facts
  about the remedies. They are used to decide nothing.
- **`g1`'s `CREW_CONTEXT.md` and `g2`'s #348/#322 fixes:** these **stand** and are merged
  into the branch. `CREW_CONTEXT.md` is flagged to Tommy but kept, because what it carries is
  observable environment facts, not distilled importance judgements.

## What is unchanged and still load-bearing

Everything in the first half of this file that is a **measurement** rather than a decision:

- the cap is binding at 20/20, reproduced (`exit 1`, `active cap 20 reached`), live file
  sha256-identical before and after;
- 10 of 20 never confirmed, 12 of 20 stale >= 4 runs;
- `.agent-work/` is NOT gitignored (exit 1, 1958 tracked files);
- the store held 7 active episodes, 0 retired, across 2 runs at `4cec87a`;
- the #342 workaround analysis, which now matters MORE, because the migration will hit
  `create`'s required `observed-behavior` on thin lessons. **Do not back-fill it.**

Under the new scope the staleness numbers **read differently and this is the important
reversal**: 10-never-confirmed and 12-stale looked like weak entries worth culling. They are
now **observations with an unknown recurrence count**. The count is empty; **the record is
not invalid.** That is the single biggest interpretive change the re-scope makes to the
measurements above.
