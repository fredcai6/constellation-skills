# Rework 1 Verdict — #305 gate g4 (closes #327)

**Discharges:** BLOCKER-1 of `.agent-work/issue-305/crew/g4-review-result.md`.
**Reviewed:** `f6acc1e` + `5ccae87`, bound to the shipped bytes at HEAD (see "bind target" below).
**Survey (engine-driven, 11 checks):** `.agent-work/issue-305/g4-review-rework/review.json`
**Fowler record:** `.agent-work/issue-305/g4-review-rework/fowler-pass.json` (rail exits 0)
**Engine session:** `g4-rw1-01V6pZ`

---

## VERDICT: `APPROVE-WITH-FOLLOWUPS`

**BLOCKER-1 is discharged.** The false clause is gone from *both* shipped copies, and the
replacement survives being attacked as a fresh claim of the same shape — which is exactly how I
treated it, not as a correction I was inclined to accept.

Three followups remain, all one-line edits, none leaving a conclusion unsupported.

**Why not `APPROVE`:** FU-A below is a real defect — a checkable-looking claim that yields the
wrong numbers under a reasonable reading. That is the same failure *shape* as BLOCKER-1, and I am
not going to launder it into a clean approve.

**Why not `BLOCK`:** the principled distinction is that BLOCKER-1 was **false under every
reading**; FU-A is **true under the reading its author intended** and refutable under none. It
costs a reader a guess, not a wrong belief.

---

## Bind target — corrected

You asked me to bind to `5ccae87`. HEAD was already past it, and moved twice more while I worked:
`5a3e7fc` → `069b405` → `07b7f2e` → `87656e6` → `18fdf82`. **For source they are all the same
tree:** `git diff --name-only 5ccae87 HEAD` filtered of `.agent-work/` returns nothing. I bound to
HEAD and verified per-blob equality rather than tree equality, and I am saying so rather than
silently reviewing a commit that is no longer the tip — that is the #381 rule you invoked, applied
to you.

A bare tree-OID check *would have failed* here and would have been the wrong instrument. Per-blob
equality on the five files under review passes.

---

## (a) The replacement clause, atom by atom — **ALL FIVE CONFIRMED**

| atom | claim | verified |
|---|---|---|
| 1 | `g1-review.json` added first | **1** A-entry, **0** D-entries per file — no add/delete/re-add, no rename ancestry. `b1707f1` vs `bcb0975`. |
| 2 | it reports `true` | `run.dirty` is literally `True`. |
| 5 | "eight minutes" | 8m11s by committer date, 8m16s by the manifests' own `generated_at`. Two instruments. |
| 4 | "2m16s" | `2456130` at `02:58:37Z` → manifest at `03:00:53Z` = **exactly `0:02:16`**. |
| 3 | "`2456130` cleaned the tree" | **Confirmed**, by an argument you did not make — see below. |

I computed every interval from `%cI` parsed to real UTC instants, **not** from a local-format date
string. A local-format date wearing a `Z` suffix is precisely the kind of thing that manufactures a
false interval, and it appeared in my own scratch output last round.

**Atom 3 is the only one that is an inference rather than a reading**, so I built the argument:

1. `2456130` is **non-empty** (2 files changed) → the working tree had uncommitted content
   immediately before it. It was dirty at `02:58:37Z`.
2. At `03:00:53Z` the tree was clean, and that is a **measurement, not an inference** — it is the
   manifest's own `run.dirty: false`, produced by the real `git status --porcelain` inside
   `repo_revision`.
3. **No commit exists strictly between** `2456130` and the reading; the next is `bcb0975` at
   `03:01:44Z`, *after* it.

∴ the dirty→clean transition occurred at `2456130` and nowhere else in the record. This also
disposes of a live alternative I checked for: the window between the last `true` reading
(`02:52:37Z`) and the `false` one contains **three** commits (`b1707f1`, `42f2348`, `2456130`), so
"the tree went clean at `42f2348` and merely stayed clean" was genuinely possible — excluded,
because `2456130` having something to commit means the tree was dirty again immediately before it.

