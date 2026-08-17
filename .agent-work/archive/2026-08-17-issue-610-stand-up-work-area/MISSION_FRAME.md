# Mission Frame

Shrunk frame: this run oriented DEGRADED-UNPARSEABLE (`map/ids.jsonl` empty, `map/INDEX.md` has no citable anchor id at HEAD 600de020 — see `map-orientation.json`, escalated as a triage candidate). There is no code-node graph to cite capability/struct/decision anchors from. This is also a local/mechanical doctrine-and-template consolidation (moving an imperative between doc files, no runtime behavior graph to walk), so per this template's own instruction the frame is built from the three hash-pinned substitutes read at orient time, not from map anchor ids.

## Intent
Make "the dispatcher stands up the worktree and work area; the Commander receives a spine path and claims it" one shared instruction set, cited (not restated) from both the Admiral's delegated-provisioning path and the human-led Commander's own stand-up, per issue #610 and the consolidated understanding in `INTERROGATION_RECORD.json`.

## Affected Capabilities
No `capability:` map nodes exist to cite (map degraded). In substitute terms (`docs/agents/ORCHESTRATOR_CONTEXT.md`, `skills/admiral/references/fleet-doctrine.md`): the Admiral's worktree-provisioning step, the Commander's init-gate imperative, and the delegated-Commander entry doc's own copy of that imperative.

## Examples / Events
- Delegated run: Admiral runs `git worktree add`, scaffolds `.agent-work`, instantiates `spine.json`, hands the Commander the spine path in `LAUNCH_ORDER.template.md`'s Workspace section — Commander's first act becomes claiming the lease, not scaffolding.
- Interactive run (this run itself): the human/Commander stands up its own worktree and work area before driving the spine — same instruction set, different hands, per `skills/commander/`'s existing framing.

## Structural Anchors
No map struct anchors (degraded). Substitute file paths this run is built from and edits:
- `README.md` — repo orientation (read, not edited)
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — repo action authority / dogfooding hazard (read, not edited)
- `skills/admiral/references/fleet-doctrine.md` — Admiral's worktree-provisioning steps 1-2 (edited: point at the new shared doc)

Additional files this run edits, read directly (not map-resolvable, doctrine prose per `unmapped` in the orientation receipt):
- `skills/_shared/stand-up-work-area.md` (new)
- `skills/commander/templates/COMMANDER_SPINE.template.json`
- `skills/admiral/templates/LAUNCH_ORDER.template.md`
- `skills/commander-delegated/SKILL.md`
- `skills/commander/references/commander-core.md` (edited: Start-here bullet 1 goes claim-only, cites the new shared doc)
- `scripts/install_constellation.py` (`SKILL_REFERENCE_BUNDLES`)
- `.agent-work/templates/COMMANDER_SPINE.template.json` (local dogfood resync)

## Governing Constraints / Assumptions
- `constraint: verify_worktree_isolation.py`'s gate-mode (Admiral's pre-wave check) and the `--here` arrival-check script itself are untouched — issue #610 explicitly does not remove them.
- `constraint:` project-local-first template resolution (`.agent-work/templates/<name>` preferred over the bundled skill template) — documented in `skills/workbench/references/checklist-engine.md` and `install_constellation.py`'s `write_template_working_copies`; governs why the local `.agent-work/templates/COMMANDER_SPINE.template.json` needs its own resync, separately from the shipped/installed copy.
- `assumption:` the local `.agent-work/templates/COMMANDER_SPINE.template.json` is safely mechanically resyncable — confirmed via `check_skill_freshness.py` (`upstream-changed`, local==baseline, no genuine local customization to preserve).

## Decision Anchors & Decision Pressure
No map-sourced decision anchors (degraded — nothing for a map anchor to be a member of). Already-settled scope decisions, signed off by Tommy in `INTERROGATION_RECORD.json` during understand (not map anchors, so not cited with the `decision:` id form here):
- Six-part scope: shared doc + 5 file edits, `verify_worktree_isolation.py` untouched. Settled/human, no open pressure.
- Collapse `commander-delegated/SKILL.md`'s duplicated "Start here" into a pointer at `commander-core.md`, matching `commander/SKILL.md`'s existing pattern, rather than just fixing the duplicate's content in place. Settled/human ("fold it in and push a pointer to both skills").
- Resync only `.agent-work/templates/COMMANDER_SPINE.template.json` in this repo, not `.baseline/` or the other 7 unrelated stale templates `check_skill_freshness.py` found. Settled/human.

No open decision pressure — the scope was fully resolved during understand.

## Claims / Evidence Surfaces
- claim: the new `skills/_shared/stand-up-work-area.md` is actually reachable from both `commander` and `admiral` installed skills — checked by `SKILL_REFERENCE_BUNDLES` wiring in `install_constellation.py` plus `validate_required_references()`.
- claim: `.agent-work/templates/COMMANDER_SPINE.template.json`'s resync is a pure drop of the stale `c0` block plus the new claim-only imperative, nothing else diverges — checked by diff against the shipped `skills/commander/templates/COMMANDER_SPINE.template.json` post-edit.
- claim: no remaining reference to `init_work_area.py` as something the Commander runs on itself — checked by grep across `skills/commander*/`.

## Map Confidence / Staleness / Disputes
- `map/INDEX.md` / `map/ids.jsonl` — DEGRADED-UNPARSEABLE at HEAD 600de020, empty ids file, unparseable index. Already escalated as a triage candidate for this run (regenerate or flag stale); not blocking this run since the affected files are doctrine/template prose outside the code map's stated scope (`unmapped` in the orientation receipt).

## Out of Scope
- `verify_worktree_isolation.py`'s gate-mode and the `--here` arrival-check script itself (explicitly retained, per issue #610 and Tommy's sign-off).
- The other 7 unrelated stale project-local templates found via `check_skill_freshness.py` (separate cleanup, not this issue).
- `.baseline/` snapshot mechanism itself (not touched; this run edits the working copy only).
- Regenerating/fixing the procedural map (filed as a triage candidate, not fixed here).
