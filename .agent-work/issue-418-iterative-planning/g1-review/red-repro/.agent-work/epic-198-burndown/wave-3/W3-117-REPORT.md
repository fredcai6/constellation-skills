# W3-117 Commander Report — curate_corpus.py v2 tooling fixes

**Verdict: COMPLETE.** One green, independently-reviewed PR. Spine driven init→archive, engine lease released
(`DONE: no open items`). **PR #212 (do NOT merge — Admiral merges).**
PR: https://github.com/fredcai6/constellation-skills/pull/212
Branch: `fix/curate-corpus-117` (base main @ 1f3417f) · commit `fcdcfdb`.

## Worktree isolation (required first step)
```
worktree OK: in C:/Programs/cs-wt-curate
EXIT: 0
```

## Per-item verdict (v2 tool fixes only, per SCOPE RULING)

| Item | Verdict | Evidence |
|---|---|---|
| Shared status/check-vocabulary contract fragment | DONE (zero-new-file design) | `curate_corpus.py`'s `STATUS_*` constants already were the single source; `test_curate_corpus.py` hardcoded them independently (~15x) — that duplication IS the drift #104's lesson named. Tests now read `cc.STATUS_FLAGGED`/`SHORTLIST`/`INFO`/`OK`. |
| Exclusion-clause matcher (`'not '` hits anywhere) | DONE | Word-boundary regex (`\bnot\b\|\bnever\b`) replaces bare substring match; false-fires on "cannot"/"whenever" eliminated, genuine standalone/phrasal usage preserved. |
| Person-shortlist matcher (`'us'` false-positive, tc6) | DONE | `_person_tokens` now only counts `"us"` when the ORIGINAL (non-lowercased) text carries a lowercase whole-word `"us"` token — a capitalized `"US"` (United States abbreviation) no longer collides with the pronoun; other pronouns unchanged. |
| Drift-vs-baseline diff block (S7) | NOT BUILT | Not demanded by this run — spec ruling S7 stands, left untouched per instruction. |

**Honest-null check:** none of the three fixes was already resolved on base main — verified directly against
`scripts/curate_corpus.py` before authoring any handoff (manual substring trace for the matcher bugs;
`git log` + reading `test_curate_corpus.py`'s existing literal-hardcoding for the vocabulary gap). All three
were real, live gaps.

## Design decision: zero-new-file vocabulary single-sourcing (mine, cold-critic-driven)

The original plan (before a dispatched cold plan critic reviewed it) was a new `scripts/curate_vocabulary.py`
sibling module imported by both files — the more literal reading of the pre-ruling's "module constant or
data file." A single cold critic (dispatched with zero authoring context, sonnet, general-purpose subagent)
found and I independently re-verified three real blockers in that design:
1. The test's `importlib.util.spec_from_file_location` loader never adds `scripts/` to `sys.path`, so a bare
   `from curate_vocabulary import ...` inside the loaded `curate_corpus.py` would raise `ModuleNotFoundError`.
2. `scripts/verify_skill_registered.py` reads `curate_corpus.STATUS_FLAGGED` directly (line 71) — an
   external consumer the plan's original "18 tests" scope didn't account for.
3. `scripts/install_constellation.py`'s `SKILL_SCRIPT_BUNDLES` hand-enumerates per-skill script bundles with
   no auto-discovery; a real regression test (`test_bundled_scripts_carry_their_sibling_imports`) would
   correctly fail on a new sibling import without a manifest update — but `install_constellation.py` is
   outside this wave's file ownership.

Revised design: no new file. `curate_corpus.py`'s existing constants stay exactly where they are (so
`verify_skill_registered.py` needs no change); only `test_curate_corpus.py` changes, to read `cc.STATUS_*`
instead of retyping the literals. This eliminates all three blockers by construction, verified independently
via `grep` (confirmed zero other scripts read `EXCLUSION_MARKERS`/`PERSON_PRONOUNS`/`_exclusion_present`/
`_person_tokens`/`STATUS_SHORTLIST`/`STATUS_INFO`/`STATUS_OK` either). Plan-alternatives (parallel candidate
authoring) was skipped as a named untaken road — the pre-rulings already settled the *what*; only the
critic ran, single (not a panel — small blast radius, 2 owned files, no architecture).

## Evidence
- `py -m unittest tests.test_curate_corpus -v` → **25 passed** (18 pre-existing + 7 new), both after gate g1
  and after gate g2, reproduced independently by the Commander at every integrate gate (never accepted a
  crew's claim on its word).
- Direct interpreter probes reproduced both matcher fixes' exact before/after behavior (`_exclusion_present`
  on "cannot"/"whenever"/"not"/"never"; `_person_tokens` on "US" vs lowercase "us").
