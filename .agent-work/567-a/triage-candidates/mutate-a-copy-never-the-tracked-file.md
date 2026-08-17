# Triage candidate: "mutate then restore" is an unsafe instruction to give a crew

- **Disposition:** `recommend-and-defer`. Not filed (`decision:no-issue-filing`). This is a
  **doctrine / handoff-template** recommendation, not a code change, so it is the human's
  call whether it belongs in `docs/agents/*` — and `decision:no-doctrine-promotion` says
  recording an observation is not authority to promote it.
- **Raised by:** `cmdr-567-a` at `600de020`, from a live near-miss in this lane.
- **Severity:** high. The failure mode leaves a security fix silently reverted in a working
  tree, and it looks exactly like a healthy tree to anyone who does not run `git status`.

## What happened

Mutation testing is the right technique and this lane depended on it — it is how the
implementing crew discovered that its own security fix was untestable (every test fixture
used a topology where the narrow and wide containment roots return the same path, so the
whole suite passed identically with the vulnerable root in place).

So I asked the reviewer to independently re-run the decisive mutation: swap the narrowed
`--show-toplevel` root back to the wide `--git-common-dir` one, confirm the suite goes red,
restore. Standard practice, and the launch order sanctions it ("break the worktree copy for
red-proofs").

**The reviewer died between mutating and restoring.** No `REVIEW_RESULT` was written. What
it left behind:

```
$ git status --short
 M scripts/mcp_spine_server.py

$ git diff scripts/mcp_spine_server.py
-    return Path(_git_rev_parse("--show-toplevel", cwd=directory)).resolve()
+    # REVIEWER MUTATION M3c -- the one flag swapped, nothing else.
+    common = Path(_git_rev_parse("--git-common-dir", cwd=directory))
...
```

The door's containment root — the entire response to a cold critic's blocking finding about
reach — was reverted to its vulnerable form in the working tree.

**Nothing was actually lost this time,** and that is luck plus a habit rather than design:
`git log --oneline -S'REVIEWER MUTATION' --all` is empty, so the mutation was never
committed and `HEAD` always carried the correct root.

## Why this is a real hazard and not just an untidy agent

Three properties make it worse than it first reads:

1. **It is silent.** A mutated-and-abandoned source file produces a *passing-looking* tree.
   Nothing errors. The next agent to run the door from that worktree gets the vulnerable
   behaviour with no signal at all.
2. **The mutation is deliberately minimal and plausible.** Good mutation testing changes one
   flag or one argument. That is precisely the kind of diff a reviewer skims past, and it
   is indistinguishable from an intentional edit.
3. **It targets the code the run cares most about.** Mutation testing is aimed at the
   security-critical line by construction, so the abandoned state is never a harmless
   corner — it is always the guard.

A crew can die at any instruction boundary: harness limits, a killed process, a context
trip, an adjudication. So "mutate, then restore" is a two-phase commit with no journal,
handed to a participant that can vanish between the phases.

## Recommendation

**Never mutate a tracked file in place. Mutate a copy.**

- `cp <file> /tmp/<name>.py`, mutate the copy, and load the copy (the door and the engine are
  both loadable from an explicit path, and this repo's own test harness already does exactly
  that — `tests/test_mcp_lifecycle.py`'s `_load_module` loads a module per binding).
- Where in-place mutation is genuinely unavoidable, `cp` a backup **first** and restore it as
  the very next action, then assert `git status --short` is clean before continuing.

**Two places this belongs, if the human wants it durable:**

1. The **implementer and reviewer handoff templates** — a line under Constraints: "if you
   mutate a tracked file to prove a test discriminates, mutate a COPY; leave the working
   tree clean and paste `git status --short` to prove it."
2. The **crew-tier doctrine** already carries "a check that cannot fail"; this is its
   operational twin — the check that *can* fail but leaves the codebase broken when the
   checker dies.

**And a dispatcher-side rule, which is the part I got right by accident:** judge a crew's
liveness and its damage over the **whole worktree**, never over its result artifact. The
missing `REVIEW_RESULT` told me nothing useful; `git status` told me everything.
`global-orchestrator.md` already says to measure liveness across the worktree, but for the
opposite reason (so a workbench-only mtime probe does not adjudicate a live agent dead).
The same rule catches a dead agent's leftovers, and that second use is not written down.

## Related, same lane

The Commander made the identical mistake in kind and got away with it: I mutated
`scripts/checklist_engine.py` in place for the `save()` red-proof. I had `cp`'d a backup
first and restored it, and I verified the restore with `git diff --stat` — which is why it
was fine. But `decision:self-hosting-engine-edit` had already told me the rule in the
spine-file case ("against a COPY, never a live spine file") and I applied it to spine files
without generalising it to source files. The rule is the same rule.
