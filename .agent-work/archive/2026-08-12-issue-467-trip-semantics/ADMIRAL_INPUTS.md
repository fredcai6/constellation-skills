# Admiral inputs received after the g1 handoff — carry these into the accounting

**Recorded by `commander-w4-467-b` at 0.1536 fill (over hard), as handoff-building, not as new work.**
These arrived from the Admiral *after* I closed `g1-implement` and released the lease. None of them
change the frozen plan. Every one is an input to the **per-done-condition accounting** in
`g5-acceptance`. My successor owns writing them into `ACCEPTANCE.md`; my job was to make sure they
survive the seam, because `current` has no channel for direction that arrives after a handoff.

---

## 1. DC1 — required accounting line: the honest boundary

**Write this into the DC1 accounting.** DC1 is **satisfied for gate-crossing roles** and
**structurally silent for long-single-gate roles.**

Two asserted readings, same machine, same model, same hour. `.agent-work/epic-418-redux/gauge.json`
present, **no `gauge-skip.json`** — a single live binding, measured, not absent:

| Role | Asserted fill | Over hard (0.15)? | Tripped? |
|---|---|---|---|
| `commander-w4-467` (predecessor) | 0.2758 | yes | **yes — at the `plan` boundary** |
| Admiral | 0.2629 | yes | **no** |

Both over by a similar margin; **only one was ever asked.** The corrected conclusion — sharper than
the retracted role-blindness claim — is that the band is not role-blind, the **evaluation points are
role-asymmetric**. A Commander crosses ten gates and meets the question repeatedly. An Admiral sits
inside `execute` for an entire epic — one gate, many hours, many waves — and can run arbitrarily far
past the limit without being asked once.

**This is not a defect in the fix and not a reason to widen #467.** Our design refuses the verbs that
*begin* work; an Admiral deep inside `execute` begins nothing, so it inherits the property unchanged.
State the boundary so no later reader assumes DC1 was universal.

Full write-up: `.agent-work/epic-418-redux/evidence/w4-467-gauge-observation.md` (Admiral's, read-only).

**Commander's judgement (mine, open to reversal):** this belongs in the **DC1 accounting**, not in
triage. It is the honest scope of what the fix covers, and the accounting is the one artifact a
future reader is guaranteed to read. A triage issue would file it away from the claim it qualifies.
My successor should note that I decided this and may overturn it.

## 2. DC5 — two required caveats, both of which outrank the pass

**(a) The round trip closes only under manual intervention.** The Admiral **manually stopped**
`commander-w4-467`'s process; that is the only reason the gauge stopped being overwritten and the
resume could proceed. Verified afterwards: this spine's `gauge.json` read **11.1% at 10:17:59Z**, my
own value. **Unassisted, the round trip does not close.** A DC5 pass reported without that sentence
would be actively misleading — it would tell every future reader the round trip works, when it works
only under an intervention that will not exist in the field. *The Admiral's words: that sentence is
worth more than the pass.*

**(b) The work area was augmented post-handoff.** Commit **`90dbd3c5` — "plan(467): record the
Admiral's wave-4 rulings as binding gate constraints"** — routed the Admiral's three rulings into
`execute.json` and `CRITIC_TRIAGE.md` **after** my predecessor's handoff was written and **before** I
started. So my cold start read a richer work area than the handoff itself created. The Admiral ruled
this **is not a re-brief from memory** (direction arriving after a handoff has to land somewhere, and
`current` had no channel for it) — but the augmentation must be **stated, never silent**. Name the
commit. My predecessor flagged this against its own interest, unprompted, and was right to.

**(c) Agreement across the boundary.** Both ends independently reached the same verdict: the
cold-start-from-`current`-alone doctrine survives **because the work area is rich, not because the
DIGEST is sufficient.** Near end: `TRIP_OBSERVATION.md` §"What the DIGEST could not carry". Far end:
`RESUME_OBSERVATION.md` §"What it did not carry" ("sufficient as an index, not as a substitute").
Put **both** in the accounting — agreement from opposite ends of the same seam is stronger evidence
than either alone.

## 3. Doctrine text is in scope if the fix touches it

`LO-467`'s own handoff instruction — *"write a refresh-request **and** make sure your `current`
carries the DIGEST"* — is **unsatisfiable**, because only `advance` writes a why-record and `advance`
is what the refusal blocks. `global-everyone.md` §reach-up says the same thing. The Admiral has
recorded this as **his** error, not the Commander's, and it is **#431 propagating into the doctrine
written on top of it** — which is the argument for dissolving #431 rather than patching it.

**If the fix touches that doctrine text, the Admiral will not treat it as scope creep.** Say so
explicitly in the return.

## 4. Triage candidates — routed by the Admiral, NOT to be fixed in this run

Do not widen the frozen plan for any of these. Record them; the Admiral carries them up.

1. **Gauge writer: many keys → one path.** #488 guarded *one key resolving to many paths*; the mirror
   case is unguarded. Trip and resume necessarily share a spine, so the design **guarantees** this
   shape at **every** handoff. Fix direction: the writer should decline to write for an agent that
   does not hold the spine **lease** — the engine already knows who owns the spine, so this needs no
   new mechanism. *(This is a gauge-**writer** change; #467's mission frame puts the write side
   explicitly out of scope.)*
2. **The DIGEST is a one-slot mailbox that only the tripping agent can write, and only by advancing.**
   A structural limit on the whole reach-up design; not in DC1–DC6. My own corollary, found the hard
   way: a Commander that trips **mid-`execute`** cannot update the spine's cold-start surface *at
   all*, because `execute` spans every gate. That is the ordinary case, not the edge one.
3. **The reach-up signal has no notion of being *served*.** Three defects, one statement:
   (i) it is **active-gate-keyed**, so a compliant handoff erases its own signal;
   (ii) its records are permanent attachments with empty `ts`, so a **served** request reads as live
   until its gate starts;
   (iii) its remedy hint asks for an id `current` never displays.
   **(ii) nearly cost this wave** — the Admiral's watcher woke him with "relaunch cold" while I was
   twelve minutes old and working at 6.9%, and he came one command from destroying me and then my
   replacement, in a loop. He fixed his instrument by gating on worktree write activity. **The
   mechanism is still broken.**
4. **`why_ref=<why-id>` is a silent no-op.** Verified empirically in g1: copy-pasting the refusal's
   literal placeholder **attaches with exit 0** but does **not** release HARD — the identity check
   never matches. This is what `g2(d)` already plans to fix (emit the concrete id); it is now
   measured, not reasoned, and it independently corroborates `TRIP_OBSERVATION.md` item 4.

## 5. Standing instructions carried forward

- **Commit at clean seams.** Done: `62f564c7` (e0 + g1-implement), `6d34379f` (lease release).
- **Never waive a governor stop on your own judgement.** Reaffirmed by the Admiral after I asked
  rather than waived. It stands.
- **On a trip, file the second refresh-request at the *resume* gate**, or the signal erases itself.
  **Already satisfied here and verified, by a different route:** I did not advance the spine, so the
  active gate is still `execute`, and the pending request targets `execute` keyed to `w-4` — which is
  still `_latest_why_record` on the spine, so #190's identity check matches and the release will
  work. `current` prints `REFRESH REQUESTED: execute (why_ref w-4)`. No second request was needed
  *because I tripped mid-step rather than at a boundary* — the failure mode inverts.
