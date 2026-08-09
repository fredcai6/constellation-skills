# Candidate C — move the refusal, add no machinery

**Constraint:** HARD stops refusing `advance` and refuses `start` instead. Closing the gate
you are in is always allowed; beginning the next gate is what is blocked. No new verb, no new
flag, no new evidence semantics.

---

## 1. The mechanism

The engine already forces the handoff — on the wrong side of the refusal. `advance` is the
only writer of `why_trail` (`_append_why`, :1095), the latest live why-record **is** the
DIGEST (`_digest`, :1139), and a non-exempt gate **fails closed on a silent advance**
(:1899–1909): you cannot close a gate without stating your running understanding. So
`advance --why` already *is* the handoff artifact. #431 is simply that the governor refuses
the one verb that writes it.

Candidate C changes nothing about what a handoff is. It moves the guard one verb later:

- `advance` is **never** governor-refused. At/over HARD, closing your gate is not merely
  permitted, it is the only forward move — and it is the move that writes the DIGEST.
- `start` (and `resume`, see below) is refused at/over HARD until a non-superseded
  `refresh-request` targets the gate with `why_ref == _latest_why_record(cl).id`.

The release condition is unchanged in form from `_trip_hard_gate` (:1439) — the same
identity-aware predicate from #190 — but under C it now means something stronger. After a
compliant `advance`, `_latest_why_record` **is the handoff the agent just wrote**. So
"a refresh-request keyed to the current why-record" reads as: *the request points at the
handoff.* Today it points at the pre-trip understanding, because no new one was allowed to
exist.

`resume` is guarded too, on the same predicate. Without it, a tripped agent could
`block` its gate and `resume` it and keep working, defeating the refusal in two verbs. `start`
and `resume` are exactly the verbs that *begin work at a gate*; that is the one line the
doctrine has to carry.

### Code sketch

```python
# dispatch(), replacing the `if v == "advance": _trip_hard_gate(...)` at :2679-2680
        # Trip HARD (#467): the refusal moved off `advance` — closing your gate is
        # always allowed and IS the handoff (`--why` -> why_trail -> DIGEST). What
        # HARD blocks is BEGINNING work: `start` a pending gate, or `resume` a
        # blocked one. Still checked BEFORE the verb, so a refusal never mutates.
        if v in ("start", "resume"):
            _trip_begin_gate(cl, getattr(args, "id", None), base_dir)


def _hard_for(cl: dict, gate: str, model: str, base_dir: Path | None) -> float:
    """The hard fraction in force AT THIS GATE. Precedence: per-gate override >
    per-checklist config > the graded model default (`thresholds_for`). Called by
    BOTH the advisory and the guard so display and enforcement cannot drift."""
    _, model_hard = _gauge_reader.thresholds_for(model)
    window = _gauge_reader.window_for(model)          # None when uncalibrated
    for source in (task(cl, gate), load_config(cl, base_dir)):
        headroom = (source or {}).get("context_headroom_tokens")
        if isinstance(headroom, int) and not isinstance(headroom, bool) and window:
            return max(0.0, 1.0 - headroom / window)  # absolute tokens, see §3
    return model_hard


def _trip_begin_gate(cl: dict, iid: str | None, base_dir: Path | None) -> None:
    """Trip HARD backstop at the verbs that BEGIN work. No-op for surveys, a
    missing/stale reading, or below hard — HARD never forces on an absent reading."""
    if cl.get("type") != GATED or not iid:
        return
    reading = _read_gauge(base_dir)
    if reading is None:
        return
    if reading.fill_fraction < _hard_for(cl, iid, reading.model, base_dir):
        return
    rec = _latest_why_record(cl)
    wid = rec["id"] if rec else None                  # None -> gate-only match (see §1b)
    if has_pending_refresh_request(cl, iid, why_ref=wid):
        return
    raise EngineError(
        f"{iid}: context at {reading.fill_fraction:.0%} is at/over the hard limit — "
        f"BEGINNING {iid} is blocked. Closing the gate you were in is not blocked and "
        f"never was: `advance <gate> --why \"<handoff>\"` is your handoff, and the "
        f"--why you pass becomes the DIGEST your successor cold-starts from. "
        f"Then run: {_refresh_attach_hint(iid)} — then go idle."
    )
