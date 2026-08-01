# Refresh — design B (constraint: MINIMAL-INTERFACE)

**Panel constraint:** the smallest possible NEW handoff artifact + signal — a
pointer-set, nothing re-serialized — plus a one-field "refresh requested"
signal the invoker reads. Reach-up (who refreshes whom) is settled by X3; this
module is packaging + signal only.

## Zero-new-verb, zero-new-file thesis

Module 1 (why-capture, approved) already added everything a refresh payload
would need to *carry the why*: a `why_trail`, evidence type `"why"`, and a
`DIGEST:` line folded into `current`'s existing output via `_why_digest_line`.
Module 4's only genuinely new job is the *signal* — a durable, crash-safe
marker that says "a handoff was requested here," because that fact does not
exist in the corpus at all today (X1: "a refresh-at-a-chosen-seam mechanism
doesn't exist at all today").

So I add exactly one thing: **a new evidence type, `"refresh-request"`,
written through the `attach` verb that already exists** — the same generic,
type-agnostic evidence-bag mechanism module-1-A used to add `"why"` with zero
plumbing. No new verb, no new top-level schema object, no new file. The only
other change is one more optional line in `current`'s output, `_refresh_line`,
built on the identical scan pattern as `_why_digest_line`.

```
attach <active-gate-id> --type refresh-request --field seam=<active-gate-id> --field why_ref=<evidence-id-of-latest-why, or "">
```

That is the entire new interface surface.

## What's added

### 1. Evidence type: `refresh-request`

```json
{
  "id": "e-g2-9",
  "type": "refresh-request",
  "payload": { "seam": "g2-integrate", "why_ref": "e-g2-8" },
  "produced_by": "engine",
  "ts": ""
}
```

- `seam` — the active gate/task id at the moment of request. Redundant with
  `current`'s own `ACTIVE <iid>` line under normal operation (nothing else can
  advance while the request is pending — see Invariants), kept anyway as a
  one-field, self-contained audit record in case the checklist moves between
  request and consumption (force-takeover, manual advance). A purist minimal
  design would drop this field as pure duplication; I keep it because the cost
  is one string and the payoff is a request that is self-describing even if
  read out of context (e.g. pasted into a human chat).
- `why_ref` — the evidence id of the most recent `"why"` record at request
  time, **a pointer, not a copy**. Optional/blank if none exists yet (e.g. a
  refresh requested before any gate has ever closed). This is the "latest
  `why_trail` seq" the fixed context asks for, expressed as the existing
  evidence-id scheme rather than inventing a new counter.
- No `requested_by` / role field: the checklist's own file identity already
  says who this is (`IMPLEMENTER_PLAN.json` → implementer, `spine.json` under
  the commander skill → commander) — adding a role string would duplicate
  what the path already encodes.

### 2. `current` gains one more optional line

```python
def _refresh_line(cl: dict) -> str | None:
    """Most recent pending refresh-request on the ACTIVE task, or None.
    'Pending' = it is the LATEST evidence item on that task — i.e. nothing
    (a why, a command-output, an advance) has happened since. The moment the
    fresh agent does anything further on this task, the request is no longer
    latest and this line silently stops firing — same free-supersession
    pattern _why_digest_line relies on for reopen, just applied as an
    is-it-still-latest check instead of a running summary."""
    aid = active_id(cl)
    if aid is None:
        return None
    ev = cl["tasks"][aid].get("evidence", [])
    if ev and ev[-1].get("type") == "refresh-request":
        p = ev[-1]["payload"]
        return f"REFRESH REQUESTED: seam {p['seam']} (why: {p.get('why_ref') or 'none yet'})"
    return None
```

`current` becomes: `LEASE` line (if any) + `DIGEST` line (if any, module 1) +
`REFRESH REQUESTED` line (if pending, this module) + the `ACTIVE`/`DONE` line
(unchanged). Every tier already calls `current` first thing on every turn —
the doctrine-mandated habit module 1 rode for free, this module rides again.

