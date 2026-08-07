# REVIEW_RESULT — issue #456, gate `g0`, re-review of the remediation delta

**Verdict: BLOCK**

Registry entry: `constellation/issue-456/g0/reviewer/attempt-2`
Survey (engine-driven, all 11 items visited): `.agent-work/issue-456/g0-rereview/review.json`
Fowler-pass record: `.agent-work/issue-456/g0-rereview/fowler-pass.json`
Delta reviewed: `b14ff3ff~1..HEAD` over `scripts/`, `tests/` — 2 files, +191/-7.

**B1 and B2 are both genuinely closed.** I reproduced every figure in the
handoff's table in my own hands, including both mutation proofs and the full
suite, and found no regression. The delta is correct, the exclusions held, and
the implementer was right to overrule the handoff on `render.py:306`.

One blocker, and it is the thing this re-review existed to look for. The
handoff asked whether there is a **third** sibling of the cannot-fail shape.
There is, and it is the fixed field itself.

---

## B3 — BLOCKER. The B2 fix relocated the tautology instead of removing it, and the delta ships a docstring claiming otherwise

`scripts/code_map/render.py:436`

```python
npages = sum(1 for _ in out.rglob("*.md"))
```

`pages` is now defined as a count of the tree it describes. It is therefore
*tautologically* true of that tree and can reveal nothing about it. B2's
original finding was **"a page is silently lost, and the count that would
reveal it cannot fail."** After the fix the count still cannot fail — it moved
from being tautological with the *writes* to being tautological with the
*tree*. The lost page is still invisible.

**Proved by mutation, not by reading.** Byte-exact-restore harness; every probe
asserted to match exactly once and the mutant read back out of the file before
pytest ran; `render.py` restored to an identical sha256 with 0 `MUTATION PROBE`
strings left.

| mutation | the defective world it creates | result |
|---|---|---|
| **N8** `unlink()` every second entity page immediately after writing it | 25% of the page tree deleted | **GREEN — 17 passed** |
| **N4** never write any module `INDEX.md` | 112 pages gone in the real corpus; the whole navigation layer | **GREEN — 17 passed** |
| **N5** write every entity page flat into `map/` instead of its module dir | the documented layout destroyed | **GREEN — 17 passed** |

```
=== N8-every-second-entity-page-dropped ===
   defect   : half the entity pages deleted after writing
   result   : GREEN  <-- NOTHING NOTICED
   summary  : 17 passed, 12 subtests passed in 1.59s

=== N4-module-index-page-never-written ===
   defect   : is a whole class of page vanishing noticed?
   result   : GREEN  <-- NOTHING NOTICED
   summary  : 17 passed, 13 subtests passed in 1.63s
```

`test_render_report_page_count_equals_the_files_on_disk` stays green through
all three because it computes its expected value with **the same
`rglob("*.md")` expression as the implementation under test**
(`tests/test_code_map.py:142` against `render.py:436`). It is a real regression
guard for the counting *method* — M2 turns it red — and nothing more.

### Why this blocks rather than deferring

Two reasons, and neither requires touching `render.py`.

**1. The delta ships the opposite claim, in the gate whose subject is exactly
this.** `tests/test_code_map.py:127-131`:

> `pages` in the render report has to be a number that can be **WRONG**.
> Counting `write_text()` calls cannot be wrong … The count has to come from
> the tree.

The second sentence is true. The first and third are not: coming from the tree
is what makes it unable to be wrong. Under `CREW_CONTEXT.md`'s *"a check that
cannot fail is indistinguishable from one that passed,"* shipping that
docstring inside `g0` is the finding.

**2. It will misdirect `g1`.** `tc18` (`spine.json:795`) tells `g1` that
`entity_pages` is *"a one-line fix in the same function."* The one-line fix
matching `g0`'s own precedent is to count the tree again — producing a second
tautological field while `g1` records the family as closed. `g1`'s entire
charter is *"a check stage that can fail."*

### The check that CAN fail is already in the artifact, and nobody runs it

