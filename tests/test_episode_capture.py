"""Tests for `scripts/episode_capture.py` — the assembly seam that makes the
context manifest a *byproduct* of starting a spine step.

The point of the seam is that nobody can forget it: `checklist_engine.advance()`
refuses a task that is not `in-progress`, and `start()`/`reopen()` are what put a
task there, so every gate that ever advances has passed the emit.

These tests are deliberately adversarial rather than round-trip. A suite that only
starts a step and finds *a* manifest proves almost nothing here, because the two
failure modes this seam actually has are both **silent**:

* `context_manifest.read_bytes` returns `None` for a missing file and `rows()`
  records `rev: null` without raising — so a wrong root ships a plausible-looking
  manifest with every revision null and every naive assertion green. The root
  tests below therefore assert the **resolved absolute path**, never the code that
  produced it, and one of them resolves a `durable` declaration end to end to prove
  the double-nesting trap is not merely avoided by luck. That declaration is
  synthetic since #308 cut the lessons read path and left the corpus shipping no
  `durable` declaration at all — the trap is a property of `resolve_roots`, not of
  whichever file happens to be declared.
* The emit is fail-soft by design (it must never change a verb's exit code), so a
  broken emit looks exactly like a working one from the caller's side. The
  fail-soft tests therefore pin the exit code *and* the failure stub, because
  "no manifest" and "manifest failed" have to stay tellable apart.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts" / "checklist_engine.py"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ec = load("episode_capture")
cm = load("context_manifest")
awr = load("agent_work_root")


def norm(path):
    """Compare paths the way the filesystem does, not the way strings do."""
    return os.path.normcase(os.path.realpath(str(path)))


def checklist(work_id="wk", items=None, declaration=None, statuses=None):
    """A minimal gated checklist. `declaration` lands on the first item."""
    items = items or ["g1"]
    statuses = statuses or {}
    tasks = {}
    for iid in items:
        tasks[iid] = {
            "id": iid,
            "title": iid,
            "imperative": f"do {iid}",
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "done", "check": None, "satisfied": False}
            ],
            "constraints": [],
            "directives": None,
            "child_checklist": None,
            "status": statuses.get(iid, "pending"),
            "status_detail": {},
            "result": None,
            "finding": None,
            "evidence": [],
            "rework_count": 0,
            "why_exempt": True,
        }
    if declaration is not None:
        tasks[items[0]]["context_refs"] = list(declaration)
    return {
        "work_id": work_id,
        "type": "gated",
        "items": list(items),
        "tasks": tasks,
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
    }


def work_area(tmp, work_id="wk", **kwargs):
    """Lay a checklist out the way a real run does — `<agent-work>/<work-id>/spine.json`
    — and return `(spine_path, checklist)`. The layout is load-bearing: the manifest
    root is the checklist directory's parent, so only this shape puts the manifest
    beside the spine."""
    directory = Path(tmp) / ".agent-work" / work_id
    directory.mkdir(parents=True, exist_ok=True)
    cl = checklist(work_id=work_id, **kwargs)
    spine = directory / "spine.json"
    with open(spine, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(cl, indent=2) + "\n")
    return spine, cl


def engine(spine, *argv):
    """Run the real engine CLI the way an agent does, and return the CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(ENGINE), "--file", str(spine), *argv],
        capture_output=True, text=True, encoding="utf-8",
    )


def git_repo(path):
    for argv in (["init"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(path), *argv], capture_output=True, text=True)


