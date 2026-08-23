# Reviewer Handoff

## Gate
g1-implement (execute.json, work-id w3-promote) — reviewing the implementer's completed slice

## Survey State Location
Create your review survey checklist at `.agent-work/w3-promote/g1-review/review.json`.

## What Was Implemented
8 named `check: null` conditions in `skills/commander/templates/COMMANDER_SPINE.template.json`
promoted to real `command`/`artifact`-kind checks (no new engine mechanism): `init.c1`, `plan.c1`,
`plan.c2`, `plan.c4`, `plan.c5`, `reconcile.c1`, `archive.c2`, `archive.c3`. Overlay synced. A new
red-proof test class `CommanderSpineW3PromotePromotions` added to `tests/test_checklist_engine.py`.
`tests/test_validate_spine.py`'s stale floor comment corrected. The Commander (this dispatcher)
additionally fixed 3 collateral test files the implementer correctly flagged as out-of-scope
(`tests/test_shipped_check_commands_resolve.py`, `tests/test_plan_step_contract.py`,
`tests/test_install_constellation.py`) and reran the code map build — review those 3 fixes too,
they are in scope for YOUR review even though they were outside the implementer's own handoff.

## How to Inspect the Diff
Uncommitted working tree. `git status --porcelain` then `git diff` for each file below (untracked-safe).

## Task Statement
Promote exactly 8 named conditions using only existing check kinds, ship them blocking (this wave
has the Admiral adjudication in hand), red-proof each with an adversary-chosen mutation, keep the
suite green at this gate boundary. Full handoff: `.agent-work/w3-promote/crew-handoffs/g1-implementer-handoff.md`.
Full result: `.agent-work/w3-promote/crew-handoffs/g1-implementer-result.md`.

## Close Criteria
- Exactly the 8 named conditions changed in `COMMANDER_SPINE.template.json`; nothing else in that
  file touched (verify against `git diff` — check `basis` objects on `plan.c2/c4/c5` are
  byte-identical before/after, and `bookend: true` on `init`/`archive` untouched).
- Each promoted `check` shape matches what the handoff specified (re-read
  `g1-implementer-handoff.md`'s Close Criteria items 1-8 and diff against the actual JSON).
- `plan.c2`'s promotion is existence-only — its `statement` text must be byte-unchanged (still
  describes anchors-cut-from-frame/ownership-scope-coverage, unverified by the check).
- Overlay (`.agent-work/templates/COMMANDER_SPINE.template.json`) byte-matches; confirm yourself
  with `python3 scripts/check_template_overlay_freshness.py`.
- The new red-proof test class: for each promoted condition, does it (a) assert the exact shipped
  shape, (b) assert no other condition changed, (c) attack with a mutation that is NOT a restatement
  of the check's own match/command text? Read `test_init_c1_command_check_discriminates_lease_status`
  and `test_archive_c2_command_check_discriminates_unpushed_commits` particularly closely — these
  spin up real tempdirs/git repos; confirm the "adversary-chosen" claim holds (e.g. `init.c1`'s
  mutation uses a status value neither `claim()` nor `release()` ever legitimately writes, not
  merely an absent key — is that actually a stronger/more adversarial probe than an absent-key case,
  or just a different one? Use your own judgment, this is a genuine question, not a leading one).
- `tests/test_validate_spine.py`'s floor assertion: is 17 (not 21, not something else) the correct
  fresh count given `init.c1`/`reconcile.c1` cleared two single-postcondition all-null gates? Re-run
  the corpus sweep yourself rather than trusting the stated number.
- The 3 collateral fixes (Commander's own, not the implementer's): do they correctly update stale
  pins to the NEW shape rather than just deleting the assertions? (`test_c4_and_c5_still_carry_no_check`
  should now assert the actual new check shape, not just disappear — confirm it does.)
- Full suite green AFTER all of the above: `python3 -m pytest -q`.

## Allowed Scope
Everything the implementer touched (see Scope in the result) plus the Commander's 3 collateral
fixes plus the code-map rebuild. You are reviewing, not editing — BLOCK with specific findings if
something is wrong, do not fix it yourself.

## Specific Exclusions
None outside this gate's files — `plan.c6`'s check text, `context.c1`, `execute.c1`, `triage.c1`,
`checklist_engine.py` should all be untouched; flag if any of these moved.

## Constraints the Implementation Must Respect
- `decision:no-new-check-kinds` — only `command`/`artifact` kinds used, verify no new kind invented.
- `decision:blocking-where-adjudicated` — all 8 shipped blocking (no report-only), verify this is
  actually justified (each reuses a kind already live elsewhere in this same file — spot-check a
  couple against the file's OWN pre-existing checks, not another template).
- Compact-format JSON hand-edit discipline — check the diff doesn't look reflowed/reformatted
  (a `json.dump` round-trip would visibly rewrite unrelated whitespace/key-ordering elsewhere in
  the file; confirm it didn't).

## Map Anchors (inbound)
- **Structural:** `skills/commander/templates/COMMANDER_SPINE.template.json`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`;
  `decision:red-proof-each-promotion` `@grade: settled/admiral`.

## Evidence Produced
See `g1-implementer-result.md`'s Evidence section (grep before/after, parse-check, overlay freshness,
targeted pytest run, full test-class listing and run). Independently reproduce every command rather
than trusting the pasted output.

## Suggested Model Tier
simple bounded — mechanical verification against a well-specified handoff.

## Stop Conditions
Return BLOCK if: any promoted check's shape diverges from spec without a stated, sound reason; the
red-proof for any condition is not genuinely adversarial (restates the match/command text); the
overlay is stale; the full suite is not green; any excluded file was touched.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write to `.agent-work/w3-promote/crew-handoffs/g1-reviewer-result.md`
before ending your turn.
