"""g2-review re-verification: does the renderer mutation leak past its own test?

`renderer_returns_empty` is the LAST entry in the mutations dict, and the restore
loop writes `pristine` back at the START of each iteration. So nothing restores
the installed renderer after the final iteration. This probe settles, deterministically
rather than by guessing pytest's ordering, what state the class-level installed
bundle is left in once the mutation test returns.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates")
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "doctrine_under_review", ROOT / "tests" / "test_iterative_planning_doctrine.py"
)
doctrine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(doctrine)


class LeakageProbe(doctrine.InstalledIterativeRoleRuntimeTests):
    def test_probe_installed_renderer_state_after_the_mutation_test(self):
        renderer = self.skills_root / "constellation-replan" / "scripts" / "verify_replan.py"
        before = renderer.read_text(encoding="utf-8")
        self.assertNotIn('return ""', before, "installed renderer should start pristine")

        # Run the delivered mutation test to completion, in this same class run,
        # against this same class-level installed bundle.
        self.test_admiral_prelaunch_stop_mutation_every_surviving_requirement_still_goes_red()

        after = renderer.read_text(encoding="utf-8")
        leaked = 'return ""' in after
        print(f"\nLEAKED={leaked}  (installed renderer still degraded after the mutation test)")
        print(f"IS_TEMP_INSTALL={str(renderer).startswith(str(Path(self.root)))}")
        print(f"REPO_RENDERER_UNTOUCHED="
              f"{'return \"\"' not in (ROOT / 'skills' / 'replan' / 'scripts' / 'verify_replan.py').read_text(encoding='utf-8')}")

        # Does a leaked renderer actually break a later run in this class?
        if leaked:
            probe = self.run_role("admiral", "admiral-prelaunch")
            print(f"LATER_RUN_RC={probe.returncode} STDERR={probe.stderr.strip()[:120]}")

        self.assertFalse(
            leaked,
            "the renderer mutation is not restored after the final loop iteration, so it "
            "leaks into every test that runs after this one in the same class",
        )
