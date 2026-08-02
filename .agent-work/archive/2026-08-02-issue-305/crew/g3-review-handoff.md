# Reviewer Handoff

## Gate
`g3-review` — issue #305, epic #298. Reviewing `g3-implement` (attempt 1, APPROVED into review by me).

## Task statement

**Your primary job is to try to make the negative control pass while testing nothing.**

The gate imperative names three specific attacks. Run them, and then go beyond them — the three are
*floor*, not ceiling:

1. Replace the composer with hardcoded constants → confirm the control goes **RED**.
2. Delete the ground-truth tally → confirm it goes **RED**.
3. Make every declared context ref resolve to a missing file → confirm an **all-null manifest does
   NOT read as success**.

**If any of those still scores green, the control is vacuous and this gate BLOCKS.**

Also verify the synthetic consolidation was genuinely discarded — **by blob OID or normalized
content, not by the implementer's say-so**.

## Why this gate exists, stated plainly

This epic has produced **seven** costumes of a check that could not fail (#337) — including one found
*inside the gate built to prove checks can fail*, and one **in this very gate**: I ran a mutation that
silently failed to apply and briefly had a "13 passed" that meant nothing. I caught it only because I
compared the blob OID before trusting the green. **Assume the same trap is still here somewhere.**

`decision:zero-agent-effort-is-literal` is `@grade: settled/human`. The control is the *test* of it,
not a formality. If the control is hollow, the issue's central claim is unevidenced.

## What to review

- **`tests/test_episode_negative_control.py`** — new, 13 tests. The control, 4 in-suite red-proofs,
  4 retrieval/canon tests.
- **`.agent-work/issue-305/evidence/g3_control_repro.py`** — one-command repro.
- **`.agent-work/issue-305/evidence/g3_return_item_4_callsite_sever.md`** — my own call-site-sever
  evidence (see "Claims of MINE to attack" below).
- **`scripts/episode_capture.py`** — must be **byte-identical to HEAD**. Verify by blob OID; do not
  eyeball it.

How to inspect the diff:
```bash
cd "C:/Programs/constellation-skills-wt/e298-305"
git log --oneline 3f787a3..HEAD
git diff 3f787a3..HEAD -- tests/ scripts/
git hash-object scripts/episode_capture.py      # must equal:
git rev-parse HEAD:scripts/episode_capture.py   # 8a38e33d1c12bb814d4383a42bfe389d6aee7e93
```

## MUTATIONS ALREADY SPENT — seven. Devise something OUTSIDE this set.

**You cannot audit your own falsifiability, and neither can I.** An independent mutation outside the
shipped set has found real holes **four times this epic**. That is your highest-value contribution
here. Do not re-run these:

| # | who | mutation | caught, naming |
|---|---|---|---|
| R1 | implementer | `mechanical_fields` → ten plausible constants | all ten fields |
| R2 | implementer | `failed_command_count` → `0` | `['failed-commands']` |
| R3 | implementer | `_lease_role` → `"implementer"` on the child | `['role']` |
| R4 | implementer | `reopen_total` → `1` | `['reopens']` |
| M-C | **me** | `manifest_ref` revision → a constant plausible sha1 | `['context-manifest-ref']` |
| M-D | **me** | drop `artifact-ref` (absent from `REQUIRED_MECHANICAL_FIELDS`, so a control iterating only that tuple would miss it) | `['artifact-ref']` |
| M-E | **me** | sever the seam at its **call site** (non-destructively, via `sitecustomize`) | control RED (8/13) |

**Fields nobody has yet mutated: `run`, `project`, `spine-step`, `rework-count`, and `refusals` on the
parent topology.** That is where I would hunt. `project_name()` and the `active_id()`-derived
`spine-step` look softest to me — but that is a hint, not an instruction, and my guesses have been
wrong before.

Also worth attacking, beyond single-field mutations:
- **Can the two topologies be made to agree when they should not?** The control's whole discriminating
  power is that parent and child differ **only** by the lease. Try making the child appear claimed, or
  the parent unclaimed, and see whether the control still distinguishes them.
- **The four counters are asserted to be four distinct numbers** (`rework-count=1, reopens=2,
  failed-commands=3, refusals=4`). Try to make two of them alias and see if it is caught.
- **`Expect(REFUSED, …)` must fail if a refused field turns up PRESENT.** R3 claims to prove this.
  Verify it independently — a refusal assertion that cannot go red is the exact hole this gate is for.

## Claims of MINE to attack — do not treat these as settled

I am not independently verifiable by myself. Three of my own calls need your adversarial read:

**1. RULING: `advance --mechanical` satisfies C1's "records nothing".**
The implementer flagged this as load-bearing and said *"if it does not, the whole control is
invalid."* It is too load-bearing to rest on my judgment alone.
My reasoning: `advance` refuses a non-`why_exempt` gate without `--why` or `--mechanical`
(`checklist_engine.py:1712`), so **one of them is mechanically required** — and C1 permits actions a
run mechanically requires. `--mechanical` is a flag, not prose; the engine appends
`why=None, mechanical=True` and explicitly never lets a mechanical marker become the digest.
`--why` would have been agent-authored content; `--mechanical` is not.
**Attack it.** If you conclude `--mechanical` is "recording something", say so and BLOCK — I would
rather re-cut the control than ship one whose premise is wrong. Same question applies to
`reopen --reason`, which the implementer disclosed as a fixed constant `"control"` feeding no field.

**2. My return-item-4 evidence.** I claim that severing the call site turns the control RED, but that
#300's own test files (`test_context_manifest.py`, `test_episode_capture.py` — 94 tests) stay
**green** under the same sever and **never reach the call site** (measured reached-count: `0`).
Reproduce it. If the reached-count is actually non-zero, my conclusion is wrong and the PR body
should not carry it.

**3. My characterisation of the honest null** (filed as **#379**): that `role`/`refusals` refuse at
every child-gate seam because the child is never claimed, and that `_validate_create` requires both,
so a gate snapshot cannot become an episode without agent effort. **Check the "requires both" half in
particular** — I read it off `MECHANICAL_SCALAR_FIELDS`; confirm it against the validator's actual
behavior, not the tuple's name.

## Close Criteria

- All three named attacks run; each confirmed RED, or the gate BLOCKS.
- **At least one mutation of your own devising, outside the seven above**, with its result — caught or
  not caught. **A not-caught result is a finding, not a failure**; report it.
- The synthetic consolidation's discard verified **by blob OID / normalized content**, independently —
  not by re-reading the implementer's pasted listing. **Confirm the store is non-empty first**, so
  identical-listing is not an empty-vs-empty pass.
- `scripts/episode_capture.py` confirmed byte-identical to HEAD by blob OID.
- Full suite re-run in your own hands. Expected **1485 passed / 2 skipped / 472 subtests**.
- My three claims above adjudicated explicitly, each as upheld or overturned.

## Constraints

- **Prove you read BOTH things, then compare.** Empty-vs-empty, missing-vs-missing and
  skipped-vs-skipped all pass a naive equality check.
- **Assert against the FIELD, never a substring of the serialized record** — `json.dumps` flattens
  structure and a substring scan cannot tell a value from a mention of it.
- **A predicate with a boundary needs cases on both sides; one over a collection needs a
  multi-element case; a fixture that cannot reach the failing condition is as vacuous as a predicate
  that cannot discriminate.**
- **Repairing a vacuous check does not retroactively support conclusions that rested on it** — if you
  fix one, name what else carries those conclusions.
- **Verify your mutation actually applied before trusting its red or green.** Compare the blob OID.
  This bit me in this very gate, and it is costume #4 in #337.
- **Restore every mutation and prove it** — blob OID equal to HEAD, `git status --porcelain` empty.
- Blob OIDs / normalized content only, never raw working-tree bytes (#319 — `core.autocrlf`).
- `python -m pytest`, never `py -m pytest`. **`py` produces no output and no exit code under the
  PowerShell tool** — use Bash for `py`.
- Windows: explicit `encoding='utf-8', newline='\n'` on writes. `Path.read_text(newline=...)` is
  3.13+ and breaks CI's 3.12 pin.
- **Do not fix what you find.** Report it. Out-of-scope finds become triage candidates.

## Map Anchors (inbound)

Carried **verbatim** from `g3-implement`'s `anchors` block in `execute.json`.

- **Structural:**
  - `struct:query_episodes — retrieval under test`
  - `struct:episodes/active — the store, as shipped`
- **Capability:**
  - `capability:cross-run-retrieval — the acceptance surface`
- **Constraints/assumptions:**
  - `constraint:throwaway-consolidation`
  - `constraint:no-raw-worktree-bytes`
- **Decision anchors:**
  - `decision:throwaway-consolidation — the synthetic consolidation is discarded; a test artifact must never become canon`
    `@grade: settled/inherited · leans g3-implement`
  - `decision:zero-agent-effort-is-literal — the control is the TEST of this, not a formality`
    `@grade: settled/human · leans g3-implement`
- **Evidence expectations:**
  - `claim:negative-control-can-fail — REQUIRED before any green is trusted; the check most at risk in this issue`
- **Map confidence flags:**
  - `This gate is the one most likely to be vacuous — four costumes already in this epic (#337), and my own first draft of it was the fifth. Scrutinize accordingly.`

## Evidence the implementer produced (verify, do not inherit)

- Both topologies driven through the **identical verb sequence**, so the lease is the only difference.
- Verbs issued: `claim, start, attest, advance, reopen` — asserted by the harness itself.
- Ground truth incremented on the line issuing each call; `context-manifest-ref` cross-checked against
  `git hash-object --no-filters` as a second code-disjoint witness.
- Canon before/after: 3 paths, 3 identical blob OIDs, store non-empty (2 real episodes + `.gitkeep`).
- `neighbour_ids("cluster-002")` → `['cluster-001','cluster-003']`, unchanged after consolidation.
- Suite 1485/2/472; baseline independently re-verified at 1472/2/472.
- **#321:** the implementer reports the unvalidated-handed-id path is on the **read** side
  (`fetch_episode` returns `None` for a malformed id, conflating it with "missing"), not the write
  side. Sanity-check that; it inverts what the launch order assumed.

## Test Mode
`inspection + adversarial mutation` — you are not adding features. Any test you write is a probe;
say so and do not leave it in the tree unless it is a genuine coverage gap you are reporting.

## Suggested Model Tier
**Opus** — mandated by the epic's cold-panel floor (`decision:review-class-floor`, not downgradable).
No Fable at any tier.

## Authority

**Settled — do not reopen:** the seam's placement (`start`+`reopen`, write-if-absent); g2's `reopens`
fix shape B; `refusals` as a documentation fix (#367); mechanical snapshot **not** auto-created
episodes; refuse-never-fabricate; the throwaway consolidation.

**Explicitly open to you:** whether the control is vacuous; whether `--mechanical` breaks C1; whether
my return-item-4 and #379 characterisations hold.

**Not yours to decide:** how to *fix* the #379 honest null — that is mine and the Admiral's.

## Stop Conditions
Stop and return if: any named attack scores green (BLOCK); a decision outside this authority is
needed; you cannot verify a load-bearing claim either way — say which, and why, rather than guessing.

## Return Format

Return **REVIEW_RESULT** with an explicit verdict: `APPROVE`, `APPROVE-WITH-FOLLOWUPS`, or `BLOCK`.

> **Verdict note:** `APPROVE-WITH-FOLLOWUPS` is a sanctioned verdict here and I will accept it. Do
> **not** round it to a bare `APPROVE` to satisfy a gate — a gate that cannot accept your real verdict
> is a gate defect (filed as **#371**), not a reason to change your finding. State what you actually
> concluded.

Include: your own mutation and its outcome; each of the three named attacks with its result; the
consolidation-discard verification; the three claims of mine, adjudicated; blockers vs followups
separated; out-of-scope observations; and **Workflow Feedback** — blunt, it is harvested into the run
retrospective.

**Deliver your REVIEW_RESULT via `SendMessage` to `commander-305d` before ending your turn.**
