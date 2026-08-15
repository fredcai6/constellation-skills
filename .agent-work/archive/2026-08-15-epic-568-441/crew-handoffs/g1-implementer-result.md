# Implementer Result — #441 transactional binding store

Return status: complete
run_id: epic-568-441-g1-attempt-1
test_id: test_spawn_binding_transaction_red_green
base_revision: 065445de
mutation: disable-binding-transaction
expected_failure: lost-update
post_change: all-entries-retained
adapter_failure: four-cases-covered
mixed_writer: sessionstart-claim
blast_radius: 4-files

## Files changed

```
scripts/hooks/gauge_writer_hook.py |  22 +-
scripts/hooks/spine_rail.py        | 489 ++++++++++++++++++++++++++++++++-----
tests/test_gauge_writer.py         |  31 ++-
tests/test_spine_rail.py           | 413 ++++++++++++++++++++++++++++++-
4 files changed, 869 insertions(+), 100 deletions(-)
```

`git check-ignore scripts/hooks/spine_rail.py scripts/hooks/gauge_writer_hook.py
tests/test_spine_rail.py tests/test_gauge_writer.py` -> exit 1 (all four committed,
none ignored).

Out-of-scope note: `map/INDEX.md` is also modified in the working tree (a
`python -m scripts.code_map build --root .` regen, run to clear a pre-existing
map-staleness failure in the full suite — see "Full non-Windows suite" below).
That regen belongs to the Commander's own `reconcile` spine step, not this
implementer's four-file mandate; it is called out here rather than silently
folded into the blast radius.

## TDD proof

**RED** (reviewed base 065445de, before any production change — evidence
already on record at `.agent-work/epic-568-441/evidence/m1-red-observed.txt`,
re-confirmed live 2026-08-15):

```
$ python -m pytest -q -s tests/test_spine_rail.py::test_spawn_binding_transaction_red_green
F
json.decoder.JSONDecodeError: Extra data: line 11 column 2 (char 472)
1 failed in 0.23s
```

16 spawned production claim writers against a shared registry produced a
TORN WRITE (two concatenated JSON documents) — stronger than the plan's
"lost update" premise, confirmed and registered per the launch order's
correction. A second run separately showed a straightforward lost update
(2/16 entries survived). Both runs prove the pre-transaction defect against
reviewed base 065445de, before any production change.

**GREEN** (current tree, transaction implemented), re-run 3x for stability:

```
$ python -m pytest -q -s tests/test_spine_rail.py::test_spawn_binding_transaction_red_green
spawned binding final JSON keys (16/16): ['spawn-shared#writer-0', ... 'spawn-shared#writer-9']
.
1 passed in 0.3x s
```
All three runs: 16/16 entries retained, valid JSON, no torn write.

No separate `disable-binding-transaction` mutation run was required: the
honest-null clause only applies when the reviewed base cannot discriminate,
and it demonstrably can (above).

## Named lock/replace/Windows-adapter tests (adapter_failure=four-cases-covered)

```
$ python -m pytest -q tests/test_spine_rail.py::test_spawn_binding_transaction_red_green tests/test_spine_rail.py::test_binding_lock_contention_fails_open tests/test_spine_rail.py::test_binding_lock_timeout_fails_open tests/test_spine_rail.py::test_binding_lock_api_failure_fails_open tests/test_spine_rail.py::test_binding_replace_failure_fails_open tests/test_spine_rail.py::test_windows_lock_adapter_contract
......                                                                   [100%]
6 passed in 0.44s
```

- `test_binding_lock_contention_fails_open` — sustained contention exhausts
  `LOCK_RETRY_ATTEMPTS`; fails open, registry never created.
- `test_binding_lock_timeout_fails_open` — a zero-second deadline fails open
  on the first attempt, independent of the attempts bound.
- `test_binding_lock_api_failure_fails_open` — a genuine lock-API error
  (not mere contention) is caught, not retried, not propagated.
