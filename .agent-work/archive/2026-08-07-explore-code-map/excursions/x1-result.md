# x1 result — scip-python on f1Brainz: degree-of-coverage measurement

**Type:** prototype / measurement · **Verdict:** POSITIVE with a sharp boundary
**Date:** 2026-08-05 · **Evidence:** `.agent-work/explore-code-map/evidence/x1/`

## Headline

scip-python runs on f1Brainz after one Windows-specific patch, and produces a
complete, accurate structural index: 443 files, 3,686 functions, 600 classes,
5,331 named module/class-level containers, 220,915 occurrences.

Against the existing map, the split is:

| Bucket | Map lines | Share |
|---|---|---|
| (a) procedurally reproducible from the SCIP index alone | ~552 | **~7%** |
| (b) partially supportable — SCIP gives the skeleton, prose is judgment | ~3,897 | **~50%** |
| (c) untouchable by extraction — capabilities, decisions, constraints, the "why" | ~3,344 | **~43%** |

Total map: 7,793 lines across 36 files.

The two numbers that matter most point in opposite directions, and both are real:

- **The structural spine is 100% reproducible.** SCIP independently confirmed
  **34 of 34** container-to-container dependency edges the map curates by hand,
  missed **zero**, and found **5 genuine edges the map does not list**. On this
  one job, extraction is not "nearly solved" — it is solved, and it is *more
  complete than the human map*.
- **That spine is ~7% of the map's text.** The other 93% is behavioral prose
  hung off the skeleton, and half of it has no structural anchor at all.

---

## 1. Did it run

Yes. **~15 minutes wall time to a working index**, including one real failure.

| Step | Command | Result |
|---|---|---|
| Environment check | `node --version; npm --version; python --version; go version` | node **v24.15.0**, npm **11.17.0**, Python **3.14.3**, **no Go** (so the `scip` CLI was not an option — decoder written in Python instead) |
| Install | `npm install --no-save @sourcegraph/scip-python` | 42 packages, **30s**. Version **0.6.6** |
| **Attempt 1 — FAILED** | `./node_modules/.bin/scip-python index --help` | `SyntaxError: Invalid regular expression: /\/g: \ at end of pattern` at `src/virtualenv/PythonEnvironment.ts:4` |
| Attempt 2 — WSL fallback | `wsl --list --quiet` | "The Windows Subsystem for Linux is not installed." Not available. |
| **Attempt 3 — patch, SUCCEEDED** | one-line patch to `dist/scip-python.js` | `--help` works |
| Index run 1 | `--cwd "C:/Programs/f1Brainz"` (forward slashes) | Ran 3m20s, exit 0, **but emitted a 56-byte index** — silently empty. Forward-slash cwd does not match pyright's normalized paths, so no document survived the project-file filter. **No error was raised.** |
| **Index run 2 — SUCCEEDED** | `--cwd "C:\Programs\f1Brainz"` (backslashes) | **6m05s**, 443 documents, **22,179,398 bytes** |

**The bug.** scip-python 0.6.6 does `new RegExp(path.sep, 'g')`. On Windows
`path.sep` is `\`, which is not a valid regex. The package is simply broken on
Windows out of the box. The patch:

```
RegExp(o.sep,"g")   ->   RegExp(o.sep==="\\"?"\\\\":o.sep,"g")
```

applied to `node_modules/@sourcegraph/scip-python/dist/scip-python.js` (one
occurrence).

**The working command:**

```
node ./node_modules/@sourcegraph/scip-python/index.js index \
  --cwd "C:\Programs\f1Brainz" \
  --project-name f1brainz --project-version excursion-x1 \
  --output "<evidence>\index.scip"
