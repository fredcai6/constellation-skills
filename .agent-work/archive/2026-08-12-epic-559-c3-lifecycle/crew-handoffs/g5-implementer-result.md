# Implementation Result

## Assigned gate
`g5-implement` — "the two carried findings"

## Completed slice
1. `scripts/generate_spine.py`'s `_cond_faults`: a new spec-shape fault `spec-not-yet-written-not-bool`
   refuses a `pytest` condition's `not_yet_written` field when it is present with a non-`bool` value,
   before `compile_condition` or the probe ever read it. Also fixed the missing `newline="\n"` on the
   compiled-spine write in `main()`.
2. `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` sections 4, 7, and 10 reconciled against
   the generator's current source (post-g4, post-this-gate).

## Scope
**Files changed:**
- `scripts/generate_spine.py` — `_cond_faults` gains the `spec-not-yet-written-not-bool` guard;
  `main()`'s `Path(args.out).write_text(...)` gains `newline="\n"`.
- `tests/test_generate_spine.py` — new `TestNotYetWrittenTypeGuard` class (12 tests).
- `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` — sections 4, 7 rewritten; section 10
  verified unchanged.
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`), never hand-edited.

**Specific exclusions touched:** no. `scripts/spine_lifecycle.py`, `scripts/mcp_spine_server.py`,
`scripts/validate_spine.py`, `checklist_engine.py`'s on-disk format, `settings.json`, `.mcp.json`,
`docs/agents/*`, `skills/**` are all untouched.

## Behavior changed
Yes. A spec author who writes `not_yet_written = "false"` (or any non-bool value) on a `pytest`
postcondition now gets a named, spec-shape-time refusal (`spec-not-yet-written-not-bool`) instead of
silently losing the check to `compile_condition`'s bare-truthiness read. `not_yet_written = true`/`false`
and the field omitted are unchanged. **Nothing shipped moves**: `specs/implementer.spine.toml` and
`specs/reviewer.spine.toml` use no `not_yet_written`, and the sweep is still exactly 23 (evidence below).

## Map Impact
- **Structural anchors touched:** `struct:generator` — `scripts/generate_spine.py`, module — `_cond_faults`
  gained the new guard; no new top-level symbol (the fault lives inside the existing pytest-kind branch).
- **Capabilities added/changed/affected:** none new — this closes a gap in the existing
  `capability:not-yet-written-declaration` (TDD-red pytest conditions), it does not add a capability.
- **Constraints/assumptions touched:** `decision:not-yet-written-refuses-not-coerces`
  (LIFECYCLE_CONTRACT.md section 7, deviation 1) — now shipped, not just decided.
- **Claims/evidence produced:** `claim:suite-green` updated to 2932 passed, 3 skipped, 1121 subtests (up
  from the 2920 pre-g5 baseline — 12 new tests). `claim:sweep-23` reconfirmed unchanged.
- **Trust limitations / drift found:** none new beyond what's already floated in LIFECYCLE_CONTRACT.md
  section 7b (`validate_spine.py` has no `not_yet_written` concept — restated below, unchanged, not a
  change to make).
- **Triage candidates:** none beyond what LIFECYCLE_CONTRACT.md section 7b already names.

## Test mode
**Required:** test-first (TDD red→green), per the handoff's close criteria.
**Satisfied:** yes — see TDD evidence below.

## Evidence

### 1. All three VIOLATING and all three INNOCENT fixtures, run directly against `spec_shape_faults`,
`compile_condition`, and `_probe_pytest`

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python - <<'PYEOF'
import sys; sys.path.insert(0, "scripts"); import generate_spine as gs

def cond(**kw):
    d = {"id": "c1", "statement": "tests pass", "kind": "pytest", "selector": "Door or Tie", "min_collect": 4}
    d.update(kw); return d

def spec_with(cond_):
    return {"work_id": "w1", "type": "gated", "config_ref": "docs/agents/engine-config.json",
            "gate": [{"id": "m1", "title": "do it", "imperative": "do the thing", "postconditions": [cond_]}]}

cases = [
    ("VIOLATING not_yet_written = 'false' (TOML string)", cond(not_yet_written="false")),
    ("VIOLATING not_yet_written = 'true' (TOML string)", cond(not_yet_written="true")),
    ("VIOLATING not_yet_written = 1 (int)", cond(not_yet_written=1)),
    ("INNOCENT not_yet_written = true", cond(not_yet_written=True)),
    ("INNOCENT not_yet_written = false", cond(not_yet_written=False)),
    ("INNOCENT not_yet_written omitted", cond()),
]
for label, c in cases:
    faults = gs.spec_shape_faults(spec_with(c), repo_root=gs.Path("."))
    print(f"{label}: faults={[f.code for f in faults]}")
PYEOF
VIOLATING not_yet_written = 'false' (TOML string): faults=['spec-not-yet-written-not-bool']
VIOLATING not_yet_written = 'true' (TOML string): faults=['spec-not-yet-written-not-bool']
VIOLATING not_yet_written = 1 (int): faults=['spec-not-yet-written-not-bool']
INNOCENT not_yet_written = true: faults=[]
INNOCENT not_yet_written = false: faults=[]
INNOCENT not_yet_written omitted: faults=[]
```

Innocent-path behavior unchanged (compiled shape and probe result, for all three INNOCENT cases):

```
not_yet_written=true  -> check: None | statement has NOT YET WRITTEN: True
not_yet_written=false -> check kind: command
omitted                -> check kind: command
not_yet_written=true probe -> faults: [] undecidable: [('undecidable-pytest-not-yet-written', False)]
not_yet_written=false probe -> faults: ['probe-pytest-below-min-collect'] undecidable: []
not_yet_written omitted probe -> faults: ['probe-pytest-below-min-collect'] undecidable: []
```

This directly satisfies close criteria 1–4: the two TOML-string VIOLATING cases and the int-`1`
VIOLATING case are all refused by `spec-not-yet-written-not-bool` before `compile_condition` or
`_probe_pytest` run; `not_yet_written = true` still compiles to `check: null` and still emits the
non-blocking `undecidable-pytest-not-yet-written` note; `= false` and omitted both still take the
strict probe path (`probe-pytest-below-min-collect` on the same nonsense selector both ways).

### 2. The mechanical enumeration of fault codes for section 7 — the command and its full output, plus
the count

```
$ grep -oE '"spec-[a-z0-9-]+"' scripts/generate_spine.py | tr -d '"' | sort -u
spec-all-qualitative-postconditions
spec-artifact-missing-match
spec-config-ref-not-json
spec-dispatch-missing-field
spec-dispatch-undeclared
spec-dispatch-unresolved-parent
spec-duplicate-condition-id
spec-duplicate-gate-id
spec-empty-because
spec-gated-missing-postconditions
spec-malformed-claim
spec-missing-field
spec-non-integer-field
spec-not-yet-written-not-bool
spec-reserved-id
spec-shipped-session-specific-parent
spec-unknown-check-kind
```

**Count: 17** distinct `spec-*` fault-code string literals in the module. **16** are reachable through
`spec_shape_faults()` (the function `main()` calls before `compile_spec` ever runs); the 17th,
`spec-shipped-session-specific-parent`, is emitted by a separate function
(`shipped_spec_session_specific_parent_faults`) deliberately never wired into `spec_shape_faults` or
`main()` — confirmed by grepping its only call sites: the two `TestShippedSpecParentGuard` test methods.
`python scripts/generate_spine.py <spec.toml>` itself can never raise it.

### 3. The `DESIGN_NOTE.md` diff, with a one-line reason per changed claim

- **Section 4, `qualitative` paragraph** — added one sentence cross-referencing the pytest
  `not_yet_written` declaration's identical `check: null` shape. *Reason: the handoff named this
  paragraph as needing to "account for what `not_yet_written` does," and it previously said nothing
  about the pytest field at all.*
- **Section 4, `pytest` paragraph** — added `not_yet_written` to the field list, and a new paragraph
  documenting: what it declares, that it compiles to `check: null` (never previously stated anywhere in
  the note), what the probe does instead (non-blocking `undecidable-pytest-not-yet-written`), and the
  new type guard. *Reason: the note never said `not_yet_written` compiles to `check: null` anywhere —
  the exact gap the handoff named.*
- **Section 7** — replaced the fault-code list wholesale with a mechanically-enumerated, complete one
  (17 codes, count stated, enumeration command shown) and added one-line explanations for the six codes
  that were previously undocumented (`spec-non-integer-field`, `spec-not-yet-written-not-bool`,
  `spec-artifact-missing-match`, `spec-dispatch-missing-field`, `spec-dispatch-unresolved-parent`,
  `spec-dispatch-undeclared`). *Reason: the prior list named only 10 of the 16 codes
  `spec_shape_faults()` can raise — an under-inclusive list presented as complete, which is exactly the
  failure this wave is watching for.* Also fixed two consecutive "That last one" back-references that,
  read together, pointed at the wrong fault code (the second one's content — `config_ref`/JSON — belongs
  to `spec-config-ref-not-json`, not `spec-malformed-claim`, the literal last item in the list it
  appeared to continue); both are now named explicitly. *Reason: ambiguous pronoun reference, found while
  reconciling this section, unrelated to but adjacent to the enumeration work.*
- **Section 10** — **no changes.** Verified each of the four rows against the current source
  (`_compile_pytest` still `shlex.quote`s the selector; `_compile_script` still never imports its
  target and `_add_argument_literals` is unchanged; the population probe still executes the compiled
  command string itself). None of g4's dispatch additions or this gate's `not_yet_written` fix touch
  the `pytest`/`script`/`population` kind logic the table describes, so every row still holds as
  written. *Reason for no diff: per the handoff, "if a claim is right, leave it exactly as it is."*

### Confirmatory

```
$ cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2932 passed, 3 skipped, 1121 subtests passed in 117.50s (0:01:57)
```
(Baseline before this gate: 2920 passed, 3 skipped, 1121 subtests — 12 net new tests, everything else
unchanged. `map/INDEX.md` needed one regeneration mid-gate, after the source edit, to stay green against
`test_map_tree_freshness_root_index_matches_a_fresh_build` — see Workflow Feedback.)

```
$ cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
23
```
**Result:** `23` — unchanged, as required. Neither shipped spec uses `not_yet_written`.

## TDD evidence, if required

**`TestNotYetWrittenTypeGuard` (tests/test_generate_spine.py):**
- Failing test observed: 5/12 red before `_cond_faults` gained the guard —
  `test_violating_is_refused` (all three VIOLATING labels), `test_fault_names_field_gate_condition_and_type`,
  `test_pre_fix_repro_is_now_caught_before_compile_condition_ever_sees_it`. The other 7 (INNOCENT +
  regression-pin tests for the unchanged paths) passed from the start, by design — they pin behavior
  the fix must not touch.
- Passing test observed: `12 passed` after the guard landed
  (`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q -k
  TestNotYetWrittenTypeGuard tests/test_generate_spine.py`).
- Refactor while green: no refactor needed; full `test_generate_spine.py` (171 tests) stayed green.

## Docs/contracts touched
- `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` — sections 4 and 7 corrected (diff and
  reasons above); section 10 verified, left unchanged.

## Assumptions
- The fault code name `spec-not-yet-written-not-bool` was not specified by the handoff (which named the
  finding but not a code string); chosen to match the existing naming convention
  (`spec-non-integer-field`, `spec-dispatch-missing-field`) — a `spec-<field-or-concept>-<problem>`
  shape naming the field and the defect class.
- The guard is scoped to `kind == "pytest"` conditions only (where `not_yet_written` is actually read).
  A non-`pytest` condition carrying a stray `not_yet_written` key is inert (never read by
  `compile_condition` or any probe) and is left unflagged, matching the handoff's framing of the finding
  as specifically about the two `pytest`-kind call sites.

## Stop conditions hit
None. Every check landed; no constraint was violated; no third attempt was needed on any check.

## Out-of-scope observations
None beyond what LIFECYCLE_CONTRACT.md section 7b and the handoff's exclusions already name
(`validate_spine.py` has no `not_yet_written` concept — a legitimately-TDD-red check and a
permanently-vacuous one are indistinguishable to the oracle; not a change to make here).

## Workflow Feedback

- **Handoff gaps:** none blocking. The handoff's "Read first" list and close criteria mapped cleanly
  onto the work; no field was missing or contradictory.
- **Context rediscovered:** the environment's inherited `SPINE_FILE`/`SPINE_SESSION` pointed at the
  Commander's own outer `execute.json` spine (`constellation/epic-559/c3-lifecycle/execute/commander`),
  not a spine scoped to this g5 dispatch — `spine_status` returned the Commander's own `execute` gate
  instructions (dispatch crews via `run_crew.py`, drive `execute.json`, etc.), not anything about g5.
  This is the same finding g4's result already recorded; I independently confirmed it by reading
  `STATE_NOTE.md` (which showed this crew was launched via `run_crew.py --gate g5 --role implementer`)
  before acting on the inherited MCP door binding, and drove my own work through a locally-authored
  `IMPLEMENTER_PLAN`-shaped file
  (`.agent-work/epic-559/c3-lifecycle/crew-runs/g5-implementer-attempt-1-plan.json`) via the CLI
  `checklist_engine.py`, matching the g4 precedent. This is now a repeated pattern across at least two
  gates in this run and is worth fixing at the `run_crew.py`/MCP-server-launch level so future crews
  don't have to rediscover it.
  Also rediscovered (matching g4): `map/*` is gitignored except `map/INDEX.md`, and
  `python -m scripts.code_map build` picked up my source edit and correctly regenerated a diff-only
  `map/INDEX.md` — the full suite briefly failed on `test_map_tree_freshness_root_index_matches_a_fresh_build`
  until I ran the regen, which the handoff's allowed scope already anticipated (`map/` — regenerated,
  never hand-edited) but is easy to forget mid-gate since it only surfaces at the very end via the full
  suite, not the targeted test run.
- **Instructions improvised around:** same as g4 — the constellation-implementer skill's default posture
  ("A dispatched crew's spine is bound for you... `spine_status` is your first call") did not fit; fell
  back to the skill's "no spine bound" branch.
- **What would have made this easier:** nothing structural. Reading LIFECYCLE_CONTRACT.md section 7b
  before section 7 (as the handoff's "Read first" list orders them) made the `not_yet_written` finding's
  full severity ("the gate does not merely misread a declaration — it silently loses its check
  entirely") clear before touching any code, which shaped the fault message to name that mechanism
  explicitly rather than just "wrong type."

## Return status
`complete`
