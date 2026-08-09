# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch.

- **step**: `execute` (in-progress) · **slug**: **`g8` — 5th pass, TEST-ONLY, in flight**
- **PID**: crew `constellation/issue-456/g8/implementer/attempt-5` running. All others closed.
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/g8-remediate-4-RESULT.md`

## 🟢 RESUME HERE — `g8` build+tests DONE and Commander-verified. Needs re-review.

**Do not touch `scripts/code_map/`.** Three reviews confirmed the production fix
at `1f2b57ab` by direct execution. The hollow-test defect is now **fixed** at
`8ad32efb` (gate removed) on top of `18dc643e` (overflow assertion).

**Commander-verified, the decisive check:** removing the truncation line
(`paragraph = paragraph[:160]`) now takes **4 tests RED**, including BOTH
previously-hollow ones (`test_long_first_paragraph_with_blank_line_and_body`,
`test_dense_paragraph_over_160_chars_no_blank_line`). The identical mutation
previously left all 11 green. Revert byte-clean; selector back to **11 passed,
4 subtests**. No `if len(summary) == 160:` remains; 3 unconditional
`assertEqual(len(summary), 160)` in its place.

**NEXT: dispatch the g8 re-review** (`SendMessage` to the existing `g8-reviewer`,
context intact, after registering `g8/reviewer/attempt-4`). Ask it to re-run its
own two mutations — the remediation-2 revert AND the surgical overflow-drop —
since those are the two it used to prove the tests hollow, and it should confirm
both now bite. Then close the gate.

**Rule this cost five passes to learn: branch on the SHAPE (fixed, known when
the case is written), never on the MEASURED output (the thing under test).**

**Engine bookkeeping still owed for g8** (same trap I hit on g7 — the work ran
ahead of the record): `g8-implement` is still `pending`. Attest `p1`, `start`,
`attach` an `implementer-result`, attest `c1`, `advance`; then `g8-review`
(evidence type `review-result`), then `g8-integrate` (`c1` command re-run by
`advance`; `c2` needs verdict **APPROVE**). Closing selector `-k 'bom or
docstring'` → **11** now, gate baseline was **4**.

**Verified at this boundary:** suite **1838 passed, 2 skipped, 701 subtests,
0 failed**; fresh `build` then `check` **7/7 exit 0**. Invariant holds
character-exact across shapes neither I nor the crew hand-picked (reviewer
checked exact-159/160/161, multi-byte em-dash straddling the cut, CRLF,
whitespace-only, all-blank, leading blank, huge body): **zero content loss**.

### Why g8 took five passes — the run's main lesson
Passes 1–3 were **Commander specification errors**: each brief named the CASE,
so each fix was correct for that case and left the same defect elsewhere.
D3 was **never defined** in any reference material; I defined it empirically,
then scoped the fix to one branch of two. Every round was caught by a reviewer
testing against the **real corpus** while fixtures stayed green.
Pass 4 flipped shape: code right, **proof hollow**. Pass 5 is the same again.
**Carry: state the INVARIANT, not the case; test it against real data.**

### Also owed at close
`tc15` shared-tmp collisions between crews. `tc16` specify-the-invariant lesson.
`tc17` my own four-shape check used word-splitting (reviewer found that throws
false positives on no-whitespace strings and redid it character-exact — my
conclusion held, my method was weaker than I stated); plus the engine note that
a second `consolidate` needs `--override-reason` ONLY for APPROVE-while-failing,
not for BLOCK — undocumented asymmetry.

## SUPERSEDED — earlier g8 history

## 🟢 RESUME HERE — `g7` CLOSED (9/11). `g8` built+verified, needs review.

**Engine:** `g7-integrate -> complete`. `g8-implement` is **still `pending`** — do
NOT skip it: attest `p1`, `start`, `attach` an `implementer-result`, attest `c1`,
`advance`. (I made exactly this mistake on g7 — drove the whole gate and only
opened it in the engine at the close. Ninth Commander error this run.)

**`g8` build state:** committed at `d727ee2f` (BOM) and `06fbc138` (D3).
Commander-verified: suite **1835 passed, 2 skipped, 697 subtests, 0 failed**
(baseline 1831); selector `-k 'bom or docstring'` **8** (gate baseline was **4**,
not the 3 an earlier note claimed — g7 had added a docstring test); fresh `build`
then `check` **7/7 exit 0**; tree clean.

### What `g8` actually fixed, and the trap it walked into
Defect 1, BOM: fixed, fixture with real BOM bytes, RED observed before green.
The crew also found the **same defect in `checks.py`'s `SourceScan`** — the check
itself couldn't parse the fixture. "The check has the defect."

Defect 2, **D3 — and this is the lesson**: `D3` is **named but never defined**
anywhere (`DESIGN_SPEC.md` §203, `ISSUE_456.md` §37 both say only
"wrapped-docstring render split (D3)"). My brief passed the phrase through
unresolved — **tenth Commander error**. The haiku crew said so plainly and
shipped "a defensive fix that may not address the actual defect." It was right:
its `split("\n")`→`splitlines()` change was cosmetic; both still cut at the first
newline. **I resolved D3 empirically:** a summary sentence wrapped across two
physical lines is CUT IN HALF — first line becomes the summary, the remainder of
the same sentence opens the body. Correct rule is PEP 257's: summary ends at the
first BLANK line. Fixed via a shared `_first_paragraph` helper + `doc_summary_of`,
all three call sites converted; no `splitlines()[0]` remains in `extract.py`.

### The haiku measurement (Tommy asked for this)
Handled the mechanical work fine — real fixture, real RED, fast. **Two process
misses, both needing a nudge:** ran only `tests/test_code_map.py` (141) instead of
the full suite, and finished its plan with **no RESULT document** twice. Its own
read: no model-tier friction, the friction was brief specificity — and it was
right, since the D3 ambiguity was mine. Verdict for feedback: **cheap tier is
fine for mechanical work IF the defect is precisely specified and the process
steps are spelled out**; it will not infer an underspecified defect, and a sonnet
crew probably would have pushed back sooner.

