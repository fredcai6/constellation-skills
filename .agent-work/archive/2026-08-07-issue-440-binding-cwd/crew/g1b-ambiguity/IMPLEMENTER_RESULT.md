# Implementation Result

## Assigned gate
`g1b` — ambiguity guard on the #440 candidate ladder (issue #440, epic-418 workstream A2).
Worktree `C:/Programs/constellation-skills-wt/epic418-a2-440`, base `9d44aa6`.

## Completed slice
`resolve_spine_candidate` now refuses to guess. Rungs 0-2 (`absolute`, `worktree_opt`,
`cd_target`) are **told truth** and short-circuit exactly as before. Among the **guessed** rungs
(3-5) the earliest validating candidate is kept, but if a later guessed rung validates a
**different** file the answer is discarded and **nothing is bound**. Two guesses naming the same
file are agreement, not ambiguity — they bind, keeping the earliest rung's `path_source`.

## Scope
**Files changed:**
- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`

**Specific exclusions touched:** no. `binding_key()` and the binding key shape untouched;
`gauge_writer_hook.py` / `checklist_engine.py` untouched (and `gauge_writer_hook.py` does not
reference the ladder at all — grep for `resolve_spine_candidate|_candidate_roots|path_source`
returns 0 hits there); the ladder is not reordered or renamed; no docs touched; nothing written to
the live main checkout's `.agent-work/.spine-rail-binding.json` or any real `.claude/settings*.json`
(every probe ran in a pytest `tmp_path`).

## Behavior changed
Yes.

1. A relative `--file` whose only answers come from **guessed** rungs, where two of those rungs name
   different files, now writes **no binding entry** where it previously wrote the payload cwd's
   (main-checkout's) copy.
2. Consequence, and the one thing worth the Commander's eye: to know a guess is unambiguous the
   scan must consult rungs 4 and 5, so **`git worktree list` now runs when no told-truth rung
   answers**. It still never runs for a told-truth rung, and it still never runs for an ordinary
   tool call — `handle_post_tool_use` returns early unless the observed command is an engine
   `claim`/`release`, which is twice per run, not once per tool use. The probe stays bounded at
   `GIT_PROBE_TIMEOUT_SECONDS = 2.0` and still returns `[]` on any failure.
3. Real-world reach of (1): in this repo `.agent-work/` is tracked and ~10 worktrees exist, so a
   **top-level** agent claiming a committed checklist from the main checkout can now legitimately
   bind nothing when a worktree holds the same relative path. That is the ruling in the handoff
   ("a missing binding is recoverable; a wrong one is not"), applied as written — flagged here so
   it is a known consequence rather than a surprise at the g2 live fire.

## Map Impact
- **Structural anchors touched:** `scripts/hooks/spine_rail.py` — `resolve_spine_candidate` (the
  ladder's consumer) and `_candidate_roots`' laziness contract. New module constant
  `TOLD_TRUTH_PATH_SOURCES` partitions the existing `PATH_SOURCE_*` values into told-truth vs
  guess. No new function, no new file, no seam moved.
- **Capabilities added/changed/affected:** the resolution now has a third outcome — *resolved*,
  *unresolvable*, and now *ambiguous → refuse* — where it previously had two.
- **Constraints/assumptions touched:** *PostToolUse never blocks* honored (`{}` on every path,
  fuzz test green). *Skip-on-uncertainty* extended from `resolve_recorded_release_target` to the
  filesystem ladder — that function is now a genuine in-module precedent, not just an analogy.
  *Binding key shape unchanged* honored. **Newly stressed:** "the git probe stays off the common
  path" — still true for the tool-use hot path and for every told-truth rung, no longer true for a
  guessed-rung claim/release (see Behavior changed #2).
- **Decision anchors:** `existence-verified-resolution` `@grade: guess · leans g1,g1b · settle: the
  two-arm live fire at g2` — unchanged in kind; g1b narrows it from "first validating candidate
  wins" to "first validating told-truth candidate wins; guesses must agree". Still a guess, still
  settled by the g2 live fire.
- **Claims/evidence produced:** ambiguity among guessed rungs binds nothing and leaves the store
  byte-unchanged, proven against a **real** `git worktree` tree on disk; told-truth rungs still win
  outright with unchanged `path_source`; rung 0 still never probes git.
- **Triage candidates:** none new. The pre-existing KNOWN-NOT-CHASED items in this module (no key
  reaper, no lock on load-modify-save, no absolute-`--file` validation) are unchanged.

## Test mode
**Required:** `test-first` (TDD required)
**Satisfied:** yes — the new tests were written and observed failing while
`scripts/hooks/spine_rail.py` was still byte-identical to `9d44aa6`, then made to pass.

## Evidence

### Load-bearing 1 — TDD red against `9d44aa6`

The module was at `9d44aa6` and unmodified when the red run happened (proved in the same command,
not asserted in prose):

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
git rev-parse HEAD                                     # 9d44aa6470719c274e6e5fe2f32af60761e97017
git diff --quiet -- scripts/hooks/spine_rail.py; echo "SPINE_RAIL_UNMODIFIED_EXIT=$?"   # 0
python -m pytest tests/test_spine_rail.py -q -k "ambiguity or ambiguous or agreement or disagreeing or under_the_guard" > /tmp/g1b-red.txt 2>&1; echo "RED_EXIT=$?"
```

