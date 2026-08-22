# Plan Critic — w2-ledger hybrid (issue #557 wave 2)

Cold review. No authoring context. Every claim below was checked against the
actual code at HEAD (worktree), not against the plan documents' own line
numbers/quotes, except where noted as unverified.

---

## Finding 1 — G6 grows `mechanical_fields()`'s output vocabulary without growing `apply_episode_delta.py`'s input allowlist; this will hard-refuse episode creation for exactly the override-bearing runs G6 exists to surface

**What I found.** `scripts/apply_episode_delta.py:179`:
`MECHANICAL_ALL_FIELDS = MECHANICAL_SCALAR_FIELDS + ("artifact-ref",)` — the
nine scalar fields plus `artifact-ref`. `_validate_create` (lines 1058-1065)
raises `EpisodeDeltaError` for **any** key under `mechanical` that is not in
this tuple: `"create: misfiled field {key!r} under mechanical — not a
recognized mechanical field"`. This is an unconditional, hard raise, not a
report-only check.

Best-seam-placement's G6 (kept by the hybrid) adds `fields["overrides"] =
override_summary(checklist)` to `episode_capture.mechanical_fields()`'s
returned dict, gated only on non-empty. Neither G6's imperative, close
criteria, nor evidence section mentions `apply_episode_delta.py`,
`MECHANICAL_ALL_FIELDS`, or `_validate_create` at all. G6's own tests
(`tests/test_episode_fields.py`) exercise `mechanical_fields()` directly and
would pass cleanly — they never route the output through
`apply_episode_delta.py`'s validator, so this gap ships untested by the
plan's own stated evidence.

I confirmed `artifact-ref`'s presence in the allowlist is not decorative:
`scripts/mcp_spine_server.py:898` builds one real "create" op's `mechanical`
dict as `{k: fields[k] for k in apply_episode_delta.MECHANICAL_SCALAR_FIELDS}`
— i.e. that specific caller (MCP-door rejection capture) explicitly
whitelists down to the 9 scalars and would silently drop an "overrides" key
before it ever reached `_validate_create` (so that one call site would not
crash, but also would never actually carry `overrides` into an episode,
quietly defeating G6's purpose for that path). But `artifact-ref` is
list-shaped and excluded from `MECHANICAL_SCALAR_FIELDS` precisely so it
*can* be included by some other, more general episode-authoring path (the
docstring above that call site calls `mechanical_fields()` "this repo's ONE
composer for that bin," implying the general workflow is to carry its output
wholesale) — that is the path `MECHANICAL_ALL_FIELDS` exists to gate, and it
is exactly the path a new "overrides" key would trip.

**Why it matters.** Two concrete failure shapes, both real:
- A workflow that copies `mechanical_fields()`'s full output into a `create`
  op's `mechanical` field (the shape `artifact-ref`'s presence in
  `MECHANICAL_ALL_FIELDS` implies exists) starts raising
  `EpisodeDeltaError: misfiled field 'overrides'` the first time it tries to
  capture an episode for a run that used any override — i.e. it fails
  precisely on the runs G6 was built to make visible, and never on the clean
  runs that don't need it. That inverse correlation with test coverage means
  ordinary dogfooding on clean runs would not catch it before it hits a real
  override-bearing closeout.
- A workflow that explicitly whitelists to the old field set (like
  `mcp_spine_server.py`'s rejection-capture code) silently drops `overrides`
  before it ever reaches the episode record — G6 ships with zero effect on
  the actual persisted episode, only on the ephemeral in-memory dict, which
  contradicts the mission's "make closeout render it" intent and G6's own
  stated rationale ("the durable, retrospective-consumed surface").

**Disposition: block-and-fix-before-execute.** Either (a) add `"overrides"`
to `MECHANICAL_ALL_FIELDS` (and decide whether it belongs in
`MECHANICAL_SCALAR_FIELDS` — it doesn't, since it's dict-shaped like
`artifact-ref`, so it wants the same treatment) plus a corresponding
`_validate_create` shape check, wiring the Episode dataclass/
`apply_episode_delta.py` change smallest-diff's own self-score correctly
flagged as "a materially larger, differently-shaped change" — meaning the
hybrid needs to actually decide to pay that cost, not silently avoid deciding
by omission — or (b) explicitly scope G6 to say "`overrides` is composer-only,
deliberately never intended to flow into an episode's persisted `mechanical`
bin," and get that ruling confirmed against how episodes are actually
authored in practice before shipping. Either is executable; leaving it
unaddressed is not.

---

## Finding 2 — smallest-diff's G5, taken "alongside" best-seam's schema, reads a data source that will be stale/wrong under the winning schema

**What I found.** Smallest-diff's G5 computes, inside `finish_work`:
```python
_tl = spine.get("trip_ledger") or []
overrides = {"count": len(_tl), "kinds": sorted({e.get("outcome") for e in _tl if isinstance(e, dict)})}
```
This is correct **only under smallest-diff's own G1-G4**, where `trip_ledger`
stays the one write target and every entry (trip, force-claim,
force-release, waive-authority-mismatch) carries an `outcome` field. The
hybrid instead adopts best-seam's schema: a new `override_ledger` key with a
`kind` discriminant, where `trip_ledger` is **never written again** once G1
(hybrid numbering) lands (`plan-candidate-best-seam-placement.md` G1: "never
again after G3 lands... nothing ever writes into `trip_ledger` again"). Under
that schema, checked against G0's own example envelope: `kind="force-claim"`,
`kind="force-release"`, and `kind="waive"` entries carry **no `outcome` field
at all** — only `kind="trip"` entries do.

**Why it matters.** If the crew lifts smallest-diff's G5 code as literally
written (which is exactly what "take smallest-diff's G5... alongside
best-seam's G6" reads as authorizing), two things happen: (1) on every fresh
spine created after the schema lands, `spine.get("trip_ledger")` is empty
forever (nothing writes it anymore), so `finish_work`'s `overrides` field
reports `{"count": 0, "kinds": []}` on every run regardless of how much
override activity actually happened — silently defeating G5's entire stated
purpose ("visible at the moment of closing"); (2) even on a spine that still
carries legacy `trip_ledger` entries, `e.get("outcome")` returns `None` for
every non-trip kind, so `sorted({...})` over a mixed set containing `None`
and strings raises `TypeError: '<' not supported between instances of
'NoneType' and 'str'` in Python 3 the moment a legacy fixture ever mixes
kinds this way (unlikely for `trip_ledger` alone today, but a live risk if
anyone naively re-purposes this snippet against `override_ledger` directly).

**Disposition: block-and-fix-before-execute.** G5's computation must be
re-specified to read through best-seam's own `override_summary(cl)` /
`_override_entries(cl)` helper (already being built for G6), not
`spine.get("trip_ledger")` + `e.get("outcome")` directly. This is a small
fix, but it is not optional, and the convergence document does not say to
make it — it says to take G5 "alongside" G6, which reads as "as written."

---

## Finding 3 — `dispatch()`'s `release` branch is an early `return`, not a fall-through; G3's "capture before, append after" imperative doesn't reckon with that

**What I found**, reading `scripts/checklist_engine.py:3670-3674` directly:
```python
if v == "release":
    return release(
        cl, args.session_id,
        force=getattr(args, "force", False), reason=getattr(args, "reason", None),
    )
