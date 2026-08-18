# Return — lane N: the tier table refuses the role this corpus actually dispatches

Branch `feat/567-n-role-key` off `fbd5cdaa`. Suite: 3432 passed, 5 skipped, 1222
subtests passed in 141.92s (0 failures) — `MapTreeFreshnessTests` included and green.

## 1. The declaration

`scripts/run_crew.py`, `ROLE_MODEL_TIERS["claude"]`:

```diff
         "commander": {"default": "sonnet", "allowed": frozenset({"sonnet", "opus"})},
+        "commander-delegated": {"default": "sonnet", "allowed": frozenset({"sonnet", "opus"})},
```

Identical shape to the `commander` row, per the human's ruling quoted in the launch
order: *"commander should be sonnet or opus allowed, haiku can't handle it."*
`commander-delegated` is the same role at the same tier, dispatched under a frozen
launch order instead of a live human — no reason to diverge.

Also extended `tests/test_crew_launcher.py`'s `ResolveModelTests.CLAUDE_ROLES` tuple
with `"commander-delegated"` so the existing parametrized-style coverage
(`test_every_populated_claude_role_resolves_to_its_own_default`) exercises it the
same way as the other five populated roles.

TDD: extending `CLAUDE_ROLES` first reproduced the exact refusal from the launch
order (`CrewLaunchError: no model tier declared for role 'commander-delegated'...`),
then the declaration turned it green (14/14 in `ResolveModelTests`).

## 2. The guard — `tests/test_role_tier_coverage.py`

**Design.** Rather than enumerate "every role term doctrine names" (which includes
plenty of skills — `scout`, `interrogator`, `curator`, `charter`, `explorer`, etc. —
that are real doctrine but dispatched by other mechanisms and correctly undeclared
today), the guard scans for a narrower, textually-grounded property: **a role
doctrine hands a model-tier-bearing dispatch artifact to.** That is exactly the
population `resolve_model` exists to serve, and it is exactly what the
`commander-delegated` defect was — `LAUNCH_ORDER.template.md` names a `Model tier
(required)` field for a role whose own table entry didn't exist.

Three signals, unioned, none of them a hand-typed role list:

1. **`skills/*/templates/*_HANDOFF.template.md`** whose body contains a
   `Suggested Model Tier` field (matched loosely as "model tier", case-insensitive)
   → role = the file's own name stem (`IMPLEMENTER_HANDOFF.template.md` →
   `implementer`). Finds `implementer`, `reviewer`. `CRITIC_HANDOFF.template.md` and
   `PROTOTYPE_HANDOFF.template.md` exist but carry no such field, so neither is
   found (see finding on `prototyper` below).
2. **`skills/*/SKILL.md`** whose text names a ratified `LAUNCH_ORDER` as its
   "frozen principal" (the load-bearing phrase from `commander-delegated`'s own
   doctrine) → role = that file's own `name: constellation-<slug>` frontmatter.
   Finds `commander-delegated`. A test (`test_frozen_principal_pattern_leaves_
   the_producer_side_alone`) pins that `admiral/SKILL.md` — which *produces*
   launch orders rather than taking one as principal — does not false-positive.
3. **`specs/*.spine.toml`** — one compiled-spine spec per role, named
   `<role>.spine.toml`. Finds `implementer`, `reviewer` again (redundant with
   signal 1 today, kept because it is genuinely a second, independent source and
   it is what makes the walk actually reach `specs/` as instructed).

Measured on this tree: 4 HANDOFF templates, 20 `SKILL.md` files, 2
`specs/*.spine.toml` files walked → scanned roles
`{'commander-delegated', 'implementer', 'reviewer'}`.

The assertion is `scanned ⊆ declared["claude"]`, never equality — `admiral`,
`cartographer` and `critic` are declared today and none of the three signals
reaches them (Cartographer is a bare "subagent" table row with no per-role
artifact; Admiral is human-invoked; Critic's own `CRITIC_HANDOFF.template.md`
has no model-tier field), and declaring ahead of a doctrine signal is harmless.
Only the reverse — doctrine hands a tier-bearing artifact to an undeclared role —
is a defect, and subset is the exact shape of that asymmetry.