```

f1Brainz was never modified. Its own `pyrightconfig.json` (`include: ["src"]`,
excluding `.venv`) drove file selection; output went to the evidence dir.

**Two adoption costs worth naming.** The Windows regex bug is a hard blocker for
any Windows-first user — the tool cannot run unpatched. And the empty-index
failure is worse than a crash: **exit 0, a success message, and a 56-byte file.**
Any pipeline built on this needs a non-empty assertion on the output.

**Decoding.** No Go, so no `scip` CLI. `evidence/x1/decode_scip.py` is a ~180-line
pure-Python protobuf wire-format reader for the SCIP schema — no protoc, no
protobuf runtime. It decoded the 22 MB index in seconds. This was cheap and is
worth knowing: **decoding SCIP does not require the Sourcegraph toolchain.**

---

## 2. What the index contains, in our vocabulary

From `evidence/x1/summary.json`, `probe2.json`, `probe3.json`.

### Information containers

| Container kind | Count | SCIP symbol form |
|---|---|---|
| Named parameters | **11,436** | `` `src.analysis.sector_analysis`/SectorAnalysis#__init__().(db_path) `` |
| Class fields / attributes | **4,131** | `` `src.calibration.baseline`/TaskCalibration#task. `` |
| Module-level state | **1,200** | `` `src.calibration.harness`/DEFAULT_BUNDLE_ROOT. `` |
| Local variables | **20,115** defs / 27,596 distinct | `local 42` |
| **Total named containers** | **16,767** | (excluding locals) |

**Granularity is excellent — locals included — but locals are anonymous.**
A local is emitted as `local 42`, scoped per-document, with only its inferred
type in the documentation field. **The variable's name is not in the index.**
`Document.text` is not emitted either (0 of 443 documents carry it), so names
must be recovered by re-reading the source at the occurrence range. This works
perfectly — verified on 12 samples in `probe3.json`:

```
local 1  -> "df"            from  df = self.db.get_lap_times(session_id=..., driver_id=...)
local 10 -> "driver_sectors" from  driver_sectors = all_sectors.loc[all_sectors['driver_id'] == drv]
```

So local-granularity containers are available, but only if you keep the source
alongside the index. The index alone is not self-sufficient at that level.

### Information transformers

**3,686 functions/methods** and **600 classes**, each with:

- an exact **body span** (`Occurrence.enclosing_range` is emitted for every one
  of the 3,682 method definitions — 4,282 definition occurrences carry it, and
  they are exactly the methods + classes). This is what makes containment
  queries exact rather than heuristic.
- a rendered signature with resolved types, in `documentation[0]`:
  ```
  ```python
  def get_sector_times(
    self,
    session_id: int,
    driver_id: Optional[str] = None,
    valid_only: bool = True
  ) -> pd.DataFrame:
  ```
  ```

### Read/write edges — **the significant structural miss**

| Symbol role | Occurrences |
|---|---|
| ReadAccess | **180,071** |
| Definition | **40,844** |
| **WriteAccess** | **0** |
| Import | **0** |

Total 220,915 — the two non-zero roles account for every occurrence exactly.

**scip-python never sets WriteAccess.** Every non-definition reference is tagged
ReadAccess, including mutations. `x = compute()` at a re-assignment, `obj.field =
v`, `lst.append(...)` — all indistinguishable from a read. The read/write
distinction our vocabulary assumes is **not available from this indexer**. You
get it back only by re-parsing the source at the occurrence range (Python's `ast`
gives `Store` vs `Load` contexts directly), which means SCIP is not the right
tool for the read/write layer — a plain AST pass is.

`Import` is also never set, so import edges must be inferred from the module
prefix of referenced symbols (which works — see §3).

### Call relationships — recoverable, with exact attribution

Yes. Because body spans are exact, every call site attributes to its enclosing
function by innermost-span containment:

- **18,761** method-reference occurrences (6,972 internal, 11,789 external)
- **2,458** sit outside any function (module-level code) — correctly unattributed
- **10,820 distinct caller→callee pairs** recovered
- **9,876 distinct function→container read pairs** (a function reading a named
  field or module-level variable)
- **1,209 distinct internal module→module dependency pairs**

Callee symbols carry their origin, so internal calls separate cleanly from
stdlib/third-party (`scip-python python python-stdlib 3.11 builtins/dict#get().`).

