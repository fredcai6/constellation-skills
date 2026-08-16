# Triage recommendations — `cleanup-b-context-identity`

Driven at the `triage` spine step, leg 3. Six candidates, all routed.

## Authority, and why every disposition is `recommend-and-defer`

`LAUNCH_ORDER.md` §Inherited Latitude does **not** grant issue-filing authority.
It grants decisions about the attribution scheme, where consumption triggers,
test structure, and whether #500 ships — and it names **publication** among the
things that must be floated to the Admiral. Filing on the tracker is publication.

`ADMIRAL_RULING-2.md` confirms the posture on the one candidate it addresses:
"I am filing it on the tracker myself; you do not need to."

So no issue is filed this run. Each candidate below is issue-ready — an Admiral
or human can file it verbatim. Per the triage ladder, a candidate that is merely
ineligible for fix-now **and** lacks clear filing authority routes to
`recommend-and-defer`, which is the recorded form of "ask". That is deliberate,
not an omission.

**Note on id collision.** The reviewer numbered its own candidates `tc1`–`tc3`
independently of `execute.json`'s `tc1`–`tc3`, and the two sets are different.
Renumbered here as **T1–T6**, with both original labels given.

---

## T1 — R4 row 2 is an untested governor branch

*(reviewer `tc1`, from `g1-review` F1 · **MEDIUM**)* · labels: **missing test**

**Priority: HIGH** — highest-value next action in this lane. See the disposition.

### Observation 1

- **What's wrong:** R4 row 2 — *2+ distinct candidates all under one owner →
  write every candidate* — is implemented and behaves correctly, but no test
  exercises it. Reverting the branch to the old skip-on-count rule
  (`unattributable = len(targets) > 1`) leaves **all 616 gauge tests green**.
- **Expected:** a behavioural row the Admiral explicitly held to is pinned by a
  test that fails when the row is removed.
- **Feeding conditions:** one binding key, one `engine_session`, two **distinct**
  work directories. Every existing multi-candidate test uses two *different*
  owners (`eng-1`/`eng-2`) and so exercises the **skip** branch; the #488 test
  covers the same-**directory** case, which dedupes to a single candidate and
  never enters the multi-candidate write loop. Environment: Linux, Python 3.12.
- **`type`:** `measured` — by mutation. The reviewer applied the revert, asserted
  it present, ran the gauge suite green, and restored byte-identical
  (`git diff --exit-code` clean).
- **`rev`:** `ccb8b8d8` (branch head; the change itself is `3bc87e93`).

### Why it matters

