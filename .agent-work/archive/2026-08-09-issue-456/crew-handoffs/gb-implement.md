# Implementer Handoff — gate `gb`: commit the thresholds, once

Issue #456. Invoke the `constellation-implementer` skill, drive it to a plan,
execute it, return an `IMPLEMENTER_RESULT`.

## Why this gate exists

Every check this run has built so far can go red. What none of them have yet is a
**committed number** to go red *against*. This gate supplies those numbers, once,
and it is deliberately placed **after** the last render-changing gate.

The reason is critic F1: thresholds committed before `g3`/`g4`/`g5` would have
been invalidated three times, and the cheapest in-gate fix each time is to edit
the baseline — which quietly turns a real check back into the print-only
diagnostic this whole issue exists to replace. `g3` (schema), `g4` (index) and
`g5` (caller split) are all now closed. The render surface is frozen. **A
threshold that a later gate edits is not a threshold.**

## THE RULING THAT GOVERNS EVERY THRESHOLD HERE

This is the human's own ruling and it outranks any instinct toward completeness:

> A tripwire must be **USEFUL**. It must not send a future run down a rabbit hole
> or make it climb an unnecessary speed bump.

Concretely, and these are the acceptance rules for every number you commit:

1. **A threshold earns its place only if tripping it means something is actually
   WRONG.** Not "changed" — wrong.
2. **If it would fire on ordinary healthy change** — the corpus grew, a docstring
   was reworded, a page gained a line — **it is a speed bump. Drop it or widen
   it.** Do not ship it and plan to waive it routinely; a routinely-waived
   threshold is worse than no threshold, because it trains everyone to waive.
3. **Prefer FEW SHARP tripwires over MANY TWITCHY ones.** You will be reviewed on
   whether you dropped things, not on coverage. Dropping a threshold you cannot
   justify is a success here, not a gap — say so explicitly in your RESULT.
4. **Every threshold must state, in one line, what a human should DO when it
   fires.** A tripwire with no action is noise. Ship that line next to the
   number, in the code, where whoever sees the failure will read it.

## NO ABSOLUTE COUNTS — and here is the proof (critic F4)

**Express every threshold as a ratio or a run-time invariant. Never an absolute
count.** This is not theoretical. *This run adds `.py` files to the corpus it
measures.* Concretely, `g5`'s remediation added one test method, and the map —
which self-indexes `tests/` — went from 3752 to 3753 entities and 3864 to 3865
pages. `g5`'s own crew hardcoded pre-remediation counts into a verification check
and it failed for exactly that reason.

So: `holes / entities`, not `holes < 12`. `churn_pages / changed_entities`, not
`churn_pages < 400`. If a number cannot be phrased as a ratio, phrase it as an
invariant that is true at any corpus size ("no page's own line count exceeds the
line count of the file it renders").

## The four threshold families to commit

### 1. Hole count
As a **ratio** against a run-time denominator (entities or pages), not a count.
State what a human does when it rises: which artifact to open first.

### 2. Template-ASCII by EXACT-LINE PROVENANCE
This one has a known trap and the trap is why the gate task words it so
precisely. **386 of the current pages are non-ASCII, and every single one was
traced to PRE-EXISTING docstring prose reproduced verbatim from source** — an
em-dash in `scripts/agent_work_root.py`. That is correct behaviour: the map must
not censor source text.

So the threshold must hold **the map's own template text** to ASCII while letting
**reproduced source text** through, and it must decide which is which by
**exact-line provenance** — i.e. does this rendered line originate from the
template, or is it a line the map copied out of a source file? **A substring
match against docstring fragments is explicitly rejected** as the mechanism: it
is the twitchy version that will fire on healthy change. If you cannot establish
provenance exactly, say so and propose the narrower invariant you *can* defend
rather than shipping the substring hack.

### 3. Edge recall per predicate, with a floor INCLUDING `writes`
Hand-label an edge sample **per predicate** and commit a **recall floor per
predicate**. `writes` gets a floor **too**, and this is the subtle part: the
independent oracle is **blind** to `writes`, so you cannot lean on the oracle to
justify that floor. Say plainly how you derived it and how confident it is. A
floor derived from a small hand sample is legitimate — an unstated one is not.

### 4. Churn ratio, 3x ceiling, on BOTH kinds of edit
Measure the churn ratio against a **3x ceiling**, and measure it on **two** edits:

- a **local edit** (the ordinary case), and
- the **adversarial widely-referenced-symbol rename**.

**The rename has NEVER been measured.** At confirm it was human-signed as
*accepted-untested*. This gate measures it for the first time, so treat the 3x
ceiling as a **hypothesis you are testing**, not a number you are confirming. If
the rename blows through 3x, that is a real finding and I want it as a finding —
do **not** quietly widen the ceiling to make it pass, and do not quietly drop the
rename because it is inconvenient. Report the measured ratio for both edits.

## Close criteria

- Every threshold committed as a **ratio or run-time invariant**, never a count.
- Every threshold carries its **one-line "what to do when this fires"**.
- Any threshold you **dropped or widened** under the ruling is named, with why.
- Churn measured on **both** a local edit and the widely-referenced-symbol rename,
  both ratios reported, the 3x ceiling explicitly confirmed or falsified.
- Template-ASCII decided by **exact-line provenance**, not substring matching.
- A recall floor exists for **every** predicate including `writes`, each with its
  derivation stated.
- **FULL suite green** at this gate boundary (critic F6).
- Fresh `build` then `check` → 7/7, exit 0.

## Your closing selector — this gate will be CLOSED against it (`tc38`, `tc47`)

```
python -m pytest tests/test_code_map.py -k 'baseline or churn or recall or ascii' -q --color=no
```

**It collects 17 tests today and they pass.** Your new threshold tests must be
named so they are caught by this selector — `baseline`, `churn`, `recall` or
`ascii` must appear in the test name. Run the selector by hand and report its
count and exit code, before and after.

This is not pedantry. At `g5` the plan's closing selector named `caller_split`
while the crew created `ProductionTestCallerSplitTests`; the selector matched
**zero** tests, pytest exited 5, and the mismatch was invisible until the gate
tried to close — surviving a whole gate, a BLOCK, a remediation and a re-review.
Do not recreate that. A check that can only ever FAIL is exactly as
informationless as one that cannot fail, and it looks like diligence.

## Do NOT touch

- `is_test_module`'s predicate, and `SPLIT_LEGEND` in **both** hand-independent
  copies (`render.py:361`, `checks.py:301`) — just closed after a BLOCK.
- The two-independent-declarations design: `checks.py` re-declares the refs
  grammar and `is_test_module` **by hand** rather than importing from `render.py`.
  This is load-bearing and proven so — diverging only `checks.py`'s copy makes two
  independent checks go red. **Never collapse them into an import.**
- `_make_collision_repo`'s `INDEX` collision — `g1`'s only cross-platform
  falsifier for `page-accounting`.
- `OWN_MODULE_NAMED_MUTATION` / `LEGEND_DROPPED_MUTATION` / `OWN_SITES_UNACCOUNTED_MUTATION`.
- `entity_symbol_join`'s two independent derivations (`g3`'s whole gate).
- `g4`'s `page_location_matches_content`.
- Page headers: path + `, N lines`, **no `:<line>`**. A direct human ruling. 0 of
  3865 headers carry a line position; three pages contain a `.py:<line>` string
  inside docstring prose copied from source, which is correct — do not "fix" it.