**Honest residual, named rather than left to be found:** nothing in the tree excludes an unrecorded
`stash`/`checkout`/`clean` inside the 2m16s window. A commit that is *known* to have occurred and
that produces *exactly* the observed transition is the evidenced explanation, and no alternative is
recorded. Crucially — and unlike the clause it replaces — **it is not refutable by the tree.** The
old clause asserted an ordering the tree contradicted; this one asserts a transition the tree
corroborates.

**No fresh BLOCK.**

---

## (b) Is `--diff-filter=A` a defensible instrument? — **Yes, because the wording is calibrated to it**

The doc says *"the **second** manifest **added** to that context directory."* `--diff-filter=A`
measures exactly addition. The claim and the instrument are the same statement — you did not
overreach from "added" to "written" or "produced". **That discipline is precisely what was missing
from the clause that sank last round**, which claimed an ordering ("the run's first") no instrument
in the tree supported.

It survives the same skepticism I applied to `--follow`, on three grounds:

1. **Unambiguous here.** Exactly one `A`-entry and zero `D`-entries per file, so there is no
   add/delete/re-add sequence to report the wrong element of, and neither path has rename ancestry
   — the exact failure mode that made `--follow` lie.
2. **Corroborated by a code-disjoint witness.** `run.generated_at` *inside* the files, stamped by
   the producer and owing nothing to git bookkeeping, gives the same ordering (`02:52:37Z` before
   `03:00:53Z`). Two instruments, no shared mechanism.
3. **Substantively, not just bookkeeping-wise.** `e5ccd37` closed `g1-implement` at `02:29:27Z` —
   *before* `g1-review.json` was even generated at `02:52:37Z`. So `g1-implement.json` exists **at
   all** only because g1 was later reopened at `bcb0975`. "Second added" is a fact about what
   happened in the run, not about when someone chose to commit.

**General weakness, recorded even though it does not bite:** commit-addition time is an *upper
bound* on file creation, and `generated_at` reflects the *last* write of an overwritten file. So
**neither instrument can establish "first written"** — and it would have been a defect to claim it.
The doc does not.

**A hypothesis I tested and discarded rather than offering you:** I suspected `g1-implement.json`
was absent because #305 g1 had not yet wired the producer. `git log -S emit_step_manifest` puts the
identifier in `scripts/` from `fba7fae` at `02:06:21Z`, *before* both manifests. The wiring
explanation is **false** and I am not offering it. The reopen explanation above is the supported one.

---

## (c) Does pinning stop the decay, or relocate it? — **It stops it**, and I say that against my own prior

In my BLOCK I raised the possibility that anchoring to a moment no commit identifies would leave the
claim true-but-unverifiable — moving the defect rather than fixing it. I measured instead of
assuming, and **the measurement goes your way.**

| revision | total | `true` | `false` | field-absent | matches 49/47/1/1? |
|---|---|---|---|---|---|
| **`35d2686^`** — the tree the removal was made **on** | **49** | **47** | **1** | **1** | **YES** |
| `35d2686` — the commit that performed it | 56 | 51 | 1 | 4 | no |
| `f6acc1e` | 56 | 51 | 1 | 4 | no |
| HEAD | 56 | 51 | 1 | 4 | no |

The pinned arithmetic is not merely true of an unrecoverable instant — it is **exactly reproducible
at a fixed commit**, so the numbers can never change again. The delta is fully explained: between
`35d2686^` and `35d2686` the g4-implement run committed its own seven manifests, four pre-removal
(all `true`, 47+4=51) and three post-removal (field-absent, 1+3=4); 49+7=56.

**FU-A falls out of the same table** — see followups.

---

## (d) Still docstring-only — **CONFIRMED** with my own instruments

I compared **`35d2686` against HEAD**, not `f6acc1e^..f6acc1e`, so the check spans the *entire*
rework; a narrower comparison would have left the gap between the commit I was pointed at and the
tip unexamined.

1. **Bytecode** (`optimize=2`, recursive compare over 14 fields + `co_consts`): exactly **one**
   code object differs — `DeclarationError.co_code`, in **one inline operand**, `LOAD_SMALL_INT 162
   → 166`. That is Python 3.13+'s `__firstlineno__`, and it checks out to the line:
   `DeclarationError` sits at 162 at `35d2686` and 166 at HEAD, **+4**, exactly the operand delta,
   because the module docstring grew by four lines. **No function's code changed.**
