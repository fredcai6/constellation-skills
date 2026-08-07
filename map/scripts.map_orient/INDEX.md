# scripts.map_orient
scripts/map_orient.py, 1732 lines, 17 holes

Orient an agent against a repo's architecture map -- or REPORT that it cannot.

The deficiency this closes is **primacy and contract, not path**. Resolving a
path to `docs/architecture/` is the easy half and several repos already do it.
The half that has to hold is the **reported degraded mode**: degrading is fine,
degrading *silently* is refused. Degraded is the COMMON case -- most repos,
including this one, have no `docs/architecture/` at all -- so the degraded
record is a first-class output, not an error path.

Subcommands
-----------
    map_orient.py orient             --root ABS --work-id ID [--entrypoint REL]
                                     [--substitute REL ...] [--unmapped TEXT ...]
                                     [--escalation TEXT]
    map_orient.py verify-orientation --root ABS --work-id ID [--report-only]
    map_orient.py verify-frame       --root ABS --work-id ID [--report-only]
    map_orient.py --self-test

`--report-only` is the gate-vs-report dial: the verdict printed is identical,
only its blocking-ness moves, so a ruling to gate or un-gate a step is a flag
flip in the template's command string rather than a rebuild here.

Where the two checks are wired, and why ASYMMETRICALLY
------------------------------------------------------
`verify-orientation` is a command postcondition at the Commander spine's
**context** step; `verify-frame` is one at the **plan** step. `verify-frame`
must NEVER run at context: no frame exists there (context precedes `understand`
and `plan`), and the only way to make it pass there is to let an ABSENT frame
pass -- which is precisely the refusal the whole check is built on. The road not
to take, recorded because the cheap symmetric resolution is tempting and a cold
critic already BLOCKed one plan over it: if `verify-frame` ever has to be
context-safe, give it a step-scoped mode; never a vacuous pass.

Exit-code vocabulary (FROZEN)
-----------------------------
The engine records only ``{cmd, exit, shell}`` for a command check and
**discards stdout**, so for anything downstream of the engine the exit code is
the only signal that survives. Three codes are already spoken for by machinery
this module does not control, and a mistyped flag must never be
indistinguishable from a truthful verdict:

    1    an unhandled Python traceback
    2    `argparse` usage error (unknown flag, missing argument)
    126  a command found but not executable
    127  the engine's synthesized "no POSIX shell found"

So every semantic code sits **above** the traceback/argparse range and
**below** the shell range -- an occupied-code-free band:

    0    contract satisfied: RESOLVED, or a DEGRADED record fully discharged,
         or a frame whose citations resolve
    10   the map contract is NOT discharged -- a DEGRADED record missing at
         least one of `substitutes` / `unmapped` / `escalation` (or one of them
         filler), or a frame whose citations do not resolve (`verify-frame`)
    11   UNRESOLVABLE-ROOT -- could not look: `--root` is not a proven repo root
    12   a required INPUT DOCUMENT is missing or unusable: the receipt, or --
         for `verify-frame` -- the mission frame itself
    13   `--self-test` falsification floor failed

`verify-frame` adds NO new codes. Two of the frozen ones carry a slightly wider
reading, stated here rather than left implicit: 12 was "the receipt is missing"
and is now "a required input document is missing", and 10 was "the degraded
record is undischarged" and is now "the map contract is undischarged". Both are
the same verdict about the same contract, reached one document later.

`0` is the only success code; `10`-`13` are the semantic verdicts; nothing this
module returns can be confused with `1`, `2`, `126`, or `127`.

Reserved stdout first line
--------------------------
The first line of stdout is ALWAYS exactly one reserved literal -- never blank,
never a bare count:

    RESOLVED  DEGRADED-NO-MAP  DEGRADED-EMPTY-MAP  DEGRADED-UNPARSEABLE
    UNRESOLVABLE-ROOT                      (the five `orient` verdicts)
    RECEIPT-MISSING                        (no usable receipt)
    FRAME-OK  FRAME-MISSING  FRAME-REFUSED (`verify-frame`)

The agent runs `orient` itself, so stdout is real there. The engine only ever
sees the exit code, which is why the table above carries the contract.

`orient` never prints an anchor id, and `verify-frame` echoes back only ids the
frame it is checking already contains. If the tool handed over the ids, citing
one would stop being evidence the map was read -- an agent could paste back what
the tool told it. The proof has to come from somewhere the tool did not give.

Resolution rule (ordered; first hit wins; EVERY candidate is still recorded)
----------------------------------------------------------------------------
    1. `--entrypoint REL`, when given
    2. `docs/architecture/generated/map.json` -- parses, >=1 `nodes[].id`
    3. `docs/architecture/index.md`
    4. `docs/architecture/` carrying >=1 non-empty `packets/*.md`

