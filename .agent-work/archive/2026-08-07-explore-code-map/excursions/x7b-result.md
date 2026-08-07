# x7b result — AST-first single extractor, measured against SCIP

**Type:** prototype (design-it-twice candidate B) · **Verdict:** POSITIVE, with the
hole in a different place than expected
**Date:** 2026-08-05 · **Evidence:** `.agent-work/explore-code-map/evidence/x7b/`

## Headline

A 732-line stdlib-only Python `ast` extractor emits the same statement lines for
the `src/utils` slice in **2.3 seconds**, with **zero external dependencies** and
**zero parse failures** across 67 files.

Against x1's SCIP index as ground truth, joined on exact source position, on the
**12,020 references SCIP resolved to a project-internal symbol**:

| Outcome | Count | Share |
|---|---|---|
| **Resolved correctly** (symbol string identical) | **10,872** | **90.4%** |
| Resolved *wrongly* | 229 | 1.9% |
| Unresolved (marker emitted, never dropped) | 661 | 5.5% |
| Called it an anonymous local | 219 | 1.8% |
| Called it external | 39 | 0.3% |

**Every one of the 229 "wrong" answers is a SCIP defect, not mine** — see §4. The
count of cases where the AST resolver produced a *different, incorrect*
project-internal symbol than SCIP is **zero**. On the `src/utils` core files
alone the correct rate is **95.6%** (715 of 748).

The one number that matters most, and it is not the accuracy number: **62.8% of
qualified call sites (`x.method(...)`) resolve to no target** — 2,017 of 3,214.
That is MATLAB's 56% hole (x6) reappearing in Python, at a *worse* rate, under a
tool with a far better parser. **The dispatch hole is not a MATLAB problem. It is
a property of parse-without-inference, and it is language-independent.**

But the hole is not where it looks. Decomposing those 2,017 unresolved qualified
calls by what SCIP knew:

| What SCIP resolved it to | Count | Meaning |
|---|---|---|
| **External** (pandas, numpy, pathlib, logging…) | **1,187** | third-party method dispatch — lost |
| SCIP was also blind (`local N` or nothing) | 784 | nobody resolves these |
| **Internal project symbol** | **46** | **the actual loss to a code map** |

**46 of 3,214 qualified calls — 1.4% — are internal edges the AST extractor
loses.** The 62.8% headline is almost entirely the library surface. For the
internal call graph, which is what a code map is made of, pure AST is close to
complete.

---

## 1. What was built

`evidence/x7b/astx.py` — 732 lines (~640 of code), single file, imports only `ast`, `builtins`,
`hashlib`, `json`, `os`, `sys`. No SCIP, no pyright, no `npm install`, no type
inference engine.

**Two passes.**

1. **Module table pass.** Parse all 440 `src/**.py` modules and record, per
   module: module-level `def`/`class`/assignment names, every import and what it
   binds, star-imported modules, each class's base list and member set. ~1.4s.
2. **Statement pass.** Walk each of the 67 slice files with a scope chain,
   emitting one statement per fact. ~0.9s.

### Resolution rules — stated explicitly, as the brief demanded

| # | Rule |
|---|---|
| R1 | A name bound in an enclosing **function** scope is `local` (anonymous). |
| R1a | …except a **parameter**, which is a named symbol owned by its function — the same model SCIP uses. A parameter reassigned in its own body keeps its parameter identity. |
| R2 | Otherwise a module-level `def`/`class`/assignment → `mod:name`. |
| R2a | Directly inside a **class body**, the class namespace beats the module namespace. Inside a *method* it does not — Python skips the class scope there. |
| R3 | `from m import n [as a]` binds `a`→(m, n); `import m.n [as a]` binds a module. Relative imports resolved from the file's package path. |
| R4 | **Re-export chase**: if `m`'s own table says `n` is itself an import, follow it (max 5 hops) to the defining module. |
| R5 | Attribute `base.attr`: module alias → `mod:attr` then R4; class name → `mod:Class.attr` walking same-module bases; `self`/`cls` in class C → `mod:C.attr`; a local whose *only* assignment is `v = Known(...)` → `mod:Known.attr`; a parameter annotated `p: Known` → `mod:Known.attr`. Anything else → **UNRESOLVED**. |
| R5a | If the base is itself an attribute chain (`a.b.c`), the type of the *field* `a.b` is unknown, so → **UNRESOLVED/chained-attribute**. Guessing here is the difference between honest and silently wrong (see §4). |
| R6 | `from m import *`: if `m` is an internal module whose table has the name, resolve it; else UNRESOLVED/star-import. |
| R7 | Builtins → external. |
| R8 | `getattr`/`setattr`/`eval`/`exec`/`__import__` → UNRESOLVED/dynamic. |

