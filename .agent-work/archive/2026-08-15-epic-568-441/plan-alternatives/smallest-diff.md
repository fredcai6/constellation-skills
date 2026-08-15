# #441 plan alternative A — smallest diff

## Verdict

**READY-FOR-REVIEW — execute one bounded Commander gate.**  This is the
smallest complete change because every required writer already converges in
`scripts/hooks/spine_rail.py`, and the sole cross-consumer identity divergence
is in its sibling gauge hook.  Do not widen into checklist-engine lifecycle,
journaling, child ownership, actor/PID liveness, durable-root policy, or a
historical migration.

Isolation was verified before planning:
`verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/epic-568-441`
reported `worktree OK`.  The only pre-existing worktree-local untracked state
is `.agent-work/epic-568-441/`; this plan artifact belongs there.  No engine
state was read or mutated for this plan.

## Governing intent and observed seam

`LAUNCH_ORDER.md` and `PROBLEM_STATEMENT.md` settle the transaction boundary:
one portable advisory-lock transaction must encompass **load -> safe reap ->
mutation -> unique-temp atomic replace** for PostToolUse claim, PostToolUse
release, and SessionStart bind-on-resume.  Current `spine_rail.py` instead
does unlocked `load_binding()` / dict mutation / `save_binding()`, whose fixed
`<registry>.tmp` also collides between writers.  `handle_post_tool_use()` and
`decide_session_start()` are the only binding writers.  Existing reads remain
outside the lock and fail open.

The current rail denylist admits values (`:`, `*`, `?`, space, `.`, and >64
characters) that `gauge_writer_hook.py` correctly refuses before deriving a
transcript filename.  The fix is to move that exact allowlist to the rail as
the authoritative `is_usable_agent_id()` and make gauge delegate to it; do not
duplicate the regex.

## Single Commander execute gate

Change exactly these four files (blast radius: **2 production modules + 2
focused test modules**):

- `scripts/hooks/spine_rail.py`
- `scripts/hooks/gauge_writer_hook.py`
- `tests/test_spine_rail.py`
- `tests/test_gauge_writer.py` (the actual focused gauge-writer suite in this
  worktree; `tests/test_gauge_writer_hook.py` named in the launch order does
  not exist)

### 1. Centralize identity and valid claim-target checks in the rail

1. Replace `_AGENT_ID_REJECT` with public
   `is_usable_agent_id(agent_id) -> bool`, using the exact ASCII allowlist
   `\A[A-Za-z0-9_-]{1,64}\Z`.  `binding_key()` keeps its current three-way
   semantics: absent `agent_id` means the bare top-level session key; a present
   but unusable id returns `None`, never the bare-key fallback.
2. Make gauge's `_is_usable_agent_id` a thin delegation (with its existing
   `_spine_rail is None` fail-open guard), and leave `_binding_key()` as the
   one call path.  This preserves its no-write outcome when the sibling fails
   to import.
3. Add a rail-only claim validator which requires a resolved absolute target
   with exact lexical shape
   `<worktree>/.agent-work/<nonempty-work-id>/<nonempty-name>.json`, and a
   readable JSON object with an `items` list.  Apply it to both absolute and
   relative claim resolution immediately before recording, and re-check it in
   the locked mutation callback.  Do not use this validator for release:
   release must first resolve the recorded entry under the lock and may delete
   it even when the checklist moved, was archived, or was deleted.

### 2. Make the binding store transactional at its one write seam

Add a small internal `mutate_binding(project_dir, mutation)` context/callback
seam in `spine_rail.py`; it is the only way either handler writes the binding
registry.  Its precise contract:

1. Open a sibling lock file (for example
   `.spine-rail-binding.json.lock`) and take a nonblocking exclusive advisory
   lock with a short bounded retry window (proposed: 200 ms in 10 ms steps).
   Use `fcntl.flock(... LOCK_EX | LOCK_NB)` where available and a one-byte
   `msvcrt.locking(... LK_NBLCK ...)` equivalent on Windows.  Failed import,
   open, contention, or lock error returns `None`/no-op; hooks never block the
   host and never raise.  The advisory lock is released on close/process exit;
   do not introduce stale-lockfile ownership, PID checks, or recovery policy.
2. While held, load the raw registry once, normalize only the established
   nested-map shape, then apply safe reaping before the writer's mutation.
   Persist only if reaping or the requested mutation changed it.  Readers keep
   `load_binding()`'s existing absent/corrupt/old-shape fail-open behavior.
3. Write through one private saver using `tempfile.NamedTemporaryFile` (or an
   equally unique same-directory stdlib temp name), close it, `os.replace`, and
   best-effort cleanup on error.  Never reuse the fixed `.tmp` name.  The lock
   covers the complete read-modify-write interval, not merely replacement.
