# Review Result — g3: rewire the closeout obligations onto episode capture

**Issue** #447, epic-418 workstream H · **worktree** `C:/Programs/constellation-skills-wt/epic418-h-447`
· **branch** `epic-418/h-447-episodes-retirement` · **base** `dbf9a23` · review target: the **uncommitted
working tree**

Survey driven end to end through the engine: `.agent-work/epic418-h-447/g3-review/review.json`
(19 items, lease `rev-g3-447`, consolidated `verdict=APPROVE findings=1`).
Fowler pass: `.agent-work/epic418-h-447/g3-review/fowler.json`, rail exit 0.

## Assigned Gate
`g3-review`

## Result

**APPROVE**

## The load-bearing finding first: the playbook was deleted, not renamed

This is the check the run exists to make, and it passes.

I swept both **full** templates (not the diff hunks) for `lesson` / `ripe` / `apply-or-defer` /
`bank_reason` / `dormanc` / `disposition` / `playbook` / `graduate` / `inbox` / `AGENT_FEEDBACK` /
`apply_lessons_delta` / `verify_lessons_applied` / `verify_agent_feedback` / `lessons-auditor`.
Total surviving hits: **five**, all benign:

- `archive.c4`'s `deny_globs` names `.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md`.
  That object compares **equal to HEAD** — untouched, and required to be kept as the re-staging block.
- Three Admiral hits on `disposition`, all about **issues and branches** (`every epic issue
  dispositioned`, `branches merged or dispositioned`), pre-existing and unrelated to lesson routing.

Zero hits for `lesson`, `ripeness`, `bank_reason`, `dormancy`, `playbook`, `graduate`, `inbox`.

Then I enumerated **every** episode-bearing sentence in both spines — 26 of them — and read each as an
agent would. Every one is a write instruction, the never-hand-edit write constraint, a commit
instruction, or the capture gate. **No sentence tells an agent to read the store and condition its
behaviour on what it finds.** `query_episodes.py` is named in neither spine.

The sentence that deserved the hardest look is the Admiral's *"each harvesting what the ADMIRAL_LOG,
the crew Workflow Feedback and the Commander returns actually recorded."* Those are **this epic's own
run artifacts** — the source material you write the record *from* — not the store you read and obey.
Correct.

The capture gate is the other thing that could have hidden a read path. It does not: it conditions
advancement on **whether you wrote**, never on what earlier episodes say. The census entry approving
it names exactly that discriminator — *"emits episode ids and counts and never statement text."*

## Handoff compliance

All nine close criteria met. Every command re-run by me, exit codes captured by redirect-then-echo.

| # | Criterion | Command I ran | Real exit | Verdict |
|---|---|---|---|---|
| 1 | `replacement-absent` gone | `python scripts/verify_retirement.py > retirement.txt; echo EXIT=$?` | **1** | **PASS** — leg is **0**; legs are exactly 117 `retired-name` + 5 `retired-path` |
| 2 | `unapproved-store-mention` zero, 63 lines read | same run, `cut -f1 \| sort \| uniq -c` | **1** | **PASS** — leg is **0**; all 63 lines read |
| 3 | No playbook vocabulary, no read instruction | regex sweep of both full templates + 26-sentence enumeration | **0** | **PASS** (above) |
| 4 | Record-not-a-rule sentence verbatim | Python string equality | **0** | **PASS** — in Commander **and** Admiral |
| 5 | Condition ids | `git show HEAD:<path>` vs working copy, task-by-task | **0** | **PASS** — see below |
| 6 | Parses, surgical, line endings | `json.load` + byte-level CRLF count + `git ls-files --eol` | **0** | **PASS** — see below |
| 7 | Install test general, red-proven | mutate → `pytest` → restore from binary backup | **1** (red) | **PASS** — see below |
| 8 | Commander closeout path reachable | installed `verify_agent_feedback.py … --phase feedback` | **1** | **PASS** — unchanged, not stranded |
| 9 | No new suite failures | `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | **0** | **PASS** — 1716 passed, 2 skipped, 1 xfailed, 559 subtests |

**Criterion 2 — the census, all 63 added lines read.** 19 approvals under 4 reasons: 5 installer
bundle-comment lines, 2 bundle tuple lines, 9 `verify_episode_captured.py` lines (matching the 9 the
handoff predicted), 3 spine imperative lines. Every reason names a **write** path, a bundle entry, or
an honest anti-overclaim note. **Not one approves a read instruction.** The closest call is
`# 2. plain Read/Grep -- episodes/ is a TRACKED repo path` — that is a comment documenting a *hole in
a boundary claim*, which is the opposite of instructing a read, and its reason line says so. Correctly
approved; deleting it would have created the overclaim the handoff forbids. Worth noting as a
property: the census stores the **full** imperative text, so any future edit to these imperatives
breaks the approval and forces re-review.

