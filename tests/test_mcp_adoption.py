"""Adoption gate for the MCP door (issue #542 criterion 1, epic-418-followon g4a).

The door (`scripts/mcp_spine_server.py`, 7 tools over 13 of the engine's 18 verbs) was
built and merged completely unused: at the wave boundary, zero files under `skills/`
mentioned it. This test pins the pre-authored Tier 1-5 invariant chain from the g4a-implement
handoff -- the frozen list of files/fields that must name a door tool as the path an agent
takes.

**THE CLI HALF IS INVERTED, AND THIS IS THE GENERALIZATION OF A PRECEDENT ALREADY IN THIS
FILE.** Every assertion here used to be TWO-SIDED: a door tool is named AND the CLI marker
for that same file/field is still present, with failure messages reading "the CLI door must
stay, never be removed or discouraged". Issue #559 ended that. The human ruling, verbatim:

    "the agents should not know about the CLI. period."

`TestTier2SpineAlreadyBoundForDispatchedCrews` below already asserted exactly that, for two
files, and already carried that ruling. The change here is that precedent WIDENED: the
CLI-presence half of Tier1, Tier2 and Tier4 is now an ABSENCE assertion, so the same rule
covers every file this suite pins rather than two of them.

Read this as continuity, not a reversal. The epic removes the CLI as an AGENT-FACING PATH,
not as a tool -- `scripts/checklist_engine.py` still exists, still registers all 18 verbs,
and is still what an operator or a debugging human runs. What no longer reaches an agent is
the instruction to run it. `TestCLIStaysAvailableNotDeprecated` keeps that distinction
explicit, and `tests/test_cli_retirement_guard.py` is the corpus-wide walk that enforces the
absence everywhere, including files this suite never names.

The two-sidedness that remains is the DOOR half: a door tool must be named affirmatively, in
a real paragraph or field, and none of those assertions was weakened. A test that only
checked "no CLI is named" would pass a file that says nothing at all about how to drive the
engine, which is the failure the protected intent calls "leaving an agent stranded".

Tier1 assertions read the JSON field itself (by field path), never the file's raw text --
a file-level `"mcp__spine__" in text` assertion would pass an edit that added one sentence
to a header while every literal engine command line still said `checklist_engine.py`.

Two rules this file learned the hard way, both of which apply to any assertion added
to it later:

1. **The corpus is WALKED, never listed.** `INSTRUCTION_FILES` comes from
   `rglob` over `skills/`, so a new instruction file is covered the day it lands.
   The 13-file literal it replaced left 87 files uncovered -- including both survey
   checklists and `skills/admiral/SKILL.md`, which drives the engine directly -- and
   each of them accepted a planted violation with this file fully green. If a file
   must be excluded, exclude it by a rule the walk applies, never by leaving a name
   out of a literal.

2. **No assertion may be satisfied by the negation of what it pins.** Word presence
   cannot tell a proposition from its opposite, because the two are written with the
   same words: "Nothing here removes or discourages the CLI" and "The CLI is removed"
   share every marker a substring check could look for.

   The answer to that used to be POLARITY predicates (`_retires_the_cli`,
   `_keeps_the_cli`) that read a retirement word and cancelled it on a denial standing
   in front. **They are deleted, and what that cost is written down at
   `TestCLIStaysAvailableNotDeprecated` rather than glossed.** The short version: at
   the DRIFT bar this file adopts they were roughly right, and they were deleted anyway
   because their errors are not symmetric across authors.

   **Rule 2 is why the #559 inversion is CHEAP rather than a new polarity problem.**
   Every CLI assertion this file carried was a presence check that had to reason about
   what the surrounding sentence MEANT. Their inverses do not: ABSENCE IS THE FACT.
   There is no polarity to out-write, because the rule is "the text is not here", not
   "the text is here and means the right thing" -- which is the same argument
   `TestTier2SpineAlreadyBoundForDispatchedCrews` already made for its two files.

   `_asserts_the_default` and `_named_affirmatively` remain: both look for a
   prohibition immediately governing a named token, which is a much narrower and much
   more reliable question than "what is the polarity of this sentence about the CLI".

Audit of every assertion here against rule 2. Presence is enough ONLY where presence IS
the fact, or where the thing pinned is an exact string:

  * PINS A PROPOSITION, PROHIBITION-CHECKED -- `test_field_names_door_tool_as_default`,
    `TestTier1CommanderCoreAttachLine::test_paragraph_names_door_tool`,
    `_door_path_paragraph` (via `_named_affirmatively`),
    `test_names_door_tools_as_default`.
  * PINS A ROUTING SENTENCE (a shape the negation cannot write, because the negation
    routes the other way) -- `test_the_cli_only_rule_itself_is_present`.
  * ABSENCE IS THE FACT (the #559 half: the text is there or it is not, and no wording
    satisfies a check for its absence) -- `test_field_no_longer_carries_a_cli_command_line`,
    `TestTier1CommanderCoreAttachLine::test_paragraph_no_longer_carries_a_cli_command_line`,
    `TestTier2SkillBodyDefaultPath`'s two, `TestTier4AuthoringTemplate`'s two,
    `TestTier2SpineAlreadyBoundForDispatchedCrews::test_file_never_names_the_cli_at_all`.
  * PRESENCE IS THE FACT -- `test_spine_template_still_valid_json` (parses or does not),
    `test_verb_still_documented` (the verb name is in the section or it is not),
    `TestTier5DoNotTouch`'s two (a door tool name appears or it does not),
    `test_the_walk_finds_the_whole_corpus`.
  * A NEGATIVE ALREADY -- `test_no_instruction_pairs_a_cli_only_verb_with_a_door_tool`
    and `test_verb_never_routed_through_a_door_tool` fail ON the violating text, so
    they have no negation to be satisfied by. They assert a STRUCTURAL fact (this unit
    names a tool and a verb that has no such tool) and make no polarity judgement at
    all. Their risk is the opposite one (a false alarm on a correct statement of the
    rule), which `TestTheViolationPredicateItself` measures in three directions:
    caught, left alone, and the one false alarm accepted on the record.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# The 9 door tools (scripts/mcp_spine_server.py TOOLS list). A door-tool mention is any of
# these bare names, or the fully-qualified `mcp__spine__<name>` form used to actually call one.
#
# Hand-typed here on purpose, not imported at module scope -- because importing
# `mcp_spine_server` is not side-effect-free. At module scope the door binds `SPINE` and
# `SESSION` from whatever the AMBIENT environment happens to hold, and it does
# `sys.path.insert(0, ENGINE.parent)` in the importing process. Either at COLLECTION time
# would tie this file's collection to the collecting shell's environment, before any test
# could supply a scratch one. (An unbound door has been a first-class state since issue
# #603: with neither variable named, the module-scope binding is simply `SPINE = None`.)
# Tied instead by
# `TestDoorSurfaceTiesToTheEngineRegistry::test_door_tool_names_tie_to_mcp_spine_servers_own_registry`,
# which imports it inside a test with a scratch env -- the same shape
# `tests/test_crew_launcher.py`'s `CrewGrantTiesToDoorTests` already uses for
# `CREW_ALLOWED_TOOLS`, so a tool the door adds or drops goes red here instead of leaving a
# stale count.
DOOR_TOOL_NAMES = (
    "spine_status",
    "spine_lease",
    "spine_start",
    "spine_advance",
    "spine_evidence",
    "spine_halt",
    "spine_survey_result",
    "spine_capture",
    "spine_amend",
)
DOOR_TOOL_RE = re.compile(r"\b(?:mcp__spine__)?(" + "|".join(DOOR_TOOL_NAMES) + r")\b")

# No verb is CLI-only anymore. Issue #559, N1 overturned the "roughly seven tools, five
# verbs left CLI-only" budget: the door grew to 9 tools and now covers all 18 of the
# engine's verbs (mcp_spine_server.py's own module docstring: "18 of 18 verbs covered.
# There is no CLI-fallback table below this one"). Kept as an empty tuple rather than
# deleted, so `_cli_only_verb_violations` and the corpus-wide guard built on it
# (`TestCLIOnlyVerbsAcrossEveryInstructionFile`) stay meaningful -- and immediately
# protective again -- the moment a future verb ships without a door tool. Tied to the
# engine's own argparse registry and the door's own dispatch code (never hand-typed
# alongside a hand-typed gap) by
# `TestDoorSurfaceTiesToTheEngineRegistry::test_cli_only_verbs_tie_to_the_gap_between_engine_and_door`.
CLI_ONLY_VERBS = ()

#: A representative CLI-only-verb set used ONLY to exercise `_cli_only_verb_violations`'s
#: own mechanism (unit width, abbreviation handling, verb-name matching) in
#: `TestTheViolationPredicateItself`. Deliberately decoupled from the real, now-empty
#: `CLI_ONLY_VERBS`: the predicate's self-test must stay meaningful regardless of how many
#: verbs are genuinely CLI-only today, while the corpus guard below keeps running against
#: the real list.
_PREDICATE_SELFTEST_VERBS = ("skip", "reopen", "append", "amend", "flag-candidate")

# The marker the spine templates USED to carry for "the engine, invoked as a command line".
# `init_work_area.py` deliberately never resolved it, so every one that survived
# instantiation reached an agent unresolved. Issue #559 swept it out of the corpus, and its
# ABSENCE from an imperative field is now what is pinned -- the inverse of what this constant
# was introduced for. It is kept, rather than inlined, because the assertions below are more
# readable naming the thing they forbid.
CLI_PLACEHOLDER = "<engine>"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _field(data: dict, *keys: str) -> str:
    node = data
    for k in keys:
        node = node[k]
    assert isinstance(node, str), f"field {'.'.join(keys)} is not a string: {type(node)}"
    return node


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _load_mcp_spine_server(scratch_root: Path):
    """Import `mcp_spine_server` fresh, under a scratch `SPINE_FILE`/`SPINE_ENGINE`/
    `SPINE_SESSION` env. It reads those from the environment at IMPORT time -- since issue
    #603 without raising, binding `SPINE = None` when nothing is named -- and the scratch
    env is what keeps this file's own tests off whatever spine the developer's shell is
    bound to. That is also why it is never imported at this file's module scope: the
    binding, and the `sys.path.insert` the door does beside it, would then happen at
    COLLECTION time, under the ambient environment, before any test could supply a scratch
    one. Same shape as `tests/test_crew_launcher.py`'s `CrewGrantTiesToDoorTests.
    _load_mcp_spine_server`, which ties `CREW_ALLOWED_TOOLS` the same way. A fresh module
    name per call, so a cached `sys.modules` entry from a prior call in the same test
    process cannot carry a stale binding forward."""
    spine_file = scratch_root / "scratch-spine.json"
    spine_file.write_text("{}", encoding="utf-8")
    saved = {k: os.environ.get(k) for k in ("SPINE_FILE", "SPINE_ENGINE", "SPINE_SESSION")}
    os.environ["SPINE_FILE"] = str(spine_file)
    os.environ["SPINE_ENGINE"] = str(ROOT / "scripts" / "checklist_engine.py")
    os.environ.setdefault("SPINE_SESSION", "")
    try:
        spec = importlib.util.spec_from_file_location(
            "mcp_spine_server_adoption_tie_check", ROOT / "scripts" / "mcp_spine_server.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _engine_verbs() -> set[str]:
    """The engine's own verb registry, read from its argparse subparsers -- never
    hand-typed. `checklist_engine.parse_args` builds the whole subparser tree in one
    function and returns `p.parse_args(argv)` on its last line, so there is no
    module-level list to import; handing it one bogus verb makes argparse itself print
    every valid choice to stderr before exiting, which is what this reads. Needs no
    `SPINE_FILE`/`SPINE_ENGINE` env -- unlike `mcp_spine_server`, `checklist_engine` reads
    neither at import time."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import checklist_engine  # noqa: E402 -- see docstring above for why this is safe here

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        try:
            checklist_engine.parse_args(["--file", "/dev/null", "__not_a_real_verb__"])
        except SystemExit:
            pass
    match = re.search(r"\{([\w,-]+)\}", buf.getvalue())
    assert match, f"could not read the engine's verb list from argparse stderr:\n{buf.getvalue()}"
    return set(match.group(1).split(","))


def _door_reachable_verbs() -> set[str]:
    """Every engine verb `mcp_spine_server.call_tool` actually reaches, read from its own
    source TEXT via the literal first argument to every `run_engine(...)` call -- never
    hand-typed, and read as text (not imported) so it needs no scratch env either."""
    text = _text("scripts/mcp_spine_server.py")
    return set(re.findall(r'run_engine\(\s*"([\w-]+)"', text))


class TestDoorSurfaceTiesToTheEngineRegistry:
    """`DOOR_TOOL_NAMES` and `CLI_ONLY_VERBS` used to be hand-typed and froze at 7 tools /
    5 CLI-only verbs while the door grew to 9 tools covering all 18 of the engine's verbs
    (issue #559, N1: "anything that we can only do via the cli is a defect"). Both are
    tied here to their sources so a future door or engine change goes red instead of
    leaving a pin that reads as coverage while asserting a false fact."""

    def test_door_tool_names_tie_to_mcp_spine_servers_own_registry(self, tmp_path):
        server = _load_mcp_spine_server(tmp_path)
        # Scoped to the engine tools (TOOL_NAMES - LIFECYCLE_TOOL_NAMES): issue #559,
        # C3/g3 added spine_open/spine_close, which are NOT pass-throughs this file's
        # Tier3 "## MCP door" section describes (see TestTier3ChecklistEngineReference
        # below, which pins DOOR_TOOL_NAMES against that doc section -- a lifecycle tool
        # is a different surface and documenting it there is a follow-on, not this pin's
        # job). DOOR_TOOL_NAMES itself stays exactly the 9 it always named.
        engine_tools = server.TOOL_NAMES - server.LIFECYCLE_TOOL_NAMES
        assert set(DOOR_TOOL_NAMES) == engine_tools, (
            "DOOR_TOOL_NAMES has drifted from mcp_spine_server.TOOL_NAMES's engine tools -- "
            "a tool the door added or removed is not reflected in this file's pin"
        )

    def test_door_has_all_nine_tools_todays_pin_expects(self, tmp_path):
        # CONTROL for the tie test above: pins the count so a future door regression
        # (e.g. a tool silently dropped) cannot slip through by shrinking both sides of
        # the comparison in lockstep. Scoped the same way: 9 engine tools, not counting
        # the 2 lifecycle tools (issue #559, C3/g3).
        server = _load_mcp_spine_server(tmp_path)
        assert len(server.TOOL_NAMES - server.LIFECYCLE_TOOL_NAMES) == 9

    def test_engine_has_all_eighteen_verbs_todays_pins_expect(self):
        # CONTROL for the gap test below, same reason: pins the engine's own verb count
        # so both sides of the gap comparison cannot shrink together unnoticed.
        assert len(_engine_verbs()) == 18

    def test_cli_only_verbs_tie_to_the_gap_between_engine_and_door(self):
        engine_verbs = _engine_verbs()
        door_reachable = _door_reachable_verbs()
        assert door_reachable <= engine_verbs, (
            f"mcp_spine_server.call_tool reaches a verb the engine does not have: "
            f"{sorted(door_reachable - engine_verbs)}"
        )
        gap = engine_verbs - door_reachable
        assert gap == set(CLI_ONLY_VERBS), (
            f"CLI_ONLY_VERBS ({sorted(CLI_ONLY_VERBS)}) no longer matches the verbs the "
            f"door does not reach ({sorted(gap)}) -- the door grew or shrank coverage and "
            f"this file's pin was not updated with it"
        )


def _paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


#: Abbreviations whose full stop is NOT the end of a sentence. Without these,
#: `re.split(r"(?<=[.!?])\s+")` cuts "…through the door, e.g. `append` a check"
#: in half and drops the door tool out of the half that names the verb -- a
#: violation that reads as clean. Measured: `e.g.` alone accounted for one of
#: the five violating instructions the one-period splitter let through.
_ABBREVIATIONS = ("e.g.", "i.e.", "etc.", "vs.", "cf.", "approx.")


def _sentences(text: str) -> list[str]:
    """Sentence-width, abbreviation-aware. Callers that want the narrower
    "sentence OR line" unit (`_cli_only_verb_violations`) split on newlines
    first and run this over each line."""
    protected = text
    for idx, abbrev in enumerate(_ABBREVIATIONS):
        protected = protected.replace(abbrev, f"\x00{idx}\x00")
    out = []
    for part in re.split(r"(?<=[.!?])\s+", protected):
        for idx, abbrev in enumerate(_ABBREVIATIONS):
            part = part.replace(f"\x00{idx}\x00", abbrev)
        if part.strip():
            out.append(part)
    return out


#: How a CLI-only verb is written when it is being NAMED AS A VERB: in
#: backticks or quotes. Bare-word matching is what made this whole check
#: unusable -- "shrink or skip the frame", "visit all, append, never block"
#: and "append checks the context warrants" are ordinary English in three
#: different files, and flagging them trains people to delete the check. Same
#: convention `TestTier3CLIOnlyVerbsStayCLI` already documents.
def _verb_name_re(verb: str) -> re.Pattern:
    return re.compile(rf"[`'\"]{re.escape(verb)}[`'\"]")