Only two inference rules exist (single-assignment construction, and parameter
annotations), both purely syntactic. Nothing walks a type lattice.

### Line shape and deviations

Per the x7a brief: `{"s","p","o","q":{file,line,col},"ref":"ast","hash"}`.
Three stated deviations:

- **Two extra fields**, `res` (`internal|external|local|unresolved|literal`) and
  `why` (failure class, present only when unresolved). These exist so the
  unresolved rate is *measurable* rather than a guess — the brief made it a
  headline number, so it has to be on the line.
- **Two extra predicates** beyond the six named: `imports` (module→symbol) and
  `inherits` (class→base). Both are one-line facts the walker gets for free and a
  map plainly needs.
- **Positions are 0-based line and column**, matching SCIP's own encoding, so the
  join needs no arithmetic. `q.col` is the column of the *identifier* — for
  `a.b`, the column of `b` — which is exactly what SCIP marks.

`ref` is `"ast"` on every line: nothing in this candidate came from SCIP.

---

## 2. Statement counts

Slice = 9 `src/utils` files + the 58 `src/` files that import from them (67
files, all 67 present in the SCIP index). The delivered
`evidence/x7b/statements.jsonl` is scoped: every statement in a `src/utils` file,
plus every statement in an importer file whose object lands in `src.utils.*` (the
inbound cross-package edges).

**Delivered slice — 2,847 statements**

| Predicate | Core (`src/utils`) | Inbound cross-package | Total |
|---|---|---|---|
| reads | 1,425 | 148 | **1,573** |
| calls | 380 | 32 | **412** |
| writes | 356 | 0 | **356** |
| imports | 57 | 123 | **180** |
| param-of | 157 | 0 | **157** |
| contains | 87 | 0 | **87** |
| documents | 81 | 0 | **81** |
| inherits | 1 | 0 | **1** |

By resolution class: 1,269 internal · 660 local · 622 external · **215
unresolved** · 81 literal (docstrings).

Of the 899 internal read/write/call edges in the delivered slice, **197 cross a
module boundary**: 17 outbound from `src/utils` into other packages, and 180
inbound from the 58 importers. Those are the cross-package edges the map cares
about, and they are in the artifact.

The full 67-file run (used for the accuracy measurement, at
`statements_all.jsonl`) is **44,554 statements**.

**Writes are the free win.** x1 established that scip-python sets `WriteAccess`
on **zero** occurrences of 220,915 — the read/write distinction is simply absent
from the index. The AST pass gets it from `ast.Store` vs `ast.Load` for nothing,
and its write *symbols* agree with SCIP **99.7%** of the time (1,473 of 1,477).
x1 asserted this from the API; it is now measured.

---

## 3. Resolution accuracy — the load-bearing measurement

**Method.** `scip_positions.py` re-decodes `evidence/x1/index.scip` (x1's
`edges.jsonl` keeps only the start line, which cannot identify an identifier)
and emits every occurrence in the 67 slice files with its full range and roles —
47,167 occurrences. `compare.py` joins AST statements to SCIP occurrences on
**(file, 0-based line, 0-based start column)** and scores only the four reference
predicates (`reads`, `writes`, `calls`, `inherits`); `contains`/`documents`/
`param-of`/`imports` are structural and need no resolution.

**The join was verified before any number was trusted.** `joincheck.py` prints
every SCIP occurrence on a source line next to the exact substring its columns
cover. On `cls._config_data = yaml.safe_load(f)` the two sides align identifier
for identifier at columns 20/24/39/44/54. No fuzzy matching anywhere.

### Full outcome table (all 38,970 scored reference statements)

| SCIP said | AST said | Count | Reading |
|---|---|---|---|
| internal | **same symbol** | **10,872** | correct |
| internal | different symbol | 229 | all SCIP star-import defects (§4) |
| internal | unresolved | 661 | honest miss |
| internal | local | 219 | modelling difference |
| internal | external | 39 | mostly `__name__` |
| local | local | 11,763 | agree |
| local | external | 2,612 | **AST is strictly better** (§4) |
| local | unresolved | 752 | attribute on an untyped local |
| external | external | 9,718 | agree |
| external | unresolved | 1,398 | third-party dispatch — the real hole |
| external | internal | 68 | `CONST.get` → `dict.get`; contained-type miss |
| *no SCIP symbol* | unresolved | 546 | pyright was blind too |
| *no SCIP symbol* | resolved | 56 | AST saw something SCIP did not |

