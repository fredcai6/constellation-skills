# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4-implement` (issue #104, constellation-curator, cluster C)

## Completed slice
Wired `constellation-curator` into the installer: added `SKILL_SCRIPT_BUNDLES["curator"]`
(bundles `curate_corpus.py`), added `SKILL_REFERENCE_BUNDLES["curator"]` (reuses the
existing `_GLOBAL_EVERYONE` bucket), added a `## Constellation Curator` entry to
`SKILL_INDEX.md`, and added three per-skill install tests in
`tests/test_install_constellation.py`.

## Scope
**Files changed:**
- `scripts/install_constellation.py`
- `SKILL_INDEX.md`
- `tests/test_install_constellation.py`

**Specific exclusions touched:** no — no other skill's bundle entry was touched, no new
`global-*.md` filename or bucket constant was added, `skills/curator/SKILL.md` and
`scripts/curate_corpus.py` were not edited, `docs/ROADMAP.md` and `_shared/` content were
not touched.

## Behavior changed
Yes — `install_constellation.py --skills curator` (or `all`, which now includes curator via
G2's `SKILL_NAMES`/discovery) now bundles `curate_corpus.py` into the installed skill's
`scripts/` and `global-everyone.md` + `windows.md` into its `references/`. `SKILL_INDEX.md`
now lists curator. No behavior changed for any other skill.

## Map Impact
- **Structural anchors touched:** `install_constellation.py` — two new dict entries
  (`SKILL_SCRIPT_BUNDLES["curator"]`, `SKILL_REFERENCE_BUNDLES["curator"]`); `SKILL_INDEX.md`
  — one new entry; `tests/test_install_constellation.py` — three new test methods on
  `InstallConstellationTests`.
- **Capabilities added/changed/affected:** curator now ships its script
  (`curate_corpus.py`) and the everyone-tier reference bucket at install time, same as
  interrogator/lessons-auditor — matches "Behavior changed" above.
- **Constraints/assumptions touched:** honored — no new `global-*.md` filename created; the
  bundle glob composition stays pinned to the four existing `_GLOBAL_*` constants; curator's
  key in both dicts is the source directory name `"curator"` (matches `skills/curator/`),
  consistent with every other entry (e.g. `"explorer"`, `"docent"`).
- **Decision candidates / resolved decisions:** DC1 (curator carries `_GLOBAL_EVERYONE`,
  the same solo/non-orchestrating audience as interrogator and lessons-auditor) — already
  ratified by the mission frame; implemented as specified, not revisited.
- **Claims/evidence produced:** three new tests assert (a) `curate_corpus.py` lands in
  `constellation-curator/scripts/`, (b) `constellation-curator/references/` contains exactly
  `global-everyone.md` among `global-*.md` files, plus `windows.md`, and (c) curator installs
  and discovers as a real skill (`constellation-curator/SKILL.md` exists after install). Each
  was falsified by temporarily removing its backing dict line and observing the assert red,
  then restoring and re-confirming full-suite green (see Evidence below).
- **Trust limitations / drift found:** none found — `SKILL_INDEX.md` currently omits entries
  for `docent`, `explorer`, and `prototyper` (pre-existing gap, not introduced by this gate);
  flagged below as a triage candidate rather than fixed, since fixing it is out of this
  gate's allowed scope (ONLY the one new curator entry).
- **Triage candidates:** `SKILL_INDEX.md` is missing entries for `docent`, `explorer`, and
  `prototyper` — pre-existing, not part of this gate's scope; worth a follow-up issue to
  backfill the index so it matches the full discovered-skill set.

## Test mode
**Required:** `evidence-only` (mechanical wiring against a clear, already-ratified
precedent — handoff Suggested Model Tier: "simple bounded")
**Satisfied:** yes — every new test was run passing, and each was individually falsified by
temporarily deleting its backing bundle-dict line and observing a red, then restored.

## Evidence

```bash
cd C:/Programs/constellation-wt-104
py -m pytest tests/test_install_constellation.py -v -k curator
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- ...
collected 43 items / 40 deselected / 3 selected

tests/test_install_constellation.py::InstallConstellationTests::test_curator_carries_global_everyone_bucket PASSED [ 33%]
tests/test_install_constellation.py::InstallConstellationTests::test_curator_installs_and_discovers_as_a_skill PASSED [ 66%]
tests/test_install_constellation.py::InstallConstellationTests::test_curator_script_bundle_lands_in_installed_skill PASSED [100%]

============= 3 passed, 40 deselected, 2 subtests passed in 0.29s =============
```

```bash
py -m pytest tests/ -q
```
```
........................................................................ [ 15%]
........................................................................ [ 30%]
.......................................................... [ 43%]
........................................................................ [ 58%]
........................................................................ [ 73%]
.............................................................................. [ 90%]
....................s........s...............                            [100%]
467 passed, 2 skipped, 152 subtests passed in 12.29s
```

```bash
py scripts/install_constellation.py --agent codex --scope user --dest /tmp/curator-install-g4 --skills curator
ls /tmp/curator-install-g4/constellation-curator/scripts /tmp/curator-install-g4/constellation-curator/references
```
```
Codex:
Installing 1 skill(s) into ...\curator-install-g4
- constellation-curator: ...\skills\curator -> ...\curator-install-g4\constellation-curator
Installed. Restart Codex to pick up new or updated skills.

references:
global-everyone.md
windows.md

scripts:
curate_corpus.py
```

**Result:** pass — all evidence commands ran clean; full suite green with zero regressions
(467 passed, 2 skipped, same skip count as pre-change baseline).

### Diff: the two `install_constellation.py` dict-entry additions

```diff
@@ -85,6 +85,7 @@ SKILL_SCRIPT_BUNDLES: dict[str, tuple[str, ...]] = {
     "implementer": ("checklist_engine.py",),
     "reviewer": ("checklist_engine.py",),
     "explorer": ("checklist_engine.py", "init_work_area.py", "run_crew.py", "recover_crews.py", "verify_cycles.py", "verify_spec_confirmed.py"),
+    "curator": ("curate_corpus.py",),
 }
 # Global doctrine buckets (single source: skills/_shared/), bundled into each skill's
 # references/ at install exactly as the scripts above are bundled into scripts/. The
@@ -111,6 +112,7 @@ SKILL_REFERENCE_BUNDLES: dict[str, tuple[str, ...]] = {
     "triage": _GLOBAL_ORCHESTRATOR,
     "explorer": _GLOBAL_ORCHESTRATOR,
     "prototyper": _GLOBAL_CREW,
+    "curator": _GLOBAL_EVERYONE,
 }
```

### Diff: `SKILL_INDEX.md` entry

```diff
@@ -59,3 +59,8 @@ Runs an epic as the human's delegate: confirms a latitude contract, dispatches C
 Path: `skills/lessons-auditor/SKILL.md`
 
 Fresh-context Reflector dispatched at closeout: distills scoped, grounded lesson candidates from run artifacts and routes them as nominations, never applying them itself.
+
+## Constellation Curator
+Path: `skills/curator/SKILL.md`
+
+Runs a mechanical measurement pass over the skill corpus (`curate_corpus.py`) and turns the findings into scoped, grounded consolidation candidates — a solo, human-invoked role that dispatches no crew and drives no engine checklist.
```

### New test code (`tests/test_install_constellation.py`, added after
`test_commander_delegated_points_at_installed_commander_core`, before
`class TemplateBaselineTests`)

