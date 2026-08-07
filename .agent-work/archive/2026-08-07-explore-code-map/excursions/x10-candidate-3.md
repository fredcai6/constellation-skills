# x10 Candidate 3 — minimal-machinery-first (YAGNI)

**Constraint:** the least store that satisfies the existing verdicts. Full rebuild + diff per
Cartographer run, git as history, no machinery for a problem not yet observed. Rename re-minting
accepted if the mitigation is a cheap ruling-time supersession step. Symbol-path identity accepted.

**The design in one sentence:** the store is a *build artifact committed to git*, mirroring the
source tree — two files per source file (`.jsonl` facts, `.md` prose) — plus exactly one
hand-authored file for the whole repo; the symbol path is the id, there is no allocator, and
nothing is stored that the crawler can recompute.

**The keystone property everything else falls out of:** the derived zone is 100% regenerable and
0% hand-edited. That single split is what lets me delete the id allocator, the position table, the
hash column, the node table, and the database, and still answer every verdict.

All numbers below are measured from `evidence/x7b/statements_all.jsonl` (44,554 occurrences,
67 files) unless marked as an estimate. Nothing was built or run — see §7.11.

---

## 1. On-disk layout, concretely

### 1.1 The tree

```
docs/map/
  README.md                                  # ~20 lines: what this is, how to rebuild,
                                             #   "never hand-edit derived/"
  rulings.jsonl                              # THE ONLY hand-authored file in the store
  derived/                                   # regenerable; blown away and rewritten each run
    MANIFEST.json
    src/
      utils/
        config.py.jsonl                      # structural layer for src/utils/config.py
        config.py.md                         # prose layer for src/utils/config.py
        constants.py.jsonl
        constants.py.md
      models/
        exceptions.py.jsonl
        exceptions.py.md
```

The path rule is a pure string transform in both directions, with no index:

```
src.utils.config:Config.load_config
  → module src.utils.config
  → source src/utils/config.py
  → docs/map/derived/src/utils/config.py.jsonl   (+ .py.md)
```

**The id is the address.** This is the second, independent argument for symbol-path identity
(§2.4): with opaque serials you need a lookup table to find where anything lives. Here you need
`replace('.', '/')`.

### 1.2 `docs/map/derived/src/utils/config.py.jsonl` — real content

Every line below is generated from the measured x7b statement set for `src/utils/config.py`,
deduplicated to facts, locals dropped, sorted by `(s, p, o)`. This is the `Config.load_config`
neighbourhood verbatim — 34 of the file's 217 lines:

```jsonl
{"s":"Config","p":"contains","o":"Config.load_config"}
{"s":"Config.get","p":"calls","o":"Config.load_config"}
{"s":"Config.load_config","p":"calls","o":"Config._setup_fastf1_cache"}
{"s":"Config.load_config","p":"calls","o":"Config._setup_logging"}
{"s":"Config.load_config","p":"calls","o":"Config._validate_config"}
{"s":"Config.load_config","p":"calls","o":"UNRESOLVED","n":2,"u":"dispatch-unknown-base"}
{"s":"Config.load_config","p":"calls","o":"builtins:open"}
{"s":"Config.load_config","p":"calls","o":"builtins:str","n":4}
{"s":"Config.load_config","p":"calls","o":"pathlib:Path"}
{"s":"Config.load_config","p":"calls","o":"src.models.exceptions:ConfigurationError","n":3}
{"s":"Config.load_config","p":"calls","o":"yaml:safe_load"}
{"s":"Config.load_config","p":"constrained-by","o":"assumption:config_cache_process_global"}
{"s":"Config.load_config","p":"reads","o":"Config.CONFIG_DIR"}
{"s":"Config.load_config","p":"reads","o":"Config._config_data","n":6}
{"s":"Config.load_config","p":"reads","o":"Config._config_source","n":2}
{"s":"Config.load_config","p":"reads","o":"yaml:","n":2}
{"s":"Config.load_config","p":"reads","o":"yaml:YAMLError"}
{"s":"Config.load_config","p":"writes","o":"Config._config_data"}
{"s":"Config.load_config","p":"writes","o":"Config._config_source"}
{"s":"Config.load_config.cls","p":"param-of","o":"Config.load_config"}
{"s":"Config.load_config.config_file","p":"param-of","o":"Config.load_config"}
{"s":"Config.reload_config","p":"calls","o":"Config.load_config"}
{"s":"load_config","p":"calls","o":"Config.load_config"}
```

(`load_config` at the bottom is the real module-level wrapper function in f1Brainz, not a
duplicate — it matters in §3.)

**The line schema, complete.** Five keys, fixed order, nothing optional beyond `n` and `u`:

| key | meaning | omitted when |
|---|---|---|
| `s` | subject id | never |
| `p` | predicate | never |
| `o` | object id, or the literal `UNRESOLVED` | never |
| `n` | how many times this fact occurs in the subject | `n == 1` |
| `u` | why unresolved | `o != "UNRESOLVED"` |

