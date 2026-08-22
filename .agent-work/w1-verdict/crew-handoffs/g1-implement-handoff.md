# Implementer Handoff

## Gate
`g1-implement` (work-id `w1-verdict`, epic 569, issue #371)

## Task
Widen `scripts/checklist_engine.py`'s two `match`-comparison sites so a list-valued `match[k]`
means "any of these values satisfies me" (membership), while every existing scalar `match[k]`
keeps today's `==` behavior unchanged. Add a `scripts/validate_spine.py` guard against a
mistyped `match` shape: (a) a blocking **shape** fault when `match` is present but not a `dict`
(this currently crashes both comparator sites with an uncaught `AttributeError` — see Required
Evidence), and (b) a **report-only** fault when a `match[k]` list value is malformed (empty, or
containing a non-JSON-scalar element).

## Protected Intent
Every existing scalar `match` anywhere in the shipped corpus (`skills/*/templates/*.json`) must
keep meaning exactly what it means today — this is non-negotiable
(`decision:backward-compatibility-is-non-negotiable`). The widening must ship live (it adds no
wall to a comparison that is currently silently broken); the new `validate_spine` refusal must
ship **report-only** (never flips `validate_spine.py`'s exit code / `any_faults`), with its
promotion trigger stated as a code comment, per `decision:widening-ships-live-refusal-ships-report-only`.

## Test Mode
Test-after allowed — this is a small, mechanical, exhaustively-testable comparator change (no
UI/behavior ambiguity to explore via TDD); the required evidence below defines exactly what must
be proven, so writing the code then the proof is fine here.

## Close Criteria
- `_check_condition`'s artifact branch (`scripts/checklist_engine.py`, currently ~line 1080-1094)
  and `attest`'s artifact branch (currently ~line 3436-3440) both use ONE shared comparator
  helper (not duplicated inline logic) that: (1) treats a list-valued `match[k]` as membership
  (`have in want`), (2) keeps scalar `match[k]` as `==` unchanged, (3) treats a present-but-non-`dict`
  `match` as a clean refusal (no `AttributeError`) — `EngineError` at the `attest` site, `satisfied
  = False` at the `_check_condition` site.
- `scripts/validate_spine.py` gains:
  - A new **shape**-family fault (blocking, alongside the existing shape faults in `_shape_faults`
    or the per-condition shape-checking path — your call which existing function family it slots
    into, as long as it fires for the same conditions `_shape_faults`/`_shape_task_faults` already
    walk) for `check.kind == "artifact"` with a `match` present but not a `dict`.
  - A new **falsifiable**-family fault (report-only — see below), sibling to
    `_fault_artifact_no_match` (~line 456), for a `match[k]` list value that is empty or contains
    a non-scalar element (not `str`/`int`/`float`/`bool`/`None`). A single-element list is NOT
    flagged.
  - `ValidationResult` gains a third channel, `report_only: list[Fault]`, parallel to the existing
    `undecidable` channel — constructed with a safe default (`report_only=()`) so
    `ValidationResult(faults, undecidable)` (both existing 2-arg call sites in `validate()`) keeps
    working unchanged. `validate()` computes the new falsifiable-family fault same as any other,
    then routes it into `report_only` instead of the base list (which is what makes it non-blocking
    — both `generate_spine.py` and `spine_lifecycle.py` check `if result:`/`if result.undecidable or
    result:` truthiness of the base list only, so anything living in `.report_only` cannot flip
    their exit code — verify this by reading both call sites, do not just assert it). `main()`'s CLI
    prints `.report_only` findings distinctly (e.g. a `[REPORT-ONLY]`-prefixed line) without
    changing `any_faults`/the exit code.
  - A `REPORT_ONLY_FAULT_CODES` module-level set naming the new falsifiable fault's code, with a
    code comment stating the promotion trigger verbatim: promote to blocking when (a)
    `validate_spine.py --sweep` reports zero occurrences across the shipped corpus AND (b) the
    Admiral/human ratifies `decision:widening-ships-live-refusal-ships-report-only` at the wave-2
    checkpoint that decision already names — then remove the fault's code from this set.
- `docs/CHECKLIST_SCHEMA.md`'s "What 'engine-checked' means" table row for `artifact` (currently
  line 233) gets one added clause describing the list-valued-match membership semantics — do not
  rewrite the row, add to it.
- Full local `pytest -q` passes (green at base commit: 3564 passed, 6 skipped — a changed count is
  expected and fine as long as it is all NEW passing tests, never fewer passing than before).
- Every existing scalar `match` in the shipped corpus resolves identically — see Required Evidence.

## Allowed Scope
- `scripts/checklist_engine.py` — the two named comparator sites, plus the new shared helper
  function.
- `scripts/validate_spine.py` — the two new faults, the `ValidationResult.report_only` channel,
  `REPORT_ONLY_FAULT_CODES`, `main()`'s report-only print.
- `docs/CHECKLIST_SCHEMA.md` — the one-clause addition to the `artifact` row.
- `tests/test_checklist_engine.py` and `tests/test_validate_spine.py` — new tests for this
  behavior are pre-authorized (per commander-core doctrine: pre-authorize the test files that
  already exercise the gated behavior). Do not touch any other test file.

## Specific Exclusions
- Do NOT touch `scripts/hooks/` (out of mission).
- Do NOT touch `waive()`'s `produced_by`/`override_policy.authority` gaps (#557, wave 2 — leave
  exactly as-is even if you notice them in passing).
