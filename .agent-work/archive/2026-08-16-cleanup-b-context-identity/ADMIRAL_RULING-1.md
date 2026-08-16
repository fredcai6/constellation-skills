# Admiral ruling 1 — lane B, in answer to FLOAT_TO_ADMIRAL.md

Ruled 2026-08-16 by `admiral-568-cleanup`. R1 and R2 are the **human's**, taken to
them because the grade required it. R3–R5 are mine, inside the Admiral's class.

The float was correct to stop. `decision:identity-not-time` is not implementable
as worded, and the measurement behind that is accepted: the engine is a CLI
process whose only identity is an agent-chosen lease string, the binding key is a
harness identity composed in the hook, and a binding-store lookup does not recover
it — two harness keys carried the identical `engine_session` against the identical
spine at 12:46:54Z. Independently confirmed here: **82 of 398** distinct
`engine_session.session_id` values in this checkout fail the proposed
`[A-Za-z0-9_-]{1,64}` allowlist.

---

## R1 — `decision:identity-not-time` is amended, not satisfied (human)

**Identity handles the concurrent case; time handles the sequential case.** Ship
`gauge-<owner>.json` keyed on the lease session id, plus an `owner` field stamped
into the record (the cold critic's graft). #601's timestamp comparison **stays**,
permanently and by design, for the relaunch case.

The pre-ruling's words *"should end up unnecessary"* are **withdrawn**. They were
written before the measurement and the measurement contradicts them. Record this as
an amendment to a `settled/human` ruling, not as a reinterpretation of it: the
epic's own definition of done said measure first, and this is what measuring first
is for.

What this does and does not claim, stated so the return does not overclaim:
- It **fixes** the confirmed defect — concurrent agents clobbering one file, which
  the timestamp guard is structurally blind to because a foreign write is fresh.
- It **does not** complete `identity-not-time`. Passing the harness identity into
  the engine remains the only route to that, and it is out of scope this wave.

## R2 — Normalize an unusable owner; never reject one (human)

Slug plus hash, so **every** lease session id yields a usable owner key, including
the 82 slash-bearing names that are current fleet practice, the two live bindings
carrying `engine_session: null`, and the one carrying the literal `'$SID'`.

The reasoning is the one the float named: rejecting an unusable owner takes the
governor away from a fifth of the fleet **permanently and invisibly**, because
losing the governor never shows up as a test failure. This repo has been burned
twice by silent governors (#252, #271) and once by a wave-long dark one (#488).
A normalization that is ugly and total beats an invariant that is clean and
partial.

## R3 — A leaseless checklist keeps exactly today's behaviour (mine)

Owner-keying applies **only where a lease exists**. With no lease there is no
owner, so read the unowned `gauge.json` and trip on it exactly as today.

The float is right that going quiet there is the permit direction and therefore
inside your latitude — but it is a real loss of coverage on checklists that are
governed today, and taking it as a side effect of a rename is how coverage
disappears without anyone deciding it should. Fail-safe stays "no attributable
reading yields None"; it does not become "no lease yields nothing".

## R4 — The #488 ambiguity guard does not fire on differing owners (mine)

`resolve_gauge_path`'s `len(gauge_paths) > 1` skip exists because the writer could
not tell **whose** reading it held when one key bound two spines. With the owner in
the filename that question is answered by construction — each candidate is written
under its own owner and cannot overwrite the other.

So: dedupe by resolved owner-keyed path, write **every** distinct candidate, and
fire the guard only when a candidate cannot be attributed an owner at all. Two
spines in one work directory under the same owner still collapse to one file,
which is #488's own case and must stay working.

Pin this with a test that reproduces #488's exact shape — an Admiral's `spine.json`
and its `latitude-interrogation.json` in one work directory — and asserts the write
happens. That regression cost an entire wave of dark governor and must not be
re-armed by a rename.

## R5 — #500: accept the tightening (mine)

Take option (a). A re-claim retires the agent's own pending refresh-request, so its
next `start` is refused where today it is released.

That is the correct behaviour on the merits and it closes the residual #601 named
as a known cost. The practical effect is one extra step, not a stall: an agent over
the band attaches its own refresh-request and then starts, which is the legal
sequence the launch-order template now teaches. Option (b) is declined for the
reason you gave — exempting a same-`session_id` re-claim preserves today's
behaviour by refusing to serve the one case #500 exists for.

`decision:consume-on-lease-change` is hereby settled rather than a guess, with the
settle condition answered by `DESIGN_500.md`.

---

## Scope for the relaunch

**In:** #600 under R1–R4, then #500 under R5 if context allows. #500 may again be
handed back as a design if it does not fit; say so at the boundary rather than
running long.

**Do not redo:** the measurement (`notes-b.md` §1–2b, `measurement/`), the
`SessionStart` bind-on-resume finding, `DESIGN_500.md`, and the cold critic's 11
triaged findings in `CRITIC_TRIAGE.md`. All of it is accepted. Cite it.

**Still fenced:** `scripts/hooks/spine_rail.py` and `scripts/run_crew.py` (lane C),
`scripts/mcp_spine_server.py` and `.mcp.json` (lane A). `checklist_engine.py` stays
yours in the gauge, trip and refresh regions only.

**Lane C landed nothing yet.** When it does, its #549 fix removes one route into
the collision you measured — it does not remove the mechanism, since your
`SessionStart` finding shows co-located sessions collide without any
orchestrator/subagent relationship. Re-measure at your gate rather than assuming
either way.

_Ruled 2026-08-16 by admiral-568-cleanup, on human rulings R1 and R2 taken the same
day._
