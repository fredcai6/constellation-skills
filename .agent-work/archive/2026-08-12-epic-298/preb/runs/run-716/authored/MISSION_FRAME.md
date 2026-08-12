# Mission Frame — issue #716 (work_id-with-slash parsing)

Commander run `issue-716`. **Planning-only engagement**: the spine stops after `plan`.

## Intent

Remove the shared assumption, in constellation's commander/admiral machinery, that a `work_id`
contains no `/` — so this repo's own nested Commander-under-Admiral convention (`epic-<N>/<issue>`)
stops forcing a waive or a CLI bypass at crew-verification and archive closeout. One installable
helper module owns the parsing and the matching; both defect sites import it; every change is
**strictly widening** (a slashless `work_id` behaves byte-identically).

**Map note.** The change lands in the **constellation-skills** repo
(`C:\Programs\constellation-skills`), not in f1Brainz. f1Brainz has a Cartographer packet map; the
target repo does **not** — it carries a `docs/agents/ORCHESTRATOR_CONTEXT.md` and per-feature design
docs instead. This frame is therefore written against **source structure + the feature design doc**
rather than packet nodes, per the commander doctrine's "no packet map → reconcile the structural
record directly" path. The frame is **not** shrunk-as-trivial: the change is small in lines but
crosses a distribution boundary (the installer) where a silent miss has precedent.

## Affected Capabilities

- **crew-run recovery / result verification** — `run_crew.py` resolves which durable registry holds a
  crew session, given only the session name. This run changes *how the work-id is recovered from the
  session name*, nothing about launch, duplicate-guard, or freshness.
- **feedback/archive closeout invariant** — `verify_agent_feedback.py` proves the durable feedback log
  exists for a run, that nothing durable leaked into the work area, and (at `--phase archive`) that a
  run package was actually archived. This run changes *how a run's archive package and feedback entry
  are matched to the work-id*, nothing about what the invariant requires.
- **skill installation / script distribution** — `install_constellation.py` copies each script named in
  a skill's bundle into the installed skill. This run adds one module to that distribution.

## Examples / Events

- `constellation/epic-659/665/g1/implementer/attempt-1` — a real session name from the epic-659 run.
  Six segments; today's parser reads the work-id as `epic-659`.
- `.agent-work/archive/2026-07-25-epic-659/665/` — the archive package the spine's own
  `<date>-<work-id>` sentence produces verbatim for that run. Two levels below `archive/`.
- `## 2026-07-25 — epic-659/665` — a feedback heading. An Admiral verifying `epic-659` substring-matches
  its own child's entry.
