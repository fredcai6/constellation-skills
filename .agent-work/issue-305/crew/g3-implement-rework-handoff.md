# Implementer Handoff — g3-implement, ATTEMPT 2 (REWORK)

## READ THIS FIRST — you are reworking, not starting over

**The `constellation-implementer` skill opens by demanding a fresh plan. That is WRONG here.** This
is attempt 2 against work that already exists and is mostly good. **This handoff overrides the
skill's opening.** Do not re-plan the gate, do not rebuild the control, do not touch anything outside
the three fixes below. (Known skill defect — four reworks this epic have now hit it. Not yours to fix.)

**The prior work is APPROVED in substance.** `tests/test_episode_negative_control.py` exists, has 13
tests, and its *central* claim — the mechanical group is present and correct against an
independently-tallied ground truth, on both lease topologies — is **real and falsifiable**. Seven
independent mutations have each been caught naming exactly the broken field.

**What failed review is narrower and sharper: two of the control's PREMISE GUARDS are checks that
cannot fail.** The control proves the right thing; two of the assertions that are supposed to prove
*the control was set up honestly* prove nothing.

## The three fixes. Nothing else.

### FIX 1 (load-bearing) — `test_control_records_nothing_agent_authored` cannot fail

Current body, in full:

```python
for run in (control["parent"], control["child"]):
    assert set(run.issued) <= set(_ControlRun.VERBS), sorted(set(run.issued))
# No `--finding`, no narrative `attach`, no `--why`, no hand-written episode: the
# only verbs above are claim/start/attest/advance/reopen, `attest` was passed no
# note, and `advance` was passed `--mechanical`.
assert "attach" not in control["parent"].issued
assert "flag-candidate" not in control["parent"].issued
```

**The problem:** it asserts only that the issued **verb names** are a subset of the allowed verbs —
which `_ControlRun._run` already asserts on every call, so this adds nothing. The two `not in`
assertions are implied by that same subset check. **Every claim about flags — `--why`, `--note`,
`--finding`, `--mechanical` — lives in a COMMENT and is asserted nowhere.**

**Proven by the reviewer (mutation M1):** rewriting every `advance --mechanical` to
`advance --why "<narrative prose>"` **and** adding a `--note` to every `attest` leaves the suite at
**13 passed**, with four prose rows verifiably present in `why_trail` and in `satisfied_by`.

A test named "records nothing agent authored" that passes while the run records agent-authored prose
is the #337 class exactly — and it sits on `decision:zero-agent-effort-is-literal`, which is
`@grade: settled/human`.

**Required:** assert against the **actual argv of every issued call**, not the verb name. The guard
must go **RED** if any of these appears anywhere in the control's issued commands:
`--why`, `--note`, `--finding`, and any narrative `attach`/`flag-candidate`.

Positively assert, rather than comment:
- every `advance` carries `--mechanical`;
- no `attest` carries `--note`;
- the **only** text-bearing flag in the entire run is `reopen --reason`, whose value equals the
  declared constant `_ControlRun.REOPEN_REASON`.

**Bounded exception to state explicitly, not to hide:** the reviewer established that
`reopen --reason` **does** write its string into `why_trail`. So the honest claim is *"the only
agent-authored text in the entire control is one fixed constant that feeds no mechanical field"*,
**not** *"nothing agent-authored was recorded."* Say it that way in the docstring and let the
assertion match it.

**Red-proof required:** reproduce the reviewer's M1 (swap `--mechanical` → `--why "<prose>"`, add
`--note` to attests) and show the fixed guard goes **RED naming that**, then restore. M1 becomes a
regression test, not a one-off.

### FIX 2 (load-bearing) — `test_every_field_has_a_named_independent_source` cannot fail

Current body:

```python
for name, exp in expected.items():
    assert exp.source.strip(), name
    for forbidden in ("mechanical_fields", "reopen_total", "failed_command_count",
                      "cm.rev(", "the emitted snapshot"):
        assert forbidden not in exp.source, (name, forbidden)
```

