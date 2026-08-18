# Candidate B — retire the mandate, pin the inversion

**Mechanism (three moves, one commit).**

1. *Retire the mandating assertions.* Delete `TestTier1ImperativeFields::
   test_field_still_carries_cli_fallback`, `TestTier1CommanderCoreAttachLine::
   test_paragraph_still_carries_cli_fallback`, the `cli_substr` column of
   `TIER1_JSON_FIELDS`, `TestTier2SkillBodyDefaultPath` (both halves), and Tier3's
   `test_still_names_cli_invocation` / `test_door_section_itself_keeps_the_cli`. These are
   the regrowth engine: they fail RED unless the text exists, so every deletion run gets
   ordered to put it back.
2. *Invert them corpus-wide.* Generalize the precedent already in-tree at
   `tests/test_mcp_adoption.py:838` (`TestTier2SpineAlreadyBoundForDispatchedCrews`,
   "presence is the fact") from its 2 files to the whole walk: over
   `_all_instruction_texts()`, no `(where, text)` pair may contain `<engine>`,
   `CLI fallback:`, or `checklist_engine.py`. Reports the pair count and the file count it
   scanned, so an empty set cannot pass. No exception list: the 3 door-refused cases
   (`crew-dispatch.md`, `commander-core.md`, interrogator) are *consolidated* into the one
   `## MCP door` section of `skills/workbench/references/checklist-engine.md` and the
   invariant is structural — carrying files == 1, and it is that file.
3. *Pin the inversion.* `tests/data/cli_retirement.approved.txt` records the retired test
   names plus the ruling verbatim; a meta-test reads `tests/test_mcp_adoption.py` source
   and fails if any retired name is redefined or any assertion again *requires* those
   tokens. Flipping back means deleting a checked-in ruling in the diff.

**Failure message** (both directions): "#559. Deleted twice, regrown twice — the third
regrowth came from a test that mandated it. Ruling: 'the agents should not know about the
CLI. period.' If you are here after restoring an `<engine>` line, delete the line; do not
restore the mandate. If the door genuinely refuses, document it under `## MCP door` — the
sole authority — never re-inline a command."

**Three ways this is wrong.**

1. *Consolidation silently breaks the 3 real cases.* Where the door refuses a second bind,
   an agent now gets a pointer, not a command. Green guard, un-driveable run — absence
   never detects "the surviving instruction became unreachable." A reachability assertion
   fixes it and reintroduces exactly the enumeration this forbids.
2. *The meta-guard is out-writable.* It text-matches one hardcoded path. A mandate
   rewritten as `_requires_cli(...)`, hidden behind a fixture, or moved to any of the other
   ~90 test files passes. It pins the mandate's string shape, not its semantics — the same
   list-vs-walk hole this suite already names about itself.
3. *"Exactly one authority file" is an exception list of length 1.* The first genuinely
   door-refused new skill makes it `== 2`, and the 11-entry decay restarts under a nicer
   name. Relatedly, non-firing on the historical plan record and `init_work_area.py:24` is
   a property of the walk root, not of anything B checks.

**Cost versus A.** B edits live doctrine — the 3 legitimate sites an agent actually reads —
so its diff is larger, riskier, and can break real runs in a way a detect-only guard
cannot; it deletes currently-green tests, giving up the two-sided door-vs-CLI proof that
keeps the remaining prose honest; it adds new machinery (a ruling file, a meta-test over
test source) that is itself unowned maintenance surface; and it burns the escape hatch on
purpose — a future run that finds the door genuinely insufficient must defeat the pin
first, which is friction that will sometimes be wrong-friction. A stays additive and
reversible and touches nothing agents read.
