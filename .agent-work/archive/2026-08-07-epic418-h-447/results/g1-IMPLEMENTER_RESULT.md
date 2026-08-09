# Implementation Result — #447 gate g1

## Assigned gate
`g1 — the guard, authored and proven RED on the untouched tree`

## Completed slice
`scripts/verify_retirement.py` (four legs, `scan()` returning named `Violation`s, TSV CLI),
`tests/test_retirement_guard.py` (one decoy red-proof per leg plus the anti-rot census), and
the seeded frozen approval census `tests/data/store_mentions.approved.txt`. Zero retirement
work was done, as the gate requires.

## Scope

**Files changed:** three created, none modified.

- `scripts/verify_retirement.py` (580 lines, new)
- `tests/test_retirement_guard.py` (295 lines, new)
- `tests/data/store_mentions.approved.txt` (71 lines, new — 18 approved entries)

`git status --porcelain` after the run, verbatim:

```
?? .agent-work/epic418-h-447/
?? scripts/verify_retirement.py
?? tests/data/
?? tests/test_retirement_guard.py
```

**Specific exclusions touched:** no. No skill, spine, script or doc was edited. Nothing was
committed — the Commander commits at integrate.

## Behavior changed
No existing behavior. One new runnable check: `python scripts/verify_retirement.py` exits 1
and names 131 violations across 3 legs on the untouched tree.

## Design as built

| leg | on the untouched tree | how it is falsified |
|---|---|---|
| `retired-path-still-tracked` | RED — 5 | decoy re-commits `.agent-work/LESSONS.md` verbatim |
| `unapproved-store-mention` | GREEN by construction | decoy plants an unapproved `episodes/` mention |
| `replacement-absent` | RED — 5 | decoy deletes the capture command from a healthy tree |
| `retired-name-on-shipped-surface` | RED — 121 | decoy plants one line of prose naming the playbook |

`scan(root) -> list[Violation]` where `Violation` is
`NamedTuple(leg: str, path: str, line: int, detail: str)`, sorted by `(leg, path, line)`.
Surfaces come from `git ls-files -z`, never `Path.rglob`. A `git ls-files` failure raises
rather than answering `[]` — "nothing is tracked" and "I could not ask" must not read the
same.

`replacement-absent` emits one violation per unmet requirement, each carrying the path that
should have satisfied it: both spine imperatives, both install bundles (read out of
`SKILL_SCRIPT_BUNDLES` via `ast`, not imported and not regexed), and the script on disk. All
five fire today.

Shipped surface = the index minus the four record-only roots the handoff names, minus two
scope exclusions (`tests/`, `notes-*.md`). Every exclusion carries a **required non-empty
reason**; `_require_reasons` raises at import if one is blank, and
`test_an_approval_without_a_reason_is_refused` pins the same rule for the census.

## Test mode
**Required:** test-first (the guard is authored and proven red before any retirement exists).
**Satisfied:** yes. The guard was observed failing on the real untouched tree, and each leg
was separately observed failing on a decoy that plants exactly one violation.

## Evidence — every command with its REAL exit code

Exit codes captured by redirecting to a file then echoing `$?`. No command was piped to
`tail` for its status.

```bash
python -m pytest tests/test_retirement_guard.py -q
# 8 passed, 1 xfailed in 1.59s
# EXIT=0
```

```bash
python scripts/verify_retirement.py > /tmp/e2.txt; echo EXIT=$?
# EXIT=1        <- required: MUST be 1 on the untouched tree
# 131 violations
```

```bash
cut -f1 /tmp/e2.txt | sort -u
# EXIT=0        <- 3 distinct legs; required: >= 3
```

```bash
python -m pytest -q
# 1696 passed, 2 skipped, 1 xfailed, 550 subtests passed in 435.91s
# EXIT=0
```

Full-suite delta against the stated baseline of **1688 passed, 2 skipped**: `+8 passed`
(the eight new guard tests) and `+1 xfailed` (`test_canon_is_clean`, expected-fail by
design). **No new failures.**

## Falsification — the guard was watched failing, not assumed able to fail

