# Implementer Handoff

## Gate
g3-implement

## Task
Wire g2's `resolve_model` into `CrewLaunchSpec.__post_init__` — the **single
choke point** every crew dispatch (both backends, and every public wrapper
function) passes through — replacing the current flat
`if not self.model: raise CrewLaunchError(...)` check. Add `--reason`
end-to-end: CLI flag, `CrewLaunchSpec` field, threaded into the registry.

## Protected Intent
Every `CrewLaunchSpec` construction anywhere in the file — not just the ones
`main()` builds — must go through `resolve_model`. `resume_crew()` is the one
deliberate exception: it replays an already-resolved `model`/`reason` from a
prior registry entry verbatim and must never re-resolve or require
`--model`/`--reason` again.

## Test Mode
Test-after allowed for the wiring itself (mechanical once g2's function is
trusted); TDD for the five new/rewritten behavioral tests named below.

## Close Criteria
- Add `reason: str | None = None` field to `CrewLaunchSpec`.
- In `CrewLaunchSpec.__post_init__`, **replace** the existing
  `if not self.model: raise CrewLaunchError(...)` block with a call to
  `resolve_model(role=self.role, harness=self.launcher, requested=self.model, reason=self.reason)`,
  then set `self.model` and `self.reason` from the returned `ResolvedModel`.
  First check whether `CrewLaunchSpec` is declared `@dataclass(frozen=True)`:
  if frozen, you must use `object.__setattr__(self, "model", resolved.model)`
  (and same for `reason`) since plain attribute assignment raises inside a
  frozen dataclass's own `__post_init__`; if not frozen, plain assignment is
  fine. This is the **entire** fix for the bypass risk: because every
  `CrewLaunchSpec(...)` construction anywhere in the file — `main()`'s
  fresh-launch and abandon+relaunch paths, **and** the public wrapper
  functions `launch_crew()` and `record_external_attempt()` (grep for both;
  neither is called from `main()` today, but both build a `CrewLaunchSpec`
  directly and must not bypass resolution) — runs through `__post_init__`,
  this single edit automatically covers all of them. Do not add a separate
  pre-resolution step anywhere else.
- `resume_crew()` stays **completely untouched** — verify it does not call
  `resolve_model`, does not construct a fresh `CrewLaunchSpec` with
  user-supplied `model`/`reason`, and requires neither flag. (It replays a
  prior registry entry's `model` verbatim — read how it currently does this
  before touching anything nearby.)
- Add `p.add_argument("--reason")` to `build_parser()` (plain optional flag,
  same shape as `--parent`).
- Thread `spec.reason` into `build_entry()` at both existing `build_entry(...)`
  call sites (the cli-backend path and the external-backend path — grep for
  `build_entry(` to find both) as a new keyword argument. In `build_entry`
  itself, add `if reason: entry["reason"] = reason` immediately beside the
  existing `if model: entry["model"] = model` line (same "recorded when
  present" shape — do not use the "recorded null, not omitted" shape `spine`
  uses).
- Thread `args.reason` into `main()`'s `CrewLaunchSpec(...)` construction
  (the fresh-launch path).
- Update `CrewLaunchSpec`'s docstring/the removed check's error text: it must
  no longer claim unconditionally that "no default is invented" — say instead
  that a role/harness **with** a table entry now resolves a default, and only
  an undeclared role/harness, an out-of-set choice, or an unreasoned
  non-default choice refuses.