All four are evaluated and recorded in `candidates_tried[]` even after an
earlier one hits: the receipt is a delivery record of what was looked for, not
a first-hit lookup log.

RESOLVED requires CITABLE CONTENT, not mere existence. Anchors are extracted
with a deliberately format-agnostic token scan::

    \b(struct|capability|event|constraint|assumption|claim|decision):[A-Za-z0-9_.\-]+\b

>=1 unique real id makes a candidate citable. A `<placeholder>` cannot match
(``<`` is outside the id character class), so a scaffolded-but-unfilled
template yields nothing and reads DEGRADED-UNPARSEABLE. This is NOT coupled to
`build_architecture_map.parse_packet` on purpose: that parser requires this
repo's bold-field packet template, while the one repo with a real map
(f1Brainz) writes YAML fences, so the strict parser returns ZERO nodes on it
(measured: 0 parsed / 16 failed). A false RESOLVED is strictly worse than an
honest DEGRADED -- it satisfies the entire contract on a map with no content.

"Could not look" vs "looked and found nothing"
----------------------------------------------
UNRESOLVABLE-ROOT requires a POSITIVE repo-root proof to fail, never an absence
test: `.git` present at the root, or `git -C <root> rev-parse --show-toplevel`
succeeding AND naming that same root. A bare non-repo directory is therefore
UNRESOLVABLE-ROOT ("I could not look"), not DEGRADED-NO-MAP ("I looked and the
map is not there"). Those two differ in exactly one bit and must never collapse.

Receipt schema (`.agent-work/<work-id>/map-orientation.json`)
------------------------------------------------------------
    schema_version   int     this file's schema revision
    work_id          str     the work id the receipt belongs to
    root             str     absolute repo root, posix separators
    mode             str     one of the five reserved `orient` verdicts
    entrypoint       str?    repo-relative path of the winning candidate, else null
    anchor_count     int     unique citable anchor ids at the entrypoint (0 when degraded)
    candidates_tried list    [{order, kind, path, exists, outcome, anchor_count, note}]
    substitutes      list    [{path, content_hash, source}] -- read INSTEAD of a map
    fallbacks_probed list    [{path, exists, content_hash}] -- the FIXED fallback
                             set, as the filesystem answers it
    unmapped         list    [str] -- what stayed unmapped, stated plainly
    escalation       str?    what is being escalated and to whom
    emitted_at       str     UTC ISO-8601 timestamp

`substitutes` are **hash-pinned**: the sha256 of each substitute's content is
recorded here so a later frame check compares against this committed prior
declaration rather than a same-breath assertion. A substitute that could not be
read carries `content_hash: null` and **refuses** the discharge -- the pin is
validated by SHAPE (64 hex chars), so no sentinel, typo, or truncated digest
can stand in for one. A single mistyped path must not be able to satisfy the
whole contract.

Each substitute also carries a provenance `source`: `known-fallback` when the
path is in the fixed corpus set (`README.md`, `AGENTS.md`, `CLAUDE.md`, a
`docs/` index) AND present on disk, `agent-declared` otherwise. `orient` probes
that whole set independently into `fallbacks_probed`. This converts HALF of the
degraded check's self-attestation into an oracle the agent does not author --
whether one of those paths resolved is the filesystem's answer, not the agent's.
It does **not** close the gap: the agent still chooses what to declare, and
anything outside the set stays labelled unverified. Do not describe it as making
the degraded check sound; it converts part of it.

Honest limits
-------------
- The token scan proves citable *shape*, not correctness: a well-formed example
  id inside prose is indistinguishable from a real anchor. It refuses empty and
  unfilled maps; it does not audit a populated one.
- Nothing here judges whether the map is accurate, current, or complete. Map
  freshness and drift are the Cartographer's job.
- The degraded record's *content* is prose the agent writes. This module can
  only check the three fields are present and are not filler -- it cannot tell a
  thoughtful substitute list from a lazy one. That judgment stays human.
- When `git` is unavailable and `.git` is absent, the verdict is
  UNRESOLVABLE-ROOT by design. Absence of proof is reported as "could not
  look", never silently upgraded to a map verdict.

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, datetime.datetime, datetime.timezone, hashlib, json, os, pathlib.Path, re, subprocess, sys, typing.Sequence
imported by: none found

```python
SCHEMA_VERSION = 1
MODE_RESOLVED = 'RESOLVED'
MODE_DEGRADED_NO_MAP = 'DEGRADED-NO-MAP'
MODE_DEGRADED_EMPTY_MAP = 'DEGRADED-EMPTY-MAP'
MODE_DEGRADED_UNPARSEABLE = 'DEGRADED-UNPARSEABLE'
MODE_UNRESOLVABLE_ROOT = 'UNRESOLVABLE-ROOT'
RECEIPT_MISSING = 'RECEIPT-MISSING'
FRAME_OK = 'FRAME-OK'
FRAME_MISSING = 'FRAME-MISSING'
FRAME_REFUSED = 'FRAME-REFUSED'
ORIENT_MODES = (MODE_RESOLVED, MODE_DEGRADED_NO_MAP, MODE_DEGRADED_EMPTY_MAP, MODE_DEGRADED_UNPARSEABL...
RESERVED_FIRST_LINES = ORIENT_MODES + (RECEIPT_MISSING, FRAME_OK, FRAME_MISSING, FRAME_REFUSED)
EXIT_OK = 0
EXIT_DEGRADED_UNDISCHARGED = 10
EXIT_UNRESOLVABLE_ROOT = 11
EXIT_RECEIPT_UNUSABLE = 12
EXIT_SELF_TEST_FAILED = 13
SEMANTIC_EXIT_CODES = (EXIT_DEGRADED_UNDISCHARGED, EXIT_UNRESOLVABLE_ROOT, EXIT_RECEIPT_UNUSABLE, EXIT_SELF_T...
OCCUPIED_EXIT_CODES = (1, 2, 126, 127)
ANCHOR_RE = re.compile('\\b(?:struct|capability|event|constraint|assumption|claim|decision):[A-Za-z...
MAP_DIR = 'docs/architecture'
GENERATED_MAP = 'docs/architecture/generated/map.json'
INDEX_MD = 'docs/architecture/index.md'
OUTCOME_HIT = 'hit'
OUTCOME_ABSENT = 'absent'
OUTCOME_EMPTY = 'empty'
OUTCOME_UNPARSEABLE = 'unparseable'
FILLER_VALUES = frozenset({'-', '--', 'n/a', 'n\\a', 'na', 'none', 'nil', 'null', 'tbd', 'todo', '?', '...
CONTENT_HASH_RE = re.compile('^[0-9a-f]{64}$')
RECEIPT_REQUIRED_FIELDS = ('schema_version', 'work_id', 'root', 'mode', 'entrypoint', 'anchor_count', 'candidates...
FRAME_NAME = 'MISSION_FRAME.md'
PATH_TOKEN_RE = re.compile('[A-Za-z0-9_.\\-]+(?:/[A-Za-z0-9_.\\-]+)*\\.[A-Za-z0-9]{1,8}\\b')
SOURCE_SUFFIXES = frozenset({'.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java', ...
KNOWN_FALLBACKS = ('README.md', 'AGENTS.md', 'CLAUDE.md', 'docs/index.md', 'docs/README.md')
KNOWN_FALLBACK_SET = frozenset((p.lower() for p in KNOWN_FALLBACKS))
LABEL_KNOWN_FALLBACK = 'known-fallback'
LABEL_AGENT_DECLARED = 'agent-declared'
SUBSTITUTE_LABELS = (LABEL_KNOWN_FALLBACK, LABEL_AGENT_DECLARED)
```

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [Candidate](Candidate.md) class: One entrypoint the resolver looked for, and what it found there.
- [RootProof](RootProof.md) class: Whether `--root` was POSITIVELY proven to be a repo root, and by what.
- [Orientation](Orientation.md) class: HOLE: no docstring
- [scan_anchors](scan_anchors.md) function: PURE. Unique citable anchor ids in `text`, in first-seen order.
- [candidate_is_citable](candidate_is_citable.md) function: PURE. A candidate counts as a hit ONLY when it yields citable content.
- [candidate_outcome](candidate_outcome.md) function: PURE. `hit` | `absent` | `empty` | `unparseable`.
- [prove_repo_root](prove_repo_root.md) function: PURE. POSITIVE repo-root proof -- never an absence test (#265).
- [_same_path](_same_path.md) function: PURE. Case- and separator-insensitive path identity (Windows-safe).
- [determine_mode](determine_mode.md) function: PURE. The reserved verdict literal for this orientation.
- [build_orientation](build_orientation.md) function: PURE. Fold the root proof and every candidate into one verdict.
- [classify_generated_map](classify_generated_map.md) function: PURE. (has_content, anchors, note) for a `generated/map.json` candidate.
- [classify_markdown](classify_markdown.md) function: PURE. (has_content, anchors, note) for a markdown candidate.
- [classify_packets](classify_packets.md) function: PURE. (has_content, anchors, note) for the `packets/*.md` candidate.
- [is_filler](is_filler.md) function: PURE. True when a field is absent, empty, a placeholder, or says nothing.
- [is_content_hash](is_content_hash.md) function: PURE. True only for a real sha256 hex digest.
- [substitute_problems](substitute_problems.md) function: PURE. Why the declared substitutes fail to pin; empty means they pin.
- [substitutes_declared](substitutes_declared.md) function: PURE. >=1 substitute, each with a real path AND a real sha256 pin.
- [unmapped_declared](unmapped_declared.md) function: PURE. >=1 plainly-stated thing that stayed unmapped.
- [escalation_declared](escalation_declared.md) function: PURE. A real statement of what is being escalated, to whom.
- [degraded_record_is_complete](degraded_record_is_complete.md) function: PURE. A DEGRADED record discharges ONLY with all three declarations.
- [missing_degraded_fields](missing_degraded_fields.md) function: PURE. Which of the three declarations are missing or filler.
- [receipt_problems](receipt_problems.md) function: PURE. Structural problems with a receipt; empty means well-formed.
- [verify_verdict](verify_verdict.md) function: PURE. (reserved first line, exit code, problems) for `verify-orientation`.
- [normalize_cited_path](normalize_cited_path.md) function: PURE. Comparable form of a cited path: posix separators, lowercased.
- [cited_paths](cited_paths.md) function: PURE. Unique path-shaped tokens in `text`, in first-seen order.
- [is_source_path](is_source_path.md) function: PURE. True when a cited path names a code file.
- [cited_source_paths](cited_source_paths.md) function: PURE. The cited paths that are code files.
- [classify_substitute](classify_substitute.md) function: PURE. Which oracle backs this substitute.
- [substitute_label](substitute_label.md) function: PURE. The label on a receipt substitute; unlabelled reads as unverified.
- [declared_substitute_paths](declared_substitute_paths.md) function: PURE. Normalized paths of every substitute the receipt hash-pinned.
- [frame_verdict](frame_verdict.md) function: PURE. (reserved first line, exit code, problems) for `verify-frame`.
- [render_frame_report](render_frame_report.md) function: PURE. stdout lines; line 0 is always a reserved literal.
- [exit_code_for](exit_code_for.md) function: PURE. The frozen exit code for a verdict.
- [build_receipt](build_receipt.md) function: PURE. The receipt document -- schema documented in the module docstring.
- [render_orient_report](render_orient_report.md) function: PURE. stdout lines; line 0 is always the reserved verdict literal.
- [render_verify_report](render_verify_report.md) function: PURE. stdout lines; line 0 is always a reserved literal.
- [_read_text](_read_text.md) function: HOLE: no docstring
- [_rel](_rel.md) function: HOLE: no docstring
- [sha256_of](sha256_of.md) function: Content hash used to pin a substitute; None when unreadable.
- [git_toplevel](git_toplevel.md) function: `git -C <root> rev-parse --show-toplevel`, or None when it cannot answer.
- [probe_root](probe_root.md) function: Impure edge feeding the pure `prove_repo_root`.
- [_candidate_from_file](_candidate_from_file.md) function: HOLE: no docstring
- [collect_candidates](collect_candidates.md) function: Impure edge: evaluate EVERY candidate, in order, and record each one.
- [receipt_path](receipt_path.md) function: HOLE: no docstring
- [frame_path](frame_path.md) function: HOLE: no docstring
- [map_inventory](map_inventory.md) function: Impure edge: every anchor id the resolved entrypoint actually carries.
- [probe_fallbacks](probe_fallbacks.md) function: Impure edge: which of the FIXED fallback set actually exist on disk.
- [write_receipt](write_receipt.md) function: HOLE: no docstring
- [pin_substitutes](pin_substitutes.md) function: Hash-pin each declared substitute so a later frame check has a prior.
- [_now_iso](_now_iso.md) function: HOLE: no docstring
- [cmd_orient](cmd_orient.md) function: HOLE: no docstring
- [cmd_verify_orientation](cmd_verify_orientation.md) function: HOLE: no docstring
- [_gate](_gate.md) function: The gate-vs-report dial, as a FLAG FLIP rather than a rebuild.
- [cmd_verify_frame](cmd_verify_frame.md) function: HOLE: no docstring
- [_check](_check.md) function: HOLE: no docstring
- [_cand](_cand.md) function: HOLE: no docstring
- [self_test](self_test.md) function: Falsification floor: assert the decision layer refuses what it must.
- [build_parser](build_parser.md) function: HOLE: no docstring
- [_add_report_only](_add_report_only.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