## 🔴 SUPERSEDED — `g7` block history (kept for the record)

**Engine state:** `g7-implement` complete. `g7-review` NOT yet advanced — its
REVIEW_RESULT (verdict **BLOCK**) is on disk at
`.agent-work/issue-456/crew-handoffs/g7-review-RESULT.md`, reviewer committed it
at `888a6807`. Build is at `0d1af801` (+ `1c70a0af`, `14197f69`).

**Next commands, in order:**
1. Poll `.agent-work/issue-456/crew-handoffs/g7-remediate-RESULT.md`.
2. Verify independently — suite, both selectors, fresh `build` then `check`, and
   **re-run the crew's own tag-staleness disable attack yourself**.
3. Close the crew: `run_crew.py --verify-result constellation/issue-456/g7/implementer/attempt-2`.
   (Registry gotcha: `recover_crews.py` can say 0 unresolved while a launch is
   REFUSED as duplicate. `--verify-result` is the correct close for a crew that
   finished; `--abandon` misrecords a success.)
4. Re-review via **`SendMessage` to the existing `g7-reviewer`** (context intact)
   after registering `g7/reviewer/attempt-2`. Do NOT self-grade the repair.
5. `g7-review` (attest `c1`, evidence type `review-result`) → `g7-integrate`
   (`c1` command re-run by `advance`; `c2` needs verdict **APPROVE**).
6. Then `g8`, then `gs`. Then reconcile, triage, review, feedback, archive.
   **RELEASE THE LEASE LAST.**

### Why g7 blocked — TWO things, the second bigger than the review scored it

**(a) retire vs alias — RULED: alias.** The crew retired `Assumption:`/
`Constraint:` (TAG_START stopped matching them). The only real corpus is
f1Brainz PR #733 — **4 `Constraint`, 1 `Rejected`, 1 `Rationale`, 0 anchors** —
so retire silently kills 4 of 6 real tags: no error, no warning, invisible to the
detector meant to catch tags going wrong. The spec's survival law ("a tag
survives when a tool visibly consumes it") is not neutral once applied to text
that already exists. Self-inflicted proof: the cull broke this gate's OWN worked
example, forcing a mid-gate substitution in the join test's docstring.
**Tommy was told and can reverse it.**

**(b) THE STALENESS MECHANISM NEVER WATCHED TAGS.** Commander-verified in the
code, not inferred: `extract.run()`'s diff reads only `st["p"] == "anchored"`;
tags emit as `p == "tag"`; `span_hash` is persisted only in `Extractor.anchor()`.
The join test's fixture `_STALE_TAG_SOURCE` gives its function **both** a
`[rate-double]` anchor and a `Rationale:` tag — **the flag fires because of the
anchor**. Real corpus has zero anchors ⇒ not one real tag would ever be watched.
That is critic IF4/TS8's original problem untouched, in the corpus it was raised
to protect, and a **test passing for the wrong reason** — the third variation on
this run of a check that cannot fail. The reviewer scored it as a phrasing
correction; it is not. **Required proof: a test on an entity with a tag and NO
anchor, plus a disable attack on the new emission.**

### One review finding OVERRULED, with reasoning (do not re-litigate)
The reviewer called wall-clock timings in `g7-implement-RESULT.md` a violation of
"the run report carries no timings." That constraint's own rationale is *"so the
determinism diff can cover it"* — it governs `render_report.json`, not
human-facing markdown. My handoff quoted it unscoped, which invited the reading.

### Verified numbers at the g7 build boundary (Commander-run)
Suite **1825 passed, 2 skipped, 692 subtests, 0 failed**. `-k 'comment_tags'`
**18** (baseline 0 by design). `-k 'stale_tag'` **15** (was 14). Fresh `build`
then `check` **7/7 exit 0**. The crew never filled in its own suite number —
backgrounded it, stalled ~20 min on buffered output, unstuck by a `SendMessage`
nudge carrying the figures. Same stall pattern as earlier crews.

### Candidates filed this gate
`tc11` the landing-zone ruling (against `gs`). `tc12` the cull test is honest but
**low-information** — a KEEP outcome was never realistically reachable, so the
decision was really made by author-convergence data, not render necessity;
tc38-family, but about the *decision procedure*. Reviewer also filed: `See:` tags
render as literal text not links; tag/anchor binding-granularity asymmetry.

## ⚖️ HUMAN RULING 2026-08-08 — what of `map/` gets committed at `gs`

Tommy, verbatim: *"middle point sounds fine, I could buy local regeneration, but
if we think we can choose a stable landing zone we should."*

**Ruling: commit the stable landing zone, regenerate the rest locally.** The
criterion is **stability**, not tier depth — pick what does not churn, and prove
it by measurement rather than assertion. This SUPERSEDES the plan-of-record
assumption ("commit the whole tree, owned here") recorded in `gs`'s decision
anchor, which was explicitly marked *pending Tommy*.

**The tree's shape makes this clean.** `map/` is two tiers:
- **Landing zone — 115 files.** `map/INDEX.md` (18KB), `map/ids.jsonl`, and one
  `INDEX.md` in each of the **113** module directories.
- **Body tier — ~3,815 files.** One page per symbol.

The landing zone tracks the **shape** of the codebase (what exists); the body
tier tracks **content** (what it does). A body-only edit — the overwhelming
majority of commits — should not touch the landing zone at all. Adds, removes
and renames do touch it, which is correct and rare.

**`gs` MUST MEASURE THIS, not assume it.** Make a body-only edit to a function,
rebuild into a scratch dir, and diff. The landing zone must come back byte-
identical. If it does not, the landing zone is drawn in the wrong place and must
be redrawn before anything is committed. Do the same for an add and a rename and
record what moves, so the churn a real commit produces is a stated number rather
than a hope. NOTE: `gb` measured a rename touching **217 of 3865** pages — check
how many of those were INDEX pages, since that bounds rename churn in the zone.

