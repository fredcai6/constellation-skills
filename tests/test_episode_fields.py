"""Tests for the MECHANICAL FIELD COMPOSER — `episode_capture.mechanical_fields()`
and the snapshot it emits at the g1 seam (#305 gate g2).

**Why these tests are shaped the way they are.** The composer's output is handed to
`apply_episode_delta.validate_delta()`, and it is tempting to treat that validator as
the oracle. It is not one. `_validate_create` is `isinstance(str) and value.strip()`
for the scalars and `isinstance(int) and >= 0` for the counters — so a composer that
reads no engine state at all and returns nine plausible constants passes it cleanly,
and so does a "red proof" that deletes one key, because deleting a key from a dict is
independent of how the dict was filled. `validate_delta()` is a shape check on the way
to the writer.

So every field here is proven by **tracking**, not by presence: each test constructs a
run whose true value is NON-DEFAULT — a work id nothing would guess, an active step
that is not the first item, a real `rework_count`, a real engine `reopen`, a real
failing command check, a real refusal — and asserts the composer follows it. A constant
cannot pass two of these at once, which is the property presence checks lack.

The `project` tests carry an extra obligation, spelled out because it is the exact way
the defect they cover was nearly shipped. `project` must be stable for a repository
across every worktree and every epic, and the natural-looking source (`durable_root()`)
returns the *worktree unchanged* whenever an active Admiral epic lease exists — which is
the condition every commander in an epic runs under. A test that exercises only a plain
checkout **passes on the broken formula**. `ProjectFieldTests` therefore builds a real
linked worktree under a real active epic lease, asserts the wrong-formula condition is
genuinely reproduced (`durable_root(linked) == linked`), and only then asserts the
composer still yields the MAIN checkout's name.
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
ENGINE = ROOT / "scripts" / "checklist_engine.py"

GIT = shutil.which("git")


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ec = load("episode_capture")
awr = load("agent_work_root")


def norm(path):
    """Compare paths the way the filesystem does, not the way strings do."""
    return os.path.normcase(os.path.realpath(str(path)))


def git(cwd, *args):
    subprocess.run(
        ["git", *args], cwd=str(cwd), check=True,
        capture_output=True, text=True, encoding="utf-8",
    )


def init_repo(path: Path) -> None:
    """A git repo with one commit, so `git worktree add` has a valid HEAD."""
    git(path, "init", "-q")
    (path / "seed.txt").write_text("seed\n", encoding="utf-8", newline="\n")
    git(path, "add", "seed.txt")
    git(path, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")


def write_epic_lease(main: Path, epic: str = "epic-298") -> Path:
    """An ACTIVE Admiral epic lease in the MAIN checkout — the exact condition under
    which `durable_root()` stops redirecting and honors the worktree instead."""
    d = main / ".agent-work" / epic
    d.mkdir(parents=True, exist_ok=True)
    spine = d / "spine.json"
    spine.write_text(
        json.dumps({
            "work_id": epic,
            "type": "gated",
            "engine_session": {"status": "active", "claimed_by": "admiral"},
        }),
        encoding="utf-8", newline="\n",
    )
    return spine


@unittest.skipUnless(GIT, "git not available on PATH")
class ProjectFieldTests(unittest.TestCase):
    """`project` must name the REPOSITORY, identically from every worktree.

    It is sourced from repository topology (`git rev-parse --git-common-dir`), never
    from the work-area helper, because those answer different questions: topology vs
    writability. Under an epic lease the writability answer is the worktree, which is
    the wrong answer for this field.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.main = Path(self.tmp.name) / "constellation-main"
        self.main.mkdir()
        init_repo(self.main)

    def tearDown(self):
        self.tmp.cleanup()

    def test_plain_checkout_yields_the_checkout_name(self):
        # `--git-common-dir` is RELATIVE (".git") in a plain checkout, so this also
        # pins that the composer resolves it against base_dir rather than cwd.
        self.assertEqual(ec.project_name(self.main), "constellation-main")

    def test_linked_worktree_under_an_active_epic_lease_still_names_the_repository(self):
        linked = Path(self.tmp.name) / "wt" / "e298-305"
        linked.parent.mkdir(parents=True, exist_ok=True)
        git(self.main, "worktree", "add", "-q", "-b", "epic-298/305", str(linked))
        write_epic_lease(self.main)

        # The fixture must genuinely reproduce the condition that broke the old
        # formula, or this test is theatre: under an active epic lease durable_root()
        # honors the WORKTREE, so `Path(durable_root(...)).name` would be 'e298-305'.
        self.assertEqual(norm(awr.durable_root(linked)), norm(linked))

        self.assertEqual(ec.project_name(linked), "constellation-main")
        self.assertNotEqual(ec.project_name(linked), linked.name)

    def test_linked_worktree_agrees_with_the_main_checkout(self):
        """The join this field exists for: the same repository, two worktrees, one
        value — including after the worktree is deleted."""
        linked = Path(self.tmp.name) / "wt" / "e298-999"
        linked.parent.mkdir(parents=True, exist_ok=True)
        git(self.main, "worktree", "add", "-q", "-b", "epic-298/999", str(linked))
        write_epic_lease(self.main)
        self.assertEqual(ec.project_name(linked), ec.project_name(self.main))

    def test_non_repository_refuses_rather_than_guessing(self):
        """Refuse, never fabricate. A worktree-derived (or cwd-derived) fallback would
        silently poison the one join meant to survive worktree deletion, and a wrong
        mechanical fact is worse than an absent one."""
        outside = Path(self.tmp.name) / "not-a-repo"
        outside.mkdir()
        self.assertIsNone(ec.project_name(outside))


