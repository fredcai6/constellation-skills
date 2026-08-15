# Reviewer Handoff — #441 transactional binding store

## Gate

`g1` (review)

## Your job

Independently verify the implementation described in
`.agent-work/epic-568-441/crew-handoffs/g1-implementer-result.md` against the
frozen contract below. You did not write this code. Be skeptical: re-run the
commands yourself rather than trusting the result artifact's prose, and read
the actual diff.

## Where to look

- Diff: `git -C /home/tommy/projects/constellation-skills/.worktrees/epic-568-441 diff scripts/hooks/spine_rail.py scripts/hooks/gauge_writer_hook.py tests/test_spine_rail.py tests/test_gauge_writer.py`
- Result artifact: `.agent-work/epic-568-441/crew-handoffs/g1-implementer-result.md`
- Frozen contract: `.agent-work/epic-568-441/crew-handoffs/g1-implementer-handoff.md`
- Frozen plan: `.agent-work/epic-568-441/plan-alternatives/best-seam.md`,
  `.agent-work/epic-568-441/plan-alternatives/smallest-diff.md`,
  `.agent-work/epic-568-441/PLAN_CONVERGENCE.md`

## What to verify

1. **Scope**: `git diff --name-only` touches exactly
   `scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py`,
   `tests/test_spine_rail.py`, `tests/test_gauge_writer.py` (a fifth file,
   `map/INDEX.md`, is a separate Commander-level map regen — confirm it is
   NOT a fifth production/test file).
2. **Transaction**: one stable sibling lock (`.spine-rail-binding.json.lock`,
   never the registry itself, never replaced) covers load -> safe reap ->
   one mutation callback -> unique-temp atomic replace -> release, for ALL
   THREE writers (PostToolUse claim, PostToolUse release, SessionStart
   bind-on-resume).
3. **Locking**: POSIX `fcntl.flock` / Windows `msvcrt.locking` (byte 0, 1
   byte, injectable for testing), bounded retry (named constants), fails
   open (no raise, no mutation) on contention, timeout, lock-API error, or
   replace failure. Re-run:
   `python -m pytest -q tests/test_spine_rail.py::test_spawn_binding_transaction_red_green tests/test_spine_rail.py::test_binding_lock_contention_fails_open tests/test_spine_rail.py::test_binding_lock_timeout_fails_open tests/test_spine_rail.py::test_binding_lock_api_failure_fails_open tests/test_spine_rail.py::test_binding_replace_failure_fails_open tests/test_spine_rail.py::test_windows_lock_adapter_contract`
   and confirm all 6 pass.
4. **Identity**: `spine_rail.is_usable_agent_id` is the sole 1-64 ASCII
   alnum/`_`/`-` predicate; `binding_key` and `gauge_writer_hook`'s
   `_is_usable_agent_id` both delegate to it (no duplicate regex left in
   gauge). Confirm `test_rail_and_gauge_agree_on_every_id_in_the_shared_table`
   actually exercises both call paths and no old divergence test survives.
5. **Claim validation**: absolute AND relative claim targets require
   `_worktree_from_spine` containment (`<worktree>/.agent-work/<work-id>/
   <name>.json`) plus `looks_like_checklist` readability, plus a
   `Path.resolve()` symlink-escape re-check, re-checked again inside the
   locked mutator. Confirm `test_post_claim_symlink_escape_target_binds_nothing`
   and the two rewritten absolute-claim tests actually prove this (read them,
   don't just trust the names).
6. **Reap**: runs inside every transaction before the mutation. Malformed/
   empty entries go immediately; readable released entries go immediately;
   missing targets go only past a 24h AWARE-timestamp grace; every readable
   non-released target and every missing target with untrustworthy age
   (naive/absent) is RETAINED. Old-shape (pre-#202) entries pass through
   untouched. Confirm `test_reap_binding_entries_matrix` covers every named
   branch with an injected clock, not wall-clock sleeps.
7. **Release**: resolves the recorded target first against the LOCKED,
   REAPED snapshot (`resolve_recorded_release_target`), THEN falls back to
   the filesystem ladder -- not the other way around.
8. **Mixed-writer proof**: `test_spawn_binding_sessionstart_claim_mixed_writer_race`
   is a REAL `multiprocessing.get_context("spawn")` topology (not threads,
   not a mock), spawning both claim writers and SessionStart resume writers
   concurrently against one registry, and asserts all entries from BOTH
   kinds survive.
9. **Stop retention**: `test_stop_old_active_binding_blocks_only_its_own_identity`
   proves age never reaps/unblocks a readable active binding, and a foreign
   session with no binding is never blocked.
10. **No scope creep**: no checklist-engine lease/journal/child/actor-PID/
    durable-root/historical-backfill changes. Confirm by reading the diff,
    not just trusting the constraint text.
11. **Full suites**:
    `python -m pytest -q tests/test_spine_rail.py tests/test_gauge_writer.py`
    and (cache-clean; unset SPINE_FILE/SPINE_SESSION/SPINE_PARENT first,
    since this worktree's own shell carries them and they falsely trip an
    unrelated env-leak test)
    `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q`.

## Known, disclosed limitations (read before flagging as findings)

- This review is being run by the SAME commander session that wrote the
  implementation (Agent-tool subagent dispatch, not `run_crew.py` -- two
  independent `run_crew.py` implementer dispatches died with `Execution
  error` this run per `LAUNCH_ORDER-resume-3.md`, and the launch order's
  Stop Conditions say to stop dispatching crews rather than risk a third
  dead child; `run_crew.py`'s own reviewer path was not attempted for the
  same reason). You do NOT share conversation history with the author --
  you are a fresh Agent-tool dispatch with no memory of writing this code --
  but you are running inside the same worktree and process family. Judge the
  CODE AND TESTS on their own merits; do not defer to the result artifact's
  claims without re-running the commands yourself.
- `map/INDEX.md` is modified as a side effect of clearing a pre-existing,
  unrelated map-staleness test failure. This is expected and out of the
  four-file scope.

## Verdict

Return your verdict as APPROVE or BLOCK with specific findings, each citing
a file and line. If BLOCK, be exact about what must change.
