# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-j` at the wave boundary. Replaces `commander-w4-467-i`'s note
wholesale — that note described `g5-acceptance`, which is DONE and now REVIEWED and INTEGRATED.**

## Where the run is

- **step:** spine `execute` · **`17/17` complete. `DONE: no open items.`**
  `g5-review` complete (verdict **APPROVE**, `blocking_findings: 0`); `g5-integrate` complete on a
  green suite and that APPROVE.
- **The issue is finished at the Commander tier. The wave is HANDED BACK to the Admiral**, who owns
  the PR and the merge. No work was opened beyond the wave.
- **next command for anyone cold-starting:**
  `python C:/Programs/constellation-skills/scripts/checklist_engine.py --file
  .agent-work/issue-467-trip-semantics/execute.json current` — its `DIGEST:` is the handback.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`.
- **engine lease:** released at the end of this session. Claimed during the run with
  `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX` (no `--force`; every agent in this harness session
  shares that id, so `claim` takes the idempotent-resume path). **Verify against the raw JSON, not
  against this line.**
- **suite, my own run at HEAD `6bc971e5`:** `1867 passed, 2 skipped, 829 subtests, REAL exit 0` in
  465s (`evidence/g5j-suite.txt`). Redirected to a file with the exit code read from the pytest
  process — never through a pipe. Same number as `g4-integrate`, `g5-acceptance`, and the g5
  reviewer's independent run.
- **`.agent-work/` is TRACKED in this repository, not ignored.** (`commander-w4-467-i`'s closing
  digest `w-15` says otherwise; the why-trail is append-only so it cannot be edited. `ACCEPTANCE.md`
  §8 carries the same correction.) Nothing under `scripts/` or `tests/` was touched by `g5`; the
  engine blob is unchanged at the value `git rev-parse HEAD:scripts/checklist_engine.py` returns.

## What `g5-review` established

The reviewer ran on **Sonnet**, dispatched through `run_crew.py --dispatch external` as
`constellation/issue-467-trip-semantics/g5-review/reviewer/attempt-1`, result verified
**fresh (completed)**. Handoff and result are in `crew-handoffs/g5-reviewer-*.md`.

It did the thing the dispatch existed for: it **broke the acceptance verifier's inputs itself**
rather than trusting the predecessor's `--self-test` — 11 attacks beyond the shipped nine — and
re-checked that the predecessor's fix to its own check-that-cannot-fail holds. It also independently
reproduced the round trip rather than reading `ACCEPTANCE.md`: the `PROMPT-B.txt` hash and byte
count; the `a1`/`a2` imperatives matching `build_acceptance_spine.py`'s source constants verbatim
with **no engine verb writing the `imperative` field** (which closes the re-briefing hole harder
than the journal can); no A/B overlap from the raw journal; the nonce counts by two independent
methods; the RED non-reproduction, the close-side probe, the DC4 neighbour probe and the anti-vacuity
check all re-run; and #431 and #504 both confirmed **open** on GitHub.

Two real, **non-blocking** gaps it found in the verifier, which I confirmed in source myself rather
than on its word (filed as **tc22**):
- `V1` decides the agents are distinct with bare string equality on session ids, so a case- or
  whitespace-varied id would read as distinct.
- `V8` decides the nonce crossed the seam with bare substring containment, so incidental noise would
  satisfy it.
Neither moves the verdict: the real ids are distinct random hex and the nonce transfer is
independently established by direct counts outside `V8`.

## What is NOT rounded up

- **DC6 is PARTIAL and stays partial.** Both trip lines were observed live in agent B's own prompt
  and the historical line survives the close the HARD band mandates — but at closeout
  `_trip_advisory` returns early on the `gate is None` path and both lines go silent. That is
  `tc19` / **#504**, deferred by Admiral ruling and deliberately not carried into `g5`. The reviewer
  judged the partial **not understated**.
- **DC2 is done-by-different-means**, never done-as-written. The shipped engine draws the line
  between **verbs** (`start`/`reopen` guarded, `advance` never governor-refused), not between two
  modes of `advance`. Outcome delivered; the literal mechanism is not the one that shipped.
- **#431 is verified dissolved, NOT closed.** Closing it is the Admiral's. Same for #504.

## Triage candidates from this gate

`tc22` verifier hardening (V1/V8 above) · `tc23` `check_gate.py` and `verify_round_trip.py` V7
re-implement the same `roundtrip.md` shape rule with separate driftable regexes · `tc24` the engine
journal's hash chain covers **event metadata, not file content**, so it cannot alone prove an
imperative was unedited between two agents — worth a line in the engine reference — and separately,
`record`/`flag-candidate` pass `--finding`/`--statement` through a POSIX shell, so backticks and a
bare `$?` in finding text get shell-evaluated before the engine sees them.

## Rulings that still hold

1. Drive the RUN spine with **MAIN's engine**
   (`C:/Programs/constellation-skills/scripts/checklist_engine.py`). `g5-acceptance` was the
   deliberate exception and exercised the branch engine.
2. Pin the engine by `git rev-parse HEAD:scripts/checklist_engine.py`, **re-derived at the moment of
   use** — never copied forward from any document, including this one.
3. **Never pipe pytest before reading its exit status.** A piped `$?` is the pipe's, and this run
   produced a false green that way once already.
4. The acceptance verifier **stays** at
   `.agent-work/issue-467-trip-semantics/acceptance/verify_round_trip.py`. Promotion to `scripts/` is
   an open follow-on question, ruled out of this gate.
5. **Never let a second Commander into this worktree.**
