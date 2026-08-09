# Implementer Handoff

## Gate
`g0` — Package, CLI and discovery: the prototype behind a real entrypoint.
First gate of eleven (`g0 g1 g2 g3 g4 g5 gb g6 g7 g8 gs`). Issue #456.

## Task

Stand up `scripts/code_map/` as this repo's **first Python package under
`scripts/`** and move the reference prototype behind a real `argparse` CLI.
Add a discovery layer that enumerates the mappable corpus and **excludes
`.agent-work/`**. Add narrow `.gitignore` entries for the rebuilt artifacts.
Resolve the bundling question on the record.

The prototype is **six modules**, read-only, at
`.agent-work/issue-456/reference/prototype/`:

| File | Size | Role |
|---|---|---|
| `astx.py` | 32.5 KB | two-pass AST extractor with its own cross-file name resolution |
| `supplement.py` | 8.3 KB | second-pass enrichment (a stage `g3` will REMOVE — port it, do not improve it) |
| `render_map.py` | 14.3 KB | page-tree renderer |
| `render.py` | 18.1 KB | render helpers; recovered from `evidence/x11` |
| `render_fn.py` | 9.3 KB | function-page renderer; imports `render as R` |
| `checks.py` + `checks2.py` | 5.5 + 2.8 KB | the print-only diagnostics |

The import graph closes: `render_fn.py` imports `render as R`, and `render.py`
is present.

**Port `checks.py`/`checks2.py` only as far as keeping the CLI wired.** They are
print-only — no assertions, no exit code. `g1` REWRITES them. Do not start that
rewrite here.

## Protected Intent

An agent can run one command against this repo and get a derived code map, with
the corpus it mapped being exactly the real source — not the run scratch. If
`.agent-work/` leaks into the corpus, ~35% of the map is scratch and every
downstream number in this run is wrong.

## Test Mode

**Test-after allowed** for the port itself (mechanical relocation of ~90 KB of
working code); **TDD required** for the two behaviors this gate actually
introduces — the discovery layer's exclusion rule, and the CLI's argument
handling. Write those two tests first and watch them fail.

## Close Criteria

- The CLI runs **extract → render end to end on this repo** and exits 0.
- The discovery layer enumerates **exactly the mappable corpus** with
  `.agent-work/` excluded.
- **A test fails if the exclusion is removed.** This is the load-bearing one:
  delete the exclusion, watch the test go red, put it back. Show both states in
  your evidence.
- The bundling question is **resolved on the record**, not deferred (see
  Constraints).
- The **full suite is green** at this gate boundary.

**Do not claim "no behavior change."** It is unfalsifiable here: the prototype
hardcodes `ROOT` to an external repo (`f1Brainz`) and has no `argparse`
anywhere, so there is no prior behavior to diff against. Say what you verified
instead.

**The corpus numbers are a measurement, not a target.** The baseline at
`.agent-work/issue-456/reference/corpus_baseline.txt` recorded **103 mappable
files / 3,411 entities / 52,292 source lines** at the time it was probed. Assert
the **exclusion rule**, not the literal 103 — this run adds files to the repo, so
a pinned count is a trap that goes red for the wrong reason. Re-derive the
number at authoring time and record what you got.

## Allowed Scope

- `scripts/code_map/**` — the new package (create).
- `tests/test_code_map.py` — the suite CI runs (create).
- `.gitignore` — narrow entries only (see Constraints).
- `scripts/install_constellation.py` and `tests/test_install_constellation.py` —
  **only** if resolving the bundling question requires a declaration or check
  there. Touch nothing else in them.

## Specific Exclusions

- **No defect fixes.** D1 (line base) is `g3`, D2 (symbol identity) is `g2`, D3
  (wrapped docstring) and BOM handling are `g8`. If you see them, leave them and
  note them in your return.
- **No schema changes.** The statement-line schema merge is `g3`.
- **Do not rewrite the checks.** That is `g1`.
- **Do not commit a `map/` page tree.** The tree is staged at `gs`, deliberately
  last, so six intermediate gate diffs stay reviewable. Build it, verify it,
  leave it uncommitted.
- `scripts/build_architecture_map.py` — the incumbent packet compiler. Untouched,
  no integration, no overlap. It never parses source.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
  Do not write to them.

## Constraints

- **Stdlib only.** CI installs pytest and coverage and nothing else, so a
  third-party import means the tool cannot run at all. Hard and mechanical.
- **Nothing committed carries a position.** No page suffixes, no line numbers in
  `ids.jsonl`. Positions are the churn that poisons every diff.
- **The run report carries no timings**, so a determinism diff can cover it.
- **`.gitignore` entries must be narrow and explicit** — one each for the
  statement store, the supplement, and the position cache. `.agent-work/` is
  **deliberately tracked** in this repo (run artifacts are durable history, per
  the `.gitignore` header), so a blanket scratch rule is wrong here.
- **Resolve the bundling question explicitly.** Grounded fact, verified at
  `scripts/install_constellation.py:111-129` and `:919-925`: source may live in
  a subdirectory of `scripts/`, but the install **destination stays flat** —
  `<installed skill>/scripts/<name>`. A multi-module package with intra-package
  imports therefore **cannot survive bundling as-is**. Pick one and record it:
  (a) state on the record that no skill bundles `code_map`, or (b) add a check
  that a package under `scripts/` is declared installable or explicitly
  excluded. Deferring is not an option — this gate closes on it.