`gs`'s original close criterion ("the committed map tree matches a fresh build,
asserted by a rebuild-and-diff") still applies — but now scoped to the landing
zone, and the map-entry-point instruction must still resolve to a file that
exists, which is the whole reason to commit anything at all.

## ✅ `g6` IS CLOSED — `g6-integrate -> complete`. **8 of 11 gates done.**

Closed on an APPROVE from the SAME reviewer that issued the original BLOCK
(resumed with context intact, not a fresh crew). Numbers at close, all re-run by
the Commander: suite **1807 passed, 2 skipped, 684 subtests, 0 failed**; selector
`-k 'stale_tag'` **14 passing** (baseline 0 by design), all 14 ids confirmed to
carry `stale_tag` via `--collect-only`; fresh `build` then `check` **7/7 exit 0**;
tree clean. Commits: build `55b95314`, remediation `cf36071f`.

### The lesson worth carrying: FOUR disable points, not one
The BLOCK was that 9 of 12 tests stayed green when the feature was disabled. The
fix was verified at four independent disable points, deliberately: (1) emission
forced empty in `extract.run()` — the reviewer's original attack, reproduced by
the crew's script; (2) **`span_hash` forced to a constant** — the Commander's own
mutation, chosen because neither the reviewer nor the crew picked it (reproducing
an author's own falsifier proves only that the author's probe works); (3)
`render.py`'s interception and (4) the persistence of `span_hash` onto the
statement — both added by the re-review with predictions stated in advance. Five
negative tests, red at every point, zero survivors. That is what separates a fix
coupled to the feature from one shaped to a known attack.

### Fixed in the rework
`tc7` uncaught `JSONDecodeError` on a truncated leftover `statements.jsonl` — now
takes the bootstrap path with one actionable line, deliberately NOT a silent skip
(a silent skip converts a corrupt store into permanently dead detection).
`tc8` advisory prefix `FAIL` → `ADVISORY`. Severity ruling unchanged and affirmed.

### Still open, filed not fixed
`tc9` **nothing in the routine pipeline exercises the staleness path** — `check`
never calls `render.py`, `deterministic-rebuild` always builds fresh. Design
question about what `check` is for. `tc10` evidence scripts self-check reverts
with `git status --porcelain`, which false-negatives under `core.autocrlf`; TWO
independent scripts hit it in this one gate despite the hazard being documented
in CREW_CONTEXT.md. Fix: `git diff --quiet -- <path>` or blob OIDs.

### Two limits ship with g6, recorded not smoothed over
Detector reports nothing stale here because **zero authored anchors exist** — so
it has only been exercised against a fixture; real validation belongs to `g7`,
which joins on the same slug allocator and needs no rework here. Docstring-only
and comment-only edits are invisible by construction.

## g6 review history (superseded — kept for the record)

`g6-review -> complete` (evidence `e-g6-review-1`, verdict BLOCK, refresh `e-g6-review-2`).
Result at `.agent-work/issue-456/crew-handoffs/g6-review-RESULT.md`; reviewer
committed it itself at `29ba98ff`.

**The blocker:** forcing `stale = []` after the real computation in
`extract.run()` — a whole-feature disable on one code path — left **9 of 12
tests green**, including *every* dedicated does-not-flag test. Only the two
flags-a-real-change tests went red, plus one incidentally. Reverted cleanly,
12/12 restored. tc38/tc47 class: the feature works, its evidence can't fail.

**Three other questions came back answered, not deferred.** Q1 slug-match is a
correctly-deferred `g7` concern. Q3 ran **8 novel mutations the crew did not
choose** — all predictions matched, no accidental behavior, no new defect, so
reformatting immunity holds under attack its author didn't design. Q2 severity
ruling (advisory-only) **stands and was affirmed**; only the text was wrong.

**Filed:** `tc7` uncaught `JSONDecodeError` on a truncated leftover
`statements.jsonl` — a NEW failure mode this gate introduces, real because the
writer has no atomic rename. `tc8` advisory line prints literal `FAIL` while
exiting 0, colliding with the genuine-failure convention. `tc9` **nothing in the
routine pipeline exercises the staleness path at all** — `check` never calls
`render.py`, `deterministic-rebuild` always builds into fresh dirs; the only
exerciser is a human not wiping `.code-map`, an unenforced convention. tc7+tc8
ride the rework; tc9 is a design question for triage.

Reviewer also settled the RESULT doc's 16-vs-12 test count at **12** (drafting
error, nothing dropped) and independently **affirmed** the crew's rename
overrule — over-flag-never-under-flag is the mechanism's consistent posture.

### The rework brief makes the attack the acceptance test
`.agent-work/issue-456/crew-handoffs/g6-remediate.md`. Fix 1 (blocker): a
positive control INSIDE each of the five does-not-flag methods, verified by
re-running the disable attack and requiring all five to go red — a criterion
that can fail. Fix 2: guard the read, actionable message, never silent. Fix 3:
`FAIL` → `ADVISORY`. Plus a citation nit. Explicitly NOT in scope: severity
ruling, rename sensitivity, a routine exerciser (tc9), splitting `run()`.

Dispatch: `python scripts/run_crew.py --dispatch external --work-id issue-456 --gate g6 --role implementer --model sonnet`
Then the **SAME reviewer** re-verifies — do not self-grade the repair.

## NEXT ACTION (superseded above — kept for the g6-implement close record)

**`g6-implement` is CLOSED** — `c1` attested via evidence `e-g6-implement-1`
(refresh-request `e-g6-implement-2`, why `w-22`), `g6-implement -> complete`.
The build was Commander-verified and pushed; the crew committed at `55b95314`.

Now: **dispatch the `g6` review** —
`python scripts/run_crew.py --dispatch external --work-id issue-456 --gate g6 --role reviewer --model sonnet`
with handoff `.agent-work/issue-456/crew-handoffs/g6-review.md` (written).
Then `g6-integrate` on an APPROVE. Then `g7`, `g8`, `gs`.

