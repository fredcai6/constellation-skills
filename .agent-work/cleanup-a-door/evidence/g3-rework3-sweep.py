#!/usr/bin/env python3
"""m5-sweep: the blast radius of issue #603, scoped to what the change
INVALIDATED rather than to what this rework was permitted to edit.

Why this exists at all. Rework 2's sweep reported `LIVE IN-SCOPE HITS: 0`. The
number was real and measured the wrong set: it was scoped to
`ALLOWED_SCOPE = ("tests/test_mcp_lifecycle.py",)`, the rework's EDIT
PERMISSION. Blast radius is every artifact that asserts something about what
changed, whether or not you may touch it.

Three failure modes are designed against, each one having actually happened:

  1. LINE-BASED (rework 1). A `git grep` cannot see a phrase assembled from
     adjacent string literals: `"...re-read " "fresh off..."`. Fixed by reading
     prose from the AST, where the parser has already joined them, and by
     whitespace-collapsing everything so a claim broken across lines is one
     string.
  2. KEYWORD-GUESSED (rework 2). A sweep triggered on remembered phrasings only
     finds claims phrased the way you remembered. Findings 3 and 4 escaped
     because they say "RE-READS `SPINE_FILE`" and "reads ... at IMPORT time".
     Fixed by triggering on the IDENTIFIERS the change touched, never on
     phrasings.
  3. CLASSIFIED-AWAY (rework 2, the one that actually hid the four). A sweep
     that sorts its own hits into live/fenced/historical reports the headline
     from its classifier. Fixed by making the classifier advisory only: this
     script prints EVERY hit for a human to read, and its --assert-clean exit
     code is decided solely by the reviewed ledger below, which a person filled
     in by reading, not by a predicate.

Tiering, and why the denominator is printed. TIER 1 is the raw blast radius:
every prose fragment mentioning any touched identifier. It is large and mostly
uninteresting, and it is printed as a count so the tier-2 number can never be
mistaken for "everything". TIER 2 is what must be READ: the UNION of two
independent triggers -- fragments mentioning one of the four DISTINCTIVE
identifiers (`SPINE_FILE`, `SPINE_ENGINE`, `spine_open`,
`_primary_checkout_for_lifecycle`), OR fragments matching any claim class.
The union is not belt-and-braces: --controls proves neither trigger alone
catches all six fixed claims. Findings 2 and 2b ("bound at server-launch
time") name no distinctive identifier and are reached only by the class
predicate; the class predicates are phrasing-based and so cannot be trusted
alone, which is blocker 3. Bare `SPINE`/`SESSION`/`KeyError` stay tier 1 only:
they occur everywhere and would bury the signal. That is a deliberate, named
cap, stated here rather than left silent.

Usage:
  g3-rework3-sweep.py                 full report, every tier-2 hit printed
  g3-rework3-sweep.py --assert-clean  exit non-zero if any live claim remains
  g3-rework3-sweep.py --controls      prove the predicates catch all 5 fixed claims
"""
from __future__ import annotations

import ast
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# The identifiers #603 touched. Tier 1 triggers on any of these.
TOUCHED = ("SPINE_FILE", "SPINE_ENGINE", "SPINE_SESSION", "SPINE_PARENT", "SPINE",
           "SESSION", "spine_open", "_primary_checkout_for_lifecycle",
           "_bind_process_to", "KeyError", "import time", "launch time")

# Tier 2: the distinctive subset. See the module docstring for why this cap.
DISTINCTIVE = ("SPINE_FILE", "SPINE_ENGINE", "spine_open",
               "_primary_checkout_for_lifecycle")

# Advisory only -- these NEVER decide the exit code. They exist so a reader can
# see which of #603's four changes a hit might bear on. Broad on purpose: a
# false alarm costs a read, a miss costs the gate.
CLASSES = {
    "a-import-raises": re.compile(
        r"(?:KeyError|raises?|dies|fails|crash\w*)[^.]{0,140}\bimport\b"
        r"|\bimport\b[^.]{0,140}(?:KeyError|raises?\b|dies\b|fails\b|crash\w*)",
        re.IGNORECASE),
    "b-launch-time-binding": re.compile(
        r"bound at (?:server-)?launch[- ]time|at server-launch time|launch-time (?:state|binding)",
        re.IGNORECASE),
    "c-checkout-from-spine-file": re.compile(
        r"(?:checkout|repo root|root)[^.]{0,140}(?:deriv\w*|fresh off|re-?reads?|reads|ambient)"
        r"[^.]{0,80}SPINE_FILE"
        r"|(?:deriv\w*|fresh off|re-?reads?|reads)[^.]{0,80}SPINE_FILE[^.]{0,140}"
        r"(?:checkout|repo root)",
        re.IGNORECASE),
    "d-spine-open-rereads": re.compile(
        r"_?spine_open[^.]{0,140}(?:re-?reads?|reads|re-?reading)[^.]{0,80}SPINE_FILE"
        r"|(?:re-?reads?|reads|re-?reading)[^.]{0,80}SPINE_FILE[^.]{0,140}_?spine_open",
        re.IGNORECASE),
}

