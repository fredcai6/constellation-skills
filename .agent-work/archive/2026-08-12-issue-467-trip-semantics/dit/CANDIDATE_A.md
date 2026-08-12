# Candidate A — zero new CLI surface

Constraint: the handoff-carrying advance must be distinguishable from the new-work advance
using state the engine already holds. No new verb, no new flag on `advance`. Authored to
that constraint alone.

Read against `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, and
`tests/test_checklist_engine.py` in this worktree.

---

## 1. The mechanism

**Thesis: under this constraint the engine must stop *inferring* which advance it is and
start *constructing* it.** At/over HARD the engine does not guess. It decrees:

> The **first** `advance` at/over HARD **is** the handoff. The engine forces it to carry a
> real running understanding, files the reach-up itself, and tells the agent to stop.
> **Every later** `advance` while still at/over HARD is, by construction, a gate that was
> started and worked *above the line* — and that is the only thing refused.

This is exact, not heuristic. `advance(g_n)` closes gate n; reaching `advance(g_{n+1})` at
the same trip means `start(g_{n+1})` plus a whole gate's work happened after the engine said
"wrap up". No intent needs to be read: the second advance's *existence* is the new work.

Three consequences fall out for free:

- **#431 dies.** The refusal no longer points away from the only verb that writes the
  digest. At HARD the agent runs exactly **one** command — `advance <gate> --why "..."` —
  down from today's two-step (`attach` a refresh-request, *then* try to advance).
- **The engine files the `refresh-request` itself**, with the *correct* `why_ref`. Today the
  agent hand-fills `<why-id>` from the DIGEST line (`_refresh_attach_hint`, `:1254`), which
  is a manual step that can be wrong; `#190`'s identity filter then silently mis-matches.
- **Nothing clears the trip.** A hard-band record is only ever consulted while
  `fill >= hard`; `_trip_hard_gate`'s existing `if reading.fill_fraction < hard: return`
  (`:1451`) already short-circuits. A refreshed successor's gauge reads low, so the gate
  reopens by itself. Zero bookkeeping, zero expiry logic.

### Code sketch

