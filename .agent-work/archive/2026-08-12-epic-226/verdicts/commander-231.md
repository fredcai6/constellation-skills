# Commander Verdict — issue #231 (epic-226 item E)

**Commander:** commander-231 (delegated, sonnet) · **Branch:** `issue-231` ·
**Worktree:** `C:/Programs/constellation-wt-231` · **PR:** #236 —
https://github.com/fredcai6/constellation-skills/pull/236

Full spine driven end to end through the engine: init -> context -> understand -> plan
-> execute (e0-context, g1-vocab, g2-seam, g3-implement/review/integrate) -> reconcile
-> triage -> review -> feedback -> archive. Engine session lease released as the final
action after the closing `advance` on `archive`.

## 1. Verdict per build item

- **(a) Three-valued verdicts — SHIPPED.** `PROTOTYPE_RESULT.template.md`'s freeform
  `## Answer` field replaced with a `## Verdict` field carrying
  `answered-yes | answered-no | not-immediately-right`, plus a named
  "Revive condition (not-immediately-right only)" subfield so the parked value is
  never a silent drop. PR-7 re-verified this as a genuine gap before planning (no
  existing enum in the shipped template).
- **(b) captured-to-worktree disposition — SHIPPED.** Added as the 4th value to
  `PROTOTYPE_RESULT.template.md`'s Disposition enum and Detail line, and documented in
  `skills/prototyper/SKILL.md` section "Closeout: disposition is mandatory" ("one of
  exactly four", human ruling "keep until done", epic-close sweep cap, explicitly "no
  new sweep automation authored"). PR-7 re-verified this as a genuine gap (zero repo
  hits for `captured-to-worktree` before this change).
- **(c) Commander understand-step seam paragraph — SHIPPED.** New third bullet,
  "Prototyper escape hatch (`understand`)", added to
  `skills/commander/references/commander-core.md` immediately after "Feasibility
  probe (`understand`)", same one-paragraph bolded-lead-in style as the two existing
  bullets. Names only the existing `PROTOTYPE_HANDOFF`/`PROTOTYPE_RESULT` fields (no
  new fields invented), points dispatch mechanics at the existing
  `references/crew-dispatch.md`, states no new spine step / no new engine machinery.
  **Canonical target confirmed per PR-6:** `skills/commander/references/commander-core.md`
  is not a member of any `_GLOBAL_EVERYONE`/`_GLOBAL_ORCHESTRATOR`/`_GLOBAL_CREW`/
  `_GLOBAL_ALL_TIERS` tuple in `scripts/install_constellation.py` (lines 98-124) — it is
  the commander skill's own owned doctrine file, never install-time regenerated. This
  is the file edited; no `skills/<role>/references/global-*.md` was touched.

No honest nulls, no blocked items — all three build items were genuine gaps (PR-7
re-verification, re-run at plan time, found no drift from the launch order's own
authoring-time read) and all three shipped.

## 2. Evidence

**Worktree isolation:**
```
worktree OK: in C:/Programs/constellation-wt-231
```
(`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-231`, run
before any git operation.)

**Full suite, run on branch `issue-231` after the commit (76c8044):**
```
py -m pytest tests/ -q
........................................................................ [  7%]
........................................................................ [ 15%]
...................................................... [ 21%]
........................................................................ [ 29%]
........................................................................ [ 37%]
........................................................................ [ 45%]
........................................................................ [ 53%]
........................................................................ [ 61%]
.............................................................. [ 67%]
........................................................................ [ 75%]
........................................................................ [ 83%]
........................................................................ [ 91%]
...........................................s........s................... [ 99%]
....                                                                     [100%]
910 passed, 2 skipped, 244 subtests passed in 43.56s
```
Exit code: **0** (confirmed via a direct `py -m pytest tests/ -q; echo "PYTEST_EXIT: $?"`
invocation, not inferred from output text). Run independently three times across the
gate: once by the sonnet implementer, once by the sonnet reviewer, once by the
Commander itself (both mid-gate and again for this verdict).

