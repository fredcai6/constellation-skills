# Review Result

## Assigned Gate
`g1-implement (reviewing)`

## Result
`APPROVE`

## Handoff compliance
Satisfied. `is_self_install(args) -> bool` exists at `scripts/install_constellation.py:2369-2373`, is pure
(`args.dest is None and args.project is None`, no I/O), and gates `main()`'s tail so the entire
`apply_repo_mcp_config_wiring(...)` call — not just its path argument — is skipped unless
`mcp_config_path is not None or is_self_install(args)` (L2533). Read the guard directly rather than trusting
the test suite alone, as the handoff required: `apply_repo_mcp_config_wiring` is called at exactly one site
(L2537-2542) and it is always passed `mcp_config_path if mcp_config_path is not None else
default_mcp_config_path()` — never `None`. All stop conditions were checked and none fired: the diff was
accessible, every piece of IMPLEMENTER_RESULT evidence reproduced exactly, and
`apply_repo_mcp_config_wiring` is never reachable with `mcp_config_path=None`.

## Scope drift
None. `git status --porcelain` shows only `scripts/install_constellation.py` and
`tests/test_install_constellation.py` as `M` (no `??` for either — confirms no new file was created). No
specific exclusion was touched: `map/INDEX.md`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
`*SPINE*.template.json`, `specs/`, and `default_mcp_config_path()`'s own signature/behavior are all
byte-identical to before. The one unrelated porcelain entry
(`.agent-work/epic-567-door/gauge-constellation-epic-567-door-...json`) is parent-run spine/gauge state, not
implementer output.

## Evidence verdict
Satisfies required evidence; independently reproduced, not merely trusted:
- `py -m pytest tests/test_install_constellation.py -q` → **206 passed, 506 subtests passed** — matches the
  claim exactly.
- **TDD red-proof reproduced**: reverted the guard to the old unconditional `if wire_repo_mcp_config:`, reran
  the new test alone, and got the exact claimed failure (`AssertionError: ... "<python-interpreter>" != ...
  "py" ... fixture .mcp.json must stay byte-identical when --dest is set`). Restored the fix; full suite green
  again (206/506).
- **Wiring grep reproduced**: `grep -rn "is_self_install" scripts/` and a repo-wide grep confirm exactly one
  non-test, non-definition call site (L2533, the guard).
- Confirmed the new regression test (`test_a_dest_outside_the_checkout_never_touches_this_checkouts_own_mcp_json`,
  L4298-4348) calls `installer.main([...], wire_repo_mcp_config=True)` with **no** `mcp_config_path` override —
  the real CLI-entry-point shape, not a version that would pass regardless of the fix.
- `git diff` on the test file shows only additions plus the one named docstring edit inside
  `RepoMcpConfigWiringTests`; every pre-existing case in that class is present and unmodified.
- `test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json`'s assertion body
  (`self.assertEqual(installer.REPO_ROOT / ".mcp.json", installer.default_mcp_config_path())`) is
  byte-for-byte unchanged — only its docstring was edited.

## Code/doc quality
Minimal and maintainable: the fix is a 2-line pure predicate plus a one-condition guard change, matching
"make the minimal change that satisfies the handoff." Project rules checked against `docs/agents/CREW_CONTEXT.md`
(Python invocation, Windows-encoding, record-stores, two-engines, verification discipline) — no violations; the
diff adds no new file-write calls and the byte-identical test asserts real bytes, not a docstring string.

**Fowler pass** (`.agent-work/567-j/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0 — `smells=12,
flagged=['duplicated-code'], overridden=['comments-as-deodorant']`): 10 of 12 baseline smells absent. One
non-blocking observation: `IsSelfInstallTests` writes 4 near-identical test methods where the file's own
established convention for the same shape (`IsRewritableMcpCommandTests`, same file) groups cases with
`subTest`. One override, logged: the WHY-comments added around the guard match this file's pre-existing dense
comment-per-nonobvious-conditional house style, so they are not comments compensating for confusing code.

## Map impact verdict
Skipped — no architecture map exists in this repo (`map/ids.jsonl` empty, DEGRADED-UNPARSEABLE), waived by the
Admiral this wave per `decision:map-index-is-admiral-owned` (handoff Map Anchors). The implementer's "No map
artifacts to update" claim is consistent with that waiver.

## Reconciliation check
None. The `--scope user` + no-`--dest` edge case (`is_self_install` still `True`, so the checkout's own
`.mcp.json` is still wired even though the install target is the user's home directory) is explicitly
documented in-line as accepted pre-existing behavior, not a new divergence this wave introduced.

## Blockers
- none

## Out-of-scope observations
- The handoff's Close Criteria named a literal test recipe ("monkeypatch `installer.REPO_ROOT` ...") that does
  not work as written: `default_mcp_config_path(repo_root: Path = REPO_ROOT)` binds its default at `def`-time,
  so patching the `REPO_ROOT` module global afterward is inert for it, and patching `REPO_ROOT` itself
  separately breaks `install_skills` (which reads `REPO_ROOT` directly). The implementer's actual fix —
  patching `default_mcp_config_path.__defaults__` directly, restored in `finally` — is correct (confirmed by
  this review) and is a better pattern than the handoff recipe. `REPO_ROOT` gates three other functions the
  same def-time-default way (`validate_required_scripts`, `source_hook_path`,
  `discover_skills`/`SOURCE_ROOT`), so the same handoff-recipe mistake will recur for any of them. Flagged as
  triage candidate `tc1` in `.agent-work/567-j/g1-review/review.json`: update the shared handoff/close-criteria
  template wording to name the `__defaults__` patch pattern instead of a bare `REPO_ROOT` monkeypatch.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: the handoff's Map Anchors, Close Criteria, and Allowed Scope
  were all accurate and sufficient to verify without needing to dig up anything not named. (The one recipe gap
  above belongs to the implementer's *upstream* handoff, not this reviewer handoff, and is reported as a triage
  candidate rather than a gap in the document I was handed.)
- **Context rediscovered:** none — confirmed after review: everything needed (diff location, evidence, symbol
  names) was in the handoff or the IMPLEMENTER_RESULT it pointed to.
- **Instructions improvised around:** the environment's `SPINE_FILE`/`SPINE_SESSION` pointed at the parent
  Commander's `execute.json` spine, not a spine bound for this reviewer crew (confirmed via `crew-runs.json`:
  this crew's own entry has `"spine": null"`). Per prior session memory of this exact shape, I did not drive
  the parent's spine; instead I authored my own `REVIEW_SURVEY` at the handoff's named Survey State Location
  (`.agent-work/567-j/g1-review/review.json`) and drove it directly through `checklist_engine.py`'s CLI (claim
  → start/record each check → consolidate → release), never touching the parent spine.
- **What would have made this easier:** the skill's "a spine is bound for you" opening line could branch
  explicitly on whether the bound spine's `session_id`/gate shape actually matches this crew's own dispatch
  (vs. belonging to the parent), since a crew with `spine: null` in `crew-runs.json` still inherits non-null
  `SPINE_FILE` env from its parent today.

## Return status
`complete`
