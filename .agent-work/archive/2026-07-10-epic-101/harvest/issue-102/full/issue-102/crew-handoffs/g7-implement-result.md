# IMPLEMENTER_RESULT — g7-implement (issue #102, Move 11 regression net)

## Outcome
DONE. Two tests-only additions to `tests/test_install_constellation.py`. No production/skill edits, no new `global-*.md` filename. Full suite green.

## New test names
- `InstallConstellationTests.test_relocated_doctrine_pins_ship_to_installed_destination` — content-pins (moves 1,2,4,5,6,7,8,9 + move-10 canonical) on their CORRECT installed destinations.
- `InstallConstellationTests.test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md` — no-residual, `skills/**/SKILL.md`-only, with the move-9 admiral-scoped exception.

## Content-pin body (part 1)
One install of `explorer commander lessons-auditor`, then per-bucket asserts:
- EVERYONE → `constellation-explorer/references/global-everyone.md`: `reporting misfit is compliance` (m1), `checklist-engine.md` (m2), `never the idea class` (m4), `Verify claimed side-effects against the world` (m5), `A delegate is not a replacement` (m8).
- ORCHESTRATOR → `constellation-commander/references/global-orchestrator.md`: `Unchanged-tree shortcut` (m6), `Idle subagent adjudication` (m7), `Design-it-twice` (m10 canonical).
- SINGLE-HOME → `constellation-lessons-auditor/SKILL.md`: `forks its identity` (m9).

Destination correctness verified against installer bundle map: `commander`/`admiral` → `_GLOBAL_ORCHESTRATOR` (global-everyone + global-orchestrator + design-it-twice-brief + windows); `lessons-auditor` → `_GLOBAL_EVERYONE`; `explorer` → `_GLOBAL_ORCHESTRATOR` (so it carries global-everyone). Move-9's `forks its identity` lives in lessons-auditor's own SKILL.md, not a bundled reference — asserted on the installed SKILL.md.

## Residual body (part 2)
Reads SOURCE tree `ROOT / "skills"`, globs `**/SKILL.md` (14 files; excludes ALL `references/`). Retired signatures asserted absent from every SKILL.md body: `reporting misfit is compliance`, `FOLLOW THIS SKILL STRICTLY`, `not on what the result claims`, `never on what the report asserted`, `delegate is not a replacement`, `Unchanged-tree shortcut`, `idle_notification`. Move-9 EXCEPTION: `breaks recurrence counting` asserted absent from `skills/admiral/SKILL.md` only (lessons-auditor legitimately keeps its rule and is NOT asserted).

## Full suite tail
```
444 passed, 2 skipped, 132 subtests passed in 11.65s
```
New-tests-only run: `2 passed, 36 deselected, 106 subtests passed in 0.42s`.

## Scoping sanity-check note
Confirmed via source grep BEFORE writing: all 7 retired signatures return 0 hits across `skills/**/SKILL.md` (absent from carrier bodies), while the moved doctrine is present in the bundled buckets — `_shared/global-everyone.md` carries all 5 everyone signatures, `_shared/global-orchestrator.md` carries the 3 orchestrator/canonical signatures (incl. `idle_notification` at the mechanism line), `lessons-auditor/SKILL.md` keeps `forks its identity`. So the SKILL.md-only exclusion does not false-fail on the retained/bundled references, and the content-pins hit real installed content. Move-9's `breaks recurrence counting` is absent from admiral (correct residual = absence).

## Assumptions
- `explorer` is a valid stand-in for "any installed skill's global-everyone.md" (it bundles `_GLOBAL_ORCHESTRATOR`, which includes global-everyone.md) — matches the model test.
- `**/SKILL.md` over `skills/` == the contract's `skills/**/SKILL.md` (SKILL.md exists only at `skills/<name>/SKILL.md`; `_shared` has none).

## Stop conditions
None triggered. Every content-pin signature was found in its expected installed destination; residual scoping expressed cleanly without false-failing on retained references.

## Out-of-scope observations
- The move-9 residual signature `breaks recurrence counting` (given contractually) does NOT literally appear anywhere in the tree — lessons-auditor's home text phrases it as "recurrence counting undercounts". The assertion is therefore an absence-only guard on admiral: it will red only if a future edit restores that exact phrase into admiral. It is a weaker sentinel than an exact echo of the home phrasing would be; kept as specified since scoping is contractual. Consider, in a future net, keying the admiral residual to a phrase the home actually uses (e.g. `recurrence counting undercounts`) — but that phrase lives in lessons-auditor, so it would need the same admiral-only scoping. Flagging, not changing.
- `FOLLOW THIS SKILL STRICTLY` is absent from the SOURCE `skills/implementer/SKILL.md`, but the currently-INSTALLED implementer skill at `~/.claude/skills/constellation-implementer/SKILL.md` still carries that banner — the installed copy is stale relative to source. Not in scope here (test reads source), noted for whoever owns re-install.

## Workflow feedback
- Handoff was complete and unusually precise on the crux (per-bucket destinations, SKILL.md-only scoping, move-9 exception). That precision is what made the false-pass/false-fail traps avoidable — good handoff.
- The one friction: the move-9 residual signature `breaks recurrence counting` is a phrase that exists nowhere in the tree (see out-of-scope note), so it can only ever be an absence guard and can't double as a "present in home" cross-check. A handoff that pairs a residual signature with its live home phrasing would let the test both guard the carrier AND positively pin the home in one shot.
- Engine ceremony: for a 2-test mechanical addition the full gated-checklist-through-the-engine flow is disproportionate; I front-loaded source-grep verification of all signatures/destinations (the actual risk surface) instead. Reporting the misfit per the skill's "reporting misfit is compliance" clause.
