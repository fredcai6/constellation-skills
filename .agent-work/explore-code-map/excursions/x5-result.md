# x5 result — scip-clang on superCoolSpaceSim: the C++ adoption cost

**Type:** prototype / measurement · **Verdict:** BLOCKED on this machine, with the
blocker precisely located — and it is not the one the brief expected
**Date:** 2026-08-05 · **Evidence:** `.agent-work/explore-code-map/evidence/x5/`

## Headline

**scip-clang cannot run on this machine, and the reason is permanent rather than
local: upstream closed Windows support `not_planned` on 2026-01-03 and rejected
the Windows build PR unmerged on 2026-02-20.** No release in the project's
history has ever shipped a Windows asset. This is not "we lack WSL today" — it
is "there is no Windows scip-clang to lack."

Everything *upstream* of the indexer, however, works cleanly and cost very
little:

- **`compile_commands.json`: 62 seconds, one command, zero failures, 110
  translation units.** The compilation database that the brief expected to be
  "where the adoption pain lives" was the cheapest step in the whole excursion.
- **A real Clang parses this GCC codebase perfectly**: 106/106 repository TUs,
  **zero errors**, using that database plus six MinGW include paths. The
  semantic prerequisite scip-clang needs is fully satisfied. Only the binary is
  missing.

There is also a finding the brief did not ask for and that invalidates its
premise: **`C:\Programs\superCoolSpaceSim_cpp` is empty** — one 0-byte stray
`nul` file, no sources. The real C++ codebase is the sibling
`C:\Programs\superCoolSpaceSim` (136 source files, 17,465 lines). I measured
that instead, read-only.

---

## 1. What it took

Total elapsed ≈ 85 minutes, of which the blocked-path investigation was ~20 and
the baseline census ~35.

| Step | Command / probe | Result |
|---|---|---|
| Locate the target | `Get-ChildItem -Force C:\Programs\superCoolSpaceSim_cpp` | **1 file, `nul`, 0 bytes.** Recursive file count: **1**. The briefed repo does not exist as a codebase. |
| Find the real one | `Get-ChildItem C:\Programs -Directory` | `superCoolSpaceSim` (no `_cpp`): 1,230 `.cpp`, 230 `.hpp`, 212 `.cc`, 149 `.h` repo-wide |
| Toolchain probe | `cmake/ninja/clang/clang-cl/cl/wsl/docker/go --version` | cmake **4.2.3**, ninja **1.12.1**, MSYS2 GCC **14.2.0**; **no clang, no clang-cl, no MSVC, no Visual Studio (no `vswhere`), no WSL, no Docker, no Go** |
| Build system | `build/CMakeCache.txt` | Generator **Ninja**, `CMAKE_HOME_DIRECTORY=C:/Programs/superCoolSpaceSim/src`, compiler `C:/msys64/ucrt64/bin/c++.exe`, `CMAKE_EXPORT_COMPILE_COMMANDS` **empty** — and **no `compile_commands.json` existed anywhere in the repo** |
| **CDB generation — SUCCEEDED first try** | `cmake -S C:/Programs/superCoolSpaceSim/src -B <evidence>/x5/build -G Ninja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=.../cc.exe -DCMAKE_CXX_COMPILER=.../c++.exe -DCMAKE_MAKE_PROGRAM=.../ninja.exe` | **62.3s**, exit 0, **110 entries / 109,283 bytes**. Fetched nlohmann/json + googletest via FetchContent, found HDF5 1.14.5. |
| Attempts 1–3 at scip-clang | see §"the three attempts" below | **all three blocked** |
| Baseline census | `census_clang.py` over the CDB, libclang 18.1.1 | **106/106 TUs, 0 errors, 375s** |

