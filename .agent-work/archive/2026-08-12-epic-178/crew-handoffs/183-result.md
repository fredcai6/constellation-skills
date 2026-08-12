# Result: implementer — issue #183 (Refresh: reach-up flow + job-file principle)

## Verdict

**Delivered, doctrine-complete, with two floats.** Not blocked — the floats are genuine gaps against #179
as merged that need engine changes I'm fenced from (`checklist_engine.py`), not decisions that stopped this
work. The HITL acceptance (the symmetric-recovery drill) is built and left for the human's qualitative
sign-off, per the launch order — not self-certified.

## Isolation

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-183
worktree OK: in C:/Programs/constellation-wt-183
```

## Doctrine files edited (list, for Admiral/human review)

1. **`skills/_shared/global-everyone.md`** — new `## Reach-up: refresh, not re-derive` section. The
   uniform, cross-tier invokee-side mechanism: on a trip, write a `refresh-request` into your OWN engine
   work file via `attach` (pointers only), then go idle — explicitly distinguished from the existing
   "wait-by-ending-turn" failure mode (there's nothing to poll for here; the next actor is a different, fresh
   agent). Encodes job-file-not-agent-file. Also carries an honest caveat: the `gated`-only display gap
   (below) is named here too, pointing at where it's worked around.
2. **`skills/_shared/global-orchestrator.md`** — extends the existing `## Idle subagent adjudication`
   section with a third read (alongside done/stalled): an idle subagent with a pending refresh-request is
   neither — relaunch a fresh agent into the same job file, cold-start from `current` alone. Distinguished
   from a query round-trip and from the dead-agent recovery drill.
3. **`skills/workbench/references/checklist-engine.md`** — new `## Refresh: reach-up without a handoff doc`
   section (added to the Contents TOC too, consistent with `curate_corpus.py`'s reference-toc convention).
   Recaps the merged #179 primitives, then documents **my fulfil-semantics decision**: no evidence mutation
   needed — advancing the tripped gate moves `active_id` past it, so both the predicate and the `current`
   display naturally stop matching (verified live, see Evidence below). Also documents two **known gaps,
   flagged not fixed** (both are `checklist_engine.py` changes, out of this issue's file fence).
4. **`skills/admiral/references/fleet-doctrine.md`** — extends the existing "Recovery drill" section: crash
   and intentional refresh now read the identical `current`; explicitly does NOT replace STATE_NOTE.md (its
   PID/expected-artifact fields track OS-process survival the engine JSON can't know about).
5. **`skills/commander/references/commander-core.md`** — extends "Idle crew at `gN-integrate`" (relaunch a
   fresh implementer/reviewer on a refresh-request, with the gated/survey display asymmetry named) and the
   delegated-mode query paragraph (a trip is a different shape than a query — Commander's own reach-up to
   Admiral).
6. **`skills/admiral/SKILL.md`** — one new bullet distinguishing a Commander's refresh (third shape) from
   both the existing query-round-trip bullet and the dead-Commander recovery drill.
7. **`skills/implementer/SKILL.md`** — one new paragraph: implementer's own reach-up to Commander.
8. **`skills/reviewer/SKILL.md`** — one new paragraph: reviewer's own reach-up to Commander, **with the
   gated-only display caveat stated inline** (see Float 1) rather than claiming false parity with
   implementer.

I judged the doctrine home for the *core* mechanism to be the two global files (`global-everyone.md` for the
uniform invokee behavior, `global-orchestrator.md` for the invoker-side relaunch judgment) plus the
mechanism reference (`checklist-engine.md`, where the fulfil-semantics decision and both gaps live) — these
three are the load-bearing edits. The per-tier-skill edits are light pointers only (1-3 sentences each),
matching the repo's existing "inherited, not restated" convention (e.g. `reviewer/SKILL.md`'s pre-existing
"per inherited doctrine" pattern) — I did not duplicate the mechanism prose into each tier file.

## Fulfil semantics I chose (and verified, not just designed)

#179's author explicitly left "how a fulfilled refresh-request is cleared" to this issue. Given the file
fence (no `checklist_engine.py` edits), I could not extend the predicate or add a supersede verb. Instead I
verified the existing predicate/display already self-clear: both `has_pending_refresh_request` and
`current`'s `_why_suffix` are evaluated against the checklist's *current* active gate, never a historical
one. Once the fresh agent advances the tripped gate, `active_id` moves past it and the stale request's
`seam` stops matching anything — no evidence mutation required. Verified live:

```
$ py scripts/checklist_engine.py --file <refresh-fixture> advance g2-implement-helper --why "implemented retryWithBackoff() per the g1 decision: ..."
g2-implement-helper -> complete
$ py scripts/checklist_engine.py --file <refresh-fixture> current
DONE: no open items.
DIGEST: implemented retryWithBackoff() per the g1 decision: ...
```
(no `REFRESH REQUESTED:` line — cleared itself.)

## The reproducible symmetric-recovery drill (for the human's qualitative sign-off)

**`docs/superpowers/drills/symmetric-recovery-refresh.md`**, backed by two fixtures:
`docs/examples/symmetric-recovery-refresh.json` and `docs/examples/symmetric-recovery-crash.json`.

- Both fixtures were produced by **actually driving the merged engine** (`start` → `advance --why "..."` →
  `start` → branch → `attach refresh-request` on one copy only) — not hand-authored. `diff` between them is
  exactly one JSON evidence object.
- The drill doc pastes the real, reproduced `current` output for both (verbatim transcript, re-verified from
  the checked-in files right before writing this result).
- **How the human runs/reads it:** open the drill doc, read the two `current` transcripts side by side (the
  symmetry is visible without running anything), then — to exercise the actual qualitative judgment — hand a
  fresh agent/subagent the exact prompt in the doc's "The human's drill" section and watch whether it resumes
  from the `DIGEST:` line without asking what happened before or re-deriving the backoff-strategy rationale.
  A rubric ("Resumed cleanly" vs "Re-derived instead of resumed") is given.
- **Explicitly not self-certified:** the doc's final section is a blank "Human verdict" block — I did not
  fill in PASS/FAIL. This differs from this repo's two existing drills (`gh-body-multiline-windows.md`,
  `dogfood-context-paths-absent.md`), which render their own verdict; #183 is HITL by the launch order's
  explicit instruction, so I deliberately did not follow that self-certifying pattern here.

## Floats to the Admiral

1. **DIGEST/REFRESH REQUESTED display is `gated`-only — verified, not assumed.** I attached a
   `refresh-request` to a standalone `survey` checklist and confirmed `current` shows nothing beyond
   `ACTIVE v1 [pending]` — no DIGEST, no REFRESH REQUESTED line, because `_why_suffix` in the merged engine
   returns `""` for any non-`gated` type. The frozen spec's reach-up chain names **reviewer** explicitly
   (a survey-driving role), so this is a real interface gap against #179 as merged, not hypothetical. I
   worked around it in `reviewer/SKILL.md` (read the survey JSON's evidence array directly instead of
   `current`) and flagged it in `checklist-engine.md` as a #179 fast-follow candidate (extend `_why_suffix`
   to surveys) — but I did not fix the engine itself, since it's fenced from this issue.
