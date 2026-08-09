"""Tests for scripts/verify_episode_captured.py — the WRITE-side capture gate that
replaces the retiring `.agent-work/LESSONS.md` / `.agent-work/AGENT_FEEDBACK.md`
machinery (issue #447, epic-418 workstream H).

The gate asserts one thing: this run left an episode behind. Not ripeness, not
apply-or-defer, not dormancy, not counters — those are playbook concepts and they
retire with the playbook.

Every test seeds a THROWAWAY temp store through the store's only sanctioned write path
(`scripts/apply_episode_delta.py`), never the real `episodes/` directory, so the repo
stays clean and the suite is order-independent.

Every seeded assertion statement is the literal SENTINEL, so any test in this file that
printed record content would show it. `ValveTests` is where that is asserted, and
`ValveTests.test_red_proof_...` is where the leak assertion is shown able to FAIL — a
leak test that cannot fail is worth nothing.
"""

import ast
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_episode_captured.py"

SENTINEL = "SENTINEL-DO-NOT-LEAK-9f2a"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _create_op(run):
    """One valid `create` op whose every assertion statement is the sentinel."""
    return {
        "op": "create",
        "mechanical": {
            "run": run,
            "project": "constellation-skills",
            "role": "commander",
            "spine-step": "feedback",
            "context-manifest-ref": "none",
            "refusals": 0,
            "reopens": 0,
            "rework-count": 0,
            "failed-commands": 0,
        },
        "agent_supplied": {
            kind: {"strength": "strong", "statement": SENTINEL}
            for kind in (
                "task-intent",
                "expected-behavior",
                "observed-behavior",
                "impact-cost",
                "workaround",
            )
        },
    }


class _StoreCase(unittest.TestCase):
    """Temp store + the two ways this gate is exercised: in-process and as a CLI."""

    def setUp(self):
        self.writer = _load("apply_episode_delta")
        self.verify = _load("verify_episode_captured")
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.store = self.base / "episodes"

    def tearDown(self):
        self.tmp.cleanup()

    def empty_store(self):
        """A store that exists and holds no episodes — the writer bootstraps the layout."""
        self.writer.ensure_store_layout(self.store)

    def seed(self, run, count=1, store=None):
        root = self.store if store is None else store
        delta = {"work_id": run, "ops": [_create_op(run) for _ in range(count)]}
        path = self.base / "delta.json"
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(delta, handle)
        rc = self.writer.main(["--delta", str(path), "--store-root", str(root)])
        self.assertEqual(0, rc, "fixture seeding failed")

    def run_gate(self, argv):
        """Run the gate IN-PROCESS with stdout and stderr both captured.

        Both the valve assertion and its red proof go through this one path, so the red
        proof exercises the same assertion the real test does."""
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = self.verify.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def run_cli(self, argv, cwd=None):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *argv],
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
        return proc.returncode, proc.stdout, proc.stderr