**The one real failure.** My first census walked every AST cursor in the
translation unit, including all of `<vector>`, `<algorithm>` and googletest —
millions of cursors per TU in Python. It produced no output in 5 minutes and was
killed. Pruning the walk to subtrees rooted in repository files (`census_clang.py`,
the `for top in tu.cursor.get_children()` guard) took the full run to 375
seconds. Worth recording because any extraction pipeline built on libclang hits
this same wall.

**Applying x1's lessons.** x1's non-empty-output assertion transferred directly
and paid off: I asserted on `compile_commands.json` (110 entries, not just
"exit 0") and on `census.json`. x1's Windows path hazard did not recur here —
CMake emits a mix of forward and backslash paths and libclang accepted both after
a `.replace("\\", "/")` normalization in `tu_args`. x1's pure-Python SCIP decoder
was **not** needed, because no index was ever produced.

### The three attempts (full evidence in `evidence/x5/attempts.md`)

**Attempt 1 — official release binaries.** `GET
/repos/sourcegraph/scip-clang/releases/latest` → **v0.4.0**, published
2026-02-23, three assets: `scip-clang-arm64-darwin`,
`scip-clang-x86_64-linux`, `scip-clang-dev-x86_64-linux`. Walking **every**
release from v0.1.3 to v0.4.0: the same three shapes every time. **No release
has ever shipped a Windows asset** — no `.exe`, no `.zip`, no
`win`/`windows`/`msvc`/`mingw` in any asset name. The README is explicit:
*"Binary releases are available for x86_64 Linux (glibc 2.16 or newer) and arm64
macOS."* Windows appears nowhere in it.

**Attempt 2 — container or compatibility layer.** `wsl --list --quiet` → *"The
Windows Subsystem for Linux is not installed"* (independently re-confirms x1).
`docker --version` → not found. There is no surface on this machine that can
load an ELF binary. Installing WSL2 or Docker Desktop needs an elevated install
and a reboot — outside what an excursion may do to the host.

**Attempt 3 — community or unofficial build.** I went to upstream rather than
trusting search summaries. `GET /search/issues?q=repo:sourcegraph/scip-clang+windows+in:title`
returns **total_count = 2**, and both are decisive:

- **Issue #170 "☂️ Windows support"** — opened 2023-04-11, **closed
  `not_planned` on 2026-01-03**, every checklist item still unticked. Its body
  enumerates exactly the work never done: *"grailbio/bazel-toolchain that we're
  using doesn't support Windows"*, *"There are certain code paths which are
  OS-specific"*, *"Automatically publish a release binary for Windows"*,
  *"Support MSVC-style command-line flags starting with `/`"*. Stated goal:
  *"Using scip-clang on Windows should be as easy as on Linux or macOS."*
- **PR #168 "build: Add support for Windows"** — **closed 2026-02-20 with
  `merged: false`, `merged_by: null`.** Rejected.

No vcpkg port (`C:\vcpkg\ports\*scip*` → 0 hits), nothing on npm under
`scip-clang` or `@sourcegraph/scip-clang`, no chocolatey/scoop/conda-forge
package. The 2023 announcement blog's *"Windows support is currently being
explored"* is stale by two years; issue #170's `not_planned` closure is the
current state of that exploration.

### What a Linux/CI run would need

From upstream docs, all satisfied by this project except the host OS:

- Invocation is a one-liner: `scip-clang --compdb-path=build/compile_commands.json`.
- *"About 2MB of temporary space for every TU"* → 110 TUs ≈ **220 MB**.
- *"On Linux, about 2MB of space in `/dev/shm` per core"* — a Linux kernel
  primitive, and concrete evidence the port is not cosmetic.
- *"2GB RAM per core is generally sufficient."*
- **Compiler compatibility is not a blocker**: *"Codebases using GCC and/or
  Clang for routine compilation are both supported. For codebases exclusively
  built using GCC, compatibility should be as good as Clang's compatibility."*
  superCoolSpaceSim is GCC-only, so it sits inside the supported set — and my
  zero-error clang parse is direct empirical confirmation.

