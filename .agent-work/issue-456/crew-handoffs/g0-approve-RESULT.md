VERDICT: APPROVE

# REVIEW_RESULT — issue #456, gate `g0`, closing pass

Third and final review pass at `g0`. Scope: the never-reviewed B3 fix (commit
`853be2bc`, a docstring at `tests/test_code_map.py:127`), a mutation attack on
every check `g0` ships using probes their authors did not choose, the suite
numbers, and whether the bundling question is resolved rather than deferred.

`g0` closes. B3's fix is honest clause by clause, every claim in it that can be
measured I measured, and no fourth cannot-fail sibling exists. The one thing I
found that its authors did not choose to test (`A5`) is a mutation of the field
already documented as tautological, so it creates no new false confidence. It is
logged as an out-of-scope candidate, not a blocker.

---

## 1. Suite numbers, in a cleared environment

`PYTHONIOENCODING` and `FORCE_COLOR` cleared in-process, `--color=no`,
`python` not `py`, working tree clean beforehand:

```
python -m pytest tests -q --color=no
1709 passed, 2 skipped, 651 subtests passed in 420.02s (0:07:00)
EXIT=0
```

**1709 passed, 2 skipped, 0 failed** — exact match to the expected figure.

```
python -m pytest tests/test_code_map.py -k "discovery or cli" -q --color=no
14 passed, 3 deselected, 10 subtests passed in 1.59s
```

**14 passed** — exact match.

All three environment traps were real. `FORCE_COLOR=3` is exported in this
shell. `python` resolves to 3.14.3 with pytest; `py` does not. Every mutation
run below cleared both variables inside the harness rather than trusting the
shell.

---

## 2. The B3 docstring, clause by clause

`tests/test_code_map.py:127-150`. Judged against the four questions in the
handoff. **No sentence in it is false.**

| # | clause | verdict | how I know |
|---|---|---|---|
| 1 | *"Guards the **method** `pages` is counted by, and nothing more."* | **true**, with one measured caveat | `A1` and `A4` both RED — method regressions are caught. `A5` shows not *every* method change is caught (below). "and nothing more" is a limiting clause and is correct. |
| 2 | *"Counting `write_text()` calls reports what the renderer TRIED to do … restore the per-write counter and it goes red."* | **true, verified** | `A1`, below: RED, `AssertionError: 5 != 4`. |
| 3 | *"the replacement is a count of the tree it describes … it cannot detect anything ABOUT the tree either"* | **true, verified** | `A2`, `A3`, `A6` all GREEN. |
| 4 | the three named mutations leave it GREEN | **true — all three verified in my hands** | `A3`, `A2`, `A6`, below. |
| 5 | *"It computes its expected value with the same `rglob("*.md")` expression as `render.run`, so it can only ever agree with it."* | **true** | `tests/test_code_map.py:160` against `scripts/code_map/render.py:436`. Structurally identical, and `render.run` writes no further `.md` after computing it. |
| 6 | *"`pages` does not detect a lost page. Do not read a green here as evidence that the page tree is complete."* | **true**, and it is the sentence that closes B3 | The real repo has a genuinely lost page and `pages` = 3648 = files on disk. |
| 7 | *"`pages - 1 - modules` against `entity_pages` differ by exactly the pages lost to filename collisions"* | **true, verified arithmetically** | Fresh build of this repo at HEAD into a temp tree: `pages` 3648, `modules` 112, `entity_pages` 3536. `3648 - 1 - 112 = 3535` against `3536`. Difference 1. `map/scripts.run_skill_eval/Verdict.md` holds `# scripts.run_skill_eval:verdict` — the class page is the lost one. |
| 8 | *"nothing asserts it"* | **true** | `grep -rn "entity_pages" tests/` returns only the docstring itself. No test reads that field. |
| 9 | *"Asserting it belongs to `g1` … `tc17` … it would be red on arrival here, because `g2` owns the rename … See `tc24`"* | **true against the record** | `spine.json:790` (`tc17`), `:795` (`tc18`), `:825` (`tc24`). Consistent with this handoff's own exclusions. |

Answering the handoff's four questions directly:

1. **Does it correctly say the test guards the counting method and is a real
   regression guard?** Yes, and it is — proved twice, by the author's probe
   (`A1`) and by one they did not choose (`A4`).
2. **Does it correctly say the count cannot detect a lost page, and not imply
   otherwise anywhere?** Yes. I read every sentence looking for an implication
   to the contrary and there is none. The bolded sentence states it flatly and
   pre-empts the misreading.
