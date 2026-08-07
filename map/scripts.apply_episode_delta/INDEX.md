# scripts.apply_episode_delta
scripts/apply_episode_delta.py, 1309 lines, 24 holes

Deterministically apply structured episode-delta operations to the episode store.

The LLM proposes operations (create/amend-assertion/retire) in a JSON delta file; this
script validates every op and applies them mechanically, all-or-nothing: any invalid op
anywhere in the delta rejects the WHOLE delta and leaves the store byte-for-byte
unchanged. The LLM never writes an episode file directly — this script is the only
write path into episodes/.

Mirrors scripts/apply_lessons_delta.py's contract (validate-then-apply, all-or-nothing,
retire-requires-reason, "- field: value" grammar) but is NOT the same store: see
docs/EPISODE_STORE.md for the full contract this writer implements, and its section 7
in particular for the retirement layout, ratified at gate g4 and bound in the seam block
below — retirement MOVES the file from episodes/active/<id>.md to
episodes/retired/<id>.md, and retired/ is an archive rather than a second live search
space.

Op vocabulary (this script's own choice — not fixed by EPISODE_STORE.md, which only
fixes the record grammar and the store's obligations):

  create           — mint a new episode. The id is ASSIGNED BY THIS WRITER (run+sequence
                     scan, EPISODE_STORE.md section 2), never supplied by the delta —
                     that is the "zero agent effort" property the doc argues for. All
                     five agent-supplied kinds are required; diagnosis is optional.
  amend-assertion  — dispute exactly ONE named assertion (agent-supplied or diagnosis):
                     changes only its lifecycle-standing and appends one history line.
                     Every sibling field, in this assertion and every other, is
                     untouched (EPISODE_STORE.md section 5).
  retire           — move an episode out of ordinary search and into the archive,
                     RETAINED in history, with a mandatory non-empty reason. Never
                     touches any assertion's own lifecycle-standing (EPISODE_STORE.md
                     section 7). The content half routes through apply_retirement()
                     alone; the layout half (the move) through destination_for()
                     alone. Both land in one write plan, so the store is never left
                     half-retired.

