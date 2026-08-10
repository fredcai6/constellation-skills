"""Adoption gate for the MCP door (issue #542 criterion 1, epic-418-followon g4a).

The door (`scripts/mcp_spine_server.py`, 7 tools over 13 of the engine's 18 verbs) was
built and merged completely unused: at the wave boundary, zero files under `skills/`
mentioned it. This test pins the pre-authored Tier 1-5 invariant chain from the g4a-implement
handoff -- the frozen list of files/fields that must now name a door tool as the DEFAULT
path while the CLI (`scripts/checklist_engine.py`) stays the documented fallback.

Every assertion in this file is TWO-SIDED: a door tool is named AND the CLI marker for
that same file/field is still present. A test that only checked "a door tool is named"
would also pass an edit that deleted the CLI -- see the g4a-implement-implementer-result.md
for the deliberate-deletion proof that this file's Tier1 assertions actually go RED when the
CLI half is removed.

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
   share every marker a substring check could look for. So propositions here are
   pinned with POLARITY (`_retires_the_cli`, `_keeps_the_cli`, `_asserts_the_default`,
   `_named_affirmatively`) and each assertion says, in its own docstring, what would
   have to be true for it to fail.

Audit of every assertion here against rule 2, including the ones deliberately left as
presence checks. Presence is enough ONLY where presence IS the fact, or where the
negation is caught by a polarity assertion elsewhere in the file:

  * PINS A PROPOSITION, POLARITY-CHECKED -- `test_field_names_door_tool_as_default`,
    `test_field_still_carries_cli_fallback`, `TestTier1CommanderCoreAttachLine`'s two,
    `_default_path_paragraph` (via `_asserts_the_default`),
    `test_names_door_tools_as_default`, `test_door_section_itself_keeps_the_cli`,
    `test_states_identity_trade_rule`, `test_the_cli_only_rule_itself_is_present`,
    `test_dispatched_crew_file_states_cli_for_own_plan`,
    `test_default_path_paragraph_states_the_cli_is_still_available`,
    `test_no_instruction_declares_the_cli_retired`.
  * PRESENCE IS THE FACT -- `test_spine_template_still_valid_json` (parses or does not),
    `test_verb_still_documented` (the verb name is in the section or it is not),
    `TestTier5DoNotTouch`'s two (a door tool name appears or it does not),
    `test_the_walk_finds_the_whole_corpus`.
  * PRESENCE, BACKSTOPPED -- `test_file_still_names_cli_at_all`,
    `test_still_names_cli_invocation`, `test_lease_section_carries_door_equivalent`.
    Each would pass text that names the CLI in order to retire it; each such text is
    red at `test_no_instruction_declares_the_cli_retired`, which runs over the whole
    walked corpus, these files included.
  * A NEGATIVE ALREADY -- `test_no_instruction_pairs_a_cli_only_verb_with_a_door_tool`
    and `test_verb_never_routed_through_a_door_tool` fail ON the violating text, so
    they have no negation to be satisfied by. Their risk is the opposite one (a false
    alarm on a correct statement of the rule), which `TestTheViolationPredicateItself`
    measures in both directions.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# The 7 door tools (scripts/mcp_spine_server.py TOOLS list). A door-tool mention is any of
# these bare names, or the fully-qualified `mcp__spine__<name>` form used to actually call one.
DOOR_TOOL_NAMES = (
    "spine_status",
    "spine_lease",
    "spine_start",
    "spine_advance",
    "spine_evidence",
    "spine_halt",
    "spine_survey_result",
)
DOOR_TOOL_RE = re.compile(r"\b(?:mcp__spine__)?(" + "|".join(DOOR_TOOL_NAMES) + r")\b")

# The 5 verbs with NO door tool -- authority is mcp_spine_server.py's own module docstring
# fallback table. An instruction naming these must keep naming the CLI; there is nothing
# else for it to reach for.
CLI_ONLY_VERBS = ("skip", "reopen", "append", "amend", "flag-candidate")

# The CLI marker used throughout the spine templates for "the engine, invoked as a command
# line" -- resolved to an absolute `python .../checklist_engine.py ...` invocation at
# instantiation time. Its literal presence in a field is what proves the CLI path was not
# deleted.
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


def _paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


#: Abbreviations whose full stop is NOT the end of a sentence. Without these,
#: `re.split(r"(?<=[.!?])\s+")` cuts "…through the door, e.g. `append` a check"
#: in half and drops the door tool out of the half that names the verb -- a
#: violation that reads as clean. Measured: `e.g.` alone accounted for one of
#: the five violating instructions the one-period splitter let through.
_ABBREVIATIONS = ("e.g.", "i.e.", "etc.", "vs.", "cf.", "approx.")


def _sentences(text: str) -> list[str]:
    """Sentence-width. Use this ONLY where sentence width is the point --
    polarity (a denial governs its own sentence, not the next one). For asking
    whether an instruction PAIRS two things, use `_units`: pairing crosses
    sentence boundaries and bullet-list items constantly, and a one-period
    window cannot see it."""
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


def _units(text: str) -> list[str]:
    """The width a reader actually takes together: a paragraph, a heading and
    its body, a bullet list WITH its lead-in.

    A sentence is the wrong unit for "does this instruction send an agent to a
    door tool for a CLI-only verb". Measured against the corpus, a one-period
    window missed 5 of 7 violating instructions -- the door tool in a list's
    lead-in with the verbs in the bullets, the tool in one sentence and the verb
    in the next, and a split on `e.g.` -- because the pairing is what a reader
    carries across the full stop, not something that has to fit inside one.
    """
    return _paragraphs(text)


#: How a CLI-only verb is written when it is being NAMED AS A VERB: in
#: backticks or quotes. Bare-word matching is what made this whole check
#: unusable -- "shrink or skip the frame", "visit all, append, never block"
#: and "append checks the context warrants" are ordinary English in three
#: different files, and flagging them trains people to delete the check. Same
#: convention `TestTier3CLIOnlyVerbsStayCLI` already documents.
def _verb_name_re(verb: str) -> re.Pattern:
    return re.compile(rf"[`'\"]{re.escape(verb)}[`'\"]")


#: Phrases that say, of the verb standing next to them, that it has no door
#: tool. A unit carrying one of these near the verb is DOCUMENTING the rule,
#: not violating it. Without this, the clearest correct statement of the rule --
#: "`spine_advance` closes a gate, but `skip` has no door tool and stays CLI" --
#: is RED, and a check that fails on the best statement of what it enforces gets
#: deleted by the next person to read it.
NO_DOOR_TOOL_FOR_IT = re.compile(
    r"no door tool|has no door|not covered by (?:a|any) (?:door )?tool|CLI[- ]only"
    r"|stays? CLI|stay CLI|remains? CLI|CLI fallback|via the CLI|through the CLI",
    re.I,
)

#: How far from the verb that exemption has to sit to be about THIS verb.
#: Wide enough for "`skip`, `reopen`, `append`, `amend`, `flag-candidate`" to
#: reach back to the "have no door tool" that introduces them.
EXEMPTION_WINDOW = 120


def _cli_only_verb_violations(where: str, text: str) -> list[str]:
    """Every place `text` routes a CLI-only verb through a door tool.

    A violation is: one unit, a door tool named in it, a CLI-only verb named as
    a verb in it, and nothing near that verb saying it has no door tool.
    """
    found = []
    for unit in _units(text):
        door = DOOR_TOOL_RE.search(unit)
        if not door:
            continue
        for verb in CLI_ONLY_VERBS:
            for match in _verb_name_re(verb).finditer(unit):
                lo = max(0, match.start() - EXEMPTION_WINDOW)
                hi = min(len(unit), match.end() + EXEMPTION_WINDOW)
                if NO_DOOR_TOOL_FOR_IT.search(unit[lo:hi]):
                    continue
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
#   * suffix not in {.md, .json} -- there is exactly one such file today
#     (`skills/workbench/scripts/checklist_engine.py`), and it is the engine
#     itself, not an instruction to an agent. Tests read it as code elsewhere.
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
    """A check is only worth what it can detect and what it leaves alone. Both
    measured here, in the assertion path, so a future edit to `_units`,
    `_verb_name_re` or `NO_DOOR_TOOL_FOR_IT` cannot quietly blind it.

    Against the one-period splitter this replaced: 5 of these 7 violating
    instructions passed, and 2 of the 3 innocent ones failed -- including the
    clearest correct statement of the rule, which is the sort of false alarm
    that gets a check deleted rather than fixed.
    """

    VIOLATING = {
        "one sentence":
            "Drive your survey through the door: call `spine_survey_result` to `append` "
            "new checks and to `skip` items an earlier answer settled.",
        "adjacent sentences":
            "Drive the survey through the door with `spine_survey_result`. Use `append` "
            "to add a check and `skip` to drop one.",
        "bullet list, tool in the lead-in":
            "Drive the survey through the door (`spine_survey_result`):\n"
            "- `append` a new check when the context warrants one.\n"
            "- `skip` an item an earlier answer settled.",
        "split on e.g.":
            "Route every survey move through `spine_survey_result`, e.g. `append` for a "
            "new check.",
        "heading and body":
            "### Surveys\nUse `spine_survey_result` for everything, including `append`.",
        "quoted rather than backticked":
            "Call `spine_survey_result` with action='append' to add a check.",
        "fully-qualified tool name":
            "Call `mcp__spine__spine_survey_result` to `skip` an item.",
    }

    INNOCENT = {
        "the clearest statement of the rule":
            "`spine_advance` closes a gate, but `skip` has no door tool and stays CLI.",
        "the rule across two sentences":
            "Call `spine_advance` to close a gate. `skip` has no door tool, so it stays "
            "CLI-only.",
        "the doctrine paragraph":
            "**5 verbs have no door tool at all, and stay CLI-only regardless of who is "
            "driving:** `skip`, `reopen`, `append`, `amend`, `flag-candidate`. Use "
            "`spine_advance` for the gates that do have one.",
    }

    @pytest.mark.parametrize("label", sorted(VIOLATING))
    def test_a_violating_instruction_is_caught(self, label):
        assert _cli_only_verb_violations("<case>", self.VIOLATING[label]), (
            f"the predicate did not catch {label!r} -- it routes a CLI-only verb through "
            f"a door tool, which is the whole defect this check exists for"
        )

    @pytest.mark.parametrize("label", sorted(INNOCENT))
    def test_an_innocent_instruction_is_left_alone(self, label):
        found = _cli_only_verb_violations("<case>", self.INNOCENT[label])
        assert not found, (
            f"the predicate flagged {label!r}, which is a CORRECT statement of the rule "
            f"it enforces. A check that fails on the best statement of its own rule gets "
            f"deleted by the next person to read it.\n" + "\n".join(found)
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
    # (path, field_path_keys, expected_door_tool_substring, expected_cli_substring)
    #
    # The CLI substring is the exact literal command line for THIS field's specific
    # action, not the bare '<engine>' placeholder -- some imperative fields (e.g.
    # COMMANDER_SPINE plan/archive) contain more than one engine verb in prose (a waive
    # alongside an attach/release), so a generic '<engine>' substring check is a vacuous
    # pass: it can be satisfied by an unrelated verb's CLI mention while the specific
    # line this edit targets is deleted. Pinning the exact command line is what makes the
    # two-sided proof (a deliberate deletion of THIS line) actually go RED.
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
    """Each of these 7 imperative fields must name a door tool as the default, by JSON
    field path, AND still carry that SAME action's exact CLI command line (two-sided)."""

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
    def test_field_still_carries_cli_fallback(self, path, keys, door_substr, cli_substr):
        """Same standard on the CLI half: "do not run `<engine> claim ...`"
        carries the command line and retires it in the same breath."""
        data = _load(path)
        field = _field(data, *keys)
        assert _named_affirmatively(field, cli_substr), (
            f"{path} .{'.'.join(keys)} lost its exact CLI command line {cli_substr!r} -- "
            f"the CLI door must stay, never be removed or discouraged, and a generic "
            f"'{CLI_PLACEHOLDER}' substring elsewhere in the field is not sufficient "
            f"proof this specific action's fallback survived"
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
    """commander-core.md:127's delegated-mode `attach` command line: text-based (this file
    is markdown, no JSON field path exists), both halves required in the SAME paragraph."""

    PATH = "skills/commander/references/commander-core.md"

    def _attach_paragraph(self) -> str:
        text = _text(self.PATH)
        for para in _paragraphs(text):
            if "user-decision` checkpoints" in para and f"{CLI_PLACEHOLDER} attach" in para:
                return para
        raise AssertionError(
            f"{self.PATH} has no paragraph containing both the checkpoint prose and "
            f"'{CLI_PLACEHOLDER} attach' -- has the CLI line moved or been deleted?"
        )

    def test_paragraph_names_door_tool(self):
        """Affirmatively: "never call spine_evidence here" names it and is the
        negation of what this pins."""
        para = self._attach_paragraph()
        assert _named_affirmatively(para, "spine_evidence"), (
            f"{self.PATH}'s delegated-mode attach paragraph does not name spine_evidence "
            f"as the door default (it must appear in a clause that is not forbidding it)"
        )

    def test_paragraph_still_carries_cli_fallback(self):
        para = self._attach_paragraph()
        assert _named_affirmatively(para, f"{CLI_PLACEHOLDER} attach")


# --------------------------------------------------------------------------- #
# Tier 2 -- default-path prose in SKILL bodies. Text-based, paragraph-scoped so a
# door-tool mention anywhere in the file cannot satisfy this on its own: the SAME
# paragraph must also still carry the checklist_engine.py CLI marker.
# --------------------------------------------------------------------------- #

TIER2_SKILL_FILES = [
    "skills/workbench/SKILL.md",
    "skills/charter/SKILL.md",
    "skills/reviewer/SKILL.md",
    "skills/interrogator/SKILL.md",
    "skills/implementer/SKILL.md",
    "skills/explorer/SKILL.md",
]

CLI_SCRIPT_MARKER = "checklist_engine.py"


def _default_path_paragraph(path: str) -> str:
    text = _text(path)
    for para in _paragraphs(text):
        if CLI_SCRIPT_MARKER in para and DOOR_TOOL_RE.search(para) and _asserts_the_default(para):
            return para
    raise AssertionError(
        f"{path} has no single paragraph naming a door tool as the DEFAULT path while "
        f"also still carrying the {CLI_SCRIPT_MARKER!r} CLI fallback"
    )


class TestTier2SkillBodyDefaultPath:
    @pytest.mark.parametrize("path", TIER2_SKILL_FILES)
    def test_default_path_paragraph_is_two_sided(self, path):
        # Raises AssertionError (via _default_path_paragraph) if no such paragraph exists.
        para = _default_path_paragraph(path)
        assert DOOR_TOOL_RE.search(para)
        assert CLI_SCRIPT_MARKER in para

    @pytest.mark.parametrize("path", TIER2_SKILL_FILES)
    def test_file_still_names_cli_at_all(self, path):
        assert CLI_SCRIPT_MARKER in _text(path)


class TestTier2IdentityTradeCarried:
    """The g1 fact ('an in-session dispatched crew member cannot drive its own plan
    through the door') must be carried in the instructions themselves, not merely cited."""

    @pytest.mark.parametrize("path", [
        "skills/implementer/SKILL.md",
        "skills/reviewer/SKILL.md",
    ])
    def test_dispatched_crew_file_states_cli_for_own_plan(self, path):
        """FAILS IF: the file stops routing a dispatched crew member's OWN plan
        to the CLI.

        The three substring checks this replaced -- `in-session`, "shares the
        parent", "parent's MCP scope" -- are all supplied by the negation ("an
        in-session subagent no longer shares the parent's MCP scope, so use the
        door for your own plan"). The routing sentence is not."""
        text = _text(path)
        routed = [
            s for s in _sentences(text)
            if re.search(r"in-session", s, re.I)
            and re.search(r"\bown\b", s, re.I)
            and (CLI_SCRIPT_MARKER in s or re.search(r"\bthe CLI\b", s, re.I)
                 or CLI_PLACEHOLDER in s)
        ]
        assert routed, (
            f"{path} no longer says, in one sentence, that an in-session dispatched crew "
            f"member drives its OWN plan through the CLI. That is the g1 identity-trade "
            f"fact, and it has to be carried in the instruction itself, not merely cited."
        )
        assert "shares the parent" in text or "shares its parent" in text or "parent's MCP scope" in text, (
            f"{path} does not explain WHY a dispatched crew member uses the CLI for its "
            f"own plan (shared MCP scope with the dispatching parent)"
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
    """All section-scoped. FAILS IF: the `## MCP door` section is deleted,
    emptied, or loses any of the four things it is the sole authority for --
    the 7 tool names, the default rule, the identity trade, and the CLI's
    survival. Prose elsewhere in the file cannot satisfy any of these."""

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

    def test_still_names_cli_invocation(self):
        # Whole-file: the CLI reference page must document the CLI, obviously.
        assert CLI_SCRIPT_MARKER in _text(TIER3_PATH)

    def test_door_section_itself_keeps_the_cli(self):
        """The section that makes the door the default must, in the same breath,
        keep the CLI.

        This assertion used to read `re.search("remove[sd]?|discourag\\w*", section)
        and re.search("\\bCLI\\b", section)` -- a retirement word somewhere, and
        the word CLI somewhere, joined by `and`. **A sentence that retires the
        CLI supplies both words itself.** Measured:

            'The CLI door stays; nothing removes it.'                 passed  (true form)
            'The CLI is removed. Everything goes through the door.'   passed  (NEGATION)
            'This section discourages the CLI; use the door.'         passed  (NEGATION)
            the sentence simply DELETED                               caught

        Replacing the real doctrine line with "The CLI is removed. Every verb
        now goes through the door; nothing here discourages that." left the
        whole file at 91 passed -- the section stated the opposite of the epic's
        hard constraint and the assertion pinning it was GREENER, because the
        retiring sentence supplied both required words.

        So the proposition is now pinned in both directions, per sentence:
          (A) no sentence in the section retires the CLI, and
          (B) at least one sentence in it keeps the CLI.
        (A) alone would pass on deletion; (B) alone would pass on a section that
        both keeps and retires it. Neither can be satisfied by the other's
        negation.
        """
        section = _tier3_door_section()
        assert CLI_SCRIPT_MARKER in section, (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section makes the door the default "
            f"without naming the {CLI_SCRIPT_MARKER} CLI at all"
        )

        retirements = [s.strip()[:200] for s in _sentences(section) if _retires_the_cli(s)]
        assert not retirements, (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section now RETIRES the CLI. 'The CLI "
            f"door stays; F is additive' is the epic's hard constraint, and this section is "
            f"where an agent reads it.\n  " + "\n  ".join(retirements)
        )

        keeps = [s.strip()[:200] for s in _sentences(section) if _keeps_the_cli(s)]
        assert keeps, (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer STATES that the CLI "
            f"stays. It must carry a sentence that names the CLI and either calls it "
            f"available or denies its retirement outright ('Nothing here removes or "
            f"discourages the CLI'). Mentioning the CLI is not enough -- an instruction can "
            f"name it precisely in order to retire it."
        )

    def test_states_identity_trade_rule(self):
        """FAILS IF: the dispatched-subagent explanation is deleted. That
        explanation is the whole reason a dispatched Implementer/Reviewer must
        not call a door tool for its own plan, and it exists nowhere else in
        this file."""
        section = _tier3_door_section()
        # The three word-presence checks this used to make -- `in-session|dispatch`,
        # `MCP scope`, `own spine|own plan` -- are ALL supplied by the negation:
        # "A dispatched subagent MAY drive its own plan through the door; MCP
        # scope is per-subagent." So the rule is pinned as a single sentence that
        # sends a dispatched subagent TO THE CLI for its own plan, which the
        # negation cannot write.
        routed = [
            s for s in _sentences(section)
            if re.search(r"in-session|dispatch\w*", s, re.I)
            and re.search(r"own\b", s, re.I)
            and (CLI_SCRIPT_MARKER in s or re.search(r"\bthe CLI\b", s, re.I))
        ]
        assert routed, (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer says, in one "
            f"sentence, that a dispatched subagent drives its OWN plan through the CLI. "
            f"That sentence is the whole reason a dispatched Implementer/Reviewer must not "
            f"call a door tool for its own plan, and it exists nowhere else in this file."
        )
        assert re.search(r"MCP scope", section, re.I), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer explains WHY "
            f"(a Task subagent inherits its dispatcher's MCP scope, so the tools stay "
            f"bound to the DISPATCHER's spine)"
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
    """Close criterion 3: the 5 CLI-only verbs have NO door tool. The `## MCP door`
    section must keep documenting them as CLI-only, and must never attribute a door
    tool to them (no door tool name in the same sentence as the verb)."""

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
        unit-width, verb-name-scoped, and exempting a unit that says the verb has
        no door tool -- so the reference page may go on DOCUMENTING the rule."""
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
    @pytest.mark.parametrize("path", TIER4_TEMPLATE_FILES)
    def test_default_path_paragraph_is_two_sided(self, path):
        para = _default_path_paragraph(path)
        assert DOOR_TOOL_RE.search(para)
        assert CLI_SCRIPT_MARKER in para

    @pytest.mark.parametrize("path", TIER4_TEMPLATE_FILES)
    def test_file_still_names_cli_at_all(self, path):
        assert CLI_SCRIPT_MARKER in _text(path)


# --------------------------------------------------------------------------- #
# Tier 5 -- DO NOT TOUCH. Both halves: the CLI artifact reference is retained
# (proves the file is intact) AND no door tool name was introduced anywhere.
# --------------------------------------------------------------------------- #

TIER5_UNTOUCHED_FILES = [
    "skills/_shared/global-everyone.md",
    "skills/admiral/references/fleet-doctrine.md",
]


class TestTier5DoNotTouch:
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

    FAILS IF: any walked file routes a CLI-only verb through a door tool -- the
    two named together in one unit, with nothing beside the verb saying it has
    no door tool. The pairing IS the defect: it is what makes a reader take the
    door tool as the route for that verb.
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

#: Words that, said ABOUT the CLI, retire it.
#:
#: This list used to be kept short by EXCLUDING every word that also occurs in
#: the affirmative sentence -- `removed`, `discourages`, `no longer`,
#: `superseded` -- on the reasoning that a marker with a legitimate use is a
#: false alarm. That reasoning is backwards, and it is what let the negation in:
#: the affirmative and the retirement SHARE vocabulary ("Nothing here removes or
#: discourages the CLI" vs "The CLI is removed"), so excluding the shared words
#: excludes the retirement too. Measured, per sentence, over today's corpus:
#: `superseded` 0 collisions, `no longer` 0, `discourages` 1, `removed` 1 -- and
#: both collisions are the SAME sentence, the affirmative one.
#:
#: So the words are all in, and what keeps the affirmative sentence green is
#: POLARITY (`_retires_the_cli`), not omission. Measured after the change: 0
#: false alarms across all 100 walked files, 3 sentences correctly read as
#: denying a retirement.
CLI_RETIREMENT_MARKERS = re.compile(
    r"\bdeprecat\w*|\blegacy\b|\bobsolete\b|\bphased out\b|\bno longer\b"
    r"|\bstop using\b|\b(?:do not|don't|never) use the CLI\b"
    r"|\bremov\w*|\bdiscourag\w*|\bsupersed\w*|\bretir\w*|\breplac\w*",
    re.I,
)

#: A denial standing in front of a retirement word cancels it: "Nothing here
#: REMOVES the CLI" is the opposite of "the CLI is REMOVED", and the only thing
#: separating them in the text is this.
#:
#: Two sets, deliberately, because the two directions want opposite errors:
#:
#:   * ANY_DENIAL is used to decide "is this a violation?" -- generous, so an
#:     innocent sentence is not flagged. A false alarm here gets the assertion
#:     deleted.
#:   * EMPHATIC_DENIAL is used to decide "does this sentence KEEP the CLI?" --
#:     narrow, so a sentence that merely happens to contain "not" somewhere
#:     cannot stand in for the doctrine sentence. Without that narrowing,
#:     "Sending an agent to a tool that does NOT exist is worse than the CLI
#:     instruction it would REPLACE" would count as the affirmative, and
#:     deleting the real one would go unnoticed.
ANY_DENIAL = re.compile(r"\b(?:nothing|never|not|n't|nor|neither|none|without)\b", re.I)
EMPHATIC_DENIAL = re.compile(r"\b(?:nothing|never|neither|nor|none)\b", re.I)

#: Naming the CLI: the script, the spine templates' `<engine>` placeholder, or
#: the bare phrase.
CLI_MENTION = re.compile(rf"{re.escape(CLI_SCRIPT_MARKER)}|{re.escape(CLI_PLACEHOLDER)}|\bthe CLI\b", re.I)

#: What "the CLI is still there" reads like when it is genuinely still there.
CLI_AVAILABILITY = re.compile(r"\bfallback\b|\balways available\b|\bstill available\b|\bremains available\b", re.I)


def _retires_the_cli(sentence: str) -> re.Match | None:
    """Does this sentence say the CLI is going away?

    It names the CLI, it uses a retirement word, and NO denial stands in front
    of that word to cancel it. That last clause is the whole point: word
    presence cannot distinguish a proposition from its negation, because the
    negation is written with the same words.
    """
    if not CLI_MENTION.search(sentence):
        return None
    for match in CLI_RETIREMENT_MARKERS.finditer(sentence):
        if ANY_DENIAL.search(sentence[:match.start()]) is None:
            return match
    return None


def _keeps_the_cli(sentence: str) -> bool:
    """Does this sentence say the CLI STAYS?

    Two forms count, and nothing else does:
      * it names the CLI and calls it available ("the fallback", "always
        available"); or
      * it names the CLI and emphatically DENIES a retirement ("Nothing here
        removes or discourages the CLI").

    Naming the CLI is not enough. An instruction can name it precisely in order
    to retire it -- that is exactly how "The CLI is removed. Everything goes
    through the door." satisfied an assertion built to pin the opposite.
    """
    if not CLI_MENTION.search(sentence):
        return False
    if CLI_AVAILABILITY.search(sentence) and _retires_the_cli(sentence) is None:
        return True
    return any(EMPHATIC_DENIAL.search(sentence[:m.start()])
               for m in CLI_RETIREMENT_MARKERS.finditer(sentence))


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
    """The Tier2/Tier4 availability check was `CLI_SCRIPT_MARKER in text` -- it
    only asked whether the CLI was MENTIONED, so it could not tell "the CLI is
    your fallback" from "the legacy CLI is DEPRECATED". Both mention it. The
    second is a violation of the epic's hard constraint and passed anyway.

    Two assertions, because mentioning and endorsing are different facts.
    """

    @pytest.mark.parametrize("path", TIER2_SKILL_FILES + TIER4_TEMPLATE_FILES)
    def test_default_path_paragraph_states_the_cli_is_still_available(self, path):
        """FAILS IF: the paragraph that makes the door the default stops
        describing the CLI as available -- as the fallback, or as always/still
        available. Naming the script is not enough: an instruction can name it
        precisely in order to retire it.

        Polarity-checked, not word-checked: "the CLI is no longer the fallback"
        contains `fallback` and would have passed the bare availability regex.
        `_keeps_the_cli` requires the availability phrase to sit in a sentence
        that is not itself retiring the CLI."""
        para = _default_path_paragraph(path)
        assert any(_keeps_the_cli(s) for s in _sentences(para)), (
            f"{path}'s default-path paragraph names the door as the default and names "
            f"{CLI_SCRIPT_MARKER}, but no longer says the CLI is still available. "
            f"'The CLI door stays; F is additive' is the epic's hard constraint -- a "
            f"paragraph that mentions the CLI without keeping it is how that constraint "
            f"gets lost while every mention-based check stays green.\n"
            f"Paragraph: {para.strip()[:400]}"
        )

    @pytest.mark.parametrize("path", INSTRUCTION_FILES)
    def test_no_instruction_declares_the_cli_retired(self, path):
        """FAILS IF: any instruction sentence in the WALKED corpus names the CLI
        and says it is going away -- deprecated, legacy, obsolete, phased out,
        no longer, removed, discouraged, superseded, retired, replaced -- with
        no denial in front of the word to cancel it."""
        violations = []
        for where, text in _instruction_texts(path):
            for sentence in _sentences(text):
                found = _retires_the_cli(sentence)
                if found:
                    violations.append(
                        f"  {where}: {found.group(0)!r}\n    {sentence.strip()[:300]}"
                    )
        assert not violations, (
            f"{path} describes the CLI as retired. The CLI door STAYS -- workstream F is "
            f"additive, and the door is a fast path for the agent that owns the bound "
            f"spine, never a replacement. A dispatched crew member driving its own plan "
            f"has no door at all, and the CLI is its only route.\n" + "\n".join(violations)
        )
