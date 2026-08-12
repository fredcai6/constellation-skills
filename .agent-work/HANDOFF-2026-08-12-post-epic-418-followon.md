# Handoff — what epic-418-followon left behind

Written 2026-08-12 at the close of `epic-418-followon`, for whoever takes the global step back.
Main is at `8734b5e9`, in sync with origin, working tree clean. Suite: 2933 passed, 4 skipped,
1121 subtests, measured in a detached foreign checkout with the spine environment unset.

Two halves: **episodes that happened after the store was written**, and **what I am worried about**.
The second half is the reason this file exists.

---

## Part 1 — Uncaptured episodes

Twenty-one episodes are in the store at `episodes/active/epic-418-followon-001..021.md`. Five more
things happened during closeout and cleanup, after the delta was applied. They are written here rather
than in the store because the run's spine is terminal and the lease is released — minting episodes
against a closed run through a re-claimed lease would put writes after the release, which is the
provenance failure the release-is-last rule exists to prevent. Each is written in the store's own
shape so it can be lifted into a delta without rewriting.

### U1 — Archiving the work areas broke the suite, and grep did not predict it

- **task-intent:** Move this epic's three work areas under `.agent-work/archive/` without breaking
  anything that points at them.
- **expected-behavior:** A grep for the paths would find every dependency, and reading the hits would
  show whether each was a live read or a prose citation.
- **observed-behavior:** The grep found nine files. I read them all as docstrings and prose, and moved
  the trees. Five tests then failed. Two of the hits were live reads — `test_generate_spine.py` opens
  `probe.spine.toml`, and `test_mcp_identity.py` asserts `IDENTITY_TRADE.md` is a file — and
  `probe.spine.toml` carried five more `.agent-work/` paths inside itself that no grep of `*.py` could
  have seen.
- **impact-cost:** One broken suite run, caught immediately. Had the move been committed on the
  strength of the grep alone, main would have gone red on a chore commit.
- **workaround:** The suite was run after the move rather than before the commit only. That is what
  separated the citations from the reads.

### U2 — Eight of my own episodes were written as rules, and the writer's own dry-run passed them

- **task-intent:** Record the epic's observations as episodes, with no rule written for a future agent
  to follow.
- **expected-behavior:** `apply_episode_delta.py --dry-run` validates a delta, so a clean dry-run means
  the episodes are well-formed.
- **observed-behavior:** The dry-run was clean and the capture gate exited 0. A separate guard,
  `verify_episode_observations.py`, then flagged eight assertions across seven episodes as written in
  the imperative — "Bind SPINE_FILE and check the child process command line", "Before carrying an
  issue as unworked, check whether a branch already answers it". Those are rules, which is the one
  thing the closeout instruction says an episode must not be.
- **impact-cost:** Eight records stated the wrong kind of thing. Nothing downstream had consumed them
  yet. The gate that governs the closeout postcondition (`verify_episode_captured.py`) does not run the
  observation guard, so the gate could have gone green with all eight in place.
- **workaround:** Restated through the writer's `restate-assertion` op, which keeps the original
  wording verbatim in each episode's history line rather than replacing it silently.

### U3 — The force-delete refusal

- **task-intent:** Delete every branch whose content is merged into main.
- **expected-behavior:** Sixteen delete cleanly with `git branch -d`; four squash-merged refs need
  `git branch -D`.
- **observed-behavior:** The harness permission classifier refused `git branch -D`. The sixteen safe
  deletes had already succeeded.
- **impact-cost:** Four stale refs remain. Their content is verified present on main, so nothing is at
  risk; the cost is four lines of clutter and a disposition entry explaining them.
- **workaround:** The refusal was recorded and not routed around, and the four refs are named in the
  log and in `STATE_NOTE.md` for a human to delete.

### U4 — Applying a delta leaves the tree dirty, and one test treats that as a failure

- **task-intent:** Apply the episode restatements and confirm the store is healthy.
- **expected-behavior:** Applying a valid delta leaves the store in a passing state.
- **observed-behavior:** `test_episode_negative_control.py::test_canon_episode_store_untouched`
  asserts the canon store has **no unstaged edits**, so it goes red between applying a delta and
  committing it. The window is real but narrow.
- **impact-cost:** An agent that applies a delta, runs the suite, and reads the failure as a defect in
  its own change would chase a ghost. It cost one investigation here.
- **workaround:** Staging the episode files cleared it. Whether that assertion should be scoped to the
  seeded store rather than the canon one is a judgment call for whoever owns that test.

### U5 — The context block cleared by compaction rather than by a fresh agent

- **task-intent:** Close the epic without starting a full retrospective at low context headroom.
- **expected-behavior:** The engine refused `start closeout` at 23% and asked for a fresh agent, so a
  fresh agent would have to run it.
- **observed-behavior:** The gate was blocked with `--authority human` and bubbled. The session then
  compacted, the gauge reported no soft or hard trip on a fresh reading, and the same agent resumed and
  drove the gate to completion.
- **impact-cost:** None measured — the closeout completed and the suite is green. Worth recording
  because the mechanism's stated remedy (a fresh agent) and the remedy that actually applied
  (compaction of the same agent) are different things, and only one of them is written into the
  refusal text.

---

## Part 2 — What I am worried about

Ordered by how much I think it matters, not by how easy it is.

### W1 — 94% of this repo is run scrap, and shipped code depends on it

Measured at `e897bfd1`, **after** the archive sweep in `e4d08fd8`/`b3271ec8`/`c25fcbb0` that took
`.agent-work/` from 63 top-level entries down to 9:

```
tracked files total              8601
tracked files under .agent-work  8105   (94%)
.agent-work on disk              151M   (150M of it under archive/)
top-level .agent-work entries     9
```

**The sweep fixed the layout and did not change the weight.** Tidying moved directories into
`archive/`; it did not delete anything, because everything under `.agent-work/` is tracked. The 94%
figure did not move — it went *up* slightly. If the goal is a smaller repo rather than a tidier one,
the sweep is not the lever.

The part that makes this more than untidiness: **35 shipped scripts and tests build real paths into
`.agent-work/`**, and five modules name a `.agent-work/` path as their "Frozen contract" in the module
docstring. Shipped code depends on run artifacts. That is why archiving three directories in this
session required editing six source files and a fixture, and it means the cleanup you are planning is
not a `git rm` — every sweep is a code change with a suite run behind it.

Worth deciding deliberately: whether `.agent-work/` should be tracked at all, and if the design
contracts those five modules cite should be moved into `docs/` where they belong instead of living in
a run directory that someone will eventually sweep.

### W2 — The door binding is the epic's own unfixed defect, and it will bite the next agent

This session's MCP door was bound to a **wave-1 scratch demo spine**, not to this epic's spine. The
Admiral drove its own closeout through the engine CLI because the door pointed somewhere else. This is
the exact defect the epic was convened to remove, and it landed on the Admiral at its own closeout.

`run_crew.py` now binds `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` per dispatch, so a crew launched
through it is fine. **An agent a human starts at a terminal is not**, because nothing in that path sets
the variable. Anyone picking up work here should call `spine_status` and confirm it names the gates
they expect before trusting a single door call.

### W3 — The repo cannot orient itself, and a commit regenerates the thing that does not work

`map_orient.py` returns `DEGRADED-UNPARSEABLE`, anchor count 0. All five entrypoints miss:
`docs/architecture/generated/map.json`, `docs/architecture/index.md` and `docs/architecture/` are
absent; `map/ids.jsonl` is empty; `map/INDEX.md` has content but carries **no citable anchor id**.

`map/INDEX.md` is 187 lines and commit `c66d2ffa` regenerates it. So there is a generator, a
regeneration step in the workflow, and a consumer that cannot read the output. Every commander that
orients in this repo orients degraded, and has for some time. **This is unfiled** — I reported it in
the log and the summary and did not open an issue, because I could not tell whether the index or the
reader is the wrong half.

Receipt: `.agent-work/archive/2026-08-12-epic-418-followon-closeout/epic-418-followon/map-orientation.json`.

### W4 — Guards that check shape do not check content, and the shape gate is the one on the spine

Three times this epic, a mechanism validated the form of something and a separate mechanism caught that
the content was wrong: the episode dry-run vs the observation guard (U2), the crew's own green suite vs
the foreign-checkout run, five APPROVE verdicts vs the cold review. In each case the gate wired into
the spine was the shape one. The content check ran because someone chose to run it.

I do not have a proposal here. I am flagging the pattern because it is the same shape three times and
the third one nearly merged a red tree.

### W5 — The dogfood feedback loop is dormant and reports green (#566)

All three roots in `docs/DEBT_SWEEP_CADENCE.md` are Windows paths (`C:/Programs/...`) that do not exist
on this Linux host. `collect_feedback.py` skips a root whose export is missing without recording the
skip, so the sweep exits 0 and writes "No new or open candidates" having read nothing. The doc's first
line says it exists to keep the sweep from going dormant.

Filed as **#566**. The scheduled-run recipe in that doc would make it worse — a weekly job writing a
clean report forever.

### W6 — The fifth done-condition does not hold, and the cause is diagnosed but unfixed

Agent-facing instruction still names the engine CLI in **11 files**: 15 `CLI fallback` clauses and 8
live `<engine>` tokens, including **all three orchestrator spine templates**, so every run instantiated
from them inherits the instruction. Two of those clauses assert the CLI is "always available, and the
only path for an in-session dispatched crew member" — both halves are false as of this epic.

- **#559** carries the full re-measurement, the file list, the two tests that pin the removed text, and
  the guard it needs.
- **#565** argues the cause: the workbench skill's teaching half is what the door's tools now carry,
  which is why the clauses grow back after each deletion. It names the blocking question — where the
  skill's four templates live, one of which the admiral spine's own precondition points at.

The instruction has been given three times and grown back twice. The deliverable is a guard, not a
deletion.

### W7 — Smaller, but real

- **Windows CI red since 08-11**, deferred by your decision. The fix for **#555** exists unmerged on
  `fix/mcp-door-launchable`; main's `.mcp.json` still hardcodes `python3`.
- **Four stale branch refs** — `epic-418/f-424-mcp-door`, `epic-418/f2-mcp-adoption`,
  `epic-418/posix-suite-green`, `epic-559/c2-generate-the-spine`. Content verified on main, safe to
  delete, blocked only by the classifier refusal in U3.
- **The episode store only grows** — 134 active, 8 retired. Nothing in this epic retired anything, and
  I did not check whether any of the 134 are stale.
- **#539** still collects the interpreter hardcodes and the installer's rewrite of the tracked
  `.mcp.json`.

---

## Where things are

| what | where |
|---|---|
| epic summary | `.agent-work/archive/2026-08-12-epic-418-followon-closeout/epic-418-followon/EPIC_SUMMARY.md` |
| admiral log | same directory, `ADMIRAL_LOG.md` |
| state note | same directory, `STATE_NOTE.md` |
| terminal spine | same directory, `spine.json` |
| orientation receipt | same directory, `map-orientation.json` |
| episodes | `episodes/active/epic-418-followon-001..021.md` |
| open issues | #559, #565, #566, #555, #539 |
