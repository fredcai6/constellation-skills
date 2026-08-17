# Mission Frame

Map-first frame for issue #565 (+ #561), lane D2 of epic #567. **Adapted for a DEGRADED map
orientation**: this repo has no `docs/architecture` packet map (a skill-source repo — see
`.agent-work/567-d2/map-orientation.json`), so there are no `capability:`/`struct:`/`event:`/
`constraint:`/`decision:` map anchors to cite here. The `orient` step discharged DEGRADED
with four hash-pinned substitutes: `docs/agents/ORCHESTRATOR_CONTEXT.md`,
`docs/agents/GLOSSARY.md`, `docs/agents/CREW_CONTEXT.md`, `map/INDEX.md`. This frame is cut
from those substitutes plus the frozen `LAUNCH_ORDER.md`, per the context step's imperative,
and is deliberately map-anchor-free rather than inventing anchor-shaped ids a DEGRADED run
cannot back. Decisions below are named by their LAUNCH_ORDER label, not `decision:` syntax.

## Intent

Delete the genuinely redundant part of `skills/workbench`'s teaching content (what the MCP
door's tool schemas now teach directly), keep all four templates unmoved at
`skills/workbench/templates/`, deregister `constellation-workbench` as a taught procedure
without new installer mechanism, and correct `docs/agents/CREW_CONTEXT.md`'s Python
Invocation section (#561), which is measured stale on this host. Full deletion of the three
teaching files, as the launch order's line-count framing suggests, is **not achievable**
without breaking two independent pre-existing test suites — the actual outcome is a partial,
evidenced deletion (see Claims / Evidence Surfaces).

## Affected Capabilities

- The checklist-engine documentation surface: what teaches an agent to drive the spine engine
  (`skills/workbench/SKILL.md`, `references/checklist-engine.md`, `references/status-model.md`)
  versus what the MCP door's 12 tool schemas (`spine_status`, `spine_lease`, `spine_start`,
  `spine_advance`, `spine_evidence`, `spine_halt`, `spine_survey_result`, `spine_capture`,
  `spine_amend`, `spine_bind`, `spine_close`, `spine_open`) teach live, at call time.
- Skill installability/registration: `scripts/install_constellation.py`'s `discover_skills()`
  requires every `skills/*` directory to carry a parseable `SKILL.md`.
- `docs/agents/CREW_CONTEXT.md`'s Python-interpreter-selection guidance (#561).

## Examples / Events

- An agent loading `constellation-workbench` today reads ~289 lines of engine-driving
  instruction before touching its own role's spine; after this change it should read the door's
  own tool descriptions instead, for everything those descriptions actually carry.
- `tests/test_install_constellation.py::test_installed_templates_use_absolute_bundled_script_paths`
  installs `workbench` end to end and reads back `references/checklist-engine.md` — an event
  this run's deletion must not silently break.
- `tests/test_mcp_adoption.py`'s Tier2/Tier3 adoption-gate sweep (epic-418-followon g4a) is a
  standing regression event: it re-runs on every future corpus change and refuses a door-tool
  mention that silently dropped the CLI fallback.

## Structural Anchors

