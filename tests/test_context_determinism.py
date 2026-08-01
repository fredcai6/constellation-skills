"""The acceptance test for issue #300: the projection manifest's *content* is
identical across environments.

Construction: two clean `git worktree` checkouts of the same commit, at two
different absolute paths, each running the real producer in a child process with
different `LC_ALL`, `LANG` and `PYTHONHASHSEED`. The manifests' `run` subtrees are
expected to differ; everything else must be byte-identical.

**The exclusion set is exactly one JSON pointer, `/run`, and nothing else.** If a
field ever has to be masked to make this pass, that field is in the wrong subtree
and the *design* is wrong, not this test.

**Honest limit.** Same OS, same filesystem, same Python. This exercises path
ordering, locale and hash-ordering — the three things that actually vary between
two runs on one machine. It is NOT a cross-OS or cross-filesystem rebuild, and it
does not claim to be one.

**Why two fresh worktrees rather than this checkout versus one fresh worktree.**
The Commander declaration legitimately names paths that are untracked here and
absent in a clean checkout (`docs/agents/…`). Comparing this working checkout
against a fresh one would therefore compare two *different sets of delivered
bytes* — an honest difference in what was delivered, not a determinism failure —
and asserting byte-identity across it would be asserting something false. Two
clean checkouts of the same commit hold the delivered bytes fixed, which isolates
exactly the variables under test. `RealCheckoutSkew` below covers the
untracked-vs-absent case explicitly instead of hiding it.

**Windows trap** (`lesson:windows-subprocess-env-does-not-shadow-path-resolution`):
passing `env=` into `subprocess.run` does not change which executable an
unqualified name resolves to on Windows. The children are launched via
`sys.executable` (fully qualified), and — more importantly — each child *reports
back* the environment it actually saw, which this test asserts against. The
mutation is verified to have taken effect, never assumed.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cm = load("context_manifest")

#: Files that carry the change under test. They are overlaid from this working tree
#: onto each fresh checkout, so the test measures determinism of *one* version of
#: the code across two environments whether or not that version is committed yet.
#: Without this the test would silently measure HEAD instead of the change.
OVERLAY = (
    "scripts/context_manifest.py",
    "scripts/checklist_engine.py",
    "skills/commander/templates/COMMANDER_SPINE.template.json",
)

#: The Commander declaration is written against the *installed* skill layout, where
#: `scripts/install_constellation.py` has copied `skills/_shared/global-*.md` into
#: each role's `references/`. A bare source checkout has not been installed, so
#: without this shim every declared row would resolve to `rev: null` and the
#: byte-identity assertion would pass vacuously. Applied identically to both
#: checkouts, so it varies nothing under test.
INSTALL_SHIM = (
    ("skills/_shared/global-orchestrator.md",
     "skills/commander/references/global-orchestrator.md"),
    ("skills/_shared/global-everyone.md",
     "skills/commander/references/global-everyone.md"),
)

#: Runs inside each checkout, in its own process, with its own environment. Reports
#: the environment it actually observed alongside the manifest it produced.
CHILD = r'''
import importlib.util, json, os, sys
checkout = sys.argv[1]
out = sys.argv[2]
spec = importlib.util.spec_from_file_location(
    "context_manifest", os.path.join(checkout, "scripts", "context_manifest.py"))
cm = importlib.util.module_from_spec(spec)
sys.modules["context_manifest"] = cm
spec.loader.exec_module(cm)

template = os.path.join(
    checkout, "skills", "commander", "templates", "COMMANDER_SPINE.template.json")
with open(template, encoding="utf-8") as fh:
    spine = json.load(fh)
# A real run reaches `context` with `init` already terminal; the producer then
# selects it through the engine's own active_id(), never a pinned step.
spine["tasks"]["init"]["status"] = "complete"
assert cm.active_id(spine) == "context", cm.active_id(spine)

roots = {
    "skill": os.path.join(checkout, "skills", "commander"),
    "repo": checkout,
    "durable": checkout,
}
manifest = cm.build_manifest(spine, roots)
cm.write_manifest(manifest, out)

print(json.dumps({
    "checkout": checkout,
    "step": manifest["step"],
    "LC_ALL": os.environ.get("LC_ALL"),
    "LANG": os.environ.get("LANG"),
    "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
    "hash_probe": hash("constellation"),
}))
'''


class DeterministicAcrossEnvironments(unittest.TestCase):
    ENVIRONMENTS = (
        {"LC_ALL": "C", "LANG": "C", "PYTHONHASHSEED": "1"},
        {"LC_ALL": "tr_TR.UTF-8", "LANG": "tr_TR.UTF-8", "PYTHONHASHSEED": "4242"},
    )

    @classmethod
    def setUpClass(cls):
        if shutil.which("git") is None:  # pragma: no cover - environment guard
            raise unittest.SkipTest("git is required to add a second checkout")
        cls._tmp = tempfile.mkdtemp(prefix="ctx-determinism-")
        cls._worktrees = []
        try:
            for index in range(len(cls.ENVIRONMENTS)):
                path = Path(cls._tmp) / f"checkout-{index}"
                added = subprocess.run(
                    ["git", "worktree", "add", "--detach", str(path), "HEAD"],
                    cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                )
                if added.returncode != 0:  # pragma: no cover - environment guard
                    raise unittest.SkipTest(f"git worktree add failed: {added.stderr}")
                cls._worktrees.append(path)
                for rel in OVERLAY:
                    shutil.copyfile(ROOT / rel, path / rel)
                for source, target in INSTALL_SHIM:
                    (path / target).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / source, path / target)
        except Exception:
            cls._cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls._cleanup()

    @classmethod
    def _cleanup(cls):
        # Never leave a stray worktree behind, on any exit path.
        for path in getattr(cls, "_worktrees", []):
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(path)],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            )
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
        shutil.rmtree(getattr(cls, "_tmp", ""), ignore_errors=True)

    def setUp(self):
        self.results = []
        script = Path(self._tmp) / "child.py"
        script.write_bytes(CHILD.encode("utf-8"))
        for checkout, mutation in zip(self._worktrees, self.ENVIRONMENTS):
            env = dict(os.environ)
            env.update(mutation)
            env["PYTHONIOENCODING"] = "utf-8"
            out = checkout / "manifest.json"
            done = subprocess.run(
                [sys.executable, str(script), str(checkout), str(out)],
                capture_output=True, text=True, encoding="utf-8", env=env,
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            self.results.append({
                "probe": json.loads(done.stdout),
                "bytes": out.read_bytes(),
                "manifest": json.loads(out.read_text(encoding="utf-8")),
                "mutation": mutation,
            })

    def test_the_two_environments_really_are_distinct(self):
        # Guard against a vacuous pass: identical checkouts would make byte-identity
        # trivially true and prove nothing.
        first, second = (r["probe"]["checkout"] for r in self.results)
        self.assertNotEqual(Path(first).resolve(), Path(second).resolve())

    def test_the_locale_and_hash_seed_mutations_took_effect_inside_the_child(self):
        # The Windows trap, closed by measurement: `env=` is asserted to have
        # actually reached the child, never assumed to have.
        for result in self.results:
            with self.subTest(seed=result["mutation"]["PYTHONHASHSEED"]):
                for key, expected in result["mutation"].items():
                    self.assertEqual(result["probe"][key], expected)
        # PYTHONHASHSEED is only *set* above; this proves it was also *honoured* —
        # str hashing is seed-randomised, so two seeds must give two probes.
        self.assertNotEqual(self.results[0]["probe"]["hash_probe"],
                            self.results[1]["probe"]["hash_probe"])

    def test_content_is_byte_identical_excluding_exactly_the_run_subtree(self):
        first, second = (r["manifest"] for r in self.results)
        self.assertNotEqual(self.results[0]["bytes"], self.results[1]["bytes"],
                            "the whole file must NOT be compared: /run varies by design")
        self.assertEqual(
            cm.encode(cm.content(first)).encode("utf-8"),
            cm.encode(cm.content(second)).encode("utf-8"),
        )
        # And the exclusion really is one pointer: `/run` is the only key removed.
        self.assertEqual(set(first) - set(cm.content(first)), {"run"})
        self.assertEqual(set(second) - set(cm.content(second)), {"run"})

    def test_the_run_subtrees_differ_so_the_exclusion_is_load_bearing(self):
        first, second = (r["manifest"]["run"] for r in self.results)
        self.assertNotEqual(first["roots"], second["roots"])

    def test_the_content_is_a_real_projection_not_an_empty_one(self):
        # A producer that emitted nothing would pass every assertion above.
        manifest = self.results[0]["manifest"]
        self.assertEqual(manifest["step"], "context")
        self.assertGreaterEqual(len(manifest["files"]), 1)
        self.assertTrue(any(row["rev"] for row in manifest["files"]),
                        "at least one declared file must have resolved to a real rev")

    def test_no_absolute_path_leaks_into_the_content(self):
        for result in self.results:
            with self.subTest(checkout=result["probe"]["checkout"]):
                rendered = cm.encode(cm.content(result["manifest"]))
                self.assertNotIn(result["probe"]["checkout"], rendered)
                self.assertNotIn(Path(result["probe"]["checkout"]).as_posix(), rendered)


class RealCheckoutSkew(unittest.TestCase):
    """The untracked-vs-absent case, stated rather than masked.

    A path that is untracked-but-present here and absent in a clean checkout is a
    real difference in what was *delivered*, and the manifest is a delivery record,
    so the two manifests SHOULD disagree on that row's `rev`. What must never
    differ is the record's shape: same step, same rows, same order.
    """

    def test_a_clean_checkout_differs_only_in_rev_never_in_shape(self):
        if shutil.which("git") is None:  # pragma: no cover - environment guard
            raise unittest.SkipTest("git is required to add a second checkout")
        spine = json.loads(
            (ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json")
            .read_text(encoding="utf-8")
        )
        spine["tasks"]["init"]["status"] = "complete"

        def project(base):
            roots = {"skill": Path(base) / "skills" / "commander",
                     "repo": Path(base), "durable": Path(base)}
            manifest = cm.build_manifest(spine, roots)
            # Presence is recorded now, while both trees still exist.
            present = [Path(cm.resolve(entry, roots)).exists()
                       for entry in spine["tasks"]["context"][cm.DECLARATION_KEY]]
            return manifest, present

        here, here_present = project(ROOT)

        tmp = tempfile.mkdtemp(prefix="ctx-skew-")
        checkout = Path(tmp) / "clean"
        try:
            added = subprocess.run(
                ["git", "worktree", "add", "--detach", str(checkout), "HEAD"],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            )
            if added.returncode != 0:  # pragma: no cover - environment guard
                raise unittest.SkipTest(f"git worktree add failed: {added.stderr}")
            for rel in OVERLAY:
                shutil.copyfile(ROOT / rel, checkout / rel)
            there, there_present = project(checkout)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(checkout)],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8")
            shutil.rmtree(tmp, ignore_errors=True)

        # Shape is invariant: same step, same rows, same declaration order.
        self.assertEqual(here["step"], there["step"])
        self.assertEqual([(r["root"], r["path"]) for r in here["files"]],
                         [(r["root"], r["path"]) for r in there["files"]])
        # Any difference is confined to `rev`, and only where the two checkouts
        # genuinely hold different bytes for that path.
        for mine, theirs, mine_here, mine_there in zip(
            here["files"], there["files"], here_present, there_present
        ):
            with self.subTest(path=mine["path"]):
                self.assertEqual(mine["rev"] is not None, mine_here)
                self.assertEqual(theirs["rev"] is not None, mine_there)
                if mine["rev"] == theirs["rev"]:
                    continue
                self.assertNotEqual(
                    mine_here, mine_there,
                    f"{mine['path']}: revs differ although the file is present in "
                    "both checkouts — that is a determinism defect, not delivery skew",
                )


if __name__ == "__main__":
    unittest.main()