```

`_trip_advisory` (:1399) gains one branch, no new state: at HARD, if the active gate is
`in-progress` say *"finish here — `advance --why` is allowed and is your handoff; the next
`start` is blocked"*; if it is `pending` say *"starting `<gate>` is BLOCKED"* + the attach
hint. Same suffix, same chokepoint.

### 1a. The #431 case: `in-progress` with UNMET postconditions

This is the case the field actually hit, and C's answer is that C **un-shadows** it. Today
`_trip_hard_gate` fires in `dispatch` (:2680) *before* `advance` runs, so the agent is told
"advance is blocked, request a refresh" and never learns its real problem. Under C the
governor is off `advance` entirely, so the same call reaches :1885 and refuses with
`g2: postconditions unmet ['c1']` — the true statement about the world.

Ruling: **you may not buy past unfinished work with a handoff.** That is already settled
engine doctrine — :1893–1896 deliberately sequences postconditions *before* the why prompt —
and C keeps it by construction. The agent's paths, in order, no new machinery:

1. **Finish the postcondition.** HARD means "wrap up", not "you are unsafe" (fixed
   constraint), and the trip checks at gate boundaries only, so nothing refuses the few tool
   calls needed to close a condition. This is the expected path.
2. **If it genuinely cannot be closed:** `block <gate> --blocker "<what stops it>"
   --authority <who> --next "<the mid-gate handoff>"`. `block` (:1979) records
   `status_detail.prior_status = "in-progress"` and bubbles to `cl["blockers"]`, and `resume`
   (:1999) restores `in-progress` for the successor. Then file the refresh-request. The
   successor's `resume` is the guarded verb, so the refusal still holds the line.

Honest gap, and I will not paper it: `block`'s `--next` text lands in `status_detail` and
`blockers[]`, which `render_human` does **not** print — `current` shows only
`ACTIVE g2 [blocked] — <imperative>` plus the DIGEST. A mid-gate handoff is therefore weaker
than a gate-closing one: it is one status word and a spine field, not the DIGEST. The minimal
fix is a render, not machinery — one line in `render_human`'s active branch surfacing
`status_detail.next_action` when status is `blocked`. C ships that line.

### 1b. The first gate of a run, with no why-record at all

Sequence: fresh claim, `g1` pending, agent runs `start g1`, gauge already reads >= hard
(inherited context, or a resumed session). `why_trail` does not exist, `_latest_why_record`
returns `None`, `wid` is `None`, the predicate degrades to the gate-only match (the
documented `why_exempt` degradation at :1456), no request exists, and **`start g1` refuses.**

That is the right answer and it is a strict improvement, not a corner case C survives. Under
today's design this agent is waved into `g1`, burns its remaining context doing the work, and
is then refused at `advance` while holding a `--why` it is not permitted to record. Under C
the refusal lands *before* the work — which is precisely "beginning the next gate is what is
blocked."

"Close the gate you are in" has nothing to record here, and nothing *needs* recording: no work
was done, so there is no understanding to hand off. The engine already says this correctly —
`_why_suffix` emits no `DIGEST:` line when `_digest` is `None` (:1189–1191), so the successor
cold-starts on `ACTIVE g1 — <imperative>` with no digest, which is exactly true. C adds
nothing here and must not: a fabricated "nothing has happened yet" why-record would be a
mechanical marker masquerading as understanding, and `_latest_why_record` already refuses to
treat mechanical markers as live (:1129).

The residual: with `wid is None` the release is gate-only, so any unsuperseded
`refresh-request` naming `g1` releases the start. This is materially *not* #190's coattails
bug. #190's hazard was a stale request keyed to an *earlier understanding within the same
agent's life*; here there is no understanding at all, so there is exactly one distinguishable
state and the gate-only match is not merely a degradation — it is complete. A successor
released by its predecessor's request is released by a request that has *already been served*:
that request is why the successor exists.

---

## 2. DC6 — the mechanical compliance record

**C's DC6 answer starts by refusing the premise.** The brief's replacement observable exists
because a design that turns HARD into an instruction has no self-recording refusal. **C loses
no refusal.** Non-compliance under C is not observed after the fact — it is *refused at the
moment of the violation*, by `_trip_begin_gate`. The disqualifier is a signal that is green in
both worlds; C's signal is a raise in one and a state transition in the other. It cannot be
green in both.

**Where the record lives.** Two rows already in the schema, in `spine.json`, joined by a
pointer that already exists:

```json
"why_trail": [ ...,
  {"id": "w-7", "gate": "g2", "why": "<the handoff>", "mechanical": false, "ts": "..."} ],

