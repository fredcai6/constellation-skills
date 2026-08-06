# x7a result — extractor candidate A: SCIP index + AST sidecar

**Type:** prototype · **Verdict:** the slice extracts, all six predicates, **but
the two-tool join is where the correctness lives, not where the plumbing lives**
**Date:** 2026-08-05 · **Evidence:** `.agent-work/explore-code-map/evidence/x7a/`

## Headline

The `src/utils` slice extracted completely: **3,400 statement lines** (3,300
distinct by content hash) across all six predicates, including read *and* write
edges and both directions of cross-package traffic. Nothing in the slice was
out of reach.

The cost is **565 lines of pipeline glue and three debugging rounds**, and the
important number is this: **85% of the statements (2,897 of 3,400) required
both tools to produce**. This is not a SCIP pipeline with an AST helper bolted
on. Neither half emits a correct statement set alone, and every one of the three
debugging rounds was triggered by the join returning a *plausible wrong number*
rather than an error.

| | |
|---|---|
| Statements emitted | **3,400** (3,300 distinct by content hash) |
| Needed both tools (`ref: scip+ast`) | **2,897 — 85%** |
| SCIP alone sufficed | 494 — 15% |
| AST alone sufficed | 9 — 0.3% |
| Positional join hit rate | **99.92%** (2,384 / 2,386 references) |
| Pipeline glue | **565 lines** across 3 scripts |
| Pipeline wall time on the slice | **3.2 s** (index reused, not rebuilt) |

---

## 1. What was built, and what was reused

**Reused, not rebuilt.** x1's `evidence/x1/index.scip` (22 MB, 443 documents,
6m05s to produce) was read as-is. **No re-index was run.** x1's
`decode_scip.py` (~180 lines of pure-Python protobuf wire reading) was imported
as a module — its `iter_fields`, `unpack_varints` and `classify_symbol` carried
over unchanged. The derived `defs.jsonl` / `edges.jsonl` were present but
**not used**: they lack occurrence *columns*, and the whole join keys on
(file, line, column). This is worth stating plainly — x1's derived artifacts are
not sufficient input for this candidate; the raw index is.

**Built (all under `evidence/x7a/`):**

| Script | Lines | Job |
|---|---|---|
| `slice_scip.py` | 140 | Pull the slice out of the index: every document under `src\utils\`, plus every document elsewhere that mentions a `src.utils.*` symbol, plus (round 2) every definition-with-body-span in those inbound files so an inbound edge can be attributed to a subject. |
| `ast_sidecar.py` | 169 | Walk the AST of the 68 relevant files, emitting one row per *identifier token* with its `Store`/`Load` context and both a UTF-8-byte and a character column. |
| `join.py` | 256 | Join on source position, resolve predicates, emit `statements.jsonl`. |
| **pipeline total** | **565** | |
| `diag.py`, `residue.py`, `sample.py`, `stats.py` | 154 | Throwaway diagnostics and the verification sampler. Not part of the pipeline. |

**The slice.** `src/utils` is 9 files. SCIP defines **549 symbols** in it:
**86 transformers** (79 methods, 7 classes) and **454 containers** (157
parameters, 115 module/class-level terms, 182 locals), plus 9 module symbols.
**59 files in other packages** reference it.

**Line-shape deviation.** The brief's `"ref": "scip|ast"` was extended to a
third value, **`"scip+ast"`**, because the two-value field cannot express the
finding: most statements are *joint products* and attributing them to one tool
would misreport the result. This is the one deviation.

---

## 2. Statement counts for the slice

```
reads       2,086          contains      397          param-of     157
writes        350          calls         267          documents    143
                                                    ------------------
                                                    total      3,400
