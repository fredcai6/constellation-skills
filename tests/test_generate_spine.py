"""Tests for scripts/generate_spine.py -- the spine spec compiler and generator.

Frozen contract: .agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md. Where a
test encodes a choice the design note leaves silent, the choice and its rationale are
named in the test's own docstring/comment, and restated in IMPLEMENTER_RESULT.md.
"""

from __future__ import annotations

import ast
import copy
import json
import shlex
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import checklist_engine  # noqa: E402
import generate_spine as gs  # noqa: E402
from validate_spine import ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH, validate  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixture builders -- minimal valid spec dicts (already TOML-parsed shape),
# one per check kind, plus a minimal full spec.
# --------------------------------------------------------------------------- #

def _qualitative_cond(id_="c1", statement="reviewer read the diff", because="no automatable signal exists"):
    return {"id": id_, "statement": statement, "kind": "qualitative", "because": because}


def _pytest_cond(id_="c1", statement="tests pass", selector="Door or Tie", min_collect=4, targets=None,
                  not_yet_written=None):
    d = {"id": id_, "statement": statement, "kind": "pytest", "selector": selector, "min_collect": min_collect}
    if targets is not None:
        d["targets"] = targets
    if not_yet_written is not None:
        d["not_yet_written"] = not_yet_written
    return d


def _script_cond(id_="c1", statement="flag exists", path="scripts/foo.py", args=None):
    d = {"id": id_, "statement": statement, "kind": "script", "path": path}
    if args is not None:
        d["args"] = args
    return d


def _population_cond(id_="c1", statement="count matches", root="specs", glob="*.toml", expected=3):
    return {"id": id_, "statement": statement, "kind": "population", "root": root, "glob": glob, "expected": expected}


def _artifact_cond(id_="c1", statement="human decided", evidence_type="user-decision", match=None):
    d = {"id": id_, "statement": statement, "kind": "artifact", "evidence_type": evidence_type}
    if match is not None:
        d["match"] = match
    return d


def _gate(id_="m1", title="do it", imperative="do the thing", postconditions=None, preconditions=None,
          constraints=None, claim=None):
    g = {"id": id_, "title": title, "imperative": imperative}
    if postconditions is not None:
        g["postconditions"] = postconditions
    if preconditions is not None:
        g["preconditions"] = preconditions
    if constraints is not None:
        g["constraints"] = constraints
    if claim is not None:
        g["claim"] = claim
    return g


def _spec(gates=None, *, work_id="w1", type_="gated", config_ref="docs/agents/engine-config.json", parent=None):
    spec = {
        "work_id": work_id,
        "type": type_,
        "config_ref": config_ref,
        "gate": gates if gates is not None else [_gate(postconditions=[_qualitative_cond()])],
    }
    if parent is not None:
        spec["parent"] = parent
    return spec


# --------------------------------------------------------------------------- #
# CHECK_KINDS
# --------------------------------------------------------------------------- #

class TestCheckKinds:
    def test_closed_vocabulary(self):
        assert gs.CHECK_KINDS == ("qualitative", "pytest", "script", "population", "artifact")


# --------------------------------------------------------------------------- #
# _RESOLVER_OWNED_TOKEN_RE -- carried finding from g1's cold review: the
# import from init_work_area sat unused (an ast.Name walk found no reference
# to it anywhere in generate_spine.py). DESIGN_NOTE.md section 4 cites it in
# prose to justify emitting "<repo-root>" unresolved; this pins that claim as
# a runtime-checked fact rather than a sentence.
# --------------------------------------------------------------------------- #

class TestResolverOwnedTokenRegex:
    def test_repo_root_token_matches(self):
        assert gs._RESOLVER_OWNED_TOKEN_RE.fullmatch("<repo-root>")

    def test_non_resolver_token_does_not_match(self):
        assert gs._RESOLVER_OWNED_TOKEN_RE.fullmatch("<exact test command>") is None


# --------------------------------------------------------------------------- #
# compile_condition -- one class per kind, exact compiled output
# --------------------------------------------------------------------------- #

class TestCompileQualitative:
    def test_check_is_null_and_because_appended(self):
        cond = _qualitative_cond(statement="reviewer read the diff", because="nothing automatable exists")
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        assert out["check"] is None
        assert out["statement"] == "reviewer read the diff -- QUALITATIVE: nothing automatable exists"
        assert out["id"] == "c1"
        assert out["satisfied"] is False

    def test_pure_no_filesystem_symbols(self):
        # Documented, not executed: purity is a property of the source, so this
        # asserts the function object carries no reference to banned globals.
        import inspect
        src = inspect.getsource(gs.compile_condition)
        for banned in ("open(", "subprocess.", "Path("):
            assert banned not in src


class TestCompilePytest:
    def test_default_min_collect_and_no_targets(self):
        cond = _pytest_cond(selector="Door or Tie", targets=None)
        del cond["min_collect"]
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        chk = out["check"]
        assert chk["kind"] == "command"
        cmd = chk["command"]
        assert cmd.startswith("cd <repo-root> && ")
        assert "test $(python -m pytest -q -k" in cmd
        assert "--collect-only" in cmd
        assert "-ge 1" in cmd  # default min_collect
        assert shlex.quote("Door or Tie") in cmd

    def test_selector_quoted_and_targets_joined(self):
        cond = _pytest_cond(selector="a or b", min_collect=4, targets=["tests/test_registry.py", "tests/test_door.py"])
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        cmd = out["check"]["command"]
        assert "-ge 4" in cmd
        assert "tests/test_registry.py tests/test_door.py" in cmd
        # the collect segment and the run segment each carry the selector once
        assert cmd.count(shlex.quote("a or b")) == 2

    def test_dangerous_selector_is_shell_quoted(self):
        # defect 1's own shape: a selector containing shell metacharacters must
        # never appear unquoted in the compiled command.
        cond = _pytest_cond(selector="Door and not $(rm -rf /)")
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        cmd = out["check"]["command"]
        assert "$(rm -rf /)" not in cmd or shlex.quote(cond["selector"]) in cmd
        assert shlex.quote(cond["selector"]) in cmd


class TestCompileScript:
    def test_no_args(self):
        cond = _script_cond(path="scripts/foo.py")
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        assert out["check"] == {"kind": "command", "command": "cd <repo-root> && python scripts/foo.py"}

    def test_args_joined_with_shlex(self):
        cond = _script_cond(path="scripts/foo.py", args=["--flag", "value with space"])
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        cmd = out["check"]["command"]
        assert cmd == "cd <repo-root> && python " + shlex.join(["scripts/foo.py", "--flag", "value with space"])


class TestCompilePopulation:
    def test_exact_count(self):
        cond = _population_cond(root="specs", glob="*.toml", expected=3)
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        cmd = out["check"]["command"]
        assert cmd.startswith("cd <repo-root> && ")
        assert "pathlib.Path(sys.argv[1]).glob(sys.argv[2])" in cmd
        assert shlex.quote("specs") in cmd
        assert shlex.quote("*.toml") in cmd
        assert "-eq 3" in cmd

    def test_band_form(self):
        cond = {"id": "c1", "statement": "band", "kind": "population", "root": "specs", "glob": "*.toml",
                "expected_min": 2, "expected_max": 5}
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        cmd = out["check"]["command"]
        assert "-ge 2" in cmd
        assert "-le 5" in cmd

    def test_probed_command_is_the_same_command_shipped(self, tmp_path):
        # Section 4's whole point: one implementation. Build a real dir tree,
        # execute the COMPILED command string itself, and confirm it agrees
        # with the declared count -- no separate Python-side glob.
        (tmp_path / "specs").mkdir()
        for name in ("a.toml", "b.toml", "c.toml"):
            (tmp_path / "specs" / name).write_text("", encoding="utf-8")
        # repo_root_token is the real tmp_path here, so the compiled command
        # is already anchored there -- no substitution needed.
        cond = _population_cond(root="specs", glob="*.toml", expected=3)
        out = gs.compile_condition(cond, repo_root_token=str(tmp_path))
        cmd = out["check"]["command"]
        proc = subprocess.run(["bash", "-c", cmd], cwd=str(tmp_path), capture_output=True)
        assert proc.returncode == 0, proc.stderr


class TestCompileArtifact:
    def test_passthrough_with_match(self):
        cond = _artifact_cond(evidence_type="review-result", match={"verdict": "APPROVE"})
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        assert out["check"] == {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}

    def test_user_decision_exempt_from_match(self):
        assert "user-decision" in ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH
        cond = _artifact_cond(evidence_type="user-decision", match=None)
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        assert out["check"]["kind"] == "artifact"
        assert out["check"]["evidence_type"] == "user-decision"

    def test_imports_not_redeclares_exception_set(self):
        import inspect
        src = inspect.getsource(gs)
        assert "ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH = " not in src


# --------------------------------------------------------------------------- #
# compile_spec -- compiler-supplied defaults
# --------------------------------------------------------------------------- #

