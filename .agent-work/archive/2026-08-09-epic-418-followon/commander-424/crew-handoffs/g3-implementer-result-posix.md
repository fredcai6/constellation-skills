# Implementation Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3fix4` (post-archive fix, issue #424, workstream F)

## Completed slice
Replaced both `test -f` postcondition checks in `tests/test_mcp_spine_server.py`'s
`write_gated_spine()` fixture with a portable, argv-passed, `shlex.quote`d
file-existence check driven through `sys.executable` — the house pattern this repo
already uses in `tests/test_checklist_engine.py` (`PASS_COMMAND`/`FAIL_COMMAND`).

## Scope
**Files changed:**
- `tests/test_mcp_spine_server.py` — added `file_exists_check()` helper + `_FILE_EXISTS_SNIPPET`
  constant, `import shlex`; replaced both `"command": f"test -f {w}/..."` call sites (former
  lines 67, 92).
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`); the new
  module-scope helper shifted the file's entity count by 1 (50 → 51), same class of
  map-staleness the prior `winfix` round hit.
- Engine bookkeeping (committed alongside, matching the `winfix` precedent):
  `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/g3fix4-implementer-plan-posix.json`
  (+ `.journal`), the plan's `mechanical/`/`context/` gauge files under
  `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/g3fix4-posix-test-f-portability/`,
  and the pre-existing `crew-handoffs/g3-implementer-handoff-posix.md` + `crew-runs.json` entry.

**Specific exclusions touched:** no. `scripts/mcp_spine_server.py`, `scripts/checklist_engine.py`,
`.mcp.json`, every template, all imperative text, `settings.json`, checklist JSON, and
`episodes/` are untouched. `tests/test_mcp_identity.py` and `tests/test_mcp_imperative_equivalence.py`
were swept (below) and needed no changes.

## Behavior changed
Yes, but only for the test fixture, not the product. The postcondition text a
gated spine can use to check file existence is now portable; the engine and
`scripts/mcp_spine_server.py` are unmodified — they were already correct (a
check that cannot run is a failing check, by design).

## Map Impact
- **Structural anchors touched:** `tests.test_mcp_spine_server` — module-scope
  addition of `file_exists_check()` / `_FILE_EXISTS_SNIPPET` (entity count 50 → 51 in
  `map/INDEX.md`, rebuilt).
- **Capabilities added/changed/affected:** none — no product-facing capability changed;
  this is a test-fixture-only change to how one postcondition's `command` text is built.
- **Constraints/assumptions touched:** reaffirms the existing `command`-postcondition
  constraint documented in `scripts/checklist_engine.py`'s `_run_check_command`/
  `_find_posix_shell` (checks run under a POSIX shell — bash on Windows via Git for
  Windows, sh on POSIX; POSIX-form text is never routed through cmd.exe) — this fix
  makes the fixture actually honor that constraint instead of assuming a `test` builtin
  the constraint never promised.
- **Trust limitations / drift found:** none beyond what's in the sweep section below.
- **Triage candidates:** none found beyond scope.

## Test mode
**Required:** test-after / evidence-only (fixture defect fix; no red state exists on
this Linux host for a POSIX-only bug — `test -f` works fine on POSIX, so TDD red→green
does not apply here; verified per the handoff's own framing).
**Satisfied:** yes — before/after demonstrated directly (see below) rather than merely
asserted.

## Evidence

### 1. The target file, `tests/test_mcp_spine_server.py`

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
```
```
......................                                                   [100%]
22 passed in 0.81s
```
**Result:** pass. Includes the four previously-Windows-only-red tests:
`test_spine_start_and_advance_drive_a_gate_to_complete`,
`test_spine_advance_mechanical_flag`,
`test_spine_evidence_attach_satisfies_artifact_postcondition`,
`test_spine_evidence_waive_satisfies_without_making_check_true`.

### 2. Full suite