**The determinism contract** (this is what makes rebuild-and-diff work at all):

1. One file per source file, path mirrored, suffix appended (`.py` → `.py.jsonl`).
2. Lines sorted by `(s, p, o)`, byte order, ASCII.
3. Keys in the fixed order above. `json.dumps(separators=(",",":"), ensure_ascii=False)`.
4. LF endings, UTF-8, no trailing whitespace, trailing newline.
5. Ids are **relative to the file's own module** when they name something in it, absolute
   otherwise. An absolute id always contains `:`; a relative one never does. That is the whole
   disambiguation rule.
6. **No line numbers, no columns, no timestamps, no hashes, anywhere.**

Consequence: identical semantic input produces byte-identical output, so
`git diff --exit-code -- docs/map/derived ':!*MANIFEST.json'` is the drift check, and nothing
else is needed to implement "re-derive, diff, update."

### 1.3 `docs/map/derived/src/utils/config.py.md` — real content

```markdown
# src/utils/config.py

Configuration management for F1Brainz.

## Config

Configuration manager for F1Brainz system.

## Config.load_config

Load and validate configuration from YAML file.

Args:
    config_file: Name of config file in configs/ directory

Returns:
    Validated configuration dictionary

Raises:
    ConfigurationError: If config file missing or invalid

### Assumption [config_cache_process_global]

The parsed config is cached on the class and keyed only by the resolved path, so a process
that loads two different config files keeps seeing the first until reload_config() is called.
Tests that switch configs mid-process must reload.
```

Everything in this file is harvested from the docstring — it is derived, not authored here. The
authored copy lives in `src/utils/config.py`, exactly as the two-way-flow verdict requires.

**Heading grammar, which is the whole prose schema:**

- `# <source path>` — one per file.
- `## <relative subject id>` — the untagged docstring body follows, becoming that subject's
  `purpose`. This is x9's zero-tag majority case: position types it, so it earns no marker.
- `### <Tag> [<id>]` — one per x9 tag paragraph. The heading *declares the node*; the edge into
  it is the `constrained-by` / `explained-by` line in the `.jsonl`.

### 1.4 `docs/map/rulings.jsonl` — the only hand-authored file

```jsonl
{"k":"superseded","old":"src.utils.config:Config.load_config","new":"src.utils.configuration:Config.load","at":"7c1a9f2","why":"PR #412 module + method rename"}
{"k":"tombstone","id":"claim:~p1b-braking-kernel-does-not-converge","anchor":"concept:braking_model","from":"src/physics/p1b_kernel.py","at":"b9248ae","body":"A dedicated P1b braking kernel was built, measured, and removed: it reproduces the incumbent result and costs O(n^2) memory. It is the obvious thing to re-propose, and it does not work."}
```

Two record kinds, both appended by a human at ruling time, both tiny. x8 measured the tombstone
population at ~6 per repo lifetime. Supersessions are per-rename.

### 1.5 `MANIFEST.json`

```json
{"crawler":"0.1.0","built_from":"7c1a9f2","files":443,"facts":158204,"generated":"2026-08-05T21:14:03Z"}
```

Four fields, one writer, two named readers: the Docent stamps staleness by comparing `built_from`
with `git rev-parse HEAD`, and the Cartographer workflow reports coverage. This is the only index
file, and it exists because two consumers named in the verdicts require it.

### 1.6 Where the parent's lean fits, and where I deviate

**File-per-layer: kept.** `.jsonl` is the structural layer, `.md` is the concept/prose layer. The
split is real and I honour it — statements in JSON-lines, prose in markdown, per the substrate
verdict. Escaping a multi-line docstring into a JSON string would produce one unreviewable line;
this is the split earning its keep.

**Directory-per-subject: deviated.** Measured: 23,875 facts over 3,501 subjects for 67 files —
**6.8 facts per subject**. A filesystem entry per 6.8 facts is a ~25× inode overhead; f1Brainz
repo-wide would be ~23,000 subject directories, and the brief's 10× target ~230,000. What
directory-per-subject buys is diff locality within a file — which sorted lines in a deterministic
file already provide, at line granularity, for free. Cut; see the deletion test in §6.

### 1.7 Scale, measured and projected

| | facts | store bytes |
|---|---|---|
| 67-file slice, all statements deduped to facts | 23,875 (from 44,554 occurrences, **46.4% collapse**) | 2.3 MB |
| same, locals + own-param reads dropped (boundary-stored default) | **14,603** | **1.53 MB** |
| f1Brainz repo-wide (×443/67, estimate) | ~97,000 | ~10 MB |
| brief's 10× target (estimate) | ~970,000 | ~101 MB |

Average line: 98 bytes uncompressed. 10 MB of text across ~900 files is an unremarkable git repo.
101 MB is at the edge — the escape hatch is §7.6, and it is a `.gitignore` line, not a redesign.

---

## 2. Identity scheme

### 2.1 The ids

