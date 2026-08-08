# Review Handoff — gate `gb`: are these thresholds USEFUL, or just safe?

Issue #456. Invoke the `constellation-reviewer` skill, drive it to a plan, execute
it, return a `REVIEW_RESULT` with a verdict of `APPROVE` or `BLOCK`.

Implementation is commit `3a9b4495`; the crew's own account is at
`.agent-work/issue-456/crew-handoffs/gb-implement-RESULT.md`.

## What this gate committed

Four threshold families in the new `scripts/code_map/thresholds.py`, each a ratio
or a run-time invariant, each carrying a one-line "what to do when this fires":

| threshold | committed | measured |
|---|---|---|
| `HOLE_RATIO_CEILING` | **0.90** | 0.673 here, 0.572 on f1Brainz |
| `CHURN_RATIO_CEILING_LOCAL_EDIT` | **3.0** | **1.27x** |
| `CHURN_RATIO_CEILING_RENAME` | **3.0** | **1.02x** (first ever measurement) |
| `RECALL_FLOORS` | **1.0** for `calls`, `reads`, `writes` | 4/4, 4/4, 3/3 on an 11-edge hand fixture |
| `TEMPLATE_ASCII_INVARIANT` | invariant, not a ratio | AST scan of `render.py`'s own literals |

## The governing ruling — this is what you are reviewing against

The human ruled that a tripwire must be **USEFUL**: it must not send a future run
down a rabbit hole or make it climb an unnecessary speed bump. A threshold earns
its place only if tripping it means something is actually **WRONG**, not merely
changed. **Your central question is not "are these numbers correct?" — it is "will
these numbers ever tell anyone anything?"**

That cuts BOTH ways, and the second way is the one I want attacked hardest.

## Where to spend your budget — attack these

### 1. Are the loose ceilings so loose they can never fire? (HIGHEST VALUE)

`HOLE_RATIO_CEILING` is **0.90** against a measured **0.673**. Both churn ceilings
are **3.0** against measured **1.27x** and **1.02x**. That is a lot of headroom.

The run's own standing lesson is that **a check that cannot fail is exactly as
informationless as one that can only fail** — and this run has already been bitten
by BOTH halves (`tc38`, and `tc47` where a gate's own selector matched zero tests
and could never pass). A threshold set so far from reality that no realistic
regression reaches it is the first half of that lesson wearing a number.

So: for each loose ceiling, work out **what would actually have to go wrong** to
reach it, and judge whether that is a regression anyone would plausibly ship. The
crew claims a mutation proof for each. **Do not accept its mutation** — reproducing
a falsifier its author designed proves only that their probe works. Build your own,
and make it a *realistic* regression rather than a contrived catastrophe. If a
realistic bad change sails under the ceiling, that is a real finding.

Be fair, though: the ruling explicitly prefers a loose sharp tripwire over a
twitchy one, and the crew's framing of the hole ratio as "a canary for a
catastrophic extraction collapse, not a documentation-completeness gate" is a
legitimate design choice **if** it is stated and if the canary can still fire.
Judge the honesty of the framing, not just the size of the gap.

### 2. Is the rename-churn finding actually right?

This is the gate's headline and the first measurement of something the design
signed off as accepted-untested. The claim: a pure identifier rename changes one
line per call site on **both** sides of the ratio, so the diff-**lines** ratio
stays near 1x regardless of caller count — even though 217 of 3865 pages changed.

Attack the reasoning, not just the number. Is there a rename shape that breaks the
1:1 relationship? Consider at least: a rename that changes a symbol's **sort
position** (reordering caller lists), one that changes a **line's wrap or
length**, one that collides with an existing name, and a rename of something
referenced from **index/summary pages** rather than only entity pages. If any
realistic rename shape blows past 3x, the ceiling is wrong and this is a BLOCK.

Also verify the measurement procedure itself was sound — the crew says it used
isolated `git worktree add` copies and never the main worktree.

### 3. `RECALL_FLOORS = 1.0` — brittle, or correct?

A floor of **1.0** means *any* miss fires. Against a **fixed hand-labelled 11-edge
fixture** that is defensible (it is a fixture, not a sample of the corpus). But
check the wiring: does the check run against the **fixture**, or against the live
corpus? If it ever runs against live code, 1.0 is a speed bump that will fire on
healthy change and it must be blocked.