Fresh build of this repo at `HEAD`, into a temp tree:

```
{ "modules": 112, "entities": 3536, "pages": 3648, "entity_pages": 3536, ... }

md files on disk            : 3648
module dirs                 : 112
entity pages (non-INDEX .md): 3535
```

`pages - 1 - modules` = **3535**, against `entity_pages` = **3536**. The report
**already contradicts itself by exactly the lost `Verdict` page** — it carries a
falsifiable invariant and asserts nothing about it. That is the constructive
close, and it is one line. The ruling on where it lands is the Commander's.

---

## B1 and B2 — verified closed

### B1 — no rendered page carries a source position

Reproduced over a full rebuild of this repo at `HEAD`, not only the fixture:

```
total .md pages       : 3648
entity pages          : 3535
headers with .py:LINE : 0
headers with file path: 3535
headers with N lines  : 3535
BLUNT position hits   : 3
    tests.test_checklist_engine\INDEX.md:450
    tests.test_checklist_engine\TestGlobToRegex.md:8
    tests.test_code_map\RenderedPageFormatTests.md:26
```

All three blunt hits are one authored docstring copied through by the renderer,
not a position the renderer emitted. (Three, not the two `tc21` claims — see
O3.)

Mutation proof, reproduced:

```
=== M1-B1-defect-restored ===
   applied  : yes (probe matched 1x; mutant verified in file)
   result   : RED
        FAILED tests/test_code_map.py::RenderedPageFormatTests::test_no_rendered_page_carries_a_source_line_number
```

The implementer was **right** to overrule the handoff: `module_index`
(`render.py:317`) emits `f"{ms['file']}, {ms['loc']} lines"` and was already
compliant. `loc()` was the only position emitter, with one call site
(`render.py:273`).

**Blast radius: zero.** Enumerated by command — no reader of the page-header
format anywhere in `scripts/` or `tests/`; `render_report.json` is read by
exactly one test, the new one; `checks.py` reads page *lines* for non-ASCII
characters and never the header.

### B2 — the page count matches the tree

```
=== M2-B2-defect-restored ===
   applied  : yes (probe matched 1x; mutant verified in file)
   result   : RED
        FAILED tests/test_code_map.py::RenderReportTests::test_render_report_page_count_equals_the_files_on_disk
```

`pages` = 3648 against 3648 `.md` on disk. The `Verdict` page is **still lost**
(`map/scripts.run_skill_eval/Verdict.md` holds `# scripts.run_skill_eval:verdict`),
which is the required outcome. Restored: `17 passed, 13 subtests`, `render.py`
byte-identical.

### Full suite at the boundary

`PYTHONIOENCODING` and `FORCE_COLOR` unset, `--color=no`, `python` not `py`,
working tree clean beforehand:

```
1709 passed, 2 skipped, 651 subtests passed in 416.44s (0:06:56)
EXIT=0
```

Exact match to the claim.

### `, N lines` and D1 — intact, and safe for `g3`

`render.py:186` is byte-identical: `head += f", {e['end_line'] - e['line'] + 1} lines"`.
3535 of 3535 headers carry it. Mutation **N2** changed the arithmetic to `+ 7`
and **all 17 tests stayed green** — no new test freezes the value, so `g3` can
change the line base without fighting a `g0` test. `render.py:97` and
`checks.py:98,:138` are untouched.

---

## Constraints

| constraint | verdict | evidence |
|---|---|---|
| Stdlib only | **PASS** | delta adds `json`, `re` to the test file; `render.py` imports unchanged |
| No timings in any run report | **PASS** | report key-set carries no time field |
| Full suite green at the boundary | **PASS** | 1709 / 2 / 0, reproduced |
| No `git add -A`; `map/` untracked | **PASS** | `git ls-tree -r HEAD -- map/` empty; still untracked on disk |
| f1Brainz / superCoolSpaceSim read-only | **PASS** | no write of any kind to either |
| Nothing committed carries a position | **PASS** | renderer complies; `gs-implement` says *"Generate and commit the map tree"*, so the rebuild is obliged |
| No other defect fixes; D1 stays `g3`'s | **PASS** | collision unfixed, no position cache, D1 arithmetic unchanged |