### What the g6 review handoff asks for — do not let it come back thin

Four questions, in the handoff verbatim: (1) does slug-match really constitute
the "text did not change" half of the rule, or beg the question, given `g7`
introduces prose that can change under a fixed slug; (2) is advisory-only right,
and does printing the literal word `FAIL` while exiting 0 collide with `check`'s
output convention; (3) attack reformatting immunity with mutations the crew did
NOT choose (quote style, line-splitting, default-arg value, statement reorder,
type annotation, literal→expression, loop→comprehension) — reproducing the
author's own falsifier proves only the author's probe works; (4) **the sharp
one** — the crew disclosed that 7 of its 10 "does-not-flag" assertions passed
VACUOUSLY during red. Verify the shipped negatives now have a positive control:
disable flag emission on one path, rebuild, count how many of the 12 go red. If
most stay green they are checks that cannot fail — tc38/tc47 class, BLOCK-worthy.

Also flagged to the reviewer: the RESULT's Scope section says "16 new tests"
while its own Evidence section and my independent run both say **12**.

## `g6` BUILD — what landed, and what the reviewer should attack

Mechanism: `extract.span_hash(node)` hashes an entity's own **AST subtree** via
`ast.dump(node, annotate_fields=False)` with the leading docstring excluded.
`ast.dump` never encodes source text, whitespace or position, so the hash is
immune to reindentation, line-wrapping and blank lines **BY CONSTRUCTION** — not
by a hand-defended normalisation. `extract.run()` reads the PREVIOUS
`statements.jsonl` before overwriting it, diffs span hashes by slug, and emits a
`stale-anchor` statement per changed slug. `render.load_stores()` intercepts it,
surfaces `report["stale_tags"]` in `render_report.json` — **the run report the
reviewer already reads** — and prints an advisory line naming the human action
**without failing the build**.

**Commander-verified:** suite **1805 passed / 2 skipped / 683 subtests / 0
failed** (baseline 1793 + 12 methods, 672 + 11 subtests); closing selector
`-k 'stale_tag'` now **12 passing** where it collected **0 by design**; fresh
`build` then `check` **7/7 exit 0**, `deterministic-rebuild` still `ok`.

**Built against a FIXTURE** (`_make_anchor_repo`/`_ANCHOR_SOURCE`), because the
real tag surface does not exist yet — `g7` is the comment-tags gate and comes
after. That was explicitly permitted and is stated, not hidden. **`g7` must wire
the real tag-text surface into this mechanism** — carry that forward.

**The crew's own named blind spot** (state it to the reviewer; do not let the
reviewer "discover" it as though it were concealed): changes confined to a
docstring or to a comment are **invisible by design**; and a bare **local-variable
rename DOES trip the flag**. The crew **overruled my handoff** on that second
point — I had listed an unrelated local rename as twitchiness; it argued a tag's
prose can name a specific variable, so a rename is a legitimate staleness
candidate, at the cost of occasional false positives. Defensible; accepted.

**Best review targets:** (1) is the slug-match really the "text did not change"
half of the rule, or does it beg the question? (2) does the advisory-only
behaviour mean the flag can be ignored forever — and is that right? (3) attack the
reformatting immunity with mutations the crew did NOT choose. (4) confirm the new
report field cannot perturb `deterministic-rebuild`.

## Three facts from crew debriefs — worth real time to a successor

1. **`g7` wires into `g6` by joining on slug — no rework in `g6` is needed.** The
   `g6` crew established the dependency direction from `gate-spec.json`: **`g7`
   depends on `g6`**, not the reverse. No comment-tag vocabulary
   (`Assumption:`/`Constraint:`/…) exists yet — that IS `g7`'s build. The only
   pre-`g7` authored-identity surface is the `[slug]` anchor
   (`extract.ANCHOR` / the `anchored` predicate), and per `DESIGN_SPEC` §3
   **`g7`'s real tags mint with the SAME `[slug]` allocator**. So `g7` joins real
   tag text on slug and the staleness mechanism needs no change. Put this in the
   `g7` handoff.

2. **`stale_tags: []` on the real repo is CORRECT, not a silent failure.** The repo
   has **zero anchors today** (`ids: 0`), so nothing can be flagged yet. Do not
   read the empty list as the detector being broken. Corollary and a real
   limitation to carry: **the mechanism has never been exercised against real
   authored tags** — only the fixture. That validation belongs to `g7`.

3. **ENGINE: survey `reopen` does not exist** — it is gated-checklist-only and
   refuses with `REFUSED: reopen applies to gated checklists`. To re-verify a fix
   against an **already-consolidated** survey, the pattern is **`append` a recheck
   item → `record` it → re-`consolidate` with `--override-reason` pointing at that
   item**. The original failing item stays in the record for audit and simply stops
   blocking. The `gb` reviewer used exactly this to move BLOCK → APPROVE honestly
   rather than hand-editing the survey. **Route to feedback**, and reuse the pattern
   the next time a reviewer must re-verify a Commander-applied fix.

Also reinforcing **`tc39`**: the governor's HARD band fired for BOTH the `gb` and
`g6` crews **at `m0-context`, before either had written a line of code** — ~19–22%
fill from the upfront reading a bounded gate requires. It is tripping on
orientation cost, not on runaway work. That is the concrete argument for feedback.

## Record correction (do not propagate the error)

`cb99a901`'s message says the crew "again left its work uncommitted". **That is
false.** The crew committed at **`55b95314`** while I was mid-verification, so my
`git add` picked up only the run log. Same pattern as `g5`, where I made the same
wrong call in a handoff and had to correct it. **Check `git log` immediately
before asserting a crew did not commit** — these crews commit late, not never.
The `gb` crew genuinely did not commit; `g5`'s and `g6`'s did.