def checklist(work_id="wk-042", items=None, statuses=None, claimed_by=None,
              rework=None, evidence=None, checks=None):
    """A gated checklist with deliberately NON-DEFAULT values, so a composer that
    returns constants cannot accidentally match."""
    items = items or ["s1", "s2", "s3"]
    statuses = statuses or {}
    rework = rework or {}
    evidence = evidence or {}
    checks = checks or {}
    tasks = {}
    for iid in items:
        tasks[iid] = {
            "id": iid,
            "title": iid,
            "imperative": f"do {iid}",
            "preconditions": [],
            "postconditions": [
                {"id": "c1", "statement": "done",
                 "check": checks.get(iid), "satisfied": False}
            ],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": statuses.get(iid, "pending"), "status_detail": {},
            "result": None, "finding": None,
            "evidence": evidence.get(iid, []),
            "rework_count": rework.get(iid, 0),
        }
    cl = {"work_id": work_id, "type": "gated", "items": items, "tasks": tasks,
          "consolidation": None, "triage_candidates": [], "blockers": []}
    if claimed_by is not None:
        cl["engine_session"] = {
            "session_id": "sess-xyz", "status": "active", "claimed_by": claimed_by,
            "last_heartbeat": "2026-08-02T00:00:00+00:00",
        }
    return cl


