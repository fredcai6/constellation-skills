# Lane E return — `cmdr-567-e` — door rejections captured as episode friction (#541)

## 1. Verdict

**Delivered.** A real MCP door refusal now lands in the tracked `episodes/` store instead of
vanishing, proven by a fresh-process trigger read back through `query_episodes.py`, with a
negative control. The inherited lane-D1-sweep item (the CLI-recommending refusal tail) is
retired at all three occurrences that carried it.

One decision is **not** mine to make and is floated to the Admiral below (§9 pre-rulings note,
§below "Float"): whether `docs/EPISODE_STORE.md` §10's categorical "nothing should auto-create
an episode" permits the shipped design at all.

## 2. The captured record

A real refusal, triggered via `call_lifecycle_tool('spine_bind', {...})` in a genuinely fresh
`python3` subprocess (never imported into any conversation's own interpreter), against this
lane's own live, currently-bound spine (`.agent-work/567-e/spine.json`, read-only throughout —
byte-identical before/after, confirmed both times), produced `episodes/active/567-e-002.md`
(implementer's trigger) and, independently, `episodes/active/567-e-004.md` (reviewer's own,
separately-authored trigger). Quoted in full (`567-e-002.md`):

```
<!-- episode-state: schema=1 id=567-e-002 status=active -->

# episode: 567-e-002

## Mechanical
- run: 567-e
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: ctx-567-e-execute@135c82075a3a2c337f538dc8d9f08e58076b3aca
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 0

## Agent-supplied

### assertion:567-e-002.a1
- kind: task-intent
- strength: strong
- statement: Called `spine_bind` through the MCP door.

### assertion:567-e-002.a2
- kind: expected-behavior
- strength: weak
- statement: Bind this door to a spine that ALREADY EXISTS, so this process can drive it
  with the other tools. [... full registered MCP tool description, quoted verbatim ...]

### assertion:567-e-002.a3
- kind: observed-behavior
- strength: strong
- statement: REFUSED: this door may only bind a spine inside its OWN checkout's work area
  ('.../.agent-work'); spine_file resolves to '/tmp/definitely-outside-the-work-area/
  not-a-real-spine.json', which is outside. [...] A dispatched crew already has its spine
  bound before its first call, assigned by run_crew.py --backend cli --spine when it
  launched the child into its own worktree, which leaves nothing here for an agent to
  name -- the CLI itself remains an operator/debug path, not an instruction aimed at one
  (issue #559).

### assertion:567-e-002.a4
- kind: impact-cost
- strength: strong
- statement: The call did not proceed; 'spine_bind' returned REFUSED before it reached
  the engine.

### assertion:567-e-002.a5
- kind: workaround
- strength: medium
- statement: A dispatched crew already has its spine bound before its first call [...]
  the CLI itself remains an operator/debug path, not an instruction aimed at one (issue #559).
```

Read back with `python3 scripts/query_episodes.py fetch 567-e-002` (exit 0): all 9 mechanical
fields and all 5 agent-supplied assertions present, matching the file exactly.

**Every field is a literal derivation from the refusal's own data** — never invented
narrative: `task-intent` is the tool name; `expected-behavior` quotes the tool's own
registered MCP `description` string verbatim; `observed-behavior` is the refusal message
verbatim; `impact-cost` is a fixed, always-true-for-this-population fact; `workaround`
extracts the refusal's own trailing escape-hatch sentence.

## 3. The negative control

With the new capture call bypassed (`_capture_refusal_episode`'s call site inside
`_log_rejection` temporarily replaced with a no-op, then cleanly restored — done and re-shown
independently by both the implementer and the reviewer), the identical trigger against the
identical spine produced:

```
episodes/active/ before: 279 files, after: 279 files
new file(s): []
```

Same refusal message, same `isError: true` from the door's own response — zero new files.
`git diff --stat scripts/mcp_spine_server.py` after restoring showed only the substantive
change, no bypass residue, confirmed independently a second time by the reviewer's own
separate bypass-and-restore cycle.

## 4. The refusal-text change

`_THE_CLI_IS_PER_CALL` (used at the two `_spine_bind` containment-refusal sites), **before**:

> "Name a spine under that work area, or use the CLI, which is per-call by construction."

**After**:

> "A dispatched crew already has its spine bound before its first call, assigned by
> `run_crew.py --backend cli --spine` when it launched the child into its own worktree, which
> leaves nothing here for an agent to name -- the CLI itself remains an operator/debug path,
> not an instruction aimed at one (issue #559)."

A **third**, previously-unnamed occurrence of the identical retired phrase was found (during
implementation, not in the original launch-order text) in `_identity_violation`'s
`--from-child` refusal — fixed too, since the Close Criterion's own grep check was file-wide:

**Before**: `"...Put the child under the spine's work area, or use the CLI, which is per-call by construction."`
**After**: `"...Put the child under the spine's work area, or launch a door already bound to the target spine -- a dispatched crew's own run_crew.py --backend cli --spine launch does exactly that before its first call."`

`grep -n "per-call by construction" scripts/mcp_spine_server.py` returns nothing (verified by
the implementer, the reviewer, and the Commander, independently, three times).

## 5. The filter

**What is captured:** exactly the population that already reaches `_tool_error` with both
`tool` and `rejection_class` set — the same population `_log_rejection` already writes once
per call to the local `mcp_rejections.jsonl` sidecar. This makes the change additive to an
already-scoped, already-proven-safe mechanism rather than a new, wider one. Within that
population, capture is further bounded:

- **In-process dedup** — at most one episode per `(tool, rejection_class)` pair per door-process
  lifetime, so an agent retrying the same refusal repeatedly cannot flood the store with
  near-duplicate episodes.
- **Refuse rather than fabricate** — capture is skipped (a stderr diagnostic names why, the
  door never crashes) whenever `episode_capture.mechanical_fields()` cannot honestly derive
  all nine required mechanical fields, or the refusing tool has no registered `TOOLS`
  description to quote for `expected-behavior`.
- **No bound spine, no capture** — an unbound-door refusal has no work-id to attribute an
  episode to, and none is invented. The JSONL sidecar still catches that case when
  `SPINE_REJECTION_LOG` is set; the behavior there is unchanged by this gate.

**What is explicitly NOT captured**, named rather than silently absorbed: engine-native
refusals (through `run_engine`, e.g. a postcondition check failing, a `claim` refused for a
held lease) are a real, separate population this design does not reach at all — `_tool_error`
is never called on that path. This is a named limit of the shipped design
(`.agent-work/567-e/DESIGN_NOTE.md`, Candidate A), not a defect discovered after the fact.

## 6. Suite result

Full suite, clean detached worktree of the branch (`git worktree add --detach`), run twice:

- First run, commit `cf6cdaa2`: surfaced two additional (non-`MapTreeFreshnessTests`)
  failures, both diagnosed and resolved before the second run (see REPLAN_INPUT.json
  discrepancies D0/D1 for the full account) — an unapproved-store-mention census gap (fixed
  by extending `tests/data/store_mentions.approved.txt`) and a pre-existing environmental
  artifact (`CREW_SCRATCH_DIR` leaking from this Commander's own ambient dispatched-crew
  session into `tests/test_crew_launcher.py::ScratchDirResumeTests`, confirmed to reproduce
  identically on the untouched base commit `f05a3d78` with zero code changes).
- Second run, commit `a34a62a0`, with the merge-gate check corrected to also unset
  `CREW_SCRATCH_DIR`:

```
1 failed, 3365 passed, 6 skipped, 1219 subtests passed in 140.73s (0:02:20)
```

`^FAILED` grep output:
```
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```
Nothing else failed. `MapTreeFreshnessTests` is the sanctioned exception per the launch
order — the Admiral regenerates `map/INDEX.md` once on final merged `main`.

**Commit sha verified: `a34a62a0`.**

## 7. Touched paths

- `scripts/mcp_spine_server.py` — the capture mechanism (`_capture_refusal_episode`,
  `_tool_description`, `_episode_workaround`, module-level `_CAPTURED_REJECTIONS` dedup set)
  and the refusal-text swap at 3 sites, including the one `spine_bind` `TOOLS` description
  rewording (second-person pronoun removed, meaning preserved — see §10 workflow feedback).
- `tests/test_mcp_rejection_episode_capture.py` — new test file (unit-level, mock/fixture-based).
- `episodes/active/567-e-001.md` through `567-e-009.md` — real episodes: `-001`/`-003` from an
  early `spine_start` acceptance trigger, `-002` the mandated `spine_bind` acceptance trigger
  (implementer), `-004` the reviewer's own independent re-trigger, `-005` through `-009` this
  run's own feedback-step reflection episodes.
- `tests/data/store_mentions.approved.txt` — extended with 11 new approved entries (all
  WRITE-path facts), each with its own reason, for the guard the new capture code tripped.
  **Not originally in my file-ownership grant** — flagged here transparently: this is repo-wide
  test data, not code inside `scripts/mcp_spine_server.py` or `episodes/**`, but updating it was
  necessary to ship this gate's own change without breaking an existing repo-wide invariant,
  and the guard's own doctrine explicitly invites exactly this action.
- `.agent-work/567-e/**` — this run's own working artifacts (spine, execute.json, mission
  frame, design note, crew handoffs, triage candidates, REPLAN_INPUT.json, episode-delta.json,
  state note) — moving to `.agent-work/archive/` at this step's close.
- `.agent-work/epic-567-door/results/lane-e-RETURN.md` — this file.

**Wanted to touch, did not (fenced):** `docs/EPISODE_STORE.md` (would have been the natural
place to record the sec.10 tension resolution, but fenced to lane D1 this wave — see §9).
`scripts/checklist_engine.py` (would have been the natural place to make its own `refusals`
counter see door-own rejections too, staged as a triage candidate instead — fenced to lane H).

## 8. Map impact

