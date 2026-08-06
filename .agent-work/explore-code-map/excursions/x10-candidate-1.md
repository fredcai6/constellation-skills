# x10 candidate 1 — diff-ergonomics-first

**Constraint:** optimize the on-disk shape for reviewable git diffs and human-auditable
files above all else. A small code change must produce a small, legible diff; a reviewer
must be able to audit crawler output in a PR without tooling.

**One-line summary.** A store that mirrors the source tree, one directory per module and
one grouped plain-text file per class, holding **deduplicated boundary facts with no line
numbers and no hashes**, addressed by **module-relative symbol paths** — so a code edit
adds the lines it actually added, and a file move becomes a git-detected directory rename
of byte-identical content.

---

## 0. The three decisions the constraint forces, up front

Everything below follows from three rulings. Each is stated as a ruling with its measured
justification, because each one trades away something the other candidates will keep.

### Ruling A — positions do not live in git

Every statement x7b emits carries `q: {file, line, col}`. If that is committed, **inserting
one line at the top of a source file rewrites every store line derived from that file.**
Measured on the x7b corpus: `src/utils/config.py` produces **493 statements**, all
position-bearing. A one-line import added at the top changes ~490 of them. The busiest file
in the slice (`src/evo_predictor/data_adapter/_build.py`) produces **1,696**. A reformat, a
`black` run, or a docstring rewrap would produce a five-figure diff repo-wide while changing
nothing a reader of the map cares about.

Positions are 100% re-derivable from the source at the same commit, so they belong to the
"DB is a disposable index" half of the substrate verdict, not the "git is truth" half.
**`.cmap-index/` holds positions and is gitignored.** What is committed is what a human must
audit: which symbol relates to which, and the prose.

*Cost:* the store alone cannot jump to a line. Section 7 accounts for it.

### Ruling B — facts, not occurrences

x7a left this open ("the numbers differ by 3% and the choice must be explicit") — but that
3% was measured at the `(s, p, o, file, line)` key. At the **`(s, p, o)`** key, which is
what a store without positions can use, the collapse is much larger. Measured over the full
x7b corpus (67 files, 44,554 statements):

| | count |
|---|---|
| occurrences (what the crawler emits) | 44,554 |
| distinct facts `(s, p, o, why)` | 23,938 (**−46.4%**) |
| distinct **boundary** facts (locals and param self-reads excluded, Ruling C) | **14,458 (−67.5%)** |

`Config.load_config` alone drops from **65 occurrences to 26 facts to 19 boundary facts**.
Concretely: it reads `Config._config_data` at lines 67, 70, 72 and elsewhere — the map's
reader wants to know *that* it reads it, not four times over. One fact, one line, and the
line stops changing when the source is edited around it.

*Cost:* call multiplicity is gone from the store. Section 7 accounts for it.

### Ruling C — module-relative ids

`src.utils.config:Config.load_config` is 36 characters, of which 17 are the module prefix
repeated on every line of every file in that module's own directory. Inside
`map/src/utils/config/`, symbols of that module are written bare: `Config.load_config`.
Cross-module targets stay fully qualified.

This is not only compression. It is what makes a module rename a **content-preserving
directory rename**: everything inside the moved directory is byte-identical afterwards, so
`git diff -M` reports `rename map/src/utils/{config => configuration}/ (100%)` instead of
several hundred changed lines. The identity work happens in the artifact the human actually
reads.

---

## 1. On-disk layout, concretely

### 1.1 The tree

The store mirrors the source tree exactly. One **directory per module**, named for the
module file without its extension.

```
map/
  MANIFEST.md                        # schema + crawler version, 8 lines, changes only when the crawler does
  .gitattributes                     # diff drivers and review-collapse rules
  src/
    utils/
      config/                        # <- src/utils/config.py
        _module.facts                # module-scope facts: imports, contains, module-level state
        _module.md                   # module purpose prose
        Config.facts                 # the class and every method it contains
        Config.md                    # class + method purpose prose
        Config.tags.md               # Assumption:/Constraint:/Rationale:/Rejected: nodes anchored in this class
        _module.flow                 # locals and param self-reads (committed, review-collapsed)
        Config.flow
      constants/
        _module.facts
        _module.md
      environment/
        _module.facts                # free functions live here; no class files
        _module.md
        _module.tags.md
```

