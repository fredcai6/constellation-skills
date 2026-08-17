# A headless `claude -p` launched inside a lane worktree inherits that lane's spine and Stop hook

**Observed, 567-d1.** A trivial headless probe (`claude -p "create a file and stop"`) launched from
this worktree inherited `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` and the session's Stop hook. It
wrote its file, then spent its remaining turn reasoning about whether it should claim the lease and
drive gate `plan` on **the parent Commander's spine** — declining only because the MCP tools were
not in its permission set. A design helper with wider permissions would have driven the parent's
spine.

Mitigation used for all subsequent dispatches: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`.

**Candidate fix:** have the dispatch path strip `SPINE_*` by default for any helper that is not
being given its own spine, rather than leaving each Commander to remember. Related to the recorded
guidance that a crew's `SPINE_*` env is its parent's and must never be driven.
