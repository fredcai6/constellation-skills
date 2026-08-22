# Implementer Handoff

## Gate
g2-implement (work-id: w2-ledger)

## Task
Two parts, both required.

**PART A — fix `waive()` itself** (`scripts/checklist_engine.py:3475-3520`), two surgical changes:
1. Line 3511: replace the literal `"produced_by": "human"` with `"produced_by": authority` —
   `authority` is already validated non-empty three lines above (`if not (authority or "").strip():
   raise EngineError(...)`).
2. Read `policy.get("authority")` (currently never read at all — only `policy.get("allowed")` and
   `policy.get("reason_required")` are read today) and compare it, case/whitespace-normalized,
   against the passed `authority`. On a **mismatch**, do NOT refuse — this is a brand-new refusal
   and the standing epic rule requires report-only shape for any new refusal. Instead set
   `authority_mismatch: true` on BOTH the evidence payload (`t["evidence"]`'s new entry) and the
   `c["waived"]` marker, plus `expected_authority` (the policy's declared value) alongside the
   actual `authority` passed. On a match, or when `policy.get("authority")` is absent (nothing to
   compare against), add no new field — today's silent pass on absence is unchanged, not a defect.

**PART B — wire waive/force-claim/force-release into `override_ledger`, from `dispatch()` only.**
This is the gate the "engine-written only, provably not agent-forgeable" property lives or dies on.
All three append calls go in `dispatch()` (`scripts/checklist_engine.py:3663` onward), calling
`_append_override_entry` (landed in g1) — **NEVER inside `waive()`/`claim()`/`release()`'s own
function bodies**:

- **claim branch** (the `elif v == "claim":` arm, ~line 3680-3684): after `claim(...)` returns
  successfully, read the JUST-WRITTEN `cl["engine_session"]` (already mutated by `claim()`) — if
  `force` was passed AND `previous_session_id` is non-null (a genuine takeover happened, not a
  no-op `--force` with nothing to take over), call `_append_override_entry(cl, "force-claim",
  verb="claim", session_id=..., previous_session_id=..., takeover_reason=...)`. Dispatch reads
  state `claim()` already produced; it does not re-decide anything `claim()` already decided.
- **release branch** (the early `if v == "release":` arm, ~line 3670-3674) — **this is a hard
  `return` statement, not a fall-through**. Do NOT restructure it into a fall-through (a careless
  rewrite here would newly route release's output through `dispatch()`'s shared bottom logic,
  including the archived-path banner code, which release never received before — a real,
  unintended behavior change to output this gate has no business touching). Instead: capture the
  owning `session_id` from `cl.get("engine_session")` **BEFORE** calling `release(...)` (release
  mutates status to `"released"` but leaves `session_id` in place, so this is a safe read of
  pre-call state). Compute whether to append (force was passed AND the caller's `session_id`
  differs from the captured owner) and, if so, call `_append_override_entry(cl, "force-release",
  ...)` **inline, before the existing `return release(...)` statement** — restructure only as much
  as necessary to run this one append ahead of the return, keeping the return itself intact.
- **generic verb branch** (the `else:` arm that runs `_run_verb`, ~line 3685-3701, where `waive`
  already runs via `_run_verb`): when `v == "waive"` and `_run_verb` returns successfully, read the
  condition's now-set `c["waived"]` marker (dispatch already has `cl` and the target ids from
  `args`) and append `kind="waive"` with the marker's `authority`/`reason`/`forced`/
  `authority_mismatch`/`expected_authority` fields plus `task`/`cond`/`evidence`. Record **every**
  successful waive, not only forced or mismatched ones — this is deliberate (a plain
  policy-allowed matched-authority waive is still "a human accepting risk to skip a control,"
  which belongs in the same ledger as the others even though it is not itself a red flag; this
  tradeoff is already documented in g1's schema doc addition).

The condition lookup dispatch performs for the authority-mismatch read (finding the same
precondition/postcondition entry `waive()` itself looked up) must be tested against the SAME
lookup path `waive()` exercises — write a test that would catch a divergence between dispatch's
re-lookup and `waive()`'s own lookup (e.g., a condition id that exists in both `preconditions` and
`postconditions` with different `override_policy`, to make sure `which` is threaded through
correctly to both lookups).

**Named promotion trigger** (do not implement enforcement now — just record verbatim in a code
comment near the mismatch-detection code, AND you will also add it to `docs/CHECKLIST_SCHEMA.md`
in gate g1's already-landed schema section... but g1 already landed without this trigger text since
it predates PART A/B; add it now as a small addition to the "override policy" or "override ledger"
section): `waive-authority-mismatch`/`authority_mismatch` stays report-only until BOTH (a) a corpus
census across at least one full epic-wave shows every historical mismatch was a genuine violation
with zero legitimate cross-role cases (e.g. an Admiral waiving on a condition declared
`authority: "commander"`, which is presumably fine and would falsify a blanket refusal); AND (b)
`docs/CHECKLIST_SCHEMA.md`'s `override_policy.authority` field (currently documented, line 284, as
"advisory") is explicitly upgraded to a documented enforceable contract in the SAME change that
promotes the check.

