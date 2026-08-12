# Review Result

## Assigned Gate
`g2` — close: `closeout_refusal` (pure) and `close_work` (impure) on `scripts/spine_lifecycle.py`.

## Verdict
`APPROVE`

## Result
`APPROVE`

## Handoff compliance
Both functions match `LIFECYCLE_CONTRACT.md` §4 and the g2 implementer handoff exactly. `closeout_refusal`
is pure (no `Path`/`open`/`subprocess`, AST-confirmed by its own test) and refuses in order: lease not
`"released"` → non-terminal gate (naming it) → archive already exists. `close_work` starts at "move the
work area, spine file last," never performs or re-implements satisfying postconditions / the final
`advance` / `release`, and never opens a PR or removes a worktree. All 10 close criteria in the handoff
have a corresponding, independently re-run, passing test. Required evidence (differing-basename mutation,
interruption fixture, end-to-end real-engine close) reproduced myself, not accepted on the report's word.

## Scope drift
None. `git diff --stat` against every named exclusion (`checklist_engine.py`, `validate_spine.py`,
`mcp_spine_server.py`, `generate_spine.py`, `settings.json`, `.mcp.json`, `docs/agents/*`, `skills/**`) is
empty. Only `scripts/spine_lifecycle.py`, `tests/test_spine_lifecycle.py`, and the mechanically-regenerated
`map/INDEX.md` changed. Branch is `epic-559/c3-lifecycle`, not `main`; no push evidence.

## Evidence verdict
Reproduced everything myself rather than trusting the result artifact:

- Full suite: **2875 passed, 3 skipped, 1121 subtests** (exact match; +19 net matches
  `test_spine_lifecycle.py`'s 32→51 `def test_` growth, grep-confirmed).
- `validate_spine.py --sweep`: exactly **23**.
- **Differing-basename mutation (criterion 5, mandatory):** independently mutated `spine_name =
  absolute_spine_path.name` to the literal `"spine.json"`. `TestCloseWorkDifferingBasenameMandatory` went
  RED with the exact predicted signature (`triage-candidates` never moved because `execute.json` sorted
  into the "everything else" batch and the interruption fired there first). Restored; GREEN again; `git
  diff` showed no residue.
- **Went further than the handoff asked** on the ordering question (review item 3, "could the test pass if
  the spine moved first?"): mutated `close_work` itself to move the spine **before** the other entries.
  Both `TestCloseWorkSpineLastUnderInterruption` and `TestCloseWorkDifferingBasenameMandatory` went RED —
  proof these fixtures check genuine ordering, not merely that a monkeypatched `_git` raised. Restored;
  both GREEN.
- **Interruption fixture (criterion 6):** confirmed simulated (a monkeypatched raise on any git call naming
  the spine), stated as such in the test's own comments; the file-listing assertion covers both the spine
  and its journal at their original path.
- **End-to-end (criterion 8):** read `TestCloseWorkEndToEndRealEngine`'s source — it calls
  `checklist_engine.claim/start/attest/attach/advance` directly on a real `open_work`-compiled spine, then
  `release`, then `close_work`. Not simulated. Reran green.
- **Differential test (criterion 9):** `TestCloseoutRefusalAgreesWithSpineTerminal` exercises one terminal
  and one non-terminal case against the real `run_crew.spine_terminal` reading a real file. `closeout_refusal`
  adds a survey-consolidation refusal branch beyond the handoff's 3 literal bullets — checked
  `run_crew.spine_terminal`'s own source (`run_crew.py:358-359`) and confirmed this branch is *required* for
  genuine agreement, not scope creep: `spine_terminal` also treats an unconsolidated survey as non-terminal.
- **Stage-by-name guard (criterion 7):** the positive control
  (`test_violating_a_mutated_copy_with_add_dash_a_is_caught`) genuinely injects a `git add -A` call and
  asserts the AST guard catches it. Reran, passes.
- **Refusal does nothing (review item 2):** the three refusal tests snapshot the FULL `.agent-work` tree
  byte-for-byte before/after, not just archive absence.
- **`map/INDEX.md`:** regenerated myself (`python -m scripts.code_map build --root .`); idempotent on a
  second run; matches the claimed entity-count delta (`scripts` 1156→1160, `tests` 4332→4371).

## Code/doc quality
Minimal and maintainable. `close_work` reuses g1's existing `_git` helper rather than duplicating
subprocess plumbing. `newline="\n"` is not weakened: `close_work` adds zero new `write_text` call sites
(only g1's pre-existing one in `open_work` exists, already pinned); the g1 `TestEveryWriteTextPinsNewline`
guard is still present and green. Full Fowler baseline pass run (`.agent-work/epic-559/c3-lifecycle/g2-review/FOWLER_PASS.json`,
`scripts/verify_fowler_pass.py` exits 0): 12/12 smells visited, 10 absent, 2 overridden with a logged
repo-standard reason — `long-method` (the fixed close-ordering invariant needs single-function locality,
per the inherited "deep-module vocabulary" doctrine, and matches `open_work`'s own shape) and
`primitive-obsession` (the dict-in/dict-out pure-function shape is the contract-mandated convention shared
with every sibling in this module and with `generate_spine.py`/`validate_spine.py`/`checklist_engine.py`).

## Map impact verdict
- **Evidence supports claimed change:** yes — entity-count delta independently reproduced.
- **Constraints not violated:** yes — no inbound constraint (g1's functions, `checklist_engine.py`'s
  format, `validate_spine.py`) was silently broken; g1's own code is untouched except the module docstring.
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** yes — the implementer flagged the work-id-derived-structurally-not-from-origin
  choice as a latitude decision, consistent with §8's "retrofitting `origin` onto spines opened by hand" exclusion.
- **Durable context routed:** n/a — no triage candidates raised, none found in independent review either.

## Reconciliation check
No divergence from the recorded architecture requiring Commander reconciliation. See `r5-reconciliation` in
the driven survey.

## Blockers
- none

## Out-of-scope observations
- none

## Workflow Feedback

- **Handoff gaps:** none blocking. One genuine soft gap: the handoff's review item 5 asks whether
  `closeout_refusal` "agrees with `run_crew.spine_terminal`" but its own 3-bullet summary of
  `closeout_refusal`'s refusal conditions omits the survey-consolidation branch that turns out to be
  *required* for that agreement to hold. Confirmed the implementation is correct (verified against
  `spine_terminal`'s own source); the handoff text just under-describes its own acceptance criterion. Worth
  a one-line addition if this contract is ever revisited.
- **Context rediscovered:** none — the contract and implementer result artifact were unusually complete;
  no empirical rediscovery was needed on my side.
- **Instructions improvised around:** none — the review standard's five numbered ordering checks (item 3)
  asked for something stronger than "does the fixture prove ordering" so I added the spine-first mutation
  experiment myself; this wasn't a case of the instruction not covering the situation, just going one level
  deeper than the literal ask.
- **What would have made this easier:** none — confirmed after review: the handoff's "verify in this order"
  list and the implementer's evidence section were both precise enough that no additional digging was
  needed beyond the mutation experiments the standard itself calls for.

## Most likely way this gate ships green and wrong
None found after independently falsifying the two candidate mechanisms named in the handoff (literal
basename hardcode, and moved-first-not-last ordering) — both correctly go red. If this gate were to ship
green-and-wrong, the most plausible remaining seam is `close_work`'s reliance on `work_dir.relative_to(agent_work_dir)`
to derive `work_id` structurally: if a caller ever invoked `close_work` with a `spine_path` that resolves
outside `root/.agent-work/` (a path-confinement question `close_work` itself does not guard, unlike
`open_work`'s validated `work_id` input), `relative_to` raises `ValueError` rather than a `SpineLifecycleError`
naming the problem legibly. Not a defect against this handoff's stated scope (no confinement requirement is
named for `close_work` in the contract, and every caller in this codebase reaches `close_work` via a
spine path the engine itself bound), so not raised as a blocker — recorded here as the honest answer to the
question, not as a finding.

## Return status
`complete`
