"""Regrowth guard for issue #559 -- the door is the interface, not a second path.

The human ruling this guard enforces, verbatim:

    "the agents should not know about the CLI. period."

That text has been deleted from the instruction corpus TWICE and has grown back
TWICE. The deliverable of this lane is therefore not the deletion -- it is the
guard that makes the third deletion stick. This file is that guard, and it is
authored BEFORE the sweep on purpose: a guard written against an already-clean
corpus can only be red-proofed against a scratch string its own author chose,
which any pattern passes. Written now, its RED is produced by the real corpus.

WHAT THIS PINS. Over every agent-facing instruction text in the corpus, the
ABSENCE of three things:

  1. The `<engine>` placeholder token -- a spine template's stand-in for an
     engine command line. `init_work_area.py` deliberately never resolves it,
     so every one that reaches an agent reaches it unresolved.
  2. A `CLI fallback` clause, case-insensitive, in ANY punctuation form.
  3. A command-shaped `checklist_engine.py` invocation -- the script reached by
     a path or an interpreter, or followed by a flag or an engine verb.

Pattern 3 exists because 1 and 2 are defeated by rewording. Once the phrase
"CLI fallback" is gone, a rename-around reads "run the engine script directly"
and both of the other patterns stay green. What a rename-around cannot do is
omit the runnable command, because the command is the point of the sentence.

THIS IS A GENERALIZATION, NOT A NEW INVENTION. `test_mcp_adoption.py`'s
`TestTier2SpineAlreadyBoundForDispatchedCrews` already asserts this same
absence, for two files, and already pins the ruling above verbatim. This file
is that precedent widened from 2 files to the whole corpus.

THE CORPUS IS WALKED, NEVER LISTED, AND THE EXCEPTION LIST IS EMPTY. The walk
is `test_mcp_adoption.INSTRUCTION_FILES` -- imported, not re-derived, so the
repo has exactly ONE machine-readable definition of "agent-facing instruction
text" and the two cannot drift apart in silence -- extended here to
`specs/**/*.toml`, which is where door doctrine lands and which the adoption
walk does not reach.

There is NO per-file exclusion, of any length. A sibling guard's exception list
reached 11 entries across five runs; that decay is the named failure mode this
file exists to avoid. Everything excluded is excluded by a rule the walk itself
applies, and measured against this tree that rule is already sufficient: it puts
all 10 target files IN, and it puts both sites that must survive OUT --
`docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` (a
historical plan record) and `scripts/init_work_area.py:24` (a comment
documenting the never-resolved-placeholder convention itself). Neither is named
here, and neither needs to be: they are not under `skills/` and not a
`specs/*.toml`, because of what they ARE. Same for `episodes/**`,
`tests/fixtures/` and `tests/data/`, every one of them a record of what was
said rather than text an agent is handed today.

WHAT THIS DOES NOT ENFORCE, STATED RATHER THAN GLOSSED:

  * The bare word "CLI". Corpus-wide that is over-broad -- `--backend cli` is a
    real flag and a real dispatch mode -- so it is left alone here even though
    the two-file precedent does assert it. The scope where it is safe is the
    scope that precedent already covers.
  * A bare prose mention of `checklist_engine.py` that names the engine as a
    component rather than telling anyone to run it ("an epic that rewrites
    `checklist_engine.py`", a scripts manifest). Measured on this tree, that
    distinction leaves 6 such mentions alone while catching all 10 command
    forms; see `TestTheInvocationPredicateItself`, which pins both directions in
    the assertion path so a later edit to the pattern cannot quietly move them.
  * Prose that FORBIDS the violation while quoting it. A guard reading a
    quotation cannot tell a prohibition from an instruction, and this file
    accepts that false alarm rather than growing a polarity predicate: the
    corpus this guards should not need to quote the clause at all, and a
    deliberate quotation is a one-line judgement for a human, not a rule to
    encode.

EVERY FAILURE MESSAGE QUOTES THE RULING VERBATIM rather than citing a location.
This lane may not write `docs/agents/*` and files no issue, so any pointer this
file could offer would dangle. Carrying the ruling inline means deleting the
guard also deletes the reason, which is the property a dangling pointer loses.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The repo's own definition of "agent-facing instruction text" lives in the
# adoption suite. Import it rather than re-deriving it: a re-derived copy is two
# definitions that agree today and drift silently tomorrow. The explicit
# sys.path insert is this directory's house idiom for a cross-test import (see
# test_mcp_imperative_equivalence.py) rather than relying on incidental ordering.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_mcp_adoption import INSTRUCTION_FILES, _instruction_texts  # noqa: E402

#: The ruling, verbatim, carried by every failure message in this file.
HUMAN_RULING = "the agents should not know about the CLI. period."

#: Instruction text the adoption walk does not reach. `specs/*.toml` is where
#: door doctrine is authored, so a fallback clause could otherwise be written
#: there with this guard green. A suffix rule, not a file list.
SPEC_SUFFIXES = (".toml",)


def _walk_spec_files() -> list[str]:
    specs = ROOT / "specs"
    if not specs.is_dir():
        return []
    return sorted(
        p.relative_to(ROOT).as_posix()
        for p in specs.rglob("*")
        if p.is_file() and p.suffix in SPEC_SUFFIXES
    )


SPEC_FILES = _walk_spec_files()
GUARDED_FILES = INSTRUCTION_FILES + SPEC_FILES


def _guard_texts() -> list[tuple[str, str, str, bool]]:
    """(file, where, text, is_whole_file) for everything the guard reads.

    Markdown and TOML are one whole-file chunk each, so a match's line number is
    meaningful and is reported. JSON is decomposed into its string leaves by the
    adoption suite's own extractor, each addressed by its JSON path, which
    localizes a match better than a line number would.
    """
    out: list[tuple[str, str, str, bool]] = []
    for path in INSTRUCTION_FILES:
        whole_file = not path.endswith(".json")
        for where, text in _instruction_texts(path):
            out.append((path, where, text, whole_file))
    for path in SPEC_FILES:
        out.append((path, path, (ROOT / path).read_text(encoding="utf-8"), True))
    return out


GUARD_TEXTS = _guard_texts()

# --------------------------------------------------------------------------- #
# The three patterns.
# --------------------------------------------------------------------------- #

#: A spine template's placeholder for an engine command line.
ENGINE_PLACEHOLDER_RE = re.compile(r"<engine>")

#: Measured on this tree the clause has THREE surface forms -- `CLI fallback:`
#: x10, `CLI fallback,` x4, `CLI fallback ` x1 -- so a colon-only pattern misses
#: a third of them. The separator is loosened the same way, so a re-spelling as
#: `CLI-fallback` is not a way out either.
CLI_FALLBACK_RE = re.compile(r"CLI[\s-]+fallback", re.IGNORECASE)

#: Engine verbs, as a command line writes them. Used only as the lookahead that
#: makes a trailing argument recognizable.
_ENGINE_VERBS = (
    "current|start|advance|record|consolidate|claim|release|heartbeat|"
    "attest|attach|waive|skip|block|reopen|append|amend|flag-candidate"
)

#: A COMMAND-SHAPED reference to the engine script: an interpreter runs it, or a
#: path leads to it, or an argument follows it. Any one of the three is a
#: sentence telling an agent how to drive a checklist from a shell, which is the
#: behaviour this guard is about -- not the string `checklist_engine.py`, which
#: is also how the corpus legitimately names the engine as a component.
#:
#: The trailing-argument arm requires a LONG FLAG (`--file`), never a bare `--`.
#: Written the loose way it red-lighted `rewrites checklist_engine.py -- the very
#: engine driving it`, where the dashes are an ASCII em-dash and the sentence is
#: about editing the file, not running it. That false alarm was caught by
#: `TestTheInvocationPredicateItself` before this guard was ever offered as
#: evidence, which is what that class is for.
ENGINE_INVOCATION_RE = re.compile(
    r"""(?:(?:python3?|py)\s+(?:[^\s`'"]+\s+)?|[^\s`'"]*/)checklist_engine\.py"""
    r"""|checklist_engine\.py(?=[`'"\s]*(?:--[A-Za-z]|(?:""" + _ENGINE_VERBS + r""")\b))"""
)


def _sites(pattern: re.Pattern[str]) -> list[str]:
    """Every match of `pattern`, addressed and excerpted. One line per match."""
    found: list[str] = []
    for path, where, text, whole_file in GUARD_TEXTS:
        for match in pattern.finditer(text):
            if whole_file:
                address = f"{where}:{text.count(chr(10), 0, match.start()) + 1}"
            else:
                address = where
            excerpt = text[max(0, match.start() - 40):match.end() + 40]
            excerpt = " ".join(excerpt.split())
            found.append(f"    {address}\n        ...{excerpt}...")
    return found


def _census() -> str:
    """What the walk actually covered. Every failure message carries it, so a
    finding can never be read without the size of the corpus it came from."""
    return (
        f"scanned {len(GUARD_TEXTS)} texts across {len(GUARDED_FILES)} files "
        f"({len(INSTRUCTION_FILES)} under skills/, {len(SPEC_FILES)} under specs/)"
    )


def _report(what: str, sites: list[str]) -> str:
    return (
        f"{len(sites)} {what} survive in agent-facing instruction text "
        f"({_census()}).\n"
        f"The ruling, verbatim: \"{HUMAN_RULING}\"\n"
        f"Sites:\n" + "\n".join(sites)
    )


class TestTheWalkIsNotVacuous:
    """A guard that loops must assert what it looped over. A narrowed walk --
    a moved directory, a renamed suffix, an import that silently returned an
    empty list -- reports a clean corpus without ever reading an interesting
    file, and reads exactly like a passing guard. These floors are what make the
    absence assertions below mean something."""

    def test_the_walk_reaches_the_skills_corpus(self):
        assert len(INSTRUCTION_FILES) >= 60, (
            f"the instruction walk found only {len(INSTRUCTION_FILES)} files under skills/ "
            f"-- it covered 101 when this guard was written, so a count this low means the "
            f"walk narrowed and every absence assertion below is passing vacuously"
        )

    def test_the_walk_reaches_the_spec_corpus(self):
        assert len(SPEC_FILES) >= 1, (
            f"the walk found no {'/'.join(SPEC_SUFFIXES)} file under specs/ -- door doctrine "
            f"is authored there, so with this extension empty a fallback clause could be "
            f"written into specs/ with this guard green"
        )

    def test_the_walk_yields_texts_not_just_paths(self):
        assert len(GUARD_TEXTS) >= 600, (
            f"the walk yielded only {len(GUARD_TEXTS)} texts from "
            f"{len(GUARDED_FILES)} files -- it yielded 1007 when this guard was written, "
            f"so the extractor is returning empty or collapsed content and the patterns "
            f"below are searching nothing"
        )


class TestTheInvocationPredicateItself:
    """`ENGINE_INVOCATION_RE` is the only pattern here that judges rather than
    matches: it must separate "run this from a shell" from "this file is the
    engine". Both directions are pinned in the assertion path, so a later edit
    to the pattern cannot quietly widen it into a false-alarm generator or
    narrow it into blindness.

    Measured on the corpus when this guard was written: 10 command forms caught,
    6 prose mentions left alone. The strings below are the SHAPES of those two
    populations, written out so the discrimination is testable without a corpus;
    the corpus census itself is in the failure messages above."""

    COMMAND_SHAPED = [
        "the CLI fallback: through `scripts/checklist_engine.py`.",
        "`python <skill-dir>/scripts/checklist_engine.py --file <checklist.json> <verb>`",
        "run checklist_engine.py advance g1 when the gate closes",
        "py /home/tommy/.claude/skills/constellation-workbench/scripts/checklist_engine.py",
        "./scripts/checklist_engine.py current",
        "checklist_engine.py --session-id <id> release",
    ]

    PROSE_ONLY = [
        "the engine rail string table (`checklist_engine.py`, #140)",
        "an epic that rewrites `checklist_engine.py` -- the very engine driving it",
        "Scripts: `checklist_engine.py`, `init_work_area.py`, `run_crew.py`",
        "nothing enforces the execution-time half in code -- `checklist_engine.py` does not",
    ]

    def test_catches_every_command_shape(self):
        missed = [s for s in self.COMMAND_SHAPED if not ENGINE_INVOCATION_RE.search(s)]
        assert not missed, f"invocation pattern missed a command shape: {missed}"

    def test_leaves_a_bare_component_mention_alone(self):
        flagged = [s for s in self.PROSE_ONLY if ENGINE_INVOCATION_RE.search(s)]
        assert not flagged, (
            f"invocation pattern red-lighted prose that names the engine as a component "
            f"rather than telling an agent to run it: {flagged}"
        )

    def test_the_clause_pattern_reads_every_measured_surface_form(self):
        forms = ["CLI fallback:", "CLI fallback,", "CLI fallback ", "CLI-fallback:", "cli fallback:"]
        missed = [f for f in forms if not CLI_FALLBACK_RE.search(f)]
        assert not missed, (
            f"clause pattern is punctuation-sensitive and misses {missed} -- the three "
            f"forms measured in this corpus were 'CLI fallback:' x10, 'CLI fallback,' x4 "
            f"and 'CLI fallback ' x1, so a pattern blind to one of them is blind to a "
            f"third of its targets"
        )


class TestNoSecondPathReachesAnAgent:
    """The guard proper. Each of these asserts the ABSENCE of the text itself --
    never the presence of a sentence describing the rule, which is the failure
    mode this whole epic is about: a corpus can carry a perfect statement of the
    doctrine in one paragraph and violate it in the next."""

    def test_no_engine_placeholder_token_reaches_an_agent(self):
        sites = _sites(ENGINE_PLACEHOLDER_RE)
        assert not sites, _report(
            "`<engine>` placeholder tokens -- a stand-in for an engine command line that "
            "init_work_area.py deliberately never resolves, so each one reaches an agent "
            "unresolved --",
            sites,
        )

    def test_no_cli_fallback_clause_reaches_an_agent(self):
        sites = _sites(CLI_FALLBACK_RE)
        assert not sites, _report(
            "`CLI fallback` clauses -- each one hands an agent a second path to the "
            "checklist engine beside the MCP door --",
            sites,
        )

    def test_no_engine_invocation_reaches_an_agent(self):
        sites = _sites(ENGINE_INVOCATION_RE)
        assert not sites, _report(
            "command-shaped `checklist_engine.py` invocations -- the rename-around that "
            "survives deleting the phrase, because the runnable command is what the "
            "sentence is for --",
            sites,
        )