- Do NOT add or wire a new `scripts/verify_*.py`/`scripts/check_*.py` script — that is the sibling
  `w1-wiring` commander's fenced territory this wave (`../569-w1-wiring`). If your work seems to
  want one, stop and say so in your result instead.
- Do NOT reintroduce `APPROVE-WITH-FOLLOWUPS` or any verdict-vocabulary change.
- Do NOT edit any file under `skills/*/templates/*.json` or `.agent-work/templates/` — no shipped
  template's `match` value needs to change; this gate is comparator-only.
- Do NOT make the new `validate_spine` refusal blocking, and do NOT wire `validate_spine.py` into
  any new call site (e.g. execute.json authoring) — both are floats to the Admiral, not this gate's
  decision.

## Constraints
- Every existing scalar `match` anywhere in the shipped corpus must keep behaving identically —
  see Required Evidence for the exact corpus inventory to re-run.
- The shared comparator helper is a plain, pure function: `have == want` unless `want` is a
  `list`, in which case `have in want`. No third shape (no `{"any_of": [...]}` or similar
  operator dict) — that alternative was compared and rejected in `PLAN_ALTERNATIVES.md`.
- `EngineError` (imported/used already in `checklist_engine.py`) is the right exception type at
  the `attest` site for a malformed (non-dict) `match` — match the existing style of the sibling
  `raise EngineError(f"evidence {evidence_id!r} does not match required {want_match}")` line right
  below it.

## Map Anchors (inbound)
map/INDEX.md and map/ids.jsonl are DEGRADED-UNPARSEABLE at this commit (packet dirs referenced but
absent on disk) — there is no map entry point to hand down. Anchors below are source-line pointers
from `.agent-work/w1-verdict/MISSION_FRAME.md`.
- **Structural:**
  - `scripts/checklist_engine.py:_check_condition` — artifact branch, currently line ~1080-1094
  - `scripts/checklist_engine.py:attest` — artifact branch, currently line ~3436-3440
  - `scripts/validate_spine.py:_fault_artifact_no_match` — currently line ~456, sibling to extend
    the fault family beside
  - `scripts/validate_spine.py:ValidationResult` — currently line ~535
- **Capability:** engine `artifact`-postcondition match comparison; `validate_spine`'s
  falsifiability fault family
- **Constraints/assumptions:** `decision:backward-compatibility-is-non-negotiable`,
  `decision:widening-ships-live-refusal-ships-report-only`
- **Decision anchors:**
  - `decision:match-shape-bare-list` — list-valued `match[k]` means membership; every other shape
    keeps scalar `==` unchanged.
    `@grade: settled/admiral · leans g1-implement,g1-review`
  - `decision:match-not-dict-is-shape-fault` — a present-but-non-`dict` match is a blocking shape
    fault, not the new report-only family.
    `@grade: settled/admiral · leans g1-implement,g1-review`
  - `decision:malformed-list-definition` — malformed (report-only) means empty or non-scalar
    element; single-element list is NOT flagged.
    `@grade: settled/admiral · leans g1-implement,g1-review`
  - `decision:promotion-trigger` — see Close Criteria's `REPORT_ONLY_FAULT_CODES` comment text.
    `@grade: settled/admiral · leans g1-implement,g1-review`
- **Evidence expectations:** the red-proof (below, already run against base commit
  `244665ee0f669a0bb23847c8fa695c430910c06d`) and the corpus backward-compat inventory (below).
