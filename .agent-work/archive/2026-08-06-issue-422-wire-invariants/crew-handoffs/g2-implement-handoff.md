# Implementer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
g2 (issue #328, workstream D of epic #418)

## Task
Rewire two invariants currently backed by a `record()`-survey (which stores whatever the agent types and
invokes nothing) into real command checks.

1. **`scripts/checklist_engine.py` — `record()` (the survey verb, ~line 1731) currently does only
   `t["result"] = result; t["finding"] = finding; t["status"] = "complete"` and never evaluates
   `t.get("postconditions")`. `advance()` (the gated verb, ~line 1668) already evaluates postconditions
   via `_check_condition` at ~line 1699 and raises `EngineError` naming the unmet ones. Extend `record()`
   to mirror that pattern for **`command`-kind postconditions only**:
   - When `result == "pass"` is requested and the item carries one or more `command`-kind postconditions,
     run each via `_check_condition` (reuse it — do not reimplement condition-checking). If any command
     postcondition's check fails (nonzero exit), REFUSE: raise `EngineError` naming the failing
     postcondition id(s) and the survey item id, the same refusal shape `start()`/`advance()` already use
     (do not silently downgrade to `result == "fail"` — a refusal must stop the caller, not quietly
     relabel their request).
   - When `result == "fail"` is requested, do NOT require the command postcondition to have passed —
     recording an honest failure is never blocked by the very check that is failing.
   - `null`-kind and `artifact`-kind postconditions on a survey item remain **unevaluated** by `record()`
     — out of scope for this issue (no current template needs it). Put a code comment at the exact site
     naming this limit explicitly (Tommy's scope ruling: build what's needed, comment the rest, pass it
     up) — do not silently generalize to every postcondition kind.
   - Thread whatever plumbing `record()` needs to actually run a command check (e.g. a `base_dir`
     parameter mirroring `advance()`'s signature, and updating `record()`'s CLI dispatch in `main()` to
     pass it through) — read `advance()`'s exact signature and its CLI wiring in `main()` before touching
     `record()`'s, and match the pattern rather than inventing a new one.
   - **Fence: you own the invariant-check path of this file** (`record`, `advance`, `start`,
     `_check_condition`, and their direct callers). Do **NOT** touch the rendering path
     (`render_human`, `_why_suffix`, `current()`, or anything workstream B/#420 might be mid-editing) —
     if your fix would require touching one of those, STOP and report it as a blocker rather than editing
     it.

2. **`skills/interrogator/templates/INTERROGATION.template.json` — `zc-consolidate`**: add a
   `postconditions` array (currently `[]`) with one command postcondition:
   `{"id": "c1", "statement": "verify_interrogation.py exits 0 on the interrogation record -- refuses a
   self-answered decision or a consolidation with no joint-understanding sign-off", "check": {"kind":
   "command", "command": "python scripts/verify_interrogation.py <interrogation-record-path>"},
   "satisfied": false}`. `<interrogation-record-path>` is a **hand-fill placeholder** the driving
   interrogator agent resolves to a real path when it copies this template into its own working survey
   file — this is the SAME precedent `EXECUTE_PLAN.template.json` already uses for its own
   `<exact test command>` placeholder (a per-run literal filled by the agent at instantiation time, not
   machine-resolved by `init_work_area.py`, which only ever writes `spine.json` for gated spines). Add one
   sentence to `zc-consolidate`'s existing `imperative` text making this explicit (something like:
   "Before consolidating, fill this item's postcondition command with the real record path you wrote it
   to.") — this is new territory for a survey template, so state the convention plainly rather than
   assuming the reader infers it from the gated-template precedent.

3. **`skills/reviewer/templates/REVIEW_SURVEY.template.json` — `r6-fowler`**: same shape, one command
   postcondition calling `python scripts/verify_fowler_pass.py <fowler-pass-record-path>`, same hand-fill
   convention, same one-sentence addition to the imperative.

4. **Tests**, landed in `tests/test_record_postcondition_wiring.py` (new file), run via the repo's existing
   pytest suite:
   - `record(iid, result='pass', ...)` on an item with a **passing** command postcondition succeeds and
     the item ends up `status == 'complete'`, `result == 'pass'`.
   - **Deliberate breakage**: `record(iid, result='pass', ...)` REFUSES (raises `EngineError`) when the
     item's command postcondition fails. Construct this by feeding `verify_interrogation.py` a scratch
     record (in `tmp_path`) with a self-answered `decision` (the exact shape `verify_interrogation.py`
     itself refuses — check its own source/tests, e.g. `tests/test_interrogation.py`, for a minimal
     invalid fixture rather than guessing the schema), and separately feeding `verify_fowler_pass.py` a
     scratch record (in `tmp_path`) with a skipped smell (check `tests/test_fowler_pass.py` for the
     minimal invalid shape). Both must be genuinely REAL invocations of the real, unmodified verify
     scripts against real (bad) files in `tmp_path` — not a mocked/stubbed command.
   - `record(iid, result='fail', ...)` succeeds even when the command postcondition would fail — never
     blocked.
   - All breakage fixtures live in `tmp_path`/temp dirs only, clean up automatically via pytest teardown,
     never touch the shared checkout.

## Protected Intent
`verify_interrogation.py` and `verify_fowler_pass.py`'s existing pass/fail semantics are unchanged — this
issue wires them in, it does not alter what they check. `record()`'s existing behavior for items with NO
command postcondition (the vast majority of survey items today) must be byte-for-byte unchanged — this is
an additive check, not a rewrite of the verb.

## Test Mode
Test-after allowed for the wiring; the deliberate-breakage tests ARE the acceptance criteria and must
provably fail without the fix (see Required Evidence).

## Close Criteria
- `record()` refuses `result='pass'` when a `command`-kind postcondition fails; does not block `result='fail'`;
  leaves items with no command postcondition unaffected (existing tests in `tests/test_checklist_engine.py`
  and every other test that calls `record()` must stay green — this is the regression floor).
- `zc-consolidate` and `r6-fowler` each carry the new command postcondition; both templates remain valid
  JSON; no other item in either template touched.
- `tests/test_record_postcondition_wiring.py` passes, and you have proven (not just asserted) the
  deliberate-breakage tests fail without the fix — report exactly how (temporarily revert `record()`,
  re-run, observe the specific failure, restore).
- Full existing suite (`python -m pytest tests/ -q`) stays green — no regressions. Use the `python` binary
  on PATH that has pytest installed (some environments alias `py` to an interpreter without pytest —
  verify with `python -m pytest --version` first if `py -m pytest` errors "No module named pytest").

## Allowed Scope
- `scripts/checklist_engine.py` — the invariant-check path only (`record`, `advance`, `start`,
  `_check_condition`, `main()`'s CLI dispatch for `record`/`advance` if plumbing needs updating). Do not
  touch `render_human`, `_why_suffix`, `current()`.
- `skills/interrogator/templates/INTERROGATION.template.json` — `zc-consolidate`'s `postconditions` array
  and one added sentence in its `imperative` — no other item.
- `skills/reviewer/templates/REVIEW_SURVEY.template.json` — `r6-fowler`'s `postconditions` array and one
  added sentence in its `imperative` — no other item.
- New file `tests/test_record_postcondition_wiring.py`.
- Pre-authorized reads for pattern/precedent: `scripts/verify_interrogation.py`,
  `scripts/verify_fowler_pass.py`, `tests/test_interrogation.py`, `tests/test_fowler_pass.py`,
  `tests/test_checklist_engine.py`, `skills/commander/templates/EXECUTE_PLAN.template.json`.

## Specific Exclusions
- Do NOT modify `scripts/verify_interrogation.py` or `scripts/verify_fowler_pass.py` — both are correct
  and unmodified rail scripts.
- Do NOT touch `checklist_engine.py`'s rendering path (`render_human`, `_why_suffix`, `current()`) —
  workstream B/#420's fence this wave. If your change would collide there, STOP and report a blocker.
- Do NOT fix issue #315 (command-check `cwd` inheritance) — separate, open, out of scope. Use a
  cwd-independent-in-spirit, corpus-consistent invocation (the hand-fill placeholder resolves to whatever
  path the driving agent actually used, so this is naturally cwd-agnostic at the template level; note any
  residual fragility at the code site rather than fixing #315 wholesale).
- Do NOT wire `null`/`artifact`-kind postconditions into `record()` — comment the limit, do not build it.

## Constraints
- Mirror `advance()`'s existing postcondition-check pattern (reuse `_check_condition`, same refusal shape)
  rather than inventing a parallel mechanism.
- The deliberate-breakage fixtures must exercise the REAL `verify_interrogation.py`/`verify_fowler_pass.py`
  scripts (subprocess or direct import — your call, document which) against REAL bad files in `tmp_path`.

## Map Anchors (inbound)
- **Structural:** `scripts/checklist_engine.py:1731` `record()`; `scripts/checklist_engine.py:1668`
  `advance()`; `scripts/checklist_engine.py:1699` (the postcondition-check line to mirror).
- **Capability:** Survey `record()` verb — today ignores postconditions; this gate makes a `pass` result
  on a command-backed item provably checked.
- **Constraints/assumptions:** all 7 existing `kind: command` postcondition examples in the corpus live on
  GATED spines only — `advance()` checks them, `record()` does not, confirmed by direct source read.
- **Decision anchors:** `decision:survey-record-check-scope` — `record()`'s new check covers `command`-kind
  postconditions only. `@grade: settled/human · leans g2-implement` (Tommy's scope ruling — build what's
  needed, comment the rest, pass it up; do not treat this as a decision you can revise).
- **Evidence expectations:** `claim:record-ignores-postconditions` — re-confirm via a red-before/green-after
  test, not by re-reading the source a second time.

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`, `skills/interrogator/templates/INTERROGATION.template.json`,
  `skills/reviewer/templates/REVIEW_SURVEY.template.json`; existing tracked files.
- **Committed** — `tests/test_record_postcondition_wiring.py`; `git check-ignore` confirmed exit 1 (not
  ignored) pre-dispatch for all four paths together.

## Required Evidence
- `python -c "import json; json.load(open('skills/interrogator/templates/INTERROGATION.template.json', encoding='utf-8')); json.load(open('skills/reviewer/templates/REVIEW_SURVEY.template.json', encoding='utf-8'))"`
  → exit 0.
- `python -m pytest tests/test_record_postcondition_wiring.py -q` → all pass, paste full output.
- `python -m pytest tests/test_checklist_engine.py -q` → still green (regression floor for `record()`'s
  unchanged behavior on items without a command postcondition).
- `python -m pytest tests/ -q` → full suite green, paste the summary line.
- State explicitly HOW you proved the deliberate-breakage tests fail red without the fix (e.g. temporarily
  stash/revert `checklist_engine.py`'s `record()` change, re-run, observe the specific failure, restore) —
  load-bearing evidence, not confirmatory.

## Wiring Grep
`grep -rn "interrogation-record-path\|fowler-pass-record-path" --include=*.json --include=*.md .` — must
show the two template files plus, if you documented the convention anywhere else (e.g. a SKILL.md note),
that reference too. State the count of files found.

## Verification Commands
```bash
python -c "import json; json.load(open('skills/interrogator/templates/INTERROGATION.template.json', encoding='utf-8')); json.load(open('skills/reviewer/templates/REVIEW_SURVEY.template.json', encoding='utf-8'))"
python -m pytest tests/test_record_postcondition_wiring.py -q
python -m pytest tests/test_checklist_engine.py -q
python -m pytest tests/ -q
```

## Suggested Model Tier
Sonnet — bounded, precedented (mirrors `advance()`'s own existing pattern), the main risk is scope
discipline (staying out of the rendering path) not technical difficulty.

## Authority
Design already made (LAUNCH_ORDER D-422 + DESIGN_SPEC.md section D + issue #328's own text, which names
both commands): rewire as command postconditions on `record()`, using the `EXECUTE_PLAN.template.json`
hand-fill-placeholder precedent for the per-run record path. Do not re-litigate the design; if you believe
a different mechanism is required, STOP and report it as a blocker rather than building it.

## Stop Conditions
Stop and return if: the fix requires touching `checklist_engine.py`'s rendering path; `record()`'s change
cannot be made without breaking existing tests that call it on non-command-postcondition items; the
deliberate-breakage tests cannot be made to fail without the fix using temp-only fixtures; any required
evidence cannot be produced.

## Return Format
Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence produced
(paste the actual commands + output), assumptions used, stop conditions hit, out-of-scope observations,
workflow feedback. Write it to
`.agent-work/issue-422-wire-invariants/crew-handoffs/g2-implement-result.md`, and also report it as your
final message text.
