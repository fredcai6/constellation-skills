# Review Result

## Assigned Gate
g2 (issue #549)

## Result
`APPROVE`

## Handoff compliance
915daefa does exactly what g2 asked: keeps `decide_stop` blocking exactly the same stops, and changes only the rendered `reason`/`additionalContext` text for a mid-flight entry reachable only through a per-agent (`sid#agent_id`) key.

- `_session_keys(binding, sid)` (`scripts/hooks/spine_rail.py:515-538`) reproduces `session_view`'s exact pre-existing two-branch asymmetry — diffed the old inline condition against the new extracted one and they are byte-identical: `key == sid or (isinstance(key, str) and key.startswith(prefix))`. Not tidied into a single coerced check.
- `session_view_provenance(binding, sid)` (`:558-580`) folds over the **same** `_session_keys(binding, sid)` call `session_view` uses — confirmed by reading the code (both call sites pass identical arguments with no mutation of `binding` in between) and by `test_session_view_provenance_mixed_matches_session_view_keys`, which asserts key-set equality between `session_view`'s and `session_view_provenance`'s outputs against a real multi-agent parent+2-subagent fixture.
- `decide_stop` (`:1439-1494`) branches only at the render step: `owner_key is None or owner_key == sid` → unchanged `_mid_flight_reason`/`reconstruct_current`; else → new `_owning_session_reason` and a withheld `additionalContext` (`"(withheld: gate belongs to {owner})"`, never calling `reconstruct_current` in that branch). Isolated the full `decide_stop` diff (old vs new) and it is exactly two hunks: the `owners = session_view_provenance(...)` addition, and this if/else — nothing else in the function moved.
- `decide_session_start`'s function body is **byte-identical** old vs new — extracted both 81-line bodies programmatically and diffed them; zero delta. `grep` for `def (binding_key|_foreign_worktree|_mid_flight_reason|_entry_mid_flight_view)` added/removed lines returns nothing — all four specifically-excluded functions are used as-is.

## Scope drift
None. `git show 915daefa --stat` touches exactly `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`. `git diff --stat 915daefa~1 915daefa` is empty for every fenced file (`scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json`) and for `scripts/run_crew.py` / `tests/test_crew_launcher.py` (the separate, already-merged g1 gate, `cbd18faf`).

## Evidence verdict
Reproduced everything myself, not just trusted the pasted evidence:

- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_spine_rail.py` → **150 passed, 1 skipped**, matching the handoff's pasted evidence exactly. Named the skip with `-rs`: `tests/test_spine_rail.py:833` — `ntpath`'s normcase, Windows-only, pre-existing and unrelated.
- `test_session_view_merges_one_bare_and_two_composite_keys` passes unmodified; extracted its body from the old and new test file revisions and diffed them — byte-identical, confirming zero test-content drift.
- Ran the full repo suite (`tests/`) as a broader sanity pass: 3077 passed, 6 skipped, 1146 subtests passed, **1 pre-existing unrelated failure** (`test_code_map.py::MapTreeFreshnessTests` — `map/INDEX.md` staleness). Verified via a throwaway `git worktree add` at the parent commit (`915daefa~1` / `cbd18faf`) that this test **already failed before this change** (drift 1198 vs. committed 1197); this commit's 3 new top-level functions widened that pre-existing drift to 1201 vs. 1197. Not a blocker (see Reconciliation below), but the implementer's own "unrelated to this change" framing understates it slightly — raised as a triage candidate, not silently dropped.
- **Both** `reason` and `additionalContext` verified to withhold the imperative for the foreign-owned case, by two independent adversarial mutations (not just reading the assertions):
  1. Forced the render-step branch to always take the same-session path (`if owner_key is None or owner_key == sid` → `if True`). `test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` failed exactly as predicted (`COMPOSITE-MARKER` leaked into `reason`). Reverted; `git status --short` clean; suite back to 150/1.
  2. With the fix restored, mutated **only** the foreign branch's `ctx` line back to `reconstruct_current(spine)` (leaving `reason`'s branch alone). The same test failed on its **other** assertion (`COMPOSITE-MARKER` leaked into `additionalContext` this time) — proving the test's two assertions are independently load-bearing, not one vacuous and one redundant. Reverted; `git status --short` clean; suite green again.
- `test_stop_bare_sid_owned_mid_flight_still_renders_original_imperative_text` is a genuine control: it builds a binding with `list(binding.keys()) == [sid]` only (no subordinate involved) and asserts the **original** `BARE-MARKER` imperative still renders in both `reason` and `additionalContext` — proving the fix is scoped to foreign-owned entries, not a blanket reword. Confirmed it is not accidentally re-exercising the foreign-owned path.
- `test_session_start_composite_key_entry_still_renders_full_imperative_unchanged` is the required `decide_session_start` regression guard — confirmed it exists, exercises the composite-key-only path through `decide_session_start` (not `decide_stop`), and asserts the imperative is **not** withheld there (correctly out of scope for this fix).

## Code/doc quality
- `_session_keys`, `session_view_provenance`, `_owning_session_reason` are genuinely pure (no file I/O, no globals) — confirmed by reading every line, and by tests exercising them directly with plain dicts.
- `session_view` still never raises and returns `{}` on unusable input — unchanged `try/except`; both new helpers carry the same guarantee, covered by dedicated never-raises tests.
- Fowler pass (`r6-fowler`, `.agent-work/cleanup-c-liveness-rail/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0): 12/12 smells visited. 1 **flagged**, non-blocking: `session_view` and `session_view_provenance` both duplicate the `entries = binding.get(key); if not isinstance(entries, dict): continue` fetch-and-validate step — a small `_iter_owned_entries(binding, sid)` helper would remove the duplication and structurally guarantee (rather than merely test-prove) that the two functions can never disagree. 1 **overridden**, logged: the new functions' dense invariant-explaining docstrings match the file's own pre-existing documentation convention for hook-rail correctness invariants (e.g. the old `session_view`/`_mid_flight_reason` docstrings) — not comments papering over code that should have been simplified; the invariants they explain are proven genuinely load-bearing by this review's own mutation tests.