```

By provenance:

| Predicate | both tools | SCIP only | AST only |
|---|---:|---:|---:|
| `reads` | 2,084 | 2 | — |
| `writes` | **350** | **0** | 0 |
| `calls` | 267 | 0 | — |
| `contains` | 196 (locals) | 201 | — |
| `param-of` | — | 157 | — |
| `documents` | — | 134 | 9 |

Cross-package traffic separates cleanly in both directions:

| | inbound (other → utils) | internal | outbound (utils → elsewhere) |
|---|---:|---:|---:|
| `reads` | 357 | 590 | 1,139 |
| `calls` | 38 | 72 | 157 |
| `writes` | 0 | 325 | 25 |

**Zero inbound writes** is a real structural claim about this slice, not a gap:
no module outside `src/utils` assigns to a `src.utils` symbol. That is exactly
the kind of fact the read/write distinction exists to produce, and it is
invisible to SCIP alone.

---

## 3. The WriteAccess gap in practice

x1 established that scip-python emits **zero** `WriteAccess` roles and asserted
(without measuring) that Python's `ast` would recover writes from `Store`
contexts. Confirmed on the slice — the slice's 3,764 occurrences carry 2,386
`ReadAccess` and 1,378 `Definition` and no writes at all. But the recovery is
**not** the one-line rule x1's phrasing implies.

### The write signal is split across *both* SCIP roles

This is the finding that cost the most time:

- A **first binding** — `DEFAULT_BASELINE_PATH = PROJECT_ROOT / "config" / ...`
  — is a SCIP **`Definition`** occurrence. It is a write.
- A **re-binding or attribute store** — `cls._config_source = None` at
  `config.py:328` — is a SCIP **`ReadAccess`** occurrence. It is also a write.

So the write set is
`(Definition ∪ ReadAccess) ∩ ast.Store`, and it lands **317 + 33 = 350**.

The naive reading — "SCIP says ReadAccess, AST says Store, therefore write" —
recovers **33 of 350 writes, 9%**. It does not crash. It emits a tidy JSONL file
with a plausible-looking `writes: 33`. I shipped that number in round 1 and
caught it only by asking why writes were 2% of reads. **A pipeline built this way
needs a ratio assertion, because the failure mode is a quiet undercount.**

### The join itself: 99.92%, after two rounds

Join key: SCIP `Occurrence.range` is 0-based `(line, char)`; CPython's
`col_offset` is a 0-based UTF-8 *byte* offset. The sidecar emits both columns and
`join.py` probes which agrees.

| Round | What was joined | Hit rate on 2,386 refs |
|---|---|---:|
| 1 | `ast.Name` + `ast.Attribute` + `arg` only | 1,999 — **83.8%** |
| 2 | + import aliases, + keyword arguments | 2,384 — **99.92%** |

The 387 round-1 misses were **not noise** — they were two whole syntactic
classes that SCIP indexes and `ast.Name` does not cover:

- **Imports (209 refs).** `from src.utils.constants import MIN_CLEAN_LAPS,
  LONG_RUN_THRESHOLD, DNF_POSITION` produces a SCIP occurrence per imported
  name *and* one for the module path. Python's AST represents these as
  `ast.alias` nodes, and — the sharp bit — **`from <module>` has no AST node at
  all**. `ImportFrom.module` is a bare string. I recover its position as
  `node.col_offset + 5`, hard-coding `len("from ")`. That works here and is
  **the most brittle line in the pipeline**: it breaks on `from  m import x`
  (double space) and on any comment or continuation between the keyword and the
  name.
- **Keyword arguments (114 refs).** `Violation(path=rel, symbol=name, ...)` —
  SCIP emits an occurrence of the *parameter* symbol at the keyword token, where
  there is no `Name` node. `ast.keyword` carries its own position, so this one
  is clean.

### Where the two tools misalign — the full residue

After round 2, **2 of 2,386** references and **14 of 210** local definitions
fail to join. Every one is explained, and they cluster into node types whose
identifiers are bare strings rather than nodes:

| Case | Count | Example |
|---|---:|---|
| `except E as e` | 9 | `except Exception as e:` — `ExceptHandler.name` is a `str` |
| Lambda parameters | 5 | `key=lambda r: r.race_date` — the walker handles `FunctionDef`, not `Lambda` |
| `global x` | 1 | `global _calendar` — `ast.Global.names` is a list of `str` |
| `import x as y` | 1 | SCIP places `local 0` at the **asname** (`pd`, col 17); `alias.col_offset` is the source name (`pandas`, col 7) |

Each is 2–3 more lines of glue. None challenges the approach; together they say
the sidecar is not "a small AST pass" but **a walker that must be taught every
node type the indexer chose to index**, discovered by residue analysis rather
than by reading a spec.

### Two misalignments that are *positional arithmetic*, not missing nodes

- **`ast.Attribute`**: `node.col_offset` points at the base expression
  (`obj` in `obj.field`), while SCIP marks the `field` token. Recovered as
  `end_col_offset - len(attr.encode("utf-8"))`. Robust, including across line
  breaks, because `end_lineno` tracks the attribute name. 3 lines.
- **Dotted import segments**: `import a.b.c` needs a row per segment, walked
  forward by `len(seg) + 1` bytes. Correct only because Python forbids
  whitespace inside a dotted name.

### The byte-vs-character column question is **unresolved, not answered**

Both conventions scored **identically (2,384)**. That is not agreement, it is
non-discrimination: f1Brainz has **no non-ASCII identifiers**, even though 37 of
the 68 files carry non-ASCII bytes in strings and comments. On a codebase with
non-ASCII identifiers this is a live coin-flip that this excursion did not
resolve, and it would present as a *partial* join failure confined to certain
files — the hardest kind to notice.

---

## 4. What the join buys, beyond writes

Three results that neither tool produces alone, which raise the join from
"overhead" to "the point":

**(a) SCIP's `method` kind conflates three different things.** Of 350
method-symbol references, only **267 are call sites**. **62 are imports** and
**21 are attribute reads** — `rel.parts` at `simplification_limits.py:66` is a
`@property`, indexed as `PurePath#parts()`. Taking SCIP's word for it makes
**24% of `calls` statements wrong**, including the absurd
`module:sampled_backtest.py --calls--> get_calendar()` emitted at the line
`from src.utils.constants import get_calendar`. Only the AST knows the position
is a call.

