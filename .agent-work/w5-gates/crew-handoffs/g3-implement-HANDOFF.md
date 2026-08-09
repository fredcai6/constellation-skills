# Implementer Handoff

## Gate
`g3-implement` — `archive.c2b` reachability check (issues #439 + #484), work-id `w5-gates`, epic #418
wave 5.

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Use absolute paths.

## Operational facts — these have cost this run real time

1. **Use `python`, never `py`.** Different interpreters here; `py` has no pytest, so `py -m pytest`
   exits nonzero and reads exactly like a red suite when the tests never ran.
2. **Never pipe a pytest command into `tail` or `head`.** `$?` then belongs to the pipe, and a
   zero-match `-k` selector — which exits **5** — reads as exit 0. If you want both the exit code and
   the output, redirect to a file and echo `$?`; a redirect is not a pipe. I made this mistake myself
   on this run and nearly recorded exit 0 for a red run.
3. **Find code by text, not by line number.** g1 and g2 grew the test file by ~590 lines. Every line
   number in the frozen plan is stale.
4. Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` in `git status`
   with **empty diffs** — a CRLF stat artifact. **Leave them unstaged.**

## Task Statement

Rewrite **`archive.c2b`** in `skills/commander/templates/COMMANDER_SPINE.template.json`. The shipped
check command is currently, verbatim:

```
gh pr list --head <branch> --state open --json number --jq 'length > 0'
```

### TWO defects, not one (launch-order pre-ruling 5)

1. **The literal `<branch>` token is never substituted.** It is not a resolver-owned token, so
   instantiation cannot catch it — the command ships with `<branch>` in it and fails at runtime.
2. **The criterion accepts only an OPEN pull request.** A merged PR means the work is reachable; this
   check calls it unreachable.

**A third property you must preserve, which is why the replacement is shaped as it is:** `--jq
'length > 0'` *prints* `true` or `false`, but `gh` exits **0 either way**. The engine's verdict for a
`command` condition is the **exit code**, and stdout is discarded (`docs/CHECKLIST_SCHEMA.md`). So the
current check's verdict never rides the exit code at all. Compare the count **in the shell** so the
exit code carries the verdict.

### The resolved shape

Already verified against four real branches (no-PR → 1, MERGED → 0, CLOSED-unmerged → 1, MERGED → 0):

```sh
test "$(gh pr list --head "$(git -C <repo-root> rev-parse --abbrev-ref HEAD)" --state all --json state --jq '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length')" -gt 0
```

Derive the branch through the **EXISTING `<repo-root>` token**. Accept `{OPEN, MERGED}` while still
rejecting **CLOSED-unmerged**.

**NO new resolver token.** `scripts/init_work_area.py` stays **UNTOUCHED** — the branch is not
guaranteed to exist when the spine is instantiated, because `init`'s own imperative instantiates the
spine first and starts the branch after. `init_work_area.py` is inside the ownership scope but is
**expected to take a ZERO-line diff**; if you find yourself editing it, **stop and say why**.

### DO NOT adopt #484's suggested replacement verbatim

It exits 0 on an empty list and is **a check that cannot fail** — that was cold critic finding 1, and
this whole wave is about checks that cannot fail.

## Test Mechanism — the hard part

No test in this repo invokes `gh`, and the verifier is explicitly network-free. So:

- Put a **STUB `gh`** (and `git`, if you need to pin the branch name) **early on PATH** inside the test.
- Assert on the **EXIT CODE** of the resolved text, run through **the same POSIX shell the engine
  uses**.
- **Extract the command text FROM the template.** Never hand-retype it — a retyped copy stops testing
  the shipped artifact, and this gate exists because a byte-identical template would have closed the
  old check green.

Cover the four states: **no PR**, **OPEN**, **MERGED**, **CLOSED-unmerged**. The first and last must
fail; the middle two must pass.

## Test Naming Contract — LOAD-BEARING

This gate's close criteria are `-k` selectors on these substrings. A zero-match selector exits 5 and
**fails the gate closed** — deliberate, and the remedy for cold critic BLOCK finding F2, which
measured that fix C touches no Python at all and a byte-identical template would have left the old
whole-file check green. **Do not rename around it.**

- State-matrix tests **MUST** carry **`archive_c2b`** in their names.
- Tests proving a reintroduced literal `<branch>` or a narrowed `--state open` goes **RED** **MUST**
  carry **`archive_mutation`**.

## Allowed Scope

- `skills/commander/templates/COMMANDER_SPINE.template.json`
- `tests/test_iterative_planning_doctrine.py`
- `scripts/init_work_area.py` — in scope but **expected to be a zero-line diff**.

## Specific Exclusions

- `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — **crew 4 is their sole writer.**
- `scripts/install_constellation.py` — crew 2 (readable, not editable).
- Handoff templates — crew 3. `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` — crew 5.
- `scripts/verify_iterative_role_artifacts.py` — gates g1/g2, already closed. Do not touch.
- Hooks, any `settings.json`, `docs/agents/*` doctrine.

**Any red outside the ownership scope is a FLOAT, not an edit.**

## HONEST NULL — read before you start

If the resolved text **cannot** be exercised without real network or `gh` auth, **say so plainly** and
report what you could and could not prove. **Do NOT substitute a test that only re-reads the template
string and calls that verification** — that would be a check that cannot fail, inside a gate about
checks that cannot fail. Scope the null precisely: "this specific mechanism is refuted because X",
never "this approach is impossible."

## Map Anchors (inbound)

No architecture map — orientation is `DEGRADED-NO-MAP`, anchors named by path, no `struct:`/`decision:`
ids.

- **Structural:** `skills/commander/templates/COMMANDER_SPINE.template.json` — the `archive` task's
  `c2b` postcondition. Find it by the text `the work is REACHABLE`.
- **Capability:** Commander closeout reachability — a strengthened durable system.
- **Constraints:** `docs/CHECKLIST_SCHEMA.md` — a `command` condition's verdict is its **exit code**;
  stdout is **discarded**. This is why the count comparison must happen in the shell.
- **Decision anchor:** the branch is derived at check time from `<repo-root>`, not resolved at
  instantiation time, because the branch may not exist when the spine is instantiated.
  `@grade: settled/human · leans g3-implement,g3-review · (pre-ruling 5 — two defects, not one; a contradiction is a float, not a revision)`
- **Map confidence flags:** the instantiate-time vs check-time distinction is this gate's **unmapped
  seam**. Measure `init_work_area.py`'s actual ordering rather than assuming it.

## Evidence Expected

Run each bare (or redirected, never piped), report the exit code you actually saw and **how many tests
each selector collected** — zero is a gate failure, not a pass:

- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_c2b`
- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_mutation`
- Coupled suite:

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

Baseline at HEAD `bd56ac8a` is **390 passed / 488 subtests, exit 0**. Report your delta and account for
it — an unexplained delta is a finding.

Report the **four-state measurement** explicitly (no-PR, OPEN, MERGED, CLOSED-unmerged with their exit
codes); the Commander must record it in `REPLAN_INPUT.json` as observed evidence.

## A warning from this run's own history

At gate g2 the reviewer found the implementer's mutation test had a **no-op leg**: one mutation looked
like it proved something but could not fail, because the mutated field was legitimately empty for that
packet shape. **For each mutation you write, ask what would have to be true for it to be a no-op, and
say so in your result.** That is the single most valuable thing you can report here.

## Stop Conditions

Return BLOCKED if: the resolved text cannot be exercised without real network (the honest null); a
non-owned file goes red; `init_work_area.py` appears to need edits; or a policy decision is required.

## Return Format

Write your IMPLEMENTER_RESULT to `.agent-work/w5-gates/crew-handoffs/g3-implement-RESULT.md`. State
`COMPLETE` or `BLOCKED`, the four-state measurement, per-item evidence with real exit codes and
collection counts, files touched (with `git diff --numstat`), the no-op analysis above, anything you
floated, and workflow feedback.

## Suggested Model Tier

Stronger. The test mechanism has to be invented rather than followed, and the honest-null branch needs
judgment.