def _cli_only_verb_violations(
    where: str, text: str, verbs: tuple[str, ...] = CLI_ONLY_VERBS
) -> list[str]:
    """Every place `text` routes a CLI-only verb through a door tool.

    `verbs` defaults to the real `CLI_ONLY_VERBS` (empty today) for every production
    caller. `TestTheViolationPredicateItself` passes `_PREDICATE_SELFTEST_VERBS` instead,
    so this predicate's own mechanism stays exercised independent of how many verbs are
    genuinely CLI-only right now.

    A violation is a STRUCTURAL FACT about one unit: it names a door tool, and
    it names a verb for which no such tool exists. **No polarity judgement is
    made at all** -- there is nothing here that reads intent, so there is
    nothing here to out-write.

    **Unit = sentence OR line, whichever is narrower.** Both halves are load
    bearing:

      * SENTENCE, because a paragraph-wide unit pairs a door tool with a verb
        three sentences away that no reader would connect. Measured at
        paragraph width: 3 false alarms on a coverage table, 5 on the fallback
        prose, and one each on "`skip` is not covered, so it stays CLI" and
        "There is no tool for `append`" -- 5 of 5 false-alarm classes fired.
        At sentence-or-line width, 1 of 5 does.
      * LINE, because a markdown TABLE has no sentence punctuation. Sentence
        splitting alone merges every row into one unit and pairs a header's
        tool names with a verb three rows down. A table row is structurally its
        own unit, and a newline is what says so.

    This replaces a paragraph-wide unit plus an exemption regex
    (`NO_DOOR_TOOL_FOR_IT`) and a +/-120 character window around the verb. The
    exemption is DELETED because the narrowed unit makes it unnecessary, **not
    because it was inert**: its phrases match 21 times across 17 places in the
    walked corpus, and it is what kept this file's own INNOCENT fixtures green.
    As an exemption inside this loop it fires 0 times today, because no
    paragraph in the corpus currently pairs a door tool with a backticked
    CLI-only verb at all. Both numbers are the record; an earlier audit reported
    only the second and concluded the regex was dead code.

    KNOWN, ACCEPTED COST -- one false-alarm class survives: prose that FORBIDS
    the violation inside a single sentence ("`spine_advance` closes a gate, but
    `skip` has no door tool and stays CLI") is flagged. That is accepted because
    it is VISIBLE and REWORD-ABLE: the author sees a red test and splits the
    sentence in two, which the corpus's own doctrine paragraph already does. It
    is a documentation style rule an author can follow deterministically, not a
    silent hole. Pinned by
    `TestTheViolationPredicateItself::test_the_one_accepted_false_alarm_still_fires`.

    STATED RESIDUAL -- narrowing gives up cross-sentence pairing. A door tool in
    one sentence and a CLI-only verb in the next is no longer caught. Pinned, so
    that a future widening has to be a deliberate edit to
    `NOT_CAUGHT_AT_THIS_WIDTH` and a re-measurement of the false alarms above.
    """
    found = []
    for line in text.split("\n"):
        for unit in _sentences(line):
            door = DOOR_TOOL_RE.search(unit)
            if not door:
                continue
            for verb in verbs:
                if _verb_name_re(verb).search(unit):
                    found.append(
                        f"  {where}: verb {verb!r} + door tool {door.group(0)!r}\n"
                        f"    {unit.strip()[:300]}"
                    )
                    break
    return found


