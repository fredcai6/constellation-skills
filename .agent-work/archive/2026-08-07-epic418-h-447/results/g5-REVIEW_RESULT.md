# REVIEW_RESULT — g5: the prose sweep, the doctrine tombstone, and the guard's last leg

**Gate:** `g5-review` · issue #447 · epic-418 workstream H
**Worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447` · HEAD `77e428d` · work uncommitted
**Survey:** `.agent-work/epic418-h-447/g5-review/review.json` (20 checks, engine-driven, lease `g5-reviewer-447`)
**Fowler pass:** `.agent-work/epic418-h-447/g5-review/fowler-pass.json` (`verify_fowler_pass.py` exit 0)

## APPROVE

No blockers. All 20 checks pass; all eleven invariants met.

---

## The two checks that carry this review

### A. Is this an absence-only edit? — NO. The survivors hold.

Graded as hard as the removals, and it passes on the harder half.

- **Invariant 7** — `docs/RECURSIVE_IMPROVEMENT_DESIGN.md`: `git diff HEAD --stat` shows **16 insertions,
  0 deletions**. `git grep -c 'LESSONS.md'` returns **12 at `77e428d` and 12 now**. The 33 sites survive
  untouched.
- **Invariant 8** — the `docs/CONSTELLATION_OVERVIEW.md` ruling paragraph is **byte-identical**
  (grepping the diff for `taxonomy` returns 0 hits).
- **Invariant 9** — `docs/superpowers/` and `tests/fixtures/` empty diff, exit 0.
- **Invariant 10** — the important one. All nine `apply_lessons_delta.py` pointers became **descriptions
  of the property**, and I checked each paragraph for a thrown-away argument. None was thrown away:
  - `mirroring apply_lessons_delta.py's contract` → `(validate the whole delta first, then apply every
    op or none)` — this tells the reader **more** than the dead pointer did.
  - The "Rhyme / depart" section **gained** a sentence defining the prior art rather than losing the
    comparison.
  - `docs/EPISODE_STORE.md` appears **zero times** in the 53-entry census. All nine were fixed by
    editing, none approved — the right disposition, and the one that would have been easiest to fake.
- **`episodes/README.md`** (invariant 3) is the clearest non-deletion: the false premise
  (`.agent-work/` is gitignored) was removed and the argument **re-founded on a true one** *and*
  strengthened with a second true reason — a store whose location must be computed can be written to
  the wrong place while every gate reports green. The deleted "Not to be confused with" section was
  replaced by a positive **"No rules."** bullet, not left as a hole.

### B. Did the sweep write the defect it was sweeping out? — NO.

Read every new and rewritten sentence as an agent would, then cross-checked mechanically. A regex for
read-shaped verbs (`read|consult|query|search|look up|check|review|load|skim|refer to|inspect`) within
60 characters of `episode`/`store`/`episodes/`, across **all 521 added lines**, returns **7 hits — and
6 are explicit denials of the read**:

- `Do not read the store back and condition behaviour on what you find there` (AGENT_GUIDE.template)
- `no shipped surface tells an agent to READ the store and condition its behaviour on what it finds`
- `an identifier reference, not an instruction to read the store`
- `a denial of the read path, not an instruction to consult the store`
- `No consolidation / rhyme-search (issue #308) — downstream of this store, not part of it`
- the tombstone's `Do not write, and do not obey, an instruction that has an agent consult the store…`

The 7th is an audience-column entry, discussed under Observations.

**The redefined `harvest` is genuinely write-side.** New definition: *"Gathering what a run's own
artifacts recorded and writing it into the episode store as episodes… The direction is INTO the store.
There is no reading harvested episodes back out as rules."* I checked **every live use of `harvest` in
the corpus**; none reads the store. The two closeout uses (`skills/admiral/SKILL.md` step 1,
`ADMIRAL_SPINE.template.json`) harvest **from** the ADMIRAL_LOG and crew feedback **into** episodes —
exactly the new definition. One residual coverage gap is recorded as an observation, not a blocker.

---

## Per-invariant verdict (all eleven)

| # | Invariant | Verdict | Proof |
|---|---|---|---|
| 1 | `CREW_CONTEXT.md` live read prescription removed; LESSONS row deleted; census reason fixed | **PASS** | `grep 'Read them with\|query_episodes'` exit 1; `grep 'LESSONS.md\|apply_lessons_delta'` exit 1; table now reads "Two stores"; census line + reason both replaced |
| 2 | `harvest` redefined or removed; `episode` not left dangling | **PASS** | `harvest` now write-side; `episode` row lost "kept for later harvest", gained "A record, never a rule." |
| 3 | `episodes/README.md` false premise replaced, not deleted | **PASS** | `grep 'gitignored\|Not to be confused'` exit 1; I confirmed the old premise WAS false — `.gitignore` line 1 is the "# .agent-work/ is TRACKED" comment and `git ls-files .agent-work \| wc -l` = **3067** |
| 4 | Tombstone in `ORCHESTRATOR_CONTEXT.md`, all five clauses, as doctrine | **PASS** | five independent greps, all exit 0, lines 39/43/45/48/51 |
| 5 | Every remaining live pointer repointed or removed | **PASS** | guard exit 0 with zero unapproved residue; 14 files repointed |
| 6 | `Lesson:` field accepts an episode id | **PASS** | template reads `<originating episode id from episodes/ (stable identity), or n/a>` |
| 7 | `RECURSIVE_IMPROVEMENT_DESIGN.md` — 33 sites untouched, header only | **PASS** | 16 insertions / 0 deletions; `git grep -c` 12 = 12 |
| 8 | `CONSTELLATION_OVERVIEW.md:98` ruling paragraph survives | **PASS** | byte-identical |
| 9 | `docs/superpowers/**`, `tests/fixtures/**` untouched | **PASS** | empty diff, exit 0 |
| 10 | `EPISODE_STORE.md` pointers → descriptions | **PASS** | all 9 fixed by editing; zero census entries for this file |
| 11 | The guard can reach green — reason-carrying census, one parser, red-proved | **PASS** | guard exit 0 / 0 bytes; census exactly-covering; red-proved two ways by me |

---

## Verdict on the census reasons

**PASS — and this is the criterion I spent the most time on.**

`tests/data/retired_names.approved.txt`: **53 entries, 53 distinct reasons.** No repeated reason text
at all, so the specific defect this gate exists to fix — one reason written for a block of four lines
and true of three — **cannot recur in this file**. Every reason describes its own line and falls in an
approvable class:

| count | class | path |
|---|---|---|
| 33 | frozen historical design record | `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` |
| 8 | survivor script naming what it stages | `scripts/stage_feedback.py` |
| 3 | replacement writer recording inherited contract | `scripts/apply_episode_delta.py` |
| 2 | another workstream's inherited finding record | `RETURN.md` |
| 2 | replacement gate naming what it replaced | `scripts/verify_episode_captured.py` |
| 1 | the ruling that records the exclusion | `docs/CONSTELLATION_OVERVIEW.md` |
| 1 | the tombstone, naming the files in order to forbid them | `docs/agents/ORCHESTRATOR_CONTEXT.md` |
| 1 | deny-glob re-staging block | `COMMANDER_SPINE.template.json` (`archive.c4`) |
| 1 | hypothetical placeholder-token example | `scripts/init_work_area.py` |
| 1 | bundle comment analogy, nothing installed under that name | `scripts/install_constellation.py` |

**Not one reason amounts to "an agent is still told to use the retired thing."** I opened the two
comment-analogy files rather than trusting the reasons: `init_work_area.py:21` literally reads *"a
hypothetical `<lessons-auditor-skill-dir>`"*, and `install_constellation.py:221` is a comment saying
how-to-talk *"mirrors interrogator/lessons-auditor. It ships no script."* — both accurate.

I also verified the census header's own factual claim: `git grep` finds **no shipped surface**
referencing `stage_feedback.py` outside its own file, its tests, `verify_retirement.py`'s explanatory
comment, and the historical record. Good faith is visible — the header **records** that script's
residue as an open triage candidate instead of quietly approving past it.

**A structural note worth the Commander's attention:** the RID header is load-bearing for the census.
It is what makes **33 of the 53** approvals honest — without a header saying "do not act on any of
this", those lines read as live proposals. Invariant 7's deliverable and invariant 11's census are
coupled, and both landed.

`tests/data/store_mentions.approved.txt`: all **18** g5-touched entries carry bespoke reasons, and the
`CREW_CONTEXT.md` read instruction was removed from **both** the prose and the census — the both-sides
fix the handoff demanded. Pre-existing repeats elsewhere in that file are recorded as an observation
below.

---

## Per-check findings, with the command and its real exit code

| check | command | real exit | result |
|---|---|---|---|
| Guard | `python scripts/verify_retirement.py > guard.txt` then `wc -c` | **0**, 0 bytes | PASS |
| Fences | `git diff HEAD --stat -- <4 fenced files>` | **0**, 0 bytes | PASS — none touched |
| Untouched | `git diff HEAD --stat -- docs/superpowers/ tests/fixtures/ episodes/active/ episodes/retired/ RETURN.md` | **0**, 0 bytes | PASS |
| Invariant 7 | `git diff HEAD --stat -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md` | **0** | 16 insertions, 0 deletions |
| Invariant 7 | `git grep -c 'LESSONS.md' -- <RID>` and same at `77e428d` | **0** / **0** | 12 = 12 |
| Invariant 3 premise | `head -1 .gitignore`; `git ls-files .agent-work \| wc -l` | **0** | old premise was indeed false (3067 tracked) |
| Tombstone | 5 independent `grep -n` calls | **0** ×5 | all five clauses present |
| Line endings | Python byte measurement over all 23 changed files + 14 unchanged | **0** | 23/23 100% CRLF, zero mixed |
| Red-proof A | library repoint of `RETIRED_NAME_CENSUS_PATH` | **0** | 0 → 53, exactly-covering |
| Red-proof B | six-property decoy suite | **0** (all 6 PASS) | see below |
| Parser claim | read `scripts/collect_feedback.py` | **0** | keys on the literal `Lesson` |
| Suite | `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | **1** | 5 failed, 1619 passed, 2 skipped |
| Fowler | `python verify_fowler_pass.py <record>` | **0** | 12 smells, 1 flagged, 3 overridden |

### My own red-proof — two independent ways, neither replaying the implementer's

**(A) Read-only library repoint.** Importing `scripts/verify_retirement.py` and pointing
`RETIRED_NAME_CENSUS_PATH` at a nonexistent file takes the scan from **0 → 53** violations, all on the
retired-name leg, distributed exactly as the table above. The decisive property: the census is
**exactly-covering** — 53 approvals against 53 fired content-hits, **zero dead approvals and zero
uncovered lines**. No slack in either direction, so the census can neither be hiding anything nor
carrying an unreviewed licence. This mutated no file.

**(B) A six-property decoy suite of my own construction.** All six PASS:

1. an unapproved retired name **fires** on both planted lines;
2. approving line 1 exactly **silences only line 1**;
3. a **reworded near-miss** approval suppresses nothing;
4. the same line text approved under a **different path** still fires;
5. the **PATH half fires** despite an explicit approval entry written for it;
6. a **reasonless** approval is refused, and the error names the **right** census.

Properties 3, 4 and 5 are the direct answer to "was the leg weakened into a pattern allowlist" — it
was not. Approval is keyed on the exact `(path, normalized line)` pair, and a verbatim re-commit of a
retired file or skill directory can never be reasoned around. Decoy trees removed; `git status`
confirms the worktree unchanged. **No repo file was mutated at any point in this review.**

### Line endings — the trap runs in both directions

Measured in Python bytes as instructed. All 23 changed files are **100% CRLF**, zero lone-LF, zero
mixed. Worth recording for the next gate: comparing against `git show 77e428d:<file>` reports *every*
file as "changed LF→CRLF", because `.gitattributes` sets `* text=auto` so blobs are stored LF by
design. I re-derived the baseline from the **worktree** instead — 14 unmodified tracked files sampled,
14/14 CRLF. CRLF is the worktree norm and every changed file matches it.

### The suite — I agree, and I can sharpen it

`5 failed, 1619 passed, 2 skipped, 549 subtests passed`, exit 1. The 5 is 3 test-level failures plus 2
subtest entries for the same test. **All three are working-tree-vs-HEAD artifacts, not masked
regressions**, re-derived by me:

1. `test_canon_is_clean` **XPASS(strict)** — caused *by* the deliverable: the guard now exits 0, so the
   strict xfail inverts. Its own reason string says `#447 g6 removes this marker`. g6's to close.
2. `test_canon_episode_store_untouched` — I read the assertion text itself:
   `AssertionError: canon episode store is dirty: M episodes/README.md`. The test asserts
   `git status --porcelain episodes/` is **empty**; `episodes/README.md` is the only file under
   `episodes/` differing from HEAD, and invariant 3 mandates editing it. The test's real subject — the
   tracked files under `episodes/active/` — is untouched.
3. `test_a_clean_checkout_differs_only_in_rev_never_in_shape` — the test runs
   `git worktree add --detach <tmp> HEAD` and requires every `TRACKED` file to be byte-identical
   between this worktree and that clean HEAD checkout. `TRACKED[0]` is `scripts/agent_work_root.py`,
   whose docstring invariant 5 mandates editing, so `differed` becomes 2 instead of 1.

**Adding to the Commander's reading:** failures 2 and 3 both compare against **HEAD**, so they
**self-resolve the moment you commit**. Only failure 1 needs an actual code action, and that action is
g6's. Worth knowing before anyone treats all three as g6's backlog.

**Count arithmetic closes exactly:** 1618 baseline + 3 new tests − 2 that moved passed→failed = **1619**.
The 3 new tests confirmed by command (`git diff HEAD -- tests/ | grep -cE '^\+def test_'` = 3):
`test_the_two_censuses_share_one_parser`, `test_every_retired_name_approval_exists_verbatim`,
`test_a_retired_name_approval_suppresses_only_the_line_it_names`. `test_canon_is_clean` does not shift
the passed count because it was an xfail at HEAD and never counted as passed.

### Declared deviations — all three grade out

1. **`harvest` redefined, not deleted.** Allowed by invariant 2. The claim that live uses are all
   write-side **holds in the sense that matters**: no live use reads the store back. Residual coverage
   gap noted in Observations.
2. **`Lesson:` field name kept — VERIFIED AT THE SOURCE**, which is where it could have failed.
   `scripts/collect_feedback.py` maps the lowercased literal label through
   `_PROSE_LABELS = {… "lesson": "lesson" …}`, strips a literal heading prefix with
   `re.sub(r"^Lesson:\s*", …)`, and fingerprints on `_hash12("lesson:" + slug)` from
   `entry.get("lesson")`. Renaming the template field to `**Episode:**` would map to **no key** and
   silently drop every export's stable identity to the slug fallback — exactly as claimed. Invariant 6
   said "accepts an episode id", not "is renamed". **Justified.**
3. **The RID header spells no retired name.** Judged on merit, and it is not merely a workaround for
   the grep count — it is the **better** wording. *"Every surface, writer, gate and role named below
   was retired at issue #447"* is a blanket quantifier covering all of them (both files,
   `apply_lessons_delta.py`, `verify_lessons_applied.py`, `verify_agent_feedback.py`, the
   lessons-auditor role); naming two would have been **under-inclusive** and could imply the rest
   survived. The header is clear without them.

