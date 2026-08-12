# Cold plan critic — panel of 3, findings and disposition

**Panel, not a single critic.** Surfaced choice: this plan changes the engine's core policy
and #467 records that workstream F (#424) is blocked on it. Three lenses, each a cold reader
given only the issue, the mission frame, and `execute.json` — no design candidates, no
convergence note, no exploration record.

The panel found **two disqualifying defects in my converged plan**. Both are recorded here
in full, because a critic panel that produced only cosmetic edits would itself be a check
that cannot fail.

## Accepted — plan changed

| # | Lens | Finding | Disposition |
|---|---|---|---|
| 1 | intent-fit, testability (**independently, both**) | **DC6 as I specified it was true by construction.** "Did a handoff artifact appear before the next advance" is always yes: `advance` already refuses a non-exempt gate without `--why`. The signal would have read compliant in both the healthy world and the world where the agent ignored the instruction. | **Redefined.** The observable is now **"did anyone BEGIN work while over the line"** — `begin-refused` / `begin-released` ledger entries. In the healthy world **no ledger entry exists at all**, because the agent stopped and its successor's gauge reads below the line. g4 rewritten. |
| 2 | intent-fit | **`advance --mechanical` defeats DC3.** With the guard off `advance`, a tripped agent closes its gate with a mechanical marker; `_latest_why_record` skips markers, so the DIGEST stays pre-trip — #431 reproduced *after* the fix — and the releasing refresh-request would then be keyed to that stale record and pass #190's identity check. | **Accepted.** g2(c): at/over hard, `--mechanical` is refused and `why_exempt` is suspended. Framed as a refusal of *silence*, not of the advance. |
| 3 | intent-fit | **`reopen` is an unguarded begin-work verb.** It drives a complete gate back to `in-progress` and cascades. | **Accepted, verified in source.** `reopen` is now guarded alongside `start`. |
| 4 | simplicity | **Guarding `resume` reintroduces #431.** `resume` restores a *blocked* gate to its prior status; for an `in-progress` prior it returns the agent to the gate it is already mid-way through — the exact case the design promises never to refuse. | **Accepted, verified in source.** The `resume` guard is dropped. Findings 3 and 4 are opposite corrections to the same line; both are right. |
| 5 | testability | **g5's attestation was unfalsifiable** — a well-written ACCEPTANCE.md is indistinguishable from a round trip, and nothing records what agent B was actually given. | **Accepted.** g5 gains a `g5-review` + `g5-integrate` pair; c1 becomes a **command** postcondition running a verifier script over the round-trip spine (two distinct session ids, A's why-record at the tripping gate, B's advance after A's last action, expected ledger entries); B's **verbatim dispatch prompt** must be recorded. |
| 6 | testability | **The mutation mandate was satisfiable by an unrelated break** — "I deleted the guard, 40 tests went red" met it verbatim. | **Accepted.** Every log line must name the branch broken, show **the named test** failed, and state the **total** failure count. |
| 7 | testability | **Every integrate postcondition was a bare `pytest -q`**, which is already green at the untouched baseline — it cannot distinguish "fix shipped with tests" from "fix shipped with none". | **Accepted.** Each integrate gains a `pytest -k <pattern>` check. `pytest` exits **5** on an empty collection, so a gate that shipped no tests cannot satisfy it. |
| 8 | testability | **The DC2 "not refused" half was trivially satisfiable** by copying an existing test that passes on both sides of the fix — and, pinned correctly at `fill >= hard` with **no** pending request, it **is** a permanent regression guard against the deadlock. | **Accepted, and it corrects #467.** g2 now mandates that pinning. See "Surfaced to the Admiral" below. |
| 9 | testability, simplicity (**both**) | **The ledger cannot be written at `current`** — `main()` skips `save()` for that verb, which is where the band is most often evaluated. | **Accepted.** The ledger is scoped to **mutating** chokepoints, and the case it therefore cannot see (an agent told to wrap up that simply stops) is written into `docs/CHECKLIST_SCHEMA.md` as a named limit rather than left to be discovered. |
| 10 | testability, simplicity, intent-fit (**all three**) | **g2(e), refusing a dangling `why_ref` on `attach`, is unasked scope** that breaks existing tests, and it already fails **closed** — a dangling pointer makes the identity predicate return False, so the agent stays guarded. | **Dropped from the plan.** The concrete-why-id improvement to the hint text is kept: it serves DC1 (the instruction must be actionable) and changes no behaviour. |
| 11 | simplicity | **The override's checklist-config tier has zero adapters** — one adapter is a hypothetical seam. | **Accepted.** Gate-level only. |
| 12 | testability | **g3's "malformed value resolves to 0" test is green if the whole mechanism is dead code.** | **Accepted.** The same test must carry a positive assertion through the same resolver. |
| 13 | simplicity | **g4's separate `current` render duplicates `_trip_advisory`'s HARD branch** — two strings computing one fact will drift. | **Accepted.** Extend the existing branch; do not add a second render. |
| 14 | simplicity | **The ledger was over-specified at seven fields**; `why_ref` is recoverable from `why_trail`. | **Accepted in part.** `why_ref` dropped. `gate` and `hard` kept: `hard` is the *resolved* threshold under a per-gate override and is not recoverable without re-resolving. |
| 15 | intent-fit | **DC4 ships an ungraded number into a production template.** | **Accepted in part.** The reserve is graded `@grade: guess` with a named settle experiment, and the number's provenance is stated. Surfaced to the Admiral below. |
| 16 | simplicity | **`constraint:no-threshold-values` contradicts recording the resolved threshold.** | **Accepted as a wording fix.** The engine does not *compute* thresholds; `gauge_reader` does. Recording the fraction it returned is not arithmetic. Stated explicitly in g3. |

