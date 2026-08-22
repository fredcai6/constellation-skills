# Candidate gate plan — smallest-diff (issue #557 wave 2, "w2-ledger")

Constraint under test: minimize code touched and concepts introduced. No new
top-level key, no new module, no new abstraction where an existing structure
can be widened in place. `trip_ledger` (scripts/checklist_engine.py:2167-2263)
is reused, verbatim key name, as the one unified home. `_append_trip_entry` is
generalized in place, never replaced or duplicated.

Everything below stays inside the owned surface: `waive()`, forced
claim/release, `consolidate`, the trip ledger, amend's authority handling.
Nothing touches `generate_spine.py`, `specs/`, the attest/condition surface,
or shipped spine templates.

---

## G1 — Widen `_append_trip_entry` to accept a non-gauge entry, in place

**Imperative.** Change `_append_trip_entry`'s signature
(scripts/checklist_engine.py:2166-2187) so `reading` and `hard` become
optional (default `None`). When `reading is None`, emit `fill`/`hard`/`model`
as `None` instead of calling `round(reading.fill_fraction, ...)` (which would
raise on `None`). No new parameter names, no new function, no new list, no
change to the `trip_ledger` key or the `tl-N` id scheme. Every existing call
site (`_trip_hard_gate`) is untouched and its three existing outcomes
(`begin-refused`, `begin-released`, `begin-instructed`) keep emitting the
exact same shape they do today.

**Done when.** `_append_trip_entry(cl, gate, verb, outcome, reading=None,
hard=None, why_ref=None)` appends `{id, gate, verb, outcome, fill: None,
hard: None, model: None, why_ref, ts}` and nothing else in the codebase calls
it yet outside `_trip_hard_gate`.

**Evidence.** `pytest tests/test_checklist_engine.py -k trip` unchanged and
green (proves zero regression on the three existing outcomes — same
assertions, same values). One new direct unit test calling the widened
signature with `reading=None` and asserting the `None` fields.

**Anchors.** scripts/checklist_engine.py:2166-2187; tests/test_checklist_engine.py.

---

## G2 — Record forced claim/release into `trip_ledger`, written only from `dispatch()`

**Imperative.** In `dispatch()` (scripts/checklist_engine.py:3663-3702), at
the two existing branches that already call `claim(...)` and `release(...)`
directly (the `elif v == "claim":` branch and the `if v == "release":` early
return — dispatch already calls these two functions itself, not through
`_run_verb`), add: if the call succeeds AND `getattr(args, "force", False)`
is true, call the widened `_append_trip_entry(cl, gate=active_id(cl), verb=v,
outcome=f"{v}-force", reading=None, hard=None, why_ref=None)`. `claim()` and
`release()`'s own bodies (scripts/checklist_engine.py, lines ~1259-1354 and
~1401-1416) are not modified — they keep writing `engine_session`'s
`previous_session_id`/`takeover_reason` exactly as today. This is additive:
the same forced-override fact now has two homes — `engine_session` (current
state, overwritten by the next claim) and `trip_ledger` (append-only,
survives the next claim).

**Why this is the chokepoint, provably.** The only two call sites of
`_append_trip_entry` after this gate are `_trip_hard_gate` and these two
`dispatch()` branches — both are lines inside `dispatch()`'s own body or a
function `dispatch()` calls before `_run_verb` runs. Neither `claim()` nor
`release()` nor `waive()` (G4) ever calls it. This is checked by a grep-based
test (see Evidence), not asserted in prose.

**Done when.** `claim --force --reason ... ` against an already-owned lease
appends exactly one `trip_ledger` entry with `outcome: "claim-force"`; same
for `release --force --reason ...` → `"release-force"`. A non-forced
claim/release (including the idempotent same-session resume and a stale-lease
reclaim without `--force`) appends nothing.

**Evidence.**
- pytest cases in tests/test_checklist_engine.py: forced claim on a
  different active lease appends one entry; forced release (non-owner)
  appends one entry; plain claim/idempotent resume/stale reclaim append zero.
- A static test: `grep -n "_append_trip_entry(" scripts/checklist_engine.py`
  has exactly the call sites named above (`_trip_hard_gate`, and the two
  `dispatch()` branches) — codified as a pytest test that reads the source
  file and asserts the call sites are inside `dispatch`'s or
  `_trip_hard_gate`'s function body (by line-range check against
  `ast`/`inspect`, not just string count), so a future verb quietly calling
  it directly fails this test.