| class | form | example |
|---|---|---|
| module | `<dotted.path>:` | `src.utils.config:` |
| class | `<module>:<Name>` | `src.utils.config:Config` |
| function / method | `<module>:<Qual.name>` | `src.utils.config:Config.load_config` |
| parameter | `<function id>.<param>` | `src.utils.config:Config.load_config.config_file` |
| external | `<package>:<symbol>` | `yaml:safe_load`, `builtins:str`, `pathlib:Path` |
| unresolved | the literal `UNRESOLVED` + a `u` reason | — |
| concept, author-declared | `<kind>:<bracket-id>` | `assumption:config_cache_process_global` |
| concept, slugged | `<kind>:~<slug-of-first-clause>` | `claim:~the-brake-onset-knee-is-benign` |
| local | **not stored** | — |

Two conventions carry real weight:

- **`UNRESOLVED` is not a node.** It is a typed absence. x7b measured 3,428 unresolved sites
  across 67 files, 98.6% third-party dispatch, and the verdict is that this is a permanent class,
  not a gap to close. Minting a node per unresolved site would create ~3,400 phantom nodes with no
  referent. It stays a marker with a reason code.
- **The `~` prefix is the confidence field.** x9 rules that an author-supplied `[stable-id]` is
  high confidence and a slugged id is medium, because the slug is not guaranteed across a
  rewording. Rather than carry a `confidence` column on every concept edge, the id itself is
  marked: `~` present means slugged means medium. One character, no field, and it makes slug drift
  visible in the diff (§5.2), which is the behaviour that actually matters.

### 2.2 Who assigns

**Nobody.** Every id is a pure function of the source text at the crawl point:

- Structural ids come from the module path and the dotted qualified name — Python's own name
  resolution, so a within-scope collision is a syntax error the interpreter rejects before the
  crawler runs, and a cross-scope collision gets a different prefix by construction.
- Concept ids come from the author's bracket, or from a slug of the tag paragraph's first clause.

There is no allocator, no counter, no registry, no persisted id file, and therefore no
merge-conflict class on one, no bootstrap ordering, and no id→symbol resolution step in any
consumer.

### 2.3 Stability, stated honestly

**The guarantee is exactly this: an id is stable as long as its spelling in the source is
stable.** No more.

| id | survives | re-mints on |
|---|---|---|
| module | any edit inside the file | file move or rename |
| class | any edit, including all method changes | class rename, file move |
| function / method | body changes, signature changes, docstring rewrites | its own rename, enclosing class rename, file move, moving between classes |
| parameter | reorder, type-annotation change, default change | its own rename, or anything that re-mints its function |
| concept, `[stable-id]` | rewording, anchor rename, file move, **even deletion of the anchor** | changing the bracket text |
| concept, slugged | any edit that leaves the tag's first clause alone | rewording the first clause, or anything re-minting the anchor |

**The asymmetry is the entire design.** The layer that re-mints freely (structural) is the layer
where nothing was hand-authored — x7b rebuilds it in 2.3 s for 67 files. The layer that is
expensive to recreate (concept prose, authored by a human or an agent under the standard) already
has an author-supplied stable id built into the grammar x9 recommends. So the store needs no
identity machinery, because the only content worth protecting already carries its own.

### 2.4 Two arguments for symbol paths over opaque serials

1. **The one the constraint requires.** An allocator buys id stability for content someone paid to
   create. The structural layer has no such content.
2. **The one that holds regardless of the constraint.** The id *is* the file address (§1.1). Under
   opaque serials, "where do I find node 41822" needs an index; the index is state; state in a
   store designed to be 100% derived is exactly the thing that gets stale, conflicts on merge, and
   needs its own repair path.

The honest cost of both: cross-references *out of* the store break on rename. §3 handles that.

---

## 3. The rename scenario, walked

**Change:** `src/utils/config.py` → `src/utils/configuration.py`, and `Config.load_config` →
`Config.load`. Measured context: `Config.load_config` is the subject of 18 facts and the object of
4; **7 files import `src.utils.config`** (`src/data/collector.py`,
`src/data/database/{__init__,_ingest,_results,_telemetry_store}.py`, `src/data/load_fastf1.py`,
`src/physics/physics_config.py`).

### Step 1 — the developer makes the change

They must fix all 7 importers and every `Config.load_config(` call site, or the code does not run.
**This is the observation that makes re-minting affordable:** a rename that re-mints ids is a
rename the interpreter already forced the developer to propagate. The store's churn is bounded by
churn the PR already contains.

### Step 2 — the Cartographer run rebuilds

Full rebuild of `docs/map/derived/`, ~10 s for f1Brainz at x7b's measured 2.3 s / 67 files.

### Step 3 — what git status shows