## Map Anchors (inbound)

Orientation for this run was **DEGRADED-NO-MAP**: this repo has no
`docs/architecture` packets, so anchors below are **paths, not anchor ids**. No
anchor id exists to cite; citing one would be inventing it.

- **Structural:** `scripts/code_map/` (new package, first under `scripts/`) ·
  `.gitignore` · `scripts/install_constellation.py` (flat install destination)
- **Capability:** derive structure from source · render an agent-lean page tree
- **Constraints/assumptions:** stdlib-only · nothing committed carries a
  position · the run report carries no timings
- **Decision anchors:** package layout vs the 42 flat `scripts/*.py` — the
  package wins; `scripts/hooks/` is the directory precedent.
  `@grade: settled/human · leans g0-implement,g0-review · ` — **ruled by Tommy.
  Not yours to unsettle.** If you meet reality contradicting it, stop and return
  rather than reverting to flat scripts.
- **Evidence expectations:** the mappable-corpus baseline at
  `.agent-work/issue-456/reference/corpus_baseline.txt`
- **Map confidence flags:** `install_constellation.py` flattens the destination —
  a package cannot survive bundling as-is. **This is the real hazard**; an
  earlier version of this flag pointed at a test helper that can never fire.

## Deliverable Path Check

Run before dispatch: `git check-ignore -v scripts/code_map/__init__.py
tests/test_code_map.py tests/fixtures/x .gitignore` → **exit 1, no output**
(none are ignored). All four are **Committed** paths.

`map/` — build it to prove the pipeline runs end to end, but **leave it
uncommitted this gate**; it is staged at `gs`.

These are **new** files: they are untracked until staged, so `git diff` will not
show them. They appear in `git status`. A "diff touches exactly N files" claim
that ignores this reads as false against a correct tree.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. The exclusion test **red with the exclusion removed, green with it in
   place**. Paste both runs. This is the one criterion a reviewer will
   reproduce first.
2. The full suite green: `python -m pytest tests/ -q --color=no`, with the
   count.
3. The end-to-end CLI run: exact command, exit code, and what it produced.

**Confirmatory — a spot-check suffices:** the corpus count you re-derived; the
`.gitignore` entries; the bundling resolution as a written statement.

**Baseline you are starting from — read this before you diagnose anything.**
The suite was **10 failed / 1678 passed** on this branch until a few minutes
ago, and **all 10 were in `tests/test_mutation_floor.py`**. That was
**environmental, not a regression**: this shell exports `FORCE_COLOR=3`, the
harness spawned an inner pytest that inherited it, and an ANSI colour code
landed between `FAILED` and the node id, so the harness's regex matched nothing
and every killed mutant reported as `HARNESS ERROR`. Proven by running the same
tree with the variable removed: **14 passed**. It is **already fixed** on this
branch (`run_floor` now passes `--color=no` and drops `FORCE_COLOR`), verified
green with `FORCE_COLOR=3` still set. **If you see mutation-floor failures,
that regex is the first thing to check — do not go looking for a code-map
cause.** Any failure outside that root cause is a stop condition.

Derive any failure distribution mechanically, never from the output tail:
`python -m pytest tests/ -q --color=no | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`
(the `--color=no` matters — without it the grep silently finds nothing, which
is the same defect described above).

## Wiring Grep

Required. One command naming every symbol this slice adds, each shown with a
call site **outside its own definition** and outside any `--self-test` path:

```bash
grep -rn "discover_corpus\|build_parser\|main" --include=*.py scripts/code_map/ tests/test_code_map.py | grep -v "def discover_corpus" | grep -v "def build_parser" | grep -v "def main"
```

Substitute the real symbol names you added. **State the count of external call
sites.** Zero external call sites for any new symbol is a **stop condition**, not
a note — a symbol referenced only by its own definition and its own self-test is
shipped-inert: it passes review, passes tests, and no caller ever reaches it.
Grep for the *caller*, because grep for the *name* is satisfied by the module's
own self-test.

## Verification Commands

```bash
python -m pytest tests/ -q --color=no
python -m pytest tests/test_code_map.py -k 'discovery or cli' -q --color=no
```

## Suggested Model Tier

**Stronger.** Scope is wide (six modules, ~90 KB ported), the package layout is
a durable structural choice, and the bundling question needs a judgment call
against the installer's real behavior.

## Authority

Already decided — **not yours to reopen**:

- The tool lands at `scripts/code_map/` as a **package**. Ruled by Tommy.
- All eleven gates ship this run. Ruled by Tommy.
- Local commits are allowed. **Push and a full non-draft PR are pre-approved**
  for this work. **Merge to `main` is NOT approved** — do not merge.

**You must not decide alone:** anything that changes the gate sequence, the
package location, or the schema. Surface it and stop.

The bundling question **is** yours to resolve — that is this gate's job — but
record the resolution as a written statement in your result, not as an
undocumented code choice.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be
touched; required evidence cannot be produced; a decision outside the given
authority is needed; or any test fails outside the mutation-floor colour root
cause described above.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode
satisfied, evidence produced, assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback (what in this handoff or the
workflow made the work harder than it needed to be).

**Return thin, write fat.** Put the detail in the result artifact at
`.agent-work/issue-456/crew-handoffs/g0-implement-RESULT.md` and keep the
returned message a pointer to it: the verdict, the evidence that decides it, and
the path. Deliver it via `SendMessage` before ending your turn.
