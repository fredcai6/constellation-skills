# Triage candidate: a real (non-dry-run) install_constellation.py invocation mutates the CALLING repo's own .mcp.json regardless of --dest

**Found during:** 567-d2 g2-verify-registration, verifying the installer against the
post-change workbench skill.

**What:** Running `py scripts/install_constellation.py --agent codex --scope user
--dest /tmp/some-other-dir --skills workbench commander cartographer` (no
`--dry-run`) from inside this worktree rewrote **this worktree's own**
`.mcp.json` (`"command": "python3"` -> `"command": "py"`, the probed
interpreter), even though `--dest` pointed entirely outside the repo. The
`--dry-run` form does not do this.

**Evidence:** `git diff .mcp.json` showed the rewrite immediately after the real
install; reverted with `git checkout -- .mcp.json` before committing. Confirmed
by re-reading the installer's own output line: `wired 1
/home/tommy/projects/.../.mcp.json server command(s) -> 'py' (probed)` — it
targets the **cwd's** `.mcp.json`, not `--dest`'s.

**Why this lane didn't fix it:** This is `scripts/install_constellation.py`
behavior, which this lane DOES own this wave -- but changing it is a behavior
change to a widely-depended-on script, out of this lane's bounded mission
(sunset workbench's teaching half), and the commit history already shows a
prior revert of an installer `.mcp.json` probe change (`f40472e8`: "reverted the
installer's .mcp.json probe"), suggesting this exact surface has already been
adjusted/reverted once and deserves deliberate handling, not a drive-by fix.

**Suggested disposition:** recommend-and-defer — worth a deliberate look at
whether `.mcp.json` wiring should be opt-in/scoped to `--dest`, or whether this
is intended and just needs documenting loudly so verification runs don't get
surprised (as this run did).