3. **Does it point the next reader at where the check that can fail lives?**
   Yes — the invariant is written out, assigned to `g1`, tied to `tc17`, and
   `tc24`'s correction ("counting the tree again is NOT the fix") is named so
   the next implementer does not repeat `g0`'s move.
4. **Is any sentence false?** No.

It replaces a claim that was false with a measurement that is true, and it
carries the reason. That is the fix B3 asked for.

---

## 3. Mutations — every one asserted applied, every one restored byte-exact

Harness held each target's original **bytes** (not text — this worktree is
CRLF), normalised probe newlines to the target's, required each probe to match
exactly once, read the mutant back out of the file before pytest ran, restored
from the held bytes, and ran `git status --porcelain -- scripts/ tests/` after
every single mutation.

### The three GREEN claims the docstring makes — all three run, all three GREEN

| id | mutation | defective world | result |
|---|---|---|---|
| `A3` | `unlink()` every second entity page immediately after writing it | half the entity pages deleted | **GREEN — 17 passed, 12 subtests** |
| `A2` | never write any module `INDEX.md` | 112 pages in the real corpus; the whole navigation layer | **GREEN — 17 passed, 13 subtests** |
| `A6` | write every entity page flat into `map/` instead of its module dir | the documented layout destroyed | **GREEN — 17 passed, 13 subtests** |

The docstring's measurement is accurate. It did not overstate and it did not
understate.

### The RED claim

| id | mutation | result |
|---|---|---|
| `A1` | `npages = 1 + len(MODULES) + len(sizes)` — the removed per-write count, restored | **RED** — `FAILED …RenderReportTests::test_render_report_page_count_equals_the_files_on_disk`, `AssertionError: 5 != 4` |

### Mutations their authors did NOT choose — the standing lesson of this gate

| id | check attacked | mutation nobody chose | result | what it proves |
|---|---|---|---|---|
| `A4` | `RenderReportTests` | `npages = sum(1 for _ in out.rglob("*"))` — count every entry, not only pages | **RED**, `7 != 4` | The method guard has teeth beyond the probe it was built against. It is a real regression guard, not a mirror. |
| `A5` | `RenderReportTests` | `npages = sum(1 for _p in out.rglob("*.md") if _p.stat().st_size > 0)` — a genuinely different counting method that drops emptied pages | **GREEN** | See "the one hole" below. |
| `B1` | `DiscoveryTests::test_discovery_predicate_and_listing_agree` | weaken `is_mappable` while keeping `discover_corpus`'s *behaviour* byte-identical (two-site edit) | **RED** | That test is NOT the B3 shape. It really does catch the predicate and the listing drifting apart, with observable behaviour held constant. |
| `B2` | the `.agent-work/` exclusion | `EXCLUDED_PREFIXES = (".agent-work/issue-1/",)` — exclude a *subdirectory* of the scratch instead of the scratch | **RED — 4 failed** | The exclusion is load-bearing under a mutation nobody designed for it, not only under the author's `()`. The fourth failure, `CliBuildCommandTests::test_cli_build_maps_the_corpus_and_not_the_scratch`, reds on the rendered page tree, so the exclusion is proven through the whole pipeline. |
| `C1` | the four bundling guards | **over**-declare: `frozenset({"code_map", "hooks"})` | **RED — 3 failed** | Every prior falsifiability check on this declaration was *under*-declaration (emptying the frozenset). It bites in the opposite direction too: `test_a_non_installable_package_is_a_package_and_a_flattened_dir_is_not` and `test_no_skill_bundles_a_module_from_a_non_installable_package` both red. |
| `C2` | `test_the_declared_package_is_runnable_from_a_checkout` | `from .cli import main` → `from cli import main` in `__main__.py` — exactly what flat bundling produces | **RED**, `ModuleNotFoundError: No module named 'cli'` | The guard catches the precise failure mode the bundling ruling exists to prevent, not merely "the package imports". |
| `D1` | the position guard | re-emit the position as `pkg/thing.py (line 12)` | **GREEN** | Confirms `tc3` (already filed by the re-reviewer, who found it with `#L12`) with a second spelling. Known, filed, not new. |

### The one hole, and why it is not a fourth blocker

`A5` changes the counting method to skip zero-byte pages and nothing notices.
So clause 1's "guards the *method*" is broader than what is proven: it guards
*some* method regressions, decisively including the one that mattered.