```python
# --- scripts/gauge_reader.py ------------------------------------------------
def thresholds_for(model: str, *, hard_headroom_tokens: int = 0) -> tuple[float, float]:
    window, soft_cap, hard_cap = _PROFILES.get(model, _DEFAULT_PROFILE)
    # Overrides TIGHTEN ONLY. headroom clamped >= 0 (a gate may not buy MORE room
    # than the production default -- retuning that default is out of scope), and
    # the resolved hard cap is floored at soft_cap (a gate may never pull HARD
    # below SOFT: that would make the SOFT advisory unreachable and turn every
    # advance into a forced handoff).
    headroom = max(0, int(hard_headroom_tokens))
    return (soft_cap / window, max(soft_cap, hard_cap - headroom) / window)


# --- scripts/checklist_engine.py (Trip section, ~:1439) ---------------------
def _gate_headroom(cl: dict, iid: str, base_dir: Path | None) -> int:
    """Per-gate HARD headroom in TOKENS. First hit wins; see DC4 below.
    Any malformed/negative value resolves to 0 -- a bad override degrades to the
    production default, it never manufactures a trip point."""
    t = cl.get("tasks", {}).get(iid) or {}
    for src in (t.get("context_budget"),
                (load_config(cl, base_dir) or {}).get("context_budget")):
        if isinstance(src, dict):
            v = src.get("hard_headroom_tokens")
            if isinstance(v, int) and not isinstance(v, bool) and v > 0:
                return v
    return 0


def _hard_handoff(cl: dict) -> tuple[str, str] | None:
    """(seam, why_ref) of the newest live ENGINE-FILED hard-band refresh-request,
    or None. THIS IS THE DC6 RECORD -- it exists iff some gate was closed with a
    real handoff while the gauge read >= hard."""
    found = None
    for t in cl.get("tasks", {}).values():
        if not isinstance(t, dict):
            continue
        for ev in (t.get("evidence") or []):
            p = (ev.get("payload") or {}) if isinstance(ev, dict) else {}
            if (ev.get("type") == "refresh-request" and not ev.get("superseded")
                    and p.get("band") == "hard" and p.get("auto") is True):
                found = (p.get("seam"), p.get("why_ref"))   # append order == time order
    return found


def _trip_hard_gate(cl, iid, base_dir, *, why=None, mechanical=False):
    """Returns the (Reading, hard) this advance is the HANDOFF for, or None when the
    band does not apply. Raises only for an advance that starts NEW work."""
    if cl.get("type") != GATED or not iid:
        return None
    reading = _read_gauge(base_dir)
    if reading is None:
        return None                                    # FIXED: None never forces
    _, hard = _gauge_reader.thresholds_for(
        reading.model, hard_headroom_tokens=_gate_headroom(cl, iid, base_dir))
    if reading.fill_fraction < hard:
        return None                                    # (B1) below the line

    prior = _hard_handoff(cl)
    if prior is not None and prior[0] != iid:
        # (B2) THE REFUSAL -- the ONLY refusal in this design. A handoff is already
        # on the record at prior[0]; arriving at a DIFFERENT gate's boundary still
        # at/over hard means a whole gate was worked above the line.
        _record_trip_violation(cl, iid, prior, reading)   # BEFORE the raise: main()
        raise EngineError(                                # persists on error (:2853)
            f"{iid}: context at {reading.fill_fraction:.0%} is at/over the hard limit "
            f"and you already handed off at {prior[0]!r} -- this gate is new work "
            f"started above the line. Stop here and let your invoker refresh you.")

    # (B3) THE HANDOFF ADVANCE -- permitted, but it must actually carry the handoff.
    if mechanical or not (why or "").strip():
        raise EngineError(
            f"{iid}: context at {reading.fill_fraction:.0%} is at/over the hard limit, "
            f"so THIS advance is your handoff seam and must carry a real running "
            f"understanding. Run: advance {iid} --why \"<what a fresh successor needs "
            f"to pick this up>\"  (--mechanical and why_exempt are suspended at HARD).")
    if (why or "").strip() == (_digest(cl) or ""):
        raise EngineError(
            f"{iid}: that --why is byte-identical to the live DIGEST, so this advance "
            f"records nothing new at your handoff seam. Say what CHANGED.")
    return (reading, hard)                              # permit; dispatch files the record


def _file_handoff_record(cl, iid, reading, hard) -> str:
    """THE DC6 GREEN RECORD. Filed by the ENGINE on the success path only, right
    after the handoff advance returns, through the EXISTING `attach` function and
    the EXISTING `refresh-request` type -- so `has_pending_refresh_request` (:1146)
    and the `REFRESH REQUESTED:` line on `current` (:1179) light up unchanged."""
    trail = cl.get("why_trail") or []
    why_ref = trail[-1]["id"] if trail else None   # advance is the ONLY why-writer
    attach(cl, iid, "refresh-request", {
        "seam": iid, "why_ref": why_ref,           # pointers, per #179
        "band": "hard", "auto": True,
        "fill": round(reading.fill_fraction, 4), "model": reading.model,
        "hard": round(hard, 4),
    })
    return (f"\nHANDOFF FILED at {iid} (context {reading.fill_fraction:.0%} >= hard): your "
            f"understanding is now the live DIGEST and a refresh-request is on the record "
            f"for your invoker. STOP HERE -- starting another gate will be refused.")


def _record_trip_violation(cl, iid, prior, reading) -> None:
    """THE DC6 RED RECORD. Deduped on why_ref so a retry loop leaves one row."""
    seam, why_ref = prior
    for ev in (cl["tasks"][iid].get("evidence") or []):
        if (ev.get("type") == "trip-violation"
                and (ev.get("payload") or {}).get("why_ref") == why_ref):
            return
    attach(cl, iid, "trip-violation", {
        "seam": iid, "prior_handoff": seam, "why_ref": why_ref,
        "band": "hard", "fill": round(reading.fill_fraction, 4)})


# --- dispatch() (:2679) -- the policy stays AT THIS BOUNDARY -----------------
        if v == "advance":
            trip = _trip_hard_gate(cl, getattr(args, "id", None), base_dir,
                                   why=getattr(args, "why", None),
                                   mechanical=getattr(args, "mechanical", False))
        message = _run_verb(cl, args, base_dir)
        if v == "advance" and trip is not None:
            message += _file_handoff_record(cl, args.id, *trip)


# --- advance() (:1899) -- the ONE line outside the Trip section -------------
-   if not bool(t.get("why_exempt")):
+   if not bool(t.get("why_exempt")) or (why or "").strip():
```