---

## Blockers

**None.**

---

## Out-of-scope observations (6 triage candidates, `tc1`–`tc6`, none blocking)

1. **`tc1` — README's skill table lists 18 while README:31 says the corpus is 19.**
   `constellation-how-to-talk` was never added to the table. **Pre-existing at `77e428d` and not caused
   by g5**: at HEAD the table also carried a phantom `constellation-lessons-auditor` row (directory
   deleted at g4), so 19 rows matched the count *for the wrong reason*. g5 correctly removed the
   phantom, which makes the real omission visible. Note g5 left `SKILL_INDEX.md` **exactly correct** —
   19 entries, all matching a directory on disk. Fix: add a `constellation-how-to-talk` row.

2. **`tc2` — `store_mentions.approved.txt` still carries repeated reason text.** 52 entries share only
   **29 distinct reasons** across 7 groups (×9 `verify_episode_captured.py`, ×5
   `install_constellation.py`, ×5 `CONSTELLATION_OVERVIEW.md`, ×3 `TRIPWIRES.md`, ×3
   `episode_capture.py`, ×3 the two spine templates, ×2 `install_constellation.py`). This is the same
   **structural shape** as the defect g5 was sent to fix — but it is **not that defect here**: I read
   every group and none covers a line instructing an agent to read the store and act on it. Verified
   mechanically that **zero g5-added entries sit under a repeated reason**, and all 7 groups live in
   files g5 never touched, so they were outside this gate's scope. The retired-name census sets the
   better standard at 53/53. Recommend a follow-up.

