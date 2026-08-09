"""Attack the new pinning test with overclaim wordings the author did NOT choose.

The wording half of test_the_legend_states_the_rule_the_predicate_actually_applies
is `assertNotIn("top-level", legend)` -- a negative assertion against ONE literal
string. This script mutates SPLIT_LEGEND in both render.py and checks.py to a
handful of DIFFERENT overclaiming wordings that describe the same false
"top-level-only" rule without containing the literal substring "top-level", then
runs the pinning test and records whether it goes red (catches the overclaim) or
stays green (mutant survives -- the pin is narrower than it looks).

Each file is restored byte-identical after every trial and the restore is
verified by direct read-back, not assumed.
"""
import subprocess
import sys
from pathlib import Path

RENDER = Path("scripts/code_map/render.py")
CHECKS = Path("scripts/code_map/checks.py")

ORIGINAL_RENDER = RENDER.read_text(encoding="utf-8")
ORIGINAL_CHECKS = CHECKS.read_text(encoding="utf-8")

CURRENT_LEGEND_BODY = (
    "split: production vs test caller module, by pytest's "
    "default discovery convention -- test_*.py / *_test.py "
    "naming, or a tests package anywhere on the module path. "
    "a module matching neither is counted production."
)

# Each mutant restates the SAME false claim the original defect made (a
# top-level-only tests package) using different words that avoid the literal
# substring "top-level".
MUTANTS = {
    "front-of-path": (
        "split: production vs test caller module, by pytest's "
        "default discovery convention -- test_*.py / *_test.py "
        "naming, or a tests package at the front of the module path. "
        "a module matching neither is counted production."
    ),
    "first-segment": (
        "split: production vs test caller module, by pytest's "
        "default discovery convention -- test_*.py / *_test.py "
        "naming, or a tests package as the first segment of the module path. "
        "a module matching neither is counted production."
    ),
    "root-level": (
        "split: production vs test caller module, by pytest's "
        "default discovery convention -- test_*.py / *_test.py "
        "naming, or a root-level tests package. "
        "a module matching neither is counted production."
    ),
    "outermost": (
        "split: production vs test caller module, by pytest's "
        "default discovery convention -- test_*.py / *_test.py "
        "naming, or an outermost tests package. "
        "a module matching neither is counted production."
    ),
}

TEST_SELECTOR = (
    "tests/test_code_map.py::ProductionTestCallerSplitTests::"
    "test_the_legend_states_the_rule_the_predicate_actually_applies"
)


def replace_legend(text, new_body):
    old_stmt = 'SPLIT_LEGEND = ("' + CURRENT_LEGEND_BODY.split('" "')[0]
    # Locate the exact multi-line literal by its known first-line prefix and
    # replace the whole parenthesized string literal.
    marker_start = text.index('SPLIT_LEGEND = (')
    marker_end = text.index(')', marker_start) + 1
    old_block = text[marker_start:marker_end]
    assert 'top-level' not in old_block or True  # informational only
    new_block = 'SPLIT_LEGEND = (%r)' % new_body
    return text[:marker_start] + new_block + text[marker_end:]


def run_test():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", TEST_SELECTOR, "-q", "--color=no"],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


results = {}
try:
    for name, mutant_body in MUTANTS.items():
        render_mut = replace_legend(ORIGINAL_RENDER, mutant_body)
        checks_mut = replace_legend(ORIGINAL_CHECKS, mutant_body)
        assert render_mut != ORIGINAL_RENDER, "mutation did not apply to render.py"
        assert checks_mut != ORIGINAL_CHECKS, "mutation did not apply to checks.py"
        RENDER.write_text(render_mut, encoding="utf-8", newline="\n")
        CHECKS.write_text(checks_mut, encoding="utf-8", newline="\n")
        rc, out = run_test()
        results[name] = (rc, out.strip().splitlines()[-1] if out.strip() else "")
        # restore before next trial
        RENDER.write_text(ORIGINAL_RENDER, encoding="utf-8", newline="\n")
        CHECKS.write_text(ORIGINAL_CHECKS, encoding="utf-8", newline="\n")
finally:
    # final restore + verify byte-identical
    RENDER.write_text(ORIGINAL_RENDER, encoding="utf-8", newline="\n")
    CHECKS.write_text(ORIGINAL_CHECKS, encoding="utf-8", newline="\n")
    assert RENDER.read_text(encoding="utf-8") == ORIGINAL_RENDER, "render.py NOT restored"
    assert CHECKS.read_text(encoding="utf-8") == ORIGINAL_CHECKS, "checks.py NOT restored"

print("RESTORED: render.py and checks.py verified byte-identical to original")
print()
for name, (rc, last_line) in results.items():
    verdict = "RED (caught)" if rc != 0 else "GREEN (mutant SURVIVED)"
    print(f"{name:16s} exit={rc}  {verdict}  -- {last_line}")