### What SCIP does *not* give at the symbol level

- `SymbolInformation.kind` is **never set** (null on every sample) — entity
  classification must be parsed from the symbol-string grammar, not read from a
  field. Workable, but it means the descriptor grammar is the real API.
- `display_name`, `enclosing_symbol`, `signature_documentation`: **all zero**.
- **Only 105 `Relationship` records** across the whole codebase. Inheritance and
  interface-implementation edges are effectively **absent** despite 600 classes.

---

## 3. Side-by-side vs the existing map

The map is 7,793 lines / 36 files: `index.md` 1,042 · `packets/` 4,686 (16 files)
· `decisions/` 1,405 (15 files) · `overlays/` 478 · `reference/` 121 ·
`MAP_BUILD.md` 61. By shape: **1,282 lines inside fenced/YAML blocks, 6,511 lines
of prose.**

### (a) Procedurally reproducible — ~552 lines, ~7%

**The node catalog's structural fields.** `index.md` declares 48 YAML nodes (16
containers, 29 components, plus system-context and external systems). Of the six
fields per node, five are derivable from the index — `id`, `level`, `parent`,
`path`, `status` (240 lines) — plus the same five fields on the 26 packet front
blocks (130 lines). `purpose` and `confidence` are not.

**The dependency graph — and this is the strongest result in the excursion.**
`index.md` curates 39 `depends-on` edges. I rebuilt the container graph from
nothing but SCIP occurrences (`probe4_edges.py`: attribute each referencing file
to a container, each referenced internal symbol's module to a container, roll
up):

| | |
|---|---|
| Map edges between two `src/` containers | 34 |
| **Confirmed by SCIP** | **34 (100%)** |
| **Map edges SCIP could not see** | **0** |
| SCIP-derived container edges total | 39 |
| **Real edges SCIP found that the map omits** | **5** |

The five the map is missing: `analysis→data`, `compound_prior→utils`,
`physics→common`, `reporting→fantasy_scoring`, `utils→models`. These are
candidate map-drift findings, produced for free.

The remaining 5 map edges touch external nodes (`struct:sqlite_db`,
`struct:fastf1_api`). SCIP *does* see the `fastf1` and `sqlite3` external symbols
(453 external symbols indexed), so the edges are visible — but the decision that
"FastF1 is an architectural node worth naming" is human. That is a promotion
judgment, not an extraction gap.

The `evidence:` file lists on each edge (39 lines) are also derivable — SCIP
knows exactly which files carry each dependency, more precisely than the curated
lists do.

### (b) Partially supportable — ~3,897 lines, ~50%

This is the packets, and it is the interesting bucket. A packet is a skeleton of
named entities with behavioral prose hung off each one. Measured section sizes
across `packets/*.md`:

| Section type | Lines |
|---|---|
| `## Component: <name> — <description>` (10 sections) | 2,382 |
| `## Key Modules` (15 files) | 901 |
| `## Key Components` | 156 |
| `## Dependencies` / `External Dependencies` | 71 |
| `## Module Registry`, `Module Families`, `Scripts` | 55 |
| `## Data Flow` | 24 |

SCIP can generate **every heading, every bold module/class/function name, the
signature under it, and the dependency lists** — the skeleton is exact and
complete. What it cannot generate is the sentence. From `packets/data.md`:

> `collect_season(year)` → `collect_race(year, gp_name)` → `collect_session(year, gp_name, session_type)`. Handles retry logic with exponential backoff, rate limiting (INTER_SESSION_DELAY=55s), and rate-limit detection on "500 calls/h" errors (RATE_LIMIT_WAIT=1200s). **FP position derivation uses best-lap ordering because FastF1 FP results have Position=NaN.**

The call chain in the first clause is derivable. The constant names are
derivable. The *reason* — FastF1 returns NaN, so we order by best lap — is not in
any structure. That last sentence is the packet's actual value.

The `## Data Flow` blocks are a near-miss: they are the module dependency chain
SCIP already has, but as a *chosen path* through it (which of 1,209 module pairs
constitute "the" flow) — selection, not extraction.