```
renamed:    docs/map/derived/src/utils/config.py.jsonl -> docs/map/derived/src/utils/configuration.py.jsonl
renamed:    docs/map/derived/src/utils/config.py.md    -> docs/map/derived/src/utils/configuration.py.md
modified:   docs/map/derived/src/data/collector.py.jsonl
modified:   docs/map/derived/src/data/database/__init__.py.jsonl
modified:   docs/map/derived/src/data/database/_ingest.py.jsonl
modified:   docs/map/derived/src/data/database/_results.py.jsonl
modified:   docs/map/derived/src/data/database/_telemetry_store.py.jsonl
modified:   docs/map/derived/src/data/load_fastf1.py.jsonl
modified:   docs/map/derived/src/physics/physics_config.py.jsonl
modified:   docs/map/derived/MANIFEST.json
```

**Git's own rename detection fires, and that is a payoff of mirroring the source tree.** The
content similarity is >90%, well over git's 50% threshold, so git reports a rename rather than a
delete-plus-add. Rename detection for the file-move half of the problem costs zero design — it is
inherited from the substrate the verdict already chose.

### Step 4 — the file move alone produces **zero content diff**

Because `s` and same-module `o` values are relative (rule 5 of the determinism contract), the
module name does not appear anywhere inside its own `.jsonl`. Cross-module `o` values are
absolute but point at *other* modules, which did not move. So renaming the file changes the
filename and not one byte inside it.

### Step 5 — the symbol rename diff, line by line

```diff
--- a/docs/map/derived/src/utils/config.py.jsonl
+++ b/docs/map/derived/src/utils/configuration.py.jsonl
@@
-{"s":"Config","p":"contains","o":"Config.load_config"}
+{"s":"Config","p":"contains","o":"Config.load"}
-{"s":"Config.get","p":"calls","o":"Config.load_config"}
+{"s":"Config.get","p":"calls","o":"Config.load"}
+{"s":"Config.load","p":"calls","o":"Config._setup_fastf1_cache"}
+{"s":"Config.load","p":"calls","o":"Config._setup_logging"}
+{"s":"Config.load","p":"calls","o":"Config._validate_config"}
+{"s":"Config.load","p":"calls","o":"UNRESOLVED","n":2,"u":"dispatch-unknown-base"}
+{"s":"Config.load","p":"calls","o":"builtins:open"}
+{"s":"Config.load","p":"calls","o":"builtins:str","n":4}
+{"s":"Config.load","p":"calls","o":"pathlib:Path"}
+{"s":"Config.load","p":"calls","o":"src.models.exceptions:ConfigurationError","n":3}
+{"s":"Config.load","p":"calls","o":"yaml:safe_load"}
+{"s":"Config.load","p":"constrained-by","o":"assumption:config_cache_process_global"}
+{"s":"Config.load","p":"reads","o":"Config.CONFIG_DIR"}
+{"s":"Config.load","p":"reads","o":"Config._config_data","n":6}
+{"s":"Config.load","p":"reads","o":"Config._config_source","n":2}
+{"s":"Config.load","p":"reads","o":"yaml:","n":2}
+{"s":"Config.load","p":"reads","o":"yaml:YAMLError"}
+{"s":"Config.load","p":"writes","o":"Config._config_data"}
+{"s":"Config.load","p":"writes","o":"Config._config_source"}
+{"s":"Config.load.cls","p":"param-of","o":"Config.load"}
+{"s":"Config.load.config_file","p":"param-of","o":"Config.load"}
-{"s":"Config.load_config","p":"calls","o":"Config._setup_fastf1_cache"}
-{"s":"Config.load_config","p":"calls","o":"Config._setup_logging"}
-{"s":"Config.load_config","p":"calls","o":"Config._validate_config"}
-{"s":"Config.load_config","p":"calls","o":"UNRESOLVED","n":2,"u":"dispatch-unknown-base"}
-{"s":"Config.load_config","p":"calls","o":"builtins:open"}
-{"s":"Config.load_config","p":"calls","o":"builtins:str","n":4}
-{"s":"Config.load_config","p":"calls","o":"pathlib:Path"}
-{"s":"Config.load_config","p":"calls","o":"src.models.exceptions:ConfigurationError","n":3}
-{"s":"Config.load_config","p":"calls","o":"yaml:safe_load"}
-{"s":"Config.load_config","p":"constrained-by","o":"assumption:config_cache_process_global"}
-{"s":"Config.load_config","p":"reads","o":"Config.CONFIG_DIR"}
-{"s":"Config.load_config","p":"reads","o":"Config._config_data","n":6}
-{"s":"Config.load_config","p":"reads","o":"Config._config_source","n":2}
-{"s":"Config.load_config","p":"reads","o":"yaml:","n":2}
-{"s":"Config.load_config","p":"reads","o":"yaml:YAMLError"}
-{"s":"Config.load_config","p":"writes","o":"Config._config_data"}
-{"s":"Config.load_config","p":"writes","o":"Config._config_source"}
-{"s":"Config.load_config.cls","p":"param-of","o":"Config.load_config"}
-{"s":"Config.load_config.config_file","p":"param-of","o":"Config.load_config"}
-{"s":"Config.reload_config","p":"calls","o":"Config.load_config"}
+{"s":"Config.reload_config","p":"calls","o":"Config.load"}
-{"s":"load_config","p":"calls","o":"Config.load_config"}
+{"s":"load_config","p":"calls","o":"Config.load"}
```