**Where the parent's directory-per-subject / file-per-layer lean fits, and where it bends.**
File-per-layer is taken wholesale: `.facts` / `.md` / `.tags.md` / `.flow` are four layers
of the same subject sitting side by side, each with its own churn rate and its own reviewer.
Directory-per-subject is bent one notch coarser: **the directory is the module, not the
symbol.** A directory per symbol would put `Config.load_config/` next to 3,500 siblings —
`git diff --stat` would still be readable, but a checkout on Windows would carry ~45,000
directories at the 10× scale target, and a reviewer opening the tree in a PR would see depth
instead of shape. Module-level directories give ~440 directories at 1×, ~4,400 at 10×, and
the tree still reads like the source tree, which is the property that matters: a reviewer who
knows where `config.py` is knows where its map lives.

**Classes get their own file; module-level functions do not.** A class is a review unit and
a rename target, so `Config.facts` earns a path that shows up in `git diff --stat`. Free
functions are reviewed together with their module, and giving each one a file would double
the file count for no diff-legibility gain (a free-function rename is a one-line header
change either way, since ids inside a file are module-relative).

### 1.2 `map/src/utils/config/Config.facts` — the `load_config` bundle

Real content, derived from the x7b statements for `src.utils.config:Config.load_config`
(26 facts, minus the 7 local/param-self facts that Ruling C routes to `.flow`).

```
# cmap facts v0 — generated; edit the source and re-run, never edit this file.
# subject blocks in source declaration order; fact lines sorted within a block.

Config                                        class
  contains  PROJECT_ROOT
  contains  CONFIG_DIR
  contains  OUTPUTS_DIR
  contains  _config_data
  contains  _config_source
  contains  load_config
  contains  _validate_config
  reads     PROJECT_ROOT
  reads     OUTPUTS_DIR
  writes    CACHE_DIR
  writes    CONFIG_DIR
  calls     pathlib:Path
  calls     ?dispatch-unknown-base

Config.load_config                            classmethod
  param     cls
  param     config_file
  calls     Config._setup_fastf1_cache
  calls     Config._setup_logging
  calls     Config._validate_config
  calls     builtins:open
  calls     builtins:str
  calls     pathlib:Path
  calls     src.models.exceptions:ConfigurationError
  calls     yaml:safe_load
  calls     ?dispatch-unknown-base
  reads     Config.CONFIG_DIR
  reads     Config._config_data
  reads     Config._config_source
  reads     yaml:YAMLError
  writes    Config._config_data
  writes    Config._config_source
```

**The format rules, each one a diff decision:**

- **Subject header at column 0, facts indented two.** This gives git a free `xfuncname`
  hunk header — see §1.5 — so `@@` lines in a PR name the symbol that changed.
- **Predicate is a fixed 10-column field, never computed from content.** Alignment that
  adapts to the longest object would reflow a whole block when one long name is added.
- **Blocks in source declaration order; lines within a block sorted by predicate then
  object — except `contains`, which stays in declaration order.** Declaration order for
  blocks means a rename does not move the block, and inserting a method inserts one
  contiguous hunk. Alphabetical order within a block means adding a call adds exactly one
  line in a predictable place.
- **`?reason` is the unresolved token**, carrying x7b's `why` inline. The 62.8% qualified-
  dispatch hole is a permanent class, so it gets a permanent one-token shape rather than a
  `"o": "UNRESOLVED"` plus a sibling `why` field. After dedup, `load_config`'s three
  unresolved dispatch sites become one line.
- **Bare = this module. `mod:Sym` = elsewhere.** `Config._validate_config` and
  `src.models.exceptions:ConfigurationError` are visibly different kinds of dependency
  without a legend.

### 1.3 `map/src/utils/config/Config.md` — the prose layer

One sentence per line (semantic linefeeds), so a reworded sentence is a one-line diff rather
than a reflowed paragraph.

```markdown
# Config

Configuration manager for F1Brainz system.

## load_config

Load and validate configuration from YAML file.

- `config_file` — Name of config file in configs/ directory.
- *returns* — Validated configuration dictionary.
- *raises* `src.models.exceptions:ConfigurationError` — If config file missing or invalid.
```

