# Review Result

## Assigned Gate
`g2-review` — DC4, same-gate equivalence as a property (issue #424, workstream F of epic #418)

## Result
`APPROVE`

APPROVE

## Handoff compliance
Yes. The handoff asked for independent verification that `tests/test_mcp_imperative_equivalence.py`
(commit `696caaea`) is a genuine population property over the whole shipped template tree, not a
sample, and that the delivered permanent positive control is real. All nine numbered close criteria
plus the two central asks (draw the divergence-mode boundary; mutate the permanent control yourself)
were verified directly, not accepted on report. Full detail is in the driven survey at
`.agent-work/epic-418-followon/commander-424/g2-review/review.json` (items r0–r14, all `pass`,
0 `fail`).

## Scope drift
None. `git show --stat 696caaea` lists exactly 18 changed files: the deliverable test file,
`map/INDEX.md`, and the implementer's own workbench artifacts. `git diff fda35ec0..HEAD`, scoped to
every fenced file (`install_constellation.py`, `test_feedback_tooling.py`,
`test_install_constellation.py`, `test_run_skill_eval.py`, `test_spine_rail.py`), `checklist_engine.py`,
and `test_mcp_identity.py`, is **0 lines**. `settings.json` untouched at every scope. `docs/agents/`
untouched. Issue #424 confirmed still OPEN (`gh issue view`: `closedAt: null`).

## Evidence verdict
Present and independently reproduced, not merely re-run:

- **Population count.** My own standalone walk of `skills/*/templates/*.template.json` found 61 gates
  across 12 templates (20 files, 8 skipped) — exact match to the implementer's claim.
- **Walk, not a list.** I added a real scratch template
  (`skills/scout/templates/ZZREVIEW424.template.json`) with a distinct canary gate. The module's own
  `discover_gates_with_imperative()` picked it up (61→62), and a live `pytest -k population` run picked
  it up too (13 templates, canary compared through both real arms, passed). Deleted it afterward;
  `git status` confirmed clean.
- **The load-bearing check — mutate the real door, not just the shipped control.** The shipped
  `PositiveControlTests` proves the comparator can go red, using two different spine files (one
  mutated, one not) driven through the real CLI subprocess and a real MCP server subprocess over real
  JSON-RPC — not a bare string comparison. I went further: I edited **the actual production door**,
  `scripts/mcp_spine_server.py`'s `as_result()`, to truncate the `ACTIVE` line's own imperative text —
  a genuine MCP-side rendering bug, applied against the **same shared spine file** both arms read (the
  real production shape). 4/5 tests in the file went RED with an `AssertionError` naming the exact byte
  mismatch. Restored via `git checkout`; `git diff`/`git status` confirmed clean; reran green (5/5).
  This is direct, reproduced proof — not argument — that the property is sensitive to a real MCP-door
  rendering-side bug.
- **Full suite.** Independently reproduced: `2177 passed, 1 skipped, 1061 subtests passed, 0 failed` —
  exact match to the implementer's report and to baseline (2172) + 5 new tests.

## Code/doc quality
Fowler pass: 12/12 smells rendered (record at
`.agent-work/epic-418-followon/commander-424/g2-review/fowler-pass.json`, `verify_fowler_pass.py` exits
0). 2 flagged, non-blocking: `long-method` (two multi-step test methods, matching
`test_mcp_identity.py`'s own established `DC3PositiveControlTests` shape); `comments-as-deodorant` (a
stale count in the file's own header comment — see tc1 below). 1 overridden: `duplicated-code`
(repeated per-class tempdir/spine/`ServerInstance` setup across three `TestCase` classes), subordinate
to `test_mcp_identity.py`'s own house pattern of independent per-class setup, which this file's module
docstring explicitly cites as the convention it is reusing. 9 absent.

## Map impact verdict
- **Evidence supports claimed change:** Yes — no production code changed; the new test file is
  read-only against `checklist_engine.py` and `mcp_spine_server.py`.
- **Constraints not violated:** Yes — the shared-spine-file design fact the implementer surfaced was
  independently confirmed correct and correctly scoped (see boundary discussion below).
- **Notes match the diff:** Yes.
- **Decision candidates surfaced:** None required; none forced.
- **Durable context routed:** Yes — two triage candidates logged below and in the survey's
  `triage_candidates` (tc1, tc2), not fixed silently.

## Reconciliation check
None requiring Commander action. The implementer's surfaced structural fact (both arms read one shared
spine file per gate by design) is correct and does not weaken DC4 — confirmed directly by my own
mutation, which shows the property is sensitive to the door's own rendering/transport layer regardless
of that shared-read design.

## The boundary, drawn plainly (the review's central ask)

The MCP arm's pipeline, after the point where both arms call the identical
`checklist_engine.main(argv)` function, is: `run_engine()` (capture stdout+stderr) → `as_result()`
(wrap into the MCP content envelope) → `json.dumps` over the JSON-RPC line → `ServerInstance`'s
`json.loads`/`content[0].text` read. The CLI arm never touches any of that — its stdout is read
directly off its own subprocess.

**Catches (proven by mutation, not argued):** the MCP door truncating, stripping, re-wrapping, or
re-encoding an imperative the CLI renders in full — any of these, wherever in that MCP-side transport
layer they happen, corrupt the `ACTIVE` line's captured imperative substring, and the byte-exact
comparison catches it. I proved this directly by truncating the real door's output and watching the
suite go red. A divergence in "only one arm's rendering path" is caught, and in practice this is what
the property is testing: the MCP arm is the only side with a transport/wrapping layer of its own — the
CLI arm is a bare engine invocation with nothing to diverge in.

**Does not catch:** a bug inside the *shared* `checklist_engine.main()`/`render_human()` function
itself, because both arms call that literal same Python function (the CLI's own subprocess `__main__`,
the MCP server's in-process import-and-call). A corruption there renders identically wrong on both
sides, so `cli_imp == mcp_imp` still holds and this suite stays green. This is correctly out of DC4's
own stated scope — DC4 says "the CLI projection and MCP tool result carry the same imperative text,"
and same-but-wrong is not a DC4 violation by that wording. A shared-engine-correctness bug needs a
different test.

**Verdict on the boundary:** the property is not weaker than DC4 claims. It is exactly as strong as
DC4's own wording requires — proven sensitive to every MCP-door-side divergence mode the handoff named,
and its one blind spot is a genuinely different claim (shared-engine correctness) that DC4 was never
written to cover.

## Blockers
- none

## Out-of-scope observations
- **tc1** (from r5/r6-fowler): `tests/test_mcp_imperative_equivalence.py` lines 80–89 (module header
  comment) says "of 19 `*.template.json` files found; the other 7 are result/record templates" while
  listing exactly 8 names right next to it — the tree today (and the file's own printed pytest
  evidence) actually has 20 files / 8 skipped, not 19/7. Cosmetic only; the runtime discovery is dynamic
  and correct, and the 61/12 headline claim is unaffected. Worth a one-line comment fix.
- **tc2** (from r12): `PopulationPropertyTests` only asserts `cli_imp == mcp_imp` across the 61-gate
  loop; it does not extend `SingleGateWiringTests`' ground-truth-vs-source-template check (asserting
  both arms also match `gate.task["imperative"]`) beyond its one canary gate (`g1-implement`). Not a DC4
  gap — DC4 only requires CLI==MCP agreement — but means a shared-render corruption affecting only some
  gates would slip past every check in this file, caught only by the single canary if it happened to be
  the affected gate. Worth considering for a future gate: fold the three-way (source/CLI/MCP) check into
  the population loop, or explicitly accept it as covered elsewhere.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff's central ask ("state plainly which divergence modes
  this property would catch") was answerable directly from the code plus one mutation — no ambiguity
  in what was being asked.
- **Context rediscovered:** had to trace `mcp_spine_server.py`'s `run_engine()`/`as_result()` byte-for-
  byte to determine exactly which pipeline stage sits downstream of the shared `main()` call — this is
  the crux of the boundary question and isn't spelled out anywhere in the handoff or the implementer's
  result (reasonably so; it's exactly what a reviewer is for). Worth noting for future DC4-shaped gates:
  the useful reviewer move here was mutating the *real* door directly rather than only re-running the
  shipped control — the shipped control alone (two different spine files) does not, by itself, prove
  sensitivity to a rendering-side bug against the real shared-file production shape; only mutating the
  actual door does that.
- **Instructions improvised around:** one of my own Bash invocations used backticks inside a
  double-quoted `--finding` string (to typeset `` `python checklist_engine.py current` `` as inline
  code); bash interpreted them as command substitution and silently emptied that one illustrative
  parenthetical in the r12 finding (the substance of the finding is intact; only a short aside lost its
  inner text). Self-inflicted, not a defect in the deliverable or the engine — logging it because a
  future reviewer driving the engine via Bash will hit the same trap if they typeset inline code inside
  a `--finding`/`--summary` argument.
- **What would have made this easier:** nothing structural. The one real friction was environmental
  (the harness's permission classifier reportedly refused the implementer's attempted temporary edit to
  `scripts/mcp_spine_server.py`; my own equivalent edit was **not** refused in this session) — worth a
  note in `checklist-engine.md` or this skill's doctrine that a reviewer's temporary, restored
  mutate-and-watch edit against a "fenced-in-the-final-diff" file is the *expected* verification
  technique for this shape of gate, distinct from a permanent change, so a future permission classifier
  (or a future reviewer second-guessing themselves) doesn't treat the two as identical.

## Return status
`complete`
