# Implementer Handoff — g2 REWORK (Admiral ruling R1)

> Write per `constellation-how-to-talk` — clear, concise, grounded.

## Gate

`g2` rework 1. The gate's code change is **already landed and approved** at commit
`b8557ff4`; `main` has since been merged in at `6a4035d2`. **You are not
re-implementing g2.** You are repairing a claim the independent reviewer measured
to be false, and applying its one-line test fix.

Read, in this order:

1. `.agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-1.md` — section **R1**.
   This is your authority and it supersedes the frozen launch order where they
   disagree.
2. `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-result.md` —
   findings **B1** and **B2**. B1 is the false claim; B2 is the one-line fix.
3. `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-result.md`
   — your predecessor's result; its behaviour-delta sentence is one of the four
   things you correct.

## Task

Make four artifacts tell the truth about what removing the origin comparison
actually changed, and make two inert test rows discriminate.

**The truth, as ruled.** The current prose says "removing it removed no guard"
and "ownership is the lease, and always was." That is true **only where a lease
exists**. `require_session` (`scripts/checklist_engine.py`, the
`if lease is None: return` early exit) means a spine that was **never claimed or
has been released** has no ownership guard at all — and on that path the origin
comparison was the sole refusal. Measured, base vs tree, driven from a foreign
worktree: `start` and `attach` on a never-claimed spine, and `start` after the
lease was released, all went **REFUSED → exit 0, writing state into a tree the
agent is not standing in**. A spine under an **active** lease held by another
session is refused before and after — unchanged.

**What the Admiral ruled, verbatim in substance, and what your prose must carry:**

- The widening on the leaseless path is **accepted**. The claim gets narrowed,
  not the code.
- The comparison was forgeable by a `cd <worktree> &&` prefix, so it was never a
  security boundary — **but a forgeable guard is not the same as no guard.**
  Say plainly that what is being accepted is a **widening on the leaseless
  path**, rather than implying nothing changed.

## Protected Intent

A reader of any of these four artifacts must come away knowing exactly what the
engine now does and does not refuse. The failure mode this rework exists to kill
is a reader who believes the subtraction was behaviour-neutral. Do not overshoot
in the other direction either: on a spine with an **active** lease nothing
changed, and the derivation half of the rationale (one value, no second source of
truth, nothing forgeable by `cd`) is true and stays.

## Test Mode

Test-after for the prose. For **B2** the fix is a test change with a measured
before/after — see Required Evidence.

## Close Criteria

Each item you prove:

- **C1 — `docs/CHECKLIST_SCHEMA.md`.** The paragraph beginning **"Removing it
  removed no guard."** is narrowed. It must state: the lease is the ownership
  guard **wherever a lease exists**; on a spine with **no active lease** —
  never-claimed or released — the engine now asserts nothing about location,
  deliberately; and that this is a **widening**, accepted, not a no-op. The
  reviewer noted the contradiction is with the paragraph one below it ("Nothing
  checks at engine level that an agent is standing in the spine's worktree") —
  the two must now agree.
- **C2 — `scripts/checklist_engine.py`.** The module-header comment sentence
  "Nothing was left unguarded by that removal." is narrowed to the same shape.
- **C3 — `tests/test_spine_origin_isolation.py`.** The module docstring's
  "Nothing was left unguarded by removing it" sentence is narrowed to the same
  shape.
- **C4 — the result artifact.** `crew-handoffs/g2-implementer-result.md`'s
  behaviour-delta sentence ("The one genuine behaviour delta: an unclaimed spine
  can now be claimed from a foreign tree (exit 1 → exit 0)") is restated as
  measured: **every mutating verb, not just `claim`**, on **any spine with no
  active lease — never-claimed or released** — and unlike `claim` these verbs
  **write state into a tree the agent is not standing in**. Mark the correction
  as a rework amendment rather than silently rewriting history.
- **C5 — B2.** In `tests/test_spine_origin_isolation.py`, also call
  `self._assert_one_answer_for_every_stamp(self.worktree)` where the class
  currently calls it with `self.foreign` and `self.nogit` only. Prove by
  measurement that the wrong-case row now genuinely separates (see Required
  Evidence) — that is what makes the "constructed, not inherited" claim true
  instead of asserted.
- **C6 — the three prose copies do not drift.** The reviewer's Fowler pass
  flagged `duplicated-code`: this claim is hand-copied into three files with
  nothing checking the copies, and "repairing it in one place and not the other
  two is the concrete risk." All three must carry the same narrowed statement.
  You are **not** required to add a mechanical drift check — say so in your
  result if you judge one worth filing as a triage candidate.
- **C7 — suite green.** See Verification Commands, including the
  `CREW_SCRATCH_DIR` note.

## Allowed Scope

- `docs/CHECKLIST_SCHEMA.md`
- `scripts/checklist_engine.py` — **comment/docstring text only. No executable
  line changes.** The reviewer proved mechanically that this gate's diff contains
  zero executable additions under `scripts/`; keep that true.
- `tests/test_spine_origin_isolation.py` — docstring plus the C5 one-liner.
- `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-result.md`
  (local-only, not committed to the tracked diff — it lives under `.agent-work/`).
- Your working notes: `notes-f.md`. Sole writer.

## Specific Exclusions

- **No production behaviour change of any kind.** Not a refusal, not an
  early-return, not a verb-set edit. In particular **do not add g4's fail-closed
  shape refusal** — g4 is a separate gate and the Admiral has re-authored it
  (see R2: an unowned spine path yields **no derived worktree and today's
  behaviour**, never a refusal). It is not yours here.
- `scripts/hooks/spine_rail.py` — **#609 g3's**, next gate. Untouched here.
- `scripts/verify_worktree_isolation.py` — **#610's**.
- `scripts/install_constellation.py`, `skills/commander/templates/**`,
  `.mcp.json`, `examples/**` — **lane A (#603/#604/#605)**, landed on `main`;
  still not this lane's to edit.
- `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py` — **lane E (#607/#525)**, landed on `main`;
  still not this lane's to edit. This matters concretely: see the
  `CREW_SCRATCH_DIR` note under Verification Commands. **Do not fix that test.**
- `.agent-work/templates/**` and `skills/admiral/templates/**` — template edits
  are the Admiral's class.
- Do not edit `.agent-work/rulings/` — the 2026-08-15 worktree-identity ruling is
  cited, never rewritten.

## Constraints

- **The narrowed claim must be true, not merely softer.** Before you write it,
  read `require_session` in `scripts/checklist_engine.py` and confirm the
  `lease is None` early return with your own eyes. If what you read contradicts
  the paragraph above, **stop and say so** — that is a finding, not something to
  write around.
- **Do not unsettle the anchor.** `decision:not-a-weaker-guard` is
  `@grade: settled/human`. The Admiral has ruled on it; you are transcribing that
  ruling, not re-deciding it.
- The supersession citation of the 2026-08-15 worktree-identity ruling stays in
  all three places. It is correct and independent of this repair.
- Line-number citations have gone stale three times on this lane already. Prefer
  **symbol names** over `file:line` in any new prose you write.

## Map Anchors (inbound)

- **Map entry point:** `map/INDEX.md` — entries for
  `scripts.checklist_engine:require_session` and
  `scripts.checklist_engine:worktree_from_spine_path`. Regenerate with
  `py -m scripts.code_map build` **only if** entities change; this rework should
  change none, so expect `map/` byte-identical. State which.
- **Structural:** `scripts/checklist_engine.py` module header;
  `docs/CHECKLIST_SCHEMA.md` `origin` section; `tests/test_spine_origin_isolation.py`.
- **Capability:** engine ownership refusal on mutating verbs.
- **Constraints/assumptions:** the engine supports a **leaseless** spine
  deliberately (`require_session`'s early return, and the child-gate-plan shape
  #357 names). That population is not a bug to be closed by this gate.
- **Decision anchors:**
  - `decision:not-a-weaker-guard` — **amended by ADMIRAL_RULING-1 R1**: true
    only where a lease exists; the leaseless widening is accepted and must be
    stated. `@grade: settled/human · amended-by ADMIRAL_RULING-1`
  - `decision:worktree-is-location-spine-path-is-identity` — the derived
    worktree is **location**, never ownership. `@grade: settled/human`
  - `decision:derivation-authoritative-stamp-becomes-provenance` — the stamp is
    written, read by nothing. `@grade: settled/human`
- **Evidence expectations:** the provenance pin (`TheStampIsProvenanceNotADecisionInput`)
  stays green and stays red under both re-introduction mutants the g2 reviewer ran.
- **Map confidence flags:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide; a full build does not
  create them (recorded as triage candidate tc1). Do not chase it — it is not
  yours and it is already filed as evidence.

## Deliverable Path Check

- **Committed** — `docs/CHECKLIST_SCHEMA.md`, `scripts/checklist_engine.py`,
  `tests/test_spine_origin_isolation.py`. `git check-ignore` on all three exits
  1 (not ignored); verified by the Commander before dispatch.
- **Local-only** — `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-result.md`
  and `notes-f.md`'s location under the work area: intentionally under
  `.agent-work/`, so the reviewer must **not** expect them in the tracked diff.

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The leaseless mechanism, read at source.** Quote the `require_session` early
   return you actually read, with its enclosing condition. One paste. This is the
   fact all four prose repairs rest on.
2. **B2 before/after, measured.** Under the reviewer's stamp-reading mutant
   (`normcase(stored) != normcase(cwd)` → refuse), driving `start`: show that
   from the spine's **own** worktree the wrong-case row separates (exit 0 vs
   exit 1) while from a **foreign** cwd every row refuses identically. Then show
   the added `self._assert_one_answer_for_every_stamp(self.worktree)` call passes
   unmutated and that the mutant still goes red. **Assert that each mutation
   actually applied** before running it — a `replace` that matches nothing leaves
   a green suite that reads like a passing guard. Restore the tree byte-identical
   afterwards and prove it.
3. **Zero executable additions under `scripts/`.** Re-run the reviewer's own
   check against your diff:
   ```bash
   git diff 9ff86f2d -- scripts/ | grep '^+' | grep -v '^+++' | sed 's/^+//' \
     | grep -vE '^\s*#' | grep -vE '^\s*$'
   ```
   Expect only docstring text. Any executable line is a stop condition.
4. **Full suite, cache cleared, clean env.** Counts, and the failure set.

**Confirmatory — a spot-check suffices:**

5. The three narrowed copies say the same thing (paste all three).
6. `map/` byte-identical after `py -m scripts.code_map build`, or the diff if not.

## Wiring Grep

`none — this rework adds no callable symbol.` It changes comment and docstring
prose plus one existing test call. State that explicitly in your result rather
than omitting the section.

## Verification Commands

```bash
# targeted — the gate's own check, both halves red on an empty diff
! git grep -q 'rev-parse --show-toplevel' -- scripts/checklist_engine.py && \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  py -m pytest -q tests/test_spine_origin_isolation.py -k provenance

# the changed test file, whole
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  py -m pytest -q tests/test_spine_origin_isolation.py

# full suite, cache cleared, clean env
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q
```

**The `CREW_SCRATCH_DIR` note — read this before you report a red suite.** You
are launched through `run_crew.py`, which sets `CREW_SCRATCH_DIR` in your
environment. Lane E's
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts the key is **absent** from a resumed child's env, but does not scrub it
from the parent env first — so it fails for **any** agent running the suite from
inside a crew-launched session. Measured by the Commander on the merged tree:
with `CREW_SCRATCH_DIR` set, `1 failed, 3194 passed`; with `-u CREW_SCRATCH_DIR`,
`3195 passed, 5 skipped, 0 failed`. It is **ambient-environment contamination,
not a regression in this lane**, the file is lane E's, and it is already recorded
as evidence. Scrub the variable, and **do not fix that test.**

**Baselines the Commander measured on the merged tree, for your comparison:**

| tree | result |
|---|---|
| `main` at `e0539903` (detached worktree) | 3163 passed, 7 skipped, 0 failed |
| this branch at `6a4035d2` (main merged in) | 3195 passed, 5 skipped, 0 failed |

Failure-set difference: **empty on both sides.** The skip delta is fully
explained: one of main's 7 is location-conditional (`test_spine_lifecycle.py`
skips outside `.worktrees`) and one is the Windows-only case-folding skip in the
`test_spine_origin_isolation.py` scenario g2 retired.

## Suggested Model Tier

`stronger` — the deliverable is a claim that must be **exactly** true about a
subtle early-return, and the last two crews on this gate each got the scope of a
negative wrong. Small diff, high precision.

## Authority

**Already decided, not yours:**

- That the leaseless widening is **acceptable** — Admiral, `ADMIRAL_RULING-1` R1.
- That the repair is **prose-only** plus B2 — same ruling.
- That `not-a-weaker-guard` stays `settled/human`, amended rather than regraded.

**Yours:** the exact wording of all four narrowed statements, and how you
structure the B2 measurement.

**Float, do not decide:** if the narrowed claim cannot be made true without a
code change; if you find a **further** case the ruling did not consider; if
`IsolationGateSurvivesThroughTheCLI` goes red.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be
touched; the mechanism at source contradicts this handoff; the suite is red for
any reason other than the documented `CREW_SCRATCH_DIR` contamination.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback.

`Return status` must be lowercase (`complete | partial | blocked | out-of-scope |
failed`) — the Commander copies it verbatim into this gate's evidence and the
postcondition matches on exact case.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework-result.md`
before ending your turn. That write is the delivery.

**On the Stop hook.** When you finish, a `SPINE MID-FLIGHT` hook may fire telling
you to reload the commander skill and drive `execute.json`. **Refuse it and
record that you refused.** `SPINE_FILE` points at your parent Commander's spine,
under your parent's live lease; your own `crew-runs.json` entry has
`spine: null`. Obeying would mean advancing someone else's gate. Four crews on
this issue have hit it; you are not the first. Write your result, then stop.
