# REVIEW_RESULT — g3-review — cold review of the dispatch proof

Verdict: APPROVE

## Close criteria — verified by running

### 1. The driven spine is genuinely terminal

Read from the driven file directly (not a transcript):

```
.agent-work/epic-559/c2-generate-the-spine/dispatch-proof/spine.json
  tasks.m0-context.status = "complete"
  tasks.m1.status         = "complete"
  engine_session.status   = "released"
  engine_session.released_at = "2026-08-11T18:54:01.374715+00:00"
```

Both items `complete`, lease `released`. Confirmed by direct read, not by trusting the handoff's summary.

### 2. Journal and `why_trail` tell the same story

```
$ cat .agent-work/epic-559/c2-generate-the-spine/dispatch-proof/spine.json.journal
seq1 attest m0-context
seq2 start  m0-context
seq3 advance m0-context   (evidence e-m0-context-1, e-m0-context-2)
seq4 attest m1
seq5 start  m1
seq6 block  m1                <- the block
seq7 resume m1                <- the resume
seq8 amend  (null task)       <- the amendment
seq9 advance m1   (evidence e-m1-3, e-m1-4)   <- the relaunch's successful close
```

`amendments[0]` records: reason (missing `--out`, argparse `required=True` unconditionally),
authority `commander-epic-559-c2 (delegated Commander)`, ops `["retext-check m1.c2"]`. This is a real,
persisted audit entry — not a claim in prose. `m1.status_detail.blocker`/`next_action`/`resume_reason`
match the amendment and the handoff's narrative verbatim in substance. The **relaunch** (a fresh crew
process, not just a resumed one) is evidenced separately — see criterion 9's process-log check below;
the journal's `session_id` field stays constant across the block/resume/amend/advance because it names
the *engine session bound to the job file*, not the OS process, so a fresh crew reusing the same spine
job is expected to keep the same session id. Confirmed this is the documented mechanism, not a
discrepancy, by reading `spine_terminal`'s and the lease code's own comments in `scripts/run_crew.py`.

Noted, not a finding: `refusals: 1` with no visible failed verb in the journal. This is documented,
correct behavior — `checklist_engine.py:3305` states the journal is "success-only by construction," so a
refusal (e.g. an early `start m1` attempted before `p1` was attested, which the imperative text
explicitly warns about) leaves no journal trace but does bump the separate `refusals` counter. Consistent
with the code, not a gap.

### 3. The spine was generated, not hand-written

```
$ python scripts/generate_spine.py .agent-work/epic-559/c2-generate-the-spine/dispatch-proof/probe.spine.toml \
    --out /tmp/regen-probe-spine.json --root .
wrote /tmp/regen-probe-spine.json
```

Structurally diffed the regenerated file against the driven file (ids, titles, imperatives,
preconditions/postconditions/checks, constraints, directives — excluding status/evidence/work_id
literal). The **only** differences are resolver-token substitutions expected from `resolve_spine`
(`<work-id>` → `epic-559/c2-generate-the-spine/dispatch-proof`, `<repo-root>` → the absolute repo path)
plus the one expected divergence: `m1.postconditions.c2.check.command`, which differs because the driven
file carries the **amended** text (`--out /tmp/m1-c2-check-out.json` added) while the freshly regenerated
file — from the untouched TOML source — still carries the original, broken text. That is exactly the
expected shape of an amendment applied post-generation, not a discrepancy. Gates, checks, and directives
otherwise byte-for-byte match.

### 4. The blocked-gate story is true

```
$ python scripts/generate_spine.py specs/reviewer.spine.toml --check-only --root .
usage: generate_spine.py [-h] --out OUT [--root ROOT] [--check-only] spec
generate_spine.py: error: the following arguments are required: --out
exit: 2

$ python scripts/generate_spine.py specs/reviewer.spine.toml --check-only \
    --root /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine \
    --out /tmp/m1-c2-check-out.json
check-only: specs/reviewer.spine.toml would compile clean
exit: 0
```

