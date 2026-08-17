# Review Result

## Assigned Gate

`g4-review` — Dispose #596 and #526: review.

## Verdict

`APPROVE`

## Result

`APPROVE`

Survey: `.agent-work/567-d1/g4-review/review.json` — 11 items, all recorded `pass`, consolidated
`APPROVE` with `override_reason: none`. Fowler record: `.agent-work/567-d1/g4-review/FOWLER_PASS.json`.

## Handoff compliance

Both issues carry a disposition backed by a grep, and both files are non-empty and quote their
evidence, including negatives. The asymmetric standard the handoff set is met: every negative
survived a widened re-run, and I ran each widened search with a positive control so an empty result
could not be mistaken for a clean one.

**#596 — the crux, verified at source.** I read the `feedback` gate in
`skills/commander/templates/COMMANDER_SPINE.template.json` myself:

```
feedback.preconditions  == [p1]  (run summary accepted)
feedback.postconditions == [c1]  command: verify_episode_captured.py <work-id> --store-root episodes --phase feedback
```

One postcondition, one check, no reference to any export. **The old clause was false as written.**
*"A `FENCE.md` citation without the staged export still fails the gate"* asserts a failure mode the
gate has no mechanism to produce. The repair replaces it with the measured statement and is true as
written.

**#526 splits three ways, correctly.** Defect 1 does not reproduce; the widened form does, once; and
defect 2 reproduces. Details under Evidence verdict.

## Scope drift

None that matters, and the one departure is sanctioned.

Eight tracked files. Seven are squarely in allowed scope, including all three mirrors of
`REVIEW_SURVEY.template.json` — I re-measured them at md5 `d8c1fb421b78799a1cae8662c04fe467`,
identical across `skills/reviewer/templates/`, `.agent-work/templates/`, and
`.agent-work/templates/.baseline/constellation-reviewer/`. **Zero fenced files touched:** no
`docs/agents/**`, no `skills/workbench/**`, no `scripts/*`, no `episodes/**`, no `map/INDEX.md`, no
`tests/test_cli_retirement_guard.py`.

`skills/admiral/references/fleet-doctrine.md` is admiral-owned source, not one of the per-role copies
`install_constellation.py` regenerates — `skills/_shared/` holds only `global-*`, `windows`,
`design-it-twice-brief`, `skill-goodness`, `stand-up-work-area` — so CREW_CONTEXT's "never edit the
per-role copies" rule is not engaged.

`tests/data/store_mentions.approved.txt` is outside the allowed-scope list. **Accepted:** handoff
constraint 4 ("any edit to `skills/**` must keep the guard green") is unsatisfiable without moving the
census in lockstep; the file is not on the fence list; the implementer disclosed it in `596.md` §7
rather than slipping it through; and commit `aeba10ae`, earlier in this same lane, set the precedent —
I confirmed it edits ten `skills/**` files and the same census in one commit.

## Evidence verdict

Every claim I checked reproduced. I re-ran all five close criteria and read the exit codes.

| check | result |
|---|---|
| `pytest tests/test_cli_retirement_guard.py -q` | exit 1; violations **only** in `skills/workbench/` (2 of them, so the extraction is non-empty) — 0 outside |
| `pytest tests/test_mcp_adoption.py -q` | exit 0 — 172 passed, 2 skipped |
| `pytest tests/test_retirement_guard.py -q` | 16 passed |
| JSON parse over `skills/**` + `.agent-work/templates/**` | 41 files, all parse |
| three-copy identity | identical, md5 above |

**The widened negatives.**

*#526 defect 1 — "does not reproduce, and never did, in the skill corpus."* This is the strong claim
the handoff told me to test against history, and it holds.

- The implementer's grep, widened with `.agent-work/templates/` and its `.baseline/` mirror: still 3
  hits, all in `docs/CONSTELLATION_OVERVIEW.md`, all naming the *package*, never the two standalone
  scripts.
- `code_map` anywhere under `skills/` or the overlay: **0**.
- Widened past the script name to **any** `build.py`/`check.py` across `skills/` + overlay + `specs/`:
  **0**.
- History, widened from `-S 'code_map/build.py'` to bare `-S 'code_map'`:
  `git log --all -S 'code_map' -- skills/` = **0** and `-- .agent-work/templates/` = **0**, across
  **1792 revisions on all refs**. The same probe *without* the pathspec returns **10 commits**, which
  is the positive control proving the search reaches.

*#526 defect 2 — the survey-reuse negative.* Re-run against the **pre-change** tree (`96f1198f^`),
because the fix itself would otherwise pollute the result, and widened from `skills/reviewer/` to all
of `skills/` + `docs/agents/` + `.agent-work/templates/` with four patterns the implementer did not
try (`round file`, `re-drive`, `rework round`, `review-2`): **0 hits**. Post-change the same pattern
set finds exactly the new paragraph — the control.

*#526 defect 1, widened — the positive.* I rebuilt the census independently rather than trusting it,
extracting every `kind: command` check from all 20 shipped `skills/**/templates/*.json` and
classifying its script references:

