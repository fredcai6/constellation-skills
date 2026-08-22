# Reviewer Handoff: `w1-wiring` — clean-room review of the registration lint

You are an **independent reviewer**. You did not author this change and you have no authoring
context. Do not seek any. Everything you need is below.

**Read nothing the implementer wrote about why its work is correct.** Specifically: do NOT read
`.agent-work/w1-wiring/PLAN_CRITIC.md`, `PLAN_ALTERNATIVES.md`, `MISSION_FRAME.md`, `RESULT.md`, or
the commit messages' justifications. Read the **diff** and the **acceptance criteria**. The whole
point of this pass is that the change has, so far, only ever been judged by the agent that wrote it.

## Why you exist

This change was produced by a Commander that — through a dispatcher error, not its own fault — ran
with no independent review at any gate. Its plan-alternatives were self-authored, its "cold" plan
critic was itself, and its disposition gate had no reviewer. Every quality claim attached to this
work is currently the author's own assertion about the author's own work.

The change being reviewed is, with some irony, **a lint whose entire purpose is to stop checks that
cannot fail from shipping**. If it ships unreviewed on its own say-so, the epic it belongs to would
be citing it as evidence that its thesis works.

## What to review

**Repo:** `/home/tommy/projects/569-w1-wiring` (git worktree, branch `epic-569/w1-wiring`)
**Diff:** `git diff 244665ee..HEAD -- . ':!.agent-work'`
**Base:** `244665ee`

Primary files:
- `tests/test_check_script_registration.py` — the new `RegistrationLint` and `VocabularyRule`
- `tests/test_gauge_writer.py` — the new `GaugeRecordFieldTableReconciliation`
- `docs/CHECK_SCRIPT_CENSUS.md` — the census the lint's allowlist is justified by
- `docs/GAUGE_WRITER_HOOK.md` — a field-table fix
- `scripts/prove_docstring_only.py` — **deleted**
- `map/INDEX.md`, `tests/data/store_mentions.approved.txt` — incidental

## The two questions only you can answer

These are the failure modes a self-review structurally cannot catch. Spend your effort here.

### 1. Is every allowlist entry TRUE?

`RegistrationLint` requires every check-shaped script in `scripts/` to be wired into a real
`command` check, **or** to carry an allowlist entry with a stated reason. There are roughly 12
entries, each claiming a specific live path, e.g.:

- `"verify_skip_guard.py": "live via .github/workflows/ci.yml's Skip guard step, not a template check"`
- `"verify_coverage_ledger.py": "live via tests/test_verify_coverage_ledger.py::test_real_repo_ledger_passes, not a template command check"`
- `"verify_declared_dispatch.py": "live only on generate_spine.py's compiler path (MCP spine_open), not the template-instantiation path any shipped role uses"`

**Verify each claim against the repo. Do not take the reason string on trust — that string is the
author asserting the thing you are here to check.** For each entry ask: does the named caller exist,
does it actually invoke this script, and would it actually FAIL if the script's condition were
violated? A test that imports a script but asserts nothing about the real repo is not a live
enforcement path.

**Why this is the sharpest risk in the change:** a wrong allowlist entry silently exempts a script
from the lint forever, and produces exactly the defect the lint was built to prevent — something
that looks enforced and is not. One false entry is a genuine finding, not a nitpick.

### 2. Do the negative self-tests fail for the RIGHT reason?

Two tests claim to prove the rules can fail:
- `test_negative_self_test_catches_an_unregistered_synthetic_script`
- `test_negative_self_test_catches_a_synthetic_mechanically_enforced_claim`

Check that each fails **because the rule detected the planted defect**, not incidentally — a
fixture path error, an exception from the wrong layer, or an assertion that would pass on an
unrelated failure. A negative test that goes red for the wrong reason certifies nothing, and this
project has a filed issue about exactly that shape (#382: "independence guard defeated by an aliased
import").

Also check the mirror: could either rule ever fire on something legitimate? Both ship **blocking**,
so a false positive breaks the suite for an unrelated contributor.

## Secondary checks

- **The deletion.** `scripts/prove_docstring_only.py` is deleted as dead. Confirm nothing references
  it — including CI, hooks, other scripts, and prose that instructs an agent to run it.
- **`VocabularyRule` scope.** It bans "mechanically enforced" / bare "RAIL" claims outside the
  engine's own doctrine files. Check the exemption set is not so broad the rule is vacuous.
- **The `#444` doc fix.** `docs/GAUGE_WRITER_HOOK.md` gained an `owner` field. Confirm the doc now
  matches the code, rather than matching a different wrong thing.
- **Suite.** Author reports 3573 passed / 6 skipped, up from 3564 at base. Re-run and confirm.
  Note: CI here is **Windows-only and known-red**; ignore CI, the local run is the gate.

## Acceptance criteria

1. Every allowlist entry names a real, verified live enforcement path.
2. Both negative self-tests fail for the reason they claim.
3. Neither blocking rule can fire on legitimate current content.
4. The deleted script is genuinely unreferenced.
5. The local suite is green at the shipped revision.

## Out of scope — do not review these

- Whether the lint should ship **blocking or report-only.** That is an open question with the human
  and is not yours to settle. Report evidence bearing on it if you find any; do not rule on it.
- The `#368`/`#444` measurement counts, except where a count is load-bearing for a test's assertion.
- Anything in `scripts/checklist_engine.py` or `scripts/validate_spine.py` — a sibling commander owns
  those this wave and they are unchanged here.
- Epic-level scope, wave ordering, or the epic's premises.

## Verdict

Return one of `APPROVE`, `APPROVE-WITH-FOLLOWUPS`, or `BLOCK`, with findings.

**A `BLOCK` is a successful review, not a failure.** So is `APPROVE` if the work genuinely holds —
do not manufacture findings to look thorough. Given the review gap this pass exists to close, an
`APPROVE` that says plainly "I checked all 12 allowlist entries individually and here is what each
resolved to" is worth far more than a list of style observations.

Write your result to `/home/tommy/projects/569-w1-wiring/.agent-work/w1-wiring/REVIEW_RESULT-clean-room.md`.