This is **not** a fourth cannot-fail sibling, for a reason that decides it:
the field it weakens is the field the docstring already tells the reader not to
trust. A new cannot-fail check is dangerous because it manufactures confidence.
This one manufactures none — the docstring's own bolded sentence forbids the
reader from drawing any conclusion about tree completeness from a green here.
The remedy is the invariant assertion, which is already assigned to `g1` with
`tc17`/`tc24` and which this handoff explicitly forbids me from adding.

Logged as **`tc26`** below.

---

## 4. The bundling question — RESOLVED on the record, not deferred

It is a resolution, and it is option (b), the stronger of the two the gate
offered. Three places carry it.

**The declaration and its rationale**, `scripts/install_constellation.py:123-137`:

> NON-INSTALLABLE PACKAGES: directories under `scripts/` that are real Python
> packages — they carry an `__init__.py` and their modules import each other with
> intra-package relative imports (`from .discovery import ...`). Because the
> install destination is FLAT (above), copying such a package's modules out
> strips the package that those relative imports resolve against, and every one
> of them raises at import. **So these are not bundled at all: they are run from a
> checkout as `python -m scripts.<package>`, and no skill declares them.**
> …
> `tests/test_install_constellation.py` holds every directory under `scripts/` to
> one of these two declarations, **so a new package cannot arrive undeclared.**
>
> `NON_INSTALLABLE_PACKAGES: frozenset[str] = frozenset({"code_map"})`

**The written resolution**, `crew-handoffs/g0-implement-RESULT-pass2.md:200-204`:

> ## The bundling question — resolution on the record
> **Resolved as option (b): a declared, checked exclusion.**
> `scripts/code_map/` is **not installable and is not bundled by any skill.**

**The enforcement**: four tests in `ScriptsPackageBundlingTests`
(`tests/test_install_constellation.py:1529-1590`), which I attacked from two
directions the gate had not tried — over-declaration (`C1`, RED) and the actual
flat-bundling import breakage (`C2`, RED).

This is a decision with a stated reason, a mechanism, and falsifiable
enforcement — not a deferral wearing a resolution's clothes. Nothing about it
is postponed to a later gate.

---

## 5. Restoration

`git status --porcelain -- scripts/ tests/ .gitignore` → **empty**, verified
after every mutation and again at the end. `git diff --cached` → empty; nothing
staged. `git ls-tree -r HEAD -- map/` → empty; `map/` is still untracked, as
`gs` requires. I never ran `git add`, and I performed no write of any kind to
`C:/Programs/f1Brainz` or `C:/Programs/superCoolSpaceSim`.

**One restoration defect of my own, disclosed.** My first harness stored the
"original" bytes per *edit* rather than per *file*, so on the one two-site
mutation (`B1`) the second edit captured the already-mutated bytes and the
restore left `scripts/code_map/discovery.py` half-mutated. Everything that ran
after it in that batch (`B2`, `A6`, `D1`) inherited the corruption and I
discarded those three results. I restored from git, fixed the harness to hold
the first reading of each file, added a `git status` check to every mutation,
and re-ran all four. The results reported above are from the clean re-run.
`A1`–`A5` ran before `B1` and were never contaminated. This is the same family
as the re-reviewer's byte-exact-restore lesson and it argues for the same
conclusion more strongly: **the restore is not verified until git says so**, not
when the harness says it wrote the bytes back.

---

## 6. Out-of-scope candidates

- **`tc26` — the pages count has one more unguarded method mutation.** Skipping
  zero-byte pages in `render.py:436` leaves all 17 tests green. Belongs with
  `g1`'s invariant work (`tc17`/`tc24`), which subsumes it: an assertion of
  `pages - 1 - modules == entity_pages` would red on it. Not fixable here — this
  handoff forbids both the invariant and a `render.py` change.
- **`tc4` re-measured and still wrong.** `tests/test_code_map.py:198-201` states
  a blunt position scan of the real page tree "still reports **two** hits". A
  fresh build at HEAD reports **three**: `tests.test_checklist_engine/INDEX.md:450`,
  `tests.test_checklist_engine/TestGlobToRegex.md:8`, and
  `tests.test_code_map/RenderedPageFormatTests.md:26` — that docstring's own
  text, echoed back onto the map it describes. Already filed by the re-reviewer
  as `tc4`. Not a blocker: it misstates a measurement, not a check's coverage,
  and no check's ability to fail depends on it. But it is a false sentence in a
  `g0`-shipped docstring, and it will keep going stale because a count of the map
  written into the map is self-falsifying. Recommend `g1` replace the number
  with the rule.