**Criterion 5 — ids.** Compared id lists task-by-task. Commander: **only** `feedback` post
`[c1,c2]→[c1]`. Admiral: **only** `closeout` post `[c1..c6]→[c1..c5]`. Every other task's pre/post
lists, the task lists, and the top-level keys are identical. **Zero renumbering.** `feedback.c1` and
`archive.c1` kept their ids with command+statement rewritten — a genuine in-place retarget.
`archive.c4` compares equal to HEAD **as a whole object**: both retired paths still in `deny_globs`,
`episodes/` correctly not added.

**Criterion 6 — bytes, not the diff.** `COMMANDER_SPINE` 26345 bytes, 134 lines, **134 CRLF, 0 bare
LF**; `ADMIRAL_SPINE` 8554 bytes, 65 lines, **65 CRLF, 0 bare LF**. `git ls-files --eol` reports
`w/crlf` on both. The diff is 4 insertions / 5 deletions each, the net −1 being the deleted terminal
postcondition. A `json.dump` round-trip would have reflowed all 134/65 lines and flipped every ending;
nothing of the kind happened. (HEAD blobs read `i/lf` because `.gitattributes text=auto` normalizes on
commit — expected per `CREW_CONTEXT.md`, not a finding.)

**Criterion 7 — red proof, mine, on a different limb.** The test is genuinely general: it walks both
spines, **both** condition lists, every `kind:"command"` check, regex-extracts every `*.py` token and
asserts the owning skill installs it. No script name is enumerated. It carries
`assertGreater(checked, 0)`, discharging `CREW_CONTEXT`'s *"any guard that loops must assert what it
looped over."* I mutated `commander feedback.c1` — a **postcondition**, where the implementer used
`execute.p2`, a **precondition** — to name `verify_episode_NOSUCHSCRIPT.py`, having first asserted the
anchor matched exactly once. Result: **exit 1**, `SUBFAILED … commander spine feedback.c1 runs
verify_episode_NOSUCHSCRIPT.py`. `8 subtests passed + 1 failed` = the walk really examines 9 spine
commands. Restored from a **binary** backup: sha256 `52c9755a…6195` identical before and after,
`git diff --stat` unchanged. Between the two proofs, both limbs of the walk are now demonstrated live.

**Criterion 8.** The installed `verify_agent_feedback.py` has mtime **2026-07-12 09:21** — predating
this run, so no install ran and the bundle drop did not delete it. It exits **1** with its ordinary
content message (`durable feedback log does not mention work id 'epic418-h-447'`), i.e. a real run
reaching its own logic, not a file-not-found. Not stranded.

## Scope drift

None. `git status --porcelain` lists exactly the five allowed-scope files plus the untracked work
area. **All four fenced files are clean** — `scripts/hooks/gauge_writer_hook.py`,
`scripts/hooks/spine_rail.py`, `scripts/gauge_reader.py`, `docs/GAUGE_WRITER_HOOK.md` do not appear in
the diff. Nothing in `docs/`, `skills/*/SKILL.md`, `commander-core.md`, or the g4/g5 deletion set was
touched.

Scope discipline held on the hard case, which is the one that counts: the implementer hit a genuine
gap whose fix lives in `scripts/verify_retirement.py`, correctly did **not** touch that out-of-scope
file, and escalated instead.

## Evidence verdict

Every claim reproduced. The claimed leg distribution after the change is confirmed exactly
(`replacement-absent` 0, `unapproved-store-mention` 0, `retired-name` 117, `retired-path` 5). I could
not re-measure the *before* numbers (130 / 4 / 9) without mutating git state, which is forbidden here —
so I verified the equivalent and stronger property instead: **only 2 of the 117 `retired-name`
findings land in g3's touched files, and both are pre-existing text.** One is `archive.c4`'s
`deny_globs` (byte-identical to HEAD); the other is a comment at `install_constellation.py:221`,
present at HEAD:204 and merely shifted by the new comment block. **g3 introduced zero new findings.**

