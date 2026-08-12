# Candidate B — intent stated, never inferred

**Constraint:** the agent declares which advance this is. No engine decision rests on guessing
what the agent meant. Authored to that constraint alone.

---

## 1. The mechanism

One new flag on one existing verb: **`advance <gate> --handoff`**.

`--handoff` means: *"this advance closes the gate I am in, and I am stopping here. The `--why`
I am passing is my handoff."* Plain `advance` keeps its existing meaning: *"close this gate and
keep going."* That is the whole distinction #467 asks for, and it is now a token on the command
line rather than a property the engine reads off the world.

At/over HARD, `_trip_hard_gate` refuses plain `advance` and permits `advance --handoff`. The
refusal text changes from "advance is blocked, go file a refresh-request" to "this advance may
only *close* this gate and stop — re-run it as `--handoff --why …`". That single re-aim is the
#431 fix: the refusal now points **at** the only writer of `why_trail` instead of away from it,
so the tripped agent's last understanding lands on the DIGEST the successor cold-starts from.

`--handoff` does four things the agent no longer has to do by hand:

1. **Forces a real why.** `--handoff` with no `--why` is refused, and `--handoff` **overrides
   `why_exempt`** — exemption says "this step carries no new understanding", a handoff says
   "carry my understanding forward"; the handoff wins. So the record always exists.
2. **Marks the why-record** `handoff: true`, so the trail says which record was a seam.
3. **Auto-attaches the `refresh-request`** with correct pointers (`{seam: <resume gate>,
   why_ref: <the id just written>}`). Today the agent hand-types two fields and looks up a
   `<why-id>` placeholder from `current`. That whole ritual disappears.
4. **Opens a handoff pledge** — the DC6 record (§2).

**`_trip_hard_gate` stops consulting `has_pending_refresh_request` entirely.** The #190 `why_ref`
identity filter exists solely to patch a coattails hole in an *inference*-based release: an old
artifact lying around could be mistaken for "I filed my handoff". Stating intent dissolves the
hole — there is no artifact to ride. The predicate keeps its display role in `_why_suffix`; it
stops being load-bearing.

### Why a flag, not a new verb (the constraint's other branch, ruled)

A distinct `handoff` verb would either duplicate `advance`'s postcondition / why / `--from-child`
logic or wrap it, and would hand workstream F **two** signatures to carry plus a place for them
to drift. It would also break the "advance is the only writer of `why_trail`" invariant. Flag.

### The #424 cost, and why it is worth paying

F must carry `handoff: bool = False` on `advance` forever. Keep it minimal: **one optional
boolean with a default**, no new verb, no other signature touched. Any caller that never passes
it behaves exactly as today — a strictly backward-compatible widening, which is the cheapest
permanent change a typed tool can absorb.

It is worth paying because a typed tool's parameter list *is* the agent's affordance surface —
it is where an agent looks to find out what it may do. Putting `handoff` there makes "you may
close this gate and stop" discoverable **at the moment of choosing**, not in a refusal message
the agent only sees after failing. Contrast what F would otherwise ship: a signature whose
behaviour silently depends on repo state the schema cannot name — an `advance` that sometimes
refuses for reasons no parameter explains. That is strictly worse for F than one documented bool.
And a bool is the smallest thing that can be versioned: if the semantics later split (handoff /
pause / abort), it widens to an enum with `False → None`, no removal, no new verb.

### Code sketch

```python
# gauge_reader.py — threshold arithmetic stays in the module that owns _PROFILES
def thresholds_for(model: str, headroom_tokens: int = 0) -> tuple[float, float]:
    window, soft_cap, hard_cap = _PROFILES.get(model, _DEFAULT_PROFILE)
    reserve = max(0, int(headroom_tokens))          # TIGHTEN ONLY — never loosens
    return (max(0, soft_cap - reserve) / window,
            max(0, hard_cap - reserve) / window)
```