Every word here is harvested from the untagged docstring body and its Google-style `Args:` /
`Returns:` / `Raises:` blocks — x9's zero-tag majority case, which is also x1's measured
largest harvest (646 parameters already carry prose).

### 1.4 `map/src/utils/config/Config.tags.md` — one `Assumption:`-minted node

Source side, in `config.py`, inside `load_config`'s docstring:

```python
        Assumption: A bare config_file name resolves under CONFIG_DIR, not the
            process working directory. If a caller starts passing cwd-relative
            paths, resolution changes silently and the cache key still matches.
```

Store side:

```markdown
# Config — asserted nodes

## assumption: bare-config-name-resolves-under-config-dir
- anchor: `Config.load_config`
- origin: `Assumption:` #1 in `src/utils/config.py`
- confidence: medium — id slugged from text, not author-fixed

A bare config_file name resolves under CONFIG_DIR, not the process working directory.
If a caller starts passing cwd-relative paths, resolution changes silently and the cache key still matches.
```

The tag node lives **in the same directory as its anchor**, deliberately: a reviewer auditing
a PR that touches `config.py` sees the structural facts, the prose, and the asserted nodes as
three adjacent files in one directory, and never has to open a central registry to know what
this change asserted. Locality of review beats locality of kind.

x9's edge falls out of the target kind and is not stored: `assumption:` ⇒
`Config.load_config --constrained-by--> assumption:...`. Storing it would be a second line
that changes whenever the first does.

**`origin` carries no line number** — `(path, anchor, tag, ordinal)` instead. This is not a
concession to Ruling A; it is better provenance. A line number goes stale the moment anyone
edits above it, whereas `the first Assumption: in Config.load_config` re-resolves after any
edit that does not touch the tag. org-babel's law wants a pointer that survives; a line is
the one pointer that does not.

### 1.5 `map/.gitattributes` — the review machinery

Three lines, all standard git, no tooling for the reviewer to install.

```
map/**/*.facts   diff=cmap
map/**/*.flow    linguist-generated=true
map/**/*.facts   merge=cmap-rederive
```

- `diff=cmap` with `[diff "cmap"] xfuncname = "^[^ #].*$"` in `.git/config` makes git print
  the enclosing **subject header** in every `@@` hunk line. A PR diff reads
  `@@ -18,6 +19,8 @@ Config.load_config` — the changed symbol is named in the hunk header.
- `linguist-generated=true` collapses `.flow` by default in a GitHub PR while leaving it
  fully diffable for anyone who expands it. Intra-function dataflow is committed truth but
  is not what a reviewer is auditing.
- `merge=cmap-rederive` — see §7.7. A derived store is never merged by hand.

---

## 2. Identity scheme

**The id on every `s`/`o` is the symbol path**, written module-relative inside its own
module's directory and fully qualified outside it:

```
<module dotted path> ":" <dotted symbol chain within the module>
```

`src.utils.config:Config.load_config`, `src.models.exceptions:ConfigurationError`,
`yaml:safe_load`, `builtins:str`. Four id namespaces are distinguished lexically, with no
lookup: bare (this module), `dotted.path:Sym` (another module — internal if it starts with
the project root package, external otherwise), `?reason` (unresolved), and
`assumption:`/`constraint:`/`claim:`/`decision:` (tag-minted and curated overlay nodes).

**Who assigns it:** nobody. It is a pure function of the AST — the module's path from the
repo root plus the enclosing declaration chain. Two crawler runs over the same tree produce
the same ids; two branches produce the same ids for unchanged code; no counter, no registry,
no allocation step, no state carried between runs.

**Why not an opaque serial.** An opaque serial (`n:4f2a91`) is the right answer for rename
survival and the wrong answer for this constraint, because it makes every line of the store
unreadable without a lookup table. `n:4f2a91 reads n:9c11de` cannot be audited in a PR; the
constraint I was given says a reviewer must be able to. This is the single largest
divergence between this candidate and candidate 2, and it is a real fork, not a detail.

**Stability guarantees, stated honestly:**

| Change | Id survives? |
|---|---|
| Edit a function body | **yes** — ids are position-free |
| Reformat / reflow / reorder imports | **yes** |
| Add or remove a parameter | **yes** for the function; params are not subjects |
| Reorder methods within a class | **yes** (blocks move; see §7.6) |
| Rename a method | **no** — re-mints, plus every reference to it |
| Rename or move a module | **no** — re-mints every symbol in it and every inbound reference |
| Move a class between modules | **no** |
| Split one function into two | **no** for the new one; the original survives if the name does |

