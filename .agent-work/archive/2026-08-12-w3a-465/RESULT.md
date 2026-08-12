# RESULT — dispatch w3a-465, issue #465

**PR: https://github.com/fredcai6/constellation-skills/pull/492** (branch `epic-418/w3a-465`,
commit `6774e75e`). Reviewer verdict **APPROVE**, no blockers.

## 1. Verdict

- **Placeholder: the affordance was added and the imperative now names it.** `amend`'s existing
  `retext-check` op runs on a survey, where it is the *only* permitted op. `add`/`drop`/`rescope`
  stay gated-only, and the refusal says that is a conservative choice, not a type-level
  impossibility.
- **`SKILL.md` contradiction: the prose moved.** `consolidate()` is untouched. The sentence now
  names both honest exits — BLOCK, or APPROVE with `--override-reason` — plus an explicit "never
  downgrade a fail to pass."

## 2. The evidence that decided each

**Placeholder.** The launch order's rule: if nothing reads the filled value, removal is honest; if
something reads it, the verb is required. Something reads it, and not passively — `record()` in
`scripts/checklist_engine.py` evaluates `command`-kind postconditions before it will accept `pass`,
so the check string is *executed* on the reviewer's own `record --result pass`. The two captured
refusals, at `.agent-work/w3a-465/red/amend-refusal.txt`:

```
REFUSED: amend applies to gated checklists
amend exit=1

REFUSED: r6-fowler: command postconditions unmet ['c1']; cannot record pass
  Recovery: fix the underlying issue so postcondition c1 passes, then retry
  record r6-fowler. Do not edit the JSON — use the engine.
record exit=1
```

The second refusal is the issue in one line: the engine tells the reviewer to use the engine, and
there is no verb. Removing the check instead would have moved an enforced invariant into the prose
bin, which the repo's own two-bin rule says enforces nothing.

**Prose contradiction.** `docs/CHECKLIST_SCHEMA.md` documents the override as deliberate — the guard
"is pure shape-checking — the engine is not judging quality, only refusing a verdict that contradicts
its own recorded findings. It kills the weak-reviewer failure mode." The affordance is intentional;
the sentence was wrong.

## 3. The red

On **win32**, the **LF** fixture is the discriminating one:

```
AssertionError: save() churned an LF file to CRLF (8 CRLF endings written)
```

The **CRLF** fixture *passed* against the same broken `save()` — on this platform it is exactly the
test that proves nothing, and the test file's docstring says so rather than hiding it. A negative
control shows the CRLF fixture catches a different broken world: an "always write LF"
over-correction. The reviewer reproduced both independently, reverting only `save()` to its HEAD
text-mode form and verifying that revert byte-identical to the HEAD blob.

Three shapes that cannot fail were named up front and avoided: an LF fixture built with `write_text`
(born CRLF on Windows, so the discriminating test silently degenerates into the vacuous one);
assertions on `read_text()` (universal newlines make them vacuously true); asserting saved bytes
equal fixture bytes (`indent=2` re-serialises, so it fails for the wrong reason and gets loosened).

## 4. Test command and real exit code

`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` → **1786 passed, 2 skipped, 682 subtests, exit 0**
(redirected, not piped). The reviewer's independent run matched exactly.

## 5. Isolation proof

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/wt-w3a-465
worktree OK: in C:/Programs/wt-w3a-465
EXIT=0
```

## 6. Floated to the Admiral

- **The affordance path was taken**, as the launch order requires me to say. It is not a new verb —
  one existing op's type guard was relaxed — but it is still a change to a shared interface.
- **A fence was extended, deliberately.** `docs/CHECKLIST_SCHEMA.md` and
  `skills/workbench/references/checklist-engine.md` were not in my fence. The implementer found five
  statements there asserting `amend` is gated-only, which this change made false. I ruled to fix them
  rather than defer: shipping a fix that opens five new prose/affordance gaps is this issue's own
  defect with my name on it. Neither file is owned by a concurrent sibling.
- **The cold critic caught that my own integrate gate could not fail** — its check was
  `pytest -q tests`, green on a suite that never gained the new tests. It now names the four test node
  ids. The wave's organizing lesson reproduced *inside* the dispatch sent to apply it.

## 7. Triage candidates

1. `skills/interrogator/templates/INTERROGATION.template.json` `zc-consolidate` carries the identical
   placeholder defect word for word, and the identical open-fail prose claim. Its template is
   `type: "survey"`, so this change already supplies the engine half — only its prose remains.
2. The engine journal append (`checklist_engine.py`, `jp.open("a", encoding="utf-8")`) is still
   text-mode — same defect class as `save()`, deliberately fenced out.
3. Six repo JSON writers pass `encoding` but not `newline`, against CREW_CONTEXT's own rule:
   `collect_feedback.py:290,365`, `install_constellation.py:911,1182,1241`,
   `build_architecture_map.py:385`.
4. CREW_CONTEXT's always-pass-newline rule now has an unnamed exception in `save()`, which satisfies
   the rule's *intent* more strongly than its prescribed mechanism. Same prose-contradicts-code
   class, one tier up.
5. `amend()` is 215 lines. Fowler long-method, *flagged not overridden* — `global-crew.md`'s "split a
   unit when its intent blurs" agrees with the smell.
6. `amend`'s type applicability is restated in six places. The first implementer return shipped
   without the five prose sites; the structure guarantees recurrence.
7. The `{checklist_dir}` substitution road, named untaken in `plan-alternatives.md`. It would kill
   this defect class corpus-wide and is additive, but it does not fix the residual case that drives
   hand-editing.

## 8. Workflow feedback

- **My own handoff said `amend --op retext-check`. There is no `--op` flag** — ops live inside the
  `--delta` file. The implementer caught it and wrote the true shape into the shipped template rather
  than parroting mine. A Commander inventing CLI syntax for a verb it is simultaneously making
  authoritative is worth noticing.
- **`current` rejects `--session-id` while every mutating verb requires it.** Cost the reviewer two
  failed calls and me one.
- **Neither handoff named a home for scratch.** The implementer improvised `g1-implement/evidence/`,
  the reviewer improvised its own reproduction trees, and both flagged it independently. The reviewer
  skill separately warns about orphan untracked scratch at the worktree root, so the gap has a
  consequence.
- **My reviewer handoff's criterion 5 instructed an action doctrine forbids** — "inspect the
  `amendments` array" — when no engine verb prints it and reading checklist JSON directly is a
  documented violation. The reviewer routed around it honestly and said so. My error.
- **The implementer's suggested doctrine, which I endorse:** *a fixture that does not assert it was
  born in the defective state is the general shape of a test that cannot fail.* That states the
  wave's lesson as a test-side invariant instead of prose an implementer must hold. **Recorded as an
  observation, not promoted** — doctrine promotion is the human's call.
- **The plan template leaves the TDD red as a bare self-attestation** (`check: null`, correctly,
  since a command check would run the by-design-failing test). Its default should be: attest the red
  *and* name the file the output landed in.

## 9. Run state at handoff

The context governor HARD-tripped at the `g1-implement` seam of `execute.json`, exactly as the launch
order predicted. The work itself is **complete, committed, reviewed APPROVE, and pushed as PR #492**.
What remains is engine bookkeeping: advance `execute.json`'s three gates, then the spine's
reconcile → triage → review → feedback → archive. A refresh-request is attached at the seam;
`STATE_NOTE.md` names the resume command.