# --------------------------------------------------------------------------- #
# roots
# --------------------------------------------------------------------------- #
class RootResolution(unittest.TestCase):
    """Every assertion here is on a RESOLVED ABSOLUTE PATH, never on the helper
    that produced it. A wrong root does not raise anywhere in the producer — it
    yields `rev: null` rows — so asserting "we called the right function" would
    pass just as happily with the wrong one wired underneath it."""

    def test_roots_are_exactly_the_three_declared_tokens(self):
        roots = ec.resolve_roots(ROOT / ".agent-work")
        self.assertEqual(tuple(roots), cm.ROOT_TOKENS)
        for token, value in roots.items():
            self.assertTrue(os.path.isabs(str(value)), f"{token} is not absolute: {value}")

    def test_roots_skill_is_the_parent_of_the_scripts_directory(self):
        # In an installed skill this is `<skill>/`, where references/global-*.md live.
        roots = ec.resolve_roots(ROOT / ".agent-work")
        self.assertEqual(norm(roots["skill"]), norm(Path(ec.__file__).resolve().parent.parent))

    def test_roots_repo_is_the_worktree_root_where_docs_agents_resolves(self):
        roots = ec.resolve_roots(ROOT / ".agent-work")
        self.assertEqual(norm(roots["repo"]), norm(ROOT))
        # The point of this root, asserted as a resolved path rather than described.
        self.assertTrue((Path(roots["repo"]) / "docs" / "agents").is_dir())

    def test_roots_durable_is_the_checkout_root_not_the_agent_work_directory(self):
        """The silent trap: `durable_agent_work()` returns `<root>/.agent-work`, which
        double-nests any `.agent-work/…`-relative durable declaration to
        `.agent-work/.agent-work/…` — a path that simply does not exist, so the row
        records `rev: null` and every naive check stays green."""
        base = ROOT / ".agent-work"
        roots = ec.resolve_roots(base)
        # Resolved from the repo root — see the sibling test for why the argument,
        # not the helper name, is what makes this correct.
        self.assertEqual(norm(roots["durable"]), norm(awr.durable_root(ROOT)))
        self.assertNotEqual(norm(roots["durable"]), norm(awr.durable_agent_work(ROOT)))
        self.assertNotEqual(
            os.path.basename(str(roots["durable"]).rstrip("/\\")), ".agent-work"
        )

    def test_roots_durable_resolves_a_declaration_without_double_nesting(self):
        """Resolve a `durable`-rooted declaration through the real producer and assert
        the absolute path it lands on.

        The entry is **synthetic**. Until #308 this test resolved the corpus's one
        shipped `durable` declaration (`.agent-work/LESSONS.md` in
        `COMMANDER_SPINE.template.json`); cutting the lessons read path removed it, and
        the corpus now ships none — asserted below, so a re-added one is visible rather
        than silently changing what this test exercises. The subject was never that
        path: it is the double-nesting trap in `resolve_roots`, which any
        `.agent-work/…`-relative durable path exposes."""
        declared = json.loads(
            (ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json")
            .read_text(encoding="utf-8")
        )["tasks"]["context"]["context_refs"]
        self.assertEqual([e for e in declared if e["root"] == "durable"], [])

        entry = {"root": "durable", "path": ".agent-work/synthetic-durable.md",
                 "required": False}
        roots = ec.resolve_roots(ROOT / ".agent-work")
        resolved = cm.resolve(entry, roots)
        self.assertEqual(
            norm(resolved),
            norm(Path(roots["durable"]) / ".agent-work" / "synthetic-durable.md"),
        )
        tail = os.path.normcase(resolved)
        self.assertNotIn(
            os.path.normcase(os.path.join(".agent-work", ".agent-work")), tail,
            f"durable root double-nested: {resolved}",
        )

    def test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory(self):
        """`durable_root(start)` redirects to the main checkout ONLY for a linked
        worktree with no active Admiral epic lease. On every other path — plain
        checkout, active lease, no git — it returns `start` UNCHANGED. So handing it
        the spine's own directory silently makes that directory the durable root, and
        a `.agent-work/…`-relative durable declaration nests under it. This is the
        argument, not the helper, and no assertion about which function was called
        can see it."""
        with tempfile.TemporaryDirectory() as tmp:
            git_repo(tmp)  # plain checkout: durable_root always returns `start`
            spine_dir = Path(tmp) / ".agent-work" / "wk"
            spine_dir.mkdir(parents=True)
            roots = ec.resolve_roots(spine_dir)
            self.assertEqual(norm(roots["durable"]), norm(tmp))
            self.assertEqual(
                norm(cm.resolve(
                    {"root": "durable", "path": ".agent-work/synthetic-durable.md"}, roots)),
                norm(Path(tmp) / ".agent-work" / "synthetic-durable.md"),
            )

    def test_roots_outside_a_git_repository_fall_back_visibly_and_never_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots = ec.resolve_roots(tmp)
            self.assertEqual(norm(roots["repo"]), norm(tmp))
            self.assertEqual(norm(roots["durable"]), norm(tmp))

    def test_roots_from_a_nonexistent_base_never_raise(self):
        roots = ec.resolve_roots(Path(tempfile.gettempdir()) / "no-such-dir-305")
        self.assertEqual(tuple(roots), cm.ROOT_TOKENS)


# --------------------------------------------------------------------------- #
# emit
# --------------------------------------------------------------------------- #
class Emit(unittest.TestCase):
    def test_emit_writes_a_manifest_carrying_a_non_null_rev(self):
        """Guards against the all-null manifest: a wrong root produces a structurally
        valid file whose every `rev` is null, so the shape alone proves nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            git_repo(tmp)
            doctrine = Path(tmp) / "docs" / "agents"
            doctrine.mkdir(parents=True)
            payload = b"# orchestrator context\n"
            with open(doctrine / "ORCHESTRATOR_CONTEXT.md", "wb") as handle:
                handle.write(payload)
            spine, cl = work_area(
                tmp,
                declaration=[
                    {"root": "repo", "path": "docs/agents/ORCHESTRATOR_CONTEXT.md"},
                    {"root": "repo", "path": "docs/agents/ABSENT.md"},
                ],
            )
            written = ec.emit_step_manifest(cl, "g1", spine.parent)
            self.assertIsNotNone(written)
            manifest = json.loads(Path(written).read_text(encoding="utf-8"))
            self.assertEqual(manifest["step"], "g1")
            self.assertEqual(manifest["files"][0]["rev"], cm.rev(payload))
            self.assertIsNone(manifest["files"][1]["rev"])

    def test_emit_lands_beside_the_spine_at_the_manifest_path_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine, cl = work_area(tmp, work_id="issue-305")
            written = ec.emit_step_manifest(cl, "g1", spine.parent)
            self.assertEqual(
                norm(written),
                norm(cm.manifest_path(Path(tmp) / ".agent-work", "issue-305", "g1")),
            )
            self.assertEqual(norm(Path(written).parent.parent), norm(spine.parent))

    def test_emit_never_overwrites_an_already_present_manifest(self):
        """A per-step *delivery snapshot*. If a later call rewrote it, the record
        would silently become "whatever was available at the last call"."""
        with tempfile.TemporaryDirectory() as tmp:
            git_repo(tmp)
            (Path(tmp) / "a.md").write_bytes(b"first\n")
            (Path(tmp) / "b.md").write_bytes(b"second\n")
            spine, cl = work_area(tmp, declaration=[{"root": "repo", "path": "a.md"}])
            written = ec.emit_step_manifest(cl, "g1", spine.parent)
            before = Path(written).read_bytes()

            cl["tasks"]["g1"]["context_refs"] = [{"root": "repo", "path": "b.md"}]
            again = ec.emit_step_manifest(cl, "g1", spine.parent)
            self.assertEqual(norm(again), norm(written))
            self.assertEqual(Path(written).read_bytes(), before)
            reread = json.loads(Path(written).read_text(encoding="utf-8"))
            self.assertEqual([r["path"] for r in reread["files"]], ["a.md"])

    def test_emit_writes_lf_line_endings_on_every_platform(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine, cl = work_area(tmp)
            written = ec.emit_step_manifest(cl, "g1", spine.parent)
            self.assertNotIn(b"\r\n", Path(written).read_bytes())

    def test_emit_records_the_step_the_engine_would_be_activating(self):
        """The step is chosen by the engine's own `active_id()`, so the seam must be
        called AFTER the status mutation — otherwise `reopen` would record the wrong
        step. Pinned with a checklist whose earlier gates are terminal."""
        with tempfile.TemporaryDirectory() as tmp:
            spine, cl = work_area(
                tmp, items=["g1", "g2", "g3"], statuses={"g1": "complete", "g2": "skipped"}
            )
            written = ec.emit_step_manifest(cl, "g3", spine.parent)
            self.assertEqual(json.loads(Path(written).read_text(encoding="utf-8"))["step"], "g3")

    def test_emit_without_a_checklist_directory_writes_nothing_at_all(self):
        """No spine location means no work area; inventing one would write the record
        outside the run it belongs to. Absence here is the correct answer, and it is
        what keeps in-process engine calls from scattering manifests."""
        cl = checklist()
        self.assertIsNone(ec.emit_step_manifest(cl, "g1", None))


# --------------------------------------------------------------------------- #
# seam — through the real engine CLI, the way an agent drives it
# --------------------------------------------------------------------------- #
class Seam(unittest.TestCase):
    def test_seam_start_emits_the_manifest_as_a_byproduct(self):
        with tempfile.TemporaryDirectory() as tmp:
            git_repo(tmp)
            (Path(tmp) / "doctrine.md").write_bytes(b"doctrine\n")
            spine, _ = work_area(tmp, declaration=[{"root": "repo", "path": "doctrine.md"}])
            proc = engine(spine, "start", "g1")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            manifest = cm.manifest_path(Path(tmp) / ".agent-work", "wk", "g1")
            self.assertTrue(manifest.exists(), f"no manifest at {manifest}")
            rows = json.loads(manifest.read_text(encoding="utf-8"))["files"]
            self.assertEqual(rows[0]["rev"], cm.rev(b"doctrine\n"))

    def test_seam_reopen_emits_the_manifest_too(self):
        """`reopen` is the second and only other door to `in-progress`; a seam wired
        to `start` alone would leave reworked gates unrecorded."""
        with tempfile.TemporaryDirectory() as tmp:
            git_repo(tmp)
            (Path(tmp) / "doctrine.md").write_bytes(b"doctrine\n")
            spine, _ = work_area(
                tmp, items=["g1", "g2"], statuses={"g1": "complete"},
                declaration=[{"root": "repo", "path": "doctrine.md"}],
            )
            manifest = cm.manifest_path(Path(tmp) / ".agent-work", "wk", "g1")
            self.assertFalse(manifest.exists())
            proc = engine(spine, "reopen", "g1", "--reason", "rework")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(manifest.exists(), f"no manifest at {manifest}")
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["step"], "g1")

    def test_seam_a_task_declaring_nothing_still_gets_a_manifest(self):
        """An empty `files` list is a real reading: "this step was delivered nothing
        declared". It must not be confused with a step that was never started."""
        with tempfile.TemporaryDirectory() as tmp:
            spine, _ = work_area(tmp)
            self.assertEqual(engine(spine, "start", "g1").returncode, 0)
            manifest = cm.manifest_path(Path(tmp) / ".agent-work", "wk", "g1")
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["files"], [])

    def test_seam_a_refused_start_emits_nothing(self):
        """The manifest records delivery to a step that actually activated. A refused
        verb activated nothing, so a manifest would be a false record."""
        with tempfile.TemporaryDirectory() as tmp:
            spine, _ = work_area(tmp, items=["g1", "g2"])
            proc = engine(spine, "start", "g2")  # not the active gate
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(cm.manifest_path(Path(tmp) / ".agent-work", "wk", "g2").exists())