**Why that one `advance()` line is required and why it is safe.** `why_exempt` must be
suspended at HARD, or an exempt gate closes at the hard band writing *no* why-record — the
DC6 record's `why_ref` would then point at the **stale, pre-trip** digest and compliance
would read green in the defective world. That is the exact disqualifier. The widening is
strictly additive ("an exempt gate that was nonetheless given a `--why` records it"), so no
existing call site changes behaviour, no signature moves, no return string changes — and it
independently fixes a wart: today a `--why` passed to an exempt gate is silently discarded.
No production template sets `why_exempt`; only the Trip test fixtures do.

**Rejected alternative:** having `dispatch` stamp the record by mutating the just-appended
`why_trail` entry. Rejected — `why_trail` entries are never mutated (`:1087`), and buying
byte-purity in `advance()` by breaking that invariant is a bad trade.

---

## 2. DC6 — the mechanical compliance record

**Shape and location.** Ordinary evidence on the gate that was handed off at,
`cl["tasks"][<seam>]["evidence"][]` in `spine.json`:

```json
{ "id": "e3", "type": "refresh-request", "produced_by": "engine", "ts": "",
  "payload": { "seam": "execute", "why_ref": "w-7", "band": "hard", "auto": true,
               "fill": 0.1620, "model": "claude-opus-5", "hard": 0.1500 } }
```

and, on the violation path, on the gate that was refused:

```json
{ "id": "e1", "type": "trip-violation", "produced_by": "engine", "ts": "",
  "payload": { "seam": "reconcile", "prior_handoff": "execute", "why_ref": "w-7",
               "band": "hard", "fill": 0.1710 } }
```

Both are written **only by the engine**, on paths an agent cannot reach: the green record
only after a hard-band advance that carried a non-empty, non-duplicate `--why`; the red
record only inside the refusal, before the raise. The red row survives the exception because
`main()` already `save()`s on the `EngineError` path (`:2853`) — shipped behaviour, not new
machinery.

**What makes it fail RED.** Compliance is a pure function of the spine plus the current
reading, so the healthy and defective worlds differ **in the file**, not only in what got
printed to a terminal:

| world | observable |
|---|---|
| GREEN — complied | exactly one live `auto` hard-band `refresh-request`, its `payload.why_ref` **equal to** `_latest_why_record(cl)["id"]`, and zero `trip-violation` rows |
| RED-1 — ignored the instruction | gauge `>= hard`, active gate still `in-progress`, **no** `auto` hard-band record anywhere. The agent was told at its gate boundary and closed nothing. Visible live on `current`. |
| RED-2 — handed off, then kept working | a `trip-violation` row exists. Only the engine writes it, only on the refusal path. |
| RED-3 — handed off, then the digest moved off it | a live `auto` record exists but `payload.why_ref != _latest_why_record(cl)["id"]` — the successor no longer cold-starts on the handoff. |

RED-1 is the case #467 names ("did a handoff artifact appear before the next advance at an
over-threshold gate"), and it is the case where **there is no refusal at all** — so it is
carried entirely by the *absence* of an engine-only artifact, which an agent cannot forge by
proceeding. That is the property today's design lacks.

**One ruling to flag.** The fixed constraints say `refresh-request` payloads are pointers
only. `band`/`fill`/`model`/`hard` are the *cause* of the record, not copies of checklist
state, and they cannot be pointed at — `gauge.json` is overwritten on every tool call, so
the reading that tripped is gone by the next command. If a reviewer reads that rule
strictly, the fallback costs one row and no mechanism change: keep the `refresh-request`
payload at `{seam, why_ref}` and put the cause in a sibling `trip-handoff` evidence item
that points at the refresh-request's `id`.

---

## 3. DC4 — the per-gate threshold override