```
PRE-change (96f1198f^):  17 refs = 16 resolver-token + 1 bare
   BARE: skills/reviewer/templates/REVIEW_SURVEY.template.json  r6-fowler.c1 -> scripts/verify_fowler_pass.py
POST-change:             17 refs = 17 resolver-token + 0 bare
```

Exactly the implementer's 16-of-17. And the token resolves rather than being a phantom — I ran
`init_work_area.resolve_spine` over the edited template in both layouts and got byte-identical output
to the implementer's, with no leftover `<...>` token:

```
source-repo (no --skill-dir)  -> python scripts/verify_fowler_pass.py .agent-work/567-d1/FOWLER_PASS.json
installed skill dir           -> python /home/tommy/.claude/skills/constellation-reviewer/scripts/verify_fowler_pass.py .agent-work/567-d1/FOWLER_PASS.json
```

`_ROLE_SKILL_DIR_RE` is generic (`<([a-zA-Z0-9-]+)-skill-dir>`), so `<reviewer-skill-dir>` works
through the existing mechanism, not a hardcoded addition.

**The two questions the handoff required answers to.**

*No successor playbook.* `docs/agents/ORCHESTRATOR_CONTEXT.md` §"The Retired Learning Playbook"
retires `.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md`, and
`verify_retirement.py`'s `RETIRED_NAMES` agrees exactly — `CONSTELLATION_FEEDBACK.md` is in neither,
so rescoping rather than deleting is the right call. Against the hard bound *"no successor playbook
and no read-and-apply loop"*: the repair creates no file, no store, and nothing an agent is told to
consult; it only **deletes** claims about what gates enforce. I searched for a read-back path and
found none — the sole consumers of `CONSTELLATION_FEEDBACK.collected.json` are `collect_feedback.py`'s
own dedupe sidecar and the `archive` `c4` deny-glob. The surviving channel runs
consuming-project → maintainer, never store → agent behaviour.

*The fence case, and `c4`.* A fenced Commander's episodes reach the Admiral through the commit —
`episodes/` is tracked inside its own worktree — and that capture is the gate's only postcondition.
For the export half I ran the **real** `evaluate_git_change_policy` from `scripts/checklist_engine.py`
against `archive` `c4`'s actual policy rather than reasoning about globs:

```
allowed  .agent-work/staged-feedback/567-d1/CONSTELLATION_FEEDBACK.md
allowed  .agent-work/staged-feedback/567-d1/FENCE.md
DENIED   .agent-work/CONSTELLATION_FEEDBACK.md
DENIED   .agent-work/CONSTELLATION_FEEDBACK.collected.json
```

`_glob_match`'s basename fallback fires only for separator-free patterns, so the deny globs anchor at
the root and cannot reach the nested staging dir. "Stage it under `.agent-work/staged-feedback/`" and
"`c4` deny-globs it out of your commit outright" are therefore both true at once, and the two sides
are symmetric — the Admiral text says look in both places the delegated text says to write.

**The census delta.** 3 insertions / 3 deletions: the admiral entry plus its reason comment
(`harvest` → `collect`), and the commander-delegated entry. No entry removed without a replacement.
`fleet-doctrine.md` correctly needed none — only its `episodes/`-bearing line is keyed and the
rewrite left that line byte-identical, which is why two violations appeared mid-edit rather than
three. The two guard tests are complementary (`test_canon_is_clean` catches an edited line that is no
longer approved; `test_every_approved_entry_exists_verbatim` catches a census entry that no longer
exists), so a silent drop in either direction would have gone red. Both green.

## Code/doc quality

The prose is a clear improvement. It replaces three unfalsifiable mandates with measured statements,
and the `harvest` → `collect` rename is required by `docs/agents/GLOSSARY.md`, which defines `harvest`
narrowly as writing **into** the episode store — using it for moving a markdown file between checkouts
was the glossary's own counter-example. `collect` matches the tool that does it.

Compact JSON was edited as raw text, not round-tripped: each of the three copies is a 1-line `+/-`
change, so blame survives and no reflow occurred.

Fowler pass: 12 smells rendered, `verify_fowler_pass.py` exits 0. One flagged (`shotgun-surgery`),
three overridden with a named standard and reason (`long-method`, `duplicated-code`,
`speculative-generality`), eight absent.

## Map impact verdict

- **Evidence supports claimed change:** yes. I reproduced the map claim rather than accepting it —
  `map_orient.py orient --root . --work-id 567-d1` returns `DEGRADED-UNPARSEABLE`, `anchor_count 0`.
  Framing Map Impact against the handoff's named entry points is honest, not evasive.
- **Constraints not violated:** yes. `constraint:episodes-are-not-prescriptions` holds — see the
  successor-playbook check above.
- **Notes match the diff:** yes, and the notes understate nothing.
- **Decision candidates surfaced:** yes, and genuinely deferred — both concern fenced files.
- **Durable context routed:** yes. Two candidates staged by the implementer, one more by me. No
  issues filed, per the standing constraint.

Not architecture-significant: doctrine prose plus one command-check string that resolves
byte-identically in this repo.

## Reconciliation check

Nothing for the Commander to reconcile. No module added, no boundary shifted, no interface changed.

