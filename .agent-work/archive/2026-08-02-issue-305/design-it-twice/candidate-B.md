# Candidate B — issue #305 gate plan, authored under MAXIMUM UNSKIPPABILITY

Author stance: assume the agent driving this plan is actively unhelpful — it drives
the engine as little as possible, never runs an optional script, and stops the
moment its own code path works. Every gate below is designed so that gap has no
foothold: either the fact is produced as a side effect of something the agent
cannot avoid doing, or the absence of the fact is loud (a refusal, a red test),
never silent.

## The seam, and why

### Manifest byproduct (requirement 1)

**Seam chosen: the top of `dispatch()`, `checklist_engine.py:2375-2424`, not just
the `current` branch at `:2387-2391`.**

The settled pre-ruling (`PROBLEM_STATEMENT.md` "Manifest as a byproduct of
assembly") names `current` as assembly: `current(cl)` is
`render_human(state(cl))`, and `state(cl)` derives everything from `active_id(cl)`
— the same selector `build_manifest()` already uses (`context_manifest.py:374`,
`checklist_engine.py:184-189`). I keep that as the anchor, but I do not stop
there, because `current` is not actually unskippable: `RAIL_VERBS =
{"claim", "current", "start", "advance", "attest", "attach"}` (`:206`) means the
same doctrine-rail text `current` shows is also appended to `start`'s,
`advance`'s, `attest`'s and `attach`'s own success output
(`dispatch():2422-2423`). An agent that never calls `current` and goes straight
to `start id1` / `attest id1 --cond c1` / `advance id1` gets the same "ACTIVE
{id}..." framing baked into those verbs' own replies and has no mechanical reason
to ever call `current` at all. Under my constraint that is exactly the shape of
gap I was told to design out, not document.

So the seam widens: emit the manifest for `active_id(cl)` right after
`config = load_config(cl, base_dir)` (`:2377`), before the `v == "heartbeat"` /
`v == "release"` early returns — the only paths that skip it (`:2380-2386`) —
because those two manage the lease only and touch no task state, so they have
nothing to project. Every other verb — `current`, `claim`, and every mutating
verb — falls through this point before it does anything else. There is no verb
call that mutates or reads task state without a manifest being (re)written for
the active step first. `produce()` writes a separate file (`manifest_path()`,
`context_manifest.py:413-417`); it never touches `cl`, so this stays compatible
with `main()` deliberately not calling `save()` for `current` (`:2558`) — the
manifest is a side artifact of dispatch, not a state mutation, for every verb,
not only the read-only one.

A malformed `context_refs` entry (`DeclarationError`) is wrapped into
`EngineError` and allowed to refuse the verb, rather than silently degrading to
"no manifest this time." `context_manifest.py`'s own philosophy is "fail visibly,
never degrade into a plausible-looking manifest missing a row" (`DeclarationError`
docstring, `:154-159`); letting that refusal reach the agent is the same
philosophy applied one level up, and it composes for free with requirement 2 —
G1's `refusals` counter — since a refused verb now increments the same mechanical
fact either way.

### Mechanical field group (requirement 2)

Composed by a new, small, pure module, `scripts/episode_mechanical.py`,
mirroring `context_manifest.py`'s own shape: no CLI verb of its own (a verb would
touch persistence control flow for a convenience print — the same argument
`context_manifest.py:64-66` already makes), one pure function
(`mechanical_fields`), engine state and the journal file as its only inputs,
injected-edge-testable. It imports `active_id` and `journal_path` from
`checklist_engine` by name — the same "no second selector" discipline
`context_manifest.py:80-83` already enforces — and it imports `manifest_path`
from `context_manifest` so `context-manifest-ref` is the exact formula the engine
used to write the file at G2, not a second guess at the same path.

This is deliberately not a change to `apply_episode_delta.py`. The writer's
`MECHANICAL_ALL_FIELDS` allowlist (`:120-132`) and `_validate_create` (`:865-939`)
are the frozen contract; the composer's whole job is to hand that writer a
`mechanical` dict it would have accepted from a careful human, without a human
ever having to be careful.

### `run.dirty` removal (requirement 3)

