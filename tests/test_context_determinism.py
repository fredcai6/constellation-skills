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
#:
#: It writes **two** artifacts, and the second one is the load-bearing one. The
#: manifest is written whole; then `content_out` is written as
#: `encode(content(manifest))` **using this child's own encoder, in this child's own
#: environment**. The parent byte-compares those two files verbatim and never
#: re-encodes anything itself. That distinction is the whole acceptance criterion:
#: if the parent parsed both artifacts and re-encoded them, any environment
#: dependence in serialisation would be normalised away by the parent's own encoder
#: before the comparison ever happened, and the test would report green on two
#: children that had written materially different bytes.
#:
#: `argv[4]` overrides which producer module is loaded. Real runs leave it at the
#: checkout's own; `TheComparisonHasTeeth` points it at a deliberately
#: environment-dependent copy to prove this comparison can fail.
CHILD = r'''
import importlib.util, json, os, sys
checkout = sys.argv[1]
out = sys.argv[2]
content_out = sys.argv[3]
producer = sys.argv[4] if len(sys.argv) > 4 else os.path.join(
    checkout, "scripts", "context_manifest.py")
spec = importlib.util.spec_from_file_location("context_manifest", producer)
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
# The comparison surface: the content subtree, encoded HERE, by this environment.
cm.write_manifest(cm.content(manifest), content_out)

print(json.dumps({
    "checkout": checkout,
    "cwd": os.getcwd(),
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
            content_out = checkout / "content.json"
            done = subprocess.run(
                [sys.executable, str(script), str(checkout), str(out), str(content_out)],
                # Each child runs from its OWN checkout. Without this both children
                # inherit the pytest process's cwd, and cwd is the one
                # environment fact `run_facts()` reads — held constant, a cwd leak
                # out of `/run` and into the content would be invisible here.
                cwd=str(checkout),
                capture_output=True, text=True, encoding="utf-8", env=env,
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            self.results.append({
                "probe": json.loads(done.stdout),
                "bytes": out.read_bytes(),
                # The bytes THIS child wrote for the content subtree. Never
                # re-encoded by the parent — that is the point of the artifact.
                "content_bytes": content_out.read_bytes(),
                "manifest": json.loads(out.read_text(encoding="utf-8")),
                "mutation": mutation,
            })

    def test_the_two_environments_really_are_distinct(self):
        # Guard against a vacuous pass: identical checkouts would make byte-identity
        # trivially true and prove nothing.
        first, second = (r["probe"]["checkout"] for r in self.results)
        self.assertNotEqual(Path(first).resolve(), Path(second).resolve())
        # And they really ran from different working directories, so cwd — the one
        # environment fact `run_facts()` reads — is a live variable here, not a
        # constant that would hide a leak out of `/run`.
        cwds = [Path(r["probe"]["cwd"]).resolve() for r in self.results]
        self.assertNotEqual(cwds[0], cwds[1])

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
        self.assertNotEqual(self.results[0]["bytes"], self.results[1]["bytes"],
                            "the whole file must NOT be compared: /run varies by design")
        # THE acceptance assertion. Both operands are bytes a child wrote, with its
        # own encoder, in its own environment. Nothing is re-encoded here — a parent
        # re-encode would launder away exactly the class of defect this test exists
        # to catch (see CHILD's comment, and TheComparisonHasTeeth below).
        self.assertEqual(self.results[0]["content_bytes"],
                         self.results[1]["content_bytes"])

        # The exclusion really is one pointer, in BOTH directions: nothing was
        # dropped besides `/run`, and nothing was added. A one-directional
        # `set(m) - set(content(m)) == {"run"}` is blind to an added key.
        for result in self.results:
            with self.subTest(checkout=result["probe"]["checkout"]):
                manifest = result["manifest"]
                self.assertEqual(set(manifest), set(cm.content(manifest)) | {"run"})
                self.assertNotIn("run", cm.content(manifest))

    def test_the_compared_bytes_are_the_ones_the_children_wrote(self):
        # Parsing for diagnostics is fine; the assertion above must be over the
        # child's own bytes. This pins that they are in fact a faithful encoding of
        # the content subtree, so the comparison is not comparing two empty files.
        for result in self.results:
            with self.subTest(checkout=result["probe"]["checkout"]):
                parsed = json.loads(result["content_bytes"].decode("utf-8"))
                self.assertEqual(parsed, cm.content(result["manifest"]))
                self.assertTrue(result["content_bytes"].endswith(b"\n"))
                self.assertNotIn(b"\r\n", result["content_bytes"])

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
                # Read from the child's own bytes, not a parent re-render.
                rendered = result["content_bytes"].decode("utf-8")
                for varying in (result["probe"]["checkout"], result["probe"]["cwd"]):
                    self.assertNotIn(varying, rendered)
                    self.assertNotIn(Path(varying).as_posix(), rendered)


#: Deliberately defective producers: the real module plus one appended definition
#: that shadows a canonical one. Both are real defect shapes that a cold review
#: demonstrated this acceptance test used to report **green** on, and each is the
#: minimal expression of one of the two guarantees the test claims to keep.
#:
#: They are appended as source rather than monkey-patched in-process because the
#: defect only exists across a process and environment boundary — that is precisely
#: where the old comparison was blind.
POISONS = {
    # Different bytes per environment, still valid JSON parsing to the same object.
    # A parent that parses both artifacts and re-encodes them cannot see this.
    "environment_dependent_encoder": '''

