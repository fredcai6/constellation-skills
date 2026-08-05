# x6 result — MATLAB structural extraction: no scip-matlab, but mtree wins outright

**Type:** prototype / measurement · **Verdict:** POSITIVE — the cheapest route of the three arms
**Date:** 2026-08-05 · **Evidence:** `.agent-work/explore-code-map/evidence/x6/`

## Headline

**There is no scip-matlab and never has been** — MATLAB is absent from SCIP's own
indexer list. But the fallback is better than the thing we went looking for:
**MATLAB ships its own full parse tree, `mtree`, and it indexed all 539 files in
21.4 seconds with zero parse failures.**

From `matlab_src` (539 `.m` files, 65,287 lines) it emits, in our vocabulary:

| | Count |
|---|---|
| **Transformers** (named) | **3,493** |
| **Containers** (named, non-local) | **7,085** |
| Local variable scopes (function × name) | 16,070 |
| **Caller→callee pairs** | **16,269** |
| Directory-level dependency edges | 73 |

Two results matter more than the totals:

- **mtree gives us the write side that scip-python does not.** x1 found
  scip-python emits `WriteAccess: 0` — every mutation indistinguishable from a
  read. mtree carries assignment structure directly: **17,488 write occurrences**
  against 90,400 identifier occurrences, plus `asgvars`/`sets`/`lhs`/`depends`
  methods built in. The read/write layer x1 had to punt to a separate AST pass is
  native here.
- **The MATLAB-specific wall is name resolution, not parsing.** Of 9,855
  qualified call sites (`obj.method(...)`, `pkg.fn(...)`, `Class.static(...)`),
  **5,527 — 56% — resolve to no target**, because the base is a local variable
  whose class is unknown without type inference. Parsing is free; *dispatch* is
  the hole.

---

## 1. Does a SCIP emitter for MATLAB exist — no

Checked, in order:

| Source | Result |
|---|---|
| `sourcegraph/scip` README (fetched raw from `main`) | Lists **10 indexers**: scip-java, scip-typescript, rust-analyzer, scip-clang, scip-ruby, scip-python, scip-dotnet, scip-dart, scip-php, debian-lsp. **MATLAB appears nowhere in the file.** |
| Sourcegraph docs / announcing-scip blog / scip-code.org | Same list; no MATLAB. |
| Community indexers | `tjdevries/scip-ocaml` exists — so third-party SCIP indexers *do* get written — but no MATLAB equivalent surfaced. |

**One trap worth flagging for whoever searches next.** Searching "scip matlab"
returns `scipopt/MatlabSCIPInterface` at the top. That is a **name collision**:
that SCIP is the *SCIP Optimization Suite* (a mixed-integer programming solver),
entirely unrelated to the SCIP Code Intelligence Protocol. It is a MATLAB binding
to a solver, not an indexer. Do not mistake it for a hit.

So the SCIP route for MATLAB is not "blocked" as in x5 — it simply **does not
exist to attempt**. That makes the local-tooling question the whole question.

---

## 2. Which routes were tried, and what each cost

MATLAB R2025b (`25.2.0.3150157`, Update 4), headless via `matlab -batch`.
**Licence checked out on the first try and every try** — no hang, no fallback to
tree-sitter needed. Startup overhead is ~5-8s per invocation; that dominates the
small runs.

| Route | Command | Result |
|---|---|---|
| Smoke test | `matlab -batch "disp(version)"` | **30.5s** first launch (cold), ~5-8s after. Home Licence banner on stdout. |
| **`mtree` — full parse, all 539 files** | `mtree(f,'-file')` per file | **1.54s for all 539**, **0 failures**. This is the whole corpus parsed in under two seconds. |
| **`mtree` — full extraction** | `extract2.m` | **21.4s**, 0 failures, ~26s wall including MATLAB startup |
| `checkcode` — whole corpus | `checkcode(files,'-struct','-id')` | **4.0s**, 539 files, **526 messages** |
| `matlab.codetools.requiredFilesAndProducts` | 6-file sample | **works, but slow: 34.3s for 6 files** → extrapolated **~51 minutes** for 539 |
| tree-sitter-matlab fallback | not needed | **NOT RUN** — MATLAB never failed, so the fallback was never triggered (see nulls) |

