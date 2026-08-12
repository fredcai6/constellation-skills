APPROVE
blocking_findings: 0

# REVIEW_RESULT — g5-review (issue #467, gate g5-acceptance)

Reviewer session: `constellation/issue-467-trip-semantics/g5-review/reviewer/attempt-1`.
Survey driven through the engine at
`.agent-work/issue-467-trip-semantics/g5-review/review.json` (work_id `g5-review-467`),
consolidated APPROVE, 0 fails. Fowler pass record at
`.agent-work/issue-467-trip-semantics/g5-review/fowler-pass-record.json`
(`verify_fowler_pass.py` exit 0).

## 1. Did the round trip happen?

Yes. Independently reproduced, not accepted on the write-up's word:

- **PROMPT-B.txt**: sha256 `3da641137aa5b7c67bf59c35c6991911a05adb3958458bbbf8f505a98d92f80f`,
  3754 bytes — matches the claim exactly. The block quoted in `ACCEPTANCE.md` §2 is
  byte-identical modulo the one trailing newline a markdown fence swallows (a fence
  artifact, not an edit — confirmed by diffing normalized content, single-character
  delta at the very end).
- **The a1/a2 gate imperatives are unedited job-file content.** `spine.json`'s stored
  `imperative` strings for both gates match `build_acceptance_spine.py`'s `A1`/`A2`
  constants **verbatim** (checked programmatically). No verb in `scripts/checklist_engine.py`
  writes the `imperative` field anywhere (grepped the whole file, no match) — so no `attach`,
  `start`, or `advance` call between A and B could have altered it. `build_acceptance_spine.py`
  refuses a second run (`if SPINE.exists(): return 1`), confirmed by reading its source. Together
  these close the "B was secretly re-briefed" hole harder than the journal alone can: the
  journal's own hash chain (`_journal_hash`) commits only to `(seq, ts, session_id, verb, task,
  evidence_ids, prev_hash)` — event metadata, not file content — so it cannot by itself prove the
  imperative text was untouched. The static-authorship argument above is what actually closes it.
- **No overlap.** Journal: A's last action `attach a2` at 20:08:25.897461Z; B's first action
  `start a2` at 20:11:11.787480Z. Confirmed by reading `spine.json.journal` directly.
- **Nonce containment**, counted myself two ways (git-tracked grep and a full working-tree
  walk, both agreeing): `log-acc-89f734.txt` (A) 0, `PROMPT-A.txt` 0, `roundtrip.md` 1 (written
  by B), `log-acc-7f3d1b.txt` (B) 1, `spine.json` 2 (`why_trail` w-1 and w-2, the legitimate
  transport). A's log redaction is genuinely explained inline (`log-acc-89f734.txt` line 79),
  not silently scrubbed — I read the surrounding text myself.
- **The full suite**: `1867 passed, 2 skipped, 829 subtests, REAL EXIT=0` — my own run, 487s,
  matches the cited number exactly.
- **RED non-reproduction, close-side probe, DC4 neighbour probe, anti-vacuity check** — all
  re-run by me, all matched the cited evidence exactly (details in §5 below).
- **#431 is open, not closed** (`gh issue view 431` — state OPEN). **#504 is open**
  (`gh issue view 504` — state OPEN, tc19's deferred fix).
- **DC2's shipped mechanism** (`TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}`) and **DC6's
  closeout gap** (`_trip_advisory`'s `if gate is None: return ""`) both confirmed directly against
  `scripts/checklist_engine.py` source, matching the write-up's characterization exactly.
- **The crew waiver is real**, not a post-hoc excuse: `execute.json`'s `g5-acceptance` imperative
  itself states "Crew waiver reason: the deliverable is an acceptance MEASUREMENT... a crew
  implementing it would sit between the measurement and the thing measured" — I read this
  independent of the handoff's framing.
- **The gauge-writer confidence-flag correction is right**: `settings.local.json` (outside my
  worktree, read-only) shows `PostToolUse` matcher `"*"` wired to `gauge_writer_hook.py` — the
  writer is wired as an untracked hook, contradicting the gate's own stated `confidence_flags`.

## 2. My own attacks on the verifier

Ran the shipped `--self-test` first (9/9 rejected, exit 0, matches claim), then 11 of my own
attacks against a temp copy of the real inputs, beyond the shipped nine:

| # | Attack | Result | Assessment |
|---|---|---|---|
| 1 | Empty `trip_ledger` + empty `why_trail` | REJECTED by V2 | no vacuous pass on empty |
| 2 | Empty journal entries | REJECTED by V1 | no vacuous pass on empty |
| 3 | Mutate `model` field (never read) — control | PASSED (correctly) | verifier is precisely scoped, not overly brittle |
| 4 | B's session id = uppercase of A's own id | **PASSED — should have been rejected** | **real gap** |
| 5 | B's session id = A's id + trailing space | **PASSED — should have been rejected** | **real gap** |
| 6 | Case-flip the refresh-request `seam` field | REJECTED by V6 | exact match enforced correctly |
| 7 | Deliverable nonce uppercased vs why-record's lowercase | REJECTED by V8 | case-sensitive containment, correctly strict |
| 8 | `fill == hard` exactly (boundary) | PASSED (correctly) | "at/over" correctly inclusive |
| 9 | Duplicate B's own advance entry | PASSED (correctly) | benign noise, not a real break |
| 10 | Extra 7th line after the nonce | REJECTED by V7 | exact-length check works |
| 11 | Nonce present only as incidental substring noise in a doctored why-record | **PASSED — should have been rejected** | **real gap** |

**Two genuine gaps found, neither masked behind an earlier check** (both sail through all 9
assertions cleanly — I confirmed each by running `verify()` directly and checking which
assertions, if any, fired):

- **V1's session-distinctness check is naive string equality** (`first_closer == last_closer`),
  with no normalization or shape validation. A spine where B's recorded id is a case- or
  whitespace-varied copy of A's own id still reads as "two distinct engine session ids acted."
- **V8's nonce-containment check is a bare substring test** (`nonce in why_text`). A doctored
  why-record containing the six hex characters as incidental noise — not as an actual statement
  of the nonce — still satisfies it.

**Neither gap is the predecessor's kind of defect reborn.** I specifically re-checked the fixed
one: `shipped_hard` (hard=0.15 only) is still caught by the earlier `f < h` assertion, not the
override assertion — but `shipped_hard_isolated` (hard=0.15 AND fill=0.2) independently exercises
the override assertion on its own, confirming the predecessor's fix holds and the override check
is no longer unreachable.

**Neither gap changes this run's actual verdict.** The real session ids (`acc-89f734`,
`acc-7f3d1b`) are genuinely distinct random hex with no case games, and the nonce-transfer claim
is independently confirmed by direct count (§1), not solely by V8's assertion. These are verifier
**hardening** findings — filed as triage candidates (tc2), not blockers.

## 3. Prompt-purity check (C1)

Hash and byte comparison done directly (§1). Read the full prompt text for briefing language:
none found — it is exactly the engine's `current` output (RAIL/LEASE/ACTIVE/imperative/
postconditions/DIGEST/REFRESH REQUESTED/CONTEXT/TRIP LEDGER/TRIP HISTORY), the same shape as
`PROMPT-A.txt`. The harder claim — that the gate imperatives inside that output are static
job-file content, not something edited between A and B — is independently confirmed (§1) by
matching `spine.json` against `build_acceptance_spine.py`'s source constants and by confirming no
engine verb writes the `imperative` field.

## 4. Nonce-containment check (C4)

My own counts (§1) match `ACCEPTANCE.md`'s exactly, verified via two independent methods (a
git-tracked grep and a full working-tree walk that includes untracked files — tree was clean at
both points so the two agreed). A's self-redaction in `log-acc-89f734.txt` is visible, explained
in-line, and does not leak the nonce elsewhere in the surrounding text — read directly, not taken
on A's word.

## 5. Per-criterion findings C1–C8

- **C1 — PASS.** See §1, §3.
- **C2 — PASS, with findings.** See §2. The verifier discriminates on all 9 shipped assertions
  and on 8 of my 11 additional ones; 2 real, non-blocking gaps found and reported (V1, V8).
- **C3 — PASS.** Journal timestamps confirm no overlap (A last 20:08:25.897461Z, B first
  20:11:11.787480Z), independently read from `spine.json.journal`, not from `ACCEPTANCE.md`'s
  table.
- **C4 — PASS.** See §4.
- **C5 — PASS.** All six reading-ledger rows (R1–R6) independently reproduced: R1/R2/R3 read
  directly from `spine.json`'s `trip_ledger` (`tl-1`, `tl-2`, `tl-3`, exact fill/hard/model
  values match); R4 confirmed via my own RED repro run (`CONTEXT 30% (>= hard)` printed, all
  three pre-asserts OK before the expected-refusal check); R5 confirmed via my own close-side
  probe run (`CONTEXT 5% (>= hard)`, three moves as claimed); R6 confirmed via my own DC4
  neighbour probe run (`tl-1` naming only `p2`). The planted-vs-live asymmetry (writer silent for
  A, live for B) is stated honestly and I found nothing to add to that characterization.
- **C6 — PASS.** DC2's departure and DC6's partial verdict both confirmed directly against
  `scripts/checklist_engine.py` source (§1). DC1/DC3/DC4/DC5 `done` verdicts all checked against
  their cited evidence and hold. I do not think DC6's partial is understated — it names exactly
  what works (both lines live in-band) and exactly what fails (both go silent at closeout), with
  the issue number and Admiral-ruling deferral stated plainly.
- **C7 — PASS.** Re-ran `repro_431.py --all` myself: exit 1, "NOT reproduced," all three
  pre-asserts OK before the expected-refusal step (which instead completed). Re-running it did
  dirty the tree (13 tracked `red-repro/scratch/` and `transcript-all.txt` files), exactly as the
  handoff predicted as expected residue — I reverted these with `git checkout --` before
  finishing (`git status --porcelain` clean afterward, no CRLF residue).
- **C8 — PASS.** Re-ran `probe_close_side.py` myself: exit 0, all three moves (refuse BEGIN,
  refuse silent close, allow handoff-carrying close) at one reading of 5%. The standing pin
  `test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest` exists at
  `tests/test_checklist_engine.py:3514` exactly as described, asserting
  `_refresh_requests_anywhere(cl) == []` both before (line 3524) and after (line 3534) the
  advance. #431 confirmed open on GitHub; no artifact in this gate closes it.

## 6. Non-blocking findings

- **Fowler pass** (full record at `g5-review/fowler-pass-record.json`, rail-cleared): flagged
  `duplicated-code` (`check_gate.py`'s a1/a2 shape check and `verify_round_trip.py`'s V7
  independently re-implement the identical rule on `roundtrip.md` with separately-authored,
  driftable regexes) and `long-method` (`verify()` is a ~140-line flat sequence of V1–V9, minor,
  organized clearly by comment); overrode `speculative-generality` for the probes' duplicated
  `run()`/`gate()` helpers, citing `references/global-crew.md`'s no-speculative-abstraction
  standard for disposable single-use scripts.
- Two shell mishaps of my own while recording findings through the engine (backtick and `$?`
  inside a `--finding` string got shell-evaluated) cost a few words of cosmetic detail in two
  recorded findings; the substantive content survived intact in both cases.

## 7. Triage candidates

Flagged through the engine (`tc1`–`tc3` on `review.json`):

1. Gauge writer was silent for agent A on the acceptance spine with no skip record explaining
   why (already self-reported in `ACCEPTANCE.md` §0/§7 — restated here for the reviewer record).
2. Verifier hardening: V1's session-id equality should normalize/validate id shape; V8's
   nonce-containment should assert an anchored pattern (e.g. literally "the nonce is `<hex>`")
   rather than bare substring containment. Relevant if/when the verifier is promoted to
   `scripts/` or reused (the promotion question itself is already an open, Admiral-deferred
   decision, not reopened here).
3. `check_gate.py` and `verify_round_trip.py` V7 should share one source of truth for
   `roundtrip.md`'s shape rule if either script is ever promoted.

## 8. Workflow feedback

- The handoff was thorough and load-bearing almost to a fault in a good way — every suggested
  attack (case/whitespace session ids, an unread-field control, an empty-list check) actually
  surfaced something worth checking, which is the right ratio for a review this central.
- One real friction: the checklist engine's `record`/`flag-candidate` verbs pass `--finding`/
  `--statement` straight to a POSIX-shell-invoking Bash call, so backticks and `$?` inside a
  finding string get shell-evaluated before the engine ever sees them. Not a defect in this gate,
  but worth a note for future reviewers writing findings that quote code: avoid backticks and
  bare `$?` in `--finding` text, or write the finding to a file and reference it.
- The journal's hash-chain scope (event metadata only, not file content) is not obvious from
  `checklist-engine.md` and is directly relevant to the "was the imperative edited after A ran"
  question the handoff poses — I had to read `_journal_hash`'s source to learn it does not cover
  file content. Worth a line in the engine reference doc for the next reviewer who reaches for
  the journal as a content-integrity proof.