**But the compilation database generated here will not travel.** The 110 entries
contain **806 Windows absolute paths** and **110 references to `C:/msys64/...`**.
Every `directory`, `file`, `-I`, and compiler path is a Windows path pointing at
a MinGW toolchain that does not exist on a Linux runner. So "generate the CDB on
Windows, index on Linux" **does not work** — the Linux CI job must check out the
repo and re-run `cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` itself, against a
Linux GCC. That is cheap (62s here) but it means the CI job must be able to
*configure* the project, including its HDF5 dependency and two FetchContent
network fetches. One genuine piece of good news: the CDB uses **0 MSVC-style
`/flags`** (all GNU `-` style), so scip-clang's known MSVC-flag gap is irrelevant
to this codebase.

---

## 2. What the index would contain, in our vocabulary

**No SCIP index was produced, so this section is a measured *baseline*, not an
index census.** It is built from the same compilation database scip-clang would
consume, parsed by a real Clang 18.1.1 (the `libclang.dll` bundled in the PyPI
`libclang` wheel — 84 MB, installed in **7.2 seconds**, and notably the only way
to get a Clang onto this machine at all). Because scip-clang is itself
Clang-based and consumes the same CDB, these counts are a close upper bound on
what it would emit.

`evidence/x5/census.json`, deduplicated by USR across all 106 TUs:

### Information containers

| Container kind | Count |
|---|---|
| Class fields | **814** |
| Named parameters | **783** |
| Module/class-level state | **433** |
| Enum constants | 3 |
| **Total named containers** | **2,033** |
| Function-local variables | **4,648** (by distinct source location) |

### Information transformers

| Kind | Count |
|---|---|
| Methods | 455 |
| Constructors | 407 |
| Destructors | 396 |
| Free functions | 280 |
| **Total** | **1,538** |

### Types and structure

408 classes · 150 structs · 27 namespaces · 7 type aliases · 1 enum ·
**141 distinct repository files** touched.

### Relationships

**8,559 distinct caller→callee pairs** and **19,558 member-reference
expressions**, recovered from the AST alone.

### The correction that matters

**395 of those "classes" are googletest macro expansions, not application
types.** `grep -c "TEST_F|TEST_P|TEST("` over `src/tests/` returns exactly
**395**, and each `TEST_F` expands to a class with a constructor, a destructor
and a `TestBody()` method — which accounts for almost all of the 408 classes,
407 constructors, 396 destructors, and a large share of the 455 methods. The
honest reading of the application's own surface is closer to **156
class/struct declarations in the 94 non-test source files** (grep-level count),
of which the census's **150 structs** are the substantive part. This is a
struct-and-free-function codebase — 280 free functions against ~60
non-macro methods — which is exactly what a physics simulation looks like.

Any real extraction pipeline must therefore **partition test scaffolding from
application code before counting anything**, or its numbers will be dominated by
macro-generated fixtures. That lesson is independent of scip-clang and applies
to the map builder directly.

### On the WriteAccess / Import gap x1 measured — UNTESTED

**I cannot answer the brief's second question.** Symbol *roles* are a property of
what the SCIP emitter chooses to write, not of the AST. x1's finding — that
scip-python tags every non-definition reference `ReadAccess` and emits **zero**
`WriteAccess` and **zero** `Import` — can only be checked against an actual
scip-clang index. A libclang AST census cannot stand in for it: libclang exposes
the information (an lvalue in an assignment's LHS is recoverable from
`CursorKind.BINARY_OPERATOR` structure) but that says nothing about what
scip-clang chooses to emit.

What is worth recording for whoever runs this on Linux: scip-clang and
scip-python are **entirely separate codebases** (C++/Clang vs
TypeScript/pyright) sharing only the SCIP schema. x1's zero-WriteAccess result
is a scip-python property and **must not be generalized to scip-clang** — the
schema defines the roles, and there is no evidence either way about whether
scip-clang populates them. This is the single highest-value question for the
Linux run.

