# tests.test_spine_rail:test_session_start_real_engine_claim_produces_real_binding_diff
function, tests/test_spine_rail.py:1010, 99 lines

```python
def test_session_start_real_engine_claim_produces_real_binding_diff(proj)
```

The single most important proof on this gate

(lesson:verify-harness-field-and-drive-real-writer, #261): a hand-set
cwd/session_id fixture would pass green even if production never
delivers the field, hiding a silent no-op fix -- so every layer here is
driven by the real production code, not a stub.

(1) A REAL checklist_engine.py subprocess claims a REAL spine file
    (copied from the repo's own vendored IMPLEMENTER_PLAN template, not
    sr.make_spine()'s hand-built dict) -- the active lease on disk is
    genuinely engine-produced.
(2) That exact claim command's text is fed through the REAL
    handle_post_tool_use, exactly as the harness's PostToolUse hook
    would deliver it after really running that command, writing a real
    binding entry via the real save_binding writer for an OWNER
    session (simulating "this spine was already claimed by someone
    else").
(3) A SECOND, different, never-before-bound session_id then fires a
    SessionStart payload shaped like the real documented contract
    (session_id, cwd, transcript_path, hook_event_name, source --
    code.claude.com/docs/en/hooks, confirmed live in notes-261.md)
    straight at decide_session_start (the real function, no stub).

The real `.spine-rail-binding.json` file on disk is shown, by content
diff, to gain a fresh entry for that new session_id it did not have
before the call. Run with `-s` so the printed before/after text lands
in the evidence output verbatim.

calls stdlib: builtins.str x7, builtins.print x4, json.loads x2, builtins.iter, builtins.len, builtins.next, subprocess.run
reads internal: sr x5, _REPO_ROOT x3
reads stdlib: json (module) x2, subprocess (module), sys (module), sys.executable
unresolved: 12 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