**Anchors.** scripts/checklist_engine.py `dispatch()` (~3663-3684); `claim()`
(~1259-1354, unmodified); `release()` (~1401-1416, unmodified);
tests/test_checklist_engine.py.

---

## G3 — Fix `waive()`'s hardcoded `produced_by` (issue #503, defect 1)

**Imperative.** At scripts/checklist_engine.py:3511, replace the literal
`"produced_by": "human"` with `"produced_by": authority` — `authority` is
already validated non-empty three lines above (`if not (authority or
"").strip(): raise EngineError(...)`), so this is a one-token substitution,
no new validation, no new field.

**Done when.** `waive(cl, iid, cond_id, which, authority="commander",
reason=..., forced=...)` produces an evidence item whose `produced_by` reads
`"commander"`, not `"human"`.

**Evidence.** pytest case in tests/test_checklist_engine.py asserting
`produced_by` for a non-"human" `--authority` value; existing waive tests
that pass `authority="human"` keep passing unchanged (same value, still
correct by coincidence of the input, not by hardcoding).

**Anchors.** scripts/checklist_engine.py:3505-3517 (`waive()`).

---

## G4 — Record `override_policy.authority` vs `--authority` mismatch, report-only (issue #503, defect 2)

**Imperative.** `waive()` itself gets no new logic beyond G3 — the mismatch
check is a POST-HOC read done by `dispatch()`, mirroring G2 exactly, so the
chokepoint property extends to this case for free instead of needing a new
justification.

In `dispatch()`, in the generic mutating-verb branch (the `else:` at
~3676-3701, which is where `waive` already runs via `_run_verb`), after
`_run_verb` returns successfully AND `v == "waive"`: look up the same
condition `waive()` just touched (`task(cl, args.id)`, then find `args.cond`
in `preconditions`/`postconditions` per `args.which` — the exact same lookup
`waive()` itself performs, duplicated as a ~4-line read, not factored into a
shared helper, because factoring would mean `waive()` and `dispatch()` share
a private helper that must then itself be scrutinized for chokepoint-safety;
a plain duplicate read is smaller and unambiguously safe). Read
`policy.get("override_policy", {}).get("authority")`. If it is set and,
case/whitespace-normalized, does not equal `args.authority`, call
`_append_trip_entry(cl, gate=args.id, verb="waive",
outcome="waive-authority-mismatch", reading=None, hard=None,
why_ref=None)` — and nothing else. The waive itself already succeeded before
this check runs; this gate never blocks it, per the standing report-only
rule for a brand-new refusal.

**Named promotion trigger (do not implement now).** `waive-authority-mismatch`
stays report-only until BOTH: (a) a corpus census (same methodology already
used to clear `consolidate --override-reason` in this plan's G7 — a scan of
`.agent-work/archive/`, this time filtered to `trip_ledger` entries with this
outcome) across at least one full epic-wave shows every historical mismatch
was a genuine authority violation, with zero legitimate cross-role cases
(e.g. an Admiral waiving on a condition declared `authority: "commander"`,
which is presumably fine and would falsify a blanket refusal); AND (b)
`docs/CHECKLIST_SCHEMA.md`'s `override_policy.authority` field
(currently documented, line 284, as "advisory") is explicitly upgraded to a
documented enforceable contract in the SAME change that promotes the check —
so a template author who names an authority today is not retroactively
surprised by an enforcement nobody told them was coming.

**Done when.** Waiving a condition whose `override_policy.authority` differs
from the passed `--authority` still succeeds exactly as before (same return
string, same evidence/`waived` marker) and appends exactly one `trip_ledger`
entry naming `gate` (the task id) and `outcome: "waive-authority-mismatch"`.
A matching authority, a case/whitespace-only difference, an absent
`override_policy`, or an absent `override_policy.authority` all append
nothing.

**Evidence.**
- pytest cases: mismatched authority → one ledger entry, waive still
  reports success; matching authority (exact and case/whitespace-varied) →
  zero entries; forced waive with no `override_policy` at all → zero entries
  (nothing to mismatch against).
- The same grep/AST-based chokepoint test from G2, extended: `waive()`'s own
  function body (by line range) contains zero calls to `_append_trip_entry`.
- Doc note in docs/CHECKLIST_SCHEMA.md (see G8) states report-only status and
  the promotion trigger verbatim, so the trigger is not just a code comment
  nobody re-reads.

**Anchors.** scripts/checklist_engine.py `dispatch()` (~3676-3701); `waive()`
(unmodified beyond G3, ~3475-3520 for reference only); tests/test_checklist_engine.py.

---

## G5 — Closeout renders the ledger (issue #504)

