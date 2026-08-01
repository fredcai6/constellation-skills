#!/usr/bin/env python
"""Curator MEASUREMENT pass over the skills corpus (mechanical-only, flags-never-gates).

This is the curator's measurement/flagging tool, NOT a linter that fails a build.
It performs MECHANICAL checks over each `skills/<name>/SKILL.md` (and its
`references/`) and emits a human findings table plus a `--json` machine record.

Two invariants are enforced IN CODE so prose drift cannot erode them:

  * FLAGS-NEVER-GATES (curator invariant #2): every run ALWAYS exits 0. Soft
    budgets are review heuristics, never build gates — there is deliberately no
    code path that returns non-zero. An unparseable skill becomes a findings ROW
    (check="parse", status flagged), never a crash or a nonzero exit.

  * DECIDABILITY-HONESTY (T7): the script reports only mechanically-decidable
    facts (counts, token presence/absence, shared shingles). It NEVER renders a
    semantic verdict (e.g. "this register is wrong", "this clause is a
    procedure"). Where the convention needs a human judgment, it SHORTLISTS a
    candidate (status="shortlist") for a human to adjudicate — it never judges.

No baseline/drift-vs-previous-run diff lives here (spec ruling S7 — that is a
future v2). Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# CURATOR REVIEW HEURISTICS
#
# Every constant below is a SOFT BUDGET a curator uses to decide what to LOOK
# at — never a gate. Over-budget produces a findings row for a human to weigh,
# never a failure. Seed values are calibrated against the current corpus so a
# flag means something (it bites the outliers) without flagging everything.
# --------------------------------------------------------------------------- #

# SKILL.md body size. The corpus norm is a tight one-screen skill; the long
# outliers (admiral/docent/explorer) are the ones worth a curator's eye. ~400
# words is the target a well-scoped skill sits under; 500 lines is a hard line
# flag well above every current skill (max is docent at 143), so tripping it
# signals a skill that has grown into a manual and should probably be split or
# moved to references/.
SKILL_WORD_TARGET = 400          # soft target; body words over this -> flag
SKILL_LINE_HARD_FLAG = 500       # hard line flag; body lines over this -> flag

# Description register. A skill `description:` is the trigger a router scans; it
# should read as one or two scannable sentences. The current corpus runs
# 105-397 chars / 16-63 words, so a soft ceiling of 350 chars / 50 words flags
# only the longest, chattiest descriptions — the ones a curator would tighten.
DESCRIPTION_MAX_CHARS = 350      # soft budget; description longer -> flag
DESCRIPTION_MAX_WORDS = 50       # soft budget; description wordier -> flag

# First/second-person pronoun tokens. Third-person is the description
# convention, but whether a given "you"/"we" is actually a register slip is a
# HUMAN judgment — presence here only SHORTLISTS the description for review; it
# never asserts the description is wrong (T7 mechanical-only).
PERSON_PRONOUNS = ("i", "you", "your", "we", "our", "us")

# When-to-use marker. A description should carry a triggering-condition clause.
# These lowercase markers detect its PRESENCE mechanically; absence is flagged
# as "no when-to-use marker" (mechanical absence, not a quality verdict).
WHEN_TO_USE_MARKERS = ("use when", "use to", "use for", "use during")

# Exclusion-clause markers. A description may carry a "don't confuse me with X"
# clause. These detect its PRESENCE mechanically. Absence is only FLAGGED for
# the known confusable-pair skills below; for every other skill absence is fine.
EXCLUSION_MARKERS = ("not ", "do not", "don't", "instead of", "rather than", "never ")
# ...plus the "for <other-thing> use <X>" redirect pattern:
EXCLUSION_REDIRECT_RE = re.compile(r"\bfor\b.*?\buse\b", re.IGNORECASE)

# Confusable pairs (epic-101 cross-cutting rule 1): skills a router most easily
# mixes up. ONLY these skills are flagged when their description lacks an
# exclusion clause — the disambiguation matters most where confusion is likely.
# Encoded as pairs (documents WHY each skill is here); membership is the union.
CONFUSABLE_PAIRS = (
    ("scout", "cartographer"),
    ("explorer", "interrogator"),
    ("admiral", "commander"),
    ("curator", "scout"),
    ("curator", "write-a-skill"),
    ("commander-delegated", "admiral"),
)
CONFUSABLE_SKILLS = frozenset(s for pair in CONFUSABLE_PAIRS for s in pair)

# Invoker tag. The `invoker:` frontmatter key declares who invokes a skill.
# On the current corpus only curator will carry one — every other skill flags
# here, which is EXPECTED: the flag is how the convention gets seeded.
VALID_INVOKERS = ("human", "agent", "both")

# Reference TOC. A references/*.md long enough to need navigation should carry
# a table-of-contents heading. 100 lines is the soft threshold above which a
# curator expects a "## Contents" anchor; shorter files scroll fine without one.
REFERENCE_TOC_LINE_THRESHOLD = 100
TOC_MARKER_RE = re.compile(r"^\s*#{1,6}\s+(table of contents|contents)\b", re.IGNORECASE | re.MULTILINE)

# Duplication-signature clustering (the drift-elimination detector). We shingle
# each SKILL.md body into k-word windows and report shingles shared across
# distinct skills. k=8 is long enough that a match is a genuinely shared
# doctrine sentence (not an incidental short phrase like "through the engine")
# yet short enough to still match after small edits around it. A cluster needs
# the same shingle in >= 2 DISTINCT skills to report.
SHINGLE_SIZE = 8                 # words per shingle; drift detector window
MIN_CLUSTER_SKILLS = 2           # a shingle must span >= this many skills to cluster

# Status vocabulary (mechanical outcomes only, never a quality verdict).
STATUS_FLAGGED = "flagged"       # over a soft budget / a marker is absent
STATUS_SHORTLIST = "shortlist"   # a candidate for a HUMAN to judge (never judged here)
STATUS_INFO = "info"             # neutral observation
STATUS_OK = "ok"                 # a check passed cleanly


class CorpusParseError(Exception):
    """A skill's SKILL.md could not be parsed. Becomes a findings row, never a crash."""


