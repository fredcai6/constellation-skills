# Review Result

## Assigned Gate
`g1-review` (569 w3-basis)

## Result
`APPROVE`

## Handoff compliance
Diff accessible at commit `8691a40e` on `epic-569/w3-basis`; branch and working tree confirmed
clean (`git status --porcelain` shows only untracked `.agent-work/w3-basis/`). All Close Criteria
independently checked against the actual diff and by running commands, not just reading source:

- `PINNED_HEAD`/`_skip_if_head_moved` are gone; `PINNED_BLOB`/`_fail_if_template_drifted` replace
  them (confirmed in `git show 8691a40e`).
- Zero `self.skipTest` remains in `CommanderSpineBasisFields` — `grep -n skipTest
  tests/test_checklist_engine.py` finds exactly one hit at line 1544, in an unrelated class far
  outside this class's line range (class starts at 8543). Drift path is `self.fail(...)` only.
- `self.assertEqual(out.returncode, 0, out.stderr)` runs before the blob comparison in
  `_fail_if_template_drifted`, keeping a `rev-parse` failure distinct from a drift failure (critic
  finding 6, `PLAN_CRITIC.md` line 112-129) — confirmed by reading the method body.
- Fail message verified live (see Evidence verdict below): contains "stale", both blob OIDs, the
  exact literal command `git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json`,
  and "pasting the result into PINNED_BLOB above."
- All 3 original test methods call `self._fail_if_template_drifted()` (confirmed in diff, all
  three call sites renamed). `EXPECTED_BASIS` and `_load_spine` are untouched by the diff —
  `git diff 135c34eb 8691a40e` shows no `+`/`-` lines inside either, only a reference to
  `EXPECTED_BASIS` inside the new fail-message string.
- Class docstring's second paragraph rewritten: no longer says "skip rather than assert"; now
  reads "Pinned to the **blob OID** ... FAILS loudly rather than silently skipping."
- Inline comment near `PINNED_BLOB` reads "g1 dispatch" (was "g2 dispatch" on the retired
  `PINNED_HEAD` line).
- Two new mutation-battery tests (`test_mutation_battery_template_edit_fails_not_skips`,
  `test_mutation_battery_unrelated_commit_stays_green`) actually run and pass individually and
  together (see Evidence verdict).
- `python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs` →
  `5 passed, 3 subtests passed`, zero skipped, run live at commit `8691a40e` (HEAD).
- `PINNED_BLOB` (`6953ac90f2568890fddbe187ad5fc8dd095041dd`) matches
  `git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json` run live against
  current HEAD — not stale.

Suggested model tier ("simple bounded, mechanical criteria list is exhaustive") held up; every
criterion was directly checkable against the diff or a command run.

## Scope drift
Exactly one file changed: `tests/test_checklist_engine.py` (`git show 8691a40e --stat`:
`1 file changed, 133 insertions(+), 16 deletions(-)`). `skills/commander/templates/COMMANDER_SPINE.template.json`
is NOT in the commit's changed-file list — confirmed via `--stat` and via `git log -1` on that
path, whose last touching commit (`a62d0d0e`) predates `8691a40e`. `scripts/checklist_engine.py`
likewise untouched (last commit `bb829a1e`, predates `8691a40e`). No qualitative-condition
population or `basis`-field rollout occurred (inherently true — the template itself was never
touched by this commit). No allowed-scope or exclusion violation found.

## Evidence verdict
Required evidence is present and was independently re-run, not just read:

- `python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs` → ran live:
  `5 passed, 3 subtests passed in 2.78s`. Matches the close criterion exactly.
- Both new mutation-battery tests run individually with `-v`: each `PASSED`.
- Independently reproduced the RED direction *outside* the test's own assertions, to avoid trusting
  a loosely-written self-check: manually cloned the repo to an isolated `/tmp` dir, appended a
  trailing space to the live template, committed in the clone, then ran the 3 protected tests
  against that clone. Result: `3 failed`, each failure body reading
  `AssertionError: CommanderSpineBasisFields' proof is stale: pinned to blob
  6953ac90f2568890fddbe187ad5fc8dd095041dd ... current blob is 1cc57ddc7bc624a377cd18213d477ac4f218dab3
  -- the template changed ... re-pin by running:\n    git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json\nand pasting the result into PINNED_BLOB above.`
  — confirms "stale", both OIDs, the exact literal command, and the paste instruction, all live,
  all in an isolated clone (scratch dir removed after; `git status --porcelain` on the shared
  worktree stayed clean throughout, and no `/tmp/commander-spine-basis-*` or `/tmp/manual-red-*`
  directories were left behind).
- Whole-file regression (extra sanity, not required): `python3 -m pytest
  tests/test_checklist_engine.py -q -rs` → `538 passed, 150 subtests passed in 8.24s`, zero skips —
  no other test in the file disturbed.
- Test mode ("test-after," this gate IS the test file) matches the implementer's claim; TDD-style
  red/green evidence was reproduced independently rather than accepted from the report.

