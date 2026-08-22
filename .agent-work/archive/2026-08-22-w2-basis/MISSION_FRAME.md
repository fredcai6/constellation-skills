# Mission Frame — w2-basis

Map DEGRADED-UNPARSEABLE (no Cartographer packet map exists for this repo; `docs/architecture/generated/map.json` is empty). Anchors below cite the substitutes `map_orient.py` hash-pinned into `.agent-work/w2-basis/map-orientation.json`: `map/INDEX.md` (code map) and `docs/CHECKLIST_SCHEMA.md`, plus `docs/CHECK_SCRIPT_CENSUS.md` (wave-1 committed doc, not a substitute but load-bearing prior evidence) and direct source reads of `scripts/checklist_engine.py`. Anchor ids below are `file:symbol` / `file:line-range` pairs, not packet-map node ids, per the DEGRADED discharge.

## Intent
Make a qualitative (`check: null`) postcondition state, at plan (authoring) time, what evidence would satisfy it — a "basis" — then make the engine (a) render that basis to the agent at the moment the gate is active, and (b) refuse a bare assertion at `attest` unless the basis is discharged with a resolvable locator. Ship the mechanism plus authored basis for exactly ONE shipped template (`skills/commander/templates/COMMANDER_SPINE.template.json`, 19 `check: null` postconditions, 0 `because`) as proof, not a 65-condition rollout.

## Affected Capabilities
- `checklist_engine.py:attest` (line ~3404-3472) — the verb that currently satisfies any `check: null` condition unconditionally: `c["satisfied_by"] = note or "attested"` with no minimum note shape. This is the refusal surface.
- `checklist_engine.py:render_human` (line ~2679-2749) + `_condition_view`/`state()` — the projection `current` renders from. Constraints/anchors/directives already render as populated-only blocks; a basis needs the same treatment or it is decorative (per `ruling-decorative-basis-is-a-failure`).
- `checklist_engine.py:Condition` schema (`docs/CHECKLIST_SCHEMA.md` §Condition, line ~213-236) — `id`, `statement`, `check`, `satisfied`, `satisfied_by`, `override_policy`, `waived`, `attested`. No `basis`/`because`/locator field exists on a Condition today.
- Hand-written templates under `skills/*/templates/*.template.json` (20 files, 105 postconditions, 65 `check: null`) — the actual authoring surface per `ruling-basis-lives-in-hand-written-templates`.

## Examples / Events
- `checklist_engine.py:3431-3434` — the exact quoted attest path from the launch order, confirmed byte-for-byte at this run's HEAD.
- `generate_spine.py:512-521` (`compile_condition`, `kind == "qualitative"`) — the compiler's own convention: `statement = f"{statement} -- QUALITATIVE: {cond['because']}"`, `check = None`. This is a **live precedent for folding a basis into the statement string**, but it is exactly the "decorative" shape the epic's hard constraint forbids reusing verbatim: text folded into `statement` renders (it's already inside what `render_human` prints per condition) but is **not required at attest** — `attest` never parses `statement` — so borrowing this convention unmodified would satisfy render but not require.

## Structural Anchors
- `scripts/checklist_engine.py:attest` (primitive, ~70 lines) — level: engine verb.
- `scripts/checklist_engine.py:render_human` / `_condition_view` (primitive) — level: engine projection.
- `skills/commander/templates/COMMANDER_SPINE.template.json` (compact-format JSON, hand-edited surgically per doctrine) — level: shipped template, the one this wave authors basis into.
- `.agent-work/templates/` — overlay mirror with `.baseline` copies; changing the shipped template means syncing both (Inherited Context).

## Governing Constraints / Assumptions
- `ruling-basis-lives-in-hand-written-templates` — target the templates + engine; never `generate_spine.py`/`specs/`. What breaks if ignored: re-opens the out-of-scope migration wave 1 measured as stalled.
- `ruling-decorative-basis-is-a-failure` — hard constraint: authored, rendered, AND required-at-attest, together. What breaks if ignored: ships exactly the `map_check_note`-shaped defect the epic exists to kill (template-only prose, read by no code, per `TemplateOnlyFieldAllowlist` in `tests/test_checklist_engine.py`).
- `ruling-engine-first-backfill-where-it-earns-it` — ONE template only; backfill elsewhere needs measured evidence of loose attestation (episode store / archived spines), not blanket authoring.
- `ruling-widening-live-refusal-report-only` — rendering ships live (widening); a new attest refusal ships report-only with a named promotion trigger, unless the Admiral's adjudication is in hand at authoring time.
- `ruling-no-new-unwired-checker` — any new script-shaped check must run somewhere that can fail it (template `command` check, pytest, or CI).
- `ruling-report-only-names-its-trigger`, `ruling-red-proof-pinned-to-shipped-revision`, `ruling-no-spec-migration` — standing epic pre-rulings, unconditional.
- **Dogfooding constraint** (`ORCHESTRATOR_CONTEXT.md`): this run edits `checklist_engine.py`, the engine its own MCP door is running. Any in-session observation of the edited engine's live behavior (e.g. calling `attest`/`current` through this run's own bound door after editing `checklist_engine.py`) is not evidence — validate engine-code changes as fresh-process runs with explicit paths (a standalone `python scripts/checklist_engine.py ...` CLI invocation against a throwaway checklist fixture, or the pytest suite), not by re-querying this run's own live MCP door.
- **Two-bin rule** (`GLOSSARY.md`): every enforced invariant is either checked by a command or attested by a named human — prose alone enforces nothing. This is the glossary-level restatement of the epic's own thesis.