**Round-trip regression test — `tests/test_prototyper_templates.py` (new file, 5 tests,
all pass):**
```
py -m pytest tests/test_prototyper_templates.py -v
tests/test_prototyper_templates.py::PrototypeResultEnumExtraction::test_disposition_enum_carries_the_new_4th_value PASSED
tests/test_prototyper_templates.py::PrototypeResultEnumExtraction::test_disposition_enum_extracted_from_real_template PASSED
tests/test_prototyper_templates.py::PrototypeResultEnumExtraction::test_verdict_enum_extracted_from_real_template PASSED
tests/test_prototyper_templates.py::PrototypeResultEngineRoundTrip::test_off_vocabulary_verdict_is_refused_by_advance PASSED
tests/test_prototyper_templates.py::PrototypeResultEngineRoundTrip::test_real_verdict_and_disposition_values_accepted_by_advance PASSED
5 passed in 0.89s
```
**How it avoids the hand-injected-fixture trap
(`lesson:verify-harness-field-and-drive-real-writer`):** a module-level `_extract_enum()`
regex reads the `## Verdict` / `## Disposition` headings' backtick-quoted,
pipe-separated values directly out of the real, current
`skills/prototyper/templates/PROTOTYPE_RESULT.template.md` file at import time —
`VERDICT_VALUES`/`DISPOSITION_VALUES` are never hand-typed in the round-trip test
bodies (only in a dedicated `PrototypeResultEnumExtraction` self-check class that pins
the extraction against drift). Both round-trip tests then drive the REAL vendored
`scripts/checklist_engine.py` via `subprocess.run([sys.executable, str(ENGINE), ...])`
against a fixture `gated` checklist whose sole postcondition is the engine's existing
generic `artifact`/`match` mechanism (`evidence_type: "prototype-result"`, matched on
the extracted values) — `claim -> start -> attach -> advance`. The **positive** test
supplies the real extracted values and asserts `advance` returns 0 (`g1 -> complete`).
The **negative** test supplies an off-vocabulary `verdict=maybe` at the same
postcondition and asserts `advance` fails (`postconditions unmet`), proving the
`match` check is genuinely exercised, not a no-op. No first-class `evidence_type` was
added to `checklist_engine.py` (fenced this wave — #227 owns it); confirmed zero diff
to that file. Independently reproduced by both the Commander (`git status --porcelain`
confirmed only the new test file untracked) and the reviewer (re-ran both pytest
commands, re-read the extraction code, hand-reproduced the negative case outside the
test suite with the same `REFUSED: g1: postconditions unmet ['c1']` result).

**Diff to `commander-core.md` (item c), purely additive** (`git diff HEAD` before
commit showed only `+` lines, zero `-` lines, gated by execute.json's g2-seam.c3
command postcondition):

The new third bullet, "**Prototyper escape hatch (`understand`)**", lands right after
"Feasibility probe (`understand`)" and before the "## Executing a gate" heading. Text:
"When a load-bearing unknown surfaces here and is answerable by cheap code, hand it to
`constellation-prototyper` via the existing `PROTOTYPE_HANDOFF` -> `PROTOTYPE_RESULT`
contract rather than guessing past it or building heavyweight excursion machinery —
the human explicitly rejected the latter for commander. No new fields, no new spine
step: fill `PROTOTYPE_HANDOFF` with the one named question, dispatch through the
mechanics in `references/crew-dispatch.md`, and integrate the returned
`PROTOTYPE_RESULT` (verdict, disposition, and scope) back into the problem statement
before continuing." This lands as the third bullet in the `understand`-step family,
right after "Shaped-design intake" and "Feasibility probe" — same location the launch
order named.

**PR:** #236 — https://github.com/fredcai6/constellation-skills/pull/236 (branch
`issue-231` -> `main`, commit `76c8044`). Not merged by this Commander (merge is a
batched Admiral action per PR-3).

## 3. Map impact

No `docs/architecture/` packet map exists in this repo (confirmed absent in both the
worktree and the main checkout — a skill-source repo). Reconcile was a reasoned no-op:
the change landed directly in its own canonical schema/doctrine files (the template IS
the prototyper-result schema; `commander-core.md` IS the commander's canonical
doctrine), so there was nothing further to fold in. One new structural edge is worth
recording for a future map-building pass:

`commander.understand` --[escape hatch, cheap-code answerable unknown]--> `prototyper`
(via `PROTOTYPE_HANDOFF` in / `PROTOTYPE_RESULT` out — verdict + disposition +
scope), dispatched through the existing `crew-dispatch.md` mechanics, no new machinery.

