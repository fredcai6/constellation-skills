# Review Result — gate g5

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g5-doctrine-version` (issue #300, epic-298) — the repo-revision traceability stamp
after Tommy's 2026-08-01 ruling. Working-tree diff, uncommitted, `+259 / −11` over
five files (HEAD is still `0b15d5b`).
Survey: `.agent-work/300/g5-review/review.json`, session `reviewer-300-g5`,
7/7 items visited, consolidated `verdict=BLOCK`.

## Result

# `BLOCK`

**1 blocker · 1 major · 2 triage candidates.**

You asked me to attack the placement judgement. I did, and **it does not hold — for
the `dirty` half.** The settle condition you named has now actually been run, and it
comes back `/run`. `commit` is fine and belongs exactly where you put it.

---

## BLOCKER-1 — `repo_rev.dirty` is not a fact about canon; the settle experiment says `/run`

You graded the placement a guess and named the settle condition yourself:

> *if two checkouts at the same commit disagree on the field, it belongs in `/run`.*

I built exactly that case. **They disagree.**

Construction, chosen so the only variable is the one under test:

- two fresh worktrees at the **same commit** (`0b15d5b`);
- **nothing overlaid**, so one stays genuinely clean (this is where the shipped test
  differs — see below);
- the declaration names only files that are **tracked and unmodified** here, so both
  checkouts deliver **byte-identical canon**;
- the dirt is confined to `docs/CHECKLIST_SCHEMA.md`, which **no declaration names**.

```
  clean   porcelain: ''
  dirty   porcelain: 'M docs/CHECKLIST_SCHEMA.md'

  declared rows identical : True
  same commit             : True
  repo_rev(clean)         : {'commit': '0b15d5b8d857…', 'dirty': False}
  repo_rev(dirty)         : {'commit': '0b15d5b8d857…', 'dirty': True}

  >>> CONTENT byte-identical across two environments at the same commit: False
  >>> ONLY differing content key(s): ['repo_rev']
```

Identical canon delivered; the content disagrees. That is the definition of a field
that belongs in the excluded subtree.

**The split is surgical, and it matters.** `commit` *is* canon-determined — identical
in both checkouts, and it would be identical in any checkout of that commit anywhere.
Only `dirty` varies, because `dirty` is a fact about **the working tree that produced
the manifest**, not about the bytes it delivered. Two agents at the same commit, one
mid-edit on an unrelated file, hand you the same doctrine and two different content
records.

### Why the test's silence is accidental, not meaningful — measured both ways

This was your sharper question, and it has two halves that must be answered separately:

**Can the test see the field?** Yes. I mutated `repo_revision` to be
environment-dependent, twice — once through `commit`, once through `dirty` — and both
are **CAUGHT** by `test_content_is_byte_identical_excluding_exactly_the_run_subtree`,
with baseline green:

```
 survived  baseline (control)                              ran=7 failing=none
   CAUGHT  repo_rev varies with the environment            ran=7
   CAUGHT  repo_rev.dirty varies with the environment      ran=7