### By predicate, on the internal population

| Predicate | Population | Correct | Rate |
|---|---|---|---|
| **writes** | 1,477 | 1,473 | **99.7%** |
| **reads** | 8,689 | 8,078 | **93.0%** |
| **calls** | 1,647 | 1,321 | **80.2%** |

Calls are the weak predicate, and it is entirely the dispatch hole plus SCIP's
star-import stubs.

### On the core slice only (`src/utils`, 9 files)

715 of 748 internal references correct — **95.6%** — with 22 unresolved, 3
said-local, 5 said-external, and **zero wrong**.

### The qualified-call hole, side by side with x6

| | MATLAB (x6, `mtree`) | Python (x7b, `ast`) |
|---|---|---|
| Qualified call sites | 9,855 | 3,214 |
| **Unresolved** | **5,527 (56%)** | **2,017 (62.8%)** |
| Bare/unqualified call sites | — | 3,882 |
| Bare unresolved | — | **161 (4.1%)** |

Unqualified calls are essentially solved (4.1%); qualified calls are essentially
unsolved (62.8%). The gap between those two numbers *is* the type-inference gap,
isolated. And as the headline notes, only **46** of the 2,017 are internal edges —
1,187 are third-party method calls and 784 are calls nobody can resolve.

**What this means for the fork decision.** x6 read MATLAB's 56% as a
language-specific wall. It is not. Python — with a first-class parser, a real
indexer available, and full stdlib introspection — has the same wall at the same
place. Whatever the extractor design is, it must treat unresolved qualified
dispatch as a *permanent* class, not a gap to close.

---

## 4. Failure classes — mine, and the ground truth's

### Mine

| Class | Count | What it is |
|---|---|---|
| `dispatch-unknown-base` | 2,253 | attribute on a local/expression whose type is unknown. **The dominant class by a factor of ten.** |
| `chained-attribute` | 163 | `a.b.c` where `a`'s type is known but field `b`'s is not |
| `dynamic` | 160 | `getattr`/`setattr`/`eval` |
| `star-import` | 42 | name from `import *` where the source module does not define it |
| `non-name-expr` | 7 | callee is a subscript or a call result |
| `unbound-name` | 6 | genuinely unresolvable in-file |

One dominant class, and it is the same one x6 named: **you cannot resolve
`obj.method()` without knowing the type of `obj`.** Everything else is noise.

### The ground truth's — four SCIP defects the measurement exposed

This matters as much as the accuracy number, because it means "measured against
SCIP" cannot be taken at face value. All four were found by inspecting
disagreements rather than assuming SCIP was right.

1. **Star imports resolve to a module stub.** `from ._config import *` then
   `get_circuit_profile(...)` — scip-python emits the symbol
   `` `src.evo_predictor.data_adapter._config`/__init__: ``, i.e. the *module*,
   not the function. The function is plainly defined at `_config.py:147`; the AST
   extractor names it correctly by reading `_config`'s own table. **229
   occurrences in this slice** — and this is 100% of my apparent "wrong"
   answers. On star-imported code the AST resolver is more accurate than SCIP.
2. **Third-party symbols are filed under the project name.**
   `` scip-python python f1brainz excursion-x1 `pandas.core.frame`/DataFrame# ``
   — the package field says `f1brainz` for a pandas symbol. Project membership
   has to be decided from the module path (`src.` prefix), not the package field.
   Naively trusting the field inflates the "internal" population by ~250 and
   would have corrupted the accuracy denominator. **221 occurrences here.**
3. **Annotated module-level variables get a doubled descriptor.**
   `F1_CALENDARS: Dict[...] = {...}` → `` `src.utils.constants`/F1_CALENDARS.F1_CALENDARS. ``.
   Unannotated ones do not. **136 occurrences here.**
4. **Imported module aliases and builtins are emitted as anonymous locals.**
   `yaml` in `yaml.safe_load(f)` is `local 0`; `isinstance` is `local 36`.
   **2,612 occurrences in this slice where SCIP carries no name and the AST
   extractor carries `yaml:safe_load` / `builtins:isinstance`.** This is a
   straight information gain for the AST side, and it is 6.5% of all scored
   references.

### Four bugs in my own resolver that the measurement caught

Worth recording because it is the argument for building the measurement at all —
each of these was invisible until joined against ground truth, and each was a
silently-wrong answer, not a crash.

