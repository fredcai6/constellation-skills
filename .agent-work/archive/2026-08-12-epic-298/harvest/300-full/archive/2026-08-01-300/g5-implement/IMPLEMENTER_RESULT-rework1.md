# Implementation Result — Rework 1

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5-doctrine-version` (issue #300, epic-298), rework round 1 against
`.agent-work/300/g5-review/REVIEW_RESULT.md` (verdict BLOCK: 1 blocker, 1 major, 2 triage
candidates) and `.agent-work/300/g5-implement/REWORK-1.md`.

## Completed slice
Fixed BLOCKER-1 (the placement error) and MAJOR-2 (the stale AST-guard comment), both named in
REWORK-1.md, and nothing else. The error was in the gate imperative I inherited, not a redesign: it
named a settle condition ("if two checkouts at the same commit disagree on the field, it belongs in
`/run`") and then assumed its own conclusion by asserting the two determinism-test children would
always be "equally dirty." A reviewer ran the excluded case for real and found the two fields
disagreed.

**The split, surgical as specified:** `repo_rev` stays admitted into `CONTENT_KEYS` but now carries
`{commit}` only — canon-determined, identical for any checkout of that commit. `dirty` moved into the
excluded `run` subtree (`run.dirty`) — a fact about the working tree that *produced* the manifest, not
about the bytes it delivered. Nothing was deleted: `dirty` is still computed, still present in every
manifest, just in the right subtree.

## Scope
**Files changed:**
- `scripts/context_manifest.py` — `build_manifest()` now calls `repo_state(roots)` once and splits the
  returned `{commit, dirty}` pair at assembly: `repo_rev` in content becomes `{"commit": ...}`;
  `run_facts()` grew a `dirty` parameter and the `run` subtree now carries `run.dirty`. Module
  docstring point 1, the `CONTENT_KEYS` comment, and `default_repo_state()`'s docstring all rewritten
  to state the split and why it does not reopen the honesty gap a bare commit SHA has (the per-file
  blob OID already answers "which bytes did this agent actually get" for a dirty/untracked/out-of-repo
  file — that was the question `dirty` was really protecting).
- `scripts/checklist_engine.py` — `repo_revision()`'s docstring rewritten: removed the disproven claim
  that `dirty` keeps the repo-wide SHA honest *inside content*; replaced with the corrected argument
  (commit is canon-determined so it's safe as content; dirty describes the producing working tree, not
  the delivered bytes, so it belongs in `/run`; the split is made once, at `build_manifest`'s assembly
  point — this function still returns both fields together as a general repo-facts primitive, not
  pre-shaped to one caller's content/run boundary).
- `docs/CHECKLIST_ENGINE_DESIGN.md` — "Two-level revision scheme" paragraph rewritten to describe the
  split, the reviewer's BLOCKER-1 construction, and why the split is safe.
- `tests/test_context_manifest.py`:
  - `RepoRevContent` — every test asserting the old `{commit, dirty}` shape updated to the split shape;
    added `test_dirty_lives_in_run_not_content` and `test_content_is_unaffected_by_dirty_when_commit_is_equal`
    (fast, in-process complement to the git-worktree regression: two `repo_state` fakes sharing
    `commit` but differing on `dirty` must produce byte-identical `content()`).
  - `ProducerGuards` — MAJOR-2 fix: `test_producer_shells_out_to_nothing`'s comment corrected to state
    its actual, narrower AST-level property (no longer claims assembly never shells out). Added
    `test_build_manifest_with_both_edges_injected_shells_out_to_nothing`, which patches
    `subprocess.run`/`subprocess.Popen` module-wide to raise if called, then builds a manifest with
    both `reader` and `repo_state` faked and asserts it completes — the real invariant (injectability),
    which nothing tested before.
- `tests/test_context_determinism.py` — added
  `RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content`,
  the reviewer's own reproduction turned into a permanent regression (see "TDD evidence" below). No
  existing test in this file was weakened, deleted, or edited.

**Untouched, confirmed unchanged:** `scripts/context_manifest.py`'s `rev()` and the per-file row shape;
`docs/CHECKLIST_SCHEMA.md`; `tests/test_checklist_engine.py` (still carries round-1's diff only, not
touched this round). The absent-production-caller question and the "un-gitignoring `.agent-work/`"
observation (both flagged out-of-scope by the reviewer) were not revisited, per REWORK-1.md's "not in
scope" list.

**Specific exclusions touched:** no.

## Behavior changed
Yes. Every manifest's `repo_rev` content field now carries `{"commit": ...}` only (previously
`{"commit": ..., "dirty": ...}`). `dirty` is still computed and still present in every manifest, now
under `run.dirty` instead. Any consumer that read `manifest["repo_rev"]["dirty"]` needs to read
`manifest["run"]["dirty"]` instead — there are none yet (the design doc's "downstream, not yet
resolved" note still holds; no production caller exists).

## Map Impact

- **Structural anchors touched:** `scripts/context_manifest.py` — `build_manifest()` (split point,
  ~line 340), `run_facts()` (new `dirty` parameter, ~line 295). `scripts/checklist_engine.py` —
  `repo_revision()` docstring only, function body unchanged.
- **Capabilities added/changed/affected:** the content-projection's doctrine-version stamp narrows to
  exactly the canon-determined half (`repo_rev.commit`); the working-tree-honesty half (`dirty`) moves
  to the run-provenance capability alongside `roots`/`host`/`generated_at`. No capability was removed.
- **Constraints/assumptions touched:** `constraint:content-is-canon-determined` — now actually holds
  for `repo_rev`, closing the gap BLOCKER-1 found. The round-1 assumption
  `decision:repo-rev-computed-via-checklist-engine` (repo_revision lives in checklist_engine.py,
  imported by name to keep context_manifest.py's no-subprocess AST guard true) is unchanged and
  restated more precisely in the corrected docstrings.
- **Decision candidates / resolved decisions:** `decision:split-happens-at-assembly-not-in-git-helper`
  — `repo_revision()`/`default_repo_state()` keep returning `{commit, dirty}` together; `build_manifest`
  is the one place that splits them. Chosen over splitting inside the git helper because
  `repo_revision()` is a general repo-facts primitive with one caller today — pre-shaping its return
  value to this module's own content/run boundary would couple a reusable primitive to one consumer's
  design choice for no present benefit.
- **Claims/evidence produced:** `claim:repo-rev-content-is-canon-determined` — asserted directly by
  `RepoRevContent.test_content_is_unaffected_by_dirty_when_commit_is_equal` (unit-level) and
  `RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content`
  (end-to-end, real git worktrees) — the second is the reviewer's own reproduction, now a permanent
  regression that failed before this fix and passes after (transcripts below).
- **Trust limitations / drift found:** none new. The placement defect the reviewer found is now closed
  and pinned by a regression at both the unit and end-to-end level.
- **Triage candidates:** none raised beyond what REVIEW_RESULT.md already listed under "Out-of-scope
  observations" (`tc1` — a latent poison-framework trap around `default_repo_state`'s default-argument
  binding; `tc2` — un-gitignoring `.agent-work/` would make `dirty` permanently `True`), neither
  revisited per REWORK-1.md's scope fence.

## Test mode
**Required:** test-first for the regression (REWORK-1.md: "must fail before your fix and pass after");
test-after/inspection for the split itself and the MAJOR-2 comment fix (matching the original gate's
test mode — wiring-level changes to an already-tested pair, not new algorithmic risk).
**Satisfied:** yes. The regression test was written and run RED against the pre-fix code before any
production-code edit this round, then run GREEN after the fix, with both transcripts captured below
from the same, unedited test body.

## Evidence

```bash
python -m pytest tests/test_context_manifest.py -q -k 'repo_rev or doctrine_version' --no-header
# 6 passed, 58 deselected   <- gate g5 postcondition c2, verbatim

