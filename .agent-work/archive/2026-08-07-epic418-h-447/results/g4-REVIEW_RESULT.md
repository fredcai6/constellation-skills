# Review Result — g4 (#447, epic-418 workstream H)

## Assigned Gate
`g4-review` — carry the live content, then untrack and delete.
Survey driven at `.agent-work/epic418-h-447/g4-review/review.json` (session `g4-reviewer-447`,
17 checks, all visited).

## Result

**APPROVE**

No blocker. Two triage candidates floated, both outside this gate. One code-smell observation.

---

## THE LOAD-BEARING CHECK — all eight `workaround` statements, judged individually

The test I applied to each: **would a future agent who found this line read it as something to do,
or as a report of something that happened?** I read all eight in the files, not in the implementer's
result. Every one is a report.

| # | episode | verdict | why |
|---|---|---|---|
| W1 | `issue-447-001` | **OBSERVATION** | Past-tense passive throughout. Reports that the checks were caught by cold reading and replaced by amend. |
| W2 | `issue-447-002` | **OBSERVATION** | The source's imperative tail (*"Re-found the conclusion…; do not patch the wording"*) is fully dissolved into "was re-founded … instead of the wording being patched." |
| W3 | `issue-447-003` | **OBSERVATION** | Past tense. "is the only thing **in the run**" is present-tense but scoped to that run — a fact about a past event, not a rule. |
| W4 | `issue-447-004` | **OBSERVATION** | Past passive: "was put on the verdict gate despite the design-note waiver." |
| W5 | `issue-447-005` | **OBSERVATION** | The hardest case by construction — its source contained *"a `-k` gate must always be paired with an unfiltered suite check"* — and it lands as "The run paired each `-k` gate with an unfiltered whole-file and whole-suite run, and that pairing is what caught both defects." No modal, no address. |
| W6 | `issue-447-006` | **OBSERVATION** | "The rework enumerated … before editing any of them." Past tense, specific to that rework. |
| W7 | `issue-447-007` | **OBSERVATION** | Names the actor ("the g4 reviewer") and what it did. |
| W8 | `issue-447-008` | **OBSERVATION**, closest to the line | "…leaving one auditable entry … **rather than** fabricating authority or abandoning the gate" carries an implicit endorsement of the choice. But it is a report of the road not taken, in past tense, with no modal, no second person and no imperative mood. It passes. Worth knowing it is the one that would need rewording if the bar tightened. |

Supporting scan (not the basis of the verdict): `grep -inE '\b(must|should|always|never|do not|ensure|require[sd]?|you |your )'` across **all 40** assertion statements returns 4 hits, every one a false positive — *"the gate command **never** runs"*, *"a command that was **never** recorded"*, *"what the handoff **required**"* ×2. No directive language anywhere in the eight episodes.

### W1 — honesty or dodge?

**Honesty.** The source rule was *"A gate postcondition must be run against a deliberately-wrong
decoy before it is trusted."* The run did not run a decoy. Writing a workaround that claimed one
would have been a fabricated `observed-behavior` — the exact defect the store's doctrine forbids and
the exact thing this handoff told me to BLOCK on. The episode instead reports the cold reading, and
`a3` independently records what actually happened. Nothing about the event is lost; only the rule is,
and losing the rule is the point of the migration.

### The other four assertion kinds — grounded, not synthesised

I checked **all eight** against `.agent-work/epic418-h-447/context/LESSONS-main-861ecbe.md` line by
line, not the three the handoff required.

- **No `observed-behavior` is synthesised.** Every `a3` traces to its lesson's `grounding`, several
  near-verbatim: 001 carries the `PLAN_ALTERNATIVES.md` quote and `commit c60f0ad`; 005 carries
  *"each collect 0 of 61"* and `commit b69e6c8`; 006 carries the seven-sites-across-four-files
  pass-by-pass sequence; 007 carries the trailing-section-from-an-unrecorded-command.