**Imperative.** In `spine_lifecycle.finish_work`
(scripts/spine_lifecycle.py:1005 onward), right after step 1 loads `spine =
json.loads(...)`, compute one small pure summary:

```python
_tl = spine.get("trip_ledger") or []
overrides = {
    "count": len(_tl),
    "kinds": sorted({e.get("outcome") for e in _tl if isinstance(e, dict)}),
}
```

Attach `"overrides": overrides` to EVERY dict `finish_work` returns —
including the early `stage: "verify"` refusal — not only the final success
dict, because a run can carry overrides and still not be ready to close; a
human/agent reading a refusal should see that fact too, at zero extra cost
(the summary is already computed before the refusal check).

No new top-level key on the checklist itself (`trip_ledger` already exists,
untouched), no change to `episode_capture.py`'s "mechanical" field allowlist
or the `Episode` dataclass / `apply_episode_delta.py` schema (that machinery
is its own separately-governed, strictly-validated surface — extending its
required-field contract for one new mechanical fact is a materially larger
change than this gate's job, and is explicitly left alone here; see
"Depth" in the self-score below for why that tradeoff is made deliberately).
The render seam chosen is the one already wired end-to-end today:
`spine_done_cli.py` (scripts/spine_done_cli.py:73) does
`print(json.dumps(result, indent=2))` on `finish_work`'s exact return dict —
so this gate's one new key is visible to whoever runs the close command
without touching that CLI file at all.

**Done when.** A spine whose `trip_ledger` holds one `begin-refused` and one
`claim-force` entry closes with `result["overrides"] == {"count": 2, "kinds":
["begin-refused", "claim-force"]}`. A spine with no `trip_ledger` key at all
closes with `result["overrides"] == {"count": 0, "kinds": []}` (absence is a
real, meaningful zero, matching this repo's existing doctrine for
`refusals` — never an omitted key that a reader could confuse with "wasn't
checked").

**Evidence.** New pytest cases in tests/test_spine_lifecycle.py: one fixture
spine with a populated `trip_ledger` asserts the non-empty summary through a
full `finish_work` call; one clean fixture asserts the zero-value summary;
one case exercises the `stage: "verify"` refusal path and asserts `overrides`
is still present on that returned dict.

**Anchors.** scripts/spine_lifecycle.py `finish_work` (~1005-1040);
tests/test_spine_lifecycle.py; scripts/spine_done_cli.py (read-only
reference, not modified).

---

## G6 — Doc: extend the trip-ledger section for the three new outcomes

**Imperative.** Extend "### The trip ledger" in docs/CHECKLIST_SCHEMA.md
(line 459 onward) with the three new `outcome` values this plan adds
(`claim-force`, `release-force`, `waive-authority-mismatch`), each with: one
example entry (matching G1's `None`-valued `fill`/`hard`/`model` shape
exactly), a one-line statement that all three are report-only and never
block the verb they accompany, and — for `waive-authority-mismatch`
specifically — the promotion trigger from G4, copied verbatim so the code
comment and the schema doc cannot drift apart silently.

**Done when.** The doc's entry shapes match what G1/G2/G4 actually emit
(reviewed by hand against the code, since no doc-vs-code sync checker exists
for this section today — stated here rather than invented as a new checker,
per this plan's own smallest-diff rule: a doc-sync test is a new concept this
gate does not need).

**Evidence.** The doc diff itself, reviewed against G1/G2/G4's code.

**Anchors.** docs/CHECKLIST_SCHEMA.md:459-622 (trip ledger section through
just before "## Engine verbs ↔ schema").

---

## G7 — Doc: close issue #259 on the census evidence, no code change

**Imperative.** Add a short note near "### Override policy" (line 271) or
"## Consolidation (survey output)" (line 338) in docs/CHECKLIST_SCHEMA.md
recording: `consolidate --override-reason` (scripts/checklist_engine.py:2906)
is the sanctioned "APPROVE-with-findings" reviewer pattern on a SURVEY
checklist's verdict — never a bypass of engine-enforced gate-advancement
authority, because survey verbs never run through `_trip_hard_gate`/
`TRIP_HARD_GUARDED_VERBS`, which is gated-spine-only. A census of
`.agent-work/archive/` (117 files, this run's investigation) shows constant,
correct use of this pattern. This directly refutes issue #259's premise that
`--override-reason` has "no sanctioned use case." Issue #259 should close
citing this note, not by deleting the field and not by folding it into
`trip_ledger` — folding it in would misrepresent ordinary correct reviewer
behavior as an audit-worthy gate-authority override.

**Done when.** The doc note exists and names the census evidence concretely
enough that an Admiral/human closing #259 can cite it directly rather than
re-deriving the argument.

**Evidence.** None required beyond the doc diff itself — this gate adds no
new check and asserts no new runtime behavior, so this plan's own rule
("any new check must run somewhere that can fail it") does not apply to it;
stating that explicitly here so a reviewer does not go looking for a test
that was never meant to exist.

**Anchors.** docs/CHECKLIST_SCHEMA.md (near line 271 or 338); the issue-259
closing action itself is outside this plan's file-write scope (human/Admiral
action on GitHub).

---

## G8 — Closing gate: full local test run + code map refresh

**Imperative.** Run `pytest tests/` (the real gate — Windows CI here is
known-red and not authoritative) until fully green across G1-G7's changes.
Then run `python -m scripts.code_map build --root .` per repo doctrine,
since G1/G2/G4 touch scripts/checklist_engine.py and G5 touches
scripts/spine_lifecycle.py, both of which the map indexes.

**Done when.** `pytest tests/` exits 0. `code_map build` produces either no
diff or a clean, reviewed diff to the map/INDEX.md, committed alongside the
code change in the same commit (not a follow-up).

**Evidence.** Full local pytest output (pass count, e.g. "3607 passed"
baseline noted in this epic's own recent history, now plus this plan's new
cases); the code_map diff (or explicit "no changes" note).

**Anchors.** Whole repo; scripts/code_map.py; docs/architecture/INDEX.md (or
wherever `code_map build` writes).

---

# Self-score

**Depth.** Shallow by design, on purpose: no new top-level key, no new
module, no new abstraction. G1 widens one existing function's signature; G2
and G4 add a handful of lines each, entirely inside `dispatch()`'s own body,
reusing the exact append primitive and list `_trip_hard_gate` already
proved safe; G3 is a one-token fix; G5 adds one computed field to a dict that
already flows end-to-end to a CLI that already prints it. The one place this
plan deliberately does NOT go deep is issue #504's closeout visibility: it
stops at `finish_work`'s return dict rather than plumbing a new field through
`episode_capture.py`'s "mechanical" allowlist, the `Episode` dataclass, and
`apply_episode_delta.py`'s validation (all three of which would need to
change together to add a fifth mechanical counter alongside `refusals`/
`reopens`/`rework-count`/`failed-commands`). That system is a separately-
governed, strictly-validated closed schema; touching it to add one field is
a materially larger, differently-shaped change than "make closeout visibly
render it," and this plan chooses the shallower, already-wired seam instead.
That is a real scope tradeoff, not an oversight — a future gate can promote
the summary into the mechanical-fields schema if the shallow seam proves
insufficient in practice, but this plan does not pre-build for that.