class CaptureTests(_StoreCase):
    def test_seeded_store_passes_and_prints_ids_and_count(self):
        self.seed("issue-447", count=2)
        rc, out, err = self.run_gate(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(0, rc, err)
        self.assertIn("issue-447-001", out)
        self.assertIn("issue-447-002", out)
        self.assertIn("2", out)

    def test_empty_store_fails(self):
        self.empty_store()
        rc, out, err = self.run_gate(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(1, rc)
        self.assertIn("issue-447", err)

    def test_store_holding_only_other_runs_fails(self):
        self.seed("issue-999")
        rc, out, err = self.run_gate(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(1, rc)
        self.assertIn("issue-447", err)

    def test_cli_exit_codes_match_the_in_process_ones(self):
        self.seed("issue-447")
        rc, out, err = self.run_cli(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(0, rc, err)
        rc, out, err = self.run_cli(["issue-000", "--store-root", str(self.store)])
        self.assertEqual(1, rc)


class RefusalTests(_StoreCase):
    """A store this gate cannot read is REFUSED, not answered as zero.

    `episodes/README.md`: *"A missing directory is refused, not answered."* A typo'd
    `--store-root` enumerating to zero episodes with exit 0 reads exactly like an empty
    store, and the exit code is the only thing a spine sees."""

    def test_missing_store_root_is_refused(self):
        rc, out, err = self.run_gate(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(self.verify.EXIT_REFUSED, rc)
        self.assertNotEqual(self.verify.EXIT_CAPTURED, rc)
        self.assertIn(str(self.store), err)

    def test_missing_active_directory_is_refused(self):
        (self.store / "retired").mkdir(parents=True)
        rc, out, err = self.run_gate(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(self.verify.EXIT_REFUSED, rc)
        self.assertIn("active", err)

    def test_refusal_is_distinguishable_from_the_no_match_block(self):
        """Two different failures must not share one exit code — a spine that cannot
        tell "you did not capture" from "I could not look" cannot act on either."""
        self.empty_store()
        blocked, _, _ = self.run_gate(["issue-447", "--store-root", str(self.store)])
        refused, _, _ = self.run_gate(["issue-447", "--store-root", str(self.base / "typo")])
        self.assertEqual(self.verify.EXIT_BLOCKED, blocked)
        self.assertEqual(self.verify.EXIT_REFUSED, refused)
        self.assertNotEqual(blocked, refused)

    def test_unreadable_record_is_refused_not_skipped(self):
        """A record with no `- run:` line is refused rather than skipped: skipping is
        how a real record becomes invisible to the gate that is supposed to require it."""
        self.seed("issue-447")
        stray = self.store / "active" / "issue-447-002.md"
        with stray.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write("<!-- episode-state: schema=1 id=issue-447-002 status=active -->\n")
        rc, out, err = self.run_gate(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(self.verify.EXIT_REFUSED, rc)
        self.assertIn("issue-447-002.md", err)


class ArchivePhaseTests(_StoreCase):
    """`--phase archive` additionally asks git whether the episode will survive.

    This is what replaces the old archive-phase durability question: a run that writes
    an episode and forgets to `git add episodes/` has captured nothing that outlives
    the worktree, and must fail."""

    def _git_repo(self):
        subprocess.run(["git", "init", "-q", str(self.base)], check=True, capture_output=True)

    def _episode_path(self, episode_id):
        return self.store / "active" / f"{episode_id}.md"

    def test_archive_phase_passes_for_a_tracked_episode(self):
        self._git_repo()
        self.seed("issue-447")
        subprocess.run(
            ["git", "add", str(self._episode_path("issue-447-001"))],
            cwd=str(self.base), check=True, capture_output=True,
        )
        rc, out, err = self.run_gate(
            ["issue-447", "--store-root", str(self.store), "--phase", "archive"]
        )
        self.assertEqual(0, rc, err)
        self.assertIn("issue-447-001", out)

    def test_archive_phase_fails_for_an_untracked_episode(self):
        self._git_repo()
        self.seed("issue-447")
        rc, out, err = self.run_gate(
            ["issue-447", "--store-root", str(self.store), "--phase", "archive"]
        )
        self.assertEqual(1, rc)
        self.assertIn("issue-447-001", err)
        self.assertIn("git add", err)

    def test_archive_phase_accepts_a_relative_store_root(self):
        """Regression, found by running the gate against the real store: git resolves a
        relative pathspec against ITS OWN cwd, so a `--store-root episodes` reaching the
        git check unresolved asked about `episodes/active/episodes/active/<id>.md` and
        reported 25 of 25 committed episodes as untracked. Absolute temp paths — the
        only shape the other tests use — cannot catch that."""
        self._git_repo()
        self.seed("issue-447")
        subprocess.run(
            ["git", "add", "episodes"], cwd=str(self.base), check=True, capture_output=True
        )
        rc, out, err = self.run_cli(
            ["issue-447", "--store-root", "episodes", "--phase", "archive"], cwd=self.base
        )
        self.assertEqual(0, rc, err)

    def test_feedback_phase_does_not_ask_git(self):
        """The green half of the pair above: the same untracked episode passes at the
        feedback phase, so the archive failure is the git question and nothing else."""
        self._git_repo()
        self.seed("issue-447")
        rc, out, err = self.run_gate(["issue-447", "--store-root", str(self.store)])
        self.assertEqual(0, rc, err)


class ValveTests(_StoreCase):
    """THE VALVE: ids and counts out, assertion statements never.

    Episodes are a record of what happened, not a playbook. A capture gate that can
    surface episode content is one refactor away from being the playbook again, so the
    absence of statement text in the gate's output is asserted here rather than
    asserted in prose."""

    def _assert_no_leak(self, argv):
        """The leak assertion itself, factored out so the red proof below can exercise
        this exact code path rather than a lookalike."""
        rc, out, err = self.run_gate(argv)
        self.assertNotIn(SENTINEL, out, "assertion statement text reached stdout")
        self.assertNotIn(SENTINEL, err, "assertion statement text reached stderr")
        return rc

    def test_no_statement_text_reaches_stdout_or_stderr(self):
        """Every outcome path, not just the happy one: a pass, a block, and a refusal."""
        self.seed("issue-447", count=2)
        self.seed("issue-999")
        cases = {
            "captured": ["issue-447", "--store-root", str(self.store)],
            "blocked": ["issue-000", "--store-root", str(self.store)],
            "archive-blocked": ["issue-447", "--store-root", str(self.store), "--phase", "archive"],
            "refused": ["issue-447", "--store-root", str(self.base / "typo")],
        }
        seen = 0
        for label, argv in cases.items():
            with self.subTest(outcome=label):
                self._assert_no_leak(argv)
                seen += 1
        self.assertEqual(len(cases), seen, "not every outcome path was exercised")

    def test_the_leak_assertion_can_fail(self):
        """The red proof. A leak test that cannot fail is worth nothing.

        Patch the gate's one read seam so it echoes the whole record body, then run the
        SAME assertion helper the test above uses and require it to fail. If this test
        ever passes silently, the assertion above has stopped asserting anything."""
        self.seed("issue-447")
        real_scan = self.verify.scan_episode

        def leaky_scan(path):
            print(path.read_text(encoding="utf-8"))  # the defect, injected on purpose
            return real_scan(path)

        self.verify.scan_episode = leaky_scan
        try:
            with self.assertRaises(AssertionError) as caught:
                self._assert_no_leak(["issue-447", "--store-root", str(self.store)])
        finally:
            self.verify.scan_episode = real_scan
        self.assertIn("reached stdout", str(caught.exception))
        # and the gate is un-leaky again once the patch is off
        self._assert_no_leak(["issue-447", "--store-root", str(self.store)])

    def test_the_gate_links_to_no_store_reader(self):
        """No `query_episodes` import — and more generally, no import of ANY module in
        scripts/. The check reads the real import graph with `ast` rather than grepping
        text, because this file's own prose names `query_episodes` several times."""
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported, "no imports parsed — the guard looped over nothing")
        self.assertNotIn("query_episodes", imported)
        repo_local = sorted(n for n in imported if (ROOT / "scripts" / f"{n}.py").exists())
        self.assertEqual([], repo_local, f"the gate imports repo-local module(s): {repo_local}")


if __name__ == "__main__":
    unittest.main()
