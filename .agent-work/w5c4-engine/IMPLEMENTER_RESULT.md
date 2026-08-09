# IMPLEMENTER_RESULT — wave 5, `impl-w5-engine` (crew 4: engine internals)

Epic #418, wave 5. Launch order: `LO-w5-c4-engine.md`. Branch:
`epic-418/w5-engine-internals`, based on `ea854471`. Engine hash at HEAD:
`git rev-parse HEAD:scripts/checklist_engine.py` = `c281cb68eaac65d1169dd6737a6a322728df98eb`.

Nine issues, one crew, sole writer of `scripts/checklist_engine.py` and
`tests/test_checklist_engine.py` for the whole wave. **Six fixed, two floated,
one verified (already fixed/guarded) — plus one unfilled cross-file
regression found and fixed before push.**

## Return Shape — one line per issue

- **#474 — fixed.** `_new_task()` is now the one shared Task constructor;
  `append()` and `_build_amend_task()` both delegate to it. No observable
  behavior change. Evidence: `e-m1-474-1`.
- **#475 — fixed.** `TemplateOnlyFieldAllowlist` added (six fields, each
  with a stated reason). **Planted-field red-before-fix (pre-ruling #2):**
  `test_negative_self_test_catches_a_synthetic_planted_field` was written
  first, referencing not-yet-defined `_builder_task_keys` /
  `_assert_task_fields_allowed`, and run standalone via
  `pytest -k TemplateOnlyFieldAllowlist` **before** the walker existed.
  Observed genuine red: `NameError: name '_builder_task_keys' is not
  defined`. Walker + assertion then implemented; same test re-run green.
  Evidence: `e-m2-475-1`.
- **#476 — fixed.** `SchemaDocFieldReconciliation` reconciles
  `docs/CHECKLIST_SCHEMA.md`'s Task table against the engine's Task builder,
  both directions. No doc edit needed; one residual gap noted (a
  template-only field invisible to the property class) but deliberately not
  fixed — it is not what this check asserts. Evidence: `e-m3-476-1`.
- **#427 — fixed, then re-scoped after a regression it caused (see below).**
  Refusals counter arms on load. TDD red confirmed first
  (`AssertionError: None != 1`). Evidence: `e-m4-427-1`, superseded in
  scope by the fix described in "Regression found and fixed."
- **#503 — floated, larger-than-filed.** Investigated whether `--authority`
  on `amend`/`waive` can be bound to something checkable. Fresh
  `grep -n "authority=" tests/test_engine_survey_retext_and_newlines.py`
  (not owned, not in this crew's sole-writer set) confirms 5 call sites, all
  free-text (`authority="Commander w3a-465"`), not a resolvable
  why-record/evidence id. A reference-binding fix satisfying the issue's
  acceptance test would break those existing passing calls in a file this
  crew cannot edit. A shape/length heuristic is explicitly insufficient per
  the issue's own text (`"the agent itself"` is an equally-plausible bogus
  phrase). Pre-ruling #4 forbids a cryptographic ratification scheme,
  closing the remaining mechanical option. Floated to the Admiral: options
  are rename-only / evidence-id-binding / first-class grants. No code
  change. Evidence: `e-m5-503-2`.
- **#479 — fixed (kept-and-guarded, not deleted, per pre-ruling #3).** The
  `_render_directive_lines` `else` branch (a dict value that is not itself a
  dict) is proved dead by mutation and kept deliberately, mirroring
  `_render_anchor_lines`'s own unrecognized-shape posture. Added
  `test_dict_value_that_is_not_a_dict_renders_as_one_leaf_line`
  (`RenderDirectives`), confirmed green, then re-ran the mutation check
  myself: replaced the branch body with `raise RuntimeError(...)`, confirmed
  the new test now fails, restored the original code (verified by grep
  finding zero occurrences of the mutation marker afterward). The branch's
  "kept deliberately" reason is now checkable. Evidence: `e-m6-479-1`.
- **#480 — verified, already fixed and guarded (no code change).**
  Confirmed the issue's own claim: the directives flat-list-drop defect
  fixed in #433's g2 is guarded by
  `test_flat_list_with_a_non_string_item_renders_every_item` plus the
  `TaskFieldCompleteness` property class. Ran all four named/implied tests
  (the one plus three `TaskFieldCompleteness` tests, including the in-suite
  negative self-test `test_the_property_fails_when_a_populated_field_is_
  unrendered`): all passed. Confirms the defect is fixed and would be
  caught if it regressed. Evidence: `e-m7-480-1`.
- **#493 — fixed.** `append_journal_entry` wrote the journal in text mode,
  the same defect class #465 fixed in `save()`. Added
  `AppendJournalEntryLineEndings` (three fixtures: LF-preserved,
  CRLF-preserved, new-file-defaults-LF), mirroring
  `test_engine_survey_retext_and_newlines.py`'s `write_bytes`/`read_bytes`
  pattern. Ran against unfixed code: 2 of 3 failed for the real reason
  (line-ending churn) — `AssertionError: 1 != 0 : append_journal_entry
  churned an LF journal to CRLF`, and the new-file default likewise red.
  Fixed by reusing `_dominant_newline(jp)` (append-only variant of `save`'s
  pattern) and switching to binary append (`"ab"`). All three green after.
  Evidence: `e-m8-493-1`.
- **#495 — floated entirely (none of the six writers are inside this
  crew's owned files).** Command run:
  `grep -rn "encoding=.utf-8." --include="*.py" scripts/ | grep -v checklist_engine.py`.
  Confirmed all six issue-named sites present exactly as claimed:
  `collect_feedback.py:290,365`; `install_constellation.py:911,1182,1241`;
  `build_architecture_map.py:385` — all `write_text(..., encoding="utf-8")`
  with no `newline=`. The command surfaced many additional
  `encoding="utf-8"` matches (read_text calls, subprocess `encoding=`,
  writers that already pass `newline=`); named honestly, none of those are
  additional instances of the same defect. `install_constellation.py` is
  crew 2's owned file; `collect_feedback.py` and `build_architecture_map.py`
  are outside every owned-file list for this wave. No code change; none of
  the three files touched.

## Regression found and fixed (not one of the nine, found running the full suite before push)

The #427 fix as originally landed (`if cl.get("engine_session") is None:
cl.setdefault("refusals", 0)` on **every** `main()` load) broke
`tests/test_episode_negative_control.py` (3 failures: `test_unclaimed_
child_topology_refuses_only_role_and_refusals`, `test_the_seam_emits_the_
same_group_unasked`, `test_red_proof_sharp_fabricated_role`) — a file this
crew does not own.

Root cause: a **child gate plan** (#357's documented shape) is legitimately
driven with `engine_session` staying `None` for its **entire life** —
`start`/`attest`/`advance`/`reopen` with no lease and no `claim` call, ever.
The original #427 fix could not distinguish that shape from "a checklist
about to get its first-ever `claim`," and armed `refusals` on **any**
refusal while unclaimed — giving the never-claimed child topology a
`refusals` key it must never carry. `test_episode_negative_control.py`
asserts that key's *absence* is structural for that shape, not "zero
refusals happened."

Fix (in `scripts/checklist_engine.py`, owned): narrowed the arming
condition to `cl.get("engine_session") is None and args.verb == "claim"` —
arms only on an attempted `claim` call, which still covers #427's own
confirmed acceptance test (a malformed `claim --session-id ""`) while
leaving every non-claim verb on a never-claimed checklist untouched.

Added a red-before-green regression test,
`test_refusal_on_a_never_claimed_child_gate_plan_does_not_arm_the_counter`
(`Leasing`, `tests/test_checklist_engine.py`): reproduces the #357 shape (a
refused `start` on an unknown gate id, no `claim` ever called) and asserts
`refusals` stays absent. Confirmed genuinely red against the original #427
fix (`AssertionError: 'refusals' unexpectedly found in {...}`), green after
the narrowing.

Both `tests/test_checklist_engine.py`'s own `test_refusal_before_the_first_
ever_claim_is_counted` and the new regression test pass together after the
fix, and all 15 tests in `tests/test_episode_negative_control.py` now pass.

## Evidence

- Targeted suite (`tests/test_checklist_engine.py`): **428 passed, 128
  subtests passed.**
- Full suite (`python -m pytest -q`, real unpiped exit code, not read from a
  pipe): **1877 passed, 2 skipped, 828 subtests passed, real exit 0**
  (up from main's pre-wave baseline of 1871 passed / 2 skipped / 829
  subtests — the subtest count shift is `TaskFieldCompleteness`'s subtest
  shape changing under the new allowlist walker, not a dropped check; net
  new tests added by this wave more than offset it).
- `tests/test_episode_negative_control.py` re-run standalone after the
  regression fix: **15 passed.**

## PR

**#514**: https://github.com/fredcai6/constellation-skills/pull/514

All nine issues (#474, #475, #476, #427, #503, #479, #480, #493, #495)
commented with their return-shape line and evidence, then closed.

## Not done

- **#503, #495** floated to the Admiral rather than fixed — see above for
  the specific reasons and the decision options for #503.
- **#480** required no code change (already fixed/guarded); listed as
  "verified," not "fixed," to avoid claiming a fix that didn't happen.
- Nothing else was left undone inside this crew's scope. The
  `test_episode_negative_control.py` regression was found and fixed as part
  of "run the full suite before you push," not floated, because its root
  cause lived entirely inside this crew's owned file
  (`scripts/checklist_engine.py`) and the fix did not touch the
  unowned test file.

## Workflow Feedback

- The launch order's #427 pre-ruling and issue body describe the target
  scenario as "malformed calls prior to `claim`," which reads as
  verb-agnostic. The actual acceptance test (and the only test this crew
  wrote against it) exercises specifically a malformed `claim` call. The
  broader (verb-agnostic) reading is the one that collides with #357's
  documented child-gate-plan shape. A launch order or issue body that names
  the #357 interaction explicitly would have let this be designed away
  instead of caught at the wrapup full-suite run — worth flagging for #357
  and #427-adjacent issues in future waves that touch `main()`'s
  refusal-counting path.
- No other handoff gaps: the nine issue bodies, pre-rulings, and file
  ownership boundary were sufficient to run every other item without
  needing to guess.

## Map Impact

- `scripts/checklist_engine.py`'s `main()` now has a verb-scoped guard
  (`args.verb == "claim"`) on the `#427` refusals-arming logic, specifically
  because of the `#357` child-gate-plan shape (`engine_session` stays `None`
  for that shape's entire life by design). Any future change to
  `main()`'s refusal-counting or lease-arming logic should re-check this
  interaction against `tests/test_episode_negative_control.py`'s child
  topology, since that invariant is not visible from
  `tests/test_checklist_engine.py` alone.
