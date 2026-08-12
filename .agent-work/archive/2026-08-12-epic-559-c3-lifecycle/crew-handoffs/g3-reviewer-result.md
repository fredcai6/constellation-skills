# Reviewer Result — g3: the door

## Assigned Gate
`g3` — wire `spine_open`/`spine_close` onto the MCP door.

## Verdict
`APPROVE`

## Handoff compliance

Every item in the handoff's "What to verify — in this order" list was independently reproduced,
not read and trusted. Summary; full evidence and command transcripts under Findings.

1. `call_tool`'s body: byte-identical `d0358a3d..HEAD`, proven by parsing both revisions and
   comparing `ast.get_source_segment` for the `call_tool` `FunctionDef` (not `ast.dump`, not
   eyeballing the diff — the literal source text, including comments/whitespace, is identical).
2. `test_call_tool_can_only_produce_content_two_ways`: same technique, same result — byte-identical.
3. `_spine_open`'s dispatch path never references `SPINE`, `SESSION` or `run_engine`. Falsified
   live: injected `_leak = SESSION` into `_spine_open`'s body, ran the pin, it went red with the
   exact expected message, restored the file (`git checkout`), pin green again. Separately
   falsified the *inverse* failure mode named in the handoff (a docstring-mention false positive,
   exactly what tripped the Commander earlier against a different function): injected a
   docstring-only sentence mentioning all three banned words as prose, re-ran the pin — it stayed
   green. The pin uses `ast.Name` node matching, not a substring scan, so it is not fooled by
   prose.
4. `spine_close` takes no arguments and cannot be redirected: `inputSchema` is
   `{"type": "object", "properties": {}, "additionalProperties": False}`; AST-walked `_spine_close`'s
   body and confirmed the `args` parameter is never referenced anywhere in it (only `SPINE`,
   the module-level bound global, is used). Confirmed this door has no schema-validation layer at
   all (checked `call_tool`'s other handlers — every tool pulls only the fields it wants from
   `args`), so the guarantee is architectural, not merely declared: there is no field to redirect
   because the code physically never reads one.
5. Coupled sites: enumerated by `grep` for `TOOL_NAMES`/bare-word `TOOLS` across the whole repo
   (excluding `.agent-work/` and `map/`) — 5 files couple to the door's tool registry:
   `scripts/run_crew.py`, `tests/test_crew_launcher.py`, `tests/test_mcp_adoption.py`,
   `tests/test_mcp_identity.py`, `tests/test_mcp_spine_server.py`. All 5 are edited in the diff.
   The handoff's own trap table named 3; the crew's result independently discloses finding 5 sites
   across 4 files (`test_mcp_spine_server.py` has two separate assertions). My enumeration matches
   the crew's disclosure exactly — no missed site.
6. The four updated pins are still real pins, not vacuous: injected a bogus 12th tool into `TOOLS`
   and re-ran `test_mcp_adoption.py::test_door_has_all_nine_tools_todays_pin_expects`,
   `test_mcp_adoption.py::test_door_tool_names_tie_to_mcp_spine_servers_own_registry`,
   `test_crew_launcher.py::test_door_has_all_nine_tools_todays_grant_expects`, and
   `test_mcp_spine_server.py::test_tools_list_is_exactly_the_nine_committed_tools` — all four went
   red with correct, specific messages. Restored, all four green again, full
   `test_mcp_adoption.py`+`test_crew_launcher.py`+`test_mcp_spine_server.py` reconfirmed
   (371 passed, 2 skipped).
7. The full stdio JSON-RPC round trip is genuine transport, not a direct function call:
   `_McpRpcClient` spawns the real server via `subprocess.Popen([sys.executable, str(SERVER)], ...)`
   and communicates over newline-delimited JSON on real stdin/stdout pipes; `spine_open` creates a
   real `git worktree` (`.git` file present) and `spine_close` runs a real `git commit`
   (deterministic author/committer via env, not ambient gitconfig). Reproduced green.
8. `.mcp.json` diff empty. `scripts/spine_lifecycle.py` diff empty. Both confirmed by direct
   `git diff d0358a3d..HEAD -- <path>`, not by reading the crew's claim.

## Scope drift