**Locality.** Every write to the unified ledger happens inside `dispatch()`,
provably by the grep/AST test G2 introduces and G4 extends — no verb's own
handler (`claim`, `release`, `waive`) gains a new call to the append
function; each keeps behaving exactly as it does today, observably, from the
outside. The two genuinely new pieces of logic (the force-detection in G2,
the authority-mismatch read in G4) are both small, local reads of `args` and
already-loaded state, not new helper functions threaded through the module —
deliberately avoiding a shared "override detector" abstraction that would
itself need its own chokepoint-safety argument.

**Seam placement.** The seam is the one the repo already trusts:
`dispatch()`, before/around `_run_verb`, exactly where `_trip_hard_gate`
already sits for the proven trip-ledger case. This plan does not invent a
second seam — G5's closeout seam is also an existing, already-wired one
(`finish_work`'s return dict → `spine_done_cli.py`'s `json.dumps`), chosen
specifically because it required zero new plumbing. The one place a genuinely
new decision was made (G4's mismatch check needing to run in `dispatch()`
rather than in `waive()`) is justified by the same chokepoint property this
whole plan is built to preserve, not by convenience.

**Testability.** Every code gate (G1-G5) ships a concrete, currently-failing-
then-passing pytest assertion, plus G2/G4 add a structural test that would
catch a REGRESSION of the chokepoint property itself (a future verb quietly
calling the append function directly), not just a behavior test — which is
what makes "reachable only from dispatch" a provable property of this plan
rather than a comment. G6/G7 are honestly marked as doc-only with no new
runtime check, rather than inventing a doc-sync checker or a GitHub-issue-
closing test that this plan has no way to actually enforce. G8 is the
non-negotiable closing gate naming the actual command (`pytest tests/`) and
the actual doctrine command (`code_map build`) rather than a vague "run
tests."