@dataclass
class Finding:
    """One mechanical observation. `extra` carries structured data (e.g. the
    skills + example shingle of a duplication cluster) for machine consumers."""

    skill: str
    check: str
    status: str
    detail: str
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        row = {"skill": self.skill, "check": self.check, "status": self.status, "detail": self.detail}
        row.update(self.extra)
        return row


def _utf8_stdio() -> None:
    """Match the sibling scripts: don't force every caller to set PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            pass


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse a leading YAML frontmatter block into a flat dict of top-level
    scalar `key: value` pairs, returning (meta, body). Raises CorpusParseError
    on missing or unterminated frontmatter — the caller turns that into a row.

    Deliberately minimal (stdlib-only, no yaml dep): the corpus frontmatter is
    flat single-line scalars. Block scalars / nested maps are not expected; a
    key we cannot parse is simply skipped, not fatally malformed.
    """
    if not text.startswith("---"):
        raise CorpusParseError("no YAML frontmatter (missing opening '---')")
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise CorpusParseError("unterminated YAML frontmatter (no closing '---')")
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"([A-Za-z0-9_-]+):\s?(.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
    body = "\n".join(lines[end + 1:])
    return meta, body


def _words(text: str) -> list[str]:
    """Lowercased alphanumeric word tokens; whitespace and punctuation normalized."""
    return re.findall(r"[a-z0-9]+", text.lower())


def check_size(skill: str, body: str) -> list[Finding]:
    """Body line/word counts vs the soft size budgets."""
    findings: list[Finding] = []
    n_lines = len(body.splitlines())
    n_words = len(body.split())
    if n_words > SKILL_WORD_TARGET:
        findings.append(Finding(skill, "size", STATUS_FLAGGED,
                                f"body {n_words} words > target {SKILL_WORD_TARGET}",
                                {"words": n_words, "lines": n_lines}))
    if n_lines > SKILL_LINE_HARD_FLAG:
        findings.append(Finding(skill, "size", STATUS_FLAGGED,
                                f"body {n_lines} lines > hard flag {SKILL_LINE_HARD_FLAG}",
                                {"words": n_words, "lines": n_lines}))
    if not findings:
        findings.append(Finding(skill, "size", STATUS_OK,
                                f"body {n_lines} lines / {n_words} words within budget",
                                {"words": n_words, "lines": n_lines}))
    return findings


def _person_tokens(desc: str) -> list[str]:
    tokens = set(_words(desc))
    return [p for p in PERSON_PRONOUNS if p in tokens]


def _exclusion_present(desc: str) -> bool:
    low = desc.lower()
    if any(marker in low for marker in EXCLUSION_MARKERS):
        return True
    return bool(EXCLUSION_REDIRECT_RE.search(desc))