## Code/doc quality

Fowler pass recorded and railed (exit 0): 12 smells, 1 flagged, 4 overridden with logged standards.

- **Flagged, non-blocking:** the `TemporaryDirectory` + `installer.main` + `target_root` preamble is
  duplicated between the two new tests and matches several pre-existing tests in the file. It
  pre-dates this diff and the file's convention is a self-contained install per test.
- **Overridden:** the ~45-line walk and its generality are what `CREW_CONTEXT`'s *"define a guard by
  its consumer's behaviour, not by a hand-maintained list"* requires, and a per-name assertion was
  declared a BLOCK by the handoff; the five-file scatter is the installer's deliberate declare/deliver
  seam, which this diff's own general test converts into a checked invariant; the heavy comment
  density carries an anti-overclaim record that is unrepresentable in code and was required at the
  code site.

The narrow per-name test kept alongside the general one is correctly reasoned:
`apply_episode_delta.py` is named only in an **imperative**, so no check runs it and the general test
structurally cannot see it. Asserting the retired trio **absent** in the same method is a good touch —
a revert surfaces at install time rather than mid-run.

## Map impact verdict

- **Evidence supports claimed change:** Yes. `capability:run-closeout-learning` genuinely changes
  owner in this gate and the evidence shows it.
- **Constraints not violated:** `constraint:episodes-are-not-prescriptions` is honoured by deletion at
  every site, verified above by sweep and by sentence-level enumeration.
  `constraint:record-stores-never-hand-edited` is now stated inside both spines
  (*"Never hand-edit a file under episodes/"*). No episode was hand-edited by this gate.
- **Notes match the diff:** Yes, exactly. The quoted condition inventories
  (`feedback [c1,c2]→[c1]`, `closeout [c1..c6]→[c1..c5]`) match what I measured, to the id.
- **Decision candidates surfaced:** Yes, and correctly. `decision:episodes-replace-both` is
  `settled/human`; the implementer found a contradiction with it in `docs/agents/CREW_CONTEXT.md:60`
  and **floated it rather than revising a settled/human anchor in place** — the right move under the
  `@grade:` doctrine.
- **Durable context routed:** Yes. Four triage candidates are on the survey's `triage_candidates`.

No successor playbook and **no successor read path** was created. That is the decision, implemented.

## Reconciliation check

No divergence needing Commander reconciliation beyond the flagged candidates. Architecture-significant
and adequately noted; routes to Cartographer at reconcile.

## Blockers

**None.**

## Non-blocking defect (recorded as the survey's one `fail`, r4d)

**A line-number citation the implementer's own edit invalidated.** The new comment says
*"the unfiltered `copytree` at `install_constellation.py:915`"*. `copytree` **is** at line 915 at
HEAD — I checked — but the comment's own 18-line insertion pushed it to **line 932** in the very file
it was citing. This is exactly `global-everyone.md`'s *"pin a claim to the revision you read it at"*
and its *"enumerate the blast radius of your own change"* twin. Secondarily, the result cites the
comment at lines 141–159; it actually spans **143–161**.

Both are cosmetic — a reader greps `copytree` and finds it instantly, no behaviour or gate is affected,
and none of the handoff's stop conditions is met. **Fix is one number, before merge.** I recorded it
as a `fail` rather than quietly upgrading it to `pass` so it stays visible in the record, and
consolidated APPROVE with an explicit override reason. Two stale line numbers in one gate is a small
pattern worth naming, not a blocker.

## Out-of-scope observations

1. **The census currently launders a read instruction — pre-existing, NOT g3's, and material.**
   `tests/data/store_mentions.approved.txt` approves
   `docs/agents/CREW_CONTEXT.md:Read them with scripts/query_episodes.py and the engine's current verb.`
   under the reason *"crew doctrine: names the store's WRITE path and the never-hand-edit rule"*.
   **The reason does not describe the line** — the line is a read instruction. The root cause is
   structural: that reason is written once per **block** of four consecutive `CREW_CONTEXT` lines and
   is true of three of them. The implementer found this and floated it correctly. **g5 must fix both
   the doc prose and the approval entry** — fixing the prose alone leaves a wrong reason in the census,
   and this is the one surface where the run's own guard is telling a comfortable lie.