**Surviving "not trivially green."** `TestTheWalkIsNotVacuous` floors every walk
at its measured count (≥4 HANDOFF files, ≥15 SKILL.md files, ≥1 spec file, ≥2
scanned roles) and separately pins that signal 1 still finds
`{implementer, reviewer}` and signal 2 still finds `commander-delegated`
specifically — so a narrowed glob or a retyped field name reads red, not clean.
`test_the_assertion_can_actually_fail` proves the subset check is a real
predicate against a local fixture (never the real table).

I additionally reverted the declaration under `git stash` and re-ran the guard
to confirm it reds on exactly the real defect before this lane's fix:

```
AssertionError: ['commander-delegated'] live doctrine hands a model-tier-bearing
dispatch artifact to, but ROLE_MODEL_TIERS['claude'] does not declare...
```

then restored it and confirmed green (13/13 new tests, 251 combined with
`test_crew_launcher.py`).

**Surviving "not red on archive noise."** All three globs are rooted at `skills/`
and `specs/` only — no walk ever reaches `.agent-work/**` or
`docs/superpowers/plans/**`. `TestTheWalkStaysInsideDoctrine` pins this by
asserting every walked path's first component is `skills` or `specs`. This
matters because `.agent-work/**` — including this very lane's own `LAUNCH_ORDER.md`
and now `RETURN.md` — legitimately quotes "Model tier (required)" and "frozen
principal" constantly as a *record* of what was said, not as doctrine a future
agent reads; a widened glob would make the guard permanently and meaninglessly
red on its own artifacts.

## 3. Findings beyond the seven

- **`prototyper` is a real, same-shape gap, not declared.** It is genuinely
  dispatched via its own bounded contract (`PROTOTYPE_HANDOFF.template.md`,
  `commander-core.md`'s "Prototyper escape hatch," `crew-dispatch.md`'s
  mechanics), but `PROTOTYPE_HANDOFF.template.md` carries no "Suggested Model
  Tier" field the way `IMPLEMENTER_HANDOFF.template.md` /
  `REVIEWER_HANDOFF.template.md` do — so signal 1 doesn't find it, and neither do
  signals 2/3. I did not declare a tier for it: no human ruling in the launch
  order or elsewhere grounds one, and guessing is exactly what this lane exists
  to stop doing. Worth a doctrine decision: either give `PROTOTYPE_HANDOFF` a
  Suggested Model Tier field (making the gap self-measuring the same way
  `commander-delegated`'s now is) or rule that prototyper intentionally inherits
  its dispatcher's tier.
- **`scout` is doctrine-named as subagent-dispatched but has no tier-bearing
  artifact of its own.** `checklist-engine.md` groups it with `cartographer` as
  "dispatch a subagent," and `test_unknown_role_under_known_harness_refuses_
  by_name_branch_one` pins its refusal as today's intentional behavior. My scan
  does not surface it (no HANDOFF template, no principal claim, no spec file),
  so I neither declared it nor touched that pin — flagging here only because the
  launch order asked for anything the scan's edges brush against.
- **`codex`/`local` harness rows.** Untouched, as instructed. I don't have a
  strong view beyond what's already recorded: `decision:harness-dimension-is-
  required` treats an empty row as fail-closed-by-design, and every dispatch
  under either harness refuses today regardless of role. That seems like the
  right default for two harnesses with no tier doctrine of their own yet, but
  it's the human's call, not this lane's.

## 4. Hazards observed

- Ran with `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`/`CREW_SCRATCH_DIR` unset
  for every suite run, per the inherited hazard. `ScratchDirResumeTests` did not
  red.
- Did not touch `map/INDEX.md`. `MapTreeFreshnessTests` was green anyway (2/2) —
  better than the "green except" the launch order anticipated, nothing to
  reconcile.
- Drove this lane's own plan (`.agent-work/567-n/IMPLEMENTER_PLAN.json`) through
  the MCP door's CLI fallback (`scripts/checklist_engine.py`, the vendored copy
  in this worktree) — no crew was dispatched, so the MCP door binding never
  applied; nothing to report here.
- No issue filed. Nothing staged under `.agent-work/567-n/triage-candidates/` —
  both findings above are named inline per the launch order's own instruction
  ("name it in your return either way"), and neither is a fix-now candidate.

## Workflow feedback

None — the launch order named task, scope, exclusions, evidence, and stop
conditions in full; nothing was ambiguous or improvised around.