- `test_binding_replace_failure_fails_open` — a real lock is acquired, then
  `os.replace` fails; the registry is left untouched and the unique temp
  file is cleaned up (no leftover `.tmp`).
- `test_windows_lock_adapter_contract` — the Windows byte-range adapter's
  full contract (`_open_lock_file` one-byte init, `_windows_try_lock`
  seek+`LK_NBLCK`, `_windows_unlock` seek+`LK_UNLCK`, contention returns
  False without raising) unit-tested directly via an injected fake
  `msvcrt`-shaped object — proven on this Linux host, not only assumable on
  a real Windows box.

## Mixed-writer proof (mixed_writer=sessionstart-claim)

```
$ python -m pytest -q -s tests/test_spine_rail.py::test_spawn_binding_sessionstart_claim_mixed_writer_race
mixed-writer race final keys (16/16): [8 'resume-NN' keys, 8 'spawn-shared#writer-N' keys]
.
1 passed in 0.3x s
```
8 real spawned PostToolUse claim writers and 8 real spawned SessionStart
bind-on-resume writers race on the same registry file at once; all 16 serial
updates survive, each under its own key with exactly its own entry. Re-run 3x
for stability, stable each time.

## Stop retention (old-active, own-identity-only)

```
$ python -m pytest -q tests/test_spine_rail.py::test_stop_old_active_binding_blocks_only_its_own_identity
.                                                                        [100%]
1 passed in 0.0Xs
```
A readable active binding blocks Stop for its own session regardless of
`claimed_at` age (matches the reap matrix's `active_sp` case: age never
reaps a readable non-released target); a foreign session with no binding
into that spine is never blocked.

## Identity / path / reaper matrices

```
$ python -m pytest -q tests/test_spine_rail.py -k 'agent_id or claim or release or reap or binding' tests/test_gauge_writer.py -k 'agent_id or identity'
............                                                             [100%]
13 passed, ... deselected
```
- `test_reap_binding_entries_matrix` — malformed entry/malformed outer value
  (go immediately), readable released (goes immediately), readable
  non-released (stays regardless of age), missing target at 24h+1s (goes),
  missing target at 24h-1s (stays), missing target with naive/absent
  `claimed_at` (stays, untrustworthy age is never evidence of staleness),
  empty-after-reap per-key map (key itself goes), old-shape per-key value
  (passed through untouched, never migrated).
- `test_reap_binding_entries_never_raises_and_keeps_data_on_error` — a
  defect inside the reaper fails toward KEEPING data, not discarding it.
- `test_post_claim_symlink_escape_target_binds_nothing` — a symlink at the
  exact lexical `.agent-work/<work>/spine.json` shape, pointing outside that
  containment, is rejected: `_is_valid_claim_target` re-runs the containment
  check against `Path.resolve()`'s fully-resolved path.
- `test_rail_and_gauge_agree_on_every_id_in_the_shared_table` — replaces the
  now-obsolete rail-vs-gauge divergence test (the two predicates converged
  on one definition, so there is nothing left to diverge); one shared table
  driven through both `sr.binding_key` and `gw._binding_key`.

## Focused suites (c1)

```
$ python -m pytest -q tests/test_spine_rail.py tests/test_gauge_writer.py
.........................s..............................................
..........................................................................
..................................................
193 passed, 1 skipped in 1.34s
```