```bash
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
First run (before the map rebuild):
```
1 failed, 2177 passed, 1 skipped, 1061 subtests passed in 98.41s (0:01:38)
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```
Rebuilt the map (`python -m scripts.code_map build --root .`; only `map/INDEX.md`
changed — `tests` 3564 → 3565 entities, `tests.test_mcp_spine_server` 50 → 51). Re-ran:
```
2178 passed, 1 skipped, 1061 subtests passed in 98.40s (0:01:38)
```
**Result:** pass. Exact match to the stated baseline (2178 passed, 1 skipped, 1061
subtests, 0 failed).

## Both directions of the new check, demonstrated with real exit codes

Ran the exact command string `file_exists_check()` builds, through the same
POSIX-shell selection logic the engine uses (`subprocess.run([shell, "-c", cmd], ...)`),
against a temp directory **deliberately named with a space** (`/tmp/posix fix u735m975`)
to exercise the quoting the same way a Windows `%TEMP%` path with a space would:

```bash
$ python3 - <<'PYEOF'
... (loads file_exists_check from tests/test_mcp_spine_server.py, builds the
     command for <tmpdir with space>/notes.txt, runs it once before the file
     exists and once after)
PYEOF
```
```
COMMAND STRING: /usr/bin/python3 -c 'import sys, pathlib; sys.exit(0 if pathlib.Path(sys.argv[1]).is_file() else 1)' '/tmp/posix fix u735m975/notes.txt'
shell used: /usr/bin/sh
ABSENT -> exit code: 1 stdout: '' stderr: ''
PRESENT -> exit code: 0 stdout: '' stderr: ''
BOTH DIRECTIONS CONFIRMED: absent -> non-zero, present -> 0
SCRIPT EXIT CODE: 0
```

This is the load-bearing evidence the handoff asked for by name: the check
genuinely fails while the file is absent (exit 1, not merely "asserted
non-zero") and genuinely passes once it exists (exit 0) — the property the
`waive` test in `test_spine_evidence_waive_satisfies_without_making_check_true`
depends on.

## Sweep findings (all three MCP-door files)

Grepped `tests/test_mcp_spine_server.py`, `tests/test_mcp_identity.py`, and
`tests/test_mcp_imperative_equivalence.py` for six categories:

| # | category | result |
|---|---|---|
| 1 | shell builtins/`sh`-only syntax in `command` checks, `shell=True` | Only the two `file_exists_check()` sites remain as `"command"` postconditions anywhere in these three files; both are now portable. Nothing else matched `test -f/-e/-d`, `[ ... ]`, or `shell=True`. |
| 2 | `/dev/null` | Zero hits. |
| 3 | `os.kill`/`signal.*` | Zero hits. |
| 4 | backticks (shell command substitution) | Every hit is Markdown code-span formatting inside a docstring or comment (e.g. `` `mcp_spine_server.py` ``, `` `test -f` ``) — not shell syntax, never executed. **Deliberately left alone.** |
| 5 | `&&`/`\|\|` chaining inside a `command` check | Zero hits. |
| 6 | forward-slash-only path assembly inside command text | Two residual hits are the fix itself (`file_exists_check(f"{w}/notes.txt")`, `file_exists_check(f"{w}/optional_report.txt")`) — already portable via `shlex.quote`. A third, `f"create {w}/notes.txt"` (the g1 `imperative` field), is human-readable prose rendered to a client, never handed to a shell, so shell backslash/quoting mangling cannot occur there. **Deliberately left alone.** A fourth, an assertion message in `test_mcp_imperative_equivalence.py` (`f"only checked {checked}/{len(self.gates)} ..."`), is a pytest failure message, not a command. **Deliberately left alone.** |

Additionally checked `select.select` (informational, not one of the six named
categories, but the handoff calls it out as one of the three prior platform
breaks): three hits in `tests/test_mcp_identity.py`, all in comments describing
the *already-fixed* prior defect (the `winfix` reader-thread rewrite) — no live
`import select` remains in that file (`grep -n "^import " tests/test_mcp_identity.py`
confirmed). **Deliberately left alone**, no action needed.

**Conclusion:** no real portability defect found outside the two `test -f`
sites fixed in this round. `tests/test_mcp_identity.py` and
`tests/test_mcp_imperative_equivalence.py` needed no changes — neither is
touched by this commit.

## TDD evidence, if required
Not applicable — this is a test-after/evidence-only fixture fix, not a
product behavior change with a red/green surface (see Test mode above).
- Failing test observed: N/A — no code-level red state; the *original* bug's
  red state only manifests on Windows CI (out of reach here). Demonstrated
  instead via direct exit-code inspection of the pre-fix and post-fix check
  strings (see "Both directions" above).
- Passing test observed: `tests/test_mcp_spine_server.py` — 22 passed.
- Refactor while green: no additional refactor beyond the minimal fix.

## Docs/contracts touched
- none

## Assumptions
- None beyond what's stated in the Local vs. reasoned split below.

## Local vs. reasoned-about-Windows split

**Verified locally (Linux, this run):**
- The old `f"test -f {w}/notes.txt"` command text is gone from both sites; the
  new `file_exists_check()` helper is in place and used at both call sites.
- The new check's command string, run through the same `[shell, "-c", command]`
  invocation shape the engine uses, exits 1 when the target file is absent and
  0 once it exists — against a temp directory path containing a space, so the
  `shlex.quote` quoting is exercised, not merely present in the source.
- `tests/test_mcp_spine_server.py` (22/22) and the full suite (2178 passed, 1
  skipped, 1061 subtests, 0 failed) both pass on this Linux host, matching the
  stated baseline exactly.
- The sweep's six grep categories ran to completion with real output captured
  above; nothing outside the two known sites matched.

**Reasoned about, not run (no Windows host available):**
- That `shlex.quote` on a Windows-style path (`C:\Users\...\workspace\notes.txt`,
  possibly with a space, e.g. `C:\Users\John Smith\AppData\Local\Temp\...`)
  produces the same single-quote-wrap behavior it produced here for a
  space-containing POSIX path. `shlex.quote`'s "unsafe character" set
  (`[^\w@%+=:,./-]`) does **not** include `\w`-excluded characters as safe, and a
  backslash is not in the safe set, so any Windows path is guaranteed to be
  wrapped in single quotes by `shlex.quote` regardless of platform — this is a
  property of the `shlex` module's own regex, not something that behaves
  differently under CPython on Windows vs. Linux, but it was not executed on an
  actual Windows interpreter as part of this run.
- That bash (Git for Windows) on the Windows CI runner treats single-quoted
  text with zero escape processing, preserving embedded backslashes byte for
  byte, the same way `/usr/bin/sh` did here. This is standard, documented POSIX
  shell behavior (single quotes suppress all metacharacter interpretation
  except the closing quote itself) and the same mechanism `_find_posix_shell()`
  in `scripts/checklist_engine.py` already routes every `command` check
  through on Windows — but it was reasoned from that code and from POSIX shell
  semantics, not observed on a Windows box.
- That this fix is what actually turns the four named Windows CI tests green.
  The mechanism match is exact (portable `command` check replacing a
  POSIX-only builtin, mirroring the shipped and CI-proven `test_checklist_engine.py`
  house pattern) and the local evidence is as complete as a non-Windows host
  allows, but the CI run itself was not observed in this session.

## Stop conditions hit
- none

## Out-of-scope observations
- none

## Workflow Feedback
- **Handoff gaps:** none — the handoff named the two exact line numbers, the
  house pattern to copy with its file/line citation, the quoting hazard, and
  the sweep categories explicitly. Nothing had to be guessed.
- **Context rediscovered:** had to read `scripts/checklist_engine.py`'s
  `_run_check_command`/`_find_posix_shell` (lines 736–800) myself to confirm
  *how* `command` checks are actually executed (`subprocess.run([shell, "-c",
  command], ...)`, `returncode == 0` as the pass criterion, and that a missing
  POSIX shell fails visibly with rc 127 rather than silently degrading to
  `cmd.exe`). The handoff didn't need to carry this — it's one grep away — but
  a one-line pointer to that function would have saved the lookup.
- **Instructions improvised around:** none. The plan's `m3-full-suite-baseline`
  postcondition initially failed on the map-freshness test
  (`test_map_tree_freshness_root_index_matches_a_fresh_build`), a known
  consequence of adding a module-scope symbol (the exact same trap the
  `winfix` round hit and documented). Rebuilt the map
  (`python -m scripts.code_map build --root .`) and re-ran to green — not a
  deviation, just the expected follow-through the prior round's own
  Workflow Feedback should make routine for whoever writes the next handoff
  in this file.
- **What would have made this easier:** nothing structural. One small
  suggestion: since this is now the *second* round in this workstream to hit
  the map-freshness trap from adding a module-scope symbol to a test file, a
  one-line note in the handoff template ("adding a top-level function/class to
  a covered file may require `python -m scripts.code_map build --root .`
  before the full-suite check will pass") would pre-empt the surprise instead
  of each implementer rediscovering it independently.

## Commit
`fd754ed9` on `epic-418/f-424-mcp-door`.

## Return status
`complete`