## Rejected, with reasons

| # | Lens | Finding | Why rejected |
|---|---|---|---|
| R1 | simplicity | g1 spends three tasks on an artifact the plan itself calls disposable; five gates could be four. | #467 **mandates** reproducing the deadlock RED first, and an independent read on the RED is the one guard against a *manufactured* RED — which is this epic's central defect. The cost is real and accepted. |
| R2 | intent-fit | g5 licenses "partial is acceptable", so DC5 could be reported unearned. | Half accepted, half rejected: partial stays honest reporting for DC1-DC4 and DC6, but **DC5 is now excluded from it** — it completes, or it returns to the Admiral as a scoped null naming the specific mechanism. |
| R3 | testability | "The agent that kept working" is unobservable by construction (gate-boundaries-only), yet g4 asks the implementer to enumerate its own defect shapes. | Partly right, and the redefinition in finding 1 is the answer: the agent that kept working must eventually run `start` or `reopen`, and *that* is observable. The mid-gate stretch remains unobservable and is now a stated limit, not a claim. |

## ADMIRAL RULINGS — 2026-08-08: all three APPROVED, none reversed

Read this before the section below it. That section is what I *asked*; this is what was
*answered*. Every condition is binding and has been written into `execute.json` as a gate
constraint.

1. **DC2 by verb choice — APPROVED.** *Condition:* report it as **done-by-different-means**,
   never as done-as-written, with the reasoning inline in the per-done-condition accounting. A
   reviewer must be able to see the departure without reading the DIT. → `g5-acceptance`.
2. **The "no residue" over-statement — APPROVED, and it improves the issue.** Not a spec
   challenge; #467 was pessimistic about its own RED. *Condition:* say plainly in ACCEPTANCE.md
   and in the return that the claim was over-stated and this pin is the correction, so the
   finding is visible rather than buried in a passing test. → `g5-acceptance`.
3. **The production-template override — APPROVED.** Acceptable because DC4 mandates exercising
   exactly one, it is tighten-only so it can only fail in the conservative direction, and it is
   graded `guess` with a named settle experiment. *Condition, straight from DC4's literal
   text:* show the override changes that gate's behaviour **and not its neighbours'** — a test
   proving only that the overridden gate trips earlier has **not** met DC4. Name the settle
   experiment in the return so the Admiral can route it. → `g3-implement`. The Admiral is
   disclosing this to Tommy at the wave-4 checkpoint as a behaviour change shipping for every
   future commander run; that is disclosure, not a hold.

**Binding retraction — the Admiral withdrew his own field evidence.** LO-467's item 2 (crews
trip at 17-21%, the Admiral ran to 44% untripped) is **retracted** and must not be used for
anything. My refutation was accepted: `no trip at 44%` and `no gauge at 44%` are
indistinguishable without an asserted live reading, and the engine's own projection had in fact
printed `CONTEXT GAUGE SILENT ... too old (or otherwise rejected) to trust as a live reading`
at that path. What survives is stronger and stands alone: **this Commander's own asserted,
live, single-binding reading of `0.194023`** (`claude-opus-5`, 2026-08-08T09:49:48Z), recorded
by the Admiral at `.agent-work/epic-418-redux/evidence/w4-467-gauge-observation.md`. That is
DC4's *"overrides only where a gate has bitten"*, exercised, with no comparison needed.

**Two write-ups the Admiral values above the fix itself:**

- **`CHECK_THAT_CANNOT_FAIL.md`** — my own first DC6 observable was a check that cannot fail,
  true by construction, caught by my own cold panel before any code was written. To be written
  up properly as a first-class artifact, not compressed to a line. Required deliverable of
  `g4`.
- **The anti-vacuity gate check** (`pytest -k` exiting 5 on an empty collection). Being routed
  as a doctrine candidate. The return must say where it lives **and how it was verified to
  actually fire** — an unfired anti-vacuity check is itself a check that cannot fail. → `g5`.

**Provenance note on `execute.json`.** These conditions were added after `plan` closed but
before `execute` was ever started: the file had never been driven by the engine — no lease, no
evidence, every gate `pending` — so this is still authoring, not a mid-run hand-edit of a
frozen plan. Once `execute` starts, the ban stands and any further change goes through the
engine's `amend` verb.

## Surfaced to the Admiral — decided under Commander's-call latitude, open to reversal

1. **DC2 is satisfied by verb choice, not by two kinds of `advance`.** #467's words are "an advance that starts new work above threshold is refused". Under the shipped engine no advance ever starts work — `start` does. My reading refuses `start`/`reopen` and never refuses an `advance`. The intent-fit critic called this "defensible under Open (Commander's call)" and it is the reading I have taken; it is the one place my plan departs from the issue's literal text, and I would rather you knew than discovered it at return.
2. **#467's Evidence section slightly over-states the residue claim.** It says the RED "cannot stand as a regression test". True for the full end-to-end scenario; **not** true for its load-bearing branch — a test pinned at `fill >= hard` with no pending refresh-request, asserting the advance completes and the digest updates, is red against today's code, green only after the fix, and permanent. I am shipping it as the standing guard. This strengthens the issue rather than contradicting a `Fixed` item, so I have not treated it as a spec challenge.
3. **One production-template change.** The exercised DC4 override lands on the commander spine's `execute` gate. It is **tighten-only** — it can only make that gate trip earlier, never later — and it is graded `guess` with a settle experiment. It is not the global default, so it is inside my fence, but it changes behaviour for every future commander run and you should have the chance to say no.