class ComposerCoreTests(unittest.TestCase):
    """Every field is proven by TRACKING a non-default value, never by presence.

    Presence is what `validate_delta()` checks, and nine constants satisfy it. These
    tests are the oracle it is not: each asserts the composer followed engine state
    that a constant could not have guessed.
    """

    def test_run_tracks_the_checklists_own_work_id(self):
        fields = ec.mechanical_fields(checklist(work_id="issue-305-g2"), base_dir=ROOT)
        self.assertEqual(fields["run"], "issue-305-g2")
        # A second, different run through the SAME composer — one constant cannot
        # satisfy both, which is the property a presence check cannot express.
        other = ec.mechanical_fields(checklist(work_id="governor-268"), base_dir=ROOT)
        self.assertEqual(other["run"], "governor-268")

    def test_role_tracks_the_leases_claimed_by(self):
        fields = ec.mechanical_fields(checklist(claimed_by="cartographer"), base_dir=ROOT)
        self.assertEqual(fields["role"], "cartographer")
        other = ec.mechanical_fields(checklist(claimed_by="reviewer"), base_dir=ROOT)
        self.assertEqual(other["role"], "reviewer")

    def test_role_is_refused_when_no_lease_was_ever_claimed(self):
        """Refuse, never fabricate: a lease-less run has no role to report, and
        'implementer' is exactly the plausible constant this rule exists to forbid."""
        self.assertNotIn("role", ec.mechanical_fields(checklist(), base_dir=ROOT))

    def test_spine_step_tracks_the_engines_own_selector_not_the_first_item(self):
        """The active step is the first NON-TERMINAL item. A composer that returned
        `items[0]`, or any constant, gets this wrong the moment a run is underway."""
        cl = checklist(statuses={"s1": "complete", "s2": "in-progress"})
        self.assertEqual(ec.mechanical_fields(cl, base_dir=ROOT)["spine-step"], "s2")
        cl2 = checklist(statuses={"s1": "complete", "s2": "complete"})
        self.assertEqual(ec.mechanical_fields(cl2, base_dir=ROOT)["spine-step"], "s3")

    def test_spine_step_agrees_with_the_imported_selector_it_must_not_re_derive(self):
        engine = load("checklist_engine")
        cl = checklist(statuses={"s1": "skipped", "s2": "complete"})
        self.assertEqual(
            ec.mechanical_fields(cl, base_dir=ROOT)["spine-step"], engine.active_id(cl)
        )

    def test_a_fully_terminal_checklist_refuses_rather_than_naming_a_step(self):
        cl = checklist(statuses={"s1": "complete", "s2": "complete", "s3": "complete"})
        fields = ec.mechanical_fields(cl, base_dir=ROOT)
        self.assertNotIn("spine-step", fields)
        # ...and the fields that are SCOPED to a step go with it, rather than being
        # silently reported against some other step.
        self.assertNotIn("rework-count", fields)

    def test_rework_count_tracks_the_active_steps_own_counter(self):
        cl = checklist(statuses={"s1": "complete"}, rework={"s1": 9, "s2": 3})
        fields = ec.mechanical_fields(cl, base_dir=ROOT)
        self.assertEqual(fields["spine-step"], "s2")
        # 3, not 9 and not 0: scoped to the ACTIVE step, and a constant 0 fails here.
        self.assertEqual(fields["rework-count"], 3)

    @unittest.skipUnless(GIT, "git not available on PATH")
    def test_artifact_ref_tracks_the_real_staged_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            (repo / "docs").mkdir()
            (repo / "docs" / "TRACKED.md").write_text("x\n", encoding="utf-8", newline="\n")
            git(repo, "add", "docs/TRACKED.md")
            fields = ec.mechanical_fields(checklist(), base_dir=repo)
            self.assertEqual(fields["artifact-ref"], ["docs/TRACKED.md"])
            # Stage a second file: the value MOVES. A constant cannot do that.
            (repo / "second.txt").write_text("y\n", encoding="utf-8", newline="\n")
            git(repo, "add", "second.txt")
            self.assertEqual(
                sorted(ec.mechanical_fields(checklist(), base_dir=repo)["artifact-ref"]),
                ["docs/TRACKED.md", "second.txt"],
            )

    def test_project_is_refused_rather_than_defaulted_outside_a_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertNotIn("project", ec.mechanical_fields(checklist(), base_dir=tmp))


class LiveSpine:
    """A real spine on disk, driven through the engine's own CLI.

    These fields are read out of state the engine WROTE — a journal line, an evidence
    item, a manifest's bytes — so exercising them through the Python API would prove
    the wrong thing. Every mutation below goes through `checklist_engine.py` as a
    subprocess, exactly as an agent drives it.
    """

    SESSION = "sess-live"

    def __init__(self, root: Path, work_id="wk-live", items=("s1", "s2"), checks=None,
                 in_repo=False):
        if in_repo:
            # A real repository, so `project` and `artifact-ref` have something to
            # read. Outside one they are legitimately refused, which is the right
            # behavior but cannot demonstrate a FULL group.
            root.mkdir(parents=True, exist_ok=True)
            init_repo(root)
        self.dir = root / work_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "spine.json"
        checks = checks or {}
        tasks = {}
        for iid in items:
            tasks[iid] = {
                "id": iid, "title": iid, "imperative": f"do {iid}",
                "preconditions": [],
                "postconditions": [{"id": "c1", "statement": "done",
                                    "check": checks.get(iid), "satisfied": False}],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            }
        self.path.write_text(
            json.dumps({"work_id": work_id, "type": "gated", "items": list(items),
                        "tasks": tasks, "consolidation": None,
                        "triage_candidates": [], "blockers": []}, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
        self.run("claim", "--session-id", self.SESSION, "--claimed-by", "implementer")

    def run(self, *args):
        return subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(self.path), *args],
            capture_output=True, text=True, encoding="utf-8",
        )

    def verb(self, *args):
        return self.run(*args, "--session-id", self.SESSION)

    def complete(self, iid):
        self.verb("start", iid)
        self.verb("attest", iid, "--cond", "c1", "--which", "postconditions",
                  "--note", "ok")
        return self.verb("advance", iid, "--why", f"{iid} understood")

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def fields(self):
        return ec.mechanical_fields(self.load(), base_dir=self.dir)