# --------------------------------------------------------------------------- #
# Every file that carries an INSTRUCTION an agent acts on -- DISCOVERED BY
# WALKING `skills/`, never enumerated.
#
# This used to be a hand-written list of 13 files under a docstring claiming it
# covered "every instruction an agent actually acts on". There are 100 files
# under `skills/`. The 87 that were not on the list included BOTH survey
# checklists (`REVIEW_SURVEY.template.json`, `INTERROGATION.template.json`),
# both implementer/commander plan templates, and `skills/admiral/SKILL.md`,
# which drives the engine directly and appeared in no tier at all. Each of them
# accepted a planted violation with the suite fully green.
#
# An enumerated list is the same defect as an enumerated pin: it covers what
# someone thought of on the day, and a file that lands tomorrow is uncovered
# until somebody remembers. So the corpus is WALKED, and the only exclusion is
# a rule the walk itself applies:
#
#   * suffix not in {.md, .json} -- MEASURED, not assumed: there is exactly one
#     such file today, `skills/replan/scripts/verify_replan.py`, and it is a
#     verifier a human/agent RUNS, not prose an agent reads and acts on.
#     This rationale previously named `skills/workbench/scripts/checklist_engine.py`
#     as that one file. **No such file exists** -- the engine lives at
#     `scripts/checklist_engine.py`, outside `skills/` entirely, so it was never
#     in the walk's scope to exclude. The COUNT was right by luck; the reason
#     given for it had never been run. Same shape as the `directives` claim
#     below: a documented coverage claim about something nobody measured.
#
# There is no per-file exclusion, and adding one would be the defect returning.
# --------------------------------------------------------------------------- #

#: Suffixes that carry instruction text an agent reads.
INSTRUCTION_SUFFIXES = (".md", ".json")


def _walk_instruction_files() -> list[str]:
    return sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "skills").rglob("*")
        if p.is_file() and p.suffix in INSTRUCTION_SUFFIXES
    )


INSTRUCTION_FILES = _walk_instruction_files()


def _json_strings(node, prefix: str, out: list[tuple[str, str]]) -> None:
    """Every string leaf in a JSON document, addressed by its own path.

    Every string, with no key allow-list. The previous version named four keys
    (`imperative`, `directives`, `constraints`, pre/postcondition `statement`)
    and only under `tasks`, which is an enumeration one level down from the file
    list -- an instruction in a key nobody listed is invisible, and a template
    whose top level is not `tasks` (8 of the 20 JSON files) contributed nothing
    at all.

    It also makes the `directives` claim TRUE. That extractor guarded on
    `isinstance(value, str)` while `directives` is `dict` (3 occurrences) or
    `None` (58) and never once a string in this corpus -- a documented coverage
    claim over a field it could not reach. Recursing over every value covers the
    dict's own strings instead of claiming to.
    """
    if isinstance(node, str):
        if node.strip():
            out.append((prefix, node))
    elif isinstance(node, dict):
        for key, value in node.items():
            _json_strings(value, f"{prefix}.{key}", out)
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            _json_strings(value, f"{prefix}[{idx}]", out)


def _instruction_texts(path: str) -> list[tuple[str, str]]:
    """(where, text) pairs of everything in `path` that instructs an agent.

    Markdown: the whole file, one chunk. JSON: every string leaf, by JSON path.
    """
    if not path.endswith(".json"):
        return [(path, _text(path))]
    out: list[tuple[str, str]] = []
    _json_strings(_load(path), path, out)
    return out


def _all_instruction_texts() -> list[tuple[str, str]]:
    out = []
    for path in INSTRUCTION_FILES:
        out.extend(_instruction_texts(path))
    return out


