# Review Result

## Assigned Gate
`g2` — reap + child-plan release (the #552 mechanism). Gate 2 of 3.

## Result
`APPROVE`

## Handoff compliance
Satisfied, independently reproduced rather than trusted from either account.

- `force_reap(project_dir) -> dict | None`: a genuine one-line library call, `return spine_rail._binding_transaction(Path(project_dir), lambda reaped: reaped)`. Zero edits to `spine_rail.py` (empty `git diff --stat`). Read `spine_rail.py:397-436` directly: `_binding_transaction` loads `raw`, computes `reaped = _reap_binding_entries(raw, now)`, calls `mutate(reaped)`, and persists only `if new_map != raw` — comparing against the *original* load, not the reaped map — so handing the reaped map straight back genuinely persists the reap now rather than eventually. `TestForceReap::test_innocent_a_released_targets_entry_is_gone_immediately` re-run alone: asserts the fixture target reads `status == "released"` *before* `force_reap` runs (the precondition sanity the handoff required), then the binding entry is gone immediately after, read via `spine_rail.load_binding`. The paired `test_violating_an_active_targets_entry_is_retained` confirms an active target survives, proving the reap is conditional, not a blanket wipe.
- `_release_child_plans(spine_path, work_dir, *, root, reason) -> dict`: read the full function body, not just the tests. All three safety properties present as shipped code:
  1. **Lineage, not proximity** — `declared_children` is built from each task's `child_checklist`, resolved relative to `work_dir`; an active-leased JSON under `work_dir` not in that set is left alone and reported in `unclaimed_active` (verified via the independently re-run negative test).
  2. **Honest non-owner release** — `caller_id` is read exclusively from the *parent* spine's own `engine_session.session_id` (loaded from `spine_path`, before the scan loop); the per-candidate scan loop reads only `.get("status")` on the child's data, never `.get("session_id")`. An AST-scoped source-segment check of `_release_child_plans` alone confirms no `session_id` read inside the loop.
  3. **Escape refusal** — both the declaration loop and the scan loop resolve every candidate via `Path.resolve()` and refuse (`continue`) unless `resolved.is_relative_to(resolved_work_dir)`; confirmed via the independently re-run symlink negative test (the real target's lease survives, and neither the symlink path nor the real target ends up in `released`).
- Every release routes through g1's `_engine_call` with `--force --reason`; `checklist_engine.main` independently grepped to appear exactly once in the module (line 661, inside `_engine_call`'s span) — the other 4 hits are docstring/comment prose, not call sites.
- Full suite independently re-run: **104 passed** (95 baseline → 104, +9: 2 `TestForceReap` + 7 `TestReleaseChildPlans`, matching the claimed count exactly).

## Scope drift
None. `git status --porcelain` shows only `scripts/spine_lifecycle.py` and `tests/test_spine_lifecycle.py` modified — the two allowed-scope files. `git check-ignore` exit 1 on both (tracked, not ignored). Fenced files (`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py`) independently re-confirmed empty `git diff --stat`. `finish_work`/`open_pr`/CLI absent (g3's scope, as expected). `done_refusal`/`_engine_call`/`_advance_and_release` (g1) reused, not modified — the only new lines around them are module-docstring prose. `closeout_refusal`/`close_work` untouched entirely. Wiring grep confirms `force_reap`/`_release_child_plans`'s only non-definition references are inside the test file — no production caller yet, matching the handoff's own stated expectation that g3's `finish_work` is the intended consumer.

## Evidence verdict
Required evidence present and demonstrates the behavior, independently reproduced:
- All three negative tests re-run in isolation (`-k "ReleaseChildPlans and violating"`, 3 passed): outside-`work_dir` prefix-sharing spine untouched, unclaimed active JSON left alone **and** reported in `unclaimed_active`, symlink escape refused with the real target's lease surviving.
- `force_reap` immediacy test re-run alone (`-k ForceReap`, 2 passed) — the precondition-sanity assertion (target reads `"released"` before the call) is present in the test body, not merely assumed.
- Fenced-file diff independently re-run: empty.
- Test mode: test-after (per handoff), satisfied — no TDD red step required or claimed.

## Code/doc quality
Constraints checked individually and pass:
- **Never run against a live spine file** — grep for live-repo paths (`epic-567-door`, `cmdr-g/spine`, `cmdr-g/execute`) in the new test block found none; every `TestForceReap`/`TestReleaseChildPlans` fixture builds under `tmp_path` exclusively.
- **Realpath-based containment, not string-prefix matching** — every containment check in `_release_child_plans` uses `Path.resolve()` + `is_relative_to`; no `startswith`/string-prefix comparison anywhere in the file. The outside-`work_dir`-sharing-a-prefix negative test (`cmdr-g` vs `cmdr-g2`) is exactly the adversarial case a string-prefix check would fail and the shipped check passes.

Fowler baseline pass complete (recorded to `.agent-work/epic-567-door/cmdr-g/g2-review/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0): 10/12 absent, 1 flagged, 2 overridden.
- **Flagged (non-blocking):** `duplicated-code` — the realpath-resolve-then-containment-check block is repeated verbatim across `_release_child_plans`'s declaration loop and scan loop. A small helper (e.g. `_resolve_within(path, boundary)`) would give property 3 one implementation instead of two. Carried forward as a triage candidate; consistent with g1-review's treatment of an analogous repeated-shape finding in `_advance_and_release`.
- **Overridden:** `primitive-obsession` (the plain-dict return shape is ratified in the handoff's Task/Authority sections and matches the module's own `close_work`/`_advance_and_release` convention) and `speculative-generality` (zero non-test callers at gate end, but the handoff's own Wiring Grep section names this as an expected, bounded consequence of the fixed g1/g2/g3 gate sequence — g1's identically-uncalled primitives were treated the same way at their own review).

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in the implementer's Map Impact section was independently reproduced (see Handoff compliance above), not merely trusted.
- **Constraints not violated:** yes — `constraint:fenced-files-untouched` and `constraint:single-engine-choke-point` both independently confirmed true.
- **Notes match the diff:** yes — the structural claim (two new module-level functions appended after `_advance_and_release`, plus a new `sys.path.insert` for `hooks/` and a new top-level `import spine_rail`) matches the diff exactly; the capability claims (`capability:force-reap`, `capability:release-child-plans`, both dormant) match the wiring grep.
- **Decision candidates surfaced:** `decision:child-plans-count` (the inbound Map Anchor decision) is now implemented as shipped code, not merely designed — correctly reported, not overstated.
- **Durable context routed:** yes. The implementer's own trust-limitations note — `release` is not a `MUTATING_VERBS` member (`checklist_engine.py:70-74`), so no journal line is written for a release call — was independently verified accurate by grepping the `MUTATING_VERBS` set. This is a genuine, correctly-surfaced finding, not an overstated audit-trail claim, and g3 should not assume journal coverage for child releases either.

## Reconciliation check
No divergence from recorded architecture needing Commander reconciliation. `decision:child-plans-count` is honored as designed. No fenced files touched; g1's primitives reused, not modified.

## Blockers
- none

## Out-of-scope observations
- Non-blocking: `scripts/spine_lifecycle.py`'s module docstring narrates the pure/impure split through `_advance_and_release` but was not extended to describe `force_reap`/`_release_child_plans`. Deliberately deferred — g3 adds a third closeout primitive (`finish_work`) to the same section, so one docstring update after g3 lands avoids two touches. Flag for g3/its reviewer so it is not missed.
- Non-blocking: `_release_child_plans` walks `work_dir` with `Path.rglob("*.json")`, which can traverse a symlinked *directory* (not just a symlinked file) during recursion — the handoff's close criteria and required evidence name only the file-symlink case. Verified this is not a live safety gap: every discovered candidate is still realpath-resolved and `is_relative_to`-checked before any release, so a file reached via a symlinked directory that escapes `work_dir` would still be refused by the same guard. Recorded as a triage candidate if a directory-symlink escape test is judged worth adding explicitly.
- Non-blocking: the realpath-containment check is duplicated between `_release_child_plans`'s declaration loop and scan loop (see Fowler pass above) — a small extraction candidate, possibly combined with g1-review's analogous `_advance_and_release` finding into one later cleanup pass.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: gate, task, the three safety properties, allowed scope, exclusions, constraints, map anchors, required evidence, wiring grep, verification commands, and stop conditions were all present, internally consistent, and directly actionable.
- **Context rediscovered:** the reviewer survey template's `r6-fowler` postcondition command still carries a literal, unsubstituted `<work-id>` bug when the actual work-id is nested (e.g. `epic-567-door/cmdr-g/g2-review` rather than a flat `g2-review`) — a plain find/replace of `<work-id>` in the template produces `.agent-work/g2-review/FOWLER_PASS.json` instead of the survey's real path. This is the identical defect g1-review's own workflow feedback already reported and worked around via `amend --delta` (`retext-check`); it recurred verbatim here because the template itself was not corrected between the two reviews. Worth fixing at the template level (either drop the literal path and derive it structurally, or document the substitution as "the survey's own directory" rather than a bare `<work-id>` token) so a third gate in this same epic does not hit it a third time.
- **Instructions improvised around:** none beyond the above — repeated the same `amend --delta` / `retext-check` repair path g1-review used, per the survey template's own documented REPAIR PATH instructions.
- **What would have made this easier:** fixing the `r6-fowler` template's `<work-id>` substitution (see above) would save every future reviewer on a nested work area the same detour.

## Return status
`complete`
