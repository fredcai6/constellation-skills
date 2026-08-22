# Mission Frame

Map-first frame for w1-wiring (epic 569, wave 1; issues #345, #444, #368). No `struct:`/`capability:`
anchor system exists at base commit `244665ee` — `map/ids.jsonl` is empty and
`docs/architecture/generated/map.json` has zero `nodes[]` (context step returned
`DEGRADED-UNPARSEABLE`, discharged in `.agent-work/w1-wiring/map-orientation.json`). This frame is cut
from the discharged substitutes — `docs/agents/AGENT_GUIDE.md`, `map/INDEX.md`,
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md` — plus the launch order's own pasted
measurement, not from a live anchor inventory. Every citation below is a repo-relative path, never an
anchor id, per that degraded state.

## Intent

Take an accurate, evidence-backed census of every check-shaped script in `scripts/` (`verify_*.py`,
`check_*.py`, `prove_*.py`, `measure_*.py`), classify each **live / unwired / dead**, and let that
census — not a prior assumption — decide whether a registration lint or vocabulary rule is warranted.
Separately, settle `generate_spine.py`'s disposition (does any live path call it), and re-measure the
`#368`/`#444` duplicated-field-group counts against the current repo rather than the stale issue text.
Ship whichever of the three honest-null outcomes the evidence supports.

## Affected Capabilities

- Check-shaped scripts under `scripts/` (`verify_*.py`, `check_*.py`, `prove_*.py`, `measure_*.py`) —
  the census population itself (`map/INDEX.md` lists `scripts` as 61 modules / 1292 entities; the
  census re-derives which of those are the ~26 check-shaped ones by filename pattern, per
  `LAUNCH_ORDER:The measurement that motivated this`).
- `skills/*/templates/*.json` `"check": {"kind": "command"}` blocks — the only enforcement surface a
  script can be genuinely wired into (`docs/agents/GLOSSARY.md` "two-bin rule").
- `scripts/hooks/` — a legitimate wiring point the launch order calls out by name
  (`LAUNCH_ORDER:Isolation is git-only`); inspect-only in this worktree, no edit validated from here.
- `scripts/generate_spine.py` — the gate-plan-spec compiler epic 569's wave 2 is blocked on; disposition
  is a required deliverable (`LAUNCH_ORDER:The finding that reordered the epic`).
- `scripts/checklist_engine.py` (`match` comparison ~L1090/~L3439) and `scripts/validate_spine.py` —
  **fenced**: sibling commander `w1-verdict` owns these; census may cite them but not edit them
  (`LAUNCH_ORDER:Fence`).
- `.agent-work/templates/` project-local overlay + `.baseline` mirrors, and
  `scripts/check_template_overlay_freshness.py` — named by the launch order as a live-or-ironic case to
  resolve (`LAUNCH_ORDER:Template overlay`).

## Examples / Events

- The Admiral's own grep-based pre-census (pasted in `LAUNCH_ORDER:The measurement that motivated this`)
  — a starting point, explicitly not truth; this run's job is to redo it properly (CI workflows, git
  hooks, pytest tests, cross-script calls a grep over `skills/*/templates/*.json` alone cannot see).
- Commit `244665ee` ("Rebuild the Commander plan step around the order it actually requires") — the one
  prior artifact binding `#368`'s field-group count; it added `map_check_note` to
  `TemplateOnlyFieldAllowlist`, which is why the issue's stale count cannot be copied forward.
- `episodes/` (via `query_episodes.py`) and `/home/tommy/projects/constellation-skills/.agent-work/`
  (prior epics' work areas, read-only, outside this worktree) — evidence of which scripts actually ran
  in anger, per `LAUNCH_ORDER:Data Locations`.

## Structural Anchors

None citable — no `struct:` node inventory exists at this revision (empty `map/ids.jsonl`). Structural
orientation instead comes from `map/INDEX.md`'s package listing (`scripts` 61 modules/1292 entities,
`tests` 98 modules/5430 entities) and direct `scripts/` directory listing taken during the census itself.

## Governing Constraints / Assumptions

