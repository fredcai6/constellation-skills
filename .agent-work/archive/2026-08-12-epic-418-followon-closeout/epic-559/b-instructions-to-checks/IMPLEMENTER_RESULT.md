# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`epic-559/b-instructions-to-checks` — rework (`REWORK_PLAN.json`: `r1-convention`, `r2-satisfiable`, `r3-shipped-checks-run`, `r4-verify`)

## Completed slice
Closed the loop the cold reviewer opened: (1) documented the `implementer-result` evidence convention `g1-implement.c1` depends on — field name `status`, value copied from the IMPLEMENTER_RESULT's own `Return status`, lowercase — in the three places a Commander would look, and pinned it with tests; (2) proved by a real engine drive (not an assertion) that a Commander following the new instruction actually clears `g1-implement`, both directions (complete advances, blocked refuses); (3) fixed `REVIEW_SURVEY.template.json`'s `<fowler-pass-record-path>` placeholder plus a second, previously-unreported instance of the identical bug in `INTERROGATION.template.json`'s `zc-consolidate.c1`, and pinned a sweep across all six shipped role templates so neither can regress and a third site can't ship silently.

## Scope
**Files changed:**
- `skills/commander/templates/EXECUTE_PLAN.template.json` — `g1-implement` imperative now names the field, its source, and the lowercase rule.
- `skills/commander/references/commander-core.md` — `gN-implement` bullet repeats the same convention.
- `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md` — `Return Format` section repeats it a third time, where a Commander fills the handoff an implementer returns against.
- `skills/reviewer/templates/REVIEW_SURVEY.template.json` — `r6-fowler.c1`'s check command and imperative now derive the Fowler-pass record path from `<work-id>` alone.
- `skills/interrogator/templates/INTERROGATION.template.json` — `zc-consolidate.c1`'s check command and imperative, same fix, same shape of bug.
- `tests/test_commander_evidence_convention.py` (new)
- `tests/test_shipped_template_gates_satisfiable.py` (new)
- `tests/test_shipped_check_commands_resolve.py` (new)

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/run_crew.py`, `skills/implementer/*`, `skills/reviewer/SKILL.md`, `settings.json`, `docs/agents/*` are all untouched — confirmed by the file list above and by `git diff --name-only main...HEAD` after this rework, which shows only the five source files and three new test files.

## Behavior changed
Yes. A Commander that follows the shipped `g1-implement` imperative now attaches `implementer-result` evidence with the field name and lowercase value the check actually matches, instead of guessing — closing #562 the way the reviewer required (fix the convention gap, don't weaken the check). Two review-survey/interrogation-survey gates (`r6-fowler`, `zc-consolidate`) that shipped non-functional out of the box now resolve their command checks from `<work-id>` alone, with nothing left for an instantiating agent to invent or forget.

## Map Impact
No `docs/architecture` map exists in this repo (`ls docs/architecture` → no such directory, matching the prior pass's and the reviewer's independent finding) — nothing to reconcile against. This is doctrine/template text and check-command wiring, not application code; no structural/capability/constraint anchors apply.

## Test mode
**Required:** `test-first` where each gate names a test-file postcondition (all three rework gates did).
**Satisfied:** yes — `tests/test_commander_evidence_convention.py`, `tests/test_shipped_template_gates_satisfiable.py`, and `tests/test_shipped_check_commands_resolve.py` were all written and run before their gate's `advance`, each gated by the plan's own `--collect-only` minimum-count check (`-ge 3`, `-ge 2`, `-ge 1` respectively) so a file that collects nothing could not have satisfied the gate.

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

**Result:** `pass` — `2542 passed, 1 skipped, 1102 subtests passed in 106.26s`. (The prior pass's reviewer reproduced `2532 passed, 1 skipped` before this rework's 10 new tests landed; `2542 = 2532 + 10`, consistent.)

```bash
python -m pytest -q tests/test_commander_evidence_convention.py tests/test_shipped_template_gates_satisfiable.py tests/test_shipped_check_commands_resolve.py -v
```

**Result:** `pass` — 4 + 2 + 4 = 10 tests, all green, run individually per-gate before the full-suite gate (`r4-verify`) re-ran them as part of the whole 2542.

## TDD evidence, if required
- Failing test observed: n/a for `r1`/`r3` — these tests assert a documentation/template convention that did not exist before this rework (there was nothing to be red against; the tests are the pin, not a red-green cycle over app logic). For `r3` specifically, I did verify red-before-fix by hand: the pre-fix `tests/test_shipped_check_commands_resolve.py` logic (built and dry-run before editing the templates) reported both `<fowler-pass-record-path>` and `<interrogation-record-path>` as offenders; after the template edits, the same test reports zero.
- Passing test observed: all three new files pass (see Evidence above), and `r2-satisfiable`'s test drove the *real* CLI (subprocess against `scripts/checklist_engine.py`) through a scratch instantiation of `EXECUTE_PLAN.template.json`, observing `g1-implement -> complete` on `status=complete` evidence and a `REFUSED: ... postconditions unmet` exit-1 refusal (gate left `in-progress`, not silently closed) on `status=blocked`.
- Refactor while green: no refactor step; each gate's tests were written once, correct, then the plan advanced.

## Docs/contracts touched
- `skills/commander/references/commander-core.md`, `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`, `skills/commander/templates/EXECUTE_PLAN.template.json` — the evidence convention, now stated in three places by design (the reviewer's own recommendation: "close the loop instead of guessing at it," repeated where a Commander would look).
- `skills/reviewer/templates/REVIEW_SURVEY.template.json`, `skills/interrogator/templates/INTERROGATION.template.json` — check-command and imperative text for the two fixed placeholder sites.

## Assumptions
- "The other shipped role templates as r3 requires" (handoff Scope section) and "ALL six shipped role templates" (r3's imperative) refer to the exact six-row "Template set" table in `skills/workbench/references/checklist-engine.md` (`COMMANDER_SPINE`, `EXECUTE_PLAN`, `INTERROGATION`, `REVIEW_SURVEY`, `IMPLEMENTER_PLAN`, `ENGINE_CONFIG`) — an already-existing, named list in the repo's own doctrine, not an arbitrary subset I chose. I did not extend the sweep to `ADMIRAL_SPINE.template.json`, `EXPLORER_SPINE.template.json`, `CARTOGRAPHER.template.json`, `CHARTER.template.json`, `SCOUT.template.json`, or `DEFAULT.template.json` (workbench) — these are real `gated` checklist templates too, but they are not in that table's "six," and the handoff scoped r3 to "all six," not "every gated/survey template in the repo." I did visually scan `ADMIRAL_SPINE.template.json` while investigating (its command checks use only resolver-owned `<work-id>`/`<repo-root>`/`<admiral-skill-dir>` tokens, all fine) but did not run the mechanical sweep or write it up as covered — flagged below as an out-of-scope observation rather than silently expanding scope.
- `<exact test command>` (in `EXECUTE_PLAN.template.json`'s `g1-integrate.c1` and `IMPLEMENTER_PLAN.template.json`'s `m1.c2`) is a legitimate authoring-time fill-in slot, not the same bug class as `<fowler-pass-record-path>`/`<interrogation-record-path>`: a Commander/implementer necessarily writes fresh, per-plan content there (there is no fixed value to derive from `<work-id>` or any other resolver-owned token), and each gate's own imperative instructs exactly that. I encoded this as a closed, two-item allowlist in the new sweep test rather than silently excluding it, so the allowlist itself is visible and reviewable.
- The Fowler-pass and interrogation record paths (`.agent-work/<work-id>/FOWLER_PASS.json`, `.agent-work/<work-id>/INTERROGATION_RECORD.json`) are the correct, already-established convention, not a value I invented: I verified `.agent-work/<work-id>/FOWLER_PASS.json` was the exact path the previous pass's reviewer actually used to repair their own survey mid-review (`REVIEW_SURVEY.json`'s `r6-fowler.c1`, current state on this branch), and `.agent-work/<work-id>/INTERROGATION_RECORD.json` matches the path convention visible across 10+ archived interrogation records under `.agent-work/` (e.g. `.agent-work/epic-298/INTERROGATION_RECORD.json`, `.agent-work/epic-418-redux/INTERROGATION_RECORD.json`).

## Stop conditions hit
None. All four rework gates advanced without a blocker or scope exception.

## Out-of-scope observations
- `ADMIRAL_SPINE.template.json` and `EXPLORER_SPINE.template.json` are real, engine-driven `gated` spine templates outside the named "six" and outside r3's scope as written, but they carry the same class of risk (a command check with a placeholder token). I spot-checked both while investigating; both currently use only resolver-owned tokens. Worth a triage candidate: extend the `test_shipped_check_commands_resolve.py` sweep (or a sibling test) to cover them and `CARTOGRAPHER.template.json`/`CHARTER.template.json`/`SCOUT.template.json`/`DEFAULT.template.json` too, so the "six" in the workbench doc and the actual set of engine-driven templates converge, rather than leaving a documented list that quietly under-covers the real population.
- The `implementer-result` evidence convention is now documented in three places, all pointing at the same source of truth (`status-model.md`'s `Crew Return Status` enum) via `tests/test_commander_evidence_convention.py`. That test derives its expected field/value directly from the shipped template rather than hardcoding `"status"`/`"complete"` as literals, so a future rename of the field (not just a value drift) stays caught — but it does not, and cannot, prevent a *fourth* undocumented copy of the convention from appearing in some future template. If the convention grows a fourth call site, extending the existing test's doc list is cheaper than writing a new one.

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`; a bare `none` is treated as an unfilled field.

- **Handoff gaps:** `REWORK_PLAN.json` (my own spine, handed down as "drive it gate by gate") used the key `"gates"` for its ordered item-id list; the engine (`checklist_engine.py`) reads `cl["items"]` unconditionally and raised a bare `KeyError: 'items'` on the very first `current` call, before any doctrine or rail text could even print. Every other real spine in this repo (`IMPLEMENTER_PLAN.json`, `EXECUTE_PLAN.template.json`, the schema doc's own storage-model example) uses `"items"`. I fixed the one-line key rename as a raw-text edit (re-validated with `json.load`) before doing anything else, since without it the plan could not be driven at all — this is a handoff-authoring bug, not a rework-content one, and is worth catching before a plan file is handed to an implementer, e.g. a cheap `json.load` + `"items" in data` sanity check at handoff-authoring time.
- **Context rediscovered:** The exact scope of "all six shipped role templates" (r3's imperative) was not self-evident from the rework plan alone — I had to find `skills/workbench/references/checklist-engine.md`'s "Template set" table to get an authoritative, non-arbitrary six-item list rather than guessing among the twelve `gated`/`survey` templates that actually exist in this repo. Naming that table directly in r3's imperative (or the handoff) would have saved the search and removed a scope-interpretation judgment call I otherwise had to make and then defend in Assumptions above.
- **Instructions improvised around:** The handoff names `spine_capture` and `spine_amend` as denied MCP door tools "on this branch." I never needed either verb for this rework (no `amend`, no `capture` — every gate advanced cleanly through documentation + tests), so I drove the entire rework through the CLI (`scripts/checklist_engine.py`) throughout rather than touching the MCP door at all, and cannot independently confirm the denial from this run.
- **What would have made this easier:** Fixing `REWORK_PLAN.json`'s `"gates"`/`"items"` mismatch before handoff, and citing `checklist-engine.md`'s Template set table by name in r3's imperative instead of leaving "all six" to be resolved by search.

## Return status
`complete`

---

## What the first census missed, and why

The census (`CENSUS.md` row #21) marked `REVIEW_SURVEY.r6-fowler`'s command check "already converted, no action" — true in the narrow sense the census was checking (the row's check *shape* had already been converted from a mandatory-prose instruction to a `command`-kind postcondition, which was that pass's actual task). What the census never checked, for that row or any other, is whether the resulting command would **run successfully once a real agent instantiated the template** — it verified presence and shape, never resolvability. `python scripts/verify_fowler_pass.py <fowler-pass-record-path>` is syntactically a well-formed `command` check; nothing about its *shape* signals a defect. Only tracing what actually substitutes `<fowler-pass-record-path>` — and finding the answer is "nothing, automatically" — surfaces the bug, and that trace was outside the census's question.

**Would the new tests have caught it?** Yes, directly: `tests/test_shipped_check_commands_resolve.py` is built exactly to answer the question the census never asked — for every command check across the six shipped templates, resolve it the way a real instantiation would and assert nothing unresolved survives except a closed, named allowlist. Run against the pre-fix templates (verified by hand before editing them), it reports both `r6-fowler.c1`'s `<fowler-pass-record-path>` and the previously-unreported `zc-consolidate.c1`'s `<interrogation-record-path>` as offenders; after the fix, zero. That second finding is itself evidence for the test's value: it caught a real, shipped instance of the exact bug class that neither the original census nor the cold reviewer's manual read had reported, simply because the test checks the mechanism (does it resolve?) rather than trusting a per-row human judgment call.
