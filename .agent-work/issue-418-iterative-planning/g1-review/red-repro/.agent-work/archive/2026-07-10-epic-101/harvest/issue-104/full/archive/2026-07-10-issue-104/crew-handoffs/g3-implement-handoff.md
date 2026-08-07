# Implementer Handoff

Concise fragments. Paste, don't point — you start cold.

## Gate
`g3-implement` (issue #104, constellation-curator, cluster C)

## Task
Create `tests/test_curate_corpus.py` — a golden-file test suite for
`scripts/curate_corpus.py` (built in G1). It runs the tool over a FIXTURE skills/
corpus whose planted flaws DERIVE FROM real pre-#108 duplication shapes (T6), asserts
each detector BITES, and FALSIFIES flags-never-gates (exit 0 on a maximally-flagged
fixture). No changes to `curate_corpus.py` or any skill.

Repo: `C:\Programs\constellation-wt-104` (branch constellation/issue-104).

## Protected Intent
A detector that finds nothing on fixtures is a BROKEN detector. This suite is the
proof that curate_corpus's checks actually fire, and the enforcement that
flags-never-gates cannot regress (a maximally-flagged fixture must still exit 0). The
planted duplication flaws must be AUTHENTIC (sourced from git history), not invented,
so the golden test measures the real failure modes the epic eliminated.

## Read first
- `scripts/curate_corpus.py` — the tool under test. It exposes importable functions
  returning structured `Finding` objects (`curate`, `check_size`, `check_description`,
  `check_invoker`, `check_references`, `check_duplication`, `parse_frontmatter`) and a
  `main(argv)->int`. Read it to learn the EXACT status vocabulary (the strings are
  `flagged` / `shortlist` / `info` / `ok`), the exact `check` names
  (`size`, `description-length`, `description-when-to-use`, `description-exclusion`,
  `invoker`, `reference-toc`, `duplication`, `parse`), and each Finding's fields. Assert
  against those exact strings — do not guess them.
- `tests/test_install_constellation.py` — house test style (unittest.TestCase,
  a `load_module` helper that imports a script by path, `tempfile.TemporaryDirectory`).
  Follow it: load curate_corpus via the same load-by-path helper, build fixture corpora
  in temp dirs.

## Authentic pre-#108 shapes (source of the planted duplication flaws — T6)
These are REAL duplication shapes from commit `2696769` (pre-#108, before cluster A
single-sourced them). Provenance commands (run them, PASTE their output into your
IMPLEMENTER_RESULT so fixture provenance is auditable):
```bash
git show 2696769:skills/implementer/SKILL.md | grep -n "misfit is compliance"
git show 2696769:skills/commander/SKILL.md   | grep -n "FOLLOW THIS SKILL STRICTLY"
git show 2696769:skills/workbench/SKILL.md    | grep -n "checklist_engine.py"
```
The three authentic shapes (use their verbatim text as the planted duplication
signatures — plant EACH into >= 2 fixture skills so the shingle detector clusters them):
1. **Compliance boilerplate** (was pasted verbatim into 10 skills):
   `Mandatory, no exceptions: once loaded, drive the checklist to completion through the engine and dispatch each step it names. Within a step, judgment is yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit in your workflow feedback; reporting misfit is compliance, not deviation.`
2. **Emphatic banner** (was in 6 skills): `FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY`
   (NOTE: a banner is a short phrase — if it is shorter than SHINGLE_SIZE words it will
   NOT cluster on its own. Plant it inside a longer shared sentence, OR plant the longer
   compliance boilerplate as the primary duplication signal and treat the banner as an
   additional planted flaw whose detection you verify via whatever check catches it. Read
   SHINGLE_SIZE in curate_corpus.py and design the planted duplicated passage to exceed it.)
3. **Engine-invocation string** (was restated in ~7 skills with drift):
   `Drive a controller one step at a time with the absolute path to this installed skill's bundled scripts/checklist_engine.py`

## Close Criteria (each proven in your IMPLEMENTER_RESULT)
Build fixture corpora (temp dirs) and assert curate_corpus flags each planted flaw. At
minimum:
1. **Duplication detector BITES:** a fixture with the authentic compliance-boilerplate
   passage (a shared window longer than SHINGLE_SIZE words) planted into >= 2 fixture
   skills produces a `duplication` finding naming those skills. Assert the shared-skills
   set and that the finding is `flagged`. Add a second planted duplication shape (engine
   string) to show the detector clusters more than one signature.
2. **Size detector bites:** a fixture skill with an oversized body (over the word target /
   line hard-flag) produces a `size` finding `flagged`.
3. **Invoker detector bites:** a fixture skill with no `invoker:` frontmatter key produces
   an `invoker` finding `flagged`; a fixture skill WITH `invoker: human` produces
   `invoker` `ok` (both directions).
4. **Description detectors bite:** a first/second-person description produces a person
   SHORTLIST (`shortlist`, not a verdict); a description with no "Use when" marker produces
   `description-when-to-use` `flagged`; a confusable-pair fixture skill with no exclusion
   clause produces `description-exclusion` `flagged`. (Use skill dir NAMES that are in
   curate_corpus's confusable set so the exclusion check applies — read the set.)
5. **Reference-TOC detector bites:** a fixture skill with a `references/foo.md` over 100
   lines lacking a TOC marker produces a `reference-toc` finding `flagged`; a short
   reference or one WITH a `## Contents` TOC does NOT.
6. **Unparseable dir → row, not crash:** a fixture skill dir with malformed frontmatter
   (and one with no SKILL.md) produces a `parse` finding `flagged`, `main()` exits 0, no
   exception raised.
7. **FLAGS-NEVER-GATES falsification:** assemble a MAXIMALLY-flagged fixture (every
   detector firing at once) and assert `main([...])` RETURNS 0 (exit 0). This is the
   invariant-#2 falsification — it must be a real assertion, not a comment.
8. Tests pass: `py -m pytest tests/test_curate_corpus.py -q` green, and the full suite
   `py -m pytest tests/ -q` stays green.

## Allowed Scope
`tests/test_curate_corpus.py` (new file only). You MAY read `scripts/curate_corpus.py`,
`tests/test_install_constellation.py`, and use `git show 2696769:...`. Change NO other file.

## Specific Exclusions
- Do NOT modify `scripts/curate_corpus.py` (if you believe a detector is wrong, that is a
  STOP-and-return, not a fix here).
- Do NOT modify any real skill or other test.
- Do NOT invent duplication shapes — the planted duplication flaws must be the authentic
  pre-#108 text above (T6). Non-duplication flaws (oversized body, missing tag, etc.) may
  be synthesized minimally since those detectors are structural, not shape-derived.

## Constraints
- stdlib + unittest only (match the repo; no pytest-only fixtures needed — pytest runs
  unittest classes fine).
- Build every fixture in a `tempfile.TemporaryDirectory`; write files with
  `encoding="utf-8"`. Do not touch the real `skills/` tree.
- Assert against the EXACT status/check strings read from curate_corpus.py.

## Map Anchors (inbound)
- **Structural:** `tests/test_curate_corpus.py` (new).
- **Capability:** detector falsification.
- **Constraint:** planted duplication flaws derive from git 2696769 shapes (T6).
- **Evidence:** each detector bites; exit 0 on a maximally-flagged fixture.

## Deliverable Path Check
- **Committed** — `tests/test_curate_corpus.py`; `git check-ignore` exits 1 (not ignored),
  verified before dispatch.

## Required Evidence (paste into IMPLEMENTER_RESULT)
- The provenance command outputs above (git show ... | grep), proving the planted
  duplication text is authentic pre-#108 shape.
- `py -m pytest tests/test_curate_corpus.py -q` full output (all green), with the test
  names visible (`-v` is fine) so each detector's biting test is named.
- `py -m pytest tests/ -q` tail showing the whole suite green.
- A one-line note of the flags-never-gates falsification assertion (quote the assert line).

## Verification Commands
```bash
cd C:/Programs/constellation-wt-104
py -m pytest tests/test_curate_corpus.py -v
py -m pytest tests/ -q
```

## Suggested Model Tier
`stronger — reason: fixture design + detector-falsification discipline (each must bite)`

## Authority
Decided (do not revisit): planted duplication flaws use the authentic pre-#108 text;
assert against curate_corpus's real status/check strings; no edits to the tool or skills.
You DECIDE: fixture corpus layout, test decomposition, how you assemble the
maximally-flagged fixture.

## Stop Conditions
Stop and return if: a detector does NOT bite as the spec expects (report it as a finding
— it may be a real tool bug to route, not something to paper over); you would need to edit
`curate_corpus.py` or a real skill; a planted authentic shape cannot be made to cluster
(report the SHINGLE_SIZE interaction honestly).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, evidence (pasted provenance +
test runs), assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
WRITE the full IMPLEMENTER_RESULT as your final message AND to the given result path before
going idle.
