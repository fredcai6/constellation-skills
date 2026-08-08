# Review Result

## Assigned Gate
`w3a-465 / g1-review` — issue #465, epic #418 wave 3, under Admiral launch order LO-465.

Survey driven at `.agent-work/w3a-465/g1-review/review.json`, engine session `rev-w3a-465-g1`,
12 checks (7 template + 5 appended), all visited.

## Result

**APPROVE**

No blockers. Four triage candidates. All seven close criteria met, each verified against the world
rather than against the implementer's report.

## Handoff compliance

All five items were implemented and each does what it claims.

Criteria 3, 4 and 5 were confirmed by live engine runs on a **probe survey instantiated from the
shipped `REVIEW_SURVEY.template.json`**, not from a unit fixture
(`.agent-work/w3a-465/g1-review/probe/`):

| step | observed |
|---|---|
| record `r6-fowler` pass with a wrong path in `c1` | `REFUSED: r6-fowler: command postconditions unmet ['c1']` |
| `amend --delta <file>` with one `retext-check` op | `amended: retext-check r6-fowler.c1 (authority Commander w3a-465)`, real exit 0 |
| record `r6-fowler` pass again | `r6-fowler recorded pass`, real exit 0 |
| `add` / `drop` / `rescope` on the same survey | each refused, real exit 1, each naming its own op and the word **conservative** |