class ReopensFieldTests(unittest.TestCase):
    """`reopens` sums the tasks' own `rework_count`, which only `reopen` writes.

    Neither of the two obvious alternatives can serve. The checklist's `why_trail`
    over-counts: `reopen` appends a marker for the target AND for every cascaded
    downstream gate, so gates nobody reopened would report reopens. The journal
    sidecar over-counts too, for a subtler reason — see
    `EscalatedReopenIsNotAReopenTests`, which is the test that killed it.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.spine = LiveSpine(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_reopens_tracks_real_engine_reopens_and_keeps_counting(self):
        self.spine.complete("s1")
        self.assertEqual(self.spine.fields().get("spine-step"), "s2")

        out = self.spine.verb("reopen", "s1", "--reason", "rework one")
        self.assertEqual(out.returncode, 0, out.stderr)
        fields = self.spine.fields()
        self.assertEqual(fields["spine-step"], "s1")
        self.assertEqual(fields["reopens"], 1)
        self.assertEqual(fields["rework-count"], 1)

        # A SECOND real reopen: the value moves to 2. A constant cannot be both.
        self.spine.verb("attest", "s1", "--cond", "c1", "--which", "postconditions",
                        "--note", "ok")
        self.spine.verb("advance", "s1", "--why", "reworked")
        self.assertEqual(self.spine.verb("reopen", "s1", "--reason", "rework two").returncode, 0)
        self.assertEqual(self.spine.fields()["reopens"], 2)

    def test_reopens_is_run_scoped_where_rework_count_is_step_scoped(self):
        """The two fields must be two facts, not one written twice."""
        self.spine.complete("s1")
        self.spine.complete("s2")
        self.assertEqual(self.spine.verb("reopen", "s2", "--reason", "only s2").returncode, 0)
        after = self.spine.fields()
        self.assertEqual(after["spine-step"], "s2")
        self.assertEqual(after["reopens"], 1)
        self.assertEqual(after["rework-count"], 1)

        # Reopen s1 as well. The run has now been reopened TWICE; the active step (s1)
        # has been reopened once. A single number cannot be both.
        self.assertEqual(self.spine.verb("reopen", "s1", "--reason", "also s1").returncode, 0)
        both = self.spine.fields()
        self.assertEqual(both["spine-step"], "s1")
        self.assertEqual(both["reopens"], 2)
        self.assertEqual(both["rework-count"], 1)

    def test_the_journal_sidecar_is_not_consulted_at_all(self):
        """The journal is NOT a witness, and this pins that it has not crept back in.

        It once was, reconciled by `max()` on the claim that neither witness could
        over-count. That claim was false — an escalated `reopen` journals a line
        without incrementing `rework_count` — so the journal witness was removed
        rather than compensated for. Deleting the sidecar outright must therefore
        leave the field completely unmoved, at a real non-zero value.
        """
        engine = load("checklist_engine")
        self.spine.complete("s1")
        self.assertEqual(self.spine.verb("reopen", "s1", "--reason", "r").returncode, 0)
        self.assertEqual(self.spine.fields()["reopens"], 1)

        engine.journal_path(self.spine.path).unlink()
        self.assertEqual(self.spine.fields()["reopens"], 1)

    def test_reopens_is_refused_only_when_the_witness_cannot_be_read(self):
        """Tested on the helper directly: a checklist malformed enough to lose its
        `tasks` mapping cannot produce an active step either, so `mechanical_fields`
        would never reach this branch. It is kept because a partial read must still
        refuse rather than answer 0."""
        self.assertIsNone(ec.reopen_total({"tasks": "not a mapping"}))
        self.assertEqual(ec.reopen_total({"tasks": {}}), 0)


class EscalatedReopenIsNotAReopenTests(unittest.TestCase):
    """An ESCALATED `reopen` is journalled as a `reopen` but never was one.

    This is the case a journal-witness `reopens` gets WRONG, and the reason the
    field now reads the per-task `rework_count` witness alone. `reopen()`'s
    rework-cap branch blocks and bubbles WITHOUT incrementing `rework_count`, and
    it returns a normal string rather than raising — so `main()` takes the success
    path and journals a `reopen` line for a reopen that its own message says did
    not happen. Ground truth is `rework_count`; the journal is inflated by exactly
    one line per escalation.

    **Both seams are exercised, and that is not belt-and-braces.** The journal line
    for the in-flight verb is written by `main()` AFTER the verb returns, so the
    journal witness read at a seam is short by one: the inflation is `E` at a
    `start` seam but `E-1` at a `reopen` seam. A single escalation is therefore
    exactly cancelled at a `reopen` seam, and a test that exercises only that seam
    PASSES on the journal-witness code it is supposed to catch. The `reopen`-seam
    case below needs two escalations to bite.

    Everything runs through the real CLI so the journal sidecar is written by
    `main()` exactly as in production. Nothing here hand-edits a journal: the
    escalation is reached the only way it can be reached, and `skip` is the only
    continuation past a cap-escalated gate (`resume` refuses it by design, `reopen`
    refuses a blocked gate, and `start` refuses because a blocked gate is
    non-terminal so `active_id()` keeps returning it).
    """

    SESSION = "sess-esc"
    CAP = 1

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # `<root>/<work-id>/spine.json`: `snapshot_path` is
        # `manifest_root(base_dir)/<work-id>/mechanical/<step>.json` and
        # `manifest_root` is the checklist directory's PARENT, so the emit lands
        # back in this directory only because it is named for the work id.
        self.dir = Path(self.tmp.name) / "esc"
        self.dir.mkdir(parents=True)
        self.path = self.dir / "spine.json"

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, items):
        tasks = {
            iid: {
                "id": iid, "title": iid, "imperative": f"do {iid}",
                "preconditions": [],
                "postconditions": [{"id": "c1", "statement": "done", "check": None,
                                    "satisfied": False}],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            }
            for iid in items
        }
        self.path.write_text(
            json.dumps({"work_id": "esc", "type": "gated",
                        "config": {"rework_cap": self.CAP},
                        "items": list(items), "tasks": tasks, "consolidation": None,
                        "triage_candidates": [], "blockers": []}, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
        out = self.verb("claim", "--claimed-by", "implementer")
        self.assertEqual(out.returncode, 0, out.stderr)

    def verb(self, *args):
        return subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(self.path), *args,
             "--session-id", self.SESSION],
            capture_output=True, text=True, encoding="utf-8",
        )

    def say(self, out):
        """The verb's own last line — the engine's message, not our paraphrase."""
        self.assertEqual(out.returncode, 0, out.stderr)
        return ((out.stdout or out.stderr).strip().splitlines() or [""])[-1]

    def complete(self, iid):
        self.say(self.verb("start", iid))
        self.say(self.verb("attest", iid, "--cond", "c1", "--which",
                           "postconditions", "--note", "ok"))
        self.say(self.verb("advance", iid, "--why", f"{iid} done"))

    def rework(self, iid, reason):
        """Reopen, satisfy again, advance — leaving `iid` complete and reopenable."""
        line = self.say(self.verb("reopen", iid, "--reason", reason))
        self.assertTrue(line.startswith(f"{iid} reopened"), line)
        self.say(self.verb("attest", iid, "--cond", "c1", "--which",
                           "postconditions", "--note", "ok"))
        self.say(self.verb("advance", iid, "--why", f"{iid} reworked"))

    def escalate(self, iid):
        """Breach the cap. The engine's OWN message is the ground truth here."""
        line = self.say(self.verb("reopen", iid, "--reason", "over the cap"))
        self.assertTrue(line.startswith(f"ESCALATED {iid}"), line)
        self.assertIn("not reopened", line)
        self.say(self.verb("skip", iid, "--reason", "escalation resolved: OBE"))

    def snapshot(self, step):
        """The record the SEAM emitted, not a value we asked the composer for."""
        return json.loads((self.dir / "mechanical" / f"{step}.json")
                          .read_text(encoding="utf-8"))

    def journal_reopen_lines(self):
        entries = [json.loads(ln) for ln
                   in (self.dir / "spine.json.journal").read_text(encoding="utf-8")
                   .splitlines() if ln.strip()]
        return sum(1 for e in entries if e.get("verb") == "reopen")

    def rework_total(self):
        return sum(t.get("rework_count", 0)
                   for t in json.loads(self.path.read_text(encoding="utf-8"))
                   ["tasks"].values())

    def test_an_escalation_does_not_inflate_reopens_at_a_start_seam(self):
        """ONE real reopen plus one escalation, read at a `start` seam.

        Inflation is `E` = 1 here: the journal carries two `reopen` lines for one
        reopen, and it is fully written by the time `start b` fires the seam.
        """
        self.build(["a", "b"])
        self.complete("a")
        self.rework("a", "the one real reopen")   # T = 1
        self.escalate("a")                        # E = 1, then skipped
        self.say(self.verb("start", "b"))         # <- the seam emits here

        # The fixture really does reproduce the divergence it exists to catch.
        # Without this the test could go green on a run where the witnesses agree.
        self.assertEqual(self.journal_reopen_lines(), 2, "fixture no longer diverges")
        self.assertEqual(self.rework_total(), 1)

        self.assertEqual(self.snapshot("b")["mechanical"]["reopens"], 1)

    def test_escalations_do_not_inflate_reopens_at_a_reopen_seam(self):
        """THREE real reopens plus two escalations, read at a `reopen` seam.

        Two escalations are required. At a `reopen` seam the in-flight verb's own
        journal line does not exist yet, so the journal witness is `T + E - 1`;
        with `E = 1` that equals `T` and a journal-witness implementation passes
        by coincidence. With `E = 2` it reads 4 against a true 3.
        """
        self.build(["a", "b", "c"])
        for iid in ("a", "b"):
            self.complete(iid)
            self.rework(iid, f"real reopen of {iid}")   # T += 1
            self.escalate(iid)                          # E += 1, then skipped
        self.complete("c")
        line = self.say(self.verb("reopen", "c", "--reason", "real reopen of c"))
        self.assertTrue(line.startswith("c reopened"), line)   # T = 3, seam emits

        # 5 lines AFTER the verb returned; the seam ran one line earlier, so the
        # witness the composer would have read is 4 against a ground truth of 3.
        self.assertEqual(self.journal_reopen_lines(), 5, "fixture no longer diverges")
        self.assertEqual(self.rework_total(), 3)

        self.assertEqual(self.snapshot("c")["mechanical"]["reopens"], 3)


class FailedCommandsFieldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_failed_commands_tracks_real_non_zero_command_checks(self):
        spine = LiveSpine(
            Path(self.tmp.name),
            checks={"s1": {"kind": "command", "command": "exit 3"}},
        )
        spine.verb("start", "s1")
        self.assertEqual(spine.fields()["failed-commands"], 0)

        # A real failing check, run by the engine, refusing the advance.
        self.assertEqual(spine.verb("advance", "s1", "--why", "try").returncode, 1)
        self.assertEqual(spine.fields()["failed-commands"], 1)
        # Again: it counts, it is not a boolean and not a constant.
        spine.verb("advance", "s1", "--why", "try again")
        self.assertEqual(spine.fields()["failed-commands"], 2)

    def test_a_passing_command_check_does_not_count(self):
        """The one-sided test's blind spot: a counter that counted every command
        would pass a test that only ever checks it goes up."""
        spine = LiveSpine(
            Path(self.tmp.name),
            checks={"s1": {"kind": "command", "command": "exit 0"}},
        )
        spine.verb("start", "s1")
        self.assertEqual(spine.verb("advance", "s1", "--why", "ok").returncode, 0)
        # s1 advanced, so the active step is s2 — read s1's own tally directly.
        cl = spine.load()
        evidence = cl["tasks"]["s1"]["evidence"]
        self.assertTrue(any(e["type"] == "command-output" for e in evidence),
                        "the engine must have recorded a command-output item")
        self.assertEqual(ec.failed_command_count(cl["tasks"]["s1"]), 0)


