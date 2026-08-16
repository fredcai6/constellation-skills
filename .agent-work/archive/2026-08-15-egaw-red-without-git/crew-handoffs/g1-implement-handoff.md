# Implementer Handoff

## Gate
`g1-implement`

## Task
In `tests/test_episode_observation_guard_at_write.py`, rewrite
`RedBeforeGreenAfterTests.test_bare_verb_workaround_was_accepted_before_this_change` so it no longer
depends on git, and delete the now-unused git-only machinery (`PRE_CHANGE_REV`, `_git_show`,
`load_pre_change`).

**Root cause being fixed:** `load_pre_change()` runs `git show 2c46cab8:scripts/apply_episode_delta.py`
to reconstruct the writer as it was before the guard existed. On CI's shallow clone (`actions/checkout@v4`,
no `fetch-depth`, depth 1) that commit object is absent and `git show` exits 128. The hardcoded SHA is
also a latent trap independent of CI (breaks in any shallow clone/worktree, silently redefines "before" on
rebase).

**Approach (ratified in LAUNCH_ORDER.md, not yours to reopen):** approach (a) — exercise the CURRENT
writer with the guard call neutralized, prove the delta writes; restore it, prove the same delta is
rejected. Same code path, same process, no git.

Concretely, replace the body of `test_bare_verb_workaround_was_accepted_before_this_change` with something
along these lines (adapt to fit the class's existing helpers — `load_current()`, `self._run()`,
`create_op()`, `BARE_VERB_WORKAROUND` are all already defined in this file and must NOT change):

```python
def test_bare_verb_workaround_was_accepted_before_this_change(self):
    """RED (before): with the guard call neutralized, the writer has no opinion about
    statement content at all -- the delta this suite now refuses used to write cleanly."""
    cur = load_current()
    original = cur._reject_instruction_shaped
    cur._reject_instruction_shaped = lambda kind, statement, where: None
    try:
        rc, out, root = self._run(cur, create_op(workaround=BARE_VERB_WORKAROUND))
    finally:
        cur._reject_instruction_shaped = original
    self.assertEqual(0, rc, out)
    self.assertTrue((root / "active" / "egaw-guard-001.md").is_file())
```

