# tests.test_write_a_skill
tests/test_write_a_skill.py, 210 lines, 16 holes

Tests for constellation-write-a-skill's mint RAIL (scripts/verify_skill_registered.py)

and the shared skill-goodness criteria seam.

The rail is the single mechanically-enforced check the minted skill must clear
(DESIGN_SPEC Section C): it composes the existing curate_corpus.py mechanical
checks + install --dry-run installability, and adds the one property neither can
see on its own — install-BUNDLE REGISTRATION. An unregistered skill installs as
a dead seam (no doctrine, no rail script) while looking fine on disk; that is the
named failure mode this rail guards.

  * RailPassTests    -- a well-formed, REGISTERED toy skill clears curate +
                        installability + registration, and installs via dry-run.
  * RailRefuseTests  -- a toy skill MISSING bundle registration -> rail REFUSES.
  * SharedSeamTests  -- the prose criteria reference EXISTS and BOTH write-a-skill
                        and curator reference it.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.

imports stdlib: importlib.util, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
TOY_SKILL_MD = '---\nname: constellation-toy-widget\ndescription: Turn a toy capability into a repeata...
```

- [load](load.md) function: HOLE: no docstring
- [_write_toy](_write_toy.md) function: HOLE: no docstring
- [RailPassTests](RailPassTests.md) class: HOLE: no docstring
  - [RailPassTests.setUp](RailPassTests.setUp.md) method: HOLE: no docstring
  - [RailPassTests.test_registered_wellformed_toy_passes](RailPassTests.test_registered_wellformed_toy_passes.md) method: HOLE: no docstring
  - [RailPassTests.test_registered_toy_installs_via_dry_run](RailPassTests.test_registered_toy_installs_via_dry_run.md) method: HOLE: no docstring
- [RailRefuseTests](RailRefuseTests.md) class: HOLE: no docstring
  - [RailRefuseTests.setUp](RailRefuseTests.setUp.md) method: HOLE: no docstring
  - [RailRefuseTests.test_missing_bundle_registration_refused](RailRefuseTests.test_missing_bundle_registration_refused.md) method: HOLE: no docstring
  - [RailRefuseTests.test_mechanically_broken_skill_refused](RailRefuseTests.test_mechanically_broken_skill_refused.md) method: HOLE: no docstring
- [RealSkillRegistrationTests](RealSkillRegistrationTests.md) class: write-a-skill must itself satisfy its own rail — registered in the bundles
  - [RealSkillRegistrationTests.setUp](RealSkillRegistrationTests.setUp.md) method: HOLE: no docstring
  - [RealSkillRegistrationTests.test_write_a_skill_is_registered_in_bundles](RealSkillRegistrationTests.test_write_a_skill_is_registered_in_bundles.md) method: HOLE: no docstring
  - [RealSkillRegistrationTests.test_write_a_skill_clears_its_own_rail](RealSkillRegistrationTests.test_write_a_skill_clears_its_own_rail.md) method: HOLE: no docstring
  - [RealSkillRegistrationTests.test_rail_resolves_a_subdir_sourced_script_instead_of_falsely_refusing](RealSkillRegistrationTests.test_rail_resolves_a_subdir_sourced_script_instead_of_falsely_refusing.md) method: Regression (#262): the rail checked bundle members with a hand-rolled
  - [RealSkillRegistrationTests.test_rail_still_refuses_a_script_that_really_is_missing](RealSkillRegistrationTests.test_rail_still_refuses_a_script_that_really_is_missing.md) method: The resolver fix must not soften the check it was guarding: a bundle
- [SharedSeamTests](SharedSeamTests.md) class: HOLE: no docstring
  - [SharedSeamTests.test_criteria_reference_exists_and_both_consumers_reference_it](SharedSeamTests.test_criteria_reference_exists_and_both_consumers_reference_it.md) method: HOLE: no docstring
  - [SharedSeamTests.test_installed_curator_carries_the_criteria_reference](SharedSeamTests.test_installed_curator_carries_the_criteria_reference.md) method: HOLE: no docstring