- **Map confidence flags:** none beyond the DEGRADED map noted above.

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`; `git check-ignore scripts/checklist_engine.py`
  exited 1 (not ignored).
- **Committed** — `scripts/validate_spine.py`; `git check-ignore scripts/validate_spine.py`
  exited 1 (not ignored).
- **Committed** — `docs/CHECKLIST_SCHEMA.md`; `git check-ignore docs/CHECKLIST_SCHEMA.md` exited 1
  (not ignored).
- **Committed** — any new/changed test file under `tests/`; same check applies, not ignored by
  default in this repo.

## Required Evidence
1. **Red-proof (already run by the Commander, reproduce it yourself before changing code, then
   again after):**
   ```
   python3 - <<'EOF'
   import sys
   sys.path.insert(0, "scripts")
   import checklist_engine as ce
   cond = {"id": "c1", "statement": "x", "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": ["APPROVE", "BLOCK"]}}, "satisfied": False}
   t = {"id": "g1-review", "evidence": [{"id": "e1", "type": "review-result", "payload": {"verdict": "APPROVE"}, "produced_by": "reviewer", "ts": ""}]}
   print(ce._check_condition(cond, t))
   EOF
   ```
   Before your change: prints `False` (confirmed by the Commander at commit
   `244665ee0f669a0bb23847c8fa695c430910c06d`). After your change: must print `True`.
2. **Non-dict-match crash proof, before and after:**
   ```
   python3 -c "
   import sys; sys.path.insert(0, 'scripts')
   import checklist_engine as ce
   cond = {'id':'c1','statement':'x','check':{'kind':'artifact','evidence_type':'review-result','match':['APPROVE','BLOCK']},'satisfied':False}
   t = {'id':'g1-review','evidence':[{'id':'e1','type':'review-result','payload':{'verdict':'APPROVE'},'produced_by':'reviewer','ts':''}]}
   print(ce._check_condition(cond, t))
   "
   ```
   Before your change: raises `AttributeError: 'list' object has no attribute 'items'`. After:
   must return `False` cleanly, no traceback.
3. **Backward-compat corpus proof.** Re-run `grep -rn '"match"' skills/*/templates/*.json` (2
   hits: `EXECUTE_PLAN.template.json:21` `{"status": "complete"}`,
   `EXECUTE_PLAN.template.json:52` `{"verdict": "APPROVE"}`) and show, for each, that your new
   comparator still returns the exact same boolean it did before your change for both a matching
   and a non-matching payload (4 total cases: 2 matches x true/false). Do this either as a targeted
   pytest or as an inline verification script; state which and paste the output.
4. **validate_spine proof.** Show `python3 scripts/validate_spine.py --sweep` output before and
   after your change (should be unaffected — no shipped template triggers either new fault), plus
   a standalone positive test: construct a minimal spine dict with an artifact check whose `match`
   is `{"k": []}` (empty list) and confirm `validate()`'s `.report_only` is non-empty while the
   base list (and therefore `bool(result)`/exit code) is unaffected; and another with `match:
   ["a","b"]` (non-dict) and confirm it lands in the BASE (blocking) list.
5. **Full suite.** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q` —
   paste the final summary line. Any failure outside your own new/changed tests is a stop
   condition, not something to work around.
6. Commit SHA your final red/green proof pair ran against — state it explicitly; it must be the
   commit you are handing back (not an earlier intermediate one you iterated through).

## Wiring Grep
```
grep -rn "<your new shared comparator helper's name>" scripts/checklist_engine.py | grep -v "^scripts/checklist_engine.py:<its own def line>"
grep -rn "<your new validate_spine fault function names>" scripts/validate_spine.py
```
State the count of call sites found outside each function's own definition for every new symbol
you add. Zero external call sites for a new helper actually wired into both comparator sites
would be wrong — expect 2 call sites for the shared comparator helper (one per site).

## Verification Commands
```bash
cd /home/tommy/projects/569-w1-verdict
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q
python3 scripts/validate_spine.py --sweep --root .
```

## Suggested Model Tier
simple bounded — the change is fully specified (exact code, exact shapes, exact test evidence);
no open design question remains once this handoff is filled.

## Authority
The match shape (bare list = membership), the shared-helper factoring, the non-dict-match shape
fault, the malformed-list definition, and the promotion-trigger text are all decided already (see
Map Anchors above) — do not re-derive or re-litigate any of them. Widening-live/refusal-report-only
is a pre-ruling (`decision:widening-ships-live-refusal-ships-report-only`), also not yours to
revisit.

## Stop Conditions
Stop and return if: the shared-helper factoring turns out to require touching a third call site not
named above, the non-dict-match guard cannot be added without a larger refactor than one
`isinstance` check per site, or any existing test's CURRENT PASS depends on a non-dict match/list
match behaving as it does today (i.e., a test that currently expects the crash, or expects a
list-valued match to be silently unsatisfiable) — none is expected to exist (checked: no test in
the corpus constructs a list-valued or non-dict `match`), but if you find one, stop rather than
break it silently.

## Return Format
Return `IMPLEMENTER_RESULT` per the standard contract to
`.agent-work/w1-verdict/crew-handoffs/g1-implement-implementer-result.md` before ending your turn.
