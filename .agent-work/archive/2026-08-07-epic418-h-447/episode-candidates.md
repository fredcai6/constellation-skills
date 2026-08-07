# Episode-candidate pool — run `issue-447` (epic-418 workstream H)

Raw observations harvested from each gate's crew Workflow Feedback and from the Commander's own
run. **This is a staging file, not a record.** g4 converts the selected candidates into a delta and
writes them through `scripts/apply_episode_delta.py`, which is the only write path into
`episodes/`. Nothing here is a rule to follow — a rule to follow belongs in `docs/agents/*`
(`constraint:doctrine-lives-in-docs-agents`).

Harvested so far: g1 (implementer + reviewer), g2 (implementer + reviewer), Commander.

---

## C1 — a guard that names the thing it guards fires on itself
**Gate:** g1, surfaced by the reviewer as a BLOCK.
- intent: ship a regression guard that keeps the retirement true.
- expected: a guard authored against the untouched tree goes red on the disease and green after.
- observed: once the guard was tracked, it fired on ITSELF — 12 self-hits plus 6 store-mention
  hits, because its own constants name the retired files. The clean tree could then never go green
  and the xfail marker would have outlived the work.
- cost: one full rework round-trip inside g1.
- workaround: a guard cannot be inside the set it guards. Excluded the guard's own module from the
  scanned surface; staged and working-tree scans now agree at zero self-hits. The test module had
  already applied this principle to `tests/`.

## C2 — an evidence command that exercises the real invocation shape finds what unit tests cannot
**Gate:** g2, found by the implementer while running the handoff's own evidence list.
- intent: verify an episode is durable under `--phase archive`.
- expected: the 25 committed `issue-308` episodes report tracked.
- observed: all 25 reported UNTRACKED. `_git_tracked` passed a relative pathspec to git while
  setting `cwd=path.parent`, so `--store-root episodes` asked git about
  `episodes/active/episodes/active/<id>.md`.
- cost: a false BLOCK that would have failed every real archive gate. Invisible to the unit tests
  because every one of them used an absolute temp path. Caught at m6, not m3.
- workaround: `path.resolve()`, plus a subprocess regression test with a RELATIVE `--store-root`
  in a real temp git repo. The handoff's evidence list had specified a relative root for the
  feedback phase but not for the archive phase — the missing command is exactly the one that would
  have caught it a gate earlier.

## C3 — a leak proof only proves the stream it leaked to
**Gate:** g2, found by the reviewer re-running the red proof with its own mutation.
- intent: prove no assertion statement text can reach stdout or stderr.
- expected: the implementer's red proof establishes the whole assertion can fire.
- observed: the implementer's leak went to stdout only, so the STDERR half of the assertion had
  never been shown able to fire. The reviewer leaked from `matched_episodes()` to stderr and got a
  red, which is what actually established it.
- cost: none realised — caught in review. Had it not been, the valve would have shipped with half
  its guarantee unproven.
- workaround: a red proof must exercise every branch of the assertion it is proving, not one.

## C4 — an informative null: leaking what the code reads leaks nothing
**Gate:** g2, reviewer.
- intent: find a leak the sentinel test would miss.
- expected: echoing the lines `scan_episode()` reads would leak the sentinel.
- observed: it stayed GREEN. Not a hole in the test — the mechanism itself. `scan_episode()` stops
  at the `## Agent-supplied` heading, so statement bytes never enter memory; there is nothing to
  leak from what it reads.
- cost: none. Recorded because it names where the guarantee actually lives.
- workaround: the read boundary is the valve. Print statements are not.

