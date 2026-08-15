# Implementer Handoff

## Gate
`g2`

## Task
Harden the `external` crew-dispatch backend's already-known unbound-MCP-door hazard: a crew dispatched via
`ExternalBackend` gets no `SPINE_FILE`/`SPINE_SESSION` binding (it spawns no process, so nothing binds an
environment), and its MCP door therefore resolves to `.mcp.json`'s demo default. This has previously caused
a `claim` to mutate the wrong spine while reporting success. Binding the door out-of-band is impossible by
construction (module-import-time env read in `scripts/mcp_spine_server.py`, pinned by
`tests/test_mcp_identity.py:914` — do not attempt it, do not propose relaxing that pin). This gate's job is
visibility, not binding: make the hazard impossible to miss.

**Cold-critic correction, already verified by direct read — read `ExternalBackend.dispatch` yourself
(`scripts/run_crew.py:1278-1310`) before starting:** it builds NO prompt. Its own comments say the
out-of-band caller (a Commander) builds the prompt itself, outside this file. So "state it in the crew
prompt" cannot be satisfied inside `scripts/run_crew.py` — there is no prompt-building code here to edit.
Two concrete pieces ARE genuinely buildable here, and BOTH are required:

1. **Registry entry field.** `build_entry` (~line 868) assembles the dict every registry entry is built
   from. Add an explicit field recording whether the door is bound, e.g. `entry["door_bound"] = (backend ==
   "cli")` — `True` for `cli`-backend entries (which genuinely get `SPINE_FILE`/`SPINE_SESSION` bound into
   their spawned child), `False` for `external`-backend entries (which get nothing). This makes
   `crew-runs.json` state the hazard plainly for anyone reading the registry — including a resumed/relaunched
   Commander or a human debugging a crew's behavior after the fact.
2. **CLI stderr banner.** `ExternalBackend.dispatch` (or its caller in `main()`) prints an explicit stderr
   line when recording an external-backend entry, naming the unbound door and instructing the caller to
   verify `spine_status` before any mutating verb. This is what a Commander sees at the exact moment it is
   building the out-of-band prompt for the Agent-tool subagent it's about to dispatch — the practical
   equivalent of "in the prompt," without editing any file outside `scripts/run_crew.py`.

## Protected Intent
The door must never SILENTLY read as bound when it is not. Do not attempt to bind it — that is impossible
by construction and out of scope; this gate only makes the unbound state loud and unmissable.

## Test Mode
TDD required for the registry-entry field (a `build_entry`/`ExternalBackend.dispatch` unit test asserting
the field's value per backend). The stderr banner is inspection/output-assertion (capture stderr in a test
and assert the hazard text appears) — same test mode, just asserting output instead of a dict key.

## Close Criteria
- Every registry entry produced by `build_entry` carries a `door_bound` field: `True` when `backend ==
  "cli"`, `False` when `backend == "external"`. Pin this exact field name and these exact boolean semantics
  — do not invent a different name or a three-valued scheme.
- `ExternalBackend.dispatch` prints a stderr line (or logs via whatever the file's existing print/log
  convention is) that plainly states: the door is unbound, it resolves to `.mcp.json`'s demo default, and
  the crew must verify `spine_status` before any mutating verb. Match `run_crew.py`'s existing hazard-message
  style (see `CrewLaunchError` messages in the same file for tone/format) rather than inventing a new one.
  Quote your exact chosen wording in your `IMPLEMENTER_RESULT` so the reviewer can check it verbatim.
- Both pieces are built. If, after re-reading this corrected handoff, something ELSE beyond these two
  concrete pieces looks like it needs a design decision, name exactly what and return `blocked` — do not
  silently drop either of the two named pieces to avoid that decision.
- Full existing test suite for `scripts/run_crew.py` still passes — this is an additive, non-breaking change
  (existing registry entries/dispatch calls must not need to change their call sites).

## Allowed Scope
`scripts/run_crew.py` (`build_entry`, `ExternalBackend.dispatch`, and `CliBackend`'s equivalent entry
construction if `door_bound` needs setting there too — read both backends' entry-construction call sites
before choosing where the field is actually set) and `tests/` (new/extended tests for the above).

## Specific Exclusions
- Do not touch `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`, `.mcp.json`.
- Do not touch `.worktrees/epic-568-441/` or `.worktrees/tc1-worktree-identity/`.
- Do not attempt to bind the door out-of-band — impossible by construction, do not propose it, do not touch
  `scripts/mcp_spine_server.py`.
- Do not touch `finalize_from_exit_code` or anything g1 already changed (already committed at `f06d314e`).

## Constraints
- `door_bound` must be `True` for `cli`, `False` for `external` — no other backend value exists today, but
  write the condition as `backend == "cli"` (not `backend != "external"`) so a future third backend defaults
  to the safer `False` rather than silently inheriting `True`.
- The stderr banner must appear on EVERY external-backend dispatch, not just some — grep your own diff for
  the print/log call site and confirm it is unconditional within `ExternalBackend.dispatch`.

## Map Anchors (inbound)
- **Map entry point:** none — repo's derived code map is DEGRADED-UNPARSEABLE (structurally empty,
  repo-wide). Start directly from source.
- **Structural:** `scripts/run_crew.py:868-` (`build_entry`); `scripts/run_crew.py:1278-1310`
  (`ExternalBackend.dispatch`, confirmed by direct read to build no prompt); `scripts/mcp_spine_server.py:145-146`
  (binds at module import — read-only reference, do not touch); `tests/test_mcp_identity.py:914` (the pin
  against out-of-band rebinding — read-only reference, do not touch).

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; verify via `git check-ignore scripts/run_crew.py` exiting 1.
- **Committed** — whichever test file you add to under `tests/`; verify the same way before dispatch is not
  possible for a file you haven't chosen yet — state in your result which file you used and confirm
  `git check-ignore <that file>` exits 1 yourself before finishing.

## Required Evidence
- The exact diff to `build_entry`/`ExternalBackend.dispatch` (or paste the new lines).
- The exact banner text you chose, quoted verbatim.
- Test output showing the new/extended tests pass (`python -m pytest -q -k <your new test names>`).
- `python -m pytest -q tests/test_crew_launcher.py` full-file run showing no regressions.

## Wiring Grep
`grep -rn "door_bound" --include=*.py .` — state the count and every call site (the field is new; expect
readers to be your own tests only, plus the two write sites in `build_entry`/backend dispatch — say so).

## Verification Commands
```bash
git check-ignore scripts/run_crew.py; echo "exit:$?"
python -m pytest -q tests/test_crew_launcher.py
```

## Suggested Model Tier
simple bounded — one new field, one new stderr line, tests for both.

## Authority
The two-piece scope (registry field + stderr banner) is pinned by this handoff after a cold-critic
correction to the original plan — do not redesign it further. If it genuinely does not cover the ask, name
what's missing and stop; do not invent a third piece on your own authority.

## Stop Conditions
Stop and return `blocked` if: something beyond the two named pieces is required to make the hazard
"impossible to miss," and you cannot build it within `scripts/run_crew.py` alone. Name exactly what.

## Return Format
Return IMPLEMENTER_RESULT per `templates/IMPLEMENTER_RESULT.template.md` to
`.agent-work/crew-verdict-and-door/crew-handoffs/g2-implementer-result.md` before ending your turn. `Return
status` lowercase: `complete | partial | blocked | out-of-scope | failed`.
