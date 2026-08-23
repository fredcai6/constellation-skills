"""Tests for scripts/validate_spine.py (epic-559/c1-spine-lint, #518, #562).

Nothing in the corpus looked at a spine's own checks before this module --
`checklist_engine.py` trusts the file it is handed and only discovers a
malformed shape or a vacuous check live, at the gate that tries to close over
it. This suite covers two families:

- **Shape** (`-k Shape`): the file the engine cannot even walk. Includes
  `TestShapeAcceptsEveryShippedTemplate`, which proves the checker does not
  refuse the 12 real templates the repo ships -- a shape checker that flags
  its own corpus is worse than no checker.
- **Falsifiability / Boundary** (`-k "Falsifiab or Boundary"`): the four #518
  faults. Faults 3 and 4 need judgment about what counts, so those get the
  three-way VIOLATING / INNOCENT / ACCEPTED fixture set
  (`tests/test_mcp_adoption.py::_cli_only_verb_violations` is the pattern this
  copies), plus a `Boundary` case reading the REAL shipped EXECUTE_PLAN
  gates the handoff named: `g1-review.c1` (honest bare artifact check) and
  `g1-integrate.c2` (the same claim, but with `match` -- both must stay clean).

`TestCorpus` (`-k Corpus`) is the g3 sweep: discovers every gated-or-survey
template by its own `type` field and asserts the discovered count, so a
broken discovery step cannot read as a clean pass.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TESTS = Path(__file__).resolve().parent / "fixtures" / "spine_lint" / "fixture_tests.py"


def _load(name: str, path: Path):
    import sys

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # Register BEFORE exec (checklist_engine.py's own gauge_reader loader does
    # the same): validate_spine's frozen @dataclass, with `from __future__
    # import annotations`, resolves its own module via sys.modules during
    # class creation and crashes if we exec unregistered.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


vs = _load("validate_spine", ROOT / "scripts" / "validate_spine.py")


def _codes(faults) -> set[str]:
    return {f.code for f in faults}


# --------------------------------------------------------------------------- #
# A minimal, valid GATED spine and a minimal, valid SURVEY spine -- every Shape
# test below mutates a deep copy of one of these rather than hand-building a
# fresh dict per case, so a case's mutation is the only thing that varies.
# --------------------------------------------------------------------------- #

def _valid_gated() -> dict:
    return {
        "work_id": "x",
        "type": "gated",
        "items": ["g1", "g2"],
        "tasks": {
            "g1": {
                "id": "g1", "title": "g1", "imperative": "do g1",
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "g1 done", "check": {"kind": "command", "command": "true"}, "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "evidence": [], "rework_count": 0,
            },
            "g2": {
                "id": "g2", "title": "g2", "imperative": "do g2",
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "g2 done", "check": {"kind": "command", "command": "true"}, "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "evidence": [], "rework_count": 0,
            },
        },
    }


def _valid_survey() -> dict:
    return {
        "work_id": "x",
        "type": "survey",
        "items": ["v1"],
        "tasks": {
            "v1": {
                "id": "v1", "title": "v1", "imperative": "check v1",
                "preconditions": [], "postconditions": [],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None, "finding": None,
                "evidence": [], "rework_count": 0,
            },
        },
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


# --------------------------------------------------------------------------- #
# Shape
# --------------------------------------------------------------------------- #

class TestShapeRejectsWrongTopLevelKey:
    def test_gates_instead_of_items(self):
        spine = _valid_gated()
        spine["gates"] = spine.pop("items")
        faults = vs.validate(spine)
        assert "shape-missing-items" in _codes(faults)
        assert any("gates" in f.message for f in faults if f.code == "shape-missing-items")

    def test_items_missing_entirely(self):
        spine = _valid_gated()
        del spine["items"]
        assert "shape-missing-items" in _codes(vs.validate(spine))

    def test_items_wrong_type(self):
        spine = _valid_gated()
        spine["items"] = {"g1": True}
        assert "shape-items-not-list" in _codes(vs.validate(spine))


class TestShapeRejectsTasksMismatch:
    def test_dangling_item(self):
        spine = _valid_gated()
        spine["items"].append("g3-does-not-exist")
        faults = vs.validate(spine)
        assert "shape-dangling-item" in _codes(faults)
        assert any(f.where == "g3-does-not-exist" for f in faults)

    def test_orphan_task(self):
        spine = _valid_gated()
        spine["tasks"]["g3-orphan"] = copy.deepcopy(spine["tasks"]["g1"])
        faults = vs.validate(spine)
        assert "shape-orphan-task" in _codes(faults)
        assert any(f.where == "g3-orphan" for f in faults)

    def test_tasks_not_a_dict(self):
        spine = _valid_gated()
        spine["tasks"] = ["g1", "g2"]
        assert "shape-tasks-not-dict" in _codes(vs.validate(spine))


class TestShapeRejectsUnknownCheckKind:
    def test_unimplemented_kind(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"][0]["check"] = {"kind": "vibe-check"}
        faults = vs.validate(spine)
        assert "shape-unknown-check-kind" in _codes(faults)

    @pytest.mark.parametrize("kind", ["command", "artifact", "git-change-policy"])
    def test_implemented_kinds_pass_shape(self, kind):
        spine = _valid_gated()
        chk = {"kind": kind}
        if kind == "command":
            chk["command"] = "true"
        elif kind == "artifact":
            chk["evidence_type"] = "review-result"
        spine["tasks"]["g1"]["postconditions"][0]["check"] = chk
        faults = vs.validate(spine)
        assert "shape-unknown-check-kind" not in _codes(faults)


class TestShapeRejectsUnknownType:
    def test_missing_type(self):
        spine = _valid_gated()
        del spine["type"]
        assert "shape-unknown-type" in _codes(vs.validate(spine))

    def test_bogus_type(self):
        spine = _valid_gated()
        spine["type"] = "freeform"
        assert "shape-unknown-type" in _codes(vs.validate(spine))


class TestShapeRejectsGatedMissingPostconditions:
    def test_postconditions_absent(self):
        spine = _valid_gated()
        del spine["tasks"]["g1"]["postconditions"]
        assert "shape-gated-missing-postconditions" in _codes(vs.validate(spine))

    def test_postconditions_empty(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"] = []
        assert "shape-gated-missing-postconditions" in _codes(vs.validate(spine))

    def test_postconditions_not_a_list(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"] = "yes"
        assert "shape-conditions-not-list" in _codes(vs.validate(spine))


class TestShapeRejectsSurveyMissingResult:
    def test_result_field_absent(self):
        spine = _valid_survey()
        del spine["tasks"]["v1"]["result"]
        assert "shape-survey-missing-result" in _codes(vs.validate(spine))

    def test_result_field_present_is_fine(self):
        spine = _valid_survey()
        assert "shape-survey-missing-result" not in _codes(vs.validate(spine))


class TestShapeAcceptsValidFixtures:
    def test_valid_gated_has_no_shape_faults(self):
        faults = vs.validate(_valid_gated())
        assert not [f for f in faults if f.code.startswith("shape-")]

    def test_valid_survey_has_no_shape_faults(self):
        faults = vs.validate(_valid_survey())
        assert not [f for f in faults if f.code.startswith("shape-")]


#: Every gated-or-survey checklist template the repo ships, discovered the
#: same way `discover_checklist_templates` does -- module-level so it is
#: computed once for both the Shape acceptance test below and TestCorpus.
SHIPPED_TEMPLATES = vs.discover_checklist_templates(ROOT)


class TestShapeAcceptsEveryShippedTemplate:
    """A shape checker that refuses its own corpus is worse than none. Every
    template the repo currently ships must carry zero shape faults, whatever
    it says about falsifiability (that is TestCorpus's job, not this one's)."""

    @pytest.mark.parametrize("path", SHIPPED_TEMPLATES, ids=lambda p: p.relative_to(ROOT).as_posix())
    def test_no_shape_faults(self, path):
        spine = json.loads(path.read_text(encoding="utf-8"))
        faults = [f for f in vs.validate(spine, repo_root=ROOT) if f.code.startswith("shape-")]
        assert not faults, f"{path}: {[str(f) for f in faults]}"

    def test_at_least_eleven_shipped_templates_found(self):
        # A floor, not a literal -- red only if the population narrows back
        # toward the table's stale count of 6, never on a legitimate addition.
        # Lowered 12 -> 11 by #639, which retired `workbench` and with it the
        # unused DEFAULT.template.json (one doc citation, no driver).
        assert len(SHIPPED_TEMPLATES) >= 11


# --------------------------------------------------------------------------- #
# Falsifiability fault 1: all postconditions check: null
# --------------------------------------------------------------------------- #

class TestFalsifiabilityAllNullPostconditions:
    def test_all_null_is_caught(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"] = [
            {"id": "c1", "statement": "a", "check": None, "satisfied": False},
            {"id": "c2", "statement": "b", "check": None, "satisfied": False},
        ]
        faults = vs.validate(spine)
        assert "falsifiable-all-null" in _codes(faults)
        assert any(f.where == "g1" for f in faults if f.code == "falsifiable-all-null")

    def test_one_real_check_among_nulls_is_innocent(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"] = [
            {"id": "c1", "statement": "a", "check": None, "satisfied": False},
            {"id": "c2", "statement": "b", "check": {"kind": "command", "command": "true"}, "satisfied": False},
        ]
        assert "falsifiable-all-null" not in _codes(vs.validate(spine))

    def test_survey_all_null_postconditions_not_flagged(self):
        # Survey postconditions are usually empty/unused ("the item IS the
        # check") -- this fault is scoped to gated tasks only.
        spine = _valid_survey()
        spine["tasks"]["v1"]["postconditions"] = [
            {"id": "c1", "statement": "a", "check": None, "satisfied": False},
        ]
        assert "falsifiable-all-null" not in _codes(vs.validate(spine))


# --------------------------------------------------------------------------- #
# Falsifiability fault 2: pytest -k selector collects zero tests
# --------------------------------------------------------------------------- #

def _spine_with_command(command: str) -> dict:
    spine = _valid_gated()
    spine["tasks"]["g1"]["postconditions"][0]["check"] = {"kind": "command", "command": command}
    return spine


class TestFalsifiabilityZeroCollectedSelector:
    def _spine_with_command(self, command: str) -> dict:
        return _spine_with_command(command)

    def test_selector_matching_nothing_is_caught(self):
        spine = self._spine_with_command(
            f"python -m pytest -q {FIXTURE_TESTS.as_posix()} -k this_selector_matches_nothing_zzz"
        )
        faults = vs.validate(spine, repo_root=ROOT)
        assert "falsifiable-zero-collected" in _codes(faults)

    def test_selector_matching_a_real_test_is_innocent(self):
        spine = self._spine_with_command(
            f"python -m pytest -q {FIXTURE_TESTS.as_posix()} -k alpha"
        )
        faults = vs.validate(spine, repo_root=ROOT)
        assert "falsifiable-zero-collected" not in _codes(faults)

    def test_the_gate_that_self_checks_collection_inline_is_still_caught(self):
        # The corpus's own idiom: `test $(pytest ... --collect-only ... | grep
        # -c '::') -ge N && pytest ...`. If the SAME zero-matching selector is
        # embedded in that idiom, the second (real-run) segment is still a
        # zero-collect check and must still be caught -- a well-formed inline
        # self-check elsewhere in the command does not exempt it.
        target = FIXTURE_TESTS.as_posix()
        spine = self._spine_with_command(
            f"test $(python -m pytest -q {target} -k nope_zzz --collect-only 2>/dev/null | grep -c '::') -ge 0 "
            f"&& python -m pytest -q {target} -k nope_zzz"
        )
        faults = vs.validate(spine, repo_root=ROOT)
        assert "falsifiable-zero-collected" in _codes(faults)

    def test_command_with_no_pytest_at_all_is_innocent(self):
        spine = self._spine_with_command("test -f scripts/validate_spine.py")
        faults = vs.validate(spine, repo_root=ROOT)
        assert "falsifiable-zero-collected" not in _codes(faults)


class TestFalsifiabilityZeroCollectDocumentedIdiom:
    """The corpus's own recommended self-checking idiom
    (docs/agents/CREW_CONTEXT.md, Verification Discipline): `test $(pytest
    ... --collect-only 2>/dev/null | grep -c '::') -ge N && pytest ...`. The
    `2>/dev/null` token lands in the first segment right after `pytest`; if
    it is folded in as a bogus positional test path, that path collects zero
    for real and the whole check is refused -- the 8-in-9 false-positive rate
    measured on the archive sweep. This must stay clean regardless of whether
    the SAME zero-matching selector elsewhere would legitimately be caught
    (see test_the_gate_that_self_checks_collection_inline_is_still_caught
    above -- that test is the control this one must not break)."""

    def test_documented_idiom_with_a_real_selector_is_innocent(self):
        target = FIXTURE_TESTS.as_posix()
        spine = _spine_with_command(
            f"test $(python -m pytest -q {target} -k alpha --collect-only "
            f"2>/dev/null | grep -c '::') -ge 1 && python -m pytest -q {target} -k alpha"
        )
        faults = vs.validate(spine, repo_root=ROOT)
        assert "falsifiable-zero-collected" not in _codes(faults)

    def test_idiom_still_catches_a_genuinely_zero_selector(self):
        # The redirect fix must not blanket-exempt the idiom shape -- a real
        # zero-collect selector wrapped in the idiom is still a real fault.
        target = FIXTURE_TESTS.as_posix()
        spine = _spine_with_command(
            f"test $(python -m pytest -q {target} -k this_matches_nothing_zzz "
            f"--collect-only 2>/dev/null | grep -c '::') -ge 1 "
            f"&& python -m pytest -q {target} -k this_matches_nothing_zzz"
        )
        faults = vs.validate(spine, repo_root=ROOT)
        assert "falsifiable-zero-collected" in _codes(faults)


class TestFalsifiabilityZeroCollectRedirectTokenShapes:
    """Direct unit coverage of the mechanism: a shell-redirect-shaped token
    must never be folded into `_pytest_targets` as a positional test path,
    whatever form it takes."""

    @pytest.mark.parametrize(
        "token",
        ["2>/dev/null", ">/dev/null", "2>&1", "&>/dev/null", "1>>/tmp/out", ">>out.log"],
        ids=lambda t: t,
    )
    def test_attached_redirect_token_excluded_from_targets(self, token):
        assert vs._pytest_targets(["-q", "-k", "sel", token]) == []

    def test_bare_redirect_operator_and_its_separate_destination_are_both_excluded(self):
        # shlex splits "2> /dev/null" (a space before the destination) into
        # two tokens; both the bare operator and its destination must go.
        assert vs._pytest_targets(["-k", "sel", "2>", "/dev/null"]) == []

    def test_a_real_path_is_still_collected_as_a_target(self):
        # The fix must stay narrow: an ordinary positional path is untouched.
        assert vs._pytest_targets(["-k", "sel", "tests/some_test.py"]) == ["tests/some_test.py"]


class TestFalsifiabilityZeroCollectInterpreterUnavailable:
    """Second #518 mechanism, same fault code: `_collects_zero` must invoke
    the interpreter the check's command TEXT names, not `sys.executable`
    (whichever python happens to be running this tool), and must confirm
    pytest is importable there before ever trusting an empty collection
    result as a real zero. docs/agents/CREW_CONTEXT.md documents that on the
    reference host `python3` has no pytest while `python` does, so a command
    written `python -m pytest ...` must resolve `python` even when
    `validate_spine.py` itself is invoked via `python3`. These tests use a
    fabricated fake interpreter rather than the real `python3`, so the
    assertion holds regardless of what any given CI host happens to have
    installed."""

    @staticmethod
    def _fake_interpreter(tmp_path: Path, body: str) -> str:
        script = tmp_path / "fake-interpreter"
        script.write_text(f"#!/usr/bin/env python3\n{body}\n")
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        return str(script)

    def test_interpreter_without_pytest_importable_is_undecidable_not_a_fault(self, tmp_path):
        # Simulates the reference host's python3: a real, runnable python
        # that simply cannot `import pytest`.
        fake = self._fake_interpreter(tmp_path, "import sys\nsys.exit(1)\n")
        assert vs._resolve_interpreter(fake) is None
        outcome, reason = vs._collects_zero(fake, ["-k", "alpha"], ROOT)
        assert outcome is vs._CollectOutcome.UNDECIDABLE
        assert reason and fake in reason

    def test_a_name_not_found_on_path_at_all_is_undecidable_not_a_fault(self):
        assert vs._resolve_interpreter("this-interpreter-does-not-exist-zzz") is None

    def test_the_real_interpreter_running_this_test_resolves_and_still_catches_real_zero(self, tmp_path):
        # Control: naming the interpreter that DOES have pytest importable
        # (this very test process) must still behave exactly as before --
        # the fix narrows false positives, it does not blind the checker.
        assert vs._resolve_interpreter(sys.executable) == sys.executable
        outcome, reason = vs._collects_zero(
            sys.executable, ["-k", "this_matches_nothing_zzz", FIXTURE_TESTS.as_posix()], ROOT
        )
        assert outcome is vs._CollectOutcome.ZERO
        assert reason is None

    def test_no_selector_segment_is_not_applicable_not_undecidable(self):
        # A pytest segment with no -k at all has nothing for this fault to
        # evaluate -- that is a different kind of "no fault" than genuinely
        # trying and failing, and must not be reported on either channel.
        outcome, reason = vs._collects_zero(sys.executable, [FIXTURE_TESTS.as_posix()], ROOT)
        assert outcome is vs._CollectOutcome.NOT_APPLICABLE
        assert reason is None

    def test_unresolvable_interpreter_yields_no_fault_end_to_end(self, tmp_path):
        # Full validate() path: a command naming an interpreter that cannot
        # run pytest must not read as `check: null`-equivalent vacuous, nor
        # as a fault -- it is undecidable, and undecidable must still be
        # visible on the result's own undecidable channel, not silence.
        fake = self._fake_interpreter(tmp_path, "import sys\nsys.exit(1)\n")
        spine = _spine_with_command(f"{fake} -m pytest -q {FIXTURE_TESTS.as_posix()} -k alpha")
        result = vs.validate(spine, repo_root=ROOT)
        assert "falsifiable-zero-collected" not in _codes(result)
        assert "undecidable-zero-collect" in {u.code for u in result.undecidable}


# --------------------------------------------------------------------------- #
# The undecidable channel itself (UNDECIDABLE_HANDOFF.md, C1): "could not
# tell" and "checked, found nothing wrong" must never share a code path.
# --------------------------------------------------------------------------- #

class TestUndecidableChannelIsReportedNotOmitted:
    """`validate()`'s return value must be able to SAY undecidable, in a
    place a caller actually reads: `.undecidable` on the returned
    `ValidationResult`, and its `str()` -- the same channel `main()`'s CLI
    output and any future library caller both go through."""

    @staticmethod
    def _fake_interpreter_without_pytest(tmp_path: Path) -> str:
        script = tmp_path / "fake-interpreter-no-pytest"
        script.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(1)\n")
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        return str(script)

    def test_validation_result_undecidable_attribute_is_populated(self, tmp_path):
        fake = self._fake_interpreter_without_pytest(tmp_path)
        spine = _spine_with_command(f"{fake} -m pytest -q {FIXTURE_TESTS.as_posix()} -k alpha")
        result = vs.validate(spine, repo_root=ROOT)
        assert len(result.undecidable) == 1
        assert isinstance(result.undecidable[0], vs.Undecidable)

    def test_str_of_a_clean_result_says_undecidable_when_present(self, tmp_path):
        # This is the exact defect: two runs that both print "no faults"
        # must not be allowed to look identical when one of them also could
        # not evaluate something. str() must name the difference.
        fake = self._fake_interpreter_without_pytest(tmp_path)
        spine = _spine_with_command(f"{fake} -m pytest -q {FIXTURE_TESTS.as_posix()} -k alpha")
        result = vs.validate(spine, repo_root=ROOT)
        assert not result  # zero faults -- the misleading-silence case
        text = str(result).lower()
        assert "undecid" in text

    def test_str_of_a_genuinely_sound_result_does_not_claim_undecidable(self):
        result = vs.validate(_valid_gated(), repo_root=ROOT)
        assert not result
        assert not result.undecidable
        assert "undecid" not in str(result).lower()

    def test_validate_file_result_also_carries_the_channel(self, tmp_path):
        fake = self._fake_interpreter_without_pytest(tmp_path)
        spine = _spine_with_command(f"{fake} -m pytest -q {FIXTURE_TESTS.as_posix()} -k alpha")
        p = tmp_path / "spine.json"
        p.write_text(json.dumps(spine))
        result = vs.validate_file(p, repo_root=ROOT)
        assert result.undecidable
        assert "undecid" in str(result).lower()

    def test_cli_output_names_the_undecidable_count_even_when_no_faults(self, tmp_path, capsys):
        fake = self._fake_interpreter_without_pytest(tmp_path)
        spine = _spine_with_command(f"{fake} -m pytest -q {FIXTURE_TESTS.as_posix()} -k alpha")
        p = tmp_path / "spine.json"
        p.write_text(json.dumps(spine))
        exit_code = vs.main([str(p), "--root", str(ROOT)])
        out = capsys.readouterr().out
        # Undecidable is not a failure -- exit code semantics are unchanged.
        assert exit_code == 0
        assert "OK" in out
        assert "undecidable" in out.lower()


# --------------------------------------------------------------------------- #
# Falsifiability fault 3: artifact, no match, statement asserts a property
# (#562) -- three-way VIOLATING / INNOCENT / ACCEPTED, per the handoff.
# --------------------------------------------------------------------------- #

class TestFalsifiabilityArtifactAssertsPropertyBoundary:
    VIOLATING = {
        "verdict is a specific value": ("review-result", "reviewer verdict is APPROVE", None),
        "the real #562 wording": ("implementer-result", "IMPLEMENTER_RESULT returned with no unresolved blockers", None),
        "explicit equality": ("review-result", "verdict == APPROVE", None),
    }

    INNOCENT = {
        "bare arrival, the shipped g1-review.c1 wording": ("review-result", "REVIEW_RESULT returned", None),
        "arrival with a qualifier but no property claim": ("implementer-result", "IMPLEMENTER_RESULT received for this gate", None),
        "property claim, but match is present (the fix)": ("review-result", "reviewer verdict is APPROVE", {"verdict": "APPROVE"}),
    }

    ACCEPTED = {
        "user-decision has no field to match against": ("user-decision", "human confirmed the decision is APPROVE", None),
    }

    def _faults(self, evidence_type, statement, match):
        check = {"kind": "artifact", "evidence_type": evidence_type}
        if match:
            check["match"] = match
        cond = {"id": "c1", "statement": statement, "check": check, "satisfied": False}
        return vs._fault_artifact_no_match("g1.postconditions.c1", cond, check)

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_violating_is_caught(self, label):
        evidence_type, statement, match = self.VIOLATING[label]
        assert self._faults(evidence_type, statement, match), (
            f"{label!r} asserts a property with no match to back it -- the "
            f"#562 defect this fault exists to catch"
        )

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_innocent_is_left_alone(self, label):
        evidence_type, statement, match = self.INNOCENT[label]
        found = self._faults(evidence_type, statement, match)
        assert not found, f"{label!r} is a correct statement/check pair, flagged anyway: {found}"

    @pytest.mark.parametrize("label", sorted(ACCEPTED))
    def test_accepted_exception_is_named_and_left_alone(self, label):
        evidence_type, statement, match = self.ACCEPTED[label]
        found = self._faults(evidence_type, statement, match)
        assert not found, (
            f"{label!r} is ACCEPTED (evidence_type {evidence_type!r} has no structured "
            f"field a human decision could `match`), flagged anyway: {found}"
        )


class TestBoundaryArtifactAgainstTheRealShippedGates:
    """The exact pair the handoff names: g1-review.c1 (honest, bare) and
    g1-integrate.c2 (same claim, but with `match`). Neither may be flagged --
    this is the shipped file getting it right, read live rather than copied."""

    PATH = ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json"

    def _cond_and_check(self, task_id, cond_id):
        data = json.loads(self.PATH.read_text(encoding="utf-8"))
        task = data["tasks"][task_id]
        cond = next(c for c in task["postconditions"] if c["id"] == cond_id)
        return cond, cond["check"]

    def test_g1_review_c1_bare_artifact_is_innocent(self):
        cond, check = self._cond_and_check("g1-review", "c1")
        assert check.get("kind") == "artifact" and not check.get("match")
        assert not vs._fault_artifact_no_match("g1-review.postconditions.c1", cond, check)

    def test_g1_integrate_c2_matched_artifact_is_innocent(self):
        cond, check = self._cond_and_check("g1-integrate", "c2")
        assert check.get("kind") == "artifact" and check.get("match")
        assert not vs._fault_artifact_no_match("g1-integrate.postconditions.c2", cond, check)


# --------------------------------------------------------------------------- #
# Falsifiability fault 4: unresolved <placeholder> in a command check --
# three-way VIOLATING / INNOCENT / ACCEPTED.
# --------------------------------------------------------------------------- #

class TestFalsifiabilityUnresolvedPlaceholderBoundary:
    VIOLATING = {
        "the real REVIEW_SURVEY defect": "python scripts/verify_fowler_pass.py <fowler-pass-record-path>",
        "an authoring scaffold placeholder": "<exact test command>",
        "an arbitrary made-up token": "python scripts/check.py <TODO-fill-me-in>",
    }

    INNOCENT = {
        "no placeholder at all": "python -m pytest -q tests",
        "shell input redirection, not a placeholder": "python check.py < input.txt",
    }

    ACCEPTED = {
        "work-id, resolved by resolve_spine": "python <commander-skill-dir>/scripts/init_work_area.py <work-id>",
        "repo-root, resolved by resolve_spine": "python scripts/map_orient.py verify-frame --root <repo-root>",
        "a role-specific session-id token": "echo <admiral-session-id>",
        "bare skill-dir, hardcoded-special-cased by resolve_spine": "python <skill-dir>/scripts/verify_cycles.py <work-id>",
    }

    def _faults(self, command):
        return vs._fault_unresolved_placeholder("g1.postconditions.c1", {"kind": "command", "command": command})

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_violating_is_caught(self, label):
        assert self._faults(self.VIOLATING[label]), (
            f"{label!r} carries a placeholder nothing will ever substitute"
        )

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_innocent_is_left_alone(self, label):
        found = self._faults(self.INNOCENT[label])
        assert not found, f"{label!r} carries no real placeholder, flagged anyway: {found}"

    @pytest.mark.parametrize("label", sorted(ACCEPTED))
    def test_accepted_resolver_owned_token_is_left_alone(self, label):
        found = self._faults(self.ACCEPTED[label])
        assert not found, (
            f"{label!r} is a resolver-owned token family (init_work_area.resolve_spine "
            f"substitutes it before a spine is ever driven), flagged anyway: {found}"
        )


class TestBoundaryPlaceholderAgainstTheRealShippedTemplate:
    """REVIEW_SURVEY.template.json's r6-fowler check once shipped the literal
    `<fowler-pass-record-path>` (the handoff's cited incident). It is fixed
    now -- this pins that the live file stays clean, read from disk rather
    than copied into a fixture."""

    def test_r6_fowler_check_carries_no_unresolved_placeholder(self):
        path = ROOT / "skills" / "reviewer" / "templates" / "REVIEW_SURVEY.template.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        check = data["tasks"]["r6-fowler"]["postconditions"][0]["check"]
        assert not vs._fault_unresolved_placeholder("r6-fowler.postconditions.c1", check)


# --------------------------------------------------------------------------- #
# g3: the corpus sweep. Population enumerated from each file's own `type`
# field (never the stale checklist-engine.md table), count asserted so a
# broken discovery step cannot read as a clean pass.
# --------------------------------------------------------------------------- #

class TestCorpusSweepPopulation:
    def test_population_matches_measured_gated_and_survey_types(self):
        # Independently recomputed here (not just reusing discover_checklist_templates)
        # so a bug shared by both the production function and this assertion cannot
        # hide -- this walks skills/*/templates/*.json and reads `type` itself.
        on_disk = []
        for path in sorted(ROOT.glob("skills/*/templates/*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("type") in ("gated", "survey"):
                on_disk.append(path)
        assert set(SHIPPED_TEMPLATES) == set(on_disk)
        assert len(SHIPPED_TEMPLATES) == 11, (
            f"measured population is {len(SHIPPED_TEMPLATES)}, not the 11 a cold "
            f"reviewer counted (12 before #639 retired workbench's unused "
            f"DEFAULT.template.json) -- if this is a legitimate addition/removal, update "
            f"this pin in the same edit; it exists so a broken discovery step (e.g. "
            f"a glob that stops matching) cannot silently read as a clean pass"
        )

    def test_discovery_would_not_be_fooled_by_the_stale_table(self):
        # The checklist-engine.md Template set table names 6; a discovery step
        # that quietly fell back to counting rows in that table instead of
        # walking the corpus would pass a `>= 6` assertion. Assert `> 6`
        # specifically so that regression is visible here, not just in prose.
        assert len(SHIPPED_TEMPLATES) > 6


class TestCorpusSweepFindings:
    """Measures; fixes nothing (the handoff is explicit: a later wave decides
    what to do about a shipped template that fails the lint). This test's job
    is only that the sweep actually RAN over the whole population -- every
    template gets a real validate() call, and the total is asserted against
    the population size so a short-circuited sweep cannot look complete.

    The measured findings themselves (23 faults, 8 of 12 templates), written
    out in full, live in IMPLEMENTER_RESULT.md -- the two assertions below
    pin the totals so a regression in the checker (or a template edit that
    changes the count) is visible here, not just in that prose."""

    def test_every_template_is_actually_validated(self):
        results = {p: vs.validate_file(p, repo_root=ROOT) for p in SHIPPED_TEMPLATES}
        assert len(results) == len(SHIPPED_TEMPLATES)
        assert set(results) == set(SHIPPED_TEMPLATES)
        # No assertion that every template is clean -- g3 measures, it does
        # not fix. See IMPLEMENTER_RESULT.md for the findings this produced.

    def test_measured_finding_totals(self):
        results = {p: vs.validate_file(p, repo_root=ROOT) for p in SHIPPED_TEMPLATES}
        clean = [p for p, faults in results.items() if not faults]
        all_faults = [f for faults in results.values() for f in faults]
        by_code = {}
        for f in all_faults:
            by_code[f.code] = by_code.get(f.code, 0) + 1

        # A floor on how many templates are clean, not an exact count: a
        # future template gaining a real check should never make this red.
        assert len(clean) >= 4, f"only {len(clean)} of {len(SHIPPED_TEMPLATES)} templates are clean: {[p.name for p in clean]}"
        # The two faults measured live in the shipped corpus today. Pinned so
        # a checker regression (a fault that stops firing) is visible here --
        # if a template is genuinely fixed, this count drops and the pin
        # should move down in the same edit, never silently.
        assert by_code.get("falsifiable-all-null", 0) >= 15, (
            f"expected at least 15 all-null gates across the corpus (measured 17 at "
            f"authoring time -- epic-569/w3-promote g1 cleared init/reconcile's "
            f"single-postcondition all-null gates in COMMANDER_SPINE.template.json, "
            f"dropping the prior 19), found {by_code.get('falsifiable-all-null', 0)}: this is "
            f"the epic's central claim (#518) -- a drop this large means the checker "
            f"stopped finding what it exists to find, not that the corpus improved that "
            f"much between edits"
        )
        assert by_code.get("falsifiable-unresolved-placeholder", 0) >= 2, (
            f"expected at least 2 unresolved `<exact test command>` scaffold "
            f"placeholders (EXECUTE_PLAN.template.json, IMPLEMENTER_PLAN.template.json), "
            f"found {by_code.get('falsifiable-unresolved-placeholder', 0)}"
        )


# --------------------------------------------------------------------------- #
# decision:match-shape-bare-list widening (#371): a non-dict `match` is now a
# blocking SHAPE fault (never the falsifiable/report-only family), and a
# malformed list-valued match[k] (empty, or a non-scalar element) is a
# report-only falsifiable fault that must never affect `bool(result)`.
# --------------------------------------------------------------------------- #

class TestShapeRejectsArtifactMatchNotDict:
    def test_list_valued_match_itself_is_not_the_shape_fault(self):
        # A list-valued match (membership) is the WIDENED, legal shape --
        # only a match that is present but not a dict at all is the fault.
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"][0]["check"] = {
            "kind": "artifact", "evidence_type": "review-result", "match": {"verdict": ["APPROVE", "BLOCK"]},
        }
        faults = vs.validate(spine)
        assert "shape-artifact-match-not-dict" not in _codes(faults)

    def test_non_dict_match_is_a_blocking_shape_fault(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"][0]["check"] = {
            "kind": "artifact", "evidence_type": "review-result", "match": ["APPROVE", "BLOCK"],
        }
        result = vs.validate(spine)
        assert "shape-artifact-match-not-dict" in _codes(result)
        assert result  # blocking: in the base list, bool(result) is True
        assert not result.report_only

    def test_no_match_at_all_is_not_this_fault(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"][0]["check"] = {
            "kind": "artifact", "evidence_type": "user-decision",
        }
        assert "shape-artifact-match-not-dict" not in _codes(vs.validate(spine))

    def test_non_artifact_kind_is_not_this_fault(self):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"][0]["check"] = {"kind": "command", "command": "true"}
        assert "shape-artifact-match-not-dict" not in _codes(vs.validate(spine))


class TestFalsifiabilityArtifactMalformedMatchListBoundary:
    """VIOLATING / INNOCENT, per the handoff's malformed-list definition
    (decision:malformed-list-definition): empty or non-scalar element is
    malformed; a single-element list is NOT flagged."""

    def _faults(self, match):
        check = {"kind": "artifact", "evidence_type": "review-result", "match": match}
        return vs._fault_artifact_malformed_match_list("g1.postconditions.c1", check)

    def test_empty_list_is_malformed(self):
        assert self._faults({"verdict": []})

    def test_non_scalar_element_is_malformed(self):
        assert self._faults({"verdict": [{"nested": "dict"}]})

    def test_single_element_list_is_not_flagged(self):
        assert not self._faults({"verdict": ["APPROVE"]})

    def test_multi_element_scalar_list_is_not_flagged(self):
        assert not self._faults({"verdict": ["APPROVE", "BLOCK"]})

    @pytest.mark.parametrize("scalar", ["s", 1, 1.5, True, None])
    def test_every_json_scalar_type_is_accepted(self, scalar):
        assert not self._faults({"k": [scalar, scalar]})

    def test_scalar_match_value_untouched(self):
        assert not self._faults({"verdict": "APPROVE"})

    def test_non_dict_match_is_not_this_faults_job(self):
        # The non-dict case is `shape-artifact-match-not-dict`'s job, not this
        # one's -- this function is defensive and returns nothing for it.
        assert not self._faults(["APPROVE", "BLOCK"])


class TestReportOnlyChannelNeverFlipsExitCode:
    """decision:widening-ships-live-refusal-ships-report-only: the malformed-
    list fault is computed but never blocks -- `ValidationResult.report_only`
    carries it, `bool(result)`/the base list/`main()`'s exit code do not see
    it, exactly like `generate_spine.py`/`spine_lifecycle.py`'s own
    `if result:` / `if result.undecidable or result:` call sites."""

    def _gated_with_match(self, match):
        spine = _valid_gated()
        spine["tasks"]["g1"]["postconditions"][0]["check"] = {
            "kind": "artifact", "evidence_type": "review-result", "match": match,
        }
        return spine

    def test_empty_list_match_lands_in_report_only_not_base(self):
        result = vs.validate(self._gated_with_match({"verdict": []}))
        assert "falsifiable-artifact-malformed-match-list" not in _codes(result)
        assert "falsifiable-artifact-malformed-match-list" in _codes(result.report_only)

    def test_empty_list_match_does_not_flip_bool_or_len(self):
        result = vs.validate(self._gated_with_match({"verdict": []}))
        assert len(result) == 0
        assert bool(result) is False

    def test_report_only_fault_code_is_in_the_named_set(self):
        assert "falsifiable-artifact-malformed-match-list" in vs.REPORT_ONLY_FAULT_CODES

    def test_cli_prints_report_only_but_exit_code_stays_zero(self, tmp_path, capsys):
        spine = self._gated_with_match({"verdict": []})
        p = tmp_path / "spine.json"
        p.write_text(json.dumps(spine))
        exit_code = vs.main([str(p), "--root", str(ROOT)])
        out = capsys.readouterr().out
        assert exit_code == 0
        assert "REPORT-ONLY" in out

    def test_two_arg_validation_result_construction_still_works(self):
        # Both existing 2-arg call sites inside validate() itself must keep
        # working unchanged -- report_only defaults to empty.
        result = vs.ValidationResult([], [])
        assert result.report_only == []
        assert not result

    def test_str_names_report_only_when_present(self):
        result = vs.validate(self._gated_with_match({"verdict": []}))
        assert "report-only" in str(result).lower()

    def test_str_of_a_genuinely_sound_result_does_not_claim_report_only(self):
        result = vs.validate(_valid_gated())
        assert not result.report_only
        assert "report-only" not in str(result).lower()