- `docs/agents/GLOSSARY.md` "two-bin rule": every enforced invariant is either checked by a `command`, or
  attested by a named human — prose alone enforces nothing. This is the yardstick the census applies to
  every script.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` "Dogfooding" section: hook-code changes cannot be validated
  in-session (`CLAUDE_PROJECT_DIR` resolves once at session launch, issue #269); any hook edit this run
  makes must be proved from a fresh process, never an in-worktree observation.
- `docs/CHECKLIST_SCHEMA.md` documents `generate_spine.py`'s compiled format and the `because` field
  contract — read before ruling on its disposition.
- Compact-format `*.template.json` files are edited surgically, never round-tripped through
  `json.load`/`json.dump` (destroys blame); re-validate with `json.load` after.
- Windows CI is known-red; the local `pytest` run (3564 passed, 6 skipped at base) is the real gate.

## Decision Anchors & Decision Pressure

- decision -- census-before-mechanism — classify every check-shaped script live/unwired/dead with one
  evidence row before any mechanism decision.
  `@grade: settled/human · leans plan,g1`
- decision -- honest-null-is-a-win — a mostly-dead-code census ships as deletions and no lint, and that is
  a complete success, not a failed wave.
  `@grade: settled/human · leans g1,g2`
- decision -- registration-lint-shape — if warranted, build #345 options (1) registration lint and (2)
  vocabulary rule, not (3) handoff question.
  `@grade: guess/admiral · leans g2 · settle: census shows whether unwired scripts are unwired because
  nobody knew they existed (favors option 3) or because nothing checked (favors 1/2)`
- decision -- no-new-unwired-checker — hard constraint: any new lint must run somewhere that can fail
  (command check in a shipped template, pytest test, or CI job) — not another unwired checker.
  `@grade: settled/human · leans g2`
- decision -- report-only-names-its-trigger — a report-only refusing check must name its promotion trigger
  in the same PR; ship blocking where the adjudication is already in hand.
  `@grade: guess/admiral · leans g2 · settle: Admiral confirms with human at wave-2 checkpoint`
- decision -- 368-census-is-stale — re-measure the #368 field-group count from the current repo; do not
  copy the issue's stale "eleven".
  `@grade: settled/admiral · leans g3`
- decision -- 444-is-the-same-shape — try one consistency check over both #444 and #368's field groups;
  report plainly as two problems if it needs per-site special-casing.
  `@grade: guess · leans g3 · settle: attempt one shared check first; split only if forced`
- decision pressure — whether `generate_spine.py` (no caller found in the launch order's own grep) is
  wired into a genuinely live path this census must find, or is dead and should be deleted; this is a
  measurement, not yet made.

## Claims / Evidence Surfaces

- claim -- census-completeness — every check-shaped script in `scripts/` has exactly one classification row
  with an evidence string; re-checked by grepping the committed census file's row count against `ls
  scripts/{verify,check,prove,measure}_*.py | wc -l`.
- claim -- new-check-can-fail — any lint this run ships is proved to fail by a reproducible negative-case
  run, not asserted; re-checked by re-running that reproduction.
- claim -- field-group-count — the #368/#444 field-group counts are taken from the current repo, not the
  issue text; re-checked by re-running the same grep/count command this run used.

## Map Confidence / Staleness / Disputes

- The entire code-map/anchor system is **absent** at this revision (empty `map/ids.jsonl`, empty
  `docs/architecture/generated/map.json`) — not merely stale. This is itself a finding for **Map
  impact** in `RESULT.md`, not something this run silently works around. No scout/verify gate is
  planned to rebuild it: rebuilding the map is out of scope for this mission (it is not one of #345 /
  #444 / #368), and `python -m scripts.code_map build` is a separate, larger action than this wave's
  bounded ask. This gap is reported plainly to the Admiral instead.

## Out of Scope

- `scripts/checklist_engine.py`'s `match` comparison and `scripts/validate_spine.py` — fenced to sibling
  commander `w1-verdict`; float any needed change there instead of making it.
- Rebuilding `map/ids.jsonl` / `docs/architecture/generated/map.json` — a real gap, reported, not fixed
  in this wave.
- Building epic 569's wave-2 declared-basis machinery itself — this wave only settles whether
  `generate_spine.py` is wave 2's carrier path; it does not build wave 2's `because`-through-structure
  work.
- Filing GitHub issues — disfavoured exit per `LAUNCH_ORDER:Filing is the disfavoured exit`; fix-now or
  episode instead, filing only for a high-certainty run impact this wave cannot fix.
