# Crash-resume state note - issue-456

- **step**: `execute` **COMPLETE - all 11 gates closed**. Next spine step: `reconcile`.
- **PID**: no crew running. Registry clean, 0 unresolved.
- **HEAD**: `9b60562a` on `issue-456/code-map`, pushed, tree clean.

## RESUME HERE - the build is FINISHED. What remains is spine closeout + the PR.

### Do NOT re-run gates. All 11 are closed and advanced.

Numbers at the boundary, all re-run by me at gs-integrate:
- suite **1840 passed / 2 skipped / 701 subtests / 0 failed**, exit 0
- `-k map_tree_freshness` **2 passed**, exit 0
- `python -m scripts.code_map build --root .` then `check --root .`: **7/7, exit 0**
  (**the package CLI is the entry point - there is no `scripts/code_map/build.py`**)
- `git ls-files map/` -> exactly `map/INDEX.md`, `map/ids.jsonl`

### Remaining sequence

`reconcile` -> `triage` (drain **tc1-tc20**) -> `review` -> `feedback` ->
`archive` -> **`release` the lease LAST**. The engine will refuse a premature
release; release is a journaled action, not a claim.

**Then push and open a FULL non-draft PR. Do NOT merge - merge is NOT approved
by the human.** Push and a non-draft PR ARE pre-approved.

### The one open question for Tommy

The map ships as **2 tracked files**, not ~3,975, because the landing zone was
measured (`landing-zone-measurement.md`) and the planned 116-file zone is NOT
stable - one reworded docstring rewrites its module `INDEX.md`. The 2-file zone
is stable and the negative control fires on it. **He can reverse this before the
PR**; if he does, commit the full tree instead. Known accepted limitation: the
entry point's links do not resolve until a build runs.

### Route to feedback (do not lose these)

- **tc18** - a stock close criterion names a build script that does not exist;
  three reviewers each rediscovered it and it had already propagated into my own
  tooling.
- **tc19** - the reuse-a-survey-across-review-rounds convention is written nowhere.
- **tc20 - REFUTED, record the refutation not the claim.** I called the
  `ids.jsonl` freshness assertion a check that cannot fail. The reviewer authored
  a real anchor and took it RED. It CAN fail; the true, narrower fact is only
  that no repo history has ever exercised it. My framing was the stronger claim
  and the wrong one.
- **My `gs` close criterion was unsatisfiable**: `git diff d102c05 -- skills/`
  can never be empty again now that later gates moved other files there. The
  crew caught it and amended in-engine with logged authority. A criterion that
  can never pass is the mirror of a check that cannot fail.
- tc39 (governor trips on orientation cost), tc16, tc17, tc15, the haiku
  measurement, and the Commander-error tally (now fourteen).
- **A crew died silently.** `gs/reviewer/attempt-1` wrote its survey once and
  stopped for 75 min, unresponsive to a nudge; nothing in the harness surfaced
  it - I found it by comparing file mtimes. Abandoned and relaunched as
  attempt-2, which approved. Worth a real liveness signal.

### The rule this run cost five passes to learn

**Branch on the SHAPE** - fixed, known when the case is written - **never on the
MEASURED output**, the thing under test.