"tasks": { "g3": { "evidence": [ ...,
  {"id": "e-3", "type": "refresh-request",
   "payload": {"seam": "g3", "why_ref": "w-7"},
   "produced_by": "engine", "ts": "..."} ] } }
```

The join is `payload.why_ref -> why_trail[].id`. The compliance claim is not "a why-record
exists" and not "a request exists" — it is that **the request points at the why-record written
by the advance that closed the gate the agent was in.** That is the release condition
`_trip_begin_gate` already evaluates.

**What makes the ordering auditable, not just the end state.** The journal sidecar
(`spine.json.journal`, :2754) already writes one hash-chained line per *successful* mutating
verb, at the CLI boundary, and the engine never reads it back. So "did a handoff artifact
appear before the next advance at an over-threshold gate" is answerable by reading the chain:

```
advance g2 --why …        # writes w-7
attach  g3 refresh-request {seam: g3, why_ref: w-7}
<run ends>
start   g3                # successor, next session
```

A spine edited to fake this leaves the chain broken. C adds nothing to the journal.

**What makes it go RED.** Three defect shapes, three distinct mechanical signals:

| world | what the engine does | where it is red |
|---|---|---|
| healthy: advance, then request, then stop | `start g3` succeeds for the successor; `current` renders `DIGEST: <handoff>` | — |
| agent ignores the instruction and tries to keep working | `dispatch(start g3)` **raises**; nothing is written | no `start g3` line in the journal; `g3` still `pending` |
| agent stops without closing its gate | it can only file a request keyed to the *previous* gate's why-record (or an id that names nothing) | `why_trail[-1].gate != <the gate left open>` — one predicate over state the engine already holds |

The third row is the only one C observes rather than refuses (the agent never ran the verb C
guards). C renders it: `current` gains a `HANDOFF MISSING` line when a pending
refresh-request's `why_ref` names a why-record whose `gate` is not the gate that was left open.
That is a render on the existing `_why_suffix` chokepoint, not machinery — and it is an
observation, not enforcement, which is the honest weak spot (§6).

One validation earns its keep and is not new semantics: `attach` of type `refresh-request`
refuses a `why_ref` that names no entry in `why_trail`. #179 already declares `why_ref` to be
"the why-record id it was raised against"; today `attach` (:2513) appends any payload blindly,
so a dangling pointer is writable and the DC6 join is forgeable by typo. Making a declared
pointer resolve is enforcing the existing semantics, not adding one.

---

## 3. DC4 — the per-gate override

**Location.** On the task object in the spine: `tasks.<gate>.context_headroom_tokens`. The
precedent is exact and already load-bearing — `why_exempt` is a per-gate policy field read off
the task with `t.get(...)`, absent meaning "default" (:1899). No schema migration, no 68
placeholders, no new file.

**Precedence**, resolved in one place (`_hard_for` above), most specific first:

1. `tasks.<gate>.context_headroom_tokens` — per-gate.
2. `config.context_headroom_tokens` — per-checklist, via the existing `load_config` (:203),
   inline `config` or `config_ref`. Precedent: `rework_cap` (:221).
3. `_PROFILES` via `thresholds_for(reading.model)` — the graded model default, untouched
   (fixed constraint).

Absent at every level is level 3, so a spine that names nothing behaves exactly as today.
An override on an **uncalibrated** model (`window_for` returns `None`) falls back to level 3
rather than computing against a guessed window — the #252 failure mode, refused by
construction.

`_hard_for` is called by both `_trip_advisory` and `_trip_begin_gate`, so the number the agent
is *shown* and the number it is *judged against* cannot diverge. That is the locality argument
for putting resolution in a helper rather than inline at each site.

**Fraction or absolute headroom? — ABSOLUTE TOKENS.** Grounded, not stylistic:

- `_PROFILES` already stores absolute caps and divides by the window (`gauge_reader.py`:76–89,
  124–134), because the context-rot finding is that degradation tracks *absolute* token count,
  not window fraction — onset clusters ~32–100K regardless of advertised window.
- A per-gate override written as a fraction is silently window-relative: `0.60` means 120K on a
  200K model and 600K on a 1M one. That is exactly the miscalibration #252 fixed, re-imported
  at a finer grain and harder to see.
- The question a gate override answers is *"how much room does this gate need to be done at
  all?"* — a token quantity, not a proportion. Headroom states it in the unit the author
  actually reasons in.

`window_for(model) -> int | None` is one total accessor beside `thresholds_for`, returning
`_PROFILES[model][0]` or `None`. It reads an existing column; it adds no table and no policy.

**Exercised once, changing one gate and not its neighbours.** Exactly one gate in the shipped
gated template carries it: the long execution gate — the one gate that must not be entered on
fumes — as `"context_headroom_tokens": 250000`. The demonstration test asserts, on one spine
at one reading: that gate's `start` refuses while its immediate neighbours' `start` does not,
and that `_hard_for` returns the model default for the neighbours.

---

## 4. DC2 — the two tests, and the exact branch to mutate

Both run through `dispatch` with `_read_gauge` patched to a controlled `Reading`, exactly as
`TripTwoBandGatePolicy` does today (`tests/test_checklist_engine.py`:3245), and both read
`(soft, hard)` from the table rather than hardcoding numbers.

**Test 1 — "starts new work above threshold → refused."**
`test_hard_refuses_start_of_next_gate`: `g1` in-progress, `g2` pending, `why_exempt=False`.
At `fill == hard`, `dispatch(advance g1 --why "u1")` succeeds (w-1 written). Then
`dispatch(start g2)` at `fill == hard` raises `EngineError`; `g2` stays `pending`; the message
contains `attach g2 --type refresh-request`; and `assertEqual(cl, before)` — the refusal
mutates nothing.
**Mutation target:** the boundary comparison in `_trip_begin_gate` —
`if reading.fill_fraction < _hard_for(...): return`. Flip `<` to `<=` and the
at-exactly-hard case passes through; the test goes red. (Secondary: delete the
`if v in ("start", "resume")` call site in `dispatch`.)

**Test 2 — "carries a handoff → not refused."**
`test_hard_never_refuses_the_advance_that_carries_the_handoff`: `g1` in-progress,
`why_exempt=False`, `fill == hard + 0.05`, **no refresh-request anywhere in the spine**.
`dispatch(advance g1 --why "handoff")` returns `g1 -> complete`, `_digest(cl) == "handoff"`,
and `current` renders `DIGEST: handoff`.
**Mutation target:** `dispatch`'s `if v == "advance": _trip_hard_gate(cl, ..., base_dir)`
at `checklist_engine.py`:2679–2680. Restoring that line — i.e. today's code — turns this test
red. That is the strongest available mutation: the test is red against `main` right now and
green only after the fix, so it pins the change rather than the implementation.

**Two supporting tests I would not ship without.**

- `test_hard_start_releases_only_on_a_request_keyed_to_the_handoff`: after `advance g1 --why
  "u2"` (w-2), attach a request keyed to `w-1` → `start g2` still refuses; re-attach keyed to
  `w-2` → `start g2` succeeds. **Mutation:** drop the `why_ref=wid` argument at the
  `has_pending_refresh_request` call in `_trip_begin_gate` (gate-only match releases the stale
  request; first half goes green, test red). This carries #190's identity guard across the move
  and proves the release is keyed to *this* handoff.
- `test_unmet_postconditions_surface_instead_of_the_governor` (#431's observed case): `g1`
  in-progress with a failing command postcondition at `fill == hard`;
  `dispatch(advance g1 --why "u")` raises with `postconditions unmet` and **not** with
  `refresh`. **Mutation:** same line 2679–2680.

**Existing tests that must change, and why that is correct.** Four assertions in
`TripTwoBandGatePolicy` / `RefreshRequestIdentity` pin HARD-refuses-`advance`:
`test_hard_refuses_at_and_above_hard_without_refresh` (:3268),
`test_hard_passes_once_refresh_request_exists` (:3287),
`test_hard_refusal_leaves_state_unmutated` (:3296), and
`test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases` (:3372). Each is rewritten
to target `start`. Their current assertion *is* the defect #431 reports, so changing them is the
fix, not collateral — but the count should be stated plainly at review: four tests move.
`test_hard_advisory_on_current_points_at_attach` (:3304) needs its `"BLOCKED"` assertion
re-aimed at the new two-branch advisory text. Everything else in the class — SOFT,
None-reading, survey, no-base_dir — passes untouched.

---

## 5. The four axes

**Depth.** Highest of the three candidates. Interface a caller must learn: **zero new
surface** — no verb, no flag, no evidence type, no payload field. `advance`'s signature is
untouched, so #424 (F) can ship its typed wrapper today; the only thing that changes for F is
`start`'s *failure modes*, and F wraps refusals as errors, not as parameters. What replaces the
machinery is one sentence of doctrine: **HARD blocks starting, never finishing.** That is the
whole interface delta.

**Locality.** Mixed, and I will not claim better. Resolution concentrates well: one new guard
(`_trip_begin_gate`) sitting beside `_trip_hard_gate`'s old home, one threshold resolver
(`_hard_for`) shared by advisory and guard, one advisory branch, one render line. But the guard
now hangs at **two** dispatch sites (`start`, `resume`) where it had one, and `resume` is a verb
the Trip has never touched. Verification stays in one test class.

**Seam placement.** **Holds the line, exactly** — this is C's strongest axis. Both bands stay on
the CLI boundary in `dispatch`. `start`, `resume`, and `advance` all stay pure; their return
values are unchanged, so every existing exact-equality test on verb output keeps passing, and
the `GoldenOutputBriefing` pins on `current`'s first line are untouched. C does not move the
seam; it moves *which chokepoint on the same seam* the guard hangs from — one line, one
condition, in the function that already hosts the doctrine rail and the SOFT suffix.

**Testability.** Every pathway is exercisable through `dispatch` with the existing
`_read_gauge` patch and the existing `_reading()` helper — no new fixture, no new injection
point, no clock. Falsification is two-sided and boundary-exact because thresholds are read from
the table. The one pathway that is *observed* rather than refused — the agent that stops without
advancing (§2, row 3) — is testable only by asserting a render string, which is the weakest test
in the set and is honestly the weakest part of C.

---

## 6. The one thing my constraint makes worse

**C cannot force a handoff. It can only forbid new work.**

An agent that trips HARD and simply *stops* — never running `advance` at all — leaves its gate
`in-progress` with the *previous* gate's understanding standing as the live DIGEST, and C has no
refusal to catch it, because the verb C would have to refuse is the one the agent never ran.
Today's design at least stopped the agent *at* the verb that writes the handoff — uselessly, but
adjacently, with the handoff text already in hand. C moves the refusal one verb further from the
recording, and therefore leans on advisory text to get the `advance` written.

C's answer to that case is a `HANDOFF MISSING` render, not a refusal. That is exactly the
instruction-not-enforcement shape #467 is right to distrust, and under C it survives at precisely
this one spot. A candidate that puts the declaration on `advance` itself (B) closes this hole and
pays for it in interface; C makes the opposite trade and should be judged on it.