def encode(obj):  # noqa: F811 - deliberately shadows the canonical encoder
    _indent = 4 if os.environ.get("LC_ALL") == "tr_TR.UTF-8" else 2
    return json.dumps(obj, indent=_indent, ensure_ascii=False) + "\\n"
''',
    # An environment-varying fact promoted out of `/run` and into the content.
    # `cwd` is the one such fact `run_facts()` already reads.
    "varying_field_outside_run": '''

def content(manifest):  # noqa: F811 - deliberately shadows the canonical filter
    out = {k: v for k, v in manifest.items() if k != "run"}
    out["host_cwd"] = manifest.get("run", {}).get("host", {}).get("cwd")
    return out
''',
}


class TheComparisonHasTeeth(unittest.TestCase):
    """The acceptance test above, turned on itself.

    A determinism test that cannot fail is worse than none, because it reads as
    coverage. This class runs the *same* two-child harness against deliberately
    defective producers and asserts the comparison **does** separate them — and,
    as a control, that the real producer still comes out byte-identical through
    the identical path, so a difference here means the defect and not the harness.
    """

    def _producer(self, tmp, poison):
        """A copy of the real producer under `tmp`, optionally poisoned."""
        stage = Path(tmp) / "scripts"
        stage.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "scripts" / "checklist_engine.py", stage / "checklist_engine.py")
        source = (ROOT / "scripts" / "context_manifest.py").read_text(encoding="utf-8")
        target = stage / "context_manifest.py"
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(source + (POISONS[poison] if poison else ""))
        return target

    def content_bytes_from_two_environments(self, poison=None):
        tmp = tempfile.mkdtemp(prefix="ctx-teeth-")
        try:
            producer = self._producer(tmp, poison)
            script = Path(tmp) / "child.py"
            script.write_bytes(CHILD.encode("utf-8"))
            written = []
            for index, mutation in enumerate(DeterministicAcrossEnvironments.ENVIRONMENTS):
                env = dict(os.environ)
                env.update(mutation)
                env["PYTHONIOENCODING"] = "utf-8"
                work = Path(tmp) / f"run-{index}"
                work.mkdir()
                out, content_out = work / "manifest.json", work / "content.json"
                done = subprocess.run(
                    [sys.executable, str(script), str(ROOT), str(out),
                     str(content_out), str(producer)],
                    cwd=str(work), capture_output=True, text=True,
                    encoding="utf-8", env=env,
                )
                self.assertEqual(done.returncode, 0, done.stderr)
                written.append(content_out.read_bytes())
            return written
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_real_producer_is_byte_identical_through_this_harness(self):
        first, second = self.content_bytes_from_two_environments()
        self.assertEqual(first, second)
        self.assertGreater(len(first), 0)

    def test_an_environment_dependent_encoder_is_caught(self):
        first, second = self.content_bytes_from_two_environments(
            "environment_dependent_encoder")
        # Same object, different bytes. This is the exact shape a parent-side
        # re-encode launders away.
        self.assertEqual(json.loads(first.decode("utf-8")),
                         json.loads(second.decode("utf-8")))
        self.assertNotEqual(first, second)

    def test_a_varying_field_placed_outside_run_is_caught(self):
        first, second = self.content_bytes_from_two_environments(
            "varying_field_outside_run")
        self.assertNotEqual(first, second)
        # And it is caught for the right reason: the leaked key is present and
        # holds two different values.
        self.assertNotEqual(json.loads(first.decode("utf-8"))["host_cwd"],
                            json.loads(second.decode("utf-8"))["host_cwd"])


class RealCheckoutSkew(unittest.TestCase):
    """The untracked-vs-absent case, stated rather than masked.

    A path that is untracked-but-present here and absent in a clean checkout is a
    real difference in what was *delivered*, and the manifest is a delivery record,
    so the two manifests SHOULD disagree on that row's `rev`. What must never
    differ is the record's shape: same step, same rows, same order.

    **The skew is materialised, not hoped for.** An earlier version of this class
    projected the shipped Commander declaration, whose every path is legitimately
    absent from a skill-source tree — so all six rows were `rev: None` on both
    sides, the "revs differ" branch never executed, and the class could not fail.
    The declaration below therefore names real **tracked** files (identical in both
    trees, so their revs must AGREE — the determinism half) alongside one file this
    test creates untracked in the working tree only (so its rev must DIFFER — the
    skew half). Both halves are asserted to have actually occurred.
    """

    #: Created untracked in the working tree for the duration of the test. Absent
    #: from any clean checkout of HEAD by construction — that IS the skew.
    PROBE = "untracked-skew-probe.md"

    #: Tracked and unmodified in this worktree, so byte-identical in a clean
    #: checkout of the same commit. `skill` resolves to `skills/commander`.
    TRACKED = (
        {"root": "repo", "path": "scripts/agent_work_root.py", "required": True},
        {"root": "skill", "path": "templates/COMMANDER_SPINE.template.json",
         "required": True},
    )

    def declaration(self):
        return [
            *self.TRACKED,
            {"root": "repo", "path": self.PROBE, "required": False},
            {"root": "repo", "path": "docs/absent-from-both-checkouts.md",
             "required": False},
        ]

    def test_a_clean_checkout_differs_only_in_rev_never_in_shape(self):
        if shutil.which("git") is None:  # pragma: no cover - environment guard
            raise unittest.SkipTest("git is required to add a second checkout")

        declaration = self.declaration()
        checklist = {
            "work_id": "skew", "type": "gated", "items": ["context"],
            "tasks": {"context": {"id": "context", "title": "context",
                                  "imperative": "…", "status": "pending",
                                  cm.DECLARATION_KEY: declaration}},
        }

        probe = ROOT / self.PROBE
        self.addCleanup(lambda: probe.unlink(missing_ok=True))
        with open(probe, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("untracked in this working tree only\n")

        def project(base):
            roots = {"skill": Path(base) / "skills" / "commander",
                     "repo": Path(base), "durable": Path(base)}
            manifest = cm.build_manifest(checklist, roots)
            # Presence is recorded now, while both trees still exist.
            present = [Path(cm.resolve(entry, roots)).exists() for entry in declaration]
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

        # The premise, established rather than assumed: the probe really was present
        # on one side and absent on the other, and the tracked files really resolved.
        self.assertEqual(here_present, [True, True, True, False])
        self.assertEqual(there_present, [True, True, False, False])

        # Shape is invariant: same step, same rows, same declaration order.
        self.assertEqual(here["step"], there["step"])
        self.assertEqual([(r["root"], r["path"]) for r in here["files"]],
                         [(r["root"], r["path"]) for r in there["files"]])

        # The determinism half: identical tracked bytes give identical revs across
        # two independent checkouts at two different absolute paths.
        for index in range(len(self.TRACKED)):
            with self.subTest(path=here["files"][index]["path"]):
                self.assertIsNotNone(here["files"][index]["rev"])
                self.assertEqual(here["files"][index]["rev"],
                                 there["files"][index]["rev"])

        # The skew half: the untracked probe differs, and differs in exactly the way
        # a delivery record should — present here, absent there.
        probe_here, probe_there = here["files"][-2], there["files"][-2]
        self.assertEqual(probe_here["path"], self.PROBE)
        self.assertIsNotNone(probe_here["rev"])
        self.assertIsNone(probe_there["rev"])
        self.assertNotEqual(probe_here["rev"], probe_there["rev"])

        # Absent on both sides is not skew, and must not masquerade as it.
        self.assertIsNone(here["files"][-1]["rev"])
        self.assertIsNone(there["files"][-1]["rev"])

        # Nothing else moved: every remaining difference is confined to `rev`, and
        # only where the two checkouts genuinely hold different bytes.
        differed = 0
        for mine, theirs, mine_here, mine_there in zip(
            here["files"], there["files"], here_present, there_present
        ):
            with self.subTest(path=mine["path"]):
                self.assertEqual(mine["rev"] is not None, mine_here)
                self.assertEqual(theirs["rev"] is not None, mine_there)
                if mine["rev"] == theirs["rev"]:
                    continue
                differed += 1
                self.assertNotEqual(
                    mine_here, mine_there,
                    f"{mine['path']}: revs differ although the file is present in "
                    "both checkouts — that is a determinism defect, not delivery skew",
                )
        # The headline assertion above ran. Without this the whole loop can be
        # vacuous and still report green.
        self.assertEqual(differed, 1)

    def test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content(self):
        """Regression, review BLOCKER-1 (#300 g5 rework 1).

        Reproduces the reviewer's own construction: two FRESH worktrees at the
        SAME commit, nothing overlaid. One stays genuinely clean; the other gets a
        one-line edit to `docs/CHECKLIST_SCHEMA.md` -- a file NO declaration
        names (the reviewer's own choice of undeclared file). The declaration
        below names only `TRACKED` paths, so declared canon is byte-identical on
        both sides; the only variable is dirt the declaration never sees.

        FAILS before the split fix: `repo_rev` carried `dirty` inside content, so
        `content()` differed between the two checkouts even though every declared
        byte was identical. PASSES after: `dirty` moved to `/run`, so identical
        canon means identical content regardless of undeclared dirt.

        Deliberately does NOT assert which subtree `dirty` lives in -- only that
        `content()` agrees -- so this exact test body produces both the red
        transcript (run against the pre-fix shape) and the green one (run after)
        without being edited in between.

        No `unittest.SkipTest` environment guard here (unlike its siblings above
        in this file) per this round's explicit "introduce no skipTest"
        constraint: if git is somehow absent, `git worktree add` fails loudly
        below via the ordinary assertion on its return code instead.
        """
        declaration = list(self.TRACKED)
        checklist = {
            "work_id": "skew-dirt", "type": "gated", "items": ["context"],
            "tasks": {"context": {"id": "context", "title": "context",
                                  "imperative": "…", "status": "pending",
                                  cm.DECLARATION_KEY: declaration}},
        }

        def project(base):
            roots = {"skill": Path(base) / "skills" / "commander",
                     "repo": Path(base), "durable": Path(base)}
            return cm.build_manifest(checklist, roots)

        tmp = tempfile.mkdtemp(prefix="ctx-dirt-skew-")
        clean = Path(tmp) / "clean"
        dirty = Path(tmp) / "dirty"
        try:
            for path in (clean, dirty):
                added = subprocess.run(
                    ["git", "worktree", "add", "--detach", str(path), "HEAD"],
                    cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                )
                self.assertEqual(added.returncode, 0, added.stderr)

            # The dirt: an edit to a file NO declaration names -- not in TRACKED,
            # not an overlay of the change under test, just an ordinary undeclared
            # tracked file, modified in only one of the two checkouts.
            undeclared = dirty / "docs" / "CHECKLIST_SCHEMA.md"
            with open(undeclared, "a", encoding="utf-8", newline="\n") as handle:
                handle.write("\n<!-- regression probe: undeclared edit, #300 g5 rework 1 -->\n")

            clean_status = subprocess.run(
                ["git", "status", "--porcelain"], cwd=clean,
                capture_output=True, text=True, encoding="utf-8",
            )
            dirty_status = subprocess.run(
                ["git", "status", "--porcelain"], cwd=dirty,
                capture_output=True, text=True, encoding="utf-8",
            )
            # The premise, established rather than assumed: one side really is
            # clean, the other really is dirty, on a file no declaration names.
            self.assertEqual(clean_status.stdout.strip(), "")
            self.assertNotEqual(dirty_status.stdout.strip(), "")

            m_clean = project(clean)
            m_dirty = project(dirty)

            # Declared canon really is identical -- the only variable is dirt on
            # a file the declaration never names.
            self.assertEqual(
                [(r["root"], r["path"], r["rev"]) for r in m_clean["files"]],
                [(r["root"], r["path"], r["rev"]) for r in m_dirty["files"]],
            )
            self.assertEqual(m_clean["repo_rev"]["commit"], m_dirty["repo_rev"]["commit"])

            # THE regression assertion: identical canon must mean identical
            # content, regardless of which side happens to be dirty on a file
            # nothing declares.
            self.assertEqual(cm.content(m_clean), cm.content(m_dirty))
        finally:
            for path in (clean, dirty):
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(path)],
                    cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                )
            subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8")
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
