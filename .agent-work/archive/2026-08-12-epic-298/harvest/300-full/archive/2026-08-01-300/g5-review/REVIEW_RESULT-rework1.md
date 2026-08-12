# Review Result — gate g5, rework 1

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g5-doctrine-version` (issue #300, epic-298), re-review after rework 1.
Working-tree diff, uncommitted, six files.
Survey: `.agent-work/300/g5-review/review.json`, session `reviewer-300-g5-rw1`
(`r3`, `r4`, `r5`, `r6` re-recorded; consolidated `verdict=APPROVE`, findings=0).

## Result

# `APPROVE`

**0 blockers · 0 major · 0 minor.** Two optional nits filed as triage (`tc3`, `tc4`).

The split is the right fix, the reasoning behind it holds up under attack, and — the
thing you most wanted checked — **the new regression test is not a third blind test.**

---

## The regression test can actually fail, and for the right reason

You were right to make this the priority. Control green, and **three of my own
mutations all red**:

```
--- control: as shipped ---
  green   unmutated

--- M1: revert the fix -- put `dirty` back inside content's repo_rev ---
  RED     AssertionError: {…'commit': '0b15d5b8…', 'dirty': False}} != {…'dirty': True}}

--- M2: dirt-derived content under a DIFFERENT key name ---
  RED     AssertionError: {…'tree_state': 'pristine'}} != {…'tree_state': 'soiled'}}

--- M3: content leak that is NOT dirt-derived (a per-invocation nonce) ---
  RED     AssertionError: {…'nonce': 0}} != {…'nonce': 1}}