def check_description(skill: str, meta: dict[str, str]) -> list[Finding]:
    """Mechanical description lint: length, person-pronoun shortlist, when-to-use
    marker presence, and (confusable-pairs only) exclusion-clause presence."""
    findings: list[Finding] = []
    desc = meta.get("description")
    if not desc:
        findings.append(Finding(skill, "description", STATUS_FLAGGED, "no description field in frontmatter"))
        return findings

    n_chars = len(desc)
    n_words = len(desc.split())
    if n_chars > DESCRIPTION_MAX_CHARS or n_words > DESCRIPTION_MAX_WORDS:
        findings.append(Finding(skill, "description-length", STATUS_FLAGGED,
                                f"{n_chars} chars / {n_words} words > budget "
                                f"{DESCRIPTION_MAX_CHARS} chars / {DESCRIPTION_MAX_WORDS} words",
                                {"chars": n_chars, "words": n_words}))

    persons = _person_tokens(desc)
    if persons:
        # SHORTLIST only — presence of a pronoun token, NOT a verdict that the
        # register is wrong. A human decides (T7).
        findings.append(Finding(skill, "description-person", STATUS_SHORTLIST,
                                f"first/second-person token(s) present: {', '.join(persons)} "
                                f"(third-person is the convention; human judges)",
                                {"pronouns": persons}))

    if not any(marker in desc.lower() for marker in WHEN_TO_USE_MARKERS):
        findings.append(Finding(skill, "description-when-to-use", STATUS_FLAGGED,
                                "no when-to-use marker (e.g. 'Use when ...')"))

    if skill in CONFUSABLE_SKILLS:
        if _exclusion_present(desc):
            findings.append(Finding(skill, "description-exclusion", STATUS_INFO,
                                    "exclusion clause present (confusable-pair skill)"))
        else:
            findings.append(Finding(skill, "description-exclusion", STATUS_FLAGGED,
                                    "confusable-pair skill has no exclusion clause "
                                    "(e.g. 'not', 'instead of', 'for X use Y')"))
    return findings


def check_invoker(skill: str, meta: dict[str, str]) -> list[Finding]:
    """Presence + validity of the `invoker:` frontmatter tag."""
    value = meta.get("invoker")
    if value is None:
        return [Finding(skill, "invoker", STATUS_FLAGGED, "missing invoker tag (expected one of human/agent/both)")]
    if value not in VALID_INVOKERS:
        return [Finding(skill, "invoker", STATUS_FLAGGED,
                        f"invoker tag value {value!r} not in {'/'.join(VALID_INVOKERS)}",
                        {"invoker": value})]
    return [Finding(skill, "invoker", STATUS_OK, f"invoker={value}", {"invoker": value})]


def check_references(skill: str, skill_dir: Path) -> list[Finding]:
    """Each references/*.md longer than the threshold should carry a TOC heading."""
    findings: list[Finding] = []
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return findings
    for ref in sorted(refs_dir.glob("*.md")):
        try:
            text = ref.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(Finding(skill, "reference-toc", STATUS_FLAGGED,
                                    f"could not read {ref.name}: {exc}"))
            continue
        n_lines = len(text.splitlines())
        if n_lines > REFERENCE_TOC_LINE_THRESHOLD and not TOC_MARKER_RE.search(text):
            findings.append(Finding(skill, "reference-toc", STATUS_FLAGGED,
                                    f"{ref.name} is {n_lines} lines (> {REFERENCE_TOC_LINE_THRESHOLD}) "
                                    "without a '## Contents' TOC",
                                    {"reference": ref.name, "lines": n_lines}))
    return findings


def check_duplication(bodies: dict[str, str]) -> list[Finding]:
    """Corpus-level: report k-word shingles shared across >= MIN_CLUSTER_SKILLS
    distinct skills. Grouped by the exact set of sharing skills so the human
    table shows one row per shared-signature pattern, not one per shingle."""
    shingle_to_skills: dict[str, set[str]] = {}
    for skill, body in bodies.items():
        tokens = _words(body)
        seen_here: set[str] = set()
        for i in range(len(tokens) - SHINGLE_SIZE + 1):
            shingle = " ".join(tokens[i:i + SHINGLE_SIZE])
            if shingle in seen_here:
                continue
            seen_here.add(shingle)
            shingle_to_skills.setdefault(shingle, set()).add(skill)

    # Group shared shingles by the exact frozenset of skills that share them.
    clusters: dict[frozenset[str], list[str]] = {}
    for shingle, skills in shingle_to_skills.items():
        if len(skills) >= MIN_CLUSTER_SKILLS:
            clusters.setdefault(frozenset(skills), []).append(shingle)

    findings: list[Finding] = []
    for skills, shingles in sorted(clusters.items(), key=lambda kv: (-len(kv[1]), sorted(kv[0]))):
        skill_list = sorted(skills)
        example = sorted(shingles, key=len, reverse=True)[0]
        findings.append(Finding(
            ",".join(skill_list), "duplication", STATUS_FLAGGED,
            f"{len(shingles)} shared {SHINGLE_SIZE}-word shingle(s); e.g. \"{example}\"",
            {"skills": skill_list, "shingle_count": len(shingles), "example": example},
        ))
    return findings


