# Launch Order: `commander-tests — #116`

Commanders start cold. Everything you need is pasted below.

## Mission
Three test-hardening fixes that close silent-gap holes in the install/skill-registry checks. Deliverable: one green, reviewed PR.

**Issue #116 (verbatim):**
- `SKILL_INDEX.md` has no automated pin: a missing/wrong entry passes every gate (the docent/explorer/prototyper gap sat unnoticed until a cartographer commit). Add an every-installed-skill-appears-in-the-index test.
- `_shared/` sources vs bundled installed copies have no sync-integrity test beyond the per-doctrine content pins.
- `tests/test_install_constellation.py::SKILL_NAMES` is a hardcoded full-roster list every new skill must hand-update (the cold critic's BLOCKER in #104 traced here) — derive from skill discovery instead.

## Prior-Wave Verdicts (pasted)
Base is current main (see Workspace). No cross-issue dependency; these are self-contained test additions.

## Pre-Rulings (overridable with evidence)
- SKILL_INDEX pin: enumerate the actually-installed/discovered skill set and assert every one appears in `SKILL_INDEX.md` (and optionally: no index entry lacks a skill). Model discovery on however the install/discovery code already enumerates skills — do not hardcode a second roster.
- `_shared`→bundled sync-integrity: assert each `skills/_shared/<f>` source is byte-identical to the copy bundled into every role's `references/<f>` at install (the install step that copies them). This is the test that would catch an edit to a role's install-copy that diverges from source.
- SKILL_NAMES: derive it from skill discovery (the same enumeration the pin test uses), so a new skill needs no hand-edit here. Keep any test that consumed SKILL_NAMES green.
- These are TEST/harness changes — do not change install behavior itself; if a test reveals a real sync bug, report it as a finding (float) rather than silently "fixing" a source to make the test pass.

## Honest-Null Clause
A measured negative is a complete deliverable. If one of the three already has coverage on current main, report exactly what exists with evidence rather than duplicating it.

## Inherited Latitude
Implement the tests, open the PR. FLOAT: any change to install/discovery production behavior; any real sync bug the new test surfaces; any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `tests/test_install_constellation.py` and any new test module you add under `tests/`. Do NOT edit `scripts/install_constellation.py` (production install), `SKILL_INDEX.md`, `skills/_shared/*`, or any skill SKILL.md — if the test needs a fixture, add it under tests/. If a test surfaces a real drift in a source file, FLOAT it, don't fix it here.

## Workspace
Worktree `C:/Programs/cs-wt-tests` — branch `test/hardening-116`, base `c0f18ce` (current main), provisioned via `git worktree add -b test/hardening-116 C:/Programs/cs-wt-tests main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-tests` → exit 0; paste into report.
PR = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** multiline `gh --body` → temp file + `gh pr create -F <file>`; `@'...'@` is PowerShell-only, NOT a Git-Bash commit construct — real heredoc or quoted `-m`. Use `py`. Verify your worktree.
**Active lesson `test-harness-concurrency-failsafe`:** concurrent-file-I/O tests need try/except + stop-signal in `finally` + `daemon=True` (unlikely to apply here — these are static/registry checks).
Read `tests/test_install_constellation.py` and `scripts/install_constellation.py` first to learn how skills are discovered and how `_shared` is bundled. Run the suite before/after; all pre-existing tests stay green.

## Budget
- **Model tier (required):** sonnet. Bounded, well-scoped test additions against an established harness.
- Checkpoint and return if you near a session limit, or float to re-tier if a piece proves larger than a bounded test add.

## Stop Conditions
Stop and return when: a test surfaces a real source-drift/sync bug (float it); a piece is already covered (report the null); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-3/W3-116-REPORT.md` BEFORE going idle: verdict (per fix), evidence (each new test's name + green output; a note that the SKILL_INDEX/SKILL_NAMES tests are discovery-derived not hardcoded; full suite green), PR URL, map impact, triage candidates (incl. any real drift surfaced), workflow feedback (under the epic your durable root now resolves worktree-local — write the trio there; else stage and name the path), isolation output. Open PR with `gh pr create -F <bodyfile>`; title `test(install): SKILL_INDEX pin + _shared sync-integrity + discovery-derived SKILL_NAMES (#116)`. Post verdict, go idle.