- Rewrite the two existing tests that currently assert a **no-`--model`**
  dispatch is refused for a **populated** role (grep `MandatoryModelTests` for
  both: the fresh-dispatch case and the abandon-relaunch case) — both must now
  assert **resolved-default** behavior instead (no exception, `model` in the
  built entry equals the role's table default) for any role/harness pair that
  IS in `ROLE_MODEL_TIERS` (e.g. `role="implementer", launcher="claude"`).
  Keep a still-refusing case for a role/harness pair that is genuinely absent
  from the table (e.g. `launcher="codex"`).
- Add new tests: (a) explicit out-of-set model refused by name (assert the
  message names the model, role, and allowed set); (b) unpopulated harness
  (`launcher="codex"` or `"local"`) refused by name even with a `--model`
  given; (c) non-default in-set model with no `--reason` refused; (d) same
  choice **with** `--reason` succeeding, and the resulting registry entry
  (via `build_entry` directly, or a full dispatch-level test reading back
  `crew-runs.json`) carrying `"reason"` beside `"model"`; (e) a default-tier
  dispatch (explicit or resolved) never requires or records a `reason` key at
  all in the entry.
- Confirm an **old-shape** `crew-runs.json` entry (a `model` key present, no
  `reason` key at all) round-trips through `resume_crew()` and any other
  reader without error — add a small test for this if none already covers it.

## Allowed Scope
- `scripts/run_crew.py` — `CrewLaunchSpec` (field + `__post_init__`),
  `build_parser`, `build_entry`, `main()`'s `CrewLaunchSpec` construction only.
  `resume_crew()` must show **zero** diff.
- `tests/test_crew_launcher.py` — the two rewritten `MandatoryModelTests`
  cases, plus the five new tests above.

## Specific Exclusions
- `resume_crew()` — must not change at all (state this explicitly in your
  result if the diff confirms it, per the handoff-completeness rule that an
  invalidated-test claim needs to be named, not left implicit).
- `map/INDEX.md`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
  any `*SPINE*.template.json`, `specs/` — fenced to lane K this wave.

## Constraints
- `resolve_model`'s signature from g2 is fixed: `resolve_model(role, harness, requested, reason)`
  positionally; call it with the exact keyword names shown above.
- `CrewLaunchSpec.launcher` (already a field, default `DEFAULT_LAUNCHER = "claude"`)
  is the harness value passed to `resolve_model` — do not add a new
  `--harness` flag or any harness-detection logic.

## Map Anchors (inbound)
No architecture map exists in this repo (DEGRADED-UNPARSEABLE, waived by the
Admiral, evidence `e-plan-1`, `decision:map-index-is-admiral-owned`).
- **Map entry point:** `scripts/run_crew.py` — `CrewLaunchSpec`, `build_entry`,
  `build_parser`, `main()`, `resume_crew`, `launch_crew`,
  `record_external_attempt`. `resolve_model`/`ROLE_MODEL_TIERS` from g2 (same
  file, beside `build_crew_argv`).
- **Decision anchors:** same set as g2 (`decision:ship-todays-tiers`,
  `decision:fail-closed-cheaper`, `decision:refuse-by-name`,
  `decision:reason-on-deviation`, `decision:harness-dimension-is-required`),
  plus:
  - `decision:refuse-a-tierless-dispatch` (#611) — superseded in scope, not
    reverted: an absent `--model` no longer hard-refuses when the
    role/harness pair has a table entry; it still refuses when no table entry
    exists. `@grade: settled/human · leans g3-implement`
- **Evidence expectations:** `claim:role-default-resolves` — a crew
  dispatched with no `--model` runs at its role's table default, checked here
  by a `run_crew.py` unit test and, at g4, one real dispatch inspected via the
  registry entry.

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; `git check-ignore` exits 1 — verified
  before dispatch.
- **Committed** — `tests/test_crew_launcher.py`; `git check-ignore` exits 1 —
  verified before dispatch.

## Required Evidence
- Full output of `py -m pytest tests/test_crew_launcher.py -q`, green.
- A `grep -n "CrewLaunchSpec(" scripts/run_crew.py` listing **every**
  construction site, with a one-line note per site confirming it goes through
  `__post_init__` (all of them do, by Python's own construction semantics —
  state this plainly rather than leaving it implicit).
- Confirmation (diff or explicit statement) that `resume_crew()` has zero
  changes.
- The registry round-trip evidence for an old-shape entry (item above).

## Wiring Grep
```bash
grep -rn "resolve_model" --include=*.py scripts/run_crew.py | grep -v "def resolve_model"
```
Expected: exactly one call site, inside `CrewLaunchSpec.__post_init__`. State
the count.

## Verification Commands
```bash
py -m pytest tests/test_crew_launcher.py -q
```

## Suggested Model Tier
sonnet — moderate risk (touches a shared choke point + rewrites two existing
tests), well-specified.

## Authority
Where resolution happens (`CrewLaunchSpec.__post_init__`, not a
pre-resolution step in `main()`) and that `resume_crew()` is exempt are both
fixed by this handoff, per the plan critic's finding that a `main()`-only
resolution step would silently bypass `launch_crew()`/`record_external_attempt()`.
Do not move resolution to `main()` even if it looks simpler.

## Stop Conditions
Stop and return if: `CrewLaunchSpec` cannot be confirmed frozen/non-frozen
without ambiguity, `resume_crew()` cannot avoid touching `resolve_model`
without duplicating logic, or an existing test beyond the two named
`MandatoryModelTests` cases needs rewriting (name it and stop rather than
silently rewriting more than specified).

## Return Format
Return IMPLEMENTER_RESULT per the standard shape, including Workflow Feedback.
Write it to `.agent-work/567-j/crew-handoffs/g3-implement-result.md` before
ending your turn.