Original check text (recovered from the `amendments` audit entry) fails on the missing required `--out`
before any spec is opened; the amended text succeeds. Matches the block/resume story exactly.

### 5. The driven work is real and correct

Read `_probe_script`/`_positional_arg_faults` (`scripts/generate_spine.py:566-591`) directly, then
exercised the three-way rule against the actual function, not a description of it:

```python
_positional_arg_faults(..., ['definitely/does/not/exist.json'], ...)          -> 1 fault (not found)
_positional_arg_faults(..., ['scripts/generate_spine.py'], ...)               -> [] (real path, exists)
_positional_arg_faults(..., ['.agent-work/<work-id>/FOWLER_PASS.json'], ...)  -> [] (resolver token, skipped)
_positional_arg_faults(..., ['some_selector'], ...)                            -> [] (not path-shaped, left alone)
```

Then end to end:

```
$ python scripts/generate_spine.py specs/implementer.spine.toml --check-only --root . --out /tmp/impl-check.json
check-only: specs/implementer.spine.toml would compile clean   exit: 0
$ python scripts/generate_spine.py specs/reviewer.spine.toml --check-only --root . --out /tmp/rev-check.json
check-only: specs/reviewer.spine.toml would compile clean      exit: 0
```

Read `specs/reviewer.spine.toml`'s `r6-fowler` directly: `args = [".agent-work/<work-id>/FOWLER_PASS.json"]`
— a path-shaped positional carrying `<work-id>`, exactly the trap case. It generates clean. Getting the
skip rule wrong would have made this fail; it does not.

### 6. The `claim` spec-shape fault

Exercised `_claim_faults` directly against all five shapes (array-of-tables, bad magnitude, `large` with
no `text`, clean `normal`, clean `large`+`text`) — all five behave correctly, all producing
`spec-malformed-claim` where expected and `[]` where not. Then end to end with a real malformed spec:

```
$ python scripts/generate_spine.py /tmp/bad-claim.spine.toml --check-only --root . --out /tmp/bad-claim-out.json
spec-shape refused: 2
  [spec-malformed-claim] g1.claim: gate.claim must be a table (`[gate.claim]`), not list -- ...
  [spec-all-qualitative-postconditions] g1: ...
exit: 2
```

A named refusal, not `AttributeError: 'list' object has no attribute 'get'`. Confirmed the fault is wired
into `spec_shape_faults` before `compile_spec` ever runs (read the call order in the module).

### 7. Three-way fixtures for the new positional cases

Read `tests/test_generate_spine.py:792-834` directly. `VIOLATING_POSITIONAL` (two wrong-path cases,
caught), `INNOCENT_POSITIONAL` (a real existing path, a resolver-token path mirroring `r6-fowler`
exactly, and a non-path-shaped token — all left alone), and the pre-existing `ACCEPTED_FALSE_ALARM` case
(`test_the_accepted_false_alarm_still_fires`) is untouched and still fires. Ran the whole class:

```
$ python -m pytest -q -k TestScriptProbe --collect-only tests/test_generate_spine.py | grep -c '::'
12
$ python -m pytest -q -k TestScriptProbe tests/test_generate_spine.py
12 passed, 87 deselected in 0.05s
```

Claim-fault tests (`test_claim_array_of_tables_is_a_named_fault_not_a_crash`,
`test_claim_bad_magnitude`, `test_claim_large_missing_text`, `test_claim_normal_is_clean`,
`test_claim_large_with_text_is_clean`) cover the same five shapes I exercised by hand above.

### 8. `validate_spine.py --sweep` and untouched-scope constraints

```
$ python scripts/validate_spine.py --sweep --root . 2>&1 | grep -c '^\s*\['
23
$ git status --porcelain skills/*/templates/ scripts/validate_spine.py scripts/checklist_engine.py
(empty)
$ git diff --stat scripts/validate_spine.py scripts/checklist_engine.py
(empty)
```