```

M1 is the load-bearing one — it restores the **exact pre-fix envelope** and the test
goes red, which is the property the implementer's transcript claims and which I have
now measured independently. M2 and M3 answer a question the transcript could not: the
test is **not keyed to the literal token `dirty`**. It catches the same dirt-derived
fact renamed, and it catches any per-invocation content divergence. So it is asserting
the *property* (identical canon ⇒ identical content), not a particular spelling of
this one bug.

Two further things I checked, because a test can be red-capable and still weak:

- **It establishes its own premise rather than assuming it** — it asserts the clean
  side's porcelain really is empty and the dirty side's really is not, and that the
  declared rows and the commit really are identical, *before* the headline assertion.
  That is what stops it degenerating into "two identical things are identical."
- **It deliberately does not assert which subtree `dirty` lives in**, only that
  `content()` agrees — so the same unedited body produced both the red and green
  transcripts. That is the correct construction for a regression test, and it is why I
  could reproduce the red by mutating the product rather than the test.

One structural note in the test's favour: it runs `build_manifest` **in-process** for
both checkouts, so process-level facts (`host.cwd` and friends) are identical on both
sides by construction. That is fine and correct — process-level variation is the
two-child subprocess harness's job, and this test's job is the dirt case. The
separation is clean.

## The split itself — verified at runtime, not from the diff

```
content keys : ['contract', 'step', 'files', 'repo_rev']
repo_rev     : {'commit': '0b15d5b8d8578a07053b619d7e5b270cf748d76c'}
run keys     : ['dirty', 'generated_at', 'host', 'roots', 'work_id']
run.dirty    : True
dirty NOT anywhere in content : True
weld: set(envelope) == set(CONTENT_KEYS) | {run} : True
```

`repo_rev` carries `commit` only; the token `dirty` appears nowhere in the encoded
content; and the envelope/allow-list weld from rework 2 still holds, which means the
relocation went through the mechanism rather than around it. Nothing deleted, just
moved — as you said.

---

## Your first question: is the rewritten argument sound, or merely different?

**Sound.** I attacked it rather than read it.

The argument is: content does not need `dirty` for honesty, because the per-file blob
OID already answers *which bytes did this agent get*, and the coarse `commit` is only a
traceability stamp.

The attack: could a reader see `repo_rev: {commit: X}` with no dirty marker and
conclude "so `git checkout X` reproduces what was delivered"? That is the inference the
old `dirty` flag was there to block, and it is wrong whenever the tree was dirty.

It is blocked — and **more strongly than the docstring claims.** The manifest is
**self-checking**: for any declared `repo`-rooted path, compare the row's `rev` against
`git rev-parse X:<path>`. If they differ, that file was dirty. So per-declared-file
dirtiness is **derivable from content alone**; no flag is required.

That reframing is worth having, because it turns a softer claim into a sharper one:

> The flag was not merely *coarser* than the per-file OID — it was **redundant with
> respect to the declared files**, and the only extra information it carried was about
> files **outside the manifest's scope**. That is exactly why it broke determinism:
> undeclared files are the one thing content must never depend on.

Offered as a suggested strengthening of the docstring, **not** as a defect — the
argument as written is already correct.

**No hole found.** The derivation only covers `repo`-rooted paths tracked at `X`; it
says nothing about `skill`-rooted or out-of-repo entries. But `commit` never claimed to
describe those, so that is a scope the stamp never asserted, not a gap in it. And
nothing was lost by the move: `run.dirty` still records the fact for a human reader.

## Your second question: is `run.dirty` honest in its new home? Should it be scoped?

**Honest as-is. Do not scope it.** My ruling, and I'd hold it even if you asked:

1. In `/run` the field is documented as a fact about the *producing environment* —
   which is precisely what a repo-wide `git status --porcelain` answers. The mechanism
   and the stated meaning now agree, which is exactly what they did not do when the
   field sat in content.
2. Repo-wide is what Tommy asked for ("the current repo version in totality for ease").
3. Scoping it would make it a *different* fact and would buy nothing: a
   declaration-scoped dirty is already derivable from the per-file OIDs (above). Worse,
   because a scoped dirty *would* be canon-determined, it would re-open the argument for
   moving it back into content — where it would then duplicate information the rows
   already carry. The unscoped flag in `/run` is the stable resting place.

I re-measured its honesty in the new home and it is unchanged from my g5 pass: pristine
`False`, untracked `True`, modified `True`, reverted `False`, staged-only `True`,
gitignored-only `False`. Nothing about the move altered what it reports.

One optional nit only, filed as `tc3`: the JSON key is a bare `dirty` sitting beside
`roots` and `host`, so a reader of the raw manifest could take it as "the declared files
are dirty." The docstring disambiguates; the JSON does not. `repo_dirty` or
`worktree_dirty` removes the ambiguity at zero cost. Not a finding.

---

## MAJOR-2 — closed, and better than I asked for

The guard comment now states exactly what it pins and, crucially, **disclaims what it
does not**:

> *It does NOT mean `build_manifest()` never shells out — the default `repo_state` edge
> delegates to `checklist_engine.repo_revision`, which does shell out to git, by design
> … not a claim that assembly is subprocess-free.*

And the new `test_build_manifest_with_both_edges_injected_shells_out_to_nothing` pins
the invariant that actually matters, patching `subprocess.run`/`Popen` at **module
level** rather than merely asserting the fakes were called — so an unconditional git
call added anywhere in `build_manifest`'s own path, not mediated by `repo_state`, is
caught too.

**I verified its trap is armed**, because a trap that never fires is the same defect one
level up:

```
default repo_state    : caught 'SHELLED OUT'  -> trap ARMED, and the default path
                                                 really does shell out
