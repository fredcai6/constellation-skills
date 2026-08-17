# Triage candidate — `scripts/mcp_spine_server.py` carries a CLI-fallback sentence no walk reads

**Found at:** `g1-integrate`, lane D1, epic #567 wave 2. Reported by the g1 reviewer (`tc2`).

**What was found.** `scripts/mcp_spine_server.py:123` contains a `CLI-fallback` sentence. It is
prose that *forbids* the violation while quoting it, so it is not itself a defect — but it sits in
a file that **no instruction walk reads**: `tests/test_cli_retirement_guard.py` walks `skills/`,
`specs/**/*.toml` and (as of g2) `.agent-work/templates/`, and `tests/test_mcp_adoption.py` walks
`skills/` only. Python source is outside both by design.

**Why it is a candidate and not a fix.** `scripts/mcp_spine_server.py` is **lane E's** file this
wave, so this lane is fenced from it. And the question of whether the door's own source should be
inside an agent-facing-text walk is a scope decision, not a cleanup: a docstring in the server is
read by a maintainer, not handed to an agent, which is exactly the distinction the guard's walk
rule encodes.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run` (the human: *"we've been
ballooning out tracking"*).
