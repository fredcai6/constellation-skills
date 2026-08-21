
class ParentOptionalForRecoveryVerbsTests(unittest.TestCase):
    """F2 (deficiency cleanup batch A+B, review-adjudicated): B2's AST
    patches added `--parent` to `--resume`/`--verify-result` test calls
    that construct no `CrewSpec` and never needed it -- exactly why B2 put
    the requirement at `CrewSpec.__post_init__` rather than a blanket
    argparse `required=True`. The reviewer verified by hand that these
    three paths still work with no `--parent`; this class is the missing
    proof, mirroring `MandatoryModelTests`'s existing
    `test_resume_needs_no_model_at_all` / `test_bare_abandon_needs_no_model_
    at_all` pattern for the same reason: it is what would catch someone
    later "tidying" the enforcement up into argparse and silently breaking
    all three."""

    def test_resume_succeeds_with_no_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            session = "constellation/issue-1/g1/reviewer/attempt-1"
            stdout, stderr = RC.run_log_paths("issue-1", "g1", "reviewer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]  # deliberately no "parent" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(["--root", str(root), "--resume", session])
            self.assertEqual(0, code)
            self.assertEqual(
                "completed", RC.load_registry(RC.registry_path("issue-1", root))[0]["status"]
            )

    def test_bare_abandon_succeeds_with_no_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
            }]  # deliberately no "parent" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main([
                    "--root", str(root),
                    "--abandon", "constellation/issue-1/g1/reviewer/attempt-1",
                ])
            self.assertEqual(0, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertTrue(entry["abandoned"])

    def test_verify_result_succeeds_with_no_parent(self):
        # `ExternalBackend.verify` reads the stored entry directly -- no
        # `CrewSpec` is built on the verify path either. Uses the
        # `--accept-mtime-only-risk` escape hatch (#432) rather than a
        # spine, so no dispatch of any kind (which WOULD need --parent) is
        # needed to set the fixture up.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "dispatch": "external", "pid": None,
                "result": result, "started_at": RC._now(),
            }]  # deliberately no "parent" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main([
                    "--root", str(root), "--verify-result", session,
                    "--accept-mtime-only-risk", "no spine on this dispatch, result alone accepted",
                ])
            self.assertEqual(0, code)
            self.assertEqual(
                "completed", RC.load_registry(RC.registry_path("issue-1", root))[0]["status"]
            )