**Tag-node ids** are slugged from the tag text and scoped to their anchor's module, per x9's
`confidence: medium` rule. One added rule this layout requires: **a tag node referenced by
`See:` from outside its own module must carry an explicit `[stable-id]`.** The crawler errors
if a cross-module `See:` resolves to a location-slugged node. This turns the one genuinely
fragile cross-reference into a build failure instead of a silent break, and the fix lands in
the source docstring — which is the two-way-flow verdict working as intended.

---

## 3. The rename scenario, walked

`src/utils/config.py` → `src/utils/configuration.py`, and `Config.load_config` →
`Config.load`, in one commit.

### 3.1 What the crawler emits

Nothing special. It re-derives the whole tree from scratch and writes files; it has no
memory of the previous run and does not attempt rename detection. Every id under the old
module path is gone; every id under the new one is new. The store on disk after the run is:

- `map/src/utils/configuration/` exists with `_module.facts`, `_module.md`, `Config.facts`,
  `Config.md`, `Config.tags.md`, `Config.flow`
- `map/src/utils/config/` does not exist
- files elsewhere that referenced `src.utils.config:...` now reference
  `src.utils.configuration:...`

### 3.2 What the diff looks like

**Inside the moved module — git does the identity work.** Because ids are module-relative,
`_module.md`, `Config.md`, `Config.tags.md` and `Config.flow` are byte-identical before and
after. `git diff -M` reports:

```
 rename map/src/utils/{config => configuration}/_module.md    (100%)
 rename map/src/utils/{config => configuration}/Config.md     (100%)
 rename map/src/utils/{config => configuration}/Config.tags.md (100%)
 rename map/src/utils/{config => configuration}/Config.flow   (96%)
 rename map/src/utils/{config => configuration}/_module.facts (100%)
 rename map/src/utils/{config => configuration}/Config.facts  (94%)
```

Six renames, two of them with small content deltas. The reviewer's first screen tells them
*this was a move*, in git's own vocabulary, with no id ledger to consult.

**The method rename, inside `Config.facts`.** Blocks are in declaration order, so the block
does not move; only its header and the `contains` line change. The full delta:

```diff
@@ -3,7 +3,7 @@ Config
   contains  _config_data
   contains  _config_source
-  contains  load_config
+  contains  load
   contains  _validate_config

@@ -17,4 +17,4 @@ Config.load_config
-Config.load_config                            classmethod
+Config.load                                   classmethod
   param     cls
   param     config_file
```

Two changed lines for a method rename. The `@@` header names the old subject because
`xfuncname` picked it up from the pre-image — which is itself useful: the hunk header reads
`@@ ... @@ Config.load_config`, so the reviewer sees what it was.

**The inbound references.** This is the expensive half, and it is measurable. Counting
statements in the x7b corpus whose object is a `src.utils.config:*` symbol and whose source
file is outside that module:

| module renamed | inbound facts to rewrite | store files touched |
|---|---|---|
| `src.utils.config` | 13 | 7 |
| `src.utils.environment` | 13 | 9 |
| `src.utils.constants` | **262** | **46** |
| `src.utils.ids` | 0 | 0 |

So the honest range for a module rename in a 67-file slice is **7 to 46 additional store
files touched, one changed line per inbound fact**. `config` happens to be cheap because
most of its inbound traffic is `Config.load_config()` qualified dispatch, which is
unresolved anyway (`?dispatch-unknown-base`) and therefore carries no id to rewrite —
an accident of the permanent dispatch hole, not a property of the design. `constants`, a
plain module of plain names, is the realistic worst case: **262 single-line changes across
46 files.**

Each of those lines is legible:

```diff
   calls     src.utils.config:Config.load_config
+  calls     src.utils.configuration:Config.load
-  calls     src.utils.config:Config.load_config
```

### 3.3 What survives, what re-mints, what a human rules on

