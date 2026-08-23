# RESULT — epic-569/w3-promote

## 1. Verdict

Promoted **16 of 65** corpus-wide `check: null` postconditions across 6 of the 8 templates this
lane owns, using only check kinds the engine already has (`decision:no-new-check-kinds`, honored
throughout — no new mechanism was invented anywhere in this wave). This is materially below the
~31 the wave-2 N=3 design-it-twice panel extrapolated from `COMMANDER_SPINE.template.json`'s own
9/19 (47%) figure — a measured negative the launch order's own Honest-Null Clause explicitly
pre-sanctions: **"a small number promoted, honestly measured, is a successful wave."** Every
promotion is red-proofed against an adversary-chosen mutation (never one the promotion's own
match/command text already implies), independently re-derived by a separate reviewer crew for
every gate that touched a file, and shipped with the suite green at every gate boundary — not just
at the end.

`scripts/validate_spine.py`'s corpus-wide `falsifiable-all-null` fault count dropped **19 → 13**,
tracked gate-by-gate in the same commit as each promotion (never a single opaque jump at the end).
The repo's own validator no longer refuses `COMMANDER_SPINE.template.json` on `init`/`reconcile` —
the concrete defect the launch order opened with.

**Per-template assessed-vs-promoted** (fresh-verified at each gate against the real shipped JSON,
not carried over from the wave-2 panel's single-template measurement):

| template | null conditions | promoted | % | vs. predicted [30%,65%] band | shipped |
|---|---|---|---|---|---|
| COMMANDER_SPINE | 19 | **8** (`init.c1`, `plan.c1`, `plan.c2`[existence-only], `plan.c4`[partial], `plan.c5`[partial], `reconcile.c1`, `archive.c2`, `archive.c3`) | 42% | in-band | blocking |
| ADMIRAL_SPINE | 10 | **3** (`init.c2`, `latitude.c1`, `execute.c2`) | 30% | in-band (floor) | blocking |
| EXPLORER_SPINE | 10 | **3** (`init.c2` full; `context.c1`/`spec.c1` split, existence-only) | 30% | in-band (floor) | blocking |
| CHARTER | 10 | **1** (`project-templates.c1`) | 10% | **outside (low)** | blocking |
| IMPLEMENTER_PLAN | 3 | **0** | 0% | **outside (low)** — `m1.c1` is *self-declared* unpromotable (TDD-red condition; a command check would refuse the gate exactly when the run is correct) | n/a |
| SCOUT | 4 | **1** (`report.c1`, split — existence+nonempty half only) | 25% | **outside (low)** | **report-only** (first live check kind in this file) |
| CARTOGRAPHER | 5 | **0** | 0% | **outside (low)** — map DEGRADED-UNPARSEABLE forecloses the only 2 weak candidates (`packets.c1`/`index-overlays.c1`) | n/a |
| EXECUTE_PLAN | 4 | **0** | 0% | **outside (low)** — thin gate-order scaffolding, no artifact-producing claims outside its already-checked test gate | n/a |
| **Total** | **65** | **16** (each row's count above is the number of distinct `postconditions[].check` fields that changed from `null` to a real check dict in that gate's commit; verified directly via `git show <commit> -- '*.template.json' \| grep -c '^\+.*"check":'` divided by 2 for the shipped-file/overlay pair, per gate) | **~25%** | **5 of 8 templates land below the predicted band** | — |

**Structural finding, stated plainly because it is the load-bearing caveat on the ~31 extrapolation
this wave was scoped against**: bucket-2 density correlates with template *shape*, not template
identity. "Rich top-level orchestrator spine with many artifact-producing gates"
(COMMANDER_SPINE, ADMIRAL_SPINE, EXPLORER_SPINE) lands in or near the predicted band every time.
"Thin gate-order/child-plan/bootstrap-once/report-focused scaffolding" (CHARTER, EXECUTE_PLAN,
IMPLEMENTER_PLAN, SCOUT, CARTOGRAPHER) lands at or below the low edge every time, with two clean
structural zeros. The 9/19 (47%) figure that scoped this wave was measured on exactly one instance
of the first shape and should not be assumed to generalize to the second — this is precisely what
`decision:record-the-partition-per-condition` was written to catch, and it caught it: **5 of 7
non-baseline templates fall outside the [30%,65%] band, every one on the low side.** Recorded per
`decision:record-the-partition-per-condition`'s own disposition as a float-note (user-decision
evidence attached at `g0-corpus-survey`), not a hard stop — the Honest-Null Clause explicitly
anticipates this exact shape of result.

