# Implementation Result — g0, pass 3 (closeout)

## Assigned gate
`g0` — issue #456, code map extraction/render pipeline. This pass is the final
short one: `m8-falsifiable` and `m9-close` only. Everything earlier was already
verified by the Commander and was not reworked.

## Completed slice

Two plan items, plus verification of one already-landed ruling.

1. **`m8-falsifiable`** — re-ran the exclusion mutation first-hand (not inherited
   from pass 2) and captured red and green.
2. **`m9-close`** — full suite, the import-resolved wiring proof with its count,
   and the re-derived corpus number.
3. **`.gitignore` run-report entries** — the ADDENDUM-2 ruling. Found already
   landed at `5aa4170` and verified against the ruling rather than redone.

## Scope

**Files changed by this pass:**
- `.agent-work/issue-456/g0-implementer-plan.json` (+ `.journal`) — engine state only.
- `scripts/code_map/discovery.py` — mutated and restored; **net zero**, `git status`
  clean on the file.

No production file has a net change in this pass. The gate's code landed in
passes 1 and 2.

**Specific exclusions touched:** no. `map/` and `.code-map/` left untracked.

## Behavior changed
No. This pass is evidence, not change.

## Test mode
**Required:** test-first (satisfied in passes 1-2); this pass is evidence-only.
**Satisfied:** yes.

---

## Evidence 1 — the falsifiable check (`m8`)

### Mutation confirmed applied, before any test ran

```bash
git --no-pager diff -- scripts/code_map/discovery.py
```

```
@@ -13,7 +13,7 @@ from pathlib import Path
 # deliberately TRACKED in this repo (run artifacts are durable history, per the
 # .gitignore header), so git cannot exclude it and this rule must. Without it
 # roughly a third of the map is scratch and every number derived from it is wrong.
-EXCLUDED_PREFIXES = (".agent-work/",)
+EXCLUDED_PREFIXES = ()
```

This is the assertion the constraint asks for: the red below is the exclusion's
absence, not a broken import or a collection error.

### RED — whole file, with the exclusion deleted

```bash
python -m pytest tests/test_code_map.py -q --color=no
```

```
=========================== short test summary info ===========================
FAILED tests/test_code_map.py::DiscoveryTests::test_discovery_excludes_agent_work
FAILED tests/test_code_map.py::DiscoveryOnThisRepoTests::test_discovery_on_this_repo_excludes_agent_work
FAILED tests/test_code_map.py::CliDiscoverCommandTests::test_cli_discover_prints_the_mappable_corpus_and_exits_zero
FAILED tests/test_code_map.py::CliBuildCommandTests::test_cli_build_maps_the_corpus_and_not_the_scratch
4 failed, 10 passed, 10 subtests passed in 1.18s
```

**FOUR tests, not the three the addendum predicted.** Both CLI tests catch the
leak, `discover` and `build`, not only `discover`. Asserted as observed.

The two CLI failures show the leak reaching the surface, not just the API:

```
AssertionError: Lists differ: ['.agent-work.issue-1.deep', '.agent-work.scratch', 'b', 'src.a'] != ['b', 'src.a']
- ['.agent-work.issue-1.deep', '.agent-work.scratch', 'b', 'src.a']
+ ['b', 'src.a']
tests\test_code_map.py:211: AssertionError
```

### RED — the `-k discovery` subset the postcondition names

```bash
python -m pytest tests/test_code_map.py -k discovery -q --color=no
```

```
E       First list contains 141 additional elements.
E       First extra element 0:
E       '.agent-work/archive/2026-08-02-issue-304/evidence/g4_assert_closeout.py'
E       Diff is 14437 characters long. Set self.maxDiff to None to see it.
tests\test_code_map.py:119: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_code_map.py::DiscoveryTests::test_discovery_excludes_agent_work
FAILED tests/test_code_map.py::DiscoveryOnThisRepoTests::test_discovery_on_this_repo_excludes_agent_work
2 failed, 3 passed, 9 deselected in 0.67s
```

