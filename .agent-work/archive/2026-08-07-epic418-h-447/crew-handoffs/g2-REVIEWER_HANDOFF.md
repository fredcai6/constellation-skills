# Reviewer Handoff — g2: the replacement capture obligation

## Gate
`g2-review` — issue #447, epic-418 workstream H. Spine `.agent-work/epic418-h-447/execute.json`.

## Survey State Location
Create your review survey checklist at
`.agent-work/epic418-h-447/g2-review/review.json` — under the issue workbench, **never at the
worktree root**.

## Worktree
`C:/Programs/constellation-skills-wt/epic418-h-447`, branch `epic-418/h-447-episodes-retirement`.
This is the only tree you may write to. Use absolute paths; your cwd resets between bash calls.

## What Was Implemented
A **write-side capture gate** that lets the retirement of `.agent-work/LESSONS.md` and
`.agent-work/AGENT_FEEDBACK.md` proceed without leaving a window with no closeout path.

- NEW `scripts/verify_episode_captured.py` — `verify_episode_captured.py <work-id> [--store-root PATH] [--phase feedback|archive]`
- NEW `tests/test_verify_episode_captured.py` — 16 tests, 4 classes
- `scripts/apply_episode_delta.py` — **comment only** at `store_root()`

## How to Inspect the Diff
The review target is the **UNCOMMITTED WORKING TREE**, not `git diff main...HEAD`.
`git status --porcelain` first (the two new files are untracked and `git diff` alone hides them),
then `git diff` for the `apply_episode_delta.py` change. Confirm the comment-only claim with
`git diff -U0 scripts/apply_episode_delta.py` — every added line must be a comment, zero deletions.

## Task Statement
Build the write-path replacement BEFORE the old machinery is removed. The verifier globs
`<store-root>/active/` for episodes whose mechanical `- run:` line matches the work id and fails
if none. Under `--phase archive` it additionally requires `git ls-files --error-unmatch` to
succeed on each matched path, so a run that writes an episode and forgets to `git add episodes/`
genuinely fails.

**THE VALVE — the load-bearing design property, not a detail.** The verifier parses ONLY the
`<!-- episode-state: -->` header and the `- run:` line. It MUST NOT parse or emit any assertion
`statement`, and MUST NOT import `query_episodes`. Ids and counts out; statements never. It
asserts CAPTURE ONLY — no ripeness, no apply-or-defer, no dormancy, no counters; those are
playbook concepts that retire with the playbook.

Full implementer specification: `.agent-work/epic418-h-447/crew-handoffs/g2-IMPLEMENTER_HANDOFF.md`.
Implementer's result: `.agent-work/epic418-h-447/results/g2-IMPLEMENTER_RESULT.md`.

## Close Criteria
Each becomes a review check. **RE-RUN every one yourself** — do not grade the implementer's
transcript. Redirect to a file then `echo $?`; a pipe captures the pipe's exit code.

1. Passes on a seeded store; **fails on an empty store**; **fails on a store holding only other
   runs' episodes**.
2. `--phase archive` **fails** on an episode that exists but is not committed.
3. A missing `active/` directory (or a missing store root) is **refused, not answered as zero**.
4. The sentinel test proves no statement text reaches stdout **or** stderr, **and its own red
   proof shows that test can fail.** Re-run the red proof yourself: inject a leak into
   `scan_episode()`, confirm the sentinel test goes RED, then restore and confirm the bytes are
   identical and the test is green again. A leak test that cannot fail is worth nothing.
5. The verifier does not import `query_episodes` and links to no store reader. Verify the import
   graph directly (`ast` or `python -c "import ast; ..."`) — **a grep false-passes here**, because
   the module's own prose names `query_episodes`.
6. No new failures in the full suite. **See the transient-failure scoping note below before you
   grade this one.**

### Expected transient failure set — scoped by root cause, read this before grading criterion 6
`tests/test_mutation_floor.py` may report up to 10 failures whose message is `HARNESS ERROR: ...
non-zero exit with no FAILED test node`. **Root cause, measured by the Commander:** the harness
regex at `tests/test_mutation_floor.py:255` matches `FAILED (tests[/\\]test_map_orient\.py::\S+)`,
and when the environment forces colour (`FORCE_COLOR` / `PY_COLORS` set, as this session does)
pytest emits an ANSI reset between `FAILED` and the node id, so the regex cannot match. It is an
environment artifact, not a code regression and not caused by this gate.

Run the suite with colour disabled and the class disappears:
`FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` → `tests/test_mutation_floor.py` alone gives
`14 passed, 11 subtests passed`, exit 0 (Commander-measured, `.agent-work/epic418-h-447/evidence/g2-mutation-floor-nocolor.txt`).

A failure matching **that root cause** — the colour-defeated regex, wherever it surfaces — is the
waiver working. A failure **outside** that class is a BLOCK. Do not grade by file name alone.

Also known load-sensitive: `tests/test_crew_launcher.py::LaunchTests::test_records_entry_before_launch_and_completes`
flaked once under concurrent load and passed in isolation. If you see it, re-run it in isolation
before calling it a blocker; a concurrent Commander is running on this box.

## Allowed Scope
**CREATE:** `scripts/verify_episode_captured.py`, `tests/test_verify_episode_captured.py`.
**COMMENT ONLY:** `scripts/apply_episode_delta.py` at `store_root()`.
Nothing else.

