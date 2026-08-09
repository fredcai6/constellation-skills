#!/usr/bin/env python3
"""measure_overread.py -- count STRUCTURAL READS per agent run in a transcript.

Built for issue-227 gate g1 (epic-226). Epic-226's headline claim is "~8.8k
tokens/run of scaffolding over-read" -- agents re-reading spine.json and
checklist_engine.py because the engine's `current` output doesn't tell them
enough (see the epic's grounding excursion,
.agent-work/archive/2026-07-24-explore-design-thrust/excursions/x1-overread-RESULT.md,
run against real Claude Code session transcripts). This script is the
instrument that makes that claim falsifiable: it takes a fixed transcript
corpus and produces one deterministic number, so a pre-change run and a
post-change run (after later gates rewrite checklist_engine.py) are directly
comparable.

DEFINITION OF "STRUCTURAL READ" (governs every future over-read claim in this
project -- this is the precise, defensible line the instrument draws):

A structural read is a `Read`-tool-use event in the transcript (a JSONL
session log; one line is one event, following the schema already used by
tests/fixtures/golden_transcript.jsonl and consumed by
scripts/hooks/gauge_writer_hook.py: `message.content[]` blocks with
`type == "tool_use"`) whose `input.file_path` basename matches ONE of:

  (a) STATE -- a spine/cycle/checklist JSON working-state file: `spine.json`,
      `cycle-*.json`, any `*checklist*.json`, or `execute.json` exactly. These
      are the engine's own live state; a driven agent is supposed to learn
      their contents ONLY through the engine's verbs (`current`, `attest`,
      `advance`, ...), never by reading the raw file -- checklist-engine.md
      states this plainly ("An agent does not re-read and self-manage a
      checklist; it asks the engine what to do").
  (b) ENGINE SOURCE -- `checklist_engine.py` itself, the engine's own
      implementation. Reading the engine's source to work out how to recover
      from a refusal is a documented bypass pattern in the x1 excursion
      (exhibit B): a real cost paid because the engine's own refusal message
      gave no next-step hint.

Both categories name a read that costs context tokens BECAUSE the
engine/workbench abstraction was supposed to make the raw file unnecessary.

Explicitly NOT counted, on purpose, so the number cannot be silently
inflated with reads the doctrine already sanctions:

  - `*.journal` files (`execute.json.journal`, `spine.json.journal`, ...) --
    these are append-only audit logs, a different artifact from the live
    state read the definition targets, and normally far larger than the
    state file itself; counting them would swamp the signal with an
    artifact nobody claims is being over-read.
  - `references/*.md`, `templates/*`, schema/design docs, `SKILL.md` -- this
    is the checklist's OWN documented context-read step
    (checklist-engine.md: "Every checklist opens with a context-read item so
    the agent pulls the right baseline... reads its inherited global
    doctrine... first"). Counting it would blur a by-design read with a
    bypass, making the claim LESS falsifiable, not more.
  - any tool other than `Read` (e.g. `Grep`, or a `Bash` `cat`/`type` of a
    matching path) -- a real limitation of this version, stated rather than
    silently ignored: those tools can read the same bytes but are not
    counted here. Widening the tool set is a future extension of the
    definition, not an accident.
  - narrative prose that merely MENTIONS a matching filename -- only an
    actual tool invocation costs real context tokens.

DETERMINISM: corpus files are iterated in sorted filename order; nothing
depends on wall-clock time or dict/set iteration order from external input.
The same corpus produces the same number on this machine and on a fresh
clone, because the corpus is committed in-repo under tests/fixtures/ and
resolved by a REPO-RELATIVE path (derived from this script's own location,
never from the caller's current working directory or any path outside the
repo).

A malformed JSON line (a truncated/corrupted transcript row) is skipped, not
fatal -- real transcripts can be interrupted mid-write -- but the skip is
counted and surfaced in the per-run report, never silently dropped.

Usage:
    python scripts/measure_overread.py [--corpus DIR]

`--corpus` overrides the default committed corpus
(tests/fixtures/overread_corpus/, repo-relative); a relative value is
resolved against the repo root, not the caller's cwd.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_DIR = REPO_ROOT / "tests" / "fixtures" / "overread_corpus"

# See the module docstring's "DEFINITION OF STRUCTURAL READ" above -- these
# patterns ARE that definition, kept close to the prose so the two cannot
# silently drift apart.
_STATE_FILE_PATTERNS = (
    re.compile(r"^spine\.json$", re.IGNORECASE),
    re.compile(r"^cycle-.*\.json$", re.IGNORECASE),
    re.compile(r"^.*checklist.*\.json$", re.IGNORECASE),
    re.compile(r"^execute\.json$", re.IGNORECASE),
)
_ENGINE_SOURCE_PATTERNS = (
    re.compile(r"^checklist_engine\.py$", re.IGNORECASE),
)


def _basename(path: str) -> str:
    """Basename of `path`, tolerant of both '/' and '\\' separators
    regardless of the host OS running this script -- a transcript captured
    on Windows can contain backslash paths even when this scan runs on a
    POSIX CI box, and pathlib.PurePath's separator handling is platform-
    dependent, so this is done by hand for cross-platform determinism."""
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def classify_path(path: str) -> str | None:
    """Classify `path` as "state", "engine-source", or None (not structural).

    None includes every path this instrument does not count as a structural
    read -- see the module docstring's "Explicitly NOT counted" section."""
    name = _basename(path)
    for pattern in _STATE_FILE_PATTERNS:
        if pattern.match(name):
            return "state"
    for pattern in _ENGINE_SOURCE_PATTERNS:
        if pattern.match(name):
            return "engine-source"
    return None