class TestCompilerDefaults:
    def test_top_level_defaults(self):
        spec = _spec()
        spine = gs.compile_spec(spec)
        assert spine["consolidation"] is None
        assert spine["triage_candidates"] == []
        assert spine["blockers"] == []
        assert spine["items"] == ["m1"]
        assert spine["work_id"] == "w1"
        assert spine["type"] == "gated"

    def test_task_defaults_when_gate_has_no_preconditions(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        spine = gs.compile_spec(spec)
        t = spine["tasks"]["m1"]
        assert t["preconditions"] == []
        assert t["status"] == "pending"
        assert t["status_detail"] == {}
        assert t["result"] is None
        assert t["finding"] is None
        assert t["evidence"] == []
        assert t["rework_count"] == 0
        assert t["child_checklist"] is None

    def test_condition_satisfied_defaults_false(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        spine = gs.compile_spec(spec)
        cond = spine["tasks"]["m1"]["postconditions"][0]
        assert cond["satisfied"] is False

    def test_items_order_is_gate_order(self):
        spec = _spec(gates=[
            _gate(id_="m1", postconditions=[_qualitative_cond()]),
            _gate(id_="m2", postconditions=[_qualitative_cond()]),
            _gate(id_="m0", postconditions=[_qualitative_cond()]),
        ])
        spine = gs.compile_spec(spec)
        assert spine["items"] == ["m1", "m2", "m0"]

    def test_pure_no_filesystem_symbols(self):
        import inspect
        src = inspect.getsource(gs.compile_spec)
        for banned in ("open(", "subprocess.", "Path("):
            assert banned not in src


# --------------------------------------------------------------------------- #
# Handback contract (DESIGN_NOTE.md section 5) -- every gate, unconditionally
# --------------------------------------------------------------------------- #

class TestHandback:
    def test_every_gate_carries_the_handback_contract(self):
        spec = _spec(gates=[
            _gate(id_="m1", postconditions=[_qualitative_cond()]),
            _gate(id_="m2", postconditions=[_qualitative_cond()]),
        ])
        spine = gs.compile_spec(spec)
        for gid in ("m1", "m2"):
            handback = spine["tasks"][gid]["directives"]["handback"]
            assert handback["belief_worth_recording"].startswith("spine_evidence attach")
            assert handback["open_question_out_of_scope"].startswith("spine_capture flag-candidate")
            assert handback["concern_that_must_stop_this_gate"].startswith("spine_halt block")
            assert "purpose" in handback
            assert "note" in handback

    def test_hand_back_to_names_parent_when_declared(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])], parent="admiral-epic-418-followon")
        spine = gs.compile_spec(spec)
        assert spine["tasks"]["m1"]["directives"]["handback"]["hand_back_to"] == "admiral-epic-418-followon"

    def test_hand_back_to_defaults_to_unknown(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        spine = gs.compile_spec(spec)
        assert spine["tasks"]["m1"]["directives"]["handback"]["hand_back_to"] == "unknown"

    def test_handback_has_no_writable_arrays(self):
        # The whole point of section 5: no beliefs/concerns/open_questions
        # array field that no engine verb ever appends to.
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        spine = gs.compile_spec(spec)
        handback = spine["tasks"]["m1"]["directives"]["handback"]
        for leaf in handback.values():
            assert not isinstance(leaf, list)


# --------------------------------------------------------------------------- #
# Claim escalation (DESIGN_NOTE.md section 6) -- `type_="gated"` (the `_spec()`
# default) throughout this class. `gated` behaviour is UNCHANGED by the g2
# rework round 2 fix below: `advance()` checks every postcondition with no
# kind filter, so injecting c-escalation here is genuinely load-bearing. The
# `survey` side (where it is NOT) is TestClaimEscalationOnSurvey below.
# --------------------------------------------------------------------------- #

class TestClaimEscalation:
    def test_large_claim_injects_c_escalation_postcondition(self):
        spec = _spec(gates=[_gate(
            postconditions=[_qualitative_cond()],
            claim={"magnitude": "large", "text": "this rewires the auth layer"},
        )])
        spine = gs.compile_spec(spec)
        posts = spine["tasks"]["m1"]["postconditions"]
        esc = next(c for c in posts if c["id"] == "c-escalation")
        assert esc["check"] == {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}
        assert "this rewires the auth layer" in esc["statement"]
        assert esc["satisfied"] is False

    def test_large_claim_renders_directives_claim(self):
        spec = _spec(gates=[_gate(
            postconditions=[_qualitative_cond()],
            claim={"magnitude": "large", "text": "this rewires the auth layer"},
        )])
        spine = gs.compile_spec(spec)
        claim = spine["tasks"]["m1"]["directives"]["claim"]
        assert claim["magnitude"] == "large"
        assert claim["text"] == "this rewires the auth layer"
        # g2 rework round 2: the enforced reading, naming the injected condition.
        assert claim["enforcement"] == gs.CLAIM_ENFORCEMENT_GATED
        assert "c-escalation" in claim["enforcement"]
        assert "advance()" in claim["enforcement"]

    def test_normal_magnitude_injects_nothing(self):
        spec = _spec(gates=[_gate(
            postconditions=[_qualitative_cond()],
            claim={"magnitude": "normal", "text": "routine"},
        )])
        spine = gs.compile_spec(spec)
        posts = spine["tasks"]["m1"]["postconditions"]
        assert not any(c["id"] == "c-escalation" for c in posts)
        assert "claim" not in spine["tasks"]["m1"]["directives"]

    def test_no_claim_table_injects_nothing(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        spine = gs.compile_spec(spec)
        assert "claim" not in spine["tasks"]["m1"]["directives"]

    def test_rolls_up_onto_last_gate_keyed_by_source(self):
        spec = _spec(gates=[
            _gate(id_="m1", postconditions=[_qualitative_cond()],
                  claim={"magnitude": "large", "text": "claim one"}),
            _gate(id_="m2", postconditions=[_qualitative_cond()]),
            _gate(id_="m3", postconditions=[_qualitative_cond()]),
        ])
        spine = gs.compile_spec(spec)
        assert "claims_rollup" not in spine["tasks"]["m1"]["directives"]
        assert "claims_rollup" not in spine["tasks"]["m2"]["directives"]
        rollup = spine["tasks"]["m3"]["directives"]["claims_rollup"]
        assert "m1" in rollup
        assert rollup["m1"]["text"] == "claim one"
        assert rollup["m1"]["enforcement"] == gs.CLAIM_ENFORCEMENT_GATED

    def test_no_rollup_key_when_no_large_claims(self):
        spec = _spec(gates=[
            _gate(id_="m1", postconditions=[_qualitative_cond()]),
            _gate(id_="m2", postconditions=[_qualitative_cond()]),
        ])
        spine = gs.compile_spec(spec)
        assert "claims_rollup" not in spine["tasks"]["m2"]["directives"]


# --------------------------------------------------------------------------- #
# Claim escalation on a `survey` spec (g2 rework round 2) -- the cold review's
# finding: `checklist_engine.record()` on a survey item evaluates only
# command-kind postconditions and `consolidate()` reads only `result`, so an
# injected artifact-kind c-escalation would be silently inert there. The fix:
# inject NOTHING on a survey spec, and make the non-enforcement loud in
# `directives.claim.enforcement` / `directives.claims_rollup[*].enforcement`
# instead of enforcing it falsely.
# --------------------------------------------------------------------------- #

class TestClaimEscalationOnSurvey:
    def test_large_claim_injects_no_postcondition(self):
        spec = _spec(type_="survey", gates=[_gate(
            postconditions=[_qualitative_cond()],
            claim={"magnitude": "large", "text": "the Fowler-pass verdict spans the entire diff"},
        )])
        spine = gs.compile_spec(spec)
        posts = spine["tasks"]["m1"]["postconditions"]
        assert not any(c["id"] == "c-escalation" for c in posts)
        assert len(posts) == 1  # only the qualitative postcondition the fixture already carried

    def test_large_claim_renders_directives_claim_with_non_enforcement(self):
        spec = _spec(type_="survey", gates=[_gate(
            postconditions=[_qualitative_cond()],
            claim={"magnitude": "large", "text": "the Fowler-pass verdict spans the entire diff"},
        )])
        spine = gs.compile_spec(spec)
        claim = spine["tasks"]["m1"]["directives"]["claim"]
        assert claim["magnitude"] == "large"
        assert claim["text"] == "the Fowler-pass verdict spans the entire diff"
        assert claim["enforcement"] == gs.CLAIM_ENFORCEMENT_SURVEY
        # Names the actual mechanism, not just "not enforced" -- the whole
        # point of stating a limit truthfully instead of a vague disclaimer.
        assert "record()" in claim["enforcement"]
        assert "command-kind" in claim["enforcement"]
        assert "consolidate()" in claim["enforcement"]
        assert "result" in claim["enforcement"]

    def test_rollup_carries_enforcement_on_survey(self):
        spec = _spec(type_="survey", gates=[
            _gate(id_="m1", postconditions=[_qualitative_cond()],
                  claim={"magnitude": "large", "text": "claim one"}),
            _gate(id_="m2", postconditions=[_qualitative_cond()]),
        ])
        spine = gs.compile_spec(spec)
        rollup = spine["tasks"]["m2"]["directives"]["claims_rollup"]
        assert rollup["m1"]["text"] == "claim one"
        assert rollup["m1"]["enforcement"] == gs.CLAIM_ENFORCEMENT_SURVEY

    def test_gated_and_survey_enforcement_text_differ(self):
        # The two cases must be told apart by CONTENT, not by absence (the
        # handoff's explicit ask) -- the two constants must genuinely diverge.
        assert gs.CLAIM_ENFORCEMENT_GATED != gs.CLAIM_ENFORCEMENT_SURVEY


# --------------------------------------------------------------------------- #
# Driven proof (g2 rework round 2, close criterion 4): the round-1 evidence
# gap this rework answers is that the escalation's SHAPE was dumped from
# compile_spec's output but never actually driven through
# checklist_engine.record/consolidate/advance. This drives both a `survey`
# spec and a `gated` spec through the REAL engine verbs and asserts the
# outcome matches what directives.claim.enforcement says it will be -- not
# what compile_spec's dict shape merely suggests it will be.
# --------------------------------------------------------------------------- #

class TestClaimEnforcementDrivenThroughEngine:
    def test_survey_large_claim_consolidates_approve_with_nothing_attached(self):
        # CLAIM_ENFORCEMENT_SURVEY says this is exactly what happens: no
        # postcondition was injected, so nothing on the record()/consolidate()
        # path ever looks for a review-result -- consolidate() APPROVEs a
        # survey whose large-claim item was never independently reviewed.
        spec = _spec(type_="survey", gates=[_gate(
            id_="r1",
            postconditions=[_qualitative_cond()],
            claim={"magnitude": "large", "text": "the Fowler-pass verdict spans the entire diff"},
        )])
        spine = gs.compile_spec(spec)
        assert not any(c["id"] == "c-escalation" for c in spine["tasks"]["r1"]["postconditions"])
        # No evidence attached anywhere -- exactly the "no independent reviewer
        # ever approved this" scenario the cold review flagged as silently
        # passing on a survey gate.
        assert spine["tasks"]["r1"]["evidence"] == []

        msg = checklist_engine.record(spine, "r1", "pass", None)
        assert msg == "r1 recorded pass"
        assert spine["tasks"]["r1"]["status"] == "complete"

        msg = checklist_engine.consolidate(spine, "APPROVE", None, None)
        assert spine["consolidation"]["verdict"] == "APPROVE"
        assert "APPROVE" in msg
        # This is the measured behaviour CLAIM_ENFORCEMENT_SURVEY describes,
        # not a hoped-for one: consolidate() never raised, never asked for an
        # override, never looked at a (nonexistent) c-escalation.

    def test_gated_large_claim_blocks_advance_until_review_result_attached(self):
        # The contrasting, enforced case: CLAIM_ENFORCEMENT_GATED says
        # advance() checks every postcondition with no kind filter, so this
        # gate genuinely cannot close without an attached APPROVE.
        spec = _spec(type_="gated", gates=[_gate(
            id_="m1",
            postconditions=[_qualitative_cond()],
            claim={"magnitude": "large", "text": "this rewires the auth layer"},
        )])
        spine = gs.compile_spec(spec)
        assert any(c["id"] == "c-escalation" for c in spine["tasks"]["m1"]["postconditions"])

        checklist_engine.start(spine, "m1")
        checklist_engine.attest(spine, "m1", "c1", "postconditions", "verified by hand")
        with pytest.raises(checklist_engine.EngineError) as excinfo:
            checklist_engine.advance(spine, "m1", mechanical=True)
        assert "c-escalation" in str(excinfo.value)

        checklist_engine.attach(spine, "m1", "review-result", {"verdict": "APPROVE"})
        msg = checklist_engine.advance(spine, "m1", mechanical=True)  # no longer raises
        assert spine["tasks"]["m1"]["status"] == "complete"
        assert "complete" in msg


# --------------------------------------------------------------------------- #
# Spec-shape faults (DESIGN_NOTE.md section 7) -- refused before any probe
# --------------------------------------------------------------------------- #

class TestSpecShapeFaults:
    def test_clean_spec_has_no_faults(self):
        # A single qualitative postcondition would itself trip
        # spec-all-qualitative-postconditions (below), so "clean" here uses a
        # real check -- the shared _spec()/_gate() defaults elsewhere in this
        # file are deliberately all-qualitative and are never run through
        # spec_shape_faults, only compile_spec, so they do not need to dodge
        # this rule.
        spec = _spec(gates=[_gate(postconditions=[_pytest_cond()])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert faults == []

    def test_unknown_check_kind(self):
        spec = _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "x", "kind": "raw-command", "command": "echo hi"}
        ])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-unknown-check-kind" for f in faults)

    def test_missing_field(self):
        spec = _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "x", "kind": "pytest"}  # no selector
        ])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-missing-field" for f in faults)

    def test_empty_because(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond(because="")])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-empty-because" for f in faults)

    def test_gated_missing_postconditions(self):
        spec = _spec(gates=[_gate(postconditions=[])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-gated-missing-postconditions" for f in faults)

    def test_all_qualitative_postconditions(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond(id_="c1"), _qualitative_cond(id_="c2")])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-all-qualitative-postconditions" for f in faults)
        assert any("falsifiable-all-null" in f.message for f in faults)

    def test_not_all_qualitative_is_clean(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond(id_="c1"), _pytest_cond(id_="c2")])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert not any(f.code == "spec-all-qualitative-postconditions" for f in faults)

    def test_duplicate_gate_id(self):
        spec = _spec(gates=[
            _gate(id_="m1", postconditions=[_qualitative_cond()]),
            _gate(id_="m1", postconditions=[_qualitative_cond()]),
        ])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-duplicate-gate-id" for f in faults)

    def test_duplicate_condition_id_across_pre_and_post(self):
        spec = _spec(gates=[_gate(
            preconditions=[_qualitative_cond(id_="c1")],
            postconditions=[_qualitative_cond(id_="c1")],
        )])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-duplicate-condition-id" for f in faults)

    def test_reserved_id(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond(id_="c-escalation")])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-reserved-id" for f in faults)

    def test_config_ref_not_json(self, tmp_path):
        bad = tmp_path / "not_json.toml"
        bad.write_text("this = 'is toml, not json'\n", encoding="utf-8")
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        spec["config_ref"] = "not_json.toml"
        faults = gs.spec_shape_faults(spec, repo_root=tmp_path)
        assert any(f.code == "spec-config-ref-not-json" for f in faults)

    def test_config_ref_valid_json_is_clean(self, tmp_path):
        good = tmp_path / "config.json"
        good.write_text("{}", encoding="utf-8")
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        spec["config_ref"] = "config.json"
        faults = gs.spec_shape_faults(spec, repo_root=tmp_path)
        assert not any(f.code == "spec-config-ref-not-json" for f in faults)

    # -- m1's second task: `[[gate.claim]]` (array-of-tables) parses to a
    # `list`, not the `dict` compile_spec expects; without a named fault this
    # reaches `(g.get("claim") or {}).get("magnitude")` as an unhandled
    # `AttributeError: 'list' object has no attribute 'get'`.
    def test_claim_array_of_tables_is_a_named_fault_not_a_crash(self):
        spec = _spec(gates=[_gate(
            postconditions=[_qualitative_cond()],
            claim=[{"magnitude": "large", "text": "x"}],
        )])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-malformed-claim" for f in faults)

    def test_claim_bad_magnitude(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()],
                                   claim={"magnitude": "huge", "text": "x"})])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-malformed-claim" for f in faults)

    def test_claim_large_missing_text(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()],
                                   claim={"magnitude": "large"})])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-malformed-claim" for f in faults)

    def test_claim_normal_is_clean(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()],
                                   claim={"magnitude": "normal"})])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert not any(f.code == "spec-malformed-claim" for f in faults)

    def test_claim_large_with_text_is_clean(self):
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()],
                                   claim={"magnitude": "large", "text": "big deal"})])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert not any(f.code == "spec-malformed-claim" for f in faults)