**22 lines rewritten** in a 217-line file for a 46-subject module. `Config.load` sorts before
`Config.load_config`, so the block moves up a little and the removed/added runs are adjacent — a
reviewer reads it as one block, not scattered. The module-level `load_config` wrapper is untouched
except for its one outbound edge, which is correct: it did not get renamed.

Each importer file changes **one line**:

```diff
--- a/docs/map/derived/src/data/collector.py.jsonl
+++ b/docs/map/derived/src/data/collector.py.jsonl
-{"s":"","p":"imports","o":"src.utils.config:Config"}
+{"s":"","p":"imports","o":"src.utils.configuration:Config"}
```

Total store diff: 22 lines in one file + 7 lines across 7 files + MANIFEST. **29 semantic lines
for a rename touching a whole module.**

### Step 6 — the supersession report the run prints

```
SUPERSESSION REPORT — rebuild at 7c1a9f2 (was a31fc3e)

  file renamed (git rename detection, 100% content match)
    src/utils/config.py  ->  src/utils/configuration.py

  subjects gone (3)                                subjects new (3)
    src.utils.config:Config.load_config   18 facts   src.utils.configuration:Config.load   18
    ...load_config.cls                     1          ...load.cls                            1
    ...load_config.config_file             1          ...load.config_file                    1

  AUTO-SUPERSEDED (fact set identical modulo id, 1:1, >=3 facts) — 1
    src.utils.config:Config.load_config  ->  src.utils.configuration:Config.load   [18/18]

  CONFIRM (parameters follow their function; <3 facts) — 2
    ...load_config.cls          -> ...load.cls           [y/n]
    ...load_config.config_file  -> ...load.config_file   [y/n]

  concept nodes carried unchanged (1)
    assumption:config_cache_process_global   (author-declared id; anchor moved, id did not)

  orphaned concept nodes (0)
```

**The pairing heuristic, in full.** For each gone subject and each new subject, build the multiset
of `(p, o)` pairs with the subject's own id erased from `o` as well. Identical multisets and a 1:1
match → propose. This is a dict lookup on a tuple of already-computed values: no similarity model,
no embedding, no git-blame walk. Auto-confirm when the match is 100%, 1:1, and the subject has ≥3
facts; ask otherwise.

### Step 7 — the human's ruling

One line appended to `rulings.jsonl`:

```json
{"k":"superseded","old":"src.utils.config:Config.load_config","new":"src.utils.configuration:Config.load","at":"7c1a9f2","why":"PR #412 module + method rename"}
```

That is the complete rename-survival mechanism: a redirect table read by any consumer that
resolves an id and misses.

### Step 8 — what survived, what re-minted, what a human had to rule on

| | outcome |
|---|---|
| **Survived with no action** | every fact (rebuilt identically), all prose (it moved with the docstring), and the tag node `assumption:config_cache_process_global` — because its id came from the author's bracket, not from its anchor |
| **Re-minted** | all structural ids in the module. **Cost: zero**, because none of it was hand-authored |
| **Broke without the ruling** | (a) any `See: struct:src.utils.config:Config.load_config` written in a docstring elsewhere; (b) external citations — issues, PR bodies, decision files, a Docent URL someone bookmarked |
| **Human ruled on** | 2 confirms (the parameters), 0 orphan adjudications, ~15 seconds |

**The store is complete and correct without `rulings.jsonl`.** The redirect table is a
convenience index for references that point *into* the store from outside it. That is why it is
YAGNI-legal: it is not load-bearing for any query the store itself answers.

---

## 4. The re-derive diff scenario, walked

**Change:** `Config.load_config` gains a `strict: bool = False` parameter and a call to
`cls._validate_strict()`. The new code is inserted at line 49 and pushes ~350 lines down.

### The full store diff a PR reviewer sees

```diff
--- a/docs/map/derived/src/utils/config.py.jsonl
+++ b/docs/map/derived/src/utils/config.py.jsonl
@@ -12,6 +12,7 @@
 {"s":"Config.load_config","p":"calls","o":"Config._setup_logging"}
 {"s":"Config.load_config","p":"calls","o":"Config._validate_config"}
+{"s":"Config.load_config","p":"calls","o":"Config._validate_strict"}
 {"s":"Config.load_config","p":"calls","o":"UNRESOLVED","n":2,"u":"dispatch-unknown-base"}
@@ -24,6 +25,7 @@
 {"s":"Config.load_config","p":"reads","o":"Config._config_source","n":2}
+{"s":"Config.load_config","p":"reads","o":"Config.load_config.strict"}
 {"s":"Config.load_config","p":"reads","o":"yaml:","n":2}
@@ -30,6 +32,7 @@
 {"s":"Config.load_config.config_file","p":"param-of","o":"Config.load_config"}
+{"s":"Config.load_config.strict","p":"param-of","o":"Config.load_config"}
 {"s":"Config.reload_config","p":"calls","o":"Config.load_config"}
@@ -95,0 +98 @@
+{"s":"Config","p":"contains","o":"Config._validate_strict"}
+{"s":"Config._validate_strict","p":"reads","o":"Config._config_data"}
+{"s":"Config._validate_strict.cls","p":"param-of","o":"Config._validate_strict"}
```