## Map impact verdict
- **Evidence supports claimed change:** yes — the implementer's evidence (the updated composite test, the full suite) backs the claimed behavior exactly as verified above.
- **Constraints not violated:** yes — `session_view`'s two-caller constraint and `decide_session_start`'s untouched-code constraint are both honored and independently confirmed.
- **Notes match the diff:** yes, with one caveat — the implementer's Map Impact "Trust limitations / drift found: none found ... unrelated to this change" is imprecise. `map/INDEX.md` staleness predates this commit (confirmed on the parent commit), but this commit's 3 new functions did widen the pre-existing drift. Minor, non-blocking, flagged as a triage candidate (`tc1`) rather than accepted silently.
- **Decision candidates surfaced:** yes — `keep-the-block-drop-the-imperative` (`@grade: settled/human`) is cited and implemented exactly as graded.
- **Durable context routed:** yes — `tc1` (map staleness) is captured in the survey's `triage_candidates` for Commander/Triage.

## Reconciliation check
Map orientation is DEGRADED-UNPARSEABLE at baseline (zero authored architecture-map anchors corpus-wide, per the handoff) — nothing to reconcile against on that front. No other architecture/contract divergence found.

## Blockers
- none

## Out-of-scope observations
- `duplicated-code` (Fowler, non-blocking): `session_view` and `session_view_provenance` duplicate a 3-line fetch-and-validate step; a shared `_iter_owned_entries` helper would remove it and strengthen the "must never disagree" invariant structurally. Not required for this gate.
- `map/INDEX.md` is stale (triage candidate `tc1`, recorded in the survey): pre-existing before this commit, widened by this commit's 3 new functions. Rerun `python -m scripts.code_map build --root .` and commit the result at Commander's discretion; not a g2 blocker.

## Workflow Feedback
- **Handoff gaps:** none — the handoff was unusually precise (specific line ranges, specific test names, specific grep commands to run). The one soft gap: it doesn't say what to do if the implementer's own "Trust limitations" claim in Map Impact turns out to be slightly wrong (as it was here, re: map staleness) — I treated this as a non-blocking finding + triage flag rather than a BLOCK, since the stop conditions list doesn't cover "an implementer note is imprecise but not materially wrong."
- **Context rediscovered:** had to independently discover that `map/INDEX.md` staleness predates this commit by spinning up a throwaway `git worktree add` at the parent commit — the handoff's "Map orientation is DEGRADED-UNPARSEABLE" note primed me to expect no map artifact at all, not a *separate*, pre-existing, code-generated `map/INDEX.md` staleness test failure in the full suite. Worth naming in a future handoff if the two are meant to be understood as unrelated concerns.
- **Instructions improvised around:** the skill's "claim the checklist lease... this is your first command" instruction; I built my own `REVIEW_SURVEY.json` per the "nothing bound" branch (the handoff explicitly said no MCP spine door is bound and not to attempt `spine_*` calls), matching the precedent set by `g1-review/review.json` (claim → start/record loop, no session-id needed on `current`, release at the end). This worked cleanly; no friction.
- **What would have made this easier:** none — the handoff's file:line citations, named tests, and explicit stop conditions made this reproducible end-to-end without guessing.

## Return status
complete