# Areas. The close criterion is 0 LIVE invalidated claims in the source tree.
SOURCE_AREAS = ("scripts/", "tests/", "examples/", "docs/")
HISTORICAL_AREAS = ("episodes/", "map/", ".agent-work/")

# --------------------------------------------------------------------------- #
# THE REVIEWED LEDGER -- the only thing --assert-clean's exit code comes from.
#
# Every classified hit in the source tree, with the disposition I reached by
# READING it. Not a predicate, not a file-level allowlist: one entry per hit.
#
#   "fixed"       corrected by this rework
#   "accurate"    mentions #603's identifiers and is TRUE at HEAD -- usually a
#                 past-tense record of what #603 changed, which is history and
#                 must not be rewritten
#   "unrelated"   matched a claim class but is about some other import/binding
#                 concern entirely (the class predicates are broad on purpose)
#   "live-fenced" a genuine surviving invalidated claim in a file this rework is
#                 forbidden to touch -- REPORTED, not fixed, per the handoff's
#                 stop condition
#
# --assert-clean REFUSES if a classified source hit is absent from this ledger,
# so a newly-introduced claim cannot pass by not being listed. It also refuses
# on any "live" entry outside the fenced set.
# --------------------------------------------------------------------------- #
REVIEWED = {
    ("docs/superpowers/plans/2026-06-24-worktree-isolation-real-fix.md", "para@13"):
        ("unrelated", "verify_worktree_isolation.py's _utf8_stdio() helper 'called at import'. "
                      "Nothing to do with the door's binding."),
    ("scripts/checklist_engine.py", "comment@182"):
        ("unrelated", "gauge_reader's fail-safe import. Different module, different concern; "
                      "also fenced."),
    ("scripts/generate_spine.py", "comment@114"):
        ("unrelated", "_RESOLVER_OWNED_TOKEN_RE's unused import made into an assertion."),
    ("scripts/install_constellation.py", "comment@110"):
        ("unrelated", "run_crew.py's module-scope `import install_constellation` and the "
                      "companion-declaration guard that missed it (#559 pass 3)."),
    ("scripts/install_constellation.py", "comment@145"):
        ("unrelated", "non-installable packages whose relative imports raise once copied flat."),
    ("scripts/mcp_spine_server.py", "string@157"):
        ("accurate", "_spine_from_env's docstring, past tense: 'this USED TO BE "
                     "os.environ[\"SPINE_FILE\"], a KeyError at module scope, at import'. This "
                     "is #603's own record of what it fixed. Deleting it would erase the "
                     "history that makes the current shape legible."),
    ("scripts/mcp_spine_server.py", "string@394"):
        ("accurate", "_unbound_refusal's docstring: five inputs collapsed into one refusal "
                     "class, 'all five USED TO produce a different wrong answer'. Past tense, "
                     "true, and the point of the gate."),
    ("scripts/mcp_spine_server.py", "string@879"):
        ("accurate", "_bind_process_to's own docstring, which QUOTES the stale sentence in "
                     "order to prescribe its replacement: \"the module docstring's 'bound at "
                     "server-launch time' is now 'bound at launch OR at spine_open'\". It "
                     "states the corrected form in the same breath, and it is the authority "
                     "that made finding 2 findable. As of this rework the requirement it "
                     "states is satisfied."),
    ("scripts/run_crew.py", "comment@463"):
        ("live-fenced", "GENUINE SURVIVING INVALIDATED CLAIM. :468-471 says mcp_spine_server "
                        "'reads SPINE_FILE and SPINE_ENGINE straight out of the environment at "
                        "import time (raises KeyError if either is unset) so importing it here "
                        "would make importing run_crew itself require a bound spine'. Measured "
                        "false: import with both unset succeeds, SPINE = None. Same class as "
                        "finding 4, same falsified rationale, same still-fine practice. "
                        "scripts/run_crew.py is on the handoff's fenced list, so this is "
                        "reported and NOT fixed."),
    ("tests/test_crew_launcher.py", "string@128"):
        ("unrelated", "#559 pass 3's ModuleNotFoundError from run_crew.py's missing companion."),
    ("tests/test_install_constellation.py", "string@1623"):
        ("unrelated", "SCRIPT_RUNTIME_COMPANIONS keyed to a literal script name."),
    ("tests/test_install_constellation.py", "string@1865"):
        ("unrelated", "bundling a package flat breaks its relative imports."),
    ("tests/test_install_constellation.py", "string@1500"):
        ("unrelated", "undeclared engine runtime siblings; ImportError fallback going silent."),
    ("tests/test_install_constellation.py", "string@1678"):
        ("unrelated", "fragment of the same companion-import guard."),
    ("tests/test_map_contract_wiring.py", "comment@250"):
        ("unrelated", "frozen dataclass resolving its module through sys.modules on 3.14."),
    ("tests/test_map_orient.py", "comment@36"):
        ("unrelated", "the same 3.14 dataclass note."),
    ("tests/test_mcp_door_unbound.py", "string@1"):
        ("accurate", "the #603 test file's own module docstring, past tense: 'an unbound door "
                     "USED TO do one of two things'. This is the record of the fixed defect."),
    ("tests/test_mcp_door_unbound.py", "string@220"):
        ("accurate", "an assertion MESSAGE -- 'the door still dies at import on an unset "
                     "SPINE_FILE' is what prints IF assertNotIn('KeyError', ...) fails. The "
                     "test asserts the opposite of the claim the text states."),
    ("tests/test_mcp_identity.py", "string@494"):
        ("accurate", "test_control_is_red_when_the_config_never_delivered's docstring already "
                     "records the mechanism change explicitly: 'The MECHANISM changed at gate "
                     "g3 (issue #603). This used to read os.environ[\"SPINE_FILE\"] at import "
                     "... so the door now stays UP and REFUSES.'"),
    ("tests/test_mcp_lifecycle.py", "string@200"):
        ("live-fenced", "BORDERLINE, REPORTED NOT FIXED. The spine_open identity pin's failure "
                        "message says spine_open 'must act purely on server-launch-time "
                        "state'. Since bind-on-open, the SPINE that _primary_checkout_for_"
                        "lifecycle anchors on need not date from launch. The parenthetical "
                        "immediately names exactly what is read and is correct, and rework 2 "
                        "already corrected this text (176133ac). tests/test_mcp_lifecycle.py:194 "
                        "and its positive control are fenced byte-identical by three reviews, "
                        "so this is reported for the reviewer to rule on, not touched."),
    ("tests/test_run_skill_eval.py", "string@83"):
        ("unrelated", "a fixture script whose body is print('this check always fails')."),
}

