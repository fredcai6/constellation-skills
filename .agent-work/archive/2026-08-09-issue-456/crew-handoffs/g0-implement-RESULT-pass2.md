# IMPLEMENTER_RESULT — issue #456, gate g0, pass 2

**Verdict: PARTIAL.** All four module ports are done, committed and green. The
full suite is green at the gate boundary. A **HARD context trip fired at
`advance m8-falsifiable`**, after that item's load-bearing evidence had already
been produced and attested. A `refresh-request` is filed on the plan. Two gates
remain open: `m8` (evidence complete, gate unclosed) and `m9` (closeout —
evidence produced below, artifact written, commit pending pass 3).

Plan: `.agent-work/issue-456/g0-implementer-plan.json`, session
`g0-impl-9febe0be` (same-id idempotent re-claim, no `--force`).

---

## Completed slices

| Item | Title | State |
|---|---|---|
| `m2-cli` | argparse CLI | complete (predecessor's work; only the gate was open) |
| `m3-extract` | port `astx.py` | complete, committed `377ea98` |
| `m4-supplement` | port `supplement.py` | complete, committed `11a2679` |
| `m5-render` | port `render_map.py` + end-to-end `build` | complete, committed `05be7db` |
| `m6-checks` | wire `checks.py`/`checks2.py` | complete, committed `0ec8c55` |
| `m7-gitignore-bundling` | ignore entries + bundling resolution | complete, committed `bf6de01` |
| `m8-falsifiable` | red/green mutation proof | **evidence complete and attested; gate blocked by the trip** |
| `m9-close` | closeout | **evidence produced below; gate not driven** |

## Files changed

Created:
- `scripts/code_map/extract.py` — ported from `astx.py`
- `scripts/code_map/supplement.py` — ported from `supplement.py`
- `scripts/code_map/render.py` — ported from `render_map.py`
- `scripts/code_map/checks.py` — `checks.py` + `checks2.py` folded into one

Modified:
- `tests/test_code_map.py` — two hermetic end-to-end wiring tests added
- `tests/test_install_constellation.py` — `ScriptsPackageBundlingTests`, 4 tests
- `scripts/install_constellation.py` — `NON_INSTALLABLE_PACKAGES` declaration only
- `.gitignore` — two entries

Not ported, per ADDENDUM ruling 1: `render.py`, `render_fn.py`.
Not committed, per the handoff: the `map/` page tree (built and verified, left
uncommitted for `gs`).

## Test mode satisfied

TDD was required for the two behaviors this gate introduces — the discovery
exclusion and the CLI's argument handling. Both were written test-first by the
previous pass, with the reds recorded on the plan. The four ports were
**test-after**, as the handoff allows.

I added two hermetic end-to-end tests at `m5` that the plan did not ask for.
Reason: without them the four ported stages had **no automated check at all**,
only evidence — which is the "shipped-inert" hazard the handoff's own wiring
grep exists to catch. They assert that each stage produces its artifact and
that scratch never reaches the page tree. They deliberately do **not** pin page
content, which would freeze prototype behavior `g2` and `g3` are going to
change.

---

## Evidence

### 1. Load-bearing — the exclusion test red, then green

Mutation confirmed applied, not assumed:

```
$ git diff --unified=0 -- scripts/code_map/discovery.py
@@ -16 +16 @@ from pathlib import Path
-EXCLUDED_PREFIXES = (".agent-work/",)
+EXCLUDED_PREFIXES = ()
```

RED, `-k discovery`:

```
>       self.assertEqual([p for p in corpus if p.startswith(".agent-work/")], [])
E       AssertionError: Lists differ: ['.agent-work/archive/2026-08-02-issue-304[13962 chars].py'] != []
E       First list contains 141 additional elements.
E       First extra element 0:
E       '.agent-work/archive/2026-08-02-issue-304/evidence/g4_assert_closeout.py'

FAILED tests/test_code_map.py::DiscoveryTests::test_discovery_excludes_agent_work
FAILED tests/test_code_map.py::DiscoveryOnThisRepoTests::test_discovery_on_this_repo_excludes_agent_work
2 failed, 3 passed, 9 deselected in 0.54s
```

RED across the whole file — the rule is load-bearing **end to end**, not only
where it is asserted:

```
FAILED tests/test_code_map.py::DiscoveryTests::test_discovery_excludes_agent_work
FAILED tests/test_code_map.py::DiscoveryOnThisRepoTests::test_discovery_on_this_repo_excludes_agent_work
FAILED tests/test_code_map.py::CliDiscoverCommandTests::test_cli_discover_prints_the_mappable_corpus_and_exits_zero
FAILED tests/test_code_map.py::CliBuildCommandTests::test_cli_build_maps_the_corpus_and_not_the_scratch
4 failed, 10 passed, 10 subtests passed in 0.85s
```

**Reconciling the count with ADDENDUM 2.** That addendum says the mutation
turns **3** red and warns that a pass-1 note saying 2 is stale. Both numbers are
selection-dependent, and neither is what I got. What I actually observed:
**2 red under `-k discovery`** (the selection the plan's own check uses) and
**4 red across the whole file**. The extra one over the addendum's 3 is
`test_cli_build_maps_the_corpus_and_not_the_scratch`, which I added at `m5` in
this pass — it did not exist when the addendum was measured. Asserting what I
observed, as instructed.

Revert confirmed against git (`git status --porcelain` on the file: no output),
then GREEN:

```
$ python -m pytest tests/test_code_map.py -k discovery -q --color=no
.....                                                                    [100%]
5 passed, 9 deselected in 0.86s
```

### 2. Full suite green at the gate boundary

```
$ python -m pytest tests/ -q --color=no
1706 passed, 2 skipped, 648 subtests passed in 296.25s (0:04:56)
```

No `FAILED` lines, so the mechanical distribution command has nothing to
partition. **No mutation-floor failures** — the colour root cause described in
the handoff did not recur.

### 3. End-to-end CLI run

```
$ python -m scripts.code_map build --root .
pass1: 112 modules indexed
statements: 89672 over 112 files (0 failures)
entities: 3523 modules: 112 failures: 0
{
 "modules": 112, "entities": 3523, "pages": 3636, "entity_pages": 3523,
 "holes": 2419, "alias_missing": 0, "median_entity_page_lines": 15, ...
}
```

Exit 0. Produced `map/INDEX.md`, `map/ids.jsonl`, 112 module directories and
3,523 entity pages, plus `.code-map/statements.jsonl` and
`.code-map/supplement.json`. `alias_missing: 0` — every supplement entity
joined to a store symbol on (file, line).

`check` also runs and exits 0 (print-only, as required).

### 4. Mappable corpus, re-derived

```
$ python -m scripts.code_map discover --root . | wc -l
112
$ python -m scripts.code_map discover --root . | grep -c "^\.agent-work/"
0
```

**112**, against the baseline's 103. The delta is this run's own additions
(4 new modules) plus commits landing during the run — the count moved
**three times while I worked** (108 → 110 → 112) as each port was committed.
This is exactly why the handoff says assert the rule, not the number.

### 5. Wiring grep — external call sites

Command run over `scripts/code_map/`, `scripts/install_constellation.py`,
`tests/test_code_map.py`, `tests/test_install_constellation.py`, excluding each
symbol's own `def` line. Counting only real call sites (not docstrings,
comments or import lines):

| Symbol | External call sites |
|---|---|
| `discover_corpus` | **9** — `cli.py:76`, `extract.py:750`, `supplement.py:126`, `checks.py:210`, + 5 test sites |
| `build_parser` (code_map) | **7** — `cli.py:120`, + 6 test sites |
| `load_stores` | **1** — `render.py:390` |
| `repo_name` | **1** — `render.py:415` |
| `non_ascii_provenance` | **1** — `checks.py:204` |
| `reconciliation` | **1** — `checks.py:208` |
| `store_only_sites` | **1** — `checks.py:209` |
| `function_local_imports` | **1** — `checks.py:210` |
| `NON_INSTALLABLE_PACKAGES` | **4** — all in `ScriptsPackageBundlingTests` |
| `extract.run` / `supplement.run` / `render.run` / `checks.run` | **1 each** — `cli.py:83,88,93,106` |

**Zero symbols with no external call site.** Note the grep also matches the
installer's own unrelated `build_parser` at `install_constellation.py:1305` —
different symbol, same name; it is not evidence for `code_map`'s.

### 6. Deliverable paths not ignored

```
$ git check-ignore -v scripts/code_map/__init__.py tests/test_code_map.py .gitignore
CHECK_IGNORE_EXIT=1 (1 = none ignored)
```

Exit 1, no output — none are ignored, as the handoff's pre-dispatch check
requires. See the defect note below about the plan's own version of this check.

---

## The bundling question — resolution on the record

**Resolved as option (b): a declared, checked exclusion.**

`scripts/code_map/` is **not installable and is not bundled by any skill.**

The grounded reason: `install_constellation.py` keeps the install destination
flat — `<installed skill>/scripts/<name>` — for every script, regardless of
where the source lives (`:918-925`, and `SCRIPT_SOURCE_SUBDIRS` at `:111-121`
varies only the *source* lookup). `code_map` is a real package whose modules
import each other relatively (`from .discovery import discover_corpus`).
Flattening strips the package those relative imports resolve against, so every
one of them raises **on the installed side**, where no test here would see it.
The tool is run from a checkout instead: `python -m scripts.code_map <stage>`.

`scripts/hooks/` is deliberately **not** in the same position and stays
flattenable: its modules import nothing from each other, so
`SCRIPT_SOURCE_SUBDIRS` continues to handle it. That distinction is what the
declaration encodes — package vs plain source directory — rather than a flat
denylist someone would have to remember to update.

Enforced by `ScriptsPackageBundlingTests` (4 tests):

1. every directory under `scripts/` holding Python modules is declared **either**
   in `NON_INSTALLABLE_PACKAGES` **or** fully in `SCRIPT_SOURCE_SUBDIRS` — so
   the next package fails here, at authoring time, rather than at install time
   in someone else's run;
2. the declaration matches reality: a declared non-installable directory has an
   `__init__.py` and a flattened one does not;
3. no skill bundle names a module inside a non-installable package;
4. the stated alternative actually works — `python -m scripts.code_map --help`
   exits 0 from a checkout, so the declaration is a route, not just a refusal.

**The guard is falsifiable.** Emptying `NON_INSTALLABLE_PACKAGES` turned 3 of
the 4 red (2 with named subtests), restoring it turned them green:

```
SUBFAILED(directory='code_map') ...::test_a_non_installable_package_is_a_package_and_a_flattened_dir_is_not
SUBFAILED(directory='code_map') ...::test_every_scripts_subdirectory_is_declared_one_way_or_the_other
FAILED ...::test_no_skill_bundles_a_module_from_a_non_installable_package
3 failed, 3 passed, 102 deselected, 2 subtests passed in 0.32s
```

---

## Assumptions used

1. **`.gitignore` entries: two per ADDENDUM ruling 3, then three more per
   ADDENDUM 2.** The plan item's imperative still says "three", meaning the
   stores plus a position cache; ADDENDUM 1 cut the position cache (no gate
   produces one) and ADDENDUM 2 added the three run reports. Final state: five
   narrow entries, no blanket rule.
2. **The top index is titled from the git *common* dir's parent, not the root
   directory name.** A worktree directory is named for the branch, so
   `Path(root).name` would have titled the committed map `issue-456 map`. It
   now reads `constellation-skills map` from either checkout. Falls back to the
   directory name if git is unavailable.
3. **Module-level state kept in the ports.** `extract.ROOT`/`TABLES` and
   `render`'s index dicts stay module-level and are reset by `run()` /
   `load_stores()`. Threading a context object through every formatter would
   have been a rewrite, not a port, and `g2`/`g3` are going to move this code.
4. **`checks.py` section (d) dropped, per the plan's own imperative.** It
   spot-checked one hardcoded file of another repo. The docstring says so and
   says where the real rule belongs (`g1`, corpus-wide).
5. **`checks.py` prints a "run build first" line instead of crashing** when
   there is no page tree. This keeps `check` print-only and exit-0 as required,
   rather than raising on a missing directory.

---

## Stop conditions hit

**One: a HARD context trip at `advance m8-falsifiable`.**

```
REFUSED: m8-falsifiable: context at 16% is at/over the hard limit — advancing is
blocked until you request a refresh, so work is handed off at a seam rather than
lost to a runaway.
```

Filed as instructed and did not push through:
`attach m8-falsifiable --type refresh-request --field seam=m8-falsifiable --field why_ref=w-8`
→ `attached e-m8-falsifiable-1`.

**How much real work was left** (the Commander asked for this explicitly):
**very little.** `m8`'s own evidence was already produced and `c1` attested
before the trip — only the gate transition was refused. `m9` is closeout:
full-suite run, wiring grep, corpus re-derivation and this artifact. **All four
are done and pasted above.** What remains for pass 3 is purely engine driving:
`advance m8`, then `attest m9.p1`, `start m9`, `advance m9`, `release`, plus one
commit of this file. Perhaps ten minutes.

**On the reading itself (`tc5`):** 16% does not match my own sense of headroom —
I had done heavy file reading but was not near a limit, and the two heaviest
reads (`astx.py`, `render_map.py`) were long behind me when it fired. Consistent
with the work-area-scoped gauge. I did not push through, and I am not claiming
the reading is wrong; I am reporting the mismatch as the addendum asked.

---

## Defects found in the plan and handoff — not fixed, flagged

### D-a. `m7`'s postcondition check **cannot fail**

The plan's `m7-gitignore-bundling.c2` ends with:

```bash
! git check-ignore -q scripts/code_map/__init__.py tests/test_code_map.py .gitignore
```

`git check-ignore -q` **rejects multiple pathnames**:

```
$ git check-ignore -q scripts/code_map/__init__.py tests/test_code_map.py .gitignore
fatal: --quiet is only valid with a single pathname
raw_exit=128
$ if ! git check-ignore -q ... ; then echo "negated_form=PASSES"; fi
negated_form=PASSES
```

The `!` inverts the 128, so the clause passes **whether or not the deliverables
are ignored**. It would have passed on a tree where all three were ignored.
This gate is precisely the one that cares — "a check that cannot fail is
indistinguishable from one that passed." I produced the real evidence by hand
(section 6: `-v` form, exit 1, no output). **The engine still recorded a pass
for this check; treat that pass as unearned and section 6 as the actual
evidence.** The fix is `git check-ignore -v <paths>` and asserting exit 1.

### D-b. The run reports are neither tracked nor ignored — RULED AND FIXED

> **Update.** `g0-implement-ADDENDUM-2.md` landed while I was writing this and
> ruled exactly this point: add the three reports in the same narrow,
> one-file-per-line style, no blanket `.code-map/` rule. **Applied.**
> `.gitignore` now carries five entries; `git check-ignore -v` confirms all
> three reports resolve, the deliverable paths still exit 1 (not ignored), and
> `.code-map/` no longer shows as untracked. The original finding is kept below
> as written, since it is what prompted the ruling.


`build` writes three report files the two ruled `.gitignore` entries do not
cover:

```
?? .code-map/extract_report.json
?? .code-map/render_report.json
?? .code-map/supplement_report.json
```

They are rebuilt artifacts exactly like the two stores, so they appear as
untracked dirt in `git status` after any build. **I did not add entries for
them** — ADDENDUM ruling 3 fixed the count at two, and expanding a ruled count
is not mine to do. But the ruling's stated reason was that no gate *produces* a
position cache; these three **are** produced, so I read this as an oversight
rather than a decision. Recommend three more narrow entries, or dropping the
report files. **Commander's call.**

### D-c. `m9`'s wiring-grep check under-names the slice

`m9.c3` greps only `discover_corpus\|build_parser`. This slice added nine more
public symbols. The check passes on the two oldest symbols regardless of the
four modules ported in this pass. Section 5 above is the real grep.

---

## Out-of-scope observations (triage candidates)

- **`tc7` (new): the `map/` page tree has one directory per module, flat and
  dotted** (`map/scripts.code_map.render/`). At 112 modules that is fine; the
  prototype's own header notes it was designed against ~1,200. The top index
  groups by package, but the directory listing does not. Not `g0`'s problem —
  noting it for whichever gate owns page-tree layout.
- **Defects left untouched as instructed:** D1 (0-based `q.line`, `g3`), D2
  (truncated `contains` chain — measured at **25** same-position-different-symbol
  collisions in this repo, `g2`), D3/BOM (`g8`). D4's function-local-import
  measurement now reads **13 of 111 files, 33 names, 2 affected calls/reads,
  0.01%** on this repo — far smaller than on f1Brainz, worth knowing before `g2`
  invests in it.
- **`tc6` observed in practice:** I used "mappable corpus" in prose throughout
  and kept `discover_corpus` as the symbol, exactly as ruled.

---

## Map Impact

Reusing the inbound anchor vocabulary (orientation was DEGRADED-NO-MAP, so these
are paths, not anchor ids):

- **Structural:** `scripts/code_map/` now holds seven modules
  (`__init__`, `__main__`, `cli`, `discovery`, `extract`, `supplement`,
  `render`, `checks`) — the first real Python package under `scripts/`, and now
  the *only* one, a distinction the installer encodes explicitly.
- **Capability:** "derive structure from source" and "render an agent-lean page
  tree" are both live and reachable from one command.
- **Constraints/assumptions:** stdlib-only holds (`ast`, `json`, `os`,
  `pathlib`, `hashlib`, `subprocess`, `shutil`, `collections`, `sys`,
  `argparse`, `builtins` — nothing else). No timings in any of the three run
  reports. Nothing committed carries a position: `ids.jsonl` is empty by
  construction and no page filename carries a line number, though page *bodies*
  still carry `path:line, N lines`, which is `g3`'s to change.
- **Decision anchors:** the package-vs-flat-scripts decision
  (`@grade: settled/human`) is untouched and now has a second, mechanical
  consequence on the record — `NON_INSTALLABLE_PACKAGES` — which a future
  reader will meet before they meet the decision.

---

## Workflow Feedback

1. **The handoff's module table and its wiring rule contradicted each other**,
   and the ADDENDUM fixed it. Worth noting the addendum was *enough*: I lost no
   time on it. Ruling-as-addendum, written to the next agent rather than as a
   revised handoff, worked well.
2. **The addendum changed a plan item's imperative but the plan file still says
   the old thing.** `m7`'s stored imperative reads "three narrow entries"
   forever; only the addendum says two. I recorded the divergence in the
   `--why`, but a cold-starting agent drives from `current`, which prints the
   *stale* imperative. If the engine cannot amend an imperative, the addendum
   needs to be named in the item's own text, not only in a side file.
3. **Two of the plan's own postcondition checks are weaker than the work they
   gate** (D-a, D-c). D-a is the serious one: it silently cannot fail.
4. **`--session-id` position is not obvious.** It is a *verb* argument, not a
   global one: `advance <item> --session-id X` works, `--session-id X advance`
   is a parse error, and the global `--file` form trains you to expect the
   opposite. Cost me two failed calls.
5. **`current` does not accept `--session-id` at all** — a third failed call.
6. **The `.agent-work/g0-implement/{context,mechanical}/*.json` step manifests
   appear as untracked files as you drive.** Nothing said whether an implementer
   commits them; the predecessor's Commander did. I committed mine with the
   `m7` commit. Worth one line in the handoff.