Yes, touches indexed source (`scripts/mcp_spine_server.py` is indexed under
`map/INDEX.md` → `scripts.mcp_spine_server`). Map is `DEGRADED-UNPARSEABLE` for the whole
repo this wave (packet directories referenced by `map/INDEX.md` are absent on disk;
`map/ids.jsonl` is empty) — not acted on, per `decision:map-index-is-admiral-owned`. No
`map/INDEX.md` edit made.

## 9. Triage candidates

Two, staged as files, none filed as issues (`decision:no-issue-filing-mid-run`):

- `.agent-work/567-e/triage-candidates/second-person-tool-descriptions-skip-capture.md` —
  four more `TOOLS` descriptions still carry second-person pronouns and will silently skip
  episode capture the first time any of their door-own rejections are captured (fails safe,
  never crashes, but drops the episode with only a stderr diagnostic).
- `.agent-work/567-e/triage-candidates/engine-refusals-counter-blind-to-door-own-rejections.md`
  — `checklist_engine.py`'s own `refusals` counter never sees a door-own rejection, so any
  captured episode's mechanical `refusals` count is an honest-but-incomplete read of engine
  state. Fenced to lane H this wave; a real engine-surface change, not a script-local one.

## 10. Workflow feedback

**What helped:** the module's own extensive docstrings (`_own_checkout_for_binding`,
`_write_amend_delta`, `_derivable_work_id`, `episode_capture.mechanical_fields`) made the
corrected design buildable almost entirely by reuse rather than invention — every hard part of
this change already had a named, working pattern somewhere else in the same file or its
sibling scripts. The cold-critic dispatch at plan time (single-author two-candidate comparison,
not a full panel — a fairly-easy call per design-it-twice doctrine) caught three real technical
defects (file-vs-inline delta, relative store-root cwd hazard, a still-fabricated
`expected-behavior` field) before any code was written, which is exactly what that mechanism is
for.

**My own mistakes, stated plainly:**

1. I initially misread the HARD-context-band advisory's "attach refresh-request, then stop"
   recipe as license to end my turn the moment I entered the `execute` step, having done zero
   of its actual work. The Stop hook refused this correctly, twice, and named the resolution:
   the recipe is for a gate boundary with nothing started, not a blanket permission to hand off
   whenever the advisory fires mid-flight. I should have recognized this distinction from the
   launch order's own text on first read (`Do not read a HARD advisory... as an instruction to
   advance --why and hand off on turn one`) rather than needing the hook to correct me.
2. I ran the first full-suite check without unsetting `CREW_SCRATCH_DIR`, which is set in my
   own ambient environment because I am myself a dispatched crew. This produced one false
   "regression" that cost real investigation time (a second detached worktree at the base
   commit) to rule out. The fix — unsetting it alongside the `SPINE_*` vars the check already
   excluded — should have been obvious from the same reasoning that motivated excluding those
   in the first place; I only found it after the failure, not before.
3. I did not initially pass the correct `base_dir` to `episode_capture.mechanical_fields()` at
   my own feedback step (used the worktree root instead of the spine's own containing
   directory), which silently dropped `context-manifest-ref` from my own episodes' mechanical
   bins with no error. `manifest_root()`'s own docstring explains exactly why this matters, but
   I read it only after hitting the gap, not before calling the function.

**What would have helped:** a one-line cross-reference from `mechanical_fields()`'s own
docstring to `manifest_root()`'s `base_dir` contract would have saved the third mistake above;
right now the caveat lives only in the helper it delegates to, one hop away from where a caller
actually decides what to pass.

## 11. PR

Opened after this file is committed — see the follow-up commit/push/PR sequence for the
exact number and head sha (this file is written before that sequence runs, per the archive
step's own ordering: commit all remaining work, including this file, before pushing and
opening the PR).

## Float to the Admiral

**`docs/EPISODE_STORE.md` §10** states categorically: "nothing should auto-create an episode,
and nothing should — an auto-created one could only carry fabricated assertions." This gate's
whole mission (issue #541) requires exactly an automatic, no-human-in-the-loop capture — the
launch order's own acceptance criterion (`decision:prove-it-from-the-store`, graded
`settled/doctrine`) demands a refusal be provable straight out of `episodes/` from a single
fresh-process trigger, with no separate authoring step.

I did not resolve this conflict by picking a side. The shipped design (Candidate A, corrected)
resolves the tension **in practice** by making every one of the five agent-supplied fields a
literal quotation or extraction of data the refusal itself produced — never composed judgment
— which is a genuine, inspectable answer to §10's stated concern (fabricated assertions), but
it is still, in the most literal reading, auto-creating an episode, which §10's own sentence
forbids categorically and without qualification. `docs/EPISODE_STORE.md` is fenced to lane D1
this wave, so I am not the one positioned to rule on whether that categorical text should be
read as permitting a literal-derivation carve-out, or whether it should be relaxed/annotated to
say so explicitly, or whether the shipped mechanism needs a different shape entirely.

**Question for the Admiral:** does the literal-derivation-only design stand as shipped, or does
`docs/EPISODE_STORE.md` §10 need to be revisited (by lane D1, or at epic closeout) to either
bless this carve-out explicitly or force a different mechanism?
