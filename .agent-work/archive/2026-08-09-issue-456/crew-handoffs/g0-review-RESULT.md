# REVIEW_RESULT — issue #456, gate `g0`

**Verdict: BLOCK**

Registry entry: `constellation/issue-456/g0/reviewer/attempt-1`
Survey (engine-driven, all 12 items visited): `.agent-work/issue-456/g0-review/review.json`
Fowler-pass record: `.agent-work/issue-456/g0-review/fowler-pass.json`
Diff reviewed: `6ae6193..HEAD` over `scripts/`, `tests/`, `.gitignore` — 13 files, +2145/-1.

The gate is close. The package is clean, the discovery layer is right, the
falsifier is genuinely load-bearing, the stdlib constraint holds mechanically,
and every number in the handoff's evidence table reproduced in my hands. Two
findings block, and both are the kind that get more expensive at every gate
downstream rather than cheaper.

---

## Findings

### B1 — BLOCKER. Every rendered page carries a source position, against a human-confirmed ruling with no owning gate

`scripts/code_map/render.py:171-176` (`loc()`) builds the string
`"<file>:<line>, <N> lines"` and puts it in the header of every entity page.
`scripts/code_map/render.py:306` does the same for module indexes.

Measured on a full build of this repo: **3523 of 3635 pages carry a
`.py:<line>` position.** Example, `map/scripts.run_skill_eval/Verdict.md` line 2:

```
function, scripts/run_skill_eval.py:407, 33 lines
```

The confirmed design says this must not happen. From
`.agent-work/issue-456/reference/ISSUE_456.md`, "Rulings that constrain the
build":

> **Nothing committed carries a position.** A page's `path:line, N lines`
> suffix and `ids.jsonl`'s location both move to the rebuildable cache.
> Positions are the churn that poisons every diff.

> **Committed artifact is the rendered page tree** … Statements, supplement,
> and **the position cache** are gitignored and rebuilt.

`DESIGN_SPEC.md:88-89` says the same, and `DESIGN_SPEC.md:227` shows where it
came from: it is the disposition of **SY1, a BLOCKING critic finding**, ruled at
the confirm gate. Its exact words: *"pages are committed WITHOUT the
line-number suffix, which moves to the cache."* The churn it exists to prevent
was measured — a 3-line source edit rewrites ~450 position-bearing lines.

The `g0` handoff carried the constraint verbatim (`g0-implement.md:100`):
*"Nothing committed carries a position. **No page suffixes**, no line numbers in
`ids.jsonl`."* Two of three obligations are honored — `ids.jsonl` is empty (0
bytes) and page **filenames** carry no suffix. The page suffix itself is not.

Why it was missed, on the record: pass 1 assessed the constraint *"trivially
held: nothing position-bearing has been produced yet"*
(`g0-implement-RESULT.md:178`) — written **before** render was ported. Pass 2
narrowed it to `ids.jsonl` alone (`g0-implement-RESULT-pass2.md:396`). Neither
reading survives the ported renderer.

**Why this blocks rather than deferring to `gs`.** It is literally true that
nothing is committed *at g0*, so the constraint holds by timing. But the
artifact does not hold it, and the gate that ships the renderer is this one.
`map/` is committed at `gs`, the last of eleven — discovering it there means
eight gates of downstream work built on a page format that has to change.

**And the destination artifact has been ruled out of existence.** The
Commander's ruling 4 dropped the third `.gitignore` entry on the finding that
*"no gate produces a position cache."* I verified that finding: no gate in the
build queue (`ISSUE_456.md:25-37`) creates a position cache or strips the
suffix. The finding is correct. The conclusion drawn from it — that the ignore
line was stale — is the one reading of two, and the other reading was never put
on the record: **a human-confirmed deliverable lost its owner when the nine
gates were cut.**

**This is not the Commander's to settle and it is not mine.** The ruling carries
`settled/human` provenance (a confirm-gate disposition of a BLOCKING critic
finding), so inherited doctrine says it goes up. It goes back to Tommy as a
straight either/or:

- **(a)** assign the position cache and the suffix removal to a named gate; or
- **(b)** amend the ruling to accept positions inside committed pages, and
  record the churn cost SY1 measured (~450 position-bearing lines rewritten per
  3-line source edit) as accepted.

Either is fine. Neither being chosen is not.

---

### B2 — BLOCKER. A page is silently lost, and the count that would reveal it cannot fail

This is the exact defect family issue #456 exists to remove, shipping inside
`g0`.

`scripts/code_map/render.py:397-419` increments `npages` once per `write_text()`
**call**, not once per distinct output path. So `render_report.json`'s `pages`
field is identical in the healthy world and in a world where pages overwrite
each other. It is a number that cannot go wrong.

It is wrong right now:

| source | page count |
|---|---|
| `render_report.json` `"pages"` | **3636** |
| `.md` files on disk | **3635** |
| this gate's own `checks.py`, "pages scanned:" | **3635** |

Two `g0` artifacts disagree by one, in the same run, and nothing notices.

**The lost page is real.** `scripts/run_skill_eval.py` defines
`class Verdict` (line 178) and `def verdict` (line 407). `render.py:405` names
the output file:

```python
(d / (key.split(":", 1)[1] + ".md")).write_text(...)
```

Both entities therefore target `map/scripts.run_skill_eval/Verdict.md` on a
case-insensitive filesystem — which is this repo's platform **and CI's**
(`windows-latest`). I confirmed which one wins: the file contains the
**function's** page (`# scripts.run_skill_eval:verdict`). The class `Verdict` is
unreachable from the map, while the module `INDEX.md` still links to it.

I checked for a guard and there is none: **no test in `tests/` reads any of the
three run reports**, and no test compares the report's count to the tree.

Two consequences beyond the one lost page:

1. **The map is platform-dependent.** On a case-sensitive filesystem the same
   source renders 3636 pages. That fails the spec's own determinism falsifier,
   *"any non-empty diff on unchanged source."*
2. **`pages` is the wrong shape for the job it was given.** The constraint "the
   run report carries no timings" exists *so a determinism diff can cover the
   report*. A field that counts write calls cannot serve that purpose.

I am not asking for the collision to be fixed in `g0` — renaming is a real
design question (`g2` owns symbol identity). I am asking that the count stop
lying, and that the collision be filed against a named gate with a falsifying
test. `g1` is "a check stage that can fail" and is the natural home; it cannot
write that check if it does not know the case is there.

---

### O1 — Observation. The `check` subcommand has no execution coverage

`tests/test_code_map.py:128` parses `"check"` as a subcommand *name*. Nothing
calls `cli.main(["check", ...])`. All 211 lines of `scripts/code_map/checks.py`
could raise on import or at run time with the suite still green. I ran it by
hand — exit 0, full diagnostics, output below — but that is my hands, not CI.
Filed as `tc5`.

### O2 — Observation. Guard tests are blind below one directory level

`ScriptsPackageBundlingTests._source_dirs`
(`tests/test_install_constellation.py:1535-1539`) uses a non-recursive
`iterdir()` plus a non-recursive `glob("*.py")`. A nested package under
`scripts/`, or a directory whose modules sit one level further down, is
invisible to all four guards. The guards are otherwise correctly enumerated
**from the filesystem**, which is the important half and which they get right.
Secondary: `test_no_skill_bundles_a_module_from_a_non_installable_package`
compares basenames, so a future flat `scripts/render.py` legitimately bundled by
a skill would trip it as a false red. Filed as `tc2`.

### O3 — Observation. Dead state and a wrong cross-reference

`extract.Extractor.__init__` takes `core` and stores `self.core`
(`extract.py:256-262`); nothing reads it and the only construction site
(`extract.py:766`) passes the literal `True`. It is the prototype's slice flag
carried into production.

`scripts/code_map/__init__.py:21` points readers at
`NON_INSTALLABLE_SCRIPT_PACKAGES`; the symbol is `NON_INSTALLABLE_PACKAGES`
(`scripts/install_constellation.py:135`). That comment is the only link between
the package and its install-side declaration, so a reader who greps the name it
gives finds nothing. Filed as `tc3`.

