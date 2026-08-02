# Reviewer Handoff — g1 RE-REVIEW after packaging rework

## Gate
`g1-review` (issue #305, epic #298). This gate was cascade-reset by a `reopen`; its prior evidence is superseded but retained.

## Survey State Location
`.agent-work/issue-305/g1-review-rework/review.json`. **Not** at the worktree root, and not at the old `g1-review/` path (that holds the superseded survey).

Drive it with the **worktree's** `scripts/checklist_engine.py`. On a survey, `record` is the re-record verb; `advance`/`reopen` refuse as gated-only. Note `--session-id` is required on `record`/`start` but **rejected** by `consolidate`.

## What happened before you

A prior reviewer approved criteria 2/3/4 of the g1 seam and **BLOCKed** on one finding: `episode_capture.py` was not shipped to any installed skill, so the seam was **inert in production** — the engine's `try/except ImportError` no-op fallback ran, `start` and `advance` returned 0, and zero manifests were written with nothing on stderr. Filed as **#362**. The Admiral ruled the fix in scope: *"a capture that does not ship is not captured."*

**Your job is to review the rework, not to re-review the seam.** The seam itself (emit at `start()`/`reopen()`, write-if-absent, fail-soft-not-silent, root resolution) was already independently verified with 17 case/verb pairs and six mutants. Do not spend your budget there. If you happen to see something wrong in it, say so — but it is not your assignment.

## What to inspect

Everything is committed on `epic-298/305`. The rework is the last commit:

```
cd C:/Programs/constellation-skills-wt/e298-305
git show 0201a52 --stat
git diff 0201a52~1..0201a52
```

The implementer's own result: `.agent-work/issue-305/crew/g1-implement-rework-result.md`
Its handoff (what it was asked for): `.agent-work/issue-305/crew/g1-implement-rework-handoff.md`

## What was built

1. **Closure shipped.** `SCRIPT_RUNTIME_COMPANIONS["checklist_engine.py"]` widened from `("gauge_reader.py",)` to include `episode_capture.py`, `agent_work_root.py`, `context_manifest.py`.
2. **The detector (the actual deliverable).** The pre-existing guard regexed only for `parent / "x.py"` dynamic loads and was structurally blind to `sys.path.insert` + plain import. Replaced with two helpers — an AST walk collecting imports at any nesting depth (so function-local deferred imports count, filtered to names that exist as `scripts/<name>.py`), and a transitive, cycle-safe BFS closure.
3. **A second guard:** `test_installed_engine_binds_the_real_capture_seam_not_the_fallback` really installs the `implementer` skill (bundle is `("checklist_engine.py",)` alone, so every companion must arrive via `expand_script_bundle()`), then asserts `emit_step_manifest.__module__ == "episode_capture"` rather than the fallback.
4. Two false-rationale comments rewritten in `checklist_engine.py` — **zero executable lines changed there.**

## Close criteria — hunt these specifically

1. **Is the detector genuinely falsifiable, and is it overfitted?** I reproduced the implementer's red myself: reverting the companion tuple turns both guards red. **That is not enough and it is not your job to repeat it.** Your job: **devise a mutation the implementer did not ship.** Specifically — add a *new* sidecar module reached by a mechanism the AST walk should catch, do **not** declare it, and confirm the detector names it. If the detector only catches the three modules that already exist, it is a hardcoded assertion wearing a parser's clothes.
2. **Does the `scripts/<name>.py` existence filter create a hole?** A sibling import of a module that does not yet exist, or one whose name collides with a stdlib/third-party module, is where this design can silently drop a dependency. Probe it.
3. **Is the closure really transitive and really cycle-safe?** `context_manifest` imports `checklist_engine` right back. Construct the cycle and confirm no hang and no missed node.
4. **Do all ten engine-carrying skills genuinely get all four companions?** Verify through a **real install**, not by reading the dict. `agent_work_root.py` was previously hand-listed on only `admiral` and `commander`; confirm the other eight now get it and that the two hand-listed ones did not get a duplicate.
5. **Was anything weakened rather than generalized?** Three existing tests were rewritten: the detector test, the companion test (10 → 44 subtests), and `test_expansion_preserves_order_and_does_not_duplicate` (de-literalized). **For each, confirm the new form still asserts everything the old form did.** A test that was rewritten because a legitimate change broke it is the single easiest place to lose an invariant. In particular, confirm `gauge_reader.py` is still pinned **by name** so the #256 guarantee was not dissolved into the generalization.
6. **Additive-only.** No existing bundle entry changed meaning; `gauge_reader.py` keeps position 0. Other commanders are live on this installer.

## Constraints

- Do **not** touch `C:/Programs/constellation-skills` (the main checkout). It has uncommitted human work in `install_constellation.py` — two lines adding `"clean-codebase"` keys. That is a *different* dict entry from what changed here; note it, do not treat it as a conflict to resolve, and do not flag it as un-inspectable.
- Do not modify `scripts/episode_capture.py` or `tests/test_episode_capture.py`.
- `python -m pytest` (3.14.3 / pytest 9.0.2); `py` has no pytest. Neither reproduces CI.
- `encoding='utf-8', newline='\n'` on every write. `Path.read_text(newline=...)` is 3.13+ and fails CI.
- Compare normalized content or blob OIDs, never raw working-tree bytes.

## Evidence standing (verify, do not accept)

Full suite **1436 passed, 2 skipped, 471 subtests** — I reproduced this. Pre-fix revert produces:
`AssertionError: 'episode_capture' != 'installed_engine_305'` — the no-op fallback caught in the act.

## Two things the implementer self-reported; judge them

- It fixed a **second** false comment I had not assigned (the engine's import-site comment, which after the dict change asserted the opposite of the truth and named the wrong dict). In scope or scope creep? Your call.
- It flagged that `gauge_writer_hook.py` still has **no closure guard** — the same protection for ~4 lines — and chose not to do it. Agree or disagree.

## Suggested Model Tier
**Opus.** The deliverable is a guard, and a guard that cannot fail is the failure mode this epic has hit six times.

## Return
`REVIEW_RESULT` to `.agent-work/issue-305/crew/g1-review-rework-result.md` with an explicit **APPROVE** or **BLOCK**, per-criterion disposition, **your independent mutation and its outcome**, and blunt `Workflow Feedback`. Your final message must contain the same result.