2. **`assert` statements** (which `optimize=2` hides) counted separately: identical, 0 in both.
3. **Positional:** every changed line on both sides — pre 34–36, post 34–40 — lies strictly inside
   the module docstring's node span (pre 2–75, post 2–79).
4. **Runtime**, because a docstring *can* be behaviour in this repo: `scripts/context_manifest.py`
   contains **zero** `__doc__` reads (unlike `checklist_engine.py`, which feeds its module docstring
   to argparse at :2301), and nothing anywhere reads `context_manifest.__doc__`. Invisible at
   runtime by compilation *and* by inspection.

---

## (e) Your sweep — **checks out**, and I ran a wider one

| sweep | result |
|---|---|
| false causal claim (`run's first\|no predecessor\|first manifest\|…`) | only `file_issue_set.py:13` and `verify_issue_set.py:126`, both "runs first" about **rail ordering** — unrelated, pre-existing. **Zero** surviving copies; **zero** occurrences of "no predecessor" anywhere. |
| permanence claim ∩ `dirty` | **zero** |
| `run.dirty` | **zero** |
| **stale present tense** (`has written\|have written\|producer has`) — *the sweep you didn't name, which I added because the second defect you self-reported was a tense* | `episode_capture.py:40` ("the producer **has** legitimate raising paths") and `install_constellation.py:1328`, both unrelated on inspection. **Zero** surviving present-tense statements of the measurement. |
| every site of the arithmetic (by numeral **and** independently by `field-absent`) | **exactly two** — `CHECKLIST_ENGINE_DESIGN.md:256` and `context_manifest.py:35-36`. **No third copy.** Both past-perfect, both scoped. |

So **"both copies were corrected, not one" is CONFIRMED** — which matters, because my own
root-cause finding predicted the second copy would be the one left behind.

---

## The `5ccae87` re-wrap changed **no word** — proved, not read

- **Token stream, whole file:** 5937 tokens both sides, **identical**, joined-stream sha256
  `5734173a60edac38` on both.
- **Whitespace-stripped character stream:** 32964 chars both sides, **identical** — this catches
  what a token compare alone would miss, a word split or two words joined.
- **Localisation:** 428 lines both sides; difflib finds exactly **one** changed region, lines
  262–264. File is byte-length-identical at 39451, which is what a pure re-break produces.

**One precision note, on the commit message, not on shipped content.** It says the edit left a line
past *"the ~100-column wrap the rest of the document keeps."* The document does **not** keep that
wrap throughout: 90 lines exceed 100 columns, only 4 of them table rows, and 68 non-table lines
exceed 110 with several past 400 and one at 817. What *is* true is the part that matters — the
paragraph's neighbourhood (lines 245–270) runs 89–110 with a strong 94–102 mode, the pre-rewrap
outlier at line 262 was **128**, and the paragraph's lines are now 98/97/78. The action was right;
only the generalisation is loose, and it lives in a commit message.

---

## Suite

My own run, reworked tree, `python` 3.14.3 / pytest 9.0.2 (**never `py`**):

```
1487 passed, 2 skipped, 472 subtests passed in 132.47s
```

Identical on all three counts to my pre-rework baseline. Note the subtests stayed at **472** rather
than dropping — confirming the tree was committed when I ran it, since `RevIsGitBlobOid`'s
clean-subset subtest falls to 3 against a modified `scripts/` file.

---

## Fowler pass (rework diff)

Rail exits 0: *smells=12, flagged=[duplicated-code, shotgun-surgery], overridden=[comments-as-deodorant]*.
`rail_exception` is **null** — I did not skip the pass, which matters because a prose-only diff is
exactly the case the skill says a reviewer may not self-grant a skip for. Nine `absent` verdicts are
grounded in the *mechanically established* fact that the diff contains zero executable code, not in
the file extensions.