Beyond the per-leg decoys, one temporary mutation was applied to the guard itself and then
reverted from a byte-exact backup: dropping `"LESSONS.md"` from `RETIRED_NAMES`.

```
1 failed, 7 passed, 1 xfailed
FAILED tests/test_retirement_guard.py::test_red_proof_retired_name_on_shipped_surface
  Right contains one more item: 'retired-name-on-shipped-surface'
```

Restored, the suite returns to `8 passed, 1 xfailed`. The guard is not merely green; its
green is load-bearing.

## Verbatim red transcript

Captured to `.agent-work/epic418-h-447/evidence/g1-guard-red.txt` (also carries the full
131-line violation list).

```
# g1 guard RED transcript — captured on the REAL, untouched tree
# worktree: C:/Programs/constellation-skills-wt/epic418-h-447
# branch:   epic-418/h-447-episodes-retirement
# HEAD:     cbd9aee86c54e612b148dc7220b262c5bef03aa4
# tree state: no retirement work has been done; only the guard, its tests and
#             its approval census exist. This is the evidence #308 could not produce.

$ python -m pytest tests/test_retirement_guard.py -q
........x                                                                [100%]
8 passed, 1 xfailed in 1.59s
EXIT=0

$ python scripts/verify_retirement.py > <file>
EXIT=1   (violations: 131)

$ python scripts/verify_retirement.py | cut -f1 | sort -u        # VERBATIM OUTPUT
replacement-absent
retired-name-on-shipped-surface
retired-path-still-tracked
EXIT=0   (distinct legs: 3)

$ python scripts/verify_retirement.py | cut -f1 | sort | uniq -c   # per-leg counts
      5 replacement-absent
    121 retired-name-on-shipped-surface
      5 retired-path-still-tracked

# unapproved-store-mention is absent by construction: the census was seeded
# against this tree, so that leg goes red at g3 when the mentions move.
```

## Close criteria

1. Four legs, no more — `test_every_leg_has_a_red_proof` asserts `len(vr.LEGS) == 4`. **met**
2. Every leg has a decoy asserting leg AND path. **met**
3. The leg census passes, against a roster pinned as an independent literal. **met**
4. `scan()` on the untouched tree returns >= 3 distinct legs. **met — exactly the 3 named**
5. No new failures beyond the baseline. **met — +8 passed, +1 xfailed, 0 failed**

## Corner cases NOT chased — each commented at the code site

**1. `notes-*.md` is an exclusion the handoff did not enumerate.**
`scripts/verify_retirement.py:137`

