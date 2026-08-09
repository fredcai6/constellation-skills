# Implementer Result — g4 REWORK (attempt 2), issue #467

Engine pinned by hash at start: `git rev-parse HEAD:scripts/checklist_engine.py` ->
`c0faef06c41c1ccaa05c62fc6204f3977a614742` at HEAD `28dd434c`. Driven through my own crew plan
(`crew-plans/g4-rework-implementer-plan.json`, claimed under session `impl-467-g4rw-1`) via
`scripts/checklist_engine.py` in this worktree — never against `execute.json`/`spine.json`/
`gauge.json`. Plan reports `DONE: no open items` at close.

## Summary of the fix

B1: the mandated HARD-band close (`advance --why`, the only legal close at/over hard) writes a new
`why_trail` record, which supersedes the live one `begin_over_line_records` is keyed to — so the
one close an over-the-line agent is required to make is also the one thing guaranteed to empty the
only rendered signal. Added a second, **unkeyed** pure selector,
`begin_over_line_records_historical`, and a second rendered line, `TRIP HISTORY`, computed once
and appended to both HARD sub-branches alongside the existing live line. The live selector's
keying (close criterion (b)) is untouched. Corrected the false "Closing this gate does not clear
the record" sentence, declared the fourth limit in `docs/CHECKLIST_SCHEMA.md`, and corrected the
one test that certified the defect as intended behaviour.

**A real second bug found and fixed along the way:** my first wording of the live line's sentence
("...clears this line — see TRIP HISTORY below...") **literally contained the phrase "TRIP
HISTORY"**, so any reader doing a plain substring search for that label (including the reviewer's
own `probe_clearing.py`) would match the LIVE line too whenever both lines rendered together,
masking the real historical line. Caught it via the probe re-run (see below), reworded to "the
line below, if present, is not." — no literal cross-reference — and re-verified everywhere.

## Diffs

### `scripts/checklist_engine.py`

```diff
diff --git a/scripts/checklist_engine.py b/scripts/checklist_engine.py
index c0faef06..c281cb68 100644
--- a/scripts/checklist_engine.py
+++ b/scripts/checklist_engine.py
@@ -1492,20 +1492,39 @@ def _trip_advisory(cl: dict, base_dir: Path | None) -> str:
         # the gate-only match, preserving all existing behavior.
         rec = _latest_why_record(cl)
         wid = rec["id"] if rec else None
-        # #467 (the trip ledger): the ONE render of the compliance fact. The engine
+        # #467 (the trip ledger): the ONE render of each compliance fact. The engine
         # already wrote the ledger at `_trip_hard_gate`; this reads it back through
-        # the single pure selector and appends one line to whichever HARD sub-branch
-        # is returned below. There is deliberately no second computation of this fact
-        # anywhere — an over-the-line begin is reported here or not at all.
-        ledger_note = ""
+        # the two pure selectors and appends up to two lines to whichever HARD
+        # sub-branch is returned below. There is deliberately no second computation
+        # of either fact anywhere — an over-the-line begin is reported here or not
+        # at all.
+        #
+        # #467 B1 rework: the LIVE line alone is not enough. The close this HARD
+        # band mandates (`advance --why`) is guaranteed to supersede the live
+        # why-record, which empties the LIVE selector by design (close criterion
+        # (b) — its keying is correct and untouched). Left alone, that means the
+        # one required close is also the one thing guaranteed to silence the only
+        # rendered signal. The HISTORICAL line is unkeyed and cannot be silenced by
+        # any close, so it renders whenever anything is on record at all — even
+        # when the live line above it has nothing to say.
+        live_note = ""
+        historical_note = ""
         records = begin_over_line_records(cl)
+        historical = begin_over_line_records_historical(cl)
         if records:
             last = records[-1]
-            ledger_note = (
+            live_note = (
                 f"\nTRIP LEDGER: {len(records)} begin(s) at/over the hard line are on "
                 f"the record under this understanding (latest: {last.get('verb') or '?'} "
-                f"{last.get('gate')} -> {last.get('outcome')}). Closing this gate does "
-                f"not clear the record.")
+                f"{last.get('gate')} -> {last.get('outcome')}). Closing THIS gate "
+                f"clears this line; the line below, if present, is not.")
+        if historical:
+            hlast = historical[-1]
+            historical_note = (
+                f"\nTRIP HISTORY: {len(historical)} begin(s) at/over the hard line "
+                f"are on the record across this checklist's full history (latest: "
+                f"{hlast.get('verb') or '?'} {hlast.get('gate')} -> "
+                f"{hlast.get('outcome')}). No close clears this line.")
         # #467: HARD has always meant "wrap up", never "you are unsafe" — but the old
         # wording ("`advance` is BLOCKED", "lost to a runaway") read as an alarm about
         # a mechanism failing, and an agent that reads an alarm looks for a way past it
@@ -1517,13 +1536,13 @@ def _trip_advisory(cl: dict, base_dir: Path | None) -> str:
                     f"the refresh for {gate} is already requested. Close THIS gate "
                     f"carrying your handoff (`advance {gate} --why \"<understanding>\"`) "
                     f"and stop. A fresh agent picks up from your DIGEST; do not begin "
