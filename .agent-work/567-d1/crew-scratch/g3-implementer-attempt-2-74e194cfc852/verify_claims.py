"""g3-implement rework: every factual assertion left standing in the specs' new
prose, each measured against the file, symbol or behaviour that makes it true.

This is the check the reopened gate turns on. The BLOCK was not that the prose was
careless -- it was that ONE claim sat inside a sentence advertising a measurement and
had none behind it. So the assertion set is enumerated here as executable checks
rather than restated in a result document: it re-runs, and it fails loudly if the
prose or the code moves apart.

The rebind refusal itself is measured in `door_probe.py` (fresh processes; it also
reads the quoted fragment out of the specs rather than restating it). Everything
else is here. Exit 0 means every enumerated assertion holds.

Run: python3 .agent-work/567-d1/crew-scratch/g3-implementer-attempt-2-74e194cfc852/verify_claims.py
"""
import copy
import os
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard")
SKILLS = Path("/home/tommy/.claude/skills")
IMPL_SPEC = REPO / "specs/implementer.spine.toml"
REV_SPEC = REPO / "specs/reviewer.spine.toml"

sys.path.insert(0, str(REPO / "scripts"))

FAILURES: list[str] = []
CHECKED = 0


def check(cond: bool, claim: str, measurement: str) -> None:
    global CHECKED
    CHECKED += 1
    print(f"{'PASS' if cond else 'FAIL'}  {claim}\n        <- {measurement}")
    if not cond:
        FAILURES.append(claim)


def imperative(spec_path: Path) -> str:
    spec = tomllib.loads(spec_path.read_text(encoding="utf-8"))
    return spec["gate"][0]["imperative"]


IMPL_TEXT = imperative(IMPL_SPEC)
REV_TEXT = imperative(REV_SPEC)
IMPL_RAW = IMPL_SPEC.read_text(encoding="utf-8")
REV_RAW = REV_SPEC.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# 1. The repaired clause: the check it names, named as the role skills name it
# --------------------------------------------------------------------------- #
def role_skill(name: str) -> str:
    """The INSTALLED role skill -- what a dispatched crew actually loads. The repo's
    skills/<role>/SKILL.md is the source it is installed from; both are checked, so
    the claim cannot be true of only one of them."""
    return (SKILLS / f"constellation-{name}" / "SKILL.md").read_text(encoding="utf-8")


for role in ("implementer", "reviewer"):
    installed = role_skill(role)
    in_repo = (REPO / "skills" / role / "SKILL.md").read_text(encoding="utf-8")
    for src_label, text in (("installed skill", installed), ("skills/%s/SKILL.md" % role, in_repo)):
        check("the lease must cover every journaled action" in text,
              f"[{role}] the specs' phrase 'the lease must cover every journaled action' is the "
              f"role skill's own wording, not a paraphrase",
              f"{src_label}: substring present verbatim")
        check("terminal provenance check" in text,
              f"[{role}] 'terminal provenance check' is the INHERITED name for that check "
              f"-- the specs invent no third name",
              f"{src_label}: substring present verbatim")
        check("as your very last action" in text,
              f"[{role}] 'your role skill holds the lease open until your last action' "
              f"restates a rule the role skill states",
              f"{src_label}: 'as your very last action' present verbatim")

check("archive gate" not in IMPL_RAW and "archive gate" not in REV_RAW,
      "the blocked clause is gone: neither spec names an 'archive gate'",
      "substring absent from both spec files")

for label, text in (("implementer", IMPL_TEXT), ("reviewer", REV_TEXT)):
    check("terminal provenance check" in text and "the lease must cover every journaled action" in text,
          f"[{label}] the repair landed in this file's imperative",
          "both phrases present in the compiled-through imperative")