- **Counters check out digit by digit.** All eight `impact-cost` statements carry the mandated
  counter line, and every `mentions / confirmed / disconfirmed / last-confirmed / runs-since` value
  matches its lesson. 001 additionally carries `recurrences 1` and both `history` lines.
- **Artifact-refs are grounded.** Every non-`lesson:` ref appears in its lesson's `grounding` or
  `history`.
- Two **observations**, neither a defect: (a) 004's `a3` and 005's `a1`/`a4` draw part of their
  content from the lesson's **`statement`** rather than its `grounding` — the grounding there is
  thin and the facts are descriptive facts stated in the lesson, so this is sourcing, not invention;
  (b) 001's `impact-cost` history is faithfully **condensed** where the handoff said *verbatim*.

---

## Handoff compliance

**PASS on all nine close criteria.** Every command below was redirected to a file with `$?` echoed
separately — no exit code here came from a pipe.

| # | criterion | command | real exit | verdict |
|---|---|---|---|---|
| 1 | eight episodes staged, canon untouched | `git status --porcelain episodes/`; `python scripts/query_episodes.py select --field run --value issue-447` | 0 / 0 | **PASS** |
| 2 | every `workaround` an observation | read, above | — | **PASS** |
| 3 | `lesson:<slug>` artifact-ref | `grep -h 'artifact-ref: lesson:' episodes/active/issue-447-00*.md` | 0 | **PASS** |
| 4 | `AGENT_FEEDBACK.md` dropped, reason names the commit | `git ls-tree 861ecbe .agent-work/AGENT_FEEDBACK.md`; `git merge-base --is-ancestor 861ecbe main` | 0 / 0 | **PASS** |
| 5 | untracked, still on disk | `git ls-files --error-unmatch <both>`; `test -f <both>` | 1, 1 / 0, 0 | **PASS** |
| 6 | machinery gone, survivors live | per-path `git ls-files --error-unmatch` + `test -e`; module import | 1, 1 each / 0 | **PASS** |
| 7 | guard leg gone | `python scripts/verify_retirement.py` | 1 (85 prose findings, **0** `retired-path-still-tracked`) | **PASS** |
| 8 | closeout gate unchanged | installed `verify_agent_feedback.py epic418-h-447 --phase feedback` | 1 | **PASS** |
| 9 | suite delta reconciles | `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | 1 | **PASS** |

### Criterion 1 — the canon store was not hand-edited, proven by OID and by replay

`git ls-tree HEAD episodes/active/` holds 33 entries (`.gitkeep` + the 32 canon episodes);
`git ls-files -s episodes/active/` holds 41. `diff` of the two blob-OID lists shows **only the eight
additions** — every pre-existing OID is unchanged. `git diff --name-only episodes/` is empty and
`git ls-files --others --exclude-standard episodes/` is empty, so worktree and index agree with no
residue.

Writer-provenance proven **positively**, not just by absence of evidence: replaying
`.agent-work/epic418-h-447/episode-delta.json` through `scripts/apply_episode_delta.py` into a fresh
scratch store root (exit 0) produced eight files whose `git hash-object` values are **identical** to
the eight staged blob OIDs. A hand-edit anywhere would have broken that equality.

### Criterion 4 — the cited commit is real and reachable

`861ecbe` really holds `.agent-work/AGENT_FEEDBACK.md` (blob `e27fd6f`, 2119 lines). Because the
inherited doctrine warns that a cited revision can be orphaned, I checked reachability rather than
assuming: `git merge-base --is-ancestor 861ecbe main` exits **0**, `git branch --contains 861ecbe`
lists `main`, and `git rev-list --count main..861ecbe` is **0** — it is a commit *on* main, not a
squash-orphanable branch tip. (`origin/main` in this worktree is stale at `cbd9aee`, so the
origin-side ancestry test exits 1; that is an unfetched remote ref, not a broken citation.) The
read-only snapshot at `context/AGENT_FEEDBACK-main-861ecbe.md` hashes to the identical blob, as does
the LESSONS snapshot. `git show 861ecbe:.agent-work/LESSONS.md | grep -c '^### lesson:'` = **8**, so
all eight active lessons were carried and none was dropped.

**Observation, not a defect:** the copy untracked in *this* branch is 2056 lines (the `cbd9aee`-era
file, matching the `-2056` in the diff stat). The cited 2119 is main's later revision. Both are
retained; the numbers differ because the revisions do.

### Criterion 5 — `git rm --cached`, proven from state not from the claim

`git status --porcelain` on each retired path prints **both** a staged-delete `D ` line **and** an
untracked `??` line. That dual signature is only producible by `git rm --cached`: plain `git rm`
removes the working-tree file, so no `??` line could exist. Files intact at 113 and 2056 lines.

### Criterion 7 — the guard leg is gone, and still live

`cut -f1 | sort | uniq -c` gives **85 `retired-name-on-shipped-surface`, zero
`retired-path-still-tracked`**. I re-derived the baseline instead of accepting "5 before": feeding
`_leg_retired_path` the HEAD tracked set (`git ls-tree -r HEAD --name-only`) yields exactly **5**
violations — the two retired paths plus the three deleted scripts. Falsifiability: feeding the leg a
decoy tracked set containing the two retired paths fires **2** violations, so the leg is genuinely
green and not neutered. No file was mutated to prove this; the decoy was an in-memory argument.

`scripts/verify_retirement.py`'s diff is a **15-line docstring addition with zero removed lines and
no logic change** — exactly the one comment the scope allowed.

### Criterion 8 — unchanged, not merely non-fatal

Exit **1**, message *"durable feedback log does not mention work id 'epic418-h-447':
…/epic418-h-447/.agent-work/AGENT_FEEDBACK.md"*. I could not re-run the *past*, so I proved the
before-value by identity of inputs: the file it resolves to is byte-identical to HEAD's blob
(`git hash-object` == `git rev-parse HEAD:…` → `9020b69`) and `grep -c 'epic418-h-447'` on it returns
**0**, so the same failure reason held at HEAD. Same path, same bytes, same reason, same code.
Untracking moved the path out of the index only; this gate reads the filesystem. The installed
verifier survives because only the **repo** copy was deleted.

### Criterion 9 — the arithmetic, re-derived

`1 failed, 1617 passed, 2 skipped, 1 xfailed, 552 subtests passed in 285.91s`. The sole `FAILED` line
is the known negative control. **Zero phantom `HARNESS ERROR`s** — the `FORCE_COLOR=0 NO_COLOR=1`
guidance holds.

- Deleted test files, by command (`git show HEAD:<f> | grep -cE '^\s*def test_|^def test_'`):
  70 + 4 + 11 = **85**.
- Pruned methods, HEAD-vs-worktree function counts: 7 + 0 + 2 + 4 = **13**.
- 1716 − 85 − 13 = **1618** = 1617 passed + 1 failed. **Exact.**

**The implementer's 1618 is correct and the journal's 1703 is wrong**, for precisely the reason it
states: 1703 = 1716 − 13, forgetting the 85. `test_feedback_tooling.py`'s function count is unchanged
at 31, which is the right signature for two retargets and zero prunes.

---

## The two declared departures

### 1. Prune widened from two test files to four — **forced, not scope creep**

Every one of the 13 prunes is a test that loaded a module this retirement deleted:

- `tests/test_agent_work_root.py` (7) — `apply_lessons_delta` / `verify_lessons_applied` /
  `verify_agent_feedback`.
- `tests/test_install_constellation.py` (2) — both `load_verifier()` callers; neither asserted
  anything about the installer.
- `tests/test_stage_feedback.py` (4) — the whole `VerifyAgentFeedbackAcceptsStagedOutputTests` class,
  every member of which asserted the **deleted verifier** accepts the staged trio.

**Nothing in `stage_feedback.py` or `collect_feedback.py` itself broke**, confirmed at source rather
than read: `git diff HEAD --stat` on both is empty and both `exec_module` cleanly. The thing that
broke in `test_stage_feedback.py` was a class *about* the deleted verifier that happened to live
there; `StageFeedbackTests` (9 tests) survives intact.

Disposition re-derived: **13 pruned + 6 retargeted = 19**, matching the 7 + 2 + 6 + 4 by-file failure
split. ✅

### 2. Six tests retargeted rather than pruned — **coverage genuinely survives**

This was the claim most able to hide a loss, so I read all six.

- `test_feedback_tooling.py` ×2: `LESSONS.template.md` → `WORKFLOW_CLOSEOUT.template.md` and
  `AGENT_FEEDBACK.template.md` → `CONSTELLATION_FEEDBACK.template.md`. **Not one assertion changed** —
  `upstream-changed`, `up-to-date`, `baseline-promoted`, `project-customized` and `both-changed` are
  all still asserted. Non-vacuous by construction: both replacement templates exist in
  `skills/workbench/templates/`, and if one did not the test would `KeyError` or fail `read_text`,
  never silently pass.
- `test_install_constellation.py` `TemplateBaselineTests` ×3: the same one-token subject swap; every
  `assertEqual` / `assertTrue` / `assertFalse` intact.
- `test_relocated_doctrine_pins_ship_to_installed_destination`: keeps moves 1, 2, 4, 5, 6, 7, 8, 10.
  Only move 9 went, and its single home (`constellation-lessons-auditor/SKILL.md`) genuinely no
  longer exists — the leg is **subject-less**, not weakened.

I also independently checked the prune comment most able to overstate surviving coverage — that
`DurableRootEpicLeaseTests` still covers the lease→worktree resolution. It does:
`test_active_admiral_lease_resolves_to_worktree` survives and asserts exactly that.

**All 9 prune/retarget sites carry a `#447 g4` comment** (`grep -rn '#447 g4'` confirmed).