class ContextManifestRefTests(unittest.TestCase):
    """`context-manifest-ref` is `<manifest-ref>@<revision>` per EPISODE_STORE.md §8,
    where the revision pins the manifest's OWN blob hash at capture time. That is only
    honest because g1's emit is write-if-absent: bytes that could be rewritten cannot
    be pinned."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.spine = LiveSpine(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self):
        return self.spine.dir / "context" / "s1.json"

    def test_ref_pins_the_manifests_own_blob_oid(self):
        self.spine.verb("start", "s1")
        self.assertTrue(self.manifest().exists(), "g1's seam must have emitted it")
        ref = self.spine.fields()["context-manifest-ref"]
        head, _, revision = ref.partition("@")
        self.assertEqual(head, "ctx-wk-live-s1")
        self.assertEqual(revision, cm_rev_of(self.manifest()))

    @unittest.skipUnless(GIT, "git not available on PATH")
    def test_the_pin_equals_git_hash_object_on_that_exact_file(self):
        self.spine.verb("start", "s1")
        revision = self.spine.fields()["context-manifest-ref"].split("@")[1]
        proc = subprocess.run(
            ["git", "hash-object", str(self.manifest())],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(revision, proc.stdout.strip())

    def test_the_pin_moves_when_the_manifest_bytes_move(self):
        """A pin that did not follow its own bytes would be a decoration."""
        self.spine.verb("start", "s1")
        before = self.spine.fields()["context-manifest-ref"]
        path = self.manifest()
        path.write_text(path.read_text(encoding="utf-8").replace('"step"', '"STEP"'),
                        encoding="utf-8", newline="\n")
        self.assertNotEqual(self.spine.fields()["context-manifest-ref"], before)

    def test_ref_is_refused_when_no_manifest_was_taken(self):
        """Never a plausible `ctx-<run>-<step>@` with an empty or invented revision."""
        self.spine.verb("start", "s1")
        self.manifest().unlink()
        self.assertNotIn("context-manifest-ref", self.spine.fields())


class RefusalsCounterTests(unittest.TestCase):
    """`refusals` had NO engine-state source before this change.

    A refusal raises `EngineError`; `main()` catches it and DOES persist the
    checklist, but recorded nothing about the refusal, and the journal sidecar is
    documented and implemented as success-only (`append_journal_entry` sits after the
    `return 1`). So the field was secretly agent-dependent — the exact thing
    `decision:zero-agent-effort-is-literal` forbids. These tests pin both directions,
    because a counter that incremented on EVERYTHING would pass a one-sided test that
    only ever checks it goes up.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.spine = LiveSpine(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_real_refusal_increments_the_counter_to_a_specific_value(self):
        self.assertEqual(self.spine.load()["refusals"], 0)

        # A real, state-caused refusal: advance a task that was never started.
        out = self.spine.verb("advance", "s1", "--why", "not started")
        self.assertEqual(out.returncode, 1)
        self.assertIn("REFUSED", out.stderr)
        self.assertEqual(self.spine.load()["refusals"], 1)
        self.assertEqual(self.spine.fields()["refusals"], 1)

        # A second, DIFFERENT refusal: the value is a tally, not a flag.
        self.assertEqual(self.spine.verb("start", "no-such-item").returncode, 1)
        self.assertEqual(self.spine.load()["refusals"], 2)
        self.assertEqual(self.spine.fields()["refusals"], 2)

    def test_a_successful_verb_does_not_move_the_counter(self):
        """The case a one-sided test misses entirely."""
        self.assertEqual(self.spine.verb("start", "s1").returncode, 0)
        self.assertEqual(self.spine.load()["refusals"], 0)
        self.assertEqual(
            self.spine.verb("attest", "s1", "--cond", "c1", "--which",
                            "postconditions", "--note", "ok").returncode, 0)
        self.assertEqual(self.spine.load()["refusals"], 0)
        self.assertEqual(self.spine.verb("advance", "s1", "--why", "done").returncode, 0)
        self.assertEqual(self.spine.load()["refusals"], 0)
        self.assertEqual(self.spine.fields()["refusals"], 0)


class AdditiveOnlyTests(unittest.TestCase):
    """A checklist saved BEFORE the counter existed must still work everywhere.

    Other commanders are live on this engine, so "additive" is a hard constraint, not
    a preference: no existing field changes meaning and no existing reader breaks.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.spine = LiveSpine(Path(self.tmp.name))
        # Strip the counter back out — this file is now byte-identical in shape to one
        # written by the pre-#305 engine.
        data = self.spine.load()
        data.pop("refusals", None)
        self.spine.path.write_text(json.dumps(data, indent=2) + "\n",
                                   encoding="utf-8", newline="\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_existing_engine_reader_still_works(self):
        engine = load("checklist_engine")
        cl = self.spine.load()
        self.assertNotIn("refusals", cl)
        self.assertEqual(engine.active_id(cl), "s1")
        self.assertEqual(engine._all_evidence_ids(cl), set())
        self.assertIsInstance(engine.task(cl, "s1"), dict)
        self.assertIsNone(engine._latest_why_record(cl))

    def test_the_cli_drives_a_pre_counter_checklist_end_to_end(self):
        self.assertEqual(self.spine.run("current").returncode, 0)
        self.assertEqual(self.spine.complete("s1").returncode, 0)
        self.assertEqual(self.spine.verb("reopen", "s1", "--reason", "r").returncode, 0)

    def test_the_field_is_refused_rather_than_reported_as_zero(self):
        """Absence must not be readable as "no refusals happened" — this checklist was
        driven by an engine that could not have counted them."""
        self.assertNotIn("refusals", self.spine.fields())

    def test_a_manifest_can_still_be_built_from_a_pre_counter_checklist(self):
        cm = load("context_manifest")
        manifest = cm.build_manifest(self.spine.load(), ec.resolve_roots(self.spine.dir))
        self.assertEqual(manifest["step"], "s1")


@unittest.skipUnless(GIT, "git not available on PATH")
class ZeroAgentEffortTests(unittest.TestCase):
    """The acceptance property, end to end and through the CLI: a run in which the
    agent records NOTHING still yields the full mechanical field group.

    The completeness assertion is delegated to `apply_episode_delta.validate_delta()`
    — the real writer's own validator, which requires every mechanical scalar field —
    rather than to a list retyped here, which could drift from the contract silently.
    Note carefully what that does and does not prove: it proves the group is COMPLETE
    and writer-ready. It does not prove any value is RIGHT; that is what every
    tracking test above is for. Presence and truth are different checks and this file
    keeps them apart on purpose.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.spine = LiveSpine(Path(self.tmp.name) / "repo", in_repo=True)

    def tearDown(self):
        self.tmp.cleanup()

    def snapshot_file(self, step="s1"):
        return self.spine.dir / "mechanical" / f"{step}.json"

    def test_claim_and_start_alone_emit_the_full_group(self):
        # `claim` happened in setUp. This is the ONLY other command, and it is not a
        # capture command — it is how an agent begins any step.
        self.assertEqual(self.spine.verb("start", "s1").returncode, 0)

        self.assertTrue(self.snapshot_file().exists(),
                        "the seam must have emitted a mechanical snapshot")
        snapshot = json.loads(self.snapshot_file().read_text(encoding="utf-8"))
        mech = snapshot["mechanical"]

        aed = load("apply_episode_delta")
        aed.validate_delta({"work_id": mech["run"], "ops": [{
            "op": "create", "mechanical": mech,
            "agent_supplied": {k: {"strength": "medium", "statement": "s"}
                               for k in aed.AGENT_SUPPLIED_KINDS},
        }]})

        # ...and the values are REAL, not placeholders that merely satisfy the shape.
        self.assertEqual(mech["run"], "wk-live")
        self.assertEqual(mech["role"], "implementer")
        self.assertEqual(mech["spine-step"], "s1")
        self.assertEqual(mech["project"], "repo")
        self.assertTrue(mech["context-manifest-ref"].startswith("ctx-wk-live-s1@"))
        self.assertEqual(snapshot["refused"], [])

    def test_the_snapshot_refreshes_when_the_step_is_reopened(self):
        """Unlike the manifest, the snapshot OVERWRITES: it carries counters, and a
        stale counter is a wrong fact rather than a preserved record."""
        self.spine.complete("s1")
        self.assertEqual(self.spine.verb("reopen", "s1", "--reason", "again").returncode, 0)
        mech = json.loads(self.snapshot_file().read_text(encoding="utf-8"))["mechanical"]
        self.assertEqual(mech["reopens"], 1)
        self.assertEqual(mech["rework-count"], 1)

    def test_a_refused_field_is_named_rather_than_silently_missing(self):
        """Fail-soft is not fail-silent, inherited from g1: an absent field and a
        field nobody tried to read must stay tellable apart."""
        outside = LiveSpine(Path(self.tmp.name) / "plain")  # not a repository
        outside.verb("start", "s1")
        snapshot = json.loads(
            (outside.dir / "mechanical" / "s1.json").read_text(encoding="utf-8"))
        self.assertIn("project", snapshot["refused"])
        self.assertNotIn("project", snapshot["mechanical"])


class SnapshotIsFailSoftTests(unittest.TestCase):
    """The seam's hardest constraint, inherited unchanged from g1: the byproduct must
    never be able to break its host. A composer that throws must not raise into a
    verb, must not change an exit code, and must not make a healthy manifest look
    like a failed one."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "wk"
        self.dir.mkdir(parents=True)
        self.cl = checklist(work_id="wk", items=["s1"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_throwing_composer_neither_raises_nor_corrupts_the_manifest(self):
        original = ec.mechanical_fields
        try:
            def boom(*a, **k):
                raise RuntimeError("composer exploded")

            ec.mechanical_fields = boom
            written = ec.emit_step_manifest(self.cl, "s1", self.dir)
        finally:
            ec.mechanical_fields = original

        self.assertIsNotNone(written)
        manifest = json.loads(Path(written).read_text(encoding="utf-8"))
        # A real manifest, NOT g1's failure stub: the manifest did not fail, the
        # snapshot did, and conflating them would misreport g1's own health.
        self.assertNotIn("emit_error", manifest)
        self.assertEqual(manifest["files"], [])

    def test_the_engine_verb_still_exits_zero_when_the_snapshot_cannot_be_written(self):
        spine = LiveSpine(Path(self.tmp.name))
        # Occupy the snapshot's directory path with a FILE, so any write under it
        # fails at the OS level.
        (spine.dir / "mechanical").write_text("not a directory\n",
                                              encoding="utf-8", newline="\n")
        out = spine.verb("start", "s1")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("s1 -> in-progress", out.stdout)


def cm_rev_of(path: Path) -> str:
    cm = load("context_manifest")
    with open(path, "rb") as handle:
        return cm.rev(handle.read())


if __name__ == "__main__":
    unittest.main()