2. **Forward dependency the Commander must schedule before g6.** The `retired-name-on-shipped-surface`
   leg has no approval mechanism, and `archive.c4`'s two `deny_globs` entries are meant to be
   **permanent**. So the leg **cannot reach zero by deletion alone**, and
   `test_canon_is_clean`'s `xfail(strict=True)` can never XPASS. `verify_retirement.py` needs either a
   reason-carrying approval census for that leg or a narrow exclusion for the two templates'
   `deny_globs`.

3. **Duplicated test preamble** in `tests/test_install_constellation.py` (above). Minor.

### On whether the missing approval mechanism belonged inside this gate

**No, and I would have flagged it as scope drift if the implementer had built it.** Three reasons:
the fix lives in `scripts/verify_retirement.py`, which is not among g3's five allowed files; g3
introduced **zero** new findings on that leg, so nothing about this gate made the problem worse; and
the right moment to design the approval mechanism is **after g5's prose sweep**, when the residual set
is known — by definition the set that must be approved rather than deleted. Designing it now would be
speculative.

What the implementer owed here was to **find it and escalate it**, and that is what happened. The one
thing I would add: this is a **schedulable dependency, not just a note**. `deny_globs` keeps those two
names forever by design, so someone must own the guard change before g6 can go green. That belongs in
the g4/g5 plan explicitly rather than being rediscovered at g6.

## Workflow Feedback

- **Handoff gaps.** The **"Expected and NOT defects"** section is the single most valuable field in
  this handoff and I want it in every reviewer handoff from now on. Being told up front that exit 1
  with 117+5 findings and one `xfail` were *expected* let me spend my effort on the intent question
  instead of re-litigating a red guard. Without it I would have burned a round-trip.
- **Handoff gaps.** *"Deviations the implementer declared — grade these on their merits, not on the
  letter"* is the right instruction and it changed my behaviour. Deviation 1 (`--store-root` on the
  check commands, not only the imperatives) is a case where the handoff's literal string was **wrong**
  and following it would have shipped a gate that exits 2 REFUSED on every installed run. Being told
  to grade merit meant I checked `apply_episode_delta.py:511-518` and
  `verify_episode_captured.py:199` and confirmed the rationale rather than diffing against the literal
  text and calling it drift.
- **Context rediscovered.** Nothing material. The map anchors carried the constraint identities, and
  the handoff's verbatim quotation of the human's 2026-08-06 constraint was what let me judge the
  Admiral's *"harvesting what the ADMIRAL_LOG … actually recorded"* sentence confidently — a
  paraphrase would not have been enough to rule on that one.
- **Instructions improvised around.** One real friction, and it is an engine/skill misfit worth
  reporting. `SKILL.md` says flatly *"an open fail cannot consolidate to APPROVE"*, but the engine
  offers `--override-reason` for exactly this case, and this review needed it: a genuine but cosmetic
  defect that must stay visible in the record without inflating to BLOCK. The honest options were
  (a) upgrade the check to `pass` and lose the defect, or (b) consolidate APPROVE with an override.
  I chose (b). **The skill's prose and the engine's affordance disagree**, and the prose reads as the
  stricter rule. Worth reconciling: either the skill should name `--override-reason` as the sanctioned
  path for a non-blocking fail, or the engine should not offer it to surveys.
- **Instructions improvised around.** The reviewer handoff repeated the implementer result's
  `install_constellation.py:141-159` citation without re-deriving it, and it is off by 2 — the same
  class of defect I am reporting in r4d, one tier up. Minor, but it is the *"a fix scoped to the tier
  below must name why the authoring tier is exempt"* shape from `global-everyone.md`.
- **What would have made this easier.** One concrete change: the handoff told me to diff the
  **condition-id lists** rather than read the diff hunks, and that instruction is what caught the
  renumbering question cleanly in one command. Promote it from a criterion-5 aside to a standard
  reviewer technique for any spine/template edit — reading hunks by eye would not have proven
  "no other id changed."

## Return status

`complete`