### O4 — Observation. Store filenames are duplicated between code and `.gitignore`

The five artifact names live as module constants (`extract.STATEMENTS_NAME`,
`extract.REPORT_NAME`, `supplement.SUPPLEMENT_NAME`, `supplement.REPORT_NAME`,
`render.REPORT_NAME`) and again as hand-typed literals at `.gitignore:29,30,34,
35,36`. The narrow one-per-line policy is right and I am not arguing against it;
the gap is that nothing ties the lines to the constants, so a renamed store
silently starts being committed. Filed as `tc4`.

### O5 — Observation, out of scope. The `tc8` shape was never fixed at its source

`.agent-work/issue-456/g0-implementer-plan.json:394` and `:415` still carry
`! git check-ignore -q <three pathnames>`. Run bookkeeping, not shipped code, so
out of this review's scope — but the engine recorded `m7` complete on the
strength of it and the record still reads as though the check earned that.
Filed as `tc1`.

---

## Already-ruled list — checked, not re-litigated

| ruling | verdict |
|---|---|
| 1. `NON_INSTALLABLE_PACKAGES` has zero production call sites — accepted as a policy declaration | **Falsifiability claim verified.** Emptying the frozenset turns exactly 3 of the 4 guards red (declared-one-way-or-other, is-a-package, no-skill-bundles), and the 4th (runnable-from-a-checkout) is correctly unaffected. Not inert. No disagreement. |
| 2. Four prototype modules ported, not six | **Confirmed.** `render_map.py` → `render.py` is a real adaptation (403→439 lines); porting `render.py`/`render_fn.py` would have created uncalled symbols. No disagreement. |
| 3. Artifact paths: stores to `.code-map/`, pages to `map/` | **Confirmed and load-bearing.** `render.run` does `shutil.rmtree(out)` at `render.py:393`, so intermediates under `map/` would be destroyed. No disagreement. |
| 4. Two store ignore entries, not three — no gate produces a position cache | **Premise verified, conclusion disputed — see B1.** No gate does produce one. That is the finding, not the resolution: the position cache is a confirmed deliverable that lost its owner. |

---

## Close criteria, one by one

**1. The CLI runs extract → render end to end on this repo and exits 0. — PASS**

```
$ python -m scripts.code_map build --root . --artifacts <tmp>/.code-map --out <tmp>/map
pass1: 112 modules indexed
statements: 89672 over 112 files (0 failures)
entities: 3523 modules: 112 failures: 0
{ "modules": 112, "entities": 3523, "pages": 3636, "entity_pages": 3523,
  "holes": 2419, "alias_missing": 0, "median_entity_page_lines": 15, ... }
EXIT=0   (real 7.4s)
```

Produced `.code-map/statements.jsonl` at 23,916,503 bytes and 3635 `.md` pages.
Built into a temp tree deliberately, so the real `map/` staged at `gs` was not
disturbed. (The `pages: 3636` in that output is B2.)

**2. Discovery enumerates exactly the mappable corpus with `.agent-work/`
excluded. — PASS**

112 files / 3523 entities against the 103-file baseline; the +9 are this gate's
own new `.py` files. There is exactly **one** enumerator and every stage goes
through it: `discovery.discover_corpus` (`discovery.py:33`) is the only caller
of `tracked_python_files`, which holds the only `git ls-files` invocation in the
package. `extract.run:750`, `supplement.run:126` and `checks.run:210` each call
it; `render` derives its module list entirely from the two stores
(`render.py:84-88`) and never touches the filesystem, so it cannot introduce a
second path. The prototype's two independent enumerations (three hardcoded
`INDEX_DIRS` for pass 1, a handwritten `slice_manifest.json` for pass 2) were
both collapsed into this single call — confirmed by normalized diff.

**3. A test fails if the exclusion is removed. — PASS, and it is genuinely
load-bearing**

Mutation asserted applied (`EXCLUDED_PREFIXES = ()`), not assumed:

```
FAILED tests/test_code_map.py::DiscoveryTests::test_discovery_excludes_agent_work
FAILED tests/test_code_map.py::DiscoveryOnThisRepoTests::test_discovery_on_this_repo_excludes_agent_work
FAILED tests/test_code_map.py::CliDiscoverCommandTests::test_cli_discover_prints_the_mappable_corpus_and_exits_zero
FAILED tests/test_code_map.py::CliBuildCommandTests::test_cli_build_maps_the_corpus_and_not_the_scratch
4 failed, 10 passed, 10 subtests passed in 0.91s
```

Restored → `14 passed, 10 subtests passed`, working tree clean.

The fourth failure is the one that matters: `test_cli_build_maps_the_corpus_and_
not_the_scratch` reds on the **rendered page tree**, not merely on the corpus
listing, so the exclusion is proven to hold through the whole pipeline. Both
exclusion tests also assert their input precondition — that scratch was actually
present to filter — so neither can pass vacuously.

**4. The bundling question is resolved on the record. — PASS**

Option (b), and then some: `NON_INSTALLABLE_PACKAGES`
(`install_constellation.py:135`) with a 16-line rationale naming the flat
install destination as the mechanism, plus four guards. Falsifiability verified
above.

**5. The full suite is green at the gate boundary. — PASS**

`PYTHONIOENCODING` cleared, `--color=no`:

```
1706 passed, 2 skipped, 648 subtests passed in 335.56s (0:05:35)
EXIT=0
```

Exact match to the claim, against the 1688 baseline.

I also independently checked the `tc3` fix in the condition that broke it —
`FORCE_COLOR=3` exported, `tests/test_mutation_floor.py` → `14 passed, 11
subtests passed` (183s). It holds.

---

## Constraints, one by one

| constraint | verdict | evidence |
|---|---|---|
| **Stdlib only** | **PASS** | AST-walked every `Import`/`ImportFrom` in all 8 modules. Absolute: `argparse, ast, builtins, collections, hashlib, json, os, pathlib, shutil, subprocess, sys`. Relative: `.cli, .discovery, .extract, .supplement`, `from . import`. Zero third-party. |
| **Nothing committed carries a position** | **FAIL** | B1. |
| **Run report carries no timings** | **PASS** | All three report key-sets checked. The prototype's `pass1_sec`/`pass2_sec` were deliberately removed in the port — visible in the normalized `astx.py` → `extract.py` diff. |
| **`.gitignore` narrow, one file per line** | **PASS** | Five entries at `:29,30,34,35,36`. Each verified by its **own single-pathname** `git check-ignore -v` call — never a multi-pathname call, per the `tc8` lesson. Each of the four deliverable paths verified NOT ignored by its own single-pathname call (exit 1). No blanket `.code-map/` rule. |
| **No defect fixes, no schema changes** | **PASS** | D1 and D2 are documented at `render.py:12-20` and worked around (`+1` at `render.py:97`), not fixed. `checks.py` is a port; its docstring records that `g1` rewrites it. |
| **f1Brainz / superCoolSpaceSim read-only** | **PASS** | I performed no write of any kind to either. |

Scope: 13 files, all inside the allowed scope or authorized.
`tests/test_mutation_floor.py` is outside `g0`'s allowed scope but was authored
by the **Commander** (commit `0223be79`) as the `tc3` fix and surfaced to the
human; sanity-checked above and correct. `map/` is not tracked
(`git ls-tree -r HEAD -- map/` empty) and untracked on disk — the `d236f22e`
sweep and its immediate reversal are correct history, not a defect.

---

## Fowler refactoring pass

Rail cleared: `verify_fowler_pass.py` exit 0, 12 of 12 baseline smells visited.

**Overridden (3)** — all citing the same documented standard, `g0-implement.md`
Specific Exclusion *"Do not rewrite the checks. That is `g1`"* plus
`global-crew.md`'s minimal-change rule: **long-method** (`supplement.run` 86
lines, `render.load_stores` 70, `extract.resolve_attr` 63), **large-class**
(`Extractor`, 467 lines / 26 methods), **feature-envy** (`checks.py` reaching
through raw supplement structure). Logged reason in each case: the bodies are a
*verified* faithful port — the normalized `astx.py` → `extract.py` diff is 144
lines and every one is docstring rewording, `ROOT` parameterisation, or the
timings removal — so restructuring them now would destroy the only baseline a
later gate has to diff against.

