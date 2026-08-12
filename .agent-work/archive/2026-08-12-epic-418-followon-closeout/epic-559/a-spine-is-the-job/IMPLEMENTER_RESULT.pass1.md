# Implementation Result

## Assigned gate
`g1-implement` (implementer) — work id `epic-559/a-spine-is-the-job`

## Completed slice
All four required changes, all in `scripts/run_crew.py` plus the two named skill files:

1. `build_crew_argv` gets a spine-carried prompt branch: when a `spine` is given and no `handoff` is, the prompt names no document at all and tells the crew to call `mcp__spine__spine_status` first, then drive the bound spine gate by gate until it reports done. The old handoff-branch prompt is byte-identical, proven by a literal-string assertion (`SpineOwnershipPromptTests::test_control_handoff_branch_is_byte_identical_to_the_pre_559_prompt`).
2. `--handoff` is now optional. `CrewSpec.handoff` is nullable; `CrewSpec.__post_init__` refuses a dispatch with neither `handoff` nor `spine`. `_require_handoff` runs only when a handoff was actually supplied (cli backend). The registry records `handoff: null` for a spine-only crew. The external backend still unconditionally requires a handoff (it cannot bind a spine, so a spine-only dispatch there would leave the crew with no job) and refuses explicitly, naming why.
3. Both `skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md` had their CLI-fallback paragraph replaced: a dispatched crew is now told its spine is already bound, `spine_status` is its first call, and it must not author a plan/survey of its own. Neither file mentions the engine CLI or `checklist_engine.py` anywhere anymore.
4. A crew can no longer waive its own bound spine's check. `CREW_ALLOWED_TOOLS` still grants `mcp__spine__spine_evidence` (so `attest`/`attach` work), but `build_crew_argv` now also emits `--settings` with an inline `PreToolUse` hook that denies only `action=waive` on that tool, with a `permissionDecisionReason` naming the "ask up" path (`spine_halt` block). Verified directly by piping fake tool-call JSON at the exact hook command the argv carries (`WaiveHookTests`), so the behavior is checked without spawning a real agent CLI.

Also fixed the named coupling: `CREW_ALLOWED_TOOLS`'s `mcp__spine__*` entries grew from 7 to the door's real 9 (adding `spine_capture`, `spine_amend`), and are now tied to `mcp_spine_server.TOOL_NAMES` by a test (`CrewGrantTiesToDoorTests`) that goes red if the two lists diverge — verified by mutating the constant and re-running that test.

## Scope
**Files changed:**
- `scripts/run_crew.py`
- `skills/implementer/SKILL.md`
- `skills/reviewer/SKILL.md`
- `tests/test_crew_launcher.py`
- `tests/test_mcp_adoption.py` (see "Specific exclusions touched" below)
- `map/INDEX.md` (mechanical regeneration, `python -m scripts.code_map build --root .`)

**Specific exclusions touched:** yes, and it needs explaining. `checklist_engine.py` and `mcp_spine_server.py` were **not** modified (per the hard no-go). `tests/test_mcp_adoption.py` **was** modified, which is not named in the handoff's file list but falls under its blanket "and tests." Two pre-existing test classes in that file literally pinned the fact this task was asked to remove — that `skills/implementer/SKILL.md`/`skills/reviewer/SKILL.md` must route a dispatched crew's own plan to the CLI. Removing the CLI paragraph (item 3) turned those tests red by design, not by accident. I removed `implementer`/`reviewer` from `TIER2_SKILL_FILES` (with a comment explaining why) and replaced `TestTier2IdentityTradeCarried` with `TestTier2SpineAlreadyBoundForDispatchedCrews`, which pins the opposite, superseding fact for exactly those two files (spine already bound, `spine_status` named affirmatively, no CLI mention at all) using the same two-sided-pin style the rest of that file already uses. No other tier, file, or rule in `test_mcp_adoption.py` was touched.

## Behavior changed
Yes. A crew dispatched with `--spine` and no `--handoff` gets a document-free, spine-driving prompt instead of a "read this file" instruction; a crew dispatched with only `--handoff` is unaffected byte-for-byte. Every crew's `spine_evidence` grant can no longer `waive`. `CREW_ALLOWED_TOOLS` grants two more door tools than before.

