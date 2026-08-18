# Implementer Handoff — g3-implement, REWORK (attempt 2)

## Gate
g3-implement

## What changed since attempt 1
Your attempt 1 (`.agent-work/567-j/crew-handoffs/g3-implement-result.md`) was
correct to stop rather than guess. Ruling on both open questions, both within
my own file ownership (`scripts/run_crew.py`, its tests) — proceed, no further
float needed:

**Ruling 1 — the three additional failing tests: fix all three, in scope.**
Wiring `resolve_model` into the shared choke point genuinely changed their
premise, not just `MandatoryModelTests`'s two named cases. Rewrite each
preserving its *original testing intent*, not by weakening the new
validation:
- `MandatoryModelTests::test_crew_spec_refuses_falsy_model_directly` — same
  defect class as the two already-rewritten cases. Rewrite to assert
  `CrewSpec(role="reviewer", model=None)` now resolves to the `"reviewer"`
  role's declared default (`"sonnet"`) instead of raising. Add (or confirm
  already covered) a case using a role/harness pair genuinely absent from
  `ROLE_MODEL_TIERS` that still raises, so "an undeclared pair still refuses"
  stays asserted somewhere in this class.
- `ExternalDispatchTests::test_cli_parser_persists_model_and_reasoning_effort_to_external_registry` —
  its intent is "an explicit `--model`/`--reasoning-effort` pair on the CLI
  persists to the external registry entry," not "any arbitrary string
  persists unchanged." Swap the arbitrary `"gpt-5.6"` for a real, in-table,
  non-default choice for the role under test (e.g. `role="implementer"`,
  `--model haiku --reason "<something plausible>"` — `"haiku"` is in
  `implementer`'s allowed set under harness `"claude"`, non-default, so it
  requires a `--reason`, which is itself worth asserting persists too). Keep
  asserting the registry entry's `model` (and now also `reason`) field.
- `BackendEquivalenceTests::test_external_dispatch_records_without_spawning_returns_none` —
  its intent is proving the external backend's record-only behavior (no
  process spawned, returns `None`), not testing a specific model value. Swap
  `CrewSpec(role="implementer", model="opus")` for
  `CrewSpec(role="implementer", model="sonnet")` (`"sonnet"` is
  `"implementer"`'s **default**, so it needs no `--reason`) — the smallest
  change that keeps the test's actual assertion (no spawn, returns `None`)
  intact while satisfying the new validation.

After these three plus the two already-rewritten cases, re-run the full
suite. The only failure that may remain is the 4th one you already correctly
diagnosed as pre-existing and environmental
(`ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`,
`CREW_SCRATCH_DIR` leak — confirmed via your own `git stash` isolation test).
That one is **out of scope**, named in the launch order's own Inherited
Context as a known, do-not-fix failure; leave it exactly as-is.

**Ruling 2 — the `--abandon --relaunch` reason asymmetry: fix it, in scope.**
You correctly followed the handoff's literal wording (fresh-launch path
only) and flagged the asymmetry rather than silently extending it — that was
the right call given the stop-condition instruction at the time. Now
extending it explicitly: thread `reason=args.reason` into the
`--abandon --relaunch` `CrewSpec(...)` construction too (the second call site
you found at your evidence's line ~2363), exactly parallel to the
fresh-launch site. The two call sites should end up symmetric — both pass
`reason=args.reason`. Add one small test confirming a relaunch with a
non-default in-set `--model` and a `--reason` succeeds and records the reason,
mirroring the fresh-launch case's equivalent test.

## Everything else from the original handoff stands unchanged
Allowed Scope, Specific Exclusions, Constraints, Map Anchors, Deliverable Path
Check, Wiring Grep, Verification Commands, and Authority are all exactly as
in `.agent-work/567-j/crew-handoffs/g3-implement-handoff.md` — re-read it
alongside this addendum rather than treating this as a full replacement.

## Close Criteria (addendum — supersedes the "two tests" count in the original)
- All five originally-named test obligations (two rewrites + three new) PLUS
  the three additional rewrites above PLUS the one new relaunch-reason test =
  full suite green except the one confirmed pre-existing/environmental
  failure.
- `py -m pytest tests/test_crew_launcher.py -q` output pasted in full.
- State the final tally explicitly (e.g. "N passed, 1 known-unrelated failed").

## Stop Conditions
Unchanged from the original handoff, with the two rulings above now settled
and no longer stop conditions. Stop and return again only for a genuinely new
issue not covered by this addendum.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape, including Workflow Feedback.
Write it to `.agent-work/567-j/crew-handoffs/g3-implement-result.md` (same
path, this is attempt 2 — overwrite) before ending your turn.
