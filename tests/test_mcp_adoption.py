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


def _sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", text)


# --------------------------------------------------------------------------- #
# Every file that carries an INSTRUCTION an agent acts on. `CLI_ONLY_VERBS` is a
# statement about instructions, not about one reference page, so it is enforced
# over all of them -- see TestCLIOnlyVerbsAcrossEveryInstructionFile.
#
# The markdown list is Tier1's commander-core + all six Tier2 skill bodies +
# Tier3's engine reference + both Tier4 authoring templates. Tier5 is
# deliberately absent: those files must name NO door tool at all, which
# TestTier5DoNotTouch already enforces more strictly than this could.
# --------------------------------------------------------------------------- #
INSTRUCTION_MARKDOWN_FILES = [
    "skills/commander/references/commander-core.md",
    "skills/workbench/SKILL.md",
    "skills/charter/SKILL.md",
    "skills/reviewer/SKILL.md",
    "skills/interrogator/SKILL.md",
    "skills/implementer/SKILL.md",
    "skills/explorer/SKILL.md",
    "skills/workbench/references/checklist-engine.md",
    "skills/write-a-skill/templates/gated-engine-SKILL.template.md",
    "skills/write-a-skill/templates/survey-SKILL.template.md",
]

INSTRUCTION_JSON_FILES = [
    "skills/commander/templates/COMMANDER_SPINE.template.json",
    "skills/admiral/templates/ADMIRAL_SPINE.template.json",
    "skills/explorer/templates/EXPLORER_SPINE.template.json",
]


def _instruction_texts(path: str) -> list[tuple[str, str]]:
    """(where, text) pairs of everything in `path` that instructs an agent.

    Markdown: the whole file, one chunk.

    JSON spine templates: the instruction-bearing fields of every task, by field
    path -- the `imperative` (what the agent is told to do), its `directives`,
    its `constraints`, and every pre/postcondition `statement` (what the agent
    is told to make true). Bookkeeping strings (`id`, `title`, `status`) are
    excluded: they are labels, they cannot contain an instruction, and
    parametrizing over them would bury the real cases in noise.
    """
    if not path.endswith(".json"):
        return [(path, _text(path))]

    data = _load(path)
    out: list[tuple[str, str]] = []
    for task_id, task in (data.get("tasks") or {}).items():
        if not isinstance(task, dict):
            continue
        for key in ("imperative", "directives"):
            value = task.get(key)
            if isinstance(value, str) and value.strip():
                out.append((f"{path}:{task_id}.{key}", value))
        for idx, value in enumerate(task.get("constraints") or []):
            if isinstance(value, str) and value.strip():
                out.append((f"{path}:{task_id}.constraints[{idx}]", value))
        for which in ("preconditions", "postconditions"):
            for cond in task.get(which) or []:
                if isinstance(cond, dict) and isinstance(cond.get("statement"), str):
                    out.append((f"{path}:{task_id}.{which}.{cond.get('id')}", cond["statement"]))
    return out