## Code/doc quality
Refactoring / code-smell pass run against Fowler's baseline catalog per this skill's `r6-fowler`
requirement. Record written to `.agent-work/w3-basis/g1-review/FOWLER_PASS.json` and cleared by
`scripts/verify_fowler_pass.py` (`fowler pass ok: ... smells=12, flagged=['duplicated-code'],
overridden=[]`). Verdicts: 11 of 12 baseline smells `absent`. One `flagged`, non-blocking:
`test_mutation_battery_template_edit_fails_not_skips` and
`test_mutation_battery_unrelated_commit_stays_green` share ~15-20 lines of near-identical
scaffolding (mkdtemp+rmdir, `git clone --local`, subprocess pytest invocation, try/finally
cleanup) that a shared `_isolated_clone()` helper could remove; the node-id duplication was
already extracted to `BASIS_TEST_NODE_IDS` but the clone/commit/run boilerplate was not. No
documented repo standard exempts this, so it is not overridden — it is flagged as a minor,
contained, out-of-scope observation (see below), not a blocker: de-duplicating this scaffolding
was not asked for by the handoff's close criteria, and the duplication does not obscure either
method's individual readability. Otherwise the diff is a clean, surgical rename plus an additive
two-method mutation-battery proof; docstring and inline comments are accurate and match the
shipped behavior; no dead code, no speculative abstraction, no primitive-obsession beyond what the
retired code already had (blob/HEAD OIDs as strings, unchanged pattern).

## Map impact verdict
- **Evidence supports claimed change:** yes — the implementer's claims
  (`claim:pin-tracks-file-not-repo`, `claim:drift-fails-not-skips`, `claim:re-verify-is-cheap`)
  were each independently re-confirmed live (GREEN direction, RED direction, and the re-verify
  one-liner itself, respectively), not accepted from the report.
- **Constraints not violated:** yes — `constraint:file-ownership` (only the allowed file touched),
  `constraint:no-skip-on-drift` (zero `skipTest` in the class), `constraint:blob-oid-granularity`
  (`git rev-parse HEAD:<path>`), `constraint:cheap-re-verify` (single `git rev-parse` command,
  printed verbatim in the fail message), `constraint:prove-both-directions` (both directions run
  live) all held.
- **Notes match the diff:** yes — the implementer's Map Impact section (structural anchors,
  capabilities, constraints, decisions, claims) matches what the diff actually touched; no
  overstatement or omission found.
- **Decision candidates surfaced:** n/a — all four decision anchors
  (`decision:blob-oid-not-head`, `decision:drift-fails`, `decision:ship-the-re-verify-path`,
  `decision:prove-both-directions`) were already settled per the handoff/plan; none required new
  authority and none were re-litigated by the implementer.
- **Durable context routed:** yes — the one new observation this review surfaces (test-scaffolding
  duplication between the two mutation-battery methods) is routed below as an out-of-scope
  observation / triage candidate, not silently dropped.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation. Repo map is flagged
DEGRADED-UNPARSEABLE for this run per the handoff — explicitly noted as not this gate's concern,
and this gate's change (test-file-only, one class) has no bearing on that flag.

## Blockers
- none

## Out-of-scope observations
- Minor test-scaffolding duplication between `test_mutation_battery_template_edit_fails_not_skips`
  and `test_mutation_battery_unrelated_commit_stays_green` (clone/commit/run boilerplate,
  ~15-20 lines shared) — candidate for a future `_isolated_clone()` helper extraction. Non-blocking;
  flagged as a Fowler `duplicated-code` finding in `.agent-work/w3-basis/g1-review/FOWLER_PASS.json`.
  Triage candidate for whoever next touches this class, not required for this gate.

## Workflow Feedback

- **Handoff gaps:** none of substance. One small ambiguity: the handoff's stop condition says
  "any file besides `tests/test_checklist_engine.py` changed" but doesn't explicitly say to check
  `.agent-work/w3-basis/` untracked scratch against the constraint "no new self-mutating side
  effects on the shared worktree" — I verified this anyway (`git status --porcelain` before/after
  running both mutation-battery tests) since the constraint implied it, but a one-line evidence
  item naming this explicitly would remove the inference step.
- **Context rediscovered:** none — the handoff's "How to Inspect the Diff" commands and Close
  Criteria list were sufficient on their own; did not need to dig into `PLAN_ALTERNATIVES.md` or
  `MISSION_FRAME.md` beyond reading `PLAN_CRITIC.md`'s finding 6 to confirm the return-code-guard
  ordering claim the handoff itself already stated as a close criterion.
- **Instructions improvised around:** this dispatch's channel has no `mcp__spine__*` access (by
  design — an in-harness subagent's `SPINE_*` env resolves to the dispatcher's spine, not one this
  process should drive). Per the explicit dispatch instructions, I drove this review as an
  independent task using Read/Bash/Grep rather than claiming an engine lease or calling
  `spine_status`/`current`/`advance`. I still built a local Fowler-pass record at
  `.agent-work/w3-basis/g1-review/FOWLER_PASS.json` and ran `verify_fowler_pass.py` against it
  (a standalone script, not an MCP call) so the r6-fowler check's rail was genuinely cleared rather
  than skipped. I did not write a `REVIEW_SURVEY.json` scratch file under `.agent-work/w3-basis/g1-review/`
  beyond the Fowler record, since nothing in this dispatch's channel could advance/consolidate it
  through the engine, and hand-writing a survey that only *looks* engine-driven would misrepresent
  provenance — this REVIEW_RESULT carries the full verification record instead.
- **What would have made this easier:** an explicit line in the handoff (or the dispatch prompt)
  distinguishing "reviewer without spine access, write REVIEW_RESULT directly" from the skill's
  default "claim a survey lease and drive the engine" path would remove the need to infer the
  right mode from the dispatch prompt's override language.

## Return status
`complete`