# The two files must carry the repaired clause identically (the reviewer flagged the
# paragraph as a linked pair, so divergence here is the defect to catch).
CLAUSE_RE = re.compile(r"and that\s+escape is not yours to take:.*?the escape never\s+arises\.", re.S)
impl_clause = CLAUSE_RE.search(IMPL_TEXT)
rev_clause = CLAUSE_RE.search(REV_TEXT)
check(bool(impl_clause) and bool(rev_clause)
      and " ".join(impl_clause.group().split()) == " ".join(rev_clause.group().split()),
      "both specs carry the repaired clause with identical wording",
      "regex-extracted clause, whitespace-normalised, compared between files")


# --------------------------------------------------------------------------- #
# 2. "starts with SPINE_FILE and SPINE_SESSION already in its environment"
# --------------------------------------------------------------------------- #
import run_crew  # noqa: E402

def door_env(spine: str | None, ambient: dict[str, str]) -> dict[str, str]:
    """`_crew_door_env` under a CONTROLLED ambient environment.

    Controlling it is the point: with `spine=None` the launcher deliberately leaves
    the inherited route untouched, so a dispatcher that itself has
    SPINE_FILE/SPINE_SESSION ambient passes ITS OWN pair down to a no-spine child.
    Reading os.environ as it happens to be gives a different answer depending on who
    runs this check -- which is exactly what happened the first time the engine ran
    it, from a door process that had the pair set."""
    saved = {k: os.environ.get(k) for k in ("SPINE_FILE", "SPINE_SESSION")}
    try:
        for k in saved:
            os.environ.pop(k, None)
        os.environ.update(ambient)
        return run_crew._crew_door_env(
            work_id="probe", gate="g0", role="implementer",
            spine=spine, root=REPO, parent="probe-parent")
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


AMBIENT_PAIR = {"SPINE_FILE": "/tmp/dispatcher-spine.json",
                "SPINE_SESSION": "constellation/the-dispatchers-own"}

with_spine = door_env(".agent-work/probe/PLAN.json", {})
without_spine = door_env(None, {})
inherited = door_env(None, AMBIENT_PAIR)

check("SPINE_FILE" in with_spine and "SPINE_SESSION" in with_spine,
      "a role dispatched WITH a spine of its own starts with SPINE_FILE and "
      "SPINE_SESSION already in its environment",
      f"run_crew._crew_door_env(spine=...) -> {sorted(k for k in with_spine if k.startswith('SPINE'))}")
check("SPINE_FILE" not in without_spine and "SPINE_SESSION" not in without_spine,
      "a role dispatched WITHOUT one is bound to nothing BY THE LAUNCHER -- its door is "
      "unbound and it holds no lease of its own",
      f"run_crew._crew_door_env(spine=None), no ambient pair -> "
      f"{sorted(k for k in without_spine if k.startswith('SPINE'))}")
check(inherited.get("SPINE_FILE") == AMBIENT_PAIR["SPINE_FILE"],
      "and where a no-spine child does arrive with the pair set, it is the DISPATCHER's "
      "own, passed through untouched -- so 'unbound' is a state the door reports, never "
      "one to assume",
      f"run_crew._crew_door_env(spine=None) under an ambient pair -> "
      f"SPINE_FILE={inherited.get('SPINE_FILE')!r} (the dispatcher's)")
derived = with_spine.get("SPINE_SESSION", "")
check(all(part in derived for part in ("probe", "g0", "implementer")),
      "and that identity is DERIVED from the assignment, not supplied as a free string "
      "(the spec's 'never from a string you supply' is scoped to the unbound bind, which "
      "door_probe measures against the spine's own work id)",
      f"run_crew._crew_door_env -> SPINE_SESSION={derived!r}, built from (work_id, gate, role)")


# --------------------------------------------------------------------------- #
# 3. "no session id is passed anywhere" + the tool inventory the prose lists
# --------------------------------------------------------------------------- #
import mcp_spine_server as door  # noqa: E402

TOOLS = {t["name"]: t for t in door.TOOLS}


def props(name: str) -> dict:
    return TOOLS[name].get("inputSchema", {}).get("properties", {}) or {}


def actions(name: str) -> set[str]:
    return set(props(name).get("action", {}).get("enum", []))