**`g6` = staleness detection.** Hash each tag's enclosing entity span at
extraction; on rebuild flag any tag whose anchor body changed while its text did
not, **in the run report the reviewer already reads** (no new channel; **no
timings** — the determinism diff covers the report). Designed but never built,
human-signed **accepted-untested** at confirm — **first build**.

Two things the handoff makes the crew resolve rather than assume: (1) **what a
"tag" even is today** — `g7` is the comment-tags gate and comes AFTER, so the
surface may not exist yet; building against a fixture is a legitimate stated
outcome. (2) **what the "anchor body" is** — this gate's open decision.
The twitchiness trap is named: a naive span-text hash fires on reindentation and
rewrapping, and an ignored flag is worse than none.

## `gb` IS CLOSED — `gb-integrate -> complete` on an APPROVE

**CLOSED: `g0` `g1` `g2` `g3` `g4` `g5` `gb`.** Seven of eleven. Remaining:
**`g6` `g7` `g8` `gs`**, then `reconcile → triage → review → feedback → archive`.
**Release the lease LAST.**

### `g6` starts here — its closing selector collects ZERO today, BY DESIGN

`g6-integrate`'s `c1` selects `-k 'stale_tag'` on **`tests/test_code_map.py`**,
which collects **0**. That is a **specification**, not a `tc47` defect: `g6` must
CREATE a test whose name contains `stale_tag`. **Say this in the handoff** — at
`g5` the plan waited on `caller_split` while the crew wrote
`ProductionTestCallerSplitTests`, and the mismatch was invisible until close.
Same for `g7` (`comment_tags`) and `gs` (`map_tree_freshness`). `g8`'s
`bom or docstring` already collects **3**.

### How `gb` closed — the process point worth keeping

The reviewer returned a correct, narrow **BLOCK**: one of five thresholds
(`CHURN_RATIO_CEILING_RENAME`) carried no `WHEN THIS FIRES` action line, against
this gate's explicit constraint. **My own grep had shown four lines against five
thresholds and I missed it.** Because the fix was a single documentation block
with no logic change, and the reviewer had already specified its content, a fresh
remediation crew was disproportionate — **so I wrote it and handed it straight
back to the SAME reviewer rather than self-grading.** It confirmed the wording is
actionable and distinct from the local-edit symptom, confirmed the diff purely
additive with no regression, and — asked directly whether its scan had been
exhaustive or had merely found the first instance — mechanically re-verified that
all **5 of 5** checked thresholds now carry an action line 1:1. **Use this shape
again for one-line constraint gaps: Commander fixes, original reviewer verifies.**

### What `gb` committed — `scripts/code_map/thresholds.py` (new)

`HOLE_RATIO_CEILING` **0.90**; `CHURN_RATIO_CEILING_LOCAL_EDIT` and `..._RENAME`
both **3.0**; `RECALL_FLOORS` **1.0** for `calls`/`reads`/`writes`;
`TEMPLATE_ASCII_INVARIANT`. All ratios or invariants, never counts. All five carry
an action line.

**The looseness question is ANSWERED — do not re-litigate it.** The reviewer built
its own realistic partial regression (disabled docstring emission on ONE code
path, `extract.Extractor._func`, not globally), rebuilt the real repo through it,
and drove the hole ratio to **0.933**, past the 0.90 ceiling. A generous ceiling
that still fires on a plausible bug is a sharp tripwire, not a decorative one.

**Rename churn — resolved, first measurement ever.** 1.02x (implementer, 212-caller
test symbol) and **0.5x** (reviewer, real 80-call-site PRODUCTION symbol
`scripts.checklist_engine:EngineError`, isolated worktree). Three synthetic rename
shapes — reordering, non-reordering, short-to-much-longer — all landed identically
at **1.545x**, so reordering and length changes never split one call-site mention
into more than one diff line. **Measure churn in diff LINES, never diff PAGES:**
the rename touched 217 of 3865 pages, so measured in pages the honest finding
would have been "blew the ceiling" — and it would have been wrong.

Four families committed in the NEW `scripts/code_map/thresholds.py`, each a ratio
or run-time invariant, each with its own one-line "what to do when this fires":
`HOLE_RATIO_CEILING` **0.90** (measured 0.673 here / 0.572 f1Brainz);
`CHURN_RATIO_CEILING_LOCAL_EDIT` and `..._RENAME` both **3.0** (measured **1.27x**
and **1.02x**); `RECALL_FLOORS` **1.0** for `calls`/`reads`/`writes` off an
11-edge hand fixture; `TEMPLATE_ASCII_INVARIANT` as an AST scan of `render.py`'s
own literal `Constant` nodes — structurally blind to the 386 pre-existing
non-ASCII pages, never a substring match.

**Headline: the widely-referenced-symbol rename was measured for the first time
and HELD at 1.02x** — flat, not a near-miss. Signed off "accepted-untested" at
design confirm; now resolved. Structural reason: a pure identifier rename changes
one line per call site on BOTH sides of the ratio, so the diff-LINES ratio stays
near 1x however many callers exist, even though 217 of 3865 pages changed. **Had
churn been measured in PAGES the honest finding would have been "blew the
ceiling" — and it would have been wrong, an artifact of the unit.** Vindicates
DESIGN_SPEC line 180.

Commander-verified: suite **1793 passed / 2 skipped / 672 subtests / 0 failed**
(baseline 1781 + 12 new methods); closing selector **13 passed exit 0**; fresh
`build` then `check` **7/7 exit 0**. **The crew left its work UNCOMMITTED with
`thresholds.py` untracked** — the Commander committed it, explicit paths only.

### COMMANDER ERROR #7, caught by the crew — fix carried

My `gb` handoff said the closing selector collects **17**. It collects **1**.
My scanner ran selectors against the whole `tests/` directory; the gates' real
commands target **`tests/test_code_map.py`** only. **Corrected table (re-run
against the right file):**