- **Class-body scope precedence.** `config.py` has `PROJECT_ROOT` both as a
  `Config` field and as a module-level alias at line 332. My lookup checked the
  module table first; Python checks the class namespace first inside a class
  body (and *not* inside a method). Cost: 8 wrong answers -- small, but it was
  producing confident nonsense, and the same rule error would scale with any
  codebase that shadows class fields at module level.
- **Chained-attribute over-reach.** For `config.data.train_years` where
  `config: GoldCycleConfig`, I applied the last attribute to the *head's* type,
  producing `GoldCycleConfig.train_years` when the truth is
  `GoldCycleDataConfig.train_years`. 137 silently wrong answers, now honest
  unresolveds (R5a). **This trade is the right one for a map**: a wrong edge
  is worse than a missing edge, because a wrong edge cannot be detected
  downstream.
- **Parameters reassigned in their own body** lost their parameter identity and
  degraded to anonymous locals. Cost: 153.
- A subscript-store marker (`c[k] = v` → `writes c[]`) that SCIP has no
  equivalent for; folded in the comparison, kept in the artifact.

Accuracy moved **87.7% → 90.4%** across the whole repair sequence, on a fixed
denominator. The split is worth keeping straight: **+1.3pp came from fixing my
resolver** (class precedence +8, parameter identity +153) and **+1.4pp from
correcting normalisation artifacts in the ground truth** (descriptor doubling
+96, `__init__`/subscript +75). The chained-attribute fix bought no accuracy at
all -- it converted 137 confident wrong answers into 137 honest unresolveds,
which is why genuine wrong answers are now **zero**.

---

## 5. Cost accounting

| | |
|---|---|
| Extractor | **732 lines** of file, of which ~90 are the rules docstring and comments — one file, `astx.py` |
| Measurement harness | 722 lines total: 496 doing the measurement (`scip_positions` 159, `compare` 162, `make_slice` 84, `qualified_calls` 91) and 226 of sampling, join-proof and hand-check tooling (`samples` 66, `finalize` 56, `handcheck` 69, `joincheck` 35). **The harness is larger than nothing and smaller than the extractor — but it is what found four bugs in the extractor.** |
| **External dependencies** | **zero** — `ast`, `builtins`, `hashlib`, `json`, `os`, `sys`, all stdlib |
| Install step | **none** |
| Wall time, full run | **2.3 s** (440 modules indexed + 67 files extracted, 44,554 statements) |
| Parse failures | **0 of 67** |
| Setup cost | **0** — no `npm`, no patched dist file, no Windows regex bug, no 56-byte silent-empty failure mode |

Against x1's SCIP path: 30s install, a mandatory one-line patch to a broken
`dist/` file, one silent-empty index run, and **6m05s** per full index. The AST
extractor is **~160× faster** here — not quite like for like, since SCIP
type-resolves all 443 files while this parses 440 and fully extracts 67, but the
gap is two orders of magnitude and no accounting closes it. It is also
trivially incremental — re-parsing one changed file is milliseconds — which x1
listed as the untested question that gates a live map. Here it is not a question.

**The honest cost on the other side:** ~640 lines of resolution logic is ~640 lines
of *our* code to own, and four real bugs lived in it — two producing confidently
wrong output, one silently under-resolving, one a shape mismatch. SCIP's resolution logic is somebody else's problem and
is right more often per line — except on star imports, where it is not right at
all.

---

## 6. Sample-verified correctness

Eleven statements, selected to span every predicate and every resolution class
rather than the easy cases, hand-checked against source. Full output at
`evidence/x7b/handcheck.txt`; generator at `handcheck.py`.

| # | Statement | Verified against |
|---|---|---|
| 1 | `src.utils.config:` **contains** `…:Config` | `config.py:17` `class Config:` ✓ |
| 2 | `src.utils:` **documents** "Utility Functions Module" | `__init__.py` module docstring ✓ |
| 3 | `…:Config.db_path_for_year.cls` **param-of** `…:Config.db_path_for_year` | `config.py:36` classmethod ✓ |
| 4 | `…:Config.load_config` **calls** `src.models.exceptions:ConfigurationError` | `config.py:75` raise; relative import `..models.exceptions` chased; class defined at `exceptions.py:92` ✓ |
| 5 | `…:Config` **calls** `pathlib:Path` (external) | `config.py:21`, `from pathlib import Path` ✓ |
| 6 | `…:Config.load_config` **calls** UNRESOLVED/dispatch-unknown-base | `config.py:63` `config_path.is_absolute()` — SCIP resolves this to `pathlib/PurePath#is_absolute()`. **This is the type-inference gap, caught in the act, and correctly declared rather than guessed.** ✓ |
| 7 | `…:F1Calendar.get_season_calendar` **reads** `src.utils.constants:SPRINT_WEEKENDS` | `f1_calendar.py:90`; import at line 15; defined `constants.py:82` ✓ |
| 8 | `…:Config` **writes** `…:Config.PROJECT_ROOT` | `config.py:21` — class-body write, correct owner after the R2a fix ✓ |
| 9 | `…:Config.load_config` **reads** `local:config_path` | `config.py:63` local ✓ |
| 10 | `src.utils.config:` **imports** `src.models.exceptions:ConfigurationError` | `config.py:14` relative import resolved ✓ |
| 11 | `…:JobExecutionError` **inherits** `builtins:RuntimeError` | `utilization.py:68` ✓ |