python -m pytest tests/test_context_manifest.py -q
# 65 passed, 62 subtests passed

python -m pytest tests/test_context_determinism.py -q
# 12 passed, 14 subtests passed   <- gate g5 postcondition c3's intent, now genuinely exercising the
# case it previously could not reach; 12 vs the prior round's 11 is exactly the new regression test

python -m pytest tests/ -q --junitxml=junit-report.xml && python scripts/verify_skip_guard.py junit-report.xml && rm -f junit-report.xml
# 1254 passed, 2 skipped, 336 subtests passed   <- 1254 vs prior round's 1250 is exactly the 4 new
# tests this round (1 regression + 3 in test_context_manifest.py)
# skip guard ok: 2 skip(s) in report, all match documented allow-tuples
```

**Result:** pass — all four commands, all exit 0.

## TDD evidence, if required

**Failing test observed** (`RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content`,
run standalone, BEFORE any production-code edit this round — pre-fix `repo_rev` still carries `dirty`
inside content):

```
$ python -m pytest tests/test_context_determinism.py -q -k test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content
F                                                                        [100%]
================================== FAILURES ===================================
_ RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content _
...
>           self.assertEqual(cm.content(m_clean), cm.content(m_dirty))
E           AssertionError: {'con[289 chars]': '0b15d5b8d8578a07053b619d7e5b270cf748d76c', 'dirty': False}} != {'con[289 chars]': '0b15d5b8d8578a07053b619d7e5b270cf748d76c', 'dirty': True}}
E             {'contract': 1,
E              'files': [{'path': 'scripts/agent_work_root.py',
E                         'rev': '9074549724a9e5eb77d06cbe46017f12afbe115d',
E                         'root': 'repo'},
E                        {'path': 'templates/COMMANDER_SPINE.template.json',
E                         'rev': '7b5eba7574732d3df9eb668747443a084017db75',
E                         'root': 'skill'}],
E              'repo_rev': {'commit': '0b15d5b8d8578a07053b619d7e5b270cf748d76c',
E           -               'dirty': False},
E           +               'dirty': True},
E              'step': 'context'}

