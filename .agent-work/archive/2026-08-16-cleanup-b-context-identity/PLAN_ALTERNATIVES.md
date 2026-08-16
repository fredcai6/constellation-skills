# Plan alternatives — #600 attribution scheme

Design-it-twice, run on the one load-bearing interface this wave introduces: how a
gauge reading carries the identity of the agent that produced it. The launch order
names this choice as inherited latitude ("per-agent filename versus an owner field
in the record"), so it is the right thing to author twice.

**Untaken road, surfaced with its reason:** the two candidates were authored
**serially by the Commander**, not in parallel by independent agents. Reason: this
Commander was already over the HARD band (18%) at the `plan` step, and two
dispatched authors would each have had to read the same ~5,000 lines the
comparison turns on. The cold plan critic **was** dispatched for real to a fresh
context, because that is the mechanism whose value depends on having no authoring
context. Recorded as a named untaken road rather than a silent skip.

Both candidates are judged against the same three inherited pre-rulings:
`identity-not-time`, `unattributable-means-no-reading`, `no-new-state-file`.

---

## Candidate A — owner field in the record

**Constraint: change the smallest number of files.**

The writer stamps `record["owner"] = entry["engine_session"]` from the binding
entry it already resolved. `gauge_reader` parses it as an optional fifth field
(precedent: `identity_resolution_ms`, #419). The engine compares
`reading.owner` against its own active lease's `session_id`; a mismatch yields
`None` — no trip — and an advisory says so.

- **Depth** — shallow. The interface a caller must learn grows by one field and
  one comparison.
- **Locality** — good. Three files, no filename or path changes, no migration.
- **Seam placement** — the seam stays where it is: the gauge *file format*. The
  reader keeps its writer-agnostic posture.
- **Testability** — easy. A record with a foreign `owner` is one fixture.

**Why it loses.** It makes a foreign reading *detectable* but leaves the file
itself folder-owned and clobberable. Measured in `probe_cross_key.out`: the
orchestrator's `0.9` still lands on top of the dispatched agent's `0.02`. Under
`unattributable-means-no-reading` the subordinate then correctly gets **no
reading** — so the governor goes **dark for exactly the crews it exists to
govern**, for as long as the orchestrator keeps writing. That is safety without
function: no wrong trip, and no right one either. It also keeps #601's timestamp
comparison load-bearing for every pre-`owner` record, so `identity-not-time`
is only half-honoured.

## Candidate B — per-agent filename  ← recommended

**Constraint: make the collision impossible rather than detectable.**

The writer resolves a binding entry, so it knows `engine_session`. It writes to
`gauge-<owner>.json` beside the spine instead of `gauge.json`. The engine, which
knows its own lease `session_id`, reads `gauge-<own-session>.json`. Two agents in
one work directory write two files and never meet.

- **Depth** — deeper. The caller learns one thing (the gauge is named for its
  owner) and gets ownership, collision-freedom, and the retirement of the
  timestamp comparison out of it.
- **Locality** — change concentrates in `_gauge_path` (engine) and the path
  resolution (writer). ~~The sidecars follow the gauge name for free, since both
  are derived with `.with_name()` off the gauge path.~~ **CORRECTED after cold
  critic F4 — this was wrong.** `.with_name()` is called with a *constant*
  (`SKIP_FILENAME`, `UNCALIBRATED_FILENAME`), on both the writer and reader sides,
  so the sidecars do **not** follow the gauge name. They stay folder-owned, which
  means the collision survives on the sidecar family and one agent can be handed a
  skip flag another agent's writer raised. Making them per-owner is a named cost,
  not free. There is also a namespace collision the allowlist does not exclude: an
  owner named `skip` or `uncalibrated` produces a sidecar's own filename.
- **Seam placement** — moves the seam from *file contents* to *file identity*,
  which is where it belongs: a reading that is not mine is not a record I must
  inspect and reject, it is a file I never open.
- **Testability** — the acceptance test is the probe already written: two keys,
  one work dir, assert both agents keep their own reading.

**Costs, stated plainly.**

1. **Owner names must be filename-safe.** Engine session ids are agent-chosen
   strings. Mitigation: reuse the existing single identity predicate idiom
   (`spine_rail.is_usable_agent_id`, a 1–64 char `[A-Za-z0-9_-]` allowlist) rather
   than inventing a second one; an unusable owner writes nothing, which is
   `unattributable-means-no-reading` applied to the write side.
2. **No fallback to the shared `gauge.json`** (`decision:no-shared-file-fallback`).
   A fallback would reinstate the folder-owned file. The cost is a one-tool-call
   window on first run where the governor is quiet — the same window, and the same
   remedy, the existing `_declined_reading_advisory` already tells agents about
   ("make any tool call, then re-read `current`").
3. **Blast radius must be enumerated by command, not memory** — every artifact
   that asserts the literal name `gauge.json`. That enumeration is gate g1's own
   first task, and its count gets stated.

## Convergence

**Original recommendation: B, with no hybrid.** A is a strict subset of B's safety
property and buys nothing B does not already have.

~~B is also the only one of the two that lets #601's timestamp comparison actually
become unnecessary, which the launch order names as the point of
`identity-not-time`.~~ **RETRACTED after cold critic F1 — this claim was false, and
it was the load-bearing half of the recommendation.**

`engine_session` / the lease `session_id` is an agent-**chosen** string passed to
`claim --session-id`. It is a **lease name, not an agent identity**, and a
relaunched agent deliberately reuses its predecessor's — that is the premise of
#601 and of `job-file-not-agent-file` doctrine. So on the same-id relaunch path the
successor opens `gauge-<same-id>.json`, which is its predecessor's file: exactly
the #477 shape this issue exists to remove. **B and #601 are complementary, not
successor-and-bridge.** B separates *concurrent* agents (the confirmed candidate-2
mechanism); #601's timestamp comparison remains the only thing that separates
*sequential legs of one job*.

**Revised recommendation: B + the critic's graft — name the file for the owner
AND stamp `owner` into the record** — plus owner *normalization* rather than
rejection (critic F2 measured 82 of 395 real session ids failing the proposed
allowlist, all slash-bearing crew names, plus 2 null owners and one literal
`'$SID'` live in the binding store; rejecting them would take the governor away
from a fifth of the fleet). The stamped field is what lets a reader tell "this
file is named for me but was written by something else", which a filename alone
cannot express.

**But the revised design is BLOCKED on a float, and is not frozen.** See
`FLOAT_TO_ADMIRAL.md`: the pre-ruling `decision:identity-not-time` (graded
`settled/human`) specifies ownership by **binding key**, and the engine cannot
learn its own binding key — measured live, two harness keys carried the identical
`engine_session` against the identical spine, so even a binding-store lookup keyed
on (spine, engine_session) comes back ambiguous. Only the ruling tier can unsettle
a `settled/human` decision.

---

## Addendum — leg 2, after `ADMIRAL_RULING-1.md` (2026-08-16)

Candidate B is **amended, not replaced**. The comparison above still holds on its
own terms; four things in it are now settled from above rather than argued here.

- **Filename *and* field (R1).** B chose the filename *over* the record field. The
  ruling takes the cold critic's graft and ships **both**: `gauge-<owner>.json`
  keyed on the lease session id, plus an `owner` field stamped into the record. The
  filename removes the collision, the field makes a mismatch visible if one
  reappears. B's retraction stands — the rename does **not** retire #601's
  timestamp comparison, which stays permanently for the sequential relaunch case.
- **Normalize, never reject (R2).** B's allowlist-and-refuse is **withdrawn**: 82
  of 398 real session ids fail it. Slug plus hash, total over every input.
- **`decision:no-shared-file-fallback` is narrowed (R3).** It applies where a lease
  exists. A **leaseless** checklist keeps exactly today's behaviour — read the
  unowned `gauge.json`, trip on it — because losing that coverage as a side effect
  of a rename is how governors go dark.
- **The `len(gauge_paths) > 1` guard is re-scoped (R4)** rather than re-armed:
  dedupe by owner-keyed path, write every distinct candidate, fire only on a
  candidate that cannot be attributed an owner at all. Pinned by a test in #488's
  exact shape.

**Untaken road, named:** leg 2 did **not** re-run plan-alternatives on the amended
plan. The alternatives exercise answered "filename versus field", and the ruling
answered that question from above with a settled/human decision; a second panel
would have been re-litigating a ruling, not exploring a space. The cold critic's
findings were carried into this revision instead, all 11 disposed of in
`CRITIC_TRIAGE.md`.