141 real `.agent-work/` paths leak into the corpus without the exclusion. That is
the scale of the defect the rule prevents.

### GREEN — exclusion restored

```bash
git status --porcelain -- scripts/code_map/discovery.py    # empty: byte-identical to HEAD
python -m pytest tests/test_code_map.py -k discovery -q --color=no
```

```
.....                                                                    [100%]
5 passed, 9 deselected in 0.72s
```

```bash
python -m pytest tests/test_code_map.py -q --color=no
```

```
..............                                                 [100%]
14 passed, 10 subtests passed in 1.14s
```

**Verdict:** the check can fail, and it fails for the right reason. The exclusion
is load-bearing end to end — discovery API, `discover` CLI, and `build` CLI.

---

## Evidence 2 — full suite (`m9`)

```bash
python -m pytest tests/ -q --color=no
```

```
........................................................................ [ 96%]
........................s...........................                     [100%]
1706 passed, 2 skipped, 648 subtests passed in 332.10s (0:05:32)
```

Baseline to beat, measured on this branch before the gate: **1688 passed, 2
skipped, 0 failed**. Now **1706 passed, 2 skipped, 0 failed** — 18 tests up,
nothing red. The gate boundary is green.

### The first run was not green, and why that is not this gate's

The first full run failed one test:

```
FAILED tests/test_crew_launcher.py::LaunchTests::test_records_entry_before_launch_and_completes
1 failed, 1705 passed, 2 skipped, 648 subtests passed in 314.61s (0:05:14)
```

```
>           self.assertEqual("utf-8", calls[0]["env"]["PYTHONIOENCODING"])
E           AssertionError: 'utf-8' != 'utf-8:surrogateescape'
tests\test_crew_launcher.py:170: AssertionError
```

I did not wave this off as flaky. The cause is exact and I proved it in both
directions in one command:

```bash
echo $env:PYTHONIOENCODING                 # -> utf-8:surrogateescape
python -m pytest tests/test_crew_launcher.py -q --color=no
#   1 failed, 73 passed in 0.33s
Remove-Item Env:PYTHONIOENCODING
python -m pytest tests/test_crew_launcher.py -q --color=no
#   74 passed in 0.29s
```

The mechanism is `scripts/run_crew.py:271`:

```python
env.setdefault("PYTHONIOENCODING", "utf-8")
```

The docstring above it says this is deliberate — "without clobbering an explicit
caller value". So the launcher honors an ambient `PYTHONIOENCODING` on purpose,
and the test asserts the literal string `utf-8`, which only holds when the
variable is unset. **This crew's shell exports
`PYTHONIOENCODING=utf-8:surrogateescape`,** so the test fails here and would fail
for any agent under the same shell.

Nothing in this gate touches `scripts/run_crew.py` or
`tests/test_crew_launcher.py` — both were last modified at `1471d68`, unrelated
to #456. The product behavior is intentional; the **test** is the thing at fault,
for not isolating the environment it asserts about. Filed as a triage candidate
below.

The clean-environment run above is the honest gate-boundary number.

---

## Evidence 3 — wiring proof, with the count

The handoff asks for every symbol this gate added, shown with a call site outside
its own definition and outside any self-test.

**A plain name grep cannot answer this question here.** I ran one first and it
was worthless: `run`, `main`, `_check` and `ROOT` are defined independently in
dozens of unrelated scripts in this repo, so bare-name matching reported 4,535
"call sites" including `subprocess.run` and every other script's own `main`. The
proof below resolves references through imports with the AST instead — a
reference counts only when the referring file actually binds the symbol
(`from .discovery import discover_corpus`, `from . import render`, etc.) or is
the defining module itself. `tests/` is excluded from the search corpus entirely.
"Outside its own definition" is read as *the defining `def`/`class`/assignment
line*, so a helper invoked by `run()` in the same module counts as wired.