**`requiredFilesAndProducts` is real but is the wrong tool for a live map.** It
resolves the *transitive* closure through the actual path, which is genuinely
more than syntax gives you: the entry point `superCoolSpaceSim.m` reports **247
required files, all inside `matlab_src`, 1 product** in 21.5s. That is a true
reachability answer and it cleanly separates the ~247-file live application
surface from the rest of the 539. But per-file cost scales with closure size
(0.4s for a leaf, 21.5s for the root), it returns a flattened closure rather than
direct edges, and ~51 minutes for a full pass rules it out as anything but an
occasional cross-check. It also requires the sources on the MATLAB path
(`addpath(genpath(src))` in-session; the original path was captured and restored
via `onCleanup`, and `savepath` was never called).

**`checkcode` is a cheap bonus channel.** 4 seconds for the corpus, and its
message ids are directly useful to a mapper rather than merely stylistic — the
top ids are `NBRAK2` (117), `MSNU` (99), `ASGLU` (75), `NASGU` (57), `INUSD`
(43). `ASGLU`/`NASGU`/`INUSD` are *unused value* and *unused argument* findings —
i.e. dead containers — and `DEFNU` (6) is "function defined but never used", a
dead-transformer signal. That is drift evidence for free at 4 seconds a run.

**One route caveat: `mtree` is officially undocumented.** MathWorks ships it in
`toolbox/matlab/codetools/@mtree/` and does not document it publicly. This
excursion found direct evidence that it lags its own language: **MATLAB's own
`tree2str` throws `unknown expr node PROPTYPEDECL`** when asked to render a typed
property declaration — a language feature since R2016b. The parser handles it;
the shipped pretty-printer does not. Anything built on mtree must expect
undocumented, occasionally stale internals and pin behaviour with its own tests.

---

## 3. What the best route emits, in our vocabulary

All figures from `evidence/x6/summary3.json`, produced by `extract2.m`.

### Information transformers — 3,493 named

| Kind | Count |
|---|---|
| Methods (in `methods` blocks) | **2,606** |
| Subfunctions | 614 |
| Main functions (one per function file) | 256 |
| Nested functions | 7 |
| Property accessors (`get.X` / `set.X`) | 4 |
| Scripts (whole-file transformer) | 6 |
| **Total named** | **3,493** |
| Anonymous functions (unnamed, counted separately) | 867 |

Each carries an exact **character span** (`lefttreepos`/`righttreepos`), a line
number, its name, and its input/output arity — so call sites attribute to their
enclosing transformer by innermost-span containment, exactly the technique x1
used with SCIP's `enclosing_range`.

### Information containers

| Container kind | Count |
|---|---|
| Input parameters | **5,100** |
| Output parameters | **1,569** |
| Class properties | **414** (224 with defaults, 190 typed declarations) |
| `persistent` | 2 |
| `global` | **0** |
| **Total named, non-local** | **7,085** |
| Function-local scopes (distinct function × name) | **16,070** |
| Loop induction variables | 504 |
| Anonymous-function parameters | 120 |

**Locals come with their names attached** — a strict improvement over x1, where
scip-python emitted anonymous `local 42` and the name had to be recovered by
re-reading source at the occurrence range. Here `stringval` on the ID node gives
the name directly from the tree.

### Edges and occurrences

| | Count |
|---|---|
| Bare call sites (`f(x)`) | **22,278** |
| Qualified call sites (`a.b(x)`) | **9,855** |
| **Distinct caller→callee pairs** | **16,269** |
| Directory-level dependency edges | **73** (57 excluding `unit_tests`) |
| Internal call occurrences | 5,592 (648 distinct targets) |
| External/builtin call occurrences | 20,938 (733 distinct targets) |
| Identifier occurrences | 90,400 |
| **Write occurrences** | **17,488** |
| Read occurrences (derived: identifiers − writes) | 72,912 |

Internal/external separates cleanly by resolving the callee root against the
corpus's own class names, file stems and package directories. The external head
is unmistakably the MATLAB standard library — `struct` (3,230), `error` (1,266),
`zeros` (872), `isfield` (861), `numel` (691) — which is the same clean split x1
got from SCIP symbol origins, obtained here without an indexer.

The directory edges are the closest analogue to x1's container dependency graph;
the top non-test edges are `core\+intproc → core\integrator` (36),
`software → core` (24), `core\+intproc → core` (20),
`software\targeting\+orbitproc → core` (13), `io → core` (12).

**Caveat on the write count.** 17,488 counts assignment *statements* (plus loop
induction variables), resolved to base identifiers through `DOT`/`SUBSCR` chains.
It does not include mutation through a function call (MATLAB's copy-on-write
value semantics make `obj = obj.step(dt)` an ordinary assignment, which helps,
but handle-class mutation inside a callee is invisible). The read count is
*derived by subtraction*, not measured directly — treat it as an order of
magnitude, not a fact.

### Sample-verification — and the two bugs it caught

