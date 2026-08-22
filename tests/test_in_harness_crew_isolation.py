"""#632: an in-harness subagent shares its dispatcher's harness session id, so
the checklist engine's MCP door resolves to the DISPATCHER's spine. The guard is
a declared tool exclusion on a checked-in agent definition, plus the doctrine
that tells a dispatcher to use it.

This is a lint over the guard's two halves. It cannot prove the harness enforces
the exclusion -- that was measured once, live: a fresh session registers the type
and the dispatched subagent reports no `mcp__spine__*` tool and no `ToolSearch`
with which to recover one. What it CAN do is stop the guard from silently
rotting: an agent definition that quietly regains the door, or doctrine that
stops naming the type, both pass every other test in this suite.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_DEF = ROOT / ".claude" / "agents" / "constellation-crew.md"
DOCTRINE = ROOT / "skills" / "commander" / "references" / "crew-dispatch.md"


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not key.startswith(" "):
            fields[key.strip()] = value.strip()
    return fields


class CrewAgentDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            AGENT_DEF.exists(),
            f"{AGENT_DEF.relative_to(ROOT)} is missing -- the declared exclusion "
            "IS the guard; without the file, every in-harness dispatch is back to "
            "a hand-written prose warning",
        )
        self.text = AGENT_DEF.read_text(encoding="utf-8")
        self.fm = frontmatter(self.text)

    def test_it_declares_an_explicit_tool_allowlist(self):
        """An absent `tools:` means the subagent inherits EVERY tool, door
        included. The exclusion only exists because the list is explicit."""
        self.assertIn("tools", self.fm,
                      "no `tools:` in the frontmatter -- an agent definition "
                      "without one inherits all tools, including the door")
        self.assertTrue(self.fm["tools"].strip(),
                        "`tools:` is empty; it must name the allowed tools")

    def test_the_allowlist_names_no_spine_door_tool(self):
        tools = [t.strip() for t in self.fm.get("tools", "").split(",")]
        leaked = [t for t in tools if t.startswith("mcp__spine__") or t == "*"]
        self.assertEqual(
            leaked, [],
            f"the crew allowlist grants door access via {leaked!r} -- an "
            "in-harness subagent shares its dispatcher's harness session id, so "
            "this drives the DISPATCHER's spine (#632, lane H)",
        )

    def test_the_definition_says_why_the_door_is_absent(self):
        """A bare allowlist reads as an arbitrary restriction and invites someone
        to widen it. The reason has to travel with it."""
        body = self.text.split("---", 2)[-1]
        self.assertIn("mcp__spine__", body,
                      "the body never mentions the door, so a crew hitting the "
                      "gap has no idea it is deliberate")
        self.assertRegex(
            body, r"session id",
            "the body does not name the shared harness session id -- that is the "
            "whole mechanism, and without it the exclusion looks like caution",
        )
        self.assertIn(
            "run_crew.py", body,
            "the body must name the channel a crew needing its own spine belongs "
            "on; an exclusion with no alternative route is a crew stuck rather "
            "than a crew guarded",
        )
        self.assertNotIn(
            "checklist_engine.py", body,
            "the escape hatch must not be the CLI -- 'the agents should not know "
            "about the CLI. period.' (tests/test_cli_retirement_guard.py)",
        )


class DispatchDoctrineNamesTheTypeTests(unittest.TestCase):
    def setUp(self):
        self.text = DOCTRINE.read_text(encoding="utf-8")

    def test_doctrine_names_the_subagent_type(self):
        self.assertIn(
            "constellation-crew", self.text,
            "crew-dispatch.md never names the `constellation-crew` subagent "
            "type, so a dispatcher has no way to know the guard exists",
        )

    def test_doctrine_connects_the_type_to_the_dispatch_call(self):
        """Co-occurrence is not connection. Require one sentence that names both
        the type and `subagent_type`, so the doctrine says what to PASS rather
        than merely mentioning that a type exists."""
        sentences = self.text.replace("\n", " ").split(". ")
        connecting = [
            s for s in sentences
            if "constellation-crew" in s and "subagent_type" in s
        ]
        self.assertTrue(
            connecting,
            "no single sentence in crew-dispatch.md names both "
            "`subagent_type` and `constellation-crew`",
        )

    def test_doctrine_states_the_asymmetry_between_the_two_channels(self):
        """The issue as filed said a helper *inherits* its launcher's spine. For
        the channel that is still open that is wrong -- there is no env
        inheritance at all; the door resolves through the shared harness session
        id. Doctrine that repeats the wrong mechanism sends the next fix to the
        wrong place."""
        self.assertIn(
            ".spine-rail-binding.json", self.text,
            "crew-dispatch.md does not name the binding file the in-harness door "
            "actually resolves through",
        )
        self.assertIn(
            "_crew_door_env", self.text,
            "crew-dispatch.md does not name the subprocess channel's assignment, "
            "so the two channels read as one problem",
        )


if __name__ == "__main__":
    unittest.main()