class TestTheViolationPredicateItself:
    """A check is only worth what it can detect, what it leaves alone, and what
    it openly gives up. All three are measured here, in the assertion path, so a
    future edit to the unit width or `_verb_name_re` cannot quietly move any of
    them.

    The unit was PARAGRAPH-wide and carried an exemption regex. Both are gone.
    Measured, paragraph-vs-sentence-or-line:

        real defect (interrogator:26 pre-repair)   caught -> CAUGHT
        planted violation (the walk's own target)  caught -> CAUGHT
        coverage table                              3 FA  -> clean
        fallback prose (7 tools, then the 5)        5 FA  -> clean
        "`skip` is not covered, so it stays CLI"    1 FA  -> clean
        "There is no tool for `append`"             1 FA  -> clean
        prose FORBIDDING the violation              1 FA  -> 1 FA  (accepted)
        live corpus (100 files)                     0     -> 0
    """

    VIOLATING = {
        "one sentence":
            "Drive your survey through the door: call `spine_survey_result` to `append` "
            "new checks and to `skip` items an earlier answer settled.",
        "split on e.g.":
            "Route every survey move through `spine_survey_result`, e.g. `append` for a "
            "new check.",
        "heading and body":
            "### Surveys\nUse `spine_survey_result` for everything, including `append`.",
        "quoted rather than backticked":
            "Call `spine_survey_result` with action='append' to add a check.",
        "fully-qualified tool name":
            "Call `mcp__spine__spine_survey_result` to `skip` an item.",
        "table row":
            "| verb | route |\n| --- | --- |\n| `append` | `spine_survey_result` |",
    }

    INNOCENT = {
        "the rule across two sentences":
            "Call `spine_advance` to close a gate. `skip` has no door tool, so it stays "
            "CLI-only.",
        "the doctrine paragraph":
            "**5 verbs have no door tool at all, and stay CLI-only regardless of who is "
            "driving:** `skip`, `reopen`, `append`, `amend`, `flag-candidate`. Use "
            "`spine_advance` for the gates that do have one.",
        "a coverage table":
            "| tool | verbs |\n| --- | --- |\n| `spine_advance` | advance |\n"
            "| (none) | `skip`, `reopen`, `append`, `amend`, `flag-candidate` |",
    }

    #: THE ACCEPTED COST, written out rather than argued. Correct prose that
    #: forbids the violation inside ONE sentence is flagged. The remedy is
    #: deterministic and takes one edit -- split the sentence, exactly as
    #: `INNOCENT["the rule across two sentences"]` does -- so this is a
    #: documentation style rule, not a silent hole. It is pinned as FIRING so
    #: that anyone who finds it annoying has to change this test deliberately.
    ACCEPTED_FALSE_ALARM = {
        "the rule stated in a single sentence":
            "`spine_advance` closes a gate, but `skip` has no door tool and stays CLI.",
    }

    #: THE STATED RESIDUAL. Narrowing the unit from paragraph to sentence-or-line
    #: buys 4 of 5 false-alarm classes and costs cross-sentence pairing: these
    #: two ARE violations and are no longer detected. Pinned as NOT caught, so a
    #: future widening is a deliberate edit here plus a re-measurement of the
    #: false alarms in this class's docstring -- never an accident.
    NOT_CAUGHT_AT_THIS_WIDTH = {
        "adjacent sentences":
            "Drive the survey through the door with `spine_survey_result`. Use `append` "
            "to add a check and `skip` to drop one.",
        "bullet list, tool in the lead-in":
            "Drive the survey through the door (`spine_survey_result`):\n"
            "- `append` a new check when the context warrants one.\n"
            "- `skip` an item an earlier answer settled.",
    }

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_a_violating_instruction_is_caught(self, label):
        assert _cli_only_verb_violations(
            "<case>", self.VIOLATING[label], verbs=_PREDICATE_SELFTEST_VERBS
        ), (
            f"the predicate did not catch {label!r} -- it routes a CLI-only verb through "
            f"a door tool, which is the whole defect this check exists for"
        )

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_an_innocent_instruction_is_left_alone(self, label):
        found = _cli_only_verb_violations(
            "<case>", self.INNOCENT[label], verbs=_PREDICATE_SELFTEST_VERBS
        )
        assert not found, (
            f"the predicate flagged {label!r}, which is a CORRECT statement of the rule "
            f"it enforces. A check that fails on the best statement of its own rule gets "
            f"deleted by the next person to read it.\n" + "\n".join(found)
        )

    @pytest.mark.parametrize("label", sorted(ACCEPTED_FALSE_ALARM))
    def test_the_one_accepted_false_alarm_still_fires(self, label):
        """Not a defect being hidden -- a cost being recorded where it can be
        read. If this ever stops firing the predicate has changed shape, and the
        false-alarm table in this class's docstring is stale."""
        assert _cli_only_verb_violations(
            "<case>", self.ACCEPTED_FALSE_ALARM[label], verbs=_PREDICATE_SELFTEST_VERBS
        ), (
            f"{label!r} is no longer flagged. That is an improvement, not a failure -- but "
            f"it means the predicate changed, so re-measure the false-alarm table above "
            f"and move this case into INNOCENT in the same edit."
        )

    @pytest.mark.parametrize("label", sorted(NOT_CAUGHT_AT_THIS_WIDTH))
    def test_the_stated_residual_is_still_the_residual(self, label):
        """Cross-sentence pairing is given up on purpose. Asserting the gap
        keeps it visible: a reader of this file learns what the check does NOT
        do from the check itself, not from a paragraph somebody has to remember
        to update."""
        found = _cli_only_verb_violations(
            "<case>", self.NOT_CAUGHT_AT_THIS_WIDTH[label], verbs=_PREDICATE_SELFTEST_VERBS
        )
        assert not found, (
            f"{label!r} is now caught, which means the unit was widened. That is allowed, "
            f"but the false alarms it buys back are the reason it was narrowed -- "
            f"re-measure the table in this class's docstring against the live corpus and "
            f"update it in the same edit.\n" + "\n".join(found)
        )

    def test_the_sentence_splitter_does_not_cut_on_an_abbreviation(self):
        text = "Route it through `spine_survey_result`, e.g. `append` for a new check."
        assert len(_sentences(text)) == 1, (
            "`e.g.` was read as the end of a sentence, which splits an instruction in "
            "half and drops the door tool out of the half that names the verb"
        )

    def test_json_extraction_reaches_a_directives_dict(self):
        """The `directives` coverage claim, made true. `directives` is `dict` or
        `None` in every template in this corpus and never a string, so the
        previous `isinstance(value, str)` guard reached none of them."""
        out: list[tuple[str, str]] = []
        _json_strings({"tasks": {"g1": {"directives": {"a": {"b": "REACHED"}, "c": ["ALSO"]}}}},
                      "x.json", out)
        assert ("x.json.tasks.g1.directives.a.b", "REACHED") in out
        assert ("x.json.tasks.g1.directives.c[0]", "ALSO") in out

        real = _instruction_texts("skills/admiral/templates/ADMIRAL_SPINE.template.json")
        assert any(".directives." in where for where, _ in real), (
            "no string under a real template's `directives` field is extracted -- the "
            "docstring claims that field is covered, so either cover it or stop claiming it"
        )


class TestTheCorpusIsWalkedNotListed:
    """The walk itself, pinned. FAILS IF: the walk stops finding the corpus, or
    somebody replaces it with a list again.

    What would have to be true for this to fail: `skills/` shrinks below 60
    files, or a file that carries an instruction stops being discovered."""

    def test_the_walk_finds_the_whole_corpus(self):
        on_disk = [p for p in (ROOT / "skills").rglob("*")
                   if p.is_file() and p.suffix in INSTRUCTION_SUFFIXES]
        assert len(INSTRUCTION_FILES) == len(on_disk)
        # Not an exact count -- that would be a literal by another name, red on
        # every legitimate addition. A floor, because the failure this guards
        # against is the corpus silently NARROWING back to a handful.
        assert len(INSTRUCTION_FILES) >= 60, (
            f"the instruction walk found only {len(INSTRUCTION_FILES)} files under "
            f"skills/. It used to be a 13-file literal while 100 files were on disk; "
            f"if the walk has been narrowed, say by what rule and put the rule IN the "
            f"walk, never by dropping names from a list."
        )

    def test_the_suffix_exclusion_names_a_file_that_exists(self):
        """The walk's ONE exclusion rule, measured rather than described.

        Its rationale used to name `skills/workbench/scripts/checklist_engine.py`
        as the single non-`.md`/`.json` file under `skills/`. That path does not
        exist and never did -- the engine is at `scripts/checklist_engine.py`,
        outside `skills/`. The exclusion was correct; the reason given for it was
        fiction. So the reason is now run.

        Not an exact count of excluded files -- that would be a literal by
        another name, red on any legitimate addition. Two facts only: the file
        the comment names is real, and the suffix rule is what keeps it out.
        """
        excluded = ROOT / "skills" / "replan" / "scripts" / "verify_replan.py"
        assert excluded.is_file(), (
            f"{excluded} is named in the walk's exclusion rationale but does not exist. "
            f"An unrunnable reason is how the last one stayed wrong -- name a real file "
            f"or drop the example."
        )
        assert excluded.suffix not in INSTRUCTION_SUFFIXES
        assert excluded.relative_to(ROOT).as_posix() not in INSTRUCTION_FILES

    @pytest.mark.parametrize("path", [
        # The eight that a planted violation walked straight through when the
        # corpus was a literal. Named here as a REGRESSION record, not as the
        # source of coverage -- coverage is the walk.
        "skills/reviewer/templates/REVIEW_SURVEY.template.json",
        "skills/interrogator/templates/INTERROGATION.template.json",
        "skills/implementer/templates/IMPLEMENTER_PLAN.template.json",
        "skills/commander/templates/EXECUTE_PLAN.template.json",
        "skills/admiral/SKILL.md",
        "skills/commander/SKILL.md",
        "skills/write-a-skill/SKILL.md",
        "skills/cartographer/SKILL.md",
    ])
    def test_previously_uncovered_files_are_now_in_the_corpus(self, path):
        assert path in INSTRUCTION_FILES
        assert _instruction_texts(path), f"{path} is walked but yields no instruction text"


# --------------------------------------------------------------------------- #
# Tier 1 -- literal engine command lines an agent executes. JSON field path.
# --------------------------------------------------------------------------- #