The handoff names exactly four record-only roots and states the store-mention census is
"~18 lines". Those two facts do not reconcile: the census is **37** lines with the
root-level run notes on the surface and **exactly 18** with them off it. `notes-304.md`,
`notes-308.md` and `notes-309.md` are the same class as `docs/superpowers/` — records of
what a past issue found. I excluded them (with a reason string, in `SCOPE_EXCLUSIONS`
rather than in `RECORD_ONLY_ROOTS`, so the handoff's own four stay recognisable) and
reproduced the handoff's stated measurement. **This is a judgement call on an inconsistency
in the handoff, not a licence I granted myself — it wants a Commander ruling.** Reverting it
means 19 more approved entries, no code change.

**2. A path staged for deletion is seen by the path leg but not the content legs.**
`scripts/verify_retirement.py:215`

`_read_lines` reads the working tree; a file staged for deletion is still in the index
(so `retired-path-still-tracked` sees it) but has no working-tree content (so the two
content legs skip it). Closing this means reading blobs through `git cat-file --batch`. No
such path exists in this tree today and the gap is in the safe direction for the leg that
matters, so I did not build the batch-read path.

## Docs/contracts touched
None. The gate produces zero retirement by design.

## Map Impact

- **Structural anchors touched:** new leaf `scripts/verify_retirement.py`; new test module
  `tests/test_retirement_guard.py`; new data root `tests/data/`. No existing module was
  edited, so no anchor moved.
- **Capabilities added:** *verify-retirement-holds* — the repository can now be asked, and
  answer with named legs, whether the #403 retirement holds. This is the capability #308
  lacked and the reason its retirement silently regressed.
- **Constraints touched:** `constraint:episodes-are-not-prescriptions` is now mechanically
  guarded, via the frozen approval census rather than a pattern allowlist. The guard's own
  discriminator message states the constraint by name at the point of failure.
- **Claims/evidence produced:** the guard fails on the real untouched tree across three
  legs, with the transcript at
  `.agent-work/epic418-h-447/evidence/g1-guard-red.txt` — the falsification #308 could not
  produce.
- **Decision candidates:** the `notes-*.md` exclusion above.
- **Trust limitations:** `replacement-absent` is red and MUST stay red until g3. Any later
  gate that "fixes" it without shipping `scripts/verify_episode_captured.py` has defeated
  the presence half. `test_canon_is_clean` is `xfail(strict=True)` — g6 removes the marker,
  and strict XPASS means the suite breaks the moment the tree goes clean, which is
  deliberate.

## Assumptions
- "BOTH spine imperatives" = `skills/commander/templates/COMMANDER_SPINE.template.json` and
  `skills/admiral/templates/ADMIRAL_SPINE.template.json` (the only two shipped spines that
  carry a closeout-tier bundle; `EXPLORER_SPINE` has neither bundle).
- The bundle check reads the `SKILL_SCRIPT_BUNDLES` literal, not `expand_script_bundle`'s
  expansion. g3 adds the name to the literal, so the two agree; a name arriving only as a
  runtime companion would not satisfy this leg.

## Stop conditions hit
None.

## Out-of-scope observations
- 121 of the 131 violations are `retired-name-on-shipped-surface`, concentrated in
  `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (33), `docs/EPISODE_STORE.md` (9),
  `scripts/verify_agent_feedback.py` (9) and `scripts/stage_feedback.py` (8). Two of those
  are themselves retired paths, so leg 1 and leg 4 will clear together for them. The design
  docs are the real body of work for g3–g5.
- `scripts/stage_feedback.py` and `scripts/collect_feedback.py` are not on the handoff's
  retired-path list but carry retired names heavily. Whether they are in or out of the
  retirement is a Commander question, not a guard question.

## Workflow Feedback

- **Handoff gaps:** two, both real. (a) The record-only roots list and the stated
  measurement contradict each other — four roots yields 37 census lines, the handoff says
  "~18", and only excluding root-level `notes-*.md` reconciles them. I had to reverse-engineer
  the author's surface definition from an approximate count in prose. A handoff that pins a
  measurement should pin the *command* that produced it, exactly the way this epic's own
  doctrine says distribution claims must come from a `uniq -c`. (b) `unapproved-store-mention`'s
  discriminator message contains `<path>:<line>` with no statement of whether `<line>` is the
  line number or the line text. I used the number (the standard `file:line` idiom; the
  census carries the text) — but "state it verbatim" and an ambiguous placeholder are in
  tension, and the next agent will guess differently.
- **Context rediscovered:** which two spines "BOTH spine imperatives" means, and where the
  install bundles live (`SKILL_SCRIPT_BUNDLES` in `scripts/install_constellation.py`).
  Neither is named in the handoff; both are load-bearing for `replacement-absent` and I
  found them by grep. One line of Map Anchors would have carried it.
- **Instructions improvised around:** the plan template's TDD shape assumes red-then-green
  on the SAME assertion. Here the deliverable is a check that must END red — `test_canon_is_clean`
  is `xfail(strict=True)` and `replacement-absent` stays red until g3 — so a command
  postcondition phrased "the tests pass" would have been satisfied by a guard that could not
  fire. I inverted the postconditions instead: each leg's gate asserts the guard *fails* in
  a specific, named way (`awk -F'\t' '$1=="replacement-absent" && $2=="..."'`). The engine
  handled it fine, but the template has no vocabulary for "green means red".
- **What would have made this easier:** put the exact command that produced any measurement
  the handoff quotes directly beside the number. That one change removes the whole
  `notes-*.md` judgement call — I would have run the command, got 18, and known the surface
  definition without inferring it.

## Return status
`complete`

---

## REWORK — round 2, after the Commander's BLOCK

Three blocking findings, all confirmed against the tree before anything was changed. Scope
unchanged: the same three files, nothing else touched, nothing committed.

### BLOCKING-1 — the guard fired on itself once committed. FIXED.

**Confirmed independently before fixing.** I copied the index to a throwaway, staged the
three files into it, and re-ran my own scanner:

```
STAGED, pre-fix:   5 replacement-absent
                 133 retired-name-on-shipped-surface     (121 + 12 self-hits)
                   5 retired-path-still-tracked
                   6 unapproved-store-mention            (0 + 6 self-hits)
self-hit lines:  92, 97-101, 108-113        (retired-name)
                 126, 194, 292, 298, 299, 311 (store-mention)
```

Exactly the lines the review named. My round-1 numbers were an artifact of the guard being
untracked — `git ls-files` hid it from itself, so every claim I made was pinned to a state
the repo leaves the moment it is committed. The finding is correct and my evidence was
measuring the wrong tree.

**Fix:** `scripts/verify_retirement.py` now excludes itself via `SCOPE_EXCLUSIONS`, with the
reason at the code site (`scripts/verify_retirement.py:135-150`) stating the same principle
the test docstring already applied to `tests/` — a guard cannot be inside the set it guards
— and naming the consequence: unexcluded, the tree still reports 18 violations after g6,
`test_canon_is_clean` can never XPASS, and the `xfail(strict=True)` marker outlives the work.

**Verified the way the bug was found — against a staged index, not the working tree:**

```bash
cp "$(git rev-parse --git-dir)/index" /tmp/rw-index
GIT_INDEX_FILE=/tmp/rw-index git add scripts/verify_retirement.py \
    tests/test_retirement_guard.py tests/data/store_mentions.approved.txt
GIT_INDEX_FILE=/tmp/rw-index python scripts/verify_retirement.py > /tmp/rw-staged.txt; echo EXIT=$?
# EXIT=1
#       5 replacement-absent
#     121 retired-name-on-shipped-surface
#       5 retired-path-still-tracked
# unapproved-store-mention: 0
```

**121 / 5 / 5 across exactly 3 legs, store-mention back to 0** — the required numbers, hit
exactly. Pinned against regression by `test_the_guard_is_not_inside_the_set_it_guards`.

### BLOCKING-2 — the retired-name leg never tested the path string. FIXED.

`_leg_retired_name` now tests each shipped path against `RETIRED_NAMES` before reading its
lines, emitting a `line 0` violation — the whole path is the violation, not any line in it.
The comment claiming coverage of "a skill directory" was true of the intent and false of the
code; both now agree.

New decoy `test_red_proof_retired_name_on_a_path_string` re-adds
`skills/lessons-auditor/SKILL.md` with contents that name nothing at all, and asserts leg,
path and `line == 0`. That is the case the old leg missed entirely: a restored skill can be
innocent line by line and still be the retired thing, because what identifies it is where it
sits.

Effect on the real tree: `retired-name-on-shipped-surface` 121 -> 128. The seven new
path-string violations:

```
scripts/apply_lessons_delta.py
scripts/verify_agent_feedback.py
scripts/verify_lessons_applied.py
skills/lessons-auditor/SKILL.md
skills/lessons-auditor/templates/LESSONS_AUDIT.template.json
skills/lessons-auditor/templates/LESSON_CANDIDATES.template.md
skills/lessons-auditor/templates/RUN_BRIEF.template.md
```

### BLOCKING-3 — silent skip on a decode failure. FIXED.

`_read_lines` no longer swallows a decode failure. A shipped file that is not UTF-8 text now
raises, naming the file and the two ways out (make it UTF-8, or exclude it in
`SCOPE_EXCLUSIONS` with a reason). The docstring cites this repository's own precedent:
`apply_episode_delta._require_store_layout` refuses a missing store rather than answering
"0 episodes", because "nothing is wrong here" and "I could not look" must not be the same
answer.

**Exactly one skip survives, and it is named rather than incidental:** `FileNotFoundError`,
the path-staged-for-deletion case — it counts for the path legs (which ask the index) and has
no content for the content legs to read. That is the corner case already recorded in round 1,
now the only one left.

Covered by `test_an_undecodable_shipped_file_is_refused_not_skipped` (a latin-1 file planted
in a decoy). There are zero non-UTF-8 shipped files in this tree today; the point is that
adding one cannot quietly shrink the guard's coverage.

### ADVISORY — `notes-*.md` narrowed, per the ruling

The glob is gone. `RUN_NOTES` now enumerates the **seven** tracked files explicitly
(`notes-261/269/301/304/308/309/b420.md`) and the comment's count is corrected — it said
three, which was the number I had *observed in the census* rather than the number the glob
*removed*. That gap is precisely the drift flagged: an exclusion whose extent is a pattern
grows without review.

`is_shipped` now has no pattern matching at all — every exclusion is a directory prefix or an
exact path — and `test_every_exclusion_is_bounded_and_reasoned` asserts no key contains `*`
or `?`, that every reason is non-empty, and that `_require_reasons` really raises.

### Known bypasses — recorded, not built for

One comment at `scripts/verify_retirement.py:180-191`, as instructed: lowercase `lessons.md`
(matching is case-sensitive on purpose — lowering it would collide with ordinary prose); a
NEW root note such as `notes-999.md` (the deliberate cost of enumerating rather than
globbing, and the review step that buys); and a prescription split across two lines (all
matching is line-scoped; closing it needs a paragraph parse this gate does not need). No code
was written for any of them.

### Falsification — both new fixes watched failing

Two temporary mutations, each reverted from a byte-exact backup (`diff` confirms zero
residue):

| mutation | result |
|---|---|
| path-string half disabled | `FAILED test_red_proof_retired_name_on_a_path_string` — 1 failed, 11 passed |
| silent decode skip restored | `FAILED test_an_undecodable_shipped_file_is_refused_not_skipped` — 1 failed, 11 passed |

Restored: `12 passed, 1 xfailed`.

### Evidence — every command with its REAL exit code

Exit codes captured by redirecting to a file then echoing `$?`. Nothing was piped to `tail`
for its status.

| command | exit |
|---|---|
| `python -m pytest tests/test_retirement_guard.py -q` -> `12 passed, 1 xfailed` | **0** |
| `python scripts/verify_retirement.py` (working tree) -> 138 violations | **1** |
| `cut -f1 <out> \| sort -u` -> 3 distinct legs | **0** |
| `python scripts/verify_retirement.py` (STAGED index) -> 138 violations | **1** |
| `cut -f1 <staged> \| sort -u` -> 3 distinct legs | **0** |
| `python -m pytest -q` -> `1700 passed, 2 skipped, 1 xfailed, 550 subtests passed` | **0** |

Full suite against the 1688 passed / 2 skipped baseline: **+12 passed** (the twelve guard
tests) and **+1 xfailed** (`test_canon_is_clean`). **No new failures.**

**The working-tree and staged-index violation lists are now byte-identical** — `diff` of
leg+path across both produces no output. That is the direct proof BLOCKING-1 is closed: the
guard no longer sees itself, so what I measured is what the repo reports after the commit.

Both transcripts are in `.agent-work/epic418-h-447/evidence/g1-guard-red.txt`, labelled
`WORKING TREE` and `STAGED INDEX`, with the round-1 to round-2 deltas and the full 138-line
violation list.

### Corner cases still open after rework

Only one, down from two. The `notes-*.md` judgement call is now ruled and bounded; what
remains is the staged-deletion skip at `scripts/verify_retirement.py:215-231`, which is named
in the docstring and is the single surviving `None` return.

### What this round changed about my own evidence discipline

Round 1's central claim — "observed failing on the real untouched tree" — was measured on a
tree that did not include the artifact under test. The lesson is narrow and worth carrying:
when the deliverable is itself a tracked file, the working tree is not the shipped set, and
`git ls-files` will quietly agree with you. Verify against a staged index whenever the thing
you built will be part of what it measures.

### Final state

```
?? .agent-work/epic418-h-447/
?? scripts/verify_retirement.py
?? tests/data/
?? tests/test_retirement_guard.py
```

Three files, nothing else, not committed.

### Rework return status
`complete`