```

I also instrumented the real children to rule out the vacuity I found in round 1:
`repo_rev` is genuinely present in the compared bytes with a real value
(`{'commit': '0b15d5b8…', 'dirty': True}`), not `{None, None}`.

**Can the test reach the varying case?** No — and this is the whole point. Both
children are dirty **by construction**: `setUpClass` overlays the same three
working-tree files into both worktrees, so both are equally dirty, and I measured that
both read `dirty: True`. The harness holds constant the exact variable that would
falsify the placement.

Your own gate imperative says it out loud: *"both children are worktrees at the SAME
commit **and are equally dirty**, so the field is identical across environments."* The
"and are equally dirty" clause is the tell — the test passes because of an incidental
property of the harness, not because the field is canon-determined. So the empirical
answer did not "come back content"; the question was never put.

### What I am *not* asking for

This is a design decision above my latitude and I am not picking the redesign. Under
`@grade: guess` doctrine the settle experiment has now been run and says `/run` for
`dirty`; the ruling is yours (or Tommy's). The options I can see, with the honest cost
of each:

1. **`commit` in content, `dirty` in `/run`.** Restores the determinism property
   exactly. Cost: the content stamp no longer carries its own honesty marker — the
   incoherence your gate text explicitly warned about. Mitigated somewhat by the fact
   that the per-file `rev` rows already answer "which bytes did this agent get,"
   which is the question `dirty` was protecting.
2. **Scope `dirty` to the declared paths.** A declaration-scoped dirty *is*
   canon-determined: if the declared bytes are identical, their dirtiness relative to
   HEAD is identical too. This makes the field legitimately content and keeps the
   stamp honest. **One correction to the implementer's stated reason for rejecting
   it:** they judged it needs "a full git-index/tree-object reimplementation ... or a
   second git call per declared file." It needs neither — `git status --porcelain`
   accepts pathspecs, so it is one call with the declared repo-rooted paths appended.
   Cost is not the objection; the real objection is that declarations span three roots
   and only `repo` is inside the repository, so `skill`- and `durable`-rooted entries
   would be outside its reach. That is a real design question, but it is a different
   one from the cost they cited.
3. **Keep it and weaken the claim.** Document that content is environment-independent
   *given an equally-dirty tree*. I'd argue against — that is the kind of
   asterisk this issue has spent three rounds removing.

Whichever you pick, the acceptance test should grow the case it currently cannot
reach: **two checkouts at the same commit, unequally dirty.** That is a five-line
addition to `RealCheckoutSkew`, which already builds a clean second checkout and
already materialises undeclared dirt.

---

## MAJOR-2 — the AST guard's comment now asserts a property the code does not have

`tests/test_context_manifest.py`, `ProducerGuards.test_producer_shells_out_to_nothing`,
unchanged by this diff:

```python
# `rev` is computed in-process: no `git` process, and no network or LLM call
# at assembly time. The manifest is a pure function of (canon, selector).
```

`build_manifest()` now spawns **two `git` subprocesses per call by default** — the
implementer says so themselves ("every existing test/fixture that builds a manifest
over a plain (non-git) tempdir now also triggers two extra `git` subprocess calls per
`build_manifest()` call").

**Your specific question — is the import a technicality that defeats the guard?**
Half. The guard is **not weakened**: it still bans the identifier `subprocess` in that
file's AST, and that is a real, if narrower, property. The implementer is right that
it stays literally true. But the comment states the guard's *purpose*, and the purpose
is no longer served — assembly *does* shell out now, and the manifest is *not* a pure
function of (canon, selector); it is a function of (canon, selector, working-tree
state). A reader will believe the comment.

This is the same class as the cold panel's two blockers and my own round-1 MAJOR-2: a
claim the mechanism does not deliver. Notably the **module docstring was updated
honestly** in this same diff (it now says "no `git` subprocess **in this file**") — so
the two now contradict each other, and only the honest one was revised.

Fix is small and there is a stronger version available: re-comment to what the guard
actually pins, and consider adding the assertion that would pin the guarantee that
still matters — that `build_manifest` with **both** edges injected performs zero
subprocess calls. That is the real invariant (injectability), and nothing currently
tests it.

---

## The other three hunts — all sound

**Is `dirty` honest?** Yes. I measured every kind of dirt against a fresh worktree:

| tree state | `dirty` |
|---|---|
| pristine checkout | `False` |
| + untracked file | `True` |
| + modified tracked file | `True` |
| after revert | `False` |
| + staged change (index only) | `True` |
| + file under gitignored `.agent-work/` | `False` |

**Your specific worry — `dirty: false` with untracked files present — does not
occur.** `git status --porcelain` reports untracked as `??` by default, and the code
does not pass `--untracked-files=no`. The ignored-files row is honest by git's own
definition, though see `tc2`.

**Silent `{None, None}` — right or loud?** **Right, and I rule it so.** It is a
*visibly-absent* value, not a plausible wrong one — the same shape as `rev: null` for
an absent file, which this design explicitly sanctions ("absence is normal, never
raise"). That is precisely the opposite of last round's `declaration_of` case, where
silence produced an **empty manifest that looked valid**. Different failure mode,
different correct answer.

Two details that make it right rather than merely defensible, both of which I checked:

- `default_repo_state` returns `{None, None}` when `roots` has no `repo` key, instead
  of falling through to `repo_revision(None)`. I verified that fallback would otherwise
  stamp **whatever repository the process's cwd happens to sit in** — a wrong answer,
  not an absent one. The guard against it is correct and load-bearing.
- A partial stamp (`{commit: <sha>, dirty: None}` when `rev-parse` succeeds but
  `status` fails) is honest: "I know the commit, I don't know if the tree is clean" —
  better than defaulting `dirty` to `False`.

**Did the bidirectional envelope assertion grow legitimately?** Yes — it is
*strengthened*, not weakened:

- `test_the_envelope_is_exactly_the_content_allowlist_plus_run` is **parameterised on
  `CONTENT_KEYS`** (`set(m) == set(CONTENT_KEYS) | {"run"}` and
  `list(content(m)) == list(CONTENT_KEYS)`), so it auto-welds the new key rather than
  being edited around it. This is exactly the property I asked to be preserved in
  rework 2, and it did its job here without anyone touching it.
- `test_content_excludes_exactly_the_run_subtree` is **unchanged** and still
  bidirectional.
- The `four_keys` → `five_keys` edit pins the exact **ordered** list
  `["contract", "step", "files", "repo_rev", "run"]`, which is stronger than a set.

## Evidence reproduced at the source

| command | result |
|---|---|
| `git diff --exit-code -- tests/test_context_determinism.py` | exit 0 — byte-unchanged |
| `pytest tests/test_context_determinism.py -q` | 11 passed, 14 subtests |
| `pytest tests/test_context_manifest.py tests/test_checklist_engine.py -q` | 392 passed, 86 subtests |
| `pytest tests/ -q --junitxml=…` | **1250 passed, 2 skipped**, 336 subtests |
| `verify_skip_guard.py` | `2 skip(s), all match documented allow-tuples` — exit 0 |
| `rev()` byte-unchanged | no diff hunk touches the hash |

All your reported numbers hold. The blocker is not that the evidence is wrong — it is
that the critical piece of it does not support the claim it is offered for.

## Fowler pass

All 12 baseline smells recorded to `.agent-work/300/g5-review/FOWLER_PASS.json`;
`verify_fowler_pass.py` exits 0. Flagged: `comments-as-deodorant` (that is MAJOR-2 —
accuracy, not density), and `divergent-change` as an observation: `repo_revision()` is
a general-purpose git fact with no checklist involvement, placed in
`checklist_engine.py` for one reason — to keep another module's AST guard literally
true. Defensible as reuse of the existing `_git()` helper, but the *driver* was a
test's implementation detail rather than cohesion, and the docstring says so outright.
If a third such git fact arrives, a small shared git-facts module is the honest move
rather than accreting them where an AST guard happens to point.

**Notably absent: speculative-generality.** I checked this specifically, because
rework 2 had just deleted six zero-caller seams and a re-growth would be a regression.
`repo_state` is not that — it has a real default caller and a real injection test, and
the injectability is what keeps the existing non-git-tempdir fixtures working.

## Out-of-scope observations

- **`tc1` — a latent trap in the poison framework you just built.** Shadowing
  `default_repo_state` by appending source does **not** reach `build_manifest`, because
  it is bound as a **default argument at def time**. I hit this myself: my first
  mutation run reported "the acceptance test cannot see `repo_rev`" and I nearly
  recorded a false blocker before spotting that my mutation had never taken effect. The
  shipped `POISONS` (`encode`, `content`) are call-time global lookups so they work
  correctly — but a future poison aimed at `repo_state` would silently no-op and read
  as green. Worth one comment beside `POISONS`.
- **`tc2` — un-gitignoring `.agent-work/` will make `dirty` permanently `True`.**
  Measured above: a file under gitignored `.agent-work/` reads `dirty: False` today.
  Once that directory is tracked, every run dirties the tree — including writing the
  manifest itself, which lands there. The field would then be constant-true and carry
  no information. You fenced the un-gitignoring as out of scope and I have not blocked
  on it, but it changes what `dirty` **means**, not just where the manifest is stored,
  so it should be decided together with BLOCKER-1 rather than after it.
- Not raised, per your instruction: the absent production caller.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: you named the design judgement you
  most wanted attacked, named its settle condition in falsifiable terms, listed four
  specific hunts, and fenced two things explicitly. The settle condition being stated
  as a concrete experiment ("two checkouts at the same commit disagree") is what made
  this reviewable at all; without it I would have been arguing taxonomy instead of
  running an experiment. Keep that pattern.
- **Context rediscovered:** that the determinism harness overlays into **both**
  children and therefore dirties both equally. That fact is what makes the acceptance
  test unable to answer the placement question, and it is visible only by reading
  `setUpClass`. A gate that leans on a test as a settle condition should state what the
  test holds constant — your imperative actually *did* say "and are equally dirty",
  which is to your credit; it just wasn't read as the caveat it is.
- **Instructions improvised around:** the survey-vs-gated verb mismatch again
  (`record` is the survey verb for both recording and re-recording; `advance`/`reopen`
  are gated-only). Fourth round, same friction. Separately: a finding string containing
  backticks was mangled by the shell when passed to `--finding`, silently dropping two
  words from the journal — worth knowing that engine finding text needs single-quoting.
- **What would have made this easier:** nothing about the brief. The one process note
  is that this gate's settle condition was checkable by an experiment nobody had run,
  and the gate's own postcondition (`c3`: "the determinism test still passes unchanged")
  was satisfied by a test that structurally could not fail on this question. **A
  postcondition that a test still passes is not evidence unless someone has shown the
  test can fail on the specific property.** That is the third time in this issue that
  the same shape has bitten, and it is worth a lesson.

## Return status
`complete`
