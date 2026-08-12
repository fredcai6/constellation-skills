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

## 3. Survey checklists: `record` is the re-record verb, and nothing says so

**Target:** `constellation-reviewer` skill's checklist doctrine, and the engine's REFUSED text.

**Defect:** on a `survey`-type checklist, `advance` and `reopen` both refuse as gated-only. The way to
re-record a check after a rework round is to call `record` again on a terminal item. That works, but
it is documented nowhere and the refusal message names neither the rule nor the alternative — the
same shape as the already-exported
`lesson:checklist-engine-from-child-relative-path-and-gated-vs-survey`.

**Grounding:** the g1/g3/g5 reviewer hit it across **five** review rounds in this one issue and
reported it each time, having found it by being refused rather than by reading anything. Its words:
*"Fifth round, one-line fix in the reviewer SKILL."*

**Suggested fix:** one line in the reviewer skill's checklist section, and add the alternative to the
engine's gated-only refusal message so it is discoverable from the error.

## 4. Engine `--finding` text is shell-mangled when it contains backticks

**Target:** `scripts/checklist_engine.py` journal writes, or the doctrine that tells agents how to
pass finding text.

**Defect:** a `--finding` string containing backticks was mangled by the shell and **silently dropped
two words** from the journal. The engine accepted the truncated text without complaint, so the
provenance record is quietly wrong rather than loudly rejected.

**Grounding:** reported by the g5 reviewer at the end of its BLOCK round. Same class as this run's
other silent-degradation findings: the failure produces a plausible-looking artifact.

**Suggested fix:** either strip/escape control characters on the engine side, or state the
single-quoting requirement where agents are told to pass finding text. Given how much of this system's
value is in journal provenance, silent truncation of a finding is worse than a refusal.
