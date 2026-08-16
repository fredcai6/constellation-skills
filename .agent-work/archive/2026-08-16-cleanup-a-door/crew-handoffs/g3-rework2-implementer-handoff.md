# Implementer Handoff — g3 REWORK 2 (attempt 3)

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g3` — issue #603. **Rework 2 of a cap of 3.** One blocker. Text only.

## Everything else is done — do not touch it

Two independent reviews have reproduced the whole of `#603`: the six unbound-class refusals,
bind-on-open through to a successful `claim`, the regression suite red pre-fix,
`tests/test_mcp_lifecycle.py:194` byte-identical plus the new module-wide pin with its own
mutated control, `IdentityGuardSurvivesARebindTests`, the env overrides, the lease-held
rebind refusal. The full clean-env suite is green at `359d93df`
(**3093 passed, 6 skipped, 1153 subtests, 0 failed**).

**Change nothing but the one string below.**

## The blocker

`tests/test_mcp_lifecycle.py:201` — the pin's **failure message** still tells a future
debugger:

```
"purely on ambient, server-launch-time state (SPINE_FILE/SPINE_PARENT re-read "
"fresh) and never on the identity THIS door happens to be bound to, ..."
```

Measured against the AST at HEAD: `_spine_open` reads `SPINE_PARENT` from `os.environ`
**once** (still true) and `SPINE_FILE` **zero** times — because removing that read **is** the
#603 fix. So the parenthetical asserts something this change made false. It is the same
invalidated claim, in the same words, that rework 1 already fixed at
`scripts/mcp_spine_server.py:962-963`.

**Fix:** correct the parenthetical to name what `_spine_open` actually reads —
`SPINE_PARENT` re-read fresh, and the repo root from `_primary_checkout_for_lifecycle`,
which reads no environment at all.

**Do not change the surrounding claim.** That `spine_open` must never touch the bound
identity is still exactly right and is the reason the pin exists.

## Why it survived, and the part that matters more than the line

The rework-1 sweep ran a **line-based** `git grep` and found nothing, because the phrase is
assembled from **two adjacent string literals** and therefore appears on **no single line**:

```
git grep -F 're-read fresh'    ->  0 files, tree-wide
whitespace-normalized sweep    ->  1 file  (tests/test_mcp_lifecycle.py)
```

That is `docs/agents/CREW_CONTEXT.md`'s own warned hazard — *"a grep for a message string is
not a test of the branch that emits it"* — firing against the very sweep meant to enforce
the blast-radius rule. **The instance is one line; the hole in the method is what would
recur.**

So: when you re-run the blast-radius sweep to confirm you are done, **use a
whitespace-normalized or AST-aware sweep, not a line-based grep**, and say which you used.

## Close criteria

- `tests/test_mcp_lifecycle.py:201`'s message names what `_spine_open` actually reads.
- A **whitespace-normalized** (not line-based) sweep for the invalidated phrasing returns
  **zero** live in-scope hits. State the command and the count.
- Full clean-env suite still green — paste the count.
- `git diff` for this rework touches **exactly one file**.

## Allowed scope

`tests/test_mcp_lifecycle.py` — **the failure-message string only.**

## Specific exclusions

- **Any behaviour change, any test-logic change, any assertion change.** This is message
  text. If you believe anything else must change, that is a stop condition — say so and stop.
- **No `map/` rebuild** — no entity changes, so the map is unaffected. (If you somehow do
  change an entity, then stage first and rebuild the map **last**, per rework 1's lesson.)
- `tests/test_mcp_lifecycle.py:194` and its positive control — **byte-identical, fenced by
  two reviews.** Do not touch.
- `_identity_violation`; `scripts/checklist_engine.py`, `scripts/hooks/**`,
  `scripts/run_crew.py`, `scripts/gauge_reader.py` (lanes B and C, concurrent);
  `scripts/install_constellation.py` / `COMMANDER_SPINE.template.json` doctrine.
- **`scripts/hooks/spine_rail.py` carries a second invalidated claim — it is FENCED.** Do
  not fix it. It is being reported to the Admiral as a cross-lane consequence.

## Constraints

- Clear `__pycache__` before the suite measurement (#597).

## Map anchors (inbound)

Unchanged. **Map entry point: none** (`map/ids.jsonl` empty). Relevant:
`tests/test_mcp_lifecycle.py:194-210`. No decision anchor is touched by this rework.

## Deliverable path check

- **Committed** — `tests/test_mcp_lifecycle.py`; `git check-ignore` exits 1 (not ignored).

## Required evidence

1. The before/after of the corrected string.
2. Your whitespace-normalized sweep command and its count.
3. Full clean-env suite green, with the count.
4. `git diff --stat` showing exactly one file.

## Wiring grep

`none — this rework adds no callable symbol.`

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

## Suggested model tier

`simple bounded` — one string, fully specified. The only judgment is the sweep method.

## Authority

Already decided: the fix is text-only; the surrounding claim stays; the sweep must not be
line-based. Yours: the exact replacement wording, and the sweep's implementation.

## Stop conditions

Stop and return if a behaviour or assertion change turns out to be required, or if the sweep
finds an in-scope invalidated claim that is **not** a message string.

## Return format

`IMPLEMENTER_RESULT` with `Return status` one of
`complete | partial | blocked | out-of-scope | failed`, **lowercase**.

**Delivery.** Write it to
`.agent-work/cleanup-a-door/crew-handoffs/g3-rework2-implementer-result.md` **before ending
your turn**.
