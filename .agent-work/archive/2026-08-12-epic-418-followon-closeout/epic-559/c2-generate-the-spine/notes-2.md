# g2 notes — generated-vs-shipped disagreements and other findings

Every disagreement between a generated spine and its shipped template, plus everything else
worth recording that the handoff or DESIGN_NOTE.md left silent. `decision:no-template-edited-to-pass`
governs every item below where the generated spine and the shipped template diverge: the shipped
template was read, never edited.

## Finding 1 — a `gated` role spec cannot reproduce the shipped `m0-context`'s pure-qualitative shape

`IMPLEMENTER_PLAN.template.json`'s `m0-context` ships one postcondition, `check: null` — pure
"Attest c1," nothing mechanical behind it. The new format's `spec_shape_faults` refuses that
outright: `spec-all-qualitative-postconditions` fires on any `gated` gate whose postconditions are
**all** `qualitative` (DESIGN_NOTE.md section 4's "`falsifiable-all-null` gate refused at compile
time"). I could not author the shipped shape byte-for-byte; the format itself forecloses it.

**Resolution (DESIGN_NOTE.md is silent here, so this is my call):** `specs/implementer.spine.toml`'s
`m0-context` keeps the qualitative claim (`c1`, "handoff loaded and complete" — still fundamentally
unverifiable by any machine) and adds two `population` postconditions (`c2`, `c3`) that check the two
doctrine files this gate's own imperative names actually exist on disk:

```
cd <repo-root> && test $(python -c '...glob...' skills/_shared global-crew.md) -eq 1
cd <repo-root> && test $(python -c '...glob...' skills/_shared global-everyone.md) -eq 1
```

This is a **partial** proxy, stated plainly: it proves the files exist to be read, not that they were
read or understood. That is exactly DESIGN_NOTE.md section 10's own honesty about defect 3 — "the
defect shrinks; it does not vanish" — one layer further out.

## Finding 2 — DESIGN_NOTE.md's own claim about `r0-context` does not match the measured oracle

DESIGN_NOTE.md section (Close Criterion 4 of this gate's handoff) states: *"The shipped `m0-context`
and `r0-context` gates [carry `falsifiable-all-null`] (they are two of the 23 baseline faults)."*
Measured:

```
$ python scripts/validate_spine.py --sweep --root . | grep -A2 REVIEW_SURVEY
.../skills/reviewer/templates/REVIEW_SURVEY.template.json: OK
```

`REVIEW_SURVEY.template.json` is clean — `r0-context` carries **no** fault today. Reading
`validate_spine.py::_fault_all_null`, the reason is structural, not a stale template: `_fault_all_null`
returns `[]` unconditionally when `spine_type != GATED`. `r0-context` is a `survey` item with
`"postconditions": []` (empty, not `[{"check": null}]`), so the all-null walk never even reaches it —
survey items are exempted from this fault by the oracle's own type check, and an *empty* postcondition
list is not "all null," it is zero conditions. Only `m0-context` (a `gated` task) is actually one of the
23 baseline faults; `r0-context` is not, and never was under the shipped oracle. I am recording this as
a finding rather than silently fixing the design note's prose (out of scope: I do not own DESIGN_NOTE.md).

Given this, I still added a qualitative postcondition to `r0-context` in the generated reviewer spec
(see Required Evidence #4 in the result) — not because the shipped file needed one to pass, but because
the handoff explicitly asks to "paste the emitted statement so the stated form is visible" for this gate,
and a survey item with `postconditions: []` has no statement to emit at all. Demonstrating the
`qualitative`+`because` form on a **survey** gate (not just the **gated** `m0-context`) is what actually
answers that ask.

## Finding 3 — `config_ref: "docs/agents/engine-config.json"` points at a file that does not exist

Both shipped templates (and both role specs, matching that intent) declare
`config_ref = "docs/agents/engine-config.json"`. That path does not exist anywhere in this repo:

```
$ ls docs/agents/
CREW_CONTEXT.md  GLOSSARY.md  ORCHESTRATOR_CONTEXT.md
```

Neither the generator nor the oracle flags this. `generate_spine.spec_shape_faults`'s
`spec-config-ref-not-json` check (DESIGN_NOTE.md section 7) is explicitly guarded
`if cfg_path.exists():` — a **missing** `config_ref` is silently accepted; only an **existing,
non-JSON** one is refused. This is a narrower gap than the one DESIGN_NOTE.md section 7 already names
(a `config_ref` that exists but is not JSON crashes `checklist_engine.load_config` with an unhandled
`JSONDecodeError`) — a config_ref that never resolves at all is a third, distinct case, currently
unchecked by either layer. Not fixed (`validate_spine.py` is off-limits, and this predates both role
specs — the shipped templates carry the identical gap). Recorded per the handoff's "the gap in the
oracle is a finding for the return report, not a change to the oracle."

## Finding 4 — the `script` kind's probe does not check positional arguments at all

`r6-fowler`'s postcondition compiles `scripts/verify_fowler_pass.py` against one positional argument
(`.agent-work/<work-id>/FOWLER_PASS.json`). The `script` probe (DESIGN_NOTE.md section 4,
`generate_spine._probe_script`) only validates tokens in `args` that start with `--` against
`add_argument` literals; a **positional** argument is never inspected — `flags = [a for a in args if
a.startswith("--")]`, and an `args` list with no `--` items returns `([], [])`, "nothing to check,
accepted," before any AST walk runs. So had I typed the wrong record path shape entirely (say, the
record's parent directory instead of the file, or a stray extra positional), the probe would not have
caught it — only `probe-script-not-found` (a missing script path) fires. This is the honest edge of
DESIGN_NOTE.md section 10's row for defect 3: "a wrong flag is caught loudly at generation time" is
true; a wrong **positional value** is not caught at all, by design (section 4's own wording scopes the
probe to "the FIRST positional argument to a call named `add_argument`," which finds what flags exist,
not what a positional means). I did not work around this with a raw command — I read
`scripts/verify_fowler_pass.py`'s own `parser.add_argument("record", ...)` line directly to confirm the
positional's role before writing the arg, rather than trusting the probe to have caught a mistake here.

## Finding 5 — `r6-fowler`'s script check embeds `<work-id>` quoted; the shipped template does not

Shipped: `"python scripts/verify_fowler_pass.py .agent-work/<work-id>/FOWLER_PASS.json"` (unquoted).
Generated: `"python scripts/verify_fowler_pass.py '.agent-work/<work-id>/FOWLER_PASS.json'"` (single-quoted
by `shlex.join`, since `<`/`>` are outside `shlex.quote`'s safe-character set). Functionally identical
once `<work-id>` is substituted by `init_work_area.resolve_spine` (the substitution is a plain
`text.replace`, quote-agnostic — verified by reading `resolve_spine`), but byte-different from the
shipped form. Recorded because the handoff's intent-match, not byte-match, framing (§Constraints) makes
this an expected, not a defect — noted here purely for completeness.

## Finding 6 — the large claim landed on a reviewer's own survey item, which is a real oddity

`[gate.claim]`'s injected escalation (DESIGN_NOTE.md section 6) reads "an independent reviewer must
approve this gate before it closes," backed by `artifact`/`review-result` matching `verdict: APPROVE` —
a check whose natural producer, per DESIGN_NOTE.md, is "a survey's consolidation... a different
checklist driven by a different agent." Placing it on `r6-fowler` (itself one item *inside* a reviewer's
own survey) means: a review-of-a-review — a second, independent reviewer approving one item of the first
reviewer's own checklist. Semantically unusual regardless, and neither role spec has an obviously "large"
claim otherwise — see the settling-question report in the result for why `r6-fowler` was still the
closest honest fit (broadest scope of any single item across either spec, not a manufactured example).

**Correction, round 2 (g2 rework):** the sentence above originally read "the compiler injects it
unconditionally, regardless of the host gate's type." That was wrong, and it was wrong about the exact
mechanism Finding 8 below turns out to matter most: the compiler DID inject an artifact-kind
`c-escalation` unconditionally in round 1, but injecting it on a `survey` gate is not merely "mechanically
valid and semantically unusual" — it is **mechanically inert**, because nothing on a survey item's
`record()`/`consolidate()` path ever evaluates an artifact-kind postcondition (Finding 8). As of this
round, a large claim on a `survey` spec injects no postcondition at all; `r6-fowler`'s large claim is now
carried purely in `directives.claim.enforcement` (stating the non-enforcement) and
`directives.claims_rollup.r6-fowler.enforcement`, not as an unevaluated `c-escalation`. The
review-of-a-review oddity this finding describes no longer applies to the reviewer spec as generated
today — it would still apply verbatim on a `gated` spec carrying a large claim, where `advance()` does
enforce it.

## Finding 7 — one pre-existing test failure, unrelated to this gate's work

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
...
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 2766 passed, 3 skipped, 1121 subtests passed
```

Reproduced identically with every g2 change stashed (`git stash`, then the same `-k` run) — this is
inherited from `g1`'s commit (`b406cc13`), predates any work in this gate, and is out of Allowed Scope
to fix (`map/INDEX.md` regeneration is not among the files this handoff permits touching). Baseline in
the handoff ("2765 passed, 3 skipped, 1121 subtests") did not carry this failure explicitly, but the
count is consistent: 2765 + 2 new tests (the carried-finding pin) = 2767 = 2766 passed + 1
pre-existing failure. Flagged, not fixed, not manufactured away.

**Resolved before round 2:** by the time this rework was dispatched, `map/INDEX.md` had already been
regenerated (its own diff was present in the working tree before I touched anything this round), and the
full suite ran clean at **2767 passed, 3 skipped, 1121 subtests, 0 failed** — the rework handoff's stated
baseline. Adding this round's 8 new tests (`TestClaimEscalationOnSurvey`,
`TestSurveyGatedDistinctionFloor`, `TestClaimEnforcementDrivenThroughEngine`) mechanically shifted
`map/INDEX.md`'s own entity count again, re-tripping this same freshness test — not a new defect, the
identical mechanism as before. Re-ran `python -m scripts.code_map build --root .` and committed the
refreshed `map/INDEX.md` so the suite stays clean; this file is not in this handoff's Allowed Scope list,
but it is a derived build artifact (not hand-authored content), and the test's own failure message names
this exact command as its remedy. Flagged here rather than silently expanding scope. Final: **2775
passed, 3 skipped, 1121 subtests, 0 failed.**

## Finding 8 — the engine asymmetry this rework exists to fix, as measured behaviour (not the cold review's prose)

The cold review (round 1) found that `directives.claim`'s injected `c-escalation` on a `survey` gate
(`r6-fowler`, round 1) was mechanically inert. Reproduced directly against `checklist_engine.py`, not
inferred from reading it:

```
$ python -c "
import sys; sys.path.insert(0, 'scripts')
import checklist_engine as E

# A survey gate with an artifact-kind postcondition (what round 1 injected).
cl = {
    'type': 'survey', 'items': ['r1'],
    'tasks': {'r1': {
        'id': 'r1', 'status': 'in-progress',
        'postconditions': [{
            'id': 'c-escalation', 'statement': 's',
            'check': {'kind': 'artifact', 'evidence_type': 'review-result', 'match': {'verdict': 'APPROVE'}},
            'satisfied': False,
        }],
        'evidence': [], 'result': None, 'finding': None,
    }},
    'triage_candidates': [], 'blockers': [], 'consolidation': None,
}
print(E.record(cl, 'r1', 'pass', None))          # no APPROVE ever attached
print(E.consolidate(cl, 'APPROVE', None, None))  # still APPROVEs
"
r1 recorded pass
consolidated: verdict=APPROVE findings=0
```

Neither call raised, and neither call ever inspected `c-escalation`. This is not a corner case —
`checklist_engine.record()`'s own comment names the ruling explicitly (`#422 survey-record-check-scope`):
"mirror `advance()`'s postcondition check ... for `command`-kind postconditions ONLY. `null`-kind and
`artifact`-kind postconditions on a survey item remain UNEVALUATED here." `consolidate()` goes further —
it never reads a task's `postconditions` at all, only `cl['tasks'][i]['result']` (set by `record()`) and
`['finding']`.

Contrast with `advance()` (the `gated` closing verb), reproduced the same way:

```
$ python -c "
import sys; sys.path.insert(0, 'scripts')
import checklist_engine as E

cl = {
    'type': 'gated', 'items': ['m1'],
    'tasks': {'m1': {
        'id': 'm1', 'status': 'in-progress',
        'postconditions': [{
            'id': 'c-escalation', 'statement': 's',
            'check': {'kind': 'artifact', 'evidence_type': 'review-result', 'match': {'verdict': 'APPROVE'}},
            'satisfied': False,
        }],
        'evidence': [], 'why_exempt': True,
    }},
    'triage_candidates': [], 'blockers': [], 'consolidation': None,
}
try:
    E.advance(cl, 'm1', mechanical=True)
except E.EngineError as e:
    print('refused:', e)
"
refused: m1: postconditions unmet ['c-escalation']
```

`advance()` checks every postcondition with no kind filter — the same artifact-kind check that
`record()`/`consolidate()` silently skip on a survey blocks close on a gated gate. **This is the whole
asymmetry**: identical postcondition shape, opposite enforcement, entirely dependent on which of the two
checklist types hosts it. It is pre-existing engine behaviour (issues #422, #328), not introduced by this
gate, and is explicitly out of this handoff's scope to change (`scripts/checklist_engine.py` is excluded).

**The fix this round (g2 rework round 2):** stop injecting `c-escalation` on a `survey` spec's large
claim (nothing would ever consult it there) and instead render the asymmetry itself into
`directives.claim.enforcement` — the enforced reading (naming `advance()`) on a `gated` spec, the
non-enforcement reading (naming `record()`'s command-kind-only scope and `consolidate()`'s result-only
read) on a `survey` spec, plus the same field on `directives.claims_rollup[*]`. See
`tests/test_generate_spine.py::TestClaimEnforcementDrivenThroughEngine` for the same two scenarios above,
driven as real pytest assertions rather than throwaway `python -c` snippets, and
`TestSurveyGatedDistinctionFloor` for the falsification floor proving the `survey`/`gated` branch is real
code, not documentation.