**Result:** `RED_EXIT=1` — `3 failed, 8 passed, 98 deselected in 2.09s`

The headline failure, verbatim:

```
__ test_post_claim_ambiguous_guessed_rungs_bind_nothing_store_byte_unchanged __
        out = sr.handle_post_tool_use(_bash(cmd, cwd=str(main_tree)), main_tree)
        assert out == {}                              # PostToolUse never blocks
>       assert store.read_bytes() == before           # not one byte written
E       assert b'{\r\n  "oth...}\r\n  }\r\n}' == b'{"other-sid": {}}'
E         At index 1 diff: b'\r' != b'"'
```

That is the residual exactly as the reviewer described it: two real trees, no told-truth signal,
and the hook confidently writes the main checkout's copy. The other two reds were
`..._guessed_rungs_naming_the_same_file_is_agreement_not_ambiguity` (the scan never consulted rung
4) and `..._two_worktree_roots_disagreeing_bind_nothing` (bound `wtA` outright).

No stash and no `git show` restore was needed — the tests were added **before** the module was
touched, so the red run is against the real `9d44aa6` file in place. Nothing to restore, hence
nothing that could fail to restore.

### Load-bearing 2 — the handoff's verification command, real exit code

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q > /tmp/g1b.txt 2>&1; echo "EXIT=$?"; tail -5 /tmp/g1b.txt
```

**Result:** `EXIT=0` — `176 passed in 6.24s`
(169 at `9d44aa6` + 7 new tests. Redirected to a file and `echo $?` taken from the pytest process,
not from a pipe.)

`tests/test_spine_rail.py` alone: `EXIT=0`, `109 passed in 5.22s`.

### Confirmatory — the close criteria, one test each

| Close criterion | Test |
|---|---|
| two trees, no told-truth signal → no entry, store byte-unchanged | `test_post_claim_ambiguous_guessed_rungs_bind_nothing_store_byte_unchanged` |
| same case **with** a `cd` → still resolves to the told-truth answer, `path_source == cd_target` | `test_post_claim_cd_target_still_wins_outright_under_ambiguity` |
| same case **with** an absolute `--worktree` → `path_source == worktree_opt` | `test_post_claim_absolute_worktree_opt_still_wins_outright_under_ambiguity` |
| same case **with** an absolute `--file` → `path_source == absolute`, **and git never probed** | `test_post_claim_absolute_file_wins_and_never_probes_git_under_ambiguity` |
| two guesses → same file → still binds, earliest rung's `path_source` | `test_post_claim_guessed_rungs_naming_the_same_file_is_agreement_not_ambiguity` |
| ambiguity needs no second rung — two rung-4 roots alone → bind nothing | `test_post_claim_two_worktree_roots_disagreeing_bind_nothing` |
| a single validating candidate still binds under the guard | `test_post_claim_one_worktree_root_still_binds_under_the_guard` |
| the g1 rung-4 real-`git worktree` fresh-subprocess proof still passes | `test_post_claim_rung4_real_git_worktree_resolved_in_a_fresh_subprocess` (unchanged, green) |
| `handle_post_tool_use` returns `{}` on every path and never raises | `test_post_tool_use_never_raises_on_junk` (unchanged, green) |

The three `_under_ambiguity` told-truth tests and the headline test all build a **real** repo with a
**real** `git worktree add` tree on disk (`_two_tree_ambiguity` → `_make_repo_with_worktree`), not a
monkeypatched root — the tie they break is a real one.

### Confirmatory — diff size

```bash
git diff --numstat
```

```
57      7       scripts/hooks/spine_rail.py
156     4       tests/test_spine_rail.py
```

(plus the Commander's own `.agent-work/issue-440-binding-cwd/*` workflow files, which this gate did
not author.)

**The 4 test-file deletions are deliberate and are the one place I did not meet g1's zero-deletion
standard.** All four are in the single existing probe-spy test
`test_git_probe_does_not_run_when_an_earlier_rung_answers` — its two-line docstring, and two
assertions:

```
-    """The probe is off the common path. Rungs 0-3 answer first, and the
-    generator is lazy, so `git` is never spawned for an ordinary claim."""
-    assert calls == [], "git probe ran on the common path"
-    assert calls == []
```

Both assertions became **stricter**, not weaker — `assert calls == []` → `assert calls == [str(proj)]`
in the rung-3 half (the scan must probe **exactly once**, not "at most") and the same exact-list
assertion in the rung-0 half (rung 0 adds no probe of its own). Nothing was deleted to make a
failing assertion pass; the assertion changed because the specified behavior changed, and the
handoff's close criterion scopes the invariant to **told-truth** rungs ("the git probe still does
not run when a told-truth rung answers — keep or extend g1's `subprocess.run` spy test"). The
told-truth half of that claim is now asserted in three places instead of one. No test was deleted
or renamed.

### Deliverable path check

```bash
git check-ignore scripts/hooks/spine_rail.py; echo "EXIT_A=$?"   # 1
git check-ignore tests/test_spine_rail.py;    echo "EXIT_B=$?"   # 1
```

Both **exit 1** — tracked, will be committed. This result file lives under `.agent-work/` and is
correctly absent from the code diff.

### Wiring grep

One new symbol: `TOLD_TRUTH_PATH_SOURCES` (a module constant).

```bash
grep -rn "TOLD_TRUTH_PATH_SOURCES" --include=*.py scripts/ tests/ | grep -v "= frozenset" | wc -l
```

**Count: 1** call site outside the definition —
`scripts/hooks/spine_rail.py:658: if source in TOLD_TRUTH_PATH_SOURCES:`.
Not zero, so the stop condition does not fire. No other new callable symbol was added; the rest of
the change is inline in `resolve_spine_candidate`.

### Blast radius of the change (authored side, enumerated by command)

```bash
grep -rln "path_source" --include=*.py --include=*.md --include=*.json . | grep -v "^./.git/" | grep -v __pycache__ | wc -l
```

**13 files.** Two are code — `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`, both in
scope and both updated. The other **11 are this run's own workflow artifacts** under
`.agent-work/issue-440-binding-cwd/` (g1 handoff/plan/result, g1 review, CRITIC_TRIAGE,
execute.json, spine.json, and this gate's own handoff) — Commander-owned, not mine to edit.
**Zero docs** describe the rung semantics today: `grep -n "candidate root\|rung\|payload cwd\|git_worktree" docs/GAUGE_WRITER_HOOK.md`
returns nothing, so no doc is stranded by this change. The docs gate the handoff defers is
therefore writing new text, not correcting text this change invalidated.

## TDD evidence, if required
- Failing test observed: yes — `RED_EXIT=1`, `3 failed, 8 passed`, against `9d44aa6` with
  `git diff --quiet -- scripts/hooks/spine_rail.py` exiting 0 in the same command.
- Passing test observed: yes — `EXIT=0`, `176 passed`.
- Refactor while green: no — the change is 12 lines of logic; there was nothing to refactor.

## Docs/contracts touched
- None. `docs/GAUGE_WRITER_HOOK.md` is explicitly the Commander's at a later gate, and (see blast
  radius) it currently says nothing about the ladder that this change contradicts.

## Assumptions
- "More than one candidate root validates and they name **different** files" is compared with the
  module's existing `_same_path` (normcase + normpath) on two already-`resolve()`d absolute paths.
  I reused `_same_path` rather than minting a comparator; its documented fail-safe-`True` on an
  un-comparable input means a comparison failure reads as *agreement*, but both inputs here are
  strings this function just built, so that branch is unreachable in practice.
- The guard scans the guessed rungs **in order and stops at the first disagreement**. A third
  guessed rung that would have agreed with the first is never consulted — irrelevant, since one
  disagreement is already enough to refuse.

## Stop conditions hit
- None. Scope was not exceeded, no exclusion was touched, all required evidence was produced, and
  no decision outside my authority was needed.

## Out-of-scope observations
- **For the Commander, not a defect:** the guard makes it possible for a *top-level* main-checkout
  agent to bind nothing whenever any worktree holds a valid checklist at the same tracked relative
  path — which in this repo is common. That is the handoff's own ruling applied faithfully, but it
  is worth a line in the g2 live-fire design: the two-arm test should be able to tell "bound
  nothing because ambiguous" from "bound nothing because unresolvable". Today both look identical
  in the store (silence). A `path_source: "ambiguous"` sentinel written to a side channel would
  distinguish them, but that is a new field and a new decision — **not** taken here.
- The two long-standing KNOWN-NOT-CHASED items in this module (no reaper for keys left by killed
  agents; no lock around the load-modify-save) are untouched and still stand as the module's own
  comments record them.
- A corner case I chose not to chase is commented at the code site as the module's register
  requires: `resolve_spine_candidate`'s docstring now carries a `KNOWN, NOT CHASED (#440 g1b)`
  paragraph saying the guard is all-or-nothing and deliberately does not try to *break* a tie by
  mtime, lease freshness, or reading which spine is active — every such tie-break is a fresh guess
  stacked on the guesses that just disagreed.

## Workflow Feedback
- **Handoff gaps:** one real one, in **Close Criteria** vs **Required Evidence**. "Zero deletions in
  the test diff" and "the git probe still does not run when a told-truth rung answers — keep or
  extend g1's spy test" cannot both hold literally: g1's spy test asserts no probe after a **rung-3**
  answer, and detecting ambiguity among guessed rungs requires consulting rung 4. The word
  *told-truth* in the second clause reads as though the tension was anticipated, but the zero-deletion
  line does not acknowledge it. I flagged this to the Commander in my proof-of-life before writing
  any code rather than discovering it at review.
- **Context rediscovered:** that `handle_post_tool_use` early-returns unless the command is an
  engine `claim`/`release`. That single fact is what reconciles "the git probe now runs on guessed
  rungs" with the Protected Intent's "nothing may put the git probe on the common path" — the probe
  is twice per run, not once per tool call. The handoff's phrase "the common path" is ambiguous
  between those two readings, and the whole judgment of whether this change is acceptable turns on
  which one is meant. Naming it explicitly ("the git probe must stay off the per-tool-call path")
  would have removed the guesswork.
- **Instructions improvised around:** the plan template prescribes a `git show 9d44aa6:...` /
  stash-and-restore dance for the TDD red. I skipped it: writing the tests before touching the
  module makes the red run *natively* against `9d44aa6`, which is strictly stronger evidence (no
  restore step that could silently fail) and I proved the module's pristine state with
  `git diff --quiet` inside the same command. Recommend the template say "observe red against the
  base revision" and leave the mechanism to the implementer.
- **What would have made this easier:** stating the expected direction of the *rung-3* probe
  behavior in the handoff — one sentence, "expect the probe to move onto the guessed-rung path;
  update g1's spy test accordingly" — would have turned my proof-of-life escalation into a
  non-event.

## Return status
`complete`