# --------------------------------------------------------------------------- #
# Numeric field type faults -- rework Blocker 1/2. `selector`, `targets`,
# `path`, `args`, `root`, `glob` are all shlex.quote'd/shlex.join'd; the four
# NUMERIC fields (population.expected/expected_min/expected_max,
# pytest.min_collect) are interpolated unquoted and untyped, so a string value
# compiles a check that cannot fail: `{"kind":"population","root":".",
# "glob":"*.py","expected":"1 || echo PWNED"}` -> `test $(...) -eq 1 || echo
# PWNED`, exit 0 regardless of the count (verified live against a real shell:
# `test $(echo 99) -eq 1 || echo PWNED` exits 0). VIOLATING/INNOCENT modeled on
# tests/test_mcp_adoption.py::_cli_only_verb_violations, per DESIGN_NOTE.md
# section 9 / the rework handoff's Blocker 2 -- a guard proven only against an
# INNOCENT case is the same defect one tier up: absence does not announce
# itself.
# --------------------------------------------------------------------------- #

class TestNumericFieldTypeFaults:
    #: The Admiral's own repro, verbatim, through spec_shape_faults (not just
    #: compile_condition) -- before this fix it returned no faults at all.
    def test_admiral_repro_population_expected_injection_is_now_refused(self):
        spec = _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "count matches", "kind": "population",
             "root": ".", "glob": "*.py", "expected": "1 || echo PWNED"},
        ])])
        faults = gs.spec_shape_faults(spec, repo_root=ROOT)
        assert any(f.code == "spec-non-integer-field" for f in faults), faults

    VIOLATING = {
        "population expected -- shell injection string": _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "x", "kind": "population", "root": ".", "glob": "*.py",
             "expected": "1 || echo PWNED"},
        ])]),
        "population expected_min -- non-integer string": _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "x", "kind": "population", "root": ".", "glob": "*.py",
             "expected_min": "1 || echo PWNED", "expected_max": 5},
        ])]),
        "population expected_max -- non-integer string": _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "x", "kind": "population", "root": ".", "glob": "*.py",
             "expected_min": 1, "expected_max": "5 || echo PWNED"},
        ])]),
        "population expected -- float, not int": _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "x", "kind": "population", "root": ".", "glob": "*.py",
             "expected": 1.5},
        ])]),
        "population expected -- bool, not int (isinstance(True, int) is True in Python)": _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "x", "kind": "population", "root": ".", "glob": "*.py",
             "expected": True},
        ])]),
        "pytest min_collect -- shell injection string": _spec(gates=[_gate(
            postconditions=[_pytest_cond(min_collect="1; echo PWNED")],
        )]),
        "pytest min_collect -- bool, not int": _spec(gates=[_gate(
            postconditions=[_pytest_cond(min_collect=False)],
        )]),
    }

    INNOCENT = {
        "population expected -- valid int": _spec(gates=[_gate(postconditions=[_population_cond(expected=3)])]),
        "population band -- valid ints": _spec(gates=[_gate(postconditions=[
            {"id": "c1", "statement": "band", "kind": "population", "root": "specs", "glob": "*.toml",
             "expected_min": 2, "expected_max": 5},
        ])]),
        "pytest min_collect -- valid int": _spec(gates=[_gate(postconditions=[_pytest_cond(min_collect=4)])]),
        "pytest min_collect -- absent (default applies)": _spec(gates=[_gate(postconditions=[
            {k: v for k, v in _pytest_cond().items() if k != "min_collect"},
        ])]),
    }

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_violating_is_refused(self, label):
        faults = gs.spec_shape_faults(self.VIOLATING[label], repo_root=ROOT)
        assert any(f.code == "spec-non-integer-field" for f in faults), (label, faults)

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_innocent_is_left_alone(self, label):
        faults = gs.spec_shape_faults(self.INNOCENT[label], repo_root=ROOT)
        assert not any(f.code == "spec-non-integer-field" for f in faults), (label, faults)

    def test_valid_spec_compiled_output_is_unchanged(self):
        # Blocker 1's own constraint: the fix must not change compiled output
        # for a spec whose numeric fields are already valid integers.
        spec = _spec(gates=[_gate(postconditions=[_population_cond(expected=3)])])
        assert gs.spec_shape_faults(spec, repo_root=ROOT) == []
        compiled = gs.compile_spec(spec)
        cmd = compiled["tasks"]["m1"]["postconditions"][0]["check"]["command"]
        assert cmd == "cd <repo-root> && test $(python -c " + shlex.quote(gs._POPULATION_COUNTER_PY) + \
            " " + shlex.quote("specs") + " " + shlex.quote("*.toml") + ") -eq 3"


