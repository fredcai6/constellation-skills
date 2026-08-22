# Candidate gate plan — best-seam-placement (issue #557 wave 2, w2-ledger)

Constraint under which this candidate was authored: optimize for the seam a fresh
design would choose, even at higher diff cost, over the seam that is cheapest to
reach from today's code. The central seam decision this candidate makes: **retire
`trip_ledger` as a top-level key going forward and replace it with a top-level
`override_ledger`, of which "trip" is one `kind` among several** — because once the
ledger is asked to also hold waive and forced-claim/release events, "trip" stops
describing what the container holds and starts describing only one entry
`kind`. A future maintainer grepping for "where does this repo record an agent
bypassing an enforced control" should land on one name that says that, not on a
name whose literal meaning (a governor tripping on context fill) is a strict
subset of what is now inside it.

---

## G0 — Freeze the seam: envelope schema + naming decision, no code

**Imperative:** Write the `override_ledger` entry envelope and the migration
contract as a doc-first change to `docs/CHECKLIST_SCHEMA.md`, before any Python
changes, so every later gate implements an already-agreed shape instead of
discovering it by accretion (the trap `trip_ledger`'s own history shows — outcome/
fill/hard/model/why_ref accreted one field at a time across #182/#467/#510).

Decision recorded here: entries are flat dicts (not nested envelope+detail) to
minimize churn in the two existing pure selectors (`begin_over_line_records`,
`begin_over_line_records_historical`), which already do `e.get("outcome")` /
`e.get("why_ref")` on the current flat trip shape:

```json
"override_ledger": [
  {"id": "ov-1", "kind": "trip", "gate": "g2", "verb": "start",
   "outcome": "begin-refused", "fill": 0.95, "hard": 0.9,
   "model": "claude-opus-4-8", "why_ref": "w-1", "ts": "..."},
  {"id": "ov-2", "kind": "force-claim", "verb": "claim",
   "session_id": "s2", "previous_session_id": "s1",
   "takeover_reason": "stale lease reclaimed", "ts": "..."},
  {"id": "ov-3", "kind": "force-release", "verb": "release",
   "session_id": "s1", "released_by": "s2",
   "reason": "s1 abandoned mid-gate", "ts": "..."},
  {"id": "ov-4", "kind": "waive", "verb": "waive", "task": "g3",
   "cond": "c2", "authority": "commander", "expected_authority": "human",
   "authority_mismatch": true, "forced": false, "reason": "...",
   "evidence": "e5", "ts": "..."}
]
```

`id` is ledger-scoped (`ov-N`), not per-kind, so ordering across kinds is
recoverable from the id alone — same idiom as `trip_ledger`'s `tl-N`, just
renamed to avoid a reader assuming `ov-4` is the 4th *trip*.

**Migration contract (the seam's hard part):** `trip_ledger` is never written
again after G3 lands, but old archived spines carry it forever, and nothing may
break reading them.
- A new top-level helper `_override_entries(cl, kind=None)` becomes the ONE read
  path: it yields `cl.get("override_ledger", [])` entries (optionally filtered by
  `kind`) **plus**, for backward reads only, every entry of `cl.get("trip_ledger",
  [])` re-tagged with `kind="trip"` in the returned (not stored) dict — so a spine
  written before this change reads identically to one written after it, and nothing
  ever writes into `trip_ledger` again to keep that true.
- `trip_ledger` the KEY stays legal to find on old spines (never migrated in
  place — no rewrite-in-place of archived JSON, which is out of scope and
  would touch archived history) but is retired from `docs/CHECKLIST_SCHEMA.md`'s
  "current" schema block once G3 lands; the doc keeps one short paragraph under a
  "Migrated" heading pointing at `override_ledger`, per this repo's stated
  map-as-truth / current-only documentation doctrine.

**Close criteria / done-when:** `docs/CHECKLIST_SCHEMA.md` shows the new
`override_ledger` block, the entry shape for all four `kind`s, and the
migration-contract paragraph, reviewed for internal consistency (field names
match what G1-G4 below actually implement) before any of those gates starts.

**Evidence:** the diff to `docs/CHECKLIST_SCHEMA.md` itself; no test yet (nothing
to test until code exists) — this gate's evidence is the doc text being
self-consistent with G1-G4's close criteria.

**Anchors:** `docs/CHECKLIST_SCHEMA.md` (schema block near line 77, "Trip ledger"
section near line 459, verb table near line 632).

---

## G1 — Land `override_ledger` + `_append_override_entry`, re-home the trip writer

**Imperative:** Add the top-level `_append_override_entry(cl, kind, **fields) ->
str` function (the `override_ledger` analogue of today's `_append_trip_entry`,
same `setdefault`/never-mutate/never-remove idiom). Re-point `_append_trip_entry`
to call it with `kind="trip"` and the existing trip-specific fields, so
`_trip_hard_gate` — and therefore `dispatch()`'s pre-verb chokepoint call at
`start`/`reopen` — is the ONLY caller that ever creates a `kind="trip"` entry,
exactly preserving today's "engine-written only, no verb handler calls it"
property. Add `_override_entries(cl, kind=None)` per G0's contract. Rewrite
`begin_over_line_records` and `begin_over_line_records_historical` to source
from `_override_entries(cl, kind="trip")` instead of `cl.get("trip_ledger")`
directly — this is the one required touch to the two existing selectors, and it
is a read-path swap only, no change to their filtering logic on `outcome`/
`why_ref`.

**Close criteria / done-when:**
- `cl.get("trip_ledger")` is never assigned to again anywhere in
  `scripts/checklist_engine.py` (grep-verifiable: zero writes, only the
  backward-compat read in `_override_entries`).
- Every existing trip-ledger test in `tests/test_checklist_engine.py` still
  passes unmodified against a checklist that has never seen `override_ledger`
  (proves the rename didn't move the goalposts for the trip mechanism itself)
  AND against a hand-built fixture carrying only the new `override_ledger` key
  with `kind="trip"` entries and no `trip_ledger` key at all (proves the new
  write path feeds the same selectors).
- A fixture carrying BOTH an old `trip_ledger` (simulating an archived spine)
  and a fresh `override_ledger` with unrelated `kind="force-claim"` entries
  reads correctly through `_override_entries(cl, kind="trip")` — the merge does
  not leak non-trip kinds into the trip view and does not drop the legacy
  entries.

**Evidence:** `pytest tests/test_checklist_engine.py -k trip` green; a new test
in the same file exercising the dual-source merge fixture above; a `grep -n
'trip_ledger'` over `scripts/checklist_engine.py` pasted into the PR body
showing only the one read site.

**Anchors:** `scripts/checklist_engine.py:2167` (`_append_trip_entry`), `:2192`
(`begin_over_line_records`), `:2230` (`begin_over_line_records_historical`),
`:2263` (`_trip_hard_gate`), `:3663`/`:3698` (`dispatch`'s pre-verb call site,
unchanged); `tests/test_checklist_engine.py`.

---

## G2 — Fix waive()'s two named defects (#503), keep the write inside waive() itself

**Imperative:** Two surgical fixes inside `waive()` (scripts/checklist_engine.py
:3475-3520), neither touching the ledger yet:
1. Line 3511: `"produced_by": "human"` → `"produced_by": authority` — the
   evidence item should say who actually produced it (the passed `--authority`
   string, e.g. `"commander"`), matching how `attach()` already stamps
   `"produced_by": "engine"` for its own writes rather than a fixed literal.
2. Read `policy.get("authority")` (currently never read at all) and compare it
   against the passed `authority`, case-and-whitespace-normalized. On a
   **mismatch**: do NOT refuse (standing epic rule — a brand-new refusal ships
   report-only). Instead set `authority_mismatch: true` on both the evidence
   payload and the `c["waived"]` marker, and record `expected_authority` (the
   policy's declared value) alongside the actual `authority` passed. On a match,
   or when `policy.get("authority")` is absent (nothing to compare against —
   today's silent-pass stays silent-pass by design, not a defect), no new field
   is added.

**Named promotion trigger** (what must be true before `authority_mismatch` can
become a hard `EngineError` instead of a report-only flag): (a) at least one full
epic's worth of archived runs shows the flag firing on true error, never on a
sanctioned cross-authority waive the Admiral ruling already recognizes (parent
waives child, admiral waives commander); and (b) the Admiral or a doc ruling
names which authority strings are commensurable/ordered (so "commander waiving a
`human`-declared condition" can be told apart from "a stray typo'd authority
string") — until (b) exists, a hard block would refuse the exact sanctioned
five-step handshake `require_session`'s own docstring names verbatim.

**Close criteria / done-when:** `waive()` never blocks on mismatch; every
existing waive test still passes; a new test asserts `produced_by` echoes the
passed authority for a non-"human" value (e.g. `"commander"`); a new test
asserts `authority_mismatch: true` + `expected_authority` appear when
`override_policy.authority` disagrees with `--authority`, and are ABSENT (not
`false`) when there is no `override_policy.authority` to compare against
(absence stays meaningful, matching this codebase's existing convention for
`refusals`/`reopens`/etc.).

**Evidence:** `pytest tests/test_checklist_engine.py -k waive` green including
the two new cases.

**Anchors:** `scripts/checklist_engine.py:3475-3520`; `tests/test_checklist_engine.py`.

---

## G3 — Wire waive/force-claim/force-release into `override_ledger` from `dispatch()` only

**Imperative:** This is the gate the "engine-written only, provably not agent-
forgeable" constraint lives or dies on. All three append calls go in
`dispatch()`, never inside `waive()`/`claim()`/`release()`:

- **claim branch** (`dispatch()`, the `elif v == "claim":` arm, ~line 3680-3684):
  after `claim(...)` returns successfully, read the JUST-WRITTEN
  `cl["engine_session"]` (already mutated by `claim()`) — if `force` was passed
  AND `previous_session_id` is non-null (a genuine takeover happened, not a
  no-op `--force` with nothing to take over), call
  `_append_override_entry(cl, "force-claim", verb="claim",
  session_id=..., previous_session_id=..., takeover_reason=...)`. Dispatch reads
  state `claim()` produced; it does not re-decide anything `claim()` already
  decided, so there is exactly one source of truth for "did a takeover happen."
- **release branch** (`dispatch()`, the early `if v == "release":` arm, ~line
  3670-3674): capture the owning `session_id` from `cl.get("engine_session")`
  BEFORE calling `release(...)` (release mutates status to `"released"` but
  leaves `session_id` in place, so this is a read of pre-call state, safe to do
  first). After a successful `release(...)`, if `force` was passed AND the
  caller's `session_id` differs from the captured owner, append
  `kind="force-release"`.
- **generic verb branch** (`dispatch()`'s `else:` arm that runs `_run_verb`,
  ~line 3685-3703): when `v == "waive"` and `_run_verb` returns successfully,
  read the condition's now-set `c["waived"]` marker (dispatch already has `cl`
  and the target ids from `args`) and append `kind="waive"` with the marker's
  `authority`/`reason`/`forced`/`authority_mismatch`/`expected_authority`
  fields plus `task`/`cond`/`evidence`. This records EVERY successful waive, not
  only forced or mismatched ones — parity with claim/release/trip all being
  fully captured is the point of "one home for every path," and a plain
  policy-allowed matched-authority waive is still a human accepting risk to
  skip a control, which belongs in the same ledger as the others even though it
  is not itself a red flag.

Each of these three call sites reads state a verb already computed and
committed; none of them re-implements verb logic in `dispatch()`, and none of
them lets a verb's own function body write to `override_ledger` directly — the
same separation of "decide" (verb) from "record-that-it-happened" (dispatch)
that `_trip_hard_gate` already models, just applied post-verb instead of
pre-verb because these three are the verb's OWN action being audited, not a
pre-verb refusal gate.

**Close criteria / done-when:**
- `grep -n 'override_ledger' scripts/checklist_engine.py` shows write sites
  ONLY inside `dispatch()` (plus the `_append_override_entry` definition and
  the `_override_entries` reader) — zero write sites inside `waive`, `claim`,
  or `release`'s own function bodies. This is the provable form of the
  constraint: a reviewer runs the grep, not "trust me."
- A test drives `waive`/`claim --force`/`release --force` through
  `checklist_engine.dispatch()` (the CLI path, via `main()`/`dispatch()`, not by
  calling `waive()`/`claim()`/`release()` directly) and asserts the resulting
  `override_ledger` entries; a companion test calls `waive()`/`claim()`/
  `release()` directly (as library functions, simulating anything that is NOT
  the CLI chokepoint) and asserts `override_ledger` is UNCHANGED — proving the
  append genuinely lives at the chokepoint and not just "usually alongside" it.
- `claim --force` with no actual prior owner (no-op force) produces NO
  `force-claim` entry (matches the "genuine takeover only" criterion above);
  covered by a test.

**Evidence:** new tests in `tests/test_checklist_engine.py` (or a new
`tests/test_override_ledger.py` if the file is getting large — see G6);
`pytest tests/ -k override_ledger` and `-k "waive or claim or release"` green;
the grep output pasted into the PR body per the close criterion above.

**Anchors:** `scripts/checklist_engine.py:3663-3708` (`dispatch`), `:1244`
(`claim`), `:1371`(`release`), `:3475`(`waive`).

---

## G4 — `consolidate --override-reason`: close #259 on evidence, no code

**Imperative:** No code change. Write a short doc note (candidate home:
`docs/CHECKLIST_SCHEMA.md` near the `consolidate` verb-table row, or a
standalone note under `docs/agents/` if the Charter's doc layout prefers that —
Charter owns that call) recording the finding already established: a census of
`.agent-work/archive/` (117 files) shows `--override-reason` in constant,
correct use as the standard "APPROVE-with-findings" reviewer pattern; survey
verbs never pass through `dispatch()`'s `TRIP_HARD_GUARDED_VERBS`/
`_trip_hard_gate` machinery at all, so `consolidate` is not a bypass of
engine-enforced GATE-advancement authority in the sense the other three paths
are — it is a reviewer's own recorded judgment about check severity on a survey
verdict. Folding it into `override_ledger` would misrepresent ordinary correct
reviewer behavior as an audit-worthy override event. This closes issue #259's
claim that the flag has "no sanctioned use case" — refuted by the census, not by
deletion or fold-in.

**Close criteria / done-when:** the doc note exists, cites the census count and
the structural reason (survey verbs bypass `TRIP_HARD_GUARDED_VERBS` entirely),
and issue #259 has a closing comment pointing at it.

**Evidence:** the doc diff; the issue-close comment text (both are the
"episode-write / doc note" gate the background section calls for — no pytest
needed because no behavior changed).

**Anchors:** `docs/CHECKLIST_SCHEMA.md` (`consolidate` row, ~line 634 area);
issue #259.

---

## G5 — Relocate `amend`'s audit write to the dispatch chokepoint (consistency, not fold-in)

**Imperative:** `amend()` (scripts/checklist_engine.py:3144) requires
`--authority`/`--reason` "same as waive" per its own docstring, but today writes
its own `cl.setdefault("amendments", []).append(...)` audit entry
(scripts/checklist_engine.py:3388) INSIDE the verb body, not from `dispatch()` —
the pre-G1 pattern the other three paths are being moved away from. Move that
one append call (and only that call — `amend`'s validate-on-copies/commit
logic stays exactly where it is) to `dispatch()`'s generic verb branch,
mirroring G3's waive handling: `amend()` returns/leaves-in-`cl` enough for
`dispatch()` to read the just-committed `cl["amendments"][-1]` and re-append it
itself, OR (simpler, chosen here to avoid a second read-back) `amend()` keeps
building the entry dict internally but returns it via a documented convention
(e.g. stash it transiently, or have `dispatch()` snapshot `len(cl.get
("amendments", []))` before and after the call and treat the delta as
"appended by amend, now co-owned by the chokepoint discipline") — the exact
mechanical choice is an implementation detail for the crew executing this gate,
not a design decision this plan needs to freeze.

**Explicit scope ruling, stated so it cannot be silently re-litigated later:**
`amendments` entries do NOT fold into `override_ledger`. Amend is authoring
(mid-stream re-planning of gate structure that the human/commander ratifies),
not a bypass of an engine-enforced control the way waive/claim/release/trip
are — there is no `override_policy`-shaped expectation being defeated. This
gate only asks amend to follow the same "write-site lives at the chokepoint"
discipline for consistency and future-proofing (e.g. if amend later grows its
own authority-mismatch check against something, the write site is already in
the right place to add it), not to merge its records into the unified ledger.

**Close criteria / done-when:** `grep -n 'amendments' scripts/checklist_engine.py`
shows the append call site inside `dispatch()`, not inside `amend()`; every
existing amend test still passes; a new test proves calling `amend()` directly
(bypassing `dispatch()`) does not write to `cl["amendments"]` (same
chokepoint-proof pattern as G3).

**Evidence:** `pytest tests/test_checklist_engine.py -k amend` green including
the new chokepoint-proof test.

**Anchors:** `scripts/checklist_engine.py:3144-3391` (`amend`), `:3663-3708`
(`dispatch`).

---

## G6 — Closeout visibility: render the ledger where a human/PR/episode actually looks (#504)

**Imperative:** Today nothing outside the engine's own internal trip-advisory
logic reads `trip_ledger` (confirmed: no reference in `scripts/spine_lifecycle.py`
at all), so a completed run that used overrides is currently indistinguishable
from a clean one at closeout. Two additions, chosen to land the visibility at
the two places a human or a future reader actually looks — not just one:

1. **`scripts/checklist_engine.py`**: a small pure summarizer,
   `override_summary(cl) -> dict`, returning counts by `kind`
   (`{"trip": N, "force-claim": N, "force-release": N, "waive": N,
   "waive_authority_mismatch": N}`) plus the full list of entry ids, reading
   only `_override_entries(cl)` — same purity discipline as
   `begin_over_line_records` (no subprocess/gauge/clock).
2. **`scripts/episode_capture.py`**: extend `mechanical_fields()` (line 407)
   with the same idiom already used for `refusals` (line 448-450) — a
   checklist-scoped, presence-means-something field, e.g. `fields["overrides"]
   = override_summary(checklist)` gated on the summary being non-empty (a run
   with zero override entries reports nothing here, same as `refusals`
   absence-is-meaningful convention already established), so the episode
   record — which is what an Admiral's retrospective and a PR-body author
   actually read — stops being blind to override use. This is the seam choice:
   ride the EXISTING mechanical-fields pipeline that already flows into the
   episode snapshot and is already the thing closeout tooling consults, rather
   than inventing a new, unwired "closeout renderer" nothing calls (which
   would violate the standing "no unwired checkers" rule).

Do NOT touch `scripts/spine_lifecycle.py`'s `close_work`/`finish_work` bodies to
add a second, competing summary path — `open_pr`'s body is caller-composed
today (confirmed: no script in this repo currently auto-builds a PR body from
mechanical fields), so wiring through `mechanical_fields()` is the one seam that
is both already-consumed and doesn't require inventing a second, redundant
"closeout summary" concept.

**Close criteria / done-when:** a checklist fixture carrying `override_ledger`
entries of at least two different `kind`s produces a `mechanical_fields()`
result whose `overrides` key correctly counts each kind; a fixture with an
empty/absent `override_ledger` produces a result with NO `overrides` key at
all (absence-is-meaningful, matching `refusals`); `REQUIRED_MECHANICAL_FIELDS`
(episode_capture.py:483) is deliberately NOT extended to require `overrides` —
same reasoning already applied to `artifact-ref` there: it is list/dict-shaped
and its absence is definitionally valid, not a refusal-worthy gap.

**Evidence:** new tests in `tests/test_episode_fields.py` (the existing
mechanical-fields test home, confirmed present) exercising both the non-empty
and empty/absent cases; `pytest tests/test_episode_fields.py` green.

**Anchors:** `scripts/checklist_engine.py` (new `override_summary`, near
`_override_entries`/G1); `scripts/episode_capture.py:407-475`
(`mechanical_fields`, `REQUIRED_MECHANICAL_FIELDS` at :483);
`tests/test_episode_fields.py`.

---

## G7 — Closing gate: map refresh, full local suite, doc consistency pass

**Imperative:** Re-run `python -m scripts.code_map build --root .` (repo
doctrine: map/INDEX.md must stay fresh whenever code changes — G1/G2/G3/G5/G6
all touch `scripts/checklist_engine.py` and `scripts/episode_capture.py`) and
commit the regenerated map alongside the code. Run the full local `pytest
tests/` (the real gate — CI here is Windows-only and known-red, per standing
constraint) and confirm the count is at or above the pre-change baseline (no
net loss of coverage). Re-read `docs/CHECKLIST_SCHEMA.md` end to end once more
against the actually-landed code (not against G0's forecast) to catch any field
that drifted during G1-G6's implementation — this is the same discipline
`docs/CHECKLIST_SCHEMA.md`'s own "current, not historical" doctrine demands of
every change that touches it.

**Close criteria / done-when:** `map/INDEX.md` diff present and reflects the new
symbols (`_append_override_entry`, `_override_entries`, `override_summary`,
`override_ledger`); `pytest tests/` green locally; `docs/CHECKLIST_SCHEMA.md`
reviewed against the final diff (not just G0's plan) with any drift corrected.

**Evidence:** the `code_map build` command's own output/diff; the full local
pytest run's pass count; a final read-through note (can be as short as "doc
verified against landed diff, no drift found" or a list of corrections made).

**Anchors:** `map/INDEX.md`, all files touched by G1-G6.

---

# Self-scoring

**Depth.** This candidate does not stop at "add a ledger and call it done." It
traces the actual defect chain for #503 (both the `produced_by` hardcode and the
never-read `override_policy.authority`), gives the new authority-mismatch check
a named, falsifiable promotion trigger rather than leaving "someday, blocking"
unspecified, and separately resolves the two structural questions the mission
implicitly poses but does not spell out: what happens to `amend`'s own
chokepoint-adjacent write (G5, explicitly scoped OUT of the ledger with a
stated reason, not silently ignored), and where closeout visibility should
actually attach given that nothing today auto-composes a PR body (G6, chosen to
ride the existing `mechanical_fields` pipeline rather than invent a second,
unwired one). The depth cost is real: G0's schema freeze and G5's amend
relocation are both work the smallest-possible-diff version of this plan would
skip, and both are included because skipping them would leave a "why is amend
different" question for the next reader to re-discover from scratch.

**Locality.** Deliberately NOT local in the small-diff sense — that is the
constraint's whole point. G1 touches two existing selectors
(`begin_over_line_records`/`_historical`) to change their read source, which a
minimal patch could avoid by leaving `trip_ledger` as the literal name and just
adding sibling top-level lists for the other kinds. This candidate accepts that
cost because the alternative (three co-equal top-level lists —
`trip_ledger`, plus new `claim_release_ledger`, plus new `waiver_ledger` — or a
single list still called `trip_ledger` holding non-trip entries) is the leaky
abstraction the constraint explicitly asks to be weighed against. Every touch
point is still narrow within each file (one function's read source, one
function's write call site moved), so "not local across files" does not mean
"sprawling within a file" — G3's grep-provable single-write-site criterion is
itself a locality discipline, just applied to the NEW seam rather than the old
one.

**Seam placement.** This is the axis the candidate is built around. The rename
to `override_ledger` with `kind` as the discriminant, backward-compat handled
by a single reader function rather than a data migration, is the fresh-design
answer to "what does a future maintainer grep for." The dispatch-only write
discipline is extended (G3) from the one path that already modeled it
(`_append_trip_entry`/`_trip_hard_gate`) to the two paths that didn't (claim/
release force-paths, waive), and — this is the part a smaller-diff plan would
likely skip — to a FOURTH path (`amend`, G5) that isn't even one of the three
unifying paths, purely for the sake of leaving no visibly inconsistent
write-site pattern behind for a future reader to puzzle over. The one seam
NOT moved is `consolidate` (G4): the candidate treats "correctly excluding a
lookalike" as itself a seam-placement decision worth a gate and a paper trail,
not a thing to leave implicit.

**Testability.** Every code gate (G1-G3, G5-G6) specifies a chokepoint-proof
test pattern: call the verb function directly (bypassing `dispatch()`) and
assert the ledger did NOT move, then call it through `dispatch()`/`main()` and
assert it did. This is a stronger test than "the entry has the right shape" —
it is the only test that actually exercises the "no CLI verb can forge this"
claim rather than asserting it in a docstring, which is exactly the standard
`trip_ledger`'s own existing tests already set and this plan holds every new
path to. G6's absence-is-meaningful assertions (no `overrides` key on a
zero-override run) are specified as explicit close criteria, not left to be
noticed later, matching this codebase's own established convention for
`refusals`/`artifact-ref`. The one place this candidate is honestly weaker on
testability is G0 and G4 (doc-only gates) and G7 (a process gate) — there is
nothing to unit-test there by design, which is why each names a concrete,
checkable artifact (a doc diff, an issue-close comment, a map diff plus a pytest
pass count) as its evidence instead.
