#!/usr/bin/env python
"""Lint `@grade:` decision tags — a plan decision's fixedness as an inline,
greppable property of the decision itself, so no second hand-maintained ledger
ever has to exist.

Grammar (frozen by a prior 3-agent design panel; do NOT redesign here):

    @grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]

`·` is U+00B7 MIDDLE DOT, the field separator. `tier` is exactly one of
`settled`, `guess`, `placeholder` and is always required; `provenance`
(`human`, `measured`, `inherited`) is written suffixed to the tier as
`settled/human` and is required when tier is `settled` (absent -> WARN, never
FAIL); `leans` is a comma-separated list of gate/item ids in this plan and is
optional; `settle:` is one line naming the cheapest experiment and is required
when tier is `guess`. `@grade:` is the sole greppable anchor; only the tier is
hard-required, every other field degrades gracefully and never raises.

The tag welds to its decision either on the decision's own Markdown list-item
line, or on the next non-blank line as a child of that bullet (bare or wrapped
in single backticks — both accepted), or as a suffix appended to the decision
string itself in JSON (`"decision:foo — text @grade: guess · ..."`).

Three binding rulings from a cold-critic review (see g1-implement handoff,
issue #230, epic-226):

  1. `decision:md-decision-is-a-list-item` — in Markdown, a candidate decision
     is a LIST-ITEM LINE ONLY (matches ``^\\s*[-*+]\\s``) inside a recognized
     block. Prose sentences are never decisions.
  2. `decision:gl012-scoped-per-file` — contradictory-grade detection (GL012)
     is scoped per input file, never across files. Decision identity comes
     only from an explicit `decision:<id>` token; a decision with no such
     token is excluded from GL008/GL012 cross-occurrence comparison.
  3. `decision:placeholder-is-not-a-decision` — a decision payload that is
     ENTIRELY an angle-bracket placeholder (``^<.*>$`` after stripping the
     list marker and any wrapping backticks) is template scaffolding, not a
     decision, and is skipped everywhere — no ``--include-templates`` flag,
     no filename-based skipping.

THE FORK — `--mode preflight` (default) treats an ungraded decision in a
recognized block as GL001 UNGRADED_DECISION, a FAIL. `--mode execute` reads an
ungraded decision as implicitly `settled` and suppresses GL001 entirely. This
is a DIAGNOSTIC PREVIEW of the lenient execution-time reading, NOT enforcement:
nothing here is wired to `checklist_engine.py`, which does not parse `@grade:`
tags at all — "lint loud, execute safe."

Locality (invariant 7): this script NEVER creates, writes, reads, or caches a
ledger file. Every run recomputes its view from the inline tags alone.

Exit codes: 0 = pass, 1 = FAIL-severity violations present (or a WARN present
under --strict-warnings), 2 = tooling/usage error (missing file, invalid JSON,
bad flags) — matching argparse's own convention and the sibling
`scripts/verify_*.py` rails.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MIDDOT = "·"

TIERS = {"settled", "guess", "placeholder"}

FAIL = "FAIL"
WARN = "WARN"

CODE_INFO = {
    "GL001": ("UNGRADED_DECISION", FAIL),
    "GL002": ("INVALID_TIER", FAIL),
    "GL003": ("MISSING_PROVENANCE", WARN),
    "GL004": ("GUESS_MISSING_SETTLE", FAIL),
    "GL005": ("DANGLING_LEAN", FAIL),
    "GL006": ("PLACEHOLDER_OVERSPECIFIED", FAIL),
    "GL007": ("MALFORMED_GRADE", FAIL),
    "GL008": ("DUPLICATE_GRADE", FAIL),
    "GL009": ("TBD_MARKER", WARN),
    "GL010": ("ORPHAN_GRADE", WARN),
    "GL011": ("NO_ID_SOURCE", WARN),
    "GL012": ("CONTRADICTORY_GRADE", FAIL),
}

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
RECOGNIZED_RE = re.compile(r"pre-rulings|decision anchors", re.IGNORECASE)
LIST_ITEM_RE = re.compile(r"^\s*[-*+]\s+")
PLACEHOLDER_RE = re.compile(r"^<.*>$", re.DOTALL)
DECISION_ID_RE = re.compile(r"\bdecision:([A-Za-z0-9_.\-]+)")
TBD_RE = re.compile(r"\b(TBD|TODO|CONTRADICTION)\b", re.IGNORECASE)
GRADE_MARKER = "@grade:"


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------


@dataclass
class GradeTag:
    tier: str | None
    provenance: str | None
    leans: list[str] = field(default_factory=list)
    settle: str | None = None
    malformed_segments: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class DecisionRecord:
    file: str
    location: str
    decision_id: str | None
    tag: GradeTag | None


@dataclass
class Violation:
    code: str
    name: str
    severity: str
    file: str
    location: str
    message: str


def make_violation(code: str, file: str, location, message: str) -> Violation:
    name, severity = CODE_INFO[code]
    return Violation(code=code, name=name, severity=severity, file=file,
                      location=str(location), message=message)


# --------------------------------------------------------------------------
# Shared grade-body parsing (Markdown and JSON funnel through this)
# --------------------------------------------------------------------------


def find_grade_occurrences(text: str) -> list[str]:
    """Every literal '@grade:' occurrence's body in `text`, each bounded by the
    next occurrence (or end of string). A trailing backtick closing a
    backtick-wrapped tag is stripped. Returns [] when no occurrence exists."""
    positions = [m.start() for m in re.finditer(re.escape(GRADE_MARKER), text)]
    bodies = []
    for i, pos in enumerate(positions):
        start = pos + len(GRADE_MARKER)
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        body = text[start:end].strip()
        if body.endswith("`"):
            body = body[:-1].rstrip()
        bodies.append(body)
    return bodies


def parse_grade_body(body: str) -> GradeTag:
    segments = [s.strip() for s in body.split(MIDDOT)]
    first = segments[0] if segments else ""
    if "/" in first:
        tier, _, provenance = first.partition("/")
        tier = tier.strip()
        provenance = provenance.strip() or None
    else:
        tier = first.strip()
        provenance = None

    leans: list[str] = []
    settle: str | None = None
    malformed: list[str] = []
    for seg in segments[1:]:
        seg_stripped = seg.strip()
        if not seg_stripped:
            continue
        if re.match(r"^leans\b", seg_stripped, re.IGNORECASE):
            rest = seg_stripped[len("leans"):].strip()
            leans = [x.strip() for x in rest.split(",") if x.strip()]
        elif re.match(r"^settle:", seg_stripped, re.IGNORECASE):
            settle = seg_stripped[len("settle:"):].strip()
        else:
            malformed.append(seg_stripped)

    return GradeTag(tier=tier or None, provenance=provenance, leans=leans,
                     settle=settle, malformed_segments=malformed, raw=body)


def strip_wrapping_backticks(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        return s[1:-1].strip()
    return s


def is_placeholder(payload: str) -> bool:
    return bool(PLACEHOLDER_RE.match(payload.strip()))


def extract_decision_id(s: str) -> str | None:
    m = DECISION_ID_RE.search(s)
    return m.group(1) if m else None


# --------------------------------------------------------------------------
# Markdown parsing — anchor-first, block-scoped
# --------------------------------------------------------------------------


def scan_block(file: str, block_lines: list[tuple[int, str]]) -> tuple[list[DecisionRecord], list[Violation]]:
    decisions: list[DecisionRecord] = []
    violations: list[Violation] = []

    for lineno, text in block_lines:
        if TBD_RE.search(text):
            violations.append(make_violation("GL009", file, lineno,
                                              "TBD/TODO/CONTRADICTION marker present"))

    n = len(block_lines)
    consumed_as_child: set[int] = set()

    def child_grade_bodies(idx: int) -> list[str]:
        """Grade bodies on the decision's child line, if any, marking that line
        consumed so it is not later mistaken for an orphan grade."""
        k = idx + 1
        while k < n and block_lines[k][1].strip() == "":
            k += 1
        if k >= n:
            return []
        k_text = block_lines[k][1]
        if LIST_ITEM_RE.match(k_text):
            return []
        bodies = find_grade_occurrences(k_text)
        if bodies:
            consumed_as_child.add(k)
        return bodies

    for idx in range(n):
        if idx in consumed_as_child:
            continue
        lineno, text = block_lines[idx]
        m = LIST_ITEM_RE.match(text)
        if m:
            payload_raw = text[m.end():].rstrip()
            payload = strip_wrapping_backticks(payload_raw)
            if is_placeholder(payload):
                # Template scaffolding is not a decision — and neither is a grade
                # welded to it, so consume the child line too rather than leaving
                # it to report as an orphan.
                child_grade_bodies(idx)
                continue
            decision_id = extract_decision_id(payload_raw)

            same_bodies = find_grade_occurrences(text)
            next_bodies = child_grade_bodies(idx)

            all_bodies = same_bodies + next_bodies
            if all_bodies:
                if len(all_bodies) > 1:
                    violations.append(make_violation(
                        "GL008", file, lineno,
                        "multiple @grade: tags welded to one decision"))
                tag = parse_grade_body(all_bodies[0])
            else:
                tag = None

            decisions.append(DecisionRecord(file=file, location=str(lineno),
                                             decision_id=decision_id, tag=tag))
        else:
            bodies = find_grade_occurrences(text)
            if bodies:
                violations.append(make_violation(
                    "GL010", file, lineno,
                    "@grade tag present with no decision to weld to"))

    return decisions, violations


def scan_markdown(file: str, text: str) -> tuple[list[DecisionRecord], list[Violation]]:
    lines = text.splitlines()
    decisions: list[DecisionRecord] = []
    violations: list[Violation] = []

    in_fence = False
    current_block_level: int | None = None
    current_block_lines: list[tuple[int, str]] = []

    def flush_block() -> None:
        nonlocal current_block_lines
        if current_block_lines:
            decs, viols = scan_block(file, current_block_lines)
            decisions.extend(decs)
            violations.extend(viols)
        current_block_lines = []

    for i, raw_line in enumerate(lines, start=1):
        if FENCE_RE.match(raw_line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading_m = HEADING_RE.match(raw_line)
        if heading_m:
            level = len(heading_m.group(1))
            heading_text = heading_m.group(2)
            if current_block_level is not None and level <= current_block_level:
                flush_block()
                current_block_level = None
            if RECOGNIZED_RE.search(heading_text):
                current_block_level = level
                current_block_lines = []
            continue

        if current_block_level is not None:
            current_block_lines.append((i, raw_line))

    flush_block()
    return decisions, violations


# --------------------------------------------------------------------------
# JSON parsing — structural walk, never regex over raw text
# --------------------------------------------------------------------------


def extract_plan_ids(data) -> set[str]:
    """The known gate/item id universe a JSON plan self-sources: its top-level
    `items` list plus its `tasks` keys."""
    ids: set[str] = set()
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            ids.update(str(x) for x in items)
        tasks = data.get("tasks")
        if isinstance(tasks, dict):
            ids.update(str(k) for k in tasks.keys())
    elif isinstance(data, list):
        ids.update(str(x) for x in data)
    return ids


def scan_json(file: str, data) -> tuple[list[DecisionRecord], list[Violation]]:
    decisions: list[DecisionRecord] = []
    violations: list[Violation] = []

    def handle_anchor_list(entries: list, path_prefix: str) -> None:
        for idx, entry in enumerate(entries):
            if not isinstance(entry, str):
                continue
            loc = f"{path_prefix}[{idx}]"
            payload = strip_wrapping_backticks(entry)
            if is_placeholder(payload):
                continue
            if TBD_RE.search(entry):
                violations.append(make_violation(
                    "GL009", file, loc, "TBD/TODO/CONTRADICTION marker present"))
            decision_id = extract_decision_id(entry)
            bodies = find_grade_occurrences(entry)
            if bodies:
                if len(bodies) > 1:
                    violations.append(make_violation(
                        "GL008", file, loc,
                        "multiple @grade: tags welded to one decision"))
                tag = parse_grade_body(bodies[0])
            else:
                tag = None
            decisions.append(DecisionRecord(file=file, location=loc,
                                             decision_id=decision_id, tag=tag))

    if isinstance(data, dict):
        top_anchors = data.get("anchors")
        if isinstance(top_anchors, dict):
            dec_list = top_anchors.get("decision")
            if isinstance(dec_list, list):
                handle_anchor_list(dec_list, "anchors.decision")

        tasks = data.get("tasks")
        if isinstance(tasks, dict):
            for task_id, task_obj in tasks.items():
                if not isinstance(task_obj, dict):
                    continue
                anchors = task_obj.get("anchors")
                if not isinstance(anchors, dict):
                    continue
                dec_list = anchors.get("decision")
                if isinstance(dec_list, list):
                    handle_anchor_list(dec_list, f"tasks.{task_id}.anchors.decision")

    return decisions, violations


# --------------------------------------------------------------------------
# Shared validation over a parsed tag struct (Markdown and JSON cannot diverge)
# --------------------------------------------------------------------------


def validate_decision(dec: DecisionRecord, known_ids: set[str], ids_provided: bool,
                       mode: str) -> list[Violation]:
    violations: list[Violation] = []
    tag = dec.tag

    if tag is None:
        if mode == "preflight":
            violations.append(make_violation(
                "GL001", dec.file, dec.location, "decision has no @grade tag"))
        return violations  # execute mode: ungraded reads as settled, nothing else to check

    if tag.tier not in TIERS:
        violations.append(make_violation(
            "GL002", dec.file, dec.location,
            f"invalid tier {tag.tier!r}; want one of {sorted(TIERS)}"))

    if tag.malformed_segments:
        violations.append(make_violation(
            "GL007", dec.file, dec.location,
            f"unparseable segment(s): {tag.malformed_segments!r}"))

    if tag.tier == "settled" and not tag.provenance:
        violations.append(make_violation(
            "GL003", dec.file, dec.location, "settled tier missing provenance"))

    if tag.tier == "guess" and not (tag.settle and tag.settle.strip()):
        violations.append(make_violation(
            "GL004", dec.file, dec.location, "guess tier missing settle:"))

    if tag.tier == "placeholder" and (tag.provenance or (tag.settle and tag.settle.strip())):
        violations.append(make_violation(
            "GL006", dec.file, dec.location,
            "placeholder tier must not carry provenance or settle"))

    if tag.leans:
        if ids_provided:
            for unknown in [x for x in tag.leans if x not in known_ids]:
                violations.append(make_violation(
                    "GL005", dec.file, dec.location,
                    f"leans id {unknown!r} does not resolve to a known gate/item id"))
        # else: no id source supplied -- GL005 is skipped; caller emits GL011.

    return violations


def cross_occurrence_violations(file: str, decisions: list[DecisionRecord]) -> list[Violation]:
    """GL008 (same decision id repeated with the same tier) and GL012 (same
    decision id repeated with conflicting tiers), scoped to THIS file only
    (ruling: decision:gl012-scoped-per-file). Decisions with no id token are
    excluded from this comparison."""
    violations: list[Violation] = []
    by_id: dict[str, list[DecisionRecord]] = {}
    for dec in decisions:
        if dec.decision_id:
            by_id.setdefault(dec.decision_id, []).append(dec)

    for did, group in by_id.items():
        graded = [d for d in group if d.tag is not None]
        if len(graded) < 2:
            continue
        tiers = {d.tag.tier for d in graded}
        locations = ", ".join(f"{d.file}:{d.location}" for d in graded)
        if len(tiers) > 1:
            violations.append(make_violation(
                "GL012", file, locations,
                f"decision:{did} graded with conflicting tiers {sorted(tiers)} in this file"))
        else:
            violations.append(make_violation(
                "GL008", file, locations,
                f"decision:{did} graded more than once in this file"))

    return violations


# --------------------------------------------------------------------------
# Ledger view (recomputed every run -- never persisted; invariant 7)
# --------------------------------------------------------------------------


def build_ledger(decisions: list[DecisionRecord]) -> dict:
    settled = []
    guesses = []
    load_bearing_guesses = []
    guesses_missing_settle = []
    placeholders = []
    ungraded = []

    for dec in decisions:
        loc = {"file": dec.file, "location": dec.location, "decision_id": dec.decision_id}
        tag = dec.tag
        if tag is None:
            ungraded.append(loc)
            continue
        if tag.tier == "settled":
            settled.append(loc)
        elif tag.tier == "guess":
            guesses.append(loc)
            if tag.leans:
                load_bearing_guesses.append(loc)
            if not (tag.settle and tag.settle.strip()):
                guesses_missing_settle.append(loc)
        elif tag.tier == "placeholder":
            placeholders.append(loc)

    return {
        "settled": settled,
        "guesses": guesses,
        "load_bearing_guesses": load_bearing_guesses,
        "guesses_missing_settle": guesses_missing_settle,
        "placeholders": placeholders,
        "ungraded": ungraded,
    }


def ledger_summary_line(ledger: dict) -> str:
    return (
        f"{len(ledger['settled'])} settled, "
        f"{len(ledger['guesses'])} guesses "
        f"({len(ledger['load_bearing_guesses'])} load-bearing, "
        f"{len(ledger['guesses_missing_settle'])} missing settle), "
        f"{len(ledger['placeholders'])} placeholder, "
        f"{len(ledger['ungraded'])} ungraded"
    )


# --------------------------------------------------------------------------
# id-universe loading for --ids-from
# --------------------------------------------------------------------------


def load_id_universe(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {line.strip() for line in text.splitlines()
                if line.strip() and not line.strip().startswith("#")}
    return extract_plan_ids(data)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grade_lint.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="+", metavar="PATH",
                         help="Markdown or JSON plan file(s) to lint")
    parser.add_argument(
        "--mode", choices=["preflight", "execute"], default="preflight",
        help="preflight (default): an ungraded decision in a recognized block is "
             "GL001 UNGRADED_DECISION, a FAIL. execute: ungraded reads as settled "
             "and GL001 is suppressed entirely -- a DIAGNOSTIC PREVIEW of the "
             "lenient execution-time reading, NOT enforcement; nothing here is "
             "wired to checklist_engine.py, which does not parse @grade tags at all.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text",
                         help="text (default): terse batched-objections view ending "
                              "in one question. json: structured records + ledger.")
    parser.add_argument(
        "--ids-from", action="append", default=[], metavar="PATH",
        help="file supplying known gate/item ids for `leans` resolution when "
             "linting Markdown (repeatable). A JSON file is read the same way a "
             "linted plan self-sources ids (items[] + tasks{} keys); any other "
             "file is read as one id per line.",
    )
    parser.add_argument("--known-id", action="append", default=[], metavar="ID",
                         help="a single known gate/item id for leans resolution (repeatable)")
    parser.add_argument("--strict-warnings", action="store_true",
                         help="WARN-severity findings also flip the exit code")
    parser.add_argument("-q", "--quiet", action="store_true",
                         help="suppress the clean-run banner")
    return parser


def compute_exit_code(violations: list[Violation], strict_warnings: bool) -> int:
    has_fail = any(v.severity == FAIL for v in violations)
    has_warn = any(v.severity == WARN for v in violations)
    if has_fail or (strict_warnings and has_warn):
        return 1
    return 0


def violation_to_dict(v: Violation) -> dict:
    return {"code": v.code, "name": v.name, "severity": v.severity,
            "file": v.file, "location": v.location, "message": v.message}


def render_text(violations: list[Violation], ledger: dict, quiet: bool) -> None:
    if not violations:
        if not quiet:
            print(f"grade_lint: clean -- {ledger_summary_line(ledger)}")
        return
    print(f"grade_lint: {len(violations)} objection(s)")
    for v in violations:
        print(f"  [{v.severity}] {v.code} {v.name}  {v.file}:{v.location}  {v.message}")
    print(f"guess-ledger: {ledger_summary_line(ledger)}")
    print("Proceed despite the above, or fix the grades first?")


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    global_ids: set[str] = set(args.known_id)
    try:
        for raw_ids_from in args.ids_from:
            global_ids |= load_id_universe(Path(raw_ids_from))
    except OSError as exc:
        print(f"grade_lint: cannot read --ids-from {raw_ids_from}: {exc}", file=sys.stderr)
        return 2

    ids_provided_globally = bool(args.ids_from or args.known_id)

    all_decisions: list[DecisionRecord] = []
    all_violations: list[Violation] = []

    for raw_path in args.paths:
        path = Path(raw_path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"grade_lint: cannot read {raw_path}: {exc}", file=sys.stderr)
            return 2

        if path.suffix.lower() == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                print(f"grade_lint: invalid JSON in {raw_path}: {exc}", file=sys.stderr)
                return 2
            known_ids = extract_plan_ids(data) | global_ids
            ids_provided = True
            decisions, violations = scan_json(str(raw_path), data)
        else:
            known_ids = global_ids
            ids_provided = ids_provided_globally
            decisions, violations = scan_markdown(str(raw_path), text)

        any_leans_without_ids = False
        for dec in decisions:
            violations.extend(validate_decision(dec, known_ids, ids_provided, args.mode))
            if dec.tag and dec.tag.leans and not ids_provided:
                any_leans_without_ids = True
        if any_leans_without_ids:
            violations.append(make_violation(
                "GL011", str(raw_path), "-",
                "leans present but no --ids-from/--known-id supplied; "
                "GL005 skipped for this file"))

        violations.extend(cross_occurrence_violations(str(raw_path), decisions))

        all_decisions.extend(decisions)
        all_violations.extend(violations)

    exit_code = compute_exit_code(all_violations, args.strict_warnings)
    ledger = build_ledger(all_decisions)

    if args.format == "json":
        print(json.dumps({
            "mode": args.mode,
            "exit_code": exit_code,
            "violations": [violation_to_dict(v) for v in all_violations],
            "ledger": ledger,
        }, indent=2))
    else:
        render_text(all_violations, ledger, args.quiet)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