## Specific Exclusions — flag if touched
- No spine files, no install bundles, no `scripts/verify_retirement.py` (the g1 guard).
- No `episodes/` content. That store is written ONLY through `scripts/apply_episode_delta.py`;
  a hand-edited episode file is an automatic BLOCK.
- No commits, no git state changes. The Commander commits.
- No change to `store_root()`'s **semantics** in `apply_episode_delta.py` — comment only.

**Expected and NOT a defect:** `scripts/verify_retirement.py`'s `replacement-absent` leg is
currently RED. It names this script and stays red until g3 wires the spines. That was stated in
the implementer's handoff. Do not BLOCK on it.

## Constraints the Implementation Must Respect
Each becomes a review check.

- `python`, **NEVER** `py` — `py` resolves to a runtime with no pytest on this box and produces
  fake greens. This applies to **your own commands** too.
- Windows: `encoding='utf-8', newline='\n'` explicitly on every file write.
- Record stores are never hand-edited: `episodes/` only through `apply_episode_delta.py`. The
  tests must seed **temp** stores, never the real one.
- Scope discipline (Tommy's standing ruling, epic-418): build the thing that needs to work and no
  more. A corner case deliberately not chased must carry a comment **at the code site** naming it
  and be reported up. Verify each of the four declined corner cases the implementer names
  actually has its comment at the stated file:line — that is the sanctioned exit, and a missing
  comment is a real finding.
- Use your own session scratchpad for temp files, **never** `/tmp` — a concurrent Commander run
  shares it and has already polluted one evidence file this epic.
- No Fable at any tier. If you dispatch anything, cap at Opus and name the model explicitly.

## Map Anchors (inbound)
- **Structural:** `struct:docs/EPISODE_STORE.md` — the store's grammar, partition and retirement
  policy (doc level); `struct:episodes/README.md` — the store's own directory doctrine (doc level).
- **Capability:** `capability:episode-store` — `episodes/{active,retired}` +
  `apply_episode_delta.py` + `query_episodes.py`; `capability:run-closeout-learning` — the
  Commander/Admiral feedback step's write path, which this gate becomes the checker for.
- **Constraints/assumptions:**
  - `constraint:episodes-are-not-prescriptions` — Tommy, 2026-08-06: *"we shouldn't be reading the
    episodes like lessons, it's a store for things that happened to replace both feedback and
    lessons."* The store records what happened; nothing may read it back as a rule. **THE
    constraint this whole run exists to honour.** Verify it was not silently violated: a gate
    that can surface episode content is one refactor away from being the playbook again.
  - `constraint:doctrine-lives-in-docs-agents` — a rule to follow belongs in `docs/agents/*`,
    never in the store.
  - `constraint:record-stores-never-hand-edited`.
- **Decision anchors:**
  - `decision:episodes-replace-both` — one store of observations replaces two inboxes plus a
    playbook; no successor playbook is created. `@grade: settled/human`
  - `decision:capture-gate-checks-capture-only` — no ripeness, apply-or-defer or dormancy is
    ported. `@grade: settled/human`
  If you find a contradiction with a `settled/human` anchor, that is a decision candidate to
  float back in your report, not something to revise in place.
- **Evidence expectations:** `claim:suite-no-failures` — the suite reports 0 failed with the
  count delta explained by name (see the transient-failure scoping note above).

## Evidence Produced
From the implementer, for you to **independently reproduce**:

| command | claimed exit |
|---|---|
| `python -m pytest tests/test_verify_episode_captured.py -q` | 0 (15 passed, 4 subtests) |
| `python scripts/verify_episode_captured.py no-such-run --store-root episodes` | 1 |
| `python scripts/verify_episode_captured.py issue-308 --store-root episodes` | 0 (25 of 32 scanned) |
| `python scripts/verify_episode_captured.py issue-308 --store-root /nonexistent` | 2 |
| `python scripts/verify_episode_captured.py issue-308 --store-root episodes --phase archive` | 0 |
| `python -m pytest -q` | no new failures vs baseline |

Exit-code contract as built: **0** captured · **1** BLOCKED (readable store, no such episode, or
archive-phase untracked) · **2** REFUSED (unreadable store, malformed record). The implementer
invented the 1-vs-2 split; the handoff said only "non-zero". Grade whether the split is coherent
and tested, not whether it matches a code the handoff never named.

Mid-run defect the implementer found and fixed, worth confirming the fix holds: `_git_tracked`
passed a **relative** pathspec to git while setting `cwd=path.parent`, so `--store-root episodes`
asked about `episodes/active/episodes/active/<id>.md` and reported all 25 committed episodes
untracked — a false BLOCK. Fixed with `path.resolve()` plus a regression test using a relative
root in a real temp git repo. **Re-run the archive phase with a relative `--store-root` yourself.**

## Suggested Model Tier
**Opus** — the valve is a design property, not a behaviour, and grading it requires reading intent
against the diff. No Fable.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, a policy
decision is required before a verdict is possible, or the valve can be shown to leak.

## Return Format
Write `REVIEW_RESULT` to `.agent-work/epic418-h-447/results/g2-REVIEW_RESULT.md` with:
an explicit **APPROVE** or **BLOCK** verdict on its own line, per-check findings (one per close
criterion and per constraint, each with the command you ran and its **real** exit code), blockers,
out-of-scope observations, and workflow feedback. Deliver the substance as your final message too.
