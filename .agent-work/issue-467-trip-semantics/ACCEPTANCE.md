# ACCEPTANCE — issue #467, trip semantics (gate `g5-acceptance`)

Written by `commander-w4-467-i` at HEAD `cc4aed99`, branch `epic-418/a2-467-trip-semantics`.

**Engine under test, pinned by hash re-derived at the moment of use:**
`git rev-parse HEAD:scripts/checklist_engine.py` → `c281cb68eaac65d1169dd6737a6a322728df98eb`.
The acceptance round trip exercises that BRANCH engine. The run's own spine is driven with
MAIN's engine, which is the deliberate split this gate inherits.

**Full suite at `cc4aed99`, my own run:** `1867 passed, 2 skipped, 829 subtests, REAL exit 0`
(`evidence/g5-suite.txt`). Matches the g4 number exactly.

---

## 0. NO ABSENCE IS EVIDENCE — the reading ledger

Every claim below about trip behaviour is preceded here by the reading that was in force,
quoted from a record the **engine itself** wrote. Nothing in this document infers a trip from
the absence of one.

| # | Event | Reading in force | Line judged against | Source of the reading | Where the engine recorded it |
|---|---|---|---|---|---|
| R1 | A's `start a1` released | fill **0.05** | hard **0.001** | **planted by me** | `trip_ledger` `tl-1` |
| R2 | A's `start a2` refused | fill **0.05** | hard **0.001** | **planted by me** | `trip_ledger` `tl-2` |
| R3 | B's `start a2` released | fill **0.0359** | hard **0.001** | **live, harness-written** | `trip_ledger` `tl-3` |
| R4 | RED re-run, `advance` allowed | fill **0.30** | hard 0.15 | planted by the repro | engine printed `CONTEXT 30% (>= hard)` |
| R5 | close-side probe, all three moves | fill **0.05** | hard **0.001** | planted by the probe | engine printed `CONTEXT 5% (>= hard)` |
| R6 | DC4 neighbour probe | fill **0.05** | hard 0.001 (p2) / 0.15 (p1) | planted by the probe | `trip_ledger` `tl-1`, naming p2 only |

The engine writes `fill`, `hard`, and `model` into **every** `trip_ledger` entry, so each row
above is a reading that provably existed at that moment, not one reconstructed afterwards.

### The planted-vs-live split, stated exactly

The gate's `confidence_flags` say: *"#458: the gauge writer is not wired in tracked settings, so
every reading in this acceptance is planted rather than harness-produced."* **Half of that is
right and the half that is wrong matters.**

- **Right:** no *tracked* setting wires the writer.
- **Wrong:** the writer **is** wired, as a `PostToolUse` `*` hook in
  `C:/Programs/constellation-skills/.claude/settings.local.json`, which is untracked — and it
  demonstrably fires. I proved it live rather than inferring it from the file: when I ran
  `current` the run's gauge held `0.155212 @ 19:44:55Z` (my predecessor's trip reading); I claimed
  the lease, and on my next tool call the hook overwrote it with `0.058956 @ 19:55:24Z` carrying
  `identity_resolution_ms`, i.e. it took the dispatched-agent path and resolved **my** agent id.

So on this run's own spine the governor is live and harness-produced, and the three #431 trips
this run recorded were real readings, not plants.

On the **acceptance** spine the picture is mixed, and I report it as observed rather than
smoothing it:

- **Agent A: the writer stayed silent.** Through A's whole window the acceptance gauge still held
  my plant (`0.05 @ 20:04:58Z`). No fresh record, and **no skip record either** — so I cannot say
  *why* it was silent, only that it was. R1 and R2 are therefore judged against a planted number.
- **Agent B: the writer produced live readings.** `tl-3` records fill **0.0359**, which is not my
  plant (0.05), and the gauge file afterwards reads `0.038176 @ 20:11:31Z` **with**
  `identity_resolution_ms` — the dispatched-agent path, B's own fill. B's release over the line was
  judged against B's **own live harness-produced reading**.

Naming which of the two I observed, as the constraint requires: **the governor was not silent —
it fired at every one of the six events above.** What was intermittently silent is the *writer*,
for agent A only. That asymmetry is a real finding and is filed as a triage candidate, not
papered over.

The gate's own imperative asks for "a planted, asserted over-threshold reading", so planting is
compliant here, not a shortfall. The honest statement is: **A's trip is a planted-reading
demonstration; B's release is a live-reading demonstration.**

