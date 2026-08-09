# Implementer Handoff — g8 remediation

## Gate
`g8` — two code defects (issue #456). **Rework pass.** Defect 1 (BOM) is done and stays. Defect 2 (D3) is not fixed.

## Plan state
`.agent-work/issue-456/g8-remediate/plan.json`.

## First: you were right, and the fault was mine

Your result said the docstring defect was underspecified and that you "defaulted to a defensive fix (consistency) that is sound but may not address the actual defect." That was an accurate and useful thing to write, and it is exactly what a crew should do when a brief is vague instead of guessing quietly.

You were right. I checked. `D3` is **named but never defined** anywhere in the reference material — not in `DESIGN_SPEC.md`, not in `ISSUE_456.md`. Both say only "wrapped-docstring render split (D3)". My brief passed that phrase straight through without resolving it, which is my error, not a gap in your work.

I have now resolved it empirically. Here is the defect, precisely.

## THE DEFECT — what D3 actually is

A docstring's **summary is taken as the first physical line**. When an author wraps the summary sentence across two lines — which authors do constantly — the sentence is **cut in half**: the first physical line becomes the summary, and the remainder of that same sentence becomes the opening of the body.

Reproduced directly, on the current committed tree at `d727ee2f`:

```
SUMMARY as stored : 'This summary sentence is deliberately long enough that an author'
BODY as stored    : 'would wrap it across two physical lines, as authors constantly do.\n\nArgs:\n ...'
```

That is the split. A page renders a summary that stops mid-clause and a body that opens with a sentence fragment.

Your change — `split("\n")` → `splitlines()` — is a genuine consistency improvement and I am keeping it, but both forms still take `[1:]`, so both still cut at the first **newline**. The defect is untouched by it.

**The correct rule:** the summary is the text up to the first **blank line**, not the first newline. That is PEP 257's own convention — a multi-line docstring is a summary paragraph, a blank line, then the body. A wrapped summary spans several physical lines and ends at the blank line.

## What to build

Three sites, all in `scripts/code_map/extract.py`:

- **`doc_body_of`** (~line 268). Currently `"\n".join(doc.strip().splitlines()[1:])`. Must return everything after the first blank line, or `None` when there is no blank line (a docstring that is only a summary, however many lines it wraps to, has no body).
- **The module summary site** (~line 778): `doc.strip().splitlines()[0][:160]`.
- **The class/function summary site** (~line 888, and check ~line 919 too): same shape.

Each summary site must take the first **paragraph**, not the first line, then collapse its internal newlines to single spaces so it renders as one flowing sentence. Keep the existing `[:160]` truncation, applied after the join.

Three sites repeating the same rule is a duplication risk — factor the paragraph split into one small helper and call it from all of them, so the summary and body sides can never drift apart again. That drift is precisely what produced this defect.

**Watch the boundary cases** and cover each with a test:
- A one-line docstring — summary is that line, body is `None`.
- A wrapped summary with **no** blank line and no body — the whole thing is the summary, body `None`. Do not leave the wrapped remainder in the body.
- A wrapped summary followed by a blank line and an `Args:` block — summary is the joined sentence, body starts at `Args:`.
- A docstring whose first paragraph exceeds 160 characters — truncation still applies, after joining.

## Evidence required

1. **Reproduce the defect before fixing it.** Run the demonstration above (or your own equivalent) on the current tree, observe the mid-sentence cut, and record it. Then fix, and show the same input producing a whole summary and a body starting at `Args:`. Red before green, observed — not inferred.
2. **Break the fix and confirm the tests go red.** Revert the paragraph split to a line split and report how many tests fail. Any test that stays green is a test that was not testing this.
3. Closing selector `-k 'bom or docstring'` before and after. Currently **6 passing**.
4. **THE FULL SUITE — this is the one you missed.** Not `tests/test_code_map.py` alone. The command is exactly:
   `python -m pytest tests/ -q --color=no`
   Baseline is **1831 passed, 2 skipped, 697 subtests, 0 failed**. Your 141 was `test_code_map.py` only, which is why the numbers looked incompatible — you were right that the scopes differed, and right to say so rather than reconcile them by guessing. This gate carries an explicit full-suite constraint (critic F6), so it has to be the whole thing. It takes 7–11 minutes: background it and poll.
5. Fresh `python -m scripts.code_map build --root .` then `python -m scripts.code_map check --root .`, in that order. Currently 7/7 exit 0. **Expect the page content to change** — real docstring summaries across this repo will now render whole instead of clipped. That is the fix working. `deterministic-rebuild` must still pass.
6. Clean tree, committed with explicit paths.

## Not in this pass
- Defect 1 (BOM) is done. Leave it alone.
- Keep your `splitlines()` change.
- Do not touch `g6`'s staleness machinery, `g7`'s tag machinery, `thresholds.py`, page headers, or any named exclusion from the original brief.

## Constraints
- Full suite green (critic F6). Stdlib only. Page headers carry path and `, N lines`, never `:<line>`. `render_report.json` carries no timings. One name for one thing.

## Operating constraints
- No compound Bash: no loops, heredocs, `$(...)`, `env -u`, variable-assignment chaining, or long quoted strings. Plain separate commands or a script file. `git commit -F <file>`.
- **Do NOT `git add -A`.** The untracked `map/` tree is staged deliberately at the final gate.
- Do not push, merge, or force-push. Commit your own work.
- Revert checks: `git diff --quiet -- <path>`, never `git status --porcelain` (false-negatives under `core.autocrlf`).
- **Write the `IMPLEMENTER_RESULT` before you close the plan** — at `.agent-work/issue-456/crew-handoffs/g8-remediate-RESULT.md`. Last pass the plan reached all-complete with no result document, and the gate cannot close without one.
- Engine CLI: `--file` before the verb, `--session-id` after. `start <id>` before `advance`. Governor: attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`, read fresh each time.

## Model tier
`haiku` again, deliberately. Your own read was that this gate sat fine at this tier and that the friction was brief specificity rather than model capability. That is now testable: the defect above is specified as precisely as I know how to state it. If it goes smoothly, your read was right.

## Return format
`IMPLEMENTER_RESULT` with the evidence above, real numbers, and honest workflow feedback. If something did not land, say so — your last report's candour about the defensive fix is the reason this gate is being fixed properly instead of shipping broken.
