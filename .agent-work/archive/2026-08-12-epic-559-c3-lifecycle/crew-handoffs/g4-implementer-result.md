# Implementation Result

## Assigned gate
`g4-implement` — "the dispatch is emitted, not remembered"

## Completed slice
`[[gate.dispatch]]` (LIFECYCLE_CONTRACT.md section 5): `role` and `model` required per entry, `parent`
filled from the spec's own top-level `parent` (never declared per entry). Three new spec-shape faults,
refused before any probe. `_compile_gate` renders `directives.dispatch` and injects one `command`-kind
postcondition per entry, reading `crew-runs.json` through a new `scripts/verify_declared_dispatch.py`
that reuses `run_crew.py`'s own registry loading and `is_abandoned`.

## Scope
**Files changed:**
- `scripts/generate_spine.py` — `_dispatch_faults`, the `c-dispatch-<n>` reserved-id family,
  `_compile_dispatch_entry`, wiring into `_compile_gate`/`compile_spec` (threading `work_id` through).
- `scripts/verify_declared_dispatch.py` (new) — the oracle the injected postcondition shells out to.
- `tests/test_generate_spine.py` — `TestDeclaredDispatchSpecShapeFaults`, `TestDeclaredDispatchEmission`,
  `TestDeclaredDispatchDrivenThroughEngine`; extended `_gate()`/added `_dispatch()` fixture helpers.
