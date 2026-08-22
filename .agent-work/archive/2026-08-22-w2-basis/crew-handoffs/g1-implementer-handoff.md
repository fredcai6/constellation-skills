# Implementer Handoff

## Gate
g1 (g1-implement)

## Task
Add a new, report-only `basis` sibling field to the `Condition` schema in `scripts/checklist_engine.py`, so a `check: null` (qualitative) postcondition can declare, at plan-authoring time, a resolvable locator (`file` or `evidence_ref`) that the engine renders when the gate is active and checks (report-only, never blocking) when the condition is attested — without changing behavior for any condition that does not carry a `basis`.

## Protected Intent
Every existing `check: null` condition without a `basis` field must attest **exactly as it does today** — unchanged legacy behavior (`c["satisfied"] = True; c["satisfied_by"] = note or "attested"`). This gate must not make any existing shipped template's attest path stricter, slower, or different in any observable way. The new guard is strictly additive.

## Test Mode
TDD required. Write the red-proof test(s) first against a throwaway fixture checklist (not a real shipped template — g2, a separate gate, edits the real template), confirm they fail against the current engine, then implement until green.

## Close Criteria
- `Condition` schema gains an optional `basis` field: `{"locator_kind": "file"|"evidence_ref"|"abstain", "locator": {...}, "because": "<optional string>"}`. Absent `basis` = unchanged behavior (verify with a test).
- `render_human` (scripts/checklist_engine.py, currently ~line 2679-2749) emits one additional indented line under an open condition, immediately after its `{id} [unmet] {kind} — {statement}` line, **only when** `c.get("basis")` is populated and `basis.get("locator_kind") != "abstain"` — e.g. `    basis: file .agent-work/<work-id>/MISSION_FRAME.md`. Same populated-only rendering convention `constraints`/`anchors`/`directives` already use (see `_render_anchor_lines`/`_render_directive_lines` for the existing pattern to follow, not copy verbatim).
- `attest()` (currently ~line 3404-3472), inside the existing `if chk is None:` branch, gains a new guard inserted **before** the unconditional `c["satisfied"] = True` accept:
  - If `c.get("basis")` is absent, or its `locator_kind == "abstain"`: skip the guard entirely, fall through to the unchanged legacy accept.
  - Otherwise, resolve the locator via a new small dispatcher `_resolve_basis_locator(cl, base_dir, basis) -> str | None` (`None` = resolved; a string = the problem, human-readable):
    - `locator_kind == "file"`: `locator = {"path": str, "glob": bool (optional, default false), "min_matches": int (optional, default 1)}`. Resolve `path` relative to `base_dir` (the same base the engine's existing `command`-kind checks resolve against — check how `_run_check_command` or the nearest existing file-resolution helper does this, and reuse that resolution logic rather than inventing a second one). When `glob` is true, use glob matching and require at least `min_matches` matches; when false, require the exact path to exist.
    - `locator_kind == "evidence_ref"`: `locator = {"task_id": str, "cond_id": str}`. Resolve by walking `cl["tasks"][task_id]`'s preconditions+postconditions for `cond_id`, requiring it `satisfied` with a non-null `satisfied_by`.
  - Regardless of resolved/unresolved, **always** attach a new evidence item of type `"basis-check"` to the checklist (use the engine's existing internal evidence-append helper — the same one `attach()` uses — do not duplicate that logic) with payload `{"locator_kind": ..., "locator": ..., "resolved": bool, "problem": str|null}`. This must happen on every attest of a basis-bearing condition, pass or fail — it is what makes a future promotion decision auditable.
  - This is **report-only**: on an unresolved locator, do **not** raise — attach the evidence, then fall through to the same unconditional accept every other `check: null` condition gets. Never block.
- Two locator kinds only: `file` and `evidence_ref`. Do **not** implement `state_field` or `command` — explicitly out of scope this gate (named untaken roads in the plan).
- `docs/CHECKLIST_SCHEMA.md`'s `## Condition` field table gets a new row for `basis`, and a new short subsection (near the existing "Qualitative conditions (`check: null`) — trust but verify" section) documenting: the field shape, the two locator kinds, that it is report-only by design, and that a `basis-check` evidence item is always attached (this is the durable record a future promotion-to-blocking decision is measured against).
- A fresh-process test (pytest, run via `python -m pytest`, not through this run's own live MCP door — the dogfooding constraint: this engine is the one your own session's door is running, so an in-session live-door observation after editing it is not evidence) demonstrates, against a throwaway fixture checklist you construct in the test:
  1. A `check: null` condition with no `basis` attests exactly as before (same `satisfied_by` shape as pre-change).
  2. A condition with a populated `file` basis whose target is **missing** still attests successfully (report-only — no exception raised) AND a `basis-check` evidence item with `resolved: false` is recorded.
  3. Same, but target **present**: attests successfully, `basis-check` evidence with `resolved: true`.
  4. A condition with `locator_kind: "abstain"` behaves exactly like no-basis (no `basis-check` evidence attached, no extra render line).
  5. `render_human`/`current` output includes the `basis:` sub-line only for the populated, non-abstain case.
- Full `tests/test_checklist_engine.py` suite passes (including the existing `GoldenOutputBriefing` class — if your render change alters any EXISTING shipped template's `current` output, that is a real regression to fix, not a fixture to update, since no shipped template carries a `basis` field yet at this gate).

## Allowed Scope
- `scripts/checklist_engine.py` — add the `basis` field support (schema is implicit/dict-based in this codebase, not a separate typed schema file — check how `override_policy`, an existing optional sibling field, is threaded through to see if there's a central place types are declared, or if it's purely dict-shaped throughout).
- `docs/CHECKLIST_SCHEMA.md` — document the new field.
- `tests/test_checklist_engine.py` — add your new red-proof tests here, following the existing test-class organization in this file (e.g. near the existing artifact-check tests).
- Pre-authorized: any test fixture data/harness in `tests/test_checklist_engine.py` that already exercises `attest()`/`render_human()`, if a legitimate minimal reconciliation is needed (e.g. the `GoldenOutputBriefing` fixture set, if and only if your render change requires it — it should not, per the Protected Intent above, but if it genuinely does, name that explicitly in your result).

## Specific Exclusions
- Do **not** touch `skills/commander/templates/COMMANDER_SPINE.template.json` or any other shipped template — that is gate g2's scope, a separate gate, dispatched after this one.
- Do **not** touch `scripts/generate_spine.py` or anything under `specs/` — out of scope for the whole epic wave.
- Do **not** touch `checklist_engine.py`'s `waive()`, forced claim/release, `consolidate --override-reason`, or `trip_ledger` code paths — fenced to the `w2-ledger` lane running in a sibling worktree; touching them risks colliding with that lane's own in-flight evidence.
- Do **not** implement `state_field` or `command` locator kinds — named untaken roads, not this gate's job.
- Do **not** make the new guard blocking under any config or flag — report-only is not a toggle to add "for completeness"; there is no blocking mode to build this gate.

## Constraints
- `basis` object fields: `locator_kind` (string, one of `"file"|"evidence_ref"|"abstain"`), `locator` (dict, shape depends on `locator_kind`; absent/`{}` when `locator_kind == "abstain"`), `because` (optional string, one-line authoring rationale — never a substitute for the locator, never parsed/required by any code, purely for human readers).
- The new `_resolve_basis_locator` dispatcher should be **pure where possible** — no side effects for `evidence_ref` (reads `cl` only); `file` resolution touches the filesystem (`base_dir`), which is unavoidable but keep it isolated to that one function, mirroring the existing `git-change-policy` evaluator/collector purity split documented in `docs/CHECKLIST_SCHEMA.md`.
- Never round-trip any shipped `*.template.json` through `json.load`/`json.dump` — not applicable to this gate (you touch no template), stated for awareness since g2 will inherit this constraint.

## Map Anchors (inbound)
- **Map entry point:** `.agent-work/w2-basis/MISSION_FRAME.md` (this repo has no packet map — DEGRADED-UNPARSEABLE — the mission frame is the map-context artifact for this run; read it first).
- **Structural:** `scripts/checklist_engine.py:render_human` (~2679-2749), `scripts/checklist_engine.py:attest` (~3404-3472) — where this gate's two edits land.
- **Constraints/assumptions:** `ruling-decorative-basis-is-a-failure` (basis must be authored+rendered+required-report-only, together, or it is decorative) | `ruling-widening-live-refusal-report-only` (this is genuinely new attest code — report-only is not optional) | INV-2 purity (`docs/CHECKLIST_SCHEMA.md`, `checklist_engine.py:~2363-2368`) — `state()`/`render_human`/`_condition_view` must never probe live state or run a check; your new render line reads only the stored `basis` dict off the condition, never triggers resolution — resolution happens only inside `attest()`, which is the correct place per INV-2 (only `start()`/`advance()`/`attest()` actually run checks).
- **Decision anchors:** the locator-kind vocabulary is narrowed to `file`/`evidence_ref` only, per `.agent-work/w2-basis/PLAN_ALTERNATIVES.md`'s critic-corrected design (`state_field`/`command` are named untaken roads — real designs exist in `.agent-work/w2-basis/plan-candidate-structured-field.md` §1 if you want to see why they were considered and declined, but do not build them).
  `@grade: settled/human — this is the ratified plan for this wave, not open for re-litigation at implementation time`
- **Evidence expectations:** `.agent-work/w2-basis/PLAN_CRITIC.md` findings 5 and 6 — the promotion-trigger auditability requirement (finding 5, satisfied by always-attach `basis-check` evidence) and the honest justification for building new schema at all (finding 6, rollout safety not expressiveness — see PLAN_ALTERNATIVES.md's revised Output section item 5).

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`; `git check-ignore scripts/checklist_engine.py` exited 1 (not ignored).
- **Committed** — `docs/CHECKLIST_SCHEMA.md`; `git check-ignore docs/CHECKLIST_SCHEMA.md` exited 1 (not ignored).
- **Committed** — `tests/test_checklist_engine.py`; `git check-ignore tests/test_checklist_engine.py` exited 1 (not ignored).

## Required Evidence
- **Load-bearing**: the fresh-process pytest run output for your new tests, red-then-green (paste both the pre-implementation failure and the post-implementation pass).
- **Load-bearing**: full `tests/test_checklist_engine.py` suite result (exact pass count, e.g. "1234 passed").
- **Confirmatory**: a one-line diff-stat (`git diff --stat`) confirming only the three allowed-scope files changed.
- Quote your test's exact expected `basis-check` payload shape in your result, not just "it works" — e.g. `{"locator_kind": "file", "locator": {"path": "...", "glob": false}, "resolved": false, "problem": "..."}`.

## Wiring Grep
```bash
grep -rn "_resolve_basis_locator\|basis-check" --include=*.py . | grep -v "def _resolve_basis_locator"
```
State the count of call sites found for `_resolve_basis_locator` (expect exactly 1: the new `attest()` guard) and for the `"basis-check"` evidence-type string (expect at least 2: the `attach`-equivalent call site in `attest()`, and your test assertions).

## Verification Commands
```bash
cd /home/tommy/projects/569-w2-basis && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q tests/test_checklist_engine.py
```

## Suggested Model Tier
stronger — reason: this is a load-bearing engine change (new Condition field, new attest code path) that must not regress any of the ~20 shipped templates' existing behavior; the INV-2 purity invariant and the report-only-not-blocking requirement both need careful reasoning to get right on the first pass.

## Authority
The design (basis field shape, two locator kinds, report-only-always, basis-check evidence persistence) is ratified in `.agent-work/w2-basis/PLAN_ALTERNATIVES.md` after a 3-candidate design-it-twice panel and a cold critic pass — do not re-derive or second-guess the mechanism shape; implement it as specified. If you find the specified shape is genuinely unbuildable as written (not just inconvenient), stop and report why rather than substituting your own design.

## Stop Conditions
Stop and return if: the render or attest change appears to require modifying any EXISTING shipped template's behavior (Protected Intent violation), the specified basis shape cannot be threaded through the codebase's existing dict-based Condition representation without a larger refactor than this gate's scope allows, or you find `_check_condition`/`attest`/`render_human` do not match this handoff's line-number references closely enough to locate the right insertion points (the codebase may have moved since this handoff was authored — verify against the live file, don't guess).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full `IMPLEMENTER_RESULT` to `.agent-work/w2-basis/crew-handoffs/g1-implementer-result.md` before ending your turn.