## 2. Evidence

All commands below were re-run by the Commander (this run) and independently reproduced by a
separate reviewer crew for every gate that touched a template file. Every number is pinned to the
revision measured.

**Baseline, matching the launch order exactly (before any work):**
```
$ git log -1 --format=%H
135c34eb0b0a10bc5cebb0e6e3869b124e63735e
$ python3 scripts/validate_spine.py skills/commander/templates/COMMANDER_SPINE.template.json
2 fault(s)
  [falsifiable-all-null] init: ...
  [falsifiable-all-null] reconcile: ...
exit 1
```
23 postconditions, 11 `check: null` in `COMMANDER_SPINE.template.json` at that revision — matches
the launch order's stated baseline exactly, no drift.

**Corpus-wide fault count, tracked gate-by-gate (never a single end-of-wave jump):**
| after gate | commit | falsifiable-all-null | falsifiable-unresolved-placeholder |
|---|---|---|---|
| (baseline) | `135c34eb` | 19 | 2 |
| g1 (COMMANDER_SPINE, 8/19) | `ff8e9640` | 17 | 2 |
| g3 (ADMIRAL_SPINE, 3/10 — none cleared a whole gate) | `44180fe0` | 17 | 2 |
| g4 (EXPLORER_SPINE, 3/10, cleared 2 gates) | `442a5826` | 15 | 2 |
| g5 (CHARTER, 1/10, cleared 1 gate) | `d73c6b9a` | 14 | 2 |
| g7 (SCOUT 1/3 + CARTOGRAPHER 0/4, cleared 1 gate) | `450dca6d` | **13** | 2 |