The brief asked for hand verification, and it earned its keep: **it caught two
real extractor bugs that a totals-only check would have passed.**

Corpus-wide grep ground truth matched the totals exactly from the first run —
277 `classdef`, 3,487 `function` lines (+6 scripts = 3,493), 539 `methods`
blocks, 85 `properties` blocks, 2 `persistent`, 0 `global`. But the totals being
right hid two classification errors:

1. **Sibling functions chain through `Parent`.** Walking `Parent` up to find an
   enclosing `methods` block classified only the *first* function in each block
   as a method — `method` came out as exactly 539, suspiciously equal to
   `methods_blocks` = 539, with the other 2,607 misfiled as "nested functions."
   A dump of `Integrator.m` (50 functions, 5 methods blocks) showed
   `fn#1 parentKind=METHODS` but `fn#2..fn#8 parentKind=FUNCTION`: **mtree's
   `Parent` on a list element returns the previous sibling, not the container.**
   Fixed by classifying on span containment instead. Corrected: 2,606 methods,
   7 genuinely nested functions.
2. **Typed properties were invisible.** `SolarArray.m`'s second properties block
   declares 18 properties; the extractor found **zero**. `joint_id double = 0`
   parses as `EQUALS(Left=PROPTYPEDECL, Right=INT)`, and **no accessor on
   `PROPTYPEDECL` returns the identifier** — `Left` is null. (This is the same
   node that crashes `tree2str`.) Fixed by resolving the leftmost identifier at
   the node's character position.

Final verification of the fix: **414 properties extracted vs 414 by a careful
independent grep**, across 78 files. On `SolarArray.m`, the extractor emits
exactly the 18 names I read out of the source by hand, in source order —
`ANGLE_ERROR_DEADBAND_RAD`, then `joint_id, body_id, mass, inertia,
hingePosBody, panelDimensions, jointType, kp, kd, max_torque, friction_coef,
body_rate_limit, commanded_angle, is_2dof, actual_angle, actual_rate,
applied_torque`. Full listing in `evidence/x6/properties_extracted.tsv`.

Files read directly to check against: `unit_tests/TestRecordingIntegrator.m`
(1 classdef, 1 methods block, 1 method — extractor agrees),
`core/+contractspec/software.m` (FunctionFile, 1 main function, 0 in / 1 out —
agrees), `subsystems/SolarArray.m` (29 functions = 27 methods + 2 subfunctions,
3 methods blocks, 2 properties blocks — agrees).

---

## 4. MATLAB-specific mapper hazards actually observed

Ordered by how much they cost.

1. **Dynamic dispatch is the real hole — 56% of qualified calls.** MATLAB's
   `a.b(c)` is syntactically ambiguous between method call, field access,
   package function, and array index. mtree resolves what it can and leaves the
   rest:

   | Qualified call site resolution | Count | Share |
   |---|---|---|
   | Base is a known class → static method / constant | 2,378 | 24.1% |
   | Base is a known package → package function | 1,874 | 19.0% |
   | **Base is a local variable → target UNRESOLVED** | **5,527** | **56.1%** |
   | Base unknown | 76 | 0.8% |

   Every `obj.step(dt)` needs the runtime class of `obj` to name a target. **Type
   inference, not parsing, is what a MATLAB call graph is missing** — and it is
   the majority of the object-oriented call surface in a codebase that is 51%
   classdef files.

2. **`CALL` is not where the calls are.** mtree emits `CALL` only when the target
   is a bare identifier it believes is a function; `obj.m(...)`, `pkg.f(...)` and
   `Class.s(...)` all parse as **`SUBSCR` over `DOT`**. Verified on
   `AttitudeController.m`: of 226 `CALL` nodes, **zero** have a non-`ID` `Left`.
   An extractor that reads only `CALL` silently loses 9,855 of 32,133 call sites
   (31%) — and loses them *quietly*, which is x1's empty-index lesson again.

3. **`SUBSCR` conflates indexing with dispatch.** 11,218 `SUBSCR` nodes cover
   both `a(i)` array indexing and calls. mtree disambiguates using local variable
   knowledge, which is why the resolution table above has a large unresolved
   bucket rather than a wrong-answer bucket. It fails safe, but it fails.

4. **Scripts vs functions is a non-issue here, and `FileType` settles it.**
   `mtree(...).FileType` reliably returns `ScriptFile` / `FunctionFile` /
   `ClassDefinitionFile`. The split is **6 / 256 / 277** — only 6 scripts in 539
   files, so the "a script has no signature and leaks variables into a shared
   workspace" hazard is nearly absent from this corpus. Do not generalize: this
   is a property of superCoolSpaceSim, not of MATLAB.