- `tests/test_declared_dispatch.py` (new) — `TestCheckDeclaredDispatch`, `TestMainCLI`.
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`), never hand-edited.

**Specific exclusions touched:** no. `scripts/spine_lifecycle.py`, `scripts/mcp_spine_server.py`,
`scripts/validate_spine.py`, `checklist_engine.py`'s on-disk format, `settings.json`, `.mcp.json`,
`docs/agents/*`, `skills/**`, `DESIGN_NOTE.md`, and the `not_yet_written`/`newline="\n"` carried findings
at `generate_spine.py:424/673/910` are all untouched.

## Behavior changed
Yes. A spec author can now declare `[[gate.dispatch]]` on a gate; the generator emits the crew's identity
(`role`, `model`, `parent`) into the gate's `directives.dispatch` and injects a machine-checked
postcondition that refuses `advance` unless `crew-runs.json` actually recorded that identity for a
non-abandoned attempt. **Nothing shipped moves**: `specs/implementer.spine.toml` and
`specs/reviewer.spine.toml` declare no dispatch, and the sweep is still exactly 23 (evidence below).

## Map Impact
- **Structural anchors touched:** `struct:generator` — `scripts/generate_spine.py`, module — gained
  `_dispatch_faults`, `_compile_dispatch_entry`, and the `dispatch`-aware `_compile_gate`/`compile_spec`
  signatures (now threading `work_id`). New module `scripts/verify_declared_dispatch.py` (3 entities,
  mapped: `find_candidates`, `check_declared_dispatch`, `main`).
- **Capabilities added/changed/affected:** `capability:declared-dispatch` — the generator emits parent and
  model so they cannot be forgotten; shipped exactly as forecast in the g4 anchor, now a checked property
  instead of a plan line.
- **Constraints/assumptions touched:** `decision:dispatch-is-checked-data` (a command-kind postcondition
  reads `crew-runs.json`) — resolved from `@grade: guess` to settled/measured: the wrong-parent fixture in
  `TestDeclaredDispatchDrivenThroughEngine` is the pin.
- **Claims/evidence produced:** `claim:suite-green` updated to 2920 passed, 3 skipped, 1121 subtests on
  this branch (up from the 2884/3/1121 baseline — 36 new tests). `claim:sweep-23` reconfirmed unchanged.
- **Trust limitations / drift found:** none new. The repo still carries no Cartographer packet map
  (confirmed by MISSION_FRAME.md's own confidence flag); this section is a re-runnable measurement, not a
  map anchor.
- **Triage candidates:** `spec-dispatch-undeclared`'s textual-marker detection (see "What
  spec-dispatch-undeclared does and does not close" below) is a residual, not a defect — closing it fully
  needs the engine to know what a dispatch is, named as out of scope in both the handoff and
  LIFECYCLE_CONTRACT.md section 5. No new triage candidate beyond what the contract already names.

## Test mode
**Required:** test-after allowed (no explicit mode named in the handoff; the close criteria are the spec,
matching g2's precedent).
**Satisfied:** yes, with genuine TDD red→green for the two riskiest slices (spec-shape faults, and the
emission wiring into `_compile_gate`/`compile_spec`) — see TDD evidence below. `scripts/verify_declared_dispatch.py`
itself was written test-after (see Workflow Feedback); its dedicated test file passed 11/11 on first run.

## Evidence

### 1. Wrong-parent fixture (close criterion 4) — the registry entry, the command actually run, its
non-zero exit naming the offending entry

Registry entry (`crew-runs.json`), a realistic Admiral-looking session id, not garbage:
```json
[
  {
    "crew_id": "constellation/epic-559/c3-lifecycle/g4/implementer/attempt-1",
    "session_name": "constellation/epic-559/c3-lifecycle/g4/implementer/attempt-1",
    "work_id": "epic-559/c3-lifecycle",
    "gate": "g4",
    "role": "implementer",
    "parent": "admiral-epic-418-followon",
    "model": "sonnet",
    "status": "completed",
    "abandoned": false
  }
]
```

The injected postcondition's command, run exactly as the engine would run it:
```
$ cd /tmp/g4_fake_repo && python scripts/verify_declared_dispatch.py --root . --work-id epic-559/c3-lifecycle --gate g4 --role implementer --parent constellation/epic-559/c3-lifecycle/execute/commander/attempt-1 --model sonnet
gate='g4' role='implementer' declared parent='constellation/epic-559/c3-lifecycle/execute/commander/attempt-1' model='sonnet', but no non-abandoned entry matches -- found: constellation/epic-559/c3-lifecycle/g4/implementer/attempt-1 (parent='admiral-epic-418-followon', model='sonnet')
exit: 1
```

The same fixture driven through the real engine (`tests/test_generate_spine.py::TestDeclaredDispatchDrivenThroughEngine::test_wrong_parent_fails_the_compiled_command_and_advance`):
`checklist_engine.advance()` raises `EngineError` naming the unmet postcondition id `c-dispatch-0`.

### 2. ACCEPTED_FALSE_ALARM — an abandoned wrong-parent entry does NOT block (close criterion 8, populated
not merely named)

Registry: the same wrong-parent entry, now `"abandoned": true`, plus a second, correctly-parented attempt:
```json
[
  {
    "crew_id": "constellation/epic-559/c3-lifecycle/g4/implementer/attempt-1",
    "parent": "admiral-epic-418-followon", "model": "sonnet",
    "status": "abandoned", "abandoned": true, "gate": "g4", "role": "implementer"
  },
  {
    "crew_id": "constellation/epic-559/c3-lifecycle/g4/implementer/attempt-2",
    "parent": "constellation/epic-559/c3-lifecycle/execute/commander/attempt-1", "model": "sonnet",
    "status": "completed", "abandoned": false, "gate": "g4", "role": "implementer"
  }
]
```
```
$ cd /tmp/g4_fake_repo && python scripts/verify_declared_dispatch.py --root . --work-id epic-559/c3-lifecycle --gate g4 --role implementer --parent constellation/epic-559/c3-lifecycle/execute/commander/attempt-1 --model sonnet
constellation/epic-559/c3-lifecycle/g4/implementer/attempt-2 matches declared dispatch (gate='g4' role='implementer' parent='constellation/epic-559/c3-lifecycle/execute/commander/attempt-1' model='sonnet')
exit: 0
```
A naive checker that ignored `abandoned` would flag this; `check_declared_dispatch`'s `find_candidates`
filters `is_abandoned(entry)` (imported from `run_crew.py`, never re-implemented) before matching, so it
does not. Same fixture driven through the real engine
(`test_abandoned_wrong_parent_entry_does_not_block_advance`): `advance()` succeeds, gate reaches
`complete`.

### 3. A real `generate_spine.py` run against a fixture spec carrying `[[gate.dispatch]]`

Fixture spec (`/tmp/g4_dispatch_demo.spine.toml`):
```toml
work_id    = "epic-559/c3-lifecycle"
type       = "gated"
config_ref = "docs/agents/engine-config.json"
parent     = "constellation/epic-559/c3-lifecycle/execute/commander/attempt-1"

[[gate]]
id    = "g4"
title = "demo: declared dispatch"
imperative = "dispatch an implementer crew through run_crew.py"

  [[gate.dispatch]]
  role  = "implementer"
  model = "sonnet"

  [[gate.postconditions]]
  id = "c1"
  statement = "demo postcondition"
  kind = "qualitative"
  because = "this is a fixture demo, not a real gate"

  [[gate.postconditions]]
  id = "c2"
  statement = "the two shipped role specs still exist"
  kind = "population"
  root = "specs"
  glob = "*.toml"
  expected = 2
```
```
$ python scripts/generate_spine.py /tmp/g4_dispatch_demo.spine.toml --out /tmp/g4_dispatch_demo.spine.json --root .
wrote /tmp/g4_dispatch_demo.spine.json
exit: 0
```

Emitted `directives.dispatch`:
```json
[
  {
    "role": "implementer",
    "model": "sonnet",
    "parent": "constellation/epic-559/c3-lifecycle/execute/commander/attempt-1"
  }
]
```

Injected postcondition (`c-dispatch-0`):
```json
{
  "id": "c-dispatch-0",
  "statement": "declared dispatch -- role='implementer' model='sonnet' parent='constellation/epic-559/c3-lifecycle/execute/commander/attempt-1' must be recorded by a non-abandoned crew-runs.json entry for gate 'g4' role 'implementer' before this gate can advance",
  "check": {
    "kind": "command",
    "command": "cd <repo-root> && python scripts/verify_declared_dispatch.py --root . --work-id epic-559/c3-lifecycle --gate g4 --role implementer --parent constellation/epic-559/c3-lifecycle/execute/commander/attempt-1 --model sonnet"
  },
  "satisfied": false
}
```

### Confirmatory

New fault codes (spec-shape, refused before any probe):
`spec-dispatch-missing-field`, `spec-dispatch-unresolved-parent`, `spec-dispatch-undeclared`.

Command-kind, never artifact, asserted directly
(`TestDeclaredDispatchEmission::test_injected_postcondition_is_command_kind_never_artifact`).

```bash
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** `2920 passed, 3 skipped, 1121 subtests passed` (baseline: 2884 passed, 3 skipped, 1121
subtests — 36 net new tests, everything else unchanged).

```bash
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```
**Result:** `23` — unchanged. The two shipped specs declare no dispatch.

## TDD evidence, if required

**Slice 1 — spec-shape faults (`TestDeclaredDispatchSpecShapeFaults`):**
- Failing test observed: 10/14 red (`AssertionError`: fault codes `spec-dispatch-missing-field` /
  `spec-dispatch-unresolved-parent` / `spec-dispatch-undeclared` / `spec-reserved-id` absent from
  `spec_shape_faults`'s output) before `_dispatch_faults` existed.
- Passing test observed: `14 passed` after `_dispatch_faults` + the `c-dispatch-<n>` reserved-id check
  landed.
- Refactor while green: no refactor needed; full `test_generate_spine.py` (148 tests) stayed green.

**Slice 2 — emission (`TestDeclaredDispatchEmission`, `TestDeclaredDispatchDrivenThroughEngine`):**
- Failing test observed: 10/10 red (`StopIteration` — no postcondition with id `c-dispatch-0`, no
  `directives.dispatch` key) before `_compile_dispatch_entry` and its `_compile_gate` wiring existed.
- Passing test observed: `11 passed` after the emission landed.
- Refactor while green: no refactor needed.

## Docs/contracts touched
- None. `DESIGN_NOTE.md` and `LIFECYCLE_CONTRACT.md` are read-only inputs per the exclusions; the new
  fault codes are listed below for g5 to fold into `DESIGN_NOTE.md` section 7.

## Assumptions
- The `c-dispatch-<n>` reserved-id family (analogous to `RESERVED_CONDITION_ID`/`c-escalation`) was not
  explicitly named in the handoff, but is necessary for correctness: without it, an author's own
  postcondition id could silently collide with an injected dispatch postcondition the same way an
  unprotected `c-escalation` could before section 6 shipped. Added and tested
  (`test_reserved_dispatch_condition_id_is_refused`), reusing the existing `spec-reserved-id` fault code
  rather than minting a fourth one — the handoff's close criteria name exactly three new codes, and this
  is a defensive extension of an existing one, not a new fault family.
- A malformed `dispatch` shape (`[gate.dispatch]` — a single table — instead of `[[gate.dispatch]]`) is
  refused via the existing `spec-dispatch-missing-field` code rather than a new one, mirroring how
  `spec-malformed-claim` handles the analogous `[[gate.claim]]` mistake but reusing rather than minting,
  since the handoff names exactly three dispatch fault codes.

## Stop conditions hit
None. Every check landed; no constraint was violated; no third attempt was needed on any check.

## Out-of-scope observations
None beyond what LIFECYCLE_CONTRACT.md section 5 and the handoff already name as residual (see below).

## Workflow Feedback

- **Handoff gaps:** none blocking. The handoff's close criteria (10 numbered items) mapped cleanly onto
  test classes; no field was missing or contradictory.
- **Context rediscovered:** the environment's inherited `SPINE_FILE`/`SPINE_SESSION` pointed at the
  Commander's own outer `execute.json` spine (`constellation/epic-559/c3-lifecycle/execute/commander`),
  not a spine scoped to this g4 dispatch — the actual gate tracking for g4 lives in the Commander's
  separate `GATE_PLAN.json` (item `g4-implement`), which this crew does not drive. I confirmed this by
  reading `GATE_PLAN.json` directly rather than acting on the inherited MCP door binding, and drove my own
  work through a locally-authored `IMPLEMENTER_PLAN`-shaped file
  (`.agent-work/epic-559/c3-lifecycle/crew-runs/g4-implementer-attempt-1-plan.json`) via the CLI
  `checklist_engine.py`, matching the pattern already used by `g1-implementer-attempt-2-plan.json`. Also
  had to discover, by reading `.gitignore`, that `map/*` is gitignored except `map/INDEX.md` — the
  per-module `map/<pkg>.<mod>/INDEX.md` files `code_map build` writes are never committed, so "regenerate
  map/" in practice means "regenerate, then `git add map/INDEX.md` only."
  Also discovered that `python -m scripts.code_map build` enumerates via `git ls-files`
  (`scripts/code_map/discovery.py`), so a brand-new file must be `git add`ed BEFORE the map regen picks it
  up — my first regen (before committing) silently missed both new modules.
- **Instructions improvised around:** the constellation-implementer skill's default posture ("A dispatched
  crew's spine is bound for you... spine_status is your first call") did not fit this dispatch — the bound
  spine was the Commander's own outer spine, not a g4-scoped one — so I fell back to the skill's "no spine
  bound" branch (author + drive my own `IMPLEMENTER_PLAN`-shaped plan via the CLI engine) rather than
  attempting to drive the Commander's `execute` item myself, which was clearly out of this crew's
  authority.
- **What would have made this easier:** nothing structural. The handoff's explicit "Read first" list
  (contract section, design note sections, and the four named `generate_spine.py` symbols) was exactly the
  right amount of context and needed no expansion.

## What `spec-dispatch-undeclared` does and does not close

Stated as plainly as LIFECYCLE_CONTRACT.md section 5 states it, because the handoff asked for honesty here
specifically: **detection is textual.** The fault fires when a gate declares no `[[gate.dispatch]]` and its
`imperative` string contains one of three literal markers — `run_crew.py`, `constellation-implementer`,
`constellation-reviewer`. An imperative phrased without any of those three strings (e.g. "hand this to an
implementer crew", tested in `test_imperative_with_none_of_the_three_markers_stays_invisible`) is invisible
to this check and compiles clean even though it dispatches a crew in prose.

**What it closes:** the exact defect the launch order names — an author who writes a dispatch imperative
using one of the corpus's own conventional invocation phrases and forgets to also declare
`[[gate.dispatch]]`. That author's mistake is now refused at generation time instead of surviving to
`advance()` where `crew-runs.json` might quietly carry the wrong parent.

**What it does not close:** any dispatch phrased without those three markers stays completely undetected —
no fault, no injected postcondition, silent pass-through exactly as before this change. The residual is the
same shape as the launch order's own open question, restated in code: the defect moves from "a crew
forgets `--parent`, invisible for a wave" to "an author phrases a dispatch with none of three markers,
invisible for a wave" — strictly smaller, never closed. Closing it fully needs the engine itself to know
what a dispatch is (a structural, not textual, definition), which is an engine change outside a Commander's
latitude and explicitly out of scope for this gate.

## New fault codes (for g5's `DESIGN_NOTE.md` section 7)

- `spec-dispatch-missing-field` — a declared `[[gate.dispatch]]` entry missing `role` or `model` (also
  covers a malformed `dispatch` shape, e.g. `[gate.dispatch]` instead of `[[gate.dispatch]]`).
- `spec-dispatch-unresolved-parent` — a dispatch declared while the spec's own top-level `parent` is
  absent; refused rather than emitting a dispatch naming `"unknown"`.
- `spec-dispatch-undeclared` — a gate whose imperative names a dispatch marker (`run_crew.py`,
  `constellation-implementer`, `constellation-reviewer`) but declares no `[[gate.dispatch]]`. Textual
  detection only — see the section above.

(No fourth code: the reserved-id collision on `c-dispatch-<n>` and the malformed-shape case both reuse the
existing `spec-reserved-id` and `spec-dispatch-missing-field` codes respectively, per the Assumptions
section above.)

## Return status
`complete`