## Full non-Windows suite

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q
3015 passed, 6 skipped, 1130 subtests passed in 123.98s
```

Two anomalies observed and resolved/explained, neither a regression from
this change:

1. `test_map_tree_freshness_root_index_matches_a_fresh_build` initially
   failed (stale `map/INDEX.md`, unrelated to this change's structure since
   the four hook/test files carry no architecture-doc anchors of their own).
   Fixed by running `python -m scripts.code_map build --root .`; the test
   now passes. See "Files changed" above for the resulting diff.
2. `test_launching_the_parent_never_touches_the_calling_processs_own_environ`
   fails ONLY inside this interactive commander session, because the
   harness driving this session itself sets `SPINE_FILE`/`SPINE_SESSION` in
   this shell's own environment (visible in the test's own failure dump).
   Confirmed environmental, not caused by this diff: re-run with those three
   vars unset (`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`), it
   passes, and the full-suite run above (same unset env) shows 0 failures.

Skipped count moved 7 -> 6 between the recorded baseline and this run; not
traced further, as it lies outside the four-file blast radius and the
allowed-scope files carry no skip markers.

## Wiring grep

One new production symbol at a time, `grep -rn '\b<symbol>\b' scripts/hooks/`
excluding each symbol's own `def` line: every symbol below has a nonzero
EXTERNAL call-site count (all are genuinely wired into `handle_post_tool_use`,
`decide_session_start`, or `gauge_writer_hook._is_usable_agent_id`):

`is_usable_agent_id` (2), `_binding_transaction` (3 call sites: claim,
release, SessionStart resume), `_reap_binding_entries` (1), `_is_valid_claim_target`
(2), `_replace_binding_atomically` (1), `_acquire_lock` (1), `_open_lock_file`
(1), `_try_lock` (1), `_unlock` (1), `_lock_path` (1), `_parse_aware_iso` (2).
Zero would have been a stop condition; none are zero.

## Assumptions

- The 24h missing-target grace and the 200-attempt/10ms/2.0s lock retry
  budget are read from the module globals on every call (not baked into
  function-default parameter values), specifically so tests can monkeypatch
  them deterministically without racing wall-clock time.
- `_binding_transaction`'s `mutate` callback returning `None` means "abandon,
  no write" (used only when a claim target fails re-validation under the
  lock); returning an unchanged map (equal to what reap produced) is the
  normal "nothing to do" outcome and also skips the write, via an equality
  check against the pre-mutation snapshot.
- The Windows adapter (`_windows_try_lock`/`_windows_unlock`) is exercised
  via dependency injection (a fake `msvcrt`-shaped object) rather than on a
  real Windows host, per the launch policy that non-Windows failures must
  never be masked and Windows evidence may be recorded rather than run live.

## Stop conditions encountered

None. The production spawn topology discriminated the defect on the first
attempt (stronger than the plan's premise — a torn write, not merely a lost
update); no honest-null was needed.

## Out-of-scope observations

- The pre-existing `#419`/`#440` binding-store defects this issue targets
  (unlocked load-modify-save, fixed `.tmp` collision) are now closed at
  their one write seam; the sibling KNOWN-NOT-CHASED comment in
  `_save_json_map`'s docstring is now stale for the binding store
  specifically (readers still use `_save_json_map`/`_load_json_map` for the
  nudge ledger, which is intentionally NOT part of this transaction per the
  frozen plan — nudge-ledger writes are not binding-store writers).
- `map/INDEX.md` regeneration (see "Files changed") is a Commander-level
  `reconcile` concern, noted rather than silently absorbed into this
  four-file blast radius.

## Workflow feedback

The frozen plan alternatives (`plan-alternatives/best-seam.md` and
`smallest-diff.md`) and `PLAN_CONVERGENCE.md` were detailed enough to
implement directly with almost no re-derivation — the transaction contract,
reap matrix, and claim-validator shape were all specified precisely enough
to code straight from prose. The one friction point: three existing tests
had baked-in assumptions the new transactional/validated behavior
necessarily broke (`test_post_claim_absolute_file_preserved`,
`test_post_claim_absolute_file_is_rung_zero_and_is_not_validated`,
`test_session_start_unambiguous_scan_merges_onto_existing_sibling_binding`'s
incidental use of a `released`-status sibling, and one Stop-composite-key
test whose claim ordering incidentally exercised the new reap-on-write); the
handoff's "existing tests may be reseeded or rewritten" clause covered this,
but a plan that named the exact ordering conflict between reap-on-every-
write and a test fixture reusing `lease_status="released"` for unrelated
reasons would have saved a debugging pass.
