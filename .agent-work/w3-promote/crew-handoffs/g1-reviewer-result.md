# Review Result

## Assigned Gate
`g1-implement` (execute.json, work-id w3-promote) — 8 promoted conditions in
`skills/commander/templates/COMMANDER_SPINE.template.json` plus the Commander's 3 collateral test
fixes.

## Result
`APPROVE`

## Handoff compliance
Full compliance, independently reproduced. All 8 named conditions (`init.c1`, `plan.c1`, `plan.c2`,
`plan.c4`, `plan.c5`, `reconcile.c1`, `archive.c2`, `archive.c3`) changed from `check: null` to the
exact shape the implementer handoff specified:

- `init.c1` → `command`, `python3 -c "..."` reading `<repo-root>/.agent-work/<work-id>/spine.json`'s
  `engine_session.status`, exits 0 iff `"active"`.
- `plan.c1` → `artifact`, `evidence_type: "mission-frame"`, `match: {"status": ["produced",
  "skipped-as-trivial"]}`.
- `plan.c2` → `artifact`, `evidence_type: "execute-plan"`, `match: {"exists": true}` — existence-only,
  `statement` text byte-unchanged, confirmed.
- `plan.c4` → `artifact`, `evidence_type: "plan-alternatives"`, `match: {"converged": true}`.
- `plan.c5` → `artifact`, `evidence_type: "plan-critic"`, `match: {"triaged": true}`.
- `reconcile.c1` → `artifact`, `evidence_type: "file-diff"`, `match: {"nonempty": true}`.
- `archive.c2` → `command`, `test "$(git -C <repo-root> rev-parse @)" = "$(git -C <repo-root>
  rev-parse @{u})"`.
- `archive.c3` → `artifact`, `evidence_type: "user-decision"`, no `match` key — byte-identical to
  the pre-existing `archive.c5`/`review.c1`/`triage.c2`/`understand.c1` shape (grepped and
  confirmed).

A new red-proof test class, `CommanderSpineW3PromotePromotions`, was independently run
(`pytest tests/test_checklist_engine.py -k CommanderSpineW3PromotePromotions -v`): 10/10 pass. Each
promoted condition is attacked at (a) exact shape, (b) no-condition-outside-the-13-pre-existing-plus-8
population, (c) an adversary-chosen mutation, and none of the mutations restate the check's own
match/command text.

## Scope drift
None. `git diff --stat` on the spine template: exactly 8 insertions/8 deletions, total line count
unchanged at 142 before and after (no reflow). The `basis` objects on `plan.c2/c4/c5` are
byte-identical (the diff shows only the sibling `check` field moved on those lines). `bookend: true`
is intact on both `init` (line 16) and `archive` (line 136). `plan.c6`, `context.*`, `execute.*`,
`triage.*` are untouched — confirmed by grepping the diff for those task ids and finding no hits.
`scripts/checklist_engine.py`'s diff is empty. `tests/test_checklist_engine.py`'s diff is a pure
341-line append at EOF; no existing class (including `CommanderSpineBasisFields`) is touched.
`map/INDEX.md`'s 6-line diff is a legitimate freshness rebuild (5723→5739 entities, exactly matching
the new test class's added Python entities) — `tests/test_code_map.py -k freshness` independently
reproduced green.

## Evidence verdict
Every command in the implementer's Evidence section and the handoff's Verification Commands was
independently re-run, not trusted from the pasted transcript:

- `python3 -c "import json; json.load(...)"` — parse OK.
- `python3 scripts/check_template_overlay_freshness.py` — 56/56 templates, none stale.
- `python3 -m pytest tests/test_checklist_engine.py -k CommanderSpineW3PromotePromotions -v` — 10
  passed.
- Full corpus sweep (`validate_spine.validate_file` over `SHIPPED_TEMPLATES`, run directly, not
  just via the `>= 15` assertion) — re-measured `falsifiable-all-null: 17`,
  `falsifiable-unresolved-placeholder: 2`. **17 is confirmed correct**, not merely "passes the
  floor" — matches the corrected comment exactly.
- `python3 -m pytest -q` (full suite, no filter) — **3739 passed, 9 skipped, 1282 subtests passed,
  exit 0**.
- Grepped `scripts/checklist_engine.py` for the exact refusal strings the red-proof test asserts
  (`"is type {type!r}, not the required {want_type!r}"`, `"does not match required"`,
  `"engine-checked; cannot attest"`) — all three match verbatim, not a loose regex coincidence.
