# Implementation Result

## Assigned gate
`w3a-465 / g1-implement` — issue #465, epic #418 wave 3, under Admiral launch order LO-465.

## Completed slice
Three coupled changes: `amend`'s `retext-check` op now runs on a survey; `save()` preserves the
file's existing line ending; the two reviewer prose corrections. Driven through my own gated plan at
`.agent-work/w3a-465/g1-implement/plan.json`, session `impl-w3a-465-g1`.

## Scope

**Files changed:**
- `scripts/checklist_engine.py` — two edits, nothing else:
  - new `_dominant_newline(path)` helper + rewritten `save()` (was line 169, now 169–202).
  - `amend()` — the opening type gate now admits `SURVEY`, its docstring names the survey rule, and a
    new pre-loop guard refuses a survey delta carrying any non-`retext-check` op.
- `skills/reviewer/templates/REVIEW_SURVEY.template.json` — `r6-fowler`'s imperative rewritten. The
  `<fowler-pass-record-path>` placeholder and the command postcondition are **unchanged**.
- `skills/reviewer/SKILL.md` — line 28 rewritten.
- `tests/test_engine_survey_retext_and_newlines.py` — new, the four required node ids.

**Specific exclusions touched:** no. Verified by command, not memory:
`git status --short tests/test_episode_negative_control.py scripts/hooks/gauge_writer_hook.py
tests/test_verify_spec_confirmed.py skills/interrogator/` → empty. `consolidate()` unchanged; the
journal append unchanged; no other engine refactoring. Diffstat: 3 files, +62/−6, plus the new test.

## Behavior changed

Yes, three ways.

1. **`amend` on a survey.** A delta whose ops are *all* `retext-check` is now applied to a survey
   checklist. `add`/`drop`/`rescope` still refuse, and the refusal says why:

   > amend on a survey accepts a retext-check-only delta; drop refused here. This is a CONSERVATIVE
   > choice, not a type-level impossibility: adding, dropping or rescoping a survey item is a
   > coherent thing to want, and it is refused only because nothing needs it yet. Split the
   > retext-check ops into their own delta, or raise the need with the authority named in your handoff.

   The guard sits *before* the op loop, so a mixed delta is refused whole — all-or-nothing holds, and
   a refused delta leaves the survey unmutated (asserted in the test).

2. **`save()` preserves line endings.** It serialises with LF, translates to the ending the target
   file already uses, and writes **bytes**. A file that does not exist yet, or one with **mixed**
   endings, gets LF — stated in the docstring. `json.dumps` escapes any literal CR, so the
   `b"\n"` → `b"\r\n"` translation cannot produce `b"\r\r\n"`; that reasoning is a comment in the code.

3. **Reviewer prose.** Both instructions now name actions the engine can perform.

## Evidence 1 — the line-ending test observed FAILING against the unmodified `save()`

**Platform: `win32`** (`python -c "import sys,os; print(sys.platform, os.name, os.linesep.encode())"`
→ `win32 nt b'\r\n'`).

**The fixture that went red: the LF one**, `test_save_preserves_lf_line_endings`. This is the
discriminating case on Windows: the old `write_text` already emitted CRLF here, so the CRLF fixture
passed in the broken world and the healthy one alike. Note the `F.` on the first line — the LF test
failed, the CRLF test passed, against the *same* unmodified `save()`. That asymmetry is the proof the
test is not vacuous.

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q \
    tests/test_engine_survey_retext_and_newlines.py::test_save_preserves_lf_line_endings \
    tests/test_engine_survey_retext_and_newlines.py::test_save_preserves_crlf_line_endings

F.                                                                       [100%]
================================== FAILURES ===================================
_____________________ test_save_preserves_lf_line_endings _____________________

tmp_path = WindowsPath('C:/Users/fredc/AppData/Local/Temp/pytest-of-fredc/pytest-5425/test_save_preserves_lf_line_en0')

    def test_save_preserves_lf_line_endings(tmp_path: Path):
        """An LF file stays LF after a save. On WINDOWS this is the discriminating
        case: the old text-mode `write_text` emitted the platform ending, so it
        rewrote every `\n` to `\r\n` and churned the whole file.

        Also pins the two documented LF defaults: a file that does not exist yet, and
        a file with MIXED endings, both get LF.
        """
        target = tmp_path / "lf.json"
        write_with_endings(target, b"\n")
        assert line_ending_counts(target.read_bytes())[0] == 0, "fixture was not born LF"

        E.save(target, {"work_id": "t", "type": "survey", "items": ["r1"], "tasks": {}})

        crlf, lf = line_ending_counts(target.read_bytes())
