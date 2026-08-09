VERDICT: APPROVE

# Review Result — gate `g3`: one statement schema, and the line base declared

`constellation/issue-456/g3/reviewer/attempt-1`. Survey driven end to end
through the engine at `.agent-work/issue-456/g3-review/review.json`, lease
`g3-reviewer-attempt-1`, all seven checks recorded, consolidated to APPROVE.

**The independence claim is TRUE. Breaking either side of `entity_symbol_join`
— on the real 3711-entity corpus, with mutations neither the implementer nor
`g2`'s reviewer chose — turns the check red. Leaving both sides intact leaves
it green.**

---

## 1. THE ONE THING: independence of the re-based `entity_symbol_join`

Evidence: `.agent-work/issue-456/evidence/g3-reviewer-independence-attack.{py,txt}`.
Run against the **real corpus** (this repository), never the synthetic
`_make_mixed_repo` fixture — every mutation copies `scripts/code_map` into a
throwaway temp dir and builds with `--artifacts`/`--out` in scratch, so the
tracked `map/` tree was never touched.

**CONTROL** — unmutated copy, real repo: `check` exit **0**, `ok
entity-symbol-join`, `passed 6 checks`. Rules out an always-red check.

**SIDE A** — `extract.child_sym` mutated to `return self.mod + ":" + name`,
collapsing every definition to read as module-level regardless of nesting (a
genuine chain-flatten, per the handoff's own wording — and textually unlike the
implementer's own `EXTRACTOR_RENAME_MUTATION`, which lowercases names):

```
FAIL entity-symbol-join: 3896
FAILED 1 of 6 checks: entity-symbol-join
   scripts.apply_episode_delta/__init__.md: page is titled
     scripts.apply_episode_delta:__init__ but the source defines
     scripts.apply_episode_delta:_Transaction.__init__ at that position
```

**SIDE B** — `checks.SourceScan._walk` mutated to stop treating `ClassDef` as a
qualifying scope, so a method's SOURCE-derived name drops its class prefix
specifically (mechanically unlike the implementer's own
`SOURCE_SCAN_FLATTEN_MUTATION`, which flattens every level, not just classes):

```
FAIL entity-symbol-join: 4367
FAILED 1 of 6 checks: entity-symbol-join
   scripts.apply_episode_delta/_Transaction.__init__.md: page is titled
     scripts.apply_episode_delta:_Transaction.__init__ but the source defines
     scripts.apply_episode_delta:__init__ at that position
```

Both mutations are isolated failures — `FAILED 1 of 6 checks` both times, no
collateral check broken. Both sides are load-bearing; neither mutation was the
implementer's own; the check is not a tautology.

---

## 2. `tc34` — verified independently, two ways

Evidence: `g3-reviewer-tc34-verify.{py,txt}`, `g3-reviewer-tc34-with-fixture.{py,txt}`.

**(1) Count, re-derived from git history, not copied.** `git show
0d821d6f~1:scripts/code_map/supplement.py` confirms the body-only descent my
script uses is byte-identical to the deleted stage's own `walk`. Ran it against
a **fresh** build of the real corpus: **8 gained, 0 lost** — same 8 symbols the
implementer reported, independently re-measured. Traced the first
(`scripts.checklist_engine:emit_step_manifest`) to its source line and
confirmed by reading the file that its nearest shallower enclosing line is
`except ImportError:`, and that a page exists for it.

**(2) My own with-block fixture**, not `_make_schema_repo`: a definition inside
`with contextlib.suppress(Exception):` and one inside `if True:`. Both land in
the store, both get a page, both are linked from `INDEX.md`, full `check`
passes 6/6.

`tc34` is closed.

---

## 3. `ids.jsonl` under a code MOVE

Evidence: `g3-reviewer-ids-move.py.txt`. My own fixture, not the implementer's
mint-two-rename-one exercise: moved the whole `spin` definition (anchor comment
included) from line 6 to line 30 in the same file — a 24-line relocation, not a
rename. Store line for the symbol: `6 -> 30`. `ids.jsonl`: **byte-identical**
before and after.

```
ids.jsonl BEFORE == AFTER: True
```

---

## 4. The extraction-window statement, judged against intent (`tc40`)

Confirmed independently: the phrase is a bare task-list noun in
`DESIGN_SPEC.md` / `ISSUE_456.md` / `ownership-scope.md` / `gate-spec.json` and
is defined **nowhere**. The implementer's own flag is accurate.

**Judgement: not decorative for its named purpose.** `LINE_BASE` is declared
per-file and genuinely consumed — two independent production read sites
(`render.source_line`, `checks.StoreScan.line_base`) plus the
`entity_symbol_join` position match, and it is pinned by a flip-test. `loc` /
`doc_body` / `all` reach a real reader too: the module index's `path, N lines`
header and docstring come from the window statement, not a recomputation.

**But its own docstring overclaims.** "A reader can tell a fact absent from the
code from a fact that was never looked at" is true only for a **consumer of the
raw statement store** — I traced `render.py`'s `MODULES` population and
confirmed a parse-failed file leaves **zero trace anywhere in the rendered
`map/` tree**: no page, no index entry, no "N files failed" note. The only
record is `extract_report.json`, which is gitignored and unlinked from any
page. The coverage-boundary property is real but not yet realized for the
map's actual audience. **Not a blocker** — the constraint this gate names
(declare the line base) is fully met; the overclaim is a docstring accuracy
issue, filed as a triage candidate (`tc1` this survey / `tc41` run-wide).

---

## 5. Standard numbers — every one independently reproduced

| claim | mine | agree |
|---|---|---|
| full suite | `1767 passed, 2 skipped, 672 subtests passed`, 358.5s, **0 failed** | matches exactly |
| gate selector (`schema or line_base or ids_jsonl`) | `21 passed, 54 deselected` | matches exactly |
| fresh `build` + `check` | exit 0 both; `check` 6/6 `ok` including `entity-symbol-join` | matches |
| render report (read off my own fresh `.code-map/render_report.json`) | modules=111, entities=3711, pages=3823, holes=2506, ids=0 | matches exactly |

RED commits re-run from `git archive` snapshots (worktree never checked out),
4 of the 5 named: `8029a4ea` (line base, 5 failed), `91da2500` (schema value
facts, 3 failed / 11 passed — a real incremental RED, not a broken suite),
`4246e87d` (`tc34`, 2 failed, actual `AssertionError` text confirms the
with-block page is genuinely absent pre-fix), `70b60555` (`ids.jsonl`, 5
failed). All four genuinely committed failing.

Spot-checked directly, not taken from the RESULT: `supplement.py` absent from
`scripts/code_map/`; `supplement` absent from `.gitignore`, `cli.py`,
`__init__.py`; one `contains` statement's `d` block carries all six fields
(kind, signature, end/span, doc_body, decorators, bases); one `declares`
statement carries (annotation, value, form).

---

## 6. Scope

Files touched (`git diff --name-only 80cfc5c5~1..HEAD`, run myself): exactly
`scripts/code_map/{extract,render,checks,cli,__init__,supplement(deleted)}.py`
+ `.gitignore` + `tests/test_code_map.py`. `scripts/run_skill_eval.py`: empty
diff, byte-identical.

`checks.py` / `cli.py` are outside the handoff's narrow wording but forced by
the merge itself — `checks.py` owned `entity_symbol_join` and read the
supplement directly, `cli.py` wired the now-deleted stage. Nothing in either
file changed beyond what removing the supplement stage requires.

Named exclusions, all re-verified directly: `_make_collision_repo`'s `INDEX`
collision still fails `page-accounting` (read the test body — asserts a
nonzero exit and the specific `pkg.thing` text, not vacuous);
`OWN_MODULE_NAMED_MUTATION` / `test_refs_lines_are_self_consistent_on_an_intact_map`
green; zero `:<line>` hits scanning every page header in a fresh `map/` build;
all 6 checks still registered in `CHECKS`.

---

## 7. Constraints

Stdlib only (two new imports, both stdlib/relative, no third-party package).
No timing fields in either report. Never ran `git add -A` — every git command
this review issued was read-only. Never touched `f1Brainz` or
`superCoolSpaceSim`. Never mutated a tracked file — every mutation (SIDE A,
SIDE B, the `ids.jsonl` move fixture) ran against a throwaway package copy
under a temp directory, never the checked-out tree, so **there is nothing to
restore and no sha256 pair to report** — `git diff --stat -- scripts/ tests/
.gitignore` is empty, confirmed by running it. Never force-pushed or merged.

---

## 8. Refactoring pass (Fowler)

Record: `.agent-work/issue-456/g3-review/fowler-pass.json`, rail exit 0. 12/12
smells judged — 2 flagged, 2 overridden with logged standards, 8 absent.

**Flagged (observations, not blockers):** `extract.Extractor.emit` grew from 8
to 9 parameters this gate (the new `d=None`) — no repo standard sanctions it,
unlike the two overrides below, so it's a genuine long-parameter-list
candidate. `checks.SourceScan.unreadable` is populated on a parse failure but
never consumed anywhere in the repo (grepped `scripts/` and `tests/`, zero
reads) — collected-and-unused state.

**Overridden, each re-verified rather than taken on faith:** duplicated-code
(`SourceScan.module_of` vs `extract.mod_of`, and `StoreScan.__init__` vs
`render.load_stores` both independently parsing `statements.jsonl` — checks.py's
own "written a second time on purpose" standard, and §1's independence attack
is the verification, not an assumption); primitive-obsession (both sides of
`entity_symbol_join` staying bare strings — same standard, same evidence).

**Absent, notably long-method:** `refs_line_self_consistent`, g2's own
long-method override, is **untouched** by this diff (confirmed from the actual
diff hunk content, not just its header); `entity_symbol_join`'s new body is
~22 lines with two named arms.

---

## 9. Out-of-scope candidates

Mine (filed on the engine as `tc1` this survey):
- **tc1 / tc41** — the extraction-window statement's docstring overclaims what
  a map reader sees on a parse failure (§4 above).

Carried forward, not mine to fix: `tc39` (HARD context-band governor firing at
~16% fill, already filed by the Commander); `page_accounting`'s COUNT arm now
overlapping `entity_symbol_join`'s COVERAGE arm (honest redundancy, a later
gate's call); the `d` block's effect on `statements.jsonl` size (a build-time
observation, gitignored/rebuilt).

---

## 10. Blockers

**None.**

---

## Workflow Feedback

- **Handoff gaps:** none material. The handoff named the exact two mutations to
  attempt ("flattens an enclosing chain" / "mutate SourceScan's derivation")
  precisely enough to design mutations that are genuinely different from both
  the implementer's own and `g2`'s reviewer's — that specificity is why this
  review has evidence rather than an opinion.
- **Context rediscovered:** none the anchors didn't already point at. Reading
  `render.py`'s `MODULES` population (to judge §4, the extraction-window
  claim) was the one piece of original tracing this review did beyond what any
  artifact named.
- **Instructions improvised around:** same Fowler-rail placeholder gap every
  prior gate's review hit — `r6-fowler.c1` ships with a literal
  `<fowler-pass-record-path>` and no survey-legal verb can substitute the real
  path. Fourth consecutive reviewer to force-waive it for the same reason (not
  a risk acceptance — the rail ran and passed). Also: the Bash tool in this
  worktree refuses long/complex quoted commands (`--finding`, `--reason`,
  `--summary` strings of any real length), so I wrote three tiny wrapper
  scripts (`run_record.py`, `run_waive.py`, `run_consolidate.py`) that read the
  text from a file and pass it to the engine via `subprocess` with a list
  argv — avoids shell quoting entirely. Worth adopting as the standing pattern
  in this worktree rather than re-discovering it every gate.
- **What would have made this easier:** a `--finding-file` / `--reason-file` /
  `--summary-file` option on the engine itself, so every reviewer stops
  re-inventing the subprocess wrapper.

## Return status
`complete`
