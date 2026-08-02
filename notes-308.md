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
