# Implementer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
g1 (issue #329, workstream D of epic #418)

## Task
Convert the prose-only worktree-isolation invariant into a real engine gate, plus an enumeration check
that catches a template left out.

1. Add ONE command **precondition** to `skills/commander/templates/COMMANDER_SPINE.template.json`'s
   `init` gate: `{"id": "c0", "statement": "this Commander is operating in the worktree it was
   provisioned into, not the shared checkout or another agent's worktree -- proven, not asserted",
   "check": {"kind": "command", "command": "python scripts/verify_worktree_isolation.py --here
   <repo-root>"}, "satisfied": false}`. Put it FIRST in the `preconditions` array (currently `[]`).
   `<repo-root>` is a token already resolved by `instantiate_spine()`/`resolve_spine()` in
   `scripts/init_work_area.py` — do not invent new resolver machinery. Do not touch
   `verify_worktree_isolation.py` itself — it is correct and unmodified.
2. Write `scripts/verify_worktree_precondition_coverage.py`: a standalone CLI script (standard library
   only, matching the style of `scripts/verify_state_note.py`/`scripts/verify_cycles.py`) that:
   - Holds an explicit, commented Python list/tuple naming the "worktree-entering" templates — today
     exactly one entry: `skills/commander/templates/COMMANDER_SPINE.template.json`, gate `init`. Document
     in the module docstring WHY membership is a maintained list rather than an auto-detector: which
     roles get dispatched into an isolated worktree (via an Admiral `LAUNCH_ORDER`) is an architectural
     fact about the fleet, not something derivable by scanning spine JSON content — Admiral provisions
     worktrees for Commanders but does not itself enter one; Explorer is human-synchronous/upstream-only
     and never delegated into a worktree. Note explicitly: adding a new worktree-entering role means
     adding it to this list by hand — that is a known, accepted limit, not silently covered.
   - For each listed `(template_path, gate_id)`, load the template's JSON, find the named gate, and
     assert it has an unmet-by-default `preconditions` (or `postconditions`) entry whose `check.command`
     contains `verify_worktree_isolation.py`. Missing → exit 1, print the offending template path and gate
     id by name (a script that only prints "FAIL" without naming what failed repeats the #329 defect at
     the reporting layer).
   - All templates present and wired → exit 0, print how many templates were checked (the "assert what you
     looped over" mechanical detector from `references/global-orchestrator.md` "A check that cannot fail" —
     state the count, do not just say "OK").
   - CLI: `python scripts/verify_worktree_precondition_coverage.py [--root PATH]` (default cwd), no other
     required args.
3. Tests, landed in `tests/test_worktree_precondition_wiring.py` (new file), run via the repo's existing
   pytest suite — NOT manual scratch demonstrations:
   - **Enumeration deliberate breakage**: copy `COMMANDER_SPINE.template.json` into a `tmp_path` fixture,
     strip the new precondition from the copy's `init` gate, run the coverage script against that broken
     copy (point `--root` at the tmp dir with the same relative `skills/commander/templates/...` layout, or
     parametrize the script to accept an override — implementer's call, document which), and assert exit
     code 1 / nonzero. Then run it against the real (fixed) repo tree and assert exit 0. Both assertions in
     the same test — a check that only ever demonstrates the pass side is not proven to fail on a genuine
     omission (the #392 shape this issue exists to prevent).
   - **Engine deliberate breakage**: using `scripts/checklist_engine.py`'s Python API (see
     `tests/test_checklist_engine.py` for the existing pattern — import functions directly, build a
     minimal in-memory or `tmp_path`-written gated checklist with one `init`-like gate carrying the new
     precondition), call `start()` with a command whose `--here <expected>` does NOT match the actual
     `git rev-parse --show-toplevel` (e.g. expect a nonexistent/sibling path) and assert `start()` raises
     `EngineError` naming the unmet precondition. Then fix the expected path to the real worktree root and
     assert `start()` succeeds. This proves the WIRED precondition — not just the standalone script —
     actually blocks `start`, mirroring how `advance()`'s postconditions already block `advance` (see
     `checklist_engine.py:1699`).
   - Both deliberate-breakage constructions run in `tmp_path`/temp fixtures only, never against this
     worktree's own `.git` or the shared checkout, and clean up automatically as pytest teardown (no
     manual revert needed — nothing persists outside the fixture).