5. **classdef dominates — 277 of 539 files (51%).** 2,606 of 3,493 transformers
   (75%) are methods. Any MATLAB mapper that treats "file = module = function
   file" (the Python-shaped assumption) gets three quarters of this codebase
   wrong. Note also **539 methods blocks across 277 classes** — a class routinely
   has several, split by `Access`/`Static` attributes, so the class→method
   relation is not one block deep.

6. **Path-dependent name resolution.** MATLAB resolves a function file by its
   **filename**, not by the function name inside it, and 16 package directories
   (`+cfgio`, `+contractspec`, `+intproc`, `+mbdproc\+backends`, …) mean the same
   short name can mean different things depending on the calling context. There
   are 2,958 distinct defined names against 3,493 transformers, so **~535 names
   are reused across classes** — resolving a callee by bare name alone will
   mis-attribute. No `@class` directories were present, which removes one variant
   of the same hazard.

7. **`eval`-family dynamism is essentially absent — measured, not assumed.**
   Corpus-wide: `eval(` **0**, `evalin(` **0**, `assignin(` **0**, `feval(`
   **0**, `str2func(` **1**. This codebase is far cleaner than MATLAB's
   reputation implies, so the *textual* dynamism hazard is a non-issue here even
   though the *dispatch* hazard (item 1) is severe. Again — a property of this
   corpus, not the language.

8. **Parse artifacts to filter.** `end` shows up as a "callee" 209 times (it is
   `end` in an indexing context), and `true`/`pi` appear as calls because they
   are builtin functions, not literals. Any callee list needs a builtin filter or
   it will report nonsense edges.

---

## 5. Adoption-cost verdict, beside x1 and x5

| | x1 — Python / scip-python | x5 — C++ / scip-clang | **x6 — MATLAB / mtree** |
|---|---|---|---|
| Indexer exists? | yes | yes | **no scip-matlab, ever** |
| Install | `npm install`, 30s | **impossible on Windows** | **nothing to install** — ships with MATLAB |
| Blocker | Windows regex bug, 1-line patch | upstream closed Windows `not_planned` | none hit |
| Prerequisite artifact | none | `compile_commands.json` (62s) | none |
| **Time to full structural index** | **~15 min** | **never reached** | **~26 seconds** |
| Re-index cost (full corpus) | 6m05s | n/a | **21.4s** |
| Parse failures | 0 | 0 TU errors | **0 / 539** |
| Write/read distinction | **absent** (0 WriteAccess) | untested | **native** (17,488 writes) |
| Local variable names | **not in index** | in frontend, emission untested | **in the tree** |
| Biggest gap | 43% of map has no structural anchor | no Windows binary | **56% of qualified calls unresolved** |

**MATLAB is the cheapest of the three arms by a wide margin, and it inverts the
expected ranking.** The language with no SCIP indexer is the one where full
structural extraction is a 26-second local command with no install step, no build
artifact, and no network. Where x5's blocker was availability and x1's was a
patch, x6 had no setup blocker at all — the cost moved entirely into *semantics*,
where 56% of the object-oriented call graph needs type inference that no amount
of parsing supplies.

**The consequence for a code-map design.** x5 already suggested that a single
AST-based extractor might beat a per-language SCIP indexer fleet for the
structural spine. x6 is a second, independent data point for that: mtree
delivered more than scip-python did on the two axes x1 flagged as gaps
(write/read roles, local names), at 1/17th the runtime, with no indexer in
existence. For MATLAB specifically the design question is not "how do we index
it" — that is solved and fast — but **"where does the class of a variable come
from"**, since that single missing fact is what stands between 16,269 call pairs
and a complete call graph.

**Incrementality looks solved here too, though untested.** 1.54s to parse all 539
files means per-file re-parse is ~3ms, so a live map could re-extract a changed
file essentially instantly rather than rebuilding. x1 named a 6-minute full
re-index as the thing that gates a live map; that gate is simply not present on
this route. I did not build the incremental path — see nulls.

---

## 6. Scoped nulls — what was and was NOT tested

**What this establishes:** mtree-based extraction on **one MATLAB codebase**
(539 files, 65,287 lines), on **MATLAB R2025b Update 4**, on **one Windows 11
machine**, on 2026-08-05. Nothing broader.

- **tree-sitter-matlab was NOT run.** It was the designated fallback and MATLAB
  never failed, so it was never triggered. Its parse fidelity, speed, and
  crucially its behaviour **without a MATLAB licence** are all unmeasured. This
  matters: every number here is gated on having MATLAB installed and licensed,
  which is a materially stronger precondition than `npm install`. **A CI runner
  without a MATLAB licence cannot reproduce any of this**, and whether
  tree-sitter closes that gap is exactly the open question.