**(b) Local names come back for free.** x1 found locals are emitted as anonymous
`local 42` and concluded names "must be recovered by re-reading the source at
the occurrence range." The join already re-reads the source, so the name arrives
at zero marginal cost: **196 of 210 named (93%)**, e.g. `local 6` →
`vapor_pressure`. The 14 misses are the `except`/`lambda` cases above.

**(c) SCIP's `documentation` field is not a docstring field.** It carries hover
text: a fenced signature, prose *and* — for symbols with no source docstring —
a bare inferred type like `(module): yaml [unable to resolve module]`. Stripping
only the fence promoted **11 type annotations into `documents` statements**.
Filtering the hover-type prefixes and excluding locals brings it to 143. The
free win x1 spotted holds: **per-parameter prose from Google-style `Args:`
blocks** attaches to the parameter symbol itself, e.g.
`load_config().(config_file)` → "config_file: Path to config file or name of
file in configs/ directory".

---

## 5. Sample-verified correctness

24 statements drawn across every predicate and both cross-package directions,
each printed with the literal source line it claims
(`evidence/x7a/verify_sample.json`, regenerate with `sample.py`). All 24 check
out. Twelve, spanning all six predicates:

| # | Statement | Source |
|---|---|---|
| 1 | `simplification_limits/__init__:` **writes** `DEFAULT_BASELINE_PATH.` | `simplification_limits.py:28` `DEFAULT_BASELINE_PATH = PROJECT_ROOT / "config" / ...` — first binding, was a SCIP `Definition` |
| 2 | `Config#reload_config().` **writes** `Config#_config_source.` | `config.py:328` `cls._config_source = None` — **re-binding, SCIP called this ReadAccess**; verified in context at lines 318–329 |
| 3 | `Config#ensure_directories().` **writes** `local 27` (`name`) | `config.py:237` `for name, path in paths.items():` — loop target is a store |
| 4 | `Config#ensure_directories().` **calls** `builtins/dict#items().` | same line — call and write correctly separated on one line |
| 5 | `moist_air_density_from_pressure().` **contains** `vapor_pressure` | `environment.py:58` `vapor_pressure = (humidity_pct / 100.0) * saturation_pressure` — name recovered by the join |
| 6 | `DriverMapper#` **contains** `DriverMapper#map_driver_name().` | `ids.py:103` `def map_driver_name(self, first_name: str, ...)` |
| 7 | `resolve_resource_plan().` **param-of** `...(mem_per_worker_gb)` | `utilization.py:113` `mem_per_worker_gb: float = 1.0,` — a continuation line; attributed to the right function |
| 8 | `map_driver_name().(first_name)` **documents** "first_name: Driver's first name" | `ids.py:103` — parameter-level prose from the `Args:` block |
| 9 | `resolve_resource_plan().` **calls** `_detect_physical_cores().` | `utilization.py:135` `cores = physical_cores if physical_cores is not None else _detect_physical_cores()` — internal |
| 10 | `F1DataCollector#collect_race().` **calls** `constants/get_weekend_sessions().` | `collector.py:190` — **inbound cross-package**, attributed to the calling method not the file |
| 11 | `models/__init__.py` **reads** `constants/DNF_POSITION.` via import | `models/__init__.py:12` `from src.utils.constants import DNF_POSITION` — inbound, and correctly a read, not a call |
| 12 | `_radon_complexity_violations().` **calls** `pathlib/PurePath#relative_to().` | `simplification_limits.py:162` — outbound to stdlib, separated from internal by symbol origin |

