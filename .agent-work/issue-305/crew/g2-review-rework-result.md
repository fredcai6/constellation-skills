# Reviewer Result — g2-review RE-REVIEW (attempt 2)

**Crew id:** `constellation/issue-305/g2-review/reviewer/attempt-2`
**Survey:** `.agent-work/issue-305/g2-review-rework/review.json` — all 7 checks driven and
consolidated (`consolidate` → `verdict=APPROVE-WITH-FOLLOWUPS`, 0 open findings).
**Fowler record:** `.agent-work/issue-305/g2-review-rework/fowler-pass.json` — rail exits 0.

# VERDICT: APPROVE-WITH-FOLLOWUPS

No blockers. Two observation-level Fowler flags and one triage candidate, none of which
should hold the gate.

---

## 1. My independent mutation — what I broke, what caught it, what survived

Both spent mutations avoided. I broke the **call site** in four of five cases, as directed.
Every mutation was applied by script, run, restored, and the restore verified by blob OID
(`git hash-object` vs `git rev-parse HEAD:<path>`) — **five for five OK**.

### The primary one — M-A, and it is the informative result

**`scripts/episode_capture.py:419` (call site).** Hand `reopen_total()` a checklist with
`skipped` gates filtered out — the plausible-looking reading that *"a gate we skipped after
escalating shouldn't count its reopens."* It targets exactly what the new tests are for: in
both new cases the escalated gate is `skip`ped while still carrying a real `rework_count`.

```
NEW EscalatedReopenIsNotAReopenTests -> RED    2 failed
    AssertionError: 0 != 1      (start seam)
    AssertionError: 1 != 3      (reopen seam)
OLD ReopensFieldTests            -> GREEN  4 passed
whole tests/test_episode_fields.py -> RED    2 failed, 34 passed
```

**Caught, and caught by the NEW tests alone.** That is the finding the dispatch was for: the
old tests do not discriminate this mutation at all, so the new tests are not restating
existing coverage — they add a discriminating axis (a reopen recorded on a gate that has
since left the active path) that nothing else in the suite pinned.

### Three more, to hunt a survivor

| # | Mutation | New tests | Old tests | Suite |
|---|---|---|---|---|
| M-B | callee: `total += 1` instead of `total += count` — count reworked *tasks*, not reopens | **GREEN (survived)** | RED | RED |
| M-C | call site: `if reopens:` instead of `if reopens is not None:` — suppress a genuine `0` | GREEN | GREEN | RED |
| M-D | call site: read only the ACTIVE step's `rework_count` (run-scoped → step-scoped collapse) | RED | RED | RED |
| M-E | call site: drop `pending` gates — i.e. apply the conceded under-count deliberately | — | — | RED (full suite: 1 failed) |

**Nothing survived the suite.** Two results worth reporting anyway:

- **M-B survives the new tests.** With `T=1,E=1` and `T=3,E=2` spread one-per-gate, counting
  tasks and counting reopens give the same answer. Magnitude is pinned only by the older
  `test_reopens_tracks_real_engine_reopens_and_keeps_counting` (one gate reopened twice). Not
  a defect — the new tests are not *supposed* to own magnitude — but it is the shape of the
  new coverage, stated honestly: the new tests pin **which gates count**, the old ones pin
  **how much each counts**. Neither alone is sufficient.
- **M-C is caught, but not where you would look.** Both `Reopens` test classes stay green;
  the catch comes from `ZeroAgentEffortTests::test_claim_and_start_alone_emit_the_full_group`
  via the delta validator (`create.mechanical.reopens: must be a non-negative integer`). The
  `0`-vs-absent distinction this field's doctrine rests on is pinned — just at the schema
  boundary rather than in the field's own tests.

---

## 2. Both-seams verification — the test does what it claims

Verified **by measurement, without touching `episode_capture.py`**: I rebuilt the scenario
through the real CLI and read the journal/rework state *the seam would see*.

```
E=1  journal-at-seam=2   truth=2   -> CANCELS   (a max() implementation emits 2 = correct)
E=2  journal-at-seam=4   truth=3   -> DIVERGES by 1   (emitted 3)
     journal lines after the verb = 5
```

- **The cancellation is real.** At a `reopen` seam with a single escalation the journal
  witness reads exactly the truth, so a one-escalation reopen-seam test **passes on the
  broken code**. The reviewer of attempt 1 was right and the implementer's response is
  correct: the two escalations in `test_escalations_do_not_inflate_reopens_at_a_reopen_seam`
  are **load-bearing, not belt-and-braces**.
- **The test really does use two.** It escalates `a` and `b` (loop), reopens `c` for the
  third real reopen. `T=3, E=2`. My measured journal-after-verb of `5` matches the test's own
  `assertEqual(self.journal_reopen_lines(), 5)` exactly.
