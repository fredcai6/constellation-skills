# #441 plan alternative B — best seam / most testable

## Verdict

**READY-FOR-REVIEW — one bounded Commander execute gate.**  Put the whole
binding-store contract behind a private transaction seam in
`scripts/hooks/spine_rail.py`, then make the three writers call that seam:
PostToolUse claim, PostToolUse release, and SessionStart's unambiguous
bind-on-resume.  This is the narrowest point that owns the registry pathname,
current load/save behavior, key construction, and all three mutations; it
does not make gauge a second store owner.

The governing sources are `LAUNCH_ORDER.md` and `PROBLEM_STATEMENT.md`.  The
baseline confirms the fault: `_save_json_map` atomically replaces a fixed
`.tmp`, but `handle_post_tool_use` and `decide_session_start` each do an
unlocked load/mutate/save.  It also confirms the identity split: rail's
denylist in `binding_key` admits punctuation which gauge's path allowlist
rejects.

## Execute gate

### 1. Centralize the store transaction in `spine_rail.py`

Introduce private, fail-open helpers adjacent to `binding_path`,
`load_binding`, and `save_binding`:

* `is_usable_agent_id(value)` is the authoritative `str` allowlist:
  `^[A-Za-z0-9_-]{1,64}$`.  `binding_key` calls it whenever `agent_id` is
  present; absent `agent_id` retains the bare-session path.  Thus malformed,
  empty, non-string, whitespace, punctuation, wildcard, separator, traversal,
  and over-64 identities return `None` and cause no binding write.
* A portable advisory-lock context opens a sibling lock file such as
  `.spine-rail-binding.json.lock`, tries nonblocking `fcntl.flock` on POSIX or
  `msvcrt.locking` on Windows, and retries only until a small named deadline.
  Unsupported/import/lock/open/timeout failures yield no transaction and the
  hook returns `{}`.  The descriptor remains open over load, reap, mutation,
  unique-temp write, and replace; OS release on process death is the only
  recovery mechanism (no stale-lock PID policy).
* `_binding_transaction(project_dir, mutate, *, now=_now_iso)` loads the raw
  object while locked; reap-normalizes it; gives a mutable nested map to the
  small claim/release/resume mutator; then, only when bytes/state changed,
  writes JSON to a same-directory **unique** `tempfile.NamedTemporaryFile`
  and `os.replace`s it.  It cleans a failed temp best-effort.  It returns the
  post-transaction map/operation result, never raises.  Readers stay on
  fail-open `load_binding`, with no locking obligation.

The lock need not cover checklist command execution or SessionStart scanning:
those are discovery/read inputs.  It begins immediately before current store
load and ends after replacement, which supplies serializable registry mutation
without widening hook latency unnecessarily.

### 2. Make reaping a transaction-internal normalization, not a lifecycle feature

Every successful writer transaction reaps before its mutator, using one
deterministic helper and a single injected UTC clock for tests:

* Remove malformed or empty outer-key/entry records immediately.
* For a structurally valid entry with a string target: remove it when its
  readable checklist explicitly has `engine_session.status == "released"`.
* If the target is missing/unreadable, remove only when `claimed_at` parses as
  an aware timestamp and is at least 24 hours old.  Missing, invalid, naive,
  or otherwise untrustworthy age is retained.
* A readable target with an active lease is retained regardless of age.  No
  age-based removal of readable records, lease inference, actor/PID liveness,
  journal consultation, historical scan, or migration is introduced.

For claims, require the resolved absolute target to be an existing readable
JSON checklist and lexically/resolve-contained as
`<worktree>/.agent-work/<work-id>/<name>.json` before entering the mutator;
apply the same test to absolute and relative `--file`.  Release first searches
the locked, reaped key-local records through `resolve_recorded_release_target`,
then falls back to existing resolution so moved/deleted compatibility remains.

### 3. Route all production writers through it

* **PostToolUse claim:** resolve/validate first; transaction reap + add exactly
  one `key -> abs_spine -> entry`, retaining siblings.
* **PostToolUse release:** transaction reap + resolve recorded target first +
  delete only that entry/key.  Keep nudge-ledger behavior outside this store
  transaction and unchanged; it is not a binding writer.