```
This is a hard `return` — function execution ends there. Best-seam's G3 says
to "capture the owning `session_id`... BEFORE calling `release(...)`... After
a successful `release(...)`, if force was passed AND the caller's
`session_id` differs from the captured owner, append `kind="force-release"`"
inside "the early `if v == "release":` arm." Smallest-diff's G2 makes the
same move and even names it "the early return" in its own anchors section,
but neither plan spells out that adding code "after" a `return` statement
requires restructuring the control flow, nor names the risk of getting that
restructuring wrong.

The risk is concrete: `release` is not in `RAIL_VERBS = {"claim", "start",
"advance", "attest", "attach"}` (`checklist_engine.py:468`), and the
archived-path banner check at the bottom of `dispatch()` (`if archived:
message = f"{_ARCHIVED_BANNER}\n\n{message}"`, line 3726) runs
unconditionally for whatever code path reaches it — today `release` never
reaches it (the early return skips straight past). If an implementer
naturally rewrites `if v == "release": return release(...)` into `if v ==
"release": message = release(...)` and lets it **fall through** to
`dispatch()`'s shared bottom logic (the obvious way to "run code after" in
Python), a force-release message would newly and silently start receiving
the archived-path banner it never got before — a real behavior change to
existing (non-ledger) output that nothing in either plan calls out or tests
for.

**Why it matters.** This is exactly the class of thing the mission's "no
unwired checkers / provable, not asserted" discipline is trying to prevent
being introduced by accident: a chokepoint refactor silently changing
unrelated output shape for a verb that isn't even part of this mission's
scope for that behavior.

**Disposition: fix-during-execute.** Cheap to get right (compute the
append inline before the `return`, keep the early return), but call it out
explicitly in the gate's close criteria so a reviewer checks for it: "a
force-release against an archived-path spine still gets zero archived-banner
decoration, exactly as before" should be one of G3's asserted behaviors, not
left implicit.

---

## Finding 4 — G5's "every dict `finish_work` returns" is asserted but only two of four return points are tested

**What I found.** `scripts/spine_lifecycle.py`'s `finish_work` has four
distinct `return` statements: the verify refusal (`stage: "verify"`, ~line
1102), the advance-release refusal (`stage: "advance-release:<substage>"`,
line 1116-1120), the archive refusal (`stage: "archive"`, line 1132), and the
final success dict (line 1149-1161). Smallest-diff's G5 imperative says to
attach `overrides` to "EVERY dict `finish_work` returns — including the
early `stage: "verify"` refusal — not only the final success dict," but its
"Done when"/Evidence sections only specify tests for the populated-success
case, the zero-value-success case, and the verify-refusal case. The
advance-release and archive refusal paths are never named.

**Why it matters.** An implementer following the stated close criteria
literally (which is what close criteria are for) can ship a version where
two of the four exit points are missing `overrides`, and no test in the
plan's own evidence list would catch the regression — a human reading a
refusal at the `archive` stage (step 6, arguably the MOST relevant one,
since by then children are released and reaped and the run really is nearly
done) would be the one silently denied the visibility G5 promises.

**Disposition: fix-during-execute.** Extend G5's test list to explicitly
cover the advance-release and archive refusal return points, not just verify.

---

## Finding 5 — `_override_entries`'s merge order is unspecified, and the "archived spine" framing undersells a live, in-flight collision case

**What I found.** Best-seam's G0 describes `_override_entries` as yielding
`cl.get("override_ledger", [])` entries **plus**, for backward reads,
`cl.get("trip_ledger", [])` entries retagged `kind="trip"` — override_ledger
entries first, legacy trip entries appended after, by the order they're
described. G1's close criteria test this dual-source case but frame it
explicitly as "simulating an archived spine" with **unrelated** `kind`s in
each source (trip in the legacy list, force-claim in the new list) — i.e.
the test never asks what happens to a single checklist's own **continuous**
trip history that straddles the deploy boundary.

That case is not hypothetical: any spine that is claimed and mid-flight at
the moment this migration ships, and that already has `trip_ledger` entries
`tl-1`, `tl-2` from before the deploy, will get its *next* trip event
(`start`/`reopen` refused again) appended to the *new* `override_ledger` as
`ov-1` — because G1 re-points `_append_trip_entry` to write
`override_ledger` unconditionally, with no distinction for "this spine
already has legacy entries." That single checklist's trip history is now
split `tl-1, tl-2` (old key, chronologically first) then `ov-1` (new key,
chronologically later) — one continuous sequence, not two eras. If
`_override_entries` yields override_ledger entries before the retagged
legacy ones (as G0 describes), a reader iterating the merged sequence in
order sees `ov-1, tl-1, tl-2` — reversed relative to when they actually
happened.

**Why it matters.** `begin_over_line_records`/`begin_over_line_records_historical`
as read today don't appear to depend on ordering (they filter, they don't
sort), so this may not break an existing test. But `override_summary()`'s
"full list of entry ids" (G6) and any future consumer that does care about
chronology (a human skimming a closeout summary, a future PR-body composer)
would see a wrong order with no warning that order isn't guaranteed.

**Disposition: fix-during-execute (or accept as a named tradeoff).** Either
sort `_override_entries`'s merged output by `ts`, or explicitly document in
G0's schema note that iteration order across the two sources is unspecified
and no consumer may rely on it — and add the live-transition case (not just
"simulating an archived spine") to G1's test fixture so this is a decision,
not an accident.

---

## Finding 6 — recording every successful waive is defensible by the mission's own naming, but it will make "waive" the dominant, least-informative count in the closeout summary

**What I found.** G3 records every successful `waive`, not just forced or
mismatched ones, on the stated rationale that "a plain policy-allowed
matched-authority waive is still a human accepting risk to skip a control."
`docs/CHECKLIST_SCHEMA.md:267` documents the *expected*, routine path: "A
human who intends an artifact does not hand-mark the condition — they carry
an `override_policy` on it and `waive` it" — i.e. this is not a rare event by
the schema's own design; it's the sanctioned way to satisfy a whole class of
conditions.

**Why it matters.** `override_summary()`'s per-kind counts
(`{"trip": N, "force-claim": N, "force-release": N, "waive": N,
"waive_authority_mismatch": N}`) will show a nonzero `waive` count on a large
fraction of ordinary, unremarkable runs — anything touching an
artifact-policy condition — while `force-claim`/`force-release`/`trip`
entries stay genuinely rare (each requires an actual conflict or a governor
trip). A reader of `mechanical_fields()`'s `overrides` key or the episode
snapshot who sees "overrides: {waive: 1}" cannot tell "routine, expected,
sanctioned artifact intent" from "someone quietly skipped a control" without
separately checking `authority_mismatch`/`forced` on the underlying entries
— the top-level count alone, which is the thing most likely to get glanced
at in a retrospective, is not discriminating for the thing "override" implies
to a reader.

**Disposition: accept-as-a-named-tradeoff, but name it.** This is consistent
with the mission's own framing ("waive" is one of the three named bypass
paths, not "misused waive"), so it is not wrong to include — but neither the
hybrid write-up nor G0's schema doc says out loud that `waive`'s count will
usually be the loudest and least meaningful of the four kinds. Worth one
sentence in G0's doc note so a future reader of the closeout summary doesn't
over-index on a nonzero `waive` count.

---

## Finding 7 — #259's evidence is solid; the residual risk is purely in the out-of-repo closing action

**What I found.** `notes-w2b.md` (repo root) backs the census claim with a
concrete, reproducible command (`grep -rn override-reason
.agent-work/archive/`, 117 files) and names specific issues/waves exhibiting
the pattern, plus states the Honest-Null reasoning for why `consolidate`
stays out of the unified ledger. This is not a bare assertion — it is
checkable evidence, and I consider the underlying call sound.

**Why it matters (residually).** G4's close criteria require "issue #259 has
a closing comment pointing at it" — that is a GitHub action outside this
repo's file-write scope, explicitly called out as such in the anchors
("outside this plan's file-write scope (human/Admiral action on GitHub)").
Nothing in this gate's evidence mechanically confirms that action happened;
the doc note landing in-repo and the issue actually closing are two
different, independently-forgettable steps.

**Disposition: fix-during-execute.** Not a design flaw — just don't let the
gate read as "done" on the doc diff alone; confirm the GitHub-side close
happened before calling G4 closed.

---

## Finding 8 — dropping best-seam's G5 (amend-relocation) is the right call

**What I found.** `amend()`'s own `cl.setdefault("amendments",
[]).append(...)` write (line ~3388) is `amend`'s pre-existing, long-standing
audit trail — structurally the same kind of thing `waive()`'s own
`t["evidence"]`/`c["waived"]` writes are (both stay inside the verb's own
body even after G3 lands; G3 only chokepoint-gates the *new*
`override_ledger` entries, not `waive()`'s pre-existing per-task audit
writes). `amendments` was never claimed to be part of the provable
"engine-written-only, no CLI verb can forge this" property this mission is
actually about — that property applies to `override_ledger` specifically, a
container `amend` was never going to join (both candidates agree `amend`
stays out of the unified ledger). Relocating `amend`'s write site buys
naming/pattern consistency, not any additional forgery-proofing, since a
direct call to `amend()` bypassing dispatch could write `cl["amendments"]`
before the relocation and would still be able to before if a future
regression reintroduced a direct call — the relocation doesn't change what's
provable about `amend`, only where the code lives.

**Disposition: not a real issue — the convergence's reasoning for dropping
this is correct.** Agreed as a legitimate future-issue candidate if `amend`
ever grows its own `override_policy`-shaped check, not before.

---

## Finding 9 — the AFTER-the-verb append pattern (G3) is safe for the stated threat model; one residual exception-path gap is worth naming

**What I traced.** `checklist_engine.main()` (lines 3997-4118): `dispatch()`
mutates the in-memory `cl` dict only. `save(path, cl)` is called exactly
once, **after** `dispatch()` fully returns (line 4106-4107) on the success
path, or inside the `except EngineError` block (line 4092) on a refusal —
never mid-`dispatch()`. So there is no persisted, on-disk intermediate state
between "the verb succeeded" and "dispatch appended the override entry" —
both happen in memory before the one `save()` call. A hard crash there would
abort before any write, leaving the file exactly as it was pre-call, for the
same reason a crash mid-`_trip_hard_gate`+`_run_verb` would today. This is a
stronger safety argument than either plan document actually makes (both
argue from "dispatch already decided this, so it's safe to trust," never
from the persistence-timing argument) — worth stating explicitly as the real
reason it holds.

I also checked the chokepoint-forgery claim directly: grepped all
non-test, non-archive `.py` files for direct calls to
`checklist_engine.claim(`/`.release(`/`.waive(`. None exist. The MCP door
(`scripts/mcp_spine_server.py:743`) calls `checklist_engine.main(argv)` — the
full CLI path — never the bare verb functions. (`scripts/run_crew.py:1771-1773`
does call `checklist_engine.heartbeat()` directly, bypassing dispatch — an
existing, already-accepted direct-call precedent, but for a verb outside this
mission's ledger scope, so it doesn't undermine the claim for
claim/release/waive specifically.)

**Residual gap.** `main()`'s `try/except` only catches `EngineError` (line
4058-4070). If a bug in the *new* post-verb append code itself (not the
verb) raised some other exception — e.g. an edge case in dispatch's
duplicate condition lookup for `waive` that the original `waive()` call
didn't hit — it would propagate out of `main()` uncaught, crashing the whole
CLI invocation with no `save()` at all. That silently discards the verb's
own otherwise-successful mutation (worse than a normal refusal, which still
saves) — not a persistence-corruption risk, but a "the user thinks nothing
happened, but the verb actually ran and its effect vanished" surprise.

**Disposition: accept-as-a-named-tradeoff (verified safe as designed) with
one execute-time note.** Since the append logic is new, its test suite
should include the same duplicate-lookup path `waive()` itself exercises,
so a divergence between the two lookups (dispatch's args-based re-lookup vs.
waive()'s own) gets caught by a test rather than by a crash in production.

---

## Finding 10 (minor) — doctrine citations are imprecise but not fabricated

Both candidate plans cite "this repo's map-as-truth / current-only
documentation doctrine" and "`docs/CHECKLIST_SCHEMA.md`'s own 'current, not
historical' doctrine." I could not find either exact phrase in
`docs/CHECKLIST_SCHEMA.md` itself — this doctrine most likely lives in
`docs/agents/AGENT_GUIDE.md`/`ORCHESTRATOR_CONTEXT.md` as a repo-wide norm
rather than being stated in the schema doc verbatim. Not a substantive
problem, just an imprecise attribution.

**Disposition: not a real issue** — the underlying norm is real (consistent
with this session's own MEMORY.md note on "map-as-truth"), just misattributed
to the wrong specific file.

---

## Summary table

| # | Finding | Disposition |
|---|---|---|
| 1 | G6 grows mechanical_fields() output without growing apply_episode_delta.py's allowlist — will hard-refuse episode creation on override-bearing runs | block-and-fix-before-execute |
| 2 | Smallest-diff's G5 reads `trip_ledger`/`outcome`, stale/wrong under the winning `override_ledger`/`kind` schema | block-and-fix-before-execute |
| 3 | `dispatch()`'s `release` arm is a hard `return`; careless fall-through refactor would newly apply archived-banner decoration | fix-during-execute |
| 4 | G5's "every dict finish_work returns" tested for only 2 of 4 return points | fix-during-execute |
| 5 | `_override_entries` merge order unspecified; in-flight (not just archived) spines can read out of chronological order | fix-during-execute / named tradeoff |
| 6 | Recording every waive dilutes the closeout signal (waive count will usually be routine, not exceptional) | accept-as-a-named-tradeoff |
| 7 | #259's evidence is solid; the actual GitHub close is an unverified out-of-repo step | fix-during-execute |
| 8 | Dropping best-seam's amend-relocation G5 | not-a-real-issue |
| 9 | AFTER-the-verb append pattern is safe given save() timing and grep-verified chokepoint; one exception-path edge worth a test | accept-as-a-named-tradeoff |
| 10 | Doctrine citation imprecise (not found verbatim in CHECKLIST_SCHEMA.md) | not-a-real-issue |

---

## Commander triage (delegated mode — no reachable human; disposed within
inherited latitude "implementation shape; fix-now triage")

| # | Disposition taken | Where it lands in execute.json |
|---|---|---|
| 1 | Fix now: extend `apply_episode_delta.py`'s `MECHANICAL_ALL_FIELDS` with `"overrides"` (dict-shaped like `artifact-ref`, not a scalar) plus a `_validate_create` shape check, so the two vocabularies actually travel together as Finding 1 shows they must. | g3-implement |
| 2 | Fix now: the `finish_work` `overrides` computation reads through `override_summary()`/`_override_entries()`, never raw `spine.get("trip_ledger")`. | g3-implement |
| 3 | Fix now: `release`'s append happens before the existing `return`, and g2's close criteria explicitly assert a force-release against an archived-path spine gets zero archived-banner decoration, unchanged from today. | g2-implement / g2-integrate close criteria |
| 4 | Fix now: g3's test list explicitly covers all four `finish_work` return points (verify, advance-release, archive, success), not just two. | g3-implement / g3-integrate close criteria |
| 5 | Fix now: `_override_entries` yields legacy `trip_ledger` entries (retagged `kind="trip"`) BEFORE `override_ledger` entries — chronologically correct for the one-time-deploy migration case, since no spine's override_ledger entries can predate the code that introduces the key. Documented explicitly in the schema note (not left "unspecified"), and g1's test fixture includes the live-transition case (a spine with legacy trip entries that then receives a fresh trip event post-migration), not only the "simulating an archived spine" case. | g1-implement |
| 6 | Accept as a named tradeoff: one sentence added to the schema doc note (g1) stating the `waive` count is expected to be the loudest, least-exceptional of the four kinds on ordinary runs, so a reader does not over-index on it. | g1-implement (doc) |
| 7 | Fix now (process, not code): g4's close criteria treat the doc note landing in-repo and the GitHub-side #259 close as two separate, both-required facts; RESULT.md states plainly whether the GitHub close was actually performed or is left as a named recommendation to the Admiral (repo action authority for closing an issue is not unambiguously mine per `docs/agents/ORCHESTRATOR_CONTEXT.md`'s Repo Action Authority — local commits are pre-authorized, closing an issue on the human's tracker is not named either way, so it is treated as float-worthy rather than assumed). | g4 |
| 8 | No action — confirmed correct as designed. | (not a gate) |
| 9 | Fix now: g2's test suite includes a case exercising the same duplicate-condition-lookup path `waive()` itself uses, so a divergence between dispatch's re-lookup and `waive()`'s own lookup is caught by a test. | g2-implement |
| 10 | No action — citation attribution only, not a plan defect. | (not a gate) |

All ten findings are addressed inside execute.json below (fix-now, per this
run's standing preference for fixing over filing) except #8/#10, which needed
none. No finding rises to "block the plan from proceeding to execute.json" —
each is a bounded correction to a specific gate's imperative or close
criteria, not a structural objection to the hybrid's schema or seam choice.