- Edge cases the helper must hold: 1-segment work-id (today's behaviour, unchanged); 3+ segments;
  a legacy/hand-written session name that does **not** end in `attempt-<n>`; an archive package whose
  first segment happens to equal a shorter work-id.

## Structural Anchors

- `scripts/run_crew.py:933-940` — `load_registry_for_resume`, defect site 1. Called from three CLI
  paths: `--verify-result` (`:824`), `--resume` (`:848`), bare `--abandon` (`:867`).
- `scripts/run_crew.py:83-88` — `session_name`, the grammar the parse must invert.
- `scripts/verify_agent_feedback.py:72-80` — `_current_run_archive_dirs`, defect site 2. Called from
  `_negative_errors` (`:121`, `:133`).
- `scripts/verify_agent_feedback.py:24-39` — `_entry_block`, defect site 3 (unnamed in the issue).
- `scripts/install_constellation.py:87-101` — `SCRIPT_RUNTIME_COMPANIONS` + `expand_script_bundle`, the
  declared mechanism for shipping a sibling module a bundled script imports.
- `scripts/install_constellation.py:104-121` — `SKILL_SCRIPT_BUNDLES`. `run_crew.py` → commander,
  explorer. `verify_agent_feedback.py` → commander, admiral. (`commander-delegated` ships **no**
  scripts; it is not a distribution target.)
- `tests/test_install_constellation.py:638-654` — `test_bundled_scripts_carry_their_sibling_imports`,
  the existing guard on plain sibling imports.
- `tests/test_crew_launcher.py`, `tests/test_verify_agent_feedback.py` — the two regression homes.
- `docs/RECURSIVE_IMPROVEMENT_DESIGN.md:20` — the one-line structural record of the feedback invariant.

## Governing Constraints / Assumptions

- **constraint:strictly-widening** — no session name or archive layout that resolves correctly today may
  resolve differently. The slashless path must stay byte-identical. Both defects currently fail
  *misleadingly* (empty list, not an exception), so the regression tests must assert the **positive**
  match, not merely that an error is raised.
- **constraint:green-at-every-gate-boundary** — `test_bundled_scripts_carry_their_sibling_imports`
  compares sibling imports against the **raw** `SKILL_SCRIPT_BUNDLES` entry. The moment a bundled
  script does `from work_id import ...` without the module being distributed, that test goes red.
  **This forces gate order: distribution before use.**
- **constraint:installer-is-the-only-distribution-path** — the `~/.claude/skills/*/scripts/` copies are
  install output. A module not named in a bundle (directly or via a companion) is simply absent in
  every install; the installer's own comment records this exact class leaving the Context Governor inert
  from the day it shipped. A fix that works in the source repo and not in the install is not a fix.
- **assumption:gate-and-role-carry-no-slash** — verified, not assumed: `run_log_paths` uses gate and role
  verbatim as filename stems, so a `/` in either would already break log capture. This is what makes the
  right-anchored parse exact.
- **constraint:stdlib-only** — every script in this repo is standard-library-only; the helper must be too.
- **constraint:no-f1brainz-source-change** — f1Brainz invokes the installed copies by absolute path and
  vendors nothing. Its `ORCHESTRATOR_CONTEXT.md` evidence table does not bind this change.

## Decision Anchors & Decision Pressure

Three decisions were forced during `understand` and taken by the Commander under the engagement's
standing delegation (no human reachable). Each is listed with the alternative it rejected, so the
principal can reverse any one independently.

- decision:archive-matcher-not-convention — fix by generalizing the **matcher** to a relative-path,
  segment-count rule; leave the `<date>-<work-id>` archive naming convention untouched. Rejected: flatten
  `/` in the archive directory name (would rewrite the archive sentence in three spine templates, orphan
  existing packages, and *add* a rule every future agent must remember — the exact failure mode being
  fixed). The matcher will additionally tolerate a flattened name, so a later switch costs nothing.
  @grade: settled/human · leans g1-implement,g3-implement · settle: n/a — reversible by the principal
- decision:new-shared-module — the helper is a new `scripts/work_id.py`, not an extension of
  `agent_work_root.py`. Rejected: fold into `agent_work_root.py` (one job — durable-root resolution — and
  it is not bundled to explorer, which does carry `run_crew.py`). The issue asks literally for "a single
  shared work_id-safe parsing/matching helper both scripts import".
  @grade: settled/human · leans g1-implement · settle: n/a — reversible by the principal
- decision:entry-block-tiebreak-in-scope — the unnamed third instance (`_entry_block` substring match) is
  in scope, bounded to a **strictly-widening tie-break**: when more than one heading matches, prefer the
  most specific; a single match behaves exactly as today. Rejected: defer to triage (same root cause,
  same file, same helper — deferring guarantees a third waive).
  @grade: settled/human · leans g3-implement · settle: n/a — reversible by the principal
- decision pressure (surface at implementation, do **not** pre-decide): whether
  `test_bundled_scripts_carry_their_sibling_imports` should compare against the **expanded** bundle
  (companion-aware) or whether `work_id.py` should instead be hand-added to three bundle literals. The
  expanded-bundle read is the Commander's recommendation — the expanded bundle is what actually installs,
  so the raw-bundle comparison is arguably a latent defect in the test — but it edits an existing guard
  and therefore belongs to the human/principal, not to a crew acting alone.

## Claims / Evidence Surfaces

- claim:defect-1-live — `load_registry_for_resume("constellation/epic-659/665/g1/implementer/attempt-1")`
  returns `[]` against a registry that exists. Checked by `evidence/repro_716.py` (run 2026-08-01);
  re-confirmed by a new positive-match regression test in `tests/test_crew_launcher.py`.
- claim:defect-2-live — `_current_run_archive_dirs(agent_work, "epic-659/665")` returns `[]` against
  `archive/2026-07-25-epic-659/665`, while the slashless control matches. Same repro; re-confirmed in
  `tests/test_verify_agent_feedback.py`.
- claim:defect-3-live — `_entry_block(text, "epic-659")` returns the heading for `epic-659/665`. Same repro.
- claim:back-compat — every currently-passing test in `tests/test_crew_launcher.py`,
  `tests/test_verify_agent_feedback.py`, `tests/test_install_constellation.py` still passes, unmodified,
  except where a test is deliberately widened.
- claim:distribution — after the change, a real install writes `work_id.py` into
  `constellation-commander/scripts/`, `constellation-admiral/scripts/`, `constellation-explorer/scripts/`,
  and the installed `run_crew.py` / `verify_agent_feedback.py` import it without `ModuleNotFoundError`.
  The repo already runs real end-to-end installs into a tempdir in its tests — that is the proof shape.
- claim:guard-falsifies — deleting the companion declaration makes the guard test **fail**. Demonstrated,
  not asserted.

## Map Confidence / Staleness / Disputes

- **`lesson:constellation-slash-workid-parsing-gaps` (LESSONS.md:373) is a 2026-07-27 report, not current
  truth.** It was treated as a lead and **verified against the code**, not trusted: both named defects
  reproduce today, and the lesson's own claim that `_current_run_archive_dirs` fails on *both* its string
  tests is confirmed. It did **not** name the `_entry_block` instance — the lesson under-reports the blast
  radius. Plan effect: the run reproduces before it fixes, and sweeps the file for siblings rather than
  patching only the two cited lines.
- **The target repo has no packet map.** Structural anchors above are source-derived, so they are
  line-numbered and re-verifiable rather than map-cited. Plan effect: every gate's close criteria names a
  file and symbol, not a map node; the structural record is reconciled into
  `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` rather than into packets.
- **`SCRIPT_RUNTIME_COMPANIONS` has exactly one entry today** (`checklist_engine.py` → `gauge_reader.py`),
  so it is a one-adapter seam — hypothetical, not proven. Plan effect: the second adapter is added
  deliberately and its guard is *demonstrated to falsify*, rather than assumed to work.

## Out of Scope

- Any f1Brainz source, test, or documentation change. f1Brainz is a consumer of the installed copies.
- Changing the `<date>-<work-id>` archive naming convention, or any spine/skill template text.
- Any change to `checklist_engine.py`, or to what the feedback/archive invariant *requires*.
- `recover_crews.py` — it builds registry paths from a work-id directly (`Path` division), so it is
  already slash-safe. Its `import run_crew` form is invisible to the sibling-import guard's
  `^from (\w+) import` regex; that is a real latent gap, but it is a **triage candidate**, not this run.
- Retro-fixing archives already on disk, or the epic-659 forced waive.
- The `--verify-result` CLI's error text quality (it names the session, never the parse) beyond what
  falls out of the fix.
