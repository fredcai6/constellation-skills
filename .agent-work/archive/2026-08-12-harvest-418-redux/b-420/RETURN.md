# RETURN — cmdr-420-engine-channel (issue #420, epic #418 workstream B)

## 1. Verdict

**Both fixes landed. This is a win, not a measured negative.** Asked: fix the two engine-channel
defects named in #420 (RAIL echo duplication, unrendered `anchors`/`constraints`) plus a
completeness property test, driven end-to-end through the `constellation-commander-delegated`
spine, no hand-solving around it. Did: drove the full spine (init → context → understand → plan →
execute → reconcile → triage → review → feedback → archive) through the engine; dispatched an
implementer and reviewer as Sonnet subagents via `run_crew.py --dispatch external`; caught a real
defect in my own independent re-verification that neither the implementer's tests nor the cold
plan critic found (a third live anchors shape that exploded into one line per character), sent it
back for rework, and re-verified the fix myself and via an independent reviewer before integrating.
**Both of the two required fixes landed** — say this explicitly since the launch order raised the
partial-land cost: RAIL dedup (verb-aware, `current` only) **and** anchors/constraints rendering
are both in the merged PR. Workstream C (#421) is unblocked.

Vestigial-fields pre-ruling: **not taken.** Corpus inventory (grep across `skills/**/*.json` and
`.agent-work/**/execute.json`) found `anchors`/`constraints` genuinely populated on 20+ real
archived gates with real structured content. Built the renderer; did not delete the fields. No
consequence for C's relocation plan — the fields exist to relocate into, as C assumed.

DIGEST-staleness observation: judged **separate** from this issue's scope, per the launch order's
stated default. Not absorbed here. Routing to workstream G (#425) is the Admiral's call, not mine.

## 2. Evidence

**Tests (targeted, re-run independently by both me and the reviewer, not just trusted from a
claim):**
```
python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q
397 passed, 24 subtests passed in ~15s
```
Baseline before this run (also independently re-run): `388 passed, 24 subtests passed`. Net +9
tests, 0 regressions.

**Commits (branch `epic-418/b-420-engine-channel`):**
- `05cc4db` — the fix itself (`scripts/checklist_engine.py`, `tests/test_checklist_engine.py`,
  `docs/CHECKLIST_SCHEMA.md`) + full run provenance.
- `8d4342f` — work area moved to `.agent-work/archive/2026-08-06-b420-engine-channel/`.
- `e6a91bc` — trailing spine-closeout state (archive gate complete, `c2b` force-waived, lease
  released) — landed in a small follow-up PR since the main PR had already merged by the time the
  archive gate ran.

**PRs, forge-confirmed (not ancestry-tested):**
- `gh pr view 434 --json state` → `{"state":"MERGED", "baseRefName":"main",
  "headRefName":"epic-418/b-420-engine-channel"}`. CI (`gh pr checks 434 --watch`): `test  pass
  5m2s`.
- PR #435 (trailing closeout-bookkeeping commit, no code) — CI green, merged
  (state MERGED, mergedAt 2026-08-06T00:43:42Z, confirmed via gh pr view).

**c2b force-waive, surfaced as required:** the archive gate's `c2b` postcondition checks for an
**open** PR to prove branch-reachability. By the time I reached that gate, PR #434 had already been
merged (by someone/something outside this session — I did not merge it myself; I only observed it
via `gh pr view`) — which exceeds the check's literal ask (merged is more reachable than open, not
less), but the check has no `override_policy`, so `waive` was refused and I used `--force`, citing
the reason in the journal (`e-archive-4`) and here. Flagging this explicitly per doctrine's "treat
`--force` as a last resort and surface it to the human."

## 3. Isolation proof
```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/epic418-b-420
worktree OK: in C:/Programs/constellation-skills-wt/epic418-b-420
```
(exit 0, both at session start and re-confirmed just before writing this file)

## 4. Scope-discipline report

- **`directives` rendering** — same unrendered-defect class as `anchors`/`constraints`, confirmed by
  both the implementer and reviewer, but out of #420's authorized scope ("the two named fields").
  Named at the code site: `tests/test_checklist_engine.py`'s `TaskFieldCompleteness._EXCLUDED_FIELDS`
  comment block. Filed as follow-up issue **#433** (not fixed here).
- **`anchors` missing from `docs/CHECKLIST_SCHEMA.md`'s Task table** — a real doc gap the reviewer
  flagged; **resolved directly in this run's reconcile step** (added to the schema doc), not filed as
  a separate issue since it was small and directly the doc this change touches.
- **A Fowler DRY note** (reviewer, non-blocking): `render_human()`'s new `constraints`/`anchors`
  blocks could fold into the already-generalized pre/postconditions rendering loop instead of
  repeating the label+lines shape as two more `if` statements. Five lines, correctness unaffected.
  Named at the code site (reviewer's Fowler pass record) and here; not fixed — worth folding in on
  the next touch to `render_human()`.
- **`render_human()`'s docstring citation was stale** (`tests/test_checklist_engine.py:818`, an
  unrelated `require_session` test) — fixed opportunistically since I was already editing that
  docstring, not spun into a separate pass to hunt other stale citations elsewhere.
- **RAIL-echo compliance-neutrality** — explicitly NOT evaluated; that is workstream C's
  end-of-tranche tracer's job per `DESIGN_SPEC.md`, not testable from this gate.

## 5. Map impact

No architecture map exists in this repo (skill-source repo, no `docs/architecture/`) — reconciled
directly per `commander-core.md`'s no-map path. Net change for a future reconcile/architecture pass
to know about:
- `scripts/checklist_engine.py`: `_rail()`/`_rail_position()` are now verb-aware (the `point`
  argument, already threaded through from `dispatch()`, now changes what fills the mid-flight
  `{imperative}` token — full text for 5 verbs, a short pointer for `current` only). `state()` now
  passes `anchors`/`constraints` through purely; `render_human()` renders both when populated, via a
  new `_render_anchor_lines()`/`_anchor_category_items()` helper pair that normalizes 3 real corpus
  shapes.
- `docs/CHECKLIST_SCHEMA.md`'s Task table now documents `anchors` (previously prose-only in
  `commander-core.md`) and carries a short "Rendering" note on what `current` shows.