| | |
|---|---|
| **Survives untouched** | all prose (`.md`), all tag-node content, all module-relative structural facts — carried across by git's rename detection, not by any id mechanism |
| **Re-mints** | every symbol id in the module, and one line in every inbound reference elsewhere |
| **Human rules on** | (1) *is this a move or a rewrite?* — answered by git's similarity percentage on the six renamed files, already on screen; (2) *do any `[stable-id]` tag nodes need re-homing?* — only if the module's tags are `See:`-referenced from outside, which the crawler flags as an error rather than leaving to judgment; (3) nothing else |

There is no supersession ruling, no id-merge decision, and no ledger to maintain — because
this design does not claim identity survived. It claims the **diff** shows a human that the
thing survived, which is a weaker guarantee bought much more cheaply. Anything downstream
that stored the old ids (a cached index, an open PR on another branch) is simply wrong and
must re-derive.

---

## 4. The re-derive diff scenario, walked

`Config.load_config` gains a `strict: bool = False` parameter and a call to a new
`Config._validate_schema` helper.

**Source change:** three lines (the signature, one call site, a docstring `Args:` entry) plus
the new helper.

**Store diff, in full:**

```diff
--- a/map/src/utils/config/Config.facts
+++ b/map/src/utils/config/Config.facts
@@ -8,6 +8,7 @@ Config
   contains  load_config
   contains  _validate_config
+  contains  _validate_schema
   reads     PROJECT_ROOT

@@ -19,6 +20,7 @@ Config.load_config
   param     cls
   param     config_file
+  param     strict
   calls     Config._setup_fastf1_cache
   calls     Config._setup_logging
   calls     Config._validate_config
+  calls     Config._validate_schema
   calls     builtins:open

@@ -41,0 +44,8 @@
+Config._validate_schema                       method
+  param     cls
+  param     data
+  calls     builtins:isinstance
+  calls     src.models.exceptions:ConfigurationError
+  reads     Config._config_data
```

```diff
--- a/map/src/utils/config/Config.md
+++ b/map/src/utils/config/Config.md
@@ -9,3 +9,9 @@
 - `config_file` — Name of config file in configs/ directory.
+- `strict` — Reject unknown top-level keys instead of warning.
 - *returns* — Validated configuration dictionary.
+
+## _validate_schema
+
+Check the parsed config against the expected top-level key set.
```

**Totals: 12 added lines, 0 changed lines, 0 deleted lines**, across 2 files (plus a few
lines in `Config.flow`, collapsed by default in the PR). Every added line is a sentence a
reviewer can check against the source diff sitting in the same PR: *did this function gain
that parameter? does it call that helper?*

For contrast, the same source change against a committed position-bearing JSON-lines store:
the new parameter shifts every subsequent line of `config.py`, so all ~490 statements derived
from that file below line 49 get a new `line` value and a new content hash — roughly **450
changed lines** carrying **12 lines of information**. That ratio is the entire argument for
Ruling A and Ruling B, and it is why this candidate is willing to pay for it elsewhere.

---

## 5. Tag attachment and slug drift

**On disk:** `<Class>.tags.md` beside `<Class>.facts` in the module directory, or
`_module.tags.md` for module- and free-function-anchored tags. Structure is one `##` section
per node: the typed id, then `anchor` / `origin` / `confidence` as a short list, then the tag
text one sentence per line. The `constrained-by` / `explained-by` edge is not stored — x9
proved it is a pure function of the id prefix, so storing it would be a redundant line that
changes in lockstep with the id.

**When the docstring is reworded**, the slug drifts and the node re-mints. That is not
prevented, and the design does not pretend otherwise. What it does is make the drift the most
legible thing on the reviewer's screen:

```diff
--- a/map/src/utils/config/Config.tags.md
+++ b/map/src/utils/config/Config.tags.md
@@ -3,7 +3,7 @@
-## assumption: bare-config-name-resolves-under-config-dir
+## assumption: unqualified-config-name-resolves-under-config-dir
 - anchor: `Config.load_config`
 - origin: `Assumption:` #1 in `src/utils/config.py`
 - confidence: medium — id slugged from text, not author-fixed

-A bare config_file name resolves under CONFIG_DIR, not the process working directory.
+An unqualified config_file name resolves under CONFIG_DIR, not the process working directory.
 If a caller starts passing cwd-relative paths, resolution changes silently and the cache key still matches.
```