- Both gates: fresh-context implementer + independent fresh-context reviewer, both **APPROVE**, both verdicts
  re-verified directly (review.json read, verdict field + fresh mtime confirmed) rather than trusted from the
  crew's summary.
- `git diff` at each integrate confirmed only the allowed file(s) changed; `scripts/curate_corpus.py` showed
  zero diff after gate g1 (as required); only `scripts/curate_corpus.py` + `tests/test_curate_corpus.py`
  changed in the final commit.

## Map impact
Skill-source repo, no packet map. Reconciled directly at the `reconcile` step: checked all `docs/`
references to `curate_corpus.py` (`docs/CONSTELLATION_OVERVIEW.md`, an eval-latitude drill doc) — both
describe it at a level unaffected by this run's internal changes. Reasoned no-op, recorded compliant.

## Triage candidates — recommend-and-defer (not filed; #117 already tracks it)
Full recommendation: `.agent-work/archive/2026-07-19-117-curate/triage-candidates/consolidation-half-of-117.md`
(worktree copy, `C:/Programs/cs-wt-curate`).
- **Consolidation-run half of #117** (engine-invocation rule restated in 5 skills; implementer/reviewer
  Workflow-Feedback paragraph hoist; commander/commander-delegated spine-enumeration overlap re-measure) —
  explicitly deferred per the Admiral's SCOPE RULING to Fred's human-invoked `constellation-curator` run
  (that skill's own "cadence-is-a-habit" design). Not attempted, not measured. No new issue filed — #117
  already tracks it; this run's Inherited Latitude reserves filing/consolidation decisions to that human run.

## Workflow feedback (staged trio — fenced)
This run's installed `agent_work_root.py` is the stale-vs-main copy the launch order warned about (base
`1f3417f` predates #118/PR #207, which is itself still open, not merged) — confirmed by inspecting
`durable_root()`'s own docstring/logic (no epic-lease-aware branch). Combined with ~11 other concurrently
active `commander-*` agents in this same wave's team session, I staged the feedback trio rather than
writing directly to the shared main-checkout `AGENT_FEEDBACK.md`/`LESSONS.md` (plain read-modify-write, no
locking — a real lost-update race across concurrent writers), per this skill's own bundled "stage, do not
waive" doctrine (confirmed `verify_agent_feedback.py` already supports the staged-trio acceptance path
before relying on it).

Staged at (worktree copy, now under the archived work area):
`C:/Programs/cs-wt-curate/.agent-work/archive/2026-07-19-117-curate/` was the live location before archive
moved it; the **staged-feedback trio itself lives separately** at
`C:/Programs/cs-wt-curate/.agent-work/staged-feedback/117-curate/`:
- `AGENT_FEEDBACK.md` — full retrospective entry for `117-curate`.
- `lessons-delta.json` — 1 banked lesson (`command-postcondition-cannot-attest`, scope `constellation`,
  `tick=true`), validated `--dry-run` against a scratch playbook before staging.
- `CONSTELLATION_FEEDBACK.md` — present, no entries (nothing export-ripe this run — fresh add, mentions=1).
- `FENCE.md` — citation (launch-order friction note + the concurrent-wave race concern above).

**Harvest note for the Admiral:** this trio is under `staged-feedback/117-curate/` in the worktree, per the
normal fenced convention (NOT worktree-root `.agent-work/`, unlike W3-118's dogfooded worktree-local path —
my `agent_work_root.py` copy predates that fix). Harvest before sweeping the worktree.

**Lesson banked (needs-human doctrine target, not self-applied):** `command-postcondition-cannot-attest` — a
`command`-kind postcondition is REFUSED by `attest` ("engine-checked; cannot attest"); the caller must run
the check independently for confidence, then call `advance` directly with `--why` (the engine evaluates the
command check internally during that call). Reproduced 3x this run (both implementer crews' Workflow
Feedback + the Commander itself at `g1-integrate`/`g2-integrate`/`archive`). Fix target is doctrine wording
(the spine/plan template's `gN-integrate` imperative, or `checklist-engine.md`), which needs human authority
to apply in delegated mode — banked, not self-applied.

## Isolation output
`py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-curate` → `worktree OK: in
C:/Programs/cs-wt-curate` / EXIT 0 (pasted above; ran as the literal first action before any problem-solving).
