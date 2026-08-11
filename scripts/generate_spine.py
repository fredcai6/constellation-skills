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

_REPO_ROOT_TOKEN = "<repo-root>"


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

    if cond.get("id") == RESERVED_CONDITION_ID:
        faults.append(Fault("spec-reserved-id", where, f"{RESERVED_CONDITION_ID!r} is a reserved condition id"))

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


def _compile_gate(g: dict, *, hand_back_to: str, is_last: bool, large_claims: list[tuple[str, str]]) -> dict:
    preconditions = [compile_condition(c, repo_root_token=_REPO_ROOT_TOKEN) for c in g.get("preconditions") or []]
    postconditions = [compile_condition(c, repo_root_token=_REPO_ROOT_TOKEN) for c in g.get("postconditions") or []]

    directives: dict = {"handback": _handback_contract(hand_back_to)}

    claim = g.get("claim")
    if claim and claim.get("magnitude") == "large":
        text = claim["text"]
        postconditions.append({
            "id": RESERVED_CONDITION_ID,
            "statement": f"LARGE CLAIM -- an independent reviewer must approve this gate before it closes: {text}",
            "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
            "satisfied": False,
        })
        directives["claim"] = {
            "magnitude": "large",
            "text": text,
            "note": (
                f"postcondition {RESERVED_CONDITION_ID} was injected because this gate carries "
                f"a large claim -- an unexplained injected condition is a comprehension cost "
                f"paid down deliberately"
            ),
        }

    if is_last and large_claims:
        directives["claims_rollup"] = {gid: {"magnitude": "large", "text": text} for gid, text in large_claims}

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
    gates = spec.get("gate") or []
    large_claims = [
        (g["id"], g["claim"]["text"])
        for g in gates
        if (g.get("claim") or {}).get("magnitude") == "large"
    ]
    tasks = {}
    for idx, g in enumerate(gates):
        is_last = idx == len(gates) - 1
        tasks[g["id"]] = _compile_gate(g, hand_back_to=hand_back_to, is_last=is_last, large_claims=large_claims)
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
    layer."""

    code: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.where}: {self.message}"


def _probe_pytest(gid: str, cid: str, cond: dict, *, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """DESIGN_NOTE.md section 4: run `python -m pytest --collect-only -q -k
    <selector> <targets>` and refuse below min_collect, reporting the actual
    count."""
    selector = cond["selector"]
    min_collect = cond.get("min_collect", 1)
    targets = cond.get("targets") or []
    where = f"{gid}.{cid}"
    cmd = ["python", "-m", "pytest", "--collect-only", "-q", "-k", selector, *targets]
    try:
        proc = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
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


def _probe_script(gid: str, cid: str, cond: dict, *, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """DESIGN_NOTE.md section 4: ast.parse the target file and collect every
    add_argument literal; every `--flag` in `args` must be in that set. The
    target is NEVER imported -- importing it would run its import-time code
    inside the generator, defect 2's own shape one layer up."""
    path = cond["path"]
    args = cond.get("args") or []
    where = f"{gid}.{cid}"
    target = Path(repo_root) / path
    if not target.exists():
        return [Fault("probe-script-not-found", where, f"script path {path!r} does not exist")], []

    flags = [a for a in args if a.startswith("--")]
    if not flags:
        return [], []  # nothing to check, accepted

    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [], [Undecidable("undecidable-script-parse", where, f"could not ast.parse {path!r}: {exc}")]

    declared = _add_argument_literals(tree)
    if not declared:
        return [], [Undecidable(
            "undecidable-script-no-add-argument", where,
            f"{path!r} declares no add_argument literals at all -- cannot tell whether {flags} are real flags",
        )]

    unknown = [f for f in flags if f not in declared]
    if unknown:
        return [Fault(
            "probe-script-unknown-flag", where,
            f"{path!r} has no add_argument for {unknown} (known: {sorted(declared)})",
        )], []
    return [], []


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

    # 4. Probes -- the expensive, environment-touching layer. Undecidable
    #    refuses exactly like a fault; there is no flag to skip it.
    probe_faults, probe_undecidable = probe_spec(spec, repo_root=root)
    if probe_undecidable:
        _print_faults("undecidable -- could not tell", probe_undecidable)
        return 3
    if probe_faults:
        _print_faults("probe refused", probe_faults)
        return 3

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