3. **`tc3` — the redefined `harvest` under-covers a live second sense.** The Admiral's
   *harvest-before-sweep* (`admiral/SKILL.md` step 3, `fleet-doctrine.md`,
   `commander-delegated/SKILL.md`, `global-orchestrator.md`, `stage_feedback.py`) harvests a
   worktree-local `CONSTELLATION_FEEDBACK.md` export into the durable root — **not** "into the episode
   store as episodes". Not a blocker and not a regression: no live use reads the store back, and the
   **old** definition covered *zero* live uses, so this is a strict improvement. But one term now names
   two things, against the repo's one-name-per-thing standard.

4. **`tc4` — cosmetic.** `scripts/agent_work_root.py`'s edited docstring has a ragged wrap
   (`ledger) must be shared by` left on a short line). Content correct; worth a reflow when next
   touched.

5. **`tc5` — Fowler data-clump (non-blocking).** The approval key `(entry.path, entry.mention)` is
   assembled at two sites; a one-line `key` property on `ApprovedEntry` would name the concept once.

6. **`tc6` — seconding the implementer's own open note.** `scripts/stage_feedback.py` still writes an
   `AGENT_FEEDBACK.md` and a `lessons-delta.json` and names `verify_agent_feedback.py`, deleted at g4.
   I independently confirmed it is orphaned. It accounts for **8 of the 53** approvals. Out of g5's
   scope by explicit ruling; worth an issue to retire or update it.