TIER1_JSON_FIELDS = [
    # (path, field_path_keys, expected_door_tool_substring, removed_cli_substring)
    #
    # The fourth column is the exact literal command line issue #559 REMOVED from this
    # field -- it is a record of what was swept, and its absence is what is now asserted.
    # It was chosen as the exact line rather than the bare '<engine>' placeholder because
    # some imperative fields (e.g. COMMANDER_SPINE plan/archive) carried more than one
    # engine command in prose, so a generic placeholder check could be satisfied by an
    # unrelated verb's mention while the specific line in question was untouched. That
    # precision is worth exactly as much to the absence assertion as it was to the
    # presence one, so the data is kept verbatim and only the assertion is inverted.
    # The placeholder itself is forbidden field-wide alongside it, which is what catches
    # a reworded command line that no longer matches the recorded literal.
    ("skills/commander/templates/COMMANDER_SPINE.template.json", ("tasks", "init", "imperative"),
     "spine_lease", "<engine> claim --session-id <commander-session-id>"),
    ("skills/commander/templates/COMMANDER_SPINE.template.json", ("tasks", "plan", "imperative"),
     "spine_evidence", "attach plan --type user-decision --field cite='LAUNCH_ORDER:Mission'"),
    ("skills/commander/templates/COMMANDER_SPINE.template.json", ("tasks", "archive", "imperative"),
     "spine_lease", "<engine> release --session-id <commander-session-id>"),
    ("skills/admiral/templates/ADMIRAL_SPINE.template.json", ("tasks", "init", "imperative"),
     "spine_lease", "<engine> claim --session-id <admiral-session-id>"),
    ("skills/admiral/templates/ADMIRAL_SPINE.template.json", ("tasks", "closeout", "imperative"),
     "spine_lease", "<engine> release --session-id <admiral-session-id>"),
    ("skills/explorer/templates/EXPLORER_SPINE.template.json", ("tasks", "init", "imperative"),
     "spine_lease", "<engine> claim --session-id <work-id>"),
    ("skills/explorer/templates/EXPLORER_SPINE.template.json", ("tasks", "route", "imperative"),
     "spine_lease", "<engine> release --session-id <work-id>"),
]


class TestTier1ImperativeFields:
    """Each of these 7 imperative fields must name a door tool as the path an agent
    takes, by JSON field path, AND must no longer carry that SAME action's engine
    command line (issue #559).

    The second half used to be its mirror image -- `test_field_still_carries_cli_fallback`,
    failing with "the CLI door must stay, never be removed or discouraged". That
    assertion is why the swept text grew back twice: a lane deleted the clauses, this
    suite went red, and the lane restored them believing it had broken a rule. The
    human ruling that settles it, verbatim: "the agents should not know about the CLI.
    period." """

    @pytest.mark.parametrize("path,keys,door_substr,cli_substr", TIER1_JSON_FIELDS)
    def test_field_names_door_tool_as_default(self, path, keys, door_substr, cli_substr):
        """Affirmatively, not merely present. "never call spine_lease" names
        `spine_lease` and is the negation of what this pins."""
        data = _load(path)
        field = _field(data, *keys)
        assert _named_affirmatively(field, door_substr), (
            f"{path} .{'.'.join(keys)} does not name the door tool {door_substr!r} "
            f"as a default path (it must appear in a sentence that is not forbidding it)"
        )

    @pytest.mark.parametrize("path,keys,door_substr,cli_substr", TIER1_JSON_FIELDS)
    def test_field_no_longer_carries_a_cli_command_line(self, path, keys, door_substr, cli_substr):
        """ABSENCE IS THE FACT, so no prohibition check is needed or wanted here --
        unlike the door half above, there is no polarity to out-write. "do not run
        `<engine> claim ...`" retires the command line and hands it over in the same
        breath, and this assertion is red on it either way, which is the point."""
        data = _load(path)
        field = _field(data, *keys)
        assert cli_substr not in field, (
            f"{path} .{'.'.join(keys)} carries the engine command line {cli_substr!r} "
            f"again. The ruling, verbatim: \"the agents should not know about the CLI. "
            f"period.\" This text was deleted twice before and grew back twice, both "
            f"times because this very assertion used to REQUIRE it."
        )
        assert CLI_PLACEHOLDER not in field, (
            f"{path} .{'.'.join(keys)} carries the {CLI_PLACEHOLDER!r} placeholder -- a "
            f"stand-in for an engine command line that init_work_area.py deliberately "
            f"never resolves, so it reaches an agent unresolved. Checked alongside the "
            f"exact line above because a REWORDED command line would not match that "
            f"literal while still handing over the same second path."
        )

    @pytest.mark.parametrize("path", [
        "skills/commander/templates/COMMANDER_SPINE.template.json",
        "skills/admiral/templates/ADMIRAL_SPINE.template.json",
        "skills/explorer/templates/EXPLORER_SPINE.template.json",
    ])
    def test_spine_template_still_valid_json(self, path):
        # Guards the "edit as raw text, re-validate with json.load" constraint.
        json.loads((ROOT / path).read_text(encoding="utf-8"))


class TestTier1CommanderCoreAttachLine:
    """commander-core.md's delegated-mode `attach` paragraph: text-based (this file is
    markdown, no JSON field path exists), so the door tool must be named and the engine
    command line must be gone in the SAME paragraph.

    THE LOCATOR MOVED TO THE DOOR SIDE, and it had to. It used to find this paragraph by
    requiring `'<engine> attach'` in it -- the very text issue #559 removes -- so after
    the sweep it could not find the paragraph at all, and BOTH assertions here, including
    the door-affirmative one that is not being weakened, would have died with an
    unrelated "has the CLI line moved?" message. A locator keyed to what must be present
    survives the sweep; one keyed to what must be absent cannot."""

    PATH = "skills/commander/references/commander-core.md"

    def _attach_paragraph(self) -> str:
        text = _text(self.PATH)
        for para in _paragraphs(text):
            if "user-decision` checkpoints" in para and DOOR_TOOL_RE.search(para):
                return para
        raise AssertionError(
            f"{self.PATH} has no paragraph containing both the checkpoint prose and a door "
            f"tool name -- has the delegated-mode attach instruction moved or been deleted?"
        )

    def test_paragraph_names_door_tool(self):
        """Affirmatively: "never call spine_evidence here" names it and is the
        negation of what this pins."""
        para = self._attach_paragraph()
        assert _named_affirmatively(para, "spine_evidence"), (
            f"{self.PATH}'s delegated-mode attach paragraph does not name spine_evidence "
            f"as the door default (it must appear in a clause that is not forbidding it)"
        )

    def test_paragraph_no_longer_carries_a_cli_command_line(self):
        para = self._attach_paragraph()
        assert CLI_PLACEHOLDER not in para, (
            f"{self.PATH}'s delegated-mode attach paragraph carries the "
            f"{CLI_PLACEHOLDER!r} placeholder again. The ruling, verbatim: \"the agents "
            f"should not know about the CLI. period.\""
        )
        assert CLI_SCRIPT_MARKER not in para, (
            f"{self.PATH}'s delegated-mode attach paragraph names "
            f"{CLI_SCRIPT_MARKER!r} -- the placeholder is not the only spelling of the "
            f"second path, and a rename-around that writes the script's own name is the "
            f"form that survives deleting the placeholder"
        )


# --------------------------------------------------------------------------- #
# Tier 2 -- the drive-path prose in SKILL bodies. Text-based, paragraph-scoped so a
# door-tool mention anywhere in the file cannot satisfy this on its own: the SAME
# paragraph that tells an agent how to drive the engine must name a door tool and
# must not hand over the CLI beside it (issue #559).
# --------------------------------------------------------------------------- #

#: `skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md` are DELIBERATELY
#: not on this list (issue #559, "a spine is the job"): a dispatched crew now
#: gets its OWN spine bound before it starts (`run_crew.py`'s `--spine`
#: binding), so the g1 identity-trade fact this tier pinned -- "an in-session
#: dispatched crew shares its parent's MCP scope and must use the CLI for its
#: own plan" -- is no longer true for these two files, and the human ruling is
#: "the agents should not know about the CLI. period." Their own,
#: CLI-mentions-nothing invariant is `TestTier2SpineAlreadyBoundForDispatchedCrews`
#: below, not this tier -- and as of #559 this tier now holds every file on this
#: list to that same standard.
#:
#: `skills/workbench/SKILL.md` came OFF this list with the inversion. It carries the
#: swept text today and is owned by a different lane in the same wave, so an absence
#: assertion here would go red on a file this change is fenced from. Coverage of its
#: absence is not lost -- `tests/test_cli_retirement_guard.py` walks the whole corpus,
#: `skills/workbench/**` included. What IS lost is this tier's paragraph-scoped DOOR
#: assertion for that one file, which nothing else replaces; re-adding the entry once
#: that lane merges restores it.
TIER2_SKILL_FILES = [
    "skills/charter/SKILL.md",
    "skills/interrogator/SKILL.md",
    "skills/explorer/SKILL.md",
]

CLI_SCRIPT_MARKER = "checklist_engine.py"


def _door_path_paragraph(path: str) -> str:
    """The paragraph that tells an agent how to drive this skill's checklist.

    Located by the DOOR half, which is what must be present. Two things changed
    here with #559, and both are consequences of the sweep rather than choices:

      * the CLI marker is no longer part of the locator, because it is no longer
        in the corpus to locate by; and
      * `_asserts_the_default` is no longer required, because "default" is
        two-path vocabulary. A default implies an alternative, and for a bound
        spine there is now exactly one path. Requiring the word would mean
        writing it back into the very sentences this epic rewrote -- and in
        `skills/interrogator/SKILL.md` it would be a lie, since a survey the
        door is not bound to cannot be driven through the door at all.

    What replaces it is not weaker in the way that matters: the door tool must
    still be named AFFIRMATIVELY (prohibition-checked), in the paragraph that is
    about driving the checklist, not merely somewhere in the file.
    """
    text = _text(path)
    for para in _paragraphs(text):
        if DOOR_TOOL_RE.search(para) and any(
            _named_affirmatively(para, name) for name in DOOR_TOOL_NAMES
        ):
            return para
    raise AssertionError(
        f"{path} has no single paragraph naming a door tool affirmatively as the way its "
        f"checklist is driven -- an agent reading this file has no path at all"
    )


