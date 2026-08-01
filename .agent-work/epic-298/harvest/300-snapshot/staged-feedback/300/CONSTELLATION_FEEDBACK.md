# CONSTELLATION_FEEDBACK exports — staged from issue-300 (epic-298)

Constellation-scoped findings from this run. Per the counter semantics, a constellation-scoped
lesson accrues *debt*, not trust — these are exported for upstream fixing rather than confirmed into
permanent workarounds. Both are already filed to the tracker.

## 1. Delegated Commander (teammate) cannot spawn named or background subagents

**Target:** `constellation-commander` skill's `references/commander-core.md` (§Mission frame,
the "must be told in its spawn prompt to deliver via SendMessage" clause) and
`constellation-commander-delegated/SKILL.md` (§5, "wait actively, inside your turn: poll the crew's
result artifact ... in a loop").

**Defect:** a delegated Commander dispatched by an Admiral runs as a harness teammate. Teammates
cannot spawn *named* subagents ("the team roster is flat") and cannot spawn *background* subagents
at all. So an unnamed subagent has no address and cannot `SendMessage` a teammate parent, and a
synchronous dispatch cannot be polled because it blocks. Both instructions are unfollowable at the
exact tier that is told to follow them.

**Not a blocker:** multiple synchronous `Agent` calls issued in ONE message do run concurrently, and
the result-artifact file is a fine delivery channel. But each restriction costs a failed-dispatch
discovery round-trip, and a Commander that trusts the doctrine will burn both.

**Suggested edit:** qualify both clauses with the teammate case — "when you are yourself a teammate,
dispatch synchronous subagents in parallel in a single message and take delivery from the result
artifact rather than SendMessage."

**Filed:** issue #316.

## 2. Engine command postconditions inherit the launcher's cwd

**Target:** `scripts/checklist_engine.py`, `_run_check_command`.

**Defect:** it calls `subprocess.run([shell, "-c", command])` with no `cwd=`, while `_git()` in the
same file passes `cwd=base_dir`. Every relative path in a gate's `command` postcondition therefore
resolves against wherever the engine process was launched rather than the checklist's own base dir.
Fails closed for most check shapes, but a negated or short-circuiting form can return 0.

**Filed:** issue #315.

## Also filed, project-scoped rather than constellation-scoped

Issue #317 — every spine template carries `config_ref: docs/agents/engine-config.json`, a path that
is absent-by-design in skill-source repos, together with several hundred words of imperative prose
explaining that it is dead. A corpus-wide cleanup, deliberately not fixed inside #300 because a
single divergent plan is a worse local state than the redundancy.