### One judgment call I want visible rather than buried

`docs/CONSTELLATION_OVERVIEW.md`'s new taxonomy row names **`curator rhyme-search`** in its audience
column — the single read-shaped hit in the diff that is not a denial. I did **not** block it:
it is an audience column in a taxonomy table (the same column the retired row filled with "future
Charter refresh, maintainers"), it issues no imperative to any agent, rhyme-search is #308 and
explicitly out of scope, and the row's own description column ends *"a record of what happened, never a
rule to follow"*. But it is the one sentence in this diff closest to the line, and it should be a
conscious call rather than an unnoticed one.

---

## Workflow Feedback

1. **The `advance` verb does not exist for a `survey` controller.** The reviewer SKILL.md instructs
   "`advance`/`record` only once its postconditions pass" and "run the engine's final
   `advance`/`consolidate`", but the engine refuses with `REFUSED: advance is for gated checklists; use
   record`. `record` alone moves a survey. Costs one wasted call per reviewer run and briefly reads
   like a broken lease. The skill should say `record` for surveys.

2. **`start` takes the id positionally, not as `--id`.** Not documented in the skill; discovered by
   `--help` after a failed call. Minor, but it is the first verb after `claim`.

3. **The two handoffs disagree on the scope of `store_mentions.approved.txt`.** The IMPLEMENTER handoff
   scopes it to "(for the §1 reason fix)"; the REVIEWER handoff's close criterion 6 says "**Every**
   census entry in **BOTH** files carries a reason that describes THAT line" and calls it "the criterion
   most worth your time". Read strictly, criterion 6 demands rewriting 7 pre-existing reason groups the
   implementer was never asked to touch. I resolved it by grading the *defect* (a reason untrue of a
   line it covers) rather than the *shape* (a reason shared by several lines), and routed the shape to
   triage. **A future handoff pair should make the reviewer's close criteria a subset of the
   implementer's scope, or say explicitly that a criterion is a survey rather than a gate.**

4. **The line-ending guidance was right but incomplete, and the gap is a real trap.** The handoff warned
   that `grep -c $'\r$'` is unreliable. It did not warn that the *obvious* Python check — comparing the
   worktree against `git show <rev>:<file>` — is **also** wrong, and wrong in the alarming direction: it
   reports all 23 files as corrupted, because `.gitattributes` sets `* text=auto` so blobs are LF by
   design. The correct baseline is unmodified files **in the worktree**. Worth adding to the constraint
   text; it very nearly produced a false BLOCK.

5. **The handoff's "13 new store mentions" needed reconciling.** `git diff` shows **18** added entry
   lines; 13 is the count under the new `#447 g5` block header, with 5 more being rewrites of removed
   entries elsewhere in the file. Both numbers are honest, but the reviewer has to derive the
   difference. Naming the basis ("13 under the new block; 18 added lines net of 3 removed") would save
   a step.

6. **Positive, worth keeping.** The implementer recording the `stage_feedback.py` residue as an open
   note *inside the census header* — rather than silently approving it or quietly dropping it — is
   exactly the behaviour that makes a reason-carrying census trustworthy. It is what let me confirm the
   claim in one `git grep` instead of auditing 8 approvals from scratch.