# --------------------------------------------------------------------------- #
# Blocker 4 (rework handoff): specs/implementer.spine.toml and
# specs/reviewer.spine.toml both shipped with one Admiral session's id
# hardcoded as `parent` -- a reusable role TEMPLATE, not a per-run dispatch
# spec. `shipped_spec_session_specific_parent_faults` is deliberately NOT
# wired into `spec_shape_faults` (a real per-run spec legitimately carries a
# concrete parent); it is exercised directly, here and against the real
# shipped files, per DESIGN_NOTE.md section 9 / Blocker 2's VIOLATING+INNOCENT
# shape.
# --------------------------------------------------------------------------- #

class TestShippedSpecParentGuard:
    #: The EXACT value that shipped -- proves the guard would have caught the
    #: real defect, not just a synthetic stand-in.
    VIOLATING = {
        "the exact prior shipped value": {"parent": "admiral-epic-418-followon"},
        "a different concrete commander session id": {"parent": "constellation/epic-1/x/execute/commander"},
        "not a string at all": {"parent": 12345},
    }

    INNOCENT = {
        "placeholder token": {"parent": "<parent>"},
        "absent": {},
        "explicit None": {"parent": None},
    }

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_violating_is_caught(self, label):
        faults = gs.shipped_spec_session_specific_parent_faults(self.VIOLATING[label])
        assert any(f.code == "spec-shipped-session-specific-parent" for f in faults), (label, faults)

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_innocent_is_left_alone(self, label):
        faults = gs.shipped_spec_session_specific_parent_faults(self.INNOCENT[label])
        assert not faults, (label, faults)

    @pytest.mark.parametrize("spec_name", ["implementer.spine.toml", "reviewer.spine.toml"])
    def test_real_shipped_spec_is_now_clean(self, spec_name):
        spec = tomllib.loads((ROOT / "specs" / spec_name).read_text(encoding="utf-8"))
        faults = gs.shipped_spec_session_specific_parent_faults(spec)
        assert not faults, (spec_name, faults)

    def test_real_shipped_spec_still_carries_a_placeholder_not_silence(self):
        # Absence would also pass the guard, but the intent here is a filled
        # slot, not a dropped field -- pin the actual chosen form.
        for spec_name in ("implementer.spine.toml", "reviewer.spine.toml"):
            spec = tomllib.loads((ROOT / "specs" / spec_name).read_text(encoding="utf-8"))
            assert spec.get("parent") == "<parent>", spec_name


# --------------------------------------------------------------------------- #
# Purity guard on the module boundary itself
# --------------------------------------------------------------------------- #

def _real_toml_spec_text(gate_id="m1", extra_gate_toml="") -> str:
    # c1 is deliberately `artifact`/`user-decision` (no `match`, exempt) rather
    # than `qualitative`: a lone qualitative postcondition would itself trip
    # spec-all-qualitative-postconditions, and artifact carries no probe, so a
    # base spec with no extra_gate_toml compiles and validates cleanly with no
    # live-environment dependency.
    return f'''
work_id = "w1"
type = "gated"
config_ref = "docs/agents/engine-config.json"

[[gate]]
id = "{gate_id}"
title = "do it"
imperative = "do the thing"

  [[gate.postconditions]]
  id = "c1"
  statement = "human decided"
  kind = "artifact"
  evidence_type = "user-decision"
{extra_gate_toml}
'''