| gate | selector | collects |
|---|---|---|
| `gb-integrate` | `baseline or churn or recall or ascii` | 1 before / **13** after |
| `g6-integrate` | `stale_tag` | **0** |
| `g7-integrate` | `comment_tags` | **0** |
| `g8-integrate` | `bom or docstring` | **3** |
| `gs-integrate` | `map_tree_freshness` | **0** |

Conclusions unchanged: the three zeroes are unbuilt gates, so the selector is a
**specification** for a test that gate must create, not a `tc47` defect. Every
remaining handoff must still state the exact closing selector.

### For the `gb` reviewer / next Commander to settle

The two loose ceilings are the live question: **0.90 vs measured 0.673**, and
**3.0 vs 1.27x/1.02x**. A threshold no realistic regression can reach is the
"check that cannot fail" wearing a number. The crew's framing — the hole ratio is
a canary for catastrophic extraction collapse, not a documentation gate — is a
legitimate design choice IF stated and IF the canary can still fire. That is the
review's central call.

## `g5` IS CLOSED — `g5-integrate -> complete` on an APPROVE

**CLOSED: `g0` `g1` `g2` `g3` `g4` `g5`.** Six of eleven. Remaining: **`gb` `g6`
`g7` `g8` `gs`**, then `reconcile → triage → review → feedback → archive`.

### `tc47` — the trap that nearly ate the gate close, READ THIS BEFORE ANY GATE

`g5-integrate`'s own postcondition `c1` selected `-k 'caller_split'` — **a name no
test in this repo has ever carried**. It collects **ZERO** tests and pytest exits
**5**, so the `&&` chain could never pass however correct the code was. This is
`tc38`'s defect class in the PLAN's own check. It survived plan review, all of
`g5-implement`, a BLOCK, a remediation and a re-review, because **nothing runs a
gate's own postcondition command until `advance`**.

**Repaired** by `amend --delta ... retext-check` (authority `commander`) to
`-k 'CallerSplit'`, which collects **7** and passes. Only the selector changed;
statement, env prefix and the human-authority override policy untouched — nothing
was waived. Discrimination proved: the remediation's red-before-green ran a test
inside that very class RED at exit 1.

**DO THIS AT EVERY REMAINING GATE:** before dispatching, run that gate's own
`c1`/`c2` command postcondition **by hand** and confirm any test selector collects
a **non-zero** count. Exit 5 is "no tests collected" — categorically different
from a red, and it looks like diligence.

### ALL REMAINING SELECTORS ALREADY SCANNED — done 2026-08-08, do not redo

Scanner: `C:/Users/fredc/.claude/jobs/9cbc67f4/tmp/scan_selectors.py`.

| gate | closing selector | collects today |
|---|---|---|
| `gb-integrate` | `baseline or churn or recall or ascii` | **17** ✅ |
| `g6-integrate` | `stale_tag` | **0** (rc 5) |
| `g7-integrate` | `comment_tags` | **0** (rc 5) |
| `g8-integrate` | `bom or docstring` | **2** ✅ |
| `gs-integrate` | `map_tree_freshness` | **0** (rc 5) |

**The three zeroes are NOT `tc47` defects.** Those gates have not been built yet,
so the selector is a **specification**: "this gate must produce a test matching
this name." That is red-by-absence, a legitimate grade-B falsifier.

**But this is EXACTLY how `g5`'s trap formed** — `g5`'s crew created its tests as
`ProductionTestCallerSplitTests` while the plan waited on `caller_split`, and the
mismatch only surfaced at close. So: **every remaining implementer handoff MUST
state the gate's exact closing selector and require the new tests to match it**,
and the crew must run that selector by hand and report the count. `g6`, `g7` and
`gs` each need a test whose name contains, respectively, `stale_tag`,
`comment_tags`, `map_tree_freshness`.

### Engine details learned this gate

- `amend --delta` op key is **`"op"`, not `"kind"`** (a `"kind"` key fails with the
  unhelpful `unknown op kind None`).
- `retext-check` accepts a **pending or in-progress** gate; `reopen` a complete one.
- **Registry vs recovery disagree:** `recover_crews.py` reports `0 unresolved`
  while `run_crew.py` REFUSES the launch as a duplicate. An externally dispatched
  crew stays `running` until closed with
  `run_crew.py --verify-result <session-name>` — the correct close for a crew that
  finished. `--abandon` also frees the hold but **misrecords a successful attempt**.
- `.agent-work/issue-456/evidence/run_flag_candidate.py` points at the **reviewer's**
  engine and takes 4 args. Commander wrappers that work are in the job tmp dir:
  `run_advance.py`, `run_amend.py`, `run_attest.py`, `run_flag.py`.

### Candidates filed at `g5-integrate` (numbering trap still applies)

`execute.json`'s own counter printed these as **`tc4`/`tc5`**; run-wide they are
**`tc47`/`tc48`**. Run-wide total is now **tc1–tc48**. Triage must not double-count
— and `tc48` is ALSO the g5 re-review survey's own `tc1`, re-filed so the drain
list holds it in one place.

- **`tc47`** = a gate's own postcondition can be a check that could only ever fail;
  run test selectors at authoring time; `exit 5` should never read as a normal red.
- **`tc48`** = the new pinning test guards one literal string, not the defect class.
  The re-reviewer mutation-proved it: four differently-worded top-level-only
  overclaims that avoid the literal "top-level" all survive undetected. Not a
  blocker — its docstring does not overclaim, and its behavioural half is a full
  general pin. Joins **`tc45`**; the robust form derives the legend's prose from the
  predicate's own literal values.

### Also for feedback, new this gate

`tc42` may be **retired**: the g5 re-reviewer resolved `<fowler-pass-record-path>`
to a real path **at instantiation, before `claim`**, and needed **no waiver** —
the first of six reviewers to get the normal path. The template's imperative text
should state that as the default expectation.

## REMEDIATION LANDED — commit `588d5419`, verified by the Commander

