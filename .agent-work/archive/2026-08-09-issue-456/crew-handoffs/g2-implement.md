# Implementer Handoff — gate `g2`: symbol identity and page identity

Issue #456. Invoke the `constellation-implementer` skill and drive it to a plan,
then execute the plan. Return an `IMPLEMENTER_RESULT`.

## Task — THREE defects, not two

The gate spec names two. A third is ruled in scope by the Commander and is
explained below; take all three.

### (a) D2 — the enclosing METHOD is dropped from a nested symbol

`scripts/code_map/extract.py:500-501` and `:524-525`:

```python
sym = "%s:%s" % (self.mod, node.name) if not self.clsstack else \
      "%s:%s.%s" % (self.mod, self.clsstack[-1], node.name)
```

The name is built from `clsstack[-1]` whenever **any** class is on the stack,
regardless of how deep inside a method the definition sits. So a closure defined
inside `Class.test_x` is emitted as `mod:Class.<closure>` — the **method** name is
dropped, not the class. Two same-named closures in two methods of one class
collide into one symbol and **their caller sets union**, which is the part that
makes the map lie rather than merely look untidy.

**MEASURED on this repo: exactly 4 real collisions.** They are named
individually in `.agent-work/issue-456/reference/d2_collisions.txt`; the probe
that found them is `.agent-work/issue-456/reference/probe_d2.py` and it
simulates the extractor's actual rule. All four are same-depth siblings, e.g.

```
tests.test_feedback_tooling:InboxLifecycleTests.f
     <- tests.test_feedback_tooling:InboxLifecycleTests._filer.f
     <- tests.test_feedback_tooling:InboxLifecycleTests._recorder.f
```

**Write the failing test against those 4 NAMED collisions first.** "All N
resolve" is a vacuous close criterion — it passes on an empty set and it passes
if the extractor silently stops emitting nested definitions at all. Name them.

The second arm — a class defined inside a function, currently named as if it
were module-level — has **0 occurrences on this repo**. It is fixture-only, and
a gate that closed on "4 → 0" would ship that arm unwritten. Cover it with a
synthetic fixture and say plainly in your result that it has no real-corpus
instance here.

### (b) Referenced-by — the count and the list disagree, silently

The name list omits the defining module while the count includes it, and nothing
on the page states that the count already excludes definition, import, and
docstring mentions. So the map says 3 where `grep` says 7, **and the reader
cannot tell which is wrong** — that is the actual defect. Either number alone is
defensible; a page that shows both without saying what either means is not.

Two things must be true when you are done: the count and the list are derived so
they agree, and the page states in its own text what the count includes and
excludes. The issue itself notes this "ships with #2 — same line".

### (c) The page-filename case collision — RULED IN SCOPE, read this carefully

`scripts/code_map/render.py:414` writes each entity page as:

```python
(d / (key.split(":", 1)[1] + ".md")).write_text(...)
```

`scripts/run_skill_eval.py` declares both `class Verdict` and `def verdict`.
Their two distinct pages resolve to **one filename** on a case-insensitive
filesystem. The map advertises one more page than it holds; on this Windows box
one page silently overwrites the other.

This is not in the gate spec. It is in scope anyway, for two reasons you can
check yourself: `tests/test_code_map.py:917` states in its own words that **g2
renames**, and the assertion at `:982` is `xfail(CASE_INSENSITIVE_FS,
strict=True)` — so the moment you fix this, that test XPASSes, `strict` turns
the XPASS into a failure, and **you are forced to delete the marker**. That is
deliberate: the defect cannot be silently left behind. Deleting the marker is
part of your job, not a surprise.

**COMMANDER RULING — do not get this backwards.** Fix the **map's page naming**.
Do **NOT** rename `class Verdict` or `def verdict` in
`scripts/run_skill_eval.py`. Production symbols do not get renamed to suit the
tool that reads them. If you believe the ruling is wrong, say so in your result
with the evidence — do not just do it the other way.

Your disambiguation must be **general**, not a special case for these two names.
Prove that with a synthetic fixture containing a fresh case-only pair that has
nothing to do with `Verdict`. A fix that only resolves the pair you were shown is
a fix that cannot fail on the next pair.

## Protected intent

The map exists so a reader can answer cross-file questions cheaply and **trust
the answer**. Every one of these three defects is the same failure in a
different place: the map states something specific and confident that is not
true. A merged symbol, a count that disagrees with its own list, and a page that
overwrote another all read as authoritative. Fixing the number without making the
page say what the number means fixes nothing.

## Test mode — red before green, and the reproducer is committed failing

This gate's constraint is explicit: **the reproducer must be committed failing
first.** Follow the run's established `port-defective-then-fix` mechanism, the
same idiom as `tests/test_mutation_floor.py`: port the defect, capture RED with
the actual command output, fix, then commit a mutation entry proving the test
kills it.