```python
# checklist_engine.py
def _headroom_for(cl: dict, gate: str, base_dir: Path | None) -> int:
    """Absolute-token reserve for this gate. Gate wins over checklist config wins
    over 0; every level can only TIGHTEN (negatives clamp), so no override can
    disable the governor and a missing override IS the graded default."""
    t = (cl.get("tasks") or {}).get(gate) or {}
    if isinstance(t.get("context_headroom_tokens"), int):
        return max(0, t["context_headroom_tokens"])
    cfg = load_config(cl, base_dir) or {}
    return max(0, int(cfg.get("context_headroom_tokens", 0) or 0))


def _trip_hard_gate(cl, iid, base_dir, handoff: bool = False) -> None:
    if cl.get("type") != GATED or not iid:
        return
    reading = _read_gauge(base_dir)
    if reading is None:
        return                                       # FIXED: no reading never forces
    _, hard = _gauge_reader.thresholds_for(reading.model, _headroom_for(cl, iid, base_dir))
    if reading.fill_fraction < hard:
        return
    if handoff:
        return          # <<< THE branch both DC2 tests bracket, from opposite sides
    raise EngineError(
        f"{iid}: context at {reading.fill_fraction:.0%} is at/over the hard limit — this "
        f"advance may only CLOSE this gate and stop. Re-run it as a declared handoff so "
        f"your understanding reaches your successor:\n"
        f'  advance {iid} --handoff --why "<what a fresh agent needs to know>"\n'
        f"Starting new work at this fill is what is blocked; recording what you learned is not."
    )
```

```python
def advance(cl, iid, from_child=None, base_dir=None, why=None, mechanical=False,
            handoff: bool = False, session_id: str | None = None) -> str:
    ...                                              # unchanged through postconditions
    if handoff and not (why or "").strip():
        raise EngineError(f"{iid}: --handoff IS the handoff — it needs --why "
                          f"(--mechanical cannot carry one)")
    if handoff:                                      # a handoff overrides why_exempt
        wid = _append_why(cl, iid, why=why.strip(), mechanical=False)
    elif not bool(t.get("why_exempt")):
        ...                                          # existing why/mechanical branch
    t["status"] = "complete"
    if handoff:
        (cl["why_trail"][-1])["handoff"] = True
        resume = active_id(cl) or iid                # next non-terminal gate
        _open_pledge(cl, gate=iid, resume=resume, why_ref=wid,
                     session_id=session_id, base_dir=base_dir)
        attach(cl, resume, "refresh-request", {"seam": resume, "why_ref": wid})
    return f"{iid} -> complete"        # STRING UNCHANGED — exact-equality tests hold
```

```python
# dispatch() — unchanged seam, one extra argument and one extra call
if v in ("start", "advance"):
    _resolve_pledge(cl, getattr(args, "session_id", None), base_dir)
if v == "advance":
    _trip_hard_gate(cl, getattr(args, "id", None), base_dir,
                    handoff=getattr(args, "handoff", False))
```

```python
# CLI
s = sub.add_parser("advance")
s.add_argument("--handoff", action="store_true",
               help="this advance CLOSES this gate and STOPS: --why becomes the handoff "
                    "your successor reads. Required to advance at/over the hard context "
                    "limit; requires --session-id.")
```

---

## 2. DC6 — the mechanical compliance record

**Where it lives:** a new top-level list on the spine, `cl["handoff_pledges"]`, created by
`setdefault` on first write (same backward-compatibility idiom as `why_trail`).

**What one entry contains, at creation:**

```json
{
  "id": "hp-1",
  "status": "open",
  "declared_at_gate": "g4",
  "resume_gate": "g5",
  "why_ref": "w-7",
  "session_id": "S-predecessor",
  "fill_at_pledge": 0.163,
  "ts": "2026-08-08T…Z"
}
```

`--handoff` **requires `--session-id`** — you cannot pledge a session boundary anonymously.

**Resolution.** `_resolve_pledge` runs at the `dispatch` boundary before the next `start` or
`advance` and closes an open pledge exactly once (`open` is the only writable state; a resolved
pledge is never touched again):

```python
def _resolve_pledge(cl, acting_session, base_dir) -> None:
    p = next((x for x in reversed(cl.get("handoff_pledges") or [])
              if x.get("status") == "open"), None)
    if p is None:
        return
    kept = bool(acting_session) and acting_session != p.get("session_id")
    p["status"] = "kept" if kept else "broken"       # KEPT needs a DIFFERENT, NAMED session
    p["resolved_by"] = acting_session
    p["resolved_at"] = _now()
    r = _read_gauge(base_dir)
    p["fill_at_resolve"] = r.fill_fraction if r else None   # corroborating fact only
```