def _all_instruction_texts() -> list[tuple[str, str]]:
    out = []
    for path in INSTRUCTION_MARKDOWN_FILES + INSTRUCTION_JSON_FILES:
        out.extend(_instruction_texts(path))
    return out


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
        data = _load(path)
        field = _field(data, *keys)
        assert door_substr in field, (
            f"{path} .{'.'.join(keys)} does not name the door tool {door_substr!r} "
            f"as a default path"
        )

    @pytest.mark.parametrize("path,keys,door_substr,cli_substr", TIER1_JSON_FIELDS)
    def test_field_still_carries_cli_fallback(self, path, keys, door_substr, cli_substr):
        data = _load(path)
        field = _field(data, *keys)
        assert cli_substr in field, (
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
        para = self._attach_paragraph()
        assert "spine_evidence" in para, (
            f"{self.PATH}'s delegated-mode attach paragraph does not name spine_evidence "
            f"as the door default"
        )

    def test_paragraph_still_carries_cli_fallback(self):
        para = self._attach_paragraph()
        assert f"{CLI_PLACEHOLDER} attach" in para


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
        if CLI_SCRIPT_MARKER in para and DOOR_TOOL_RE.search(para) and re.search(r"default", para, re.I):
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
        text = _text(path)
        assert re.search(r"in-session", text, re.I), (
            f"{path} does not state the in-session dispatch identity-trade fact"
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
        assert re.search(r"default", section, re.I), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer states the door "
            f"is the default path"
        )

    def test_still_names_cli_invocation(self):
        # Whole-file: the CLI reference page must document the CLI, obviously.
        assert CLI_SCRIPT_MARKER in _text(TIER3_PATH)

    def test_door_section_itself_keeps_the_cli(self):
        """The section that makes the door the default must, in the same breath,
        keep the CLI. FAILS IF: the section stops naming checklist_engine.py, or
        stops saying the CLI is not being removed/discouraged."""
        section = _tier3_door_section()
        assert CLI_SCRIPT_MARKER in section, (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section makes the door the default "
            f"without naming the {CLI_SCRIPT_MARKER} CLI at all"
        )
        assert re.search(r"remove[sd]?|discourag\w*", section, re.I) and re.search(
            r"\bCLI\b", section
        ), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section lost its statement that "
            f"nothing here removes or discourages the CLI -- that sentence is the epic's "
            f"hard constraint ('the CLI door stays; F is additive') written where an agent "
            f"actually reads it"
        )

    def test_states_identity_trade_rule(self):
        """FAILS IF: the dispatched-subagent explanation is deleted. That
        explanation is the whole reason a dispatched Implementer/Reviewer must
        not call a door tool for its own plan, and it exists nowhere else in
        this file."""
        section = _tier3_door_section()
        assert re.search(r"in-session|dispatch\w*", section, re.I), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer explains what a "
            f"dispatched subagent must do"
        )
        assert re.search(r"MCP scope", section, re.I), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer explains WHY "
            f"(a Task subagent inherits its dispatcher's MCP scope, so the tools stay "
            f"bound to the DISPATCHER's spine)"
        )
        assert re.search(r"own spine|its own process|bound spine|own plan", section, re.I)

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
        assert re.search(r"no door tool", section, re.I), (
            f"{TIER3_PATH}'s {TIER3_SECTION_HEADING} section no longer states that some "
            f"verbs have NO door tool. Without that sentence there is no written authority "
            f"for CLI_ONLY_VERBS, and an author has no way to know that naming a door tool "
            f"for {', '.join(CLI_ONLY_VERBS)} sends an agent to something that does not exist."
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

    @pytest.mark.parametrize("verb", CLI_ONLY_VERBS)
    def test_verb_never_paired_with_a_door_tool_in_the_same_sentence(self, verb):
        for sentence in _sentences(_text(TIER3_PATH)):
            if re.search(rf"[`'\"]?{re.escape(verb)}[`'\"]?", sentence):
                found = DOOR_TOOL_RE.search(sentence)
                assert not found, (
                    f"{TIER3_PATH} pairs CLI-only verb {verb!r} with door tool "
                    f"{found.group(0) if found else ''!r} in the same sentence -- "
                    f"no door tool exists for this verb"
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
    page. Every instruction an agent actually acts on lives somewhere else -- the
    six skill bodies, commander-core, the two authoring templates, the three
    spine templates -- and none of them were covered. That is how
    `skills/interrogator/SKILL.md` shipped naming the door as the default in the
    same sentence that orders `append` and `skip`, two verbs with no door tool,
    while this file reported 55/55 green.

    FAILS IF: any of those files puts a CLI-only verb in the same sentence as a
    door tool name. The pairing IS the defect: it is what makes a reader take
    the door tool as the route for that verb.
    """

    @pytest.mark.parametrize("path", INSTRUCTION_MARKDOWN_FILES + INSTRUCTION_JSON_FILES)
    def test_no_instruction_pairs_a_cli_only_verb_with_a_door_tool(self, path):
        # One case per FILE, but every violation inside it is collected and
        # reported by field path and verb -- so a JSON template's 43 instruction
        # fields do not become 215 near-identical test ids, and a failure still
        # names exactly which field and which verb.
        violations = []
        for where, text in _instruction_texts(path):
            for sentence in _sentences(text):
                found = DOOR_TOOL_RE.search(sentence)
                if not found:
                    continue
                for verb in CLI_ONLY_VERBS:
                    if re.search(rf"[`'\"]?{re.escape(verb)}[`'\"]?", sentence):
                        violations.append(
                            f"  {where}: verb {verb!r} + door tool {found.group(0)!r}\n"
                            f"    {sentence.strip()[:300]}"
                        )
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

#: Words that, said ABOUT the CLI, retire it. Every one of these was checked
#: against the corpus and occurs zero times today, so a match is a real change
#: of stance, not a coincidence of vocabulary.
#:
#: Deliberately NOT included, because they have legitimate unrelated uses here:
#: `superseded` (the engine's own evidence state after a `reopen` cascade),
#: `discourages` (only ever in the affirmative sentence "Nothing here removes or
#: discourages the CLI"), `no longer` (used throughout to describe fixed bugs),
#: `removed` (used about gates and evidence). Widening this list means
#: re-running that check; a marker with a legitimate use is a false alarm, and a
#: false alarm here trains people to delete the assertion.
CLI_RETIREMENT_MARKERS = re.compile(
    r"\bdeprecat\w*|\blegacy\b|\bobsolete\b|\bphased out\b|\bno longer supported\b"
    r"|\bstop using\b|\b(?:do not|don't|never) use the CLI\b",
    re.I,
)

#: Naming the CLI: the script, the spine templates' `<engine>` placeholder, or
#: the bare phrase.
CLI_MENTION = re.compile(rf"{re.escape(CLI_SCRIPT_MARKER)}|{re.escape(CLI_PLACEHOLDER)}|\bthe CLI\b", re.I)

#: What "the CLI is still there" reads like when it is genuinely still there.
CLI_AVAILABILITY = re.compile(r"\bfallback\b|\balways available\b|\bstill available\b|\bremains available\b", re.I)


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
        precisely in order to retire it."""
        para = _default_path_paragraph(path)
        assert CLI_AVAILABILITY.search(para), (
            f"{path}'s default-path paragraph names the door as the default and names "
            f"{CLI_SCRIPT_MARKER}, but no longer says the CLI is still available. "
            f"'The CLI door stays; F is additive' is the epic's hard constraint -- a "
            f"paragraph that mentions the CLI without keeping it is how that constraint "
            f"gets lost while every mention-based check stays green.\n"
            f"Paragraph: {para.strip()[:400]}"
        )

    @pytest.mark.parametrize("path", INSTRUCTION_MARKDOWN_FILES + INSTRUCTION_JSON_FILES)
    def test_no_instruction_declares_the_cli_retired(self, path):
        """FAILS IF: any instruction sentence names the CLI and calls it
        deprecated, legacy, obsolete, phased out or no longer supported, or
        tells the agent to stop using it."""
        violations = []
        for where, text in _instruction_texts(path):
            for sentence in _sentences(text):
                if not CLI_MENTION.search(sentence):
                    continue
                found = CLI_RETIREMENT_MARKERS.search(sentence)
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