A future "simplification" back to a count check restores the **#488-class dark
governor** for the multi-directory same-owner case, with no failing test
anywhere. That is the silent shape this subsystem has been burned by three times
(#252, #271, #488) and the exact regression `ADMIRAL_RULING-2.md` point 1 exists
to prevent.

### Possible fix

One test: one binding key, one `engine_session`, two distinct work directories →
assert **both** owner-keyed files are written and no sidecar appears. The
reviewer notes that extracting the attribution decision (the `owners` set and
`unattributable`) out of `handle_post_tool_use` would give this its natural unit
seam — see T5.

### Open questions

None. The behaviour is verified correct by direct drive; only its coverage is
missing.

### Disposition: `recommend-and-defer`

It **clears all four fix-now rungs** — bounded (one test), adjacent
(`tests/test_gauge_writer.py`, a file this lane owns), verifiable now, no
architecture impact — and it was still not fixed here. The reason is stated
plainly rather than dressed up: it surfaced at `g1-review`, and by the time it
was routable `g1-integrate` was **closed**. Adding implementation code after the
gate that verifies it has closed is work the engine never saw, which is the one
thing a Commander run may not do. Filing authority is also absent.

**For the next leg: this is the first thing to pick up**, as a small crew gate
(`g1b`) before #500.

---

## T2 — a `SessionStart`/stop hook tells a dispatched crew to drive its parent's gate

*(`execute.json` `tc1`, also reviewer `tc3`)* · labels: **bug**

**Priority: HIGH** — same defect class as #600, one layer up. **Three
occurrences now.**

### Observation 1 — the g1 implementer

- **What's wrong:** the hook named the **parent Commander's** `spine.json` and
  instructed the crew to load `constellation-commander`, write `STATE_NOTE.md`
  and drive `execute.json` gate by gate.
- **Expected:** a dispatched crew is pointed at its **own** assignment, or at
  nothing.
- **Feeding conditions:** the hook resolves `SPINE_FILE` from an **inherited
  environment**. The crew's own registry row records `spine: null`.
- **`type`:** `measured` — the crew verified the refusal by command and left
  `spine.json` byte-identical.
- **`rev`:** at `g1-implement`, pre-`3bc87e93`.

### Observation 2 — the g1 reviewer

- **What's wrong:** identical misfire. The reviewer's environment carried
  `SPINE_FILE=.agent-work/cleanup-b-context-identity/spine.json` and
  `SPINE_SESSION=constellation/cleanup-b-context-identity/execute/commander` —
  the parent's spine and the parent's **role**, not its own.
- **Expected:** as above. Note the reviewer skill says "`spine_status` is your
  first call" and "do not author a survey of your own when a spine is already
  bound", which points a compliant crew **straight at the wrong spine**.
- **Feeding conditions:** as above. The reviewer concluded nothing was bound for
  it (its `SPINE_SESSION` names the parent's role, not
  `g1-review/reviewer/attempt-1`), authored its own survey per the skill's
  fallback branch, and never touched the parent's spine.
- **`type`:** `measured` — reported with the exact inherited variable values.
- **`rev`:** `ccb8b8d8`.

### Observation 3 — this Commander leg

- **What's wrong:** leg 3's own `SessionStart` carried the same foreign
  imperative.
- **Expected:** as above.
- **`type`:** `measured` — visible in this session's own start context; not
  acted on.
- **`rev`:** `ccb8b8d8`.

### Why it matters

Acting on the misfire requires a `--force` takeover of a **live parent's** lease
and would deadlock the wave. Every crew so far refused correctly, but the
refusal depends on the crew noticing — and the reviewer says explicitly that the
**handoff's closing warning** is what made it unambiguous.

### Possible fix

Resolve the crew's spine from its **own** dispatch assignment rather than from an
inherited environment — the same "identity, not ambient context" move #600 made
one layer down. `run_crew.py` already knows the assignment; the registry row
records `spine: null` correctly.

### Open questions

Whether the reviewer-skill wording ("do not author a survey of your own when a
spine is already bound") should change independently of the hook fix, since it
actively steers a compliant crew toward the wrong spine.

### Disposition: `recommend-and-defer`

Ineligible for fix-now: `scripts/hooks/spine_rail.py` is **fenced** (lane C owns
it), and `LAUNCH_ORDER.md` requires floating any change to it. Filing authority
absent. **Until it is fixed, keep the explicit warning in every crew handoff** —
it is load-bearing, and the reviewer says so in as many words.

---

## T3 — a blocked Commander goes lease-stale while healthy

*(`execute.json` `tc2`)* · labels: **bug**, **tooling**

**Priority: HIGH** — the Admiral has taken the filing himself.

### Observation 1 — leg 2

- **What's wrong:** a Commander blocked on a foreground crew is called
  lease-**stale** by the engine while perfectly healthy.
- **Expected:** liveness reflects whether the agent is alive, not whether it
  recently issued a mutating verb.
- **Feeding conditions:** `run_crew.py` is **blocking by design**, and a parent
  waiting on a child issues no mutating verb, so it cannot heartbeat.
- **`type`:** `measured` — last heartbeat 13:20:19Z while blocked **53 minutes**
  on a live crew; the engine already called that lease stale.
- **`rev`:** at `g1-implement`.

### Observation 2 — leg 3, independent reproduction

- **What's wrong:** identical. `advance execute` was **REFUSED** with
  "checklist lease 'commander-cleanup-b-context-identity' is stale".
- **Expected:** as above.
- **Feeding conditions:** this leg blocked ~25 minutes on the `g1-review` crew
  and then on three full-suite runs (~2 min each) — all non-mutating waits.
- **`type`:** `measured` — the refusal is in this leg's journal; recovered by
  re-claiming with the **same** session id, never `--force`.
- **`rev`:** `95fe848c`.

### Why it matters

`ADMIRAL_RULING-2.md`: this "directly qualifies the liveness work merged this
morning — anything judging a lease or an entry by heartbeat age can force-claim
a spine out from under a running parent." A blocking wait is the **normal** shape
of a Commander run, so the false-stale window is routine, not exceptional.

### Possible fix

Either heartbeat from the blocking wait itself, or judge liveness by process
liveness (the registry already stores a live PID and `recover_crews.py` already
classifies on it) rather than by heartbeat age alone.

### Open questions

Whether same-id re-claim should refresh the lease silently — it currently does,
which is what made both recoveries safe, and that behaviour should be preserved
by any fix.

### Disposition: `recommend-and-defer`

Not fix-now: touches `run_crew.py`/liveness, both fenced to lane C, and is
multi-gate work. **The Admiral stated he is filing this one himself**, so it is
recorded here and deliberately not filed. Leg 3's independent reproduction is
new evidence worth attaching to his issue.

---

## T4 — a format sweep is not a dependency sweep

*(`execute.json` `tc3`)* · labels: **missing doc**, **tooling**

**Priority: MEDIUM**

### Observation 1

- **What's wrong:** the gate handoff commissioned a **format-change**
  enumeration (the prescribed Wiring Grep for the literal `gauge.json`) and
  treated it as sufficient. It could not see a dependency expressed as
  `gauge_reader.py` — the installer's runtime-companion declaration was
  invisible to it.
- **Expected:** the sweep that gates a format change also finds the code that
  depends on the format's **carrier**.
- **Feeding conditions:** the dependency is named by module, not by the string
  being changed.
- **`type`:** `measured` — the full suite caught it; the grep did not.
- **`rev`:** at `g1-implement`.

### Why it matters

Uncaught, it would have shipped a **dark governor into every install**: the
writer emitting `gauge.json` while a leased engine reads `gauge-<owner>.json`.
`ADMIRAL_RULING-2.md` rules this "worth stating as **doctrine** rather than a
defect".

### Possible fix

Specify the two sweeps separately wherever a Wiring Grep is prescribed: enumerate
the literal being changed **and** the module(s) that carry it.

### Open questions

None.

### Disposition: `recommend-and-defer`

Ineligible for fix-now: it is a doctrine change to shared handoff/sweep
specification, i.e. a cold-start area outside this lane's file ownership.
Filing authority absent; the Admiral has already ruled on how to frame it.

---

## T5 — sidecars are per-directory while readings are per-owner

*(reviewer `tc2`)* · labels: **architecture weakness**

**Priority: LOW** — bounded, verified advisory-only.

### Observation 1

- **What's wrong:** `gauge-skip.json` / `gauge-uncalibrated.json` stay
  per-directory and unowned, so one owner's advisory can be rendered to a
  **different** owner sharing the work directory.
- **Expected:** arguably, an advisory reaches only the owner it concerns.
- **Feeding conditions:** agent B holds the lease; agent A's unowned
  `gauge-skip.json` sits in the shared directory. B is shown "CONTEXT GAUGE
  SILENT: this session is bound to 2 candidate spines at once…".
- **`type`:** `measured` — driven by the reviewer.
- **`rev`:** `ccb8b8d8`.

### Bounded by measurement, not by assumption

A sidecar carries no `fill_fraction`/`model`, so it can **never** become a
`Reading`: `gauge_reader.read(<sidecar path>)` returns `None`, and it can never
cause a trip or refusal for **any** owner. B's own owner-keyed reading still
wins. The residual is exactly what the implementer declared — an advisory shown
to an owner it does not concern — and it is advisory-only and in the **permit**
direction. Widened slightly by #600, since more agents now have their own
readings alongside one shared sidecar.

### Possible fix

Owner-key the sidecars too. Note the counter-argument already recorded in
`decision:sidecar-name`: the skip case is *by definition* one where no owner can
be named, so there may be nothing to key on — which is why this is an open
weakness rather than an obvious fix.

### Open questions

Whether a skip sidecar can be attributed at all. If not, the honest fix may be to
word the advisory so it does not read as being about the reader.

### Disposition: `recommend-and-defer`

Ineligible for fix-now: it carries a **decision** (`decision:sidecar-name`) and
therefore routes through reconcile, which the ladder excludes from fix-now.
Filing authority absent.

---

## T6 — `map_orient.py verify-frame` refuses every decision id under a degraded map

*(from `plan`, original `tc6`)* · labels: **bug**, **tooling**

**Priority: MEDIUM**

### Observation 1

- **What's wrong:** `verify-frame` refuses `decision:` / `constraint:` /
  `assumption:` / `claim:` ids whenever the map is DEGRADED, so a mission frame
  that **complies with the required template** cannot pass.
- **Expected:** a frame is judged against the template it was required to use.
- **Feeding conditions:** map DEGRADED (`map/ids.jsonl` empty, per-module
  `INDEX.md` targets absent). All **11** refusals here were decision ids, while
  the frame's **path** citations resolved cleanly.
- **`type`:** `measured` — at `plan`, this run.
- **`rev`:** at `plan`.

### Why it matters

It forces a waiver on every run whose map is degraded, which trains agents to
waive a check rather than read it. `plan.c6` was **waived on this reason** here —
recorded, not skipped.

### Possible fix

Judge id citations against the map's **actual** capability when degraded, or
report them as unverifiable rather than refused.

### Open questions

Whether the right behaviour under DEGRADED is "pass with a warning" or "report
unverifiable" — they differ in whether the gate can still catch a genuinely bad
id.

### Disposition: `recommend-and-defer`

Ineligible for fix-now: `scripts/map_orient.py` is outside this lane's file
ownership and the fix needs its own tests. Filing authority absent.

---

## Summary

| id | candidate | labels | priority | disposition |
|---|---|---|---|---|
| T1 | R4 row 2 untested | missing test | **HIGH** | `recommend-and-defer` — **clears the fix-now ladder**; first pickup for the next leg |
| T2 | crew told to drive its parent's gate | bug | **HIGH** | `recommend-and-defer` — fenced (lane C); 3 occurrences |
| T3 | blocked Commander goes lease-stale | bug, tooling | **HIGH** | `recommend-and-defer` — **Admiral is filing this himself**; leg 3 adds a second reproduction |
| T4 | format sweep ≠ dependency sweep | missing doc, tooling | MEDIUM | `recommend-and-defer` — ruled to be doctrine |
| T5 | sidecars per-directory, readings per-owner | architecture weakness | LOW | `recommend-and-defer` — carries a decision; advisory-only |
| T6 | `verify-frame` refuses decision ids when degraded | bug, tooling | MEDIUM | `recommend-and-defer` — outside file ownership |

**Zero `fixed-now`. Zero `filed`. Six `recommend-and-defer`.** No candidate is
unrouted, and no issue was created without authority.

_Leg 3, `commander-cleanup-b-context-identity`, 2026-08-16._
