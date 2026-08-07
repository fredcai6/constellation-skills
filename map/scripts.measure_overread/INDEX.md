# scripts.measure_overread
scripts/measure_overread.py, 271 lines, 2 holes

measure_overread.py -- count STRUCTURAL READS per agent run in a transcript.

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

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, json, pathlib.Path, re, sys
imported by: none found

```python
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_DIR = REPO_ROOT / 'tests' / 'fixtures' / 'overread_corpus'
_STATE_FILE_PATTERNS = (re.compile('^spine\\.json$', re.IGNORECASE), re.compile('^cycle-.*\\.json$', re.IGNORE...
_ENGINE_SOURCE_PATTERNS = (re.compile('^checklist_engine\\.py$', re.IGNORECASE),)
```

- [_basename](_basename.md) function: Basename of `path`, tolerant of both '/' and '\' separators
- [classify_path](classify_path.md) function: Classify `path` as "state", "engine-source", or None (not structural).
- [ScanResult](ScanResult.md) class: One transcript's (one agent run's) structural-read counts.
  - [ScanResult.structural_reads](ScanResult.structural_reads.md) property: HOLE: no docstring
- [_read_events](_read_events.md) function: Yield each `Read` tool_use block's `input.file_path` string found in
- [scan_transcript](scan_transcript.md) function: Scan one JSONL transcript file and count its structural reads.
- [scan_corpus](scan_corpus.md) function: Scan every *.jsonl transcript directly under `corpus_dir`, in sorted
- [aggregate](aggregate.md) function: The single unambiguous aggregate number: total structural reads
- [format_report](format_report.md) function: Per-run breakdown, then the aggregate on its own clearly-labelled
- [main](main.md) function: HOLE: no docstring