tests\test_context_determinism.py:611: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_context_determinism.py::RealCheckoutSkew::test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content
1 failed, 11 deselected in 0.90s
```

Note the premise inside the failure: `commit` already agrees across the two checkouts
(`0b15d5b8d857...`), and every declared file row is identical — the only variable is `dirty`
(`False` vs `True`), and it alone drags `content()` apart. This is exactly the reviewer's BLOCKER-1
reproduction.

**Passing test observed** (same test, unedited, run AFTER the split fix landed):

```
$ python -m pytest tests/test_context_determinism.py -q -k RealCheckoutSkew
..                                                                 [100%]
2 passed, 10 deselected, 6 subtests passed in 1.10s
```

(Both `RealCheckoutSkew` tests pass: the pre-existing untracked-vs-absent skew test, unedited, and the
new regression.)

**Refactor while green:** no refactor beyond the split itself; docstrings were rewritten alongside the
code they document, not as a separate pass.

## Docs/contracts touched
- `docs/CHECKLIST_ENGINE_DESIGN.md` — "Two-level revision scheme" paragraph rewritten to describe the
  split and the reviewer's disproof of the original placement.

## Assumptions
- **The split happens at `build_manifest`'s assembly point, not inside `repo_revision()`/`default_repo_state()`.**
  REWORK-1.md left this as my call ("`repo_revision()` may keep returning both ... Your call; say which
  you chose and why"). I kept the git helper and the injected edge returning `{commit, dirty}` together
  and split only at the one place that currently cares about the content/run boundary
  (`build_manifest`). Reasoning: `repo_revision()` is a general repo-facts primitive already documented
  as reusable ("a real git subprocess... not a second ad-hoc caller"); pre-shaping its return value to
  `context_manifest.py`'s own content/run split would couple a shared primitive to one consumer's
  design choice, for no present benefit, and would make a future second caller with different
  content/run needs re-split it back apart anyway.
- **`run.dirty` sits as a flat top-level key inside `run`, not nested under a `repo_rev`-shaped
  sub-object.** REWORK-1.md said only "the dirty flag appears under the `run` subtree," not naming a
  shape. I chose flat (`run["dirty"]`) to match how `run`'s other facts (`work_id`, `generated_at`,
  `roots`, `host`) are already flat siblings, rather than introducing the only nested fact in that
  subtree. A reviewer preferring `run["repo_rev"] = {"dirty": ...}` would be a one-line shape change,
  not a redesign.
- **The regression test lives in `RealCheckoutSkew` as a new method, not a new class.** REVIEW_RESULT.md
  suggested exactly this ("a five-line addition to `RealCheckoutSkew`, which already builds a clean
  second checkout"). Mine builds two *fresh* checkouts rather than reusing `ROOT` as one side, because
  `ROOT` is the working tree I am actively editing this round and its own dirtiness is not a controlled,
  repeatable variable — the reviewer's own construction used two fresh worktrees for the same reason.

## Stop conditions hit
None. Every check passed on the first attempt after each corresponding code change; no design-invalidating
finding surfaced.

## Out-of-scope observations
None beyond what REVIEW_RESULT.md already listed (`tc1`, `tc2`, and the deliberately-not-raised absent
production caller) — none of those were revisited, per REWORK-1.md's scope fence ("Do not widen beyond
the split, the docstring correction, the test extension, and the reviewer's major").

## Workflow Feedback

- **Handoff gaps:** none — REWORK-1.md was unusually precise: it named the exact defect mechanism (the
  gate imperative asserting its own settle condition's negation), the exact fix ("commit stays content,
  dirty moves to run"), the exact regression case to add (the reviewer's own construction, verbatim),
  and explicitly delegated the one open design call (git-helper split vs. assembly-point split) with
  a request to justify the choice. Nothing was ambiguous.
- **Context rediscovered:** `run_facts()` had exactly one caller (`build_manifest`), so adding a `dirty`
  parameter to it was safe without a wider signature audit — worth confirming before editing a shared
  helper's signature, even when a grep suggests it's low-risk; this repo's prior rounds have taught that
  guessing "obviously safe" without the grep is exactly how earlier defects here slipped through.
- **Instructions improvised around:** the rework note's constraint "No skipTest" reads, taken literally,
  as forbidding new `unittest.SkipTest` calls anywhere I write — but this file's own pre-existing
  convention (`DeterministicAcrossEnvironments.setUpClass`, `RealCheckoutSkew`'s existing method) guards
  `git worktree add` with exactly that pattern. I resolved the tension by NOT adding a new SkipTest in my
  regression test — if git is absent, `git worktree add`'s return code assertion fails loudly instead —
  and left a comment at the point of divergence explaining why. Worth Commander deciding, for future
  rounds, whether "no skipTest" means "introduce no *new* skip points" (what I assumed) or "match
  existing file convention even where it uses skip" — the two read identically until a file already has
  the pattern.
- **What would have made this easier:** nothing about REWORK-1.md itself. One small friction: the
  engine's `attest`/`advance --why` verb pair repeats the full next-step imperative back on every call
  (visible throughout this transcript) — harmless, but it means each engine call's output is dominated
  by the same repeated paragraph rather than the delta, which made scanning for the actual state
  transition (`m2-split-fix -> complete`, etc.) slightly slower than it needed to be. Not a blocker, just
  a minor legibility note for whoever tunes the RAIL banner.

## Return status
`complete`