session_args = {n: [p for p in props(n) if "session" in p.lower()] for n in TOOLS}
check(not any(session_args.values()),
      "no session id is passed to the door -- no tool takes one",
      f"every tool's inputSchema properties scanned for a 'session' argument: "
      f"{sum(len(v) for v in session_args.values())} found across {len(TOOLS)} tools")

INVENTORY = [
    ("spine_status", "reads where you are", lambda: not (TOOLS["spine_status"]["inputSchema"].get("required") or [])),
    ("spine_start", "opens a gate", lambda: "task_id" in TOOLS["spine_start"]["inputSchema"].get("required", [])),
    ("spine_advance", "closes one", lambda: "task_id" in TOOLS["spine_advance"]["inputSchema"].get("required", [])),
    ("spine_evidence", "attests or attaches", lambda: {"attest", "attach"} <= actions("spine_evidence")),
    ("spine_lease", "claims and gives back the working lease", lambda: {"claim", "release"} <= actions("spine_lease")),
    ("spine_capture", "appends an item or flags a triage candidate",
     lambda: actions("spine_capture") == {"append", "flag-candidate"}),
    ("spine_halt", "blocks", lambda: "block" in actions("spine_halt")),
    ("spine_amend", "re-plans under a named authority",
     lambda: "authority" in props("spine_amend")),
    ("spine_bind", "an unbound door binds one spine", lambda: "spine_bind" in door.TOOL_NAMES),
]
for name, phrase, probe in INVENTORY:
    check(name in TOOLS and probe(),
          f"the implementer spec says {name} {phrase}",
          f"scripts/mcp_spine_server.py TOOLS[{name!r}] schema")

check("spine_amend" in TOOLS and "authority" in (TOOLS["spine_amend"]["inputSchema"].get("required") or []),
      "'under a NAMED authority' -- the authority is required, not optional",
      f"spine_amend required={TOOLS['spine_amend']['inputSchema'].get('required')}")

# The reviewer spec's dialect sentence.
check(actions("spine_survey_result") == {"record", "consolidate"},
      "the reviewer spec says spine_survey_result records each item pass or fail AND "
      "consolidates the verdict at the end",
      f"spine_survey_result action enum = {sorted(actions('spine_survey_result'))}")
check("Survey-type plans only" in TOOLS["spine_survey_result"]["description"],
      "and that it is the survey dialect's verb, not a shared one",
      f"spine_survey_result description opens {TOOLS['spine_survey_result']['description'][:28]!r}")


# --------------------------------------------------------------------------- #
# 4. "spine_advance is the gated plan's closing verb and is not yours"
#    Measured on the engine, not on the text that describes it.
# --------------------------------------------------------------------------- #
import checklist_engine as engine  # noqa: E402

survey = json.loads((REPO / ".agent-work/templates/REVIEW_SURVEY.template.json")
                    .read_text(encoding="utf-8").replace("<work-id>", "probe"))
gated = json.loads((REPO / ".agent-work/templates/IMPLEMENTER_PLAN.template.json")
                   .read_text(encoding="utf-8").replace("<work-id>", "probe"))

try:
    engine.advance(copy.deepcopy(survey), survey["items"][0])
    refused, msg = False, "(no refusal)"
except engine.EngineError as exc:
    refused, msg = True, str(exc)
check(refused and "advance is for gated checklists" in msg,
      "the engine REFUSES advance on a survey -- so the gated verb genuinely is not "
      "the reviewer's",
      f"checklist_engine.advance(survey) -> EngineError {msg!r}")

try:
    engine.record(copy.deepcopy(gated), gated["items"][0], "pass", None)
    g_refused, g_msg = False, "(no refusal)"
except engine.EngineError as exc:
    g_refused, g_msg = True, str(exc)
check(g_refused,
      "and the refusal is symmetric -- record is not the gated plan's verb either, so "
      "'the survey dialect is not the gated one' is a real split",
      f"checklist_engine.record(gated) -> EngineError {g_msg!r}")


