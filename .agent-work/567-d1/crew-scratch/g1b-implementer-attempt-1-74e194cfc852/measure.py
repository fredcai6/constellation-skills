"""Measurement harness for g1b. Not a deliverable -- scratch only.

Prices each candidate widened pattern the only way that matters: the set of
ADDRESSES the guard would report, before vs after. A candidate's false-alarm
cost is the addresses it adds that the three g1 patterns did not already flag.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))

from test_mcp_adoption import (  # noqa: E402
    INSTRUCTION_FILES,
    INSTRUCTION_SUFFIXES,
    _instruction_texts,
)

OVERLAY_DIR = ".agent-work/templates"


def _walk(rel: str, suffixes) -> list[str]:
    base = ROOT / rel
    if not base.is_dir():
        return []
    return sorted(
        p.relative_to(ROOT).as_posix()
        for p in base.rglob("*")
        if p.is_file() and p.suffix in suffixes
    )


SPEC_FILES = _walk("specs", (".toml",))
OVERLAY_FILES = _walk(OVERLAY_DIR, INSTRUCTION_SUFFIXES)


def texts(include_overlay: bool):
    out = []
    for path in INSTRUCTION_FILES + (OVERLAY_FILES if include_overlay else []):
        whole = not path.endswith(".json")
        for where, text in _instruction_texts(path):
            out.append((path, where, text, whole))
    for path in SPEC_FILES:
        out.append((path, path, (ROOT / path).read_text(encoding="utf-8"), True))
    return out


_V = (
    "current|start|advance|record|consolidate|claim|release|heartbeat|"
    "attest|attach|waive|skip|block|reopen|append|amend|flag-candidate"
)

OLD = {
    "placeholder": re.compile(r"<engine>"),
    "fallback": re.compile(r"CLI[\s-]+fallback", re.IGNORECASE),
    "invocation": re.compile(
        r"""(?:(?:python3?|py)\s+(?:[^\s`'"]+\s+)?|[^\s`'"]*/)checklist_engine\.py"""
        r"""|checklist_engine\.py(?=[`'"\s]*(?:--[A-Za-z]|(?:""" + _V + r""")\b))"""
    ),
}

NAMED = r"(?:<[A-Za-z0-9_.-]*(?:engine|cli)[A-Za-z0-9_.-]*>" \
        r"|\{\{[^{}\n]*(?:engine|cli)[^{}\n]*\}\}" \
        r"|\$\{?[A-Za-z0-9_]*(?:ENGINE|CLI)[A-Za-z0-9_]*\}?)"
ANY = r"(?:<[A-Za-z0-9_.-]+>|\{\{[^{}\n]+\}\}|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?)"

CANDIDATES = {
    # named stand-in, any whitespace (incl. newline) before the verb
    "A": re.compile(NAMED + r"""[`'"]*\s+(?:""" + _V + r""")\b""", re.IGNORECASE),
    # named stand-in, same-line separator only
    "A-sameline": re.compile(NAMED + r"""[`'"]*[ \t]+(?:""" + _V + r""")\b""", re.IGNORECASE),
    # any stand-in, any whitespace
    "B": re.compile(ANY + r"""[`'"]*\s+(?:""" + _V + r""")\b"""),
    # any stand-in, same-line separator only
    "B-sameline": re.compile(ANY + r"""[`'"]*[ \t]+(?:""" + _V + r""")\b"""),
}

MISSES = [
    "Second path: <cli> claim --session-id <commander-session-id> --claimed-by commander.",
    "If the door is down: <engine-cli> advance g1 --why 'gate closed'.",
    "Fallback command line: {{engine}} release --session-id <work-id>.",
    "Then run `$ENGINE claim --session-id <id>`",
]
PROSE_ONLY = [
    "the engine rail string table (`checklist_engine.py`, #140)",
    "an epic that rewrites `checklist_engine.py` -- the very engine driving it",
    "Scripts: `checklist_engine.py`, `init_work_area.py`, `run_crew.py`",
    "nothing enforces the execution-time half in code -- `checklist_engine.py` does not",
    "a `templates/*.json` checklist driven through `checklist_engine.py` (`commander`)",
]


def addresses(pattern, corpus):
    out = {}
    for path, where, text, whole in corpus:
        for m in pattern.finditer(text):
            addr = f"{where}:{text.count(chr(10), 0, m.start()) + 1}" if whole else where
            ex = " ".join(text[max(0, m.start() - 60):m.end() + 60].split())
            out.setdefault(addr, []).append((m.group(0), ex))
    return out


if __name__ == "__main__":
    include_overlay = "--overlay" in sys.argv
    corpus = texts(include_overlay)
    print(f"corpus: {len(corpus)} texts / {len(INSTRUCTION_FILES)} skills + "
          f"{len(SPEC_FILES)} specs + {len(OVERLAY_FILES) if include_overlay else 0} overlay\n")

    baseline = set()
    for name, pat in OLD.items():
        a = addresses(pat, corpus)
        baseline |= set(a)
        print(f"old {name}: {sum(len(v) for v in a.values())} matches at {len(a)} addresses")
    print(f"old TOTAL distinct addresses: {len(baseline)}\n")

    for name, pat in CANDIDATES.items():
        a = addresses(pat, corpus)
        new = {k: v for k, v in a.items() if k not in baseline}
        caught = [s for s in MISSES if pat.search(s)]
        falsefire = [s for s in PROSE_ONLY if pat.search(s)]
        print(f"### {name}: {sum(len(v) for v in a.values())} matches / {len(a)} addresses; "
              f"NEW addresses = {len(new)}; respellings caught {len(caught)}/{len(MISSES)}; "
              f"PROSE_ONLY fired {len(falsefire)}")
        for k, v in new.items():
            for tok, ex in v:
                print(f"    NEW {k}  [{tok!r}]\n        ...{ex}...")
        for s in MISSES:
            if not pat.search(s):
                print(f"    MISSED: {s}")
        print()