## Protected Intent
The worktree-isolation invariant (`skills/_shared/windows.md` hazard #3: "that is data loss, not
friction") gets a REAL engine gate a Commander cannot silently skip, not a second layer of prose. Do not
weaken `verify_worktree_isolation.py`'s existing pass/fail semantics.

## Test Mode
Test-after allowed (wiring existing, already-tested rail scripts into the engine, not new business logic) —
but the deliberate-breakage tests are the acceptance criteria themselves, not incidental coverage; they
must exist and must actually flip red-to-green across the fix.

## Close Criteria
- `skills/commander/templates/COMMANDER_SPINE.template.json`'s `init` gate has the new `c0` precondition,
  valid JSON (re-validate with `json.load` after the surgical text edit).
- `scripts/verify_worktree_precondition_coverage.py` exists, exits 0 against the fixed real tree, states
  the count of templates checked.
- `tests/test_worktree_precondition_wiring.py` exists and passes; it contains at least one assertion that
  fails when the fix is absent (verified by you running it against a `git stash`ed/reverted copy of the
  template, or equivalent, before finalizing — report which method you used).
- Full existing suite (`python -m pytest tests/ -q`) stays green — no regressions.

## Allowed Scope
- `skills/commander/templates/COMMANDER_SPINE.template.json` (the `init` gate's `preconditions` array only
  — do not touch any other gate).
- New file `scripts/verify_worktree_precondition_coverage.py`.
- New file `tests/test_worktree_precondition_wiring.py`.
- Pre-authorized: reading (not modifying) `scripts/checklist_engine.py`, `scripts/verify_worktree_isolation.py`,
  `tests/test_checklist_engine.py`, `tests/test_verify_worktree_isolation.py`,
  `skills/admiral/templates/LAUNCH_ORDER.template.md`, `skills/admiral/templates/ADMIRAL_SPINE.template.json`,
  `skills/explorer/templates/EXPLORER_SPINE.template.json` for pattern/precedent.

## Specific Exclusions
- Do NOT modify `scripts/checklist_engine.py` — this gate's fence is wiring the template + the new
  standalone script only. If you find you need an engine change to make the deliberate-breakage test work,
  STOP and report it as a blocker rather than editing the engine (workstream B/#420 shares this file and
  owns the rendering path this wave).
- Do NOT modify `scripts/verify_worktree_isolation.py`.
- Do NOT touch any other gate in `COMMANDER_SPINE.template.json` (context/understand/plan/execute/reconcile/
  triage/review/feedback/archive) — this gate is `init` only.
- Do NOT build the PreToolUse-hook mechanism #329's own issue text speculates about — out of scope, per
  the confirmed spec (DESIGN_SPEC.md T13); the command-precondition + enumeration design is the whole ask.

## Constraints
- `<repo-root>` resolves via `scripts/init_work_area.py`'s existing `resolve_spine()`; do not add a new
  placeholder token.
- The check command runs under a POSIX shell per the engine's `_run_check_command` — plain
  `python scripts/verify_worktree_isolation.py --here <repo-root>` needs no `&&`/pipe/grep, so this is a
  non-issue here, but keep the command simple/POSIX-safe regardless.
- `_run_check_command` passes no `cwd=` (issue #315, open, out of scope) — the command above uses no
  relative paths besides `scripts/...` (repo-root-relative, matching every other shipped command-check in
  this corpus), so it inherits the same accepted fragility as those, not a new one.

## Map Anchors (inbound)
- **Structural:** `scripts/checklist_engine.py:1635` `start()` — the existing precondition-check mechanism
  this rides, unchanged.
- **Capability:** Commander spine `init` gate — proves worktree isolation before any git operation.
- **Constraints/assumptions:** Only `COMMANDER_SPINE.template.json`'s role is dispatched into an isolated
  worktree via a `LAUNCH_ORDER` today — the enumeration list has exactly one entry; do not add entries for
  roles that do not actually enter worktrees.
- **Decision anchors:** `decision:worktree-entering-membership` — explicit maintained list, not a heuristic.
  `@grade: guess · leans g1-implement · settle: confirm the enumeration check's refusal-on-omission fires
  when a second worktree-entering spine ships`
- **Evidence expectations:** `claim:no-template-wires-isolation` — re-confirm
  `grep -rln verify_worktree_isolation skills/*/templates/*.json` is non-empty (COMMANDER_SPINE only) after
  your change; it was empty before.

## Deliverable Path Check
- **Committed** — `skills/commander/templates/COMMANDER_SPINE.template.json`; existing tracked file, no
  check needed (already committed).
- **Committed** — `scripts/verify_worktree_precondition_coverage.py`; `git check-ignore` on this path (run
  before your commit) must exit 1 (not ignored). Verified pre-dispatch: `git check-ignore
  scripts/verify_worktree_precondition_coverage.py` → exit 1 (not ignored).
- **Committed** — `tests/test_worktree_precondition_wiring.py`; same check, exit 1 confirmed pre-dispatch.

## Required Evidence
- `python -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json', encoding='utf-8'))"`
  → prints nothing / exits 0 (valid JSON after the surgical edit).
- `python scripts/verify_worktree_precondition_coverage.py` → exit 0, states the count checked.
- `python -m pytest tests/test_worktree_precondition_wiring.py -q` → all pass, paste full output.
- `python -m pytest tests/ -q` → full suite green, paste the summary line (pass/fail counts).
- State explicitly HOW you proved the deliberate-breakage tests fail red without the fix (temporarily
  reverted file + re-run, or a fixture that constructs the "before" state directly) — load-bearing evidence,
  not confirmatory.

## Wiring Grep
`grep -rn "verify_worktree_precondition_coverage" --include=*.py .` — must show at least the test file
calling it as a subprocess/import, beyond its own `if __name__ == "__main__"` definition. State the count
of call sites found (expect ≥1: the test file).

## Verification Commands
```bash
python -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json', encoding='utf-8'))"
python scripts/verify_worktree_precondition_coverage.py
python -m pytest tests/test_worktree_precondition_wiring.py -q
python -m pytest tests/ -q
```

## Suggested Model Tier
Sonnet — bounded, well-precedented (mirrors 7 existing command-postcondition examples plus
`test_checklist_engine.py`'s existing test patterns), no architectural ambiguity.

## Authority
Design already made (LAUNCH_ORDER D-422 + DESIGN_SPEC.md section D, Tommy-approved 2026-08-03): wire as a
command-check precondition + enumeration check, not a PreToolUse hook. Do not re-litigate that choice.
Membership-list scope (which templates count as worktree-entering) is pre-decided above (one entry) — if
you find a second candidate template during implementation, name it in your return as a triage candidate,
do not add it to the list yourself (spec-deviation-adjacent, floats to the Commander).

## Stop Conditions
Stop and return if: the fix requires touching `checklist_engine.py`; a second worktree-entering template
surfaces and you're unsure whether to include it; the deliberate-breakage test cannot be made to fail
without the fix using a temp-only fixture; any required evidence cannot be produced.

## Return Format
Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence produced
(paste the actual commands + output), assumptions used, stop conditions hit, out-of-scope observations,
workflow feedback. **Deliver it via `SendMessage` to the dispatching Commander before ending your turn** —
do not end idle with the result unsent.