```python
    def test_curator_script_bundle_lands_in_installed_skill(self):
        # issue-104 G4: curate_corpus.py (G1) rides SKILL_SCRIPT_BUNDLES["curator"]
        # into the installed skill's scripts/, same mechanism as explorer above.
        # Falsification: delete the SKILL_SCRIPT_BUNDLES["curator"] line -> this
        # asserts red (the file never lands).
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "curator"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            self.assertTrue(
                (target_root / "constellation-curator" / "scripts"
                 / "curate_corpus.py").is_file()
            )

    def test_curator_carries_global_everyone_bucket(self):
        # issue-104 G4: curator is a solo, non-orchestrating, human-invoked role
        # (same audience as interrogator/lessons-auditor) so it carries
        # _GLOBAL_EVERYONE only: global-everyone.md + windows.md, no
        # global-orchestrator.md or global-crew.md.
        # Falsification: delete the SKILL_REFERENCE_BUNDLES["curator"] line ->
        # this reds (neither file lands, references/ has no global-*.md at all).
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "curator"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            refs = target_root / "constellation-curator" / "references"
            for ref in ("global-everyone.md", "windows.md"):
                with self.subTest(ref=ref):
                    self.assertTrue((refs / ref).is_file(), refs / ref)
            self.assertEqual({"global-everyone.md"}, {p.name for p in refs.glob("global-*.md")})

    def test_curator_installs_and_discovers_as_a_skill(self):
        # issue-104 G4: curator is a real installable/discoverable skill (dir +
        # SKILL.md), not just present in SKILL_NAMES for other tests.
        # Falsification: rename/remove skills/curator/SKILL.md (or drop curator
        # from discover_skills' source tree) -> install exit_code != 0 / the
        # SKILL.md assertion reds.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "curator"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            self.assertTrue(
                (target_root / "constellation-curator" / "SKILL.md").is_file()
            )
```