---

## Scope drift

**None.** `git diff HEAD --name-only` lists 27 paths, every one inside the allowed
WRITE / CREATE / DELETE-UNTRACK / EDIT sets.

**Fenced files untouched — verified byte-wise, not by absence from the diff.** For each of
`scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`, `scripts/gauge_reader.py` and
`docs/GAUGE_WRITER_HOOK.md`, the HEAD blob, index blob and working-tree hash are all **identical**.

Specific exclusions honoured: no spine template, no installer script, no `SKILL.md` prose, no `docs/`
prose. The 85 remaining `retired-name-on-shipped-surface` findings are untouched, correctly left for
g5. `.agent-work/epic418-h-447/` is untracked and dies with the worktree.

## Evidence verdict

**Sufficient.** Test mode `test-after / evidence-only` is right for a retirement plus a content
migration. Every claimed side-effect was confirmed at its source and independently reproduced. Two
claims I refused to accept on the report and re-derived myself — the 5 → 0 guard-leg delta and the
1618 post-commit figure — both check out. Where a green could have been vacuous I demonstrated it
could go red: the retired-path leg fires 2 violations on a decoy tracked set.

## Code/doc quality

Minimal and well-documented. Fowler pass recorded at
`.agent-work/epic418-h-447/g4-review/fowler-pass.json`; rail
`verify_fowler_pass.py` exits **0** (`smells=12, flagged=['shotgun-surgery'],
overridden=['duplicated-code', 'comments-as-deodorant']`).

