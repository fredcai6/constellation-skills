"""Fresh-subprocess structural proof that the rewritten rail mechanism still
works: imports scripts/checklist_engine.py from this worktree in a brand-new
interpreter (never the running commander session) and confirms _rail() still
emits the fixed 'RAIL: ' envelope for the 'early' position. Content-agnostic
on purpose -- the exact new wording is proven separately by the cold-agent
measurement and quoted verbatim in the return; this only proves the edit did
not break the mechanism itself. g4-validate's engine-checked command runs
this file so the proof is re-derived by the engine, not self-reported.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import checklist_engine as E  # noqa: E402

cl = {
    "type": "gated",
    "items": ["g1", "g2"],
    "tasks": {
        "g1": {"id": "g1", "status": "pending", "imperative": "x"},
        "g2": {"id": "g2", "status": "pending", "imperative": "y"},
    },
}
out = E._rail("claim", cl)
assert out.startswith("\n\nRAIL: "), f"rail envelope broken: {out!r}"
assert len(out) > len("\n\nRAIL: "), "rail text is empty"
assert "{id}" not in out, f"unsubstituted token leaked: {out!r}"
print("OK: fresh-subprocess 'early' rail check passed:", out.replace("\n", " ").strip())