- **duplicated-code — flagged.** This diff **is the duplication's bill arriving**: one factual
  correction required editing the same measurement in two shipped files, with nothing mechanical
  guaranteeing the second moved with the first. The two copies have now begun to **diverge in
  detail** (the doc names `2456130`; the docstring says only "a commit"). Benign today — the
  docstring's form is a strict weakening, so they cannot contradict — but it is the first visible
  step of exactly the drift that produced BLOCKER-1.
- **shotgun-surgery — flagged, now with a second data point**, which is what turns a suspicion into
  a pattern under Fowler's own repeat test. Last round: seven prose sites, five files, one boolean.
  This round: two files, one clause. **Not a defect of this rework — it paid the cost correctly, it
  did not create it.**
- **speculative-generality — recorded `absent` *from this diff*, deliberately.** The property
  persists in the file, untouched, and is already an accepted triage candidate. Re-charging it would
  double-count a finding you have already routed.
- **comments-as-deodorant — overridden, scoped.** A 100%-prose diff is the maximal surface for this
  smell and deserves a real answer: deodorant is prose masking unclear *code*, and this diff has no
  code at all — the prose **is** the artifact under repair. Scoped to the prose's *existence* and
  register, **not** its multiplicity, which stays charged under the two flags.

---

## FOLLOWUPS

- **FU-A** *(the reason this is not a bare APPROVE)* — `"at the point of removal"` has **two natural
  readings that give different numbers**: `35d2686^` → 49/47/1/1, `35d2686` → 56/51/1/4. A reader
  who takes the second and checks will conclude the doc is wrong. **Name the revision** — *"as of
  `35d2686^`, the tree the removal was made on"* — and the sentence becomes settleable by one
  command instead of a guess. Applies to both copies.
- **FU-B** — the module docstring carries a reader warning the design doc does not:
  *"(the arithmetic is pinned to that moment deliberately; the live count keeps growing as this
  producer runs)."* That guard belongs in the copy a reader is **more** likely to check. One edit
  with FU-A.
- **FU-C** *(optional strengthening)* — *"the second manifest added to that context directory"*
  reads like git bookkeeping. The substantive fact underneath is that `g1-implement.json` exists
  **only because g1 was reopened**. Saying so converts a bookkeeping sentence into the run's actual
  history.
- **Carried unchanged from round 1**, not re-charged here: FU-1 (encode-token comment), **FU-2 (the
  surviving mutant — deleting `"dirty": None` from `default_repo_state`'s early return leaves the
  full suite green)**, FU-3/4/5/6 (single-source the measurement; one JSON walker; the
  `repo_revision` unused half).

---

## Method & tree

**I mutated nothing and committed nothing.** This round required no mutation — every check was
read-only (`git show`/`ls-tree`/`log`/`grep`, an in-process `compile`, and pytest) — so there was no
restore to perform and no window in which the tree could have been left mutated. All five source
blobs are byte-identical to my baseline and to HEAD:

```
docs/CHECKLIST_ENGINE_DESIGN.md    98c54464152c868aeded67c1d8c319fc8a5d822d
scripts/context_manifest.py        54babe716bf010237b3e01162a2e8251172422c0
scripts/checklist_engine.py        23ba70391b78808b95fb6842b95e13f36af820c5
tests/test_context_manifest.py     43b39bbeeb9550d5264322a7be2baa107dc83638
tests/test_context_determinism.py  3a21311cad664f2fad97e5c7d1223bac94adbcda
```

EOL re-derived per base (#319): both touched files are 100% CRLF in the worktree (428/428 and
457/457, zero bare LF).

**Two things I am reporting rather than quietly passing:**

1. **The tree OID changed under me** — HEAD advanced four commits mid-survey. Verified source-neutral
   (`git diff --name-only 5a3e7fc HEAD` filtered of `.agent-work/` returns nothing).
2. **Commit `5a3e7fc` swept my in-flight survey** (`.agent-work/issue-305/g4-review-rework/review.json`)
   into the index while every item was still `pending`. The committed copy is a snapshot of an
   **undriven** survey, and every engine write I make now registers as tracked dirt on it. Harmless
   to the verdict; at closeout, commit the **driven** survey over the pending snapshot so the two are
   not confused.

