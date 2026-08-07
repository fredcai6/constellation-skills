# RESUME ADDENDUM — issue-304 gate g2, implementer attempt-2

Read this **first**, then `g2-implementer-handoff.md` (unchanged; it is still your assignment).
Where the two conflict, this file wins.

## You are a relaunch into a live plan file, not a fresh start

Implementer attempt-1 died on a **session usage limit** — not a stall, not a refusal, an external
ceiling. Its last engine journal entry is `2026-08-01T23:39:46Z` (`start m2`); its last file write is
`2026-08-01T23:44:23Z`. It is confirmed dead. **You are alone in this worktree.**

Its work was uncommitted at death and the Commander committed it as-is:

```
6d35fe2  gate g1(#304): map_orient resolver, receipt, and REPORTED degraded mode   <- g1, APPROVED
fdec654  gate g2(#304): re-anchor map-first ... (WIP, resumed)                      <- attempt-1's g2 work
```

`git diff 6d35fe2 fdec654` is exactly attempt-1's output. Nothing in it has been reviewed.

**Your job file is `.agent-work/issue-304/g2-implementer-plan.json`.** Cold-start from its `current`.
Never hand-edit it. Its lease `g2-implementer-304` is held by the dead agent and is stale — take it:

```
py C:/Users/fredc/.claude/skills/constellation-implementer/scripts/checklist_engine.py \
   --file .agent-work/issue-304/g2-implementer-plan.json \
   claim --session-id g2-implementer-304b --force --reason "attempt-1 died on a session usage limit"
```

(If that path does not exist, use the engine at
`C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py` — same engine.)
Pass `--session-id g2-implementer-304b` on **every** mutating call.

## Plan state vs. filesystem state — they disagree, and that is the whole problem

The plan records: `m0-context` complete, `m1` complete, **`m2` in-progress**, `m3`–`m6` pending.

The filesystem records more. Attempt-1 wrote m2's implementation (`cmd_verify_frame` + 18 tests) and,
by its own m1 digest — *"m1's authored gate command runs the whole wiring file, so the template wiring
and installer registration (m4/m5 substance) had to land here too — recorded as a deviation"* — parts of
m3/m4/m5 as well. The Commander measured at resume:

```
python -m pytest tests/test_map_orient.py -q      -> 68 passed, 39 subtests passed
python scripts/map_orient.py --self-test          -> exit 0
```

That is m2's `c2` command, and it is green.

**Do not re-implement what exists. Do not trust it either.** For each remaining slice your first act is
an audit against the handoff's deliverables: does the landed code actually do what deliverable 1/2/3
demands, or only enough to make attempt-1's own tests pass? Attempt-1 was never reviewed and never
finished. If you find a gap, fix it and record it.

## THE ONE THING THIS ADDENDUM EXISTS TO SETTLE: the TDD-red postconditions

Every slice's `c1` reads *"TDD red: <test> written and observed FAILING **before** <X> exists."*
For m2 — and for whichever of m3/m4/m5 attempt-1 already landed — **X now exists.** You cannot observe
that red in TDD order, and you must not attest as though you had. Fabricated evidence is a forbidden
exit; so is quiet abandonment.

**The sanctioned substitute — use it, and record it as a deviation:**

Reconstruct the red against a tree in which X genuinely does not exist. `6d35fe2` is exactly that tree.

1. Revert only the implementation file under test:
   `git checkout 6d35fe2 -- scripts/map_orient.py`
   (for a wiring slice: `git checkout 6d35fe2 -- skills/commander/templates/COMMANDER_SPINE.template.json`)
2. Run the specific new tests. **Observe and paste the genuine failure**, with the count.
3. Restore: `git checkout fdec654 -- <same path>`
4. **Verify the restore by blob OID, never by raw bytes** — Windows `core.autocrlf` makes working-tree
   bytes differ for identical committed content, and it has bitten three agents this epic:
   ```
   git diff --quiet HEAD -- <path>   # must exit 0
   git status --porcelain -- <path>  # must be empty
   ```
5. Re-run the slice's `c2` command to confirm you are green again **before** advancing.

This proves the property the `c1` conditions exist to prove — *the test discriminates; it can fail* —
which is the epic's stated method bar (*"a check that cannot fail is indistinguishable from one that
passed"*). It does **not** prove TDD authoring order, and you must not claim it does.

When you attest such a `c1`, say so in the note, verbatim shape:
`"red reconstructed against 6d35fe2 (a tree without <X>), not observed in TDD order — attempt-1 died before attesting; N failures pasted"`

For any slice whose implementation does **not** yet exist (m6's new mutation is the clear case, and
possibly parts of m3), **write the test first and observe the real red normally.** The reconstruction is
only for work attempt-1 already landed.

## What is still genuinely unstarted

- **m6** — extend the mutation floor against `verify-frame`. New work. Keep the **applied-before-red**
  discipline: assert the substitution landed via a **strict count delta**, and make a non-matching anchor
  raise a loud harness error rather than be credited as a kill. A no-op mutation and a killed mutant both
  yield green; only the count delta tells them apart.
- **m6 c3** — write `IMPLEMENTER_RESULT` to `.agent-work/issue-304/crew-handoffs/g2-result.md`.

## Free fix, take it only if it costs nothing

g1's re-review left one honest survivor: `CONTENT_HASH_RE` in `scripts/map_orient.py` uses `{64}` where
`{64,}` is correct (a longer-than-64 digest currently slips the pin). One token. If it is free, take it
and say you did; if it drags anything, leave it and say that instead.

## Commit as you go

Attempt-1 lost nothing only because a human-directed commit caught it. **Commit after each slice closes**
— `git add -A && git commit -m "g2 m<N>(#304): <what>"`. Do not leave a slice's work uncommitted.

## Constraints that have already cost this epic real time

- `python -m pytest`, **not** `py -m pytest` — `py` is 3.12 (CI's pin) but has **no pytest**; `python` is
  3.14 with pytest. Neither reproduces CI. **No 3.13+-only APIs**: `Path.read_text(newline=...)` passed
  locally and cost 39 CI failures on PR #320.
- Windows: write files with explicit `encoding='utf-8', newline='\n'`.
- **Do not point any tooling at `C:/Programs/f1Brainz`** — `orient` WRITES a receipt into whatever
  `--root` it is given, and that repo is read-only. Use a temp fixture.
- Do not touch `C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.
- `--finding` text containing backticks is shell-mangled and silently drops words. Avoid backticks in
  engine findings; `--note` takes the verification text.

## Stop conditions (in addition to the handoff's)

Stop and report if the reconstruction method above cannot produce a genuine red for some slice — that
would mean the test does not discriminate, which is a finding, not a nuisance. Report **"this specific
check failed"**, never "this approach is impossible."

## Return

Write `IMPLEMENTER_RESULT` to `.agent-work/issue-304/crew-handoffs/g2-result.md` with evidence pasted
verbatim, **every deviation and its reason** (the reconstructions are deviations — list them), and any
unresolved blocker. Only claim a cleanup you have verified.

**`g2-result.md` on disk is the contract** — your Commander polls for it and verifies it with
`run_crew.py --verify-result`. Write it before you end your turn, and make your final assistant message
the same verdict in short form. An idle turn with no result file on disk reads as stalled, not done.