**The problem:** `exp.source` is a **human-readable description string**. This scans that prose for
forbidden substrings. An oracle whose *code* calls `mechanical_fields()` passes cleanly as long as
its *description* does not mention it. The guard checks what the harness **says about itself**, not
what it **does** — and it is a substring scan on a description, which is the "assert against the
FIELD, never a substring of the serialized record" trap one level up.

**Proven by the reviewer (mutation M5):** rewiring the oracle to read its tallies back out of the
composer is **not caught**.

**Required:** make the independence structural rather than declarative. Either is acceptable; pick
one and justify it:
- **(a) Behavioural:** build the expectations with the forbidden symbols patched to raise
  (`mechanical_fields`, `reopen_total`, `failed_command_count`, `manifest_ref`, `context_manifest.rev`,
  and any read of the emitted snapshot). If the oracle touches one, it raises and the test fails. This
  proves independence by execution, which is the strongest form.
- **(b) Static over CODE, not prose:** inspect the source of the expectation-building code
  (`_ControlRun.expectations` and anything it calls) and assert the forbidden symbols do not appear.
  Weaker than (a) — an indirection defeats it — so if you choose (b), say why (a) was not workable.

**Keep the prose check too** — it is cheap and it documents intent — but it must no longer be the
only thing standing.

**Red-proof required:** reproduce M5 (make the oracle source a tally from the composer) and show the
fixed guard goes **RED**, then restore.

### FIX 3 (smaller, but it closes the reviewer's A3) — the delivered-context half is never exercised

Attack A3 was *"make every declared context ref resolve to a missing file; confirm an all-null
manifest does not read as success."* It scored **GREEN (13 passed)**, and the reviewer confirmed all
three manifest rows really were `rev: null`.

That green is **defensible for `context-manifest-ref` itself** — the field is a byte-pin over the
manifest's own bytes, and the harness's independently-computed OID correctly tracked the mutated
bytes. So the field behaved correctly.

**But the reviewer identified the real gap: the control's plan declares NO `context_refs` at all**, so
the delivered-context half of the manifest is never exercised in the first place. The attack passed
through a hole rather than being caught.

**Required:** declare at least one real `context_refs` entry on a gate in the control's plan, so that
a manifest with resolvable rows is actually produced and compared. Then confirm A3's condition is
**reachable**: with those declared refs pointing at missing files, show what the control does and
assert it deliberately — whether that is red, or a documented "this field is still correct because it
pins bytes, and here is what separately covers the row contents."

**A fixture that cannot reach the failing condition is as vacuous as a predicate that cannot
discriminate.** Right now this one cannot reach it.

## Explicitly OUT of scope

- **Do not re-cut the control.** Its verb sequence, both-topology design, ground-truth model, four
  in-suite red-proofs, and retrieval/canon tests all stand.
- **`advance --mechanical` is RULED CORRECT and upheld on review** — confirmed at the world (`advance`
  with neither flag exits 1) and empirically by M1 itself, where maximal agent prose moved **not one**
  mechanical field. Do not change it to `--why`. Do not re-litigate it.
- **Do not fix #379** (the `role`/`refusals` honest null). Reported, filed, deliberately unfixed.
- `run.dirty`/#327 and the #300 successor line are **g4's**. Do not touch them.
- Do not change the seam, `reopens` shape B, or `refusals` semantics.
- Do not modify any file under `scripts/` **except temporarily for a red-proof**, restored and
  verified by blob OID.

## Constraints

