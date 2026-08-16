# Review Result — g2, rework 2

Written by `constellation/cleanup-f-derive-worktree/g2/reviewer/attempt-2`.
Survey: `.agent-work/cleanup-f-derive-worktree/g2-review-rework2/review.json`
(driven through the engine under my own lease; `consolidate` recorded
`verdict=BLOCK findings=1`).
Fowler record: `.agent-work/cleanup-f-derive-worktree/FOWLER_PASS-g2-reviewer-rework2.json`.

## Assigned Gate

`g2`, rework 2 — the deletion of `checklist_engine.worktree_from_spine_path`
under `ADMIRAL_RULING-2` N2, plus rework 1 carried in the same result.
Review target: the single commit `84d949eb` (base `cb77ff4d`).

## Result

`BLOCK`

One blocker. It is narrow, in scope, comment-only, and changes no behaviour.
Everything else on this gate passes, and most of it I reproduced myself.

---

## The blocker

**B1 — the prose repair is incomplete inside the file that needed it most.**

`scripts/checklist_engine.py`'s `main()` carries a comment block that opens
"Nothing stands between `load` and the arming below any more (#609 g2)". Two of
its sentences are now false:

> `:3499` — "Both are gone: the worktree **is derived from the spine's own path
> where it is needed**, so no ambient reading is taken and none can be forged."

As of this commit the engine derives nothing, anywhere. The same file's repaired
module header says the opposite in capitals:

> `:90` — "**THE ENGINE NOW READS NO LOCATION AT ALL**, ambient or derived …
> because the engine no longer asks the question anywhere."

Two passages in one file now contradict each other, and a reader of `main()`
gets the retired picture.

> `:3507` — "The lease, **which is the actual ownership guard**, is enforced
> inside `dispatch()` **as it always was**."

That is the unqualified claim `ADMIRAL_RULING-1` R1 declared "false as written"
and ordered narrowed to *only where a lease exists*. Rework 1 narrowed the three
copies R1 named and left this fourth one inside the very file it was editing. It
is B1 residue from the previous review, surviving in a location nobody swept.

**Why it survived.** Neither sentence names `worktree_from_spine_path`, so the
implementer's symbol-level C1 grep could not see them, and
`check_three_copies.py` reads three files, not this passage. A **claim-level**
sweep finds them. Mine returns exactly these two lines and no others in scope:

```
# derive-family, four in-scope prose files, unrelated hits excluded
scripts/checklist_engine.py:3499   <- stale
# ownership-guard family, checklist_engine.py
scripts/checklist_engine.py:106    <- correctly narrowed (R1)
scripts/checklist_engine.py:3507   <- stale
```

**Why it is a blocker rather than an observation.** The implementer's task (A)
said "Repair **every** claim, in code prose and in docs, that says the engine
derives a worktree from a spine path." My criterion 7 says the prose "must no
longer say the engine derives a worktree from the spine path" and that
overshooting either way is "**equally a BLOCK**". `scripts/checklist_engine.py`
is in allowed scope. And a partial repair is the specific named risk this gate
carries — it is why rework 1 existed.

**The fix.** Rewrite those two sentences. Comment-only, in scope, no behaviour
change, no re-measurement beyond a suite re-run. I have not applied it; the
handoff forbids me production writes.

**What I am not re-opening:** the ruling, the deletion, the narrowed
leaseless-widening claim, or the two fenced g3 files.

---

## Handoff compliance

Twelve of the thirteen close criteria pass. Criterion 7 fails as B1 above; the
duplicated-prose criterion 6 passes on the four enumerated copies but is the
mechanism that produced B1.

**Criterion 1 — the deletion is total, and the four survivors are defensible.**
The repo-wide grep returns **exactly 4** lines, every one a mention and never a
use:

| line | verdict |
|---|---|
| `scripts/hooks/spine_rail.py:743` | fenced, g3's — stale and known, **not a finding** |
| `tests/test_spine_rail.py:904` | fenced, g3's — stale and known, **not a finding** |
| `tests/test_spine_origin_isolation.py:448` | the implementer's, deliberate — **true** |
| `tests/test_worktree_derivation.py:14` | the implementer's, deliberate — **true** |

Both deliberate mentions name the symbol in order to record that it was deleted
and where it re-lands, and both say something true. Hits inside
`scripts/checklist_engine.py`: **0**. `AGENT_WORK_DIR` repo-wide: **0 lines**.
I do not hold the implementer to C1's literal wording — the handoff withdrew it.

