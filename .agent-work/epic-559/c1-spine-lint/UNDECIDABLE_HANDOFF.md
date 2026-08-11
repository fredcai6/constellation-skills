# Fix handoff — C1: the lint cannot say "I could not tell"

**Work id:** `epic-559/c1-spine-lint` · **Role:** implementer · **Model:** Sonnet
**Your spine:** `.agent-work/epic-559/c1-spine-lint/UNDECIDABLE_PLAN.json` — one gate, five checks. Two are red.

## Your rework was approved

The round-2 cold reviewer re-swept the corpus independently — 553 files — and got fault counts for
faults 1, 3 and 4 that **match your resweep table exactly**, confirming nothing regressed into them
when you touched shared tokenization. Fault 2 is at 1 hit, 0 false positives, and it verified your
epic-298 true positive down to the commit that renamed the test away. It also built 7 zero-collect
shapes and confirmed the lint still catches the ones it should.

Verdict `APPROVE`. This gate is one finding it raised and judged non-blocking, which I am promoting
because it is this epic's own subject.

## The finding

`_collects_zero` returns `None` when the interpreter cannot be resolved, when pytest is not
importable, when there is no `-k` selector, or on subprocess error. `_fault_zero_collect` appends a
fault only when that value is truthy. So **"could not tell" and "checked, found real tests" take the
identical path**: no fault, either way. `validate()` returns only `list[Fault]` with no companion
channel, and `main()` prints either `path: OK` or `path: N fault(s)`.

The reviewer confirmed it live: the same file, under two interpreters differing only in whether
pytest is importable, prints `OK` for one and `1 fault(s)` for the other.

So an operator running under the wrong interpreter — the most likely way to hit this, and a host
hazard `docs/agents/CREW_CONTEXT.md` documents explicitly — gets a clean `OK` with no sign that
anything went unevaluated.

**This tool exists to refuse things that look fine. A silence that looks like a pass is its worst
possible failure mode**, and it is the exact defect class the lint was built to detect, in the lint
itself.

## What to build

The rework's rule stands: an undecidable check is not a failing check, and the exit code should not
change. But the tool has to be able to *say* undecidable.

Add that channel in both places a caller reads: the library return and the CLI output. A caller must
be able to distinguish "this spine is sound" from "I could not judge N of these conditions". A
future generator will gate on this lint, and gating on silence is how the original defect got in.

`c1` checks the library side by handing it a check whose interpreter cannot run pytest and requiring
the result to mention that it could not evaluate it.

## Note on your `c3`

`check_corpus_fp.py` was wrong a second time and I fixed it. It filtered by filename substring —
`PLAN` or `SPINE` — which is the exact anti-pattern your own resweep identified and avoided, and it
silently dropped 11 of 25 real checklists including every `REVIEW_SURVEY`. It now discovers the
population by each file's own `type` field, the method you used, and asserts both that it examined
something and that what it examined is the population it claims to model. It reports 25 now.

It is still not yours to edit. Block against it if it is wrong a third time.

## Before you finish

Full suite, rebuild `map/INDEX.md`, append to `IMPLEMENTER_RESULT.md`, commit. `c5` refuses on a
dirty tree. Do not dispatch anything and then end your turn waiting for it.