### (c) Untouchable by extraction — ~3,344 lines, ~43%

- **`decisions/` — 1,405 lines, 15 files, 100% untouchable.** Titles alone make
  the point: `pooled-sigma-shared-systematic-floor`,
  `smoother-rounds-braking-knee`, `two-cycle-external-anchor-design`. These
  record why one of several viable designs was chosen. Nothing in the code says
  what was rejected.
- **`overlays/` — 478 lines, ~90% untouchable.** 18 purpose/capability nodes and
  their constraints. `purpose:weekend_state_decomposition` — "Four-layer
  decomposition of the fitted quali physics store into a per-car-weekend signal"
  — is a capability claim over a set of modules; no amount of symbol data yields
  it. Constraint `rationale:` blocks are pure judgment. Only the `evidence:` file
  lists (46 lines) are checkable against the index.
- **`index.md`'s `purpose:` field on all 48 nodes and `confidence:` on 87 lines.**
- **`## Responsibility` (218), `## Known Limits` (230), `## Decision anchors`
  (90), `## Trust limitations` (27), `## Open Questions` (19)** in packets.
- **`## Open Structural Questions`** — ~33 lines of the densest judgment in the
  map, each row a *disposition*: `WIRED` / `KEPT-WITH-REASON` /
  `removal-PROPOSED`. Note that SCIP can compute the *input* to these calls
  ("`driver_utility_observable` has zero production importers" is exactly a
  reference count) but not the verdict — "validated substrate awaiting its Build-2
  consumer; do not remove" is a decision that reverses the obvious reading of the
  reference count.
- **`reference/physics-unit-conventions.md` (121)** and **`MAP_BUILD.md` (61)**.

### The shape of the answer

Extraction owns the **skeleton** completely and owns **nothing else**. On the
node catalog and the dependency graph, SCIP is not merely adequate — it beat the
hand-curated map by 5 edges with zero false negatives. But that spine is 7% of
the text, and the map's value is concentrated in the 43% that has no structural
anchor at all. The interesting engineering question this raises is not "can we
extract the structure" (yes, decisively) but **"can the 50% middle bucket be
generated as a skeleton and then filled?"** — which is what §4 measures.

---

## 4. Comment/docstring coverage on f1Brainz — the concept-layer seed density

**Method.** `evidence/x1/docstring_census.py` parses each file with Python's
`ast` and counts, per module/class/function: a non-empty `ast.get_docstring()`,
and separately whether the physical line above the `def`/`class` (skipping
decorators and blanks) starts with `#`. Run twice — once over all 677 source
files, once restricted to exactly the 443 files SCIP indexed
(`indexed_files.txt`, derived from the index itself) for an apples-to-apples
comparison.

**Cross-validation.** The AST census and the SCIP index agree *exactly* on the
443 indexed files: both count **3,686 functions**, and both count **2,113** with
a docstring. Two fully independent methods, identical numbers. The class counts
differ trivially (600 AST vs 589 SCIP definitions; 426 vs 419 documented) from
conditionally-defined classes.

**Coverage on the 443 indexed files:**

| Entity | Count | Docstring | Doc or leading comment |
|---|---|---|---|
| Modules | 443 | **93.7%** (415) | — |
| Classes | 600 | **71.0%** (426) | 72.2% (433) |
| Functions — all | 3,686 | **57.3%** (2,113) | 59.0% (2,174) |
| Functions — public | 1,536 | **72.3%** (1,110) | — |
| Functions — private (`_`-prefixed) | 2,150 | **46.7%** (1,003) | — |
| Module-level assignments | 1,447 | n/a | **23.7%** (343) |
| Class fields | 3,959 | n/a | **4.1%** (164) |

**Reading it.** Seed density is good for transformers and poor for containers.
Roughly **7 in 10 classes and 7 in 10 public functions** arrive with prose
attached — enough to seed a concept layer over the skeleton for most of the
surface that a packet's "Key Modules" section actually describes. Adding leading
comments buys almost nothing (+1.7pp on functions), so **docstrings are the
channel**; comment-scraping is not worth building.