- **The start-seam case is genuinely a `start` seam.** `mechanical/b.json` is first written
  by `start b`; `b` was never started before. The escalated `reopen` returns from its
  cap branch *before* `emit_step_manifest`, so it writes nothing.
- **The reopen-seam case is genuinely a fresh reopen-seam read, not a stale start-seam file.**
  `emit_mechanical_snapshot` **overwrites** where the manifest is write-if-absent
  (`episode_capture.py:454` docstring, and the code does what it says). Without that,
  `mechanical/c.json` would still hold the `reopens: 2` written at `start c` and the test
  would be reading the wrong instant. It does not.
- **Fixture-divergence assertions present in both.** Each test asserts
  `journal_reopen_lines()` and `rework_total()` *before* asserting the emitted value, with an
  explicit `"fixture no longer diverges"` message. The tests cannot drift quietly green.

---

## 3. Fix B — completeness, cost honesty, and the fold-in deviation

**Complete. Your claim CONFIRMED, not taken.** Repo-wide sweep:

- `journal_reopens` — **zero** references anywhere (excluding `.git`).
- `find_spine_path` — **zero** references anywhere.
- `_rework_total` — **zero** references anywhere.
- `spine_path` still appears widely, but every hit is an unrelated local in
  `checklist_engine.journal_path`, `scripts/hooks/spine_rail.py`,
  `scripts/hooks/gauge_writer_hook.py` and their tests. **No caller passes `spine_path=` to
  `mechanical_fields`** — the only two call sites are `episode_capture.py:491` and
  `tests/test_episode_fields.py`, both on the two-argument form.

**The under-count cost is real, reachable, and correctly described — measured, not reasoned.**
The docstring concedes an `amend` dropping a `pending` gate with `rework_count > 0`. A reader
could reasonably doubt that state exists at all, since `reopen` refuses anything that is not
`complete` and sets it `in-progress`. It exists, by an ordinary route:

```
1. reopen b (its own rework)  -> b complete, rework_count=1, reopen_total=1
2. reopen a (upstream)        -> cascade-reset downstream ['b']
                                 b: status=PENDING, rework_count=1, reopen_total=2
3. amend --delta drop b       -> rc=0, "amended: dropped b"
                                 reopen_total = 1   (was 2)
```

The cascade in `reopen()` resets a downstream `complete` gate to `pending` **without clearing
its `rework_count`**, and `amend`'s `drop` accepts any `pending` gate. So the docstring does
**not** overstate the cost. Nor does it understate it: `amend drop` is the only thing in the
engine that removes a task, so this is the whole of the exposure. The one thing the docstring
leaves out is *how* a pending gate acquires a `rework_count` — the cascade — which is worth a
clause but is not a correctness defect.

**Fold-in deviation: ACCEPT, and I agree with your inclination.** Behaviour is identical, and
not by inspection alone — the diff shows the old `_rework_total` **body was moved intact**;
only its `def` line and docstring were deleted. The `None`-on-non-dict-`tasks` path and the
`isinstance(count, int) and not isinstance(count, bool)` guard are byte-identical.
`test_reopens_is_refused_only_when_the_witness_cannot_be_read` still exercises both directly
(`None` for `"tasks": "not a mapping"`, `0` for `{}`). With one witness left, two names for
one sum is indirection with no reader; the implementer's reasoning holds.

The one behaviour change that *is* real is the intended one: `reopen_total` previously
returned the journal reading when `_rework_total` was `None`, and now returns `None`. That is
fix shape B, ruled.

---

## 4. Doc and prose corrections — re-measured, not read

All three schema-doc claims re-measured on a live checklist through the real CLI. **All three
true as written.**

| Claim | My measurement | Verdict |
|---|---|---|
| The arming write sits inside a verb function, so "written by the CLI boundary alone, never by a verb function" was wrong | `cl.setdefault("refusals", 0)` at `checklist_engine.py:964`, inside `claim()` (def at 894; `main()` at 2591) | TRUE |
| A malformed verb exits 2 before the checklist loads and is never counted | `frobnicate a` → `rc=2`, argparse usage on stderr, `refusals` unmoved at `0` | TRUE |
| Checklist-scoped: a foreign session's refusal increments the owning run's tally | `start b --session-id SOMEONE-ELSE` against a held lease → `rc=1`, `refusals 1 → 2` | TRUE |

I also checked the new sub-claim the doc adds — that the arming write *must* sit after
`claim`'s idempotent-resume early return. It does: the `return f"resumed lease {session_id}
(heartbeat refreshed)"` is ~34 lines above line 964. **True as written.**