## Map Impact
- **Structural anchors touched:** `scripts/run_crew.py::build_crew_argv` (new `spine` parameter, nullable `handoff`, new branch), `scripts/run_crew.py::CrewSpec` (nullable `handoff`, construction-time refusal), `scripts/run_crew.py::crew_settings_json`/`_WAIVE_HOOK_PY`/`WAIVE_DENY_REASON` (new), `scripts/run_crew.py::CREW_ALLOWED_TOOLS` (7 → 9 mcp entries), `skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md` (CLI-fallback paragraph replaced).
- **Capabilities added/changed/affected:** a crew dispatch can now be spine-only (no handoff document at all); a crew's `spine_evidence` grant is capability-restricted (waive removed) without removing the tool.
- **Constraints/assumptions touched:** the external backend's "cannot bind a spine" constraint is now stated as "therefore always needs a handoff," made explicit rather than incidental.
- **Decision candidates / resolved decisions:** the mechanism for restricting one action inside a multi-action MCP tool (a `PreToolUse` hook via inline `--settings`, since Claude Code's `--allowedTools`/`--disallowedTools` grants/denies a whole tool, not one of its actions) is a pattern worth recording durably if another tool ever needs the same treatment — flagged as a triage candidate below.
- **Triage candidates:** (1) the `PreToolUse`-hook-via-inline-`--settings` pattern for restricting one action of a multi-action MCP tool is worth a durable note somewhere Cartographer/future authors would find it — it is not obvious from `mcp_spine_server.py`'s docstring, which only discusses the tool-grouping decision, not the grant-restriction one. (2) `skills/implementer/SKILL.md`'s "Start here" section (step 1) still tells *any* invocation to "build the plan and claim the lease" as its first command, which is generically true for a human/commander-driven run but is now directly superseded, later in the same file, by "do not author a plan of your own when a spine is already bound" for the dispatched-crew case. A weaker agent reading top-to-bottom hits the generic instruction first. Out of my named scope (the handoff named one paragraph, not the "Start here" section), but worth a follow-up pass. Same shape in `skills/reviewer/SKILL.md`.

## Test mode
**Required:** test-first / evidence-only (handoff: "Tests that fail without your change")
**Satisfied:** yes — 14 new tests independently verified red against the unmodified `scripts/run_crew.py` (via `git stash push -- scripts/run_crew.py`, rerun, `git stash pop`), and the crew-grant tie test independently verified red against a mutated `CREW_ALLOWED_TOOLS` (temporarily commenting out one entry, rerun, restore).

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** pass — `2548 passed, 1 skipped, 1101 subtests passed`

```bash
# control, captured before any change (a1-control):
# prompt: "You are the constellation implementer crew for session ... Read the
#   handoff at /abs/HANDOFF.md and execute it exactly. The run is only complete
#   when the result artifact the handoff names exists."
# names handoff path: True / mentions spine: False / mentions spine_status: False
# CREW_ALLOWED_TOOLS had 7 mcp__spine__* entries (missing spine_capture, spine_amend)
# mcp__spine__spine_evidence granted wholesale -> waive reachable
```
**Result:** pass — control reproduced exactly as described in the handoff.

```bash
git stash push -- scripts/run_crew.py
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_crew_launcher.py
git stash pop
```
**Result:** pass — 14 failed / 98 passed with the production change stashed out (red), 112 passed with it restored (green).

## TDD evidence, if required
- Failing test observed: 14 tests in `tests/test_crew_launcher.py` fail against unmodified `scripts/run_crew.py` (see above); `CrewGrantTiesToDoorTests::test_crew_grant_mcp_entries_equal_the_doors_own_tool_names` fails when `CREW_ALLOWED_TOOLS` is mutated to drop one `mcp__spine__*` entry.
- Passing test observed: full suite green at `2548 passed, 1 skipped` with the real change in place.
- Refactor while green: no refactor pass was needed beyond the implementation itself; the map regeneration (`map/INDEX.md`) was mechanical, not a refactor.

## Docs/contracts touched
- `skills/implementer/SKILL.md`, `skills/reviewer/SKILL.md` — CLI-fallback paragraph replaced (in scope, named in the handoff).
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`) after the entity count drifted from the diff; the repo enforces this via `tests/test_code_map.py::MapTreeFreshnessTests`.

## Assumptions
- Claude Code's `--settings <file-or-json>` flag accepts an inline JSON string (confirmed via `claude --help`) and its hook system supports a `PreToolUse` hook returning `hookSpecificOutput.permissionDecision: "deny"` (confirmed via strings extracted from the installed CLI binary's embedded hook documentation) — this repo has no prior example of this exact mechanism, so I verified both claims directly against the installed `claude` binary rather than assuming.
- The "control" evidence a1-control gate asked for ("Record both verbatim") was interpreted as attaching it as spine evidence rather than requiring a separate committed artifact, since the gate's own evidence trail is durable.

## Stop conditions hit
- None. The one thing the handoff flagged as a possible stop/escape ("if deriving [CREW_ALLOWED_TOOLS] means importing mcp_spine_server at module scope and that turns out to be awkward... do the smallest honest thing instead") **did** turn out to be awkward — confirmed by reading `mcp_spine_server.py`, which does `Path(os.environ["SPINE_ENGINE"])` / `Path(os.environ["SPINE_FILE"])` at module import time, raising `KeyError` without both set. Importing it at `run_crew.py` module scope would make importing `run_crew` itself require a bound spine, breaking the CLI and the test suite. Per the handoff's own escape hatch, I did the smallest honest thing: kept `CREW_ALLOWED_TOOLS` hand-typed (now correct, 9 of 9) and added a test that imports `mcp_spine_server` with a scratch environment and asserts the two lists are equal, going red on drift.

## Out-of-scope observations
- See the two triage candidates under Map Impact above (durable-doc gap for the `PreToolUse`-hook pattern; the "Start here" section ordering tension in both SKILL.md files).
- `tests/test_mcp_adoption.py`'s `CLI_PLACEHOLDER`/`DOOR_TOOL_NAMES` (7 tools) and `CLI_ONLY_VERBS` (5 verbs) constants are stale relative to the already-merged N1 change (door now covers 9/9 tools, 0 CLI-only verbs) — I did not touch this, since it is unrelated to my four required changes and touching it risks unwinding a large, deliberately-built test file outside my scope. Flagging as a triage candidate for whoever owns that file next.

## Workflow Feedback

- **Handoff gaps:** none — the handoff named the exact paragraph, the exact ruling, the exact files, and the exact escape hatch for the one genuinely hard part (the `mcp_spine_server` import). The one thing it did not anticipate: fixing item 3 (SKILL.md) collides with pre-existing tests in `tests/test_mcp_adoption.py` that pin the fact being removed. Not a gap so much as a downstream consequence worth naming for the next handoff of this shape: when a change is explicitly designed to overturn a previously-pinned invariant, say so, so the implementer doesn't have to rediscover which pins are load-bearing versus obsolete by reading a ~1150-line test file's docstrings.
- **Context rediscovered:** whether Claude Code's `--allowedTools`/permission-rule system supports per-argument scoping of an MCP tool (it does not — confirmed by reading strings in the installed CLI binary, since no public doc or repo example covers this) versus whether its hook system does (it does, via `PreToolUse` + `hookSpecificOutput.permissionDecision`). This took real investigation; a pointer to "Claude Code hooks, PreToolUse, permissionDecision" in `docs/agents/` or the workbench reference would have saved it for the next person solving this exact "restrict one action of a multi-action tool" shape.
- **Instructions improvised around:** none in the four required changes. In the "also fix the coupling" section, I used the named escape hatch as designed (test that ties the lists) rather than importing at module scope.
- **What would have made this easier:** a one-line pointer in the handoff (or in `mcp_spine_server.py`'s docstring, which already documents the tool-grouping decision at length) toward the fact that `--settings` accepts inline JSON and that hooks are the mechanism for action-level tool restriction — I would have reached for it directly instead of first checking whether the permission-rule specifier syntax (`ToolName(specifier)`) covered MCP tool arguments.

## Return status
`complete`