>       assert crlf == 0, f"save() churned an LF file to CRLF ({crlf} CRLF endings written)"
E       AssertionError: save() churned an LF file to CRLF (8 CRLF endings written)
E       assert 8 == 0

tests\test_engine_survey_retext_and_newlines.py:114: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_engine_survey_retext_and_newlines.py::test_save_preserves_lf_line_endings
1 failed, 1 passed in 0.43s
REAL EXIT=1
```

Captured at `.agent-work/w3a-465/red/newline-red.txt`.

**The three forbidden shapes, and how each is avoided:**

| forbidden shape | what this test does instead |
|---|---|
| LF fixture via `write_text` (born CRLF on Windows) | `write_with_endings()` uses `write_bytes`; each test also *asserts its fixture was born right* (`"fixture was not born LF"` / `"fixture was not born CRLF"`), so a future edit that reintroduces `write_text` fails loudly instead of degenerating |
| asserting on `read_text()` | every assertion goes through `line_ending_counts(raw)` on `read_bytes()` |
| asserting saved bytes == fixture bytes | the assertion is scoped to two integers, `(crlf_count, bare_lf_count)`; the docstring on `line_ending_counts` says why equality would fail for the wrong reason |

**Negative control on the CRLF fixture** — the LF fixture proved itself by going red, so I proved the
CRLF one the only other way available: I ran it against the obvious over-correction (`save` that
always writes LF) and confirmed it catches that too. Both fixtures are therefore known-discriminating,
not just known-passing.

```
$ python /tmp/negctl.py
negative control OK -- crlf test catches always-LF: save() wrote no CRLF endings at all
```

## Evidence 2 — the same test passing after the fix

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_engine_survey_retext_and_newlines.py
....                                                                     [100%]
4 passed in 0.53s
REAL EXIT=0
```

The two amend node ids were also observed red first, before `amend()` was touched
(`.agent-work/w3a-465/red/amend-unit-red.txt`):

```
>           assert name in msg, f"{name}: refusal must name the op that was refused -- got {msg!r}"
E           AssertionError: add: refusal must name the op that was refused -- got 'amend applies to gated checklists'
E           assert 'add' in 'amend applies to gated checklists'
...
FAILED tests/test_engine_survey_retext_and_newlines.py::test_retext_check_works_on_a_survey
FAILED tests/test_engine_survey_retext_and_newlines.py::test_add_drop_rescope_still_refuse_a_survey
2 failed in 0.49s
REAL EXIT=1
```

## Evidence 3 — `amend --op retext-check` on a REAL survey, and the three ops still refusing

Not a unit fixture: a survey instantiated from the **shipped** `REVIEW_SURVEY.template.json`, with a
**real** Fowler-pass record the rail actually accepts, driven through the engine CLI. Step 1
reproduces captured RED 2 exactly; step 3 is the whole point of the change — after the engine-driven
repair the reviewer can record its own pass. Full transcript at
`.agent-work/w3a-465/g1-implement/evidence/live-amend-cli.txt`. Exit codes captured from the command,
not from a pipe.