def _write_script_fixture(root: Path, rel_path: str, body: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Probes -- one class per kind. VIOLATING/INNOCENT modeled on
# tests/test_mcp_adoption.py::_cli_only_verb_violations; script and population
# additionally carry a POPULATED ACCEPTED_FALSE_ALARM bucket (the two probes
# with no oracle behind them).
# --------------------------------------------------------------------------- #

class TestPytestProbe:
    VIOLATING = {
        "nonsense selector": _pytest_cond(selector="ThisSelectorMatchesNothingAtAll12345", min_collect=1),
        "another nonsense selector": _pytest_cond(selector="NoSuchTestEverExistedZZZ9876", min_collect=1),
    }

    INNOCENT = {
        "real class in this file": _pytest_cond(selector="TestCheckKinds", min_collect=1,
                                                  targets=["tests/test_generate_spine.py"]),
        "another real class in this file": _pytest_cond(selector="TestCompileScript", min_collect=1,
                                                          targets=["tests/test_generate_spine.py"]),
    }

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_violating_is_caught(self, label):
        faults, undecidable = gs._probe_pytest("m1", "c1", self.VIOLATING[label], repo_root=ROOT)
        assert not undecidable, undecidable
        assert any(f.code == "probe-pytest-below-min-collect" for f in faults), (label, faults)

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_innocent_is_left_alone(self, label):
        faults, undecidable = gs._probe_pytest("m1", "c1", self.INNOCENT[label], repo_root=ROOT)
        assert not faults, (label, faults)
        assert not undecidable, (label, undecidable)


# --------------------------------------------------------------------------- #
# Blocker 0 (rework handoff) -- the pytest probe asserted a close-time truth
# at generation time, so the generator could not author a TDD-shaped plan: a
# gate whose own imperative is "write this test" cannot declare a pytest
# postcondition on itself, because at GENERATION time the test does not exist
# yet. `not_yet_written` is the stated declaration (never inferred): well-
# formedness (selector syntax, target existence) is still checked either way;
# only the min_collect/count assertion is deferred to gate-close, where the
# compiled command (UNCHANGED) enforces it strictly. Silence keeps today's
# strict default -- this is VIOLATING both ways per Blocker 2: a wrong
# selector with no declaration must still refuse, and a declared-not-yet-
# written test must not be refused.
# --------------------------------------------------------------------------- #

class TestPytestNotYetWritten:
    # (a) declared + short collect -> Undecidable, not Fault, non-blocking.
    def test_declared_short_collect_is_undecidable_not_fault(self):
        cond = _pytest_cond(selector="ThisSelectorMatchesNothingAtAll12345", min_collect=1, not_yet_written=True)
        faults, undecidable = gs._probe_pytest("m1", "c1", cond, repo_root=ROOT)
        assert not faults, faults
        assert len(undecidable) == 1
        assert undecidable[0].code == "undecidable-pytest-not-yet-written"
        assert undecidable[0].blocking is False

    # (b) declared + malformed selector -> well-formedness still checked, still a Fault.
    def test_declared_malformed_selector_still_faults(self):
        cond = _pytest_cond(selector="TestFoo and (", min_collect=1, not_yet_written=True)
        faults, undecidable = gs._probe_pytest("m1", "c1", cond, repo_root=ROOT)
        assert any(f.code == "probe-pytest-malformed-selector" for f in faults), faults
        assert not undecidable, undecidable

    # (c) declared + a named target that does not exist -> Undecidable, non-blocking, not a Fault.
    def test_declared_missing_target_is_undecidable_not_fault(self):
        cond = _pytest_cond(selector="AnythingAtAll", min_collect=1,
                             targets=["tests/_gs_not_yet_written_target.py"], not_yet_written=True)
        faults, undecidable = gs._probe_pytest("m1", "c1", cond, repo_root=ROOT)
        assert not faults, faults
        assert len(undecidable) == 1
        assert undecidable[0].code == "undecidable-pytest-not-yet-written"
        assert undecidable[0].blocking is False

    # (d) silence + short collect -> unchanged strict Fault (regression pin).
    def test_silence_keeps_strict_default(self):
        cond = _pytest_cond(selector="ThisSelectorMatchesNothingAtAll12345", min_collect=1)
        assert "not_yet_written" not in cond
        faults, undecidable = gs._probe_pytest("m1", "c1", cond, repo_root=ROOT)
        assert not undecidable, undecidable
        assert any(f.code == "probe-pytest-below-min-collect" for f in faults), faults

    # A wrong selector with no declaration must still refuse -- Blocker 2's
    # "both ways" VIOLATING pairing with (a) above.
    def test_no_declaration_wrong_selector_still_refused(self):
        cond = _pytest_cond(selector="NoSuchTestEverExistedZZZ9876", min_collect=1)
        faults, undecidable = gs._probe_pytest("m1", "c1", cond, repo_root=ROOT)
        assert any(f.code == "probe-pytest-below-min-collect" for f in faults), faults

    # (e) the declaration renders on the gate -- a reviewer sees the claim.
    def test_compiled_statement_carries_the_declaration(self):
        cond = _pytest_cond(statement="tests pass", not_yet_written=True)
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        assert "NOT YET WRITTEN" in out["statement"]
        assert out["statement"].startswith("tests pass")

    def test_compiled_statement_unchanged_when_silent(self):
        cond = _pytest_cond(statement="tests pass", not_yet_written=None)
        out = gs.compile_condition(cond, repo_root_token="<repo-root>")
        assert out["statement"] == "tests pass"

    # The compiled CHECK becomes `null` (a manual attest) when declared --
    # `validate_spine.validate()` (out of scope to edit, and the literal
    # last statement before success) unconditionally re-probes any
    # `command`-kind pytest check LIVE and refuses a genuine zero-collect;
    # there is no compiled shape that both keeps a strict command AND
    # survives that oracle check before the test exists. `null` mirrors
    # qualitative's own shape and the shipped IMPLEMENTER_PLAN.template.json's
    # existing TDD-red convention (check:null, never a command, for the
    # by-design-failing step).
    def test_compiled_check_becomes_null_when_declared(self):
        declared = gs.compile_condition(_pytest_cond(not_yet_written=True), repo_root_token="<repo-root>")
        assert declared["check"] is None

    def test_compiled_check_stays_a_strict_command_when_silent(self):
        plain = gs.compile_condition(_pytest_cond(not_yet_written=None), repo_root_token="<repo-root>")
        assert plain["check"]["kind"] == "command"
        assert "pytest" in plain["check"]["command"]

    # (f) end-to-end through main(): this is the actual proof the generator
    # can now author a TDD-shaped plan -- a gate whose test does not exist
    # yet still generates.
    def test_main_writes_the_spine_for_a_not_yet_written_gate(self, tmp_path):
        extra = (
            "\n  [[gate.postconditions]]\n"
            '  id = "c2"\n'
            '  statement = "the new test passes"\n'
            '  kind = "pytest"\n'
            '  selector = "TestThisDoesNotExistYetAtAll"\n'
            "  min_collect = 1\n"
            "  not_yet_written = true\n"
        )
        spec_path = tmp_path / "tdd.spine.toml"
        spec_path.write_text(_real_toml_spec_text(extra_gate_toml=extra), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(ROOT)])
        assert rc == 0, "the generator must be able to author a TDD-shaped plan (Blocker 0)"
        assert out_path.exists()
        written = json.loads(out_path.read_text(encoding="utf-8"))
        posted = written["tasks"]["m1"]["postconditions"][1]
        assert posted["check"] is None
        assert "NOT YET WRITTEN" in posted["statement"]
        assert "TestThisDoesNotExistYetAtAll" in posted["statement"]

    # Same shape, but WITHOUT the declaration -- must still refuse (the
    # control pairing for (f), Blocker 2's "both ways" at the CLI layer).
    def test_main_without_declaration_still_refuses(self, tmp_path):
        extra = (
            "\n  [[gate.postconditions]]\n"
            '  id = "c2"\n'
            '  statement = "the new test passes"\n'
            '  kind = "pytest"\n'
            '  selector = "TestThisDoesNotExistYetAtAll"\n'
            "  min_collect = 1\n"
        )
        spec_path = tmp_path / "no_tdd.spine.toml"
        spec_path.write_text(_real_toml_spec_text(extra_gate_toml=extra), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(ROOT)])
        assert rc == 3
        assert not out_path.exists()


