# Review Result

## Assigned Gate
Wave 3 batch A+B independent review — `efe92791..99a46a08` on `afk/20260821-ab`
(A1–A6, B1–B2, plus the coordinator-adjudicated R1/R2 residuals).

## Result
`APPROVE`

## Handoff compliance
All eight items plus R1/R2 verified individually against source, not against
the implementer's transcript. B2 (highest-risk) and B1 (the journaling trap)
got the most effort, per the handoff's instruction; A1–A6 and the map commit
were each checked against their specific named trap. No source, test, or
commit was edited. No `mcp__spine__*` tool was called. No commit/push/PR.

## Scope drift
None. `git diff --name-status efe92791..99a46a08` is exactly: `map/INDEX.md`,
`scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`scripts/run_crew.py`, and 10 test files — the allowed set precisely.
`git diff --stat` against `skills/charter`, `skills/_shared/global-everyone.md`,
`tests/data/store_mentions.approved.txt`, and `docs/` returns nothing; none of
the human's own uncommitted work appears anywhere in this branch's diff.
`git status --short` in the worktree shows only the untracked
`.agent-work/20260821-ab/` work directory. Option C (lease demotion) and
R9/R10 (leaseless hole): confirmed absent by grep across the full diff.

## Evidence verdict
Independently reproduced, not trusted:
- Full suite: `py -m pytest -q` → **3469 passed, 6 skipped, 1224 subtests
  passed, 0 failures** — exact match to the claim (base was 3447/6/1222).
- `git diff --check efe92791..99a46a08` → exit 0.
- Before/after render, both renderers, against an identical synthetic
  22d19h-stale lease: `checklist_engine.render_human` and
  `spine_rail.reconstruct_current` both produce `LEASE HELD: ... last
  heartbeat 547h00m ago`; the base renderer produces `LEASE active: ...
  heartbeat <raw ISO>`. Confirmed by running both renderers directly, not by
  reading the implementer's transcript.
- Mutation tests: broke `spine_rail`'s `HELD` string shape →
  `ReconstructCurrentLeaseShapeMatchesA3` catches it (2 failures); broke A5's
  owned-binding staleness exemption → `test_owned_binding_resume_is_not_gated_
  by_staleness` catches it (`KeyError`/missing `hookSpecificOutput`). Both
  worktree files restored clean afterward (`git diff --stat` empty).
- Red/green check: swapped in the base `run_crew.py` and re-ran the two
  reversed-premise B2 tests (`test_fresh_launch_with_no_parent_is_refused_
  naming_what_to_pass`, `test_fresh_dispatch_with_no_parent_is_refused_never_
  reads_ambient`) — both genuinely fail against base (`AssertionError`,
  `CrewLaunchError not raised`), confirming they are not tautologies.

## Code/doc quality
Fowler pass run (`r6-fowler`, record + `verify_fowler_pass.py` exit 0, see
`.agent-work/20260821-ab/FOWLER_PASS.json`): 10/12 smells absent. Two
overridden with a logged standard: **duplicated-code** (the `_format_age`/
lease-line duplication between `checklist_engine.py` and `spine_rail.py` is
forced by `spine_rail.py`'s own pre-existing, base-commit-documented
stdlib-only/no-subprocess law, and is guarded by a mutation-tested pinning
regression, not left as an unenforced promise) and **comments-as-deodorant**
(the dense rationale comments extend this repo's pre-existing house style and
explain design history next to simple code, not confusing code). No smell
was flagged as a real defect.

## Map impact verdict
- **Evidence supports claimed change:** yes — entity-count deltas
  (scripts 1274→1277, tests 5291→5319, etc.) are attributable to this batch's
  two new functions (`_is_archived_path`, `_lease_is_stale`) plus new test
  coverage; verified directly in `git show 99a46a08 -- map/INDEX.md`.
- **Constraints not violated:** yes — `_RAIL_STRINGS` confirmed byte-identical
  to base by direct `diff`, not by re-reading prose; `MUTATING_VERBS`
  confirmed set-identical to base including `waive`'s continued membership.
- **Notes match the diff:** yes — no new verb, schema field, or file; matches
  the implementer's own Map Impact section exactly.
- **Decision candidates surfaced:** yes — A4's identity-blind relabeling
  choice and B2's construction-time-not-argparse enforcement point are both
  disclosed as deliberate, latitude-bound choices with reasoning.
- **Durable context routed:** yes — R1 (Stop-hook render drift) and R2 (map
  staleness) were both flagged out-of-scope by the original batch and then
  actually adjudicated and closed by the Admiral in this same branch, the
  correct path. This review adds two further triage candidates below.

## Reconciliation check
No divergence from recorded architecture in the reviewed diff itself. One
real, out-of-scope gap found by this review (not introduced by the diff, but
newly load-bearing because of it): `skills/commander/references/crew-dispatch.md`
— the doctrine a Commander reads before every crew dispatch — documents
`--model`, `--reasoning-effort`, `--backend`, `--resume`, `--abandon` in
detail but has **zero** mentions of `--parent`, even though B2 now makes it a
hard requirement for a fresh/relaunched dispatch. A grep of the entire
`skills/` corpus and `docs/agents/` for `--parent` returns nothing. Every real
Commander/Admiral dispatch going forward will hit the new refusal cold.
Materially mitigated, not a blocker: the refusal message is self-teaching
("pass the identifier of whoever is dispatching this crew, e.g. a
Commander/Admiral session name"), so the first refusal is directly
actionable without the doc being fixed first — but it should still be fixed.

## Blockers
- none

## Out-of-scope observations
- **B2 test-coverage gap (real, non-blocking).** The three scripted AST
  patches added `--parent test-parent` to every `RC.main([...])` call they
  touched, including `--resume`/`--verify-result`/bare-`--abandon` call sites
  that architecturally do not need it (`CliBackend.resume` and the
  verify-result path build no fresh `CrewSpec`, confirmed by reading the
  source). Net effect: the shipped suite no longer contains a single test
  that exercises `--resume`, `--verify-result`, or bare `--abandon` **without**
  `--parent` — the exact guarantee the handoff asked to confirm. I
  independently reproduced all three working with no `--parent` (exit 0 in
  each case, direct `RC.main()` calls against real fixtures) — the
  implementer's claim is TRUE — but the regression coverage for it is gone
  forward. A future change that accidentally required `--parent` on these
  paths would not be caught by this suite. Recommend a small follow-on: one
  focused test each for `--resume` and `--verify-result` with no `--parent`.
- **`crew-dispatch.md`'s `--parent` gap** — see Reconciliation check above.
  Recommend routing to whoever next touches Commander doctrine, or fixing
  directly in the next doc-touching pass.
- **Hand-rewrite count discrepancy (informational only).** The handoff
  estimated "four hand-rewritten tests" for B2; a full line-by-line audit of
  every diff hunk in the four B2-scoped test files (confirmed by diffing
  each file's pre-batch scratch `.orig` copy against its current version)
  found exactly **three** substantive rewrites, not four:
  `test_fresh_launch_with_no_parent_is_refused_naming_what_to_pass` (renamed
  from `..._still_works_and_records_none`),
  `test_fresh_dispatch_with_no_parent_is_refused_never_reads_ambient`
  (renamed from `..._binds_unknown_not_ambient`), and
  `test_blocked_with_unknown_parent_says_so_plainly` (name kept, body fully
  rewritten to call `_crew_status_line` directly on a legacy fixture, since a
  fresh CLI dispatch can no longer reach that scenario post-B2). A fourth
  candidate, `test_abandon_relaunch_inherits_stored_parent_when_not_
  reasserted`, only gained an explanatory comment — its assertions were
  already correct pre-batch (it never passed `--parent` on the relaunch call)
  and needed no rewrite. This does not change the verdict; noted so the
  estimate isn't silently carried forward as fact.

## Workflow Feedback

- **Handoff gaps:** none material. The B2/B1 traps named exactly the risks
  that mattered (the AST-patch blast radius, the `MUTATING_VERBS` journaling
  coupling); both were real and both held up under audit.
- **Context rediscovered:** the implementer's scratch directory
  (`.agent-work/20260821-ab/scratch/`) carried pre-patch `.orig` copies of
  every B2-touched test file, an intermediate `.pass2` copy for
  `test_crew_launcher.py`, and pre-change baseline copies of both edited
  source modules. This made the B2 audit dramatically faster and more
  precise (byte-diff against a known-good baseline instead of reconstructing
  intent from the final diff alone) — worth naming explicitly as a pattern
  other Implementers should leave behind for a scripted-patch-heavy item,
  since the handoff itself didn't ask for it but it was exactly what made
  independent verification tractable.
- **Instructions improvised around:** the handoff's Survey State Location
  convention (`.agent-work/<work-id>/<gate>-review/review.json`) and the
  `r6-fowler` postcondition's fixed path
  (`.agent-work/<work-id>/FOWLER_PASS.json`, no subdirectory) point at two
  different directories for the same work-id. I kept the survey under
  `ab-review/` per the stated convention and placed `FOWLER_PASS.json` at
  the bare `.agent-work/20260821-ab/` path the postcondition's command
  literally names (also mirrored a copy under `ab-review/` for
  proximity to the survey). Not a blocker, just a path mismatch worth
  tightening in the template.
- **What would have made this easier:** nothing significant — this handoff
  was unusually well-scoped and its named traps were real. The one small
  win would be the scratch-directory convention noted above being named as
  a standing Implementer practice, not just something this run happened to
  do.

## Return status
`complete`
