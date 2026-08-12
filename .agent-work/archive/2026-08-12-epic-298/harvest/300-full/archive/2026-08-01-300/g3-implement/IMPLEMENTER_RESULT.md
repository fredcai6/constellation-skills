# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-implement` (issue #300, epic-298)

## Completed slice
Four bounded deliverables, all shipped: (1) a mechanical lint (`scripts/verify_context_declaration.py`)
pinning every declared `context_refs` path against its own task's `imperative` prose, with a genuine
negative test (`test_divergent_declaration_is_rejected`) proving it rejects a divergent fixture; (2) one
schema-table row for `context_refs` in `docs/CHECKLIST_SCHEMA.md`; (3) a narrative section in
`docs/CHECKLIST_ENGINE_DESIGN.md` describing the manifest beside the existing state-projection section;
(4) `.agent-work/300/OBLIGATIONS-301.md` (two explicit halves: "may rely on" / "may not") plus a shape test
(`test_produced_manifest_is_assignable_to_episode_context_field_untransformed`) in
`tests/test_context_manifest.py`.

## Scope
**Files changed:**
- `scripts/verify_context_declaration.py` (new)
- `tests/test_context_declaration_lint.py` (new)
- `tests/fixtures/context_declaration_lint.json` (new)
- `docs/CHECKLIST_SCHEMA.md` (one Task-table row added)
- `docs/CHECKLIST_ENGINE_DESIGN.md` (one narrative section added, after "Answerability", before "Evidence")
- `tests/test_context_manifest.py` (one shape test class added)
- `.agent-work/300/OBLIGATIONS-301.md` (new, gitignored local artifact)

**Specific exclusions touched:** no. `scripts/context_manifest.py` and
`skills/commander/templates/COMMANDER_SPINE.template.json` were read but never edited;
`scripts/checklist_engine.py`, `scripts/verify_skip_guard.py`, `.github/` untouched; no committed
`CONTEXT_PROJECTION.json` / `scripts/context_projection.py` built; `verify_spec_confirmed.py` untouched;
`.agent-work/LESSONS.md` never hand-edited.