class TestTier2SkillBodyDefaultPath:
    """Was two-sided (a door tool AND the CLI marker in one paragraph). Issue #559
    inverted the second half: the paragraph that names the door must not also hand
    over the engine command line, and the file must not name it anywhere else
    either. This is `TestTier2SpineAlreadyBoundForDispatchedCrews` widened from its
    two files to this tier's."""

    @pytest.mark.parametrize("path", TIER2_SKILL_FILES)
    def test_door_path_paragraph_names_the_door_and_not_the_cli(self, path):
        # Raises AssertionError (via _door_path_paragraph) if no such paragraph exists.
        para = _door_path_paragraph(path)
        assert DOOR_TOOL_RE.search(para)
        assert CLI_SCRIPT_MARKER not in para, (
            f"{path}'s drive-path paragraph names the door and then hands over "
            f"{CLI_SCRIPT_MARKER!r} beside it. The ruling, verbatim: \"the agents should "
            f"not know about the CLI. period.\""
        )

    @pytest.mark.parametrize("path", TIER2_SKILL_FILES)
    def test_file_hands_over_no_second_path_anywhere(self, path):
        """File-wide, so a clause pushed out of the drive-path paragraph into a
        neighbouring one does not escape.

        NOT `CLI_SCRIPT_MARKER not in text`, which is what
        `TestTier2SpineAlreadyBoundForDispatchedCrews` asserts for its two files.
        That standard is right there and wrong here: `skills/explorer/SKILL.md`
        carries a scripts manifest -- "Scripts: `checklist_engine.py`,
        `init_work_area.py`, `run_crew.py` ..." -- which names the engine as a
        component of the skill and tells nobody to run it. The epic drew its line
        between a command and a component mention, and `test_cli_retirement_guard.py`
        pins BOTH directions of that line (`TestTheInvocationPredicateItself`); this
        assertion sits on the same side of it.
        """
        text = _text(path)
        assert CLI_PLACEHOLDER not in text, (
            f"{path} carries the {CLI_PLACEHOLDER!r} placeholder -- an unresolved stand-in "
            f"for an engine command line"
        )
        clause = re.search(r"CLI[\s-]+fallback", text, re.I)
        assert clause is None, (
            f"{path} carries a {clause.group(0)!r} clause again -- it hands an agent a "
            f"second path to the engine beside the door. The ruling, verbatim: \"the "
            f"agents should not know about the CLI. period.\""
        )


class TestTier2SpineAlreadyBoundForDispatchedCrews:
    """Issue #559 ("a spine is the job") supersedes the g1 identity-trade fact
    the old `TestTier2IdentityTradeCarried` pinned for these two files
    specifically: `run_crew.py` now binds a dispatched crew's OWN spine before
    it starts (`--spine`, `SPINE_FILE`/`SPINE_SESSION`), so it no longer shares
    the dispatching parent's MCP scope and no longer needs the CLI for its own
    plan. The human ruling this pins, verbatim: "the agents should not know
    about the CLI. period."

    FAILS IF either file regresses to routing a dispatched crew's own plan
    through the CLI, stops telling it a spine is already bound, or mentions the
    CLI/`checklist_engine.py` at all."""

    PATHS = ["skills/implementer/SKILL.md", "skills/reviewer/SKILL.md"]

    @pytest.mark.parametrize("path", PATHS)
    def test_file_never_names_the_cli_at_all(self, path):
        """PRESENCE IS THE FACT (same category as Tier5's `test_no_door_tool_name_introduced`,
        applied in reverse): there is no polarity to out-write here, because the
        rule is "never mention it", not "mention it a certain way"."""
        text = _text(path)
        assert CLI_SCRIPT_MARKER not in text, (
            f"{path} mentions {CLI_SCRIPT_MARKER!r} -- issue #559 removed the CLI-fallback "
            f"instruction from this file so a dispatched crew is never told about the "
            f"engine CLI at all"
        )
        assert re.search(r"\bCLI\b", text) is None, (
            f"{path} still says \"CLI\" -- a dispatched crew must not be told it exists"
        )

    @pytest.mark.parametrize("path", PATHS)
    def test_file_states_a_dispatched_crews_own_spine_is_already_bound(self, path):
        text = _text(path)
        assert _named_affirmatively(text, "spine_status"), (
            f"{path} does not name spine_status as a dispatched crew's first call"
        )
        bound = [
            s for s in _sentences(text)
            if re.search(r"\bbound\b", s, re.I) and re.search(r"spine", s, re.I)
        ]
        assert bound, (
            f"{path} no longer states, in one sentence, that a dispatched crew's spine "
            f"is already bound"
        )

    @pytest.mark.parametrize("path", PATHS)
    def test_file_tells_a_dispatched_crew_not_to_author_its_own_plan(self, path):
        text = _text(path)
        assert re.search(r"do not author", text, re.I), (
            f"{path} no longer tells a dispatched crew NOT to author a plan/survey of its "
            f"own when a spine is already bound -- without that instruction a crew reading "
            f"the generic 'build your own plan' guidance elsewhere in the file has no "
            f"reason not to"
        )


# --------------------------------------------------------------------------- #
# Tier 3 -- the engine CLI reference every Tier2 file points at.
# --------------------------------------------------------------------------- #

TIER3_PATH = "skills/workbench/references/checklist-engine.md"

#: The heading of the section this tier exists to pin. Every Tier3 assertion
#: below is scoped to the text UNDER this heading, never to the whole file.
#:
#: Why: before this scoping, deleting the entire `## MCP door` section -- all of
#: it, including the CLI-only-verb rule, the dispatched-subagent explanation and
#: "Nothing here removes or discourages the CLI" -- left every Tier3 assertion
#: green, because the single rewritten leading paragraph at the top of the file
#: already satisfied each whole-file substring check on its own. A tier that
#: cannot detect the deletion of the thing it pins is not a tier.
TIER3_SECTION_HEADING = "## MCP door"


def _tier3_door_section() -> str:
    """The body under `## MCP door`, up to the next `## ` heading.

    Raises if the heading is gone -- which is itself the first way the deletion
    mutation is caught, before any content assertion runs.
    """
    text = _text(TIER3_PATH)
    start = text.find(TIER3_SECTION_HEADING)
    assert start != -1, (
        f"{TIER3_PATH} no longer has a {TIER3_SECTION_HEADING!r} section. Every "
        f"assertion in Tier3 is about the content of that section; if it was renamed, "
        f"update TIER3_SECTION_HEADING in the same change, and if it was deleted, the "
        f"door is no longer documented anywhere an agent reads."
    )
    rest = text[start + len(TIER3_SECTION_HEADING):]
    end = rest.find("\n## ")
    return rest[:end] if end != -1 else rest


class TestTier3ChecklistEngineReference:
    """Section-scoped. FAILS IF: the `## MCP door` section is deleted, emptied, or
    stops naming the door tools and the rule that they are how a checklist is
    driven. Prose elsewhere in the file cannot satisfy either.

    THREE ASSERTIONS WERE DELETED HERE BY ISSUE #559, not inverted:
    `test_still_names_cli_invocation`, `test_door_section_itself_keeps_the_cli` and
    `test_states_identity_trade_rule`. All three REQUIRED this file to hand an agent
    the CLI -- the last of them required a sentence routing a dispatched subagent to
    it for its own plan, which `run_crew.py --spine` made false. They are deleted
    rather than inverted because this file belongs to a different lane in the same
    wave: it still carries the swept text today, and an absence assertion would go
    red on a file this change is fenced from. `tests/test_cli_retirement_guard.py`
    walks the whole corpus and asserts that absence, `skills/workbench/**` included,
    so the coverage lands there instead."""

    def test_names_door_tools_as_default(self):
        section = _tier3_door_section()
        for name in DOOR_TOOL_NAMES:
            assert name in section, (
                f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section never names door tool "
                f"{name} -- an agent reading this section would not know it exists"
            )
        assert _asserts_the_default(section), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer states the door "
            f"is the default path. Asked with the denial in front counted: 'the door is "
            f"NOT the default' contains the word 'default' and used to satisfy this."
        )

    def test_lease_section_carries_door_equivalent(self):
        text = _text(TIER3_PATH)
        # Session lease section: the CLI claim/heartbeat/release block must still be there,
        # AND a door equivalent (spine_lease) must be named near it.
        idx = text.find("## Session lease")
        assert idx != -1, "Session lease section missing"
        section = text[idx: idx + 2000]
        assert "claim" in section and "heartbeat" in section and "release" in section
        assert "spine_lease" in section


