APPROVE

blocking_findings: 0

# Review Result — g3 REWORK re-review, issue #467 (epic #418)

## Assigned gate

`g3` — narrow re-review, scoped to the rework of the first review's single blocking finding
(**B-1**: the mutation log's false `EQUIVALENT` declaration for M15). The eight criteria that
passed in the first review were not re-opened.

Diff under review (uncommitted working tree):
`tests/test_checklist_engine.py` (+38, one appended method) and
`.agent-work/issue-467-trip-semantics/g3-mutation-log.md` (M15 entry + Summary).
`git diff --stat -- scripts` is **empty**.

Survey driven at `.agent-work/issue-467-trip-semantics/g3-rework-review/review.json`
(session `g3-rework-review-rev-01`, 13 items, all `complete`, consolidated **APPROVE**,
0 blockers, 2 triage candidates). Fowler record at
`.agent-work/issue-467-trip-semantics/g3-rework-review/fowler-pass.json` (rail exit 0).
Anti-vacuity probe at `.agent-work/issue-467-trip-semantics/g3-rework-review/antivacuity_probe.py`.

## Result

**APPROVE** — zero blocking findings. Two non-blocking observations.

The kill is real, I reproduced it with my own hands, and the log correction is honest. The
rework does exactly the two things B-1 asked for and nothing else.

---

## Criterion 1 — the new test genuinely kills M15 — **PASS**

I applied the mutation myself; nothing here is taken from the implementer's report.

**Pre-state.**

```
$ python -c "import hashlib;print(hashlib.sha256(open('scripts/checklist_engine.py','rb').read()).hexdigest()[:16])"
ccbc247e0de0dcaa
$ git diff --stat -- scripts
(empty)
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py \
    -k test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate
1 passed, 383 deselected in 0.84s
```

**Mutation applied, and asserted applied** (byte-replace, uniqueness asserted before writing;
post-mutation `sha256[:16] = e595ac0da257e23e`):

```
$ git diff -- scripts/checklist_engine.py
@@ -2855,7 +2855,7 @@ def _run_verb(cl: dict, args: argparse.Namespace, base_dir: Path | None) -> str:
                        require_why=_trip_hard_band_reading(
-                           cl, base_dir, getattr(args, "id", None)) is not None)
+                           cl, base_dir) is not None)
```

**RED:**

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py \
    -k test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate
            self.assertEqual(cl["tasks"]["g1"]["status"], "blocked")
            self.assertEqual(E.active_id(cl), "g1")
>           with self.assertRaises(E.EngineError) as ctx:
E           AssertionError: EngineError not raised
tests\test_checklist_engine.py:3988: AssertionError
FAILED tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate
1 failed, 383 deselected in 0.72s
```

Note **where** it fails: at the `assertRaises`, *after* both divergence assertions
(`g1` is `blocked`, `active_id == "g1"`) have already passed. That is the strongest possible
failure site — it proves the fixture still reaches the divergent state under the mutation and
that the single thing the mutation removes is the refusal.

**Narrowness**, under the mutation log's own declared frozen selector (the file pair, no `-k`):

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py
FAILED ...::test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate
1 failed, 433 passed, 155 subtests passed in 11.95s
```

Exactly one test, the named one.

**Reverted clean:**

```
$ git checkout -- scripts/checklist_engine.py
$ python -c "...sha256..."          -> ccbc247e0de0dcaa   (byte-identical to pre)
$ git diff --stat -- scripts        -> (empty)
$ git status --porcelain -- scripts -> (empty)
$ pytest -k <named test>            -> 1 passed, 383 deselected
```

## Criterion 2 — the test is not vacuous — **PASS**

I did not take this on report either. I wrote an independent probe that imports the shipped
engine and the test module's own helpers, rebuilds the fixture, and runs the counterfactuals
the test itself cannot run. Output:

```
P1 statuses {'g1': 'blocked', 'g2': 'in-progress'} | active_id = g1   (gate being CLOSED is g2)
P2 at fill 0.12:  _trip_hard_band_reading(cl,'.', 'g2') -> Reading (require_why)
                  _trip_hard_band_reading(cl,'.')       -> None
P3 SAME fixture WITHOUT the block: active_id = g2; both readings -> Reading;
                  advance g2 --mechanical REFUSED under shipped AND under the mutant
P4 identical fixture+verb: fill 0.00 -> CLOSED (g2 -> complete); 0.12 -> REFUSED; 0.99 -> REFUSED
P5 mechanical close REFUSED "...cannot be closed silently..." | same close WITH --why -> g2 -> complete
P6 same public-verb sequence, g2 carrying NO override: CLOSED at the same 12% fill
```

Against the three sub-questions the handoff names:

- **Does it assert the refusal, not just no-crash?** Yes — `assertRaises(E.EngineError)` plus
  `assertIn("cannot be closed silently", ...)` plus `g2` still `in-progress`. P5 shows the
  refusal is specifically the no-silent-close rule and that the same close **succeeds with
  `--why`**, so the assertion is about the silence, not about a gate that cannot close at all.
- **Is the gauge reading live in the assertion window?** Yes — P4. The identical fixture and
  verb close cleanly at `fill=0.00` and refuse at `0.12` and `0.99`. The refusal tracks the live
  reading, not a leftover.
- **Would it still pass if the fixture never reached `active_id != gate being closed`?** On
  shipped code, yes — and P3 shows *that is exactly why the `block` step is load-bearing*:
  without it both readings return a `Reading` and the advance is refused under shipped **and**
  under the mutant, so a no-divergence fixture would kill nothing. The test does not merely rely
  on the divergence, it **asserts** it (`assertEqual(E.active_id(cl), "g1")`). That converts any
  future silent vacuity — e.g. if `block()` ever gains a status guard — into a red test with a
  named reason rather than a quiet pass. This is the correct anti-vacuity construction.

P2 is the crisp statement of the kill: in this state the two expressions the mutation chooses
between genuinely return different things, `Reading` vs `None`.

## Criterion 3 — reached through PUBLIC verbs — **PASS**

Re-driven by me (P1). `gated()`/`gate()` build an ordinary two-gate checklist; then
`E.dispatch` for `start g1`, `advance g1`, `start g2`, `block g1` — every step through the same
boundary the CLI uses. The `block` call is a `types.SimpleNamespace` matching `_run_verb`'s
block branch (`id`/`blocker`/`authority`/`next_action`), i.e. the shape `argparse` produces, not
a hand-shaped dict. The only direct JSON write is
`cl["tasks"]["g2"]["context_headroom_tokens"] = 50000`, which is the authored override this
issue ships and is how every existing test in the class declares it — not a status or ordering
forced by hand. The resulting `{'g1': 'blocked', 'g2': 'in-progress'}` with `active_id == 'g1'`
is **produced by the engine, not written**.

So the kill is not hollow, and the manufactured-unreachable-fixture defence the original
declaration rested on does not apply: the state it called unreachable is reachable.

## Criterion 4 — no source change — **PASS**

`git diff --stat -- scripts` and `git status --porcelain -- scripts` both empty, before my
mutation and after my revert; file `sha256[:16]` identical (`ccbc247e0de0dcaa`). Specifically
confirmed **untouched**: `block()` at `:2116` still has no status guard, and `TERMINAL` at `:63`
is still `{"complete", "skipped"}`. The excluded "fixes" were not made — correctly, since the
new test depends on that state.

## Criterion 5 — the M15 log correction is honest — **PASS** (with NB-1)

All four required elements are present, and the facts it cites check out against the tree:

- States the kill (header `NO NARROW MUTATION; DECLARED` → **`KILLED`**).
- Names the test in full.
- Gives the failure count (`1 failed`) — correct; I measured `1 failed, 433 passed` under the
  log's own selector.
- **Visibly records the earlier declaration as wrong**, under a labelled
  `CORRECTION (g3 rework 2, reviewer finding B-1)` heading that restates the old reasoning
  before falsifying it — *"That reasoning is false and the fixture is reachable, not
  manufactured"* — and names `f9925be6`'s commit message as also wrong. Verified: that commit
  message does contain *"1 declared EQUIVALENT rather than faked"*.

The Summary section is corrected the same visible way (15 killed + 1 equivalent → 16 killed,
with the correction named, and M15 added to the "mutations that matter most" list). This is a
correction in place, not a quiet rewrite.

Cited facts independently confirmed: `block()` `:2116` has no status guard; `TERMINAL` `:63` is
`{"complete","skipped"}`.

## Criterion 6 — both closeout suites — **PASS**

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py \
    tests/test_init_work_area.py tests/test_install_constellation.py
572 passed, 535 subtests passed in 32.93s              (expected 572 / 535)

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py \
    -k 'headroom or override'
21 passed, 413 deselected, 125 subtests passed in 1.65s   (expected 21 / 413 / 125)
```

Both match the handoff exactly.

## Corroborating the Commander's own shell

Everything the Commander stated reproduces. Its CLI reproduction (shipped **refuses**
`advance g2 --mechanical`; the M15 mutant prints `g2 -> complete`) is what my P2/P5 show at the
library level and what my RED/GREEN pair shows through pytest. No contradiction to report.

## Refactoring pass (Fowler)

Record: `.agent-work/issue-467-trip-semantics/g3-rework-review/fowler-pass.json`, rail exit 0
(`smells=12, flagged=[], overridden=['message-chains','comments-as-deodorant']`).

Ten absent. Two overridden with logged standards:

- **message-chains** — `cl["tasks"]["g1"]["status"]` is a three-deep subscript chain, but the
  chain **is** the schema (`docs/CHECKLIST_SCHEMA.md`); `checklist_engine.py` itself addresses
  the document that way, there is no object to ask instead, and a test-local accessor would hide
  the very shape the assertion is about.
- **comments-as-deodorant** — 18 of 38 lines are prose, the classic signature. Subordinated to
  CREW_CONTEXT's Verification Discipline: the prose records *why* the fixture is shaped as it is
  (no status guard on `block()`, `blocked` not in `TERMINAL`, the fill must rise only after `g2`
  is started because `start` is `TRIP_HARD_GUARDED` and `advance` is not) — none of it
  recoverable from the code, and all of it exactly the reasoning the falsified M15 declaration
  lacked. Deleting it would not simplify the code, it would delete the audit trail this rework
  exists to create.

Nothing flagged, and both non-findings were measured rather than assumed: `verb="block"` appears
exactly once in `tests/test_checklist_engine.py` (so no duplication), and the new method is
about 20 executable lines, linear, comparable to its siblings.

## Non-blocking findings

- **NB-1 (`tc1`) — the corrected M15 entry mislabels its own selector.** The TOTAL line reads
  `1 failed, 383 deselected (frozen headroom or override selector)`. That is wrong twice. The
  log's own Method section freezes
  `pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py` with **no `-k`**, and
  every other entry reports against it as `N failed, M passed`. `383 deselected` actually comes
  from `-k <the named test>` over `test_checklist_engine.py` alone, and the
  `headroom or override` selector deselects **413**, not 383 (measured, criterion 6). The
  failure count itself is correct, and the true figure under the log's own selector is
  **1 failed, 433 passed** — which I measured and which is strictly *more* favourable to the
  entry. So this is a sloppy provenance label, not a flattering one, and it does not touch the
  claim. Non-blocking. But this is the one entry in the log being corrected *for a false claim*,
  so the number under it should match the log's stated method: suggest replacing that line with
  `**TOTAL: 1 failed**, 433 passed (frozen file-pair selector; 155 subtests).` One-line edit in
  an evidence document.
- **NB-2 (`tc2`) — no `_block_ns` helper.** `tests/test_checklist_engine.py` has `_start_ns`,
  `_advance_ns`, `_reopen_ns` and `_resume_ns` but nothing for `block`, so the new test
  hand-rolls the namespace. One call site today, so it is not duplication and declining to
  abstract it now is the right call against speculative generality — worth a helper the second
  time a test needs to dispatch `block`.

## Out-of-scope observations

- `block()` accepting an already-`complete` gate with no status guard, and `blocked` not being
  in `TERMINAL`, remain **untouched and correctly so**. Already filed by the first review as
  NB-5. This rework depends on that state; "fixing" it would have been the scope violation the
  handoff warned about.
- The first review's reconciliation item (`docs/CHECKLIST_SCHEMA.md` under-describing the Task
  object by `context_headroom_tokens`) is unaffected by this rework and still belongs to the
  run's `reconcile` gate.

## Anything I could not verify

Nothing. Every claim in the handoff, the implementer's result and the Commander's own shell
either reproduced for me or was measured directly.

## Workflow Feedback

- **What worked, and is worth keeping.** The handoff gave the exact mutation text, exact line
  numbers, both expected suite numbers, and named the standing trap ("a test that passes for the
  wrong reason"). That let me spend the whole run attacking rather than locating. The
  instruction to use `g3-rework-review/` rather than `g3-review/` was concrete and prevented a
  real collision — the two surveys do share item ids.
- **The one instruction still in tension** (also reported by the first reviewer, so this is the
  second time): "do not modify `scripts/` or `tests/` yourself **beyond applying and reverting
  the M15 mutation**" versus criterion 2, which asks whether the test would still pass if the
  fixture never reached the divergent state — a question that naturally wants a *test* edit. The
  first reviewer resolved the analogous tension with `git archive` sandboxes. I resolved it a
  different way: a probe script under my own review directory that imports the shipped engine
  and the test module's helpers and runs the counterfactuals outside the test file. That is
  cleaner than a sandbox for this shape of question (no `.git`-missing test noise, no baseline
  subtraction) and left the worktree untouched throughout. **Suggest the handoff sanction one of
  these explicitly** — "counterfactual probes belong in a script under your review directory,
  not in `tests/`" — rather than leaving each reviewer to invent a method.
- **The Fowler placeholder is now a non-event.** Resolving `<fowler-pass-record-path>` at
  instantiation time, alongside `<work-id>`, meant no `amend` and no waiver. The handoff's
  wording ("fill placeholders properly rather than force-waive") plus the template's own
  NORMAL PATH sentence were sufficient; no further handoff text is needed here.
- **Nothing was missing from the handoff.** No field I needed was absent, and no number in it
  failed to reproduce.

## Return status

`APPROVE`
