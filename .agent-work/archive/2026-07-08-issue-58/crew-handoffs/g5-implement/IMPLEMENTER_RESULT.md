# Implementer Result — g5-implement (issue-58, FINAL gate)

## Completed slice
Wired constellation-explorer and constellation-prototyper into shared doctrine, the Commander understand-step seam, and the installer; extended the install tests. This gate takes `python -m pytest tests/ -q` fully green with no waiver — the epic's exit criterion is met.

## Files changed
- `skills/_shared/global-everyone.md` — appended a dense, departures-only **Deep-module vocabulary** section: the six spec-fixed terms (module, interface, seam, adapter with the one-adapter/two-adapter rule, depth/leverage, locality) plus the two working rules (the interface is the test surface; the deletion test). Single-source file, so it rides the existing reference-bundle mechanism into every installed skill.
- `skills/commander/SKILL.md` — one line-scale addition to the understand guidance (a bolded note directly under the spine step-location table): a shaped-design ask is verified confirmed (`verify_spec_confirmed.py` passes / CONFIRMED marker visible) before work is cut; an `UNCONFIRMED — DO NOT CUT` issue is never cut. Marker mention is inline in prose (surrounded by other words, so `verify_spec_confirmed.py`'s `_unconfirmed_marker_hit` `fullmatch` cannot fire). No other Commander doctrine touched.
- `scripts/install_constellation.py` — two dict entries only: `SKILL_SCRIPT_BUNDLES["explorer"]` = the six-script bundle; `SKILL_REFERENCE_BUNDLES["explorer"] = _GLOBAL_ORCHESTRATOR`, `SKILL_REFERENCE_BUNDLES["prototyper"] = _GLOBAL_CREW`. Prototyper gets no script bundle. Keys are source directory names, matching the dicts' consumer (`SKILL_*_BUNDLES.get(source_path.name, ())`).
- `tests/test_install_constellation.py` — additive: both installed names added to `SKILL_NAMES` (clears the 2 waived failures); `test_explorer_script_bundle_lands_in_installed_skill` (all six scripts land); `test_deep_module_vocabulary_ships_into_installed_skill` (installed explorer's `references/global-everyone.md` carries the vocabulary section — spec Testing pathway 3).

## Evidence

### BEFORE (red — the 2 pre-existing waived failures)
```
FAILED tests/test_install_constellation.py::...test_codex_project_scope_installs_all_skills_under_project_codex_skills
FAILED tests/test_install_constellation.py::...test_shared_reference_dir_is_not_installed_as_a_skill
2 failed, 420 passed, 1 skipped, 20 subtests passed
```
Both failures were the expected-skills list missing `constellation-explorer` and `constellation-prototyper`.

### AFTER — targeted install tests
```
33 passed, 12 subtests passed in 2.00s
```

### AFTER — full suite (epic exit criterion)
```
424 passed, 1 skipped, 26 subtests passed in 9.75s
```
Zero failures. The 1 skipped is pre-existing (unrelated to this gate). Net vs BEFORE: the 2 red tests are green, plus 2 new install-test methods and their subtests.

### Integrate-gate greps
```
GREPS-OK   (grep -qi 'deep-module' skills/_shared/global-everyone.md && grep -qi 'shaped-design' skills/commander/SKILL.md)
```

### Dry-run discovery (both skills, correct installed names)
```
- constellation-explorer: .../skills/explorer -> .../constellation-explorer
- constellation-prototyper: .../skills/prototyper -> .../constellation-prototyper
```
(`--dry-run` is the actual flag per `--help`.)

## Assumptions
- Bundle dict keys are **source directory names** (`explorer`, `prototyper`), confirmed against the consumer `discover_skills` (`SKILL_*_BUNDLES.get(source_path.name, ())`), not installed names. Matches the spec text.
- Placed the Commander intake line as a bolded one-sentence note immediately after the spine step-location table — the tightest fit for "one line-scale addition to the understand-step guidance" without opening a new section.
- The vocabulary-ships assertion targets the explorer's bundled `global-everyone.md` copy as a representative installed skill; the mechanism is skill-agnostic, so one skill proves the reference-bundle path.

## Stop conditions hit
None. No frozen/excluded file needed touching; the installer dict conventions matched the spec exactly; full green was reachable within Allowed Scope.

## Out-of-scope observations
None. All six explorer bundle scripts already existed in `scripts/` (verified before editing); no frozen-file mismatch surfaced.

## Workflow feedback
Run-specific: the handoff's instruction to check `_unconfirmed_marker_hit` before writing the Commander marker line was the right pointer — the check is a `fullmatch` on decoration-stripped lines, so any inline prose mention (marker embedded in a sentence with other words) is provably safe, while a standalone bolded/heading line would fire. Confirming that against source before writing removed all guesswork about the marker-discipline constraint. No friction with scope, evidence, or stop conditions.

## Commit
`2c8074d` on `constellation/issue-58`.