```diff
--- a/docs/map/derived/src/utils/config.py.md
+++ b/docs/map/derived/src/utils/config.py.md
@@
     config_file: Name of config file in configs/ directory
+    strict: Raise on unknown configuration keys instead of warning
@@
+## Config._validate_strict
+
+Reject configuration keys not present in the schema.
```

**Six added statement lines, zero removed, zero moved.** Every one of them is the semantic change:
one new parameter, one new call, one parameter read, and the three lines that are the new private
method itself.

**The number that justifies dropping positions.** 427 of the 493 statement occurrences in
`src/utils/config.py` (87%) sit at or below line 49. With line numbers in the store, this 3-line
semantic edit rewrites ~427 store lines and buries the six that matter. Without them, the diff is
exactly the change. That single measurement is why the no-positions rule is the first thing I
would defend in this design.

**Callers show no diff at all.** If `src/data/collector.py` now calls
`Config.load_config(strict=True)`, the `calls` fact already existed and keyword arguments are not
stored, so `collector.py.jsonl` is byte-identical. The store shows the interface changing, not
every site adapting to it — which is what a reviewer wants from a map and is a direct consequence
of storing facts rather than occurrences.

**And a pure reformat produces an empty diff.** Reindenting the whole file, moving methods around,
or running a formatter changes nothing in the store, because there is nothing positional in it.

---

## 5. Tag attachment

### 5.1 An `Assumption:`-minted node on disk

Written in the source, per x9's grammar (`src/utils/config.py`, inside `load_config`'s docstring):

```
Assumption: [config_cache_process_global] The parsed config is cached on the
    class and keyed only by the resolved path, so a process that loads two
    different config files keeps seeing the first until reload_config() is
    called. Tests that switch configs mid-process must reload.
```

It lands in exactly two places, and no third:

**Prose layer** — `config.py.md`, nested under its anchor's `##` heading (§1.3). The `###` heading
*is* the node declaration; the body is the node's text.

**Structural layer** — `config.py.jsonl`, one line:

```json
{"s":"Config.load_config","p":"constrained-by","o":"assumption:config_cache_process_global"}
```

Per x9's mechanical rule, the edge type is a pure function of the target's kind prefix, so the
crawler needs no edge vocabulary and the store needs no edge-type column beyond `p`.