---

## 3. Granularity notes

From the AST baseline, at the granularity a Clang-based indexer sees:

- **Locals: yes, and richer than Python's.** 4,648 function-local variables with
  exact locations. Unlike x1's finding for scip-python — where a local appears as
  an anonymous `local 42` and the *name is not in the index* — a Clang cursor
  carries `spelling` (the name) and full type. Whether scip-clang *writes* those
  names into the SCIP index is untested, but the information is present in the
  frontend.
- **Fields: yes.** 814, the largest named-container population.
- **Parameters: yes**, 783, with resolved types.
- **Templates: effectively absent in this codebase.** The census found **0 class
  templates and 0 function templates** among repository definitions. That is a
  property of superCoolSpaceSim, not a limitation of the tooling — which means
  **this codebase cannot answer "how does SCIP handle C++ templates?"**, the
  question most likely to differentiate C++ indexing from Python. See nulls.
- **Macro-generated entities are indistinguishable from hand-written ones** at
  the AST level without checking whether the cursor's location is inside a macro
  expansion. The 395 gtest classes are the demonstration. Python has no
  equivalent hazard; this is genuinely new surface for C++.
- **Headers are the unit of duplication.** 141 distinct repository files were
  reached from 106 TUs, and header declarations are re-parsed once per including
  TU. Deduplication by USR is mandatory — a naive census would multiply-count
  every header entity. This is the structural difference from Python, where
  module ≈ file ≈ one parse.

---

## 4. Adoption-cost verdict, next to x1's Python result

| | x1 — scip-python on f1Brainz | x5 — scip-clang on superCoolSpaceSim |
|---|---|---|
| Install | `npm install`, 30s | **impossible — no Windows binary has ever existed** |
| Blocker | Windows regex bug, fixed by a **1-line patch** | Upstream **closed Windows support `not_planned`**; PR rejected unmerged |
| Prerequisite artifact | none (pyright config already present) | `compile_commands.json` — **62s, one command, worked first try** |
| Time to a working index | **~15 minutes** | **never reached on this machine** |
| Index produced | 22 MB, 443 documents | **none** |

**The verdict inverts the brief's expectation.** The brief predicted the
compilation database would be where the pain lived. It was not: it was the
single cheapest step, one command, first try, 62 seconds, and it produced a
database clean enough for a real Clang to parse all 106 TUs with zero errors.
The pain is entirely in **binary availability**, and it is not a temporary gap —
it is a documented, dated upstream decision to stop.

So the two costs are different in kind, not degree. x1's blocker was a
**one-line patch away** and a Windows-first user can adopt scip-python today.
x5's blocker is **not patchable by us at any budget**: the remedy is a Linux
runner, which changes the deployment story rather than the setup story.

**The practical consequence for a code-map design.** If the map is to cover C++
on a Windows workstation, SCIP-based extraction is not available *locally* — it
is a CI-only capability, and CI must be able to configure the project (HDF5 plus
two network FetchContent dependencies) to regenerate a Linux-native CDB, because
the Windows CDB's 806 absolute paths do not travel. A live, incremental,
local map for C++ on this machine cannot be built on scip-clang.

**The consolation is larger than it looks.** libclang cost 7.2 seconds to
install via `pip` and parsed the entire codebase natively on Windows with zero
errors. Every structural number in §2 came from it. If the map needs C++
structure on Windows, **libclang is available today and scip-clang is not** —
and x1 already concluded that the read/write layer wants a plain AST pass rather
than SCIP anyway. That points at a single AST-based extractor rather than a
per-language SCIP indexer fleet, at least for the structural spine. I did not
test that proposition; I am naming it as the thing this excursion makes
askable.

---

## 5. Scoped nulls — what was and was NOT tested

