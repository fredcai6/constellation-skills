"""Golden-fixture suite for scripts/curate_corpus.py.

Each test builds a throwaway skills/ corpus in a tempfile.TemporaryDirectory,
runs the curator's mechanical checks over it, and asserts that a specific
detector BITES (a detector that finds nothing on a planted flaw is a broken
detector). The planted DUPLICATION flaws are the AUTHENTIC pre-#108 doctrine
passages (sourced verbatim from commit 2696769, before cluster A single-sourced
them) so the golden test measures the real drift the epic eliminated.

The final test FALSIFIES curator invariant #2 (flags-never-gates): a corpus with
every detector firing at once must still exit 0.

Stdlib + unittest only; asserts against the EXACT status/check strings read from
curate_corpus.py.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURATE = ROOT / "scripts" / "curate_corpus.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cc = load_module("curate_corpus", CURATE)


# --- authentic pre-#108 duplication shapes (verbatim, commit 2696769) --------
# These are the exact doctrine passages cluster A single-sourced. Planted into
# >= 2 fixture skills each, they are what the shingle detector must cluster.
COMPLIANCE_BOILERPLATE = (
    "Mandatory, no exceptions: once loaded, drive the checklist to completion "
    "through the engine and dispatch each step it names. Within a step, judgment "
    "is yours — when an instruction does not fit the work, do the closest "
    "compliant thing and report the misfit in your workflow feedback; reporting "
    "misfit is compliance, not deviation."
)
EMPHATIC_BANNER = "FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY"
ENGINE_INVOCATION = (
    "Drive a controller one step at a time with the absolute path to this "
    "installed skill's bundled scripts/checklist_engine.py"
)


def write_skill(root: Path, name: str, frontmatter: dict, body: str,
                references: dict | None = None) -> Path:
    """Write skills/<name>/SKILL.md (+ optional references/*.md) under root."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    fm_lines = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
    (skill_dir / "SKILL.md").write_text(
        f"---\n{fm_lines}\n---\n{body}\n", encoding="utf-8")
    if references:
        refs = skill_dir / "references"
        refs.mkdir(exist_ok=True)
        for fname, text in references.items():
            (refs / fname).write_text(text, encoding="utf-8")
    return skill_dir


def write_raw_skill(root: Path, name: str, raw: str) -> Path:
    """Write a SKILL.md with fully raw (possibly malformed) content."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(raw, encoding="utf-8")
    return skill_dir


def clean_frontmatter(name: str, **overrides) -> dict:
    """A third-person, budget-clean, non-confusable frontmatter baseline so that
    only the flaw a test PLANTS shows up. Callers override to plant a flaw."""
    fm = {
        "name": name,
        "description": "Compress logs. Use when a run leaves scattered records.",
        "invoker": "agent",
    }
    fm.update(overrides)
    return fm


def find(findings, skill=None, check=None):
    out = findings
    if skill is not None:
        out = [f for f in out if f.skill == skill]
    if check is not None:
        out = [f for f in out if f.check == check]
    return out


class StatusVocabularyTests(unittest.TestCase):
    """Lock the exact status strings the whole suite asserts against."""

    def test_status_vocabulary_is_the_expected_literals(self):
        self.assertEqual(cc.STATUS_FLAGGED, "flagged")
        self.assertEqual(cc.STATUS_SHORTLIST, "shortlist")
        self.assertEqual(cc.STATUS_INFO, "info")
        self.assertEqual(cc.STATUS_OK, "ok")


class DuplicationDetectorTests(unittest.TestCase):
    def test_duplication_bites_two_authentic_signatures(self):
        """Compliance boilerplate in {alpha,beta} and the engine-invocation
        string in {delta,gamma} produce two distinct `duplication` clusters,
        each `flagged`, naming exactly the sharing skills."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "alpha", clean_frontmatter("alpha"),
                        COMPLIANCE_BOILERPLATE + "\nAlpha keeps one distinctive tail clause.")
            write_skill(root, "beta", clean_frontmatter("beta"),
                        COMPLIANCE_BOILERPLATE + "\nBeta diverges wholly elsewhere in prose.")
            write_skill(root, "gamma", clean_frontmatter("gamma"),
                        ENGINE_INVOCATION + "\nGamma padding stays entirely singular here.")
            write_skill(root, "delta", clean_frontmatter("delta"),
                        ENGINE_INVOCATION + "\nDelta padding shares nothing with the rest.")

            findings = cc.curate(root)
            dups = find(findings, check="duplication")

            self.assertEqual(len(dups), 2,
                             f"expected two clusters, got {[d.detail for d in dups]}")
            for d in dups:
                self.assertEqual(d.status, "flagged")

            by_skills = {tuple(d.extra["skills"]): d for d in dups}
            self.assertIn(("alpha", "beta"), by_skills)
            self.assertIn(("delta", "gamma"), by_skills)
            # finding.skill is the comma-joined sorted sharing set.
            self.assertEqual(by_skills[("alpha", "beta")].skill, "alpha,beta")
            self.assertGreaterEqual(by_skills[("alpha", "beta")].extra["shingle_count"], 1)

    def test_duplication_ignores_a_single_planting(self):
        """A signature in only one skill must NOT cluster (needs >= 2 skills)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "solo", clean_frontmatter("solo"), COMPLIANCE_BOILERPLATE)
            write_skill(root, "other", clean_frontmatter("other"),
                        "Wholly unrelated body with no shared eight word window at all here.")
            self.assertEqual(find(cc.curate(root), check="duplication"), [])

    def test_emphatic_banner_clusters_as_exact_shingle(self):
        """The banner tokenizes to exactly SHINGLE_SIZE (8) words
        ('follow this skill strictly use the engine rigorously'), so it is the
        boundary case: planted in >= 2 skills it forms exactly one shingle and
        DOES cluster. (Any shorter phrase would not.)"""
        self.assertEqual(cc.SHINGLE_SIZE, 8)
        self.assertEqual(len(cc._words(EMPHATIC_BANNER)), cc.SHINGLE_SIZE)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "eps", clean_frontmatter("eps"),
                        EMPHATIC_BANNER + "\nEpsilon owns a totally separate closing remark.")
            write_skill(root, "zeta", clean_frontmatter("zeta"),
                        EMPHATIC_BANNER + "\nZeta closes on an unrelated singular note now.")
            dups = find(cc.curate(root), check="duplication")
            self.assertEqual(len(dups), 1)
            self.assertEqual(dups[0].status, "flagged")
            self.assertEqual(tuple(dups[0].extra["skills"]), ("eps", "zeta"))


class SizeDetectorTests(unittest.TestCase):
    def test_oversized_body_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            big_body = " ".join(["word"] * (cc.SKILL_WORD_TARGET + 25))
            write_skill(root, "bloated", clean_frontmatter("bloated"), big_body)
            sizes = find(cc.curate(root), skill="bloated", check="size")
            self.assertTrue(any(f.status == "flagged" for f in sizes),
                            f"size did not flag: {[(f.status, f.detail) for f in sizes]}")

    def test_within_budget_body_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "tight", clean_frontmatter("tight"),
                        "A tight one-screen body well under the word budget.")
            sizes = find(cc.curate(root), skill="tight", check="size")
            self.assertEqual([f.status for f in sizes], ["ok"])


class InvokerDetectorTests(unittest.TestCase):
    def test_missing_invoker_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fm = clean_frontmatter("noinv")
            del fm["invoker"]
            write_skill(root, "noinv", fm, "Body without any invoker frontmatter key at all.")
            inv = find(cc.curate(root), skill="noinv", check="invoker")
            self.assertEqual([f.status for f in inv], ["flagged"])

    def test_present_invoker_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "withinv", clean_frontmatter("withinv", invoker="human"),
                        "Body carrying a valid invoker tag on the frontmatter.")
            inv = find(cc.curate(root), skill="withinv", check="invoker")
            self.assertEqual([f.status for f in inv], ["ok"])
            self.assertEqual(inv[0].extra["invoker"], "human")


class DescriptionDetectorTests(unittest.TestCase):
    def test_first_person_shortlists_not_a_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "persony",
                        clean_frontmatter("persony",
                                          description="Use when you want your logs compressed for us."),
                        "Body text.")
            person = find(cc.curate(root), skill="persony", check="description-person")
            self.assertEqual([f.status for f in person], ["shortlist"])

    def test_missing_when_to_use_marker_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "nowhen",
                        clean_frontmatter("nowhen",
                                          description="Compresses scattered run records into one archive."),
                        "Body text.")
            wtu = find(cc.curate(root), skill="nowhen", check="description-when-to-use")
            self.assertEqual([f.status for f in wtu], ["flagged"])

    def test_confusable_skill_without_exclusion_flagged(self):
        """A skill named in curate_corpus's CONFUSABLE set whose description has
        no exclusion clause is flagged; the same name WITH one is only `info`."""
        self.assertIn("scout", cc.CONFUSABLE_SKILLS)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "scout",
                        clean_frontmatter("scout",
                                          description="Audit architecture. Use when hunting bad patterns."),
                        "Body text.")
            excl = find(cc.curate(root), skill="scout", check="description-exclusion")
            self.assertEqual([f.status for f in excl], ["flagged"])

    def test_confusable_skill_with_exclusion_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "cartographer",
                        clean_frontmatter("cartographer",
                                          description="Map structure. Use when verifying the baseline, "
                                                      "not auditing patterns."),
                        "Body text.")
            excl = find(cc.curate(root), skill="cartographer", check="description-exclusion")
            self.assertEqual([f.status for f in excl], ["info"])

    def test_nonconfusable_skill_gets_no_exclusion_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "randomskill", clean_frontmatter("randomskill"), "Body text.")
            self.assertEqual(
                find(cc.curate(root), skill="randomskill", check="description-exclusion"), [])


class ReferenceTocDetectorTests(unittest.TestCase):
    def test_long_reference_without_toc_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            long_ref = "\n".join(f"line {i}" for i in range(cc.REFERENCE_TOC_LINE_THRESHOLD + 5))
            write_skill(root, "reffed", clean_frontmatter("reffed"), "Body text.",
                        references={"big.md": long_ref})
            toc = find(cc.curate(root), skill="reffed", check="reference-toc")
            self.assertEqual([f.status for f in toc], ["flagged"])
            self.assertEqual(toc[0].extra["reference"], "big.md")

    def test_short_reference_and_toc_reference_not_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            short_ref = "\n".join(f"line {i}" for i in range(10))
            long_with_toc = "## Contents\n" + "\n".join(
                f"line {i}" for i in range(cc.REFERENCE_TOC_LINE_THRESHOLD + 5))
            write_skill(root, "okrefs", clean_frontmatter("okrefs"), "Body text.",
                        references={"small.md": short_ref, "toc.md": long_with_toc})
            self.assertEqual(find(cc.curate(root), skill="okrefs", check="reference-toc"), [])


class ParseAndCrashTests(unittest.TestCase):
    def test_malformed_and_missing_skill_md_become_parse_rows_no_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_raw_skill(root, "badfm", "no frontmatter here at all\njust a body line")
            (root / "nomd").mkdir()  # a skill dir with no SKILL.md
            # curate must not raise:
            findings = cc.curate(root)
            for name in ("badfm", "nomd"):
                rows = find(findings, skill=name, check="parse")
                self.assertEqual([f.status for f in rows], ["flagged"],
                                 f"{name} did not produce a flagged parse row")

    def test_main_exits_zero_even_with_unparseable_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_raw_skill(root, "badfm", "no frontmatter\nbody")
            self.assertEqual(cc.main([str(root)]), 0)


class FlagsNeverGatesTests(unittest.TestCase):
    def _build_maximally_flagged_corpus(self, root: Path):
        """Every detector firing at once in one corpus."""
        # size + missing invoker + missing when-to-use, all on one skill.
        big_body = " ".join(["word"] * (cc.SKILL_WORD_TARGET + 25))
        fm = {"name": "monster",
              "description": "A long chattier description " + ("padding " * 60) + "end."}
        write_skill(root, "monster", fm, big_body)  # size flag, invoker flag, when-to-use flag, length flag
        # duplication (authentic boilerplate) across two skills.
        write_skill(root, "dupone", clean_frontmatter("dupone"),
                    COMPLIANCE_BOILERPLATE + "\nDupone tail clause stands apart from siblings.")
        write_skill(root, "duptwo", clean_frontmatter("duptwo"),
                    COMPLIANCE_BOILERPLATE + "\nDuptwo tail clause is otherwise wholly unique.")
        # confusable skill with no exclusion + first/second person shortlist.
        write_skill(root, "scout",
                    clean_frontmatter("scout",
                                      description="Audit patterns. Use when you scan your codebase."),
                    "Body text.")
        # long reference without a TOC.
        long_ref = "\n".join(f"line {i}" for i in range(cc.REFERENCE_TOC_LINE_THRESHOLD + 5))
        write_skill(root, "reffed", clean_frontmatter("reffed"), "Body text.",
                    references={"big.md": long_ref})
        # unparseable skill dir.
        write_raw_skill(root, "badfm", "no frontmatter here\njust a body")

    def test_maximally_flagged_fixture_still_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._build_maximally_flagged_corpus(root)

            # Sanity: prove the fixture really is maximally flagged before we
            # assert the invariant — every detector's flag is present.
            findings = cc.curate(root)
            flagged_checks = {f.check for f in findings if f.status == "flagged"}
            for expected in ("size", "invoker", "description-length",
                             "description-when-to-use", "description-exclusion",
                             "reference-toc", "duplication", "parse"):
                self.assertIn(expected, flagged_checks,
                              f"fixture did not flag {expected}; flags={sorted(flagged_checks)}")
            self.assertTrue(any(f.status == "shortlist" for f in findings))

            # THE FALSIFICATION: a maximally-flagged corpus must still exit 0.
            self.assertEqual(cc.main([str(root)]), 0)
            self.assertEqual(cc.main([str(root), "--json"]), 0)


if __name__ == "__main__":
    unittest.main()
