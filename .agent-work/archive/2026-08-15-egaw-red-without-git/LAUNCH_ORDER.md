# Launch Order: `egaw-red-without-git` — the RED proof cannot depend on git history

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

Small and precisely scoped. PR #592's production change is finished, correct, verified, and **not in
scope**. One test is blocking it.

## Mission

`tests/test_episode_observation_guard_at_write.py::RedBeforeGreenAfterTests::test_bare_verb_workaround_was_accepted_before_this_change`
fails on Windows CI:

```
subprocess.CalledProcessError: Command '['git', 'show', '2c46cab8:scripts/apply_episode_delta.py']'
returned non-zero exit status 128
cwd = WindowsPath('D:/a/constellation-skills/constellation-skills')
```

**Cause, verified before this order was written:** `.github/workflows/ci.yml:29` uses
`actions/checkout@v4` with **no `fetch-depth`**, which defaults to a **shallow clone of depth 1**. The
runner's object store contains only the merge commit, so `2c46cab8` is not resolvable there.
`load_pre_change()` (`tests/…:64-72`) reconstructs the pre-change writer via
`git show <hardcoded SHA>:scripts/apply_episode_delta.py`, and that cannot work on CI.

This is a **genuinely new failure with a new cause** — it is not the `Author identity unknown` class
already failing on `main` — so it does not pass the merge gate's cause-based comparison. It is the only
thing standing between #592 and merge.

## The real problem with the approach, not just the symptom

Even if you deepened the clone, `PRE_CHANGE_REV = "2c46cab8"` is a **hardcoded commit SHA in a test**.
That is a latent trap independent of CI: it breaks in any shallow clone, in any worktree without that
object, and it silently redefines what "before" means as soon as someone rebases or the branch point
moves. **Fix the approach, not the fetch depth.**

**Do not change `.github/workflows/ci.yml`.** Adding `fetch-depth: 0` would make every CI run clone the
full history to serve one test, and would leave the hardcoded-SHA fragility in place. That is the
workaround, not the fix.

## What the RED actually needs to prove

That **the write-time guard is what does the rejecting** — i.e. the delta this suite now refuses would
have written cleanly through the same code path without the new check. It does **not** require
resurrecting old source to prove that.

Cheaper and more durable options — pick one and defend it:

- **(a)** Exercise the current writer with the guard call neutralized (monkeypatch the guard seam to a
  no-op), assert the delta writes; restore it, assert the same delta is rejected. Same code path, same
  process, no git, and it keeps testing the *seam you added* rather than a historical file.
- **(b)** Split the proof: assert at guard level that `triggers_for` flags the statement, and at writer
  level that the write is refused and names the offending word. The "before" is then carried by the
  guard's own established behavior rather than by old source.

**(a) is the closer match to a true RED/GREEN pair** and I lean toward it, but you are closer to the code.
Whichever you choose, the property that must survive is: **the rejection is attributable to this change**,
not merely present.

## Two things you must not do

- **Do not delete the RED.** A GREEN with no RED proves the test passes, not that the change did anything.
  Losing that property is a worse outcome than the current failure.
- **Do not `pytest.skip` it on Windows or on shallow clones.** `.github/workflows/ci.yml` runs
  `scripts/verify_skip_guard.py`, which **fails the build on any undocumented pytest skip** — so a skip is
  not even available to you, and a documented one would mean the RED never runs on CI at all, which
  defeats its purpose.

## Everything else in #592 is finished — do not touch it

Reviewed and verified by the Admiral: `scripts/apply_episode_delta.py` (+136, the guard call correctly
placed in the *apply* phase rather than `validate_delta`, preserving that function's documented purity
because only apply knows which store is being written), `scripts/install_constellation.py` (+12, required
so the installed writer can import the guard), `tests/data/store_mentions.approved.txt` (+15, mechanical),
and the rest of `tests/test_episode_observation_guard_at_write.py` (+302).

The grandfathered-record decision — a `restate-assertion` against an `EXCEPTIONS`-listed pair stays exempt
— is settled and correct. **Do not revisit any of it.**

## File Ownership

**Yours:** `tests/test_episode_observation_guard_at_write.py`, your work area.

**NOT yours:** `.github/workflows/ci.yml`, `scripts/apply_episode_delta.py`,
`scripts/verify_episode_observations.py`, `tests/test_episode_observations.py`,
`scripts/install_constellation.py`, `scripts/hooks/spine_rail.py` and `.claude/settings.json` (the sibling
lane `stop-hook-door-binding` is live in those), `.mcp.json`, existing `episodes/` records.

## Do not park — run this as your first action

Your process exits when your turn ends; nothing wakes it. The suite auto-backgrounds at ~120s, and
`checklist_engine.py advance` re-runs it during postcondition verification, backgrounding the same way.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write
rm -f /tmp/egawr-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/egawr-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/egawr-suite.log; do sleep 15; done
tail -20 /tmp/egawr-suite.log
```

If something backgrounds anyway, poll with `TaskOutput(block=true)` or `tail`. If you are about to write
"I'll resume when…", that sentence ends your run. **Do not dispatch a crew.**

## Your own closeout episodes

**Your branch now enforces this at write time** — your own change will reject an instruction-shaped
statement as you author it. Past tense, describing this run, not addressing a reader; no clause-opening
bare verb in `workaround` / `proposed-remedy`. If your own writer refuses one of your statements, **say
so in your report** — that is the fix working on its intended target.

Known trap: a verbatim quotation in **single** quotes containing an apostrophe breaks the guard's
quote-pairing and leaks a second-person hit; use double quotes for quoted machine output.

## Evidence required

- The chosen approach, with reasoning for (a) vs (b) or your own alternative.
- Proof the RED still proves attribution — that the rejection is caused by this change — **without git**.
- No hardcoded commit SHA anywhere in the test file. Grep for it and say so.
- Full clean-env cache-clean suite: **0 failed.** Your branch measured **3040 passed, 6 skipped, 1146
  subtests** before this fix; `main` at `2c46cab8` is 3031/6.
- Push to `fix/episode-guard-at-write` so #592's CI re-runs.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write`, **branch
`fix/episode-guard-at-write` — the existing PR #592 branch.** No second PR. Work area
`.agent-work/egaw-red-without-git/`. Archived work areas sit alongside; leave them.

`spine_status` must describe `egaw-red-without-git` — if not, stop and report.

## Stop Conditions

- The RED cannot be proven without git history — that is a finding, report it rather than deleting the test.
- Green would require a skip, a workflow change, or touching anything in the not-yours list.
- The suite shows any failure other than what you are fixing.

## Return Shape

What `spine_status` resolved to, named explicitly; the approach and why; the attribution proof; grep
confirmation that no hardcoded SHA remains; clean-env suite counts; the commit SHA; and confirmation you
pushed with #592 open and unmerged.

**You are fenced from merging.** The Admiral merges.
