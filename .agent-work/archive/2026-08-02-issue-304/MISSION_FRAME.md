# Mission Frame — issue #304, Commander map-input contract

> **MAP INPUT: DEGRADED** (`no-architecture-root`)
> Oriented from: `README.md`, `docs/CONSTELLATION_OVERVIEW.md`, `docs/CHECKLIST_SCHEMA.md`,
> `docs/EPISODE_STORE.md`, `skills/_shared/global-orchestrator.md`, `scripts/checklist_engine.py`
> Not knowable without a map: the durable structural relationship between the checklist engine, the
> role templates, and the install-time script bundles — I reconstructed it by reading source, which is
> exactly the failure mode this issue exists to fix. **This frame is itself an instance of the defect.**
> Paid for by: gate g0 (an independent read of the engine's command-check semantics before any design
> depends on them) — already run, and it overturned the launch order's own illustrative sketch.

This banner is written by hand here because the mechanism that would generate it is what this issue
builds. It is the first worked example of the artifact the contract will require.

## Intent

Express Commander map-first intake as one canonical concern-owned contract projected into Commander
context and plan: a resolved canonical entrypoint, a **REPORTED** degraded mode, and deletion of the
scattered prose it supersedes — each deletion filed with a predictive tripwire, then the affected
workflows actually run and the outcome recorded against each tripwire.

The deficiency is **primacy and contract, not path**. Ratified; not re-derived.

## Affected Capabilities

- Commander context intake (`COMMANDER_SPINE.template.json` task `context`)
- Commander plan/mission-frame authoring (task `plan`)
- The checklist engine's `command`-kind postcondition path (consumer, not modified)
- Spine materialization / placeholder resolution (`scripts/init_work_area.py`)
- The episode store (`episodes/active/`) as the tripwire carrier

## Examples / Events

- Five #299 baseline runs at f1Brainz `3541d292`: every run read source before the map; every run did
  eventually read the map. Failure is **ordering**, not availability.
- Zero `Skill` invocations across those five runs — the corpus was offered and declined.
- This very run: `docs/agents/` exists here, falsifying shipped prose at the first gate.

## Structural Anchors

Degraded — no map anchors exist in this repo. Substituted structural facts, each verified in source:

- `scripts/checklist_engine.py:_run_check_command` — command checks run via
  `subprocess.run([shell,"-c",cmd], capture_output=True)`; **stdout discarded, no `cwd` passed**.
- `scripts/checklist_engine.py:_check_condition` — evidence payload is `{"cmd","exit","shell"}`;
  the **exit code is the only signal reaching the spine**.
- `scripts/init_work_area.py:resolve_spine` — placeholder substitution at materialization; carries
  `<work-id>` and the `<role-skill-dir>` family; **no `<repo-root>`** today.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — `context` (:22), `plan` (:48),
  `reconcile` (:75).
- `episodes/README.md` + `docs/EPISODE_STORE.md` — write path is `scripts/apply_episode_delta.py`
  only; ids assigned by the writer; store currently empty.

## Governing Constraints / Assumptions

- Two-bin rule ratified, **no third bin** (#302). Machinize the mechanizable; the rest stays prose.
- Wiring at **context** and **plan** only. Reconcile is explicitly out — do not smuggle a third
  wiring point in under a consistency banner.
- Degraded is the **common case**, not the edge case.
- Every check must be provably falsifiable **by mutation** (#300).
- Windows: write with `encoding='utf-8', newline='\n'`. Run the suite with `python -m pytest`.
- A local green is never the merge gate; gate on the CI check exit code read at source.

## Decision Anchors & Decision Pressure

- `decision:primacy-not-path` — settled/human.
- `decision:contract-at-context-and-plan` — settled/human.
- `decision:317-folds-in` — settled/human. Scope corrected against code: 2 files / 112 words of wrong
  prose, not 11 files / several hundred words.
- `decision:tripwires-are-episodes` — settled/human. Episodes, not LESSONS.md.
- `decision:degraded-mode-is-the-common-case` — was `guess`; **now supported**: this repo has no
  `docs/architecture/`.
- **OPEN, floated, human-only:** the reach fork (does the contract project into the target repo's
  bootstrap), and whether necessity + reported-degradation is the accepted shipped meaning of
  "primacy" with ordering measured but not gated. Plan is authored so neither blocks the core.

## Claims / Evidence Surfaces

| claim | evidence surface |
|---|---|
| entrypoint resolution is correct incl. false-RESOLVED refusal | `tests/test_map_orient.py` resolver matrix |
| degraded is REPORTED and complete-or-refused | mutation floor: partial-fill matrix, all three arms |
| "could not look" is distinct from "looked, found nothing" | exit-code vocabulary test (2 vs 0) |
| the map informed the plan | frame-anchor set-membership check |
| the deletions were safe | tripwire episodes + the affected workflows actually run |
| corpus trend | `git`-derived corpus-size / per-role-surface snapshot |

## Map Confidence / Staleness / Disputes

No map. Confidence in the substituted structural anchors is **high but source-derived**: each was read
directly in the file and two of them overturned claims made in the launch order and in the design brief.
The dispute this frame carries forward: the launch order's "several hundred words on every template"
does not match the code, and the code wins.

## Out of Scope

- Re-running the #299 baseline arm.
- Any write, push, PR, or issue comment against `fredcai6/f1Brainz` (read-only).
- Candidate B's bootstrap-stanza install lifecycle — pending the Admiral's ruling; explicitly not
  built without it.
- Retrofitting the same pathless phrasing in cartographer/scout/explorer templates — routed to triage
  rather than quietly fanned out.