def _skill_dirs(root: Path) -> list[Path]:
    """Immediate subdirectories that are candidate skills. Dirs whose name starts
    with '_' or '.' (e.g. `_shared`) are infrastructure, not skills, and skipped."""
    if not root.is_dir():
        return []
    return sorted(d for d in root.iterdir()
                  if d.is_dir() and not d.name.startswith(("_", ".")))


def curate(root: Path) -> list[Finding]:
    """Run every mechanical check over `root` (a skills/ directory) and return
    all findings. Never raises for a bad skill — an unparseable skill becomes a
    parse findings row and is excluded from the duplication corpus."""
    findings: list[Finding] = []
    bodies: dict[str, str] = {}

    for skill_dir in _skill_dirs(root):
        skill = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        try:
            if not skill_md.is_file():
                raise CorpusParseError("no SKILL.md")
            text = skill_md.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)
        except (CorpusParseError, OSError) as exc:
            findings.append(Finding(skill, "parse", STATUS_FLAGGED, str(exc)))
            continue

        bodies[skill] = body
        findings.extend(check_size(skill, body))
        findings.extend(check_description(skill, meta))
        findings.extend(check_invoker(skill, meta))
        findings.extend(check_references(skill, skill_dir))

    findings.extend(check_duplication(bodies))
    return findings


def render_table(findings: list[Finding]) -> str:
    """A readable fixed-width findings table: skill | check | status | detail."""
    header = ("skill", "check", "status", "detail")
    rows = [(f.skill, f.check, f.status, f.detail)
            for f in sorted(findings, key=lambda f: (f.skill, f.check, f.status))]
    all_rows = [header, *rows]
    widths = [max(len(r[i]) for r in all_rows) for i in range(3)]  # detail not padded (last col)
    lines = []
    fmt = f"{{:<{widths[0]}}}  {{:<{widths[1]}}}  {{:<{widths[2]}}}  {{}}"
    lines.append(fmt.format(*header))
    lines.append(fmt.format("-" * widths[0], "-" * widths[1], "-" * widths[2], "-" * 6))
    for r in rows:
        lines.append(fmt.format(*r))
    flagged = sum(1 for f in findings if f.status == STATUS_FLAGGED)
    shortlisted = sum(1 for f in findings if f.status == STATUS_SHORTLIST)
    lines.append("")
    lines.append(f"{len(findings)} finding(s): {flagged} flagged, {shortlisted} shortlisted "
                 "(measurement only — this tool never gates; exit 0 always)")
    return "\n".join(lines)


def build_record(root: Path, findings: list[Finding]) -> dict:
    """The --json machine record: the run's root, the heuristic constants that
    produced it, and the findings as structured rows."""
    return {
        "root": str(root),
        "heuristics": {
            "SKILL_WORD_TARGET": SKILL_WORD_TARGET,
            "SKILL_LINE_HARD_FLAG": SKILL_LINE_HARD_FLAG,
            "DESCRIPTION_MAX_CHARS": DESCRIPTION_MAX_CHARS,
            "DESCRIPTION_MAX_WORDS": DESCRIPTION_MAX_WORDS,
            "REFERENCE_TOC_LINE_THRESHOLD": REFERENCE_TOC_LINE_THRESHOLD,
            "SHINGLE_SIZE": SHINGLE_SIZE,
            "MIN_CLUSTER_SKILLS": MIN_CLUSTER_SKILLS,
            "CONFUSABLE_SKILLS": sorted(CONFUSABLE_SKILLS),
        },
        "findings": [f.to_dict() for f in findings],
    }


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", default=None,
                        help="skills/ directory to measure (default: skills)")
    parser.add_argument("--root", dest="root_opt", default=None,
                        help="skills/ directory to measure (overrides the positional)")
    parser.add_argument("--json", action="store_true",
                        help="emit the findings as a JSON record instead of the table")
    args = parser.parse_args(argv)

    root = Path(args.root_opt or args.root or "skills")
    findings = curate(root)

    if args.json:
        print(json.dumps(build_record(root, findings), indent=2))
    else:
        if not root.is_dir():
            print(f"note: root {root} is not a directory — no skills measured")
        print(render_table(findings))

    # FLAGS-NEVER-GATES: always 0. There is intentionally no non-zero path.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