**Your sweep claim — CONFIRMED.** Repo-wide grep for `over-count`/`overcount` and `witness`
across `*.py` and `*.md`: the only surviving prose is in `episode_capture.py` (the corrected
docstring), `tests/test_episode_fields.py` (the two corrected docstrings, including the
`ReopensFieldTests` class docstring at :331 the implementer found), and one unrelated hit at
`docs/EPISODE_STORE.md:302` about an `impact-cost` assertion. **`docs/EPISODE_STORE.md` names
`reopens` (lines 145, 249) but nowhere pins its SOURCE**, so there was no fourth site to
correct. No falsified assertion of the "neither can over-count" invariant survives anywhere.

**Handoff error (your §5) independently confirmed:** the falsified test docstring is in
`tests/test_episode_fields.py`, not `test_episode_capture.py`. The implementer was right and
the code wins.

---

## 5. Deviations

- **Nothing contradicted the handoff.** Both claims you flagged as unverified checked out.
  Where the handoff and the code could have disagreed (§5's file name), the implementer had
  already corrected it and I confirm the correction.
- **I ran five mutations, not one.** The brief asked for one outside both spent sets; I added
  four more specifically to hunt a survivor, because "nothing survived" is only worth
  reporting if you actually tried to make something survive.
- **Fowler `comments-as-deodorant` marked `overridden`, not `flagged`.** 38 lines of docstring
  over an 8-line body is prima facie deodorant on Fowler's baseline reading. I overrode it
  citing `docs/EPISODE_STORE.md`'s mechanical-bin standard: the prose is not covering for
  unclear code, it records the measurement that falsified the previous sourcing — and this
  entire rework exists because the earlier docstring asserted an invariant nobody had
  measured. Reason logged in the record; rail exits 0.
- **Two observation-level Fowler flags, neither a blocker.** `large-class`
  (`EscalatedReopenIsNotAReopenTests` carries seven fixture helpers for two tests) and
  `duplicated-code` (it re-implements `build`/`verb`/`complete` that the file's existing
  `LiveSpine` already provides; the divergences — `config.rework_cap: 1`, a three-item spine,
  and `say` asserting the engine's own message — are real, but the two fixtures are now one
  refactor apart).
- **Triage candidate `tc1` raised on the survey:** nothing pins the conceded under-count. It
  is deliberately accepted, but unpinned, so a future change could widen an accepted cost into
  an unaccepted one silently.

---

## 6. Suite

```
$ python -m pytest -q          # in C:/Programs/constellation-skills-wt/e298-305
1472 passed, 2 skipped, 472 subtests passed in 73.47s
```

Matches the handoff baseline exactly. Run twice: once at the start (80.58s) and once after
all mutation work, to prove I left nothing behind.

**Tree integrity after five mutate/restore cycles** — `git status --porcelain -- scripts/
tests/ docs/` is empty, and every touched file's blob OID equals HEAD's:

```
scripts/episode_capture.py    head=8a38e33d… work=8a38e33d…
tests/test_episode_fields.py  head=fde5041a… work=fde5041a…
docs/CHECKLIST_SCHEMA.md      head=2f378d80… work=2f378d80…
```

Nothing committed. `C:/Programs/constellation-skills` and all sibling worktrees untouched.

---

## Workflow Feedback

- **The handoff was unusually good on the one thing that mattered**: naming both spent
  mutations *with their reported failure values* let me check my own results against them for
  consistency (my `E=2` measurement of 4-vs-3 matches the implementer's reported `4 != 3`
  exactly, which is corroboration I could not have got from "a mutation was run").
- **Friction, minor:** the handoff says to drive the survey with the worktree's
  `scripts/checklist_engine.py` but does not mention that `current` **refuses** `--session-id`
  (unrecognized argument) while `record`/`start`/`consolidate` require it. Cost one refused
  invocation. Similarly `flag-candidate` takes `--from`/`--statement`, not
  `--title`/`--rationale`; the handoff's survey-verb note covers `record`/`advance`/`reopen`
  but not the candidate verb.
- **Improvised around:** the survey template's `config_ref` points at
  `docs/agents/engine-config.json`, which does not exist in this worktree (`docs/agents/` holds
  only `ORCHESTRATOR_CONTEXT.md`). The engine did not object, so I left it. Likewise
  `r0-context` directs me to `docs/agents/CREW_CONTEXT.md` and `GLOSSARY.md`, neither of which
  exists here — recorded as "not present" rather than treated as a gap.
- **What I would want next time:** the handoff's §3 asked me to confirm a path is "actually
  reachable" without saying whether a measurement or an argument was wanted. I measured. If
  measurement is the standard for reachability claims, saying so would make the bar explicit
  rather than a reviewer's choice.
