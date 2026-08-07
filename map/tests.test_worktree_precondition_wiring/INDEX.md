# tests.test_worktree_precondition_wiring
tests/test_worktree_precondition_wiring.py, 186 lines, 10 holes

Deliberate-breakage tests for the worktree-isolation precondition (#329/#422).

Two things are asserted, each with BOTH a broken-state and a fixed-state
assertion in the same test (a check that only ever demonstrates the pass
side is not proven to fail on a genuine omission -- the #392 shape this
issue exists to prevent):

  1. `scripts/verify_worktree_precondition_coverage.py` (the enumeration
     script) actually refuses when a worktree-entering template is missing
     the wired precondition, and actually passes when it is present.
  2. The precondition, once wired onto `COMMANDER_SPINE.template.json`'s
     `init` gate, actually blocks `checklist_engine.start()` when the
     `--here` argument does not match the real worktree, and actually lets
     `start()` proceed once it does.

Both deliberate-breakage constructions run in temp fixtures only
(`tempfile.TemporaryDirectory`, cleaned up in `tearDown`) -- never against
this worktree's own `.git` or the shared checkout.

imports stdlib: __future__.annotations, importlib.util, json, os, pathlib.Path, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
COVERAGE_SCRIPT = ROOT / 'scripts' / 'verify_worktree_precondition_coverage.py'
ISOLATION_SCRIPT = ROOT / 'scripts' / 'verify_worktree_isolation.py'
ENGINE_SCRIPT = ROOT / 'scripts' / 'checklist_engine.py'
REAL_TEMPLATE = ROOT / 'skills' / 'commander' / 'templates' / 'COMMANDER_SPINE.template.json'
TEMPLATE_REL_PATH = 'skills/commander/templates/COMMANDER_SPINE.template.json'
```

- [_load_engine](_load_engine.md) function: HOLE: no docstring
- [_run_coverage_script](_run_coverage_script.md) function: HOLE: no docstring
- [EnumerationDeliberateBreakage](EnumerationDeliberateBreakage.md) class: The coverage script must refuse a template missing the precondition,
  - [EnumerationDeliberateBreakage.setUp](EnumerationDeliberateBreakage.setUp.md) method: HOLE: no docstring
  - [EnumerationDeliberateBreakage.tearDown](EnumerationDeliberateBreakage.tearDown.md) method: HOLE: no docstring
  - [EnumerationDeliberateBreakage._write_broken_copy](EnumerationDeliberateBreakage._write_broken_copy.md) method: Copy the real COMMANDER_SPINE.template.json into the tmp fixture
  - [EnumerationDeliberateBreakage.test_refuses_broken_copy_and_passes_real_fixed_tree](EnumerationDeliberateBreakage.test_refuses_broken_copy_and_passes_real_fixed_tree.md) method: HOLE: no docstring
- [EngineDeliberateBreakage](EngineDeliberateBreakage.md) class: The wired precondition must actually block `start()` -- not just the
  - [EngineDeliberateBreakage.setUp](EngineDeliberateBreakage.setUp.md) method: HOLE: no docstring
  - [EngineDeliberateBreakage.tearDown](EngineDeliberateBreakage.tearDown.md) method: HOLE: no docstring
  - [EngineDeliberateBreakage._git](EngineDeliberateBreakage._git.md) method: HOLE: no docstring
  - [EngineDeliberateBreakage._gated_checklist](EngineDeliberateBreakage._gated_checklist.md) method: HOLE: no docstring
  - [EngineDeliberateBreakage.test_start_refused_on_mismatch_then_succeeds_once_fixed](EngineDeliberateBreakage.test_start_refused_on_mismatch_then_succeeds_once_fixed.md) method: HOLE: no docstring