- Grepped `scripts/checklist_engine.py`'s `claim()`/`release()` — confirmed they only ever write
  `status: "active"` / `status: "released"`, so `init.c1`'s adversary value
  `"quantum-entangled-lease"` is genuinely never written by the legitimate lease machinery, not a
  straw-man mutation.

**On the handoff's specific question** (is a present-but-wrong-value mutation actually a
stronger/more adversarial probe than an absent-key case, or just different?): it is stronger, not
merely different. The check reads `d.get('engine_session', {}).get('status') == 'active'`. An
absent-key mutation would also correctly fail a weaker, buggy implementation that only tested key
*presence* (e.g. `'status' in d.get('engine_session', {})`) — that buggy version happens to agree
with the correct one on an absent key. A present-but-wrong-value mutation is the only kind that
distinguishes "compares to the specific literal `'active'`" from "merely checks the key exists" —
so it discriminates against a strictly larger class of incorrect implementations. Same reasoning
applies to `archive.c2`'s "local commit made after the last push" mutation versus a weaker "no
upstream configured at all" mutation: the chosen one is the only one that actually exercises the
`@` vs `@{u}` comparison the check text names, rather than failing for an unrelated reason (missing
upstream) that a wrong implementation could also stumble into passing/failing by coincidence.

## Code/doc quality
Fowler pass recorded to `.agent-work/w3-promote/g1-review/FOWLER_PASS.json`,
`scripts/verify_fowler_pass.py` exits 0 (`smells=12, flagged=[], overridden=['large-class']`). 11 of
12 baseline smells absent. `large-class` (the new ~340-line test class) is overridden: the
implementer handoff explicitly required the class be "modeled directly on the existing
CommanderSpineBasisFields class in the same file," which already establishes this size/shape as the
repo's convention for a self-contained, drift-guarded, per-gate red-proof class — splitting it would
scatter one cohesive gate's fixtures across files for no locality gain. `duplicated-code` is absent
on its merits, not by override: the 5 artifact-kind promotions share one parameterized helper,
`_assert_artifact_discriminates`, rather than restating the 3-step wrong-type/wrong-match/matching
drive per test. `comments-as-deodorant` is absent: the mutation-rationale comments were a named
handoff requirement documenting genuinely non-obvious test-design choices, not compensation for
unclear code.

## Map impact verdict
- **Evidence supports claimed change:** yes — the red-proof test class and the independently
  re-run full suite both back the claimed "each check now genuinely discriminates" behavior.
- **Constraints not violated:** yes — `decision:no-new-check-kinds` (only `command`/`artifact`
  used) and `decision:blocking-where-adjudicated` (no `report_only`/`override_policy` on any of the
  8, independently confirmed by loading the JSON and inspecting each condition) both hold.
- **Notes match the diff:** yes. The implementer's Map Impact note that `plan.c4`/`plan.c5`'s
  `statement` text still literally says "NOT machine-verified" despite now carrying a real check is
  accurate and correctly flagged as a genuine follow-up, not a defect — Close Criteria named only
  the `check` field in scope, and the sibling `test_c4_and_c5_declare_they_are_not_machine_verified`
  test (unchanged) still passes for the same reason.
- **Decision candidates surfaced:** none needed beyond what was already surfaced; no new authority
  gap was hit.
- **Durable context routed:** yes — `map/INDEX.md` staleness and the 3 collateral test breaks were
  both flagged loudly in the implementer's Out-of-scope observations rather than silently
  fixed-out-of-scope or silently dropped, and the Commander correctly picked both up.

New `evidence_type` values (`mission-frame`, `execute-plan`, `plan-alternatives`, `plan-critic`,
`file-diff`) are not previously used anywhere in the shipped corpus. Verified this is sound, not an
undocumented new mechanism: `evidence_type` is a free-form string in both `checklist_engine.py`
(`attach()`/`_check_condition()`, `ev.get("type") == chk["evidence_type"]`, no closed set) and
`validate_spine.py` (only `"user-decision"` is special-cased, for the *absent-match* exemption, which
does not apply here since 4 of these 5 new checks carry a real `match`). The one check without a
`match` (`archive.c3`) reuses `"user-decision"`, already in
`ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH`. No `falsifiable-artifact-asserts-property` fault appears in
the re-measured corpus sweep, confirming this independently rather than trusting the implementer's
prose claim about it.

## Reconciliation check
No structural/architecture-baseline concern. `map/INDEX.md`'s rebuild is the correct, narrowly
scoped reconciliation for this gate's own diff (new test entities only) — independently confirmed
green via `tests/test_code_map.py -k freshness`.