## Decision Anchors & Decision Pressure
- `ruling-locator-definition-is-yours` — what counts as a *resolvable* locator for a basis is the open design question this wave must settle via plan-alternatives against the real 19 conditions in `COMMANDER_SPINE.template.json`.
  `@grade: guess · leans plan-alternatives,g1-implement · settle: apply each candidate locator shape to the 19 conditions and count how many express a real (re-runnable/re-readable-by-a-stranger) locator vs degenerate into prose`
- decision pressure: refusal blocking-vs-report-only for the new attest check — `ruling-widening-live-refusal-report-only` defaults report-only; promote to blocking only if the Admiral's adjudication is in hand at authoring time. Surface at plan approval.
- decision pressure: whether the basis lives as a new sibling `Condition` field (e.g. `basis`) or is folded into `statement` with a parseable delimiter — this is the render/require design itself, resolved by plan-alternatives.

## Claims / Evidence Surfaces
- `docs/CHECK_SCRIPT_CENSUS.md:126-127` — `grep -c '"because"' skills/commander/templates/COMMANDER_SPINE.template.json` → 0; re-confirmed this run at current HEAD (0 because, 19 check:null).
- `docs/CHECK_SCRIPT_CENSUS.md:134-152` — `generate_spine.py`'s `because`-requiring compile step is live (via `spine_lifecycle.open_work` → MCP `spine_open`) but invisible to any of the 19 shipped role skills' actual stand-up path (`init_work_area.py --spine <template>`, raw placeholder substitution, never compiles).
- `episodes/active/569-001.md` (569-001.a3/a5) — the spec-to-template migration is stalled and explicitly out of scope; hand-editing shipped templates is the ratified working method.
- `tests/test_checklist_engine.py::TemplateOnlyFieldAllowlist` / `TaskFieldCompleteness` — the existing regression pattern this wave's new field(s) must not silently violate: a populated field the engine's own render skips is exactly the failure class named in `ruling-decorative-basis-is-a-failure`.
- `docs/CHECKLIST_SCHEMA.md` §"Rendering" (issue #420/#433) — precedent: `constraints`/`anchors`/`directives` render on `current` only when populated, and a `TaskFieldCompleteness` property test catches a populated-but-unrendered field going forward. The new basis mechanism should extend this same tested pattern rather than inventing a parallel one.

## Map Confidence / Staleness / Disputes
- Packet-map absent for the whole repo (DEGRADED-UNPARSEABLE, `map/ids.jsonl` empty, `docs/architecture/generated/map.json` empty). This alters the plan: no Cartographer packet exists to verify a structural claim against, so every structural anchor above is a direct, freshly-re-run source/grep read (dated to this run's HEAD) rather than a map citation — this is the DEGRADED substitute path, not silent trust. `reconcile` will fold the resulting structural change into `docs/CHECKLIST_SCHEMA.md` directly (no packet map exists to reconcile into), per commander-core.md's Architecture bookend "no packet map" branch.

## Out of Scope
- `generate_spine.py`, `specs/*.toml`, and the spec-to-template migration (`ruling-no-spec-migration`).
- Authoring basis for all 65 conditions — only `COMMANDER_SPINE.template.json`'s 19 (`ruling-engine-first-backfill-where-it-earns-it`); backfill elsewhere requires separate measured evidence.
- The `w2-ledger` lane's override paths in `checklist_engine.py`: `waive()`, forced claim/release, `consolidate --override-reason`, and the trip ledger — fenced, do not edit.
- Making the new attest refusal blocking (default report-only per `ruling-widening-live-refusal-report-only`) absent an in-hand Admiral adjudication.
