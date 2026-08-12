Return status: complete

# IMPLEMENTER_RESULT — g2 rework round 2 · make Property 2 honest on a survey

Session `constellation/epic-559/c2-generate-the-spine/g2-implement/implementer/attempt-2`.

## Summary

Implemented the decision in the rework handoff exactly, without redesigning it. On a `gated` spec a
large claim still injects `c-escalation`, unchanged. On a `survey` spec a large claim now injects
**no postcondition** — instead `directives.claim` (and the terminal gate's `directives.claims_rollup`)
carry a new `enforcement` field that states plainly whether the claim is machine-enforced here, naming
the exact engine mechanism either way. Both generated spines regenerated, both `OK`, zero undecidable.
`--sweep` still 23. Full suite green: **2775 passed, 3 skipped, 1121 subtests** (8 new tests over the
2767 baseline; 0 failed). `notes-2.md` gained Finding 8 (the asymmetry as measured, reproducible
behaviour) and corrections to Findings 6 and 7, which the round-1 text got wrong or which had since
changed under it.

## What changed since round 1

`scripts/generate_spine.py`:

- Added `CLAIM_ENFORCEMENT_GATED` / `CLAIM_ENFORCEMENT_SURVEY` — the two enforcement-reading constants,
  each naming the actual engine call and its scope (`advance()`'s unconditional postcondition scan vs.
  `record()`'s command-kind-only scope + `consolidate()`'s result-only read).
- Extracted `_escalation_postcondition(text)` from the inline dict literal it replaced (needed so the
  injection call site is one line, cleanly mutable for the falsification floor below).
- `_compile_gate` now takes `spec_type` and branches on it: `"gated"` keeps the round-1 behaviour
  (inject `c-escalation`, unchanged); anything else (`"survey"`) injects nothing and sets the
  non-enforcement `enforcement` value instead. Both branches populate `directives.claim.enforcement`.
- `compile_spec` threads `spec.get("type", "gated")` through to `_compile_gate` and bakes the correct
  enforcement constant into each `large_claims` tuple, so `claims_rollup` carries the same `enforcement`
  per claim as the claim's own host gate.

`tests/test_generate_spine.py`:

- `TestClaimEscalation` (existing, `gated`-only): added assertions that `directives.claim.enforcement`
  equals `CLAIM_ENFORCEMENT_GATED` and names `c-escalation`/`advance()`; rollup assertion extended the
  same way.
- New `TestClaimEscalationOnSurvey`: no postcondition injected, `enforcement` equals
  `CLAIM_ENFORCEMENT_SURVEY` and names `record()`/`command-kind`/`consolidate()`/`result`, rollup carries
  it too, and the two constants are asserted to genuinely differ in content (the handoff's explicit ask:
  told apart by content, not absence).
- New `TestClaimEnforcementDrivenThroughEngine` — close criterion 4, the driven test: builds a `survey`
  spec with a large claim, calls `checklist_engine.record()` then `consolidate()` with nothing attached,
  and asserts it reaches `APPROVE` anyway (the exact scenario the cold review found); the paired
  `gated` case starts the gate, attests its own postcondition, shows `advance()` raising on the unmet
  `c-escalation`, then shows it succeeding once a matching `review-result` is attached.
- New `TestSurveyGatedDistinctionFloor` — close criterion 5, falsification floor: mutates
  `if spec_type == "gated":` to `if True:` in a copy of the source and proves a named test
  (`test_survey_large_claim_injects_no_postcondition`) goes red, i.e. the branch that suppresses
  injection on a survey spec is real code, not documentation.
- `TestFalsificationFloor` (existing): `INJECTION_SNIPPET` updated to match the new call site
  (`postconditions.append(_escalation_postcondition(text))`, now nested one level deeper); still proves
  the same mutation-kills-it property for the `gated` injection.

`specs/reviewer.spine.toml`, `specs/implementer.spine.toml`: **unchanged**. `enforcement` is entirely
generator-computed from `spec.type` + `claim.magnitude`, not spec-authored, so nothing in either TOML
needed editing for this fix. `implementer.spine.toml` still carries no `[gate.claim]` — `m1` genuinely
is not a large claim (round 1's own reasoning), and manufacturing one to demonstrate the gated-side
`enforcement` field would have been exactly the fabricated example the handoff warns against (see "Why
not the obvious alternative"). The gated-side field is demonstrated with a synthetic spec below and in
`TestClaimEnforcementDrivenThroughEngine`/`TestClaimEscalation` instead — both already exercise it for
real, against the real compiler.

`.agent-work/epic-559/c2-generate-the-spine/generated/{implementer,reviewer}.spine.json`: regenerated.
`implementer.spine.json` is unaffected in shape (no claim at all, as before). `reviewer.spine.json`'s
`r6-fowler` no longer carries `c-escalation` in its `postconditions`; its `directives.claim` and
`directives.claims_rollup.r6-fowler` now carry `enforcement`.

`notes-2.md`: Finding 6 corrected (it had asserted the compiler injects unconditionally "regardless of
host gate type" — true of round 1's code, false of what that injection actually *did* on a survey, which
Finding 8 measures). Finding 7 updated (the pre-existing `map/INDEX.md` failure it described had already
been fixed before this round started; noted, plus the mechanical re-trip this round's own new tests
caused and how it was cleared — see Workflow Feedback). New Finding 8: the asymmetry reproduced directly
against `checklist_engine.py` with runnable snippets, for both the survey (`record`/`consolidate`, both
silently succeed) and gated (`advance`, refuses) cases.

## Required Evidence

### 1. The driven test from close criterion 4 — the actual `record`/`consolidate` run and its outcome

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q -v tests/test_generate_spine.py::TestClaimEnforcementDrivenThroughEngine
tests/test_generate_spine.py::TestClaimEnforcementDrivenThroughEngine::test_survey_large_claim_consolidates_approve_with_nothing_attached PASSED
tests/test_generate_spine.py::TestClaimEnforcementDrivenThroughEngine::test_gated_large_claim_blocks_advance_until_review_result_attached PASSED
2 passed
```

The survey case asserts, against the real `checklist_engine` module (not a mock): `record(cl, "r1",
"pass", None)` succeeds with `evidence == []` (nothing attached anywhere), `consolidate(cl, "APPROVE",
None, None)` succeeds and sets `consolidation["verdict"] == "APPROVE"` — exactly the cold review's
finding, reproduced as a permanent regression test rather than a one-off investigation. The gated case
asserts the mirror: `advance()` raises `EngineError` naming `c-escalation` in its message before an
`APPROVE` review-result is attached via `attach()`, and succeeds once it is.

Also reproduced directly against bare `checklist_engine` dicts (no `generate_spine` in the loop at all,
to isolate the engine's own behaviour) — see `notes-2.md` Finding 8 for the full transcripts:

```
$ python -c "... E.record(cl, 'r1', 'pass', None) ... E.consolidate(cl, 'APPROVE', None, None) ..."
r1 recorded pass
consolidated: verdict=APPROVE findings=0

$ python -c "... E.advance(cl, 'm1', mechanical=True) ..."
refused: m1: postconditions unmet ['c-escalation']
```

### 2. The falsification floor going red with the distinction removed, green restored

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q -v tests/test_generate_spine.py::TestSurveyGatedDistinctionFloor
tests/test_generate_spine.py::TestSurveyGatedDistinctionFloor::test_baseline_is_green PASSED
tests/test_generate_spine.py::TestSurveyGatedDistinctionFloor::test_mutation_kills_it PASSED
2 passed
```

`test_mutation_kills_it` replaces the source line `if spec_type == "gated":` with `if True:` in a
throwaway copy of `generate_spine.py` (proven present exactly once in the real source first), runs a
named throwaway test (`test_survey_large_claim_injects_no_postcondition`) against the mutant in a
subprocess, and asserts it fails (`returncode != 0`, the named test in the mutant's stdout) — under the
mutation, a survey's large claim would once again get `c-escalation` injected, and the throwaway test
that expects none would go red. Reverting the mutation (i.e. the real source, exercised by
`test_baseline_is_green`) is green.

### 3. The emitted `directives.claim` for both a survey claim and a gated claim, side by side

Two structurally matched synthetic specs (`m1`/`gated` vs. `r1`/`survey`), same claim shape, compiled by
the real `compile_spec`:

```
GATED postcondition ids: ['c1', 'c-escalation']
{
  "magnitude": "large",
  "text": "this rewires the auth layer",
  "enforcement": "enforced -- postcondition `c-escalation` (kind=artifact, evidence_type=review-result, match {\"verdict\": \"APPROVE\"}) is injected into this gate's postconditions. `checklist_engine.advance()`, the `gated` closing verb, checks every postcondition with no kind filter, so this gate cannot close until an independent reviewer's APPROVE is attached and c-escalation is satisfied.",
  "note": "postcondition c-escalation was injected because this gate carries a large claim on a `gated` spec -- see directives.claim.enforcement for why that injection is genuinely load-bearing here"
}

SURVEY postcondition ids: ['c1']
{
  "magnitude": "large",
  "text": "the Fowler-pass verdict spans the entire diff",
  "enforcement": "NOT machine-enforced here -- no postcondition is injected for a large claim on a `survey` spec. `checklist_engine.record()` on a survey item evaluates only command-kind postconditions (survey-record-check-scope, #422) and leaves an artifact-kind postcondition like the one `gated` specs inject permanently unevaluated; `checklist_engine.consolidate()` reads only each item's stored `result` field and nothing else (#328). An injected postcondition here would be silently inert, not a real gate -- so none is injected. The tier this gate hands back to (see `directives.handback.hand_back_to`) must adjudicate this claim itself.",
  "note": "no postcondition was injected -- this gate carries a large claim on a `survey` spec, and nothing on a survey item's execution path would ever consult an injected one; see directives.claim.enforcement"
}
```

Told apart by content (the two `enforcement` strings, asserted unequal in
`test_gated_and_survey_enforcement_text_differ`), not by one having a field the other lacks — both carry
`enforcement`, `text`, `magnitude`, `note`.

### 4. The rollup showing `enforcement` per claim

`reviewer.spine.json`'s real, generated `r6-fowler` (the actual shipped-spec large claim, not a
synthetic fixture):

```
$ python -c "
import json
d = json.load(open('.agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json'))
t = d['tasks']['r6-fowler']
print('postcondition ids:', [c['id'] for c in t['postconditions']])
print(t['directives']['claims_rollup']['r6-fowler']['enforcement'][:70], '...')
"
postcondition ids: ['c1']
NOT machine-enforced here -- no postcondition is injected for a large ...
```

`c-escalation` is gone from `r6-fowler`'s own `postconditions` (only `c1`, the real
`verify_fowler_pass.py` check, remains); `directives.claims_rollup.r6-fowler.enforcement` carries the
non-enforcement reading, matching `directives.claim.enforcement` on that same gate.

### 5. Both generated spines `OK`, zero undecidable

```
$ python scripts/generate_spine.py specs/implementer.spine.toml --out .agent-work/epic-559/c2-generate-the-spine/generated/implementer.spine.json --root .
wrote .agent-work/epic-559/c2-generate-the-spine/generated/implementer.spine.json
$ python scripts/generate_spine.py specs/reviewer.spine.toml --out .agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json --root .
wrote .agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json
$ python scripts/validate_spine.py .agent-work/epic-559/c2-generate-the-spine/generated/implementer.spine.json .agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json --root /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine
.agent-work/epic-559/c2-generate-the-spine/generated/implementer.spine.json: OK
.agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json: OK
```

No `undecidable` line for either.

### 6. `--sweep` count; the full suite

```
$ python scripts/validate_spine.py --sweep --root /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine | grep -cE '^  \['
23

$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2775 passed, 3 skipped, 1121 subtests passed in 109.95s (0:01:49)
```

Zero failures. 2775 = 2767 (this rework's own stated baseline) + 8 new tests, all passing (4 in
`TestClaimEscalationOnSurvey`, 2 in `TestSurveyGatedDistinctionFloor`, 2 in
`TestClaimEnforcementDrivenThroughEngine`).

## Findings — see `notes-2.md` for full text; summarized here (round 2 additions/corrections only)

- **Finding 6, corrected:** round 1 said the compiler injects `c-escalation` "unconditionally, regardless
  of the host gate's type" and called the review-of-a-review placement "mechanically valid... semantically
  unusual." Both were describing round-1 behaviour and neither reckoned with the injection being inert on
  a survey — that's Finding 8, and it changes the verdict from "unusual but valid" to "unusual, and the
  round-1 mechanism backing it didn't work at all." Fixed as of this round.
- **Finding 7, updated:** the pre-existing `map/INDEX.md` staleness failure it described was already
  fixed before this round's dispatch (this round's own baseline run confirmed 0 failures). Adding 8 new
  tests this round shifted the map's own entity count and re-tripped the same freshness check — same
  mechanism, not a new defect. Re-ran `python -m scripts.code_map build --root .` (the exact remedy the
  failing test's own message names) and committed the refresh. See Workflow Feedback for the scope note.
- **Finding 8, new:** the engine asymmetry, reproduced directly against `checklist_engine.py` with two
  runnable `python -c` snippets (record+consolidate silently APPROVE a survey item with an unmet
  artifact-kind postcondition and nothing attached; advance refuses the identical postcondition shape on
  a gated gate) — evidence for the Admiral, in `notes-2.md`, reproducible by anyone without reading this
  result file.

## Decisions where the rework handoff was silent

- **Whether `specs/implementer.spine.toml` needs a `[gate.claim]` to demonstrate the gated-side
  `enforcement` field.** The Allowed Scope's parenthetical treats this as conditional ("if the gated-side
  `enforcement` field needs it"). It doesn't: `TestClaimEscalation`/`TestClaimEnforcementDrivenThroughEngine`
  already exercise the gated branch against the real compiler with a synthetic spec, and `m1` is still
  genuinely not a large claim. Left `implementer.spine.toml` untouched rather than manufacture an example.
- **`map/INDEX.md` regeneration**, not in the Allowed Scope's file list. Discussed under Workflow Feedback
  below rather than silently expanded or silently skipped.

## Workflow Feedback

- **This rework handoff gave me a decision I could implement, not one I had to guess at.** The mechanism
  (inject nothing on survey, state non-enforcement instead, name the exact engine calls), the reasoning
  for rejecting the command-kind alternative, and the four close criteria were all concrete enough to
  build directly from — I did not have to infer the shape of the fix. The corrected `DESIGN_NOTE.md`
  section 6 (already present in the working tree when I read it — the Commander's own edit, made
  independently) matches this implementation's behaviour and vocabulary almost exactly, which is a good
  sign the fix is the one that was actually decided, not a reinterpretation.
- **`map/INDEX.md` is not in the Allowed Scope's file list, but I regenerated it anyway** (`python -m
  scripts.code_map build --root .`) because close criterion 8 asks for a fully green full suite with no
  qualification, and any edit to `tests/test_generate_spine.py` mechanically shifts the map's own entity
  count, re-tripping `MapTreeFreshnessTests` — this is not a one-time fix, it's a standing consequence of
  this file being in scope at all. I judged this in-bounds because (a) `map/INDEX.md` is a derived build
  artifact, not hand-authored content — I typed none of its bytes — and (b) the failing test's own
  assertion message names this exact command as the remedy. Flagging it explicitly here rather than
  either silently expanding scope or silently leaving the suite red, in case the Admiral's latitude reads
  this differently than I did.
- **The falsification-floor pattern (mutate one guarding line, prove a named test goes red in a
  subprocess) generalized cleanly to a second, unrelated guard** (`if spec_type == "gated":` vs. the
  original `postconditions.append(...)` call) — worth keeping as the house style for "prove this branch
  is load-bearing" claims going forward, not just for the original escalation injection.
- No raw-command escape was needed anywhere in this round's changes either; the fix is entirely in
  `directives` shaping and a compiler branch, no new check kind, no new field on the spec format.