# --------------------------------------------------------------------------- #
# fail-soft, but never silent
# --------------------------------------------------------------------------- #
class FailSoft(unittest.TestCase):
    """The emit runs inside every `start`, on an engine two other commanders are live
    on. A crash here would break every verb for all of them, so it catches broadly —
    and each case below pins the *exit code*, which is the thing that must not move."""

    def test_failsoft_a_fully_terminal_checklist_does_not_change_any_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine, _ = work_area(tmp, items=["g1"], statuses={"g1": "complete"})
            self.assertEqual(engine(spine, "current").returncode, 0)
            self.assertEqual(engine(spine, "start", "g1").returncode, 1)

    def test_failsoft_an_unmapped_root_token_does_not_change_the_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine, _ = work_area(tmp, declaration=[{"root": "vendor", "path": "x.md"}])
            proc = engine(spine, "start", "g1")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(
                json.loads(spine.read_text(encoding="utf-8"))["tasks"]["g1"]["status"],
                "in-progress",
            )

    def test_failsoft_a_directory_that_is_not_a_git_repo_does_not_change_the_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine, _ = work_area(tmp, declaration=[{"root": "repo", "path": "docs/x.md"}])
            proc = engine(spine, "start", "g1")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            manifest = cm.manifest_path(Path(tmp) / ".agent-work", "wk", "g1")
            self.assertIsNone(json.loads(manifest.read_text(encoding="utf-8"))["files"][0]["rev"])

    def test_failsoft_a_malformed_declaration_does_not_change_the_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine, _ = work_area(tmp, declaration=[{"path": "no-root.md"}])
            self.assertEqual(engine(spine, "start", "g1").returncode, 0)

    def test_stub_records_the_failure_instead_of_leaving_silence(self):
        """A non-reading must be visibly distinct from an uncollected one. "No file"
        means nobody started this step; "a file carrying `emit_error`" means the step
        started and the record could not be taken."""
        with tempfile.TemporaryDirectory() as tmp:
            spine, cl = work_area(tmp, declaration=[{"root": "vendor", "path": "x.md"}])
            written = ec.emit_step_manifest(cl, "g1", spine.parent)
            stub = json.loads(Path(written).read_text(encoding="utf-8"))
            self.assertEqual(stub["step"], "g1")
            self.assertIn("emit_error", stub)
            self.assertEqual(stub["emit_error"]["error"], "DeclarationError")
            self.assertIn("vendor", stub["emit_error"]["message"])
            # `files: null` is not `files: []` — a failed reading is not an empty one.
            self.assertIsNone(stub["files"])

    def test_stub_is_distinguishable_from_a_real_manifest_by_a_later_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            good_spine, good = work_area(tmp, work_id="ok")
            bad_spine, bad = work_area(
                tmp, work_id="bad", declaration=[{"root": "vendor", "path": "x.md"}]
            )
            ok = json.loads(
                Path(ec.emit_step_manifest(good, "g1", good_spine.parent)).read_text(encoding="utf-8")
            )
            broken = json.loads(
                Path(ec.emit_step_manifest(bad, "g1", bad_spine.parent)).read_text(encoding="utf-8")
            )
            self.assertNotIn("emit_error", ok)
            self.assertIn("emit_error", broken)

    def test_stub_does_not_overwrite_a_manifest_that_was_already_taken(self):
        with tempfile.TemporaryDirectory() as tmp:
            git_repo(tmp)
            (Path(tmp) / "a.md").write_bytes(b"first\n")
            spine, cl = work_area(tmp, declaration=[{"root": "repo", "path": "a.md"}])
            written = ec.emit_step_manifest(cl, "g1", spine.parent)
            before = Path(written).read_bytes()
            cl["tasks"]["g1"]["context_refs"] = [{"root": "vendor", "path": "x.md"}]
            ec.emit_step_manifest(cl, "g1", spine.parent)
            self.assertEqual(Path(written).read_bytes(), before)

    def test_failsoft_an_arbitrary_producer_crash_leaves_a_stub_not_silence(self):
        """Broad-except is the deliberate choice here, so prove it against something
        other than the errors the producer is known to raise — and prove it is
        fail-SOFT without being fail-SILENT.

        Writing nothing is the easy swallow and the wrong one. A vanished manifest
        is indistinguishable from a step nobody ever started, and those are
        different facts about the run. So the crash path must still leave the
        reading it failed to take: a stub carrying the exception type."""
        with tempfile.TemporaryDirectory() as tmp:
            spine, cl = work_area(tmp)
            # Not one of the producer's deliberate raises — `active_id` will index a
            # string, which nothing in `context_manifest` anticipates.
            cl["tasks"] = "not a mapping"
            written = ec.emit_step_manifest(cl, "g1", spine.parent)
            self.assertIsNotNone(written, "a swallowed crash wrote nothing at all")
            self.assertTrue(Path(written).exists(), f"no stub at {written}")
            stub = json.loads(Path(written).read_text(encoding="utf-8"))
            self.assertEqual(stub["step"], "g1")
            self.assertEqual(stub["emit_error"]["error"], "TypeError")
            self.assertTrue(stub["emit_error"]["message"])
            self.assertIsNone(stub["files"])

    def test_stub_files_null_is_not_the_same_reading_as_empty_files(self):
        """`files: []` and `files: null` are the two readings that must never
        collide. `[]` is a *complete* reading — "this step declared no context
        refs". `null` is the *absence* of a reading — "the record could not be
        taken". A consumer that conflated them would report a step as having been
        delivered nothing when in truth nothing is known about what it was
        delivered.

        Both sides are produced from real emits and both are read, so this cannot
        pass on an empty-vs-empty or missing-vs-missing coincidence — and the last
        three assertions pin the trap directly: BOTH values are falsy, so any
        consumer discriminating on truthiness loses the distinction. Only
        `is None` separates them."""
        with tempfile.TemporaryDirectory() as tmp:
            empty_spine, declares_nothing = work_area(tmp, work_id="declares-nothing")
            broken_spine, cannot_read = work_area(
                tmp, work_id="cannot-read",
                declaration=[{"root": "vendor", "path": "x.md"}],
            )
            real = json.loads(
                Path(ec.emit_step_manifest(declares_nothing, "g1", empty_spine.parent))
                .read_text(encoding="utf-8")
            )
            stub = json.loads(
                Path(ec.emit_step_manifest(cannot_read, "g1", broken_spine.parent))
                .read_text(encoding="utf-8")
            )

            # Both files were really written and really read — the distinction
            # below is between two present readings, not between one and a gap.
            self.assertEqual(real["step"], "g1")
            self.assertEqual(stub["step"], "g1")

            self.assertEqual(real["files"], [])           # read it, found nothing declared
            self.assertNotIn("emit_error", real)
            self.assertIsNone(stub["files"])              # could not read it at all
            self.assertIn("emit_error", stub)

            # The trap, pinned: both are falsy, and they are still not the same.
            self.assertFalse(bool(real["files"]))
            self.assertFalse(bool(stub["files"]))
            self.assertNotEqual(real["files"], stub["files"])
            self.assertIsNot(real["files"], None)


# --------------------------------------------------------------------------- #
# the seam's own premise
# --------------------------------------------------------------------------- #
class SeamPremise(unittest.TestCase):
    """The gate rests on a claim about the engine's status machine, not on agent
    discipline. If that claim ever stops holding, these fail rather than the seam
    quietly becoming skippable."""

    def test_seam_advance_refuses_a_task_that_was_never_started(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine, _ = work_area(tmp)
            proc = engine(spine, "advance", "g1")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("must be in-progress", proc.stderr)

    def test_seam_only_start_and_reopen_assign_the_in_progress_status(self):
        source = (ROOT / "scripts" / "checklist_engine.py").read_text(encoding="utf-8")
        assigns = [
            n for n, line in enumerate(source.splitlines(), 1)
            if line.strip() == 't["status"] = "in-progress"'
        ]
        self.assertEqual(len(assigns), 2, f"literal in-progress assignments at {assigns}")


if __name__ == "__main__":
    unittest.main()