Grade every falsifier **A** (reproduces on real input today) or **B** (red by
absence — the negative control *is* the falsifier), and say which.

## Close criteria — you are judged against these

- The 4 named D2 collisions resolve to 4 distinct symbols that each carry the
  enclosing **method** name, verified against
  `.agent-work/issue-456/reference/d2_collisions.txt` by name, not by count.
- The class-in-function arm has a synthetic test, with its 0-occurrence status
  stated.
- Referenced-by count and list agree, and the page states what the count
  excludes.
- Case-only page collisions are impossible by construction, proven with a
  synthetic pair unrelated to `Verdict`/`verdict`.
- The strict-xfail marker at `tests/test_code_map.py:982` is **deleted**, and
  `python -m scripts.code_map check` **exits 0** on this repository.
- **The FULL suite is green at this gate boundary** (this is an explicit gate
  constraint, not a nicety).

## Allowed scope

`scripts/code_map/extract.py`, `scripts/code_map/render.py`, and
`tests/test_code_map.py`. Touch other `scripts/code_map/` modules only where one
of the three fixes genuinely requires it, and say so.

## Specific exclusions

- Do **not** rename symbols in `scripts/run_skill_eval.py` or any other
  non-map source file. See the ruling above.
- Do **not** "fix" the page-accounting number by counting the rendered tree
  again. `tc24` corrects `tc18`: the root is the `sizes` list at
  `render.py:415`, which appends **per emit call** and feeds three fields. A
  second tree-count manufactures a second self-agreeing field and buys nothing —
  that is exactly the "expected value computed by the same expression as the
  thing under test" shape that got past two reviewers at `g0`.
- Do **not** touch the line base or the page header format. Both are settled
  elsewhere; the header format by the human's own ruling — headers carry path +
  `, N lines` and **no** `:<line>` position. Do not reintroduce positions.
- Do **not** weaken or delete any of the six checks `g1` shipped. If one of them
  now fails for a reason your change created, that is your bug, not its.
- No scope widening. Log anything else as an out-of-scope candidate in your
  result.

## Required evidence

For each of the three defects: the reproducer, its RED output with the exit
code, the fix, and its GREEN output. For (a), the before/after symbol strings for
all four named collisions. For (c), the synthetic case-only pair and proof the
disambiguation is general.

Then: full suite numbers in a cleared environment, and the `check` exit code.

## Verification commands

```
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/ -q
env -u FORCE_COLOR -u PYTHONIOENCODING python -m pytest tests/test_code_map.py -q
python -m scripts.code_map check
```

Baseline before this gate: **1729 passed, 2 skipped, 1 xfailed, 0 failed**.
After your change the xfail should be **gone**, so expect `1730+ passed,
2 skipped, 0 xfailed`. `check` currently exits **1**, correctly; after (c) it
must exit **0**. If your numbers differ from that shape, that is the headline of
your report, not a footnote.

## Constraints

- Stdlib only. No timings in any run report — it breaks the determinism diff.
- **Do NOT `git add -A`.** The untracked ~3,635-page `map/` tree is staged at the
  final gate. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- Work only in `C:/Programs/constellation-skills/.claude/worktrees/issue-456`.
- Restore byte-exact anything you mutate for a probe; prove `git status` is clean
  of stray edits at the end.
- Never force-push; do not merge to `main`.

## Environment traps — all three confirmed real on this run

`FORCE_COLOR=3` and possibly `PYTHONIOENCODING` are exported; clear both before
trusting any suite number. **Use `python`, NEVER `py`** — `py` has no pytest, so
`py -m pytest` dies with "No module named pytest" and reads as a silently green
run. That one already reached three command postconditions in another crew's plan
before it was caught.

## You are expected to overrule this handoff if you can falsify it

Twice on this run a crew has proven a Commander instruction wrong — most recently
by showing that a bare `xfail(strict=True)` would turn CI red on Linux while
looking correct on this Windows machine. Both times the crew was right, and both
times it found it by **running the thing rather than reading it**. If something
here is wrong, prove it and say so.

## Map anchors (inbound)

- **Map entry point:** `map/INDEX.md`, then `map/scripts.code_map.extract/` and
  `map/scripts.code_map.render/`
- structural: `scripts/code_map/` name-resolution and render modules
- capability: derive structure from source; answer cross-file questions cheaply
- constraint: checks must be able to fail
- decision: symbol identity for function-nested definitions — the enclosing
  METHOD must appear; durable, every consumer inherits it
- decision: referenced-by semantics — what the count includes vs what the list shows
- evidence: inbound-edge attribution — any page whose caller set differs from an
  independent full scan

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g2-implement-RESULT.md`. Per defect: the
reproducer, RED output + exit code, the fix, GREEN output, and the falsifier
grade (A or B). Then suite numbers, the `check` exit code, the deleted xfail
marker, and any out-of-scope candidates.

If you hit a context seam, park cleanly and hand off rather than pushing through.

**Return thin, write fat.**
