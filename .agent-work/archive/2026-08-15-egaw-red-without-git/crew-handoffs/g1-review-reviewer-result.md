# REVIEW_RESULT — g1-review

## Verdict: APPROVE

## Per-check findings

1. **Scope — `git status --porcelain`**
   Only `tests/test_episode_observation_guard_at_write.py` is modified in the source tree. The only
   other diffs are under `.agent-work/` (an archived stdout log and untracked work-area directories),
   which are explicitly excluded as scratch, not source. Confirmed.

2. **No git/subprocess/SHA reference; no `pytest.skip`; attribution proof**
   Read the full current file. `import subprocess`, `PRE_CHANGE_REV`, `_git_show`, `load_pre_change`
   are all gone; no literal `2c46cab8` anywhere; no `pytest.skip` anywhere.
   `_reject_instruction_shaped` is defined once in `scripts/apply_episode_delta.py:996` and invoked by
   bare name at three call sites (lines 1413, 1426, 1515) inside other module-level functions — since
   Python resolves a bare name at call time via the module's global namespace, monkeypatching
   `cur._reject_instruction_shaped` on the loaded module object genuinely intercepts all three call
   sites; it is not a no-op capture.
   The RED test (`test_bare_verb_workaround_was_accepted_before_this_change`) and GREEN test
   (`test_bare_verb_workaround_is_rejected_now`, unmodified) each call `load_current()` independently,
   which does a fresh `importlib.util.spec_from_file_location` + `exec_module` — a brand-new module
   object with brand-new function objects every time. So the pair is a genuine controlled comparison:
   identical delta, identical writer source, the *only* variable is whether `_reject_instruction_shaped`
   is neutralized (RED) or left real (GREEN). If the guard call sites were deleted from the source
   entirely (not just neutralized), GREEN would fail (rc would be 0, contradicting
   `assertNotEqual(0, rc, out)`) — so the pair together cannot pass under "guard call always a no-op."
   If the function definition itself were deleted, `original = cur._reject_instruction_shaped` in RED
   would raise `AttributeError` before the neutralization even happens, erroring loudly rather than
   silently passing. This satisfies the attribution requirement.
   The `finally: cur._reject_instruction_shaped = original` genuinely restores on any exception path
   (verified by reading the try/finally structure directly) — defensive-in-depth given `load_current()`
   already isolates each test via a fresh module object, so no cross-test leak is currently exploitable,
   but the restore is correct and matches the close criterion literally (finally, not bare sequential
   code).

3. **Test run**
   `python -m pytest -q tests/test_episode_observation_guard_at_write.py -v` → 9 passed, 0 skipped, 0
   failed. Matches the implementer's claimed count and the file's actual 9 test methods.

4. **Excluded files untouched**
   `git status --porcelain -- scripts/apply_episode_delta.py scripts/verify_episode_observations.py
   tests/test_episode_observations.py scripts/install_constellation.py .github/workflows/ci.yml
   .claude/settings.json .mcp.json scripts/hooks/spine_rail.py episodes/` → empty output. None of the
   excluded paths were touched.

## Blockers
None.

## Out-of-scope observations
None found beyond what's already noted by the implementer (the handoff's "8 tests" estimate vs. the
actual 9 — a pre-existing discrepancy in the handoff prose, not introduced by this change).

## Workflow feedback
None — handoff and implementer result were both accurate and independently reproducible; no
discrepancies found between claimed and actual evidence.
