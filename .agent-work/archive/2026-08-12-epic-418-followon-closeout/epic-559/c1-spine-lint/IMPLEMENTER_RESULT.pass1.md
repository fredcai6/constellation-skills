# Implementation Result

## Assigned gate
`epic-559/c1-spine-lint` (four gates: `g1-shape`, `g2-falsifiable`, `g3-corpus`, `g4-verify`)

## Completed slice
Built `scripts/validate_spine.py`: an importable checker (`validate(spine) -> list[Fault]`) plus a
thin CLI, that refuses a spine or spine template for two families of fault — shape faults that stop
the engine dead (wrong top-level key, `items`/`tasks` mismatch, an unimplemented check `kind`, a
`gated` task missing postconditions, a `survey` task missing `result`) and the four #518/#562
falsifiability faults (all-null postconditions, a pytest `-k` selector that collects zero tests, an
`artifact` check with no `match` whose statement asserts a property, an unresolved `<placeholder>` in
a command). Ran the checker over every gated-or-survey template the repo ships (discovered by each
file's own `type` field) and recorded the findings below without touching the templates.

## Scope
**Files changed:**
- `scripts/validate_spine.py` (new)
- `tests/test_validate_spine.py` (new)
- `tests/fixtures/spine_lint/fixture_tests.py` (new — tiny pytest-collectable fixture for the
  zero-collect fault's live subprocess tests; named so default `pytest tests` discovery never picks
  it up on its own)
- `map/INDEX.md` (rebuilt)

**Specific exclusions touched:** no — `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
`scripts/run_crew.py`, `skills/implementer/*`, `skills/reviewer/SKILL.md`, `settings.json`,
`docs/agents/*` all untouched. Every shipped spine template is untouched (g3 measures, does not fix).

## Behavior changed
Yes — new capability. Nothing previously read a spine's own checks; `checklist_engine.py` is
unchanged and still trusts the file it is handed. `validate_spine.py` is a new, separate lint an
agent or a future spine generator can run before a spine is ever driven.

## Map Impact
- **Structural anchors touched:** none pre-existing — this adds a new leaf module
  (`scripts.validate_spine`) alongside the other `verify_*.py`/`checklist_engine.py` scripts; no
  existing structural anchor changed shape.
- **Capabilities added:** a spine/template shape-and-falsifiability linter, importable
  (`validate`, `discover_checklist_templates`, `validate_file`) for a later wave's spine generator to
  refuse emitting past, per the handoff's "where this is going" note.
- **Constraints/assumptions touched:** relies on `init_work_area._RESOLVER_OWNED_TOKEN_RE` as the
  single source of truth for which `<placeholder>` families the resolver owns (imported, not
  re-declared) — a change to that regex changes fault-4's ACCEPTED set too.
- **Trust limitations / drift found:** `init_work_area._RESOLVER_OWNED_TOKEN_RE` is itself
  incomplete relative to what `resolve_spine` actually substitutes — it never names the bare
  `<skill-dir>` token, which `resolve_spine` resolves via a separate hardcoded call
  (`_resolve_skill_dir_token(text, "skill-dir", ...)`, outside the role-prefixed regex family). Caught
  live during the g3 sweep (EXPLORER_SPINE.template.json and INTERROGATION.template.json both ship
  bare `<skill-dir>`) and worked around locally in `validate_spine.py` (`_BARE_RESOLVER_TOKENS`)
  rather than editing `init_work_area.py`, which was out of this gate's scope. A later wave should
  either fold `<skill-dir>` into `_RESOLVER_OWNED_TOKEN_RE` directly or accept this workaround as
  permanent — flagged as a triage candidate below.
- **Triage candidates:** (1) `init_work_area._RESOLVER_OWNED_TOKEN_RE` gap above; (2) the g3
  findings themselves (21 all-null gates across 8 templates, 2 unresolved `<exact test command>`
  scaffold placeholders) are unfixed findings for a later wave, detailed below.

## Test mode
**Required:** test-first (TDD implied by the handoff's fixture-set requirement and the frozen gate
postconditions, each a real `pytest -k` command).
**Satisfied:** yes — each gate's own postcondition command (a `pytest --collect-only` floor plus a
real run) was red before the corresponding code existed (no `scripts/validate_spine.py`,
`tests/test_validate_spine.py` collected 0 for every `-k` selector) and green after.

## Evidence

```bash
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2638 passed, 1 skipped, 1121 subtests passed in 105.58s
```

**Result:** pass.

```bash
$ python -m scripts.validate_spine --sweep
sweep: 12 gated-or-survey templates discovered under .../skills
```
(full per-template output below, under "g3 findings")

## TDD evidence, if required
- Failing test observed: before `scripts/validate_spine.py` existed,
  `pytest -q tests/test_validate_spine.py -k Shape --collect-only | grep -c '::'` was 0 (module did
  not exist to import), so g1's own postcondition command failed at the `-ge 6` floor. Same shape for
  g2 (`-k "Falsifiab or Boundary"`, floor 10) and g3 (`-k Corpus`, floor 2) before each fault family's
  code and tests were written.
- Passing test observed: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m
  pytest -q tests/test_validate_spine.py` → `61 passed` (all four gates' test classes together).
- Refactor while green: yes — the `<skill-dir>` false-positive fix (Map Impact, above) was applied
  and re-verified green during g3, after the corpus sweep surfaced it live.

## Docs/contracts touched
- none — `map/INDEX.md` is regenerated output, not an authored contract.

## Assumptions
- "Every gated-or-survey checklist template" (g3's population) means files under
  `skills/*/templates/*.json` whose own `type` field is `gated` or `survey` — not the data-record
  templates in the same directories (`ENGINE_CONFIG`, `FINDING`, `INTERROGATION_RECORD`,
  `REPLAN_INPUT`/`REPLAN_RESULT`, `FOWLER_PASS`, `INITIAL_ISSUE_SET`, `SHAPED_BRIEF`), and not the
  `docs/examples/*`, `examples/*`, or `tests/fixtures/*` JSON files that also happen to carry a
  `gated`/`survey` `type` — those are demo/fixture data, not shipped templates a role copies to start
  a real run. Measured population: 12, matching the handoff's cited cold-reviewer count.
- Fault 3's property-assertion heuristic is a deliberately narrow regex (an enum-like `is <Value>`,
  an explicit `==`/`equals`/`matches`, or a negated `no <word...>` claim) tuned against the real
  corpus to zero false positives — a statement that asserts a property in some other phrasing (e.g.
  "must be true", "should equal") would currently be missed. Documented as a stated residual in the
  module's own docstrings rather than silently assumed complete.
- Fault 4's `<placeholder>` token regex requires the bracket content to start with a letter, so it
  will not mis-flag shell input redirection (`< file`, no closing `>`) or a numeric comparison; it
  will also not catch a placeholder-shaped token that happens to start with a digit or symbol (none
  exist in the corpus today).

## Stop conditions hit
- none.

## Out-of-scope observations
- `init_work_area._RESOLVER_OWNED_TOKEN_RE` gap (bare `<skill-dir>` never named) — see Map Impact,
  Triage candidates.
- g3's measured findings are themselves out-of-scope-to-fix by this gate's own instruction (measure,
  do not fix): 21 gates across 8 of 12 templates carry all-null postconditions (mostly a
  bootstrapping "load context, attest c1" gate — `CARTOGRAPHER`, `CHARTER`, `COMMANDER_SPINE`,
  `EXECUTE_PLAN`, `EXPLORER_SPINE`, `IMPLEMENTER_PLAN`, `SCOUT`, `DEFAULT`), and 2 templates
  (`EXECUTE_PLAN.template.json` gate `g1-integrate.c1`, `IMPLEMENTER_PLAN.template.json` gate
  `m1.c2`) carry the literal, unresolved `<exact test command>` authoring-scaffold placeholder in a
  `command` check — expected for a fill-in-the-blank template, but exactly the shape fault-4 exists to
  catch once a spine is actually driven, so a later wave (the spine generator this checker is meant to
  gate) needs a plan for templates specifically, not just instantiated spines.
- `checklist-engine.md`'s "Template set" table names 6 templates against the measured population of
  12 — confirmed live, not fixed (out of scope: `skills/workbench/references/*` is not named in this
  gate's in-scope file list). Flagged as a triage candidate for whoever owns that doc next.

## Workflow Feedback

- **Handoff gaps:** none — the handoff's four fault descriptions, the `g1-review.c1`/`g1-integrate.c2`
  worked example, and the `_cli_only_verb_violations` pattern pointer were all directly actionable.
- **Context rediscovered:** the g2-falsifiable gate's own frozen postcondition command carried an
  unquoted two-word `pytest -k` expression (`-k Falsifiab or Boundary`) that a POSIX shell
  word-splits into three argv tokens, so pytest received `or`/`Boundary` as bogus positional paths
  and errored (exit 4, zero collected) — unrelated to anything my test file could be named. This
  wasn't documented anywhere; I found it by actually running the exact frozen command text before
  writing tests against it, which is the same "re-run the check, don't just read it" discipline the
  handoff itself argues for. Fixed via `spine_amend`'s sanctioned `retext-check` op (quoting the `-k`
  expression only, intent unchanged), with the amendment's `reason` recording the root cause.
- **Instructions improvised around:** `init_work_area._RESOLVER_OWNED_TOKEN_RE` was the natural
  single source of truth for fault 4's ACCEPTED set (imported, not re-declared), but it undercounts
  what `resolve_spine` actually substitutes (the bare `<skill-dir>` case). Rather than edit that file
  (out of this gate's scope) I added a small, explicitly-commented local exception
  (`_BARE_RESOLVER_TOKENS`) in `validate_spine.py` and recorded the gap for a later wave instead of
  silently living with a false positive.
- **What would have made this easier:** naming `init_work_area.py` explicitly in the handoff's
  in/out-of-scope lists — it wasn't listed either way, and I had to reason from "not a hard no-go, not
  something I own" to "read-only import is fine, editing it is not."

## Return status
`complete`
