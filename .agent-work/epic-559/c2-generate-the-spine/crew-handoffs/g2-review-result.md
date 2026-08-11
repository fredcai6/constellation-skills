Verdict: APPROVE

# REVIEW_RESULT — `g2-review` ROUND 2 · the role specs, after the round-1 BLOCK

Session `constellation/epic-559/c2-generate-the-spine/g2-review/reviewer/attempt-2`. Cold, independent
of the implementer. Survey driven through `scripts/checklist_engine.py` at
`.agent-work/epic-559/c2-generate-the-spine/g2-review/review.json` (fresh instance for this round;
round 1's completed BLOCK survey is preserved in git history / prior attempt, not overwritten in spirit —
this file records round 2's own drive).

## Assigned Gate
`g2-review` (round 2, rework re-verification)

## Result
`APPROVE`

## Round 2 — what I re-verified, and how

Round 1 BLOCKED because `[gate.claim] magnitude = "large"` injected an artifact-kind `c-escalation`
postcondition onto `r6-fowler` (a survey item), and `checklist_engine.record()`/`consolidate()` never
evaluate artifact-kind postconditions on a survey item — so the escalation was silently inert. The fix:
on a `gated` spec, inject `c-escalation` unchanged; on a `survey` spec, inject **nothing** and instead
state the non-enforcement truthfully in `directives.claim.enforcement` (and the rollup), naming the exact
engine mechanism.

I did not read this claim and accept it. For every check below I ran the command myself, and for R2-a/
R2-b/R2-c I drove the real engine directly (not just the implementer's own pytest suite) so a bug in the
implementer's test could not launder a false APPROVE.

**R2-a — survey non-enforcement is real and stated, not silent.**
```
$ python -c "
import sys; sys.path.insert(0,'scripts')
import json, init_work_area as iwa, checklist_engine as E
from pathlib import Path
text = Path('/tmp/rev.spine.json').read_text()
resolved = iwa.resolve_spine(text, 'epic-559/c2-generate-the-spine', None, Path('.'))
cl = json.loads(resolved)
for item in cl['items']:
    print(E.record(cl, item, 'pass', 'scratch-drive'))
print(E.consolidate(cl, 'APPROVE', None, None))
print('c-escalation anywhere?', any(c['id']=='c-escalation' for t in cl['tasks'].values() for c in t.get('postconditions',[])))
print('verdict:', cl['consolidation']['verdict'])
"
r0-context recorded pass: scratch-drive
...
r6-fowler recorded pass: scratch-drive
consolidated: verdict=APPROVE findings=0
c-escalation anywhere? False
verdict: APPROVE
```
(`/tmp/rev.spine.json` is my own fresh `python scripts/generate_spine.py specs/reviewer.spine.toml`
output, resolved through the real `init_work_area.resolve_spine` so `<repo-root>`/`<work-id>` tokens
substitute exactly as they would in a real dispatch; `r6-fowler`'s own real `c1` check was satisfied by
the pre-existing `.agent-work/epic-559/c2-generate-the-spine/FOWLER_PASS.json`, so this exercises the
genuine command-kind gate too, not just a stub.) No `c-escalation` postcondition exists anywhere in the
generated spine, and `directives.claim.enforcement` on `r6-fowler` reads exactly: *"NOT machine-enforced
here — no postcondition is injected for a large claim on a `survey` spec... An injected postcondition
here would be silently inert, not a real gate — so none is injected."* That is now **true of the
generated artifact**, where in round 1 it would have been false.

**R2-b — the gated side genuinely enforces.**
```
$ python -c "
import sys; sys.path.insert(0,'scripts')
import checklist_engine as E
cl = {...'type':'gated','tasks':{'m1':{...'postconditions':[
    {'id':'c1','check':None,...},
    {'id':'c-escalation','check':{'kind':'artifact','evidence_type':'review-result','match':{'verdict':'APPROVE'}},...},
]}}...}
E.start(cl,'m1'); E.attest(cl,'m1','c1','postconditions','verified by hand')
try:
    E.advance(cl,'m1',mechanical=True); print('UNEXPECTED')
except E.EngineError as e:
    print('advance correctly refused:', e)
E.attach(cl,'m1','review-result',{'verdict':'APPROVE'})
print('after attach:', E.advance(cl,'m1',mechanical=True), cl['tasks']['m1']['status'])
"
advance correctly refused: m1: postconditions unmet ['c-escalation']
after attach: m1 -> complete complete complete
```
Property 2 genuinely holds on the `gated` side, exactly where `CLAIM_ENFORCEMENT_GATED`'s text claims it
does.

**R2-c — the falsification floor mutation genuinely lands (hand-verified, not trusting the test's own
assertion).**
```
$ python -c "... replace 'if spec_type == \"gated\":' with 'if True:  # MUTATED' in a standalone copy ..."
occurrences of snippet in real source: 1
$ cd /tmp/mutant_verify/work && python -m pytest -q test_floor_throwaway.py -v
    assert not any(c["id"] == "c-escalation" for c in posts)
E   assert not True
FAILED test_floor_throwaway.py::test_survey_large_claim_injects_no_postcondition
1 failed in 0.02s
```
I built the mutant myself, wrote the named throwaway test myself, and watched a real `AssertionError` —
not the test harness's own `returncode != 0` check, which could in principle pass for the wrong reason.
The mutation is real and the guard is load-bearing.

**R2-d — the `enforcement` prose itself.** Judged sound: it matches what I independently measured in
R2-a/R2-b exactly (no paraphrase drift), names the specific engine calls and their scoping
(`record()`'s command-kind-only scope, `consolidate()`'s result-only read, `advance()`'s no-filter scan),
and points the reader to `directives.handback.hand_back_to` for who must adjudicate the claim instead.
A crew reading the rendered gate would know: this claim is not machine-checked here, and whoever this
gate hands back to must judge it themselves. The one soft edge — it does not prescribe *how* that
adjudication should happen — is consistent with this being floated to the Admiral as an out-of-Commander-
latitude engine change (DESIGN_NOTE.md section 6's residual paragraph), not a gap in this round's work.

**R2-e — no command-kind escalation with no producer was smuggled in.** Confirmed: grepped the diff for
every `"kind": "command"` emission site — all three (`pytest`, `script`, `population` compilers) are
unchanged and pre-existing; nothing new ties a command check to the claim-escalation path. `CHECK_KINDS`
is untouched. The generator's only change for the survey case is prose in `directives`, exactly as
DESIGN_NOTE.md's "why not the obvious alternative" paragraph argues it should be.

## Handoff compliance
All 12 original close criteria plus R2-a..e satisfied, each independently re-run this round (not
inherited from round 1 — the generated artifacts, tests, and DESIGN_NOTE.md all changed since then):

1. **Both spines OK, zero undecidable.** `python scripts/validate_spine.py /tmp/impl.spine.json
   /tmp/rev.spine.json --root $(pwd)` → `OK` for both, no `undecidable` line. My freshly regenerated
   output (`python scripts/generate_spine.py specs/{implementer,reviewer}.spine.toml ...`) diffs
   byte-identical (`python -m json.tool` normalized) to the committed
   `.agent-work/.../generated/{implementer,reviewer}.spine.json` — the committed artifacts are current,
   not stale.
2. **Placeholder gone, selector round-trips.** `m1.c2`'s check is a real pytest command
   (`-k TestResolverOwnedTokenRegex ... --collect-only`); `validate_spine._pytest_segments` +
   `_selector` parse it back to `'TestResolverOwnedTokenRegex'` for both the collect-only and real
   segments, verified with a direct `python -c` call against the real `validate_spine` module. No
   `<exact test command>` placeholder anywhere in either generated spine (grepped).
3. **The pytest selector actually collects what it claims.** Ran the emitted command directly:
   `2 passed, 84 deselected`. Separately ran `--collect-only -k TestResolverOwnedTokenRegex
   tests/test_generate_spine.py` and counted 2 `::` lines. `min_collect: 2` is honest.
4. **Population checks are honest, as disclosed.** Ran both compiled commands directly (`skills/_shared
   global-crew.md` / `global-everyone.md` existence counts) — both exit 0. Judgment: this is a real,
   falsifiable check (delete either doctrine file and it goes red) but a weak proxy for the property that
   matters (comprehension, not presence) — exactly what the implementer's own "presence, not
   comprehension" framing says, not oversold. Acceptable given the format has no comprehension-checking
   kind and the alternative (the shipped template's `check: null`) is a strictly weaker signal.
5. **Qualitative form is stated.** `m0-context.c1`'s emitted statement carries the `-- QUALITATIVE:
   <because>` suffix verbatim, `check: null`.
6. **Handback contract on every gate.** Verified programmatically across all 9 gates in both spines
   (2 in implementer, 7 in reviewer) — `directives.handback` present and complete on every one,
   `hand_back_to: "admiral-epic-418-followon"` throughout.
7. **The large claim — superseded by the round-2 fix, as intended.** `r6-fowler`'s postconditions carry
   only `c1` (the real Fowler-pass check); `c-escalation` is gone. Notes-2.md Finding 6's "review-of-a-
   review" oddity no longer applies to the generated spine as shipped — its own round-2 correction
   paragraph says so, and I confirmed the underlying fact (no injected postcondition) directly.
8. **Notes-2 Finding 2 vs DESIGN_NOTE.md — Finding 2 is right.** `python scripts/validate_spine.py
   skills/reviewer/templates/REVIEW_SURVEY.template.json --root .` → `OK`; `r0-context`'s
   `postconditions` is `[]` (empty), not all-null, and `_fault_all_null` returns `[]` unconditionally for
   non-`gated` spines. DESIGN_NOTE.md's own "second correction, of fact" paragraph already states this.
9. **The carried assertion is real.** Mutated `_REPO_ROOT_TOKEN` to a non-resolver-owned string in a
   standalone import and watched the module-level `assert` fire with a real `AssertionError` at import
   time, naming the exact reason.
10. **No shipped template edited; oracle unmoved.** `git diff HEAD --name-only` has no
    `skills/*/templates/*`; `validate_spine.py`/`checklist_engine.py` untouched;
    `--sweep | grep -cE '^  \['` → `23`.
11. **Full suite.** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m
    pytest -q tests` → **2775 passed, 3 skipped, 1121 subtests passed, 0 failed** — matches the
    implementer's own reported count exactly. **Discrepancy noted, not blocking:** this handoff's own
    text (above) states "Expected: 2767 passed" — that number predates this round's 8 new tests and
    appears carried over unedited from before round 2 was dispatched. The measured suite is fully green
    either way; see Workflow Feedback.
12. **Settling-question residual is real, verified adversarially.** Built a `script` postcondition with
    a deliberately wrong *positional* argument (`args = ["this/path/does/not/exist/AT/ALL.json"]`
    against `scripts/verify_fowler_pass.py`) and ran the generator: **exit 0, no complaint**, the wrong
    path baked verbatim into the compiled command. Exactly the stated residual — not worse, not better.

## Scope drift
None. `git diff HEAD --stat` (excluding `.agent-work/`) touches exactly 3 tracked files:
`map/INDEX.md` (Commander's disclosed regeneration, re-tripped by this round's own new tests — same
mechanism as before, not new scope drift), `scripts/generate_spine.py`, `tests/test_generate_spine.py`.
`specs/*.toml` are untracked but confirmed byte-unchanged from round 1 (enforcement is fully
generator-computed from `spec.type`). No shipped template, `validate_spine.py`, or `checklist_engine.py`
touched.

## Evidence verdict
Sufficient and behavior-demonstrating, not shape-demonstrating — the specific gap round 1 found in the
implementer's own Evidence #6 (compilation shown, enforcement never driven) does not recur: every claim
in this round's Required Evidence was independently reproduced against the real engine by me, using my
own scratch spines and hand-built mutants, not just by re-running the implementer's pytest suite.

## Code/doc quality
Minimal, matches the decision the rework handoff specified exactly, no speculative abstraction. Fresh
Fowler pass run specifically over this round's diff (round 1's `FOWLER_PASS.json` only covered the
earlier carried-cleanup diff and did not mention the enforcement branch or the 3 new test classes;
overwritten with a pass scoped to this round — see `.agent-work/epic-559/c2-generate-the-spine/
FOWLER_PASS.json`). All 12 baseline smells `absent`, each with a considered, non-blank finding where a
smell was plausible enough to warrant one (duplicated-code on the two enforcement constants,
divergent-change on `_compile_gate`'s added axis, shotgun-surgery noting `specs/*.toml` correctly
untouched). `python scripts/verify_fowler_pass.py .agent-work/epic-559/c2-generate-the-spine/
FOWLER_PASS.json` → exit 0.

## Map impact verdict
No structural/capability/constraint change to review here beyond what `g1`/round-1 `g2` already
established (this round is a compiler-internal branch + test additions, no new spec field, no new check
kind). Skipping per the template's own "skip for trivial local edits" guidance — the one durable item
(the engine's survey/artifact-postcondition gap) is already routed via DESIGN_NOTE.md's floated residual
and my own `tc1` below, not silently dropped.

## Reconciliation check
Round-1's `tc2` (DESIGN_NOTE.md's `r0-context` factual error) is resolved — DESIGN_NOTE.md section 6 now
states the correct measurement. Round-1's `tc1` (the underlying engine gap) persists and is not this
round's to fix; re-flagged below, already floated to the Admiral in DESIGN_NOTE.md itself.

## Blockers
- none

## Out-of-scope observations
- **tc1 (re-flagged, filed into this survey's `triage_candidates[]` via `flag-candidate`):**
  `checklist_engine.py`'s `record()`/`consolidate()` never evaluate artifact-kind (or null-kind)
  postconditions on a survey checklist. This round's fix correctly works around it for large-claim
  escalations by not injecting on survey specs, but the gap itself is unchanged and, per DESIGN_NOTE.md
  section 6's own residual paragraph, applies to every `artifact`/`user-decision` human checkpoint in the
  corpus, not just claim escalations — a determined single agent can still self-attach an `APPROVE`
  `review-result` on a survey with no independent check. Already floated to the Admiral in
  DESIGN_NOTE.md; this is a durable-context re-file, not a new finding.

## Workflow Feedback

- **Handoff gaps:** Close criterion 11's stated "Expected: 2767 passed, 3 skipped, 1121 subtests" is
  stale — it does not account for the 8 tests this round's rework added (measured: 2775). This is a
  carry-over artifact from the original (pre-round-2) handoff text, not a defect in the change; a future
  rework handoff should re-derive expected suite counts from the round's own dispatch point rather than
  copying the prior round's numbers verbatim, since a diligent reviewer has to notice the drift and
  decide it's not a red flag rather than being told it's expected.
- **Context rediscovered:** None beyond what the handoff and DESIGN_NOTE.md already carried — this
  round's handoff was unusually complete (it names the exact root cause, the decision made, and the
  files touched), which made re-verification straightforward rather than exploratory.
- **Instructions improvised around:** Driving a scratch copy of the generated `reviewer.spine.json`
  through the real engine required resolving `<repo-root>`/`<work-id>` tokens myself via
  `init_work_area.resolve_spine` first (the raw generator output still carries the literal tokens) —
  the handoff doesn't mention this step, and a first attempt without it fails opaquely (`cd <repo-root>`
  is not a valid shell target). Not a defect, just a step future reviewers driving a generated-but-
  unresolved spine will hit the same way.
- **What would have made this easier:** None otherwise — the round-2 preamble's explicit "what changed
  since your BLOCK" section made it possible to re-verify precisely the delta rather than re-doing all of
  round 1's work from scratch.

## Return status
`complete`
