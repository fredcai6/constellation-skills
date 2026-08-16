# Float to admiral-568-cleanup — lane B

One decision beyond inherited latitude, plus the budget note that goes with it.
Everything not dependent on this answer has been completed and is listed in
`RESULT.md`.

## The float

**`decision:identity-not-time` (`@grade: settled/human`) is not implementable as
worded, and the grade says only you may unsettle it.**

It reads: *"ownership of a reading is decided by the binding key that produced it,
not by comparing timestamps."*

The engine cannot learn its own binding key. That is measured, not argued:

- The binding key is a **harness** identity — the bare `session_id`, or
  `session_id#agent_id` for a dispatched agent. It is composed by
  `spine_rail.binding_key` from the hook payload, which only the hook ever sees.
- The engine is a CLI process. Its only identity is the lease `session_id` it was
  handed on `claim` — an agent-**chosen** string.
- A binding-store lookup keyed on (spine path, `engine_session`) does **not**
  recover the binding key. **Measured live on this run at 12:46:54Z**: two
  different harness keys — `2271de9b-…` (this Commander) and `aaeefd73-…` (a
  dispatched crew) — carried the *identical* `engine_session`
  (`commander-cleanup-b-context-identity`) against the *identical* `spine.json`.
  The lookup returns two entries. Artifact:
  `measurement/worktree-binding-at-T1.json`.

So every route to satisfying the pre-ruling as worded needs one of:

- **(a)** the harness identity passed into the engine — *"any change to `claim`'s
  semantics beyond what #601 landed"*, which the launch order lists as a
  must-float; or
- **(b)** accepting that identity alone **cannot** replace time, and that #601's
  timestamp comparison stays permanently load-bearing for the sequential
  (relaunch) case while identity handles the concurrent case.

**(b) is what the evidence supports**, and it is a smaller change than (a). But it
contradicts the pre-ruling's own words ("should end up unnecessary"), and
`settled/human` means STOP and float rather than revise in place. Hence this.

### What we would ship under (b)

`gauge-<owner>.json` keyed on the lease session id, **plus** an `owner` field
stamped into the record (the cold critic's graft), **plus** owner *normalization*
rather than rejection. This fixes the **confirmed** defect — concurrent agents
clobbering one file — and leaves #601 in place for relaunch. It does not claim to
complete `identity-not-time`.

### Three measured facts you need to rule with

1. **82 of 395** distinct `engine_session.session_id` values in this checkout fail
   the proposed `[A-Za-z0-9_-]{1,64}` allowlist — every slash-bearing name, and
   they are **current practice**, e.g.
   `constellation/tc1-worktree-identity/g1-implement/implementer/attempt-1`. Two of
   38 live binding entries carry `engine_session: null`, and one carries the
   literal `'$SID'`. Rejecting an unusable owner would therefore take the governor
   away from a large slice of the fleet, permanently, and **invisibly** — losing
   the governor never shows up as a test failure. Normalizing (hash or slug+hash)
   avoids this; it needs your nod because it changes what "identity" means.
2. **A leaseless checklist trips today** (`_reading_predates_claim` fails open to
   using the reading) and would stop tripping under any owner-keyed scheme. That
   is the governor going quiet where it currently governs — the *permit* direction,
   so inside latitude — but it is a real loss of coverage and should be your call,
   not a side effect.
3. **The rename re-arms the ambiguity guard #488 disarmed.** `resolve_gauge_path`
   dedupes candidates *by resolved gauge path*; two spines in one work directory
   currently collapse to one `gauge.json`. Under `gauge-<owner>.json` with
   differing owners they stop collapsing, `len(gauge_paths) > 1` fires, and the
   write is skipped — which is precisely the regression #488 fixed after it "left
   an Admiral's own governor dark for an entire wave." The dedup key must become an
   explicit decision.

## The budget note

This Commander is at **~220,000 absolute tokens against a 150,000 hard cap** — 47%
over — having read only the four artifacts the wave is about. The revised design
now needs re-planning, a second cold critic pass, and a full implement/review/
integrate cycle. Pushing that through this context would be the exact "push
through the trip" failure the governor exists to prevent, while writing the fix
for the governor.

**Recommendation: rule on the float, then relaunch a fresh Commander into this
same spine.** It cold-starts from `current`'s `DIGEST:` and inherits a plan that
has already been cold-critiqued, with all 11 findings triaged. The measurement —
the launch order's first deliverable, and "a deliverable in its own right even if
no code ships" — is **complete and needs no rework**.

## What is NOT blocked on you

Shipped and self-contained regardless of how you rule:

- The settled measurement, twice over (`notes-b.md` §1–2b, `measurement/`).
- The live-caught second entry route — `SessionStart` bind-on-resume (#261) binds
  **any** co-located session to the single active-leased spine it finds, so the
  collision is not limited to orchestrator+subagent. Nobody had enumerated this.
- `#500`'s settled design (`DESIGN_500.md`), which answers its own pre-ruling's
  settle condition and carries **its own separate float** (that design tightens the
  governor, which is also outside latitude).
- The cold critic's 11 findings, triaged, in `CRITIC_TRIAGE.md`.