`context_manifest.py` `run_facts()` (`:320-348`) drops its `dirty` parameter and
the `"dirty": dirty` key; `build_manifest()` (`:351-388`) stops reading
`state.get("dirty")` at `:387`. `default_repo_state()`/`checklist_engine.repo_revision()`
are not touched — they remain the general, dual-fact primitive their own
docstrings describe ("a second caller with different needs is free to use either
half," `context_manifest.py:310-312`). Only the one caller-side consumption of
the `dirty` half is deleted. This is removal, not repair, per
`decision:drop-run-dirty`: nothing replaces the key.

### The refusals gap (the central problem, not a footnote)

`main()`'s `except EngineError` branch (`:2556-2572`) already persists `cl` on a
non-dry-run, non-`current` refusal (`:2558-2559`) — it just records nothing about
the refusal itself. I close this with the smallest possible engine-state change:
a new top-level scalar, `cl["refusals"]`, incremented in that same branch, gated
by the exact same condition that already decides whether to save:

    if not args.dry_run and args.verb != "current":
        cl["refusals"] = int(cl.get("refusals", 0)) + 1
        save(path, cl)

No new file, no new persistence mechanism, and deliberately not a journal entry:
the journal is documented and implemented as one line per successful mutating
verb (`:2469`, `append_journal_entry` called only on the success path at
`:2578-2583`), and widening that invariant is a bigger, riskier change than this
issue needs — every other mechanical fact I need (`reopens`, `rework-count`,
`failed-commands`) is already available without touching the journal's own
success-only contract. `cl["refusals"]` rides the persistence path that already
exists for exactly this branch. A thin reader, `refusal_count(cl) -> int`, sits
beside `active_id()` (`:184-189`) for symmetry and testability. This is additive
to the raw spine schema (like `rework_count` was before it) and does not change
`_STATE_CONTRACT_VERSION` (`:1404`), because it is never rendered into
`state()`/`render_human()` — an agent never sees it, which is the point: it is a
fact about the agent, not for the agent.

## Gate list

Each gate below is the smallest bite I could defend closing independently. Where
a gate authors a checklist `command`-kind postcondition, its check is a plain
`pytest -k <name> -q` invocation (pytest's own 0/pass, 1/failure vocabulary is not
the ambiguous kind the constraint warns about) unless noted; any new verifier
script I introduce reserves exit 0 = pass, 3 = genuine check failure, and lets an
unhandled traceback surface as Python's default 1 and argparse errors as 2 — so 1
and 2 are never defined to mean "check failed" by my own scripts, only by
accident of an unrelated crash, and 3 is unambiguous. No check anywhere passes
`cwd=`; all paths are absolute.

**G1 — Record refusals in engine state.**
`checklist_engine.py:2556-2559`: increment `cl["refusals"]` as shown above; add
`refusal_count(cl)` beside `active_id()`. Close: a test drives `main()` through
two distinct refusal causes on the same spine file across two subprocess
invocations (a status-caused refusal — `start` on a non-active gate — and a
malformed-argument refusal — `attach` with no payload) and asserts the persisted
spine reads `refusals == 2`; a third, `--dry-run`, refusal must leave the count
unchanged. Evidence: `pytest tests/test_checklist_engine.py -k refusal_count -q`,
exit 0.

**G2 — Widen the manifest-emission seam to dispatch() entry.**
`checklist_engine.py`, new code after `:2377`, before `:2380`. Wrap
`DeclarationError`/`ValueError` from `produce()` into `EngineError`. Close: a test
drives a 2-gate gated checklist purely via `start`+`attest`+`advance`, never
calling `current`, and asserts a manifest file exists at both steps'
`manifest_path()`s afterward — the direct test of the seam-widening rationale
above. A second assertion re-runs the same sequence's tail and confirms
idempotent overwrite (`content()` identical; only `run.generated_at` differs).
Evidence: `pytest tests/test_checklist_engine.py -k manifest_byproduct -q`.

**G3 — Root resolution (repo / skill / durable).**
New helpers in `checklist_engine.py`: `_repo_root(base_dir)` via the existing
`_git()` helper (`git rev-parse --show-toplevel`, the same subprocess pattern
`repo_revision()` and `_collect_changed_files()` already use — no new pattern);
`_skill_root()` = `Path(__file__).resolve().parent.parent` (correct per-binary
even under #344's two-copy reality, since each running copy answers for itself);
`durable` reuses `agent_work_root.durable_root(base_dir)` (new one-directional
import, verified no reverse dependency exists). Close: before wiring,
`grep -rn '"root": *"durable"' skills/ tests/` (and the installed
`~/.claude/skills/...` tree) to confirm what "durable" actually means to a real
declared `context_refs` entry today; if nothing uses it, say so in the gate's own
evidence rather than asserting production behavior for an untested token, and
add only a fixture-level test of the formula. Evidence: the grep output, pasted
verbatim.

**G4 — Manifest destination vs. `roots["durable"]`.**
These are not the same path: the manifest must land in the worktree-local
`.agent-work` (the one #327's dirty-flag defect is about), which is
`base_dir.parent` given the real layout `<agent_work_root>/<work_id>/spine.json`
(verified against this run's own `.agent-work/issue-305/spine.json`). Close: a
test asserts `path.parent.parent == agent_work_root` and
`path.parent.name == cl["work_id"]` for the checklist actually being driven.

**G5 — `run.dirty` removal.**
`context_manifest.py` `run_facts()` / `build_manifest()` per the seam section
above; trim the module docstring's point 1 (`:20-38`) to stop describing a split
that no longer exists, replacing it with one sentence naming #327 and the
self-referential-defect reason, so a future reader doesn't reinvent the removed
field. Close: `grep -n "dirty" scripts/context_manifest.py` returns only that one
historical sentence; every `run["dirty"]`/`m["run"]["dirty"]` assertion in
`tests/test_context_manifest.py` (15+ call sites, lines ~861-1026 pre-change) is
rewritten to `assertNotIn("dirty", m["run"])`, not merely deleted; a new
`test_run_dirty_is_gone` guards regression. Evidence:
`pytest tests/test_context_manifest.py tests/test_context_determinism.py -q`,
exit 0.

**G6 — `episode_mechanical.py`: the composer.**
`mechanical_fields(cl, journal_lines, project, agent_work_root,
manifest_exists=Path.exists)`. Sourcing, field by field: `run` = `cl["work_id"]`;
`spine-step` = `active_id(cl)` or, when the run is fully terminal (all items
terminal — the only time `active_id` is `None`), `cl["items"][-1]`; raise if
`cl["items"]` is empty. `role` = `cl["engine_session"]["claimed_by"]`; raise if
absent ("capture requires at least one `claim`"). `context-manifest-ref` =
`str(context_manifest.manifest_path(agent_work_root, run, spine_step))`,
verified to exist via the injected `manifest_exists` edge — raise if the file G2
should have written is missing, so a broken or bypassed assembly seam is loud,
never a dangling reference. `refusals` = `int(cl.get("refusals", 0))` (G1).
`reopens` = count of `journal_lines` with `"verb" == "reopen"`. `rework-count` =
`sum(t.get("rework_count", 0) for t in cl["tasks"].values())` — run-wide, not
per-step (see Weaknesses). `failed-commands` = count of evidence items, across
every task, with `type == "command-output"` and `payload["exit"] != 0` (evidence
is appended before the refusal raises, `checklist_engine.py:747-759`, so this is
already durable today). `artifact-ref` = `payload["path"]` for evidence items
with `type == "artifact-ref"` — a new, narrow, documented convention
(`attach --type artifact-ref --field path=<p>`), chosen over sweeping every
existing evidence shape because a guess-based sweep risks silent
over/under-collection, which is exactly the vacuous-check failure mode this issue
exists to close. Close: one unit test per sourcing rule against a hand-built
`cl`/journal fixture. Evidence: `pytest tests/test_episode_mechanical.py -q`.

**G7 — Wire the composer into `apply_episode_delta.py`, unmodified.**
A thin caller assembles `{"work_id": ..., "ops": [{"op": "create", "mechanical":
mechanical_fields(...), "agent_supplied": {...}}]}` and either emits it as a
draft delta file for a human/agent to add judgment content to, or (if
`--agent-supplied <file>` is given) calls `apply_delta()` directly. I keep the
draft-file path as the default: it costs nothing mechanically (the writer's own
`_validate_create` is still the last line of defense either way) and it is the
only point a reviewer can catch a composer bug before it is baked into
`episodes/active/*.md`. Close: an end-to-end test creates a real episode via
`apply_episode_delta.main(["--delta", ..., "--store-root", tmp])`, exit 0, then
`query_episodes.fetch_episode` re-parses it and every `_FIELD_READERS` value
matches G6's output exactly.

**G8 — The negative control (primary evidence surface).**
A scenario harness drives the real engine (subprocess or in-process
`dispatch()`) through a scripted run inducing: 1 status-caused refusal, 1
malformed-argument refusal, 1 reopen, 1 command-check failure (exit 2), 1
`artifact-ref` attach. The harness tallies each induced event itself, at the
moment it issues the triggering call — never by reading `cl` back — producing an
independent `ground_truth` dict. The episode is created with the bare legal
minimum `agent_supplied` content (`strength: "weak"`, `statement: "n/a"` times 5
— the schema's `_require_str`/`_reject_newline` floor makes true emptiness
impossible, which is the honest boundary of "the agent records nothing," not a
gap I invented). Close: every mechanical field in the resulting episode equals
the matching `ground_truth` value exactly, not merely "present" — presence-only
would pass even if `mechanical_fields()` silently miscounted, which is the
vacuous shape this whole issue is about. Evidence: the test file, plus the
printed `engine=<n> ground_truth=<n>` comparison per field on assertion.

**G9 — Proof that G8 can fail.**
Same harness, but the composer is fed a `copy.deepcopy(cl)` snapshot taken
immediately after `claim`, before either refusal-inducing call runs; every other
input (`journal_lines`, `agent_work_root`, `project`) is the real,
fully-progressed state. This reproduces, by construction, the exact shape of gap
`PROBLEM_STATEMENT.md` names for `refusals` before G1: a fact that only a
remembering agent could have supplied. Close:
`assertNotEqual(mechanical["refusals"], ground_truth["refusals"])` must hold —
proof that G8's `assertEqual` would have failed had G1 not existed. Required
evidence, both: (a) a one-time transcript, captured during implementation, of
this exact test run genuinely red against the pre-G1 code and green after —
pasted verbatim into the PR description, the literal "run it against a
deliberately incomplete capture, confirm red" the constraint demands; (b) the
stale-snapshot test itself stays in the suite permanently as the regression
guard, since it is red-by-construction regardless of G1's presence and does not
rot the way a one-time transcript would if G1 is ever reverted. A dedicated
wrapper script (not raw pytest) runs this specific test and exits 0 iff it
correctly stayed red, 3 iff it unexpectedly passed (the control has gone
vacuous) — the concrete exit-code-vocabulary artifact this gate produces.

**G10 — #300 AC1 non-vacuous-domain proof.**
Distinct surface from G8/G9: proves the domain of "a manifest is produced on
every assembly" is non-empty and the criterion holds over a real multi-step run,
not only that the mechanical fields are correct. Drive a full 3+ gate checklist
end to end (`claim` -> `current` -> `start` -> `attest` -> `advance`, repeated ->
`release`) via real subprocess calls, and assert a manifest exists for every step
visited, each `content()` matching a hand-computed expectation for that step's
declared `context_refs`. Evidence: `ls .agent-work/<work>/context/*.json` count
equals the fixture's gate count.

**G11 — Cross-run retrieval smoke.**
Seed 2-3 episodes via G7's real path (not hand-written fixtures) from two
different synthetic `work_id`s; `query_episodes.select_episode_ids(root, "run",
[work_id_a])` returns exactly that run's episode(s);
`select_episode_ids(root, "spine-step", [...])` cross-run-joins correctly. No
ranking or similarity — count/id equality only, per the out-of-scope boundary.
Evidence: CLI output pasted verbatim.

**G12 — Doc sync.**
`docs/EPISODE_STORE.md` section 1's stale `git check-ignore .agent-work/`
transcript (already flagged in `MISSION_FRAME.md`, already tripped once by #309)
gets a one-line correction pointing at #326/#305 rather than staying silently
wrong for the next reader. `docs/CHECKLIST_ENGINE_DESIGN.md` gains one sentence
each for the two new engine behaviors (refusal counter,
manifest-emission-at-dispatch). Close: the specific stale claim string is gone
from `EPISODE_STORE.md`; both new behaviors are cited by function name in
`CHECKLIST_ENGINE_DESIGN.md`.

## What I deliberately did not do

- Did not touch `apply_episode_delta.py`. The composer conforms to its existing
  `MECHANICAL_ALL_FIELDS` allowlist exactly; no new fields, no schema
  negotiation, no relaxation of `_validate_create`'s refusals.
- Did not make episode creation itself unskippable — only the mechanical half of
  a creation, once attempted. `agent_supplied` content (task-intent,
  expected-behavior, observed-behavior, impact-cost, workaround) genuinely
  requires judgment; auto-firing a create op at `release` with placeholder
  judgment text would manufacture noise episodes, which
  `decision:throwaway-consolidation` forbids ("a test artifact must never become
  canon") and which crosses into #308's territory (the real first
  consolidation), explicitly out of scope.
- Did not widen the journal's success-only invariant (`:2469`) to also log
  refusals. `cl["refusals"]` rides the persistence path that already exists for
  the refusal branch; a second, riskier change to the forgery-cost mechanism
  wasn't needed to close the gap.
- Did not sweep every existing evidence shape for `artifact-ref`; invented one
  narrow, documented convention instead of guessing, because a guess-based sweep
  risks exactly the silent over/under-collection this issue is about
  eliminating.
- Did not resolve `roots["durable"]`'s real-world semantics from first
  principles — flagged it (G3) as a verify-before-wire gate rather than
  asserting a plausible-sounding formula.
- Did not re-verify any of this against the served engine binary
  (`~/.claude/skills/constellation-commander/scripts/checklist_engine.py`,
  128,889 vs 120,146 bytes, #344) — every line-number anchor here is against the
  repo copy only, and `PROBLEM_STATEMENT.md`'s own discipline (re-verify engine
  facts in both binaries) was not repeated here for time.

## Honest weaknesses of this candidate

- G2's widened seam is the biggest risk this candidate accepts. Moving manifest
  emission from the `current`-only branch to the top of `dispatch()` means a bug
  in G3/G4's root resolution — or in `produce()` itself — now throws on every
  mutating verb call, across every concurrently-running commander spine
  (`dispatch()` is explicitly shared machinery three other commanders depend on,
  per `MISSION_FRAME.md`). A defect that would have been isolated to a read-only
  status check can now block real progress-making verbs
  (`start`/`advance`/`attest`) repo-wide. The constraint explicitly authorizes a
  bigger diff for unskippability, but the blast radius here is categorically
  larger than a `current`-only seam, and I am not fully certain that trade is
  right.
- Wrapping `DeclarationError` into a hard refusal is a new way for verbs to fail
  that did not exist before. Any checklist author who has ever authored a
  slightly-malformed `context_refs` entry that today sits silently unused
  (because nothing calls `build_manifest()`) will discover it breaks
  `start`/`advance` the moment this ships. That is a correctness win — it
  surfaces a real defect — and simultaneously a compatibility risk for spines
  already in flight when this lands.
- G9's falsifiability proof is partly a one-time, manually-captured transcript.
  The permanent regression guard (the stale-snapshot test) is what actually
  protects the invariant going forward; the "red before / green after"
  transcript demanded by the constraint is real evidence but is captured once,
  by hand, during implementation, and does not itself re-run in CI.
- "Zero agent effort" is asserted for the composer, not enforced against a
  forging agent. Nothing stops an agent from hand-authoring a create-op delta
  with fabricated mechanical values and never running the composer at all —
  `apply_episode_delta.py`'s validator checks shape and type, never provenance.
  I make the composer the path of least resistance; I do not and cannot close
  the adversarial case within this issue's scope (that would need something
  foreign to a plain-markdown store, like a signature scheme) and I am saying so
  rather than claiming false completeness.
- `rework-count`/`reopens` are run-wide sums, not scoped to the named
  `spine-step`. If two gates on the same run each get their own episode, both
  will report identical run-wide totals — which could misread as double-counting
  to a future consolidation pass (#308). I chose run-wide because scoping to one
  task loses context from reopens/rework on other gates that still shaped how
  the run went, but this tension is real and `MISSION_FRAME.md` does not
  adjudicate it.

## How I'd know this was the wrong choice

- If, after G2 ships, real concurrent commander runs start refusing on
  `start`/`advance` because of previously-inert malformed `context_refs` entries
  at a rate that reads as collateral damage rather than genuine
  defect-surfacing, that is evidence the seam should have stayed `current`-only,
  or the `DeclarationError` wrap should degrade to a warning evidence item
  instead of a hard refusal.
- If G9's permanent stale-snapshot guard never goes red across many future PRs
  while real production episodes' `refusals` field is later found (by a human,
  not by the gate) to have drifted from ground truth, that means the synthetic
  staleness technique did not actually model the real failure mode, and the
  falsifiability proof was theater.
- If a future consolidation pass (#308) can't tell "this gate was reworked" from
  "some other gate on this run was reworked" because every episode on a run
  carries the same run-wide `rework-count`/`reopens`, that is a sign G6 should
  have scoped those two fields per-step instead of run-wide.
- If implementation of G3 finds that no shipped spine anywhere — in this repo or
  the installed skill trees — declares `root: "durable"`, the honest move is to
  leave `roots["durable"]` unresolved (raise only if actually referenced) rather
  than ship a resolution formula nobody uses.