class TestScriptProbe:
    VIOLATING = {
        "unknown flag against a real script":
            ("scripts/_gs_fixture_a.py",
             'import argparse\n\ndef build():\n    p = argparse.ArgumentParser()\n    p.add_argument("--known")\n    return p\n',
             ["--unknown"]),
        "near-miss typo against another real script":
            ("scripts/_gs_fixture_b.py",
             'import argparse\n\ndef build():\n    p = argparse.ArgumentParser()\n    p.add_argument("--work-id")\n    p.add_argument("--session")\n    return p\n',
             ["--session-id"]),
    }

    INNOCENT = {
        "exact match":
            ("scripts/_gs_fixture_c.py",
             'import argparse\n\ndef build():\n    p = argparse.ArgumentParser()\n    p.add_argument("--flag")\n    p.add_argument("--other")\n    return p\n',
             ["--flag", "--other"]),
        "no flags requested at all -- nothing to check":
            ("scripts/_gs_fixture_a.py",
             'import argparse\n\ndef build():\n    p = argparse.ArgumentParser()\n    p.add_argument("--known")\n    return p\n',
             []),
    }

    #: One real, principled limitation, not a bug: DESIGN_NOTE.md section 4 says
    #: the probe collects literals passed as the FIRST positional argument to
    #: add_argument. A short-then-long registration (`add_argument("-f",
    #: "--foo")`) puts the long form SECOND, so a real, legitimately-registered
    #: `--foo` is flagged anyway. Pinned as FIRING (not fixed) so a future
    #: change to the collection rule is a deliberate edit here, exactly the
    #: convention test_mcp_adoption.py's own ACCEPTED_FALSE_ALARM documents.
    ACCEPTED_FALSE_ALARM = {
        "long flag in second position":
            ("scripts/_gs_fixture_d.py",
             'import argparse\n\ndef build():\n    p = argparse.ArgumentParser()\n    p.add_argument("-f", "--foo")\n    return p\n',
             ["--foo"]),
    }

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_violating_is_caught(self, label, tmp_path):
        rel_path, body, args = self.VIOLATING[label]
        _write_script_fixture(tmp_path, rel_path, body)
        cond = _script_cond(path=rel_path, args=args)
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert not undecidable, (label, undecidable)
        assert any(f.code == "probe-script-unknown-flag" for f in faults), (label, faults)

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_innocent_is_left_alone(self, label, tmp_path):
        rel_path, body, args = self.INNOCENT[label]
        _write_script_fixture(tmp_path, rel_path, body)
        cond = _script_cond(path=rel_path, args=args)
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert not faults, (label, faults)
        assert not undecidable, (label, undecidable)

    @pytest.mark.parametrize("label", sorted(ACCEPTED_FALSE_ALARM))
    def test_the_accepted_false_alarm_still_fires(self, label, tmp_path):
        rel_path, body, args = self.ACCEPTED_FALSE_ALARM[label]
        _write_script_fixture(tmp_path, rel_path, body)
        cond = _script_cond(path=rel_path, args=args)
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert any(f.code == "probe-script-unknown-flag" for f in faults), (
            f"{label!r} is no longer flagged -- the probe's collection rule changed; "
            f"re-measure and move this case into INNOCENT in the same edit"
        )

    def test_never_imports_the_target(self, tmp_path):
        # A script whose import-time code would blow up if ever imported --
        # the probe must never trip it (defect 2's own shape one layer up).
        _write_script_fixture(tmp_path, "scripts/_gs_fixture_boom.py",
                               'raise RuntimeError("must never be imported")\n')
        cond = _script_cond(path="scripts/_gs_fixture_boom.py", args=[])
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert not faults
        assert not undecidable

    def test_missing_target_is_a_fault(self, tmp_path):
        cond = _script_cond(path="scripts/does_not_exist.py", args=["--flag"])
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert any(f.code == "probe-script-not-found" for f in faults)

    # -- m1: positional (non-`--`) arguments. r6-fowler's own args
    # (`.agent-work/<work-id>/FOWLER_PASS.json`) is the case this guards --
    # a path-shaped positional carrying an unresolved resolver-owned token
    # must be SKIPPED, never refused, or a check that could not fail turns
    # into one that cannot pass.
    _NO_FLAGS_SCRIPT = (
        "scripts/_gs_fixture_a.py",
        'import argparse\n\ndef build():\n    p = argparse.ArgumentParser()\n    p.add_argument("--known")\n    return p\n',
    )

    VIOLATING_POSITIONAL = {
        "wrong positional path, no resolver token":
            (*_NO_FLAGS_SCRIPT, [".agent-work/definitely-missing/RESULT.json"]),
        "another wrong positional path":
            (*_NO_FLAGS_SCRIPT, ["scripts/_gs_definitely_missing_script.py"]),
    }

    INNOCENT_POSITIONAL = {
        "real positional path that exists":
            (*_NO_FLAGS_SCRIPT, ["scripts/_gs_fixture_a.py"]),
        "positional path carrying a resolver-owned <work-id> token -- skipped, not refused":
            (*_NO_FLAGS_SCRIPT, [".agent-work/<work-id>/FOWLER_PASS.json"]),
        "not path-shaped at all -- left alone even though it doesn't exist as a file":
            (*_NO_FLAGS_SCRIPT, ["SomeSelectorNotAPath"]),
    }

    @pytest.mark.parametrize("label", sorted(VIOLATING_POSITIONAL))
    def test_violating_positional_is_caught(self, label, tmp_path):
        rel_path, body, args = self.VIOLATING_POSITIONAL[label]
        _write_script_fixture(tmp_path, rel_path, body)
        cond = _script_cond(path=rel_path, args=args)
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert not undecidable, (label, undecidable)
        assert any(f.code == "probe-script-positional-path-not-found" for f in faults), (label, faults)

    @pytest.mark.parametrize("label", sorted(INNOCENT_POSITIONAL))
    def test_innocent_positional_is_left_alone(self, label, tmp_path):
        rel_path, body, args = self.INNOCENT_POSITIONAL[label]
        _write_script_fixture(tmp_path, rel_path, body)
        cond = _script_cond(path=rel_path, args=args)
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert not faults, (label, faults)
        assert not undecidable, (label, undecidable)


class TestPopulationProbe:
    def _make_tree(self, tmp_path, names):
        (tmp_path / "specs").mkdir()
        for name in names:
            (tmp_path / "specs" / name).write_text("", encoding="utf-8")

    VIOLATING_TOO_FEW = ["a.toml", "b.toml"]  # expect 3, only 2 present
    VIOLATING_TOO_MANY = ["a.toml", "b.toml", "c.toml", "d.toml"]  # expect 3, 4 present

    def test_violating_too_few(self, tmp_path):
        self._make_tree(tmp_path, self.VIOLATING_TOO_FEW)
        cond = _population_cond(root="specs", glob="*.toml", expected=3)
        faults, undecidable = gs._probe_population("m1", "c1", cond, repo_root=tmp_path)
        assert not undecidable
        assert any(f.code == "probe-population-count-mismatch" for f in faults)

    def test_violating_too_many(self, tmp_path):
        self._make_tree(tmp_path, self.VIOLATING_TOO_MANY)
        cond = _population_cond(root="specs", glob="*.toml", expected=3)
        faults, undecidable = gs._probe_population("m1", "c1", cond, repo_root=tmp_path)
        assert not undecidable
        assert any(f.code == "probe-population-count-mismatch" for f in faults)

    def test_innocent_exact_match(self, tmp_path):
        self._make_tree(tmp_path, ["a.toml", "b.toml", "c.toml"])
        cond = _population_cond(root="specs", glob="*.toml", expected=3)
        faults, undecidable = gs._probe_population("m1", "c1", cond, repo_root=tmp_path)
        assert not faults
        assert not undecidable

    def test_innocent_band_match(self, tmp_path):
        self._make_tree(tmp_path, ["a.toml", "b.toml", "c.toml"])
        cond = {"id": "c1", "statement": "band", "kind": "population", "root": "specs", "glob": "*.toml",
                "expected_min": 2, "expected_max": 5}
        faults, undecidable = gs._probe_population("m1", "c1", cond, repo_root=tmp_path)
        assert not faults
        assert not undecidable

    #: `pathlib.Path.glob("**/*.toml")` matches "this directory AND all
    #: subdirectories, recursively" -- so it also matches TOP-LEVEL files, not
    #: only nested ones (DESIGN_NOTE.md section 4's own caveat about `**`
    #: recursion, measured live: verified against this host's Python). An
    #: author who writes `**/*.toml` reading it as "only inside subfolders"
    #: (the common, intuitive misreading) declares a count that excludes the
    #: top level and gets a mismatch -- the check is faithfully reproducing
    #: real pathlib semantics, not a bug, so this is pinned as FIRING.
    ACCEPTED_FALSE_ALARM = "** intuitively read as subdirectories-only, but also matches the top level"

    def test_the_accepted_false_alarm_still_fires(self, tmp_path):
        (tmp_path / "specs" / "sub").mkdir(parents=True)
        (tmp_path / "specs" / "a.toml").write_text("", encoding="utf-8")
        (tmp_path / "specs" / "b.toml").write_text("", encoding="utf-8")
        (tmp_path / "specs" / "sub" / "nested.toml").write_text("", encoding="utf-8")
        # A naive author intends "just the nested one" and declares expected=1.
        cond = _population_cond(root="specs", glob="**/*.toml", expected=1)
        faults, undecidable = gs._probe_population("m1", "c1", cond, repo_root=tmp_path)
        assert not undecidable
        assert any(f.code == "probe-population-count-mismatch" for f in faults), (
            "the ** recursion false alarm stopped firing -- pathlib.Path.glob's ** "
            "semantics changed, or the probe stopped using it; re-measure"
        )


# --------------------------------------------------------------------------- #
# main() -- order of operations and exit codes (DESIGN_NOTE.md section 8)
# --------------------------------------------------------------------------- #