# Files this rework corrected -- used only to label output, never to excuse a hit.
FIXED_THIS_REWORK = (
    "scripts/mcp_spine_server.py",       # findings 1 and 2
    "tests/test_mcp_lifecycle.py",       # finding 3
    "tests/test_mcp_adoption.py",        # finding 4, plus a 5th instance at :172
    "tests/test_mcp_identity.py",        # finding 2's quoted copy, plus a 6th at :18
    "docs/CHECKLIST_ENGINE_DESIGN.md",   # a 7th instance, found by reading the dump
)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.split("\n")
    return [ROOT / p for p in out if p.strip()]


def prose_fragments(path: Path) -> list[tuple[str, str]]:
    """Whitespace-collapsed prose fragments.

    For .py: AST string constants (implicit concatenation already joined by the
    parser) plus comment RUNS (consecutive `#` lines joined, so a claim spanning
    several of them reads as one sentence). For every other text file: the whole
    file collapsed, then split on blank lines, so a claim broken across lines is
    still one fragment.
    """
    try:
        src = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    if path.suffix == ".py":
        out: list[tuple[str, str]] = []
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return [("wholefile", collapse(src))]
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                out.append((f"string@{node.lineno}", collapse(node.value)))
        run: list[str] = []
        start = 0
        prev = -2
        try:
            for tok in tokenize.generate_tokens(io.StringIO(src).readline):
                if tok.type == tokenize.COMMENT:
                    if tok.start[0] != prev + 1 and run:
                        out.append((f"comment@{start}", collapse(" ".join(run))))
                        run = []
                    if not run:
                        start = tok.start[0]
                    run.append(tok.string.lstrip("#").strip())
                    prev = tok.start[0]
        except tokenize.TokenError:
            pass
        if run:
            out.append((f"comment@{start}", collapse(" ".join(run))))
        return out

    frags = []
    para: list[str] = []
    start = 1
    for i, line in enumerate(src.split("\n"), start=1):
        if line.strip():
            if not para:
                start = i
            para.append(line)
        elif para:
            frags.append((f"para@{start}", collapse(" ".join(para))))
            para = []
    if para:
        frags.append((f"para@{start}", collapse(" ".join(para))))
    return frags