#: How a CLI-only verb must be written when it is documented as such: in
#: backticks, as a literal verb name. A BARE substring check (`"skip" in text`)
#: is vacuous -- it is satisfied by ordinary English prose ("do not improvise,
#: skip, or ...") that is not documenting the verb at all, which is exactly how
#: this assertion used to survive the deletion of the rule it was pinning.
def _verb_token_re(verb: str) -> re.Pattern:
    return re.compile(rf"`{re.escape(verb)}`")


class TestTier3CLIOnlyVerbsStayCLI:
    """Close criterion 3, as it stood while `CLI_ONLY_VERBS` was non-empty: any verb it
    names has NO door tool, and the `## MCP door` section must keep documenting it as
    CLI-only, never attribute a door tool to it (no door tool name in the same sentence
    as the verb).

    `CLI_ONLY_VERBS` is empty today (issue #559: the door covers all 18 engine verbs), so
    there is no CLI-only-verb doctrine sentence left to require -- `test_the_cli_only_rule_
    itself_is_present` below is skipped rather than deleted, and
    `test_verb_still_documented` collects zero parametrizations, both of which reactivate
    the moment a verb regresses to CLI-only. `test_verb_never_routed_through_a_door_tool`
    stays live either way: it is a structural guard, not a doctrine-presence check, so
    running it against an empty `CLI_ONLY_VERBS` is simply honest -- no violation is
    possible."""

    @pytest.mark.skipif(
        not CLI_ONLY_VERBS,
        reason="CLI_ONLY_VERBS is empty -- no CLI-only-verb doctrine sentence is required "
               "while there is nothing CLI-only to document (issue #559: the door reaches "
               "all 18 engine verbs). Reactivates the moment CLI_ONLY_VERBS is non-empty.",
    )
    def test_the_cli_only_rule_itself_is_present(self):
        """The rule sentence, not just the words. FAILS IF: the `## MCP door`
        section stops saying these verbs have no door tool -- which is the
        instruction every other file's author is supposed to obey, and the only
        place it is written down."""
        section = _tier3_door_section()
        # The RULE, not the words: a sentence that says these verbs have no door
        # tool AND names at least three of the five it is about. "there is no
        # door tool missing, every verb has one" contains `no door tool` and is
        # the negation of this rule; it names none of the verbs.
        stated = [
            s for s in _sentences(section)
            if re.search(r"no door tool|CLI[- ]only", s, re.I)
            and sum(bool(_verb_name_re(v).search(s)) for v in CLI_ONLY_VERBS) >= 3
        ]
        assert stated, (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer states, in one "
            f"sentence, that these specific verbs have NO door tool. Without that sentence "
            f"there is no written authority for CLI_ONLY_VERBS, and an author has no way to "
            f"know that naming a door tool for {', '.join(CLI_ONLY_VERBS)} sends an agent to "
            f"something that does not exist."
        )

    @pytest.mark.parametrize("verb", CLI_ONLY_VERBS)
    def test_verb_still_documented(self, verb):
        """FAILS IF: the verb stops being named as a literal verb inside the
        `## MCP door` section. Deliberately NOT `verb in text`: 'skip' and
        'append' occur as ordinary English elsewhere in this file, so a bare
        whole-file substring check passes even after the entire section that
        documents them is deleted."""
        section = _tier3_door_section()
        assert _verb_token_re(verb).search(section), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer documents the "
            f"CLI-only verb `{verb}`. It must appear there in backticks, as a verb name -- "
            f"incidental prose using the same word elsewhere in the file is not "
            f"documentation of the verb."
        )

    def test_verb_never_routed_through_a_door_tool(self):
        """Same predicate the whole corpus is held to (`_cli_only_verb_violations`):
        unit-width and verb-name-scoped. There is NO exemption vocabulary -- the
        old `NO_DOOR_TOOL_FOR_IT` phrase list is deleted. The reference page may
        go on documenting the rule because the UNIT is narrow (line, then
        sentence), not because a phrase excuses it; a single sentence that names
        both is still flagged, which is what `ACCEPTED_FALSE_ALARM` pins."""
        violations = _cli_only_verb_violations(TIER3_PATH, _text(TIER3_PATH))
        assert not violations, (
            f"{TIER3_PATH} routes a CLI-only verb through a door tool -- no door tool "
            f"exists for it.\n" + "\n".join(violations)
        )


# --------------------------------------------------------------------------- #
# Tier 4 -- authoring templates that would otherwise propagate the CLI default to
# future skills. Same two-sided, paragraph-scoped shape as Tier 2.
# --------------------------------------------------------------------------- #

TIER4_TEMPLATE_FILES = [
    "skills/write-a-skill/templates/gated-engine-SKILL.template.md",
    "skills/write-a-skill/templates/survey-SKILL.template.md",
]


class TestTier4AuthoringTemplate:
    """Same inversion as Tier2, and this tier is where it compounds: these two files
    are what a NEW skill is authored from, so a CLI-fallback clause left here
    propagates the second path into every skill minted after it."""

    @pytest.mark.parametrize("path", TIER4_TEMPLATE_FILES)
    def test_door_path_paragraph_names_the_door_and_not_the_cli(self, path):
        para = _door_path_paragraph(path)
        assert DOOR_TOOL_RE.search(para)
        assert CLI_SCRIPT_MARKER not in para, (
            f"{path}'s drive-path paragraph names the door and then hands over "
            f"{CLI_SCRIPT_MARKER!r} beside it -- and this file is a template, so every "
            f"skill authored from it inherits that second path"
        )

    @pytest.mark.parametrize("path", TIER4_TEMPLATE_FILES)
    def test_file_never_names_the_cli_at_all(self, path):
        """Whole-file, and stricter than Tier2's equivalent on purpose: an authoring
        template has no scripts manifest and no reason to name the engine as a
        component at all, so the bare-mention allowance Tier2 needs does not apply
        here. A mention that survives in a template propagates into every skill
        minted from it."""
        assert CLI_SCRIPT_MARKER not in _text(path), (
            f"{path} mentions {CLI_SCRIPT_MARKER!r} -- issue #559 removed the second path "
            f"from the authoring templates so it stops propagating into new skills"
        )


# --------------------------------------------------------------------------- #
# Tier 5 -- DO NOT TOUCH. Both halves: the CLI artifact reference is retained
# (proves the file is intact) AND no door tool name was introduced anywhere.
# --------------------------------------------------------------------------- #

TIER5_UNTOUCHED_FILES = [
    "skills/_shared/global-everyone.md",
    "skills/admiral/references/fleet-doctrine.md",
]


class TestTier5DoNotTouch:
    """UNCHANGED BY ISSUE #559, deliberately. This tier asserts only that these two
    files still NAME `checklist_engine.py` as an artifact -- "the engine rail string
    table (`checklist_engine.py`, #140)", "nothing enforces the execution-time half in
    code -- `checklist_engine.py` does not". That is a bare prose mention of a component,
    not an instruction to run it: no path, no interpreter, no flag, no verb beside it.
    The sweep's own guard draws its line in exactly the same place and leaves these
    mentions alone (`tests/test_cli_retirement_guard.py`, `TestTheInvocationPredicateItself`,
    which pins both directions). Inverting this tier would therefore assert something
    the epic did not decide, and would go red on two files nothing swept."""

    @pytest.mark.parametrize("path", TIER5_UNTOUCHED_FILES)
    def test_still_names_checklist_engine_as_artifact(self, path):
        assert CLI_SCRIPT_MARKER in _text(path)

    @pytest.mark.parametrize("path", TIER5_UNTOUCHED_FILES)
    def test_no_door_tool_name_introduced(self, path):
        text = _text(path)
        found = DOOR_TOOL_RE.search(text)
        assert found is None, (
            f"{path} is Tier5 DO-NOT-TOUCH but now mentions door tool "
            f"{found.group(0) if found else ''!r}"
        )