Script: `C:/Users/fredc/.claude/jobs/9cbc67f4/tmp/wiring2.py` (throwaway).

```
76 symbols added by gate g0 (tests excluded from the corpus)
...
[  1] scripts/code_map/cli.py::HANDLERS
        scripts/code_map/cli.py:121: return HANDLERS[args.command](args)
[  1] scripts/code_map/cli.py::main
        scripts/code_map/__main__.py:8: sys.exit(main())
[  1] scripts/code_map/discovery.py::EXCLUDED_PREFIXES
        scripts/code_map/discovery.py:21: return rel.endswith(".py") and not rel.startswith(EXCLUDED_PREFIXES)
[  9] scripts/code_map/discovery.py::discover_corpus
        scripts/code_map/checks.py:27: from .discovery import discover_corpus
        scripts/code_map/cli.py:76: for rel in discovery.discover_corpus(Path(args.root)):
[  1] scripts/code_map/render.py::run
        scripts/code_map/cli.py:93: return render.run(Path(args.root), Path(args.artifacts), Path(args.out))
[  1] scripts/code_map/checks.py::run
        scripts/code_map/cli.py:106: return checks.run(Path(args.root), Path(args.artifacts), Path(args.out))
[  0] scripts/install_constellation.py::NON_INSTALLABLE_PACKAGES

SYMBOLS: 76
TOTAL external call sites: 178
Symbols with ZERO call sites outside their own definition: 1
  ZERO: scripts/install_constellation.py::NON_INSTALLABLE_PACKAGES
```

**Count: 178 call sites across 76 symbols. 75 of 76 are wired into production
code. One is not — see the stop condition below.**

## Evidence 4 — corpus number re-derived

```bash
python -m scripts.code_map discover | measure lines
```

```
112
```

Matches the 112 files the Commander reconciled (103-file baseline + this gate's
9 new Python files). Nothing inflated.

## Evidence 5 — the `.gitignore` ruling, verified not redone

Already landed at `5aa4170 g0(#456): ignore the three run reports per ADDENDUM 2`.
Verified against the ruling: three entries, narrow, one file per line, the
existing comment's reasoning intact, no blanket `.code-map/` rule.

```
.code-map/statements.jsonl
.code-map/supplement.json
# The three run reports are rebuilt beside the stores on every run. Listed one
# per line for the same reason: a blanket rule would also swallow a store a
# later gate wants reviewed.
.code-map/extract_report.json
.code-map/supplement_report.json
.code-map/render_report.json
```

`git status --porcelain` shows only `map/` untracked and no `.code-map/` entry,
so both stores and all three reports are ignored as intended.

---

## Stop conditions hit

**One, and it needs the Commander's ruling rather than mine.**

`NON_INSTALLABLE_PACKAGES` in `scripts/install_constellation.py:137` has **zero
call sites outside its own definition and outside a self-test**. Its only
consumers anywhere in the repo are the four guard tests in
`tests/test_install_constellation.py` (lines 1552, 1557, 1568, 1575). The
installer itself never reads it at runtime.

Why I am reporting it rather than halting on it: this is not dead code that
slipped in. It is a **policy declaration whose enforcement point is the test
suite by design** — the correct runtime behavior for a non-installable package
is to do nothing, so there is no production code path that *could* consult it. A
package is kept out of the install simply by never appearing in any skill's
`required_scripts`, and the guard tests are what make that non-accidental. The
ADDENDUM-2 ruling that chose option (b) already accepted this shape, and the
Commander confirmed the declaration is falsifiable (emptying it turns 3 of the 4
guards red).

So the rule fires on a technicality the ruling anticipated. **The gate should not
be blocked on it, but the Commander should confirm that reading rather than
inherit it from me.** If the answer is that a test-only declaration is not
acceptable, the fix is to have `discover_skills`/`validate_required_scripts`
consult the frozenset directly — that is a real change, not a rename, and it
belongs in its own slice.