Rename the docstring/comment as needed so it reads correctly (it currently frames itself as "the pre-change
writer"; it is now "the same writer with its guard call neutralized"). Update the module docstring's SCOPE
section and the `PRE_CHANGE_REV` code comment (lines ~42-45) if they still describe the git-based
mechanism after your edit — they must describe what the file actually does once you are done, not the
old approach.

Remove the now-dead imports (`subprocess` is used only by `_git_show`; check before removing — nothing else
in the file uses `subprocess`) and the now-dead `WRITER_SCRIPT`/`ROOT`-only-for-git-show usage (keep `ROOT`
and `WRITER_SCRIPT` themselves — `load_current()` still needs `WRITER_SCRIPT`).

## Protected Intent
The RED/GREEN pair must still prove **attribution**: that the rejection in
`test_bare_verb_workaround_is_rejected_now` is caused by the guard call this change (PR #592) added, not
merely present. Do not weaken this to "the writer rejects some things" — it must specifically show the
guard call is the mechanism.

## Test Mode
TDD not applicable — this is a rewrite of an existing test's plumbing, not new production behavior. The
existing `ControlTests`, `ScopeTests`, and `GrandfatheredExceptionTests` classes are the safety net; they
must keep passing unchanged.

## Close Criteria
- `test_bare_verb_workaround_was_accepted_before_this_change` passes and no longer imports/calls `git`,
  `subprocess`, or references the SHA `2c46cab8`.
- The identical delta (same `create_op(workaround=BARE_VERB_WORKAROUND)`) is proven to write cleanly with
  the guard call neutralized, and proven to be rejected with it restored, in the same test — both against
  `load_current()`, never a resurrected historical module.
- `grep -n "2c46cab8\|import subprocess\|git show\|_git_show\|load_pre_change\|PRE_CHANGE_REV" tests/test_episode_observation_guard_at_write.py` returns nothing.
- Every other test in the file (`test_bare_verb_workaround_is_rejected_now`,
  `test_the_rejection_names_the_offending_word_and_kind`, all of `ControlTests`, `ScopeTests`,
  `GrandfatheredExceptionTests`) is unchanged and still passes.
- No `pytest.skip` added anywhere in the file.

## Allowed Scope
`tests/test_episode_observation_guard_at_write.py` only. You may also read (never modify)
`scripts/apply_episode_delta.py` to confirm `_reject_instruction_shaped`'s exact signature and behavior.

## Specific Exclusions
Everything else named in LAUNCH_ORDER.md's "File Ownership — NOT yours" list:
`.github/workflows/ci.yml`, `scripts/apply_episode_delta.py`, `scripts/verify_episode_observations.py`,
`tests/test_episode_observations.py`, `scripts/install_constellation.py`,
`scripts/hooks/spine_rail.py`, `.claude/settings.json`, `.mcp.json`, existing `episodes/` records.

## Constraints
- Do not delete the RED test or reduce it to a no-op.
- Do not add `pytest.skip` anywhere in this file — the repo's `scripts/verify_skip_guard.py` fails the
  build on any undocumented skip.
- No hardcoded commit SHA anywhere in the file after this change.
- Monkeypatch `cur._reject_instruction_shaped` (a module attribute on the object `load_current()` returns),
  not `sys.modules` globally, and always restore it in a `finally` so a test failure never leaks state into
  a later test in the same process.

## Map Anchors (inbound)
- **Structural:** `scripts/apply_episode_delta.py:996-1010` (`_reject_instruction_shaped`),
  `tests/test_episode_observation_guard_at_write.py:39-72` (the git-dependent machinery being removed),
  `tests/test_episode_observation_guard_at_write.py:135-163` (`RedBeforeGreenAfterTests`).
- **Decision anchor:** approach (a) is ratified in LAUNCH_ORDER.md ("(a) is the closer match to a true
  RED/GREEN pair and I lean toward it") — settled, not yours to reopen.
- **Evidence expectations:** claim:attribution (the rejection is caused by the guard call), claim:no-git
  (grep returns nothing).

## Deliverable Path Check
- **Committed** — `tests/test_episode_observation_guard_at_write.py`; verified via
  `git check-ignore tests/test_episode_observation_guard_at_write.py` exiting 1 (not ignored).

## Required Evidence
- `python -m pytest -q tests/test_episode_observation_guard_at_write.py` output, full (all 8 tests in the
  file), showing all pass.
- The exact grep command from Close Criteria and its (empty) output.
- The diff (`git diff -- tests/test_episode_observation_guard_at_write.py`).

## Wiring Grep
None — this gate renames/removes test helpers, it adds no new production symbol.

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write
python -m pytest -q tests/test_episode_observation_guard_at_write.py
grep -n "2c46cab8\|import subprocess\|git show\|_git_show\|load_pre_change\|PRE_CHANGE_REV" tests/test_episode_observation_guard_at_write.py
git diff -- tests/test_episode_observation_guard_at_write.py
```

## Suggested Model Tier
simple bounded — one test method rewrite plus dead-code removal in one file, mechanism already specified.

## Authority
Approach (a) vs (b) is already decided by LAUNCH_ORDER.md and the dispatching Commander — do not
re-litigate it. If neutralizing `_reject_instruction_shaped` turns out not to be sufficient to make the
delta write cleanly (e.g. some other check also fires), stop and report rather than guessing at a second
seam to patch.

## Stop Conditions
Stop and return if: the guard seam does not behave as described (neutralizing it does not make the delta
write cleanly), a change outside the allowed scope seems necessary, or required evidence cannot be
produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/egaw-red-without-git/crew-handoffs/g1-implement-implementer-result.md` before ending your turn.