The floor is containers. **Class fields are 4.1% commented** and module-level
state 23.7% — so the 16,767 named containers, the largest population in the
index, arrive almost entirely unannotated. Any concept layer over containers
will be inferring, not harvesting.

One free bonus: scip-python parses Google-style `Args:` blocks and attaches
per-parameter prose to the parameter symbol itself — **646 of 11,436 parameters
(5.6%)** carry their own documentation string, e.g.
`SectorAnalysis#__init__().(db_path)` → "db_path: Path to the SQLite database
file". Small, but it is parameter-level concept data for free.

---

## 5. Scoped nulls — what was NOT tested

This test covers **scip-python 0.6.6 against one Python codebase on one Windows
machine, once**. It kills nothing outside that.

- **Not tested: any other language.** `scip-clang`, `scip-typescript`,
  `scip-java`, `scip-go` were not installed or run. The C++ case
  (`superCoolSpaceSim_cpp`, in scope for this repo) is completely unmeasured, and
  scip-clang requires a compilation database — a materially harder setup than
  `npm install`.
- **Not tested: incrementality.** Every run was a full 6-minute index. Whether
  scip-python supports or approximates incremental re-indexing on a single-file
  change is unknown, and this is the load-bearing question for a live map. A
  6-minute full rebuild per edit is not viable.
- **Not tested: rename/move identity.** Whether a symbol keeps a stable identity
  across a rename or a file move — the thing a durable statement store needs to
  avoid re-minting every fact — was not exercised. Only one revision of the
  codebase was indexed.
- **Not tested: any second codebase.** The 7/50/43 split is *this* map's shape.
  f1Brainz's map is unusually prose-heavy and decision-heavy (a research
  codebase); a CRUD service's map would likely skew far more toward bucket (a),
  and the proportions would move a lot.
- **Not tested: the WriteAccess gap against an AST baseline.** I established
  scip-python emits zero writes; I did *not* build the `ast`-based read/write
  pass to confirm it recovers them cheaply. That is asserted from the Python
  `ast` API (`Store`/`Load` contexts), not measured.
- **Not tested: whether generated skeletons are actually useful.** Bucket (b) is
  an estimate of what SCIP *could* scaffold, computed from section line counts —
  no packet skeleton was generated and put in front of a reader. That is the
  obvious next excursion.
- **Not tested: the patched build's fidelity.** The Windows regex patch makes the
  tool run; I did not verify that module-name computation is byte-identical to a
  Linux run. The 34/34 edge agreement is strong indirect evidence it is correct,
  but it is indirect.
- **Not tested: cross-file `local N` collision handling** at scale, and **not
  tested: performance of the Python decoder** on indexes much larger than 22 MB.

**Default next move:** the two variants worth running are (1) incremental
re-index cost, since it gates everything, and (2) scip-clang on the C++ repo,
since a Python-only result does not generalize.

---

## Artifacts

All under `C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x1\`:

| File | What |
|---|---|
| `index.scip` | The 22 MB SCIP index (443 documents) |
| `decode_scip.py` | Pure-Python SCIP protobuf decoder — no protoc, no Go |
| `probe2.py`, `probe3.py` | Call-edge reconstruction, enclosing ranges, local-name recovery |
| `probe4_edges.py` | Map-vs-SCIP container dependency comparison |
| `docstring_census.py`, `docstring_census_indexed.py` | AST docstring/comment census |
| `summary.json`, `probe2.json`, `probe3.json`, `edge_compare.json`, `docstring_census*.json` | All measurements quoted above |
| `defs.jsonl` (16,767 defs), `edges.jsonl` (180,071 occurrences), `call_edges.jsonl` (10,820 pairs), `module_deps.jsonl` (1,209 pairs) | Extracted graph data |
| `indexed_files.txt` | The exact 443-file set, for reproducing the census |

f1Brainz was not modified.