Determinism: same delta + same starting state -> same bytes. This writer never calls
date.today() or any other wall-clock source — every free-text value that would carry a
"when" (a retire's retired-at, a dispute's history line) must be supplied BY THE DELTA,
not generated here. (apply_lessons_delta.py stamps its own dates; this store departs
from that on purpose — see the g2 handoff's determinism constraint.)

Newline handling (Windows hazard, named explicitly): every read and write in this module
passes newline="" to disable Python's own universal-newline translation, so a `
` in
an existing file is preserved as literal CRLF bytes during parsing (never silently
folded to `
`, which would corrupt a byte-for-byte-unchanged comparison), and every
write emits LF-only line endings on every platform, including Windows. Combined with the
newline-injection guard (which rejects any delta value containing a literal `
` or ``
before it is ever rendered), this keeps the store's bytes fully deterministic regardless
of which OS produced them.

That newline discipline goes through `read_text_exact` / `write_text_exact` below rather
than `Path.read_text(newline=...)` / `Path.write_text(newline=...)`, which exist only on
Python 3.13+ while CI pins 3.12 — see those helpers.

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, dataclasses.field, json, os, pathlib.Path, re, sys, uuid
imported by: none found

```python
REQUIRES_PYTHON = (3, 12)
ID_RE = re.compile('[a-z0-9][a-z0-9-]*-[0-9]{3,}')
RUN_RE = re.compile('[a-z0-9][a-z0-9-]*')
MECHANICAL_SCALAR_FIELDS = ('run', 'project', 'role', 'spine-step', 'context-manifest-ref', 'refusals', 'reopens',...
MECHANICAL_INT_FIELDS = ('refusals', 'reopens', 'rework-count', 'failed-commands')
MECHANICAL_ALL_FIELDS = MECHANICAL_SCALAR_FIELDS + ('artifact-ref',)
AGENT_SUPPLIED_KINDS = ('task-intent', 'expected-behavior', 'observed-behavior', 'impact-cost', 'workaround')
ASSERTION_ALLOWED_FIELDS = ('strength', 'statement')
DIAGNOSIS_KINDS = ('suspected-cause', 'proposed-remedy')
STRENGTHS = ('weak', 'medium', 'strong')
LIFECYCLE_STANDINGS = ('active', 'disputed', 'superseded', 'rejected')
OP_KINDS = ('create', 'amend-assertion', 'retire')
HEADER_RE = re.compile('<!--\\s*episode-state:\\s*schema=(\\d+)\\s+id=(\\S+)\\s+status=(\\S+)\\s*-->')
ASSERTION_HEADING_RE = re.compile('^### assertion:(\\S+)\\.([ad][0-9]+)$')
FIELD_RE = re.compile('^- ([a-z-]+): ?(.*)$')
ACTIVE_DIR = 'active'
RETIRED_DIR = 'retired'
NON_EPISODE_FILENAMES = frozenset({'README.md'})
```

- [read_text_exact](read_text_exact.md) function: Read a store file with newline translation DISABLED, so bytes survive the round trip.
- [write_text_exact](write_text_exact.md) function: Write a store file emitting exactly `text`, with no platform newline translation.
- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [EpisodeDeltaError](EpisodeDeltaError.md) class: Raised when a delta cannot be applied; nothing is written.
- [_reject_newline](_reject_newline.md) function: C3b — the injection defense named in EPISODE_STORE.md section 7: a free-text
- [_require_str](_require_str.md) function: HOLE: no docstring
- [Assertion](Assertion.md) class: HOLE: no docstring
  - [Assertion.render](Assertion.render.md) method: HOLE: no docstring
- [Episode](Episode.md) class: HOLE: no docstring
  - [Episode.all_assertions](Episode.all_assertions.md) method: Flat aid -> Assertion map spanning both agent-supplied and diagnosis bins,
- [render_episode](render_episode.md) function: HOLE: no docstring
- [parse_episode](parse_episode.md) function: HOLE: no docstring
  - [parse_episode.parse_assertions](parse_episode.parse_assertions.md) method: HOLE: no docstring
    - [parse_episode.parse_assertions.flush](parse_episode.parse_assertions.flush.md) method: HOLE: no docstring
- [episode_id_for](episode_id_for.md) function: THE classifier: is this file an episode, and if so, which one? Returns the
- [store_root](store_root.md) function: The ONE named seam for where episodes/ lives (EPISODE_STORE.md section 1): the
- [ensure_store_layout](ensure_store_layout.md) function: Create the store's two layout directories if they are absent — the WRITER's
- [_require_store_layout](_require_store_layout.md) function: Every READ seam's first act: refuse a store that is not there.
- [stray_episode_paths](stray_episode_paths.md) function: Every Markdown file sitting at the store's FLAT root — i.e. in neither active/
- [_reject_strays](_reject_strays.md) function: HOLE: no docstring
- [_layout_episode_ids](_layout_episode_ids.md) function: Every episode id held by ONE layout directory — the only place a directory
- [_reject_half_retired](_reject_half_retired.md) function: An id present in BOTH directories is a retirement that half-happened: retired by
- [iter_episode_ids](iter_episode_ids.md) function: Base enumeration seam (section 7), bound to Option A.
- [resolve_episode_path](resolve_episode_path.md) function: Fetch-by-id path-resolution seam (section 7), bound to Option A: try active/,
- [_new_episode_path](_new_episode_path.md) function: Where a brand-new (always-active) episode is written. Not one of section 7's five
- [is_episode_in_ordinary_search](is_episode_in_ordinary_search.md) function: Per-id membership seam (section 7), bound to Option A: a directory check.
- [apply_retirement](apply_retirement.md) function: THE retirement write-side seam (section 7): the entire CONTENT effect of a retire
- [destination_for](destination_for.md) function: The layout-dependent HALF of retiring, bound to Option A: where should this
- [_next_episode_id](_next_episode_id.md) function: Zero-agent-effort id assignment: scan existing <run>-*.md basenames (across
- [validate_delta](validate_delta.md) function: HOLE: no docstring
- [_validate_create](_validate_create.md) function: HOLE: no docstring
- [_validate_assertion_payload](_validate_assertion_payload.md) function: HOLE: no docstring
- [_validate_amend_assertion](_validate_amend_assertion.md) function: HOLE: no docstring
- [_validate_retire](_validate_retire.md) function: HOLE: no docstring
- [_place](_place.md) function: Move one staged temp file onto its final path. A single os.replace() is atomic on
- [_remove_superseded](_remove_superseded.md) function: Remove the source path a moved episode has left behind — the second half of a
- [_Transaction](_Transaction.md) class: Everything an apply_delta() run needs, kept in memory until every op in the
  - [_Transaction.__init__](_Transaction.__init__.md) method: HOLE: no docstring
  - [_Transaction.known_ids](_Transaction.known_ids.md) method: HOLE: no docstring
  - [_Transaction.load](_Transaction.load.md) method: HOLE: no docstring
  - [_Transaction.create](_Transaction.create.md) method: HOLE: no docstring
  - [_Transaction.write_plan](_Transaction.write_plan.md) method: Renders every touched episode to its FINAL destination path. Returns
  - [_Transaction.commit](_Transaction.commit.md) method: REWORK (g2 review BLOCK, defect 2): stage every touched file to a temp
- [apply_delta](apply_delta.md) function: HOLE: no docstring
- [_apply_create](_apply_create.md) function: HOLE: no docstring
- [_apply_amend_assertion](_apply_amend_assertion.md) function: HOLE: no docstring
- [_apply_retire](_apply_retire.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
- [_dry_run_log](_dry_run_log.md) function: Validate and compute the write-plan, but never call commit().