The `BLOCK` defect is fixed. Legend reworded in BOTH hand-independent copies to
"a tests package anywhere on the module path"; pinning test added guarding both
directions of drift; `measure_split.py` now carries the definer dimension.
Commander-verified independently: **no import** between the copies; fresh `build`
then `check` → **7/7 exit 0**; modules 111, entities **3753**, pages **3865**;
suite **1781 passed / 2 skipped / 672 subtests / 0 failed**; commit is explicit
paths only with **0** tracked `map/` files.

**The one moved number is benign and confirmed:** `unused_test_defined` 2340 →
2341, because the new pinning test is ITSELF a newly mapped entity with no
callers (this repo self-indexes `tests/`). Corroborated by entities 3752 → 3753
and pages 3864 → 3865. A NEW entity, not a reclassified one. All five other
cells byte-identical: 88 / 2 / 449 / 873 / 0.

**Exactly 1 of 3865 pages** still contains "top-level tests package" — the new
test's own page, whose docstring quotes the old legend to explain what it guards.
Correct behaviour, not a leftover. **Do not "fix" it.**

**NEW candidate for triage (tc47):** this repo's `code_map` self-indexes
`tests/test_code_map.py`, so any test added under TDD changes the repo's own map
by +1 entity/page. It cost the crew one failed `advance` on hardcoded counts.
Belongs in `CREW_CONTEXT.md`.

**NEW for feedback:** `current` does not surface the latest `why_trail` id, so the
`tc39` refresh-request recovery forces a crew to read the plan JSON directly — a
documented exception to "never read the JSON for state". Ask for a
`latest_why_id` field or an `attach ... --why-ref latest` shorthand.
- **REGISTRY GOTCHA (new, 2026-08-08):** `recover_crews.py` reported `0 unresolved` while
  `run_crew.py` still REFUSED the launch as a duplicate — the two disagree. An externally
  dispatched crew stays `running` in the registry until you close it explicitly with
  `run_crew.py --verify-result <session-name>`. That is the correct close for a crew that
  finished; `--abandon` would misrecord a successful attempt. Both `g5` attempt-1 entries
  (implementer and reviewer) were verified and closed this way before attempt-2 registered.
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/g5-remediate-RESULT.md`
- **lease**: `commander-issue-456` — re-claim IDEMPOTENTLY (same id, NOT a takeover, no `--force`)

## Where the run is

CLOSED: `g0`, `g1`, `g2`, `g3`, `g4`.
**`g5` is NOT closed — the review returned `BLOCK` and the block is correct.**
`g5-implement` and `g5-review` are both `complete`; `g5-integrate` must NOT be
advanced on a BLOCK. **Next action: dispatch the remediation crew** with the
ready handoff at `.agent-work/issue-456/crew-handoffs/g5-remediate.md`, at
**`--model sonnet`**, role `implementer`, gate `g5` (it will register as
`attempt-2`). Then re-review, then `g5-integrate` on an APPROVE.

### The block, in one line

`SPLIT_LEGEND` — printed on all **3864** pages — says the split keys on a
**top-level** `tests` package; `is_test_module` is `return "tests" in parts`,
matching a `tests` segment **anywhere**. Confirmed in BOTH hand-independent
copies by reviewer and Commander. **Commander's ruling: fix the LEGEND, keep the
PREDICATE, add the pinning check** (precedent: `RefsAccountingTests.
test_the_legend_names_the_predicates_the_count_actually_counts` pins
`REFS_LEGEND`). Reclassifies zero entities, so all measured numbers stand.

### What g5 already got RIGHT (do not redo)

Two attributed lines per page; `TEST_NOTE` on 2789 test-defined pages and 0
production-defined; test pages NOT deleted (IF7 over SY8); `tc32` genuinely
closed and attacked with three unchosen mutations; the hand-restated
`is_test_module` in `checks.py` **proven load-bearing** (diverging only that copy
made TWO checks go red) — which retires the standing worry that this gate would
collapse `g2`'s two-independent-declarations design.

### The corrected split — measured twice independently, agreeing exactly

| bucket | prod-defined | test-defined |
|---|---|---|
| unused | **88** | **2340** |
| test-only | **2** | 449 |
| production | 873 | 0 |

The crew's shipped headline of "unused 2428 (64.7%)" is **96.4% test-defined**.
Genuinely unused production code is **88**, not 2428 — a 27x difference.

REMAINING AFTER `g5`: `gb g6 g7 g8 gs`, then
`reconcile → triage → review → feedback → archive`. **Release the lease LAST.**

## Resume recipe

```
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py \
  --file .agent-work/issue-456/spine.json resume execute --session-id commander-issue-456 --reason "<why>"
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py \
  --file .agent-work/issue-456/execute.json current