- **Verify every mutation actually applied before trusting its red OR its green** — compare
  `git hash-object <path>` against `git rev-parse HEAD:<path>`. A mutation that silently fails to
  apply yields a meaningless green. **This happened in this gate already** (costume #4 of #337).
- Restore every mutation; prove restoration by blob OID; `git status --porcelain` empty.
- Blob OIDs or normalized content, never raw working-tree bytes (#319).
- `python -m pytest`, never `py -m pytest`. `py` produces **no output and no exit code** under the
  PowerShell tool — use Bash for `py`.
- Windows: explicit `encoding='utf-8', newline='\n'` on writes. `Path.read_text(newline=...)` is
  3.13+ and breaks CI's 3.12 pin.
- Editing `scripts/checklist_engine.py` may be blocked by a safety classifier. Do not fight it — an
  in-process monkeypatch or a `sitecustomize.py` on `PYTHONPATH` achieves the same mutation
  non-destructively. Worked example: `.agent-work/issue-305/evidence/g3_return_item_4_callsite_sever.md`.
- **Repairing a vacuous check does not retroactively support conclusions that rested on it.** For each
  guard you fix, state what *else* carries the conclusions that guard was supposed to support.

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

## MUTATIONS ALREADY SPENT — nine now. Do not repeat one.

| # | who | mutation | outcome |
|---|---|---|---|
| R1 | implementer | `mechanical_fields` → ten constants | caught, all ten |
| R2 | implementer | `failed_command_count` → `0` | caught, `['failed-commands']` |
| R3 | implementer | `_lease_role` → `"implementer"` on child | caught, `['role']` |
| R4 | implementer | `reopen_total` → `1` | caught, `['reopens']` |
| M-C | commander | `manifest_ref` revision → constant sha1 | caught, `['context-manifest-ref']` |
| M-D | commander | drop `artifact-ref` | caught, `['artifact-ref']` |
| M-E | commander | sever the seam at its call site | caught (control RED) |
| **M1** | reviewer | `--mechanical` → `--why <prose>` + `--note` on attests | **NOT caught — FIX 1** |
| **M5** | reviewer | oracle reads tallies from the composer | **NOT caught — FIX 2** |

Your red-proofs for FIX 1 and FIX 2 **are** M1 and M5 — reproducing them is the point, not a repeat.

## Required Evidence

**Load-bearing — prove rigorously:**
1. FIX 1's guard goes **RED under M1**, and green after restore. Show the assertion text.
2. FIX 2's guard goes **RED under M5**, and green after restore. Show the assertion text.
3. FIX 3: a manifest with **resolvable declared rows** is actually produced (paste it), and A3's
   condition is demonstrably **reachable** — with your deliberate assertion about what happens.
4. Blob-OID restoration proof for every mutation; `git status --porcelain` empty.
5. Full suite. Prior was **1485 passed / 2 skipped / 472 subtests**; account for every moved number.

**Confirmatory — spot-check:**
6. The other 11 tests still pass unchanged.
7. For each fixed guard, one line on what else carries the conclusions it had been propping up.

## Verification Commands

```bash
cd "C:/Programs/constellation-skills-wt/e298-305"
python -m pytest tests/test_episode_negative_control.py -v
python -m pytest -q
git status --porcelain
git hash-object scripts/episode_capture.py
git rev-parse HEAD:scripts/episode_capture.py   # must match; 8a38e33d... at handoff time
```

## Suggested Model Tier
**Opus** — epic budget floor, not downgradable. No Fable at any tier.

## Authority

**Settled, do not reopen:** `--mechanical` satisfies "records nothing" (upheld on review); the seam's
placement; `reopens` shape B; `refusals` as documentation-only (#367); mechanical snapshot **not**
auto-created episodes; refuse-never-fabricate; throwaway consolidation; #379 stays unfixed.

**Yours to decide:** the shape of each of the three fixes, and whether FIX 2 uses approach (a) or (b).

**Not yours:** anything that changes what the control concludes, as opposed to how honestly it
verifies its own setup.

## Stop Conditions

Stop and return if: a fix would require re-cutting the control; a guard cannot be made falsifiable and
you can say precisely why; allowed scope must be exceeded; a decision outside the above is needed; or
**you discover a THIRD vacuous guard** — report it rather than quietly fixing beyond this scope.

## Return Format

Return **IMPLEMENTER_RESULT**: what changed per fix, the M1/M5 red-proofs with their assertion text,
restoration proof, suite numbers with the delta accounted for, assumptions, stop conditions hit,
out-of-scope observations, and **Workflow Feedback** — blunt.

**Deliver your IMPLEMENTER_RESULT to `commander-305d` via `SendMessage` before ending your turn.**
