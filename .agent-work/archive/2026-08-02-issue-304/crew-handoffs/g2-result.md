# Implementation Result — issue-304 gate g2 (implementer attempt-2)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2 — wire the contract at context and plan`

Driven through `.agent-work/issue-304/g2-implementer-plan.json` under engine session
`g2-implementer-304b` (forced takeover of the dead `g2-implementer-304` lease). Slices m2–m6 all
advanced to `complete`; m0/m1 were already closed by attempt-1.

## Completed slice
All six. Attempt-1 died on a session usage limit mid-`m2` with m2/m4/m5 substance landed at `fdec654`
and unreviewed. This attempt **audited that work against the handoff's deliverables rather than
trusting it**, found and fixed a real gap (m3's oracle was dead code), and completed m6.

Commits, one per slice:

```
22e5134 g2 m6(#304): extend the mutation floor with three verify-frame mutations
06ce473 g2 m5(#304): close installer registration slice - audited, red reconstructed vs 6d35fe2
e7d63ea g2 m4(#304): close template wiring slice - audited, red reconstructed vs 6d35fe2
8ba4529 g2 m3(#304): wire the degraded fallback oracle - probe into the receipt, label both substitute provenances
72a7de0 g2 m2(#304): close verify-frame slice - audited landed impl, red reconstructed vs 6d35fe2
fdec654 gate g2(#304): re-anchor map-first ... (WIP, resumed)   <- attempt-1
6d35fe2 gate g1(#304): map_orient resolver, receipt, REPORTED degraded mode   <- g1 baseline
```

### The audit gap I found and fixed (m3)

Attempt-1 wrote `probe_fallbacks()`, `classify_substitute()` and `substitute_label()` — and **never
called any of them from `cmd_orient`**. `pin_substitutes()` wrote no `source` key. The self-test
exercised the pure helpers, so everything was green while the receipt recorded **nothing** of the
independent oracle the handoff's "ALSO ADDED" section asked for. The two degraded-arm test fixtures
(`DEGRADED_FRAME`, `UUNDECLARED_FALLBACK_FRAME`) were defined and never used by any test.

Fixed: `cmd_orient` now calls `probe_fallbacks(root)`; every receipt carries `fallbacks_probed`;
`pin_substitutes` stamps `source` on each entry.

> **CORRECTION (rework m7) — my audit was incomplete, and I reported it as complete.**
> The paragraph above names **three** dead helpers and then lists fixes for only **two**.
> `probe_fallbacks` and `classify_substitute` got call sites; **`substitute_label` did not.** It
> stayed reachable only from `self_test()`, so the `source` key was written to every receipt and read
> back by nothing — no output surface, no test outside the module's own harness. The g2 review caught
> it and returned BLOCK. Closed in m7 below.
>
> **Why my reachability pass missed it, stated plainly:** I grepped for call sites rooted at `main`
> as the entrypoint. `main` reaches `self_test` via the `--self-test` subcommand, so every
> self-tested helper came back "reachable" — including one whose only caller was the test harness.
> **A module that ships its own test harness as a subcommand launders dead code as live.** The
> reviewer re-ran the same pass with `self_test` blocked as a traversal node and it fell out
> immediately.
>
> This is the identical defect class I had just flagged in attempt-1's work and called a BLOCK-level
> trap. Finding it once did not stop me from reproducing it, because I fixed the *instance* and never
> fixed the *method*. The corrected rule is in Workflow Feedback: **a call site outside the def AND
> outside the self-test.**

A second defect surfaced while writing m3's tests: the undeclared-substitute refusal **renamed the
offender to lowercase** (`CLAUDE.md` reported as `claude.md`), and `--self-test` was asserting the
lowercased form — the self-test was pinning the defect. Both fixed; matching stays case-insensitive,
reporting is now as-cited.

## Scope
**Files changed** (whole gate, `6d35fe2..HEAD`):
- `scripts/map_orient.py`
- `scripts/install_constellation.py`
- `skills/commander/templates/COMMANDER_SPINE.template.json`
- `tests/test_map_orient.py`
- `tests/test_map_contract_wiring.py` (new)
- `tests/test_mutation_floor.py`

```
scripts/install_constellation.py                   |  10 +-
scripts/map_orient.py                              | 578 ++++++++++++++++++++-
skills/commander/templates/COMMANDER_SPINE.template.json |  12 +-
tests/test_map_contract_wiring.py                  | 271 ++++++++++
tests/test_map_orient.py                           | 395 ++++++++++++++
tests/test_mutation_floor.py                       |  63 +++
6 files changed, 1311 insertions(+), 18 deletions(-)
```

This attempt's own contribution (`fdec654..HEAD`): 251 insertions, 9 deletions across
`map_orient.py`, `test_map_orient.py`, `test_mutation_floor.py`.

**Specific exclusions touched:** `no`. No prose deletion (g3's job — the dead-path block is
untouched). No bootstrap/CLAUDE.md stanza. `reconcile` untouched. #341/#342/`--receipt-dir` not
fixed. `checklist_engine.py` not modified. Nothing outside
`C:/Programs/constellation-skills-wt/e298-304`; `C:/Programs/f1Brainz` was never given to any tool.

## Behavior changed
**Yes.**
1. `map_orient.py verify-frame --root ABS --work-id ID` — new subcommand. Refuses an absent frame, an
   unknown anchor (naming it), a code-cut frame, and a degraded frame citing an undeclared substitute.
2. Every orientation receipt now carries `fallbacks_probed` and a per-substitute `source` label.
3. `COMMANDER_SPINE.template.json` gates `verify-orientation` at context c2 and `verify-frame` at
   plan c6, and the context imperative is re-anchored to "Before you open any source file".
4. `map_orient.py` now ships with the commander bundle.

## Map Impact
- **Structural anchors touched:** `scripts/map_orient.py` — the map-contract module; gained the
  `verify-frame` seam and the fallback-probe edge alongside the existing `orient` /
  `verify-orientation` seams.
- **Capabilities added/changed/affected:** frame-citation verification (new, observable via exit
  code); degraded-substitute provenance labelling (new).
- **Constraints/assumptions touched:** the frozen g1 exit-code vocabulary is **honored** — no new
  codes. Codes `10` and `12` carry a documented wider reading (10 = the map contract is undischarged;
  12 = a required input document is missing), stated in the module docstring rather than left implicit.
- **Decision candidates / resolved decisions:** `verify-frame` is deliberately **absent** from the
  context step. Making it context-safe by letting an absent frame pass would destroy the anti-vacuity
  property the whole check rests on; the road-not-to-take is recorded in the plan imperative prose and
  in the module docstring. If it ever must be context-safe, give it a step-scoped mode, never a
  vacuous pass.
- **Claims/evidence produced:** the citation check is a **regression floor against map-ignoring**, not
  the fix for map-lateness. Measured sensitivity 0/4, specificity 0/1 against the epic's baseline five.
  Stated in that form in the module docstring, the test file header, and the plan imperative — not
  overclaimed anywhere.
- **Trust limitations / drift found:** the degraded check remains **partly self-attested**. The
  fallback probe converts *half* of it to a filesystem oracle; the agent still chooses what to
  declare, and anything outside the fixed set stays labelled `agent-declared`. Deliberately not
  described as closing the gap.
- **Triage candidates:** see *Out-of-scope observations*.

## Test mode
**Required:** `test-first`
**Satisfied:** `partially — 2 of 5 c1 conditions were genuine TDD red; 3 were reconstructed. Every
reconstruction is named below as a deviation.` See *TDD evidence*.

## Evidence

### 1. The handoff's required evidence command, run verbatim

```bash
cd C:/Programs/constellation-skills-wt/e298-304
python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_context_manifest.py tests/test_context_declaration_lint.py tests/test_context_determinism.py tests/test_install_constellation.py -q
```

```
............................................................................................................................ [ 43%]
................................................. [ 60%]
.................................................... [ 79%]
...........................................................                  [100%]
284 passed, 419 subtests passed in 161.02s (0:02:41)
PYTEST_EXIT=0
```

```bash
python scripts/map_orient.py --self-test
```

```
self-test OK
SELFTEST_EXIT=0
```

**Result:** `pass`

### 2. Superset including the new wiring file

The handoff's command predates `tests/test_map_contract_wiring.py`, so it does not cover it. Same
command plus that file:

```bash
python -m pytest tests/test_map_orient.py tests/test_map_contract_wiring.py tests/test_mutation_floor.py tests/test_context_manifest.py tests/test_context_declaration_lint.py tests/test_context_determinism.py tests/test_install_constellation.py -q
```

```
.................................................... [ 70%]
........................................................................ [ 94%]
................                                                         [100%]
303 passed, 433 subtests passed in 155.00s (0:02:35)
```

**Result:** `pass`

### 3. The exact JSON of the two new checks, as they appear in the template

Context step, `c2`:

```json
{
  "id": "c2",
  "statement": "the map input was resolved BEFORE any source file was opened, and the orientation contract is satisfied: RESOLVED, or a DEGRADED verdict discharged with hash-pinned substitutes AND the unmapped gap AND an escalation. Gate-vs-report is a flag flip: append --report-only to the command below to turn this gate into a non-blocking report without rewiring the step.",
  "check": {
    "kind": "command",
    "command": "python <commander-skill-dir>/scripts/map_orient.py verify-orientation --root <repo-root> --work-id <work-id>"
  },
  "satisfied": false
}
```

Plan step, `c6`:

```json
{
  "id": "c6",
  "statement": "the mission frame at .agent-work/<work-id>/MISSION_FRAME.md cites anchors that resolve against the map the context step oriented on (or, when context degraded, against the substitutes the receipt hash-pinned) \u2014 an ABSENT frame REFUSES and never vacuously passes. A regression floor against map-ignoring, NOT a check for map-lateness; waive it for a genuinely trivial change so the escape is recorded. Gate-vs-report is a flag flip: append --report-only to turn this gate into a non-blocking report without rewiring the step.",
  "check": {
    "kind": "command",
    "command": "python <commander-skill-dir>/scripts/map_orient.py verify-frame --root <repo-root> --work-id <work-id>"
  },
  "override_policy": {
    "allowed": true,
    "authority": "human",
    "reason_required": true
  },
  "satisfied": false
}
```

The asymmetry the handoff demanded holds: context `c2` carries **no** `override_policy` (tighter);
plan `c6` carries the human-authority recorded-waiver policy; both use `<repo-root>`, not a relative
path; `verify-frame` does **not** appear at context.

### 4. `verify-frame` refusing an absent frame

Run against a throwaway fixture repo in the scratchpad (never f1Brainz — `orient` writes a receipt
into whatever `--root` it is given):

```bash
python scripts/map_orient.py orient --root <fixture> --work-id demo
python scripts/map_orient.py verify-frame --root <fixture> --work-id demo
```

```
FRAME-MISSING
frame: .agent-work/demo/MISSION_FRAME.md
orientation: RESOLVED
no mission frame to check -- REFUSED, never a vacuous pass
problems: 1
  - no mission frame: .agent-work/<work-id>/MISSION_FRAME.md is absent or empty. An absent frame REFUSES -- it never vacuously passes.
EXIT=12
```

## TDD evidence, if required

### m2 `c1` — RECONSTRUCTED (deviation)

`verify-frame` already existed at `fdec654`, so the red could not be observed in TDD order.
Reconstructed against `6d35fe2`, a tree in which the subcommand genuinely does not exist:

```bash
git checkout 6d35fe2 -- scripts/map_orient.py
python -m pytest tests/test_map_orient.py -q -k "AbsentFrameRefuses"
```

```
E       AssertionError: 'MISSION_FRAME.md' not found in "usage: map_orient.py [-h] [--self-test] {orient,verify-orientation} ...\nmap_orient.py: error: argument command: invalid choice: 'verify-frame' (choose from orient, verify-orientation)\n"
FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_a_frame_without_a_receipt_refuses_rather_than_passing
FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_an_absent_frame_refuses_on_a_degraded_repo_too
FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_an_absent_frame_refuses_on_a_resolved_repo
FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_an_empty_frame_file_is_the_same_as_no_frame
FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_the_refusal_names_the_path_it_looked_for
5 failed, 63 deselected in 0.94s
```

Restore verified **by blob OID**, not by raw bytes:

```
git checkout fdec654 -- scripts/map_orient.py
BLOB-OID-MATCH: git diff --quiet HEAD exit 0
porcelain:[]
5 passed, 63 deselected in 0.92s
```

### m3 `c1` — GENUINE TDD red, observed in order (no deviation)

The fallback probe was dead code, so the tests were written first and the red is real:

```bash
python -m pytest tests/test_map_orient.py -q -k "KnownFallbackProbe or SubstituteLabels or VerifyFrameDegraded"
```

```
E       KeyError: 'fallbacks_probed'
E       KeyError: 'source'
E       AssertionError: 'CLAUDE.md' not found in 'FRAME-REFUSED\n...\n  - the frame cites claude.md, which the receipt never declared as a hash-pinned substitute -- ...'
FAILED tests/test_map_orient.py::KnownFallbackProbe::test_a_probed_fallback_that_exists_is_hash_pinned_too
FAILED tests/test_map_orient.py::KnownFallbackProbe::test_orient_records_which_known_fallbacks_actually_exist
FAILED tests/test_map_orient.py::KnownFallbackProbe::test_the_probe_reports_a_fallback_the_agent_never_declared
FAILED tests/test_map_orient.py::SubstituteLabels::test_a_declared_but_ABSENT_known_fallback_is_not_labelled_verified
FAILED tests/test_map_orient.py::SubstituteLabels::test_a_docs_index_fallback_is_labelled_known_fallback
FAILED tests/test_map_orient.py::SubstituteLabels::test_a_path_outside_the_known_set_is_labelled_agent_declared
FAILED tests/test_map_orient.py::SubstituteLabels::test_a_present_known_fallback_is_labelled_known_fallback
FAILED tests/test_map_orient.py::SubstituteLabels::test_the_label_never_upgrades_the_pin
FAILED tests/test_map_orient.py::VerifyFrameDegraded::test_a_degraded_frame_citing_an_UNDECLARED_fallback_refuses
9 failed, 3 passed, 68 deselected in 1.69s
```

Green after implementation: `12 passed, 68 deselected in 2.48s`.

**Honest note:** 3 of the 12 passed *before* the implementation — the three degraded-frame cases that
attempt-1's `frame_verdict` already handled. Only the 9 above were red. I am not claiming the other
three as TDD red.

### m4 `c1` — RECONSTRUCTED (deviation)

```bash
git checkout 6d35fe2 -- skills/commander/templates/COMMANDER_SPINE.template.json
python -m pytest tests/test_map_contract_wiring.py -q
```

```
E       AssertionError: False is not true : no verify-frame check on the plan step: []
FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_degraded_is_a_declared_reading_not_a_licence_to_start_from_code
FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_later_source_reads_are_framed_as_confirming_not_building
FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_the_context_imperative_names_the_orient_command_it_expects
FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_the_map_read_is_anchored_before_any_source_file_is_opened
FAILED tests/test_map_contract_wiring.py::ContractWiring::test_context_c2_is_a_command_check_naming_verify_orientation
FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_imperative_names_where_the_frame_must_be_written
FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_imperative_records_the_asymmetry_and_the_road_not_to_take
FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_imperative_states_that_the_check_is_a_floor_not_the_fix
FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_step_carries_a_verify_frame_command_check
9 failed, 10 passed, 7 subtests passed in 0.23s
```

Restore: `BLOB-OID-MATCH: git diff --quiet HEAD exit 0`, `porcelain:[]`,
`19 passed, 14 subtests passed in 0.16s`.

### m5 `c1` — RECONSTRUCTED (deviation)

```bash
git checkout 6d35fe2 -- scripts/install_constellation.py
python -m pytest tests/test_map_contract_wiring.py tests/test_install_constellation.py -q
```

```
E               AssertionError: 'map_orient.py' not found in ('checklist_engine.py', 'gauge_reader.py', 'init_work_area.py', 'verify_agent_feedback.py', 'verify_state_note.py', 'run_crew.py', 'recover_crews.py', 'apply_lessons_delta.py', 'verify_lessons_applied.py', 'verify_worktree_isolation.py', 'agent_work_root.py')
SUBFAILED(skill='commander') tests/test_map_contract_wiring.py::ScriptIsBundled::test_map_orient_ships_with_every_skill_whose_template_invokes_it
1 failed, 120 passed, 306 subtests passed in 15.09s
```

Restore: `BLOB-OID-MATCH: git diff --quiet HEAD exit 0`, `porcelain:[]`,
`120 passed, 308 subtests passed in 18.63s`.

### m6 `c1` — GENUINE, applied-before-red discipline held (no deviation)

Three new mutations against `verify-frame`. For the vacuous-pass mutant the applied-before-red
assertions were evaluated **first**, and only then was the floor run:

```
APPLIED-BEFORE-RED, mutation: an ABSENT mission frame credited as a pass
  anchor unique in original : 1 (must be 1)
  anchor gone after sub     : 0 (must be 0)
  replacement count delta   : 0 -> 1 (must be +1)

FLOOR UNDER MUTANT -> returncode 1
killed by:
  tests/test_map_orient.py::ContractShape::test_self_test_floor_passes
  tests/test_map_orient.py::AbsentFrameRefuses::test_an_absent_frame_refuses_on_a_degraded_repo_too
  tests/test_map_orient.py::AbsentFrameRefuses::test_an_absent_frame_refuses_on_a_resolved_repo
  tests/test_map_orient.py::AbsentFrameRefuses::test_an_empty_frame_file_is_the_same_as_no_frame
```

All three new mutants killed:

```bash
python -m pytest tests/test_mutation_floor.py -q -k "test_6 or test_7 or test_8 or HarnessSelfCheck"
```

```
6 passed, 6 deselected, 9 subtests passed in 35.92s
```

The three mutations: (6) an absent mission frame credited as a pass — the vacuous pass, killed by
`AbsentFrameRefuses`; (7) the undeclared-substitute refusal disabled — killed by
`VerifyFrameDegraded`; (8) the known-fallback label granted on set membership alone — killed by
`SubstituteLabels`. `HarnessSelfCheck` still proves a non-matching anchor raises `HarnessError`
rather than being credited as a kill.

**Refactor while green:** yes — the `cited` loop in `frame_verdict` was restructured to carry the
as-cited spelling alongside the comparable one, with the suite green either side.

## Deviations — every one, with its reason

1. **m2 `c1` red reconstructed, not observed in TDD order.** `verify-frame` already existed at
   `fdec654`. Reconstructed against `6d35fe2` per the resume addendum's sanctioned method; 5 genuine
   failures pasted above; restore verified by blob OID. This proves the tests **discriminate**; it
   does **not** prove TDD authoring order, and I do not claim it does.
2. **m4 `c1` red reconstructed** — same reason, same method, template file, 9 failures pasted.
3. **m5 `c1` red reconstructed** — same reason, same method, installer file, 1 failure pasted.
4. **Engine lease force-taken.** `claim --session-id g2-implementer-304b --force`, reason
   "attempt-1 died on a session usage limit". Sanctioned by the addendum.
5. **A `--self-test` assertion was changed, not just added.** `"that refusal names the undeclared
   path"` asserted the lowercased `claude.md`. That assertion was pinning a defect: the refusal
   renamed the offender the author has to act on. Changed to assert the as-cited `CLAUDE.md`. This is
   the only pre-existing assertion I altered, and it was altered to be **stricter**, not to make my
   change pass. Flagging it explicitly because "changed a test to green" is exactly the shape a
   reviewer must not have to discover on their own.
6. **The "free fix" from the addendum was NOT taken — the finding is a false positive.** See below.
7. **(m7) An incomplete audit was reported as complete.** See the CORRECTION block above. The
   narrative named three dead helpers and fixed two; the third, `substitute_label`, was closed only
   after the review returned BLOCK.
8. **(m7) The plan was amended, not appended to.** Commander directed `append` a slice rather than
   `reopen m3` (correct: `reopen` cascade-resets m4–m6, whose work this finding does not touch and
   which were independently verified). The engine **refused** `append`: `REFUSED: append only on
   survey checklists`. This is a gated plan. I used the sanctioned gated re-planning verb instead —
   `amend --delta <ops> --authority "commander-304c (relaying g2 review BLOCK)"` with an `add` op
   inserting `m7` after `m6`. Same effect Commander asked for, different verb; recorded because the
   instruction named a verb this controller type does not have. Engine gap noted in Workflow Feedback.

## Rework m7 — the g2 review BLOCK, closed

**Finding:** `substitute_label()` (`scripts/map_orient.py:704`) was reachable only from `self_test()`.
The `source` key it decodes was written at `cmd_orient` and never read back by any output surface or
test. Dead **read**-side code — the write side was correctly wired, so real receipts did carry
`source` and `fallbacks_probed`. Verified independently before acting: `grep -n substitute_label`
returned the def plus three call sites at `:1575`, `:1580`, `:1585`, all inside `self_test` (`:1274`).

**Resolution taken: wire it into the reported output** (Commander's first-choice adjudication; the
delete-instead fallback was not needed, and the "document it as a receipt decoder" third path was
explicitly refused and not taken).

`render_verify_report()` now decodes each receipt substitute through `substitute_label()` and emits a
provenance line. `verify-orientation` is the honest home: it is the surface that genuinely reads a
receipt back **from disk**, which is the only situation in which `substitute_label`'s lenient-decode
contract is real — a receipt written by an older version carries no `source` and must read as the
conservative `agent-declared`, never be upgraded by omission.

Both constraints honored:
- The `source` key on each receipt entry **stays** — untouched. It remains the committed prior
  declaration `verify-frame` checks a frame against.
- **`orient` still never prints an anchor id.** Re-run, not assumed: `test_orient_never_prints_an_anchor_id`
  passes, and a new `test_the_report_still_prints_no_anchor_id` asserts the same of the surface I
  changed, using a `README.md` that deliberately contains `struct:app` in its prose.

### m7 TDD evidence — GENUINE red, observed in order (no reconstruction)

Test class `SubstituteProvenanceIsReported` written **outside `self_test`** first, then run:

```bash
python -m pytest tests/test_map_orient.py -q -k "SubstituteProvenanceIsReported"
```

```
E       AssertionError: 'agent-declared' not found in 'DEGRADED-NO-MAP\nreceipt: .agent-work/w/map-orientation.json\norientation contract SATISFIED\nproblems: 0\n'
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_BOTH_labels_appear_in_one_real_report
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_a_present_known_fallback_is_REPORTED_as_known_fallback
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_a_receipt_with_no_source_key_reports_as_agent_declared
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_an_agent_declared_substitute_is_REPORTED_as_unverified
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_an_unrecognised_source_value_reports_as_agent_declared
5 failed, 2 passed, 80 deselected in 1.79s
```

The red is the report itself: `problems: 0` and **no provenance line at all**. After wiring:

```
7 passed, 80 deselected in 1.58s
```

**Reachability re-verified** with the reviewer's own method — `substitute_label` is now called at
`map_orient.py:958`, inside `render_verify_report` (defined `:923`), which `cmd_verify_orientation`
calls. That is well outside `self_test`, which begins at `:1274`.

### m7 — both labels in real command output

```bash
python scripts/map_orient.py orient --root <fixture> --work-id demo \
  --substitute README.md --substitute docs/notes/mine.md \
  --unmapped "everything structural" --escalation "ask commander for a map"
python scripts/map_orient.py verify-orientation --root <fixture> --work-id demo
```

```
DEGRADED-NO-MAP
receipt: .agent-work/demo/map-orientation.json
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
substitute: docs/notes/mine.md [agent-declared] -- UNVERIFIED -- declared by the agent, not corroborated by the filesystem
EXIT=0
```

That `README.md` contains `struct:app` in its prose; no anchor id reaches the output.

### m7 — two new mutations pin the read side

Because the original defect was precisely "a helper nothing reads," the floor now attacks the read
path itself. Both killed, applied-before-red discipline unchanged:

- **"every substitute reported as known-fallback"** — the dangerous direction: an agent-declared
  substitute silently wearing the verified label. **The original g2 work could not have killed this
  mutation at all**, because no output surface read the label back.
- **"the provenance line dropped from the report"** — reverts the BLOCK exactly: receipt still
  carries the provenance, no reader is ever shown it.

```bash
python -m pytest tests/test_mutation_floor.py -q -k "test_9 or test_10 or HarnessSelfCheck"
```

```
5 passed, 9 deselected, 11 subtests passed in 26.51s
```

### m7 — full close-criteria suite

```bash
python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_context_manifest.py tests/test_context_declaration_lint.py tests/test_context_determinism.py tests/test_install_constellation.py tests/test_map_contract_wiring.py -q
python scripts/map_orient.py --self-test
```

```
............................................................................................................................................................................... [ 56%]
.............................................. [ 70%]
...........................................................................................                                              [100%]
312 passed, 435 subtests passed in 200.00s (0:03:20)
PYTEST_EXIT=0
=== SELF-TEST ===
self-test OK
SELFTEST_EXIT=0
```

**Result:** `pass`. 312 passed vs 303 at the pre-rework result — the delta is m7's 7 new
provenance-report tests plus 2 new mutation tests. The suite did not hang (200s).

## The addendum's offered free fix — declined, with evidence

The addendum said `CONTENT_HASH_RE` uses `{64}` where `{64,}` is correct, "a longer-than-64 digest
currently slips the pin." **Measured, and it does not:**

```
pattern: ^[0-9a-f]{64}$
short     len= 63 is_content_hash -> False
exact     len= 64 is_content_hash -> True
long-65   len= 65 is_content_hash -> False
long-128  len=128 is_content_hash -> False
```

The `$` anchor already rejects longer-than-64 digests. Changing `{64}` to `{64,}` would **loosen**
the pin — a 128-char sha512 would then be accepted as a sha256 pin. I left it alone deliberately.
g1's re-review survivor should be closed as **not a defect**.

## Docs/contracts touched
- `scripts/map_orient.py` module docstring — receipt schema updated with `fallbacks_probed` and the
  per-substitute `source`, plus an honest paragraph on what the partial oracle does and does not buy.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — context and plan imperatives (served
  behaviour). Per the handoff, runtime descriptions cite the **served** line numbers `:22` (context)
  and `:40` (plan) at `74953936`; the repo copy has drifted to `:22`/`:48` (#344).

## Assumptions
- The handoff's required-evidence command predates `tests/test_map_contract_wiring.py`. I ran it
  verbatim **and** ran the superset, and reported both rather than silently substituting.
- `python` is 3.14 with pytest; `py` is 3.12 with none. Neither reproduces CI 3.12-with-pytest, so
  green here is **not** proof of CI green. No 3.13+-only APIs were introduced (no
  `Path.read_text(newline=...)`); all new code is stdlib and version-neutral.

## Stop conditions hit
- `none — confirmed after review:` no stop condition fired. `verify-frame` wired at plan without
  running at context (asserted by `test_verify_frame_never_runs_at_the_context_step`); the three
  template-pinning suites pass unchanged because no `context_refs` entry was added; every required
  negative case was written and observed failing.

## Out-of-scope observations
- **Triage candidate — the fallback probe runs on RESOLVED receipts too.** Deliberate (an agent must
  not be able to suppress the probe by claiming the map resolved), but it costs 5 `stat` calls plus
  up to 5 file hashes on every `orient`. Cheap today; worth a look if `orient` ever runs hot.
- **Triage candidate — `PATH_TOKEN_RE` over-matches.** Tokens like `e.g` are silently ignored because
  they fail both the source-suffix and fallback-membership tests. Correct today, but the silence is
  load-bearing and undocumented at the regex itself.
- **g1 re-review survivor `CONTENT_HASH_RE` should be closed as not-a-defect** — evidence above.
- **#344 (repo/served template line drift `:40` vs `:48`) is still open** and made citing runtime
  behaviour needlessly manual. Not fixed here (out of scope).

## Workflow Feedback

- **Handoff gaps:** the **Required evidence** field is stale by construction — it names a fixed test
  list, but the gate's own work *adds* a test file (`test_map_contract_wiring.py`), which the list
  then does not cover. A handoff that mandates new tests should say "the listed suites **plus any
  test file this gate adds**", or the required-evidence command silently under-covers the gate it is
  certifying. This is the one field I had to improvise around.
- **Context rediscovered:** which of m3/m4/m5's substance attempt-1 had actually landed. The addendum
  said "parts of m3/m4/m5" and pointed at m1's digest, but the real answer only came from diffing
  `6d35fe2..fdec654` and grepping for callers. The specific trap: m3's helpers **existed and were
  self-tested but were never called**, so every green signal said "done". A resume addendum that says
  "audit, don't trust" is right, but "green tests" is not evidence a deliverable landed — **grep for
  the caller** is. Worth promoting to doctrine for resumed gates.
- **Instructions improvised around:** the addendum's reconstruction note shape says "N failures
  pasted" but does not say where the paste lives. The engine's `--note` is the natural home, yet
  notes are not what a reviewer reads — `g2-result.md` is. I put the count and root cause in the note
  and the full paste in the result, and cross-referenced them.
- **What would have made this easier:** one line in the resume addendum stating, per slice, the
  **grep that proves the deliverable is wired**, not merely present — e.g. "m3 lands only if
  `grep -n 'probe_fallbacks' scripts/map_orient.py` shows a call site outside its own def." That
  single line would have collapsed my whole audit phase into three commands.

### Added at rework (m7) — the two that actually cost a review round-trip

- **The reachability rule I wrote above was WRONG, and it is the reason the BLOCK happened.** I said
  "a call site outside its own def." That is insufficient for any module that ships its own test
  harness as a subcommand: `--self-test` makes `self_test` reachable from `main`, so every
  self-tested helper passes an "outside its own def" grep while being dead to every real caller.
  **Corrected rule, worth promoting to doctrine:** *a call site outside the def **and outside the
  self-test*** — equivalently, run the reachability pass with `self_test` blocked as a traversal
  node. This defect class has now been found **twice in the same gate** (attempt-1's
  `probe_fallbacks`, then my own `substitute_label`), which is the signal that the *method* needed
  fixing, not just each instance. A module that self-tests in-process should probably carry this
  warning at the `self_test` def itself.
- **Engine gap: `append` is survey-only, but the rework instruction assumed it works on a gated
  plan.** Commander correctly directed "`append` a new slice rather than `reopen m3`" — `reopen`
  would cascade-reset m4–m6, forcing re-attestation of reds that cannot honestly be re-observed. The
  engine refused: `REFUSED: append only on survey checklists`. The gated equivalent exists but is
  named differently and takes a JSON delta file: `amend --delta <ops.json> --reason --authority`
  with an `add` op. Two asks: (1) the `append` refusal message should **name the gated alternative**
  ("use `amend` with an `add` op") instead of only stating what is not allowed, since the agent
  hitting it always wants the same thing; (2) orchestrator-tier doctrine on rework should say
  "append (survey) / amend-add (gated)" rather than "append", because the verb genuinely differs by
  controller type and the instruction as written is unrunnable half the time.

## Return status
`complete` — including rework m7, which closes the g2 review's single BLOCK finding.

Rework summary for the reviewer: `substitute_label()` is now read by `render_verify_report()` and
asserted by 7 tests outside `self_test`, plus 2 new mutations attacking the read path. The `source`
receipt key is unchanged. `orient` still prints no anchor id (re-run, not assumed). The audit
narrative above is corrected with the reason my `main`-rooted reachability pass missed it. Full
close-criteria suite: 312 passed, 435 subtests, `--self-test` exit 0.
