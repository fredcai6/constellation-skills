# Review Result

## Assigned Gate
g3 (g3-review)

## Result
`APPROVE`

## Handoff compliance
Full. `tests/test_code_map_precommit_e2e.py` delivers all 8 numbered cases from
`g3-implement-handoff.md` via 7 real-subprocess-`git` test methods (case2/3 deliberately combined,
per `InstallThenGreenProofTests`'s own name/docstring — not a dropped case). Every scratch topology
is one shared bare clone (`git clone --bare` of this repo's own common `.git`, read-only) followed
by one or more `git worktree add` calls off it — grepped the whole file for `git clone`/`worktree
add`: the only clone call anywhere is that single shared one. Independently re-ran
`python -m pytest tests/test_code_map_precommit_e2e.py -v` → 7 passed in 60.14s. `git diff --
tests/test_code_map.py` empty (confirmed). `PINNED_SHA_PREFIX = "9d5aac6d"` matches this branch's
actual `HEAD` (`git rev-parse HEAD` → `9d5aac6daa58a72fc6a665cb39879ee5705f7f71`) at review time. All
Close Criteria and Stop Conditions satisfied; no policy decision was required.

## Scope drift
None. This gate's own diff is exactly one new file, `tests/test_code_map_precommit_e2e.py`
(confirmed via `git status --porcelain`). `map/INDEX.md`'s 6-line change is the Commander's separate
mechanical rebuild, not this gate's implementation — independently confirmed byte-identical to a
fresh `python -m scripts.code_map build --root . --artifacts /tmp/... --out /tmp/...` run (`diff`
against `map/INDEX.md`: identical). No Specific Exclusion touched: `git diff --stat -- generate_spine.py
specs/ scripts/checklist_engine.py` and `git status --porcelain` against those same paths are both
empty. `scripts/code_map/`, `scripts/hooks/`, `scripts/install_constellation.py` remain gates 1-2's
already-approved diff, untouched here.

## Evidence verdict
Required evidence present and independently reproduced, not merely trusted:
- `python -m pytest tests/test_code_map_precommit_e2e.py -v` → **7 passed** (matches claim).
- **Case 1 (red proof), independently reproduced by hand** outside the test file: built a fresh
  scratch bare clone + `git worktree add --detach` at `9d5aac6d`, confirmed no `pre-commit` hook
  present (only `pre-commit.sample`), hand-edited `scripts/code_map/discovery.py`, committed with no
  hook installed, then ran `tests/test_code_map.py::MapTreeFreshnessTests` — it **FAILED** exactly as
  claimed (`AssertionError: ... map/INDEX.md is stale`).
- **Case 7 (second worktree), independently reproduced by hand** outside the test file: one shared
  bare clone, `git worktree add` for a first worktree, snapshotted gates 1-2's code onto it as a
  baseline commit, ran the real CLI install (`scripts/install_constellation.py --agent claude --scope
  project --skills charter`) from the first worktree only (`git pre-commit hook: wired ->
  <shared>/hooks/pre-commit`), then `git worktree add` a **second** worktree off the **same** shared
  `.git`. Both worktrees resolved to the identical hooks dir. Committed for real from the second
  worktree with no install run there — the hook fired (`code-map-precommit: staged map/INDEX.md`,
  confirmed in `git log -1 --stat`), `MapTreeFreshnessTests` passed in the second worktree, and the
  first worktree's `git status --porcelain` stayed empty throughout.
- `map/INDEX.md`'s 6-line rebuild independently confirmed byte-identical to a fresh build (`diff
  /tmp/map-check-out/INDEX.md map/INDEX.md` → identical), not accepted on the implementer's
  line-count claim alone.
- Full local suite, independently re-run foreground to completion: **3656 passed, 6 skipped, 0
  failed**, 1275 subtests passed — matches the claimed evidence exactly and clears the
  `3622 passed, 6 skipped, 0 failed` floor.
- `git diff -- tests/test_code_map.py` → empty, confirmed directly.

## Code/doc quality
Minimal, maintainable, matches surrounding style. Every fixture helper read directly (not just
docstrings): `_resolve_hooks_dir` uses the identical `git rev-parse --path-format=absolute
--git-path hooks` idiom `install_constellation.py`'s own resolver uses, so case 7's "same hooks dir"
assertion is a real structural check. Every scratch checkout lives under
`tempfile.TemporaryDirectory()` (auto-discarded); no path outside the temp dir or the explicitly
read-only `ROOT` is touched. No production code changed — proof-only gate honored. Docstrings are
dense and WHY-focused (topology rationale, why hunk-5's edits are placed to force two hunks, why
`_snapshot_gates_1_2_onto` exists), consistent with this project's "agent-facing, dense by design"
doctrine.

**Fowler refactoring pass** (full record: `.agent-work/w2-reindex/FOWLER_PASS.json`, verified by
`scripts/verify_fowler_pass.py` exit 0 — `fowler pass ok: ... (smells=12, flagged=['duplicated-code'],
overridden=[])`). 11 of 12 baseline smells absent. **Flagged** (non-blocking): `duplicated-code` — the
"fresh worktree + real CLI install + assert returncode 0" two-line pattern recurs across cases 4, 5,
6, 8. Judged non-blocking: each occurrence calls into already-shared helpers
(`_fresh_scratch_worktree`, `_run_real_cli_install`), so the duplication is call-site boilerplate, not
duplicated logic, and each test staying an explicit, self-contained narrative is a deliberate
integration-test readability property — case 1 deliberately omits install, so a combining fixture
would obscure which cases install and which do not. Worth a shared `setUp` only if a 5th+ case makes
the boilerplate-to-signal ratio worse. No `overridden` verdicts were needed this pass.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in `g3-implement-implementer-result.md` was
  independently reproduced (full suite, both worktree cases, the `map/INDEX.md` diff), not taken on
  the report's word.
- **Constraints not violated:** yes — `must-be-installed-not-merely-built` is what case 7 proves (the
  second worktree never runs install itself); `do-not-weaken-the-freshness-test` holds (`git diff --
  tests/test_code_map.py` empty); the red-proof pin matches current `HEAD`.
- **Notes match the diff:** yes — this gate's diff is exactly the new test file plus the Commander's
  separately-explained mechanical `map/INDEX.md` refresh; no missing or overstated impact.
- **Decision candidates surfaced:** none were needed — a proof-only gate with no new decision.
- **Durable context routed:** yes — nothing new to route; this gate re-proves already-recorded
  architecture rather than changing it.

## Reconciliation check
No divergence from recorded architecture. The change is additive test coverage only, proving
already-approved gates 1-2 code end to end; it introduces no new capability, interface, or
constraint. Nothing here requires Commander adjudication.

## Blockers
- none

## Out-of-scope observations
- `duplicated-code` Fowler finding (see Code/doc quality above) — non-blocking, worth a shared
  `setUp` helper only if a future case adds a 5th install-then-assert repetition.

## Workflow Feedback
- **Handoff gaps:** one concrete field was wrong, not missing: `REVIEW_SURVEY.template.json`'s
  `r6-fowler` postcondition command names `<reviewer-skill-dir>/scripts/verify_fowler_pass.py`, but
  the script actually lives at `scripts/verify_fowler_pass.py` (repo root) — `skills/reviewer/scripts/`
  does not exist in this checkout. Corrected via the engine's own documented repair path
  (`amend` with a single `retext-check` op on `r6-fowler.c1`, authority
  `constellation/w2-reindex/execute/execute`, reason logged in the amendment) rather than
  hand-editing the survey — exactly the path the item's own imperative names for this situation.
  Worth fixing in the template itself so future reviewers on this repo don't hit the same dead path.
- **Context rediscovered:** none beyond what g1/g2's own reviewer-result files and this session's
  memory already pointed at — confirmed the same `"spine": null` shape in this crew's own
  `crew-runs.json` entry (env `SPINE_FILE`/`SPINE_SESSION` belong to the Commander, not this crew)
  and authored/drove an own survey at the handoff's named Survey State Location through
  `checklist_engine.py`'s CLI, per the skill's own documented branch for this case, rather than
  touching the parent's bound spine.
- **Instructions improvised around:** the `r6-fowler` postcondition command path (see Handoff gaps
  above) — corrected through `amend`/`retext-check` as the item's own REPAIR PATH instructs.
- **What would have made this easier:** fix `REVIEW_SURVEY.template.json`'s `r6-fowler` postcondition
  command to `scripts/verify_fowler_pass.py` (drop the nonexistent `<reviewer-skill-dir>/scripts/`
  prefix) so this correction is not needed on the next reviewer dispatch.

## Return status
`complete`