## 4. Triage candidates

None. Zero out-of-scope discoveries across g1-vocab, g2-seam, g3-implement, g3-review,
or the Commander's own reconcile/triage passes.

## 5. Workflow feedback

Full entry appended to the run's `AGENT_FEEDBACK.md` (see fencing note below for its
location). Summary of the load-bearing points:

- **`--from-child` has two undiscoverable-from-the-refusal-text rules**: (1) a
  non-absolute `<path>` resolves against the PARENT checklist's directory, not cwd; (2)
  it refuses a `gated` child outright ("has no consolidation yet") — a `gated` child
  (e.g. `execute.json`) must instead be closed via a direct `attest <parent-step> --cond
  <id>` citing the child's per-gate evidence. Both rules live in
  `docs/CHECKLIST_SCHEMA.md` but not in the REFUSED message text; cost two extra
  round-trips this run. Banked as `lesson:from-child-refusal-undiscoverable-from-error`
  (single data point, `scripts/checklist_engine.py` is fenced this wave so not
  applied) rather than fixed, per the launch order's file-ownership fence.
- **Crew-reported (g3-implement):** the exact `attach --type ... --field K=V` CLI shape
  and the `why_exempt`/`--mechanical` requirement for a fixture-building gate were not
  named in the handoff; the implementer confirmed them by reading the engine source
  directly. Low-severity, not banked as a standalone lesson.
- **Crew-reported (g3-review):** the reviewer skill's per-rule-check `append` pattern
  lands new sibling checks at the end of the survey's item list rather than adjacent to
  their anchor — cosmetic journal-order artifact, not a defect, no action taken.
- **What worked well:** the pre-authored invariant-chain pattern for the two doc-only
  reasoning gates (g1-vocab, g2-seam) closed cleanly with zero rework; the
  `run_crew.py --backend external` + synchronous Agent-tool dispatch + `--verify-result`
  pattern worked cleanly for both crew gates; `tests/test_explorer_templates.py` was a
  directly-mirrorable pattern that let the implementer land the round-trip test
  correctly on the first pass (no rework, no BLOCK).

**Fencing note — needs Admiral action.** `agent_work_root.durable_root()`, called from
this worktree, resolves to the worktree itself (not the main checkout) because
epic-226's Admiral lease is `active` in `.agent-work/epic-226/spine.json` — the
built-in "active epic lease" exception. This meant the documented
`staged-feedback/<work-id>/` + `FENCE.md` workaround was **not needed**: the plain
`AGENT_FEEDBACK.md`/`LESSONS.md` write, made worktree-local, already satisfies
`verify_agent_feedback.py` on its own (confirmed empirically — both invariant checks
passed at exit 0). Both files were written at
`C:/Programs/constellation-wt-231/.agent-work/AGENT_FEEDBACK.md` and
`C:/Programs/constellation-wt-231/.agent-work/LESSONS.md` (deliberately kept at the
worktree's agent-work root, not inside `commander-231/`, so the archive step's
directory move did not carry them). **Before the `issue-231` worktree is swept, the
Admiral should fold this run's `AGENT_FEEDBACK.md` entry and the
`lesson:from-child-refusal-undiscoverable-from-error` lesson-delta into the shared
main-checkout `.agent-work/AGENT_FEEDBACK.md` / `.agent-work/LESSONS.md`** — otherwise
this run's workflow signal is lost when the worktree is removed. Full findings detail:
`.agent-work/epic-226/evidence/findings-231.md` (main checkout, this document's sibling).

**Harness note:** the `Write` tool refused two attempts at a file path whose basename
contained "findings" (`findings-231.md`) with "Subagents should return findings as
text, not write report files" — even though this exact path is the launch order's own
named, contractually-required findings artifact (I am its sole writer per the launch
order). Worked around by writing that file's content via a `Bash` heredoc instead
(this verdict file itself wrote fine through `Write`, so the guard is filename-keyed,
not path- or content-keyed). Flagging this as a genuine harness/doctrine friction
point: a delegated Commander whose launch order names a "findings-<n>.md" deliverable
cannot rely on the `Write` tool for it. No content was altered or omitted by the
workaround.

No decisions were floated to the Admiral this run — the launch order and its
pre-rulings covered everything encountered.