The old and new slugs are adjacent, the changed sentence is adjacent to both, and the
unchanged second sentence stays put — the reviewer can rule *"same assumption, reworded"* or
*"different assumption"* by reading four lines. Because the section stays in the same place
in the file (tags are ordered by anchor declaration order, then by tag ordinal), a rewording
never looks like a delete-and-add somewhere else in the file.

**Two escape hatches, both already in the grammar.** If the node matters enough that drift is
unacceptable, the author writes `Assumption: [config_dir_resolution] ...` and the id is fixed
by the author, `confidence: high`, immune to rewording — this is x9's `[stable-id]` doing
exactly the job it was designed for. And the cross-module rule from §2 makes the only case
where drift breaks something *other* than a diff — an inbound `See:` — a crawler error.

**What the crawler does not do:** it does not fuzzy-match old slugs to new ones, does not
keep an alias table, and does not carry a `superseded-by` line. Every one of those would be
store state that exists to describe a change rather than to describe the code, and every one
of them is a line in the diff that a reviewer then has to interpret. The run report — printed
to the console, not committed — can say *"3 tag slugs changed, text similarity 0.91, 0.88,
0.34"* as a courtesy; only the third is worth a human's attention, and the diff already shows
it.

---

## 6. Docent feasibility

The store already *is* the site's content tree: `map/` mirrors the source tree, so the URL
`/src/utils/config/Config` maps to a directory listing, and one page per `.facts` file needs
only a walk plus a template — no database, no build-time graph load. Each page's body is the
`.md` prose verbatim, its "relates to" section is the `.facts` block rendered as links (every
object is already an id, and every id is already a path, so link resolution is string
manipulation), and its sidebar is the `.tags.md` sections. The one thing the layout does not
give the docent for free is **inbound** edges — "who calls this?" requires a reverse index,
which is a single pass over `map/**/*.facts` at build time (14,458 lines at 1×) producing an
in-memory dict, and is exactly the "DB is a disposable derived index" the substrate verdict
already sanctions.

---

## 7. Costs and risks of taking this constraint seriously

Stated as compromises, not as caveats. Six of the nine are things another candidate would
not pay.

### 7.1 It deviates from the JSON-lines verdict — the biggest one

The substrate verdict says *"statement layers JSON-lines."* This design commits **grouped
plain text**, not JSON-lines, because JSON-lines is precisely the thing that fails the
constraint: it repeats a 36-character subject on every line, wraps every field in punctuation,
and gives the eye no column to scan. `{"s": "src.utils.config:Config.load_config", "p":
"reads", "o": "src.utils.config:Config._config_data"}` is 110 characters carrying about 25
characters of information, and a reviewer cannot skim forty of them.

The mitigation is that JSON-lines survives everywhere except the committed bytes: the crawler
still *emits* the x7b line shape, a ~40-line writer groups and sorts it into `.facts`, and a
~30-line reader turns `.facts` back into the same JSON-lines stream for any consumer. The
round trip is lossless for everything the store keeps. But it is real added machinery on a
seam every producer and consumer touches, and any tool written against the JSON-lines shape
now has a converter between it and the truth. **If the human weights substrate consistency
above diff legibility, this ruling is the one to reverse — and reversing it takes most of
§4's win with it.**

### 7.2 Renames re-mint, and the inbound churn is real

Measured above: 7 to 46 store files touched for a module rename in a 67-file slice, up to 262
single-line changes. Extrapolating to f1Brainz's 443 source files, a rename of a
widely-imported module could touch a few hundred store files. Git's rename detection covers
the *moved* files elegantly and does nothing at all for the *referencing* ones. A PR that
renames a core module will have a store diff an order of magnitude larger than its source
diff — the exact failure the constraint exists to prevent, occurring on the one operation the
constraint cannot help with. This is the honest boundary of the approach, and it is why
candidate 2 exists.

### 7.3 Positions are not auditable from the store

A reviewer cannot answer "where in the file?" from `map/` alone. In a PR this is nearly
free — the source diff is on the adjacent tab — but three things do get worse: a reader
browsing the store outside a PR has no jump target beyond "find this symbol"; a bug report
about a wrong fact cannot cite a store line as evidence of *where* the crawler saw it, only
*what* it concluded; and `git blame` on a `.facts` line tells you which commit changed the
fact but not which source line produced it. Re-running the crawler regenerates
`.cmap-index/` with full positions in seconds (x7b: 2.3 s for the slice), so this is a
convenience loss, not an information loss — but it is a loss on every debugging session.

