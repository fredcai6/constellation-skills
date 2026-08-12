# Reviewer Handoff — g3: the door

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g3` · **Role:** `reviewer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g3-reviewer-result.md`

## The review standard this wave inherits — read it twice

C2's branch was reviewed **five** times. The first four each ran real commands, each answered its own
questions correctly, and each missed something different: a field that was never quoted (invisible because
**absent**); a stale session id on nine of nine gates (invisible because **ubiquitous**); that same id
written into a review's own evidence line **as proof of completeness**; and a divergence one reviewer saw,
described accurately, then **scoped away**.

**A review establishes that a mechanism operates and does not ask whether the value it carries is right.**
For every check: ask both questions. Treat your own green results as questions.

Already demonstrated on this run, twice: `g1`'s first review found a write missing `newline="\n"` that
every test passed over; and the Commander's own first check of this gate produced a **false positive** —
an AST substring scan said `_spine_open` referenced `SESSION`, when the hit was in a **docstring**. The
mechanism ran correctly and the value it reported was wrong. Assume something equivalent is in this diff.

## What was implemented

`spine_open` and `spine_close` on the already-registered `spine` MCP server, dispatched from
`call_lifecycle_tool` — a new module-level sibling of `call_tool`. **The crew committed its own work**
(`2f6b932e`, `5b082371`), which is unusual here; inspect the commits, not just the working tree:

```
git diff d0358a3d..HEAD --stat
git diff d0358a3d..HEAD -- scripts/mcp_spine_server.py
```

Its account is at `.agent-work/epic-559/c3-lifecycle/crew-handoffs/g3-implementer-result.md`. Read it
**after** forming your own view.

## The specification

`LIFECYCLE_CONTRACT.md` §6, and the handoff `g3-implementer-handoff.md`.

## What to verify — in this order

1. **`call_tool`'s body is byte-identical.** The forbidden fix was to handle the new tools inside
   `call_tool` to make the coupled sweep pass. Prove it independently — parse both revisions and compare
   the `call_tool` `FunctionDef`, do not eyeball the diff. (The Commander did this and got identical;
   confirm rather than trust.)
2. **`test_call_tool_can_only_produce_content_two_ways` is unmodified.**
3. **The `spine_open` path never references `SPINE`, `SESSION` or `run_engine` — in CODE, not prose.** The
   crew's own pin claims to check this. **Falsify it**: inject `_leak = SESSION` into `_spine_open`, run
   the pin, confirm red, restore. A guard you did not falsify is a guard you did not check. And check
   whether the pin itself can be fooled by a docstring mention, given that exact false positive happened.
4. **`spine_close` takes no arguments and cannot be redirected.** Is there any field, anywhere in its
   schema or handler, that steers which spine it acts on?
5. **The coupled sites.** The handoff named three; the crew found and edited a **fourth**
   (`tests/test_mcp_spine_server.py`). Enumerate every site that couples to `TOOLS`/`TOOL_NAMES`
   **by command**, state the count, and say whether the crew's set is complete. An under-inclusive
   enumeration presented as complete is the failure mode this wave is watching for.
6. **Are the updated pins still pins?** `test_mcp_adoption` and `test_crew_launcher` assert a tool count
   *because* the door once grew 7→9 while a hand-typed list froze. Do the edits preserve that protection,
   or do they now assert something that cannot fail?
7. **The full stdio JSON-RPC round trip** — does it really open a worktree and close it through the
   transport, or does it call the functions directly and call that a round trip?
8. `.mcp.json` is **not** modified. `scripts/spine_lifecycle.py` is **not** modified (g1/g2 own it).

## Constraints — check against the diff yourself

`checklist_engine.py` and `validate_spine.py` unchanged · `.mcp.json`, `settings.json`, `docs/agents/*`
untouched · `skills/**` untouched · `scripts/generate_spine.py` untouched (g4/g5) ·
`encoding="utf-8", newline="\n"` on every write (`docs/agents/CREW_CONTEXT.md:43`; CI runs
`windows-latest`) · no push to `main`.

## Evidence

Before g3: 2875 passed, 3 skipped, 1121 subtests; sweep 23.
After, reproduced by the Commander: **2884 passed, 3 skipped, 1121 subtests**; sweep **23**.

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

Use `python`, never `python3`. `mcp_spine_server` reads `SPINE_FILE` at import time — import it only
inside a test with a scratch env, never at module scope.

## Stop conditions

- Cannot reproduce a claimed result → **BLOCK** with the output.
- A constraint above is violated → **BLOCK**.
- Leave the tree unmodified — check `git status` before finishing.
- **Never waive.** `spine_halt` with `action=block` and return.

## Return format

Write the result artifact at the path above **before ending your turn**. Carry a **`Verdict`** field whose
value is exactly `APPROVE` or `BLOCK`. Number every finding with evidence, consequence, and
confirmed-vs-suspected. End with the single most likely way this gate produces a green run that is wrong,
and a short **Workflow Feedback** section.