**What makes it go RED.** The instruction is "you may close this gate, then stop." The defective
world is: the agent types `--handoff` to buy passage and then keeps working. Its very next gate
verb is `start <resume_gate>` **under its own session id** — so `acting_session ==
p["session_id"]`, and the engine writes `status: "broken"`, `resolved_by: "S-predecessor"`, plus
`fill_at_resolve` still at/over hard (fill only rises within a session) as corroboration. The
healthy world writes `status: "kept"`, `resolved_by: "S-successor"`, `fill_at_resolve` far below
soft. **Different field values in the two worlds, written by the engine, from a fact the agent
did not supply.**

Two red shapes, one green: `broken` (declared and kept working) and `open` at closeout (declared
and nobody ever came — a stranded handoff) are both distinguishable from `kept`.

**Why it is not gameable.** The agent cannot fake having stopped, because the next actor's
identity is *already required* by machinery that predates this design: `require_session` refuses
any mutating verb from a non-owner or an anonymous caller once a lease is active. A real handoff
therefore *necessarily* involves `release` + a successor's `claim` under a new session id. So
`resolved_by != session_id` is not extra ceremony bolted on to observe compliance — it is the
mechanical consequence of the handoff the agent claims to have performed. Dropping
`--session-id` to dodge the comparison does not work either: silence resolves **broken** (fail
closed, matching the engine's existing `--why` rule), and with a lease claimed the verb is
refused outright.

**Surfacing.** `dispatch`'s `current` output gains one line when the latest pledge is `broken`:

```
HANDOFF PLEDGE BROKEN: hp-1 — session 'S-predecessor' declared a handoff at g4 (16% full)
and then kept working at g5. The digest it promised (w-7) was written; no successor took it.
```

**Deliberate deviation, stated:** `handoff_pledges` allows a single one-way `open → kept|broken`
transition rather than being strictly append-only like `why_trail`. An append-only pledge/
resolution pair would make "is a pledge open?" a fold; the red check has to be a one-line lookup
to be usable by an auditor or a closeout gate. The transition is guarded (only `open` is
writable, once).

---

## 3. DC4 — per-gate threshold override

**Location.** `tasks.<gate>.context_headroom_tokens` (an int) in the spine, alongside
`why_exempt`. Nothing is authored for a gate that does not need one — a missing key **is** the
graded default, so 68 ungraded placeholders are never created.

**Precedence.** Gate key → checklist `config.context_headroom_tokens` (via the existing
`load_config`, so `config_ref` files work unchanged) → `0`. First hit wins; `_headroom_for` is
the only reader.

**Ruling: absolute headroom, in tokens — not a fraction, and not a replacement cap.**

- *Absolute, because `_PROFILES` is already intent-first absolute*: the table stores
  `(window, soft_cap, hard_cap)` in tokens and only divides at the end because Trip's interface
  consumes fractions. Its own comment records why — context-rot degradation is driven by
  absolute token count, not window fraction. A fractional override would mean the same authored
  number reserves 8× more room on a 1M model than on a 200K one, which is exactly backwards.
- *Headroom, not a cap*: a per-gate cap would need re-tuning every time the human moves the
  global default. Headroom composes — "gate g5 is the big one; trip me 40K earlier so I arrive
  with room to do it" — and survives a default change untouched.
- *Tighten-only*: `max(0, cap - reserve)`, negatives clamped. **An override can never raise a
  threshold**, so no gate can quietly opt out of the governor, and no reviewer has to audit 68
  gates for one that disabled it. A reserve larger than the cap clamps the fraction to `0.0`,
  meaning "this gate always trips" — a legitimate, if extreme, setting for a gate that must be
  started fresh.

**Where the arithmetic lives.** `thresholds_for(model, headroom_tokens=0)` — inside
`gauge_reader`, the only module that knows the window and the caps. The engine passes a number
and never does threshold math (it carries an explicit `constraint:no-threshold-values` note).

**Exercised once, on neighbours.** One real gate carries `context_headroom_tokens`; the test
pins one fill at which that gate refuses a plain advance and its immediate neighbour, at the
*same* fill and the *same* model, does not.

---

## 4. DC2 — the two tests, and the exact branch each mutates

Both tests bracket **one** source branch — `if handoff: return` in `_trip_hard_gate` — from
opposite sides. No mutation of that branch can leave both green.

**Test 1 (refusal half) — `test_hard_refuses_plain_advance_above_threshold`**
Gated spine, `g1` in-progress, `_read_gauge` patched to `_reading(hard)`. `dispatch(advance g1)`
**without** `--handoff` → `EngineError`; `g1` still `in-progress`; spine byte-identical to
`before`; message contains `advance g1 --handoff --why`.
*Mutation:* change `if handoff:` to `if True:` (treat every advance as declared). The refusal
never fires → **Test 1 red, Test 2 still green.**

**Test 2 (permission half) — `test_hard_allows_declared_handoff_and_records_pledge`**
Same spine, same patched fill. `dispatch(advance g1 --handoff --why "…" --session-id S1)` →
returns `"g1 -> complete"`; `g1` is `complete`; `why_trail[-1]` has `why == "…"` and
`handoff is True`; `handoff_pledges[-1]` is `{"status": "open", "why_ref": "w-1",
"session_id": "S1"}`; a `refresh-request` with `{"seam": "g2", "why_ref": "w-1"}` is attached
to `g2`.
*Mutation:* change `if handoff:` to `if False:` (ignore the declared flag). HARD refuses even a
declared handoff → **Test 2 red, Test 1 still green.**

**Third test, for DC6 — `test_pledge_breaks_when_the_pledging_session_keeps_working`**
After Test 2's state, `dispatch(start g2, session_id="S1")` → `handoff_pledges[-1]["status"] ==
"broken"`; then the same from `"S2"` on a fresh copy → `"kept"`.
*Mutation:* in `_resolve_pledge`, change `kept = bool(acting) and acting != p["session_id"]` to
`kept = True`. The broken half goes red, the kept half stays green.

---

## 5. The four axes

**Depth.** One optional bool, on one verb, buys: the HARD release, a mandatory why that lands on
the DIGEST (the actual #431 fix), a correctly-pointed auto-attached `refresh-request`, and the
compliance record. Net CLI surface a tripped agent must learn goes **down**: one flag replaces
`attach <gate> --type refresh-request --field seam=… --field why_ref=<why-id>` plus the id
lookup from `current` that the placeholder demands. It also *deletes* load-bearing logic — the
#190 `why_ref` coattails filter stops guarding HARD.

**Locality.** Four touch points, each in the place that already owns the concern: the decision is
one boolean read in `_trip_hard_gate` (dispatch boundary, where Trip already lives); the record
writes in `advance` (already the sole `why_trail` writer); the threshold arithmetic in
`gauge_reader` (already the sole owner of `_PROFILES`); the resolution in `dispatch`. Honest
cost: pledge *resolution* needs a hook on the `start` path, which today carries no trip logic at
all. That is the one genuinely new place.

**Seam placement.** Holds the line, with one stated exception. HARD stays a pre-`advance` guard
in `dispatch`; `_trip_hard_gate` takes the flag as a parameter, and `advance()` never reads the
gauge. But pledge *creation* must be inside `advance()`, because it has to be atomic with the
why-record it points at — writing it from `dispatch` would let a refused advance leave a dangling
pledge, or a successful one leave a pledge pointing at nothing. So `advance`'s **signature**
crosses the seam while its **gauge dependency** does not, and its return string is unchanged
(`"g1 -> complete"`), so the existing exact-equality tests keep passing.

**Testability.** `handoff` is an argument, not an inference, so no test has to arrange a world in
which the engine happens to guess right — the two DC2 tests differ by one keyword and are
bracketed on one branch. The pledge lifecycle is exercised with no gauge mocking at all (the flag
and the session id are both inputs); only the two HARD tests need the `_read_gauge` patch the
suite already has.

---

## 6. The one thing this constraint makes worse

**A declared intent can be declared falsely, and the flag is the cheapest thing in the world to
type.** At HARD, `--handoff` is the only way past, so the flag becomes a toll — and the agent
under pressure to keep working simply pays it and continues. The pledge catches that, but *one
gate later*: the run is already contaminated by the time the record turns red. An inference-based
release at least binds passage to a state the agent had to actually produce; B binds it to a
string. I am trading enforcement-at-the-moment for honesty-of-signal — the engine never claims to
know something it guessed — and paying for it with a compliance signal that is a post-hoc audit
record rather than a gate.

Two sharp edges this leaves, named rather than papered over: a `--handoff --why "done stuff"`
with a worthless handoff text is indistinguishable from a good one to any mechanism here (no
candidate can fix that); and a single-session run that legitimately continues after a pledge —
say the human takes over in the same session — reads as `broken`. That second one is the price of
fail-closed; the fix is a `resume` with a reason, not a softer default.