2. **Predicate is `why_ref`-blind and boolean-per-gate.** If a second, unrelated trip lands on the same
   still-open gate before the first request clears, `has_pending_refresh_request` is already true and
   silently waves the second trip through. This is exactly the "collision with #182's HARD-band use of
   `has_pending_refresh_request`" the launch order asked me to watch for — flagged in `checklist-engine.md`
   for the Admiral and for #182's author, since closing it needs a predicate or evidence-identity change in
   the fenced file.
3. **Launch-order path detail (minor, not blocking):** the launch order says global doctrine lives at
   `skills/<role>/references/global-*.md`; the actual canonical *source* is `skills/_shared/global-*.md`,
   copied into each skill's `references/` at install time by `install_constellation.py` (confirmed by
   grep + reading `workbench/references/checklist-engine.md`'s own description of the bundling). I edited the
   `_shared` source, which is correct, but flagging the discrepancy in case future launch orders should cite
   the source path instead.

## Diffstat

```
 docs/examples/symmetric-recovery-crash.json        |  92 ++++++++++++++++++
 docs/examples/symmetric-recovery-refresh.json       | 103 ++++++++++++++++++++
 docs/superpowers/drills/symmetric-recovery-refresh.md | 104 +++++++++++++++++++++
 skills/_shared/global-everyone.md                   |  41 ++++++++
 skills/_shared/global-orchestrator.md               |  10 ++
 skills/admiral/SKILL.md                             |   1 +
 skills/admiral/references/fleet-doctrine.md         |  10 ++
 skills/commander/references/commander-core.md       |   3 +-
 skills/implementer/SKILL.md                         |   2 +
 skills/reviewer/SKILL.md                            |   2 +
 skills/workbench/references/checklist-engine.md     |  35 +++++++
 11 files changed, 402 insertions(+), 1 deletion(-)
```

`checklist_engine.py` and gauge modules: **untouched**, confirmed by the diffstat above and by
`py -m pytest tests/test_checklist_engine.py -q` still passing (166 passed, 18 subtests passed) — this is a
doctrine-only + fixtures + drill-doc change.

## PR

**https://github.com/fredcai6/constellation-skills/pull/188** (branch `epic178-183-refresh`, base `main`),
opened via `gh pr create --body-file`.

## Verification run

- `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-183` → `worktree OK`
- `py -m pytest tests/test_checklist_engine.py -q` → `166 passed, 18 subtests passed`
- `py scripts/curate_corpus.py` → no new flags on any touched file (checked by grepping output for each
  touched filename)
- Fixture `current` output re-verified from the checked-in `docs/examples/*.json` paths immediately before
  writing this result (not just from my scratch copies)

## Map impact / triage

No structural/capability/constraint changes — this is doctrine text + reference fixtures, no code, no new
capability surface. Nothing to route to Cartographer or Triage beyond the three floats above.
