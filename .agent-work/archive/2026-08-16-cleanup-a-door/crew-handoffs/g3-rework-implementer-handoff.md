# Implementer Handoff — g3 REWORK (attempt 2)

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g3` — issue #603. **This is rework, not a fresh gate.** The substance of g3 is APPROVED and
reproduced. Two mechanical blockers remain.

## What is already done — do not redo it

`4e1f22cb` landed both halves and an independent reviewer reproduced every functional claim:

- unbound / empty / missing / not-a-file / unreadable all refuse, server alive, exit 0;
- bind-on-open through to a successful `claim`, in one process, no CLI;
- the regression suite red pre-fix (12 red);
- `tests/test_mcp_lifecycle.py:194` and its control byte-identical, new module-wide pin
  added with its own mutated control;
- `IdentityGuardSurvivesARebindTests` 17 passed;
- env overrides, lease-held refusal, unset `SPINE_ENGINE` — all reproduced.

**Do not re-litigate any of that.** Touch only what the two blockers name.

## Blocker 1 — the suite is red: `map/INDEX.md` is stale

```
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
AssertionError: ...ts: 84 modules, 4743 entities... != ...ts: 83 modules, 4710 entities...
```

**Mechanism, proven by the reviewer — you do not need to re-derive it.** `code_map`
enumerates via `git ls-files -- '*.py'`, i.e. **tracked files only**. The previous run's
suite evidence is stamped `07:19:27` and the commit is `07:27:11`: the map was rebuilt
**eight minutes before `tests/test_mcp_door_unbound.py` was staged**, so the "fresh build"
counted 83 test modules and matched the index it had just written. Staging the new file made
it tracked, and the same guard went red.

**Remedy, already measured at this exact commit:**

```bash
py -m scripts.code_map build --root .
```

The reviewer measured the result as **3 insertions, 2 deletions** to `map/INDEX.md`, after
which both `MapTreeFreshness` tests pass.

**The ordering rule this teaches, and the reason blocker 1 exists at all: stage first,
rebuild the map last, then commit.** A rebuild run while a new file is still untracked
passes its own guard, which is why this is invisible. This trap has now fired twice in this
run (g1 `0060dc08` and g3 `4e1f22cb`; g2 repaired g1's only incidentally). Do it in the
right order this time.

## Blocker 2 — three doc references stranded by this commit's own renames

This commit renamed or deleted three identifiers and left references behind:

| Location | Stranded reference |
|---|---|
| `scripts/mcp_spine_server.py:685` | `REJECTIONLOG` |
| `scripts/mcp_spine_server.py:962-963` | *"ambient `SPINE_FILE`, re-read fresh"* — no longer true |
| `examples/mcp-interactive-demo/README.md:69` | a renamed test |

Fix each to name what the code now actually does. Then **regenerate the two
`map/scripts.mcp_spine_server/` pages** — which happens naturally if you follow the ordering
rule above and rebuild the map last.

This is the inherited rule `global-everyone.md` states as *"enumerate the blast radius of
your own change — by command, never by memory."* **Apply it while fixing these:** run one
command that finds references to every identifier this commit renamed or deleted, and
**state the count**. Three were found by review; confirm there is no fourth.

## Close criteria

- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q` is **fully green** —
  paste the count.
- No stranded reference to any identifier this change renamed or deleted. **State the count
  from your own command**, not from this handoff's table of three.
- `map/INDEX.md` and `map/` are fresh **against the staged tree**, and committed.
- Nothing else about `4e1f22cb`'s behaviour changes.

## Allowed scope

- `map/**` — regenerate, do not hand-edit.
- `scripts/mcp_spine_server.py` — **docstrings and comments only.** No behaviour change.
- `examples/mcp-interactive-demo/README.md` — the stranded test name.

## Specific exclusions

- **Any behaviour change.** The functional work is approved and reproduced; this rework is
  documentation and a generated index. If you believe a behaviour change is required, that
  is a stop condition — say so and stop.
- `_identity_violation` — fenced by the launch order.
- `scripts/checklist_engine.py`, `scripts/hooks/**`, `scripts/run_crew.py`,
  `scripts/gauge_reader.py` — lanes B and C, running concurrently.
- `scripts/install_constellation.py` / `COMMANDER_SPINE.template.json` doctrine — the
  "door-detection change" is undefined and floated to the Admiral.
- The two triage candidates the reviewer **refuted by measurement** (the `SPINE_ENGINE`
  sibling-fallback claims). Do not act on them; they do not reproduce.

## Constraints

- **Order of operations: stage → rebuild map → commit.** This is blocker 1's whole lesson.
- **Clear `__pycache__` before the suite measurement**
  (`find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +`) — #597.
- Do **not** hand-edit anything under `map/`; it is generated.

## Map anchors (inbound)

Unchanged from `g3-implement` attempt 1. **Map entry point: none** — `map/ids.jsonl` is
tracked but empty. Relevant here: `scripts/mcp_spine_server.py:685`, `:962-963`;
`examples/mcp-interactive-demo/README.md:69`; `map/scripts.mcp_spine_server/`.

- **Decision anchors:** unchanged and already satisfied —
  `decision:one-spine-per-process-stands` `@grade: settled/human`,
  `decision:fail-closed-beats-fail-open` `@grade: settled/measured`,
  `decision:bind-on-open-over-new-verb` `@grade: guess`. This rework touches none of them.

## Deliverable path check

- **Committed** — `map/**`, `scripts/mcp_spine_server.py`,
  `examples/mcp-interactive-demo/README.md`. None ignored (`git check-ignore` exits 1).

## Required evidence

**Load-bearing:**

1. Full clean-env suite green, with the count.
2. Your blast-radius command and **its count** of stranded references, before and after.

**Confirmatory:**

3. `git diff --stat` for the rework commit — it should be small and touch only docs plus
   generated map pages.

## Wiring grep

`none — this rework adds no callable symbol.`

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
# stage everything first, THEN rebuild the map, THEN commit
py -m scripts.code_map build --root .
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

## Suggested model tier

`simple bounded` — both blockers are fully diagnosed with measured remedies. The only
judgment is the blast-radius sweep for a possible fourth stranded reference.

## Authority

Already decided: the remedy for blocker 1; that blocker 2's fixes are documentation-only;
that the refuted triage candidates are not acted on. Yours: the exact replacement wording
for the three doc references, and the shape of the blast-radius command.

## Stop conditions

Stop and return if: a behaviour change turns out to be required; the map rebuild does not
produce a green suite; your blast-radius sweep finds something that is not a doc reference;
or scope must be exceeded.

## Return format

Return `IMPLEMENTER_RESULT` with `Return status` one of
`complete | partial | blocked | out-of-scope | failed`, **lowercase**.

**Delivery.** Write it to
`.agent-work/cleanup-a-door/crew-handoffs/g3-rework-implementer-result.md` **before ending
your turn** — that write is the delivery.