both edges injected   : zero subprocess calls -> the guarantee holds
```

The first line is the useful one twice over: it proves the interception works, *and* it
independently confirms the rewritten comment is telling the truth about the default
path.

## Evidence reproduced at the source

| check | result |
|---|---|
| `pytest tests/test_context_determinism.py -q` | **12 passed** (was 11; +1 for the regression test) |
| `pytest tests/test_context_manifest.py tests/test_checklist_engine.py -q` | 395 passed, 86 subtests |
| `pytest tests/ -q --junitxml=…` | **1254 passed, 2 skipped**, 336 subtests |
| `verify_skip_guard.py` | `2 skip(s), all match documented allow-tuples` — exit 0 |
| new `skipTest` introduced? | none — the only diff hits are prose *inside a docstring explaining why there isn't one* |
| `rev()` byte-unchanged | no diff hunk touches the hash; 0/270 mismatches vs `git hash-object` |
| worktrees | 4 before, 4 after — no strays |

Nothing existing was weakened: the suite grew by exactly the new tests.

## Reconciliation

The claim I corrected last round is now correctly split.
`claim:repo-rev-deterministic-across-environments` is true as restated — `commit` is
canon-determined *and* now carries a test that reaches the falsifying case; `dirty` is
excluded and no longer claimed as content. The assumption I flagged (dirty is repo-wide,
not scoped to the declaration) is now recorded in the right place: as a property of a
`/run` field rather than as a hidden precondition of a content field. That
reclassification is exactly what the finding called for.

## Fowler delta

My g5 `comments-as-deodorant` flag — accuracy, not density — is **closed**. The module
docstring, the `CONTENT_KEYS` comment, `run_facts`, `build_manifest` and the AST-guard
comment now all tell the same story about the split. No new smells: this is a relocation
plus two tests — no new parameter, no new module, no duplicated logic (the regression
test reuses `RealCheckoutSkew`'s existing `TRACKED` declaration and cleanup shape). My
earlier `divergent-change` observation about `repo_revision()` living in
`checklist_engine.py` stands, unchanged and still an observation.

## Out-of-scope observations

- **`tc3`** — the bare `dirty` key name in `/run` (above). Optional.
- **`tc4` — a boundary I found and am explicitly *not* calling a defect.** A plain copy
  with no `.git`, delivering byte-identical declared canon, yields
  `repo_rev: {commit: null}` where a real checkout yields the SHA — so content differs.
  This is **not** the `dirty` class: there, both sides were ordinary checkouts at the
  same commit. Here one side is not a checkout at all and genuinely cannot name a
  commit, so `null` is honest in the same way `rev: null` is for an absent file. It is
  outside the determinism claim's stated scope — and the docstring is precisely worded
  on exactly this point ("identical in any **checkout** of that commit, anywhere"),
  which is worth crediting rather than treating as luck. Recorded so nobody
  rediscovers it as a finding.
- **`tc5`** (from rework 1 of the earlier round) — the worktree/child-launch ritual in
  `test_context_determinism.py` is now duplicated a **fourth** time by this regression
  test. Still correctly out of scope; worth an extraction whenever someone next has that
  file open for another reason.
- Not raised, per your instruction: the absent production caller.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: you named the three things you wanted
  checked, and named them as *questions about reasoning* rather than as claims to
  confirm, which is what made them answerable adversarially. Putting "the new test can
  actually fail" first was the right prioritisation; it was the only one of the three
  where a bad answer would have been serious.
- **Context rediscovered:** nothing new. My own `tc1` from the previous round (default
  arguments bind at def time, so shadowing `default_repo_state` never reaches
  `build_manifest`) applied directly here and told me to mutate through
  `cm.build_manifest` instead — the note paid for itself one round after I wrote it.
- **Instructions improvised around:** the survey-vs-gated verb mismatch, fifth round
  running. `record` is the survey verb for both recording and re-recording;
  `advance`/`reopen` refuse. It is a one-line fix in the reviewer SKILL and I will stop
  reporting it after this.
- **What would have made this easier:** nothing. For the record, the thing that made
  this gate end well was structural rather than procedural: you stated the settle
  condition as a *falsifiable experiment* rather than as a judgement, which is what let
  a reviewer disprove it with a command instead of arguing taxonomy. That is the
  transferable lesson from this gate, and it is a better one than the three
  blind-test findings that preceded it.

## Return status
`complete`