---

## Neighbouring mutations — what noticed and what did not

Nine run, each asserted applied, each restored byte-identical.

**RED:** M1, M2; **N6b** two modules forced into one directory (caught by the
*pre-existing* `CliBuildCommandTests`, not by the new tests); **N7** entity-key
prefix bug so no entity page is ever emitted — caught by
`RenderedPageFormatTests`'s own input precondition *"the tree must contain
entity pages"*. **That precondition genuinely earns its keep.**

**GREEN:** N1, N2 (correctly), N4, N5, N8.

**Inconclusive, recorded as such:** N6 (`d = out / mod.lower()`) applied to the
text but was a behavioural no-op — the fixture's module names are already
lowercase. A mutation that cannot change behaviour is the same shape I was
hunting, so I authored N6b to replace it rather than claim from it.

---

## Observations — not blockers

**O1. The position guard is tied to one spelling.** `tests/test_code_map.py:123`,
`POSITION = re.compile(r"\.py:\d+")`. Mutation **N1** re-emitted the position as
`pkg/thing.py#L12` and all 17 tests stayed green — the regex needs a colon, and
the keeps-the-path test passes on the prefix. The ruling is *"nothing committed
carries a position,"* not *"no colon-form position."* Filed `tc3`.

**O2. The output layout has no guard at all.** `render.py:22-26` documents the
committed contract every consumer navigates by; **N5** destroyed it with all 17
tests green. `g4`'s two-tier index and `gs`'s Map-entry-point instruction both
depend on it. Filed `tc1`.

**O3. A count of the map, written into a file the map maps, falsifies itself.**
`tc21` and `tests/test_code_map.py:180-184` both say a blunt position scan
returns **two** hits. A fresh build returns **three** — the third being that
very docstring, echoed onto `map/tests.test_code_map/RenderedPageFormatTests.md:26`.
The on-disk `map/` returns 3524. Filed `tc4`.

**O4. `tc18` is scoped narrower than the defect it names.** The root is the
`sizes` list, and `sizes` feeds **three** report fields, not one: `entity_pages`,
`median_entity_page_lines`, `largest_5`. `largest_5` can name a key whose page
was overwritten. Filed `tc2`.

**O5. `tc17` names two different findings.** `spine.json:790` is the
`Verdict`/`verdict` collision; `execute.json:223,:244` say the `r6-fowler`
engine defect was *"Refiled as tc17."* `g1`'s residual from both blockers is
routed by that id. Also: `.agent-work/issue-456/triage-candidates/` is **empty**
— every candidate lives in `spine.json`'s array. I nearly concluded none were
filed. Filed `tc5`.

**O6. Heads-up for `gs`, not a defect.** The `map/` tree on disk right now was
built by the pre-fix renderer: **3523 of 3635 pages still carry a `.py:<line>`**
(3524 hits). `gs-implement` obliges a regenerate, so B1 will not ship — but a
`gs` implementer who stages the existing tree instead of rebuilding it commits
3523 positions against a human-confirmed ruling. One explicit line in the `gs`
handoff closes it. Filed `tc6`.

**O7. `_write_calls()` hand-copies the renderer's arithmetic.**
`tests/test_code_map.py:145-151` re-derives `1 + len(modules) + len(entities)`
from `supplement.json`. Correct only while every supplement entity is reachable
through `children`; nothing checks that, so a future extractor change makes the
input precondition overstate silently and the guard stops guarding. It holds
today: `1 + 112 + 3536 = 3649` against 3648 on disk.

---

## Fowler refactoring pass

Rail cleared: `verify_fowler_pass.py` exit 0, 12 of 12 baseline smells visited.

**Flagged (4):** duplicated-code, feature-envy, primitive-obsession,
comments-as-deodorant.
**Overridden (1), with logged standard:** long-method on `render.run()` —
subordinated to `g0-remediate.md`'s no-refactors exclusion plus the
port-baseline argument: restructuring the one function `g1` and `gb` are both
queued to enter would destroy the baseline before either has used it.
**Absent (7).**

