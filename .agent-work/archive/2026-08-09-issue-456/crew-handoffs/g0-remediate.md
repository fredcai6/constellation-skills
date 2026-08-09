# Remediation Handoff — gate `g0`, blockers B1 and B2

Issue #456. The `g0` reviewer returned **BLOCK** on two findings. **Both are
yours** — the human answered B1 while this handoff was being written.

Full review: `.agent-work/issue-456/crew-handoffs/g0-review-RESULT.md`.

## The defect

`scripts/code_map/render.py:397-419` increments `npages` once per `write_text()`
**call**, not once per **distinct output path**. So the `pages` field in
`.code-map/render_report.json` is identical in a healthy world and in a world
where pages silently overwrite each other. It is a number that cannot go wrong.

It is wrong right now, and I confirmed all three figures myself:

| source | count |
|---|---|
| `render_report.json` `"pages"` | **3636** |
| `.md` files on disk under `map/` | **3635** |
| this gate's own `checks.py`, `pages scanned:` | **3635** |

The cause is a real lost page. `scripts/run_skill_eval.py` defines
`class Verdict` (line 178) and `def verdict` (line 407). `render.py:405` derives
the filename from `key.split(":", 1)[1]` with no collision check and no case
check, so both target `map/scripts.run_skill_eval/Verdict.md`. This filesystem
is case-insensitive and so is CI's `windows-latest`. The **function** wins; the
class page is unreachable while the module `INDEX.md` still links to it.

**No test in `tests/` reads any of the three run reports.**

## B1 — the human's answer, and the ruling I derived from it

Every rendered page header currently carries a source position:
`scripts/code_map/render.py:171-176` (`loc()`) emits
`"<file>:<line>, <N> lines"`, and `render.py:306` does the same for module
indexes. **3523 of 3635 pages** carry a `.py:<line>`. This contradicts the
confirmed ruling *"nothing committed carries a position"*, which is the recorded
disposition of **SY1, a BLOCKING critic finding** settled by the human at the
confirm gate. The step that would have removed it was lost when the plan was cut
to nine gates.

Asked to choose, the human said: **"strip the line numbers."** Option (a).

**It is done HERE, in `g0`, not deferred to a later gate.** The reviewer's whole
argument for blocking was that `map/` is committed at `gs`, the last of eleven —
finding this there means eight gates of downstream work built on a page format
that has to change. `g0` is the gate that ships the renderer, so `g0` fixes it.

**Ruling on exactly what "the line numbers" means** — apply this literally:

- **REMOVE the `:<line>` component.** This is the churn SY1 measured: a 3-line
  source edit shifts every entity below it in the file, rewriting ~450
  position-bearing lines across unrelated pages. That is the poison.
- **KEEP the bare file path**, e.g. `scripts/run_skill_eval.py`. A path is not a
  position — it changes only when the file moves, so it does not churn.
- **KEEP `, N lines`.** An entity's own size changes only that entity's own page.
  A page changing when its own subject changes is correct behavior, not churn.

**No new cache is needed and you must not build one.** I verified this myself:
`.code-map/statements.jsonl` already carries per-statement `{file, line, col}`
and is already gitignored at `.gitignore:29`. The rebuildable position store the
ruling calls for **already exists**. Your job is removal plus a test, nothing
more.

**Add a test that can go red:** assert that **no** rendered page under the output
tree matches a `.py:<line>` position pattern. Prove it load-bearing the same way
as below — restore the suffix, watch it fail, capture it, remove it again.

## Your task — three changes, nothing more

### 1. Make the count honest

`pages` must count **distinct output paths actually written**, not write calls.
After the fix, a fresh build of this repo must report `pages` equal to the number
of `.md` files on disk.

Decide for yourself whether to count a set of resolved paths or to count files
after the fact — but the number must become **incapable of disagreeing with the
tree**, which is the whole point.

### 2. Add a test that can actually go red

A test that **reads `render_report.json`** and asserts its `pages` field equals
the count of `.md` files in the rendered tree. Build into a **temp tree** — do
not touch the real `map/`.

**Prove it is load-bearing before you call it done.** Port the defect back
(restore the write-call counting), watch the new test go RED, capture that
output, restore the fix, watch it go GREEN, capture that too. A test you did not
watch fail is not evidence. Paste both runs in your result.

### 3. Strip the line number from page headers, plus its own test

Specified in full in the **B1** section above. Same evidence bar: restore the
suffix, watch the new test go RED, capture it, remove it again, capture GREEN.

## Explicitly NOT yours

- **Do not fix the `Verdict`/`verdict` collision.** Renaming is a symbol-identity
  question and `g2` owns symbol identity. Detection is already filed as `tc17`
  and assigned to `g1`, whose charter is a check stage that can fail. Your fix
  makes the count honest; it does **not** make the collision go away, and after
  your change the report will legitimately read **3635**, matching the tree,
  with the page still lost. **That is the correct outcome of this pass.**
- **Do not build a position cache.** It already exists — see B1 above.
- **Do not remove the file path or the `N lines` count** while stripping the
  line number. Read the B1 ruling again if you are tempted; the distinction
  between them is the whole reasoning.
- No other defect fixes, no schema changes. D1 is `g3`, D2 is `g2`, D3 and BOM
  are `g8`. Note D1 is the *line-base* defect and stays `g3`'s — stripping the
  suffix does not fix it and must not try to.

## Constraints that still bind

- **Stdlib only.** CI installs pytest and coverage and nothing else. One
  third-party import and the tool cannot run at all.
- **The run report carries no timings** — a determinism diff has to be able to
  cover it. Do not add one while you are in there.
- **Full suite green at the boundary.** The number to match or beat is
  **1706 passed, 2 skipped, 0 failed**.
- **Do NOT `git add -A`.** The untracked 3,635-page `map/` tree is staged at gate
  `gs`, deliberately last. Stage explicit paths. I made this mistake once already
  and had to fix it forward.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.

## Two environment traps that will otherwise cost you an hour

- The shell exports **`FORCE_COLOR=3`**. Pass `--color=no` to pytest whenever you
  intend to grep its output, or your greps silently match nothing. This exact
  trap already produced one false red on this run (`tc3`).
- The shell exports **`PYTHONIOENCODING=utf-8:surrogateescape`**, which makes
  `tests/test_crew_launcher.py::LaunchTests::test_records_entry_before_launch_and_completes`
  fail. Filed as `tc7`, not yours. Clear the variable for an honest suite number.

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g0-remediate-RESULT.md`: what changed with
`file:line`, the RED and GREEN runs of the mutation proof with real output, the
before/after `pages` figure against the on-disk count, the full-suite number, and
anything you found that I did not ask about.

**Return thin, write fat** — your message back is the outcome, the deciding
evidence, and the path. Commit your work with **explicit paths** before you
finish.
