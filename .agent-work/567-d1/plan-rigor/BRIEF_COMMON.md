# Context (read-only; do not edit any file)

Repo: /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard

Issue #559: "the door is the interface, not a second path — remove the CLI fallback for agents."
The corpus of agent instruction files under `skills/` carries 13 "CLI fallback:" clauses and 9
live `<engine>` placeholder tokens telling agents to drive the checklist engine from the command
line instead of through the MCP "door" tools (spine_status/spine_start/spine_advance/...).

**This text has been deleted twice and grown back twice.** The deliverable is therefore not the
deletion — it is a GUARD: a test that fails if any of it comes back.

Measured facts you may rely on (all verified in this tree):
- `tests/test_mcp_adoption.py` currently MANDATES the text: `TestTier1ImperativeFields::
  test_field_still_carries_cli_fallback` asserts each of 7 imperative fields still carries its
  exact `<engine> ...` command line, failing with "the CLI door must stay, never be removed or
  discouraged". This is the regrowth mechanism.
- That same file defines `INSTRUCTION_FILES` = rglob over `skills/` for `.md`/`.json` (101 files
  today), *walked never listed*, with a >=60 floor. Measured: it contains all 10 files holding the
  target text, and EXCLUDES both sites that must survive
  (`docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59`, a historical plan
  record, and `scripts/init_work_area.py:24`, a comment documenting the placeholder convention),
  plus `episodes/**` and all test fixtures/approved data.
- A door holding its own lease is REFUSED when it binds a second checklist ("one door drives one
  spine at a time"), so for a Commander's `execute.json`, an Interrogator's `interrogation.json`,
  and an in-session crew's own plan, the CLI is genuinely the ONLY path. 3 of the 13 clauses are
  of this kind.

Hard constraints on any guard design:
- NO exception list. A sibling guard's exception list reached 11 entries across five runs; that
  decay is the named failure mode to avoid.
- Assert against the TEXT'S ABSENCE in a way a reintroduction trips — never against a description
  of the rule.
- Any guard that loops must assert WHAT IT LOOPED OVER and state the count, so it cannot pass
  vacuously on an empty set.
- It must not fire on a legitimate historical mention.