class TestMainCLI:
    def test_malformed_toml_exit_1(self, tmp_path):
        spec_path = tmp_path / "bad.spine.toml"
        spec_path.write_text("this is not [ valid toml\n", encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path)])
        assert rc == 1
        assert not out_path.exists()

    def test_spec_shape_fault_exit_2(self, tmp_path):
        # Two [[gate]] blocks sharing one spec header -- valid TOML, but a
        # spec-shape fault (duplicate gate id).
        extra_gate = '''
[[gate]]
id = "m1"
title = "do it again"
imperative = "do the thing again"

  [[gate.postconditions]]
  id = "c1"
  statement = "human decided"
  kind = "artifact"
  evidence_type = "user-decision"
'''
        spec_path = tmp_path / "dup.spine.toml"
        spec_path.write_text(_real_toml_spec_text() + extra_gate, encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path)])
        assert rc == 2
        assert not out_path.exists()

    def test_malformed_claim_is_exit_2_not_a_crash(self, tmp_path):
        # `[[gate.claim]]` (array-of-tables) instead of `[gate.claim]` (a
        # table) -- valid TOML, but compile_spec expects a dict. Before m1's
        # second task this reached an unhandled `AttributeError` out of
        # main(); it must now refuse at the spec-shape layer instead.
        extra = '\n  [[gate.claim]]\n  magnitude = "large"\n  text = "x"\n'
        spec_path = tmp_path / "bad_claim.spine.toml"
        spec_path.write_text(_real_toml_spec_text(extra_gate_toml=extra), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path)])
        assert rc == 2
        assert not out_path.exists()

    def test_probe_fault_exit_3(self, tmp_path):
        extra = (
            "\n  [[gate.postconditions]]\n"
            '  id = "c2"\n'
            '  statement = "collects something"\n'
            '  kind = "pytest"\n'
            '  selector = "NoSuchTestEverExistedAnywhereZZZ"\n'
            "  min_collect = 1\n"
        )
        spec_path = tmp_path / "zero.spine.toml"
        spec_path.write_text(_real_toml_spec_text(extra_gate_toml=extra), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(ROOT)])
        assert rc == 3
        assert not out_path.exists()

    def test_success_exit_0_writes_file(self, tmp_path):
        spec_path = tmp_path / "good.spine.toml"
        spec_path.write_text(_real_toml_spec_text(), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path)])
        assert rc == 0
        assert out_path.exists()
        written = json.loads(out_path.read_text(encoding="utf-8"))
        assert written["items"] == ["m1"]
        assert written["work_id"] == "w1"

    def test_check_only_writes_nothing_on_success(self, tmp_path):
        spec_path = tmp_path / "good.spine.toml"
        spec_path.write_text(_real_toml_spec_text(), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path), "--check-only"])
        assert rc == 0
        assert not out_path.exists()

    def test_validate_is_the_literal_last_statement_before_success(self):
        import inspect
        src = inspect.getsource(gs.main)
        write_idx = src.index("write_text")
        validate_idx = src.rindex("validate(")
        assert validate_idx < write_idx


# --------------------------------------------------------------------------- #
# The real specs/*.spine.toml files, through the real CLI -- m1's own trap.
# r6-fowler in specs/reviewer.spine.toml carries a positional arg
# (`.agent-work/<work-id>/FOWLER_PASS.json`) with an unresolved resolver-owned
# token; it must keep generating cleanly, not be refused, after m1's change.
# --------------------------------------------------------------------------- #

class TestRealRoleSpecsRegenerateClean:
    @pytest.mark.parametrize("spec_name", ["implementer.spine.toml", "reviewer.spine.toml"])
    def test_role_spec_check_only_succeeds(self, spec_name, tmp_path):
        spec_path = ROOT / "specs" / spec_name
        out_path = tmp_path / spec_name.replace(".spine.toml", ".spine.json")
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(ROOT), "--check-only"])
        assert rc == 0
        assert not out_path.exists()  # --check-only writes nothing


# --------------------------------------------------------------------------- #
# "The artifact diverged from its source" (rework handoff): the g3 --out fix
# was applied by `amend` to the GENERATED spine, leaving the SOURCE spec
# (dispatch-proof/probe.spine.toml) stale -- regenerating from that TOML
# reproduced the broken check. Fixed at the source; this pins that the
# source itself, not a one-off manual patch, is what carries --out now, so
# regenerating never regresses it again.
# --------------------------------------------------------------------------- #

class TestDispatchProofOutFlagRegression:
    def test_m1_c2_compiled_command_carries_out_flag(self):
        spec_path = ROOT / ".agent-work" / "epic-559" / "c2-generate-the-spine" / "dispatch-proof" / "probe.spine.toml"
        spec = tomllib.loads(spec_path.read_text(encoding="utf-8"))
        assert gs.spec_shape_faults(spec, repo_root=ROOT) == []
        compiled = gs.compile_spec(spec)
        cmd = [c for c in compiled["tasks"]["m1"]["postconditions"] if c["id"] == "c2"][0]["check"]["command"]
        assert "--out" in cmd, "the source spec regressed to missing --out -- see rework handoff 'artifact diverged from its source'"

    def test_regenerating_check_only_from_the_real_source_succeeds(self, tmp_path):
        spec_path = ROOT / ".agent-work" / "epic-559" / "c2-generate-the-spine" / "dispatch-proof" / "probe.spine.toml"
        out_path = tmp_path / "probe.spine.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(ROOT), "--check-only"])
        assert rc == 0
        assert not out_path.exists()


# --------------------------------------------------------------------------- #
# Undecidable -- refuses, always, no flag to skip it (close criterion 9)
# --------------------------------------------------------------------------- #

class TestUndecidable:
    def test_script_probe_undecidable_refuses(self, tmp_path):
        _write_script_fixture(tmp_path, "scripts/_gs_dynamic.py",
                               'import argparse\n\nNAMES = ["--alpha", "--beta"]\n\n'
                               'def build():\n    p = argparse.ArgumentParser()\n'
                               '    for name in NAMES:\n        p.add_argument(name)\n    return p\n')
        cond = _script_cond(path="scripts/_gs_dynamic.py", args=["--alpha"])
        faults, undecidable = gs._probe_script("m1", "c1", cond, repo_root=tmp_path)
        assert not faults
        assert len(undecidable) == 1
        assert undecidable[0].code == "undecidable-script-no-add-argument"

    def test_undecidable_refuses_via_main_with_nothing_written(self, tmp_path):
        extra = (
            "\n  [[gate.postconditions]]\n"
            '  id = "c2"\n'
            '  statement = "flag is registered"\n'
            '  kind = "script"\n'
            '  path = "scripts/_gs_dynamic.py"\n'
            '  args = ["--alpha"]\n'
        )
        _write_script_fixture(tmp_path, "scripts/_gs_dynamic.py",
                               'import argparse\n\nNAMES = ["--alpha", "--beta"]\n\n'
                               'def build():\n    p = argparse.ArgumentParser()\n'
                               '    for name in NAMES:\n        p.add_argument(name)\n    return p\n')
        spec_path = tmp_path / "undecidable.spine.toml"
        spec_path.write_text(_real_toml_spec_text(extra_gate_toml=extra), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path)])
        assert rc != 0
        assert not out_path.exists()

    def test_no_flag_to_skip_undecidable(self):
        # There is no escape hatch: parsing an unknown --skip-undecidable-style
        # flag must fail argparse, not be silently accepted.
        parser_help = gs.main.__doc__ or ""
        with pytest.raises(SystemExit):
            gs.main(["spec.toml", "--out", "out.json", "--skip-undecidable"])


# --------------------------------------------------------------------------- #
# The control pairing (close criterion 3) -- demonstrated for real, both halves.
# compile_spec TRANSLATES a spec whose command carries a literal
# placeholder-shaped token the generator's own probes do not examine (a
# script's non-flag argument VALUE); the guarded CLI still refuses it, because
# validate_spine.validate() is the last word, not the generator's own probes.
# --------------------------------------------------------------------------- #

class TestControlPairing:
    SCRIPT_BODY = 'import argparse\n\ndef build():\n    p = argparse.ArgumentParser()\n    p.add_argument("--flag")\n    return p\n'

    def _spec_text(self, value: str) -> str:
        extra = (
            "\n  [[gate.postconditions]]\n"
            '  id = "c2"\n'
            '  statement = "flag carries the right value"\n'
            '  kind = "script"\n'
            '  path = "scripts/_gs_target.py"\n'
            f'  args = ["--flag", "{value}"]\n'
        )
        return _real_toml_spec_text(extra_gate_toml=extra)

    def test_translation_completes_but_guarded_cli_refuses_with_nothing_written(self, tmp_path):
        _write_script_fixture(tmp_path, "scripts/_gs_target.py", self.SCRIPT_BODY)
        spec_path = tmp_path / "refused.spine.toml"
        spec_path.write_text(self._spec_text("<oops>"), encoding="utf-8")

        # Half one: compile_spec TRANSLATES cleanly -- it does not judge.
        spec = tomllib.loads(spec_path.read_text(encoding="utf-8"))
        assert gs.spec_shape_faults(spec, repo_root=tmp_path) == []
        compiled = gs.compile_spec(spec)
        assert "<oops>" in compiled["tasks"]["m1"]["postconditions"][1]["check"]["command"]

        # Half two: the guarded CLI refuses it -- the oracle is the last word.
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path)])
        assert rc == 4
        assert not out_path.exists()

    def test_same_spec_corrected_is_accepted_and_written(self, tmp_path):
        _write_script_fixture(tmp_path, "scripts/_gs_target.py", self.SCRIPT_BODY)
        spec_path = tmp_path / "accepted.spine.toml"
        spec_path.write_text(self._spec_text("real-value"), encoding="utf-8")
        out_path = tmp_path / "out.json"
        rc = gs.main([str(spec_path), "--out", str(out_path), "--root", str(tmp_path)])
        assert rc == 0
        assert out_path.exists()


# --------------------------------------------------------------------------- #
# Property 1, verified against BEHAVIOUR (DESIGN_NOTE.md section 5): rendered
# text through the engine's own render_human, and the three verbs actually
# driven against a generated spine.
# --------------------------------------------------------------------------- #