Also: `writes` has a floor of 1.0 even though the independent oracle is blind to
it. The crew says every predicate is derived the same way because no SCIP is
wired into this stdlib-only pipeline. Verify that claim and judge whether the
derivation is honestly stated — an unstated derivation is the defect, not a small
sample.

### 4. Does the template-ASCII invariant do what it claims?

It AST-scans `render.py`'s own literal `Constant` nodes, minus `render.py`'s own
docstrings, and never reads rendered pages — so it should be **structurally blind**
to the 386 pre-existing non-ASCII pages that reproduce source prose verbatim.

Verify both directions: (a) put a non-ASCII character into a real template literal
and confirm it **fires**; (b) confirm it does **not** fire on the 386 pages, and
does not fire on `render.py`'s own docstrings. The substring-match-against-
docstring-fragments approach was explicitly rejected as the twitchy version — check
that it did not sneak back in under another name.

### 5. Every threshold's "what to do when it fires" line

The ruling requires one, and requires it to be actionable. Read each. A line that
says "investigate" is noise. A line that names the file to open first is useful.

## What the Commander already verified — do NOT just reproduce these

- Suite **1793 passed, 2 skipped, 672 subtests, 0 failed** (baseline 1781 + the 12
  new methods).
- Closing selector `-k 'baseline or churn or recall or ascii'` on
  `tests/test_code_map.py` → **13 passed, exit 0**.
- Fresh `build` then `check` → **7/7, exit 0**.
- Committed explicit paths only; `git ls-tree -r HEAD -- map/` → **0**.

## A correction you should know about, because it was my error

My implement handoff told the crew the closing selector collected **17**. The crew
checked and it collected **1** — my scan had run the selector against the whole
`tests/` directory instead of the single file the gate's command actually targets.
The crew was right and I was wrong. That is the **seventh** time on this run a crew
has corrected a Commander instruction, every time by running the thing rather than
reading it. You are expected to do the same.

## Do NOT touch

- `is_test_module` and `SPLIT_LEGEND` in **both** hand-independent copies — just
  closed after a BLOCK.
- The two-independent-declarations design: `checks.py` re-declares the refs grammar
  and `is_test_module` **by hand**, never importing from `render.py`. Load-bearing
  and proven so. Never collapse into an import.
- `_make_collision_repo`'s `INDEX` collision (`g1`'s only cross-platform falsifier).
- `OWN_MODULE_NAMED_MUTATION` / `LEGEND_DROPPED_MUTATION` / `OWN_SITES_UNACCOUNTED_MUTATION`.
- `entity_symbol_join`'s two independent derivations (`g3`).
- `g4`'s `page_location_matches_content`.
- Page headers: path + `, N lines`, **no `:<line>`** — a direct human ruling.
- The 386 non-ASCII pages.

## Constraints

- Stdlib only. **No timings in any run report** — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,865-page `map/` tree is staged at `gs`.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- `C:/Programs/f1Brainz` is **READ-ONLY** (1227 modules / 15037 entities) — the only
  real second Python corpus, and the right place to check a ratio at another scale.
- `C:/Programs/superCoolSpaceSim` is C++/Obj-C with **zero** `.py` files — a **null
  test, never a shape test**.
- Use `python`, **never `py`**.
- The full suite takes ~6.5 minutes. Run it with `run_in_background` and let the
  completion notification wake you. **Do not poll a buffered output file** — every
  crew on this run that did so stalled and had to be nudged twice.
- **Shell quoting:** this worktree's Bash refuses long quoted strings, loops,
  `env -u`, heredocs, `$(...)`, and `VAR=x && ...` chaining. Use plain separate
  commands and script files. Dropping a redundant `cd` prefix often clears a refusal.
- **Context governor (`tc39`):** HARD band fires around 15% fill and refuses
  `advance` until you attach
  `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail id>`,
  read from the plan JSON. Every advance mints a new one — read and attach in the
  same breath. The `gb` implementer tripped it **four** times.
- **Fowler rail:** resolve `<fowler-pass-record-path>` to a real path **at
  instantiation, before `claim`**. The `g5` re-reviewer did that and needed no
  waiver — the first of six reviewers to get the normal path.

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/gb-review-RESULT.md`, with an explicit verdict
line of `APPROVE` or `BLOCK`.

**Do not end your turn with the RESULT file absent** — if blocked, write it anyway
with the blocker named. A partial result with an honest blocker beats silence.

**Return thin, write fat.**