**One known misclassification, unfixed.** Constructor calls land as **`reads` of
the class symbol**, not `calls`: `simplification_limits.py:140` `Violation(` is
emitted as `_function_line_violations() --reads--> Violation#`. SCIP types the
symbol `type`, not `method`, so it never enters the call path — verified against
source at lines 134–146. Fixing it means routing `type`-kind symbols through the
`callee` check too, roughly 4 more lines. It is left in as a measured defect
rather than papered over.

**On the content hash.** 3,400 statements collapse to **3,300 distinct hashes**;
91 groups repeat. These are genuine: `config.py:21`
`PROJECT_ROOT = Path(__file__).parent.parent.parent` asserts
`Config# reads PurePath#parent()` three times on one line. The hash keys
`(s, p, o, file, line)` — a *fact* identity, deliberately coarser than an
occurrence. Whether the store wants facts or occurrences is a schema decision
this excursion does not make, but the numbers differ by 3% and the choice must
be explicit.

---

## 6. Cost accounting and coupling risks

**Direct cost.** 565 lines of pipeline; **3.2 s** to run the whole slice
(1.4 s SCIP decode + 1.1 s AST walk + 0.7 s join); ~60 min of agent time, of
which the join consumed roughly two thirds across three rounds.

**How much of that is the two-tool tax?** Roughly **115 lines (~20%)** exist
only because there are two tools: the position-key index and convention probe
(~15), the split write rule (~20), the calls disambiguation by AST context
(~22), local-name recovery (~12), the hover-type filter (~10), and the sidecar
nodes that exist purely to meet SCIP occurrences — dotted imports, the
`from <module>` offset, keyword arguments, the attribute back-off (~35). The
other 450 lines are statement emission that any candidate needs.

**Coupling risks, in the order I would worry about them:**

1. **Both failure modes are silent.** x1 already found scip-python emitting a
   56-byte index on exit 0. Add: a join that misses a syntactic class produces a
   *smaller correct-looking* output, and one that misreads a role produces a
   *wrong correct-looking* one. Nothing in this pipeline raises. It needs
   invariant assertions — non-empty index, join hit rate above a floor,
   write/read ratio in a band — and those assertions are more glue.
2. **Two parsers must agree on the grammar.** scip-python is pyright-based
   (TypeScript); the sidecar is CPython 3.14 `ast`. They are independent
   implementations of the Python grammar, coupled only by byte offsets. A file
   using syntax one accepts and the other does not desynchronises the whole file
   silently. Nothing here detects that.