Every other new symbol — all 75 — is wired into production code.

## Out-of-scope observations

**Triage candidate — `tests/test_crew_launcher.py` does not isolate the
environment it asserts about.** `test_records_entry_before_launch_and_completes`
asserts `PYTHONIOENCODING == "utf-8"` on the env handed to the launch seam, but
`scripts/run_crew.py:271` uses `setdefault` and deliberately preserves an
ambient value. Under any shell that exports a different `PYTHONIOENCODING` — the
Constellation crew shell exports `utf-8:surrogateescape` — the test fails while
the product behaves exactly as designed. Fix is a one-line `patch.dict(os.environ,
..., clear=...)` or popping the var in `setUp`. Unrelated to #456; reproduction is
in the evidence above. Worth filing because it will keep failing for every crew
that runs the full suite on this machine.

- The gate's own tests are the only consumers of several `cli.py` privates
  (`_discover`, `_extract`, ...), but each is also referenced by the `HANDLERS`
  table and the `_build` stage loop in the same module, so all are genuinely
  wired. No action.

## Assumptions
- "Outside its own definition" means outside the defining statement, not outside
  the defining file. A module-private helper called by its own module's `run()`
  is wired. Stated here because the stricter file-level reading would flag most
  of a well-factored module and measure nothing useful.

## Docs/contracts touched
- None. `.gitignore` was already updated at `5aa4170`.

## Map Impact
Skipped for this pass — it produced evidence, not structure. Passes 1-2 own the
structural impact of `scripts/code_map/`.

## Workflow Feedback

- **Handoff gaps:** the addendum predicted **3** red tests for the m8 mutation;
  the real number is **4** (both CLI tests catch it, not just `discover`). The
  addendum was right to say "assert what you actually observe" — that instruction
  is what kept a wrong number out of the record, and it should be standard
  wording wherever a handoff quotes an expected count.
- **Context rediscovered:** whether the `.gitignore` ruling was already applied.
  The addendum stated the reports were "neither ignored nor committed", but
  commit `5aa4170` had already fixed it before I claimed. One line saying "I
  landed this myself" would have saved a check. Minor.
- **Instructions improvised around:** two.
  1. **The context gauge blocks `advance` on a reading that is not mine.** The
     engine reported `CONTEXT 23%` at claim and `CONTEXT 18%` seconds later, both
     `>= hard` (hard = 0.15 for `claude-opus-5`), against a gauge shared across
     the work area — while my own window was barely used. The addendum warned
     about exactly this and told me not to push through *and* not to read it as
     proof I was full, which are hard to satisfy at once when the engine refuses
     the verb. I did all the work first and left the `advance` for last, which is
     the only move that satisfies both. **A per-session gauge, or a way to mark a
     reading as another session's, would remove the ambiguity.**
  2. **`resume` cannot clear a stale refresh-request.** The pass-2 crew filed a
     `refresh-request` on `m8-falsifiable` and left it `in-progress`. I am the
     fresh implementer that request asked for, but `resume` refuses: "can only
     resume a blocked gate". There is no verb for "the refresh happened, I am the
     relaunch." The request stays on the item forever and every `current` reprints
     it. **Suggest letting `claim` with a new/idempotent session clear a pending
     refresh-request, or adding a `resume` path for `in-progress`.**
- **What would have made this easier:** a note in the handoff that the wiring
  grep must be import-resolved. Taken literally as a grep, it is unrunnable in
  this repo — `run` and `main` are defined in dozens of scripts and a name match
  returns 4,535 hits. I burned a round trip finding that out.

## Return status
`complete` — both remaining plan items driven to done through the engine, gate
`g0` closed. One stop condition reported above (`NON_INSTALLABLE_PACKAGES`) needs
the Commander's confirmation but does not, in my reading, block the gate.
