# Mission Frame — issue-716 (work_id-with-slash parsing in shared constellation machinery)

## Intent

Make the two constellation shared-machinery functions that recover a `work_id` handle a `work_id`
containing `/` path segments, so this repo's nested Commander-under-Admiral convention
(`epic-<N>/<issue>`) stops forcing waives and CLI-bypass workarounds. Delivered as **one shared
helper module both scripts import**, in the **constellation-skills source repo**.

**Map-scope declaration (read this before the anchors below).** The map the `context` step resolved
is *this* repo's map (`docs/architecture/index.md`, 76 anchors, RESOLVED — receipt
`.agent-work/issue-716/map-orientation.json`). The code under change is **not in it**: it lives in
`C:/Programs/constellation-skills/scripts/`, which f1Brainz consumes as an installed skills tree at
`~/.claude/skills/`. So this frame is deliberately split:

- the **f1Brainz map** is the map of the *trigger and the consumer* — it explains why a slash-bearing
  work_id exists here at all, and what breaks in this repo's runs when the tooling mishandles it;
- the **structural anchors of the change itself** are cited as source paths in the constellation-skills
  repo, verified by direct read, and are explicitly **outside** the resolved map inventory.

That mismatch is why the `plan.c6` verify-frame gate is expected to refuse and is taken as a
**recorded waiver**, not a silent skip. This is not a "trivial change so skip the frame" waiver — the
frame is written in full; the anchors simply belong to another repo's structure.

## Affected Capabilities

- `capability: crew recovery by session name` — `run_crew.py` re-derives the `work_id` from a crew
  session name to find that run's `crew-runs.json`. Today it truncates a multi-segment work_id to its
  first segment and then reports "no crew recorded", i.e. it fails by **looking in the wrong place**
  while sounding like a missing record. Touched by this run: the derivation only.
- `capability: feedback/archive invariant verification` — `verify_agent_feedback.py --phase archive`
  proves the run package was archived and that the durable trio did not leak into it. Today, for a
  nested work_id, the archive-dir set is **always empty**: the positive check fails and the two
  leak checks pass vacuously. Touched by this run: the archive-dir matcher only.
- `capability: skill install bundling` (`install_constellation.py`) — relied on, not changed in
  behavior: a new sibling module must ride along with **both** consumers or an install ships a
  script whose import fails.

## Examples / Events

- **The observed failure, twice in one run** (`epic-659/665`, 2026-07-25): all four
  `--verify-result` calls refused against genuinely-fresh, correctly-recorded crews; then
  `archive.c1` was **force-waived** (`--force`, `authority=commander-self`) because the archive check
  could not be satisfied by any directory name. Grounding:
  `.agent-work/staged-feedback/epic-659/665/CONSTELLATION_FEEDBACK.md` (both entries), and
  `.agent-work/epic-659/ADMIRAL_LOG.md` ("2nd instance this run, same root").
- **Session-name example**: `constellation/epic-659/665/g1-implement/implementer/attempt-1` →
  current parse yields `epic-659`; correct parse yields `epic-659/665`.
- **Archive-name examples in the field**: `.agent-work/archive/2026-07-26-664-reference-laps` (flat,
  dated leaf) and the nested `.agent-work/archive/<date>-epic-659/665/` that the spine's own archive
  imperative literally produces for a slash-bearing work_id. Both shapes must be recognized.
- **Edge cases the helper must answer explicitly**: a single-segment work_id (the overwhelmingly
  common case — must behave exactly as today); a malformed session name (must still refuse *visibly*,
  not silently resolve to something); a Windows-authored `epic-659\665`; a work_id whose leaf name
  collides with a different run's leaf (`epic-659/665` vs `epic-660/665`) — the matcher must not
  accept the wrong package.

## Structural Anchors

Outside the resolved f1Brainz map (see the map-scope declaration); verified by direct source read.

- `C:/Programs/constellation-skills/scripts/run_crew.py` — `session_name()` (l.83-88, the grammar),
  `registry_path()` (l.95-96), `load_registry_for_resume()` (l.933-940, **defect 1**), call sites
  l.824 / l.848 / l.867. Level: function.
- `C:/Programs/constellation-skills/scripts/verify_agent_feedback.py` —
  `_current_run_archive_dirs()` (l.72-80, **defect 2**), consumers l.121-137. Level: function.
- `C:/Programs/constellation-skills/scripts/agent_work_root.py` — the **precedent** for a shared
  sibling module and its import idiom (`sys.path.insert` + plain import, mirrored at
  `verify_agent_feedback.py:12-13`). Level: module.
- `C:/Programs/constellation-skills/scripts/install_constellation.py` —
  `SCRIPT_RUNTIME_COMPANIONS` (l.88-109) and `SKILL_SCRIPT_BUNDLES` (l.143-173). Level: module.
- `C:/Programs/constellation-skills/tests/{test_crew_launcher.py,test_verify_agent_feedback.py,test_install_constellation.py}`
  — the three existing test homes. Level: module.

f1Brainz-side anchors (the consumer, unchanged by this run): the `.agent-work/` work-area convention
itself — `.agent-work/epic-659/…` nested work areas, `.agent-work/archive/<date>-<work-id>/`,
`.agent-work/staged-feedback/<work-id>/`.

## Governing Constraints / Assumptions

