# REVIEW_RESULT

**Verdict: APPROVE**

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
Branch: `feat/567-k-one-spine-mutable-middle`, base `9b38b9d9`.

I did not trust the implementer's account. Every criterion below was reproduced independently —
diff read line-by-line, a base-commit worktree built for differential testing, and two guards
disabled locally to prove the tests can fail.

## Criteria

**1. The four guards refuse.** Read `scripts/checklist_engine.py:3084-3159` directly. `drop`,
`rescope`, `retext-check` each call `_is_bookend(tid)` and raise before their status check; `add`
computes `ceiling = max(bookends)` over `new_items` and raises when `insert_at > ceiling`. Verified
via the new `AmendBookendGuard` test class (10 tests, all green) plus my own differential harness
(below). PASS.

**2. `drop` refuses regardless of status — including pending.** Confirmed by code: the
`_is_bookend` guard in the `drop` branch runs *before* the `status != "pending"` check, so status
never matters once the flag is set. Reproduced the exact hole against the real base commit
(`9b38b9d9`, built in a detached worktree): a pending gate carrying an (unrecognized, at base)
`bookend: True` key dropped cleanly —
```
BASE: drop of pending 'archive' (with unknown bookend=True key) result: ['g1']
CONFIRMED: base 9b38b9d9 has no bookend guard -- the hole is real
```
`test_amend_drop_refuses_bookend_gate_pending` and `test_amend_reproduces_measured_gap_refused_when_declared`
cover this on the new code and both pass. PASS.

**3. The middle still grows.** `test_amend_add_into_middle_still_succeeds` passes, and my own
`add_middle` differential scenario (insert after `g1` in a 3-gate plan with no bookend) succeeds
identically on base and new engines. Separately confirmed the ceiling math itself: inserting *at*
the bookend's own index (i.e., immediately before it) is allowed since the guard only fires on
`insert_at > ceiling`. PASS.

**4. Backward compatibility.** Built a differential harness that loads both `9b38b9d9`'s
`checklist_engine.py` and the working tree's copy as separate modules and runs six no-bookend-key
scenarios (`add_middle`, `add_append`, `drop_pending`, `rescope_pending`, `retext_check`,
`drop_nonpending`) through both. All six produced byte-identical results (`ALL MATCH`). Also ran
the full pre-existing suite against the base worktree: `456 passed, 140 subtests passed` — exactly
466 − 10 new `AmendBookendGuard` tests, confirming no pre-existing test's behavior shifted. PASS.

**5. All-or-nothing survives.** Read `amend()`'s structure: `new_items`/`new_tasks` are copies
(`:3032-3033`), every op validates against the copies inside the loop, and `cl["items"]`/
`cl["tasks"]` are only assigned after the loop completes (`:3217-3222`) — a raise anywhere aborts
before that assignment. `test_amend_all_or_nothing_leaves_checklist_unmutated_with_bookend_violation`
mixes a legal `add` with a bookend-violating `drop` and asserts `items`/`tasks` are unchanged and
`"amendments"` was never added — I re-ran it in isolation and it passes; I also disabled the drop
guard (see criterion 10) and confirmed this exact test goes red, proving it's actually exercising
the guard rather than passing vacuously. PASS.

**6. The one-way latch.** `rescope {bookend: true}` on an unmarked pending gate: guard doesn't
fire (not yet a bookend), status check passes, `bookend` is in the new `overwritable` tuple
(`:3132`) so the field lands. A following `rescope {bookend: false}`: now `_is_bookend` is true, so
the guard fires unconditionally and refuses — the field-overwrite code is never reached, so there
is no path to unset it. `test_amend_rescope_sets_bookend_flag_via_overwritable` and
`test_amend_rescope_bookend_flag_is_one_way_latch` both pass. PASS.

**7. One swappable seam.** `grep -n "bookend" scripts/checklist_engine.py` shows every guard site
(`add`, `drop`, `rescope`, `retext-check`) calling `_is_bookend(tid)`; the only `task.get("bookend")`-
shaped read is inside `_is_bookend` itself (`:3054`). `overwritable` at `:3132` adds the string
`"bookend"` as a settable field name, not a read of the flag. `mcp_spine_server.py`'s
`task.get('bookend')` mention is inside a docstring/description string, not executable code. No
other file references `bookend`. PASS.

**8. `from_child` and `consolidate()` untouched.** `git diff scripts/checklist_engine.py | grep
'^@@'` shows five hunks, all within lines 3042–3163 — entirely inside `amend()` (which starts at
`:2971`). `from_child` (`:2617`) and `consolidate()` (`:2733`) are both before this range and
appear nowhere in the diff. PASS.

