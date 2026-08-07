# Implementer Result — g4 (explorer SKILL.md + templates)

## Completed slice
Authored the constellation-explorer doctrine (`SKILL.md`) and the four remaining templates, plus the authorized carry-forward CYCLE config fix and its runtime test. All Close Criteria met; full-suite inflection landed exactly as predicted.

## Files changed
- **NEW** `skills/explorer/SKILL.md` — orchestrator-tier doctrine; frontmatter `name: constellation-explorer`. Headline doctrine 1-2-3 in order; spine walk-through table; flavors (shotgun/compare/refine); excursion ramps; ideas-board-as-source-of-truth; spec phase (per-section, delta-based, design-it-twice); critical review (panel scaling, findings table, reopen cascade); route (three outcomes, explorer never cuts). Register/length modeled on `skills/commander/SKILL.md`.
- **NEW** `skills/explorer/templates/EXPLORER_STARTING_QUESTIONS.template.md` — the five first-cycle seeds; notes later cycles seed from the board.
- **NEW** `skills/explorer/templates/IDEAS_BOARD.template.md` — the point / candidates / verdicts (with tested-vs-NOT-tested scope) / open threads / rejected-with-reasons / cycle log.
- **NEW** `skills/explorer/templates/EXCURSION_BRIEF.template.md` — single dispatch template; common fields + three type sections; prototype section reproduces the six frozen PROTOTYPE_HANDOFF top-level headings verbatim.
- **NEW** `skills/explorer/templates/CRITIC_HANDOFF.template.md` — cold-read contract (spec only, nothing sacred, assigned lens / full-adversary); return format = the fixed 6-column table with Disposition/Reason left EMPTY (human-only triage; EDIT / RE-EXPLORE / REJECT).
- **EDIT** `skills/explorer/templates/CYCLE.template.json` — removed `config_ref` (carry-forward tc2).
- **EDIT** `tests/test_explorer_templates.py` — additive `CycleSurveyConfiglessRuntime` class (2 tests, +24 total in suite).

Commit: **9b89e530e4164e75542f13b2a1f560f3fe68d3e3** on `constellation/issue-58`.

## Evidence produced

### Full-suite inflection (root-cause distribution)
Baseline (before SKILL.md): 31 failed —
```
      5 FAILED tests/test_feedback_tooling.py
     26 FAILED tests/test_install_constellation.py
```
After (SKILL.md present): 2 failed, 420 passed, 1 skipped, 20 subtests —
```
      2 FAILED tests/test_install_constellation.py
```
Both remaining are the expected-skills-list class (g5): the installer now discovers `constellation-explorer` and `constellation-prototyper`, but the test's expected list has neither — `AssertionError: Second list contains 2 additional elements` (`constellation-explorer`, `constellation-prototyper`). The 5 `test_feedback_tooling.py` failures CLEARED. No failure outside the expected-skills class — no stop condition.

### Targeted suite
`python -m pytest tests/test_explorer_templates.py -q` → `24 passed in 0.94s` (includes the 2 new config-less runtime checks).

### Six-heading byte-match (EXCURSION_BRIEF vs PROTOTYPE_HANDOFF)
`diff` of the two heading sets → **IDENTICAL**:
```
## Question
## Branch
## Host-project conventions
## Location
## Stop conditions
## Return format
```

### Doctrine key-phrase greps (SKILL.md)
- "never initiates convergence" — line 20
- "standalone message" — line 20
- "NOT tested" — line 22
- "no delegated" — lines 14, 27
- Scoped-nulls passage genuine — line 22 (kills that test under those conditions; states tested vs NOT tested; impossibility needs class-spanning evidence; default next move is another variant).

### Marker discipline (verified against the script, not by eye)
Ran `verify_spec_confirmed._unconfirmed_marker_hit` over all five of my files: SKILL.md and all four templates report **clean (all mentions inline)**. The one standalone-marker hit is in `DESIGN_SPEC.template.md` — the frozen g2 template that intentionally ships as a refused DRAFT; not in my scope and correct as-is. The shelve route in SKILL.md instructs placing the marker as a standalone header line on shelved issues (enforceable), while every in-prose mention is inline.

## Assumptions
- **CYCLE config fix = drop the key, not inline config.** The engine's `load_config` returns `{}` gracefully for a missing `config_ref` file (no crash), and `rework_cap` is consulted only by `reopen`, which raises for non-gated checklists — so a survey never uses config. Dropping `config_ref` is the honest expression of "this survey needs no config" and removes the dangling reference to a `docs/agents/engine-config.json` a fresh install lacks. The spine keeps inline `config` only because its reopen loop needs cap=99. This matches "fail visibly; no silent fallback": there is no file to silently fall back to hunting for.
- Frontmatter `description` written in the sibling style (imperative "Use when…"), consistent with commander/prototyper.

## Stop conditions hit
None.

## Out-of-scope observations
- The g2 `DESIGN_SPEC.template.md` standalone marker is correct by design (refused DRAFT); flagged only so g5's invariant tests expect exactly one enforceable standalone marker there and none in SKILL.md/the other templates.
- `test_install_constellation.py` expected-skills list and explorer script-bundle assertions remain g5's, as scoped.

## Workflow feedback
The handoff's predicted inflection (31 → 2, naming the exact remaining class and the `grep '^FAILED' | sed | sort | uniq -c` recipe) made verification unambiguous — I could confirm "no failure outside the expected class" mechanically rather than by judgment, which is the right shape for a hard-gated epic. One friction point worth recording: the carry-forward item framed `config_ref` as something that "can hard-fail the engine," but the engine actually degrades gracefully to `{}`; the real defect is the dangling reference to a non-existent install-time file, not a crash. Stating the defect as "dangling ref → silent default-hunt" rather than "hard-fail" would have pointed straight at drop-the-key without needing to read `load_config` to disprove the crash framing.