**What this kills:** running scip-clang on *this* Windows 11 machine, on
2026-08-05, with no WSL/Docker/Clang/MSVC installed. Nothing more.

**This does NOT kill scip-clang.** It was never executed. Its correctness,
completeness, output quality, symbol roles, and performance are **entirely
unmeasured here**. On Linux it is a supported, actively-released tool — v0.4.0
shipped 2026-02-23, five months before this run — and the project it would index
sits inside its documented support set (GCC-only codebases are explicitly
supported; the CDB uses zero MSVC-style flags).

Specifically NOT tested:

- **The brief's second question is unanswered.** Whether scip-clang populates
  `WriteAccess` and `Import` is unknown. x1's zero-for-both result is a
  *scip-python* property; the two indexers share only a schema. Treating x1's
  gap as a SCIP-wide property would be unfounded, in either direction.
- **Whether the emitted index carries the structural completeness x1 measured.**
  No index exists. §2 is a libclang baseline over the same CDB — a close upper
  bound on what scip-clang would see, but *not* a measurement of what it emits.
  The gap between "the frontend has it" and "the indexer writes it" is exactly
  where x1 found scip-python's misses (`SymbolInformation.kind` never set,
  `display_name` zero, 105 relationships for 600 classes).
- **Templates.** superCoolSpaceSim contains **zero** class or function template
  definitions, so the hardest and most C++-specific indexing question is
  untouched. A template-heavy codebase would be a materially different test, and
  no conclusion here transfers to one.
- **The test/application partition is estimated, not measured.** I established
  395 gtest macros exist and that they explain the class/ctor/dtor inflation, but
  the census did not record per-declaration file paths, so the exact
  application-only counts are inferred from a grep, not computed. Re-running
  `census_clang.py` with a `tests/` filter would settle it in ~6 minutes.
- **The briefed repository was never measured** — `superCoolSpaceSim_cpp` is
  empty. If it is meant to hold something, the premise of this excursion needs
  re-checking before its numbers are reused. All results here describe
  `C:\Programs\superCoolSpaceSim`.
- **Correctness of the libclang parse against a real build.** Zero diagnostics is
  strong evidence, but I did not compile the project — no object files were
  produced and no build was run. A clean parse is not a clean build.
- **Incrementality, rename/move symbol stability, and a second C++ codebase** —
  all still open, exactly as x1 left them.
- **Whether a Linux run would actually succeed.** Asserted from upstream docs and
  a zero-error local parse. Not run. `/dev/shm` sizing, the 220 MB temp
  requirement, and HDF5 availability on a CI image are all untested assumptions.

**Default next move:** run scip-clang v0.4.0 on a Linux runner against a
Linux-regenerated CDB for this project, and answer the one question this
excursion could not — does scip-clang populate `WriteAccess` and `Import` where
scip-python emits zero? That single answer determines whether SCIP is the right
substrate for the read/write layer or whether, as x1 suspected, an AST pass owns
it regardless of language.

---

## Artifacts

All under `.agent-work/explore-code-map/evidence/x5/`:

| File | What |
|---|---|
| `attempts.md` | The three attempts with verbatim API/doc evidence |
| `build/compile_commands.json` | **110-entry compilation database** — the reusable output of this excursion |
| `cmake_configure.log` | Full configure output, 62.3s |
| `census_clang.py` | libclang AST census over the CDB (includes the traversal-pruning fix) |
| `census.json` | All structural counts quoted in §2 |
| `census_errors.txt` | **Empty — 0 TUs with errors** |
| `census_progress.log`, `census_run.log` | Per-TU parse timings |
| `gcc_include_paths.txt` | The six MinGW UCRT64 system include paths clang needed |
| `pylib/` | The `libclang` 18.1.1 wheel (bundled `libclang.dll`, 84 MB) |

`C:\Programs\superCoolSpaceSim` was not modified: the CMake build directory,
all FetchContent downloads, and every output were written under `evidence/x5/`.