```
### platform
win32

### 0. claim the REAL survey lease (instantiated from the SHIPPED reviewer template)
claimed lease live-w3a-465 -> active
REAL exit=0

### 1. record r6-fowler pass with the SHIPPED placeholder still in the check -- reproduces captured RED 2
REFUSED: r6-fowler: command postconditions unmet ['c1']; cannot record pass Recovery: fix the underlying issue so postcondition c1 passes, then retry record r6-fowler. Do not edit the JSON — use the engine.
REAL exit=1

### 2. amend --op retext-check on the SURVEY -- the change under test
amended: retext-check r6-fowler.c1 (authority Commander w3a-465 (LO-465))
REAL exit=0

### 3. record r6-fowler pass again -- the corrected check now runs and passes
r6-fowler recorded pass: Fowler pass clean
REAL exit=0

### 4. add / drop / rescope on the SAME survey -- still refused
--- drop ---
REFUSED: amend on a survey accepts a retext-check-only delta; drop refused here. This is a CONSERVATIVE choice, not a type-level impossibility: adding, dropping or rescoping a survey item is a coherent thing to want, and it is refused only because nothing needs it yet. Split the retext-check ops into their own delta, or raise the need with the authority named in your handoff.
REAL exit=1
--- add ---
REFUSED: amend on a survey accepts a retext-check-only delta; add refused here. This is a CONSERVATIVE choice, not a type-level impossibility: adding, dropping or rescoping a survey item is a coherent thing to want, and it is refused only because nothing needs it yet. Split the retext-check ops into their own delta, or raise the need with the authority named in your handoff.
REAL exit=1
--- rescope ---
REFUSED: amend on a survey accepts a retext-check-only delta; rescope refused here. This is a CONSERVATIVE choice, not a type-level impossibility: adding, dropping or rescoping a survey item is a coherent thing to want, and it is refused only because nothing needs it yet. Split the retext-check ops into their own delta, or raise the need with the authority named in your handoff.
REAL exit=1

### 5. release
released lease live-w3a-465
REAL exit=0
```

**A second, unplanned live proof.** My own plan's `m3` check text grepped for `instantiate`
case-sensitively while the template says `INSTANTIATE` — an error in my *check*, not in the prose. I
repaired it the way the new prose tells a reviewer to: `amend --delta` with a single `retext-check`
op, never by hand.

```
amended: retext-check m3-reviewer-prose.c1 (authority Commander w3a-465 (LO-465))
REAL exit=0
m3-reviewer-prose -> complete
REAL exit=0
```