## C5 — a forced-colour environment silently converts real kills into HARNESS ERRORs
**Gate:** g2, Commander, while falsifying the crew's own suite claim.
- intent: confirm the crew's "10 pre-existing failures, identical to baseline" claim.
- expected: either a real pre-existing red, or a regression the crew introduced.
- observed: neither. `FORCE_COLOR=3` in the session environment makes pytest emit an ANSI reset
  between `FAILED` and the node id, defeating `tests/test_mutation_floor.py:255`'s regex
  `FAILED (tests[/\\]test_map_orient\.py::\S+)`. The harness then reports
  `HARNESS ERROR: non-zero exit with no FAILED test node` for 10 mutations that were in fact
  killed. With `FORCE_COLOR=0 NO_COLOR=1` the same file is 14 passed, exit 0.
- cost: two agents (the crew and the g1 session before it) reasoned from a failure count that was
  an artifact of their own terminal. It is fail-loud rather than fail-green, so nothing shipped
  wrong — but while it is red it permanently masks any REAL regression in that file.
- workaround: strip ANSI before matching, or pin `FORCE_COLOR=0` inside `run_floor()`. Triage
  candidate, not fixed here — out of scope for the retirement.

## C6 — a checklist can name a config that does not exist and the engine will not say so
**Gate:** g2, raised independently by both the implementer and the reviewer.
- intent: run the crew plans under the project's engine configuration.
- expected: `config_ref` resolves.
- observed: `docs/agents/engine-config.json` does not exist, yet every checklist in this work area
  names it. The engine accepts the dangling reference silently.
- cost: the rework cap and checkpoint policy are running on defaults nobody chose.
- workaround: none applied. Triage candidate.

## C7 — a Windows text-mode fill of the engine's state file silently rewrites every line ending
**Gate:** g2, reviewer, while filling the reviewer template's `r6-fowler` placeholder.
- intent: fill an unfilled postcondition placeholder the template's own imperative orders you to
  fill, for which no engine verb exists.
- expected: a one-field edit.
- observed: the text-mode write rewrote all 371 CRLF line endings in the engine's state file.
- cost: caught on the diff and reverted byte-for-byte, then redone in binary. Anyone following the
  same instruction on Windows corrupts the work file and does not notice.
- workaround: binary I/O for engine state; and the template gap (an imperative with no verb behind
  it) is itself the defect. Triage candidate.

## C8 — a guard that checks imperatives is checking that an AGENT is told, not that a machine will
**Gate:** g3, implementer.
- intent: clear `verify_retirement.py`'s `replacement-absent` leg by wiring the capture verifier in.
- expected: retargeting the Admiral's `closeout.c2` check command would satisfy the leg.
- observed: it stayed red. `_spine_names_replacement` scans task **imperatives**, not check
  commands.
- cost: one diagnosis cycle inside the gate.
- workaround: the Admiral imperative now tells its agent to run the gate. Not a bug in the guard —
  the leg asserts an agent is instructed, which is a stronger property than a postcondition
  existing, and it is the property #308 lost.

## C9 — a comment citing a line number in its own file is invalidated by the edit that writes it
**Gate:** g3, found by the reviewer.
- intent: name the four measured routes around the unbundled `query_episodes.py`.
- expected: the citation `install_constellation.py:915` would point at the `copytree`.
- observed: the comment's own 18-line insertion pushed `copytree` to 932. The citation was wrong
  the moment it was written.
- cost: none — caught in review, fixed at integrate by naming the symbol `install_skills()` instead
  of a line number.
- workaround: cite symbols, not line numbers, when the citation lives in the file it cites.

## C10 — an approval reason written once for a block of lines describes only some of them
**Gate:** g3, found by the reviewer; **pre-existing, seeded at g1.**
- intent: the `unapproved-store-mention` census approves each shipped mention with a reason, and
  the reason is the thing under review.
- expected: each approved line's reason describes that line.
- observed: `docs/agents/CREW_CONTEXT.md`'s *"Read them with `scripts/query_episodes.py`…"* is
  approved under *"names the store's WRITE path and the never-hand-edit rule"* — a reason written
  once for a block of four consecutive lines and true of three of them. The approved line is a
  READ instruction.
