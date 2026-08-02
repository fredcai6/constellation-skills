# Reviewer Handoff — issue-304 gate g1

## What was implemented

`scripts/map_orient.py` (new) — subcommands `orient` and `verify-orientation`. Resolves a canonical map
entrypoint, writes a receipt to `.agent-work/<work-id>/map-orientation.json`, and REPORTS a degraded
verdict rather than silently falling back. Plus a `<repo-root>` placeholder in
`scripts/init_work_area.py`, and two new test files.

## How to inspect the diff

```
cd C:/Programs/constellation-skills-wt/e298-304
git status --porcelain
git diff -- scripts/init_work_area.py
```
New files: `scripts/map_orient.py`, `tests/test_map_orient.py`, `tests/test_mutation_floor.py`.
Implementer's own report: `.agent-work/issue-304/crew-handoffs/g1-result.md`.

## Task statement it was built against

`.agent-work/issue-304/crew-handoffs/g1-implementer-handoff.md` — read it; it is the contract.

## THE QUESTION THIS HANDOFF EXISTS TO ASK

**CAN THIS CHECK FAIL?**

This is asked because #300 shipped an acceptance test that **survived two independent reviewer rounds**
while being structurally unable to falsify the property it existed to falsify. One of those rounds
returned a correct BLOCK on a different real defect — so competence was not the problem. The commander's
diagnosis: *"a reviewer given a handoff checks conformance to that handoff, and no handoff asked 'can
this test fail?'"*

**This handoff asks it. Answer it with execution, not judgement.**

You MUST:
1. **Devise at least one mutation of your own that is NOT in the shipped floor.** The shipped three are
   `all`→`any` on degraded-completeness, `UNRESOLVABLE-ROOT`→`DEGRADED-NO-MAP` with exit 0, and
   citable-content→`path.exists()`. Yours must be different.
2. **Apply it.**
3. **Run the suite.**
4. **Report whether it went red**, with the actual output.

A review that reports conformance without attempting a mutation **has not completed this gate** and I
will send it back.

### Specifically attack the mutation harness itself

`tests/test_mutation_floor.py` is supposed to assert **the mutation APPLIED before it asserts red**,
because a substitution that silently fails to match produces a green baseline **indistinguishable from a
killed mutant**. The implementer reports the applied-assertion uses a strict **count delta** rather than
`assertIn`, because mutation 2's replacement text already occurs elsewhere in the module — so `assertIn`
would have passed with nothing substituted.

**Verify that claim independently.** Then attack it: can you construct a mutation whose anchor does not
match, and does the harness raise a loud `HarnessError` rather than reporting a killed mutant? If the
harness can be fooled into reporting a kill it did not earn, that is a BLOCK.

## Close criteria

- `python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_init_work_area.py -q` green.
- `python scripts/map_orient.py --self-test` green.
- Exit-code vocabulary provably clear of argparse (2), traceback (1), and 126/127.
- **RESOLVED requires citable content**, not file existence — a scaffolded-but-empty index must read
  DEGRADED. A false RESOLVED is strictly worse than an honest DEGRADED.
- **"Could not look" (`UNRESOLVABLE-ROOT`) is distinguishable from "looked and found nothing"
  (`DEGRADED-NO-MAP`)** via a *positive* repo-root proof, not an absence test (#265).
- DEGRADED completeness requires `substitutes` AND `unmapped` AND `escalation` — all three; empty or
  `"none"`/`"n/a"` fillers refuse.

## Three deviations already adjudicated — do not re-litigate, but DO verify the reasoning

1. `<repo-root>` emits `.as_posix()`, not `str(Path(root).resolve())` — because `str()` breaks
   `instantiate_spine`'s own `json.loads` on Windows (`Invalid \escape`). **ACCEPTED.** Verify the claim
   is true; flag if not.
2. Additive 5-test class appended to `tests/test_init_work_area.py` (26→31, nothing existing modified).
   **ACCEPTED.** Confirm nothing pre-existing was modified.
3. `orient` gained `--substitute` / `--unmapped` / `--escalation` beyond the frozen synopsis — without
   them nothing can declare a substitute for the tool to hash-pin. **ACCEPTED** as a necessary
   consequence of the hash-pinning requirement.

## Allowed scope / exclusions

Review only the four files above. **Out of scope, do not flag as defects:** `verify-frame` (g2), any
template wiring (g2), any prose deletion (g3), the five fragile relative command checks (#341), the
episode store (#342), a bootstrap/CLAUDE.md stanza (ruled OUT — the map is orchestrator content).

## Known limitation you should NOT report as a novel find

The necessity/citation property this gate builds toward has **measured sensitivity 0/4 and specificity
0/1** against the epic's baseline five. It ships as a **regression floor**, explicitly not as the fix for
the measured defect. That is a ratified framing, not an oversight.

## One real issue found in review-of-the-review — confirm the fix

Running `orient --root <a read-only repo>` **writes a receipt into that repo**. Your commander hit this
while verifying against f1Brainz and had to clean it up. Assess whether `orient` should refuse or offer a
no-write mode when pointed at a repo it does not own. Report as a finding with a severity; do not fix it.

## Constraints

- Windows: `encoding='utf-8', newline='\n'`. Tests via `python -m pytest` (local 3.14 vs CI 3.12 —
  flag any 3.13+-only API as a BLOCK; `Path.read_text(newline=...)` cost 39 CI failures on PR #320).
- `C:/Programs/f1Brainz` is **READ-ONLY** — and note that `orient` writes a receipt, so do **not** point
  it at f1Brainz without `--work-id` pointing somewhere disposable, or you will repeat the mistake above.
- Never touch `C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.

## Required evidence

Paste actual command output for: the suite, the self-test, your own mutation (before/after + red/green),
and your check of the applied-assertion claim.

## Return format

Write `REVIEW_RESULT` to `.agent-work/issue-304/crew-handoffs/g1-review-result.md` with a verdict of
exactly **APPROVE** or **BLOCK**, findings by severity, and the evidence above. Return thin.