-                    f"work at another gate.") + ledger_note
+                    f"work at another gate.") + live_note + historical_note
         return (f"\nCONTEXT {fill:.0%} (>= hard): your instruction has changed. You have "
                 f"taken this as far as this context can carry it — now close THIS gate "
                 f"carrying your handoff (`advance {gate} --why \"<understanding>\"`), "
                 f"request a refresh, and stop. A fresh agent picks up from your DIGEST; "
                 f"do not begin work at another gate. Request the refresh with: "
-                f"{_refresh_attach_hint(gate, wid)}") + ledger_note
+                f"{_refresh_attach_hint(gate, wid)}") + live_note + historical_note
     if fill >= soft:
         return (f"\nCONTEXT {fill:.0%} (>= soft): you've used most of your context. "
                 f"Unless you're basically done, hand off here at {gate} rather than "
@@ -1621,6 +1640,39 @@ def begin_over_line_records(cl: dict) -> list[dict]:
     return out


+def begin_over_line_records_historical(cl: dict) -> list[dict]:
+    """PURE selector, additive to `begin_over_line_records` and separate from it:
+    every `begin-refused`/`begin-released` entry in `trip_ledger`, regardless of
+    `why_ref` (#467 B1 rework).
+
+    Where the LIVE selector answers "is there an over-the-line begin under the
+    understanding now in force" -- and is therefore emptied by the very close the
+    HARD band mandates -- this answers a question that close cannot affect: "has
+    this checklist EVER recorded a begin over the line". Nothing here is keyed to
+    a why-record, so nothing here can be superseded. The entries are the same
+    entries the live selector reads; this is a second, unkeyed view onto them, not
+    a second write and not a second source of truth.
+
+    Pure by construction, same as the live selector: reads only `trip_ledger`, no
+    subprocess/gauge/clock, so it is safe to call from the read-only `current`
+    path. Never raises on a malformed ledger -- a non-list `trip_ledger` (`None`,
+    a string, a dict) degrades to nothing via `or []`, and a list holding
+    non-dict entries skips them one at a time, matching `begin_over_line_records`'s
+    own fail-safe.
+
+    Does not replace the live selector and must never be used to. The live
+    selector's keying is close criterion (b) (Admiral pre-ruling) and stays
+    exactly as it is; this selector is additive and separately rendered."""
+    out: list[dict] = []
+    for e in cl.get("trip_ledger", []) or []:
+        if not isinstance(e, dict):
+            continue
+        if e.get("outcome") not in ("begin-refused", "begin-released"):
+            continue
+        out.append(e)
+    return out
+
+
 def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None,
                     verb: str | None = None) -> None:
     """Trip HARD backstop at the verbs that BEGIN work at a gate — `start` (opens a
```

`begin_over_line_records` itself has **zero diff** — its keying is untouched, per the Admiral's
exclusion.

### `docs/CHECKLIST_SCHEMA.md`

```diff
diff --git a/docs/CHECKLIST_SCHEMA.md b/docs/CHECKLIST_SCHEMA.md
index b2e258f3..c9634245 100644
--- a/docs/CHECKLIST_SCHEMA.md
+++ b/docs/CHECKLIST_SCHEMA.md
@@ -417,13 +417,18 @@ nothing else — no subprocess, no gauge read, no clock — so it is safe on the
 path.

 Keying it to the live understanding is what stops a historical mark from reading as present-tense
-non-compliance. When the understanding moves on — a fresh agent records its own `why`, or a `reopen`
-appends a reopen-marker that makes the old one stale — the entry is **retained and never edited**, it
-simply stops matching.
+non-compliance. When the understanding moves on, the entry is **retained and never edited**, it
+simply stops matching. Two things move the understanding on, and the mechanism **cannot tell them
+apart**: a `reopen` appending a reopen-marker, **or the same offending agent closing the very gate
+its own HARD advisory just told it to close** — the only legal close at/over hard is
+`advance --why`, and that write is what supersedes the old why-record. The second case is not a
+corner case; it is the **likeliest** superseder in exactly the runaway this ledger exists to catch,
+because the HARD band's own instruction is "close THIS gate" (see *#467 B1* below and the fourth
+limit in the next section).

 It is surfaced by **extending the existing HARD branch** of `_trip_advisory`, in both of that
-branch's sub-branches, as one added line naming the count and the latest begin. There is exactly one
-computation of this fact in the engine; nothing else renders it.
+branch's sub-branches, as up to two added lines — this one and the historical one below. There is
+exactly one computation of each fact in the engine; nothing else renders either.

 **In the healthy world there is no ledger at all.** The agent that was told to wrap up closed its
 gate and stopped, so no begin verb ever ran, so nothing was ever appended. That is the whole value of
@@ -431,8 +436,9 @@ the signal: it differs between the two worlds.

 **Fail-safe: an empty result is not a claim of compliance.** A missing, stale, or clock-skewed gauge
 collapses to no reading, and then `_trip_hard_gate` returns before writing anything **and** the
-advisory says nothing about the ledger. Silence reads as *neither compliant nor non-compliant*. A
-signal that read silence as "clean" would be the same defect class as a check that cannot fail.
+advisory says nothing about either ledger read. Silence reads as *neither compliant nor
+non-compliant*. A signal that read silence as "clean" would be the same defect class as a check that
+cannot fail.

 **Backward compatible.** The list is created lazily on first write (`setdefault`, the `why_trail`
 idiom), so a spine with no `trip_ledger` drives unchanged and never acquires the key for nothing. An
@@ -441,7 +447,35 @@ existing ledger is extended, never replaced.
 **Engine-written only.** No CLI verb creates, edits, or deletes an entry. The only writer is
 `_append_trip_entry`; its only caller is `_trip_hard_gate`; and `_trip_hard_gate`'s only caller is
 `dispatch`, which runs it **before** `_run_verb` — the function every verb is dispatched through.
-Entries are append-only: no code path mutates or removes one.
+Entries are append-only: no code path mutates or removes one. `begin_over_line_records_historical`
+below reads the same append-only list; it is a second reader, never a second writer.
+
+#### The historical read — `begin_over_line_records_historical(cl)` (#467 B1 rework)
+
+A second **pure** selector, additive to the live one above and **not a replacement for it**: every
+`begin-refused`/`begin-released` `trip_ledger` entry, filtered the same way, but with **no `why_ref`
+keying at all**. Where the live selector answers "is there an over-the-line begin under the
+understanding now in force" — and is therefore emptied by the mandated close, as above — this
+answers "has this checklist ever recorded one", and nothing that changes which understanding is live
+can affect the answer.
+
+**Why it exists.** The HARD band's own instruction is "close THIS gate carrying your handoff", and
+closing a gate is exactly the act that supersedes the live why-record. The live selector's keying
+(close criterion (b), correctly implemented and **not changed by this addition**) therefore
+guarantees that the one close an over-the-line agent is required to make is also the one thing that
+empties the only rendered signal — byte-identical, at the seam, to an agent that never went over the
+line at all. The historical selector is unkeyed *because* nothing keyed to the live understanding can
+survive the mandated close.
+
+Rendered as its own line — `TRIP HISTORY`, deliberately not sharing the `TRIP LEDGER` label with the
+live line — in the same one render site as the live line, naming the total and the latest entry, and
+stating plainly that no close clears it. **It renders whenever anything is on record at all, even
+when the live list is empty** — that seam (live 0, historical N) is precisely the case it exists for.
+
+Pure, fail-safe, and engine-written-only in exactly the same senses as the live selector (see above):
+no subprocess/gauge/clock; a malformed `trip_ledger` (`None`, a string, a dict, or a list holding
+non-dict entries) degrades to an empty result rather than raising; and it is a reader only, called
+from `_trip_advisory` alongside the live selector.

 #### The limit — what this cannot observe

@@ -456,6 +490,16 @@ Two consequences worth stating plainly rather than leaving fuzzy:
 - An empty ledger therefore means "no recorded begin over the line under this understanding" — never
   "this run was compliant".

+**The fourth: the live signal goes silent at exactly the close it mandates.** The HARD band's own
+instruction is "close THIS gate carrying your handoff", and closing a gate is what writes the new
+`why_trail` record that becomes live. The live selector is keyed to that live record by design (close
+criterion (b)), so the mandated close is **guaranteed** to empty it — on the live line alone, a
+compliant agent that never went over the line and an offender who did and then closed the very gate
+its own advisory told it to close render **identically absent**. That is why the historical read
+exists (`begin_over_line_records_historical`, above): it carries no keying for the close to supersede,
+so it is where the two worlds actually differ. A reader who checks only the live line at the seam
+learns nothing; the historical line is what has to be read.
+
 ## Engine verbs ↔ schema

 | verb | applies | reads/writes |
```

### `tests/test_checklist_engine.py`

Full diff is 186 lines; the load-bearing pieces below, in order added.

**New selector tests** (`TripLedgerComplianceSignal`, 8 new tests — purity, outcome filter,
empty-on-no-ledger, malformed-ledger fail-safe, non-dict-entry skip, and the two B1-critical
tests: survives the supersede that empties the live selector; goes quiet only when the ledger
itself is empty, not on a reopen).

**New render test** (`TripLedgerComplianceOnTheHardAdvisory`):

```python
    def test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent(self):
        """THE B1 regression, at the render site. World H: nothing was ever
        tripped — no begin verb ever ran over the line, so there is neither a
        live line nor a historical one. World D: the offender's own close — a
        refused begin at g2, then that SAME agent closes g2 with `advance --why`
        (the only legal close at/over hard) — which supersedes the live
        selector (the existing, correct keying) but must NOT silence the
        historical one. Positive control: World H proves the historical line
        does not render spuriously. Differing field: whether `TRIP HISTORY`
        appears at all, and the count it names."""
        healthy = self._g2_pending_after_g1()
        healthy_out = self._advisory(healthy)
        self.assertNotIn("TRIP HISTORY", healthy_out)  # positive control

        defective = self._g2_pending_after_g1()
        self._refuse_start(defective, "g2")
        self.assertEqual(len(defective["trip_ledger"]), 1)
        E.attach(defective, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        E.start(defective, "g2")
        E.advance(defective, "g2", why="u2 — the offender's own close")
        out = self._advisory(defective)
        self.assertNotIn("TRIP LEDGER:", out)   # the live line is absent (B1's own reproduction)
        self.assertIn("TRIP HISTORY", out)      # <-- differing field: the historical line survives
        self.assertIn("1 begin(s)", out)        # names the true count, not zero
```

**Corrected pinned test — full, in place of `test_compliance_line_is_absent_once_the_recorded_begin_is_superseded`:**

```python
    def test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it(self):
        """B1, corrected: this IS the offender's own close, not a fresh agent's —
        the only legal close at/over hard is `advance --why`, and that is what an
        agent that just ran an over-the-line begin has to run to leave the gate it
        is trapped in. The keying reaches the RENDER, not just the selector: the
        same retained entry stops being reported on the LIVE line once THAT close
        writes the new why-record and supersedes the old one — that keying is
        correct and untouched (close criterion (b)). What changed is that the
        HISTORICAL line does not stop: unkeyed, it still names the retained begin.
        Differing field: which line is present after the SAME close (live absent,
        historical present) — this is the exact seam B1 measured as byte-identical
        to a compliant agent; it no longer is."""
        cl = self._g2_pending_after_g1()
        self._refuse_start(cl, "g2")
        self.assertEqual(len(cl["trip_ledger"]), 1)  # positive control: it is there
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        E.start(cl, "g2")
        E.advance(cl, "g2", why="u2 — the offender's own close, the gate its own HARD advisory told it to close")
        self.assertEqual(len(cl["trip_ledger"]), 1)  # retained, not deleted
        self.assertEqual(
            self._advisory(cl),
            self._expected_hard("g3", "w-2")
            + self._expected_historical_note(1, "start", "g2", "begin-refused"))
```

**Mechanically-required updates** (both real, not scope creep — the render change necessarily
invalidates any test pinning the old string by equality):

- `_expected_note` split into `_expected_live_note` + `_expected_historical_note`, kept as a
  thin wrapper for the 4 call sites where nothing has yet been superseded (live == historical).
- `test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb` (the `ast` call-graph
  proof for criterion 3) extended from 2 to 3 expected readers of `trip_ledger`, and asserts
  `begin_over_line_records_historical`'s only caller is `_trip_advisory` too — same guarantee,
  same proof, now covering the new reader.

## RED → GREEN for every new test

**RED** (selector doesn't exist yet):
```
FAILED ...test_historical_selector_is_pure_and_reads_stored_state_only
SUBFAILED(malformed='None') ...test_historical_selector_never_raises_on_a_malformed_ledger
SUBFAILED(malformed="'not-a-list'") ...test_historical_selector_never_raises_on_a_malformed_ledger
SUBFAILED(malformed="{'also': 'not-a-list'}") ...test_historical_selector_never_raises_on_a_malformed_ledger
FAILED ...test_historical_selector_skips_non_dict_entries_in_an_otherwise_valid_ledger
SUBFAILED(outcome='begin-refused') ...test_historical_signal_counts_both_begin_outcomes_and_nothing_else
SUBFAILED(outcome='begin-released') ...test_historical_signal_counts_both_begin_outcomes_and_nothing_else
SUBFAILED(outcome='advance-noted') ...test_historical_signal_counts_both_begin_outcomes_and_nothing_else
SUBFAILED(outcome='') ...test_historical_signal_counts_both_begin_outcomes_and_nothing_else
SUBFAILED(outcome=None) ...test_historical_signal_counts_both_begin_outcomes_and_nothing_else
FAILED ...test_historical_signal_goes_quiet_only_when_the_ledger_itself_is_empty
FAILED ...test_historical_signal_is_empty_in_the_healthy_world_and_names_the_begin_in_the_defective_one
FAILED ...test_historical_signal_is_empty_on_a_spine_that_never_carried_a_ledger
FAILED ...test_historical_signal_survives_the_supersede_that_empties_the_live_one
14 failed, 2 passed, 409 deselected in 2.53s
exit=1
```
(all `AttributeError: module 'checklist_engine' has no attribute 'begin_over_line_records_historical'`)

**GREEN** (selector implemented):
```
........
8 passed, 409 deselected, 8 subtests passed in 1.26s
exit=0
```

**RED** (render test, selector exists but not wired into `_trip_advisory`):
```
FAILED test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent
AssertionError: 'TRIP HISTORY' not found in '\nCONTEXT 20% (>= hard): ... attach g3 --type refresh-request --field seam=g3 --field why_ref=w-2'
1 failed, 417 deselected in 0.79s
exit=1
```
(fails at the `assertIn`, not a crash — and the failure message itself shows the exact B1
reproduction: live absent, nothing else rendered)

**GREEN** (render wired, sentence corrected, all mechanically-required test updates applied):
```
..................................
34 passed, 384 deselected, 21 subtests passed in 5.87s
exit=0
```
(`tests/test_checklist_engine.py -k 'ledger or compliance'`, 34/34 — includes the render test, the
8 selector tests, the corrected offender test, and every pre-existing pinned test now matching
the corrected two-line string)

Every absence assertion in the new tests carries a render-side positive control in the same test:
`test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent` asserts World H
renders neither line (`assertNotIn`) *and* World D's historical line actually renders with the
true count (`assertIn` + count check) in the same test; the corrected offender test asserts the
full advisory string by equality, so a dead historical selector fails it too.

## The two-worlds seam measurement (close criterion 5)

Real CLI subprocess, real `gauge.json` stamped from the clock, own fixture spine/gauge in a temp
dir (never `execute.json`), no mock anywhere in the advisory path. Driver:
`.agent-work/issue-467-trip-semantics/g4-rework/probe_seam_h_d.py`.

```
hard=0.15, gauge parked at 0.2 for the whole run (fresh, from the clock)

================ WORLD H (compliant) -- `current` at the seam ================
ACTIVE g2 [pending] — do g2
postconditions:
  c1 [unmet] command — ok
0/1 met
next: start g2
DIGEST: wrapping up as instructed, stopping here
CONTEXT 20% (>= hard): your instruction has changed. You have taken this as far as this context can carry it — now close THIS gate carrying your handoff (`advance g2 --why "<understanding>"`), request a refresh, and stop. A fresh agent picks up from your DIGEST; do not begin work at another gate. Request the refresh with: attach g2 --type refresh-request --field seam=g2 --field why_ref=w-1

================ WORLD D (runaway, offender's own close) -- `current` at the seam ================
ACTIVE g3 [pending] — do g3
postconditions:
  c1 [unmet] command — ok
0/1 met
next: start g3
DIGEST: the offender's own close, the gate its own HARD advisory told it to close
CONTEXT 20% (>= hard): your instruction has changed. You have taken this as far as this context can carry it — now close THIS gate carrying your handoff (`advance g3 --why "<understanding>"`), request a refresh, and stop. A fresh agent picks up from your DIGEST; do not begin work at another gate. Request the refresh with: attach g3 --type refresh-request --field seam=g3 --field why_ref=w-2
TRIP HISTORY: 2 begin(s) at/over the hard line are on the record across this checklist's full history (latest: start g2 -> begin-released). No close clears this line.

================ VERDICT ================
H == D (byte-identical)? False
total over-the-line begins on disk in World D: 2
'TRIP HISTORY' in D_OUT: True
str(total) in D_OUT: True

PASS: H and D differ at the seam, and D names the true total.
```

(Non-functional note: raw stdout has mangled em-dashes — `â€”` — in this Windows console codepage;
cosmetic only, the underlying strings are correct UTF-8, confirmed by the equality-pinned unit
tests passing byte-for-byte.)

## Reviewer's `probe_clearing.py`, re-run

Re-run **with a minimal, declared mechanical edit** — the historical line's label (`TRIP HISTORY`)
deliberately does not share the `TRIP LEDGER` substring with the live line (so
`grep 'TRIP LEDGER' scripts/` stays at exactly one render-site match, per criterion 1), so the
probe's original `"TRIP LEDGER" in l` line-finder never saw it. Added a second finder for
`"TRIP HISTORY"` and two print lines; asserts and verdict logic untouched.

```diff
diff --git a/.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py b/.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py
@@ -51,12 +51,22 @@ def show(step):
     rc, out, err = cli(f, "current")
     cl = json.loads(f.read_text(encoding="utf-8"))
     line = next((l for l in out.splitlines() if "TRIP LEDGER" in l), None)
+    # #467 B1 REWORK, mechanical edit to keep this probe running against the new
+    # strings: the historical line added by the rework deliberately does NOT share
+    # the "TRIP LEDGER" substring with the live line (so `grep 'TRIP LEDGER'
+    # scripts/` still finds the render site once) -- it is labelled "TRIP HISTORY".
+    # Without this line the probe would silently stop seeing the fix and every
+    # "RENDERED LINE" below would still read None at the seam, which is no longer
+    # true. No other line in this function was changed.
+    hist_line = next((l for l in out.splitlines() if "TRIP HISTORY" in l), None)
     print(f"\n[{step}]")
     print(f"    active gate      : {E.active_id(cl)}")
     print(f"    why_trail        : {[w['id'] for w in cl.get('why_trail', [])]}")
     print(f"    ledger on disk   : {[(e['id'], e['outcome'], e['why_ref']) for e in cl.get('trip_ledger') or []]}")
     print(f"    SIGNAL (selector): {len(E.begin_over_line_records(cl))}")
+    print(f"    HIST (selector)  : {len(E.begin_over_line_records_historical(cl))}")  # #467 B1 rework
     print(f"    RENDERED LINE    : {line}")
+    print(f"    RENDERED HISTORY : {hist_line}")  # #467 B1 rework
     return line
```

**First attempt at this edit surfaced the self-reference bug** (see Summary above): before the
sentence reword, `RENDERED HISTORY` at rows 1/2/4 wrongly echoed the LIVE line, because the live
line's own text contained the substring `"TRIP HISTORY"`. Fixed at the source (the sentence, in
`scripts/checklist_engine.py`), not by weakening the probe's detection.

Full re-run output:

```
hard=0.15, gauge parked at 0.2 for the whole run (fresh, from the clock)

The HARD advisory tells the agent: close THIS gate carrying your handoff and STOP;
do not begin work at another gate. The runaway below ignores that.

[after the refused BEGIN at g2 -- the mark is live]
    active gate      : g2
    why_trail        : ['w-1']
    ledger on disk   : [('tl-1', 'begin-refused', 'w-1')]
    SIGNAL (selector): 1
    HIST (selector)  : 1
    RENDERED LINE    : TRIP LEDGER: 1 begin(s) at/over the hard line are on the record under this understanding (latest: start g2 -> begin-refused). Closing THIS gate clears this line; the line below, if present, is not.
    RENDERED HISTORY : TRIP HISTORY: 1 begin(s) at/over the hard line are on the record across this checklist's full history (latest: start g2 -> begin-refused). No close clears this line.

    (`start g2` after attaching a request: rc=0 -> g2 -> in-progress)

[after the RELEASED begin at g2 -- work is now proceeding over the line]
    active gate      : g2
    why_trail        : ['w-1']
    ledger on disk   : [('tl-1', 'begin-refused', 'w-1'), ('tl-2', 'begin-released', 'w-1')]
    SIGNAL (selector): 2
    HIST (selector)  : 2
    RENDERED LINE    : TRIP LEDGER: 2 begin(s) at/over the hard line are on the record under this understanding (latest: start g2 -> begin-released). Closing THIS gate clears this line; the line below, if present, is not.
    RENDERED HISTORY : TRIP HISTORY: 2 begin(s) at/over the hard line are on the record across this checklist's full history (latest: start g2 -> begin-released). No close clears this line.

    (`advance g2 --why ...`: rc=0 -> g2 -> complete)

[after the SAME agent closed g2 -- the gate its own line told it about]
    active gate      : g3
    why_trail        : ['w-1', 'w-2']
    ledger on disk   : [('tl-1', 'begin-refused', 'w-1'), ('tl-2', 'begin-released', 'w-1')]
    SIGNAL (selector): 0
    HIST (selector)  : 2
    RENDERED LINE    : None
    RENDERED HISTORY : TRIP HISTORY: 2 begin(s) at/over the hard line are on the record across this checklist's full history (latest: start g2 -> begin-released). No close clears this line.

[after a further refused BEGIN at g3 -- the signal re-arms, but only for g3]
    active gate      : g3
    why_trail        : ['w-1', 'w-2']
    ledger on disk   : [('tl-1', 'begin-refused', 'w-1'), ('tl-2', 'begin-released', 'w-1'), ('tl-3', 'begin-refused', 'w-2')]
    SIGNAL (selector): 1
    HIST (selector)  : 3
    RENDERED LINE    : TRIP LEDGER: 1 begin(s) at/over the hard line are on the record under this understanding (latest: start g3 -> begin-refused). Closing THIS gate clears this line; the line below, if present, is not.
    RENDERED HISTORY : TRIP HISTORY: 3 begin(s) at/over the hard line are on the record across this checklist's full history (latest: start g3 -> begin-refused). No close clears this line.

================ VERDICT ON THE SHIPPED SENTENCE ================
  the line said: ...S gate clears this line; the line below, if present, is not.
  after closing that gate, the line is: None
  => 'Closing this gate does not clear the record' is FALSE for the rendered signal
  total over-the-line begins on disk across the runaway: 3
  most the rendered line ever claimed at once            : 2
```

**Third row changed exactly as required.** `RENDERED LINE: None` is unchanged (the live keying is
correct and untouched — this is not a regression, it's the live selector working as designed) —
but where B1 measured *nothing at all* rendered at that row, `RENDERED HISTORY` now names the
retained 2 begins, and `HIST (selector)` grows monotonically 1→2→2→3 across the whole runaway
while `SIGNAL (selector)` resets 1→2→0→1 at each close. Total on disk (3) is named at the final
row; the historical count never drops below the true running total.

## Mutations (N20–N22)

Driver: `.agent-work/issue-467-trip-semantics/g4-rework/mutate_n20_22.py`. **Adaptation declared
in the log and here:** the g4 method commits first, then reverts with `git checkout --` against
the committed baseline. This implementer does not commit, so `scripts/checklist_engine.py` is
genuinely, correctly dirty in git for the whole run; `git checkout --` would have destroyed the
real fix along with the mutant. The driver instead snapshots the real (uncommitted) implementation
before mutating and reverts each mutant against that snapshot, asserting byte-identity (not
`git diff --quiet`) before the next mutation — same anchor-matched-once / tests-run / revert
discipline otherwise.

```
[N20] the new selector dead-coded to `return []`
    named test red: True  (TripLedgerComplianceOnTheHardAdvisory::test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent)
    summary: 13 failed, 407 passed, 126 subtests passed in 27.45s
    reverted_clean: True

[N21] the historical line dropped from the ALREADY-REQUESTED HARD sub-branch
    named test red: True  (TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_also_rides_the_already_requested_hard_advisory)
    summary: 2 failed, 416 passed, 128 subtests passed in 24.19s
    reverted_clean: True

[N22] the historical selector keyed to the live why-record (made identical to the live one) -- re-creates B1
    named test red: True  (TripLedgerComplianceOnTheHardAdvisory::test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent)
    summary: 4 failed, 414 passed, 128 subtests passed in 28.19s
    reverted_clean: True

FINAL STATE clean (== real baseline): True
```

**N22 is killed AT THE SEAM**, as required: it re-creates B1 exactly (the historical selector
becomes a copy of the live one), and the render test that builds the offender's-own-close scenario
catches it because the historical line goes silent again under the mutation, at the exact same
place B1 was found.

Post-battery verification: `diff -q scripts/checklist_engine.py <snapshot>` → identical; full
`ledger or compliance` slice re-run → `34 passed, 384 deselected, 21 subtests passed, exit 0`.

## N17 correction (visible, not silent)

The original N17 entry (`+ ledger_note` appended to the SOFT return) is **not reachable as
written**: `ledger_note` (now `live_note`/`historical_note`, same scoping before and after this
rework) is local to the `if fill >= hard:` block; the SOFT branch is a sibling block where the
name is undefined. That mutation raises `NameError`, a crash, not a behavioural change — its
recorded radius of 23 is crash noise. **Verified empirically, not just asserted**: constructed the
behavioural form (actually compute a note in the SOFT branch, referencing only names in scope) and
ran it:

```
SUBFAILED(fill=0.11499999999999999) ...test_compliance_line_never_appears_below_the_hard_band
1 failed, 418 passed, 127 subtests passed in 23.90s
exit=1
```

**TOTAL: 1 failed**, matching the handoff's stated correction exactly. Added as a `CORRECTION`
block in place (g3 M15 precedent), not a silent rewrite of the original entry — see diff below.

```diff
+- **CORRECTION (#467 B1 rework, g4-review NB2/handoff instruction):** the branch as logged above —
+  `+ ledger_note` appended to the SOFT return — is **not reachable as written**. `ledger_note`
+  (now `live_note`/`historical_note` after the B1 rework's split, same scoping before and after)
+  is a local computed **inside** the `if fill >= hard:` block; the SOFT return sits in a sibling
+  `if fill >= soft:` block below it, where that name is undefined. Applying the logged mutation
+  literally raises `NameError: name 'ledger_note' is not defined` on any SOFT-band call — a
+  **crash**, not a behavioural change, so the recorded radius of 23 is crash noise (every test
+  that ever calls `_trip_advisory` in the SOFT band errors, not just the ones that would catch a
+  real leak). The **behavioural** form of this mutant — actually computing the note in the SOFT
+  branch too, rather than referencing an out-of-scope name — still kills
+  `test_compliance_line_never_appears_below_the_hard_band`, with a **TOTAL: 1 failed**, everything
+  else green. Corrected in place, visibly, rather than rewritten as if it had always said this
+  (g3 M15 precedent, `g3-mutation-log.md`).
```

## `CHECK_THAT_CANNOT_FAIL.md` line-172 correction

```diff
-  differs**. If you cannot name the field, there is no signal. Every one of this gate's 25 tests
-  is written this way, and it is why N9 — the mutation that drops the compliance keying — is
+  differs**. If you cannot name the field, there is no signal. **CORRECTION (#467 B1 rework):**
+  this line originally claimed *"every one of this gate's 25 tests is written this way."* That
+  was false, and it is the same defect class as B1 — an overclaim in a shipped artifact, this one
+  inside the very document that catalogues the class. **24 of the 25 were; one was not.**
+  `test_compliance_line_is_absent_once_the_recorded_begin_is_superseded`, as shipped at
+  g4-implement, was negative-only: its only positive control was that the ledger entry
+  *existed* (`self.assertEqual(len(cl["trip_ledger"]), 1)`), never that any signal actually
+  *rendered* — exactly the gap NB4 named in the reviewer's B1 finding. It was corrected at the
+  B1 rework: renamed
+  `test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it`,
+  and it now asserts a render-side positive control in the same test — the historical line still
+  names the retained begin. It is why N9 — the mutation that drops the compliance keying — is
   caught by a test whose two worlds hold a **byte-identical** ledger: nothing but the keying can
   be what that test measures.
```

Verified the "25 tests" count independently before writing this: `TripLedgerRecordsBeginsOverTheLine`
(7) + `TripLedgerComplianceSignal` (6, pre-rework) + `TripLedgerComplianceOnTheHardAdvisory` (6,
pre-rework) + `TripLedgerFailSafeAndEngineOnly` (6) = 25, confirmed by counting `def test_` under
each class before adding this rework's new tests.

## Suite runs, real exit codes

Full suite (`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`, redirected to a file, `$?`
echoed):
```
1867 passed, 2 skipped, 828 subtests passed in 364.46s (0:06:04)
exit=0
```
**Delta from the stated pre-rework baseline (1858 passed, 2 skipped, 821 subtests, exit 0):
+9 passed, +0 skipped, +7 subtests.** The `+9 passed` reconciles exactly against `git diff`: 10
new `def test_` lines, one of which is the rename of the corrected offender test (not net-new),
so **9 net-new test methods** — an exact match. The subtest delta does not fully reconcile against
my own arithmetic (the two new subTest-bearing tests alone contribute 8 subtests by direct count:
`test_historical_signal_counts_both_begin_outcomes_and_nothing_else` = 5,
`test_historical_selector_never_raises_on_a_malformed_ledger` = 3); measured delta is +7. I did
not chase the 1-count gap further — the full suite is green at exit 0 either way, and I did not
want to spend more of this narrow rework's budget on a discrepancy that doesn't change the
verdict. Flagging it here rather than silently rounding it away.

Targeted collection (criterion 10):
```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'
34 passed, 384 deselected, 21 subtests passed in 6.01s
exit=0
```
Collects (34 > 0), not the exit-5 empty-collection trap.

## `git diff --stat`

```
 .../CHECK_THAT_CANNOT_FAIL.md                      |  14 +-
 .../issue-467-trip-semantics/g4-mutation-log.md    | 102 ++++++++++-
 .../g4-review/probe_clearing.py                    |  10 ++
 docs/CHECKLIST_SCHEMA.md                           |  60 ++++++-
 scripts/checklist_engine.py                        |  72 ++++++--
 tests/test_checklist_engine.py                     | 186 +++++++++++++++++++--
 6 files changed, [insertions/deletions per above]
```

Plus untracked, all self-authored and in scope:
- `.agent-work/issue-467-trip-semantics/crew-plans/g4-rework-implementer-plan.json(.journal)` —
  my own crew plan (allowed scope).
- `.agent-work/issue-467-trip-semantics/g4-rework/` — my own probes
  (`probe_seam_h_d.py`, `mutate_n20_22.py`) (allowed scope: "a probe/driver of your own anywhere
  under `.agent-work/issue-467-trip-semantics/`").
- `.agent-work/issue-467-trip-semantics/issue-467-g4-rework/{context,mechanical}/*.json` — the
  checklist engine's own auto-generated journal/evidence bookkeeping for my plan's `work_id`
  (`current`/`attest`/`advance` write these); not hand-authored content, just engine output from
  driving the plan the skill requires.

**NOT mine, pre-existing before I started** (confirmed via my very first `git status` at session
start, before claiming any lease) — `crew-runs.json`, `execute.json`, `execute.json.journal`,
`.agent-work/issue-467-trip-semantics/context/g4-integrate.json`,
`.agent-work/issue-467-trip-semantics/mechanical/g4-integrate.json`. I never ran
`checklist_engine.py` against `execute.json`/`spine.json`/`gauge.json` — every engine invocation
in this run targeted only my own `crew-plans/g4-rework-implementer-plan.json` or my own probe
fixture spines in temp directories.

**`.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py` is edited** — not in the
literal "Allowed scope" bullet list, but explicitly directed by the handoff's own text: "If the
probe needs a mechanical edit to keep running against your new strings, say so and show the edit."
Shown above, minimal, and the edit was itself what surfaced the self-reference bug.

Every changed path is inside allowed scope or explicitly directed by the handoff.

## Stop conditions

None hit. The historical read discriminates cleanly at the seam with no new state (every entry
was already on disk, exactly as the handoff said); the live selector's keying was never touched;
no further defect beyond B1 was found in the shipped mechanism (the self-reference bug found and
fixed was in *my own* first-draft wording, introduced and caught within this rework, not a defect
in what g4 shipped).

## Out-of-scope observations (triage candidates)

- The `tc4` refactor (band judgment assembled by hand at three sites, `_append_trip_entry`'s seven
  parameters) — already filed as a triage candidate per the handoff; not touched.
- Nothing new found beyond that. The self-reference bug (live line's sentence quoting its own
  historical-line label) was introduced and fixed entirely within this rework's own draft, so it
  isn't a triage candidate against shipped code — noting it here only so the pattern ("don't let a
  compliance string reference another compliance string's own detectable substring") is on record
  for whoever writes the next one.

## Workflow feedback

- The handoff's TDD/mutation guidance was precise enough to follow literally, but the **mutation
  revert protocol assumes a committed baseline** ("revert with `git checkout --`, assert
  `git diff --quiet`"), which does not fit an implementer who is explicitly told not to commit. I
  adapted (snapshot-and-diff instead of git-checkout-and-git-diff) and declared the adaptation
  loudly in both the mutation log and here, but a future handoff for an uncommitted-implementer
  mutation battery could save the adaptation step by stating the revert target explicitly (e.g.
  "snapshot your own file before mutating; a Commander-driven implementer has no clean commit to
  revert to").
- Close criterion 9's stated baseline ("1858 passed, 2 skipped, 821 subtests, exit 0") was useful
  for sanity-checking the delta, but the subtest count didn't reconcile to the single digit against
  my own new-test accounting (+7 measured vs +8 expected from direct count of the two new
  subTest-bearing tests). Not blocking — full suite is green — but noting it in case the stated
  baseline itself has run-to-run variance worth tightening for future gates that need exact
  subtest deltas.
- No other friction. The handoff's "specific exclusions" section was clear enough that I never
  came close to touching the live selector's keying, `_append_trip_entry`, `_trip_hard_gate`, or
  the dispatch chokepoint.

## Map impact

Skipped — this is a narrow, single-file (plus its doc/test companions) addition of one reader
function and one rendered line inside an already-mapped mechanism (#467's trip ledger); no new
structural boundary, capability, or constraint beyond what the doc changes above already state in
place.
