"""Regrowth guard for issue #559 -- the door is the interface, not a second path.

The human ruling this guard enforces, verbatim:

    "the agents should not know about the CLI. period."

That text has been deleted from the instruction corpus TWICE and has grown back
TWICE. The deliverable of this lane is therefore not the deletion -- it is the
guard that makes the third deletion stick. This file is that guard, and it is
authored BEFORE the sweep on purpose: a guard written against an already-clean
corpus can only be red-proofed against a scratch string its own author chose,
which any pattern passes. Written now, its RED is produced by the real corpus.

WHAT THIS PINS. Over every agent-facing instruction text in the corpus, the
ABSENCE of four things:

  1. The `<engine>` placeholder token -- a spine template's stand-in for an
     engine command line. `init_work_area.py` deliberately never resolves it,
     so every one that reaches an agent reaches it unresolved.
  2. A `CLI fallback` clause, case-insensitive, in ANY punctuation form.
  3. A command-shaped `checklist_engine.py` invocation -- the script reached by
     a path or an interpreter, or followed by a flag or an engine verb.
  4. A stood-in-for command line: ANY placeholder shape followed on the same
     line by an engine verb. This is pattern 1 generalized from the token to the
     shape, and it is what stops the whole "engine command line inside a JSON
     spine template" class from resting on one 8-character literal.

Pattern 3 exists because 1 and 2 are defeated by rewording. Once the phrase
"CLI fallback" is gone, a rename-around reads "run the engine script directly"
and both of the other patterns stay green. What a rename-around cannot do is
omit the runnable command, because the command is the point of the sentence.

Pattern 4 exists because pattern 3 cannot reach a spine template at all: a
command line in a template never contains the literal `checklist_engine.py` --
a placeholder is precisely what stands in for it -- so before pattern 4 the only
thing catching that class was the exact spelling `<engine>`. The g1 review
verified three respellings that passed all of 1-3 clean; they are pinned as
caught in `TestTheStandInCommandPredicateItself`.

WHAT COUNTS AS AN ENGINE VERB IS READ FROM THE ENGINE, NOT LISTED HERE. Patterns
3 and 4 both rest on that verb set, and it was hand-typed for exactly one
revision before the g1b review found it already wrong: 17 verbs against the
engine's 18, missing `resume`, so `<cli> resume g1 --reason 'unblocked'` passed
all four patterns clean -- the very class pattern 4 was added to close, and
inside none of the limits declared below. It is now derived from
`test_mcp_adoption._engine_verbs()`, which reads `checklist_engine.parse_args`'s
own argparse choices, and `TestTheVerbSetIsTheEnginesOwn` pins the tie in the
assertion path so the two cannot drift again in silence.

THIS IS A GENERALIZATION, NOT A NEW INVENTION. `test_mcp_adoption.py`'s
`TestTier2SpineAlreadyBoundForDispatchedCrews` already asserts this same
absence, for two files, and already pins the ruling above verbatim. This file
is that precedent widened from 2 files to the whole corpus.

THE CORPUS IS WALKED, NEVER LISTED, AND THE EXCEPTION LIST IS EMPTY. The walk
is `test_mcp_adoption.INSTRUCTION_FILES` -- imported, not re-derived, so the
repo has exactly ONE machine-readable definition of "agent-facing instruction
text" and the two cannot drift apart in silence -- extended here by two rules,
each a directory plus a suffix, never a file list:

  * `specs/**/*.toml`, which is where door doctrine lands and which the
    adoption walk does not reach.
  * `.agent-work/templates/**`, at the SAME suffixes the adoption walk uses
    (imported too, for the same anti-drift reason). That directory is a tracked
    overlay of the skills templates, and workbench doctrine tells an agent to
    PREFER it over the bundled `skills/` copy when instantiating. A sweep of
    `skills/` alone therefore turns this guard green while the copy an agent in
    this repo actually instantiates still hands over the second path -- measured
    on this tree, the overlay carries 16 of the corpus's 26 `<engine>`
    OCCURRENCES, across 6 of the 11 files containing one, and 18 of its 34
    `CLI fallback` occurrences, across 10 of the 21 files containing one. Each
    overlay file is byte-identical to its `skills/` source and mirrored again
    under `.baseline/`, so a sweep must edit all three copies.

EVERY CENSUS HERE IS WRITTEN AS "N occurrences of X across M files containing
X", and reading one in any other unit will mislead you. Occurrences, lines and
files are three different numbers over this corpus and they are not close: those
16 overlay `<engine>` occurrences sit in just 6 JSON string leaves, every one of
which carries more than one, so a per-line sweep fixes 6 things and leaves 10.
This lane has now conflated those units at three consecutive tiers, in both
directions, so state the unit or do not state the number.

The overlay rule is scoped to `.agent-work/templates/` and not to
`.agent-work/`, because the rest of that directory is a live run's own working
artifacts -- launch orders, notes, crew handoffs, review results. Those quote
the forbidden clause constantly and legitimately: they are a RECORD of what was
said, not instruction an agent is handed. Same distinction, same side of the
line, as `episodes/**`, `tests/fixtures/` and `tests/data/`.

There is NO per-file exclusion, of any length. A sibling guard's exception list
reached 11 entries across five runs; that decay is the named failure mode this
file exists to avoid. Everything excluded is excluded by a rule the walk itself
applies, and measured against this tree that rule is already sufficient: it puts
every target file IN, and it puts both sites that must survive OUT --
`docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` (a
historical plan record) and `scripts/init_work_area.py:24` (a comment
documenting the never-resolved-placeholder convention itself). Neither is named
here, and neither needs to be: they are not under `skills/`, not a
`specs/*.toml` and not under `.agent-work/templates/`, because of what they ARE.

EVERY NUMBER IN THIS FILE WAS MEASURED -- at 8ba1334c, and re-measured on the
working tree when the verb set was derived from the engine. None is inherited
from a review or a handoff. Read as a permanent property of the tree they are a
defect; read as a pin they are what makes a later drift visible. Re-measure
before you repeat one, and repeat the unit with it.

WHAT THIS DOES NOT ENFORCE, STATED RATHER THAN GLOSSED:

  * The bare word "CLI". Corpus-wide that is over-broad -- `--backend cli` is a
    real flag and a real dispatch mode -- so it is left alone here even though
    the two-file precedent does assert it. The scope where it is safe is the
    scope that precedent already covers.
  * A bare prose mention of `checklist_engine.py` that names the engine as a
    component rather than telling anyone to run it ("an epic that rewrites
    `checklist_engine.py`", a scripts manifest). Measured on this tree, that
    distinction leaves 6 such mentions alone while catching all 10 command
    forms; see `TestTheInvocationPredicateItself`, which pins both directions in
    the assertion path so a later edit to the pattern cannot quietly move them.
  * A prose mention that asserts a DRIVE PATH without writing a command --
    `skills/write-a-skill/SKILL.md:20`, an archetype table cell reading "a
    `templates/*.json` checklist driven through `checklist_engine.py`". The g1
    review raised it as the corpus shape closest to the line, and it is left on
    the prose side DELIBERATELY, pinned in `PROSE_ONLY` so the decision is
    testable rather than incidental. It does assert the belief #559 removes, and
    it is a real target for the sweep -- but it hands an agent no runnable path,
    and no predicate can separate "driven through X" from "Scripts: X" without
    reading English. That predicate is exactly the class `test_mcp_adoption.py`
    built, measured and DELETED (`TestCLIStaysAvailableNotDeprecated`). Deciding
    that cell is a one-line human judgement; encoding it is a check the next
    author deletes.
  * Three placeholder dialects nobody in this corpus writes: `[engine]`,
    `__ENGINE__` and `$(engine)`. The g1b review found them and did not demand
    them, and that distinction is deliberate rather than an oversight. `resume`
    had an ORACLE -- `parse_args` states what the verb set is, so a verb missing
    from this file was drift and is now derived away. Which placeholder dialect
    an author reaches for has no oracle; it is a judgement, and a pattern built
    on a guess about it is the open-ended class `test_mcp_adoption.py` measured
    and deleted. They are accepted residuals: adding them would cost zero today,
    and they stay out until a corpus site or a review finding argues otherwise.
  * Prose that FORBIDS the violation while quoting it. A guard reading a
    quotation cannot tell a prohibition from an instruction, and this file
    accepts that false alarm rather than growing a polarity predicate: the
    corpus this guards should not need to quote the clause at all, and a
    deliberate quotation is a one-line judgement for a human, not a rule to
    encode.

EVERY FAILURE MESSAGE QUOTES THE RULING VERBATIM rather than citing a location.
This lane may not write `docs/agents/*` and files no issue, so any pointer this
file could offer would dangle. Carrying the ruling inline means deleting the
guard also deletes the reason, which is the property a dangling pointer loses.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The repo's own definition of "agent-facing instruction text" lives in the
# adoption suite. Import it rather than re-deriving it: a re-derived copy is two
# definitions that agree today and drift silently tomorrow. The explicit
# sys.path insert is this directory's house idiom for a cross-test import (see
# test_mcp_imperative_equivalence.py) rather than relying on incidental ordering.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_mcp_adoption import (  # noqa: E402
    INSTRUCTION_FILES,
    INSTRUCTION_SUFFIXES,
    _engine_flags,
    _engine_verbs,
    _instruction_texts,
)

#: The ruling, verbatim, carried by every failure message in this file.
HUMAN_RULING = "the agents should not know about the CLI. period."

#: Instruction text the adoption walk does not reach. `specs/*.toml` is where
#: door doctrine is authored, so a fallback clause could otherwise be written
#: there with this guard green. A suffix rule, not a file list.
SPEC_SUFFIXES = (".toml",)

#: The project's tracked template overlay. Workbench doctrine tells an agent to
#: instantiate from here IN PREFERENCE to the bundled `skills/` copy, so this is
#: the text that actually reaches an agent working in this repo -- and the
#: adoption walk, rooted at `skills/`, never sees it.
#:
#: The rule is this ONE directory, not `.agent-work/`. Everything else under
#: `.agent-work/` is a live run's own artifacts (`.agent-work/<work-id>/**`:
#: launch orders, notes, crew handoffs, review results), which quote the clause
#: constantly because they are a record of what was said. Rooting the rglob at
#: the overlay directory itself is what expresses that -- there is no sibling to
#: filter back out, so no file is ever named.
#:
#: Suffixes are the adoption walk's own, imported rather than restated: one
#: definition of "a file that carries instruction text", used by both walks.
OVERLAY_DIR = ".agent-work/templates"


def _walk_dir(rel_dir: str, suffixes: tuple[str, ...]) -> list[str]:
    """Repo-relative paths of every file under `rel_dir` with one of `suffixes`.

    A directory-plus-suffix rule is the whole exclusion mechanism this file has.
    Returns [] when the directory is absent, so a consumer repo without the
    overlay collects and runs -- the floor test below is what makes an overlay
    that vanished HERE say so instead of quietly covering nothing.
    """
    base = ROOT / rel_dir
    if not base.is_dir():
        return []
    return sorted(
        p.relative_to(ROOT).as_posix()
        for p in base.rglob("*")
        if p.is_file() and p.suffix in suffixes
    )


SPEC_FILES = _walk_dir("specs", SPEC_SUFFIXES)
OVERLAY_FILES = _walk_dir(OVERLAY_DIR, INSTRUCTION_SUFFIXES)
GUARDED_FILES = INSTRUCTION_FILES + SPEC_FILES + OVERLAY_FILES


def _guard_texts() -> list[tuple[str, str, str, bool]]:
    """(file, where, text, is_whole_file) for everything the guard reads.

    Markdown and TOML are one whole-file chunk each, so a match's line number is
    meaningful and is reported. JSON is decomposed into its string leaves by the
    adoption suite's own extractor, each addressed by its JSON path, which
    localizes a match better than a line number would.

    The overlay is read through that same extractor, not a second one: its files
    are the skills templates, so a `.json` template must decompose into string
    leaves in the overlay exactly as it does under `skills/`.
    """
    out: list[tuple[str, str, str, bool]] = []
    for path in INSTRUCTION_FILES + OVERLAY_FILES:
        whole_file = not path.endswith(".json")
        for where, text in _instruction_texts(path):
            out.append((path, where, text, whole_file))
    for path in SPEC_FILES:
        out.append((path, path, (ROOT / path).read_text(encoding="utf-8"), True))
    return out


GUARD_TEXTS = _guard_texts()

# --------------------------------------------------------------------------- #
# The three patterns.
# --------------------------------------------------------------------------- #

#: A spine template's placeholder for an engine command line.
ENGINE_PLACEHOLDER_RE = re.compile(r"<engine>")

#: Measured on this tree the clause has THREE surface forms -- `CLI fallback:`
#: x10, `CLI fallback,` x4, `CLI fallback ` x1 -- so a colon-only pattern misses
#: a third of them. The separator is loosened the same way, so a re-spelling as
#: `CLI-fallback` is not a way out either.
CLI_FALLBACK_RE = re.compile(r"CLI[\s-]+fallback", re.IGNORECASE)

#: Engine verbs, as a command line writes them -- READ FROM THE ENGINE, never
#: hand-typed. Two patterns below are built from this alternation, so a verb
#: missing here is a hole in both at once.
#:
#: It was hand-typed once, for exactly one revision, and the list was wrong the
#: day it was written: 17 verbs against the engine's 18, missing `resume`, which
#: let `Second path: <cli> resume g1 --reason 'unblocked'.` through all four
#: patterns clean. `docs/agents/CREW_CONTEXT.md` states the rule that predicts
#: that outcome -- "Define a guard by its consumer's behaviour, not by a
#: hand-maintained list ... and the gap is silent."
#:
#: `_engine_verbs()` is the repo's existing oracle, imported rather than
#: re-derived for the same reason `INSTRUCTION_FILES` is: it hands
#: `checklist_engine.parse_args` a bogus verb and reads the choices argparse
#: itself prints, so the answer is the engine's own registry and cannot be a
#: stale copy of it. It needs no `SPINE_FILE`/`SPINE_ENGINE` env, which is what
#: makes it safe to call at import time here.
#:
#: Sorted so the compiled pattern is byte-identical run to run, and `re.escape`d
#: per verb so a future verb carrying a regex metacharacter cannot silently
#: break the alternation -- `flag-candidate` already carries a hyphen.
_ENGINE_VERBS = "|".join(re.escape(verb) for verb in sorted(_engine_verbs()))

#: The verb set the patterns below ACTUALLY apply, recovered from the alternation
#: itself rather than from whatever produced it. Read this way the tie test below
#: still holds if a later author replaces the derivation with a literal that
#: happens to agree today: what it compares against the engine is the string the
#: compiled patterns are built from.
ENGINE_VERBS = frozenset(
    re.sub(r"\\(.)", r"\1", token) for token in _ENGINE_VERBS.split("|")
)

#: A COMMAND-SHAPED reference to the engine script: an interpreter runs it, or a
#: path leads to it, or an argument follows it. Any one of the three is a
#: sentence telling an agent how to drive a checklist from a shell, which is the
#: behaviour this guard is about -- not the string `checklist_engine.py`, which
#: is also how the corpus legitimately names the engine as a component.
#:
#: The trailing-argument arm requires a LONG FLAG (`--file`), never a bare `--`.
#: Written the loose way it red-lighted `rewrites checklist_engine.py -- the very
#: engine driving it`, where the dashes are an ASCII em-dash and the sentence is
#: about editing the file, not running it. That false alarm was caught by
#: `TestTheInvocationPredicateItself` before this guard was ever offered as
#: evidence, which is what that class is for.
ENGINE_INVOCATION_RE = re.compile(
    r"""(?:(?:python3?|py)\s+(?:[^\s`'"]+\s+)?|[^\s`'"]*/)checklist_engine\.py"""
    r"""|checklist_engine\.py(?=[`'"\s]*(?:--[A-Za-z]|(?:""" + _ENGINE_VERBS + r""")\b))"""
)


#: A stand-in for a program name: any placeholder shape the corpus's authors
#: reach for. Angle-bracketed is the house idiom; the rest are the spellings a
#: fresh author arrives with.
_ENGINE_STANDIN = (
    r"(?:<[A-Za-z0-9_.-]+>"             # <engine>, <cli>, <engine-cli>, <script>
    r"|\{\{[^{}\n]+\}\}"                # {{engine}}
    r"|\{[A-Za-z0-9_.-]+\}"             # {engine}
    r"|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?"  # $ENGINE, ${ENGINE}
    r"|%[A-Za-z_][A-Za-z0-9_]*%)"       # %ENGINE%
)

#: A COMMAND LINE WHOSE PROGRAM NAME IS STOOD IN FOR. `<engine>` above is one
#: spelling; this is the class. The invariant is the SHAPE -- a stand-in,
#: IMMEDIATELY followed on the SAME LINE by an engine verb -- not the token.
#:
#: Two width decisions, both settled by measurement over the whole walk rather
#: than by argument. The bar either way is `TestCLIStaysAvailableNotDeprecated`
#: in `test_mcp_adoption.py`: a pattern that red-lights honest text is deleted
#: by the next author who trips it, after which there is no check at all.
#:
#:   * The stand-in is NOT required to spell "engine" or "cli". Requiring it
#:     would rebuild the very defect this pattern exists to remove, one level up:
#:     the class would then rest on two substrings instead of one token, and
#:     `<script> claim --session-id <id>` would walk straight through. Measured
#:     cost of the wider form: ZERO. Over 3098 texts it reports 26 matches at 23
#:     addresses, every one of them an address `<engine>` already reports.
#:   * The stand-in must be followed by HORIZONTAL whitespace directly -- no
#:     newline, and no closing backtick or quote in between. Both halves are
#:     load-bearing and both were measured:
#:       - allowing `\s` red-lights `heartbeat --session-id <id>` followed by
#:         `release --session-id <id>`, two adjacent lines of a usage block, on
#:         the strength of `<id>` being a session id;
#:       - allowing a closing backtick red-lights ordinary prose -- "the
#:         `<work-id>` record", "each `<gate>` block", "the `<path>` append".
#:     Both false alarms are pinned as must-not-match below, so a later loosening
#:     goes red rather than quiet.
#:
#: DO NOT OVER-TRUST THE CODE-SPAN ARGUMENT. The reason a closing backtick can be
#: treated as prose -- in Markdown a code span wraps the WHOLE command
#: (`` `<engine> attach <step>` ``), so a stand-in carrying its own closing
#: backtick is a noun rather than a program name -- is a MARKDOWN argument, and
#: most of this corpus is not Markdown. Measured on this tree: a stand-in
#: followed by horizontal whitespace and an ordinary English word occurs 40 times
#: across 25 files containing one (13 distinct sentences, each mirrored into
#: `skills/`, the overlay and `.baseline/`). 27 of those 40 sit in JSON template
#: imperatives, where backticks are not the house habit, and 31 of the 40 are not
#: inside a code span at all -- so on three quarters of the population the
#: argument offers no protection whatsoever.
#:
#: What actually holds this pattern's false-alarm count at zero is narrower and
#: more fragile than the code-span story: NONE of those 40 following words
#: happens to be an engine verb. Several verbs are common English -- `record`,
#: `block`, `append`, `start`, `current`, `release`, `skip`, `claim`, `attach` --
#: so "the `<gate>` record", "each `<work-id>` block" or "<skill-dir> release
#: notes" would fire, in Markdown or JSON alike, the day someone writes one. The
#: measured 0/3098 is real; it is a property of today's sentences, not a proof
#: about tomorrow's. If this pattern ever starts red-lighting honest text, the
#: fix is to require a following ARGUMENT (a flag, an id) rather than to loosen
#: the separator -- loosening the separator is what the must-not-match list above
#: already prices, and it costs more.
ENGINE_STANDIN_COMMAND_RE = re.compile(
    _ENGINE_STANDIN + r"[ \t]+(?:" + _ENGINE_VERBS + r")\b"
)


#: Engine long flags, READ FROM THE ENGINE for the same reason the verbs are.
#: `_engine_flags()` walks each subparser's own argparse help, so this cannot be
#: a stale copy of a registry that has moved on.
_ENGINE_FLAGS = "|".join(re.escape(flag) for flag in sorted(_engine_flags()))

#: The flag set the pattern below ACTUALLY applies, recovered from the alternation
#: itself rather than from whatever produced it -- the same guard against a later
#: author swapping the derivation for a literal that happens to agree today.
ENGINE_FLAGS = frozenset(
    re.sub(r"\\(.)", r"\1", token) for token in _ENGINE_FLAGS.split("|")
)

#: A COMMAND LINE WITH NO PROGRAM NAME AT ALL. Patterns 1-4 above all identify a
#: command by the thing you would type first -- the script, a path to it, or a
#: stand-in for it. This one drops that assumption, because a CLI lesson does not
#: need to name its program: the verbs and their real flags ARE the teaching, and
#: the program name is the one part a reader can infer.
#:
#: The live instance that motivated it, in `skills/workbench/references/checklist-engine.md`:
#:
#:     claim     --session-id <id> --claimed-by <role> [--worktree .] [--force --reason "..."]
#:     heartbeat --session-id <id>
#:     release   --session-id <id>
#:
#: No `checklist_engine.py`, no placeholder, no "fallback". Pattern 4 comes closest
#: and misses on ORDER: it wants stand-in then verb, and this is verb then stand-in.
#: All four ran green over this block while it taught the lease CLI in full.
#:
#: THE INVARIANT IS VERB-THEN-FLAG, one engine verb followed on the SAME LINE by
#: one engine long flag. Both halves are the engine's own registries, so neither
#: can drift into a hole. The 60-character window between them is what keeps the
#: two tokens parts of one command rather than two sentences that happen to share
#: a line.
#:
#: DIRECTION IS A MEASURED CHOICE, NOT AN OVERSIGHT. A reverse arm (flag, then
#: verb) was priced over the whole walk and rejected: 5 matches, of which the
#: honest-text cost is immediate -- `--reason is why the path changed. Do NOT
#: silently skip` fires on the English word "skip", not on the verb. The true
#: sites it added were already reported by the forward arm in the same file. The
#: bar here is the one this file applies throughout: a pattern that red-lights
#: honest text is deleted by the next author who trips it, after which there is
#: no check at all.
#:
#: THIS PATTERN FIRES ON GRAMMAR THE OTHERS WOULD CALL PROSE, AND THAT IS
#: DELIBERATE. `every \`claim --force\` writes previous_session_id` names an
#: operation rather than instructing anyone to run one -- but `--force` is CLI
#: syntax whichever grammatical role the phrase plays, and the door spells the
#: same thing `force=true`. Reading intent out of English is exactly the
#: predicate this file refuses to build (see `TestCLIStaysAvailableNotDeprecated`
#: in `test_mcp_adoption.py`, whose polarity predicates were measured wrong 9/10
#: and deleted). So the rule is syntactic: verb plus engine flag is CLI surface,
#: and the sweep rewrites it as the door call it means.
ENGINE_PROGRAMLESS_COMMAND_RE = re.compile(
    r"\b(?:" + _ENGINE_VERBS + r")\b[^\n]{0,60}?[ \t](?:" + _ENGINE_FLAGS + r")\b"
)


def _sites(pattern: re.Pattern[str]) -> list[str]:
    """Every match of `pattern`, addressed and excerpted. One line per match."""
    found: list[str] = []
    for path, where, text, whole_file in GUARD_TEXTS:
        for match in pattern.finditer(text):
            if whole_file:
                address = f"{where}:{text.count(chr(10), 0, match.start()) + 1}"
            else:
                address = where
            excerpt = text[max(0, match.start() - 40):match.end() + 40]
            excerpt = " ".join(excerpt.split())
            found.append(f"    {address}\n        ...{excerpt}...")
    return found


def _census() -> str:
    """What the walk actually covered. Every failure message carries it, so a
    finding can never be read without the size of the corpus it came from."""
    return (
        f"scanned {len(GUARD_TEXTS)} texts across {len(GUARDED_FILES)} files "
        f"({len(INSTRUCTION_FILES)} under skills/, {len(SPEC_FILES)} under specs/, "
        f"{len(OVERLAY_FILES)} under {OVERLAY_DIR}/)"
    )


def _report(what: str, sites: list[str]) -> str:
    return (
        f"{len(sites)} {what} survive in agent-facing instruction text "
        f"({_census()}).\n"
        f"The ruling, verbatim: \"{HUMAN_RULING}\"\n"
        f"Sites:\n" + "\n".join(sites)
    )


class TestTheWalkIsNotVacuous:
    """A guard that loops must assert what it looped over. A narrowed walk --
    a moved directory, a renamed suffix, an import that silently returned an
    empty list -- reports a clean corpus without ever reading an interesting
    file, and reads exactly like a passing guard. These floors are what make the
    absence assertions below mean something."""

    def test_the_walk_reaches_the_skills_corpus(self):
        assert len(INSTRUCTION_FILES) >= 60, (
            f"the instruction walk found only {len(INSTRUCTION_FILES)} files under skills/ "
            f"-- it covered 101 when this guard was written, so a count this low means the "
            f"walk narrowed and every absence assertion below is passing vacuously"
        )

    def test_the_walk_reaches_the_spec_corpus(self):
        assert len(SPEC_FILES) >= 1, (
            f"the walk found no {'/'.join(SPEC_SUFFIXES)} file under specs/ -- door doctrine "
            f"is authored there, so with this extension empty a fallback clause could be "
            f"written into specs/ with this guard green"
        )

    def test_the_walk_reaches_the_project_template_overlay(self):
        assert len(OVERLAY_FILES) >= 60, (
            f"the walk found only {len(OVERLAY_FILES)} instruction files under "
            f"{OVERLAY_DIR}/ -- it covered 113 when this surface was added (8ba1334c). "
            f"That overlay is what workbench doctrine tells an agent to instantiate "
            f"FROM, in preference to the bundled skills/ copy, so with this extension "
            f"empty a sweep of skills/ alone turns this whole guard green while the "
            f"copy an agent actually reads still hands over the second path"
        )

    def test_the_overlay_rule_does_not_reach_a_live_runs_own_artifacts(self):
        """The overlay rule is a directory rule, and this is what that buys. A
        run's own `.agent-work/<work-id>/**` artifacts quote the forbidden clause
        constantly and correctly -- they are a record of what was said. Widening
        the rule from `.agent-work/templates/` to `.agent-work/` would drag every
        one of them in and make the guard permanently, meaninglessly red."""
        strays = [p for p in GUARDED_FILES
                  if p.startswith(".agent-work/") and not p.startswith(OVERLAY_DIR + "/")]
        assert not strays, (
            f"{len(strays)} file(s) under .agent-work/ but outside {OVERLAY_DIR}/ entered "
            f"the walk -- those are a run's own records, not instruction handed to an "
            f"agent: {strays[:10]}"
        )

    def test_the_walk_yields_texts_not_just_paths(self):
        assert len(GUARD_TEXTS) >= 1800, (
            f"the walk yielded only {len(GUARD_TEXTS)} texts from "
            f"{len(GUARDED_FILES)} files -- it yielded 1007 when this guard was written "
            f"and 3098 once the {OVERLAY_DIR}/ surface was added (8ba1334c), so the "
            f"extractor is returning empty or collapsed content and the patterns below "
            f"are searching nothing"
        )


class TestTheInvocationPredicateItself:
    """`ENGINE_INVOCATION_RE` is the only pattern here that judges rather than
    matches: it must separate "run this from a shell" from "this file is the
    engine". Both directions are pinned in the assertion path, so a later edit
    to the pattern cannot quietly widen it into a false-alarm generator or
    narrow it into blindness.

    Measured on the corpus when this guard was written: 10 command forms caught,
    6 prose mentions left alone. The strings below are the SHAPES of those two
    populations, written out so the discrimination is testable without a corpus;
    the corpus census itself is in the failure messages above."""

    COMMAND_SHAPED = [
        "the CLI fallback: through `scripts/checklist_engine.py`.",
        "`python <skill-dir>/scripts/checklist_engine.py --file <checklist.json> <verb>`",
        "run checklist_engine.py advance g1 when the gate closes",
        "py /home/tommy/.claude/skills/constellation-workbench/scripts/checklist_engine.py",
        "./scripts/checklist_engine.py current",
        "checklist_engine.py --session-id <id> release",
    ]

    PROSE_ONLY = [
        "the engine rail string table (`checklist_engine.py`, #140)",
        "an epic that rewrites `checklist_engine.py` -- the very engine driving it",
        "Scripts: `checklist_engine.py`, `init_work_area.py`, `run_crew.py`",
        "nothing enforces the execution-time half in code -- `checklist_engine.py` does not",
        # The corpus shape closest to the line, raised by the g1 review and
        # decided HERE rather than left incidental: an archetype table cell
        # (`skills/write-a-skill/SKILL.md:20`) that asserts a drive path but
        # writes no command. It stays on the prose side -- see the module
        # docstring's "what this does not enforce" for the argument, which is
        # that separating it from "Scripts: `checklist_engine.py`" needs a
        # predicate that reads English, and that predicate is the one
        # `test_mcp_adoption.py` built, measured and deleted.
        "a `templates/*.json` checklist driven through `checklist_engine.py` (`commander`)",
    ]

    def test_catches_every_command_shape(self):
        missed = [s for s in self.COMMAND_SHAPED if not ENGINE_INVOCATION_RE.search(s)]
        assert not missed, f"invocation pattern missed a command shape: {missed}"

    def test_leaves_a_bare_component_mention_alone(self):
        flagged = [s for s in self.PROSE_ONLY if ENGINE_INVOCATION_RE.search(s)]
        assert not flagged, (
            f"invocation pattern red-lighted prose that names the engine as a component "
            f"rather than telling an agent to run it: {flagged}"
        )

    def test_the_clause_pattern_reads_every_measured_surface_form(self):
        forms = ["CLI fallback:", "CLI fallback,", "CLI fallback ", "CLI-fallback:", "cli fallback:"]
        missed = [f for f in forms if not CLI_FALLBACK_RE.search(f)]
        assert not missed, (
            f"clause pattern is punctuation-sensitive and misses {missed} -- the three "
            f"forms measured in this corpus were 'CLI fallback:' x10, 'CLI fallback,' x4 "
            f"and 'CLI fallback ' x1, so a pattern blind to one of them is blind to a "
            f"third of its targets"
        )


class TestTheVerbSetIsTheEnginesOwn:
    """The tie that stops this file's verb alternation from drifting from the
    engine's registry. It is here because the drift already happened, on day one:
    the alternation was hand-typed with 17 verbs while the engine registered 18,
    and the missing one -- `resume` -- let
    `Second path: <cli> resume g1 --reason 'unblocked'.` pass all four patterns
    clean. That is precisely the class this file exists to catch, and it was
    inside none of the docstring's declared limits.

    `docs/agents/CREW_CONTEXT.md`, Verification Discipline, names the shape:
    "Define a guard by its consumer's behaviour, not by a hand-maintained list.
    A list of characters, filenames or call sites drifts from the predicate the
    code actually applies, and the gap is silent." So the fix is the derivation
    above, and these are the assertions that keep the two sides tied.

    Both directions are asserted BEHAVIOURALLY -- every verb the engine has is
    run through the pattern as a command line, and a word the engine does not
    have is run through it too -- rather than by comparing two strings. A string
    comparison would still pass if the alternation were later rewritten as a
    literal that happens to agree today."""

    def test_every_verb_the_engine_has_is_caught_as_a_stood_in_for_command(self):
        missed = sorted(v for v in _engine_verbs()
                        if not ENGINE_STANDIN_COMMAND_RE.search(f"<engine> {v} g1"))
        assert not missed, (
            f"the engine registers {sorted(missed)} but this file's pattern does not catch a "
            f"command line using it -- that is the exact gap `resume` opened: a verb the "
            f"engine really has, written in a spine template behind a stand-in, reported "
            f"clean. The alternation must be derived from the engine, never hand-typed"
        )

    def test_the_verb_set_is_the_engines_own_registry(self):
        engine = _engine_verbs()
        assert ENGINE_VERBS == engine, (
            f"this file's verb set has drifted from the engine's argparse registry.\n"
            f"  in the engine, missing here: {sorted(engine - ENGINE_VERBS)}\n"
            f"  here, not in the engine:     {sorted(ENGINE_VERBS - engine)}\n"
            f"A verb in the first list is a live evasion route; a verb in the second is a "
            f"pattern arm matching text no engine command can contain"
        )

    def test_the_engine_has_all_eighteen_verbs_todays_pin_expects(self):
        # CONTROL for the tie above, following test_mcp_adoption.py's
        # `test_engine_has_all_eighteen_verbs_todays_pins_expect`: pin the count
        # too, so the two sides cannot shrink together unnoticed. A derivation
        # that started returning the empty set would satisfy the tie and catch
        # nothing.
        assert len(ENGINE_VERBS) == 18, (
            f"the engine's verb registry now has {len(ENGINE_VERBS)} verbs, not the 18 "
            f"measured when this tie was written: {sorted(ENGINE_VERBS)}. If the engine "
            f"really changed, re-measure this file's address counts and update this pin; "
            f"if it did not, the derivation is reading the wrong thing"
        )

    def test_a_word_the_engine_does_not_have_is_not_a_command(self):
        assert not ENGINE_STANDIN_COMMAND_RE.search("<engine> frobnicate g1"), (
            "the pattern fires on any word after a stand-in, so it is no longer reading "
            "the engine's verb set at all and its false-alarm measurement is void"
        )


class TestTheStandInCommandPredicateItself:
    """`ENGINE_STANDIN_COMMAND_RE` is the widening, and a widening is judged in
    BOTH directions or not at all. Too narrow is a live evasion route; too wide
    is a check the next author deletes, after which there is nothing.

    The catches below are not invented shapes. The first three are the exact
    strings the g1 review verified pass all three g1 patterns clean; the fourth
    is the alias form it found beside a declared limit; the rest are the residual
    a "the token must say engine or cli" version would have left open. The
    must-not-match list is the measured false-alarm cost of two loosenings that
    look harmless -- allowing a newline before the verb, and allowing a closing
    backtick after the stand-in -- each pinned so a later edit that reaches for
    the obvious `\\s` or `` [`'"]* `` goes red immediately.

    Measured at 8ba1334c: over 3098 texts this pattern adds ZERO addresses the
    other three patterns did not already report. Its false-alarm cost on this
    corpus is nil, and that is the only reason it is allowed to be this wide."""

    STAND_IN_COMMANDS = [
        # Verified by the g1 review as passing every g1 pattern clean.
        "Second path: <cli> claim --session-id <commander-session-id> --claimed-by commander.",
        "If the door is down: <engine-cli> advance g1 --why 'gate closed'.",
        "Fallback command line: {{engine}} release --session-id <work-id>.",
        # The alias form, whose definition site the invocation pattern catches
        # but whose USE site nothing did.
        "Then run `$ENGINE claim --session-id <id>`",
        # The residual a name-constrained version leaves open: a stand-in that
        # spells neither "engine" nor "cli".
        "restore the second path with <script> claim --session-id <id>",
        # The g1b review's finding, pinned as a fixture in its own right. This
        # line passed ALL FOUR patterns while the verb alternation was a
        # hand-typed 17-verb string missing `resume`, which the engine has had
        # all along. The derivation below is what closes it, and this fixture is
        # what keeps it closed if the derivation is ever replaced by a literal.
        "Second path: <cli> resume g1 --reason 'unblocked'.",
        # Other placeholder dialects an author arrives with.
        "single-brace template: {engine} current",
        "windows: %ENGINE% advance g1 --why 'gate closed'",
        # The corpus's own live shapes, which must keep matching.
        "the CLI `<engine> block`, recording the crew id",
        "CLI fallback `<engine> attach <step> --type user-decision`",
    ]

    NOT_A_STAND_IN_COMMAND = [
        # Two adjacent lines of a usage block. `<id>` is a session id, not a
        # program; `release` opens the NEXT line. This is the whole measured
        # cost of writing the separator as `\s` instead of `[ \t]`, and it is a
        # real site: skills/workbench/references/checklist-engine.md:92.
        "heartbeat --session-id <id>\nrelease --session-id <id>",
        # A code-spanned placeholder used as a NOUN. In Markdown a code span
        # wraps the whole command, so a stand-in carrying its own closing
        # backtick is prose. This is the cost of allowing `[`'\"]*` after the
        # stand-in -- three honest sentences, none of which exists in the corpus
        # today and any of which a future author might write.
        "the `<work-id>` record is written by the engine",
        "each `<gate>` block names its own postconditions",
        "the `<path>` append is idempotent",
    ]

    def test_catches_every_stand_in_command_shape(self):
        missed = [s for s in self.STAND_IN_COMMANDS
                  if not ENGINE_STANDIN_COMMAND_RE.search(s)]
        assert not missed, (
            f"stand-in pattern missed a command shape, so the 'engine command line in a "
            f"spine template' class is back to resting on the exact spelling `<engine>`: "
            f"{missed}"
        )

    def test_leaves_a_placeholder_used_as_prose_alone(self):
        flagged = [s for s in self.NOT_A_STAND_IN_COMMAND
                   if ENGINE_STANDIN_COMMAND_RE.search(s)]
        assert not flagged, (
            f"stand-in pattern red-lighted text where the placeholder is a noun, not a "
            f"program name -- a pattern that fires on honest sentences is deleted by the "
            f"next author who trips it: {flagged}"
        )

    def test_the_three_verified_misses_are_the_ones_pinned(self):
        """The g1 review's finding, stated as an assertion rather than a claim in
        a document: each of these was reproduced passing all three g1 patterns,
        and each is now caught. Deleting the widening without deleting this test
        is not possible."""
        g1_patterns = (ENGINE_PLACEHOLDER_RE, CLI_FALLBACK_RE, ENGINE_INVOCATION_RE)
        for respelling in self.STAND_IN_COMMANDS[:3]:
            assert not any(p.search(respelling) for p in g1_patterns), (
                f"this string is supposed to be one the three original patterns MISS -- "
                f"if it now matches one of them, the review's finding has been "
                f"misrecorded here: {respelling!r}"
            )
            assert ENGINE_STANDIN_COMMAND_RE.search(respelling), (
                f"the widening does not catch a respelling the review verified as a live "
                f"evasion route: {respelling!r}"
            )


class TestTheProgramlessCommandPredicateItself:
    """`ENGINE_PROGRAMLESS_COMMAND_RE` widens past the program name, so like every
    widening in this file it is judged in BOTH directions.

    The catches are not invented. The first three are the real lease block from
    `skills/workbench/references/checklist-engine.md`, which ran green against all
    four earlier patterns while teaching the lease CLI in full; the rest are the
    live sites the first run over this corpus reported.

    The must-not-match list is the measured false-alarm cost. Two entries matter
    most: an engine verb used as an ordinary English word near an unrelated flag,
    and a verb and a flag that merely share a line as separate sentences. Both are
    what the 60-character window and the verb-then-flag order are buying."""

    PROGRAMLESS_COMMANDS = (
        'claim     --session-id <id> --claimed-by <role> [--worktree .]',
        "heartbeat --session-id <id>",
        "release   --session-id <id>",
        "attest <task> --cond <id> --which postconditions --evidence <evidence-id>",
        "attach <active-gate> --type refresh-request --field seam=<active-gate>",
        "waive gN-integrate --cond <id> --authority human --reason \"...\"",
        "advance --why 'the gate is closed'",
        "amend --delta <file>",
        "consolidate --verdict APPROVE",
        "record --result pass",
        "claim --force",
    )

    NOT_A_PROGRAMLESS_COMMAND = (
        # An engine verb as plain English, with a flag belonging to another tool.
        "resume a recoverable attempt (run_crew.py --resume <session>)",
        "retire it with --abandon <session> --relaunch",
        # A verb and an engine flag on one line, but as two separate sentences --
        # further apart than any command line puts its own tokens.
        "record what you observed in the episode store, and remember that the "
        "engine stamps every takeover for audit; the --reason it carries is durable",
        # The verb alone, with no flag at all: how the corpus legitimately names
        # an operation once the flags are gone. The sweep's OUTPUT must pass.
        "attach the review-result evidence, then advance the gate",
        "a forced claim (spine_lease with force=true) records the prior session",
        # A flag-shaped token that is not an engine flag.
        "start --verbose",
    )

    def test_catches_every_programless_command_shape(self):
        missed = [c for c in self.PROGRAMLESS_COMMANDS
                  if not ENGINE_PROGRAMLESS_COMMAND_RE.search(c)]
        assert not missed, (
            f"the programless pattern missed a command shape, so a CLI lesson that "
            f"simply omits the script name is back to being invisible to this guard: "
            f"{missed}"
        )

    def test_leaves_prose_and_swept_text_alone(self):
        flagged = [c for c in self.NOT_A_PROGRAMLESS_COMMAND
                   if ENGINE_PROGRAMLESS_COMMAND_RE.search(c)]
        assert not flagged, (
            f"the programless pattern red-lighted text that is not a command line -- a "
            f"pattern that fires on honest sentences is deleted by the next author who "
            f"trips it, and the last two entries are the shape the sweep PRODUCES, so "
            f"firing on them would make the corpus unfixable: {flagged}"
        )

    def test_the_four_earlier_patterns_miss_what_this_one_catches(self):
        """The gap, stated as an assertion rather than a claim in a document. The
        real lease block passed all four earlier patterns; if that stops being
        true, this pattern's justification has changed and should be re-read."""
        earlier = (ENGINE_PLACEHOLDER_RE, CLI_FALLBACK_RE, ENGINE_INVOCATION_RE,
                   ENGINE_STANDIN_COMMAND_RE)
        for command in self.PROGRAMLESS_COMMANDS[:3]:
            assert not any(pattern.search(command) for pattern in earlier), (
                f"this string is supposed to be one the four earlier patterns MISS -- "
                f"if it now matches one, the gap this pattern was added for has been "
                f"misrecorded here: {command!r}"
            )
            assert ENGINE_PROGRAMLESS_COMMAND_RE.search(command), (
                f"the widening does not catch the live block it was added for: {command!r}"
            )


class TestTheFlagSetIsTheEnginesOwn:
    """The same tie as `TestTheVerbSetIsTheEnginesOwn`, for the other registry the
    programless pattern rests on. A flag missing here is a live evasion route, and
    flags are added to a subparser far more often than verbs are added to the
    engine -- so this side drifts faster, not slower."""

    def test_every_flag_the_engine_has_is_caught_in_a_command_line(self):
        missed = sorted(f for f in _engine_flags()
                        if not ENGINE_PROGRAMLESS_COMMAND_RE.search(f"advance {f} x"))
        assert not missed, (
            f"the engine accepts {missed} but this file's pattern does not catch a "
            f"command line using it. The alternation must be derived from the engine, "
            f"never hand-typed"
        )

    def test_the_flag_set_is_the_engines_own_registry(self):
        engine = _engine_flags()
        assert ENGINE_FLAGS == engine, (
            f"this file's flag set has drifted from the engine's argparse registry.\n"
            f"  in the engine, missing here: {sorted(engine - ENGINE_FLAGS)}\n"
            f"  here, not in the engine:     {sorted(ENGINE_FLAGS - engine)}"
        )

    def test_the_flag_set_is_not_empty(self):
        # CONTROL for the tie above, mirroring the verb-count pin: a derivation
        # that started returning the empty set would satisfy the tie and catch
        # nothing. `_engine_flags` asserts non-empty itself; this pins that the
        # PATTERN was built from a non-empty one.
        assert len(ENGINE_FLAGS) >= 20, (
            f"only {len(ENGINE_FLAGS)} engine flags reached the pattern; the derivation "
            f"has quietly stopped reading argparse's help"
        )


class TestNoSecondPathReachesAnAgent:
    """The guard proper. Each of these asserts the ABSENCE of the text itself --
    never the presence of a sentence describing the rule, which is the failure
    mode this whole epic is about: a corpus can carry a perfect statement of the
    doctrine in one paragraph and violate it in the next."""

    def test_no_engine_placeholder_token_reaches_an_agent(self):
        sites = _sites(ENGINE_PLACEHOLDER_RE)
        assert not sites, _report(
            "`<engine>` placeholder tokens -- a stand-in for an engine command line that "
            "init_work_area.py deliberately never resolves, so each one reaches an agent "
            "unresolved --",
            sites,
        )

    def test_no_stood_in_for_command_line_reaches_an_agent(self):
        sites = _sites(ENGINE_STANDIN_COMMAND_RE)
        assert not sites, _report(
            "stood-in-for engine command lines -- a placeholder standing where the "
            "program name goes, followed on the same line by an engine verb, which is "
            "what a command line in a spine template looks like when the script's own "
            "name is never written --",
            sites,
        )

    def test_no_cli_fallback_clause_reaches_an_agent(self):
        sites = _sites(CLI_FALLBACK_RE)
        assert not sites, _report(
            "`CLI fallback` clauses -- each one hands an agent a second path to the "
            "checklist engine beside the MCP door --",
            sites,
        )

    def test_no_engine_invocation_reaches_an_agent(self):
        sites = _sites(ENGINE_INVOCATION_RE)
        assert not sites, _report(
            "command-shaped `checklist_engine.py` invocations -- the rename-around that "
            "survives deleting the phrase, because the runnable command is what the "
            "sentence is for --",
            sites,
        )

    def test_no_programless_command_line_reaches_an_agent(self):
        sites = _sites(ENGINE_PROGRAMLESS_COMMAND_RE)
        assert not sites, _report(
            "engine command lines with no program name -- an engine verb followed on the "
            "same line by an engine long flag, which is what a CLI lesson looks like once "
            "it stops naming the script, and which all four patterns above read as prose --",
            sites,
        )