def area_of(rel: str) -> str:
    for a in SOURCE_AREAS:
        if rel.startswith(a):
            return "source"
    for a in HISTORICAL_AREAS:
        if rel.startswith(a):
            return "historical"
    return "other"


def sweep():
    files = tracked_files()
    tier1: list[tuple[str, str, str]] = []
    tier2: list[tuple[str, str, str]] = []
    scanned_files = 0
    scanned_frags = 0

    for path in files:
        if not path.is_file():
            continue
        frags = prose_fragments(path)
        if not frags:
            continue
        scanned_files += 1
        rel = str(path.relative_to(ROOT))
        for where, text in frags:
            scanned_frags += 1
            # TIER 2 is the UNION of two independent triggers, because the
            # controls proved neither alone is sufficient. The distinctive-id
            # trigger misses findings 2 and 2b, which say "bound at
            # server-launch time" and name no distinctive identifier at all.
            # The claim-class trigger misses nothing there but is phrasing-based
            # and so cannot be trusted alone -- that is blocker 3. Either fires
            # and the fragment gets read. The class predicates run over EVERY
            # fragment, not just tier 1, so tier 2 does not inherit the
            # identifier list's blind spots.
            distinctive = any(t in text for t in DISTINCTIVE)
            classed = bool(classify(text))
            if any(t in text for t in TOUCHED):
                tier1.append((rel, where, text))
            if distinctive or classed:
                tier2.append((rel, where, text))

    # THE GUARD THAT LOOPS MUST ASSERT WHAT IT LOOPED OVER.
    assert scanned_files > 0, "swept 0 files -- an empty sweep reports clean without looking"
    assert scanned_frags > 0, "swept 0 fragments -- same failure, one level down"
    assert tier1, "0 fragments mention ANY touched identifier -- impossible in this repo; "\
                  "the extractor is broken, not the tree clean"

    return files, scanned_files, scanned_frags, tier1, tier2


def classify(text: str) -> list[str]:
    return [name for name, rx in CLASSES.items() if rx.search(text)]