No `struct:` map nodes exist for this repo (DEGRADED). Structural anchors instead, cited by
path (also serving as this frame's DEGRADED-mode backing citations):
- `docs/agents/CREW_CONTEXT.md` — crew-tier doctrine; owns the #561 Python Invocation section.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project deltas; confirms repo action authority
  (local commits allowed; push/PR/merge need human approval unless pre-approved) and dogfooding
  doctrine (validate engine/hook changes fresh-process only).
- `map/INDEX.md` — the code map (AST-derived); confirms `scripts.install_constellation`,
  `scripts.verify_skill_registered`, `scripts.measure_overread` are indexed modules, and that
  no `skills.workbench` entry exists there (skills/* prose is out of the code map's scope).

## Governing Constraints / Assumptions

- `skills/workbench/templates/*.template.*` (4 files) move **nowhere** — settled by the human
  (LAUNCH_ORDER Pre-Rulings: workbench stays a template package). Violating this churns every
  `skills/workbench/templates/X` path reference across the corpus, including the Admiral
  spine's own `execute` precondition.
- No new `scripts/install_constellation.py` mechanism — declined per the human's stated reason
  on the adjacent template-home question ("new mechanism spent to remove old text"); float
  instead if one turns out to be required.
- `install_constellation.py`'s `discover_skills()` (measured, not assumed) requires a
  parseable `SKILL.md` with `name`+`description` frontmatter for every non-underscore `skills/*`
  directory, or the **whole installer** raises — this bounds what "deregister" can mean without
  new code.
- Two pre-existing, independently-engineered test suites — `tests/test_mcp_adoption.py`
  (Tier2 `TIER2_SKILL_FILES` incl. `skills/workbench/SKILL.md`; Tier3 `TIER3_PATH =
  skills/workbench/references/checklist-engine.md`) and
  `tests/test_install_constellation.py::test_installed_templates_use_absolute_bundled_script_paths`
  — hard-pin specific paragraphs/sections of the "teaching half" as the corpus's sole written
  authority that the MCP door is the default path while the CLI remains available. These are
  governing constraints on this run, not just informative background: violating them fails the
  merge gate (full suite green).
- `docs/agents/ORCHESTRATOR_CONTEXT.md`: pushes/PRs/merges need human approval unless
  pre-approved for the specified work — the launch order is that pre-approval for this run.

## Decision Anchors & Decision Pressure

Pre-settled by LAUNCH_ORDER (cited by section label, not map anchor syntax — DEGRADED mode):
- "workbench stays a template package" (Pre-Rulings) — settled/human. Templates move nowhere;
  teaching half deleted; skill deregistered.
- "establish the door carries it" (Pre-Rulings) — settled/doctrine. Resolved at `understand`
  (interrogation q2): partial, not full — see Claims / Evidence Surfaces.
- "three scripts must still pass" (Pre-Rulings) — settled/doctrine. Resolved at `understand`
  (interrogation q3): deregistration without new installer code requires a minimal-but-present
  `SKILL.md`, not a missing one.
- "reduce complexity" / "no net-deletion rule" / "honest-null-is-complete" (Standing) —
  settled/human. This run's honest finding (partial deletion, not full) is reported as the
  complete deliverable, not softened to match the order's original line-count framing.

Decision pressure this run forces (surfaced, not self-resolved):
- How workbench is deregistered, given no supported installer path exists for a SKILL.md-less
  directory (LAUNCH_ORDER: "How workbench is deregistered — yours"). Resolved at `understand`
  (interrogation q4): keep a minimal, present `SKILL.md`/`checklist-engine.md`/`status-model.md`
  in each file, shrunk to only what is structurally required or evidenced load-bearing; delete
  the rest. A first-class "retired skill" installer state is named as the cleaner long-term
  fix and floated to the Admiral, not built here (new installer mechanism is a float, not
  "yours").

## Claims / Evidence Surfaces

- Claim: "the MCP door's tool schemas now carry what the teaching half taught" — checked by
  reading all 12 door tool schemas against `checklist-engine.md`/`status-model.md` section by
  section (interrogation q2). Verdict: **partially true**. Not carried: the door-vs-CLI
  coexistence doctrine pinned verbatim by `tests/test_mcp_adoption.py` Tier2 (`skills/workbench/
  SKILL.md`'s default-path paragraph) and Tier3 (`checklist-engine.md`'s `## MCP door` +
  `## Session lease` sections, including the byte-exact sentence "Nothing here removes or
  discourages the CLI."); and the post-install existence of `checklist-engine.md` with its
  `<skill-dir>` token substituted, pinned by `tests/test_install_constellation.py:344-352`.
  Also not carried: the `Crew Return Status` vocabulary pinned by
  `tests/test_commander_evidence_convention.py` and cited by
  `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md:106` (a file this lane does not
  own and must not edit); nor `## Refresh: reach-up without a handoff doc`, cited by name
  ("§refresh") from `skills/commander/references/commander-core.md:81` and
  `docs/superpowers/drills/symmetric-recovery-refresh.md`; nor `status-model.md`'s `Review
  Verdict` (APPROVE|BLOCK|COMMENT) section, generically pointed at by
  `skills/reviewer/templates/REVIEW_RESULT.template.md:5` and
  `skills/implementer/templates/IMPLEMENTER_RESULT.template.md:5`. A cold plan critic (fresh
  agent, no authoring context) surfaced the Refresh and Review Verdict gaps after the initial
  retention list was drafted; both are folded into the retained content (execute.json
  g1-implement) rather than floated, since fixing wording that points into the teaching half
  is this lane's own latitude.
- Claim: "deregistration needs no new installer mechanism" — checked by reading
  `discover_skills()` or (interrogation q3). Verdict: true **only** if each of the three files
  keeps enough content to remain a parseable, frontmatter-valid `SKILL.md` plus whatever the
  two test suites above pin. A fully empty/missing `SKILL.md` is not achievable without new
  installer code.
- Re-confirm at each execute gate: `git check-ignore` on every committed deliverable path (none
  expected — all paths are already-tracked repo files); the three named scripts' actual output
  against workbench post-change; the full suite green in a clean detached worktree.

## Map Confidence / Staleness / Disputes

- No `docs/architecture` packet map exists for this repo at all (DEGRADED-UNPARSEABLE,
  `map/INDEX.md` has content but no citable anchor id — it is a generated AST code map, not a
  decision-anchor map). This is the expected, documented shape for a skill-source repo per
  `commander-core.md`'s Architecture bookend, not a fresh staleness finding.
- `map/ids.jsonl` is empty (0 bytes) — confirms the code map's anchor layer was never
  populated for this repo, consistent with the above rather than contradicting it.
- No scout/verification gate is added for this: the DEGRADED discharge above already
  substitutes the closest real doctrine (`docs/agents/*`) and the actual load-bearing facts
  (test-suite pins, installer constraints) were independently verified by reading the source
  and running the checks directly, not inferred from a stale or partial map.

## Out of Scope

- `skills/**` outside `skills/workbench/**` — fenced to lane D1 this wave (13 of the epic's 15
  "CLI fallback" clauses live there, including `skills/_shared/global-everyone.md`'s own
  pointer sentence to `checklist-engine.md`, which stays a live pointer since the file is
  shrunk, not deleted).
- `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`'s citation of
  `skills/workbench/references/status-model.md` — left as-is; it stays valid because
  `status-model.md`'s `Crew Return Status` section is retained at the same path.
- Moving any template, anywhere — forbidden, settled by the human.
- Filing issues — ruled out; triage candidates staged as files only.
- `map/INDEX.md` — Admiral-owned; not regenerated or hand-edited here.
- A first-class "retired skill" state in `install_constellation.py` — named as the cleaner fix,
  floated to the Admiral, not built in this run (new installer mechanism is a float).