### 3. The mid-gate why gap — resolved by reuse, not a new field

A real tension: module 1 enforces the why triad only at `advance` (a *closed*
gate). Trip's SOFT question can fire **mid-gate**, before the agent has
anything to advance — so the mandatory why never triggers, and `current`'s
`DIGEST:` line would be stale (last gate's understanding, not this one's).

I resolve this with **zero new fields**: nothing stops an agent from a
*voluntary*, free-standing `attach <iid> --type why --field
now_understand="..."` before or alongside the `refresh-request` attach — it
uses module 1's exact evidence shape, and `_why_digest_line`'s scan already
picks up the latest `"why"` evidence regardless of whether `advance` wrote it
or a bare `attach` did (the function only checks `type == "why" and not
superseded`, never *how* it got there). So a mid-gate refresh gets a fresh
digest for free if the agent bothers to volunteer one, and a documented,
honest staleness risk if it doesn't — this module does not mechanically force
it (that would be module 1's or module 3's job, not this seam's), it only
makes sure the channel that would carry it already exists and needs no
extension.

## How the invoker consumes it

1. Invoker calls `current` on the checklist it already knows the path to (see
   "Spine path — deliberately not carried," below).
2. Sees, in order: lease status, `DIGEST:` (latest understanding), `REFRESH
   REQUESTED:` (if pending), `ACTIVE <iid> [in-progress] — <imperative>`.
   That four-line block **is** the cold-start payload — no file to open
   beyond the checklist itself and the already-durable handoff/launch-order
   file that named the task in the first place.
3. Invoker re-dispatches through the **same per-tier machinery that already
   exists** — this module does not invent a new dispatch protocol:
   - Commander → implementer/reviewer: a fresh `run_crew.py` launch (not
     `--resume`) against the unchanged `IMPLEMENTER_HANDOFF.md`/
     `REVIEWER_HANDOFF.md`; the only behavioral change is *which* branch of
     the existing resumable/relaunch decision the Commander takes — explicit
     now (`REFRESH REQUESTED` seen), instead of inferred from session
     liveness alone (X1's gap: today only CLI session-continue is
     decided-on; this gives Commander a machine-readable "no, actually start
     fresh" trigger even when the old session is technically resumable).
   - Commander → Admiral: Commander's own return message (already required
     by the LAUNCH_ORDER's "Return Shape"/"Stop Conditions") echoes what
     `current` showed; Admiral re-issues a launch order for a fresh
     Commander pointed at the same spine.
   - Admiral → human: same, one level up, human-synchronous.
4. The fresh agent's first action, per existing doctrine at every tier, is
   `current` — it now resumes from `DIGEST` + `ACTIVE`'s imperative with no
   separate resume-artifact to locate. The `REFRESH REQUESTED` line evaporates
   the moment the fresh agent attaches or advances anything (see
   `_refresh_line`'s free-supersession note above) — no explicit "consume"
   or "clear" call is needed.

### Spine path — deliberately not carried

The pointer-set does **not** include the checklist's own file path as a new
field, even though the fixed context's own phrasing suggests one
("spine path + latest `why_trail` seq/digest + current gate/seam id"). The
path is already durable, already known to the invoker, and carrying it again
would be exactly the re-serialization Pocock's don't-duplicate rule forbids:
the Commander that dispatched the implementer already wrote
`IMPLEMENTER_HANDOFF.md` naming the plan's path; the Admiral that dispatched
the Commander already wrote the `LAUNCH_ORDER` naming the spine's work area;
the human who started the Admiral already knows the epic/work-id. In every
reach-up case in this design, **the invoker is the one who created the path
in the first place** — it is never a stranger who needs to be told where to
look. I flag this as the sharpest edge of "smallest": it is exactly enough
*given* that invariant holds, and would be under-specified the moment it
doesn't (see Honest gaps).

## Symmetric recovery

The identical artifact serves both paths, by construction, because it is
never spoken only — it is written through `attach` before the agent can be
said to have "handed off" at all:

- **Intentional refresh (SOFT-accepted or HARD-forced):** the dying agent
  itself writes the `refresh-request` evidence, then goes idle/exits. The
  invoker's next `current` call sees it.
- **Genuine crash (no chance to attach anything):** no `refresh-request`
  evidence exists. `current` shows exactly what X1 already documented for
  cold-start today — lease, `DIGEST` (from the last *closed* gate's why, if
  any), `ACTIVE`'s imperative, plus (Commander/Admiral) `STATE_NOTE.md`. The
  invoker's response is **the same kind of action** either way — re-dispatch
  fresh from `current` — just missing one optional confirmation line. This
  module does not need a special crash-detection branch: "was a refresh
  requested" and "did it crash with nothing recorded" collapse to the same
  `current` read, one with the line, one without.

The one asymmetry, named honestly: a SOFT-accepted refresh that dies *between*
writing `refresh-request` and actually going idle (e.g. host killed mid-write)
could in principle leave a torn write. This module inherits whatever
atomicity the engine's existing JSON write path already provides for every
other verb (`attach` is not special-cased) — no new durability guarantee is
added or claimed here.

## Interaction with Trip (module 3) — the contract, not the design

Trip's HARD band needs one predicate from this module: "has a refresh already
been requested for the active task." This module supplies it as a pure
function symmetric with `_refresh_line`:

```python
def has_pending_refresh_request(cl: dict, iid: str) -> bool:
    ev = cl["tasks"][iid].get("evidence", [])
    return bool(ev) and ev[-1].get("type") == "refresh-request"
```

`advance()` at HARD fill (Trip's concern, not this module's) calls this and
refuses if `False`, pointing the agent at the one `attach --type
refresh-request` command above. This is the entire seam between the two
modules — one boolean function, no shared mutable state, no callback.

## Invariants

- A `refresh-request` evidence item, once it is the *latest* item on its
  task, is visible via `current` until superseded by any further evidence on
  that same task (attach or advance) — never cleared by a separate verb.
- `refresh-request` never blocks anything by itself; it is read-only signal.
  Only Trip's HARD-band check (module 3, outside this module) turns its
  *absence* into a refusal.
- The artifact never duplicates engine state: no copy of the plan, the
  handoff, the mission frame, or the why text itself — only two ids (`seam`,
  `why_ref`) that point at state the checklist and its evidence list already
  hold.
- Reach-up terminates at the human, same as the fixed context states; this
  module adds nothing at that boundary beyond "the human also just reads
  `current`."

## Error modes

| Condition | Result |
|---|---|
| `attach --type refresh-request` on a task not currently active | existing `attach` id-validation refuses it exactly as it would for any other type — no new check needed |
| `refresh-request` attached, then agent attaches/advances anything else before the invoker reads `current` | `_refresh_line` returns `None` (no longer latest) — the request is silently withdrawn by the agent's own further action, which is correct: it kept working |
| `current` on a task with no evidence at all | no `REFRESH REQUESTED` line, same as no `DIGEST` line today |
| HARD band reached, no `refresh-request` present | `advance` refused by Trip (module 3's concern), citing the missing predicate this module exposes |
| Genuine crash, no `refresh-request` written | identical to today's crash-resume path (X1) — no regression, no special case |

## Config

None. No new config file, no threshold, no path convention beyond the ones
that already exist (`.agent-work/<work-id>/...`, unchanged by this module).

## Honest gaps

- **File-continuity assumption, inherited from X1, not solved here.** X1
  flagged as untested whether a relaunched (non-resumable) implementer/
  reviewer crew *reuses* the existing `IMPLEMENTER_PLAN.json`/
  `REVIEW_SURVEY.json` at its fixed path, or a fresh crew overwrites it. This
  module's entire signal lives as evidence *inside* that file. If a relaunch
  in practice starts a new file at the same path, the `refresh-request` (and
  the why_trail digest with it) is destroyed before any invoker reads it —
  silently, with no error, because nothing today detects "this path already
  had content." This is the single biggest risk to "smallest is enough": the
  minimal design is correct *conditional on* file continuity across relaunch,
  a precondition this module assumes but cannot itself enforce (that would be
  a `run_crew.py`/relaunch-path change, out of this module's scope) — flagged
  per the fixed context's own honesty request, not quietly assumed away.
- **"Spine path not carried" is a real bet, not a proof.** It holds for every
  reach-up pair the fixed context names (Commander↔implementer/reviewer,
  Admiral↔Commander, human↔Admiral) because the invoker is always the prior
  dispatcher. It would NOT hold for a hypothetical lateral handoff (peer
  agent to peer agent, no shared dispatcher) — out of scope here since reach-
  up is the only sanctioned direction, but worth naming as the boundary
  condition that would force adding the path field back.
- **No cross-checklist rollup.** An Admiral watching several Commanders (or a
  Commander watching an implementer and a reviewer at once) still polls each
  checklist's `current` individually — this module buys a signal per
  checklist, not a fleet-wide dashboard. Correctly out of scope under this
  constraint (that would be new aggregation machinery, not a minimal pointer)
  but it is a real capability a heavier design could have included.

## Self-assessment

**DEPTH — very strong.** The entire module is one new evidence-type string
(no new enum, no new object), one new ~10-line pure function mirroring an
already-approved sibling, and one predicate function for Trip to call. In
exchange it closes the one gap X1 named as existing nowhere in the corpus —
a durable, crash-safe "refresh was requested here" fact — and does so by
composing two mechanisms (`attach`, `current`) that already existed before
this design touched anything. Very little new surface for a real, previously-
absent guarantee.

**LOCALITY — very strong.** No new file, no new top-level schema key, no new
verb-dispatch entry. The diff is: one new value the `type` field of an
evidence item is allowed to hold (already free-form, so literally zero schema
change), and one new helper function called from `current` alongside the one
module 1 already added. A reviewer sees the whole thing in the same single
screen module-1-A's diff fit in.

**SEAM PLACEMENT — good, with the one real cost named above.** `attach` is
the correct existing seam (a generic, already-untyped evidence sink) and
`current` is the correct existing seam (the call every tier already makes
first). The genuine risk isn't seam *choice*, it's seam *durability*: this
design's minimalism is bought by trusting that the file it writes into
survives a relaunch untouched — a trust X1 explicitly could not confirm.
Candidate A's heavier, tier-specific-artifact approach might sidestep that
exact risk (or might not — untested either way); this candidate accepts it
openly rather than building new machinery to guarantee it, because building
that guarantee is not a "smallest new artifact" problem, it is a relaunch-
path problem.

**TESTABILITY — very strong.** `_refresh_line` and `has_pending_refresh_
request` are both pure functions of a plain dict, no filesystem or subprocess
involvement, directly unit-testable the same way `_why_digest_line` already
is. The spec's own falsifiable test ("must the fresh agent reconstruct
reasoning the trail already holds? — must not") is answerable by one
`current()` call after a scripted `attach --type why` + `attach --type
refresh-request` sequence, asserting both lines appear verbatim with no
additional file reads. The supersession behavior ("does the line survive one
more attach/advance? — must not") is a second one-call assertion, equally
cheap.

**What the constraint cost, overall.** MINIMAL-INTERFACE buys a signal that
is genuinely free to add (reuses two existing verbs, adds one string and two
tiny functions) and genuinely enough for the happy path at every reach-up
pair the fixed context names. What it does *not* buy: any new guarantee about
file continuity across a relaunch (X1's named untested gap stays untested and
this design's correctness leans on it), any carried self-description for an
invoker who is not already the dispatcher (a boundary condition outside
today's reach-up-only scope, but worth knowing), and any cross-checklist
aggregation for an invoker watching several dispatched agents at once. Those
are the honest costs of "smallest" — none of them are silent; all are named
above rather than assumed away.