# --------------------------------------------------------------------------- #
# 5. "spine_evidence, spine_lease, spine_capture, spine_halt and spine_amend are
#    shared with every other plan" -- exercised on BOTH dialects.
# --------------------------------------------------------------------------- #
def with_condition(plan: dict, cond: dict) -> tuple[dict, str, str]:
    """A deepcopy of the template with one extra postcondition on its first item.
    The survey template ships conditions on r6-fowler alone, and that one is
    engine-checked -- so probing the shipped conditions would measure the condition's
    KIND, not the dialect. Injecting the same condition into both dialects is what
    isolates the variable this claim is about. In memory only; no file is written."""
    clone = copy.deepcopy(plan)
    iid = clone["items"][0]
    clone["tasks"][iid].setdefault("postconditions", []).append(cond)
    return clone, iid, cond["id"]


QUALITATIVE = {"id": "zz-probe", "statement": "probe", "check": None, "satisfied": False}
CHECKED_COND = {"id": "zz-probe", "statement": "probe", "satisfied": False,
                "check": {"kind": "command", "command": "true"}}

for label, plan in (("survey", survey), ("gated", gated)):
    ok, detail = True, ""
    try:
        clone, iid, cid = with_condition(plan, QUALITATIVE)
        engine.attest(clone, iid, cid, "postconditions", "probe")
        engine.flag_candidate(copy.deepcopy(plan), plan["items"][0], "probe candidate")
        engine.block(copy.deepcopy(plan), plan["items"][0], "probe blocker", "probe", "probe next")
    except Exception as exc:  # noqa: BLE001 -- any refusal falsifies the claim
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    check(ok,
          f"the shared verbs (evidence/capture/halt) work on a {label} plan too",
          f"checklist_engine.attest(qualitative) + flag_candidate + block on the {label} "
          f"template" + (f" -> {detail}" if detail else " -> no refusal"))

    # And where attest DOES refuse, it refuses on the condition's kind, identically in
    # both dialects -- so the refusal is not evidence against the verb being shared.
    clone, iid, cid = with_condition(plan, CHECKED_COND)
    try:
        engine.attest(clone, iid, cid, "postconditions", "probe")
        msg = "(no refusal)"
    except engine.EngineError as exc:
        msg = str(exc)
    check("engine-checked" in msg,
          f"and on a {label} plan an engine-checked condition refuses attest for the same "
          f"reason -- the split is condition kind, not dialect",
          f"checklist_engine.attest(command-checked) -> {msg!r}")


# --------------------------------------------------------------------------- #
# 6. The governing decision the prose cites by id
# --------------------------------------------------------------------------- #
door_src = (REPO / "scripts/mcp_spine_server.py").read_text(encoding="utf-8")
design_src = (REPO / "docs/CHECKLIST_ENGINE_DESIGN.md").read_text(encoding="utf-8")
check("decision:one-spine-per-process-stands" in door_src and
      "decision:one-spine-per-process-stands" in design_src,
      "'decision:one-spine-per-process-stands' is a real decision id, cited where the "
      "behaviour lives",
      "present in scripts/mcp_spine_server.py and docs/CHECKLIST_ENGINE_DESIGN.md")


# --------------------------------------------------------------------------- #
# 7. The header comment's own claims about the compiler
# --------------------------------------------------------------------------- #
import generate_spine  # noqa: E402

spec_dict = tomllib.loads(IMPL_RAW)
poisoned = copy.deepcopy(spec_dict)
poisoned["doctrine"] = "a top-level key an author might add"
poisoned["gate"][0]["doctrine"] = "a gate-level key an author might add"

faults_clean = generate_spine.spec_shape_faults(copy.deepcopy(spec_dict), repo_root=REPO)
faults_poisoned = generate_spine.spec_shape_faults(copy.deepcopy(poisoned), repo_root=REPO)
check([str(f) for f in faults_clean] == [str(f) for f in faults_poisoned],
      "spec_shape_faults has no unknown-key fault -- a new spec key is not refused",
      f"faults with and without two invented keys are identical "
      f"({len(faults_clean)} vs {len(faults_poisoned)})")