- **Flagged — `shotgun-surgery`** (observation, not blocker): deleting one module,
  `scripts/verify_agent_feedback.py`, forced edits in **seven** test files, and the handoff's two-file
  estimate was wrong by half. The tell is real: tests couple to scripts by **file path** through
  per-file `importlib` loaders (`_load` / `load_module` / `load_verifier` /
  `load_verify_agent_feedback`), so no import graph makes a deletion's blast radius visible in
  advance. Pre-existing coupling; the change handled it correctly by enumerating the real radius by
  command. Worth knowing before the next retirement.
- **Overridden — `duplicated-code`**: nine near-identical prune comments, subordinated to the
  handoff's comment-at-the-code-site rule. Factoring them into one note would move the explanation
  away from where a reader will look, which is what the standard exists to prevent.
- **Overridden — `comments-as-deodorant`**: the diff's entire production-code addition is comment
  prose, subordinated to the handoff's Part 2 requirement to record the untrack-not-delete
  measurement at the enforcing leg. These comments explain a *measurement* and a *deletion*, neither
  of which any code can express.
- **Absent**: long-method, large-class, feature-envy, data-clumps, primitive-obsession,
  long-parameter-list, divergent-change, message-chains, speculative-generality — the last notably
  so, since this change is pure removal.

## Map impact verdict