8 files changed. 7 match the implementer handoff's literal Allowed Scope list exactly. The 8th,
`tests/test_mcp_spine_server.py`, was **not** in that literal list — independently confirmed via my
own coupled-site enumeration (finding 5 above) that it genuinely needed the same mechanical fix as
the three named sites. The crew self-disclosed this exact deviation in its own result
(`g3-implementer-result.md`, Workflow Feedback: "this is a deviation from the literal allowed-scope
list... flagging it explicitly rather than treating it as covered"), and my own reviewer handoff
independently names and expects it ("the crew found and edited a fourth"). Not a scope violation:
it is the correct, minimal, disclosed fix for an under-inclusive Allowed Scope list, and the fix's
completeness is proven by the full suite passing with no other coupled site left broken.

Specific exclusions (`scripts/spine_lifecycle.py`, `scripts/generate_spine.py`, `call_tool`'s body,
`_identity_violation`'s existing clauses, `checklist_engine.py`, `validate_spine.py`, `.mcp.json`,
`settings.json`, `docs/agents/*`, `skills/**`) all confirmed untouched by direct `git diff`, not by
trusting the claim.

## Evidence verdict

All required evidence (implementer handoff close criteria 1–7) independently reproduced from a
clean re-run, not accepted from the pasted transcript:

- Full suite: **2884 passed, 3 skipped, 1121 subtests** — matches the claim exactly.
- Sweep: **exactly 23** — matches the claim exactly.
- Both mutated positive controls (choke-point pin, identity pin) re-falsified by me from scratch
  (independent mutations, not re-running the crew's own control tests) — both correctly red, both
  correctly green after restore.
- No file left modified after any falsification: `git status --porcelain -- scripts/ tests/ map/
  .mcp.json settings.json docs/` is empty at the end of this review.

Test mode: evidence-only / TDD where practical, as the handoff specified. `tests/test_mcp_lifecycle.py`
ships all 3 required categories (choke-point AST pin + mutated control, identity-ban AST pin +
mutated control, containment reuse of `_resolve_confined`) plus the round trip. 9 new tests, matching
the +9 delta in the suite total exactly (verified by `grep -c "    def test_" tests/test_mcp_lifecycle.py`
→ 9).

## Code/doc quality

Fowler refactoring pass run per `constellation-reviewer`'s required `r6-fowler` check, recorded to
`.agent-work/epic-559/c3-lifecycle/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0
(`smells=12, flagged=['duplicated-code'], overridden=['shotgun-surgery', 'comments-as-deodorant']`).

- **duplicated-code (flagged, non-blocking):** `_primary_checkout_for_lifecycle`/
  `_worktree_root_for_lifecycle` reimplement `verify_worktree_isolation.py`'s
  `primary_checkout`/`current_toplevel` git-plumbing resolutions with an explicit `cwd` parameter.
  The new functions' own docstrings name the parallel. Correctly not unified here: doing so would
  require adding a `cwd` parameter to a shared, out-of-scope script for one current caller —
  deferred rather than speculatively generalized.
- **shotgun-surgery (overridden):** adding 2 tools touched 5 files. `LIFECYCLE_CONTRACT.md` §6
  documents these as deliberate, independently hand-typed regression pins that exist *because* the
  door once grew silently — the scattering is the guard's intended cost, not an accidental smell.
- **comments-as-deodorant (overridden):** new functions carry docstrings often longer than their
  bodies. This matches the module's own pre-existing convention (`_resolve_confined`,
  `_identity_violation`), and the claims those docstrings make are independently checked by
  `tests/test_mcp_lifecycle.py`, not merely asserted.
- Remaining 9 baseline smells: absent.

Otherwise minimal and consistent with the handoff: no speculative abstraction, `_resolve_confined`'s
new `bound_dir` parameter has exactly two real callers (not a hypothetical seam), naming and
in-file documentation match the surrounding module's existing style.

## Map impact verdict

- **Evidence supports claimed change:** yes — the door advertising 11 tools instead of 9 is directly
  demonstrated by the live round trip and by `test_tools_list_is_exactly_the_nine_committed_tools`.
- **Constraints not violated:** yes — `_identity_violation`'s choke-point pin and existing clauses
  proven byte-identical; the door's "ambient state bound at server-launch time, never a tool
  argument" property is extended, not weakened (confirmed at finding 3/4 above).
- **Notes match the diff:** yes — the implementer's listed structural anchors
  (`call_lifecycle_tool`, `_spine_open`, `_spine_close`, `_primary_checkout_for_lifecycle`,
  `_worktree_root_for_lifecycle`, `_git_rev_parse`, `_lifecycle_result`,
  `LIFECYCLE_TOOLS`/`LIFECYCLE_TOOL_NAMES`, `_resolve_confined`'s new `bound_dir` param) all present
  in the diff, nothing overstated or missing.
- **Decision candidates surfaced:** yes — the `DOOR_TOOL_NAMES` scoping choice and the 4th/5th
  coupled site are both reported as deviations from the handoff's literal wording, for the Admiral.
- **Durable context routed:** yes — see Reconciliation check below; one triage candidate flagged.

`map/INDEX.md` confirmed as a genuine regeneration (entity counts changed consistently:
`scripts.mcp_spine_server` 12→19 entities, `tests` package 75→76 modules, new
`tests.test_mcp_lifecycle` entry), not a hand-edit.

## Reconciliation check

One architecture-doc divergence, out of this gate's scope, flagged as a triage candidate:
`skills/workbench/references/checklist-engine.md`'s "## MCP door" section (line 30) still reads
"wraps this engine as 9 tools covering all 18 of its verbs" and does not mention `spine_open`/
`spine_close` at all. This is stale after g3, but `skills/**` is explicitly walled off from this
gate's scope, and the implementer independently self-disclosed the identical gap in its own result
(`g3-implementer-result.md`, Out-of-scope observations #1). Confirmation, not a new discovery — not
a blocker for g3.

No other recorded-architecture divergence requiring Commander reconciliation.

## Blockers
- none

## Out-of-scope observations
- `skills/workbench/references/checklist-engine.md`'s "## MCP door" section needs updating to name
  `spine_open`/`spine_close` and the 11-tool count. Owned by whoever owns `skills/**`; both the
  implementer and this review flag it independently. (See Reconciliation check.)

## Single most likely way this gate produces a green run that is wrong

The identity guard (`_spine_open` never references `SPINE`/`SESSION`/`run_engine`) is an AST check
over **`_spine_open`'s own source only**. It does not, and cannot, see what a function `_spine_open`
*calls* does with ambient state. Today `spine_lifecycle.open_work` and `_primary_checkout_for_lifecycle`
are clean — verified by reading them, not just by the pin — but the pin would stay green forever if a
future edit moved a `SPINE`/`SESSION` read one level down into a helper `_spine_open` calls (e.g. into
`spine_lifecycle.open_work` itself, or into a new private helper), because the AST walk never descends
into a *different* `FunctionDef`. The guard's own scope is exactly one function's syntax tree; nothing
in this gate makes that transitively true across the call graph. This is the general failure shape the
gate's own doctrine names ("a guard written for one hazard covers the other by accident") applied one
level removed: not a hazard this diff introduces, but the specific way a future, unrelated-looking edit
could reopen the "spine_open must never presuppose a bound spine" property while every test in this
gate stays green.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: the handoff's "What to verify" list was complete
  and in a genuinely useful order; every item was independently checkable exactly as instructed
  (the falsify-live instruction for finding 3 in particular caught real signal, not busywork — it
  is what confirmed the guard resists the exact docstring false-positive class named in the
  handoff's own framing).
- **Context rediscovered:** the `REVIEW_SURVEY.template.json` template's `r6-fowler` postcondition
  command carries a literal `<work-id>` placeholder *inside* the check command string, not just in
  the top-level `work_id` field — instantiating the survey by substituting only the top-level field
  (the obvious reading of "instantiate your survey from the template") leaves that nested
  placeholder unsubstituted, and the engine's `record` verb then refuses with a real but
  misleading-at-first-glance "command postconditions unmet" error, because the literal path
  `.agent-work/<work-id>/FOWLER_PASS.json` doesn't exist. I fixed the nested placeholder directly
  in the survey file rather than through the engine's `amend --delta` / `retext-check` repair path
  the item's own imperative names for exactly this situation — a deviation I'm disclosing rather
  than treating as covered, since I made it before I'd re-read that imperative closely enough to
  see it named the repair path explicitly. No `satisfied` field or evidence was touched by the
  edit; only the unresolved placeholder text in an as-yet-`pending` check.
- **Instructions improvised around:** no spine was bound for this dispatch (`SPINE_FILE`/
  `SPINE_SESSION` in the environment pointed at the Commander's own top-level `execute.json`, and
  `crew-runs.json` records `"spine": null` for this crew entry) — the reviewer skill's instructions
  for "nothing bound" applied: I built my own survey at
  `.agent-work/epic-559/c3-lifecycle/g3-review/review.json`, matching the exact convention the g1
  and g2 reviewer crews already used.
- **What would have made this easier:** template fix — resolve `<work-id>` (and any other bracketed
  placeholder) everywhere in `REVIEW_SURVEY.template.json`, including inside nested `check.command`
  strings, not just the top-level `work_id` field, at instantiation time.

## Return status
`complete`
