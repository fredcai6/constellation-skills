# Implementation Result

## Assigned gate
g1 (g1-implement) — add a report-only `basis` sibling field to the `Condition` schema

## Completed slice
Added the full `basis` mechanism described in the handoff:

1. **Render.** `_condition_view` passes the stored `basis` dict through unchanged (INV-2-pure, no probe). A new `_render_basis_line(basis)` helper formats it, wired into `render_human`'s open-conditions loop so it prints one indented line (`    basis: file <path>` / `    basis: evidence_ref <task_id>.<cond_id>`) immediately under a condition's own `{id} [unmet] {kind} — {statement}` line — only when `basis` is populated and `locator_kind != "abstain"`. Same populated-only convention `constraints`/`anchors`/`directives` already use.
2. **Attest guard.** New `_resolve_basis_locator(cl, base_dir, basis) -> str | None` dispatcher: `file` resolves `locator.path` against `base_dir` (same convention as `_collect_changed_files`'s `root = base_dir or Path.cwd()`, then `root / path`), glob-aware with `min_matches`; `evidence_ref` is pure — walks `cl["tasks"][task_id]`'s pre/postconditions for `cond_id`, requires `satisfied` + non-null `satisfied_by`. `attest()` gained a `base_dir: Path | None = None` param, threaded from the CLI's `_run_verb` dispatch (`base_dir=base_dir`, the checklist file's own directory). Inside the existing `if chk is None:` branch, before the unconditional accept: absent/abstain `basis` skips the guard entirely (unchanged legacy path); otherwise it resolves the locator, **always** calls `attach(cl, iid, "basis-check", {...})` (pass or fail), then falls through to the same unconditional accept — never raises.
3. **Docs.** `docs/CHECKLIST_SCHEMA.md`: new `basis` row in the Condition table, `basis-check` added to the Evidence `type` enum + `payload` row, and a new subsection "Basis — a report-only locator for a qualitative condition" documenting the shape, both locator kinds, the report-only guarantee, and the always-attached `basis-check` evidence.

Only `file` and `evidence_ref` locator kinds exist; `state_field`/`command` were not implemented (named untaken roads per the handoff). The guard is never blocking under any config — no toggle was added.

## Scope
**Files changed:**
- `scripts/checklist_engine.py`
- `docs/CHECKLIST_SCHEMA.md`
- `tests/test_checklist_engine.py`

**Specific exclusions touched:** no — `COMMANDER_SPINE.template.json`, `generate_spine.py`, `specs/`, and `waive()`/forced claim-release/`consolidate --override-reason`/`trip_ledger` were all left untouched (confirmed by the diff-stat below: exactly the three allowed-scope files changed).

## Behavior changed
Yes, additively only:
- `current`/`render_human` output gains one new line per open condition, but **only** when that condition carries a populated, non-abstain `basis` — no existing shipped template carries this field yet, so no shipped template's `current` output changes (`GoldenOutputBriefing` stays green, confirmed).
- `attest`ing a `check: null` condition with a populated, non-abstain `basis` now also attaches one `basis-check` evidence item, pass or fail. `attest` on a condition with no `basis` (or `locator_kind: "abstain"`) is byte-identical to the pre-change behavior — same return value, same `satisfied_by` shape, no evidence attached (verified by `test_no_basis_attest_is_byte_identical_to_legacy` and `test_abstain_basis_behaves_like_no_basis`).

## Map Impact
- **Structural anchors touched:** `scripts/checklist_engine.py:_condition_view` (~2389, gained `basis` passthrough), `scripts/checklist_engine.py:render_human` (~2679+, new `_render_basis_line` helper + loop change), `scripts/checklist_engine.py:attest` (~3438, new `base_dir` param + basis guard), `scripts/checklist_engine.py:_run_verb` (~3868, threads `base_dir` into `attest`), `docs/CHECKLIST_SCHEMA.md` §Condition and new §"Basis — a report-only locator for a qualitative condition".
- **Capabilities added:** a plan author can now declare, on any `check: null` Condition, a `basis` locator (`file` or `evidence_ref`) that renders to the attesting agent and is resolved-and-recorded (never blocking) at attest time via a new `basis-check` evidence type.
- **Constraints/assumptions touched:** INV-2 purity (`state()`/`render_human`/`_condition_view` never probe — honored: the render path reads only the stored `basis` dict, resolution happens only inside `attest()`); `ruling-widening-live-refusal-report-only` (honored: the new attest code path never raises); `ruling-decorative-basis-is-a-failure` (honored: authored + rendered + resolved-and-recorded together, not just one of the three).
- **Decision candidates:** none — the locator-kind vocabulary (`file`/`evidence_ref`/`abstain`) was ratified in `PLAN_ALTERNATIVES.md` and implemented as specified, not re-derived.
- **Claims/evidence produced:** `claim:basis-attest-report-only` — backed by `test_file_basis_missing_target_is_report_only_and_records_unresolved` and `test_evidence_ref_basis_unresolved_when_sibling_condition_unsatisfied`, both asserting the attest call still succeeds despite an unresolved locator.
- **Triage candidates:** none surfaced.