11 of 11 correct. Item 6 is the most informative: the extractor knew what it did
not know.

---

## 7. Scoped nulls — what was and was NOT tested

This tested **one hand-written Python AST resolver, on 67 files of one Python
codebase, against one SCIP index, once.** It kills nothing outside that.

- **Not tested: any language but Python.** The resolver is built on Python's
  scoping rules and `ast`. Nothing here says a hand-written C++ or MATLAB
  resolver is comparably cheap — and for C++ it plainly is not (no stdlib
  parser). The 62.8%-vs-56% comparison to x6 is about *the dispatch hole*, which
  does generalise; the 640-line cost does not.
- **Not tested: the whole repo.** 67 of 443 indexed files. `src/utils` is a
  leaf-ish utility package; packages with heavy dynamic construction, decorators,
  or metaclasses would likely resolve worse. The 90.4% is a slice figure, and
  the slice was not chosen to be hard.
- **Not tested against a *correct* ground truth.** SCIP is the reference here and
  it has at least four defects (§4). The 229 "wrong" answers were adjudicated by
  reading source, but only for the star-import class; if SCIP is wrong in a way
  that *agrees* with my resolver, both are wrong and this measurement cannot see
  it. The correct-rate is an upper bound of agreement, not of truth.
- **Not tested: decorators, metaclasses, `__getattr__`, properties, dataclass
  field generation, `TYPE_CHECKING` blocks, conditional imports.** The resolver
  handles conditional module-level imports inside `if`/`try` by flattening them
  (last binding wins) and does nothing special for the rest.
- **Not tested: inheritance across packages.** `class_member` walks base classes
  within a module and follows one from-import hop; deeper cross-package MRO was
  not exercised or measured. The slice had exactly **one** `inherits` statement,
  which is far too few to say anything.
- **Not tested: incrementality, as measured.** Re-parsing one file is obviously
  fast, but the *module table pass* is currently whole-repo (1.4s) and no
  invalidation logic was written. Cheap, but asserted, not measured.
- **Not tested: rename/move symbol identity.** Same null as x1. Symbols here are
  `module:dotted.path` strings, so any rename or file move re-mints every
  statement in the affected module. For a durable statement store this is the
  open question, and neither candidate has addressed it.
- **Not tested: whether these statements are *useful*.** 2,847 lines of subject/
  predicate/object were produced and verified; no map section was generated from
  them and put in front of a reader. Same null x1 closed with.
- **Not tested: the two candidates head to head.** x7a ran independently and was
  not consulted. Comparability rests on both targeting the same 9-file core and
  the same line shape; any divergence in slice definition (I took `src/utils` +
  58 importers) has to be reconciled before the two accuracy figures are set
  side by side.

---

## Artifacts

All under `.agent-work/explore-code-map/evidence/x7b/`. f1Brainz was not
modified — every write landed in the evidence directory.

| File | What |
|---|---|
| `statements.jsonl` | **The deliverable** — 2,847 slice-scoped statements |
| `statements_all.jsonl` | 44,554 statements over all 67 files (the accuracy corpus) |
| `astx.py` | The extractor — 732 lines, stdlib only |
| `make_slice.py`, `slice_files.txt`, `slice_manifest.json` | Slice definition: 9 core + 58 importers |
| `scip_positions.py`, `scip_occ.jsonl` | Ground truth: 47,167 positioned SCIP occurrences, normalised |
| `compare.py`, `accuracy.json` | The accuracy measurement and all buckets |
| `qualified_calls.py`, `qualified_calls.json` | The 62.8% qualified-dispatch measurement |
| `statement_counts.json`, `finalize.py` | Counts by predicate and slice |
| `handcheck.py`, `handcheck.txt` | The 11 hand-verified statements |
| `samples.py`, `joincheck.py`, `wrong_samples.json` | Disagreement inspection and the position-join proof |