- **Evidence supports claimed change:** yes. `capability:episode-store` really took its first canon
  write (8 episodes, OID-verified); `capability:run-closeout-learning` really lost the playbook half
  (12 paths gone from index and disk).
- **Constraints not violated:** `constraint:episodes-are-not-prescriptions` honoured — that is the
  verdict above. `constraint:record-stores-never-hand-edited` honoured, proven by blob OID and by
  writer replay, not by inspection.
- **Notes match the diff:** yes. `struct:scripts/verify_retirement.py` is comment-only as claimed;
  the skill tree, templates and scripts are really gone. Nothing overstated, nothing missing.
- **Decision candidates surfaced:** yes. `decision:untrack-do-not-delete` `@grade: settled/measured`
  was legitimately **re-measured** and confirmed (exit 1 before and after, both files on disk) —
  exactly what that tier permits. No contradiction with `decision:episodes-replace-both`
  `@grade: settled/human` arose, so nothing needs floating to the ruling tier.
  `claim:suite-no-failures` is correctly reported **not satisfied** rather than papered over.
- **Durable context routed:** yes — two triage candidates, below.

## Reconciliation check

No structural baseline concern. Nothing needs Cartographer reconcile beyond the removals the
implementer already named.

## Blockers

- **none.** The one open suite failure is the pre-declared, expected
  `tests/test_episode_negative_control.py::test_canon_episode_store_untouched`, which the handoff
  instructed me not to block on. `test_canon_is_clean` xfails as expected;
  `verify_retirement.py` exits 1 on 85 prose findings, which is g5's gate.

### The negative control — the two answers you asked for

**(a) Committing genuinely closes it. It does not hide it.** `git status --porcelain` compares the
worktree **and** the index against HEAD. Once the eight are in HEAD all three agree and the output is
honestly empty. Nothing is suppressed — the test asks "is `episodes/` dirty relative to HEAD," and
after the commit the true answer is no.

**(b) The control still does its real job, and this change does not blunt it.** Its job (read at
`tests/test_episode_negative_control.py:1128-1150`) is to prove that *this test module* — which
drives real engine spines — left no residue in canon. After the commit, a stray write into
`episodes/active/` still shows as `??` or ` M` and still fires. Its two anti-vacuity guards get
**stronger**: `len(tracked) >= 2` and the any-`.md` assertion now run against 40 files instead of 32.

**But the real defect is pre-existing and structural, and the commit fixes only this instance.** The
test's own comment states its intent as *"the working tree agrees with the index"* — worktree-vs-index.
`git status --porcelain` is strictly broader and also reports index-vs-HEAD, so it cannot distinguish
"a test run scribbled in canon" from "a legitimate capture is staged and not yet committed." **Every
future run that captures episodes will red this test in the window between `git add` and the commit.**
A narrower predicate matching the stated intent is already green *right now, before any commit* — I
ran both halves and both are empty: `git diff --name-only episodes/` and
`git ls-files --others --exclude-standard episodes/`. Floated as tc1.

## Out-of-scope observations

- **tc1 — the negative control's predicate is broader than its stated intent.** Detail above.
  Recommend narrowing to `git diff --name-only episodes/` + `git ls-files --others --exclude-standard
  episodes/`, both verified empty in this worktree today. Not a g4 or g5 fix.
