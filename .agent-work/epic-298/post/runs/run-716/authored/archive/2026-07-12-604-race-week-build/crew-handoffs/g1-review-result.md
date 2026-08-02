# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` (issue #604, race-week staged pipeline — Candidate C, gate G1)

## Result
`BLOCK`

## Handoff compliance
6 of 7 close criteria independently re-verified true:

- Four pure stage functions exist (`discover_sessions_stage`, `predict_stage`, `optimize_stage`,
  `explain_stage`), no hidden global state (only immutable imports + the `VALID_LANES` tuple sit at
  module scope) — confirmed by reading `scripts/race_week_stages.py` in full.
- `predict_stage` never defaults `db_path` — the `SimpleNamespace` threads the caller-supplied value
  verbatim (line 186: `db_path=db_path`, no `or` fallback); confirmed by code read AND by re-running
  `test_predict_stage_never_defaults_db_path`.
- `optimize_stage` calls `generate_report` exactly once and never imports/calls
  `write_beam_search_report` directly — `hasattr(rws, 'write_beam_search_report')` is `False` (I ran
  this live), and reading `generate_report` at `src/fantasy_scoring/artifacts.py:200-228` confirms it
  already writes both `<stem>.json`/`<stem>.md` internally via `write_beam_search_report` at line 227.
- `optimize_stage`'s `lane` parameter rejects anything outside `{"mean","risk","balanced"}` with a
  `ValueError` raised BEFORE `generate_report` is invoked (source read: the `if lane not in
  VALID_LANES: raise` check sits above the `generate_report(...)` call). Independently re-read
  `FantasyBeamSearchResult` at `src/fantasy_scoring/beam_search.py:52-63` — it genuinely exposes only
  `best_mean`/`best_risk`/`best_balanced`, no `best_max`.
- `tests/unit/scripts/test_race_week_stages.py` — re-ran myself: **31 passed in 0.21s**, same test
  names/order as the pasted implementer output.
- `py -m src.utils.simplification_limits --paths scripts/race_week_stages.py` — re-ran myself:
  `PASS (1 files checked)`.

**The 7th criterion fails**, and it is a real, independently-reproduced defect, not a style nit — see
Blockers below.

## Scope drift
None. `git status --porcelain` in the worktree (run by me, not pasted) shows exactly the two
sanctioned new files as untracked additions: `scripts/race_week_stages.py`,
`tests/unit/scripts/test_race_week_stages.py`. `scripts/race_week.py` does not exist (`ls` confirms
"No such file or directory"). `git status --porcelain | grep '^.. src/'` returns nothing — zero `src/`
changes. All Specific Exclusions respected.

One incidental, non-scope item: `data/f1_data_2026.db` also shows as modified (binary, 0
insertions/deletions, identical byte size) in the worktree's `git status`. This predates any command I
ran this session, is not one of the two sanctioned files, and is not mentioned by either the handoff
or the implementer result. Flagged as an out-of-scope observation, not a scope violation of this
gate's mandate (see Out-of-scope observations).

## Evidence verdict
Test-mode is `test-after` (no pre-existing test surface); acceptable per the handoff. The 31-test
suite and `simplification_limits` evidence are solid and independently reproduced (see above).

Required-note evidence (a) no-double-call and (c) lane-validates-before-`generate_report`: solid,
both code-read-confirmed and test-confirmed.

Required-note evidence (b) "`explain_stage` never raises" is **not adequately supported by the
evidence offered**. The implementer's live REPL check and the test suite only exercise the
`shutil.copyfile`-raises-`OSError` mid-copy path — never a bad `explainer_path` input. The broader
claim in the implementer result ("The entire function body is wrapped in a broad try/except
Exception... so no path out of `explain_stage` can propagate an exception") is stated more strongly
than the evidence supports, and is in fact false — see Blockers.

## Code/doc quality
Otherwise good: docstrings are thorough and cite exact source line numbers that all checked out on
re-verification (`get_practice_session_types` at `constants.py:312`, `has_session_classification` at
`_metadata_session.py:506`, round-num pattern at `collector.py:232`, `cmd_sampled_predict` at
`run.py:544`, parser dest names at `run.py:792-814`, `generate_report` at `artifacts.py:200-228`,
`FantasyBeamSearchResult` at `beam_search.py:52-63`). No live FastF1/Jolpica imports, no module-level
`DatabaseManager` construction (`db: DatabaseManager` is always caller-injected).

Minor, non-blocking: `optimize_stage`'s keyword defaults (`lineup_size=10`, `beam_width=25`,
`risk_percentile=90.0`, `balanced_risk_weight=0.25`) are literal numbers that happen to equal
`artifacts.py`'s own `DEFAULT_LINEUP_SIZE`/`DEFAULT_BEAM_WIDTH`/`DEFAULT_RISK_PERCENTILE`/
`DEFAULT_BALANCED_RISK_WEIGHT` (`artifacts.py:27-30`, exported in `__all__`) rather than
importing/referencing those constants. Functionally correct today; a silent-drift risk if
`artifacts.py`'s defaults ever change without a matching update here.

## Map impact verdict

