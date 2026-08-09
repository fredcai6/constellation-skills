# Implementer Handoff — gate `g6`: catch an authored tag that has gone stale

Issue #456. Invoke the `constellation-implementer` skill, drive it to a plan,
execute it, return an `IMPLEMENTER_RESULT`.

## The gate, in one sentence

Hash each tag's enclosing entity span at extraction; on rebuild, **flag any tag
whose anchor body changed while its text did not**, in the run report the reviewer
already reads.

## Why this gate exists — and why it is the run's central theme

The predecessor system's failure mode was an **authored layer that silently went
stale**: a human wrote a note about some code, the code moved on, and the note
kept being displayed as though it were still true. Critics IF4/TS8: without this,
the design ships that exact failure in a smaller box.

**You are building the same defence this run has already built twice, one layer
up.** At `g5` a printed legend claimed the split keyed on a top-level `tests`
package while the predicate matched anywhere — a stated rule that had drifted from
the applied rule, and nothing detected it. The remediation added a check that goes
red when the two disagree. `tc45`, `tc48` and `tc49` are all the same shape:
**something asserted drifting away from something applied, with no mechanism to
notice.** A stale tag is that defect in the authored layer, and this gate is the
mechanism that notices.

Staleness detection was **designed but never built**, and was human-signed
**accepted-untested** at confirm. **This is its first build.** Treat the design as
a hypothesis, not a specification handed down — if it does not survive contact,
say so.

## Resolve this FIRST, before designing: what tags actually exist today?

The gate task says "each tag" and the anchors name **"what constitutes a tag's
anchor body"** as this gate's open **decision**. Do not assume — establish it:

- **What is a "tag" in this pipeline right now?** Find the authored-layer construct
  the extractor already recognises. Note that `g7` is the *comment-tags* gate
  (`-k 'comment_tags'`), which strongly suggests the comment-tag surface is
  **built after you**. If the tag surface you need does not exist yet, say so
  plainly and build the mechanism against a **fixture** you construct, so `g7` can
  wire the real surface into it. **That is a legitimate outcome — not a blocker —
  but it must be stated, not silently worked around.**
- **What is the "anchor body"?** This is the decision you own. The enclosing entity
  span is the obvious candidate, and `g3` put the span in the schema precisely so
  it could be hashed. Say what you include and, more importantly, **what you
  exclude and why**.

## The hard design question — and the ruling that governs it

`gb` just committed the human's ruling and it governs you too:

> A tripwire must be **USEFUL**. It earns its place only if tripping it means
> something is actually **WRONG**. If it would fire on ordinary healthy change, it
> is a speed bump — drop it or widen it. Prefer few sharp tripwires over many
> twitchy ones.

A naive `hash(span_text)` is the twitchy version. It fires when someone reindents,
rewraps a line, renames an unrelated local, or adds a blank line — none of which
make the tag wrong. **A staleness flag that fires on every reformat will be
ignored within a week, and an ignored flag is worse than none, because it trains
people to ignore it.**

So: **normalise the anchor body before hashing**, and defend your normalisation.
Consider excluding pure whitespace/indentation changes and comment-only changes.
Consider whether the hash should cover the entity's **semantic** content (e.g. the
AST shape) rather than its literal text — an AST-based hash is immune to
reformatting by construction. **Whatever you choose, state the trade-off**: what
real staleness does your normalisation make invisible? An honest gap that is named
beats a hidden one.

Then state, in one line, **what a human should DO when a tag is flagged** — `gb`
requires this of every tripwire and it applies here.

## Where the flag goes

**Into the run report the reviewer already reads.** Do not invent a new channel, a
new file, or a new command. A staleness signal nobody is already looking at is a
signal nobody sees.

**The run report carries NO TIMINGS** — that is a hard constraint, because the
determinism diff covers the report and a timing makes every rebuild differ. Your
new line must be deterministic across two builds of an unchanged tree, or you
break `deterministic-rebuild`, which is one of the 7 checks.

## Close criteria

- Each tag's enclosing entity span is hashed **at extraction** and the hash
  persisted with the tag.
- On rebuild, a tag whose **anchor body changed while its text did not** is
  **flagged in the run report**.
- The flag does **not** fire on reformatting-only change — demonstrated, not
  asserted.
- Your normalisation choice and its **named blind spot** are stated.
- A one-line "what to do when this fires" ships with it.
- The run report stays **deterministic** and timing-free; `deterministic-rebuild`
  stays `ok`.
- **FULL suite green** at this gate boundary (critic F6).
- Fresh `build` then `check` → 7/7, exit 0.

## Your closing selector — this gate WILL be closed against it (`tc38`, `tc47`)