- `constraint: fail visibly, never a hidden fallback` (inherited, `global-everyone.md` §Universal
  posture) — the fix must never make a wrong-but-plausible resolution succeed. An unparseable session
  name keeps raising `CrewLaunchError`; an ambiguous archive match must not be silently picked.
- `constraint: the engine owns spine state` — nothing in this change touches checklist state; it only
  changes how two scripts *read* the filesystem.
- `constraint: an installed script must find its siblings` — a bundled script importing a sibling
  that some bundle omits is a broken install. `explorer` bundles `run_crew.py` **without**
  `agent_work_root.py`, which is the concrete trap here.
- `constraint: no behavior change for single-segment work ids` — every existing run must keep working
  byte-for-byte; this is a widening, not a redefinition.
- `assumption: gate / role / attempt segments never contain '/'` — verified against
  `session_name()`'s construction; this is what makes the inverse exact rather than heuristic.
- `constraint (f1Brainz-local, ORCHESTRATOR_CONTEXT)`: push/PR needs the owner's go-ahead; this
  engagement is planning-only, so **no** repo write, commit, push, or issue comment happens here.

## Decision Anchors & Decision Pressure

- decision:change-target-is-the-source-repo — the fix lands in `C:/Programs/constellation-skills`, never in the installed `~/.claude/skills` copies, and never in f1Brainz.
  @grade: settled/human · leans g1,g2,g3 · (the issue itself routes it: "route to wherever constellation-commander's scripts are maintained")
- decision:one-shared-helper-module — both defects are fixed through one imported module (`scripts/work_id_paths.py`), not two local patches.
  @grade: settled/human · leans g1,g2,g3 · (stated in the issue text; ruled at interrogation d2)
- decision:archive-matcher-is-a-recognizer-not-a-namer — accept the nested AND the flattened dated archive shape, normalize separators, and legislate no naming convention.
  @grade: settled/human · leans g3 · (ruled at interrogation d3, grounded in both shapes existing in the field)
- decision:no-doctrine-or-template-edit-this-issue — code + tests + the helper's docstring contract only; a doctrine note routes to triage.
  @grade: settled/human · leans g4 · (ruled at interrogation d4)
- decision:widen-the-companion-closure-guard — the installer's runtime-sibling test is extended to every bundled script rather than left engine-only.
  @grade: guess · leans g2 · settle: attempt the data-driven widening; if any existing bundle fails for an unrelated pre-existing reason, narrow to the two consumer scripts and record why
- **decision pressure** (surface, do not decide here): whether `.agent-work/archive/` should ever hold
  nested directories at all, or whether the archive step should flatten a slash-bearing work_id into a
  single dated name. This run deliberately makes the question moot by recognizing both; the naming
  convention itself stays the owner's call.

## Claims / Evidence Surfaces

- `claim: the session-name inverse is exact` — verified by a round-trip test:
  `work_id_from_session_name(session_name(w, g, r, n)) == w` over single- and multi-segment ids,
  plus a refusal test for malformed names.
- `claim: --verify-result resolves the right registry for a nested work_id` — verified by a
  registry-level test that writes `.agent-work/epic-659/665/crew-runs.json` and asserts the entry is
  found (the exact scenario that failed four times in the field).
- `claim: the archive gate is satisfiable, and still refuses when it should` — verified by paired
  tests: a nested work_id with a correctly-archived package **passes**; the same work_id with **no**
  package still **fails**; a leaked `AGENT_FEEDBACK.md`/`LESSONS.md` inside the nested package is
  still **caught** (this is the vacuous-pass regression).
- `claim: no install ships a script that cannot import its sibling` — verified by the widened
  companion-closure test over `SKILL_SCRIPT_BUNDLES`.
- `claim: single-segment behavior is unchanged` — verified by the pre-existing suites in
  `tests/test_crew_launcher.py` and `tests/test_verify_agent_feedback.py` staying green untouched.

## Map Confidence / Staleness / Disputes

- **The whole change area is out-of-map** (highest-impact statement in this frame). No packet,
  overlay, or decision anchor in `docs/architecture/index.md` describes constellation-skills
  internals — correctly so, it's a different repo. Plan consequence: every structural claim in this
  frame was taken from a **direct source read at planning time**, and each gate re-verifies its own
  anchors (line numbers included) rather than trusting this frame; and `plan.c6` (verify-frame) is
  taken as a **recorded waiver**, since its inventory cannot contain out-of-repo anchors.
- The constellation-skills repo's own working state (branch, dirty files, whether `main` has moved
  since the `CORPUS.json` pin `3595955666`) was **not** inspected during planning. Plan consequence:
  gate g0 re-checks the two defect sites are still present and unmodified before any edit.

## Out of Scope

- Any change to f1Brainz source, tests, or docs (this issue produces none).
- Reinstalling / rolling out the fixed scripts into `~/.claude/skills` — a post-merge operator step,
  called out as a handover note, not a gate deliverable.
- Adding a `--work-id` override flag to `--verify-result` (the proposal in the original field report):
  unnecessary once the parse is exact, and it would add a second way to say the same thing.
- Editing the spine template's archive imperative or any doctrine `.md` (routed to triage).
- Any redesign of the work-id naming convention, the registry format, or the archive layout.
- Retroactively repairing the epic-659/665 forced waive.
