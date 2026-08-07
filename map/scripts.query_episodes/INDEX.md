# scripts.query_episodes
scripts/query_episodes.py, 576 lines, 7 holes

Deterministic retrieval over the episode store (docs/EPISODE_STORE.md section 8).

The store never guesses. This module exposes exactly four primitives — fetch by id,
enumerate, select by exact field value / set membership, and enumerate an episode's
neighbours by shared exact join key — and nothing else. There is no ranking, no
scoring, no similarity, no embedding, no ordering by relevance. What it hands a
downstream sensor is a candidate set that is COMPLETE by construction and unordered
(results are id-sorted purely so the same store always produces the same bytes;
alphabetical order is a canonical enumeration, not a relevance ranking). Deciding that
two episodes *rhyme* is a stochastic sensor's job, owned at issue #308, and happens
entirely on top of this surface — never inside it (governing principle B0.1, the
stochastic boundary).

Silent omission is the failure mode this module is written against. A retrieval that
crashes is a bug you find; a retrieval that quietly returns one record fewer than it
should is a bug you ship. Three concrete defenses, each with an adversarial test in
tests/test_episode_store.py:

  1. Every field read goes through field_values(), which returns a LIST for every
     field. artifact-ref is genuinely list-shaped, and the natural implementation of
     "read the mechanical block into a dict" keeps only the LAST artifact-ref line and
     silently drops the rest — so an episode whose only matching ref is not the final
     one vanishes from the candidate set with no error at all.
  2. Matching compares whole parsed field VALUES with ==, never a substring of the file
     text. A substring match over-returns (a prefix matching a longer value); a
     line-oriented grep that forgot to anchor under-returns once free text is involved.
     Neither failure is available to an == over parsed values.
  3. An unrecognized field name RAISES. It never returns an empty candidate set, which
     is what makes a typo'd field name a visible failure instead of a silent "no
     episodes matched".

Retirement (EPISODE_STORE.md section 7, ratified at gate g4). Retiring an episode MOVES
its file out of the ordinary-search set and into the archive. The ruling's second half —
"prefer to keep files clean of history unless they're historical; archives are available
strats" — is a design principle this module implements literally:

  * **the archive is opt-in, never opt-out.** Ordinary retrieval scans the ordinary set
    and never touches the archive, so it is not a second live search space that every
    query has to remember to exclude. Every scanning primitive takes `include_retired`,
    defaulting to False; history-inclusive retrieval is a deliberate, separate act.
    A default that included the archive would make every future caller's *omission* of a
    filter a silent correctness bug — the exact failure class this module exists against;
  * **fetch-by-id is exempt, on purpose.** An addressed lookup by name is not a search;
    retirement excludes an episode from search, never from retrieval by name. A
    cross-reference (`consolidated-into:`, `superseded-by:`) would dangle otherwise.

Store-level refusals. A store that is ABSENT (a typo'd --store-root, or a layout that was
never committed), MALFORMED (a Markdown file outside the two layout directories, or one
inside them whose name is not a well-formed episode id), or HALF-RETIRED (an id in both
directories) is refused by every primitive here, with an exit code, rather than answered.
Each of those would otherwise produce a plausible wrong answer — most often `count: 0`,
which reads exactly like an empty store. The refusals live in the writer's seams, so
retrieval inherits them instead of restating them.

Layout containment. Every path resolution goes through resolve_episode_path(), every
store scan through iter_episode_ids(), every membership question through
is_episode_in_ordinary_search() — all three are the writer's seams
(scripts/apply_episode_delta.py). This module inlines no path, no glob, and no grep, and
tests/test_episode_store.py asserts it: with the layout bound, the containment is what
keeps the binding in one place instead of scattered across call sites.

Section 7's composition rule for the ordinary set — scan with
iter_episode_ids(include_retired=False), then confirm each returned id through
is_episode_in_ordinary_search(), always both steps, never one folded into the other — is
followed here. Under the bound layout the second step cannot subtract anything from the
first, so it is kept for a different reason than the one that introduced it: the scan and
the membership predicate are two INDEPENDENT seams, and a change that updated only one of
them is caught here. Their disagreement is therefore raised, never silently dropped —
dropping is how a candidate set gets quietly shorter.

Newline handling (Windows hazard): every read passes newline="" so a stored 
 is
never silently folded to 
, exactly as the writer does. Retrieval must see the bytes
that are actually on disk, since one of this gate's obligations is proving a stored
line is BYTE-identical before and after an unrelated write. That read goes through the
writer's read_text_exact() helper — NOT Path.read_text(newline=...), which is Python
3.13+ while CI pins 3.12.

imports stdlib: __future__.annotations, argparse, importlib.util, json, os, pathlib.Path, sys
imported by: none found

```python
_WRITER_PATH = Path(__file__).resolve().parent / 'apply_episode_delta.py'
_WRITER_MODULE = 'apply_episode_delta'
_FIELD_READERS = {'id': lambda ep: [ep.episode_id], 'run': lambda ep: [ep.run], 'project': lambda ep: [e...
SELECTABLE_FIELDS = tuple(sorted(_FIELD_READERS))
JOIN_KEYS = ('artifact-ref', 'role+spine-step')
```

- [_utf8_stdio](_utf8_stdio.md) function: HOLE: no docstring
- [writer](writer.md) function: g2's writer module — the single home of the record grammar (parse_episode) and
- [QueryError](QueryError.md) class: Raised when a query cannot be answered. Never swallowed into an empty result —
- [EpisodeNotFound](EpisodeNotFound.md) class: The named episode does not exist. A distinct type (and a distinct CLI exit code)
- [store_root](store_root.md) function: The store-root seam (EPISODE_STORE.md section 1), re-exported from the writer so
- [_read_episode](_read_episode.md) function: HOLE: no docstring
- [fetch_episode](fetch_episode.md) function: Fetch one episode by id. Returns the parsed Episode, or None if no episode with
- [HalfRetiredStore](HalfRetiredStore.md) class: The base scan and the membership predicate disagree about one id. Under the bound
- [enumerate_episode_ids](enumerate_episode_ids.md) function: Every episode id in the ordinary rhyme-search set, id-sorted for determinism.
- [enumerate_episodes](enumerate_episodes.md) function: Every episode in the ordinary set as parsed records, id-sorted — or the
- [_selectable_field_reader](_selectable_field_reader.md) function: The one place a field name is checked and the one place the refusal is worded.
- [field_values](field_values.md) function: Every value an episode carries for `field`, as strings — one element for a
- [select_episodes](select_episodes.md) function: Every episode whose `field` carries at least one of `values` — exact match, set
- [select_episode_ids](select_episode_ids.md) function: HOLE: no docstring
- [_join_key_values](_join_key_values.md) function: An episode's join-key values as (key-name, value) pairs. Two episodes are
- [neighbours](neighbours.md) function: Every OTHER episode sharing at least one exact join key with `episode_id`.
- [neighbour_ids](neighbour_ids.md) function: HOLE: no docstring
- [assertion_to_dict](assertion_to_dict.md) function: HOLE: no docstring
- [episode_to_dict](episode_to_dict.md) function: The record as data. Carries no score, rank, distance or relevance field — there
- [_envelope](_envelope.md) function: The CLI's answer shape. `pid` names the OS process that produced this answer —
- [main](main.md) function: HOLE: no docstring
  - [main.add_archive_flag](main.add_archive_flag.md) method: HOLE: no docstring