4. Route all three writers through it:
   - claim: validate the candidate and add only `binding[key][abs_spine]`;
   - release: in the locked snapshot use
     `resolve_recorded_release_target(file_val, binding.get(key))` before the
     existing fallback ladder, then delete only that target/key;
   - SessionStart: retain its scan and resume-output behavior, but put its
     unambiguous bare-session insertion/merge into the transaction and reload
     the map there so it cannot overwrite a concurrent claim or release.
   Nudge-ledger writes remain separate: they are not binding-store writers and
   are outside #441.

### 3. Use intentionally conservative safe reap

Implement a pure-ish `_reap_binding_entries(binding, now)` called only inside
the transaction.  It may delete:

- malformed nested entries and empty per-key maps immediately;
- an entry whose readable checklist reports `engine_session.status ==
  "released"`;
- a genuinely missing target only when `claimed_at` parses as timezone-aware
  ISO-8601 and is at least 24 hours old.

It must retain a missing target with absent/unparseable age, inaccessible or
ambiguous targets, and every readable active lease regardless of age.  It does
not scan globally, infer liveness, change a lease, write a journal, or
backfill/mutate the historical registry except incidentally during a new
writer transaction.

## Proof gate

Add focused tests before declaring green.

1. **Identity parity:** table-drive good ids and rejected punctuation,
   whitespace, wildcard, separator/traversal, non-string, empty, and 65-byte
   ids through both rail key construction and gauge transcript derivation;
   prove their outcomes agree while preserving top-level no-`agent_id`
   behavior.
2. **Claim/release shape:** prove absolute and relative claims reject missing,
   non-JSON, wrong-layout, and traversal targets without touching the store;
   prove a valid contained `<name>.json` claim succeeds.  Preserve the existing
   deleted/moved recorded-release tests and add a direct assertion that the
   recorded target is selected from the locked map ahead of a valid decoy.
3. **Reaper matrix:** malformed/empty goes immediately; readable released goes
   immediately; missing at `24h - ε` stays; missing at `24h + ε` goes;
   missing with bad/missing timestamp stays; and old readable active lease
   stays.  Inject `now` into the reaper rather than making wall-clock tests.
4. **SessionStart:** retain the existing unambiguous scan/bare-key and sibling
   merge cases, plus a concurrent-writer preservation case through the shared
   transaction seam.
5. **Required production spawn red/green:** add a module-level, picklable test
   worker in `tests/test_spine_rail.py`; start independent
   `multiprocessing.get_context("spawn")` children against one temporary
   registry.  Each calls the real `spine_rail.handle_post_tool_use()` with a
   different valid, contained checklist and a start barrier so the production
   handler/store paths contend.  Collect exit/errors over queues, parse the
   final registry with `json.loads`, and assert all expected keys/paths remain.
   This is not a mocked writer or threads-only surrogate.
6. **Mutation control:** run the identical spawn topology with the transaction
   seam disabled only inside each test worker and a test-only post-load barrier
   wrapper around the raw loader.  The wrapper forces every child to take the
   same pre-mutation snapshot; then the final registry deterministically lacks
   at least one expected entry.  The green run uses the unmodified production
   seam and preserves all entries.  This demonstrates why the transaction,
   rather than merely the test's process scheduling, supplies the guarantee.

Run:

```bash
pytest -q tests/test_spine_rail.py tests/test_gauge_writer.py
```

On Linux, every test must pass.  Keep the spawn topology Windows-compatible;
record a Windows-specific advisory-lock failure if encountered, but it cannot
mask any non-Windows failure.

## Scoring

| Dimension | Score | Why |
|---|---:|---|
| Depth | 5/5 | One serialization boundary covers all three writers, plus the required validation and reaping policies. |
| Locality | 5/5 | Two production modules and their focused tests; no engine/lifecycle files. |
| Seam placement | 5/5 | Central write helper prevents a future writer from accidentally bypassing lock/reap/unique replace. |
| Testability | 5/5 | Real spawned production handlers, valid final JSON, deterministic unlocked mutation control, and policy matrices. |

## Remaining risks / explicit floats

- `msvcrt` byte-range locking and network filesystems can differ from POSIX
  `flock`; keep the adapter narrow and fail open, then record Windows evidence.
- A 200 ms contention budget intentionally drops a discovery update under
  sustained contention rather than delaying a hook; that is the specified
  fail-open tradeoff, not a lease/liveness decision.
- Reaping malformed legacy data during the next writer transaction is a
  localized schema cleanup.  Do not add a standalone historical sweep.
- If the spawn test cannot produce a deterministic unlocked red result with
  the stated post-load barrier, stop and float under the launch order's
  honest-null clause rather than claim concurrency proof from timing.

## Out of scope

Checklist-engine leases, claim/release journaling, child semantics, actor or
PID ownership/liveness, durable-root discovery, stale-lock ownership policy,
historical registry migration, and any engine-spine mutation remain excluded.