Fresh re-measurement this gate (g8), after all promotions landed:
```
$ python3 -m pytest tests/test_validate_spine.py -q
103 passed in 0.77s
$ python3 -c "... discover_checklist_templates + validate_file sweep over all 11 checklist templates ..."
{'falsifiable-all-null': 13, 'falsifiable-unresolved-placeholder': 2}
```
The 2 `falsifiable-unresolved-placeholder` faults (`EXECUTE_PLAN.template.json`'s
`g1-integrate.c1`, `IMPLEMENTER_PLAN.template.json`'s `m1.c2`) are literal unfilled template
placeholders (e.g. `"<exact test command>"`, filled per-run by each Commander at authoring time) —
a different defect class than `check: null` and out of this lane's promotion scope. Filed as a
triage candidate (§5), never fixed or suppressed to make a number look better
(`decision:validate-spine-wiring-is-in-scope`'s own constraint).

**Per-gate commits, all on branch `epic-569/w3-promote` atop `135c34eb`:**
```
ff8e9640 g1: promote 8 check:null conditions in COMMANDER_SPINE.template.json
44180fe0 g3: promote 3 check:null conditions in ADMIRAL_SPINE.template.json
442a5826 g4: promote 3 check:null conditions in EXPLORER_SPINE.template.json
d73c6b9a g5: promote 1 check:null condition in CHARTER.template.json
450dca6d g7: promote 1 check:null condition in SCOUT.template.json, decline all 4 in CARTOGRAPHER.template.json
e70f2df6 g9: close out execute.json gate progression through g8
f6367f1f: rebuild map/INDEX.md after g5/g7's new test classes
```

**Reviewer verdicts, every gate, first pass** (no BLOCK, no rework anywhere this wave):
| gate | reviewer verdict | review rounds |
|---|---|---|
| g1 (COMMANDER_SPINE) | APPROVE | 1 |
| g3 (ADMIRAL_SPINE) | APPROVE | 1 |
| g4 (EXPLORER_SPINE) | APPROVE | 1 |
| g5 (CHARTER) | APPROVE | 1 |
| g7 (SCOUT + CARTOGRAPHER) | APPROVE | 1 |

Every reviewer independently re-derived the implementer's claims from source rather than trusting
prose — re-running the `falsifiable-all-null` sweep pre/post-edit via `git stash`, dumping
`git show HEAD:...` to confirm pre-existing check kinds, and (for g7's report-only promotion)
actually executing the promoted shell command against missing/empty/populated fixtures to prove it
genuinely discriminates while never blocking `advance`.

**Overlay sync, every gate:** `python3 scripts/check_template_overlay_freshness.py` → `all 56
overlay template(s) checked -- none stale`, confirmed after every template edit.

## 3. Suite result

Full suite, run **after** the final commit (`f6367f1f`) — commit, then re-run, per the launch
order's own discipline (PLAN_CRITIC.md finding 8; this is what let wave 2 ship six tests that only
passed uncommitted):

```
$ git log -1 --format=%H
f6367f1f<...>
$ python3 -m pytest -q
3729 passed, 44 skipped, 1275 subtests passed in 212.83s (0:03:32)
```

Exit code 0. This includes one intermediate red caught and fixed within this same gate: the
first post-g9-commit run (at `e70f2df6`) failed
`MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build` (entity count
drift, `tests.test_checklist_engine` 778→790 entities from the new `CharterW3PromotePromotions` /
`ScoutW3PromotePromotions` / `CartographerW3PromoteDeclined` test classes this wave added).
Rebuilt with `python3 -m scripts.code_map build --root .`, committed (`f6367f1f`), re-ran — green.
Re-confirmed once more after this file's own commit (`476d4cc6`, doc-only, no code touched):
`python3 -m pytest -q` → `3729 passed, 44 skipped, 1275 subtests passed in 217.90s`, exit 0 — the
true final commit on this branch is `476d4cc6`.

## 4. Map impact

**Yes, `map/INDEX.md` needed a rebuild** — see §3. **No active pre-commit hook fired**, because
none is installed in this worktree: `cat "$(git rev-parse --git-common-dir)/hooks/pre-commit"`
returns nothing (only `pre-commit.sample` exists). The launch order's own inherited-context section
did not claim a hook mechanizes this for template edits specifically, but a separate g9 gate
imperative in this run's own `execute.json` did assume one exists ("a pre-commit hook now
mechanizes this; say if it fired") — it did not fire, because it is not installed; the staleness was
caught by `tests/test_code_map.py`'s own freshness assertion in the full suite, not by any hook.
Worth correcting that assumption for future waves in this repo/worktree (§6).

No structural anchors were touched by this wave's own work — every promotion reuses
`checklist_engine.py`'s existing `command`/`artifact` check-kind machinery; `checklist_engine.py`
itself was never edited.

## 5. Triage candidates

- **The 2 `falsifiable-unresolved-placeholder` faults** (`EXECUTE_PLAN.template.json`
  `g1-integrate.c1`, `IMPLEMENTER_PLAN.template.json` `m1.c2`) — literal unfilled template
  placeholders, a template-authoring-bug defect class distinct from `check: null`, out of this
  lane's promotion scope. Filed per g8's own disposition, not fixed or suppressed.
- **CARTOGRAPHER's `packets.c1`/`index-overlays.c1`** — re-assessable once `docs/architecture/`
  carries a real, non-empty, parseable map again (it is currently DEGRADED-UNPARSEABLE repo-wide,
  confirmed independently by both the g7 implementer and reviewer). Not a defect this wave caused.
- **SCOUT's `report.c1` report-only status** — its own named promotion trigger: revisit after N
  clean report-only runs through this gate with zero false-refusals, at the next
  Cartographer/Scout-owning wave, and flip to blocking (a flag-flip per the shipped `command`
  text's own trailing `; exit 0`, not a rebuild).
- **`install_constellation.py`'s manifest gap** — `verify_interrogation.py` exists and could satisfy
  CHARTER's `interrogate.c1`, but the installer's `SKILL_SCRIPTS` manifest doesn't bundle it with
  `"charter"`. Wiring that manifest entry is a genuine, separate future fix (g5's finding,
  independently reconfirmed by g5's reviewer).
- **Whether to additionally tighten `tests/test_validate_spine.py` to zero-tolerance blocking** on
  `falsifiable-all-null` for this lane's 8 templates (mirroring
  `TestShapeAcceptsEveryShippedTemplate`'s already-blocking pattern) — declined this wave (g8):
  cannot land clean without first resolving the 2 out-of-scope placeholder faults above, and several
  remaining all-null gates are honestly-declined by design (`IMPLEMENTER_PLAN`'s `m1.c1` most of
  all — a *self-declared* unpromotable TDD-red condition, not a defect). Floated rather than forced.
- **A stray `.agent-work/<work-id>/` directory** (the literal, unresolved placeholder string as a
  path, containing duplicated `mechanical/`+`context/` receipt JSON for every gate this run closed)
  appeared in the worktree during this session, alongside the correctly-resolved
  `.agent-work/w3-promote/mechanical/` and `.agent-work/w3-promote/context/` directories. This looks
  like a tool somewhere in the harness resolving `<work-id>` literally instead of substituting the
  real work-id on at least one call path — worth someone tracing, though it never affected this
  lane's own deliverable (it sits outside `.agent-work/w3-promote/`, untouched, uncommitted, and not
  part of this PR).

## 6. Workflow feedback

- **The report-only-default reversal at g7 worked cleanly.** g7's handoff explicitly named that
  SCOUT/CARTOGRAPHER measured zero live check kinds and pre-answered the hardest judgment call
  (report-only-by-default, reversing every prior gate's blocking-by-default) precisely enough that
  neither the implementer nor the reviewer needed a round-trip, despite it being a genuine reversal
  of pattern the crew had followed four times already. This is what a well-specified handoff looks
  like when a default needs to flip mid-wave — worth citing as the template for the next wave that
  needs a similar reversal.
- **The single-template extrapolation this wave was scoped against did not generalize, and the
  launch order's own framing ("it is this three-way partition... between bucket 2 and bucket 3")
  undersold how much the corpus-wide 9/19 figure was really a COMMANDER_SPINE-shaped number.** 5 of
  7 non-baseline templates land below the predicted [30%,65%] band, all on the low side, correlated
  cleanly with "thin scaffolding" vs. "rich orchestrator spine" shape. The launch order's own
  `decision:record-the-partition-per-condition` anticipated exactly this and built the right escape
  hatch (float, don't force) — but a future wave scoping itself off a single-template panel should
  weight the corpus-wide extrapolation lower, or explicitly name which OTHER templates it expects to
  share that template's shape, rather than applying one ratio uniformly across 8 structurally
  different files.
- **The launch order's claim that "a pre-commit hook now mechanizes" `map/INDEX.md` freshness does
  not hold in this worktree** — no hook is installed (only `.sample` files); the pytest suite's own
  `test_code_map.py` is what actually catches drift, one full-suite run after the fact rather than
  at commit time. Worth correcting for the next wave, since a Commander that skips a full
  `pytest -q` run between commits (relying on a hook that isn't there) would ship a stale map
  silently.
- **In-harness reviewer/implementer crews consistently report they cannot reach the MCP spine door**
  (their `SPINE_SESSION` env resolves to the dispatching Commander's own bound spine, not a spine of
  their own) at every gate this wave dispatched one. This did not block any gate — each crew
  correctly fell back to a hand-tracked survey per the `constellation-crew`/`constellation-reviewer`
  skill's own documented fallback for "no spine bound" — but it fired identically at g5 and g7 and
  is presumably firing on every crew dispatch across the whole epic, not just this lane. Worth
  someone confirming this is the intended dispatch shape rather than a standing gap nobody has
  looked at because it never blocks.
- **Two real, self-caught process near-misses, neither of which needed Admiral intervention**: g4's
  implementer first pass added a `basis` field to two split conditions
  (`decision:no-basis-backfill` violation, citing an out-of-wave precedent that predated this wave's
  own rulings) — caught by the Commander before review, independently re-confirmed by the reviewer
  against the actual pre-ruling text rather than trusting the correction. g5's reviewer's own
  mutation-testing `git checkout --` reverted the uncommitted file to pre-gate HEAD instead of
  undoing just the reviewer's own test mutation — caught immediately via `git diff`, restored,
  independently re-verified byte-identical by the Commander. Both are evidence the review discipline
  this wave used (independent re-derivation from source, never prose-trust) genuinely catches
  mistakes crews make, including reviewers' own — worth keeping exactly as specified for future
  waves rather than treating it as ceremony.

## 7. Refresh comparison (wave-3 exit criteria)

- **Refresh-request count this run:** 2 — `plan` gate (`why_ref w-3`) and `execute` gate
  (`why_ref w-4`), each recorded once in `.agent-work/w3-promote/mcp_calls.jsonl` and echoed once
  more on a subsequent `current` read before being cleared.
- **Whether a relaunch actually happened:** yes, twice — this session is
  `constellation/w3-promote/commander/commander/attempt-3`, meaning 2 relaunches occurred following
  the 2 refresh-requests above. This is the fix the launch order named working as intended: **"this
  wave the Admiral IS watching for `REFRESH REQUESTED:` and will relaunch you"** — contrasted
  explicitly against wave 2, which raised 8 refresh-requests and had 0 answered.
- **Final `attempt`:** 3 (this session's own identifier). **`total_rework`:** 0 — every task in both
  the top-level commander spine (`init` through `archive`, `rework_count: 0` on all 10) and
  `execute.json`'s own 20 gates (`rework_count: 0` on all) closed without a single rework cycle.
- **Reviewer verdict and review-round count:** APPROVE on the first pass at every one of the 5 gates
  that dispatched a reviewer (g1, g3, g4, g5, g7) — 5 review rounds total, 0 BLOCKs, 0 re-dispatches.