def main(assert_clean: bool) -> None:
    files, scanned_files, scanned_frags, tier1, tier2 = sweep()

    classified = [(rel, where, text, cls) for rel, where, text in tier2
                  if (cls := classify(text))]
    live = [(rel, where, text, cls) for rel, where, text, cls in classified
            if area_of(rel) == "source"]

    print("=" * 78)
    print("BLAST-RADIUS SWEEP -- issue #603")
    print("=" * 78)
    print(f"tracked files listed                 : {len(files)}")
    print(f"files with readable prose (SCANNED)  : {scanned_files}")
    print(f"prose fragments scanned              : {scanned_frags}")
    print(f"TIER 1 -- mention any touched id     : {len(tier1)}")
    print(f"TIER 2 -- mention a distinctive id   : {len(tier2)}   <- every one printed below")
    print(f"  of those, matching a claim class   : {len(classified)}  (advisory only)")
    print(f"  of those, in the source tree       : {len(live)}")
    print()
    print("Tier-2 hits by file:")
    by_file: dict[str, int] = {}
    for rel, _, _ in tier2:
        by_file[rel] = by_file.get(rel, 0) + 1
    for rel in sorted(by_file, key=lambda r: (-by_file[r], r)):
        print(f"  {by_file[rel]:4d}  {rel}  [{area_of(rel)}]")
    print()
    print("-" * 78)
    print("CLASSIFIED HITS -- advisory; the exit code does not come from here")
    print("-" * 78)
    for rel, where, text, cls in classified:
        print(f"\n[{area_of(rel)}] {rel} {where}  classes={cls}")
        print(f"    {text[:400]}")
    if not classified:
        print("\n(none)")

    if assert_clean:
        print()
        print("=" * 78)
        print("REVIEWED-LEDGER VERDICT")
        print("=" * 78)
        unlisted = [(r, w, t, c) for r, w, t, c in live if (r, w) not in REVIEWED]
        if unlisted:
            print(f"REFUSED: {len(unlisted)} classified source hit(s) absent from the reviewed "
                  "ledger. A hit nobody read is not a hit nobody needs to read:")
            for r, w, t, c in unlisted:
                print(f"  {r} {w} classes={c}\n    {t[:300]}")
            sys.exit(1)

        dispositions: dict[str, list[str]] = {}
        for r, w, _, _ in live:
            kind = REVIEWED[(r, w)][0]
            dispositions.setdefault(kind, []).append(f"{r} {w}")
        for kind in sorted(dispositions):
            print(f"  {kind:<12} {len(dispositions[kind])}")

        unfixed = [k for k in dispositions if k not in ("accurate", "unrelated", "live-fenced")]
        if unfixed:
            print(f"REFUSED: unexpected dispositions {unfixed}")
            sys.exit(1)

        fenced = dispositions.get("live-fenced", [])
        print()
        print("LIVE INVALIDATED CLAIMS IN NON-FENCED SOURCE FILES: 0")
        if fenced:
            print(f"REPORTED, NOT FIXED -- {len(fenced)} live claim(s) in FENCED files, which "
                  "this gate's stop condition says to report:")
            for f in fenced:
                r, w = f.rsplit(" ", 1)
                print(f"  * {f}\n      {REVIEWED[(r, w)][1]}")
        print()
        print(f"measured over {scanned_files} files / {scanned_frags} fragments; "
              f"tier 1 = {len(tier1)}, tier 2 = {len(tier2)}, classified = {len(classified)}")
        print("=" * 78)


def controls() -> None:
    """Every claim this rework fixed, fed back as text. All five must trip.

    This is the answer to "a check that cannot fail is indistinguishable from
    one that passed" -- and to blocker 3 specifically, where the sweep's
    triggers matched no finding.
    """
    fixtures = {
        "finding 1 (module docstring, split across LITERALS)": (
            "deriving the primary checkout it opens work from fresh off `SPINE_FILE` "
            "(ambient, server-launch-time state) rather than the module's own `SPINE` binding"),
        "finding 2 (:30)": (
            "Ambient state is bound at server-launch time from the environment, NOT exposed "
            "as tool arguments"),
        "finding 2b (identity quote)": (
            "'Ambient state is bound at server-launch time from the environment ... that is "
            "the seam identity rides on.'"),
        "finding 3 (comment, split across LINES)": (
            "`_spine_open` deliberately RE-READS `SPINE_FILE` from the environment at call "
            "time (never the module's own bound `SPINE` -- that is the whole point of the "
            "identity pin above), so it must still be set now"),
        "finding 4 (adoption rationale)": (
            "`mcp_spine_server` reads SPINE_FILE/SPINE_ENGINE from the environment at IMPORT "
            "time and raises KeyError without both set"),
        "finding 5 (_load_mcp_spine_server docstring)": (
            "It reads those from the environment at IMPORT time and raises KeyError without "
            "both `SPINE_FILE`/`SPINE_ENGINE` set (its own module docstring)"),
    }
    bad = []
    for label, text in fixtures.items():
        t = collapse(text)
        distinctive = any(d in t for d in DISTINCTIVE)
        cls = classify(t)
        tier2_ok = distinctive or bool(cls)
        status = "OK " if tier2_ok else "MISS"
        if status == "MISS":
            bad.append(label)
        print(f"{status}  {label}\n      tier2={tier2_ok} (distinctive-id={distinctive}, classes={cls})")
    if bad:
        print(f"\nCONTROLS BROKEN: the sweep would not have caught {bad}")
        sys.exit(1)
    print("\nCONTROLS OK: all 6 corrected claims land in tier 2 and would be read.")
    print("Both hard cases pass. Findings 1 and 3 were split across adjacent string")
    print("literals and across comment lines respectively -- invisible to a line-based")
    print("grep, joined into one fragment by the AST + comment-run extractor. Findings")
    print("2 and 2b name NO distinctive identifier and are caught only by the claim")
    print("class; that is why tier 2 is a union and not the identifier cap alone.")


if __name__ == "__main__":
    if "--controls" in sys.argv:
        controls()
    else:
        main(assert_clean="--assert-clean" in sys.argv)