## Behavior changed
Yes, additively: a new CI-runnable lint now exists (not yet wired into `.github/workflows/ci.yml` — that
wiring was not in this gate's scope), and two docs gained explicit, checkable descriptions of a feature
that previously existed only in code and in the design-it-twice comparison. No existing runtime behavior
changed — `scripts/context_manifest.py` was not touched.

## Map Impact
- **Structural anchors touched:** `scripts/verify_context_declaration.py` — new module, sibling of the
  existing `scripts/verify_*.py` family; reads (never imports) the `context_refs` shape documented by
  `scripts/context_manifest.py`.
- **Capabilities added/changed/affected:** a mechanical guard now exists that keeps a spine step's
  `context_refs` declaration from silently narrowing away from its own `imperative` prose. One-directional
  by design (documented in the module docstring): it cannot detect the prose naming a file the declaration
  omits.
- **Constraints/assumptions touched:** `docs/CHECKLIST_SCHEMA.md`'s Task table now documents
  `context_refs` as a first-class, optional field, matching what `g1-implement` already shipped in code.
- **Decision candidates / resolved decisions:** none forced here — the load-bearing design choices
  (declaration shape, no committed artifact, prose stays) were settled in `g1` / `DIT-COMPARISON.md`; this
  gate only documented and pinned them.
- **Claims/evidence produced:** the negative-test proof that the lint distinguishes a genuinely divergent
  declaration from a clean one (see Evidence below), and that the shipped `COMMANDER_SPINE.template.json`
  declaration is clean against its own prose.
- **Triage candidates:** the lint is not yet wired into `.github/workflows/ci.yml` as a CI step — that
  wiring was explicitly excluded from this gate's scope (`.github/` is a listed exclusion) and is a
  candidate for a follow-up issue/gate, not raised here as a defect.

## Test mode
**Required:** `test-first` (TDD) for the lint and its negative test, per the handoff's explicit
"the negative test is the load-bearing one" framing and the skill's TDD-when-test-mode-requires-it rule;
`evidence-only`/inspection for the schema row, design-doc narrative, and obligations doc (no test surface);
`test-after`/inspection for the shape test (asserts an existing, untouched producer's output shape — no
production code changed).
**Satisfied:** yes. RED observed for the lint (9/9 tests failed with `FileNotFoundError` before
`scripts/verify_context_declaration.py` existed), then GREEN (9/9 passed) after implementation. The shape
test was written directly against the real producer and passes.

## Evidence

### 1. TDD RED — lint tests fail before the script exists
```
$ python -m pytest tests/test_context_declaration_lint.py -q
FAILED ...CheckChecklistTests::test_check_checklist_accepts_the_valid_fixture
FAILED ...CheckChecklistTests::test_check_checklist_reports_the_narrowed_away_path
FAILED ...CheckChecklistTests::test_prose_naming_more_than_declared_is_not_flagged
FAILED ...CliTests::test_divergent_declaration_is_rejected
FAILED ...CliTests::test_lint_passes_over_real_shipped_spine_templates
FAILED ...CliTests::test_nonexistent_path_fails_visibly_not_silently
FAILED ...CliTests::test_valid_declaration_is_accepted
FAILED ...DiscoveryTests::test_default_discovery_finds_the_commander_spine_and_passes
FAILED ...DiscoveryTests::test_default_discovery_skips_non_checklist_template_json
FileNotFoundError: [Errno 2] No such file or directory: '...\\scripts\\verify_context_declaration.py'
9 failed in 0.25s
```

### 2. TDD GREEN — same file, after implementation
```
$ python -m pytest tests/test_context_declaration_lint.py -q
.........
9 passed in 0.16s
```

### 3. The negative test is genuinely load-bearing (direct CLI proof, not a proxy)
The fixture `tests/fixtures/context_declaration_lint.json`'s `"divergent"` entry declares
`references/narrowed-away.md` in `context_refs` on the `context` task, while that task's `imperative`
string never mentions it (the other two declared paths, `references/global-everyone.md` and
`docs/agents/GLOSSARY.md`, DO appear verbatim). Run directly against a temp file holding that fixture:
```
$ python scripts/verify_context_declaration.py <tmp>/divergent.json
context_refs declaration diverges from imperative prose:
  - <tmp>/divergent.json: task 'context' declares context_refs path 'references/narrowed-away.md'
    that does not appear verbatim in its own imperative prose
exit=1

$ python scripts/verify_context_declaration.py <tmp>/valid.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders
exit=0
```
`test_divergent_declaration_is_rejected` asserts BOTH the non-zero exit AND that
`"narrowed-away.md"` appears in stderr — guarding against the exact "non-zero for an unrelated
reason" trap the handoff calls out. A companion test, `test_valid_declaration_is_accepted`, proves the
zero-exit path is real (the failure cannot be a probe that always fails).

### 4. Lint passes over the real shipped corpus
```
$ python -m pytest tests/test_context_declaration_lint.py::CliTests::test_lint_passes_over_real_shipped_spine_templates -q
.
1 passed in 0.1x s
```
Runs `main()` against every real `skills/*/templates/*.json` (17 files, incl. 7 non-checklist templates
that discovery/checking correctly skips), asserting exit 0 — i.e. `COMMANDER_SPINE.template.json`'s real
`context` declaration is clean against its real prose.

### 5. Full pre-authored invariant chain (HANDOFF.md), each command + exit code, run VERBATIM
```bash
$ python -m pytest tests/test_context_declaration_lint.py -q                                       # EXIT=0 (9 passed)
$ python -m pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected -q  # EXIT=0 (1 passed)
$ grep -q 'substitute the closest repo doctrine' skills/commander/templates/COMMANDER_SPINE.template.json  # EXIT=0
$ grep -q 'sanctioned degradation' skills/commander/templates/COMMANDER_SPINE.template.json                # EXIT=0
$ grep -qE '^\| *`?context_refs`?' docs/CHECKLIST_SCHEMA.md                                                 # EXIT=0
$ test -f .agent-work/300/OBLIGATIONS-301.md && grep -qi 'may rely' .agent-work/300/OBLIGATIONS-301.md \
    && grep -qi 'may not' .agent-work/300/OBLIGATIONS-301.md                                                # EXIT=0
$ python -m pytest tests/test_context_manifest.py -q -k 'episode_context_field' --no-header                 # EXIT=0 (1 passed)
```
**Self-caught defect, fixed in-gate:** the second command uses a bare node id with no class qualifier.
pytest's `::` node-id selector is an **exact match**, not a substring search — a first draft that nested
`test_divergent_declaration_is_rejected` inside a `CliTests` unittest class made this exact command fail
(`ERROR: not found ... exit=4`), even though the general `-q` run and a `-k` keyword run both passed. Caught
by literally running the pre-authored chain command verbatim rather than trusting an equivalent-looking
substitute, per this repo's own standing lesson about probes failing for the wrong reason. Fixed by moving
`test_divergent_declaration_is_rejected` to a **module-level** pytest function (pytest freely mixes
unittest classes and bare functions in one file); the companion `CliTests.test_valid_declaration_is_accepted`
and the corpus test stayed in the class. Re-verified above with the exact command text — passes.

### 6. Full suite + skip guard (no regression, no new skip)
```
$ python -m pytest tests/ -q --junitxml=junit-report.xml
1221 passed, 2 skipped, 329 subtests passed in 39.75s
EXIT=0
$ python scripts/verify_skip_guard.py junit-report.xml
skip guard ok: 2 skip(s) in report, all match documented allow-tuples
EXIT=0
$ rm -f junit-report.xml
```
1221 passed vs. a pre-change baseline of 1220 — net +1 test-file count is consistent with the tests added
(9 + 4 + 1, minus subtest/class collection differences; verified no test was removed and the 2 skips are
the same two pre-existing, allow-listed ones — no new `skipTest` introduced anywhere).

### 7. Deliverable path check (`git check-ignore`)
```
scripts/verify_context_declaration.py       -> exit 1 (not ignored, committable)
tests/test_context_declaration_lint.py      -> exit 1
docs/CHECKLIST_SCHEMA.md                    -> exit 1
docs/CHECKLIST_ENGINE_DESIGN.md             -> exit 1
tests/test_context_manifest.py              -> exit 1
tests/fixtures/context_declaration_lint.json -> exit 1
.agent-work/300/OBLIGATIONS-301.md          -> exit 0 (gitignored, intentional)
```

## TDD evidence, if required
- Failing test observed: see Evidence §1 above (9/9 FileNotFoundError before `scripts/verify_context_declaration.py` existed).
- Passing test observed: see Evidence §2 above (9/9 passed after implementation).
- Refactor while green: yes, two rounds. (1) A leftover dead-code fragment in `discover_templates()`
  (`(root / "skills").glob(...) if False else ...`) left over from drafting was cleaned to
  `sorted(root.glob(DEFAULT_GLOB))` before the first green run; behavior unchanged, all tests stayed green.
  (2) After first reaching green, running the gate's pre-authored invariant chain **verbatim** (not a
  keyword-equivalent substitute) surfaced that `test_divergent_declaration_is_rejected` nested inside a
  `CliTests` class does not satisfy pytest's exact-match `::` node-id selector; moved it to a module-level
  function (see Evidence §5) and re-ran the full file green again.

