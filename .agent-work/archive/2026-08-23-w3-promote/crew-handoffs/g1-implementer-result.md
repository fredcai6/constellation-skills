# Implementation Result

## Assigned gate
g1-implement (execute.json, work-id w3-promote)

## Completed slice
Promoted exactly the 8 named `check: null` conditions in
`skills/commander/templates/COMMANDER_SPINE.template.json` to real, mechanically-checked
conditions using only the engine's existing check kinds (`command`, `artifact`), per
`decision:no-new-check-kinds`:

1. `init.c1` -> `command` reading `.agent-work/<work-id>/spine.json`'s `engine_session.status`,
   exits 0 iff `"active"`.
2. `plan.c1` -> `artifact`, `evidence_type: "mission-frame"`, `match: {"status": ["produced",
   "skipped-as-trivial"]}`.
3. `plan.c4` -> `artifact`, `evidence_type: "plan-alternatives"`, `match: {"converged": true}`.
4. `plan.c5` -> `artifact`, `evidence_type: "plan-critic"`, `match: {"triaged": true}`.
5. `plan.c2` -> `artifact`, `evidence_type: "execute-plan"`, `match: {"exists": true}`
   (existence-only; `statement` text untouched, exactly as directed).
6. `reconcile.c1` -> `artifact`, `evidence_type: "file-diff"`, `match: {"nonempty": true}`.
7. `archive.c2` -> `command` comparing `git rev-parse @` vs `git rev-parse @{u}` (no unpushed
   commits).
8. `archive.c3` -> `artifact`, `evidence_type: "user-decision"` (reuses the archive.c5/review.c1/
   triage.c2 shape exactly -- no `match` key).

The `.agent-work/templates/` overlay was synced (byte-for-byte copy, confirmed by
`check_template_overlay_freshness.py` reporting no stale files). A new red-proof test class,
`CommanderSpineW3PromotePromotions`, was added to `tests/test_checklist_engine.py`, modeled on
`CommanderSpineBasisFields`. `tests/test_validate_spine.py`'s `falsifiable-all-null` floor
assertion's message was corrected from a stale "21" to the fresh measured count (17, down from 19
before this edit, since `init` and `reconcile` were each single-postcondition all-null gates that
this promotion clears).

## Scope
**Files changed:**
- `skills/commander/templates/COMMANDER_SPINE.template.json` (8 `check` fields, hand-edited as raw
  text; nothing else in the file touched -- verified byte-for-byte against the pre-edit `git show
  HEAD:...` snapshot).
- `.agent-work/templates/COMMANDER_SPINE.template.json` (overlay sync, byte-identical copy).
- `tests/test_checklist_engine.py` (new class `CommanderSpineW3PromotePromotions` + its
  `_gate_with_check` helper appended at file end; no existing class touched, including
  `CommanderSpineBasisFields`).
- `tests/test_validate_spine.py` (one assertion message in `TestCorpusSweepFindings.
  test_measured_finding_totals`: stale "21" -> fresh "17", with a one-line note on why).

**Specific exclusions touched:** no. `plan.c6`'s check text is untouched; `context.c1`,
`execute.c1`, `triage.c1` are untouched; `checklist_engine.py` is untouched; the `basis` objects on
`plan.c2`/`c4`/`c5` are untouched (only their sibling `check` field changed, confirmed by the git
diff showing the `basis` blocks byte-identical before/after).

## Behavior changed
Yes. Each of the 8 conditions now genuinely fails against the defective world it names, where
before `check: null` accepted any manual attestation unconditionally. Verified directly (not just
asserted) for every one of the 8: see Evidence below and the red-proof test class.

## Map Impact
- **Structural anchors touched:** none new -- these are data-only JSON conditions inside an
  already-mapped template file; no code symbol changed.
- **Capabilities added/changed/affected:** `init.c1`, `plan.c1/c2/c4/c5`, `reconcile.c1`,
  `archive.c2/c3` on the Commander spine are now mechanically enforced rather than
  attestation-only; the `plan.c4`/`plan.c5` conditions still literally say "NOT machine-verified"
  in their `statement` text even though they now carry a real check -- see Out-of-scope
  observations, this is a genuine follow-up, not fixed here (Close Criteria named only the `check`
  field for these two).