class TestRenderHuman:
    def test_handback_block_appears_in_rendered_text(self):
        spec = _spec(gates=[_gate(postconditions=[_pytest_cond()])], parent="admiral-epic-418-followon")
        spine = gs.compile_spec(spec)
        rendered = checklist_engine.current(spine)
        assert "directives:" in rendered
        assert "handback:" in rendered
        assert "spine_evidence attach" in rendered
        assert "spine_capture flag-candidate" in rendered
        assert "spine_halt block" in rendered
        assert "admiral-epic-418-followon" in rendered


class TestHandbackVerbs:
    def _spine(self):
        spec = _spec(gates=[_gate(postconditions=[_pytest_cond()])])
        return gs.compile_spec(spec)

    def test_attach_lands_in_gate_own_evidence(self):
        spine = self._spine()
        checklist_engine.attach(spine, "m1", "review-result", {"verdict": "APPROVE"})
        evidence = spine["tasks"]["m1"]["evidence"]
        assert len(evidence) == 1
        assert evidence[0]["type"] == "review-result"
        assert evidence[0]["payload"] == {"verdict": "APPROVE"}

    def test_flag_candidate_lands_in_top_level_triage_candidates(self):
        spine = self._spine()
        checklist_engine.flag_candidate(spine, "m1", "found something out of scope")
        assert len(spine["triage_candidates"]) == 1
        assert spine["triage_candidates"][0]["statement"] == "found something out of scope"
        assert spine["triage_candidates"][0]["from"] == "m1"

    def test_block_lands_in_top_level_blockers_and_sets_gate_status(self):
        spine = self._spine()
        checklist_engine.block(spine, "m1", "needs a decision", "human", "confirm the approach")
        assert spine["tasks"]["m1"]["status"] == "blocked"
        assert len(spine["blockers"]) == 1
        assert spine["blockers"][0]["item"] == "m1"
        assert spine["blockers"][0]["blocker"] == "needs a decision"


# --------------------------------------------------------------------------- #
# Falsification floor (close criterion 8) -- in the tests/test_mutation_floor.py
# style: the c-escalation injection is mechanically deleted from a COPY of
# generate_spine.py, and a throwaway test exercising ONLY that postcondition is
# run against the copy in a subprocess. A guard whose own removal changes
# nothing is the defect this epic exists to find.
# --------------------------------------------------------------------------- #

class TestFalsificationFloor:
    INJECTION_SNIPPET = '            postconditions.append(_escalation_postcondition(text))\n'

    _THROWAWAY_TEST = (
        "import sys\n"
        "sys.path.insert(0, {scripts_dir!r})\n"
        "import generate_spine as gs\n"
        "\n"
        "def test_large_claim_injects_c_escalation_postcondition():\n"
        "    spec = {{\n"
        '        "work_id": "w1", "type": "gated", "config_ref": None,\n'
        '        "gate": [{{\n'
        '            "id": "m1", "title": "t", "imperative": "i",\n'
        '            "postconditions": [{{"id": "c1", "statement": "s", "kind": "artifact", "evidence_type": "user-decision"}}],\n'
        '            "claim": {{"magnitude": "large", "text": "big claim"}},\n'
        "        }}],\n"
        "    }}\n"
        "    spine = gs.compile_spec(spec)\n"
        '    posts = spine["tasks"]["m1"]["postconditions"]\n'
        '    assert any(c["id"] == "c-escalation" for c in posts)\n'
    )

    def _run_against(self, scripts_dir: Path, work_dir: Path):
        work_dir.mkdir(parents=True, exist_ok=True)
        test_file = work_dir / "test_floor_throwaway.py"
        test_file.write_text(self._THROWAWAY_TEST.format(scripts_dir=str(scripts_dir)), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(test_file)],
            capture_output=True, text=True, timeout=60,
        )

    def test_baseline_is_green(self, tmp_path):
        proc = self._run_against(ROOT / "scripts", tmp_path / "baseline")
        assert proc.returncode == 0, "harness error, not a kill:\n" + proc.stdout + proc.stderr

    def test_mutation_kills_it(self, tmp_path):
        original = (ROOT / "scripts" / "generate_spine.py").read_text(encoding="utf-8")
        before = original.count(self.INJECTION_SNIPPET)
        assert before == 1, "harness error: injection snippet not found exactly once in the real source"
        mutated = original.replace(self.INJECTION_SNIPPET, "            pass  # MUTATED: injection removed\n")
        after = mutated.count(self.INJECTION_SNIPPET)
        assert after == 0
        assert before - after == 1  # the mutation landed -- prove it before comparing red/green

        mutant_dir = tmp_path / "mutant_scripts"
        mutant_dir.mkdir()
        (mutant_dir / "generate_spine.py").write_text(mutated, encoding="utf-8")
        for name in ("init_work_area.py", "validate_spine.py"):
            (mutant_dir / name).write_text((ROOT / "scripts" / name).read_text(encoding="utf-8"), encoding="utf-8")

        proc = self._run_against(mutant_dir, tmp_path / "mutant")
        assert proc.returncode != 0, (
            "the mutation did NOT turn the floor red -- a guard whose own removal "
            "changes nothing is the defect this epic exists to find\n" + proc.stdout + proc.stderr
        )
        assert "test_large_claim_injects_c_escalation_postcondition" in proc.stdout


# --------------------------------------------------------------------------- #
# Falsification floor for the survey/gated distinction itself (g2 rework
# round 2, close criterion 5): same style as TestFalsificationFloor above, but
# the mutation removes the `if spec_type == "gated":` branch entirely (so a
# `survey` spec's large claim would ALSO get c-escalation injected, exactly
# the cold-review-found defect this rework fixes). A named test asserting the
# `survey` side stays clean must go red.
# --------------------------------------------------------------------------- #

class TestSurveyGatedDistinctionFloor:
    DISTINCTION_SNIPPET = '        if spec_type == "gated":\n'

    _THROWAWAY_TEST = (
        "import sys\n"
        "sys.path.insert(0, {scripts_dir!r})\n"
        "import generate_spine as gs\n"
        "\n"
        "def test_survey_large_claim_injects_no_postcondition():\n"
        "    spec = {{\n"
        '        "work_id": "w1", "type": "survey", "config_ref": None,\n'
        '        "gate": [{{\n'
        '            "id": "r1", "title": "t", "imperative": "i",\n'
        '            "postconditions": [{{"id": "c1", "statement": "s", "kind": "artifact", "evidence_type": "user-decision"}}],\n'
        '            "claim": {{"magnitude": "large", "text": "big claim"}},\n'
        "        }}],\n"
        "    }}\n"
        "    spine = gs.compile_spec(spec)\n"
        '    posts = spine["tasks"]["r1"]["postconditions"]\n'
        '    assert not any(c["id"] == "c-escalation" for c in posts)\n'
    )

    def _run_against(self, scripts_dir: Path, work_dir: Path):
        work_dir.mkdir(parents=True, exist_ok=True)
        test_file = work_dir / "test_floor_throwaway.py"
        test_file.write_text(self._THROWAWAY_TEST.format(scripts_dir=str(scripts_dir)), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(test_file)],
            capture_output=True, text=True, timeout=60,
        )

    def test_baseline_is_green(self, tmp_path):
        proc = self._run_against(ROOT / "scripts", tmp_path / "baseline")
        assert proc.returncode == 0, "harness error, not a kill:\n" + proc.stdout + proc.stderr

    def test_mutation_kills_it(self, tmp_path):
        original = (ROOT / "scripts" / "generate_spine.py").read_text(encoding="utf-8")
        before = original.count(self.DISTINCTION_SNIPPET)
        assert before == 1, "harness error: distinction snippet not found exactly once in the real source"
        mutated = original.replace(self.DISTINCTION_SNIPPET, '        if True:  # MUTATED: survey/gated distinction removed\n')
        after = mutated.count(self.DISTINCTION_SNIPPET)
        assert after == 0
        assert before - after == 1  # the mutation landed -- prove it before comparing red/green

        mutant_dir = tmp_path / "mutant_scripts"
        mutant_dir.mkdir()
        (mutant_dir / "generate_spine.py").write_text(mutated, encoding="utf-8")
        for name in ("init_work_area.py", "validate_spine.py"):
            (mutant_dir / name).write_text((ROOT / "scripts" / name).read_text(encoding="utf-8"), encoding="utf-8")

        proc = self._run_against(mutant_dir, tmp_path / "mutant")
        assert proc.returncode != 0, (
            "the mutation did NOT turn the floor red -- a guard whose own removal "
            "changes nothing is the defect this epic exists to find\n" + proc.stdout + proc.stderr
        )
        assert "test_survey_large_claim_injects_no_postcondition" in proc.stdout


class TestPureBoundary:
    def test_compile_condition_is_pure_function(self):
        import inspect
        assert not inspect.isgeneratorfunction(gs.compile_condition)

    def test_compile_spec_never_writes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        spec = _spec(gates=[_gate(postconditions=[_qualitative_cond()])])
        gs.compile_spec(spec)
        assert list(tmp_path.iterdir()) == []