3. **The refresh costs are wildly asymmetric.** The AST half runs in 1.1 s for
   68 files and is trivially incremental per save. The SCIP half was **6m05s for
   a full repo index**, and x1 found no incremental mode. A live map cannot
   refresh the two halves on the same cadence, so the join must tolerate a stale
   SCIP side — which means symbol identity has to survive edits the index has
   not seen yet. Untested, and it is the load-bearing question.
4. **Symbol identity carries the index run's version string.** Every symbol
   embeds `excursion-x1` (the `--project-version` flag). Raw SCIP symbols are
   therefore not stable across index runs unless that field is pinned. My
   `short()` strips it; any consumer keying on the raw string inherits the trap.
5. **The real API is two undocumented grammars.** x1 found
   `SymbolInformation.kind` is never set, so entity classification must be
   parsed from the symbol *string*. Add the AST node-attribute surface, and this
   candidate depends on two things neither tool documents as an interface.
   The `documentation` field mixing hover types with prose (§4c) is exactly
   this hazard in miniature.

---

## 7. Scoped nulls — what was NOT tested

This tested **one package (`src/utils`, 9 files) of one Python codebase, on one
Windows machine, against one index built once**. It kills nothing outside that.

- **Not tested: any language but Python.** Both halves are Python-specific — the
  sidecar is `import ast`. The C++ repo in scope for this design
  (`superCoolSpaceSim_cpp`) has no equivalent, and scip-clang needs a
  compilation database (x6 covers that ground, not this).
- **Not tested: the whole repo.** The slice is 9 of 443 indexed files. Whether
  the 99.92% join rate holds across the repo's full syntactic variety —
  decorators, metaclasses, `match` statements, comprehension scopes, nested
  classes — is unmeasured. The residue analysis found 4 uncovered node types in
  9 files, so I expect more, and the discovery method (inspect what failed to
  join) does scale.
- **Not tested: non-ASCII identifiers.** §3 explains why: the byte-vs-character
  column choice was non-discriminating on this slice, so the pipeline's
  correctness on such a codebase is genuinely unknown, not merely unverified.
- **Not tested: incremental re-index.** Inherited from x1 and still the gating
  question. Both halves were run cold.
- **Not tested: identity across rename or move.** Only one revision of f1Brainz
  was indexed. Whether a statement's `s`/`o`/`hash` survives a file move — the
  thing a durable store needs to avoid re-minting every fact — was not
  exercised, and risk 4 above suggests it will not without work.
- **Not tested: inheritance edges.** x1 found only 105 `Relationship` records
  repo-wide, so class hierarchy is effectively absent from SCIP. I did not add an
  AST pass for `ClassDef.bases`, which would be cheap. No `inherits` predicate
  was attempted — it was not in the brief's six.
- **Not tested: whether these statements are useful.** 3,400 lines exist and are
  correct. Nobody has queried them, rendered them, or compared them to the map's
  prose. Correctness at this granularity is not the same as value, and only the
  50%-middle-bucket question x1 identified would settle it.
- **Not tested: agreement with candidate B.** By design — x7b ran independently
  on the same slice. Whether the two candidates produce the *same* statements is
  the comparison's job, not this excursion's.
- **Not compared: the 21 `attribute-not-call` and 62 `import` reclassifications**
  were verified by sampling, not exhaustively. And the single unfixed defect
  (constructor calls as `reads`, §5) is left in the output.

---

## Artifacts

All under
`C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x7a\`:

| File | What |
|---|---|
| **`statements.jsonl`** | **The deliverable — 3,400 statement lines** |
| `slice_scip.py`, `ast_sidecar.py`, `join.py` | The 565-line pipeline, in order |
| `diag.py`, `residue.py`, `sample.py`, `stats.py` | Diagnostics and the verification sampler |
| `scip_defs.jsonl`, `scip_occ.jsonl` | Slice-scoped SCIP defs (549) and occurrences (3,764) |
| `ast_ctx.jsonl` | 56,499 AST identifier rows over 68 files |
| `join_report.json`, `stats.json` | Every count quoted above |
| `residue.json` | The 16 unjoined positions, each with its source line |
| `verify_sample.json` | The 24 hand-checked statements with source |

f1Brainz was not modified. x1's index was read, never rebuilt.