### 7.4 Occurrence counts are gone

"This helper is called 40 times from this function" and "this field is read once and written
once" are not answerable from the store. x4 validated **raw call frequency** as the one
hole-prioritization signal that beat random — and this store cannot compute it. The signal
survives only in `.cmap-index/`, which means the hole queue becomes a product of the
disposable index rather than of git truth. That is a defensible split, but it puts a
*validated measurement* on the disposable side of the line, and anyone reasoning from the
committed store alone will get de-duplicated, unweighted edges.

### 7.5 The first commit is unauditable

The design optimizes the *derivative*, not the *value*. Incremental diffs are excellent;
the initial import is ~14,500 fact lines plus prose across ~2,000 files at 1× scale, and
~145,000 lines at the 10× target. Nobody reviews that. The store's auditability claim is
honestly *"every change after the first is auditable"*, and the first one has to be trusted
on the strength of the crawler's own tests. There is no way around this that the constraint
would accept — sampling the initial commit is a tooling answer, and the constraint says no
tooling.

### 7.6 Declaration-order block sort is unstable under source reordering

Sorting blocks by declaration order is what makes a rename a two-line diff (§3.2) and an
insertion a single hunk (§4). The price: if someone reorders methods within a class, every
block after the first moved one shifts, and the diff shows the whole file rewritten.
Alphabetical sorting would be immune to that and would instead make renames move blocks.
Renames and insertions are far more common than deliberate reordering, and a source reorder
is itself a large legible source diff — so the trade is right, but it is a trade, and the
failure mode is a several-hundred-line store diff for a zero-semantics source change.
`git diff --color-moved` mitigates it for a reviewer who knows to reach for it, which is
one small step past "without tooling."

### 7.7 Merge conflicts are frequent, and must never be resolved by hand

Two branches each adding a call to the same function insert adjacent lines in the same sorted
group — a textual conflict on a semantically trivial change. Because the store is fully
derived, the correct resolution is always *take neither side and re-run the crawler on the
merged source*, which is what the `merge=cmap-rederive` driver in §1.5 does. That driver is
unbuilt machinery this design requires (roughly: ignore all three inputs, invoke the crawler
on the merged worktree, write its output). Until it exists, contributors will hand-resolve
`.facts` conflicts, and a hand-resolved derived file is a silent lie until the next full
rebuild — which the Cartographer-workflow rebuild-and-diff posture would catch, but only at
the next run.

### 7.8 File count

~2,000 files at 1× (443 modules × ~2, plus 600 classes × ~3), ~20,000 at the 10× target.
Git is comfortable there; Windows checkout and `git status` are noticeably slower, and a
`git log --follow` across a module rename works per-file only. Choosing module-level rather
than symbol-level directories already spent this budget once; going finer to make *method*
renames git-detectable would cost another 5×, and §3.2 shows the two-line in-file diff is
good enough that it is not worth it.

### 7.9 Locals are committed but hidden by default

`.flow` files are truth in git but `linguist-generated` in review. If the crawler's local
handling regresses, nobody sees it in a PR — the collapse that protects reviewers from 12,053
lines of intra-function noise also protects a bug. The mitigation is that `.flow` is the one
layer whose correctness is checkable by a test rather than by a reader (x7b's SCIP cross-check
harness covers exactly this class at 99.7% write agreement), but it means the store has a
region no human routinely reads.

---

## 8. Summary table — what this candidate buys and what it spends

| | |
|---|---|
| **Buys** | 12-line store diff for a real 3-line source change; a `git diff --stat` that reads as a symbol-level changelog; module moves rendered as git renames of byte-identical content; every line auditable against the source diff in the same PR with no tooling; ~68% smaller store than raw occurrences |
| **Spends** | the JSON-lines substrate verdict; positions and occurrence counts (to a disposable index, taking x4's validated call-frequency signal with them); rename identity entirely — up to 262 inbound line changes across 46 files; an unauditable first commit; a required custom merge driver |
| **Sharpest single trade** | **symbol-path ids instead of opaque serials.** Readable ids are what make the store auditable in a PR, and they are also the reason renames re-mint. There is no version of this candidate that keeps both. |