- **The licence was a Home Licence.** It checked out instantly every time. Behaviour
  under a network/floating licence — the realistic CI case — is untested, and
  licence contention is the most likely way this route breaks for someone else.
- **`requiredFilesAndProducts` was sampled, not run to completion.** 6 of 539
  files. The ~51-minute figure is a linear extrapolation from a sample whose
  per-file cost ranged 0.4s–21.5s; closure cost is nonlinear in practice, so that
  number could be badly wrong in either direction. The full dependency closure
  for the corpus was never computed.
- **Incrementality is inferred, not built.** The 3ms/file parse figure is real;
  an actual incremental pipeline (change detection, partial re-extraction, edge
  invalidation) was not written or timed.
- **Rename/move symbol stability was not exercised** — one revision of the corpus
  was analysed, exactly as x1 and x5 left this question.
- **The 56% unresolved-dispatch figure is a *ceiling on syntax*, not a verdict on
  what is achievable.** No type inference was attempted. MATLAB's own Code
  Analyzer, `matlab.lang` reflection, or property type declarations
  (`jointType mbd.JointType = ...` — the typed properties are *right there* in
  the tree and 190 of them carry a type) could recover a large share of the
  5,527. Declared property types were extracted as names only; **their type
  annotations were not harvested**, and that is the obvious next move.
- **The read count is derived, not measured.** 72,912 = identifiers − writes. A
  direct read/write classification per occurrence was not performed. The write
  count itself excludes handle-class mutation inside callees.
- **Call attribution to enclosing transformer was not spot-checked** the way
  properties and function classification were. Span containment is the same
  technique x1 validated, but it is unverified *here*.
- **No comment/docstring census was run.** x1's §4 equivalent — how much prose
  seeds a concept layer — is entirely unmeasured for MATLAB, and MATLAB's
  H1-line/help-block convention is a different shape from Python docstrings.
  This is a clean gap next to x1.
- **No map comparison.** Unlike x1, there is no existing hand-written
  architecture map for `matlab_src` to diff against, so the (a)/(b)/(c)
  reproducibility split x1 produced has **no counterpart here**. The counts stand
  alone; what fraction of a human map they would reproduce is unknown.
- **The two extractor bugs found are evidence the corpus should not be trusted
  from a single pass.** Both produced plausible totals with wrong internals, and
  both were caught only by reading source by hand. There may be more of the same
  class in the call-edge data, which received less hand-checking than properties.
- **`superCoolSpaceSim` was not modified.** All output is under `evidence/x6/`.
  The MATLAB path was mutated in-session only (`addpath(genpath(...))`, restored
  via `onCleanup`); `savepath` was never called and no MATLAB setting was
  persisted. The simulation was never run.

**Default next move:** harvest the declared property/argument types already in
the tree (190 typed properties, plus `arguments` blocks) and measure how far that
alone drives the 5,527 unresolved qualified calls down. That is the single number
standing between this route and a complete MATLAB call graph, and the data for it
is already parsed.

---

## Artifacts

All under `.agent-work/explore-code-map/evidence/x6/`:

| File | What |
|---|---|
| `extract2.m` | **The final extractor** (span-based classification, qualified-call resolution, PROPTYPEDECL fix). Emits the `*3` outputs. |
| `summary3.json` | **All counts quoted above** — the headline artifact |
| `extract.m`, `summary.json`, `summary2.json` | The two superseded runs, kept so the two bugs and their corrections are inspectable |
| `probe1.m` / `probe1_log.txt` | mtree API surface, FileType census, node-kind distribution |
| `probe2.m` / `probe2_log.txt` | `dumptree` structure, `requiredFilesAndProducts` timings, `checkcode` run |
| `probe3.m` / `probe3_log.txt`, `probe3_err.txt` | PROPTYPEDECL structure; `probe3_err.txt` holds the verbatim `tree2str` crash |
| `verify.m` / `verify_log.txt` | Per-function classification for the 3 hand-checked files |
| `check_props.m`, `properties_extracted.tsv` | All 414 properties with file and block line — the 414-vs-414 verification |
| `call_edges3.tsv` | **16,269 caller→callee pairs** with file, enclosing function, and call kind |
| `dir_edges3.txt` | 73 directory-level dependency edges with weights |
| `top_callees3.txt` | Top 70 callees tagged INTERNAL/EXTERNAL |
| `per_file3.json` | Per-file function/method/local counts |