- cost: the run's own guard tells one comfortable lie, in the exact category it exists to catch.
- workaround: g5 must fix the prose **and** the approval entry together; fixing the prose alone
  leaves a wrong reason in the census. Per-line reasons, not per-block.

## C11 — a deny-list entry keeps a retired name on a shipped surface forever, and the guard has no way to approve it
**Gate:** g3, escalated by the implementer, confirmed by the reviewer, Commander's ruling.
- intent: drive `verify_retirement.py` green at g6.
- expected: the `retired-name-on-shipped-surface` leg reaches zero once the prose sweep lands.
- observed: it cannot. `archive.c4`'s `deny_globs` correctly names both retired paths as a
  re-staging block and must keep them; `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` is a frozen
  historical record g5 is required NOT to rewrite (33 of the 117 findings). The leg has no
  approval mechanism at all — `SCOPE_EXCLUSIONS` covers only `tests/` and the guard itself.
- cost: `test_canon_is_clean`'s `xfail(strict=True)` could never XPASS, so the scaffolding would
  have outlived the work — the exact failure g1's own review already caught once.
- workaround: give the leg a reason-carrying approval census mirroring
  `tests/data/store_mentions.approved.txt`. Folded into g5, not g3 — the residual set is only
  knowable after the prose sweep.

## C12 — the store already contains prescriptions; the retirement's own carry is the exception
**Gate:** g4, found by the reviewer while confirming a smaller observation.
- intent: check the migration precedent (`episodes/active/issue-308-001.md`) that the g4 handoff
  pointed the implementer at.
- expected: the precedent demonstrates the record-not-a-rule inversion.
- observed: the precedent's own `workaround` is imperative. Reading all 32 canon workarounds,
  roughly **24 of 32** read as instructions — opening with bare imperative verbs (Answer, Locate,
  Give, Verify, Pair, Run, Use, Replace, Require, Dispatch, Instruct) or carrying "must".
- cost: the eight episodes this run wrote are currently the **only** ones in canon honouring
  `constraint:episodes-are-not-prescriptions`, and the handoff pointed a crew at one of the
  offending records as its model. This run introduced none of it.
- workaround: floated and filed, not fixed. `decision:store-hardening-out-of-scope` makes the
  store's content quality a different job; the remedy is an `amend-assertion` pass over the
  existing records.

## C13 — a negative control asserted a broader predicate than its own stated intent
**Gate:** g4, raised by the implementer as a blocker, root-caused by the reviewer.
- intent: `test_canon_episode_store_untouched` exists to catch a *test run* accidentally writing
  into the canon store.
- expected: writing episodes as the gate requires, then committing, leaves it green.
- observed: it went red between `git add` and the commit. Its docstring says "the working tree
  agrees with the index", but `git status --porcelain` also reports index-vs-HEAD, so any staged
  addition reds it. Every future run that captures episodes hits this.
- cost: one raised blocker, resolved by the Commander's integrate commit. It hides nothing —
  after the commit worktree, index and HEAD all agree, so the emptiness is honest — and the
  control's anti-vacuity guard actually strengthens (40 tracked files instead of 32).
- workaround: a narrower pair is green pre-commit — `git diff --name-only episodes/` and
  `git ls-files --others --exclude-standard episodes/` both empty.

## C14 — an OID-against-HEAD check cannot prove provenance for a file that has no HEAD blob
**Gate:** g4, the reviewer going past the handoff I wrote.
- intent: prove the eight new episodes came from the writer rather than a hand edit.
- expected: comparing blob OIDs against HEAD would settle it, which is what my handoff asked for.
- observed: it cannot — a newly added file has no HEAD blob to compare against, so the check is
  vacuous exactly where it is needed. The reviewer instead replayed `episode-delta.json` into a
  scratch store and got the eight staged blobs back byte-identically.
- cost: none realised; the defect was in the handoff, not the work.
- workaround: OID-against-HEAD proves the *existing* records were not touched; a delta replay
  proves the *new* ones came from the writer. Two different questions, two different commands.