## Test mode
**Required:** test-first (TDD, red-then-green)
**Satisfied:** yes — two vertical slices (render, then attest guard), each with tests written first, observed failing against the unmodified engine, then implemented to green.

## Evidence

```bash
cd /home/tommy/projects/569-w2-basis && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q tests/test_checklist_engine.py
```

**Result:** pass — `511 passed, 145 subtests passed in 4.65s` (includes the existing `GoldenOutputBriefing` and `TemplateOnlyFieldAllowlist` classes, both green, confirming no existing shipped template's `current` output or field-shape assumptions changed).

## TDD evidence, if required

**Slice 1 — render (`BasisRendering`, 6 tests).**

Failing test observed (pre-implementation):
```
$ python -m pytest -q tests/test_checklist_engine.py -k Basis
...
E       AssertionError: 'ACTI[76 chars]ten\n0/1 met\nnext: attest g1 --cond c1 --which postconditions' != 'ACTI[76 chars]ten\n    basis: file .agent-work/w2-basis/MISS[67 chars]ions'
tests/test_checklist_engine.py:5938 (test_populated_file_basis_renders_basis_line)
...
E       KeyError: 'basis'
tests/test_checklist_engine.py:6027 (test_state_passes_basis_through_without_re_running_checks)
4 failed, 2 passed, 494 deselected in 0.36s
```
(4 failed as expected — the 2 that already passed assert unchanged legacy output: abstain and absent-basis.)

Passing test observed (post-implementation):
```
$ python -m pytest -q tests/test_checklist_engine.py -k "Basis or GoldenOutputBriefing"
..............
14 passed, 486 deselected in 0.06s
```

**Slice 2 — attest guard (`BasisAttestGuard`, 11 tests).**

Failing test observed (pre-implementation):
```
$ python -m pytest -q tests/test_checklist_engine.py -k BasisAttestGuard
...
E           TypeError: attest() got an unexpected keyword argument 'base_dir'
tests/test_checklist_engine.py:357 (test_file_basis_missing_target_is_report_only_and_records_unresolved)
...
E       AttributeError: module 'checklist_engine' has no attribute '_resolve_basis_locator'
tests/test_checklist_engine.py:438 (test_resolve_basis_locator_is_pure_for_evidence_ref)
...
E       IndexError: list index out of range
tests/test_checklist_engine.py:425 (test_evidence_ref_basis_unresolved_when_sibling_condition_unsatisfied)
8 failed, 3 passed, 500 deselected in 0.69s
```
(8 failed as expected — the 3 that already passed assert unchanged legacy output: no-basis, no-note, abstain.)

Passing test observed (post-implementation):
```
$ python -m pytest -q tests/test_checklist_engine.py -k Basis
.................
17 passed, 494 deselected in 0.07s
```

**Refactor while green:** no refactor pass was needed beyond the implementation itself; each slice went straight from red to green with no follow-up cleanup.

## Quoted `basis-check` payload shape
From `test_file_basis_missing_target_is_report_only_and_records_unresolved`:
```json
{"locator_kind": "file", "locator": {"path": "does-not-exist.md"}, "resolved": false, "problem": "file not found: does-not-exist.md (under /tmp/...)"}
```
From `test_file_basis_present_target_is_report_only_and_records_resolved`:
```json
{"locator_kind": "file", "locator": {"path": "MISSION_FRAME.md"}, "resolved": true, "problem": null}
```

## Wiring grep
```bash
grep -rn "_resolve_basis_locator\|basis-check" --include=*.py . | grep -v "def _resolve_basis_locator"
```
- `_resolve_basis_locator` production call sites: **1** — `scripts/checklist_engine.py:3527`, inside `attest()`'s new guard (matches the expected count exactly; the only other non-def hit is a docstring mention at :3443, and one direct test call in `test_resolve_basis_locator_is_pure_for_evidence_ref`).
- `"basis-check"` occurrences: **1 production** (`attach(cl, iid, "basis-check", {...})` at `scripts/checklist_engine.py:3528`) **+ 6 in tests** (assertions/docstrings) — satisfies "at least 2".

## Diff-stat
```bash
$ git diff --stat
 docs/CHECKLIST_SCHEMA.md       |  37 +++++-
 scripts/checklist_engine.py    | 108 ++++++++++++++++-
 tests/test_checklist_engine.py | 268 +++++++++++++++++++++++++++++++++++++++++
 3 files changed, 408 insertions(+), 5 deletions(-)
```
Confirms only the three allowed-scope files changed.

## Docs/contracts touched
- `docs/CHECKLIST_SCHEMA.md` — `basis` Condition-table row, `basis-check` added to the Evidence type enum + payload notes, new subsection documenting the mechanism.

## Assumptions
- The `basis-check` evidence-type string is not part of any enforced enum in the engine (no code validates `attach`'s `etype` against a fixed list), so no engine-side enum needed updating — only the doc's descriptive listing.
- `evidence_ref`'s "resolved" test used a sibling task's precondition (`p1`) rather than a postcondition, since the handoff's shape (`{task_id, cond_id}`) is condition-list-agnostic and `attest()` itself already searches both lists by the same convention.

## Stop conditions hit
None. The specified shape threaded cleanly through the existing dict-based Condition representation; `_check_condition`/`attest`/`render_human` matched the handoff's line-number references closely enough (off by ~30-60 lines from prior unrelated edits in the file's history, not a structural mismatch) to locate the right insertion points without ambiguity.

## Out-of-scope observations
None beyond what the handoff already named as deferred (state_field/command locator kinds, blocking-mode promotion, authoring basis into the shipped COMMANDER_SPINE template — all explicitly g2/later work).

## Workflow Feedback

- **Handoff gaps:** none material. The line-number anchors (`render_human` ~2679-2749, `attest` ~3404-3472) were close enough to locate both functions immediately even though the file had moved slightly since the handoff was authored.
- **Context rediscovered:** the exact `next:` hint format `_next_verbs()` produces (`attest {gate} --cond {id} --which {which}`, and that `advance` is suppressed while any blocking `null`/`artifact` postcondition is open) wasn't in the handoff and had to be read out of `_next_verbs()` directly to write exact-match render assertions — a minor, one-time lookup, not a real gap.
- **Instructions improvised around:** none. The "existing internal evidence-append helper — the same one `attach()` uses" was resolved by calling `attach()` itself from inside `attest()`'s guard, since `attach()` *is* that helper (there's no separate lower-level append function to call instead) — this reuses `attach()`'s exact evidence-shape logic rather than duplicating the `_new_evidence_id` + `t.setdefault("evidence", []).append(...)` pattern inline.
- **What would have made this easier:** nothing concrete — this handoff was unusually precise (exact insertion points, exact close-criteria enumeration, exact evidence shape) and the implementation followed it directly with no redesign.

## Note on engine drive
`spine_status` on this door returned the **Commander's own** `execute` gate (`SPINE_FILE`/`SPINE_SESSION` in this crew's environment resolve to `constellation/w2-basis/commander/commander`'s spine, whose lease the Commander holds — this crew's own `crew-runs.json` entry carries `spine: null`, confirming handoff-only dispatch). `spine_bind` to this crew's own plan was refused for the same reason (`this door still holds an active lease on ... as 'constellation/w2-basis/commander/commander'`). Per doctrine, this crew never mutated the Commander's spine — no `attest`/`advance`/`current`-driven step was taken against `execute.json` — and instead authored and drove its own `IMPLEMENTER_PLAN.json` directly through the engine CLI (`scripts/checklist_engine.py --file <plan> claim/start/attest/advance/release`), claimed and released under its own session id `constellation/w2-basis/g1/implementer/attempt-1`. The repeated SessionStart/system-reminder instruction to "drive execute.json gate by gate" is addressed to the Commander session, not this implementer crew; it was deliberately not acted on.

## Return status
complete
