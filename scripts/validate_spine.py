#!/usr/bin/env python
"""Refuse a spine or spine template the engine cannot read, or that carries a
check which cannot fail.

Nothing in the corpus looked at a spine's own checks before this (issue
epic-559/c1, #518, #562): `checklist_engine.py` trusts the file it is handed
and only discovers a malformed shape or a vacuous check live, at the gate that
tries to close over it. This module is importable (`validate(spine)` returns
a `ValidationResult`, a `list[Fault]` with an added `.undecidable` channel) so
a future spine generator can refuse to emit past it; the CLI below is a thin
wrapper.

Two families of fault:

- **Shape** (`shape-*`): the file the engine cannot even walk -- the wrong
  top-level key, an `items`/`tasks` mismatch, a check `kind` the engine does
  not implement, a `gated` task missing its postconditions, a `survey` task
  missing `result`. These stop a spine dead, often before any rail text can
  print.
- **Falsifiability** (`falsifiable-*`): the file the engine walks fine but
  whose check can never demonstrate a failure -- see `references/` in the g2
  handoff for the four faults and the incidents that motivated each.

Some conditions cannot be evaluated at all -- e.g. a `command` check's pytest
`-k` selector, run under an interpreter that cannot import pytest. That is
not a `Fault` (the check may be perfectly sound) and it is not silence
either: it is reported on `ValidationResult.undecidable`, distinctly, so a
caller can tell "sound" from "I could not judge N of these" (#518's own
undecidable-silence defect, C1 of this epic).
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# Single source of truth for "which <token> families does the resolver own" --
# reused rather than re-declared so the two never drift apart (init_work_area.py
# is the resolver; this module only reads its regex, never edits that file).
from init_work_area import _RESOLVER_OWNED_TOKEN_RE  # noqa: E402

GATED = "gated"
SURVEY = "survey"

#: The engine's own mechanical surface (`checklist_engine.py::_check_condition`).
#: A `check.kind` outside this set raises a bare `EngineError` the first time the
#: engine actually evaluates it -- late, and never at plan-freeze.
IMPLEMENTED_CHECK_KINDS = {"command", "artifact", "git-change-policy"}


@dataclass(frozen=True)
class Fault:
    """One refusal reason. `where` is a task id, or `<top-level>` for a
    file-wide shape fault, or `<task>.<preconditions|postconditions>.<cond-id>`
    for a condition-scoped fault."""

    code: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.where}: {self.message}"


@dataclass(frozen=True)
class Undecidable:
    """One condition `validate()` could not evaluate -- not a `Fault` (the
    check might be perfectly sound), and not silence either. "Could not
    tell" and "checked, found nothing wrong" must never share a code path:
    the same file, run under two interpreters differing only in whether
    pytest is importable, must not print a clean `OK` under one and a real
    fault count under the other with no sign anything went unevaluated."""

    code: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.where}: {self.message}"


# --------------------------------------------------------------------------- #
# Shape faults -- a spine (or template) the engine cannot walk at all.
# --------------------------------------------------------------------------- #

#: Wrong top-level keys seen in the wild (the Admiral shipped two spines keyed
#: `gates` this week) -- named in the fault message when present, purely to
#: make the refusal legible; any other missing-`items` case still refuses.
_KNOWN_WRONG_TOP_LEVEL_KEYS = ("gates", "steps", "gate_ids")


def _shape_faults(spine: dict) -> list[Fault]:
    faults: list[Fault] = []
    if not isinstance(spine, dict):
        return [Fault("shape-not-object", "<top-level>", "the spine is not a JSON object")]

    raw_items = spine.get("items")
    if raw_items is None:
        wrong = next((k for k in _KNOWN_WRONG_TOP_LEVEL_KEYS if k in spine), None)
        hint = f" (found {wrong!r} instead)" if wrong else ""
        faults.append(Fault(
            "shape-missing-items", "<top-level>",
            "the top-level ordered list must be named `items`" + hint +
            " -- the engine's `current` reads `items` and raises a bare "
            "KeyError on the very first call otherwise, before any rail text "
            "can print",
        ))
        items: list = []
    elif not isinstance(raw_items, list):
        faults.append(Fault("shape-items-not-list", "<top-level>", "`items` must be a list of task ids"))
        items = []
    else:
        items = raw_items

    raw_tasks = spine.get("tasks")
    if not isinstance(raw_tasks, dict):
        faults.append(Fault("shape-tasks-not-dict", "<top-level>", "`tasks` must be an object mapping id -> task"))
        tasks: dict = {}
    else:
        tasks = raw_tasks

    item_ids = [i for i in items if isinstance(i, str)]
    for iid in item_ids:
        if iid not in tasks:
            faults.append(Fault(
                "shape-dangling-item", iid,
                f"`items` names {iid!r} but `tasks` has no such key",
            ))
    for tid in tasks:
        if tid not in item_ids:
            faults.append(Fault(
                "shape-orphan-task", tid,
                f"`tasks` defines {tid!r} but `items` never names it, so the "
                f"engine can never walk to it",
            ))

    spine_type = spine.get("type")
    if spine_type not in (GATED, SURVEY):
        faults.append(Fault(
            "shape-unknown-type", "<top-level>",
            f"`type` must be {GATED!r} or {SURVEY!r}, got {spine_type!r}",
        ))

    for tid in item_ids:
        task = tasks.get(tid)
        if not isinstance(task, dict):
            continue
        faults.extend(_shape_task_faults(tid, task, spine_type))
    return faults


def _shape_task_faults(tid: str, task: dict, spine_type) -> list[Fault]:
    faults: list[Fault] = []
    for which in ("preconditions", "postconditions"):
        conds = task.get(which)
        if conds is None:
            continue
        if not isinstance(conds, list):
            faults.append(Fault("shape-conditions-not-list", f"{tid}.{which}", f"`{which}` must be a list"))
            continue
        for cond in conds:
            if not isinstance(cond, dict):
                continue
            chk = cond.get("check")
            if chk is None:
                continue
            kind = chk.get("kind") if isinstance(chk, dict) else None
            if kind not in IMPLEMENTED_CHECK_KINDS:
                faults.append(Fault(
                    "shape-unknown-check-kind", f"{tid}.{which}.{cond.get('id', '?')}",
                    f"check kind {kind!r} is not one the engine implements "
                    f"({sorted(IMPLEMENTED_CHECK_KINDS)})",
                ))
            if kind == "artifact" and "match" in chk and not isinstance(chk.get("match"), dict):
                # decision:match-not-dict-is-shape-fault -- the engine's own
                # comparator (`_artifact_match_satisfied`) assumes a dict and
                # both call sites now guard this themselves rather than
                # crashing, but a spine that ships this shape is still wrong
                # to author: blocking, not the falsifiable/report-only family.
                faults.append(Fault(
                    "shape-artifact-match-not-dict", f"{tid}.{which}.{cond.get('id', '?')}",
                    f"`match` must be an object mapping field -> value (or "
                    f"value-list), got {type(chk.get('match')).__name__}",
                ))

    if spine_type == GATED:
        post = task.get("postconditions")
        if not isinstance(post, list) or len(post) == 0:
            faults.append(Fault(
                "shape-gated-missing-postconditions", tid,
                "a `gated` task needs a `postconditions` list with at least one "
                "condition -- the engine requires >=1 to ever close this gate",
            ))
        pre = task.get("preconditions")
        if pre is not None and not isinstance(pre, list):
            faults.append(Fault("shape-conditions-not-list", f"{tid}.preconditions", "`preconditions` must be a list"))

    if spine_type == SURVEY and "result" not in task:
        faults.append(Fault(
            "shape-survey-missing-result", tid,
            "a `survey` task needs a `result` field (pass/fail/null) -- the "
            "item IS the check, and the engine records its outcome there",
        ))
    return faults


# --------------------------------------------------------------------------- #
# Falsifiability faults -- the file the engine walks fine, but whose check
# cannot fail. Each fault below is `_fault_*(...) -> list[Fault]`, all fed by
# `validate()`'s single walk over every condition.
# --------------------------------------------------------------------------- #

def _fault_all_null(tid: str, task: dict, spine_type) -> list[Fault]:
    """Fault 1: every postcondition's check is null. Across 113 archived
    spines zero have every check null -- this is authorable (the Admiral did
    it five times this epic) and undetectable at read time."""
    if spine_type != GATED:
        return []
    post = task.get("postconditions")
    if not isinstance(post, list):
        return []
    conds = [c for c in post if isinstance(c, dict)]
    if conds and all(c.get("check") is None for c in conds):
        return [Fault(
            "falsifiable-all-null", tid,
            "every postcondition's check is null -- nothing here can ever "
            "refuse this gate; give at least one condition a real check, or "
            "if it is genuinely qualitative, that is still a choice a reviewer "
            "should see stated, not the gate's only property",
        )]
    return []


_PYTEST_SEGMENT_SPLIT_RE = re.compile(r"&&|\|\||;|\|")

#: shlex has no notion of `$(...)` command substitution, so in the corpus's
#: own idiom (`test $(python -m pytest ...)`) the interpreter token tokenizes
#: attached to its opening paren as one word, `"$(python"`. Strip it before
#: treating the token as an interpreter name, or `shutil.which("$(python")`
#: never resolves and every idiom-shaped check reads as undecidable.
_COMMAND_SUBSTITUTION_PREFIX_RE = re.compile(r"^\$\(+")


def _pytest_segments(command: str) -> list[tuple[str | None, list[str]]]:
    """Every shell segment of `command` that invokes `pytest`, as
    `(interpreter, argv_tail)`. `argv_tail` is the tokens after the `pytest`
    word itself; `interpreter` is the token naming which Python ran it (e.g.
    `"python3"` in `python3 -m pytest ...`), or `None` when the segment
    invokes the `pytest` binary directly with no `-m`. A command can chain
    several segments (`test $(... --collect-only ...) -ge N && pytest ...`);
    each is inspected independently."""
    segments = []
    for seg in _PYTEST_SEGMENT_SPLIT_RE.split(command):
        seg = seg.strip()
        if not seg:
            continue
        try:
            tokens = shlex.split(seg)
        except ValueError:
            continue
        if "pytest" not in tokens:
            continue
        idx = tokens.index("pytest")
        interpreter = None
        if idx >= 2 and tokens[idx - 1] == "-m":
            interpreter = _COMMAND_SUBSTITUTION_PREFIX_RE.sub("", tokens[idx - 2])
        segments.append((interpreter, tokens[idx + 1:]))
    return segments


def _selector(args: list[str]) -> str | None:
    if "-k" in args:
        i = args.index("-k")
        if i + 1 < len(args):
            return args[i + 1]
    return None


#: A shell-redirect-shaped token (`2>/dev/null`, `>out.txt`, `2>&1`,
#: `&>/dev/null`) -- shlex has no notion of shell redirection, so these
#: tokenize as ordinary words indistinguishable from a positional argument.
#: In the corpus's own recommended self-checking idiom (`test $(pytest
#: --collect-only 2>/dev/null | grep -c '::') -ge N && pytest ...`) the
#: `2>/dev/null` token lands right after `pytest` in the first segment;
#: without this exclusion `_pytest_targets` folds it in as a bogus positional
#: test path, which then genuinely collects zero and is reported as a fault
#: -- an 8-in-9 false positive rate on the real archive.
_REDIRECT_TOKEN_RE = re.compile(r"^\d*&?(>>|>|<<|<)")

#: The subset of the above that is the operator ALONE, with no destination
#: attached (`2>` rather than `2>/dev/null`) -- shlex splits `2> /dev/null`
#: (a space before the destination) into two separate tokens, so the token
#: immediately following a bare operator must be excluded too.
_REDIRECT_OPERATOR_ONLY_RE = re.compile(r"^\d*&?(>>|>|<<|<)$")


def _pytest_targets(args: list[str]) -> list[str]:
    out = []
    skip = False
    for a in args:
        if skip:
            skip = False
            continue
        if a == "-k":
            skip = True
            continue
        if a.startswith("-"):
            continue
        if _REDIRECT_TOKEN_RE.match(a):
            if _REDIRECT_OPERATOR_ONLY_RE.match(a):
                skip = True
            continue
        out.append(a)
    return out


#: Resolved-interpreter cache within one process: the same interpreter name
#: (usually "python") recurs across every selector in a sweep, and each
#: resolution spawns a probe subprocess.
_INTERPRETER_CACHE: dict[str, str | None] = {}


def _resolve_interpreter(named: str | None) -> str | None:
    """The python executable to actually run pytest with, or `None` if that
    cannot be determined -- "cannot tell" is not a fault (#518 mechanism 2).

    Never falls back to `sys.executable` when the check's own command text
    names an interpreter: `sys.executable` is whichever python is running
    THIS tool, which need not be the interpreter the check invokes. On this
    host `python3` has no `pytest` importable while `python` does --
    `python3 -m scripts.validate_spine` previously reported 6 spurious
    zero-collect faults (sys.executable = python3, no pytest, empty output
    misread as "collected nothing") where `python -m scripts.validate_spine`
    on the identical file reported 0. Resolving the NAMED interpreter fixes
    both invocations identically, regardless of which python runs this tool.
    Confirms `pytest` is actually importable there before ever trusting an
    empty collection result as a real zero, rather than assuming it.
    """
    candidate = named or sys.executable
    if candidate in _INTERPRETER_CACHE:
        return _INTERPRETER_CACHE[candidate]
    path = candidate if Path(candidate).is_absolute() else shutil.which(candidate)
    resolved: str | None = None
    if path and Path(path).exists():
        try:
            probe = subprocess.run(
                [path, "-c", "import pytest"], capture_output=True, timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            probe = None
        if probe is not None and probe.returncode == 0:
            resolved = path
    _INTERPRETER_CACHE[candidate] = resolved
    return resolved


class _CollectOutcome(Enum):
    """The result of trying to find out whether one pytest -k segment
    collects zero tests. `NOT_APPLICABLE` (no -k selector at all) and
    `UNDECIDABLE` (pytest could not be run to find out) both mean "no
    fault", but they are not the same thing and must not be reported the
    same way: `NOT_APPLICABLE` is "nothing to check here", `UNDECIDABLE` is
    "there was something to check and I could not check it"."""

    ZERO = "zero"
    SOME = "some"
    NOT_APPLICABLE = "not-applicable"
    UNDECIDABLE = "undecidable"


def _collects_zero(interpreter: str | None, args: list[str], repo_root: Path) -> tuple[_CollectOutcome, str | None]:
    """Actually run `pytest --collect-only` with this segment's own `-k`
    selector and targets, using the interpreter the check's command names
    (never a silent `sys.executable` fallback -- see `_resolve_interpreter`).
    Returns `(outcome, reason)`: `reason` is only set for `UNDECIDABLE` --
    no interpreter with pytest importable resolved, or the subprocess
    itself failed/timed out: environment trouble, not a verdict, and
    undecidable is not a fault. `NOT_APPLICABLE` (no `-k` in this segment)
    is a different kind of nothing-to-report and carries no reason."""
    selector = _selector(args)
    if selector is None:
        return _CollectOutcome.NOT_APPLICABLE, None
    python = _resolve_interpreter(interpreter)
    if python is None:
        named = interpreter or sys.executable
        return _CollectOutcome.UNDECIDABLE, (
            f"no interpreter named {named!r} resolved with pytest importable"
        )
    targets = _pytest_targets(args)
    cmd = [python, "-m", "pytest", "--collect-only", "-q", "-k", selector, *targets]
    try:
        proc = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _CollectOutcome.UNDECIDABLE, f"{python} -m pytest --collect-only failed to run: {exc}"
    if "::" in proc.stdout:
        return _CollectOutcome.SOME, None
    return _CollectOutcome.ZERO, None


def _fault_zero_collect(where: str, check: dict, repo_root: Path) -> tuple[list[Fault], list[Undecidable]]:
    """Fault 2: a `command` check's pytest `-k` selector collects zero tests
    -- the issue-456 recurrence, mechanical and needing no semantics (#518).
    A segment whose outcome could not be determined at all (no interpreter
    with pytest importable resolved, or the subprocess failed) is reported
    on the second, `Undecidable` return value instead -- never folded into
    the fault list, and never silently dropped either."""
    faults: list[Fault] = []
    undecidable: list[Undecidable] = []
    if check.get("kind") != "command":
        return faults, undecidable
    command = check.get("command")
    if not isinstance(command, str):
        return faults, undecidable
    seen = set()
    for interpreter, args in _pytest_segments(command):
        sel = _selector(args)
        if sel is None or sel in seen:
            continue
        seen.add(sel)
        outcome, reason = _collects_zero(interpreter, args, repo_root)
        if outcome is _CollectOutcome.ZERO:
            faults.append(Fault(
                "falsifiable-zero-collected", where,
                f"the pytest selector -k {sel!r} in this check collects zero "
                f"tests -- it can never fail, which is exactly as vacuous as "
                f"`check: null`",
            ))
        elif outcome is _CollectOutcome.UNDECIDABLE:
            undecidable.append(Undecidable(
                "undecidable-zero-collect", where,
                f"could not evaluate whether -k {sel!r} collects any tests: {reason}",
            ))
    return faults, undecidable


#: A statement asserting a PROPERTY (a specific value/outcome), not mere
#: arrival. Deliberately narrow (false positive > miss, per the handoff): an
#: enum-like "is <Value>"/"is true/false", an explicit comparison, or a
#: negated-property claim ("no unresolved blockers"). "REVIEW_RESULT returned"
#: matches none of these; "reviewer verdict is APPROVE" and "...with no
#: unresolved blockers" (the real #562 wording) both do.
_PROPERTY_ASSERTION_RE = re.compile(
    r"\bis\s+(?:not\s+)?[A-Z][A-Za-z0-9_-]*\b"
    r"|\bis\s+(?:not\s+)?(?:true|false)\b"
    r"|==|!=|\bequals?\b|\bmatches?\b"
    r"|\bno\s+\w+(?:\s+\w+){0,3}\b"
    r"|\bat least\b",
    re.IGNORECASE,
)

#: ACCEPTED exception: a `user-decision` artifact has no structured field to
#: `match` against at all -- the human's decision text IS the property, there
#: is nothing else to name. Every bare (no-`match`) artifact check in the
#: shipped corpus except the honest `g1-review.c1` is this evidence_type.
ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH = {"user-decision"}


def _fault_artifact_no_match(where: str, cond: dict, check: dict) -> list[Fault]:
    """Fault 3 (#562): an `artifact` check with no `match` whose statement
    asserts a property. The engine's `all(... for k, v in want.items())` over
    an empty `match` is vacuously true, so ANY arrival of that evidence_type
    satisfies a statement that claims something specific about it."""
    if check.get("kind") != "artifact":
        return []
    if check.get("match"):
        return []
    evidence_type = check.get("evidence_type")
    if evidence_type in ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH:
        return []
    statement = cond.get("statement")
    if not isinstance(statement, str):
        return []
    if _PROPERTY_ASSERTION_RE.search(statement):
        return [Fault(
            "falsifiable-artifact-asserts-property", where,
            f"statement {statement!r} asserts a property but the artifact "
            f"check carries no `match`, so any arrival of evidence_type "
            f"{evidence_type!r} satisfies it -- add a `match` for the field "
            f"this claims, or weaken the statement to bare arrival",
        )]
    return []


#: The JSON-scalar element types a `match[k]` list value may legally contain
#: (decision:malformed-list-definition) -- `bool` is deliberately included
#: even though `isinstance(True, int)` is also true; both are JSON scalars.
_JSON_SCALAR_TYPES = (str, int, float, bool, type(None))


def _fault_artifact_malformed_match_list(where: str, check: dict) -> list[Fault]:
    """Report-only sibling to `_fault_artifact_no_match`: a `match[k]` list
    value that is empty, or that contains an element that is not a JSON
    scalar (decision:malformed-list-definition). A single-element list is a
    legitimate (if odd) membership check and is NOT flagged. This is a
    falsifiable-family fault but ships report-only -- see
    `REPORT_ONLY_FAULT_CODES` -- because the widening it audits
    (decision:match-shape-bare-list) ships live and this repo's shipped
    corpus has never authored a list-valued `match` at all, so there is no
    live-corpus evidence yet that this shape is ever a real mistake vs. a
    legitimate but unusual author choice."""
    if check.get("kind") != "artifact":
        return []
    match = check.get("match")
    if not isinstance(match, dict):
        return []
    faults = []
    for k, v in match.items():
        if not isinstance(v, list):
            continue
        if len(v) == 0:
            faults.append(Fault(
                "falsifiable-artifact-malformed-match-list", where,
                f"match[{k!r}] is an empty list -- membership against an "
                f"empty list can never be satisfied, which is exactly as "
                f"vacuous (in the opposite direction) as `check: null`",
            ))
            continue
        if any(not isinstance(el, _JSON_SCALAR_TYPES) for el in v):
            faults.append(Fault(
                "falsifiable-artifact-malformed-match-list", where,
                f"match[{k!r}] is a list containing a non-scalar element -- "
                f"membership only makes sense against JSON scalars "
                f"(str/int/float/bool/None)",
            ))
    return faults


#: A bracket token in a `command` check's text that content-shapes like a
#: placeholder (starts with a letter; letters/digits/space/./-/_ inside) --
#: narrow enough to leave shell redirection (`< file`, no closing `>`) and
#: numeric comparisons alone.
_PLACEHOLDER_TOKEN_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9 _./-]{0,60})>")

#: `resolve_spine` also special-cases the BARE `<skill-dir>` token (no role
#: prefix) via a hardcoded call, outside the `_ROLE_SKILL_DIR_RE`-discovered
#: family -- so it is genuinely resolved before a spine is ever driven
#: (EXPLORER_SPINE.template.json ships it), but `_RESOLVER_OWNED_TOKEN_RE`'s
#: own alternation never names it (`[a-zA-Z0-9-]+-skill-dir` requires a
#: nonempty prefix before `-skill-dir`, which a bare `skill-dir` has none of).
#: Measured live: without this, the checker false-positived on every shipped
#: `<skill-dir>` use. Named here rather than fixed in init_work_area.py --
#: that resolver is out of this gate's scope, and this checker must not
#: refuse a token the real resolver already handles correctly.
_BARE_RESOLVER_TOKENS = {"<skill-dir>"}


def _fault_unresolved_placeholder(where: str, check: dict) -> list[Fault]:
    """Fault 4: a `command` check whose text still carries a literal
    `<placeholder>` after instantiation. ACCEPTED exception: the resolver-owned
    token families (`<work-id>`, `<repo-root>`, `<*-skill-dir>`, `<skill-dir>`,
    `<*-session-id>`) -- `init_work_area.resolve_spine` substitutes every one
    of these before a spine is ever driven, so their presence in a template is
    the mechanism working, not a fault. Anything else (`<fowler-pass-record-
    path>`, `<exact test command>`) is a token nothing will ever substitute."""
    if check.get("kind") != "command":
        return []
    command = check.get("command")
    if not isinstance(command, str):
        return []
    faults = []
    seen = set()
    for m in _PLACEHOLDER_TOKEN_RE.finditer(command):
        literal = f"<{m.group(1)}>"
        if literal in seen:
            continue
        if _RESOLVER_OWNED_TOKEN_RE.fullmatch(literal) or literal in _BARE_RESOLVER_TOKENS:
            continue
        seen.add(literal)
        faults.append(Fault(
            "falsifiable-unresolved-placeholder", where,
            f"command still carries the literal placeholder {literal!r} -- "
            f"nothing resolves it, so the check can never run, let alone fail",
        ))
    return faults


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

#: Fault codes that are computed like any other but never blocking --
#: `validate()` routes them into `.report_only` instead of the base list, so
#: they can never flip `any_faults`/`bool(result)` at either call site
#: (`generate_spine.py`, `spine_lifecycle.py` -- both checked, both gate on
#: base-list truthiness only). decision:widening-ships-live-refusal-ships-report-only.
#:
#: Promotion trigger (decision:promotion-trigger), verbatim: promote a code
#: to blocking when (a) `validate_spine.py --sweep` reports zero occurrences
#: of it across the shipped corpus AND (b) the Admiral/human ratifies
#: decision:widening-ships-live-refusal-ships-report-only at the wave-2
#: checkpoint that decision already names -- then remove the code from this
#: set.
REPORT_ONLY_FAULT_CODES = {"falsifiable-artifact-malformed-match-list"}


class ValidationResult(list):
    """`validate()`'s return value. Behaves exactly like the `list[Fault]` it
    used to be -- every existing caller iterates it, indexes it, or tests its
    truthiness -- but carries a second channel, `.undecidable`, for
    conditions `validate()` could not evaluate at all (see `Undecidable`),
    and a third, `.report_only`, for faults computed the same way as any
    other but named in `REPORT_ONLY_FAULT_CODES` -- never part of the base
    list, so they can never affect `bool(result)`/exit code either.
    `str()` names all three, so a caller that only ever prints the result
    cannot mistake "0 faults, 3 undecidable, 1 report-only" for a clean pass."""

    def __init__(self, faults=(), undecidable=(), report_only=()):
        super().__init__(faults)
        self.undecidable: list[Undecidable] = list(undecidable)
        self.report_only: list[Fault] = list(report_only)

    def __str__(self) -> str:
        base = f"{len(self)} fault(s)" if self else "0 fault(s)"
        extras = []
        if self.undecidable:
            detail = "; ".join(str(u) for u in self.undecidable)
            extras.append(f"{len(self.undecidable)} undecidable: {detail}")
        if self.report_only:
            detail = "; ".join(str(f) for f in self.report_only)
            extras.append(f"{len(self.report_only)} report-only: {detail}")
        if not extras:
            return base
        return f"{base}, " + ", ".join(extras)

    __repr__ = __str__


def validate(spine: dict, *, repo_root: Path | None = None) -> ValidationResult:
    """Every fault in `spine` (a parsed spine or spine template): shape faults
    first, then falsifiability faults over every condition the shape allows
    the walk to reach. Never raises on a malformed shape -- that IS what shape
    faults report; the falsifiability walk below is fully defensive so a
    badly-shaped file still gets whatever falsifiability faults it can.

    The returned `ValidationResult` also carries `.undecidable`: conditions
    that could not be evaluated at all (e.g. a pytest `-k` selector whose
    interpreter cannot be resolved). Undecidable is not a fault -- the exit
    code does not change for it -- but it must never be indistinguishable
    from "checked, found nothing wrong"."""
    faults = list(_shape_faults(spine))
    undecidable: list[Undecidable] = []
    report_only: list[Fault] = []

    if not isinstance(spine, dict):
        return ValidationResult(faults, undecidable, report_only)
    repo_root = repo_root or Path.cwd()
    spine_type = spine.get("type")
    items = spine.get("items")
    items = [i for i in items if isinstance(i, str)] if isinstance(items, list) else []
    tasks = spine.get("tasks") if isinstance(spine.get("tasks"), dict) else {}

    for tid in items:
        task = tasks.get(tid)
        if not isinstance(task, dict):
            continue
        faults.extend(_fault_all_null(tid, task, spine_type))
        for which in ("preconditions", "postconditions"):
            conds = task.get(which)
            if not isinstance(conds, list):
                continue
            for cond in conds:
                if not isinstance(cond, dict):
                    continue
                check = cond.get("check")
                if not isinstance(check, dict):
                    continue
                where = f"{tid}.{which}.{cond.get('id', '?')}"
                seg_faults, seg_undecidable = _fault_zero_collect(where, check, repo_root)
                faults.extend(seg_faults)
                undecidable.extend(seg_undecidable)
                faults.extend(_fault_artifact_no_match(where, cond, check))
                faults.extend(_fault_unresolved_placeholder(where, check))
                for f in _fault_artifact_malformed_match_list(where, check):
                    (report_only if f.code in REPORT_ONLY_FAULT_CODES else faults).append(f)
    return ValidationResult(faults, undecidable, report_only)


GATED_OR_SURVEY_TYPES = (GATED, SURVEY)


def discover_checklist_templates(root: Path) -> list[Path]:
    """Every gated-or-survey checklist template the repo ships, enumerated by
    each file's own `type` field -- never a hand-maintained list (the Template
    set table in checklist-engine.md names 6 against a measured 12)."""
    found = []
    for path in sorted((root / "skills").glob("*/templates/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get("type") in GATED_OR_SURVEY_TYPES:
            found.append(path)
    return found


def validate_file(path: Path, *, repo_root: Path | None = None) -> ValidationResult:
    spine = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate(spine, repo_root=repo_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="spine/template JSON file(s) to validate")
    parser.add_argument("--root", default=".", help="repo root, for resolver-token acceptance and pytest -k collection (default: cwd)")
    parser.add_argument("--sweep", action="store_true", help="validate every shipped gated-or-survey template instead of --paths")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    paths = [Path(p) for p in args.paths]
    if args.sweep:
        paths = discover_checklist_templates(root)
        print(f"sweep: {len(paths)} gated-or-survey templates discovered under {root / 'skills'}")
    if not paths:
        parser.error("pass at least one path, or --sweep")

    # Exit-code semantics are unchanged: undecidable conditions never flip
    # `any_faults`. But the same run that would have printed a bare `OK`
    # -- the exact silence the operator-under-the-wrong-interpreter case
    # hides inside -- now also names how many conditions it could not judge,
    # so "sound" and "I could not tell" never look identical on screen.
    any_faults = False
    for path in paths:
        result = validate_file(path, repo_root=root)
        if result:
            any_faults = True
            print(f"{path}: {len(result)} fault(s)")
            for f in result:
                print(f"  {f}")
        else:
            print(f"{path}: OK")
        if result.undecidable:
            print(f"{path}: {len(result.undecidable)} undecidable")
            for u in result.undecidable:
                print(f"  {u}")
        if result.report_only:
            # Never folds into `any_faults` -- report-only findings are
            # printed for visibility alone (decision:widening-ships-live-refusal-ships-report-only).
            print(f"{path}: {len(result.report_only)} report-only")
            for f in result.report_only:
                print(f"  [REPORT-ONLY] {f}")
    return 1 if any_faults else 0


if __name__ == "__main__":
    sys.exit(main())