class TestCLIOnlyVerbsAcrossEveryInstructionFile:
    """The same rule, applied where instructions actually live.

    `CLI_ONLY_VERBS` carried the comment "An instruction naming these must keep
    naming the CLI" and was then enforced against exactly ONE file, the reference
    page. That is how `skills/interrogator/SKILL.md` shipped naming the door as
    the default in the same sentence that orders `append` and `skip`, two verbs
    with no door tool, while this file reported 55/55 green.

    It was then enforced over a 13-file LIST, which is the same defect with a
    bigger number: both survey checklists, both plan templates and
    `skills/admiral/SKILL.md` were off it, and each accepted a planted violation
    at 91/91 green. It is now enforced over the WALK (`INSTRUCTION_FILES`), so a
    new instruction file is covered the day it lands.

    FAILS IF: any walked file names a CLI-only verb and a door tool in the SAME
    unit (line, then sentence). There is no exemption vocabulary -- a unit saying
    "the verb has no door tool" is flagged like any other, which is the accepted
    false alarm pinned in `ACCEPTED_FALSE_ALARM` and remedied by splitting the
    sentence. The pairing IS the defect: it is what makes a reader take the door
    tool as the route for that verb.

    `CLI_ONLY_VERBS` is empty today (issue #559: the door reaches all 18 engine
    verbs), so this guard currently finds nothing by construction -- that is
    honest, not vacuous: it stands ready to catch the day a verb regresses to
    CLI-only again, without anyone having to remember to re-add the check.
    """

    @pytest.mark.parametrize("path", INSTRUCTION_FILES)
    def test_no_instruction_pairs_a_cli_only_verb_with_a_door_tool(self, path):
        # One case per FILE, but every violation inside it is collected and
        # reported by field path and verb -- so a JSON template's 43 instruction
        # fields do not become 215 near-identical test ids, and a failure still
        # names exactly which field and which verb.
        violations = []
        for where, text in _instruction_texts(path):
            violations.extend(_cli_only_verb_violations(where, text))
        assert not violations, (
            f"{path} names a CLI-only verb in the same sentence as a door tool. There is "
            f"no door tool for {', '.join(CLI_ONLY_VERBS)} (authority: "
            f"mcp_spine_server.py's fallback table, restated in {TIER3_PATH}'s "
            f"{TIER3_SECTION_HEADING} section). Sending an agent to a tool that does not "
            f"exist is worse than the CLI instruction it would replace, so an instruction "
            f"naming one of these 5 verbs keeps naming the CLI, never a door tool.\n"
            + "\n".join(violations)
        )


# --------------------------------------------------------------------------- #
# The hard constraint itself: "The CLI door stays; F is additive."
# --------------------------------------------------------------------------- #

#: A denial standing in front of a word cancels it: "the door is NOT the
#: default" contains "default". Used by `_asserts_the_default`, which is a
#: positive check ("something here is called the default") and so wants a
#: generous denial set -- a false alarm there would flag correct prose.
ANY_DENIAL = re.compile(r"\b(?:nothing|never|not|n't|nor|neither|none|without)\b", re.I)


#: A prohibition standing in front of a name turns "here is the tool to call"
#: into "do not call it". A test that pins "this field names the door tool as
#: the default" by substring is satisfied by "never call spine_lease".
PROHIBITION = re.compile(
    r"\b(?:do not|don't|never|no longer|stop|avoid|must not|cannot)\b", re.I)


def _clauses(text: str) -> list[str]:
    """Clause-width: a sentence cut at `;`, `:` and dashes as well as at its end.

    A prohibition governs its own clause, not the whole sentence. Measured: both
    spine templates say "...so a resumed or duplicated parent CANNOT concurrently
    drive it: by default, call the spine_lease MCP tool...". Sentence-width reads
    the `cannot` -- which is about the duplicate parent, in the clause before the
    colon -- as forbidding the tool named after it.
    """
    return [c for c in re.split(r"(?<=[.!?;:])\s+|\s+[—–-]{1,2}\s+|\n", text) if c.strip()]


def _named_affirmatively(text: str, token: str) -> bool:
    """`token` appears in at least one clause that is not forbidding it."""
    for clause in _clauses(text):
        for match in re.finditer(re.escape(token), clause):
            if PROHIBITION.search(clause[:match.start()]) is None:
                return True
    return False


def _asserts_the_default(text: str) -> bool:
    """A sentence that calls something the default, with no denial in front of
    the word. "The door is NOT the default" contains "default"."""
    for sentence in _sentences(text):
        for match in re.finditer(r"\bdefault", sentence, re.I):
            if ANY_DENIAL.search(sentence[:match.start()]) is None:
                return True
    return False


class TestCLIStaysAvailableNotDeprecated:
    """**ISSUE #559 SUPERSEDED THE CONSTRAINT THIS CLASS DEFENDED, AND NARROWED IT TO
    ITS TRUE HALF.** "The CLI door stays; F is additive" was read here as a claim about
    the CORPUS: every drive-path paragraph had to go on telling an agent the CLI was
    available. The human ruling ended that reading -- "the agents should not know about
    the CLI. period." What survives is the claim about the TOOL: the engine was not
    deprecated, deleted or reduced. It is still there, still complete, and still what an
    operator or a debugging human runs. Only the instruction to run it left the corpus.

    Two assertions were deleted here, both corpus-side:
    `test_the_canonical_cli_sentence_is_present_verbatim` (a byte equality on
    "Nothing here removes or discourages the CLI." inside another lane's file) and
    `test_default_path_paragraph_states_the_cli_is_still_available` (which required the
    word "fallback", or "always/still available", in every Tier2 and Tier4 drive-path
    paragraph -- the exact clause the sweep removes). The single assertion below is what
    is left, and it is deliberately about the tool rather than about any prose.

    The account of the DELETED POLARITY PREDICATES that follows is kept verbatim,
    because it is the measured record two other files cite -- including
    `tests/test_cli_retirement_guard.py`, which names this class as the precedent for
    refusing to build a predicate that reads English.

    ----

    The Tier2/Tier4 availability check was `CLI_SCRIPT_MARKER in text` -- it
    only asked whether the CLI was MENTIONED, so it could not tell "the CLI is
    your fallback" from "the legacy CLI is DEPRECATED". Both mention it.

    **What replaced it, what it does not claim, and WHAT IT COST.** A pair of
    polarity predicates (`_retires_the_cli` / `_keeps_the_cli`) used to sit here,
    reading retirement words and cancelling them on a denial standing in front.
    They are deleted. They were also unexercised -- gutting `_retires_the_cli` to
    `return None` left the file at 282 passed, so the predicate could be replaced
    by a constant with the suite fully green.

    **Measured at TWO bars, because the bar is the whole argument.** The first
    pass measured only the adversarial one, and reported that tail as the
    distribution:

      ADVERSARIAL bar (crafted sentences, denial front-loaded)
        wrong 9/10 on retirements, 6/7 on affirmatives.
      DRIFT bar (plain deprecation appended to a skill body -- the failure this
      file argues is the real one, below)
        3/4 retirements CAUGHT. It was roughly right at its own bar.

    So the honest case for deleting it is NOT "the predicate was wrong". It was
    a coin-flip in both directions. The case is that **its errors are not
    symmetric across authors**: 5 of 6 planted honest affirmatives fired it --
    "the door is additive and removes nothing", "The door supersedes nothing",
    "Adopting the door replaces no CLI instruction". Every one of those is a
    sentence whose PURPOSE is that the CLI stays. An author strengthening the
    CLI-stays language was the author most likely to get a red suite, and a check
    that punishes the people doing the right thing is deleted by the next person
    who trips it -- after which there is no check at all.

    **What was given up, stated plainly:** the only corpus-wide guard on the
    epic's hard constraint, running over all 100 walked files, catching plain
    deprecation / legacy / supersede retirements. What is here instead is an
    equality on a byte string covering ONE sentence in ONE section of ONE file,
    plus the positive-presence checks that were already here. That is a real
    reduction in coverage and it is a deliberate trade, not an upgrade.

    **This catches an adoption pass that DROPS the CLI, not an author determined
    to retire it while keeping the words. The second property is a stated
    residual this suite does not enforce.**

    The reason that is sufficient is a threat-model distinction this file never
    stated. Every mutation that defeated the deleted predicates was an
    ADVERSARIALLY CRAFTED SENTENCE. That is the right bar for the identity pin
    in `tests/test_mcp_identity.py`, because `parse_args` supplies a mechanical
    oracle -- ask the parser and there is no spelling left to invent. **For prose
    there is no oracle, and the realistic failure is DRIFT**: an adoption pass
    rewrites an instruction to name the door and drops or softens the CLI
    sentence on the way past. **Drift removes things; it does not compose
    sentences that satisfy a checker while meaning the opposite.**
    Positive-presence catches removal. Negation-detection was the only part that
    needed to model an adversary, and the only part that cannot.
    """

    def test_the_engine_survives_as_a_tool_even_though_no_instruction_names_it(self):
        """The half of "the CLI door stays" that issue #559 did NOT overturn.

        The sweep removed an agent-facing PATH, not a program. If a later change
        reads the sweep as licence to delete or gut the engine, an operator, a
        debugging human and the door itself all lose their execution surface --
        the door does not reimplement the engine, it drives it.

        Read from the engine's own argparse registry rather than from a count
        written here, for the reason `_engine_verbs` exists: a hand-typed list
        drifts from what the program actually accepts, silently.
        """
        engine = ROOT / "scripts" / "checklist_engine.py"
        assert engine.is_file(), (
            f"{engine} is gone. Issue #559 removed the CLI as an AGENT-FACING path -- "
            f"'the agents should not know about the CLI. period.' -- and removed nothing "
            f"else. The engine is what the door drives and what an operator runs."
        )
        verbs = _engine_verbs()
        assert len(verbs) == 18, (
            f"the engine registers {len(verbs)} verbs, not the 18 the corpus sweep was "
            f"measured against: {sorted(verbs)}. The sweep took the CLI out of the "
            f"instruction text; it was not supposed to reduce what the engine can do."
        )