## Evidence 4 — full suite, real exit code

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
...
1786 passed, 2 skipped, 682 subtests passed in 481.81s (0:08:01)
REAL EXIT=0
```

`REAL EXIT` is `${PIPESTATUS[0]}`, not `$?` — the run was piped through `tee`. Captured at
`.agent-work/w3a-465/g1-implement/evidence/full-suite.txt`.

## Map Impact

- **Structural anchors touched:** `scripts/checklist_engine.py` — `save()` (function level, rewritten
  + new sibling `_dominant_newline`) and `amend()` (function level, type gate + one new guard). No
  new module, no new seam, no signature change: `save(path, data) -> None` and
  `amend(cl, delta, reason, authority, base_dir)` are unchanged, so no caller moves.
- **Capabilities added/changed/affected:** the `amend` verb's applicability widens from *gated only*
  to *gated, plus retext-check-only on a survey*. This is the capability the reviewer skill's repair
  path now depends on — before this change that instruction named an action the engine could not
  perform. `save()` gains a preservation guarantee it did not have.
- **Constraints/assumptions touched:** honors `docs/agents/CREW_CONTEXT.md` §"Writing Files On
  Windows" (never let default newline translation reach a file the repo will diff) — `save()` was a
  standing violation of a rule the project had already written down. Newly relied on: `json.dumps`
  emits no literal CR, which is what makes the byte-level translation safe.
- **Decision candidates / resolved decisions:** *mixed endings normalise to LF* was decided by the
  handoff, not by me. Two decisions were mine, both inside latitude: (a) the survey guard sits before
  the op loop, so a mixed delta is refused whole rather than partially applied — this preserves the
  existing all-or-nothing contract; (b) the unknown-type message widened to "gated and survey
  checklists", since a third type would otherwise get a message naming only `gated`.
- **Claims/evidence produced:** four new test node ids pin both behaviors; both line-ending fixtures
  are demonstrated discriminating (one by observed red, one by negative control); the live CLI
  transcript shows the reviewer's repair path working end to end on the shipped template.
- **Trust limitations / drift found:** **the docs now contradict the code.** Five places assert
  `amend` is gated-only — `docs/CHECKLIST_SCHEMA.md:43,63,280,372` and
  `skills/workbench/references/checklist-engine.md:62` — all outside this issue's allowed scope.
  Enumerated by `grep`, not memory. This matters more than a stale sentence usually would: the
  reviewer template I just edited *tells a reviewer to run `amend` on a survey*, and the schema doc
  tells the same reviewer that is impossible. Flagged as `tc1`.
- **Triage candidates:** filed through the engine as `tc1`–`tc4` (see below).

## Test mode
**Required:** `test-first` (the handoff mandates observing red first).
**Satisfied:** yes. All four node ids were written and observed failing before the code that makes
them pass was touched — the line-ending pair against the unmodified `save()`, the amend pair against
the unmodified `amend()`.

## TDD evidence, if required
- Failing test observed: yes, both pairs — Evidence 1 and Evidence 2 above.
- Passing test observed: yes — `4 passed`, then the full suite.
- Refactor while green: one, small. After the first red I reordered two assertions in the LF test so
  the failure names the real defect (`save() churned an LF file to CRLF (8 CRLF endings written)`)
  rather than the misleading downstream symptom (`save() wrote no line endings at all` — true, but
  only because every `\n` had become `\r\n`). Red re-observed after the reorder, and that is the
  output pasted above.

## Docs/contracts touched
- `skills/reviewer/SKILL.md` and `skills/reviewer/templates/REVIEW_SURVEY.template.json` — in scope.
- `docs/CHECKLIST_SCHEMA.md` and `skills/workbench/references/checklist-engine.md` — **corrected**
  under the Commander-authorised scope extension below. (At first return these were untouched and
  raised as `tc1`; the Commander then ruled to fix rather than defer.)

## Assumptions
- The four node ids are module-level pytest functions. Confirmed against the gate's own check command
  (`tests/test_engine_survey_retext_and_newlines.py::test_...`), not guessed.
- `--authority` on a delegated run is the dispatching Commander string, `Commander w3a-465 (LO-465)`.
  The engine only enforces non-empty; the handoff names the Commander as the authority.

## Stop conditions hit
- None. Nothing required a block.

## Out-of-scope observations
Filed through the engine as triage candidates on `m4-integrate`:
- **tc1** — 5 places assert `amend` is gated-only and now contradict the code
  (`docs/CHECKLIST_SCHEMA.md:43,63,280,372`, `skills/workbench/references/checklist-engine.md:62`).
- **tc2** — the engine journal append is still text mode
  (`append_journal_entry`, `jp.open("a", encoding="utf-8")`, `newline=None`), so every journal line is
  CRLF on Windows and LF on POSIX. Same defect class as `save()`, explicitly fenced out by the handoff.
- **tc3** — five other repo JSON writers pass `encoding` but not `newline="\n"`, against
  CREW_CONTEXT's explicit rule: `scripts/collect_feedback.py:290,365`,
  `scripts/install_constellation.py:911,1182`, `scripts/build_architecture_map.py:385`. Only
  `scripts/file_issue_set.py:214` gets it right.
- **tc4** — `skills/interrogator` `zc-consolidate` carries the reviewer's open-fail defect word for
  word. Fenced out and already raised; restated because the reviewer half is now fixed and the two
  have diverged.

## Workflow Feedback

- **Handoff gaps:** two, both small.
  1. **The `amend` CLI has no `--op` flag.** "Required evidence" item 3 and the template instruction
     both say `amend --op retext-check`; ops live inside the `--delta` file. I wrote the true shape
     (`amend --delta <file>` whose single op is `retext-check`) into the shipped template rather than
     parroting a flag a reviewer would then fail to find. Flagging it because the same phrasing may
     be in the gate's own wording.
  2. **The handoff did not say where to put live-CLI scratch.** It names the result path and the red
     path but not a home for an evidence survey, its Fowler record, and four delta files. I used
     `.agent-work/w3a-465/g1-implement/evidence/`. A named scratch location would remove the guess —
     and it matters here, because the reviewer skill separately warns about orphan untracked scratch
     at the worktree root.
- **Context rediscovered:** the blast radius of the `amend` change. The handoff fenced scope tightly
  and listed exclusions, but nothing pointed at the five doc sites that assert the *old* behavior; I
  found them only by running the authoring-side enumeration from `global-everyone.md`. A handoff that
  relaxes a documented constraint could carry the doc sites it invalidates — the author of the fence
  is better placed to know them than the implementer inside it.
- **Instructions improvised around:** the plan template's `m1` note says to encode the TDD red as a
  `check: null` postcondition because a command check would run the by-design-failing test. Correct,
  but it leaves the red as a bare self-attestation. I attested it *and* captured the red output to
  `.agent-work/w3a-465/red/` so the claim is reproducible — the attestation alone would have been
  exactly the unverifiable assertion `global-everyone.md` §"Verify claimed side-effects" warns about.
  Worth making the template's default: attest the red, and name the file the output landed in.
- **What would have made this easier:** the discriminating-fixture reasoning ("on Windows the LF
  fixture is the red one, on POSIX they swap") was the single most valuable thing in the handoff and
  it is currently prose an implementer must hold. Making it a **test-side** invariant is cheap and
  durable — each fixture asserting it was *born* with the endings it claims, which is what I did. If
  that pattern is right, it belongs in crew doctrine, not in one handoff: a fixture that does not
  assert its own defective state is the general shape of a test that cannot fail.

## Scope extension — Commander-authorised, after the first return

Commander `w3a-465` ruled on `tc1` rather than deferring it, and extended the fence by exactly one
item. The Commander's reasoning: this dispatch exists to close prose/affordance gaps, so shipping a
fix that opens five *new* ones — docs saying `amend` is gated-only while the shipped reviewer template
tells a reviewer to run it on a survey — would be the same defect one tier up. The Commander is
flagging the fence extension in their own return. `tc2`, `tc3` and `tc4` were explicitly left alone
and are being passed up, not fixed.

Added to the plan as gate `m5-doc-correction` through `amend`. The plan was already `complete` and its
lease released, so it was re-claimed and amended — never hand-edited.

**Files changed under the extension:**
- `docs/CHECKLIST_SCHEMA.md` — 4 surgical claim corrections at lines 43, 63, 280, 372. Surrounding
  sections untouched.
- `skills/workbench/references/checklist-engine.md` — the `amend` entry in the verb list, line 62.

Each now says the same thing: `amend` applies to gated checklists; `retext-check` is additionally
available on a survey, where it is the **only** permitted op; `add`/`drop`/`rescope` stay gated-only
as a conservative choice, not a type-level impossibility. The workbench entry also gained the note
that ops live inside the `--delta` file and there is **no `--op` flag**, so the wrong shape is not
propagated from there either.

**Re-grep — no sixth site.** Run after the edits:

```
$ grep -rn "gated only\|gated checklists only\|gated-only" --include=*.md --include=*.py --include=*.json . \
    | grep -v "^./.agent-work" | grep -i amend