@dataclass(frozen=True)
class ScanResult:
    """One transcript's (one agent run's) structural-read counts."""

    transcript: Path
    state_reads: int
    engine_source_reads: int
    skipped_lines: int

    @property
    def structural_reads(self) -> int:
        return self.state_reads + self.engine_source_reads


def _read_events(record: dict):
    """Yield each `Read` tool_use block's `input.file_path` string found in
    one decoded transcript line's `message.content`. Never raises on
    unexpected shape -- an unrecognized block is simply not a Read event."""
    message = record.get("message")
    if not isinstance(message, dict):
        return
    content = message.get("content")
    if not isinstance(content, list):
        return
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") != "tool_use" or block.get("name") != "Read":
            continue
        tool_input = block.get("input")
        if not isinstance(tool_input, dict):
            continue
        file_path = tool_input.get("file_path")
        if isinstance(file_path, str):
            yield file_path


def scan_transcript(path: str | Path) -> ScanResult:
    """Scan one JSONL transcript file and count its structural reads."""
    path = Path(path)
    state_reads = 0
    engine_source_reads = 0
    skipped_lines = 0

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                skipped_lines += 1
                continue
            if not isinstance(record, dict):
                skipped_lines += 1
                continue
            for file_path in _read_events(record):
                category = classify_path(file_path)
                if category == "state":
                    state_reads += 1
                elif category == "engine-source":
                    engine_source_reads += 1

    return ScanResult(
        transcript=path,
        state_reads=state_reads,
        engine_source_reads=engine_source_reads,
        skipped_lines=skipped_lines,
    )


def scan_corpus(corpus_dir: str | Path) -> list[ScanResult]:
    """Scan every *.jsonl transcript directly under `corpus_dir`, in sorted
    filename order (determinism: never directory-iteration-order dependent)."""
    corpus_dir = Path(corpus_dir)
    files = sorted(corpus_dir.glob("*.jsonl"), key=lambda p: p.name)
    return [scan_transcript(f) for f in files]


def aggregate(results: list[ScanResult]) -> int:
    """The single unambiguous aggregate number: total structural reads
    summed across every run in the corpus."""
    return sum(r.structural_reads for r in results)


def format_report(results: list[ScanResult]) -> str:
    """Per-run breakdown, then the aggregate on its own clearly-labelled
    line so a verdict can quote it directly."""
    lines = [f"STRUCTURAL-READ SCAN -- {len(results)} transcript(s)", ""]
    for r in results:
        lines.append(
            f"  {r.transcript.name}: structural_reads={r.structural_reads} "
            f"(state={r.state_reads}, engine_source={r.engine_source_reads}, "
            f"skipped_lines={r.skipped_lines})"
        )
    lines.append("")
    total = aggregate(results)
    mean = total / len(results) if results else 0.0
    lines.append(f"runs={len(results)} mean_structural_reads_per_run={mean:.2f}")
    lines.append(f"AGGREGATE_STRUCTURAL_READS: {total}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--corpus",
        default=None,
        help=(
            "Directory of *.jsonl transcripts to scan. A relative value is "
            "resolved against the repo root (this script's own location), "
            "never the caller's cwd. Defaults to the committed corpus at "
            "tests/fixtures/overread_corpus/."
        ),
    )
    args = parser.parse_args(argv)

    if args.corpus:
        corpus_dir = Path(args.corpus)
        if not corpus_dir.is_absolute():
            corpus_dir = REPO_ROOT / corpus_dir
    else:
        corpus_dir = DEFAULT_CORPUS_DIR

    if not corpus_dir.is_dir():
        print(f"ERROR: corpus directory not found: {corpus_dir}", file=sys.stderr)
        return 1

    results = scan_corpus(corpus_dir)
    if not results:
        print(f"ERROR: no *.jsonl transcripts found in corpus directory: {corpus_dir}", file=sys.stderr)
        return 1

    print(format_report(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