**9. No fenced path was written.** `git diff --stat` shows exactly three files: `scripts/
checklist_engine.py`, `scripts/mcp_spine_server.py`, `tests/test_checklist_engine.py`. Checked
`run_crew.py`, `install_constellation.py`, both `LAUNCH_ORDER.template.md`, `map/INDEX.md`,
`generate_spine.py`, `specs/`, and every `*SPINE*.template.json` on disk — none appear in the diff
or contain a `bookend` reference. PASS.

**10. The tests can fail.**
- Disabled the `drop` guard (`if False and _is_bookend(tid):`) and reran
  `AmendBookendGuard`: 3 failed, 7 passed —
  `test_amend_drop_refuses_bookend_gate_pending`,
  `test_amend_reproduces_measured_gap_refused_when_declared`, and
  `test_amend_all_or_nothing_leaves_checklist_unmutated_with_bookend_violation` all went red with
  `AssertionError: EngineError not raised`. Restored the guard.
- Disabled the `add` ceiling guard (`if False and bookends:`) and reran: 1 failed, 9 passed —
  `test_amend_add_refuses_after_last_bookend` went red the same way. Restored the guard.
- Confirmed restoration: `git diff scripts/checklist_engine.py` matches the original diff exactly
  (`42` added lines, no `False and` markers left), and the full suite is green again
  (`466 passed, 140 subtests passed`). PASS.

## Test tallies (fresh subprocess, crew env vars unset, per #269)

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py
466 passed, 140 subtests passed

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py
62 passed, 14 subtests passed

git status --porcelain
 M scripts/checklist_engine.py
 M scripts/mcp_spine_server.py
 M tests/test_checklist_engine.py
?? .agent-work/567-k/          (pre-existing, not from this review)
```

## Findings

- **[info] Design-B formula divergence, correctly resolved.** The implementer's result notes that
  `DESIGN_COMPARISON.md`/`design-B-result.md`'s literal `_bookend_ceiling()` formula
  (`max(marked_indices) + 1`) has an off-by-one that would allow `add` to append immediately after
  a bookend that is the last item. I independently re-derived this: with that formula, a bookend at
  the final index `n-1` yields `ceiling = n`, and an append computes `insert_at = n` (current list
  length), so `insert_at > ceiling` is `n > n` — false, i.e. allowed. The shipped code instead sets
  `ceiling = max(bookends)` (the bookend's own index, not +1), which correctly refuses `insert_at =
  n` (`n > n-1` is true). This is not a defect in the shipped code — it's a correct deviation from a
  buggy design artifact, worth someone updating `DESIGN_COMPARISON.md` so a future reader doesn't
  copy the formula verbatim, but that's a doc fix, not a code fix, and is out of this gate's scope.
- **[info, disagreement noted per handoff invitation] `retext-check` coverage.** The handoff invites
  disagreement on covering `retext-check` in the freeze. I don't disagree — the stated rationale
  (retext-check could rewrite a frozen gate's command to something trivially true, defeating a
  drop-only freeze) is sound and the risk is real: nothing else in `amend()` stops that rewrite on a
  bookend gate. No finding to raise here.
- **[nit] Error message duplication.** All four guard messages hand-write "declared bookend gate"
  prose independently rather than sharing a message-building helper. Given criterion 7's "one
  swappable seam" requirement was about the *read*, not the message text, and the four messages are
  usefully distinct (each names its own verb's specific consequence), I don't think this rises to a
  blocking finding — noting it only because a future guard addition (a fifth op, if one is ever
  added) should keep matching this shape rather than drifting.

## Workflow Feedback

- The handoff's differential-testing hint ("verify against the real base... rather than by
  reasoning about it") was exactly right and I'd have under-verified criterion 4 without it — my
  first instinct was to read the base diff and reason from there, which would have missed subtleties
  like the `overwritable` tuple's new `"bookend"` entry interacting with the base's total absence of
  that key.
- My own mistake: my first differential-harness draft used `importlib.util.spec_from_file_location`
  with a module name (`E_base`) but didn't isolate `sys.modules`, which risked base/new modules
  colliding if either was ever `import`ed a second time in the same run (they weren't here, since I
  ran the script once and exited, but a longer-lived comparison harness would need to guard against
  that). Not a problem for this review's scope, but worth remembering for next time.
- No handoff gaps — the ten criteria were concrete and independently checkable; I did not need to
  escalate anything to the parent.
