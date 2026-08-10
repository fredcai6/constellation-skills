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


class TestTier3ChecklistEngineReference:
    def test_names_door_tools_as_default(self):
        text = _text(TIER3_PATH)
        for name in DOOR_TOOL_NAMES:
            assert name in text, f"{TIER3_PATH} never names door tool {name}"
        assert re.search(r"default", text, re.I)

    def test_still_names_cli_invocation(self):
        text = _text(TIER3_PATH)
        assert CLI_SCRIPT_MARKER in text

    def test_states_identity_trade_rule(self):
        text = _text(TIER3_PATH)
        assert re.search(r"in-session", text, re.I)
        assert re.search(r"own spine|its own process|bound spine", text, re.I)

    def test_lease_section_carries_door_equivalent(self):
        text = _text(TIER3_PATH)
        # Session lease section: the CLI claim/heartbeat/release block must still be there,
        # AND a door equivalent (spine_lease) must be named near it.
        idx = text.find("## Session lease")
        assert idx != -1, "Session lease section missing"
        section = text[idx: idx + 2000]
        assert "claim" in section and "heartbeat" in section and "release" in section
        assert "spine_lease" in section


class TestTier3CLIOnlyVerbsStayCLI:
    """Close criterion 3: the 5 CLI-only verbs have NO door tool. checklist-engine.md must
    keep documenting them as CLI, and must never attribute a door tool to them (no door
    tool name in the same sentence as the verb)."""

    def _sentences(self) -> list[str]:
        text = _text(TIER3_PATH)
        return re.split(r"(?<=[.!?])\s+", text)

    @pytest.mark.parametrize("verb", CLI_ONLY_VERBS)
    def test_verb_still_documented(self, verb):
        assert verb in _text(TIER3_PATH), f"{TIER3_PATH} no longer documents {verb!r}"

    @pytest.mark.parametrize("verb", CLI_ONLY_VERBS)
    def test_verb_never_paired_with_a_door_tool_in_the_same_sentence(self, verb):
        for sentence in self._sentences():
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