---

## 1. DC5 — the round trip. What actually happened.

The round trip ran on a **separate** acceptance spine
(`.agent-work/acceptance-467/spine.json`), never on this run's own spine.

**How the trip was made to fire on a real reading rather than a big planted number.** Both gates
declare `context_headroom_tokens: 149000`. With the shipped `claude-*` profile
(window 1,000,000; hard cap 150,000) the per-gate hard line becomes 1,000/1,000,000 = **0.001**,
so any real reading is at/over hard. This is the shipped #467 per-gate override doing exactly
what it exists for. It is **verified in force**, not assumed: at a fill of **0.05** — well BELOW
the shipped 0.15 default — the engine renders the HARD band, which is impossible without the
override, and every `trip_ledger` entry records `hard: 0.001`.

`a1` carries a pre-attached refresh-request (`e-a1-1`) so agent A can `start a1` at all;
without it the begin-work guard refuses the first gate and nothing can run. That is not a
contrivance — a fresh agent starting the gate a refresh was requested for is the real relaunch
shape, and is precisely what I am on this run.

### The sequence, from the engine's journal

| seq | ts (UTC) | session id | verb | gate |
|---|---|---|---|---|
| 1 | 20:03:37 | `acc-setup` (me) | attach | a1 |
| 2 | 20:06:35 | **`acc-89f734` (A)** | start | a1 |
| 3 | 20:07:15 | **`acc-89f734` (A)** | advance | a1 |
| 4 | 20:08:25 | **`acc-89f734` (A)** | attach | a2 |
| 5 | 20:11:11 | **`acc-7f3d1b` (B)** | start | a2 |
| 6 | 20:11:33 | **`acc-7f3d1b` (B)** | advance | a2 |

A worked `a1`, was refused at `a2` (`tl-2`, `begin-refused`), filed the refresh-request the
refusal printed, released the lease and stopped. A had **fully returned** before B was
dispatched — A and B were synchronous subagents, so A's stop is a fact of the dispatch, not a
judgment call, and the journal shows no overlap (A's last action 20:08:25; B's first 20:11:11).

### B's work, verified item by item against what A was mid-way through

A left `roundtrip.md` at items 1–3 and carried **one fact in its handoff and nowhere else**: a
six-hex nonce, which its gate imperative forbade it to write to disk. B's gate required item 6 to
be that nonce.

| item | who wrote it | expected | on disk | verdict |
|---|---|---|---|---|
| heading | A | `# Round trip 467` | `# Round trip 467` | match |
| 1 | A | `1. alpha` | `1. alpha` | match |
| 2 | A | `2. bravo` | `2. bravo` | match |
| 3 | A | `3. charlie` | `3. charlie` | match |
| 4 | **B** | `4. delta` | `4. delta` | match |
| 5 | **B** | `5. echo` | `5. echo` | match |
| 6 | **B** | the nonce from A's digest | `6. NONCE: 4b3dc4` | match |

A's why-record `w-1` reads *"The nonce is 4b3dc4."* B wrote `4b3dc4`. **The one fact that existed
only in the handoff crossed the seam.** That is what makes this a round trip rather than two
agents doing adjacent chores: B could not have completed its gate without reading A's
understanding, and there was nowhere else to read it from.

A's own report flagged that the nonce briefly reached its log file, because the engine echoes the
`--why` text back as the `DIGEST:` line and A was required to log complete output. A caught this
on its own post-run audit and redacted that one occurrence, leaving an explanatory note in place
of it.

