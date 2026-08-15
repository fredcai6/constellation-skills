# Problem statement — tc1-episode-rewording

Reconciled against `LAUNCH_ORDER.md` (frozen, `admiral-post-568`). No live human; delegated mode.

## Ask
Two `a5` (workaround) assertions in `episodes/active/` are written as imperative advice to a
future reader, tripping the episode-observation guard
(`tests/test_episode_observations.py`, purpose: "records reading as observations rather than
instructions (issue #460)"):

- `tc1-windows-path-form-002.a5` (read in full at understand): "Read the verifier source (not
  just the template) to get the exact required/optional field split, then keep the template's
  structural shape and substitute real run content -- rather than guessing at which template
  fields could be dropped."
- `tc1-windows-path-form-003.a5` (read in full at understand): "Always pass --why with a genuine
  one-line understanding statement on every advance call for a non-exempt gate, rather than
  waiting for the refusal to name it."

## What this run does
Reword both `a5` statements as past-tense observations of what this run (`tc1-windows-path-form`)
actually did and found, preserving substance. Write via `scripts/apply_episode_delta.py` only
(the sole write path into `episodes/`); no hand-editing.

## Explicitly out of bounds (LAUNCH_ORDER)
- No addition to the guard's exception list (`decision:reword-not-except`, settled/human).
- No deletion of either record.
- No touching `tests/test_episode_observations.py`, `scripts/checklist_engine.py`,
  `tests/test_spine_origin_isolation.py`, `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`,
  `.mcp.json`, or the four `tc1-worktree-identity-00*.md` episodes.

## Verification required
- `python -m pytest -q tests/test_episode_observations.py` green.
- Full Linux suite, cache-clean, `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`: target
  3010 passed / 6 skipped / 0 failed / 1136 subtests.
- Commit + push to `tc1/worktree-identity` (existing PR #588 branch); no new branch, no new PR,
  no merge (Admiral merges).

## Stop conditions carried forward
- `spine_status` not resolving to `tc1-episode-rewording`.
- A statement provably cannot be expressed as an observation without losing substance.
- Green requiring the exception list, a deletion, or a guard-file edit.
- Suite not reaching the exact target counts in a clean env.

## Ambiguity check
None found. The launch order names the exact files, exact lines, exact rough-shape content, the
write path, the guard boundaries, and the evidence/return shape. No gap requires floating to the
Admiral at this step.