**Location and precedence** (first hit wins, resolved in `_gate_headroom`):

1. **Gate** — `spine.json → tasks.<gate>.context_budget.hard_headroom_tokens`
2. **Checklist** — `config.context_budget.hard_headroom_tokens`, resolved by the existing
   `load_config` (`:203`): inline `config`, else `config_ref` →
   `docs/agents/engine-config.json` (the charter-compiled file; template at
   `skills/charter/templates/ENGINE_CONFIG.template.json`)
3. **Model default** — absent/malformed/non-positive → `0` headroom → `_PROFILES` untouched

The graded default stays exactly one table. No gate needs an entry; 67 of 68 inherit and
stay ungraded-placeholder-free.

**Ruling: absolute headroom in tokens, not a fraction.** Three reasons, and the third is
decisive:

1. `gauge_reader.py` already argues this in its own comments (`:53–60`): degradation tracks
   **absolute** token count, onset clusters ~32–100K regardless of window, which is why
   `_PROFILES` is stored intent-first as absolute caps and divided only at the boundary. A
   fraction override would fight the module's own representation.
2. A fraction is meaningless without knowing which model's window divides it: `0.05` on a
   200K model is 10K and on a 1M model is 50K, so the same authored gate would get a 5x
   different real budget depending on who ran it.
3. **Headroom, not a cap.** `hard_headroom_tokens: 40000` says *"this gate needs 40K of room
   to be finished properly"* — a statement about the **gate**, which stays true when the
   production caps are retuned or a new model lands. `hard_cap_tokens: 110000` says
   something about the gate **and** the model, and goes stale the moment either moves.

**Overrides tighten only.** `max(0, headroom)` and the `max(soft_cap, ...)` floor mean a
gate can pull HARD *earlier* but never later, and never below SOFT. This is what keeps the
fixed constraint intact — the production default is a ceiling no gate can raise.

**Exercised once.** `skills/commander/templates/COMMANDER_SPINE.template.json`, the
`execute` gate — the run's longest by a wide margin (it drives a whole child checklist and
dispatches crews), and the one whose imperative already tells the agent to "ensure context
headroom" before entering:

```json
"id": "execute",
"context_budget": { "hard_headroom_tokens": 40000 }
```

Behaviour change, demonstrable and neighbour-free: on a 1M model the default hard is
`150_000/1_000_000 = 0.15`. At `execute` it resolves to `(150_000-40_000)/1_000_000 = 0.11`.
At `fill = 0.12`, `advance execute` **is** the forced handoff seam; `advance reconcile`,
`advance triage`, and `advance plan` are untouched at `0.15`. One assertion pins the
difference and one pins a neighbour.

---

## 4. The two DC2 tests, with disjoint mutation targets

Both drive `dispatch` with `_read_gauge` patched, exactly as `TripTwoBandGatePolicy`
(`tests/test_checklist_engine.py:3221`) already does. Fixtures use **non-**`why_exempt`
gates so the `--why` path is live.

