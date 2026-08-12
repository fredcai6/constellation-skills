#!/usr/bin/env python
"""Compile a `specs/<role>.spine.toml` spec into an engine-native spine JSON, and
refuse to emit anything `scripts/validate_spine.py` would reject.

Frozen contract: `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md`. There
is no raw-command field anywhere in the spec format -- a check is authored as a
typed, closed-vocabulary kind (`CHECK_KINDS`), never a shell string typed from
memory, which is the class of defect (issue epic-559) this generator exists to
close.

Two layers, split at FUNCTION granularity (matching validate_spine.py's own pure
`_fault_*` beside subprocess-calling `_collects_zero`, and checklist_engine.py's
pure `evaluate_git_change_policy` beside `_collect_changed_files`):

- `spec_shape_faults`, `compile_condition`, `compile_spec` are PURE: dict in, dict
  out, no `Path`, no `open`, no `subprocess` reachable from them. (`spec_shape_faults`
  is the one exception that touches the filesystem -- it does a cheap `open`+
  `json.loads` on `config_ref` to catch the epic-559 config-ref-not-json crash --
  but never runs a subprocess, matching DESIGN_NOTE.md section 8 step 2's own
  "cheap, no subprocess" framing.)
- The probes, the oracle call, the write and `main()` sit below them and do the
  expensive, environment-touching work.

Order, and nothing is written unless every layer passes (DESIGN_NOTE.md section 8):

    1. tomllib.load                         -- malformed TOML: exit 1
    2. spec_shape_faults (section 7)        -- exit 2
    3. compile_spec                         -- pure, always succeeds past 1-2
    4. probes (section 4)                   -- exit 3 (includes probe-level undecidable)
    5. validate_spine.validate(...)         -- the literal last statement before
                                                success; any Fault or .undecidable
                                                entry refuses -- exit 4
    6. write                                -- exit 0

`--check-only` runs 1-5 and writes nothing.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shlex
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from init_work_area import _RESOLVER_OWNED_TOKEN_RE  # noqa: E402
from validate_spine import ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH, validate  # noqa: E402

#: The closed vocabulary (DESIGN_NOTE.md section 4). Single source of truth --
#: a later gate pins DESIGN_NOTE.md's kind list against this exact constant, so
#: it is never renamed casually.
CHECK_KINDS = ("qualitative", "pytest", "script", "population", "artifact")

#: The reserved id the claim-escalation postcondition (section 6) owns. A spec
#: that declares a condition with this id is refused at spec-shape time.
RESERVED_CONDITION_ID = "c-escalation"

#: The reserved id FAMILY the declared-dispatch postconditions (section 5) own
#: -- one `c-dispatch-<idx>` per declared [[gate.dispatch]] entry, injected in
#: `_compile_gate`. An author who declares a postcondition/precondition id
#: matching this family collides with an injected one silently (the same
#: hazard RESERVED_CONDITION_ID/c-escalation already guards against), so it is
#: refused here too, before compile_spec ever runs.
_RESERVED_DISPATCH_ID_RE = re.compile(r"^c-dispatch-\d+$")

#: DESIGN_NOTE.md section 5 / LIFECYCLE_CONTRACT.md section 5: textual markers
#: that name a dispatch in a gate's prose imperative. Detection is TEXTUAL --
#: an imperative phrased without any of these ("hand this to an implementer
#: crew") stays invisible; spec-dispatch-undeclared narrows the hole, it does
#: not close it.
_DISPATCH_MARKERS = ("run_crew.py", "constellation-implementer", "constellation-reviewer")

#: `directives.claim.enforcement` on a `gated` spec (g2 rework round 2, the
#: DESIGN_NOTE.md section 6 defect the cold review found): `c-escalation` IS
#: injected here, and `checklist_engine.advance()` -- the `gated` closing verb
#: -- checks every postcondition with no kind filter, so this text states a
#: mechanism that is genuinely load-bearing.
CLAIM_ENFORCEMENT_GATED = (
    "enforced -- postcondition `c-escalation` (kind=artifact, evidence_type=review-result, "
    "match {\"verdict\": \"APPROVE\"}) is injected into this gate's postconditions. "
    "`checklist_engine.advance()`, the `gated` closing verb, checks every postcondition "
    "with no kind filter, so this gate cannot close until an independent reviewer's "
    "APPROVE is attached and c-escalation is satisfied."
)

#: `directives.claim.enforcement` on a `survey` spec: no postcondition is injected
#: here at all, because nothing on a survey item's execution path would ever
#: consult it. `checklist_engine.record()` evaluates only command-kind
#: postconditions on a survey item (the survey-record-check-scope ruling,
#: #422) -- an artifact-kind postcondition would sit unevaluated forever.
#: `checklist_engine.consolidate()` reads only each item's own stored `result`
#: field and nothing else (#328). Injecting `c-escalation` here would not fail
#: loudly; it would pass silently, which is worse than not injecting it -- see
#: the cold review this round-2 rework answers.
CLAIM_ENFORCEMENT_SURVEY = (
    "NOT machine-enforced here -- no postcondition is injected for a large claim on a "
    "`survey` spec. `checklist_engine.record()` on a survey item evaluates only "
    "command-kind postconditions (survey-record-check-scope, #422) and leaves an "
    "artifact-kind postcondition like the one `gated` specs inject permanently "
    "unevaluated; `checklist_engine.consolidate()` reads only each item's stored "
    "`result` field and nothing else (#328). An injected postcondition here would be "
    "silently inert, not a real gate -- so none is injected. The tier this gate hands "
    "back to (see `directives.handback.hand_back_to`) must adjudicate this claim itself."
)

_REPO_ROOT_TOKEN = "<repo-root>"

#: Pins DESIGN_NOTE.md section 4's own claim -- "`<repo-root>` is resolver-owned
#: -- verified, `_RESOLVER_OWNED_TOKEN_RE.fullmatch("<repo-root>")` is true --
#: so it is legitimate in output and is not the placeholder class the generator
#: refuses." Without this, that sentence was argued in prose while the import
#: that could check it sat unused (g1's cold review, carried into g2). If
#: `_REPO_ROOT_TOKEN` is ever edited to something outside the resolver-owned
#: families, this fails at import time instead of silently emitting a spine the
#: resolver can never finish resolving.
assert _RESOLVER_OWNED_TOKEN_RE.fullmatch(_REPO_ROOT_TOKEN), (
    f"{_REPO_ROOT_TOKEN!r} is not a resolver-owned token per "
    f"_RESOLVER_OWNED_TOKEN_RE -- DESIGN_NOTE.md section 4 depends on this"
)


@dataclass(frozen=True)
class Fault:
    """One spec-shape refusal reason (DESIGN_NOTE.md section 7) -- distinct from
    `validate_spine.Fault`, which reports faults found in the COMPILED spine.
    This one reports faults found in the AUTHORED spec, before compilation ever
    runs."""

    code: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.where}: {self.message}"


# --------------------------------------------------------------------------- #
# spec_shape_faults -- section 7, refused before any probe
# --------------------------------------------------------------------------- #

_REQUIRED_COND_FIELDS = {
    "qualitative": ("because",),
    "pytest": ("selector",),
    "script": ("path",),
    "population": ("root", "glob"),
    "artifact": ("evidence_type",),
}


#: The four fields that are interpolated into a compiled `command` UNQUOTED --
#: `population.expected`/`expected_min`/`expected_max` and `pytest.min_collect`
#: (rework Blocker 1). Every other field that reaches a compiled command
#: (`selector`, `targets`, `path`, `args`, `root`, `glob`) is `shlex.quote`d or
#: `shlex.join`ed, so a string value there is inert; these four are not, and a
#: string value here compiles a check that cannot fail (`test $(...) -eq 1 ||
#: echo PWNED` exits 0 regardless of the count). `bool` is deliberately
#: excluded even though `isinstance(True, int)` is `True` in Python -- a
#: TOML/JSON `true`/`false` value must still refuse.
def _numeric_field_faults(where: str, cond: dict, *fields: str) -> list[Fault]:
    faults: list[Fault] = []
    for field in fields:
        if field not in cond:
            continue
        value = cond[field]
        if isinstance(value, bool) or not isinstance(value, int):
            faults.append(Fault(
                "spec-non-integer-field", where,
                f"{cond.get('kind')} condition field {field!r} must be an integer, "
                f"got {value!r} ({type(value).__name__}) -- interpolated unquoted into "
                f"the compiled command, so a non-integer here can compile a check that "
                f"cannot fail",
            ))
    return faults


def _cond_faults(where: str, cond: dict) -> list[Fault]:
    faults: list[Fault] = []
    kind = cond.get("kind")
    if kind not in CHECK_KINDS:
        faults.append(Fault(
            "spec-unknown-check-kind", where,
            f"check kind {kind!r} is not one of the closed vocabulary {CHECK_KINDS} -- "
            f"there is no raw-command field and no escape kind",
        ))
        return faults

    for field in _REQUIRED_COND_FIELDS[kind]:
        if kind == "qualitative" and field == "because":
            continue  # handled below, distinctly from "missing" vs "empty"
        if not cond.get(field):
            faults.append(Fault("spec-missing-field", where, f"{kind} condition is missing required field {field!r}"))

    if kind == "qualitative":
        because = cond.get("because")
        if because is None:
            faults.append(Fault("spec-missing-field", where, "qualitative condition is missing required field 'because'"))
        elif isinstance(because, str) and because.strip() == "":
            faults.append(Fault("spec-empty-because", where, "`because` is present but empty"))

    if kind == "population":
        has_expected = "expected" in cond
        has_band = "expected_min" in cond and "expected_max" in cond
        if has_expected == has_band:  # neither, or both -- exactly one is required
            faults.append(Fault(
                "spec-missing-field", where,
                "population condition needs exactly one of `expected` or the "
                "`expected_min`/`expected_max` pair",
            ))
        faults.extend(_numeric_field_faults(where, cond, "expected", "expected_min", "expected_max"))

    if kind == "pytest":
        faults.extend(_numeric_field_faults(where, cond, "min_collect"))

    if kind == "artifact":
        evidence_type = cond.get("evidence_type")
        if not cond.get("match") and evidence_type not in ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH:
            faults.append(Fault(
                "spec-artifact-missing-match", where,
                f"artifact check for evidence_type {evidence_type!r} carries no `match`, and "
                f"that evidence type is not in ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH -- the "
                f"oracle's own falsifiable-artifact-asserts-property fault waits for exactly "
                f"this shape; failing here is a better error than failing at the spine",
            ))

    cid = cond.get("id")
    if cid == RESERVED_CONDITION_ID:
        faults.append(Fault("spec-reserved-id", where, f"{RESERVED_CONDITION_ID!r} is a reserved condition id"))
    elif isinstance(cid, str) and _RESERVED_DISPATCH_ID_RE.fullmatch(cid):
        faults.append(Fault(
            "spec-reserved-id", where,
            f"{cid!r} is a reserved condition id -- the c-dispatch-<n> family is injected per "
            f"declared [[gate.dispatch]] entry",
        ))

    return faults


_CLAIM_MAGNITUDES = ("normal", "large")


def _claim_faults(gid: str, claim) -> list[Fault]:
    """`[gate.claim]` (DESIGN_NOTE.md section 6) must be a TOML table, not an
    array-of-tables -- an author who writes `[[gate.claim]]` gets a `list`
    where `compile_spec` expects a `dict`, and without this check that reaches
    `(g.get("claim") or {}).get("magnitude")` as an unhandled
    `AttributeError: 'list' object has no attribute 'get'`, a traceback with
    no fault code (m1's own second task). Refused here, by name, before
    compile_spec ever runs."""
    if claim is None:
        return []
    where = f"{gid}.claim"
    if not isinstance(claim, dict):
        return [Fault(
            "spec-malformed-claim", where,
            f"gate.claim must be a table (`[gate.claim]`), not {type(claim).__name__} -- "
            f"did you write `[[gate.claim]]` (array-of-tables) instead of `[gate.claim]`?",
        )]
    magnitude = claim.get("magnitude", "normal")
    if magnitude not in _CLAIM_MAGNITUDES:
        return [Fault(
            "spec-malformed-claim", where,
            f"gate.claim.magnitude {magnitude!r} is not one of {_CLAIM_MAGNITUDES}",
        )]
    if magnitude == "large" and not claim.get("text"):
        return [Fault(
            "spec-malformed-claim", where,
            "gate.claim.magnitude is 'large' but claim.text is missing or empty",
        )]
    return []


def _dispatch_faults(gid: str, gate: dict, *, spec_parent) -> list[Fault]:
    """LIFECYCLE_CONTRACT.md section 5: `[[gate.dispatch]]`, `role` and `model`
    required, `parent` never declared per entry -- it is filled from the
    spec's own top-level `parent` at compile time. Three faults, refused
    before any probe:

    - `spec-dispatch-missing-field` -- a declared entry missing `role` or
      `model`.
    - `spec-dispatch-unresolved-parent` -- a dispatch declared while the
      spec's own top-level `parent` is absent, so there is nothing concrete
      to fill in. Refused rather than emitting a dispatch naming "unknown".
    - `spec-dispatch-undeclared` -- a gate whose imperative names a dispatch
      marker but declares no `[[gate.dispatch]]` at all. Detection is
      TEXTUAL (see `_DISPATCH_MARKERS`'s own docstring) -- this NARROWS the
      hole, it does not close it."""
    faults: list[Fault] = []
    raw_dispatch = gate.get("dispatch")

    if raw_dispatch is None:
        imperative = gate.get("imperative") or ""
        found = [m for m in _DISPATCH_MARKERS if m in imperative]
        if found:
            faults.append(Fault(
                "spec-dispatch-undeclared", gid,
                f"gate {gid!r}'s imperative names dispatch marker(s) {found} but declares no "
                f"[[gate.dispatch]] -- detection is textual, so this narrows the hole rather "
                f"than closing it: an imperative phrased with none of {_DISPATCH_MARKERS} "
                f"stays invisible",
            ))
        return faults

    if not isinstance(raw_dispatch, list):
        faults.append(Fault(
            "spec-dispatch-missing-field", gid,
            f"gate.dispatch must be an array of tables (`[[gate.dispatch]]`), not "
            f"{type(raw_dispatch).__name__} -- did you write `[gate.dispatch]` (a single "
            f"table) instead?",
        ))
        return faults

    for idx, entry in enumerate(raw_dispatch):
        where = f"{gid}.dispatch[{idx}]"
        if not isinstance(entry, dict):
            faults.append(Fault(
                "spec-dispatch-missing-field", where,
                f"gate.dispatch entry must be a table, got {type(entry).__name__}",
            ))
            continue
        for field in ("role", "model"):
            if not entry.get(field):
                faults.append(Fault(
                    "spec-dispatch-missing-field", where,
                    f"dispatch entry is missing required field {field!r}",
                ))
        if not spec_parent:
            faults.append(Fault(
                "spec-dispatch-unresolved-parent", where,
                f"gate {gid!r} declares a dispatch but the spec's top-level `parent` is "
                f"absent -- refusing rather than emitting a dispatch naming \"unknown\"",
            ))

    return faults


def spec_shape_faults(spec: dict, *, repo_root: Path) -> list[Fault]:
    """Every DESIGN_NOTE.md section 7 fault in `spec` (a tomllib-parsed spec
    dict), checked before `compile_spec` ever runs. Pure except for one cheap,
    subprocess-free read of `config_ref` (see module docstring)."""
    faults: list[Fault] = []
    spine_type = spec.get("type")
    gates = spec.get("gate") or []
    seen_gate_ids: set[str] = set()

    for g in gates:
        gid = g.get("id", "?")
        if gid in seen_gate_ids:
            faults.append(Fault("spec-duplicate-gate-id", gid, f"gate id {gid!r} is declared more than once"))
        seen_gate_ids.add(gid)

        for field in ("id", "title", "imperative"):
            if not g.get(field):
                faults.append(Fault("spec-missing-field", gid, f"gate is missing required field {field!r}"))

        faults.extend(_claim_faults(gid, g.get("claim")))
        faults.extend(_dispatch_faults(gid, g, spec_parent=spec.get("parent")))

        pre = g.get("preconditions") or []
        post = g.get("postconditions") or []
        pre_ids: set[str] = set()
        post_ids: set[str] = set()
        for cond in pre:
            where = f"{gid}.preconditions.{cond.get('id', '?')}"
            faults.extend(_cond_faults(where, cond))
            cid = cond.get("id")
            if cid in pre_ids:
                faults.append(Fault("spec-duplicate-condition-id", where, f"condition id {cid!r} repeated within preconditions"))
            pre_ids.add(cid)
        for cond in post:
            where = f"{gid}.postconditions.{cond.get('id', '?')}"
            faults.extend(_cond_faults(where, cond))
            cid = cond.get("id")
            if cid in post_ids:
                faults.append(Fault("spec-duplicate-condition-id", where, f"condition id {cid!r} repeated within postconditions"))
            post_ids.add(cid)
        for cid in pre_ids & post_ids:
            faults.append(Fault(
                "spec-duplicate-condition-id", f"{gid}.{cid}",
                f"condition id {cid!r} used in both preconditions and postconditions -- "
                f"ids must be disjoint (attest's --which fallback resolves by first match)",
            ))

        if spine_type == "gated" and len(post) == 0:
            faults.append(Fault(
                "spec-gated-missing-postconditions", gid,
                "a gated gate needs a postconditions list with at least one condition",
            ))
        if spine_type == "gated" and post and all(c.get("kind") == "qualitative" for c in post):
            faults.append(Fault(
                "spec-all-qualitative-postconditions", gid,
                "every postcondition is qualitative -- quoting validate_spine's own "
                "falsifiable-all-null wording: nothing here can ever refuse this gate; "
                "failing at the spec is a better error than failing at the spine",
            ))

    config_ref = spec.get("config_ref")
    if config_ref:
        cfg_path = Path(repo_root) / config_ref
        if cfg_path.exists():
            try:
                json.loads(cfg_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                faults.append(Fault(
                    "spec-config-ref-not-json", "<top-level>",
                    f"config_ref {config_ref!r} exists but is not valid JSON -- "
                    f"checklist_engine.load_config calls json.loads on any config_ref that "
                    f"exists and crashes with an unhandled JSONDecodeError before any rail "
                    f"text can print",
                ))

    return faults


#: A shipped role spec under specs/ is a reusable TEMPLATE, instantiated by
#: many future runs -- `<parent>` (or any other single bracket-wrapped
#: token) is a legitimate slot filled in at instantiation; a concrete session
#: id baked into the template is not (rework Blocker 4: specs/implementer
#: .spine.toml and specs/reviewer.spine.toml both shipped with one specific
#: Admiral session hardcoded, so every future instantiation inherited a
#: `hand_back_to` naming a session that no longer exists).
_SHIPPED_SPEC_PLACEHOLDER_PARENT_RE = re.compile(r"^<[A-Za-z0-9-]+>$")


def shipped_spec_session_specific_parent_faults(spec: dict) -> list[Fault]:
    """Only meaningful against a spec meant to SHIP as a reusable template
    (specs/*.spine.toml) -- NOT called from `spec_shape_faults`, which runs
    against every spec including a real per-run dispatch spec, where a
    concrete `parent` is exactly correct. `parent` absent, or a
    bracket-wrapped placeholder token, is the only accepted shape for a
    shipped template; anything else is a session-specific literal baked in."""
    parent = spec.get("parent")
    if parent is None:
        return []
    if isinstance(parent, str) and _SHIPPED_SPEC_PLACEHOLDER_PARENT_RE.fullmatch(parent):
        return []
    return [Fault(
        "spec-shipped-session-specific-parent", "<top-level>.parent",
        f"parent {parent!r} looks like a concrete session id, not a placeholder "
        f"(e.g. '<parent>') or absent -- a reusable role template under specs/ must "
        f"not hardcode one run's session",
    )]


# --------------------------------------------------------------------------- #
# compile_condition / compile_spec -- PURE (dict in, dict out)
# --------------------------------------------------------------------------- #

def _compile_pytest(cond: dict, repo_root_token: str) -> dict:
    selector = cond["selector"]
    min_collect = cond.get("min_collect", 1)
    targets = cond.get("targets") or []
    quoted_sel = shlex.quote(selector)
    joined_targets = shlex.join(targets)
    tail = f" {joined_targets}" if joined_targets else ""
    collect = f"python -m pytest -q -k {quoted_sel} --collect-only{tail}"
    run = f"python -m pytest -q -k {quoted_sel}{tail}"
    command = f"cd {repo_root_token} && test $({collect} 2>/dev/null | grep -c '::') -ge {min_collect} && {run}"
    return {"kind": "command", "command": command}


def _compile_script(cond: dict, repo_root_token: str) -> dict:
    path = cond["path"]
    args = cond.get("args") or []
    command = f"cd {repo_root_token} && python " + shlex.join([path, *args])
    return {"kind": "command", "command": command}


_POPULATION_COUNTER_PY = (
    "import pathlib,sys;print(sum(1 for _ in pathlib.Path(sys.argv[1]).glob(sys.argv[2])))"
)


def _compile_population(cond: dict, repo_root_token: str) -> dict:
    root = cond["root"]
    glob = cond["glob"]
    count_cmd = f"python -c {shlex.quote(_POPULATION_COUNTER_PY)} {shlex.quote(root)} {shlex.quote(glob)}"
    if "expected" in cond:
        command = f"cd {repo_root_token} && test $({count_cmd}) -eq {cond['expected']}"
    else:
        command = (
            f"cd {repo_root_token} && n=$({count_cmd}) "
            f"&& test \"$n\" -ge {cond['expected_min']} && test \"$n\" -le {cond['expected_max']}"
        )
    return {"kind": "command", "command": command}


def _compile_artifact(cond: dict) -> dict:
    out = {"kind": "artifact", "evidence_type": cond["evidence_type"]}
    match = cond.get("match")
    if match is not None:
        out["match"] = match
    return out


def compile_condition(cond: dict, *, repo_root_token: str) -> dict:
    """One authored [[gate.preconditions]] / [[gate.postconditions]] entry ->
    the engine-native Condition dict. PURE: no Path, no open, no subprocess call.
    Assumes `cond` already passed `spec_shape_faults` -- this never raises for
    a shape-valid condition."""
    kind = cond["kind"]
    statement = cond["statement"]
    if kind == "qualitative":
        statement = f"{statement} -- QUALITATIVE: {cond['because']}"
        check = None
    elif kind == "pytest" and cond.get("not_yet_written"):
        # Blocker 0: no compiled shape keeps this a `command` check AND lets
        # generation succeed before the test exists -- validate_spine's own
        # zero-collect oracle check is unconditional and out of scope to
        # edit. `check: null` mirrors qualitative's own shape (and the
        # shipped IMPLEMENTER_PLAN.template.json's TDD-red convention): a
        # manual attest at gate close rather than a machine check, with the
        # declaration and its terms rendered into the statement itself so a
        # reviewer sees the claim.
        check = None
        selector = cond["selector"]
        min_collect = cond.get("min_collect", 1)
        statement = (
            f"{statement} -- NOT YET WRITTEN AT GENERATION: pytest -k {selector!r} must "
            f"collect >= {min_collect} and pass when this gate closes; attested manually, "
            f"not machine-checked, until the test exists"
        )
    elif kind == "pytest":
        check = _compile_pytest(cond, repo_root_token)
    elif kind == "script":
        check = _compile_script(cond, repo_root_token)
    elif kind == "population":
        check = _compile_population(cond, repo_root_token)
    elif kind == "artifact":
        check = _compile_artifact(cond)
    else:  # pragma: no cover -- unreachable once spec_shape_faults gated the kind
        raise ValueError(f"unknown check kind {kind!r}")
    return {"id": cond["id"], "statement": statement, "check": check, "satisfied": False}


def _handback_contract(hand_back_to: str) -> dict:
    """DESIGN_NOTE.md section 5 -- injected, unconditional, on every gate. Names
    the three verbs that actually persist (`attach`, `flag-candidate`, `block`),
    never a beliefs/concerns/open_questions array: no engine verb appends to a
    `directives` field on an ACTIVE gate (`amend rescope` touches pending gates
    only), so an array shape would render empty forever."""
    return {
        "purpose": "where this gate hands something back -- these are the engine's real, persistent channels, not a field to write prose into",
        "belief_worth_recording": "spine_evidence attach -- lands in this gate's own evidence[]",
        "open_question_out_of_scope": "spine_capture flag-candidate -- lands in the top-level triage_candidates[]",
        "concern_that_must_stop_this_gate": "spine_halt block -- sets status blocked and appends to the top-level blockers[], bubbling to the parent named below",
        "hand_back_to": hand_back_to,
        "note": "there is NO engine verb that appends to a directives field on an active gate (amend rescope touches pending gates only), so this contract names verbs that persist rather than offering arrays that would render empty forever",
    }


def _escalation_postcondition(text: str) -> dict:
    return {
        "id": RESERVED_CONDITION_ID,
        "statement": f"LARGE CLAIM -- an independent reviewer must approve this gate before it closes: {text}",
        "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
        "satisfied": False,
    }


def _compile_dispatch_entry(idx: int, entry: dict, *, gid: str, work_id: str, parent: str,
                             repo_root_token: str) -> tuple[dict, dict]:
    """One declared `[[gate.dispatch]]` entry -> (the rendered dict for
    `directives.dispatch`, the injected postcondition). PURE: no Path, no
    open, no subprocess. Assumes `entry` already passed `_dispatch_faults` --
    `role`/`model` present, `parent` concrete (never "unknown").

    `command`, never `artifact` -- LIFECYCLE_CONTRACT.md section 5 /
    DESIGN_NOTE.md section 6's own correction: `record`/`consolidate` never
    evaluate artifact-kind postconditions on a survey item, so an artifact
    check would be silently inert there. The command shells out to
    `scripts/verify_declared_dispatch.py`, which reuses `run_crew.py`'s own
    registry loading and `is_abandoned` rather than re-parsing `crew-runs.json`."""
    role = entry["role"]
    model = entry["model"]
    rendered = {"role": role, "model": model, "parent": parent}
    command = (
        f"cd {repo_root_token} && python scripts/verify_declared_dispatch.py --root . "
        f"--work-id {shlex.quote(work_id)} --gate {shlex.quote(gid)} "
        f"--role {shlex.quote(role)} --parent {shlex.quote(parent)} --model {shlex.quote(model)}"
    )
    postcondition = {
        "id": f"c-dispatch-{idx}",
        "statement": (
            f"declared dispatch -- role={role!r} model={model!r} parent={parent!r} must be "
            f"recorded by a non-abandoned crew-runs.json entry for gate {gid!r} role {role!r} "
            f"before this gate can advance"
        ),
        "check": {"kind": "command", "command": command},
        "satisfied": False,
    }
    return rendered, postcondition


def _compile_gate(g: dict, *, hand_back_to: str, is_last: bool,
                   large_claims: list[tuple[str, str, str]], spec_type: str, work_id: str) -> dict:
    preconditions = [compile_condition(c, repo_root_token=_REPO_ROOT_TOKEN) for c in g.get("preconditions") or []]
    postconditions = [compile_condition(c, repo_root_token=_REPO_ROOT_TOKEN) for c in g.get("postconditions") or []]

    directives: dict = {"handback": _handback_contract(hand_back_to)}

    claim = g.get("claim")
    if claim and claim.get("magnitude") == "large":
        text = claim["text"]
        if spec_type == "gated":
            # Unchanged from round 1: `advance()` (the `gated` closing verb)
            # checks every postcondition with no kind filter, so injecting
            # c-escalation here genuinely blocks close.
            postconditions.append(_escalation_postcondition(text))
            enforcement = CLAIM_ENFORCEMENT_GATED
            note = (
                f"postcondition {RESERVED_CONDITION_ID} was injected because this gate carries "
                f"a large claim on a `gated` spec -- see directives.claim.enforcement for why "
                f"that injection is genuinely load-bearing here"
            )
        else:
            # g2 rework round 2: on a `survey` spec, `record()`/`consolidate()`
            # never consult an artifact-kind postcondition (see
            # CLAIM_ENFORCEMENT_SURVEY) -- injecting c-escalation here would be
            # silently inert, not a real gate. Say so instead of injecting it.
            enforcement = CLAIM_ENFORCEMENT_SURVEY
            note = (
                "no postcondition was injected -- this gate carries a large claim on a "
                "`survey` spec, and nothing on a survey item's execution path would ever "
                "consult an injected one; see directives.claim.enforcement"
            )
        directives["claim"] = {
            "magnitude": "large",
            "text": text,
            "enforcement": enforcement,
            "note": note,
        }

    if is_last and large_claims:
        directives["claims_rollup"] = {
            gid: {"magnitude": "large", "text": text, "enforcement": enforcement}
            for gid, text, enforcement in large_claims
        }

    dispatch_entries = g.get("dispatch") or []
    if dispatch_entries:
        rendered_dispatch = []
        for idx, entry in enumerate(dispatch_entries):
            rendered, postcondition = _compile_dispatch_entry(
                idx, entry, gid=g["id"], work_id=work_id, parent=hand_back_to,
                repo_root_token=_REPO_ROOT_TOKEN,
            )
            rendered_dispatch.append(rendered)
            postconditions.append(postcondition)
        directives["dispatch"] = rendered_dispatch

    return {
        "id": g["id"],
        "title": g["title"],
        "imperative": g["imperative"],
        "preconditions": preconditions,
        "postconditions": postconditions,
        "constraints": g.get("constraints") or [],
        "directives": directives,
        "child_checklist": None,
        "status": "pending",
        "status_detail": {},
        "result": None,
        "finding": None,
        "evidence": [],
        "rework_count": 0,
    }


def compile_spec(spec: dict) -> dict:
    """The full spec -> engine-native spine, PURE: no Path, no open, no
    subprocess call. Assumes `spec` already passed `spec_shape_faults`."""
    hand_back_to = spec.get("parent") or "unknown"
    spec_type = spec.get("type", "gated")
    gates = spec.get("gate") or []
    large_claims = [
        (g["id"], g["claim"]["text"], CLAIM_ENFORCEMENT_GATED if spec_type == "gated" else CLAIM_ENFORCEMENT_SURVEY)
        for g in gates
        if (g.get("claim") or {}).get("magnitude") == "large"
    ]
    tasks = {}
    for idx, g in enumerate(gates):
        is_last = idx == len(gates) - 1
        tasks[g["id"]] = _compile_gate(g, hand_back_to=hand_back_to, is_last=is_last,
                                        large_claims=large_claims, spec_type=spec_type,
                                        work_id=spec["work_id"])
    return {
        "work_id": spec["work_id"],
        "type": spec.get("type", "gated"),
        "config_ref": spec.get("config_ref"),
        "items": [g["id"] for g in gates],
        "tasks": tasks,
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
    }


# --------------------------------------------------------------------------- #
# Probes -- the expensive, environment-touching layer (DESIGN_NOTE.md section 4).
# Everything below this point may use Path/open/subprocess.
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Undecidable:
    """One condition a probe could not evaluate at all -- not a Fault (the
    check might be sound), and not silence either. Mirrors
    `validate_spine.Undecidable`'s own contract at the generator's probe
    layer.

    `blocking` defaults `True` -- the historical, still-correct behaviour for
    a probe that genuinely could not run (pytest missing, an unparseable
    script). The one exception (rework Blocker 0) is a `pytest` condition
    whose author STATED `not_yet_written = true`: at generation time the
    truth genuinely is "could not tell" (the test does not exist yet by
    design), but that is a stated declaration a reviewer sees rendered on the
    gate, not an unexplained probe failure -- so it must not refuse
    generation the way a genuine infra-level undecidable does."""

    code: str
    where: str
    message: str
    blocking: bool = True

    def __str__(self) -> str:
        return f"[{self.code}] {self.where}: {self.message}"


def _run_pytest_collect(selector: str, targets: list[str], *, repo_root: Path):
    """`python -m pytest --collect-only -q -k <selector> <targets>`, run once.
    Returns the completed process, or `None` plus the exception text when the
    subprocess itself could not be launched at all (missing interpreter,
    timeout) -- distinct from pytest running and reporting a usage error."""
    cmd = ["python", "-m", "pytest", "--collect-only", "-q", "-k", selector, *targets]
    try:
        return subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=120), None
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)


def _probe_pytest_not_yet_written(gid: str, cid: str, cond: dict, *, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """Blocker 0 (rework handoff): `not_yet_written = true` is a stated
    declaration that this pytest condition asserts a CLOSE-TIME truth, not a
    generation-time one -- the entire point of a red step. Generation still
    verifies well-formedness (selector parses, targets resolve); it does not
    assert the check is already green -- there IS no live count to assert:
    `compile_condition` compiles this condition to `check: null` (never a
    `command`), because `validate_spine.validate()` -- out of scope to edit,
    and the literal last statement before success -- unconditionally re-probes
    any `command`-kind pytest check and refuses a genuine zero-collect live.
    There is no compiled shape that is both a strict command AND survives
    that oracle check before the test exists, so the declared case is
    attested manually at gate close, exactly the shape the shipped
    `IMPLEMENTER_PLAN.template.json` already uses for a TDD red step
    (`check: null`, never a command check for the by-design-failing step)."""
    selector = cond["selector"]
    targets = cond.get("targets") or []
    where = f"{gid}.{cid}"

    # Targets resolve: a target that does not exist IS the declared scenario
    # (the whole test file may not exist yet) -- pytest itself cannot tell
    # "missing file" apart from "bad -k syntax" (both exit 4), so this must be
    # decided from the filesystem before pytest ever runs, or the declared,
    # expected case would be refused as if it were a typo.
    missing = [t for t in targets
               if not _RESOLVER_OWNED_TOKEN_RE.search(t) and not (Path(repo_root) / t).exists()]
    if missing:
        return [], [Undecidable(
            "undecidable-pytest-not-yet-written", where,
            f"declared not_yet_written -- target(s) {missing} do not exist yet; attested "
            f"manually when this gate closes, not machine-checked at generation",
            blocking=False,
        )]

    proc, exc = _run_pytest_collect(selector, targets, repo_root=repo_root)
    if proc is None:
        return [], [Undecidable("undecidable-pytest-collect", where, f"could not run pytest --collect-only: {exc}")]
    if proc.returncode == 4:
        # Selector parses: a usage error with every named target present on
        # disk means the -k expression itself is malformed -- a real
        # authoring defect the declaration does not excuse.
        return [Fault(
            "probe-pytest-malformed-selector", where,
            f"selector {selector!r} is not valid pytest -k syntax (pytest usage error): "
            f"{proc.stderr.strip()}",
        )], []
    return [], [Undecidable(
        "undecidable-pytest-not-yet-written", where,
        f"declared not_yet_written -- selector {selector!r} is well-formed; whether it "
        f"collects and passes is attested manually when this gate closes, not "
        f"machine-checked at generation",
        blocking=False,
    )]


def _probe_pytest(gid: str, cid: str, cond: dict, *, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """DESIGN_NOTE.md section 4: run `python -m pytest --collect-only -q -k
    <selector> <targets>` and refuse below min_collect, reporting the actual
    count. Silence (no `not_yet_written` declaration) keeps this strict
    default -- load-bearing for regression guards, where refusing a
    zero-collect selector is correct."""
    if cond.get("not_yet_written"):
        return _probe_pytest_not_yet_written(gid, cid, cond, repo_root=repo_root)

    selector = cond["selector"]
    min_collect = cond.get("min_collect", 1)
    targets = cond.get("targets") or []
    where = f"{gid}.{cid}"
    proc, exc = _run_pytest_collect(selector, targets, repo_root=repo_root)
    if proc is None:
        return [], [Undecidable("undecidable-pytest-collect", where, f"could not run pytest --collect-only: {exc}")]
    count = proc.stdout.count("::")
    if count < min_collect:
        return [Fault(
            "probe-pytest-below-min-collect", where,
            f"selector {selector!r} collected {count} test(s), need >= {min_collect}",
        )], []
    return [], []


def _add_argument_literals(tree: ast.AST) -> set[str]:
    """Every string literal passed as the FIRST positional argument to a call
    named `add_argument`, anywhere in `tree` -- static, never executed. This
    scope (first positional only) is DESIGN_NOTE.md section 4's own wording;
    `TestScriptProbe::ACCEPTED_FALSE_ALARM` pins the resulting, accepted gap
    (a long flag registered second, e.g. `add_argument("-f", "--foo")`)."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "attr", None) if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name != "add_argument" or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            found.add(first.value)
    return found


#: A positional argument is "path-shaped" if it contains a `/` or ends in
#: what looks like a file suffix. Deliberately loose -- a heuristic, not a
#: curated whitelist, matching the corpus's existing convention
#: (`map_orient.PATH_TOKEN_RE`'s own "deliberately loose" comment). Scope is
#: enforced by the exists()/resolver-token checks below, not by this
#: predicate: over-matching just means one more existence check, never a
#: false fault, since a resolver-owned token or a real on-disk path both
#: pass it cleanly.
_PATH_SUFFIX_RE = re.compile(r"\.[A-Za-z0-9]{1,8}$")


def _looks_path_shaped(token: str) -> bool:
    return "/" in token or bool(_PATH_SUFFIX_RE.search(token))


def _positional_arg_faults(gid: str, cid: str, path: str, args: list[str], *, repo_root: Path) -> list[Fault]:
    """DESIGN_NOTE.md m1: every path-shaped POSITIONAL argument (not a
    `--flag`) is checked against the repo tree, UNLESS it carries a
    resolver-owned token -- that family (`<work-id>`, `<repo-root>`,
    `<*-skill-dir>`, `<*-session-id>`) is filled in by the resolver after
    generation, cannot be checked here, and is already accepted by
    validate_spine.py, so it is skipped rather than refused. A positional arg
    that is not path-shaped at all (a selector, a flag value, a number) is
    left alone -- there is nothing to check it against."""
    where = f"{gid}.{cid}"
    faults: list[Fault] = []
    for arg in args:
        if arg.startswith("--") or not _looks_path_shaped(arg):
            continue
        if _RESOLVER_OWNED_TOKEN_RE.search(arg):
            continue  # resolver-owned -- unresolved by design at generation time
        if not (Path(repo_root) / arg).exists():
            faults.append(Fault(
                "probe-script-positional-path-not-found", where,
                f"{path!r}'s positional argument {arg!r} does not exist under the repo root",
            ))
    return faults


def _probe_script(gid: str, cid: str, cond: dict, *, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """DESIGN_NOTE.md section 4 + m1: ast.parse the target file and collect
    every add_argument literal; every `--flag` in `args` must be in that set,
    and every path-shaped positional argument (see `_positional_arg_faults`)
    must exist on disk unless it carries a resolver-owned token. The target
    is NEVER imported -- importing it would run its import-time code inside
    the generator, defect 2's own shape one layer up."""
    path = cond["path"]
    args = cond.get("args") or []
    where = f"{gid}.{cid}"
    target = Path(repo_root) / path
    if not target.exists():
        return [Fault("probe-script-not-found", where, f"script path {path!r} does not exist")], []

    faults = _positional_arg_faults(gid, cid, path, args, repo_root=repo_root)

    flags = [a for a in args if a.startswith("--")]
    if not flags:
        return faults, []  # nothing else to check

    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return faults, [Undecidable("undecidable-script-parse", where, f"could not ast.parse {path!r}: {exc}")]

    declared = _add_argument_literals(tree)
    if not declared:
        return faults, [Undecidable(
            "undecidable-script-no-add-argument", where,
            f"{path!r} declares no add_argument literals at all -- cannot tell whether {flags} are real flags",
        )]

    unknown = [f for f in flags if f not in declared]
    if unknown:
        faults.append(Fault(
            "probe-script-unknown-flag", where,
            f"{path!r} has no add_argument for {unknown} (known: {sorted(declared)})",
        ))
    return faults, []


def _probe_population(gid: str, cid: str, cond: dict, *, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """DESIGN_NOTE.md section 4: execute the COMPILED command string itself and
    judge on its exit status -- one implementation, the thing probed is the
    thing shipped."""
    where = f"{gid}.{cid}"
    check = _compile_population(cond, str(repo_root))
    command = check["command"]
    try:
        proc = subprocess.run(["bash", "-c", command], cwd=str(repo_root), capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], [Undecidable("undecidable-population-probe", where, f"could not execute the compiled check: {exc}")]
    if proc.returncode != 0:
        return [Fault(
            "probe-population-count-mismatch", where,
            "the declared population count/band does not match the live tree "
            "(the compiled check, executed as-is, exited nonzero)",
        )], []
    return [], []


def probe_spec(spec: dict, *, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """Probe every `pytest`/`script`/`population` condition in `spec` against
    live state. `qualitative` and `artifact` conditions carry no probe (there
    is nothing environment-touching to check)."""
    faults: list[Fault] = []
    undecidable: list[Undecidable] = []
    for g in spec.get("gate") or []:
        gid = g["id"]
        for which in ("preconditions", "postconditions"):
            for cond in g.get(which) or []:
                kind = cond.get("kind")
                cid = cond.get("id", "?")
                if kind == "pytest":
                    f, u = _probe_pytest(gid, cid, cond, repo_root=repo_root)
                elif kind == "script":
                    f, u = _probe_script(gid, cid, cond, repo_root=repo_root)
                elif kind == "population":
                    f, u = _probe_population(gid, cid, cond, repo_root=repo_root)
                else:
                    continue
                faults.extend(f)
                undecidable.extend(u)
    return faults, undecidable


# --------------------------------------------------------------------------- #
# main() -- ties the layers together. Order, and nothing is written unless
# every layer passes (module docstring / DESIGN_NOTE.md section 8).
# --------------------------------------------------------------------------- #

def _print_faults(label: str, items) -> None:
    print(f"{label}: {len(items)}")
    for item in items:
        print(f"  {item}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="path to a specs/<role>.spine.toml file")
    parser.add_argument("--out", required=True, help="path to write the compiled spine JSON")
    parser.add_argument("--root", default=".", help="repo root")
    parser.add_argument("--check-only", action="store_true", help="run every layer but write nothing")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    spec_path = Path(args.spec)

    # 1. tomllib.load
    try:
        with open(spec_path, "rb") as fh:
            spec = tomllib.load(fh)
    except (tomllib.TOMLDecodeError, OSError) as exc:
        print(f"could not parse {spec_path}: {exc}")
        return 1

    # 2. Spec-shape check -- cheap, no subprocess.
    shape_faults = spec_shape_faults(spec, repo_root=root)
    if shape_faults:
        _print_faults("spec-shape refused", shape_faults)
        return 2

    # 3. compile_spec -- pure.
    compiled = compile_spec(spec)

    # 4. Probes -- the expensive, environment-touching layer. An undecidable
    #    that could not be helped (a probe that genuinely could not run)
    #    refuses exactly like a fault; there is no flag to skip THAT. A
    #    non-blocking undecidable (Blocker 0: a STATED `not_yet_written`
    #    declaration) is printed but does not refuse -- it is a different
    #    channel from silence, not an escape hatch from one.
    probe_faults, probe_undecidable = probe_spec(spec, repo_root=root)
    blocking_undecidable = [u for u in probe_undecidable if u.blocking]
    non_blocking_undecidable = [u for u in probe_undecidable if not u.blocking]
    if blocking_undecidable:
        _print_faults("undecidable -- could not tell", blocking_undecidable)
        return 3
    if probe_faults:
        _print_faults("probe refused", probe_faults)
        return 3
    if non_blocking_undecidable:
        _print_faults("undecidable -- declared not yet written (informational, not blocking)", non_blocking_undecidable)

    # 5. validate_spine.validate() -- the literal last statement before success.
    #    Imported and called, never re-implemented. Fault messages print
    #    verbatim via Fault.__str__, never paraphrased.
    result = validate(compiled, repo_root=root)
    if result.undecidable:
        _print_faults("undecidable -- could not tell", result.undecidable)
        return 4
    if result:
        _print_faults("oracle refused", result)
        return 4

    if args.check_only:
        print(f"check-only: {spec_path} would compile clean")
        return 0

    # 6. Write.
    Path(args.out).write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
