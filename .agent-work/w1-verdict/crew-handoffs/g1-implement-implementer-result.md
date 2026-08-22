# Implementation Result

## Assigned gate
`g1-implement` (work-id `w1-verdict`, epic 569, issue #371)

## Completed slice
Widened the artifact-check comparator (`checklist_engine.py`'s `_check_condition` artifact
branch and `attest` artifact branch) so a list-valued `match[k]` means membership (`have in
want[k]`), while every scalar `match[k]` keeps `==` unchanged, via one shared helper
(`_artifact_match_satisfied`). Both sites now guard a present-but-non-`dict` `match` as a clean
refusal instead of the prior uncaught `AttributeError` (`satisfied = False` at `_check_condition`,
`EngineError` at `attest`). `validate_spine.py` gained a blocking shape fault for that same
non-dict-match shape, plus a report-only falsifiable fault (`_fault_artifact_malformed_match_list`)
for an empty or non-scalar-element list value, routed through a new `ValidationResult.report_only`
channel and `REPORT_ONLY_FAULT_CODES` so it can never flip the exit code. `docs/CHECKLIST_SCHEMA.md`
gained one clause on the `artifact` row.

## Scope
**Files changed:**
- `scripts/checklist_engine.py`
- `scripts/validate_spine.py`
- `docs/CHECKLIST_SCHEMA.md`
- `tests/test_checklist_engine.py`
- `tests/test_validate_spine.py`

**Specific exclusions touched:** no — `scripts/hooks/`, `waive()`'s `produced_by`/
`override_policy.authority` gaps, any new `verify_*.py`/`check_*.py` script,
`APPROVE-WITH-FOLLOWUPS`/verdict vocabulary, and `skills/*/templates/*.json`/`.agent-work/templates/`
were all left untouched.

## Behavior changed
Yes. `artifact` checks now accept a list-valued `match[k]` as membership (previously any
non-scalar `match[k]` either silently failed to satisfy or crashed with `AttributeError` on a
non-dict `match`). Every existing scalar `match` in the shipped corpus resolves identically (see
Evidence). The new `validate_spine` faults are new, additive diagnostics; one is blocking (non-dict
`match` shape), one is report-only (malformed list value) and cannot affect any caller's exit code.

## Map Impact
- **Structural anchors touched:** `scripts/checklist_engine.py:_check_condition` (artifact branch,
  now ~1080-1112, delegates to new `_artifact_match_satisfied` at ~1036) — `scripts/checklist_engine.py:attest`
  (artifact branch, now ~3450-3463, same helper) — `scripts/validate_spine.py:_shape_task_faults`
  (new inline non-dict-match check) — `scripts/validate_spine.py:_fault_artifact_malformed_match_list`
  (new, sibling to `_fault_artifact_no_match`) — `scripts/validate_spine.py:ValidationResult` (new
  `.report_only` channel) — `scripts/validate_spine.py:REPORT_ONLY_FAULT_CODES` (new module-level set).
- **Capabilities added/changed/affected:** engine `artifact`-postcondition match comparison now
  supports list-valued membership; `validate_spine`'s falsifiability fault family gained a
  report-only member and its own non-blocking channel.
- **Constraints/assumptions touched:** `decision:backward-compatibility-is-non-negotiable` (honored
  — see corpus proof below), `decision:widening-ships-live-refusal-ships-report-only` (honored —
  widening is live, `validate_spine` refusal is report-only and never wired into a new call site).
- **Decision anchors resolved (already settled, implemented as specified):**
  `decision:match-shape-bare-list`, `decision:match-not-dict-is-shape-fault`,
  `decision:malformed-list-definition`, `decision:promotion-trigger` (comment text lives verbatim at
  `scripts/validate_spine.py` above `REPORT_ONLY_FAULT_CODES`).
- **Claims/evidence produced:** see Evidence section below — red/green comparator proof, corpus
  backward-compat proof, validate_spine positive-test proof, full suite.
- **Trust limitations / drift found:** `map/INDEX.md`/`map/ids.jsonl` were already flagged
  DEGRADED-UNPARSEABLE in this gate's Map Anchors; separately, `tests/test_code_map.py`'s map
  freshness test fails identically at the base commit (pre-existing, unrelated to this diff — see
  Out-of-scope observations).
- **Triage candidates:** none raised by this gate's own work; the map-freshness pre-existing
  failure is noted below for Commander/Cartographer, not filed as an issue per discrepancy-handling
  doctrine.

## Test mode
**Required:** test-after
**Satisfied:** yes — code written first per the exact specified shapes, then the required evidence
(red/green proofs, corpus proof, standalone positive tests, full suite) reproduced and pasted below.

## Evidence

### 1. Red-proof (list-valued match membership)
Before:
```
False
```
After:
```
True
```

### 2. Non-dict-match crash proof
Before:
```
AttributeError: 'list' object has no attribute 'items'
  (checklist_engine.py:1088, ev.get("payload", {}).get(k) == v for k, v in want.items())
```
After (`_check_condition`):
```
False
```
After (`attest`, via a minimal in-process check):
```
EngineError: evidence 'e1' match must be a dict, got list
```

### 3. Backward-compat corpus proof (inline verification script, 4 cases)
```
grep -rn '"match"' skills/*/templates/*.json
skills/commander/templates/EXECUTE_PLAN.template.json:21:...match": {"status": "complete"}...
skills/commander/templates/EXECUTE_PLAN.template.json:52:...match": {"verdict": "APPROVE"}...
```
```
EXECUTE_PLAN.template.json:21 match={'status': 'complete'} payload={'status': 'complete'} -> True (expected True) [OK]
EXECUTE_PLAN.template.json:21 match={'status': 'complete'} payload={'status': 'partial'} -> False (expected False) [OK]
EXECUTE_PLAN.template.json:52 match={'verdict': 'APPROVE'} payload={'verdict': 'APPROVE'} -> True (expected True) [OK]
EXECUTE_PLAN.template.json:52 match={'verdict': 'APPROVE'} payload={'verdict': 'BLOCK'} -> False (expected False) [OK]
```

### 4. validate_spine proof
`--sweep` before and after are byte-identical (`diff /tmp/sweep_before.txt /tmp/sweep_after.txt` —
no output, both exit code 1 from the same pre-existing corpus faults, unrelated to this change).

Standalone positive tests:
```
match: {"k": []}   -> base faults=[], report_only=[falsifiable-artifact-malformed-match-list], bool(result)=False
match: ["a", "b"]  -> base faults=[shape-artifact-match-not-dict], report_only=[], bool(result)=True
```
Read (not just asserted) `generate_spine.py:1043` (`if result:`) and `spine_lifecycle.py:396,454`
(`if result.undecidable or result:`): both test only `ValidationResult`'s base-list truthiness, so
`.report_only` content can never reach either code path.

### 5. Full suite
```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q
```
```
1 failed, 3592 passed, 6 skipped, 1261 subtests passed in 143.99s
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```
That one failure is **pre-existing at the base commit** (verified via `git stash` + re-running the
same test against `244665ee0f669a0bb23847c8fa695c430910c06d` unmodified — it fails identically
there, with a different entity-count diff but the same assertion). Deselecting only that test:
```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q --deselect tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```
```
3592 passed, 6 skipped, 1 deselected, 1261 subtests passed in 140.83s
```
3592 passed vs. base 3564 passed — all new tests, zero fewer passing than before. 6 skipped matches
base exactly.

**Result:** pass (all evidence above), with the one out-of-scope pre-existing failure noted, not
worked around in the shipped code.

## Docs/contracts touched
- `docs/CHECKLIST_SCHEMA.md` — one clause added to the `artifact` row (line 233), row not rewritten.

## Assumptions
- The map-freshness pytest failure (`test_code_map.py`) is environmental/pre-existing and out of
  this gate's scope (map regeneration is not named in Allowed Scope); confirmed via base-commit
  reproduction rather than assumed.

## Stop conditions hit
- None. The shared-helper factoring needed only the two named call sites; the non-dict-match guard
  was a one-`isinstance`-check addition at each site; no existing test depended on the old crash or
  on a list-valued match being silently unsatisfiable.

## Out-of-scope observations
- `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  fails at the base commit `244665ee0f669a0bb23847c8fa695c430910c06d` before any change in this
  gate — `map/INDEX.md` is stale against a fresh `code_map` build. This is consistent with this
  gate's own Map Anchors, which already flag `map/INDEX.md`/`map/ids.jsonl` as
  DEGRADED-UNPARSEABLE at this commit. Surfacing for Commander/Cartographer rather than fixing
  (out of Allowed Scope) or filing as an issue (a discrepancy, not something to auto-file).

## Workflow Feedback

- **Handoff gaps:** none — the handoff was unusually complete (exact shapes, exact evidence,
  exact stop conditions). One friction point: Required Evidence #5's full-suite command, run
  verbatim, hits a pre-existing, unrelated failure (`test_code_map.py` map staleness) that the
  handoff's stated base-commit baseline ("green at base commit: 3564 passed, 6 skipped") did not
  anticipate — my own measurement at that exact commit shows the same test already red there, so
  the "green at base" claim and my observation disagree. I resolved it by reproducing the failure
  at base (ruling out a regression), then reporting the true delta with the one known failure
  deselected, rather than treating the mismatch as license to declare success unverified.
- **Context rediscovered:** none beyond ordinary source reading — the handoff's Map Anchors line
  numbers (~1080-1094, ~3436-3440) were close enough to navigate by directly.
- **Instructions improvised around:** I was dispatched as a `run_crew.py` CLI crew but my
  environment carried only `SPINE_PARENT` (no `SPINE_FILE`/`SPINE_SESSION`) — no spine was bound to
  my door (`spine_status` refused: "no spine is bound to this door"). Per this skill's own
  instruction to author a plan only when nothing is bound, I built my own `IMPLEMENTER_PLAN.json`
  in my crew-scratch dir and drove it through the CLI (`checklist_engine.py --file ...`) rather than
  the MCP door, exactly as this shape was previously observed and documented (567-d1 g4). I also hit
  one pre-existing test failure unrelated to my diff (see above) and used `amend --op retext-check`
  (self-authority `implementer`, reasoned in the amendment record) to correct my own plan's full-suite
  check to deselect it, rather than leaving a command check that would perpetually and misleadingly
  fail my own internal plan.
- **What would have made this easier:** the crew dispatch mechanism could set `SPINE_FILE`/
  `SPINE_SESSION` even for the `cli` backend so an implementer's door is bound to its own plan from
  the first call, matching what `crew-runs.json` already records (`door_bound: true`) — right now
  that field claims true while the actual environment carries none of the three spine variables a
  bound door needs.

## Return status
`complete`