**`origin` is structural, not positional.** x9 requires an `origin: {tag, path, line}` so that
write-back is a pointer lookup rather than a similarity match (org-babel's law). My `origin` is the
same pointer with the line number removed, and it is not a stored field — it is the node's own
address in the tree:

```
docs/map/derived/src/utils/config.py.md
  ## Config.load_config          →  subject
  ### Assumption [config_...]    →  tag kind + id
```

A write-back tool opens `src/utils/config.py`, finds `Config.load_config`, finds the docstring
paragraph starting `Assumption:` whose bracket-id matches, and replaces it. That satisfies
org-babel's law — the emitted text carries a pointer back to its source — with a symbolic pointer
instead of a positional one, and it survives every edit above it in the file.

### 5.2 Docstring reworded — slug drift

**The author-declared case (shown above): nothing happens.** Reword the whole paragraph, move the
function, rename the file — the id is `config_cache_process_global` because the author typed it.
The `.md` body changes; the `.jsonl` line does not. This is the case the design steers authors
toward.

**The slugged case:** had the author omitted the bracket, the id would be
`assumption:~the-parsed-config-is-cached-on-the-class`. Rewording the first clause re-mints it:

```diff
--- a/docs/map/derived/src/utils/config.py.jsonl
+++ b/docs/map/derived/src/utils/config.py.jsonl
-{"s":"Config.load_config","p":"constrained-by","o":"assumption:~the-parsed-config-is-cached-on-the-class"}
+{"s":"Config.load_config","p":"constrained-by","o":"assumption:~config-is-cached-per-process-and-keyed-by-path"}
```

```diff
--- a/docs/map/derived/src/utils/config.py.md
+++ b/docs/map/derived/src/utils/config.py.md
-### Assumption [~the-parsed-config-is-cached-on-the-class]
+### Assumption [~config-is-cached-per-process-and-keyed-by-path]
```

The supersession report catches it with a pairing rule even cheaper than the structural one —
**same anchor subject, same tag kind, exactly one gone and one new → propose**; more than one of
either → ask:

```
  concept nodes re-minted (1)
    assumption:~the-parsed-config-is-cached-on-the-class
      -> assumption:~config-is-cached-per-process-and-keyed-by-path
      anchor unchanged: Config.load_config     [confirm / reject]
      NOTE: this node has no author id. Add `Assumption: [some_id]` in the
            docstring and this stops happening.
```

**That note is the actual mitigation.** I do not build identity stability for slugged concept
nodes; I make the recurring cost visible at the moment the author is looking at the diff, and give
them the one-token fix. A recurring annoyance converted into a one-time authoring correction is
the YAGNI answer to slug drift, and it uses machinery the grammar already ships.

### 5.3 The anchor is deleted — the tombstone gate

A gone subject that carried a concept node, with no proposed pair, is a genuine orphan. It is the
only case that reaches the ruling gate the tombstone verdict describes:

```
  ORPHANED concept nodes (1) — rule: promote to tombstone, or let it die
    claim:~p1b-braking-kernel-does-not-converge
      anchor src.physics.p1b_kernel:solve  (deleted at b9248ae)
      body:  "A dedicated P1b braking kernel was built, measured, and removed..."
      [tombstone <concept-id> / drop]
```

Promotion appends the tombstone line shown in §1.4. This is the one place prose lives outside a
`.md` file, and it has to: by construction there is no source file left to hold it. x8's measured
volume (~6 per repo lifetime) is what makes a single flat file the right answer.

---

## 6. Docent feasibility

The Docent walks `docs/map/derived/` as a directory tree, so the source tree's shape *is* the
site's navigation with no sitemap to build: one page per source file, the `.md` rendered as the
body and the `.jsonl` grouped by subject into outgoing-link lists, with incoming links coming from
a single in-memory inverted index of `o → s` built at site-build time (23,875 facts for f1Brainz —
milliseconds, no database). Concept nodes get their own pages by collecting every
`### <Tag> [<id>]` heading across the tree, and every cross-link resolves without a lookup table
because ids are text: a structural id maps to a file path by string transform, and a concept id
maps to a heading anchor. Staleness stamping is `MANIFEST.json`'s `built_from` compared against
`git rev-parse HEAD`, which is the only reason `MANIFEST.json` exists.

---

## 7. The cuts, defended — and the costs

### 7.0 The deletion test, applied to each cut

The test: **if this mechanism were needed later, what reappears across N callers?**

| cut | if reinstated later, what reappears | verdict |
|---|---|---|
| **A. Opaque serial ids + allocator** | an id→symbol resolution step in *every* consumer (Docent, dev skills, drift check, write-back), a persisted allocator file that is hand-edited state inside a zone designed to be 100% derived, a merge-conflict class on that file across parallel branches, and an index to answer "where does node 41822 live" | **cut.** It buys stability only for authored content; the structural layer has none, and the concept layer already has `[stable-id]` — a free, author-supplied allocator with better semantics |
| **B. Line/column** | one new file class, `<src>.py.positions.jsonl`, one writer (the crawler), regenerable, gitignorable. **Zero consumer changes** — existing consumers ignore it | **cut.** Pure additive retrofit, and it costs 87% spurious diff churn today (§4) |
| **C. Per-statement content hash** | nothing on disk. `sha256` over the sorted lines with a given `s`, computed by whoever wants it | **cut.** See §7.2 — this is the one verdict I satisfy by a different mechanism |
| **D. Directory-per-subject** | a re-split of one deterministic generator's output. Ids do not encode the file, so **no consumer semantics change** — only the writer and the path transform | **cut.** Cheap to retrofit precisely because ids are addresses, not locations |
| **E. A database** | the verdict already calls a DB a disposable derived index. Building one now indexes queries nobody has written | **cut** |
| **F. A separate node table** | nothing. A node exists iff it appears as `s` or `o`. If node *attributes* ever matter (kind, visibility, signature), they become predicates — `{"s":"Config.load_config","p":"kind","o":"classmethod"}` — in the file that already exists | **cut.** The statement form is universal; attributes need no new file class |
| **G. Occurrence-level storage** | a positions file (same as B) plus the 46.4% size increase. Distinct-caller count and total call count both survive via `n` | **cut** |

### 7.1 Rename re-mints the structural layer, always

The mitigation is a report and a redirect line, not identity. Two named limits:

- **The confirm queue is the workflow's soft spot.** A refactor renaming 40 symbols means up to 40
  pairings; auto-confirm handles the clean ones, but partial matches (a rename *plus* a body
  change) all land on the human at once. **Trigger to revisit:** more than ~20 non-auto-paired
  supersessions in a run, twice.
- **Auto-supersession can mis-pair.** Two trivially-identical functions — one deleted, one added in
  the same run — with matching fact sets get linked silently. Guards: ≥3 facts and a 1:1 match.
  Residual risk accepted; the consequence is a wrong redirect, never a wrong fact.

### 7.2 The per-node content hash verdict is satisfied by a different mechanism

The substrate verdict names a per-node content hash as the change-detection mechanism for forced
supersession. I store none. The textual diff detects change directly at statement granularity, and
git's blob sha is a free per-file hash. **This is a real deviation from the letter of the verdict**
and I am flagging it rather than claiming compliance: if a consumer genuinely needs a node-level
hash it is a `sha256` over the sorted lines with that `s`, computed at read time, no store change
(cut C). If the human wants the letter honoured, adding a `nodes.tsv` per file is a small, purely
additive change — but it re-introduces a derived value that can disagree with the file it
summarises.

### 7.3 The redirect table is unbounded and never garbage-collected

After 200 renames, `rulings.jsonl` has 200 redirect lines, and an id renamed twice needs transitive
chasing (A→B→C). I build no chain collapse and no compaction. **Trigger to revisit:** any chain
longer than 2, or the file passing ~200 lines.

### 7.4 No positions means the store cannot answer "where"

This is the sharpest single loss. Any consumer wanting a line number must re-run the crawler (2.3 s
/ 67 files) or grep. The Docent's "jump to source" links are symbol-name links, not line links —
worse than a line anchor, better than nothing, and an editor resolves a symbol name more reliably
than a stale line number anyway. Named honestly: this is the cost I traded for §4's clean diffs,
and it is the trade the whole design turns on.

### 7.5 Facts, not occurrences — what actually goes

x4's two validated hole-priority signals both survive: distinct-caller count is the number of
distinct `s` with a `calls` edge to a target, and total call count is the sum of `n` over those
lines. What is genuinely lost is the ability to **enumerate** call sites — "show me the 17 places
this is called" becomes "17 calls from 4 subjects." A consumer wanting the sites re-runs the
crawler.

Separately, `n` is a deliberate diff-noise source: adding one more `str()` call flips `"n":4` to
`"n":5`, a real line change for a non-structural edit. I kept it because x4 validated the signal it
carries.

### 7.6 The scale ceiling is ~100 MB, and the escape hatch is a gitignore line

At the brief's 10× target the derived zone is ~101 MB of text. The mitigation is to stop committing
`derived/**/*.jsonl` and keep only `derived/**/*.md` + `rulings.jsonl` in git, regenerating
structure on demand. That degrades "git is truth" for the structural layer to "source is truth,
structure is a cache" — which is arguably already what the code-is-truth verdict says. It is a
graceful degradation rather than a redesign **only because** the derived zone is 100% regenerable,
which is the same property every other cut rests on. Named, not solved.

### 7.7 Locals are not stored

Per the boundary-stored default (open thread 9), 12,053 local statements and 5,867 own-parameter
reads are dropped — 40% of the corpus. A consumer asking "what does this function bind internally"
re-runs the crawler on one file. Cheap in milliseconds, but it is a second code path, and if
locals turn out to matter for the dev-agent skills the store grows 40% overnight.

### 7.8 The relative-id convention is the one piece of cleverness, and it breaks on C++

"Absolute ids contain `:`, relative ones do not" holds for Python, where symbol names cannot
contain a colon. **C++ `Foo::bar` contains `:` and would be misread as absolute.** A future C++
adapter must either not relativize or use a different absolute marker. Named now because it is
exactly the kind of thing that gets discovered in the adapter's third debugging round.

### 7.9 The `~` slug marker is a convention, not a field

Confidence is readable only by inspecting the id's first character. If a third confidence level
ever appears, a real field reappears on every concept edge. One level of encoding, one failure mode.

### 7.10 `MANIFEST.json` is never diff-clean

It carries the built-from commit, so it changes on every run even when nothing else did. Deliberate,
and it means the drift check must exclude it:
`git diff --exit-code -- docs/map/derived ':!*MANIFEST.json'`. A reviewer who skims will see one
modified file in every map PR and must learn to ignore it.

### 7.11 Nothing here was built or run

Every diff in this document is hand-derived from x7b's measured statement set, not produced by a
crawler. The determinism guarantee — byte-identical rebuild from identical semantic input — is a
design requirement I am asserting, not an observation. x7a's warning applies with full force: both
failure modes in this pipeline are silent, and a rebuild that quietly drops a syntactic class
produces a smaller correct-looking store. The first thing to build is not the store; it is the
assertion that a rebuild with no source change produces an empty diff.

---

## Summary against the comparison axes

- **Depth.** Two file kinds, five line keys, one heading grammar, one hand-authored file. The
  behaviour learned per interface is high because there are almost no interfaces.
- **Locality.** A change concentrates: §4's three-line edit produces six store lines and touches
  one file. A rename scatters proportionally to the code churn the PR already contains (29 lines,
  8 files), and the file-move component costs zero content diff.
- **Seam placement.** One writer (the crawler) owns `derived/` entirely; one human-owned file
  (`rulings.jsonl`) sits outside it. Consumers read text and resolve ids by string transform, with
  no index in between. The staleness seam is one `MANIFEST.json` field.
- **Testability.** The central invariant is one command: rebuild with no source change, then
  `git diff --exit-code`. Every other property (rename churn, insertion churn, reformat-immunity)
  is a diff assertion on a fixture repo.
- **What I would fix first if this wins.** The auto-supersession mis-pairing guard (§7.1) and the
  C++ colon collision (§7.8) — both cheap now, both expensive after adoption.