**I did not take that on A's word.** My own count of the nonce string across the acceptance
directory: `log-acc-89f734.txt` (A's log) **0**; `roundtrip.md` before B ran **0** — the `a1`
postcondition asserts that file holds exactly four lines, and it passed; `spine.json` **2**, the
two why-records, which is the engine's own legitimate record and the intended transport;
`log-acc-7f3d1b.txt` (B's log) **1**, written by B after it had already read the digest. So at the
moment B was dispatched, the nonce existed on disk **only** inside the engine's why-trail, and it
reached B through the `DIGEST:` line of the prompt.

### The verifier

`acceptance/verify_round_trip.py` reads the spine, its journal, and the deliverable, and asserts nine things
mechanically. **It passes: 9/9** (`evidence/g5-verifier.txt`).

```
V1 two distinct engine session ids acted -- acc-89f734 closed a1, acc-7f3d1b closed a2
V2 A's why-record w-1 exists at gate 'a1', carries a real understanding, and is the record
   the refusal at 'a2' was keyed to
V3 the agent that was refused (acc-89f734) is the agent that wrote the handoff
V4 B advanced a2 at 20:11:33, after A's last action at 20:08:25
V5 ledger holds 3 entries (1 refused, 2 released); every one carries its own fill/hard pair,
   every fill is at/over its hard, and every hard is below the shipped 0.15
V6 the refresh-request for 'a2' is keyed to w-1 -- B was released by A's handoff
V7 the deliverable holds items 1-6 exactly; A left 1-3, B added 4-6
V8 the nonce 4b3dc4 in B's line 6 appears in A's why-record w-1
V9 every gate is complete
```

**The verifier discriminates, and this is proved rather than asserted.** `--self-test` mutates a
copy of the real inputs nine ways — one per way the round trip could be faked — and requires a
rejection each time. **All 9 rejected** (`evidence/g5-verifier-selftest.txt`): one agent doing
everything; no begin ever refused; a handoff carrying no understanding; B acting before A
finished; the refused gate never resumed; the override not in force (twice, the second isolated so
an earlier assertion cannot be what catches it); the request keyed to nothing; and B inventing the
nonce.

The isolated ninth mutation exists because of something I found in my own verifier: the first
"override not in force" mutation was being caught by the *earlier* `fill >= hard` assertion, so the
override assertion was never independently exercised. A check that only ever fires behind another
check is a check that cannot fail. I added the isolated variant rather than leave that gap
unstated.

---

## 2. Agent B's VERBATIM dispatch prompt

The claim under test is that a cold agent resumes from `current` **alone**. B's prompt was the
`current` output and nothing else — no summary, no handoff document, no pointer from me.

Captured before dispatch to `.agent-work/acceptance-467/PROMPT-B.txt`:
**3754 bytes, sha256 `3da641137aa5b7c67bf59c35c6991911a05adb3958458bbbf8f505a98d92f80f`.**
That file is the byte-for-byte source of the prompt below, so the cold-start claim stays
falsifiable after the fact. Agent A was dispatched under the same discipline
(`PROMPT-A.txt`, 2901 bytes) even though only B was required to be.

The gate imperatives inside the spine — the operating instructions B needed, such as the engine
command shape and the instruction to invent its own session id — were authored **before agent A
ran** and were never edited afterwards. They are job-file content, which is what
`constraint:job-file-not-agent-file` requires; B reuses A's spine file, which was never copied or
recreated. The authoring script refuses to run a second time, so "authored once" is enforced, not
promised.

```text
RAIL: The finish is a sequence, not an announcement. Final `advance` first, then `release` — the journal, not your prose, is the proof.

LEASE released: acc-89f734
ACTIVE a2 [pending] — ACCEPTANCE ROUND TRIP (issue #467) -- gate a2 of 2, the last gate.

The agent that worked gate a1 is gone. Everything you need is in this output.

HOW TO DRIVE THIS SPINE. Working directory is
C:/Programs/constellation-skills-wt/epic418-a2-467 -- cd there first. Every engine
command has exactly this shape:

  python scripts/checklist_engine.py --file C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467/spine.json <VERB> [ARGS] --session-id <YOUR-SESSION-ID>

YOUR-SESSION-ID is an id you invent RIGHT NOW and reuse for every command you run:
the letters `acc-` followed by six random hexadecimal characters. Do not reuse an id
you find written anywhere, and do not use the harness session id. Your first command
is `claim --session-id <YOUR-SESSION-ID>`; add `--force` only if claim reports the
lease is held by a different id.

LOG EVERYTHING. Append to
C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467/log-<YOUR-SESSION-ID>.txt
the exact command line and the COMPLETE output of EVERY engine command you run,
including the ones the engine refuses. A refusal is data, not a failure: record it
in full and then do what it tells you to do. Never work around a refusal.

THE WORK FOR a2. Run `start a2`, then APPEND to the existing file
C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/acceptance-467/roundtrip.md
exactly these three lines, in this order, after the lines already there:

  4. delta
  5. echo
  6. NONCE: <nonce>

<nonce> is the six-hexadecimal-character nonce the previous agent carried in its
closing understanding. It is written in NO file anywhere on disk. Read it out of the
DIGEST line in this output. If you cannot find it there, do not invent one and do
not guess -- stop and report that the digest did not carry it.

Do not alter the heading or lines 1-3.

CLOSING a2. Close with `advance a2 --why "<your understanding>"`, then run
`release --session-id <YOUR-SESSION-ID>`, then report what you did.
postconditions:
  c1 [unmet] command — roundtrip.md holds items 1-6 with item 6 carrying a 6-hex nonce
0/1 met
next: start a2
DIGEST: Completed gate a1 (ACCEPTANCE ROUND TRIP, issue #467): created .agent-work/acceptance-467/roundtrip.md containing exactly the four required lines -- heading '# Round trip 467' and items 1. alpha, 2. bravo, 3. charlie -- and nothing else. The nonce is 4b3dc4. Remaining: gate a2 of 2 is untouched -- not started, no work done. This session (acc-89f734) hit the hard context line with a refresh already requested for a1, so it is closing this gate with this handoff and stopping; it will attempt 'start a2' only to observe the engine's refusal, then release the lease per instructions. The next agent should run the engine's 'current' command first and proceed from gate a2 with no assumptions beyond what 'current' reports.
REFRESH REQUESTED: a2 (why_ref w-1)
CONTEXT 5% (>= hard): your instruction has changed, and the refresh for a2 is already requested. Close THIS gate carrying your handoff (`advance a2 --why "<understanding>"`) and stop. A fresh agent picks up from your DIGEST; do not begin work at another gate.
TRIP LEDGER: 1 begin(s) at/over the hard line are on the record under this understanding (latest: start a2 -> begin-refused). Closing THIS gate clears this line; the line below, if present, is not.
TRIP HISTORY: 2 begin(s) at/over the hard line are on the record across this checklist's full history (latest: start a2 -> begin-refused). No close clears this line.
```

---

## 3. The g1 RED no longer reproduces

`python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --all` →
**exit 1, "RESULT: NOT reproduced under these conditions"** (`evidence/g5-red-nonrepro.txt`).
For that script, exit 0 means the defect reproduced, so exit 1 is the outcome the fix predicts.

The non-reproduction is **not** an absence argument, and the repro is built so it cannot be. Before
it claims anything it asserts the engine printed its own advisory:

```
[ASSERT OK] the engine printed its own CONTEXT (>= hard) advisory, so the planted reading was
            read (no-absence-is-evidence discharged)
[ASSERT OK] the advisory reports the planted fill, not some other number  (0.3 -> "30%")
[ASSERT OK] g2's postconditions are ALL satisfied, so nothing but the gauge can block this advance
```

and only then fails at the step that used to be the defect:

```
step 2: the agent tries to advance g2 carrying its CURRENT understanding
$ checklist_engine.py ... advance g2 --why "CURRENT UNDERSTANDING: ..."
| g2 -> complete
| (exit 0)
REPRO FAILED (scoped to this check): expected a refusal, got exit 0
```

The reading was read, the gate was otherwise closable, and the handoff-carrying advance
**completed**. That is the fix, observed.

---

## 4. #431 verified dissolved — NOT closed

**Not closed. Closing it is the Admiral's.** The evidence that it is dissolved:

1. **The RED cannot reproduce it** (§3) — with the reading asserted present first.
2. **The permanent regression guard exists and is pinned in the right place:**
   `tests/test_checklist_engine.py:3514`,
   `test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest`. It pins
   `fill >= hard` with **no refresh-request anywhere in the spine** — exactly the condition under
   which the pre-#467 engine refused — and asserts both halves: the advance completes AND the
   digest becomes the understanding written at that gate. It also asserts
   `_refresh_requests_anywhere(cl) == []` before and after, so if the fixture ever acquires a
   pending request the guard cannot silently lift.
3. **Live, at one and the same over-the-line reading** (`evidence/g5-close-side.txt`, exit 0),
   after the engine printed `CONTEXT 5% (>= hard)`:
   - `start q2` → **REFUSED** ("not the moment to BEGIN work here")
   - `advance q1 --mechanical` → **REFUSED** ("this gate cannot be closed silently")
   - `advance q1 --why "..."` → **exit 0, `q1 -> complete`**, and the digest became the
     understanding written at that gate.
4. **Three live #431 specimens were produced by this run itself**, all to Commanders on the real
   spine, all against **main's pre-#467 engine** — which is the defect still standing in main and
   the reason the branch exists.

---

## 5. Admiral conditions

### 5a. DC2 is **done-by-different-means**, never done-as-written

#467's DC2 says the engine *"distinguishes an advance that **carries a handoff** from one that
**starts new work**, and refuses only the second."* **The shipped engine does not have that
distinction, and a reviewer must be able to see the departure without reading the DIT.**

There is no such thing as an `advance` that starts new work. `advance` only ever closes the gate
the agent is already inside. The verb that begins work is `start` (and `reopen`). So the shipped
engine draws the line **between verbs**, not between two modes of `advance`:

- `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}` — the begin-work verbs, refused over the line.
- `advance` is **never** governor-refused, because closing the gate you are inside *is* the
  handoff.
- What HARD adds on the close side is a ban on **silence**: `--mechanical` is refused and
  `why_exempt` is suspended, so the digest cannot stay pre-trip while the gate closes.

The outcome DC2 wanted — "refuse the thing that begins work you cannot finish, never the thing
that hands off" — is delivered. The mechanism named in the literal text is not the mechanism
shipped. Reported as **done-by-different-means**.

The two-way test DC2 demands is satisfied twice over, both times at one and the same reading:
in the round trip (A's `start a2` refused at `tl-2` while A's `advance a1` completed), and in the
close-side probe (three moves, one reading, §4.3).

### 5b. #467's Evidence section OVER-STATED "the RED leaves no residue"

**Stating it plainly, as required, and not burying it in a passing test:** #467's Evidence section
claimed the RED leaves no residue. **That claim was too strong.** The RED is disposable and is
correctly not promoted to a regression test — the deadlock is a property of a refusal path this
issue deletes, so it is unreproducible by construction after the fix. But "unreproducible by
construction" is exactly the condition under which a defect can return unnoticed, because nothing
is left watching.

**The correction is the standing pin**, and it is in place:
`test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest`
(`tests/test_checklist_engine.py:3514`) — `fill >= hard` with **no pending refresh-request**,
asserting the advance completes **and** the digest updates. That is the residue the RED itself
does not leave. The finding is recorded here as a finding, not as a green tick.

### 5c. The anti-vacuity gate check, and proof that it FIRES

**Where it lives:** `execute.json`, gate `g4-integrate`, postcondition **`c2`** —
`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'`
with the statement *"the compliance-observable tests EXIST and pass — pytest exits 5 on an empty
collection."* The mechanism is pytest's exit code 5 for "no tests collected": if the named tests
were deleted or renamed away, the pattern would collect nothing, pytest would exit 5, and the
engine's `command` postcondition would refuse the advance.

**Demonstrated firing against a pattern that collects nothing** (`evidence/g5-antivacuity.txt`):

```
$ python -m pytest -q tests/test_checklist_engine.py -k "this_pattern_collects_absolutely_nothing_xyzzy"
418 deselected in 0.19s
REAL EXIT = 5

$ python -m pytest -q tests/test_checklist_engine.py -k "ledger or compliance or trip_log"
34 passed, 384 deselected, 21 subtests passed in 6.05s
REAL EXIT = 0
```

**A warning that belongs with this, because I walked into it while proving the check fires.** My
first attempt piped pytest to `tail`, and `$?` then reported the **exit code of `tail`, not of
pytest** — I read `EXIT=0` on the very command that actually exits 5. Any invocation of this check
that pipes pytest anywhere before its status is read converts a firing anti-vacuity check into a
silent one. If this is routed as a doctrine candidate, that pipeline hazard should ride along with
it: the check is only as good as the exit code someone actually reads.

---

## 6. Per-done-condition accounting, DC1–DC6

A blanket "done" is not on offer. Where partial is true, it says partial.

| DC | Verdict | Evidence, and what is NOT claimed |
|---|---|---|
| **DC1** — at/over HARD the engine changes the imperative rather than refusing the verb it needs | **done** | Live in both dispatch prompts: `CONTEXT 5% (>= hard): your instruction has changed…`, naming the close the agent should make. The verb the agent needed (`advance`, to close and hand off) was never refused; A used it successfully at `a1` while over the line. |
| **DC2** — distinguishes a handoff-carrying advance from one that starts new work; refuses only the second; two-way test | **done-by-different-means** (§5a) | The distinction ships **between verbs** (`start`/`reopen` guarded, `advance` never), not between two modes of `advance`. Outcome delivered; literal mechanism not. Two-way test satisfied twice at one reading. **Not claimed:** that the engine implements DC2's literal text. |
| **DC3** — the why-record lands on the handoff-carrying advance, so DIGEST is fresh at the seam; #431 dissolved | **done** | `advance a1 --why` wrote `w-1`; `current` then rendered it as the `DIGEST:` line that B was dispatched with; B used a fact available only there. #431 dissolved per §4. **#431 is NOT closed.** |
| **DC4** — per-gate threshold override exists and is exercised once; one gate's behaviour changes and not its neighbours'; global default unchanged | **done** | `evidence/g5-dc4-neighbour.txt`, exit 0: at one reading of 0.05, the gate declaring `context_headroom_tokens` was refused and its neighbour without one started fine; the ledger names only the overridden gate. Global default unchanged — the un-overridden gate still uses the shipped 0.15, which is why 0.05 passed it. |
| **DC5** — round trip completes once; resumed work verified against what the tripped agent was mid-way through | **done** | §1. Two distinct session ids, A's handoff at the tripping gate, B's advance strictly after A's last action, expected ledger entries, and the nonce crossing the seam. Verifier 9/9, self-test 9/9. |
| **DC6** — non-compliance is mechanically observable: the engine can see whether a handoff appeared before the next advance at an over-threshold gate | **partial** | **What works:** `trip_ledger` is engine-written-only at the single mutating chokepoint; both selectors are pure; and both rendered lines were observed live in B's prompt — `TRIP LEDGER: 1 begin(s)…` and `TRIP HISTORY: 2 begin(s)…`. The historical line survives the close the HARD band mandates, which was the g4 B1 rework. **What does not:** once a checklist has no active gate, `_trip_advisory` returns early on the `gate is None` path and **both** lines go silent at closeout — B1's shape at the vantage point an auditor actually occupies. That is `tc19`/**#504**, filed and **deferred by Admiral ruling**; I did not carry it into g5, because touching that code would void the approval the g4 rework earned. Also scoped by the engine's own documented limit: an agent that is told to wrap up and simply stops without running another verb leaves no entry — an empty ledger is not a claim of compliance. |

**Overall: DC1, DC3, DC4, DC5 done; DC2 done-by-different-means; DC6 partial.** DC5 — the one the
issue exists for — completed, and is not being reported on the strength of the others.

---

## 7. Limits, and what I am not claiming

1. **The gauge writer was silent for agent A** (§0) with no skip record to say why. A's two ledger
   entries are judged against a planted reading. B's are live. Filed as a triage candidate.
2. **`tc19`/#504 stands open** — the trip lines go silent at closeout. Deferred by ruling, not
   fixed here, and DC6 is reported `partial` because of it.
3. **The acceptance spine is not a production spine.** Its per-gate reserve of 149,000 tokens is
   deliberately extreme so that any real reading is over the line. It demonstrates the mechanism
   under a controlled condition; it does not demonstrate the thresholds an operator would choose.
4. **`ROLLOUT CAVEAT` in the engine still stands** — the HARD band is not to be enabled in
   production until #183's tier-skill wiring lands. Nothing in this acceptance changes that.
5. **The verifier lives in the work area, not in `scripts/`.** This gate makes no source change,
   matching the pattern g1-integrate pinned. If the Admiral wants it durable, that is a decision
   above me and I have not made it.

## Artifacts

| Path | What |
|---|---|
| `.agent-work/acceptance-467/spine.json` (+ `.journal`) | the acceptance spine and its provenance |
| `.agent-work/acceptance-467/roundtrip.md` | the deliverable A and B built between them |
| `.agent-work/acceptance-467/PROMPT-A.txt`, `PROMPT-B.txt` | the verbatim dispatch prompts |
| `.agent-work/acceptance-467/log-acc-89f734.txt`, `log-acc-7f3d1b.txt` | A's and B's own command logs |
| `.agent-work/issue-467-trip-semantics/acceptance/verify_round_trip.py` | the verifier (`--self-test` proves it discriminates) |
| `.agent-work/issue-467-trip-semantics/acceptance/build_acceptance_spine.py` | authored the spine once; refuses to run twice |
| `.agent-work/issue-467-trip-semantics/acceptance/probe_close_side.py` | the three-move close-side test |
| `.agent-work/issue-467-trip-semantics/acceptance/probe_dc4_neighbour.py` | the DC4 override/neighbour test |
| `evidence/g5-*.txt` | every command output cited above |
