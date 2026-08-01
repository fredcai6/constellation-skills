# Review Result — g5 (issue-58, FINAL gate)

## Verdict: APPROVE

Commit `2c8074d` on `constellation/issue-58`. Every close criterion reproduced independently; the epic exit criterion (fully green suite, no override) holds. Working tree clean, HEAD at the reviewed commit.

## Per-check findings

**Exit criterion — full suite (reproduced).** `python -m pytest tests/ -q` → **424 passed, 1 skipped, 26 subtests passed, zero failures**. Targeted `tests/test_install_constellation.py -q` → 33 passed, 12 subtests. No red anywhere; the waiver window closes cleanly.

**Vocabulary vs "Chosen design 3", term by term.** All six terms present with their spec-fixed meanings, none diluted:
- *Module* — interface plus implementation; header carries the scale-agnostic note (function / file / service).
- *Interface* — *everything* a caller must know: invariants, ordering, error modes, config, performance envelope — explicitly "not just the type/signature surface."
- *Seam* — where an interface lives; placement is its own decision, not a byproduct of the implementation.
- *Adapter* — a thing satisfying an interface at a seam; "One adapter = a hypothetical seam; two = a real one."
- *Depth / leverage* — behavior per unit of interface a caller must learn ("Deep = much behind little").
- *Locality* — change and verification concentrate in one place rather than scattering across callers.

Both working rules present: *the interface is the test surface* with the wrong-shape consequence ("wanting to reach behind it means the module is the wrong shape"); *the deletion test* with both outcomes (pass-through vs earning-its-keep across N callers). Register matches the file — dense, departures-only, no essay.

**Commander intake line.** One bolded prose line added to the understand-step guidance (hunk is exactly the line + a blank line — no section, no multi-paragraph addition). Semantics match the spec seam paragraph: a shaped-design ask is verified confirmed (`verify_spec_confirmed.py` passes / CONFIRMED marker visible) before any cut; a `UNCONFIRMED — DO NOT CUT` issue is never cut. No other Commander doctrine changed.

**Marker discipline (verified against the script, not by eye).** Scratch fixture ran `verify_spec_confirmed._unconfirmed_marker_hit` on the exact Commander line → `None`; on a genuine standalone marker line → hit; on the full installed `skills/commander/SKILL.md` → `None`. The mention is mid-sentence prose wrapped in backticks, so it cannot `fullmatch` the marker regex. No standalone marker line was introduced anywhere in the diff.

**Installer edits.** Exactly the two dict entries plus the one script-bundle entry the spec names: `SKILL_SCRIPT_BUNDLES["explorer"]` = the six spec scripts (checklist_engine, init_work_area, run_crew, recover_crews, verify_cycles, verify_spec_confirmed); `SKILL_REFERENCE_BUNDLES["explorer"]` = `_GLOBAL_ORCHESTRATOR`, `["prototyper"]` = `_GLOBAL_CREW`; prototyper carries no script bundle. Keys match the consumer convention — `SKILL_*_BUNDLES.get(source_path.name, ())` at lines 163–164, and `source_path.name` is the source skill directory name. No refactors.

**Install tests genuine.** Both new methods call `installer.main(...)` into a temp `target_root` and assert on the *installed* tree — `constellation-explorer/scripts/*.py` land as files, and `constellation-explorer/references/global-everyone.md` contains "Deep-module vocabulary". Not source-tree tautologies. Both installed names are in the expected-skills list.

**Red→green.** Checked out the four files at `HEAD~1` and ran the install suite: exactly two failures — `test_codex_project_scope_installs_all_skills_under_project_codex_skills` and `test_shared_reference_dir_is_not_installed_as_a_skill` — the two the expected-list addition fixes (the skills already discover but weren't in the expected list). Matches the BEFORE evidence. Tree restored, verified clean.

**Dry-run discovery.** `install_constellation.py --dry-run` lists both skills with installed names `constellation-explorer` and `constellation-prototyper`.

**Greps / scope.** `grep -qi deep-module skills/_shared/global-everyone.md` OK; `grep -qi shaped-design skills/commander/SKILL.md` OK. `git show 2c8074d --stat` = the four allowed files only (+52 lines); no excluded path touched; `git status` clean; commit on `constellation/issue-58`.

## Blockers
None.

## Out-of-scope observations
None. Diff is strictly within the allowed four files; the frozen g2–g4 skill trees and the verifier scripts are untouched.

## Workflow feedback (run-specific)
This gate was cheap to review with high confidence precisely because the hard-gate mechanism was already built and unit-tested in prior gates — the marker check reduced to running one existing function against a fixture rather than reasoning about prose. Two things made reproduction fast and worth keeping as a pattern: (1) the handoff naming `_unconfirmed_marker_hit` as the thing to fixture rather than "check the marker looks inline" turned a judgment call into a mechanical yes/no; (2) the red→green claim was verifiable by a single `git checkout HEAD~1 -- <four files>` because the change was tightly scoped to those files — a larger blast radius would have forced a full-suite rerun at HEAD~1. One minor note for future final gates: the diff mixes the installer's script-bundle entry (line 84 region) and reference-bundle entry (line 108 region) in the same commit, so a `--stat`-only glance undercounts the installer change as "one hunk"; reading the full file diff (which the handoff correctly instructed) is what surfaced both. No process defect — just a reminder that `--stat` is insufficient for the installer-edits check.
