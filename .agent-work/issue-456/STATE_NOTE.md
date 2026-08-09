# Crash-resume state note - issue-456

- **step**: `execute` (in-progress) - **slug**: **`gs-review` - reviewer crew DIED, must relaunch**
- **PID**: crew `constellation/issue-456/gs/reviewer/attempt-1` is registered `running` but is **DEAD**.
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/gs-review-RESULT.md` (never written)
- **handoff (reusable as-is)**: `.agent-work/issue-456/crew-handoffs/gs-review.md`

## RESUME HERE - the build is DONE and pushed. Only the final review is missing.

### First action: clear the dead crew, then relaunch

`gs/reviewer/attempt-1` wrote its survey once at 20:46 (stuck on `r0-context`
`in-progress`) and never wrote again. A `SendMessage` nudge at 21:47 produced
nothing. It is dead, not slow. Its registry entry will REFUSE a duplicate
launch, so:

```
python scripts/run_crew.py --abandon constellation/issue-456/gs/reviewer/attempt-1
python scripts/recover_crews.py issue-456        # expect 0 unresolved
```
Then relaunch as `attempt-2` with the SAME handoff
(`.agent-work/issue-456/crew-handoffs/gs-review.md`) - it is complete and needs
no edits. Note `--abandon` is correct here **because the crew genuinely failed**;
do NOT use it on a crew that finished (use `--verify-result` for those).
The stale `.agent-work/issue-456/gs-review/review.json` from the dead run should
be discarded, not appended to - attempt-2 is a fresh survey, as its handoff says.

### State of the work: 10.5 of 11 gates

Everything below is committed and pushed at **`e77ccb89`** on branch
`issue-456/code-map`. Working tree clean.

- **g8 CLOSED** - implement, review (APPROVE on the 4th pass from the reviewer
  that BLOCKed three times), integrate all advanced.
- **gs build DONE and Commander-verified**, `gs-implement` advanced. Only the
  review + integrate remain.

### Numbers, all re-run and current

- suite **1840 passed / 2 skipped / 701 subtests / 0 failed** (1838 baseline + 2 new)
- `python -m scripts.code_map build --root .` then `check --root .`: **7/7, exit 0**
- `git ls-files map/` -> exactly **`map/INDEX.md`, `map/ids.jsonl`**
- four skills paths scoped diff vs `d102c05`: empty; `cycle-3.json` untouched
- **build entry point is the package CLI.** There is no `scripts/code_map/build.py`.

### The landing zone was MEASURED - see `landing-zone-measurement.md`

The planned 116-file zone is **NOT stable**: one reworded docstring rewrites its
module `INDEX.md`. The **2-file** zone (`map/INDEX.md` + `map/ids.jsonl`) **IS**,
and the negative control fires on it. So 2 tracked files ship, not 3,975, and
critic F9's repo-doubling objection retires outright. **Flagged to Tommy; he can
reverse it before the PR.** Known, accepted limitation: the entry point's links
do not resolve until a build runs.

### Owed after the reviewer returns

`attach` review-result -> attest `c1` -> `advance` **gs-review**; then
**gs-integrate**: attest `p1`, `start`, attach review-result, attest `c2`
(verdict APPROVE), run the c1 command yourself, then `advance` (c1 is
command-kind - satisfied BY `advance`, never by `attest`).

Then: `reconcile` -> `triage` (drain **tc1-tc20**) -> `review` -> `feedback` ->
`archive`. **Release the lease LAST.**

**Push and open a FULL non-draft PR. Do NOT merge - merge is NOT approved.**

### Route to feedback

tc18 (a stock close criterion naming a build script that does not exist - three
reviewers each rediscovered it, and it had already propagated into my own
tooling), tc19 (the reuse-a-survey-across-rounds convention is written nowhere),
tc20 (the `ids.jsonl` half of the new freshness test compares empty to empty -
the sixth check-that-cannot-fail on this run and the first shipping green),
tc39 (governor trips on orientation cost), tc16, tc17, tc15, the haiku
measurement, and the twelve-Commander-error tally.

**Also mine, found this session:** my `gs` close criterion
`git diff d102c05 -- skills/` is **unsatisfiable** - later gates legitimately
moved other files under `skills/`. The crew caught it, amended in-engine with
logged authority, and told me. A criterion that can never pass is the mirror of
a check that cannot fail.

### The rule this run cost five passes to learn

**Branch on the SHAPE** - fixed, known when the case is written - **never on the
MEASURED output**, the thing under test.
