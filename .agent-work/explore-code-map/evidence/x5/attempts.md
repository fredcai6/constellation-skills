# x5 — scip-clang on Windows: the three attempts, with evidence

Machine probe (2026-08-05), all from one PowerShell block:

| Tool | Result |
|---|---|
| `cmake --version` | 4.2.3 |
| `ninja --version` | 1.12.1 (also `C:\msys64\ucrt64\bin\ninja.exe`) |
| `clang --version` | **not found** |
| `clang-cl --version` | **not found** |
| `cl` on PATH | **not found**; recursive search of `C:\Program Files*` for `cl.exe` → 0 hits |
| `vswhere.exe` | **absent** — no Visual Studio installation registered |
| `wsl --list --quiet` | "The Windows Subsystem for Linux is not installed." |
| `docker --version` | **not found** |
| `go version` | **not found** |
| `python --version` | 3.14.3 |
| `node --version` | v24.15.0 |
| `g++ --version` | **14.2.0**, MSYS2 UCRT64 (`C:\msys64\ucrt64\bin\g++.exe`) |

The only C++ toolchain on this machine is MSYS2 UCRT64 GCC 14.2.0. There is no
Clang of any kind (the `libclang.dll` used later for the census came from a
PyPI wheel, not from an installed toolchain).

## Attempt 1 — official release binaries

`GET https://api.github.com/repos/sourcegraph/scip-clang/releases/latest`
→ tag **v0.4.0**, published 2026-02-23. Assets, verbatim:

```
scip-clang-arm64-darwin          71,043,408 bytes
scip-clang-dev-x86_64-linux     239,951,376 bytes
scip-clang-x86_64-linux         149,130,216 bytes
```

`GET .../releases` (all releases, v0.1.3 → v0.4.0): every release ships exactly
the same three shapes — `*-x86_64-linux`, `*-dev-x86_64-linux`, and a darwin
binary (`x86_64-darwin` through v0.3.1, `arm64-darwin` from v0.3.2). **No
release has ever shipped a Windows asset** — no `.exe`, no `.zip`, no
`win`/`windows`/`msvc`/`mingw` in any asset name, at any version.

The README is explicit: *"Binary releases are available for x86_64 Linux (glibc
2.16 or newer) and arm64 macOS."* Windows is not mentioned as a platform
anywhere in the README.

**Verdict: no artifact exists to run.** The Linux assets are ELF executables;
with no WSL and no container runtime there is nothing on this machine that can
load them.

## Attempt 2 — container / compatibility layer

- `wsl --list --quiet` → "The Windows Subsystem for Linux is not installed."
  (independently re-confirms x1's finding)
- `docker --version` → command not found; no Docker Desktop, no daemon.

**Verdict: no Linux execution surface on this machine.** Installing WSL2 or
Docker Desktop both require a reboot and an elevated install, which is outside
an excursion's budget and outside what an excursion may do to the host.

## Attempt 3 — community / unofficial Windows build

Searched upstream directly rather than trusting search-engine summaries:

- `GET /search/issues?q=repo:sourcegraph/scip-clang+windows+in:title` →
  **total_count = 2**. Both are the canonical Windows threads:
  - **Issue #170 "☂️ Windows support"** — opened 2023-04-11, **closed
    `not_planned` on 2026-01-03**. Every checklist item is still unticked. Its
    body names exactly the work that was never done: *"Right now,
    grailbio/bazel-toolchain that we're using doesn't support Windows"*,
    *"There are certain code paths which are OS-specific"*, *"Automatically
    publish a release binary for Windows"*, *"Support MSVC-style command-line
    flags starting with `/`"*, *"Automatic resource directory detection needs to
    correctly determine the standard library on Windows"*. Stated goal: *"Using
    scip-clang on Windows should be as easy as on Linux or macOS."* — closed
    unachieved.
  - **PR #168 "build: Add support for Windows"** — opened 2023-04-06,
    **closed 2026-02-20 with `merged: false`, `merged_by: null`.** Rejected,
    not integrated.
- No `scip-clang` port in the local vcpkg checkout (`C:\vcpkg\ports\*scip*` → 0
  hits); nothing on npm under `scip-clang` or `@sourcegraph/scip-clang`;
  no chocolatey/scoop/conda-forge package surfaced.

**Verdict: no community build exists, and upstream formally abandoned the
effort seven months before this excursion ran.** The 2023 announcement blog's
"Windows support is currently being explored" is stale — issue #170's
`not_planned` closure in January 2026 is the current state of that exploration.

## What a Linux/CI run would need (from upstream docs)

- Invocation: `scip-clang --compdb-path=build/compile_commands.json`
- *"About 2MB of temporary space for every TU in the compilation database"* —
  110 TUs here ≈ 220 MB.
- *"On Linux, about 2MB of space in `/dev/shm` per core"* — a Linux-kernel
  primitive, and a concrete reason the port is not cosmetic.
- *"2GB RAM per core is generally sufficient."*
- Compiler compatibility is **not** a blocker: *"Codebases using GCC and/or
  Clang for routine compilation are both supported. For codebases exclusively
  built using GCC, compatibility should be as good as Clang's compatibility."*
  superCoolSpaceSim is a GCC-only codebase, so it is in the supported set.