```
python -m pytest tests/test_code_map.py -k 'stale_tag' -q --color=no
```

**It collects ZERO tests today.** That is deliberate — it is a **specification**:
this gate must create at least one test whose name contains **`stale_tag`**. Name
your tests accordingly and **run the selector by hand**, reporting its count and
exit code before and after.

This matters concretely. At `g5` the plan's closing selector named `caller_split`
while the crew created `ProductionTestCallerSplitTests`; the selector matched zero
tests, pytest exited **5**, and the mismatch stayed invisible through an entire
gate, a BLOCK, a remediation and a re-review. **A check that can only ever FAIL is
exactly as informationless as one that cannot fail**, and it looks like diligence.

## Required evidence

- **red-before-green.** Commit your reproducer in its FAILING state first. Grade it
  honestly: **A** if it reproduces on real input today, **B** if it is red only by
  absence of the feature.
- The reformatting-immunity demonstration (a reformat that does **not** flag,
  alongside a real body change that **does**).
- Selector counts and exit codes, before and after.

## Do NOT touch

- `is_test_module` and `SPLIT_LEGEND` in **both** hand-independent copies.
- The two-independent-declarations design: `checks.py` re-declares the refs grammar
  and `is_test_module` **by hand**, never importing from `render.py`. Load-bearing
  and proven so — diverging only `checks.py`'s copy makes two independent checks go
  red. **Never collapse into an import.**
- `_make_collision_repo`'s `INDEX` collision — `g1`'s only cross-platform falsifier.
- `OWN_MODULE_NAMED_MUTATION` / `LEGEND_DROPPED_MUTATION` / `OWN_SITES_UNACCOUNTED_MUTATION`.
- `entity_symbol_join`'s two independent derivations (`g3`'s whole gate) — you
  depend on that join being trustworthy; do not weaken it.
- `g4`'s `page_location_matches_content`.
- `gb`'s committed thresholds in `scripts/code_map/thresholds.py`. If your work
  would change a committed number, **stop and say so** — a threshold a later gate
  edits is not a threshold, and that is the whole reason `gb` was placed where it
  was.
- Page headers: path + `, N lines`, **no `:<line>`** — a direct human ruling.
- The 386 non-ASCII pages — pre-existing docstring prose, out of scope.

## Constraints

- Stdlib only. **No timings in any run report.**
- **Do NOT `git add -A`.** The untracked ~3,865-page `map/` tree is staged at `gs`.
  Stage explicit paths only. **Commit your own work** — the `gb` crew left its work
  uncommitted and the Commander had to do it.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- `C:/Programs/f1Brainz` is **READ-ONLY** (1227 modules / 15037 entities) — the only
  real second Python corpus.
- `C:/Programs/superCoolSpaceSim` is C++/Obj-C with **zero** `.py` files — a **null
  test, never a shape test**.
- Use `python`, **never `py`** (`py -m pytest` dies "No module named pytest" and
  reads as a silently green run).
- The full suite takes ~6.5 minutes. Run it with `run_in_background` and let the
  completion notification wake you. **Do not poll a buffered output file** — every
  crew on this run that did so stalled and had to be nudged twice.
- **Shell quoting:** this worktree's Bash refuses long quoted strings, loops,
  `env -u`, heredocs, `$(...)`, and `VAR=x && ...` chaining. Use plain separate
  commands and script files, and `git commit -F <file>`. Dropping a redundant `cd`
  prefix often clears a refusal.
- **Context governor (`tc39`):** the HARD band fires around 15% fill and refuses
  `advance` until you attach
  `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail id>`
  read from the plan JSON. Every advance mints a new one, so read it and attach in
  the same breath. The `gb` implementer tripped it **four** times and handled each
  by writing a full digest at the seam — do the same.

## Baseline entering this gate

Commit `5d8e9804`. Suite **1793 passed, 2 skipped, 672 subtests, 0 failed**. Fresh
`build` then `check` → **7/7 exit 0**. Modules **111**. Closing selector `stale_tag`
→ **0 collected** (by design, see above).

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g6-implement-RESULT.md`.

**Do not end your turn with the RESULT file absent** — if blocked, write it anyway
with the blocker named. A partial result with an honest blocker beats silence.

## You are expected to overrule this handoff if you can falsify it

**Eight** times on this run a crew has proven a Commander instruction wrong, every
time by **running the thing rather than reading it** — including twice in the last
two gates. This gate especially: staleness detection was signed off as
accepted-untested, so the design has never met reality. If hashing the entity span
turns out to be the wrong anchor, that is a finding worth more than a compliant
implementation.

**Return thin, write fat.**
