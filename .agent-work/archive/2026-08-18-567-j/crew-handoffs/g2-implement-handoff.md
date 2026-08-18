# Implementer Handoff

## Gate
g2-implement

## Task
Add a pure, zero-I/O role×harness model-tier resolver to `scripts/run_crew.py`:
a module-level tier table plus a `resolve_model(role, harness, requested, reason)`
function. This gate adds **tested, unreferenced** code only — do not wire it
into `CrewLaunchSpec`, `build_parser`, or any dispatch path yet (that is g3).
The full existing suite must stay green and untouched.

## Protected Intent
The existing tierless-dispatch refusal (`CrewLaunchSpec.__post_init__` raising
`CrewLaunchError` when `model` is falsy, issue #611) must keep protecting
against a truly undeclared tier — this gate builds the piece that lets a
declared *role default* satisfy that protection instead of always refusing,
but that wiring happens in g3, not here.

## Test Mode
TDD preferred — this is new, pure, easily-testable logic with no existing
scaffolding to extend; write the test class alongside (or just ahead of) each
branch.

## Close Criteria
- Add `ROLE_MODEL_TIERS: dict[str, dict[str, dict[str, object]]]` to
  `scripts/run_crew.py`, keyed **harness -> role -> {"default": str, "allowed": frozenset[str]}**.
  Populate **only** harness `"claude"`:
  - `"admiral"`: `{"default": "opus", "allowed": frozenset({"opus"})}`
  - `"commander"`, `"implementer"`, `"reviewer"`, `"critic"`, `"cartographer"`:
    each `{"default": "sonnet", "allowed": frozenset({"sonnet", "haiku"})}`
  Add harness keys `"codex"` and `"local"` as **empty dicts** (`{}`) — the
  shape must express them; do **not** invent model identifiers for either (no
  codex/local dispatch exists anywhere in this repo today).
- Add a small frozen dataclass `ResolvedModel` with fields `model: str` and
  `reason: str | None`.
- Add `resolve_model(role: str, harness: str, requested: str | None, reason: str | None) -> ResolvedModel`,
  pure (no filesystem/subprocess/env access), living beside `build_crew_argv`.
  Exact branches, in this order:
  1. `(role, harness)` has no entry in `ROLE_MODEL_TIERS` (harness missing, or
     role missing under that harness) -> raise `CrewLaunchError` naming **both**
     the role and the harness explicitly (e.g. "no model tier declared for
     role 'implementer' under harness 'codex' -- refusing rather than
     guessing"). This is what makes an unpopulated codex/local dispatch refuse
     instead of inventing a model.
  2. `requested` is falsy (`None` or `""`) -> return
     `ResolvedModel(tier["default"], None)`. No reason required or recorded.
  3. `requested` is truthy and **not** in `tier["allowed"]` -> raise
     `CrewLaunchError` naming the requested model, the role, and the full
     allowed set (mirror the duplicate-crew-guard's named-refusal phrasing —
     grep the file for an existing `CrewLaunchError(f"...")` that names a
     rejected value against a known set, and match that style).
  4. `requested` is truthy, **in** `tier["allowed"]`, and **not equal to**
     `tier["default"]`, and `reason` is falsy -> raise `CrewLaunchError` naming
     the requested model, the default it would override, and that `--reason`
     is required.
  5. `requested` is truthy, in `tier["allowed"]`, and (`requested == tier["default"]`
     or `reason` is truthy) -> return `ResolvedModel(requested, reason)`.
     (A default-tier explicit choice never requires a reason even if one is
     passed — pass it through if given, but don't require it.)
- A full unit-test class (e.g. `ResolveModelTests`) exercising every one of
  the five branches above by direct import and function call — no argv, no
  subprocess, no filesystem. Include: each populated claude-harness role
  resolving to its own default with no `requested`; an out-of-set model
  refused (name the exact expected error-message substrings you assert on);
  a codex-harness and a local-harness call both refusing by name (branch 1);
  a non-default in-set choice with no reason refused (branch 4); the same
  choice with a reason succeeding and carrying the reason through (branch 5);
  a default-tier explicit choice never requiring a reason.
- Confirm by reading the file (not just running tests) that `resolve_model`
  and `ROLE_MODEL_TIERS` are **not referenced anywhere else** in
  `scripts/run_crew.py` outside their own definitions and your new tests —
  this gate is additive-only.

## Allowed Scope
- `scripts/run_crew.py` — only the new table, dataclass, and function, added
  beside `build_crew_argv`. No other edits.
- `tests/test_crew_launcher.py` — only the new test class.

## Specific Exclusions
- Do not touch `CrewLaunchSpec`, `build_parser`, `build_entry`, `main()`, or
  `resume_crew` — wiring is g3's job, not this gate's.
- `map/INDEX.md`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
  any `*SPINE*.template.json`, `specs/` — fenced to lane K this wave.
- Do not create a new file/module — this lives inside `run_crew.py` (avoids a
  new `SKILL_SCRIPT_BUNDLES`/`SCRIPT_RUNTIME_COMPANIONS` install-wiring entry
  that a separate module would need).

## Constraints
- `resolve_model`'s four parameters are exactly `role: str`, `harness: str`,
  `requested: str | None`, `reason: str | None`, in that order — a later gate
  (g3) calls it positionally-compatible with this signature, so do not
  reorder or rename.
- `ROLE_MODEL_TIERS`'s `"allowed"` values are `frozenset`, not `list`/`set` —
  g3's tests may assert on the type.

## Map Anchors (inbound)
No architecture map exists in this repo (DEGRADED-UNPARSEABLE, waived by the
Admiral this wave, evidence `e-plan-1`, `decision:map-index-is-admiral-owned`).
- **Map entry point:** `scripts/run_crew.py` — read `build_crew_argv` (for
  house style: how it's documented/tested) and `CrewLaunchSpec.__post_init__`
  (for the existing tierless-dispatch refusal's exact wording, which your new
  `CrewLaunchError` messages should read consistently beside, even though you
  are not editing that function this gate).
- **Decision anchors:**
  - `decision:ship-todays-tiers` — the exact table values above.
    `@grade: settled/human · leans g2-implement`
  - `decision:fail-closed-cheaper` — unset model resolves from role, never
    host settings. `@grade: settled/human · leans g2-implement`
  - `decision:refuse-by-name` — model outside allowed set refused by name.
    `@grade: settled/doctrine · leans g2-implement`
  - `decision:reason-on-deviation` — non-default in-set choice requires
    `--reason`. `@grade: settled/human · leans g2-implement,g3-implement`
  - `decision:harness-dimension-is-required` — table expresses codex/local;
    harness is declared via `--command`/`DEFAULT_LAUNCHER`, never detected.
    `@grade: settled/human · leans g2-implement`

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; `git check-ignore` exits 1 (not
  ignored) — verified before dispatch.
- **Committed** — `tests/test_crew_launcher.py`; `git check-ignore` exits 1
  (not ignored) — verified before dispatch.

## Required Evidence
- Full output of `py -m pytest tests/test_crew_launcher.py -q`, green,
  including your new test class's individual test names in the output.
- A `grep -n "resolve_model\|ROLE_MODEL_TIERS" scripts/run_crew.py` showing
  only the definitions plus zero other call sites in the file (confirms
  additive-only).
- The full existing suite's tally before/after your change should be
  identical except for your added tests — state the delta explicitly (e.g.
  "N pre-existing + M new = N+M total, 0 pre-existing changed").

## Wiring Grep
```bash
grep -rn "resolve_model" --include=*.py . | grep -v "def resolve_model"
```
Expected: only your new test file's call sites. State the count.

## Verification Commands
```bash
py -m pytest tests/test_crew_launcher.py -q
```

## Suggested Model Tier
sonnet — new pure logic with clear branch spec, bounded scope.

## Authority
The table's exact values, the five branch semantics (including their order —
branch 1's harness/role-missing check runs before any requested-value check),
and `resolve_model`'s exact parameter signature are fixed by this handoff.
Test structure, helper naming, and error-message exact wording (beyond "names
the role/harness/model/allowed-set/default" as stated) are yours.

## Stop Conditions
Stop and return if: the five branches cannot be expressed without wiring into
`CrewLaunchSpec` (they should not need to be — this is pure standalone logic),
or an existing test in `tests/test_crew_launcher.py` breaks (none should,
since nothing existing calls the new code).

## Return Format
Return IMPLEMENTER_RESULT per the standard shape, including Workflow Feedback.
Write it to `.agent-work/567-j/crew-handoffs/g2-implement-result.md` before
ending your turn.