- **Evidence supports claimed change:** Mostly yes — the four stage functions are real and tested as
  claimed, consuming `cmd_sampled_predict`/`generate_report` unmodified exactly as claimed. The one
  overclaim is the "explainer never raises" behavior claim (see Blockers) — the evidence backing that
  specific claim does not actually cover the failure mode that breaks it.
- **Constraints not violated:** DB-only discipline honored (no FastF1/live-API imports); per-year
  `db_path` threading honored (never defaulted internally); compound-prior XOR propagation honored
  (bare call, no swallowing try/except around `cmd_sampled_predict`).
- **Notes match the diff:** Yes, structurally — `struct:scripts`-level new file, no new `src/`
  package, no map-visible structural node, matching the Map Impact notes.
- **Decision candidates surfaced:** N/A — no new architectural decision required at this gate.
- **Durable context routed:** Partially. The implementer's Map Impact section *narrated* that
  `docs/design/race_week_seam.md:26,218`'s "4-lane, includes best_max" claim is stale against actual
  source, but did not file it as a Triage candidate (only listed the pre-known db-path bug under
  "Triage candidates: none beyond..."). I independently re-confirmed the staleness is real
  (`FantasyBeamSearchResult` genuinely has no `best_max`) and filed it as a Triage candidate (`tc1` in
  the survey) so it reaches Commander/Triage rather than being dropped. Not architecture-significant
  enough to block on its own (docs-only staleness, no behavior/capability/constraint mismatch).

## Reconciliation check
No `src/` change, no new Cartographer-visible structural node — `struct:scripts` is script-level per
the handoff's own anchors. See Triage candidate `tc1` above for the one durable-context item that
needed routing.

## Blockers
- **`explain_stage` can raise, contradicting the handoff's close criterion and the implementer's own
  claim.** `scripts/race_week_stages.py:288-289` —
  `explainer_path = Path(explainer_path)` and
  `stub_path = explainer_path.with_name(f"{explainer_path.stem}.STUB{explainer_path.suffix}")` —
  execute **before** the `try:` block that starts at line 291. Live reproduction (run by me against
  the worktree, not hypothetical):
  ```
  >>> import scripts.race_week_stages as rws
  >>> rws.explain_stage('some/stem', None)
  TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'
  >>> rws.explain_stage('some/stem', '')
  ValueError: WindowsPath('.') has an empty name
  ```
  Both are uncaught — they propagate straight out of `explain_stage`, defeating its entire documented
  purpose ("the explainer stage's entire contract is 'never blocks the hard gate'"). The handoff's
  close criterion states explicitly: "`explain_stage` cannot raise under any input, including an
  exception thrown mid-copy — trace the exception-handling path yourself, don't just trust the test
  names." Tracing it (not trusting the test names) is exactly what surfaces this. No test in the
  31-test suite passes a bad `explainer_path`, so the gap was never exercised. This needs a fix
  (move the `Path(...)`/`with_name(...)` construction inside the `try`, or validate/guard before it)
  plus a regression test covering `explainer_path=None`/`''` before this gate can close.

## Out-of-scope observations
- `docs/design/race_week_seam.md:26,218` — stale "4 lanes including `best_max`" claim, confirmed
  factually wrong against `src/fantasy_scoring/beam_search.py:52-63`. Filed as Triage candidate `tc1`
  in the review survey (`.agent-work/604-race-week-build/g1-review/review.json`). Recommend a small
  doc-fix issue.
- `optimize_stage`'s literal-duplicated defaults vs `artifacts.py`'s `DEFAULT_*` constants (see Code/doc
  quality) — low-severity drift risk, not urgent.
- `data/f1_data_2026.db` shows modified in the worktree's `git status` (binary, same size, 0
  insertions/deletions). Predates this review session, not part of the two sanctioned files, origin
  unclear (plausibly a WAL/journal touch from an earlier pytest run in this worktree). Worth a glance
  before this branch is committed/merged so a stray binary diff doesn't ride along, but not this
  gate's defect.

## Workflow Feedback
Mandatory section.

- **Handoff gaps:** None — the handoff was unusually precise and its explicit instruction to
  "trace the exception-handling path yourself, don't just trust the test names" for `explain_stage`
  is exactly what caught the real bug here. That instruction earned its keep; keep writing handoffs
  this way.
- **Context rediscovered:** None beyond ordinary independent seam re-verification the handoff already
  asked for — every cited signature (`run.py:792-814`, `artifacts.py:200-228`,
  `beam_search.py:52-63`, `constants.py:312`, `_metadata_session.py:506`, `collector.py:232`) matched
  source exactly on my own re-read.
- **Instructions improvised around:** none — confirmed after review: the engine's `append` verb for
  survey sub-checks (r4a/r4b/r4c) worked cleanly for decomposing the handoff's "Constraints the
  Implementation Must Respect" list into individually-recorded checks; no workaround was needed.
- **What would have made this easier:** none — confirmed after review: the handoff's line-cited
  seams and explicit "don't trust test names, trace it yourself" instruction were sufficient to find
  the real defect without additional scaffolding.

## Return status
`complete`