## TDD evidence, if required

Test-after / evidence-only for mechanical wiring (per suggested tier), but each new test
was individually falsified rather than merely trusted:

- `test_curator_script_bundle_lands_in_installed_skill`: temporarily deleted the
  `"curator": ("curate_corpus.py",),` line from `SKILL_SCRIPT_BUNDLES` and re-ran — reds
  with `AssertionError: False is not true` (the file never lands, since
  `required_scripts=SKILL_SCRIPT_BUNDLES.get(source_path.name, ())` falls back to `()`).
  Restored the line and re-ran — passes again. Full-suite confirmed green after restore.
- `test_curator_carries_global_everyone_bucket`: temporarily deleted the
  `"curator": _GLOBAL_EVERYONE,` line from `SKILL_REFERENCE_BUNDLES` and re-ran — both
  subTests red (`global-everyone.md` / `windows.md` missing) plus the final
  `assertEqual({"global-everyone.md"}, ...)` reds with `Items in the first set but not the
  second`. Restored and re-ran — passes again.
- `test_curator_installs_and_discovers_as_a_skill`: falsification would require
  removing/renaming `skills/curator/SKILL.md`, which is out of this gate's allowed scope
  (`Do NOT edit skills/curator/SKILL.md`) — not executed destructively, but the causal chain
  is direct: `discover_skills()` raises `InstallError` if `SKILL.md` is missing from a source
  dir, and `installer.main` would return a non-zero exit code, so the first
  `assertEqual(0, exit_code)` would red before the file-existence assert is even reached.
- Passing tests observed: `py -m pytest tests/test_install_constellation.py -v -k curator`
  → 3 passed, 2 subtests passed (see Evidence above).
- Refactor while green: no refactor needed — additions only, no reformatting of shipped
  dict literals (constraint honored).

## Docs/contracts touched
- `SKILL_INDEX.md` — added the one new curator entry (in allowed scope).

## Assumptions
- The dict key for curator in both `SKILL_SCRIPT_BUNDLES` and `SKILL_REFERENCE_BUNDLES` is
  the source directory name `"curator"` (matching `skills/curator/`), consistent with every
  existing entry keyed by source dir name rather than install name
  (`constellation-curator`). Confirmed correct: `discover_skills()` looks up both dicts by
  `source_path.name`.
- Placed the new tests in the `InstallConstellationTests` class (where
  `test_commander_delegated_*` and `test_explorer_script_bundle_lands_in_installed_skill`
  already live), matching the handoff's named model tests.

## Stop conditions hit
None. Wiring curator required no change to any other skill's bundle entry, and no new
`global-*.md` filename was needed — `_GLOBAL_EVERYONE` covered the DC1 rationale exactly as
specified.

## Out-of-scope observations
- `SKILL_INDEX.md` is missing entries for `docent`, `explorer`, and `prototyper` (pre-existing
  gap predating this gate — confirmed by grepping `^##` headings against the full
  `SKILL_NAMES` list in the test file). Not fixed here (outside allowed scope: "ONLY the one
  new curator entry"). Flagged as a triage candidate above.

## Workflow Feedback
- **Handoff gaps:** none — the handoff named the exact two dict entries, the exact
  `SKILL_INDEX.md` heading format, and the exact model tests to imitate
  (`test_explorer_script_bundle_lands_in_installed_skill`,
  `test_global_doctrine_buckets_bundled_per_audience`). Nothing was ambiguous.
- **Context rediscovered:** had to grep `SKILL_INDEX.md`'s existing `##` headings to
  discover it doesn't cover the full skill set (docent/explorer/prototyper missing) — not
  called out in the handoff, but harmless since I only needed to append one entry
  consistent with the existing ones present.
- **Instructions improvised around:** none — the plan template's TDD red/green framing
  (m1's c1/c2 postconditions) fit an evidence-only/test-after gate awkwardly since there is
  no meaningful "red" step for adding dict entries alongside their tests (the test simply
  doesn't exist yet, not "observed failing" in a TDD sense). I collapsed to the template's
  documented fallback: "For a test-after/inspection run, collapse to the single green
  postcondition (c2)" and instead proved falsification post-hoc by temporarily reverting
  each dict line and re-running — stronger evidence than a pre-write red would have given,
  since it directly ties each test to the specific line it protects.
- **What would have made this easier:** nothing concrete — this handoff was unusually
  complete (exact dict values, exact model test names/line numbers, exact close criteria).

## Return status
`complete`