## Docs/contracts touched
- `docs/CHECKLIST_SCHEMA.md` — added the `context_refs` Task-table row.
- `docs/CHECKLIST_ENGINE_DESIGN.md` — added the "Context manifest: a second, delivery-shaped projection
  (#300)" section, placed directly after "Answerability: `current` as a complete briefing..." (the
  state-projection section) and before "Evidence: gate on type/shape, not quality".

## Assumptions
- "Where an episode addresses one" in `OBLIGATIONS-301.md` is answered from `scripts/context_manifest.py`'s
  own API (`step` field + `manifest_path()`), since #301's actual episode-record shape does not exist yet
  in this repo to check against directly.

## Stop conditions hit
- None. `scripts/context_manifest.py` was read-only throughout and looks correct against its own
  docstring's stated design (blob-OID identity, no globs, `/run` as the sole exclusion set, metadata-only
  rows) — no defect found, so no stop was warranted.
- `skills/commander/templates/COMMANDER_SPINE.template.json`'s `context` imperative prose was verified
  unchanged (both non-regression greps pass) and was never edited.

## Out-of-scope observations
- The lint is not wired into `.github/workflows/ci.yml`. `.github/` is a listed exclusion for this gate,
  so this is reported as a triage candidate, not fixed here: a follow-up should add
  `python scripts/verify_context_declaration.py` as a CI step alongside the other `verify_*.py` checks.
- `docs/CHECKLIST_SCHEMA.md`'s `context_refs` row uses `\[{root, path, required}\]` shorthand consistent
  with neighboring rows (`\[Condition\]`, `\[string\]`); if the schema doc ever gains a dedicated
  sub-table convention for compound-typed fields (none exists today), this row would be a candidate to
  reformat alongside it — not a defect, just noted for consistency.

## Workflow Feedback
- **Handoff gaps:** none in content, but one worth flagging as a pattern: the handoff names the required
  test id as `test_divergent_declaration_is_rejected` and separately shows the exact invariant command
  `pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected`, but does not
  say the test must be a **module-level** function for that bare node id to resolve (pytest's `::`
  selector is exact-match, not substring). My first draft nested it in a `CliTests` class — a natural
  choice since it is the CLI-level, end-to-end test — and the pre-authored command would have failed had I
  not run it verbatim before closing the gate. Worth a one-line callout in this skill/handoff pattern going
  forward: "when a postcondition names a bare `test_x` node id, the test must be module-level, not a class
  method."
- **Context rediscovered:** none — `HANDOFF.md`, `scripts/context_manifest.py`'s docstring, and
  `.agent-work/300/DIT-COMPARISON.md` together were sufficient; no additional digging was needed to place
  the design-doc section or draft the obligations statement.
- **Instructions improvised around:** none. The `constellation-implementer` skill's plan template and
  `checklist_engine.py` verbs (`claim`/`start`/`attest`/`advance`, `--session-id` required on every
  mutating verb) worked as documented once the `--session-id` requirement was discovered from the first
  refusal message; no workaround needed.
- **What would have made this easier:** the one concrete change above (state the module-level-function
  requirement explicitly wherever a postcondition pins a bare test-function node id) would have caught the
  defect before writing the test the first time, instead of on the verbatim re-run.

## Return status
`complete`
