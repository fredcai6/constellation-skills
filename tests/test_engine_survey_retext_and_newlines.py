"""Issue #465: the engine must not churn a file's line endings, and `amend`'s
`retext-check` op must be usable on a SURVEY checklist.

Two independent defects, one file, because they are the two engine changes that
make every instruction in the reviewer skill name an action the engine can
actually perform.

Line-ending note for whoever edits this file next: **both** fixtures ship and each
has a different job. On Windows the LF fixture is the discriminating one — the old
`write_text` already emitted CRLF there, so a CRLF-only test passes in the healthy
world and the broken one alike and proves nothing. The CRLF fixture is the guard
against the obvious over-correction of "just always write LF". On POSIX the roles
swap. Build fixtures with `write_bytes` (a `write_text("...\\n")` fixture is born
CRLF on Windows) and assert on `read_bytes` (universal-newline translation makes a
`read_text` assertion vacuously true forever).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "checklist_engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("checklist_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


E = load_engine()


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
def survey_item(iid: str, command: str | None = None, status: str = "pending") -> dict:
    post = []
    if command is not None:
        post = [{
            "id": "c1",
            "statement": f"{iid} postcondition",
            "check": {"kind": "command", "command": command},
            "satisfied": False,
        }]
    return {
        "id": iid, "title": iid, "imperative": f"check {iid}",
        "preconditions": [], "postconditions": post,
        "constraints": [], "directives": None, "child_checklist": None,
        "status": status, "status_detail": {}, "result": None, "finding": None,
        "evidence": [], "rework_count": 0,
    }


def survey(**tasks) -> dict:
    return {
        "work_id": "t", "type": "survey", "config": {},
        "items": list(tasks.keys()), "tasks": tasks,
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


def write_with_endings(path: Path, eol: bytes) -> None:
    """Lay down a multi-line JSON file whose endings are EXACTLY `eol`.

    `write_bytes`, never `write_text`: on Windows text mode translates every `\\n`
    to `\\r\\n`, so an LF fixture built with `write_text` is born CRLF and the test
    that depends on it degenerates into one that cannot fail.
    """
    import json
    body = json.dumps({"work_id": "t", "type": "survey", "items": [], "tasks": {}}, indent=2)
    path.write_bytes((body + "\n").replace("\n", eol.decode("ascii")).encode("utf-8"))


def line_ending_counts(raw: bytes) -> tuple[int, int]:
    """(crlf_count, bare_lf_count) — the only property these tests assert on.

    Deliberately NOT a whole-file byte comparison against the fixture: `save()`
    re-serialises with `indent=2`, so the content legitimately differs and an
    equality assertion would fail for the wrong reason and get loosened until it
    proved nothing.
    """
    crlf = raw.count(b"\r\n")
    return crlf, raw.count(b"\n") - crlf


# --------------------------------------------------------------------------- #
# save() line endings
# --------------------------------------------------------------------------- #
def test_save_preserves_lf_line_endings(tmp_path: Path):
    """An LF file stays LF after a save. On WINDOWS this is the discriminating
    case: the old text-mode `write_text` emitted the platform ending, so it
    rewrote every `\\n` to `\\r\\n` and churned the whole file.

    Also pins the two documented LF defaults: a file that does not exist yet, and
    a file with MIXED endings, both get LF.
    """
    target = tmp_path / "lf.json"
    write_with_endings(target, b"\n")
    assert line_ending_counts(target.read_bytes())[0] == 0, "fixture was not born LF"

    E.save(target, {"work_id": "t", "type": "survey", "items": ["r1"], "tasks": {}})

    crlf, lf = line_ending_counts(target.read_bytes())
    assert crlf == 0, f"save() churned an LF file to CRLF ({crlf} CRLF endings written)"
    assert lf > 0, "save() wrote no line endings at all"

    # A file that does not exist yet gets LF.
    fresh = tmp_path / "does-not-exist-yet.json"
    E.save(fresh, {"work_id": "t", "type": "survey", "items": [], "tasks": {}})
    crlf, lf = line_ending_counts(fresh.read_bytes())
    assert lf > 0 and crlf == 0, "a new file must be written with LF"

    # A file with MIXED endings gets LF — we do not guess which one the author meant.
    mixed = tmp_path / "mixed.json"
    mixed.write_bytes(b'{\r\n  "work_id": "t",\n  "type": "survey"\r\n}\n')
    E.save(mixed, {"work_id": "t", "type": "survey", "items": [], "tasks": {}})
    crlf, lf = line_ending_counts(mixed.read_bytes())
    assert lf > 0 and crlf == 0, "a mixed-ending file must be normalised to LF"


def test_save_preserves_crlf_line_endings(tmp_path: Path):
    """A CRLF file stays CRLF after a save. This is the guard against the obvious
    over-correction of "always write LF" — on POSIX it is the discriminating case,
    on Windows it is the one that must not regress.
    """
    target = tmp_path / "crlf.json"
    write_with_endings(target, b"\r\n")
    crlf, lf = line_ending_counts(target.read_bytes())
    assert crlf > 0 and lf == 0, "fixture was not born CRLF"

    E.save(target, {"work_id": "t", "type": "survey", "items": ["r1"], "tasks": {}})

    crlf, lf = line_ending_counts(target.read_bytes())
    assert crlf > 0, "save() wrote no CRLF endings at all"
    assert lf == 0, f"save() churned a CRLF file to LF ({lf} bare LF endings written)"


# --------------------------------------------------------------------------- #
# amend on a survey
# --------------------------------------------------------------------------- #
def retext_op(iid: str, cond: str, command: str) -> dict:
    return {"op": "retext-check", "id": iid, "cond": cond,
            "which": "postconditions", "command": command}


def test_retext_check_works_on_a_survey():
    """A delta whose ops are ALL `retext-check` is accepted on a survey.

    This is the repair path the reviewer skill points at: `r6-fowler` ships with a
    placeholder record path in its command postcondition, and when the record moves
    the reviewer must be able to correct that text THROUGH the engine instead of
    hand-editing the survey JSON.
    """
    cl = survey(r6=survey_item("r6", command="python scripts/verify_fowler_pass.py <placeholder>"))
    delta = {"ops": [retext_op("r6", "c1", "python scripts/verify_fowler_pass.py real/record.json")]}

    out = E.amend(cl, delta, reason="record path resolved", authority="Commander w3a-465")

    assert "retext-check r6.c1" in out
    check = cl["tasks"]["r6"]["postconditions"][0]["check"]
    assert check["command"] == "python scripts/verify_fowler_pass.py real/record.json"
    assert check["kind"] == "command", "retext-check must never change a check's kind"
    assert cl["tasks"]["r6"]["postconditions"][0]["satisfied"] is False, \
        "retext-check must never mark the condition satisfied"
    assert cl["amendments"][-1]["authority"] == "Commander w3a-465"

    # It also works on an IN-PROGRESS survey item, the status the reviewer is
    # actually in when the placeholder bites.
    live = survey(r6=survey_item("r6", command="cmd <placeholder>", status="in-progress"))
    E.amend(live, {"ops": [retext_op("r6", "c1", "cmd real")]},
            reason="r", authority="Commander w3a-465")
    assert live["tasks"]["r6"]["postconditions"][0]["check"]["command"] == "cmd real"


def test_add_drop_rescope_still_refuse_a_survey():
    """`add`/`drop`/`rescope` stay gated-only, and the refusal says WHY.

    The refusal must read as a conservative choice, not a type-level impossibility:
    dropping a survey item is a coherent thing to want, it is refused because
    nothing needs it yet. It must also not refuse a delta merely for MIXING a
    gated-only op in with retext-check ops — that mix is refused too, all-or-nothing.
    """
    ok_retext = retext_op("r6", "c1", "cmd real")

    cases = {
        "add": {"op": "add", "id": "r7", "title": "t", "imperative": "i",
                "postconditions": [{"id": "c1", "statement": "s", "check": None, "satisfied": False}]},
        "drop": {"op": "drop", "id": "r6"},
        "rescope": {"op": "rescope", "id": "r6", "title": "new title"},
    }
    for name, op in cases.items():
        cl = survey(r6=survey_item("r6", command="cmd <placeholder>"))
        with pytest.raises(E.EngineError) as exc:
            E.amend(cl, {"ops": [op]}, reason="r", authority="Commander w3a-465")
        msg = str(exc.value)
        assert name in msg, f"{name}: refusal must name the op that was refused -- got {msg!r}"
        assert "conservative" in msg.lower(), \
            f"{name}: refusal must frame the limit as a conservative choice -- got {msg!r}"
        # all-or-nothing: the refused delta leaves the survey unmutated
        assert cl["tasks"]["r6"]["title"] == "r6"
        assert "r7" not in cl["tasks"]
        assert cl.get("amendments") is None

        # mixing a gated-only op into an otherwise-legal delta is refused too
        mixed = survey(r6=survey_item("r6", command="cmd <placeholder>"))
        with pytest.raises(E.EngineError):
            E.amend(mixed, {"ops": [ok_retext, op]}, reason="r", authority="Commander w3a-465")
        assert mixed["tasks"]["r6"]["postconditions"][0]["check"]["command"] == "cmd <placeholder>", \
            f"{name}: a refused mixed delta must leave the retext-check op unapplied"

    # ...and all three still work on a GATED checklist, unchanged.
    gated = survey(r6=survey_item("r6", command="cmd <placeholder>"))
    gated["type"] = "gated"
    E.amend(gated, {"ops": [cases["drop"]]}, reason="r", authority="Commander w3a-465")
    assert "r6" not in gated["tasks"]