- The 386 non-ASCII pages themselves. You are building the *threshold* that
  reasons about them; you are not editing them.

## Constraints

- Stdlib only. **No timings in any run report** — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,865-page `map/` tree is staged at the
  final gate `gs`. Stage explicit paths only.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- `C:/Programs/f1Brainz` is **READ-ONLY** — 1227 modules / 15037 entities, the
  only real second Python corpus, and your best check that a ratio holds at a
  different scale. **Use it for exactly that.**
- `C:/Programs/superCoolSpaceSim` is C++/Obj-C with **zero** tracked `.py` files —
  it indexes to 0 modules. It is a **null test, never a shape test**. A ratio with
  a zero denominator there is not evidence.
- Use `python`, **never `py`** (`py -m pytest` dies "No module named pytest" and
  reads as a silently green run).
- The full suite takes ~6 minutes. Run it with `run_in_background` and let the
  completion notification wake you. **Do not poll a buffered output file** — every
  crew on this run that did so stalled and had to be nudged twice.
- **Shell quoting:** this worktree's Bash refuses long quoted strings, loops,
  `env -u`, heredocs, `$(...)`, and `VAR=x && ...` chaining. Use plain separate
  commands, script files, `git commit -F <file>`. Dropping a redundant `cd` prefix
  often resolves a refusal on its own.
- **Context governor (`tc39`):** the HARD band fires around 15% fill and refuses
  `advance` until you attach a refresh-request:
  `attach <item> --type refresh-request --field seam=<item> --field why_ref=<id>`
  where `<id>` is the **current latest** `why_trail[-1].id` read from the plan
  JSON. Every `advance` mints a new one, so a cited id goes stale instantly — read
  it and attach in the same breath. Every crew on this run has hit this.

## Baseline entering this gate

Commit `c1fccdd8`. Modules **111**, entities **3753**, pages **3865**. Fresh
`build` then `check` → **7/7 exit 0**. Suite **1781 passed, 2 skipped, 672
subtests, 0 failed**. Closing selector collects **17**.

Useful measured context for your thresholds: the corrected production/test split
is unused **88** prod-defined / **2341** test-defined, test-only **2** / 449,
production **873** / 0. Genuinely unused production code is **88** — the naive
2429 headline is 96.4% test code.

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/gb-implement-RESULT.md`.

**Do not end your turn with the RESULT file absent** — if blocked, write it anyway
with the blocker named. A partial result with an honest blocker beats silence.

## You are expected to overrule this handoff if you can falsify it

Six times on this run a crew has proven a Commander instruction wrong, every time
by **running the thing rather than reading it**. This gate especially: I have
written down four threshold families, but the ruling above says a threshold that
would fire on healthy change must be **dropped**. If one of my four cannot be made
sharp, the right answer is to drop it and tell me — not to ship a twitchy version
because I listed it.

**Return thin, write fat.**