- No interface/schema shape changed (no new field, no renamed field, no changed verb signature) —
  this is a rendering-completeness fix to an existing documented contract (INV-1 in
  `docs/CHECKLIST_ENGINE_DESIGN.md`), not a new interface.

## 6. Triage candidates

- **#433** (filed) — render `directives` in `current`, same shape as this issue.
- The DIGEST-staleness-after-HARD-trip observation from the Admiral's live run — explicitly judged
  out of this issue's scope per the launch order's default; not filed by me (the launch order says
  I flag it, the Admiral routes it to #425).

## 7. Workflow feedback

- **The cold-plan-critic mechanism earned its keep concretely.** Before any code was written, a
  single Sonnet critic (no authoring context) found that my first RAIL-fix sketch was verb-blind —
  a pointer like "the ACTIVE gate above" would have been false on 5 of 6 railed verbs. Cheap,
  plan-time catch of what would otherwise have been a review-time or production defect.
- **Independent re-verification at gate-integrate caught a real defect the implementer's own tests
  missed**, and neither the plan-time cold critic nor the launch order's pre-rulings anticipated it:
  a third live `anchors` shape (`{category: "<plain string>"}`, used by `g1-review`'s own gate in
  the shipped `EXECUTE_PLAN.template.json`) exploded into ~90 lines of one-character-per-line
  garbage on the implementer's first pass — worse than the pre-#420 silent drop. Caught by literally
  re-running the implementer's own claimed evidence myself rather than trusting the pasted output;
  fixed via a same-agent `SendMessage` rework round-trip (~3 minutes, no re-briefing needed) rather
  than a fresh dispatch.
- **`py` vs `python` on this Windows worktree:** `py` resolves to an interpreter with no `pytest`
  installed; `python` has pytest 9.0.2. `_COMMON.md`'s platform invariants say "both `py` and
  `python` work" for the engine CLI — true, but not for the test suite. Cost one failed command.
- **`c2b`'s open-PR check has no path for "already merged, which is a BETTER outcome than open."**
  Worth a doctrine note or a check update (`state in {"OPEN", "MERGED"}`) so a fast-merging PR
  doesn't force a `--force` waive on every run where the Admiral (or auto-merge) is quick.
- Full retrospective, including crew-reported friction, is in the staged
  `AGENT_FEEDBACK.md`/`lessons-delta.json` (see below) — not duplicated here.

## Fenced feedback closeout

This worktree is fenced off the main checkout's durable `.agent-work/` — `durable_root()` auto-
detected an ACTIVE Admiral epic lease on `C:/Programs/constellation-skills/.agent-work/epic-418/
spine.json` and correctly redirected durability to the worktree. Staged the full trio (not waived)
under `.agent-work/archive/2026-08-06-b420-engine-channel/../staged-feedback/b420-engine-channel/`
(now moved alongside the archived work area — actual path:
`.agent-work/staged-feedback/b420-engine-channel/`):
- `AGENT_FEEDBACK.md` — full retrospective, real content in every signal section.
- `lessons-delta.json` — 1 new `constellation`-scoped lesson
  (`lesson:docstring-line-citations-drift-silently`), dry-run validated against a scratch copy of
  the real playbook (never written to it — read-only `--ripe` check confirmed 0 ripe lessons this
  run, including this new one on its first mention).
- `CONSTELLATION_FEEDBACK.md` — staged as an honest empty-this-run placeholder (nothing ripe to
  export).
- `FENCE.md` — cites this launch order and the `durable_root()` auto-detection.

**Please harvest this trio into the shared main-checkout root before sweeping this worktree** — it
carries real signal (the docstring-citation-drift lesson, the `c2b`/merged-PR friction note) that
should not be lost with the worktree.