- **Decision candidates / resolved decisions:** `decision:no-new-check-kinds` and
  `decision:blocking-where-adjudicated` both applied exactly as directed; no new decision
  candidate raised by this slice itself.
- **Claims/evidence produced:** the red-proof test class is direct evidence that each of the 8
  checks discriminates a healthy state from an adversary-chosen defective one (never a restatement
  of the check's own match text) -- see the quoted source in Evidence below.
- **Trust limitations / drift found:** `map/INDEX.md` (code-map entity index, distinct from the
  packet-based architecture map the handoff's Map Anchors named as N/A for this gate) is now stale
  because the new test class added ~16 Python entities to `tests/test_checklist_engine.py`; a
  rerun of `python -m scripts.code_map build --root .` is needed before that freshness check is
  green again. This is out of this gate's Allowed Scope (only 4 files were authorized) -- flagged
  for whichever later gate/reconcile step owns `map/INDEX.md`.
- **Triage candidates:** see Out-of-scope observations below -- 3 test files elsewhere in the
  corpus pin the pre-promotion shape of exactly these conditions and now fail; each fix is a
  1-3 line, purely mechanical pin update, but none of the 3 files was in this gate's Allowed Scope.

## Test mode
**Required:** test-after (data/JSON + pytest authorship, not TDD red/green application code)
**Satisfied:** yes -- each promotion was hand-verified against a real healthy/defective pair before
the red-proof test class was written (see Evidence), then the test class itself was run and is
green.

## Evidence

```bash
$ grep -n '"check"' skills/commander/templates/COMMANDER_SPINE.template.json   # BEFORE (git show HEAD:...)
13:  ... "check": null, "satisfied": false}
25:  ... "check": null, ...   26: ... "check": {"kind": "command", ...} ...   (context.c1/c2, pre-existing)
42:  ... "check": null, ...   43: ... "check": {"kind": "artifact", "evidence_type": "user-decision"}, ...  (understand)
52:  ... "check": null, ...
54:  ... "check": null, ...        <- plan.c1 (TARGET)
55:  ... "check": null, ... basis: {...}   <- plan.c2 (TARGET)
56:  ... "check": {"kind": "artifact", "evidence_type": "user-decision"}, ...   (plan.c3, pre-existing)
57:  ... "check": null, ... basis: {...}   <- plan.c4 (TARGET)
58:  ... "check": null, ... basis: {...}   <- plan.c5 (TARGET)
59:  ... "check": {"kind": "command", ...}   (plan.c6, pre-existing)
69:  ... "check": null, ...
70:  ... "check": {"kind": "command", ...}   (execute.p2, pre-existing)
73:  ... "check": null, ...
74:  ... "check": {"kind": "command", ...}   (execute.c2, pre-existing)
87:  ... "check": null, ...
88:  ... "check": null, ...        <- reconcile.c1 (TARGET)
96:  ... "check": null, ...
98:  ... "check": null, ...
99:  ... "check": {"kind": "artifact", "evidence_type": "user-decision"}, ...   (triage.c2, pre-existing)
108: ... "check": null, ...
109: ... "check": {"kind": "artifact", "evidence_type": "user-decision"}, ...   (review.c1, pre-existing)
117: ... "check": null, ...
118: ... "check": {"kind": "command", ...}   (feedback.c1, pre-existing)
126: ... "check": null, ...
128: ... "check": {"kind": "command", ...}   (archive.c1, pre-existing)
129: ... "check": null, ...        <- archive.c2 (TARGET)
130: ... "check": {"kind": "command", ...}   (archive.c2b, pre-existing)
131: ... "check": null, ...        <- archive.c3 (TARGET)
132: ... "check": {"kind": "git-change-policy", ...}   (archive.c4, pre-existing)
133: ... "check": {"kind": "artifact", "evidence_type": "user-decision"}, ...   (archive.c5, pre-existing)

$ grep -n '"check"' skills/commander/templates/COMMANDER_SPINE.template.json   # AFTER
13: "check": {"kind": "command", "command": "python3 -c \"import json,sys; d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', encoding='utf-8')); sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""}, "satisfied": false}
54: "check": {"kind": "artifact", "evidence_type": "mission-frame", "match": {"status": ["produced", "skipped-as-trivial"]}}, "satisfied": false,
55: "check": {"kind": "artifact", "evidence_type": "execute-plan", "match": {"exists": true}}, "satisfied": false, "basis": {...},
57: "check": {"kind": "artifact", "evidence_type": "plan-alternatives", "match": {"converged": true}}, "satisfied": false, "basis": {...},
58: "check": {"kind": "artifact", "evidence_type": "plan-critic", "match": {"triaged": true}}, "satisfied": false, "basis": {...},
88: "check": {"kind": "artifact", "evidence_type": "file-diff", "match": {"nonempty": true}}, "satisfied": false}],
129: "check": {"kind": "command", "command": "test \"$(git -C <repo-root> rev-parse @)\" = \"$(git -C <repo-root> rev-parse @{u})\""}, "satisfied": false},
131: "check": {"kind": "artifact", "evidence_type": "user-decision"}, "satisfied": false},
```
(full verbatim grep output for both before/after was produced during the run; the table above is
condensed for readability -- exactly 8 lines flip from `null` to a real object, nothing else moves.)

```bash
$ python3 -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json',encoding='utf-8')); print('OK')"
OK

$ python3 scripts/check_template_overlay_freshness.py
  ...
  ok                 .agent-work/templates/COMMANDER_SPINE.template.json -- matches skills/commander/templates/COMMANDER_SPINE.template.json
  ...
all 56 overlay template(s) checked -- none stale

$ python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
........................................................................ [ 11%]
.................................................... [ 19%]
........................................................................ [ 30%]
.......................................................................................................................................... [ 51%]
........................................................................................................................... [ 70%]
............................................................................sss............................. [ 87%]
........................................................................ [ 98%]
............                                                             [100%]
646 passed, 3 skipped, 155 subtests passed in 5.87s

$ python3 -m pytest tests/test_checklist_engine.py -q -k CommanderSpineW3PromotePromotions --collect-only
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_archive_c2_command_check_discriminates_unpushed_commits
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_archive_c3_user_decision_type_only_discriminates
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_init_c1_command_check_discriminates_lease_status
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_no_condition_outside_pre_existing_and_promoted_carries_a_check
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_plan_c1_mission_frame_status_membership_discriminates
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_plan_c2_execute_plan_existence_only_discriminates
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_plan_c4_plan_alternatives_converged_discriminates
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_plan_c5_plan_critic_triaged_discriminates
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_promoted_checks_match_shipped_shape
tests/test_checklist_engine.py::CommanderSpineW3PromotePromotions::test_reconcile_c1_file_diff_nonempty_discriminates
10/546 tests collected (536 deselected) in 0.05s

$ python3 -m pytest tests/test_checklist_engine.py -q -k CommanderSpineW3PromotePromotions
..........
10 passed, 639 deselected in 0.12s
```

**Result:** pass -- both handoff-named verification commands green, overlay fresh, parse-check OK,
Wiring Grep shows exactly the 8 targeted lines flipped.

### The red-proof test class's own source (`tests/test_checklist_engine.py`, appended at EOF)

```python
def _gate_with_check(iid, check, status="in-progress"):
    """A gate whose single postcondition IS `check` -- the shipped shape
    copied verbatim from the template, never re-typed by hand."""
    t = gate(iid, status)
    t["postconditions"] = [
        {"id": "c1", "statement": "s", "check": check, "satisfied": False}
    ]
    return t


class CommanderSpineW3PromotePromotions(unittest.TestCase):
    """569-w3-promote g1: 8 named `check: null` conditions in the shipped
    COMMANDER_SPINE.template.json promoted to real, mechanically-checked
    conditions using only the engine's existing check kinds (`command`,
    `artifact`) per `decision:no-new-check-kinds` -- init.c1, plan.c1/c2/c4/
    c5, reconcile.c1, archive.c2/c3. Every other condition in the file, and
    every `basis` object already present on plan.c2/c4/c5 (CommanderSpine
    BasisFields above), is untouched.

    Modeled directly on CommanderSpineBasisFields above: pin PINNED_HEAD via
    `git rev-parse HEAD` captured at implementation time, `skipTest` (never
    fail) if HEAD has since moved past it -- this repo's edits are still
    uncommitted at authoring time, so HEAD is the base commit this gate's
    edit sits on top of, not a future commit; see that class's own docstring
    for why a moved HEAD skips rather than asserts against drift.

    Each promoted condition is attacked with an ADVERSARY-CHOSEN mutation --
    never a restatement of the check's own match text -- to prove the check
    can genuinely discriminate the healthy world from the defective one, per
    this epic's own thesis: a check with zero discriminating power is worse
    than the honest `check: null` it replaces."""

    SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"

    # Captured via `git rev-parse HEAD` at implementation time (g1 dispatch).
    PINNED_HEAD = "135c34eb0b0a10bc5cebb0e6e3869b124e63735e"

    EXPECTED_CHECKS = {
        ("init", "c1"): {
            "kind": "command",
            "command": (
                "python3 -c \"import json,sys; "
                "d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', "
                "encoding='utf-8')); "
                "sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""
            ),
        },
        ("plan", "c1"): {
            "kind": "artifact", "evidence_type": "mission-frame",
            "match": {"status": ["produced", "skipped-as-trivial"]},
        },
        ("plan", "c2"): {
            "kind": "artifact", "evidence_type": "execute-plan",
            "match": {"exists": True},
        },
        ("plan", "c4"): {
            "kind": "artifact", "evidence_type": "plan-alternatives",
            "match": {"converged": True},
        },
        ("plan", "c5"): {
            "kind": "artifact", "evidence_type": "plan-critic",
            "match": {"triaged": True},
        },
        ("reconcile", "c1"): {
            "kind": "artifact", "evidence_type": "file-diff",
            "match": {"nonempty": True},
        },
        ("archive", "c2"): {
            "kind": "command",
            "command": (
                'test "$(git -C <repo-root> rev-parse @)" '
                '= "$(git -C <repo-root> rev-parse @{u})"'
            ),
        },
        ("archive", "c3"): {"kind": "artifact", "evidence_type": "user-decision"},
    }

    # Every condition (across pre- and post-conditions) that already carried a
    # non-null check BEFORE this gate's promotion, measured directly against
    # `git show HEAD:...` rather than trusted from the handoff's own prose --
    # the handoff's "pre-existing 5" undercounts these 13; see this class's
    # entry in the g1 IMPLEMENTER_RESULT's Workflow Feedback.
    PRE_EXISTING_NONNULL = {
        ("context", "c2"), ("understand", "c1"), ("plan", "c3"), ("plan", "c6"),
        ("execute", "p2"), ("execute", "c2"), ("triage", "c2"), ("review", "c1"),
        ("feedback", "c1"), ("archive", "c1"), ("archive", "c2b"), ("archive", "c4"),
        ("archive", "c5"),
    }

    def _skip_if_head_moved(self):
        import subprocess
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        head = out.stdout.strip()
        if head != self.PINNED_HEAD:
            self.skipTest(
                f"pinned to shipped revision {self.PINNED_HEAD}, HEAD is now "
                f"{head} -- this test's assumptions about the template's "
                "shape need re-verifying against the current HEAD before "
                "they can be trusted, not silently re-run against drift"
            )

    def _load_spine(self):
        return json.loads(self.SPINE.read_text(encoding="utf-8"))

    def test_promoted_checks_match_shipped_shape(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        for (tid, cid), expected in self.EXPECTED_CHECKS.items():
            with self.subTest(cond=f"{tid}.{cid}"):
                by_id = {c["id"]: c for c in cl["tasks"][tid]["postconditions"]}
                self.assertEqual(by_id[cid]["check"], expected)

    def test_no_condition_outside_pre_existing_and_promoted_carries_a_check(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        nonnull = set()
        for tid, t in cl["tasks"].items():
            for which in ("preconditions", "postconditions"):
                for c in t.get(which) or []:
                    if c.get("check") is not None:
                        nonnull.add((tid, c["id"]))
        expected = self.PRE_EXISTING_NONNULL | set(self.EXPECTED_CHECKS)
        self.assertEqual(
            nonnull, expected,
            "exactly the 13 pre-existing non-null checks plus these 8 "
            "promotions -- and no other condition anywhere in the template "
            "-- may carry a check; a mismatch means either a missed target "
            "or drift onto a condition this gate must not touch",
        )

    # ---- artifact-kind promotions: attest() cross-task reference, exactly ----
    # the mechanism `docs/CHECKLIST_SCHEMA.md`'s "attest" row documents (verify
    # exists + evidence_type + match; never asserts an artifact from thin air).

    def _assert_artifact_discriminates(
        self, cid, wrong_type_evidence, adversary_payload, matching_payload,
    ):
        """Shared drive for every artifact-kind promotion below: (1) evidence
        of the WRONG `type` is refused on the `evidence_type` boundary; (2)
        evidence of the RIGHT type but an adversary-chosen non-matching
        payload is refused on the `match` boundary; (3) a genuinely matching
        payload satisfies it -- proving the check can pass as well as fail."""
        tid, real_cid = cid.split(".")
        check = self.EXPECTED_CHECKS[(tid, real_cid)]
        src = gate("src", "in-progress")
        target = _gate_with_check("target", check)
        cl = gated(src=src, target=target)

        # (1) wrong evidence_type -- attacks the TYPE boundary, not the match.
        E.attach(cl, "src", wrong_type_evidence, {})
        with self.assertRaisesRegex(
            E.EngineError,
            re.escape(f"is type {wrong_type_evidence!r}, not the required {check['evidence_type']!r}"),
        ):
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-1")

        # (2) right type, adversary-chosen non-matching payload -- attacks the
        # boundary the match does NOT restate; see each caller's own rationale.
        E.attach(cl, "src", check["evidence_type"], adversary_payload)
        with self.assertRaisesRegex(E.EngineError, "does not match required"):
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-2")

        # (3) positive control: a genuinely matching artifact DOES satisfy it.
        E.attach(cl, "src", check["evidence_type"], matching_payload)
        self.assertEqual(
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-3"),
            "attested target.c1 via e-src-3",
        )

    def test_plan_c1_mission_frame_status_membership_discriminates(self):
        self._skip_if_head_moved()
        # adversary: a differently-CASED status string -- attacks the
        # case-sensitivity boundary the match list does not spell out, not a
        # restatement of "produced" / "skipped-as-trivial" themselves.
        self._assert_artifact_discriminates(
            "plan.c1",
            wrong_type_evidence="user-decision",
            adversary_payload={"status": "Produced"},
            matching_payload={"status": "skipped-as-trivial"},
        )

    def test_plan_c2_execute_plan_existence_only_discriminates(self):
        self._skip_if_head_moved()
        # adversary: an EXPLICIT `exists: false` -- a real "checked for it and
        # it is NOT there" claim, distinct from simply attaching no evidence
        # at all (which a different assertion already covers via wrong-type).
        self._assert_artifact_discriminates(
            "plan.c2",
            wrong_type_evidence="mission-frame",
            adversary_payload={"exists": False},
            matching_payload={"exists": True},
        )

    def test_plan_c4_plan_alternatives_converged_discriminates(self):
        self._skip_if_head_moved()
        # adversary: the STRING "true" rather than the boolean True -- attacks
        # exact-type equality (`_artifact_match_satisfied` uses `==`, so a
        # truthy-looking string is not a truthy-looking bool), never a
        # restatement of "converged".
        self._assert_artifact_discriminates(
            "plan.c4",
            wrong_type_evidence="plan-critic",
            adversary_payload={"converged": "true"},
            matching_payload={"converged": True},
        )

    def test_plan_c5_plan_critic_triaged_discriminates(self):
        self._skip_if_head_moved()
        # adversary: an explicit `triaged: false` -- the actual defect this
        # check exists to catch (critic ran, findings never triaged), not a
        # restatement of the match's own "triaged" key.
        self._assert_artifact_discriminates(
            "plan.c5",
            wrong_type_evidence="plan-alternatives",
            adversary_payload={"triaged": False},
            matching_payload={"triaged": True},
        )

    def test_reconcile_c1_file_diff_nonempty_discriminates(self):
        self._skip_if_head_moved()
        # adversary: an explicit `nonempty: false` -- "the diff came back
        # empty", the actual defect (map never touched), not a restatement of
        # "nonempty" itself.
        self._assert_artifact_discriminates(
            "reconcile.c1",
            wrong_type_evidence="command-output",
            adversary_payload={"nonempty": False},
            matching_payload={"nonempty": True},
        )

    def test_archive_c3_user_decision_type_only_discriminates(self):
        self._skip_if_head_moved()
        # This check carries NO `match` at all (reuses the archive.c5 /
        # review.c1 / triage.c2 shape exactly), so `match={}` is vacuously
        # true for ANY payload of the right type -- the ONLY boundary this
        # check has is `evidence_type` itself. The adversary payload below is
        # therefore an arbitrary dict; what discriminates is exclusively (1).
        check = self.EXPECTED_CHECKS[("archive", "c3")]
        self.assertNotIn("match", check)
        src = gate("src", "in-progress")
        target = _gate_with_check("target", check)
        cl = gated(src=src, target=target)
        E.attach(cl, "src", "review-result", {"verdict": "APPROVE"})
        with self.assertRaisesRegex(
            E.EngineError,
            re.escape("is type 'review-result', not the required 'user-decision'"),
        ):
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-1")
        E.attach(cl, "src", "user-decision", {"cite": "spine_close"})
        self.assertEqual(
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-2"),
            "attested target.c1 via e-src-2",
        )

    # ---- command-kind promotions: `advance` runs them; `attest` refuses ----

    def test_init_c1_command_check_discriminates_lease_status(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("init", "c1")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            (root / ".agent-work" / work_id).mkdir(parents=True)
            spine_path = root / ".agent-work" / work_id / "spine.json"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real claim() write -- status == "active".
            spine_path.write_text(json.dumps({"engine_session": {"status": "active"}}), encoding="utf-8")
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): a status value the lease machinery
            # itself never legitimately writes -- claim() only ever writes
            # "active", release() only ever writes "released" -- this is
            # neither, so it attacks "the check ran and saw a BAD value", not
            # merely "the key/file was absent" (a different, easier defect).
            spine_path.write_text(
                json.dumps({"engine_session": {"status": "quantum-entangled-lease"}}),
                encoding="utf-8",
            )
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            # command checks are satisfied by `advance`, never `attest`.
            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)

    def test_archive_c2_command_check_discriminates_unpushed_commits(self):
        self._skip_if_head_moved()
        import shutil
        import subprocess
        if shutil.which("git") is None:
            self.skipTest("git not available")

        check = self.EXPECTED_CHECKS[("archive", "c2")]

        def run(args, cwd):
            r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            return r

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            remote = Path(tmp) / "remote.git"
            repo.mkdir()
            remote.mkdir()
            run(["git", "init", "-q", "-b", "main"], repo)
            run(["git", "config", "user.email", "t@t.example"], repo)
            run(["git", "config", "user.name", "t"], repo)
            run(["git", "commit", "-q", "--allow-empty", "-m", "init"], repo)
            run(["git", "init", "-q", "--bare"], remote)
            run(["git", "remote", "add", "origin", str(remote)], repo)
            run(["git", "push", "-q", "-u", "origin", "main"], repo)

            cmd = check["command"].replace("<repo-root>", repo.as_posix())
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: pushed, local HEAD == upstream.
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): a LOCAL commit made AFTER the last
            # push -- attacks branch-ahead-of-upstream specifically, not "no
            # upstream configured at all" (a different, less targeted defect
            # this check would also refuse but which never probes the
            # boundary the check text actually names -- @ vs @{u}).
            run(["git", "commit", "-q", "--allow-empty", "-m", "unpushed"], repo)
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)
```

## TDD evidence, if required
N/A -- test-after mode (data/JSON + pytest authorship, not application-code TDD). Each of the 8
promoted checks was hand-verified against a real healthy/defective pair (via direct
`subprocess`/engine calls) before the red-proof test class encoded that same verification as
pytest, so the discriminating behavior was observed before being formalized, not asserted blind.

## Docs/contracts touched
- none. `docs/CHECKLIST_SCHEMA.md` and `docs/CHECK_SCRIPT_CENSUS.md` were read (Map Anchors) but
  not edited -- the 8 promotions reuse existing, already-documented check kinds and match shapes
  verbatim; no contract changed.

## Assumptions
- `evidence_type` values (`mission-frame`, `plan-alternatives`, `plan-critic`, `execute-plan`) are
  free-form strings scoped to the `artifact` check's own `evidence_type`/match mechanism, distinct
  from the fixed enum documented for evidence *items'* own `type` field
  (`docs/CHECKLIST_SCHEMA.md` line ~338: `command-output | review-result | file-diff |
  user-decision | cartographer-verification | waiver | artifact-policy | refresh-request |
  basis-check`). Verified directly: neither `checklist_engine.py`'s `attach()`/`_check_condition()`
  nor `validate_spine.py` enforce that enum against `evidence_type`; it documents currently-used
  values, not a closed set. The handoff's own explicit instruction to use these 4 new values would
  have been unsatisfiable otherwise, so this reading is required, not optional.
- `PINNED_HEAD` in the new test class is the CURRENT `git rev-parse HEAD`
  (`135c34eb0b0a10bc5cebb0e6e3869b124e63735e`), since this gate's edits are still uncommitted at
  authoring time -- mirroring `CommanderSpineBasisFields`'s own pattern, where the pin names the
  commit the test's assumptions are valid against, not a future one.

## Stop conditions hit
None of the three named stop conditions fired: all 8 promotions expressed cleanly in an existing
check kind exactly as specified; every one demonstrably discriminates (see red-proof); no edit
touched `checklist_engine.py`. See Out-of-scope observations for a related but distinct finding
(collateral test breakage outside this gate's Allowed Scope) that is NOT one of the named stop
conditions and did not block completion.

## Out-of-scope observations
Running the full `pytest tests/ -q` suite (not the handoff's own narrower Verification Commands,
which are both green) surfaces 3 test files elsewhere in the corpus that pin the PRE-promotion
shape of exactly these 8 conditions and now fail as a direct, mechanical consequence of this
gate's own sanctioned promotion. None of the 3 is in this gate's Allowed Scope
(`skills/commander/templates/COMMANDER_SPINE.template.json`, its overlay, `tests/
test_checklist_engine.py`, `tests/test_validate_spine.py`), so none was touched here -- flagging
for Commander/a follow-up gate to fix, each is a small, mechanical, single-assertion update:

1. `tests/test_shipped_check_commands_resolve.py::ShippedCheckCommandsResolveTests::
   test_no_unresolved_token_survives_instantiation` -- `EXPECTED_COMMAND_CHECK_COUNT = 11` (line
   102) needs bumping to `13`: `init.c1` and `archive.c2` are two NEW `command`-kind checks across
   the shipped corpus.
2. `tests/test_plan_step_contract.py::HonestAboutNotBeingChecked::
   test_c4_and_c5_still_carry_no_check` (2 subtests) -- this test's own docstring already says "If
   a check ever lands, these tests must be revisited rather than left asserting a limit that no
   longer holds" (line ~206-208). `plan.c4`/`plan.c5` now carry the `artifact` checks this gate
   shipped; the test needs retiring or rewriting to assert the NEW shape instead. Note also: the
   sibling test in the same class, `test_c4_and_c5_declare_they_are_not_machine_verified`, still
   passes (their `statement` text literally says "NOT machine-verified", untouched by this gate
   per Close Criteria's "only the `check` field" scope) -- that statement text is now arguably
   stale given a real check exists, a genuine follow-up wording question for whoever owns that
   file, not resolved here.
3. `tests/test_install_constellation.py::InstallConstellationTests::
   test_installed_templates_use_absolute_bundled_script_paths` (line ~326) -- asserts
   `spine["tasks"]["init"]["postconditions"][0]["check"]` is `None` with a comment explaining the
   historical reason (issue #610 retired `init`'s self-scaffolding call); needs updating to assert
   the new command-check shape instead (or just that it is non-null and contains no unresolved
   `<...-skill-dir>` placeholder, matching the test's own actual subject -- bundled-script-path
   resolution, which this new check does not use at all since it inlines `python3 -c` rather than
   invoking a bundled script).

Additionally, `map/INDEX.md` (the code-map entity index) is now stale --
`tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
fails (5739 vs. 5723 entities) purely because the new test class added ~16 Python entities to
`tests/test_checklist_engine.py`. Confirmed this is caused by my edit (passes clean on `git
stash`). `map/INDEX.md` is not in this gate's Allowed Scope; a `python -m scripts.code_map build
--root .` rerun is needed, likely as part of whichever gate in this epic's own `execute.json`
handles Cartographer reconciliation.

An untracked `.agent-work/<work-id>/` directory (literal, unsubstituted placeholder as its own
name) exists in the worktree, dated before this session started -- not created by this gate, left
untouched.

## Workflow Feedback

- **Handoff gaps:** the Close Criteria's phrase "no other condition in the file is touched" and
  the red-proof instruction "no other condition in the file carries a non-null check outside the
  pre-existing 5 + these 8" undercounts: the actual pre-existing non-null-check population (across
  both pre- and post-conditions) is 13, not 5, measured directly against `git show HEAD:...`. I
  used the real, measured 13 in the shipped test rather than the handoff's "5" (which would have
  made the test assert something false). Whoever wrote "5" may have meant a narrower subset (e.g.
  distinct `user-decision`-shaped artifact checks, of which there ARE exactly 5:
  `understand.c1`/`plan.c3`/`triage.c2`/`review.c1`/`archive.c5`) -- worth confirming which was
  intended, though it did not change what I shipped.
- **Context rediscovered:** the handoff named `docs/CHECK_SCRIPT_CENSUS.md` and
  `docs/CHECKLIST_SCHEMA.md` as map entry points but not the actual mechanics needed to build a
  correct red-proof: `_check_condition`/`attest`/`_artifact_match_satisfied` in
  `scripts/checklist_engine.py` (exact match semantics, exact refusal message text), and the
  existing `AttestArtifactByReference` test class in `tests/test_checklist_engine.py` (the
  idiomatic `gate()`/`gated()`/`E.attach()`/`E.attest()` fixture pattern this new class reuses). I
  had to read the engine source directly to confirm command checks are satisfied by `advance` and
  refuse `attest` (line ~3775, `raise EngineError(f"{cond_id} is engine-checked; cannot attest")`)
  -- the handoff asserted this as fact ("confirm this in your test"), which was correct, but the
  where-to-look wasn't named.
- **Instructions improvised around:** the handoff's Verification Commands and Required Evidence
  scope narrowly to `tests/test_checklist_engine.py tests/test_validate_spine.py`. I additionally
  ran the full `pytest tests/` suite on my own initiative (not required) and found 3 more test
  files broken by this exact, correctly-scoped promotion (see Out-of-scope observations). I did
  NOT expand my Allowed Scope to fix them, honoring the handoff's explicit file list and its own
  emphasis on scope discipline (the compact-JSON-format warning) -- I judged that silently leaving
  them broken was worse than surfacing them loudly here, but fixing them was not authorized.
- **What would have made this easier:** before scoping a promotion gate like this one, grep the
  whole `tests/` tree for hardcoded pins on the specific conditions being promoted (e.g.
  `grep -rn 'postconditions.*check.*None\|assertIsNone.*check'` scoped to each `task.cond` id) and
  either pre-authorize the resulting fix list in Allowed Scope, or explicitly declare them
  out-of-scope-but-expected so the implementer doesn't have to decide alone whether running the
  full suite is even worth it.

## Return status
`complete`