## Blockers

- none.

The handoff's three stop conditions were each tested and none fired: every negative survived its
widened search; the repair reinvents no successor playbook; and no fenced file needed editing.

## Out-of-scope observations

1. **The new re-review convention over-prescribes one clause, and this run is the counterexample.**
   The paragraph's decisive claim is right and well-evidenced: both `g1b` and `g3` used a new round
   file, left round 1 untouched, and consolidated `APPROVE` with **no** override, which is exactly why
   the re-consolidate-with-`--override-reason` shape is the wrong one. But *"Add this round's rechecks
   with `append`, one flat sibling per finding the previous round raised"* describes **neither** round.
   `g3` round 2 appended **nothing** and re-ran base check `r3-evidence` in the fresh file; `g1b`
   round 2 appended **five** siblings against **two** prior findings. The actual practice is: a
   finding that maps onto a base check is rechecked there — the new file's base checks are fresh and
   pending, so recording `pass` is not a downgrade — and a finding with no base-check home gets an
   appended sibling. Following the clause literally yields a redundant sibling beside an already-fresh
   base check. Harmless in effect, and the `append`-is-a-sibling mechanics it teaches are correct and
   necessary (I relied on them here), so this is **incomplete prose, not a false model** — which is
   why it is an observation and not a blocker. The Commander may want the clause to say "one sibling
   per finding that has no base check to re-run."

2. **The coupling that caused #596 is uncorrected.** Staged as
   `.agent-work/567-d1/triage-candidates/doctrine-asserts-spine-postconditions-with-no-tie.md`. Three
   doctrine files plus two census entries assert facts owned by `COMMANDER_SPINE.template.json`, and
   no check connects them. Move the spine's postconditions again and all three go stale silently — the
   #596 shape recurring. The census does not help: it pins the prose to *itself*, so a
   wrong-but-stable claim stays approved indefinitely. By `docs/agents/GLOSSARY.md`'s `two-bin rule`
   these claims are in neither bin. Not actionable here — it needs tooling or a `docs/agents/*` rule,
   and that promotion is the human's call.

3. **Minor, introduced by this change.** `r6-fowler`'s imperative still says the postcondition
   *"resolves the record path from `<work-id>` alone … so no separate placeholder to fill."* That
   remains true of the **record** path, but the command now also carries `<reviewer-skill-dir>`. A
   reviewer hand-instantiating from the imperative alone could leave the token literal. It is only
   *technically* accurate because the resolver owns the token and the workbench engine reference
   separately instructs resolving `<…-skill-dir>`. Half a sentence would close it.

## Workflow Feedback

- **Handoff gaps.** The **Survey State Location** and the Fowler record path conflict with the
  template. The handoff names `.agent-work/567-d1/g4-review/FOWLER_PASS.json`; the template's
  `r6-fowler.c1` resolves `.agent-work/<work-id>/FOWLER_PASS.json`. I corrected it through the
  engine's `amend`/`retext-check` repair path as the template directs, with `--authority` set to the
  Commander named in the handoff — but the handoff could have said "expect to amend `c1`" in one line
  and saved the round trip. The staged candidate `fowler-record-path-collides-across-gates.md` shows
  this is now the third gate to hit it.
- **Context rediscovered.** Two things. (1) Whether `<reviewer-skill-dir>` should resolve to the
  installed skill dir or the repo root — the reviewer SKILL.md does not say; the answer is in the
  **workbench** engine reference's dogfooding paragraph, which is not among my handoff's map anchors.
  On this repo it is the repo root. (2) `docs/agents/CREW_CONTEXT.md` states that `python3` has no
  pytest on this host, measured 2026-08-10. It does now (9.1.1, same as `py`), so the handoff's
  `python3 -m pytest` commands ran fine. The doc tells you to check first, so it defended itself — but
  a crew that trusted the measurement would have switched interpreters for no reason.
- **Instructions improvised around.** The `amend --delta` op shape is undocumented in the engine
  reference, which says only "the ops live inside the `--delta` FILE". My first attempt used
  `task_id`/`condition_id`/`check` and was refused with `REFUSED: retext-check None: no such gate` —
  a refusal that names the *symptom*, not the wrong key. The working shape is
  `{"id", "cond", "which", "command"}`. I found it by reading the leftover delta files in
  `g3-review/`, where the previous reviewer visibly needed three attempts at the same thing. That is
  two reviewers burning turns on one undocumented shape.
- **My own mistakes.** I initially read the new `<reviewer-skill-dir>` token as contradicting the
  imperative's "no separate placeholder to fill" and was ready to raise it as a repeat of the exact
  #596 defect. Re-reading, the sentence's subject is the *record* path, which is still true, and the
  engine reference already governs `<…-skill-dir>` resolution corpus-wide. I downgraded it from a
  candidate blocker to observation 3. I also nearly ran the full suite before re-reading constraint 7.
- **What would have made this easier.** Document the `amend --delta` op shape — one worked example in
  the workbench engine reference under `amend` — and add the workbench dogfooding paragraph to the
  reviewer handoff's map anchors whenever the gate touches a `<*-skill-dir>` token.

## Return status

`complete`
