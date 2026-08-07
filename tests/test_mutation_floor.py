"""EXECUTED falsifiability for scripts/map_orient.py.

Falsifiability is demonstrated by execution, never asserted by the party being
graded. Each named mutation is mechanically applied to a COPY of the module,
the whole floor (tests/test_map_orient.py) is re-run against that copy, and the
run must go RED.

LOAD-BEARING -- the reason this file exists at all
--------------------------------------------------
Every mutation asserts it APPLIED **before** it asserts red:

  * the original text occurred exactly once,
  * it occurs zero times afterwards,
  * and the replacement's occurrence count went UP by exactly one
    (a count delta, not `in`, so a replacement string that already appears
    elsewhere in the module cannot fake the assertion).

If a substitution does not land, this file fails LOUDLY as a HARNESS ERROR and
never reports a killed mutant. A mutation that silently fails to match produces
a green baseline that is *indistinguishable from a killed mutant* -- this epic
already lost a round to exactly that with a non-matching `sed`. Without the
applied-assertion the check that verifies falsifiability is itself
unfalsifiable. Prove you changed the thing, THEN compare.

The unmutated baseline is asserted GREEN first, so a red result is attributable
to the mutation rather than to the harness. Each kill must also name a test in
the class the mutation is supposed to break, and the run must still have
collected and passed other tests -- otherwise a mutation that merely broke the
import would count as a kill for the wrong reason.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "map_orient.py"
FLOOR = ROOT / "tests" / "test_map_orient.py"

ORIGINAL = MODULE.read_text(encoding="utf-8")


class HarnessError(AssertionError):
    """The mutation did not land. NOT a killed mutant -- a broken harness."""


@dataclass(frozen=True)
class Mutation:
    name: str
    why: str
    # Every substitution must land; a multi-part mutation is all-or-nothing.
    subs: tuple[tuple[str, str], ...]
    # The floor class that is supposed to notice.
    expect_kills: str


MUTATIONS = (
    Mutation(
        name="degraded-completeness `all` -> `any`",
        why=(
            "Under `any`, a degraded record carrying ONE of substitutes/unmapped/"
            "escalation and omitting the other two would discharge -- exactly the "
            "silent degradation this module exists to refuse."
        ),
        subs=(("    return all(checks)\n", "    return any(checks)\n"),),
        expect_kills="PartialFillMatrix",
    ),
    Mutation(
        name="UNRESOLVABLE-ROOT collapsed into DEGRADED-NO-MAP, exiting 0",
        why=(
            "The #315 failure mode wearing a friendly face: 'I could not look' "
            "reported as 'I looked and the map is not there', with a satisfied "
            "exit code. A naive tmpdir test passes identically before and after, "
            "which is why the discriminator pair differs in exactly one bit."
        ),
        subs=(
            ("        return MODE_UNRESOLVABLE_ROOT\n", "        return MODE_DEGRADED_NO_MAP\n"),
            (
                "    return EXIT_OK if discharged else EXIT_DEGRADED_UNDISCHARGED\n",
                "    return EXIT_OK\n",
            ),
        ),
        expect_kills="CouldNotLookDiscriminator",
    ),
    Mutation(
        name="citable-content requirement weakened to mere existence",
        why=(
            "Makes a scaffolded-but-empty map read RESOLVED -- a false RESOLVED "
            "satisfies the ENTIRE contract on a map with no content, which is "
            "strictly worse than an honest DEGRADED."
        ),
        subs=(("    return candidate.anchor_count >= 1\n", "    return candidate.exists\n"),),
        expect_kills="CitableContent",
    ),
    # ---- added at rework, after each SURVIVED or was shipped as a defect ----
    Mutation(
        name="unmapped filler check `not any` -> `not all`",
        why=(
            "Under `not all`, an `unmapped` list needs only ONE real entry to pass, so "
            "['none', 'something real'] would discharge. This mutation SURVIVED the "
            "first shipped floor (42 passed, 0 failed): every filler case used a "
            "single-element list, where `any` and `all` are identical and the two "
            "cannot be told apart. The kill now comes from the multi-element cases in "
            "PartialFillMatrix.test_one_filler_poisons_a_multi_element_unmapped_list."
        ),
        subs=(
            (
                "    return not any(is_filler(entry) for entry in entries)\n",
                "    return not all(is_filler(entry) for entry in entries)\n",
            ),
        ),
        expect_kills="PartialFillMatrix",
    ),
    Mutation(
        name="an unreadable substitute accepted as a hash pin",
        why=(
            "The B1 blocker as shipped: accepting a non-empty sentinel where a sha256 "
            "belongs let a single mistyped substitute path discharge the entire "
            "degraded record at exit 0 -- the exact hole this contract exists to close."
        ),
        subs=(
            (
                "    return CONTENT_HASH_RE.match(value.strip().lower()) is not None\n",
                "    return bool(value.strip())\n",
            ),
        ),
        expect_kills="UnreadableSubstitute",
    ),
    # ---- g2: mutations against verify-frame --------------------------------
    Mutation(
        name="an ABSENT mission frame credited as a pass",
        why=(
            "THE vacuous pass. A check that reports success when the artifact it "
            "checks does not exist is not a check -- it reports success for every "
            "run that skipped the work entirely, which is the single failure mode "
            "the whole citation contract is built on refusing. Note the shape of "
            "this mutant: it does not crash and it does not go quiet, it returns "
            "the SATISFIED verdict on an empty repo, so nothing but an explicit "
            "absent-frame test can tell it from the real thing."
        ),
        subs=(
            (
                "        return (\n            FRAME_MISSING,\n            EXIT_RECEIPT_UNUSABLE,\n",
                "        return (\n            FRAME_OK,\n            EXIT_OK,\n",
            ),
        ),
        expect_kills="AbsentFrameRefuses",
    ),
    Mutation(
        name="the undeclared-substitute refusal disabled",
        why=(
            "Degraded frames would then be checked against nothing but themselves: "
            "an agent could cite any known fallback it never declared at orient "
            "time, which collapses the comparison against a COMMITTED PRIOR back "
            "into the same-breath assertion the hash-pinning exists to replace."
        ),
        subs=(
            (
                "            if norm in KNOWN_FALLBACK_SET and norm not in declared:\n",
                "            if False:\n",
            ),
        ),
        expect_kills="VerifyFrameDegraded",
    ),
    Mutation(
        name="the known-fallback label granted on set membership alone",
        why=(
            "Drops the filesystem half of the partial oracle. A declared-but-ABSENT "
            "README.md would wear the verified label, so the receipt's distinction "
            "between 'resolved from the known fallback set' and 'the agent said so' "
            "would be decoration -- the label would be re-derived from the agent's "
            "own declaration, which is precisely what it exists to be independent of."
        ),
        subs=(
            (
                "    if exists and normalize_cited_path(rel_path) in KNOWN_FALLBACK_SET:\n",
                "    if normalize_cited_path(rel_path) in KNOWN_FALLBACK_SET:\n",
            ),
        ),
        expect_kills="SubstituteLabels",
    ),
    # ---- g2 rework: the label must stay REPORTED, not merely stored ---------
    Mutation(
        name="every substitute reported as known-fallback",
        why=(
            "The dangerous direction: an agent-declared substitute silently wearing "
            "the verified label. This is the mutation the ORIGINAL g2 work could not "
            "have killed at all, because `substitute_label` was reachable only from "
            "`self_test` -- no output surface read it back, so no test outside the "
            "module's own harness could tell the two labels apart. Pinned here so the "
            "read side cannot rot back into dead code."
        ),
        subs=(
            (
                '        return entry["source"]\n    return LABEL_AGENT_DECLARED\n',
                '        return entry["source"]\n    return LABEL_KNOWN_FALLBACK\n',
            ),
        ),
        expect_kills="SubstituteProvenanceIsReported",
    ),
    Mutation(
        name="the provenance line dropped from the report",
        why=(
            "Reverts the g2 review BLOCK exactly: the receipt still CARRIES the "
            "provenance and no reader is ever shown it. A distinction no output "
            "surface emits is a distinction that does not exist."
        ),
        subs=(
            (
                '        lines.append(f"substitute: {path if path else \'(no path)\'} [{label}] -- {note}")\n',
                "        pass\n",
            ),
        ),
        expect_kills="SubstituteProvenanceIsReported",
    ),
)


def apply_mutation(source: str, mutation: Mutation) -> str:
    """Apply every substitution, refusing loudly when one does not match."""
    mutated = source
    for old, new in mutation.subs:
        occurrences = mutated.count(old)
        if occurrences != 1:
            raise HarnessError(
                f"HARNESS ERROR: mutation {mutation.name!r} did not apply -- the anchor "
                f"text occurred {occurrences} time(s), expected exactly 1. The module was "
                f"edited without updating this harness. This is NOT a killed mutant.\n"
                f"  anchor: {old!r}"
            )
        mutated = mutated.replace(old, new, 1)
    return mutated


# ANSI CSI sequences (colour, bold, cursor moves). See strip_ansi() below.
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    """Remove ANSI escapes so captured output can be parsed as plain text.

    ISSUE #454 -- the defect this exists to refuse. The Claude Code harness
    exports `FORCE_COLOR=3`, which makes pytest colourize even when its stdout
    is a captured pipe rather than a terminal. The colour RESET then lands
    between `FAILED` and the test path:

        \\x1b[31mFAILED\\x1b[0m tests/test_map_orient.py::\\x1b[1mFoo::bar\\x1b[0m

    `failed_nodes` matched nothing, so this harness reported
    "HARNESS ERROR: non-zero exit with no FAILED test node" while its own
    captured output plainly contained those nodes -- ten tests red for a reason
    with no bearing on what they test. That false red burned three independent
    agents in one day.

    `run_floor` now neutralises colour in the child's environment, so in the
    normal case this function has nothing to do. It is kept as a second line of
    defence: a future forced-colour source this harness does not control (a
    pytest plugin, a CI runner, a config file) must not be able to silently
    reintroduce the failure. Parsing is written to tolerate colour rather than
    to assume its absence.
    """
    return ANSI_RE.sub("", text)


def clean_stdout(proc: subprocess.CompletedProcess) -> str:
    """The child's stdout as plain text -- always parse and report through this."""
    return strip_ansi(proc.stdout)


def run_floor(module_path: Path) -> subprocess.CompletedProcess:
    """Run the whole floor with the module under test pointed at `module_path`."""
    env = dict(os.environ)
    env["MAP_ORIENT_MODULE"] = str(module_path)
    # #454: keep the captured output colour-free AT THE SOURCE. `--color=no` is
    # the authoritative switch for pytest itself; the two env vars cover any
    # other colour-capable library the child imports. Belt and braces here is
    # cheap, and the alternative is output nobody can parse OR read.
    env.pop("FORCE_COLOR", None)
    env["NO_COLOR"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(FLOOR), "-q", "-p", "no:cacheprovider", "--color=no"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def failed_nodes(proc: subprocess.CompletedProcess) -> list[str]:
    return re.findall(
        r"(?:SUB)?FAILED(?:\([^)]*\))? (tests[/\\]test_map_orient\.py::\S+)", clean_stdout(proc)
    )


def passed_count(proc: subprocess.CompletedProcess) -> int:
    match = re.search(r"(\d+) passed", clean_stdout(proc))
    return int(match.group(1)) if match else 0


class MutationFloor(unittest.TestCase):
    maxDiff = None

    def _copy_module(self, source: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        scripts = Path(tmp.name) / "scripts"
        scripts.mkdir(parents=True)
        target = scripts / "map_orient.py"
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(source)
        return target

    # -- positive control ---------------------------------------------------

    def test_0_unmutated_baseline_is_green(self):
        """A red below must be attributable to the mutation, not to the harness."""
        copy = self._copy_module(ORIGINAL)
        self.assertEqual(copy.read_text(encoding="utf-8"), ORIGINAL)
        proc = run_floor(copy)
        self.assertEqual(
            proc.returncode,
            0,
            "HARNESS ERROR: the unmutated copy does not pass its own floor, so no "
            f"red below proves anything.\n{clean_stdout(proc)[-4000:]}\n{strip_ansi(proc.stderr)[-2000:]}",
        )
        self.assertGreater(passed_count(proc), 0)

    def test_1_mutation_all_to_any_is_killed(self):
        self._assert_mutation_is_killed(MUTATIONS[0])

    def test_2_mutation_unresolvable_root_collapse_is_killed(self):
        self._assert_mutation_is_killed(MUTATIONS[1])

    def test_3_mutation_existence_instead_of_citable_content_is_killed(self):
        self._assert_mutation_is_killed(MUTATIONS[2])

    def test_4_mutation_unmapped_not_any_to_not_all_is_killed(self):
        """Regression: this one SURVIVED the first shipped floor."""
        self._assert_mutation_is_killed(MUTATIONS[3])

    def test_5_mutation_sentinel_accepted_as_a_hash_pin_is_killed(self):
        """Regression: the B1 blocker, pinned so it cannot come back."""
        self._assert_mutation_is_killed(MUTATIONS[4])

    def test_6_mutation_absent_frame_credited_as_a_pass_is_killed(self):
        """THE vacuous pass -- the one mutation this gate exists to pin."""
        self._assert_mutation_is_killed(MUTATIONS[5])

    def test_7_mutation_undeclared_substitute_refusal_disabled_is_killed(self):
        self._assert_mutation_is_killed(MUTATIONS[6])

    def test_8_mutation_known_fallback_label_on_membership_alone_is_killed(self):
        self._assert_mutation_is_killed(MUTATIONS[7])

    def test_9_mutation_every_substitute_reported_as_verified_is_killed(self):
        """g2 review BLOCK regression: the label must stay READ, not just written."""
        self._assert_mutation_is_killed(MUTATIONS[8])

    def test_10_mutation_provenance_line_dropped_is_killed(self):
        self._assert_mutation_is_killed(MUTATIONS[9])

    # -- the shared harness -------------------------------------------------

    def _assert_mutation_is_killed(self, mutation: Mutation) -> None:
        mutated = apply_mutation(ORIGINAL, mutation)

        # ---------------------------------------------------------------
        # STEP 1 -- prove the mutation APPLIED. Everything below is
        # meaningless unless this holds, so it runs first and fails as a
        # HARNESS ERROR rather than as a killed mutant.
        # ---------------------------------------------------------------
        self.assertNotEqual(
            mutated,
            ORIGINAL,
            f"HARNESS ERROR: {mutation.name}: post-mutation source is identical to the "
            "original. Nothing was changed, so a red run would be a lie.",
        )
        for old, new in mutation.subs:
            self.assertEqual(
                ORIGINAL.count(old),
                1,
                f"HARNESS ERROR: {mutation.name}: anchor {old!r} is not unique in the "
                "original module; the harness cannot target it.",
            )
            self.assertEqual(
                mutated.count(old),
                0,
                f"HARNESS ERROR: {mutation.name}: original text {old!r} survived the "
                "substitution.",
            )
            # A count DELTA, not `in`: the replacement text may legitimately
            # already appear elsewhere in the module, and `in` would then pass
            # even if nothing had been substituted.
            self.assertEqual(
                mutated.count(new),
                ORIGINAL.count(new) + 1,
                f"HARNESS ERROR: {mutation.name}: replacement {new!r} did not increase by "
                f"exactly one (before={ORIGINAL.count(new)}, after={mutated.count(new)}).",
            )

        copy = self._copy_module(mutated)
        self.assertEqual(
            copy.read_text(encoding="utf-8"),
            mutated,
            f"HARNESS ERROR: {mutation.name}: the copy on disk is not the mutated source.",
        )

        # ---------------------------------------------------------------
        # STEP 2 -- only now, compare. The floor must go RED.
        # ---------------------------------------------------------------
        proc = run_floor(copy)
        self.assertNotEqual(
            proc.returncode,
            0,
            f"MUTANT SURVIVED: {mutation.name}\nwhy it matters: {mutation.why}\n"
            "The floor passed against a module that no longer holds the contract, so "
            "the floor does not actually test it.\n"
            f"{clean_stdout(proc)[-4000:]}",
        )

        # The red must be a real kill, not a broken import.
        self.assertGreater(
            passed_count(proc),
            0,
            f"HARNESS ERROR: {mutation.name}: the mutated module collected no passing "
            f"tests, so the floor went red for the wrong reason.\n{clean_stdout(proc)[-4000:]}",
        )
        nodes = failed_nodes(proc)
        self.assertTrue(
            nodes,
            f"HARNESS ERROR: {mutation.name}: non-zero exit with no FAILED test node.\n"
            f"{clean_stdout(proc)[-4000:]}",
        )
        self.assertTrue(
            any(f"::{mutation.expect_kills}::" in node for node in nodes),
            f"{mutation.name} went red, but no test in {mutation.expect_kills} failed -- "
            f"the intended guard did not catch it.\nfailed: {nodes}",
        )


class HarnessSelfCheck(unittest.TestCase):
    """The harness's own failure mode must be loud, not silent."""

    def test_a_non_matching_substitution_raises_a_harness_error(self):
        bogus = Mutation(
            name="deliberately non-matching",
            why="proves a missed substitution is reported as a harness error",
            subs=(("this text is not in the module at all\n", "replacement\n"),),
            expect_kills="CitableContent",
        )
        with self.assertRaises(HarnessError) as caught:
            apply_mutation(ORIGINAL, bogus)
        self.assertIn("did not apply", str(caught.exception))
        self.assertIn("NOT a killed mutant", str(caught.exception))

    def test_an_ambiguous_anchor_raises_a_harness_error(self):
        ambiguous = Mutation(
            name="deliberately ambiguous",
            why="an anchor matching many sites cannot be targeted",
            subs=(("\n", "\n"),),
            expect_kills="CitableContent",
        )
        with self.assertRaises(HarnessError):
            apply_mutation(ORIGINAL, ambiguous)

    def test_every_named_mutation_has_a_unique_anchor_in_the_shipped_module(self):
        for mutation in MUTATIONS:
            for old, _ in mutation.subs:
                with self.subTest(mutation=mutation.name):
                    self.assertEqual(ORIGINAL.count(old), 1, f"anchor not unique: {old!r}")


class ForcedColourDoesNotBreakParsing(unittest.TestCase):
    """ISSUE #454 regression guard -- a false RED is as bad as a false GREEN.

    Under `FORCE_COLOR=3` (which the Claude Code harness exports) pytest
    colourizes into a captured pipe, `failed_nodes` matched nothing, and this
    file reported ten HARNESS ERRORs about output that plainly contained the
    nodes it said were missing. Three independent agents were sent chasing a
    defect that did not exist.

    Both halves of the fix are pinned here, because either alone would let it
    back: the environment neutralisation stops colour AT THE SOURCE, and the
    parsing tolerates colour anyway in case some future source is one this
    harness does not control.
    """

    # Recorded VERBATIM from the RED run of this file under FORCE_COLOR=3.
    # Do not "tidy" the escapes -- the point is that this is what pytest really
    # emitted, including the reset sitting between `FAILED` and the test path.
    COLOURED_TAIL = (
        "\x1b[31mFAILED\x1b[0m tests/test_map_orient.py::"
        "\x1b[1mSubstituteProvenanceIsReported::test_BOTH_labels_appear_in_one_real_report"
        "\x1b[0m - AssertionError: 'known-fallback' not found in 'DEGRADED-NO-MAP...\n"
        "\x1b[31m\x1b[31m\x1b[1m5 failed\x1b[0m, \x1b[32m82 passed\x1b[0m, "
        "\x1b[32m39 subtests passed\x1b[0m\x1b[31m in 14.33s\x1b[0m\x1b[0m\n"
    )
    EXPECTED_NODE = (
        "tests/test_map_orient.py::"
        "SubstituteProvenanceIsReported::test_BOTH_labels_appear_in_one_real_report"
    )

    @staticmethod
    def _captured(stdout: str) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(args=[], returncode=1, stdout=stdout, stderr="")

    def test_the_fixture_really_does_carry_ansi_escapes(self):
        """Guards the guard: a fixture that lost its escapes proves nothing."""
        self.assertIn("\x1b[", self.COLOURED_TAIL)
        self.assertNotIn("\x1b[", strip_ansi(self.COLOURED_TAIL))

    def test_failed_nodes_reads_a_colourized_FAILED_line(self):
        self.assertEqual(
            failed_nodes(self._captured(self.COLOURED_TAIL)),
            [self.EXPECTED_NODE],
            "#454 REGRESSION: a FAILED node wrapped in ANSI was not parsed, so a real "
            "kill would be reported as 'non-zero exit with no FAILED test node'.",
        )

    def test_passed_count_reads_a_colourized_summary_line(self):
        self.assertEqual(
            passed_count(self._captured(self.COLOURED_TAIL)),
            82,
            "#454 REGRESSION: the passed count was misread from a colourized summary.",
        )

    def test_run_floor_strips_colour_from_the_child_even_when_FORCE_COLOR_is_set(self):
        """The source-side half: the captured output must be clean as CAPTURED.

        This is the assertion that actually reproduces the bug -- it sets the
        exact variable the harness sets and looks at what comes back. Runs the
        real floor once, which is the only honest way to prove what the child
        environment does.
        """
        with mock.patch.dict(os.environ, {"FORCE_COLOR": "3"}):
            proc = run_floor(MODULE)
        self.assertNotIn(
            "\x1b",
            proc.stdout,
            "#454 REGRESSION: FORCE_COLOR leaked into the floor subprocess, so its "
            "captured stdout carries ANSI escapes. Every parse and every truncated "
            f"diagnostic dump in this file is now unreliable.\n{proc.stdout[:2000]}",
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"the unmutated floor should still pass\n{clean_stdout(proc)[-2000:]}",
        )


if __name__ == "__main__":
    unittest.main()
