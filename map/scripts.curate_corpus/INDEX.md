# scripts.curate_corpus
scripts/curate_corpus.py, 452 lines, 4 holes

Curator MEASUREMENT pass over the skills corpus (mechanical-only, flags-never-gates).

This is the curator's measurement/flagging tool, NOT a linter that fails a build.
It performs MECHANICAL checks over each `skills/<name>/SKILL.md` (and its
`references/`) and emits a human findings table plus a `--json` machine record.

Two invariants are enforced IN CODE so prose drift cannot erode them:

  * FLAGS-NEVER-GATES (curator invariant #2): every run ALWAYS exits 0. Soft
    budgets are review heuristics, never build gates — there is deliberately no
    code path that returns non-zero. An unparseable skill becomes a findings ROW
    (check="parse", status flagged), never a crash or a nonzero exit.

  * DECIDABILITY-HONESTY (T7): the script reports only mechanically-decidable
    facts (counts, token presence/absence, shared shingles). It NEVER renders a
    semantic verdict (e.g. "this register is wrong", "this clause is a
    procedure"). Where the convention needs a human judgment, it SHORTLISTS a
    candidate (status="shortlist") for a human to adjudicate — it never judges.

No baseline/drift-vs-previous-run diff lives here (spec ruling S7 — that is a
future v2). Standard library only.

imports stdlib: __future__.annotations, argparse, dataclasses.dataclass, dataclasses.field, json, pathlib.Path, re, sys
imported by: none found

```python
SKILL_WORD_TARGET = 400
SKILL_LINE_HARD_FLAG = 500
DESCRIPTION_MAX_CHARS = 350
DESCRIPTION_MAX_WORDS = 50
PERSON_PRONOUNS = ('i', 'you', 'your', 'we', 'our', 'us')
WHEN_TO_USE_MARKERS = ('use when', 'use to', 'use for', 'use during')
EXCLUSION_MARKERS = ('not ', 'do not', "don't", 'instead of', 'rather than', 'never ')
EXCLUSION_NOT_NEVER_RE = re.compile('\\bnot\\b|\\bnever\\b', re.IGNORECASE)
EXCLUSION_REDIRECT_RE = re.compile('\\bfor\\b.*?\\buse\\b', re.IGNORECASE)
CONFUSABLE_PAIRS = (('scout', 'cartographer'), ('explorer', 'interrogator'), ('admiral', 'commander'), ('c...
CONFUSABLE_SKILLS = frozenset((s for pair in CONFUSABLE_PAIRS for s in pair))
VALID_INVOKERS = ('human', 'agent', 'both')
REFERENCE_TOC_LINE_THRESHOLD = 100
TOC_MARKER_RE = re.compile('^\\s*#{1,6}\\s+(table of contents|contents)\\b', re.IGNORECASE | re.MULTILINE)
SHINGLE_SIZE = 8
MIN_CLUSTER_SKILLS = 2
STATUS_FLAGGED = 'flagged'
STATUS_SHORTLIST = 'shortlist'
STATUS_INFO = 'info'
STATUS_OK = 'ok'
```

- [CorpusParseError](CorpusParseError.md) class: A skill's SKILL.md could not be parsed. Becomes a findings row, never a crash.
- [Finding](Finding.md) class: One mechanical observation. `extra` carries structured data (e.g. the
  - [Finding.to_dict](Finding.to_dict.md) method: HOLE: no docstring
- [_utf8_stdio](_utf8_stdio.md) function: Match the sibling scripts: don't force every caller to set PYTHONIOENCODING.
- [parse_frontmatter](parse_frontmatter.md) function: Parse a leading YAML frontmatter block into a flat dict of top-level
- [_words](_words.md) function: Lowercased alphanumeric word tokens; whitespace and punctuation normalized.
- [check_size](check_size.md) function: Body line/word counts vs the soft size budgets.
- [_person_tokens](_person_tokens.md) function: HOLE: no docstring
- [_exclusion_present](_exclusion_present.md) function: HOLE: no docstring
- [check_description](check_description.md) function: Mechanical description lint: length, person-pronoun shortlist, when-to-use
- [check_invoker](check_invoker.md) function: Presence + validity of the `invoker:` frontmatter tag.
- [check_references](check_references.md) function: Each references/*.md longer than the threshold should carry a TOC heading.
- [check_duplication](check_duplication.md) function: Corpus-level: report k-word shingles shared across >= MIN_CLUSTER_SKILLS
- [_skill_dirs](_skill_dirs.md) function: Immediate subdirectories that are candidate skills. Dirs whose name starts
- [curate](curate.md) function: Run every mechanical check over `root` (a skills/ directory) and return
- [render_table](render_table.md) function: A readable fixed-width findings table: skill | check | status | detail.
- [build_record](build_record.md) function: The --json machine record: the run's root, the heuristic constants that
- [main](main.md) function: HOLE: no docstring