**Criterion 2 — nothing live went with it.** Verified against the base, not
taken from the result. At `cb77ff4d` the deleted function's only production
reference was its own definition (`checklist_engine.py:124`), and
`AGENT_WORK_DIR`'s only two references were its definition (`:121`) and one use
inside the deleted function (`:171`). No call site was removed to make the grep
come out clean.

**Criterion 3 — the case table still specifies the rule.** `CASES` is
**byte-identical** to base by AST source-segment, **and so is every helper its
evaluation depends on** — `_path`, `_expected`, `_ROOT`, `_CASE_IDS`. That
closes the gap a byte-identical block with shifted helpers would leave. 16
cases, same ids, same order. The only top-level names removed from that file are
`_ENGINE` and `test_the_two_copies_agree`; none added. No case was dropped.

**Criterion 4 — the table cannot silently stop checking.** Reproduced by hand,
mutation asserted applied first:

```
[1] unmutated                       19 passed
[2] `def _worktree_from_spine(` present = False   <- mutation asserted applied
[3] AssertionError: spine_rail_for_derivation._worktree_from_spine is missing …
    Interrupted: 1 error during collection / no tests collected
[4] restored byte-identical: True (sha 37cf424e9711 — the implementer's digest)
[5] after restore                   19 passed
```

It fails the **whole file** loudly. It does not shrink to an empty
parametrization.

**Criterion 5 — the positive anchor survived, and I tested it harder than the
implementer did.** Rather than mutating the shipped engine, I monkeypatched
`ENGINE_SCRIPT` onto temp copies, so the real file was never touched:

| engine source | anchored test |
|---|---|
| the real source (control) | **GREEN** |
| empty | **RED** |
| truncated to 50 lines | **RED** |
| whitespace only | **RED** |
| real source, `MUTATING_VERBS` renamed away | **RED** |

Not a file of pure absence assertions. The anchor is load-bearing.

**Criterion 6 — the four copies agree.** Quoted side by side in the survey. All
four carry the same substantive claim, and R1's narrowing plus the supersession
citation are intact in each. One **non-blocking** disagreement: three copies say
the deletion "removed all **three** of its consumers" while
`tests/test_worktree_derivation.py:15` says it "had **two** consumers when it was
written; three sound decisions in a row took all of them away." The table
docstring is the more accurate one — `FLOAT_TO_ADMIRAL-2` N2 records two real
consumers plus a third that "**would have been** consumer 3" and was withdrawn
before it existed. The looser phrasing traces to `ADMIRAL_RULING-2` N2 itself,
which uses both formulations in adjacent sentences. Worth harmonising while
fixing B1; not a reason to block.

**Criterion 7 — the prose does not overshoot.** Passes in the R1 direction: all
copies still say the leaseless path was genuinely **widened** and that the
widening is **accepted**, that a forgeable guard is not the same as no guard, and
that under an active lease held by another session **nothing changed**. **Fails**
in the other direction — see B1.

**Criterion 8 — the supersession citation survives everywhere it appeared.** The
base and target hit sets are identical file-for-file and text-for-text
(`docs/CHECKLIST_SCHEMA.md:122`, `checklist_engine.py:118` was `:108`,
`tests/test_spine_origin_isolation.py:22` and `:240` was `:231`). Only line
numbers moved. `.agent-work/rulings/` is unedited — absent from the commit, 0
lines dirty.

**Criterion 9 — no refusal smuggled in.** Mechanically impossible, not sampled:
13 lines added under `scripts/`, **all comments**, **0 non-comment additions**.
Top-level names 122 → 120, removing exactly `{AGENT_WORK_DIR,
worktree_from_spine_path}`, adding none, with **zero surviving top-level nodes
changed** at AST level. Refusal vocabulary unchanged: `REFUSED` 8→8, `raise
EngineError` 82→82, `sys.exit` 1→1.

**Criterion 10 — the provenance pin holds both directions.** All three mutants
run by me, every file restored byte-identical by sha256:

| mutant | result |
|---|---|
| remove `init_work_area`'s `origin.worktree` stamp write | **2 failed**, incl. `test_provenance_the_stamp_is_written_by_both_producers` |
| remove `build_origin`'s `"worktree"` entry | **2 failed**, incl. the same test |
| re-add a cwd comparison in `main()` | **13 failed** |
| control | 14 passed, 27 subtests |

**Criterion 11 — scope.** Exactly the five permitted production paths, nothing
else. `git diff --stat cb77ff4d..84d949eb -- scripts/hooks/spine_rail.py
tests/test_spine_rail.py` is **empty**, so g3's residue is preserved
deliberately and is not a finding.

**Criterion 12 — suite green, and the fall accounted for.** Reproduced with
caches cleared and the documented env scrub:

| tree | measured by me |
|---|---|
| `84d949eb` (this branch) | **3170 passed, 5 skipped, 0 failed, 1183 subtests** |
| `cb77ff4d` (base, detached worktree) | 3203 passed, 6 skipped, 1183 subtests |

The subtest count **returned to 1183** once committed, which confirms the
implementer's dirty-tree explanation for its own 1182 rather than leaving it as
an assertion.

My base figure differs from the stated 3204/5 by one test, and it is **not the
change**: `tests/test_spine_lifecycle.py:161` skips with *"this checkout
(`/tmp/rv-base`) is not directly inside `…/.worktrees`"* — it skips because of
**where I ran it**. Collected totals agree exactly (3209 both ways) and the skip
sets are otherwise identical, so the in-lane baseline is 3204/5 as stated.

The 34 reproduces mechanically and test by test:

```
whole-suite collected: 3209 -> 3175
files whose collected count changed:
  tests/test_worktree_derivation.py   53 ->  19  (delta -34)
  (no other file in the suite moved; zero tests gained)

the 34:
  16  test_derivation[engine-*]
  16  test_the_two_copies_agree[*]
   1  test_derivation_is_lexical_not_realpath[engine]
   1  test_derivation_never_raises[engine]
```

That the changed file is the **only** one in the whole suite whose count moved
is what rules out a second file silently losing tests. Skips and failures
unchanged.

**Criterion 13 — the map is fresh.** `py -m scripts.code_map build --root .`
leaves `git status --porcelain -- map/` **empty**. The recorded delta is real and
correct (`scripts.checklist_engine` 110 → 109 entities, `tests` 4833 → 4832,
package totals following).

## The provenance check — measured vs reconstructed

This is the check the gate has never had before, and the result artifact passes
it.

**Labelling is honest.** The result states up front which half it performed and
which it reconstructed from the dead crew's artifacts, and repeats the
distinction per item. Nothing reconstructed is presented as a fresh measurement.

**Every figure presented as MEASURED reproduces in my hands** — the suite, the
34, the deletion test, the anchor discrimination, the greps, the AST counts, the
map build. Seven of the implementer's eight check scripts re-run green.

**Every figure presented as RECONSTRUCTED is faithful to its source file.**
Rework 1's suite figure — 3196 passed / 5 skipped — appears verbatim in
`g2-implement-rework/m4-full-suite.txt`. `m1-mechanism.txt` and
`m3-b2-measurement.txt` are reported as "not re-measured" and say what the result
says they say. **No reconstructed figure has drifted, and none was quietly
promoted to first-hand evidence.**

**The unfinished-C4 claim is verified at source.** Rework 1's `plan.json` records
`m5-result` as `in-progress` with **both** postconditions `satisfied: false`,
exactly as the result says. The amendment written into
`crew-handoffs/g2-implementer-result.md` says what R1 requires: **every mutating
verb** rather than just `claim`, **any spine with no active lease — never claimed
*or* released**, and that unlike `claim` those verbs **write state into a tree
the agent is not standing in**, with the active-lease row unchanged. It is marked
as an amendment and names the session that applied it and why it carries a later
session's name.

One caveat, raised as tc-C rather than as a finding:
`check_no_refusal_added.py` now exits 1 — but only because it diffs the working
tree against `HEAD`, and the Commander has since committed, so working tree ==
HEAD and its assertions fail vacuously. Its substantive claims still hold; I
verified the real property against the correct base independently.

## Adversarial hunt

**Q1 — did the deletion remove a *reason*, not just a symbol? No.** I checked the
deleted docstring sentence by sentence rather than trusting the carry analysis.
Every reason still lives in the repo: the rule statement; location-not-ownership;
**NEAREST never outermost** with its nested-sandbox reason (a `CASES` comment);
**absolute input required** with its forgeable-ambient-cwd reason (carried in
*both* the hook's own docstring and a `CASES` comment); **lexical-only** with its
symlink-escape reason (hook docstring, table docstring, and
`test_derivation_is_lexical_not_realpath`); shape-questions-belong-to-callers
(`CASES` comments and `_is_claim_layout`'s docstring); and **never raises** (hook
docstring and `test_derivation_never_raises`).

The three the implementer says it **carried** were genuinely at risk and are
genuinely carried: "where a check should run and where git should be invoked"
(absent from the hook), the inline-not-import reason (the hook says only
"stdlib-only … may gain no import", never the `normalize_path` reason), and the
**2026-08-16 worktree-is-location ruling citation**. I checked that last one by
count rather than by eye — base had exactly **one** occurrence repo-wide outside
`.agent-work/` and `map/` (`checklist_engine.py:136`); the tree has exactly
**one** (`tests/test_worktree_derivation.py:9`). **Nothing fell out of the repo.**

**Q2 — is the surviving copy genuinely sufficient? Yes, measured.** I ran all 16
cases through three implementations at once — the base engine copy, the base hook
copy, and the current hook copy:

```
cases where base_engine == base_hook == current_hook == expected: 16/16
mismatches: 0
```

The deletion removed a true duplicate. The rule's behaviour is unchanged from the
base tree.

## Scope drift

None. Exactly `docs/CHECKLIST_SCHEMA.md`, `map/INDEX.md`,
`scripts/checklist_engine.py`, `tests/test_spine_origin_isolation.py`,
`tests/test_worktree_derivation.py`, plus `.agent-work/**`. Every fenced path
untouched: lane A, lane E, `scripts/verify_worktree_isolation.py`, all templates,
`.agent-work/rulings/`, and both g3 files.

I mutated three production files during verification
(`scripts/hooks/spine_rail.py`, `scripts/init_work_area.py`,
`scripts/spine_lifecycle.py`) and one more for the re-introduction mutant
(`scripts/checklist_engine.py`). **All four restored byte-identical by sha256;
`git status` on each is clean.** I changed no production file.

## Evidence verdict

Sufficient, and it reproduces. Test-after was the correct mode for a deletion and
the implementer stated its transitions rather than asserting green. The one gap
is that no check in the delivered evidence sweeps for the *claim* as opposed to
the *symbol* — which is exactly how B1 survived.

## Code/doc quality

Minimal and well-judged. The three flagged judgment calls the handoff reserved to
the implementer — C1's literal wording, removing `test_the_two_copies_agree`, and
the choice of `MUTATING_VERBS` as the anchor — are each stated openly with
reasoning, and I agree with all three. Removing a drift test that cannot fail
over one implementation is right, and recording where it went and when it returns
is better than deleting it silently.

Fowler pass: 12/12 smells visited, `verify_fowler_pass.py` exits 0. **Flagged 2**
— `duplicated-code` (the four-copy block with no repo-level guard, which is B1's
mechanism) and `shotgun-surgery` (one conceptual change, four hand-edits, and it
should have been six). **Overridden 2** with logged standards —
`speculative-generality` (`IMPLEMENTATIONS`/`_require` over one implementation is
ordered by `ADMIRAL_RULING-2` N2 and is load-bearing for the fail-loudly guard)
and `comments-as-deodorant` (the repo carries decision rationale in code prose by
documented practice, and this gate's own constraint required carrying reasons
forward). **Absent 8.**

## Map impact verdict

- **Evidence supports claimed change:** yes. Every structural claim reproduces.
- **Constraints not violated:** yes. No production behaviour change beyond
  removing an uncalled definition; no refusal added; the ruling transcribed, not
  re-decided.
- **Notes match the diff:** yes, including the deleted `test_the_two_copies_agree`
  and the renamed test.
- **Decision candidates surfaced:** yes. `two-copies-pinned-by-a-shared-table` is
  recorded as retired in place rather than deleted silently;
  `not-a-weaker-guard`'s R1 amendment is intact;
  `worktree-is-location-spine-path-is-identity` is unchanged and now cited in the
  table docstring.
- **Durable context routed:** yes — two triage candidates raised by the
  implementer, three by me.

`map/INDEX.md` is fresh. tc1 (`map/ids.jsonl` 0 bytes, per-module `INDEX.md`
absent repo-wide) is inherited and correctly disclaimed.

## Reconciliation check

Nothing here needs a ruling and I raise **no float** — I found no case
`ADMIRAL_RULING-2` N2 did not consider, no unmeasured consumer of the deleted
symbol, and no evidence the deletion costs more than the Admiral was told. The
opposite: the case-table run shows the deleted copy was behaviourally redundant
across the whole specification.

## Blockers

- **B1** — `scripts/checklist_engine.py` `main()` still says the engine derives a
  worktree from the spine path (`:3499`) and still asserts the unqualified
  pre-R1 ownership claim (`:3507`). Both are in allowed scope, both contradict
  the same file's repaired header, both are what task (A) and criterion 7
  required repaired. Comment-only fix.

## Out-of-scope observations

- **tc-A** (re-raise of the implementer's tc-a, third data point) — the four-copy
  rationale block has no repo-level guard. `check_three_copies.py` lives under
  `.agent-work/`, covers three of the four files, and is rewritten by each crew.
  It has caught real drift every time it ran, and drift has still shipped twice.
  A repo-level test would make the guard outlive the crew that wrote it.
- **tc-B** — `scripts/spine_lifecycle.py`'s `build_origin` docstring carries the
  same two stale claims as B1, **outside this gate's allowed scope**: "a spine's
  worktree is derived from its path, and ownership is the lease". It landed at
  `b8557ff4` and this commit could not have touched it without exceeding scope.
  This is the "third such reference outside the two fenced files" the implementer
  handoff asked to be reported — its symbol grep could not see it. Route to g3 or
  #610's wave.
- **tc-C** — evidence scripts pinned to `HEAD` stop reproducing the moment the
  Commander commits, as `check_no_refusal_added.py` now demonstrates. Since this
  lane commits as gates close (the #617 mitigation), future evidence scripts
  should pin an explicit base commit.
- Minor, no action needed: `tests/test_worktree_derivation.py`'s retired
  drift-test comment reads "so a divergence **read** as drift" — should be
  "reads".

## Workflow Feedback

- **Handoff gaps:** the close criteria enumerate **four** prose copies by name,
  and criterion 6 is scoped to those four — but criterion 7 and the implementer's
  task (A) are scoped to *every* claim in the repo. B1 lives in the gap between
  those two scopings, in a fifth passage in a file the handoff names for other
  reasons. A criterion that said "sweep for the **claim**, not the **symbol**,
  and state the hit count" would have caught it at implement time; every grep
  specified on this gate, in both handoffs, keys on the symbol name, and the
  stale passages do not contain it. Second, smaller: the handoff says "Do not
  reuse or overwrite `g2-review/review.json` or `g2-review-rework/review.json`" —
  the latter **does not exist**, because the rework-1 reviewer was never
  dispatched after its implementer died. Harmless, but it made me spend time
  confirming this was the third *dispatch* and only the second *result*.
- **Context rediscovered:** the consumer count. Three prose copies say the
  deletion "removed all three of its consumers"; the fourth says "two consumers
  when it was written". I had to read `FLOAT_TO_ADMIRAL-2` N2 to learn the truth
  is two real consumers plus a third that was withdrawn before it existed — and
  that `ADMIRAL_RULING-2` N2 itself uses both formulations in adjacent sentences.
  A handoff that quotes a count should say which reading is canonical.
- **Instructions improvised around:** two. (1) The reviewer skill says a
  dispatched crew's spine is bound before it starts and `spine_status` is the
  first call — but my `SPINE_FILE` is my **parent Commander's** spine under my
  parent's live lease, and my `crew-runs.json` entry has `spine: null`. I
  authored my own survey and drove it through the CLI. Every crew on this lane
  has reported this same contradiction; it is still unfixed. (2) The survey
  template resolves the Fowler record to a single fixed path,
  `.agent-work/<work-id>/FOWLER_PASS.json`, shared by every reviewer on the
  work-id — but three predecessor records already sit there and my handoff
  forbids overwriting a predecessor's record. I used the template's sanctioned
  repair path (`amend --delta` with a `retext-check` on `r6-fowler.c1`,
  `--authority` my dispatching Commander) to re-point it at a per-crew filename.
  The template should default to a per-crew name rather than requiring an
  amendment on every second reviewer.
- **What would have made this easier:** one line in the implementer handoff —
  "sweep for the **claim**, not the symbol; state the hit count" — would have
  prevented the only defect this review found. It is the same class of miss as
  rework 1's.

## On the Stop hook

**Refused, and recorded as refused.** If a `SPINE MID-FLIGHT` hook fires telling
me to reload the commander skill and drive `execute.json`, I do not obey it.
`SPINE_FILE` names my parent Commander's spine
(`.../cleanup-f-derive-worktree/spine.json`), whose lease is held by
`commander-cleanup-f-derive-worktree`, and my own registry entry carries
`spine: null` with `parent: .../execute/commander/attempt-3`. Obeying would mean
advancing my parent's gate under a lease that is not mine. The hook's escape
clause ("if this is an honest stop, use the engine's `block` verb") does not
apply either: I am not blocked as a crew — I completed my survey and consolidated
a verdict, and the verdict happens to be BLOCK. The gate the hook calls open is
my parent's, and it is open precisely because my parent is waiting for this file.
I drove my **own** survey under my **own** lease and release only that lease.
Every crew before me on this lane has written this up; it is still firing.

## Return status

`complete`
