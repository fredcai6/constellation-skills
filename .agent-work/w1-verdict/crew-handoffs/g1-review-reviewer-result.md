# Review Result

## Assigned Gate
`g1-review` (work-id `w1-verdict`, epic 569, issue #371)

## Result
`APPROVE`

## Handoff compliance
The change does exactly what the handoff asked, within its allowed scope. Both `match`-comparison
sites (`_check_condition`'s artifact branch, `attest`'s artifact branch) now share one comparator
helper, `_artifact_match_satisfied`: a list-valued `match[k]` is membership (`have in want[k]`),
every scalar `match[k]` keeps `==` unchanged. A present-but-non-`dict` `match` is a clean refusal
at both sites (`satisfied=False` / `EngineError`) instead of the prior uncaught `AttributeError`.
`validate_spine.py` gained the blocking `shape-artifact-match-not-dict` shape fault and the
report-only `falsifiable-artifact-malformed-match-list` falsifiability fault, routed through a new
`ValidationResult.report_only` channel and `REPORT_ONLY_FAULT_CODES` set.
`docs/CHECKLIST_SCHEMA.md` gained one added clause on the `artifact` row.

## Scope drift
None. `git status --porcelain` / `git diff --name-only` confirm exactly the 5 allowed files touched
(`scripts/checklist_engine.py`, `scripts/validate_spine.py`, `docs/CHECKLIST_SCHEMA.md`,
`tests/test_checklist_engine.py`, `tests/test_validate_spine.py`) and nothing else. Grepped the diff
for every named exclusion (`APPROVE-WITH-FOLLOWUPS`/verdict vocabulary, `produced_by`/
`override_policy`) — zero matches. No `scripts/hooks/`, no new `verify_*.py`/`check_*.py` script, no
`skills/*/templates/*.json` or `.agent-work/templates/` edit.

## Evidence verdict
All 5 required evidence items independently reproduced, not just re-read from the implementer
result:
1. **Comparator red/green**: `_artifact_match_satisfied({"verdict": "APPROVE"}, {"verdict":
   ["APPROVE", "BLOCK"]})` → `True`; the miss case (`"PENDING"`) → `False`.
2. **Non-dict-match crash proof**: reproduced the pre-change `AttributeError: 'list' object has no
   attribute 'items'` by loading `checklist_engine.py` from base commit `244665ee` directly and
   calling `_check_condition` with a bare-list `match`; post-change the same call returns `False`
   cleanly, and the equivalent `attest` call raises `EngineError: evidence 'e-g1-1' match must be a
   dict, got list`.
3. **Backward-compat corpus proof**: `grep -rn '"match"' skills/*/templates/*.json` finds exactly
   the 2 sites the implementer named (`EXECUTE_PLAN.template.json:21,52`); all 4 hit/miss cases
   reproduce identically to the claimed table.
4. **`validate_spine` positive tests**: both standalone constructions reproduce exactly —
   `match: {"k": []}` → `report_only=[falsifiable-artifact-malformed-match-list]`,
   `bool(result)=False`; `match: ["a","b"]` → base `faults=[shape-artifact-match-not-dict]`,
   `bool(result)=True`. Read (not just grepped) both existing `validate()` callers
   (`generate_spine.py:1043`, `spine_lifecycle.py:396,454`) — both test only base-list truthiness.
5. **Full suite**: reproduced verbatim — `1 failed, 3592 passed, 6 skipped, 1261 subtests passed in
   144.08s`, same failing test named. Independently confirmed the failure is pre-existing (not this
   diff's own claim) by `git stash push` on exactly the 5 diff files (HEAD is already the named base
   commit `244665ee0f669a0bb23847c8fa695c430910c06d` — no commits on top), re-running
   `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
   alone, observing the same `AssertionError` (map staleness) with no diff-file changes present, then
   `git stash pop` to restore the working tree cleanly.

## Code/doc quality
Minimal, maintainable, matches surrounding conventions. The two call sites' near-duplicated match
logic is consolidated into one shared helper (`_artifact_match_satisfied`), which *removes*
pre-existing duplication rather than adding any. New comments (decision pointers, the promotion
trigger, the `bool`/`int` JSON-scalar note) explain non-obvious WHY, consistent with this repo's own
`# decision:<id>` convention (already present pre-diff in `scripts/gauge_reader.py`). Full Fowler
pass run (see below) found no smell to flag.

## Map impact verdict
- **Evidence supports claimed change:** yes — see Evidence verdict above; every structural anchor
  and capability claim was checked against the actual diff, not asserted.
- **Constraints not violated:** yes — `decision:backward-compatibility-is-non-negotiable` and
  `decision:widening-ships-live-refusal-ships-report-only` both independently verified (see below).
- **Notes match the diff:** yes — all named structural anchors (`_check_condition`, `attest`,
  `_artifact_match_satisfied`, `_shape_task_faults`, `_fault_artifact_malformed_match_list`,
  `ValidationResult`) are present at the claimed locations; no missing or overstated impact.
- **Decision candidates surfaced:** n/a — all 4 named decision anchors were already settled/admiral
  and implemented exactly as specified; no new authority gap arose.
- **Durable context routed:** yes — the pre-existing `map/INDEX.md` staleness
  (`test_code_map.py` freshness failure, `map/INDEX.md`/`map/ids.jsonl` DEGRADED-UNPARSEABLE) is
  correctly reported as an out-of-scope observation for Commander/Cartographer, not silently fixed
  and not auto-filed as an issue.

## Reconciliation check
No divergence from recorded architecture needing Commander reconciliation. Map is
DEGRADED-UNPARSEABLE at this commit (per the handoff's own Map Anchors note and independently
reproduced via the same pre-existing `test_code_map` freshness failure) — no live map entry point
exists to reconcile against; this does not block review, per the handoff.

### Constraint checks (appended per-rule, `r4a-backcompat` / `r4b-report-only-shipping`)
- `decision:backward-compatibility-is-non-negotiable`: **pass** — every existing scalar `match` in
  the shipped corpus resolves identically pre/post, verified both via direct helper calls and the
  full `attach`/`advance` engine path.
- `decision:widening-ships-live-refusal-ships-report-only`: **pass** — the comparator widening ships
  unconditionally live; the new `validate_spine` refusal is exclusively routed through
  `.report_only` and demonstrably cannot reach either existing caller's exit code; the promotion
  trigger is a verbatim, actionable code comment.

### Fowler refactoring pass (`r6-fowler`)
Recorded to `.agent-work/w1-verdict/FOWLER_PASS.json`; `verify_fowler_pass.py` exits 0
(`smells=12, flagged=[], overridden=[]`). All 12 baseline smells rendered `absent` — notably
`duplicated-code` went from present pre-diff (near-identical match logic at two call sites) to
absent post-diff, since consolidating that duplication is this change's own point.

## Blockers
- none

## Out-of-scope observations
- `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  fails at base commit `244665ee0f669a0bb23847c8fa695c430910c06d`, independently reproduced by this
  reviewer (not just re-verified from the implementer's claim) by stashing the diff and re-running
  the test in isolation against the unmodified base tree. Pre-existing, unrelated to this diff,
  already flagged by this gate's own Map Anchors as DEGRADED-UNPARSEABLE. Surfacing for
  Commander/Cartographer, consistent with discrepancy-handling doctrine (not auto-filed as an
  issue).

## Workflow Feedback

- **Handoff gaps:** none — the handoff was complete and precise: exact function names, exact line
  ranges, exact evidence commands, exact decision ids, exact stop conditions. Every claimed figure
  reproduced exactly as stated.
- **Context rediscovered:** none — the handoff's Map Anchors line numbers were accurate enough to
  navigate by directly; the implementer's result file supplied everything needed to plan
  independent reproduction without re-deriving it from scratch.
- **Instructions improvised around:** dispatched as a `run_crew.py` CLI crew but my environment
  carried only `SPINE_PARENT` (no `SPINE_FILE`/`SPINE_SESSION`) — `spine_status`/door tools were not
  usable. Per this skill's own instruction to author a survey only when nothing is bound, I built my
  own `REVIEW_SURVEY.json` at the handoff's named Survey State Location and drove it via the CLI
  (`checklist_engine.py --file ...`), matching the same shape the implementer's own result already
  documented for this run. I also made one recording slip — `record r6-fowler` was first submitted
  with a placeholder finding (`"test"`) before the Fowler pass artifact and rail check were actually
  in place to attach a real finding to; since `reopen` refuses on a `survey` checklist
  (`"REFUSED: reopen applies to gated checklists"`), I re-issued `record` on the same still-open
  item id with the correct finding, which the engine accepted cleanly (no `rework_count` increment,
  no evidence lost) — worth noting as a survey-vs-gated asymmetry in case a future reviewer hits the
  same `reopen` refusal and isn't sure re-`record`ing is the sanctioned recovery.
- **What would have made this easier:** same gap the implementer already reported — the crew
  dispatch mechanism could set `SPINE_FILE`/`SPINE_SESSION` even for the `cli` backend so a
  reviewer's door is bound to its own survey from the first call, matching what `crew-runs.json`
  already claims (`door_bound: true`).

## Return status
`complete`