**Criterion 4 — the imperative names a verb that actually works.** Yes, on both paths. I drove this
review's own `r6-fowler` by the imperative's **normal path** — resolve `<fowler-pass-record-path>` at
instantiation time, exactly like `<work-id>` — and it worked first time; this survey's `record
r6-fowler --result pass` succeeding *is* that proof, because the engine ran the `c1` command to let it
through. The **repair path** was exercised separately on the probe above. The Commander's own wrong
wording (`amend --op retext-check`) was **not** propagated: `grep -rn "\-\-op "` over
`skills/reviewer/`, `docs/CHECKLIST_SCHEMA.md` and `skills/workbench/references/checklist-engine.md`
returns nothing. The shipped `skills/workbench/references/checklist-engine.md` goes further and states
the ops live inside the `--delta` file and there is no `--op` flag.

**Criterion 5 — `amendments` is read, not just written.** Read back from the probe survey on disk
after the retext:

```json
{
  "ts": "2026-08-08T05:59:21.700503+00:00",
  "reason": "the record path substituted at instantiation was wrong",
  "authority": "Commander w3a-465",
  "ops": ["retext-check r6-fowler.c1"]
}
```

Reason, authority and op are all recorded, and the op entry names the target condition too. The audit
trail the safety argument rests on is real.

## Scope drift

None. The changed set is exactly the allowed set: `docs/CHECKLIST_SCHEMA.md`,
`scripts/checklist_engine.py`, `skills/reviewer/SKILL.md`,
`skills/reviewer/templates/REVIEW_SURVEY.template.json`,
`skills/workbench/references/checklist-engine.md`, plus new
`tests/test_engine_survey_retext_and_newlines.py`.

All four named exclusions are untouched — `git status --porcelain --` over them returns empty, and I
confirmed all four paths **exist**, so the empty result is real and not a mistyped pathspec.

`consolidate()` is unchanged. The engine diff has four hunks, at `load`/`save` (168–183) and inside
`amend` (2181–2200) only; `consolidate()` lives at 1949–1971 and the string `consolidate` appears zero
times in the engine diff.

**Constraint held:** `r6-fowler`'s `c1` is still a `kind: command` check. The template diff touches
only the imperative string; the postconditions line is unchanged diff context. It also still bites at
runtime — the probe's first `record` was refused by it.

## Evidence verdict

**I reproduced the red myself. It is real, and it is the fixture the implementer named.**

Method: copied `scripts/checklist_engine.py` and the new test into
`.agent-work/w3a-465/g1-review/red-repro/`, reverted **only** `save()` to its exact HEAD text-mode
form, and left every other change in place. The revert was verified character-identical to
`git show HEAD:scripts/checklist_engine.py` after newline normalisation, with `_dominant_newline`
removed.

- **Platform:** `win32` / Windows 11 / Python 3.14.3 / pytest 9.0.2
- **Result:** 1 failed, 3 passed
- **The fixture that goes red:** `test_save_preserves_lf_line_endings` — the **LF** one

```
E       AssertionError: save() churned an LF file to CRLF (8 CRLF endings written)
E       assert 8 == 0
```

`test_save_preserves_crlf_line_endings` **passed** against that same broken `save()`. So on this
platform the CRLF fixture is exactly the test that proves nothing — and the test file's own module
docstring says so, in those terms, rather than hiding it.

**Negative control reproduced too.** A second scratch tree with `save()` replaced by the "just always
write LF" over-correction makes the CRLF fixture fail: `save() wrote no CRLF endings at all`. Both
fixtures are therefore demonstrated discriminating, each in the world where it is the discriminating
one. Neither test can pass identically in a healthy and a broken world.

**None of the three forbidden shapes is present.** `write_text` and `read_text` appear in this test
file **only inside docstrings explaining why they are forbidden**. Every fixture is built with
`write_bytes` (lines 81, 125); every assertion goes through `line_ending_counts()` on `read_bytes()`.
There is no saved-bytes-equals-fixture-bytes assertion — the assertions are scoped to two integers,
and the helper's docstring records that `indent=2` re-serialisation would make equality fail for the
wrong reason. Each test additionally asserts its **own fixture was born** with the endings it claims,
which is a durable guard against the degeneration rather than a one-time check.

**Criterion 7.** `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` → `1786 passed, 2 skipped, 682
subtests passed in 555.77s`, **real exit 0**. Output was redirected to a file, not piped, so `$?` is
pytest's own code with no `PIPESTATUS` ambiguity. `python`, never `py`, per #454. Counts match the
implementer's claim exactly.

## Code/doc quality

Good, and unusually disciplined in one respect worth naming: the survey affordance is narrowed to the
**one op that has a caller**, and the refusal text says the others are withheld "only because nothing
needs it yet." Capability added at the size of the demonstrated need, with the door documented rather
than pre-built.

The guard is placed **before** the op loop, which is what preserves the all-or-nothing contract — a
mixed delta is refused whole, and the test asserts the survey is left unmutated.

Fowler pass recorded at `.agent-work/w3a-465/g1-review/fowler-pass.json`;
`scripts/verify_fowler_pass.py` exits 0 (12 smells; flagged `long-method`, `shotgun-surgery`;
overridden `large-class`, `divergent-change`, `comments-as-deodorant`, each with the standard named
and the reason logged). Both flags are observations, filed as triage candidates below — neither is a
blocker and neither is this issue's job.

## Map impact verdict

- **Evidence supports claimed change:** Yes. Every claim I could reproduce, I reproduced; nothing
  rested on the transcript.
- **Constraints not violated:** Held, with one documented departure — see `tc1`.
- **Notes match the diff:** Yes. Signatures unchanged (`save(path, data)`,
  `amend(cl, delta, reason, authority, base_dir)`), no new module or seam, line numbers accurate
  (`_dominant_newline` 169–181, `save` 182–202). One imprecision: the diffstat quoted as "3 files,
  +62/−6" is the pre-extension shape, stale against the final 5-file +67/−11 — the scope-extension
  section explains why, so this is looseness rather than a wrong claim.
- **Decision candidates surfaced:** Yes. The scope extension was taken **up** to the Commander and
  ruled on, not self-granted.
- **Durable context routed:** Yes. The drift the implementer found is **closed in this diff**, not
  merely flagged; I re-grepped and there is no sixth site.

## Reconciliation check

Nothing needs Commander reconciliation. The only capability change is `amend`'s applicability widening
from gated-only to gated-plus-`retext-check`-on-a-survey, which is precisely what the reviewer
template's repair path now depends on — before this change that instruction named an action the engine
refused.

**Criterion 6, no sixth stale claim.** Two greps. The narrow one returns exactly two hits, both
correct: `docs/CHECKLIST_SCHEMA.md:280` uses "gated-only" about `add`/`drop`/`rescope`, which is true,
and `checklist_engine.py:2190` now says "gated and survey checklists". A wider sweep of every `amend`
mention intersected with gated/survey/only surfaces only `skills/commander/references/commander-core.md:46`,
which describes `amend` in the context of the commander's own **gated** `execute.json` and makes no
type-exclusivity claim, and `checklist_engine.py:405-409`, whose "only applies to" text is about
pending/in-progress **status**, not checklist type. No bundled second copy of either doc exists.

## Blockers

- None.

## Out-of-scope observations

Filed through the engine as `tc1`–`tc4`.

- **tc1 — `docs/agents/CREW_CONTEXT.md` "Writing Files On Windows" now has an unnamed exception.**
  It says pass `newline='\n'` on **every** write. The new `save()` writes bytes and may deliberately
  write CRLF. It satisfies the rule's stated intent more strongly than the prescribed mechanism does
  — explicit UTF-8, no translation layer at all — and the same section's next paragraph
  (".gitattributes sets `* text=auto`, so a checkout may legitimately hold CRLF") argues **for**
  preservation. Verified against the world: `core.autocrlf=true`, and the working-tree engine file
  holds 2883 CRLF / 0 LF while the HEAD blob holds 0 CRLF / 2827 LF. But a reader applying
  CREW_CONTEXT literally would read `save()` as violating repo doctrine. That is the same
  prose-contradicts-code defect class this issue exists to close, one tier up. CREW_CONTEXT is
  outside the allowed scope.
- **tc2 — `amend()` is 215 lines** (`checklist_engine.py:2158-2372`) and this change added ~29 more.
  Fowler long-method, **flagged not overridden**: `global-crew.md`'s "split a unit when its intent
  blurs" agrees with the smell rather than subordinating it. The per-op validation bodies are the
  natural extraction.
- **tc3 — `amend`'s type applicability is restated in six places** (engine guard, engine docstring,
  `docs/CHECKLIST_SCHEMA.md` ×4, `skills/workbench/references/checklist-engine.md`). Widening the
  verb by one op forced edits in all of them, and the first return shipped without the five prose
  sites. The structure guarantees the stale claim recurs on the next `amend` change.
- **tc4 — correction to the implementer's own tc3 count.** **Six** repo JSON writers pass `encoding`
  but not `newline='\n'`, not five: `scripts/install_constellation.py:1241` is missing from the list
  alongside `collect_feedback.py:290,365`, `install_constellation.py:911,1182` and
  `build_architecture_map.py:385`.

Two of the handoff's known out-of-scope items were re-verified so the Commander's triage is accurate,
**not** blocked on: the journal append is still text-mode (now `checklist_engine.py:2818`, not 2762 —
drifted by this diff's own +30 lines, same call); and the interrogator's `zc-consolidate` does carry
the identical `<interrogation-record-path>` placeholder in a command postcondition **and its template
is `type: "survey"`** — so this change already supplies the engine half of that fix, and only the
interrogator's prose is left to do.

## Workflow Feedback

- **Handoff gaps:** Close criterion 5 says "**Inspect** the `amendments` array on a survey you
  retext." There is no engine verb that prints `amendments` — `current` does not surface it — while
  `global-everyone.md` says opening a checklist JSON to read state is a **violation**. The criterion
  therefore instructs an action the doctrine forbids and the engine does not expose. I did the
  closest compliant thing: inspected the **probe** survey's JSON, an artifact under test rather than
  my own driven state, and left my own survey read only through `current`. The criterion should
  either name the probe route explicitly or the engine should grow an `amendments` view.
- **Context rediscovered:** The `--delta` file's **op schema**. The new `r6-fowler` imperative
  correctly says `amend --delta <file>` whose single op is `retext-check`, but never gives the op's
  key shape (`{"op","id","cond","which","command"}`). I recovered it from
  `docs/CHECKLIST_SCHEMA.md` and the new test. A reviewer on the repair path — already in a failure
  state — has to go find that. One clause naming the keys, or a pointer to the schema section, would
  close it; this is the last remaining "names a verb but not how to call it" gap in an item whose
  whole purpose is closing those.
- **Instructions improvised around:** Two. (1) The skill says never hand-write the survey file, but
  instantiating it from the template necessarily means writing it. The new imperative resolves that
  tension explicitly — "an instantiation-time substitution exactly like `<work-id>`" — and it worked;
  worth saying the fix landed. (2) Engine flag asymmetry: every mutating verb **requires**
  `--session-id` once a lease exists, but `current` **rejects** it with an argparse error. That cost
  me two failed calls. `current` accepting and ignoring it would remove a papercut every driven run
  hits.
- **What would have made this easier:** Name a **scratch location for reviewer reproduction trees**
  in the handoff. Reproducing the red honestly needs a whole scratch tree, and the negative control
  needs a second — I created `red-repro/`, `negctl/` and `probe/` under
  `.agent-work/w3a-465/g1-review/` by guess, while the skill separately warns about orphan untracked
  scratch. The implementer flagged this identical gap for their own tier and the handoff still did
  not carry it for mine, which is itself the `global-everyone.md` pattern: a fix scoped to one tier
  that never asks whether the tier above is exempt.

## Return status
`complete`