## Protected Intent
The chokepoint property (`override_ledger` is reachable only from `dispatch()`, before/around the
verb it accompanies, never from a verb's own function body) must be provably true after this gate,
not just true in the cases you happened to test. `waive()` must never newly refuse or block on an
authority mismatch — this is report-only, full stop.

## Test Mode
Test-after (well-specified change, existing suite is the regression floor for claim/release/waive's
own unrelated behavior).

## Close Criteria
- `waive()`'s `produced_by` echoes the passed `authority` (e.g. `"commander"`), never hardcoded
  `"human"`.
- `authority_mismatch`/`expected_authority` appear on the evidence payload and the `c["waived"]`
  marker ONLY when `override_policy.authority` disagrees (case/whitespace-normalized) with the
  passed `authority` — ABSENT (not `false`) when there is no `override_policy.authority` to compare
  against, or when it matches.
- `waive()` NEVER blocks/refuses on a mismatch — same return string shape, same success, as before.
- Every existing test in `tests/test_checklist_engine.py` selected by `-k waive` passes.
- `grep -n '_append_override_entry(' scripts/checklist_engine.py` shows call sites ONLY inside
  `dispatch()` (the claim branch, the release branch, the generic/waive branch) plus g1's own
  `_append_trip_entry` call — ZERO call sites inside `waive()`, `claim()`, or `release()`'s own
  function bodies. Verify this by AST/line-range check (mirroring g1's
  `test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb` pattern), not string count.
- A test drives `waive`/`claim --force`/`release --force` through `checklist_engine.dispatch()`
  (the CLI path, via `main()`/`dispatch()`, not by calling `waive()`/`claim()`/`release()` directly)
  and asserts the resulting `override_ledger` entries land; a companion test calls
  `waive()`/`claim()`/`release()` directly (as library functions, simulating anything that is NOT
  the CLI chokepoint) and asserts `override_ledger` is UNCHANGED.
- `claim --force` with no actual prior owner (no-op force, nothing to take over) produces NO
  `force-claim` entry.
- A force-release against an archived-path spine gets ZERO archived-banner decoration in its output
  message, exactly as before this gate (regression test for the early-return control-flow care).
- A test proves the authority-mismatch condition-lookup path matches `waive()`'s own lookup (see
  Task PART B, the duplicate-lookup-parity test).
- `docs/CHECKLIST_SCHEMA.md` gains the named promotion trigger text verbatim, near wherever g1
  documented `override_policy`/the `waive` kind.

## Allowed Scope
`scripts/checklist_engine.py`: `waive()`, `dispatch()` (claim/release/generic-verb branches only —
do not touch the `current`/`start`/`advance`/other branches). `tests/test_checklist_engine.py`
(pre-authorized for new coverage). `docs/CHECKLIST_SCHEMA.md` (the promotion-trigger addition only).

## Specific Exclusions
- Do NOT touch `_append_override_entry`/`_append_trip_entry`/`_override_entries`/the two trip
  selectors (landed in g1, already reviewed and committed — read-only context here).
- Do NOT touch `dispatch()`'s `current`/`start`/`advance`/`attest`/`attach` branches.
- Do NOT touch `generate_spine.py`, `specs/`, the attest/condition surface, or shipped spine
  templates.