* **SessionStart bind-on-resume:** after its existing unambiguous active scan,
  transaction reap + merge exactly the scanned entry under bare `sid`.

`gauge_writer_hook.py` becomes a consumer of `spine_rail.is_usable_agent_id`;
remove its duplicate `_AGENT_ID_ALLOWED` policy while retaining its
`_spine_rail is None` fail-open guard.  It still only derives a transcript and
reads bindings/gauge paths; it never enters the binding transaction.

## Proof plan

Change only `scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py`,
`tests/test_spine_rail.py`, and the actual focused gauge suite
`tests/test_gauge_writer.py` (the launch-order ownership name
`test_gauge_writer_hook.py` does not exist in this checkout).  No engine file,
journal, checklist lease behavior, child ownership, or PID code changes.

1. Add a Linux-real `multiprocessing.get_context("spawn")` regression in
   `test_spine_rail.py`.  Its module-level worker invokes the production
   `handle_post_tool_use` against a common temporary project and real readable
   checklists.  A start barrier plus a test-only transaction seam/barrier makes
   all claim workers overlap at the read/write window; workers use distinct
   session/agent keys and expected spines.  Join with finite timeouts, assert
   clean exits, parse the final file with `json.loads`, and assert every
   expected key/entry survives.
2. Establish **red** by disabling/bypassing only the transaction seam with the
   exact same worker payloads, registry, barrier topology, and assertions; it
   must deterministically lose at least one entry.  Establish **green** by
   restoring the transaction.  Do not accept an in-process thread test,
   timing-only loop, synthetic store writer, or a topology that cannot fail
   when the lock is absent.  Windows may be marked recorded/allowed by launch
   policy, but every non-Windows failure blocks.
3. Add mutation control for the write side: assert two concurrent writers use
   distinct temp names and that a held lock makes the handler return `{}` with
   registry bytes unchanged after the bounded deadline.  These tests prove the
   fail-open contention contract rather than merely observing final JSON.
4. Extend focused deterministic tests for all three writers' merge behavior,
   each reaper branch (malformed/empty, released, missing old, missing unknown
   age retained, active old retained), absolute/relative claim containment and
   non-JSON/missing rejection, and release-after-delete/move.  Inject clock and
   lock/temp adapters rather than patching global time or relying on sleeps.
5. Replace the current rail-vs-gauge divergence test with a shared table over
   both public call paths: accepted ASCII alnum/`_`/`-` values of 1 and 64;
   rejected punctuation, whitespace, wildcard, `/`, `\\`, `..`, empty,
   non-string, and 65-character values.  Confirm rejected IDs neither bind
   nor cause gauge transcript/gauge writes.

Run the two focused suites and the new isolated spawn regression first; then
the relevant non-Windows suite.  Preserve existing fail-open reader tests for
absent, corrupt, ambiguous, and inaccessible state.

## Scores

| Dimension | Score | Reason |
| --- | ---: | --- |
| Depth | 5/5 | Changes the one lost-update boundary, rather than disguising it in individual handlers. |
| Locality | 5/5 | Four scoped files; no engine, lifecycle, journal, child, or PID surface. |
| Seam placement | 5/5 | `spine_rail` already owns registry path/schema and all writers; gauge is correctly a consumer. |
| Testability | 5/5 | Spawned production-handler red/green plus lock and temp mutation controls discriminate the fix. |

## Remaining risks / floats

* `msvcrt.locking` region/seek behavior and `fcntl` import availability need a
  small adapter and Windows recording; do not silently substitute a stale
  lockfile protocol without a float.
* Lock timeout must be short enough for hooks yet long enough for the tested
  critical section.  Name and test the constant; changing the policy needs a
  float.
* The exact reaper definition of a structurally malformed legacy record should
  be encoded narrowly so corrupt data is discarded only where the protected
  statement explicitly authorizes it; do not migrate historical entries.
* The red control must synchronize the unprotected read phase.  If it cannot
  lose an update on the reviewed base with that exact topology, invoke the
  honest-null clause and retain only independently red policy defects.

## Non-goals (enforced)

No checklist-engine lease lifecycle changes, claim/release journal, child
ownership, actor identity, durable-root liveness, PID inference, stale-lock
PID reclamation, historical bulk backfill, or historical registry mutation.
