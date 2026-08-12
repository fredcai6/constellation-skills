# Implementer Handoff — g3: the door

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g3` · **Role:** `implementer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g3-implementer-result.md`

## Read first

`.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` — **§6 is your specification.** Read §1b too.
Then read `scripts/mcp_spine_server.py`'s module docstring and `_identity_violation`'s docstring in full:
both are unusually explicit about *why* each guard is shaped the way it is, and this gate lives or dies on
respecting that.

`scripts/spine_lifecycle.py` already exists with `open_work` and `close_work` (g1, g2). **You are wiring
them to the door. You are not changing them.**

## Task

Add `spine_open` and `spine_close` to `scripts/mcp_spine_server.py`, plus `tests/test_mcp_lifecycle.py`.

### The shape — and the one rule that matters most

The two tools are dispatched from **`call_lifecycle_tool`, a NEW MODULE-LEVEL SIBLING of `call_tool`.**

**`call_tool`'s body is NOT TOUCHED.** Its choke-point pin
(`tests/test_mcp_identity.py::IdentityBindingPinTests::test_call_tool_can_only_produce_content_two_ways`)
resolves `call_tool`'s own `ast.FunctionDef` node and walks only that subtree, so a true sibling is
structurally outside it. That pin must remain **unmodified and green**.

`main()`'s `tools/call` branch (`scripts/mcp_spine_server.py:962`) routes every known name to `call_tool`
unconditionally, so **`main()` must grow a branch** sending the two lifecycle names to
`call_lifecycle_tool`. **Route in `main()`, never inside `call_tool`.**

- `spine_open` — takes `work_id`, `spec`, optional `base`. It **never references `SPINE`, `SESSION` or
  `run_engine`.** The repo root is derived from the bound spine's own worktree, never caller-supplied,
  matching the "ambient state is bound at server-launch time, not exposed as tool arguments" rule the rest
  of this door already lives by.
- `spine_close` — takes **no arguments at all**. It acts on the bound spine, full stop; there is no field
  to redirect because none exists.

Two tools, never one `action` switch: their identity postures are opposite, and folding them into one
function body is exactly the "a guard written for one hazard covers the other by accident" failure
`_identity_violation`'s own docstring records as history.

### THE TRAP — named here so it is not discovered mid-flight

Adding two entries to `TOOLS` breaks **three** coupled sites in **three** files. All verified on this base:

| Site | What breaks |
|---|---|
| `tests/test_mcp_identity.py:998-999` | iterates `module.TOOLS`, indexes `TOOL_MINIMAL_ARGS[tool["name"]]` → `KeyError` |
| `tests/test_mcp_adoption.py:236,246` | `set(DOOR_TOOL_NAMES) == server.TOOL_NAMES`, and `len(...) == 9` |
| `tests/test_crew_launcher.py:536,551` | derives the crew grant from `TOOL_NAMES`, asserts `len(...) == 9` |

The last two are **deliberate regression pins that exist because the door once grew from 7 to 9 tools
while a hand-typed list froze.** They are working as designed; updating them is the required work, not a
workaround. `test_crew_launcher.py:536` also means the two new tools must be added to
`run_crew.CREW_ALLOWED_TOOLS`, or a dispatched crew cannot call them.

**The required fix** is to scope the identity sweep to the engine tools
(`TOOL_NAMES - LIFECYCLE_TOOL_NAMES`) and update the two counts, `DOOR_TOOL_NAMES`, and the grant.

**The FORBIDDEN fix** is to handle `spine_open`/`spine_close` inside `call_tool` to make the sweep pass.
That is the exact regression the pin exists to catch, arriving disguised as test maintenance. If you find
yourself editing `call_tool`'s body, stop — you are doing the forbidden thing.

### The lifecycle surface gets its OWN containment pin

The existing pin was written for a pass-through door. A lifecycle tool is **not** a pass-through and must
not inherit a guard built for a different hazard. Ship, in `tests/test_mcp_lifecycle.py`:

1. An **AST pin over `call_lifecycle_tool`** restricting its return shapes the same way `call_tool`'s pin
   does, **with a mutated positive control** proving the pin can fail.
2. An assertion that `spine_open`'s dispatch path **never references** `SPINE`, `SESSION` or `run_engine`
   — this is what makes "it does not presuppose a bound spine" a checked fact rather than a claim. Include
   a mutated positive control.
3. Containment on every caller-supplied path, reusing `_resolve_confined`'s posture rather than a second
   predicate.

## Protected intent

`generate_spine.py` is reachable only from a shell today, and the standing human ruling is verbatim:
*"anything that we want to do for the spine needs to be accessible via mcp. the agents should not know
about the cli. period. anything that we can only do via the cli is a defect."* **This gate is what makes
the generator reachable at all.** And the door's one-spine binding is a safety property, not an
inconvenience — the new surface must not weaken it.

## Close criteria

1. `test_call_tool_can_only_produce_content_two_ways` is **unmodified** and green. (`git diff` it and show
   it is untouched.)
2. The AST pin over `call_lifecycle_tool` refuses a third return shape, with a mutated positive control.
3. A check proves `spine_open`'s path never references `SPINE`, `SESSION` or `run_engine`, with a mutated
   positive control.
4. A **full stdio JSON-RPC round trip**, in a throwaway git repo under `tmp_path`: `tools/call spine_open`
   creates a real worktree and spine; drive that spine to terminal; `tools/call spine_close` archives it;
   assert the readiness verdict names the branch, the commit, and **"ready to PR"**.
5. All three coupled sites updated; `tests/test_mcp_adoption.py` and `tests/test_crew_launcher.py` green.
6. `.mcp.json` is **not modified** — a tool is not a server. Show `git diff -- .mcp.json` is empty.
7. Suite green; `python scripts/validate_spine.py --sweep --root .` still exactly **23**.

## Allowed scope

`scripts/mcp_spine_server.py` · `tests/test_mcp_lifecycle.py` (new) · `tests/test_mcp_identity.py`
(sweep scoping only) · `tests/test_mcp_adoption.py` (`DOOR_TOOL_NAMES` and the count only) ·
`tests/test_crew_launcher.py` (the count only) · `scripts/run_crew.py` (`CREW_ALLOWED_TOOLS` only) ·
`map/` (regenerated, never hand-edited).

The test-file edits are **pre-authorized and expected** — they are the coupled sites above. Keep each edit
minimal and say in your result exactly what you changed and why.

## Specific exclusions

- **Do not change `scripts/spine_lifecycle.py`.** g1 and g2 shipped it and it is reviewed. If a g3 test
  proves it wrong, **say so** rather than quietly editing it.
- `scripts/generate_spine.py` is g4's and g5's.
- Do not touch `call_tool`'s body. Do not touch `_identity_violation`'s existing clauses.

## Constraints — a violation voids the gate

- **`settings.json`, `.mcp.json` and `docs/agents/*` untouched.** The harness refuses `Edit`/`Write` on
  `.mcp.json` for headless crews and **that guard is deliberate — an agent must not silently expand its
  own MCP-server trust. Do NOT route around a permission refusal with a `Bash` write. If you need
  something there, block and ask the Commander.**
- `checklist_engine.py`'s on-disk format unchanged. `validate_spine.py` unchanged.
- `skills/**` untouched — a different crew owns it. If something there must change, **block and say so.**
- **`encoding="utf-8", newline="\n"` on EVERY write** (`docs/agents/CREW_CONTEXT.md:43`); CI runs
  `windows-latest`. g1 was BLOCKed for exactly this.
- Never run `scripts/install_constellation.py`.
- No merge and no push to `main`. Never `git add -A`. Never two crews in one worktree.

## Deliverable path check

- **Committed** — `tests/test_mcp_lifecycle.py` (new; `git check-ignore` exits 1, verified) and every
  edited source/test file above.
- **Local-only** — your result artifact under `.agent-work/`; the Commander commits it.

## Required evidence

Load-bearing — prove rigorously:

1. The full stdio round trip (criterion 4), with the actual verdict text pasted.
2. Both mutated positive controls (criteria 2 and 3): the mutation, the test going red, and green again
   after restoring.
3. `git diff -- tests/test_mcp_identity.py` showing **only** the sweep scoping changed, and the
   choke-point pin untouched.

Confirmatory: the suite total, the sweep count, the empty `.mcp.json` diff.

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Use `python`, never `python3`. Note `tests/test_mcp_adoption.py` imports `mcp_spine_server` only inside a
test with a scratch env, because it reads `SPINE_FILE` at import time — follow that pattern, never a
module-scope import.

**Baseline before your change: 2875 passed, 3 skipped, 1121 subtests; sweep exactly 23.**

## Stop conditions

- A constraint above would have to be violated → **block**, name it, return. In particular, **if you
  believe `.mcp.json` must change, that is a block, not a workaround.**
- You cannot wire the tools without editing `call_tool`'s body → **block and say so.** That would refute a
  load-bearing plan measurement, and a measured negative is a complete deliverable.
- Two failed attempts at the same check → block rather than a third.
- **Never waive.** `spine_halt` with `action=block`, name what you cannot satisfy, and return.

## Return format

Write the result artifact at the path above **before ending your turn**. Carry a **`Return status`** field
whose value is exactly `complete` (lowercase) when done, the evidence above pasted verbatim, an explicit
list of every coupled-site edit you made, anything you could not do, and a short **Workflow Feedback**
section.
