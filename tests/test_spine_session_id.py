"""`spine_lifecycle.session_id_for` -- the ONE definition of the lease identity
a spine for a `work_id` is driven under (epic #567 lane A, gate g2-implement).

The rule `constellation/<work_id>` was an inline f-string inside `open_work`'s
return dict (`spine_lifecycle.py:357`). Two callers now need it: `open_work`,
which returns it as `SPINE_SESSION` when it MINTS a spine, and the door's
`spine_bind`, which recovers it from a spine that already exists. Two callers
with two copies of one f-string is a drift waiting to happen -- and the drift
would be silent and load-bearing, because it would mean "the identity a spine
was opened under" and "the identity a spine is bound under" could disagree
while both looked right. So the rule is extracted and both call it.

This module tests the extraction ONLY. `spine_bind` itself is
`tests/test_mcp_spine_bind.py`.
"""

from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import spine_lifecycle as sl  # noqa: E402


class TestSessionIdFor:
    def test_the_rule_is_constellation_slash_work_id(self):
        assert sl.session_id_for("w1") == "constellation/w1"

    def test_a_slashed_work_id_is_carried_verbatim(self):
        """`work_id` legitimately contains `/` (`epic-567-door/cmdr-a`), and the
        session string keeps it -- the engine matches session ids by plain
        string equality, so any normalisation here would be a second identity."""
        assert sl.session_id_for("epic-567-door/cmdr-a") == "constellation/epic-567-door/cmdr-a"

    def test_it_is_pure(self):
        """No clock, no environment, no filesystem: a session id derived from
        ambient state could not be reproduced by a second process binding the
        same spine, which is the whole property `spine_bind` needs."""
        src = inspect.getsource(sl.session_id_for)
        for forbidden in ("datetime", "os.environ", "Path(", "getenv"):
            assert forbidden not in src, f"session_id_for reads {forbidden}"


class TestOpenWorkUsesTheOneDefinition:
    """A pin proving there is one definition is satisfied vacuously by a
    definition nothing calls. This is the other half: `open_work` reaches it,
    and the old inline f-string is gone rather than merely shadowed."""

    def test_open_work_calls_session_id_for_in_its_own_source(self):
        src = inspect.getsource(sl.open_work)
        assert "session_id_for(" in src, (
            "open_work no longer calls session_id_for -- the extraction is inert and "
            "the two callers can drift"
        )

    def test_the_inline_f_string_is_gone_from_the_module(self):
        """Text-level, module-wide: the literal `constellation/` prefix must
        appear in exactly ONE place in `spine_lifecycle.py` -- inside
        `session_id_for` -- or the extraction added a definition instead of
        replacing one."""
        source = Path(sl.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        holders = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            segment = ast.get_source_segment(source, node) or ""
            if "constellation/" in segment:
                holders.append(node.name)
        assert holders == ["session_id_for"], (
            f"the `constellation/<work_id>` rule appears in {holders} -- it must live only "
            "in session_id_for"
        )