compiled_poisoned = generate_spine.compile_spec(poisoned)
check("doctrine" not in compiled_poisoned,
      "compile_spec builds the top level from a FIXED field list -- an unknown key is "
      "dropped silently",
      "compile_spec(spec + top-level 'doctrine') -> key absent from the compiled spine")
first_gate_id = spec_dict["gate"][0]["id"]
check("doctrine" not in compiled_poisoned["tasks"][first_gate_id],
      "_compile_gate does the same for every compiled task",
      f"compiled task {first_gate_id!r} keys = {sorted(compiled_poisoned['tasks'][first_gate_id])}")

compiled_clean = json.dumps(generate_spine.compile_spec(copy.deepcopy(spec_dict)))
check("Door vocabulary lives in" not in compiled_clean,
      "comments are dropped too -- doctrine in a comment is doctrine nobody is handed",
      "the header comment's own text is absent from the compiled spine")
check("one door drives one spine at a time" in compiled_clean
      and "terminal provenance check" in compiled_clean,
      "while the imperative's prose -- including the repaired clause -- DOES reach the "
      "compiled spine",
      "both phrases present in compile_spec's output")

qual = generate_spine.compile_condition(
    {"id": "c1", "statement": "a statement", "kind": "qualitative", "because": "the reason"},
    repo_root_token="<repo-root>")
check("the reason" in qual["statement"] and qual["check"] is None,
      "compile_condition folds a qualitative `because` into the statement -- so it is "
      "authored text an agent reads",
      f"compile_condition(qualitative) -> statement={qual['statement']!r}")


# --------------------------------------------------------------------------- #
# 8. The reviewer spec's pointer to its own worked example
# --------------------------------------------------------------------------- #
rev_spec = tomllib.loads(REV_RAW)
fowler = [g for g in rev_spec["gate"] if g["id"] == "r6-fowler"]
check(bool(fowler) and "REPAIR PATH" in fowler[0]["imperative"],
      "the reviewer spec's \"r6-fowler's own REPAIR PATH below\" points at text that is "
      "there",
      "specs/reviewer.spine.toml gate r6-fowler imperative contains 'REPAIR PATH'")


# --------------------------------------------------------------------------- #
# 9. The constraints arrays carry no claim the imperatives do not
# --------------------------------------------------------------------------- #
impl_constraints = " ".join(tomllib.loads(IMPL_RAW)["gate"][0].get("constraints", []))
rev_constraints = " ".join(rev_spec["gate"][0].get("constraints", []))
check("archive" not in impl_constraints and "archive" not in rev_constraints,
      "no constraint repeats the withdrawn archive-gate reason",
      "'archive' absent from both gates' constraints arrays")
check("spine_survey_result, never spine_advance" in rev_constraints,
      "the reviewer's third constraint states the engine refusal measured in section 4",
      "constraint text matches the measured behaviour")


# --------------------------------------------------------------------------- #
# 10. Both specs still parse, compile, and stay clear of the retirement guard
# --------------------------------------------------------------------------- #
for spec_path in (IMPL_SPEC, REV_SPEC):
    proc = subprocess.run([sys.executable, "scripts/generate_spine.py", str(spec_path.relative_to(REPO)),
                           "--out", f"/tmp/g3r2-verify-{spec_path.stem}.json", "--check-only"],
                          cwd=str(REPO), capture_output=True, text=True)
    check(proc.returncode == 0, f"{spec_path.name} compiles clean",
          f"generate_spine --check-only rc={proc.returncode}: {proc.stdout.strip() or proc.stderr.strip()}")

print(f"\n{CHECKED - len(FAILURES)}/{CHECKED} claim checks passed")
for label in FAILURES:
    print(f"  FAILED: {label}")
raise SystemExit(1 if FAILURES else 0)