The pass earned its place. **comments-as-deodorant is what surfaced B3** — it is
the smell that asks whether prose asserts more than the code delivers, and both
overclaiming docstrings are in the delta. **duplicated-code named the
mechanism**: the test computing its expected value with the same expression as
the implementation. **primitive-obsession explains why B3 was reachable at all**
— no type owns page-name derivation, so there is no single place that could
answer *"how many pages should exist,"* which is why the fix had to fall back to
counting the files it had just written.

---

## What I checked that nobody asked for

- **Whether `tc17`/`tc18` actually exist.** The directory named for triage
  candidates is empty; they are in `spine.json:790,795`, correctly stated with
  Commander rulings. Verified, not assumed — and it produced O5.
- **Whether the new tests could clobber the real `map/`.** `cli.py:47-53`
  resolves `--artifacts` and `--out` against `--root` at parse time, so the
  fixtures are hermetic. Confirmed after my suite run: `map/` still 3635 files.
- **Whether any gate commits the page tree.** `gs-implement` does —
  *"Generate and commit the map tree for this repo … and state which gate owns
  keeping it fresh."* The B1-shaped worry (a confirmed deliverable with no
  owning gate) does not recur here.
- **Every report field, one by one**, against whether it describes the input or
  the tree. `modules`/`entities`/`holes`/`alias_missing` are honest input
  counts. `pages` is B3. `entity_pages`, `median_entity_page_lines` and
  `largest_5` share the `sizes` root (O4).

---

## Workflow Feedback

**1. The `r6-fowler` postcondition is still unsatisfiable on a survey — same
engine gap the attempt-1 reviewer reported, and the recovery text is still
wrong.** `c1` ships as the literal `python scripts/verify_fowler_pass.py
<fowler-pass-record-path>`, which a POSIX shell parses as an input redirection.
`amend` is gated-only and its signature is `--delta/--reason/--authority`, not
the `--op retext-check` form the previous report described. `attest` is refused
for an engine-checked command. `waive --force` remains the only legal route, and
it frames a rail that ran and passed as an accepted risk; I recorded the true
reason in the waive text. I ran the real check twice, with both the repo's copy
and the installed skill's copy, exit 0 each time. The honest fix is for `record`
to accept the record path as an argument.

**2. The handoff was accurate and the three environment traps were all real.**
`python`-not-`py` in particular: it is the one that reads as silently green. I
hit a fourth of the same family and mention it because it bit *me* in this
review — Git Bash rewrites POSIX-looking **arguments** to Windows paths for
native executables, but not paths inside a quoted Python string. My first scan
pointed at `C:\tmp\...` instead of `C:\Users\...\Temp\...`, and `rglob` on a
missing directory returns empty **silently**. It printed `0` for every count.
Only the `assert pages` I had added caught it. That is the shape this issue
exists to remove, and it is one line of defence away in any sweep script.

**3. A byte-exact-restore harness is worth mandating for mutation work here.**
My first harness used `read_text`/`write_text`, which normalised the worktree's
CRLF to LF and left `render.py` "modified" after a clean restore.
`CREW_CONTEXT.md` warns about exactly this and I still walked into it. Holding
the original **bytes** and writing them back is the only restore that verifies.

**4. "Do not raise X, it is filed as tcN" worked well and I want more of it —
with one refinement.** Being told the collision and `entity_pages` were out of
bounds let me spend the whole pass hunting the third instance instead of
re-arguing the first two. The refinement: give the reviewer the tc **statement**,
not just the id. I had to go find `tc18`'s text to discover it was scoped to one
field when the root feeds three, and I only found it after suspecting the
candidates had not been filed at all.

**5. Bash-tool friction, minor.** The worktree-isolation guard refuses compound
commands containing shell variables or redirects, so every engine call had to
carry both absolute paths inline. Not a handoff problem; it shaped how the
evidence commands above are written.
