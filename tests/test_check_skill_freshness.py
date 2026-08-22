"""Coverage for `_resolved_interpreter()`'s sidecar-missing/malformed fallback
(issue #532).

PR #531 fixed `_normalized_hash()`'s phantom `upstream-changed` bug: it used
to re-derive the installed interpreter by mirroring `os.name`
(`_platform_interpreter()`) instead of reading what the installer actually
probed, so a POSIX host where `py` genuinely resolves (a shim, an alias) read
its own untouched install as drifted. The fix added `_resolved_interpreter()`,
which reads the per-skill `interpreter.json` sidecar the installer now writes,
falling back to the old `_platform_interpreter()` guess only when the sidecar
is missing or malformed.

#532's claim was two-part: (a) that fallback has no test, and (b) it
"restores the bug it replaced". (a) was simply true -- nothing under tests/
referenced `_resolved_interpreter` before this file. (b) is true in a narrow,
literal sense: TestPhantomConsequence below reproduces the exact PR #531
symptom for a no-sidecar (legacy) skill, on purpose -- read it as
documentation of an accepted, bounded gap, not a red-before-green fix. It was
deliberately NOT changed: unlike `install_constellation.resolve_interpreter()`
(owner ruling #539), where a failed probe permanently stamps a
guaranteed-wrong value into shipped skill bodies with no trace back,
`_resolved_interpreter()` is read-only and transient -- `update_baseline()`
hashes raw upstream bytes directly and never calls it (nothing it returns is
ever persisted), and a wrong guess only mislabels one freshness-report row,
recomputed fresh next run, with the mislabel itself as the trace. There is
also no dominant replacement: a no-sidecar skill was installed either before
#228 added host probing (when the real installer used exactly this os.name
guess -- today's fallback is the historically ACCURATE reconstruction) or
between #228 and #531 (when the installer probed live but wrote no sidecar --
a live re-probe now would help only these). The checker cannot tell which
epoch a given skill belongs to, so no single strategy dominates. Hence: tests
only, no source behavior change.

House pattern (`tests/test_mcp_spine_server.py::McpJsonTests`): every guard
gets a positive control proving it is not vacuous -- a value engineered to
prove the guard actually discriminates, not just that it runs once and
passes."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_skill_freshness.py"
_spec = importlib.util.spec_from_file_location("check_skill_freshness", SCRIPT)
CSF = importlib.util.module_from_spec(_spec)
sys.modules["check_skill_freshness"] = CSF
_spec.loader.exec_module(CSF)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ResolvedInterpreterFallbackTests(unittest.TestCase):
    """Direct coverage of `_resolved_interpreter()`'s three degrade-gracefully
    branches, each paired with a positive control."""

    def test_missing_sidecar_falls_back_to_platform_guess(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp)
            (skills_root / "constellation-widget").mkdir()
            # no interpreter.json at all
            self.assertEqual(
                CSF._platform_interpreter(),
                CSF._resolved_interpreter("constellation-widget", skills_root),
            )

    def test_sidecar_present_is_read_not_ignored(self):
        """POSITIVE CONTROL for the missing-sidecar case: proves the
        `sidecar.is_file()` branch is actually gating a real read, not a dead
        check that always falls through to the guess regardless."""
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp)
            skill_dir = skills_root / "constellation-widget"
            skill_dir.mkdir()
            _write(skill_dir / "interpreter.json", json.dumps({"interpreter": "distinctive-marker"}))
            self.assertEqual(
                "distinctive-marker",
                CSF._resolved_interpreter("constellation-widget", skills_root),
            )

    def test_malformed_json_sidecar_falls_back_to_platform_guess(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp)
            skill_dir = skills_root / "constellation-widget"
            skill_dir.mkdir()
            _write(skill_dir / "interpreter.json", "{not valid json")
            self.assertEqual(
                CSF._platform_interpreter(),
                CSF._resolved_interpreter("constellation-widget", skills_root),
            )

    def test_well_formed_sidecar_is_not_treated_as_malformed(self):
        """POSITIVE CONTROL for the malformed-JSON case: proves the
        json.JSONDecodeError catch is scoped to genuinely bad JSON, not
        silently swallowing well-formed sidecars too."""
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp)
            skill_dir = skills_root / "constellation-widget"
            skill_dir.mkdir()
            _write(skill_dir / "interpreter.json", json.dumps({"interpreter": "py"}))
            self.assertEqual(
                "py", CSF._resolved_interpreter("constellation-widget", skills_root)
            )

    def test_sidecar_missing_interpreter_key_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp)
            skill_dir = skills_root / "constellation-widget"
            skill_dir.mkdir()
            # a sidecar shape with no "interpreter" key -- e.g. a stale/partial write
            _write(skill_dir / "interpreter.json", json.dumps({"candidates": ["py", "python3"]}))
            self.assertEqual(
                CSF._platform_interpreter(),
                CSF._resolved_interpreter("constellation-widget", skills_root),
            )

    def test_sidecar_empty_interpreter_value_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp)
            skill_dir = skills_root / "constellation-widget"
            skill_dir.mkdir()
            _write(skill_dir / "interpreter.json", json.dumps({"interpreter": ""}))
            self.assertEqual(
                CSF._platform_interpreter(),
                CSF._resolved_interpreter("constellation-widget", skills_root),
            )


class PhantomConsequenceTests(unittest.TestCase):
    """The 'consequence' pair #532 named as the one that matters: what
    actually happens through check() -- not just what _resolved_interpreter()
    returns in isolation -- when the sidecar-missing fallback's guess
    disagrees with the interpreter really baked into an installed skill.

    A template lives in three forms compared by check(): baseline and the
    project working copy stay in portable TOKEN form (`python <script.py>`
    literally, never rewritten); the installed upstream copy has the token
    already replaced with the interpreter that install actually resolved.
    _normalized_hash() re-derives what upstream's replacement WOULD be for
    baseline/local so the three sides compare on equal footing -- so a wrong
    guess desyncs baseline/local from upstream's real, unchanged text."""

    @staticmethod
    def _seed(repo: Path, *, real_interpreter: str) -> None:
        skills_root = repo / "skills"
        skill_dir = skills_root / "constellation-widget"
        _write(skill_dir / "templates" / "WIDGET.template.md", f"{real_interpreter} <script.py>\n")
        _write(skill_dir / "interpreter.json", json.dumps({"interpreter": real_interpreter}))

        templates_root = repo / ".agent-work" / "templates"
        _write(
            templates_root / ".baseline" / "constellation-widget" / "WIDGET.template.md",
            "python <script.py>\n",
        )
        _write(templates_root / "WIDGET.template.md", "python <script.py>\n")
        _write(
            templates_root / "TEMPLATES_MANIFEST.json",
            json.dumps({"templates": [{"skill": "constellation-widget", "template": "WIDGET.template.md"}]}),
        )

    def _status(self, repo: Path) -> str:
        rows = CSF.check(repo, repo / "skills")
        self.assertEqual(1, len(rows))
        return rows[0]["status"]

    def test_phantom_upstream_changed_reproduced_when_sidecar_missing_and_guess_wrong(self):
        """Documents the accepted, narrow gap #532 identified -- pinned on
        purpose, not silently accepted. A real install stamped `py` (the
        probed interpreter); the sidecar that would prove it is then lost
        (deleted / never written, e.g. a pre-#531 install); the platform
        guess disagrees. The phantom PR #531 fixed is back, scoped to exactly
        this narrow condition."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._seed(repo, real_interpreter="py")
            (repo / "skills" / "constellation-widget" / "interpreter.json").unlink()
            with mock.patch.object(CSF, "_platform_interpreter", return_value="python3"):
                self.assertEqual("upstream-changed", self._status(repo))

    def test_sidecar_present_prevents_phantom_even_when_guess_would_be_wrong(self):
        """POSITIVE CONTROL: same seed, same wrong guess forced -- but the
        sidecar PR #531 added is present, so it is read instead of the guess
        and the phantom does not appear. Proves the test above is measuring
        the sidecar's absence, not something else."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._seed(repo, real_interpreter="py")
            with mock.patch.object(CSF, "_platform_interpreter", return_value="python3"):
                self.assertEqual("up-to-date", self._status(repo))


if __name__ == "__main__":
    unittest.main()