## C15 — deleting one script rippled into seven test files because tests couple to scripts by path
**Gate:** g4, Fowler pass in review; pre-existing.
- intent: delete three retired scripts and prune the tests that load them.
- expected: two test files, as planned.
- observed: 19 failures across four files, found by command rather than by eye. Tests load
  scripts through per-file `importlib` loaders keyed on file path, so a deletion is
  shotgun-surgery by construction.
- cost: the prune widened mid-gate — 13 pruned, 6 retargeted. Six were retargeted rather than
  pruned because their subject was a deleted *template* while the machinery under test survives,
  so pruning would have silently dropped its only coverage.
- workaround: enumerate the blast radius by command before editing. Worth knowing before the next
  retirement.

## C16 — the guard caught its own Commander within a minute of the tree going green
**Gate:** g5, Commander, acting on a judgement call the reviewer routed up.
- intent: remove `curator rhyme-search` from `docs/CONSTELLATION_OVERVIEW.md:40`'s audience column —
  it named a consumer with no implementation (`grep -rn rhyme skills/curator/` returns nothing) and
  was the closest sentence in the whole sweep to a read-back instruction.
- expected: a one-column prose edit with no mechanical consequence.
- observed: `verify_retirement.py` went from exit 0 / 0 bytes to exit 1, and
  `test_every_approved_entry_exists_verbatim` failed. The census records approved lines
  **verbatim**, and it is exactly-covering, so editing an approved line orphans its approval.
- cost: one cycle. The fix was to update the census entry alongside the prose.
- workaround: an approval and the line it approves are one object; editing either alone breaks the
  pair. This is the guard working, and it worked on the person who commissioned it, inside the same
  gate that turned it green.

## C17 — the obvious byte-level baseline for a line-ending check is the wrong one
**Gate:** g5, found by the reviewer, and it nearly produced a false BLOCK.
- intent: verify a doc sweep did not flip CRLF files to LF, having been warned that
  `grep -c $'\r$'` is unreliable on this box.
- expected: comparing the worktree bytes against `git show <rev>:<file>` would settle it.
- observed: that check reported **all 23 changed files as corrupted**. `.gitattributes` sets
  `* text=auto`, so blobs are stored LF by design — the baseline was wrong, not the files.
- cost: none realised; caught before the verdict. The correct baseline is unmodified worktree
  files: 14/14 CRLF, and all 23 changed files 100% CRLF, zero mixed.
- workaround: compare worktree against worktree. A git blob is not a filesystem byte record.

## C18 — an exactly-covering census is a stronger property than a passing one
**Gate:** g5, established by the reviewer beyond what was asked.
- intent: check the new `retired_names.approved.txt` census is honest.
- expected: confirm each of the 53 reasons describes its line.
- observed: it did — 53 entries, 53 **distinct** reason texts, so the block-reason defect that
  seeded this whole census cannot recur in it. The reviewer then measured coverage in both
  directions: 53 approvals against 53 residual sites, zero dead approvals and zero uncovered
  lines, plus a six-property decoy suite showing a reworded near-miss suppresses nothing, the same
  text under a different path still fires, and the path half fires despite an approval.
- cost: none. Recorded because it names what "the census is good" actually means.
- workaround: an approval file passes trivially by approving too much; the property worth checking
  is that it approves exactly the residual set and nothing else.

---

## Not candidates — routed elsewhere

- **Counts carried in prose and never re-derived** ("16 tests" vs 15, "223 lines" vs 245, in both
  the g2 implementer result and the g2 reviewer handoff — the handoff inherited them from me).
  Real, but it is a writing-discipline point for `constellation-how-to-talk`, not an episode.
- **`tests/test_crew_launcher.py::LaunchTests::test_records_entry_before_launch_and_completes`
  flaked once under concurrent load**, passed in isolation and on re-run. Watch, do not record
  until it recurs.
