# Excursion Brief: scip-clang on superCoolSpaceSim_cpp — the C++ adoption cost

## The one named question

What does it actually cost to get a SCIP index out of a real C++ codebase (`C:\Programs\superCoolSpaceSim_cpp`) with scip-clang — and does the emitted index carry the same structural completeness (and the same WriteAccess gap) x1 measured on Python?

## Type

prototype

**Why this type:** x1 measured Python only and explicitly scoped C++ as untested; scip-clang's compilation-database requirement is where the adoption pain is expected to live, and only running it measures that.

## What "answered" looks like

`excursions/x5-result.md` containing: (1) what it took — compile_commands.json generation, scip-clang install (it ships Linux binaries; on Windows expect WSL absence — document what works or fails, exactly), wall time, every failure; (2) index contents in our vocabulary (containers/transformers/occurrence counts; whether WriteAccess/Import roles are populated — x1 found scip-python emits zero of both); (3) granularity notes (locals? fields? templates?); (4) an honest adoption-cost verdict next to x1's 15-minutes-and-one-patch Python result; (5) scoped nulls.

## Budget / stop conditions

- Budget: ~75 minutes. scip-clang may be genuinely impossible on native Windows (Linux-only binaries, no WSL on this machine per x1) — if so, establish that crisply (3 distinct attempts: native binary?, container?, any community Windows build?) and report the blocked path as the adoption-cost finding, plus what a Linux/CI run would need. An honest "not runnable on this machine" IS an answer.
- `C:\Programs\superCoolSpaceSim_cpp` is READ-ONLY. CMake configure may write ONLY to a build dir under the evidence area (`cmake -S <repo> -B <evidence>/build`), never inside the repo.
- All outputs under `.agent-work/explore-code-map/evidence/x5/`.
- Reuse x1's tooling: pure-Python SCIP decoder at `evidence/x1/decode_scip.py`; apply x1's lessons (assert the index is non-empty; backslash paths on Windows).
- **Scoped nulls:** a null verdict states what was and what was NOT tested; a Windows-blocked scip-clang does not kill scip-clang.

## Question
What does a SCIP index of superCoolSpaceSim_cpp cost to produce on this machine, and does it carry the structural completeness and role gaps x1 measured?

## Branch
measurement

**Why this branch:** the deliverable is a measured adoption cost and index census.

## Host-project conventions
- **Runtime / language:** C++ project (inspect for CMake/Make/other build system first). Windows 11 host, no WSL (x1 verified), no Go. Node/npm available.
- **Task runner:** n/a — excursion runs its own commands.
- **Routing:** n/a
- **Other conventions:** none.

## Location
worktree

**Driver:** agent-driven; target repo read-only; outputs in explorer work area only.

## Stop conditions
- Answered when the five deliverable sections are filled (measured, or crisply blocked with evidence).
- Budget and exclusions as above.

## Return format
`PROTOTYPE_RESULT` at `excursions/x5-result.md` — the answer, what was tested / NOT tested, what it taught, disposition.