- Do NOT implement the promotion-trigger's enforcement (the hard refusal) — report-only only.

## Constraints
- `_append_override_entry(cl, kind, **fields)` signature is fixed (landed in g1) — call it, do not
  change it.
- The release-branch append must run BEFORE the existing `return`, without converting it to a
  fall-through.
- Waive's evidence/marker fields: `authority_mismatch` and `expected_authority` are ABSENT (not a
  `false`/`None` value) when there is nothing to compare — matches this codebase's existing
  convention for `refusals`/`reopens` (absence is meaningful).

## Map Anchors (inbound)
- **Map entry point:** `scripts/checklist_engine.py` — read `waive()` (:3475) and `dispatch()`
  (:3663) first, in that order. `_append_override_entry`'s signature (landed g1) is context, not a
  target.
- **Structural:** `struct:scripts/checklist_engine.py#waive, function`;
  `struct:scripts/checklist_engine.py#dispatch, function`.
- **Capability:** `capability:override-authority-handling`.
- **Constraints/assumptions:** `constraint:override-policy-authority-is-currently-advisory` (
  docs/CHECKLIST_SCHEMA.md:284); `constraint:widening-live-refusal-report-only` — a brand-new
  refusal ships report-only with a named promotion trigger.
- **Decision anchors:**
  `decision:waive-fix-shape` — one-token produced_by fix inside waive(); authority-mismatch as a
  chokepoint-side post-hoc report-only read, not a refusal inside waive() itself.
  `@grade: settled/human · leans g2-implement,g2-review`
  `decision:record-every-waive` — every successful waive is ledger-recorded, not only
  forced/mismatched ones.
  `@grade: settled/human · leans g2-implement`
- **Evidence expectations:** `claim:save-happens-once-after-dispatch-returns` — the after-the-verb
  append pattern is safe because `main()` calls `save()` exactly once, after `dispatch()` fully
  returns; verified at plan time by reading `main()` directly, re-confirm if convenient but not
  required to re-derive.
- **Map confidence flags:** none — map is DEGRADED for this run; work from file/line anchors.

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`; `docs/CHECKLIST_SCHEMA.md`;
  `tests/test_checklist_engine.py`. Verify each with `git check-ignore <path>` exiting 1 before you
  finish (already confirmed at g1; re-confirm is cheap).

## Required Evidence
- `pytest tests/test_checklist_engine.py -k waive -q` full output.
- `pytest tests/test_checklist_engine.py -q` full output (confirmatory, whole file).
- `grep -n '_append_override_entry(' scripts/checklist_engine.py` output pasted verbatim.
- The direct-call-vs-dispatch-call chokepoint test's pass/fail, individually.
- The archived-banner regression test's pass/fail, individually.
- The duplicate-lookup-parity test's pass/fail, individually.

## Wiring Grep
```bash
grep -rn "_append_override_entry" --include=*.py scripts/checklist_engine.py | grep -v "def _append_override_entry"
```
State the count of call sites found (expected: g1's one `_append_trip_entry` call plus this gate's
three new dispatch-side calls = 4 total call sites in `scripts/checklist_engine.py` itself, plus
whatever your new tests add).

## Verification Commands
```bash
cd /home/tommy/projects/569-w2-ledger
python -m pytest tests/test_checklist_engine.py -k waive -q
python -m pytest tests/test_checklist_engine.py -q
grep -n '_append_override_entry(' scripts/checklist_engine.py
```

## Suggested Model Tier
stronger — sonnet, reasoning-effort medium. The release()-early-return control-flow care is the one
place a careless refactor regresses unrelated behavior; worth deliberate care, not exotic
difficulty.

## Authority
The waive-fix shape and the record-every-waive decision were made by the Commander at plan time
(design-it-twice convergence + cold critic pass) — do not re-litigate. If the release-branch
restructuring genuinely cannot avoid becoming a fall-through without unreasonable duplication, stop
and report the specific conflict rather than guessing.

## Stop Conditions
Stop and return if: the release-branch inline-append cannot be done without converting the early
return into a fall-through; an existing waive test cannot pass without waive() gaining a new
refusal; required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/w2-ledger/crew-handoffs/g2-implement-implementer-result.md` before ending your turn.