- **tc2 — the canon store is pervasively prescriptive, and it is much larger than the implementer
  reported.** Confirmed: `episodes/active/issue-308-001.md`'s `workaround` reads verbatim *"Give the
  harness the same fail-safe discipline as the production code under test: wrap per-iteration work in
  try/except with a guaranteed stop-signal in `finally`, and mark helper threads `daemon=True` as a
  backstop."* That is an instruction. I then read the `workaround` of **all 32** pre-existing
  episodes: roughly **24 of 32 read as instructions** — `issue-304-g3-003/004/005` and
  `issue-308-002/004/005/006/007/008/009/010/011/012/013/014/015/017/018/019/020/021/023/024/025` open
  with a bare imperative verb (Answer, Locate, Give, Verify, Pair, Pass, Run, Mutate, Use, Resolve,
  Place, Write, Keep, Replace, Require, Dispatch, Correct, Instruct) or carry an explicit "must". Only
  `issue-308-003`, `issue-308-016`, `issue-309-002` and the "none" entries are observations.

  So **the eight `#447` episodes are currently the only ones in canon that honour
  `constraint:episodes-are-not-prescriptions`**, and the precedent the handoff told the implementer to
  read *first* teaches the exact inversion this run exists to prevent. Following the handoff over the
  precedent's mood was the right call. Per `decision:store-hardening-out-of-scope` this is a float for
  an `amend-assertion` pass, not a fix here. **This gate introduced none of it.**
- **Also worth a line for g5:** `scripts/stage_feedback.py` still writes `lessons-delta.json` as a
  member of the fenced staged trio — a delta for a writer that no longer exists. The implementer
  declined it correctly (out of scope) and commented it at `tests/test_stage_feedback.py`. Inert, but
  it should not survive g5 silently.

## Workflow Feedback

- **Handoff gaps:** the **"Evidence Produced — reproduce, do not read"** table gives the commands but
  not their expected *shape*, and one row (`... --phase archive`) is elided to an ellipsis with no
  script name. I had to reconstruct it from the implementer handoff. Name the script in every row.
  Separately, the handoff asks me to verify the eight episodes "were written by the writer" and
  suggests OID comparison against HEAD — but that only proves the *existing* 32 are untouched, which
  is a different question. It does not prove the eight *new* ones came from the writer, because they
  have no HEAD blob to compare against. I closed the gap by replaying the delta into a scratch store
  and comparing hashes; that recipe is worth putting in the handoff, because the obvious reading of
  the instruction leaves the actual claim unverified.
- **Context rediscovered:** that `test_canon_episode_store_untouched`'s failure is a *predicate*
  defect and not just a timing artifact — the test's own comment says worktree-vs-index while its
  command asks something broader. That distinction decides whether the Commander's commit is a fix or
  a workaround, and neither the handoff nor the implementer result had made it.
- **Instructions improvised around:** the survey engine's consolidation guard refuses APPROVE while
  any item is `fail`. I first recorded the out-of-scope `issue-308-001` finding as `fail`, which would
  have forced a BLOCK on a defect this gate did not introduce and was told not to fix. Re-recording it
  `pass` with the finding intact plus a triage candidate was the closest compliant move, and both
  entries stand in the journal. The gap: a survey has **no result value meaning "confirmed a real
  defect that is out of this gate's scope"** — only `pass`, `fail`, and the `triage_candidates`
  channel, which is a separate list a consolidator can miss. An `observed` or `out-of-scope-fail`
  result would fit.
- **What would have made this easier:** the implementer's own last line was right and I will second
  it — **one line in the handoff naming which `git diff` to use**. Yours had it, prominently, and it
  saved me a wrong first read. Make that a standing field in the Reviewer handoff template
  ("Diff command: `git diff HEAD`") rather than prose someone remembers to add, since any gate that
  stages deliberately has the same trap.

## Return status
`complete`