## The 3 collateral fixes (Commander's own)
All 3 correctly update stale pins to the new shape rather than deleting the assertions, matching the
Close Criteria's explicit ask:

- `tests/test_shipped_check_commands_resolve.py`: `EXPECTED_COMMAND_CHECK_COUNT` 11 → 13, with a
  comment naming exactly which two checks (`init.c1`, `archive.c2`) account for the delta. Correct —
  those are the only two of the 8 promotions that are `command`-kind.
- `tests/test_plan_step_contract.py`: `test_c4_and_c5_still_carry_no_check` renamed to
  `test_c4_and_c5_now_carry_an_existence_only_artifact_check` and rewritten to assert the exact new
  `artifact` check shape (via `assertEqual` against the literal dict), not just deleted — matches the
  test's own prior docstring instruction ("If a check ever lands, these tests must be revisited"),
  and the sibling `test_c4_and_c5_declare_they_are_not_machine_verified` is correctly left unchanged.
- `tests/test_install_constellation.py`: rewritten to assert `init`'s check is non-null and carries
  no unresolved `<commander-skill-dir>` placeholder, with an updated comment explaining the new
  shape is an inlined `python3 -c` call (not a bundled-script path), correctly matching the test's
  actual subject (absolute bundled-script-path resolution) rather than asserting something the new
  check doesn't even exercise.

## Blockers
- none.

## Out-of-scope observations
- `plan.c4`/`plan.c5`'s `statement` text still says "NOT machine-verified" though both now carry a
  real `artifact` check. Correctly out of this gate's scope (Close Criteria named only the `check`
  field); flagging as a triage candidate for a wording follow-up.
- `map/INDEX.md` freshness maintenance is a recurring collateral cost of any pytest-authoring gate in
  this repo. Worth considering whether a later wave folds a code-map rebuild step into the standard
  implementer/Commander checklist rather than leaving each gate to discover it independently, as this
  one did.
- An untracked `.agent-work/<work-id>/` directory (literal, unsubstituted placeholder name) exists
  in the worktree, predating this session. Not created by this gate; confirmed harmless and correctly
  left untouched.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: the reviewer handoff's Close Criteria, Stop
  Conditions, and specific probing questions (init.c1 adversarial-strength question, the 17-count
  re-derivation) were all answerable directly from the diff and repo state without needing anything
  the handoff omitted.
- **Context rediscovered:** the mechanism by which `evidence_type` is a free-form string (not a
  closed enum) is documented nowhere in one place — I had to independently grep
  `checklist_engine.py`'s `attach()`/`_check_condition()` and `validate_spine.py`'s
  `ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` to confirm the implementer's own Assumptions-section claim
  about this, since it is exactly the kind of claimed side-effect this skill's doctrine says must be
  independently reproduced, not trusted. This is the second review in this repo's history (per the
  implementer's own Workflow Feedback) to have needed this same fact; it may be worth landing a
  one-line note on `evidence_type` in `docs/CHECKLIST_SCHEMA.md` itself so future promotions don't
  each have to re-derive it from source.
- **Instructions improvised around:** this dispatch's parent explicitly instructed me not to call
  any `mcp__spine__*` tool and stated I have none on my tool surface — correct, per
  `references/checklist-engine.md`'s "The door does not follow you into a Task-tool subagent's OWN
  work" section: as a Task-tool subagent sharing my dispatcher Commander's process, any door I could
  see would be bound to the Commander's own `spine.json`, not a survey I own. I therefore did not
  claim a lease or drive `REVIEW_SURVEY.template.json` through the engine's verb loop as the skill's
  "Start here" section describes for a bound-door crew; instead I hand-tracked the same r0-r6 checks
  in a plain JSON file at `.agent-work/w3-promote/g1-review/review.json` (the path the handoff named
  as "Survey State Location"), worked every check to a recorded pass, and consolidated by hand. This
  is a real gap between the skill's default assumption (a dispatched crew always has *some* door,
  even if not its own) and this dispatch's actual environment (no `mcp__spine__*` tools at all) — the
  skill's own carve-out for "nothing is bound" case (author your own survey, no engine) is the
  closest documented match, and I followed that path.
- **What would have made this easier:** a short, explicit line in the skill itself (not just in the
  dispatch preamble) covering the "you have zero `mcp__spine__*` tools, not merely a foreign-bound
  door" case, so a future reviewer in this exact position doesn't have to infer the right fallback
  from a cross-reference in `references/checklist-engine.md` written primarily for the
  foreign-door case.

## Return status
`complete`