```

CLI shape: `--file` goes **BEFORE** the verb; `--session-id` **AFTER** it (and
`current` takes **no** `--session-id`). `advance` needs a positional id **and**
`--why`. `claim` takes no `--actor`. `block` needs `--blocker`. `attest` uses
`--cond` + `--which` (+ `--evidence` for postconditions). `attach` uses `--type`
+ `--payload-file`. **Evidence TYPE is enforced** — a postcondition wanting
`implementer-result` rejects `--type artifact`. **Evidence FIELDS are enforced**
— a postcondition wanting `{'verdict':'APPROVE'}` rejects `APPROVE-WITH-FINDINGS`;
put the reviewer's own three-way label in a second key.
`flag-candidate` uses `--from` + `--statement`.

## Crew model — settled 2026-08-08

The human asked; the registry said **`opus` ×9**. Corrected: from `g3-review` on,
**dispatch crews at `sonnet`** (`--model sonnet` to `run_crew.py` AND
`model: "sonnet"` on the Agent call). Haiku declined for **reviewer** roles (a
rubber-stamp review is the exact defect this run hunts); try haiku on a
mechanical gate and **measure it**. The `g3`/`g4` sonnet crews each caught
something the Commander missed — quality held.

## Standing rules

- **tc38**: a check that can only ever FAIL is as informationless as one that
  cannot fail. Tell every crew its own gate selector up front and make it run the
  selector by hand. `g5` selector: `-k 'refs or caller'` → **11 collected** today.
- **tc36**: a handoff naming an exclusion without naming **where** the tripwire
  sits makes every successor rediscover it at full cost.
- Reproducing a falsifier its author designed proves only that probe works —
  attack with a mutation the author did NOT choose.
- red-before-green: every reproducer committed in its FAILING state before the fix.
- **Six** Commander errors caught by crews so far, every one by running rather
  than reading. Tell each crew it is expected to overrule the handoff.

## Numbers at this boundary

- suite **1772 passed, 2 skipped, 672 subtests, 0 failed, 0 xfailed**
- fresh `build` then `check` → **7/7, exit 0**. `check` reads a **stale** tree at
  `<root>/map`; run `build` first or the exit code means nothing.
- render report: modules **111**, entities **3728**, pages **3840**, ids 0
- `git ls-tree -r HEAD --name-only -- map/` → **0** tracked files
- zero `:<line>` across all 3840 pages (the human's strip-the-line-numbers ruling)
- CARRY-FORWARD SPENT: the old note that `check` "correctly exits 1" is dead.
- Use `python`, **never `py`** (`py -m pytest` dies "No module named pytest" and
  reads as a silently green run).

## Authority

- Push and a **full non-draft PR** are **PRE-APPROVED**. **Merge to `main` is NOT.**
- Never force-push. Never merge.
- **Do NOT `git add -A`** — the untracked ~3,840-page `map/` tree is staged at `gs`,
  deliberately last. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
  `superCoolSpaceSim` is **C++/Obj-C with ZERO tracked `.py`** — it indexes to 0
  modules. It is a **null test, never a cross-corpus shape test**. `f1Brainz`
  (1227 modules / 15037 entities) is the only real second Python corpus.
- Worktree isolation refuses compound Bash with loops, `env -u`, heredocs,
  `$(...)`, `VAR=x && ...` chaining, or long quoted strings. Use plain separate
  commands, script files, `git commit -F <file>`. Working env form:
  `unset FORCE_COLOR PYTHONIOENCODING && python ...`.
- **Shell-quoting workaround (tc43)**: engine verbs taking free text fail on any
  real message. Wrapper scripts that read text from a file and pass list argv via
  `subprocess` live in `.agent-work/issue-456/evidence/` — `run_record.py`,
  `run_waive.py`, `run_consolidate.py`, `run_flag_candidate.py`. **Reuse them.**
- Ask the human decisions in **plain text**, never `AskUserQuestion`.

## Gate assignments still to honor

- **g5** owned `tc32` — **CLOSED and attacked**, no longer outstanding.
- **CANDIDATE NUMBERING TRAP:** `execute.json` has its OWN candidate counter. The
  two candidates filed at `g5-review` print as **`tc2`/`tc3`** but are the
  run-wide **`tc45`/`tc46`**. Triage must not double-count. `tc45` = nothing pins
  a printed legend to the predicate the code applies (generalize past
  `SPLIT_LEGEND`). `tc46` = a gate's own evidence script reproduced the exact
  conflation the gate removed, and evidence scripts get no adversarial read.
- **tc39 CONFIRMED AGAIN, live:** the context governor's HARD band fired at
  **15%** fill and refused `advance` until a `refresh-request` was attached. The
  crew independently hit the undocumented `why_ref` rule — it must cite the
  **CURRENT latest** why-record id, and **every** `advance` mints a new one, so a
  cited id goes stale immediately. Read `why_trail[-1].id` and attach in the same
  breath. Both route to **feedback**.
- **New from the g5 crew, for feedback:** a `command` postcondition ALWAYS
  re-runs and cannot be satisfied by reference to evidence already gathered the
  way `attest --evidence` can — so one `advance` re-ran a ~5-minute full suite
  that had just been run by hand.
- **Non-blocking, carried forward:** 386 pages are non-ASCII, every one traced to
  PRE-EXISTING docstring prose (an em-dash in `scripts/agent_work_root.py`).
  `g5`'s own strings are pure ASCII. Not `g5`'s defect; do not re-litigate.
- **Line-position ruling, precisely restated:** **0 of 3864 page HEADERS** carry a
  line position. Three pages do contain a `.py:<line>` string — all inside
  docstring prose the map reproduces verbatim from source. That is correct
  behaviour, not a header defect. Do not "fix" it by censoring source text.
- **tc35** (INDEX collision family) needs `g1`'s `page-accounting` falsifier rebuilt
  on a DIFFERENT collision FIRST.
- **tc39** (governor HARD band at ~16% of real fill), **tc42** (Fowler rail's
  unsubstitutable `<fowler-pass-record-path>` placeholder — four consecutive
  reviewers force-waived it) and **tc43** route to **feedback**, not a gate.
- **tc44** (routing tier degenerates on the flat 74% tests package) — triage.
- **gs** needs an explicit "rebuild, then stage" line and must expect `check`
  **exit 0**.
- Triage must drain **tc1–tc44**.

## The tripwire map (where each protected thing physically sits)

- `checks.py` `REFS_PREFIX` / `REFS_LEGEND` / `REFS_MODULES` / `parse_refs` are
  declared **independently** of `render.py`'s copies **on purpose** — a check that
  reads its expected text out of the code under test can only ever agree with it.
  **`g5` changes this grammar, so `g5` is the gate most at risk of collapsing that
  independence into an import.**
- `_make_collision_repo`'s `INDEX` collision is `g1`'s only cross-platform
  falsifier for `page-accounting` and must keep colliding.
- `OWN_MODULE_NAMED_MUTATION`'s byte-exact anchor in `render.py`.
- `entity_symbol_join`'s two independent derivations (`extract.child_sym` vs
  `checks.SourceScan`) must stay independent — `g3`'s whole gate proved that.