**Test 1 — `test_hard_refuses_the_advance_that_starts_new_work`.**
Seed the prior handoff *directly* (`E.attach(cl, "g1", "refresh-request", {"seam":"g1",
"why_ref":"w-1", "band":"hard", "auto":True, ...})`, `g1` complete, `g2` in-progress) so this
test does **not** depend on the permit path. Patch the reading to `hard`. `dispatch(advance
g2 --why "...")` must raise `EngineError`; assert `g2` stays `in-progress`, `why_trail` is
unchanged, and a `trip-violation` row naming `prior_handoff == "g1"` is on `g2`.
→ **Mutation target: branch (B2)** — the `if prior is not None and prior[0] != iid:` block
in `_trip_hard_gate`. Change its `raise` to `return None`. Test 1 goes red; Test 2 is
unaffected (it has no prior record, so B2's condition is `False` there).

**Test 2 — `test_hard_permits_the_advance_that_carries_the_handoff`.**
No prior record; reading at exactly `hard`. `dispatch(advance g1 --why "<handoff>")` must
return `"g1 -> complete"` **and** the `HANDOFF FILED` suffix; assert `g1` is `complete`,
`_digest(cl) == "<handoff>"`, and the `auto` hard-band `refresh-request` on `g1` carries
`why_ref == _latest_why_record(cl)["id"]`.
→ **Mutation target: branch (B3)** — the terminal `return (reading, hard)` in
`_trip_hard_gate`. Replace it with today's blanket refusal (`raise EngineError(...)`). Test
2 goes red; Test 1 is unaffected (it raises at B2 and never reaches B3).

Two further tests keep the band honest but are not the DC2 pair: `--mechanical` at HARD
refuses with the "this advance is your handoff seam" text (pins B3's first guard), and a
`None` reading passes both gates untouched (the fixed no-op rule, already covered by
`test_none_reading_never_forces_and_gives_no_advice`).

---

## 5. The four comparison axes

**Depth.** Highest available, by construction: the behaviour delivered per unit of interface
a caller must learn is unbounded, because **the interface delta is zero**. `parse_args` is
untouched; `advance`'s CLI signature is frozen, so **#424 (F) can ship its typed wrapper
today** and pays nothing for this issue. What the agent learns is a *sentence*, delivered by
the engine at the moment it applies, not an API. And the agent's action count at a trip goes
**down** — one command instead of two.

**Locality.** Strong. Every new line lives in the Trip section of `checklist_engine.py`
(`:1399–1466`) plus one keyword argument in `gauge_reader.thresholds_for`. Exactly one line
sits outside: `advance()`'s widened `why_exempt` guard. No skill/doctrine rewrite is needed
for the mechanism, because the remedy text is engine-authored and travels with the refusal.
Verification concentrates in one test class.

**Seam placement.** **Holds the line, with one named exception.** All *policy* — the gauge
read, the band comparison, the refusal, the record filing — stays at the `dispatch` CLI
boundary. `advance()` performs no gauge read, no I/O, no band comparison; its signature and
every return string are unchanged, so the existing exact-equality tests keep passing. The
exception is that one boolean, so `advance()` is no longer *byte*-untouched — but it stays
*pure*, which is the property the line actually protects. Two existing Trip tests change
**deliberately**: `test_hard_refuses_at_and_above_hard_without_refresh:3268` (that behaviour
*is* the #431 defect) and `test_hard_refusal_leaves_state_unmutated:3296` (a refusal must now
leave the violation row — that *is* DC6). Both are the issue, not collateral; its replacement
asserts state is unmutated **except** for the appended `trip-violation` row.

**Testability.** Every pathway is exercisable through `dispatch` with a patched
`_read_gauge`, as the suite already does. The compliance verdict is a pure function of the
spine JSON plus a reading, so it is assertable in a unit test *and* auditable after the fact
against any real run's spine, with no agent in the loop. The one pathway that cannot be
falsified mechanically: handoff **quality**. The engine proves a non-empty, non-duplicate
understanding was written; it cannot prove it was a *good* one. That is consistent with the
existing v1 doctrine ("we do not police reason quality", `:1209`), and the byte-identity
check is the cheapest real bite available without crossing into quality-policing.

---

## 6. The one thing my constraint makes worse

**The engine never hears the agent's intent, so it substitutes a decree — and when the
decree is wrong, the agent pays.**

Concretely: an agent genuinely two minutes from the end of its run crosses HARD at the
`triage` boundary. It is forced to write a full cold-start handoff for a successor that will
never exist, the engine files a reach-up its invoker must now read and dismiss, and its
`review` gate is then **refused** — a run that was about to finish cleanly ends in a stall
that requires a human. Candidate B's agent says "this one isn't a handoff, I'm nearly done"
and is believed; mine has no way to say it.

The deeper version: under this constraint the engine structurally cannot distinguish *"I
filed my handoff"* from *"the engine filed one on my behalf while I was mid-thought"* —
because under my design **they are the same event**. I bought a zero-cost interface by
making the mechanism deaf to the one fact the agent has and the engine does not. My defence
is that this deafness is *safe by direction* (it errs toward recording a handoff nobody
needed, never toward losing one somebody did) and that the escape hatch already exists and is
already recorded — the human `waive` verb — but it is a real, foreseeable cost paid by every
run that happens to finish near the line.