./docs/CHECKLIST_SCHEMA.md:280: ... `amend` applies to **gated** checklists; on a **survey**,
`retext-check` is additionally available and is the **only** permitted op — `add`/`drop`/`rescope`
stay gated-only, a conservative choice rather than a type-level impossibility, and the refusal says so.
```

One hit, and it is **my own new sentence**, using "gated-only" correctly — about `add`/`drop`/`rescope`,
which really are gated-only. No surviving site claims the *verb* is gated-only. I also confirmed the
correction cannot be evaded by a duplicate copy: `find . -name "checklist-engine.md"` and
`find . -name "CHECKLIST_SCHEMA.md"` each return exactly one path, so there is no bundled second copy
still carrying the stale claim.

**Template wording confirmed (Commander's item 3).** The shipped template already carries the true
invocation shape — the handoff's `amend --op retext-check` phrasing was never propagated into it.
Exact sentence:

> REPAIR PATH -- only if the record later moves or the path you substituted was wrong, correct it
> through the engine with `amend --delta <file>` whose single op is `retext-check` on this item's c1,
> never by hand-editing this survey. There, --authority is the dispatching Commander named in your
> reviewer handoff (never a string you invent), and --reason is why the path changed.

**Full suite re-run after the doc correction:**

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1786 passed, 2 skipped, 682 subtests passed in 481.68s (0:08:01)
REAL EXIT=0
```

`REAL EXIT` is `${PIPESTATUS[0]}`. Captured at
`.agent-work/w3a-465/g1-implement/evidence/full-suite-after-docs.txt`.

**Map Impact delta.** `docs/CHECKLIST_SCHEMA.md` and `skills/workbench/references/checklist-engine.md`
now match the engine's actual `amend` applicability. The drift recorded above under "Trust limitations
/ drift found" is **closed in this diff**, not merely flagged — `tc1` is resolved. `tc2`, `tc3` and
`tc4` remain open and are the Commander's to route.

## Return status
`complete`
