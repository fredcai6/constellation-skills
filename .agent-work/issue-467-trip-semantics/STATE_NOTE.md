# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-g` at the `g4-integrate` seam. Replaces `commander-w4-467-f`'s note
wholesale — its content is either carried below or is now done.**

## READ THIS FIRST — g4-review is CLOSED with a BLOCK. The rework has NOT been started.

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g4-integrate` — `pending`, NOT
  started.** **13/17 complete:** `e0-context`, all three `g1-*`, `g2-*`, `g3-*`, `g3b-glossary`,
  `g4-implement`, `g4-review`. `amendments: 2`. 17 gates. Remaining 4: `g4-integrate`,
  `g5-acceptance`, `g5-review`, `g5-integrate`.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`.
- **engine lease:** **RELEASED** on both `spine.json` and `execute.json`. Claim each **without
  `--force`** — every agent in this session shares `session_01TTKPTbD6nnMt7jFWw9GtjX`, so `claim`
  takes the idempotent-resume path. Mutating verbs need
  `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX`. **Verify with the raw JSON, not with this line.**
- **pid:** none — foreground, nothing running. Crew backend is `external` (record-only registry +
  Agent-tool subagent), so there is no process to kill or resume.
  `recover_crews.py issue-467-trip-semantics` → 11 crews, **0 unresolved**.
- **refresh-request:** `e-g4-review-2`, concrete **`why_ref=w-12`**. Read the raw `why_trail` for
  yourself; do not trust this line.
- **next command:** claim both leases, then **`start g4-integrate`** and run the rework. The verdict
  is `BLOCK`, so `g4-integrate`'s job is **return for rework**, not closeout.

## Why I stopped here

I crossed **hard** (fill **0.169769** ≥ **0.15**, my own fresh reading) while closing `g4-review`. I
closed that gate carrying my full understanding and stopped. The rework is **new work** and `start`
is a **begin-work** verb — opening a gate at/over hard is the exact violation this issue's fix
refuses. **This is a clean seam, not an interruption.**

**This is the SECOND live #431 on this run.** The pre-#467 engine driving the spine refused the
`advance` that *carries the handoff* — the exact defect this branch fixes — and I released it the
engine's own prescribed way with the concrete `why_ref=w-12`. **Two live specimens now exist, both
to Commanders, both on the real spine.** See "Open, for the Admiral".

## THE BLOCK — read this before you touch anything

**B1: the close the HARD band ORDERS the agent to make is guaranteed to clear the compliance signal,
and the shipped line says the opposite.**

Three shipped mechanisms compose:

1. at/over hard, `advance --mechanical` is refused, so the **only legal close is `advance --why`**;
2. that appends a **new why-record**;
3. `begin_over_line_records` matches only entries keyed to the **live** why-record.

So **the mandated close supersedes every ledger entry at once.**

**I reproduced this myself** with the reviewer's own probe
(`.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py` — run it, it takes seconds).
At gauge 0.20 / hard 0.15:

| after | selector | rendered line |
|---|---|---|
| a refused begin at `g2` | 1 | present |
| a released begin at `g2` | 2 | present |
| **the same agent closes `g2`** | **0** | **gone** |

Across a 3-gate runaway with **3** over-the-line begins on disk, the rendered line peaked at **2**
and was **ABSENT AT THE SEAM** — byte-identical to a compliant agent that closed and stopped.
**Green in both worlds, at exactly the place the next reader looks.**

The engine's own line ends *"Closing this gate does not clear the record."* I closed that gate and it
vanished. The schema doc says the understanding moves on when *"a fresh agent records its own
`why`"* — **the mechanism cannot tell a fresh agent from the offender**, and the offender's own close
is the likeliest superseder in exactly the runaway the ledger was built for. Their own test
`test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` runs **byte-for-byte the
offender's path** and labels it "a fresh agent" in a comment — **it pins the defect as intended
behaviour.**

### The fix space — narrow, cheap, and the keying is NOT in it

**The reviewer explicitly does not ask the keying to change: close criterion (b) is correctly
implemented.** Three cheap exits, and they compose:

1. **Correct the sentence** to what is true.
2. **Declare this limit as plainly as the other three are declared** (the three existing ones are
   present and honest — this is criterion 5's actual failure).
3. **Render a HISTORICAL read alongside the live one.** Every entry is already on disk and the ledger
   is append-only, so **no new state is needed** — and it keeps `(b)`'s live-keyed predicate exactly
   as frozen while letting the observable survive the supersede.

**My recommendation to the rework implementer: do all three**, because (1)+(2) alone leave the
observable honest but *defeated at the seam*, which is DC6's one job. **(3) is an addition to frozen
criterion (b) — I floated it to the Admiral and the answer had not arrived when I tripped.** If the
Admiral reverses it, dropping the historical clause is a one-line change; ship (1)+(2) regardless.

## WHAT ELSE THE REVIEW FOUND — all of it good news

- **17/17 defect shapes discriminate**, constructed by the reviewer itself with hand-built spines,
  clock-stamped gauges and real CLI subprocesses.
- **19/19 mutations re-run and killed**, tree clean after every revert.
- Write-site claim and its `ast` method independently verified; every evidence number reproduced.
- **A1 — keep `why_ref`, but the evidence offered for it was wrong.** N7's 12-test blast radius is
  *coupling*, not load-bearingness. The real argument is that the supersede rule cannot be replayed
  from the trail. (My float to the Admiral on A1 still wants answering, but both the reviewer and I
  land on **keep**.)
- **A3 — the declared TDD deviation STRENGTHENS the guarantee.** A5 — the `amend` record is honest.

## TWO CORRECTIONS AGAINST MY OWN HANDOFF — carry them, they are fair

1. **The shape count is 12 numbered rows, not 11.** My handoff said 11 and told the reviewer to count
   for itself. It did. One that trusted the number would have under-constructed by one and never
   known.
2. **My trap-6 engine byte-size (156060) matches nothing on disk** — the file is **161503** bytes in
   this CRLF checkout and **158377** as a blob. A size that cannot confirm you have the right file is
   useless for the one job a size has. **Use
   `git rev-parse HEAD:scripts/checklist_engine.py` instead** — and note this is exactly the
   checkable pin **`g5` is required to produce**, so it solves two problems.

## MODEL TIERS — Admiral ruling, binding

Sonnet by default; **Opus needs a named reason in the dispatch**.

- **`g4` rework implementer — Sonnet.** The target is demonstrated and narrow (a sentence, a declared
  limit, one extra render clause over state that already exists). The g3 rework ran this way against
  a demonstrated target and did it cleanly.
- **The g4 re-review — Opus** (adversarial-review carve-out). It must re-run
  `probe_clearing.py` itself and confirm the seam is no longer silent.
- **`g5-review` — Opus.**

## BASELINES — pinned to the commit they were measured at

| Command | At parent `9997c32d` | At `f74ef422` (g4 head) |
|---|---|---|
| `pytest -q tests` | **1833 passed, 2 skipped, 808 subtests** | **1858 passed, 2 skipped, 821 subtests** |
| `pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'` | **exit 5**, 384 deselected | **25 passed, 384 deselected, 13 subtests** |

Delta **+25 passed, +13 subtests** — exactly the selector's own collection, and the 384 deselected is
unchanged, so all 25 tests are genuinely new. **I measured every one of these myself.**

**Standing handoff rule, twice-reported and now applied twice:** a criterion asking for a suite delta
must name the **diff's parent commit**. Do not restate a baseline without the commit it was measured
at.

## WHICH ENGINE — Admiral ruling, settled, do not re-litigate

`installed workbench` / `main` — **no fix**. `branch worktree` — **HAS the fix**.

- **Drive the spine with `python C:/Programs/constellation-skills/scripts/checklist_engine.py`**
  (main's). **Do not switch the driving instrument mid-run** — that is plan surgery.
- **`g5-acceptance` is the exception and the point:** it must exercise the **branch worktree** engine
  explicitly and **pin the binary by hash** (`git rev-parse HEAD:scripts/checklist_engine.py`),
  naming which one it ran. Acceptance evidence produced through a pre-#467 bundle proves nothing.
- **Do not reinstall anything.** Both installed bundles are pre-#467; that goes to closeout.

## STANDING TRAPS — do not spend context rediscovering these

1. **#431 is instruction-conformance, not a deadlock.** A test worded *"the advance is no longer
   blocked"* passes in **both** worlds. **Verify on what the agent is TOLD.**
2. **DC6's observable is "did anyone BEGIN work while over the line"**, never "did a handoff artifact
   appear" — that is true by construction.
3. **The gauge is discarded if `observed_at` is in the future (clock skew) or older than 30 minutes**
   — it collapses to "no gauge" and any scenario built on it goes **vacuously green**. Generate
   fixture timestamps from the clock.
4. **A negative-only test cannot fail.** Ask of every test: *what would this do if the mechanism were
   deleted?*
5. **The printed `<why-id>` placeholder is literal** — attaching it verbatim exits 0 and silently
   does nothing. Read the real id from the raw `why_trail`.
6. **`main()` does not save on `current`.**
7. **Write reviewer handoffs in `APPROVE` / `BLOCK`.** Every `*-integrate.c3` matches that literal.
8. **`execute.json["tasks"]` is a dict keyed by id; `["items"]` is a list of id STRINGS.** Iterating
   `items` gives you strings, not tasks.
9. **A grep for `^FAILED` misses pytest's `SUBFAILED` lines.** The g4 reviewer's `FAILED`-only regex
   produced two apparent mutation survivors that were not. A `FAILED`-only distribution command can
   manufacture a false BLOCK on this suite.

## SANCTIONED METHOD for re-running mutations — keep using this one route

Commit first; apply the mutation directly to `scripts/checklist_engine.py`; run the **named** test;
**revert with `git checkout -- scripts/checklist_engine.py`** and confirm `git diff --stat` is clean
before the next. Scratch probes go under the crew's **own** review directory. **Do not** use
`git archive` temp trees — no cross-commit baseline is needed here and a tree with no `.git` produces
constant git-oracle noise. Both g4 crews used this route cleanly; it resolved a tension that caught
two reviewers in a row.

## TRUST ORDER

1. The raw task JSON and `current` — **authoritative**.
2. This note — a *pointer*, correct only as of its timestamp.
3. `MISSION_FRAME.md`, `LO-467.md` — **stale until proven otherwise**.

## OPEN, for the Admiral — carry these up, do not decide them

- **Whether the rework may add a HISTORICAL render** (fix-space item 3). It is an addition to frozen
  criterion (b). **Floated; unanswered when I tripped.** Ship (1)+(2) regardless.
- **A1 — the ninth field `why_ref`, which reverses critic-panel finding 14.** Floated; unanswered.
  Both the reviewer and I recommend **keep** — but the reviewer **rejects the evidence originally
  offered** (N7's 12-test radius is coupling, not load-bearingness).
- **THE g5 QUESTION, now much stronger and still unanswered: two live #431 trips have now happened
  to Commanders on the real spine** — `commander-w4-467-f` at `g3-integrate` and me at `g4-review`.
  `g5-acceptance` plans a *staged* round trip with two dispatched agents. Real ones already
  happened. **May they be cited as acceptance evidence?** g5's scope is frozen, so it is not the
  Commander's call. **This is the one I most want answered** — it is two gates away.
- **The stale installed engine bundles** — reinstall at closeout, or rule that the run continues on
  them deliberately.
- **`decision:execute-gate-reserve-value` (30000) is `@grade: guess` and its authored settle
  experiment is NOT RUNNABLE** — confirmed independently four times. **Cheaper replacement, ready to
  route:** log `(gate, fill_fraction)` at each gate boundary.
- **`docs/CHECKLIST_SCHEMA.md` under-documents the Task object by one optional key**
  (`context_headroom_tokens`). Natural home is this run's `reconcile` step.

## TRIAGE CANDIDATES — `tc1`–`tc13` are now ALL on `execute.json`

I flagged the g4 candidates into the engine rather than leaving them in survey files, because "the
survey candidates get missed" has bitten this run twice. **`tc1` CLOSED** (shipped as
`g3b-glossary`), **`tc3` RESOLVED** (the parent-commit baseline). Live: `tc2`, `tc4` (`block()`'s
missing status guard — **pre-existing, not ours, and the M15 kill now DEPENDS on that state**),
`tc5`, `tc6` (survey sidecar collision), `tc7` (a lint for the `| tail` class of unfailable check),
`tc8` (the `git status`/`git diff` renormalization disagreement that silently drops a test target),
`tc9`–`tc13` (from the g4 review: `--authority` accepts any string so "human ratification" is
enforced by nothing; N15/N16 share one point of coverage; a crashing mutation is not a kill; the Trip
section assembles the band judgment by hand at three sites; `outcome` is a bare string).

**Still only in survey files:** `g3-review/review.json` (5, including `thresholds_for`'s docstring
overclaiming "for every input") and `g3-rework-review/review.json` (2).

## If you trip

Commit at the seam, file the `refresh-request` with the **concrete** why-id from the raw `why_trail`,
rewrite this note, release **both** leases, go idle. **Nine predecessors have now done this cleanly
and none lost work.** Do not push through, and **do not `start` new work over the line.**