**Flagged (6):** duplicated-code (the D1 `+1` written out three times at
`render.py:97`, `checks.py:98`, `checks.py:138`), data-clumps
(`root, artifacts, out` travelling as a trio, with `cli.py:38-39`'s two
membership sets as the clump made visible), primitive-obsession,
shotgun-surgery, speculative-generality, comments-as-deodorant.

**Absent (3):** long-parameter-list (widest signature is 3), divergent-change,
message-chains.

The pass earned its place twice. **primitive-obsession is the mechanism behind
B2** — the supplement key is a bare `"module:Qualified.Name"` string that five
call sites re-parse by hand, and `render.py:405` turns its raw tail straight
into a filename with no collision check and no case check. A key type owning its
own page-name derivation would have had exactly one place to put that check.
And **speculative-generality found the dead `self.core`** that three implementer
passes and the Commander's re-verification all walked past.

---

## What I checked that nobody asked for

- **The `check-ignore` shape does not survive into shipped code.** Grepped
  `check-ignore` across `scripts/` and `tests/`: zero hits. It exists only in
  `.agent-work/` job files (`O5`). Clean.
- **Case-collision sweep of the whole page tree**, not just the one instance —
  exactly one collision (`Verdict`/`verdict`), no duplicate keys, no module
  directory collisions, no reserved or invalid filename characters.
- **Prototype-drift read by normalized diff** (BOM- and CRLF-stripped, per
  `CREW_CONTEXT.md`'s "never compare raw working-tree bytes" rule). The
  extractor's resolution logic is carried across untouched.
- **Ran the `check` subcommand** — exit 0, and it is the artifact that
  contradicts the render report (`O1`, `B2`).

---

## Out-of-scope observations → triage candidates

`tc1` the `tc8` shape uncorrected in the job file · `tc2` guard tests blind
below one directory level · `tc3` dead `self.core` + wrong cross-reference ·
`tc4` store filenames duplicated between code and `.gitignore` · `tc5` no
execution coverage for `check`.

---

## Workflow Feedback

**1. `r6-fowler`'s postcondition cannot be satisfied on a survey — an engine
rail defect.** `SKILL.md` says *"fill this item's postcondition command with the
real record path you wrote it to."* No engine verb can do that on a `survey`
controller. `amend --op retext-check` is refused (*"amend applies to gated
checklists"*) and `attest` is refused (*"c1 is engine-checked"*). The template
ships `c1` with a literal `<fowler-pass-record-path>` placeholder, which under a
POSIX shell parses as an input redirection and fails regardless. The only route
left was `waive --force`, which frames a rail that **actually ran and passed**
as an accepted risk. I recorded the true reason in the waive text so the record
is not misleading, but the honest fix is either to let `retext-check` work on
surveys or to have `record` accept the record path as an argument.

**2. The handoff's evidence table said "3,635 pages"; the report says 3636.**
That one-off is not a transcription slip — it is B2, and it was sitting in plain
sight in the handoff. Worth noting that the discrepancy between a claim and its
own cited artifact was the thread that unravelled the finding. It is a good
argument for the evidence table quoting artifact fields verbatim rather than
prose counts.

**3. The already-ruled list worked exactly as intended.** Being told to *verify
the falsifiability claim, do not re-argue the ruling* on
`NON_INSTALLABLE_PACKAGES` saved a round trip and still produced real evidence.
More of this. The one refinement: ruling 4's stated premise ("no gate produces a
position cache") was checkable and turned out to be the finding. Where a ruling
rests on a premise, giving the reviewer the premise — as this handoff did — is
what made B1 findable.

**4. The two environment traps were accurate and saved real time.** Both
`FORCE_COLOR=3` and `PYTHONIOENCODING` behaved exactly as described. No
complaint — this is the handoff field working.

**5. Bash-tool friction, minor.** The worktree-isolation guard in this harness
refuses compound commands containing redirects, so several verification runs had
to be split into separate calls. Not a handoff problem; noting it because it
shaped how the evidence commands are written above.