- **`tc27` — the `g0-close` handoff's return artifact was never written.**
  `crew-handoffs/g0-close.md` requires `IMPLEMENTER_RESULT` at
  `g0-close-RESULT.md`; that file does not exist. The Commander made the change
  directly (disclosed, with the registry defect that forced it, as `tc25`) and
  put the substance — old claim, new claim, reasoning, suite number — in the
  commit message of `853be2bc`. The content requirement is met; the artifact
  requirement is not. Noting it so the `g0` evidence chain is not read as
  complete-by-artifact when it is complete-by-commit-message.
- **`tc28` — the engine advanced past `g0-review` before this verdict existed.**
  `execute.json.journal` seq 24 records `advance` on `g0-review` and seq 25
  `attest` on `g0-integrate`, both at `2026-08-08T00:06`, roughly eight minutes
  before this closing handoff was written. Had my verdict been BLOCK, the record
  would already have moved past the gate that the block applies to. The verdict
  precedes the advance in doctrine; here it did not in the journal.
- **Stale artifacts on disk, for `gs`.** `.code-map/render_report.json` still
  reads `"pages": 3636` and the on-disk `map/` is the pre-fix tree carrying
  positions. Both are gitignored or untracked and `gs-implement` obliges a
  rebuild, so nothing ships — this is the already-filed `tc6`, re-confirmed.

---

## 7. What I checked that nobody asked for

- **Whether the invariant the docstring points at is actually true today**, by
  building this repo fresh into a temp tree rather than trusting the stale
  on-disk report. It is: 3648 / 112 / 3536, differing by exactly one, and the
  one is `Verdict`. The stale `.code-map/render_report.json` in the worktree
  reads 3636 / 3523 / 3523 — those agree only because they are both the pre-fix
  renderer's output, and a reviewer who read that file instead of rebuilding
  would have concluded the invariant already holds.
- **Whether `test_discovery_predicate_and_listing_agree` is the same shape as
  B3** — it computes its expected value from `is_mappable`, which is also what
  the implementation calls. It is not: `B1` holds `discover_corpus`'s observable
  behaviour constant and it still reds. That was my strongest fourth-sibling
  candidate and it survived.
- **Whether the bundling guards fail in both directions**, not only the one the
  implementer tested. They do (`C1`).
- **Whether `test_the_declared_package_is_runnable_from_a_checkout` proves
  anything beyond "argparse exits 0"**. It does — `C2` breaks exactly one
  relative import in the way flattening would and the guard reds.

---

## 8. Workflow Feedback

1. **"Attack it with a mutation its author did not choose" is the single most
   productive line in any handoff I have been given here.** It is what produced
   `A4`, `B1`, `C1` and `C2`, none of which any prior pass ran, and it is what
   let me distinguish a *documented* tautology (`pages`, fine) from an
   *undetected* one (none found). Recommend it becomes standing reviewer
   doctrine for this issue's remaining gates, not a per-handoff reminder.
2. **The handoff's "explicitly NOT yours" list did real work again.** Being told
   the invariant would be RED today and belongs to `g1` meant I could verify the
   docstring's pointer without being tempted to implement it. The refinement the
   re-reviewer asked for — give the `tc` statement, not just the id — was applied
   here for `tc17`/`tc18`/`tc24` and it saved a lookup.
3. **The three environment traps were accurate, and a fourth belongs in the
   list: a mutation harness must verify its restore with `git status`, not with
   its own bookkeeping.** My per-edit-instead-of-per-file bug produced a harness
   that reported "restored: byte-identical" while the file was half-mutated,
   because it was comparing the bytes it had just written against themselves.
   Three subsequent mutation results were silently wrong and read as coherent
   failures. That is precisely the shape issue #456 exists to remove — a check
   that reports success by construction — appearing inside the review of that
   very defect class. One line of `git status` per mutation catches it.
4. **The `python`-not-`py` trap:** confirmed real. `py` is not on this box's
   pytest path at all.
5. **Bash-tool friction, unchanged.** The worktree-isolation guard refuses any
   compound command with a redirect, a pipe into a variable, or an `env -u`
   wrapper, so the full suite had to run through PowerShell and every mutation
   through a Python driver that cleared the environment in-process. Not a
   handoff problem; it is why the harness exists in the shape it does.