---

## Where this verdict lives

I wrote this as a **separate file** (`g4-review-rework-result.md`) and appended a short pointer
stub to `g4-review-result.md`, so a reader who opens the original does not act on a BLOCK that has
since been discharged. Answering your question: **separate file, with a pointer.**

---

## Workflow feedback

- **The rework handoff was well-shaped.** Naming (a)–(e) as things to *attack*, and explicitly
  saying "my replacement is itself a causal claim, and it is the same shape of claim that just
  failed", is the single most useful sentence in it — it told me the standard to hold you to.
- **You self-reported a second defect I had not named** (the present-perfect tense) and fixed both
  copies. That is the behaviour that made this round cheap.
- **Friction worth recording:** the bind target moved four times while I worked. `#381` says prove
  against what ships; when the tip advances mid-review, "what ships" is a moving target and the
  reviewer has to re-establish it. Per-blob equality on the files under review is the instrument
  that survives this; tree-OID equality is not.
- **Repeat of a round-1 item:** the reviewer SKILL.md still says to `advance` a survey check, which
  the engine refuses (`advance is for gated checklists; use record`). Second time it cost me a
  refused call.

---

## Confirmation — `e61578b`

**All three answers are yes, nothing new is wrong, and my `APPROVE-WITH-FOLLOWUPS` re-binds to
`e61578b` (verified equal to shipped bytes at HEAD `fd2fc0b`, which touches no source).**

**(1) FU-A/B/C discharged.** FU-A: **both** copies now read *"as of `35d2686^`, the tree the removal
was made on"* — `CHECKLIST_ENGINE_DESIGN.md:256` and `context_manifest.py:35`. FU-B: the live-count
guard is now in **both** (`:258` and `:40`), which was the whole point — it previously sat only in
the copy a reader is less likely to check. FU-C: the reopen fact is in the design doc (`:262`),
which is exactly the scope I specified; its absence from the docstring is correct, not a gap.

**(2) Nothing new is wrong.** *"At `35d2686` itself it already reads 56 / 51 / 1 / 4"* is **correct
as written** — I re-measured from scratch rather than accepting the agreement: `35d2686^` → 49/47/1/1,
`35d2686` → 56/51/1/4. **No self-reference problem**: `git show 35d2686:scripts/context_manifest.py`
contains **zero** occurrences of either SHA, so the file names an ancestor that already existed when
the naming was written — there is no bootstrap paradox, and `35d2686^` (= `aa5d06dd`) is reachable
from HEAD. Two observations, neither blocking, both strictly milder than what they replace:
**(i)** *"It recorded what its predecessor left behind — `g1-review.json`, eight minutes earlier,
reporting `true` — not what it was itself about to do."* Both halves are true and the causal
attribution is correctly made to `2456130` in the preceding sentence, but the appositive sits where a
reader can take it as claiming `g1-review.json` left the clean tree, which it did not. Moving the
naming out of that clause would remove the invitation. **(ii)** `main`'s recent history is flat with
`(#NNN)` suffixes — squash merges — so after merge **neither SHA will exist in `main`**, and the
anchor a reader of `main` can resolve is the prose, not the ref. This degrades gracefully (the doc
now states both counts explicitly, so the measurement stays unambiguous without the SHAs) and is
strictly better than the ambiguity it replaced, but it is worth a decision at the PR step rather than
a surprise afterwards. Cosmetically, the docstring's new wrap leaves one short line at `:41-42`.

**(3) Still docstring-only.** Same instrument as before, `optimize=2` bytecode over `e61578b^..HEAD`:
exactly **one** code object differs — `DeclarationError.co_code`, one inline operand
`LOAD_SMALL_INT 166 → 168` — and `DeclarationError` moved from line 166 to 168, **+2**, exactly the
module docstring's growth. No function's code changed; asserts identical; every changed line
(pre 34–40, post 34–42) lies strictly inside the module docstring's span. Method note: this
confirmation was run as a direct check rather than a new engine survey, at the Commander's explicit
scoping — the rework survey it appends to was already driven to consolidation and released.