Exactly 23 fault lines, no shipped template touched, `validate_spine.py`/`checklist_engine.py` byte-
identical to `HEAD`.

### 9. Full suite

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2788 passed, 3 skipped, 1121 subtests passed in 109.84s
```

Exact match to the expected count. The 3 skips are pre-existing, unrelated conditionals
(`test_mcp_adoption.py` empty-`CLI_ONLY_VERBS` skips, `test_spine_rail.py` Windows-only `ntpath` case) —
none newly introduced by this change.

Scope check: `git diff --stat HEAD` shows content changes confined to `scripts/generate_spine.py`,
`tests/test_generate_spine.py`, `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md`, plus
`map/INDEX.md` (entity-count regen — `scripts` 1135→1138, `tests` 4237→4247 entities, consistent with the
new functions/tests added, not scope drift) and the engine's own bookkeeping files
(`STATE_NOTE.md`, `crew-runs.json`, `execute.json[.journal]`, `spine.json[.journal]`). The two regenerated
role spines under `.agent-work/epic-559/c2-generate-the-spine/generated/` exist and are already tracked
with **no diff** — byte-identical to the versions already committed, matching attempt-1's own claim that
the probe only affects generation-time validation, not compiled output. `DESIGN_NOTE.md` §4, §7, §10 were
each updated to describe the new positional-arg rule, the `spec-malformed-claim` fault, and the widened
(but still partial) coverage of defect class 3 — read and confirmed against the diff, not the summary.

## Task-statement questions

**1. Did a generated spine really drive to a terminal state in a real dispatch?**

Yes. Verified directly from `dispatch-proof/spine.json` (not a transcript): both items `complete`, lease
`released`. The journal shows a genuine, non-trivial path — attest, start, block, resume, amend, advance
— across two separate crew processes (`g3-dispatch-spine-probe-attempt-1` and `-attempt-2`, both present
under `crew-runs/` with distinct stdout logs telling a consistent before/after story), not a single
straight-through run. The spine itself was compiled from `probe.spine.toml` by `generate_spine.py` and
resolved by `init_work_area.resolve_spine` — confirmed by regenerating it myself and structurally
matching the driven file (criterion 3).

**2. Does a spine-only dispatch judged on `spine_terminal` actually prove what the mission claims? Is
`spine_terminal` a check that cannot fail?**

`spine_terminal` itself (`run_crew.py:317`) is a purely **structural** predicate — every item
`complete`/`skipped`, nothing more. Read in isolation, it proves nothing about whether real work
happened: a spine authored with only `qualitative` postconditions (`check: null`, satisfied by bare
attestation) could reach `spine_terminal` on nothing but a crew's say-so, and the engine would never
object. **That would be a check that cannot fail.**

What makes *this* dispatch's proof meaningful is not `spine_terminal` in the abstract — it is what this
particular spine's postconditions actually are. `m1.c1` and `m1.c2` are `command`-kind checks, and I
confirmed by reading `checklist_engine._check_condition` (`scripts/checklist_engine.py:802-845`) that a
command-kind postcondition is **executed by the engine itself** via `subprocess`
(`_run_check_command`), with `cond["satisfied"] = proc.returncode == 0` and the resulting evidence tagged
`"produced_by": "engine"` — matching exactly what `e-m1-3`/`e-m1-4` show in the driven file. This is not
crew self-report: the crew cannot mark `m1` complete by asserting it is done; `advance` requires the
engine's own subprocess run of the real pytest command (which needed the 12 real `TestScriptProbe` tests,
including the 4 new positional-case tests, to actually exist and pass) and the real
`generate_spine.py --check-only` invocation to actually exit 0. A crew could not have reached terminal
here without the underlying code change being genuinely correct.

So: **this specific proof is real**, because this specific spine happened to gate its one substantive
postcondition behind a falsifiable, engine-run command check. But that is a property of *how the
Commander authored this spine*, not a guarantee `spine_terminal` provides in general. Say plainly: **a
`spine_terminal` dispatch proves real work only to the extent its postconditions are `command`/`artifact`
checks the engine itself runs or verifies; a spine authored with only `qualitative` postconditions would
let `spine_terminal` be reached by attestation alone, and this proof format would not catch that.** The
mission's protected intent #4 is proven for *this* dispatch, not proven as a property of the
`spine_terminal` completion contract itself.

## The adjudication question

**Was the Commander's adjudication right?** Yes, on the evidence, for four converging reasons:

1. **The check was provably wrong on its own terms**, independent of the crew's work: `--check-only`
   only skips the WRITE step (module docstring, step 6), never the CLI's own `required=True` parsing of
   `--out` — I reproduced this myself (criterion 4) and it fails identically for anyone, including a
   perfect implementation. A gate whose check can never pass regardless of the work underneath it is not
   testing the work; it is a broken instrument.
2. **`retext-check` is the sanctioned, narrowly-scoped tool for exactly this**, not an improvised
   workaround. Reading `checklist_engine.amend`'s docstring (`scripts/checklist_engine.py:2593-2622`):
   it "corrects the check TEXT... then resets that condition to unsatisfied — an authoring fix that never
   marks the condition satisfied." I confirmed this held here: the amended check still had to be run
   again and pass on its own (`e-m1-4`, exit 0) — the amendment did not grant credit, it repaired the
   instrument and let the real check run.
3. **The fix did not move the goalpost.** The substantive assertion — does `specs/reviewer.spine.toml`
   still compile clean after the change — is unchanged before and after the amendment; only an
   incidental, mandatory CLI flag was added to the invocation. I verified the corrected command still
   genuinely exercises the real generator against the real spec (criterion 4/5), not a weakened
   substitute.
4. **Authority was correctly separated.** The crew (attempt 1) diagnosed the defect, verified its own
   work independently with `--out` added by hand, explicitly declined to edit the check itself, and
   named the exact repair with the correct authority (`commander-epic-559-c2`) — this is visible verbatim
   in its stdout log. The Commander, not the crew, performed the amendment. A fresh crew (attempt 2, a
   distinct process per the crew-run logs) then independently re-earned the pass under the corrected
   check.

The one thing I'd flag as worth naming explicitly, not as a defect but as an observation: this incident
is itself a small instance of defect class 3 (a wrong flag/arg caught loudly, this time in the meta-
checklist's own authoring rather than the code under test) — which is a point *in favor* of the epic's
premise, not against it. The mechanism designed to catch exactly this class of authoring slip in specs
also caught it in the spine driving the dispatch itself, and routed it through the correct repair path
rather than silently working around it.

## Findings

None — nothing BLOCKING, SERIOUS, or MINOR survived direct verification. Every claim in the handoff's
"what happened, in order" section was independently reproduced from the driven artifacts, not taken on
trust from the transcript.

## Workflow Feedback

- The handoff's instruction to run things rather than read transcripts was well-calibrated: the two most
  load-bearing facts (that `m1.c2`'s failure was a check-authoring bug rather than an implementation bug,
  and that the positional-arg skip rule is correctly scoped) are only checkable by execution, and reading
  the transcript alone would not have distinguished "the crew is right" from "the crew is rationalizing a
  failure."
- The `checklist_engine._check_condition` code path (engine runs `command` checks itself, tags evidence
  `produced_by: "engine"`) is the single fact that most changes the shape of the answer to "does
  `spine_terminal` prove anything" — worth citing explicitly in any future DESIGN_NOTE.md discussion of
  Property 2/spine-only dispatch, since it is not obvious from the spine JSON alone that this distinction
  exists between engine-verified and crew-attested postconditions.
- No process friction to report; the close-criteria list mapped cleanly onto verifiable commands and
  nothing required guessing at intent.
